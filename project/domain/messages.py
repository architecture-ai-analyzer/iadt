"""Contratos de mensagem SQS v1 e serialização de saída (sem boto3)."""

from __future__ import annotations

import json
import urllib.parse
from dataclasses import dataclass
from typing import Any

from domain.report_sections import markdown_to_structured_sections


@dataclass(frozen=True)
class InputJob:
    """Trabalho normalizado após parse do corpo SQS."""

    job_id: str
    correlation_id: str | None
    source_bucket: str
    source_key: str


def parse_input_message(body: str, *, fallback_job_id: str) -> InputJob:
    """
    Aceita:
    - JSON v1 com `schema_version`, `source`: {type, bucket, key}, `job_id` opcional.
    - Corpo de notificação S3→SQS (`Records[0].s3...`).
    """
    data = json.loads(body)
    if isinstance(data, dict) and data.get("Message") and isinstance(data["Message"], str):
        # envelope SNS
        data = json.loads(data["Message"])

    if not isinstance(data, dict):
        raise ValueError("corpo da mensagem deve ser um objeto JSON")

    if data.get("Records") and isinstance(data["Records"], list) and len(data["Records"]) > 0:
        return _parse_s3_event_record(data["Records"][0], fallback_job_id=fallback_job_id)

    return _parse_custom_v1(data, fallback_job_id=fallback_job_id)


def _parse_s3_event_record(record: dict[str, Any], *, fallback_job_id: str) -> InputJob:
    s3 = record.get("s3") or {}
    bucket = ((s3.get("bucket") or {}) or {}).get("name") or ""
    key_raw = ((s3.get("object") or {}) or {}).get("key") or ""
    key = urllib.parse.unquote_plus(str(key_raw))
    if not bucket or not key:
        raise ValueError("evento S3: bucket ou key ausente")
    return InputJob(
        job_id=fallback_job_id,
        correlation_id=None,
        source_bucket=str(bucket),
        source_key=key,
    )


def _parse_custom_v1(data: dict[str, Any], *, fallback_job_id: str) -> InputJob:
    ver = data.get("schema_version")
    if ver not in (1, "1"):
        raise ValueError(f"schema_version não suportado (esperado 1): {ver!r}")

    src = data.get("source") or {}
    if src.get("type") != "s3":
        raise ValueError("source.type deve ser 's3'")

    bucket = src.get("bucket")
    key = src.get("key")
    if not bucket or not key:
        raise ValueError("source.bucket e source.key são obrigatórios")

    job_id = data.get("job_id")
    cid = data.get("correlation_id")
    return InputJob(
        job_id=str(job_id) if job_id is not None else fallback_job_id,
        correlation_id=str(cid) if cid is not None else None,
        source_bucket=str(bucket),
        source_key=str(key),
    )


def build_output_message_v1(
    job: InputJob,
    *,
    report: str | None,
    validation_approved: bool,
    validation_errors: list[str],
    elapsed_s: float,
    pipeline_error: str | None = None,
    report_raw_max_chars: int = 12_000,
) -> dict[str, Any]:
    """
    Monta o dicionário serializável para JSON de saída (v1).
    `pipeline_error`: exceção durante o pipeline (download/extract/etc.).
    """
    base: dict[str, Any] = {
        "schema_version": 1,
        "job_id": job.job_id,
        "correlation_id": job.correlation_id,
        "source": {"bucket": job.source_bucket, "key": job.source_key},
        "elapsed_s": elapsed_s,
        "validation": {
            "approved": validation_approved,
            "errors": list(validation_errors),
        },
    }

    if pipeline_error is not None:
        base["status"] = "failed"
        base["failure_stage"] = "pipeline"
        base["error"] = pipeline_error
        base["report"] = {}
        return base

    parse = markdown_to_structured_sections(report or "")
    if not parse.ok:
        base["status"] = "failed"
        base["failure_stage"] = "report_parse"
        base["error"] = "seções obrigatórias ausentes no relatório"
        base["report"] = {}
        base["report_parse_missing_headers"] = parse.missing_headers
        if report:
            raw = report if len(report) <= report_raw_max_chars else report[:report_raw_max_chars] + "…"
            base["report_raw"] = raw
        return base

    base["report"] = parse.sections
    base["status"] = "success" if validation_approved else "failed"
    if not validation_approved:
        base["failure_stage"] = "validation"
        base["error"] = "validação do relatório reprovada"
    return base


def _payload_utf8_size(payload: dict[str, Any]) -> int:
    return len(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def _truncate_utf8(s: str, max_bytes: int) -> str:
    raw = s.encode("utf-8")
    if len(raw) <= max_bytes:
        return s
    cut = raw[:max_bytes]
    return cut.decode("utf-8", errors="ignore")


def fit_message_payload(payload: dict[str, Any], max_bytes: int) -> dict[str, Any]:
    """Garante que o JSON serializado não ultrapassa `max_bytes` (UTF-8)."""
    import copy

    out = copy.deepcopy(payload)
    if _payload_utf8_size(out) <= max_bytes:
        return out

    report = out.get("report")
    if isinstance(report, dict):
        for _ in range(24):
            if _payload_utf8_size(out) <= max_bytes:
                break
            for k in list(report.keys()):
                if isinstance(report[k], str) and report[k]:
                    new_len = max(len(report[k]) // 2, 0)
                    report[k] = report[k][:new_len]
                    if new_len > 0:
                        report[k] += "…"

    if _payload_utf8_size(out) > max_bytes:
        err = out.get("validation", {})
        errs = err.get("errors") if isinstance(err, dict) else None
        if isinstance(errs, list):
            err["errors"] = [_truncate_utf8(str(e), 512) for e in errs[:30]]

    if _payload_utf8_size(out) > max_bytes and isinstance(report, dict):
        out["report"] = {"_truncated": True}
        out["truncation_note"] = "corpo do relatório omitido após truncamento — ver logs"

    return out


def build_system_failure_output_v1(
    *,
    job_id: str,
    correlation_id: str | None,
    error: str,
    stage: str,
    source_bucket: str | None = None,
    source_key: str | None = None,
) -> dict[str, Any]:
    """Falha antes do pipeline completo (parse, S3, etc.)."""
    src: dict[str, str] = {}
    if source_bucket and source_key:
        src = {"bucket": source_bucket, "key": source_key}
    return {
        "schema_version": 1,
        "job_id": job_id,
        "correlation_id": correlation_id,
        "source": src,
        "status": "failed",
        "failure_stage": stage,
        "error": error,
        "elapsed_s": 0.0,
        "validation": {"approved": False, "errors": []},
        "report": {},
    }
