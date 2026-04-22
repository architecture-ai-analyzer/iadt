from config.settings import LLM_PROVIDER, CLAUDE_MODEL_TEXT, OPENAI_MODEL_TEXT
from llm.client import call_with_retry


def call_text(prompt: str, system: str | None = None) -> str:
    def _call():
        if LLM_PROVIDER == "openai":
            return _openai_text(prompt, system)
        return _anthropic_text(prompt, system)

    return call_with_retry(_call, context="text_generation")


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
