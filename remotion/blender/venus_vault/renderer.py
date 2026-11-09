"""Opt-in Blender renderer using the existing bridge's geometry, colour and device helpers.
Static meshes are grouped by material/joint; the original bridge and episodes are unchanged.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from import_scene import mesh_data, linear_color, choose_device
from venus_vault.geometry import PALETTE, QUALITY, digest
from cinematic_vex.materials import add_wear
from venus_vault.design import generate_design
from venus_vault.request import validate, select
from venus_vault.camera import camera_pose
from environments import venus, vault_of_glass
from characters import vex_bosses


def compile_design(spec, materials, collection, joints=None):
    """Batch boxes using the existing bridge unit mesh; no per-box Blender operators."""
    import bpy
    from mathutils import Matrix, Vector, Euler
    unit=mesh_data('box');vertices=[v.co.copy() for v in unit.vertices];faces=[tuple(p.vertices) for p in unit.polygons]
    groups={}
    for box in spec['objects']:
        key=(box['joint'],box['material']);vs,fs=groups.setdefault(key,([],[]))
        transform=Matrix.LocRotScale(Vector(box['position']),Euler(box['rotation'],'XYZ').to_quaternion(),Vector(box['size']))
        offset=len(vs);vs.extend(tuple(transform@v) for v in vertices);fs.extend(tuple(i+offset for i in f) for f in faces)
    result=[]
    for (joint,mat),(vs,fs) in groups.items():
        mesh=bpy.data.meshes.new(spec['name']+'/'+str(joint)+'/'+mat);mesh.from_pydata(vs,[],fs);mesh.materials.append(materials[mat]);mesh.update()
        obj=bpy.data.objects.new(mesh.name,mesh);collection.objects.link(obj)
        if joint:obj.parent=joints[joint]
        result.append(obj)
    bpy.data.meshes.remove(unit)
    return result


def build_scene(request, device='auto', threads=3):
    import bpy
    from mathutils import Vector
    r=validate(request)
    if device not in ['auto','cpu'] or type(threads) is not int or not 1<=threads<=64:raise ValueError('Invalid device or threads')
    if not bpy.app.build_options.cycles:raise RuntimeError('Cycles-enabled Blender required')
    settings=QUALITY[r['quality']];outside=r['environmentId']=='venus'
    scene=bpy.data.scenes.new('VenusVault');scene.render.engine='CYCLES'
    bpy.context.window.scene=scene
    scene.cycles.samples=settings['samples'];scene.cycles.max_bounces=settings['bounces']
    scene.render.use_persistent_data=True
    scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.01 if outside else {'draft':.12,'balanced':.06,'cinematic':.025}[r['quality']];scene.cycles.adaptive_min_samples=0 if outside else 8
    scene.cycles.volume_bounces=1;scene.cycles.seed=r['seed'];scene.cycles.use_animated_seed=False
    import _cycles
    denoise=bool(getattr(_cycles,'with_openimagedenoise',False))
    scene.cycles.use_denoising=denoise;scene.cycles.sample_clamp_indirect=3
    scene.render.resolution_x=r['width'];scene.render.resolution_y=r['height'];scene.render.resolution_percentage=100
    scene.render.fps=r['fps'];scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
    scene.render.threads_mode='FIXED';scene.render.threads=threads
    scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.1 if outside else 0
    scene.world=bpy.data.worlds.new('VenusVaultWorld');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=linear_color('#a1b4a2' if outside else '#31505c')
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35 if outside else .22
    mats={}
    for name,(color,rough,metal,emission) in PALETTE.items():
        mat=bpy.data.materials.new('VV/'+name);mat.use_nodes=True;bsdf=mat.node_tree.nodes.get('Principled BSDF')
        bsdf.inputs['Base Color'].default_value=linear_color(color);bsdf.inputs['Roughness'].default_value=rough;bsdf.inputs['Metallic'].default_value=metal
        bsdf.inputs['Emission Color'].default_value=linear_color(color);bsdf.inputs['Emission Strength'].default_value=emission
        add_wear(mat,name)
        if name in ['portal-film','portal-film-amber']:
            nodes=mat.node_tree.nodes;links=mat.node_tree.links;output=nodes.get('Material Output')
            tex=nodes.new('ShaderNodeTexNoise');tex.name='Temporal interference';tex.noise_dimensions='4D';tex.inputs['Scale'].default_value=1.8;tex.inputs['Detail'].default_value=2
            transparent=nodes.new('ShaderNodeBsdfTransparent');emitter=nodes.new('ShaderNodeEmission');emitter.inputs['Color'].default_value=linear_color('#6cd8ff' if name=='portal-film' else '#d6ab68');emitter.inputs['Strength'].default_value=.6
            remap=nodes.new('ShaderNodeMath');remap.operation='MULTIPLY';remap.inputs[1].default_value=.28;links.new(tex.outputs['Fac'],remap.inputs[0])
            mix=nodes.new('ShaderNodeMixShader');links.new(remap.outputs[0],mix.inputs[0]);links.new(transparent.outputs[0],mix.inputs[1]);links.new(emitter.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],output.inputs['Surface'])
        mats[name]=mat
    env,boss,dust_spec=generate_design(r)
    env_col=bpy.data.collections.new('Environment/'+r['environmentId']);scene.collection.children.link(env_col)
    meshes=compile_design(env,mats,env_col);joints={}
    if r['bossId']:
        col=bpy.data.collections.new('Boss/'+r['bossId']);scene.collection.children.link(col)
        for j in boss['joints']:
            ob=bpy.data.objects.new(j['id'],None);col.objects.link(ob);ob.location=j['position']
            if j['parent']:ob.parent=joints[j['parent']]
            joints[j['id']]=ob
        meshes+=compile_design(boss,mats,col,joints)
    # Repeatable luminous dust motes; geometry, not an unseeded simulation/particle cache.
    dust_objects=compile_design(dust_spec,mats,env_col)
    # Bounded homogeneous volume, volumetric light shafts, no simulated weather claim.
    haze=bpy.data.materials.new('VenusMist');haze.use_nodes=True;n=haze.node_tree.nodes;n.clear()
    out=n.new('ShaderNodeOutputMaterial');vol=n.new('ShaderNodeVolumePrincipled');vol.inputs['Density'].default_value=settings['haze']*(.55 if r['environmentId']=='arena-glass-throne' else 1)
    vol.inputs['Color'].default_value=linear_color('#b9c5a8' if outside else '#7ca6b4');vol.inputs['Anisotropy'].default_value=.25
    haze.node_tree.links.new(vol.outputs['Volume'],out.inputs['Volume'])
    fog=bpy.data.objects.new('Bounded atmosphere',mesh_data('box'));env_col.objects.link(fog);fog.data.materials.append(haze)
    fog.location=(0,35,29) if r['environmentId']=='arena-glass-throne' else (0,12,14);fog.scale=(150,170,64) if r['environmentId']=='arena-glass-throne' else (82,82,32)
    def light(name,kind,pos,target,color,power,size=6):
        data=bpy.data.lights.new(name,kind);data.energy=power;data.color=linear_color(color)[:3]
        if kind=='AREA':data.shape='DISK';data.size=size
        if kind=='SUN':data.angle=.15
        obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=pos
        obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    if outside:
        light('Warm key','SUN',(-18,-10,30),(0,9,2),'#ffdf9c',3.2,15)
        light('Cyan fill','AREA',(14,-4,14),(0,9,5),'#82dbf5',2000,12)
        light('Vault rim','AREA',(0,21,20),(0,9,6),'#d1f5ff',3500,10)
        light('Boss face','AREA',(-5,-4,10),(0,9,6),'#e5e7d5',600,8)
    else:
        light('Warm sculpting key','AREA',(-21,-15,32),(0,9,11),'#e4e4d5',18000,11)
        light('Cyan fill','AREA',(19,-3,21),(0,9,10),'#79c9ef',6500,11)
        light('Vault backlight','AREA',(-5,27,34),(0,9,10),'#b9dcff',26000,8)
        light('Boss face','AREA',(-7,-9,19),(0,9,13),'#c3e8ff',2400,6)
        for s in [-1,1]:light('Portal bounce '+str(s),'AREA',(s*16,21,10),(0,9,9),'#86e6ff' if s<0 else '#ffe3aa',2000,7)
    data=bpy.data.cameras.new('VaultCinema');camera=bpy.data.objects.new('VaultCinema',data);scene.collection.objects.link(camera);scene.camera=camera
    scene.use_nodes=True;tree=scene.node_tree;tree.nodes.clear();layers=tree.nodes.new('CompositorNodeRLayers');layers.scene=scene
    glow=tree.nodes.new('CompositorNodeGlare');glow.glare_type='FOG_GLOW';glow.quality='HIGH';glow.threshold=2;glow.size=7;glow.mix=-.9
    output=tree.nodes.new('CompositorNodeComposite');tree.links.new(layers.outputs['Image'],glow.inputs['Image']);tree.links.new(glow.outputs['Image'],output.inputs['Image'])
    info=choose_device(scene,device)
    info.update(lod=r['lod'],adaptiveThreshold=scene.cycles.adaptive_threshold,persistentData=scene.render.use_persistent_data,samples=settings['samples'],bounces=settings['bounces'],denoise=denoise,threads=threads,
                hazeDensity=vol.inputs['Density'].default_value,viewTransform='AgX',environmentBoxes=len(env['objects']),bossBoxes=len(boss['objects']) if boss else 0,
                batchedMeshes=len(meshes),particles=settings['particles'],designSha256=digest({'environment':env,'boss':boss,'dust':dust_spec}))
    if not denoise:info['notes'].append('OpenImageDenoise unavailable; rendered without denoising.')
    state=dict(scene=scene,request=r,joints=joints,boss=boss,dust=dust_objects,materials=mats,configuration=info)
    update_frame(state,0)
    return state


def update_frame(state, frame):
    from mathutils import Vector
    r=state['request'];scene=state['scene'];scene.frame_set(frame)
    p=camera_pose(r['environmentId'],r['camera'],frame,r['fps']);cam=scene.camera
    cam.location=p['position'];cam.rotation_euler=(Vector(p['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.sensor_fit=p['sensorFit'];cam.data.sensor_height=p['sensorHeight'];cam.data.lens=p['lens'];cam.data.clip_start=p['near'];cam.data.clip_end=p['far']
    if r['bossId']:
        pose=vex_bosses.pose(r['bossId'],r['animation'],frame,r['fps'])
        for j in state['boss']['joints']:
            obj=state['joints'][j['id']];obj.location=pose['position'].get(j['id'],j['position']);obj.scale=pose.get('scale',{}).get(j['id'],(1,1,1))
            if j['id'] in pose.get('quaternion',{}):obj.rotation_mode='QUATERNION';obj.rotation_quaternion=pose['quaternion'][j['id']]
            else:obj.rotation_mode='XYZ';obj.rotation_euler=pose['rotation'].get(j['id'],(0,0,0))
        state['materials']['cyan'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=PALETTE['cyan'][3]*pose['emissionPulse']
    if r['bossId']:
        for material in ['circuit','radiolaria','temporal','shield-trace']:
            state['materials'][material].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=PALETTE[material][3]*pose['emissionPulse']
    for material in ['portal-film','portal-film-amber']:
        state['materials'][material].node_tree.nodes['Temporal interference'].inputs['W'].default_value=frame/r['fps']*.35
    for ob in state['dust']:ob.location.z=.15*math.sin(frame/r['fps'])
    scene.view_layers[0].update()


def main(argv):
    import argparse
    import bpy
    p=argparse.ArgumentParser();p.add_argument('request');p.add_argument('output');p.add_argument('--device',choices=['auto','cpu'],default='auto');p.add_argument('--threads',type=int,default=3);p.add_argument('--check-only',action='store_true');a=p.parse_args(argv)
    r=validate(json.loads(Path(a.request).read_text()))
    # Re-resolve against the current Atlas, so hand-edited requests cannot bypass bindings.
    fresh=select(r['selectionId'],r['quality'],r['seed'],r['camera'],r['animation'],r['frames'],r['fps'],r['width'],r['height'],r['startFrame'],r['lod'])
    if fresh!=r:raise ValueError('Request differs from current Atlas')
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True);report_path=out/'render-report.json'
    if report_path.exists() or any(out.glob('frame-*.png')):raise ValueError('Choose a fresh output directory; no stale render evidence')
    started=time.monotonic();report={'status':'running','request':r,'blenderVersion':bpy.app.version_string,'frames':[]}
    try:
        state=build_scene(r,a.device,a.threads);scene=state['scene'];report['configuration']=state['configuration'];report['buildSeconds']=round(time.monotonic()-started,3)
        for index in range(r['frames']):
            f=r['startFrame']+index
            update_frame(state,f)
            if a.check_only:continue
            frame_started=time.monotonic();path=out/f'frame-{index:04d}.png';scene.render.filepath=str(path.resolve())
            try:bpy.ops.render.render(write_still=True,scene=scene.name)
            except RuntimeError as error:
                if report['configuration']['selected']!='GPU' or a.device!='auto':raise
                scene.cycles.device='CPU';report['configuration'].update(selected='CPU',backend=None)
                report['configuration']['notes'].append('GPU render failed; CPU retry: '+str(error));bpy.ops.render.render(write_still=True,scene=scene.name)
            payload=path.read_bytes()
            if not payload.startswith(b'\x89PNG\r\n\x1a\n') or len(payload)<1000:raise RuntimeError('Missing/invalid rendered PNG')
            report['frames'].append({'frame':f,'file':path.name,'seconds':round(time.monotonic()-frame_started,3),'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest(),
                                     'camera':camera_pose(r['environmentId'],r['camera'],f,r['fps'])})
            report_path.write_text(json.dumps(report,indent=2)+'\n')
        report['status']='checked-only' if a.check_only else 'success'
    except Exception as error:
        report.update(status='failed',error=str(error));raise
    finally:
        report['secondsInsideBlender']=round(time.monotonic()-started,3)
        report['peakProcessRssKiB']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        report['memoryScope']='Linux Blender process peak RSS; GPU memory/utilization not measured.'
        report_path.write_text(json.dumps(report,indent=2)+'\n')
    print('VENUS_VAULT_RESULT '+json.dumps(report),flush=True)

if __name__=='__main__':main(sys.argv[sys.argv.index('--')+1:])
