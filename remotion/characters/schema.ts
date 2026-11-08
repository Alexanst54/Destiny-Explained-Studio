import {z} from 'zod';
export const civilizations=['human','awoken','exo','eliksni','krill','hive','cabal','vex','taken','scorn','witness-precursors','machine','cosmic'] as const;
export const modelKinds=['humanoid','four-arm','heavy','krill','hive','vex','beast','drone','giant','sphere','terminal','unknown'] as const;
export const animations=['idle','walk','run','flee','look','salute','talk','interact','observe','kneel','fall','combat','attack','hit','terminal','appear','disappear'] as const;
const text=z.string().trim().min(1),names=z.object({fr:text,en:text}).strict();
export const visualSchema=z.object({model:z.enum(modelKinds),silhouette:text,palette:z.array(z.string().regex(/^#[a-fA-F0-9]{6}$/)).min(3).max(6),equipment:z.array(text),scale:z.number().min(.2).max(8),certainty:z.enum(['stylized-documented','reconstruction','unknown']),note:text}).strict();
const variant=z.object({id:text,names,change:z.enum(['baseline','transformation','renaming','resurrection','equipment']),civilization:z.enum(civilizations),eras:z.array(text),events:z.array(text),sources:z.array(text).min(1),visual:visualSchema,datedBySource:text.nullable()}).strict();
export const characterSchema=z.object({id:text,names,civilization:z.enum(civilizations),faction:text,affiliations:z.array(z.object({faction:text,era:text.nullable()}).strict()),archetype:z.enum(['civilian','scientist','soldier','leader','creature','drone','entity']),identityNote:text,visual:visualSchema,variants:z.array(variant).min(1),animations:z.array(z.enum(animations)).min(1),events:z.array(text),locations:z.array(text),sources:z.array(text).min(1)}).strict();
export const characterCatalogSchema=z.object({schemaVersion:z.literal('0.4.0'),scope:text,sources:z.array(z.object({id:text,title:text,url:z.url().refine(s=>s.startsWith('https://')),kind:z.enum(['primary','secondary']),locator:text,verification:z.enum(['reference-only','retrieved'])}).strict()),characters:z.array(characterSchema)}).strict().superRefine((c,ctx)=>{
 const fail=(message:string)=>ctx.addIssue({code:'custom',message});
 if(new Set(c.characters.map(x=>x.id)).size!==c.characters.length)fail('Duplicate character id');
 const sources=new Set(c.sources.map(x=>x.id));if(sources.size!==c.sources.length)fail('Duplicate source id');
 for(const a of c.characters){
  if(new Set(a.variants.map(v=>v.id)).size!==a.variants.length)fail('Duplicate character variant');
  for(const id of [...a.sources,...a.variants.flatMap(v=>v.sources)])if(!sources.has(id))fail('Unknown character source');
  for(const v of [a.visual,...a.variants.map(v=>v.visual)])if(v.certainty==='unknown'&&v.model!=='unknown')fail('Unknown appearance must not invent a model');
 }
});
export type Character=z.infer<typeof characterSchema>;
