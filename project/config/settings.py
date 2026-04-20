import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY: str = os.environ["ANTHROPIC_API_KEY"]
CLAUDE_MODEL_VISION: str = os.getenv("CLAUDE_MODEL_VISION", "claude-opus-4-5-20251101")
CLAUDE_MODEL_TEXT: str = os.getenv("CLAUDE_MODEL_TEXT", "claude-haiku-4-5-20251001")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf"}
PDF_TEXT_THRESHOLD = 50  # chars mínimos para classificar como pdf_exportado
LLM_MAX_RETRIES = 1
