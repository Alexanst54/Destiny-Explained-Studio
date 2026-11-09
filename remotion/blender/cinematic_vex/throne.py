"""Glass Throne v0.9.1: deep mineral chasm, layered Vex megastructure and temporal gates."""
from venus_vault.geometry import Design
from cinematic_vex.shapes import beam,lance
import math


def ground_height(x,y):
    """Authored flat walking deck, not an inferred collision mesh."""
    if abs(x)<=12 and -11<=y<=25:return 1.25
    raise ValueError('Point is outside the supported combat deck')


def generate(seed=42,quality='balanced',lod=0):
    if type(lod) is not int or lod not in [0,1,2]:raise ValueError('LOD must be 0, 1 or 2')
    d=Design('arena-glass-throne',seed,quality);r=d.rng
    d.box('chasm-bottom',(0,34,-22),(150,180,4),'mineral')
    d.box('combat-deck',(0,7,.6),(24,36,1.3),'mineral')
    d.box('deck-sublayer',(0,7,-.4),(26,38,.7),'alloy-dark')
    for side in [-1,1]:
        for i in range(7):
            y=-8+i*5
            beam(d,f'deck-cantilever-{side}-{i}',(side*11,y,-.4),(side*19,y,-12),1.7,2.1,'mineral-edge')
        d.box('outer-terrace-'+str(side),(side*22,32,-1),(16,90,2),'mineral')
        d.box('portal-bridge-'+str(side),(side*13,20,.5),(15,8,1.5),'alloy-dark')
        for k in range(14):
            x=side*(8+k*.7)
            d.box(f'bridge-paving-{side}-{k}',(x,20,1.29),(.58,7,.08),'vex-patina')
            for edge in [-1,1]:
                if k%2==0:d.box(f'handrail-post-{side}-{k}-{edge}',(x,20+edge*3.6,1.8),(.12,.12,1.1),'alloy-dark')
        for row in range(4):
            x=side*(26+row*1.5);y=3+row*22;height=43+row*10
            d.box(f'colossus-{side}-{row}/core',(x,y,height/2-3),(4.5,6,height),'mineral')
            for layer in range(4):
                offset=side*(1.8+layer*.6)
                d.box(f'colossus-{side}-{row}/lamina-{layer}',(x+offset,y-.8,height*.48),(1.1,6.8,height*.83),'vex-patina' if layer%2 else 'alloy-dark')
            beam(d,f'colossus-{side}-{row}/flying-buttress',(x,y,height*.65),(x-side*7,y,height*.9),2,4,'mineral-edge')
            for level in range([18,9,4][lod]):
                z=1+level*(height-3)/[18,9,4][lod]
                d.box(f'colossus-{side}-{row}/circuit-{level}',(x-side*2.3,y-3.05,z),(.15,.08,1.1),'circuit')
                d.box(f'colossus-{side}-{row}/step-{level}',(x,y-3.15,z),(4.8,.7,.22),'vex-patina')
                if lod==0:
                    for column in range(5):d.box(f'colossus-{side}-{row}/glyph-{level}-{column}',(x-1.6+column*.8,y-3.53,z+.35),(.28,.06,.12 if (level+column)%3 else .48),'alloy-dark')
            if row<3:
                d.box(f'catwalk-{side}-{row}',(x,y+11,15+row*8),(6,23,1.1),'mineral-edge')
                for edge in [-1,1]:d.box(f'catwalk-rail-{side}-{row}-{edge}',(x+edge*2.8,y+11,16.4+row*8),(.15,23,.16),'vex-patina')
    # Nested angular vaults and hanging crystalline blades provide depth without a flat back wall.
    for layer in range(4):
        y=46+layer*15;height=38+layer*9
        for side in [-1,1]:
            beam(d,f'folded-vault-{layer}-{side}',(side*28,y,5),(side*10,y,height),3.4,5,'mineral-edge')
            beam(d,f'folded-cap-{layer}-{side}',(side*10,y,height),(0,y,height+7),2,4,'vex-patina')
        for i in range(9):
            x=(i-4)*5;top=height+3+r.uniform(-2,4)
            lance(d,f'hanging-blade-{layer}-{i}',(x,y,top),(x*.7,y-3,top-r.uniform(11,20)),2.2,2.8,lod,'alloy-dark')
    # Non-checkerboard fractured floor plates, inset channels and circuit knots.
    for ix in range(-4,5):
        for iy in range(-3,9):
            x=ix*2.6;y=iy*3
            d.box(f'plate-{ix}-{iy}',(x,y,1.265),(2.5,2.9,.03),'vex-patina' if (ix+iy)%5==0 else 'mineral-edge')
            if lod<2:
                d.box(f'plate-inset-{ix}-{iy}',(x+.7,y,1.29),(.04,2.5,.025),'alloy-dark')
                if (ix+iy)%3==0:d.box(f'plate-trace-{ix}-{iy}',(x-.5,y,1.29),(.035,1.8,.025),'circuit')
            if lod==0:
                for n in range(4):
                    d.box(f'plate-engraving-{ix}-{iy}-{n}',(x-.9+n*.45,y+.9,1.29),(.18,.07,.014),'alloy-dark')
    # Broad entrance stairs remain away from the IK walking corridor.
    for step in range(8):d.box(f'entrance-step-{step}',(0,-15+step*.55,-.65+step*.25),(17,4,.5),'mineral-edge')
    for side in [-1,1]:
        x=side*17;y=23;z=9;colour='portal' if side<0 else 'portal-amber'
        d.box(f'gate-foundation-{side}',(x,y,.25),(13,10,2),'mineral-edge')
        for layer in range(5):
            radius=5.4+layer*.48
            d.ring(f'temporal-gate-{side}/ring-{layer}',(x,y+layer*.22,z),radius,'vex-patina' if layer%2==0 else 'alloy-dark',.45,[80,48,24][lod],'xz')
        d.ring(f'temporal-gate-{side}/conductive-ring',(x,y-.4,z),5.7,colour,.10,[96,48,24][lod],'xz',gap=8)
        for i in range([32,16,8][lod]):
            a=math.tau*i/[32,16,8][lod];px=x+6.65*math.cos(a);pz=z+6.65*math.sin(a)
            d.box(f'temporal-gate-{side}/radial-lock-{i}',(px,y+.4,pz),(.55,1.3,1.4),'vex-polished',rot=(0,math.pi/2-a,0))
            if lod<2:d.box(f'temporal-gate-{side}/glyph-{i}',(px,y-.3,pz),(.13,.05,.35),colour,rot=(0,-a,0))
        # Procedural transparent film and thin interference chords; no imported images.
        d.box(f'temporal-gate-{side}/film',(x,y+.8,z),(9.9,.035,9.9),'portal-film' if side<0 else 'portal-film-amber')
        for k in range([17,9,5][lod]):
            u=(k/([17,9,5][lod]-1)-.5)*9
            span=2*math.sqrt(max(.1,5.0**2-u*u))
            d.box(f'temporal-gate-{side}/interference-{k}',(x+u,y+.6,z),(.025,.02,span),colour)
        for side2 in [-1,1]:lance(d,f'gate-fin-{side}-{side2}',(x+side2*7,y+1,1),(x+side2*8,y+2,19),2.4,2.5,lod,'mineral-edge')
    # Human-scale architecture cues, not new character assets or a model display pedestal.
    for side in [-1,1]:
        for i in range(9):
            y=-8+i*3.7
            d.box(f'waymarker-{side}-{i}',(side*10.8,y,1.9),(.25,.25,1.3),'alloy-dark')
            d.box(f'waymarker-light-{side}-{i}',(side*10.8,y,2.55),(.2,.2,.12),'circuit')
    spec=d.result();spec['lod']=lod;return spec
