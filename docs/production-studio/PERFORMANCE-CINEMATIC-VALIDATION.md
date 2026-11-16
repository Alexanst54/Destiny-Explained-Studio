# Performance and cinematic direction: validation scope

Date: 2026-11-12. Base: PR #25 `4f006f1`. Target-platform acceptance remains pending; no T4 speedup or six-hour result is claimed.

## Executed locally

- **118 Node tests**, **100 Python tests** (30 Studio, 56 Blender, 10 narration, 4 manifest), and all three TypeScript configurations pass. The initial Node run correctly rejected the stale notebook asset hash; regenerating the audit and repeating resolved it.
- Native Blender checks pass for **19 directed shots**: reverse/random-access camera and articulated pose evaluation is deterministic, approved design hashes remain stable, mesh/vertex counts do not grow during updates. This check renders zero images and is distinct from still evidence.
- [Six real CPU Blender previews](performance-cinematic-evidence/README.md): establishing Vault, Atheon reveal, Templar, Guardian team and both revised portal views. Balanced/48 samples, LOD0, 360×640, Blender 4.3.2. All were visually inspected. The initially occluded portal camera was revised and both gate views were actually rerendered.
- A separate original CPU frame rendered with split render/save calls is pixel-identical to the existing renderer's original frame (ffmpeg PSNR infinite). This validates one frame's save-path equivalence, not GPU or all-samples equivalence.
- Real scratch/checkpoint/warm-resume exercise: three verified frame hits, zero newly rendered frames and zero builds on resume. Local filesystem directories represented both sides; no actual Google Drive I/O performance was measured.
- Real Remotion H.264 export of three distinct rendered images passed decoded frame count. This **silent 0.1-second labeled montage is not the pilot or an animation validation clip**. Its combined CLI timing includes browser startup/bundling. The real-word subtitle screenshot is a separately labeled layout fixture using a genuine still.
- The actual pinned-dependency/source/device preflight ran locally and correctly refused the GPU benchmark on CPU before rendering any benchmark frames. [Actual probe](performance-cinematic-evidence/actual-local-device-probe.json). Drive capacity checks remain untested on real Drive.
- Read-only inspector test confirms completed-project bytes remain unchanged; synthetic corrupted PNGs are detected when verification is enabled. Offline tests cover checkpoint corruption/repair, restored source identity, frame continuity, canonical Atheon/Templar bindings, native subtitle grouping, invalid timings, missing telemetry, warm/CPU speedup exclusion, notebook compilation and per-invocation log parsing.
- Existing Studio and Lot C offline evidence verifiers still pass. Approved boss sources, universal registry/providers, English script/WAV/timing evidence, historical compositions/episodes, Kokoro, legacy Studio and complete-episode implementation remain unchanged.

[Machine-readable evidence and artifact hashes](performance-cinematic-evidence/validation.json). Reports retain the recorded render-source fingerprints; final log-offset/staging-preflight changes do not alter model geometry. No older local file is represented as a new T4 benchmark.

## Reproduce

Use the installed pinned Node 22, Blender 4.3.2, ffmpeg/ffprobe and Python environment:

```sh
python -m unittest discover -s remotion/studio -p 'test_*.py'
python -m unittest discover -s remotion/blender/tests
python -m unittest discover -s remotion/tests -p test_manifest_import.py
python -m unittest discover -s remotion/tests -p 'test_*narration.py'
python remotion/studio/verify_smoke.py
python remotion/blender/universal/lot_c_evidence.py --check
blender --background --factory-startup --python-exit-code 1 --python remotion/studio/direction_check.py -- work/direction-check.json
cd remotion
node --experimental-strip-types --test tests/*.test.mjs blender/tests/*.test.mjs studio/*.test.mjs
node --experimental-strip-types scripts/asset-audit.mjs --check
npx tsc --noEmit
npx tsc --noEmit -p atlas/universal/tsconfig.json
npx tsc --noEmit -p studio/tsconfig.json
```

The new scripts use the Python standard library and existing renderer/Remotion dependencies; prepared-pilot use does not download or resynthesize Kokoro.

## Not executed / do not infer

No actual Colab/T4/CUDA/OptiX benchmark, mounted Drive latency/quota test, GPU OOM test, physical Android check, complete directed scene animation or 2672-frame directed episode export was executed. Telemetry with no NVIDIA device reports null, not zero utilization. User observations of the successful original episode are not this branch's benchmark results.

Some profiler phases necessarily overlap: PNG encoding/write, Cycles/denoising/compositing and browser composition/encoding are labeled accordingly. Cycles progress parsing is approximate. No exclusive GPU-kernel or remote-server durability timing is claimed. The cold 30–60-frame T4 matrix, visual noise/flicker comparison and full audio export measurement are still required before selecting an optimized configuration or recommending a full rerender.

The cinematic treatment is a prototype: all 19 shots need user art/motion review, especially Guardian teleportation, portal staging, Oracle timing, shield effects and cuts. Native word times and scene durations are exact; artistic pacing within those durations remains reviewable. Models themselves are not redesigned or reapproved by this PR.

No GitHub Actions were invoked or required, no PR #17 commits were integrated, and no PR was merged. Existing successful output folders must remain on their saved source commit; the new benchmark and directed edition use separate folders.
