import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('animation_narration', Path(__file__).resolve().parents[1]/'scripts/narration.py')
n = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n)

class NarrationGroups(unittest.TestCase):
    def episode(self):
        return {'audio':{'voiceover':{}},'scenes':[{'id':str(i),'startFrame':i*60,'durationFrames':60,'narration':'word '+str(i)} for i in range(4)]}
    def test_no_groups_preserves_legacy_units(self):
        e=self.episode()
        self.assertEqual(n.narration_units(e), e['scenes'])
    def test_contiguous_group_preserves_every_word_and_timing_budget(self):
        e=self.episode();e['audio']['voiceover']['groups']=[['1','2','3']]
        units=n.narration_units(e)
        self.assertEqual(len(units),2)
        self.assertEqual(units[1]['startFrame'],60)
        self.assertEqual(units[1]['durationFrames'],180)
        self.assertEqual(units[1]['narration'],'word 1 word 2 word 3')
        self.assertEqual(len(e['scenes']),4)
    def test_missing_noncontiguous_and_duplicate_ids_fail(self):
        for groups in [[['0','2']],[['0','missing']],[['0','1'],['1','2']]]:
            e=self.episode();e['audio']['voiceover']['groups']=groups
            with self.assertRaises(ValueError):n.narration_units(e)
