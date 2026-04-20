from typing import Any


def check(components: list[dict], relationships: list[dict]) -> dict[str, Any] | None:
    externals = {c["name"] for c in components if c["type"] == "external"}
    if not externals:
        return None

    internal_types = {"service", "gateway", "load_balancer", "cache", "queue"}
    internal = {c["name"] for c in components if c["type"] in internal_types}
    mediators = {c["name"] for c in components if c["type"] in ("gateway", "load_balancer", "queue")}

    for rel in relationships:
        src, dst = rel["from"], rel["to"]
        if src in externals and dst in internal:
            intermediaries = {r["to"] for r in relationships if r["from"] in externals and r["to"] in mediators}
            if dst not in mediators and dst not in intermediaries:
                return {
                    "type": "unmediated_external",
                    "description": f"Integração direta entre sistema externo {src} e componente interno {dst} sem mediador",
                    "affected_components": [src, dst],
                    "severity": "medium",
                    "evidence": f"Relacionamento direto {src} → {dst} sem gateway, queue ou proxy intermediário",
                }
    return None
