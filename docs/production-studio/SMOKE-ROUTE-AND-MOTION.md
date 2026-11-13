# Investigating `atheon-smoke` before any full rerender

## Route finding

The user supplied the filename **`atheon-smoke`**. In the actual PR #26 notebook and entry points, the stock `atheon-smoke.mp4` file is produced by **B. Smoke-test → `complete_atheon.py smoke`**, the prepared pilot route inherited from PR #25. It does not call the cinematic director.

That route uses scene 1's original `camera=environment`, mapped by `universal/worker.py` to `venus_vault`'s **`wide`** camera. In `venus_vault/camera.py`, the Glass Throne `wide` position is `(17, -48, 21)`, target `(0, 21, 15)`, lens 30; these values do not depend on frame. An almost fixed composition in that video is therefore expected and is not evidence that Q's 19 shots failed.

| Notebook cell | Entry point | Output / expected scope |
| --- | --- | --- |
| General Studio **3. Smoke-test** | `production.py --smoke` | `smoke/video.mp4`, two seconds / 60 frames at 30 FPS |
| Prepared pilot **B. Smoke-test** | `complete_atheon.py smoke` | **`atheon-smoke.mp4`**, scene 1 only, 345 decoded video frames / 11.5 seconds at 30 FPS, static wide camera |
| **Q1** | `cinematic_atheon.py prepare` | Project and directed plan; no rendered images |
| **Q2** | `cinematic_atheon.py preview` | Real still previews; **no motion MP4** |
| **Q3** | `cinematic_atheon.py render` | Directed image sequences; requires explicit full-render approval flags |
| **Q4** | `cinematic_atheon.py assemble` | `atheon-episode-01-cinematic.mp4`, full 2672-frame episode |
| New **M1–M3** | `motion_test.py` | `atheon-motion-test.mp4`, exactly three seconds / three moving cinematic compositions, silent diagnostic |

The user's MP4 itself was not provided in this environment. The filename identifies the stock route, but the reported **11.52 seconds / 346 frames is not a verified decoded-stream measurement here**. The current prepared package locks 345 video frames / 11.5 seconds. Container/audio duration or a player's duration-derived frame estimate may differ; an older/custom source is another possibility. Do not change frame count or speech to match a GUI value.

**R0** checks the actual saved `project.json`, archived camera matrices and `ffprobe -count_frames` output. It reports the video stream's decoded frames, video duration, container duration and FPS separately. It never writes inside the completed project. `identity.kind=complete-atheon-v1` identifies the legacy prepared pilot; `directed-atheon-v1` identifies Q. Unknown identities remain unknown rather than being guessed from duration.

## Timeline verification and instrumentation fixes

All **19 shots** cover global source frames **[0,2672)** exactly once across six scenes. The native Blender audit evaluates the actual directed camera on **every one of those 2672 source frames**, including cuts and scene transitions, without rendering any episode images. Position/lens must match the intended shot; every shot moves, cuts have different transforms, and geometry/design hashes remain stable.

The existing job/image mapping was correct. Some `shot_at()` diagnostic bounds used `round(fraction * frames)` while the actual selector changes at the first integer frame satisfying `frame / frames >= fraction`. For example the Templar begins at scene-local frame **284**, not 283. The fix aligns logged ranges to the actual selector; it does not move the cut or redesign a camera/model.

Every newly rendered cinematic frame now records:

- Unique scene/shot ID, camera preset ID and Blender camera object name.
- Scene-local and episode-global source frame, half-open shot ranges.
- Actual `matrixWorld`, camera position, lens, sensor fit and expected-position error.
- Update/render/PNG wall and CPU measurements plus Linux scheduler evidence.

The same `camera-applied` records appear in `renders/events.jsonl` and each frame's `cameraDiagnostic` inside its `profile.json`. A discrepancy between requested and applied camera raises an error before accepting a frame.

Final job-boundary Drive checkpoints were previously copied successfully but omitted from the worker checkpoint-duration sum for short jobs. They are now measured too. This corrects instrumentation, not a measured GPU-speed optimization.

## Exact Colab cells — no full episode

[Open the PR #26 notebook](https://colab.research.google.com/github/Alexanst54/Destiny-Explained-Studio/blob/feat/atheon-performance-cinematic-direction/remotion/blender/Destiny-Studio-Colab-Pro.ipynb).

1. Start a **fresh T4 GPU runtime**. Run installation **cell 1** with `prepared_pilot_only=True` and an empty `projet_a_reprendre`. This loads the updated diagnostic code instead of restoring an older project's source. Mount Drive.
2. Scroll to **Identify the route, then test three moving cinematic shots**. In **R0**, enable `inspect_smoke_route`, set `existing_smoke_path` to the actual old project folder or `atheon-smoke.mp4`, and save `route_report` in a sibling location outside that project. Inspect the manifest classification and decoded count. Original bytes/caches are read only.
3. Run **M1** with a **NEW sibling Drive folder** such as `MyDrive/Destiny-Studio/atheon-three-shot-motion-01`. Defaults: **Balanced / 540×960 / 10 output FPS**. It only saves the plan and source identity. It does not render images. For a quicker visual-only diagnostic choose Draft / 324×576 in a new folder; that is not a performance comparison against the Balanced original.
4. In **M2**, enable `run_three_shot_test` and execute. It renders only **30 real images**, ten per shot, and exports a **three-second** silent H.264 clip with visible shot/camera/source-frame labels. The frames sample every third original 30-FPS source frame, so movement time is preserved at reduced temporal resolution. No repeated stills, artificial interpolation or pilot audio cut is used. Optional 30 output FPS renders 90 real images, still only three seconds.
5. Watch the three distinct compositions: **Vault establishing → monumental Atheon → head/torso mechanism close-up**. Inspect motion within each shot as well as the cuts. Then run **M3** for actual camera transforms, phase times, backends, GPU power/utilization and sampled VRAM. Read `motion-validation.json`, `renders/result.json`, `renders/events.jsonl`, `renders/gpu.jsonl` and per-job `profile.json`.

For this investigation **do not execute B, Q3/Q4 or the full prepared episode C/D**. M's CLI has no full-render action and permits only 30 or 90 diagnostic frames. It refuses paths inside an existing project. On interruption, retain the new diagnostic folder and restore its saved commit/settings before resuming M1/M2; valid frames are reused independently. Original episodes, approved models, narrations and existing caches remain untouched.

## Measurement interpretation and optimization decision

The test measures scene construction (wall/process CPU + geometry profiles), frame update, render-and-compositor operation, PNG encode/write, verification, Drive checkpoint/restore, composition staging, Remotion and final copy. `renderAndCompositeSeconds` is the synchronous Blender operation, **not an exclusive CUDA kernel measurement**. GPU power/utilization/VRAM come from actual device-wide `nvidia-smi` samples; the selected OptiX/CUDA backend comes from each rendered frame. Probe-only discovery does not count as rendering validation.

CPU scheduling includes per-thread runnable queue wait and voluntary/involuntary context switches. It cannot attribute the duration of blocking specifically to GPU or I/O. **Do not subtract multithreaded process CPU seconds from wall time and label the result GPU time or CPU waiting.** Missing/unavailable measurements are null.

The development environment has CPU only and ordinary local filesystem directories, not a T4 or mounted Google Drive. The delivered local motion clip is explicitly Draft/324×576/10 FPS. Its phase table validates instrumentation and real movement, not the reported Colab performance. No GPU-utilization percentage, wattage, VRAM value or speedup is invented.

No production samples, denoiser, thread count, GPU backend policy or approved geometry is changed by this investigation. Measurements on the actual T4/Drive path are required before selecting any optimization or recommending a complete rerender. The existing paired P1/P2 benchmark remains available after this short route/motion check.

[Measured local results and actual motion clip](SMOKE-MOTION-VALIDATION.md).
