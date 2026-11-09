import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {exportFrame} from './export.ts';
const [source,startText,countText,folder]=process.argv.slice(2),start=Number(startText),count=Number(countText);
if(!folder||!Number.isInteger(start)||!Number.isInteger(count)||count<1||count>90)throw Error('Usage: export-sequence.mjs PROJECT START COUNT(1–90) FOLDER');
const input=JSON.parse(readFileSync(source,'utf8')),out=resolve(folder);mkdirSync(out,{recursive:true});
// Validate the entire range before writing it; no timing resampling or repeated stills.
const frames=Array.from({length:count},(_,i)=>exportFrame(input,start+i));
for(let i=0;i<count;i++)writeFileSync(join(out,`${i.toString().padStart(5,'0')}.json`),JSON.stringify(frames[i]));
writeFileSync(join(out,'export.json'),JSON.stringify({version:1,startFrame:start,fps:30,count,projectId:input.id}));
console.log(`${count} frame-specific snapshots at 30 fps (${count/30}s), source frames ${start}–${start+count-1}`);
