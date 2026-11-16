"""Offline control tests: synthetic PNGs are fixtures, never visual evidence."""
import json,pathlib,sys,tempfile,unittest
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from test_complete_atheon import fixture_png
import performance as perf
import perf_common as common
import cinematic_atheon as cine
from cinematic_direction import SHOTS,shot_at,camera
from complete_atheon import load_package

class Performance(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.package=load_package()
 def test_same_representative_windows_all_six_scenes(self):
  for n in [30,36,48,60]:
   jobs=perf.jobs_for(self.package,540,960,n);self.assertEqual(sum(len(j['indices']) for j in jobs),n);self.assertEqual(len(jobs),6)
   for j in jobs:self.assertEqual((j['request']['seed'],j['request']['lod'],j['request']['fps']),(42,0,30))
  with self.assertRaises(ValueError):perf.jobs_for(self.package,540,960,29)
 def test_directed_frame_plan_exact_no_duplicates_and_true_templar_binding(self):
  jobs=cine.jobs_for(self.package,540,960);props=cine.props_for(self.package,dict(width=540,height=960),jobs)
  self.assertEqual(props['frames'],2672);self.assertEqual(sum(len(j['indices']) for j in jobs),2672)
  self.assertEqual(len(set(p for s in props['scenes'] for p in s['frameSources'])),2672)
  for j in jobs:
   self.assertLessEqual(len(j['indices']),120);self.assertTrue(j['id'].startswith('scenes/'))
   expected=('boss-templar','arena-templars-well') if j['shotName']=='templar' else ('boss-atheon','arena-glass-throne')
   self.assertEqual((j['request']['selectionId'],j['request']['binding']['environmentId']),expected)
 def test_cameras_and_all_shot_frames_are_deterministic(self):
  for item in self.package['scenes']:
   frames=item['timing']['durationFrames'];sid=item['scene']['id'];names=set()
   for f in range(frames):
    shot=shot_at(sid,f,frames);names.add(shot['name']);self.assertEqual(camera(shot),camera(shot));self.assertTrue(0<=shot['progress']<1)
   self.assertEqual(names,{p[2] for p in SHOTS[sid]})
   with self.assertRaises(ValueError):shot_at(sid,frames,frames)
 def test_checkpoint_resume_corruption_and_identity_isolation(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);local=root/'local';remote=root/'remote';local.mkdir();png=local/'frame-0000.png';png.write_bytes(fixture_png(360,640,1));rec=dict(file=png.name,sha256=common.sha(png));common.atomic_json(local/'profile.json',dict(identity='unit-fixture',frames={'0':rec}))
   first=common.checkpoint(local,remote,'unit-fixture',360,640);self.assertEqual(first['copiedFrames'],1)
   self.assertEqual(common.checkpoint(local,remote,'unit-fixture',360,640)['copiedFrames'],0)
   (remote/png.name).write_bytes(b'corrupt');self.assertEqual(common.checkpoint(local,remote,'unit-fixture',360,640)['copiedFrames'],1)
   restored=root/'new-runtime';perf.restore_job(remote,restored,'unit-fixture',360,640);self.assertEqual((restored/png.name).read_bytes(),png.read_bytes())
   with self.assertRaises(ValueError):common.checkpoint(local,remote,'wrong-source',360,640)
   (remote/png.name).write_bytes(b'bad');perf.restore_job(remote,root/'after-corruption','unit-fixture',360,640);self.assertEqual(json.loads((root/'after-corruption/profile.json').read_text())['frames'],{})
 def test_no_gpu_sample_is_not_zero_utilization(self):
  with tempfile.TemporaryDirectory() as d,patch('perf_common.shutil.which',return_value=None):
   monitor=common.Telemetry(pathlib.Path(d)/'gpu.jsonl');monitor.poll();self.assertIsNone(monitor.report()['meanUtilizationPercent']);self.assertIsNone(monitor.report()['peakMemoryMiB']);self.assertIn('unavailable',monitor.report()['error'])
 def test_warm_cpu_and_missing_trials_never_claim_t4_speedup(self):
  with tempfile.TemporaryDirectory() as d:
   folder=pathlib.Path(d);r=dict(status='passed',wallSeconds=20,frames=30,coldRun=True,actualT4Rendering=False)
   for gpu,cold in [(False,True),(True,False)]:
    rr={**r,'actualT4Rendering':gpu,'coldRun':cold};report=perf.summarize(folder,[],{'baseline-current':rr,'scratch-persistent':rr});self.assertFalse(report['fullEpisodeRerenderRecommended']);self.assertTrue(all(x['measuredSpeedRatio'] is None for x in report['estimates']))
 def test_cycles_log_labels_nested_approximate_scope(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'log';p.write_text('Fra:1 | Time:00:01.00 | Updating Scene\nFra:1 | Time:00:02.50 | Sample 1/48\nFra:1 | Time:00:05.00 | Denoising\n');r=perf.cycles_stages(p);self.assertEqual(r['approximateProgressSeconds']['geometry-sync-bvh'],1.5);self.assertEqual(r['approximateProgressSeconds']['sampling'],2.5);offset=p.stat().st_size;p.write_text(p.read_text()+'New warm run, no Cycles frames\n');self.assertEqual(perf.cycles_stages(p,offset)['approximateProgressSeconds'],{})
 def test_notebook_new_controls_compile_and_standalone_is_preserved(self):
  notebook=json.loads((perf.ROOT/'remotion/blender/Destiny-Studio-Colab-Pro.ipynb').read_text());texts=[''.join(c['source']) for c in notebook['cells']]
  for i,c in enumerate(notebook['cells']):
   if c['cell_type']=='code':compile(''.join(c['source']),f'cell-{i}','exec')
  all_text='\n'.join(texts)
  for text in ['Render Complete Atheon Episode','P1. Plan','Q4. Assemble','first_scene_reviewed','paired_benchmark_reviewed','prepared_pilot_only']:self.assertIn(text,all_text)
if __name__=='__main__':unittest.main()
