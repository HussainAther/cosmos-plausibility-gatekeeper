from __future__ import annotations
import json
import re
from typing import Any, Dict, Optional, Tuple

def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Extracts the first JSON object found in a response.
    Handles extra text by grabbing the first {...} block.
    """
    if not text:
        return None

    # If it's pure JSON already:
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    # Try to find a JSON object substring
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        return None
    candidate = m.group(0)

    try:
        obj = json.loads(candidate)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None

def parse_model_output(raw_text: str) -> Tuple[Optional[float], Optional[str], str, list]:
    """
    Returns: (score, verdict, explanation, flagged_objects_list)
    If parsing fails, returns (None, None, fallback_explanation, []).
    """
    obj = _extract_json(raw_text)
    if not obj:
        return None, None, "Model response not parseable as JSON; falling back to heuristics.", []

    score = obj.get("plausibility_score", None)
    verdict = obj.get("verdict", None)
    explanation = obj.get("explanation", "") or ""
    flagged = obj.get("flagged_objects", []) or []

    # Light validation
    try:
        score_f = float(score) if score is not None else None
    except Exception:
        score_f = None

    verdict_s = str(verdict) if verdict is not None else None
    return score_f, verdict_s, str(explanation), flagged if isinstance(flagged, list) else []

