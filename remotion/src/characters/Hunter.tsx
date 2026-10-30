import React from 'react';
import {spring,useCurrentFrame,useVideoConfig} from 'remotion';
import {INK,PAL,blink} from '../animation/helpers';
import type {Pose} from '../types';
const SW=6;
const Limb:React.FC<{x:number;y:number;angle:number;w:number;h:number;fill:string}>=({x,y,angle,w,h,fill})=><g transform={`translate(${x} ${y}) rotate(${angle})`}><rect x={-w/2} y={-w/2} width={w} height={h} rx={w/2} fill={fill} stroke={INK} strokeWidth={SW} strokeLinejoin="round"/></g>;
type Props={x:number;y:number;pose:Pose;talking?:boolean;scale?:number};
export const Hunter:React.FC<Props>=({x,y,pose,talking=false,scale=1.5})=>{
const frame=useCurrentFrame(),{fps}=useVideoConfig(),t=frame/fps;let legL=0,legR=0,armL=8,armR=-8,lift=0,rot=0,eyeOpen=blink(frame);
const speak=talking||pose==='talk',breathe=Math.sin(t*5)*3;
if(pose==='talk')armR=-35+Math.sin(t*7)*14;
if(pose==='walk'){const s=Math.sin(t*Math.PI*3.2);legL=s*35;legR=-s*35;armL=-s*30+8;armR=-s*30-8;lift=-Math.abs(s)*14}
if(pose==='jump'){const ph=(t*1.2)%1;lift=-Math.sin(ph*Math.PI)*260;armL=150;armR=-150;legL=20;legR=-20}
if(pose==='resurrect'){const p=spring({frame:frame-8,fps,config:{damping:15,stiffness:50}});rot=(1-p)*-88;lift=-(1-p)*50;if(p<.75)eyeOpen=.08;if(frame>70){const ph=(((frame-70)/fps)*1.4)%1;lift-=Math.sin(ph*Math.PI)*180;armL=140;armR=-140}}
const mouth=speak?.3+.7*Math.abs(Math.sin(frame*.8)):0,sway=pose==='walk'?Math.sin(t*Math.PI*3.2)*4:0,shadowScale=Math.max(.4,1+lift/400);
return <g><ellipse cx={x} cy={y+6} rx={95*scale*.7*shadowScale} ry={14*shadowScale} fill={INK} opacity={.18}/>
<g transform={`translate(${x} ${y+lift}) scale(${scale}) rotate(${rot})`}><g transform={`translate(0 ${-breathe*.5})`}>
<g transform={`rotate(${sway} 0 -245)`}><path d="M -62 -245 L 62 -245 L 100 -30 Q 0 -6 -100 -30 Z" fill={PAL.voidDark} stroke={INK} strokeWidth={SW} strokeLinejoin="round"/></g>
<Limb x={62} y={-225} angle={armR} w={30} h={100} fill={PAL.voidLight}/>
<Limb x={-24} y={-110} angle={legL} w={36} h={112} fill={PAL.void}/>
<Limb x={24} y={-110} angle={legR} w={36} h={112} fill={PAL.void}/>
<rect x={-55} y={-250} width={110} height={150} rx={40} fill={PAL.voidLight} stroke={INK} strokeWidth={SW}/>
<rect x={-55} y={-170} width={110} height={16} fill={PAL.gold} stroke={INK} strokeWidth={SW-2}/>
<circle cx={0} cy={-205} r={15} fill={PAL.gold} stroke={INK} strokeWidth={SW-2}/>
<Limb x={-62} y={-225} angle={armL} w={30} h={100} fill={PAL.void}/>
<g transform="translate(0 -318)"><path d="M -34 -64 Q 14 -150 66 -58 Z" fill={PAL.void} stroke={INK} strokeWidth={SW} strokeLinejoin="round"/>
<circle r={78} fill={PAL.void} stroke={INK} strokeWidth={SW}/>
<ellipse cx={0} cy={10} rx={58} ry={44} fill={PAL.cream} stroke={INK} strokeWidth={SW}/>
{[-22,22].map(ex=><g key={ex}><ellipse cx={ex} cy={6} rx={11} ry={16*eyeOpen} fill={INK}/>{eyeOpen>.5&&<circle cx={ex+4} cy={-1} r={4} fill="#fff"/>}</g>)}
<circle cx={-40} cy={28} r={8} fill={PAL.pink} opacity={.7}/><circle cx={40} cy={28} r={8} fill={PAL.pink} opacity={.7}/><ellipse cx={0} cy={30} rx={9} ry={3+10*mouth} fill={INK}/>
</g></g></g></g>};