import React,{useLayoutEffect,useRef,useMemo} from 'react';
import {InstancedMesh,Matrix4,Quaternion,Vector3,Euler} from 'three';
import type {TimedEvent,Timeline} from './timeline';
import {profiles,smooth} from './timeline';
import {particleSeed} from '../timeline';
import {Block} from '../Models';

export const VoxelBurst:React.FC<{event:TimedEvent;frame:number;intensity:Timeline['intensity']}>=({event,frame,intensity})=>{
  const ref=useRef<InstancedMesh>(null),count=profiles[intensity].particles;
  const local=frame-event.start,t=local/30,p=local/event.durationFrames;
  useLayoutEffect(()=>{
    const matrix=new Matrix4(),rotation=new Quaternion(),scale=new Vector3(),position=new Vector3();
    for(let i=0;i<count;i++){
      const angle=particleSeed(i,0)*Math.PI*2,r=0.4+particleSeed(i,1)*2;
      if(event.type==='explosion'){
        position.set(Math.cos(angle)*r*t,Math.max(0.08,(1.4+particleSeed(i,2)*3)*t-2.5*t*t),Math.sin(angle)*r*t);
      }else{
        const phase=(p*1.7+particleSeed(i,2))%1;
        position.set(Math.cos(angle+t)*r*0.35,phase*2.2,Math.sin(angle+t)*r*0.35);
      }
      position.add(new Vector3(...event.position));
      const size=(0.05+particleSeed(i,3)*0.12)*event.strength*(event.type==='explosion'?1-p:Math.sin(((p*1.7+particleSeed(i,2))%1)*Math.PI));
      scale.setScalar(Math.max(0,size));rotation.setFromEuler(new Euler(t+i,t*1.3+i,t*0.8));
      matrix.compose(position,rotation,scale);ref.current!.setMatrixAt(i,matrix);
    }
    ref.current!.instanceMatrix.needsUpdate=true;
  },[count,event,t,p]);
  return <instancedMesh ref={ref} args={[undefined,undefined,count]} frustumCulled={false}>
    <boxGeometry args={[1,1,1]}/>
    <meshStandardMaterial color={event.type==='explosion'?'#ffd27a':'#8deaff'}
      emissive={event.type==='explosion'?'#ffd27a':'#8deaff'} emissiveIntensity={1.4} roughness={0.85}/>
  </instancedMesh>;
};
export const Hologram:React.FC<{event:TimedEvent;frame:number}>=({event,frame})=>{
  const local=frame-event.start,fade=Math.min(smooth(local/9),smooth((event.durationFrames-local)/9));
  return <group position={event.position} scale={fade*event.strength} rotation={[0,local*0.008,0]}>
    <mesh><boxGeometry args={[1.2,1.2,1.2]}/><meshBasicMaterial color="#8deaff" wireframe/></mesh>
    {Array.from({length:8},(_,i)=>{const a=i*Math.PI/4;return <Block key={i}
      position={[Math.cos(a)*1.2,Math.sin(a*2)*0.25,Math.sin(a)*1.2]} size={[0.16,0.16,0.16]} color="#8deaff" emissive/>;})}
    <mesh rotation={[Math.PI/2,0,0]}><torusGeometry args={[1.2,0.02,4,24]}/><meshBasicMaterial color="#8deaff"/></mesh>
  </group>;
};
export const LightRay:React.FC<{event:TimedEvent;frame:number}>=({event,frame})=>{
  const from=new Vector3(...event.position),to=new Vector3(...event.to!),delta=to.clone().sub(from);
  const rotation=useMemo(()=>new Quaternion().setFromUnitVectors(new Vector3(0,1,0),delta.clone().normalize()),[event]);
  const p=(frame-event.start)/event.durationFrames,opacity=Math.min(smooth(p*7),smooth((1-p)*7))*event.strength;
  return <group position={from.clone().add(to).multiplyScalar(0.5)} quaternion={rotation}>
    <mesh><cylinderGeometry args={[0.06,0.42,delta.length(),6,1,true]}/>
      <meshBasicMaterial color="#8deaff" transparent opacity={opacity*0.22} depthWrite={false} side={2}/></mesh>
    <mesh><cylinderGeometry args={[0.025,0.06,delta.length(),6]}/>
      <meshBasicMaterial color="#e6faff" transparent opacity={opacity*0.8} depthWrite={false}/></mesh>
  </group>;
};
