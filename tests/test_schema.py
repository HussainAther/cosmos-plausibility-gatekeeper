from gatekeeper.io.schema import ClipDetections

def test_schema_load_minimal():
    obj = {
        "meta": {"clip_id":"x", "fps":30, "frame_width":640, "frame_height":480, "time_unit":"seconds"},
        "frames": [{"t":0.0, "objects": []}]
    }
    det = ClipDetections.model_validate(obj)
    assert det.meta.clip_id == "x"

