# Nezarec — Final God of Pain — Lot C prototype

**Partial dedicated prototype, awaiting visual review. Not user-approved or artistically complete.**

Heavy red barrel torso, asymmetrical pale/black shoulders, horned narrow mask with seven authored purple eyes, back growths and a large crescent scythe.

Atlas ID `boss-nezarec` → `root-of-nightmares`. Broken Pyramid terraces cut by branching pale roots, with separated Light/Dark seed motifs.

[Identity, sources and reconstruction boundaries](../ART-DIRECTION.md) · [Reference URLs and hashes](../references.json) · [Actual render manifest](evidence.json)

| View | Actual Blender PNG |
| --- | --- |
| Front | ![Nezarec — Final God of Pain — Front](front.png) |
| Profile — 90° | ![Nezarec — Final God of Pain — Profile — 90°](profile.png) |
| Three-quarter — 45° | ![Nezarec — Final God of Pain — Three-quarter — 45°](three-quarter.png) |
| Full-body cinematic low angle | ![Nezarec — Final God of Pain — Full-body cinematic low angle](cinematic.png) |
| Arena wide | ![Nezarec — Final God of Pain — Arena wide](environment.png) |

## Animated combat clip

[Actual H.264 animation](animation.mp4) — **36 rendered frames, 24 FPS, 1.5 seconds, 480×360, Balanced, LOD 0**, no audio.

![nezarec frame 0](animation-0000.png) ![nezarec frame 12](animation-0012.png) ![nezarec frame 24](animation-0024.png) ![nezarec frame 35](animation-0035.png)

A scythe sweep/lunge moves torso, shoulder, elbow, fingers and weapon; the signature gesture adds a jump/slam-like rise and back-fan movement.

All five controls are available: `idle`, `move`, `combat`, `signature`, `reveal`. They are deterministic functions of frame/FPS and articulate multiple joints; this is not a whole-model turntable.

## Technical settings and measured CPU results

Blender official 4.3.2 (32f5fdce0a0a), Cycles/AgX/OpenImageDenoise, seed 42. Stills use Cinematic (128 samples maximum), clips Balanced (48 maximum); adaptive sampling may stop earlier. Every delivered scene uses **explicit LOD 0**, independent of resolution. The arena view is 960×540; anatomical/cinematic dimensions are recorded below.

| Output | Pixels / frames | Actual render sum | Average / frame | Process peak RSS | Report |
| --- | --- | --- | --- | --- | --- |
| front | 640×640 / 1 | 49.51 s | 49.51 s | 745.4 MiB | [JSON](front-report.json) |
| profile | 640×640 / 1 | 36.65 s | 36.65 s | 741.1 MiB | [JSON](profile-report.json) |
| three-quarter | 640×640 / 1 | 46.91 s | 46.91 s | 741.4 MiB | [JSON](three-quarter-report.json) |
| cinematic | 640×640 / 1 | 158.78 s | 158.78 s | 778.9 MiB | [JSON](cinematic-report.json) |
| environment | 960×540 / 1 | 164.24 s | 164.24 s | 870.8 MiB | [JSON](environment-report.json) |
| animation | 480×360 / 36 | 1342.34 s | 37.29 s | 630.1 MiB | [JSON](animation-report.json) |

| Explicit LOD | Boss pieces | Joints | Environment pieces |
| --- | --- | --- | --- |
| 0 | 6724 | 23 | 8149 |
| 1 | 2069 | 23 | 2869 |
| 2 | 715 | 23 | 995 |

Each report records real device/backend, thread setting, lighting/atmosphere, camera matrix/lens/sensor, render-source hashes, geometry and per-frame pose digests. PNGs are direct Blender outputs; no retouch, generated placeholder or interpolated video frame is substituted. The MP4 is encoded from those real frames.

Native checks: **240 pose evaluations**, five view bounds, **36 clip-frame projections**, zero measured framing overflow, stable objects/meshes and random access. **Physical foot contact is not validated.**

## Remaining limitations

Skin and root geometry use authored voxel shells; no muscle/cloth/fluid simulation. Eye placement and back structures are original interpretations. Fine eye detail is difficult to read at the full-body validation framing. Arena nodes are visual motifs, not a complete raid-mechanics simulator.

All local runs selected **CPU**, with three rendering threads configured. CPU contention may affect durations; these are not controlled comparative benchmarks. RSS is process memory, not VRAM. GPU/Tesla T4/Colab Pro/Android and actual GPU failure recovery remain untested. No full-length episode, narration or historical Remotion behavior is changed.

See the [Lot C reproduction/Colab guide](../README.md). Source generations and textures are entirely procedural; reference images were observed, never imported as assets.
