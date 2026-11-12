"""Storage/measurement correctness; synthetic fixtures are not GPU evidence."""
import copy,json,pathlib,sys,tempfile,unittest,zipfile
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'gpu_lab'))
import common as labcommon
from common import CASES,safe_root,run_folder,atomic_json,read,sha,cleanup,archive,restore_zip,jobs,resolved_settings
from reporting import aggregate,compare
from lab import export_configuration

class Lab(unittest.TestCase):
 def test_local_root_rejects_drive_symlinks_and_episode_ancestors(self):
  with tempfile.TemporaryDirectory() as d:
   parent=pathlib.Path(d);root=safe_root(parent/'destiny-gpu-lab',True);self.assertTrue((root/'.destiny-gpu-lab.json').exists())
   with self.assertRaises(ValueError):safe_root('/content/drive/MyDrive/destiny-gpu-lab')
   link=parent/'alias';link.symlink_to(root,target_is_directory=True)
   with self.assertRaises(ValueError):safe_root(link,True)
   (parent/'project.json').write_text('{}')
   with self.assertRaises(ValueError):safe_root(root,True)
 def test_cleanup_is_confined_and_final_outputs_survive(self):
  with tempfile.TemporaryDirectory() as d:
   parent=pathlib.Path(d);root=safe_root(parent/'destiny-gpu-lab',True);run=run_folder(root,'unit');run.mkdir(parents=True);atomic_json(run/'.lab-run.json',{'kind':'destiny-t4-lab-v1'});intermediate=run/'intermediate';intermediate.mkdir();(intermediate/'frame.png').write_bytes(b'fixture');(run/'final').mkdir();(run/'final/report.txt').write_text('keep');outside=parent/'episode.txt';outside.write_text('unchanged');(intermediate/'bad-link').symlink_to(outside)
   with self.assertRaises(ValueError):cleanup(root,run)
   self.assertEqual(outside.read_text(),'unchanged');(intermediate/'bad-link').unlink();self.assertGreater(cleanup(root,run),0);self.assertTrue((run/'final/report.txt').exists());self.assertFalse(intermediate.exists())
 def test_archive_and_restore_only_final_hash_checked_results(self):
  with tempfile.TemporaryDirectory() as d:
   root=safe_root(pathlib.Path(d)/'destiny-gpu-lab',True);run=run_folder(root,'unit');(run/'final').mkdir(parents=True);(run/'final/report.txt').write_text('real fixture, not a benchmark');z=archive(run);restored=restore_zip(root,z,'valid');self.assertEqual((restored/'final/report.txt').read_text(),'real fixture, not a benchmark')
   bad=root/'bad.zip'
   with zipfile.ZipFile(bad,'w') as f:f.writestr('final/../../outside','bad')
   with self.assertRaises(ValueError):restore_zip(root,bad,'invalid')
 def test_representative_shots_and_all_comparisons_are_identical_inputs(self):
  plan=jobs(540,960,3);self.assertEqual([j['id'] for j in plan],['vault-establish','past-gate','mechanism']);self.assertEqual(sum(j['request']['frames'] for j in plan),9)
  for j in plan:self.assertEqual((j['request']['quality'],j['request']['lod'],j['request']['seed'],j['request']['fps']),('balanced',0,42,30))
 def test_settings_only_use_supported_features_and_never_reduce_effects(self):
  caps=dict(defaults=dict(denoiser='OPENIMAGEDENOISE',denoising_use_gpu=False,compositor_device='CPU',compositor_precision='AUTO',use_auto_tile=True),oidnCompiled=True,autoTileAvailable=True,features={})
  alternate,reason=resolved_settings(CASES[3],caps);self.assertIsNone(alternate);self.assertIn('not supported',reason)
  baseline,_=resolved_settings(CASES[0],caps);self.assertEqual(baseline['samples'],48)
  caps['features']={k:dict(supported=True) for k in ['optix-denoiser','oidn-gpu','gpu-compositor']};candidate,_=resolved_settings(CASES[4],caps);self.assertTrue(candidate['denoising_use_gpu']);self.assertEqual(candidate['compositor_precision'],'FULL');self.assertFalse(candidate['use_auto_tile'])
  self.assertTrue(set(candidate).isdisjoint({'max_bounces','volume_step_rate','adaptive_threshold','lights','lod','threads'}))
 def fixture_results(self):
  records=[]
  for trial in [1,2]:
   for case,wall in [('baseline-48',20),('candidate-48',16)]:
    frames={str(i):dict(fixedSceneSignature='same-scene-'+str(i),renderOperationSeconds=wall/3) for i in range(3)}
    records.append(dict(case=case,trial=trial,status='passed',cold=True,actualT4=True,frames=frames,requestedFrames=3,newFrames=3,cacheHits=0,device=dict(backend='OPTIX',id='fixture-gpu'),invocation=dict(exitCode=0,invocationWallSeconds=wall,telemetry=dict(gpuUuids=['fixture-uuid'])),settingsRequested=dict(samples=48)))
  return records
 def test_only_repeated_comparable_cold_t4_trials_can_authorize_review(self):
  plan=dict(mode='standard',repeats=2,cases=[CASES[0],CASES[4]],jobs=[dict(id='mechanism',shotId='fixture',request=dict(frames=3))]);records=self.fixture_results()
  for r in records:
   for f in r['frames'].values():f['shotId']='fixture'
  valid=aggregate(plan,records)[1];self.assertTrue(valid['eligibleForProductionReview']);self.assertEqual(valid['speedRatio'],1.25)
  for field,value in [('cold',False),('actualT4',False),('cpuFallback',True),('oom',True)]:
   altered=copy.deepcopy(records)
   for r in altered:r[field]=value
   self.assertFalse(aggregate(plan,altered)[1]['eligibleForProductionReview'])
  self.assertFalse(aggregate({**plan,'mode':'fast'},records)[1]['eligibleForProductionReview'])
  altered=copy.deepcopy(records);altered[-1]['frames']['0']['fixedSceneSignature']='different';self.assertFalse(aggregate(plan,altered)[1]['sceneIdentityMatchesBaseline'])
 def test_export_requires_explicit_approval_and_valid_cold_temporal_evidence(self):
  with tempfile.TemporaryDirectory() as d:
   folder=pathlib.Path(d);(folder/'final').mkdir();atomic_json(folder/'final/results.json',dict(renderSources={},comparisons=[dict(case='candidate-48',eligibleForProductionReview=False,speedRatio=None)]));atomic_json(folder/'final/visual-metrics.json',{});atomic_json(folder/'final/plan.json',{});archive(folder)
   with self.assertRaises(ValueError):export_configuration(folder,'candidate-48',False)
   with patch('lab.sources',return_value={}):
    with self.assertRaises(ValueError):export_configuration(folder,'candidate-48',True)
 def test_standalone_notebook_does_not_mount_drive_or_install_voices_by_default(self):
  n=read(labcommon.ROOT/'remotion/blender/Destiny-GPU-Optimization-Lab.ipynb');cells=[''.join(c['source']) for c in n['cells']]
  for i,c in enumerate(n['cells']):
   if c['cell_type']=='code':compile(''.join(c['source']),str(i),'exec')
  main='\n'.join(s for s in cells if not s.startswith('# @title OPTIONAL Drive'))
  self.assertNotIn('drive.mount(',main);self.assertNotIn("'npm'",main);self.assertNotIn("'pip'",main)
  for name in ['O1.','O2.','O3.','O4.']:self.assertTrue(any(name in s for s in cells))
if __name__=='__main__':unittest.main()
