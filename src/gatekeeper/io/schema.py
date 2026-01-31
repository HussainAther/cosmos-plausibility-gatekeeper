from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, conlist

Verdict = Literal["OK", "QUESTIONABLE", "IMPLAUSIBLE"]

class Meta(BaseModel):
    clip_id: str
    fps: float
    frame_width: int
    frame_height: int
    time_unit: Literal["seconds"] = "seconds"

BBoxXYXY = conlist(float, min_length=4, max_length=4)
Vec2 = conlist(float, min_length=2, max_length=2)

class DetectedObject(BaseModel):
    id: str
    class_name: str = Field(alias="class")
    bbox_xyxy: BBoxXYXY
    confidence: Optional[float] = None
    track_id: Optional[int] = None
    velocity_px_s: Optional[Vec2] = None

class FrameDetections(BaseModel):
    t: float
    objects: List[DetectedObject] = Field(default_factory=list)

class ClipDetections(BaseModel):
    meta: Meta
    frames: List[FrameDetections]

class FlaggedObject(BaseModel):
    object_id: str
    reason: str

class CheckResult(BaseModel):
    name: str
    passed: bool
    details: Optional[str] = None

class ModelEvidence(BaseModel):
    provider: str
    model_name: str
    raw_response: Optional[str] = None

class Evidence(BaseModel):
    checks: List[CheckResult] = Field(default_factory=list)
    model: Optional[ModelEvidence] = None

class GatekeeperOutput(BaseModel):
    clip_id: str
    plausibility_score: float  # 0..1
    verdict: Verdict
    explanation: str
    flagged_objects: List[FlaggedObject] = Field(default_factory=list)
    evidence: Optional[Evidence] = None

