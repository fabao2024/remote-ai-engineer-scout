import os
from typing import Literal

from langchain_community.chat_models import ChatZhipuAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

# Supported providers
Provider = Literal["openai", "zhipu", "gemini", "google"]

DEFAULT_MODEL = "gemini:gemini-2.5-flash"
DEFAULT_FALLBACK_MODELS = "openai:gpt-4o-mini,zhipu:glm-4-flash"


def _max_retries() -> int:
    """Return a short retry budget so permanent quota errors fail over promptly."""
    try:
        return max(0, int(os.environ.get("LLM_MAX_RETRIES", "1")))
    except ValueError:
        return 1


def _build_model(model_str: str) -> BaseChatModel:
    """Build one provider model and fail clearly when its credential is absent."""
    if ":" in model_str:
        provider, model_name = model_str.split(":", 1)
    else:
        provider = "openai"
        model_name = model_str

    provider = provider.strip().lower()
    model_name = model_name.strip()
    retries = _max_retries()

    if provider == "zhipu":
        api_key = os.environ.get("ZHIPUAI_API_KEY")
        if not api_key:
            raise ValueError("ZHIPUAI_API_KEY environment variable is not set.")
        return ChatZhipuAI(
            model=model_name,
            api_key=api_key,
            temperature=0.5,
        )

    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            temperature=0,
            max_retries=retries,
        )

    if provider in ("gemini", "google"):
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is not set.")
        return ChatGoogleGenerativeAI(
            model=model_name,
            api_key=api_key,
            temperature=0,
            max_retries=retries,
        )

    raise ValueError(f"Unsupported LLM provider: {provider}")


def _configured_model_names(primary: str) -> list[str]:
    """Return the primary and configured fallback model names without duplicates."""
    configured_fallbacks = os.environ.get(
        "LLM_FALLBACK_MODELS",
        DEFAULT_FALLBACK_MODELS,
    )
    names = [primary]
    names.extend(item.strip() for item in configured_fallbacks.split(",") if item.strip())

    unique: list[str] = []
    for name in names:
        if name not in unique:
            unique.append(name)
    return unique


def get_llm(model_str: str | None = None) -> Runnable:
    """Build the configured LLM with credential-aware provider fallbacks.

    ``LLM_MODEL`` selects the preferred provider. ``LLM_FALLBACK_MODELS`` is a
    comma-separated list such as ``gemini:gemini-2.5-flash,zhipu:glm-4-flash``.
    Providers without credentials are skipped. Once a provider is built, the
    LangChain fallback wrapper handles quota and transient invocation failures.
    """
    primary = (model_str or os.environ.get("LLM_MODEL") or DEFAULT_MODEL).strip()
    models: list[BaseChatModel] = []
    configuration_errors: list[str] = []

    for candidate in _configured_model_names(primary):
        try:
            models.append(_build_model(candidate))
        except ValueError as exc:
            configuration_errors.append(f"{candidate}: {exc}")

    if not models:
        details = "; ".join(configuration_errors) or "no model configured"
        raise ValueError(f"No usable LLM provider is configured: {details}")

    if len(models) == 1:
        return models[0]

    return models[0].with_fallbacks(models[1:])
