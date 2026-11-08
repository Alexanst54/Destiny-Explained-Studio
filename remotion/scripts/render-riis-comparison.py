"""Render the unchanged 0.5 reference and 0.6 sequentially with identical CPU settings."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'out/riis-comparison'

def worker(args):
    source = 'out/hybrid_riis-ready.json' if args.worker == '0.5' else 'out/hybrid_riis_06-ready.json'
    episode = json.loads((ROOT/source).read_text())
    if episode['format']['durationFrames'] != 1050:
        raise ValueError('Comparison requires 1050 frames, not a partial or retimed project')
    if args.worker == '0.6' and episode['shorts']['polish']['quality'] != 'final':
        raise ValueError('Comparison requires final quality')
    command = [args.node, '--experimental-strip-types', 'scripts/episode.mjs', 'render', source, '--concurrency=1']
    if args.browser:
        command.append('--browser-executable='+args.browser)
    started = time.monotonic()
    with (OUTPUT/(args.worker+'-render.log')).open('w') as log:
        process = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    elapsed = time.monotonic()-started
    rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    result = dict(version=args.worker, exitCode=process.returncode, wallSeconds=round(elapsed, 2), maxChildRssKiB=rss,
                  concurrency=1, gl='swangle', memoryScope='Maximum observed child RSS; not total concurrent Chromium memory')
    if process.returncode == 0:
        video = ROOT/episode['render']['output']
        result['bytes'] = video.stat().st_size
        result['sha256'] = hashlib.sha256(video.read_bytes()).hexdigest()
        result['probe'] = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries',
            'stream=codec_name,width,height,r_frame_rate,nb_frames,duration,sample_rate,channels','-show_entries','format=duration,size','-of','json',str(video)]))
    print(json.dumps(result))
    return process.returncode

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', default='node')
    parser.add_argument('--browser')
    parser.add_argument('--worker', choices=['0.5','0.6'])
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if args.worker:
        return worker(args)
    results=[]
    for version in ['0.5','0.6']:
        command=[sys.executable,str(Path(__file__).resolve()),'--worker',version,'--node',args.node]
        if args.browser: command += ['--browser',args.browser]
        run=subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        if run.stdout: results.append(json.loads(run.stdout))
        (OUTPUT/'performance.json').write_text(json.dumps(dict(renders=results, note='Sequential runs with the same voice, timestamps, browser and concurrency; results depend on machine load.'),indent=2)+'\n')
        if run.returncode:
            print(run.stderr or 'Render failed; inspect the version render log.',file=sys.stderr)
            return run.returncode
        print(version,results[-1]['wallSeconds'],'seconds',flush=True)
    return 0

if __name__ == '__main__':
    sys.exit(main())
