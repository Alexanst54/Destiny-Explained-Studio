"""Isolated lab contracts. No production changes, Drive access or voice dependencies."""
import hashlib,json,os,stat,sys,uuid,zipfile,shutil,fcntl,contextlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'remotion/studio'),str(ROOT/'remotion/blender')]
from universal.cache import atomic_json,source_hashes,valid_png

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def sources():
 result=source_hashes()
 for path in list(HERE.glob('*.py'))+[ROOT/'remotion/studio/cinematic_direction.py',ROOT/'remotion/studio/shot_audit.py',ROOT/'remotion/studio/perf_common.py',ROOT/'episodes/atheon-explained-en/audio-evidence/timing.json']:
  result[str(path.relative_to(ROOT))]=sha(path)
 return result

def safe_root(path,cpu_validation=False):
 lexical=Path(os.path.abspath(path));resolved=lexical.resolve()
 if lexical!=resolved or resolved.is_mount():raise ValueError('Lab paths must not contain symlinks or mounts')
 allowed=resolved==Path('/content/destiny-gpu-lab')
 local=cpu_validation and resolved.name=='destiny-gpu-lab' and any(resolved.is_relative_to(p) for p in [Path('/tmp'),Path('/workspace')])
 if not (allowed or local):raise ValueError('Use /content/destiny-gpu-lab; local CPU validation must use a dedicated destiny-gpu-lab directory')
 if any('drive'==p.lower() for p in resolved.parts):raise ValueError('Lab work must never be inside Drive')
 for parent in [resolved,*resolved.parents]:
  if (parent/'project.json').exists():raise ValueError('Existing production project detected; lab will not access it')
 resolved.mkdir(parents=True,exist_ok=True);marker=resolved/'.destiny-gpu-lab.json'
 if marker.exists() and read(marker).get('kind')!='destiny-gpu-lab':raise ValueError('Foreign workspace marker')
 if not marker.exists():atomic_json(marker,dict(kind='destiny-gpu-lab',version=1))
 return resolved

def run_folder(root,run_id):
 import re
 if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,70}',run_id):raise ValueError('Use a simple unique lab run name')
 folder=root/'runs'/run_id
 if folder.exists() and folder.is_symlink():raise ValueError('Symlink run refused')
 return folder

def cleanup(root,folder):
 root=Path(root).resolve();folder=Path(folder)
 if folder.resolve()!=folder or not folder.is_relative_to(root/'runs') or not (root/'.destiny-gpu-lab.json').exists() or not (folder/'.lab-run.json').exists():raise ValueError('Only a marked lab run can be cleaned')
 target=folder/'intermediate'
 if not target.exists():return 0
 if target.is_symlink():raise ValueError('Symlink cleanup refused')
 total=0
 for base,dirs,files in os.walk(target,followlinks=False):
  for name in dirs+files:
   p=Path(base)/name
   if p.is_symlink() or p.is_mount():raise ValueError('Symlink/mount inside disposable files; cleanup refused')
   if p.is_file():total+=p.stat().st_size
 shutil.rmtree(target);return total

def archive(folder):
 folder=Path(folder);final=folder/'final'
 checks={str(p.relative_to(final)):sha(p) for p in final.rglob('*') if p.is_file() and p.name!='checksums.json'}
 atomic_json(final/'checksums.json',checks);dest=folder/'destiny-gpu-lab-results.zip';tmp=dest.with_suffix('.pending.zip')
 with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(final.rglob('*')):
   if p.is_file():z.write(p,'final/'+str(p.relative_to(final)))
 tmp.replace(dest)
 with zipfile.ZipFile(dest) as check:
  if check.testzip() is not None:raise ValueError('ZIP integrity check failed; intermediates kept')
 return dest

def restore_zip(root,source,name):
 target=run_folder(root,'restored-'+name)
 if target.exists():raise ValueError('Use a new restore name')
 with zipfile.ZipFile(source) as z:
  if sum(i.file_size for i in z.infolist())>512*1024**2:raise ValueError('Archive exceeds 512 MiB expanded limit')
  for i in z.infolist():
   p=Path(i.filename);mode=i.external_attr>>16
   if p.is_absolute() or '..' in p.parts or not p.parts or p.parts[0]!='final' or stat.S_ISLNK(mode):raise ValueError('Only final lab report files may be restored')
  target.mkdir(parents=True)
  for i in z.infolist():
   dest=target/i.filename
   if i.is_dir():dest.mkdir(parents=True,exist_ok=True);continue
   dest.parent.mkdir(parents=True,exist_ok=True)
   with z.open(i) as src,dest.open('xb') as out:shutil.copyfileobj(src,out)
 checks=read(target/'final/checksums.json')
 for rel,value in checks.items():
  p=(target/'final'/rel).resolve()
  if not p.is_relative_to(target/'final') or sha(p)!=value:raise ValueError('Restored checksum mismatch')
 return target

CASES=[
 dict(id='baseline-48',samples=48,denoiser='baseline',optimized=False),
 dict(id='samples-32',samples=32,denoiser='baseline',optimized=False),
 dict(id='samples-24',samples=24,denoiser='baseline',optimized=False),
 dict(id='alternate-denoiser-48',samples=48,denoiser='alternate',optimized=False),
 dict(id='candidate-48',samples=48,denoiser='baseline',optimized=True),
 dict(id='candidate-32',samples=32,denoiser='baseline',optimized=True),
]

def jobs(width=540,height=960,count=1):
 from universal.request import request
 from shot_audit import timeline
 timing=read(ROOT/'episodes/atheon-explained-en/audio-evidence/timing.json')
 package=dict(scenes=[dict(scene=dict(id=s['id']),timing=s) for s in timing['scenes']]);rows=timeline(package)
 selected=['01-hook/vault-establish','04-time/past-gate','02-identity/mechanism'];result=[]
 for sid in selected:
  row=next(r for r in rows if r['shotId']==sid);scene=next(s for s in timing['scenes'] if s['id']==row['sceneId']);start=(row['sceneFrameStart']+row['sceneFrameEndExclusive']-count)//2
  r=request('boss-atheon',quality='balanced',seed=42,lod=0,frames=count,fps=30,width=width,height=height,start_frame=start,animation=row['animation'],view='environment',arena='arena-glass-throne')
  result.append(dict(id=row['cameraId'],shotId=sid,sceneId=row['sceneId'],sceneFrames=scene['durationFrames'],episodeOffset=scene['startFrame'],request=r))
 return result

def resolved_settings(case,caps):
 base=caps['defaults'];denoiser=base['denoiser']
 if case['denoiser']=='alternate':
  denoiser='OPTIX' if denoiser!='OPTIX' else 'OPENIMAGEDENOISE'
 if denoiser=='OPTIX' and not caps['features'].get('optix-denoiser',{}).get('supported'):return None,'OptiX denoiser not supported by the selected device/probe'
 if denoiser=='OPENIMAGEDENOISE' and not caps.get('oidnCompiled'):return None,'OpenImageDenoise not compiled into this Blender'
 settings=dict(samples=case['samples'],use_denoising=True,denoiser=denoiser,denoising_use_gpu=base.get('denoising_use_gpu',False),use_auto_tile=base.get('use_auto_tile',True),compositor_device=base.get('compositor_device','CPU'),compositor_precision=base.get('compositor_precision','AUTO'))
 if case['optimized']:
  if denoiser=='OPENIMAGEDENOISE' and caps['features'].get('oidn-gpu',{}).get('supported'):settings['denoising_use_gpu']=True
  if caps['features'].get('gpu-compositor',{}).get('supported'):settings.update(compositor_device='GPU',compositor_precision='FULL')
  if caps.get('autoTileAvailable'):settings['use_auto_tile']=False
 # No bounces, threshold, lights, volumes, geometry, thread count or animation changes.
 return settings,None


@contextlib.contextmanager
def action_lock(root):
 with (Path(root)/'.lab-action.lock').open('a') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise ValueError('A lab action is already running; simultaneous Blender/report/cleanup actions are forbidden')
  try:yield
  finally:fcntl.flock(lock,fcntl.LOCK_UN)
