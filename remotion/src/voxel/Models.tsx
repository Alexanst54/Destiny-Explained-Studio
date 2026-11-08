import React from 'react';
import type {ThreeElements} from '@react-three/fiber';

export const Block: React.FC<{
  position?: [number, number, number];
  size: [number, number, number];
  color: string;
  rotation?: [number, number, number];
  emissive?: boolean;
}> = ({position, size, color, rotation, emissive = false}) => (
  <mesh position={position} rotation={rotation}>
    <boxGeometry args={size}/>
    <meshStandardMaterial color={color} roughness={0.85}
      emissive={emissive ? color : '#000000'} emissiveIntensity={emissive ? 1.8 : 0}/>
  </mesh>
);

export const Guardian: React.FC<{rise: number; t: number; headTilt?: number} & ThreeElements['group']> =
  ({rise, t, headTilt = 0, ...props}) => {
    const breath = Math.sin(t * 2.5) * 0.018 * rise;
    return <group {...props}>
      <Block position={[-0.23, 0.46, 0]} size={[0.36, 0.82, 0.4]} color="#353a61"/>
      <Block position={[0.23, 0.46, 0]} size={[0.36, 0.82, 0.4]} color="#353a61"/>
      {[-0.23, 0.23].map(x => <Block key={x} position={[x, 0.1, 0.12]}
        size={[0.42, 0.2, 0.65]} color="#20273d"/>)}
      <group position={[0, breath, 0]}>
        <Block position={[0, 1.06, 0]} size={[0.88, 0.24, 0.52]} color="#dbb56b"/>
        <Block position={[0, 1.54, 0]} size={[1, 0.76, 0.6]} color="#7462ba"/>
        <Block position={[0, 1.58, 0.33]} size={[0.25, 0.3, 0.08]} color="#f7cd7c"/>
        <Block position={[0, 1.12, -0.39]} size={[1.05, 1.55, 0.13]} color="#433568"/>
        {[-1, 1].map(side => <group key={side} position={[side * 0.67, 1.8, 0]}
          rotation={[0, 0, side * (0.08 + Math.sin(rise * Math.PI) * 0.55)]}>
          <Block position={[0, -0.06, 0]} size={[0.44, 0.4, 0.62]} color="#a090d8"/>
          <Block position={[0, -0.52, 0]} size={[0.3, 0.65, 0.36]} color="#7462ba"/>
          <Block position={[0, -0.9, 0.02]} size={[0.32, 0.23, 0.38]} color="#20273d"/>
        </group>)}
        <group rotation={[headTilt, 0, 0]} position={[0, 2.25, 0]}>
          <group position={[0, -2.25, 0]}>
        <Block position={[0, 2.25, 0]} size={[0.82, 0.72, 0.72]} color="#433568"/>
        <Block position={[0, 2.23, 0.38]} size={[0.65, 0.36, 0.08]} color="#171e33"/>
        <Block position={[0, 2.27, 0.43]} size={[0.52, 0.11, 0.04]} color="#80efff" emissive/>
        <Block position={[0, 2.64, -0.06]} size={[0.94, 0.12, 0.86]} color="#7462ba"/>
          </group>
        </group>
      </group>
    </group>;
  };

export const Ghost: React.FC<{t: number} & ThreeElements['group']> = ({t, ...props}) => (
  <group {...props}>
    <group rotation={[0, Math.sin(t * 1.4) * 0.14, Math.sin(t * 1.8) * 0.06]}>
      <Block size={[0.46, 0.46, 0.34]} color="#e8edf7" rotation={[0, 0, Math.PI / 4]}/>
      {[0, 1, 2, 3].map(i => {
        const angle = i * Math.PI / 2;
        return <Block key={i} position={[Math.sin(angle) * 0.4, Math.cos(angle) * 0.4, 0]}
          rotation={[0, 0, Math.PI / 4]} size={[0.27, 0.27, 0.25]} color="#c7b7ef"/>;
      })}
      <Block position={[0, 0, 0.22]} size={[0.25, 0.25, 0.11]} color="#27334f"/>
      <Block position={[0, 0, 0.29]} size={[0.13, 0.13, 0.06]} color="#8cf5ff" emissive/>
    </group>
  </group>
);
