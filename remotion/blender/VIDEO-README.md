# 0.8.4 — Persistent Blender-to-Video pipeline

The minimal integration replaces a **voxel image layer only**, using an optional external sequence manifest passed to HybridShort. Existing episode schemas, Kokoro, captions, source labels, audio tracks and transition code remain authoritative. No episode migration is required. The original PNG notebook and snapshot importer are unchanged. Riis architecture is an artistic reconstruction, not canonical geography.

## 3-second preview

From repository root with Node 22, Blender/Cycles and existing npm dependencies:

Recommended narration command, from `remotion/`:

```sh
python scripts/narration.py episodes/hybrid_riis_07.json
```

Then from the repository root:

```sh
python remotion/blender/sequence.py remotion/out/hybrid_riis_07-ready.json \
  /persistent/path/blender-video-cache --start 120 --count 90 \
  --detail draft --scale 10 --device auto --timeout 180 --max-new 2
# Inspect two frames first; repeat without the work limit to complete the same job.
python remotion/blender/sequence.py remotion/out/hybrid_riis_07-ready.json \
  /persistent/path/blender-video-cache --start 120 --count 90 \
  --detail draft --scale 10 --device auto --timeout 180
```

The command prints the content-addressed job folder. A complete job writes `remotion-sequences.json` and copies PNGs into the ignored `remotion/public/assets/blender-video/<key>/` folder. Incomplete jobs do not publish a ready manifest. From `remotion/`:

```sh
node --experimental-strip-types scripts/episode.mjs render out/hybrid_riis_07-ready.json \
  --frames=120-209 --scale=0.1 --blender-sequences=/persistent/path/blender-video-cache/KEY/remotion-sequences.json
```

This is exactly 90 frames / 3 seconds, H.264 with existing narration/AAC. Output suffix `-blender.mp4` prevents overwriting the original episode video. Do not omit `--frames` for this demonstration: it would render the full episode with ordinary Remotion visuals outside the substituted range. No automatic sequence length reduction or duplicated still-frame interpolation is used. Each PNG comes from the v0.7 rig/camera engine at its original global frame.

The extract preserves the original 4–7 second narration window; its ending may cut a continuing phrase. It is an integration excerpt, not a newly authored standalone narration. No speech, caption timestamp or fact is retimed. Existing transitions remain tied to scene boundaries, not to arbitrary cache-range boundaries.

## Quality and safety

Draft/Balanced/Cinematic reuse the unchanged 0.8.2 environment builder, including its materials, dawn/blue-hour lights and quality-specific atmosphere (cinematic volume, cheaper geometry-only depth in lower profiles). Scale accepts 10/25/50/100%. Draft/10% is intentionally tiny. Selecting 100% requires a complete matching lower-resolution sequence in the same cache with the same source snapshots, renderer version, device and threads. It never starts automatically. Match the desired final detail in the preview first; a Draft preview does not authorize a Cinematic Full HD job. No new GPU performance claim is made.

## Cache, progress and interruptions

Cache key includes all 90 evaluated snapshots (therefore source project, scene, poses, camera, quality, environment seed and lighting), importer/validator/environment/runner code hashes, Blender version, scale, requested device and threads. Every completed PNG has an atomic `.done.json` recording source hash, PNG SHA-256 and effective render configuration. Truncated, modified or incomplete outputs are never accepted as hits. A changed input produces another folder; old results are retained. Completion is committed only after a valid PNG is produced. A crash during public-folder copying is repaired by rerunning the same command.

Persistent mode starts one Blender process per invocation, builds Riis once, retains Cycles persistent data, and updates camera and mesh transforms for each missing frame. Static materials, lights, atmosphere and geometry remain allocated. Affine shear is rebaked from original unit vertices, avoiding accumulated deformation. A static scene change rejects the batch and can use the single-frame fallback. `--renderer single` explicitly selects the original process-per-frame path.

Live Blender logs and a heartbeat are provided per batch (`batch-*.log`), with a timeout between validated frame completions that kills the process group. Initial scene construction counts toward the first frame timeout. `--no-fallback` stops on a batch failure; otherwise unfinished frames get one bounded single-frame attempt. A GPU render RuntimeError gets one CPU retry inside Blender. Device loss that terminates Blender is handled by the controller fallback. Completed frames survive failures; retrying a run rebuilds once and skips all valid cached frames. The controller prints total count, cache hits, completed frames and a rough remaining-time estimate based on newly rendered frames (not a guarantee). Each frame has benchmark JSON, Blender report and snapshot; single-frame mode also has individual logs; the job has identity and sequence reports. An exception stops the job and records its error; existing completed frames survive. Run one controller per cache job at a time; concurrent writes to the same folder are not supported.

**Persistence requires persistent storage.** `/content` and the local filesystem disappear when Colab deletes a runtime. Mount Drive in the new [sequence notebook](Blender-Video-Colab-Pro.ipynb), keep the same cache path and saved ready project/narration, or download the whole cache folder and restore it manually. The notebook copies completed frames back into the fresh Remotion public folder on resume. A changed Blender/package version may intentionally invalidate caches. Preserve the exact Git revision for reproducible continuation. Hardware/driver changes with the same requested `auto` device are not included in the key; inspect per-frame reports for mixed CPU/GPU execution. Bit-identical pixels across devices are not guaranteed.

## Manifest

Version 1 sidecar: `{version:1,fps:30,projectId,clips:[{startFrame,width,height,frames:[relativePublicPngPaths]}]}`. Each clip has at most 90 paths. Validation rejects mismatched project IDs, overlapping ranges, non-voxel frames, invalid dimensions/FPS and unsafe paths. CLI preflights file presence before rendering; missing or unreadable images also fail through Remotion. Outside clips the original voxel renderer remains active. The sidecar is an explicit render input; after editing a project regenerate it rather than manually reusing an old manifest with the same project ID.

## Colab / GPU

The new notebook restores or generates genuine Kokoro narration, accepts Draft/Balanced/Cinematic, scale, device, frame timeout and a work limit. It always renders source frames 120–209 only. `auto` tries CUDA first, then OptiX and other supported Cycles backends / one CPU fallback. Only devices belonging to the selected backend are enabled. Inspect `selected`, `backend`, `devices`, per-frame timings and RSS, not merely nvidia-smi. GPU/driver memory is not included in Blender RSS. `sequence-report.json` records optional `nvidia-smi` samples, peak observed device memory and mean utilization. These device-wide samples (at least 5s apart) can include other workloads and miss peaks; unavailable values are null. Per-frame reports record the effective selected device/backend/names after a successful render, including CPU retries. Per-frame persistent timings exclude scene setup; sequence wall time includes Blender startup/setup, rendering and writes but excludes snapshot preparation. Use the benchmark harness for total subprocess time. CPU and GPU comparison requires identical content/quality/scale and separate cache keys, with actual effective devices checked.

## Limits

Full 35-second renders, automatic mobile-editor asset management, optical flow and new environments remain outside this change. The command remains limited to 90 frames. Existing v0.8.3 cache folders are retained but renderer code hashes intentionally create new v0.8.4 keys; frames are never silently reused across renderer revisions. The notebook is structurally checked; a new remote Colab/GPU or physical Android run is not claimed. See [GPU-REPORT.md](GPU-REPORT.md) for measured CPU results and GPU limitations; [VIDEO-REPORT.md](VIDEO-REPORT.md) preserves the v0.8.3 record.

## Reproducible comparison on Colab T4

The notebook offers an opt-in benchmark cell (`RUN_BENCHMARK=False` by default). It runs **only 90-frame sequences**, sequentially, with isolated cold caches and no persistent-to-single fallback. It pins the v0.8.3 baseline commit and preserves ready narration/timestamps. On a fresh Colab runtime select T4, mount Drive, complete setup/narration cells, close other GPU workloads, then run the benchmark cell. Inspect every effective configuration; `nvidia-smi` alone does not establish Cycles GPU rendering.

CLI equivalent from repository root (install npm dependencies in both checkouts):

```sh
git worktree add --detach work/baseline-083 1effd88e089ef4726600a223f97de8fe9abafe78
npm ci --prefix work/baseline-083/remotion
python remotion/blender/benchmark.py remotion/out/hybrid_riis_07-ready.json \
  /persistent/path/fresh-benchmark-084 --baseline-root work/baseline-083 \
  --device auto --threads 2 --timeout 600
```

The default matrix is Draft/10%, Balanced/25%, Cinematic/50%, 90 frames / 30 FPS, source 120–209, seed 42 and dawn lighting. `--qualities draft` can limit a diagnostic run. Both versions use the same ready project, binary, hardware, threads and requested render options. The JSON records revisions, input checksum, exact commands, Blender/Node versions, CPU affinity, total wall time, average per frame, Blender peak RSS, optional GPU telemetry and decoded pixel comparisons (install Pillow). No warm-cache or partial run is accepted as a performance comparison. Only matching effective GPU backends/devices with 90 GPU-rendered frames are eligible for a GPU comparison. Baseline auto may choose OptiX while v0.8.4 prefers CUDA; that difference must be disclosed and is marked ineligible for a matched-backend GPU claim. Run multiple trials and alternate execution order manually before generalizing a result.

After any optimization or Colab validation run, encode the 3-second Remotion excerpt above, then verify it:

```sh
python remotion/blender/verify-video.py remotion/out/hybrid_riis_07-ready.json \
  CACHE_KEY_FOLDER remotion/out/hybrid-riis-07-blender.mp4 validation.json
```

On Android use the existing Colab forms and rerun sequence/compositing cells after reconnecting. Drive must retain the ready project, audio and the entire hashed cache. A completed-cache rerun republishes local PNGs for Remotion. Physical Android and remote Colab testing remain separate from notebook syntax checks. Do not begin a 35-second render before the optimized 3-second MP4 and synchronization checks pass on the target device.
