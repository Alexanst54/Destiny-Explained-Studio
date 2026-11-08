import {livingShotSchema} from '../../../living/schema.ts';
import {weatherSchema} from '../../../weather/schema.ts';
import {z} from 'zod';
import {atlasRefSchema} from '../../../atlas/index.ts';
import {shotEnvironmentSchema,elementsSchema} from '../library/catalog.ts';
const reason = z.string().trim().min(8);
const vec = z.tuple([z.number().finite().min(-40).max(40),z.number().finite().min(-10).max(30),z.number().finite().min(-40).max(40)]);
export const cueSchema = z.union([
  z.object({sceneFrame:z.number().int().nonnegative()}).strict(),
  z.object({phrase:z.string().trim().min(1).refine(s=>/[a-z0-9]/i.test(s),'Narration cue must contain words'),occurrence:z.number().int().min(1).default(1),offsetFrames:z.number().int().min(-90).max(90).default(0)}).strict(),
]);
const transition = z.object({type:z.enum(['cut','fade','wipe','match']),durationFrames:z.number().int().min(0).max(30)}).strict();
const shot = z.object({id:z.string().min(1),at:cueSchema,purpose:reason,
  environment:shotEnvironmentSchema,atlas:atlasRefSchema.optional(),livingWorld:livingShotSchema.optional(),weather:weatherSchema.optional(),elements:elementsSchema.optional(),
  actors:z.object({guardian:z.boolean(),ghost:z.boolean()}).strict(),
  camera:z.object({mode:z.enum(['dolly','orbit','zoom','follow','close-up','perspective']),
    from:vec,to:vec,targetFrom:vec,targetTo:vec,
    fovFrom:z.number().min(25).max(65),fovTo:z.number().min(25).max(65),
    track:z.enum(['guardian','ghost']).optional(),
    angleFrom:z.number().min(-3).max(3).optional(),angleTo:z.number().min(-3).max(3).optional(),
  }).strict(),transition,
}).strict();
const actionBase = {id:z.string().min(1),at:cueSchema,durationFrames:z.number().int().min(12).max(600),
  from:vec,to:vec,height:z.number().min(0).max(3).default(1.3),purpose:reason};
const action = z.discriminatedUnion('actor',[
  z.object({...actionBase,actor:z.literal('guardian'),animation:z.enum(['idle','walk','run','jump','fall','resurrect','combat','interact','look-up'])}).strict(),
  z.object({...actionBase,actor:z.literal('ghost'),animation:z.enum(['hover','orbit','interact','scan'])}).strict(),
]);
const event = z.object({id:z.string().min(1),at:cueSchema,durationFrames:z.number().int().min(3).max(600),
  type:z.enum(['particles','explosion','hologram','beam','shake']),position:vec,to:vec.optional(),
  strength:z.number().min(0).max(1),purpose:reason}).strict();
export const directionSchema = z.object({version:z.literal(1),intensity:z.enum(['calm','balanced','cinematic']),
  scenes:z.array(z.object({sceneId:z.string().min(1),shots:z.array(shot).min(1),
    actions:z.array(action),events:z.array(event)}).strict()).min(1)}).strict();
export type Direction = z.infer<typeof directionSchema>;
export type Cue = z.infer<typeof cueSchema>;
export type Shot = z.infer<typeof shot>;
export type Action = z.infer<typeof action>;
export type VisualEvent = z.infer<typeof event>;
