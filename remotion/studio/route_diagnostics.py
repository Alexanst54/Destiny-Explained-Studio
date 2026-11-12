"""Identify an archived video's route from manifests, not duration or GUI estimates."""
import argparse,collections,json,math,subprocess
from pathlib import Path
from perf_common import atomic_json,digest


def inspect(source):
 source=Path(source).expanduser().resolve();folder=source if source.is_dir() else source.parent;project=None
 for parent in [folder,*folder.parents]:
  if (parent/'project.json').is_file():folder=parent;project=json.loads((parent/'project.json').read_text());break
 if project is None:raise ValueError('No project.json found. Select the Drive project containing the video, not a downloaded MP4 alone.')
 kind=project.get('identity',{}).get('kind',project.get('kind'));name=source.name
 if kind=='complete-atheon-v1':route='legacy-prepared-pilot';entry='complete_atheon.py';cell='B. Smoke-test';cinematic=False;patterns=['public/scenes/*/frames/chunk-*/progress.json']
 elif kind=='directed-atheon-v1':route='cinematic-Q';entry='cinematic_atheon.py';cell='Q1–Q4';cinematic=True;patterns=['public/scenes/*/frames/shot-*/profile.json','previews/scenes/*/frames/shot-*/profile.json']
 elif kind=='atheon-motion-test-v1':route='cinematic-motion-diagnostic';entry='motion_test.py';cell='M1–M3';cinematic=True;patterns=['renders/scenes/*/frames/*/profile.json']
 elif 'config' in project:route='legacy-general-studio';entry='production.py';cell='3. Smoke-test (2 s) or 4. Production';cinematic=False;patterns=['blender/chunk-*/progress.json']
 else:route='unknown';entry=None;cell=None;cinematic=None;patterns=[]
 paths=[]
 for pattern in patterns:paths.extend(folder.glob(pattern))
 groups=collections.defaultdict(list)
 for path in sorted(paths):
  r=json.loads(path.read_text());req=r.get('request',{});config=r.get('configuration',{});key=str((req.get('selectionId'),req.get('view'),req.get('animation')))
  for f in r.get('frames',{}).values():groups[key].append(f)
 camera=[]
 for selection,frames in groups.items():
  matrices=[f['cameraMatrix'] for f in frames if f.get('cameraMatrix')];first=matrices[0] if matrices else None
  camera.append(dict(selection=selection,recordedFrames=len(frames),recordedCameraTransforms=len(matrices),uniqueCameraTransforms=len({digest(m) for m in matrices}),maxTranslationFromFirst= max((math.sqrt(sum((m[i][3]-first[i][3])**2 for i in range(3))) for m in matrices),default=None),shotIds=sorted({f['cameraDiagnostic']['shotId'] for f in frames if f.get('cameraDiagnostic')})))
 videos=[source] if source.is_file() and source.suffix.lower()=='.mp4' else [p for p in [folder/'atheon-smoke.mp4',folder/'video.mp4',folder/'atheon-episode-01-cinematic.mp4',folder/'atheon-motion-test.mp4'] if p.is_file()]
 media=[]
 for video in videos:
  info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)],text=True));v=next(s for s in info['streams'] if s['codec_type']=='video');media.append(dict(file=video.name,decodedVideoFrames=int(v['nb_read_frames']),videoSeconds=float(v['duration']),containerSeconds=float(info['format']['duration']),fps=v['avg_frame_rate'],width=v['width'],height=v['height']))
 return dict(route=route,entrypoint=entry,notebookCell=cell,cinematic=cinematic,sourceCommit=project.get('sourceCommit'),projectKind=kind,confidence='project manifest + archived render metadata; no route inferred from duration',media=media,cameraGroups=camera,expectedPreparedPilotSmoke=dict(file='atheon-smoke.mp4',videoFrames=345,fps=30,videoSeconds=11.5,camera='environment → wide (static)'),notes=['Current Q1 prepares, Q2 renders still previews, Q3 renders image sequences and Q4 exports the full episode. It has no 11.52-second smoke export.','The current general Studio smoke uses 2 seconds / 60 frames at 30 FPS.','AAC/container duration and player-estimated frames can differ from the decoded video stream. Read both values; do not change narration or frame counts to match a GUI estimate.'],readOnly=True)


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('report');a=p.parse_args();src=Path(a.source).resolve();out=Path(a.report).resolve();folder=src if src.is_dir() else src.parent
 for parent in [folder,*folder.parents]:
  if (parent/'project.json').exists():
   if out==parent or parent in out.parents:raise ValueError('Save route diagnostics outside the existing project')
   break
 result=inspect(src);out.parent.mkdir(parents=True,exist_ok=True);atomic_json(out,result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
