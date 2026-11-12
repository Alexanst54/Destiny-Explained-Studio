# Standalone Tesla T4 Optimization Lab

[Open the independent notebook in Colab](https://colab.research.google.com/github/Alexanst54/Destiny-Explained-Studio/blob/feat/atheon-performance-cinematic-direction/remotion/blender/Destiny-GPU-Optimization-Lab.ipynb).

This updates draft PR #26 without changing the production notebook. It never renders the full episode, mounts Drive by default, downloads voice models, installs npm/Remotion or modifies an existing project. Approved geometry, all 19 shot definitions, the six English narrations and native subtitle times remain unchanged.

## Evidence and current conclusion

The [user-provided M3 aggregate](gpu-lab-evidence/user-reported-m3.json) has 19 newly rendered frames and 11 cache hits, so it is not a cold benchmark. Cycles plus compositing account for about **97% of the 294.32-second invocation**. That supports investigating this operation before optimizing the much smaller PNG, checkpoint, build or update phases. It does not separate exclusive GPU kernels, CPU synchronization, transfers, denoising or compositing. Device-wide utilization is not CUDA occupancy; the sampling interval can miss short bursts. No speedup is inferred against the approximately 20-hour first episode.

A local probe of the actual Blender 4.3.2 approved builder confirms these defaults: **48 samples, OpenImageDenoise enabled, `denoising_use_gpu=False`, `compositor_device=CPU`, five maximum bounces, volume step rate 1**. These are concrete hypotheses to test on the T4, not proof that CPU denoising/compositing explains all 285.40 seconds. The lab captures the target runtime's actual settings and device inventory.

**Current production recommendation: retain existing Balanced / 48 settings until repeated cold T4 measurements and visual review support a change.** No new T4 benchmark was available in development; no speedup, optimized preset or under-six-hour completion is claimed. O4 is intentionally conditional on real evidence.

## Exact Android workflow

1. Open the notebook, select **Runtime → Change runtime type → T4 GPU**. Start a fresh runtime. No local PC or terminal is required.
2. **O1:** keep `benchmark_mode=fast`, `resolution=540×960`, and choose a NEW simple `run_id`, such as `t4-fast-01`. Run the cell. It clones the PR #26 branch using a sparse/partial checkout, installs SHA-verified official Blender 4.3.2 and ensures ffmpeg/ffprobe. It saves the fixed plan and displays disk usage and source commit. It renders no images. No Drive mount occurs.
3. **O2:** enable `run_t4_optimization_benchmark` and run. The lab validates a physical T4 / OptiX or CUDA device and tests GPU features with tiny renders. The six cases then run sequentially on identical source frames. It builds the HTML/JSON comparison, ZIP, and safely removes disposable intermediates only after successful report/archive generation. Failures keep local intermediate caches for resume.
4. **O3:** select a case, shot, trial and source-frame index. Inspect the side-by-side image, difference map, timings, PSNR/SSIM, actual GPU backend, power/VRAM, failures and projections. The default download control sends **one ZIP** containing the complete offline HTML, JSON, comparison images and raw logs. Unzip and open `final/index.html` for the full gallery; the notebook displays selected images to avoid flooding mobile memory.
5. If a candidate looks useful, rerun **O1 with a NEW run ID and `standard` mode**, then O2/O3. Standard uses three consecutive source frames per shot and two trials in reversed order. Review metallic detail, Vex glow, portals, volumetrics, shadows, noise and frame-to-frame artifacts. A high SSIM is not artistic approval.
6. **O4, optional:** choose the measured candidate, enable both approval/export checkboxes, and run only after visual and timing review. It requires repeated cold T4 evidence, no fallback/failure, matching source/frame/geometry/light identities, temporal comparisons, a median gain of at least 5% and each trial above 2%. These thresholds are conservative review gates, not a statistical confidence claim. It downloads a **JSON settings recipe for a NEW cinematic project**. It does not change the production notebook, apply settings automatically, open episode folders or launch a render. Restored reports require their exact recorded source commit.

Fast mode renders **18 frames total**: three shots × six configurations × one frame/trial. Unsupported configurations are skipped with reasons. Fast mode does not validate flicker or authorize O4. Standard renders **108 frames total**: three shots × three consecutive frames × six configurations × two trials. CPU and partial/warm cases never produce a T4 speedup. A completed original cold trial can be reused after frame validation as archived evidence; it is explicitly labeled, not timed again as new work.

Fast cases have a five-minute timeout and standard cases fifteen minutes; feature probes have separate short bounds. Timeouts and failures are preserved rather than retried on CPU. There is no concurrent Blender worker mode or full-episode action.

## What is held constant

The three sampled cinematic shots are `01-hook/vault-establish` (complex environment/volumetrics), `04-time/past-gate` (portal/temporal effects), and `02-identity/mechanism` (Atheon metallic close-up). The same exact frame/pose, camera matrix, resolution, seed 42, LOD0, scene construction, lighting, material state, volumes, bounce limits, adaptive threshold, shadows and source code are used for each case. Per-frame scene signatures must match the baseline.

The lab reuses `universal.worker.build/update`, the approved Venus/Vault builder and `cinematic_direction.install/apply`. It does not copy the episode-production pipeline or regenerate narration. Geometry/materials persist across compatible shot updates inside each case. These mechanisms were already present; scene reuse is not claimed as a newly measured fix for the large render-operation time.

| Configuration | Explicit differences from approved Balanced baseline |
| --- | --- |
| `baseline-48` | 48 samples, existing denoiser/compositor defaults |
| `samples-32` | 32 samples with denoising |
| `samples-24` | 24 samples with denoising |
| `alternate-denoiser-48` | 48 samples with the alternative supported denoiser (normally OptiX versus OpenImageDenoise) |
| `candidate-48` | 48 samples; supported GPU denoising/compositor scheduling and auto-tiling experiment |
| `candidate-32` | Same supported candidate settings, 32 samples |

Candidate GPU denoising preserves OIDN HIGH quality / accurate guiding passes. The OIDN GPU checkbox is distinct from selecting the OptiX denoiser, which intrinsically uses a supported NVIDIA GPU. Candidate GPU compositing requests FULL precision and preserves the existing glow graph. Candidates do not alter volume step/density, bounces, threshold, lighting or artistic effects. If GPU denoising/compositing is unsupported or logs a CPU fallback during its tiny probe, that feature is not used. At most the supported auto-tiling experiment remains; a non-improving technique is not exported or enabled in production.

The available RNA property alone is not enough: actual hardware capability methods and a successful 32×32 render probe are required for OptiX denoising, OIDN GPU and GPU compositing. The probe checks operational compatibility, not an exclusive GPU-kernel trace. Actual full-resolution case failures/OOM are recorded. GPU-only selection is identical across all comparisons; CPU and duplicate backend preference entries are disabled and inventoried. Duplicate preference entries in the original configuration do not by themselves prove duplicate rendering, because Cycles filters by selected compute backend. No original GPU misconfiguration is assumed.

## Measurements and comparisons

Each case has fresh frame caches and one Blender process. Cold frame caches do **not** imply an empty global driver/compiler cache; feature probes run before trials. Standard reverses case order to reduce order/thermal bias. The report retains first-frame and per-frame records so kernel loading or synchronization outliers can be inspected.

JSON and HTML record invocation wall time, build wall/CPU time, per-frame update/render-compositor/PNG/verification wall time, actual settings/backend/device inventory, sampled CPU utilization and RSS, GPU utilization/power/VRAM, cache hits/new frames, cold/warm state and failures. GPU telemetry is device-wide at approximately 500 ms; it can miss shorter bursts or include other processes. CPU utilization uses one core = 100% and can exceed 100%. Runnable scheduler wait is summed across observed threads, not the duration of blocking on GPU or I/O.

Raw Blender progress clocks provide approximate scene-sync/BVH/kernel-load, sampling, denoising and compositor phases where printed. These may overlap or reset and are not exclusive CUDA timings. GPU transfer and kernel durations remain null without an external kernel tracer. The report never calculates GPU time as wall minus multithreaded CPU time.

Paired comparisons provide baseline-left/candidate-right PNGs, RGB PSNR/SSIM, ×4 difference maps and consecutive-frame residual-change measurements in standard mode. Baseline 48-sample images are not noiseless ground truth. Temporal residuals can contain motion/noise errors and do not establish flicker-free output. Final acceptance remains a human artistic review.

Render projections are emitted only from comparable cold T4 trials with matching GPU UUID/backend and scene signatures. They extrapolate **Cycles+compositor operation time only** from three representative shots to 2672 frames, showing a broad shot-rate envelope. It is not a confidence interval or an estimate of complete production. Remaining shots and Templar complexity, PNGs, updates, Drive checkpointing, Kokoro, Remotion/audio composition and export are not measured here. Complete-production duration stays unknown; no six-hour promise is made.

## Storage, reset and optional Drive

All code/tools, intermediates, caches and logs live under `/content/destiny-gpu-lab/`. No per-frame Drive copying occurs. ZIPs retain final paired/difference images, not the individual raw frame cache. Marked per-run `intermediate/` trees are the only directories eligible for automatic cleanup; symlinks, mounts, outside paths and episode-project ancestors are refused. Final comparisons, reports, raw logs and the ZIP remain. CPU-only validation can use a dedicated local test root; it cannot authorize GPU recommendations.

If disconnected while the runtime still exists, rerun with unchanged source/settings/run ID to validate/reuse local frames. If the runtime resets, `/content` disappears. Download the ZIP before reset; restoring a result ZIP restores reviewable reports/images, not deleted frame caches or a completed episode.

The last notebook cell is **optional and disabled by default**. It mounts Drive only after explicit selection and saves only a uniquely named final ZIP under `MyDrive/Destiny-GPU-Lab-Reports`. It refuses overwriting existing ZIPs. An explicitly chosen lab ZIP can be restored into a NEW local report directory after path, size, symlink and checksum validation. It never browses or touches existing episode folders. The ordinary O3 download workflow requires no Drive at all.

## Validation and limitations

[Local component validation and CPU-only example](GPU-OPTIMIZATION-LAB-VALIDATION.md). The complete sparse-clone path was tested: approximately 3.7 MiB, no narration WAVs and no npm dependencies. The actual Colab install/T4, GPU denoising/compositor probes, physical Android workflow, full six-configuration matrix and standard temporal T4 runs remain to be executed on target hardware. The supplied warm M3 numbers are acknowledged as user evidence, not relabeled as this lab's cold benchmark.

No PR merge, PR #17 integration or GitHub Actions invocation is part of this workflow.
