import type {FilmCamera} from '../src/voxel/cinematic/motion';
import type {Composer} from './schema';
import type {ActorFrame} from './director';
import type {Vec} from './rig';
import {smooth} from '../characters/animations/state.ts';
export function composeCamera(base:FilmCamera,c:Composer|undefined,actors:ActorFrame[],frame:number,reduced=false):FilmCamera{
 if(!c||reduced||frame<c.startFrame||frame>=c.startFrame+c.durationFrames)return base;const selected=actors.filter(a=>c.targets.includes(a.actor.id)&&a.active);if(!selected.length)return base;
 const p=smooth((frame-c.startFrame)/c.durationFrames),weight=smooth((frame-c.startFrame)/12)*smooth((c.startFrame+c.durationFrames-frame)/12),t=reduced?0:p;
 const bounds=selected.map(a=>{const height=(a.actor.rig?.height??2.4)*a.actor.scale,width=(a.actor.rig?.width??1)*a.actor.scale*1.05;return {min:[a.position[0]-width,a.position[1]-.6,a.position[2]-width],max:[a.position[0]+width,a.position[1]+height+.7,a.position[2]+width]};});
 const lo=[0,1,2].map(j=>Math.min(...bounds.map(b=>b.min[j]))),hi=[0,1,2].map(j=>Math.max(...bounds.map(b=>b.max[j]))),center=lo.map((v,j)=>(v+hi[j])/2) as Vec;
 // Radius contains arms, head, kneeling/fall envelope. Reserve bottom ~25% for captions.
 const radius=Math.hypot(...hi.map((v,j)=>(v-lo[j])/2))*c.margin,halfHorizontal=Math.atan(Math.tan(base.fov*Math.PI/360)*1080/1920),distance=Math.max(6,Math.max((hi[0]-lo[0])/2*c.margin/(Math.tan(halfHorizontal)*.8),(hi[1]-lo[1])/2*c.margin/(Math.tan(base.fov*Math.PI/360)*.7))+(hi[2]-lo[2])/2)*(1+.1*(1-c.intensity));
 const sign=c.side==='left'?-1:1,angle=c.mode==='reverse'?sign*.35:c.mode==='reaction'?sign*.2:0;
 const multiplier=c.mode==='group'?1.12:c.mode==='wide-close'?1.25-.25*t*c.intensity:c.mode==='reveal'?1.2-.2*t:1;
 const target:[number,number,number]=[center[0],center[1]-radius*.2,center[2]],position:[number,number,number]=[target[0]+Math.sin(angle)*distance*multiplier,target[1]+distance*.12,target[2]+Math.cos(angle)*distance*multiplier];
 if(c.mode==='actor'||c.mode==='follow'||c.mode==='reaction'){// A single target should be selected for a tight shot.
  position[0]+=(c.mode==='reaction'?sign:0)*.3*c.intensity;
 }
 return {position:base.position.map((v,j)=>v+(position[j]-v)*weight) as Vec,target:base.target.map((v,j)=>v+(target[j]-v)*weight) as Vec,fov:base.fov};
}
