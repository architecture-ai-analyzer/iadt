import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from pipelines.p1_extraction.classifier import classify


def test_classify_png_returns_image(tmp_path):
    f = tmp_path / "diagram.png"
    f.write_bytes(b"fake")
    assert classify(f) == "image"


def test_classify_jpg_returns_image(tmp_path):
    f = tmp_path / "diagram.jpg"
    f.write_bytes(b"fake")
    assert classify(f) == "image"


def test_classify_invalid_extension_raises(tmp_path):
    f = tmp_path / "diagram.bmp"
    f.write_bytes(b"fake")
    with pytest.raises(ValueError, match="formato não suportado"):
        classify(f)


def test_classify_pdf_with_text_returns_exported(tmp_path):
    f = tmp_path / "diagram.pdf"
    f.write_bytes(b"fake")
    with patch("pipelines.p1_extraction.classifier._extract_pdf_text", return_value="A" * 100):
        result = classify(f)
    assert result == "pdf_exported"


def test_classify_pdf_without_text_returns_scanned(tmp_path):
    f = tmp_path / "diagram.pdf"
    f.write_bytes(b"fake")
    with patch("pipelines.p1_extraction.classifier._extract_pdf_text", return_value=""):
        result = classify(f)
    assert result == "pdf_scanned"
