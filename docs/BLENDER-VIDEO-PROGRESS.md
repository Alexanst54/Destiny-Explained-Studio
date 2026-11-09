# 0.8.3 Blender-to-Video checkpoints

Base latest main cf2df80 (merged 0.8.2), branch feat/blender-video-pipeline-0.8.3. Never merge automatically.

## Inspection / chosen minimal integration

Existing exportFrame evaluates rigs, interactions and cameras directly from frame numbers. Riis generate() decorates each snapshot. HybridShort owns captions, audio, labels and transitions independently of the voxel renderer. episode.mjs already supports frame-range renders without retiming audio. Existing Kokoro ready project/WAV/word timestamps are locally available from prior development.

Plan: 90 distinct snapshots at 30 fps; deterministic environment; content-addressed persistent PNG cache with atomic completion hashes; optional HybridShort sequence prop replaces only matching voxel frames. All overlays/audio remain on original global timeline. New sequence notebook, existing single-PNG notebook untouched. Full HD requires a verified matching lower-resolution sequence first. No full 35-second video.

## Checkpoint 1

Implemented batch snapshot export, persistent per-frame cache/resume, progress/deadlines, optional Remotion image layer, and CLI sidecar flag. TypeScript passed. No GPU measurement claimed. Next: tests and low-resolution 90-frame CPU demo, mobile notebook, validation/report.

Resume: check git status; run targeted tests; use same project/cache/options to resume cached frames. Cache identity includes frame snapshots, renderer code hashes, Blender version, scale/device/threads. Do not change renderer files while benchmarking. Never rely on /content for surviving runtime deletion: Drive or downloaded cache is required.
