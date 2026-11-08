import type {Weather} from './schema';
import {random,smooth,clamp} from '../characters/animations/state.ts';
export function weatherState(w:Weather,frame:number){
 const local=frame-w.startFrame,active=local>=0&&local<w.durationFrames;
 const mix=w.to?smooth(local/Math.max(1,w.transitionFrames)):0;
 const blend=(key:'intensity'|'windDirection'|'windSpeed'|'visibility')=>w[key]+((w.to?.[key]??w[key])-w[key])*mix;
 const phase=(w.dayPhase+(w.dayCycleFrames?Math.max(0,local)/w.dayCycleFrames:0))%1;
 const daylight=clamp(.5-.5*Math.cos(phase*Math.PI*2),.12,1),intensity=blend('intensity'),visibility=blend('visibility');
 const flash=(type:string)=>type==='thunderstorm'&&random(w.seed,Math.floor(Math.max(0,local)/75))>.45&&((local%75+75)%75)<3?1:0;
 const lightning=active?((1-mix)*flash(w.type)+mix*flash(w.to?.type??w.type))*intensity:0;
 return {active,mix,intensity,visibility,windDirection:blend('windDirection'),windSpeed:blend('windSpeed'),daylight,lightning,light:daylight*(1-intensity*.45)+lightning*1.5,fogNear:4+visibility*20,fogFar:12+visibility*40,local};
}
export function weatherParticles(w:Weather,frame:number){
 const s=weatherState(w,frame);if(!s.active)return [];
 const count=Math.min(128,w.particleBudget),radians=s.windDirection*Math.PI/180;
 const speeds={clear:0,clouds:.15,rain:7,thunderstorm:9,snow:1,blizzard:2,fog:0,sandstorm:1,'strong-wind':2,spores:.3,energy:-.5,supernatural:-.2};
 const particles=[];
 for(let i=0;i<count;i++){
  const type=i<count*(1-s.mix)?w.type:w.to?.type??w.type;
  if(type==='clear'||type==='fog')continue;
  const t=Math.max(0,s.local)/30,wrap=(x:number,n:number)=>((x%n)+n)%n;
  particles.push({index:i,type,position:[wrap(random(w.seed,i*4)*32+t*s.windSpeed*.12*Math.cos(radians),32)-16,wrap(random(w.seed,i*4+1)*12-t*speeds[type],12),wrap(random(w.seed,i*4+2)*28+t*s.windSpeed*.12*Math.sin(radians),28)-18] as [number,number,number],size:type==='clouds'?1.3:.025+random(w.seed,i*4+3)*.045});
 }return particles;
}
