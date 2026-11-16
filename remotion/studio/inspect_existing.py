"""Read-only diagnosis of the user's completed PR25 episode; never renders/modifies it."""
import argparse,collections,json,statistics,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from perf_common import atomic_json,sha,valid_png


def inspect(folder,verify_cache=False):
 folder=Path(folder).resolve();project=json.loads((folder/'project.json').read_text());chunks=[];frames=[];verification_seconds=0;invalid=[];devices=collections.Counter();resolutions=collections.Counter()
 for path in sorted((folder/'public/scenes').glob('*/frames/chunk-*/progress.json')):
  started=time.perf_counter();r=json.loads(path.read_text());elapsed=time.perf_counter()-started;rwidth=r['request']['width'];rheight=r['request']['height'];resolutions[str((rwidth,rheight,r['request']['fps']))]+=len(r['frames'])
  chunks.append(dict(path=str(path.relative_to(folder)),status=r.get('status'),frames=len(r['frames']),buildSeconds=r.get('buildSeconds'),workerSeconds=r.get('workerSeconds'),lastRunWallSeconds=r.get('lastRunWallSeconds'),peakProcessRssKiB=r.get('peakProcessRssKiB'),manifestReadSeconds=elapsed))
  for key,f in r['frames'].items():
   devices[str((f.get('device',r.get('configuration',{})).get('selected'),f.get('device',r.get('configuration',{})).get('backend'),f.get('device',r.get('configuration',{})).get('devices')))]+=1
   if f.get('seconds') is not None:frames.append(f['seconds'])
   if verify_cache:
    ts=time.perf_counter();safe=f.get('file')==f'frame-{int(key):04d}.png'
    if not safe or not valid_png(path.parent/f['file'],rwidth,rheight,f.get('sha256')):invalid.append(str(path.relative_to(folder))+':'+key)
    verification_seconds+=time.perf_counter()-ts
 if not chunks:raise ValueError('No PR25 chunk manifests found; select the completed original episode folder')
 old=folder/'atheon-episode-01.validation.json';validation=json.loads(old.read_text()) if old.exists() else None
 def total(key):
  values=[c[key] for c in chunks if c.get(key) is not None];return sum(values) if len(values)==len(chunks) else None
 return dict(kind='read-only-existing-episode-diagnosis',newGpuBenchmark=False,newRenderingPerformed=False,sourceCommit=project.get('sourceCommit'),projectFingerprint=project.get('fingerprint'),recordedFrames=sum(c['frames'] for c in chunks),resolutionsAndFps=dict(resolutions),recordedDeviceDistribution=dict(devices),recordedBuildSeconds=total('buildSeconds'),recordedWorkerSeconds=total('workerSeconds'),recordedLastInvocationWallSeconds=total('lastRunWallSeconds'),recordedRenderSaveVerifyFrameSeconds=sum(frames) if frames else None,recordedMedianFrameSeconds=statistics.median(frames) if frames else None,recordedP90FrameSeconds=sorted(frames)[min(len(frames)-1,int(len(frames)*.9))] if frames else None,manifestReadSeconds=total('manifestReadSeconds'),cacheVerificationPerformed=verify_cache,cacheVerificationSeconds=verification_seconds if verify_cache else None,invalidFrames=invalid,existingFinalReport=validation,chunks=chunks,limits=['Stored times may refer to different invocations, reused frames, retries or sessions; sums are NOT a measured end-to-end wall clock.','Original frame seconds combine render, PNG save and verification; they cannot retrospectively split exclusive phases.','No historic GPU utilization series or Remotion wall clock is inferred if absent.','Completion report is read as archived evidence, not newly validated video acceptance.'])


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('episode');p.add_argument('report');p.add_argument('--verify-cache',action='store_true');a=p.parse_args();episode=Path(a.episode).resolve();report=Path(a.report).resolve()
 if report==episode or episode in report.parents:raise ValueError('Write the diagnostic report OUTSIDE the completed episode to preserve it exactly')
 result=inspect(episode,a.verify_cache);result['inspectorSourceSha256']=sha(__file__);report.parent.mkdir(parents=True,exist_ok=True);atomic_json(report,result);print(json.dumps({k:v for k,v in result.items() if k not in ['existingFinalReport','chunks']},indent=2))
if __name__=='__main__':main()
