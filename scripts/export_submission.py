from __future__ import annotations
"""
Hackathon-friendly helper.

This does NOT do fancy editing. It just ensures an overlay video exists for each sample.
For a real <3 min submission, you can stitch these in any editor.
"""
from pathlib import Path
from gatekeeper.pipeline import run_gatekeeper

def main() -> None:
    samples = Path("data/samples")
    outputs = Path("outputs")

    for det_path in sorted(samples.glob("*_detections.json")):
        clip_id = det_path.name.replace("_detections.json", "")
        clip_path = samples / f"{clip_id}.mp4"
        if not clip_path.exists():
            continue
        out = run_gatekeeper(clip_path, det_path, outputs_dir=outputs, try_overlay=True)
        print(f"Rendered: {outputs/'videos'/f'{clip_id}_overlay.mp4'} | {out.verdict} ({out.plausibility_score:.2f})")

if __name__ == "__main__":
    main()

