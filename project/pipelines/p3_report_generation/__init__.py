import json
import time
from pathlib import Path
from typing import Any

from config.logging_config import get_logger
from domain.report_layout import REQUIRED_SECTIONS
from llm.text import call_text

logger = get_logger(__name__)

_PROMPT_TEMPLATE = (Path(__file__).parent.parent.parent / "prompts" / "relatorio.md").read_text(encoding="utf-8")


def generate(enriched: dict[str, Any]) -> str:
    intent = enriched.get("intent", {})
    pattern = enriched.get("pattern", {})
    canonical = {
        "components": enriched.get("components", []),
        "relationships": enriched.get("relationships", []),
        "uncertainties": enriched.get("uncertainties", []),
    }
    observations = enriched.get("observations", [])
    inferences = enriched.get("inferences", [])
    concerns = enriched.get("concerns", [])
    limitations = enriched.get("limitations", [])

    observations_text = "\n".join(
        f"- [{obs['id']}] {obs['statement']}" for obs in observations
    )
    inferences_text = "\n".join(
        f"- [{inf['id']}] {inf['hypothesis']} (confiança: {inf['confidence']}, cita: {', '.join(inf['cites'])})"
        for inf in inferences
    )
    concerns_text = "\n".join(
        f"- [{c['id']}] {c['title']} | severidade: {c['severity']} | categoria: {c['category']} | deriva de: {', '.join(c['derived_from'])}\n"
        f"  {c['description']}\n"
        f"  Componentes: {', '.join(c['affected_components'])}"
        for c in concerns
    )
    limitations_text = "\n".join(
        f"- [{lim['id']}] {lim['statement']} (razão: {lim['reason']})" for lim in limitations
    )

    prompt = (
        _PROMPT_TEMPLATE
        .replace("{pattern_type}", pattern.get("type", "other"))
        .replace("{pattern_description}", pattern.get("description", ""))
        .replace("{intent_summary}", intent.get("summary", "não identificada"))
        .replace("{intent_kind}", intent.get("kind", "mixed"))
        .replace("{canonical_json}", json.dumps(canonical, ensure_ascii=False, indent=2))
        .replace("{observations_json}", observations_text or "(nenhuma observação registrada)")
        .replace("{inferences_json}", inferences_text or "(nenhuma inference gerada)")
        .replace("{concerns_json}", concerns_text or "(nenhum concern identificado)")
        .replace("{limitations_json}", limitations_text or "(nenhuma limitation registrada)")
    )

    t0 = time.perf_counter()
    report = _call_with_section_retry(prompt)
    elapsed = round(time.perf_counter() - t0, 2)

    sections_present = [s for s in REQUIRED_SECTIONS if s in report]
    logger.info("p3_done", extra={"extra": {
        "elapsed_s": elapsed,
        "report_chars": len(report),
        "sections_present": len(sections_present),
        "sections_missing": [s for s in REQUIRED_SECTIONS if s not in report],
    }})
    return report


def _call_with_section_retry(prompt: str) -> str:
    report = call_text(prompt)
    missing = [s for s in REQUIRED_SECTIONS if s not in report]
    if not missing:
        return report

    if not report.strip():
        raise RuntimeError("LLM retornou resposta vazia")

    reinforced = prompt + f"\n\nATENÇÃO: As seções obrigatórias ausentes na resposta anterior foram: {missing}. Inclua-as obrigatoriamente."
    report = call_text(reinforced)

    missing = [s for s in REQUIRED_SECTIONS if s not in report]
    if missing:
        raise RuntimeError(f"relatório incompleto — seções ausentes: {missing}")
    return report
