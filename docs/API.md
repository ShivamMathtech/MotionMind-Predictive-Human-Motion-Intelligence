# API and WebSocket

Interactive schema: `/docs`; JSON schema: `/openapi.json`. API base `/api`.

| Method | Path | Purpose |
|---|---|---|
| GET | /health | Service and engine metadata |
| GET / PUT | /profile | Local profile, weight and settings |
| GET | /exercises | Catalog with angles, instructions and form rules |
| GET / POST | /workouts | List/create plans |
| GET / PUT / DELETE | /workouts/{plan_id} | Inspect/edit/delete a plan |
| POST | /workouts/{plan_id}/start | Create camera or demo session |
| GET | /sessions/active | Current runtime state or null |
| POST | /sessions/{id}/command | pause, resume, next |
| POST | /sessions/{id}/finish | Finish and persist; repeat calls are idempotent |
| POST | /workouts/{session_id}/finish | Compatibility finish route |
| GET | /sessions/{id} | Details including sets, rep records and feedback |
| GET | /history?mode=camera&days=30 | History; mode camera/demo/all; days 0 means all |
| GET | /progress?mode=camera&days=30 | Completed-session analytics and exercise volume |
| GET | /analytics | Alias of progress |
| GET | /export | JSON export of profile/plans/detailed sessions |
| DELETE | /history | Remove all saved sessions; blocked while active |
| DELETE | /data | Reset profile, plans and history; blocked while active |
| GET | /diagnostics | CPU/memory and active session count |

Plan example:
```json
{"name":"Squat Practice","items":[{"exercise":"squat","sets":3,"reps":12}]}
```
Start body: `{"mode":"demo"}` or `{"mode":"camera"}`. Plank `reps` means target hold seconds. A session snapshots its plan. The local release permits one active session and one connected motion socket. Statuses: active, paused, resting, finished, interrupted. `next` ends the current set and opens the next; the UI asks before skipping an unfinished set.

## WebSocket `/ws/motion`

First send `{"type":"init","session_id":"<id returned by start>"}`. Receive `{"type":"state","state":{...}}`. Then send each frame:

```json
{"type":"pose","timestamp":12.34,"aspect":1.7777778,"landmarks":[{"x":0.5,"y":0.3,"z":-0.1,"visibility":0.98}]}
```

The example shows one landmark for readability; **exactly 33 MediaPipe landmarks** are required. Timestamp is monotonically increasing seconds from the capture clock. No visibility-confident landmarks available: send 33 zero-visibility points. No raw image data is accepted. Maximum JSON payload is 32 KiB. Wait for a response before sending the next pose.

Responses contain type `motion`, `valid`, reps, hold_seconds, phase, confidence (landmark visibility), form_score, score_parts, angle, angles, rom, tempo, feedback, pose, prediction, rep_event, processing_ms and state. Low-confidence responses omit angle and prediction data. `rep_event` appears only on the completion sample. `state.summary` carries current cumulative metrics. The prediction method is labelled; reliability is direction consistency, not trained model confidence.

Errors: `{"type":"error","message":"..."}`. Ping: `{"type":"ping"}` → pong. Invalid frames do not terminate the socket. Unknown sessions and foreign browser origins are rejected. Automatic reconnect restores the server's current state; press Resume after a connection loss.

HTTP errors use FastAPI `detail`; 404 for missing entities, 409 for incompatible state, 422 for invalid inputs. No public authentication system is supplied. Bind to localhost.
