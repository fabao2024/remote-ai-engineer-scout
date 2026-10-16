import asyncio
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from job_tracker import extract_jobs_from_markdown  # noqa: E402
from url_validator import check_job_url  # noqa: E402


class FakeTelegramResponse:
    def __init__(self, ok: bool):
        self.ok = ok
        self.status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return {"ok": self.ok}


def test_tracker_reads_only_complete_rows_from_executive_table():
    content = """# Report
## Tabela Resumo Executiva
| Dias Aberto | Cargo | Empresa | Local | Remuneração | Link |
|---|---|---|---|---|---|
| **2 dias** | **Applied AI Engineer** | **Acme** | Brazil Remote | USD 55/h | [Apply](https://jobs.example.com/acme/1?utm_source=x) |
| **3 dias** | **Missing Company** |  | Brazil Remote | Not stated | [Apply](https://jobs.example.com/missing) |

## Market Snapshot
A citation outside the table: [Narrative role](https://jobs.example.com/narrative).
| Not an executive table | link |
"""

    jobs = extract_jobs_from_markdown(content, default_date="2026-10-16")

    assert len(jobs) == 1
    assert jobs[0]["role"] == "Applied AI Engineer"
    assert jobs[0]["company"] == "Acme"
    assert jobs[0]["url"] == "https://jobs.example.com/acme/1"


def test_validator_rejects_remote_without_brazil_or_global_evidence():
    async def handler(request: httpx.Request):
        return httpx.Response(200, text="<html><body>Remote software engineer</body></html>")

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await check_job_url(client, "https://example.test/job")

    result = asyncio.run(run())

    assert result["is_valid"] is False
    assert result["eligibility_verified"] is False
    assert "eligibility" in result["reason"].lower()


def test_validator_accepts_remote_worldwide_evidence():
    async def handler(request: httpx.Request):
        return httpx.Response(200, text="<html><body>Remote worldwide position</body></html>")

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await check_job_url(client, "https://example.test/job")

    result = asyncio.run(run())

    assert result["is_valid"] is True
    assert result["eligibility_verified"] is True


def test_validator_does_not_mark_antibot_as_verified():
    async def handler(request: httpx.Request):
        return httpx.Response(403, text="challenge")

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await check_job_url(client, "https://example.test/job")

    result = asyncio.run(run())

    assert result["is_valid"] is False
    assert result["needs_manual_review"] is True


def test_llm_router_builds_fallback_chain(monkeypatch):
    import llm_router

    class FakeModel:
        def __init__(self, name):
            self.name = name

        def with_fallbacks(self, fallbacks):
            return (self.name, [item.name for item in fallbacks])

    monkeypatch.setenv("LLM_FALLBACK_MODELS", "gemini:flash,zhipu:glm")
    monkeypatch.setattr(llm_router, "_build_model", lambda name: FakeModel(name))

    result = llm_router.get_llm("openai:gpt")

    assert result == ("openai:gpt", ["gemini:flash", "zhipu:glm"])


def test_telegram_returns_false_when_document_delivery_fails(tmp_path, monkeypatch):
    from send_report_telegram import send_report_telegram

    report = tmp_path / "report.md"
    report.write_text("# Report", encoding="utf-8")
    responses = iter([FakeTelegramResponse(True), FakeTelegramResponse(False)])
    monkeypatch.setattr("send_report_telegram.httpx.post", lambda *args, **kwargs: next(responses))

    assert send_report_telegram(str(report), "token", "chat") is False


def test_telegram_returns_true_when_message_and_document_succeed(tmp_path, monkeypatch):
    from send_report_telegram import send_report_telegram

    report = tmp_path / "report.md"
    report.write_text("# Report", encoding="utf-8")
    responses = iter([FakeTelegramResponse(True), FakeTelegramResponse(True)])
    monkeypatch.setattr("send_report_telegram.httpx.post", lambda *args, **kwargs: next(responses))

    assert send_report_telegram(str(report), "token", "chat") is True
