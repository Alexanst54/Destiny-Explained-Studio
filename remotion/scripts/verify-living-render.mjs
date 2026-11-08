// CPU render evidence: identical PNGs after unrelated frames and legacy scene smoke renders.
import {bundle} from '@remotion/bundler';
import {renderStill,selectComposition} from '@remotion/renderer';
import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
process.chdir(fileURLToPath(new URL('..',import.meta.url)));
const chromiumOptions={gl:'swangle'},browserExecutable=process.env.CHROMIUM_EXECUTABLE||'/usr/bin/chromium';
mkdirSync('out/living-verification',{recursive:true});
const serveUrl=await bundle({entryPoint:resolve('src/index.ts')});
const report=[];
for(const name of ['living_europa','living_whirlwind','living_fundament','traveler_episode_002','traveler_episode_002_cinematic','voxel_worlds_demo','atlas_demo']){
 const episode=JSON.parse(readFileSync('episodes/'+name+'.json'));
 const inputProps={episode,preview:true};
 const composition=await selectComposition({serveUrl,id:episode.render.composition,inputProps,browserExecutable,chromiumOptions});
 const frames=name==='living_europa'?[120,600,120]:[120];let first;
 for(const [index,frame]of frames.entries()){
  const output='out/living-verification/'+name+'-'+index+'.png';
  await renderStill({serveUrl,composition,inputProps,output,frame,browserExecutable,chromiumOptions,imageFormat:'png',logLevel:'error'});
  const sha256=createHash('sha256').update(readFileSync(output)).digest('hex');report.push({name,frame,sha256});
  if(index===0)first=sha256;if(index===2&&sha256!==first)throw new Error('Random-order render differs');
 }
}
writeFileSync('out/living-verification/report.json',JSON.stringify(report,null,2)+'\n');console.log('PASS: CPU stills for 3 demos and 4 legacy episodes; identical frame 120 after frame 600.');
