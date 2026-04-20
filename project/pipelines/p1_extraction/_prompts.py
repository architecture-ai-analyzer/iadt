from pathlib import Path

_base = Path(__file__).parent.parent.parent / "prompts"

PROMPT: str = (_base / "extracao.md").read_text(encoding="utf-8")
REINFORCED_PROMPT: str = (_base / "extracao_reforcado.md").read_text(encoding="utf-8")
