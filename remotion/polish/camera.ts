import type {CameraDirector} from './schema';
import type {FilmCamera} from '../src/voxel/cinematic/motion';
import {clamp,smooth} from '../characters/animations/state.ts';
export function curveProgress(frame:number,c:CameraDirector){const p=clamp((frame-c.startFrame)/c.durationFrames);return c.curve==='linear'?p:c.curve==='ease-in'?p*p:c.curve==='ease-out'?1-(1-p)*(1-p):smooth(p);}
const shakeEnvelope=(c:CameraDirector,frame:number)=>smooth((frame-c.startFrame)/8)*smooth((c.startFrame+c.durationFrames-frame)/8);
export function screenCamera(c:CameraDirector|undefined,frame:number,reduced=false){
 const neutral={x:0,y:0,scale:1,focus:0,origin:'50% 50%'};if(!c||c.preset==='none'||reduced)return neutral;
 const p=curveProgress(frame,c),i=c.intensity,amount=(p-.5)*2*i;
 const result={...neutral,origin:`${c.screenTarget[0]}% ${c.screenTarget[1]}%`};
 switch(c.preset){case 'push-in':result.scale=1+p*.14*i;break;case 'pull-out':result.scale=1+(1-p)*.14*i;break;
 case 'pan-horizontal':case 'lateral':result.x=-28*amount;result.scale=1+.06*i;break;
 case 'pan-vertical':result.y=-28*amount;result.scale=1+.06*i;break;
 case 'orbit':result.x=Math.sin(p*Math.PI)*20*i;result.y=Math.cos(p*Math.PI)*8*i;result.scale=1+.06*i;break;
 case 'focus':result.scale=1+.14*p*i;result.focus=smooth(p*3)*i;break;
 case 'shake':result.x=Math.sin(frame*1.7+c.seed)*3*i*shakeEnvelope(c,frame);result.y=Math.cos(frame*2.1+c.seed)*2*i*shakeEnvelope(c,frame);result.scale=1+.025*i*shakeEnvelope(c,frame);break;
 case 'reveal':result.y=(1-p)*28*i;result.scale=1+.06*i;break;
 case 'map-to-voxel':result.scale=1+.2*p*i;result.focus=p*i;break;
 }return result;
}
export function directCamera(base:FilmCamera,c:CameraDirector|undefined,frame:number,reduced=false):FilmCamera{
 if(!c||c.preset==='none'||reduced)return base;
 const p=curveProgress(frame,c),i=c.intensity,position=[...base.position] as FilmCamera['position'],target=[...base.target] as FilmCamera['target'];
 const delta=position.map((v,j)=>v-target[j]);
 switch(c.preset){
 case 'push-in':case 'map-to-voxel':for(let j=0;j<3;j++)position[j]-=delta[j]*p*.25*i;break;
 case 'pull-out':for(let j=0;j<3;j++)position[j]+=delta[j]*p*.2*i;break;
 case 'pan-horizontal':position[0]+=(p-.5)*2*i;target[0]+=(p-.5)*2*i;break;
 case 'pan-vertical':position[1]+=(p-.5)*1.5*i;target[1]+=(p-.5)*1.5*i;break;
 case 'lateral':position[0]+=(p-.5)*3*i;break;
 case 'orbit':{const a=(p-.5)*.35*i;position[0]=target[0]+delta[0]*Math.cos(a)+delta[2]*Math.sin(a);position[2]=target[2]+delta[2]*Math.cos(a)-delta[0]*Math.sin(a);break;}
 case 'focus':if(c.worldTarget)for(let j=0;j<3;j++)target[j]+=(c.worldTarget[j]-target[j])*p*i;break;
 case 'shake':position[0]+=Math.sin(frame*1.7+c.seed)*.035*i*shakeEnvelope(c,frame);position[1]+=Math.cos(frame*2.1+c.seed)*.025*i*shakeEnvelope(c,frame);break;
 case 'reveal':position[1]+=(1-p)*1.5*i;break;
 }return {position,target,fov:base.fov};
}
