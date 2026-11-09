"""Original heavy Nezarec anatomy: red barrel chest, horned mask and crescent scythe."""
import math
from venus_vault.geometry import Design,PALETTE
from .raid_shapes import check,taper,shell,limb,beam,arc_blade,motes,floor,camera_for,wear
SUPPORTED_ENTITIES=('boss-nezarec','root-of-nightmares')
SUPPORTED_VIEWS=('front','profile','three-quarter','cinematic','environment','silhouette','reveal','close-up')
LABEL='Nezarec'
MATERIALS={'nezarec-flesh':('#ad433c',.6,.05,0),'nezarec-ridge':('#6d292b',.72,.08,0),'nezarec-armor':('#252b32',.53,.5,0),'nezarec-mask':('#879699',.38,.65,0),'nezarec-bone':('#e0d1b3',.72,.1,0),'nezarec-eye':('#be90f8',.24,.1,4),'nezarec-pain-glow':('#9354de',.3,.08,2.2),'nezarec-light-glow':('#ffe3ba',.4,.08,1.5),'nezarec-root':('#d8c8aa',.87,.06,0),'nezarec-pyramid':('#343440',.78,.32,0),'nezarec-pink':('#b68b96',.75,.15,0)}
EMISSION_MATERIALS=('nezarec-eye','nezarec-pain-glow','nezarec-light-glow')
SCENE_STYLE=dict(studioGround=True,worldColor='#8998a7',worldStrength=.32,hazeFactor=.075,hazeColor='#c9b8cf',fogPosition=(0,24,15),fogScale=(90,110,44),lights=[('Pale root key',(-17,-14,26),(0,12,8),14000,'#fff0d2',11),('Nightmare fill',(18,-1,18),(0,12,8),5000,'#b38cdd',11),('Light rim',(-4,30,25),(0,12,9),18000,'#cae8ef',10)])
def setup():PALETTE.update(MATERIALS)
def decorate_material(mat,name):wear(mat,name)

def generate(seed=42,quality='balanced',lod=0):
 check(lod);setup();d=Design('boss-nezarec',seed,quality)
 d.joint('root',(0,12,.3));d.joint('haunches',(0,0,5.4),'root');d.joint('belly',(0,.1,1.5),'haunches');d.joint('sternum',(0,-.1,1.8),'belly');d.joint('head',(0,-.3,3.15),'sternum')
 shell(d,'massive-haunches',(0,.1,.1),(2.7,1.65,1.7),'nezarec-flesh','haunches',lod)
 shell(d,'barrel-belly',(0,.1,.55),(3.0,1.95,2.45),'nezarec-flesh','belly',lod)
 shell(d,'heavy-red-thorax',(0,0,.9),(3.65,2.1,2.7),'nezarec-flesh','sternum',lod)
 for s in [-1,1]:
  for j in range([16,8,4][lod]):
   z=-.6+j*.22;beam(d,f'flesh-fold-{s}-{j}',(s*.2,-1.94,z),(s*(2.25+.1*math.sin(j)),-1.55,z+.3),.09,.09,'nezarec-ridge','belly')
  for j in range([12,6,3][lod]):
   z=-.4+j*.28
   beam(d,f'luminous-chest-vein-{s}-{j}',(s*.12,-2.13,z),(s*(1.5+j*.1),-1.9,z+.5),.06,.06,'nezarec-light-glow','sternum')
  for j in range(4):taper(d,f'hip-thorn-{s}-{j}',(s*(1.6+j*.3),.45,.2),(s*(2.5+j*.3),.6,1.2+j*.15),.6,.5,'nezarec-ridge','haunches',lod)
 # Buried neck and an elongated armoured mask with two swept horns, seven purple eyes.
 shell(d,'metallic-mask',(0,-.15,.45),(.8,.74,1.6),'nezarec-mask','head',lod)
 taper(d,'mask-keel',(0,-.84,1.2),(0,-1,-.9),.55,.28,'nezarec-armor','head',lod)
 for s in [-1,1]:
  taper(d,'swept-horn-'+str(s),(s*.55,.05,1),(s*1.15,.25,3),.6,.55,'nezarec-mask','head',lod)
  taper(d,'horn-forward-keel-'+str(s),(s*.4,-.5,.9),(s*.7,-.45,2.5),.28,.2,'nezarec-armor','head',lod)
 for i,(x,z) in enumerate([(0,.2),(-.19,.22),(.19,.22),(-.26,.42),(.26,.42),(-.15,.64),(.15,.64)]):d.box('seven-eye-'+str(i),(x,-.91,z),(.1,.08,.1),'nezarec-eye',joint='head')
 for s,n in [(-1,'L'),(1,'R')]:
  d.joint('thigh'+n,(s*1.85,.1,-.35),'haunches');d.joint('knee'+n,(s*.3,.25,-2.6),'thigh'+n);d.joint('foot'+n,(0,-.1,-2.3),'knee'+n)
  limb(d,'thick-thigh-'+n,(0,0,-.2),(s*.25,.2,-2.4),1.7,1.7,'nezarec-armor','nezarec-ridge','thigh'+n,lod)
  limb(d,'thick-shin-'+n,(0,0,-.2),(0,-.1,-2.1),1.5,1.4,'nezarec-armor','nezarec-ridge','knee'+n,lod)
  shell(d,'knee-mass-'+n,(0,0,0),(.75,.75,.6),'nezarec-ridge','knee'+n,lod,segments=[16,10,6][lod],rings=[8,4,2][lod])
  shell(d,'heavy-foot-'+n,(0,-.3,0),(.9,1.1,.32),'nezarec-armor','foot'+n,lod)
  for toe in [-1,0,1]:taper(d,f'claw-foot-{n}-{toe}',(toe*.4,-.7,.1),(toe*.5,-1.7,-.1),.36,.3,'nezarec-bone','foot'+n,lod)
  d.joint('shoulder'+n,(s*3.7,.05,1.65),'sternum');d.joint('elbow'+n,(s*.55,0,-2.35),'shoulder'+n);d.joint('palm'+n,(0,-.25,-2.25),'elbow'+n);d.joint('fingers'+n,(0,-.1,-.1),'palm'+n)
  limb(d,'massive-upper-arm-'+n,(0,0,-.1),(s*.5,0,-2.15),1.5,1.55,'nezarec-armor','nezarec-ridge','shoulder'+n,lod)
  limb(d,'massive-forearm-'+n,(0,0,-.2),(0,-.2,-2.1),1.7,1.6,'nezarec-armor','nezarec-ridge','elbow'+n,lod)
  shell(d,'elbow-mass-'+n,(0,0,0),(.8,.8,.6),'nezarec-ridge','elbow'+n,lod,segments=[16,10,6][lod],rings=[8,4,2][lod])
  shoulder_mat='nezarec-bone' if s>0 else 'nezarec-armor'
  shell(d,'asymmetric-pauldron-'+n,(s*.05,.1,-.1),(1.65,1.45,1.25),shoulder_mat,'shoulder'+n,lod)
  for j in range([7,4,2][lod]):taper(d,f'shoulder-spur-{n}-{j}',(s*(j*.18),.2+j*.15,.45),(s*(.3+j*.26),.45+j*.15,1.8+(j%2)*.5),.6,.5,shoulder_mat,'shoulder'+n,lod)
  for j in range([7,4,2][lod]):d.ring(f'arm-carapace-band-{n}-{j}',(0,0,-.25-j*.25),.9,'nezarec-mask',.06,[24,12,8][lod],joint='elbow'+n)
  shell(d,'palm-'+n,(0,-.05,-.1),(.7,.5,.55),'nezarec-armor','palm'+n,lod)
  for finger in range(3):
   x=(finger-1)*.4;beam(d,f'knuckle-{n}-{finger}',(x,-.1,-.3),(x,-.3,-1),.22,.28,'nezarec-armor','fingers'+n)
   taper(d,f'claw-hand-{n}-{finger}',(x,-.3,-1),(x*.8,-.7,-1.3),.23,.2,'nezarec-bone','fingers'+n,lod)
  d.joint('backFan'+n,(s*1.5,1.6,1.8),'sternum')
  for j in range(4):
   a=(s*.1,.1,0);b=(s*(3+j*.7),1+j*.5,3.7-j*.8)
   taper(d,f'back-growth-{n}-{j}',a,b,.55,.4,'nezarec-bone' if j%2 else 'nezarec-pink','backFan'+n,lod)
   beam(d,f'back-growth-vein-{n}-{j}',a,b,.045,.05,'nezarec-pain-glow','backFan'+n)
 d.joint('scythe',(-.3,-.1,0),'palmL');beam(d,'night-terror-shaft',(0,0,-2.7),(0,0,6),.38,.44,'nezarec-armor','scythe')
 for j in range([30,15,7][lod]):d.box('scythe-binding-'+str(j),(0,0,-2.3+j*.27),(.47,.5,.08),'nezarec-mask',joint='scythe')
 arc_blade(d,'night-terror-crescent',(-.1,0,4.7),3.35,.07*math.pi,1.35*math.pi,1.1,'nezarec-armor','scythe',lod)
 arc_blade(d,'night-terror-edge',(-.1,-.2,4.7),3.75,.1*math.pi,1.32*math.pi,.22,'nezarec-mask','scythe',lod)
 taper(d,'scythe-beak',(2.9,0,5.5),(4.35,0,4.6),.7,.4,'nezarec-armor','scythe',lod)
 d.joint('nightmare',(0,0,0),'sternum');motes(d,'nightmare-fragments','nightmare','nezarec-pain-glow',5,lod)
 return d.result()

def arena(seed=42,quality='balanced',lod=0):
 check(lod);setup();d=Design('root-of-nightmares',seed,quality);floor(d,'broken-pyramid','nezarec-pyramid','nezarec-armor',52,64,lod)
 for s in [-1,1]:
  for j in range(3):
   x=s*(12+j%2*3);y=1+j*14;d.box(f'seed-platform-{s}-{j}',(x,y,.5),(8,8,1),'nezarec-pyramid')
   shell(d,f'light-dark-seed-{s}-{j}',(x,y,2.4),(.75,.75,1.1),'nezarec-light-glow' if s<0 else 'nezarec-pain-glow',None,lod)
  for j in range(5):
   y=-5+j*13
   points=[(s*28,y,-1),(s*21,y+3,4),(s*26,y+6,11),(s*18,y+10,20),(s*7,y+16,27)]
   for k in range(4):
    limb(d,f'giant-root-{s}-{j}-{k}',points[k],points[k+1],2.6-k*.4,2.7-k*.4,'nezarec-root','nezarec-pink',None,lod)
   for k in range(3):taper(d,f'root-branch-{s}-{j}-{k}',points[k+1],(points[k+1][0]+s*5,points[k+1][1]+4,points[k+1][2]+5),.8,.7,'nezarec-root',None,lod)
 for j in range(6):
  d.box('pyramid-remnant-'+str(j),((j-2.5)*8,44,5+j%3*2),(5,6,10+j%3*4),'nezarec-armor',(0,(j-2.5)*.09,0))
 return d.result()

def pose(animation,frame,fps=24):
 if animation not in ['idle','move','combat','signature','reveal']:raise ValueError('Unknown Nezarec animation')
 if type(frame) is not int or frame<0 or type(fps) is not int or fps not in [24,30]:raise ValueError('Invalid animation time')
 t=frame/fps;b=math.sin(t*1.7);r={'sternum':(.02*b,0,.012*math.sin(t)),'head':(.06*math.sin(t*.8),0,.045*math.sin(t*.9)),'shoulderL':(-.15,0,-.13),'shoulderR':(.05,0,.13),'scythe':(0,-.23,0),'nightmare':(0,0,t*.3)};p={};scale={'belly':(1+.012*b,1+.018*b,1)}
 if animation=='move':
  q=math.sin(t*4);p['root']=(.5*math.sin(t*2),12+1.5*math.sin(t*2),.3+.15*abs(q));r.update(thighL=(-.26*q,0,0),thighR=(.26*q,0,0),kneeL=(.25*max(0,q),0,0),kneeR=(.25*max(0,-q),0,0),sternum=(.12,0,.08*q),shoulderR=(.15*q,0,.25))
 if animation=='combat':
  u=math.sin(math.pi*min(t/1.3,1));r.update(sternum=(.08*u,0,-.4*u),shoulderL=(-.8*u,0,-.13-.45*u),elbowL=(-.4*u,0,0),scythe=(0,-.23+.25*u,-.65*u),shoulderR=(-.35*u,0,.3),fingersR=(.4*u,0,0));p['root']=(0,12-1.1*u,.3)
 if animation=='signature':
  u=math.sin(math.pi*min(t/1.4,1));p['root']=(0,12,.3+1.6*u);r.update(shoulderL=(-1.2*u,0,-.3),shoulderR=(-1.2*u,0,.3),elbowL=(-.4*u,0,0),elbowR=(-.4*u,0,0),head=(.2*u,0,0),backFanL=(0,-.25*u,0),backFanR=(0,.25*u,0));scale['nightmare']=(1+1.5*u,)*3
 if animation=='reveal':
  u=min(t/2,1);u=u*u*(3-2*u);r.update(head=(.3*(1-u),0,0),sternum=(.12*(1-u),0,0),backFanL=(0,-.35*(1-u),0),backFanR=(0,.35*(1-u),0),fingersL=(.4*(1-u),0,0),fingersR=(.4*(1-u),0,0))
 return dict(position=p,rotation=r,scale=scale,emissionPulse=1+.2*b+(.75*math.sin(math.pi*min(t/1.4,1)) if animation=='signature' else 0))
def camera(view,frame=0,fps=24):return camera_for(view,15,17,frame,fps)
