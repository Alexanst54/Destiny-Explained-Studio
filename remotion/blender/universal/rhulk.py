"""Dedicated Lubrean anatomy, six-eyed elongated mask, long legs and a bladed glaive."""
import math
from venus_vault.geometry import Design,PALETTE
from .raid_shapes import check,taper,shell,limb,beam,motes,floor,camera_for,wear
SUPPORTED_ENTITIES=('boss-rhulk','vow-of-disciple')
SUPPORTED_VIEWS=('front','profile','three-quarter','cinematic','environment','silhouette','reveal','close-up')
LABEL='Rhulk'
MATERIALS={'rhulk-skin':('#9a3d31',.58,.08,0),'rhulk-muscle':('#552c29',.68,.1,0),'rhulk-armor':('#20272c',.42,.65,0),'rhulk-edge':('#5c6765',.43,.65,0),'rhulk-gold':('#a18348',.36,.7,0),'rhulk-eye':('#fff1bb',.22,.1,3),'rhulk-resonance':('#efb35a',.32,.2,2.2),'rhulk-stone':('#302e2c',.82,.25,0)}
EMISSION_MATERIALS=('rhulk-eye','rhulk-resonance')
SCENE_STYLE=dict(studioGround=True,worldColor='#43332d',worldStrength=.2,hazeFactor=.1,hazeColor='#d3aa77',fogPosition=(0,22,16),fogScale=(85,100,40),lights=[('Pyramid key',(-15,-15,27),(0,12,9),16000,'#eed9b1',10),('Red fill',(17,1,18),(0,12,10),5000,'#c25e48',10),('Resonance rim',(0,29,25),(0,12,10),18000,'#ffe1a7',8)])
def setup():PALETTE.update(MATERIALS)
def decorate_material(mat,name):wear(mat,name)

def generate(seed=42,quality='balanced',lod=0):
 check(lod);setup();d=Design('boss-rhulk',seed,quality)
 d.joint('root',(0,12,.25));d.joint('hips',(0,0,9.4),'root');d.joint('abdomen',(0,0,1.1),'hips');d.joint('chest',(0,0,1.45),'abdomen');d.joint('neck',(0,0,1.8),'chest');d.joint('mask',(0,-.05,1.25),'neck')
 shell(d,'narrow-pelvis',(0,0,-.1),(1.2,.8,1.2),'rhulk-skin','hips',lod)
 shell(d,'long-abdomen',(0,.04,.3),(.86,.64,1.7),'rhulk-skin','abdomen',lod)
 shell(d,'ribbed-chest',(0,0,.7),(1.65,.9,1.55),'rhulk-armor','chest',lod)
 for i in range([22,11,5][lod]):
  z=-.35+i*2.6/[22,11,5][lod];w=.55+.9*math.sin((i/[22,11,5][lod])*.9*math.pi)
  for s in [-1,1]:beam(d,f'pectoral-seam-{s}-{i}',(s*.04,-.94,z),(s*w,-.7,z+.22),.055,.08,'rhulk-edge','chest')
 for j in range([16,8,4][lod]):
  z=-.7+j*.19;beam(d,'abdominal-striation-'+str(j),(-.65,-.61,z),(.65,-.61,z+.08),.055,.05,'rhulk-muscle','abdomen')
 # Sculptural crescent collar and smooth high mask, not a horned Hive/Vex head.
 for s in [-1,1]:
  for i in range([24,12,6][lod]):
   t=(i+.5)/[24,12,6][lod];x=s*(.6+t*2.5);z=1.55+.6*math.sin(t*math.pi)
   d.box(f'flared-collar-{s}-{i}',(x,.35,z),(.25,1.45-.7*t,.16+.2*t),'rhulk-armor',(0,-s*.12,0),'chest')
  taper(d,'collar-tip-'+str(s),(s*2.6,.2,1.8),(s*3.1,.2,2.4),.7,.45,'rhulk-edge','chest',lod)
 limb(d,'long-neck',(0,0,0),(0,0,1.3),.6,.6,'rhulk-muscle','rhulk-armor','neck',lod)
 shell(d,'elongated-helmet',(0,.05,.6),(.54,.58,1.5),'rhulk-armor','mask',lod)
 for i in range(3):
  for s in [-1,1]:d.box(f'six-eye-{s}-{i}',(s*.18,-.56,.42+i*.26),(.09,.08,.085),'rhulk-eye',joint='mask')
 beam(d,'face-central-spine',(0,-.61,-.55),(0,-.61,1.9),.08,.08,'rhulk-muscle','mask')
 for s,n in [(-1,'L'),(1,'R')]:
  d.joint('femur'+n,(s*.78,0,-.55),'hips');d.joint('tibia'+n,(s*.13,.18,-4.3),'femur'+n);d.joint('ankle'+n,(0,-.18,-4.35),'tibia'+n);d.joint('toe'+n,(0,-.25,-.15),'ankle'+n)
  limb(d,'long-femur-'+n,(0,0,-.3),(s*.1,.15,-4.0),.95,1,'rhulk-skin','rhulk-muscle','femur'+n,lod)
  limb(d,'long-tibia-'+n,(0,0,-.2),(0,-.18,-4.05),.62,.82,'rhulk-skin','rhulk-muscle','tibia'+n,lod)
  shell(d,'knee-tendon-'+n,(0,0,0),(.45,.48,.45),'rhulk-muscle','tibia'+n,lod,segments=[16,10,6][lod],rings=[8,4,2][lod])
  for j in range([12,6,3][lod]):d.ring(f'ankle-cuff-{n}-{j}',(0,0,-.2+j*.065),.44,'rhulk-armor',.06,[24,12,8][lod],joint='ankle'+n)
  for j in range(3):
   for k in range(2):d.box(f'cuff-gold-node-{n}-{j}-{k}',((j-1)*.2,-.46,.1+k*.2),(.13,.09,.13),'rhulk-gold',joint='ankle'+n)
  for toe in [-1,0,1]:taper(d,f'long-toe-{n}-{toe}',(toe*.2,-.1,0),(toe*.32,-1.25,-.08),.26,.25,'rhulk-armor','toe'+n,lod)
  d.joint('humerus'+n,(s*1.65,.05,1.15),'chest');d.joint('ulna'+n,(s*.12,0,-2.35),'humerus'+n);d.joint('wrist'+n,(0,0,-2.55),'ulna'+n)
  limb(d,'upper-arm-'+n,(0,0,-.2),(s*.1,0,-2.2),.68,.72,'rhulk-skin','rhulk-muscle','humerus'+n,lod)
  limb(d,'forearm-'+n,(0,0,-.2),(0,0,-2.45),.64,.7,'rhulk-armor','rhulk-muscle','ulna'+n,lod)
  shell(d,'elbow-tendon-'+n,(0,0,0),(.33,.35,.4),'rhulk-muscle','ulna'+n,lod,segments=[16,10,6][lod],rings=[8,4,2][lod])
  shell(d,'hand-'+n,(0,-.05,-.2),(.42,.28,.45),'rhulk-armor','wrist'+n,lod)
  for finger in range(4):beam(d,f'finger-{n}-{finger}',((finger-1.5)*.16,-.08,-.35),((finger-1.5)*.19,-.23,-.9),.1,.13,'rhulk-armor','wrist'+n)
 d.joint('glaive',(.35,-.2,0),'wristR');beam(d,'lubrae-shaft',(0,0,-5.3),(0,0,5.5),.22,.27,'rhulk-armor','glaive')
 for j in range([36,18,8][lod]):
  z=-4.8+j*9.7/[36,18,8][lod];d.box('shaft-gold-binding-'+str(j),(0,0,z),(.29,.31,.055),'rhulk-gold',joint='glaive')
 taper(d,'lubrae-blade',(0,0,4.2),(1.65,0,7.2),1.2,.4,'rhulk-edge','glaive',lod)
 taper(d,'lubrae-dark-spine',(-.1,.15,4.4),(.9,.15,6.7),.6,.4,'rhulk-armor','glaive',lod)
 taper(d,'lubrae-crossblade',(0,0,4.5),(-1.2,0,5.7),.8,.35,'rhulk-gold','glaive',lod)
 shell(d,'glaive-counterweight',(0,0,-5.3),(.38,.36,.5),'rhulk-gold','glaive',lod)
 d.joint('resonance',(0,0,-8.5),'hips');motes(d,'resonant-motes','resonance','rhulk-resonance',3,lod)
 for j in range(3):d.ring('resonance-wave-'+str(j),(0,0,j*.24),1.3+j*.35,'rhulk-resonance',.045,[48,24,12][lod],joint='resonance')
 return d.result()

def arena(seed=42,quality='balanced',lod=0):
 check(lod);setup();d=Design('vow-of-disciple',seed,quality);floor(d,'dominion','rhulk-stone','rhulk-armor',46,58,lod)
 for s in [-1,1]:
  for j in range(5):
   y=2+j*10;h=16+j*2
   d.box(f'obsidian-wall-{s}-{j}',(s*23,y,h/2),(4,8,h),'rhulk-armor')
   for k in range([12,6,3][lod]):d.box(f'gold-strata-{s}-{j}-{k}',(s*20.9,y,h*(k+1)/[12,6,3][lod]),(.12,7,.12),'rhulk-gold')
  for j in range(8):d.box(f'resonance-floor-line-{s}-{j}',(s*(4+j*1.8),16,.13),(.06,54,.04),'rhulk-gold')
  for j in range(3):
   d.box(f'trophy-pedestal-{s}-{j}',(s*16,2+j*13,1.8),(3.6,3.6,3.6),'rhulk-armor');shell(d,f'reliquary-{s}-{j}',(s*16,2+j*13,4.2),(1,1,1.2),'rhulk-gold',None,lod)
 for j in range(5):d.box('terminal-step-'+str(j),(0,33+j*2,j*.45),(30,3,1),'rhulk-armor')
 for j in range(7):
  x=(j-3)*2.4;h=22-abs(j-3)*1.5;d.box('upended-fin-'+str(j),(x,41,h/2),(1.2,4,h),'rhulk-armor');d.box('upended-channel-'+str(j),(x,38.9,h/2),(.18,.12,h*.85),'rhulk-resonance')
 d.box('resonance-aperture',(0,38.8,17),(7,.14,7),'rhulk-gold',(0,math.pi/4,0))
 return d.result()

def pose(animation,frame,fps=24):
 if animation not in ['idle','move','combat','signature','reveal']:raise ValueError('Unknown Rhulk animation')
 if type(frame) is not int or frame<0 or type(fps) is not int or fps not in [24,30]:raise ValueError('Invalid animation time')
 t=frame/fps;breath=math.sin(t*1.4);r={'chest':(.012*breath,0,.018*math.sin(t)),'mask':(.025*math.sin(t*.8),0,.035*math.sin(t*.7)),'humerusL':(.07,0,-.13),'humerusR':(-.07,0,.13),'resonance':(0,0,t*.25)};p={};scale={}
 if animation=='move':
  stride=math.sin(t*4.5);p['root']=(0,12+3*math.sin(t*2),.25+.12*abs(stride));r.update(femurL=(-.35*stride,0,0),femurR=(.35*stride,0,0),tibiaL=(.3*max(0,stride),0,0),tibiaR=(.3*max(0,-stride),0,0),humerusL=(.2*stride,0,0),humerusR=(-.2*stride,0,0),chest=(-.08,0,0))
 if animation=='combat':
  u=min(t/1.3,1);lift=math.sin(math.pi*u);extension=math.sin(math.pi*min(u*1.6,1))
  r.update(femurL=(-1.25*lift,0,-.08*lift),tibiaL=(.65*extension,0,0),ankleL=(-.18*lift,0,0),chest=(-.15*lift,0,.2*lift),humerusL=(-.3*lift,0,-.25),ulnaR=(-.3*lift,0,0),glaive=(.25*lift,0,-.2*lift));p['root']=(.3*lift,12,.25)
 if animation=='signature':
  u=math.sin(math.pi*min(t/1.4,1));r.update(humerusL=(-1.1*u,0,-.2),humerusR=(-.8*u,0,.2),ulnaL=(-.4*u,0,0),mask=(-.12*u,0,0),glaive=(0,.3*u,0));p['root']=(0,12,.25+.5*u);scale['resonance']=(1+2*u,1+2*u,1+.5*u)
 if animation=='reveal':
  u=min(t/2,1);u=u*u*(3-2*u);r.update(mask=(.2*(1-u),0,0),humerusL=(.25*(1-u),0,-.13),humerusR=(.25*(1-u),0,.13),ulnaL=(-.35*(1-u),0,0),ulnaR=(-.35*(1-u),0,0))
 return dict(position=p,rotation=r,scale=scale,emissionPulse=1+.16*breath+(.9*math.sin(math.pi*min(t/1.4,1)) if animation=='signature' else 0))
def camera(view,frame=0,fps=24):return camera_for(view,17,8,frame,fps)
