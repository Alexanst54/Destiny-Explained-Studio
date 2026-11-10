"""Controller tests use explicitly synthetic PNG fixtures, never claimed as pilot renders."""
import array,hashlib,json,math,os,pathlib,signal,struct,subprocess,sys,tempfile,time,unittest,wave,zlib
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).parent))
import complete_atheon as ep

def fixture_png(width,height,value):
 def chunk(kind,payload):return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff)
 data=(b'\0'+bytes([value,value,value])*width)*height
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(data))+chunk(b'IEND',b'')

class CompleteAtheon(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.package=ep.load_package();cls.options=ep.settings();cls.tools=dict(blender='fixture-only',node='node',blenderVersion='fixture version\n',allow_cpu=True)
 def test_original_package_timing_voice_and_scene_specific_controls(self):
  p=self.package;configs=ep.configs(p,self.options)
  self.assertEqual(len(p['scenes']),6);self.assertEqual(sum(c['frames'] for c in configs),2672)
  self.assertAlmostEqual(sum(c['duration'] for c in configs),2672/30)
  for item,c in zip(p['scenes'],configs):
   self.assertEqual((c['width'],c['height'],c['quality']),(360,640,'balanced'))
   self.assertEqual((c['boss'],c['arena'],c['animation'],c['camera']),('boss-atheon','arena-glass-throne',item['scene']['animation'],item['scene']['camera']))
   self.assertEqual(c['language'],'en-US');self.assertEqual(c['voice'],'af_heart');self.assertEqual(c['narration'],item['scene']['narration'])
 def test_chunks_and_projection_paths_have_no_gaps_or_duplicate_frames(self):
  for c in ep.configs(self.package,self.options):
   parts=ep.chunk_specs(c);self.assertTrue(all(1<=p['frames']<=120 for p in parts))
   self.assertEqual([i for p in parts for i in range(p['start'],p['start']+p['frames'])],list(range(c['frames'])))
 def test_reject_corrupt_original_voice(self):
  with tempfile.TemporaryDirectory() as tmp:
   import shutil
   dest=pathlib.Path(tmp)/'pilot';shutil.copytree(ep.PACKAGE,dest)
   (dest/'audio-evidence/01-hook/speech.wav').write_bytes(b'corrupt')
   with self.assertRaises(ValueError):ep.load_package(dest)
 def test_project_identity_preserves_existing_content_and_rejects_changed_settings(self):
  with tempfile.TemporaryDirectory() as tmp:
   folder=pathlib.Path(tmp);(folder/'notes.txt').write_text('keep me')
   with self.assertRaises(ValueError):ep.bind_project(folder,dict(sources={},rendererSources={}))
   self.assertEqual((folder/'notes.txt').read_text(),'keep me')
  with tempfile.TemporaryDirectory() as tmp:
   folder=pathlib.Path(tmp);identity=dict(sources={},rendererSources={},options=self.options)
   with patch.object(ep.subprocess,'check_output',side_effect=['a'*40,'']):first=ep.bind_project(folder,identity)
   self.assertEqual(ep.bind_project(folder,identity),first)
   with self.assertRaises(ValueError):ep.bind_project(folder,{**identity,'options':ep.settings(540,960)})
 def test_disk_preflight_checks_both_drive_and_local_space(self):
  with tempfile.TemporaryDirectory() as tmp:
   with patch.object(ep.shutil,'disk_usage',return_value=SimpleNamespace(free=0)):
    with self.assertRaises(ValueError):ep.check_space(pathlib.Path(tmp),self.options)
   with patch.object(ep.shutil,'disk_usage',return_value=SimpleNamespace(free=100*1024**3)):
    r=ep.check_space(pathlib.Path(tmp),self.options);self.assertFalse(r['remoteDriveQuotaVerified']);self.assertGreater(r['conservativeDriveReserveBytes'],1024**3)
 def test_interrupted_scene_warm_resume_and_corrupt_frame_repair(self):
  # This fake worker tests orchestration/cache decisions; it is not Blender evidence.
  with tempfile.TemporaryDirectory() as tmp:
   folder=pathlib.Path(tmp);item=self.package['scenes'][0];c=ep.configs(self.package,self.options)[0];c={**c,'frames':3,'duration':.1};state=folder/'scenes'/item['scene']['id'];state.mkdir(parents=True)
   part=dict(start=0,frames=3);out=ep.chunk_folder(folder,item['scene']['id'],part);interrupted=[True]
   def worker(cmd,log,progress):
    out.mkdir(parents=True,exist_ok=True);r=ep.expected_request(c,part);expected=hashlib.sha256((ep.fingerprint(r,'auto',3)+self.tools['blenderVersion']).encode()).hexdigest();old=ep.read(out/'progress.json') if (out/'progress.json').exists() else dict(frames={});frames={};hits=0;new=0
    for i in range(2 if interrupted[0] else 3):
     path=out/f'frame-{i:04d}.png';f=old['frames'].get(str(i))
     if f and ep.valid_png(path,c['width'],c['height'],f['sha256']):hits+=1
     else:path.write_bytes(fixture_png(c['width'],c['height'],i+1));new+=1
     frames[str(i)]=dict(file=path.name,sourceFrame=i,sha256=ep.sha(path),seconds=.1,device=dict(selected='CPU',backend=None,devices=[]))
    ep.atomic_json(out/'progress.json',dict(status='running' if interrupted[0] else 'success',request=r,fingerprint=expected,frames=frames,cacheHits=hits,renderedThisRun=new,configuration=dict(selected='CPU')))
    if interrupted[0]:interrupted[0]=False;raise RuntimeError('simulated interrupted worker')
   with patch.object(ep,'run_task',side_effect=worker):
    with self.assertRaises(RuntimeError):ep.render_scene(folder,item,c,self.tools,0,0)
    resumed=ep.render_scene(folder,item,c,self.tools,0,0);self.assertEqual((resumed['framesReusedThisInvocation'],resumed['newFramesThisInvocation']),(2,1))
   finished=ep.read(out/'progress.json');finished['status']='running';ep.atomic_json(out/'progress.json',finished)
   with patch.object(ep,'run_task') as launch:
    warm=ep.render_scene(folder,item,c,{**self.tools,'allow_cpu':False,'device':dict(selected='CPU')},0,0);launch.assert_not_called();self.assertEqual(warm['framesReusedThisInvocation'],3)
   before=ep.sha(out/'frame-0000.png');(out/'frame-0001.png').write_bytes(b'bad')
   with self.assertRaises(ValueError):ep.render_scene(folder,item,c,{**self.tools,'allow_cpu':False,'device':dict(selected='CPU')},0,0)
   with patch.object(ep,'run_task',side_effect=worker):fixed=ep.render_scene(folder,item,c,self.tools,0,0)
   self.assertEqual((fixed['framesReusedThisInvocation'],fixed['newFramesThisInvocation']),(2,1));self.assertEqual(ep.sha(out/'frame-0000.png'),before)
   wrong=ep.read(out/'progress.json');wrong['request']['binding']['selectionId']='boss-templar';ep.atomic_json(out/'progress.json',wrong);self.assertIsNone(ep.trusted_chunk(out,c,part,self.tools))
 def test_complete_assembly_refuses_missing_scenes_without_starting_remotion(self):
  with tempfile.TemporaryDirectory() as tmp:
   folder=pathlib.Path(tmp);ep.install_inputs(folder,self.package,self.options)
   with patch.object(ep,'run_task') as launch:
    with self.assertRaises(ValueError):ep.assemble(folder,self.package,self.options,self.tools,dict(fingerprint='fixture'))
    launch.assert_not_called()
 def test_original_audio_alignment_accepts_signal_and_rejects_missing_audio(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=pathlib.Path(tmp)/'audio.wav';samples=array.array('h',[int(3000*math.sin(n*.14)) for n in range(7200)])
   with wave.open(str(path),'wb') as wav:wav.setparams((1,2,24000,0,'NONE','not compressed'));wav.writeframes(samples.tobytes())
   item=dict(scene=dict(id='fixture'),timing=dict(startFrame=0),audio=str(path))
   with patch.object(ep.subprocess,'check_output',return_value=samples.tobytes()):self.assertGreater(ep.verify_audio_alignment('fixture.mp4',[item])['scenes'][0]['envelopeCorrelation'],.99)
   with patch.object(ep.subprocess,'check_output',return_value=bytes(len(samples)*2)):
    with self.assertRaises(ValueError):ep.verify_audio_alignment('fixture.mp4',[item])
 def test_interrupt_allows_child_controller_to_reap_separate_worker_session(self):
  with tempfile.TemporaryDirectory() as tmp:
   folder=pathlib.Path(tmp);child=folder/'child.py';marker=folder/'sigint';pidfile=folder/'worker.pid'
   child.write_text("import os,signal,subprocess,sys,time\nfrom pathlib import Path\nworker=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'],start_new_session=True)\ndef stop(sig,frame):\n Path(sys.argv[2]).write_text('SIGINT')\n os.killpg(worker.pid,signal.SIGKILL)\n worker.wait(timeout=5)\n raise KeyboardInterrupt\nsignal.signal(signal.SIGINT,stop)\nPath(sys.argv[1]).write_text(str(worker.pid))\nwhile True:time.sleep(.1)\n")
   code="import sys;sys.path.insert(0,sys.argv[1]);from complete_atheon import run_task;run_task([sys.executable,sys.argv[2],sys.argv[3],sys.argv[4]],sys.argv[5])"
   proc=subprocess.Popen([sys.executable,'-c',code,str(pathlib.Path(ep.__file__).parent),str(child),str(pidfile),str(marker),str(folder/'log')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
   worker=None
   try:
    deadline=time.monotonic()+10
    while not pidfile.exists() and time.monotonic()<deadline:time.sleep(.05)
    self.assertTrue(pidfile.exists());worker=int(pidfile.read_text());os.kill(proc.pid,signal.SIGINT);self.assertNotEqual(proc.wait(timeout=10),0);self.assertEqual(marker.read_text(),'SIGINT')
    with self.assertRaises(ProcessLookupError):os.kill(worker,0)
   finally:
    if proc.poll() is None:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
    if worker:
     try:os.killpg(worker,signal.SIGKILL)
     except ProcessLookupError:pass
 def test_notebook_has_separate_complete_controls_and_keeps_standalone_entry(self):
  nb=ep.read(ep.ROOT/'remotion/blender/Destiny-Studio-Colab-Pro.ipynb');text='\n'.join(''.join(c['source']) for c in nb['cells']);self.assertIn('Render Complete Atheon Episode',text);self.assertIn('prepared_pilot_only = False',text);self.assertIn('STUDIO = form(DRIVE_ROOT)',text)
  for action in ['prepare','smoke','render','assemble','validate']:self.assertIn("episode_action('"+action+"')",text)
  for cell in nb['cells']:
   if cell['cell_type']=='code':compile(''.join(cell['source']),'notebook','exec');self.assertEqual(cell['outputs'],[])
