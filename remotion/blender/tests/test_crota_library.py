import math,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from universal import crota
from universal.registry import resolve
from universal.request import request
from venus_vault.geometry import digest

class CrotaLibrary(unittest.TestCase):
 def test_dedicated_identity_and_sourced_arena(self):
  binding=resolve('boss-crota');self.assertEqual(binding['environmentId'],'oversoul-throne');self.assertTrue(binding['entity']['encounterIds']);self.assertEqual(binding['status'],'partial-dedicated-prototype');self.assertEqual(request('boss-crota',animation='attack')['binding']['provider'],'universal')
 def test_silhouette_landmarks_not_vex_model(self):
  d=crota.generate();ids=[o['id'] for o in d['objects']]
  for landmark in ['three-eyes-0','three-eyes-1','three-eyes-2','cleaver-hook','mouth-cavity','rib-','pauldron-','soul-vessel-']:
   self.assertTrue(any(landmark in x for x in ids),landmark)
  self.assertFalse(any('chevron' in x or 'torch-cannon' in x for x in ids));self.assertTrue(all(o['material'].startswith('crota-') for o in d['objects']))
 def test_lod_quality_seed_and_joint_contract(self):
  full=crota.generate();medium=crota.generate(lod=1);low=crota.generate(lod=2);self.assertGreater(len(full['objects']),len(medium['objects']));self.assertGreater(len(medium['objects']),len(low['objects']));self.assertEqual(full['joints'],low['joints']);self.assertEqual(full['objects'],crota.generate(quality='draft')['objects']);self.assertNotEqual(digest(full),digest(crota.generate(seed=43)))
  for data in [full,medium,low,crota.arena()]:
   ids=[o['id'] for o in data['objects']];self.assertEqual(len(ids),len(set(ids)));self.assertTrue(all(math.isfinite(x) for o in data['objects'] for x in o['position']+o['rotation']+o['size']))
 def test_animation_random_access_clock_and_channels(self):
  names={j['id'] for j in crota.generate()['joints']}
  for mode in ['idle','move','attack','reveal']:
   first=crota.pose(mode,24,24);crota.pose(mode,3);self.assertEqual(first,crota.pose(mode,24,24));self.assertEqual(first,crota.pose(mode,30,30));self.assertNotEqual(first,crota.pose(mode,0))
   self.assertTrue(all(set(first[k])<=names for k in ['rotation','position','scale']));self.assertTrue(all(math.isfinite(x) for k in ['rotation','position','scale'] for v in first[k].values() for x in v))
 def test_provider_cannot_impersonate_an_unrelated_boss(self):
  from universal.providers import load
  from unittest.mock import patch
  self.assertIs(load('boss-crota'),crota)
  from universal.registry import check_registry,implementations
  entries=implementations();entries['boss-crota']={**entries['boss-crota'],'status':'implemented-user-approved'}
  with patch('universal.registry.implementations',return_value=entries):
   with self.assertRaisesRegex(ValueError,'approval'):check_registry()
  with self.assertRaises(ValueError):load('boss-riven')
  with patch('universal.providers.implementations',return_value={'boss-riven':{'provider':'universal','module':'universal.crota'}}):
   with self.assertRaisesRegex(ValueError,'identity'):load('boss-riven')
 def test_batch_keeps_missing_models_and_requires_prototype_opt_in(self):
  from universal.batch import plan
  standard=plan();extended=plan(True)
  self.assertEqual(len(standard['jobs']),10);self.assertEqual(len(extended['jobs']),33)
  self.assertTrue(any(x['id']=='boss-crota' for x in standard['backlog']));self.assertTrue(any(x['id']=='boss-riven' for x in extended['backlog']))
  self.assertTrue(all(j['lod']==0 for j in extended['jobs']))
 def test_arena_has_specific_oversoul_and_architecture(self):
  d=crota.arena();self.assertTrue(any('oversoul-latitude' in o['id'] for o in d['objects']));self.assertTrue(any('vault-rib' in o['id'] for o in d['objects']));self.assertTrue(any('rail-' in o['id'] for o in d['objects']));self.assertEqual(d['objects'],crota.arena(quality='draft')['objects'])
