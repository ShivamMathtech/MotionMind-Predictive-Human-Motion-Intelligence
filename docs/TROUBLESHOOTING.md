# Troubleshooting

## Windows setup
- Install Python **3.12 64-bit** with the Python Launcher. Verify `py -3.12 --version`.
- Avoid Python 3.14 for this release; pinned binary dependencies target the tested 3.12 environment.
- Extract the entire ZIP into a writable folder. Run `setup.bat`, not files directly inside the compressed folder.
- A virtual environment is created inside the project. No PowerShell activation-policy changes are required.
- If pip cannot connect, check your internet/proxy configuration and retry. Do not mix virtual environments from another project.
- If port 8000 is busy, close the previous app, or copy `.env.example` to `.env`, change PORT and add the matching localhost origin to ALLOWED_ORIGINS.
- If the browser does not open automatically, navigate to http://127.0.0.1:8000 while the terminal stays open.

## Camera
- Use Chrome or Edge, localhost or HTTPS. `file://` URLs do not work.
- Select Webcam, Connect camera, and allow the browser permission. Check OS camera privacy settings and close Teams/Zoom if the camera is exclusive.
- Choose the device in Settings, Save settings, then reconnect the camera.
- If a camera is unplugged, reconnect it and press Stop camera / Connect camera. Session counting naturally stops when frames stop arriving.
- Keep a single person visible and the full required limb chain inside the frame. Match the exercise's front/side-view recommendation.

## Model loading
- Confirm `frontend/dist/models/pose_landmarker_lite.task`, `dist/vendor/vision_bundle.js` and `dist/wasm/` exist.
- To rebuild: install Node 20+, then run `npm ci`, `npm run assets`, `npm run build` inside frontend. Restart the backend so it mounts the rebuilt frontend.
- Ad/script blockers or browser restrictions may block WASM or workers. Check the browser console. Demo mode can still run without pose inference.

## Counts and scores
- Start at the resting posture, reach the configured peak, and return. Partial reps and extremely fast movements are intentionally rejected.
- Low visibility and gaps reset the partial cycle so the system cannot invent a completed rep across an occlusion.
- Pausing also resets the partial cycle. After reconnect, press Resume and establish the rest posture again.
- Plank targets are seconds. The hold clock accumulates only reliable, approximately horizontal, aligned poses.
- Guided mode does not distinguish every visually similar exercise. Reverse lunge direction is selected manually.
- A heuristic form score is not an injury diagnosis or a measured accuracy percentage. A static good pose alone does not yield a completed rep or full ROM score.

## History / demo
- Demo sessions have their own history filter. They never improve camera workout charts.
- Finish & save closes the session. API exports include interrupted sessions. Progress charts use only finished sessions.
- Refreshing the page reconnects to an active session. Restarting the server cannot restore the in-memory rep phase; its last checkpoint is marked interrupted.
- Delete history is disabled while a session is active. Finish it first. Back up with Settings → Export workout data.

## Slow machine / 3D
- Select Performance, reduce maximum inference FPS, and use 640 × 360. Reconnect to change capture resolution.
- Hardware acceleration/WebGL may be unavailable over Remote Desktop. A clear 3D fallback message is shown; canvas tracking can still work.
- Close unnecessary browser tabs. The model uses CPU even if a GPU is present; browser rendering may use integrated graphics.

## Backend
- Local API health: http://127.0.0.1:8000/api/health. Swagger: /docs.
- Structured event logs appear in the terminal. Frame failures return an error without crashing the whole app.
- Database errors: confirm `data/` is writable and the disk is not full. Back up the database before manual repair.
- Do not run multiple backend worker processes: the current active-session registry is per-process. Use the supplied single-worker commands.
