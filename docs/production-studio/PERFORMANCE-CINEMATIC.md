# Atheon: measure performance before a cinematic rerender

This stacked work starts at PR #25 commit `4f006f1`. PR #25 remains unmerged. No approved model, prepared narration, original subtitle timestamps or historical episode is changed. GitHub Actions is neither called nor required.

## What is known

The user reports a successful 2672-frame, 540×960, 30 FPS episode on Colab Pro / Tesla T4 / OptiX, approximately 20 hours wall time, and approximately 10% observed GPU utilization. These are user observations, not measurements collected by this profiler. The original logs and video were not available in this development environment. 20 hours / 2672 is about 26.95 seconds per frame **including all work**, not measured Cycles kernel time.

PR #25 already builds once per block of up to 120 frames and enables Cycles persistent data. It does not restart Blender for every frame. Startup alone cannot be presumed responsible. Possible contributors include volumetric sampling, denoising/compositing, CPU scene synchronization, PNG work, mounted Drive latency, repeated verification and browser/export work. Low GPU utilization does not distinguish them.

PR #17 was inspected read-only at `146d43e0f5003a668896cdc2e7aed76f4f982290`: its `persistent_scene.py`, telemetry, GPU report and changed-file inventory target the earlier Riis per-frame bridge. Its CPU benchmark is not a T4 benchmark of Atheon. No commit was merged or cherry-picked, and no implementation was copied. This branch uses the existing universal builder/updater from PR #25 through separate profiling/production adapters.

## Exact mobile Colab benchmark procedure

[Open this branch's notebook](https://colab.research.google.com/github/Alexanst54/Destiny-Explained-Studio/blob/feat/atheon-performance-cinematic-direction/remotion/blender/Destiny-Studio-Colab-Pro.ipynb).

1. Start a fresh GPU T4 runtime. Run installation cell 1 with `prepared_pilot_only=True`, mount Drive, and leave the successful episode folder untouched. Keep one active runtime per project.
2. Optionally run **P0** against the completed original episode. It reads archived chunk timings/device reports without modifying the project; PNG verification is optional. Save its diagnostic outside the original folder. These historical sums are not a new wall-clock measurement. Then scroll to **T4 performance lab**. In **P1**, choose a **new** dedicated Drive folder, **30 frames**, **540×960** to match the reported run. P1 only writes the plan. 36, 48 and 60 frames are available; every case uses the exact same seed, source frames, six scene windows, approved LOD0 geometry and camera/animation selections.
3. In **P2**, enable `run_t4_benchmark`. Seven cases run sequentially on that same hardware. Each case renders 30 frames (five consecutive frames near each scene midpoint), not 30 frames total across all variants. Budget accordingly. Do not start a full episode yet.
4. Read `benchmark.json`, per-case `result.json`, `export-result.json`, `events.jsonl`, `gpu.jsonl` and raw Blender/Remotion logs. Open `comparison.html` with its accompanying folders; `visual-differences.json` includes paired PSNR and exact-file hash comparison. The silent, labeled `benchmark-montage.mp4` is a real representative-frame export, **not an episode**.
5. Inspect metal edges, core detail, haze, light shafts, portal noise and frame-to-frame denoising flicker. A PSNR value does not establish artistic equivalence. Review each case's actual device/backend and failures. A CPU fallback fails the GPU benchmark rather than being misreported as T4 work.
6. Interrupt a scratch case after some checkpoints; resume with identical sources/settings. Verify preserved hashes and that only missing/corrupt frames are rebuilt. A recovery run is labeled warm and excluded from speed ratios. For independent cold repeats use new folders; repeat with reversed case order via CLI `--cases` to assess thermal/order variance.
7. Reconnect using the benchmark folder in `projet_a_reprendre` in installation cell 1 to restore its saved clean commit. Rerun P1 with the same parameters and P2. Changing sources or settings refuses an incompatible manifest.

### Compared cases

| Case | Storage / process behavior | Samples / denoising | Purpose |
| --- | --- | --- | --- |
| `baseline-current` | Exact existing `render_universal.py`, direct Drive, one process per scene window | Existing Balanced 48 / existing denoiser | Real current reference; combined render/save/verify frame timing |
| `instrumented-drive` | Same approved build/update, separate render/save calls, direct Drive, build per window | 48 / existing | Quantify instrumentation/save-path overhead and separate phases |
| `scratch-blocks` | Local `/content`, read-back verified Drive checkpoints, build per window | 48 / existing | Isolate storage change |
| `scratch-persistent` | Local scratch, reuse compatible scene across windows | 48 / existing | Candidate without sample or model reductions |
| `samples-32-denoised` | Scratch / reuse | 32 / explicitly enabled available OIDN | Quality experiment, never automatically approved |
| `samples-32-no-denoise` | Scratch / reuse | 32 / off | Isolate denoising cost; likely noise tradeoff |
| `png-fast-threads-6` | Scratch / reuse, PNG compression 0, six Blender threads | 48 / existing | Lossless compression/CPU scheduling experiment; may increase Drive traffic |

All instrumented cases retain `scene.render.use_persistent_data=True` inside each window. The `persistent` case field controls reuse **across jobs**, not whether the current renderer already reuses data within a block. All cases keep resolution, geometry LOD, lighting, bounces, adaptive threshold, seed and narration assets unchanged unless the table explicitly says otherwise. The exact baseline and instrumented baseline are both needed: separated save calls and cProfile/telemetry impose overhead.

## What each measurement means

- **Startup:** parent launch to the worker-ready event, including Blender initialization/imports. Exact baseline's wall and worker/build/frame times permit a coarse residual only; they do not split exclusive startup time.
- **Scene construction:** wall and process CPU seconds with cProfile entries for procedural generation and `compile_design`. Nested cumulative function timings overlap and must not be added together.
- **Frame update:** wall/CPU time for camera/rig changes, overlays and dependency-graph synchronization. Geometry/object/vertex counts are saved to detect accidental reconstruction.
- **Cycles + compositing:** synchronous `bpy.ops.render.render(write_still=False)` wall and process CPU time. Raw Blender progress logs and approximate clock deltas distinguish sync/BVH, sampling, denoising and compositor stages. These are rounded progress clocks, **not exclusive CUDA kernel timing**. GPU kernels, driver time and CPU synchronization cannot be fully separated without an external GPU tracer.
- **PNG:** `Render Result.save_render` wall/CPU time includes encoding and filesystem writes. CPU seconds help locate CPU work but are not a pure codec timer. The scratch-vs-Drive pairing and separate checkpoint timings isolate storage effects more reliably.
- **GPU:** approximately one-second `nvidia-smi` UUID, name, utilization, memory utilization, used/total VRAM and power. These are device-wide samples that can miss peaks or include unrelated processes. Missing telemetry is null, never fabricated as zero utilization. Per-frame selected backend/device is saved separately.
- **Cache verification:** actual PNG decode/CRC/SHA timings, including resume verification. Strong validation is retained; an optimization never trusts filenames or completion labels alone.
- **Drive I/O:** restore, copy + readback validation + manifest checkpoint, byte counts, and final export copy. These measure mounted-filesystem behavior, not an API guarantee that remote storage has durably committed each write.
- **Remotion:** actual CLI composition + H.264 encoding wall time, browser/bundling included. Browser composition and encoding overlap, so the profiler reports the combined phase rather than inventing exclusive times. The benchmark montage has no narration; the complete production report measures the original six-WAV/AAC path, including audio verification.

Cold T4 paired ratios and render-only 2672-frame projections are emitted only for completed cold trials with actual T4-rendered frames. They are **not a claim of episode completion time**: 30–60 samples may not capture all camera/portal cost, and full audio composition/export, hardware variance and checkpoint delays need a budget. The target of under six hours remains unverified. No full rerender is automatically recommended. Prefer unchanged 48-sample Balanced settings until target-hardware measurements and visual review support a configuration. Do not infer a gain from CPU development tests.

## Separate directed edition

The legacy **Render Complete Atheon Episode** route remains available. Keep its completed project on its saved commit. The new **Cinematic Atheon** route writes into a new project and uses a new output name, `atheon-episode-01-cinematic.mp4`, so it never overwrites `atheon-episode-01.mp4`.

The treatment contains 19 shots:

| Scene | Visual narrative |
| --- | --- |
| The Hook | Monumental empty Vault and both gates, portal threshold, ground-to-head Atheon reveal |
| Who Is Atheon? | Full silhouette, head/torso mechanisms, articulated temporal-energy close-up |
| The Vault of Glass | Establishing shot, luminous Oracle field, approved Templar in the Templar's Well, return to Atheon |
| Master of Time? | Ochre/cyan portal landscapes, teleporting anonymous Guardian silhouettes, return view; label explicitly limits the interpretation to Vault-local timelines |
| The Guardians | Six silhouettes on the actual combat-deck height, Oracle lights, original abstract Aegis-inspired shield, Atheon combat pose |
| The Mystery | Aftermath, empty throne, slow retreat to the unanswered Vault; no assertion that the Vex control all universal time |

Portals already have animated procedural interference; the adapter animates their time input, luminous motes, silhouettes and existing approved articulated poses. No boss geometry or animation provider is rewritten. Terrain beyond portals, anonymous Guardians, Oracle staging and shield are **editorial procedural reconstruction**, not extracted game assets or a claim to exact encounter simulation. This is a shot treatment, not an implemented gameplay battle or new Guardian character library.

Original six English narrations, title, measured scene offsets and all native word intervals are preserved. Subtitle groups contain at most six words, favor short clauses and retain each word's timing for highlighting. Text stays between 8% left / 16% right margins and above the bottom 20%, away from typical mobile overlays. Eight-frame scene-edge image fades do not alter, overlap or retime narration. Internal shot cuts are intentional; full art/motion review remains required.

### Run only after measuring

- **Q1:** prepare a NEW directed Drive folder and choose resolution. Unchanged Balanced 48 samples, LOD0 and existing denoiser are the conservative candidate, not a measured recommendation. Source commit and identity are saved.
- **Q2:** render/inspect real still previews for every shot/chunk. Gallery and images are saved in Drive. Stills do not validate animation.
- **Q3:** explicitly confirm benchmark and preview review. Select a single scene first to inspect its motion, or all six only when satisfied. The CLI supports `--scene`; completed scenes can resume independently.
- **Q4:** assemble and validate all 2672 distinct source frames with their six original WAVs and native captions, then download. Missing/corrupt frames or original-audio hash changes prevent a valid export. Validation checks H.264/AAC, dimensions, duration, FPS, decoded frame count and original utterance alignment.

Scratch rendering checkpoints after every ten completed frames and each job boundary. At most nine new frames after the last successful checkpoint may need recomputing after an abrupt VM loss. A graceful interruption tries to checkpoint partial output. Every copied PNG is validated before the Drive manifest is published. Unknown or incompatible projects are refused, not deleted. Use one active VM per project: locks are not a distributed Drive lease. Check actual account quota separately from mounted Drive space statistics.

Final composition stages validated frames/WAVs into `/content` to avoid browser frame reads from Drive. Its report separately records staging, composition/encoding, final Drive copy, cache validation and actual per-frame devices. Leave enough local space for the frame cache plus staged composition cache and export. No cache is automatically deleted.

## Local validation and remaining acceptance

See [PERFORMANCE-CINEMATIC-VALIDATION.md](PERFORMANCE-CINEMATIC-VALIDATION.md). T4/Colab/physical Android benchmarks are **not executed in this development environment**. The user-reported successful T4 episode is acknowledged but not relabeled as this branch's benchmark. No speedup or under-six-hour result is claimed. Models remain approved and unchanged; the directed edition remains pending full visual/motion review.
