import argparse
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
SCRIPT = Path(__file__).resolve().parents[1] / "scripts/narration.py"
spec = importlib.util.spec_from_file_location("hybrid_narration", SCRIPT)
n = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n)
class HybridNarration(unittest.TestCase):
    def test_ready_short_embeds_complete_words_without_changing_storyboard(self):
        original = n.read_json(n.ROOT / "episodes/hybrid_riis.json")
        config = n.read_json(n.ROOT / "config/narration.json")
        class FakeKokoro:
            method = "unit-test-only"
            def __init__(self, config): pass
            def synthesize(self, text):
                tokens = text.split()
                return np.full(24000, .1, dtype=np.float32), [dict(text=t, start=i/len(tokens), end=(i+1)/len(tokens)) for i,t in enumerate(tokens)]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            n.write_json(root / "episodes/short.json", original)
            n.write_json(root / "config/narration.json", config)
            args = argparse.Namespace(episode="episodes/short.json", config="config/narration.json", provider=None, enable_openai=False, force=False)
            with patch.object(n, "ROOT", root), patch.object(n, "KokoroProvider", FakeKokoro), patch.object(n.subprocess, "run"):
                n.generate(args)
                ready = n.read_json(root / "out/short-ready.json")
                words = n.read_json(root / "public" / ready["subtitles"]["source"])
                self.assertEqual(ready["shorts"]["alignedWords"], words)
                self.assertEqual(ready["scenes"], original["scenes"])
                self.assertEqual(ready["direction"], original["direction"])
                self.assertEqual(ready["shorts"]["audio"], original["shorts"]["audio"])
