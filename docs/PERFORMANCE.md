# Performance and calibration

## Profiles

| Profile | Requested camera resolution | Maximum inference rate | Processing width |
|---|---|---|---|
| Performance | 640 × 360 | 9 FPS | 640 pixels |
| Balanced | 1280 × 720 | 12 FPS | 640 pixels |
| Quality | 1920 × 1080 | 18 FPS | 960 pixels |

Actual capture resolution/FPS depends on the camera. A slow detector lowers inference rate to approximately `min(configured rate, 1000/(1.25*latency_ms))`, with a 5 FPS scheduling floor; the one-frame-in-flight rule still prevents work piling up if inference is slower. Above 110 ms, input processing width drops to 480 pixels. Video remains at the camera's available playback rate. The first frame initializes parts of the graph and can be much slower than subsequent frames.

The dashboard's inference FPS is measured completed detections/sec. The camera FPS shown by the current implementation is the browser track setting, not a measured capture counter. Backend processing time excludes transport and inference. Therefore it is **not** end-to-end latency. The 3D renderer is capped at 30 FPS, and the overlay follows requestAnimationFrame. Browser CPU/memory are not included in backend memory diagnostics.

## Design

- Camera video never enters React state.
- One transferable bitmap at a time; bitmap resources are closed after detection.
- One outstanding WebSocket sample; skip surplus samples rather than queue them.
- Metric state updates throttled to roughly 5 Hz; canvas/3D use mutable pose buffers.
- Current and predicted skeleton geometry is reused.
- Pose inference initializes only after camera connection.
- SQL writes sampled at 1 Hz except completed reps and state changes.
- Runtime prediction history is bounded; form-score buffers are capped.
- No external fonts, animation libraries, cloud LLMs or image uploads are needed.

## Threshold configuration

Environment: `SMOOTHING_FACTOR` defaults to .65, `MIN_CONFIDENCE` .55, `MIN_REP_SECONDS` .6, `FEEDBACK_COOLDOWN` 2 seconds. Angle thresholds live in `backend/app/exercises/catalog.py`. Edit `BaseExercise` to change score weights, hysteresis (.15/.85), gap reset (.8 s) or posture rules. Re-run tests after any change.

Higher EMA factors reduce delay but increase jitter. Thresholds were selected as initial rules and need per-view/person validation. Do not interpret synthetic fixture success as real-world accuracy. Metrics using 2D landmarks change with camera angle; keep the camera fixed for comparisons.

Benchmark on the actual target i5/Ryzen machine for at least five minutes: record input resolution, achieved inference FPS, dropped samples, inference latency percentiles, full end-to-end latency, host utilization and browser memory. Test multiple lighting conditions, body types and viewpoints. No benchmark guarantees are included.
