from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
from ..io.schema import ClipDetections

@dataclass(frozen=True)
class TrackStats:
    track_id: str
    max_speed: float
    max_accel: float
    max_jump: float
    num_points: int

def _center_xy(bbox_xyxy: List[float]) -> Tuple[float, float]:
    x1, y1, x2, y2 = bbox_xyxy
    return (0.5 * (x1 + x2), 0.5 * (y1 + y2))

def compute_track_stats(det: ClipDetections) -> Dict[str, TrackStats]:
    """
    Computes speed/accel in pixel-space using bbox center differences.
    """
    # Gather per-track time series
    series: Dict[str, List[Tuple[float, float, float]]] = {}
    for fr in det.frames:
        t = float(fr.t)
        for obj in fr.objects:
            tid = obj.id
            cx, cy = _center_xy(list(obj.bbox_xyxy))
            series.setdefault(tid, []).append((t, cx, cy))

    stats: Dict[str, TrackStats] = {}
    for tid, pts in series.items():
        pts_sorted = sorted(pts, key=lambda x: x[0])
        if len(pts_sorted) < 2:
            stats[tid] = TrackStats(tid, 0.0, 0.0, 0.0, len(pts_sorted))
            continue

        t = np.array([p[0] for p in pts_sorted], dtype=float)
        x = np.array([p[1] for p in pts_sorted], dtype=float)
        y = np.array([p[2] for p in pts_sorted], dtype=float)

        dt = np.diff(t)
        dx = np.diff(x)
        dy = np.diff(y)

        # Avoid divide-by-zero
        dt_safe = np.where(dt <= 1e-9, 1e-9, dt)
        speed = np.sqrt(dx * dx + dy * dy) / dt_safe
        jump = np.sqrt(dx * dx + dy * dy)

        if len(speed) >= 2:
            ds = np.diff(speed)
            dt2 = dt_safe[1:]
            accel = ds / np.where(dt2 <= 1e-9, 1e-9, dt2)
        else:
            accel = np.array([0.0], dtype=float)

        stats[tid] = TrackStats(
            track_id=tid,
            max_speed=float(np.max(speed)) if speed.size else 0.0,
            max_accel=float(np.max(np.abs(accel))) if accel.size else 0.0,
            max_jump=float(np.max(jump)) if jump.size else 0.0,
            num_points=len(pts_sorted),
        )
    return stats

def heuristic_score(
    track_stats: Dict[str, TrackStats],
    max_speed_px_s: float,
    max_accel_px_s2: float,
    max_jump_px: float,
) -> Tuple[float, List[Tuple[str, str]]]:
    """
    Returns (score 0..1, flagged [(track_id, reason), ...])
    """
    penalties = 0.0
    flagged: List[Tuple[str, str]] = []

    for tid, st in track_stats.items():
        if st.num_points < 2:
            continue

        # Soft penalties so score degrades gracefully.
        if st.max_speed > max_speed_px_s:
            over = (st.max_speed - max_speed_px_s) / max_speed_px_s
            penalties += min(0.35, 0.10 + 0.25 * over)
            flagged.append((tid, f"speed {st.max_speed:.1f} px/s > {max_speed_px_s:.1f}"))

        if st.max_accel > max_accel_px_s2:
            over = (st.max_accel - max_accel_px_s2) / max_accel_px_s2
            penalties += min(0.45, 0.15 + 0.30 * over)
            flagged.append((tid, f"accel {st.max_accel:.1f} px/s^2 > {max_accel_px_s2:.1f}"))

        if st.max_jump > max_jump_px:
            over = (st.max_jump - max_jump_px) / max_jump_px
            penalties += min(0.45, 0.15 + 0.30 * over)
            flagged.append((tid, f"jump {st.max_jump:.1f}px > {max_jump_px:.1f}px"))

    score = max(0.0, 1.0 - penalties)
    return score, flagged

