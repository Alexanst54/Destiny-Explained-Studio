import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile} from 'remotion';
import {Subtitles} from '../components/Subtitles';
import {sceneFrames} from '../project/timeline';
import type {EpisodeDef} from '../types';
import {SceneView} from './SceneView';
export type EpisodeProps={episode:EpisodeDef};
export const Episode:React.FC<EpisodeProps>=({episode})=>{let cursor=0;return <AbsoluteFill style={{backgroundColor:'#fff'}}>{episode.scenes.map(scene=>{const from=cursor;const d=sceneFrames(scene);cursor+=d;return <Sequence key={scene.id} from={from} durationInFrames={d}><SceneView scene={scene} cues={episode.cues} startFrame={from} durationInFrames={d}/></Sequence>})}<Subtitles cues={episode.cues}/>{episode.voiceover&&<Audio src={staticFile(episode.voiceover)}/>}</AbsoluteFill>};