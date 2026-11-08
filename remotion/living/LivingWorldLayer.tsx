import type {Quality} from '../polish/schema';
import React from 'react';
import {Block} from '../src/voxel/Models';
import type {LivingWorld,LivingShot} from './schema';
import type {Weather} from '../weather/schema';
import {directWorld} from './director';
import {VoxelCharacter} from '../characters/models/VoxelCharacter';
import {WeatherLayer} from '../weather/WeatherLayer';
export const LivingWorldLayer:React.FC<{world?:LivingWorld;shot?:LivingShot;weather?:Weather;frame:number;shotStart?:number;quality?:Quality;contactShadows?:boolean;manageAtmosphere?:boolean}>=({world,shot,weather,frame,shotStart=0,quality='final',contactShadows=true,manageAtmosphere=true})=><group>
 {directWorld(world,shot).map(actor=>{const o=shot?.animations?.find(x=>x.id===actor.id);return <VoxelCharacter key={actor.id} actor={actor} frame={frame} quality={quality} contactShadows={contactShadows} override={o?{...o,startFrame:shotStart}:undefined}/>;})}
 {world?.props.map(p=><group key={p.id} position={p.position}><Block position={[0,.65,0]} size={[.8,1.3,.5]} color="#67788d"/><Block position={[0,1,.27]} size={[.65,.5,.05]} color="#72e3ee" emissive/></group>)}
 {weather&&<WeatherLayer weather={weather} frame={frame} manageAtmosphere={manageAtmosphere}/>}
</group>;
