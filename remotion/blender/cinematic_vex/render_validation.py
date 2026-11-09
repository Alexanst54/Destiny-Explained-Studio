"""Render six real Cinematic before/after pairs and two Balanced clips; bounded jobs only."""
import argparse,hashlib,json,subprocess,sys,tarfile,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cinematic_vex.provenance import render_signature
from venus_vault.camera import camera_pose
from render_one import stream_process
ROOT=Path(__file__).resolve().parents[3]


def shot_spec(shot,phase):
    spec=dict(shot);c=camera_pose('arena-glass-throne' if shot['selection']=='boss-atheon' else 'arena-templars-well',shot['camera'])
    if phase=='before' and shot.get('beforeVerticalAlignment'):
        dz=shot['beforeVerticalAlignment'];c['position']=list(c['position']);c['target']=list(c['target']);c['position'][2]+=dz;c['target'][2]+=dz
    spec['sharedCamera']=c
    return json.loads(json.dumps(spec))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output');p.add_argument('--blender',default='blender');p.add_argument('--phase',choices=['before','after','clips','all'],default='all');p.add_argument('--shot');p.add_argument('--resume',action='store_true');a=p.parse_args()
    config=json.loads(Path(__file__).with_name('validation_shots.json').read_text());out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    baseline=out/'baseline'
    if a.phase in ['before','all'] and not baseline.exists():
        # A full copy of the exact committed source, never a rebuilt imitation of 'before'.
        archive=out/'baseline.tar';subprocess.run(['git','-C',str(ROOT),'archive','--output',str(archive),config['baseline']],check=True)
        baseline.mkdir()
        with tarfile.open(archive) as tf:tf.extractall(baseline,filter='data')
    phases=['before','after'] if a.phase=='all' else [a.phase]
    for phase in phases:
        if phase=='clips':continue
        for shot in config['stills']:
            if a.shot and shot['id']!=a.shot:continue
            dest=out/phase/shot['id']
            if (dest/'render-report.json').exists():
                report=json.loads((dest/'render-report.json').read_text())
                if report.get('status')=='success' and a.resume:
                    root=baseline if phase=='before' else ROOT
                    png=dest/'frame-0000.png'
                    if report.get('shot')!=shot_spec(shot,phase):raise ValueError('Cached framing or dimensions differ: '+str(dest))
                    if report.get('sourceInputHashes')!=render_signature(root) or not png.is_file() or hashlib.sha256(png.read_bytes()).hexdigest()!=report.get('pngSha256'):raise ValueError('Stale source or damaged PNG: '+str(dest))
                    print('Validated cached shot:',dest,flush=True);continue
                raise ValueError('Existing output requires a fresh directory or validated --resume: '+str(dest))
            dest.mkdir(parents=True,exist_ok=True);spec=shot_spec(shot,phase);request=dest/'shot.json';request.write_text(json.dumps(spec,indent=2)+'\n')
            cmd=[a.blender,'--background','--factory-startup','--python-exit-code','1','--python',str(Path(__file__).with_name('comparison_worker.py')),'--','--source',str(baseline if phase=='before' else ROOT),'--phase',phase,'--shot',str(request),'--output',str(dest)]
            seconds=stream_process(cmd,dest/'blender.log',timeout=3600);(dest/'run-report.json').write_text(json.dumps({'command':cmd,'wallSeconds':seconds,'status':'success'},indent=2)+'\n')
    if a.phase in ['clips','all']:
        for clip in config['clips']:
            if a.shot and clip['id']!=a.shot:continue
            dest=out/'clips'/clip['id']
            if dest.exists():raise ValueError('Choose a fresh clip directory; interrupted clips are not silently reused')
            cmd=[sys.executable,str(ROOT/'remotion/blender/render_venus_vault.py'),clip['selection'],str(dest),'--blender',a.blender,'--quality',clip['quality'],'--lod',str(clip['lod']),'--animation',clip['animation'],'--camera',clip['camera'],'--width',str(clip['width']),'--height',str(clip['height']),'--fps',str(clip['fps']),'--frames',str(clip['frames']),'--start-frame',str(clip['startFrame']),'--video','--timeout','7200']
            subprocess.run(cmd,check=True)

if __name__=='__main__':main()
