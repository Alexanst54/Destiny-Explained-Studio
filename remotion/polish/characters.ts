import type {Cast} from '../living/schema';
import {clamp,smooth,random} from '../characters/animations/state.ts';
type Vec=[number,number,number];
type Pose={armL:number;armR:number;legL:number;legR:number;head:number;lean:number;roll:number;y:number;visibility:number};
export const angleDelta=(a:number,b:number)=>Math.atan2(Math.sin(b-a),Math.cos(b-a));
export function directedPath(a:Cast,frame:number){
 let time=Math.max(0,frame-a.startFrame-(a.director?.exodus?Math.floor(random(a.director.seed,7)*12):0)),previousYaw=a.rotation;
 if(!a.path)return {position:a.position,yaw:a.rotation,gait:['walk','run','flee'].includes(a.animation)?1:0};
 const pts=a.path.waypoints,turn=a.director?.turnFrames??12,stop=a.director?.stopFrames??12;
 for(let n=0;n<pts.length-1;n++){
  const from=pts[n],to=pts[n+1],d=to.position.map((v,j)=>v-from.position[j]),duration=Math.hypot(...d)/a.path.speed*30,yaw=Math.atan2(d[0],d[2]);
  if(time<=from.pauseFrames)return {position:from.position,yaw:previousYaw,gait:0};time-=from.pauseFrames;
  if(time<duration){const t=clamp(time/Math.max(1,duration)),ease=smooth(t),gait=Math.min(smooth(time/stop),smooth((duration-time)/stop));return {position:from.position.map((v,j)=>v+d[j]*ease) as Vec,yaw:previousYaw+angleDelta(previousYaw,yaw)*smooth(time/turn),gait};}
  time-=duration;previousYaw=yaw;
 }if(a.director?.exodus){const end=pts[pts.length-1].position,from=pts[pts.length-2].position,d=end.map((v,j)=>v-from[j]),length=Math.hypot(...d),distance=Math.min(6,time*a.path.speed/30);const position=end.map((v,j)=>clamp(v+(length?d[j]/length*distance:0),j===1?0:-18,j===1?12:18)) as Vec;return {position,yaw:previousYaw,gait:distance>=6?0:smooth(time/stop)};}
 return {position:pts[pts.length-1].position,yaw:previousYaw,gait:0};
}
export function directCharacter<T extends {position:Vec;yaw:number;pose:Pose;active:boolean;animation:string}>(a:Cast,frame:number,base:T):T{
 const c=a.director;if(!c)return base;const local=frame-a.startFrame-c.startFrame;
 const motion=directedPath(a,frame),pose={...base.pose},ramp=local>=0&&local<c.durationFrames?smooth(local/12)*smooth((c.durationFrames-local)/12):0,phase=random(c.seed,1)*Math.PI*2;
 if(['walk','run','flee'].includes(base.animation)){for(const key of ['armL','armR','legL','legR'] as const)pose[key]*=motion.gait;pose.lean*=motion.gait;pose.y=pose.y*motion.gait+Math.sin(frame/30*2+phase)*.015*(1-motion.gait);}
 if(c.target){const dx=c.target[0]-motion.position[0],dz=c.target[2]-motion.position[2],yaw=Math.atan2(dx,dz);pose.head+=(clamp(angleDelta(motion.yaw,yaw),-.75,.75)*c.headStrength-pose.head)*ramp;}
 switch(c.emotion){case 'surprise':pose.armL-=.6*ramp;pose.armR-=.6*ramp;pose.y+=.05*ramp;break;case 'fear':pose.lean+=.18*ramp;pose.head+=Math.sin(frame/11+phase)*.12*ramp;break;case 'attention':pose.head+=Math.sin(frame/45+phase)*.06*ramp;break;case 'curiosity':pose.roll+=.07*ramp;pose.head+=.22*Math.sin(frame/45+phase)*ramp;break;}
 let yaw=motion.yaw;
 switch(c.gesture){case 'point':pose.armR+=(-1.4-pose.armR)*ramp;break;case 'look':pose.head+=Math.sin(local/40+phase)*.35*ramp;break;case 'turn':yaw+=Math.PI*smooth(local/Math.max(1,c.durationFrames*.5))*ramp;break;case 'flee':pose.lean+=.15*ramp;break;}
 return {...base,position:motion.position,yaw,pose};
}
export function costumeVariation(a:Cast){const c=a.director;return c?{hue:(random(c.seed,2)-.5)*c.variation,width:1+(random(c.seed,3)-.5)*c.variation,accent:random(c.seed,4)>.5}:{hue:0,width:1,accent:false};}
