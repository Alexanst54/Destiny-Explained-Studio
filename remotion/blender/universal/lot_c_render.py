"""Render the authored Lot C validation plan through the existing universal CLI."""
import argparse,json,subprocess,sys
from pathlib import Path
sys.path[:]=[p for p in sys.path if Path(p).resolve()!=Path(__file__).resolve().parent]
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from universal.registry import ROOT

def plan():
 config=json.loads(Path(__file__).with_name('lot_c_shots.json').read_text());jobs=[]
 for boss in config['bosses']:
  for view in config['stills']['views']:
   jobs.append(dict(boss=boss['id'],slug=boss['slug'],name=view,view=view,quality=config['stills']['quality'],width=960 if view=='environment' else boss['width'],height=540 if view=='environment' else boss['height'],animation='idle',frames=1,fps=24,lod=config['lod'],seed=config['seed']))
  jobs.append(dict(boss=boss['id'],slug=boss['slug'],name='animation',animation=boss['animation'],lod=config['lod'],seed=config['seed'],**config['clip']))
 return jobs

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('output');p.add_argument('--boss',choices=['oryx','rhulk','nezarec']);p.add_argument('--phase',choices=['all','stills','clips'],default='all');p.add_argument('--blender',default='blender');p.add_argument('--resume',action='store_true');p.add_argument('--plan-only',action='store_true');p.add_argument('--threads',type=int,default=3);a=p.parse_args();jobs=[j for j in plan() if (not a.boss or a.boss==j['slug']) and (a.phase=='all' or (j['name']=='animation')==(a.phase=='clips'))]
 if a.plan_only:print(json.dumps(jobs,indent=2));return
 out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
 for j in jobs:
  folder=out/j['slug']/j['name'];cmd=[sys.executable,str(ROOT/'remotion/blender/render_universal.py'),j['boss'],str(folder),'--blender',a.blender,'--threads',str(a.threads),'--timeout','3600']
  for key in ['view','quality','width','height','animation','frames','fps','lod','seed']:cmd+=['--'+key,str(j[key])]
  if j['name']=='animation':cmd+=['--video']
  if a.resume:cmd+=['--resume']
  print('START '+j['slug']+'/'+j['name'],flush=True)
  with (out/(j['slug']+'-'+j['name']+'.log')).open('a') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
  print('DONE '+j['slug']+'/'+j['name'],flush=True)
if __name__=='__main__':main()
