"""Reusable architectural studies. No claim of reproducing a named Destiny arena."""
import math
from venus_vault.geometry import Design,PALETTE
from .registry import families

def palette():
    return {f['id']+'-'+str(i):(col,.34 if i==0 else .8,.55 if i==0 else .1,3 if i==2 else 0) for f in families() for i,col in enumerate(f['colors'])}

def generate(family_id,seed=42,quality='balanced',lod=0,variant='sanctum'):
    fs={x['id']:x for x in families()}
    if family_id not in fs or type(lod) is not int or lod not in [0,1,2]:raise ValueError('Unknown family or LOD')
    f=fs[family_id]
    if variant not in f['variants']:raise ValueError('Unknown family variant')
    PALETTE.update(palette());d=Design('family-'+family_id,seed,quality);body,shade,glow=[family_id+'-'+str(i) for i in range(3)]
    detail=[9,5,2][lod];style=f['architecture']
    def box(n,p,s,m=body,r=(0,0,0)):d.box(n,p,s,m,r)
    # Reusable terrace and paving module with deterministic local wear/misalignment.
    box('foundation',(0,12,-1),(48,60,2),shade)
    for x in range(-5,6):
        for y in range(-2,10):
            z=d.rng.uniform(-.04,.04);box(f'paving-{x}-{y}',(x*4,y*4,z),(3.9,3.9,.22),body if d.rng.random()>.2 else shade)
    box('dais',(0,19,.55),(16,14,1),shade)
    for side in [-1,1]:
        for index in range(5):
            x=side*(13+index*.3);y=2+index*9;h=13+index*2
            if style in ['ribbed','surreal']:
                for j in range(detail):
                    z=h*j/detail;inward=(j/detail)**2*4
                    box(f'rib-{side}-{index}-{j}',(x-side*inward,y,z),(2.2,2.4,h/detail*1.12),body,(0,side*.18,0))
                    if lod<2:box(f'rib-trace-{side}-{index}-{j}',(x-side*inward,y-1.24,z),(.18,.12,.6),glow)
            elif style=='fractured':
                for j in range(detail):box(f'fracture-{side}-{index}-{j}',(x+d.rng.uniform(-1,1),y,h*j/detail),(3,3,h/detail*.75),body,(0,side*.22,.15*j))
            elif style=='abstract':
                box(f'blade-{side}-{index}',(x,y,h/2),(1,6,h),body,(0,side*.12,0));d.ring(f'orbit-{side}-{index}',(x,y,h*.7),3,glow,.10,detail*4,'xz')
            else:
                box(f'column-{side}-{index}',(x,y,h/2),(3.2,4,h),shade)
                for j in range(detail):
                    z=(j+.5)*h/detail;depth=.45 if style in ['laboratory','city'] else .9
                    box(f'cladding-{side}-{index}-{j}',(x,y-2,z),(3.6,depth,h/detail*.83),body)
                    box(f'channel-{side}-{index}-{j}',(x-side*1.55,y-2.5,z),(.12,.1,h/detail*.7),glow)
            if style=='fortified':box(f'capital-{side}-{index}',(x,y,h),(6,6,2),body)
            if style=='industrial':
                for j in range(3):box(f'pipe-{side}-{index}-{j}',(x+side*(2+j*.4),y,h*.4),(.25,.25,h*.8),glow if j==0 else body)
            if style=='monolith':box(f'blade-top-{side}-{index}',(x,y,h+2),(2,2,6),body,(0,side*.3,0))
    # Distinctive focal props and facade module, shared dimensions keep camera predictable.
    if f['effect'] in ['gate','rift','sphere']:
        for j in range(3):d.ring('portal-'+str(j),(0,30,8),6+j*.55,glow if j==0 else body,.2+j*.1,detail*6,'xz',gap=5 if style=='fractured' else 0)
        if style=='abstract':
            for j in range(detail):box('floating-core-'+str(j),(0,29,8),(4-j*.16,4-j*.16,.35),body,(0,0,j*.21))
    elif f['effect'] in ['altar','roots']:
        for s in [-1,1]:
            for j in range(detail):box(f'fang-{s}-{j}',(s*(6-j*.25),28,3+j*.9),(1.5,3,4),body,(0,-s*.2,0))
        d.ring('rune',(0,27,9),4,glow,.2,detail*5,'xz');box('altar',(0,23,2),(8,5,3),shade)
    elif f['effect']=='resonance':
        for j in range(5):box('resonance-'+str(j),((j-2)*2.5,29,6+abs(j-2)*2),(1.5,3,12+abs(j-2)*4),body,(0,(j-2)*.1,0))
        for j in range(detail):d.ring('resonance-wave-'+str(j),(0,27,7),2+j*.4,glow,.07,16,'xz')
    elif f['effect']=='neon':
        for j in range(4):box('skybridge-'+str(j),(0,28+j*3,10+j*3),(30,2,1),body);box('neon-'+str(j),(0,26+j*3,10+j*3),(29,.1,.12),glow)
    elif f['effect']=='reactor':
        for j in range(5):box('reactor-'+str(j),(0,28,2+j*2),(6,6,1.3),body);box('reactor-light-'+str(j),(0,24.9,2+j*2),(4,.1,.8),glow)
    elif f['effect']=='banner':
        for s in [-1,1]:box('banner-'+str(s),(s*6,28,8),(3,.4,12),glow)
        box('command-seat',(0,28,3),(10,6,5),body)
    else:
        for j in range(5):box('conduit-'+str(j),((j-2)*2,27,5),(1,4,10),glow if j%2 else body)
    if variant=='causeway':
        for s in [-1,1]:box('bridge-rail-'+str(s),(s*5,3,1.2),(.4,28,2),body)
    if variant=='courtyard':
        for j in range(4):box('terrace-'+str(j),(0,34+j*4,-j*.5),(40,4,1),shade)
    return d.result()
