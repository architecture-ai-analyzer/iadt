"""Loop de consumo SQS + publicação na fila de saída."""

from __future__ import annotations

import json
import tempfile
import time
from typing import Any

import boto3

from adapters.aws.s3_source import download_object_to_tempfile
from config.logging_config import get_logger
from config.settings import (
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    AWS_ACCESS_KEY_ID,
    IADT_INPUT_QUEUE_URL,
    IADT_OUTPUT_QUEUE_URL,
    IADT_WORKER_OUTPUT_MAX_BYTES,
    IADT_WORKER_VISIBILITY_TIMEOUT,
)
from domain.messages import (
    build_output_message_v1,
    build_system_failure_output_v1,
    fit_message_payload,
    parse_input_message,
    peek_job_id_from_message_body,
)
from orchestrator.pipeline import run

logger = get_logger(__name__)


def _send_output(sqs_client, queue_url: str, payload: dict[str, Any], max_bytes: int) -> None:
    body = json.dumps(fit_message_payload(payload, max_bytes), ensure_ascii=False)
    sqs_client.send_message(QueueUrl=queue_url, MessageBody=body)


def _delete_message(sqs_client, queue_url: str, receipt_handle: str) -> None:
    sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)


def process_one_message(
    *,
    sqs_client: Any,
    s3_client: Any,
    body: str,
    message_id: str,
    receipt_handle: str,
    input_queue_url: str,
    output_queue_url: str,
    max_output_bytes: int,
) -> None:
    """Processa uma mensagem: publica sempre na fila de saída e remove da entrada em caso de sucesso."""
    try:
        job = parse_input_message(body, fallback_job_id=message_id)
    except Exception as exc:
        logger.exception("input_parse_failed", extra={"extra": {"message_id": message_id}})
        out = build_system_failure_output_v1(
            job_id=message_id,
            correlation_id=None,
            error=str(exc),
            stage="parse_input",
        )
        try:
            _send_output(sqs_client, output_queue_url, out, max_output_bytes)
            _delete_message(sqs_client, input_queue_url, receipt_handle)
        except Exception:
            logger.exception("sqs_output_or_delete_failed", extra={"extra": {"stage": "parse_input"}})
            raise
        return

    local_path = None
    try:
        local_path = download_object_to_tempfile(s3_client, job.source_bucket, job.source_key)
    except Exception as exc:
        logger.exception("s3_download_failed", extra={"extra": {"job_id": job.job_id}})
        out = build_system_failure_output_v1(
            job_id=job.job_id,
            correlation_id=job.correlation_id,
            error=str(exc),
            stage="s3_download",
            source_bucket=job.source_bucket,
            source_key=job.source_key,
        )
        try:
            _send_output(sqs_client, output_queue_url, out, max_output_bytes)
            _delete_message(sqs_client, input_queue_url, receipt_handle)
        except Exception:
            logger.exception("sqs_output_or_delete_failed", extra={"extra": {"stage": "s3_download"}})
            raise
        return

    t0 = time.perf_counter()
    try:
        with tempfile.TemporaryDirectory(prefix="iadt-run-") as tmp:
            result = run(local_path, output_dir=tmp)
        out = build_output_message_v1(
            job,
            report=result.report,
            enriched=result.enriched,
            validation_approved=result.validation.approved,
            validation_errors=list(result.validation.errors),
            elapsed_s=result.elapsed_s,
        )
    except Exception as exc:
        logger.exception("pipeline_failed", extra={"extra": {"job_id": job.job_id}})
        elapsed = round(time.perf_counter() - t0, 2)
        out = build_output_message_v1(
            job,
            report=None,
            enriched=None,
            validation_approved=False,
            validation_errors=[],
            elapsed_s=elapsed,
            pipeline_error=str(exc),
        )
    finally:
        if local_path is not None:
            local_path.unlink(missing_ok=True)

    try:
        _send_output(sqs_client, output_queue_url, out, max_output_bytes)
        _delete_message(sqs_client, input_queue_url, receipt_handle)
        logger.info("message_processed", extra={"extra": {"job_id": job.job_id, "status": out.get("status")}})
    except Exception:
        logger.exception("sqs_output_or_delete_failed", extra={"extra": {"job_id": job.job_id}})
        raise


def run_forever(
    *,
    input_queue_url: str | None = None,
    output_queue_url: str | None = None,
    region: str | None = None,
    max_output_bytes: int | None = None,
    visibility_timeout: int | None = None,
) -> None:
    """Long polling até interrupção do processo."""
    in_url = input_queue_url or IADT_INPUT_QUEUE_URL
    out_url = output_queue_url or IADT_OUTPUT_QUEUE_URL
    reg = region or AWS_REGION
    max_b = max_output_bytes if max_output_bytes is not None else IADT_WORKER_OUTPUT_MAX_BYTES
    vis = visibility_timeout if visibility_timeout is not None else IADT_WORKER_VISIBILITY_TIMEOUT

    if not in_url or not out_url:
        raise RuntimeError("IADT_INPUT_QUEUE_URL e IADT_OUTPUT_QUEUE_URL devem estar definidos")

    # Configure boto3 clients
    # Use credentials from environment or instance role if available
    client_kwargs = {
        "region_name": reg,
    }
    
    # Only use explicit credentials if they're not the default "test" values
    # In production EKS, the node IAM role will be used automatically
    if AWS_ACCESS_KEY_ID and AWS_ACCESS_KEY_ID != "test":
        client_kwargs["aws_access_key_id"] = AWS_ACCESS_KEY_ID
    if AWS_SECRET_ACCESS_KEY and AWS_SECRET_ACCESS_KEY != "test":
        client_kwargs["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY

    sqs = boto3.client("sqs", **client_kwargs)
    s3 = boto3.client("s3", **client_kwargs)
    logger.info("worker_start", extra={"extra": {"region": reg}})

    while True:
        resp = sqs.receive_message(
            QueueUrl=in_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20,
            VisibilityTimeout=vis,
            AttributeNames=["All"],
        )
        messages = resp.get("Messages") or []
        if not messages:
            continue
        msg = messages[0]
        body = msg.get("Body") or ""
        sqs_message_id = msg.get("MessageId") or ""
        mid = peek_job_id_from_message_body(
            body, fallback=sqs_message_id or "unknown"
        )
        rh = msg.get("ReceiptHandle") or ""
        if not rh:
            logger.error("missing_receipt_handle", extra={"extra": {"message_id": mid}})
            continue
        process_one_message(
            sqs_client=sqs,
            s3_client=s3,
            body=body,
            message_id=mid,
            receipt_handle=rh,
            input_queue_url=in_url,
            output_queue_url=out_url,
            max_output_bytes=max_b,
        )
