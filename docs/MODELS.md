# Model setup and provenance

This release bundles the official **MediaPipe Pose Landmarker Lite float16 v1** model and the WASM files corresponding to the pinned `@mediapipe/tasks-vision` package. These are pretrained pose-estimation assets, not a custom-trained exercise or future-motion model.

Official model URL:
https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task

Official API / worker guidance:
- https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker/web_js
- https://github.com/google-ai-edge/mediapipe-samples-web/blob/main/src/workers/pose-landmarker.worker.ts
- https://github.com/google-ai-edge/mediapipe

Runtime paths:
- `frontend/public/models/pose_landmarker_lite.task`
- `frontend/public/wasm/*`
- `frontend/public/vendor/vision_bundle.js`
- Copies of these paths inside `frontend/dist/` for the prebuilt application.

To restore assets after installing frontend dependencies:

```bash
cd frontend
npm ci
npm run assets
npm run build
```

The asset script copies the pinned package's WASM and CommonJS bundle. It downloads the official Lite model only if no complete bundled copy exists. A minimal `self.exports` shim lets the bundle run in a classic worker, which supports the runtime's script loading. Inference uses `delegate: CPU`, one pose, VIDEO mode and no segmentation masks. No API key is required.

The browser must support WebAssembly, Web Workers, OffscreenCanvas, ImageBitmap and camera capture. Use current Chrome or Edge on localhost. MediaPipe's model estimates 33 landmarks. Model loading failures are visible in the camera panel; Demo mode remains usable without the model.

The SHA-256 manifest in `models/SHA256SUMS.txt` records packaged assets. Third-party dependencies and assets retain their upstream licenses. See `THIRD_PARTY_NOTICES.md` and `models/LICENSE.mediapipe`.
