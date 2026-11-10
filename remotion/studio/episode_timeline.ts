import type {Word} from './captions';
export type EpisodeScene={id:string;label:string;title:string;startFrame:number;durationFrames:number;words:Word[]};
export type CompleteEpisodeProps={width:number;height:number;fps:number;frames:number;scenes:EpisodeScene[]};
export const sceneFrameSource=(id:string,frame:number)=>{
 if(!/^[a-z0-9-]+$/.test(id)||!Number.isInteger(frame)||frame<0)throw Error('Invalid scene/frame');
 const chunk=Math.floor(frame/120)*120;
 return `scenes/${id}/frames/chunk-${String(chunk).padStart(6,'0')}/frame-${String(frame%120).padStart(4,'0')}.png`;
};
export const validateEpisodeTimeline=(p:CompleteEpisodeProps)=>{
 let next=0;const ids=new Set<string>();
 if(!p.scenes.length||!Number.isInteger(p.fps)||p.fps<=0)throw Error('Empty/invalid timeline');
 for(const s of p.scenes){if(ids.has(s.id)||s.startFrame!==next||!Number.isInteger(s.durationFrames)||s.durationFrames<1)throw Error('Non-contiguous timeline');ids.add(s.id);next+=s.durationFrames;for(const w of s.words)if(!(w.start>=0&&w.end>w.start&&w.end<=s.durationFrames/p.fps))throw Error('Subtitle outside scene');}
 if(next!==p.frames)throw Error('Episode frame count mismatch');return p;
};
