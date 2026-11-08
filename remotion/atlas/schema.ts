import {z} from 'zod';
export const categories=['universe-realm','stellar-body','destination-region','zone','historical-site','activity-site','ship-station','lore-world','historical-variant'] as const;
export const families=['human','golden-age','vex','hive','cabal','eliksni','awoken','pyramid','bray','future-city','cosmic','ocean','ice','garden'] as const;
export const modules=['terrain','human','golden-age','vex','hive','cabal','eliksni','awoken','pyramid','bray','future-city','cosmic','vegetation','ocean','snow','weather'] as const;
const text=z.string().trim().min(1);
const names=z.object({en:text,fr:text}).strict();
const appearance=z.object({evidence:z.enum(['game','lore','lore-and-cinematic','simulation','manifest-only']),confidence:z.enum(['documented','partial','unknown']),note:text}).strict();
const render=z.object({family:z.enum(families),mode:z.enum(['dedicated','modular-reconstruction']),environment:z.enum(['the-tower','europa','black-garden','pyramid-interior']).optional(),modules:z.array(z.enum(modules)).max(8).optional()}).strict();
const variant=z.object({id:text,names,eras:z.array(text),events:z.array(text),sources:z.array(text).min(1),appearance,render}).strict();
const reference=z.object({game:z.enum(['D1','D2']),component:z.enum(['DestinyPlaceDefinition','DestinyDestinationDefinition','DestinyActivityDefinition']),hash:text,bubbleHash:text.optional()}).strict();
export const atlasLocationSchema=z.object({id:text,names,frenchNameStatus:z.enum(['editorial-translation','official-manifest','shortened-official-name','untranslated']),aliases:z.array(text),category:z.enum(categories),type:text,parentId:text.nullable(),civilizations:z.array(text),factions:z.array(text),eras:z.array(text),events:z.array(text),sources:z.array(text).min(1),canonStatus:z.enum(['attested','manifest-attested','editorial-container']),appearance,
 availability:z.array(z.object({game:z.enum(['D1','D2']),status:z.enum(['lore-only','manifest-listed','depicted-not-live-status','historical-content']),releases:z.array(text)}).strict()).min(1),render,variants:z.array(variant),manifestRefs:z.array(reference).optional(),
}).strict();
export const atlasCatalogSchema=z.object({schemaVersion:z.literal('0.3.0'),title:text,reviewedAt:text,scope:text,locations:z.array(atlasLocationSchema).min(1),
 sources:z.array(z.object({id:text,kind:z.enum(['primary-manifest','primary-lore-archive','secondary']),title:text,url:z.url().refine(s=>s.startsWith('https://'),'HTTPS source required'),locator:text.optional(),manifestVersion:text.optional(),checkedAt:text,verification:z.enum(['downloaded-and-inspected','retrieved-secondary-reference']),pageTitle:text.optional()}).strict()),
 coverage:z.array(z.object({id:text,title:text,game:z.enum(['D1','D2']),status:z.enum(['partial','gap']),notes:text,locationCount:z.number().int().nonnegative()}).strict()),
 knownGaps:z.array(text),unmatchedActivitySeeds:z.array(text),provenance:z.object({checkedAt:text,files:z.array(z.object({file:text,bytes:z.number().int().nonnegative(),sha256:text.regex(/^[a-f0-9]{64}$/)}).strict()),d2CandidateCount:z.number().int(),d1CandidateCount:z.number().int(),note:text}).strict(),
}).strict().superRefine((catalog,ctx)=>{
 const fail=(path:(string|number)[],message:string)=>ctx.addIssue({code:'custom',path,message});
 const ids=new Set<string>(),sourceIds=new Set<string>(),releases=new Set<string>();
 catalog.sources.forEach((s,i)=>{if(sourceIds.has(s.id))fail(['sources',i,'id'],'Duplicate source id');sourceIds.add(s.id);});
 catalog.coverage.forEach((r,i)=>{if(releases.has(r.id))fail(['coverage',i,'id'],'Duplicate release id');releases.add(r.id);});
 catalog.locations.forEach((p,i)=>{if(ids.has(p.id))fail(['locations',i,'id'],'Duplicate location id');ids.add(p.id);});
 const byId=new Map(catalog.locations.map(p=>[p.id,p]));
 catalog.locations.forEach((p,i)=>{
  if(p.parentId&&!ids.has(p.parentId))fail(['locations',i,'parentId'],'Unknown parent');
  const seen=new Set([p.id]);let parent=p.parentId;
  while(parent){if(seen.has(parent)){fail(['locations',i,'parentId'],'Parent cycle');break;}seen.add(parent);parent=byId.get(parent)?.parentId??null;}
  const variants=new Set<string>();
  for(const v of p.variants){if(variants.has(v.id))fail(['locations',i,'variants'],'Duplicate variant');variants.add(v.id);}
  for(const id of [...p.sources,...p.variants.flatMap(v=>v.sources)])if(!sourceIds.has(id))fail(['locations',i,'sources'],'Unknown source');
  for(const a of p.availability)for(const id of a.releases){if(!releases.has(id))fail(['locations',i,'availability'],'Unknown release');if(!id.startsWith(a.game.toLowerCase()+'-'))fail(['locations',i,'availability'],'Release/game mismatch');}
  for(const recipe of [p.render,...p.variants.map(v=>v.render)])if(recipe.mode==='dedicated'&&!recipe.environment)fail(['locations',i,'render'],'Dedicated environment required');
 });
});
export type AtlasLocation=z.infer<typeof atlasLocationSchema>;
export type AtlasFamily=typeof families[number];
export type AtlasModule=typeof modules[number];
