import React,{useLayoutEffect,useMemo,useRef} from 'react';
import {Color,InstancedMesh,Object3D} from 'three';
import type {EnvironmentDirector} from './schema';
import {atmosphere,environmentBlocks,atmosphereParticles} from './environment';
export const EnvironmentLayer:React.FC<{config:EnvironmentDirector;frame:number;detailCount:number;particleCount:number;reducedMotion?:boolean}>=({config,frame,detailCount,particleCount,reducedMotion=false})=>{
 const blocks=useRef<InstancedMesh>(null),particles=useRef<InstancedMesh>(null),dummy=useMemo(()=>new Object3D(),[]),a=atmosphere(config,frame,reducedMotion);
 const geometry=environmentBlocks(config,reducedMotion?0:frame,detailCount),points=atmosphereParticles(config,frame,particleCount);
 useLayoutEffect(()=>{
  const b=blocks.current,p=particles.current;if(!b||!p)return;b.count=geometry.length;p.count=points.length;
  for(let i=0;i<geometry.length;i++){const g=geometry[i];dummy.position.set(...g.position);dummy.rotation.set(0,0,g.rotation);dummy.scale.set(...g.size);dummy.updateMatrix();b.setMatrixAt(i,dummy.matrix);b.setColorAt(i,new Color(g.color));}
  for(let i=0;i<points.length;i++){const g=points[i];dummy.position.set(...g.position);dummy.rotation.set(0,0,0);dummy.scale.set(g.size,config.preset==='rain'?g.size*6:g.size,g.size);dummy.updateMatrix();p.setMatrixAt(i,dummy.matrix);}
  b.instanceMatrix.needsUpdate=true;if(b.instanceColor)b.instanceColor.needsUpdate=true;p.instanceMatrix.needsUpdate=true;
 },[geometry,points,dummy,config.preset]);
 return <group>
  <ambientLight intensity={a.light*.3}/><directionalLight position={[-6,8,-8]} color={a.horizon} intensity={a.light*1.5}/>
  <instancedMesh ref={blocks} args={[undefined,undefined,144]} frustumCulled={false}><boxGeometry args={[1,1,1]}/><meshStandardMaterial roughness={1}/></instancedMesh>
  <instancedMesh ref={particles} args={[undefined,undefined,128]} frustumCulled={false}><boxGeometry args={[1,1,1]}/><meshBasicMaterial color={a.drama?'#e3ae72':'#d8e3e5'} transparent opacity={config.intensity*.4} depthWrite={false}/></instancedMesh>
  {Array.from({length:Math.min(6,detailCount)},(_,i)=><mesh key={i} position={[0,5+i*2,-29-i*.05]}><planeGeometry args={[70,2.05]}/><meshBasicMaterial color={new Color(a.horizon).lerp(new Color(a.sky),i/6)} fog={false}/></mesh>)}
 </group>;
};
