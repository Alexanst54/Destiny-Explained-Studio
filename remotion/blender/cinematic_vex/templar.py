"""Tapered floating Hydra: crescent carapace, central eye, articulated ventral tiers."""
from venus_vault.geometry import Design
from cinematic_vex.shapes import armour,beam,joint_hub,lance
import math


def generate(seed=42,quality='balanced',lod=0):
    if type(lod) is not int or lod not in [0,1,2]:raise ValueError('LOD must be 0, 1 or 2')
    d=Design('boss-templar',seed,quality);d.joint('root',(0,9,1.35));d.joint('pelvis',(0,0,6.8),'root')
    d.joint('head',(0,-1.3,.5),'pelvis');d.joint('halo',(0,0,0),'pelvis')
    d.box('hydra-spine',(0,.6,-1.8),(1.15,1.3,7.5),'mechanism',joint='pelvis')
    armour(d,'thorax-carapace',(0,.5,1.7),(0,.7,-1.5),3.0,2.4,'pelvis',lod,'vex-patina')
    for side,n in [(-1,'L'),(1,'R')]:
        d.joint('carapace'+n,(0,0,0),'pelvis')
        j='carapace'+n
        # Tall sweeping crescents wrap a narrow central body, unlike a humanoid chest.
        count=[22,12,5][lod]
        for i in range(count):
            u=i/(count-1);a=.08+u*1.8;x=side*(1.0+2.6*math.sin(a));z=.0+3.9*math.cos(a)
            width=(.22+math.sin(math.pi*u)*.9)
            d.box(f'crescent-{n}-{i}',(x,.1,z),(width,2.0*(1-u*.55),.35),'vex-polished',rot=(0,side*(a+.15),0),joint=j)
            if lod<2:d.box(f'crescent-inner-{n}-{i}',(x-side*.18,-.95+u*.5,z),(.14,.12,.23),'mechanism',joint=j)
        lance(d,'crest-tip-'+n,(side*2.1,.1,2.7),(side*1.9,.6,5.2),.55,.9,lod,'vex-polished',j)
        armour(d,'lateral-wing-'+n,(side*1.4,.6,.1),(side*5,.5,-.3),1.4,1.8,j,lod,'vex-patina')
        beam(d,'outrigger-'+n,(side*1.2,.7,1.8),(side*5.6,.7,1.4),.35,.35,'mechanism',j)
        joint_hub(d,'outrigger-hub-'+n,(side*5.25,.7,1.45),.48,j,lod)
        lance(d,'wing-terminal-'+n,(side*3.8,.4,.0),(side*5.7,-.1,-.7),.7,.7,lod,'vex-polished',j)
    # Pointed face around an imposing circular optical assembly.
    for s in [-1,1]:
        lance(d,f'face-mask-{s}',(s*1.7,-.45,1.2),(0,-1.1,-1.5),.85,.6,lod,'vex-polished','head')
        lance(d,f'brow-swept-{s}',(0,-.55,1.0),(s*1.7,-.4,1.9),.5,.6,lod,'vex-polished','head')
    d.ring('great-eye-socket',(0,-1.12,.05),.78,'mechanism',.24,[40,24,12][lod],'xz','head')
    d.ring('great-eye-iris',(0,-1.3,.05),.56,'circuit',.13,[40,24,12][lod],'xz','head')
    d.box('great-eye',(0,-1.39,.05),(.58,.08,.58),'optic',joint='head')
    for tier in range(3):
        joint='ventral'+str(tier);z=-1.7-tier*1.4;d.joint(joint,(0,0,z),'pelvis');scale=1-tier*.22
        for side,n in [(-1,'L'),(1,'R')]:
            lance(d,f'ventral-shell-{tier}-{n}',(side*2.1*scale,0,.45),(0,-1.0,-.7),.8*scale,.8,lod,'vex-polished',joint)
            lance(d,f'ventral-claw-{tier}-{n}',(side*1.65*scale,0,.35),(side*2.4*scale,-.2,-.4),.35,.5,lod,'vex-patina',joint)
        d.box(f'ventral-core-{tier}',(0,-.6,-.15),(.22,.15,.42),'circuit',joint=joint)
    lance(d,'ventral-stinger',(0,0,-4.9),(0,0,-6.5),.35,.4,lod,'vex-patina','pelvis')
    for side in [-1,1]:
        d.joint('cannon'+str(side),(side*3.1,-.45,-1.4),'pelvis')
        armour(d,'cannon-'+str(side),(0,0,0),(0,-2.1,-.3),.8,.9,'cannon'+str(side),lod,'mechanism')
        d.ring('muzzle-'+str(side),(0,-2.2,-.3),.37,'circuit',.1,[24,16,8][lod],'xz','cannon'+str(side))
        d.joint('blast'+str(side),(0,-2.5,-.3),'cannon'+str(side))
        lance(d,'attack-spark-'+str(side),(0,0,0),(0,-1.8,0),.18,.18,lod,'temporal','blast'+str(side))
    # Layered segmented energy panels: nested angular cells, not three rectangular cages.
    for panel in range(3):
        a0=panel*math.tau/3
        for row in range([7,4,2][lod]):
            z=-3+row*6/max(1,[7,4,2][lod]-1)
            for col in range([12,8,4][lod]):
                a=a0-.42+col*.84/max(1,[12,8,4][lod]-1);x=6.4*math.sin(a);y=-6.4*math.cos(a)
                d.box(f'shield-cell-{panel}-{row}-{col}',(x,y,z),(.3,.035,.05),'shield-trace',rot=(0,0,-a),joint='halo')
                if lod<2 and (row+col)%2==0:d.box(f'shield-dash-{panel}-{row}-{col}',(x,y,z+.18),(.025,.035,.18),'circuit',joint='halo')
        for z in [-3.3,3.3]:
            for k in range([28,16,8][lod]):
                a=a0-.48+k*.96/([28,16,8][lod]-1)
                d.box(f'shield-rim-{panel}-{z}-{k}',(6.4*math.sin(a),-6.4*math.cos(a),z),(.23,.06,.07),'circuit',rot=(0,0,-a),joint='halo')
    spec=d.result();spec['lod']=lod;return spec
