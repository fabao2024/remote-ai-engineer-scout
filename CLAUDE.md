# Remote AI Engineer Scout - Project Memory

> This file contains the complete project context and implementation details for continuity across sessions and models.

## Project Overview

**Name:** Remote AI Engineer Scout
**Purpose:** Automated daily research agent that finds remote AI Engineer job opportunities using DeepAgents + LangChain + Tavily
**Core Functionality:**
- Runs `research_agent.py` to search for remote AI Engineer roles
- Uses GPT-4o-mini via OpenAI API
- Searches live web via Tavily API
- Generates structured Markdown reports
- Sends reports daily at 8:00 AM UTC via Telegram bot

## Architecture

```
User/Scheduler → GitHub Actions → research_agent.py
                                     ├─ create_deep_agent()
                                     │   ├─ research-agent (uses Tavily)
                                     │   └─ critique-agent
                                     ├─ Outputs: final_report.md
                                     └─ Sends via: send_report_telegram.py
```

## Key Files

| File | Purpose |
|------|---------|
| `research_agent.py` | Main agent orchestration with subagents |
| `send_report_telegram.py` | Telegram bot report delivery |
| `question.txt` | Base prompt for job searches |
| `final_report.md` | Latest generated report |
| `reports/` | Timestamped historical reports |
| `.github/workflows/daily-report.yml` | GitHub Actions automation |
| `llm_router.py` | Handles LLM provider switching (OpenAI/ZhipuAI) |

## Implementation History

### Phase 1: Core Agent (Completed)
- DeepAgents architecture with supervisor + subagents
- Tavily integration for live web search
- Markdown report generation

### Phase 2: Automation + Telegram (Completed)
- GitHub Actions workflow for daily execution
- `send_report_telegram.py` with Markdown message + file attachment
- Telegram bot integration
- Timestamped report archiving in `reports/`
- Auto-commit to repository

### Phase 3: LLM Routing (Completed)
- Implemented `llm_router.py`
- Added support for Z.AI / ZhipuAI models (GLM-4, GLM-4.7, etc.)
- Environment variable configuration via `.env` (`python-dotenv`)
- Configurable model selection via `LLM_MODEL`

## Environment Variables / Secrets Required

### For Local Development:
```powershell
$env:OPENAI_API_KEY = "sk-..."
$env:TAVILY_API_KEY = "tvly-..."
$env:ZHIPUAI_API_KEY = "your_key..."     # New: Z.AI / ZhipuAI
$env:LLM_MODEL = "zhipu:glm-4.7"         # Optional: Default is openai:gpt-4o-mini
$env:LANGCHAIN_API_KEY = "ls-..."      # Optional
$env:LANGCHAIN_TRACING_V2 = "true"     # Optional
$env:LANGCHAIN_PROJECT = "remote-ai-scout"  # Optional
```

### For GitHub Actions (Repository Secrets):
| Secret | Required | Description |
|--------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `TAVILY_API_KEY` | Yes | Tavily search API |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Yes | Telegram chat ID for report delivery |
| `LANGCHAIN_API_KEY` | No | For LangSmith tracing |
| `LANGCHAIN_TRACING_V2` | No | Set `true` to enable |
| `LANGCHAIN_PROJECT` | No | LangSmith project name |
| `ZHIPUAI_API_KEY` | No | For Z.AI/ZhipuAI models |
| `LLM_MODEL` | No | `openai:gpt-4o-mini` (default) or `zhipu:glm-4.7` |

## Running the Project

### Locally:
```bash
# Setup
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt  # or: uv sync --frozen

# Run agent
python research_agent.py

# Send report via Telegram
python send_report_telegram.py
```

### Via GitHub Actions:
1. Push to repository
2. Go to **Actions > Daily AI Engineer Scout Report**
3. Click **Run workflow** (manual trigger)
4. Or wait for daily 8:00 AM UTC schedule

## Current Configuration

### Schedule:
- **Daily at 8:00 AM UTC** (configurable in `daily-report.yml`)
- Cron: `'0 8 * * *'`

### Telegram Delivery:
- Markdown formatted message
- `.md` file attachment
- Push notification to your phone

### Report Storage:
- `final_report.md` - always latest
- `reports/report_YYYYMMDD_HHMMSS.md` - historical
- Committed to git by default (can be disabled in `.gitignore`)

## Roadmap / Next Steps

### Completed:
- [x] Core research agent with DeepAgents
- [x] Daily automation via GitHub Actions
- [x] Telegram bot delivery
- [x] Timestamped report archiving
- [x] Documentation in README.md and README_pt.md

### Remaining (Priority Order):

1. **Add Regression Tests for Middleware**
   - Test custom filesystem middleware
   - Test subagent spawning
   - Test Telegram sender
   - Add to GitHub Actions CI

2. **Refine Z.AI Integration**
   - Handle rate limits gracefully (currently relies on user quota)
   - Add fallback logic (Zhipu -> OpenAI)

3. **Enhanced Filtering & Customization**
   - Add filters for specific companies/roles
   - Region-specific search (LATAM focus)
   - Salary range filtering
   - Experience level targeting

4. **Cost Tracking & Budgeting**
   - Monthly cost summaries
   - Budget alerts
   - Usage dashboard integration

5. **Data Persistence Improvements**
   - Database storage for job listings
   - Deduplication logic
   - Historical trend analysis

## Technical Notes

### Dependencies:
- Python 3.11+
- `deepagents` (local package in `libs/`)
- `langchain>=1.0.2`
- `langchain-openai` (for GPT-4o-mini)
- `langchain-community` + `zhipuai` (for Z.AI support)
- `python-dotenv` (for local env vars)
- `tavily-python>=0.7.12`
- `httpx` (for Telegram API calls)

### Project Structure:
```
remote-ai-engineer-scout/
├── .github/
│   └── workflows/
│       └── daily-report.yml      # Automation workflow
├── libs/
│   ├── deepagents/               # Core agent framework
│   └── deepagents-cli/           # CLI tooling
├── reports/                      # Generated reports (auto-created)
├── research_agent.py             # Main agent
├── llm_router.py                 # LLM provider logic
├── send_report_telegram.py       # Telegram bot delivery
├── question.txt                  # Search prompt
├── final_report.md               # Latest output
├── pyproject.toml                # Project config
├── uv.lock                       # Lock file
├── README.md                     # English docs
├── README_pt.md                  # Portuguese docs
└── CLAUDE.md                     # This file
```

### GitHub Actions Workflow Steps:
1. Checkout repository
2. Setup Python 3.11
3. Install uv
4. Install dependencies (`uv sync --frozen`)
5. Create reports directory
6. Run research agent (with env vars)
7. Generate timestamp
8. Copy report to reports/
9. Commit to repository
10. Send report via Telegram bot

## Common Issues & Solutions

### Telegram Not Sending:
- Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set
- Make sure you started a chat with the bot (sent it at least one message)
- Check bot token is valid via `https://api.telegram.org/bot<TOKEN>/getMe`

### Agent Fails:
- Verify `OPENAI_API_KEY` and `TAVILY_API_KEY` are set
- Check API quotas/credits
- Enable LangSmith tracing to debug (`LANGCHAIN_TRACING_V2=true`)

### Reports Not Committing:
- Check workflow has `contents: write` permission
- Verify GitHub token permissions in repository settings

## Recent Changes (Last Session)

1. Created `send_report_telegram.py` - Telegram bot delivery
2. Removed `send_report_email.py` - Replaced by Telegram
3. Updated `.github/workflows/daily-report.yml` - Uses Telegram
4. Updated all docs to reflect Telegram integration

## Security & API Key Safety (CRITICAL)

**This is a PUBLIC repository. Follow these rules to protect your API keys:**

### ✅ SAFE - API Keys in GitHub Secrets
```yaml
# .github/workflows/daily-report.yml - This is SAFE
- name: Run research agent
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}  # Encrypted!
```
GitHub Secrets are:
- Encrypted and only accessible to Actions
- Never visible in code or logs (masked as `***`)
- Safe for public repositories

### ❌ DANGEROUS - Never Do This
```python
# research_agent.py - NEVER hardcode keys!
openai.api_key = "sk-abc123..."  # DON'T DO THIS

# .env file - NEVER commit this!
OPENAI_API_KEY=sk-abc123...

# config.json - DON'T commit with keys!
{
  "api_key": "sk-abc123..."
}
```

### Security Checklist

- [ ] No API keys in any `.py` files
- [ ] No `.env` file committed
- [ ] No `config.json` or `secrets.yaml` with keys
- [ ] All keys stored in GitHub Secrets only
- [ ] `.gitignore` includes `.env`, `*.key`, `secrets.*`

### If You Accidentally Expose a Key

1. **Immediately revoke the key** in provider's dashboard:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/settings/keys
   - Google: https://makersuite.google.com/app/apikey
   - Groq: https://console.groq.com/keys
   - Tavily: https://app.tavily.com/home

2. **Generate a new key**

3. **Update GitHub Secret** with new key

4. **Consider it compromised** - even if you delete from git, it's in history

### Local Development Safety

```bash
# Create .env file locally (it's in .gitignore, so won't be committed)
# .env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...

# Load it in Python (for local dev only)
from dotenv import load_dotenv
load_dotenv()  # Only for local development, never for production/Actions
```

**Note:** `python-dotenv` is NOT needed in GitHub Actions - secrets are injected directly.

## Contact / Reference

- **Telegram Delivery:** via @BotFather bot
- **Based on:** langchain-ai/deepagents
- **Inspired by:** Claude Code, Anthropic Deep Research, Manus

---

*Last Updated: 2026-02-12*
*Current Status: Phase 4 Completed (Telegram Bot Integration)*
