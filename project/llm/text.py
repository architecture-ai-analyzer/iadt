from config.settings import CLAUDE_MODEL_TEXT
from llm.client import call_with_retry, get_client


def call_text(prompt: str, system: str | None = None) -> str:
    messages = [{"role": "user", "content": prompt}]

    def _call():
        kwargs: dict = dict(
            model=CLAUDE_MODEL_TEXT,
            max_tokens=8192,
            temperature=0,
            messages=messages,
        )
        if system:
            kwargs["system"] = system
        response = get_client().messages.create(**kwargs)
        return response.content[0].text

    return call_with_retry(_call, context="text_generation")
