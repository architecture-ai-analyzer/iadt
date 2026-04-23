from pathlib import Path

_base = Path(__file__).parent.parent.parent / "prompts"

PROMPT: str = (_base / "semantic.md").read_text(encoding="utf-8")
