import React,{useMemo} from 'react';
import {AbsoluteFill,Audio,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {episodeSchema,validateWords} from '../episode/schema';
import type {VoxelEpisodeProps} from '../episode/VoxelEpisode';
import {captionWords,findScene} from '../episode/state';
import {Guardian,Ghost} from '../Models';
import {resolveDirection,estimatedWords,atFrame} from './timeline';
import {actorPose,cameraState,transitionState} from './motion';
import {FilmCameraRig,Stage} from './Stage';
import {VoxelBurst,Hologram,LightRay} from './Effects';
import {VoxelElements} from '../library/Library';
import {resolveEnvironment,environmentStyle} from '../library/catalog';

export const CinematicEpisode:React.FC<VoxelEpisodeProps>=({episode,preview,alignedWords})=>{
  const valid=useMemo(()=>episodeSchema.parse(episode),[episode]);
  const words=useMemo(()=>alignedWords?validateWords(alignedWords,valid):undefined,[alignedWords,valid]);
  if(!preview&&(!words||valid.subtitles.status!=='ready'||(valid.audio.voiceover.enabled&&valid.audio.voiceover.status!=='ready')))
    throw new Error('Cinematic final render requires ready narration and aligned words');
  const timeline=useMemo(()=>resolveDirection(valid,words??estimatedWords(valid)),[valid,words]);
  const frame=useCurrentFrame(),{width,height}=useVideoConfig();
  const {scene,shot,events}=atFrame(timeline,frame);
  const guardian=actorPose('guardian',scene.actions,frame,timeline.intensity),ghost=actorPose('ghost',scene.actions,frame,timeline.intensity);
  const camera=cameraState(timeline,scene,shot,frame,events),transition=transitionState(timeline,shot,frame);
  const sourceScene=valid.scenes.find(s=>s.id===scene.sceneId)!;
  const environment=resolveEnvironment(shot.environment,sourceScene.location);
  const style=environmentStyle(environment);
  const dark=environment==='collapse-vision',light=environment==='golden-age-vision';
  const captions=captionWords(findScene(valid,frame),frame,preview?undefined:words);
  const halo=valid.scenes.find(s=>s.id===scene.sceneId)!.effects.includes('traveler-halo');
  return <AbsoluteFill style={{backgroundColor:'#101a2b'}}>
    <ThreeCanvas width={width} height={height} dpr={1} camera={{fov:42,near:0.1,far:80,position:[0,4.4,13]}} gl={{antialias:true,alpha:false}}>
      <color attach="background" args={[style.sky]}/>
      <fog attach="fog" args={[style.sky,style.fogNear,style.fogFar]}/>
      <FilmCameraRig pose={camera}/>
      <ambientLight intensity={style.ambient}/>
      <directionalLight position={[4,7,5]} intensity={dark?1:2.4} color={style.key}/>
      <directionalLight position={[-5,4,-3]} intensity={2} color={style.fill}/>
      {light&&<pointLight position={[0,6,-6]} color="#ffe9a6" intensity={25} distance={15}/>}
      <Stage environment={environment} halo={halo}/>
      <VoxelElements items={shot.elements??sourceScene.elements??[]} frame={frame-scene.start}/>
      {shot.actors.guardian&&<Guardian rise={guardian.rise} t={frame/30} pose={guardian.joints}
        position={guardian.position} rotation={guardian.rotation}/>}
      {shot.actors.ghost&&<Ghost t={frame/30} position={ghost.position}
        rotation={[ghost.rotation[0],ghost.rotation[1],ghost.rotation[2]+Math.sin(frame/30*2.2)*0.03]}/>}
      {events.map(event=>event.type==='shake'?null:event.type==='hologram'?<Hologram key={event.id} event={event} frame={frame}/>:
        event.type==='beam'?<LightRay key={event.id} event={event} frame={frame}/>:
          <VoxelBurst key={event.id} event={event} frame={frame} intensity={timeline.intensity}/>)}
    </ThreeCanvas>
    {transition.opacity>0&&<AbsoluteFill style={{backgroundColor:'#101a2b',opacity:transition.type==='wipe'?1:transition.opacity,
      clipPath:transition.type==='wipe'?`inset(0 ${100*(1-transition.opacity)}% 0 0)`:undefined}}/>}
    <div style={{position:'absolute',top:140,left:70,right:70,color:'#eef7ff',textAlign:'center',fontFamily:'sans-serif',fontSize:56,fontWeight:800,
      letterSpacing:3,textShadow:'0 2px 8px #101a2b'}}>{valid.title}</div>
    {(preview||shot.environment.includes('vision'))&&<div style={{position:'absolute',top:230,width:'100%',textAlign:'center',color:'#ffe9a6',fontFamily:'sans-serif',fontSize:24}}>
      {preview?'PREVIEW · SILENT · ESTIMATED CUES':shot.environment==='collapse-vision'?'THE COLLAPSE · ILLUSTRATION':'THE GOLDEN AGE · ILLUSTRATION'}</div>}
    {captions.length>0&&<div style={{position:'absolute',bottom:valid.subtitles.safeAreaBottomPx,left:80,right:80,padding:'25px 30px',backgroundColor:'rgba(10,17,30,0.85)',
      border:'2px solid #6a91a7',borderRadius:16,color:'#e6faff',textAlign:'center',fontFamily:'sans-serif',fontSize:42,lineHeight:1.3,fontWeight:700}}>
      {[captions.slice(0,3),captions.slice(3,6)].filter(line=>line.length).map((line,i)=><div key={i}>{line.map((w,j)=><span key={j}
        style={{color:w.active?'#ffe9a6':'#e6faff'}}>{w.text}{' '}</span>)}</div>)}
    </div>}
    <div style={{position:'absolute',bottom:75,left:80,right:80,textAlign:'center',color:'#b1bfd0',fontFamily:'sans-serif',fontSize:20}}>{valid.disclaimer}</div>
    {!preview&&valid.audio.voiceover.enabled&&<Audio src={staticFile(valid.audio.voiceover.source)}/>}
  </AbsoluteFill>;
};
