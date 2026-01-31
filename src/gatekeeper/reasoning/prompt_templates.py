from __future__ import annotations
from typing import Dict, Any
from ..io.schema import ClipDetections
from ..plausibility.heuristics import TrackStats

def build_scene_summary(det: ClipDetections, track_stats: Dict[str, TrackStats]) -> str:
    lines = []
    m = det.meta
    lines.append(f"Clip: {m.clip_id}, fps={m.fps}, size={m.frame_width}x{m.frame_height}")
    lines.append(f"Frames: {len(det.frames)}")
    lines.append("Track summaries (pixel-space, bbox-center):")
    for tid, st in sorted(track_stats.items(), key=lambda x: x[0]):
        if st.num_points < 2:
            continue
        lines.append(
            f"- {tid}: points={st.num_points}, max_speed={st.max_speed:.1f}px/s, "
            f"max_accel={st.max_accel:.1f}px/s^2, max_jump={st.max_jump:.1f}px"
        )
    return "\n".join(lines)

def build_prompt_payload(
    det: ClipDetections,
    track_stats: Dict[str, TrackStats],
    constraints: Dict[str, Any],
) -> Dict[str, str]:
    """
    Returns a system + user prompt pair. Keep it short and judge-readable.
    """
    system = (
        "You are a safety auditor for autonomous-vision outputs.\n"
        "Your task: judge physical plausibility and temporal continuity only.\n"
        "Return strict JSON only. No markdown."
    )

    user = (
        "Evaluate whether the inferred object motions and interactions are physically plausible.\n\n"
        f"{build_scene_summary(det, track_stats)}\n\n"
        "Constraints:\n"
        f"- max_speed_px_s: {constraints['max_speed_px_s']}\n"
        f"- max_accel_px_s2: {constraints['max_accel_px_s2']}\n"
        f"- max_jump_px: {constraints['max_jump_px']}\n\n"
        "Return JSON with fields:\n"
        "{\n"
        '  "plausibility_score": number (0..1),\n'
        '  "verdict": "OK"|"QUESTIONABLE"|"IMPLAUSIBLE",\n'
        '  "explanation": string (1-3 sentences),\n'
        '  "flagged_objects": [{"object_id": string, "reason": string}]\n'
        "}\n"
    )
    return {"system": system, "user": user}

