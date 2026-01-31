from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class VideoInfo:
    path: Path
    fps: float
    width: int
    height: int
    frame_count: int

def probe_video(path: str | Path) -> VideoInfo:
    """
    Best-effort probe. Requires opencv-python if you want accurate info.
    If OpenCV isn't installed, this returns fallback values.
    """
    p = Path(path)
    try:
        import cv2  # type: ignore
        cap = cv2.VideoCapture(str(p))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        cap.release()
        return VideoInfo(p, float(fps), width, height, frame_count)
    except Exception:
        return VideoInfo(p, 30.0, 0, 0, 0)

