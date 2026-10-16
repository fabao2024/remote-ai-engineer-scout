import os
import sys
import traceback
from pathlib import Path
from typing import Literal

# Ensure UTF-8 console output on Windows to avoid charmap encoding errors
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Preserve TARGET_ROLE if explicitly passed via environment/CLI before loading .env
_explicit_role = os.environ.get("TARGET_ROLE")

from dotenv import load_dotenv
load_dotenv(override=True)

# Target role configuration (defaults to "AI Engineer" if not set)
TARGET_ROLE = (_explicit_role or os.environ.get("TARGET_ROLE") or "AI Engineer").strip()

from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from tavily import TavilyClient
from job_tracker import get_exclusion_prompt, update_seen_jobs

# Reuse the Tavily client across tool invocations
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


def _send_failure_alert(error_msg: str) -> None:
    """Send a Telegram alert when the agent fails."""
    import httpx
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        return
    text = f"❌ *Remote {TARGET_ROLE} Scout failed*\n\n```\n{error_msg[:3000]}\n```"
    try:
        httpx.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=15,
        )
    except Exception:
        pass  # Don't raise — we're already in an error path


def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search via Tavily."""
    try:
        clean_query = query.strip()
        words_without_site = [w for w in clean_query.split() if not w.startswith("site:")]
        if not words_without_site:
            clean_query = f"{TARGET_ROLE} {clean_query}"

        return tavily_client.search(
            clean_query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic,
        )
    except Exception as e:
        return {"error": f"Search failed: {e}. Please reformulate your search query with specific job title keywords and search terms."}


sub_research_prompt = f"""You specialize in investigating remote {TARGET_ROLE} job opportunities.
- Compile current remote-first or remote-friendly openings, employer details, required skills, compensation notes, and hiring signals.
- Verify that each role explicitly allows remote work; if unclear, flag the uncertainty.
- Capture useful metadata such as application deadlines, region restrictions, and tech stack requirements.
- Always return a concise summary plus the raw sources (title + URL) you relied on.
Only your FINAL answer is surfaced to the supervisor, so deliver a complete, citation-backed note."""

research_sub_agent = {
    "name": "research-agent",
    "description": (
        "Used to research more in depth questions. Only give this researcher one topic at a time. "
        "Do not pass multiple sub questions to this researcher. Instead, you should break down a large "
        "topic into the necessary components, and then call multiple research agents in parallel, one for each sub question."
    ),
    "system_prompt": sub_research_prompt,
    "tools": [internet_search],
}

sub_critique_prompt = """You are a dedicated editor. You are being tasked to critique a report.

You can find the report at `final_report.md`.

You can find the question/topic for this report at `question.txt`.

The user may ask for specific areas to critique the report in. Respond to the user with a detailed critique of the report. Things that could be improved.

You can use the search tool to search for information, if that will help you critique the report

Do not write to the `final_report.md` yourself.

Things to check:
- Check that each section is appropriately named
- Check that the report includes `## Tabela Resumo Executiva` right after the main title, with a markdown table sorted in ascending order by 'Dias Aberto' (from most recent/lowest days open to oldest).
- Check that the report is written as you would find in an essay or a textbook - it should be text heavy, do not let it just be a list of bullet points!
- Check that the report is comprehensive. If any paragraphs or sections are short, or missing important details, point it out.
- Check that the article covers key areas of the industry, ensures overall understanding, and does not omit important parts.
- Check that the article deeply analyzes causes, impacts, and trends, providing valuable insights
- Check that the article closely follows the research topic and directly answers questions
- Check that the article has a clear structure, fluent language, and is easy to understand.
"""

critique_sub_agent = {
    "name": "critique-agent",
    "description": "Used to critique the final report. Give this agent some information about how you want it to critique the report.",
    "system_prompt": sub_critique_prompt,
}

research_instructions = f"""You are an expert tech recruiter focused on remote {TARGET_ROLE} positions open to Brazilian professionals working from Brazil.
Write the original user request to `question.txt` first.
Use the research-agent to gather:
- Remote {TARGET_ROLE} job listings that explicitly accept candidates based in Brazil, or that are worldwide/globally remote
- Prioritize roles with no geographic restriction, or those that list Brazil, South America, or LATAM as eligible locations
- Exclude roles that restrict to US/EU/Canada only unless they explicitly list Brazil or LATAM as exceptions
- Companies currently hiring, team focus, and hiring stage
- Core skills, tools, and experience employers expect
- Compensation in USD or BRL, time-zone requirements (BRT-compatible preferred), and any Brazil-specific contractor/PJ notes
- Application tactics, networking leads, or differentiators for Brazilian candidates
- Search for recent open positions, maximum 2 or 3 weeks old from current date

{get_exclusion_prompt(max_urls=35)}

Iterate with the critique-agent whenever you need help polishing the final report.

When ready, write the report to `final_report.md` in Markdown using this structure:
# Remote {TARGET_ROLE} Opportunities Brief — Brazil
## Tabela Resumo Executiva
## Market Snapshot
## Active Remote Employers
## Representative Openings
## Required Skills & Tech Stack
## Compensation & Location Notes
## Application Strategy for Brazilian Candidates
## Sources

Guidelines:
1. Always start the report with `## Tabela Resumo Executiva` featuring a clean Markdown summary table.
   Columns required: | Dias Aberto | Cargo | Empresa | Local / Elegibilidade | Remuneração Estimada | Link / Aplicação |
   CRITICAL: Sort the rows in strict ASCENDING order by 'Dias Aberto' (from the fewest days open / most recent to oldest).
2. Each subsequent section should be thorough, using paragraphs and bullet lists only where they add clarity.
3. Pull concrete facts and insights from your research; cite each with [Title](URL).
4. For every role, explicitly state whether Brazil/LATAM is accepted, or flag it as unconfirmed.
5. Note time-zone requirements — flag roles that require US Eastern or Pacific overlap, as these may be harder from BRT (UTC-3).
6. Include contractor/PJ model notes where relevant, as many Brazilian professionals work as PJ.
7. If relevant data is scarce, explain gaps and suggest follow-up search strategies.
8. Write the report in Portuguese (Brazil).

Citation rules:
- Assign sequential citation numbers (1,2,3…)
- End with ## Sources and list `[n] Source Title: URL` per line.

Available tool:
## `internet_search`
Use it to discover current remote {TARGET_ROLE} roles open to Brazilian candidates."""

# Configure the chat model (ensure OPENAI_API_KEY is set)
from llm_router import get_llm

# Configure the chat model
model = get_llm()

# Build the agent with the research and critique subagents
agent = create_deep_agent(
    model=model,
    tools=[internet_search],
    system_prompt=research_instructions,
    subagents=[critique_sub_agent, research_sub_agent],
)

if __name__ == "__main__":
    try:
        print(f"Starting research agent for role: {TARGET_ROLE}...")
        result = agent.invoke(
            {"messages": [{"role": "user", "content": f"Find remote {TARGET_ROLE} roles hiring now that are open to Brazilian professionals working from Brazil. Focus on worldwide remote, LATAM-friendly, or Brazil-accepted positions."}]}
        )

        files = result.get("files", {})
        final_data = files.get("/final_report.md")
        if final_data:
            report_text = "\n".join(final_data["content"]) if isinstance(final_data["content"], list) else str(final_data["content"])
            Path("final_report.md").write_text(report_text, encoding="utf-8")
            print("Successfully written final_report.md")

            # Deterministic URL health check and eligibility audit
            try:
                from url_validator import sanitize_report
                print("Auditing and sanitizing job URLs in final report...")
                audit_result = sanitize_report("final_report.md")
                rem_count = audit_result.get("removed_count", 0)
                val_count = audit_result.get("valid_count", 0)
                if rem_count > 0:
                    print(f"Audit complete: {rem_count} closed/invalid positions removed ({val_count} remain active).")
                else:
                    print(f"Audit complete: All {val_count} positions are 100% active and verified.")
            except Exception as e:
                print(f"Warning: URL sanitization failed: {e}", file=sys.stderr)

            # Update persistent memory tracker (seen_jobs.json) with verified active jobs
            try:
                new_jobs = update_seen_jobs("final_report.md")
                print(f"Updated seen_jobs.json: {new_jobs} new positions recorded.")
            except Exception as e:
                print(f"Warning: Failed to update seen_jobs.json: {e}", file=sys.stderr)
        else:
            print("Warning: /final_report.md not found in agent output files.")

        question_data = files.get("/question.txt")
        if question_data:
            q_text = "\n".join(question_data["content"]) if isinstance(question_data["content"], list) else str(question_data["content"])
            Path("question.txt").write_text(q_text, encoding="utf-8")
            print("Successfully written question.txt")

        print("Agent execution completed successfully!")

        # Automatically send report to Telegram if credentials are set (skip if running in GitHub Actions to avoid duplicate)
        if not os.environ.get("GITHUB_ACTIONS"):
            if os.environ.get("TELEGRAM_BOT_TOKEN") and os.environ.get("TELEGRAM_CHAT_ID"):
                print("Sending final report to Telegram...")
                try:
                    from send_report_telegram import send_report_telegram
                    send_report_telegram("final_report.md")
                except Exception as e:
                    print(f"Warning: Failed to send Telegram report: {e}", file=sys.stderr)
    except Exception:
        error_msg = traceback.format_exc()
        print(error_msg, file=sys.stderr)
        _send_failure_alert(error_msg)
        sys.exit(1)

