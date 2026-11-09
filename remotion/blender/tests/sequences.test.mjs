import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {episodeSchema} from '../../src/voxel/episode/schema.ts';
import {validateSequences,sequenceImage} from '../sequences.ts';
const project=episodeSchema.parse(JSON.parse(readFileSync(new URL('../../episodes/hybrid_riis_07.json',import.meta.url))));
const manifest=()=>({version:1,fps:30,projectId:project.id,clips:[{startFrame:120,width:108,height:192,frames:Array.from({length:90},(_,i)=>`assets/blender-video/${'a'.repeat(64)}/${String(i).padStart(5,'0')}.png`)}]});
test('sequence mapping preserves global frame rate and bounds',()=>{const d=validateSequences(manifest(),project);assert.equal(sequenceImage(d,119),undefined);assert.match(sequenceImage(d,120),/00000/);assert.match(sequenceImage(d,209),/00089/);assert.equal(sequenceImage(d,210),undefined);assert.equal(sequenceImage(undefined,120),undefined);});
test('invalid manifests fail explicitly',()=>{for(const edit of [d=>d.fps=24,d=>d.projectId='wrong',d=>d.clips[0].startFrame=0,d=>d.clips.push(d.clips[0]),d=>d.clips[0].frames[0]='../a.png',d=>d.clips[0].width=192,d=>d.clips[0].frames=[]]){const d=manifest();edit(d);assert.throws(()=>validateSequences(d,project));}});
