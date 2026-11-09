"""Run inside Blender; tests import and matrices without rendering."""
import json
import math
from pathlib import Path
import sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from contract import load
from import_scene import build_scene,basis,source_matrix
from mathutils import Vector
source=Path(sys.argv[sys.argv.index('--')+1]);data=load(source);old_names=set(bpy.data.scenes.keys());scene,objects,info=build_scene(data,'standard','cpu',100,2)
assert old_names<=set(bpy.data.scenes.keys()),'Existing scenes deleted'
assert len(objects)==len(data['meshes'])
assert len({o.data.as_pointer() for o in objects.values()})<=2
for mesh in data['meshes']:
    expected=basis()@source_matrix(mesh['matrixWorld']);actual=objects[mesh['id']].matrix_world
    assert max(abs(expected[i][j]-actual[i][j]) for i in range(4) for j in range(4))<1e-5
    assert objects[mesh['id']]['bridge_id']==mesh['id']
expected=basis()@Vector((*data['camera']['position'],1));assert (scene.camera.location-expected.xyz).length<1e-5
assert abs(math.degrees(scene.camera.data.angle_y)-data['camera']['verticalFov'])<1e-4
point=scene.camera.matrix_world.inverted()@(basis()@Vector((*data['camera']['target'],1)))
assert abs(point.x)<1e-4 and abs(point.y)<1e-4 and point.z<0
assert info['selected']=='CPU' and scene.cycles.samples==16
cinema,_,config=build_scene(data,'cinematic','cpu',25,2);assert cinema.cycles.samples==64 and cinema.cycles.use_denoising==config['denoise'];assert config['denoise'] or config['notes']
print('PASS Blender import: axes, all mesh matrices, camera/FOV, shared geometry, profiles, scene preservation; '+str(len(objects))+' objects.')

# Exercise a sheared affine mesh and the non-humanoid shared sphere geometry.
modified=json.loads(json.dumps(data));modified['meshes'][0]['matrixWorld'][4]+=.3;modified['meshes'][1]['geometry']='sphere'
other,objs,settings=build_scene(modified,'standard','cpu',25,2);other.view_layers[0].update()
unit=[Vector((x,y,z,1)) for z in [-.5,.5] for y in [-.5,.5] for x in [-.5,.5]]
spec=modified['meshes'][0];obj=objs[spec['id']];expected=basis()@source_matrix(spec['matrixWorld'])
for original,vertex in zip(unit,obj.data.vertices):assert ((obj.matrix_world@vertex.co).to_4d().xyz-(expected@original).xyz).length<1e-4
assert settings['bakedAffineCount']>=1 and any(len(o.data.vertices)>8 for o in objs.values())
print('PASS affine shear preservation and sphere geometry.')
