"""Bounded render request and Atlas resolver. Reads existing IDs, never creates entities."""
import json
from pathlib import Path
from .geometry import QUALITY
from .camera import PRESETS
BINDINGS=json.loads(Path(__file__).with_name('atlas-bindings.json').read_text())
ATLAS=Path(__file__).resolve().parents[2]/'atlas/universal/catalog.json'


def select(entity_id, quality='balanced', seed=42, camera='wide', animation='idle', frames=1, fps=30, width=960, height=540, start_frame=0):
    catalog=json.loads(ATLAS.read_text())
    locations={p['id']:p for p in catalog['locations']};bosses={p['id']:p for p in catalog['bosses']}
    if entity_id in BINDINGS['bosses']:
        binding=BINDINGS['bosses'][entity_id];env=binding['environmentId'];boss=entity_id
        if bosses.get(boss,{}).get('blenderAssetId')!=binding['assetId']:raise ValueError('Boss Atlas binding differs')
        links=[r for r in catalog['encounterBosses'] if r['bossId']==boss]
        if not any(any(e['encounterId']==r['encounterId'] and e['locationId']==env for e in catalog['encounterLocations']) for r in links):
            raise ValueError('Boss arena is not linked in Atlas')
    elif entity_id in BINDINGS['environments']:
        env=entity_id;boss=None
    else:raise ValueError('Selection is outside the implemented Venus/Vault extension')
    if locations.get(env,{}).get('blenderAssetId')!=BINDINGS['environments'][env]['assetId']:raise ValueError('Environment Atlas binding differs')
    return validate(dict(version=1,selectionId=entity_id,environmentId=BINDINGS['environments'][env]['generator'],bossId=boss,
                         quality=quality,seed=seed,camera=camera,animation=animation,frames=frames,fps=fps,width=width,height=height,startFrame=start_frame))


def validate(r):
    fields={'version','selectionId','environmentId','bossId','quality','seed','camera','animation','frames','fps','width','height','startFrame'}
    if not isinstance(r,dict) or set(r)!=fields or type(r['version']) is not int or r['version']!=1:raise ValueError('Unsupported render request')
    if r['selectionId'] in BINDINGS['bosses']:
        b=BINDINGS['bosses'][r['selectionId']]
        if r['bossId']!=r['selectionId'] or r['environmentId']!=b['environmentId'] or r['animation'] not in b['animations']:raise ValueError('Boss, arena or animation mismatch')
    elif r['selectionId'] in BINDINGS['environments']:
        if r['bossId'] is not None or r['environmentId']!=BINDINGS['environments'][r['selectionId']]['generator'] or r['animation']!='idle':raise ValueError('Invalid environment-only request')
    else:raise ValueError('Unknown Atlas selection')
    if r['quality'] not in QUALITY or r['camera'] not in PRESETS:raise ValueError('Unknown quality or camera')
    for k,lo,hi in [('startFrame',0,17999),('seed',0,2147483647),('frames',1,120),('width',320,1920),('height',240,1920)]:
        if type(r[k]) is not int or not lo<=r[k]<=hi:raise ValueError('Invalid '+k)
    if type(r['fps']) is not int or r['fps'] not in [24,30] or r['width']%2 or r['height']%2:raise ValueError('Invalid dimensions or fps')
    if r['startFrame']+r['frames']>18000:raise ValueError('Frame range exceeds bound')
    return r
