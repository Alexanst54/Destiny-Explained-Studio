# Who Is Atheon, Time's Conflux?

Destiny Explained — Episode 01. Language **en-US**, English narration/subtitles/titles/scene labels, vertical **1080×1920, 30 FPS**. The supplied six-scene script is preserved in [script-supplied.json](script-supplied.json); [script.json](script.json) is its lore-reviewed production version. [Lore review](LORE-REVIEW.md) documents two small corrections and the sources/uncertainties.

This requested directory is `episodes/atheon-explained-en/`. No pre-existing pilot directory or PR #26 was present to rename; the supplied PR link identifies **PR #25**, which is being updated. Historical episodes are untouched.

## Speech-first preparation

From the same Studio environment (or its Colab venv):

```sh
python remotion/studio/pilot.py episodes/atheon-explained-en/script.json /path/in/Drive/atheon-explained-en
```

This command synthesizes **audio only**, with the existing pinned Kokoro pipeline, English `af_heart`, speed 1×, and actual synthesis-token timestamps. It saves separate speech WAVs/word timings, a continuous `timing.json`, an English `subtitles.en.srt` generated from the same measured words, and six Studio selections. It does not invoke Blender, Remotion or video export. Each scene's duration is the actual speech duration plus a quarter-second tail, rounded up to a frame. No words are cut or accelerated. Target duration is checked, not forced.

The prepared selections retain approved Atheon and Glass Throne IDs. Optional title/scene-label props in the separate Studio composition display the exact English title on the first scene and English scene labels throughout. No historical Remotion entry or model is changed. French remains available in the general Studio alongside English; the pilot explicitly chooses English.

The notebook includes an opt-in **audio-only English pilot preparation** cell that writes this package to Google Drive. Run the Studio's existing small smoke-test before later scene production. Existing project source hashes continue to reject incompatible cache reuse; old French projects can restore their saved source commit as before.

## Deferred production

The complete **85–95-second episode is not rendered during PR development**. Final scene/camera review, complete assembly/export and real Tesla T4/Colab/Android validation belong to the later production session on the user's Colab hardware. Six timed scene selections are preproduction outputs, not a claim that a combined pilot MP4 already exists. Do not confuse successful audio preparation with a completed episode or GPU validation.

See [TIMING.md](TIMING.md) for the measured local audio-only result and remaining checks. Review the lore changes and natural pronunciation of Destiny proper names before final production. The Studio remains multilingual; existing French proof media is preserved.
