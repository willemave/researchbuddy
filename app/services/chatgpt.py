"""Helpers for building ChatGPT continuation links."""

from __future__ import annotations

from urllib.parse import quote

CHATGPT_CONTINUE_BASE_URL = "https://chatgpt.com/?query="
CHATGPT_CONTINUE_PROMPT_PREFIX = "Continue this conversation based on the summary below:\n\n"
CHATGPT_CONTINUE_MAX_CHARS = 2000


def build_chatgpt_continue_url(summary: str) -> str:
    """Build a ChatGPT URL that seeds a new conversation from a summary.

    Args:
        summary: The text to seed into ChatGPT.

    Returns:
        A ChatGPT URL with the summary embedded in the query string.
    """

    cleaned_summary = summary.strip() or "Continue this conversation."
    clipped_summary = _clip_text(cleaned_summary, CHATGPT_CONTINUE_MAX_CHARS)
    prompt = f"{CHATGPT_CONTINUE_PROMPT_PREFIX}{clipped_summary}"
    return f"{CHATGPT_CONTINUE_BASE_URL}{quote(prompt, safe='')}"


def _clip_text(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return f"{value[: max(0, limit - 3)].rstrip()}..."
