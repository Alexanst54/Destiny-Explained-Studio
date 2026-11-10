"""Offline evidence verification. No Actions, TTS model download or Blender launch."""
import hashlib,json,pathlib,subprocess,sys,wave
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from production import ROOT,validate,verify
folder=ROOT/'docs/production-studio/smoke'
proof=json.loads((folder/'evidence.json').read_text())
for name,sha in proof['files'].items():
 if hashlib.sha256((folder/name).read_bytes()).hexdigest()!=sha:raise ValueError('Evidence changed: '+name)
c=validate(json.loads((folder/'selection.json').read_text()));verify(folder/'video.mp4',c);verify(folder/'music-no-captions.mp4',c)
speech=json.loads((folder/'speech.json').read_text())
assert hashlib.sha256((folder/'speech.wav').read_bytes()).hexdigest()==speech['sha256']
with wave.open(str(folder/'speech.wav')) as audio:assert audio.getframerate()==24000 and abs(audio.getnframes()/24000-speech['seconds'])<1e-6
assert speech['language']=='fr' and speech['voice']=='ff_siwis' and all(0<=w['start']<w['end']<=speech['seconds'] for w in speech['words'])
resume=json.loads((folder/'resume-proof.json').read_text());assert resume['cacheHits']==48 and resume['newFrames']==0 and resume['narrationCacheReused']
data=subprocess.check_output(['ffmpeg','-v','error','-i',str(folder/'video.mp4'),'-map','0:v:0','-f','framemd5','-']).decode();hashes=[x.rsplit(',',1)[-1] for x in data.splitlines() if x and not x.startswith('#')];assert len(hashes)==48 and len(set(hashes))>20
assert proof['gpuValidated'] is False
print('Verified actual French Kokoro/Blender/Remotion H.264/AAC smoke and music/subtitles-off variant; CPU only.')
