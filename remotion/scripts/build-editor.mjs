import {build} from 'esbuild';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const check=process.argv.includes('--check');
const result=await build({entryPoints:[resolve(root,'editor/app.mjs')],bundle:true,format:'esm',platform:'browser',target:'chrome110',minify:true,legalComments:'eof',write:false,outfile:resolve(root,'docs/assets/editor.js')});
const sources=['remotion/characters/catalog.json','remotion/characters/schema.ts','remotion/characters/index.ts','remotion/living/schema.ts','remotion/living/director.ts','remotion/weather/schema.ts','remotion/episodes/living_whirlwind.json','remotion/episodes/living_europa.json','remotion/episodes/living_fundament.json','remotion/atlas/catalog.json','remotion/atlas/index.ts','remotion/atlas/schema.ts','remotion/episodes/atlas_demo.json','remotion/src/voxel/library/catalog.ts','remotion/episodes/voxel_worlds_demo.json','remotion/src/voxel/episode/schema.ts','remotion/src/voxel/cinematic/schema.ts','remotion/src/voxel/cinematic/timeline.ts','remotion/episodes/traveler_episode_002_cinematic.json'];
const manifest=JSON.stringify({format:1,sources:Object.fromEntries(sources.map(p=>[p,createHash('sha256').update(readFileSync(resolve(root,p))).digest('hex')]))},null,2)+'\n';
const revision=createHash('sha256').update(result.outputFiles[0].text).update(manifest).update(readFileSync(resolve(root,'docs/assets/editor.css'))).update(readFileSync(resolve(root,'docs/index.html'))).update(readFileSync(resolve(root,'docs/GUIDE.html'))).digest('hex').slice(0,16);
const worker=readFileSync(resolve(root,'editor/service-worker.js'),'utf8').replace('destiny-studio-living-v1','destiny-studio-'+revision);
const outputs=[[resolve(root,'docs/sw.js'),worker],[resolve(root,'docs/assets/editor.js'),result.outputFiles[0].text],[resolve(root,'docs/engine-contract.json'),manifest]];
for(const [path,text]of outputs){if(check){if(readFileSync(path,'utf8')!==text)throw new Error(`Static editor stale: ${path}. Run npm run editor:build.`);}else{mkdirSync(dirname(path),{recursive:true});writeFileSync(path,text);}}
console.log(check?'Static files match engine schemas and sources.':'Static editor built in docs/ (no runtime server or CDN).');
