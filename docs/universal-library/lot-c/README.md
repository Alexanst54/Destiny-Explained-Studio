# Lot C — Oryx, Rhulk and Nezarec

Three separate procedural Blender **prototypes awaiting visual review**, based on PR #23 at `2baffff`. The universal library is not complete. No generic model substitution, proprietary model/texture imports, PR #17 integration or automatic merge.

[Research and reconstruction boundaries](ART-DIRECTION.md) · [Oryx](oryx/README.md) · [Rhulk](rhulk/README.md) · [Nezarec](nezarec/README.md) · [Validation](VALIDATION.md)

The providers have independent authored anatomy, rigs, palettes, weapons, scene styles and arenas. Shared helpers are voxel primitives (shells, beams, tapered pieces), not a shared renamed boss body. The Atlas identities and existing encounter links are retained. `arena-threshold` is Oryx's arena; Rhulk and Nezarec retain their broader `vow-of-disciple` and `root-of-nightmares` location IDs, with clearly documented original final-platform reconstructions. Oryx's Shade remains unimplemented.

## Reproduce the review renders

Official Blender 4.3.2 with Cycles/OpenImageDenoise, Python 3.12, ffmpeg/ffprobe. From the repository root:

```sh
python remotion/blender/universal/lot_c_render.py work/lot-c-review --plan-only
python remotion/blender/universal/lot_c_render.py work/lot-c-review --blender /path/to/blender
# A single boss, stills or clips only:
python remotion/blender/universal/lot_c_render.py work/oryx-review --boss oryx --phase clips --blender /path/to/blender
# Resume the same code and parameters after interruption:
python remotion/blender/universal/lot_c_render.py work/lot-c-review --resume --blender /path/to/blender
```

`lot_c_shots.json` fixes seed 42, **LOD0**, five Cinematic views per model (front, true 90° profile, true 45° three-quarter, full-body low angle, arena wide), and a 36-frame Balanced clip at 24 FPS. Cinematic and Balanced cap samples at 128 and 48; adaptive sampling may stop earlier. Resolution never selects a lower LOD. Each invocation keeps Blender and static meshes/materials alive through its frame sequence. All frame checkpoints use the existing atomic, CRC/decode/SHA-bound cache. Source/configuration changes require a new output directory; cache reuse across different code revisions is deliberately rejected.

Individual selections use the existing opt-in CLI:

```sh
python remotion/blender/render_universal.py boss-oryx work/oryx-front --view front --width 768 --height 576 --quality cinematic --lod 0
python remotion/blender/render_universal.py boss-rhulk work/rhulk-kick --view cinematic --animation combat --width 480 --height 360 --quality balanced --lod 0 --frames 36 --fps 24 --video
python remotion/blender/render_universal.py boss-nezarec work/nezarec-profile --view profile --width 640 --height 640 --quality cinematic --lod 0
python remotion/blender/render_universal.py arena-threshold work/threshold-only --quality balanced --lod 0
```

Add `--blender /path/to/blender`. Existing Athéon/Templar/Cropta controls and their render contracts are unchanged. New `profile`/`cinematic` views are rejected for providers which do not declare support, rather than silently aliasing another camera. The new scene-style and material hooks are optional; Cropta's default scene and all old evidence remain unchanged.

## Controls and limitations

Each new boss supports `idle`, `move`, `combat`, `signature`, `reveal`. Oryx hovers, flexes wings/claws and raises his arms for a ritual; Rhulk strides/dashes, extends a kick and manipulates resonance; Nezarec lunges, sweeps the scythe and performs a jump/slam-like Light/Dark gesture. Limbs, weapons and secondary structures articulate independently. Poses are direct functions of time, with no accumulated simulation state.

These are choreographed prototypes: no physical mass, collision/damage, cloth, fluid, terrain-aware foot IK or complete raid-mechanics simulation. Ground contacts and foot sliding are not physically validated. The arenas evoke the final encounters, without claiming exact maps or canonical metre measurements. Oryx's optional sword is campaign-inspired and intentionally editorial in the raid setting. All three stay partial until visual review; successful tests do not declare artistic completion.

## Colab / Tesla T4

Use [Lot-C-Colab-Pro.ipynb](../../../remotion/blender/Lot-C-Colab-Pro.ipynb), select a T4 runtime if available, and begin with one Draft frame at LOD0. Check the actual `configuration.selected`, `backend` and `devices`; an `auto` request is not proof of GPU use. Then render a short Balanced clip, inspect framing/motion and ffprobe duration, and test `--resume` with unchanged source and settings. Save the output in Drive before the session ends. The scene is rebuilt after restarting Blender; the inter-session cache is a JSON design and rendered PNGs, not a saved `.blend`.

GPU memory/utilization fields remain null when not measured. Optional `nvidia-smi` output is a snapshot, not a claimed VRAM peak or speedup. Local evidence is CPU; Colab/T4/Android and actual GPU OOM recovery are not validated here. No full-length episode rendering or audio/narration changes.

## Verification

```sh
python -m unittest discover -s remotion/blender/tests
node --test remotion/tests/universal-library.test.mjs remotion/tests/lot-c.test.mjs
blender --background --factory-startup --python-exit-code 1 --python remotion/blender/universal/lot_c_check.py
python remotion/blender/universal/lot_c_evidence.py --check
python remotion/blender/universal/verify_crota.py
python remotion/blender/universal/approved_gallery.py --check
```

The shipped evidence includes actual device settings, camera matrices/lenses, source hashes, geometry/pose digests, durations and process peak RSS. The collector requires real successful Blender outputs before publishing previews. Existing evidence is checked against [preservation.json](preservation.json) and the prior verifiers, never rewritten to fit new geometry.
