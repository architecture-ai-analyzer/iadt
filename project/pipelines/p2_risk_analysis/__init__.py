import time
from typing import Any

import jsonschema

from config.logging_config import get_logger
from pipelines.p2_risk_analysis.reasoning import generate_analysis
from schemas import load_schema

logger = get_logger(__name__)


def analyze(canonical: dict[str, Any], semantic: dict[str, Any]) -> dict[str, Any]:
    if "components" not in canonical:
        raise ValueError("JSON de entrada inválido para análise: campo 'components' ausente")

    t0 = time.perf_counter()
    analysis = generate_analysis(canonical, semantic)

    enriched = {
        **canonical,
        "observations": semantic["observations"],
        "intent": semantic["intent"],
        "pattern": semantic["pattern"],
        "inferences": analysis["inferences"],
        "concerns": analysis["concerns"],
        "limitations": analysis["limitations"],
    }

    schema = load_schema("enriched.json")
    try:
        jsonschema.validate(enriched, schema)
    except jsonschema.ValidationError as exc:
        raise ValueError(f"JSON enriquecido não passa no schema: {exc.message}") from exc

    elapsed = round(time.perf_counter() - t0, 2)
    severity_dist: dict[str, int] = {}
    for c in analysis["concerns"]:
        severity_dist[c["severity"]] = severity_dist.get(c["severity"], 0) + 1

    logger.info("p2_done", extra={"extra": {
        "components": len(canonical["components"]),
        "relationships": len(canonical.get("relationships", [])),
        "inferences": len(analysis["inferences"]),
        "concerns": len(analysis["concerns"]),
        "limitations": len(analysis["limitations"]),
        "severity_distribution": severity_dist,
        "elapsed_s": elapsed,
    }})
    return enriched
