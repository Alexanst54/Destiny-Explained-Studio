import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from contract import validate,BridgeError
from environments.riis import generate

class Environment(unittest.TestCase):
    def source(self):return json.loads((ROOT/'examples/riis-frame-210.json').read_text())
    def test_deterministic_immutable_and_quality(self):
        d=self.source();before=copy.deepcopy(d);counts=[]
        for quality in ['draft','balanced','cinematic']:
            a=generate(d,quality);generate(d,'draft',123)
            self.assertEqual(a,generate(d,quality));self.assertEqual(d,before);validate(a)
            self.assertEqual(a['actors'],d['actors']);self.assertEqual(a['camera'],d['camera']);self.assertEqual(a['source'],d['source'])
            counts.append(len(a['meshes']));self.assertLess(counts[-1],4096)
            ids={x['id'] for x in a['meshes']}
            for mesh in d['meshes']:
                if mesh['id'] not in a['environment']['replacedMeshIds']:self.assertIn(mesh['id'],ids)
        self.assertEqual(counts,sorted(set(counts)))
        self.assertNotEqual(generate(d,seed=42)['meshes'],generate(d,seed=43)['meshes'])
    def test_palette_haze_and_fixture(self):
        d=self.source();validate(d)
        for quality in ['draft','balanced','cinematic']:
            a=generate(d,quality);self.assertTrue(any(m['emission'] for m in a['materials']));self.assertEqual(a['environment']['hazeDensity']>0,quality=='cinematic')
        expected=generate(d);actual=json.loads((ROOT/'examples/riis-before-whirlwind.json').read_text());self.assertEqual(expected,actual)
        self.assertNotEqual(generate(d,lighting='blue-hour')['lights'],generate(d)['lights'])
    def test_invalid_options_and_metadata(self):
        d=self.source()
        for args in [{'detail':'ultra'},{'seed':True},{'seed':-1},{'lighting':'unknown'}]:
            with self.assertRaises(ValueError):generate(d,**args)
        with self.assertRaises(ValueError):generate(generate(d))
        other=copy.deepcopy(d);other['source']['atlas']['variantId']='whirlwind'
        with self.assertRaises(ValueError):generate(other)
        for key,value in [('hazeDensity',float('nan')),('hazeDensity',.5),('seed',-1),('detail','ultra'),('version',True),('replacedMeshIds',['a','a'])]:
            bad=generate(d);bad['environment'][key]=value
            with self.assertRaises(BridgeError):validate(bad)
        for key,value in [('roughness',2),('color','red'),('emission',3)]:
            bad=generate(d);bad['materials'][-1][key]=value
            with self.assertRaises(BridgeError):validate(bad)

if __name__=='__main__':unittest.main()
