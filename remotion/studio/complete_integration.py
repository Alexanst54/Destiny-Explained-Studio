"""Local six-sequence compositor test. Deliberately NOT the actual 2672-frame pilot.

Uses one actual approved Blender frame repeatedly as a TEST FIXTURE and generated
short test tones. It must never be described as a rendered pilot episode.
"""
import argparse,array,json,math,os,shutil,subprocess,sys,wave
from pathlib import Path
from complete_atheon import ROOT,atomic_json,valid_png,sha,run_task,verify,verify_audio_alignment,load_package,FPS,TOTAL_FRAMES

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('output');p.add_argument('--frame-dir',required=True);p.add_argument('--node',required=True);p.add_argument('--chrome',default='/usr/bin/chromium');a=p.parse_args();out=Path(a.output).resolve()
 if out.exists():raise ValueError('Use a new integration test folder.')
 out.mkdir(parents=True);source=Path(a.frame_dir).resolve();render=json.loads((source/'progress.json').read_text());image=source/'frame-0000.png'
 if render['status']!='success' or render['request']['binding']['selectionId']!='boss-atheon' or not valid_png(image,360,640,render['frames']['0']['sha256']):raise ValueError('A genuine validated 360×640 Blender Atheon frame is required for the fixture.')
 scenes=[];items=[]
 for index in range(6):
  scene_id=f'fixture-{index+1}';public=out/'public/scenes'/scene_id;chunk=public/'frames/chunk-000000';chunk.mkdir(parents=True)
  for frame in range(10):os.link(image,chunk/f'frame-{frame:04d}.png')
  samples=array.array('h',[int(5000*math.sin(n*(.08+index*.017))*min(1,n/600,(6000-n)/600)) for n in range(6000)])
  audio=public/'speech.wav'
  with wave.open(str(audio),'wb') as wav:wav.setparams((1,2,24000,0,'NONE','not compressed'));wav.writeframes(samples.tobytes())
  scenes.append(dict(id=scene_id,label=f'TEST FIXTURE {index+1}/6',title='COMPOSITOR TEST — NOT THE PILOT',startFrame=index*10,durationFrames=10,words=[dict(text='TEST',start=.02,end=.24)]))
  items.append(dict(scene=dict(id=scene_id),timing=dict(startFrame=index*10),audio=str(audio)))
 props=dict(width=360,height=640,fps=30,frames=60,scenes=scenes);atomic_json(out/'props.json',props)
 cmd=[str(Path(a.node).resolve()),ROOT/'remotion/node_modules/@remotion/cli/remotion-cli.js','render',ROOT/'remotion/studio/complete-index.tsx','CompleteAtheonEpisode',out/'fixture.mp4','--props',out/'props.json','--public-dir',out/'public','--codec','h264','--audio-codec','aac','--pixel-format','yuv420p','--image-format','png','--color-space','bt709','--concurrency',1,'--browser-executable',str(Path(a.chrome).resolve())]
 run_task(cmd,out/'render.log');result=verify(out/'fixture.mp4',dict(width=360,height=640,fps=30,frames=60,duration=2));result.update(status='passed',testFixture=True,fullEpisodeRendered=False,gpuValidated=False,fixtureUsesRepeatedStill=True,fixtureAudio='generated tones, not pilot narration',audioAlignment=verify_audio_alignment(out/'fixture.mp4',items),sourceBlenderFrameSha256=sha(image));atomic_json(out/'test-result.json',result)
 # Audio-only check of all six ORIGINAL utterances at the measured frame offsets.
 package=load_package();pcm=array.array('h',[0])*(TOTAL_FRAMES*800)
 for item in package['scenes']:
  with wave.open(item['audio']) as wav:part=array.array('h',wav.readframes(wav.getnframes()))
  start=item['timing']['startFrame']*800;pcm[start:start+len(part)]=part
 original=out/'original-six-scene-audio.wav'
 with wave.open(str(original),'wb') as wav:wav.setparams((1,2,24000,0,'NONE','not compressed'));wav.writeframes(pcm.tobytes())
 encoded=out/'original-six-scene-audio.m4a';subprocess.run(['ffmpeg','-v','error','-y','-i',str(original),'-c:a','aac',str(encoded)],check=True)
 audio_result=verify_audio_alignment(encoded,package['scenes']);audio_result.update(status='passed',audioOnly=True,fullEpisodeRendered=False,gpuValidated=False)
 atomic_json(out/'original-audio-result.json',audio_result);print(json.dumps(result),flush=True);print(json.dumps(audio_result),flush=True)
if __name__=='__main__':main()
