"""Atheon v0.9.1: tall three-bladed crown, chevron chest, narrow radiolarian waist.
Authored voxel interpretation from visual observation, never game model/texture data.
"""
from venus_vault.geometry import Design
from cinematic_vex.shapes import armour,beam,cable,joint_hub,lance
import math

THIGH=4.2
SHIN=4.1
GROUND=1.25


def generate(seed=42,quality='balanced',lod=0):
    if type(lod) is not int or lod not in [0,1,2]:raise ValueError('LOD must be 0, 1 or 2')
    d=Design('boss-atheon',seed,quality)
    d.joint('root',(0,9,GROUND));d.joint('pelvis',(0,0,8.5),'root')
    d.joint('torso',(0,0,1.1),'pelvis');d.joint('head',(0,-.2,4.3),'torso')
    d.box('pelvic-chassis',(0,.15,0),(2.65,1.65,.85),'mechanism',joint='pelvis')
    for s in [-1,1]:
        armour(d,f'hip-yoke-{s}',(s*.7,0,.4),(s*1.75,0,-.65),1.2,1.2,'pelvis',lod,'alloy-dark')
        lance(d,f'hip-swept-fin-{s}',(s*1.5,.2,-.2),(s*2.5,.6,1.25),.65,.5,lod,joint='pelvis')
    # Exposed vessel in a narrow mechanical waist. No toy-like ribcage block.
    d.box('radiolaria-vessel',(0,-.5,.22),(1.0,.8,1.9),'radiolaria',joint='torso')
    for i in range([14,8,4][lod]):
        z=-.8+i*2.05/([14,8,4][lod]-1)
        d.ring(f'abdomen-lamella-{i}',(0,0,z),1.05,'mechanism',.08,[24,16,8][lod],joint='torso',gap=5)
    for s in [-1,1]:
        beam(d,f'waist-strut-{s}',(s*.95,-.25,-.7),(s*1.3,-.25,1.25),.16,.3,'alloy-dark','torso')
        cable(d,f'waist-radiolar-tube-{s}',[(s*.75,.5,-.7),(s*1.05,.7,.1),(s*.7,.65,1.6)],'torso',lod,'circuit',.12)
    d.box('spinal-core',(0,.7,2),(.8,.9,4.2),'mechanism',joint='torso')
    # Sweeping chest chevrons and upward/outward shoulder spurs are the primary landmarks.
    for s in [-1,1]:
        armour(d,f'chest-frame-{s}',(s*.2,-.8,1.25),(s*3,-.4,3.75),1.5,1.2,'torso',lod,'alloy-dark')
        for row in range([5,3,1][lod]):
            o=row*.34
            lance(d,f'chevron-{s}-{row}',(s*(2.9+o*.38),-.95-o*.05,3.85-o*.3),(s*.12,-1.22-o*.02,1.2-o*.22),.85,.26,lod,'alloy','torso')
        lance(d,f'shoulder-crown-{s}',(s*2.3,.05,3.35),(s*5.35,.5,5.3),1.45,.65,lod,'alloy','torso')
        lance(d,f'shoulder-rear-blade-{s}',(s*2.5,.8,2.9),(s*4.7,1.5,4.7),.95,.5,lod,'alloy-dark','torso')
        d.ring(f'pectoral-sensor-{s}',(s*2.25,-1.15,3.2),.23,'circuit',.055,[20,12,8][lod],'xz','torso')
        if lod<2:
            for i in range([10,5,0][lod]):
                z=1+i*.28
                beam(d,f'scapula-rail-{s}-{i}',(s*.8,.95,z),(s*(2.2+z*.2),.95,z+.6),.1,.22,'alloy-dark','torso')
    # The old rectangular head and rabbit horns are replaced with a pointed orbital mask.
    d.box('cranial-recess',(0,0,.1),(1.35,1.2,1.25),'mechanism',joint='head')
    for s in [-1,1]:
        lance(d,f'face-cheek-{s}',(s*1.0,-.55,.6),(s*.12,-1.18,-1.3),.65,.4,lod,'alloy','head')
        lance(d,f'orbital-brow-{s}',(0,-1.0,.6),(s*1.3,-.6,1.0),.28,.3,lod,'alloy-dark','head')
        lance(d,f'crown-side-blade-{s}',(s*.7,.1,.5),(s*2.3,.25,3.45),.8,.45,lod,'alloy','head')
        if lod<2:lance(d,f'crown-back-spur-{s}',(s*.5,.8,.6),(s*1.5,1.3,2.35),.5,.4,lod,'alloy-dark','head')
    lance(d,'crown-central-spire',(0,.4,.7),(0,.8,4.05),.7,.65,lod,'alloy','head')
    d.ring('orbital-eye-socket',(0,-1.08,.2),.35,'alloy-dark',.16,[24,16,8][lod],'xz','head')
    d.ring('orbital-eye-corona',(0,-1.22,.2),.24,'circuit',.075,[24,16,8][lod],'xz','head')
    d.box('single-eye',(0,-1.27,.2),(.23,.08,.23),'optic',joint='head')
    for i in range([8,4,2][lod]):
        x=(i/([8,4,2][lod]-1)-.5)*1.3
        cable(d,f'neck-cable-{i}',[(x,.6,-1),(x,.8,-.45),(x,.65,.1)],'head',lod,'mechanism',.1)
    # Long limbs, exposed bearings, layered shin armour and claw-like feet.
    for s,n in [(-1,'L'),(1,'R')]:
        hip='hip'+n;knee='knee'+n;foot='foot'+n
        d.joint(hip,(s*1.45,0,-.3),'pelvis');d.joint(knee,(0,0,-THIGH),hip);d.joint(foot,(0,0,-SHIN),knee)
        joint_hub(d,'hip-bearing-'+n,(0,0,0),.68,hip,lod)
        armour(d,'thigh-'+n,(0,0,-.55),(0,.1,-3.6),1.35,1.45,hip,lod,'alloy-dark')
        lance(d,'thigh-outer-fin-'+n,(s*.45,0,-1.1),(s*.75,.4,-3.3),.65,.45,lod,'alloy',hip)
        joint_hub(d,'knee-bearing-'+n,(0,0,0),.55,knee,lod)
        armour(d,'shin-'+n,(0,0,-.55),(0,0,-3.7),1.0,1.2,knee,lod)
        lance(d,'shin-front-keel-'+n,(0,-.7,-.45),(0,-.92,-3.75),1.25,.45,lod,'alloy',knee)
        for side in [-1,1]:
            beam(d,f'shin-piston-{n}-{side}',(side*.5,.45,-.4),(side*.5,.45,-3.4),.14,.14,'piston',knee)
            cable(d,f'shin-trace-{n}-{side}',[(side*.3,-.7,-.4),(side*.3,-.7,-1.8),(side*.15,-.7,-3.5)],knee,lod,'circuit',.045)
        d.box('ankle-'+n,(0,0,.16),(.7,.7,.65),'mechanism',joint=foot)
        # Sole z=-.2 is the analytic contact reference used by the IK solver.
        d.box('foot-'+n,(0,-.22,-.1),(1.4,1.5,.2),'mechanism',joint=foot)
        for toe in [-1,0,1]:
            armour(d,f'claw-{n}-{toe}',(toe*.42,-.45,.05),(toe*.8,-1.7,0),.35,.38,foot,lod)
        shoulder='shoulder-upper'+n;elbow='elbow-upper'+n;hand='hand-upper'+n
        d.joint(shoulder,(s*3.25,.15,3.05),'torso');d.joint(elbow,(s*.35,0,-2.6),shoulder);d.joint(hand,(0,0,-2.7),elbow)
        joint_hub(d,'shoulder-bearing-'+n,(0,0,0),.8,shoulder,lod)
        armour(d,'biceps-'+n,(0,0,-.6),(s*.35,0,-2.2),.85,1.0,shoulder,lod,'alloy-dark')
        joint_hub(d,'elbow-bearing-'+n,(0,0,0),.5,elbow,lod)
        armour(d,'forearm-'+n,(0,0,-.5),(0,0,-2.4),1.2,1.15,elbow,lod,'alloy-dark')
        lance(d,'forearm-fin-'+n,(s*.4,.1,-1),(s*.8,.35,-2.8),.75,.4,lod,'alloy',elbow)
        beam(d,'arm-piston-'+n,(0,.65,-.15),(0,.65,-2.5),.18,.18,'piston',elbow)
        d.box('palm-'+n,(0,0,-.15),(1.1,.65,.8),'mechanism',joint=hand)
        for finger in [-1,0,1]:
            cable(d,f'claw-finger-{n}-{finger}',[(finger*.37,-.1,-.3),(finger*.5,-.25,-1),(finger*.38,-.6,-1.25)],hand,lod,'alloy',.16)
    # Asymmetry: large Torch Hammer left of screen, energy manipulator on the other hand.
    d.joint('weapon',(0,0,0),'hand-upperR')
    hand='weapon'
    armour(d,'torch-cannon',(0,-.1,-.1),(0,-4.4,-.1),1.1,1.1,hand,lod,'mechanism')
    for k in range([16,8,3][lod]):
        y=-.3-k*3.9/([16,8,3][lod]-1)
        d.ring(f'torch-cooling-ring-{k}',(0,y,-.1),.64,'alloy-dark',.09,[16,12,8][lod],'xz',hand)
    d.ring('torch-muzzle',(0,-4.55,-.1),.5,'circuit',.12,[24,16,8][lod],'xz',hand)
    d.box('torch-core',(0,-4.6,-.1),(.45,.05,.45),'optic',joint=hand)
    d.joint('energy',(0,-1,-.9),'hand-upperL')
    for k in range(4):d.ring(f'temporal-energy-{k}',(0,0,0),.65+k*.25,'temporal',.035,[48,24,12][lod],'xy' if k%2 else 'xz','energy',gap=7)
    d.box('temporal-core',(0,0,0),(.3,.3,.3),'optic',joint='energy')
    for i in range([72,32,12][lod]):
        a=i*2.399963;z=((i*17)%71/71-.5)*3;r=math.sqrt(max(.05,2.8-z*z))
        d.box(f'temporal-mote-{i}',(r*math.cos(a),r*math.sin(a),z),(.035,.035,.035),'temporal',joint='energy')
    if lod==0:
        # Discrete damaged edges and mineral inclusions without modifying major contours.
        for i in range(80):
            x=d.rng.choice([-1,1])*d.rng.uniform(1.4,2.9);z=d.rng.uniform(1.7,3.5)
            d.box(f'breastplate-scar-{i}',(x,-1.28,z),(.04+d.rng.random()*.08,.025,.025),'patina',joint='torso')
    spec=d.result();spec['lod']=lod;spec['anatomy']={'thighLength':THIGH,'shinLength':SHIN,'soleOffset':.2,'ground':GROUND}
    return spec
