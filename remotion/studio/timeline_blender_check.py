"""Check every directed source frame in Blender without rendering any images."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from complete_atheon import load_package
from cinematic_atheon import jobs_for
from cinematic_direction import install,apply,camera,shot_at
from universal.worker import build,update
from shot_audit import timeline,diagnostic
from perf_common import atomic_json,digest

def main():
 import bpy
 from mathutils import Vector
 package=load_package();rows=timeline(package);jobs=jobs_for(package,360,640);states={};output=[];last=None;last_scene=None;count=0
 for row in rows:
  boss='boss-templar' if row['cameraId']=='templar' else 'boss-atheon';j=next(j for j in jobs if j['request']['selectionId']==boss)
  if boss not in states:
   state=build(j['request'],'cpu',3,Path('/tmp'));install(state);states[boss]=state
  state=states[boss];scene=state['scene'];n=next(i['timing']['durationFrames'] for i in package['scenes'] if i['scene']['id']==row['sceneId']);offset=row['episodeFrameStart']-row['sceneFrameStart'];before=digest(state['boss']);meshes=len(bpy.data.meshes);first=None;previous=None
  for f in range(row['sceneFrameStart'],row['sceneFrameEndExclusive']):
   update(state,j['request'],f);apply(state,row['sceneId'],f,n);d=diagnostic(row['sceneId'],f,n,scene,offset)
   assert d['episodeRange']==[row['episodeFrameStart'],row['episodeFrameEndExclusive']]
   wanted=camera(shot_at(row['sceneId'],f,n));actual_forward=scene.camera.matrix_world.to_quaternion()@Vector((0,0,-1));expected_forward=(Vector(wanted['target'])-scene.camera.location).normalized();alignment=actual_forward.normalized().dot(expected_forward)
   assert alignment>.99999,'Wrong actual camera look direction';d['targetDirectionAlignment']=alignment
   if first is None:
    first=d
    if last is not None:assert digest(last['matrixWorld'])!=digest(d['matrixWorld']),'Repeated shot composition across a cut'
   previous=d;count+=1
  assert digest(state['boss'])==before and len(bpy.data.meshes)==meshes,'Geometry changed during frame updates'
  assert digest(first['matrixWorld'])!=digest(previous['matrixWorld']),'Static directed camera'
  output.append(dict(**row,firstActual=first,lastActual=previous,framesChecked=row['sceneFrameEndExclusive']-row['sceneFrameStart'],sceneTransition=last_scene!=row['sceneId']));last=previous;last_scene=row['sceneId'];print('Checked',row['shotId'],row['episodeFrameStart'],row['episodeFrameEndExclusive'],flush=True)
 assert count==2672
 path=Path(sys.argv[sys.argv.index('--')+1]);atomic_json(path,dict(status='passed',blenderVersion=bpy.app.version_string,checkedFrames=count,orientationChecked=True,shots=output,renderedFrames=0,fullEpisodeRendered=False,gpuValidated=False))
if __name__=='__main__':main()
