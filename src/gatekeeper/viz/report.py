from __future__ import annotations
import json
from pathlib import Path
from ..io.schema import GatekeeperOutput

def write_json_report(out: GatekeeperOutput, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(out.model_dump_json(indent=2), encoding="utf-8")
    return p

