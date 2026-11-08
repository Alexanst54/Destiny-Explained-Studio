import React,{createRef} from 'react';
import {flushSync} from 'react-dom';
import {createRoot} from 'react-dom/client';
import {Player} from '@remotion/player';
import {HybridShort} from '../remotion/hybrid/HybridShort';
import {episodeSchema} from '../remotion/src/voxel/episode/schema';
export function mountPreview(container,episode,options={}){
 const valid=episodeSchema.parse(episode);
 // Isolate the film from editor CSS so headings, cards and captions keep render typography.
 const host=document.createElement('div');host.style.cssText='font-family:Arial,sans-serif;font-size:16px;font-weight:400;line-height:normal;letter-spacing:normal';container.replaceChildren(host);
 if(options.localNarrationUrl&&!options.localNarrationUrl.startsWith('blob:'))throw new Error('La narration d’aperçu doit rester un fichier local.');
 const player=createRef();
 const root=createRoot(host.attachShadow({mode:'open'}));
 flushSync(()=>root.render(<Player ref={player} initialFrame={Math.max(0,Math.min(valid.format.durationFrames-1,options.initialFrame??0))} component={HybridShort} inputProps={{episode:{...valid,shorts:{...valid.shorts,quality:'draft'}},preview:true,reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches,localNarrationUrl:options.localNarrationUrl,previewMuted:options.previewMuted??false,compareBefore:options.compareBefore??false}} durationInFrames={valid.format.durationFrames} fps={30} compositionWidth={1080} compositionHeight={1920} controls loop={false} style={{width:'100%',aspectRatio:'9/16',background:'#091423'}}/>));
 return Object.assign(()=>{root.unmount();host.remove();},{seekTo:frame=>player.current?.seekTo(frame),play:()=>player.current?.play(),pause:()=>player.current?.pause(),getCurrentFrame:()=>player.current?.getCurrentFrame()??0});
}
