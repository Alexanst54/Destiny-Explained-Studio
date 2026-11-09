"""Real Blender integration: transforms, projection, animation, no scene rebuild between frames."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from venus_vault.request import select
from venus_vault.renderer import build_scene, update_frame
from characters.vex_bosses import pose

checked=0
for boss,animation in [('boss-atheon','walk'),('boss-atheon','temporal'),('boss-templar','attack')]:
    state=build_scene(select(boss,quality='draft',camera='reveal',animation=animation),'cpu',2)
    scene=state['scene'];ids={o.as_pointer() for o in scene.objects};meshes=len(bpy.data.meshes)
    rest=state['joints']['head'].matrix_world.copy()
    for frame in [0,15,30,45,12,0]:
        update_frame(state,frame)
        assert ids=={o.as_pointer() for o in scene.objects},'Scene reconstructed between frames'
        assert meshes==len(bpy.data.meshes),'Mesh resources leaked'
        eye=state['joints']['head'].matrix_world.translation
        p=world_to_camera_view(scene,scene.camera,eye)
        assert 0<p.x<1 and 0<p.y<1 and p.z>0,(boss,frame,tuple(p))
        for joint in state['joints'].values():assert all(abs(v)<1e4 for row in joint.matrix_world for v in row)
        if frame==30:assert state['joints']['head'].matrix_world!=rest,'Boss stayed static'
        checked+=1
    assert max(abs(state['joints']['head'].matrix_world[i][j]-rest[i][j]) for i in range(4) for j in range(4))<1e-5,'Random-access pose drift'
print('VENUS_VAULT_CHECK',checked,'poses; static resources, projections and random-access transforms passed')
