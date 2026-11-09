"""Persistent Blender worker; each successful PNG checkpoint is atomic and resumable."""
import sys,json,time,hashlib,resource,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from universal.request import validate
from universal.cache import atomic_json,valid_png
from universal.environments import generate,palette
from venus_vault.geometry import PALETTE,QUALITY,digest
from venus_vault.renderer import compile_design
from import_scene import linear_color,choose_device

def build(r,device,threads,out):
    import bpy
    from mathutils import Vector
    provider=r['binding']['provider']
    if provider=='venus-vault':
        from venus_vault.request import select
        from venus_vault.renderer import build_scene
        camera={'front':'front','three-quarter':'orbit','silhouette':'front','environment':'wide','reveal':'ground-reveal','close-up':'close-up'}[r['view']]
        old=select(r['binding']['selectionId'],r['quality'],r['seed'],camera,r['animation'],r['frames'],r['fps'],r['width'],r['height'],r['startFrame'],r['lod'])
        state=build_scene(old,device,threads);state['provider']=provider
    else:
        if provider!='family-study':raise ValueError('No universal model provider yet')
        PALETTE.update(palette());key=hashlib.sha256(json.dumps({k:r[k] for k in ['seed','quality','lod','environmentVariant']},sort_keys=True).encode()+r['binding']['familyId'].encode()).hexdigest()
        cache=out/'design-cache.json';design=None
        if cache.exists():
            try:
                saved=json.loads(cache.read_text())
                if saved['key']==key and saved['sha256']==digest(saved['design']):design=saved['design']
            except (ValueError,KeyError):pass
        cache_hit=design is not None
        if design is None:
            design=generate(r['binding']['familyId'],r['seed'],r['quality'],r['lod'],r['environmentVariant']);atomic_json(cache,dict(key=key,sha256=digest(design),design=design))
        scene=bpy.data.scenes.new('Universal family study');bpy.context.window.scene=scene;scene.render.engine='CYCLES';settings=QUALITY[r['quality']]
        scene.cycles.samples=settings['samples'];scene.cycles.max_bounces=settings['bounces'];scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold={'draft':.12,'balanced':.06,'cinematic':.025}[r['quality']];scene.cycles.seed=r['seed'];scene.render.use_persistent_data=True
        import _cycles
        scene.cycles.use_denoising=bool(getattr(_cycles,'with_openimagedenoise',False))
        scene.render.threads_mode='FIXED';scene.render.threads=threads;scene.render.resolution_x=r['width'];scene.render.resolution_y=r['height'];scene.render.resolution_percentage=100;scene.render.fps=r['fps'];scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.view_settings.view_transform='AgX'
        scene.world=bpy.data.worlds.new('Family world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=linear_color('#536172');scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.22
        mats={}
        for name,(color,rough,metal,emission) in PALETTE.items():
            m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=linear_color(color);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;p.inputs['Emission Color'].default_value=linear_color(color);p.inputs['Emission Strength'].default_value=emission;mats[name]=m
        collection=bpy.data.collections.new('Architectural study');scene.collection.children.link(collection);meshes=compile_design(design,mats,collection)
        for name,pos,target,power,color,size in [('Key',(-16,-12,30),(0,16,6),16000,'#ffdeb0',12),('Fill',(18,6,19),(0,18,7),9000,'#a6d4ff',9),('Rim',(0,40,25),(0,15,7),18000,'#a1daff',8)]:
            data=bpy.data.lights.new(name,'AREA');data.energy=power;data.color=linear_color(color)[:3];data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
        haze=bpy.data.materials.new('Family atmosphere');haze.use_nodes=True;nodes=haze.node_tree.nodes;nodes.clear();v=nodes.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=settings['haze']*.5;v.inputs['Anisotropy'].default_value=.2;output=nodes.new('ShaderNodeOutputMaterial');haze.node_tree.links.new(v.outputs['Volume'],output.inputs['Volume'])
        from import_scene import mesh_data
        fog=bpy.data.objects.new('Bounded family mist',mesh_data('box'));collection.objects.link(fog);fog.location=(0,22,15);fog.scale=(70,90,35);fog.data.materials.append(haze)
        data=bpy.data.cameras.new('Universal camera');cam=bpy.data.objects.new('Universal camera',data);scene.collection.objects.link(cam);scene.camera=cam
        info=choose_device(scene,device);info.update(samples=settings['samples'],lod=r['lod'],threads=threads,designSha256=digest(design),boxes=len(design['objects']),designCacheHit=cache_hit,batchedMeshes=len(meshes),persistentData=True)
        state=dict(scene=scene,provider=provider,configuration=info)
    if r['view']=='silhouette':
        # Original geometry, black emission override, isolated against a white world.
        m=bpy.data.materials.new('Silhouette override');m.use_nodes=True;n=m.node_tree.nodes;n.clear();em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,0,0,1);o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(em.outputs[0],o.inputs['Surface']);state['scene'].view_layers[0].material_override=m
        if provider=='venus-vault' and r['binding']['entity']['kind']=='boss':
            for c in state['scene'].collection.children:
                if c.name.startswith('Environment/'):c.hide_render=True
        state['scene'].world.node_tree.nodes['Background'].inputs['Color'].default_value=(1,1,1,1);state['scene'].world.node_tree.nodes['Background'].inputs['Strength'].default_value=1
    return state

def update(state,r,frame):
    if state['provider']=='venus-vault':
        from venus_vault.renderer import update_frame
        update_frame(state,frame)
    else:
        from mathutils import Vector
        scene=state['scene'];scene.frame_set(frame);cam=scene.camera;t=frame/r['fps'];a=-math.pi/2+.18+t*.035
        cam.location=(45*math.cos(a),15+45*math.sin(a),15);cam.rotation_euler=(Vector((0,20,7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=32;cam.data.clip_end=300
    state['scene'].view_layers[0].update()

def main():
    import bpy
    args=sys.argv[sys.argv.index('--')+1:];out=Path(args[0]);device=args[1];threads=int(args[2]);r=validate(json.loads((out/'request.json').read_text()));path=out/'progress.json';report=json.loads(path.read_text());started=time.monotonic()
    try:
        state=build(r,device,threads,out);scene=state['scene'];report['configuration']=state['configuration'];report['blenderVersion']=bpy.app.version_string;report['buildSeconds']=time.monotonic()-started;report['status']='running';atomic_json(path,report)
        for i in range(r['frames']):
            p=out/f'frame-{i:04d}.png';prior=report['frames'].get(str(i))
            if prior and valid_png(p,r['width'],r['height'],prior['sha256']):report['cacheHits']+=1;continue
            frame=r['startFrame']+i;update(state,r,frame);tmp=out/f'pending-{i:04d}.png';scene.render.filepath=str(tmp);ts=time.monotonic()
            try:bpy.ops.render.render(write_still=True,scene=scene.name)
            except RuntimeError as err:
                if report['configuration']['selected']!='GPU' or device!='auto':raise
                scene.cycles.device='CPU';report['configuration'].update(selected='CPU',backend=None);report['configuration'].setdefault('notes',[]).append('GPU failure, CPU retry: '+str(err));bpy.ops.render.render(write_still=True,scene=scene.name)
            if not valid_png(tmp,r['width'],r['height']):raise RuntimeError('Blender PNG decode validation failed')
            tmp.replace(p);report['frames'][str(i)]=dict(file=p.name,sourceFrame=frame,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),seconds=time.monotonic()-ts,cameraMatrix=[list(row) for row in scene.camera.matrix_world],device=dict(report['configuration']));report['renderedThisRun']+=1;atomic_json(path,report)
        report['status']='success'
    except Exception as err:report.update(status='failed',error=str(err));raise
    finally:
        report['workerSeconds']=time.monotonic()-started;report['peakProcessRssKiB']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;report['gpuMemoryAndUtilization']=None;atomic_json(path,report)

if __name__=='__main__':main()
