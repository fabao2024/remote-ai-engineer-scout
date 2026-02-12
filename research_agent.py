import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
load_dotenv()

from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from tavily import TavilyClient

# Reuse the Tavily client across tool invocations
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search via Tavily."""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


sub_research_prompt = """You specialize in investigating remote AI Engineer job opportunities.
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

research_instructions = """You are an expert tech recruiter focused on remote AI Engineer positions.
Write the original user request to `question.txt` first.
Use the research-agent to gather:
- Remote AI Engineer job listings (confirm remote eligibility)
- Companies currently hiring, team focus, and hiring stage
- Core skills, tools, and experience employers expect
- Compensation, location constraints, and visa/contract notes
- Application tactics, networking leads, or differentiators
- search for recent open positions, maximum 2 or 3 weeks old from current date

Iterate with the critique-agent whenever you need help polishing the final report.

When ready, write the report to `final_report.md` in Markdown using this structure:
# Remote AI Engineer Opportunities Brief
## Market Snapshot
## Active Remote Employers
## Representative Openings
## Required Skills & Tech Stack
## Compensation & Location Notes
## Application Strategy
## Sources

Guidelines:
1. Each section should be thorough, using paragraphs and bullet lists only where they add clarity.
2. Pull concrete facts and insights from your research; cite each with [Title](URL).
3. Make sure every role you highlight is remote-first or clearly remote-friendly; note any geographic or time-zone restrictions.
4. If relevant data is scarce, explain gaps and suggest follow-up steps.
5. Keep the language aligned with the users language.

Citation rules:
- Assign sequential citation numbers (1,2,3…)
- End with ## Sources and list `[n] Source Title: URL` per line.

Available tool:
## `internet_search`
Use it to discover current remote AI Engineer roles and supporting information."""

# Configure the chat model (ensure OPENAI_API_KEY is set)
from llm_router import get_llm

# Configure the chat model (ensure OPENAI_API_KEY or ZHIPUAI_API_KEY is set)
model = get_llm(os.environ.get("LLM_MODEL", "openai:gpt-4o-mini"))

# Build the agent with the research and critique subagents
agent = create_deep_agent(
    model=model,
    tools=[internet_search],
    system_prompt=research_instructions,
    subagents=[critique_sub_agent, research_sub_agent],
)

if __name__ == "__main__":
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "Find remote AI Engineer roles hiring now."}]}
    )
    print(result)

    files = result.get("files", {})
    final_data = files.get("/final_report.md")
    if final_data:
        Path("final_report.md").write_text("\n".join(final_data["content"]), encoding="utf-8")
    question_data = files.get("/question.txt")
    if question_data:
        Path("question.txt").write_text("\n".join(question_data["content"]), encoding="utf-8")

