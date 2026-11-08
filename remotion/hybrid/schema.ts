import {newCaptionStyles,colorSchema,projectPolishSchema} from '../polish/schema.ts';
import {z} from 'zod';
import {locationsById} from '../atlas/index.ts';
export const sceneTypes=['voxel','map','timeline','graphic','text'] as const;
export const templateIds=['did-you-know','the-story-of','destiny-mysteries','timeline','what-if','character-origins'] as const;
export const captionStyles=['clean-documentary','dynamic-shorts','cinematic-minimal',...newCaptionStyles] as const;
export const transitionTypes=['cut','fade','slide','zoom','wipe','flash','match'] as const;
export const confidenceSchema=z.enum(['documented','partial','unknown']);
const text=z.string().trim().min(1).max(600),id=z.string().regex(/^[a-zA-Z0-9_-]+$/),percent=z.number().min(0).max(100),point=z.tuple([percent,percent]);
export const assetSource=z.string().min(1).max(1500000).refine(s=>/^data:audio\/(wav|x-wav|mpeg|ogg);base64,[A-Za-z0-9+/]+=*$/.test(s)||(!s.startsWith('/')&&!s.includes('..')&&!/[\\:\x00-\x1f]/.test(s)),'Use a local public asset or an embedded licensed audio file');
const transition=z.object({type:z.enum(transitionTypes),durationFrames:z.number().int().min(0).max(24)}).strict();
const base={headline:z.string().max(140).default(''),transition:transition.default({type:'fade',durationFrames:12}),sources:z.array(z.string().min(1)).max(20).default([])};
const node=z.object({id,label:text,locationId:z.string().optional(),position:point}).strict().superRefine((n,ctx)=>{if(n.locationId&&!locationsById.has(n.locationId))ctx.addIssue({code:'custom',message:'Unknown map Atlas location'});});
const edge=z.object({from:id,to:id,label:z.string().max(80).default('')}).strict();
const map=z.object({...base,type:z.literal('map'),nodes:z.array(node).min(1).max(12),routes:z.array(edge).max(16),camera:z.object({from:point,to:point,zoomFrom:z.number().min(1).max(2),zoomTo:z.number().min(1).max(2)}).strict()}).strict();
const timeline=z.object({...base,type:z.literal('timeline'),events:z.array(z.object({id,label:text,period:text,date:z.string().max(80).nullable(),confidence:confidenceSchema,sources:z.array(z.string().min(1)).min(1).max(10)}).strict()).min(1).max(8)}).strict();
const graphic=z.object({...base,type:z.literal('graphic'),cards:z.array(z.object({id,title:text,body:z.string().max(220),position:point}).strict()).min(1).max(6),connections:z.array(edge).max(12),counter:z.object({label:text,from:z.number().min(0).max(9999),to:z.number().min(0).max(9999)}).strict().optional()}).strict();
export const hybridVisualSchema=z.discriminatedUnion('type',[
 z.object({...base,type:z.literal('voxel')}).strict(),map,timeline,graphic,
 z.object({...base,type:z.literal('text'),body:text,kind:z.enum(['hook','quote','question','reveal','conclusion'])}).strict(),
]).superRefine((s,ctx)=>{
 const fail=(message:string)=>ctx.addIssue({code:'custom',message});
 const nodes=s.type==='map'?s.nodes:s.type==='graphic'?s.cards:s.type==='timeline'?s.events:[];
 const ids=new Set(nodes.map(n=>n.id));if(ids.size!==nodes.length)fail('Duplicate hybrid visual id');
 const edges=s.type==='map'?s.routes:s.type==='graphic'?s.connections:[];
 for(const e of edges)if(!ids.has(e.from)||!ids.has(e.to))fail('Unknown graphic/map connection endpoint');
 if(s.transition.type==='cut'&&s.transition.durationFrames!==0)fail('Cut transition must have zero duration');
 if(s.transition.type!=='cut'&&s.transition.durationFrames===0)fail('Animated transition requires a duration');
 if(s.type==='text'&&s.kind==='quote'&&!s.sources.length)fail('A quotation requires a source');
});
export const trackSchema=z.object({id,kind:z.enum(['effect','ambience','music']),source:assetSource,startFrame:z.number().int().min(0),durationFrames:z.number().int().min(1).max(1800),volume:z.number().min(0).max(1),fadeInFrames:z.number().int().min(0).max(90),fadeOutFrames:z.number().int().min(0).max(90),ducking:z.number().min(0).max(1),provenance:z.object({title:text,creator:text,license:z.enum(['original','CC0','CC-BY']),sourceUrl:z.url().optional(),licenseUrl:z.url().optional(),attribution:z.string().max(500)}).strict()}).strict().superRefine((t,ctx)=>{
 if(t.fadeInFrames+t.fadeOutFrames>t.durationFrames)ctx.addIssue({code:'custom',message:'Audio fades exceed track duration'});
 if(t.provenance.license==='CC-BY'&&(!t.provenance.attribution||!t.provenance.licenseUrl))ctx.addIssue({code:'custom',message:'CC-BY requires attribution and license URL'});
});
export const shortsSchema=z.object({version:z.literal(1),template:z.enum(templateIds),mode:z.enum(['canonical','reconstruction','hypothesis','alternate-history']),confidence:confidenceSchema,sources:z.array(z.object({id,title:text,url:z.url().refine(s=>s.startsWith('https://')),locator:text}).strict()).max(30).default([]),captions:z.object({style:z.enum(captionStyles),bottomPx:z.number().int().min(280).max(520),maxWords:z.number().int().min(2).max(6),fontSize:z.number().min(28).max(66).optional(),color:colorSchema.optional(),accent:colorSchema.optional(),leftPx:z.number().int().min(50).max(140).optional(),rightPx:z.number().int().min(130).max(220).optional(),emphasis:z.array(z.string().min(1).max(64)).max(32).optional()}).strict(),audio:z.object({voiceVolume:z.number().min(0).max(1),tracks:z.array(trackSchema).max(8)}).strict(),alignedWords:z.array(z.object({text:z.string().min(1),start:z.number().nonnegative(),end:z.number().positive()}).strict()).optional(),polish:projectPolishSchema.optional(),quality:z.enum(['cpu','draft']).default('cpu')}).strict().superRefine((s,ctx)=>{
 if(s.template==='what-if'&&!['hypothesis','alternate-history'].includes(s.mode))ctx.addIssue({code:'custom',message:'What If requires an explicitly hypothetical mode'});
 if(new Set(s.sources.map(x=>x.id)).size!==s.sources.length)ctx.addIssue({code:'custom',message:'Duplicate project source id'});
 if(new Set(s.audio.tracks.map(x=>x.id)).size!==s.audio.tracks.length)ctx.addIssue({code:'custom',message:'Duplicate audio track id'});
});
export type HybridVisual=z.infer<typeof hybridVisualSchema>;
export type Shorts=z.infer<typeof shortsSchema>;
export type AudioTrack=z.infer<typeof trackSchema>;
