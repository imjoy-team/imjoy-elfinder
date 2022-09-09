"""A fastapi connector for elfinder."""
from pathlib import Path
import json

ROOT_DIR = Path(__file__).parent.resolve()
__version__ = json.loads((ROOT_DIR / "VERSION").read_text(encoding="utf-8"))["version"]
