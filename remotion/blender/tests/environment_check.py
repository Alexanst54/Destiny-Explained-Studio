"""Blender-only environment checks, without additional renders."""
import sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from contract import load
from environments.riis import generate
from import_scene import build_scene,basis,source_matrix
from mathutils import Vector
legacy=load(Path(__file__).resolve().parents[1]/'examples/riis-frame-210.json')
for quality,samples,bounces in [('draft',8,2),('balanced',32,3),('cinematic',96,5)]:
    d=generate(legacy,quality);scene,objects,config=build_scene(d,device='cpu',scale=25,threads=2)
    assert len(objects)==len(d['meshes']) and scene.cycles.samples==samples and scene.cycles.max_bounces==bounces
    assert config['environmentDetail']==quality
    assert ('RiisDepthHaze' in [o.name.split('.')[0] for o in scene.objects])==(quality=='cinematic')
    assert (scene.camera.location-(basis()@Vector((*legacy['camera']['position'],1))).xyz).length<1e-5
    for m in d['meshes']:
        obj=objects[m['id']];wanted=basis()@source_matrix(m['matrixWorld'])
        # Compare actual world-space vertices, including preserved affine residuals.
        if m['geometry']=='box':
            unit=[Vector((x,y,z,1)) for z in [-.5,.5] for y in [-.5,.5] for x in [-.5,.5]]
            assert max(((obj.matrix_world@v.co)-(wanted@p).xyz).length for v,p in zip(obj.data.vertices,unit))<3e-5
    print('PASS environment',quality,len(objects),'meshes',samples,'samples',config['viewTransform'])
