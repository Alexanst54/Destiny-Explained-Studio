"""Native Blender checks for all five animation families and exact physical view angles."""
import json,math,sys,tempfile
from pathlib import Path
sys.path[:]=[p for p in sys.path if Path(p).resolve()!=Path(__file__).resolve().parent]
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from universal.request import request
from universal.worker import build,update

DIMENSIONS={'oryx':(768,576),'rhulk':(640,800),'nezarec':(640,640)}
def main():
 results={}
 for name,(width,height) in DIMENSIONS.items():
  with tempfile.TemporaryDirectory() as tmp:
   r=request('boss-'+name,quality='draft',view='front',width=width,height=height);state=build(r,'cpu',3,Path(tmp));objects=len(bpy.data.objects);meshes=len(bpy.data.meshes);evaluations=0
   visible_eyes=None
   if name=='nezarec':
    update(state,r,0);visible_eyes=0;depsgraph=bpy.context.evaluated_depsgraph_get()
    for piece in state['providerModule'].generate()['objects']:
     if piece['material']!='nezarec-eye':continue
     target=state['joints']['head'].matrix_world@Vector(piece['position']);origin=target+Vector((0,-6,0))
     hit,location,normal,face,obj,matrix=state['scene'].ray_cast(depsgraph,origin,Vector((0,1,0)),distance=6.2)
     assert hit and obj.material_slots[obj.data.polygons[face].material_index].material.name=='nezarec-eye','Eye occluded by mask geometry'
     visible_eyes+=1
    assert visible_eyes==7
   for mode in ['idle','move','combat','signature','reveal']:
    r['animation']=mode;seen=set()
    for frame in range(48):
     update(state,r,frame);evaluations+=1
     for obj in state['joints'].values():assert all(math.isfinite(v) for row in obj.matrix_world for v in row)
     assert len(bpy.data.objects)==objects and len(bpy.data.meshes)==meshes
     seen.add(tuple(round(x,7) for key,obj in state['joints'].items() if key!='root' for row in obj.matrix_world for x in row))
    assert len(seen)>20,mode+' lacks articulated motion'
   r['animation']='idle';update(state,r,17);before={k:tuple(x for row in v.matrix_world for x in row) for k,v in state['joints'].items()};update(state,r,41);update(state,r,17);assert before=={k:tuple(x for row in v.matrix_world for x in row) for k,v in state['joints'].items()}
   worst=0;bounds={}
   for view in ['front','profile','three-quarter','cinematic','environment']:
    r['view']=view;update(state,r,0);coords=[]
    for obj in state['scene'].objects:
     if obj.type!='MESH' or obj.parent is None:continue
     if obj.parent.name in ['ritual','resonance','nightmare']:continue
     for corner in obj.bound_box:
      p=world_to_camera_view(state['scene'],state['scene'].camera,obj.matrix_world@Vector(corner));coords.append(p)
      overflow=max(0,-p.x,p.x-1,-p.y,p.y-1);worst=max(worst,overflow)
      assert p.z>0 and overflow<.025,(name,view,obj.name,tuple(p))
    bounds[view]=dict(minX=min(p.x for p in coords),maxX=max(p.x for p in coords),minY=min(p.y for p in coords),maxY=max(p.y for p in coords))
   state['scene'].render.resolution_x=480;state['scene'].render.resolution_y=360;r['view']='cinematic';r['animation']='signature' if name=='oryx' else 'combat';clip_worst=0
   for frame in range(36):
    update(state,r,frame)
    for obj in state['scene'].objects:
     if obj.type!='MESH' or obj.parent is None or obj.parent.name in ['ritual','resonance','nightmare']:continue
     for corner in obj.bound_box:
      p=world_to_camera_view(state['scene'],state['scene'].camera,obj.matrix_world@Vector(corner));overflow=max(0,-p.x,p.x-1,-p.y,p.y-1);clip_worst=max(clip_worst,overflow)
      assert p.z>0 and overflow<.01,(name,'clip',frame,obj.name,tuple(p))
   results[name]=dict(evaluations=evaluations,views=5,clipProjectionFrames=36,maxClipOverflow=clip_worst,maxNormalizedOverflow=worst,staticResources=True,randomAccess=True,articulatedMotion=True,bounds=bounds,physicalFootContactValidated=False)
   if visible_eyes is not None:results[name]['unoccludedEyeRays']=visible_eyes
  bpy.ops.wm.read_factory_settings(use_empty=True)
  lod_checks=[]
  for lod in [1,2]:
   with tempfile.TemporaryDirectory() as tmp:
    lower=request('boss-'+name,quality='draft',view='front',width=width,height=height,lod=lod);lower_state=build(lower,'cpu',3,Path(tmp));before_objects=len(bpy.data.objects);before_meshes=len(bpy.data.meshes)
    for mode in ['idle','move','combat','signature','reveal']:
     lower['animation']=mode;update(lower_state,lower,18)
     assert len(bpy.data.objects)==before_objects and len(bpy.data.meshes)==before_meshes
    lod_checks.append(dict(lod=lod,bossBoxes=lower_state['configuration']['bossBoxes'],joints=len(lower_state['joints']),animationModes=5))
   bpy.ops.wm.read_factory_settings(use_empty=True)
  results[name]['lowerLodConstructionChecks']=lod_checks
 print('LOT_C_CHECK '+json.dumps(results),flush=True)
if __name__=='__main__':main()
