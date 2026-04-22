import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "anthropic")  # "anthropic" | "openai" | "ollama"

# Anthropic
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL_VISION: str = os.getenv("CLAUDE_MODEL_VISION", "claude-opus-4-5-20251101")
CLAUDE_MODEL_TEXT: str = os.getenv("CLAUDE_MODEL_TEXT", "claude-haiku-4-5-20251001")

# OpenAI
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL_TEXT: str = os.getenv("OPENAI_MODEL_TEXT", "gpt-4o-mini")
OPENAI_MODEL_VISION: str = os.getenv("OPENAI_MODEL_VISION", "gpt-4o")

# Ollama
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL_VISION: str = os.getenv("OLLAMA_MODEL_VISION", "llama3.2-vision")
OLLAMA_MODEL_TEXT: str = os.getenv("OLLAMA_MODEL_TEXT", "qwen2.5:7b")

LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf"}
PDF_TEXT_THRESHOLD = 50
LLM_MAX_RETRIES = 1
