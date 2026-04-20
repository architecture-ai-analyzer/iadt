import time
from pathlib import Path
from typing import Any

import jsonschema

from config.logging_config import get_logger
from pipelines.p1_extraction.classifier import classify
from pipelines.p1_extraction import image_route, pdf_exported_route, pdf_scanned_route
from schemas import load_schema

logger = get_logger(__name__)


def extract(file_path: str | Path) -> dict[str, Any]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"arquivo não encontrado: {path}")

    t0 = time.perf_counter()
    file_type = classify(path)

    routes = {
        "image": image_route.extract,
        "pdf_exported": pdf_exported_route.extract,
        "pdf_scanned": pdf_scanned_route.extract,
    }
    result = routes[file_type](path)

    if "components" not in result:
        raise ValueError("extração incompleta — sem componentes identificados")

    schema = load_schema("canonical.json")
    try:
        jsonschema.validate(result, schema)
    except jsonschema.ValidationError as exc:
        raise ValueError(f"JSON extraído não passa no schema: {exc.message}") from exc

    elapsed = round(time.perf_counter() - t0, 2)
    logger.info("p1_done", extra={"extra": {
        "file_type": file_type,
        "components": len(result.get("components", [])),
        "relationships": len(result.get("relationships", [])),
        "uncertainties": len(result.get("uncertainties", [])),
        "elapsed_s": elapsed,
    }})
    return result
