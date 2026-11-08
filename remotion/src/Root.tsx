import React from 'react';
import {Composition} from 'remotion';
import {Episode} from './compositions/Episode';
import {episode1} from './project/episode1';
import {FPS, HEIGHT, WIDTH, totalFrames} from './project/timeline';
import {VoxelResurrection} from './voxel/VoxelResurrection';
import {VOXEL_DURATION, VOXEL_FPS} from './voxel/timeline';

export const RemotionRoot: React.FC = () => <>
  <Composition
    id="Episode1"
    component={Episode}
    width={WIDTH}
    height={HEIGHT}
    fps={FPS}
    durationInFrames={totalFrames(episode1)}
    defaultProps={{episode: episode1}}
    calculateMetadata={({props}) => ({durationInFrames: totalFrames(props.episode)})}
  />
  <Composition
    id="VoxelResurrection"
    component={VoxelResurrection}
    width={1080}
    height={1920}
    fps={VOXEL_FPS}
    durationInFrames={VOXEL_DURATION}
  />
</>;
