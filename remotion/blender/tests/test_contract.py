import ast
import copy
import importlib.util
import json
from pathlib import Path
import struct
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from contract import validate,BridgeError

class Contract(unittest.TestCase):
    def data(self):return json.loads((ROOT/'examples/riis-frame-210.json').read_text())
    def test_fixture_and_references(self):
        d=self.data();validate(d)
        self.assertEqual(len(d['actors']),6)
        self.assertEqual(d['source']['frame'],210)
        self.assertTrue(all(m['material'] in {v['id'] for v in d['materials']} for m in d['meshes']))
    def test_nonfinite_singular_unknown_and_missing_rejected(self):
        for fn in [lambda d:d.update(version=True),lambda d:d['meshes'][0].update(geometry='download-model'),lambda d:d['camera']['matrixWorld'].__setitem__(0,float('nan')),lambda d:d['meshes'][0].update(matrixWorld=[0]*15+[1]),lambda d:d['actors'][0]['joints'][0].update(parent='missing'),lambda d:d.update(extra='unknown')]:
            d=self.data();fn(d)
            with self.assertRaises(BridgeError):validate(d)
    def test_notebook_cells_compile_and_have_no_recorded_execution(self):
        d=json.loads((ROOT/'Blender-Colab-Pro.ipynb').read_text());code=[]
        for i,cell in enumerate(d['cells']):
            if cell['cell_type']=='code':
                self.assertEqual(cell['outputs'],[]);self.assertIsNone(cell['execution_count']);s=''.join(cell['source']);ast.parse(s,filename=f'cell-{i}');code.append(s)
        text='\n'.join(code)
        self.assertIn('len(snapshots)==1',text);self.assertIn('from render_one import render_one',text);self.assertIn('--python-exit-code',(ROOT/'render_one.py').read_text());self.assertNotIn("'--animation'",text);self.assertNotIn("'switch','-C'",text)

if __name__=='__main__':unittest.main()
