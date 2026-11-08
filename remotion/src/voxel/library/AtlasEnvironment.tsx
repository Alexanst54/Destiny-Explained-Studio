import React,{useMemo} from 'react';
import {VoxelEnvironment,VoxelBatch,VoxelElements} from './Library';
import {atlasRecipe} from '../../../atlas/recipes';
import {atlasBoxes} from '../../../atlas/geometry';
import type {AtlasReference} from '../../../atlas/index';

export const AtlasEnvironment:React.FC<{reference:AtlasReference;frame:number;halo?:boolean}>=({reference,frame,halo=false})=>{
 const recipe=useMemo(()=>atlasRecipe(reference),[reference]);
 const boxes=useMemo(()=>atlasBoxes(recipe,frame),[recipe,frame]);
 return <group>
  {recipe.baseEnvironment&&<VoxelEnvironment location={recipe.baseEnvironment} halo={halo}/>}
  <VoxelBatch boxes={boxes.filter(b=>!b.emissive)}/><VoxelBatch boxes={boxes.filter(b=>b.emissive)}/>
  {recipe.modules.includes('snow')&&<VoxelElements frame={frame} items={[{id:'atlas-snow',type:'snow',position:[0,0,-2],animation:'drift',count:32,seed:recipe.seed%65536,strength:.5}]}/>}
 </group>;
};
