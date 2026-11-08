import argparse
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/narration.py"
spec = importlib.util.spec_from_file_location("narration", SCRIPT)
n = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n)


class Timings(unittest.TestCase):
    def test_native_timings_preserve_words_and_contractions(self):
        words = n.words_from_tokens("A Traveler's Light.", [
            {"text":"A", "start":0.2, "end":0.3},
            {"text":"Traveler", "start":0.4, "end":0.9},
            {"text":"'s", "start":0.9, "end":1.0},
            {"text":"Light", "start":1.1, "end":1.5},
            {"text":".", "start":1.5, "end":1.6}], 1.7)
        self.assertEqual([w["text"] for w in words], ["A", "Traveler's", "Light."])
        self.assertEqual(words[1], {"text":"Traveler's", "start":0.4, "end":1.0})
        self.assertNotEqual(words[0]["end"]-words[0]["start"], words[1]["end"]-words[1]["start"])

    def test_missing_text_or_times_never_become_fake_uniform_timings(self):
        for tokens in [[{"text":"Wrong", "start":0, "end":1}],
                       [{"text":"Light", "start":None, "end":1}],
                       [{"text":"Light", "start":0, "end":2}]]:
            with self.assertRaises(ValueError):
                n.words_from_tokens("Light", tokens, 1)
        with self.assertRaises(ValueError):
            n.words_from_tokens("Last City", [{"text":"Last City", "start":0, "end":1}], 1)

    def test_scene_offsets_lead_in_and_overflow(self):
        scene={"id":"scene-02", "startFrame":240, "durationFrames":300, "narration":"Light"}
        words=[{"text":"Light", "start":0.2, "end":0.8}]
        self.assertEqual(n.place_words(words,scene,30,24000,0.15),
                         [{"text":"Light", "start":8.35, "end":8.95}])
        with self.assertRaisesRegex(ValueError,"exceeds"):
            n.place_words(words,scene,30,240001)
        with self.assertRaises(ValueError):
            n.place_words(words,scene,30,1000)

    def test_openai_is_disabled_even_with_a_key(self):
        with patch.dict(os.environ,{"OPENAI_API_KEY":"not-a-real-key"}):
            with self.assertRaisesRegex(ValueError,"disabled"):
                n.OpenAIProvider({}, enabled=False)
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaisesRegex(ValueError,"OPENAI_API_KEY"):
                n.OpenAIProvider({}, enabled=True)

    def test_ids_cannot_escape_the_assets_directory(self):
        for bad in ["../audio", "/tmp/file", "scene/01"]:
            with self.assertRaises(ValueError): n.slug(bad)


class Assembly(unittest.TestCase):
    def test_padding_cache_and_no_paid_provider_fallback(self):
        import numpy as np
        import soundfile as sf
        original=n.read_json(n.ROOT/"episodes/traveler_episode_002.json")
        config=n.read_json(n.ROOT/"config/narration.json")
        class FakeKokoro:
            method="unit-test-only"
            def __init__(self, config): pass
            def synthesize(self,text):
                tokens=text.split()
                return np.full(24000,0.1,dtype=np.float32), [
                    {"text":t,"start":i/len(tokens),"end":(i+1)/len(tokens)} for i,t in enumerate(tokens)]
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            n.write_json(root/"episodes/episode.json",original)
            n.write_json(root/"config/narration.json",config)
            args=argparse.Namespace(episode="episodes/episode.json",config="config/narration.json",
                                    provider=None,enable_openai=False,force=False)
            with patch.object(n,"ROOT",root), patch.object(n,"KokoroProvider",FakeKokoro), \
                    patch.object(n,"OpenAIProvider") as paid, patch.object(n.subprocess,"run"):
                n.generate(args)
                paid.assert_not_called()
                ready=n.read_json(root/"out/episode-ready.json")
                audio,sr=sf.read(root/"public"/ready["audio"]["voiceover"]["source"])
                self.assertEqual((len(audio),sr),(60*24000,24000))
                self.assertAlmostEqual(float(audio[24000*7]),0)  # Silence in scene 01's unused tail.
                self.assertGreater(float(audio[24000*8+5000]),0)
                self.assertEqual(ready["format"]["durationFrames"],1800)
                with patch.object(n,"KokoroProvider") as cached:
                    n.generate(args)
                    cached.assert_not_called()
                with patch.object(n.subprocess,"run",side_effect=n.subprocess.CalledProcessError(1,"validate")):
                    with self.assertRaises(n.subprocess.CalledProcessError): n.generate(args)
                self.assertFalse((root/"out/episode-ready.json").exists())
                n.generate(args)
                args.force=True
                with patch.object(FakeKokoro,"synthesize",side_effect=ValueError("overflow")):
                    with self.assertRaises(ValueError): n.generate(args)
                self.assertFalse((root/"out/episode-ready.json").exists())


if __name__ == "__main__": unittest.main()
