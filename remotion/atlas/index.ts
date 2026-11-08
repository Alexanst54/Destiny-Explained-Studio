import {z} from 'zod';
import raw from './catalog.json' with {type:'json'};
import {atlasCatalogSchema,categories} from './schema.ts';
import type {AtlasLocation} from './schema';
// Validate once on load: the static bundle and render process share the same catalog.
export const atlas=atlasCatalogSchema.parse(raw);
export const locationsById=new Map(atlas.locations.map(p=>[p.id,p]));
export const sourcesById=new Map(atlas.sources.map(s=>[s.id,s]));
export const atlasRefSchema=z.object({locationId:z.string().min(1),variantId:z.string().min(1).optional()}).strict().superRefine((ref,ctx)=>{
 const place=locationsById.get(ref.locationId);
 if(!place)ctx.addIssue({code:'custom',path:['locationId'],message:'Unknown Atlas location'});
 else if(ref.variantId&&!place.variants.some(v=>v.id===ref.variantId))ctx.addIssue({code:'custom',path:['variantId'],message:'Unknown historical variant for this location'});
});
export type AtlasReference=z.infer<typeof atlasRefSchema>;
export const resolveAtlas=(ref:AtlasReference)=>{
 const location=locationsById.get(ref.locationId);
 if(!location)throw new Error(`Unknown Atlas location: ${ref.locationId}`);
 const variant=ref.variantId?location.variants.find(v=>v.id===ref.variantId):undefined;
 if(ref.variantId&&!variant)throw new Error(`Unknown Atlas variant: ${ref.variantId}`);
 const render=variant?.render??location.render;
 return {location,variant,render,appearance:variant?.appearance??location.appearance,
  reconstructed:render.mode!=='dedicated',label:(variant?.names??location.names).en};
};
export const normalizeSearch=(s:string)=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
export function searchAtlas({query='',category='',civilization='',era='',parentId=''}={}){
 const q=normalizeSearch(query);
 return atlas.locations.filter(p=>(!q||normalizeSearch([p.names.en,p.names.fr,...p.aliases,p.id,...p.variants.flatMap(v=>[v.names.en,v.names.fr])].join(' ')).includes(q))&&(!category||(category==='historical-variant'?p.variants.length>0:p.category===category))&&(!civilization||p.civilizations.includes(civilization))&&(!era||p.eras.includes(era)||p.variants.some(v=>v.eras.includes(era)))&&(!parentId||p.parentId===parentId));
}
export const atlasStatistics=()=>({locations:atlas.locations.length,categories:Object.fromEntries(categories.map(c=>[c,atlas.locations.filter(p=>p.category===c).length])),sourcedLocations:atlas.locations.filter(p=>p.sources.length).length,variants:atlas.locations.reduce((sum,p)=>sum+p.variants.length,0),manifestOnlyLocations:atlas.locations.filter(p=>p.canonStatus==='manifest-attested').length,dedicatedLocations:atlas.locations.filter(p=>p.render.mode==='dedicated').length,dedicatedEnvironments:[...new Set(atlas.locations.flatMap(p=>p.render.environment?[p.render.environment]:[]))],modularLocations:atlas.locations.filter(p=>p.render.mode!=='dedicated').length,coverage:atlas.coverage});
export const descendants=(id:string):AtlasLocation[]=>atlas.locations.filter(p=>p.parentId===id);
