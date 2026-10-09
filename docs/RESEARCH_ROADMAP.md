# Research extension roadmap

1. Collect consented, diverse, camera-view-labelled movement sequences and annotate exercise identity, phases, rep boundaries and coaching observations. Split by person and recording session; adjacent frames must not leak between train/test.
2. Validate the rule-based baseline before adding complexity: per-exercise count MAE, rep event precision/recall within temporal tolerance, low-visibility false counts, phase timing errors, and performance distributions. Publish failure cases, not only successful demos.
3. Add viewpoint/occlusion estimation and per-person neutral/range calibration. Evaluate MediaPipe world-landmark angles against calibrated reference motion capture where possible. Keep confidence and visibility separate.
4. Implement a learned sequence predictor behind `MovementPredictor`: normalize by hip center and body scale, train a small GRU/TCN on observed history, predict multiple future horizons, and compare against zero-velocity and constant-velocity baselines. Report MPJPE and velocity errors, not made-up confidence percentages.
5. Train a separate exercise classifier with an explicit unknown class. Measure confusion between lunge/reverse lunge, curls/extensions, crunch/sit-up and transitions. Avoid using selected plan labels as ground truth predictions.
6. Calibrate heuristic score components against qualified human review; measure inter-rater agreement. Make feedback uncertainty and camera constraints explicit.
7. Benchmark hardware including integrated-graphics laptops. Record p50/p95 end-to-end latency, actual capture/render/inference rates, browser/backend memory, thermal throttling and long-session stability.
8. For shared hosting: add identity, authorization, per-user data isolation, CSRF/session protections, HTTPS, rate limits, audit logs, migrations and a shared session store. Add PostgreSQL only after these are designed.

No learned future-motion weights, medical validation or accuracy claims are included in this release.
