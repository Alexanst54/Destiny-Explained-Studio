import {directCharacter} from '../../polish/characters.ts';
import type {Cast,Group} from '../../living/schema';
export type Vec=[number,number,number];
export const clamp=(v:number,a=0,b=1)=>Math.max(a,Math.min(b,v));
export const smooth=(v:number)=>{const t=clamp(v);return t*t*(3-2*t);};
export const random=(seed:number,index:number)=>{let n=(seed^Math.imul(index+1,0x45d9f3b))>>>0;n=Math.imul(n^(n>>>16),0x45d9f3b);return ((n^(n>>>16))>>>0)/4294967296;};
export const bounded=(v:number[]):Vec=>[clamp(v[0],-18,18),clamp(v[1],0,12),clamp(v[2],-18,18)];
export function pathState(a:Cast,frame:number,fps=30):{position:Vec;yaw:number}{
 if(!a.path)return {position:a.position,yaw:a.rotation};
 let remaining=Math.max(0,frame-a.startFrame);const points=a.path.waypoints;
 for(let i=0;i<points.length-1;i++){
  const p=points[i],q=points[i+1],delta=q.position.map((v,j)=>v-p.position[j]);
  const yaw=Math.atan2(delta[0],delta[2]),length=Math.hypot(...delta),travel=length/a.path.speed*fps;
  if(remaining<=p.pauseFrames)return {position:p.position,yaw};remaining-=p.pauseFrames;
  if(remaining<travel)return {position:bounded(p.position.map((v,j)=>v+delta[j]*remaining/travel)),yaw};remaining-=travel;
 }
 const p=points[points.length-2].position,q=points[points.length-1].position;
 return {position:q,yaw:Math.atan2(q[0]-p[0],q[2]-p[2])};
}
export function joints(animation:Cast['animation'],local:number,duration:number){
 const t=local/30,s=Math.sin(t* (animation==='walk'?7:11)),p=smooth(local/Math.max(1,duration));
 const j={armL:0,armR:0,legL:0,legR:0,head:0,lean:0,roll:0,y:Math.sin(t*2)*.02,visibility:1};
 switch(animation){
 case 'walk':case 'run':case 'flee':{const k=animation==='walk'?.45:.8;j.armL=-s*k;j.armR=s*k;j.legL=s*k;j.legR=-s*k;j.lean=animation==='walk'?0:.2;j.y=Math.abs(s)*.06;break;}
 case 'look':case 'observe':j.head=Math.sin(t*1.3)*.5;break;
 case 'salute':j.armR=-2.2*smooth(local/12);break;
 case 'talk':j.armL=-.4+Math.sin(t*4)*.3;j.armR=-.4+Math.cos(t*3)*.3;break;
 case 'interact':case 'terminal':j.armL=-1.1+Math.sin(t*5)*.13;j.armR=-1.1+Math.cos(t*5)*.13;j.lean=.1;break;
 case 'kneel':j.legR=-1;j.y=-.6*p;j.lean=.2;break;
 case 'fall':j.roll=1.5*p;j.y=-.4*p;break;
 case 'combat':j.armL=-1;j.armR=-1+s*.4;j.lean=.15;break;
 case 'attack':j.armR=-2*Math.sin(p*Math.PI);j.lean=.3*Math.sin(p*Math.PI);break;
 case 'hit':j.roll=Math.sin(p*Math.PI)*.4;break;
 case 'appear':j.visibility=smooth(local/18);break;
 case 'disappear':j.visibility=1-smooth(local/18);break;
 }return j;
}
export function characterState(a:Cast,frame:number,override?:{animation:Cast['animation'];startFrame:number;transitionFrames:number}){
 const local=frame-a.startFrame,active=local>=0&&local<a.durationFrames;
 const clip=a.clips.find(c=>local>=c.startFrame&&local<c.startFrame+c.durationFrames);
 const name=override?.animation??clip?.animation??a.animation;
 const start=override?.startFrame??(a.startFrame+(clip?.startFrame??0));
 const duration=clip?.durationFrames??a.durationFrames;
 const current=joints(name,frame-start,duration),blend=smooth((frame-start)/Math.max(1,override?.transitionFrames??clip?.transitionFrames??12));
 const earlier=clip?a.clips.filter(c=>c.startFrame<clip.startFrame):[];const previous=earlier[earlier.length-1];
 const base=joints(previous?.animation??a.animation,local-(previous?.startFrame??0),previous?.durationFrames??a.durationFrames);
 const pose=Object.fromEntries(Object.keys(current).map(k=>[k,base[k as keyof typeof base]+(current[k as keyof typeof current]-base[k as keyof typeof base])*blend])) as typeof current;
 // Clip exit blends to the base pose; no accumulated state.
 if(clip&&!override){const exit=smooth((clip.startFrame+clip.durationFrames-local)/Math.max(1,clip.transitionFrames));const idle=joints(a.animation,local,a.durationFrames);for(const k of Object.keys(pose) as (keyof typeof pose)[])pose[k]=idle[k]+(pose[k]-idle[k])*exit;}
 const motion=pathState(a,Math.min(frame,a.startFrame+a.durationFrames));return directCharacter(a,frame,{...motion,pose,active,animation:name});
}
export function expandGroup(g:Group):Cast[]{
 return Array.from({length:g.count},(_,i)=>{
 const x=g.formation==='line'?i-(g.count-1)/2:g.formation==='grid'?i%5-2:(random(g.seed,i*3)-.5)*5;
 const z=g.formation==='grid'?Math.floor(i/5):g.formation==='scatter'?(random(g.seed,i*3+1)-.5)*4:0;
 const offset=[x*g.spacing,0,z*g.spacing];const shift=(v:number[])=>bounded(v.map((n,j)=>n+offset[j]));
 return {...g.member,...(g.member.director?{director:{...g.member.director,seed:(g.member.director.seed+i*7919)%2147483647}}:{}),id:`${g.id}:${i}`,position:shift(g.member.position),scale:clamp(g.member.scale*(1+(random(g.seed,i*3+2)-.5)*2*g.sizeVariation),.5,1.5),animation:g.behavior==='idle'?g.member.animation:g.behavior,path:g.member.path?{...g.member.path,waypoints:g.member.path.waypoints.map(p=>({...p,position:shift(p.position)}))}:undefined};
 });
}
