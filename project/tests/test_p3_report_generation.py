from unittest.mock import patch

from pipelines.p3_report_generation import generate, REQUIRED_SECTIONS


def _make_enriched():
    return {
        "components": [{"name": "API GW", "type": "gateway"}],
        "relationships": [],
        "uncertainties": [],
        "observations": [
            {"id": "O1", "statement": "Existe um gateway.", "basis": {"kind": "structural", "detail": "tipo gateway"}, "refs": ["API GW"]},
        ],
        "intent": {"kind": "flow", "summary": "Fluxo de requisições.", "compared_items": None},
        "inferences": [
            {"id": "I1", "hypothesis": "O gateway pode ser SPOF.", "cites": ["O1"], "confidence": "medium"},
        ],
        "concerns": [
            {
                "id": "C1",
                "title": "Ponto único de falha",
                "description": "Gateway sem redundância.",
                "derived_from": ["I1"],
                "affected_components": ["API GW"],
                "severity": "high",
                "category": "availability",
            },
        ],
        "limitations": [],
    }


def _full_report():
    return "\n\n".join(f"{s}\nConteúdo." for s in REQUIRED_SECTIONS)


def test_generate_returns_report_with_all_sections():
    with patch("pipelines.p3_report_generation.call_text", return_value=_full_report()):
        report = generate(_make_enriched())
    for section in REQUIRED_SECTIONS:
        assert section in report


def test_generate_retries_on_missing_sections():
    calls = [0]

    def fake_call(prompt: str) -> str:
        calls[0] += 1
        if calls[0] == 1:
            return "# Relatório parcial\n\n## 1. Resumo executivo\nOk."
        return _full_report()

    with patch("pipelines.p3_report_generation.call_text", side_effect=fake_call):
        report = generate(_make_enriched())

    assert calls[0] == 2
    for section in REQUIRED_SECTIONS:
        assert section in report
