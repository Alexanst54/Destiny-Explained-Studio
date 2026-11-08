import {z} from 'zod';

// Shared contract: renderer, editor and Colab all read these same options.
export const locations = ['the-tower', 'europa', 'black-garden', 'pyramid-interior'] as const;
export const locationSchema = z.enum(locations);
export const shotEnvironmentSchema = z.enum(['tower', 'golden-age-vision', 'collapse-vision', 'light-space', 'scene', 'europa', 'black-garden', 'pyramid-interior']);
export const environmentDefinitions = {
  'the-tower': {id:'the-tower',model:'voxel-tower-v1',props:['traveler-sphere','last-city-silhouette','tower-balcony']},
  europa: {id:'europa',model:'voxel-europa-v1',props:['ice-ridges','snowfield','research-outpost']},
  'black-garden': {id:'black-garden',model:'voxel-black-garden-v1',props:['vex-gate','garden-terraces','red-flowers']},
  'pyramid-interior': {id:'pyramid-interior',model:'voxel-pyramid-v1',props:['stepped-walls','resonant-altar','amber-trim']},
} as const;
export const environmentDeclarationSchema = z.discriminatedUnion('id', [
  z.object({id:z.literal('the-tower'),model:z.literal('voxel-tower-v1'),props:z.array(z.enum(environmentDefinitions['the-tower'].props)).length(3)}).strict(),
  z.object({id:z.literal('europa'),model:z.literal('voxel-europa-v1'),props:z.array(z.enum(environmentDefinitions.europa.props)).length(3)}).strict(),
  z.object({id:z.literal('black-garden'),model:z.literal('voxel-black-garden-v1'),props:z.array(z.enum(environmentDefinitions['black-garden'].props)).length(3)}).strict(),
  z.object({id:z.literal('pyramid-interior'),model:z.literal('voxel-pyramid-v1'),props:z.array(z.enum(environmentDefinitions['pyramid-interior'].props)).length(3)}).strict(),
]);
export const elementAnimations = {
  guardian:['idle','walk'], ghost:['hover','still'], 'vex-structure':['still','pulse'],
  'light-fragments':['pulse','still'], crystal:['pulse','still'], snow:['drift','blizzard','still'], particles:['drift','pulse','still'],
} as const;
export const elementTypes = ['guardian','ghost','vex-structure','light-fragments','crystal','snow','particles'] as const;
export const defaultElementAnimation = (type:ElementType) => elementAnimations[type][0];
export type ElementType = typeof elementTypes[number];
const position = z.tuple([z.number().finite().min(-30).max(30),z.number().finite().min(-2).max(20),z.number().finite().min(-30).max(30)]);
const rotation = z.tuple([z.number().finite().min(-Math.PI*2).max(Math.PI*2),z.number().finite().min(-Math.PI*2).max(Math.PI*2),z.number().finite().min(-Math.PI*2).max(Math.PI*2)]);
export const elementSchema = z.object({
  id:z.string().trim().min(1),type:z.enum(elementTypes),position,
  rotation:rotation.optional(),scale:z.number().min(.25).max(3).optional(),
  animation:z.enum(['idle','walk','hover','still','pulse','drift','blizzard']).optional(),
  seed:z.number().int().min(0).max(65535).optional(),count:z.number().int().min(1).max(64).optional(),
  strength:z.number().min(0).max(1).optional(),
}).strict().superRefine((item,ctx)=>{
  if(item.animation && !(elementAnimations[item.type] as readonly string[]).includes(item.animation))
    ctx.addIssue({code:'custom',path:['animation'],message:'Animation incompatible with this voxel element'});
});
export const elementsSchema = z.array(elementSchema).max(12).superRefine((items,ctx)=>{
  if(new Set(items.map(x=>x.id)).size!==items.length)ctx.addIssue({code:'custom',message:'Duplicate voxel element id'});
  const particles=items.filter(x=>['snow','particles','light-fragments'].includes(x.type)).reduce((n,x)=>n+(x.count??24),0);
  if(particles>256)ctx.addIssue({code:'custom',message:'Voxel element particle budget exceeds 256'});
});
export type VoxelElement = z.infer<typeof elementSchema>;
export type Location = z.infer<typeof locationSchema>;
export const resolveEnvironment = (environment:z.infer<typeof shotEnvironmentSchema>,location:Location) => environment==='scene' ? location==='the-tower'?'tower':location : environment;
export const environmentStyle = (id:string) => {
  switch(id){
    case 'europa': return {sky:'#24394d',fogNear:19,fogFar:48,ambient:1.25,key:'#d2edff',fill:'#769ccd'};
    case 'black-garden': return {sky:'#182b2d',fogNear:23,fogFar:52,ambient:1.05,key:'#ffe2ad',fill:'#84c9ab'};
    case 'pyramid-interior': return {sky:'#100f19',fogNear:26,fogFar:55,ambient:.85,key:'#ffcb89',fill:'#7c83b6'};
    default:return {sky:id==='collapse-vision'?'#060b17':'#101a2b',fogNear:24,fogFar:50,ambient:id==='collapse-vision'?.55:1.1,key:'#ffe2b5',fill:'#8aa8ff'};
  }
};
