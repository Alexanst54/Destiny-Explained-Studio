import type {Cast,LivingWorld,LivingShot} from '../living/schema';
import type {RigAnimation,Studio} from './schema';
import type {Pose,Vec} from './rig';
import {rigPose,animationPose,blendPose,adaptRigPose,poseForRig} from './rig.ts';
import {directWorld} from '../living/director.ts';
import {characterState,clamp,smooth,random,bounded} from '../characters/animations/state.ts';
import {directedPath,angleDelta} from '../polish/characters.ts';
export type ActorFrame={actor:Cast;position:Vec;yaw:number;pose:Pose;active:boolean;scale:number;lod:number};
export function studioReferences(actors:Cast[],studio:Studio|undefined,duration:number,props:{id:string}[]=[]):string[]{
 if(!studio)return [];const errors:string[]=[],byId=new Map(actors.map(a=>[a.id,a])),objects=new Set(props.map(p=>p.id));
 for(const i of studio.interactions){if(i.startFrame+i.durationFrames>duration)errors.push('Interaction exceeds scene: '+i.id);
  for(const id of i.actors){const a=byId.get(id);if(!a)errors.push('Unknown interaction actor: '+id);else {if(!a.rig)errors.push('Interaction actor requires rig 2.0: '+id);if(i.startFrame<a.startFrame||i.startFrame+i.durationFrames>a.startFrame+a.durationFrames)errors.push('Interaction exceeds actor lifetime: '+id);}}
  if(i.targetId){const target=byId.get(i.targetId);if(!target&&!(['point','look-at'].includes(i.kind)&&objects.has(i.targetId)))errors.push('Unknown interaction target: '+i.targetId);if(target&&(i.startFrame<target.startFrame||i.startFrame+i.durationFrames>target.startFrame+target.durationFrames))errors.push('Interaction target inactive: '+i.targetId);}
 }
 if(studio.camera){const c=studio.camera;if(c.startFrame+c.durationFrames>duration)errors.push('Composer exceeds scene');for(const id of c.targets){const a=byId.get(id);if(!a)errors.push('Unknown camera actor: '+id);else if(c.startFrame<a.startFrame||c.startFrame+c.durationFrames>a.startFrame+a.durationFrames)errors.push('Camera target inactive: '+id);}}
 return errors;
}
type RigOverride={animation:RigAnimation;startFrame:number;transitionFrames:number};
function base(a:Cast,frame:number,reduced:boolean,override?:RigOverride):ActorFrame{
 const old=characterState(a,frame),r=a.rig;
 if(!r)return {actor:a,position:old.position,yaw:old.yaw,active:old.active,pose:{rotation:{},lift:0,yaw:0},scale:a.scale,lod:2};
 const motion=directedPath(a,frame),local=frame-a.startFrame,basePose=override&&frame>=override.startFrame?blendPose(poseForRig(r,r.animation,local+r.phaseOffset,90,reduced),poseForRig(r,override.animation,frame-override.startFrame+r.phaseOffset,90,reduced),smooth((frame-override.startFrame)/Math.max(1,override.transitionFrames))):undefined,pose=rigPose(r,local,reduced,basePose);
 if(a.director){const plain=characterState({...a,director:undefined},frame),d=old.pose,b=plain.pose;pose.rotation.head??=[0,0,0];pose.rotation.head[1]+=d.head-b.head;pose.rotation.torso??=[0,0,0];pose.rotation.torso[0]+=d.lean-b.lean;pose.rotation.torso[2]+=d.roll-b.roll;pose.lift+=d.y-b.y;for(const side of ['L','R'])for(const row of ['upper','lower']){const key='shoulder-'+row+side;pose.rotation[key]??=[0,0,0];pose.rotation[key][0]+=(d[side==='L'?'armL':'armR']-b[side==='L'?'armL':'armR'])*(row==='lower'?.6:1);}}
 const activeClip=r.clips.find(c=>frame-a.startFrame>=c.startFrame&&frame-a.startFrame<c.startFrame+c.durationFrames);
 if(a.path&&['walk','run','sprint','flee'].includes(activeClip?.animation??(override&&frame>=override.startFrame?override.animation:r.animation))){const idle=animationPose('idle',frame,r.seed,90,reduced);for(const [id,angles]of Object.entries(pose.rotation))if(id.startsWith('hip')||id.startsWith('knee')||id.startsWith('shoulder-'))pose.rotation[id]=angles.map(v=>v*motion.gait) as Vec;pose.lift=pose.lift*motion.gait+idle.lift*(1-motion.gait);}
 return {actor:a,position:motion.position,yaw:(a.director?old.yaw:motion.yaw)+pose.yaw,pose:adaptRigPose(r,pose),active:old.active,scale:a.scale*r.height/2.36,lod:2};
}
export function separateActors(frames:ActorFrame[],radius:number):ActorFrame[]{
 // Two bounded spatial passes; always rebuilt from this frame, never integrated over time.
 let out=frames.map(f=>({...f,position:[...f.position] as Vec}));
 for(let pass=0;pass<2;pass++){const source=out;out=source.map((a,i)=>{if(!a.active||!a.actor.rig)return a;let x=0,z=0;
  for(let j=0;j<source.length;j++){const b=source[j];if(i===j||!b.active)continue;const dx=a.position[0]-b.position[0],dz=a.position[2]-b.position[2],distance=Math.hypot(dx,dz),limit=radius*(a.actor.scale+b.actor.scale);if(distance>=limit)continue;const angle=distance>1e-6?Math.atan2(dz,dx):i<j?0:Math.PI,k=(limit-distance)*(b.actor.rig?.5:1);x+=Math.cos(angle)*k;z+=Math.sin(angle)*k;}
  return {...a,position:bounded([a.position[0]+x,a.position[1],a.position[2]+z])};});}
 return out;
}
export function evaluateStudio(world:LivingWorld|undefined,shot:LivingShot|undefined,frame:number,reduced=false,shotStart=0):ActorFrame[]{
 const aliases:Record<string,string>={look:'look-around',observe:'look-around',talk:'talk-gesture',hit:'react',interact:'talk-gesture',terminal:'talk-gesture',combat:'react',attack:'point',salute:'celebrate',appear:'idle',disappear:'idle'};
 const actors=directWorld(world,shot),overrides=new Map((shot?.animations??[]).map(o=>[o.id,{animation:(aliases[o.animation]??o.animation) as RigAnimation,startFrame:shotStart,transitionFrames:o.transitionFrames}]));
 const sample=(a:Cast,f:number)=>base(a,f,reduced,overrides.get(a.id));
 const studio=shot?.studio??world?.studio,states=actors.map(a=>sample(a,frame)),lookup=new Map(states.map(f=>[f.actor.id,f]));
 if(!studio)return states;
 for(const i of studio.interactions){const t=frame-i.startFrame;if(t<0||t>=i.durationFrames)continue;const weight=smooth(t/Math.max(1,i.transitionFrames))*smooth((i.durationFrames-t)/Math.max(1,i.transitionFrames))*i.intensity;
  const target=i.targetId?lookup.get(i.targetId):undefined,prop=world?.props.find(p=>p.id===i.targetId),anchor=i.targetPoint??target?.position??prop?.position;
  const members=i.actors.map(id=>lookup.get(id)).filter((f):f is ActorFrame=>!!f&&f.active),center=anchor??members.reduce((sum,f)=>sum.map((v,j)=>v+f.position[j]/Math.max(1,members.length)) as Vec,[0,0,0] as Vec);
  for(let n=0;n<members.length;n++){const f=members[n];if(!f.actor.rig)continue;const original=sample(f.actor,frame),look=anchor??center,dx=look[0]-f.position[0],dz=look[2]-f.position[2],heading=Math.atan2(dx,dz),turn=angleDelta(f.yaw,heading);
   if(['face','follow'].includes(i.kind))f.yaw+=turn*weight;
   if(['walk-together','follow','form','disperse','flee'].includes(i.kind)){
    let goal:Vec;
    if(i.kind==='follow'&&target){const delayed=sample(target.actor,Math.max(target.actor.startFrame,frame-12)),side=(n%2?1:-1)*i.spacing*.65,behind=(Math.floor(n/2)+1)*i.spacing;goal=[delayed.position[0]+Math.cos(delayed.yaw)*side-Math.sin(delayed.yaw)*behind,delayed.position[1],delayed.position[2]-Math.sin(delayed.yaw)*side-Math.cos(delayed.yaw)*behind];}
    else if(i.kind==='disperse'||i.kind==='flee'){const angle=random(f.actor.rig.seed,n)*Math.PI*2,distance=Math.min(8,t/30*(i.kind==='flee'?2.6:1.1));goal=[original.position[0]+Math.cos(angle)*distance,original.position[1],original.position[2]+Math.sin(angle)*distance];}
    else goal=[center[0]+(n-(members.length-1)/2)*i.spacing,center[1],center[2]+(i.kind==='walk-together'?t/30*.8:0)];
    f.position=bounded(f.position.map((v,j)=>v+(goal[j]-v)*weight));const moveX=goal[0]-original.position[0],moveZ=goal[2]-original.position[2];if(Math.hypot(moveX,moveZ)>.01)f.yaw=original.yaw+angleDelta(original.yaw,Math.atan2(moveX,moveZ))*weight;
   }
   const animation=i.kind==='react'?'react':i.kind==='point'?'point':i.kind==='flee'?'flee':['follow','walk-together','disperse'].includes(i.kind)?(['run','flee','sprint'].includes(f.actor.rig.animation)?f.actor.rig.animation:'walk'):undefined;
   if(animation)f.pose=blendPose(f.pose,poseForRig(f.actor.rig,animation,t+f.actor.rig.phaseOffset,i.durationFrames,reduced),weight);
   if(['look-at','point','react'].includes(i.kind)){const h=f.pose.rotation.head??[0,0,0];f.pose={...f.pose,rotation:{...f.pose.rotation,head:[clamp(-Math.atan2(look[1]+(target?(target.actor.rig?.height??2.3)*target.actor.scale*.9:prop?1:0)-f.position[1]-f.actor.rig.height*f.actor.scale*.9,Math.max(.01,Math.hypot(dx,dz))),-.65,.4)*weight,h[1]+clamp(turn,-.85,.85)*weight,h[2]]}};}
  }
 }
 for(const f of states)if(f.actor.rig)f.pose=adaptRigPose(f.actor.rig,f.pose);
 return studio.avoidCollisions?separateActors(states,studio.collisionRadius):states;
}
export function lodFor(profile:Studio['profile'],distance:number){return profile==='draft'?0:distance>22?0:profile==='balanced'||distance>13?1:2;}
