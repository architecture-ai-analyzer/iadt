from typing import Any


def check(components: list[dict], relationships: list[dict]) -> dict[str, Any] | None:
    from collections import Counter
    incoming = Counter(r["to"] for r in relationships)
    outgoing = Counter(r["from"] for r in relationships)

    gateways = [c["name"] for c in components if c["type"] in ("gateway", "load_balancer")]
    for name in gateways:
        replicas = [c for c in components if c["name"] != name and c["type"] == components[next(i for i, c in enumerate(components) if c["name"] == name)]["type"]]
        total_connections = incoming[name] + outgoing[name]
        if total_connections >= 2 and not replicas:
            return {
                "type": "single_point_of_failure",
                "description": f"{name} é o único ponto de entrada sem redundância aparente",
                "affected_components": [name],
                "severity": "high",
                "evidence": f"Único componente do tipo {_type(components, name)} com {total_connections} conexões e sem réplica identificada",
            }
    return None


def _type(components: list[dict], name: str) -> str:
    return next((c["type"] for c in components if c["name"] == name), "unknown")
