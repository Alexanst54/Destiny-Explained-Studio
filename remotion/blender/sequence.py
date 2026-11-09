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
import zlib
from telemetry import GpuMonitor
from contract import load
from environments.riis import generate
from render_one import render_one, stream_process
ROOT=Path(__file__).resolve().parents[1]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(data):return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def atomic(path,data):
    path=Path(path);temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(data,indent=2)+'\n');temp.replace(path)
def png_valid(path,width,height):
    """Check CRCs and decode the complete non-interlaced RGBA/RGB PNG stream."""
    try:
        data=Path(path).read_bytes()
        if data[:8]!=b'\x89PNG\r\n\x1a\n':return False
        pos=8;compressed=[];header=None;ended=False
        while pos<len(data):
            length=struct.unpack('>I',data[pos:pos+4])[0];kind=data[pos+4:pos+8]
            body=data[pos+8:pos+8+length];crc=data[pos+8+length:pos+12+length]
            if len(body)!=length or len(crc)!=4 or zlib.crc32(kind+body)!=struct.unpack('>I',crc)[0]:return False
            if header is None and kind!=b'IHDR':return False
            if kind==b'IHDR':
                if header is not None:return False
                header=struct.unpack('>IIBBBBB',body)
            elif kind==b'IDAT':compressed.append(body)
            elif kind==b'IEND':
                if length or pos+12!=len(data):return False
                ended=True;break
            pos+=length+12
        if not ended or not header or header[:2]!=(width,height):return False
        w,h,bits,color,compression,filtering,interlace=header
        if bits!=8 or color not in (2,6) or compression or filtering or interlace:return False
        stride=1+w*(4 if color==6 else 3)
        decoder=zlib.decompressobj();raw=decoder.decompress(b''.join(compressed),h*stride+1)
        return decoder.eof and not decoder.unused_data and len(raw)==h*stride and all(raw[i*stride]<=4 for i in range(h))
    except (OSError,struct.error,zlib.error):return False

def cache_hit(folder,index,key,width,height):
    png=folder/f'{index:05d}.png';done=png.with_suffix('.done.json')
    try:
        d=json.loads(done.read_text());return d['key']==key and png_valid(png,width,height) and d['pngSha256']==sha(png)
    except (OSError,ValueError,KeyError):return False

def run(project,cache,start=120,count=90,detail='draft',scale=10,device='auto',seed=42,lighting='dawn',timeout=180,node='node',blender='blender',threads=2,max_new=90,public=None,renderer='persistent',fallback=True):
    if type(start) is not int or start<0 or type(count) is not int or not 1<=count<=90 or type(scale) is not int or scale not in [10,25,50,100] or type(max_new) is not int or not 1<=max_new<=90:raise ValueError('Invalid sequence range/scale/work limit')
    if renderer not in ['persistent','single']:raise ValueError('Invalid renderer')
    if device not in ['auto','cpu'] or type(timeout) is not int or not 1<=timeout<=7200 or type(threads) is not int or not 1<=threads<=64:raise ValueError('Invalid rendering options')
    version=subprocess.check_output([blender,'--version'],text=True,timeout=15).splitlines()[0]
    renderer_hashes={p:sha(Path(__file__).parent/p) for p in ['import_scene.py','contract.py','render_one.py','environments/riis.py','sequence.py','persistent_scene.py','render_batch.py','telemetry.py']}
    with tempfile.TemporaryDirectory() as temporary:
        command=[node,'--experimental-strip-types',str(Path(__file__).with_name('export-sequence.mjs')),str(Path(project).resolve()),str(start),str(count),temporary]
        subprocess.run(command,check=True,timeout=120)
        frames=[generate(load(Path(temporary)/f'{i:05d}.json'),detail,seed,lighting) for i in range(count)]
    identity={'version':1,'snapshots':[digest(d) for d in frames],'renderer':renderer_hashes,'blender':version,'scale':scale,'device':device,'threads':threads,'rendererMode':renderer}
    if scale==100:
        approved=False
        for candidate in Path(cache).glob('*/identity.json'):
            try:
                previous=json.loads(candidate.read_text());other={**previous,'scale':100}
                if previous['scale']<100 and other==identity and all(cache_hit(candidate.parent,i,identity['snapshots'][i],1080*previous['scale']//100,1920*previous['scale']//100) for i in range(count)):approved=True;break
            except (OSError,ValueError,KeyError):continue
        if not approved:raise ValueError('Full HD requires a complete matching lower-resolution preview in this cache first')
    key=digest(identity);folder=Path(cache).resolve()/key;folder.mkdir(parents=True,exist_ok=True)
    width=1080*scale//100;height=1920*scale//100;started=time.monotonic();new=0;hits=0;monitor=GpuMonitor()
    print(f'SEQUENCE {count} frames / {count/30}s at 30fps, {width}×{height}, {detail}; cache {folder}',flush=True)
    for i,data in enumerate(frames):atomic(folder/f'{i:05d}.json',data)
    atomic(folder/'identity.json',identity)
    report={'version':1,'key':key,'projectId':frames[0]['source']['projectId'],'startFrame':start,'count':count,'fps':30,'detail':detail,'scale':scale,'width':width,'height':height,'status':'incomplete','cache':str(folder),'rendererMode':renderer,'fallbacks':[]}
    def save():
        report.update(completed=sum(cache_hit(folder,i,identity['snapshots'][i],width,height) for i in range(count)),newFrames=new,cacheHits=hits,wallSeconds=round(time.monotonic()-started,3),gpu=monitor.report());atomic(folder/'sequence-report.json',report)
    pending=[i for i in range(count) if not cache_hit(folder,i,identity['snapshots'][i],width,height)]
    hits=count-len(pending);work=pending[:max_new]
    def collect():
        nonlocal new
        monitor.poll()
        completed=[i for i in work if i not in observed and cache_hit(folder,i,identity['snapshots'][i],width,height)]
        observed.update(completed);new+=len(completed)
        if completed:
            save();print(f'PROGRESS {report["completed"]}/{count}',flush=True)
        return bool(completed)
    observed=set()
    try:
        for i in work:
            png=folder/f'{i:05d}.png'
            png.unlink(missing_ok=True);png.with_suffix('.done.json').unlink(missing_ok=True)
        if renderer=='persistent' and work:
            # Unique session artifacts retain crash evidence across resumes.
            session=folder/f'batch-{time.time_ns()}'
            job=session.with_suffix('.json')
            atomic(job,{'indices':work,'device':device,'scale':scale,'threads':threads})
            command=[blender,'--background','--factory-startup','--python-exit-code','1','--python',str(Path(__file__).with_name('render_batch.py')),'--',str(job)]
            try:
                stream_process(command,session.with_suffix('.log'),timeout,on_tick=collect)
                collect()
                if len(observed)!=len(work):raise RuntimeError('Batch exited without all completed frames')
            except (RuntimeError,TimeoutError,OSError) as error:
                collect();report['fallbacks'].append({'error':str(error),'log':str(session.with_suffix('.log'))});save()
                if not fallback:raise
        for i in work:
            if i in observed:continue
            png=folder/f'{i:05d}.png'
            png.unlink(missing_ok=True);png.with_suffix('.done.json').unlink(missing_ok=True)
            result=render_one(folder/f'{i:05d}.json',png,blender,device,scale,threads,timeout)
            if not png_valid(png,width,height):raise RuntimeError('Invalid rendered PNG')
            atomic(png.with_suffix('.done.json'),{'key':identity['snapshots'][i],'pngSha256':sha(png),'configuration':result['report']['configuration']})
            collect()
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
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('project');p.add_argument('cache');p.add_argument('--start',type=int,default=120);p.add_argument('--count',type=int,default=90);p.add_argument('--detail',choices=['draft','balanced','cinematic'],default='draft');p.add_argument('--scale',type=int,choices=[10,25,50,100],default=10);p.add_argument('--device',choices=['auto','cpu'],default='auto');p.add_argument('--seed',type=int,default=42);p.add_argument('--lighting',choices=['dawn','blue-hour'],default='dawn');p.add_argument('--timeout',type=int,default=180);p.add_argument('--threads',type=int,default=2);p.add_argument('--max-new',type=int,default=90);p.add_argument('--node',default='node');p.add_argument('--blender',default='blender');p.add_argument('--renderer',choices=['persistent','single'],default='persistent');p.add_argument('--no-fallback',action='store_true');p.add_argument('--public',default=str(ROOT/'public'));a=p.parse_args();run(a.project,a.cache,a.start,a.count,a.detail,a.scale,a.device,a.seed,a.lighting,a.timeout,a.node,a.blender,a.threads,a.max_new,a.public,a.renderer,not a.no_fallback)
if __name__=='__main__':main()
