import {clamp,smooth} from '../characters/animations/state.ts';
export const normalizedWord=(text:string)=>text.toLocaleLowerCase('en-US').replace(/[^a-z0-9'-]/g,'');
export function wordMotion(style:string,start:number,end:number,frame:number,emphasized:boolean,reduced=false){
 const t=frame/30,active=t>=start&&t<end,entry=smooth((frame-start*30)/6),exit=smooth((end*30-frame)/5);
 const pop=active?Math.sin(clamp((t-start)/Math.max(.001,end-start))*Math.PI):0;
 return {active,opacity:style==='cinematic-reveal'?entry:1,scale:reduced?1:style==='kinetic-words'?1+pop*.09:style==='high-impact'&&emphasized?1+pop*.07:1,y:reduced?0:style==='cinematic-reveal'?(1-entry)*6:0,glow:active?Math.min(entry,exit):0};
}
export function contrastRatio(foreground:string,background='#06101e'){
 const lum=(hex:string)=>{const c=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255).map(v=>v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4));return c[0]*.2126+c[1]*.7152+c[2]*.0722;};
 const a=lum(foreground),b=lum(background);return (Math.max(a,b)+.05)/(Math.min(a,b)+.05);
}
