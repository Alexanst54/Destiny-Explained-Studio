import type {VoxelEpisodeDef,AlignedWord} from '../src/voxel/episode/schema';
import {validateWords} from '../src/voxel/episode/schema.ts';
import {estimatedWords} from '../src/voxel/cinematic/timeline.ts';
import {atlas,sourcesById} from '../atlas/index.ts';
import {characterCatalog} from '../characters/index.ts';
import type {HybridVisual,AudioTrack} from './schema';
export const clamp=(n:number,a=0,b=1)=>Math.max(a,Math.min(b,n));
export const ease=(n:number)=>{const x=clamp(n);return x*x*(3-2*x);};
export const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
export const allSourceIds=new Set([...sourcesById.keys(),...characterCatalog.sources.map(s=>s.id)]);
export function sourceTitle(episode:VoxelEpisodeDef,id:string){return episode.shorts?.sources.find(s=>s.id===id)?.title??sourcesById.get(id)?.title??characterCatalog.sources.find(s=>s.id===id)?.title??id;}
export function sourceUrl(episode:VoxelEpisodeDef,id:string){return episode.shorts?.sources.find(s=>s.id===id)?.url??sourcesById.get(id)?.url??characterCatalog.sources.find(s=>s.id===id)?.url;}
export function captionTiming(episode:VoxelEpisodeDef,words?:AlignedWord[]){
 const proposed=words??episode.shorts?.alignedWords;
 if(proposed)try{return {words:validateWords(proposed,episode),exact:true,reason:''};}catch{return {words:estimatedWords(episode),exact:false,reason:'Incomplete or invalid timestamps · estimated timing'};}
 return {words:estimatedWords(episode),exact:false,reason:'No word timestamps · estimated timing'};
}
export function captionSegment(words:AlignedWord[],frame:number,sceneStart:number,sceneEnd:number,maxWords=5){
 const local=words.filter(w=>w.start>=sceneStart/30-1e-6&&w.end<=sceneEnd/30+1e-6),t=frame/30;
 const chunks:AlignedWord[][]=[];let current:AlignedWord[]=[];
 for(const word of local){if(current.length&&(current.length>=maxWords||current.reduce((n,w)=>n+w.text.length+1,0)+word.text.length>42)){chunks.push(current);current=[];}current.push(word);}if(current.length)chunks.push(current);
 return (chunks.find(c=>c.some(w=>t>=w.start&&t<w.end))??[]).map(w=>({...w,active:t>=w.start&&t<w.end}));
}
export function transitionMotion(type:string,frame:number,duration:number,reduced=false){
 const p=duration?ease(frame/duration):1,t=reduced&&type!=='cut'?'fade':type;
 return {opacity:t==='fade'?p:1,x:t==='slide'?(1-p)*100:0,scale:t==='zoom'?1.12-.12*p:t==='match'?.97+.03*p:1,wipe:t==='wipe'?(1-p)*100:0,flash:t==='flash'?.12*(1-p):0};
}
export function audioGain(track:AudioTrack,frame:number,words:AlignedWord[]){
 const local=frame-track.startFrame;if(local<0||local>=track.durationFrames)return 0;
 const fade=Math.min(track.fadeInFrames?clamp(local/track.fadeInFrames):1,track.fadeOutFrames?clamp((track.durationFrames-local)/track.fadeOutFrames):1);
 // Smooth attack/release around every spoken word; absolute frame evaluation only.
 let speech=0;for(const w of words){const start=w.start*30,end=w.end*30;if(frame>=start-6&&frame<=end+12)speech=Math.max(speech,Math.min(ease((frame-start+6)/6),ease((end+12-frame)/12)));}
 return track.volume*fade*(1-speech*(1-track.ducking));
}
export function pacing(episode:VoxelEpisodeDef){
 const total=episode.format.durationFrames/30,average=total/episode.scenes.length,hook=episode.scenes[0].durationFrames/30;
 const staticScenes=episode.scenes.filter(s=>s.durationFrames>210&&s.visual?.type==='text').map(s=>s.id);
 const words=episode.scenes.reduce((n,s)=>n+s.narration.split(/\s+/).length,0);
 const visualSeconds=Object.fromEntries([...new Set(episode.scenes.map(s=>s.visual?.type??'voxel'))].map(type=>[type,episode.scenes.filter(s=>(s.visual?.type??'voxel')===type).reduce((n,s)=>n+s.durationFrames/30,0)]));
 return {total,average,hook,words,visualSeconds,narrationBudget:episode.scenes.filter(s=>s.narration.trim()).reduce((n,s)=>n+s.durationFrames/30,0),wpm:words*60/total,staticScenes,visualTypes:[...new Set(episode.scenes.map(s=>s.visual?.type??'voxel'))],recommendations:[...(hook>4?['Hook supérieur à 4 secondes : envisager une entrée plus courte.']:[]),...(average>8?['Durée moyenne des plans supérieure à 8 secondes.']:[]),...(staticScenes.length?['Long plan de texte : envisager une révélation ou un autre visuel.']:[]),...(total<20||total>45?['Format conseillé : 20 à 45 secondes.']:[]),'Conseils de montage uniquement ; aucune prédiction de viralité.']};
}
export function visualReferences(visual:HybridVisual){return [...visual.sources,...(visual.type==='timeline'?visual.events.flatMap(e=>e.sources):[])];}
export function hybridWarnings(episode:VoxelEpisodeDef){
 if(!episode.shorts)return [];
 const warnings=[...pacing(episode).recommendations];
 if(['hypothesis','alternate-history'].includes(episode.shorts.mode))warnings.push('HYPOTHETICAL / ALTERNATE HISTORY — NOT CANON');
 if(!captionTiming(episode).exact)warnings.push('Aperçu des sous-titres : minutage estimé avant import des mots Kokoro.');
 if(!episode.scenes.some(s=>s.visual?.sources.length))warnings.push('Associer des sources aux plans avant publication.');
 return warnings;
}
