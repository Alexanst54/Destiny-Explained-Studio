import React from 'react';
import {createRoot} from 'react-dom/client';
import {Player} from '@remotion/player';
import {HybridShort} from '../remotion/hybrid/HybridShort';
import {episodeSchema} from '../remotion/src/voxel/episode/schema';
export function mountPreview(container,episode){
 const valid=episodeSchema.parse(episode);
 // Isolate the film from editor CSS so headings, cards and captions keep render typography.
 const host=document.createElement('div');host.style.cssText='font-family:Arial,sans-serif;font-size:16px;font-weight:400;line-height:normal;letter-spacing:normal';container.replaceChildren(host);
 const root=createRoot(host.attachShadow({mode:'open'}));
 root.render(<Player component={HybridShort} inputProps={{episode:{...valid,shorts:{...valid.shorts,quality:'draft'}},preview:true,reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches}} durationInFrames={valid.format.durationFrames} fps={30} compositionWidth={1080} compositionHeight={1920} controls loop={false} style={{width:'100%',aspectRatio:'9/16',background:'#091423'}}/>);
 return ()=>{root.unmount();host.remove();};
}
