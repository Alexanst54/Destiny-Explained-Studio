"""Standalone Colab/CLI production. No Actions, historical composition or model changes."""
import argparse,fcntl,hashlib,importlib.util,json,math,os,shutil,subprocess,sys,time,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'remotion/blender'))
from universal.registry import index,implementations
from universal.request import request,VIEWS
from universal.cache import atomic_json,valid_png,source_hashes
VERSION=1
LANGUAGES={'fr-FR':dict(kokoro='f',alignment='fr',voices=['ff_siwis'],smoke='Voici ce boss.'),'en-US':dict(kokoro='a',alignment='en',voices=['af_heart'],smoke='Meet this boss.')}
VOICES=[v for x in LANGUAGES.values() for v in x['voices']]
RESOLUTIONS={'Preview':(320,240),'SD':(640,360),'HD':(1280,720),'Full HD':(1920,1080),'Portrait':(1080,1920)}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def options():
 return [{**e,'cameras':implementations()[e['id']].get('views',list(VIEWS[:-2]))} for e in index()['entities'] if e['kind']=='boss' and e['implementation']]
def validate(config):
 c=dict(config);model=next((e for e in options() if e['id']==c.get('boss')),None)
 if not model:raise ValueError('Boss non implémenté : aucun modèle de remplacement.')
 if c.get('camera') not in model['cameras']:raise ValueError('Caméra incompatible avec ce boss.')
 c.setdefault('language','fr-FR')
 if c['language'] not in LANGUAGES or c.get('voice') not in LANGUAGES[c['language']]['voices']:raise ValueError('Unsupported language/voice combination.')
 if not isinstance(c.get('narration'),str) or not c['narration'].strip():raise ValueError('Enter narration in the selected language.')
 if type(c.get('duration')) not in [int,float] or not math.isfinite(c['duration']) or not 2<=c['duration']<=600:raise ValueError('Durée attendue : 2 à 600 secondes.')
 if type(c.get('subtitles')) is not bool:raise ValueError('Sous-titres : booléen requis.')
 if c.get('music') and not c.get('musicCredit'):raise ValueError('Indiquez la provenance ou licence de votre musique.')
 for key in ['width','height','fps']:
  if type(c.get(key)) is not int:raise ValueError('Dimensions/FPS invalides.')
 if c['width']%2 or c['height']%2:raise ValueError('Les dimensions H.264 doivent être paires.')
 frames=round(c['duration']*c['fps']);c['duration']=frames/c['fps'];c['frames']=frames
 request(c['boss'],quality=c['quality'],lod=0,frames=min(120,frames),fps=c['fps'],width=c['width'],height=c['height'],animation=c['animation'],view=c['camera'],arena=c['arena'])
 if frames>18000:raise ValueError('Maximum : 18000 frames.')
 return c

def smoke_config(config):
 c=dict(config);scale=max(320/c['width'],240/c['height'])
 c.update(duration=2,width=math.ceil(c['width']*scale/2)*2,height=math.ceil(c['height']*scale/2)*2,narration=LANGUAGES[c.get('language','fr-FR')]['smoke'],quality='draft',music='',musicCredit='')
 return c

def chunks(c):
 return [dict(start=start,frames=min(120,c['frames']-start)) for start in range(0,c['frames'],120)]

def run_command(cmd,log,progress=None):
 log=Path(log);log.parent.mkdir(parents=True,exist_ok=True)
 with log.open('a') as stream:
  process=subprocess.Popen([str(x) for x in cmd],cwd=ROOT/'remotion',stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
  try:
   while process.poll() is None:
    if progress:progress()
    time.sleep(2)
  except BaseException:
   import signal
   os.killpg(process.pid,signal.SIGTERM);process.wait(timeout=30);raise
  if process.returncode:raise RuntimeError(f'Échec ({process.returncode}). Consultez {log}. Corrigez la cause puis relancez la même étape ; les frames valides seront conservées.')

def speech_chunks(text,limit=180):
 import re
 words=text.split();chunks=[];current=''
 for word in words:
  if len(word)>limit:raise ValueError('Mot trop long pour la synthèse ; reformulez le texte.')
  candidate=(current+' '+word).strip()
  if len(candidate)>limit:chunks.append(current);current=word
  else:current=candidate
 if current:chunks.append(current)
 return chunks

def narration(c,folder):
 """Reuse pinned existing Kokoro loader; French has real multilingual forced alignment."""
 import numpy as np,soundfile as sf
 sys.path.insert(0,str(ROOT/'remotion/scripts'));from narration import KokoroProvider,words_from_tokens,SAMPLE_RATE
 cfg=json.loads((ROOT/'remotion/config/narration.json').read_text())['kokoro'];locale=c.get('language','fr-FR');language=LANGUAGES[locale];cfg.update(language=language['kokoro'],voice=c['voice'],threads=2,speed=1.0)
 key=hashlib.sha256(json.dumps([c['narration'],cfg,sha(__file__)],sort_keys=True).encode()).hexdigest();audio=folder/'speech.wav';meta=folder/'speech.json'
 if meta.exists() and audio.exists():
  saved=json.loads(meta.read_text())
  if saved['key']==key and saved['sha256']==sha(audio):return saved
 print('Kokoro narration: '+locale+' (model download on first use)...',flush=True)
 provider=KokoroProvider(cfg);parts=[];native_words=[];offset=0
 for chunk in speech_chunks(c['narration']):
  if locale=='en-US':
   chunk_audio,words=provider.synthesize(chunk);parts.append(chunk_audio);native_words.extend(dict(text=w['text'],start=w['start']+offset,end=w['end']+offset) for w in words);offset+=len(chunk_audio)/SAMPLE_RATE;continue
  phonemes,_=provider.pipeline.g2p(chunk)
  if not phonemes or len(phonemes)>510:raise ValueError('Segment phonétique incompatible ; reformulez le texte. Aucune troncature autorisée.')
  for result in provider.pipeline(chunk,voice=provider.voice,speed=1.0,split_pattern=None):
   if result.audio is None or len(result.phonemes)>=510:raise ValueError('Synthèse absente ou potentiellement tronquée.')
   parts.append(result.audio.detach().cpu().numpy().astype(np.float32))
 if not parts:raise ValueError('Narration vide.')
 samples=np.concatenate(parts)
 if not np.isfinite(samples).all() or np.max(np.abs(samples))<1e-5:raise ValueError('Parole invalide ou silencieuse.')
 if np.max(np.abs(samples))>.98:samples*=.98/np.max(np.abs(samples))
 sf.write(audio,samples,SAMPLE_RATE,subtype='PCM_16')
 if locale=='en-US':
  words=native_words;method=provider.method
 else:
  print('Alignement français sur la parole réelle...',flush=True)
  import stable_whisper
  aligned=stable_whisper.load_model('base',device='cpu',download_root=str(Path(os.environ.get('DESTINY_MODEL_CACHE',str(folder.parent/'model-cache')))/'whisper')).align(str(audio),c['narration'],language='fr')
  if aligned is None:raise ValueError('Alignement français impossible ; aucune légende estimée ne sera inventée.')
  tokens=[dict(text=w['word'],start=w['start'],end=w['end']) for s in aligned.to_dict()['segments'] for w in s['words']]
  words=words_from_tokens(c['narration'],tokens,len(samples)/SAMPLE_RATE);method='stable-ts multilingual base / French forced alignment'
 result=dict(key=key,sha256=sha(audio),seconds=len(samples)/SAMPLE_RATE,words=words,voice=c['voice'],language=language['alignment'],locale=locale,alignment=method,kokoro=cfg)
 atomic_json(meta,result);return result

def prepare(config,folder):
 c=validate(config);folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=True)
 manifest=folder/'project.json';identity=dict(version=VERSION,config=c,studioSources={p.name:sha(p) for p in [Path(__file__),Path(__file__).with_name('index.tsx'),Path(__file__).with_name('captions.ts')]},rendererSources=source_hashes())
 if manifest.exists():
  saved=json.loads(manifest.read_text())
  if any(saved.get(k)!=v for k,v in identity.items()):raise ValueError('Projet/source modifié : restaurez le commit enregistré, ou choisissez un nouveau dossier Drive. Ne mélangez pas les caches.')
  identity=saved
 else:
  identity['sourceCommit']=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
  identity['sourceDirty']=bool(subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain','--','remotion/studio','remotion/blender'],text=True).strip())
 atomic_json(manifest,identity);return c,folder

def render(c,folder,blender,node='node',chrome=None):
 atomic_json(folder/'validation.json',dict(status='running'))
 speech=narration(c,folder)
 if speech['seconds']>c['duration']:raise ValueError(f"Narration de {speech['seconds']:.2f}s > vidéo de {c['duration']:.2f}s. Augmentez la durée dans un nouveau projet, ou raccourcissez le texte. Aucune parole ne sera coupée.")
 public=folder/'public';(public/'frames').mkdir(parents=True,exist_ok=True)
 import numpy as np,soundfile as sf
 audio,sr=sf.read(folder/'speech.wav',dtype='float32');padded=np.zeros(round(c['duration']*sr),dtype=np.float32);padded[:len(audio)]=audio;sf.write(public/'narration.wav',padded,sr,subtype='PCM_16')
 if c.get('music'):
  music=Path(c['music']);music_hash=sha(music);saved=folder/'music-source.json'
  if saved.exists() and json.loads(saved.read_text())['sha256']!=music_hash:raise ValueError('La musique a changé ; choisissez un nouveau projet.')
  atomic_json(saved,dict(sha256=music_hash,credit=c['musicCredit']));shutil.copyfile(music,public/'music-input')
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(public/'music-input'),str(public/'music.wav')],check=True)
 reports=[]
 for part in chunks(c):
  out=folder/'blender'/f"chunk-{part['start']:06d}";start=part['start']
  def progress():
   p=out/'progress.json'
   if not p.exists():return
   try:r=json.loads(p.read_text())
   except json.JSONDecodeError:return
   conf=r.get('configuration',{});frames=list(r.get('frames',{}).values());seconds=[f['seconds'] for f in frames if 'seconds' in f];mean=sum(seconds)/len(seconds) if seconds else None
   text=f"{start+len(frames)}/{c['frames']} frames | {conf.get('selected','détection')} {conf.get('backend') or ''} | ETA {(c['frames']-start-len(frames))*mean/60:.1f} min" if mean else f"{start+len(frames)}/{c['frames']} frames | détection backend / première frame"
   if conf.get('selected')=='CPU':text+=' | ATTENTION : repli CPU, rendu potentiellement long.'
   if getattr(progress,'last',None)!=text:print(text,flush=True);progress.last=text
  cmd=[sys.executable,ROOT/'remotion/blender/render_universal.py',c['boss'],out,'--blender',blender,'--frames',part['frames'],'--start-frame',start,'--fps',c['fps'],'--width',c['width'],'--height',c['height'],'--quality',c['quality'],'--lod',0,'--view',c['camera'],'--animation',c['animation'],'--arena',c['arena'],'--timeout',7200]
  if out.exists():cmd+=['--resume']
  run_command(cmd,folder/'logs/blender.log',progress);r=json.loads((out/'progress.json').read_text());reports.append(r)
  for local in range(part['frames']):
   f=r['frames'][str(local)];source=out/f['file'];target=public/'frames'/f'frame-{start+local:06d}.png'
   if f['sourceFrame']!=start+local or not valid_png(source,c['width'],c['height'],f['sha256']):raise ValueError('Frame Blender invalide.')
   if not valid_png(target,c['width'],c['height'],f['sha256']):shutil.copyfile(source,target)
 props=dict(width=c['width'],height=c['height'],fps=c['fps'],frames=c['frames'],words=speech['words'],subtitles=c['subtitles'],music=bool(c.get('music')),title=c.get('title',''),sceneLabel=c.get('sceneLabel',''));atomic_json(folder/'props.json',props)
 output=folder/'video.mp4';pending=folder/'pending.mp4';cmd=[node,ROOT/'remotion/node_modules/@remotion/cli/remotion-cli.js','render',ROOT/'remotion/studio/index.tsx','DestinyProductionStudio',pending,'--props',folder/'props.json','--public-dir',public,'--codec','h264','--audio-codec','aac','--pixel-format','yuv420p','--image-format','png','--color-space','bt709','--concurrency','1']
 if chrome:cmd+=['--browser-executable',chrome]
 run_command(cmd,folder/'logs/remotion.log');proof=verify(pending,c);pending.replace(output)
 proof.update(status='passed',sha256=sha(output),speechSeconds=speech['seconds'],alignedWords=len(speech['words']),backends=[r['configuration'] for r in reports],gpuValidated=all(f['device']['selected']=='GPU' for r in reports for f in r['frames'].values()))
 atomic_json(folder/'validation.json',proof);print('Terminé : '+str(output),flush=True);return proof

def verify(video,c):
 data=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]));v=next(s for s in data['streams'] if s['codec_type']=='video');a=next((s for s in data['streams'] if s['codec_type']=='audio'),None)
 from fractions import Fraction
 if v['codec_name']!='h264' or v['pix_fmt']!='yuv420p' or int(v['nb_read_frames'])!=c['frames'] or Fraction(v['avg_frame_rate'])!=c['fps'] or (v['width'],v['height'])!=(c['width'],c['height']):raise ValueError('Export vidéo incorrect (codec, FPS, résolution ou frames).')
 if a is None or a['codec_name']!='aac':raise ValueError('Piste AAC absente.')
 for duration in [float(v['duration']),float(a['duration']),float(data['format']['duration'])]:
  if abs(duration-c['duration'])>max(.12,2/c['fps']):raise ValueError('Durée vidéo/audio incohérente.')
 subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
 import array
 pcm=array.array('h',subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-map','0:a:0','-ac','1','-ar','24000','-f','s16le','-']))
 if not pcm or max(abs(x) for x in pcm)<32:raise ValueError('Audio final silencieux.')
 return dict(duration=float(v['duration']),frames=int(v['nb_read_frames']),fps=c['fps'],videoCodec=v['codec_name'],audioCodec=a['codec_name'],width=v['width'],height=v['height'])

def main():
 p=argparse.ArgumentParser();p.add_argument('config');p.add_argument('output');p.add_argument('--blender',default='blender');p.add_argument('--node',default='node');p.add_argument('--chrome');p.add_argument('--smoke',action='store_true');a=p.parse_args();config=json.loads(Path(a.config).read_text());folder=Path(a.output).resolve()
 if a.smoke:config=smoke_config(validate(config));folder=folder/'smoke'
 else:
  proof=folder/'smoke/validation.json';project=folder/'smoke/project.json'
  if not proof.exists() or json.loads(proof.read_text()).get('status')!='passed' or not project.exists():raise ValueError('Exécutez le smoke-test avant la production complète.')
  old=json.loads(project.read_text())['config'];prepare(old,folder/'smoke');verify(folder/'smoke/video.mp4',old)
  if sha(folder/'smoke/video.mp4')!=json.loads(proof.read_text())['sha256']:raise ValueError('Smoke-test corrompu : relancez-le.')
  if any(old[k]!=config[k] for k in ['boss','arena','animation','camera']):raise ValueError('La sélection a changé ; un nouveau smoke-test est requis.')
 folder.mkdir(parents=True,exist_ok=True)
 with (folder/'production.lock').open('a') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise ValueError('Ce projet est déjà en cours de production.')
  c,folder=prepare(config,folder)
  try:render(c,folder,a.blender,a.node,a.chrome)
  except BaseException as error:
   atomic_json(folder/'validation.json',dict(status='failed',error=str(error)));raise
if __name__=='__main__':main()
