from collections import Counter
from typing import Any

THRESHOLD = 2


def check(components: list[dict], relationships: list[dict]) -> dict[str, Any] | None:
    dbs = {c["name"] for c in components if c["type"] == "database"}
    if not dbs:
        return None

    incoming = Counter(r["to"] for r in relationships if r["to"] in dbs)
    for db_name, count in incoming.items():
        if count > THRESHOLD:
            return {
                "type": "centralized_database",
                "description": f"{db_name} é o único banco atendendo múltiplos serviços",
                "affected_components": [db_name],
                "severity": "medium",
                "evidence": f"{db_name} recebe {count} conexões de entrada — banco centralizado sem separação de dados",
            }
    return None
