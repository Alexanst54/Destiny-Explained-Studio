"""Optional linked-box compiler for repeated props; default boss/arena renderer uses batching.
All instances share one unit mesh; per-object material slots reuse the existing materials.
"""


def compile_linked_boxes(spec,materials,collection,joints=None):
    import bpy
    from import_scene import mesh_data
    unit=mesh_data('box');unit.name='CinematicLinkedVoxel';unit.materials.append(next(iter(materials.values())))
    result=[]
    for box in spec['objects']:
        obj=bpy.data.objects.new('Linked/'+box['id'],unit);collection.objects.link(obj)
        if box['joint']:
            if joints is None or box['joint'] not in joints:raise ValueError('Missing instance parent joint')
            obj.parent=joints[box['joint']]
        obj.location=box['position'];obj.rotation_euler=box['rotation'];obj.scale=box['size']
        obj.material_slots[0].link='OBJECT';obj.material_slots[0].material=materials[box['material']]
        result.append(obj)
    return result
