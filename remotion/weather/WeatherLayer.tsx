import React,{useLayoutEffect,useMemo,useRef} from 'react';
import {useThree} from '@react-three/fiber';
import {Color,Fog,InstancedMesh,Object3D} from 'three';
import type {Weather} from './schema';
import {weatherParticles,weatherState} from './state';
const colors={clear:'#b8cee0',clouds:'#8995aa',rain:'#8ba6c1',thunderstorm:'#5d7693',snow:'#edf7ff',blizzard:'#e3f1ff',fog:'#9ba9ba',sandstorm:'#bf9563','strong-wind':'#b9b8aa',spores:'#bdc985',energy:'#88efff',supernatural:'#a69bd8'};
export const WeatherLayer:React.FC<{weather:Weather;frame:number}>=({weather,frame})=>{
 const {scene}=useThree(),ref=useRef<InstancedMesh>(null),s=weatherState(weather,frame),particles=weatherParticles(weather,frame);
 const dummy=useMemo(()=>new Object3D(),[]);
 useLayoutEffect(()=>{
  if(!ref.current)return;ref.current.count=particles.length;
  for(let i=0;i<particles.length;i++){const p=particles[i];dummy.position.set(...p.position);dummy.scale.set(p.size,p.type==='rain'||p.type==='thunderstorm'?p.size*7:p.size,p.size);dummy.updateMatrix();ref.current.setMatrixAt(i,dummy.matrix);ref.current.setColorAt(i,new Color(colors[p.type]));}
  ref.current.instanceMatrix.needsUpdate=true;if(ref.current.instanceColor)ref.current.instanceColor.needsUpdate=true;
 },[particles,dummy]);
 useLayoutEffect(()=>{
  if(!s.active)return;
  const oldFog=scene.fog,oldBackground=scene.background;
  const sky=new Color(colors[weather.type]).lerp(new Color(colors[weather.to?.type??weather.type]),s.mix).multiplyScalar(s.daylight*(1-s.intensity*.35)+s.lightning*.3);
  scene.background=sky;scene.fog=new Fog(sky,s.fogNear,s.fogFar);
  return ()=>{scene.fog=oldFog;scene.background=oldBackground;};
 },[scene,s.active,s.mix,s.daylight,s.intensity,s.lightning,s.fogNear,s.fogFar,weather]);
 if(!s.active)return null;
 return <group><ambientLight intensity={s.light*.45}/><directionalLight position={[8*s.daylight,6,-2]} color={s.daylight<.5?'#f7bc90':'#dceeff'} intensity={s.light*1.2}/>
  <instancedMesh ref={ref} args={[undefined,undefined,128]} frustumCulled={false}><boxGeometry args={[1,1,1]}/><meshBasicMaterial transparent opacity={s.intensity*.55} depthWrite={false}/></instancedMesh>
 </group>;
};
