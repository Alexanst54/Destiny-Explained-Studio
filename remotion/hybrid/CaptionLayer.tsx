import React from 'react';
import type {AlignedWord,VoxelEpisodeDef} from '../src/voxel/episode/schema';
import {captionSegment} from './state';
export const CaptionLayer:React.FC<{episode:VoxelEpisodeDef;words:AlignedWord[];frame:number;scene:VoxelEpisodeDef['scenes'][number]}>=({episode,words,frame,scene})=>{
 const cfg=episode.shorts!.captions,segment=captionSegment(words,frame,scene.startFrame,scene.startFrame+scene.durationFrames,cfg.maxWords);
 const dynamic=cfg.style==='dynamic-shorts',minimal=cfg.style==='cinematic-minimal';
 const fontBase=minimal?40:dynamic?48:44,longest=Math.max(1,...segment.map(w=>w.text.length)),fontSize=longest>28?Math.max(36,fontBase*28/longest):fontBase;
 if(!segment.length)return null;
 return <div data-caption-style={cfg.style} style={{position:'absolute',left:80,right:180,bottom:cfg.bottomPx,padding:minimal?'16px 22px':'24px 28px',borderRadius:minimal?4:18,background:'rgba(4,10,20,.94)',color:'#fff',fontFamily:'Arial, sans-serif',fontSize,fontWeight:dynamic?800:600,lineHeight:1.25,textAlign:'center',overflowWrap:'anywhere',wordBreak:'normal',boxShadow:'0 4px 20px #0006',border:minimal?'none':'1px solid #8fa5b7',maxWidth:820}}>
  {segment.map((w,i)=><React.Fragment key={i}><span data-active={w.active} style={{color:w.active?'#ffe297':'#fff',textDecoration:w.active&&minimal?'underline':undefined,display:'inline',textShadow:w.active&&dynamic?'0 0 10px #ffdc6740':undefined}}>{w.text}</span>{' '}</React.Fragment>)}
 </div>;
};
