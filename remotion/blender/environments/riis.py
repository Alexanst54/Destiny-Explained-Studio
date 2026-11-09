"""Riis settlement reconstruction v1. Pure stdlib geometry, no bpy or external assets."""
import argparse
import copy
import json
import math
from pathlib import Path
import random
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from contract import load,validate

DETAILS={'draft':{'districts':2,'floors':2,'windows':False,'terrain':5,'haze':0},
         'balanced':{'districts':3,'floors':3,'windows':True,'terrain':8,'haze':0},
         'cinematic':{'districts':4,'floors':4,'windows':True,'terrain':12,'haze':.008}}
PALETTE={'stone':('#566d79',.82,False),'terrace':('#8b999c',.72,False),
         'roof':('#344451',.6,False),'gold':('#b58b58',.42,False),
         'window':('#ffd18a',.35,True),'accent':('#8cddd7',.4,True),
         'ground':('#3f5663',.93,False),'rock':('#475b6b',.98,False),
         'far-rock':('#687c8a',1,False),'road':('#6e7d80',.86,False)}

def generate(snapshot,detail='balanced',seed=42,lighting='dawn'):
    validate(snapshot)
    if detail not in DETAILS or lighting not in ['dawn','blue-hour'] or type(seed) is not int or not 0<=seed<=2147483647:raise ValueError('Invalid environment options')
    if 'environment' in snapshot:raise ValueError('Already decorated; regenerate from the original snapshot')
    atlas=snapshot['source'].get('atlas',{})
    if atlas.get('locationId')!='riis' or atlas.get('variantId')!='before-whirlwind':raise ValueError('Requires Riis / before-whirlwind; no automatic historical substitution')
    d=copy.deepcopy(snapshot);rng=random.Random(seed);settings=DETAILS[detail]
    # Only the explicitly named legacy stage is replaced. Actors/props/camera remain exact.
    replaced=[m['id'] for m in d['meshes'] if m['id']=='ground' or m['id'].startswith('environment-')]
    d['meshes']=[m for m in d['meshes'] if m['id'] not in replaced]
    d['exporterVersion']='0.8.2'
    d['environment']={'generator':'riis-before-whirlwind','version':1,'detail':detail,'seed':seed,'lighting':lighting,'hazeDensity':settings['haze'],'replacedMeshIds':replaced,'visualStatus':'artistic-reconstruction'}
    for name,(color,roughness,emission) in PALETTE.items():d['materials'].append({'id':'riis/'+name,'color':color,'roughness':roughness,'emission':emission})
    def box(name,pos,size,mat='stone',yaw=0):
        x,y,z=pos;sx,sy,sz=size;c=math.cos(yaw);s=math.sin(yaw)
        d['meshes'].append({'id':'riis/'+name,'geometry':'box','material':'riis/'+mat,'matrixWorld':[c*sx,0,-s*sx,0,0,sy,0,0,s*sz,0,c*sz,0,x,y,z,1]})
    # Actor-level pedestrian plaza at y=0, valley cut below it; elevated side terraces.
    box('valley-floor',(0,-3.8,-28),(100,2,130),'ground')
    box('promenade',(0,-.3,-12),(11,.6,52),'road')
    for side in [-1,1]:
        box(f'plaza-edge-{side}',(side*5.3,-.1,-12),(.25,.25,52),'gold')
        for step in range(5):box(f'valley-bank-{side}-{step}',(side*(8+step*3),-2+step*.3,-27),(5,.8,68),'ground')
    # Terraced inhabited districts: setbacks, buttresses, doors, luminous slit windows.
    def tower(name,x,z,height,width=5):
        floors=settings['floors'];h=height/floors
        box(name+'/foundation',(x,.25,z),(width+1.5,.5,6.4),'terrace')
        for level in range(floors):
            w=width-level*.5;y=.5+level*h
            box(f'{name}/body-{level}',(x,y+h/2,z),(w,h,5.2),'stone')
            box(f'{name}/ledge-{level}',(x,y+h,z),(w+1,.28,6),'terrace')
            box(f'{name}/lintel-{level}',(x,y+h-.5,z+2.65),(w+.2,.2,.25),'gold')
            if settings['windows']:
                for col in [-1,0,1]:
                    box(f'{name}/window-{level}-{col}',(x+col*w*.24,y+h*.55,z+2.62),(.18,h*.35,.08),'window')
                    box(f'{name}/side-window-{level}-{col}',(x-w/2-.025,y+h*.55,z+col*1.4),(.08,h*.3,.32),'accent')
        box(name+'/door',(x,.95,z+2.66),(1.1,1.9,.16),'roof')
        box(name+'/door-top',(x,2,z+2.8),(1.7,.18,.38),'gold')
        box(name+'/crown',(x,height+1,z),(width*.65,1.4,4),'roof')
        box(name+'/spire',(x,height+2.5,z),(.32,2,.32),'gold')
        for sign in [-1,1]:box(f'{name}/rib-{sign}',(x+sign*(width/2+.15),height*.4,z+2.5),(.4,height*.8,.7),'roof',sign*.1)
    for row in range(settings['districts']):
        z=-10-row*11
        for side in [-1,1]:
            x=side*(8+row*1.1);height=5+row*2+rng.uniform(0,2)
            tower(f'district-{row}-{side}',x,z,height)
            box(f'platform-{row}-{side}',(x,.1,z),(8,.3,8),'terrace')
            for step in range(6):box(f'stairs-{row}-{side}-{step}',(side*(5.7+step*.28),step*.13,z+4),(.3,.26,2),'terrace')
            if row:
                box(f'walkway-{row}-{side}',(x,3.3,z+5.5),(1.5,.35,6),'terrace')
                for rail in [-1,1]:box(f'rail-{row}-{side}-{rail}',(x+rail*.7,3.9,z+5.5),(.1,.12,6),'gold')
    # Two overhead spans draw the eye towards the civic monument without hiding the actors.
    for i,z in enumerate([-19,-32]):
        box(f'bridge-{i}',(0,5.7+i*1.7,z),(17,.55,2),'terrace')
        for side in [-1,1]:
            box(f'bridge-pier-{i}-{side}',(side*5.9,2.7,z),(.55,5.6,2),'roof')
            box(f'bridge-rail-{i}-{side}',(0,6.2+i*1.7,z+side*.85),(17,.16,.12),'gold')
    tower('civic-monument',0,-49,19,8)
    for side in [-1,1]:
        tower(f'monument-wing-{side}',side*10,-48,13,6)
        box(f'monument-link-{side}',(side*5,7,-48),(10,.5,2),'gold')
    # Layered voxel mountains, deliberately schematic, not a canonical Riis geography.
    for layer in range(2):
        for i in range(settings['terrain']):
            x=(i-(settings['terrain']-1)/2)*11;z=-66-layer*22;peak=rng.uniform(16,30)+layer*3
            for tier in range(4):
                height=peak*(1-tier*.23)
                box(f'mountain-{layer}-{i}-{tier}',(x,-3+height/2,z),(12-tier*2,height,14-tier*2),'far-rock' if layer else 'rock')
    # Near-frame pylons and lamps establish depth; central six rigs are unobstructed.
    for side in [-1,1]:
        box(f'foreground-pylon-{side}',(side*5.4,3,2),(1.4,6,1.8),'roof')
        box(f'foreground-cap-{side}',(side*5.4,6,2),(2,.3,2.4),'gold')
        for i in range(4):
            z=-2-i*6
            box(f'lamp-{side}-{i}',(side*4.4,1,z),(.15,2,.15),'gold')
            box(f'lamp-glow-{side}-{i}',(side*4.4,2,z),(.3,.4,.3),'window')
    d['world']={'color':'#6a8fa9' if lighting=='dawn' else '#344c79','ambient':1.1 if lighting=='dawn' else .65}
    d['lights']=[{'id':'riis/sun','type':'sun','position':[-20,28,8],'target':[0,0,-20],'color':'#ffcf98' if lighting=='dawn' else '#a0bcff','intensity':3 if lighting=='dawn' else 1.6},
                 {'id':'riis/fill','type':'sun','position':[15,9,-15],'target':[0,1,-6],'color':'#88b8df','intensity':.7}]
    d['omissions'].append(f'Riis environment v1 replaces {len(replaced)} named legacy stage meshes, recorded in environment.replacedMeshIds; actors, props and camera unchanged.')
    d['omissions'].append('Artistic reconstruction: architecture, terrain, palette and lighting are invented visual design, not documented canonical Riis geography. No external assets.')
    d['omissions'].append('Depth haze uses tinted distant geometry; cinematic additionally uses a bounded homogeneous volume. No weather simulation or canonical city map.')
    return validate(d)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');p.add_argument('output');p.add_argument('--detail',choices=list(DETAILS),default='balanced');p.add_argument('--seed',type=int,default=42);p.add_argument('--lighting',choices=['dawn','blue-hour'],default='dawn');a=p.parse_args()
    d=generate(load(a.input),a.detail,a.seed,a.lighting);out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(d,separators=(',',':'))+'\n');print(f'{len(d["meshes"])} meshes, {len(d["actors"])} actors; {a.detail} / {a.lighting}',flush=True)
if __name__=='__main__':main()
