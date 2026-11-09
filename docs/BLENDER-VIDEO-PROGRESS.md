# 0.8.3 Blender-to-Video checkpoints

Base latest main cf2df80 (merged 0.8.2), branch feat/blender-video-pipeline-0.8.3. Never merge automatically.

## Inspection / chosen minimal integration

Existing exportFrame evaluates rigs, interactions and cameras directly from frame numbers. Riis generate() decorates each snapshot. HybridShort owns captions, audio, labels and transitions independently of the voxel renderer. episode.mjs already supports frame-range renders without retiming audio. Existing Kokoro ready project/WAV/word timestamps are locally available from prior development.

Plan: 90 distinct snapshots at 30 fps; deterministic environment; content-addressed persistent PNG cache with atomic completion hashes; optional HybridShort sequence prop replaces only matching voxel frames. All overlays/audio remain on original global timeline. New sequence notebook, existing single-PNG notebook untouched. Full HD requires a verified matching lower-resolution sequence first. No full 35-second video.

## Checkpoint 1

Implemented batch snapshot export, persistent per-frame cache/resume, progress/deadlines, optional Remotion image layer, and CLI sidecar flag. TypeScript passed. No GPU measurement claimed. Next: tests and low-resolution 90-frame CPU demo, mobile notebook, validation/report.

Resume: check git status; run targeted tests; use same project/cache/options to resume cached frames. Cache identity includes frame snapshots, renderer code hashes, Blender version, scale/device/threads. Do not change renderer files while benchmarking. Never rely on /content for surviving runtime deletion: Drive or downloaded cache is required.

## Checkpoint 2

PR draft #16: https://github.com/Alexanst54/Destiny-Explained-Studio/pull/16 . First checkpoint pushed. Initial real CPU run rendered 2/90 frames in 5.184s; second command reused those two completed frames and is rendering only the remainder, Draft/10%, CPU. Source: existing ready 0.7 project with genuine Kokoro audio and aligned words, frames 120–209.

Focused tests: 7 Node passed, 11 Python passed, including mocked interruption/resume, corrupted PNG retry, invalid inputs and Full HD preview gate. New notebook keeps cache and narration on optional mounted Drive, supports work limits, progress/deadlines and only a 90-frame Remotion extract. Existing PNG notebook unchanged. Next: finish 90 frames, render/probe 3-second MP4, verify audio/frame mapping, report and final checks. No GPU/remote Colab test claimed.
