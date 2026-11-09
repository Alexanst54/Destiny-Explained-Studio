"""Collect/verify genuine Lot C renders; geometry, poses, views and source hashes remain inspectable."""
import hashlib,json,math,shutil,subprocess,sys
from pathlib import Path
sys.path[:]=[p for p in sys.path if Path(p).resolve()!=Path(__file__).resolve().parent]
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from universal.registry import ROOT,resolve,implementations
from universal.providers import load
from universal.cache import atomic_json,valid_png
from universal.lot_c_render import plan
from venus_vault.geometry import digest
FOLDER=ROOT/'docs/universal-library/lot-c'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def preserve():
 p=json.loads((FOLDER/'preservation.json').read_text())
 for path,value in p['protected'].items():
  if sha(ROOT/path)!=value:raise ValueError('Preserved input/evidence changed: '+path)
 old=json.loads(subprocess.check_output(['git','show',p['base']+':remotion/blender/universal/models.json'],text=True))
 for key,value in old.items():
  if implementations()[key]!=value:raise ValueError('Previous registry binding changed: '+key)
 return len(p['protected'])

def validate_report(report,job):
 r=report['request'];c=report['configuration'];module=load(job['boss']);binding=resolve(job['boss'])
 if report['status']!='success' or r['binding']['selectionId']!=job['boss'] or r['binding']['environmentId']!=binding['environmentId'] or r['binding']['provider']!='universal':raise ValueError('Incorrect identity/arena/provider')
 for field in ['view','quality','width','height','animation','frames','fps','lod','seed']:
  if r[field]!=job[field]:raise ValueError('Wrong scene setting: '+field)
 if c['bossDesignSha256']!=digest(module.generate(r['seed'],r['quality'],r['lod'])) or c['designSha256']!=digest(module.arena(r['seed'],r['quality'],r['lod'])):raise ValueError('Stale or substituted geometry')
 if c['sceneStyle']!=json.loads(json.dumps(module.SCENE_STYLE)):raise ValueError('Stale lighting/atmosphere')
 expected_samples=128 if job['quality']=='cinematic' else 48
 if c['samples']!=expected_samples or not c['persistentData'] or c['lod']!=0 or len(report['frames'])!=job['frames']:raise ValueError('Incomplete/wrong render configuration')
 relevant=['universal/'+job['slug']+'.py','universal/raid_shapes.py','universal/worker.py','venus_vault/geometry.py','venus_vault/renderer.py','import_scene.py']
 for part in relevant:
  path='remotion/blender/'+part
  if report['sources'].get(path)!=sha(ROOT/path):raise ValueError('Render-affecting source changed: '+part)
 for i in range(job['frames']):
  f=report['frames'][str(i)];frame=r['startFrame']+i;camera=module.camera(r['view'],frame,r['fps']);matrix=f['cameraMatrix']
  if f['sourceFrame']!=frame or f['poseSha256']!=digest(module.pose(r['animation'],frame,r['fps'])):raise ValueError('Pose/frame identity differs')
  if any(abs(matrix[k][3]-camera['position'][k])>1e-4 for k in range(3)):raise ValueError('Camera translation differs')
  direction=[camera['target'][k]-camera['position'][k] for k in range(3)];length=math.sqrt(sum(x*x for x in direction))
  if any(abs(-matrix[k][2]-direction[k]/length)>1e-4 for k in range(3)):raise ValueError('Camera direction differs')
  actual=f['cameraSettings']
  if abs(actual['lens']-camera['lens'])>1e-4 or actual['sensorFit']!=camera['sensorFit'] or abs(actual['sensorHeight']-24)>1e-4:raise ValueError('Physical camera settings differ')
 return True

def collect(source,native_log):
 source=Path(source);records={name:[] for name in ['oryx','rhulk','nezarec']};preserve()
 for job in plan():
  src=source/job['slug']/job['name'];report=json.loads((src/'progress.json').read_text());validate_report(report,job);out=FOLDER/job['slug'];out.mkdir(parents=True,exist_ok=True)
  for f in report['frames'].values():
   if not valid_png(src/f['file'],job['width'],job['height'],f['sha256']):raise ValueError('Invalid completed PNG')
  name=job['name'];shutil.copyfile(src/'progress.json',out/(name+'-report.json'));entry=dict(name=name,settings=job,report=name+'-report.json',reportSha256=sha(out/(name+'-report.json')),images=[])
  for i in ([0,12,24,35] if name=='animation' else [0]):
   target=name+f'-{i:04d}.png' if name=='animation' else name+'.png';shutil.copyfile(src/f'frame-{i:04d}.png',out/target);entry['images'].append(dict(path=target,index=i,sha256=report['frames'][str(i)]['sha256']))
  if name=='animation':
   shutil.copyfile(src/'sequence.mp4',out/'animation.mp4');entry['video']=dict(path='animation.mp4',sha256=sha(out/'animation.mp4'))
  records[job['slug']].append(entry)
 line=next(l for l in Path(native_log).read_text().splitlines() if l.startswith('LOT_C_CHECK '));native=json.loads(line.removeprefix('LOT_C_CHECK '))
 for name,entries in records.items():
  module=load('boss-'+name);counts=[dict(lod=l,boxes=len(module.generate(lod=l)['objects']),joints=len(module.generate(lod=l)['joints']),environmentBoxes=len(module.arena(lod=l)['objects'])) for l in range(3)]
  atomic_json(FOLDER/name/'evidence.json',dict(status='partial-dedicated-prototype',userApproved=False,bossId='boss-'+name,arenaId=resolve('boss-'+name)['environmentId'],renders=entries,native=native[name],geometry=counts,hardware='Actual device/backend/threads in each raw report; GPU memory/utilization not measured.'))
 atomic_json(FOLDER/'evidence.json',dict(status='three-prototypes-awaiting-visual-review',bosses=[dict(id='boss-'+n,evidence=n+'/evidence.json',sha256=sha(FOLDER/n/'evidence.json')) for n in records],protectedFiles=preserve(),fullLibraryComplete=False))

def verify():
 protected=preserve();index=json.loads((FOLDER/'evidence.json').read_text());jobs={(j['slug'],j['name']):j for j in plan()}
 if len(index['bosses'])!=3 or index['fullLibraryComplete']:raise ValueError('Wrong prototype scope')
 for item in index['bosses']:
  p=FOLDER/item['evidence'];e=json.loads(p.read_text());folder=p.parent;slug=folder.name
  if sha(p)!=item['sha256'] or e['status']!='partial-dedicated-prototype' or e['userApproved'] or e['bossId']!=item['id']:raise ValueError('Incorrect model status/identity')
  if {r['name'] for r in e['renders']}!={'front','profile','three-quarter','cinematic','environment','animation'}:raise ValueError('Missing requested view')
  for r in e['renders']:
   path=folder/r['report'];report=json.loads(path.read_text());job=jobs[(slug,r['name'])]
   if sha(path)!=r['reportSha256']:raise ValueError('Report hash differs')
   validate_report(report,job)
   for image in r['images']:
    if image['sha256']!=report['frames'][str(image['index'])]['sha256'] or not valid_png(folder/image['path'],job['width'],job['height'],image['sha256']):raise ValueError('Invalid proof image')
   if 'video' in r:
    video=folder/r['video']['path']
    if sha(video)!=r['video']['sha256']:raise ValueError('Video hash differs')
    s=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name,pix_fmt,nb_frames,avg_frame_rate,duration,width,height','-of','json',str(video)]))['streams'][0]
    if s['codec_name']!='h264' or s['pix_fmt']!='yuv420p' or int(s['nb_frames'])!=36 or s['avg_frame_rate']!='24/1' or abs(float(s['duration'])-1.5)>.02 or s['width']!=480 or s['height']!=360:raise ValueError('Invalid video settings')
    data=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-f','framemd5','-']).decode();hashes=[l.rsplit(',',1)[-1].strip() for l in data.splitlines() if l and not l.startswith('#')]
    if len(hashes)!=36 or len(set(hashes))<33:raise ValueError('Frozen/incomplete decoded clip')
  if e['native']['evaluations']!=240 or e['native']['clipProjectionFrames']!=36 or e['native']['maxNormalizedOverflow']!=0 or e['native']['maxClipOverflow']!=0:raise ValueError('Native framing/animation check failed')
 return dict(prototypes=3,cinematicStills=15,balancedFrames=108,protectedFiles=protected)

if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]!='--check':collect(sys.argv[1],sys.argv[2])
 else:print('LOT_C_EVIDENCE '+json.dumps(verify()))
