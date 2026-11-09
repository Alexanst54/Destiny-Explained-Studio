"""Venus / Ishtar: original procedural voxel interpretation, not a canonical map."""
from venus_vault.geometry import Design, QUALITY
import math


def generate(seed=42, quality='balanced'):
    d=Design('venus',seed,quality);r=d.rng
    d.box('foundation',(0,8,-1.5),(90,100,3),'basalt')
    # Block-cut plateau, overgrown Golden Age avenue; clear camera and walking corridor.
    for ix in range(-6,7):
        for iy in range(-3,10):
            x=ix*5;y=iy*5;z=r.choice([-.35,-.15,0,.15])
            d.box(f'terrain-{ix}-{iy}',(x,y,z-1),(5.15,5.15,2),'earth' if abs(x)>5 else 'basalt')
            if abs(x)>7 and r.random()<.65:
                d.box(f'moss-{ix}-{iy}',(x,y,z+.06),(r.uniform(2,4.8),r.uniform(2,4.8),.12),'moss')
    for i in range(15):
        d.box(f'paving-{i}',(0,-14+i*2.9,.12),(7.5,2.6,.22),'ishtar-dark')
        d.box(f'road-inlay-{i}',(-2,-14+i*2.9,.25),(.13,1.5,.025),'vex-edge')
    # Ishtar facade: asymmetrical shattered slabs, recessed windows and open portico.
    for side in [-1,1]:
        x=side*12
        d.box(f'academy-foot-{side}',(x,20,1),(12,15,2),'ishtar-dark')
        d.box(f'academy-shell-{side}',(x,22,6),(10,9,10),'ishtar')
        for floor in range(3):
            d.box(f'academy-floor-{side}-{floor}',(x,16.7,2.5+floor*3.1),(11,.8,.5),'ishtar-dark')
            for col in range(5):
                d.box(f'window-{side}-{floor}-{col}',(x-3.6+col*1.8,17.42,3.5+floor*3),(1.3,.12,1.8),'glass')
        for col in range(4):
            d.box(f'portico-{side}-{col}',(x-4.5+col*3,14,5),(.65,.9,8),'ishtar')
        d.box(f'cornice-{side}',(x,14.3,9.2),(12,2,.7),'ishtar')
        d.box(f'roof-break-{side}',(x+side*3,20,12.2),(5,9,2),'ishtar',rot=(0,side*.12,0))
    d.box('central-arch-lintel',(0,22,9),(14,3,2),'ishtar')
    # Golden Age relief, deliberately invented academy motif, no official emblem claim.
    for i in range(7):d.box(f'facade-relief-{i}',(-2.4+i*.8,20.42,9),(.35,.16,1.2 if i%2 else .7),'vex-edge')
    # Reclaimed academy: roof moss, hanging vines and shattered foreground wall fragments.
    for side in [-1,1]:
        for i in range(12):
            x=side*12+r.uniform(-4.5,4.5);y=r.uniform(17,25)
            d.box(f'roof-moss-{side}-{i}',(x,y,11.1),(r.uniform(.5,2),r.uniform(.5,2),.18),'moss')
            if i<8:
                length=r.uniform(1,4)
                for k in range(int(length*3)):
                    d.box(f'vine-{side}-{i}-{k}',(x+math.sin(k*.8)*.16,13.65,9-k*.3),(.25,.3,.42),'leaf' if k%2 else 'moss')
        for i in range(4):
            d.box(f'broken-wall-{side}-{i}',(side*(7+i*1.2),8-i*1.4,.5+i*.2),(1.3,1.4,1.3+i*.35),'ishtar',rot=(.15,side*.2,.2))
    # Vex structure partially buried in the jungle behind the academy.
    for side in [-1,1]:
        for i in range(3):d.pillar(f'vex-spire-{side}-{i}',side*(9+i*5),32+i*5,13+i*3,2.4,base=-3)
    for i in range(6):
        d.box(f'buried-vex-{i}',(-20+i*1.2,4+i*2,1.2),(3,3,3.2),'vex',rot=(.1,.25,.2))
        d.box(f'buried-light-{i}',(-20+i*1.2,2.4+i*2,1.8),(.1,.1,2),'cyan')
    # Layered cliffs and basalt boulders.
    for i in range(30):
        x=r.choice([-1,1])*r.uniform(22,37);y=r.uniform(-10,50);h=r.uniform(4,16)
        for tier in range(3):d.box(f'cliff-{i}-{tier}',(x,y,h*(.5-tier*.13)),(6-tier,7-tier,h*(1-tier*.22)),'rock')
    # Large branching trees and clustered voxel crowns frame the avenue.
    for i,(x,y,h) in enumerate([(-12,-7,13),(15,-3,15),(-22,17,18),(23,25,19),(-19,39,17),(11,39,16)]):
        d.box(f'tree-{i}/trunk',(x,y,h/2),(.9,1,h),'bark',rot=(0,.07*(-1)**i,0))
        for j in range(5):
            a=j*2.4;cx=x+math.cos(a)*3;cy=y+math.sin(a)*3;cz=h-j*.7
            d.box(f'tree-{i}/branch-{j}',((x+cx)/2,(y+cy)/2,cz-1),(3.2,.5,.5),'bark',rot=(0,0,a))
            for k in range(4):
                d.box(f'tree-{i}/crown-{j}-{k}',(cx+r.uniform(-2,2),cy+r.uniform(-2,2),cz+r.uniform(-.8,1)),(r.uniform(2,4.6),r.uniform(2,4.5),r.uniform(.5,1.5)),'leaf-light' if k==0 else 'leaf')
    # Ferns: five pairs of stepped voxel leaflets; avoid the avenue.
    for i in range(QUALITY[quality]['vegetation']):
        x=r.choice([-1,1])*r.uniform(5,25);y=r.uniform(-14,40);a=r.random()*math.tau
        for j in range(4):
            for side in [-1,1]:
                d.box(f'fern-{i}-{j}-{side}',(x+side*(j+1)*.14,y+j*.15,.35+j*.13),(.5-j*.06,.18,.12),'leaf-light' if j%2 else 'leaf',rot=(0,side*.2,a))
    # Dense understorey along the avenue: stepped broad leaves, shrubs and pale shoots.
    for i in range(QUALITY[quality]['vegetation']):
        x=r.choice([-1,1])*r.uniform(4.8,20);y=r.uniform(-14,26);h=r.uniform(.7,1.8)
        for j in range(5):
            a=j*math.tau/5+i*.7
            for tier in range(3):
                reach=(tier+1)*.34
                d.box(f'understorey-{i}-{j}-{tier}',(x+math.cos(a)*reach,y+math.sin(a)*reach,h-tier*.24),(.7-tier*.1,.35,.18),'leaf-light' if tier==2 else 'leaf',rot=(0,.18,a))
        d.box(f'understorey-shoot-{i}',(x,y,h*.7),(.1,.12,h*1.3),'moss')
    return d.result()
