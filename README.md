![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-DeepAgents-4B8BBE)
![CI](https://github.com/fabao2024/remote-ai-engineer-scout/actions/workflows/daily-report.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)

# 🧠🤖 Remote AI Engineer Scout

<img width="608" height="605" alt="image" src="https://github.com/user-attachments/assets/3c2cd325-c458-4cf1-a49c-92be0fb34fd5" />

> Built on top of [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) and engineered to scout, verify, and deliver remote AI Engineer roles open to Brazilian/LATAM professionals in near real time.  
> Languages: **English** (this file) · [Português](README_pt.md)

---

## Overview

**Remote AI Engineer Scout** is an autonomous deep research agent built with **DeepAgents + LangChain**, powered by Google Gemini (defaulting to `gemini:gemini-4-argon` / `gemini:gemini-2.5-flash`) via an extensible multi-provider LLM router, specialized subagents, and **Tavily** for live web search.

Each run discovers open remote opportunities for your target role, validates geographical eligibility (prioritizing Brazil, LATAM, and worldwide remote), audits tech stacks, salary bands, and contractor (PJ) models, and outputs an executive Markdown brief delivered directly to Telegram.

### Key Capabilities

- 🎯 **Target Role Customization**: Scout for any position (e.g., `Applied AI Engineer`, `Agentic AI Engineer`, `Data Engineer`, `MLOps`) simply by setting `TARGET_ROLE` in `.env`, via CLI, or via GitHub Actions workflow dispatch.
- 🛡️ **ATS-Aware Deterministic URL Validator**: Async auditor (`url_validator.py`) inspects every job link with `httpx` to eliminate 404s, detect closed roles, and catch platform-specific quirks (such as Ashby empty SPA shells, Workable `/oops` redirects, and Greenhouse `?error=true` redirects).
- 🧠 **Persistent Memory & Deduplication**: Tracks previously reported vacancies in `seen_jobs.json` to prioritize fresh opportunities and prevent repeating roles across consecutive runs.
- ⚡ **Resilient LangGraph Planning State**: Features `ResilientTodoListMiddleware` in `libs/deepagents/graph.py` with state channel reducers to withstand parallel/concurrent tool calls by modern LLMs without LangGraph state collisions.
- 🚫 **Zero-Tolerance Anti-Hallucination Guardrails**: Strict supervisor and researcher prompts guarantee that every link in the report originates from real ATS search results—no synthesized UUIDs or guessing.
- 🔄 **Multi-LLM Router**: Seamlessly switch between Google Gemini (`gemini:gemini-4-argon`, `gemini:gemini-2.5-flash`), OpenAI (`gpt-4o-mini`), and ZhipuAI (`glm-4`) with automatic retries (`max_retries=6`).
- 📊 **Executive Summary Table**: Every briefing starts with a clean table sorted in strict ascending order by days open (newest opportunities first).
- 📱 **Automated Telegram Delivery**: Dispatches instant executive Markdown summaries and attaches the complete `final_report.md` to your Telegram chat.
- ☁️ **Scheduled Cloud CI/CD**: Runs Mon/Wed/Fri at 8:00 AM BRT (11:00 AM UTC) via GitHub Actions, automatically committing updated reports and memory registries.

---

## High-Level Architecture

```
User / GitHub Actions
        │
        ▼
   research_agent.py
        ├─ llm_router.py (Gemini 4 Argon / 2.5 Flash with OpenAI/ZhipuAI fallbacks)
        ├─ create_deep_agent(...) [libs/deepagents]
        │     ├─ ResilientTodoListMiddleware (State reducer for concurrent todos)
        │     ├─ Subagent "research-agent" (Tavily search + Anti-Hallucination rules)
        │     └─ Subagent "critique-agent" (Editorial quality + Table sorting checks)
        ├─ url_validator.py (Async ATS-aware HTTP & Eligibility Auditor)
        ├─ job_tracker.py (seen_jobs.json memory & deduplication)
        ├─ Outputs: final_report.md + question.txt
        └─ Delivery: send_report_telegram.py (Telegram Chat Alert + Markdown Attachment)
```

---

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended) or standard `pip` + `venv`
- Environment variables configured in `.env` (copy from `.env.example`):
  - `GEMINI_API_KEY` (Required for default Gemini models)
  - `TAVILY_API_KEY` (Required for real-time web searches)
  - `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID` (Required for Telegram alerts and report delivery)
  - `OPENAI_API_KEY` (Optional, for OpenAI GPT models)
  - `ZHIPUAI_API_KEY` (Optional, for ZhipuAI GLM models)
  - `LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2=false`, `LANGCHAIN_PROJECT` (Optional, for LangSmith tracing)

### Environment Variables Setup

Copy the template file to initialize your `.env`:

```bash
cp .env.example .env
```

| Variable | Required | Default / Example | Purpose |
|---|---|---|---|
| `TARGET_ROLE` | No | `Applied AI Engineer` | Target job title to scout |
| `LLM_MODEL` | No | `gemini:gemini-4-argon` | Primary model provider and name |
| `LLM_FALLBACK_MODELS` | No | `gemini:gemini-2.5-flash,openai:gpt-4o-mini` | Fallback models chain |
| `GEMINI_API_KEY` | Yes (for default) | `AIzaSy...` | Google AI Studio API key |
| `TAVILY_API_KEY` | Yes | `tvly-...` | Tavily Search API key |
| `TELEGRAM_BOT_TOKEN` | Yes | `123456:ABC...` | Telegram bot token from [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | Yes | `809564944` | Telegram chat/user ID for message delivery |
| `OPENAI_API_KEY` | Optional | `sk-...` | OpenAI API key |
| `ZHIPUAI_API_KEY` | Optional | `435...` | ZhipuAI API key |

---

## Installation

Using `uv` (fastest and recommended):

```bash
uv sync --frozen
```

Or using standard `venv` + `pip`:

```bash
python -m venv .venv
.\.venv\Scripts\activate        # Windows (PowerShell)
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
```

---

## Usage

Run the scout agent locally:

```bash
uv run python research_agent.py
# or: python research_agent.py
```

### Execution Lifecycle

1. **Role & Memory Injection**: Reads `TARGET_ROLE` and injects recent exclusion links from `seen_jobs.json` into the supervisor prompt.
2. **Autonomous Research**: The deep agent queries Tavily for recent postings (1 to 3 weeks old) matching remote criteria for Brazil/LATAM.
3. **Editorial Critique**: The critique subagent inspects the draft for comprehensive depth, sorting, and markdown formatting.
4. **Deterministic ATS URL Audit**: `url_validator.py` performs async HTTP checks on all extracted URLs, purging 404s, closed jobs, and invalid ATS shells.
5. **Memory Persistence**: `job_tracker.py` registers verified active jobs in `seen_jobs.json` to avoid repeating them in future executions.
6. **Telegram Notification**: Automatically sends a summary table and attaches `final_report.md` to your Telegram chat.

---

## 🎯 Target Role Customization

You can scout for any position simply by setting `TARGET_ROLE` in `.env`:

```env
TARGET_ROLE=Applied AI Engineer
```

### Supported Role Examples
- `TARGET_ROLE=Applied AI Engineer`
- `TARGET_ROLE=Agentic AI Engineer`
- `TARGET_ROLE=Forward Deployed AI Engineer`
- `TARGET_ROLE=Machine Learning Engineer`
- `TARGET_ROLE=Data Engineer`
- `TARGET_ROLE=MLOps Engineer`

### Terminal Single-Run Override

Temporarily override the role for a single run without altering your `.env`:

```bash
# Windows (PowerShell)
$env:TARGET_ROLE="Agentic AI Engineer"; uv run python research_agent.py

# Linux / macOS
TARGET_ROLE="Agentic AI Engineer" uv run python research_agent.py
```

### GitHub Actions Manual Trigger

When triggering the workflow manually in GitHub Actions (**Actions** → **Daily AI Engineer Scout Report** → **Run workflow**), enter the desired title in the **Target job title to search for** input.

---

## 🛡️ Deterministic ATS-Aware URL Validator

Job boards and Applicant Tracking Systems (ATS) handle closed or non-existent postings in subtle ways that fool standard HTTP checks. Our enhanced `url_validator.py` applies platform-specific heuristics:

- **Ashby (`jobs.ashbyhq.com`)**: When a role is deleted, Ashby serves an empty SPA client shell with HTTP 200, `<title>Jobs</title>`, and missing `og:title`. The validator flags and removes these empty shells.
- **Workable (`apply.workable.com`)**: Closed roles redirect to `/oops` or `?not_found=true`. The validator detects redirect paths and drops inactive rows.
- **Greenhouse (`boards.greenhouse.io`)**: Deleted postings redirect with `?error=true` or status 404.
- **Lever (`jobs.lever.co`) / Teamtailor / InHire**: Detects 404s, "job no longer active" notices, and redirects to generic careers roots.
- **Geographic Filtering**: Flags and purges roles with strict US-only requirements that lack Brazil/LATAM exceptions.

Run the auditor directly on any report:

```bash
uv run python url_validator.py
```

---

## ⚡ Resilient LangGraph State Middleware

Modern LLMs (like Gemini 4 Argon) frequently execute parallel tool calls within the same execution step. LangGraph's standard `TodoListMiddleware` uses a `PlanningState` without a reducer on the `todos` channel, causing:

```
InvalidUpdateError: At key 'todos': Can receive only one value per step.
```

In [`libs/deepagents/graph.py`](libs/deepagents/graph.py), we introduced `ResilientTodoListMiddleware` with a reducer channel:

```python
def _take_last_todos(a: Any, b: Any) -> Any:
    return b

class ResilientPlanningState(PlanningState):
    todos: Annotated[list[Todo], _take_last_todos]

class ResilientTodoListMiddleware(TodoListMiddleware):
    state_schema = ResilientPlanningState
```

This ensures zero crashes during parallel agent operations.

---

## 📂 Repository Layout

```
.
├─ libs/
│  └─ deepagents/               # Custom DeepAgents engine with ResilientTodoListMiddleware
├─ research_agent.py            # Main agent orchestration + supervisor prompt + subagents
├─ url_validator.py             # Deterministic ATS-aware URL validator and report sanitizer
├─ job_tracker.py               # Memory tracker and URL deduplication utility
├─ seen_jobs.json               # Persistent registry of previously reported jobs
├─ llm_router.py                # Multi-provider LLM router (Gemini, OpenAI, ZhipuAI)
├─ send_report_telegram.py      # Telegram bot delivery utility
├─ question.txt                 # Prompt instructions for the current run
├─ final_report.md              # Latest verified executive briefing
├─ reports/                     # Historical timestamped reports
├─ .env.example                 # Template for environment variables
├─ .github/workflows/
│  └─ daily-report.yml          # GitHub Actions scheduled automation pipeline
├─ pyproject.toml / uv.lock     # Project dependencies and locks
├─ README.md                    # English documentation (this file)
└─ README_pt.md                 # Portuguese documentation
```

---

## 📱 Automation & Telegram Delivery

The GitHub Actions workflow (`.github/workflows/daily-report.yml`) runs on a schedule:

1. **Schedule**: Mon, Wed, Fri at 8:00 AM BRT (11:00 AM UTC).
2. **Deep Agent Execution**: Searches, filters, and generates `final_report.md`.
3. **URL Sanitization & Memory Sync**: Audits links, purges inactive rows, and commits updated `seen_jobs.json`.
4. **Telegram Dispatch**: Posts the executive table preview and attaches the full Markdown report to your Telegram chat.

### Required GitHub Secrets

Set these in your repository (`Settings > Secrets and variables > Actions`):

| Secret | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes (default) | Google AI Studio API key |
| `TAVILY_API_KEY` | Yes | Tavily Search API key |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram Bot Token from [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | Yes | Numeric Chat ID from [@userinfobot](https://t.me/userinfobot) |
| `OPENAI_API_KEY` | Optional | OpenAI API key (if using GPT models) |
| `ZHIPUAI_API_KEY` | Optional | ZhipuAI API key (if using GLM models) |

---

## 🔒 Security Best Practices

> ⚠️ **SECURITY WARNING**: Never commit `.env` files or API keys into git.

- API keys must only be passed via environment variables or GitHub Secrets.
- `.gitignore` is configured to prevent committing sensitive files (`.env`, `*.pem`, `credentials.json`).
- If a key is accidentally exposed, revoke it immediately in the provider's console.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
