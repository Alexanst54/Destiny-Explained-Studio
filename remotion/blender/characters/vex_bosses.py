"""Original, articulated voxel bosses. No proprietary mesh or texture data.
Joint naming follows animation/rig.ts where topology overlaps; Hydra topology is new.
"""
import math
from venus_vault.geometry import Design


def generate_v090(boss_id='boss-atheon', seed=42, quality='balanced'):
    if boss_id not in ['boss-atheon','boss-templar']:raise ValueError('Unknown Vex boss')
    d=Design(boss_id,seed,quality)
    d.joint('root',(0,9,1.35))
    if boss_id=='boss-atheon':
        d.joint('pelvis',(0,0,4.5),'root');d.joint('torso',(0,0,1.1),'pelvis')
        d.joint('head',(0,0,3.1),'torso')
        # Massive silver chassis, broad shoulders, exposed bronze joints and radiolaria core.
        d.box('pelvic-chassis',(0,0,0),(2.4,1.6,1.05),'silver-dark',joint='pelvis')
        for s in [-1,1]:
            d.box(f'hip-plate-{s}',(s*1.35,0,.1),(.7,2,1.5),'silver',rot=(0,s*.15,0),joint='pelvis')
            d.box(f'torso-side-{s}',(s*1.35,0,1.3),(.7,1.7,2.7),'silver',rot=(0,s*-.13,0),joint='torso')
            for j in range(5):
                d.box(f'chest-rib-{s}-{j}',(s*.9,-.95,.4+j*.45),(.9,.4,.18),'silver',rot=(0,s*.2,0),joint='torso')
            d.box(f'collar-{s}',(s*1.1,-.1,2.4),(1.9,1.8,.6),'silver',rot=(0,s*-.22,0),joint='torso')
        d.box('back-carapace',(0,.9,1.3),(2.5,.65,2.7),'silver-dark',joint='torso')
        d.box('spine',(0,.45,1.2),(.9,1.1,2.9),'bronze',joint='torso')
        d.box('radiolaria-vessel',(0,-.65,1.1),(1.15,.75,1.9),'core',joint='torso')
        d.box('head-cranium',(0,0,0),(1.55,1.3,1.3),'silver',joint='head')
        d.box('face-mask',(0,-.8,-.12),(1.7,.5,.8),'silver-dark',joint='head')
        d.box('single-eye',(0,-1.08,.05),(.48,.09,.25),'eye',joint='head')
        # Tall branching angular horns, backward blades and faceted shoulder mantle.
        for s in [-1,1]:
            for j in range(4):
                d.box(f'horn-{s}-{j}',(s*(.95+j*.22),.05+j*.08,.65+j*.57),(.45-j*.065,.65-j*.07,.85),'silver',rot=(0,s*.2,0),joint='head')
            d.box(f'head-fin-{s}',(s*.85,.7,.1),(.35,1.7,1.8),'silver',rot=(.25,0,0),joint='head')
        for side,name in [(-1,'L'),(1,'R')]:
            hip='hip'+name;knee='knee'+name;foot='foot'+name;shoulder='shoulder-upper'+name;elbow='elbow-upper'+name;hand='hand-upper'+name
            d.joint(hip,(side*.9,0,-.4),'pelvis');d.joint(knee,(0,.15,-2),hip);d.joint(foot,(0,-.1,-1.65),knee)
            d.box('thigh-'+name,(0,0,-.9),(.85,1.15,1.7),'silver-dark',joint=hip)
            d.box('thigh-armor-'+name,(side*.18,-.35,-.7),(1.1,.75,1.3),'silver',rot=(0,side*.08,0),joint=hip)
            d.box('knee-'+name,(0,-.35,0),(1.05,.8,.7),'bronze',joint=knee)
            d.box('shin-'+name,(0,0,-.8),(.65,.75,1.5),'silver-dark',joint=knee)
            d.box('shin-face-'+name,(0,-.44,-.7),(.75,.2,1.3),'silver',joint=knee)
            d.box('shin-glow-'+name,(0,-.56,-.7),(.12,.04,1.15),'cyan',joint=knee)
            d.box('foot-'+name,(0,-.4,-.22),(1.05,1.9,.45),'silver',joint=foot)
            d.joint(shoulder,(side*2.05,0,2.1),'torso');d.joint(elbow,(0,0,-1.7),shoulder);d.joint(hand,(0,-.05,-1.6),elbow)
            d.box('shoulder-armor-'+name,(side*.1,0,0),(1.6,2,1.4),'silver',rot=(0,side*.2,0),joint=shoulder)
            for i in range(3):d.box(f'mantle-{name}-{i}',(side*(.5+i*.26),.45,.5+i*.35),(.4,1.5,.7),'silver',joint=shoulder)
            d.box('upper-arm-'+name,(0,0,-1.05),(.65,.8,1.6),'bronze',joint=shoulder)
            d.box('forearm-'+name,(0,0,-.75),(.95,1,1.4),'silver-dark',joint=elbow)
            d.box('forearm-blade-'+name,(side*.5,0,-.4),(.28,1.1,1.8),'silver',joint=elbow)
            d.box('hand-'+name,(0,-.1,-.25),(1,.8,.65),'silver',joint=hand)
            for j in range(3):d.box(f'finger-{name}-{j}',(-.3+j*.3,-.4,-.7),(.18,.3,.8),'bronze',joint=hand)
        # Asymmetric temporal emitter in left hand; weapon silhouette on right forearm.
        d.box('torch-cannon',(0,-.7,-.35),(.75,1.7,.8),'silver',joint='hand-upperR')
        d.box('torch-muzzle',(0,-1.58,-.35),(.45,.12,.45),'eye',joint='hand-upperR')
        d.joint('energy',(0,-.4,-1.3),'hand-upperL')
        for k in range(3):d.ring('temporal-energy-'+str(k),(0,0,0),.65+k*.3,'cyan',.07,24,'xy' if k%2 else 'xz',joint='energy',gap=5)
        d.box('temporal-core',(0,0,0),(.45,.45,.45),'core',joint='energy')
    else:
        # Hydra floats as one axial chassis; rotating three-panel energy shield is separate.
        d.joint('pelvis',(0,0,4.5),'root');d.joint('head',(0,-1.25,0),'pelvis');d.joint('halo',(0,0,0),'pelvis')
        for layer in range(5):
            d.box(f'central-shell-{layer}',(0,.1,layer*.55-.8),(3.5-layer*.35,2.4-layer*.1,.5),'vex-edge' if layer%2 else 'vex-dark',joint='pelvis')
        d.box('eye-recess',(0,-.2,0),(2.3,.7,1.4),'vex-dark',joint='head')
        d.box('great-eye',(0,-.6,0),(1.15,.15,.85),'eye',joint='head')
        d.box('eye-pupil',(0,-.7,0),(.48,.08,.48),'core',joint='head')
        for s in [-1,1]:
            for i in range(5):
                x=s*(1.7+i*.47);z=.7-i*.3
                d.box(f'wing-{s}-{i}',(x,.3,z),(.7,3.1-i*.23,1.9-i*.22),'vex',rot=(0,s*.28,0),joint='pelvis')
                d.box(f'wing-seam-{s}-{i}',(x,-1.3+i*.1,z),(.12,.06,1.2),'cyan',joint='pelvis')
            d.box(f'heavy-cannon-{s}',(s*2,-1.25,-1.25),(.9,2.6,.8),'vex-dark',joint='pelvis')
            d.box(f'cannon-mouth-{s}',(s*2,-2.58,-1.25),(.6,.1,.5),'eye',joint='pelvis')
            d.box(f'ventral-prong-{s}',(s*.75,.2,-2.1),(.5,1.3,2.4),'vex',rot=(0,s*-.17,0),joint='pelvis')
        d.box('dorsal-crown',(0,1.1,2),(1.3,1.6,2.2),'vex-edge',joint='pelvis')
        d.ring('suspension-ring',(0,0,-1.7),2.7,'cyan',.08,32,joint='pelvis')
        # Segmented rotating wire shield, not a solid opaque cylinder hiding the model.
        for panel in range(3):
            a=math.tau*panel/3
            for k in range(9):
                angle=a+(k-4)*.095;x=4.4*math.sin(angle);y=-4.4*math.cos(angle)
                for z in [-2.2,2.2]:d.box(f'shield-edge-{panel}-{k}-{z}',(x,y,z),(.44,.07,.09),'shield',rot=(0,0,-angle),joint='halo')
                if k in [0,4,8]:d.box(f'shield-bar-{panel}-{k}',(x,y,0),(.06,.07,4.4),'shield',joint='halo')
    return d.result()


def pose_v090(boss_id, animation='idle', frame=0, fps=30):
    """Random-access pose; never accumulates deltas, so resume and out-of-order frames agree."""
    allowed={'boss-atheon':['idle','walk','combat','temporal'], 'boss-templar':['idle','rotate','move','attack']}
    if boss_id not in allowed or animation not in allowed[boss_id]:raise ValueError('Unsupported boss animation')
    if type(frame) is not int or frame<0 or fps not in [24,30]:raise ValueError('Invalid animation time')
    t=frame/fps;s=math.sin(t*math.tau);rot={};positions={}
    if boss_id=='boss-atheon':
        rot['torso']=(.025*math.sin(t*2),0,.025*math.sin(t));rot['head']=(0,0,.06*math.sin(t*1.3))
        if animation=='walk':
            y=9-min(t,4)*1.1
            # Smooth follow of the set's stepped dais; not foot IK or collision simulation.
            support=.31
            for step in range(1,8):
                u=max(0,min(1,(y+.25-(3.5+step*.75)+.15)/.3))
                support+=.13*u*u*(3-2*u)
            positions['root']=(0,y,support+.13+abs(s)*.08)
            for side,name in [(-1,'L'),(1,'R')]:
                rot['hip'+name]=(s*side*.23,0,0);rot['knee'+name]=(max(0,-s*side)*.35,0,0)
                rot['foot'+name]=(-max(0,-s*side)*.13,0,0)
                rot['shoulder-upper'+name]=(-s*side*.17,0,side*.09)
        if animation in ['combat','temporal']:
            k=.5-.5*math.cos(min(t/1.2,1)*math.pi)
            rot['shoulder-upperL']=(-k*.95,0,-.3*k);rot['elbow-upperL']=(-k*.65,0,0)
            rot['shoulder-upperR']=(-.45,0,.2);rot['elbow-upperR']=(-.5,0,0)
            rot['torso']=(.04,0,.09*math.sin(t*1.3))
        rot['energy']=(t*.7,t*.4,t*1.3)
    else:
        positions['pelvis']=(0,0,4.5+math.sin(t*2)*.18);rot['halo']=(0,0,t*.7)
        rot['pelvis']=(0,.035*math.sin(t),t*.25 if animation=='rotate' else .07*math.sin(t))
        if animation=='move':positions['root']=(math.sin(t*.7)*2,9+math.sin(t)*1.3,1.35)
        if animation=='attack':rot['pelvis']=(.08*max(0,s),0,.12*math.sin(t*2))
    return dict(rotation=rot,position=positions,emissionPulse=1+.15*math.sin(t*4))


def generate(boss_id='boss-atheon', seed=42, quality='balanced', lod=0):
    from cinematic_vex import atheon,templar
    if boss_id not in ['boss-atheon','boss-templar']:raise ValueError('Unknown Vex boss')
    return (atheon if boss_id=='boss-atheon' else templar).generate(seed,quality,lod)


def pose(boss_id, animation='idle', frame=0, fps=30):
    from cinematic_vex.animation import evaluate
    return evaluate(boss_id,animation,frame,fps)
