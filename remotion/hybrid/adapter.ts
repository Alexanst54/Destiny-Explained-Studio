import type {VoxelEpisodeDef} from '../src/voxel/episode/schema';
// Lossless at the project boundary: this internal projection is used only by the reused voxel visual.
export function voxelVisualEpisode(project:VoxelEpisodeDef):VoxelEpisodeDef{
 const {shorts:_shorts,...rest}=project;
 return {...rest,schemaVersion:'0.4.0',render:{...project.render,composition:'VoxelCinematicEpisode'},scenes:project.scenes.map(({visual:_visual,...scene})=>scene)};
}
