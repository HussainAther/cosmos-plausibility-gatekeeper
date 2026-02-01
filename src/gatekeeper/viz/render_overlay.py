from __future__ import annotations
from pathlib import Path
from typing import Dict, Set
from ..io.schema import ClipDetections

def render_overlay_video(
    clip_path: str | Path,
    detections: ClipDetections,
    flagged_object_ids: Set[str],
    out_path: str | Path,
) -> Path:
    """
    Optional overlay video. Requires opencv-python.
    If OpenCV isn't installed, raise a helpful error.
    """
    try:
        import cv2  # type: ignore
    except Exception as e:
        raise RuntimeError("OpenCV not installed. Run: pip install -e '.[viz]'") from e

    clip_path = Path(clip_path)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(clip_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or detections.meta.fps or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or detections.meta.frame_width)
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or detections.meta.frame_height)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, float(fps), (w, h))

    # Map frame index -> objects (best-effort alignment by order)
    frames = detections.frames
    frame_idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if frame_idx < len(frames):
            fr = frames[frame_idx]
            for obj in fr.objects:
                x1, y1, x2, y2 = [int(v) for v in obj.bbox_xyxy]
                is_flagged = obj.id in flagged_object_ids
                # Default green, flagged red (BGR)
                color = (0, 255, 0) if not is_flagged else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                label = f"{obj.class_name}:{obj.id}"
                cv2.putText(frame, label, (x1, max(10, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        writer.write(frame)
        frame_idx += 1

    cap.release()
    writer.release()
    return out_path

