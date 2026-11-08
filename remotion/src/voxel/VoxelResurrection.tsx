import React, {useLayoutEffect} from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import {Block, Ghost, Guardian} from './Models';
import {particleSeed, resurrectionState} from './timeline';

type State = ReturnType<typeof resurrectionState>;
const CameraRig: React.FC<{state: State}> = ({state}) => {
  const {camera} = useThree();
  useLayoutEffect(() => {
    camera.position.set(Math.sin(state.cameraAngle) * state.cameraDistance,
      4.4, Math.cos(state.cameraAngle) * state.cameraDistance);
    camera.lookAt(0, 1.85, 0);
    camera.updateMatrixWorld();
  }, [camera, state.cameraAngle, state.cameraDistance]);
  return null;
};

const LightParticles: React.FC<{state: State}> = ({state}) => <group>
  {Array.from({length: 48}, (_, i) => {
    const phase = ((state.t * 0.46 + particleSeed(i, 0)) % 1 + 1) % 1;
    const angle = particleSeed(i, 1) * Math.PI * 2 + state.t * 0.7;
    const radius = 0.25 + particleSeed(i, 2) * 0.85;
    const size = (0.035 + particleSeed(i, 3) * 0.055) * Math.sin(phase * Math.PI) * state.beam;
    return <group key={i} position={[Math.cos(angle) * radius, 0.2 + phase * 3.4,
      Math.sin(angle) * radius]} rotation={[state.t + i, i, state.t * 0.6]} scale={size}>
      <Block size={[1, 1, 1]} color={i % 3 === 0 ? '#ffe9a6' : '#a7f6ff'} emissive/>
    </group>;
  })}
</group>;

const ResurrectionBeam: React.FC<{state: State}> = ({state}) => {
  const top = state.ghostY - 0.25;
  const bottom = 0.28;
  return <group position={[state.ghostX, 0, 0]}>
    <mesh position={[0, (top + bottom) / 2, 0]}>
      <cylinderGeometry args={[0.12, 0.95, top - bottom, 8, 1, true]}/>
      <meshBasicMaterial color="#8deaff" transparent opacity={state.beam * 0.24}
        depthWrite={false} side={2}/>
    </mesh>
    <mesh position={[0, (top + bottom) / 2, 0]}>
      <cylinderGeometry args={[0.025, 0.09, top - bottom, 6]}/>
      <meshBasicMaterial color="#e1ffff" transparent opacity={state.beam * 0.8} depthWrite={false}/>
    </mesh>
    <mesh position={[0, 0.035, 0]} rotation={[-Math.PI / 2, 0, 0]}>
      <ringGeometry args={[0.6, 1, 8]}/>
      <meshBasicMaterial color="#8deaff" transparent opacity={state.beam * 0.65} depthWrite={false}/>
    </mesh>
    <pointLight position={[0, 1.8, 0.8]} color="#8deaff" intensity={state.beam * 8} distance={6}/>
  </group>;
};

export const VoxelResurrection: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const state = resurrectionState(frame);
  return <AbsoluteFill style={{backgroundColor: '#101a2b'}}>
    <ThreeCanvas width={width} height={height} camera={{fov: 42, near: 0.1, far: 80,
      position: [0, 4.4, 10.5]}} gl={{antialias: true, alpha: false}}>
      <color attach="background" args={['#101a2b']}/>
      <fog attach="fog" args={['#101a2b', 16, 38]}/>
      <CameraRig state={state}/>
      <ambientLight intensity={1.1}/>
      <directionalLight position={[4, 7, 5]} intensity={2.4} color="#ffe2b5"/>
      <directionalLight position={[-5, 4, -3]} intensity={2} color="#8aa8ff"/>
      <Block position={[0, -0.22, 0]} size={[24, 0.4, 24]} color="#263746"/>
      <Block position={[0, -0.01, 0]} size={[4.4, 0.06, 3.4]} color="#415363"/>
      {[-1, 1].map(side => <group key={side}>
        <Block position={[side * 3.3, 0.7, -3]} size={[1.1, 1.4, 1.2]} color="#34455b"/>
        <Block position={[side * 3.3, 1.65, -3]} size={[0.8, 0.5, 0.9]} color="#43536b"/>
        <Block position={[side * 5.2, 1, -6]} size={[2, 2, 2]} color="#2a3b50"/>
      </group>)}
      {/* A distant cuboid moon keeps the entire scene procedural and voxel styled. */}
      <Block position={[0, 6.5, -11]} size={[3.7, 3.7, 3.7]} color="#95a9bd"
        rotation={[0.12, 0.25, 0.1]}/>
      <Guardian rise={state.rise} t={state.t} position={[state.guardianX, state.guardianY, 0]}
        rotation={[0, 0, state.guardianRotation]}/>
      <Ghost t={state.t} position={[state.ghostX, state.ghostY, 0]}/>
      <ResurrectionBeam state={state}/>
      <LightParticles state={state}/>
    </ThreeCanvas>
    <div style={{position: 'absolute', top: 140, left: 70, right: 70, color: '#eef7ff',
      textAlign: 'center', fontFamily: 'sans-serif', fontSize: 56, fontWeight: 800,
      letterSpacing: 3}}>THE LIGHT RETURNS</div>
    <div style={{position: 'absolute', bottom: 230, left: 80, right: 80, padding: '25px 30px',
      backgroundColor: 'rgba(10, 17, 30, 0.85)', border: '2px solid #6a91a7',
      borderRadius: 16, color: '#e6faff', textAlign: 'center', fontFamily: 'sans-serif',
      fontSize: 46, fontWeight: 700}}>{state.caption}</div>
  </AbsoluteFill>;
};
