import {test} from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
import {groupWords,cueAt} from './cinematic_captions.ts';
test('phrases preserve every native word and its measured interval',()=>{
 const root=new URL('../../episodes/atheon-explained-en/',import.meta.url);const script=JSON.parse(readFileSync(new URL('script.json',root),'utf8'));
 for(const s of script.scenes){const words=JSON.parse(readFileSync(new URL(`audio-evidence/${s.id}/speech.json`,root),'utf8')).words;const cues=groupWords(words);assert.deepEqual(cues.flatMap(c=>c.words),words);assert(cues.length<words.length);for(const w of words)assert(cueAt(cues,(w.start+w.end)/2).words.includes(w));for(let i=1;i<cues.length;i++)assert(cues[i].start>=cues[i-1].end);}
});
test('caption boundaries, gaps and long words never gain invented word times',()=>{const words=[{text:'Who',start:.1,end:.2},{text:'is',start:.22,end:.3},{text:'Atheon?',start:.31,end:.6},{text:'Time.',start:1.2,end:1.5}];const c=groupWords(words);assert.equal(c.length,2);assert.equal(cueAt(c,.05),undefined);assert.equal(cueAt(c,.6),undefined);assert.equal(cueAt(c,1.2),c[1]);assert.equal(cueAt(c,1.5),undefined);assert.throws(()=>groupWords([{text:'bad',start:2,end:1}]));});
