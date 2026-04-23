from pipelines.p4_validation import validate
from pipelines.p4_validation.structure import REQUIRED_SECTIONS


def _make_report(missing_section: str | None = None, extra_content: str = "") -> str:
    sections = [s for s in REQUIRED_SECTIONS if s != missing_section]
    report = "\n\n".join(f"{s}\nConteúdo da seção." for s in sections)
    return report + "\n\nAPI GW é o componente principal.\n" + extra_content


def _make_enriched(
    components=None,
    observations=None,
    inferences=None,
    concerns=None,
    limitations=None,
    intent_kind="flow",
    compared_items=None,
):
    obs = observations or [
        {"id": "O1", "statement": "Existe um gateway.", "basis": {"kind": "structural", "detail": "tipo gateway"}, "refs": ["API GW"]},
    ]
    infs = inferences or [
        {"id": "I1", "hypothesis": "O gateway pode ser SPOF.", "cites": ["O1"], "confidence": "medium"},
    ]
    return {
        "components": components or [{"name": "API GW", "type": "gateway"}],
        "relationships": [],
        "uncertainties": [],
        "observations": obs,
        "intent": {"kind": intent_kind, "summary": "Fluxo.", "compared_items": compared_items},
        "inferences": infs,
        "concerns": concerns or [],
        "limitations": limitations or [],
    }


# --- estrutura ---

def test_valid_report_approved():
    result = validate(_make_report(), _make_enriched())
    assert result.approved


def test_missing_section_rejected():
    report = _make_report(missing_section="## 5. Recomendações")
    result = validate(report, _make_enriched())
    assert not result.approved
    assert any("Recomendações" in e for e in result.errors)


# --- integridade de IDs ---

def test_inference_cites_nonexistent_observation_rejected():
    enriched = _make_enriched(
        inferences=[{"id": "I1", "hypothesis": "H", "cites": ["O99"], "confidence": "high"}]
    )
    result = validate(_make_report(), enriched)
    assert not result.approved
    assert any("O99" in e for e in result.errors)


def test_concern_references_nonexistent_inference_rejected():
    enriched = _make_enriched(
        concerns=[{
            "id": "C1",
            "title": "Ponto único de falha no gateway",
            "description": "Desc.",
            "derived_from": ["I99"],
            "affected_components": ["API GW"],
            "severity": "high",
            "category": "availability",
        }]
    )
    result = validate(_make_report(), enriched)
    assert not result.approved
    assert any("I99" in e for e in result.errors)


# --- cobertura de concerns ---

def test_high_concern_missing_from_report_rejected():
    enriched = _make_enriched(
        concerns=[{
            "id": "C1",
            "title": "Ponto único de falha no gateway",
            "description": "Desc.",
            "derived_from": ["I1"],
            "affected_components": ["API GW"],
            "severity": "high",
            "category": "availability",
        }]
    )
    report = _make_report()  # não menciona o título
    result = validate(report, enriched)
    assert not result.approved
    assert any("Ponto único de falha no gateway" in e for e in result.errors)


def test_high_concern_present_in_report_approved():
    enriched = _make_enriched(
        concerns=[{
            "id": "C1",
            "title": "Ponto único de falha no gateway",
            "description": "Desc.",
            "derived_from": ["I1"],
            "affected_components": ["API GW"],
            "severity": "high",
            "category": "availability",
        }]
    )
    report = _make_report(extra_content="\n## 4. Riscos arquiteturais\nPonto único de falha no gateway: se cair, tudo cai.")
    result = validate(report, enriched)
    assert result.approved


# --- diagrama comparativo ---

def test_comparative_diagram_missing_item_in_summary_rejected():
    enriched = _make_enriched(
        intent_kind="comparison",
        compared_items=["Cenário A", "Cenário B"],
    )
    report = _make_report()  # seção 1 não menciona os itens comparados
    result = validate(report, enriched)
    assert not result.approved
    assert any("comparativ" in e.lower() for e in result.errors)


def test_comparative_diagram_item_in_summary_approved():
    enriched = _make_enriched(
        intent_kind="comparison",
        compared_items=["Cenário A", "Cenário B"],
    )
    report = _make_report(extra_content="\n## 1. Resumo executivo\nEste diagrama compara Cenário A e Cenário B.")
    result = validate(report, enriched)
    assert result.approved
