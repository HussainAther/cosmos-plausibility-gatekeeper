from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
from typing import Optional, Set

from .config import Settings
from .io.detections import load_detections
from .io.schema import (
    GatekeeperOutput, Evidence, CheckResult, FlaggedObject, ModelEvidence
)
from .plausibility.constraints import Constraints
from .plausibility.heuristics import compute_track_stats, heuristic_score
from .plausibility.scoring import combine_scores
from .reasoning.cosmos_client import CosmosClient
from .reasoning.prompt_templates import build_prompt_payload
from .reasoning.postprocess import parse_model_output
from .viz.report import write_json_report

def verdict_from_score(score: float, ok_th: float, q_th: float) -> str:
    if score >= ok_th:
        return "OK"
    if score >= q_th:
        return "QUESTIONABLE"
    return "IMPLAUSIBLE"

def run_gatekeeper(
    clip_path: str | Path,
    detections_path: str | Path,
    outputs_dir: str | Path = "outputs",
    try_overlay: bool = True,
    settings: Optional[Settings] = None,
) -> GatekeeperOutput:
    settings = settings or Settings()
    det = load_detections(detections_path)

    constraints = Constraints(
        max_speed_px_s=settings.max_speed_px_s,
        max_accel_px_s2=settings.max_accel_px_s2,
        max_jump_px=settings.max_jump_px,
    )

    track_stats = compute_track_stats(det)
    h_score, h_flagged = heuristic_score(
        track_stats,
        max_speed_px_s=constraints.max_speed_px_s,
        max_accel_px_s2=constraints.max_accel_px_s2,
        max_jump_px=constraints.max_jump_px,
    )

    # Prepare reasoning prompt
    prompt = build_prompt_payload(det, track_stats, asdict(constraints))
    cosmos = CosmosClient(settings.cosmos_api_url, settings.cosmos_api_key, model=settings.cosmos_model)
    cosmos_resp = cosmos.infer(prompt["system"], prompt["user"])

    model_score = None
    model_verdict = None
    model_expl = ""
    model_flagged = []
    if cosmos_resp.status == "ok":
        model_score, model_verdict, model_expl, model_flagged = parse_model_output(cosmos_resp.raw_text)

    final_score, method = combine_scores(h_score, model_score)
    final_verdict = verdict_from_score(final_score, settings.ok_threshold, settings.questionable_threshold)

    # Combine flagged objects: union of heuristic + model
    flagged_objects = []
    seen = set()

    for tid, reason in h_flagged:
        if tid not in seen:
            flagged_objects.append(FlaggedObject(object_id=tid, reason=f"[heuristic] {reason}"))
            seen.add(tid)

    if isinstance(model_flagged, list):
        for item in model_flagged:
            if not isinstance(item, dict):
                continue
            oid = str(item.get("object_id", "")).strip()
            rsn = str(item.get("reason", "")).strip()
            if oid and oid not in seen:
                flagged_objects.append(FlaggedObject(object_id=oid, reason=f"[model] {rsn or 'flagged'}"))
                seen.add(oid)

    explanation = model_expl.strip() if model_expl.strip() else (
        "Heuristic checks applied (speed/accel/jump). "
        "Model reasoning unavailable or skipped."
    )

    checks = [
        CheckResult(name="heuristics_score", passed=True, details=f"{h_score:.3f}"),
        CheckResult(name="combine_method", passed=True, details=method),
        CheckResult(name="cosmos_status", passed=(cosmos_resp.status in ("ok", "skipped")), details=cosmos_resp.status,
)
    ]

    evidence = Evidence(
        checks=checks,
        model=ModelEvidence(provider="cosmos", model_name=settings.cosmos_model, raw_response=cosmos_resp.raw_text[:2000] if cosmos_resp.raw_text else None),
    )

    out = GatekeeperOutput(
        clip_id=det.meta.clip_id,
        plausibility_score=float(final_score),
        verdict=final_verdict,  # type: ignore
        explanation=explanation,
        flagged_objects=flagged_objects,
        evidence=evidence,
    )

    outputs_dir = Path(outputs_dir)
    report_path = outputs_dir / "reports" / f"{det.meta.clip_id}_verdict.json"
    write_json_report(out, report_path)

    if try_overlay:
        try:
            from .viz.render_overlay import render_overlay_video
            flagged_ids: Set[str] = {fo.object_id for fo in flagged_objects}
            render_overlay_video(
                clip_path=clip_path,
                detections=det,
                flagged_object_ids=flagged_ids,
                out_path=outputs_dir / "videos" / f"{det.meta.clip_id}_overlay.mp4",
            )
        except Exception:
            # Overlay is optional; do not fail the pipeline if unavailable.
            pass

    return out

