import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import sequence
from png_fixture import png


class Persistent(unittest.TestCase):
    def test_worker_mode_resume_crash_fallback_and_strict(self):
        data=json.loads((ROOT/'examples/riis-frame-210.json').read_text())
        def export(command,**kwargs):
            for i in range(int(command[-2])):
                d=json.loads(json.dumps(data));d['source']['frame']=120+i
                (Path(command[-1])/f'{i:05d}.json').write_text(json.dumps(d))
        def commit(folder,i):
            output=folder/f'{i:05d}.png';output.write_bytes(png(108,192))
            sequence.atomic(output.with_suffix('.done.json'),{'key':sequence.digest(json.loads(output.with_suffix('.json').read_text())),'pngSha256':sequence.sha(output),'configuration':{'selected':'CPU'}})
        batches=[]
        def batch(command,log,timeout,on_tick):
            job=json.loads(Path(command[-1]).read_text());folder=Path(command[-1]).parent
            batches.append(job['indices'])
            self.assertEqual(command[command.index('--python')+1],str(ROOT/'render_batch.py'))
            commit(folder,job['indices'][0]);self.assertTrue(on_tick());self.assertFalse(on_tick())
            if len(job['indices'])>1:raise RuntimeError('simulated GPU crash')
        def single(snapshot,output,*args):
            output.write_bytes(png(108,192));return {'report':{'configuration':{'selected':'CPU'}}}
        with tempfile.TemporaryDirectory() as folder,patch.object(sequence.subprocess,'check_output',return_value='Blender test'),patch.object(sequence.subprocess,'run',side_effect=export),patch.object(sequence,'stream_process',side_effect=batch),patch.object(sequence,'render_one',side_effect=single) as fallback,contextlib.redirect_stdout(io.StringIO()):
            options=dict(project='x',cache=folder,count=3,public=None)
            cache,r=sequence.run(**options,max_new=1)
            self.assertEqual(r['rendererMode'],'persistent');self.assertEqual(r['completed'],1)
            _,r=sequence.run(**options)
            self.assertEqual(batches,[[0],[1,2]]);self.assertEqual(r['cacheHits'],1);self.assertEqual(r['newFrames'],2);self.assertEqual(len(r['fallbacks']),1);self.assertEqual(fallback.call_count,1)
            sequence.run(**options);self.assertEqual(len(batches),2)
            # Strict benchmark mode keeps committed first frame, never masks a crash.
            for i in (0,1,2):(cache/f'{i:05d}.done.json').unlink()
            with self.assertRaisesRegex(RuntimeError,'simulated'):sequence.run(**options,fallback=False)
            self.assertEqual(json.loads((cache/'sequence-report.json').read_text())['completed'],1)
            self.assertEqual(fallback.call_count,1)

    def test_png_crc_and_compressed_data(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'frame.png';path.write_bytes(png(2,3))
            self.assertTrue(sequence.png_valid(path,2,3))
            self.assertFalse(sequence.png_valid(path,3,2))
            raw=bytearray(path.read_bytes());raw[45]^=1;path.write_bytes(raw)
            self.assertFalse(sequence.png_valid(path,2,3))
