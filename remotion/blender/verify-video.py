import json,hashlib,subprocess
from pathlib import Path
import numpy as np
import argparse
p=argparse.ArgumentParser(description='Validate the 120–209 Riis demo, including Kokoro audio offset; requires existing TTS numpy dependency.')
p.add_argument('project');p.add_argument('cache');p.add_argument('video');p.add_argument('output');args=p.parse_args()
root=Path(__file__).resolve().parents[1];folder=Path(args.cache);video=Path(args.video);project=json.loads(Path(args.project).read_text())
report=json.loads((folder/'sequence-report.json').read_text())
if report['startFrame']!=120 or report['count']!=90 or report['status']!='complete':raise ValueError('Expected complete demo frames 120–209')
def pcm(path,start=None):
 cmd=['ffmpeg','-v','error','-i',str(path)]
 if start is not None:cmd+=['-ss',str(start),'-t','3']
 return np.frombuffer(subprocess.check_output(cmd+['-ac','1','-ar','24000','-f','f32le','-']),dtype=np.float32)
a=pcm(root/'public'/project['audio']['voiceover']['source'],4);b=pcm(video)[:len(a)];best=(-2,None)
for lag in range(-1200,1201,24):
 x=a[max(0,lag):min(len(a),len(b)+lag)];y=b[max(0,-lag):min(len(b),len(a)-lag)]
 if len(x)>100:
  r=float(np.corrcoef(x,y)[0,1])
  if r>best[0]:best=(r,lag/24)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
first=json.loads((folder/'00000.json').read_text());last=json.loads((folder/'00089.json').read_text());hashval=lambda d:hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
benchmarks=[json.loads((folder/f'{i:05d}.benchmark.json').read_text()) for i in range(90)]
result={'probe':probe,'pngFrameCount':90,'fps':30,'sourceRange':[120,209],'videoSha256':hashlib.sha256(video.read_bytes()).hexdigest(),'pngHashesUnique':len(set(hashlib.sha256((folder/f'{i:05d}.png').read_bytes()).hexdigest() for i in range(90))),'sixActorsEveryFrame':all(len(json.loads((folder/f'{i:05d}.json').read_text())['actors'])==6 for i in range(90)),'cameraChanges':first['camera']!=last['camera'],'posesChange':first['actors']!=last['actors'],'environmentGeometryUnchanged':hashval([m for m in first['meshes'] if m['id'].startswith('riis/')])==hashval([m for m in last['meshes'] if m['id'].startswith('riis/')]),'audioCorrelation':best[0],'bestLagMilliseconds':best[1],'audioComparison':'Decoded mono 24kHz MP4 vs original Kokoro WAV source 4–7s; ±50ms scan in 1ms increments. Not a human alignment annotation.','sequenceWallSeconds':report['wallSeconds'],'sequenceTimingScope':'Current invocation only; excludes export/preparation and prior resumed invocations','maxBlenderRssKiB':max(r['report']['maxProcessRssKiB'] for r in benchmarks),'effectiveDevices':sorted(set(r['report']['configuration']['selected'] for r in benchmarks)),'rendererWallTime':'Remotion external wall duration not instrumented; no claim made.','limitations':['CPU Draft 108×192 only; no new GPU or remote Colab test.','AAC padding produces 3.008-second container duration; video frames span exactly 3s.']}
assert probe['streams'][0]['nb_frames']=='90' and best[0]>.9 and result['cameraChanges'] and result['posesChange'] and result['environmentGeometryUnchanged']
Path(args.output).write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='probe'})
