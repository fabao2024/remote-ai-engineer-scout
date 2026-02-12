#!/usr/bin/env python3
"""Send the final report via Telegram."""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_API = "https://api.telegram.org/bot{token}"


def send_report_telegram(
    report_path: str = "final_report.md",
    bot_token: str = None,
    chat_id: str = None,
) -> bool:
    """Send the final report as a Telegram message + file attachment."""
    bot_token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("Warning: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set.")
        return False

    report_file = Path(report_path)
    if not report_file.exists():
        print(f"Error: Report file not found: {report_path}")
        return False

    report_content = report_file.read_text(encoding="utf-8")
    base_url = TELEGRAM_API.format(token=bot_token)

    # Telegram messages have a 4096 char limit — truncate if needed
    max_len = 4096
    if len(report_content) > max_len:
        message = report_content[: max_len - 30] + "\n\n... (see full report attached)"
    else:
        message = report_content

    try:
        # Send the report as a formatted message
        r = httpx.post(
            f"{base_url}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            },
            timeout=15,
        )

        # If Markdown parsing fails, retry as plain text
        if not r.json().get("ok"):
            r = httpx.post(
                f"{base_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "disable_web_page_preview": True,
                },
                timeout=15,
            )

        # Send the .md file as an attachment
        with open(report_path, "rb") as f:
            httpx.post(
                f"{base_url}/sendDocument",
                data={"chat_id": chat_id, "caption": "Full report attached"},
                files={"document": (report_file.name, f, "text/markdown")},
                timeout=15,
            )

        print(f"Telegram message sent to chat {chat_id}")
        return True
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
        return False


if __name__ == "__main__":
    success = send_report_telegram()
    raise SystemExit(0 if success else 1)
