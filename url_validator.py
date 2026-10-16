import asyncio
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
import httpx

# Ensure UTF-8 console output on Windows to avoid charmap encoding errors
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CLOSED_PATTERNS = [
    re.compile(r"this job is (?:no longer|not) available", re.IGNORECASE),
    re.compile(r"this position has been filled", re.IGNORECASE),
    re.compile(r"no longer accepting (?:applications|resumes)", re.IGNORECASE),
    re.compile(r"this (?:listing|posting|job) (?:has expired|is closed)", re.IGNORECASE),
    re.compile(r"vaga (?:encerrada|finalizada|fechada)", re.IGNORECASE),
    re.compile(r"esta vaga não está mais disponível", re.IGNORECASE),
    re.compile(r"o processo seletivo foi encerrado", re.IGNORECASE),
    re.compile(r"job is no longer active", re.IGNORECASE),
    re.compile(r"job posting is no longer active", re.IGNORECASE),
    re.compile(r"application closed", re.IGNORECASE),
    re.compile(r"oops! this page doesn't exist", re.IGNORECASE),
    re.compile(r"page (?:you are looking for )?(?:not found|could not be found|cannot be found)", re.IGNORECASE),
    re.compile(r"we couldn't find the page", re.IGNORECASE),
    re.compile(r"the page you were looking for doesn't exist", re.IGNORECASE),
]

ELIGIBLE_PATTERNS = [
    re.compile(r"\bbrazil\b", re.IGNORECASE),
    re.compile(r"\bbrasil\b", re.IGNORECASE),
    re.compile(r"\blatam\b", re.IGNORECASE),
    re.compile(r"\blatin america\b", re.IGNORECASE),
    re.compile(r"\bamérica latina\b", re.IGNORECASE),
    re.compile(r"\bsouth america\b", re.IGNORECASE),
    re.compile(r"\bworldwide\b", re.IGNORECASE),
    re.compile(r"\banywhere in the world\b", re.IGNORECASE),
    re.compile(r"\bglobal(?:ly)? remote\b", re.IGNORECASE),
    re.compile(r"\bamericas\b", re.IGNORECASE),
]

REMOTE_PATTERNS = [
    re.compile(r"\bremote\b", re.IGNORECASE),
    re.compile(r"\bdistributed team\b", re.IGNORECASE),
    re.compile(r"\bwork from home\b", re.IGNORECASE),
]

STRICT_EXCLUSION_PATTERNS = [
    re.compile(r"must (?:be located|reside) in the (?:us|united states)", re.IGNORECASE),
    re.compile(r"(?:us|united states) only\b", re.IGNORECASE),
    re.compile(r"only candidates based in the (?:us|united states)", re.IGNORECASE),
    re.compile(r"us citizenship required", re.IGNORECASE),
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


class HTMLTextExtractor(HTMLParser):
    """Fast, dependency-free HTML text extractor."""

    def __init__(self):
        super().__init__()
        self.text_parts: list[str] = []
        self._ignore_tags = {"script", "style", "noscript", "svg"}
        self._current_tag: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        self._current_tag = tag.lower()

    def handle_endtag(self, tag: str):
        self._current_tag = None

    def handle_data(self, data: str):
        if self._current_tag not in self._ignore_tags:
            text = data.strip()
            if text:
                self.text_parts.append(text)

    def get_text(self) -> str:
        return " ".join(self.text_parts)


def extract_text_from_html(html: str) -> str:
    """Extract human-readable text from an HTML document."""
    parser = HTMLTextExtractor()
    try:
        parser.feed(html)
        return parser.get_text()
    except Exception:
        return re.sub(r"<[^>]+>", " ", html)


async def check_job_url(client: httpx.AsyncClient, url: str) -> dict[str, Any]:
    """Check health, HTTP status code, ATS-specific dead-page signals, and closed status."""
    try:
        resp = await client.get(url)
        if resp.status_code in (404, 410):
            return {
                "url": url,
                "is_valid": False,
                "status_code": resp.status_code,
                "reason": f"HTTP {resp.status_code} (Job Page Not Found)",
            }

        # Anti-bot responses do not prove that the vacancy is active or eligible.
        # Keep them visible for manual review, but never publish them as verified.
        if resp.status_code in (403, 429):
            return {
                "url": url,
                "is_valid": False,
                "eligibility_verified": False,
                "needs_manual_review": True,
                "status_code": resp.status_code,
                "reason": f"HTTP {resp.status_code} (anti-bot response; eligibility not verified)",
            }

        if resp.status_code >= 500:
            return {
                "url": url,
                "is_valid": False,
                "status_code": resp.status_code,
                "reason": f"HTTP {resp.status_code} (Server Error)",
            }

        final_url_str = str(resp.url).lower()
        original_url_str = url.lower()

        # 1. ATS Redirect Checks
        # Workable dead job redirect
        if "apply.workable.com/oops" in final_url_str or "not_found=true" in final_url_str:
            return {
                "url": url,
                "is_valid": False,
                "status_code": resp.status_code,
                "reason": "Workable: Job not found (redirected to oops/not_found)",
            }

        # Greenhouse error redirect
        if "error=true" in final_url_str:
            return {
                "url": url,
                "is_valid": False,
                "status_code": resp.status_code,
                "reason": "Greenhouse: Job not found (redirected to error=true)",
            }

        # Generic redirect away from job posting to careers root
        if (
            any(k in original_url_str for k in ("/j/", "/jobs/", "/postings/", "/positions/"))
            and not any(k in final_url_str for k in ("/j/", "/jobs/", "/postings/", "/positions/"))
            and final_url_str != original_url_str
        ):
            return {
                "url": url,
                "is_valid": False,
                "status_code": resp.status_code,
                "reason": "Redirected away from job posting to main/careers page",
            }

        # 2. HTML Title & Metadata Analysis
        html = resp.text
        title_m = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        title = title_m.group(1).strip() if title_m else ""
        title_lower = title.lower()

        og_title_m = (
            re.search(r'property="og:title"\s+content="([^"]*)"', html, re.IGNORECASE)
            or re.search(r'content="([^"]*)"\s+property="og:title"', html, re.IGNORECASE)
        )
        og_title = og_title_m.group(1).strip() if og_title_m else ""

        # Ashby specific checks:
        # Invalid Ashby job URLs return HTTP 200 with an empty client shell:
        # <title>Jobs</title>, no og:title (or og:title is empty/Jobs), text length < 20k bytes
        if "ashbyhq.com" in final_url_str:
            if title_lower in ("jobs", "") or not og_title or og_title.lower() == "jobs":
                return {
                    "url": url,
                    "is_valid": False,
                    "status_code": resp.status_code,
                    "reason": "Ashby: Invalid/closed job posting (empty shell, title is 'Jobs')",
                }

        # Generic dead page titles
        generic_dead_titles = {
            "workable",
            "page not found",
            "not found",
            "404",
            "404 not found",
            "error",
            "oops",
            "jobs",
            "careers",
            "job not found",
            "position closed",
        }
        if title_lower in generic_dead_titles and len(html) < 25000:
            return {
                "url": url,
                "is_valid": False,
                "status_code": resp.status_code,
                "reason": f"Generic dead page title ('{title}') and missing job details",
            }

        # 3. Content / Text Analysis
        text = extract_text_from_html(html)

        # Check for closed position phrases
        for pattern in CLOSED_PATTERNS:
            if pattern.search(text):
                return {
                    "url": url,
                    "is_valid": False,
                    "status_code": resp.status_code,
                    "reason": "Position closed / no longer accepting applications",
                }

        # Check for strict exclusion (e.g. US Only without Brazil/LATAM exception)
        has_exclusion = any(p.search(text) for p in STRICT_EXCLUSION_PATTERNS)
        has_eligible_region = any(p.search(text) for p in ELIGIBLE_PATTERNS)
        has_remote_signal = any(p.search(text) for p in REMOTE_PATTERNS)

        if has_exclusion and not has_eligible_region:
            return {
                "url": url,
                "is_valid": False,
                "eligibility_verified": False,
                "status_code": resp.status_code,
                "reason": "Strict geographic exclusion without Brazil/LATAM/global exception",
            }

        if not has_remote_signal:
            return {
                "url": url,
                "is_valid": False,
                "eligibility_verified": False,
                "status_code": resp.status_code,
                "reason": "Remote work eligibility not verified on the official page",
            }

        if not has_eligible_region:
            return {
                "url": url,
                "is_valid": False,
                "eligibility_verified": False,
                "status_code": resp.status_code,
                "reason": "Brazil/LATAM/global eligibility not verified on the official page",
            }

        return {
            "url": url,
            "is_valid": True,
            "eligibility_verified": True,
            "status_code": resp.status_code,
            "reason": "Active, remote, and Brazil/LATAM/global eligibility verified",
        }
    except Exception as e:
        return {
            "url": url,
            "is_valid": False,
            "status_code": 0,
            "reason": f"Connection error: {e}",
        }


async def validate_urls(urls: list[str], max_concurrency: int = 8) -> dict[str, dict[str, Any]]:
    """Validate multiple job URLs concurrently with rate limiting."""
    semaphore = asyncio.Semaphore(max_concurrency)
    results: dict[str, dict[str, Any]] = {}

    async with httpx.AsyncClient(
        timeout=15.0,
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
    ) as client:

        async def worker(url: str):
            async with semaphore:
                res = await check_job_url(client, url)
                results[url] = res

        await asyncio.gather(*(worker(u) for u in urls))

    return results


def sanitize_report(report_path: str = "final_report.md") -> dict[str, Any]:
    """Validate all links in final_report.md table and remove broken/closed openings."""
    path = Path(report_path)
    if not path.exists():
        return {"error": f"{report_path} not found"}

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Find Executive Table boundaries
    in_table = False
    table_header_index = -1
    table_rows: list[tuple[int, str, str]] = []  # (line_index, line_str, url)

    link_re = re.compile(r"\[([^\]]+)\]\((https?://[^\)]+)\)")

    for idx, line in enumerate(lines):
        if "## Tabela Resumo Executiva" in line:
            in_table = True
            continue

        if in_table:
            # Table ended if we encounter next header or horizontal divider
            if line.startswith("## ") or line.strip() == "---":
                in_table = False
                continue

            if "|" in line:
                if "Dias Aberto" in line:
                    table_header_index = idx
                    continue
                if "---" in line:
                    continue

                # It's a table row, find url
                match = link_re.search(line)
                if match:
                    url = match.group(2).strip()
                    table_rows.append((idx, line, url))

    if not table_rows:
        return {"status": "No executive table rows found to validate"}

    urls_to_check = [url for _, _, url in table_rows]
    print(f"Auditing {len(urls_to_check)} job URLs in executive table...")

    validation_results = asyncio.run(validate_urls(urls_to_check))

    removed_indices = set()
    removed_details: list[dict[str, str]] = []

    for line_idx, row_str, url in table_rows:
        res = validation_results.get(url, {"is_valid": True})
        if not res["is_valid"]:
            removed_indices.add(line_idx)
            removed_details.append({"url": url, "reason": res["reason"], "row": row_str})
            print(f"  ❌ Removed invalid/closed role: {url} -> Reason: {res['reason']}")
        else:
            print(f"  ✅ Verified active role: {url}")

    if removed_indices:
        # Reconstruct sanitized content
        sanitized_lines = [line for idx, line in enumerate(lines) if idx not in removed_indices]

        # Update table count in introduction if present (e.g. "**28 vagas**" -> "**27 vagas**")
        remaining_count = len(table_rows) - len(removed_indices)
        sanitized_content = "\n".join(sanitized_lines)

        count_pattern = re.compile(r"\*\*(\d+)\s+vagas\b", re.IGNORECASE)
        sanitized_content = count_pattern.sub(f"**{remaining_count} vagas", sanitized_content, count=1)

        path.write_text(sanitized_content + "\n", encoding="utf-8")
        print(f"Sanitized {report_path}: {len(removed_indices)} inactive rows removed, {remaining_count} verified roles remain.")
    else:
        print(f"All {len(table_rows)} positions in {report_path} are 100% active and verified!")

    return {
        "total_checked": len(table_rows),
        "valid_count": len(table_rows) - len(removed_indices),
        "removed_count": len(removed_indices),
        "removed_details": removed_details,
    }


if __name__ == "__main__":
    report_file = "final_report.md"
    result = sanitize_report(report_file)
    print("\nAudit Summary:", result)
