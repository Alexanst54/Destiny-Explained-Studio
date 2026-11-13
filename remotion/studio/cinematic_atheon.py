"""Separate, opt-in directed episode. Existing outputs and PR25 workflow are untouched."""
import argparse,json,os,shutil,subprocess,sys,time
from pathlib import Path
from complete_atheon import load_package,software,probe,check_space,settings,locked,install_inputs,episode_props,verify,verify_audio_alignment,ROOT,TOTAL_FRAMES,FPS,run_task,atomic_json
from perf_common import sources,sha,digest,valid_record,identity
from performance import execute_profile,CASES
from cinematic_direction import SHOTS,shot_at
from universal.request import request


def jobs_for(package,width,height,quality='balanced',representatives=False):
 result=[]
 for item in package['scenes']:
  scene_id=item['scene']['id'];frames=item['timing']['durationFrames'];start=0
  while start<frames:
   shot=shot_at(scene_id,start,frames);stop=start+1
   while stop<frames and shot_at(scene_id,stop,frames)['name']==shot['name']:stop+=1
   boss='boss-templar' if shot['name']=='templar' else 'boss-atheon';arena='arena-templars-well' if boss=='boss-templar' else 'arena-glass-throne'
   for a in range(start,stop,120):
    n=min(120,stop-a);frame=a+n//2 if representatives else a;count=1 if representatives else n
    r=request(boss,quality=quality,seed=42,lod=0,frames=count,fps=30,width=width,height=height,start_frame=frame,animation='idle' if boss=='boss-templar' else shot['animation'],view='environment',arena=arena)
    result.append(dict(id='scenes/'+scene_id+'/frames/'+f'shot-{a:04d}',sceneId=scene_id,sceneFrames=frames,request=r,indices=list(range(count)),shotName=shot['name']))
   start=stop
 return result


def bind(folder,package,opts,tools,case):
 manifest=folder/'project.json';wanted=dict(kind='directed-atheon-v1',options=opts,renderSettings=case,sources=sources(),pilotAssetsSha256=package['assetsSha256'],blenderVersion=tools['blenderVersion'],nodeVersion=tools['nodeVersion']);fp=digest(wanted)
 if manifest.exists():
  old=json.loads(manifest.read_text())
  if old.get('fingerprint')!=fp:raise ValueError('Different directed source/settings; restore the saved commit or use a new Drive project. Old videos are preserved.')
  return old
 if any(p.name!='episode.lock' for p in folder.iterdir()):raise ValueError('Use a NEW empty folder; do not reuse an existing validated episode folder.')
 paths=list(wanted['sources'])+['episodes/atheon-explained-en']
 if subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain','--',*paths],text=True).strip():raise ValueError('Commit production changes before creating a project')
 old=dict(identity=wanted,fingerprint=fp,sourceCommit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),sourceDirty=False);atomic_json(manifest,old);return old


def verify_jobs(folder,jobs,case,tools):
 counts={};records=[];hashes=[]
 cfg={k:v for k,v in case.items() if k!='exactBaseline'}
 for j in jobs:
  out=folder/'public'/j['id'];r=json.loads((out/'profile.json').read_text());wanted=identity({**j,'direction':True},cfg,tools['blenderVersion'])
  if r.get('identity')!=wanted:raise ValueError('Directed cache provenance mismatch')
  for i in j['indices']:
   rec=r.get('frames',{}).get(str(i))
   if not valid_record(out,str(i),rec,j['request']['width'],j['request']['height']):raise ValueError('Missing/corrupt directed frames: '+j['id'])
   hashes.append(rec['sha256']);d=rec['device'];key=str((d['selected'],d.get('backend'),d.get('devices')));counts[key]=counts.get(key,0)+1;records.append(rec)
 if len(records)!=2672:raise ValueError('Full episode requires all 2672 distinct source frames')
 return dict(actualFrameBackends=counts,frameSequenceSha256=digest(hashes),frames=len(records),t4RenderingValidated=all(f['device']['selected']=='GPU' and f['device'].get('backend') in ['OPTIX','CUDA'] and any('T4' in d for d in f['device'].get('devices',[])) for f in records))


def props_for(package,opts,jobs):
 props=episode_props(package,opts)
 for s in props['scenes']:
  paths=[None]*s['durationFrames']
  for j in jobs:
   if j['sceneId']!=s['id']:continue
   for i in j['indices']:
    frame=j['request']['startFrame']+i
    if paths[frame] is not None:raise ValueError('Duplicate directed source frame')
    paths[frame]=j['id']+f'/frame-{i:04d}.png'
  if any(p is None for p in paths):raise ValueError('Directed timeline has gaps')
  s['frameSources']=paths
 return props


def assemble(folder,package,opts,tools,project,jobs,case,scratch,chrome=None):
 ts=time.perf_counter();devices=verify_jobs(folder,jobs,case,tools);cache_seconds=time.perf_counter()-ts
 for item in package['scenes']:
  if sha(folder/'public/scenes'/item['scene']['id']/'speech.wav')!=item['speech']['sha256']:raise ValueError('Original prepared audio changed')
 props=props_for(package,opts,jobs);stem='atheon-episode-01-cinematic';output=folder/(stem+'.mp4');report=folder/(stem+'.validation.json')
 if output.exists() and report.exists():
  old=json.loads(report.read_text())
  if old.get('fingerprint')==project['fingerprint'] and old.get('sha256')==sha(output) and old.get('status')=='passed':verify(output,opts);verify_audio_alignment(output,package['scenes']);print('Reused validated directed export',flush=True);return old
 # Stage only validated assets locally to isolate Drive reads from Remotion browser work.
 stage=Path(scratch)/('compose-'+project['fingerprint'][:16]);public=stage/'public';public.mkdir(parents=True,exist_ok=True);ts=time.perf_counter();bytes_copied=0
 needed=sum((folder/'public'/path).stat().st_size for s in props['scenes'] for path in s['frameSources'])+512*1024**2
 if shutil.disk_usage(stage).free<needed:raise ValueError('Insufficient local scratch space for composition staging/export; keep Drive frames and free local space before retrying assembly')
 for relative in [path for s in props['scenes'] for path in s['frameSources']]+['scenes/'+s['id']+'/speech.wav' for s in props['scenes']]:
  src=folder/'public'/relative;dest=public/relative;dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists() or sha(dest)!=sha(src):shutil.copyfile(src,dest);bytes_copied+=src.stat().st_size
 stage_seconds=time.perf_counter()-ts;path=stage/'props.json';atomic_json(path,props);pending=stage/(stem+'.mp4')
 command=[tools['node'],ROOT/'remotion/node_modules/@remotion/cli/remotion-cli.js','render',ROOT/'remotion/studio/cinematic-index.tsx','CinematicAtheonEpisode',pending,'--props',path,'--public-dir',public,'--codec','h264','--audio-codec','aac','--pixel-format','yuv420p','--image-format','png','--color-space','bt709','--concurrency',1]
 if chrome:command+=['--browser-executable',chrome]
 ts=time.perf_counter();run_task(command,folder/'logs/cinematic-remotion.log');export_seconds=time.perf_counter()-ts;proof=verify(pending,opts);proof['audioAlignment']=verify_audio_alignment(pending,package['scenes'])
 ts=time.perf_counter();dest=folder/(stem+'.pending.mp4');shutil.copyfile(pending,dest)
 if sha(dest)!=sha(pending):raise ValueError('Final Drive MP4 readback differs')
 dest.replace(output);copy_seconds=time.perf_counter()-ts
 proof.update(status='passed',fingerprint=project['fingerprint'],sha256=sha(output),sourceCommit=project['sourceCommit'],fullEpisodeRendered=True,deviceReport=devices,preparedSpeechReused=True,originalSpeechSha256={i['scene']['id']:i['speech']['sha256'] for i in package['scenes']},subtitleWords=223,subtitleTimingValidated=True,subtitlesSha256=sha(folder/'subtitles.en.srt'),cacheVerificationSeconds=cache_seconds,driveToScratchStageSeconds=stage_seconds,driveToScratchBytes=bytes_copied,remotionCompositionAndEncodeSeconds=export_seconds,finalDriveCopySeconds=copy_seconds)
 atomic_json(report,proof);return proof


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['prepare','preview','render','assemble','validate']);p.add_argument('output');p.add_argument('--scratch',default='/content/atheon-directed');p.add_argument('--blender',default='blender');p.add_argument('--node',default='node');p.add_argument('--chrome');p.add_argument('--width',type=int,default=540);p.add_argument('--height',type=int,default=960);p.add_argument('--quality',choices=['draft','balanced','cinematic'],default='balanced');p.add_argument('--allow-cpu',action='store_true');p.add_argument('--scene');p.add_argument('--reviewed-previews',action='store_true');p.add_argument('--benchmark-reviewed',action='store_true');a=p.parse_args();opts=settings(a.width,a.height,a.quality);package=load_package();tools=software(a.blender,a.node,a.chrome);case={**CASES['scratch-persistent'],'productionPreset':'candidate-48'};jobs=jobs_for(package,a.width,a.height,a.quality)
 with locked(a.output) as folder:
  project=bind(folder,package,opts,tools,case);(folder/'logs').mkdir(exist_ok=True);(folder/'reports').mkdir(exist_ok=True);check_space(folder,opts);tools['device']=probe(folder,tools);install_inputs(folder,package,opts)
  atomic_json(folder/'reports/direction-plan.json',dict(jobs=jobs,storyboard=SHOTS,approvedModelFilesUnmodified=True))
  if a.action=='prepare':return
  if a.action=='preview':
   preview=jobs_for(package,a.width,a.height,a.quality,True);execute_profile(preview,folder/'previews',Path(a.scratch)/'previews',case,tools['blender'],'auto',not a.allow_cpu,True)
   cards=['<!doctype html><meta name="viewport" content="width=device-width"><h1>Real directed Blender stills — not animation validation</h1>']
   for j in preview:cards.append(f'<h2>{j["sceneId"]}: {j["shotName"]}</h2><img width="270" src="{j["id"]}/frame-0000.png">')
   (folder/'previews/index.html').write_text('\n'.join(cards));return
  if a.action=='render':
   if not a.reviewed_previews or not a.benchmark_reviewed:raise ValueError('Review the paired T4 benchmark and all directed shot previews before a complete rerender')
   if not (folder/'previews/index.html').exists():raise ValueError('Render directed previews first')
   if a.scene and a.scene not in [s['scene']['id'] for s in package['scenes']]:raise ValueError('Unknown scene')
   selected=[j for j in jobs if not a.scene or j['sceneId']==a.scene];execute_profile(selected,folder/'public',Path(a.scratch)/'render',case,tools['blender'],'auto',not a.allow_cpu,True)
  elif a.action=='assemble':assemble(folder,package,opts,tools,project,jobs,case,a.scratch,a.chrome)
  elif a.action=='validate':
   proof=json.loads((folder/'atheon-episode-01-cinematic.validation.json').read_text());video=folder/'atheon-episode-01-cinematic.mp4'
   if proof.get('fingerprint')!=project['fingerprint'] or proof.get('sha256')!=sha(video) or proof.get('status')!='passed':raise ValueError('Stale or invalid export')
   verify_jobs(folder,jobs,case,tools);verify(video,opts);verify_audio_alignment(video,package['scenes']);print('Directed episode validated')
if __name__=='__main__':main()
