import {bundle} from '@remotion/bundler';
import {renderStill,selectComposition} from '@remotion/renderer';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {withoutPolish} from '../polish/compare.ts';
process.chdir(fileURLToPath(new URL('..',import.meta.url)));
const browserExecutable=process.env.CHROMIUM_EXECUTABLE||'/usr/bin/chromium',chromiumOptions={gl:'swangle'},serveUrl=await bundle({entryPoint:resolve('src/index.ts')});
mkdirSync('out/riis-comparison',{recursive:true});const evidence=[];
async function still(episode,frame,name,{preview=true,alignedWords,compareBefore=false}={}){
 const inputProps={episode,preview,alignedWords,compareBefore},composition=await selectComposition({serveUrl,id:episode.render.composition,inputProps,browserExecutable,chromiumOptions}),output='out/riis-comparison/'+name+'.png';
 await renderStill({serveUrl,composition,inputProps,output,frame,browserExecutable,chromiumOptions,imageFormat:'png',logLevel:'error'});
 const sha256=createHash('sha256').update(readFileSync(output)).digest('hex');evidence.push({name,frame,sha256});return sha256;
}
const baseline=JSON.parse(readFileSync('hybrid/validation-evidence.json')).stills.stills;
for(const name of ['hybrid_riis','traveler_episode_002','atlas_demo','living_europa']){
 const frame=name==='hybrid_riis'?45:120,episode=JSON.parse(readFileSync('episodes/'+name+'.json')),sha=await still(episode,frame,'legacy-'+name),expected=baseline.find(s=>s.name===name&&s.frame===frame)?.sha256;
 if(sha!==expected)throw new Error('Legacy image changed: '+name);
}
const before=JSON.parse(readFileSync('out/hybrid_riis-ready.json')),after=JSON.parse(readFileSync('out/hybrid_riis_06-ready.json')),words=JSON.parse(readFileSync('public/'+before.subtitles.source));
after.shorts.polish.previewQuality='final';
const frames=[45,210,420,660,990];
for(const [i,frame]of frames.entries()){await still(before,frame,'before-'+i,{preview:false,alignedWords:words});await still(after,frame,'after-'+i,{preview:false,alignedWords:words});}
const first=await still(after,660,'seek-a',{preview:false,alignedWords:words});await still(after,45,'seek-between',{preview:false,alignedWords:words});const second=await still(after,660,'seek-b',{preview:false,alignedWords:words});if(first!==second)throw new Error('0.6 out-of-order render differs');
const preview=await still(after,420,'aligned-preview',{preview:true,alignedWords:words}),final=evidence.find(e=>e.name==='after-2').sha256;if(preview!==final)throw new Error('Aligned preview/final graphics differ');
const compared=await still(after,45,'comparison-disabled',{preview:true,alignedWords:words,compareBefore:true});if(compared!==evidence.find(e=>e.name==='before-0').sha256)throw new Error('Before effects does not reproduce the reference');
const html='<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Riis 0.5 / 0.6</title><style>body{background:#0b1524;color:white;font:16px Arial;margin:24px}section{display:flex;gap:16px;flex-wrap:wrap}img,video{max-width:44vw;width:320px}h2{margin-top:36px}</style><h1>Riis 0.5 / 0.6</h1><p>Same 35-second script, voice, timestamps and scene durations. Left: 0.5. Right: 0.6.</p><section><video controls src="../hybrid-riis.mp4"></video><video controls src="../hybrid-riis-06.mp4"></video></section>'+frames.map((frame,i)=>'<h2>Frame '+frame+'</h2><section><img src="before-'+i+'.png" alt="Riis 0.5"><img src="after-'+i+'.png" alt="Riis 0.6"></section>').join('');
writeFileSync('out/riis-comparison/index.html',html);writeFileSync('out/riis-comparison/visual-evidence.json',JSON.stringify({stills:evidence,legacyMatches:4,randomOrder:true,alignedPreviewFinal:true,beforeEffectsMatchesReference:true},null,2)+'\n');console.log('PASS: 4 legacy gold images, 5 before/after pairs, random-order determinism, aligned preview/final, exact before-effects reference.');
