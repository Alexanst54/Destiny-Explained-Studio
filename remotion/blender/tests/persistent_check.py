"""Blender integration: all 90 poses against independent world-space unit vertices."""
import copy
import json
from pathlib import Path
import sys
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from contract import load
from environments.riis import generate
from import_scene import build_scene, basis, source_matrix
from persistent_scene import SceneUpdater
folder=Path(sys.argv[sys.argv.index('--')+1])
frames=[load(p) for p in sorted(folder.glob('[0-9][0-9][0-9][0-9][0-9].json'))]
scene,objects,info=build_scene(frames[0],device='cpu',scale=10,threads=2)
updater=SceneUpdater(scene,objects,frames[0])
static={m['id']:objects[m['id']].data.as_pointer() for m in frames[0]['meshes'] if m['id'].startswith('riis/')}
counts=[];maximum=0
for data in frames+list(reversed(frames)):
    updater.update(data)
    for m in data['meshes']:
        obj=objects[m['id']];expected=basis()@source_matrix(m['matrixWorld'])
        for original,vertex in zip(updater.vertices[m['geometry']],obj.data.vertices):
            error=((obj.matrix_world@vertex.co)-(expected@original.to_4d()).xyz).length
            maximum=max(maximum,error)
            assert error<5e-5,(m['id'],data['source']['frame'],error)
    wanted=basis()@source_matrix(data['camera']['matrixWorld'])
    assert max(abs(scene.camera.matrix_world[i][j]-wanted[i][j]) for i in range(4) for j in range(4))<1e-5
    assert static=={name:objects[name].data.as_pointer() for name in static}
    counts.append(len(bpy.data.meshes))
assert len(set(counts[1:]))==1,'Mesh data leaked during animation'
bad=copy.deepcopy(frames[0]);bad['lights'][0]['intensity']+=.1
try:updater.update(bad)
except ValueError:pass
else:raise AssertionError('Static change accepted')
# Toggle a mesh from ordinary LRS to shear and back; a copied mesh must reset.
base=copy.deepcopy(frames[0]);m=next(m for m in base['meshes'] if m['id'].startswith('riis/'))
m['matrixWorld'][4]+=.3
updater.update(base);updater.update(frames[0])
print(json.dumps({'status':'pass','sourceFrames':len(frames),'passes':'forward+reverse','maxWorldVertexError':maximum,'meshCountsStable':True,'staticGeometryReused':True}))
