import type {EpisodeDef,SceneDef} from '../types';
export const FPS=30;export const WIDTH=1080;export const HEIGHT=1920;export const GROUND=1380;
export const sceneFrames=(s:SceneDef)=>Math.max(1,Math.round(s.durationSec*FPS));
export const totalFrames=(e:EpisodeDef)=>e.scenes.reduce((sum,s)=>sum+sceneFrames(s),0);