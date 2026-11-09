"""Select a supported Atlas ID and render a bounded original Venus/Vault scene."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from venus_vault.request import select
from render_one import stream_process


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('selection');p.add_argument('output')
    p.add_argument('--lod',type=int,choices=[0,1,2],default=0);p.add_argument('--quality',choices=['draft','balanced','cinematic'],default='balanced');p.add_argument('--seed',type=int,default=42)
    p.add_argument('--camera',choices=['wide','reveal','orbit','low-angle','close-up','front','profile','ground-reveal','mechanism','temporal'],default='wide');p.add_argument('--animation',default='idle')
    p.add_argument('--start-frame',type=int,default=0);p.add_argument('--frames',type=int,default=1);p.add_argument('--fps',type=int,choices=[24,30],default=30);p.add_argument('--width',type=int,default=960);p.add_argument('--height',type=int,default=540)
    p.add_argument('--device',choices=['auto','cpu'],default='auto');p.add_argument('--threads',type=int,default=3);p.add_argument('--timeout',type=int,default=1800)
    p.add_argument('--blender',default='blender');p.add_argument('--video',action='store_true');p.add_argument('--check-only',action='store_true');a=p.parse_args()
    request=select(a.selection,a.quality,a.seed,a.camera,a.animation,a.frames,a.fps,a.width,a.height,a.start_frame,a.lod)
    if a.video and (a.frames<2 or a.check_only):p.error('--video requires at least two rendered frames')
    binary=shutil.which(a.blender)
    if not binary:raise RuntimeError('Blender not found')
    if a.video and not shutil.which('ffmpeg'):raise RuntimeError('ffmpeg required for MP4')
    if not 1<=a.threads<=64:p.error('--threads must be 1–64')
    out=Path(a.output).resolve()
    if out.exists():raise ValueError('Choose a new output directory to prevent stale evidence')
    out.mkdir(parents=True);req=out/'request.json';req.write_text(json.dumps(request,indent=2)+'\n')
    command=[binary,'--background','--factory-startup','--python-exit-code','1','--python',str(Path(__file__).parent/'venus_vault/renderer.py'),'--',str(req),str(out),'--device',a.device,'--threads',str(a.threads)]
    if a.check_only:command.append('--check-only')
    outcome={'command':command,'status':'failed','timeoutSeconds':a.timeout}
    try:
        outcome['wallSeconds']=stream_process(command,out/'blender.log',a.timeout)
        report=json.loads((out/'render-report.json').read_text())
        if report['status']!=('checked-only' if a.check_only else 'success') or not a.check_only and len(report['frames'])!=a.frames:raise RuntimeError('Incomplete render')
        if a.video:
            video=out/'sequence.mp4'
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-framerate',str(a.fps),'-start_number','0','-i',str(out/'frame-%04d.png'),'-frames:v',str(a.frames),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True,timeout=120)
            outcome['video']={'file':video.name,'bytes':video.stat().st_size,'audio':'none — visual asset test; no narration/timeline changed'}
        outcome['status']='success'
    except Exception as error:outcome['error']=str(error);raise
    finally:(out/'run-report.json').write_text(json.dumps(outcome,indent=2)+'\n')

if __name__=='__main__':main()
