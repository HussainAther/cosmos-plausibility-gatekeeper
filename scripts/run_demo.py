from __future__ import annotations
import argparse
from gatekeeper.pipeline import run_gatekeeper

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clip", required=True, help="Path to video clip (.mp4)")
    ap.add_argument("--detections", required=True, help="Path to detections JSON")
    ap.add_argument("--outputs", default="outputs", help="Outputs directory")
    ap.add_argument("--no-overlay", action="store_true", help="Disable overlay rendering")
    args = ap.parse_args()

    out = run_gatekeeper(
        clip_path=args.clip,
        detections_path=args.detections,
        outputs_dir=args.outputs,
        try_overlay=(not args.no_overlay),
    )
    print(out.model_dump_json(indent=2))

if __name__ == "__main__":
    main()

