"""Cold-cache v0.8.3 vs persistent v0.8.4, sequentially on the same host.

Default matrix: 90 frames at 30 FPS, draft/10%, balanced/25%, cinematic/50%.
The baseline must be a separate checkout with its npm dependencies installed.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from sequence import atomic, sha
from telemetry import GpuMonitor


def revision(root):
    return subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()


def compare_pixels(a,b):
    try:
        from PIL import Image, ImageChops, ImageStat
    except ImportError:
        return {'status':'unavailable','reason':'Install Pillow for decoded pixel comparisons.'}
    maxima=[];means=[];identical=0
    for i in range(90):
        with Image.open(a/f'{i:05d}.png') as x,Image.open(b/f'{i:05d}.png') as y:
            diff=ImageChops.difference(x.convert('RGBA'),y.convert('RGBA'))
            extrema=diff.getextrema();maximum=max(high for low,high in extrema)
            identical+=maximum==0;maxima.append(maximum);means.append(sum(ImageStat.Stat(diff).mean[:3])/3)
    return {'status':'measured','frames':90,'identicalDecodedFrames':identical,'maxChannelError8bit':max(maxima),'meanAbsoluteRgbError8bit':sum(means)/90,'scope':'Decoded image comparison; does not validate narration, captions or subjective quality.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('project');p.add_argument('output');p.add_argument('--baseline-root',required=True)
    p.add_argument('--qualities',nargs='+',choices=['draft','balanced','cinematic'],default=['draft','balanced','cinematic'])
    p.add_argument('--device',choices=['auto','cpu'],default='auto');p.add_argument('--blender',default='blender');p.add_argument('--node',default='node');p.add_argument('--threads',type=int,default=2);p.add_argument('--timeout',type=int,default=600)
    args=p.parse_args();current=Path(__file__).resolve().parents[2];baseline=Path(args.baseline_root).resolve()
    if baseline==current:raise ValueError('Baseline must be a separate v0.8.3 checkout')
    output=Path(args.output).resolve()
    if output.exists():raise ValueError('Use a fresh output directory: cold caches are required')
    output.mkdir(parents=True)
    evidence={'status':'running','projectSha256':sha(args.project),'baselineRevision':revision(baseline),'candidateRevision':revision(current),'candidateDiff':subprocess.check_output(['git','-C',str(current),'diff','--stat'],text=True),'platform':platform.platform(),'cpuModel':next((s.split(':',1)[1].strip() for s in Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name')),None),'cpuAffinity':sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None,'blender':subprocess.check_output([args.blender,'--version'],text=True).splitlines()[0],'node':subprocess.check_output([args.node,'--version'],text=True).strip(),'frameCount':90,'fps':30,'seed':42,'lighting':'dawn','deviceRequested':args.device,'threads':args.threads,'results':[],'limitations':['Sequential single trial per quality, baseline first; repeat with reversed order to assess host variability.','GPU telemetry is device-wide sampled data, not process-exclusive peaks.','No GPU speed claim unless both successful runs actually rendered all frames on GPU with matching devices/backends.']}
    atomic(output/'benchmark.json',evidence)
    try:
        for detail in args.qualities:
            pair={};scale={'draft':10,'balanced':25,'cinematic':50}[detail]
            for mode,root in [('baseline',baseline),('persistent',current)]:
                destination=output/detail/mode;destination.mkdir(parents=True)
                command=[sys.executable,str(root/'remotion/blender/sequence.py'),str(Path(args.project).resolve()),str(destination/'cache'),'--count','90','--start','120','--detail',detail,'--scale',str(scale),'--device',args.device,'--threads',str(args.threads),'--timeout',str(args.timeout),'--seed','42','--lighting','dawn','--node',args.node,'--blender',args.blender,'--public',str(destination/'public')]
                if mode=='persistent':command+=['--renderer','persistent','--no-fallback']
                monitor=GpuMonitor();started=time.monotonic()
                with (destination/'controller.log').open('w') as log:
                    process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
                    try:
                        while process.poll() is None:
                            monitor.poll()
                            if time.monotonic()-started>90*args.timeout+180:raise TimeoutError('Benchmark controller exceeded total budget')
                            try:process.wait(timeout=.5)
                            except subprocess.TimeoutExpired:pass
                        if process.returncode:raise RuntimeError(f'{mode} failed: see {destination}/controller.log')
                    finally:
                        if process.poll() is None:
                            process.terminate();process.wait(timeout=15)
                wall=time.monotonic()-started
                folders=list((destination/'cache').glob('*/sequence-report.json'))
                if len(folders)!=1:raise RuntimeError('Expected exactly one job')
                folder=folders[0].parent;report=json.loads(folders[0].read_text())
                if report['status']!='complete' or report['cacheHits'] or report['newFrames']!=90 or report.get('fallbacks'):raise RuntimeError('Invalid benchmark: incomplete, warm cache or fallback')
                reports=[json.loads((folder/f'{i:05d}.report.json').read_text()) for i in range(90)]
                configs=[r['configuration'] for r in reports]
                gpu_ids={(c['selected'],c['backend'],tuple(c['devices'])) for c in configs}
                row={'quality':detail,'scale':scale,'mode':mode,'folder':str(folder),'command':command,'totalSeconds':wall,'averageSecondsPerFrame':wall/90,'sequenceSeconds':report['wallSeconds'],'peakBlenderRssKiB':max(r['maxProcessRssKiB'] for r in reports),'gpu':monitor.report(),'effectiveConfigurations':[list(v[:2])+[list(v[2])] for v in sorted(gpu_ids)],'allFramesGpu':all(c['selected']=='GPU' for c in configs)}
                pair[mode]=row;evidence['results'].append(row);atomic(output/'benchmark.json',evidence)
            a=Path(pair['baseline']['folder']);b=Path(pair['persistent']['folder'])
            if any(sha(a/f'{i:05d}.json')!=sha(b/f'{i:05d}.json') for i in range(90)):raise RuntimeError('Snapshot inputs differ; comparison invalid')
            comparison={'quality':detail,'baselineOverPersistent':pair['baseline']['totalSeconds']/pair['persistent']['totalSeconds'],'pixels':compare_pixels(a,b),'gpuComparisonEligible':pair['baseline']['allFramesGpu'] and pair['persistent']['allFramesGpu'] and pair['baseline']['effectiveConfigurations']==pair['persistent']['effectiveConfigurations']}
            evidence.setdefault('comparisons',[]).append(comparison);atomic(output/'benchmark.json',evidence)
        evidence['status']='complete'
    except BaseException as error:
        evidence.update(status='failed',error=str(error));raise
    finally:atomic(output/'benchmark.json',evidence)
    print(json.dumps(evidence,indent=2))


if __name__=='__main__':main()
