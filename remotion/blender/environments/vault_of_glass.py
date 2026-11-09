"""Independent Templar's Well and Glass Throne sets; original voxel staging."""
from venus_vault.geometry import Design
import math


def generate_v090(seed=42, quality='balanced', arena='arena-templars-well'):
    if arena not in ['arena-templars-well','arena-glass-throne']:raise ValueError('Unknown Vault arena')
    d=Design(arena,seed,quality);r=d.rng;throne=arena=='arena-glass-throne'
    d.box('abyss',(0,10,-4),(100,100,2),'basalt')
    # Raised main combat deck, broken into stepped strata.
    for i in range(4):d.box(f'arena-stratum-{i}',(0,5,-1.5+i*.35),(33-i*1.2,39-i*1.3,.7),'vex-dark' if i%2 else 'bronze')
    for ix in range(-5,6):
        for iy in range(-4,8):
            d.box(f'floor-tile-{ix}-{iy}',(ix*2.65,iy*2.65,.02),(2.57,2.57,.22),'vex' if (ix+iy)%4 else 'vex-dark')
            if ix%3==0:d.box(f'floor-circuit-{ix}-{iy}',(ix*2.65+.7,iy*2.65,.145),(.04,2.5,.028),'cyan')
    for side in [-1,1]:
        for i in range(4):
            x=side*(14.5+(.9*i if not throne else 0));y=-5+i*9;h=16+i*2
            d.pillar(f'colonnade-{side}-{i}',x,y,h,2)
            for rib in range(3):d.box(f'buttress-{side}-{i}-{rib}',(x+side*(2+rib*.9),y,3+rib*3),(2,3,7+rib*3),'vex-dark')
            if i<3:d.box(f'high-link-{side}-{i}',(x,y+4.5,h-1),(1.7,9,.7),'vex-edge')
    # Background cyclopean vault and dark recess; no artificial roof over the camera.
    d.box('back-wall',(0,33,14),(47,3,34),'vex-dark')
    for i in range(11):
        h=15+(i%3)*2
        d.box(f'wall-rib-{i}',(-22+i*4.4,30.9,h/2),(1.5,1.1,h),'bronze')
        d.box(f'wall-inlay-{i}',(-22+i*4.4,30.25,h*.55),(.09,.08,h*.7),'cyan')
    for j in range(7):
        d.box(f'vault-crown-{j}',(0,29,20+j*1.6),(34-j*3,3,.7),'vex-edge')
    # Three layered stairways, clear approach lane and a luminous circular dais.
    for step in range(8):d.box(f'dais-step-{step}',(0,8+step*.5,.18+step*.13),(11-step*.3,9-step*.5,.26),'vex-edge' if step%3==0 else 'vex-dark')
    d.ring('dais-circuit',(0,9,1.27),4.5,'cyan',.06,48)
    # Deterministic fragments behind the main deck.
    for i in range(25):
        x=r.choice([-1,1])*r.uniform(18,30);y=r.uniform(0,32);z=r.uniform(-2,3)
        d.box(f'fallen-block-{i}',(x,y,z),(r.uniform(2,4),r.uniform(2,5),r.uniform(1,4)),'bronze',rot=(.12,.2,r.random()))
    if throne:
        # Two separate temporal gates, bronze stepped surrounds, cyan and amber timelines.
        for side in [-1,1]:
            x=side*9;y=15;z=5.2;mat='portal' if side<0 else 'portal-amber'
            for ring,rad in enumerate([3,3.5,3.9]):
                d.ring(f'portal-frame-{side}-{ring}',(x,y,z),rad,'vex-edge' if ring!=1 else mat,.3 if ring!=1 else .14,32,'xz')
            # Widely spaced luminous lattice leaves the scene visible, avoids opaque white discs.
            for k in range(-5,6):
                height=2*math.sqrt(max(0,2.8**2-(k*.48)**2))
                d.box(f'portal-field-{side}-{k}',(x+k*.48,y+.05,z),(.065,.08,max(.1,height)),mat)
            for foot in [-1,1]:d.box(f'portal-plinth-{side}-{foot}',(x+foot*3,y,1.3),(1.6,2,2.6),'vex-dark')
        d.ring('time-halo',(0,28,12),6.5,'cyan',.12,64,'xz',gap=6)
        d.ring('time-halo-inner',(0,28,12),5.8,'vex-edge',.18,48,'xz')
    else:
        for i,(x,y) in enumerate([(-8,3),(8,3),(0,18)]):
            d.box(f'conflux-{i}/base',(x,y,.5),(2,2,1),'vex-edge')
            for level in range(5):
                d.box(f'conflux-{i}/column-{level}',(x,y,1.3+level*.48),(.65-level*.07,.65-level*.07,.32),'core')
            d.ring(f'conflux-{i}/ring',(x,y,2.1),1,'cyan',.08,20)
        for i,(x,y,z) in enumerate([(-10,9,6),(10,9,6),(-6,18,8),(6,18,8),(0,24,10)]):
            d.box(f'oracle-{i}',(x,y,z),(.7,.7,.7),'oracle',rot=(.5,.4,.6))
            d.ring(f'oracle-halo-{i}',(x,y,z),1,'oracle',.04,16,'xz')
    return d.result()


def generate(seed=42, quality='balanced', arena='arena-templars-well', lod=0):
    if type(lod) is not int or lod not in [0,1,2]:raise ValueError('LOD must be 0, 1 or 2')
    if arena=='arena-glass-throne':
        from cinematic_vex.throne import generate as throne
        return throne(seed,quality,lod)
    return generate_v090(seed,quality,arena)
