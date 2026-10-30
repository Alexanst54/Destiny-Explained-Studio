import React from 'react';
import {useCurrentFrame} from 'remotion';
import {INK,PAL,blink} from '../animation/helpers';
type Props={x:number;y:number;scale?:number;look?:number;glow?:boolean};
export const Ghost:React.FC<Props>=({x,y,scale=1.5,look=0,glow=false})=>{
const frame=useCurrentFrame(),bob=Math.sin(frame/15)*14,tilt=Math.sin(frame/22)*6,eye=blink(frame+30,110),gaze=look+Math.sin(frame/40)*0.6,SW=6;
return <g transform={`translate(${x} ${y+bob}) rotate(${tilt}) scale(${scale})`}>
{glow&&<circle r={140+Math.sin(frame/4)*10} fill={PAL.cyan} opacity={0.3}/>}
<polygon points="-60,-35 -108,-10 -60,25" fill={PAL.voidLight} stroke={INK} strokeWidth={SW} strokeLinejoin="round"/>
<polygon points="60,-35 108,-10 60,25" fill={PAL.voidLight} stroke={INK} strokeWidth={SW} strokeLinejoin="round"/>
<polygon points="-26,-64 0,-108 26,-64" fill={PAL.voidLight} stroke={INK} strokeWidth={SW} strokeLinejoin="round"/>
<polygon points="0,-70 60,-35 60,35 0,70 -60,35 -60,-35" fill={PAL.shell} stroke={INK} strokeWidth={SW} strokeLinejoin="round"/>
<polygon points="0,-46 40,-23 40,23 0,46 -40,23 -40,-23" fill="#dfeeff" stroke={INK} strokeWidth={4} strokeLinejoin="round"/>
<g transform={`scale(1 ${eye})`}><circle r={27} fill="#fff" stroke={INK} strokeWidth={5}/><circle cx={gaze*7} r={16} fill={PAL.cyan}/><circle cx={gaze*7} r={8} fill={INK}/><circle cx={gaze*7+5} cy={-6} r={4} fill="#fff"/></g></g>};