import {test} from 'node:test';import assert from 'node:assert/strict';
import {captionsAt} from './captions.ts';
test('French speech intervals preserve punctuation and exact boundaries',()=>{const w=[{text:"L’œil",start:.2,end:.6},{text:'d’Athéon.',start:.65,end:1.2}];assert.equal(captionsAt(w,.19),'');assert.equal(captionsAt(w,.2),'L’œil');assert.equal(captionsAt(w,.6),'');assert.equal(captionsAt(w,.65),'d’Athéon.');assert.equal(captionsAt(w,1.2),'');});

import {readFileSync} from 'node:fs';
test('English pilot captions use the real six-scene Kokoro token intervals',()=>{const base=new URL('../../episodes/atheon-explained-en/',import.meta.url);const script=JSON.parse(readFileSync(new URL('script.json',base),'utf8'));assert.equal(script.language,'en-US');for(const scene of script.scenes){const speech=JSON.parse(readFileSync(new URL(`audio-evidence/${scene.id}/speech.json`,base),'utf8'));assert.equal(speech.locale,'en-US');assert.deepEqual(speech.words.map(w=>w.text),scene.narration.split(/\s+/));for(const word of speech.words)assert.equal(captionsAt(speech.words,(word.start+word.end)/2),word.text);}});
