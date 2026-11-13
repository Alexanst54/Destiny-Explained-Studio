"""Exactly three seconds / three real moving shots; cannot launch a full episode."""
import argparse,json,shutil,subprocess,time
from pathlib import Path
from complete_atheon import ROOT,load_package,software,probe,locked,run_task,settings
from perf_common import atomic_json,digest,sha,sources,identity,valid_record
from performance import execute_profile,CASES
from universal.request import request
from shot_audit import timeline

SELECTED=['01-hook/vault-establish','02-identity/monument','02-identity/mechanism']

def jobs_for(package,width,height,quality='balanced',fps=10):
 settings(width,height,quality)
 if fps not in [10,30]:raise ValueError('Use 10 or 30 output FPS; diagnostic duration stays 3 seconds')
 rows=timeline(package);result=[];stride=30//fps
 for number,shot_id in enumerate(SELECTED):
  row=next(r for r in rows if r['shotId']==shot_id);indices=[i*stride for i in range(fps)];start=(row['sceneFrameStart']+row['sceneFrameEndExclusive']-30)//2
  if start<row['sceneFrameStart'] or start+30>row['sceneFrameEndExclusive']:raise ValueError('Motion window crosses a cut')
  scene=next(i for i in package['scenes'] if i['scene']['id']==row['sceneId']);r=request('boss-atheon',quality=quality,seed=42,lod=0,frames=indices[-1]+1,fps=30,width=width,height=height,start_frame=start,animation=row['animation'],view='environment',arena='arena-glass-throne')
  result.append(dict(id='scenes/'+row['sceneId']+'/frames/motion-'+row['cameraId'],sceneId=row['sceneId'],sceneFrames=scene['timing']['durationFrames'],request=r,indices=indices,shotId=shot_id,cameraId=row['cameraId'],outputFrameStart=number*fps,outputFrames=fps,outputFps=fps,episodeSceneStart=scene['timing']['startFrame']))
 return result


def bind(folder,jobs,tools,quality,fps,width,height):
 wanted=dict(kind='atheon-motion-test-v1',jobs=jobs,sources=sources(),blenderVersion=tools['blenderVersion'],nodeVersion=tools['nodeVersion'],quality=quality,fps=fps,width=width,height=height)
 fp=digest(wanted);path=folder/'project.json'
 if path.exists():
  project=json.loads(path.read_text())
  if project.get('fingerprint')!=fp:raise ValueError('Motion source/settings changed; restore saved commit or use a NEW test folder. Existing caches are preserved.')
  return project
 if any(p.name!='episode.lock' for p in folder.iterdir()):raise ValueError('Choose a NEW empty motion-test folder')
 dirty=bool(subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain','--',*sources()],text=True).strip())
 if dirty:raise ValueError('Commit production sources before a reproducible motion render')
 project=dict(identity=wanted,fingerprint=fp,sourceCommit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),sourceDirty=False);atomic_json(path,project);return project


def checked_frames(folder,jobs,tools):
 items=[];shots=[];cfg={k:v for k,v in CASES['scratch-persistent'].items() if k!='exactBaseline'}
 for j in jobs:
  out=folder/'renders'/j['id'];report=json.loads((out/'profile.json').read_text())
  if report['identity']!=identity({**j,'direction':True},cfg,tools['blenderVersion']):raise ValueError('Motion cache provenance mismatch')
  matrices=[];hashes=[]
  for i in j['indices']:
   record=report['frames'].get(str(i));r=j['request']
   if not valid_record(out,str(i),record,r['width'],r['height']):raise ValueError('Missing/corrupt diagnostic frame')
   d=record.get('cameraDiagnostic',{})
   if d.get('shotId')!=j['shotId'] or d.get('cameraId')!=j['cameraId'] or d.get('sceneFrame')!=r['startFrame']+i:raise ValueError('Stale/wrong camera applied to a motion frame')
   matrices.append(d['matrixWorld']);hashes.append(record['sha256']);items.append(dict(path='renders/'+j['id']+'/'+record['file'],shotId=d['shotId'],cameraId=d['cameraId'],sourceFrame=d['sceneFrame'],episodeFrame=d['episodeFrame']))
  movement=max(sum((m[a][3]-matrices[0][a][3])**2 for a in range(3))**.5 for m in matrices)
  if len(set(hashes))!=len(hashes) or movement<.1:raise ValueError('Motion test contains repeated stills or an unmoving camera')
  shots.append(dict(shotId=j['shotId'],cameraId=j['cameraId'],outputRange=[j['outputFrameStart'],j['outputFrameStart']+j['outputFrames']],sourceRange=[j['request']['startFrame'],j['request']['startFrame']+j['indices'][-1]+1],cameraTranslationSpan=movement,firstMatrix=matrices[0],lastMatrix=matrices[-1],distinctRenderedFrames=len(set(hashes))))
 if len({digest(s['firstMatrix']) for s in shots})!=3:raise ValueError('The three compositions must be different')
 return items,shots


def export(folder,scratch,jobs,tools,project,chrome=None):
 items,shots=checked_frames(folder,jobs,tools);identity_=project['identity'];public=scratch/'composition/public';public.mkdir(parents=True,exist_ok=True);ts=time.perf_counter()
 for item in items:
  src=folder/item['path'];target=public/item['path'];target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists() or sha(target)!=sha(src):shutil.copyfile(src,target)
 stage_seconds=time.perf_counter()-ts;props=dict(width=identity_['width'],height=identity_['height'],fps=identity_['fps'],items=items);propfile=scratch/'motion-props.json';atomic_json(propfile,props);pending=scratch/'atheon-motion-test.mp4';output=folder/'atheon-motion-test.mp4';proof_path=folder/'motion-validation.json'
 if proof_path.exists() and output.exists():
  old=json.loads(proof_path.read_text())
  if old.get('status')=='passed' and old.get('fingerprint')==project['fingerprint'] and old.get('sha256')==sha(output):print('Reused validated motion clip',flush=True);return old
 cmd=[tools['node'],ROOT/'remotion/node_modules/@remotion/cli/remotion-cli.js','render',Path(__file__).with_name('motion-index.tsx'),'AtheonMotionDiagnostic',pending,'--props',propfile,'--public-dir',public,'--codec','h264','--pixel-format','yuv420p','--image-format','png','--color-space','bt709','--concurrency',1]
 if chrome:cmd+=['--browser-executable',chrome]
 ts=time.perf_counter();run_task(cmd,folder/'logs/motion-remotion.log');compose_seconds=time.perf_counter()-ts
 media=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(pending)],text=True));v=next(s for s in media['streams'] if s['codec_type']=='video')
 from fractions import Fraction
 if v['codec_name']!='h264' or v['pix_fmt']!='yuv420p' or int(v['nb_read_frames'])!=len(items) or Fraction(v['avg_frame_rate'])!=identity_['fps'] or abs(float(v['duration'])-3)>.001 or (v['width'],v['height'])!=(identity_['width'],identity_['height']):raise ValueError('Invalid motion diagnostic MP4')
 subprocess.run(['ffmpeg','-v','error','-i',str(pending),'-f','null','-'],check=True)
 ts=time.perf_counter();temp=folder/'atheon-motion-test.pending.mp4';shutil.copyfile(pending,temp)
 if sha(temp)!=sha(pending):raise ValueError('Motion export Drive readback differs')
 temp.replace(output);copy_seconds=time.perf_counter()-ts
 perf=json.loads((folder/'renders/result.json').read_text());proof=dict(status='passed',route='cinematic-motion-diagnostic',fingerprint=project['fingerprint'],sourceCommit=project['sourceCommit'],sha256=sha(output),frames=len(items),fps=identity_['fps'],durationSeconds=3,width=v['width'],height=v['height'],quality=identity_['quality'],sourceFps=30,sourceFrameStep=30//identity_['fps'],noRepeatedStills=True,shots=shots,silent=True,originalNarrationModified=False,fullEpisodeRendered=False,renderPerformance=perf,driveToComposeSeconds=stage_seconds,remotionCompositionAndEncodeSeconds=compose_seconds,exportCopySeconds=copy_seconds)
 atomic_json(proof_path,proof);return proof


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['plan','render']);p.add_argument('output');p.add_argument('--scratch',default='/content/atheon-motion-diagnostic');p.add_argument('--width',type=int,default=540);p.add_argument('--height',type=int,default=960);p.add_argument('--quality',choices=['draft','balanced'],default='balanced');p.add_argument('--fps',type=int,choices=[10,30],default=10);p.add_argument('--blender',default='blender');p.add_argument('--node',default='node');p.add_argument('--chrome');p.add_argument('--allow-cpu',action='store_true');a=p.parse_args();folder=Path(a.output).resolve();scratch=Path(a.scratch).resolve()
 for ancestor in folder.parents:
  if (ancestor/'project.json').exists():raise ValueError('Keep motion diagnostics OUTSIDE existing project/cache folders')
 package=load_package();jobs=jobs_for(package,a.width,a.height,a.quality,a.fps)
 with locked(folder):
  tools=software(a.blender,a.node,a.chrome);project=bind(folder,jobs,tools,a.quality,a.fps,a.width,a.height);(folder/'logs').mkdir(exist_ok=True);(folder/'reports').mkdir(exist_ok=True);atomic_json(folder/'reports/19-shot-timeline.json',timeline(package));atomic_json(folder/'reports/motion-plan.json',jobs)
  if a.action=='plan':print(f'Plan only: {3*a.fps} genuinely rendered frames, three moving shots, 3 seconds. No full render.');return
  device=probe(folder,tools)
  if not a.allow_cpu and (device['selected']!='GPU' or device.get('backend') not in ['OPTIX','CUDA']):raise ValueError('Select a Colab GPU before rendering the motion test; CPU is not enabled')
  scratch.mkdir(parents=True,exist_ok=True);reserve=a.width*a.height*3*(3*a.fps)*3+32*1024**2
  if min(shutil.disk_usage(folder).free,shutil.disk_usage(scratch).free)<reserve:raise ValueError('Insufficient reported free space for this bounded diagnostic; check Drive account quota too')
  execute_profile(jobs,folder/'renders',scratch/'frames',CASES['scratch-persistent'],tools['blender'],'auto',not a.allow_cpu,True)
  report=export(folder,scratch,jobs,tools,project,a.chrome);print(json.dumps(dict(frames=report['frames'],fps=report['fps'],seconds=3,actualBackend=report['renderPerformance']['actualFrameBackends'],gpu=report['renderPerformance']['gpu'],phaseSeconds=report['renderPerformance']['phases']),indent=2))
if __name__=='__main__':main()
