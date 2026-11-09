"""Opt-in universal Atlas selection, provenance cache and persistent Blender rendering."""
import argparse,fcntl,hashlib,json,shutil,subprocess,time
from pathlib import Path
from universal.registry import index
from universal.request import request,VIEWS
from universal.cache import atomic_json,fingerprint,valid_png,source_hashes
from render_one import stream_process

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('selection',nargs='?');p.add_argument('output',nargs='?');p.add_argument('--index',action='store_true');p.add_argument('--check-only',action='store_true')
    p.add_argument('--quality',choices=['draft','balanced','cinematic'],default='balanced');p.add_argument('--lod',type=int,choices=[0,1,2],default=0);p.add_argument('--seed',type=int,default=42);p.add_argument('--frames',type=int,default=1);p.add_argument('--fps',type=int,choices=[24,30],default=24);p.add_argument('--width',type=int,default=640);p.add_argument('--height',type=int,default=800);p.add_argument('--start-frame',type=int,default=0)
    p.add_argument('--view',choices=VIEWS,default='environment');p.add_argument('--animation',default='idle');p.add_argument('--arena');p.add_argument('--variant');p.add_argument('--family-study',action='store_true');p.add_argument('--family');p.add_argument('--environment-variant',choices=['sanctum','causeway','courtyard'],default='sanctum')
    p.add_argument('--blender',default='blender');p.add_argument('--device',choices=['auto','cpu'],default='auto');p.add_argument('--threads',type=int,default=3);p.add_argument('--timeout',type=int,default=1800);p.add_argument('--resume',action='store_true');p.add_argument('--video',action='store_true');a=p.parse_args()
    if a.index:print(json.dumps(index(),ensure_ascii=False,indent=2));return
    if not a.selection:p.error('An Atlas ID is required')
    r=request(a.selection,a.quality,a.seed,a.lod,a.frames,a.fps,a.width,a.height,a.start_frame,a.animation,a.view,a.arena,a.variant,a.family_study,a.family,a.environment_variant)
    if a.check_only:print(json.dumps(r,ensure_ascii=False,indent=2));return
    if not a.output:p.error('Output directory required')
    if not 1<=a.threads<=64 or a.timeout<1:p.error('Invalid threads or timeout')
    if a.video and a.frames<2:p.error('--video requires multiple frames')
    binary=shutil.which(a.blender)
    if not binary:raise RuntimeError('Blender not found')
    if a.video and not shutil.which('ffmpeg'):raise RuntimeError('ffmpeg required')
    out=Path(a.output).resolve();exists=out.exists()
    if exists and not a.resume:raise ValueError('Output exists; --resume required')
    out.mkdir(parents=True,exist_ok=True)
    with (out/'render.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        # Blender version is part of identity; changing a binary invalidates old cached frames.
        version=subprocess.run([binary,'--version'],check=True,capture_output=True,text=True,timeout=30).stdout
        identity=hashlib.sha256((fingerprint(r,a.device,a.threads)+version).encode()).hexdigest();progress=out/'progress.json'
        if exists:
            if not progress.exists():raise ValueError('No trusted progress manifest; use a new directory')
            report=json.loads(progress.read_text())
            if report.get('fingerprint')!=identity:raise ValueError('Source/request/Blender mismatch; use a new directory')
        else:report=dict(version=1,fingerprint=identity,request=r,sources=source_hashes(),frames={})
        report.update(status='running',cacheHits=0,renderedThisRun=0);report.pop('error',None);atomic_json(out/'request.json',r);atomic_json(progress,report)
        started=time.monotonic()
        try:
            command=[binary,'--background','--factory-startup','--python-exit-code','1','--python',str(Path(__file__).parent/'universal/worker.py'),'--',str(out),a.device,str(a.threads)]
            stream_process(command,out/('blender-'+str(time.time_ns())+'.log'),a.timeout)
            report=json.loads(progress.read_text())
            if report['status']!='success' or len(report['frames'])!=a.frames:raise RuntimeError('Incomplete worker output')
            for i in range(a.frames):
                f=report['frames'][str(i)]
                if not valid_png(out/f['file'],a.width,a.height,f['sha256']):raise RuntimeError('Invalid completed frame')
            if a.video:
                tmp=out/'pending.mp4';subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(a.fps),'-i',str(out/'frame-%04d.png'),'-frames:v',str(a.frames),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(tmp)],check=True,timeout=120);tmp.replace(out/'sequence.mp4');report['video']={'file':'sequence.mp4','sha256':hashlib.sha256((out/'sequence.mp4').read_bytes()).hexdigest(),'audio':'none'}
        except Exception as err:
            report=json.loads(progress.read_text());report.update(status='failed',error=str(err));raise
        finally:
            report['lastRunWallSeconds']=time.monotonic()-started;atomic_json(progress,report)
        print(json.dumps({k:report[k] for k in ['status','cacheHits','renderedThisRun','lastRunWallSeconds']}))

if __name__=='__main__':main()
