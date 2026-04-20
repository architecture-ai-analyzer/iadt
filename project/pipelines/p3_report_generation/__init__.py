import json
import time
from pathlib import Path
from typing import Any

from config.logging_config import get_logger
from llm.text import call_text

logger = get_logger(__name__)

_PROMPT_TEMPLATE = (Path(__file__).parent.parent.parent / "prompts" / "relatorio.md").read_text(encoding="utf-8")

REQUIRED_SECTIONS = [
    "## 1. Resumo executivo",
    "## 2. Componentes identificados",
    "## 3. Relações observadas",
    "## 4. Riscos arquiteturais",
    "## 5. Recomendações",
    "## 6. Limitações da análise",
    "## 7. Nível de confiança",
]


def generate(enriched: dict[str, Any]) -> str:
    prompt = _PROMPT_TEMPLATE.replace("{enriched_json}", json.dumps(enriched, ensure_ascii=False, indent=2))

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
