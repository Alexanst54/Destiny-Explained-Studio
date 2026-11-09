import {z} from 'zod';
const finite=z.number().finite().min(-10000).max(10000),vec=z.tuple([finite,finite,finite]);
const id=z.string().min(1).max(200),color=z.string().regex(/^#[0-9a-fA-F]{6}$/);
export const matrixSchema=z.array(finite).length(16).refine(m=>m[3]===0&&m[7]===0&&m[11]===0&&m[15]===1,'Expected affine column-major matrix').refine(m=>Math.abs(m[0]*(m[5]*m[10]-m[9]*m[6])-m[4]*(m[1]*m[10]-m[9]*m[2])+m[8]*(m[1]*m[6]-m[5]*m[2]))>=1e-12,'Singular transform');
export const bridgeSchema=z.object({format:z.literal('destiny-blender-scene'),version:z.literal(1),exporterVersion:z.enum(['0.8.1','0.8.2']),coordinateSystem:z.literal('RIGHT_HANDED_Y_UP'),matrixLayout:z.literal('column-major'),profile:z.enum(['standard','cinematic']),
 source:z.object({projectId:id,projectVersion:z.string(),projectSha256:z.string().regex(/^[a-f0-9]{64}$/),sceneId:id,shotId:id,frame:z.number().int().min(0).max(17999),localFrame:z.number().int().min(0).max(17999),fps:z.literal(30),timing:z.enum(['aligned','estimated']),loreMode:z.string(),visualStatus:z.literal('artistic-reconstruction'),atlas:z.object({locationId:z.string(),variantId:z.string().optional()}).optional(),sourceIds:z.array(id).max(128)}).strict(),
 resolution:z.object({width:z.literal(1080),height:z.literal(1920)}).strict(),
 camera:z.object({matrixWorld:matrixSchema,position:vec,target:vec,verticalFov:z.number().min(10).max(100),near:z.number().min(.01).max(10),far:z.number().min(20).max(1000)}).strict(),
 world:z.object({color,ambient:z.number().min(0).max(10)}).strict(),
 lights:z.array(z.object({id,type:z.literal('sun'),position:vec,target:vec,color,intensity:z.number().min(0).max(20)}).strict()).min(1).max(8),
 materials:z.array(z.object({id,color,emission:z.boolean(),roughness:z.number().min(0).max(1)}).strict()).min(1).max(256),
 actors:z.array(z.object({id,characterId:id,variantId:id.optional(),rigArchetype:id,position:vec,yaw:finite,rootMatrix:matrixSchema,joints:z.array(z.object({id,parent:id.nullable(),matrixWorld:matrixSchema}).strict()).max(100)}).strict()).max(32),
 meshes:z.array(z.object({id,actorId:id.optional(),geometry:z.enum(['box','sphere']),material:id,matrixWorld:matrixSchema}).strict()).min(1).max(4096),
 environment:z.object({generator:z.literal('riis-before-whirlwind'),version:z.literal(1),detail:z.enum(['draft','balanced','cinematic']),seed:z.number().int().min(0).max(2147483647),lighting:z.enum(['dawn','blue-hour']),hazeDensity:z.number().min(0).max(.02),replacedMeshIds:z.array(id).max(4096),visualStatus:z.literal('artistic-reconstruction')}).strict().optional(),
 omissions:z.array(z.string().min(1).max(500)).max(256)
}).strict().superRefine((s,ctx)=>{
 const fail=(message:string)=>ctx.addIssue({code:'custom',message});
 for(const [name,list]of [['materials',s.materials],['actors',s.actors],['meshes',s.meshes],['lights',s.lights]]as const)if(new Set(list.map(x=>x.id)).size!==list.length)fail('Duplicate '+name+' id');
 const mats=new Set(s.materials.map(m=>m.id)),actors=new Set(s.actors.map(a=>a.id));for(const m of s.meshes){if(!mats.has(m.material))fail('Unknown mesh material');if(m.actorId&&!actors.has(m.actorId))fail('Unknown mesh actor');}
 for(const a of s.actors){const ids=new Set<string>();for(const j of a.joints){if(ids.has(j.id)||j.parent&&!ids.has(j.parent))fail('Invalid joint hierarchy');ids.add(j.id);}}
});
export type BridgeScene=z.infer<typeof bridgeSchema>;
