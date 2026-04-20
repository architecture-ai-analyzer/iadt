from pipelines.p4_validation import validate
from pipelines.p4_validation.structure import REQUIRED_SECTIONS


def _make_report(missing_section: str | None = None) -> str:
    sections = [s for s in REQUIRED_SECTIONS if s != missing_section]
    return "\n\n".join(f"{s}\nConteúdo da seção." for s in sections)


def _make_enriched(components=None, risks=None):
    return {
        "components": components or [{"name": "API GW", "type": "gateway"}],
        "relationships": [],
        "uncertainties": [],
        "risks": risks or [],
    }


def test_valid_report_approved():
    report = _make_report()
    report += "\n\nAPI GW é o componente principal."
    result = validate(report, _make_enriched())
    assert result.approved


def test_missing_section_rejected():
    report = _make_report(missing_section="## 5. Recomendações")
    result = validate(report, _make_enriched())
    assert not result.approved
    assert any("Recomendações" in e for e in result.errors)


def test_missing_risk_in_report_rejected():
    enriched = _make_enriched(risks=[{
        "type": "centralized_database",
        "description": "DB centralizado atendendo múltiplos serviços",
        "affected_components": ["DB"],
        "severity": "medium",
        "evidence": "3 conexões",
    }])
    report = _make_report()
    result = validate(report, enriched)
    assert not result.approved
    assert any("centralized_database" in e or "centraliz" in e for e in result.errors)
