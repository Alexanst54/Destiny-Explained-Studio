"""Native articulation/resource/projection checks for the partial Crota model."""
import sys,json,math,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from universal.request import request
from universal.worker import build,update

def main():
    evaluated=0;worst=0
    with tempfile.TemporaryDirectory() as tmp:
        r=request('boss-crota',quality='draft',width=640,height=800,view='front');state=build(r,'cpu',3,Path(tmp));objects=len(bpy.data.objects);meshes=len(bpy.data.meshes)
        for mode in ['idle','move','attack','reveal']:
            for frame in range(48):
                r['animation']=mode;update(state,r,frame);evaluated+=1
                for obj in state['joints'].values():assert all(math.isfinite(v) for row in obj.matrix_world for v in row)
                assert len(bpy.data.objects)==objects and len(bpy.data.meshes)==meshes
        r['animation']='idle';update(state,r,12);before={k:tuple(v.matrix_world.translation) for k,v in state['joints'].items()};update(state,r,43);update(state,r,12);assert before=={k:tuple(v.matrix_world.translation) for k,v in state['joints'].items()}
        for view in ['front','three-quarter','silhouette']:
            r['view']=view;update(state,r,0)
            for obj in state['scene'].objects:
                if obj.type!='MESH' or not obj.parent:continue
                for corner in obj.bound_box:
                    p=world_to_camera_view(state['scene'],state['scene'].camera,obj.matrix_world@Vector(corner));overflow=max(0,-p.x,p.x-1,-p.y,p.y-1);worst=max(worst,overflow)
                    assert p.z>0 and overflow<.02,(view,obj.name,tuple(p))
        result=dict(status='passed',evaluations=evaluated,cameraViews=3,maxNormalizedBoundsOverflow=worst,staticResources=True,randomAccess=True,physicalGroundContactValidated=False)
        print('CROTA_BLENDER_CHECK '+json.dumps(result),flush=True)

if __name__=='__main__':main()
