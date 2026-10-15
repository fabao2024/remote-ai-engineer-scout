import os
from typing import Literal

from langchain_community.chat_models import ChatZhipuAI
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel

# Supported providers
Provider = Literal["openai", "zhipu", "gemini", "google"]

def get_llm(model_str: str | None = None) -> BaseChatModel:
    """
    Get a chat model instance based on the model string.

    Format: "provider:model_name"
    Examples:
        - "gemini:gemini-4-argon" (Default)
        - "openai:gpt-4o-mini"
        - "zhipu:glm-4"
        - "zhipu:glm-4-plus" or "zhipu:glm-4-0520"
        - "gemini:gemini-2.5-flash"

    Env Vars:
        User can set `LLM_MODEL` to override default.
        Resulting provider requires its API key:
        - GEMINI_API_KEY or GOOGLE_API_KEY
        - OPENAI_API_KEY
        - ZHIPUAI_API_KEY
    """
    # 1. Determine model string
    if not model_str:
        model_str = os.environ.get("LLM_MODEL", "gemini:gemini-4-argon")

    # 2. Parse provider and model name
    if ":" in model_str:
        provider, model_name = model_str.split(":", 1)
    else:
        # Fallback to OpenAI if no colon found (assuming it's just a model name for OpenAI)
        provider = "openai"
        model_name = model_str

    # 3. Instantiate specific provider
    if provider == "zhipu":
        api_key = os.environ.get("ZHIPUAI_API_KEY")
        if not api_key:
            raise ValueError("ZHIPUAI_API_KEY environment variable is not set.")

        return ChatZhipuAI(
            model=model_name,
            api_key=api_key,
            temperature=0.5,
        )

    elif provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")

        return ChatOpenAI(
            model=model_name, # e.g. "gpt-4o-mini"
            api_key=api_key,
            temperature=0,
            max_retries=6,  # Retry up to 6 times on rate limit / transient errors
        )

    elif provider in ("gemini", "google"):
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is not set.")

        return ChatGoogleGenerativeAI(
            model=model_name,
            api_key=api_key,
            temperature=0,
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
