from typing import Any


def check(components: list[dict], relationships: list[dict]) -> dict[str, Any] | None:
    clients = {c["name"] for c in components if c["type"] == "client"}
    gateways = {c["name"] for c in components if c["type"] in ("gateway", "load_balancer")}
    auth_components = {
        c["name"] for c in components
        if any(kw in c["name"].lower() for kw in ("auth", "jwt", "oauth", "identity", "sso", "iam"))
    }

    if not clients or gateways or auth_components:
        return None

    direct_targets = {r["to"] for r in relationships if r["from"] in clients}
    services = {c["name"] for c in components if c["type"] == "service"}
    exposed = direct_targets & services

    if exposed:
        return {
            "type": "missing_edge_auth",
            "description": "Componente(s) exposto(s) externamente sem gateway ou autenticação aparente",
            "affected_components": list(exposed),
            "severity": "high",
            "evidence": f"Client conecta diretamente a serviços {list(exposed)} sem gateway ou componente de auth identificado",
        }
    return None
