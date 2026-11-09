"""Original layered voxel armour vocabulary; all surfaces built from authored boxes."""
import math


def beam(d,name,a,b,width,depth,mat='alloy',joint=None):
    dx,dy,dz=[b[i]-a[i] for i in range(3)];length=math.sqrt(dx*dx+dy*dy+dz*dz)
    if length<1e-8:raise ValueError('Degenerate beam')
    d.box(name,tuple((a[i]+b[i])/2 for i in range(3)),(width,depth,length),mat,
          (math.asin(-dy/length),math.atan2(dx,dz),0),joint)


def lance(d,name,a,b,width,depth,lod=0,mat='alloy',joint=None):
    """Tapered stepped blade. Same outer proportions at every explicit LOD."""
    cuts=[18,8,3][lod]
    for i in range(cuts):
        p=(i+.5)/cuts;start=tuple(a[j]+(b[j]-a[j])*i/cuts for j in range(3));end=tuple(a[j]+(b[j]-a[j])*(i+1)/cuts for j in range(3))
        beam(d,f'{name}/{i}',start,end,max(.045,width*(1-p)**.7),max(.06,depth*(1-p*.75)),mat,joint)
        if lod==0 and i<cuts-3:
            # Discontinuous edge inlays and dark seams; not a uniform luminous outline.
            center=tuple((start[j]+end[j])/2 for j in range(3))
            d.box(f'{name}/etch-{i}',(center[0],center[1]-depth*.51,center[2]),(max(.04,width*(1-p)*.3),.025,.045),'circuit',joint=joint)


def joint_hub(d,name,center,radius,joint,lod=0,axis='xz'):
    d.ring(name+'/bearing',center,radius,'mechanism',radius*.42,[24,16,8][lod],axis,joint)
    d.ring(name+'/rim',center,radius*1.04,'alloy-dark',.09,[24,16,8][lod],axis,joint)
    if lod<2:d.ring(name+'/teeth',center,radius*.82,'alloy',.08,[20,12,8][lod],axis,joint,gap=3)


def cable(d,name,points,joint,lod=0,mat='circuit',width=.07):
    for i in range(len(points)-1):beam(d,f'{name}/{i}',points[i],points[i+1],width,width,mat,joint)


def armour(d,name,a,b,width,depth,joint,lod=0,mat='alloy'):
    # Layered plate around a visible dark mechanical axis.
    beam(d,name+'/axis',a,b,width*.55,depth*.75,'mechanism',joint)
    steps=[12,6,2][lod]
    for i in range(steps):
        t=(i+.5)/steps;bulge=.65+.35*math.sin(math.pi*t)
        start=tuple(a[j]+(b[j]-a[j])*(i+.03)/steps for j in range(3));end=tuple(a[j]+(b[j]-a[j])*(i+.93)/steps for j in range(3))
        start=(start[0],start[1]-depth*.25,start[2]);end=(end[0],end[1]-depth*.25,end[2])
        beam(d,f'{name}/plate-{i}',start,end,width*bulge,depth*.5,mat if i%4 else 'alloy-dark',joint)
        if lod==0:
            c=tuple((start[j]+end[j])/2 for j in range(3))
            for s in [-1,1]:d.box(f'{name}/fastener-{i}-{s}',(c[0]+s*width*.27,c[1]-depth*.3,c[2]),(.07,.04,.07),'fastener',joint=joint)
