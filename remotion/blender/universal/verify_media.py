"""Verify shipped family studies and registry coverage without requiring Blender."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from universal.registry import ROOT,check_registry,families
from universal.cache import valid_png
from universal.environments import generate
from venus_vault.geometry import digest

def verify():
    check_registry();folder=ROOT/'docs/universal-library/studies';e=json.loads((folder/'evidence.json').read_text())
    if {s['familyId'] for s in e['studies']}!={f['id'] for f in families()}:raise ValueError('Family proof coverage differs')
    for s in e['studies']:
        path=folder/s['report']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=s['reportSha256']:raise ValueError('Report hash differs')
        r=json.loads(path.read_text());q=r['request'];f=r['frames']['0']
        if r['status']!='success' or q['binding']['provider']!='family-study' or s['status']!='partial-family-study' or q['binding']['familyId']!=s['familyId']:raise ValueError('Invalid proof status')
        if s['sha256']!=f['sha256'] or not valid_png(folder/s['image'],q['width'],q['height'],s['sha256']):raise ValueError('Invalid proof PNG')
        design=generate(s['familyId'],q['seed'],q['quality'],q['lod'],q['environmentVariant'])
        if r['configuration']['designSha256']!=digest(design):raise ValueError('Current design differs from rendered proof')
    return len(e['studies'])

if __name__=='__main__':print('Verified real Blender family studies:',verify())
