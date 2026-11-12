"""Canonical discrete shot ranges; exact source-frame coverage, not rounded seconds."""
import math
from cinematic_direction import SHOTS,shot_at,camera

def timeline(package):
 rows=[]
 for item in package['scenes']:
  sid=item['scene']['id'];n=item['timing']['durationFrames'];offset=item['timing']['startFrame'];start=0
  while start<n:
   shot=shot_at(sid,start,n);end=start+1
   while end<n and shot_at(sid,end,n)['name']==shot['name']:end+=1
   rows.append(dict(shotId=sid+'/'+shot['name'],cameraId=shot['name'],sceneId=sid,sceneFrameStart=start,sceneFrameEndExclusive=end,episodeFrameStart=offset+start,episodeFrameEndExclusive=offset+end,animation=shot['animation'],firstCamera=camera(shot),lastCamera=camera(shot_at(sid,end-1,n))))
   start=end
 if len(rows)!=19 or [f for r in rows for f in range(r['episodeFrameStart'],r['episodeFrameEndExclusive'])]!=list(range(2672)):raise ValueError('Directed timeline is incomplete or overlapping')
 return rows

def diagnostic(scene_id,frame,scene_frames,scene,offset):
 shot=shot_at(scene_id,frame,scene_frames);wanted=camera(shot);matrix=[list(row) for row in scene.camera.matrix_world];position=list(scene.camera.location);delta=max(abs(a-b) for a,b in zip(position,wanted['position']))
 if delta>1e-4 or abs(scene.camera.data.lens-wanted['lens'])>1e-4:raise ValueError('Actual Blender camera does not match directed shot')
 return dict(route='cinematic',shotId=scene_id+'/'+shot['name'],cameraId=shot['name'],blenderCamera=scene.camera.name,sceneFrame=frame,episodeFrame=offset+frame,sceneRange=[shot['cutStart'],shot['cutEnd']],episodeRange=[offset+shot['cutStart'],offset+shot['cutEnd']],position=position,matrixWorld=matrix,lens=scene.camera.data.lens,sensorFit=scene.camera.data.sensor_fit,expectedPosition=list(wanted['position']),maxPositionError=delta)
