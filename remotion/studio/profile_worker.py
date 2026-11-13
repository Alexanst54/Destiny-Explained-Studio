"""Instrumented sidecar; imports approved build/update providers without editing them."""
import cProfile,json,os,pstats,resource,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'blender'))
from perf_common import atomic_json,identity,valid_record,sha,checkpoint,cpu_snapshot,cpu_delta
from universal.worker import build,update
from universal.request import validate


def main():
    import bpy
    args=sys.argv[sys.argv.index('--')+1:];plan=json.loads(Path(args[0]).read_text());settings=plan['settings'];state=None;state_key=None;wall=time.perf_counter();build_count=0
    offsets={i['id']:i['startFrame'] for i in json.loads((Path(__file__).resolve().parents[2]/'episodes/atheon-explained-en/audio-evidence/timing.json').read_text())['scenes']}
    events=Path(plan['events']);events.parent.mkdir(parents=True,exist_ok=True)
    def event(phase,**values):
        with events.open('a') as f:f.write(json.dumps(dict(phase=phase,epochSeconds=time.time(),**values))+'\n')
    event('worker-ready',blenderVersion=bpy.app.version_string)
    for job in plan['jobs']:
        r=validate(job['request']);out=Path(job['output']);out.mkdir(parents=True,exist_ok=True);path=out/'profile.json'
        wanted=identity(job['identityJob'],settings,plan['blenderVersion']);report=json.loads(path.read_text()) if path.exists() else dict(identity=wanted,frames={},builds=[])
        if report['identity']!=wanted:raise ValueError('Profile provenance mismatch; restore commit or use a new output.')
        report.update(status='running',request=r,settings=settings,builds=[],driveCheckpoints=[]);atomic_json(path,report)
        try:
            key=json.dumps({k:r[k] for k in ['selectionId','binding','quality','seed','lod','width','height','fps','environmentVariant']},sort_keys=True)
            verified=time.perf_counter();pending=[i for i in job['indices'] if not valid_record(out,str(i),report['frames'].get(str(i)),r['width'],r['height'])];report['cacheVerificationSeconds']=time.perf_counter()-verified
            if not pending:report['status']='success';atomic_json(path,report);continue
            if state is None or key!=state_key or not settings['persistent']:
                if state is not None:
                    old_scene=state['scene']
                    # Release a different scene rather than retaining multiple BVHs in VRAM.
                    state=None
                    bpy.data.scenes.remove(old_scene)
                    for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
                    for mesh in list(bpy.data.meshes):
                        if not mesh.users:bpy.data.meshes.remove(mesh)
                    for material in list(bpy.data.materials):
                        if not material.users:bpy.data.materials.remove(material)
                event('scene-build-start',job=job['id']);ts=time.perf_counter();cpu=time.process_time();prof=cProfile.Profile();prof.enable();state=build(r,plan['device'],settings['threads'],out);prof.disable();build_count+=1
                build_seconds=time.perf_counter()-ts;cpu_seconds=time.process_time()-cpu
                entries=[]
                for (file,line,function),(cc,nc,tt,ct,callers) in pstats.Stats(prof).stats.items():
                    if function in ['generate_design','compile_design','generate','build_scene','add_wear']:entries.append(dict(file=Path(file).name,function=function,calls=nc,selfProfileSeconds=tt,cumulativeProfileSeconds=ct))
                report['builds'].append(dict(seconds=build_seconds,cpuSeconds=cpu_seconds,geometryFunctions=entries,note='cProfile cumulative timings overlap; do not sum nested functions'))
                state_key=key;scene=state['scene'];scene.render.use_persistent_data=True;scene.render.image_settings.compression=settings['pngCompression']
                if settings['samples'] is not None:scene.cycles.samples=settings['samples']
                if settings.get('productionPreset')=='candidate-48':
                    # Apply the T4 lab's measured Candidate 48 recipe, without changing geometry.
                    # Fail explicitly rather than silently falling back to CPU compositing/denoising.
                    import _cycles
                    if not getattr(_cycles,'with_openimagedenoise',False):
                        raise RuntimeError('Candidate 48 requires OpenImageDenoise in Blender')
                    if not hasattr(scene.render,'compositor_device') or not hasattr(scene.render,'compositor_precision'):
                        raise RuntimeError('Candidate 48 requires Blender GPU compositor settings')
                    if not hasattr(scene.cycles,'denoising_use_gpu') or not hasattr(scene.cycles,'use_auto_tile'):
                        raise RuntimeError('Candidate 48 requires OIDN GPU and auto-tiling controls')
                    scene.cycles.samples=48
                    scene.cycles.use_denoising=True
                    scene.cycles.denoiser='OPENIMAGEDENOISE'
                    scene.cycles.denoising_use_gpu=True
                    scene.cycles.use_auto_tile=False
                    scene.render.compositor_device='GPU'
                    scene.render.compositor_precision='FULL'

                if settings['denoise']!='existing':
                    if settings['denoise']=='on':
                        import _cycles
                        if not getattr(_cycles,'with_openimagedenoise',False):raise ValueError('Requested denoising is unavailable in this Blender build')
                    scene.cycles.use_denoising=settings['denoise']=='on'
                if plan.get('direction'):
                    from cinematic_direction import install
                    install(state)
                event('scene-build-end',job=job['id'],seconds=build_seconds)
            scene=state['scene']
            # Venus/Vault stores its request in state. Never leave a previous scene's animation active.
            if state['provider']=='venus-vault':
                from venus_vault.request import select
                camera={'front':'front','three-quarter':'orbit','silhouette':'front','environment':'wide','reveal':'ground-reveal','close-up':'close-up'}[r['view']]
                state['request']=select(r['selectionId'],r['quality'],r['seed'],camera,r['animation'],r['frames'],r['fps'],r['width'],r['height'],r['startFrame'],r['lod'])
            configuration={**state['configuration'], 'samples':scene.cycles.samples,'denoise':scene.cycles.use_denoising,'persistentData':scene.render.use_persistent_data,'pngCompression':scene.render.image_settings.compression}
            if plan.get('requireGpu') and configuration.get('selected')!='GPU':raise RuntimeError('No actual GPU selected; benchmark stopped rather than silently timing CPU')
            report['configuration']=configuration
            for index in pending:
                frame=r['startFrame']+index;event('frame-update',job=job['id'],frame=frame);ts=time.perf_counter();cpu=time.process_time();before_update=cpu_snapshot();update(state,r,frame)
                if plan.get('direction'):
                    from cinematic_direction import apply
                    apply(state,job['sceneId'],frame,job['sceneFrames'])
                update_seconds=time.perf_counter()-ts;cpu_update=time.process_time()-cpu;update_scheduling=cpu_delta(before_update,cpu_snapshot());camera_diagnostic=None
                if plan.get('direction'):
                    from shot_audit import diagnostic
                    camera_diagnostic=diagnostic(job['sceneId'],frame,job['sceneFrames'],scene,offsets[job['sceneId']]);event('camera-applied',job=job['id'],**camera_diagnostic)
                geometry_counts=dict(objects=len(scene.objects),meshes=len(bpy.data.meshes),vertices=sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH'))
                event('cycles-and-compositor',job=job['id'],frame=frame);ts=time.perf_counter();cpu=time.process_time();before_render=cpu_snapshot()
                # Render and encode are intentionally separated. Blender log captures Cycles sync,
                # BVH, sampling, denoising and compositing stages; this wall metric includes all.
                bpy.ops.render.render(write_still=False,scene=scene.name)
                render_seconds=time.perf_counter()-ts;render_cpu=time.process_time()-cpu;render_scheduling=cpu_delta(before_render,cpu_snapshot())
                event('png-save',job=job['id'],frame=frame);tmp=out/f'pending-{index:04d}.png';ts=time.perf_counter();cpu=time.process_time();before_png=cpu_snapshot();bpy.data.images['Render Result'].save_render(str(tmp),scene=scene);save_seconds=time.perf_counter()-ts;save_cpu=time.process_time()-cpu;png_scheduling=cpu_delta(before_png,cpu_snapshot())
                ts=time.perf_counter()
                from universal.cache import valid_png
                if not valid_png(tmp,r['width'],r['height']):raise ValueError('Invalid rendered PNG')
                final=out/f'frame-{index:04d}.png';os.replace(tmp,final);checksum=sha(final);verification_seconds=time.perf_counter()-ts
                report['frames'][str(index)]=dict(invocationId=plan['invocationId'],file=final.name,sourceFrame=frame,sha256=checksum,updateSeconds=update_seconds,updateCpuSeconds=cpu_update,renderAndCompositeSeconds=render_seconds,renderCpuSeconds=render_cpu,pngEncodeAndWriteSeconds=save_seconds,pngCpuSeconds=save_cpu,verifySeconds=verification_seconds,device=configuration,geometry=geometry_counts,cameraDiagnostic=camera_diagnostic,cpuScheduling=dict(update=update_scheduling,render=render_scheduling,png=png_scheduling),cameraMatrix=[list(row) for row in scene.camera.matrix_world])
                atomic_json(path,report);event('frame-complete',job=job['id'],frame=frame)
                # At most checkpointEvery-1 freshly rendered frames can be lost on a VM loss.
                if job.get('remote') and len(report['frames'])%plan['checkpointEvery']==0:
                    event('drive-checkpoint',job=job['id']);io=checkpoint(out,job['remote'],wanted,r['width'],r['height']);report.setdefault('driveCheckpoints',[]).append(io);atomic_json(path,report)
            report.update(status='success',workerSeconds=time.perf_counter()-wall,processBuildCount=build_count,peakProcessRssKiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss);atomic_json(path,report)
            if job.get('remote'):
                event('drive-checkpoint',job=job['id']);io=checkpoint(out,job['remote'],wanted,r['width'],r['height']);report.setdefault('driveCheckpoints',[]).append(io);atomic_json(path,report);atomic_json(Path(job['remote'])/'profile.json',report)
        except BaseException as error:
            report.update(status='failed',error=str(error));atomic_json(path,report)
            if job.get('remote'):
                try:checkpoint(out,job['remote'],wanted,r['width'],r['height'])
                except Exception:pass
            event('failure',job=job['id'],error=str(error));raise
    event('worker-finished',seconds=time.perf_counter()-wall,builds=build_count)
if __name__=='__main__':main()
