import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {dirname,resolve} from 'node:path';
import {exportFrame} from './export.ts';
const args=process.argv.slice(2);
try{
 if(args.length<3||args.length>4)throw new Error('Usage: node --experimental-strip-types blender/export.mjs project.json frame output.json [standard|cinematic]');
 const [source,frame,out,profile='standard']=args;if(!['standard','cinematic'].includes(profile))throw new Error('Unknown quality profile');
 const data=exportFrame(JSON.parse(readFileSync(resolve(source),'utf8')),Number(frame),profile);
 mkdirSync(dirname(resolve(out)),{recursive:true});writeFileSync(resolve(out),JSON.stringify(data,null,2)+'\n');console.log(`${data.source.sceneId}: frame ${frame}, ${data.actors.length} actors, ${data.meshes.length} primitives → ${out}`);for(const omission of data.omissions)console.warn('SCOPE: '+omission);
}catch(e){console.error(e.message);process.exitCode=1;}
