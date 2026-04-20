import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from config.logging_config import get_logger
from pipelines.p1_extraction import extract
from pipelines.p2_risk_analysis import analyze
from pipelines.p3_report_generation import generate
from pipelines.p4_validation import validate, ValidationResult

logger = get_logger(__name__)


@dataclass
class PipelineResult:
    canonical: dict[str, Any]
    enriched: dict[str, Any]
    report: str
    validation: ValidationResult
    elapsed_s: float
    artifacts: dict[str, Path] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.validation.approved


def run(file_path: str | Path, output_dir: str | Path | None = None) -> PipelineResult:
    path = Path(file_path)
    out_dir = Path(output_dir) if output_dir else Path("runs") / path.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    logger.info("pipeline_start", extra={"extra": {"file": str(path)}})

    canonical = extract(path)
    _save(out_dir / "canonical.json", json.dumps(canonical, ensure_ascii=False, indent=2))

    enriched = analyze(canonical)
    _save(out_dir / "enriched.json", json.dumps(enriched, ensure_ascii=False, indent=2))

    report = generate(enriched)
    report_path = out_dir / "report.md"
    _save(report_path, report)

    validation = validate(report, enriched)

    elapsed = round(time.perf_counter() - t0, 2)
    logger.info("pipeline_done", extra={"extra": {
        "success": validation.approved,
        "elapsed_s": elapsed,
        "output_dir": str(out_dir),
    }})

    return PipelineResult(
        canonical=canonical,
        enriched=enriched,
        report=report,
        validation=validation,
        elapsed_s=elapsed,
        artifacts={
            "canonical": out_dir / "canonical.json",
            "enriched": out_dir / "enriched.json",
            "report": report_path,
        },
    )


def _save(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
