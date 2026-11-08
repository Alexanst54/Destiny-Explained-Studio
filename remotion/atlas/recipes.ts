import {resolveAtlas,locationsById} from './index.ts';
import type {AtlasReference} from './index';
import type {AtlasFamily,AtlasModule} from './schema';
const presets:Record<AtlasFamily,{modules:AtlasModule[];ground:string;structure:string;accent:string;sky:string}>={
 human:{modules:['terrain','human'],ground:'#34414a',structure:'#6a7782',accent:'#c0e4ed',sky:'#182735'},
 'golden-age':{modules:['terrain','golden-age','vegetation'],ground:'#6b8775',structure:'#ddd8bd',accent:'#e9bf71',sky:'#45636c'},
 vex:{modules:['terrain','vex'],ground:'#4a5748',structure:'#968763',accent:'#a5e7db',sky:'#213534'},
 hive:{modules:['terrain','hive'],ground:'#383c36',structure:'#7a8061',accent:'#b1e796',sky:'#151e23'},
 cabal:{modules:['terrain','cabal'],ground:'#594c45',structure:'#934c4f',accent:'#f6c68e',sky:'#292635'},
 eliksni:{modules:['terrain','eliksni','future-city'],ground:'#68697c',structure:'#9294ae',accent:'#d7c18b',sky:'#39425d'},
 awoken:{modules:['terrain','awoken','cosmic'],ground:'#4d4e6c',structure:'#c3b8d3',accent:'#c5edfb',sky:'#27253f'},
 pyramid:{modules:['terrain','pyramid'],ground:'#282433',structure:'#463846',accent:'#dca862',sky:'#141321'},
 bray:{modules:['terrain','bray'],ground:'#738c9a',structure:'#b9cad0',accent:'#f2ad72',sky:'#263b4c'},
 'future-city':{modules:['terrain','future-city'],ground:'#4b5166',structure:'#787ca3',accent:'#a8ede8',sky:'#282d4f'},
 cosmic:{modules:['terrain','cosmic'],ground:'#3d3b55',structure:'#756c91',accent:'#bceaf5',sky:'#151d31'},
 ocean:{modules:['ocean','terrain','weather'],ground:'#3c5d62',structure:'#777b72',accent:'#a2d8d4',sky:'#1b3a43'},
 ice:{modules:['terrain','snow'],ground:'#a7c7d4',structure:'#6d95a7',accent:'#d6edf5',sky:'#24394d'},
 garden:{modules:['terrain','vex','vegetation'],ground:'#40533c',structure:'#8d8665',accent:'#b0ddbc',sky:'#1d3633'},
};
export const atlasSeed=(s:string)=>{let h=2166136261;for(let i=0;i<s.length;i++)h=Math.imul(h^s.charCodeAt(i),16777619);return h>>>0;};
export const atlasRecipe=(reference:AtlasReference)=>{
 const resolved=resolveAtlas(reference),preset=presets[resolved.render.family];
 let parent:string|null=resolved.location.id,europa=false;const seen=new Set<string>();
 while(parent&&!seen.has(parent)){seen.add(parent);if(parent==='europa')europa=true;parent=locationsById.get(parent)?.parentId??null;}
 const baseEnvironment=resolved.render.mode==='dedicated'?resolved.render.environment:europa&&resolved.render.family==='bray'?'europa':undefined;
 const modules=resolved.render.mode==='dedicated'?[]:resolved.render.modules??(baseEnvironment?['bray'] as AtlasModule[]:preset.modules);
 return {...resolved,modules,palette:preset,baseEnvironment,seed:atlasSeed(reference.locationId+':'+(reference.variantId??'current'))};
};
export type AtlasRecipe=ReturnType<typeof atlasRecipe>;
