from domain.queue_analysis import build_analysis_from_enriched


def _sample_enriched():
    return {
        "components": [
            {"name": "API GW", "type": "gateway", "subtype": "aws_api_gateway", "role": "router"},
            {"name": "User DB", "type": "database", "subtype": "postgresql"},
        ],
        "relationships": [{"from": "API GW", "to": "User DB", "relation_type": "query"}],
        "concerns": [
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
    }


def test_build_analysis_components_and_connections():
    analysis = build_analysis_from_enriched(_sample_enriched())
    assert len(analysis["components"]) == 2
    gw = next(c for c in analysis["components"] if c["name"] == "API GW")
    assert gw["id"] == "comp-api-gw"
    assert gw["type"] == "API"
    assert "comp-user-db" in gw["connections"]
    assert gw["technology"] == "aws_api_gateway"


def test_build_analysis_risks_and_recommendations():
    analysis = build_analysis_from_enriched(_sample_enriched())
    assert len(analysis["risks"]) == 1
    risk = analysis["risks"][0]
    assert risk["level"] == "HIGH"
    assert risk["affectedComponent"] == "comp-api-gw"
    assert risk["category"] == "RELIABILITY"
    assert len(analysis["recommendations"]) == 1
    rec = analysis["recommendations"][0]
    assert rec["targetComponent"] == "comp-api-gw"
    assert rec["priority"] == "HIGH"
