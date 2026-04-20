from pathlib import Path
from typing import Literal

import fitz  # PyMuPDF

from config.settings import PDF_TEXT_THRESHOLD, SUPPORTED_EXTENSIONS
from config.logging_config import get_logger

logger = get_logger(__name__)

FileType = Literal["image", "pdf_exported", "pdf_scanned"]


def classify(file_path: Path) -> FileType:
    ext = file_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"formato não suportado: {ext}")

    if ext in {".png", ".jpg", ".jpeg"}:
        logger.info("file_classified", extra={"extra": {"path": str(file_path), "type": "image"}})
        return "image"

    text = _extract_pdf_text(file_path)
    file_type: FileType = "pdf_exported" if len(text.strip()) >= PDF_TEXT_THRESHOLD else "pdf_scanned"
    logger.info("file_classified", extra={"extra": {"path": str(file_path), "type": file_type, "text_chars": len(text.strip())}})
    return file_type


def _extract_pdf_text(file_path: Path) -> str:
    try:
        doc = fitz.open(str(file_path))
        return "\n".join(page.get_text() for page in doc)
    except Exception as exc:
        logger.warning("pdf_text_extraction_failed", extra={"extra": {"error": str(exc)}})
        return ""
