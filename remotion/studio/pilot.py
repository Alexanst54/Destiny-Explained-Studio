"""Speech-first six-scene English pilot preparation. Default mode never renders images."""
import argparse,hashlib,json,math,sys
from pathlib import Path
from production import ROOT,atomic_json,narration,sha,validate

def check_script(script):
 if script['id']!='atheon-explained-en' or script['language']!='en-US' or script['voice']!='af_heart':raise ValueError('Pilot identity/language/voice mismatch.')
 if script['boss']!='boss-atheon' or script['arena']!='arena-glass-throne':raise ValueError('Pilot must bind Atheon to the Glass Throne.')
 if script['targetDurationSeconds']!=[85,95]:raise ValueError('Pilot target must remain 85–95 seconds.')
 if script['title']!="Who Is Atheon, Time's Conflux?":raise ValueError('Unexpected pilot title.')
 if script['format']!={'width':1080,'height':1920,'fps':30}:raise ValueError('Pilot requires vertical 9:16 at 30 FPS.')
 if len(script['scenes'])!=6 or len({s['id'] for s in script['scenes']})!=6:raise ValueError('Six distinct scenes required.')
 for s in script['scenes']:
  if not s['narration'].strip() or not s['label'].strip():raise ValueError('Missing supplied English narration or scene label.')
 return script

def scene_config(script,scene,seconds=2):
 return validate(dict(boss=script['boss'],arena=script['arena'],language='en-US',voice='af_heart',narration=scene['narration'],title=script['title'] if scene['id']==script['scenes'][0]['id'] else '',sceneLabel=scene['label'],quality='balanced',duration=seconds,subtitles=True,width=script['format']['width'],height=script['format']['height'],fps=script['format']['fps'],animation=scene['animation'],camera=scene['camera'],music='',musicCredit=''))

def timed_scene(scene,speech,fps,start,pad=.25):
 frames=math.ceil((speech['seconds']+pad)*fps)
 if any(w['start']<0 or w['end']>speech['seconds'] or w['end']<=w['start'] for w in speech['words']):raise ValueError('Invalid actual speech timing.')
 return dict(id=scene['id'],label=scene['label'],startFrame=start,durationFrames=frames,speechSeconds=speech['seconds'],tailSeconds=frames/fps-speech['seconds'],words=[dict(text=w['text'],start=w['start']+start/fps,end=w['end']+start/fps) for w in speech['words']])

def subtitle_text(scenes):
 def stamp(seconds):
  ms=round(seconds*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);sec,ms=divmod(ms,1000)
  return f'{h:02d}:{m:02d}:{sec:02d},{ms:03d}'
 words=[w for scene in scenes for w in scene['words']]
 return '\n'.join(f"{i}\n{stamp(w['start'])} --> {stamp(w['end'])}\n{w['text']}\n" for i,w in enumerate(words,1))

def prepare_audio(path,folder):
 script=check_script(json.loads(Path(path).read_text()));folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=True)
 identity=dict(scriptSha256=sha(path),narratorSha256=sha(ROOT/'remotion/studio/production.py'),plannerSha256=sha(__file__))
 lock=folder/'script-lock.json'
 if lock.exists() and json.loads(lock.read_text())!=identity:raise ValueError('Script/source changed; use a new pilot folder.')
 atomic_json(lock,identity);fps=script['format']['fps'];start=0;scenes=[]
 for scene in script['scenes']:
  out=folder/'scenes'/scene['id'];out.mkdir(parents=True,exist_ok=True);c=scene_config(script,scene)
  speech=narration(c,out);timing=timed_scene(scene,speech,fps,start);scenes.append(timing);start+=timing['durationFrames']
  atomic_json(out/'selection.json',scene_config(script,scene,timing['durationFrames']/fps))
 target=script['targetDurationSeconds'];seconds=start/fps
 result=dict(id=script['id'],title=script['title'],language='en-US',voice='af_heart',format=script['format'],durationFrames=start,durationSeconds=seconds,targetDurationSeconds=target,targetMet=target[0]<=seconds<=target[1],scenes=scenes,fullEpisodeRendered=False,speechRate=1.0,derivedFromActualSynthesis=True)
 atomic_json(folder/'timing.json',result)
 (folder/'subtitles.en.srt').write_text(subtitle_text(scenes),encoding='utf-8')
 print(json.dumps({k:result[k] for k in ['durationSeconds','targetDurationSeconds','targetMet','fullEpisodeRendered']}),flush=True)
 if not result['targetMet']:print('Script review required for the target duration. Speech was not cut or accelerated.',flush=True)
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('script');p.add_argument('output');a=p.parse_args();prepare_audio(a.script,a.output)
