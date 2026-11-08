import {weatherState} from '../../../weather/state';
import {LivingWorldLayer} from '../../../living/LivingWorldLayer';
import {narrativeLabel} from '../../../living/director';
import React, {useLayoutEffect, useMemo} from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import {Color} from 'three';
import {Block, Ghost, Guardian} from '../Models';
import {LightParticles, ResurrectionBeam} from '../VoxelResurrection';
import {VoxelEnvironment,VoxelElements} from '../library/Library';
import {environmentStyle} from '../library/catalog';
import {AtlasEnvironment} from '../library/AtlasEnvironment';
import {atlasRecipe} from '../../../atlas/recipes';
import {episodeSchema, validateWords} from './schema';
import type {VoxelEpisodeDef, AlignedWord} from './schema';
import {cameraPose, captionWords, findScene, sceneState} from './state';
import type {CameraPose} from './state';

export type VoxelEpisodeProps = {episode: VoxelEpisodeDef; preview: boolean; alignedWords?: AlignedWord[]; visualOnly?:boolean; draftQuality?:boolean};
const Camera: React.FC<{pose: CameraPose}> = ({pose}) => {
  const {camera} = useThree();
  useLayoutEffect(() => {
    camera.position.set(...pose.position);
    camera.lookAt(...pose.target);
    camera.updateMatrixWorld();
  }, [camera, pose]);
  return null;
};
export const VoxelEpisode: React.FC<VoxelEpisodeProps> = (props) => {
  const {episode, preview, alignedWords} = props;
  const valid = useMemo(() => episodeSchema.parse(episode), [episode]);
  const words = useMemo(() => alignedWords ? validateWords(alignedWords, valid) : undefined, [alignedWords, valid]);
  if (!preview && ((valid.audio.voiceover.enabled && valid.audio.voiceover.status !== 'ready') ||
    valid.subtitles.status !== 'ready' || !words))
    throw new Error('Final render requires ready audio and validated aligned words; use preview for drafts');
  const frame = useCurrentFrame();
  const {width, height, fps} = useVideoConfig();
  const scene = findScene(valid, frame);
  const state = sceneState(scene, frame, fps);
  const fx = (name: typeof scene.effects[number]) => scene.effects.includes(name);
  const darkness = fx('sky-darken') ? 0.25 + state.progress * 0.7 : 0;
  const lightning = fx('distant-lightning') && ((state.local >= 60 && state.local < 64) ||
    (state.local >= 180 && state.local < 185));
  const style = environmentStyle(scene.location==='the-tower'?'tower':scene.location);
  const atlasState=scene.atlas?atlasRecipe(scene.atlas):undefined;
  const sky = new Color(atlasState?.palette.sky??style.sky).lerp(new Color('#030610'), darkness);
  const ws=scene.weather?weatherState(scene.weather,state.local):undefined,weatherLight=ws?.active?ws.light:1;
  const captions = captionWords(scene, frame, preview ? undefined : words);
  return <AbsoluteFill style={{backgroundColor:'#101a2b'}}>
    <ThreeCanvas width={width} height={height} dpr={1} camera={{fov:42,near:0.1,far:80,
      position:[0,4.4,13]}} gl={{antialias:true,alpha:false}}>
      <color attach="background" args={[sky]}/>
      <fog attach="fog" args={[sky,24,50]}/>
      <Camera pose={cameraPose(scene.camera,state.progress)}/>
      <ambientLight intensity={(lightning ? 2 : style.ambient-darkness*0.6)*weatherLight}/>
      <directionalLight position={[4,7,5]} intensity={(2.4-darkness*1.5)*weatherLight} color={style.key}/>
      <directionalLight position={[-5,4,-3]} intensity={2*weatherLight} color={style.fill}/>
      {fx('golden-glow') && <pointLight position={[0,6,-6]} color="#ffe9a6" intensity={35} distance={15}/>}
      {scene.atlas?<AtlasEnvironment reference={scene.atlas} frame={state.local} halo={fx('traveler-halo')}/>:<VoxelEnvironment location={scene.location} halo={fx('traveler-halo')}/>}
      <LivingWorldLayer world={scene.livingWorld} weather={scene.weather} frame={state.local}/>
      <VoxelElements items={scene.elements??[]} frame={state.local}/>
      {(!scene.livingWorld||scene.actions.some(a=>a.actor==='guardian'))&&<Guardian rise={state.rise} t={state.t} headTilt={state.lookUp ? -0.28*state.progress : 0}
        position={[state.guardianX,state.guardianY,0]} rotation={[0,0,state.guardianRotation]}/>}
      {(!scene.livingWorld||scene.actions.some(a=>a.actor==='ghost'))&&<Ghost t={state.t} position={[state.ghostX,state.ghostY,0]}
        rotation={[0,state.scan ? Math.sin(state.t*2)*0.4 : 0,0]}/>}
      {state.scan && <mesh position={[0,state.ghostY,1.1]} rotation={[Math.PI/2,0,0]}>
        <cylinderGeometry args={[0.05,0.6,2,6,1,true]}/>
        <meshBasicMaterial color="#8deaff" transparent opacity={0.14} depthWrite={false} side={2}/>
      </mesh>}
      {fx('resurrection-beam') && <ResurrectionBeam state={state}/>}
      <LightParticles state={{...state,beam:state.particles}}/>
      {lightning && <group position={[4,6,-8]}>
        <Block size={[0.08,1.4,0.08]} color="#e6faff" rotation={[0,0,-0.3]} emissive/>
        <Block position={[-0.25,-1.2,0]} size={[0.08,1.2,0.08]} color="#e6faff" rotation={[0,0,0.45]} emissive/>
      </group>}
    </ThreeCanvas>
    <div style={{position:'absolute',top:140,left:70,right:70,color:'#eef7ff',textAlign:'center',
      fontFamily:'sans-serif',fontSize:preview&&scene.livingWorld?44:56,fontWeight:800,letterSpacing:3,textShadow:'0 2px 8px #101a2b'}}>{valid.title}</div>
    {preview && <div style={{position:'absolute',top:230,width:'100%',textAlign:'center',color:'#ffe9a6',
      fontFamily:'sans-serif',fontSize:24}}>PREVIEW · SILENT · ESTIMATED CAPTIONS</div>}
    {atlasState&&<div style={{position:'absolute',top:275,left:65,right:65,textAlign:'center',color:'#ffe9a6',fontFamily:'sans-serif',fontSize:23,lineHeight:1.4}}>{atlasState.reconstructed?'ARTISTIC RECONSTRUCTION':'STYLIZED GAME-INSPIRED ENVIRONMENT'} · {atlasState.label}</div>}
    {scene.livingWorld&&<div style={{position:'absolute',top:345,left:65,right:65,textAlign:'center',color:'#ffe9a6',fontFamily:'sans-serif',fontSize:24}}>{narrativeLabel(scene.livingWorld)}</div>}
    {captions.length > 0 && <div style={{position:'absolute',bottom:valid.subtitles.safeAreaBottomPx,
      left:80,right:80,padding:'25px 30px',backgroundColor:'rgba(10,17,30,0.85)',
      border:'2px solid #6a91a7',borderRadius:16,color:'#e6faff',textAlign:'center',
      fontFamily:'sans-serif',fontSize:42,lineHeight:1.3,fontWeight:700}}>
      {[captions.slice(0,3),captions.slice(3,6)].filter(line => line.length).map((line,i) =>
        <div key={i}>{line.map((w,j) => <span key={j} style={{color:w.active?'#ffe9a6':'#e6faff'}}>{w.text}{' '}</span>)}</div>)}
    </div>}
    <div style={{position:'absolute',bottom:75,left:80,right:80,textAlign:'center',color:'#b1bfd0',
      fontFamily:'sans-serif',fontSize:20}}>{valid.disclaimer}</div>
    {!preview && valid.audio.voiceover.enabled && <Audio src={staticFile(valid.audio.voiceover.source)}/>}
  </AbsoluteFill>;
};
