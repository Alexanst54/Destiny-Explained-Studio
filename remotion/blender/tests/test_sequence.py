import contextlib
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import sequence

class Sequence(unittest.TestCase):
    def test_resume_corruption_and_fullhd_gate(self):
        data=json.loads((ROOT/'examples/riis-frame-210.json').read_text());calls=[]
        def export(cmd,**kwargs):
            for i in range(int(cmd[-2])):
                d=json.loads(json.dumps(data));d['source']['frame']=120+i
                (Path(cmd[-1])/f'{i:05d}.json').write_text(json.dumps(d))
        def render(snapshot,png,blender,device,scale,threads,timeout):
            calls.append(png.name);png.write_bytes(b'\x89PNG\r\n\x1a\n'+b'\0'*8+struct.pack('>II',1080*scale//100,1920*scale//100)+b'\0'*4+b'IEND'+b'\0'*4)
            return {'report':{'configuration':{'selected':'CPU'}}}
        with tempfile.TemporaryDirectory() as folder,patch.object(sequence.subprocess,'check_output',return_value='Blender test\n'),patch.object(sequence.subprocess,'run',side_effect=export),patch.object(sequence,'render_one',side_effect=render),contextlib.redirect_stdout(io.StringIO()):
            options=dict(project='project',cache=folder,start=120,count=3,public=Path(folder)/'public')
            with self.assertRaisesRegex(ValueError,'preview'):sequence.run(**options,scale=100)
            cache,r=sequence.run(**options,max_new=1);self.assertEqual(r['completed'],1);self.assertEqual(r['status'],'incomplete')
            _,r=sequence.run(**options);self.assertEqual(r['cacheHits'],1);self.assertEqual(r['newFrames'],2);self.assertEqual(r['status'],'complete');self.assertEqual(len(calls),3)
            manifest=json.loads((cache/'remotion-sequences.json').read_text());self.assertEqual(len(manifest['clips'][0]['frames']),3)
            (cache/'00001.png').write_bytes(b'truncated')
            _,r=sequence.run(**options);self.assertEqual(r['newFrames'],1);self.assertEqual(r['cacheHits'],2)
            _,r=sequence.run(**options,scale=100);self.assertEqual(r['status'],'complete')
            _,changed=sequence.run(**options,seed=43,max_new=1);self.assertNotEqual(r['key'],changed['key'])
    def test_invalid_options(self):
        for option in [{'count':91},{'count':0},{'scale':9},{'device':'cuda-typo'},{'max_new':0}]:
            with self.assertRaises(ValueError):sequence.run('x','x',**option)

if __name__=='__main__':unittest.main()
