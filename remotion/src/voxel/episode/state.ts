import type {VoxelEpisodeDef, VoxelSceneDef, AlignedWord} from './schema';
import {resurrectionState} from '../timeline.ts';
const smooth = (p: number) => {const x = Math.max(0, Math.min(1, p)); return x*x*(3-2*x);};
export const findScene = (episode: VoxelEpisodeDef, frame: number) => {
  const scene = episode.scenes.find(s => frame >= s.startFrame && frame < s.startFrame + s.durationFrames);
  if (!scene) throw new Error(`No scene at frame ${frame}`);
  return scene;
};
export const sceneState = (scene: VoxelSceneDef, frame: number, fps: number) => {
  const local = frame - scene.startFrame;
  const progress = smooth(local / Math.max(1, scene.durationFrames - 1));
  const resurrect = scene.actions.some(a => a.animation === 'resurrect');
  const base = resurrectionState(resurrect ? local * 449 / (scene.durationFrames - 1) : 449);
  return {...base, t: frame / fps, progress, local,
    beam: resurrect ? base.beam : 0,
    scan: scene.actions.some(a => a.animation === 'scan'),
    lookUp: scene.actions.some(a => a.animation === 'look-up'),
    particles: scene.effects.includes('light-particles') ? 0.75 :
      scene.effects.includes('voxel-particles') ? base.beam : 0,
  };
};
export type CameraPose = {position: [number, number, number]; target: [number, number, number]};
export const cameraPose = (camera: VoxelSceneDef['camera'], p: number): CameraPose => {
  switch (camera) {
    case 'wide-tilt-up': return {position: [0, 4.4, 13], target: [0, 2.6 + p * 1.4, -2]};
    case 'slow-orbit-traveler': {const a = -0.22 + p * 0.44;
      return {position: [Math.sin(a)*13, 5.2, Math.cos(a)*13], target: [0, 6, -8]};}
    case 'push-in-sky': return {position: [0, 4.5+p, 13-p*2], target: [0, 6.4, -8]};
    case 'close-up-ghost': return {position: [1.5-p*0.4, 3.8, 6], target: [0, 3.65, 0]};
    case 'medium-guardian': return {position: [-2+p, 4.4, 10.5], target: [0, 1.85, 0]};
    case 'wide-pullback': return {position: [p*1.2, 4.5+p, 11+p*3], target: [0, 3.8, -3]};
  }
};
export const captionWords = (scene: VoxelSceneDef, frame: number, words?: AlignedWord[]) => {
  const t = frame / 30;
  if (words) {
    // Keep chunks inside the current scene; global groups of six could otherwise
    // display text from the previous scene at a cut.
    words = words.filter(w => w.start >= scene.startFrame / 30 - 1e-6 &&
      w.end <= (scene.startFrame + scene.durationFrames) / 30 + 1e-6);
    const active = words.findIndex(w => t >= w.start && t < w.end);
    if (active === -1) return [];
    const chunk = Math.floor(active / 6) * 6;
    return words.slice(chunk, chunk + 6).map(w => ({text: w.text, active: t >= w.start && t < w.end}));
  }
  const tokens = scene.narration.split(/\s+/);
  const index = Math.min(tokens.length-1, Math.floor((frame-scene.startFrame)/scene.durationFrames*tokens.length));
  const start = Math.floor(index/6)*6;
  return tokens.slice(start, start+6).map((text, i) => ({text, active: start+i === index}));
};
