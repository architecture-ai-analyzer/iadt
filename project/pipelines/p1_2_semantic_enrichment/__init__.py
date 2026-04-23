import json
import time
from typing import Any

import jsonschema

from config.logging_config import get_logger
from llm.client import parse_json_response
from llm.text import call_text
from pipelines.p1_2_semantic_enrichment._prompts import PROMPT
from schemas import load_schema

logger = get_logger(__name__)
_schema = load_schema("semantic.json")


def enrich(canonical: dict[str, Any]) -> dict[str, Any]:
    t0 = time.perf_counter()

    canonical_json = json.dumps(canonical, ensure_ascii=False, indent=2)
    prompt = PROMPT.replace("{canonical_json}", canonical_json)

    raw = call_text(prompt)
    result = parse_json_response(raw, context="semantic_enrichment")
    result = _assign_ids(result)

    try:
        jsonschema.validate(result, _schema)
    except jsonschema.ValidationError as exc:
        reinforced_prompt = (
            prompt
            + f"\n\nAtenção: sua resposta anterior falhou na validação de schema. Erro: {exc.message}\n"
            "Corrija e retorne apenas o JSON válido."
        )
        raw = call_text(reinforced_prompt)
        result = parse_json_response(raw, context="semantic_enrichment_retry")
        result = _assign_ids(result)
        jsonschema.validate(result, _schema)

    elapsed = round(time.perf_counter() - t0, 2)
    logger.info(
        "semantic_enrichment_ok",
        extra={
            "extra": {
                "observations_count": len(result["observations"]),
                "intent_kind": result["intent"]["kind"],
                "pattern_type": result["pattern"]["type"],
                "pattern_confidence": result["pattern"]["confidence"],
                "elapsed_s": elapsed,
            }
        },
    )
    return result


def _assign_ids(result: dict[str, Any]) -> dict[str, Any]:
    for i, obs in enumerate(result.get("observations", []), start=1):
        obs["id"] = f"O{i}"
        if "refs" not in obs:
            obs["refs"] = []
    return result
