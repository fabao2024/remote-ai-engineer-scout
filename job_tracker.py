import json
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

DEFAULT_SEEN_FILE = "seen_jobs.json"

TRACKING_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "ref", "source", "gh_src", "lever-source", "s", "trk"}


def normalize_url(url: str) -> str:
    """Normalize URL by stripping tracking parameters, trailing slashes, and fragments."""
    try:
        parsed = urlparse(url.strip())
        # Filter query params
        query_pairs = parse_qsl(parsed.query, keep_blank_values=False)
        clean_query = [(k, v) for k, v in query_pairs if k.lower() not in TRACKING_PARAMS]
        clean_path = parsed.path.rstrip("/")
        normalized = urlunparse(
            (
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                clean_path,
                parsed.params,
                urlencode(clean_query),
                "",  # Remove fragment
            )
        )
        return normalized
    except Exception:
        return url.strip().rstrip("/")


def load_seen_jobs(filepath: str = DEFAULT_SEEN_FILE) -> dict:
    """Load seen jobs from JSON file."""
    path = Path(filepath)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_seen_jobs(seen_jobs: dict, filepath: str = DEFAULT_SEEN_FILE) -> None:
    """Save seen jobs to JSON file with sorted keys and clean indentation."""
    path = Path(filepath)
    path.write_text(json.dumps(seen_jobs, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def extract_jobs_from_markdown(content: str, default_date: str | None = None) -> list[dict]:
    """Extract job positions and links from markdown report."""
    if not default_date:
        default_date = datetime.now().strftime("%Y-%m-%d")

    jobs = []
    seen_urls_in_report = set()

    # Only the executive table is a machine-readable source of candidates.
    # Narrative sections contain citations, market examples, and research links.
    table_marker = "## Tabela Resumo Executiva"
    marker_index = content.find(table_marker)
    if marker_index < 0:
        return jobs

    table_section = content[marker_index + len(table_marker) :]
    next_header = re.search(r"^##\s+", table_section, flags=re.MULTILINE)
    if next_header:
        table_section = table_section[: next_header.start()]

    for line in table_section.splitlines():
        if "|" not in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue

        days_open, role, company, location, comp, link_col = cells[:6]
        if "Dias Aberto" in days_open or re.fullmatch(r":?-{3,}:?", days_open):
            continue

        link_match = re.search(r"\[([^\]]+)\]\((https?://[^\)]+)\)", link_col)
        role = role.replace("**", "").strip()
        company = company.replace("**", "").strip()
        if not link_match or not role or not company:
            continue

        raw_url = link_match.group(2).strip()
        norm_url = normalize_url(raw_url)
        if norm_url in seen_urls_in_report:
            continue

        seen_urls_in_report.add(norm_url)
        jobs.append(
            {
                "url": norm_url,
                "raw_url": raw_url,
                "role": role,
                "company": company,
                "location": location,
                "compensation": comp,
                "date": default_date,
                "days_open": days_open,
            }
        )

    return jobs


def update_seen_jobs(report_path: str = "final_report.md", seen_file: str = DEFAULT_SEEN_FILE, run_date: str | None = None) -> int:
    """Update seen_jobs.json with entries from a report. Returns count of newly discovered jobs."""
    report_file = Path(report_path)
    if not report_file.exists():
        return 0

    if not run_date:
        run_date = datetime.now().strftime("%Y-%m-%d")

    content = report_file.read_text(encoding="utf-8")
    extracted_jobs = extract_jobs_from_markdown(content, default_date=run_date)

    seen_jobs = load_seen_jobs(seen_file)
    new_jobs_count = 0

    for job in extracted_jobs:
        url = job["url"]
        if url not in seen_jobs:
            new_jobs_count += 1
            seen_jobs[url] = {
                "role": job.get("role", ""),
                "company": job.get("company", ""),
                "first_seen": run_date,
                "last_seen": run_date,
                "appearances": 1,
            }
        else:
            seen_jobs[url]["last_seen"] = run_date
            seen_jobs[url]["appearances"] = seen_jobs[url].get("appearances", 1) + 1
            if job.get("company") and not seen_jobs[url].get("company"):
                seen_jobs[url]["company"] = job["company"]
            if job.get("role") and not seen_jobs[url].get("role"):
                seen_jobs[url]["role"] = job["role"]

    save_seen_jobs(seen_jobs, seen_file)
    return new_jobs_count


def get_exclusion_prompt(seen_file: str = DEFAULT_SEEN_FILE, max_urls: int = 50) -> str:
    """Generate prompt instructions listing recent job URLs to avoid duplicate listings."""
    seen_jobs = load_seen_jobs(seen_file)
    if not seen_jobs:
        return ""

    # Sort by last_seen descending
    sorted_jobs = sorted(seen_jobs.items(), key=lambda item: item[1].get("last_seen", ""), reverse=True)[:max_urls]

    lines = [
        "## Previously Reported Positions (Prioritize NEW Opportunities)",
        "The following positions were already featured in recent reports. Focus your search on FRESH, UNREPORTED openings that do not duplicate these URLs:",
    ]
    for url, details in sorted_jobs:
        comp = f" ({details['company']})" if details.get("company") else ""
        role = details.get("role") or "Role"
        lines.append(f"- {url} — {role}{comp}")

    lines.append("")
    return "\n".join(lines)


def populate_from_history(reports_dir: str = "reports", seen_file: str = DEFAULT_SEEN_FILE) -> int:
    """Scan existing historical reports to initialize seen_jobs.json."""
    seen_jobs = load_seen_jobs(seen_file)
    rep_dir = Path(reports_dir)
    if not rep_dir.exists():
        return len(seen_jobs)

    report_files = sorted(rep_dir.glob("report_*.md"))
    for rpath in report_files:
        # Extract date from filename if possible: report_YYYYMMDD_HHMMSS.md
        match = re.search(r"report_(\d{4})(\d{2})(\d{2})_", rpath.name)
        if match:
            date_str = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        else:
            date_str = datetime.fromtimestamp(rpath.stat().st_mtime).strftime("%Y-%m-%d")

        try:
            content = rpath.read_text(encoding="utf-8")
            jobs = extract_jobs_from_markdown(content, default_date=date_str)
            for j in jobs:
                url = j["url"]
                if url not in seen_jobs:
                    seen_jobs[url] = {
                        "role": j.get("role", ""),
                        "company": j.get("company", ""),
                        "first_seen": date_str,
                        "last_seen": date_str,
                        "appearances": 1,
                    }
                else:
                    if date_str < seen_jobs[url]["first_seen"]:
                        seen_jobs[url]["first_seen"] = date_str
                    if date_str > seen_jobs[url]["last_seen"]:
                        seen_jobs[url]["last_seen"] = date_str
                    seen_jobs[url]["appearances"] = seen_jobs[url].get("appearances", 1) + 1
        except Exception:
            continue

    save_seen_jobs(seen_jobs, seen_file)
    return len(seen_jobs)


if __name__ == "__main__":
    count = populate_from_history()
    print(f"Populated seen_jobs.json with {count} unique positions from historical reports.")
    # Also update with current final_report.md if present
    if Path("final_report.md").exists():
        new_count = update_seen_jobs("final_report.md")
        print(f"Updated with final_report.md: {new_count} additional jobs.")
