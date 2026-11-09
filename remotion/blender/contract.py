"""Bridge v1 validation; stdlib only, also imported by Blender."""
import json
import math
import re
from pathlib import Path
class BridgeError(ValueError): pass

def keys(x, required, optional=()):
    if not isinstance(x,dict) or set(required)-set(x) or set(x)-set(required)-set(optional): raise BridgeError('Unknown or missing fields')
def number(x,lo=-10000,hi=10000,integer=False):
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or not lo<=x<=hi or integer and int(x)!=x: raise BridgeError('Invalid number')
def text(x,maximum=200):
    if not isinstance(x,str) or not 1<=len(x)<=maximum: raise BridgeError('Invalid string')
def items(x,maximum,minimum=0):
    if not isinstance(x,list) or not minimum<=len(x)<=maximum: raise BridgeError('Invalid list size')
def vec(x):
    items(x,3,3)
    for v in x:number(v)
def matrix(m):
    items(m,16,16)
    for v in m:number(v)
    if [m[i] for i in [3,7,11,15]]!=[0,0,0,1]:raise BridgeError('Expected affine column-major matrix')
    det=m[0]*(m[5]*m[10]-m[9]*m[6])-m[4]*(m[1]*m[10]-m[9]*m[2])+m[8]*(m[1]*m[6]-m[5]*m[2])
    if abs(det)<1e-12:raise BridgeError('Singular transform')
def color(x):
    if not isinstance(x,str) or not re.fullmatch(r'#[0-9a-fA-F]{6}',x):raise BridgeError('Invalid color')
def validate(d):
    keys(d,['format','version','exporterVersion','coordinateSystem','matrixLayout','profile','source','resolution','camera','world','lights','materials','actors','meshes','omissions'],['environment'])
    if (d['format'],d['version'],d['coordinateSystem'],d['matrixLayout'])!=('destiny-blender-scene',1,'RIGHT_HANDED_Y_UP','column-major') or d['exporterVersion'] not in ['0.8.1','0.8.2'] or type(d['version']) is not int:raise BridgeError('Unsupported contract/version/axes')
    if 'environment' in d:
        e=d['environment'];keys(e,['generator','version','detail','seed','lighting','hazeDensity','replacedMeshIds','visualStatus'])
        if e['generator']!='riis-before-whirlwind' or type(e['version']) is not int or e['version']!=1 or e['detail'] not in ['draft','balanced','cinematic'] or e['lighting'] not in ['dawn','blue-hour'] or e['visualStatus']!='artistic-reconstruction':raise BridgeError('Invalid environment metadata')
        number(e['seed'],0,2147483647,True);number(e['hazeDensity'],0,.02);items(e['replacedMeshIds'],4096)
        for v in e['replacedMeshIds']:text(v)
        if len(set(e['replacedMeshIds']))!=len(e['replacedMeshIds']):raise BridgeError('Duplicate replacement id')
    if d['profile'] not in ['standard','cinematic']:raise BridgeError('Unknown profile')
    s=d['source'];keys(s,['projectId','projectVersion','projectSha256','sceneId','shotId','frame','localFrame','fps','timing','loreMode','visualStatus','sourceIds'],['atlas'])
    for k in ['projectId','projectVersion','sceneId','shotId','loreMode']:text(s[k])
    if not isinstance(s['projectSha256'],str) or not re.fullmatch('[a-f0-9]{64}',s['projectSha256']):raise BridgeError('Invalid hash')
    number(s['frame'],0,17999,True);number(s['localFrame'],0,17999,True)
    if s['fps']!=30 or isinstance(s['fps'],bool) or s['timing'] not in ['aligned','estimated'] or s['visualStatus']!='artistic-reconstruction':raise BridgeError('Invalid source metadata')
    items(s['sourceIds'],128)
    for v in s['sourceIds']:text(v)
    if 'atlas' in s:
        keys(s['atlas'],['locationId'],['variantId'])
        for v in s['atlas'].values():text(v)
    if d['resolution']!={'width':1080,'height':1920}:raise BridgeError('Expected 1080x1920 target')
    c=d['camera'];keys(c,['matrixWorld','position','target','verticalFov','near','far']);matrix(c['matrixWorld']);vec(c['position']);vec(c['target']);number(c['verticalFov'],10,100);number(c['near'],.01,10);number(c['far'],20,1000)
    if c['near']>=c['far'] or any(abs(c['position'][i]-c['matrixWorld'][12+i])>1e-6 for i in range(3)):raise BridgeError('Inconsistent camera')
    keys(d['world'],['color','ambient']);color(d['world']['color']);number(d['world']['ambient'],0,10)
    for name,maximum,minimum in [('materials',256,1),('actors',32,0),('lights',8,1),('meshes',4096,1),('omissions',256,0)]:items(d[name],maximum,minimum)
    mats=set();actors=set()
    for m in d['materials']:
        keys(m,['id','color','emission','roughness']);text(m['id']);color(m['color']);number(m['roughness'],0,1)
        if type(m['emission']) is not bool or m['id'] in mats:raise BridgeError('Invalid/duplicate material')
        mats.add(m['id'])
    for a in d['actors']:
        keys(a,['id','characterId','rigArchetype','position','yaw','rootMatrix','joints'],['variantId'])
        for k in ['id','characterId','rigArchetype']:text(a[k])
        if 'variantId' in a:text(a['variantId'])
        if a['id'] in actors:raise BridgeError('Duplicate actor')
        actors.add(a['id']);vec(a['position']);number(a['yaw']);matrix(a['rootMatrix']);items(a['joints'],100);seen=set()
        for j in a['joints']:
            keys(j,['id','parent','matrixWorld']);text(j['id']);matrix(j['matrixWorld'])
            if j['id'] in seen or j['parent'] is not None and j['parent'] not in seen:raise BridgeError('Invalid joint hierarchy')
            seen.add(j['id'])
    for name in ['lights','meshes']:
        seen=set()
        for x in d[name]:
            text(x['id'])
            if x['id'] in seen:raise BridgeError('Duplicate '+name+' id')
            seen.add(x['id'])
            if name=='lights':
                keys(x,['id','type','position','target','color','intensity']);vec(x['position']);vec(x['target']);color(x['color']);number(x['intensity'],0,20)
                if x['type']!='sun':raise BridgeError('Unsupported light')
            else:
                keys(x,['id','geometry','material','matrixWorld'],['actorId']);matrix(x['matrixWorld'])
                if x['geometry'] not in ['box','sphere'] or x['material'] not in mats or 'actorId' in x and x['actorId'] not in actors:raise BridgeError('Invalid mesh reference/geometry')
    for x in d['omissions']:text(x,500)
    return d

def load(path):
    path=Path(path)
    if path.stat().st_size>4*1024*1024:raise BridgeError('Bridge JSON exceeds 4 MiB')
    return validate(json.loads(path.read_text(encoding='utf-8')))
