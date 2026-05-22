import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "anthropic")  # "anthropic" | "openai"

# Anthropic
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL_VISION: str = os.getenv("CLAUDE_MODEL_VISION", "claude-opus-4-5-20251101")
CLAUDE_MODEL_TEXT: str = os.getenv("CLAUDE_MODEL_TEXT", "claude-haiku-4-5-20251001")

# OpenAI
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL_TEXT: str = os.getenv("OPENAI_MODEL_TEXT", "gpt-4o-mini")
OPENAI_MODEL_VISION: str = os.getenv("OPENAI_MODEL_VISION", "gpt-4o")

LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf"}
PDF_TEXT_THRESHOLD = 50
LLM_MAX_RETRIES = 1

AWS_REGION: str = os.getenv("AWS_REGION", "us-east-2")
# AWS Credentials (fictícias para LocalStack)
AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
IADT_INPUT_QUEUE_URL: str = os.getenv("IADT_INPUT_QUEUE_URL", "")
IADT_OUTPUT_QUEUE_URL: str = os.getenv("IADT_OUTPUT_QUEUE_URL", "")
IADT_WORKER_VISIBILITY_TIMEOUT: int = int(os.getenv("IADT_WORKER_VISIBILITY_TIMEOUT", "300"))
IADT_WORKER_OUTPUT_MAX_BYTES: int = int(os.getenv("IADT_WORKER_OUTPUT_MAX_BYTES", "262144"))
