"""Copy only decoded, hashed Blender studies; never promotes Atlas model status."""
import json,hashlib,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from universal.registry import ROOT,families
from universal.cache import valid_png,atomic_json
from universal.environments import generate
from venus_vault.geometry import digest

def collect(source):
    out=ROOT/'docs/universal-library/studies';out.mkdir(parents=True,exist_ok=True);evidence=[]
    for f in families():
        folder=Path(source)/f['id'];r=json.loads((folder/'progress.json').read_text());req=r['request'];frame=r['frames']['0'];p=folder/frame['file']
        if r['status']!='success' or req['binding']['provider']!='family-study' or req['binding']['familyId']!=f['id'] or not valid_png(p,req['width'],req['height'],frame['sha256']):raise ValueError('Missing/invalid Blender family study '+f['id'])
        spec=generate(f['id'],req['seed'],req['quality'],req['lod'],req['environmentVariant'])
        if r['configuration']['designSha256']!=digest(spec):raise ValueError('Stale design')
        shutil.copyfile(p,out/(f['id']+'.png'));shutil.copyfile(folder/'progress.json',out/(f['id']+'-report.json'))
        evidence.append(dict(familyId=f['id'],status='partial-family-study',image=f['id']+'.png',sha256=frame['sha256'],report=f['id']+'-report.json',reportSha256=hashlib.sha256((out/(f['id']+'-report.json')).read_bytes()).hexdigest(),quality=req['quality'],lod=req['lod']))
    atomic_json(out/'evidence.json',dict(status='family-studies-only',studies=evidence,gpuValidated=False))

if __name__=='__main__':collect(sys.argv[1])
