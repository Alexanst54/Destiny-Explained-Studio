import {bundle} from '@remotion/bundler';
import {renderStill,selectComposition} from '@remotion/renderer';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
process.chdir(fileURLToPath(new URL('..',import.meta.url)));
const browserExecutable=process.env.CHROMIUM_EXECUTABLE||'/usr/bin/chromium',chromiumOptions={gl:'swangle'};
const serveUrl=await bundle({entryPoint:resolve('src/index.ts')});mkdirSync('out/hybrid-verification',{recursive:true});
const report=[];
for(const name of ['hybrid_riis','hybrid_oryx','hybrid_black_garden','traveler_episode_002','atlas_demo','living_europa']){
 const episode=JSON.parse(readFileSync('episodes/'+name+'.json'));
 const props={episode,preview:true},composition=await selectComposition({serveUrl,id:episode.render.composition,inputProps:props,browserExecutable,chromiumOptions});
 const frames=name==='hybrid_riis'?[45,390,45,210,600]:name==='hybrid_oryx'?[540]:name==='hybrid_black_garden'?[450]:[120];let first;
 for(const [i,frame]of frames.entries()){
  const output='out/hybrid-verification/'+name+'-'+i+'.png';
  await renderStill({serveUrl,composition,inputProps:props,output,frame,browserExecutable,chromiumOptions,imageFormat:'png',logLevel:'error'});
  const sha256=createHash('sha256').update(readFileSync(output)).digest('hex');report.push({name,frame,sha256});
  if(i===0)first=sha256;if(i===2&&sha256!==first)throw new Error('Out-of-order hybrid frames differ');
 }
}
// Captions and visuals share the exact component when real word timing is available.
const episode=JSON.parse(readFileSync('out/hybrid_riis-ready.json')),alignedWords=JSON.parse(readFileSync('public/'+episode.subtitles.source));
const hashes=[];
for(const preview of [true,false]){const inputProps={episode,preview,alignedWords},composition=await selectComposition({serveUrl,id:'HybridShort',inputProps,browserExecutable,chromiumOptions}),output='out/hybrid-verification/shared-'+preview+'.png';await renderStill({serveUrl,composition,inputProps,output,frame:390,browserExecutable,chromiumOptions,imageFormat:'png',logLevel:'error'});hashes.push(createHash('sha256').update(readFileSync(output)).digest('hex'));}
if(hashes[0]!==hashes[1])throw new Error('Aligned preview and final graphic/caption frames differ');
const baseline=JSON.parse(readFileSync('living/validation-evidence.json')).stills;
for(const n of report.filter(n=>['traveler_episode_002','atlas_demo','living_europa'].includes(n.name))){const old=baseline.find(o=>o.name===n.name&&o.frame===n.frame);if(!old||old.sha256!==n.sha256)throw new Error('Legacy PNG changed: '+n.name);}
writeFileSync('out/hybrid-verification/report.json',JSON.stringify({stills:report,alignedPreviewFinalHashes:hashes},null,2)+'\n');console.log('PASS: 3 hybrid demos, 3 legacy projects, random-order identical frames, aligned preview/final identical PNG.');
