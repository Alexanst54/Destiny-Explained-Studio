import React from 'react';
import {AbsoluteFill,useCurrentFrame,useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {Guardian,Ghost,Block} from '../Models';
import {actorPose} from './motion';
import {FilmCameraRig} from './Stage';
import {VoxelBurst,Hologram,LightRay} from './Effects';
import type {TimedAction,TimedEvent,Timeline} from './timeline';

const animations=['walk','run','jump','fall','resurrect','combat','interact','look-up'] as const;
export const MotionLab:React.FC<{intensity:Timeline['intensity']}>=({intensity})=>{
  const frame=useCurrentFrame(),{width,height}=useVideoConfig();
  const animation=animations[Math.min(7,Math.floor(frame/90))],local=frame%90;
  const moving=animation==='walk'||animation==='run';
  const clip:TimedAction={id:'motion-demo',actor:'guardian',animation,at:{sceneFrame:0},durationFrames:90,start:0,end:90,
    from:moving?[-1,.02,0]:[0,.02,0],to:moving?[1,.02,0]:[0,.02,0],height:1.3,purpose:'Demonstrate the procedural animation library'};
  const pose=actorPose('guardian',[clip],local,intensity);
  const event:TimedEvent={id:'effect-demo',at:{sceneFrame:0},type:'particles',start:0,end:90,durationFrames:90,
    position:[0,.2,0],strength:.8,purpose:'Show reusable effects without changing the educational episode'};
  return <AbsoluteFill style={{backgroundColor:'#101a2b'}}>
    <ThreeCanvas width={width} height={height} dpr={1} camera={{fov:42,near:.1,far:50,position:[4,4,10]}}>
      <color attach="background" args={['#101a2b']}/>
      <FilmCameraRig pose={{position:[4,4,10],target:[0,1.8,0],fov:42}}/>
      <ambientLight intensity={1.1}/><directionalLight position={[4,7,5]} intensity={2.4} color="#ffe2b5"/>
      <directionalLight position={[-5,4,-3]} intensity={2} color="#8aa8ff"/>
      <Block position={[0,-.2,0]} size={[10,.4,10]} color="#263746"/>
      <Guardian rise={pose.rise} t={frame/30} pose={pose.joints} position={pose.position} rotation={pose.rotation}/>
      <Ghost t={frame/30} position={[.7,3.4+Math.sin(frame/15)*.1,0]}/>
      {animation==='resurrect'&&<LightRay event={{...event,type:'beam',position:[.7,3.4,0],to:[0,.3,0]}} frame={local}/>}
      {animation==='combat'&&local>=20&&local<68&&<VoxelBurst event={{...event,type:'explosion',start:20,end:68,durationFrames:48,position:[1,1.4,1]}} frame={local} intensity={intensity}/>}
      {animation==='interact'&&<Hologram event={{...event,type:'hologram',position:[0,2.5,.5]}} frame={local}/>}
      {animation==='resurrect'&&<VoxelBurst event={event} frame={local} intensity={intensity}/>}
    </ThreeCanvas>
    <div style={{position:'absolute',top:150,width:'100%',textAlign:'center',fontFamily:'sans-serif',fontSize:54,color:'#eef7ff',fontWeight:800}}>
      MOTION LAB · {animation.toUpperCase()}</div>
    <div style={{position:'absolute',bottom:300,width:'100%',textAlign:'center',fontFamily:'sans-serif',fontSize:32,color:'#ffe9a6'}}>PROCEDURAL DEMO · {intensity.toUpperCase()}</div>
  </AbsoluteFill>;
};
