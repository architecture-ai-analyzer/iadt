import json
import time
from typing import Any

import anthropic

from config.logging_config import get_logger
from config.settings import ANTHROPIC_API_KEY, LLM_MAX_RETRIES

logger = get_logger(__name__)
_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def call_with_retry(
    call_fn,
    context: str,
    max_retries: int = LLM_MAX_RETRIES,
) -> str:
    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            t0 = time.perf_counter()
            result = call_fn()
            elapsed = round(time.perf_counter() - t0, 2)
            logger.info("llm_call_ok", extra={"extra": {"context": context, "attempt": attempt, "elapsed_s": elapsed}})
            return result
        except Exception as exc:
            last_error = exc
            logger.warning("llm_call_failed", extra={"extra": {"context": context, "attempt": attempt, "error": str(exc)}})
    raise RuntimeError(f"falha na chamada LLM ({context}) após {max_retries + 1} tentativas: {last_error}") from last_error


def parse_json_response(raw: str, context: str) -> dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"resposta da IA fora do formato esperado ({context}): {exc}") from exc
