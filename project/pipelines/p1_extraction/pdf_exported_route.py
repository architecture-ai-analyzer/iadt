from pathlib import Path
from typing import Any

import fitz  # PyMuPDF

from llm.multimodal import call_vision_with_text
from pipelines.p1_extraction._prompts import PROMPT, REINFORCED_PROMPT


def extract(pdf_path: Path) -> dict[str, Any]:
    text = _extract_text(pdf_path)
    image_path = _render_first_page(pdf_path)
    return call_vision_with_text(image_path, text, PROMPT, REINFORCED_PROMPT)


def _extract_text(pdf_path: Path) -> str:
    doc = fitz.open(str(pdf_path))
    return "\n".join(page.get_text() for page in doc)


def _render_first_page(pdf_path: Path) -> Path:
    import tempfile
    doc = fitz.open(str(pdf_path))
    page = doc[0]
    mat = fitz.Matrix(2, 2)
    pix = page.get_pixmap(matrix=mat)
    tmp = Path(tempfile.mktemp(suffix=".png"))
    pix.save(str(tmp))
    return tmp
