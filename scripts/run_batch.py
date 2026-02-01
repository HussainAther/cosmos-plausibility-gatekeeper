from __future__ import annotations
import argparse
from pathlib import Path
from gatekeeper.pipeline import run_gatekeeper

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples-dir", default="data/samples", help="Folder containing clips + *_detections.json")
    ap.add_argument("--outputs", default="outputs")
    args = ap.parse_args()

    samples = Path(args.samples_dir)
    det_files = sorted(samples.glob("*_detections.json"))
    if not det_files:
        raise SystemExit(f"No detections found in {samples}")

    for det_path in det_files:
        clip_id = det_path.name.replace("_detections.json", "")
        # prefer mp4
        clip = samples / f"{clip_id}.mp4"
        if not clip.exists():
            print(f"Skipping {clip_id}: missing {clip}")
            continue
        out = run_gatekeeper(clip, det_path, outputs_dir=args.outputs, try_overlay=True)
        print(f"{clip_id}: {out.verdict} ({out.plausibility_score:.2f})")

if __name__ == "__main__":
    main()

