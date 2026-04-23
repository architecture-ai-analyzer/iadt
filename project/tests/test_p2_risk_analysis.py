import pytest
from unittest.mock import patch

from pipelines.p2_risk_analysis import analyze
from pipelines.p2_risk_analysis.reasoning import _assign_ids, _validate_id_references


def _make_canonical(components=None, relationships=None):
    return {
        "components": components or [{"name": "API GW", "type": "gateway"}],
        "relationships": relationships or [],
        "uncertainties": [],
    }


def _make_semantic(observations=None, intent_kind="flow"):
    obs = observations or [
        {"id": "O1", "statement": "Existe um gateway.", "basis": {"kind": "structural", "detail": "tipo gateway"}, "refs": ["API GW"]},
    ]
    return {
        "observations": obs,
        "intent": {"kind": intent_kind, "summary": "Fluxo de requisições.", "compared_items": None},
    }


def _make_analysis_response(inferences=None, concerns=None, limitations=None):
    return {
        "inferences": inferences or [
            {"id": "I1", "hypothesis": "O gateway pode ser SPOF.", "cites": ["O1"], "confidence": "medium"},
        ],
        "concerns": concerns or [
            {
                "id": "C1",
                "title": "Ponto único de falha no gateway",
                "description": "Se o gateway cair, toda a arquitetura falha.",
                "derived_from": ["I1"],
                "affected_components": ["API GW"],
                "severity": "high",
                "category": "availability",
            },
        ],
        "limitations": limitations or [],
    }


# --- _assign_ids ---

def test_assign_ids_numbering():
    result = _assign_ids({
        "inferences": [{"hypothesis": "H1", "cites": ["O1"], "confidence": "low"}],
        "concerns": [{"title": "C", "description": "D", "derived_from": ["I1"], "affected_components": ["X"], "severity": "low", "category": "other"}],
        "limitations": [{"statement": "S", "reason": "low_confidence"}],
    })
    assert result["inferences"][0]["id"] == "I1"
    assert result["concerns"][0]["id"] == "C1"
    assert result["limitations"][0]["id"] == "L1"


# --- _validate_id_references ---

def test_validate_id_references_ok():
    obs = [{"id": "O1", "statement": "s", "basis": {"kind": "visual", "detail": "d"}, "refs": []}]
    result = _assign_ids({
        "inferences": [{"hypothesis": "H", "cites": ["O1"], "confidence": "high"}],
        "concerns": [{"title": "T", "description": "D", "derived_from": ["I1"], "affected_components": ["X"], "severity": "high", "category": "availability"}],
        "limitations": [],
    })
    _validate_id_references(result, obs)  # não deve lançar


def test_validate_id_references_bad_observation_id():
    obs = [{"id": "O1", "statement": "s", "basis": {"kind": "visual", "detail": "d"}, "refs": []}]
    result = {"inferences": [{"id": "I1", "hypothesis": "H", "cites": ["O99"], "confidence": "low"}], "concerns": [], "limitations": []}
    with pytest.raises(ValueError, match="O99"):
        _validate_id_references(result, obs)


def test_validate_id_references_bad_inference_id():
    obs = [{"id": "O1", "statement": "s", "basis": {"kind": "visual", "detail": "d"}, "refs": []}]
    result = {
        "inferences": [{"id": "I1", "hypothesis": "H", "cites": ["O1"], "confidence": "low"}],
        "concerns": [{"id": "C1", "title": "T", "description": "D", "derived_from": ["I99"], "affected_components": ["X"], "severity": "low", "category": "other"}],
        "limitations": [],
    }
    with pytest.raises(ValueError, match="I99"):
        _validate_id_references(result, obs)


# --- analyze (integration, com mock do LLM) ---

def test_analyze_returns_enriched_structure():
    canonical = _make_canonical()
    semantic = _make_semantic()

    import json
    mock_response = json.dumps(_make_analysis_response())

    with patch("pipelines.p2_risk_analysis.reasoning.call_text", return_value=mock_response):
        result = analyze(canonical, semantic)

    assert "inferences" in result
    assert "concerns" in result
    assert "limitations" in result
    assert "observations" in result
    assert "intent" in result
    assert result["inferences"][0]["id"] == "I1"
    assert result["concerns"][0]["id"] == "C1"


def test_analyze_raises_on_missing_components():
    semantic = _make_semantic()
    with pytest.raises(ValueError, match="components"):
        analyze({"relationships": [], "uncertainties": []}, semantic)


def test_analyze_empty_concerns_valid():
    canonical = _make_canonical()
    semantic = _make_semantic()

    import json
    mock_response = json.dumps(_make_analysis_response(inferences=[], concerns=[], limitations=[]))

    with patch("pipelines.p2_risk_analysis.reasoning.call_text", return_value=mock_response):
        result = analyze(canonical, semantic)

    assert result["concerns"] == []
    assert result["inferences"] == []
