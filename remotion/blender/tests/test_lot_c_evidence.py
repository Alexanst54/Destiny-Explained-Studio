"""Reject substituted identities, geometry, motion and incomplete real-render reports."""
import copy,json,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from universal.lot_c_evidence import ROOT,validate_report
from universal.lot_c_render import plan

class LotCEvidence(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.report=json.loads((ROOT/'docs/universal-library/lot-c/oryx/front-report.json').read_text())
  cls.job=next(j for j in plan() if j['slug']=='oryx' and j['name']=='front')
 def reject(self,edit):
  report=copy.deepcopy(self.report);edit(report)
  with self.assertRaises(ValueError):validate_report(report,self.job)
 def test_genuine_shipped_render_matches_authored_scene(self):
  self.assertTrue(validate_report(self.report,self.job))
 def test_substituted_boss_arena_or_geometry_is_rejected(self):
  self.reject(lambda r:r['request']['binding'].update(selectionId='boss-rhulk'))
  self.reject(lambda r:r['request']['binding'].update(environmentId='root-of-nightmares'))
  self.reject(lambda r:r['configuration'].update(bossDesignSha256='0'*64))
  self.reject(lambda r:r['configuration'].update(designSha256='0'*64))
 def test_wrong_animation_camera_or_source_is_rejected(self):
  self.reject(lambda r:r['frames']['0'].update(poseSha256='0'*64))
  self.reject(lambda r:r['frames']['0']['cameraSettings'].update(lens=2))
  self.reject(lambda r:r['frames']['0']['cameraMatrix'][0].__setitem__(3,999))
  self.reject(lambda r:r['sources'].update({'remotion/blender/universal/oryx.py':'0'*64}))
 def test_partial_frames_wrong_lod_or_samples_are_rejected(self):
  self.reject(lambda r:r.update(status='running'))
  self.reject(lambda r:r['frames'].clear())
  self.reject(lambda r:r['configuration'].update(lod=2))
  self.reject(lambda r:r['configuration'].update(samples=16))
