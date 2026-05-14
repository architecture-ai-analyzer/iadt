"""Download de diagrama a partir do S3 para arquivo temporário local."""

from __future__ import annotations

import os
import tempfile
import urllib.parse
from pathlib import Path

from config.settings import SUPPORTED_EXTENSIONS


def download_object_to_tempfile(s3_client, bucket: str, key: str) -> Path:
    """
    Baixa o objeto para um arquivo temporário com sufixo compatível com o pipeline.
    Caller deve apagar o arquivo após o uso.
    """
    suffix = Path(urllib.parse.unquote_plus(key)).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        suffix = ".pdf"
    fd, path_str = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    path = Path(path_str)
    try:
        s3_client.download_file(bucket, key, str(path))
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return path
