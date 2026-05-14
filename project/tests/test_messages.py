import json

from domain.messages import (
    InputJob,
    build_output_message_v1,
    fit_message_payload,
    parse_input_message,
)


def test_parse_custom_v1():
    body = json.dumps(
        {
            "schema_version": 1,
            "job_id": "job-1",
            "correlation_id": "corr-9",
            "source": {"type": "s3", "bucket": "b", "key": "path/to/x.pdf"},
        }
    )
    job = parse_input_message(body, fallback_job_id="sqs-msg")
    assert job == InputJob(
        job_id="job-1",
        correlation_id="corr-9",
        source_bucket="b",
        source_key="path/to/x.pdf",
    )


def test_parse_custom_v1_uses_fallback_job_id():
    body = json.dumps(
        {
            "schema_version": 1,
            "source": {"type": "s3", "bucket": "b", "key": "k"},
        }
    )
    job = parse_input_message(body, fallback_job_id="mid-42")
    assert job.job_id == "mid-42"


def test_parse_s3_event_record():
    body = json.dumps(
        {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "my-bucket"},
                        "object": {"key": "prefix%2Fhello%20world.pdf"},
                    }
                }
            ]
        }
    )
    job = parse_input_message(body, fallback_job_id="evt-1")
    assert job.source_bucket == "my-bucket"
    assert job.source_key == "prefix/hello world.pdf"
    assert job.job_id == "evt-1"


def test_parse_sns_envelope():
    inner = {
        "schema_version": 1,
        "job_id": "j",
        "source": {"type": "s3", "bucket": "b", "key": "k.pdf"},
    }
    body = json.dumps({"Message": json.dumps(inner)})
    job = parse_input_message(body, fallback_job_id="x")
    assert job.job_id == "j"


def test_build_output_success():
    report = "\n\n".join(
        [
            "## 1. Resumo executivo\nR.",
            "## 2. Componentes identificados\nC.",
            "## 3. Relações observadas\nRel.",
            "## 4. Riscos arquiteturais\nRisk.",
            "## 5. Recomendações\nRec.",
            "## 6. Limitações da análise\nLim.",
            "## 7. Nível de confiança\nAlto.",
        ]
    )
    job = InputJob("j", None, "b", "k.pdf")
    out = build_output_message_v1(
        job,
        report=report,
        validation_approved=True,
        validation_errors=[],
        elapsed_s=1.5,
    )
    assert out["status"] == "success"
    assert out["report"]["executive_summary"] == "R."
    assert out["validation"]["approved"] is True


def test_build_output_validation_failed():
    report = "\n\n".join(
        f"{h}\nX."
        for h in [
            "## 1. Resumo executivo",
            "## 2. Componentes identificados",
            "## 3. Relações observadas",
            "## 4. Riscos arquiteturais",
            "## 5. Recomendações",
            "## 6. Limitações da análise",
            "## 7. Nível de confiança",
        ]
    )
    job = InputJob("j", None, "b", "k.pdf")
    out = build_output_message_v1(
        job,
        report=report,
        validation_approved=False,
        validation_errors=["erro x"],
        elapsed_s=2.0,
    )
    assert out["status"] == "failed"
    assert out["failure_stage"] == "validation"


def test_build_output_pipeline_error():
    job = InputJob("j", None, "b", "k.pdf")
    out = build_output_message_v1(
        job,
        report=None,
        validation_approved=False,
        validation_errors=[],
        elapsed_s=0.0,
        pipeline_error="boom",
    )
    assert out["status"] == "failed"
    assert out["error"] == "boom"


def test_fit_message_payload_truncates():
    huge = "x" * 500_000
    report = "\n\n".join(
        [
            "## 1. Resumo executivo\n" + huge,
            "## 2. Componentes identificados\nC.",
            "## 3. Relações observadas\nRel.",
            "## 4. Riscos arquiteturais\nRisk.",
            "## 5. Recomendações\nRec.",
            "## 6. Limitações da análise\nLim.",
            "## 7. Nível de confiança\nAlto.",
        ]
    )
    job = InputJob("j", None, "b", "k.pdf")
    out = build_output_message_v1(
        job,
        report=report,
        validation_approved=True,
        validation_errors=[],
        elapsed_s=1.0,
    )
    fitted = fit_message_payload(out, max_bytes=4096)
    assert len(json.dumps(fitted, ensure_ascii=False).encode("utf-8")) <= 5000
