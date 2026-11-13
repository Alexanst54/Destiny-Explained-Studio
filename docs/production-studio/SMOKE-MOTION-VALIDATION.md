# Smoke-route investigation: validation

The reported name `atheon-smoke` resolves to the prepared-pilot **B** entry point in the current notebook, not Q's director. The actual user's file is not available locally, so its 346-frame/11.52-second GUI report is not presented as decoded evidence. R0 must establish its saved source and exact stream metadata on Drive. See [route analysis and exact Colab cells](SMOKE-ROUTE-AND-MOTION.md).

## Executed checks

- **118 Node tests, 106 Python tests** (36 Studio, 56 Blender, 10 narration, 4 manifest), and all three TypeScript configurations pass.
- Blender 4.3.2 evaluated **all 2672 camera positions across 19 shots** without rendering episode images. Actual position/lens/look direction matches the intended camera, all cut/scene ranges are contiguous, each shot moves, cuts differ, and model geometry remains stable. [Native audit](smoke-motion-evidence/all-frame-camera-audit.json).
- Six targeted tests cover exact half-open ranges, the fixed legacy wide camera/345-frame plan, bounded three-shot source-time sampling, route identification from manifests, unavailable GPU/power values and correct scheduler-wait semantics.
- The inspector ran on a genuine archived general-Studio smoke: it reported 48 decoded video frames at 24 FPS, 2.0 video seconds and 2.005 container seconds. This [archived example](smoke-motion-evidence/archived-general-route-example.json) is **not the user's Atheon smoke**. Existing source bytes were only read.
- Existing Studio and Lot C evidence verification passes. Approved model/provider sources, original prepared episode/script/WAV/timestamps, historical episodes, narration and legacy render entry points remain unchanged. No full episode was rendered, no PR was merged and no Actions were invoked.

## Real short motion evidence and measurements

The delivered clip is a **three-second silent diagnostic**, with three genuine moving compositions, not a repeated-still montage or a shortened narration. Local quality is explicitly **Draft / LOD0 / 324×576 / 10 output FPS**, sampling each third original 30-FPS source frame. CPU-only local data verifies behavior and instrumentation; it is not a benchmark against the user's Balanced T4 run. Local development tests overlapped part of rendering, so local timing is not a controlled performance comparison.

[Actual H.264 motion clip](smoke-motion-evidence/atheon-motion-test.mp4) · [Validation and phase data](smoke-motion-evidence/motion-validation.json) · [Per-frame shot/camera/matrix events](smoke-motion-evidence/per-frame-cameras.jsonl).

| Measured local component | Seconds |
| --- | ---: |
| Blender process wall | 562.650 |
| Startup to worker ready | 0.294 |
| Scene preparation wall | 0.364 |
| Scene preparation process CPU | 0.380 |
| Frame updates wall | 0.500 |
| Render + compositor wall | 559.623 |
| Render process CPU (summed threads) | 1031.540 |
| PNG encode + write wall | 0.758 |
| PNG validation wall | 0.101 |
| Worker checkpoints — ordinary LOCAL disk, not Drive | 0.362 |
| CPU render runnable queue wait (thread-seconds, not wall) | 612.312 |
| Local composition staging | 0.010 |
| Remotion composition + encode wall | 16.011 |
| Final local export copy | 0.001 |

CPU-only actual backend: **CPU**, OptiX/CUDA backend **null**. GPU utilization/power/VRAM: **null**, no NVIDIA hardware. Frames: **30**, cold cache; warm resume: **30 verified hits, zero new frames, zero builds, unchanged MP4 hash**. Do not add overlapping CPU/thread/operation measurements as if they were exclusive wall phases.

## Measurement boundaries and optimization decision

Actual GPU utilization, power, VRAM and OptiX/CUDA timing remain **unmeasured here**: the local rendering backend is CPU. Missing GPU metrics are null, not zero. The M1–M3 cells collect those values on the user's T4. Device-wide sampling cannot prove exclusive kernel timings; render/compositor and PNG encode/write have explicitly overlapping components.

CPU runnable scheduler wait is summed across observed threads and may exceed wall time. It is not the duration of blocking on GPU or Drive. That duration is left null; multithreaded CPU seconds are never subtracted from wall time to invent a GPU metric.

The changes fix diagnostic range metadata, route visibility and missing job-boundary checkpoint accounting. **No production samples, denoiser, thread count or approved geometry were optimized without target-hardware evidence.** No speedup, six-hour completion or full cinematic visual acceptance is claimed. The next decision should use the actual T4 M3 report and, if needed, the paired P1/P2 benchmark.

All new media/reports use a separate diagnostic folder. Previous Q/benchmark caches remain available on their saved source commit; changed render-source identity is refused instead of overwriting them. The complete original episode and narration are preserved.
