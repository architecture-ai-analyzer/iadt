from pathlib import Path
from typing import Any

from llm.multimodal import call_vision
from pipelines.p1_extraction._prompts import PROMPT, REINFORCED_PROMPT


def extract(image_path: Path) -> dict[str, Any]:
    return call_vision(image_path, PROMPT, REINFORCED_PROMPT)
