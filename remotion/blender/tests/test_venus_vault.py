"""Pure design and contract tests; run with system Python, no bpy dependency."""
import copy
import json
import math
from pathlib import Path
import random
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from environments import venus, vault_of_glass
from characters.vex_bosses import generate, pose
from venus_vault.camera import camera_pose, PRESETS
from venus_vault.geometry import QUALITY, digest
from venus_vault.request import BINDINGS, select, validate


class VenusVaultTests(unittest.TestCase):
    def test_deterministic_scene_and_seed_variation(self):
        for fn in [venus.generate, vault_of_glass.generate]:
            a=fn(seed=42);random.seed(100);random.random()
            self.assertEqual(a,fn(seed=42));self.assertNotEqual(digest(a),digest(fn(seed=43)))

    def test_quality_density_and_persistent_silhouettes(self):
        counts=[len(venus.generate(42,q)['objects']) for q in QUALITY]
        self.assertTrue(counts[0]<counts[1]<counts[2])
        for boss in BINDINGS['bosses']:
            ids=lambda q:[o['id'] for o in generate(boss,quality=q)['objects']]
            self.assertEqual(ids('draft'),ids('cinematic'))

    def test_distinct_sets_have_required_landmarks(self):
        templar=vault_of_glass.generate();throne=vault_of_glass.generate(arena='arena-glass-throne');v=venus.generate()
        self.assertTrue(any('/oracle-' in o['id'] for o in templar['objects']))
        self.assertTrue(any('/conflux-' in o['id'] for o in templar['objects']))
        self.assertFalse(any('/oracle-' in o['id'] for o in throne['objects']))
        self.assertTrue(any('/portal-frame-' in o['id'] for o in throne['objects']))
        self.assertTrue(any('/academy-' in o['id'] for o in v['objects']))
        self.assertTrue(any('/buried-vex-' in o['id'] for o in v['objects']))

    def test_geometry_and_parent_order(self):
        for s in [venus.generate(),vault_of_glass.generate(),vault_of_glass.generate(arena='arena-glass-throne'),generate(),generate('boss-templar')]:
            seen=set();ids=set()
            for j in s['joints']:
                self.assertNotIn(j['id'],seen);self.assertTrue(j['parent'] is None or j['parent'] in seen);seen.add(j['id'])
            for o in s['objects']:
                self.assertNotIn(o['id'],ids);ids.add(o['id'])
                self.assertTrue(o['joint'] is None or o['joint'] in seen)
                self.assertTrue(all(x>0 and math.isfinite(x) for x in o['size']))

    def test_boss_silhouettes_have_semantic_components(self):
        a=generate();t=generate('boss-templar');ids=lambda s:' '.join(o['id'] for o in s['objects'])
        for word in ['horn-','radiolaria-vessel','single-eye','foot-L','temporal-core']:self.assertIn(word,ids(a))
        for word in ['wing-','great-eye','shield-edge-','heavy-cannon']:self.assertIn(word,ids(t))
        self.assertNotIn('foot-L',ids(t))

    def test_animation_random_access_all_clips(self):
        for boss,b in BINDINGS['bosses'].items():
            joints={j['id'] for j in generate(boss)['joints']}
            for animation in b['animations']:
                p=pose(boss,animation,23);pose(boss,animation,45)
                self.assertEqual(p,pose(boss,animation,23));self.assertNotEqual(p,pose(boss,animation,0))
                self.assertTrue(set(p['rotation'])|set(p['position'])<=joints)
                self.assertTrue(all(math.isfinite(x) for v in list(p['rotation'].values())+list(p['position'].values()) for x in v))
        self.assertNotEqual(pose('boss-atheon','walk',30)['position']['root'],pose('boss-atheon','walk',0)['position']['root'])
        self.assertNotEqual(pose('boss-templar','rotate',30)['rotation']['halo'],pose('boss-templar','rotate',0)['rotation']['halo'])

    def test_camera_paths_continuous_and_finite(self):
        for env in ['venus','arena-templars-well','arena-glass-throne']:
            for camera in PRESETS:
                for frame in range(121):
                    p=camera_pose(env,camera,frame);self.assertNotEqual(p['position'],p['target'])
                    self.assertTrue(all(math.isfinite(x) for x in p['position']+p['target']))
                    if frame:self.assertLess(math.dist(p['position'],previous),1)
                    previous=p['position']

    def test_atlas_selection_resolves_existing_arena(self):
        for boss,b in BINDINGS['bosses'].items():
            r=select(boss);self.assertEqual(r['bossId'],boss);self.assertEqual(r['environmentId'],b['environmentId'])
        self.assertIsNone(select('venus')['bossId'])
        self.assertEqual(select('vault-of-glass')['environmentId'],'arena-templars-well')

    def test_reject_bad_requests(self):
        for key,value in [('seed',True),('seed',-1),('quality','ultra'),('camera','bad'),('animation','fly'),('frames',121),('frames',False),('fps',True),('width',961),('height',100),('environmentId','venus'),('bossId','boss-templar'),('version',True)]:
            r=select('boss-atheon');r[key]=value
            with self.assertRaises(ValueError,msg=key):validate(r)
        with self.assertRaises(ValueError):select('boss-riven')
        with self.assertRaises(ValueError):select('venus',animation='walk')
        with self.assertRaises(ValueError):generate('boss-riven')
        with self.assertRaises(ValueError):venus.generate(seed=True)
        with self.assertRaises(ValueError):pose('boss-atheon','attack')

if __name__=='__main__':unittest.main()
