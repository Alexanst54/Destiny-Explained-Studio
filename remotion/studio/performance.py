"""Opt-in paired benchmark, no Actions or full episode rendering.

Example: python remotion/studio/performance.py DRIVE_RUN --scratch /content/atheon-bench
--blender /content/.../blender --frames 30 --width 540 --height 960 --execute
"""
import argparse,html,json,math,os,re,shutil,subprocess,sys,time,uuid
from pathlib import Path
from complete_atheon import load_package,configs,settings as episode_settings,run_task,ROOT,atomic_json,software,probe
from universal.request import request
from universal.cache import valid_png
from perf_common import Telemetry,digest,identity,sources,sha,checkpoint,valid_record

CASES={
 'baseline-current':dict(storage='drive',persistent=False,samples=None,denoise='existing',pngCompression=15,threads=3,exactBaseline=True),
 'instrumented-drive':dict(storage='drive',persistent=False,samples=None,denoise='existing',pngCompression=15,threads=3),
 'scratch-blocks':dict(storage='scratch',persistent=False,samples=None,denoise='existing',pngCompression=15,threads=3),
 'scratch-persistent':dict(storage='scratch',persistent=True,samples=None,denoise='existing',pngCompression=15,threads=3),
 'samples-32-denoised':dict(storage='scratch',persistent=True,samples=32,denoise='on',pngCompression=15,threads=3),
 'samples-32-no-denoise':dict(storage='scratch',persistent=True,samples=32,denoise='off',pngCompression=15,threads=3),
 'png-fast-threads-6':dict(storage='scratch',persistent=True,samples=None,denoise='existing',pngCompression=0,threads=6),
}

def jobs_for(package,width,height,frames=30,direction=False):
 if frames not in [30,36,48,60]:raise ValueError('Choose 30, 36, 48 or 60 representative frames')
 per_scene=frames//6;result=[]
 if direction:
  from cinematic_atheon import jobs_for as directed_jobs
  directed=directed_jobs(package,width,height)
  for item in package['scenes']:
   sid=item['scene']['id'];candidates=[j for j in directed if j['sceneId']==sid];chosen=next((j for j in candidates if j['shotName']=='templar'),candidates[len(candidates)//2]);r=dict(chosen['request']);r['startFrame']+=min(r['frames']-per_scene,r['frames']//2);r['frames']=per_scene
   result.append(dict(id=sid,sceneId=sid,sceneFrames=chosen['sceneFrames'],request=r,indices=list(range(per_scene))))
  return result
 for item,c in zip(package['scenes'],configs(package,episode_settings(width,height,'balanced'))):
  # A short consecutive window near each scene midpoint; exact same source frames for every case.
  start=item['timing']['durationFrames']//2
  r=request(c['boss'],quality='balanced',seed=42,lod=0,frames=per_scene,fps=30,width=width,height=height,start_frame=start,animation=c['animation'],view=c['camera'],arena=c['arena'])
  result.append(dict(id=item['scene']['id'],sceneId=item['scene']['id'],sceneFrames=c['frames'],request=r,indices=list(range(per_scene))))
 return result

def gpu_snapshot():
 binary=shutil.which('nvidia-smi')
 if not binary:return dict(available=False,note='nvidia-smi unavailable')
 try:return dict(available=True,query=subprocess.check_output([binary,'--query-gpu=uuid,name,driver_version,memory.total','--format=csv,noheader'],text=True,timeout=10).strip())
 except subprocess.SubprocessError as e:return dict(available=False,note=str(e))

def cycles_stages(log):
 """Approximate progress-time increments, not exclusive CUDA kernel timings."""
 result={};last=0;previous=None
 for line in Path(log).read_text(errors='replace').splitlines():
  match=re.search(r'Time:(\d+):(\d+(?:\.\d+)?)',line)
  if not match:continue
  elapsed=int(match[1])*60+float(match[2]);status=line.rsplit('|',1)[-1].strip()
  if elapsed<last:previous=None;last=0
  if previous:result[previous]=result.get(previous,0)+max(0,elapsed-last)
  previous=('denoising' if 'Denois' in status else 'sampling' if re.search('Sample|Rendering',status) else 'compositor' if 'Composit' in status else 'geometry-sync-bvh' if re.search('Synchron|Updating|BVH|Loading|Kernel|Scene',status) else 'other');last=elapsed
 return dict(approximateProgressSeconds=result,scope='Blender printed progress clock deltas; nested/rounded stages, not GPU kernel timing; inspect raw log')

def restore_job(remote,local,wanted,width,height):
 started=time.perf_counter();copied=0
 if not (remote/'profile.json').exists():return dict(seconds=time.perf_counter()-started,copied=0)
 r=json.loads((remote/'profile.json').read_text())
 if r['identity']!=wanted:raise ValueError('Checkpoint source/settings mismatch; restore saved commit or use a new benchmark folder')
 local.mkdir(parents=True,exist_ok=True)
 for key,record in list(r['frames'].items()):
  if not valid_record(remote,key,record,width,height):r['frames'].pop(key);continue
  if not valid_record(local,key,record,width,height):shutil.copyfile(remote/record['file'],local/record['file']);copied+=1
 atomic_json(local/'profile.json',r);return dict(seconds=time.perf_counter()-started,copied=copied)

def execute_profile(jobs,folder,scratch,case,blender,device='auto',require_gpu=True,direction=False,checkpoint_every=10):
 """Same engine used by the benchmark and opt-in cinematic episode production."""
 folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);scratch=Path(scratch).resolve();scratch.mkdir(parents=True,exist_ok=True);version=subprocess.check_output([blender,'--version'],text=True,timeout=30)
 cfg={k:v for k,v in case.items() if k!='exactBaseline'};work=[];restore=[];cold=0;reused=0;verification=0
 for original in jobs:
  j=json.loads(json.dumps(original));identity_job={**original,'direction':direction};j['identityJob']=identity_job;remote=folder/j['id'];remote.mkdir(parents=True,exist_ok=True)
  local=(scratch/digest(str(folder.resolve()))[:16]/j['id']) if case['storage']=='scratch' else remote
  local.mkdir(parents=True,exist_ok=True);wanted=identity(identity_job,cfg,version)
  if local!=remote:restore.append(restore_job(remote,local,wanted,j['request']['width'],j['request']['height']))
  path=local/'profile.json'
  ts=time.perf_counter();prior=json.loads(path.read_text()) if path.exists() else dict(identity=wanted,frames={})
  if prior.get('identity')!=wanted:raise ValueError('Scratch/source mismatch; use a new scratch path or restore the saved source commit')
  n=sum(bool(valid_record(local,str(i),prior['frames'].get(str(i)),j['request']['width'],j['request']['height'])) for i in j['indices']);verification+=time.perf_counter()-ts;reused+=n;cold+=len(j['indices'])-n
  j.update(output=str(local.resolve()),remote=str(remote.resolve()) if local!=remote else None);work.append(j)
 run_id=uuid.uuid4().hex;plan=dict(invocationId=run_id,jobs=work,settings=cfg,blenderVersion=version,device=device,requireGpu=require_gpu,direction=direction,checkpointEvery=checkpoint_every,events=str((scratch/('events-'+digest(str(folder.resolve()))[:16]+'.jsonl')).resolve()))
 Path(plan['events']).write_text('');plan_path=scratch/('plan-'+digest(str(folder.resolve()))[:16]+'.json');atomic_json(plan_path,plan);log=folder/'blender.log';ts=time.perf_counter();launch_epoch=time.time();error=None
 with Telemetry(scratch/('gpu-'+digest(str(folder.resolve()))[:16]+'.jsonl')) as monitor:
  def progress():
   try:
    rows=Path(plan['events']).read_text().splitlines();event=json.loads(rows[-1]) if rows else {};monitor.phase=event.get('phase','startup')
    text=f"{folder.name}: {monitor.phase} {event.get('job','')} frame {event.get('frame','')} | {time.perf_counter()-ts:.0f}s"
    key=(monitor.phase,event.get('job'),event.get('frame'))
    if getattr(progress,'last',None)!=key:print(text,flush=True);progress.last=key
   except (OSError,ValueError):pass
  try:run_task([blender,'--background','--factory-startup','--python-exit-code','1','--python',Path(__file__).with_name('profile_worker.py'),'--',plan_path],log,progress)
  except BaseException as e:error=str(e) or type(e).__name__
 wall=time.perf_counter()-ts
 # Preserve partial frame checkpoints and raw profiler evidence on exceptions too.
 reports=[];frame_records=[];drive_io=[]
 for j in work:
  local=Path(j['output']);path=local/'profile.json'
  if not path.exists():continue
  if j['remote']:
   try:drive_io.append(checkpoint(local,j['remote'],identity(j['identityJob'],cfg,version),j['request']['width'],j['request']['height']))
   except Exception as e:error=(error+'; ' if error else '')+str(e)
  r=json.loads(path.read_text());reports.append(r);frame_records.extend(r['frames'][str(i)] for i in j['indices'] if str(i) in r['frames'])
 for src,name in [(Path(plan['events']),'events.jsonl'),(monitor.path,'gpu.jsonl')]:
  if src.exists():shutil.copyfile(src,folder/name)
 events=[json.loads(line) for line in Path(plan['events']).read_text().splitlines()]
 ready=next((e['epochSeconds'] for e in events if e['phase']=='worker-ready'),None)
 t4=bool(frame_records) and all(f['device']['selected']=='GPU' and f['device'].get('backend') in ['OPTIX','CUDA'] and any('T4' in d for d in f['device'].get('devices',[])) for f in frame_records)
 totals={key:sum(f.get(key,0) for f in frame_records if f.get('invocationId')==run_id) for key in ['updateSeconds','updateCpuSeconds','renderAndCompositeSeconds','renderCpuSeconds','pngEncodeAndWriteSeconds','pngCpuSeconds','verifySeconds']}
 result=dict(status='failed' if error else 'passed',error=error,wallSeconds=wall,frames=sum(len(j['indices']) for j in jobs),newFrames=cold,reusedFrames=reused,sourceFingerprint=digest(sources()),settings=cfg,direction=direction,blenderVersion=version,startupToWorkerReadySeconds=ready-launch_epoch if ready else None,buildSeconds=sum(b['seconds'] for r in reports for b in r.get('builds',[])),cpuBuildSeconds=sum(b['cpuSeconds'] for r in reports for b in r.get('builds',[])),cacheVerificationSeconds=verification+sum(r.get('cacheVerificationSeconds',0) for r in reports),restoreFromDrive=restore,driveCheckpoints=drive_io,workerCheckpointSeconds=sum(c['seconds'] for r in reports for c in r.get('driveCheckpoints',[])),phases=totals,cyclesLog=cycles_stages(log),gpu=monitor.report(),actualT4Rendering=t4,peakBlenderRssKiB=max((r.get('peakProcessRssKiB',0) for r in reports),default=0),coldRun=cold==sum(len(j['indices']) for j in jobs) and reused==0)
 atomic_json(folder/'result.json',result)
 if error:raise RuntimeError('Profiler failed; partial cache and report preserved: '+error)
 return result

def baseline(jobs,folder,blender,device):
 folder.mkdir(parents=True,exist_ok=True);ts=time.perf_counter();records=[];error=None
 with Telemetry(folder/'gpu.jsonl') as monitor:
  try:
   for j in jobs:
    r=j['request'];out=folder/j['id'];cmd=[sys.executable,ROOT/'remotion/blender/render_universal.py',r['selectionId'],out,'--blender',blender,'--device',device,'--threads',3,'--quality',r['quality'],'--lod',r['lod'],'--width',r['width'],'--height',r['height'],'--frames',r['frames'],'--start-frame',r['startFrame'],'--fps',r['fps'],'--view',r['view'],'--animation',r['animation'],'--arena',r['binding']['environmentId'],'--timeout',7200]
    existed=out.exists()
    if existed:cmd+=['--resume']
    monitor.phase='baseline-render';run_task(cmd,folder/(j['id']+'.log'));record=json.loads((out/'progress.json').read_text());records.append(record)
    if device!='cpu' and any(f['device']['selected']!='GPU' for f in record['frames'].values()):raise RuntimeError('Baseline fell back to CPU; not a comparable GPU benchmark')
  except BaseException as e:error=str(e) or type(e).__name__
 frames=[f for r in records for f in r['frames'].values()];result=dict(status='failed' if error else 'passed',error=error,wallSeconds=time.perf_counter()-ts,frames=sum(len(j['indices']) for j in jobs),newFrames=sum(r['renderedThisRun'] for r in records),reusedFrames=sum(r['cacheHits'] for r in records),coldRun=bool(records) and len(records)==len(jobs) and all(r['cacheHits']==0 for r in records),buildSeconds=sum(r['buildSeconds'] for r in records),renderEncodeVerifySeconds=sum(f['seconds'] for f in frames),gpu=monitor.report(),actualT4Rendering=bool(frames) and all(f['device']['selected']=='GPU' and f['device'].get('backend') in ['OPTIX','CUDA'] and any('T4' in d for d in f['device'].get('devices',[])) for f in frames),scope='Exact current render_universal CLI; per-frame seconds combine render, PNG save and verification; instrumented-drive separates them')
 atomic_json(folder/'result.json',result)
 if error:raise RuntimeError(error)
 return result

def compare_images(folder,jobs,cases):
 rows=[];metrics=[]
 for j in jobs:
  for index in j['indices']:
   base=folder/'baseline-current'/j['id']/f'frame-{index:04d}.png'
   if not base.exists():continue
   cells=[]
   for case in cases:
    image=folder/case/j['id']/f'frame-{index:04d}.png'
    if not image.exists():continue
    metric=dict(case=case,scene=j['id'],frame=j['request']['startFrame']+index,fileIdentical=sha(base)==sha(image))
    if case!='baseline-current':
     proc=subprocess.run(['ffmpeg','-hide_banner','-i',str(base),'-i',str(image),'-lavfi','psnr','-f','null','-'],capture_output=True,text=True)
     match=re.search(r'average:([\w.]+)',proc.stderr);metric.update(psnrDb=match[1] if match else None,comparisonError=proc.stderr[-500:] if proc.returncode else None)
    metrics.append(metric);cells.append(f'<figure><img loading="lazy" width="180" src="{html.escape(str(image.relative_to(folder)))}"><figcaption>{html.escape(case)} · {html.escape(str(metric.get("psnrDb","baseline")))} dB</figcaption></figure>')
   rows.append('<h3>'+html.escape(j['id'])+' source '+str(j['request']['startFrame']+index)+'</h3><div class="row">'+''.join(cells)+'</div>')
 (folder/'comparison.html').write_text('<!doctype html><meta name="viewport" content="width=device-width"><title>Atheon paired real renders</title><style>body{background:#121722;color:white;font:16px sans-serif}.row{display:flex;overflow:auto}figure{margin:8px}img{height:auto}</style><h1>Paired Blender benchmark renders</h1><p>Review haze, portal noise, fine armor edges and temporal flicker. PSNR alone is not artistic approval.</p>'+''.join(rows))
 atomic_json(folder/'visual-differences.json',metrics)

def summarize(folder,jobs,results):
 # Never extrapolate warm caches, CPU, missing cases or changed scenes as GPU speedups.
 base=results.get('baseline-current');estimates=[]
 for name,r in results.items():
  eligible=bool(base and base['status']=='passed' and r['status']=='passed' and base['coldRun'] and r['coldRun'] and base['actualT4Rendering'] and r['actualT4Rendering'] and r['frames']>=30)
  estimates.append(dict(case=name,measuredWallSeconds=r['wallSeconds'],frames=r['frames'],eligibleForT4Projection=eligible,renderOnlyEpisodeProjectionHours=r['wallSeconds']/r['frames']*2672/3600 if eligible else None,measuredSpeedRatio=base['wallSeconds']/r['wallSeconds'] if eligible else None))
 # Samples/denoise candidates require manual visual review; no automatic quality or <6h claim.
 report=dict(results=results,estimates=estimates,fullEpisodeRerenderRecommended=False,recommendation='Keep current 48-sample Balanced settings until paired T4 measurements and visual review. Consider scratch-persistent only after verifying paired images, checkpoint recovery and export measurements.',sixHourTarget='Unverified. Render-only projection excludes full export and workload variance; benchmark export separately.',jobs=jobs,sourceCommit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),hardware=gpu_snapshot())
 atomic_json(folder/'benchmark.json',report);return report

def export_montage(folder,jobs,case,node,scratch,chrome=None):
 """Actual 30–60-frame Remotion benchmark; silent labeled montage, not pilot audio."""
 remote=folder/case;paths=[j['id']+f'/frame-{i:04d}.png' for j in jobs for i in j['indices']]
 public=remote;copy_seconds=0
 if CASES[case]['storage']=='scratch':
  public=Path(scratch)/('export-'+digest(str(remote))[:16]);public.mkdir(parents=True,exist_ok=True);ts=time.perf_counter()
  for relative in paths:
   dest=public/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(remote/relative,dest)
  copy_seconds=time.perf_counter()-ts
 width=jobs[0]['request']['width'];height=jobs[0]['request']['height'];props=remote/'export-props.json';atomic_json(props,dict(width=width,height=height,paths=paths));output=Path(scratch)/('montage-'+case+'.mp4');ts=time.perf_counter()
 cmd=[node,ROOT/'remotion/node_modules/@remotion/cli/remotion-cli.js','render',Path(__file__).with_name('perf-export.tsx'),'PerformanceMontage',output,'--props',props,'--public-dir',public,'--codec','h264','--pixel-format','yuv420p','--image-format','png','--color-space','bt709','--concurrency',1]
 if chrome:cmd+=['--browser-executable',chrome]
 run_task(cmd,remote/'remotion.log');seconds=time.perf_counter()-ts
 media=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(output)],text=True));video=next(s for s in media['streams'] if s['codec_type']=='video')
 if int(video['nb_read_frames'])!=len(paths) or video['codec_name']!='h264':raise ValueError('Benchmark export validation failed')
 ts=time.perf_counter();shutil.copyfile(output,remote/'benchmark-montage.mp4');io=time.perf_counter()-ts
 result=dict(status='passed',frames=len(paths),driveToScratchSeconds=copy_seconds,remotionCompositionAndEncodeSeconds=seconds,finalDriveCopySeconds=io,scope='Actual CLI composition + H.264 encoding including browser/bundling; stages overlap, not exclusive GPU kernel times',notPilotEpisode=True,silentBenchmark=True,sourceFootage='distinct genuinely rendered representative frames')
 atomic_json(remote/'export-result.json',result);return result

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('output');p.add_argument('--scratch',default='/content/atheon-benchmark');p.add_argument('--frames',type=int,choices=[30,36,48,60],default=30);p.add_argument('--width',type=int,default=540);p.add_argument('--height',type=int,default=960);p.add_argument('--blender',default='blender');p.add_argument('--device',choices=['auto','cpu'],default='auto');p.add_argument('--cases',nargs='+',choices=list(CASES),default=list(CASES));p.add_argument('--direction',action='store_true');p.add_argument('--node',default='node');p.add_argument('--chrome');p.add_argument('--skip-export',action='store_true');p.add_argument('--execute',action='store_true');a=p.parse_args();out=Path(a.output).resolve();
 if out.exists() and any(out.iterdir()):
  existing=out/'project.json'
  if existing.exists() and json.loads(existing.read_text()).get('kind')!='atheon-performance-benchmark':raise ValueError('Use a dedicated NEW benchmark folder; existing projects are preserved')
  if not existing.exists() and not (out/'benchmark-plan.json').exists():raise ValueError('Existing unrelated contents; use a new benchmark folder')
 out.mkdir(parents=True,exist_ok=True);jobs=jobs_for(load_package(),a.width,a.height,a.frames,a.direction);plan=dict(jobs=jobs,cases={k:CASES[k] for k in a.cases},direction=a.direction,sources=sources());path=out/'benchmark-plan.json'
 if path.exists() and json.loads(path.read_text())!=plan:raise ValueError('Existing benchmark has different sources/settings. Restore saved commit or use a fresh run folder.')
 atomic_json(path,plan)
 manifest=out/'project.json'
 source_commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
 source_dirty=bool(subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain','--',*sources()],text=True).strip())
 if not manifest.exists():atomic_json(manifest,dict(sourceCommit=source_commit,sourceDirty=source_dirty,kind='atheon-performance-benchmark',planSha256=digest(plan)))
 if a.execute and source_dirty:raise ValueError('Commit production sources before executing a reproducible benchmark')
 if not a.execute:print('Plan saved; no render started. Add --execute on Colab T4.');return
 if a.direction and 'baseline-current' in a.cases:raise ValueError('Exact legacy baseline cannot render a new direction. Benchmark original episode first; use instrumented cases only for direction comparison.')
 tools=software(a.blender,a.node,a.chrome);(out/'logs').mkdir(exist_ok=True);device=probe(out,tools)
 if a.device!='cpu' and (device['selected']!='GPU' or device.get('backend') not in ['OPTIX','CUDA']):raise ValueError('No NVIDIA backend detected. Select a T4 runtime before the benchmark; no CPU renders were started.')
 reserve=math.ceil(a.width*a.height*3*a.frames*(len(a.cases)+1)*1.08)+512*1024**2;local_need=math.ceil(a.width*a.height*3*a.frames*3*1.08)+512*1024**2
 Path(a.scratch).mkdir(parents=True,exist_ok=True)
 if shutil.disk_usage(out).free<reserve or shutil.disk_usage(a.scratch).free<local_need:raise ValueError('Insufficient reported Drive/local benchmark space; remote Drive account quota still needs manual checking.')
 a.blender=tools['blender'];a.node=tools['node'];results={}
 try:
  for name in a.cases:
   print('Benchmark case '+name,flush=True)
   results[name]=baseline(jobs,out/name,a.blender,a.device) if name=='baseline-current' else execute_profile(jobs,out/name,Path(a.scratch)/name,CASES[name],a.blender,a.device,a.device!='cpu',a.direction)
   if not a.skip_export:results[name]['export']=export_montage(out,jobs,name,a.node,Path(a.scratch),a.chrome)
 except BaseException:
  if 'name' in locals() and (out/name/'result.json').exists():results[name]=json.loads((out/name/'result.json').read_text())
  raise
 finally:summarize(out,jobs,results);compare_images(out,jobs,a.cases)
 print('Benchmark complete. Inspect benchmark.json and comparison.html before changing production settings.')
if __name__=='__main__':main()
