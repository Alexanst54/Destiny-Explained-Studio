"""Generate and optionally execute a review grid for all registered boss providers.
Missing identities/forms remain in the backlog; no generic models are substituted.
"""
import argparse,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from universal.registry import index
from universal.cache import atomic_json

def plan(include_prototypes=False):
    d=index();jobs=[];backlog=[]
    for e in d['entities']:
        if e['kind'] not in ['boss','form']:continue
        impl=e['implementation']
        if not impl or impl['status'].startswith('partial') and not include_prototypes:
            backlog.append(dict(id=e['id'],status=e['status'],composition=e['composition'],nature=e['nature'],parentBossId=e['parentBossId'],activityIds=e['activityIds']));continue
        animation=next((a for a in ['walk','attack','rotate','combat','signature','move','temporal'] if a in impl['animations']),'idle')
        if impl.get('reviewGrid'):animation=impl['reviewGrid']['animation']
        views=['front','profile','three-quarter','cinematic','environment','animation'] if 'profile' in impl.get('views',[]) else ['front','three-quarter','silhouette','environment','animation']
        for view in views:
            jobs.append(dict(id=e['id']+'/'+view,selection=e['id'],view='environment' if view=='animation' else view,animation=animation if view=='animation' else 'idle',quality='balanced' if view=='animation' else 'cinematic',lod=0,width=480 if view=='animation' else 640,height=360 if view=='animation' else 800,frames=24 if view=='animation' else 1,fps=24,video=view=='animation',modelStatus=impl['status']))
            if 'profile' in impl.get('views',[]):
                grid=impl['reviewGrid'];jobs[-1].update(width=480 if view=='animation' else grid['width'],height=360 if view=='animation' else grid['height'],frames=grid['frames'] if view=='animation' else 1,fps=grid['fps'])
    return dict(version=1,jobs=jobs,backlog=backlog,qualityGate='A successful render is technical evidence, not automatic artistic approval.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output');p.add_argument('--execute',action='store_true');p.add_argument('--include-prototypes',action='store_true');p.add_argument('--blender',default='blender');p.add_argument('--device',choices=['auto','cpu'],default='auto');p.add_argument('--timeout',type=int,default=1800);a=p.parse_args();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True);data=plan(a.include_prototypes);atomic_json(out/'batch-plan.json',data)
    if not a.execute:print(json.dumps(dict(jobs=len(data['jobs']),backlog=len(data['backlog']),executed=False)));return
    statuses={};report=out/'batch-progress.json'
    for job in data['jobs']:
        folder=out/job['id'];cmd=[sys.executable,str(Path(__file__).resolve().parents[1]/'render_universal.py'),job['selection'],str(folder),'--blender',a.blender,'--device',a.device,'--timeout',str(a.timeout)]
        for field in ['view','animation','quality','lod','width','height','frames','fps']:cmd += ['--'+field,str(job[field])]
        if job['video']:cmd.append('--video')
        if folder.exists():cmd.append('--resume')
        try:
            subprocess.run(cmd,check=True);statuses[job['id']]='rendered-awaiting-artistic-review'
        except subprocess.CalledProcessError:
            statuses[job['id']]='failed';atomic_json(report,dict(status='failed',jobs=statuses,backlog=data['backlog']));raise
        atomic_json(report,dict(status='running',jobs=statuses,backlog=data['backlog']))
    atomic_json(report,dict(status='technically-rendered-library-incomplete',jobs=statuses,backlog=data['backlog']))

if __name__=='__main__':main()
