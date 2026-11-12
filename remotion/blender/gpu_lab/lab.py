"""Standalone, local-only T4 Optimization Lab. Production notebooks stay unchanged."""
import argparse,json,os,queue,re,shutil,signal,subprocess,sys,threading,time,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from common import *
from telemetry import Monitor


def usage(root):
 info=shutil.disk_usage(root);size=sum(p.stat().st_size for p in root.rglob('*') if p.is_file() and not p.is_symlink())
 return dict(localFreeBytes=info.free,localTotalBytes=info.total,labBytes=size)

def launch(binary,mode,plan_path,out,timeout=1800):
 out.mkdir(parents=True,exist_ok=True);log=out/'blender-log.txt';command=[str(binary),'--background','--factory-startup','--python-exit-code','1','--python',str(HERE/'worker.py'),'--',mode,str(plan_path)];started=time.perf_counter();epoch=time.time();events=[];lines=queue.Queue()
 proc=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,start_new_session=True)
 def reader():
  for line in proc.stdout:lines.put((time.time(),line))
  lines.put(None)
 thread=threading.Thread(target=reader,daemon=True);thread.start();last=0;stop=False;forced=None
 with log.open('w') as f,Monitor(out/'telemetry.jsonl',proc.pid) as monitor:
  try:
   while not stop:
    if time.perf_counter()-started>timeout:forced='timeout';raise TimeoutError('Lab case timeout')
    try:item=lines.get(timeout=.5)
    except queue.Empty:item='waiting'
    if item is None:stop=True;continue
    if item!='waiting':
     received,line=item;f.write(f'{received:.6f} '+line);f.flush()
     if line.startswith('LAB_EVENT '):
      event=json.loads(line[10:]);events.append(event);monitor.phase=event['phase']
     elif '|' in line:
      tail=line.rsplit('|',1)[-1].strip()
      if re.search('Sample|Denois|Composit|Synchron|Updating|BVH|Loading|Kernel',tail):monitor.phase=tail
    if time.perf_counter()-last>15:print(f'{out.name}: {monitor.phase} | {time.perf_counter()-started:.0f}s',flush=True);last=time.perf_counter()
   code=proc.wait(timeout=10)
  except BaseException as e:
   forced=forced or type(e).__name__
   try:os.killpg(proc.pid,signal.SIGINT)
   except ProcessLookupError:pass
   try:proc.wait(timeout=15)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
   code=proc.returncode
   if isinstance(e,KeyboardInterrupt):raise
  finally:thread.join(timeout=2)
 report=dict(invocationWallSeconds=time.perf_counter()-started,startedEpochSeconds=epoch,finishedEpochSeconds=time.time(),exitCode=code,termination=forced,telemetry=monitor.report());atomic_json(out/'invocation.json',report);atomic_json(out/'events.json',events)
 return report

def prepare(root,run_id,mode,width,height,cpu=False,cases=None):
 folder=run_folder(root,run_id);count=1 if mode=='fast' else 3;repeats=1 if mode=='fast' else 2
 plan=dict(kind='destiny-t4-lab-v1',mode=mode,width=width,height=height,repeats=repeats,jobs=jobs(width,height,count),cases=[c for c in CASES if cases is None or c['id'] in cases],sources=sources(),cpuValidation=cpu)
 if not plan['cases'] or plan['cases'][0]['id']!='baseline-48':raise ValueError('Baseline must be first and included')
 if folder.exists() and (folder/'.lab-run.json').exists():
  if read(folder/'plan.json')!=plan:raise ValueError('Run source/settings changed; use a NEW run ID or restore the saved source')
  return folder,plan
 if folder.exists() and any(folder.iterdir()):raise ValueError('Existing unrelated run contents refused')
 folder.mkdir(parents=True,exist_ok=True);atomic_json(folder/'.lab-run.json',dict(kind='destiny-t4-lab-v1',sourceCommit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),planSha256=digest(plan)));atomic_json(folder/'plan.json',plan);atomic_json(folder/'disk-before.json',usage(root));print(f'Prepared {len(plan["cases"])*3*count*repeats} total frames, {len(plan["cases"])} configurations, {repeats} trial(s). No images rendered.');return folder,plan

def capability_probe(folder,plan,binary):
 base=folder/'intermediate/probes';base.mkdir(parents=True,exist_ok=True)
 data=dict(output=str(base/'base'),jobs=plan['jobs'],cpuValidation=plan['cpuValidation']);p=base/'base-plan.json';atomic_json(p,data);result=launch(binary,'probe',p,base/'base',180)
 if result['exitCode']!=0 or not (base/'base/probe.json').exists():raise RuntimeError('Blender/T4 preflight failed. Read '+str(base/'base/blender-log.txt'))
 caps=read(base/'base/probe.json');caps['features']={}
 for feature,available in [('optix-denoiser',caps['device']['optixDenoiserSupported']),('oidn-gpu',caps['device']['oidnGpuSupported']),('gpu-compositor',not plan['cpuValidation'] and 'compositor_device' in caps['defaults'])]:
  if not available:caps['features'][feature]=dict(supported=False,reason='Device/build capability unavailable');continue
  dest=base/feature;probe_plan=base/(feature+'-plan.json');atomic_json(probe_plan,{**data,'feature':feature,'output':str(dest)});trial=launch(binary,'probe',probe_plan,dest,240)
  probe_log=(dest/'blender-log.txt').read_text(errors='replace');fallback=bool(re.search('fall.*back.*CPU|not supported.*GPU|GPU.*not supported',probe_log,re.I))
  supported=trial['exitCode']==0 and (dest/'probe.json').exists() and not fallback
  caps['features'][feature]=dict(supported=supported,probe=trial,reason=None if supported else 'Actual 32×32 probe failed or logged an unsupported/CPU fallback; feature not used')
 atomic_json(folder/'capabilities.json',caps);return caps

def run(root,folder,plan,binary):
 binary=shutil.which(str(binary))
 if not binary:raise RuntimeError('Install Blender 4.3.2 in O1 first')
 if read(folder/'plan.json')!=plan or plan['sources']!=sources():raise ValueError('Changed sources/settings; restore source or use a new run ID')
 final=folder/'final/results.json'
 if final.exists() and not (folder/'intermediate').exists():print('Run finalized; review results or use a new run ID for another cold benchmark.');return
 dirty=subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain','--',*plan['sources']],text=True).strip()
 if dirty:raise ValueError('Commit lab/renderer sources before a reproducible benchmark')
 reserve=plan['width']*plan['height']*3*sum(j['request']['frames'] for j in plan['jobs'])*len(plan['cases'])*plan['repeats']*3+32*1024**2
 if shutil.disk_usage(root).free<reserve:raise ValueError('Insufficient local space for PNGs, comparisons and ZIP')
 caps=read(folder/'capabilities.json') if (folder/'capabilities.json').exists() else capability_probe(folder,plan,binary)
 version=subprocess.check_output([binary,'--version'],text=True,timeout=30)
 results=[]
 try:
  for repeat in range(plan['repeats']):
   order=plan['cases'] if repeat%2==0 else list(reversed(plan['cases']))
   for case in order:
    settings,reason=resolved_settings(case,caps);out=folder/'intermediate'/f'trial-{repeat+1}'/case['id']
    if settings is None:results.append(dict(case=case['id'],trial=repeat+1,status='unsupported',reason=reason));continue
    identity_=digest(dict(plan=plan,case=case,settings=settings,blenderVersion=version));worker_plan=dict(output=str(out),jobs=plan['jobs'],cpuValidation=plan['cpuValidation'],settings=settings,identity=identity_);file=folder/'intermediate'/f'plan-{repeat+1}-{case["id"]}.json';file.parent.mkdir(parents=True,exist_ok=True);atomic_json(file,worker_plan)
    previous=read(out/'result.json') if (out/'result.json').exists() else None
    if previous and previous.get('identity')!=identity_:raise ValueError('Case cache identity mismatch')
    archived=out/'case-result.json'
    if previous and archived.exists() and read(archived).get('status')=='passed':
     original=read(archived);complete=len(previous['frames'])==sum(j['request']['frames'] for j in plan['jobs'])
     for key,f in previous['frames'].items():
      job=next(j for j in plan['jobs'] if j['shotId']==f['shotId']);complete=complete and valid_png(out/f['file'],job['request']['width'],job['request']['height'],f['sha256'])
     if complete:
      original['reusedCompletedTrialReport']=True;results.append(original);print('Reused original completed trial report; no frames rendered:',case['id'],flush=True);continue
    print(f'Trial {repeat+1}/{plan["repeats"]}: {case["id"]} — {settings}',flush=True);invocation=launch(binary,'render',file,out,300 if plan['mode']=='fast' else 900)
    record=read(out/'result.json') if (out/'result.json').exists() else dict(status='failed',error='No worker report',frames={},newFrames=0,cacheHits=0)
    if invocation['exitCode']!=0:record.update(status='failed',error=record.get('error','Blender exited '+str(invocation['exitCode'])))
    text=(out/'blender-log.txt').read_text(errors='replace');record.update(case=case['id'],trial=repeat+1,invocation=invocation,settingsRequested=settings,oom=bool(re.search('out of memory|CUDA_ERROR_OUT_OF_MEMORY|Failed to allocate',text,re.I)),cpuFallback=bool(record.get('device',{}).get('selected')=='CPU' and not plan['cpuValidation']),componentCpuFallback=bool(re.search('fall.*back.*CPU',text,re.I)),gpuFailure=bool(re.search('OptiX error|CUDA_ERROR|GPU.*failed',text,re.I)),configurationWarnings=[line[-500:] for line in text.splitlines() if re.search('fall.*back|not supported',line,re.I)])
    requested=sum(j['request']['frames'] for j in plan['jobs']);record['requestedFrames']=requested;record['cold']=record['newFrames']==requested and record['cacheHits']==0;record['actualT4']=record.get('device',{}).get('selected')=='GPU' and 'T4' in record.get('device',{}).get('name','') and all(f['device']['selected']=='GPU' and f['device']['backend'] in ['OPTIX','CUDA'] for f in record['frames'].values())
    # Only original cold passes remain eligible after a partial resume; warm never becomes cold.
    results.append(record);atomic_json(out/'case-result.json',record)
    atomic_json(folder/'run-progress.json',dict(status='running',results=results))
  atomic_json(folder/'run-progress.json',dict(status='finished',results=results))
 finally:atomic_json(folder/'disk-after-render.json',usage(root))


def export_configuration(folder,case_id,approved):
 if not approved:raise ValueError('O4 requires explicit user approval of performance AND visual/temporal quality')
 checks=read(folder/'final/checksums.json')
 for name in ['results.json','visual-metrics.json','plan.json']:
  if checks.get(name)!=sha(folder/'final'/name):raise ValueError('Report integrity mismatch; settings export refused')
 report=read(folder/'final/results.json')
 if report.get('renderSources')!=sources():raise ValueError('Restore the exact recorded source commit before exporting settings')
 candidate=next((c for c in report['comparisons'] if c['case']==case_id),None)
 if not candidate or not candidate['eligibleForProductionReview'] or candidate['speedRatio'] is None or candidate['speedRatio']<=1:raise ValueError('No repeated cold T4 speed improvement available for this candidate; fast, CPU, warm or failed trials cannot authorize export')
 visual=read(folder/'final/visual-metrics.json')
 if not any(r['case']==case_id for r in visual.get('temporalResiduals',[])):raise ValueError('No consecutive-frame temporal comparison available for selected case')
 payload=dict(benchmarkResolution=report['resolution'],baseline='Existing approved Balanced builder at recorded commit; apply overrides only to a NEW project',kind='destiny-reviewed-render-settings-v1',case=case_id,settings=candidate['settings'],userApprovedVisualAndTemporalQuality=True,evidenceSha256=sha(folder/'final/results.json'),sourceCommit=report['sourceCommit'],newProjectRequired=True,modifiesExistingProduction=False,automaticallyApplied=False,integration='Explicit settings recipe for a NEW cinematic project. No existing episode/cache is accessed or changed.',measuredSpeedRatio=candidate['speedRatio'],renderProjection=candidate['projection'])
 atomic_json(folder/'final/recommended-config.json',payload);archive(folder);return payload


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['prepare','run','report','export','restore']);p.add_argument('--root',default='/content/destiny-gpu-lab');p.add_argument('--run-id',default='t4-fast-01');p.add_argument('--mode',choices=['fast','standard'],default='fast');p.add_argument('--width',type=int,default=540);p.add_argument('--height',type=int,default=960);p.add_argument('--blender',default='blender');p.add_argument('--cpu-validation',action='store_true');p.add_argument('--cases',nargs='+',choices=[c['id'] for c in CASES]);p.add_argument('--keep-intermediates',action='store_true');p.add_argument('--selected-case');p.add_argument('--approved',action='store_true');p.add_argument('--archive');a=p.parse_args();root=safe_root(a.root,a.cpu_validation)
 if a.action=='restore':print(restore_zip(root,a.archive,a.run_id));return
 if a.action in ['prepare','run']:folder,plan=prepare(root,a.run_id,a.mode,a.width,a.height,a.cpu_validation,a.cases)
 else:folder=run_folder(root,a.run_id)
 if a.action=='run':run(root,folder,plan,a.blender)
 if a.action=='report':
  from reporting import make_report
  make_report(root,folder,not a.keep_intermediates)
 if a.action=='export':print(json.dumps(export_configuration(folder,a.selected_case,a.approved),indent=2))
if __name__=='__main__':main()
