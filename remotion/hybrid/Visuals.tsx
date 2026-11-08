import React from 'react';
import type {HybridVisual} from './schema';
import {clamp,ease,mix} from './state';
export type VisualProps={visual:HybridVisual;frame:number;duration:number;reducedMotion:boolean};
const accent='#f7d186',muted='#a9bfd0';
const labelStyle:React.CSSProperties={fontFamily:'Arial, sans-serif',fill:'#eff6ff',fontSize:30,fontWeight:700};
const Headline:React.FC<{text:string}>=({text})=><div style={{position:'absolute',top:145,left:85,right:175,color:'#eff6ff',fontSize:52,fontWeight:800,lineHeight:1.12,overflowWrap:'anywhere'}}>{text}</div>;
export const MapVisual:React.FC<VisualProps>=({visual,frame,duration,reducedMotion})=>{
 if(visual.type!=='map')return null;const p=ease(frame/Math.max(1,duration-1)),zoom=reducedMotion?1:mix(visual.camera.zoomFrom,visual.camera.zoomTo,p),x=mix(visual.camera.from[0],visual.camera.to[0],p),y=mix(visual.camera.from[1],visual.camera.to[1],p);
 return <><Headline text={visual.headline}/><svg viewBox="0 0 1000 1000" style={{position:'absolute',top:370,left:30,width:960,height:1000,overflow:'hidden'}} role="img" aria-label="Schematic map, not astronomical coordinates">
  <defs><pattern id="grid" width="80" height="80" patternUnits="userSpaceOnUse"><path d="M 80 0 L 0 0 0 80" fill="none" stroke="#263c52"/></pattern></defs><rect width="1000" height="1000" fill="url(#grid)"/>
  <g transform={`translate(500 500) scale(${zoom}) translate(${-x*10} ${-y*10})`}>
   {visual.routes.map((r,i)=>{const a=visual.nodes.find(n=>n.id===r.from)!,b=visual.nodes.find(n=>n.id===r.to)!,t=ease((frame-i*12)/Math.max(1,duration*.7));return <g key={i}><path d={`M${a.position[0]*10} ${a.position[1]*10} L${b.position[0]*10} ${b.position[1]*10}`} pathLength={1} stroke={accent} strokeWidth={5} strokeDasharray="1" strokeDashoffset={1-t}/><circle cx={mix(a.position[0],b.position[0],t)*10} cy={mix(a.position[1],b.position[1],t)*10} r={14} fill="#f2f5eb"/><text x={(a.position[0]+b.position[0])*5} y={(a.position[1]+b.position[1])*5-25} textAnchor="middle" style={{...labelStyle,fontSize:22,fill:accent}}>{r.label}</text></g>;})}
   {visual.nodes.map(n=><g key={n.id}><circle cx={n.position[0]*10} cy={n.position[1]*10} r={12} fill="#87cfd8"/><text x={clamp(n.position[0]*10,90,900)} y={n.position[1]*10+55} textAnchor="middle" style={labelStyle}>{n.label.length>34?n.label.slice(0,31)+'…':n.label}</text></g>)}
  </g></svg><div style={{position:'absolute',top:310,left:85,right:175,fontSize:24,color:accent}}>SCHEMATIC MAP · NOT ASTRONOMICAL COORDINATES</div></>;
};
export const TimelineVisual:React.FC<VisualProps>=({visual,frame,duration})=>{
 if(visual.type!=='timeline')return null;
 return <><Headline text={visual.headline}/><div style={{position:'absolute',top:400,left:95,right:180,borderLeft:'4px solid #56758c',paddingLeft:45}}>{visual.events.map((e,i)=>{const reveal=ease((frame-i*duration/visual.events.length)/18);return <div key={e.id} style={{opacity:reveal,marginBottom:28,padding:'18px 25px',border:'1px solid #3e6078',borderRadius:12,background:'#142438'}}><div style={{fontSize:24,color:accent}}>{e.date??e.period}{e.date?'':' · exact date unknown'}</div><div style={{fontSize:35,fontWeight:700,color:'#eff6ff',overflowWrap:'anywhere'}}>{e.label}</div><div style={{fontSize:21,color:muted}}>Evidence: {e.confidence}</div></div>;})}</div></>;
};
export const GraphicVisual:React.FC<VisualProps>=({visual,frame,duration,reducedMotion})=>{
 if(visual.type!=='graphic')return null;
 return <><Headline text={visual.headline}/><svg viewBox="0 0 1000 1000" style={{position:'absolute',top:370,left:20,width:960,height:1000}}><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill={accent}/></marker></defs>{visual.connections.map((e,i)=>{const a=visual.cards.find(c=>c.id===e.from)!,b=visual.cards.find(c=>c.id===e.to)!;return <line key={i} x1={a.position[0]*10} y1={a.position[1]*10} x2={b.position[0]*10} y2={b.position[1]*10} stroke={accent} strokeWidth={4} markerEnd="url(#arrow)" opacity={ease((frame-30)/20)}/>;})}</svg>
  {visual.cards.map((c,i)=>{const p=ease((frame-i*20)/20);return <div key={c.id} style={{position:'absolute',left:`${clamp(c.position[0],25,72)}%`,top:370+c.position[1]*8,transform:`translate(-50%,-50%) scale(${reducedMotion?1:.95+p*.05})`,width:650,padding:'28px 32px',borderRadius:18,border:'2px solid #6e889d',background:'#15283a',opacity:p,color:'#f0f7ff'}}><div style={{fontSize:35,fontWeight:800,color:accent,overflowWrap:'anywhere'}}>{c.title}</div><div style={{fontSize:29,lineHeight:1.35,marginTop:15,overflowWrap:'anywhere'}}>{c.body}</div></div>;})}
  {visual.counter&&<div style={{position:'absolute',top:1300,left:85,fontSize:38,color:accent}}>{visual.counter.label} · {Math.round(mix(visual.counter.from,visual.counter.to,ease(frame/duration)))}</div>}
 </>;
};
export const TextVisual:React.FC<VisualProps>=({visual,frame,reducedMotion})=>{
 if(visual.type!=='text')return null;const p=ease(frame/20);
 return <div style={{position:'absolute',top:410,left:85,right:180,color:'#f5f8ff',opacity:p,transform:reducedMotion?undefined:`translateY(${(1-p)*20}px)`}}><div style={{fontSize:25,color:accent,letterSpacing:4,marginBottom:28,textTransform:'uppercase'}}>{visual.kind}</div><h1 style={{fontSize:72,lineHeight:1.08,margin:0,overflowWrap:'anywhere'}}>{visual.headline}</h1><p style={{fontSize:42,lineHeight:1.3,color:muted,overflowWrap:'anywhere'}}>{visual.body}</p></div>;
};
export const visualRegistry={map:MapVisual,timeline:TimelineVisual,graphic:GraphicVisual,text:TextVisual};
