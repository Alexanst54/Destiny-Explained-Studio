import type {EnvironmentDirector,ProjectPolish,Quality} from './schema';
import {random,clamp} from '../characters/animations/state.ts';
export function effectBudget(p:ProjectPolish|undefined,quality:Quality,weatherRequested=0){
 const scale=quality==='draft'?(p?.previewEffectScale??.4):1,total=Math.min(128,Math.floor((p?.particleBudget??96)*scale)),details=Math.min(48,Math.floor((p?.detailBudget??24)*scale));
 const weather=Math.min(weatherRequested,Math.floor(total*.6));return {total,weather,atmosphere:total-weather,details};
}
export function atmosphere(c:EnvironmentDirector,frame:number,reduced=false){
 const drama=c.preset==='whirlwind',t=frame/30,flicker=reduced?0:Math.sin(t*.7+c.seed)*c.lightVariation;
 const intensity=c.intensity,light=clamp((drama?.55:1)-intensity*.18+flicker,.2,1.3);
 return {sky:drama?'#162c48':c.preset==='mystery'?'#38425d':c.preset==='dust'?'#a49480':'#7197a2',horizon:drama?'#b08767':'#c4d4cf',light,fogNear:8+(1-c.depth)*14,fogFar:26+(1-c.depth)*22,drama,t};
}
export type EnvironmentBlock={position:[number,number,number];size:[number,number,number];color:string;rotation:number};
export function environmentBlocks(c:EnvironmentDirector,frame:number,count:number){
 const items:EnvironmentBlock[]=[],t=frame/30;
 for(let i=0;i<Math.min(48,count);i++){
  const layer=i%3,x=(random(c.seed,i*5)-.5)*28,z=-7-layer*6-random(c.seed,i*5+1)*3,height=1.4+random(c.seed,i*5+2)*(3+layer),w=.8+random(c.seed,i*5+3)*1.4;
  const sway=c.preset==='whirlwind'?Math.sin(t*.9+i)*.035*c.intensity:0,shift=Math.sin(t*.18+layer)*c.parallax*.2;
  items.push({position:[x+shift,height/2,z],size:[w,height,w*.7],color:layer===0?'#496e78':layer===1?'#5b808b':'#7795a1',rotation:sway});
  items.push({position:[x+shift,height+.08,z],size:[w*1.15,.18,w*.9],color:'#c2af82',rotation:sway});
  items.push({position:[x+shift,height*.65,z+w*.36],size:[w*.2,height*.35,.05],color:c.preset==='whirlwind'?'#dca56b':'#a7d1d2',rotation:sway});
 }return items;
}
export function atmosphereParticles(c:EnvironmentDirector,frame:number,count:number){
 const t=frame/30,wrap=(x:number,n:number)=>((x%n)+n)%n;
 return Array.from({length:Math.min(128,count)},(_,i)=>{const wind=c.preset==='whirlwind'?2.8:.25,fall=c.preset==='rain'?6:c.preset==='snow'?1:-.25;return {position:[wrap(random(c.seed,i*3)*30+t*wind,30)-15,wrap(random(c.seed,i*3+1)*10-t*fall,10),-3-random(c.seed,i*3+2)*22] as [number,number,number],size:c.preset==='whirlwind'?.055:.035};});
}
