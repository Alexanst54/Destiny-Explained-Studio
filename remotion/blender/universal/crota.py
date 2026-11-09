"""Dedicated original Crota study: jagged ossified crown, exposed ribs and hooked cleaver.
Visual sources are documented separately; no image texture or game model is loaded.
"""
import math
from venus_vault.geometry import Design,PALETTE
from cinematic_vex.shapes import beam,lance
MATERIALS={'crota-bone':('#88a17b',.68,.12,0),'crota-edge':('#c0d2a5',.47,.15,0),'crota-shell':('#38483b',.82,.06,0),'crota-recess':('#142d29',.8,.05,0),'crota-soul':('#68e8b6',.28,.1,1.8),'crota-eye':('#d2ffe2',.2,.05,5),'crota-sword':('#84d99e',.38,.22,.35),'crota-stone':('#424b42',.92,0,0),'crota-rune':('#8ee8a5',.4,.1,2)}

def setup():PALETTE.update(MATERIALS)

def generate(seed=42,quality='balanced',lod=0):
    if type(lod) is not int or lod not in [0,1,2]:raise ValueError('Invalid LOD')
    setup();d=Design('boss-crota',seed,quality);steps=[14,7,3][lod]
    d.joint('root',(0,10,.22));d.joint('hips',(0,0,5.6),'root');d.joint('ribcage',(0,0,1.2),'hips');d.joint('skull',(0,-.1,3.4),'ribcage')
    def spike(n,a,b,w,j,mat='crota-bone'):lance(d,n,a,b,w,w*.5,lod,mat,j)
    def bone(n,a,b,w,depth,j):
        beam(d,n+'/dark-bone',a,b,w*.45,depth*.5,'crota-recess',j)
        sectors=[10,6,4][lod]
        for i in range(steps):
            t=(i+.5)/steps;bulge=.52+.48*math.sin(t*math.pi);p=[a[k]+(b[k]-a[k])*t for k in range(3)]
            for q in range(sectors):
                angle=math.tau*q/sectors;irregular=1+.08*math.sin(i*2+q*3)
                x=p[0]+math.cos(angle)*w*.37*bulge;y=p[1]+math.sin(angle)*depth*.36
                d.box(f'{n}/ossicle-{i}-{q}',(x,y,p[2]),(w*.4*bulge,depth*.32,math.dist(a,b)/steps*1.06),'crota-bone' if (i+q)%5 else 'crota-shell',(0,math.cos(angle)*.09,angle*.12),j)
                if lod==0 and q%3==0:d.box(f'{n}/edge-{i}-{q}',(x,y-.08,p[2]),(.07,.08,.12),'crota-edge',joint=j)
    d.box('pelvic-bone',(0,0,0),(1.8,1.5,.7),'crota-shell',joint='hips')
    for s in [-1,1]:
        spike('hip-hook-'+str(s),(s*.9,-.3,.3),(s*1.8,-.6,-1.7),.7,'hips');spike('hip-ridge-'+str(s),(s*1,.6,.2),(s*2,.9,1.4),.5,'hips')
    beam(d,'exposed-spine',(0,.55,-.6),(0,.65,3.7),.75,.65,'crota-shell','ribcage')
    for j in range([8,5,3][lod]):
        z=.1+j*.4
        d.box('spine-light-'+str(j),(0,.97,z),(.32,.13,.2),'crota-soul',joint='ribcage')
        for s in [-1,1]:
            # Open curved rib arcs, rather than a filled rectangular torso.
            points=[(s*.25,.5,z),(s*(1.65+.1*j),.1,z+.3),(s*(1.5+.1*j),-.7,z+.55),(s*.4,-1,z+.75)]
            for k in range(3):beam(d,f'rib-{j}-{s}-{k}',points[k],points[k+1],.18,.28,'crota-edge','ribcage')
    for i in range(steps):
        z=.4+i*2.5/steps;w=.35+.2*math.sin(i*.8)
        d.box('soul-vessel-'+str(i),(0,.1,z),(w,.38,.14),'crota-soul',joint='ribcage')
    for s in [-1,1]:
        spike('pectoral-blade-'+str(s),(s*.35,-.8,2.6),(s*2.4,-.5,3.25),.9,'ribcage');spike('chest-fang-'+str(s),(s*1,-.9,2.7),(s*.7,-1.2,1.4),.75,'ribcage')
        for layer in range([8,4,2][lod]):
            t=layer/[8,4,2][lod];width=2.5*math.sin((t*.7+.2)*math.pi)
            d.box(f'pauldron-{s}-{layer}',(s*2.45,-.15,2.8+t*1.4),(width,1.7-.6*t,.25),'crota-shell' if layer%4==0 else 'crota-bone',(0,s*.12,0),'ribcage')
        # Numerous irregular organic crown spines, not Atheon's three planar blades.
        for j in range([6,4,2][lod]):
            x=s*(1.6+j*.3);z=3.3+math.sin(j*.8)*.25
            spike(f'shoulder-thorn-{s}-{j}',(x,.15+j*.12,z),(x+s*(.6+j*.12),.3+j*.18,z+.7+(j%3)*.28),.65,'ribcage')
            spike(f'back-thorn-{s}-{j}',(s*(.5+j*.2),.7,2.5+j*.15),(s*(1+j*.35),2,4.3+j*.15),.45,'ribcage','crota-shell')
    # Tapered skull, jaw, cheek cavities and three clustered eyes.
    for j in range(steps):
        t=j/(steps-1);w=1.35*(.65+.35*math.sin(t*math.pi));d.box('cranial-layer-'+str(j),(0,.06,-.65+t*1.55),(w,1.05,.15),'crota-bone',joint='skull')
    for s in [-1,1]:
        spike('cheek-'+str(s),(s*.67,-.5,.45),(s*.28,-.75,-.9),.45,'skull','crota-shell')
        spike('skull-crown-'+str(s),(s*.45,.1,.6),(s*1.05,.2,1.8),.6,'skull')
        spike('brow-'+str(s),(s*.08,-.62,.5),(s*.8,-.5,.85),.3,'skull','crota-edge')
    spike('skull-central-thorn',(0,.35,.8),(0,.5,2.1),.65,'skull');d.box('mouth-cavity',(0,-.6,-.47),(.55,.18,.28),'crota-recess',joint='skull')
    for i,x in enumerate([-.32,0,.32]):d.box('three-eyes-'+str(i),(x,-.61,.23+(.13 if i==1 else 0)),(.18,.1,.16),'crota-eye',joint='skull')
    for i in range(5):d.box('jaw-tooth-'+str(i),((i-2)*.11,-.72,-.45),(.06,.09,.18),'crota-edge',joint='skull')
    for s,n in [(-1,'L'),(1,'R')]:
        d.joint('thigh'+n,(s*1.05,0,0),'hips');d.joint('shin'+n,(s*.35,.1,-2.75),'thigh'+n);d.joint('foot'+n,(0,-.1,-2.75),'shin'+n)
        bone('thigh-'+n,(0,0,-.3),(s*.3,.1,-2.3),1.35,1.1,'thigh'+n);d.ring('knee-'+n,(0,-.15,0),.55,'crota-shell',.18,[24,14,8][lod],'xz','shin'+n)
        bone('shin-'+n,(0,0,-.35),(0,-.1,-2.5),1,1,'shin'+n)
        for j in range([5,3,1][lod]):spike(f'calf-thorn-{n}-{j}',(s*.4,.4,-.3-j*.4),(s*.9,.75,.2-j*.4),.4,'shin'+n)
        d.box('sole-'+n,(0,-.45,-.1),(1.35,1.9,.2),'crota-recess',joint='foot'+n)
        for toe in [-1,0,1]:spike(f'toe-{n}-{toe}',(toe*.38,-.2,.1),(toe*.5,-1.65,-.1),.45,'foot'+n)
        d.joint('upperArm'+n,(s*2.6,0,2.9),'ribcage');d.joint('forearm'+n,(s*.55,-.15,-2.3),'upperArm'+n);d.joint('hand'+n,(0,-.2,-2.3),'forearm'+n)
        bone('upperarm-'+n,(0,0,-.3),(s*.5,-.15,-2.1),1.05,1,'upperArm'+n);bone('forearm-'+n,(0,0,-.2),(0,-.2,-2.2),1.25,1.05,'forearm'+n)
        for j in range([6,3,1][lod]):spike(f'gauntlet-thorn-{n}-{j}',(s*.35,.1,-.4-j*.25),(s*1.2,.4,.3-j*.23),.65,'forearm'+n)
        d.box('palm-'+n,(0,-.1,-.05),(.9,.7,.8),'crota-shell',joint='hand'+n)
        for i in range(4):
            x=(i-1.5)*.22;beam(d,f'finger-{n}-{i}',(x,-.25,-.25),(x,-.55,-.9),.15,.18,'crota-edge','hand'+n)
    d.joint('cleaver',(0,-.5,0),'handL')
    beam(d,'sword-hilt',(0,0,-1),(0,0,1),.32,.38,'crota-shell','cleaver');beam(d,'sword-crossguard',(-1.1,0,.8),(1.1,0,.8),.3,.45,'crota-edge','cleaver')
    # Broad asymmetrical hooked bone cleaver, multiple recessed channels.
    for j in range([40,20,8][lod]):
        t=(j+.5)/[40,20,8][lod];z=1+t*8.4;x=-t*3.2-(max(0,t-.8)*6);w=1.15+.65*t
        d.box('cleaver-blade-'+str(j),(x,0,z),(w,.4,8.4/[40,20,8][lod]*1.1),'crota-sword',(0,-.35,0),'cleaver')
        if lod<2:d.box('blade-cavity-'+str(j),(x-.06,-.22,z),(.35,.08,.13),'crota-shell',(0,-.35,0),'cleaver')
    spike('cleaver-hook',(-3.6,0,8.7),(-5.3,0,10.5),1.35,'cleaver','crota-edge')
    d.joint('soulAura',(0,0,3),'ribcage')
    for i in range([70,28,8][lod]):
        a=d.rng.uniform(0,math.tau);rad=d.rng.uniform(1,4);z=d.rng.uniform(-3,4);s=d.rng.uniform(.03,.09)
        d.box('soul-mote-'+str(i),(math.cos(a)*rad,math.sin(a)*1.3,z),(s,s,s*3),'crota-soul',joint='soulAura')
    for obj in d.objects:
        if obj['material']=='circuit':obj['material']='crota-soul'
    return d.result()

def arena(seed=42,quality='balanced',lod=0):
    setup();d=Design('oversoul-throne',seed,quality);steps=[24,12,6][lod]
    d.box('throne-foundation',(0,16,-2),(70,82,4),'crota-recess')
    for x in range(-8,9):
        for y in range(-3,12):
            d.box(f'ancient-paving-{x}-{y}',(x*3.8,y*3.8,.05),(3.73,3.73,.1),'crota-stone' if d.rng.random()>.2 else 'crota-shell')
    for s in [-1,1]:
        for j in range(5):
            y=-1+j*12
            for k in range(steps):
                t=k/steps;z=t*32;x=s*(28-8*t*t)
                d.box(f'vault-rib-{s}-{j}-{k}',(x,y,z),(3,5,32/steps*1.1),'crota-stone',(0,s*.22,0))
                if lod==0:d.box(f'rib-cut-{s}-{j}-{k}',(x-s*1.5,y-2.6,z),(.13,.12,.5),'crota-rune')
        for j in range(6):d.box(f'balcony-{s}-{j}',(s*19,15+j*4,4+j*.6),(10,4,1),'crota-shell')
        for j in range(12):d.box(f'rail-{s}-{j}',(s*10,-5+j*3,.7),(.17,.17,1.4),'crota-bone')
    # Oversoul: a huge suspended green celestial volume behind the combat floor.
    for j in range(steps):
        t=-1+(j+.5)*2/steps;radius=10.5*math.sqrt(1-t*t)
        d.ring('oversoul-latitude-'+str(j),(0,48,24+t*10.5),radius,'crota-soul',.5,[72,40,20][lod],plane='xy')
    d.ring('oversoul-occult-ring',(0,49,24),13,'crota-recess',.8,[96,48,24][lod],'xz')
    for j in range(3):
        d.box('rear-stair-'+str(j),(0,36+j*3,.5+j*.5),(28,4,1),'crota-shell')
    return d.result()

def pose(animation,frame,fps=24):
    if animation not in ['idle','move','attack','reveal']:raise ValueError('Unsupported Crota animation')
    if type(frame) is not int or frame<0 or fps not in [24,30]:raise ValueError('Invalid time')
    t=frame/fps;rot={'ribcage':(.018*math.sin(t*1.4),0,.015*math.sin(t*.8)),'skull':(0,.04*math.sin(t*.7),.03*math.sin(t*.9)),'upperArmL':(-.16,0,-.22),'forearmL':(-.1,-.1,-.15),'upperArmR':(.05,0,.13),'soulAura':(0,0,t*.2)};pos={};scale={}
    if animation=='move':pos['root']=(math.sin(t*.6)*1.5,10+t*.4,.3+.12*math.sin(t*2));rot['thighL']=(.13*math.sin(t*2),0,0);rot['thighR']=(-.13*math.sin(t*2),0,0)
    if animation=='attack':
        u=(1-math.cos(min(t/1.4,1)*math.pi))*.5;rot['ribcage']=(0,0,-.4*u);rot['upperArmL']=(-.8*u,-.7*u,-.22-.5*u);rot['forearmL']=(-.4*u,-.1,-.15);rot['cleaver']=(0,.35*u,.2*u)
    if animation=='reveal':
        u=min(t/2,1);u=u*u*(3-2*u);rot['skull']=(.28*(1-u),0,0);rot['ribcage']=(.1*(1-u),0,-.12*(1-u));scale['soulAura']=(.6+u*.4,)*3
    return dict(rotation=rot,position=pos,scale=scale,emissionPulse=1+.18*math.sin(t*2.1))
