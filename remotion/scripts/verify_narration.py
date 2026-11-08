"""Verify generated narration and MP4 stream timing without another paid service."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]


def verify(ready_path, video_path):
    episode = json.loads(ready_path.read_text())
    subprocess.run(["node", "--experimental-strip-types", str(ROOT/"scripts/episode.mjs"),
                    "validate", str(ready_path)], cwd=ROOT, check=True)
    words = json.loads((ROOT/"public"/episode["subtitles"]["source"]).read_text())
    source, sr = sf.read(ROOT/"public"/episode["audio"]["voiceover"]["source"], dtype="float32")
    duration = episode["format"]["durationFrames"] / episode["format"]["fps"]
    if sr != 24000 or source.ndim != 1 or len(source) != round(duration*sr):
        raise ValueError("Source narration must be mono 24 kHz and match the episode duration")
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video_path)],
                           check=True, capture_output=True, text=True)
    metadata = json.loads(probe.stdout)
    video = next(s for s in metadata["streams"] if s["codec_type"] == "video")
    audio = next(s for s in metadata["streams"] if s["codec_type"] == "audio")
    if (video["width"],video["height"],video["r_frame_rate"]) != (1080,1920,"30/1"):
        raise ValueError("Unexpected video format")
    if video["codec_name"] != "h264" or audio["codec_name"] != "aac":
        raise ValueError("Expected H.264 and AAC")
    if abs(float(video["duration"])-duration) > 1/30 or abs(float(audio["duration"])-duration) > 0.05:
        raise ValueError("Audio/video duration mismatch")
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp)/"decoded.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(video_path), "-vn", "-ac", "1", "-ar", str(sr), str(path)], check=True)
        decoded, _ = sf.read(path, dtype="float32")
    if len(decoded) < len(source):
        raise ValueError("Decoded narration is shorter than the source")
    checks = []
    # AAC can add trailing packet padding. Compare content in six one-second
    # windows, one per scene, allowing a 50 ms search around the expected offset.
    for scene in episode["scenes"]:
        begin = round((scene["startFrame"]/30 + 2)*sr)
        count, radius = sr, round(sr*0.05)
        ref = source[begin:begin+count]
        chunk = decoded[begin-radius:begin+count+radius]
        lag = int(np.argmax(np.correlate(chunk,ref,mode="valid"))) - radius
        actual = decoded[begin+lag:begin+lag+count]
        correlation = float(np.dot(ref,actual)/(np.linalg.norm(ref)*np.linalg.norm(actual)))
        if abs(lag/sr) > 0.01 or correlation < 0.95:
            raise ValueError(f"Encoded audio drifts in {scene['id']}: {lag/sr}s, correlation {correlation}")
        checks.append({"scene":scene["id"],"lagMs":lag/sr*1000,"correlation":correlation})
    rms = [float(np.sqrt(np.mean(source[round(w["start"]*sr):round(w["end"]*sr)]**2))) for w in words]
    if not rms or not all(np.isfinite(v) and v>1e-5 for v in rms):
        raise ValueError("An aligned word has no measurable source audio")
    report = {"durationSeconds":duration,"words":len(words),"wordsWithAudio":sum(v>1e-5 for v in rms),
              "minWordRms":min(rms),"videoCodec":video["codec_name"],"audioCodec":audio["codec_name"],
              "audioDurationSeconds":float(audio["duration"]),"videoDurationSeconds":float(video["duration"]),
              "audioChecks":checks,"method":"Source waveform vs decoded AAC, not an independent annotation of word boundaries"}
    (ROOT/"out/audio-verification.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode",default="out/traveler_episode_002-ready.json")
    parser.add_argument("--video",default="out/episode-002-traveler.mp4")
    args = parser.parse_args()
    verify((ROOT/args.episode).resolve(), (ROOT/args.video).resolve())
