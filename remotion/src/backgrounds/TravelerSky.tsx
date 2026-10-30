import React from 'react';
import {useCurrentFrame} from 'remotion';
import {INK} from '../animation/helpers';
import {GROUND,HEIGHT,WIDTH} from '../project/timeline';
const Cloud:React.FC<{x:number;y:number;s?:number}>=({x,y,s=1})=>{const parts=[{cx:0,cy:0,rx:110,ry:44},{cx:-70,cy:14,rx:70,ry:34},{cx:80,cy:16,rx:80,ry:36}];return <g transform={`translate(${x} ${y}) scale(${s})`}>{parts.map((p,i)=><ellipse key={`o${i}`} {...p} fill={INK} stroke={INK} strokeWidth={12}/>)}{parts.map((p,i)=><ellipse key={`f${i}`} {...p} fill="#fff"/>)}</g>};
export const TravelerSky:React.FC=()=>{const frame=useCurrentFrame(),drift=(speed:number,offset:number)=>((frame*speed+offset)%1500)-210;return <svg width={WIDTH} height={HEIGHT} viewBox={`0 0 ${WIDTH} ${HEIGHT}`} style={{position:'absolute',inset:0}}>
<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#b9c9ff"/><stop offset=".5" stopColor="#ffd9e8"/><stop offset="1" stopColor="#fff1cf"/></linearGradient></defs>
<rect width={WIDTH} height={HEIGHT} fill="url(#sky)"/>
{Array.from({length:18},(_,i)=><circle key={i} cx={(i*173)%WIDTH} cy={((i*97)%600)+40} r={3+i%3} fill="#fff" opacity={.4+.6*Math.abs(Math.sin((frame+i*11)/20))}/>)}
<g transform="translate(540 640)"><circle r={385} fill="none" stroke="#fff" strokeWidth={10} opacity={.5} strokeDasharray="40 30" transform={`rotate(${frame*.15})`}/><circle r={330} fill="#fff8ee" stroke={INK} strokeWidth={8}/>
<path d="M -150 -210 Q -30 -60 -90 90 L -40 190" fill="none" stroke={INK} strokeWidth={8} strokeLinecap="round" strokeLinejoin="round"/>
<path d="M 120 -250 Q 60 -120 150 -20" fill="none" stroke={INK} strokeWidth={8} strokeLinecap="round"/>
<path d="M -330 20 Q 0 90 330 20" fill="none" stroke="#e7d9f5" strokeWidth={14} strokeLinecap="round"/></g>
<polygon points="-50,1380 220,1000 450,1380" fill="#cdb8f0" stroke={INK} strokeWidth={6} strokeLinejoin="round"/>
<polygon points="300,1380 640,930 960,1380" fill="#b9a2e8" stroke={INK} strokeWidth={6} strokeLinejoin="round"/>
<polygon points="790,1380 970,1120 1160,1380" fill="#cdb8f0" stroke={INK} strokeWidth={6} strokeLinejoin="round"/>
<Cloud x={drift(.6,100)} y={380} s={1.1}/><Cloud x={drift(.9,800)} y={1000} s={.8}/><Cloud x={drift(.4,400)} y={1180} s={.9}/>
<rect y={GROUND} width={WIDTH} height={HEIGHT-GROUND} fill="#8fd9b8"/><line x1={0} x2={WIDTH} y1={GROUND} y2={GROUND} stroke={INK} strokeWidth={8}/><rect y={GROUND+40} width={WIDTH} height={HEIGHT-GROUND} fill="#7cc8a6"/>
</svg>};