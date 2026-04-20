from typing import Any, Callable

from config.logging_config import get_logger
from pipelines.p2_risk_analysis.rules import (
    centralized_database,
    excessive_coupling,
    missing_edge_auth,
    single_point_of_failure,
    unmediated_external,
)

logger = get_logger(__name__)

_RULES: list[tuple[str, Callable]] = [
    ("single_point_of_failure", single_point_of_failure.check),
    ("centralized_database", centralized_database.check),
    ("missing_edge_auth", missing_edge_auth.check),
    ("unmediated_external", unmediated_external.check),
    ("excessive_coupling", excessive_coupling.check),
]


def run_all(components: list[dict], relationships: list[dict]) -> list[dict[str, Any]]:
    risks = []
    for name, rule_fn in _RULES:
        try:
            result = rule_fn(components, relationships)
            if result:
                risks.append(result)
                logger.info("rule_matched", extra={"extra": {"rule": name, "severity": result["severity"]}})
            else:
                logger.info("rule_no_match", extra={"extra": {"rule": name}})
        except Exception as exc:
            logger.warning("rule_skipped", extra={"extra": {"rule": name, "error": str(exc)}})
    return risks
