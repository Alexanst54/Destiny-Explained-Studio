import React, {useLayoutEffect, useMemo, useRef} from 'react';
import {InstancedMesh, Matrix4} from 'three';
import {Block} from '../Models';
import {particleSeed} from '../timeline';

export const Traveler: React.FC<{halo: boolean}> = ({halo}) => {
  const mesh = useRef<InstancedMesh>(null);
  const cells = useMemo(() => {
    const points: [number, number, number][] = [];
    for (let x=-5;x<=5;x++) for (let y=-5;y<=5;y++) for (let z=-5;z<=5;z++) {
      const distance = x*x+y*y+z*z;
      if (distance <= 25 && distance >= 16) points.push([x*0.46,y*0.46,z*0.46]);
    }
    return points;
  }, []);
  useLayoutEffect(() => {
    const matrix = new Matrix4();
    cells.forEach((p, i) => mesh.current!.setMatrixAt(i, matrix.makeTranslation(...p)));
    mesh.current!.instanceMatrix.needsUpdate = true;
  }, [cells]);
  return <group position={[0, 6.5, -10]}>
    <instancedMesh ref={mesh} args={[undefined, undefined, cells.length]} frustumCulled={false}>
      <boxGeometry args={[0.48,0.48,0.48]}/>
      <meshStandardMaterial color="#c2c8d2" roughness={0.95}/>
    </instancedMesh>
    {/* Dark cubical scars, without textures or external models. */}
    <Block position={[-0.5,-0.9,2.02]} size={[0.23,1.1,0.17]} color="#69768c"/>
    <Block position={[-0.25,-1.4,1.8]} size={[0.6,0.2,0.18]} color="#69768c"/>
    {halo && <mesh position={[0,0,0.3]}>
      <torusGeometry args={[2.8,0.08,4,32]}/>
      <meshBasicMaterial color="#ffe9a6"/>
    </mesh>}
  </group>;
};
export const Tower: React.FC = () => <group>
  <Block position={[0,-0.22,0]} size={[24,0.4,24]} color="#263746"/>
  <Block position={[0,-0.01,0]} size={[5.8,0.06,4.8]} color="#415363"/>
  {[-1,1].map(side => <group key={side}>
    <Block position={[side*3.3,0.7,-3]} size={[1.1,1.4,1.2]} color="#34455b"/>
    <Block position={[side*3.3,1.65,-3]} size={[0.8,0.5,0.9]} color="#43536b"/>
    <Block position={[side*3.1,1.12,-0.1]} size={[0.16,0.18,5.5]} color="#69768c"/>
    {[-2,0,2].map(z => <Block key={z} position={[side*3.1,0.55,z]}
      size={[0.2,1.1,0.2]} color="#43536b"/>)}
  </group>)}
  <Block position={[0,0.65,-3.6]} size={[5.8,0.14,0.2]} color="#69768c"/>
  {Array.from({length:20}, (_,i) => {
    const height=0.5+particleSeed(i,4)*2.1;
    return <Block key={i} position={[(i-9.5)*0.85,height/2-0.4,-7-particleSeed(i,5)*2]}
      size={[0.65,height,0.8]} color={i%2?'#34455b':'#43536b'}/>;
  })}
</group>;
