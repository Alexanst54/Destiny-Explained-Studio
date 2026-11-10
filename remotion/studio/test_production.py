import copy,json,pathlib,sys,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from production import options,validate,chunks,prepare,ROOT,speech_chunks

def config(boss='boss-rhulk'):
 m=next(x for x in options() if x['id']==boss)
 return dict(boss=boss,arena=m['implementation']['environmentId'],animation=m['implementation']['animations'][0],camera=m['cameras'][0],quality='draft',duration=2,narration='Voici ce boss.',voice='ff_siwis',subtitles=True,width=320,height=240,fps=24,music='',musicCredit='')
class Studio(unittest.TestCase):
 def test_actual_options_and_model_specific_validation(self):
  self.assertEqual({m['id'] for m in options()},{'boss-atheon','boss-templar','boss-crota','boss-oryx','boss-rhulk','boss-nezarec'})
  for m in options():
   for a in m['implementation']['animations']:
    for v in m['cameras']:
     c=config(m['id']);c.update(animation=a,camera=v);self.assertEqual(validate(c)['frames'],48)
 def test_foreign_arena_missing_boss_and_unsupported_controls(self):
  for change in [dict(boss='boss-riven'),dict(arena='arena-threshold'),dict(animation='bogus'),dict(voice='af_heart'),dict(duration=float('nan')),dict(duration=601),dict(narration=''),dict(width=321),dict(music='track.mp3')]:
   c=config();c.update(change)
   with self.assertRaises(ValueError):validate(c)
  c=config('boss-templar');c['camera']='cinematic'
  with self.assertRaises(ValueError):validate(c)
 def test_continuous_chunk_boundaries_and_tail(self):
  c=config();c['duration']=10.125;c=validate(c);parts=chunks(c)
  self.assertEqual(parts,[dict(start=0,frames=120),dict(start=120,frames=120),dict(start=240,frames=3)])
  self.assertEqual([n for p in parts for n in range(p['start'],p['start']+p['frames'])],list(range(243)))
 def test_changed_project_cannot_reuse_incompatible_cache(self):
  with tempfile.TemporaryDirectory() as tmp:
   c,_=prepare(config(),tmp);prepare(config(),tmp)
   d=config();d['narration']='Autre texte.'
   with self.assertRaises(ValueError):prepare(d,tmp)
   self.assertEqual(json.loads((pathlib.Path(tmp)/'project.json').read_text())['config'],c)
 def test_long_french_text_is_chunked_without_losing_words(self):
  text=('Athéon contrôle le temps, Oryx surgit. '*30).strip();parts=speech_chunks(text)
  self.assertEqual(' '.join(parts).split(),text.split());self.assertTrue(all(len(x)<=180 for x in parts))
  with self.assertRaises(ValueError):speech_chunks('x'*181)
 def test_notebook_no_execution_outputs_and_compilable_cells(self):
  nb=json.loads((ROOT/'remotion/blender/Destiny-Studio-Colab-Pro.ipynb').read_text())
  for cell in nb['cells']:
   if cell['cell_type']=='code':compile(''.join(cell['source']),'notebook','exec');self.assertEqual(cell['outputs'],[])
