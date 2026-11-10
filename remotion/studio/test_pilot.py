import hashlib,json,math,pathlib,sys,unittest,wave
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from production import ROOT,validate,smoke_config
from pilot import check_script,scene_config,timed_scene,subtitle_text
FOLDER=ROOT/'episodes/atheon-explained-en'
class EnglishPilot(unittest.TestCase):
 def test_languages_are_explicit_and_voice_pairs_cannot_cross(self):
  script=check_script(json.loads((FOLDER/'script.json').read_text()));c=scene_config(script,script['scenes'][0]);self.assertEqual(c['language'],'en-US');self.assertEqual(c['voice'],'af_heart');self.assertEqual(smoke_config(c)['narration'],'Meet this boss.')
  c['voice']='ff_siwis'
  with self.assertRaises(ValueError):validate(c)
  c.update(language='fr-FR',voice='ff_siwis',narration='Voici ce boss.');self.assertEqual(validate(c)['language'],'fr-FR');self.assertEqual(smoke_config(c)['narration'],'Voici ce boss.')
 def test_supplied_script_preserved_and_only_lore_corrections_applied(self):
  initial=json.loads((FOLDER/'script-supplied.json').read_text());reviewed=json.loads((FOLDER/'script.json').read_text());self.assertEqual(len(initial['scenes']),6)
  changed=[a['id'] for a,b in zip(initial['scenes'],reviewed['scenes']) if a['narration']!=b['narration']];self.assertEqual(changed,['04-time','06-mystery'])
  self.assertEqual([s['label'] for s in initial['scenes']],[s['label'] for s in reviewed['scenes']]);self.assertEqual(initial['title'],reviewed['title'])
 def test_real_audio_and_word_timings_produce_continuous_vertical_plan(self):
  script=check_script(json.loads((FOLDER/'script.json').read_text()));out=FOLDER/'audio-evidence';plan=json.loads((out/'timing.json').read_text());start=0
  for scene,record in zip(script['scenes'],plan['scenes']):
   folder=out/scene['id'];speech=json.loads((folder/'speech.json').read_text())
   self.assertEqual(hashlib.sha256((folder/'speech.wav').read_bytes()).hexdigest(),speech['sha256']);self.assertEqual(speech['locale'],'en-US');self.assertEqual(speech['kokoro']['speed'],1.0);self.assertEqual(speech['alignment'],'kokoro-predicted-phoneme-durations')
   self.assertEqual([w['text'] for w in speech['words']],scene['narration'].split())
   with wave.open(str(folder/'speech.wav')) as audio:self.assertAlmostEqual(audio.getnframes()/audio.getframerate(),speech['seconds'])
   self.assertEqual(record,timed_scene(scene,speech,30,start));self.assertGreaterEqual(record['durationFrames']/30,speech['seconds']);start+=record['durationFrames']
   config=validate(json.loads((folder/'selection.json').read_text()));self.assertEqual(config['sceneLabel'],scene['label']);self.assertEqual(config['title'],script['title'] if start==record['durationFrames'] else '')
  self.assertEqual((out/'subtitles.en.srt').read_text(),subtitle_text(plan['scenes']));self.assertEqual(len((out/'subtitles.en.srt').read_text().strip().split('\n\n')),sum(len(s['words']) for s in plan['scenes']))
  self.assertEqual(start,plan['durationFrames']);self.assertAlmostEqual(start/30,plan['durationSeconds']);self.assertTrue(85<=start/30<=95);self.assertFalse(plan['fullEpisodeRendered']);self.assertEqual(plan['format'],dict(width=1080,height=1920,fps=30))
 def test_evidence_and_source_bindings(self):
  out=FOLDER/'audio-evidence';proof=json.loads((out/'evidence.json').read_text())
  for name,sha in proof['files'].items():self.assertEqual(hashlib.sha256((out/name).read_bytes()).hexdigest(),sha)
  lock=json.loads((out/'script-lock.json').read_text());self.assertEqual(lock['scriptSha256'],hashlib.sha256((FOLDER/'script.json').read_bytes()).hexdigest());self.assertFalse(proof['fullEpisodeRendered'])
