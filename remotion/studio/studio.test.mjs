import {test} from 'node:test';import assert from 'node:assert/strict';
import {captionsAt} from './captions.ts';
test('French speech intervals preserve punctuation and exact boundaries',()=>{const w=[{text:"L’œil",start:.2,end:.6},{text:'d’Athéon.',start:.65,end:1.2}];assert.equal(captionsAt(w,.19),'');assert.equal(captionsAt(w,.2),'L’œil');assert.equal(captionsAt(w,.6),'');assert.equal(captionsAt(w,.65),'d’Athéon.');assert.equal(captionsAt(w,1.2),'');});
