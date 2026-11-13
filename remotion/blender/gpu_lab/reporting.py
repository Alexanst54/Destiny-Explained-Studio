"""Real-image quality comparisons and cautious cold-T4 recommendations."""
import functools,html,json,math,re,shutil,statistics,subprocess,time
from pathlib import Path
from common import *


def ffmpeg(args):
 args=list(map(str,args));args=args[:-1]+['-threads','1',args[-1]]
 p=subprocess.run(['ffmpeg','-hide_banner','-loglevel','info','-threads','1',*args],capture_output=True,text=True,timeout=90)
 if p.returncode:raise RuntimeError(p.stderr[-1500:])
 return p.stderr

def compare(a,b,out):
 out.parent.mkdir(parents=True,exist_ok=True)
 fixed=['-i',a,'-i',b,'-filter_complex_threads','1']
 psnr=ffmpeg(fixed+['-filter_complex','[0:v]format=gbrp[a];[1:v]format=gbrp[b];[a][b]psnr','-f','null','-'])
 ssim=ffmpeg(fixed+['-filter_complex','[0:v]format=gbrp[a];[1:v]format=gbrp[b];[a][b]ssim','-f','null','-'])
 p=re.search(r'average:([\w.]+)',psnr);s=re.search(r'All:([\d.]+)',ssim)
 ffmpeg(['-y',*fixed,'-filter_complex','[0:v][1:v]blend=all_mode=difference,lutrgb=r=val*4:g=val*4:b=val*4','-frames:v','1',str(out)+'-diff.png'])
 ffmpeg(['-y',*fixed,'-filter_complex','[0:v][1:v]hstack=inputs=2','-frames:v','1',str(out)+'-pair.png'])
 return dict(psnrDb=float(p[1]) if p and p[1]!='inf' else None,psnrInfinite=bool(p and p[1]=='inf'),ssim=float(s[1]) if s else None,differenceMapGain=4,scope='FFmpeg RGB PSNR/SSIM against 48-sample baseline, not ground truth or artistic approval')

@functools.lru_cache(maxsize=8)
def rgb(path):
 return subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',path,'-f','rawvideo','-pix_fmt','rgb24','-threads','1','-'])

def residual_flicker(base_prev,base_now,cand_prev,cand_now):
 bp,b,cp,c=[rgb(str(p)) for p in [base_prev,base_now,cand_prev,cand_now]]
 if not(len(bp)==len(b)==len(cp)==len(c)):raise ValueError('Temporal comparison dimensions differ')
 return dict(normalizedResidualDeltaRms=math.sqrt(sum(((x-xp)-(y-yp))**2 for x,xp,y,yp in zip(c,cp,b,bp))/len(b))/255,scope='Change in candidate-minus-baseline residual between consecutive source frames; contains noise/motion errors, not a proof of temporal equivalence')

def stages(log):
 result={};last=0;previous=None
 for line in Path(log).read_text(errors='replace').splitlines():
  m=re.search(r'Time:(\d+):(\d+(?:\.\d+)?)',line)
  if not m:continue
  elapsed=int(m[1])*60+float(m[2]);tail=line.rsplit('|',1)[-1]
  if elapsed<last:last=0;previous=None
  if previous:result[previous]=result.get(previous,0)+max(0,elapsed-last)
  previous='denoising' if 'Denois' in tail else 'sampling' if re.search('Sample|Rendering',tail) else 'compositing' if 'Composit' in tail else 'sync-bvh-kernels' if re.search('Updating|Synchron|BVH|Loading|Kernel',tail) else 'other';last=elapsed
 return dict(approximatePrintedClockSeconds=result,scope='Rounded Blender progress deltas overlap operation wall; not exclusive GPU kernel, transfer or denoiser timing')

def eligible(r):
 return r.get('status')=='passed' and r.get('cold') and r.get('actualT4') and not r.get('cpuFallback') and not r.get('componentCpuFallback') and not r.get('gpuFailure') and not r.get('oom') and len(r.get('frames',{}))==r.get('requestedFrames') and r.get('invocation',{}).get('exitCode')==0

def aggregate(plan,results):
 baseline=[r for r in results if r['case']=='baseline-48'];out=[]
 for case in plan['cases']:
  group=[r for r in results if r['case']==case['id']];paired=[];invariant=True
  for r in group:
   b=next((b for b in baseline if b['trial']==r['trial']),None)
   if not b:continue
   if set(b.get('frames',{}))!=set(r.get('frames',{})):invariant=False;continue
   for key,f in r.get('frames',{}).items():
    if f['fixedSceneSignature']!=b['frames'][key]['fixedSceneSignature']:invariant=False
   ids=r.get('invocation',{}).get('telemetry',{}).get('gpuUuids');same_gpu=bool(ids) and ids==b.get('invocation',{}).get('telemetry',{}).get('gpuUuids') and r.get('device',{}).get('backend')==b.get('device',{}).get('backend') and r.get('device',{}).get('id')==b.get('device',{}).get('id')
   if eligible(r) and eligible(b) and same_gpu and invariant:paired.append(b['invocation']['invocationWallSeconds']/r['invocation']['invocationWallSeconds'])
  mean=statistics.median([r['invocation']['invocationWallSeconds'] for r in group if r.get('status')=='passed']) if any(r.get('status')=='passed' for r in group) else None
  rates=[f['renderOperationSeconds'] for r in group if eligible(r) for f in r.get('frames',{}).values()]
  projection=None
  if rates and paired:
   per_shot={j['id']:statistics.median([f['renderOperationSeconds'] for r in group if eligible(r) for f in r['frames'].values() if f['shotId']==j['shotId']]) for j in plan['jobs']}
   projection=dict(renderOperationOnlyHours=statistics.mean(per_shot.values())*2672/3600,representativeShotRateEnvelopeHours=[min(per_shot.values())*2672/3600,max(per_shot.values())*2672/3600],completeProductionHours=None,scope='Coarse 3-shot extrapolation of Cycles+compositor only; excludes PNG/update/Drive checkpoints/Remotion/audio/export. Not a confidence interval; Templar and remaining shot complexity unmeasured.')
  usable=all(j['request']['frames']>=3 for j in plan['jobs']) and plan['mode']=='standard' and len(paired)==plan['repeats'] and len(group)==plan['repeats'] and invariant and all(eligible(r) for r in group) and all(ratio>1.02 for ratio in paired) and statistics.median(paired)>=1.05
  out.append(dict(case=case['id'],status=[r.get('status') for r in group],recordedMeanRenderOperationSecondsPerFrame=statistics.mean([f['renderOperationSeconds'] for r in group for f in r.get('frames',{}).values()]) if any(r.get('frames') for r in group) else None,medianInvocationSeconds=mean,speedRatio=statistics.median(paired) if paired else None,pairedTrialRatios=paired,sceneIdentityMatchesBaseline=invariant,eligibleForProductionReview=bool(usable and case['id']!='baseline-48'),settings=group[0].get('settingsRequested') if group else None,projection=projection,qualityApproved=False,visualReviewRequired=True))
 return out


def phase_totals(record):
 frames=list(record.get('frames',{}).values())
 return dict(renderCompositorWallSeconds=sum(f.get('renderOperationSeconds',0) for f in frames),pngEncodeWriteWallSeconds=sum(f.get('pngEncodeWriteSeconds',0) for f in frames),updateWallSeconds=sum(f.get('updateWallSeconds',0) for f in frames),verificationSeconds=sum(f.get('verificationSeconds',0) for f in frames),renderProcessCpuSeconds=sum(f.get('cpu',{}).get('render',{}).get('processCpuSeconds',0) for f in frames),schedulerThreadQueueSeconds=sum(f.get('cpu',{}).get('render',{}).get('threadRunQueueWaitSeconds') or 0 for f in frames),exclusiveGpuKernelSeconds=None,transferSeconds=None,scope='Stored original per-frame values; after resume cached frames retain their creation timings. CPU/thread/operation totals overlap and must not be summed as exclusive wall phases.')

def graph(samples):
 gpu=[s for s in samples if s['kind']=='gpu' and s.get('utilizationPercent') is not None]
 if not gpu:return '<p>No GPU samples: utilization/power/VRAM are unavailable, not zero.</p>'
 start=min(s['epochSeconds'] for s in gpu);span=max(s['epochSeconds'] for s in gpu)-start or 1
 points=' '.join(f'{(s["epochSeconds"]-start)/span*600:.1f},{100-s["utilizationPercent"]:.1f}' for s in gpu)
 return '<svg viewBox="0 0 600 110" role="img" aria-label="Sampled device-wide GPU utilization"><polyline points="'+points+'" fill="none" stroke="#78d8ff" stroke-width="1.5"/></svg><small>Device-wide sampled GPU utilization, 0–100%; short bursts may be missed.</small>'


def make_report(root,folder,clean=True):
 from lab import usage
 plan=read(folder/'plan.json');progress=read(folder/'run-progress.json');results=progress['results'];final=folder/'final';final.mkdir(exist_ok=True)
 # If intermediates were cleaned, preserve and repackage the existing completed report.
 if not (folder/'intermediate').exists() and (final/'results.json').exists():return archive(folder)
 comparisons=aggregate(plan,results);visual=[];rows=[];temporal=[];artifacts=final/'images';artifacts.mkdir(exist_ok=True)
 for r in results:
  if r.get('status') not in ['passed','failed']:continue
  source=folder/'intermediate'/f'trial-{r["trial"]}'/r['case'];target=final/'telemetry'/f'trial-{r["trial"]}'/r['case'];target.mkdir(parents=True,exist_ok=True)
  for name in ['case-result.json','result.json','events.json','telemetry.jsonl','blender-log.txt','invocation.json']:
   if (source/name).exists():shutil.copyfile(source/name,target/name)
  if (source/'blender-log.txt').exists():r['observableStages']=stages(source/'blender-log.txt')
  for key,f in r.get('frames',{}).items():
   path=source/f['file']
   job=next(j for j in plan['jobs'] if j['shotId']==f['shotId']);req=job['request']
   if not valid_png(path,req['width'],req['height'],f['sha256']):raise ValueError('Bad source frame in quality report')
 for case in plan['cases']:
  if case['id']=='baseline-48':continue
  for trial in range(1,plan['repeats']+1):
   b=next((r for r in results if r['case']=='baseline-48' and r['trial']==trial and r['status']=='passed'),None);c=next((r for r in results if r['case']==case['id'] and r['trial']==trial and r['status']=='passed'),None)
   if not b or not c:continue
   for job in plan['jobs']:
    prev=None
    for i in range(job['request']['frames']):
     key=job['id']+'/'+str(i);bf=b['frames'][key];cf=c['frames'][key];a=folder/'intermediate'/f'trial-{trial}'/'baseline-48'/bf['file'];d=folder/'intermediate'/f'trial-{trial}'/case['id']/cf['file'];dest=artifacts/f'trial-{trial}'/case['id']/f'{job["id"]}-{i}';metric=compare(a,d,dest);metric.update(case=case['id'],trial=trial,shot=job['shotId'],sourceFrame=bf['sourceFrame']);visual.append(metric)
     if prev:temporal.append(dict(case=case['id'],trial=trial,shot=job['shotId'],**residual_flicker(prev[0],a,prev[1],d)))
     prev=(a,d)
     pair=str(Path(str(dest)+'-pair.png').relative_to(final));diff=str(Path(str(dest)+'-diff.png').relative_to(final));rows.append('<section><h3>'+html.escape(f'{case["id"]} · trial {trial} · {job["shotId"]} · source {bf["sourceFrame"]}')+'</h3><p>Baseline left / candidate right. PSNR '+html.escape(str(metric['psnrDb'] if not metric['psnrInfinite'] else '∞'))+' dB · SSIM '+str(metric['ssim'])+'</p><img loading="lazy" src="'+pair+'"><details><summary>Difference map ×4</summary><img loading="lazy" src="'+diff+'"></details></section>')
 atomic_json(final/'visual-metrics.json',dict(images=visual,temporalResiduals=temporal,temporalEvidenceAvailable=bool(temporal),warning='PSNR/SSIM/residuals do not prove visual equivalence. Fast mode has no consecutive-frame flicker evidence.'))
 caps=read(folder/'capabilities.json');atomic_json(final/'capabilities.json',caps);atomic_json(final/'plan.json',plan);source_commit=read(folder/'.lab-run.json')['sourceCommit']
 report=dict(kind='destiny-gpu-lab-report-v1',reportGeneratorSha256=sha(__file__),sourceCommit=source_commit,renderSources=plan['sources'],resolution=[plan['width'],plan['height']],mode=plan['mode'],cpuValidation=plan['cpuValidation'],comparisons=comparisons,results=results,visualReviewRequired=True,qualityApproved=False,temporalEvidenceAvailable=bool(temporal),recommendation='Retain existing Balanced/48 production settings until repeated cold T4 trials improve timing and the user approves visual/temporal quality. O4 exports only an eligible reviewed configuration; nothing is applied automatically.',knownLimits=['Render operation includes GPU/CPU synchronization, sampling, denoising and compositing. No exclusive GPU kernel or transfer timing is fabricated.','Printed Blender phase deltas are approximate. CPU thread wait is not blocking GPU wait.','No Drive, Remotion or narration is exercised by this isolated local-storage lab.','Fast trial timing is exploratory; standard mode adds 3 consecutive frames per shot and reversed trial order.','Only three shots tested; all 19 shots need production art validation before any full rerender.'])
 atomic_json(final/'results.json',report)
 heads=['Case','Status','Median wall s','Mean render/frame s','Paired T4 ratio','Render-only projection h','Production-review eligible']
 table='<table><tr>'+''.join('<th>'+h+'</th>' for h in heads)+'</tr>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in [c['case'],c['status'],c['medianInvocationSeconds'],c['recordedMeanRenderOperationSecondsPerFrame'],c['speedRatio'],c['projection']['renderOperationOnlyHours'] if c['projection'] else None,c['eligibleForProductionReview']])+'</tr>' for c in comparisons)+'</table>'
 telemetry=''
 for r in results:
  path=final/'telemetry'/f'trial-{r["trial"]}'/r['case']/'telemetry.jsonl'
  if path.exists():telemetry+='<h3>'+html.escape(r['case']+' / '+str(r['trial']))+'</h3>'+graph([json.loads(line) for line in path.read_text().splitlines()])
 (final/'index.html').write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Destiny T4 Optimization Lab</title><style>body{max-width:1100px;margin:auto;padding:16px;background:#111827;color:#e8edf6;font:16px system-ui}img{max-width:100%;height:auto}table{display:block;overflow:auto;border-collapse:collapse}td,th{padding:9px;border:1px solid #526071}section{border-top:1px solid #526071;padding-top:8px}summary{cursor:pointer}pre{white-space:pre-wrap}svg{max-width:100%;background:#223044}</style></head><body><h1>Destiny T4 Optimization Lab</h1><p>'+html.escape(report['recommendation'])+'</p><p>CPU validation only: '+str(plan['cpuValidation'])+' · Mode: '+plan['mode']+'. Ratios are null without comparable cold T4 passes. No Actions, Drive, voice downloads or episode export.</p>'+table+'<h2>Measured phase details and limitations</h2><pre>'+html.escape(json.dumps([dict(case=r['case'],trial=r['trial'],status=r['status'],reason=r.get('reason'),wall=r.get('invocation',{}).get('invocationWallSeconds'),telemetry=r.get('invocation',{}).get('telemetry'),build=r.get('build'),actualSettings=r.get('actualSettings'),actualDevice=r.get('device'),phaseTotals=phase_totals(r),newFrames=r.get('newFrames'),cacheHits=r.get('cacheHits'),cold=r.get('cold'),gpuFailure=r.get('gpuFailure'),cpuFallback=r.get('cpuFallback'),oom=r.get('oom'),observableStages=r.get('observableStages')) for r in results],indent=2))+'</pre><h2>Quality review</h2><p>Inspect metal detail, Vex glow, portals, volumetrics, shadows, noisy edges and consecutive-frame flicker. Baseline is 48 samples, not a noiseless ground truth. In fast mode temporal validation is unavailable.</p>'+''.join(rows)+'<h3>Consecutive-frame residual comparisons</h3><pre>'+html.escape(json.dumps(temporal,indent=2) if temporal else 'Unavailable in fast mode; no flicker approval possible.')+'</pre><h2>Telemetry</h2>'+telemetry+'</body></html>')
 # Preserve probe logs (including capability failures) and disk measurements in the ZIP.
 if (folder/'intermediate/probes').exists():shutil.copytree(folder/'intermediate/probes',final/'capability-probes',dirs_exist_ok=True)
 for name in ['disk-before.json','disk-after-render.json']:
  if (folder/name).exists():shutil.copyfile(folder/name,final/name)
 zip_path=archive(folder)
 can_clean=all(r['status'] in ['passed','unsupported'] for r in results) and progress['status']=='finished'
 removed=cleanup(root,folder) if clean and can_clean else 0
 atomic_json(final/'disk-after-report.json',dict(**usage(root),deletedDisposableBytes=removed,intermediatesRetained=bool((folder/'intermediate').exists()),temporaryStorageWarning='/content disappears when Colab resets; download the ZIP.'))
 zip_path=archive(folder);print('Report:',final/'index.html','ZIP:',zip_path,'deleted intermediates:',removed);return zip_path
