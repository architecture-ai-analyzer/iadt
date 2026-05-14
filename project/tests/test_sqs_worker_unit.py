import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from adapters.aws.sqs_worker import process_one_message
from domain.report_layout import SECTION_DEFINITIONS
from orchestrator.pipeline import PipelineResult
from pipelines.p4_validation import ValidationResult


def _full_report_md() -> str:
    return "\n\n".join(f"{h}\nCorpo." for h, _ in SECTION_DEFINITIONS)


def test_process_one_message_send_delete_and_cleanup(monkeypatch):
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tf.close()
    path = Path(tf.name)

    def fake_download(_s3, _b, _k):
        return path

    monkeypatch.setattr("adapters.aws.sqs_worker.download_object_to_tempfile", fake_download)

    def fake_run(_fp, output_dir=None):
        return PipelineResult(
            canonical={},
            semantic={},
            enriched={},
            report=_full_report_md(),
            validation=ValidationResult(True, []),
            elapsed_s=3.0,
            artifacts={},
        )

    monkeypatch.setattr("adapters.aws.sqs_worker.run", fake_run)

    sqs = MagicMock()
    s3 = MagicMock()
    body = json.dumps(
        {
            "schema_version": 1,
            "job_id": "job-x",
            "source": {"type": "s3", "bucket": "b", "key": "d.pdf"},
        }
    )

    process_one_message(
        sqs_client=sqs,
        s3_client=s3,
        body=body,
        message_id="mid-1",
        receipt_handle="rh-1",
        input_queue_url="https://sqs/in",
        output_queue_url="https://sqs/out",
        max_output_bytes=200_000,
    )

    assert not path.exists()
    sqs.send_message.assert_called_once()
    sqs.delete_message.assert_called_once()
    call_kw = sqs.send_message.call_args.kwargs
    out = json.loads(call_kw["MessageBody"])
    assert out["job_id"] == "job-x"
    assert out["status"] == "success"
    assert "executive_summary" in out["report"]
