from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Constraints:
    max_speed_px_s: float
    max_accel_px_s2: float
    max_jump_px: float

