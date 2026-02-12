import os
from typing import Literal

from langchain_community.chat_models import ChatZhipuAI
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

# Supported providers
Provider = Literal["openai", "zhipu"]

def get_llm(model_str: str | None = None) -> BaseChatModel:
    """
    Get a chat model instance based on the model string.

    Format: "provider:model_name"
    Examples:
        - "openai:gpt-4o-mini" (Default)
        - "zhipu:glm-4"
        - "zhipu:glm-4-plus" or "zhipu:glm-4-0520"

    Env Vars:
        User can set `LLM_MODEL` to override default.
        Resulting provider requires its API key:
        - OPENAI_API_KEY
        - ZHIPUAI_API_KEY
    """
    # 1. Determine model string
    if not model_str:
        model_str = os.environ.get("LLM_MODEL", "openai:gpt-4o-mini")

    # 2. Parse provider and model name
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
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
