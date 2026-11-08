import type {TimedAction,TimedShot,TimedEvent,ResolvedScene,Timeline,Vec} from './timeline';
import {lerp,mix,smooth,profiles} from './timeline.ts';
export type JointPose = {legL:number;legR:number;armL:number;armR:number;armRollL:number;armRollR:number;lean:number;head:number};
export type ActorPose = {position:Vec;rotation:Vec;joints:JointPose;rise:number};
const joints = ():JointPose=>({legL:0,legR:0,armL:0,armR:0,armRollL:0,armRollR:0,lean:0,head:0});
export const actorPose = (actor:'guardian'|'ghost',clips:TimedAction[],frame:number,intensity:Timeline['intensity']):ActorPose => {
  const profile=profiles[intensity];
  const eligible=clips.filter(a=>a.actor===actor&&frame>=a.start).sort((a,b)=>a.start-b.start);
  const action=eligible[eligible.length-1];
  const pose:ActorPose={position:actor==='guardian'?[-0.6,0.02,0]:[0.6,3.4,0],rotation:[0,0,0],joints:joints(),rise:1};
  if(!action)return pose;
  const local=frame-action.start,p=Math.min(1,Math.max(0,local/(action.durationFrames-1))),e=smooth(p);
  const active=local<action.durationFrames;
  pose.position=mix(action.from,action.to,e);
  const t=local/30,amp=profile.motion;
  if(actor==='ghost'){
    if(action.animation==='orbit'){
      pose.position[0]+=Math.sin(p*Math.PI*2)*0.6;
      pose.position[2]+=Math.cos(p*Math.PI*2)*0.4-0.4;
    }
    if(action.animation==='scan'||action.animation==='interact')pose.rotation[1]=active?Math.sin(t*3)*0.4*amp:0;
    return pose;
  }
  const dx=action.to[0]-action.from[0],dz=action.to[2]-action.from[2];
  if(Math.hypot(dx,dz)>0.001)pose.rotation[1]=Math.atan2(dx,dz);
  switch(action.animation){
    case 'walk':case 'run':{
      const run=action.animation==='run',wave=active?Math.sin(t*(run?12:7)):0;
      pose.position=mix(action.from,action.to,p);
      pose.position[1]+=Math.abs(wave)*(run?0.12:0.05)*amp;
      pose.joints.legL=wave*(run?1:0.6)*amp;pose.joints.legR=-pose.joints.legL;
      pose.joints.armL=-wave*(run?0.9:0.5)*amp;pose.joints.armR=-pose.joints.armL;
      pose.joints.lean=run?0.14*amp:0;break;
    }
    case 'jump':
      pose.position[1]+=Math.sin(p*Math.PI)*action.height;
      pose.joints.legL=pose.joints.legR=-Math.sin(p*Math.PI)*0.45;
      pose.joints.armL=pose.joints.armR=-Math.sin(p*Math.PI)*2*amp;break;
    case 'fall':
      pose.rotation=[0,0,-e*Math.PI/2];pose.position[0]-=e;
      pose.joints.armL=-Math.sin(e*Math.PI)*amp;break;
    case 'resurrect':
      pose.rotation=[0,0,-(1-e)*Math.PI/2];pose.position[0]-=(1-e);
      pose.position[1]+=Math.sin(e*Math.PI)*0.3;pose.rise=e;
      pose.joints.armRollL=Math.sin(e*Math.PI)*0.5*amp;
      pose.joints.armRollR=-pose.joints.armRollL;break;
    case 'combat':{
      const pulse=active?Math.max(0,Math.sin(t*9)):0;
      pose.joints.armR=-pulse*1.7*amp;pose.joints.armL=-0.4*amp;
      pose.joints.lean=pulse*0.12;pose.rotation[1]=Math.sin(t*4)*0.12*amp;break;
    }
    case 'interact':
      pose.joints.armR=-Math.sin(e*Math.PI/2)*0.9*amp;
      pose.joints.head=-0.12*amp;break;
    case 'look-up':pose.joints.head=-e*0.35;break;
  }
  return pose;
};
export type FilmCamera = {position:Vec;target:Vec;fov:number};
export const shotCamera = (shot:TimedShot,frame:number,scene:ResolvedScene,intensity:Timeline['intensity']):FilmCamera => {
  const p=smooth((frame-shot.start)/Math.max(1,shot.end-shot.start-1));
  const c=shot.camera;
  let position=mix(c.from,c.to,p),target=mix(c.targetFrom,c.targetTo,p);
  if(c.mode==='orbit'){
    const angle=lerp(c.angleFrom??0,c.angleTo??0,p),dx=position[0]-target[0],dz=position[2]-target[2];
    position=[target[0]+dx*Math.cos(angle)+dz*Math.sin(angle),position[1],target[2]-dx*Math.sin(angle)+dz*Math.cos(angle)];
  }
  if(c.track){
    const actor=actorPose(c.track,scene.actions,frame,intensity);
    const focus:Vec=[actor.position[0],actor.position[1]+(c.track==='guardian'?1.5:0),actor.position[2]];
    target=mix(c.targetFrom,c.targetTo,p).map((v,i)=>v+focus[i]) as Vec;
    if(c.mode==='follow')position=position.map((v,i)=>v+focus[i]) as Vec;
  }
  return {position,target,fov:lerp(c.fovFrom,c.fovTo,p)};
};
export const cameraState = (timeline:Timeline,scene:ResolvedScene,shot:TimedShot,frame:number,events:TimedEvent[]):FilmCamera=>{
  let camera=shotCamera(shot,frame,scene,timeline.intensity);
  const flat=timeline.scenes.flatMap(s=>s.shots),index=flat.findIndex(s=>s.id===shot.id);
  if(shot.transition.type==='match' && frame-shot.start<shot.transition.durationFrames && index>0){
    const previous=flat[index-1],prevScene=timeline.scenes.find(s=>previous.start>=s.start&&previous.end<=s.end)!;
    const before=shotCamera(previous,previous.end-1,prevScene,timeline.intensity);
    const blend=smooth((frame-shot.start)/shot.transition.durationFrames);
    camera={position:mix(before.position,camera.position,blend),target:mix(before.target,camera.target,blend),fov:lerp(before.fov,camera.fov,blend)};
  }
  const shake=events.filter(e=>e.type==='shake').reduce((sum,e)=>sum+e.strength*Math.sin((frame-e.start)/e.durationFrames*Math.PI),0)*profiles[timeline.intensity].shake;
  camera.position=camera.position.map((v,i)=>v+shake*Math.sin(frame*(1.71+i*0.37)+i*2)) as Vec;
  return camera;
};
export const transitionState = (timeline:Timeline,shot:TimedShot,frame:number)=>{
  const flat=timeline.scenes.flatMap(s=>s.shots),index=flat.findIndex(s=>s.id===shot.id),next=flat[index+1];
  const incoming=shot.transition;
  if(['fade','wipe'].includes(incoming.type) && frame-shot.start<incoming.durationFrames)
    return {type:incoming.type,opacity:1-smooth((frame-shot.start)/incoming.durationFrames)};
  if(next&&['fade','wipe'].includes(next.transition.type)&&shot.end-frame<=next.transition.durationFrames)
    return {type:next.transition.type,opacity:smooth(1-(shot.end-frame)/next.transition.durationFrames)};
  return {type:'cut',opacity:0};
};
