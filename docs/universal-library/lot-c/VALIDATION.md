# Lot C validation

All three models are **partial dedicated prototypes pending artistic review**. This report separates technical checks from artistic approval; the universal library is incomplete.

## Local checks

- Python Blender suite: 52 tests passed, followed by four additional evidence-rejection tests; manifest import suite: four passed.
- Node: all 105 Remotion tests and all seven Blender export/sequence tests passed (112 total). The earlier selected legacy/library run also passed 106 tests.
- TypeScript: both `remotion/tsconfig.json` and `remotion/atlas/universal/tsconfig.json` passed with Node 22.23.4 / TypeScript 5.5.4.
- Blender 4.3.2 native: 240 LOD0 poses per new boss (720 total), five camera-bound checks each, 36 clip projections each (108 total), LOD1/2 construction and five modes at each lower LOD. Stable scene resources, deterministic random access and articulated motion passed. No measured framing overflow. [Native results](native-checks.json).
- Existing mobile gallery browser check: all 300 entities, Atlas filters/variants, approved image decoding, JSON download and narrow-screen layout passed. New three-boss media browser checks await the remaining galleries.
- Existing Vex, Venus/Vault and Cropta native checks: 136 + 156 + 192 evaluations passed. All prior evidence verifiers passed. [Preservation baseline](preservation.json): 121 protected files and eight original registry bindings unchanged.
- Four independent Rhulk Draft CPU frames also have identical decoded RGB, including the frame regenerated after deliberate corruption. [Determinism proof](regressions/rhulk-determinism.json).
- Cropta repeat CPU render: identical decoded RGB to original Cinematic front image, zero differing channel samples. PNG file bytes differ because Blender writes render-time metadata. [Comparison proof](regressions/evidence.json).
- Actual Rhulk Blender-worker crash/resume: one valid frame preserved, three new frames after resume, four warm cache hits. Corrupting one PNG caused exactly one new render and preserved the other three. Changed seed rejected without altering the existing manifest. [Recovery result](recovery.json).

## Actual media

Each gallery publishes only successful real Blender render outputs, after PNG CRC/decode/SHA checks and source/identity/camera/pose validation. Video verification requires H.264/yuv420p, 36 frames, 24 FPS, 480×360, 1.5 seconds and at least 33 distinct decoded frames. The [evidence index](evidence.json) reports any still-missing collection explicitly. Oryx and Rhulk galleries are complete and verified; Nezarec evidence collection remains in progress at this checkpoint.

No physical foot-contact IK, collision/damage, fluid/cloth or full encounter-mechanics validation is claimed. Arena dimensions and added set dressing are artistic reconstruction. Oryx's carried campaign-inspired sword is an editorial choice in the raid setting; no sword-free form or Shade implementation is claimed. See [art direction](ART-DIRECTION.md).

## GitHub Actions

PR [#24](https://github.com/Alexanst54/Destiny-Explained-Studio/pull/24), stacked on PR #23, remains a draft with no auto-merge. The [registry-and-evidence check](https://github.com/Alexanst54/Destiny-Explained-Studio/actions/runs/42676063850/job/129357635844) did **not start**. GitHub's annotation says: “The job was not started because your account is locked due to a billing issue.” This is an external CI limitation, not a passing workflow; no billing change was attempted. GitGuardian passed at this checkpoint. Local equivalents run independently.

## CPU / Colab limits and backlog

CPU AMD EPYC 9V74, three configured render threads, Blender 4.3.2 / Cycles / OIDN / AgX. All delivered jobs use seed 42 and explicit LOD0. Cinematic max samples 128, Balanced max 48; adaptive sampling may stop earlier. Per-job reports carry actual device/backend, source hashes, render seconds and peak process RSS. RSS is not VRAM, durations are not controlled speedup benchmarks, and no GPU performance improvement is claimed.

GPU/Tesla T4, Colab Pro, Android, real GPU OOM recovery and full-length episode export remain untested. Use the [Colab instructions](README.md#colab--tesla-t4) and [additional notebook](../../../remotion/blender/Lot-C-Colab-Pro.ipynb), begin with a single frame, inspect actual selected backend/device, then test a short clip and unchanged-source resume. No PR #17 code was integrated. Historical episodes, narration, Kokoro and Remotion behavior remain unchanged.

Remaining backlog: 122 boss entries plus 25 independent forms (147 entries, not individuals), including the Witness, Riven, Taniks/forms, Aksis, Calus, Atraks-1, Golgoroth, Gahlran, Insurrection Prime, dungeon-specific models and encounter arenas. Savathûn needs a sourced Atlas entry before binding. No fallback model fills these gaps.
