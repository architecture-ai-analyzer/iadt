from collections import Counter
from typing import Any

COUPLING_THRESHOLD = 5


def check(components: list[dict], relationships: list[dict]) -> dict[str, Any] | None:
    counts = Counter()
    for r in relationships:
        counts[r["from"]] += 1
        counts[r["to"]] += 1

    for component, total in counts.items():
        if total > COUPLING_THRESHOLD:
            return {
                "type": "excessive_coupling",
                "description": f"{component} possui acoplamento excessivo com muitos outros componentes",
                "affected_components": [component],
                "severity": "medium",
                "evidence": f"{component} tem {total} conexões (threshold: {COUPLING_THRESHOLD})",
            }
    return None
