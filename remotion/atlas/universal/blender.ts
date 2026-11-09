/** Opt-in visual extension selector. Never changes legacy AtlasReference or episode data. */
import {z} from 'zod';
import bindings from '../../blender/venus_vault/atlas-bindings.json' with {type:'json'};
import {universalAtlas as atlas} from './index.ts';
const optionsSchema=z.object({quality:z.enum(['draft','balanced','cinematic']).default('balanced'),seed:z.number().int().min(0).max(2147483647).default(42),camera:z.enum(['wide','reveal','orbit','low-angle','close-up']).default('wide'),animation:z.string().default('idle'),startFrame:z.number().int().min(0).max(17999).default(0),frames:z.number().int().min(1).max(120).default(1),fps:z.union([z.literal(24),z.literal(30)]).default(30),width:z.number().int().min(320).max(1920).multipleOf(2).default(960),height:z.number().int().min(240).max(1920).multipleOf(2).default(540)}).strict();
export function selectBlenderAsset(selectionId:string,options:unknown={}) {
 const o=optionsSchema.parse(options);if(o.startFrame+o.frames>18000)throw Error('Frame range exceeds bound');
 const boss=Object.entries(bindings.bosses).find(([id])=>id===selectionId)?.[1],env=Object.entries(bindings.environments).find(([id])=>id===(boss?.environmentId??selectionId))?.[1];
 if(!env)throw Error('Atlas selection has no implemented Venus/Vault generator');
 const environmentId=env.generator,entity=atlas.locations.find(l=>l.id===(boss?.environmentId??selectionId));
 if(entity?.blenderAssetId!==env.assetId)throw Error('Environment binding differs from Atlas');
 if(boss){
  if(atlas.bosses.find(b=>b.id===selectionId)?.blenderAssetId!==boss.assetId)throw Error('Boss binding differs from Atlas');
  if(!(boss.animations as string[]).includes(o.animation))throw Error('Unsupported boss animation');
  if(!atlas.encounterBosses.some(b=>b.bossId===selectionId&&atlas.encounterLocations.some(l=>l.encounterId===b.encounterId&&l.locationId===environmentId)))throw Error('Boss arena not related in Atlas');
 }else if(o.animation!=='idle')throw Error('Environment-only selection needs idle');
 return {version:1,selectionId,environmentId,bossId:boss?selectionId:null,...o};
}
export const blenderSelections=Object.keys(bindings.environments).concat(Object.keys(bindings.bosses));
