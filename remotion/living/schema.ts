import {characterDirectorSchema} from '../polish/schema.ts';
import {z} from 'zod';
import {animations} from '../characters/schema.ts';
import {charactersById} from '../characters/index.ts';
export const vec=z.tuple([z.number().min(-18).max(18),z.number().min(0).max(12),z.number().min(-18).max(18)]);
const stableId=z.string().regex(/^[a-zA-Z0-9_-]+$/);
const frames=z.number().int().min(0).max(18000),duration=z.number().int().min(1).max(18000);
export const animationClipSchema=z.object({animation:z.enum(animations),startFrame:frames,durationFrames:duration,transitionFrames:z.number().int().min(0).max(60).default(12)}).strict();
export const pathSchema=z.object({waypoints:z.array(z.object({position:vec,pauseFrames:frames.default(0)}).strict()).min(2).max(24),speed:z.number().min(.05).max(12)}).strict();
export const castSchema=z.object({id:stableId,characterId:z.string().min(1),variantId:z.string().min(1).optional(),position:vec,director:characterDirectorSchema.optional(),rotation:z.number().min(-Math.PI).max(Math.PI).default(0),scale:z.number().min(.5).max(1.5).default(1),palette:z.array(z.string().regex(/^#[a-fA-F0-9]{6}$/)).length(3).optional(),equipment:z.array(z.enum(['hood','robe','coat','visor','crest','pauldrons'])).max(6).optional(),startFrame:frames.default(0),durationFrames:duration,animation:z.enum(animations).default('idle'),clips:z.array(animationClipSchema).max(32).default([]),path:pathSchema.optional()}).strict().superRefine((a,ctx)=>{
 const c=charactersById.get(a.characterId),fail=(message:string)=>ctx.addIssue({code:'custom',message});
 if(!c)fail('Unknown character');
 else {if(a.variantId&&!c.variants.some(v=>v.id===a.variantId))fail('Unknown character variant');for(const name of [a.animation,...a.clips.map(c=>c.animation)])if(!c.animations.includes(name))fail('Unsupported character animation');}
 if(a.director&&a.director.startFrame+a.director.durationFrames>a.durationFrames)fail('Character director exceeds actor lifetime');
 let end=0;for(const c of a.clips){if(c.startFrame<end)fail('Overlapping or unordered animation clips');end=c.startFrame+c.durationFrames;if(end>a.durationFrames)fail('Animation exceeds character lifetime');}
});
export const groupSchema=z.object({id:stableId,member:castSchema,count:z.number().int().min(1).max(24),seed:z.number().int().min(0).max(2147483647),formation:z.enum(['grid','line','scatter']),spacing:z.number().min(.5).max(3),behavior:z.enum(['idle','walk','flee']),sizeVariation:z.number().min(0).max(.2).default(.08)}).strict();
export const castListSchema=z.array(castSchema).max(24);
export const groupsSchema=z.array(groupSchema).max(8);
export const livingWorldSchema=z.object({mode:z.enum(['canonical','reconstruction','alternate-history']).default('reconstruction'),era:z.string().min(1).optional(),props:z.array(z.object({id:z.string().min(1),type:z.literal('terminal'),position:vec}).strict()).max(8).default([]),cast:castListSchema.default([]),groups:groupsSchema.default([])}).strict().superRefine((w,ctx)=>{
 const ids=[...w.cast.map(a=>a.id),...w.groups.map(g=>g.id)];
 if(new Set(ids).size!==ids.length)ctx.addIssue({code:'custom',message:'Duplicate living world id'});
 if(w.cast.length+w.groups.reduce((s,g)=>s+g.count,0)>32)ctx.addIssue({code:'custom',message:'CPU population budget exceeds 32'});
});
// Shot overrides are whole lists; omission inherits. Empty lists deliberately hide a layer.
export const livingShotSchema=z.object({cast:castListSchema.optional(),groups:groupsSchema.optional(),animations:z.array(z.object({id:z.string().min(1),animation:z.enum(animations),transitionFrames:z.number().int().min(0).max(60).default(12)}).strict()).max(32).optional()}).strict().superRefine((s,ctx)=>{const ids=(s.animations??[]).map(a=>a.id);if(new Set(ids).size!==ids.length)ctx.addIssue({code:'custom',message:'Duplicate shot animation target'});});
export type Cast= z.infer<typeof castSchema>;
export type LivingWorld=z.infer<typeof livingWorldSchema>;
export type LivingShot=z.infer<typeof livingShotSchema>;
export type Group=z.infer<typeof groupSchema>;
