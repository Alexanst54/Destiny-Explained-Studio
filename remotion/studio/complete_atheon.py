"""Prepared Atheon package -> resumable Drive scene frames -> one Remotion episode.

No TTS regeneration, no Actions, no model changes. Every production frame is rendered;
no still-frame repetition, audio retiming, or narration truncation is used.
"""
import argparse,array,contextlib,fcntl,hashlib,json,math,os,shutil,signal,subprocess,sys,tempfile,time,wave
from pathlib import Path
from production import ROOT,atomic_json,sha,verify,validate
from pilot import check_script,scene_config,timed_scene,subtitle_text
from universal.cache import source_hashes,valid_png,fingerprint
from universal.request import request

PACKAGE=ROOT/'episodes/atheon-explained-en'
TOTAL_FRAMES=2672
FPS=30
RESOLUTIONS={'Fast 360×640':(360,640),'540×960':(540,960),'720×1280':(720,1280),'1080×1920':(1080,1920)}
SOURCE_FILES=['complete_atheon.py','device_probe.py','complete-index.tsx','episode_timeline.ts','production.py','pilot.py','captions.ts']

def run_task(cmd,log,progress=None):
 """SIGINT lets the existing renderer reap its separately-sessioned Blender worker."""
 log=Path(log);log.parent.mkdir(parents=True,exist_ok=True)
 with log.open('a') as stream:
  proc=subprocess.Popen([str(x) for x in cmd],cwd=ROOT/'remotion',stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
  try:
   while proc.poll() is None:
    if progress:progress()
    time.sleep(2)
  except BaseException:
   # Snapshot only descendants of our own child, so escalation cannot hit other jobs.
   rows=subprocess.run(['ps','-eo','pid=,ppid=,pgid='],capture_output=True,text=True,check=False).stdout.splitlines();tree=[];owned={proc.pid}
   for _ in range(10):
    for line in rows:
     if len(line.split())!=3:continue
     pid,ppid,pgid=map(int,line.split())
     if ppid in owned and pid not in owned:owned.add(pid);tree.append((pid,pgid))
   try:os.killpg(proc.pid,signal.SIGINT)
   except ProcessLookupError:pass
   try:proc.wait(timeout=30)
   except subprocess.TimeoutExpired:
    for pid,pgid in reversed(tree):
     if pgid!=os.getpgrp():
      try:os.killpg(pgid,signal.SIGKILL)
      except ProcessLookupError:pass
    try:os.killpg(proc.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    proc.wait()
   raise
  if proc.returncode:raise RuntimeError(f'Command failed ({proc.returncode}); see {log}. Resume the same action after correcting the cause.')

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
def read(path):return json.loads(Path(path).read_text())

def load_package(package=PACKAGE):
 package=Path(package);script=check_script(read(package/'script.json'));assets=package/'audio-evidence';proof=read(assets/'evidence.json')
 if proof['fullEpisodeRendered'] or proof['gpuValidated']:raise ValueError('Unexpected prepared evidence status.')
 for relative,value in proof['files'].items():
  path=(assets/relative).resolve()
  if not path.is_relative_to(assets.resolve()) or sha(path)!=value:raise ValueError('Prepared pilot asset corrupt: '+relative)
 if read(assets/'script-lock.json')['scriptSha256']!=sha(package/'script.json'):raise ValueError('Reviewed script differs from prepared narration.')
 timing=read(assets/'timing.json');expected_start=0;scenes=[]
 if len(timing['scenes'])!=6 or timing['durationFrames']!=TOTAL_FRAMES or timing['format']!=script['format']:raise ValueError('Prepared episode timing changed.')
 for scene,record in zip(script['scenes'],timing['scenes']):
  speech=read(assets/scene['id']/'speech.json');audio=assets/scene['id']/'speech.wav'
  if sha(audio)!=speech['sha256'] or speech['locale']!='en-US' or speech['voice']!='af_heart' or speech['kokoro']['speed']!=1.0:raise ValueError('Narration identity mismatch.')
  with wave.open(str(audio)) as wav:
   if (wav.getframerate(),wav.getnchannels(),wav.getsampwidth())!=(24000,1,2):raise ValueError('Unexpected original PCM format.')
   seconds=wav.getnframes()/24000;pcm=array.array('h',wav.readframes(wav.getnframes()))
  if abs(seconds-speech['seconds'])>1/24000 or not pcm or max(abs(x) for x in pcm)<32:raise ValueError('Silent/incorrect original narration.')
  if [w['text'] for w in speech['words']]!=scene['narration'].split():raise ValueError('Prepared words differ from reviewed English script.')
  expected=timed_scene(scene,speech,FPS,expected_start)
  if record!=expected:raise ValueError('Scene timing/word offsets changed: '+scene['id'])
  previous=0
  for word in speech['words']:
   if word['start']<previous-1e-6 or word['end']>seconds:raise ValueError('Overlapping/out-of-range subtitles.')
   previous=word['end']
  scenes.append(dict(scene=scene,timing=record,speech=speech,audio=str(audio)))
  expected_start+=record['durationFrames']
 if expected_start!=TOTAL_FRAMES or abs(timing['durationSeconds']-TOTAL_FRAMES/FPS)>1e-6:raise ValueError('Episode is not the measured 2672-frame plan.')
 if (assets/'subtitles.en.srt').read_text()!=subtitle_text(timing['scenes']):raise ValueError('English subtitle file differs from actual word timings.')
 return dict(script=script,timing=timing,scenes=scenes,assetsSha256=digest(proof),scriptSha256=sha(package/'script.json'),package=str(package.resolve()))

def settings(width=360,height=640,quality='balanced'):
 if type(width)!=int or type(height)!=int or width*16!=height*9:raise ValueError('Choose a true 9:16 resolution.')
 if width<320 or width>1080 or height>1920 or width%2 or height%2:raise ValueError('Unsupported/even 9:16 dimensions required.')
 if quality not in ['draft','balanced','cinematic']:raise ValueError('Unknown quality.')
 return dict(width=width,height=height,quality=quality,fps=FPS,lod=0,frames=TOTAL_FRAMES,duration=TOTAL_FRAMES/FPS)

def configs(package,options):
 result=[]
 for item in package['scenes']:
  c=scene_config(package['script'],item['scene'],item['timing']['durationFrames']/FPS)
  c.update(width=options['width'],height=options['height'],quality=options['quality']);result.append(validate(c))
 return result

def software(blender,node,chrome=None):
 binary=shutil.which(str(blender));node_binary=shutil.which(str(node))
 if not binary or not node_binary or not shutil.which('ffmpeg') or not shutil.which('ffprobe'):raise ValueError('Run notebook installation first: Blender, Node, ffmpeg/ffprobe required.')
 binary=str(Path(binary).resolve());node_binary=str(Path(node_binary).resolve())
 version=subprocess.check_output([binary,'--version'],text=True,timeout=30)
 nv=subprocess.check_output([node_binary,'--version'],text=True,timeout=15).strip()
 if not version.startswith('Blender 4.3.2') or nv!='v22.23.4':raise ValueError('Use the notebook-pinned Blender 4.3.2 and Node 22.23.4 for reproducible resume.')
 if not (ROOT/'remotion/node_modules/@remotion/cli/remotion-cli.js').exists():raise ValueError('npm ci has not completed.')
 subprocess.run([node_binary,'-e',"for (const m of ['remotion','@remotion/renderer','react']) require(m); require.resolve('@remotion/cli');"],cwd=ROOT/'remotion',check=True,timeout=20)
 candidates=[Path(chrome)] if chrome else list((ROOT/'remotion/node_modules/.remotion/chrome-headless-shell').rglob('chrome-headless-shell'))
 browser=next((p for p in candidates if p.is_file() and os.access(p,os.X_OK)),None)
 if not browser:raise ValueError('Remotion browser missing. Run the notebook installation/browser ensure cell.')
 browser_version=subprocess.check_output([str(browser),'--version'],stderr=subprocess.STDOUT,text=True,timeout=20).strip()
 for name in ['ffmpeg','ffprobe']:subprocess.run([name,'-version'],stdout=subprocess.DEVNULL,check=True,timeout=15)
 return dict(blender=binary,node=node_binary,blenderVersion=version,nodeVersion=nv,browserVersion=browser_version)

def probe(folder,tools):
 path=folder/'reports/device.json';path.parent.mkdir(parents=True,exist_ok=True)
 with (folder/'logs/device-probe.log').open('a') as log:
  subprocess.run([tools['blender'],'--background','--factory-startup','--python-exit-code','1','--python',str(Path(__file__).with_name('device_probe.py')),'--',str(path)],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=90)
 info=read(path)
 print('Detected Cycles device (probe, not a rendered GPU benchmark): '+json.dumps(info),flush=True)
 return info

def reserve_bytes(options,remaining):
 # Conservative uncompressed RGB PNG bound plus export/log allowance, not a promised size.
 return math.ceil(options['width']*options['height']*3*remaining*1.08)+512*1024**2

def check_space(folder,options):
 recorded=0
 for p in (folder/'public/scenes').glob('*/frames/chunk-*/progress.json'):
  try:
   r=read(p)
   recorded+=sum(1 for f in r.get('frames',{}).values() if (p.parent/f['file']).is_file())
  except (OSError,KeyError,ValueError):pass
 recorded=min(TOTAL_FRAMES,recorded);need=reserve_bytes(options,TOTAL_FRAMES-recorded)
 free=shutil.disk_usage(folder).free;local_free=shutil.disk_usage('/tmp').free
 local_need=reserve_bytes(options,TOTAL_FRAMES)+512*1024**2
 result=dict(mountedDriveFreeBytes=free,localFreeBytes=local_free,conservativeDriveReserveBytes=need,conservativeLocalReserveBytes=local_need,recordedFramesForEstimateOnly=recorded,remoteDriveQuotaVerified=False)
 if free<need or local_free<local_need:raise ValueError('Not enough reported free space for conservative cache/export reserve. Choose a smaller resolution/new folder or free space. '+json.dumps(result))
 print('Space check: '+json.dumps(result)+' (Drive mount may not expose actual remote quota; verify Drive storage).',flush=True)
 return result

def source_identity(package,options,tools):
 files={str((Path(__file__).parent/name).relative_to(ROOT)):sha(Path(__file__).parent/name) for name in SOURCE_FILES}
 files['remotion/package-lock.json']=sha(ROOT/'remotion/package-lock.json')
 return dict(kind='complete-atheon-v1',options=options,pilotAssetsSha256=package['assetsSha256'],scriptSha256=package['scriptSha256'],sources=files,rendererSources=source_hashes(),blenderVersion=tools['blenderVersion'],nodeVersion=tools['nodeVersion'])

def bind_project(folder,identity):
 path=folder/'project.json'
 if path.exists():
  old=read(path)
  if old.get('identity')!=identity:raise ValueError('Different source/pilot/settings. Restore the saved commit or choose a new Drive folder; existing content is preserved.')
  return old
 for entry in folder.iterdir():
  if entry.name=='episode.lock':continue
  if entry.name=='logs' and entry.is_dir() and not any(entry.iterdir()):continue
  if entry.name=='reports' and entry.is_dir() and all(p.name=='activity.json' for p in entry.iterdir()):continue
  raise ValueError('Use a new empty episode folder; existing unrelated content will not be overwritten.')
 commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
 tracked=list(identity['sources'])+list(identity['rendererSources'])+['episodes/atheon-explained-en']
 dirty=bool(subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain','--',*tracked],text=True).strip())
 if dirty:raise ValueError('Production sources are modified/uncommitted. Use the clean branch/commit from the notebook, not an edited checkout.')
 project=dict(sourceCommit=commit,sourceDirty=False,identity=identity,fingerprint=digest(identity));atomic_json(path,project);return project

def preflight(folder,options,blender,node,allow_cpu=False,require_gpu=True,chrome=None):
 folder=Path(folder).expanduser().resolve();folder.mkdir(parents=True,exist_ok=True);(folder/'logs').mkdir(exist_ok=True)
 package=load_package();tools=software(blender,node,chrome);project=bind_project(folder,source_identity(package,options,tools));space=check_space(folder,options)
 with tempfile.NamedTemporaryFile(dir=folder,prefix='.preflight-',mode='w') as test:test.write('Drive write check')
 device=probe(folder,tools)
 gpu=device['selected']=='GPU' and device.get('backend') in ['OPTIX','CUDA']
 if not gpu:
  print('WARNING: no NVIDIA OPTIX/CUDA selected; CPU rendering may take many hours.',flush=True)
  if require_gpu and not allow_cpu:raise ValueError('Select a Colab GPU runtime, reconnect and prepare again. CPU is not enabled for this time-conscious episode run.')
 report=dict(status='passed',sourceCommit=project['sourceCommit'],fingerprint=project['fingerprint'],space=space,detectedDevice=device,renderingGpuValidated=False,gpuReadyForSceneRendering=gpu,preparedSpeechReused=True,frames=TOTAL_FRAMES,seconds=TOTAL_FRAMES/FPS,options=options)
 atomic_json(folder/'reports/preflight.json',report)
 return package,tools,project

def install_inputs(folder,package,options):
 (folder/'inputs').mkdir(exist_ok=True)
 for name in ['script.json','lore-sources.json']:shutil.copyfile(Path(package['package'])/name,folder/'inputs'/name)
 for name in ['timing.json','evidence.json']:shutil.copyfile(Path(package['package'])/'audio-evidence'/name,folder/'inputs'/name)
 shutil.copyfile(Path(package['package'])/'audio-evidence/subtitles.en.srt',folder/'subtitles.en.srt')
 for item,c in zip(package['scenes'],configs(package,options)):
  scene_id=item['scene']['id'];public=folder/'public/scenes'/scene_id;public.mkdir(parents=True,exist_ok=True)
  audio=public/'speech.wav'
  if not audio.exists() or sha(audio)!=item['speech']['sha256']:shutil.copyfile(item['audio'],audio)
  state=folder/'scenes'/scene_id;state.mkdir(parents=True,exist_ok=True)
  atomic_json(state/'selection.json',c);atomic_json(state/'speech.json',item['speech'])

@contextlib.contextmanager
def locked(folder):
 folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=True)
 with (folder/'episode.lock').open('a') as stream:
  try:fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise ValueError('This episode is already running. Do not launch concurrent render/assemble cells.')
  yield folder

def chunk_specs(config):
 return [dict(start=n,frames=min(120,config['frames']-n)) for n in range(0,config['frames'],120)]

def chunk_folder(folder,scene_id,part):return folder/'public/scenes'/scene_id/'frames'/f"chunk-{part['start']:06d}"
def expected_request(config,part):
 return request(config['boss'],quality=config['quality'],lod=0,frames=part['frames'],fps=FPS,width=config['width'],height=config['height'],start_frame=part['start'],animation=config['animation'],view=config['camera'],arena=config['arena'])

def trusted_chunk(out,config,part,tools):
 try:
  r=read(out/'progress.json');wanted=expected_request(config,part)
  expected=hashlib.sha256((fingerprint(wanted,'auto',3)+tools['blenderVersion']).encode()).hexdigest()
  if r['status']!='success' or r['request']!=wanted or r['fingerprint']!=expected or set(r['frames'])!={str(i) for i in range(part['frames'])}:return None
  for i in range(part['frames']):
   f=r['frames'][str(i)]
   if f['sourceFrame']!=part['start']+i or f['file']!=f'frame-{i:04d}.png' or not valid_png(out/f['file'],config['width'],config['height'],f['sha256']):return None
  return r
 except (OSError,ValueError,KeyError,TypeError):return None

def progress_callback(out,config,part,episode_done,scene_index):
 def update():
  try:r=read(out/'progress.json')
  except (OSError,ValueError):return
  n=len(r.get('frames',{}));device=r.get('configuration',{});samples=[f['seconds'] for f in r.get('frames',{}).values() if f.get('seconds',0)>0];total=episode_done+part['start']+n
  eta=f" | rough ETA {(TOTAL_FRAMES-total)*(sum(samples)/len(samples))/60:.1f} min" if samples else ''
  text=f"Scene {scene_index+1}/6: {part['start']+n}/{config['frames']} | episode {total}/{TOTAL_FRAMES} | {device.get('selected','detecting')} {device.get('backend') or ''}{eta}"
  if device.get('selected')=='CPU':text+=' | WARNING CPU fallback'
  if text!=getattr(update,'last',None):print(text,flush=True);update.last=text
 return update

def render_scene(folder,item,config,tools,scene_index,episode_done):
 scene_id=item['scene']['id'];reused=0;new=0;reports=[]
 state=folder/'scenes'/scene_id
 atomic_json(state/'status.json',dict(status='running',sceneId=scene_id))
 for part in chunk_specs(config):
  out=chunk_folder(folder,scene_id,part);out.parent.mkdir(parents=True,exist_ok=True)
  report=trusted_chunk(out,config,part,tools)
  if report:reused+=part['frames'];print(f"Reused {scene_id} frames {part['start']}–{part['start']+part['frames']-1}",flush=True)
  else:
   # Never delete unknown/partial files. Only a manifest-bound directory can resume.
   if out.exists() and not (out/'progress.json').exists():
    archived=folder/'recovery'/f'{scene_id}-{part["start"]}-{time.time_ns()}';archived.parent.mkdir(exist_ok=True);out.rename(archived)
   cmd=[sys.executable,ROOT/'remotion/blender/render_universal.py',config['boss'],out,'--blender',tools['blender'],'--device','auto','--threads',3,'--frames',part['frames'],'--start-frame',part['start'],'--fps',FPS,'--width',config['width'],'--height',config['height'],'--quality',config['quality'],'--lod',0,'--view',config['camera'],'--animation',config['animation'],'--arena',config['arena'],'--timeout',7200]
   if out.exists():cmd+=['--resume']
   run_task(cmd,folder/'logs'/f'{scene_id}.log',progress_callback(out,config,part,episode_done,scene_index))
   report=trusted_chunk(out,config,part,tools)
   if not report:raise ValueError('Incomplete/untrusted rendered chunk: '+str(out))
   reused+=report['cacheHits'];new+=report['renderedThisRun']
  reports.append(report)
 status=dict(status='complete',sceneId=scene_id,frames=config['frames'],framesReusedThisInvocation=reused,newFramesThisInvocation=new,preparedSpeechSha256=item['speech']['sha256'],frameSequenceSha256=digest([r['frames'][str(i)]['sha256'] for r in reports for i in range(len(r['frames']))]))
 atomic_json(state/'status.json',status);return status

def render_scenes(folder,package,options,tools,only=None):
 result=[];done=0
 for index,(item,c) in enumerate(zip(package['scenes'],configs(package,options))):
  if only is None or item['scene']['id'] in only:result.append(render_scene(folder,item,c,tools,index,done))
  done+=c['frames']
 atomic_json(folder/'reports/last-render.json',dict(status='passed',scenes=result));return result

def validate_frames(folder,package,options,tools,smoke=False):
 result=[];gpu_frames=0;backends={};frame_hashes=[];all_t4=True
 if sha(folder/'subtitles.en.srt')!=sha(Path(package['package'])/'audio-evidence/subtitles.en.srt'):raise ValueError('Original subtitle file changed; prepare again.')
 for item,c in zip(package['scenes'],configs(package,options)):
  if smoke and result:break
  for part in chunk_specs(c):
   out=chunk_folder(folder,item['scene']['id'],part);r=trusted_chunk(out,c,part,tools)
   if not r:raise ValueError('Missing/corrupt scene frames. Run Render all scenes to resume: '+item['scene']['id'])
   for i in range(part['frames']):
    f=r['frames'][str(i)];d=f.get('device',r.get('configuration',{}));key=str((d.get('selected'),d.get('backend'),d.get('devices')));backends[key]=backends.get(key,0)+1;gpu_frames+=d.get('selected')=='GPU';frame_hashes.append(f['sha256']);all_t4=all_t4 and d.get('selected')=='GPU' and d.get('backend') in ['OPTIX','CUDA'] and any('T4' in n for n in d.get('devices',[]))
  audio=folder/'public/scenes'/item['scene']['id']/'speech.wav'
  if sha(audio)!=item['speech']['sha256']:raise ValueError('Original speech changed; prepare again.')
  result.append(item)
 if not frame_hashes:raise ValueError('No validated frames.')
 return result,dict(t4RenderingValidated=all_t4,gpuFrames=gpu_frames,totalFrames=len(frame_hashes),actualFrameBackends=backends,allFramesGPU=gpu_frames==len(frame_hashes),frameSequenceSha256=digest(frame_hashes))

def episode_props(package,options,smoke=False):
 scenes=[]
 for index,item in enumerate(package['scenes'][:1] if smoke else package['scenes']):
  t=item['timing'];scenes.append(dict(id=item['scene']['id'],label=item['scene']['label'],title=package['script']['title'] if index==0 else '',startFrame=t['startFrame'],durationFrames=t['durationFrames'],words=item['speech']['words']))
 return dict(width=options['width'],height=options['height'],fps=FPS,frames=sum(s['durationFrames'] for s in scenes),scenes=scenes)

def verify_audio_alignment(video,items):
 """Check every complete source utterance survives at its measured timeline position."""
 pcm=array.array('h',subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-map','0:a:0','-ac','1','-ar','24000','-f','s16le','-']))
 block=240
 def envelope(samples):return [math.sqrt(sum(x*x for x in samples[n:n+block])/len(samples[n:n+block])) for n in range(0,len(samples),block)]
 decoded=envelope(pcm);results=[]
 for item in items:
  with wave.open(item['audio']) as wav:original=array.array('h',wav.readframes(wav.getnframes()))
  original=envelope(original);start=round(item['timing']['startFrame']/FPS*100);best=(-1,0)
  for lag in range(-5,6):
   pairs=[(value,decoded[start+n+lag]) for n,value in enumerate(original) if 0<=start+n+lag<len(decoded)]
   aa=sum(a*a for a,b in pairs);bb=sum(b*b for a,b in pairs);score=sum(a*b for a,b in pairs)/math.sqrt(aa*bb) if aa and bb else 0
   if score>best[0]:best=(score,lag)
  if best[0]<.9:raise ValueError('Final audio does not match original speech/timeline: '+item['scene']['id'])
  results.append(dict(sceneId=item['scene']['id'],envelopeCorrelation=best[0],bestLagMilliseconds=best[1]*10))
 return dict(method='10ms PCM RMS envelopes; original full speech; +/-50ms search',scenes=results)

def assemble(folder,package,options,tools,project,smoke=False,chrome=None):
 selected,device_report=validate_frames(folder,package,options,tools,smoke);props=episode_props(package,options,smoke)
 if not smoke and (props['frames']!=TOTAL_FRAMES or len(props['scenes'])!=6):raise ValueError('A complete export must contain all six scenes and 2672 frames.')
 stem='atheon-smoke' if smoke else 'atheon-episode-01';output=folder/(stem+'.mp4');report_path=folder/(stem+'.validation.json');expected=dict(width=props['width'],height=props['height'],fps=FPS,frames=props['frames'],duration=props['frames']/FPS)
 if output.exists() and report_path.exists():
  old=read(report_path)
  if old.get('status')=='passed' and old.get('fingerprint')==project['fingerprint'] and old.get('sha256')==sha(output):
   verify(output,expected);verify_audio_alignment(output,selected);print('Reused validated export: '+str(output),flush=True);return old
 atomic_json(report_path,dict(status='running',phase='smoke' if smoke else 'episode'))
 path=folder/(stem+'-props.json');atomic_json(path,props);pending=folder/(stem+'.pending.mp4')
 cmd=[tools['node'],ROOT/'remotion/node_modules/@remotion/cli/remotion-cli.js','render',ROOT/'remotion/studio/complete-index.tsx','CompleteAtheonEpisode',pending,'--props',path,'--public-dir',folder/'public','--codec','h264','--audio-codec','aac','--pixel-format','yuv420p','--image-format','png','--color-space','bt709','--concurrency',1]
 if chrome:cmd+=['--browser-executable',chrome]
 try:
  run_task(cmd,folder/'logs'/(stem+'-remotion.log'));proof=verify(pending,expected);pending.replace(output)
  audio_alignment=verify_audio_alignment(output,selected)
  proof.update(audioAlignment=audio_alignment,subtitleTimingValidated=True,subtitlesSha256=sha(folder/'subtitles.en.srt'),status='passed',phase='smoke' if smoke else 'episode',fingerprint=project['fingerprint'],sourceCommit=project['sourceCommit'],sha256=sha(output),scenes=[s['id'] for s in props['scenes']],language='en-US',voice='af_heart',narrationSpeed=1.0,subtitlesValidated=True,subtitleWords=sum(len(s['words']) for s in props['scenes']),originalSpeechSha256={i['scene']['id']:i['speech']['sha256'] for i in selected},deviceReport=device_report,fullEpisodeRendered=not smoke)
  atomic_json(report_path,proof);print('Saved '+str(output),flush=True);return proof
 except BaseException as error:
  atomic_json(report_path,dict(status='failed',error=str(error)));raise

def require_smoke(folder,project,package,options):
 path=folder/'atheon-smoke.validation.json';video=folder/'atheon-smoke.mp4'
 if not path.exists() or not video.exists():raise ValueError('Run and inspect the first-scene smoke-test before Render all scenes.')
 r=read(path);frames=package['scenes'][0]['timing']['durationFrames']
 if r.get('status')!='passed' or r.get('phase')!='smoke' or r.get('fingerprint')!=project['fingerprint'] or r.get('sha256')!=sha(video):raise ValueError('Smoke is stale/corrupt. Run smoke-test again.')
 verify(video,dict(width=options['width'],height=options['height'],fps=FPS,frames=frames,duration=frames/FPS))

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['prepare','smoke','render','assemble','validate']);p.add_argument('output');p.add_argument('--width',type=int,default=360);p.add_argument('--height',type=int,default=640);p.add_argument('--quality',choices=['draft','balanced','cinematic'],default='balanced');p.add_argument('--blender',default='blender');p.add_argument('--node',default='node');p.add_argument('--chrome');p.add_argument('--allow-cpu',action='store_true');p.add_argument('--scene');a=p.parse_args()
 if a.chrome:a.chrome=str(Path(a.chrome).resolve())
 opts=settings(a.width,a.height,a.quality)
 with locked(a.output) as folder:
  try:
   package,tools,project=preflight(folder,opts,a.blender,a.node,a.allow_cpu,require_gpu=a.action in ['smoke','render'],chrome=a.chrome);install_inputs(folder,package,opts)
   atomic_json(folder/'reports/activity.json',dict(status='running',action=a.action))
   if a.action=='smoke':
    render_scenes(folder,package,opts,tools,[package['scenes'][0]['scene']['id']]);assemble(folder,package,opts,tools,project,True,a.chrome)
   elif a.action=='render':
    require_smoke(folder,project,package,opts)
    if a.scene and a.scene not in [i['scene']['id'] for i in package['scenes']]:raise ValueError('Unknown scene ID.')
    render_scenes(folder,package,opts,tools,[a.scene] if a.scene else None)
   elif a.action=='assemble':require_smoke(folder,project,package,opts);assemble(folder,package,opts,tools,project,False,a.chrome)
   elif a.action=='validate':
    output=folder/'atheon-episode-01.mp4';r=read(folder/'atheon-episode-01.validation.json')
    if r.get('status')!='passed' or r.get('fingerprint')!=project['fingerprint'] or r.get('sha256')!=sha(output):raise ValueError('Final report/video is stale or incomplete; assemble again.')
    verify(output,opts);validate_frames(folder,package,opts,tools);verify_audio_alignment(output,package['scenes']);print('Validated complete 2672-frame English episode.',flush=True)
   atomic_json(folder/'reports/activity.json',dict(status='complete',action=a.action))
  except BaseException as error:
   (folder/'reports').mkdir(exist_ok=True);atomic_json(folder/'reports/activity.json',dict(status='failed',action=a.action,error=str(error)));raise
if __name__=='__main__':main()
