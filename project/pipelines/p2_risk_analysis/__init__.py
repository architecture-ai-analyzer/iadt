import time
from typing import Any

import jsonschema

from config.logging_config import get_logger
from pipelines.p2_risk_analysis.registry import run_all
from schemas import load_schema

logger = get_logger(__name__)


def analyze(canonical: dict[str, Any]) -> dict[str, Any]:
    if "components" not in canonical:
        raise ValueError("JSON de entrada inválido para análise de riscos")

    components = canonical["components"]
    relationships = canonical.get("relationships", [])
    if not relationships:
        logger.warning("p2_no_relationships", extra={"extra": {"warning": "campo relationships ausente ou vazio"}})

    t0 = time.perf_counter()
    risks = run_all(components, relationships)

    enriched = {**canonical, "risks": risks}

    schema = load_schema("enriched.json")
    try:
        jsonschema.validate(enriched, schema)
    except jsonschema.ValidationError as exc:
        raise ValueError(f"JSON enriquecido não passa no schema: {exc.message}") from exc

    elapsed = round(time.perf_counter() - t0, 2)
    severity_dist = {}
    for r in risks:
        severity_dist[r["severity"]] = severity_dist.get(r["severity"], 0) + 1

    logger.info("p2_done", extra={"extra": {
        "components": len(components),
        "relationships": len(relationships),
        "risks": len(risks),
        "severity_distribution": severity_dist,
        "elapsed_s": elapsed,
    }})
    return enriched
