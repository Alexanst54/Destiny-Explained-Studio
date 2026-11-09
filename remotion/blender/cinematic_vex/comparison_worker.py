"""Blender worker for reproducible real before/after stills, with recorded camera matrices.
Run with a frozen baseline checkout as --source for 'before'; no proprietary data involved.
"""
import argparse,hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--shot',required=True);p.add_argument('--output',required=True);p.add_argument('--phase',choices=['before','after'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(Path(a.source).resolve()/'remotion/blender'))
from provenance import render_signature
import bpy
from mathutils import Vector
from venus_vault.request import select
from venus_vault.renderer import build_scene,update_frame
spec=json.loads(Path(a.shot).read_text());out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
if (out/'frame-0000.png').exists():raise ValueError('Output already contains a rendered frame')
# Only supported legacy request fields enter the old, unmodified contract.
kwargs=dict(quality='cinematic',camera='wide' if a.phase=='before' else spec['camera'],seed=42,width=spec['width'],height=spec['height'])
if a.phase=='after':kwargs['lod']=0
request=select(spec['selection'],**kwargs);started=time.monotonic();state=build_scene(request,'auto',3);update_frame(state,0);scene=state['scene']
cam=scene.camera;c=spec['sharedCamera'];cam.location=c['position'];cam.rotation_euler=(Vector(c['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=c['lens'];cam.data.sensor_fit=c['sensorFit'];cam.data.sensor_height=c['sensorHeight'];cam.data.clip_start=c['near'];cam.data.clip_end=c['far']
# Shared look-development lighting for anatomy; complete original/new sets for arena shots.
studio=spec['id'] in ['front','profile','low-angle','head-torso']
if studio:
    from import_scene import mesh_data,linear_color
    for collection in scene.collection.children:
        if collection.name.startswith('Environment/'):collection.hide_render=True
    for obj in scene.objects:
        if obj.type=='LIGHT':obj.hide_render=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=linear_color('#142432')
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.18
    scene.view_settings.exposure=.2;scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.025;scene.cycles.adaptive_min_samples=8
    floor_mat=bpy.data.materials.new('SharedStudioGround');floor_mat.use_nodes=True
    bsdf=floor_mat.node_tree.nodes['Principled BSDF'];bsdf.inputs['Base Color'].default_value=linear_color('#23333e');bsdf.inputs['Roughness'].default_value=.7
    floor=bpy.data.objects.new('SharedStudioGround',mesh_data('box'));scene.collection.objects.link(floor);floor.data.materials.append(floor_mat);floor.location=(0,9,1);floor.scale=(1000,1000,.5)
    for name,pos,target,colour,power,size in [
        ('key',(-20,-15,30),(0,9,11),'#e1e6e8',18000,11),
        ('fill',(18,-5,20),(0,9,10),'#8bbacb',6500,11),
        ('rim',(-5,25,32),(0,9,11),'#b9dcff',26000,8),
        ('face',(-7,-9,19),(0,9,13),'#c3e8ff',2400,6)]:
        data=bpy.data.lights.new('SharedStudio/'+name,'AREA');data.energy=power;data.color=linear_color(colour)[:3];data.size=size
        obj=bpy.data.objects.new(data.name,data);scene.collection.objects.link(obj);obj.location=pos;obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
scene.view_layers[0].update();scene.render.filepath=str((out/'frame-0000.png').resolve());build=time.monotonic()-started
report={'status':'running','sourceInputHashes':render_signature(a.source),'phase':a.phase,'presentation':'shared-studio' if studio else 'complete-arena','adaptiveThreshold':scene.cycles.adaptive_threshold,'shot':spec,'request':request,'blenderVersion':bpy.app.version_string,'configuration':state['configuration'],'buildSeconds':round(build,3),'cameraMatrixWorld':[list(row) for row in cam.matrix_world]}
try:
    render_started=time.monotonic()
    try:bpy.ops.render.render(write_still=True,scene=scene.name)
    except RuntimeError as error:
        if state['configuration']['selected']!='GPU':raise
        scene.cycles.device='CPU';state['configuration'].update(selected='CPU',backend=None);state['configuration']['notes'].append('GPU failed; CPU retry: '+str(error));bpy.ops.render.render(write_still=True,scene=scene.name)
    payload=(out/'frame-0000.png').read_bytes()
    report.update(status='success',renderSeconds=round(time.monotonic()-render_started,3),pngBytes=len(payload),pngSha256=hashlib.sha256(payload).hexdigest())
except Exception as error:report.update(status='failed',error=str(error));raise
finally:
    report.update(secondsInsideBlender=round(time.monotonic()-started,3),peakProcessRssKiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    (out/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
print('COMPARISON_RESULT '+json.dumps(report),flush=True)
