from gatekeeper.reasoning.postprocess import parse_model_output

def test_parse_json():
    raw = '{"plausibility_score": 0.8, "verdict":"OK", "explanation":"fine", "flagged_objects":[]}'
    score, verdict, expl, flagged = parse_model_output(raw)
    assert score == 0.8
    assert verdict == "OK"
    assert "fine" in expl
    assert flagged == []

