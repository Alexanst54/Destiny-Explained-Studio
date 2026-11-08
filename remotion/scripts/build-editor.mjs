import {build} from 'esbuild';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const check=process.argv.includes('--check');
const result=await build({entryPoints:[resolve(root,'editor/app.mjs')],bundle:true,format:'esm',platform:'browser',target:'chrome110',minify:true,legalComments:'eof',write:false,outfile:resolve(root,'docs/assets/editor.js')});
const sources=['remotion/src/voxel/episode/schema.ts','remotion/src/voxel/cinematic/schema.ts','remotion/src/voxel/cinematic/timeline.ts','remotion/episodes/traveler_episode_002_cinematic.json'];
const manifest=JSON.stringify({format:1,sources:Object.fromEntries(sources.map(p=>[p,createHash('sha256').update(readFileSync(resolve(root,p))).digest('hex')]))},null,2)+'\n';
const outputs=[[resolve(root,'docs/assets/editor.js'),result.outputFiles[0].text],[resolve(root,'docs/engine-contract.json'),manifest]];
for(const [path,text]of outputs){if(check){if(readFileSync(path,'utf8')!==text)throw new Error(`Static editor stale: ${path}. Run npm run editor:build.`);}else{mkdirSync(dirname(path),{recursive:true});writeFileSync(path,text);}}
console.log(check?'Static files match engine schemas and sources.':'Static editor built in docs/ (no runtime server or CDN).');
