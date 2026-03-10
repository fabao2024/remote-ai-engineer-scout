# Roadmap — Remote AI Engineer Scout

> Tracks completed sprints and planned work for the automated job research agent.

---

## Completed

### Sprint 1 — Foundation (Nov 6–9, 2025)

**Goal:** Build and document the core research agent.

- [x] Initial project scaffold (`research_agent.py`)
- [x] DeepAgents architecture with supervisor + research + critique subagents
- [x] Tavily integration for live web search
- [x] Markdown report generation (`final_report.md`)
- [x] README.md (English) and README_pt.md (Portuguese)
- [x] README badges, images, and execution examples

---

### Sprint 2 — Automation & Delivery (Feb 12–13, 2026)

**Goal:** Automate daily execution and deliver reports to the user.

- [x] `llm_router.py` — switch between OpenAI (GPT-4o-mini) and ZhipuAI (GLM-4.x) via env var
- [x] `send_report_telegram.py` — send report as Telegram message + `.md` file attachment
- [x] `.github/workflows/daily-report.yml` — GitHub Actions pipeline
  - Runs `research_agent.py` and `send_report_telegram.py`
  - Auto-commits timestamped reports to `reports/`
- [x] Schedule adjusted to Mon/Wed/Fri at 8:00 AM BRT (11:00 UTC)
- [x] Email sender removed (replaced by Telegram)

---

### Sprint 3 — Reliability & Maintenance (Mar 9–10, 2026)

**Goal:** Improve observability and keep CI up to date.

- [x] Error handling in `research_agent.py` with full Python traceback on failure
- [x] Telegram failure alert — sends traceback to chat when agent crashes
- [x] GitHub Actions updated to Node.js 24-compatible versions:
  - `actions/checkout` v4 → v6
  - `actions/setup-python` v5 → v6
  - `astral-sh/setup-uv` v3 → v7

---

## Planned

### Sprint 4 — Test Coverage (Next)

**Goal:** Add regression tests so regressions are caught before they reach production.

- [ ] Unit tests for `llm_router.py` (provider selection logic)
- [ ] Unit tests for `send_report_telegram.py` (mocked HTTP calls)
- [ ] Integration test for `research_agent.py` (mock Tavily + LLM)
- [ ] Add test step to GitHub Actions CI

---

### Sprint 5 — Resilience & Fallbacks

**Goal:** Make the agent recover gracefully from API failures.

- [ ] Retry logic with exponential backoff for Tavily and OpenAI calls
- [ ] Fallback chain: ZhipuAI → OpenAI (or vice versa) on quota/error
- [ ] Graceful rate-limit handling for ZhipuAI (GLM-4.x)
- [ ] Alert on consecutive failures (e.g., 2+ missed runs)

---

### Sprint 6 — Enhanced Filtering & Customization

**Goal:** Make the report more targeted and actionable.

- [ ] Filters for specific companies, roles, or keywords (via `question.txt`)
- [ ] LATAM / Latin America region focus option
- [ ] Salary range and experience level targeting
- [ ] Deduplicate job listings across consecutive reports

---

### Sprint 7 — Cost Tracking & Budgeting

**Goal:** Visibility into API spend.

- [ ] Log token usage per run (OpenAI + Tavily calls)
- [ ] Monthly cost summary appended to reports
- [ ] Budget threshold alert via Telegram

---

### Sprint 8 — Data Persistence & Trends

**Goal:** Store structured data for historical analysis.

- [ ] Parse job listings from reports into structured records (JSON/SQLite)
- [ ] Deduplication logic across runs
- [ ] Weekly trend summary (new roles, companies entering/leaving market)
- [ ] Historical dashboard (optional: simple HTML or Notion integration)

---

*Last updated: 2026-03-10*
