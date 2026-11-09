import {bundle} from '@remotion/bundler';
import {selectComposition,renderStill} from '@remotion/renderer';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
process.chdir(fileURLToPath(new URL('..',import.meta.url)));
const smoke=process.argv.includes('--smoke'),browserExecutable=process.env.CHROMIUM_EXECUTABLE||'/usr/bin/chromium',chromiumOptions={gl:'swangle'},serveUrl=await bundle({entryPoint:resolve('src/index.ts')});
mkdirSync('out/animation-comparison',{recursive:true});const evidence=[];
async function still(episode,frame,name,{preview=false,reducedMotion=false}={}){
 const inputProps={episode,preview,alignedWords:episode.shorts?.alignedWords,reducedMotion},composition=await selectComposition({serveUrl,id:episode.render.composition,inputProps,browserExecutable,chromiumOptions}),output='out/animation-comparison/'+name+'.png';
 await renderStill({serveUrl,composition,inputProps,output,frame,browserExecutable,chromiumOptions,imageFormat:'png',logLevel:'error'});
 const sha256=createHash('sha256').update(readFileSync(output)).digest('hex');evidence.push({name,frame,sha256});console.log(name,frame,sha256);return sha256;
}
const next=JSON.parse(readFileSync('out/hybrid_riis_07-ready.json'));next.shorts.polish.previewQuality='final';
if(smoke){await still(next,210,'smoke-city');await still(next,660,'smoke-exodus');process.exit(0);}
const baseline=JSON.parse(readFileSync('hybrid/validation-evidence.json')).stills.stills;
for(const name of ['hybrid_riis','traveler_episode_002','atlas_demo','living_europa']){const frame=name==='hybrid_riis'?45:120,episode=JSON.parse(readFileSync('episodes/'+name+'.json')),sha=await still(episode,frame,'legacy-'+name,{preview:true}),expected=baseline.find(s=>s.name===name&&s.frame===frame)?.sha256;if(sha!==expected)throw new Error('Legacy image changed: '+name);}
const polished=JSON.parse(readFileSync('out/hybrid_riis_06-ready.json')),oldVisual=JSON.parse(readFileSync('polish/validation-evidence.json')).visual.stills;
for(const [frame,index]of [[210,1],[660,3]]){const sha=await still(polished,frame,'legacy-polish-'+frame);if(sha!==oldVisual.find(s=>s.name==='after-'+index)?.sha256)throw new Error('0.6 voxel image changed: '+frame);}
const old=JSON.parse(readFileSync('out/hybrid_riis-ready.json')),frames=[45,210,300,420,660,850,960,1020];
for(const [i,frame]of frames.entries()){await still(old,frame,'v05-'+i);await still(polished,frame,'v06-'+i);await still(next,frame,'v07-'+i);}
const a=await still(next,660,'seek-a');await still(next,210,'seek-between');const b=await still(next,660,'seek-b');if(a!==b)throw new Error('Random-order rig image differs');
const preview=await still(next,210,'aligned-preview',{preview:true});if(preview!==evidence.find(s=>s.name==='v07-1').sha256)throw new Error('Final-quality aligned voxel preview differs');
const reducedA=await still(next,210,'reduced-a',{preview:true,reducedMotion:true});await still(next,45,'reduced-between',{preview:true,reducedMotion:true});if(reducedA!==await still(next,210,'reduced-b',{preview:true,reducedMotion:true}))throw new Error('Reduced motion seek differs');
const html='<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Riis 0.5 / 0.6 / 0.7</title><style>body{background:#0b1524;color:white;font:16px Arial;margin:20px}section{display:flex;gap:12px;flex-wrap:wrap}img,video{max-width:28vw;width:300px}</style><h1>Riis 0.5 / 0.6 / 0.7</h1><p>Left to right: versions 0.5, 0.6, 0.7. Exact same 35-second WAV and 64 word timestamps. 0.7 subdivides the conclusion to show all five hybrid types.</p><section>'+['hybrid-riis','hybrid-riis-06','hybrid-riis-07'].map(n=>'<video controls src="../'+n+'.mp4"></video>').join('')+'</section>'+frames.map((frame,i)=>'<h2>Frame '+frame+'</h2><section>'+['05','06','07'].map(v=>'<img src="v'+v+'-'+i+'.png" alt="Riis 0.'+v.slice(1)+'">').join('')+'</section>').join('');
writeFileSync('out/animation-comparison/index.html',html);writeFileSync('out/animation-comparison/visual-evidence.json',JSON.stringify({legacyMatches:6,randomOrder:true,alignedVoxelPreviewFinal:true,reducedMotionRandomOrder:true,stills:evidence},null,2)+'\n');console.log('PASS: six legacy images, eight three-way comparisons, random-order rigs, aligned voxel preview/final and reduced motion.');
