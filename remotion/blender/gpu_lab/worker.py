"""Lab-only Cycles worker, reusing the original builder and cinematic director."""
import json,os,resource,sys,time,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from common import *
from universal.worker import build,update
from cinematic_direction import install,apply
from shot_audit import diagnostic
from perf_common import cpu_snapshot,cpu_delta

CYCLE_KEYS=['samples','use_denoising','denoiser','denoising_use_gpu','denoising_prefilter','denoising_quality','use_adaptive_sampling','adaptive_threshold','adaptive_min_samples','max_bounces','diffuse_bounces','glossy_bounces','transmission_bounces','transparent_max_bounces','volume_bounces','volume_step_rate','volume_max_steps','use_light_tree','use_auto_tile','tile_size','use_animated_seed','seed']
def capture(scene):
 return {**{k:getattr(scene.cycles,k) for k in CYCLE_KEYS if hasattr(scene.cycles,k)},**{k:getattr(scene.render,k) for k in ['compositor_device','compositor_precision','use_compositing','threads','threads_mode','use_persistent_data'] if hasattr(scene.render,k)}}

def device(scene,cpu=False):
 import bpy
 prefs=bpy.context.preferences.addons['cycles'].preferences
 before=[]
 if not cpu:
  for backend in ['OPTIX','CUDA']:
   try:
    prefs.compute_device_type=backend;prefs.get_devices();gpus=[d for d in prefs.devices if d.type==backend and 'T4' in d.name]
    if not gpus:continue
    before=[dict(id=d.id,name=d.name,type=d.type,use=d.use) for d in prefs.devices];chosen=sorted(gpus,key=lambda d:d.id)[0]
    for d in prefs.devices:d.use=d.id==chosen.id and d.type==backend
    scene.cycles.device='GPU'
    return dict(selected='GPU',backend=backend,name=chosen.name,id=chosen.id,before=before,enabled=[dict(id=d.id,name=d.name,type=d.type,use=d.use) for d in prefs.devices],oidnGpuSupported=bool(prefs.has_oidn_gpu_devices()),optixDenoiserSupported=bool(prefs.has_optixdenoiser_gpu_devices()))
   except (RuntimeError,TypeError):continue
  raise RuntimeError('One actual Tesla T4 / OptiX or CUDA device is required; CPU fallback is forbidden in this lab')
 scene.cycles.device='CPU';return dict(selected='CPU',backend=None,name='CPU validation only',enabled=[],oidnGpuSupported=False,optixDenoiserSupported=False)

def configure(scene,settings):
 for key,value in settings.items():
  target=scene.render if key.startswith('compositor_') else scene.cycles
  if not hasattr(target,key):raise RuntimeError('Unsupported Blender setting '+key)
  setattr(target,key,value)

def signature(state):
 scene=state['scene']
 return digest(dict(design=state['configuration']['designSha256'],objects=[(o.type,tuple(o.matrix_world[0]),tuple(o.matrix_world[1]),tuple(o.matrix_world[2]),o.hide_render) for o in sorted(scene.objects,key=lambda o:o.name)],lights=[(o.data.type,o.data.energy,tuple(o.data.color),tuple(o.location)) for o in scene.objects if o.type=='LIGHT'],materials=[(k,[tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value for i in m.node_tree.nodes['Principled BSDF'].inputs if i.name in ['Emission Strength']]) for k,m in state['materials'].items()]))

def start_state(job,out,cpu):
 ts=time.perf_counter();t_cpu=time.process_time();state=build(job['request'],'cpu' if cpu else 'auto',3,out);install(state);scene=state['scene'];dev=device(scene,cpu)
 return state,dev,dict(wallSeconds=time.perf_counter()-ts,cpuSeconds=time.process_time()-t_cpu)

def main():
 import bpy,_cycles
 args=sys.argv[sys.argv.index('--')+1:];mode=args[0];plan=read(args[1]);out=Path(plan['output']);out.mkdir(parents=True,exist_ok=True);cpu=plan.get('cpuValidation',False)
 if bpy.app.version[:2]!=(4,3) or bpy.app.version[2]!=2:raise RuntimeError('Pinned Blender 4.3.2 required')
 if mode=='probe':
  state,dev,build_time=start_state(plan['jobs'][0],out,cpu);scene=state['scene'];defaults=capture(scene);result=dict(status='passed',blenderVersion=bpy.app.version_string,device=dev,defaults=defaults,oidnCompiled=bool(_cycles.with_openimagedenoise),autoTileAvailable=hasattr(scene.cycles,'use_auto_tile'),build=build_time)
  feature=plan.get('feature')
  if feature:
   if feature=='optix-denoiser' and not dev['optixDenoiserSupported']:raise RuntimeError('Device has no OptiX denoiser capability')
   if feature=='oidn-gpu' and not dev['oidnGpuSupported']:raise RuntimeError('Device has no OIDN GPU capability')
   if cpu:raise RuntimeError('GPU feature probes are never validated on CPU')
   scene.render.resolution_x=32;scene.render.resolution_y=32;scene.cycles.samples=1
   if feature=='optix-denoiser':scene.cycles.denoiser='OPTIX';scene.cycles.use_denoising=True
   if feature=='oidn-gpu':scene.cycles.denoiser='OPENIMAGEDENOISE';scene.cycles.use_denoising=True;scene.cycles.denoising_use_gpu=True
   if feature=='gpu-compositor':scene.render.compositor_device='GPU';scene.render.compositor_precision='FULL'
   job=plan['jobs'][0];frame=job['request']['startFrame'];update(state,job['request'],frame);apply(state,job['sceneId'],frame,job['sceneFrames']);bpy.ops.render.render(write_still=False,scene=scene.name)
   result.update(feature=feature,featureProbeOnly=True,renderedProbeResolution=[32,32],settings=capture(scene),note='Successful render + device capability; not an exclusive denoiser-kernel execution trace')
  atomic_json(out/'probe.json',result);return
 path=out/'result.json';old=read(path) if path.exists() else {}
 if old and old.get('identity')!=plan['identity']:raise RuntimeError('Render cache source/settings mismatch')
 report=dict(identity=plan['identity'],settings=plan['settings'],frames=old.get('frames',{}),status='running',cacheHits=0,newFrames=0,build=None);atomic_json(path,report);state=None;started=time.perf_counter()
 def event(phase,**extra):
  print('LAB_EVENT '+json.dumps(dict(phase=phase,epochSeconds=time.time(),**extra)),flush=True)
 try:
  for job in plan['jobs']:
   r=job['request']
   for local in range(r['frames']):
    key=job['id']+'/'+str(local);file=job['id']+f'/frame-{local:04d}.png';target=out/file;prior=report['frames'].get(key)
    ts=time.perf_counter()
    if prior and prior.get('file')==file and valid_png(target,r['width'],r['height'],prior['sha256']):report['cacheHits']+=1;report['cacheVerificationSeconds']=report.get('cacheVerificationSeconds',0)+time.perf_counter()-ts;continue
    if state is None:
     event('scene-preparation');state,dev,build_time=start_state(job,out,cpu);scene=state['scene'];report['build']=build_time;report['device']=dev;configure(scene,plan['settings']);report['actualSettings']=capture(scene)
     for key_,expected in plan['settings'].items():
      if report['actualSettings'].get(key_)!=expected:raise RuntimeError('Setting was not applied: '+key_)
    from venus_vault.request import select
    state['request']=select('boss-atheon','balanced',42,'wide',r['animation'],r['frames'],30,r['width'],r['height'],r['startFrame'],0)
    frame=r['startFrame']+local;event('frame-update',shot=job['shotId'],frame=frame);ts=time.perf_counter();before=cpu_snapshot();update(state,r,frame);apply(state,job['sceneId'],frame,job['sceneFrames']);camera=diagnostic(job['sceneId'],frame,job['sceneFrames'],scene,job['episodeOffset']);fixed=signature(state);update_wall=time.perf_counter()-ts;update_cpu=cpu_delta(before,cpu_snapshot())
    event('render-operation',shot=job['shotId'],frame=frame);ts=time.perf_counter();before=cpu_snapshot();bpy.ops.render.render(write_still=False,scene=scene.name);render_wall=time.perf_counter()-ts;render_cpu=cpu_delta(before,cpu_snapshot())
    if scene.cycles.device!=dev['selected']:raise RuntimeError('Unexpected CPU/device fallback')
    event('png-encode-write',shot=job['shotId'],frame=frame);target.parent.mkdir(parents=True,exist_ok=True);pending=target.with_suffix('.pending.png');ts=time.perf_counter();before=cpu_snapshot();bpy.data.images['Render Result'].save_render(str(pending),scene=scene);png_wall=time.perf_counter()-ts;png_cpu=cpu_delta(before,cpu_snapshot());ts=time.perf_counter()
    if not valid_png(pending,r['width'],r['height']):raise RuntimeError('Invalid rendered PNG')
    pending.replace(target);checksum=sha(target);verify_wall=time.perf_counter()-ts
    report['frames'][key]=dict(file=file,sha256=checksum,sourceFrame=frame,shotId=job['shotId'],fixedSceneSignature=fixed,camera=camera,updateWallSeconds=update_wall,renderOperationSeconds=render_wall,pngEncodeWriteSeconds=png_wall,verificationSeconds=verify_wall,cpu=dict(update=update_cpu,render=render_cpu,png=png_cpu),device=dev,exclusiveGpuKernelSeconds=None,transferSeconds=None)
    report['newFrames']+=1;atomic_json(path,report);event('frame-complete',shot=job['shotId'],frame=frame)
  report['status']='passed'
 except BaseException as error:report.update(status='failed',error=repr(error));raise
 finally:
  report.update(workerWallSeconds=time.perf_counter()-started,peakBlenderRssKiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss);atomic_json(path,report)
if __name__=='__main__':main()
