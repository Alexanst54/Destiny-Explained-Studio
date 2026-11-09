"""Reproducible library index; all entries retained, missing content stays visible."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from universal.registry import index,ROOT,catalog

def build():
    d=index();d['baseCommit']='9488dd8950b05d203e892f390e4f86725a783faa';d['userApprovedModels']=['boss-atheon','boss-templar']
    locations={l['id']:l for l in d['locations']};activity_locations=catalog()['activityLocations']
    for e in d['entities']:
        seeds=set(e['arenaIds'])|({e['id']} if e['kind']=='environment' else set())|{x['locationId'] for x in activity_locations if x['activityId'] in e['activityIds']}
        ancestors=set()
        for seed in seeds:
            current=seed;seen=set()
            while current and current not in seen:
                seen.add(current);location=locations[current]
                if location['type'] in ['stellar-body','destination-region','ship-station','lore-world'] and current not in ['solar-system','sun']:ancestors.add(current)
                current=location['parentId']
        e['destinationIds']=sorted(ancestors)
        e['previews']=[]
        if e['id'] in d['userApprovedModels']:
            n='front' if e['id']=='boss-atheon' else 'templar';e['previews']=[dict(view='existing-evidence',path=f'docs/previews/cinematic-vex-0.9.1/after/{n}.png',quality='cinematic')]
        if e['id']=='boss-crota' and (ROOT/'docs/universal-library/crota/evidence.json').exists():
            proof=json.loads((ROOT/'docs/universal-library/crota/evidence.json').read_text())
            e['previews']=[dict(view=v['view'],path='docs/universal-library/crota/'+v['images'][0]['path'],quality='balanced' if v['view']=='attack' else 'cinematic') for v in proof['views']]
        # A study belongs to a family, never grants a named Atlas environment implemented status.
    used={i for e in d['entities'] for i in e['destinationIds']};d['destinations']=[l for l in d['locations'] if l['id'] in used]
    return json.dumps(d,ensure_ascii=False,indent=2)+'\n'

if __name__=='__main__':
    target=ROOT/'docs/universal-library/catalog.json';text=build()
    if '--check' in sys.argv:
        if not target.exists() or target.read_text()!=text:raise SystemExit('Library index is stale')
    else:target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
