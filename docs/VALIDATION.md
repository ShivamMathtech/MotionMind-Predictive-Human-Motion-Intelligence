# Validation record

Validation performed on 2026-10-08 in a Linux container using Python 3.12, Node 24 and a headless Chromium 133 browser. No physical webcam was attached.

| Check | Result |
|---|---|
| Python tests | 28 passed |
| Frontend Vitest tests | 5 passed |
| Strict TypeScript compilation and Vite production build | Passed |
| Synthetic exercise sequences | All 14 modes accepted; 13 cyclic modes counted exactly 2 reps; plank accumulated hold time |
| Low-confidence / stationary / gap handling | Passed; partial reps discarded and static poses do not count |
| API CRUD, validation, metrics export and delete | Passed |
| WebSocket pause / resume / disconnect / reconnect / next set | Passed |
| Prebuilt dashboard, local worker JS MIME and model route | Passed |
| Real browser demo workflow | Passed: start, 2 observed synthetic reps, pause, resume, finish, saved history, progress charts |
| Plan, empty analytics and backend failure UI | Passed in component tests |
| Exercise library search and settings save | Passed in browser |
| Responsive rendering | Inspected at 1536 px desktop and 390 px mobile; no horizontal overflow |
| Three.js skeleton | Rendered in headless WebGL, desktop and mobile layouts |
| Local CPU MediaPipe worker | Loaded bundled WASM/model, completed warm-up and blank-frame inference |
| Pose inference on provided reference image | Returned 33 landmarks |
| Missing physical camera | Clear “Requested device not found” message; UI remained usable |
| Browser JavaScript errors | None during successful end-to-end/model checks |
| Process diagnostics unavailable in sandbox | Returns null instead of failing Settings |

The model check verifies the actual pretrained pose-estimation path on a reference image, not exercise recognition accuracy on video. Blank-frame inference correctly returned no detected pose. The demo is explicitly synthetic and stored separately from camera data.

## Boundaries of verification

- Physical webcam capture, camera-specific exposure/focus, voice services, long-session performance, Windows batch execution and Docker execution were not directly tested in this Linux environment.
- No real-world exercise accuracy study, clinical validation, individual biomechanical calibration, or trained future-motion evaluation has been performed.
- Production build gives a nonfatal size advisory for the chart library chunk. Backend tests report one dependency deprecation warning; no tests fail.
- The supplied release is single-process, local and single-user. It is not ready for public internet hosting without further engineering.

## Run your hardware acceptance check

1. Extract the ZIP, install Python 3.12 and run setup. Check that Home loads at localhost.
2. Run Demo for 12 seconds and confirm rep counts change. Pause, resume, finish and review Demo history.
3. Select Webcam and grant permission. Wait for MediaPipe to load. Keep your body visible in the exercise's specified view.
4. Start a squat practice plan. Complete five deliberate repetitions and manually compare the count. Check that partial movements do not count.
5. Briefly leave the frame. Ensure low-confidence feedback appears and rep counting stops.
6. Change camera/resolution in Settings, save and reconnect. Review measured inference FPS and latency.
7. Finish and check Camera history, charts and export. Demo sessions must remain excluded.
8. Test each additional exercise mode with manual labels before relying on its counts. Adjust documented catalog thresholds for your setup.
9. Compare responsiveness during a five-minute session. Record hardware, camera, resolution and latency distributions.
