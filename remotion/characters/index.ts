import raw from './catalog.json' with {type:'json'};
import {characterCatalogSchema} from './schema.ts';
import {locationsById,normalizeSearch} from '../atlas/index.ts';
export const characterCatalog=characterCatalogSchema.parse(raw);
export const charactersById=new Map(characterCatalog.characters.map(c=>[c.id,c]));
for(const c of characterCatalog.characters)for(const id of c.locations)if(!locationsById.has(id))throw new Error(`Unknown character Atlas link: ${c.id}/${id}`);
export function characterVisual(id:string,variantId?:string){
 const c=charactersById.get(id);if(!c)throw new Error('Unknown character');
 const v=variantId?c.variants.find(v=>v.id===variantId):c.variants[0];
 if(!v)throw new Error('Unknown character variant');return {character:c,variant:v,visual:v.visual};
}
export function searchCharacters(query='',civilization='',faction=''){
 const q=normalizeSearch(query);return characterCatalog.characters.filter(c=>(!q||normalizeSearch([c.id,c.names.fr,c.names.en,...c.variants.flatMap(v=>[v.names.fr,v.names.en])].join(' ')).includes(q))&&(!civilization||c.civilization===civilization||c.variants.some(v=>v.civilization===civilization))&&(!faction||c.faction===faction));
}
