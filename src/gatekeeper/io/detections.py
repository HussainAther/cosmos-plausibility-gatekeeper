from __future__ import annotations
import json
from pathlib import Path
from .schema import ClipDetections

def load_detections(path: str | Path) -> ClipDetections:
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return ClipDetections.model_validate(data)

