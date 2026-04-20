from dataclasses import dataclass, field
from typing import Any

from config.logging_config import get_logger
from pipelines.p4_validation import consistency, structure

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    approved: bool
    errors: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        if self.approved:
            return "APROVADO"
        return "REJEITADO — " + "; ".join(self.errors)


def validate(report: str, enriched: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    errors.extend(structure.validate(report))
    errors.extend(consistency.validate(report, enriched))

    result = ValidationResult(approved=len(errors) == 0, errors=errors)
    logger.info("p4_done", extra={"extra": {
        "approved": result.approved,
        "errors": errors,
    }})
    return result
