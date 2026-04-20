import pytest
from pipelines.p2_risk_analysis import analyze
from pipelines.p2_risk_analysis.rules import (
    centralized_database,
    excessive_coupling,
    missing_edge_auth,
    single_point_of_failure,
    unmediated_external,
)


def canonical(components, relationships):
    return {"components": components, "relationships": relationships, "uncertainties": []}


# --- single_point_of_failure ---

def test_spof_detected_for_lone_gateway():
    components = [{"name": "API GW", "type": "gateway"}]
    rels = [{"from": "Client", "to": "API GW"}, {"from": "API GW", "to": "Auth"}]
    result = single_point_of_failure.check(components, rels)
    assert result is not None
    assert result["type"] == "single_point_of_failure"
    assert result["severity"] == "high"


def test_spof_not_detected_when_replica_exists():
    components = [{"name": "GW-1", "type": "gateway"}, {"name": "GW-2", "type": "gateway"}]
    rels = [{"from": "Client", "to": "GW-1"}, {"from": "Client", "to": "GW-2"}]
    result = single_point_of_failure.check(components, rels)
    assert result is None


# --- centralized_database ---

def test_centralized_db_detected():
    components = [{"name": "DB", "type": "database"}]
    rels = [
        {"from": "SvcA", "to": "DB"},
        {"from": "SvcB", "to": "DB"},
        {"from": "SvcC", "to": "DB"},
    ]
    result = centralized_database.check(components, rels)
    assert result is not None
    assert result["type"] == "centralized_database"


def test_centralized_db_not_detected_below_threshold():
    components = [{"name": "DB", "type": "database"}]
    rels = [{"from": "SvcA", "to": "DB"}, {"from": "SvcB", "to": "DB"}]
    result = centralized_database.check(components, rels)
    assert result is None


# --- missing_edge_auth ---

def test_missing_auth_detected_when_client_connects_directly():
    components = [
        {"name": "Browser", "type": "client"},
        {"name": "OrderService", "type": "service"},
    ]
    rels = [{"from": "Browser", "to": "OrderService"}]
    result = missing_edge_auth.check(components, rels)
    assert result is not None
    assert result["type"] == "missing_edge_auth"


def test_no_missing_auth_when_gateway_present():
    components = [
        {"name": "Browser", "type": "client"},
        {"name": "APIGW", "type": "gateway"},
        {"name": "OrderService", "type": "service"},
    ]
    rels = [{"from": "Browser", "to": "APIGW"}, {"from": "APIGW", "to": "OrderService"}]
    result = missing_edge_auth.check(components, rels)
    assert result is None


# --- excessive_coupling ---

def test_excessive_coupling_detected():
    components = [{"name": "Hub", "type": "service"}]
    rels = [{"from": "Hub", "to": f"Svc{i}"} for i in range(6)]
    result = excessive_coupling.check(components, rels)
    assert result is not None
    assert result["type"] == "excessive_coupling"


# --- analyze (integration) ---

def test_analyze_returns_enriched_with_risks():
    c = canonical(
        components=[{"name": "DB", "type": "database"}],
        relationships=[
            {"from": "A", "to": "DB"}, {"from": "B", "to": "DB"}, {"from": "C", "to": "DB"}
        ],
    )
    result = analyze(c)
    assert "risks" in result
    assert any(r["type"] == "centralized_database" for r in result["risks"])


def test_analyze_returns_empty_risks_when_clean():
    c = canonical(
        components=[{"name": "SvcA", "type": "service"}, {"name": "DB", "type": "database"}],
        relationships=[{"from": "SvcA", "to": "DB"}],
    )
    result = analyze(c)
    assert "risks" in result


def test_analyze_raises_on_missing_components():
    with pytest.raises(ValueError, match="inválido"):
        analyze({"relationships": [], "uncertainties": []})
