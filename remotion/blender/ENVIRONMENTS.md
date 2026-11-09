# 0.8.2 — Cinematic Voxel Environments

## Scope and provenance

**Riis — Before the Whirlwind is an artistic reconstruction.** Terraces, architecture, streets, mountain shapes, geography, materials and lighting are procedural design choices, not a sourced claim about the exact appearance of Riis. The input retains its Atlas variant, reconstruction status and documentary source IDs (`wiki-riis`, `wiki-eliksni-civilian`). These sources establish context; they do not authenticate this invented city design. No copyrighted textures, ripped models or external visual assets are used.

This extends the existing Blender Bridge, not the Remotion renderer. Six existing Eliksni rigs, poses, joints, source coordinates and camera transforms are kept byte-for-byte in the snapshot data. Remotion, the mobile editor, Kokoro, aligned words, historical episodes and the original 0.8.1 example remain unchanged. No Blender video animation, audio, automatic compositing or additional planets are implemented.

## Generate and render one image

From repository root, Python 3.11+ and a Cycles-enabled Blender:

```sh
python remotion/blender/environments/riis.py \
  remotion/blender/examples/riis-frame-210.json \
  remotion/out/riis-cinematic.json --detail cinematic --seed 42 --lighting dawn
python remotion/blender/render_one.py \
  remotion/out/riis-cinematic.json remotion/out/riis-cinematic.png \
  --device cpu --scale 25 --threads 2 --timeout 600
```

`--scale 100` targets 1080×1920; 25 targets 270×480. An existing output PNG is refused to prevent stale benchmark evidence. Use a fresh path. `--device auto` checks Cycles backends (OPTIX, CUDA, HIP, ONEAPI, METAL), selects a supported GPU, otherwise CPU. A GPU render error allows one CPU retry within the **same overall timeout**. No automatic CPU retry loop.

The committed `examples/riis-before-whirlwind.json` is Balanced, seed 42, dawn, generated from the original frame 210. Generation is pure stdlib Python; Blender is only needed to import/render. Keep the input hash/source metadata for provenance. The input project hash identifies the source Studio project, not the decorated output; hash the output separately when archiving it.

## Reusable foundation

`environments/riis.py` is a deterministic snapshot decorator. Its reusable tower builder combines base plinth, stepped floors, terraces, slit windows, entrance lintels, angled ribs, crowns and spires. Separate modules construct platforms, stairs, walkways, bridge rails, street inlays, lamps, stepped valley banks and distant mountains. The central pedestrian strip remains at actor ground level y=0. Foreground pylons and paving, midground inhabited districts and a distant civic monument/mountains create depth in the original vertical camera.

Generation uses a private seeded `random.Random` instance, fixed iteration order and explicit dimensions. There is no wall-clock simulation, network input or global random state. Identical input/seed/options produce identical JSON; hardware, Blender versions and CPU/GPU floating point may still prevent bit-identical rendered pixels.

Only the legacy `ground` and `environment-*` stage meshes are replaced. Their exact IDs are recorded in `environment.replacedMeshIds`; all other meshes and every actor are preserved. Oversized scenes fail validation at 4096 meshes rather than dropping geometry. Non-Riis / non-before-whirlwind input and already-decorated snapshots are refused. Regenerate from the original input to change quality or seed.

### Quality budgets

Counts below describe the six-actor reference example; they are not crowd recommendations.

| Detail | Snapshot meshes | District rows per side | Tower floors | Mountains per layer | Windows | Cycles samples / bounces | Atmosphere |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| draft | 392 | 2 | 2 | 5 | no | 8 / 2 | tinted distant geometry |
| balanced | 693 | 3 | 3 | 8 | yes | 32 / 3 | tinted distant geometry |
| cinematic | 912 | 4 | 4 | 12 | yes | 96 / 5 | tinted geometry + bounded volume, density .008 |

All geometry is boxes with shared unit meshes; actor shapes keep existing spheres where needed. Affine/sheared transforms are preserved through mesh copies when Blender object LRS cannot represent them; geometry counts therefore do not imply a single Blender datablock. The cinematic volume is one bounded homogeneous box behind the plaza, not a volumetric weather simulation. It increases CPU time substantially; draft/balanced omit it.

Materials share a controlled blue-grey/bronze palette, roughness .35–1 and warm/cyan emissive accents. Environment emission strength is 3; legacy emission stays 1. Two SUN lights create warm dawn highlights and cool fill, or a blue-hour preset. AgX is selected when available, with Standard fallback reported. OIDN is optional: unsupported builds disable it explicitly. Existing snapshots without environment metadata retain their previous materials, Standard view transform and legacy 16/64-sample settings.

## Contract extension

Still `format: destiny-blender-scene`, `version: 1`, right-handed Y-up / column-major. `exporterVersion` accepts both `0.8.1` and `0.8.2`. New **optional** strict field:

```json
{"environment":{"generator":"riis-before-whirlwind","version":1,"detail":"balanced","seed":42,"lighting":"dawn","hazeDensity":0,"replacedMeshIds":["ground"],"visualStatus":"artistic-reconstruction"}}
```

`seed`: integer 0–2147483647, haze: finite 0–.02, detail: draft/balanced/cinematic, lighting: dawn/blue-hour. Unknown fields, invalid materials/transforms, bad references and size overruns are errors. The material and geometry contracts themselves are unchanged. Optional environment metadata controls import-time render settings; frozen meshes carry all geometry. The old importer CLI `--profile` remains an explicit legacy sample/bounce override; the new render helper and notebook deliberately omit it for environment snapshots.

The importer does not regenerate a city from metadata: changing only `detail` in an already-exported JSON does not rebuild meshes. Use the generator/form instead. Original omission notes are retained as source provenance; the appended reconstruction/replacement notes describe the new stage. Inherited omitted equipment/weather/Remotion elements remain omitted.

## Mobile Colab Pro procedure

Open [Blender-Colab-Pro.ipynb](Blender-Colab-Pro.ipynb). Before merge choose REF `feat/cinematic-voxel-environments-0.8.2`; after merge use `main`. Execute setup and resource cells. Then choose `riis-082`, detail, lighting, seed, resolution percentage, device and deadline. Start at Balanced/25%/600s. Exactly one PNG is rendered; the fixed showcase remains frame 210. FRAME only selects a frame when importing a Studio project.

Logs stream as Blender emits them. A heartbeat prints every 15 seconds even when Blender is quiet. The deadline (10–7200s in the form) kills the Blender process group. Successful runs show the effective backend, device names, wall time, PNG bytes and Blender RSS. Failed runs keep `.log` and `.benchmark.json`; execute the download cell to save them before restarting. Do not repeatedly retry unchanged failures. A new run directory prevents stale results. Keep a clean checkout and restart the runtime when switching source revisions to avoid Python import caches.

### Honest GPU benchmark

The user reports the **0.8.1** bridge validated remotely on Tesla T4/CUDA at 1080×1920. That is context, not a newly measured 0.8.2 result. To benchmark 0.8.2 on Colab:

1. Record checkout commit, Blender version, GPU name/VRAM and visible CPU count.
2. Render the same seed/detail/lighting/scale JSON once with `cpu`, then once with `auto`, using fresh run folders and sufficient deadlines. Avoid running both concurrently.
3. Verify `configuration.selected == GPU` and inspect `backend/devices`; `nvidia-smi` availability alone proves nothing about Cycles selection.
4. Compare `.benchmark.json` wall time and PNG bytes, image dimensions, `.report.json` samples/bounces, denoise, Blender maximum RSS and fallback notes. Archive snapshots/logs/reports/PNGs together. GPU/driver memory is **not** included in Blender RSS; record VRAM separately if measured.
5. If only CPU is selected, report a CPU result. Do not label a fallback render as a GPU benchmark.

No remote Colab 0.8.2, GPU or Android physical validation is claimed by this implementation session.

## Validation and resume

See [ENVIRONMENTS-REPORT.md](ENVIRONMENTS-REPORT.md) for actual measurements and skipped checks; [progress journal](../../docs/CINEMATIC-ENVIRONMENTS-PROGRESS.md) for checkpoint/restart commands. No full video or broad Chromium suite is needed for this Python/notebook-only rendering change.
