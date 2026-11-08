import React from 'react';
import type {VoxelEpisodeDef,AlignedWord} from '../src/voxel/episode/schema';
import {captionSegment} from '../hybrid/state';
import {normalizedWord,wordMotion} from './captions';
export const PolishedCaptions:React.FC<{episode:VoxelEpisodeDef;words:AlignedWord[];frame:number;scene:VoxelEpisodeDef['scenes'][number];reducedMotion?:boolean}>=({episode,words,frame,scene,reducedMotion=false})=>{
 const c=episode.shorts!.captions,segment=captionSegment(words,frame,scene.startFrame,scene.startFrame+scene.durationFrames,c.maxWords,true);if(!segment.length)return null;
 const minimal=c.style==='cinematic-reveal',base=c.fontSize??(c.style==='high-impact'?54:46),longest=Math.max(...segment.map(w=>w.text.length)),fontSize=longest>28?Math.max(30,base*28/longest):base;
 const emphasis=new Set((c.emphasis??[]).map(normalizedWord));
 return <div data-caption-style={c.style} style={{position:'absolute',left:c.leftPx??80,right:c.rightPx??180,bottom:c.bottomPx,padding:'22px 26px',borderRadius:minimal?5:16,background:'#06101ef2',color:c.color??'#f7fbff',fontFamily:'Arial, sans-serif',fontSize,fontWeight:c.style==='high-impact'?850:700,lineHeight:1.3,textAlign:'center',overflowWrap:'anywhere',wordBreak:'normal',border:'1px solid #638296',boxShadow:'0 4px 20px #0008'}}>
  {segment.map((w,i)=>{const emph=emphasis.has(normalizedWord(w.text)),m=wordMotion(c.style,w.start,w.end,frame,emph,reducedMotion);return <React.Fragment key={i}><span data-active={m.active} data-emphasized={emph} style={{display:'inline-block',maxWidth:'100%',opacity:m.opacity,transform:`translateY(${m.y}px) scale(${m.scale})`,transformOrigin:'center bottom',color:m.active||emph?(c.accent??'#ffe297'):(c.color??'#f7fbff'),textDecoration:emph&&c.style==='documentary-clean'?'underline':undefined,textShadow:c.style==='high-impact'&&emph?'0 2px 0 #000':undefined,padding:'0 2px',borderBottom:m.active&&c.style==='kinetic-words'?'3px solid '+(c.accent??'#ffe297'):'3px solid transparent'}}>{w.text}</span>{' '}</React.Fragment>;})}
 </div>;
};
