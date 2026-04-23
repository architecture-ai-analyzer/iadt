import json
from pathlib import Path
from typing import Any

import jsonschema

from llm.client import parse_json_response
from llm.text import call_text

_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "reasoning.md"
_PROMPT_TEMPLATE: str = _PROMPT_PATH.read_text(encoding="utf-8")

_ENRICHED_SCHEMA_SLICE = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["inferences", "concerns", "limitations"],
    "properties": {
        "inferences": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "hypothesis", "cites", "confidence"],
                "properties": {
                    "id": {"type": "string", "pattern": "^I[0-9]+$"},
                    "hypothesis": {"type": "string", "minLength": 1},
                    "cites": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
                },
            },
        },
        "concerns": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "title", "description", "derived_from", "affected_components", "severity", "category"],
                "properties": {
                    "id": {"type": "string", "pattern": "^C[0-9]+$"},
                    "title": {"type": "string", "minLength": 1},
                    "description": {"type": "string", "minLength": 1},
                    "derived_from": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "affected_components": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                    "category": {"type": "string", "enum": ["availability", "security", "scalability", "coupling", "data", "operational", "other"]},
                },
            },
        },
        "limitations": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "statement", "reason"],
                "properties": {
                    "id": {"type": "string", "pattern": "^L[0-9]+$"},
                    "statement": {"type": "string", "minLength": 1},
                    "reason": {"type": "string", "enum": ["ambiguous_diagram", "missing_label", "out_of_scope", "low_confidence"]},
                },
            },
        },
    },
}


def generate_analysis(canonical: dict[str, Any], semantic: dict[str, Any]) -> dict[str, Any]:
    observations = semantic["observations"]
    intent = semantic["intent"]
    pattern = semantic["pattern"]

    observations_lines = []
    for obs in observations:
        observations_lines.append(f"- [{obs['id']}] {obs['statement']} (base: {obs['basis']['detail']})")
    observations_text = "\n".join(observations_lines)

    prompt = (
        _PROMPT_TEMPLATE
        .replace("{canonical_json}", json.dumps(canonical, ensure_ascii=False, indent=2))
        .replace("{observations_json}", observations_text)
        .replace("{intent_summary}", intent["summary"])
        .replace("{intent_kind}", intent["kind"])
        .replace("{pattern_type}", pattern["type"])
        .replace("{pattern_description}", pattern.get("description", ""))
        .replace("{pattern_confidence}", str(pattern["confidence"]))
    )

    raw = call_text(prompt)
    result = parse_json_response(raw, context="reasoning")
    result = _assign_ids(result)

    try:
        jsonschema.validate(result, _ENRICHED_SCHEMA_SLICE)
        _validate_id_references(result, observations)
    except (jsonschema.ValidationError, ValueError) as exc:
        reinforced_prompt = (
            prompt
            + f"\n\nAtenção: sua resposta anterior falhou na validação. Erro: {exc}\n"
            "Corrija e retorne apenas o JSON válido. Certifique-se de que:\n"
            "- 'cites' em cada inference usa apenas IDs de observações fornecidos (O1, O2, ...)\n"
            "- 'derived_from' em cada concern usa apenas IDs de inferences que você gerou (I1, I2, ...)\n"
        )
        raw = call_text(reinforced_prompt)
        result = parse_json_response(raw, context="reasoning_retry")
        result = _assign_ids(result)
        jsonschema.validate(result, _ENRICHED_SCHEMA_SLICE)
        _validate_id_references(result, observations)

    return result


def _assign_ids(result: dict[str, Any]) -> dict[str, Any]:
    for i, item in enumerate(result.get("inferences", []), start=1):
        item["id"] = f"I{i}"
    for i, item in enumerate(result.get("concerns", []), start=1):
        item["id"] = f"C{i}"
    for i, item in enumerate(result.get("limitations", []), start=1):
        item["id"] = f"L{i}"
    return result


def _validate_id_references(result: dict[str, Any], observations: list[dict]) -> None:
    obs_ids = {obs["id"] for obs in observations}
    inf_ids = {inf["id"] for inf in result.get("inferences", [])}

    for inf in result.get("inferences", []):
        bad = [c for c in inf.get("cites", []) if c not in obs_ids]
        if bad:
            raise ValueError(f"Inference {inf['id']} cita IDs de observação inexistentes: {bad}")

    for concern in result.get("concerns", []):
        bad = [d for d in concern.get("derived_from", []) if d not in inf_ids]
        if bad:
            raise ValueError(f"Concern {concern['id']} referencia IDs de inference inexistentes: {bad}")
