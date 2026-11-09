"""Copy the actual Crota review grid, retaining a partial artistic status."""
import hashlib,json,shutil,sys,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from universal.registry import ROOT
from universal.cache import atomic_json,valid_png
from universal.crota import generate,arena
from venus_vault.geometry import digest

def collect(source,native_log,regression=None):
    source=Path(source);out=ROOT/'docs/universal-library/crota';out.mkdir(parents=True,exist_ok=True);items=[]
    for view in ['front','three-quarter','silhouette','environment','attack']:
        folder=source/view;report=json.loads((folder/'progress.json').read_text());r=report['request'];clip=view=='attack';count=24 if clip else 1
        if report['status']!='success' or len(report['frames'])!=count or r['binding']['selectionId']!='boss-crota' or r['lod']!=0 or r['quality']!=('balanced' if clip else 'cinematic'):raise ValueError('Incomplete Crota proof')
        if report['configuration']['bossDesignSha256']!=digest(generate(r['seed'],r['quality'],r['lod'])) or report['configuration']['designSha256']!=digest(arena(r['seed'],r['quality'],r['lod'])):raise ValueError('Stale geometry')
        for i in range(count):
            frame=report['frames'][str(i)]
            if not valid_png(folder/frame['file'],r['width'],r['height'],frame['sha256']):raise ValueError('Invalid PNG')
        shutil.copyfile(folder/'progress.json',out/(view+'-report.json'))
        item=dict(view=view,status='partial-dedicated-prototype',report=view+'-report.json',reportSha256=hashlib.sha256((out/(view+'-report.json')).read_bytes()).hexdigest(),images=[])
        for i in ([0,12,23] if clip else [0]):
            name=(view+f'-{i:04d}' if clip else view)+'.png';shutil.copyfile(folder/f'frame-{i:04d}.png',out/name);item['images'].append(dict(path=name,index=i,sha256=report['frames'][str(i)]['sha256']))
        if clip:
            shutil.copyfile(folder/'sequence.mp4',out/'attack.mp4');item['video']=dict(path='attack.mp4',sha256=hashlib.sha256((out/'attack.mp4').read_bytes()).hexdigest())
        items.append(item)
    line=next(l for l in Path(native_log).read_text().splitlines() if l.startswith('CROTA_BLENDER_CHECK '));metrics=json.loads(line.removeprefix('CROTA_BLENDER_CHECK '))
    regression_proof=None
    if regression:
        regression=Path(regression);r=json.loads((regression/'progress.json').read_text());original=out/'front.png';repeat=regression/'frame-0000.png'
        if r['status']!='success' or not valid_png(repeat,640,800,r['frames']['0']['sha256']):raise ValueError('Invalid repeated Blender render')
        def rgb(path):return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-f','rawvideo','-pix_fmt','rgb24','-'])
        a,b=rgb(original),rgb(repeat)
        if a!=b:raise ValueError('Refactor changed RGB pixels')
        shutil.copyfile(repeat,out/'regression-front.png');shutil.copyfile(regression/'progress.json',out/'regression-front-report.json')
        regression_proof=dict(image='regression-front.png',sha256=r['frames']['0']['sha256'],report='regression-front-report.json',reportSha256=hashlib.sha256((out/'regression-front-report.json').read_bytes()).hexdigest(),rgbPixelIdentity=True,rgbSha256=hashlib.sha256(a).hexdigest(),differentChannelSamples=0,note='PNG metadata timestamps differ; decoded RGB is exactly identical.')
    atomic_json(out/'evidence.json',dict(status='partial-dedicated-prototype',userApproved=False,selectionId='boss-crota',environmentId='oversoul-throne',views=items,nativeBlender=metrics,providerRefactorRegression=regression_proof,notes=['Original dedicated geometry; no artistic completion claim.','Move is a floating staging motion, not foot-contact walking.','GPU/Colab/Android untested.']))

if __name__=='__main__':collect(sys.argv[1],sys.argv[2],sys.argv[3] if len(sys.argv)>3 else None)
