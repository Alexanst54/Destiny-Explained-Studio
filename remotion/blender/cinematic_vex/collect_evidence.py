"""Collect only successful real Blender outputs; preserve their original PNG/report bytes."""
import argparse,ast,datetime,hashlib,json,os,platform,shutil,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cinematic_vex.provenance import render_signature
from characters.vex_bosses import generate
ROOT=Path(__file__).resolve().parents[3]


def collect(source,output,native_log=None,compat_log=None):
    source=Path(source);out=Path(output);out.mkdir(parents=True,exist_ok=True)
    config=json.loads(Path(__file__).with_name('validation_shots.json').read_text())
    for name in ['before','after','reports','clips']: (out/name).mkdir(exist_ok=True)
    sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
    e={'version':'0.9.1','status':'complete','checkedAt':datetime.datetime.now(datetime.timezone.utc).date().isoformat(),'baseline':config['baseline'],'stills':[],'clips':[],'geometryCounts':{},'renderInputHashes':{}}
    sig=render_signature(ROOT)
    for key,value in sig.items():e['renderInputHashes']['remotion/blender/cinematic_vex/comparison_worker.py' if key=='comparison_worker' else 'remotion/blender/'+key]=value
    key='remotion/blender/cinematic_vex/validation_shots.json';e['renderInputHashes'][key]=sha(ROOT/key)
    before_e=json.loads((ROOT/'docs/previews/venus-vault/evidence.json').read_text());e['protectedInputHashes']=before_e['protectedInputHashes']
    e['historicalGalleryHashes']={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'docs/previews/venus-vault').rglob('*') if p.is_file()}
    for shot in config['stills']:
        pair={'id':shot['id'],'definition':shot}
        for phase in ['before','after']:
            src=source/phase/shot['id'];report_path=src/'render-report.json';report=json.loads(report_path.read_text())
            if report['status']!='success' or report.get('phase')!=phase:raise ValueError('Not an actual completed render: '+str(src))
            png=src/'frame-0000.png'
            if sha(png)!=report['pngSha256']:raise ValueError('Rendered PNG differs: '+str(png))
            dest=out/phase/(shot['id']+'.png');shutil.copy2(png,dest)
            report_name='reports/'+shot['id']+'-'+phase+'.json';shutil.copy2(report_path,out/report_name)
            pair[phase]={'png':str(dest.relative_to(out)),'report':report_name,'sha256':report['pngSha256'],'reportSha256':sha(out/report_name)}
        e['stills'].append(pair)
    for definition in config['clips']:
        src=source/'clips'/definition['id'];report_path=src/'render-report.json';report=json.loads(report_path.read_text());run=json.loads((src/'run-report.json').read_text());r=report['request']
        if report['status']!=run['status'] or report['status']!='success' or len(report['frames'])!=r['frames']:raise ValueError('Incomplete animated render: '+str(src))
        if r['quality']!='balanced' or r.get('lod')!=0:raise ValueError('Proof clips require Balanced / full LOD 0')
        name=definition['id'];video=out/'clips'/(name+'.mp4');shutil.copy2(src/'sequence.mp4',video)
        rp='reports/'+name+'-clip.json';shutil.copy2(report_path,out/rp)
        item={'id':name,'definition':definition,'report':rp,'reportSha256':sha(out/rp),'video':str(video.relative_to(out)),'videoSha256':sha(video),'pngs':[]}
        # Use a swinging-foot pose for walk, and a raised-energy pose for temporal.
        indices=[0,18,r['frames']-1] if name=='walk' else [0,r['frames']//2,r['frames']-1]
        for index in indices:
            path=out/'clips'/f'{name}-{index:04d}.png';shutil.copy2(src/f'frame-{index:04d}.png',path)
            frame=report['frames'][index]
            if sha(path)!=frame['sha256']:raise ValueError('Animation PNG differs')
            item['pngs'].append({'png':str(path.relative_to(out)),'index':index,'sourceFrame':frame['frame'],'sha256':frame['sha256']})
        e['clips'].append(item)
    for boss in ['boss-atheon','boss-templar']:e['geometryCounts'][boss]=[{'lod':lod,'boxes':len(generate(boss,lod=lod)['objects']),'joints':len(generate(boss,lod=lod)['joints'])} for lod in range(3)]
    if native_log:
        for line in Path(native_log).read_text().splitlines():
            if line.startswith('CINEMATIC_CHECK '):e['nativeBlenderCheck']=ast.literal_eval(line.removeprefix('CINEMATIC_CHECK '))
    if compat_log:
        e['compatibilityBlenderCheck']=next(line for line in Path(compat_log).read_text().splitlines() if line.startswith('VENUS_VAULT_CHECK '))
    configs=[]
    for pair in e['stills']:
        configs += [json.loads((out/pair[phase]['report']).read_text())['configuration'] for phase in ['before','after']]
    configs += [json.loads((out/item['report']).read_text())['configuration'] for item in e['clips']]
    observations=[]
    for c in configs:
        record={key:c.get(key) for key in ['selected','backend','devices','threads']}
        if record not in observations:observations.append(record)
    cpu=platform.processor() or 'unknown'
    if Path('/proc/cpuinfo').exists():cpu=next((line.split(':',1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines() if line.startswith('model name')),cpu)
    e['hardware']={'platform':platform.platform(),'cpu':cpu,'logicalCpusAvailable':len(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else os.cpu_count(),'renderDeviceObservations':observations,'gpuMemoryAndUtilization':None,'timingScope':'Validation runs with possible CPU contention, not controlled comparative performance benchmarks.'}
    (out/'evidence.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n')
    return e


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('--output',default=str(ROOT/'docs/previews/cinematic-vex-0.9.1'));p.add_argument('--native-log',required=True);p.add_argument('--compat-log',required=True);a=p.parse_args()
    e=collect(a.source,a.output,a.native_log,a.compat_log);print('Collected',len(e['stills']),'Cinematic pairs and',len(e['clips']),'Balanced clips')

if __name__=='__main__':main()
