"""Original voxel design vocabulary. Pure Python; metres, right-handed Z up, front = -Y.
No game meshes, textures or externally imported assets. Scene-independent generation.
"""
import hashlib
import json
import math
import random

QUALITY = {
    'draft': {'samples':16, 'bounces':3, 'vegetation':25, 'particles':24, 'haze':.002},
    'balanced': {'samples':48, 'bounces':5, 'vegetation':65, 'particles':65, 'haze':.0035},
    'cinematic': {'samples':128, 'bounces':7, 'vegetation':120, 'particles':120, 'haze':.0045},
}
# sRGB colour, roughness, metalness, emission strength. Shared bridge linearizes colour.
PALETTE = {
    'basalt':('#283b3b',.87,0,0), 'rock':('#4b6253',.95,0,0),
    'earth':('#354b32',.98,0,0), 'moss':('#6d843d',.96,0,0),
    'leaf':('#426736',.86,0,0), 'leaf-light':('#8a9f4a',.8,0,0),
    'bark':('#3b4935',.98,0,0), 'ishtar':('#b4ad8a',.78,.08,0),
    'ishtar-dark':('#5d736c',.7,.15,0), 'glass':('#327b80',.26,.5,0),
    'vex':('#8c7950',.38,.72,0), 'vex-dark':('#283a39',.4,.65,0),
    'vex-edge':('#b5a87c',.3,.65,0), 'bronze':('#685936',.38,.8,0),
    'silver':('#95aea8',.27,.85,0), 'silver-dark':('#536f70',.36,.8,0),
    'core':('#d3ffff',.18,.1,3), 'cyan':('#50dae8',.24,.15,3.8),
    'oracle':('#ffcc60',.3,.2,4), 'eye':('#ff6e32',.28,.2,6),
    'portal':('#64c9f6',.25,.2,2.2), 'portal-amber':('#e6bd65',.25,.2,2.2),
    'shield':('#95e4ff',.2,.2,2),
}

from cinematic_vex.materials import MATERIALS
PALETTE.update(MATERIALS)

class Design:
    def __init__(self, name, seed=42, quality='balanced'):
        if type(seed) is not int or not 0 <= seed <= 2147483647 or quality not in QUALITY:
            raise ValueError('Invalid seed or quality')
        self.name=name; self.seed=seed; self.quality=quality; self.rng=random.Random(seed)
        self.objects=[]; self.joints=[]

    def box(self, name, pos, size, mat='vex', rot=(0,0,0), joint=None):
        if mat not in PALETTE or any(not math.isfinite(v) or v<=0 for v in size):
            raise ValueError('Invalid material or box size')
        self.objects.append(dict(id=self.name+'/'+name, position=list(pos), size=list(size),
                                 rotation=list(rot), material=mat, joint=joint))

    def joint(self, name, pos, parent=None):
        self.joints.append(dict(id=name, position=list(pos), parent=parent))

    def ring(self, name, center, radius, mat='cyan', width=.14, segments=32, plane='xy', joint=None, gap=0):
        for i in range(segments):
            if gap and i%gap==0: continue
            a=math.tau*i/segments
            if plane=='xy':
                p=(center[0]+radius*math.cos(a),center[1]+radius*math.sin(a),center[2]);s=(width,radius*math.tau/segments*.9,width);r=(0,0,a)
            else:
                p=(center[0]+radius*math.cos(a),center[1],center[2]+radius*math.sin(a));s=(width,width,radius*math.tau/segments*.9);r=(0,-a,0)
            self.box(f'{name}-{i}',p,s,mat,r,joint)

    def pillar(self, name, x,y,height,width=1.7, base=0):
        self.box(name+'/foot',(x,y,base+.3),(width*1.5,width*1.5,.6),'vex-dark')
        self.box(name+'/shaft',(x,y,base+height/2),(width,width,height))
        for j in range(5):
            z=base+height*(.2+j*.15)
            self.box(name+f'/band-{j}',(x,y,z),(width*1.12,width*1.12,.18),'vex-edge')
        self.box(name+'/cap',(x,y,base+height),(width*1.7,width*1.7,.5),'vex-dark')
        self.box(name+'/channel',(x,y-width/2-.02,base+height*.55),(.1,.05,height*.65),'cyan')

    def result(self):
        ids=[o['id'] for o in self.objects]
        if len(set(ids))!=len(ids):raise ValueError('Duplicate design ID')
        return dict(name=self.name, seed=self.seed, quality=self.quality, objects=self.objects, joints=self.joints)


def digest(spec):
    return hashlib.sha256(json.dumps(spec,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
