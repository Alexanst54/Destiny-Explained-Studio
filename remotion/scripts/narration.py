"""Scene TTS -> real word timestamps -> padded episode WAV and ready Remotion JSON.

Kokoro is local and key-free. OpenAI requires two explicit flags and a secret in
OPENAI_API_KEY. No provider fallback, time stretching or truncated speech.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_RATE = 24000
PIPELINE_VERSION = 1


def normalize(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(path)


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def slug(value):
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", value):
        raise ValueError("Episode and scene IDs must be filesystem-safe slugs")
    return value


def words_from_tokens(text, tokens, duration):
    """Map timed synthesis tokens to original whitespace words, merging contractions.

    No equal word durations are invented. Missing, ambiguous or overlapping token
    timestamps are errors, rather than silently producing estimated captions.
    """
    pieces = []
    offset = 0
    for token in tokens:
        part = normalize(token["text"])
        if not part:
            continue
        start, end = token["start"], token["end"]
        if start is None or end is None or not all(map(math.isfinite, [start, end])):
            raise ValueError(f"Missing timing for token {token['text']!r}")
        if start < 0 or end <= start or end > duration + 0.05:
            raise ValueError(f"Invalid synthesis timing for {token['text']!r}")
        pieces.append((offset, offset + len(part), start, min(end, duration)))
        offset += len(part)
    if "".join(normalize(t["text"]) for t in tokens) != normalize(text):
        raise ValueError("Synthesized/aligned text differs from the supplied narration")
    words = []
    cursor = 0
    for match in re.finditer(r"\S+", text):
        word = match.group()
        size = len(normalize(word))
        if not size:
            if words:
                words[-1]["text"] += word
            continue
        spans = [p for p in pieces if p[0] < cursor + size and p[1] > cursor]
        if not spans:
            raise ValueError(f"No timing for {word!r}")
        start, end = spans[0][2], spans[-1][3]
        if words and start < words[-1]["end"] - 1e-6:
            raise ValueError("A timed token spans multiple whitespace words; forced alignment is required")
        words.append({"text": word, "start": start, "end": end})
        cursor += size
    return words


def place_words(words, scene, fps, samples, lead_in=0):
    duration = samples / SAMPLE_RATE
    budget = scene["durationFrames"] / fps
    if samples > round(budget * SAMPLE_RATE):
        raise ValueError(f"{scene['id']}: narration {duration:.3f}s exceeds {budget:.3f}s at speed 1x; "
                         "revise text or scene durations. Audio will not be cut or accelerated.")
    offset = scene["startFrame"] / fps
    previous = 0.0
    result = []
    for word in words:
        start, end = word["start"] + lead_in, word["end"] + lead_in
        if not all(map(math.isfinite, [start, end])) or start < previous - 1e-6 or start < 0 or end <= start or end > duration + 1e-6:
            raise ValueError(f"Invalid local word timing in {scene['id']}")
        result.append({"text": word["text"], "start": round(offset + start, 6),
                       "end": round(offset + end, 6)})
        previous = end
    if normalize(" ".join(w["text"] for w in result)) != normalize(scene["narration"]):
        raise ValueError(f"Incomplete word alignment in {scene['id']}")
    return result


class KokoroProvider:
    method = "kokoro-predicted-phoneme-durations"

    def __init__(self, config):
        os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
        import torch
        from huggingface_hub import hf_hub_download
        from kokoro import KModel, KPipeline
        torch.set_num_threads(config["threads"])
        torch.manual_seed(0)
        download = lambda name: hf_hub_download(repo_id=config["repo"], filename=name,
                                               revision=config["revision"])
        model = KModel(repo_id=config["repo"], config=download("config.json"),
                       model=download("kokoro-v1_0.pth")).to("cpu").eval()
        self.pipeline = KPipeline(lang_code=config["language"], repo_id=config["repo"], model=model)
        self.voice = download(f"voices/{config['voice']}.pt")
        self.speed = config["speed"]

    def synthesize(self, text):
        import numpy as np
        audio, tokens = [], []
        offset = 0
        for result in self.pipeline(text, voice=self.voice, speed=self.speed, split_pattern=None):
            if result.audio is None or not result.tokens:
                raise ValueError("Kokoro did not return audio with token timestamps")
            chunk = result.audio.detach().cpu().numpy().astype(np.float32)
            for token in result.tokens:
                tokens.append({"text": token.text,
                               "start": None if token.start_ts is None else offset + token.start_ts,
                               "end": None if token.end_ts is None else offset + token.end_ts})
            audio.append(chunk)
            offset += len(chunk) / SAMPLE_RATE
        if not audio:
            raise ValueError("Kokoro produced no audio")
        merged = np.concatenate(audio)
        return merged, words_from_tokens(text, tokens, len(merged) / SAMPLE_RATE)


class OpenAIProvider:
    method = "stable-ts-local-forced-alignment"

    def __init__(self, config, enabled=False):
        if not enabled:
            raise ValueError("OpenAI is disabled: explicitly pass --provider openai --enable-openai")
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError("OpenAI requires OPENAI_API_KEY; Kokoro requires no key")
        import stable_whisper
        self.aligner = stable_whisper.load_model(config["alignmentModel"], device="cpu")
        self.config, self.key = config, key

    def synthesize(self, text):
        import soundfile as sf
        payload = json.dumps({"model": self.config["model"], "voice": self.config["voice"],
                              "speed": self.config["speed"], "input": text, "response_format": "wav"}).encode()
        request = urllib.request.Request("https://api.openai.com/v1/audio/speech", data=payload,
                                         headers={"Authorization": f"Bearer {self.key}",
                                                  "Content-Type": "application/json"})
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "speech.wav"
            try:
                with urllib.request.urlopen(request, timeout=120) as response:
                    path.write_bytes(response.read())
            except urllib.error.HTTPError as error:
                raise RuntimeError(f"OpenAI TTS failed with HTTP {error.code}") from None
            audio, sr = sf.read(path, dtype="float32")
            if sr != SAMPLE_RATE or audio.ndim != 1:
                converted = Path(temp) / "mono.wav"
                subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ar", str(SAMPLE_RATE),
                                "-ac", "1", str(converted)], check=True)
                path = converted
                audio, _ = sf.read(path, dtype="float32")
            aligned = self.aligner.align(str(path), text, language="en")
            tokens = [{"text": word["word"], "start": word["start"], "end": word["end"]}
                      for segment in aligned.to_dict()["segments"] for word in segment["words"]]
            return audio, words_from_tokens(text, tokens, len(audio) / SAMPLE_RATE)


def generate(args):
    import numpy as np
    import soundfile as sf
    source = (ROOT / args.episode).resolve()
    ready_path = ROOT / "out" / f"{source.stem}-ready.json"
    ready_path.unlink(missing_ok=True)  # Even validation/config failures invalidate stale readiness.
    config = read_json(ROOT / args.config)
    provider_name = args.provider or config["provider"]
    if provider_name == "openai" and not args.enable_openai:
        raise ValueError("OpenAI is disabled: explicitly pass --provider openai --enable-openai")
    if provider_name not in ("kokoro", "openai"):
        raise ValueError("Unsupported narration provider")
    selected = copy.deepcopy(config[provider_name])
    if provider_name == "openai":
        selected["enabled"] = args.enable_openai  # Explicit opt-in overrides the disabled default for this run.
    if selected["speed"] != 1.0:
        raise ValueError("This workflow requires narration speed 1x")
    if provider_name == "kokoro" and selected["voice"] != "af_heart":
        raise ValueError("The default Kokoro workflow requires af_heart")
    subprocess.run(["node", "--experimental-strip-types", str(ROOT / "scripts/episode.mjs"),
                    "validate", str(source), "--preview"], cwd=ROOT, check=True)
    episode = read_json(source)
    fps = episode["format"]["fps"]
    slug(episode["id"])
    for scene in episode["scenes"]:
        slug(scene["id"])
    key = fingerprint({"pipeline": PIPELINE_VERSION, "episode": episode,
                       "provider": provider_name, "config": selected, "leadIn": config["leadInSeconds"]})[:16]
    folder = ROOT / "public/assets/narration" / slug(episode["id"]) / f"{provider_name}-{key}"
    folder.mkdir(parents=True, exist_ok=True)
    lead = round(config["leadInSeconds"] * SAMPLE_RATE)
    if lead < 0:
        raise ValueError("leadInSeconds must be nonnegative")
    total_samples = round(episode["format"]["durationFrames"] / fps * SAMPLE_RATE)
    track = np.zeros(total_samples, dtype=np.float32)
    all_words, reports = [], []
    provider = None  # No model or paid provider is loaded for valid cached scenes.
    for scene in episode["scenes"]:
        audio_path = folder / f"{scene['id']}.wav"
        cache_path = folder / f"{scene['id']}.cache.json"
        cached = read_json(cache_path) if cache_path.exists() and not args.force else None
        if cached and audio_path.exists() and cached.get("sha256") == hashlib.sha256(audio_path.read_bytes()).hexdigest():
            audio, sr = sf.read(audio_path, dtype="float32")
            if sr != SAMPLE_RATE or audio.ndim != 1:
                raise ValueError("Invalid cached audio")
            words, method = cached["words"], cached["method"]
            speech_seconds = cached["speechSeconds"]
        else:
            if provider is None:
                provider = KokoroProvider(selected) if provider_name == "kokoro" else OpenAIProvider(selected, args.enable_openai)
            speech, words = provider.synthesize(scene["narration"])
            if not np.isfinite(speech).all() or len(speech) == 0 or np.max(np.abs(speech)) < 1e-5:
                raise ValueError(f"{scene['id']}: empty or invalid speech")
            peak = float(np.max(np.abs(speech)))
            if peak > 0.98:
                speech = speech * (0.98 / peak)  # Gain only; no time stretching.
            speech_seconds = len(speech) / SAMPLE_RATE
            audio = np.concatenate([np.zeros(lead, dtype=np.float32), speech])
            method = provider.method
            sf.write(audio_path, audio, SAMPLE_RATE, subtype="PCM_16")
            write_json(cache_path, {"sha256": hashlib.sha256(audio_path.read_bytes()).hexdigest(),
                                   "words": words, "method": method, "speechSeconds": speech_seconds})
            audio, _ = sf.read(audio_path, dtype="float32")
        global_words = place_words(words, scene, fps, len(audio), lead / SAMPLE_RATE)
        start = round(scene["startFrame"] / fps * SAMPLE_RATE)
        track[start:start + len(audio)] = audio
        all_words.extend(global_words)
        local_words = [{"text": w["text"], "start": round(w["start"] - scene["startFrame"] / fps, 6),
                        "end": round(w["end"] - scene["startFrame"] / fps, 6)} for w in global_words]
        write_json(folder / f"{scene['id']}.words.json", local_words)
        report = {"id": scene["id"], "source": audio_path.relative_to(ROOT / "public").as_posix(),
                  "startFrame": scene["startFrame"], "budgetSeconds": scene["durationFrames"] / fps,
                  "audioSeconds": len(audio) / SAMPLE_RATE, "speechSeconds": speech_seconds,
                  "paddingSeconds": scene["durationFrames"] / fps - len(audio) / SAMPLE_RATE,
                  "wordCount": len(words), "alignment": method}
        reports.append(report)
        print(f"{scene['id']}: {report['audioSeconds']:.3f}s / {report['budgetSeconds']:.3f}s, {len(words)} words", flush=True)
    sf.write(folder / "narration.wav", track, SAMPLE_RATE, subtype="PCM_16")
    write_json(folder / "words.json", all_words)
    ready = copy.deepcopy(episode)
    relative = folder.relative_to(ROOT / "public").as_posix()
    ready["audio"]["voiceover"].update(enabled=True, status="ready", source=f"{relative}/narration.wav")
    ready["subtitles"].update(status="ready", source=f"{relative}/words.json")
    if ready.get("shorts") is not None:
        ready["shorts"]["alignedWords"] = all_words
    write_json(ready_path, ready)
    try:
        subprocess.run(["node", "--experimental-strip-types", str(ROOT / "scripts/episode.mjs"),
                        "validate", str(ready_path)], cwd=ROOT, check=True)
    except Exception:
        ready_path.unlink(missing_ok=True)
        raise
    report = {"provider": provider_name, "voice": selected["voice"], "speed": selected["speed"],
              "model": selected, "sourceSha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "sampleRate": SAMPLE_RATE, "timelineSeconds": len(track) / SAMPLE_RATE,
              "speechSeconds": sum(r["speechSeconds"] for r in reports), "wordCount": len(all_words),
              "scenes": reports, "readyEpisode": str(ready_path.relative_to(ROOT))}
    write_json(ROOT / "out/narration-report.json", report)
    write_json(folder / "manifest.json", report)
    print(f"Ready: {ready_path}\nTimeline: {len(track)/SAMPLE_RATE:.3f}s; {len(all_words)} aligned words", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("episode", nargs="?", default="episodes/traveler_episode_002.json")
    parser.add_argument("--config", default="config/narration.json")
    parser.add_argument("--provider", choices=["kokoro", "openai"])
    parser.add_argument("--enable-openai", action="store_true", help="Explicitly opt in to paid OpenAI speech calls")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        generate(args)
    except Exception as error:
        print(f"Narration failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
