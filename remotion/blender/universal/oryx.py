"""Original voxel Oryx: horizontal crown, three eyes, talons and torn articulated wings.
The carried sword is an explicitly editorial campaign-inspired option in a raid-inspired scene.
"""
import math
from venus_vault.geometry import Design,PALETTE
from .raid_shapes import check,taper,shell,limb,beam,motes,floor,camera_for,wear
SUPPORTED_ENTITIES=('boss-oryx','arena-threshold')
SUPPORTED_VIEWS=('front','profile','three-quarter','cinematic','environment','silhouette','reveal','close-up')
LABEL='Oryx'
MATERIALS={'oryx-chitin':('#514c43',.73,.18,0),'oryx-ridge':('#a49d84',.66,.16,0),'oryx-dark':('#161e20',.85,.12,0),'oryx-face':('#633e3d',.65,.05,0),'oryx-membrane':('#755944',.87,0,0),'oryx-membrane-dark':('#453d35',.91,0,0),'oryx-eye':('#e7efff',.22,.05,4),'oryx-glow':('#7ac6a0',.35,.12,2),'oryx-stone':('#45494b',.9,0,0),'oryx-sword':('#606a65',.44,.6,0)}
EMISSION_MATERIALS=('oryx-eye','oryx-glow')
SCENE_STYLE=dict(studioGround=True,worldColor='#26323b',worldStrength=.16,hazeFactor=.12,hazeColor='#a2b6c5',fogPosition=(0,24,20),fogScale=(100,120,60),lights=[('Cold sovereign key',(-24,-18,38),(0,12,15),22000,'#dedcce',14),('Green ritual fill',(24,-1,22),(0,12,13),9000,'#7cbaac',12),('Wing rim',(0,35,38),(0,12,16),28000,'#b9d9f2',13)])
def setup():PALETTE.update(MATERIALS)
def decorate_material(mat,name):wear(mat,name)

def generate(seed=42,quality='balanced',lod=0):
 check(lod);setup();d=Design('boss-oryx',seed,quality)
 d.joint('root',(0,12,.25));d.joint('pelvis',(0,0,9),'root');d.joint('thorax',(0,0,3),'pelvis');d.joint('neck',(0,.1,4.4),'thorax');d.joint('head',(0,-.4,1.15),'neck')
 shell(d,'pelvic-carapace',(0,.1,0),(2.1,1.3,1.3),'oryx-dark','pelvis',lod)
 shell(d,'chest-carapace',(0,.15,2),(3.0,1.55,2.6),'oryx-chitin','thorax',lod)
 for s in [-1,1]:
  taper(d,f'pectoral-horn-{s}',(s*.4,-1.3,2.8),(s*3.6,-.7,3.8),1.1,.7,'oryx-ridge','thorax',lod)
  for j in range([9,5,3][lod]):
   z=-1+j*.35;beam(d,f'lower-rib-{s}-{j}',(s*.35,-1.2,z),(s*(1.6+.08*j),-1,z+.4),.2,.3,'oryx-chitin','thorax')
   d.box(f'chest-rift-{s}-{j}',(s*(.3+j*.13),-1.45,z+.3),(.35,.1,.13),'oryx-glow',joint='thorax')
  taper(d,'hip-skirt-'+str(s),(s*1.6,0,.2),(s*2.4,-.1,-3.2),1,.55,'oryx-chitin','pelvis',lod)
 # A broad lateral crown framing a long tapered face, not a Vex trident.
 shell(d,'elongated-red-visage',(0,-.15,.1),(.85,.65,1.75),'oryx-face','head',lod)
 for s in [-1,1]:
  taper(d,'crown-transverse-'+str(s),(s*.45,.2,.85),(s*3.7,.4,1.55),1.4,.9,'oryx-chitin','head',lod)
  taper(d,'crown-upturn-'+str(s),(s*2.6,.3,1.2),(s*3.1,.4,2.7),.65,.6,'oryx-ridge','head',lod)
  taper(d,'mandible-'+str(s),(s*.8,-.4,-.1),(s*.25,-.75,-2),.55,.55,'oryx-ridge','head',lod)
  for j in range([5,3,1][lod]):taper(d,f'crown-cavity-{s}-{j}',(s*(.5+j*.45),-.1,1.1),(s*(1+j*.5),-.15,1.7),.25,.2,'oryx-dark','head',lod)
 for j,(x,z) in enumerate([(0,.85),(-.4,.2),(.4,.2)]):d.box('three-eye-'+str(j),(x,-.83,z),(.23,.13,.23),'oryx-eye',joint='head')
 for i in range([9,5,3][lod]):d.box('jaw-tooth-'+str(i),((i/([9,5,3][lod]-1)-.5)*.7,-.76,-1.3),(.07,.1,.18),'oryx-ridge',joint='head')
 for s,n in [(-1,'L'),(1,'R')]:
  d.joint('thigh'+n,(s*1.55,.1,-.25),'pelvis');d.joint('shin'+n,(s*.2,.2,-4.1),'thigh'+n);d.joint('talon'+n,(0,-.1,-4.2),'shin'+n)
  limb(d,'thigh-'+n,(0,0,-.4),(s*.15,.1,-3.8),1.6,1.65,'oryx-chitin','oryx-dark','thigh'+n,lod)
  limb(d,'shin-'+n,(0,0,-.3),(0,-.1,-3.9),1.2,1.25,'oryx-chitin','oryx-dark','shin'+n,lod)
  shell(d,'knee-hub-'+n,(0,0,0),(.65,.65,.5),'oryx-dark','shin'+n,lod,segments=[16,10,6][lod],rings=[8,4,2][lod])
  for toe in [-1,0,1]:taper(d,f'foot-talon-{n}-{toe}',(toe*.45,-.2,-.1),(toe*.7,-2,-.5),.45,.4,'oryx-ridge','talon'+n,lod)
  d.joint('upperArm'+n,(s*3,.2,3.1),'thorax');d.joint('forearm'+n,(s*.8,0,-3.6),'upperArm'+n);d.joint('hand'+n,(0,-.1,-3.5),'forearm'+n);d.joint('claws'+n,(0,-.2,-.2),'hand'+n)
  limb(d,'upper-arm-'+n,(0,0,-.35),(s*.7,0,-3.3),1.4,1.3,'oryx-chitin','oryx-dark','upperArm'+n,lod)
  limb(d,'forearm-'+n,(0,0,-.3),(0,0,-3.2),1.2,1.4,'oryx-chitin','oryx-dark','forearm'+n,lod)
  shell(d,'elbow-hub-'+n,(0,0,0),(.58,.6,.5),'oryx-dark','forearm'+n,lod,segments=[16,10,6][lod],rings=[8,4,2][lod])
  shell(d,'hand-'+n,(0,-.1,-.1),(.8,.6,.7),'oryx-dark','hand'+n,lod)
  for finger in [-1,0,1]:
   beam(d,f'finger-{n}-{finger}',(finger*.45,-.25,-.2),(finger*.6,-.5,-1.2),.22,.25,'oryx-chitin','claws'+n)
   taper(d,f'claw-tip-{n}-{finger}',(finger*.6,-.5,-1.2),(finger*.45,-1.1,-1.6),.22,.22,'oryx-ridge','claws'+n,lod)
  # Authored membrane silhouette and independent articulated wing spars.
  d.joint('wing'+n,(s*2.1,1.25,3.8),'thorax')
  nx=[38,20,10][lod];nz=[20,10,5][lod]
  for i in range(nx):
   t=(i+.5)/nx;x=s*(.3+t*17);top=6.7*math.sin(math.pi*t*.85)+.7;bottom=-7.5*math.sin(math.pi*t)**.7+1.5*t
   for j in range(nz):
    if j<2 and (i+(1 if s>0 else 3))%7 in [2,3]:continue
    z=bottom+(j+.5)*(top-bottom)/nz;mat='oryx-membrane-dark' if d.rng.random()<.14 else 'oryx-membrane'
    d.box(f'torn-membrane-{n}-{i}-{j}',(x,.6+t*.6+.07*math.sin(i*.5+j*.35),z),(17/nx*.98,.16,(top-bottom)/nz*.98),mat,joint='wing'+n)
  for i,(x,z) in enumerate([(5,6.4),(10,6.6),(17.3,3.5),(15,-3.5),(10,-6.8),(5,-4)]):
   beam(d,f'wing-spar-{n}-{i}',(0,0,0),(s*x,.5,z),.24,.3,'oryx-dark','wing'+n)
   taper(d,f'wing-spur-{n}-{i}',(s*x,.5,z),(s*(x+.4),.5,z+1),.32,.3,'oryx-ridge','wing'+n,lod)
 d.joint('sword',(0,-.2,0),'handR');beam(d,'willbreaker-grip',(0,0,-.7),(0,0,.8),.36,.4,'oryx-dark','sword');beam(d,'willbreaker-guard',(-1,0,.8),(1,0,.8),.3,.45,'oryx-ridge','sword')
 for i in range([36,18,8][lod]):
  t=(i+.5)/[36,18,8][lod];w=(1.35-.8*t)*(1+.14*math.sin(i*2))
  d.box('willbreaker-blade-'+str(i),(t*.8,0,1+t*8),(w,.4,8/[36,18,8][lod]*1.08),'oryx-sword',joint='sword')
 d.joint('ritual',(0,-1,1),'thorax');motes(d,'taken-sparks','ritual','oryx-glow',4,lod)
 return d.result()

def arena(seed=42,quality='balanced',lod=0):
 check(lod);setup();d=Design('arena-threshold',seed,quality);floor(d,'threshold','oryx-stone','oryx-dark',52,64,lod)
 d.box('central-approach',(0,-17,.2),(12,22,.4),'oryx-chitin')
 for s in [-1,1]:
  for j in range(2):
   x=s*16;y=4+j*25;d.box(f'ritual-plate-{s}-{j}',(x,y,.35),(9,9,.7),'oryx-dark');d.ring(f'plate-rune-{s}-{j}',(x,y,.73),3.4,'oryx-glow',.09,[48,28,16][lod])
  for j in range(5):
   y=-5+j*14;h=20+j*3
   for k in range([15,8,4][lod]):
    u=k/[15,8,4][lod];d.box(f'ancient-rib-{s}-{j}-{k}',(s*(26-5*u*u),y,h*u),(3,4,h/[15,8,4][lod]*1.07),'oryx-chitin',(0,s*.18,0))
  for j in range(16):d.box(f'walkway-rail-{s}-{j}',(s*6,-24+j*2,.8),(.16,.16,1.6),'oryx-ridge')
 # A void-facing terminal opening and separate ruined fins, not an enclosed generic room.
 for j in range(7):taper(d,'terminal-fin-'+str(j),((j-3)*8,43,0),((j-3)*8,44,20+abs(j-3)*3),2,3,'oryx-dark',None,lod)
 return d.result()

def pose(animation,frame,fps=24):
 if animation not in ['idle','move','combat','signature','reveal']:raise ValueError('Unknown Oryx animation')
 if type(frame) is not int or frame<0 or type(fps) is not int or fps not in [24,30]:raise ValueError('Invalid animation time')
 t=frame/fps;s=math.sin(t*1.3);r={'thorax':(.015*s,0,.012*math.sin(t)),'head':(.03*math.sin(t*.7),0,.03*s),'wingL':(0,.035*s,0),'wingR':(0,-.035*s,0),'upperArmL':(-.12,0,-.18),'upperArmR':(-.1,0,.18),'ritual':(0,0,t*.23)};p={};scale={}
 if animation=='move':
  p['root']=(0,12+1.2*math.sin(t*1.3),.7+.4*math.sin(t*2));r.update(wingL=(0,.16*math.sin(t*2),0),wingR=(0,-.16*math.sin(t*2),0),thighL=(-.12,0,0),thighR=(-.12,0,0))
 if animation=='combat':
  u=math.sin(math.pi*min(t/1.25,1));r.update(upperArmR=(-.9*u,0,.2+.2*u),forearmR=(-.35*u,0,0),sword=(0,-.4*u,0),thorax=(0,0,-.18*u))
 if animation=='signature':
  u=math.sin(math.pi*min(t/1.4,1));r.update(upperArmL=(-.7*u,0,-.18-.5*u),upperArmR=(-.7*u,0,.18+.5*u),forearmL=(-.5*u,0,0),forearmR=(-.5*u,0,0),clawsL=(.6*u,0,0),clawsR=(.6*u,0,0),head=(.15*u,0,0),wingL=(0,.12*u,0),wingR=(0,-.12*u,0));scale['ritual']=(1+.7*u,)*3
 if animation=='reveal':
  u=min(t/2,1);u=u*u*(3-2*u);r.update(head=(.3*(1-u),0,0),wingL=(0,.3*(1-u),0),wingR=(0,-.3*(1-u),0),forearmL=(-.25*u,0,0),forearmR=(-.25*u,0,0))
 return dict(position=p,rotation=r,scale=scale,emissionPulse=1+.2*s+(.6*math.sin(math.pi*min(t/1.4,1)) if animation=='signature' else 0))
def camera(view,frame=0,fps=24):
 c=camera_for(view,25,39,frame,fps);c['sensorFit']='HORIZONTAL'
 if view in ['front','profile','three-quarter','silhouette']:c['lens']=48
 if view=='profile':c['sensorFit']='VERTICAL';c['lens']=42
 return c
