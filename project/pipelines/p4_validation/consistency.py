from typing import Any

from config.logging_config import get_logger

logger = get_logger(__name__)


def validate(report: str, enriched: dict[str, Any]) -> list[str]:
    errors = []
    warnings = []
    errors.extend(_check_fabricated_components(report, enriched))
    errors.extend(_check_id_integrity(enriched))
    concern_errors, concern_warnings = _check_missing_concerns(report, enriched)
    errors.extend(concern_errors)
    warnings.extend(concern_warnings)
    errors.extend(_check_concern_limitation_separation(report, enriched))
    errors.extend(_check_comparative_diagram(report, enriched))

    if warnings:
        logger.warning("p4_warnings", extra={"extra": {"warnings": warnings}})

    return errors


def _check_fabricated_components(report: str, enriched: dict[str, Any]) -> list[str]:
    known = {c["name"].lower() for c in enriched.get("components", [])}
    errors = []
    in_section = False
    for line in report.splitlines():
        if "## 2. Componentes identificados" in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip():
            stripped = line.strip().lstrip("-*# ").strip()
            if len(stripped) > 10 and not any(name in stripped.lower() for name in known):
                errors.append(f"possível componente fabricado detectado na seção 2: '{stripped[:60]}'")
    return errors


def _check_id_integrity(enriched: dict[str, Any]) -> list[str]:
    obs_ids = {obs["id"] for obs in enriched.get("observations", [])}
    inf_ids = {inf["id"] for inf in enriched.get("inferences", [])}
    errors = []

    for inf in enriched.get("inferences", []):
        bad = [c for c in inf.get("cites", []) if c not in obs_ids]
        if bad:
            errors.append(f"inference {inf['id']} cita observações inexistentes: {bad}")

    for concern in enriched.get("concerns", []):
        bad = [d for d in concern.get("derived_from", []) if d not in inf_ids]
        if bad:
            errors.append(f"concern {concern['id']} referencia inferences inexistentes: {bad}")

    return errors


def _check_missing_concerns(report: str, enriched: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors = []
    warnings = []
    report_lower = report.lower()
    for concern in enriched.get("concerns", []):
        title_lower = concern["title"].lower()
        mentioned = title_lower in report_lower
        if not mentioned:
            if concern["severity"] in ("high", "medium"):
                errors.append(f"concern '{concern['title']}' (severidade {concern['severity']}) não aparece na seção 4")
            else:
                warnings.append(f"concern '{concern['title']}' (severidade low) não mencionado no relatório")
    return errors, warnings


def _check_concern_limitation_separation(report: str, enriched: dict[str, Any]) -> list[str]:
    errors = []
    section4 = _extract_section(report, "## 4. Riscos arquiteturais", "## 5.")
    section6 = _extract_section(report, "## 6. Limitações da análise", "## 7.")

    concern_titles = [c["title"].lower() for c in enriched.get("concerns", [])]
    limitation_statements = [lim["statement"].lower() for lim in enriched.get("limitations", [])]

    for title in concern_titles:
        if title in section6.lower():
            errors.append(f"concern '{title}' aparece na seção 6 (limitações) — concerns pertencem à seção 4")

    for stmt in limitation_statements:
        stmt_words = [w for w in stmt.split() if len(w) > 4][:3]
        if any(w in section4.lower() for w in stmt_words):
            errors.append(f"limitation '{stmt[:60]}' parece estar na seção 4 (riscos) — limitations pertencem à seção 6")

    return errors


def _check_comparative_diagram(report: str, enriched: dict[str, Any]) -> list[str]:
    intent = enriched.get("intent", {})
    if intent.get("kind") != "comparison":
        return []

    compared_items = intent.get("compared_items") or []
    section1 = _extract_section(report, "## 1. Resumo executivo", "## 2.")
    section1_lower = section1.lower()

    for item in compared_items:
        if item.lower() not in section1_lower:
            return [
                f"diagrama comparativo: '{item}' não aparece na seção 1 (Resumo executivo). "
                "Diagramas comparativos devem explicar o que está sendo comparado."
            ]
    return []


def _extract_section(report: str, start_header: str, end_prefix: str) -> str:
    lines = report.splitlines()
    capturing = False
    result = []
    for line in lines:
        if start_header in line:
            capturing = True
            continue
        if capturing and line.startswith(end_prefix):
            break
        if capturing:
            result.append(line)
    return "\n".join(result)
