"""Assemble and verify the v1 review grids without modifying approved Vex geometry."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from universal.registry import ROOT,check_registry
from universal.cache import atomic_json,valid_png
from venus_vault.design import generate_design
from venus_vault.geometry import digest
FOLDER=ROOT/'docs/universal-library/approved'

def hash_file(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def collect(source):
    source=Path(source);FOLDER.mkdir(parents=True,exist_ok=True);models=[]
    for boss in ['boss-atheon','boss-templar']:
        old='front' if boss=='boss-atheon' else 'templar';env='throne' if boss=='boss-atheon' else 'templar'
        views=[dict(view='front',path=f'docs/previews/cinematic-vex-0.9.1/after/{old}.png',quality='cinematic'),dict(view='environment',path=f'docs/previews/cinematic-vex-0.9.1/after/{env}.png',quality='cinematic')]
        if boss=='boss-templar':views=[v for v in views if v['view']!='environment']
        for view in (['three-quarter','silhouette','environment'] if boss=='boss-templar' else ['three-quarter','silhouette']):
            src=source/(boss+'-'+view);r=json.loads((src/'progress.json').read_text());q=r['request'];frame=r['frames']['0'];png=src/frame['file'];name=boss+'-'+view
            if r['status']!='success' or q['binding']['selectionId']!=boss or q['view']!=view or q['quality']!='cinematic' or q['lod']!=0 or not valid_png(png,q['width'],q['height'],frame['sha256']):raise ValueError('Invalid Vex grid render')
            shutil.copyfile(png,FOLDER/(name+'.png'));shutil.copyfile(src/'progress.json',FOLDER/(name+'-report.json'))
            views.append(dict(view=view,path='docs/universal-library/approved/'+name+'.png',quality='cinematic',report=name+'-report.json',reportSha256=hash_file(FOLDER/(name+'-report.json'))))
        for v in views:v['sha256']=hash_file(ROOT/v['path'])
        if boss=='boss-atheon':video=dict(path='docs/previews/cinematic-vex-0.9.1/clips/walk.mp4',frames=48,fps=24,quality='balanced')
        else:
            src=source/'boss-templar-animation';r=json.loads((src/'progress.json').read_text());q=r['request']
            if r['status']!='success' or len(r['frames'])!=24 or q['animation']!='rotate' or q['quality']!='balanced' or q['lod']!=0:raise ValueError('Incomplete Templar animation')
            for f in r['frames'].values():
                if not valid_png(src/f['file'],q['width'],q['height'],f['sha256']):raise ValueError('Invalid Templar frame')
            shutil.copyfile(src/'sequence.mp4',FOLDER/'boss-templar-rotate.mp4');shutil.copyfile(src/'progress.json',FOLDER/'boss-templar-rotate-report.json')
            images=[]
            for i in [0,12,23]:
                n=f'boss-templar-rotate-{i:04d}.png';shutil.copyfile(src/f'frame-{i:04d}.png',FOLDER/n);images.append(dict(path=n,index=i,sha256=r['frames'][str(i)]['sha256']))
            video=dict(path='docs/universal-library/approved/boss-templar-rotate.mp4',frames=24,fps=24,quality='balanced',report='boss-templar-rotate-report.json',reportSha256=hash_file(FOLDER/'boss-templar-rotate-report.json'),representativeImages=images)
        video['sha256']=hash_file(ROOT/video['path']);models.append(dict(id=boss,modelStatus='implemented-user-approved',galleryStatus='technical-grid-rendered',views=views,animation=video))
    original=ROOT/'docs/previews/cinematic-vex-0.9.1/evidence.json'
    atomic_json(FOLDER/'evidence.json',dict(models=models,existingEvidence=dict(path=str(original.relative_to(ROOT)),sha256=hash_file(original)),notes=['Atheon and Templar models are unchanged.','Templar has a new dedicated wide environment framing.','New camera views are technical validation, not a new user approval.','CPU only; no T4/Colab/Android execution.']))

def verify():
    check_registry();e=json.loads((FOLDER/'evidence.json').read_text())
    if hash_file(ROOT/e['existingEvidence']['path'])!=e['existingEvidence']['sha256']:raise ValueError('Historical proof changed')
    if {m['id'] for m in e['models']}!={'boss-atheon','boss-templar'}:raise ValueError('Approved model list differs')
    for m in e['models']:
        if {v['view'] for v in m['views']}!={'front','three-quarter','silhouette','environment'}:raise ValueError('Grid incomplete')
        for v in m['views']:
            p=ROOT/v['path']
            if hash_file(p)!=v['sha256']:raise ValueError('Image hash differs')
            if 'report' not in v:continue # Frozen original media is verified by its own verifier.
            report=json.loads((FOLDER/v['report']).read_text());r=report['request'];f=report['frames']['0']
            if hash_file(FOLDER/v['report'])!=v['reportSha256'] or report['status']!='success' or r['quality']!='cinematic' or r['lod']!=0:raise ValueError('Invalid new still report')
            if not valid_png(p,r['width'],r['height'],f['sha256']):raise ValueError('Invalid decoded PNG')
            from venus_vault.request import select
            camera={'three-quarter':'orbit','silhouette':'front','environment':'wide'}[v['view']]
            old=select(m['id'],r['quality'],r['seed'],camera,r['animation'],r['frames'],r['fps'],r['width'],r['height'],r['startFrame'],r['lod']);env,boss,dust=generate_design(old)
            if report['configuration']['designSha256']!=digest(dict(environment=env,boss=boss,dust=dust)):raise ValueError('Approved geometry changed')
        v=m['animation'];p=ROOT/v['path']
        if hash_file(p)!=v['sha256']:raise ValueError('Video hash differs')
        info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name,pix_fmt,nb_frames,avg_frame_rate','-of','json',str(p)]))['streams'][0]
        if info['codec_name']!='h264' or info['pix_fmt']!='yuv420p' or int(info['nb_frames'])!=v['frames'] or info['avg_frame_rate']!='24/1':raise ValueError('Video validation failed')
        decoded=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:v:0','-f','framemd5','-']).decode()
        hashes=[line.rsplit(',',1)[1].strip() for line in decoded.splitlines() if line and not line.startswith('#')]
        if len(hashes)!=v['frames'] or len(set(hashes))<v['frames']*.8:raise ValueError('Animation decode is frozen or incomplete')
        if 'report' in v:
            report=json.loads((FOLDER/v['report']).read_text())
            if hash_file(FOLDER/v['report'])!=v['reportSha256'] or len({x['sha256'] for x in report['frames'].values()})!=24:raise ValueError('Animation reports differ')
            for image in v['representativeImages']:
                if not valid_png(FOLDER/image['path'],480,360,image['sha256']) or image['sha256']!=report['frames'][str(image['index'])]['sha256']:raise ValueError('Invalid animation sample')
    return dict(approvedModels=2,newCinematicStills=5,newBalancedTemplarFrames=24)

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]!='--check':collect(sys.argv[1])
    else:print(json.dumps(verify()))
