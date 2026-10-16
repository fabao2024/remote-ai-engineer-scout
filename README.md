![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-DeepAgents-4B8BBE)
![CI](https://github.com/<SEU_USER>/<SEU_REPO>/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)

# 🧠🤖Remote AI Engineer Scout

<img width="608" height="605" alt="image" src="https://github.com/user-attachments/assets/3c2cd325-c458-4cf1-a49c-92be0fb34fd5" />

> Built on top of [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) and adapted to surface remote AI Engineer roles in near real time.  
> Languages: English (this file) · [Portuguese](README_pt.md)

## Overview

This repository hosts an autonomous “deep” agent built with **DeepAgents + LangChain**, powered by **Google Gemini (`gemini:gemini-4-argon`)** by default via an extensible LLM router, specialized subagents, and **Tavily** for live web search. Each run gathers remote AI Engineer openings, verifies geographical eligibility for Brazil/LATAM, cross-checks requirements (skills, seniority, stack, compensation bands, contractor/PJ models), and emits an executive brief formatted in Markdown.

Highlights:
- **Multi-LLM Routing**: Switch between Google Gemini (`gemini:gemini-4-argon`), OpenAI (`gpt-4o-mini`), and ZhipuAI (`glm-4`) via the `LLM_MODEL` environment variable.
- **Executive Summary Table**: Every report features an executive quick-view table sorted in ascending order by days open (newest roles first).
- **Supervisor & Critique Subagents**: Orchestrates **research** and **critique** subagents to guarantee comprehensive, essay-grade analysis.
- **Persistent Memory & Deduplication**: Tracks previously seen positions in `seen_jobs.json` to prioritize fresh opportunities and prevent duplicate postings across runs.
- **Deterministic URL Health & Eligibility Audit**: Pre-validates each job link asynchronously via `httpx` to eliminate 404s, detect closed positions, and enforce geographical eligibility before delivery.
- **Automated Telegram Delivery**: Sends report previews and `.md` attachments directly to your Telegram chat, with failure alert dispatching.
- **Scheduled Cloud Execution**: Runs Mon/Wed/Fri at 8:00 AM BRT via GitHub Actions without requiring your computer to stay on.

## High-Level Architecture

```
User / GitHub Actions → research_agent.py
                              ├─ llm_router.py (Gemini 4 Argon, OpenAI, ZhipuAI)
                              ├─ create_deep_agent(...)
                              │     ├─ Subagent “research-agent” (uses Tavily)
                              │     └─ Subagent “critique-agent”
                              ├─ Tools: internet_search, filesystem middleware
                              ├─ Outputs: final_report.md + question.txt
                              └─ Delivery: send_report_telegram.py (Message + .md Attachment)
```

## Prerequisites

- Python 3.10+
- Dependencies listed in `pyproject.toml` / `requirements.txt`
- Environment variables configured in `.env` (copy from `.env.example`):
  - `GEMINI_API_KEY` (Required for default model `gemini:gemini-4-argon`)
  - `TAVILY_API_KEY` (Required for web search)
  - `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID` (Required for Telegram alerts and report delivery)
  - `OPENAI_API_KEY` (Optional, required only if using OpenAI models)
  - `ZHIPUAI_API_KEY` (Optional, required only if using ZhipuAI models)
  - `LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_PROJECT` (Optional, for LangSmith tracing)

### Environment Variables Setup

Copy the example file to initialize your `.env`:

```bash
cp .env.example .env
```

| Variable | Required | Example | Purpose |
|---|---|---|---|
| `TARGET_ROLE` | No | `AI Engineer` | Target job position to search for (default: `AI Engineer`) |
| `LLM_MODEL` | No | `gemini:gemini-4-argon` | Target model provider & name |
| `GEMINI_API_KEY` | Yes (for default) | `AQ...` | Google AI Studio API key |
| `TAVILY_API_KEY` | Yes | `tvly-...` | Web search tool |
| `TELEGRAM_BOT_TOKEN` | Yes | `123456:ABC...` | Telegram bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Yes | `809564944` | Telegram chat ID for delivery |
| `OPENAI_API_KEY` | Optional | `sk-...` | OpenAI API key (if using GPT models) |
| `ZHIPUAI_API_KEY` | Optional | `435...` | ZhipuAI key (if using GLM models) |

## Installation

Using `uv` (recommended):

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

## Usage

```bash
python research_agent.py
```

Execution flow:
1. Reads `question.txt` (or uses standard query targeting remote AI roles for Brazilian/LATAM professionals).
2. Spawns the deep agent using Gemini 4 Argon, querying Tavily for fresh postings.
3. Subagent critique validates depth, structure, and executive summary table sorting.
4. Writes `final_report.md` and automatically sends the report to your Telegram chat.

## 🎯 Customizing the Target Role

You can scout for any job position simply by changing `TARGET_ROLE` in your `.env` file (defaults to `AI Engineer` if not specified):

```env
# In your .env file
TARGET_ROLE=Machine Learning Engineer
```

### Examples of Supported Roles
- `TARGET_ROLE=Machine Learning Engineer`
- `TARGET_ROLE=Data Engineer`
- `TARGET_ROLE=MLOps Engineer`
- `TARGET_ROLE=Full Stack Developer`
- `TARGET_ROLE=AI Product Manager`

### Overriding for a Single Run via Terminal
You can temporarily override the target role without editing your `.env`:

```bash
# Windows (PowerShell)
$env:TARGET_ROLE="Data Engineer"; uv run python research_agent.py

# Linux / macOS
TARGET_ROLE="Data Engineer" uv run python research_agent.py
```

### Changing the Role in GitHub Actions
When triggering the workflow manually via GitHub Actions (**Actions** → **Daily AI Engineer Scout Report** → **Run workflow**), enter the desired title in the **Target job title to search for** field.

## Repository Layout

```
.
├─ research_agent.py            # Main agent orchestration + subagent definitions
├─ url_validator.py             # Deterministic URL health checker and closed job detector
├─ job_tracker.py               # Memory tracker and URL deduplication utility
├─ seen_jobs.json               # Persistent registry of previously reported jobs
├─ llm_router.py                # Multi-provider LLM router (Gemini, OpenAI, ZhipuAI)
├─ send_report_telegram.py      # Telegram bot delivery utility
├─ question.txt                 # Prompt used for each run
├─ final_report.md              # Latest generated report
├─ reports/                     # Timestamped historical reports
├─ .env.example                 # Template for environment variables
├─ .github/workflows/
│  └─ daily-report.yml          # GitHub Actions automation pipeline
├─ pyproject.toml / uv.lock     # Project dependencies
├─ README.md                    # English documentation
└─ README_pt.md                 # Portuguese documentation
```

## Customization

```
Find remote AI Engineer roles hiring now aligned with my profile.

# Scope
- Focus: Senior AI/ML Engineer roles
- Region: Americas (remote, LATAM-friendly)
- Tech: Python, LangChain, vector DBs, LLM Ops
- Exclude: Onsite-only roles, internships
```

- **Prompt & scope** – edit `question.txt` to target a niche (LATAM-only, juniors, specific stacks, etc.).
- **Fresh sources** – pass `time_range="day"` to Tavily in `internet_search` to bias toward today’s posts.
- **Report history** – write `final_report_<YYYYMMDD>.md` inside a `reports/` directory instead of overwriting.
- **Additional tools** – register new APIs (job boards, Slack, Sheets) and mount them through middleware.
- **LangSmith metadata** – send tags via `agent.invoke(..., config={"metadata": {...}})` for easier analytics later.

## Common Issues

- `KeyError: 'TAVILY_API_KEY'` – export the variable before running the agent.
- `Failed to POST https://api.smith.langchain.com...` – LangSmith credentials or project missing; disable tracing if not needed.
- `typing.NotRequired` warnings – already fixed by replacing annotations with standard optional types in middleware.

## Tracking and Cost Reporting

### LangSmith

![Remote AI Engineer Scout_2](https://github.com/user-attachments/assets/8c522ff0-0136-44b6-9a5e-25d36950538f)

1. Export `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_API_KEY`, and `LANGCHAIN_PROJECT`.
2. Run `python research_agent.py`; each execution creates a trace detailing tools, prompts, tokens, and latency.
3. In LangSmith, filter by project and record:
   - Timestamp plus a short label (use `metadata` to tag runs automatically).
   - `prompt_tokens`, `completion_tokens`, `total_tokens`, and estimated cost.
4. Capture screenshots or use **Export CSV** to share results. Example table:

| Run        | Query                               | Prompt Tokens | Completion Tokens | Cost (USD) |
|------------|-------------------------------------|---------------|-------------------|------------|
| 2024-06-30 AM | Find remote AI Engineer roles...     | 6,245         | 4,108             | $0.21      |
| 2024-06-30 PM | Senior AI roles LATAM-friendly       | 7,002         | 4,887             | $0.24      |

### OpenAI usage dashboard

![Remote AI Engineer Scout_4_dash openAI](https://github.com/user-attachments/assets/f519ee97-90a0-4804-9261-13d70f5eb21e)


- Review the official ledger at [https://platform.openai.com/usage](https://platform.openai.com/usage).
- Capture `result["usage"]` after `agent.invoke(...)` and append it to `reports/usage_logs/YYYYMMDD.json`.
- Summarize monthly totals inside the README or a `docs/usage.md`.

## Sample Output

![Remote AI Engineer Scout_3](https://github.com/user-attachments/assets/018c2a1d-a0c9-437c-a749-e17685328d29)


```
# Remote AI Engineer Opportunities Brief

## Market Snapshot
Remote hiring remains strong across AI-first companies, with openings from junior to staff levels. Employers value end-to-end ML ownership, production LLM expertise, and timezone overlap with the Americas.

## Active Remote Employers
- Tech.co – distributed engineering squads with heavy AI roadmaps.
- Hiring Agents – boutique recruiter listing mid/senior roles up to $282K.
- Indeed – ~1,900 remote AI/ML postings refreshed daily.
- Remote Rocketship – curated feed for junior AI Engineers.
- LinkedIn – 74k+ remote-first AI roles worldwide.

## Representative Openings
1. Staff AI Engineer @ Curai Health (US) – builds LLM infrastructure and evaluation loops.
2. Senior AI Engineer @ Jitterbit (India) – focuses on integration-centric AI services.
3. AI Engineer Level IV @ Premera (US) – healthcare analytics and ML platforms.
4. AI Developer @ BambooWorks (US) – productizes AI copilots for enterprise clients.

## Required Skills & Stack
Python or Java for production services, data modeling, ML deployment/monitoring, MLOps on AWS/GCP, vector database fluency, and strong grounding in AI ethics/bias mitigation.

## Compensation & Location Notes
Typical ranges span $100K–$240K for remote IC roles; some employers accept global applicants while others prefer US/EU coverage.

## Application Strategy
Network via LinkedIn, monitor curated remote boards, tailor resumes per posting, and highlight shipped AI systems or OSS work.

## Sources
1. Tech.co – Remote Jobs
2. Hiring Agents – AI Engineer listings
3. Indeed – Remote AI Engineer jobs
4. Remote Rocketship – Junior AI Engineer feed
5. LinkedIn – Remote AI jobs
```

## Automation & Telegram Delivery

> ⚠️ **SECURITY WARNING**: This is a **public repository**. Never commit API keys or `.env` files to your code!
> All API keys for GitHub Actions must be stored in [GitHub Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions).

The repository includes a GitHub Actions workflow (`.github/workflows/daily-report.yml`) that automatically:

1. **Runs on Mon, Wed, Fri at 8:00 AM BRT (11:00 AM UTC)**
2. **Executes the research agent** with Gemini 4 Argon to gather verified remote openings
3. **Validates report depth & structure** with the critique subagent
4. **Saves timestamped reports** into the `reports/` directory
5. **Dispatches the briefing directly to your Telegram chat** (formatted text preview + full `.md` attachment)

### Setup Instructions

#### 1. Required GitHub Secrets

Configure these secrets in your repository settings (`Settings > Secrets and variables > Actions`):

| Secret | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes (for default) | Google AI Studio API key |
| `TAVILY_API_KEY` | Yes | Tavily web search API key |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token from [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | Yes | Your personal or group Telegram Chat ID |
| `LLM_MODEL` | Optional | Model identifier (defaults to `gemini:gemini-4-argon`) |
| `OPENAI_API_KEY` | Optional | Required if using OpenAI models |
| `ZHIPUAI_API_KEY` | Optional | Required if using ZhipuAI models |
| `LANGCHAIN_API_KEY` | Optional | For LangSmith tracing |
| `LANGCHAIN_TRACING_V2` | Optional | Set to `true` to enable tracing |
| `LANGCHAIN_PROJECT` | Optional | LangSmith project name |

#### 2. Telegram Bot Configuration

1. Open Telegram and message [@BotFather](https://t.me/BotFather) to create a bot (`/newbot`).
2. Copy the HTTP API token generated and save it as `TELEGRAM_BOT_TOKEN`.
3. Obtain your Chat ID by messaging [@userinfobot](https://t.me/userinfobot) or via `https://api.telegram.org/bot<TOKEN>/getUpdates`.
4. Save your numeric Chat ID as `TELEGRAM_CHAT_ID`.

#### 3. Manual Workflow Dispatch

You can manually trigger the workflow anytime:
- Go to **Actions > Daily AI Engineer Scout Report** in your GitHub repository
- Click **Run workflow**

### Telegram Report Format

The Telegram delivery includes:
- **Executive Summary Table** showing the most recent positions sorted by days open.
- **Formatted text overview** highlighting compensation, remote criteria, and required tech stacks.
- **Markdown file attachment (`final_report.md`)** containing the complete multi-page deep analysis.

## Security & API Key Safety

Since this is a **public repository**, follow these strict rules:

### ✅ SAFE - Use GitHub Secrets
API keys are stored encrypted in GitHub and only exposed to Actions at runtime:

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}  # ✅ Safe
```

### ❌ NEVER DO THIS
```python
# Hardcoding keys in code
openai.api_key = "sk-..."  # ❌ NEVER!

# Committing .env files
OPENAI_API_KEY=sk-...  # ❌ NEVER commit .env!
```

### Protected by .gitignore
The following patterns are blocked from being committed:
- `.env`, `.envrc`, `.env*.local`
- `*.pem`, `*.key`
- `secrets/`, `secrets.*`
- `config.local.json`, `credentials.json`

### If You Accidentally Expose a Key
1. **Revoke immediately** in the provider's dashboard:
   - [OpenAI](https://platform.openai.com/api-keys)
   - [Anthropic](https://console.anthropic.com/settings/keys)
   - [Tavily](https://app.tavily.com/home)
2. Generate a new key
3. Update the GitHub Secret
4. Consider the old key compromised (even if removed from git, it's in history)

## Roadmap

- [x] Persist daily reports inside `reports/`.
- [x] Automate daily execution + email delivery
- Add regression tests for the customized middleware.
- add LLM routing for better ROI

## Credits

- Based on [DeepAgents](https://github.com/langchain-ai/deepagents) and its deep-agent architecture.
- Inspired by tools such as Claude Code, Anthropic Deep Research, and Manus.
