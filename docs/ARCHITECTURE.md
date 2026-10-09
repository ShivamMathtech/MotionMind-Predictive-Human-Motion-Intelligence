# Architecture and implementation map

## Pipeline
The browser owns camera permission and capture. The video element decodes frames independently. A `requestAnimationFrame` scheduler transfers resized `ImageBitmap` objects to a classic Web Worker. The worker hosts MediaPipe Tasks WASM with the CPU delegate. One frame can be in flight, so work never accumulates in an unbounded queue. Results contain 33 landmarks and visibility scores. No JPEG encode/decode loop is involved.

Camera and synthetic streams share the same landmark WebSocket protocol. Only one socket sample is pending at a time. The server validates numeric ranges and array shape, smooths 2D positions, applies aspect-ratio correction, chooses a visible body side and runs the selected exercise state machine. Occlusion, source gaps, pause or reconnect discard incomplete reps. A rep must pass rest → peak → rest and minimum-duration checks. Plank accumulates visible, roughly aligned horizontal hold time.

The frontend refreshes metrics at approximately 5 Hz and draws canvas independently. Three.js renders up to 30 FPS using reused geometry. The backend performs analysis/database operations using `asyncio.to_thread`; session locks serialize WebSocket updates and HTTP controls. Runtime state survives a temporary socket reconnect while the server is running. Socket loss pauses the workout; reconnect requires Resume. A backend restart marks active sessions interrupted; prior persisted metrics remain exportable but the in-flight workout cannot resume.

## Main modules

| Path | Responsibility |
|---|---|
| `frontend/src/App.tsx` | Dashboard, pages, session controls, WebSocket lifecycle |
| `frontend/src/vision/useCamera.ts` | Permissions, worker scheduling, adaptive inference |
| `frontend/public/pose-worker.js` | Local MediaPipe model/WASM loading and inference |
| `frontend/src/vision/demo.ts` | Deterministic synthetic landmarks for all guided modes |
| `frontend/src/components/PoseViews.tsx` | Canvas overlay and reusable Three.js geometry |
| `frontend/src/components/PlanEditor.tsx` | Plan add/remove/reorder/targets |
| `frontend/src/components/Analytics.tsx` | Session details, charts and filtering |
| `backend/app/main.py` | HTTP/WS routes, validation orchestration and application lifecycle |
| `backend/app/workout.py` | Session/set state, transitions and persistence |
| `backend/app/exercises/` | BaseExercise plus 14 configured subclasses |
| `backend/app/vision/landmarks.py` | Angles and EMA smoother |
| `backend/app/prediction/` | Bounded trajectory history and baseline extrapolation |
| `backend/app/analytics/` | Evidence-based matching-session insights |
| `backend/app/database/` | SQLAlchemy schema, WAL setup and initialization |

## SQL schema

| Table | Main fields | Relation |
|---|---|---|
| users | id, name, weight_kg, settings JSON | Local profile id 1 |
| exercises | id, definition JSON | 14 seeded definitions |
| workout_plans | id, name, items JSON | Ordered exercise/sets/target records |
| workout_sessions | id UUID, plan_id, started, finished, mode, status, duration, summary JSON | One workout |
| exercise_sessions | id, session_id, exercise_id, set_number, metrics JSON | One set |
| repetitions | id, exercise_session_id, metrics JSON | Completed reps with ROM/tempo/form |
| form_scores | id, exercise_session_id, elapsed, score, components JSON | At most one sample/sec |
| motion_metrics | id, exercise_session_id, elapsed, metrics JSON | Angle/ROM/tempo samples |
| feedback_events | id, exercise_session_id, elapsed, message | Changed feedback only |
| progress_metrics | id, session_id unique, metrics JSON | Finished session summary |

SQLite uses foreign keys, WAL and a busy timeout. Raw frame and raw pose sequence columns intentionally do not exist. JSON fields keep the local schema extensible; PostgreSQL migration requires installing its driver and creating a managed migration strategy (no Alembic migrations are supplied).

## Scores and predictions

Form component weights: alignment .30, observed ROM .25, stability .20, measured tempo .15, bilateral symmetry .10. Unavailable components are excluded and remaining weights renormalized. Stability uses angular second differences; it remains sampling-sensitive and requires calibration. Session score averages are averages of per-set averages, not confidence-weighted biomechanics measures.

Prediction retains 12 samples and extrapolates a capped constant velocity for 250 ms. Direction consistency is the share of same-sign progress steps, not a probability. Threshold ETA assumes continued motion at the recent velocity. No next-exercise intention is inferred.

## Deliberate scope decisions

Browser inference replaces Python webcam capture to avoid sending images over the socket and to support host cameras in Docker. SQLite replaces a standalone database service in the local stack. EMA is the implemented smoother; One Euro parameters are not advertised. All exercise subclasses share a common angle-based state machine and use catalog parameters. This is guided tracking rather than a trained exercise classifier. The API is single user and unauthenticated by design for loopback use only.
