import base64
from pathlib import Path
from typing import Any

from config.settings import CLAUDE_MODEL_VISION
from llm.client import call_with_retry, get_client, parse_json_response


def call_vision(image_path: Path, prompt: str, reinforced_prompt: str | None = None) -> dict[str, Any]:
    image_data = base64.standard_b64encode(image_path.read_bytes()).decode("utf-8")
    media_type = _media_type(image_path)

    def _call(p: str):
        response = get_client().messages.create(
            model=CLAUDE_MODEL_VISION,
            max_tokens=4096,
            temperature=0,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}},
                    {"type": "text", "text": p},
                ],
            }],
        )
        return response.content[0].text

    raw = call_with_retry(lambda: _call(prompt), context="vision_extraction")
    try:
        return parse_json_response(raw, context="vision_extraction")
    except ValueError:
        if reinforced_prompt:
            raw2 = call_with_retry(lambda: _call(reinforced_prompt), context="vision_extraction_retry")
            return parse_json_response(raw2, context="vision_extraction_retry")
        raise


def call_vision_with_text(image_path: Path, extracted_text: str, prompt: str, reinforced_prompt: str | None = None) -> dict[str, Any]:
    image_data = base64.standard_b64encode(image_path.read_bytes()).decode("utf-8")
    media_type = _media_type(image_path)

    def _call(p: str):
        response = get_client().messages.create(
            model=CLAUDE_MODEL_VISION,
            max_tokens=4096,
            temperature=0,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Texto extraído do PDF:\n\n{extracted_text}\n\n---\n\n{p}"},
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}},
                ],
            }],
        )
        return response.content[0].text

    raw = call_with_retry(lambda: _call(prompt), context="vision_text_extraction")
    try:
        return parse_json_response(raw, context="vision_text_extraction")
    except ValueError:
        if reinforced_prompt:
            raw2 = call_with_retry(lambda: _call(reinforced_prompt), context="vision_text_extraction_retry")
            return parse_json_response(raw2, context="vision_text_extraction_retry")
        raise


def _media_type(path: Path) -> str:
    ext = path.suffix.lower()
    return {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext.lstrip("."), "image/png")
