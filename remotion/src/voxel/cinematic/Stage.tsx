import React,{useLayoutEffect} from 'react';
import {useThree} from '@react-three/fiber';
import {PerspectiveCamera} from 'three';
import {VoxelEnvironment} from '../library/Library';
import {Block} from '../Models';
import {particleSeed} from '../timeline';
import type {Shot} from './schema';
import type {FilmCamera} from './motion';

export const FilmCameraRig:React.FC<{pose:FilmCamera}>=({pose})=>{
  const {camera}=useThree();
  useLayoutEffect(()=>{
    camera.position.set(...pose.position);camera.lookAt(...pose.target);
    (camera as PerspectiveCamera).fov=pose.fov;
    camera.updateProjectionMatrix();camera.updateMatrixWorld();
  },[camera,pose]);
  return null;
};
export const Stage:React.FC<{environment:Shot['environment'];halo:boolean}>=({environment,halo})=>{
  if(environment==='europa'||environment==='black-garden'||environment==='pyramid-interior')return <VoxelEnvironment location={environment}/>;
  if(environment==='light-space')return <group>
    <Block position={[0,-0.15,0]} size={[5,0.3,5]} color="#263746"/>
    {Array.from({length:24},(_,i)=><Block key={i}
      position={[(particleSeed(i,4)-0.5)*14,particleSeed(i,5)*9,-4-particleSeed(i,6)*7]}
      size={[0.05,0.05,0.05]} color="#8deaff" emissive/>)}
  </group>;
  return <group>
    <VoxelEnvironment location="the-tower" halo={halo}/>
    {environment==='golden-age-vision'&&Array.from({length:10},(_,i)=><Block key={i}
      position={[(i-4.5)*0.65,1.5+particleSeed(i,7)*2,-6]} size={[0.08,0.08,0.08]} color="#ffd27a" emissive/>)}
    {environment==='collapse-vision'&&Array.from({length:12},(_,i)=><Block key={i}
      position={[(particleSeed(i,8)-0.5)*5,0.15,-1-particleSeed(i,9)*2]}
      rotation={[0,particleSeed(i,10)*3,0.2]} size={[0.35,0.3,0.4]} color="#43536b"/>)}
  </group>;
};
