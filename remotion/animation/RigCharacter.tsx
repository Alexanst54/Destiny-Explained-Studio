import {costumeVariation} from '../polish/characters';
import React,{useMemo,useEffect} from 'react';
import {BoxGeometry,SphereGeometry,CircleGeometry,MeshStandardMaterial,MeshBasicMaterial,Color} from 'three';
import {characterVisual} from '../characters/index';
import {rigBones} from './rig';
import type {Bone} from './rig';
import type {ActorFrame} from './director';
const cube=new BoxGeometry(1,1,1),orb=new SphereGeometry(.5,10,8),contact=new CircleGeometry(1,8),shadow=new MeshBasicMaterial({color:'#081322',transparent:true,opacity:.25,depthWrite:false});
export const RigCharacter:React.FC<{state:ActorFrame;contactShadows?:boolean}>=({state:s,contactShadows=true})=>{
 const a=s.actor,r=a.rig!,v=characterVisual(a.characterId,a.variantId).visual,palette=a.palette??v.palette,equipment=a.equipment??v.equipment;
 const bones=useMemo(()=>{const list=rigBones(r);if(r.archetype!=='servitor')for(const name of equipment){const head=['hood','visor','crest'].includes(name);list.push({id:'equipment-'+name,parent:head?'head':'torso',at:head?[0,name==='crest'?.4:0,name==='visor'?.28:-.07]:[0,.22,-.29],size:name==='crest'?[.12,.4,.35]:name==='visor'?[.4,.12,.05]:head?[.65,.58,.12]:[.65,.65,.15],material:1,detail:1});}return list;},[r,equipment.join(',')]);
 const key=palette.slice(0,3).join(',')+':'+(a.director?.seed??0)+':'+(a.director?.variation??0),materials=useMemo(()=>[new MeshStandardMaterial({color:a.director?new Color(palette[0]).offsetHSL(costumeVariation(a).hue,.02,0):palette[0],roughness:1}),new MeshStandardMaterial({color:palette[1],roughness:1}),new MeshBasicMaterial({color:palette[2]})],[key]);
 useEffect(()=>()=>materials.forEach(m=>m.dispose()),[materials]);
 const children=useMemo(()=>{const m=new Map<string|null,Bone[]>();for(const bone of bones)m.set(bone.parent,[...(m.get(bone.parent)??[]),bone]);return m;},[bones]);
 const renderBone=(b:Bone):React.ReactNode=><group key={b.id} name={b.id} position={b.at} rotation={s.pose.rotation[b.id]??[0,0,0]}>
  {b.size&&(b.detail??0)<=s.lod&&<mesh geometry={r.archetype==='servitor'&&b.id==='pelvis'?orb:cube} material={materials[b.material??0]} position={b.offset??[0,0,0]} scale={b.size} dispose={null}/>}
  {(children.get(b.id)??[]).map(renderBone)}
 </group>;
 if(!s.active)return null;
 return <>{contactShadows&&s.lod>0&&<mesh geometry={contact} material={shadow} dispose={null} rotation={[-Math.PI/2,0,0]} position={[s.position[0],s.position[1]+.015,s.position[2]]} scale={[a.scale*.6,a.scale*.35,1]}/>}
  <group position={[s.position[0],s.position[1]+s.pose.lift+(r.archetype==='servitor'?Math.sin((s.actor.rig!.seed+s.pose.lift)*.1)*.015:0),s.position[2]]} rotation={[0,s.yaw,0]} scale={[s.scale*costumeVariation(a).width,s.scale,s.scale]}>
   {(children.get(null)??[]).map(renderBone)}
  </group>
 </>;
};
