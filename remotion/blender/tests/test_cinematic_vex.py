"""Public compatibility, independent LOD and grounded random-access animation invariants."""
from pathlib import Path
import copy,math,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from characters.vex_bosses import generate,generate_v090,pose,pose_v090
from cinematic_vex.animation import solve_leg
from venus_vault.request import select,validate,BINDINGS
from venus_vault.design import generate_design
from venus_vault.camera import camera_pose,PRESETS


class CinematicVexTests(unittest.TestCase):
    def test_explicit_lod_changes_detail_not_identity(self):
        for boss in ['boss-atheon','boss-templar']:
            models=[generate(boss,lod=x) for x in range(3)]
            counts=[len(s['objects']) for s in models]
            self.assertTrue(counts[0]>counts[1]>counts[2]>100)
            self.assertGreater(counts[0],1000)
            self.assertEqual([j['id'] for j in models[0]['joints']],[j['id'] for j in models[2]['joints']])
            for s in models:self.assertTrue(any('great-eye' in o['id'] or 'single-eye' in o['id'] for o in s['objects']))

    def test_geometry_independent_of_quality_and_preview_resolution(self):
        for boss in BINDINGS['bosses']:
            lo=generate_design(select(boss,quality='draft',width=320,height=240,lod=0))
            hi=generate_design(select(boss,quality='cinematic',width=1920,height=1080,lod=0))
            for a,b in zip(lo[:2],hi[:2]):
                self.assertEqual(a['objects'],b['objects']);self.assertEqual(a['joints'],b['joints'])

    def test_new_anatomy_is_not_the_old_generic_minotaur(self):
        new=generate();old=generate_v090()
        self.assertGreater(new['anatomy']['thighLength'],4)
        self.assertGreater(new['anatomy']['shinLength'],4)
        self.assertGreater(len(new['objects']),10*len(old['objects']))
        self.assertTrue(any('crown-central-spire' in o['id'] for o in new['objects']))
        self.assertFalse(any(j['id'].startswith('hip') for j in generate('boss-templar')['joints']))

    def test_legacy_request_defaults_lod_without_mutating_input(self):
        r=select('boss-atheon');r.pop('lod');before=copy.deepcopy(r)
        normalized=validate(r);self.assertEqual(normalized['lod'],0);self.assertEqual(r,before)
        for lod in [-1,3,True,.5,'0',None]:
            with self.assertRaises(ValueError):validate({**r,'lod':lod})
            with self.assertRaises(ValueError):generate(lod=lod)

    def test_old_animation_names_and_new_reveal_available(self):
        for boss,old in [('boss-atheon',['idle','walk','combat','temporal']),('boss-templar',['idle','rotate','move','attack'])]:
            self.assertTrue(set(old+['reveal'])<=set(BINDINGS['bosses'][boss]['animations']))
            for clip in old+['reveal']:self.assertEqual(select(boss,animation=clip)['animation'],clip)
            for clip in old:self.assertTrue(set(pose_v090(boss,clip,13)['rotation'])<=set(pose(boss,clip,13)['rotation']))

    def test_contacts_planted_through_stance_and_feet_clear_during_swing(self):
        previous={};seen_stance=seen_swing=False
        for f in range(96):
            p=pose('boss-atheon','walk',f,24)
            for n,c in p['contacts'].items():
                if c['stance']:
                    self.assertAlmostEqual(c['soleZ'],1.25);seen_stance=True
                    old=previous.get(n)
                    if old and old['stance']:self.assertEqual(c['ankle'],old['ankle'])
                else:self.assertGreaterEqual(c['soleZ'],1.25);seen_swing=True
                previous[n]=c
            for q in p['quaternion'].values():self.assertAlmostEqual(sum(x*x for x in q),1)
        self.assertTrue(seen_stance and seen_swing)

    def test_ik_rejects_unreachable_poses_and_time_is_random_access(self):
        for target in [(0,0,-100),(0,0,0)]:
            with self.assertRaises(ValueError):solve_leg((0,0,0),target)
        for clip in BINDINGS['bosses']['boss-atheon']['animations']:
            a=pose('boss-atheon',clip,37);pose('boss-atheon',clip,4)
            self.assertEqual(a,pose('boss-atheon',clip,37))
        with self.assertRaises(ValueError):pose('boss-atheon','walk',0,True)
        self.assertEqual(pose('boss-atheon','walk',24,24),pose('boss-atheon','walk',30,30))

    def test_reveal_and_temporal_effects_are_controllable(self):
        a=pose('boss-atheon','temporal',0);b=pose('boss-atheon','temporal',45)
        self.assertNotEqual(a['scale']['energy'],b['scale']['energy'])
        self.assertNotEqual(a['rotation']['shoulder-upperL'],b['rotation']['shoulder-upperL'])
        a=camera_pose('arena-glass-throne','ground-reveal',0);b=camera_pose('arena-glass-throne','ground-reveal',120)
        self.assertGreater(b['target'][2],a['target'][2]+10)
        self.assertEqual(a['lens'],b['lens'])
        self.assertTrue({'front','profile','low-angle','orbit','mechanism','temporal'}<=set(PRESETS))

if __name__=='__main__':unittest.main()
