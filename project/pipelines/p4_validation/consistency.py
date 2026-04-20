from typing import Any


def validate(report: str, enriched: dict[str, Any]) -> list[str]:
    errors = []
    errors.extend(_check_fabricated_components(report, enriched))
    errors.extend(_check_missing_risks(report, enriched))
    return errors


def _check_fabricated_components(report: str, enriched: dict[str, Any]) -> list[str]:
    known = {c["name"].lower() for c in enriched.get("components", [])}
    errors = []
    # Varre linhas da seção de componentes procurando nomes não mapeados
    in_section = False
    for line in report.splitlines():
        if "## 2. Componentes identificados" in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip():
            for name in known:
                if name in line.lower():
                    break
            else:
                # linha com conteúdo e nenhum componente conhecido
                # heurística simples: skip linhas muito curtas ou de formatação
                stripped = line.strip().lstrip("-*# ").strip()
                if len(stripped) > 10 and not any(name in stripped.lower() for name in known):
                    errors.append(f"possível componente fabricado detectado na seção 2: '{stripped[:60]}'")
    return errors


def _check_missing_risks(report: str, enriched: dict[str, Any]) -> list[str]:
    errors = []
    for risk in enriched.get("risks", []):
        risk_type = risk["type"].replace("_", " ")
        risk_desc_words = risk["description"].lower().split()[:4]
        mentioned = risk_type in report.lower() or any(w in report.lower() for w in risk_desc_words if len(w) > 4)
        if not mentioned:
            errors.append(f"risco '{risk['type']}' não foi incluído no relatório")
    return errors
