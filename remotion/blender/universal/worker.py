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
        if provider not in ['family-study','universal']:raise ValueError('Unknown universal provider')
        style={}
        PALETTE.update(palette())
        if provider=='universal':
            from universal.providers import load
            module=load(r['binding']['selectionId']);module.setup();style=getattr(module,'SCENE_STYLE',{})
        key=hashlib.sha256(json.dumps({k:r[k] for k in ['seed','quality','lod','environmentVariant']},sort_keys=True).encode()+r['binding'].get('familyId',r['binding']['selectionId']).encode()).hexdigest()
        cache=out/'design-cache.json';design=None
        if cache.exists():
            try:
                saved=json.loads(cache.read_text())
                if saved['key']==key and saved['sha256']==digest(saved['design']):design=saved['design']
            except (ValueError,KeyError):pass
        cache_hit=design is not None
        if design is None:
            design=module.arena(r['seed'],r['quality'],r['lod']) if provider=='universal' else generate(r['binding']['familyId'],r['seed'],r['quality'],r['lod'],r['environmentVariant'])
            atomic_json(cache,dict(key=key,sha256=digest(design),design=design))
        scene=bpy.data.scenes.new('Universal family study');bpy.context.window.scene=scene;scene.render.engine='CYCLES';settings=QUALITY[r['quality']]
        scene.cycles.samples=settings['samples'];scene.cycles.max_bounces=settings['bounces'];scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold={'draft':.12,'balanced':.06,'cinematic':.025}[r['quality']];scene.cycles.seed=r['seed'];scene.render.use_persistent_data=True
        import _cycles
        scene.cycles.use_denoising=bool(getattr(_cycles,'with_openimagedenoise',False))
        scene.render.threads_mode='FIXED';scene.render.threads=threads;scene.render.resolution_x=r['width'];scene.render.resolution_y=r['height'];scene.render.resolution_percentage=100;scene.render.fps=r['fps'];scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.view_settings.view_transform='AgX'
        scene.world=bpy.data.worlds.new('Family world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=linear_color(style.get('worldColor','#536172'));scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=style.get('worldStrength',.22)
        mats={}
        for name,(color,rough,metal,emission) in PALETTE.items():
            m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=linear_color(color);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;p.inputs['Emission Color'].default_value=linear_color(color);p.inputs['Emission Strength'].default_value=emission;
            if name.startswith('crota-') and emission==0:
                noise=m.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=7;noise.inputs['Detail'].default_value=3
                bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.06;m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
            if provider=='universal' and name in module.MATERIALS and hasattr(module,'decorate_material'):module.decorate_material(m,name)
            mats[name]=m
        collection=bpy.data.collections.new('Architectural study');scene.collection.children.link(collection);meshes=compile_design(design,mats,collection)
        for name,pos,target,power,color,size in style.get('lights',[('Key',(-16,-12,30),(0,16,6),16000,'#ffdeb0',12),('Fill',(18,6,19),(0,18,7),9000,'#a6d4ff',9),('Rim',(0,40,25),(0,15,7),18000,'#a1daff',8)]):
            data=bpy.data.lights.new(name,'AREA');data.energy=power;data.color=linear_color(color)[:3];data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
        haze=bpy.data.materials.new('Family atmosphere');haze.use_nodes=True;nodes=haze.node_tree.nodes;nodes.clear();v=nodes.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=settings['haze']*style.get('hazeFactor',.5);v.inputs['Anisotropy'].default_value=.2
        if 'hazeColor' in style:v.inputs['Color'].default_value=linear_color(style['hazeColor'])
        output=nodes.new('ShaderNodeOutputMaterial');haze.node_tree.links.new(v.outputs['Volume'],output.inputs['Volume'])
        from import_scene import mesh_data
        fog=bpy.data.objects.new('Bounded family mist',mesh_data('box'));collection.objects.link(fog);fog.location=style.get('fogPosition',(0,22,15));fog.scale=style.get('fogScale',(70,90,35));fog.data.materials.append(haze)
        data=bpy.data.cameras.new('Universal camera');cam=bpy.data.objects.new('Universal camera',data);scene.collection.objects.link(cam);scene.camera=cam
        info=choose_device(scene,device);info.update(samples=settings['samples'],lod=r['lod'],threads=threads,designSha256=digest(design),boxes=len(design['objects']),designCacheHit=cache_hit,batchedMeshes=len(meshes),batchedEnvironmentMeshes=len(meshes),batchedBossMeshes=0,persistentData=True,bounces=scene.cycles.max_bounces,denoise=scene.cycles.use_denoising,adaptiveThreshold=scene.cycles.adaptive_threshold,hazeDensity=v.inputs['Density'].default_value,viewTransform=scene.view_settings.view_transform,sceneStyle=style)
        state=dict(scene=scene,provider=provider,configuration=info)
        if provider=='universal':state['providerModule']=module
        if provider=='universal' and r['binding']['entity']['kind'] in ['boss','form']:
            boss=module.generate(r['seed'],r['quality'],r['lod']);joints={};col=bpy.data.collections.new('Dedicated boss/'+getattr(module,'LABEL','Crota'));scene.collection.children.link(col)
            for j in boss['joints']:
                ob=bpy.data.objects.new(j['id'],None);col.objects.link(ob);ob.location=j['position']
                if j['parent']:ob.parent=joints[j['parent']]
                joints[j['id']]=ob
            boss_meshes=compile_design(boss,mats,col,joints);info.update(batchedBossMeshes=len(boss_meshes),batchedMeshes=len(meshes)+len(boss_meshes));state.update(boss=boss,joints=joints,materials=mats)
            info.update(bossBoxes=len(boss['objects']),bossDesignSha256=digest(boss),joints=len(joints))
        if provider=='universal' and r['view'] not in ['environment','cinematic']:collection.hide_render=True
    if provider=='universal' and style.get('studioGround') and r['view'] not in ['environment','cinematic','silhouette']:
        ground=bpy.data.materials.new('Neutral study ground');ground.use_nodes=True;ground.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=linear_color('#363c40');ground.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.95
        from import_scene import mesh_data
        obj=bpy.data.objects.new('Study ground',mesh_data('box'));scene.collection.objects.link(obj);obj.location=(0,15,-.06);obj.scale=(180,180,.12);obj.data.materials.append(ground)
    if r['view']=='silhouette':
        # Original geometry, black emission override, isolated against a white world.
        m=bpy.data.materials.new('Silhouette override');m.use_nodes=True;n=m.node_tree.nodes;n.clear();em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,0,0,1);o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(em.outputs[0],o.inputs['Surface']);state['scene'].view_layers[0].material_override=m
        if provider=='venus-vault' and r['binding']['entity']['kind'] in ['boss','form']:
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
        if state['provider']=='universal':
            framing=state['providerModule'].camera(r['view'],frame,r['fps'])
            cam.location=framing['position'];cam.rotation_euler=(Vector(framing['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=framing['lens'];cam.data.sensor_fit=framing['sensorFit'];cam.data.sensor_height=framing['sensorHeight'];cam.data.clip_end=framing['far']
            if state.get('boss'):
                module=state['providerModule'];p=module.pose(r['animation'],frame,r['fps'])
                for j in state['boss']['joints']:
                    ob=state['joints'][j['id']];ob.location=p['position'].get(j['id'],j['position']);ob.scale=p.get('scale',{}).get(j['id'],(1,1,1))
                    if j['id'] in p.get('quaternion',{}):ob.rotation_mode='QUATERNION';ob.rotation_quaternion=p['quaternion'][j['id']]
                    else:ob.rotation_mode='XYZ';ob.rotation_euler=p['rotation'].get(j['id'],(0,0,0))
                for name in module.EMISSION_MATERIALS:
                    state['materials'][name].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=module.MATERIALS[name][3]*p['emissionPulse']
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
            tmp.replace(p);report['frames'][str(i)]=dict(file=p.name,sourceFrame=frame,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),seconds=time.monotonic()-ts,cameraMatrix=[list(row) for row in scene.camera.matrix_world],device=dict(report['configuration']),cameraSettings=dict(lens=scene.camera.data.lens,sensorFit=scene.camera.data.sensor_fit,sensorHeight=scene.camera.data.sensor_height,sensorWidth=scene.camera.data.sensor_width,far=scene.camera.data.clip_end),poseSha256=digest(state['providerModule'].pose(r['animation'],frame,r['fps'])) if state.get('boss') and state['provider']=='universal' else None);report['renderedThisRun']+=1;atomic_json(path,report)
        report['status']='success'
    except Exception as err:report.update(status='failed',error=str(err));raise
    finally:
        report['workerSeconds']=time.monotonic()-started;report['peakProcessRssKiB']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;report['gpuMemoryAndUtilization']=None;atomic_json(path,report)

if __name__=='__main__':main()
