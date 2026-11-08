import React,{useMemo} from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {episodeSchema,validateWords} from '../src/voxel/episode/schema';
import type {VoxelEpisodeProps} from '../src/voxel/episode/VoxelEpisode';
import {findScene} from '../src/voxel/episode/state';
import {CinematicEpisode} from '../src/voxel/cinematic/CinematicEpisode';
import {captionTiming,transitionMotion,audioGain,sourceTitle} from './state';
import {voxelVisualEpisode} from './adapter';
import {visualRegistry} from './Visuals';
import {CaptionLayer} from './CaptionLayer';
export const HybridShort:React.FC<VoxelEpisodeProps&{reducedMotion?:boolean}>=({episode,preview,alignedWords,reducedMotion=false})=>{
 const valid=useMemo(()=>episodeSchema.parse(episode),[episode]),voxel=useMemo(()=>voxelVisualEpisode(valid),[valid]);
 const timing=useMemo(()=>captionTiming(valid,alignedWords),[valid,alignedWords]);
 if(!preview&&(!timing.exact||valid.subtitles.status!=='ready'||(valid.audio.voiceover.enabled&&valid.audio.voiceover.status!=='ready')))throw new Error('Final Short requires ready Kokoro narration and complete validated word timestamps');
 const frame=useCurrentFrame(),scene=findScene(valid,frame),visual=scene.visual!,local=frame-scene.startFrame;
 const motion=transitionMotion(visual.transition.type,local,visual.transition.durationFrames,reducedMotion),Component=visual.type==='voxel'?undefined:visualRegistry[visual.type];
 const hypothetical=['hypothesis','alternate-history'].includes(valid.shorts!.mode),sources=visual.sources;
 return <AbsoluteFill style={{background:'#091423',fontFamily:'Arial, sans-serif',overflow:'hidden'}}>
  <AbsoluteFill style={{opacity:motion.opacity,transform:`translateX(${motion.x}%) scale(${motion.scale})`,clipPath:`inset(0 ${motion.wipe}% 0 0)`}}>
   {visual.type==='voxel'?<CinematicEpisode episode={voxel} preview={true} visualOnly draftQuality={preview&&valid.shorts?.quality==='draft'}/>:Component&&<Component visual={visual} frame={local} duration={scene.durationFrames} reducedMotion={reducedMotion}/>}
   {visual.type==='voxel'&&visual.headline&&<div style={{position:'absolute',top:155,left:85,right:180,color:'#fff',fontSize:48,fontWeight:800,textShadow:'0 3px 12px #000',overflowWrap:'anywhere'}}>{visual.headline}</div>}
  </AbsoluteFill>
  {motion.flash>0&&<AbsoluteFill style={{background:'#fff',opacity:motion.flash}}/>}
  <div style={{position:'absolute',top:90,left:85,right:180,color:'#ffe297',background:'#071321e8',padding:'10px 16px',fontSize:21,borderRadius:5}}>{hypothetical?'HYPOTHETICAL · ALTERNATE HISTORY · NOT CANON':visual.type==='voxel'?'ARTISTIC VISUAL RECONSTRUCTION':'SOURCE CONFIDENCE: '+valid.shorts!.confidence.toUpperCase()}</div>
  {preview&&!timing.exact&&<div data-caption-fallback style={{position:'absolute',top:260,left:85,right:180,fontSize:22,color:'#fff',background:'#071321e8',padding:8}}>SILENT PREVIEW · ESTIMATED CAPTION TIMING</div>}
  <CaptionLayer episode={valid} words={timing.words} frame={frame} scene={scene}/>
  <div style={{position:'absolute',left:85,right:180,bottom:135,color:'#b4cad9',fontSize:20,lineHeight:1.3,overflowWrap:'anywhere'}}>{sources.length?'Sources: '+sources.map(id=>sourceTitle(valid,id)).join(' · '):'Source review required'}{valid.shorts!.audio.tracks.filter(t=>t.provenance.license==='CC-BY').map(t=>' · '+t.provenance.attribution).join('')}</div>
  <div style={{position:'absolute',bottom:95,left:85,right:180,height:4,background:'#2d4255'}}><div style={{width:`${frame/Math.max(1,valid.format.durationFrames-1)*100}%`,height:'100%',background:'#edc77e'}}/></div>
  {!preview&&valid.audio.voiceover.enabled&&<Audio src={staticFile(valid.audio.voiceover.source)} volume={valid.shorts!.audio.voiceVolume}/>}
  {valid.shorts!.audio.tracks.map(t=><Sequence key={t.id} from={t.startFrame} durationInFrames={t.durationFrames} layout="none"><Audio src={t.source.startsWith('data:')?t.source:staticFile(t.source)} volume={f=>audioGain(t,f+t.startFrame,timing.words)}/></Sequence>)}
 </AbsoluteFill>;
};
