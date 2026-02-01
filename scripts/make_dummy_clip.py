from __future__ import annotations
import json
from pathlib import Path

def main():
    det_path = Path("data/samples/clip_01_detections.json")
    out_path = Path("data/samples/clip_01.mp4")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    det = json.loads(det_path.read_text(encoding="utf-8"))
    w = int(det["meta"].get("frame_width", 640))
    h = int(det["meta"].get("frame_height", 360))
    fps = float(det["meta"].get("fps", 30))

    import cv2  # type: ignore
    import numpy as np

    frames = det["frames"]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (w, h))

    for fr in frames:
        img = np.zeros((h, w, 3), dtype=np.uint8)
        for obj in fr.get("objects", []):
            x1, y1, x2, y2 = [int(v) for v in obj["bbox_xyxy"]]
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
            label = f'{obj.get("class","obj")}:{obj.get("id","")}'
            cv2.putText(img, label, (x1, max(12, y1 - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        writer.write(img)

    writer.release()
    print(f"Wrote dummy clip: {out_path}")

if __name__ == "__main__":
    main()

