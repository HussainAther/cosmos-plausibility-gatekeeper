from __future__ import annotations
import os
from dataclasses import dataclass

def _get_float(name: str, default: float) -> float:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    try:
        return float(v)
    except ValueError:
        return default

@dataclass(frozen=True)
class Settings:
    cosmos_api_url: str | None = os.getenv("COSMOS_API_URL")
    cosmos_api_key: str | None = os.getenv("COSMOS_API_KEY")
    cosmos_model: str = os.getenv("COSMOS_MODEL", "reason-2")

    ok_threshold: float = _get_float("GATEKEEPER_OK_THRESHOLD", 0.70)
    questionable_threshold: float = _get_float("GATEKEEPER_QUESTIONABLE_THRESHOLD", 0.45)

    # Default constraints in pixel-space (demo friendly)
    max_speed_px_s: float = _get_float("MAX_SPEED_PX_S", 900.0)
    max_accel_px_s2: float = _get_float("MAX_ACCEL_PX_S2", 6000.0)
    max_jump_px: float = _get_float("MAX_JUMP_PX", 120.0)

