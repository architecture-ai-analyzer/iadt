import base64
from pathlib import Path
from typing import Any

from config.settings import LLM_PROVIDER, CLAUDE_MODEL_VISION, OPENAI_MODEL_VISION
from llm.client import call_with_retry, parse_json_response


def call_vision(image_path: Path, prompt: str, reinforced_prompt: str | None = None) -> dict[str, Any]:
    def _call(p: str):
        if LLM_PROVIDER == "openai":
            return _openai_vision(image_path, p)
        return _anthropic_vision(image_path, p)

    raw = call_with_retry(lambda: _call(prompt), context="vision_extraction")
    try:
        return parse_json_response(raw, context="vision_extraction")
    except ValueError:
        if reinforced_prompt:
            raw2 = call_with_retry(lambda: _call(reinforced_prompt), context="vision_extraction_retry")
            return parse_json_response(raw2, context="vision_extraction_retry")
        raise


def call_vision_with_text(image_path: Path, extracted_text: str, prompt: str, reinforced_prompt: str | None = None) -> dict[str, Any]:
    full_prompt = f"Texto extraído do PDF:\n\n{extracted_text}\n\n---\n\n{prompt}"

    def _call(p: str):
        if LLM_PROVIDER == "openai":
            return _openai_vision_with_text(image_path, extracted_text, p)
        return _anthropic_vision_with_text(image_path, extracted_text, p)

    raw = call_with_retry(lambda: _call(full_prompt), context="vision_text_extraction")
    try:
        return parse_json_response(raw, context="vision_text_extraction")
    except ValueError:
        if reinforced_prompt:
            full_reinforced = f"Texto extraído do PDF:\n\n{extracted_text}\n\n---\n\n{reinforced_prompt}"
            raw2 = call_with_retry(lambda: _call(full_reinforced), context="vision_text_extraction_retry")
            return parse_json_response(raw2, context="vision_text_extraction_retry")
        raise


def _anthropic_vision(image_path: Path, prompt: str) -> str:
    from llm.client import get_client
    image_data = base64.standard_b64encode(image_path.read_bytes()).decode("utf-8")
    response = get_client().messages.create(
        model=CLAUDE_MODEL_VISION,
        max_tokens=4096,
        temperature=0,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": _media_type(image_path), "data": image_data}},
            {"type": "text", "text": prompt},
        ]}],
    )
    return response.content[0].text


def _anthropic_vision_with_text(image_path: Path, extracted_text: str, prompt: str) -> str:
    from llm.client import get_client
    image_data = base64.standard_b64encode(image_path.read_bytes()).decode("utf-8")
    response = get_client().messages.create(
        model=CLAUDE_MODEL_VISION,
        max_tokens=4096,
        temperature=0,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": f"Texto extraído do PDF:\n\n{extracted_text}\n\n---\n\n{prompt}"},
            {"type": "image", "source": {"type": "base64", "media_type": _media_type(image_path), "data": image_data}},
        ]}],
    )
    return response.content[0].text


def _openai_vision(image_path: Path, prompt: str) -> str:
    from llm.client import get_openai_client
    image_data = base64.standard_b64encode(image_path.read_bytes()).decode("utf-8")
    media = _media_type(image_path)
    response = get_openai_client().chat.completions.create(
        model=OPENAI_MODEL_VISION,
        temperature=0,
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:{media};base64,{image_data}"}},
            {"type": "text", "text": prompt},
        ]}],
    )
    return response.choices[0].message.content


def _openai_vision_with_text(image_path: Path, extracted_text: str, prompt: str) -> str:
    from llm.client import get_openai_client
    image_data = base64.standard_b64encode(image_path.read_bytes()).decode("utf-8")
    media = _media_type(image_path)
    full_prompt = f"Texto extraído do PDF:\n\n{extracted_text}\n\n---\n\n{prompt}"
    response = get_openai_client().chat.completions.create(
        model=OPENAI_MODEL_VISION,
        temperature=0,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": full_prompt},
            {"type": "image_url", "image_url": {"url": f"data:{media};base64,{image_data}"}},
        ]}],
    )
    return response.choices[0].message.content


def _media_type(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    return {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "image/png")
