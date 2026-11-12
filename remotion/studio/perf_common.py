"""Opt-in profiler provenance and resumable, per-frame scratch/Drive checkpoints."""
import contextlib,hashlib,json,os,shutil,subprocess,threading,time
from pathlib import Path
from production import ROOT
from universal.cache import atomic_json,source_hashes,valid_png

def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True).encode()).hexdigest()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def sources():
    result=source_hashes()
    for name in ['perf_common.py','profile_worker.py','performance.py','cinematic_atheon.py','cinematic_direction.py','cinematic-index.tsx','cinematic_captions.ts','complete_atheon.py','production.py','episode_timeline.ts']:
        p=Path(__file__).with_name(name)
        if p.exists():result[str(p.relative_to(ROOT))]=sha(p)
    result['remotion/package-lock.json']=sha(ROOT/'remotion/package-lock.json')
    result['episodes/atheon-explained-en/script.json']=sha(ROOT/'episodes/atheon-explained-en/script.json')
    return result

def identity(job,settings,version):
    return digest(dict(job=job,settings=settings,blenderVersion=version,sources=sources()))

def valid_record(folder,key,record,width,height):
    return bool(record and record.get('file')==f'frame-{int(key):04d}.png' and valid_png(Path(folder)/record['file'],width,height,record.get('sha256')) and record.get('sha256'))

def checkpoint(local,remote,job_id,width,height):
    """Copy only CRC/SHA-verified frames; publish manifest last, never partial PNGs.

    If disconnected mid-copy, the previous remote manifest remains resumable. Copies
    are read back and verified; Drive FUSE acceptance is not a remote durability SLA.
    """
    local=Path(local);remote=Path(remote);remote.mkdir(parents=True,exist_ok=True)
    src=json.loads((local/'profile.json').read_text())
    old=json.loads((remote/'profile.json').read_text()) if (remote/'profile.json').exists() else {}
    if src['identity']!=job_id or old and old.get('identity')!=job_id:raise ValueError('Checkpoint identity mismatch; use a new folder.')
    started=time.perf_counter();copied=0;reused=0;size=0
    for key,record in src['frames'].items():
        if not valid_record(local,key,record,width,height):raise ValueError('Invalid scratch frame: '+key)
        target=remote/record['file']
        if valid_record(remote,key,record,width,height):reused+=1;continue
        pending=target.with_suffix('.checkpoint.png');shutil.copyfile(local/record['file'],pending)
        if not valid_png(pending,width,height,record['sha256']):raise ValueError('Drive checkpoint readback failed')
        os.replace(pending,target);copied+=1;size+=target.stat().st_size
    atomic_json(remote/'profile.json',src)
    return dict(seconds=time.perf_counter()-started,copiedFrames=copied,reusedFrames=reused,bytes=size,scope='copy + readback CRC/decode/SHA + manifest; mounted filesystem, not remote server timing')

class Telemetry:
    """One-second device-wide nvidia-smi observations, never inferred from Cycles flags."""
    def __init__(self,path):self.path=Path(path);self.stop_event=threading.Event();self.samples=[];self.error=None;self.phase='initializing';self.binary=shutil.which('nvidia-smi')
    def poll(self):
        if not self.binary:self.error='nvidia-smi unavailable';return
        try:
            text=subprocess.check_output([self.binary,'--query-gpu=uuid,name,utilization.gpu,utilization.memory,memory.used,memory.total,power.draw','--format=csv,noheader,nounits'],text=True,timeout=3)
            for line in text.splitlines():
                uuid,name,util,memutil,used,total,power=[x.strip() for x in line.split(',')]
                def number(v):
                    try:return float(v)
                    except ValueError:return None
                item=dict(epochSeconds=time.time(),phase=self.phase,uuid=uuid,name=name,gpuUtilPercent=number(util),memoryUtilPercent=number(memutil),usedMiB=number(used),totalMiB=number(total),powerWatts=number(power));self.samples.append(item)
                with self.path.open('a') as f:f.write(json.dumps(item)+'\n')
        except (OSError,ValueError,subprocess.SubprocessError) as error:self.error=str(error)
    def loop(self):
        while not self.stop_event.is_set():self.poll();self.stop_event.wait(1)
    def __enter__(self):self.path.parent.mkdir(parents=True,exist_ok=True);self.thread=threading.Thread(target=self.loop,daemon=True);self.thread.start();return self
    def __exit__(self,*args):self.stop_event.set();self.thread.join(timeout=4)
    def report(self):
        util=[s['gpuUtilPercent'] for s in self.samples if s['gpuUtilPercent'] is not None];mem=[s['usedMiB'] for s in self.samples if s['usedMiB'] is not None]
        return dict(scope='Device-wide ~1s polling; includes other processes, sampled peaks only; no attribution to a single process',samples=len(self.samples),peakMemoryMiB=max(mem,default=None),meanUtilizationPercent=sum(util)/len(util) if util else None,error=self.error)
