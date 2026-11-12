"""Six-scene visual treatment, non-destructive overlays around approved geometry.

Portal landscapes and anonymous Guardian silhouettes are original editorial
reconstructions. The Vex do not control all universal time. No imported game assets.
"""
import math

# Cut boundaries are scene-local fractions, independent of image resolution.
SHOTS={
 '01-hook':[(0,.42,'vault-establish','idle'),(.42,.72,'portal-threshold','idle'),(.72,1,'monument','reveal')],
 '02-identity':[(0,.30,'monument','reveal'),(.30,.66,'mechanism','idle'),(.66,1,'conflux','temporal')],
 '03-vault':[(0,.26,'vault-establish','idle'),(.26,.60,'oracle-field','temporal'),(.60,.80,'templar','idle'),(.80,1,'conflux','temporal')],
 '04-time':[(0,.35,'past-gate','temporal'),(.35,.70,'future-gate','temporal'),(.70,1,'return-gate','temporal')],
 '05-guardians':[(0,.40,'guardian-team','combat'),(.40,.74,'aegis','combat'),(.74,1,'conflux','combat')],
 '06-mystery':[(0,.25,'aftermath','idle'),(.25,.58,'empty-throne','idle'),(.58,1,'unanswered-vault','idle')],
}

def shot_at(scene,frame,frames):
 if scene not in SHOTS or type(frame) is not int or frame<0 or frame>=frames:raise ValueError('Invalid directed scene/frame')
 u=frame/frames
 for a,b,name,animation in SHOTS[scene]:
  if a<=u<b:return dict(name=name,animation=animation,progress=(u-a)/(b-a),cutStart=round(a*frames),cutEnd=round(b*frames))
 raise ValueError('No shot')

def camera(shot):
 n=shot['name'];u=shot['progress'];smooth=u*u*(3-2*u)
 paths={
 'vault-establish':((28,-66,25),(16,-50,22),(0,20,13),28),
 'portal-threshold':((-22,0,7),(-19,6,8),(-16,23,9),35),
 'monument':((10,-35,2.5),(6,-33,12),(0,9,11),35),
 'mechanism':((9,-12,15),(6,-10,16),(0,9,14),48),
 'conflux':((-25,-32,15),(-18,-26,13),(0,9,12),36),
 'oracle-field':((-14,-28,9),(-6,-24,11),(0,12,12),32),
 'templar':((10,-33,11),(4,-28,10),(0,9,8),36),
 'past-gate':((-32,-22,9),(-24,-12,10),(-16,23,10),32),
 'future-gate':((32,-22,9),(24,-12,10),(16,23,10),32),
 'return-gate':((0,-28,7),(4,-22,8),(0,15,9),30),
 'guardian-team':((-12,-28,4),(-6,-24,5),(0,9,10),30),
 'aegis':((10,-18,4),(7,-16,5),(0,-1,4),42),
 'aftermath':((9,-25,5),(6,-30,8),(0,9,11),32),
 'empty-throne':((0,-35,12),(0,-43,15),(0,20,12),30),
 'unanswered-vault':((5,-43,17),(24,-74,29),(0,22,14),27),
 }
 start,end,target,lens=paths[n];return dict(position=tuple(a+(b-a)*smooth for a,b in zip(start,end)),target=target,lens=lens)

def install(state):
 import bpy
 from mathutils import Vector
 from import_scene import linear_color,mesh_data
 scene=state['scene'];collection=bpy.data.collections.new('Editorial cinematic overlays');scene.collection.children.link(collection)
 mats={}
 for name,color,emission in [('guardian','#15212c',0),('light','#c4edff',5),('past','#a88345',1.2),('future','#72c7db',1.4),('oracle','#ffe596',7)]:
  mat=bpy.data.materials.new('Direction/'+name);mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=linear_color(color);p.inputs['Roughness'].default_value=.7;p.inputs['Emission Color'].default_value=linear_color(color);p.inputs['Emission Strength'].default_value=emission;mats[name]=mat
 unit=mesh_data('box');units={name:unit.copy() for name in mats}
 for name,mesh in units.items():mesh.materials.clear();mesh.materials.append(mats[name])
 bpy.data.meshes.remove(unit)
 def box(name,pos,size,material,parent=None):
  obj=bpy.data.objects.new(name,units[material]);collection.objects.link(obj);obj.location=pos;obj.scale=size;obj.parent=parent;return obj
 guardians=[]
 for i,(x,y) in enumerate([(-5,-2),(0,-1),(5,-2),(-8,3),(8,3),(0,-6)]):
  root=bpy.data.objects.new('Anonymous Guardian '+str(i),None);collection.objects.link(root);root.location=(x,y,1.25);guardians.append(root)
  for name,pos,size in [('torso',(0,0,1.5),(.65,.42,.9)),('helmet',(0,0,2.18),(.48,.46,.45)),('left-leg',(-.19,0,.55),(.23,.28,1.1)),('right-leg',(.19,0,.55),(.23,.28,1.1)),('left-arm',(-.48,0,1.4),(.22,.25,.85)),('right-arm',(.48,0,1.4),(.22,.25,.85))]:box(name,pos,size,'guardian',root)
  box('Helmet light',(0,-.238,2.18),(.27,.025,.07),'light',root)
 # Aegis-inspired abstract disc: an editorial shield, not a game mesh reproduction.
 shield=[]
 for k in range(28):
  a=k*math.tau/28;shield.append(box('Aegis light',(.98*math.cos(a),-1.6,3.25+.98*math.sin(a)),(.22,.09,.22),'light'))
 motes=[]
 for k in range(18):
  a=k*math.tau/18;motes.append(box('Temporal particle',(8*math.cos(a),9+4*math.sin(a),5+k*.65),(.10,.10,.10),'light'))
 oracles=[box('Oracle editorial light',(x,y,z),(.45,.45,.45),'oracle') for x,y,z in [(-10,12,12),(-6,19,15),(0,23,13),(8,17,15),(11,11,11)]]
 # Abstract ochre/cyan stepped landscapes visible beyond each real portal.
 landscapes=[]
 for side,material in [(-1,'past'),(1,'future')]:
  for row in range(5):
   for col in range(7):
    x=side*16+(col-3)*1.2;y=30+row*2;h=.4+((row*11+col*7)%9)*.4
    landscapes.append(box('Reconstructed portal landscape',(x,y,h/2),(1.1,1.7,h),material))
 state['direction']=dict(collection=collection,guardians=guardians,shield=shield,motes=motes,oracles=oracles,landscapes=landscapes)
 state['directionBossCollection']=next((c for c in scene.collection.children if c.name.startswith('Boss/')),None)
 # Existing approved Templar provider, distinct arena and model; loaded on its own shot build.


def apply(state,scene_id,frame,frames):
 from mathutils import Vector
 from characters import vex_bosses
 from venus_vault.geometry import PALETTE
 shot=shot_at(scene_id,frame,frames);scene=state['scene'];d=state['direction'];n=shot['name'];p=camera(shot);cam=scene.camera;cam.location=p['position'];cam.rotation_euler=(Vector(p['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=p['lens'];cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=24;cam.data.clip_end=400
 # Reapply an existing approved articulated animation to this shot; never alter geometry.
 boss=state['request']['bossId']
 if boss:
  pose=vex_bosses.pose(boss,shot['animation'] if boss=='boss-atheon' else 'idle',frame,30)
  for joint in state['boss']['joints']:
   obj=state['joints'][joint['id']];obj.location=pose['position'].get(joint['id'],joint['position']);obj.scale=pose.get('scale',{}).get(joint['id'],(1,1,1))
   if joint['id'] in pose.get('quaternion',{}):obj.rotation_mode='QUATERNION';obj.rotation_quaternion=pose['quaternion'][joint['id']]
   else:obj.rotation_mode='XYZ';obj.rotation_euler=pose['rotation'].get(joint['id'],(0,0,0))
  for material in ['cyan','circuit','radiolaria','temporal','shield-trace']:
   state['materials'][material].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=PALETTE[material][3]*pose['emissionPulse']
 if state.get('directionBossCollection'):state['directionBossCollection'].hide_render=n in ['vault-establish','portal-threshold','oracle-field','empty-throne','unanswered-vault']
 active=n in ['past-gate','future-gate','return-gate','guardian-team','aegis']
 for i,root in enumerate(d['guardians']):
  root.hide_render=not active
  for child in root.children:child.hide_render=not active
  # Teleport silhouettes in and out with reversible deterministic light pulses.
  fade=1
  if n in ['past-gate','future-gate']:fade=max(.005,1-shot['progress']*1.5)
  if n=='return-gate':fade=max(.005,min(1,shot['progress']*2))
  root.scale=(fade,fade,fade);root.rotation_euler.z=.05*math.sin(frame/30+i)
 for obj in d['shield']:obj.hide_render=n!='aegis';obj.rotation_euler.y=frame/30*.2
 for k,obj in enumerate(d['motes']):
  obj.hide_render=n not in ['conflux','past-gate','future-gate','return-gate'];obj.location.z=5+k*.65+.4*math.sin(frame/30*2+k)
 for k,obj in enumerate(d['oracles']):
  obj.hide_render=n not in ['oracle-field','guardian-team','aegis'];v=max(.02,1-shot['progress']*1.8+k*.12) if n=='guardian-team' else 1;obj.scale=(.45*v,)*3
 for material in ['portal-film','portal-film-amber']:
  state['materials'][material].node_tree.nodes['Temporal interference'].inputs['W'].default_value=frame/30*.5
 scene.view_layers[0].update()
 return shot
