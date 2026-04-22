from config.settings import LLM_PROVIDER, CLAUDE_MODEL_TEXT, OPENAI_MODEL_TEXT, OLLAMA_MODEL_TEXT, OLLAMA_BASE_URL
from llm.client import call_with_retry


def call_text(prompt: str, system: str | None = None) -> str:
    def _call():
        if LLM_PROVIDER == "ollama":
            return _ollama_text(prompt, system)
        if LLM_PROVIDER == "openai":
            return _openai_text(prompt, system)
        return _anthropic_text(prompt, system)

    return call_with_retry(_call, context="text_generation")


def _ollama_text(prompt: str, system: str | None) -> str:
    import ollama
    client = ollama.Client(host=OLLAMA_BASE_URL)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat(model=OLLAMA_MODEL_TEXT, messages=messages)
    return response["message"]["content"]


def _anthropic_text(prompt: str, system: str | None) -> str:
    from llm.client import get_client
    kwargs: dict = dict(
        model=CLAUDE_MODEL_TEXT,
        max_tokens=8192,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    if system:
        kwargs["system"] = system
    response = get_client().messages.create(**kwargs)
    return response.content[0].text


def _openai_text(prompt: str, system: str | None) -> str:
    from llm.client import get_openai_client
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = get_openai_client().chat.completions.create(
        model=OPENAI_MODEL_TEXT,
        temperature=0,
        messages=messages,
    )
    return response.choices[0].message.content
