"""Native Blender proof: IK sole contacts, no stance sliding, cinematic silhouette bounds, LOD."""
from pathlib import Path
import sys,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from venus_vault.request import select
from venus_vault.renderer import build_scene,update_frame
from characters.vex_bosses import pose

state=build_scene(select('boss-atheon',quality='draft',camera='front',animation='walk',fps=24,width=640,height=640,lod=0),'cpu',3)
scene=state['scene'];objects={o.as_pointer() for o in scene.objects};mesh_count=len(bpy.data.meshes)
worst=0;sliding=0;penetration=0;terrain_error=0;terrain_cache={};previous={};evaluated=0
for frame in range(96):
    update_frame(state,frame);p=pose('boss-atheon','walk',frame,24)
    for n,contact in p['contacts'].items():
        foot=state['joints']['foot'+n];ankle=foot.matrix_world.translation
        error=(ankle-Vector(contact['ankle'])).length;worst=max(worst,error);assert error<1e-4,(frame,n,'IK endpoint',error)
        sole=foot.matrix_world@Vector((0,0,-.2));assert abs(sole.z-contact['soleZ'])<1e-4
        if contact['stance']:
            assert abs(sole.z-1.25)<1e-4,(frame,n,'sole lifted',sole.z)
            key=tuple(round(v,6) for v in contact['ankle'][:2])
            if key not in terrain_cache:
                hits=[]
                for collection in scene.collection.children:
                    if not collection.name.startswith('Environment/'):continue
                    for ob in collection.objects:
                        if ob.type!='MESH' or ob.name.startswith('particles/') or ob.name.startswith('Bounded atmosphere'):continue
                        inv=ob.matrix_world.inverted();origin=inv@Vector((key[0],key[1],2));direction=inv.to_3x3()@Vector((0,0,-1))
                        hit,where,normal,index=ob.ray_cast(origin,direction,distance=10)
                        if hit:hits.append((ob.matrix_world@where).z)
                assert hits,'No actual terrain under planted foot'
                terrain_cache[key]=max(hits)
            error_height=abs(terrain_cache[key]-sole.z);terrain_error=max(terrain_error,error_height)
            # Thin decorative plates sit 3 cm above the nominal walking plane.
            assert error_height<=.04,('Contact outside authored 4 cm floor-layer tolerance',frame,n,error_height)
            prev=previous.get(n)
            if prev and prev[0] and (Vector(contact['ankle'])-prev[1]).length<1e-6:sliding=max(sliding,(ankle-prev[2]).length)
        previous[n]=(contact['stance'],Vector(contact['ankle']),ankle.copy())
        for obj in scene.objects:
            if obj.type=='MESH' and obj.parent==foot:
                bottom=min((obj.matrix_world@v.co).z for v in obj.data.vertices);penetration=max(penetration,1.25-bottom)
                assert bottom>=1.25-.015,(frame,n,obj.name,'ground penetration',bottom)
    assert objects=={o.as_pointer() for o in scene.objects} and mesh_count==len(bpy.data.meshes)
    evaluated+=1
assert sliding<1e-4
# Wide/reveal/orbit/front/profile must frame the actual geometry, not only its eye.
for preset in ['wide','reveal','orbit','front','profile','low-angle']:
    state['request']['camera']=preset
    for frame in [0,18,42,72]:
        update_frame(state,frame)
        for obj in scene.objects:
            if obj.type=='MESH' and obj.parent in state['joints'].values():
                for corner in obj.bound_box:
                    v=world_to_camera_view(scene,scene.camera,obj.matrix_world@Vector(corner))
                    assert 0<v.x<1 and 0<v.y<1 and v.z>0,('clipped',preset,frame,obj.name,tuple(v))
        evaluated+=1
# Random access must restore every joint exactly, including quaternion-driven feet and FX scales.
update_frame(state,13);snapshot={k:o.matrix_world.copy() for k,o in state['joints'].items()}
update_frame(state,71);update_frame(state,13)
assert max(abs(o.matrix_world[i][j]-snapshot[k][i][j]) for k,o in state['joints'].items() for i in range(4) for j in range(4))<1e-5
for boss,animation in [('boss-atheon','temporal'),('boss-atheon','reveal'),('boss-templar','attack'),('boss-templar','move')]:
    s=build_scene(select(boss,animation=animation,quality='draft',camera='front'),'cpu',2)
    if animation=='temporal':s['request']['camera']='temporal'
    for f in [0,18,36,60]:
        update_frame(s,f)
        assert all(math.isfinite(x) for o in s['joints'].values() for row in o.matrix_world for x in row)
        if animation=='temporal':
            for obj in s['scene'].objects:
                if obj.type=='MESH' and obj.parent in s['joints'].values():
                    for corner in obj.bound_box:
                        v=world_to_camera_view(s['scene'],s['scene'].camera,obj.matrix_world@Vector(corner))
                        assert 0<v.x<1 and 0<v.y<1 and v.z>0,('Temporal composition clipped',f,obj.name,tuple(v))
        evaluated+=1
# Linked instances are an opt-in extension API; the normal scene keeps merged mesh batches.
from cinematic_vex.instancing import compile_linked_boxes
from venus_vault.geometry import Design
sample=Design('linked-test');sample.box('a',(0,0,0),(1,2,3),'alloy');sample.box('b',(4,0,0),(2,1,3),'mechanism')
collection=bpy.data.collections.new('LinkedCompilerTest');scene.collection.children.link(collection)
linked=compile_linked_boxes(sample.result(),state['materials'],collection)
assert linked[0].data.as_pointer()==linked[1].data.as_pointer()
assert linked[0].material_slots[0].material!=linked[1].material_slots[0].material
assert tuple(linked[1].location)==(4,0,0)
print('CINEMATIC_CHECK',{'evaluations':evaluated,'maxAnkleErrorMetres':worst,'maxStanceSlidingMetres':sliding,'maxNominalPlanePenetrationMetres':max(0,penetration),'maxTerrainLayerContactErrorMetres':terrain_error,'staticResources':True,'linkedGeometryReuse':True})
