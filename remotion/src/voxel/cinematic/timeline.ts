import type {VoxelEpisodeDef,AlignedWord} from '../episode/schema';
import type {Direction,Cue,Shot,Action,VisualEvent} from './schema';
export const smooth = (p:number) => {const x=Math.max(0,Math.min(1,p));return x*x*(3-2*x);};
export const lerp = (a:number,b:number,p:number) => a+(b-a)*p;
export type Vec = [number,number,number];
export const mix = (a:Vec,b:Vec,p:number):Vec => a.map((v,i)=>lerp(v,b[i],p)) as Vec;
export const profiles = {
  calm:{motion:0.5,shake:0.025,particles:16},
  balanced:{motion:0.8,shake:0.07,particles:28},
  cinematic:{motion:1,shake:0.12,particles:40},
};
const normalized = (text:string) => text.toLowerCase().replace(/[^a-z0-9]/g,'');
export type TimedShot = Shot & {start:number;end:number};
export type TimedAction = Action & {start:number;end:number};
export type TimedEvent = VisualEvent & {start:number;end:number};
export type ResolvedScene = {sceneId:string;start:number;end:number;shots:TimedShot[];actions:TimedAction[];events:TimedEvent[]};
export type Timeline = {intensity:Direction['intensity'];scenes:ResolvedScene[]};
export const estimatedWords = (episode:VoxelEpisodeDef):AlignedWord[] => episode.scenes.flatMap(s => {
  const tokens=s.narration.split(/\s+/),step=s.durationFrames/episode.format.fps/tokens.length;
  return tokens.map((text,i)=>({text,start:s.startFrame/30+i*step,end:s.startFrame/30+(i+1)*step}));
});
export const resolveCue = (cue:Cue,scene:VoxelEpisodeDef['scenes'][number],words:AlignedWord[]) => {
  if ('sceneFrame' in cue) return scene.startFrame+cue.sceneFrame;
  const local=words.filter(w=>w.start>=scene.startFrame/30-1e-6 && w.end<=(scene.startFrame+scene.durationFrames)/30+1e-6);
  const phrase=cue.phrase.split(/\s+/).map(normalized);
  const matches=local.filter((_,i)=>phrase.every((t,j)=>normalized(local[i+j]?.text??'')===t));
  const word=matches[(cue.occurrence??1)-1];
  if (!word) throw new Error(`${scene.id}: narration cue not found: ${cue.phrase}`);
  return Math.round(word.start*30)+(cue.offsetFrames??0);
};
export const resolveDirection = (episode:VoxelEpisodeDef,words:AlignedWord[]):Timeline => {
  const direction=episode.direction;
  if (!direction) throw new Error('Cinematic episode requires direction');
  if (direction.scenes.length!==episode.scenes.length) throw new Error('Direction must cover every scene');
  const sceneIds=new Set<string>(), allIds=new Set<string>();
  const scenes=direction.scenes.map((plan,i):ResolvedScene=>{
    const scene=episode.scenes[i];
    if (plan.sceneId!==scene.id || sceneIds.has(plan.sceneId)) throw new Error('Direction scenes must match episode order exactly');
    sceneIds.add(plan.sceneId);
    const start=scene.startFrame,end=start+scene.durationFrames;
    const at=(cue:Cue)=>{
      const frame=resolveCue(cue,scene,words);
      if (frame<start || frame>=end) throw new Error(`${scene.id}: cue outside scene`);
      return frame;
    };
    const unique=(id:string)=>{if(allIds.has(id))throw new Error(`Duplicate direction id: ${id}`);allIds.add(id);};
    const starts=plan.shots.map(s=>at(s.at));
    if (starts[0]!==start) throw new Error(`${scene.id}: first shot must begin at scene start`);
    const shots=plan.shots.map((shot,j):TimedShot=>{
      unique(shot.id);
      const finish=starts[j+1]??end;
      if (finish-starts[j]<12) throw new Error(`${shot.id}: shots must be ordered and at least 12 frames long`);
      if (shot.transition.durationFrames*2>finish-starts[j]) throw new Error(`${shot.id}: transition too long`);
      if (shot.transition.type==='cut' && shot.transition.durationFrames!==0) throw new Error(`${shot.id}: cut duration must be zero`);
      if (shot.transition.type!=='cut' && shot.transition.durationFrames===0) throw new Error(`${shot.id}: transition requires a duration`);
      if (shot.camera.mode==='follow' && !shot.camera.track) throw new Error(`${shot.id}: follow requires a character`);
      if (shot.camera.mode==='orbit' && (shot.camera.angleFrom===undefined || shot.camera.angleTo===undefined)) throw new Error(`${shot.id}: orbit requires angles`);
      if (shot.camera.track && !shot.actors[shot.camera.track]) throw new Error(`${shot.id}: tracking an invisible actor`);
      if (shot.camera.from.every((v,k)=>v===shot.camera.targetFrom[k]) || shot.camera.to.every((v,k)=>v===shot.camera.targetTo[k])) throw new Error(`${shot.id}: camera must differ from its target`);
      const a=shot.camera.from.map((v,k)=>v-shot.camera.targetFrom[k]);
      const b=shot.camera.to.map((v,k)=>v-shot.camera.targetTo[k]-a[k]);
      const norm=b.reduce((sum,v)=>sum+v*v,0);
      const nearest=norm?Math.max(0,Math.min(1,-a.reduce((sum,v,k)=>sum+v*b[k],0)/norm)):0;
      if(Math.hypot(...a.map((v,k)=>v+nearest*b[k]))<0.25)throw new Error(`${shot.id}: camera path crosses its target`);
      return {...shot,start:starts[j],end:finish};
    });
    const actions=plan.actions.map((action):TimedAction=>{
      unique(action.id);const begin=at(action.at);
      if (begin+action.durationFrames>end) throw new Error(`${action.id}: action exceeds scene`);
      return {...action,start:begin,end:begin+action.durationFrames};
    });
    for (const actor of ['guardian','ghost']) {
      const clips=actions.filter(a=>a.actor===actor).sort((a,b)=>a.start-b.start);
      for (let j=1;j<clips.length;j++) if(clips[j].start<clips[j-1].end)throw new Error(`${scene.id}: overlapping ${actor} actions`);
    }
    const events=plan.events.map((event):TimedEvent=>{
      unique(event.id);const begin=at(event.at);
      if (begin+event.durationFrames>end) throw new Error(`${event.id}: effect exceeds scene`);
      if (event.type==='beam' && !event.to) throw new Error(`${event.id}: beam requires an endpoint`);
      if(event.type==='beam'&&Math.hypot(...event.position.map((v,k)=>v-event.to![k]))<0.1)throw new Error(`${event.id}: beam endpoints must differ`);
      return {...event,start:begin,end:begin+event.durationFrames};
    });
    return {sceneId:scene.id,start,end,shots,actions,events};
  });
  // Check incoming transitions against the outgoing plan too, including scene cuts.
  const shots=scenes.flatMap(s=>s.shots);
  for(let i=1;i<shots.length;i++)if(shots[i].transition.durationFrames*2>shots[i-1].end-shots[i-1].start)throw new Error(`${shots[i].id}: incoming transition exceeds previous shot`);
  return {intensity:direction.intensity,scenes};
};
export const atFrame = (timeline:Timeline,frame:number) => {
  const scene=timeline.scenes.find(s=>frame>=s.start&&frame<s.end);
  const shot=scene?.shots.find(s=>frame>=s.start&&frame<s.end);
  if(!scene||!shot)throw new Error(`No cinematic shot at frame ${frame}`);
  return {scene,shot,events:scene.events.filter(e=>frame>=e.start&&frame<e.end)};
};
