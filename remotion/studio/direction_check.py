"""Native Blender check: directed cameras/poses are deterministic and geometry stable."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from complete_atheon import load_package
from cinematic_atheon import jobs_for
from cinematic_direction import install,apply,SHOTS,shot_at
from universal.worker import build,update
from venus_vault.request import select
from perf_common import atomic_json,digest

def main():
 import bpy
 jobs=jobs_for(load_package(),360,640,representatives=True);results=[]
 for boss in ['boss-atheon','boss-templar']:
  j=next(j for j in jobs if j['request']['selectionId']==boss);state=build(j['request'],'cpu',3,Path('/tmp'));install(state);scene=state['scene']
  counts=(len(bpy.data.meshes),sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH'));design_before=digest(state['boss'])
  def capture(sid,f,n):
   update(state,j['request'],f);apply(state,sid,f,n)
   return dict(camera=[list(row) for row in scene.camera.matrix_world],joints={k:[list(row) for row in v.matrix_world] for k,v in state['joints'].items()},hidden=state['directionBossCollection'].hide_render)
  poses=[]
  for sid,cuts in SHOTS.items():
   if boss=='boss-templar' and sid!='03-vault':continue
   n=next(item['timing']['durationFrames'] for item in load_package()['scenes'] if item['scene']['id']==sid)
   for a,b,name,animation in cuts:
    if (name=='templar')!=(boss=='boss-templar'):continue
    first=int(a*n)+1;last=min(n-1,int(b*n)-1);mid=(first+last)//2
    initial=capture(sid,mid,n);capture(sid,last,n);again=capture(sid,mid,n)
    assert digest(initial)==digest(again),(sid,name,'non-deterministic reverse evaluation')
    assert counts==(len(bpy.data.meshes),sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH')),'Geometry rebuilt during frame update'
    assert digest(state['boss'])==design_before,'Approved design mutated'
    poses.append(digest(capture(sid,first,n)));poses.append(digest(capture(sid,last,n)))
    results.append(dict(boss=boss,scene=sid,shot=name,deterministic=True,stableGeometry=True))
  assert len(set(poses))>1,'No camera/pose movement'
 out=Path(sys.argv[sys.argv.index('--')+1]);atomic_json(out,dict(status='passed',blenderVersion=bpy.app.version_string,checks=results,renderedFrames=0,gpuValidated=False))
 print('DIRECTION_CHECK passed',len(results),'shots')
if __name__=='__main__':main()
