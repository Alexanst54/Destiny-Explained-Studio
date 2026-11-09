import hashlib,json,math,pathlib,struct,sys,tempfile,unittest,zlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from universal.registry import index,resolve,check_registry,implementations
from universal.request import request,validate
from universal.environments import generate
from universal.cache import valid_png,atomic_json
from venus_vault.geometry import digest

class UniversalLibrary(unittest.TestCase):
 def test_atlas_joins_keep_forms_and_collectives(self):
  d=index();self.assertEqual(len(d['entities']),300);entries={e['id']:e for e in d['entities']};self.assertEqual(len([e for e in d['entities'] if e['kind']=='boss']),128);self.assertEqual(len([e for e in d['entities'] if e['kind']=='form']),25)
  self.assertEqual(entries['boss-taniks-variant-abomination']['parentBossId'],'boss-taniks');self.assertTrue(entries['boss-taniks-variant-abomination']['encounterIds']);self.assertIn('boss-savathun',d['unlistedPriorities']);self.assertTrue(any(e['composition']!='individual' for e in d['entities'] if e['kind']=='boss'))
 def test_no_parent_or_generic_boss_fallback(self):
  for eid in ['boss-taniks','boss-taniks-variant-abomination','boss-oryx-variant-shade']:
   with self.assertRaisesRegex(ValueError,'dedicated'):resolve(eid,allow_family_study=True)
  with self.assertRaises(ValueError):resolve('boss-atheon',variant_id='boss-taniks-variant-abomination')
  with self.assertRaises(ValueError):resolve('boss-atheon',arena_id='oversoul-throne')
 def test_approved_models_protected_and_legacy_route(self):
  self.assertTrue(check_registry());b=resolve('boss-atheon');self.assertEqual(b['provider'],'venus-vault');self.assertEqual(b['environmentId'],'arena-glass-throne');self.assertTrue(implementations()['boss-atheon']['protectedFiles'])
 def test_family_studies_explicit_and_ambiguous(self):
  with self.assertRaises(ValueError):resolve('arena-golgoroth-s-cellar')
  self.assertEqual(resolve('arena-golgoroth-s-cellar',allow_family_study=True)['status'],'partial-family-study')
  with self.assertRaises(ValueError):resolve('black-garden',allow_family_study=True)
  with self.assertRaises(ValueError):resolve('arena-golgoroth-s-cellar',allow_family_study=True,family_id='neomuna')
  with self.assertRaises(ValueError):request('arena-golgoroth-s-cellar',family_study=True,family='hive',view='silhouette')
 def test_all_family_variants_determinism_and_geometry(self):
  for f in index()['families']:
   for variant in f['variants']:
    d=generate(f['id'],42,'draft',0,variant);other=generate(f['id'],42,'cinematic',0,variant)
    self.assertEqual(d['objects'],other['objects']);self.assertEqual(digest(d),digest(generate(f['id'],42,'draft',0,variant)))
    self.assertNotEqual(digest(d),digest(generate(f['id'],43,'draft',0,variant)));self.assertGreater(len(d['objects']),len(generate(f['id'],42,'draft',2,variant)['objects']))
    self.assertTrue(all(math.isfinite(v) for o in d['objects'] for v in o['position']+o['rotation']+o['size']))
 def test_request_normalization_and_bounds(self):
  r=request('boss-atheon',width=320,height=240);self.assertEqual(r['lod'],0);self.assertEqual(validate(r),r)
  for options in [dict(lod=True),dict(frames=121),dict(width=321),dict(fps=True),dict(view='unknown'),dict(animation='unknown'),dict(start_frame=17999,frames=2)]:
   with self.assertRaises(ValueError):request('boss-atheon',**options)
  altered={**r,'binding':{**r['binding'],'status':'made-up'}}
  with self.assertRaises(ValueError):validate(altered)
 def test_png_crc_decode_and_hash(self):
  def chunk(kind,payload):return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff)
  png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',2,1,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b'\0'+b'\xff\0\0'*2))+chunk(b'IEND',b'')
  with tempfile.TemporaryDirectory() as t:
   p=pathlib.Path(t)/'frame.png';p.write_bytes(png);self.assertTrue(valid_png(p,2,1,hashlib.sha256(png).hexdigest()));self.assertFalse(valid_png(p,3,1));self.assertFalse(valid_png(p,2,1,'0'*64));p.write_bytes(png[:-2]);self.assertFalse(valid_png(p,2,1));p.write_bytes(png+b'extra');self.assertFalse(valid_png(p,2,1))
   target=pathlib.Path(t)/'progress.json';atomic_json(target,{'status':'running'});self.assertEqual(json.loads(target.read_text())['status'],'running');self.assertFalse(target.with_suffix('.json.tmp').exists())
