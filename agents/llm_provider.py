from langchain_ollama import ChatOllama


def get_llm(provider="local", api_key=None, model=None, base_url=None):
    provider = (provider or "local").lower().strip()

    # ============================================================
    # LOCAL OLLAMA
    # ============================================================
    if provider == "local":
        return ChatOllama(
            model=model or "qwen3:8b",
            temperature=0.1,
        )

    # ============================================================
    # xAI / GROK
    # ============================================================
    if provider == "xai":
        if not api_key:
            raise ValueError(
                "xAI API key is required when provider='xai'."
            )

        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model or "grok-4.1-fast",
            temperature=0.1,
            api_key=api_key,
            base_url="https://api.x.ai/v1",
        )

    # ============================================================
    # OPENAI
    # ============================================================
    if provider == "openai":
        if not api_key:
            raise ValueError(
                "OpenAI API key is required when provider='openai'."
            )

        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model or "gpt-5",
            temperature=0.1,
            api_key=api_key,
        )

    # ============================================================
    # GOOGLE GEMINI
    # ============================================================
    if provider == "gemini":
        if not api_key:
            raise ValueError(
                "Gemini API key is required when provider='gemini'."
            )

        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=model or "gemini-3.6-flash",
            temperature=0.1,
            google_api_key=api_key,
        )

    # ============================================================
    # CUSTOM OPENAI-COMPATIBLE PROVIDER
    # ============================================================
    if provider == "custom":
        if not api_key:
            raise ValueError(
                "API key is required when provider='custom'."
            )

        if not base_url:
            raise ValueError(
                "Base URL is required when provider='custom'."
            )

        if not model:
            raise ValueError(
                "Model is required when provider='custom'."
            )

        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model,
            temperature=0.1,
            api_key=api_key,
            base_url=base_url,
        )

    # ============================================================
    # INVALID PROVIDER
    # ============================================================
    raise ValueError(
        f"Unsupported LLM provider: {provider}. "
        "Use: local, xai, openai, gemini, custom."
    )