import {readFileSync,writeFileSync,mkdirSync,unlinkSync,existsSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {isDeepStrictEqual} from 'node:util';
import {fileURLToPath} from 'node:url';
import {episodeSchema,validateWords} from '../src/voxel/episode/schema.ts';
import {directionSchema} from '../src/voxel/cinematic/schema.ts';
import {resolveDirection} from '../src/voxel/cinematic/timeline.ts';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const output=resolve(root,'out/traveler_episode_002_cinematic-ready.json');
try{
 try{unlinkSync(output);}catch(e){if(e.code!=='ENOENT')throw e;}
 const args=process.argv.slice(2);
 if(args.length>1||args.some(a=>!a.startsWith('--intensity=')))throw new Error('Usage: prepare-cinematic.mjs [--intensity=calm|balanced|cinematic]');
 const source=episodeSchema.parse(JSON.parse(readFileSync(resolve(root,'out/traveler_episode_002-ready.json'),'utf8')));
 const episode=episodeSchema.parse(JSON.parse(readFileSync(resolve(root,'episodes/traveler_episode_002_cinematic.json'),'utf8')));
 const spokenScenes=e=>e.scenes.map(({id,narration,startFrame,durationFrames})=>({id,narration,startFrame,durationFrames}));
 if(!isDeepStrictEqual(spokenScenes(source),spokenScenes(episode))||!isDeepStrictEqual(source.format,episode.format))
  throw new Error('Narration scene text/timing differs: regenerate the source narration');
 if(!source.audio.voiceover.enabled||source.audio.voiceover.status!=='ready'||source.subtitles.status!=='ready'||!existsSync(resolve(root,'public',source.audio.voiceover.source)))throw new Error('Generate Kokoro narration first');
 if(args[0])episode.direction.intensity=directionSchema.shape.intensity.parse(args[0].split('=')[1]);
 episode.audio=source.audio;episode.subtitles=source.subtitles;
 const words=validateWords(JSON.parse(readFileSync(resolve(root,'public',source.subtitles.source),'utf8')),episode);
 const timeline=resolveDirection(episode,words);
 mkdirSync(resolve(root,'out'),{recursive:true});
 writeFileSync(resolve(root,'out/cinematic-shot-report.json'),JSON.stringify(timeline,null,2)+'\n');
 writeFileSync(output,JSON.stringify(episode,null,2)+'\n');
 console.log(`${timeline.scenes.flatMap(s=>s.shots).length} narrative shots, 1800 frames, 60 seconds; Kokoro audio reused`);
}catch(e){console.error(e.message);process.exitCode=1;}
