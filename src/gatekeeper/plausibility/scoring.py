from __future__ import annotations
from typing import Tuple

def combine_scores(heuristic: float, model: float | None) -> Tuple[float, str]:
    """
    Combine baseline + model into final plausibility score.
    If model score is unavailable, use heuristic only.
    """
    if model is None:
        return heuristic, "heuristics_only"

    # Blend favors reasoning slightly, but still anchored by physics checks.
    final = 0.6 * model + 0.4 * heuristic
    final = max(0.0, min(1.0, float(final)))
    return final, "blend_0.6_model_0.4_heuristic"

