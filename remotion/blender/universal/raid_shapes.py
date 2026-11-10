"""Shared authored voxel primitives, not a shared boss body or rig."""
import math
from venus_vault.geometry import Design,PALETTE
from cinematic_vex.shapes import beam

def check(lod):
    if type(lod) is not int or lod not in [0,1,2]:raise ValueError('Invalid explicit LOD')

def taper(d,name,a,b,width,depth,mat,joint=None,lod=0,tip=.08):
    n=[16,8,3][lod]
    for i in range(n):
        t=(i+.5)/n;aa=tuple(a[k]+(b[k]-a[k])*i/n for k in range(3));bb=tuple(a[k]+(b[k]-a[k])*(i+.98)/n for k in range(3))
        beam(d,f'{name}/{i}',aa,bb,max(tip,width*(1-t)**.7),max(tip,depth*(1-t*.65)),mat,joint)

def shell(d,name,center,radii,mat,joint=None,lod=0,segments=None,rings=None):
    """Voxel shell with readable curved masses and open, non-cuboid contours."""
    nr=rings or [16,8,4][lod];ns=segments or [24,12,8][lod]
    for j in range(nr):
        t=(j+.5)/nr;z=-1+2*t;r=math.sqrt(max(.01,1-z*z))
        for i in range(ns):
            a=math.tau*i/ns;pos=(center[0]+radii[0]*r*math.cos(a),center[1]+radii[1]*r*math.sin(a),center[2]+radii[2]*z)
            d.box(f'{name}/{j}/{i}',pos,(max(.08,radii[0]*r*math.tau/ns*.9),max(.10,radii[1]*.25),radii[2]*2/nr*1.05),mat,(0,0,a+math.pi/2),joint)

def limb(d,name,a,b,width,depth,mat,dark,joint,lod=0):
    beam(d,name+'/core',a,b,width*.5,depth*.6,dark,joint)
    n=[16,8,4][lod];ns=[8,6,4][lod]
    for i in range(n):
        t=(i+.5)/n;bulge=.55+.45*math.sin(t*math.pi);p=tuple(a[k]+(b[k]-a[k])*t for k in range(3))
        for j in range(ns):
            angle=math.tau*j/ns
            d.box(f'{name}/plate-{i}-{j}',(p[0]+math.cos(angle)*width*.32*bulge,p[1]+math.sin(angle)*depth*.3,p[2]),(width*.4*bulge,depth*.3,math.dist(a,b)/n*.96),mat,(0,0,angle*.12),joint)

def arc_blade(d,name,center,radius,start,end,width,mat,joint,lod=0,plane='xz'):
    n=[40,20,8][lod]
    for i in range(n):
        a=start+(end-start)*i/n;b=start+(end-start)*(i+1)/n
        aa=(center[0]+radius*math.cos(a),center[1],center[2]+radius*math.sin(a));bb=(center[0]+radius*math.cos(b),center[1],center[2]+radius*math.sin(b))
        beam(d,f'{name}/{i}',aa,bb,width*(1-i/n*.85),.28,mat,joint)

def motes(d,name,joint,mat,seed_radius=3,lod=0):
    for i in range([48,20,6][lod]):
        a=d.rng.uniform(0,math.tau);r=d.rng.uniform(.8,seed_radius);s=d.rng.uniform(.025,.07)
        d.box(f'{name}/{i}',(r*math.cos(a),r*math.sin(a),d.rng.uniform(-2,3)),(s,s,s*2),mat,joint=joint)

def floor(d,name,mat,dark,width=40,length=56,lod=0):
    d.box(name+'/base',(0,16,-.6),(width,length,1.2),dark)
    nx=[12,8,4][lod];ny=[16,10,5][lod]
    for x in range(nx):
        for y in range(ny):d.box(f'{name}/tile-{x}-{y}',((x-(nx-1)/2)*width/nx,16+(y-(ny-1)/2)*length/ny,.05),(width/nx-.09,length/ny-.09,.1),mat if d.rng.random()>.15 else dark)

def camera_for(view,height=16,span=12,frame=0,fps=24):
    """True 90-degree profile / 45-degree three-quarter; physical sensor fit."""
    if view not in ['front','profile','three-quarter','cinematic','environment','silhouette','reveal','close-up'] or type(frame) is not int or frame<0 or type(fps) is not int or fps not in [24,30]:raise ValueError('Invalid camera view/time')
    center=(0,12,height*.49);distance=max(height*2.5,span*1.55);lens=42
    if view=='profile':position=(distance,12,height*.52)
    elif view=='three-quarter':position=(distance/math.sqrt(2),12-distance/math.sqrt(2),height*.52)
    elif view=='cinematic':position=(distance*.23,12-distance*.95,height*.11);center=(0,12,height*.48);lens=39
    elif view=='environment':position=(distance*.48,12-distance*1.3,height*.85);center=(0,20,height*.5);lens=30
    elif view=='close-up':position=(height*.4,12-height*1.25,height*.83);center=(0,12,height*.8);lens=50
    elif view=='reveal':
        u=min(frame/fps/2,1);u=u*u*(3-2*u);position=(distance*.14,12-distance,height*(.1+u*.45));center=(0,12,height*(.15+u*.48))
    else:position=(0,12-distance,height*.52)
    return dict(position=position,target=center,lens=lens,sensorHeight=24,sensorFit='VERTICAL',far=600)

def wear(mat,name):
    if any(k in name for k in ['glow','eye','light','resonance']):return
    tree=mat.node_tree;n=tree.nodes;bsdf=n.get('Principled BSDF');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=8;noise.inputs['Detail'].default_value=3
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.14;bump.inputs['Distance'].default_value=.045;tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);tree.links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
