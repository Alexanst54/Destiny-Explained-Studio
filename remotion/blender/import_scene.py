"""Blender 3.6+/4.x headless bridge. No video, armature baking or external assets."""
import argparse
import json
import math
import os
from pathlib import Path
import resource
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from contract import load,validate

ENV_PROFILES={'draft':{'samples':8,'bounces':2,'denoise':False},'balanced':{'samples':32,'bounces':3,'denoise':True},'cinematic':{'samples':96,'bounces':5,'denoise':True}}
PROFILES={'standard':{'samples':16,'bounces':2,'denoise':False},'cinematic':{'samples':64,'bounces':4,'denoise':True}}

def source_matrix(values):
    from mathutils import Matrix
    return Matrix([values[i:i+4] for i in range(0,16,4)]).transposed()

def basis():
    from mathutils import Matrix
    return Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))

def linear_color(value):
    rgb=[int(value[i:i+2],16)/255 for i in [1,3,5]]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)

def mesh_data(kind):
    import bpy
    mesh=bpy.data.meshes.new('BridgeUnit-'+kind)
    if kind=='box':
        vertices=[(x,y,z) for z in [-.5,.5] for y in [-.5,.5] for x in [-.5,.5]]
        faces=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(1,3,7,5),(3,2,6,7),(2,0,4,6)]
    else:
        vertices=[(0,.5,0)]
        for ring in range(1,8):
            phi=math.pi*ring/8
            for segment in range(10):
                theta=math.tau*segment/10;vertices.append((-.5*math.cos(theta)*math.sin(phi),.5*math.cos(phi),.5*math.sin(theta)*math.sin(phi)))
        bottom=len(vertices);vertices.append((0,-.5,0));faces=[]
        for segment in range(10):
            nxt=(segment+1)%10;faces.append((0,1+segment,1+nxt));faces.append((bottom,61+nxt,61+segment))
        for ring in range(6):
            for segment in range(10):
                a=1+ring*10+segment;b=1+ring*10+(segment+1)%10;faces.append((a,a+10,b+10,b))
    mesh.from_pydata(vertices,[],faces);mesh.update()
    if kind=='sphere':
        for p in mesh.polygons:p.use_smooth=True
    return mesh

def choose_device(scene,requested):
    import bpy
    scene.cycles.device='CPU';info={'requested':requested,'selected':'CPU','backend':None,'devices':[],'notes':[]}
    if requested=='cpu':return info
    prefs=bpy.context.preferences.addons['cycles'].preferences
    for backend in ['CUDA','OPTIX','HIP','ONEAPI','METAL']:
        try:
            prefs.compute_device_type=backend;prefs.get_devices()
            gpus=[d for d in prefs.devices if d.type==backend]
            if not gpus:continue
            for d in prefs.devices:d.use=d.type==backend
            scene.cycles.device='GPU';info.update(selected='GPU',backend=backend,devices=[d.name for d in gpus]);return info
        except (TypeError,RuntimeError):continue
    info['notes'].append('No compatible Cycles GPU found; CPU fallback selected.')
    return info

def build_scene(data,profile=None,device='auto',scale=100,threads=None):
    import bpy
    from mathutils import Vector
    validate(data)
    environment=data.get('environment')
    settings=ENV_PROFILES[environment['detail']] if environment and profile is None else PROFILES.get(profile or data['profile'])
    if profile is None:profile=data['profile']
    if profile not in PROFILES or device not in ['auto','cpu'] or type(scale) is not int or not 10<=scale<=100:raise ValueError('Invalid render options')
    if not bpy.app.build_options.cycles:raise RuntimeError('This Blender build has no Cycles support; install a Cycles-enabled Blender build.')
    scene=bpy.data.scenes.new('DestinyBridge');scene.render.engine='CYCLES'
    import _cycles
    denoise_supported=bool(getattr(_cycles,'with_openimagedenoise',False))
    denoise=settings['denoise'] and denoise_supported
    scene.cycles.samples=settings['samples'];scene.cycles.max_bounces=settings['bounces'];scene.cycles.use_denoising=denoise;scene.cycles.seed=int(data['source']['projectSha256'][:8],16)%2147483647;scene.cycles.use_animated_seed=False
    scene.render.resolution_x=data['resolution']['width'];scene.render.resolution_y=data['resolution']['height'];scene.render.resolution_percentage=scale;scene.render.pixel_aspect_x=1;scene.render.pixel_aspect_y=1
    scene.render.fps=data['source']['fps'];scene.frame_set(data['source']['frame']);scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=False
    scene.view_settings.view_transform='Standard';scene.view_settings.exposure=0;scene.view_settings.gamma=1
    view_fallback=False
    if environment:
        try:scene.view_settings.view_transform='AgX'
        except TypeError:view_fallback=True  # Standard remains available on older Blender builds.
        scene.cycles.sample_clamp_indirect=3
    available=len(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else os.cpu_count() or 1
    count=min(available,4) if threads is None else threads
    if type(count) is not int or not 1<=count<=64:raise ValueError('Threads must be 1–64')
    scene.render.threads_mode='FIXED';scene.render.threads=count
    world=bpy.data.worlds.new('BridgeWorld');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=linear_color(data['world']['color']);world.node_tree.nodes['Background'].inputs['Strength'].default_value=data['world']['ambient']*.25;scene.world=world
    materials={}
    for spec in data['materials']:
        mat=bpy.data.materials.new(spec['id']);mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();output=nodes.new('ShaderNodeOutputMaterial')
        shader=nodes.new('ShaderNodeEmission' if spec['emission'] else 'ShaderNodeBsdfPrincipled');shader.inputs['Color' if spec['emission'] else 'Base Color'].default_value=linear_color(spec['color'])
        if spec['emission']:shader.inputs['Strength'].default_value=3 if environment and spec['id'].startswith('riis/') else 1
        else:shader.inputs['Roughness'].default_value=spec['roughness']
        mat.node_tree.links.new(shader.outputs[0],output.inputs['Surface']);materials[spec['id']]=mat
    geometries={};objects={};conversion=basis();baked=0
    for spec in data['meshes']:
        kind=spec['geometry']
        if kind not in geometries:
            geometries[kind]=mesh_data(kind);geometries[kind].materials.append(next(iter(materials.values())))
        obj=bpy.data.objects.new(spec['id'],geometries[kind]);scene.collection.objects.link(obj);obj.rotation_mode='QUATERNION';wanted=conversion@source_matrix(spec['matrixWorld']);obj.matrix_world=wanted
        # Blender object LRS cannot store shear: retain it in vertices when needed.
        actual=obj.matrix_basis.copy()
        if max(abs(actual[i][j]-wanted[i][j]) for i in range(4) for j in range(4))>1e-6:
            obj.data=geometries[kind].copy();obj.data.transform(actual.inverted()@wanted);obj.matrix_world=actual;baked+=1
        obj.material_slots[0].link='OBJECT';obj.material_slots[0].material=materials[spec['material']]
        obj['bridge_id']=spec['id'];obj['source_actor_id']=spec.get('actorId','');objects[spec['id']]=obj
    if environment and environment['hazeDensity']>0:
        fog=bpy.data.materials.new('RiisDepthHaze');fog.use_nodes=True;n= fog.node_tree.nodes;n.clear()
        out=n.new('ShaderNodeOutputMaterial');volume=n.new('ShaderNodeVolumePrincipled');volume.inputs['Density'].default_value=environment['hazeDensity'];volume.inputs['Color'].default_value=linear_color('#a8bed0');volume.inputs['Anisotropy'].default_value=.15;fog.node_tree.links.new(volume.outputs['Volume'],out.inputs['Volume'])
        haze=bpy.data.objects.new('RiisDepthHaze',mesh_data('box'));scene.collection.objects.link(haze);haze.data.materials.append(fog)
        haze.location=(0,55,15);haze.scale=(110,85,40)  # (x,-z,y), bounded behind the actor plaza.
    camera_data=bpy.data.cameras.new('BridgeCamera');camera=bpy.data.objects.new('BridgeCamera',camera_data);scene.collection.objects.link(camera);camera.matrix_world=conversion@source_matrix(data['camera']['matrixWorld']);camera_data.sensor_fit='VERTICAL';camera_data.sensor_height=24;camera_data.lens=24/(2*math.tan(math.radians(data['camera']['verticalFov'])/2));camera_data.clip_start=data['camera']['near'];camera_data.clip_end=data['camera']['far'];scene.camera=camera
    for spec in data['lights']:
        light_data=bpy.data.lights.new(spec['id'],'SUN');light_data.energy=spec['intensity'];light_data.color=linear_color(spec['color'])[:3];light_data.angle=math.radians(2 if profile=='standard' else 5);light=bpy.data.objects.new(spec['id'],light_data);scene.collection.objects.link(light)
        origin=conversion@Vector((*spec['position'],1));target=conversion@Vector((*spec['target'],1));light.location=origin.xyz;direction=(target-origin).xyz
        if direction.length<1e-9:raise ValueError('Light direction cannot be zero')
        light.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    scene['bridge_source']=json.dumps(data['source']);scene['bridge_omissions']=json.dumps(data['omissions']);scene['bridge_profile']=profile
    info=choose_device(scene,device)
    if view_fallback:info['notes'].append('AgX unavailable; Standard view transform retained.')
    if settings['denoise'] and not denoise_supported:info['notes'].append('OpenImageDenoise unavailable or not advertised by this build; denoising disabled.')
    info.update(environmentDetail=environment['detail'] if environment else None,viewTransform=scene.view_settings.view_transform,hazeDensity=environment['hazeDensity'] if environment else 0,bakedAffineCount=baked,profile=profile,samples=settings['samples'],bounces=settings['bounces'],denoise=denoise,denoiseRequested=settings['denoise'],cpuAvailable=available,threads=count,scalePercent=scale)
    return scene,objects,info

def main(argv=None):
    import bpy
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('input');parser.add_argument('output');parser.add_argument('--profile',choices=list(PROFILES));parser.add_argument('--device',choices=['auto','cpu'],default='auto');parser.add_argument('--scale',type=int,default=100);parser.add_argument('--threads',type=int);parser.add_argument('--check-only',action='store_true');args=parser.parse_args(argv)
    output=Path(args.output).resolve()
    if output.suffix.lower()!='.png':raise ValueError('Only a PNG output is allowed; no video rendering')
    data=load(args.input);started=time.monotonic();scene,objects,info=build_scene(data,args.profile,args.device,args.scale,args.threads);output.parent.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(output)
    if not args.check_only:
        if bpy.context.window:bpy.context.window.scene=scene
        scene.frame_set(data['source']['frame'])
        try:bpy.ops.render.render(write_still=True,scene=scene.name)
        except RuntimeError as error:
            if info['selected']!='GPU' or args.device!='auto':raise
            info['notes'].append('GPU render failed; one CPU retry: '+str(error));scene.cycles.device='CPU';info['selected']='CPU';info['backend']=None;info['devices']=[];bpy.ops.render.render(write_still=True,scene=scene.name)
    report={'bridgeVersion':1,'blenderVersion':bpy.app.version_string,'source':data['source'],'environment':data.get('environment'),'objects':len(objects),'sharedGeometryCount':len({o.data.as_pointer() for o in objects.values()}),'configuration':info,'rendered':not args.check_only,'output':str(output) if not args.check_only else None,'width':int(scene.render.resolution_x*args.scale/100),'height':int(scene.render.resolution_y*args.scale/100),'secondsInsideBlender':round(time.monotonic()-started,3),'maxProcessRssKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'memoryScope':'This Blender process maximum RSS on Linux; not total GPU/driver memory.','omissions':data['omissions']}
    output.with_suffix('.report.json').write_text(json.dumps(report,indent=2)+'\n');print('BRIDGE_RESULT '+json.dumps(report),flush=True)

if __name__=='__main__':main(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
