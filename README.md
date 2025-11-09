![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-DeepAgents-4B8BBE)
![CI](https://github.com/<SEU_USER>/<SEU_REPO>/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)

# Remote AI Engineer Scout

<img width="608" height="605" alt="image" src="https://github.com/user-attachments/assets/3c2cd325-c458-4cf1-a49c-92be0fb34fd5" />

> Built on top of [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) and adapted to surface remote AI Engineer roles in near real time.  
> Languages: English (this file) · [Portuguese](README_pt.md)

## Overview

This repository hosts a “deep” agent built with **DeepAgents + LangChain**, using the `openai:gpt-4o-mini` model, specialized subagents, and **Tavily** for live web search. Each run gathers remote AI Engineer openings, cross-checks requirements (skills, seniority, stack, compensation bands, geo constraints), and emits a Markdown brief ready to share.

Highlights:
- Supervisor agent orchestrates **research** and **critique** subagents for higher-quality outputs.
- Custom filesystem middleware stores both the generated report (`final_report.md`) and the base prompt (`question.txt`).
- Optional LangSmith tracing (`LANGCHAIN_TRACING_V2=true`) keeps an auditable history of queries, tool calls, and cost.

## High-Level Architecture

```
User → research_agent.py
               ├─ create_deep_agent(...)
               │     ├─ Subagent “research-agent” (uses Tavily)
               │     └─ Subagent “critique-agent”
               ├─ Tools: internet_search, filesystem middleware
               └─ Outputs: final_report.md + question.txt
```

## Prerequisites

- Python 3.10+
- Dependencies listed in `requirements.txt`
- Environment variables:
  - `OPENAI_API_KEY`
  - `TAVILY_API_KEY`
  - `LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_PROJECT` (optional, required only for LangSmith tracing)

### PowerShell setup

| Variable             | Required | Example           | Purpose                                |
|----------------------|----------|-------------------|----------------------------------------|
| OPENAI_API_KEY       | Yes      | `sk-...`          | Chat model (`openai:gpt-4o-mini`)      |
| TAVILY_API_KEY       | Yes      | `tvly-...`        | Web search tool                        |
| LANGCHAIN_API_KEY    | No       | `ls-...`          | LangSmith API key                      |
| LANGCHAIN_TRACING_V2 | No       | `true`            | Enables tracing                        |
| LANGCHAIN_PROJECT    | No       | `remote-ai-scout` | Project bucket inside LangSmith        |

Persist values for future shells:

```powershell
setx OPENAI_API_KEY "sk-..."
setx TAVILY_API_KEY "tvly-..."
setx LANGCHAIN_API_KEY "ls-..."
setx LANGCHAIN_TRACING_V2 "true"
setx LANGCHAIN_PROJECT "remote-ai-scout"
```

Or scope them to the current session with `$env:OPENAI_API_KEY = "..."`.

## Installation

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
1. Read `question.txt` (defaults to “Find remote AI Engineer roles hiring now aligned with my profile.”).
2. Launch the deep agent, which spawns the research and critique subagents and calls Tavily for fresh postings.
3. Overwrite `final_report.md` with the newest report (adjust the script to append timestamped files if you want history).

## Repository Layout

```
.
├─ research_agent.py            # Agent wiring + subagent definitions
├─ question.txt                 # Prompt used for each run
├─ final_report.md              # Latest generated report
├─ libs/
│  ├─ deepagents-cli/...        # Memory middleware tweaks
│  └─ deepagents/...            # Custom filesystem + subagent middleware
├─ requirements.txt
├─ README.md                    # English
└─ README_pt.md                 # Portuguese
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

- Review the official ledger at [https://platform.openai.com/usage](https://platform.openai.com/usage).
- Capture `result["usage"]` after `agent.invoke(...)` and append it to `reports/usage_logs/YYYYMMDD.json`.
- Summarize monthly totals inside the README or a `docs/usage.md`.

## Sample Output

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

## Roadmap

- Persist daily reports inside `reports/`.
- Add regression tests for the customized middleware.
- Automate daily execution + publishing (for example, GitHub Actions committing the latest report).

## Credits

- Based on [DeepAgents](https://github.com/langchain-ai/deepagents) and its deep-agent architecture.
- Inspired by tools such as Claude Code, Anthropic Deep Research, and Manus.
