import json,pathlib,sys,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from inspect_existing import inspect
from perf_common import sha
from test_complete_atheon import fixture_png
class Inspect(unittest.TestCase):
 def test_read_only_inspector_labels_cumulative_history_and_measures_optional_verification(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);(root/'project.json').write_text(json.dumps(dict(sourceCommit='fixture',fingerprint='unit')));chunk=root/'public/scenes/01-hook/frames/chunk-000000';chunk.mkdir(parents=True);png=chunk/'frame-0000.png';png.write_bytes(fixture_png(360,640,1));report=dict(status='success',request=dict(width=360,height=640,fps=30),frames={'0':dict(file=png.name,sha256=sha(png),seconds=2.5,device=dict(selected='CPU',backend=None,devices=[]))},buildSeconds=.2,workerSeconds=3,lastRunWallSeconds=4);(chunk/'progress.json').write_text(json.dumps(report));before={str(p):p.read_bytes() for p in root.rglob('*') if p.is_file()}
   result=inspect(root,True);self.assertEqual(result['recordedFrames'],1);self.assertEqual(result['recordedMedianFrameSeconds'],2.5);self.assertFalse(result['newGpuBenchmark']);self.assertEqual(result['invalidFrames'],[]);self.assertEqual(before,{str(p):p.read_bytes() for p in root.rglob('*') if p.is_file()})
   png.write_bytes(b'bad');self.assertEqual(len(inspect(root,True)['invalidFrames']),1)
if __name__=='__main__':unittest.main()
