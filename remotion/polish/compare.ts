import type {VoxelEpisodeDef} from '../src/voxel/episode/schema';
export function withoutPolish(project:VoxelEpisodeDef):VoxelEpisodeDef{
 const copy=structuredClone(project);
 const stripWorld=(world:any)=>{if(!world)return;for(const a of world.cast??[])delete a.director;for(const g of world.groups??[])delete g.member.director;};
 for(const scene of copy.scenes){delete scene.polish;stripWorld(scene.livingWorld);}
 for(const plan of copy.direction?.scenes??[])for(const shot of plan.shots)stripWorld(shot.livingWorld);
 if(copy.shorts){delete copy.shorts.polish;const c=copy.shorts.captions;delete c.fontSize;delete c.color;delete c.accent;delete c.leftPx;delete c.rightPx;delete c.emphasis;if(['documentary-clean','kinetic-words','cinematic-reveal','high-impact'].includes(c.style))c.style='dynamic-shorts';}
 return copy;
}
