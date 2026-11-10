# Oryx — The Taken King — Lot C prototype

**Partial dedicated prototype, awaiting visual review. Not user-approved or artistically complete.**

Winged Hive silhouette, horizontal crown, three eyes, talons, torn voxel membranes and an editorial campaign-inspired sword.

Atlas ID `boss-oryx` → `arena-threshold`. A void-facing Threshold reconstruction with a central approach, four ritual plates, Hive ribs and terminal fins.

[Identity, sources and reconstruction boundaries](../ART-DIRECTION.md) · [Reference URLs and hashes](../references.json) · [Actual render manifest](evidence.json)

| View | Actual Blender PNG |
| --- | --- |
| Front | ![Oryx — The Taken King — Front](front.png) |
| Profile — 90° | ![Oryx — The Taken King — Profile — 90°](profile.png) |
| Three-quarter — 45° | ![Oryx — The Taken King — Three-quarter — 45°](three-quarter.png) |
| Full-body cinematic low angle | ![Oryx — The Taken King — Full-body cinematic low angle](cinematic.png) |
| Arena wide | ![Oryx — The Taken King — Arena wide](environment.png) |

## Animated signature clip

[Actual H.264 animation](animation.mp4) — **36 rendered frames, 24 FPS, 1.5 seconds, 480×360, Balanced, LOD 0**, no audio.

![oryx frame 0](animation-0000.png) ![oryx frame 12](animation-0012.png) ![oryx frame 24](animation-0024.png) ![oryx frame 35](animation-0035.png)

Ritual arm/claw gestures, chest light and wing hinges; movement is bounded hovering.

All five controls are available: `idle`, `move`, `combat`, `signature`, `reveal`. They are deterministic functions of frame/FPS and articulate multiple joints; this is not a whole-model turntable.

## Technical settings and measured CPU results

Blender official 4.3.2 (32f5fdce0a0a), Cycles/AgX/OpenImageDenoise, seed 42. Stills use Cinematic (128 samples maximum), clips Balanced (48 maximum); adaptive sampling may stop earlier. Every delivered scene uses **explicit LOD 0**, independent of resolution. The arena view is 960×540; anatomical/cinematic dimensions are recorded below.

| Output | Pixels / frames | Actual render sum | Average / frame | Process peak RSS | Report |
| --- | --- | --- | --- | --- | --- |
| front | 768×576 / 1 | 40.91 s | 40.91 s | 754.3 MiB | [JSON](front-report.json) |
| profile | 768×576 / 1 | 23.55 s | 23.55 s | 755.5 MiB | [JSON](profile-report.json) |
| three-quarter | 768×576 / 1 | 38.47 s | 38.47 s | 759.7 MiB | [JSON](three-quarter-report.json) |
| cinematic | 768×576 / 1 | 114.78 s | 114.78 s | 769.1 MiB | [JSON](cinematic-report.json) |
| environment | 960×540 / 1 | 92.34 s | 92.34 s | 816.3 MiB | [JSON](environment-report.json) |
| animation | 480×360 / 36 | 977.29 s | 27.15 s | 578.3 MiB | [JSON](animation-report.json) |

| Explicit LOD | Boss pieces | Joints | Environment pieces |
| --- | --- | --- | --- |
| 0 | 5794 | 23 | 684 |
| 1 | 1816 | 23 | 366 |
| 2 | 590 | 23 | 183 |

Each report records real device/backend, thread setting, lighting/atmosphere, camera matrix/lens/sensor, render-source hashes, geometry and per-frame pose digests. PNGs are direct Blender outputs; no retouch, generated placeholder or interpolated video frame is substituted. The MP4 is encoded from those real frames.

Native checks: **240 pose evaluations**, five view bounds, **36 clip-frame projections**, zero measured framing overflow, stable objects/meshes and random access. **Physical foot contact is not validated.**

## Remaining limitations

Wing membranes are rigid stepped panels, not cloth simulation. The sword is a carried editorial campaign-inspired choice; no sword-free raid form or Shade projection is implemented.

All local runs selected **CPU**, with three rendering threads configured. CPU contention may affect durations; these are not controlled comparative benchmarks. RSS is process memory, not VRAM. GPU/Tesla T4/Colab Pro/Android and actual GPU failure recovery remain untested. No full-length episode, narration or historical Remotion behavior is changed.

See the [Lot C reproduction/Colab guide](../README.md). Source generations and textures are entirely procedural; reference images were observed, never imported as assets.
