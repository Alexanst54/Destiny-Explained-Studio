# Actual English speech timing — audio-only preproduction

Kokoro `af_heart`, locale `en-US`, speed **1.0**. No image sequence or complete episode video was rendered.

| Scene | Actual speech | Scene duration at 30 FPS | Start frame | Frames |
| --- | --- | --- | --- | --- |
| The Hook | 11.250 s | 11.500 s | 0 | 345 |
| Who Is Atheon? | 15.025 s | 15.300 s | 345 | 459 |
| The Vault of Glass | 15.475 s | 15.733 s | 804 | 472 |
| Master of Time? | 16.675 s | 16.933 s | 1276 | 508 |
| The Guardians | 12.650 s | 12.900 s | 1784 | 387 |
| The Mystery | 16.450 s | 16.700 s | 2171 | 501 |

Total speech: **87.525 s**. Planned episode: **89.067 s / 2672 frames**, inside the 85–95-second target. Tails are a quarter-second minimum per scene plus rounding to a whole frame; no words are truncated and no playback rate is changed.

Each scene has its complete audio probe, exact source-text word sequence, synthesis-token timestamps, WAV hash and a timed Studio selection under [audio-evidence/](audio-evidence/). These files are audio-only measurements, not a final combined cinematic episode. The final vertical 9:16 scene/episode render, camera review, pronunciation listening review and T4/Colab acceptance remain for the user’s later production session.

The six supplied scenes are preserved separately from two documented lore corrections. Timing is for the lore-reviewed production script, not an estimate from word count. The audio-only planner can be rerun in the Studio notebook and writes output to Drive. It never launches Blender or Remotion.

French regression: resynthesizing the existing “Voici ce boss.” probe with `ff_siwis` produced exactly the same WAV SHA-256 as the preserved French fixture. Locale and voice validation rejects cross-language combinations; old configs without a language retain French semantics. See [language-validation.json](language-validation.json).
