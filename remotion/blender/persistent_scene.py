"""Scene reuse with exact affine updates, including changing rig shear."""
import math
from contract import validate
from import_scene import basis, source_matrix


def static_signature(data):
    # Only transforms, camera and actor/source metadata may change in a session.
    return {k: v for k, v in data.items() if k not in ('source', 'camera', 'actors', 'meshes')} | {
        'meshes': [{k: v for k, v in m.items() if k != 'matrixWorld'} for m in data['meshes']],
        'project': data['source']['projectSha256'],
        'resolution': data['resolution'],
    }


class SceneUpdater:
    def __init__(self, scene, objects, initial):
        self.scene = scene
        self.objects = objects
        self.signature = static_signature(initial)
        # Save original unit vertices once. Never transform last frame's baked vertices.
        self.vertices = {}
        self.private = set()
        self.previous = {m['id']: m['matrixWorld'] for m in initial['meshes']}
        from import_scene import mesh_data
        import bpy
        for kind in {m['geometry'] for m in initial['meshes']}:
            unit = mesh_data(kind)
            self.vertices[kind] = [v.co.copy() for v in unit.vertices]
            bpy.data.meshes.remove(unit)
        for spec in initial['meshes']:
            obj = objects[spec['id']]
            if obj.data.users == 1:
                self.private.add(spec['id'])
        scene.render.use_persistent_data = True

    def update(self, data):
        validate(data)
        if static_signature(data) != self.signature:
            raise ValueError('Static scene changed; use the single-frame renderer')
        conversion = basis()
        for spec in data['meshes']:
            name = spec['id']
            if self.previous[name] == spec['matrixWorld']:
                continue
            obj = self.objects[name]
            wanted = conversion @ source_matrix(spec['matrixWorld'])
            obj.matrix_world = wanted
            actual = obj.matrix_basis.copy()
            shear = max(abs(actual[i][j]-wanted[i][j]) for i in range(4) for j in range(4)) > 1e-6
            if shear or name in self.private:
                if name not in self.private:
                    obj.data = obj.data.copy()
                    self.private.add(name)
                transform = actual.inverted() @ wanted
                for vertex, original in zip(obj.data.vertices, self.vertices[spec['geometry']]):
                    vertex.co = transform @ original
                obj.data.update()
                obj.matrix_world = actual
            self.previous[name] = spec['matrixWorld']
        camera = self.scene.camera
        camera.matrix_world = conversion @ source_matrix(data['camera']['matrixWorld'])
        camera.data.lens = 24/(2*math.tan(math.radians(data['camera']['verticalFov'])/2))
        camera.data.clip_start = data['camera']['near']
        camera.data.clip_end = data['camera']['far']
        self.scene.frame_set(data['source']['frame'])
        self.scene.view_layers[0].update()
