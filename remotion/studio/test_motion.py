import json,pathlib,sys,tempfile,unittest
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from complete_atheon import load_package
from motion_test import jobs_for,SELECTED
from shot_audit import timeline
from cinematic_direction import shot_at
from route_diagnostics import inspect
from perf_common import cpu_delta,cpu_snapshot,Telemetry
class Motion(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.package=load_package()
 def test_nineteen_ranges_and_actual_discrete_boundaries(self):
  rows=timeline(self.package);self.assertEqual(len(rows),19);self.assertEqual([f for r in rows for f in range(r['episodeFrameStart'],r['episodeFrameEndExclusive'])],list(range(2672)))
  for row in rows:
   n=next(i['timing']['durationFrames'] for i in self.package['scenes'] if i['scene']['id']==row['sceneId'])
   for f in range(row['sceneFrameStart'],row['sceneFrameEndExclusive']):
    s=shot_at(row['sceneId'],f,n);self.assertEqual((s['cutStart'],s['cutEnd']),(row['sceneFrameStart'],row['sceneFrameEndExclusive']))
  templar=next(r for r in rows if r['cameraId']=='templar');self.assertEqual(templar['sceneFrameStart'],284)
 def test_motion_is_bounded_distinct_and_uses_true_source_time(self):
  for fps in [10,30]:
   jobs=jobs_for(self.package,540,960,fps=fps);self.assertEqual([j['shotId'] for j in jobs],SELECTED);self.assertEqual(sum(len(j['indices']) for j in jobs),fps*3)
   for j in jobs:
    frames=[j['request']['startFrame']+i for i in j['indices']];self.assertEqual(len(set(frames)),fps)
    self.assertTrue(all(shot_at(j['sceneId'],f,j['sceneFrames'])['name']==j['cameraId'] for f in frames));self.assertEqual(j['request']['fps'],30);self.assertEqual(j['indices'][1],30//fps)
  with self.assertRaises(ValueError):jobs_for(self.package,540,960,fps=60)
 def test_route_uses_manifest_not_duration(self):
  for kind,route in [('complete-atheon-v1','legacy-prepared-pilot'),('directed-atheon-v1','cinematic-Q'),('atheon-motion-test-v1','cinematic-motion-diagnostic')]:
   with tempfile.TemporaryDirectory() as d:
    p=pathlib.Path(d);(p/'project.json').write_text(json.dumps(dict(identity=dict(kind=kind),sourceCommit='fixture')));before=(p/'project.json').read_bytes();r=inspect(p);self.assertEqual(r['route'],route);self.assertEqual(before,(p/'project.json').read_bytes())
 def test_missing_gpu_power_stays_null(self):
  with tempfile.TemporaryDirectory() as d,patch('perf_common.shutil.which',return_value=None):
   m=Telemetry(pathlib.Path(d)/'gpu');m.poll();self.assertIsNone(m.report()['meanPowerWatts']);self.assertIsNone(m.report()['peakPowerWatts'])
 def test_scheduler_wait_is_not_wall_minus_cpu(self):
  a=dict(cpuSeconds=2,voluntary=3,involuntary=4,threads={'1':[100,200]});b=dict(cpuSeconds=4,voluntary=6,involuntary=5,threads={'1':[300,500]});r=cpu_delta(a,b);self.assertEqual(r['threadRunQueueWaitSeconds'],300/1e9);self.assertIsNone(r['blockingIoOrGpuWaitSeconds']);self.assertEqual(r['voluntaryContextSwitches'],3)
if __name__=='__main__':unittest.main()
