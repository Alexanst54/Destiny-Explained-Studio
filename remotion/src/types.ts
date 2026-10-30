export type Pose = 'idle' | 'talk' | 'walk' | 'jump' | 'resurrect';
export type Word = {text: string; start: number; end: number};
export type Cue = {text: string; start: number; end: number; words?: Word[]};
export type CameraDef = {zoomFrom: number; zoomTo: number; focusX: number; focusY: number};
export type SceneDef = {id: string; title: string; durationSec: number; hunterPose: Pose; hunterX: [number, number]; ghostOffset: [number, number]; camera: CameraDef};
export type EpisodeDef = {title: string; voiceover: string | null; cues: Cue[]; scenes: SceneDef[]};