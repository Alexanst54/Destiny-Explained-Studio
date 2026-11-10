# Render the complete Atheon episode tonight

[Open Destiny Studio in Colab](https://colab.research.google.com/github/Alexanst54/Destiny-Explained-Studio/blob/feat/standalone-colab-production-studio/remotion/blender/Destiny-Studio-Colab-Pro.ipynb).

Use a fresh runtime for a new project so the latest PR #25 code is cloned. Select **Runtime → Change runtime type → GPU**, preferably Tesla T4. The notebook is usable without a local PC or terminal. GitHub Actions is never called or required.

## Exact starting instructions

1. Run **cell 1 — installation**. Set **`prepared_pilot_only = True`** to skip Torch/Kokoro/model downloads: this episode already has all six original English WAVs and timestamps. Mount Google Drive. Leave `projet_a_reprendre` empty for a new episode. Installation still obtains Blender, Node, ffmpeg and the Remotion browser.
2. Scroll directly to **“Render Complete Atheon Episode”** near the bottom. Do not run the older general Studio cells or the audio-only pilot preparation cell for this existing script.
3. Run **A. Prepare** with defaults: **Balanced / Fast 360×640 / 30 FPS / LOD0**. Default destination: `/content/drive/MyDrive/Destiny-Studio/atheon-episode-01-360-balanced`. Keep CPU rendering disabled for tonight's GPU run. The fast preflight checks original assets/timing, dependencies/browser, clean source commit, writable destination, reported mounted-Drive/local space and actual Cycles device discovery. Device discovery is not a completed GPU-render validation.
4. Run **B. Smoke-test**. It renders and exports the **entire first scene, 11.5 seconds / 345 frames**, preserving its complete 11.25-second original narration. Inspect the model, camera, English title/words, voice and backend. These same real frames are reused by C. This is not an additional throwaway render or a shortened narration. The first measured frames supply a rough ETA; no unmeasured T4 completion-time guarantee is made.
5. In **C. Render all six scenes**, check `first_scene_reviewed` after watching/listening, then run. It validates/reuses the first scene and any other completed frames. Each scene keeps its reviewed camera and animation. A Blender process handles at most 120 consecutive frames, with geometry/material reuse inside that block; no Blender restart per frame.
6. Run **D. Assemble** after all scenes finish. Remotion builds one continuous **9:16, 2672-frame, 30 FPS, approximately 89.067-second H.264/AAC MP4** from every original scene frame and the six original WAVs. No intermediate per-scene video encoding, image interpolation, frame repetition, narration truncation or speed change is used in production.
7. Run **E. Validate/download**. Enable `download_complete_mp4` to download from Android Chrome. The permanent Drive files are **`atheon-episode-01.mp4`** and **`atheon-episode-01.validation.json`**. The original English `subtitles.en.srt` is also saved. Large files skip inline embedding to keep the mobile output responsive; open the Drive copy or download instead.

The general standalone Studio remains unchanged by default: leave `prepared_pilot_only = False` if you want arbitrary English/French narration synthesis. The fast option only skips unnecessary tools for this prepared pilot.

## Resolution and time tradeoffs

Default **360×640 Balanced** prioritizes finishing rather than maximum pixel count. Optional 540×960, 720×1280 and 1080×1920 are available; Draft is also offered if the measured smoke-test is too slow. Geometry stays at explicit LOD0. No approved model or camera implementation is modified.

Choose a **new episode folder** when changing resolution/quality; existing content is preserved and incompatible caches are refused. To resume, keep `restore_saved_settings = True`; A reads the saved settings instead of silently applying newly selected defaults.

Free-space checks reserve a conservative uncompressed PNG/export bound. At the default resolution the initial reported-Drive reserve is approximately 2.53 GB and local reserve approximately 3.07 GB (decimal); compressed actual files may be much smaller. Cached frame count reduces the remaining Drive estimate. **Mounted Drive statistics may not expose the account's actual remote quota**; check Drive storage too. Failed checks are explicit and do not delete your data.

## Reconnect and resume

1. Keep the complete project folder in Drive. In installation cell 1, set **`projet_a_reprendre` to that folder**, keep `prepared_pilot_only = True` and mount Drive. The saved clean source commit is restored before running code.
2. Rerun A with that folder, then B/C/D as needed. Scene completion labels alone are never trusted: exact request/source fingerprints, decoded PNGs and SHA-256 are checked. The existing renderer resumes valid partial chunks; a corrupt PNG is recalculated without replacing other valid frames.
3. If the first-scene smoke already passes and its raw frames are intact, B reuses them and its validated MP4. C reuses each completed scene independently. D reuses a validated final export. A failed export can be reassembled from existing frames.
4. Keep `project.json`, `public/scenes/`, `scenes/`, `inputs/`, logs and reports. `public/scenes/<scene>/frames/chunk-*/` is the actual persistent frame cache, not a disposable public-copy directory. Do not delete it until the final export is safely stored.
5. On deliberate interruption, the dedicated notebook action sends SIGINT so the existing renderer can stop its separately-sessioned Blender worker. A still-running action retains a project lock and a second action refuses to overlap it. A lost VM releases the lock; atomic frame manifests allow recovery in a new runtime.

GPU is requested automatically for scene rendering. B/C stop before rendering any missing frames without NVIDIA OPTIX/CUDA unless CPU rendering is explicitly enabled; CPU fallback during rendering is reported and can be slow. **Assembly and validation do not require a current GPU** when cached frames already exist. The report distinguishes per-frame actual devices/backends, CPU frames, and actual T4 rendering. Probe-only detection never counts as rendered GPU validation.

## Validation and preserved inputs

The complete package is checked against the reviewed English script and archived evidence: six unmodified WAVs, sample counts, `en-US` / `af_heart` / speed 1×, exact source words, subtitle intervals, scene frame offsets, SRT and the fixed total 2672 frames. No resynthesis is performed by this route.

Final validation checks H.264/yuv420p, AAC, dimensions, duration, actual decoded frame count/FPS and non-silent audio. In addition, 10-ms PCM envelopes of each complete original utterance are compared with the decoded final audio at its measured scene offset (±50-ms search). This detects missing/misplaced audio, without claiming human-perfect pronunciation or frame-by-frame visual review. English title and six scene labels are supplied to the separate Remotion composition.

Read `reports/activity.json` and `logs/` on error. A missing scene prevents final assembly; pending/failed exports are not reported as completed. Unknown files without a trusted project manifest are not overwritten. A changed source requires restoring the saved commit or a new folder.

This PR does **not** merge anything, integrate PR #17, modify approved models, or change historical episodes. Local development tests and their limitations are in [COMPLETE-ATHEON-VALIDATION.md](COMPLETE-ATHEON-VALIDATION.md). Real T4/Colab/Android acceptance remains to be executed by the user; no GPU speedup or full-episode rendering is claimed from development tests.
