"""Kill only our own Blender worker after a real checkpoint, then test recovery/cache integrity."""
import argparse,json,os,signal,subprocess,sys,time
from pathlib import Path
sys.path[:]=[p for p in sys.path if Path(p).resolve()!=Path(__file__).resolve().parent]
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from universal.cache import atomic_json,source_hashes

def main():
 p=argparse.ArgumentParser();p.add_argument('output');p.add_argument('--blender',default='blender');a=p.parse_args();base=Path(a.output).resolve()
 if base.exists():raise ValueError('Use a new recovery-test directory')
 base.mkdir(parents=True);out=base/'rhulk';cli=Path(__file__).resolve().parents[1]/'render_universal.py'
 cmd=[sys.executable,str(cli),'boss-rhulk',str(out),'--view','cinematic','--animation','combat','--quality','draft','--lod','0','--width','320','--height','240','--frames','4','--fps','24','--blender',a.blender,'--timeout','300']
 with (base/'interruption.log').open('w') as log:
  proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);deadline=time.monotonic()+180;killed=None
  while time.monotonic()<deadline:
   if proc.poll() is not None:raise RuntimeError('Controller completed before forced interruption')
   try:r=json.loads((out/'progress.json').read_text())
   except (FileNotFoundError,json.JSONDecodeError):r={}
   if 1<=len(r.get('frames',{}))<4:
    children=subprocess.run(['ps','-o','pid=','--ppid',str(proc.pid)],capture_output=True,text=True,check=False).stdout.split()
    for child in children:
     command=Path('/proc')/child/'cmdline'
     if command.exists():
      line=command.read_bytes().replace(b'\0',b' ').decode()
      if 'universal/worker.py' in line and str(out) in line:
       killed=int(child);os.killpg(os.getpgid(killed),signal.SIGKILL);break
    if killed:break
   time.sleep(.1)
  if not killed:proc.terminate();raise RuntimeError('No eligible owned Blender checkpoint worker found')
  assert proc.wait(timeout=30)!=0
 partial=json.loads((out/'progress.json').read_text());hits=len(partial['frames']);assert partial['status']=='failed' and 1<=hits<4
 def run(extra):
  with (base/'resume.log').open('a') as log:subprocess.run(cmd+extra,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
  return json.loads((out/'progress.json').read_text())
 resumed=run(['--resume']);assert resumed['status']=='success' and resumed['cacheHits']==hits and resumed['renderedThisRun']==4-hits
 hashes={k:f['sha256'] for k,f in resumed['frames'].items()};warm=run(['--resume']);assert warm['cacheHits']==4 and warm['renderedThisRun']==0 and warm['configuration']['designCacheHit']
 (out/'frame-0002.png').write_bytes(b'broken');fixed=run(['--resume']);assert fixed['cacheHits']==3 and fixed['renderedThisRun']==1
 assert all(fixed['frames'][k]['sha256']==v for k,v in hashes.items() if k!='2')
 before=(out/'progress.json').read_bytes();bad=subprocess.run(cmd+['--resume','--seed','43'],capture_output=True,text=True,timeout=30);assert bad.returncode!=0 and 'mismatch' in bad.stderr.lower() and (out/'progress.json').read_bytes()==before
 atomic_json(base/'result.json',dict(status='passed',bossId='boss-rhulk',blenderWorkerKilled=killed,checkpointFrames=hits,resumedCacheHits=hits,newAfterResume=4-hits,warmCacheHits=4,corruptFrameCacheHits=3,corruptFrameNewRenders=1,unchangedOtherFrames=True,changedSeedRejected=True,sourceHashes=source_hashes(),gpuValidated=False))
 print('LOT_C_RECOVERY passed')
if __name__=='__main__':main()
