"""Reproducible library index; all entries retained, missing content stays visible."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from universal.registry import index,ROOT

def build():
    d=index();d['baseCommit']='9488dd8950b05d203e892f390e4f86725a783faa';d['userApprovedModels']=['boss-atheon','boss-templar']
    for e in d['entities']:
        e['previews']=[]
        if e['id'] in d['userApprovedModels']:
            n='front' if e['id']=='boss-atheon' else 'templar';e['previews']=[dict(view='existing-evidence',path=f'docs/previews/cinematic-vex-0.9.1/after/{n}.png',quality='cinematic')]
        # A study belongs to a family, never grants a named Atlas environment implemented status.
    return json.dumps(d,ensure_ascii=False,indent=2)+'\n'

if __name__=='__main__':
    target=ROOT/'docs/universal-library/catalog.json';text=build()
    if '--check' in sys.argv:
        if not target.exists() or target.read_text()!=text:raise SystemExit('Library index is stale')
    else:target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
