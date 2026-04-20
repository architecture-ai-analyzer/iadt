from pathlib import Path
from typing import Any

import fitz  # PyMuPDF

from llm.multimodal import call_vision
from pipelines.p1_extraction._prompts import PROMPT, REINFORCED_PROMPT


def extract(pdf_path: Path) -> dict[str, Any]:
    images = _pdf_to_images(pdf_path)
    if not images:
        raise RuntimeError("falha na conversão do PDF")

    # Extrai da primeira página com diagrama relevante
    # Para MVP: processa apenas a primeira página
    return call_vision(images[0], PROMPT, REINFORCED_PROMPT)


def _pdf_to_images(pdf_path: Path) -> list[Path]:
    import tempfile
    doc = fitz.open(str(pdf_path))
    tmp_dir = Path(tempfile.mkdtemp())
    paths = []
    for i, page in enumerate(doc):
        mat = fitz.Matrix(2, 2)  # 2x zoom para resolução adequada
        pix = page.get_pixmap(matrix=mat)
        out = tmp_dir / f"page_{i}.png"
        pix.save(str(out))
        paths.append(out)
    return paths
