"""Resumable 1–90 frame Cycles sequence. Persistent cache; atomic per-frame completion."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import time
from contract import load
from environments.riis import generate
from render_one import render_one
ROOT=Path(__file__).resolve().parents[1]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(data):return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def atomic(path,data):
    path=Path(path);temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(data,indent=2)+'\n');temp.replace(path)
def png_valid(path,width,height):
    try:
        data=Path(path).read_bytes();return data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(width,height) and b'IEND' in data[-12:]
    except (OSError,struct.error):return False

def cache_hit(folder,index,key,width,height):
    png=folder/f'{index:05d}.png';done=png.with_suffix('.done.json')
    try:
        d=json.loads(done.read_text());return d['key']==key and png_valid(png,width,height) and d['pngSha256']==sha(png)
    except (OSError,ValueError,KeyError):return False

def run(project,cache,start=120,count=90,detail='draft',scale=10,device='auto',seed=42,lighting='dawn',timeout=180,node='node',blender='blender',threads=2,max_new=90,public=None):
    if type(start) is not int or start<0 or type(count) is not int or not 1<=count<=90 or type(scale) is not int or scale not in [10,25,50,100] or type(max_new) is not int or not 1<=max_new<=90:raise ValueError('Invalid sequence range/scale/work limit')
    if device not in ['auto','cpu'] or type(timeout) is not int or not 1<=timeout<=7200 or type(threads) is not int or not 1<=threads<=64:raise ValueError('Invalid rendering options')
    version=subprocess.check_output([blender,'--version'],text=True,timeout=15).splitlines()[0]
    renderer={p:sha(Path(__file__).parent/p) for p in ['import_scene.py','contract.py','render_one.py','environments/riis.py','sequence.py']}
    with tempfile.TemporaryDirectory() as temporary:
        command=[node,'--experimental-strip-types',str(Path(__file__).with_name('export-sequence.mjs')),str(Path(project).resolve()),str(start),str(count),temporary]
        subprocess.run(command,check=True,timeout=120)
        frames=[generate(load(Path(temporary)/f'{i:05d}.json'),detail,seed,lighting) for i in range(count)]
    identity={'version':1,'snapshots':[digest(d) for d in frames],'renderer':renderer,'blender':version,'scale':scale,'device':device,'threads':threads}
    if scale==100:
        approved=False
        for candidate in Path(cache).glob('*/identity.json'):
            try:
                previous=json.loads(candidate.read_text());other={**previous,'scale':100}
                if previous['scale']<100 and other==identity and all(cache_hit(candidate.parent,i,identity['snapshots'][i],1080*previous['scale']//100,1920*previous['scale']//100) for i in range(count)):approved=True;break
            except (OSError,ValueError,KeyError):continue
        if not approved:raise ValueError('Full HD requires a complete matching lower-resolution preview in this cache first')
    key=digest(identity);folder=Path(cache).resolve()/key;folder.mkdir(parents=True,exist_ok=True)
    width=1080*scale//100;height=1920*scale//100;started=time.monotonic();new=0;hits=0
    print(f'SEQUENCE {count} frames / {count/30}s at 30fps, {width}×{height}, {detail}; cache {folder}',flush=True)
    for i,data in enumerate(frames):atomic(folder/f'{i:05d}.json',data)
    atomic(folder/'identity.json',identity)
    report={'version':1,'key':key,'projectId':frames[0]['source']['projectId'],'startFrame':start,'count':count,'fps':30,'detail':detail,'scale':scale,'width':width,'height':height,'status':'incomplete','cache':str(folder)}
    def save():
        report.update(completed=sum(cache_hit(folder,i,identity['snapshots'][i],width,height) for i in range(count)),newFrames=new,cacheHits=hits,wallSeconds=round(time.monotonic()-started,3));atomic(folder/'sequence-report.json',report)
    try:
        for i,data in enumerate(frames):
            framekey=identity['snapshots'][i];png=folder/f'{i:05d}.png'
            if cache_hit(folder,i,framekey,width,height):hits+=1;print(f'CACHE {i+1}/{count}',flush=True);continue
            if new>=max_new:print('Work limit reached; resume the same command.',flush=True);break
            # Incomplete outputs never count as cached; retain failure logs until the retry starts.
            png.unlink(missing_ok=True);png.with_suffix('.done.json').unlink(missing_ok=True)
            print(f'RENDER {i+1}/{count}, source frame {start+i}; {count-i} remaining',flush=True)
            result=render_one(folder/f'{i:05d}.json',png,blender,device,scale,threads,timeout)
            if not png_valid(png,width,height):raise RuntimeError('Invalid rendered PNG')
            atomic(png.with_suffix('.done.json'),{'key':framekey,'pngSha256':sha(png),'configuration':result['report']['configuration']});new+=1;save()
            print(f'PROGRESS {report["completed"]}/{count}; new-frame mean {report["wallSeconds"]/new:.2f}s; rough remaining {(count-report["completed"])*report["wallSeconds"]/new:.1f}s',flush=True)
        save()
        if report['completed']==count:
            report['status']='complete'
            if public:
                target=Path(public)/'assets/blender-video'/key;target.mkdir(parents=True,exist_ok=True)
                for i in range(count):shutil.copy2(folder/f'{i:05d}.png',target/f'{i:05d}.png')
                manifest={'version':1,'fps':30,'projectId':report['projectId'],'clips':[{'startFrame':start,'width':width,'height':height,'frames':[f'assets/blender-video/{key}/{i:05d}.png' for i in range(count)]}]}
                atomic(folder/'remotion-sequences.json',manifest)
    except BaseException as error:
        report['error']=str(error);save();raise
    finally:save()
    print('SEQUENCE_RESULT '+json.dumps(report),flush=True);return folder,report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('project');p.add_argument('cache');p.add_argument('--start',type=int,default=120);p.add_argument('--count',type=int,default=90);p.add_argument('--detail',choices=['draft','balanced','cinematic'],default='draft');p.add_argument('--scale',type=int,choices=[10,25,50,100],default=10);p.add_argument('--device',choices=['auto','cpu'],default='auto');p.add_argument('--seed',type=int,default=42);p.add_argument('--lighting',choices=['dawn','blue-hour'],default='dawn');p.add_argument('--timeout',type=int,default=180);p.add_argument('--threads',type=int,default=2);p.add_argument('--max-new',type=int,default=90);p.add_argument('--node',default='node');p.add_argument('--blender',default='blender');p.add_argument('--public',default=str(ROOT/'public'));a=p.parse_args();run(a.project,a.cache,a.start,a.count,a.detail,a.scale,a.device,a.seed,a.lighting,a.timeout,a.node,a.blender,a.threads,a.max_new,a.public)
if __name__=='__main__':main()
