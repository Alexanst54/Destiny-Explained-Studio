"""Read-only Atlas joins, explicit implementations, no generic-boss substitution."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
ATLAS=ROOT/'remotion/atlas/universal/catalog.json'
HERE=Path(__file__).parent
PRIORITY=('boss-crota','boss-oryx','boss-rhulk','boss-nezarec','boss-witness','boss-riven','boss-taniks','boss-aksis','boss-savathun','boss-calus','boss-atraks','boss-golgoroth','boss-gahlran','boss-insurrection-prime')

def catalog():return json.loads(ATLAS.read_text())
def implementations():return json.loads((HERE/'models.json').read_text())
def families():return json.loads((HERE/'families.json').read_text())

def check_registry():
    c=catalog();m=implementations();entities={x['id']:x for k in ['bosses','bossVariants','locations'] for x in c[k]}
    for entity,b in m.items():
        if entity not in entities:raise ValueError('Unknown Atlas implementation '+entity)
        if b['provider'] not in ['venus-vault','universal']:raise ValueError('Unknown provider')
        if b.get('environmentId'):
            links=[l for l in c['encounterBosses'] if l['bossId']==entity or l['bossVariantId']==entity]
            if not any(l['encounterId']==p['encounterId'] and p['locationId']==b['environmentId'] for l in links for p in c['encounterLocations']):raise ValueError('Unlinked arena '+entity)
        for f in b['protectedFiles']:
            if hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()!=f['sha256']:raise ValueError('Validated model changed: '+f['path'])
    return True

def index():
    check_registry();c=catalog();m=implementations();fs=families();out=[]
    encounters={e['id']:e for e in c['encounters']};activities={e['id']:e for e in c['activities']}
    for kind,key in [('boss','bosses'),('form','bossVariants'),('environment','locations')]:
        for entity in c[key]:
            eid=entity['id'];bid=entity.get('bossId',eid)
            links=[l for l in c['encounterBosses'] if l['bossId']==bid and (kind!='form' or l['bossVariantId']==eid)] if kind!='environment' else []
            encounter_ids=sorted({l['encounterId'] for l in links})
            if kind=='environment':encounter_ids=sorted({l['encounterId'] for l in c['encounterLocations'] if l['locationId']==eid})
            activity_ids=sorted({encounters[x]['activityId'] for x in encounter_ids})
            arenas=sorted({l['locationId'] for l in c['encounterLocations'] if l['encounterId'] in encounter_ids})
            impl=m.get(eid)
            profiles=[p for p in c['assetReusePlans'] if p['entityId']==eid]
            family=entity['environmentFamily'];family_ids=[f['id'] for f in fs if family in f['atlasFamilies'] or eid in f.get('entityIds',[])]
            out.append(dict(id=eid,name=entity['frName'],enName=entity['enName'],kind=kind,parentBossId=entity.get('bossId'),composition=entity.get('composition'),members=entity.get('members',[]),nature=entity.get('nature'),priority=bid in PRIORITY,
              atlasVisualStatus=entity['visualStatus'],status=impl['status'] if impl else 'missing',implementation=impl,
              family=family,familyCandidates=family_ids,arenaIds=arenas,encounterIds=encounter_ids,activityIds=activity_ids,
              activityTypes=sorted({activities[x]['type'] for x in activity_ids}),variants=[x['id'] for x in c['bossVariants'] if x['bossId']==eid],
              encounterBindings=links,sourceIds=entity['sources'],reusePlans=profiles))
    return dict(version='1.0-workstream',atlasSha256=hashlib.sha256(ATLAS.read_bytes()).hexdigest(),entities=out,
        activities=c['activities'],encounters=c['encounters'],locations=c['locations'],sources=c['sources'],families=fs,
        unlistedPriorities=[x for x in PRIORITY if x not in {e['id'] for e in out}],
        note='Missing forms never inherit the parent model. Family studies do not implement named arenas or bosses.')

def resolve(entity_id,arena_id=None,variant_id=None,allow_family_study=False,family_id=None):
    data=index();entries={e['id']:e for e in data['entities']}
    if entity_id not in entries:raise ValueError('Unknown Atlas entity: '+entity_id)
    entry=entries[entity_id]
    if variant_id:
        if variant_id not in entry['variants']:raise ValueError('Variant does not belong to selected boss')
        entry=entries[variant_id]
    impl=entry['implementation']
    if impl:
        if arena_id and arena_id!=impl.get('environmentId',entry['id']):raise ValueError('Arena not implemented for this model')
        return dict(entity=entry,provider=impl['provider'],selectionId=entry['id'],environmentId=impl.get('environmentId',entry['id']),status=impl['status'])
    if entry['kind']!='environment':raise ValueError('No dedicated model for '+entry['id']+'; generic substitution prohibited')
    if not allow_family_study:raise ValueError('Environment not implemented; explicit --family-study required for architectural study')
    choices=entry['familyCandidates']
    if family_id and family_id not in choices:raise ValueError('Family is not an Atlas candidate')
    if not family_id and len(choices)!=1:raise ValueError('Choose explicit --family from '+str(choices))
    return dict(entity=entry,provider='family-study',selectionId=entry['id'],environmentId=entry['id'],familyId=family_id or choices[0],status='partial-family-study')
