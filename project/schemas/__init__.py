import json
from pathlib import Path

_schemas_dir = Path(__file__).parent


def load_schema(name: str) -> dict:
    return json.loads((_schemas_dir / name).read_text(encoding="utf-8"))
