import {z} from 'zod';
import type {VoxelEpisodeDef} from '../src/voxel/episode/schema';
const path=z.string().regex(/^assets\/blender-video\/[a-f0-9]{64}\/\d{5}\.png$/);
export const sequencesSchema=z.object({version:z.literal(1),fps:z.literal(30),projectId:z.string().min(1),clips:z.array(z.object({startFrame:z.number().int().nonnegative(),width:z.number().int().positive(),height:z.number().int().positive(),frames:z.array(path).min(1).max(90)}).strict()).min(1).max(16)}).strict();
export type BlenderSequences=z.infer<typeof sequencesSchema>;
export function validateSequences(input:unknown,episode:VoxelEpisodeDef):BlenderSequences{
 const data=sequencesSchema.parse(input);if(data.projectId!==episode.id||episode.render.composition!=='HybridShort')throw Error('Blender sequence requires matching HybridShort project');
 const covered=new Set<number>();for(const c of data.clips){if(c.width*16!==c.height*9)throw Error('Blender images must be vertical 9:16');for(let i=0;i<c.frames.length;i++){const f=c.startFrame+i;if(covered.has(f))throw Error('Overlapping Blender clips');covered.add(f);const s=episode.scenes.find(s=>f>=s.startFrame&&f<s.startFrame+s.durationFrames);if(!s||s.visual?.type!=='voxel')throw Error('Blender clip must cover voxel frames inside the episode');}}
 return data;
}
export function sequenceImage(data:BlenderSequences|undefined,frame:number){const c=data?.clips.find(c=>frame>=c.startFrame&&frame<c.startFrame+c.frames.length);return c?.frames[frame-c.startFrame];}
