import {Color} from 'three';
import {costumeVariation} from '../../polish/characters';
import type {Quality} from '../../polish/schema';
import React from 'react';
import {Block} from '../../src/voxel/Models';
import type {Cast} from '../../living/schema';
import {characterVisual} from '../index';
import {characterState} from '../animations/state';
export const VoxelCharacter:React.FC<{actor:Cast;frame:number;quality?:Quality;contactShadows?:boolean;override?:Parameters<typeof characterState>[2]}>=({actor,frame,override,quality='final',contactShadows=true})=>{
 const {visual,variant}=characterVisual(actor.characterId,actor.variantId),s=characterState(actor,frame,override);
 if(!s.active||visual.model==='unknown')return null;
 const variation=costumeVariation(actor),palette=actor.palette??visual.palette;
 const [body,trim,glow]=actor.director?[new Color(palette[0]).offsetHSL(variation.hue,.02,0).getStyle(),palette[1],palette[2]]:palette,equipment=actor.equipment??visual.equipment;
 const j=s.pose,k=visual.model,heavy=k==='heavy',four=k==='four-arm',krill=k==='krill',vex=k==='vex',hive=k==='hive'||k==='giant';
 return <>{actor.director&&contactShadows&&quality==='final'&&<mesh position={[s.position[0],s.position[1]+.02,s.position[2]]} rotation={[-Math.PI/2,0,0]} scale={[actor.scale*.65,actor.scale*.38,1]}><circleGeometry args={[1,10]}/><meshBasicMaterial color="#07131e" transparent opacity={.24*j.visibility} depthWrite={false}/></mesh>}<group position={[s.position[0],s.position[1]+j.y,s.position[2]]} rotation={[j.lean,s.yaw,j.roll]} scale={actor.scale*visual.scale*j.visibility}>
  {k==='sphere'?<mesh position={[0,3,0]}><sphereGeometry args={[2.5,12,8]}/><meshStandardMaterial color="#e3e5de" roughness={1}/></mesh>:
   k==='terminal'?<group><Block position={[0,.7,0]} size={[1.3,1.4,.7]} color={body}/><Block position={[0,1.2,.38]} size={[1,.7,.08]} color={glow} emissive/></group>:
   k==='drone'?<group position={[0,1.4,0]} rotation={[0,frame/90,0]}><Block size={[.4,.4,.4]} color={glow} emissive/>{[0,1,2,3].map(i=><group key={i} rotation={[0,0,i*Math.PI/2]}><Block position={[0,.4,0]} size={[.28,.35,.3]} color={trim}/></group>)}</group>:
   k==='beast'?<group><Block position={[0,.4,0]} size={[.7,.5,1.2]} color={body}/>{[-1,1].flatMap(side=>[-1,1].map(front=><group key={`${side}:${front}`} position={[side*.45,.45,front*.4]} rotation={[Math.sin(frame/3+front)*.4,0,side*.5]}><Block position={[0,-.25,0]} size={[.17,.6,.17]} color={trim}/></group>))}<Block position={[0,.7,.25]} size={[.35,.35,.35]} color={glow} emissive/></group>:
   <group scale={[(heavy?1.3:krill?.65:1)*variation.width,krill?.8:1,1]}>
    {[-1,1].map(side=><group key={side} position={[side*.22,.88,0]} rotation={[side<0?j.legL:j.legR,0,0]}><Block position={[0,-.4,0]} size={[heavy?.42:.26,.8,.3]} color={body}/><Block position={[0,-.78,.12]} size={[.33,.15,.5]} color={trim}/></group>)}
    {actor.director&&<><Block position={[0,1.33,.26]} size={[.55,.13,.08]} color={trim}/>{quality==='final'&&<Block position={[variation.accent?.25:-.25,1.62,.26]} size={[.14,.2,.08]} color={glow} emissive/>}</>}
    <Block position={[0,1.25,0]} size={[heavy?1.1:.8,.85,.45]} color={body}/>
    {(equipment.includes('robe')||equipment.includes('coat'))&&<Block position={[0,.85,-.17]} size={[.88,1.1,.25]} color={trim}/>}
    {[-1,1].flatMap(side=>Array.from({length:four?2:1},(_,row)=><group key={`${side}:${row}`} position={[side*.55,1.6-row*.4,0]} rotation={[side<0?j.armL:j.armR,0,side*.1]}>
      <Block position={[0,-.32,0]} size={[heavy?.42:.23,.65,.25]} color={row?trim:body}/><Block position={[0,-.68,.02]} size={[.24,.16,.28]} color={trim}/>
      {equipment.includes('pauldrons')&&row===0&&<Block size={[.5,.3,.55]} color={trim}/>}
    </group>))}
    <group position={[0,2.05,0]} rotation={[0,j.head,0]}>
     <Block size={[krill?.5:vex?.7:.6,.56,.5]} color={equipment.includes('hood')?body:variant.civilization==='awoken'?'#7d9cc1':trim}/>
     {actor.director&&four&&<><Block position={[-.25,-.12,.27]} size={[.12,.2,.14]} color={body}/><Block position={[.25,-.12,.27]} size={[.12,.2,.14]} color={body}/>{[-1,1].map(side=><Block key={side} position={[side*.14,.16,.28]} size={[.07,.07,.04]} color={glow} emissive/>)}</>}
     {vex&&<Block position={[0,.3,-.12]} size={[1,.1,.25]} color={trim}/>}
     {(hive||krill)?[-1,0,1].map((x,i)=><Block key={x} position={[x*.15,i===1?.1:-.03,.27]} size={[.08,.08,.04]} color={glow} emissive/>):<Block position={[0,.04,.27]} size={[.38,.09,.04]} color={glow} emissive/>}
     {variant.civilization==='exo'&&[-1,1].map(side=><Block key={side} position={[side*.33,-.1,0]} size={[.12,.25,.35]} color={body}/>)}
     {equipment.includes('crest')&&<Block position={[0,.4,0]} size={[.12,.4,.4]} color={trim}/>}
    </group>
    {vex&&<Block position={[0,1.15,.25]} size={[.3,.26,.08]} color={glow} emissive/>}
    {k==='giant'&&[-1,1].map(side=><Block key={side} position={[side*.9,1.7,-.4]} size={[1.2,1.6,.15]} rotation={[0,side*.3,side*-.4]} color={body}/>)}
   </group>}
 </group></>;
};
