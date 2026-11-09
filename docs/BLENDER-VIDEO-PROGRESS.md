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

## Checkpoint 3 — complete CPU draft and verified handoff

Real MP4 succeeded: remotion/out/hybrid-riis-07-blender.mp4, H.264/AAC, 108×192, 30 fps, 90 frames / 3.000s video (3.008s AAC/container), 200989 bytes. Six actors every frame, 90 unique PNG hashes; camera and poses change, city geometry remains constant. Audio correlation against original Kokoro 4–7s is .9994447, best lag 0ms. Visual sample inspected. Original full episode MP4 was not overwritten (new -blender output suffix).

Actual resume: 2 first frames 5.184s, remaining 88 with 2 cache hits 198.128s; final rerun verified all 90 hits, zero new frames, .865s controller time. Sum per-frame Blender times 199.937s, max Blender RSS 288444 KiB. No measured Remotion external wall time. Reports: remotion/blender/VIDEO-REPORT.md, video-validation.json. Existing PNG notebook unchanged.

Final tests: 16 Node passed, 12 Python passed, TypeScript passed, editor bundle regenerated and static check passed. No GPU, remote Colab, physical Android, Full HD, or full episode render. New notebook AST checked only; Drive/install behavior needs remote validation.

### Exact resume (same environment)

```sh
git fetch origin
git switch feat/blender-video-pipeline-0.8.3
git pull --ff-only
git status --short
cat docs/BLENDER-VIDEO-PROGRESS.md
python remotion/blender/sequence.py remotion/out/hybrid_riis_07-ready.json remotion/out/blender-video-cache --device cpu --detail draft --scale 10
# Node 22 must be on PATH; otherwise pass --node /path/to/node22
cd remotion
node --experimental-strip-types scripts/episode.mjs render out/hybrid_riis_07-ready.json --frames=120-209 --scale=0.1 --blender-sequences=out/blender-video-cache/dde5ce32657caf9a1fde473819fdc36dd9b81b90b0eabfa19a63d25853e210c2/remotion-sequences.json --browser-executable=/usr/bin/chromium
```

Fresh/Colab runtime: open Blender-Video-Colab-Pro.ipynb, REF feature branch before merge; mount the same Drive path, restore/generate narration, start Draft/10%/90 frames. Completed frames are reused if keys match; do not delete old cache folders. Use MAX_NEW_FRAMES=2 to inspect first images, then 90 to finish. Desired Full HD quality must first complete its matching lower-resolution preview. Download ZIP before ending the runtime if Drive was not selected. No renderer file edits during an in-progress job.

No remaining local implementation step for this handoff. Next external validation is actual Colab GPU operation and persistent Drive recovery. PR #16 must remain unmerged pending human review.
