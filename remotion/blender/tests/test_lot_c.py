import hashlib,json,math,pathlib,random,subprocess,sys,unittest
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from universal.registry import ROOT,resolve,implementations
from universal.providers import load
from universal.request import request,validate
from venus_vault.geometry import digest
NAMES=('oryx','rhulk','nezarec')
ARENAS=('arena-threshold','vow-of-disciple','root-of-nightmares')
class LotC(unittest.TestCase):
 def test_canonical_arena_activity_bindings(self):
  for name,arena in zip(NAMES,ARENAS):
   r=resolve('boss-'+name);self.assertEqual(r['environmentId'],arena);self.assertTrue(r['entity']['encounterIds']);self.assertTrue(r['entity']['activityIds']);self.assertEqual(r['status'],'partial-dedicated-prototype')
   self.assertEqual(resolve(arena)['provider'],'universal')
  with self.assertRaises(ValueError):resolve('boss-oryx',variant_id='boss-oryx-variant-shade')
  with self.assertRaises(ValueError):resolve('boss-rhulk',arena_id='root-of-nightmares')
 def test_no_cross_boss_provider_impersonation(self):
  for a in NAMES:
   m=load('boss-'+a);self.assertEqual(m.generate.__module__,'universal.'+a)
   for b in NAMES:
    if a==b:continue
    with patch('universal.providers.implementations',return_value={'boss-'+a:{'provider':'universal','module':'universal.'+b}}):
     with self.assertRaisesRegex(ValueError,'identity'):load('boss-'+a)
  for missing in ['boss-riven','boss-witness','boss-oryx-variant-shade']:
   with self.assertRaises(ValueError):resolve(missing,allow_family_study=True)
 def test_lods_quality_and_determinism(self):
  for name in NAMES:
   m=load('boss-'+name);models=[m.generate(lod=l) for l in range(3)];arenas=[m.arena(lod=l) for l in range(3)]
   for specs in [models,arenas]:self.assertGreater(len(specs[0]['objects']),len(specs[1]['objects']));self.assertGreater(len(specs[1]['objects']),len(specs[2]['objects']))
   self.assertEqual(models[0]['objects'],m.generate(quality='draft')['objects']);self.assertEqual(arenas[0]['objects'],m.arena(quality='draft')['objects']);self.assertEqual(models[0]['joints'],models[2]['joints'])
   random.seed(349);self.assertEqual(digest(models[0]),digest(m.generate()));self.assertNotEqual(digest(models[0]),digest(m.generate(seed=43)))
   for lod in [True,-1,3]:
    with self.assertRaises(ValueError):m.generate(lod=lod)
 def test_rigs_materials_and_finite_original_geometry(self):
  for name in NAMES:
   m=load('boss-'+name);d=m.generate();ids=[o['id'] for o in d['objects']];self.assertEqual(len(ids),len(set(ids)));seen=set()
   for j in d['joints']:
    self.assertNotIn(j['id'],seen)
    if j['parent']:self.assertIn(j['parent'],seen)
    seen.add(j['id'])
   for o in d['objects']:
    self.assertTrue(all(math.isfinite(x) for x in o['position']+o['size']+o['rotation']));self.assertTrue(all(x>0 for x in o['size']));self.assertIn(o['material'],m.MATERIALS);self.assertTrue(o['joint'] is None or o['joint'] in seen)
 def test_distinctive_landmarks_and_skeletons(self):
  required={'oryx':['torn-membrane','three-eye','crown-transverse','willbreaker','wing-spar'],'rhulk':['six-eye','long-femur','flared-collar','lubrae-blade','ankle-cuff'],'nezarec':['seven-eye','heavy-red-thorax','swept-horn','night-terror-crescent','asymmetric-pauldron']}
  skeletons=[]
  for name in NAMES:
   d=load('boss-'+name).generate();ids=[o['id'] for o in d['objects']]
   for word in required[name]:self.assertTrue(any(word in i for i in ids),word)
   skeletons.append({j['id'] for j in d['joints']})
  for i in range(3):
   for j in range(i):self.assertNotEqual(skeletons[i],skeletons[j])
 def test_all_animation_modes_are_articulated_and_random_access(self):
  for name in NAMES:
   m=load('boss-'+name);joints={j['id'] for j in m.generate()['joints']}
   for mode in ['idle','move','combat','signature','reveal']:
    a=m.pose(mode,0);b=m.pose(mode,18);m.pose(mode,41);self.assertEqual(b,m.pose(mode,18));self.assertEqual(m.pose(mode,24,24),m.pose(mode,30,30));self.assertNotEqual(a,b)
    changed={k for k in set(a['rotation'])|set(b['rotation']) if a['rotation'].get(k)!=b['rotation'].get(k)}
    self.assertTrue(changed-{'root','ritual','resonance','nightmare'})
    for field in ['rotation','position','scale']:
     self.assertTrue(set(b[field])<=joints);self.assertTrue(all(math.isfinite(x) for v in b[field].values() for x in v))
    self.assertGreater(b['emissionPulse'],0)
   with self.assertRaises(ValueError):m.pose('idle',-1)
 def test_true_profile_and_three_quarter_views(self):
  for name in NAMES:
   m=load('boss-'+name);front=m.camera('front');profile=m.camera('profile');three=m.camera('three-quarter')
   self.assertEqual(front['position'][0],0);self.assertEqual(profile['position'][1],12);self.assertAlmostEqual(three['position'][0],12-three['position'][1]);self.assertNotEqual(front,m.camera('cinematic'));self.assertNotEqual(front,m.camera('environment'))
   self.assertEqual(validate(request('boss-'+name,view='profile')),request('boss-'+name,view='profile'))
  with self.assertRaises(ValueError):request('boss-crota',view='profile')
  with self.assertRaises(ValueError):request('boss-atheon',view='cinematic')
 def test_preservation_of_prior_models_and_evidence(self):
  p=json.loads((ROOT/'docs/universal-library/lot-c/preservation.json').read_text())
  for path,sha in p['protected'].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),sha,path)
  old=json.loads(subprocess.check_output(['git','show',p['base']+':remotion/blender/universal/models.json'],text=True));current=implementations()
  for k,v in old.items():self.assertEqual(current[k],v,k)
 def test_new_batch_views_remain_explicit_prototypes(self):
  from universal.batch import plan
  p=plan(True)
  for name in NAMES:
   jobs=[j for j in p['jobs'] if j['selection']=='boss-'+name];self.assertEqual(len(jobs),6);self.assertEqual({j['view'] for j in jobs},{'front','profile','three-quarter','cinematic','environment'});self.assertTrue(all(j['lod']==0 and j['modelStatus'].startswith('partial') for j in jobs))
