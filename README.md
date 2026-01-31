# Physical Plausibility Gatekeeper for Autonomous Vision Systems

A lightweight reasoning module that flags **physically implausible interpretations** in autonomous-vision pipelines using a combination of simple physics checks and Cosmos Reason–style commonsense reasoning.

> **TL;DR**
> This project adds a *post-hoc sanity filter* to perception outputs (bounding boxes, tracks, trajectories), helping catch silent failure modes like impossible motion, discontinuities, or nonsensical interactions.

---

## What this does

Given:

* a short video clip, and
* precomputed perception outputs (bounding boxes, tracks, velocities),

the **Plausibility Gatekeeper** evaluates whether the inferred scene dynamics are physically reasonable.

It outputs:

* a **plausibility score** (0–1),
* a categorical **verdict** (`OK / QUESTIONABLE / IMPLAUSIBLE`),
* a short **natural-language explanation**, and
* a list of **flagged objects** with reasons.

This module does **not** replace perception or control systems — it audits them.

---

## Why this matters

Modern autonomous systems often fail *quietly*:

* objects teleport due to tracking errors,
* vehicles violate basic kinematics,
* pedestrians follow discontinuous or unsafe paths.

These failures may not trigger traditional confidence checks.

This project demonstrates how **reasoning models + simple physical constraints** can act as a safety backstop between perception and downstream decision-making.

---

## Example output

```
Verdict: IMPLAUSIBLE (score = 0.27)

Reason:
Vehicle motion implies a lateral displacement inconsistent with prior velocity.
A pedestrian track shows a discontinuous jump between frames.

Flagged objects:
- trk_3 (car): acceleration spike exceeds max_accel constraint
```

An optional visualization overlays these flags directly on the video.

---

## Repo structure (at a glance)

```
cosmos-plausibility-gatekeeper/
├─ src/gatekeeper/        # core logic
│  ├─ reasoning/          # Cosmos prompt + parsing
│  ├─ plausibility/       # physics heuristics + scoring
│  ├─ io/                 # schemas + loaders
│  └─ viz/                # overlays + reports
├─ data/samples/          # tiny demo clips + detection JSONs
├─ scripts/               # one-command demos
├─ docs/                  # prompts, evaluation, design notes
└─ outputs/               # generated reports/videos (gitignored)
```

Everything is intentionally small and reproducible.

---

## Quickstart

### 1. Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

(Or use `requirements.txt` if preferred.)

---

### 2. Run the demo

```bash
python scripts/run_demo.py \
  --clip data/samples/clip_01.mp4 \
  --detections data/samples/clip_01_detections.json
```

Outputs are written to:

```
outputs/
├─ reports/
│  └─ clip_01_verdict.json
└─ videos/
   └─ clip_01_overlay.mp4
```

---

## How it works (high level)

1. **Input parsing**
   Loads frame timestamps, bounding boxes, tracks, and optional velocities.

2. **Baseline physics checks**
   Simple constraints:

   * max speed
   * max acceleration
   * trajectory continuity
   * basic collision sanity

3. **Reasoning step**
   A Cosmos-style reasoning prompt evaluates scene plausibility using:

   * object classes,
   * motion summaries,
   * stated constraints.

4. **Scoring + verdict**
   Heuristic and reasoning scores are combined into a single plausibility score with a categorical verdict.

---

## Design principles

* **Post-hoc only** — evaluates outputs, does not generate actions
* **Bounded** — single module, no end-to-end autonomy claims
* **Interpretable** — every verdict comes with an explanation
* **Demo-friendly** — runs on small clips with precomputed detections

This is a *reasoning gate*, not a full system.

---

## Limitations (explicit by design)

* Pixel-space velocities (no real-world calibration)
* Short temporal windows only
* Relies on upstream detection/tracking quality
* Not trained or validated for deployment

These are intentional scope constraints for clarity and reproducibility.

---

## Data

Sample clips and detection JSONs in `data/samples/` are:

* short (5–15 seconds),
* low resolution,
* included solely for demonstration.

See `data/README.md` for sources and licensing notes.

---

## Demo video

A <3-minute demo video showing:

1. raw perception output
2. plausibility reasoning
3. flagged failure cases

can be generated with:

```bash
python scripts/export_submission_video.py
```

---

## One-sentence framing (for judges)

> A lightweight reasoning gate that audits autonomous-vision outputs for physical plausibility, helping catch silent failure modes before they propagate downstream.

