import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {episodeSchema} from '../src/voxel/episode/schema.ts';
import {shortsSchema,trackSchema,transitionTypes} from '../hybrid/schema.ts';
import {captionTiming,captionSegment,transitionMotion,audioGain,pacing,sourceUrl} from '../hybrid/state.ts';
import {voxelVisualEpisode} from '../hybrid/adapter.ts';
import {newHybridProject,templateLabels} from '../hybrid/templates.ts';
import {directWorld} from '../living/director.ts';
import {resolveDirection,estimatedWords} from '../src/voxel/cinematic/timeline.ts';
import {compatibleCopy,validateEpisode,moveScene,deleteScene} from '../../editor/model.mjs';
import {addStoryboard,duplicateStoryboard,setStoryboardType,resizeStoryboard} from '../../editor/hybrid-model.mjs';
const load=n=>JSON.parse(readFileSync(new URL('../episodes/'+n,import.meta.url))),demo=()=>load('hybrid_riis.json'),parse=e=>episodeSchema.parse(e);
test('all hybrid and legacy projects parse; voxel adapter retains population and direction',()=>{
 for(const f of readdirSync(new URL('../episodes/',import.meta.url)).filter(n=>n.endsWith('.json'))){const e=parse(load(f));if(e.direction)resolveDirection(e,estimatedWords(e));}
 const e=parse(demo()),v=parse(voxelVisualEpisode(e));assert.equal(v.scenes.length,5);assert.deepEqual(v.scenes[1].livingWorld,e.scenes[1].livingWorld);assert.equal(v.shorts,undefined);
});
test('sources, duplicate IDs, map endpoints, timeline, order and unsupported composition fail explicitly',()=>{
 for(const mutate of [e=>e.scenes[2].visual.nodes.push(e.scenes[2].visual.nodes[0]),e=>e.scenes[2].visual.routes[0].to='absent',e=>e.scenes[2].visual.nodes[0].locationId='missing',e=>e.scenes[0].visual.sources=['invented'],e=>e.scenes[0].id=e.scenes[1].id,e=>e.scenes[1].startFrame++,e=>e.format.durationFrames=1801,e=>e.render.composition='VoxelCinematicEpisode',e=>delete e.scenes[0].visual,e=>e.scenes[0].visual.transition.durationFrames=100,e=>e.scenes[1].livingWorld.mode='alternate-history',e=>e.scenes[0].narration='x'.repeat(121)]){const e=demo();mutate(e);assert.equal(episodeSchema.safeParse(e).success,false);}
 const o=load('hybrid_oryx.json');assert.ok(o.scenes[2].visual.events.every(x=>x.date===null&&x.sources.length));o.scenes[2].visual.events[0].sources=['unknown'];assert.equal(episodeSchema.safeParse(o).success,false);assert.match(sourceUrl(parse(demo()),'wiki-riis'),/^https:/);
});
test('inherited cast budget and duplicate populations never truncate',()=>{
 const e=parse(demo()),w=e.scenes[1].livingWorld,g=w.groups[0];assert.equal(directWorld(w).length,6);assert.equal(directWorld(w,{groups:[]}).length,0);assert.throws(()=>directWorld(w,{groups:[{...g,id:'a',count:24},{...g,id:'b',count:24}]}),/32/);assert.throws(()=>directWorld(w,{groups:[g,g]}),/Duplicate/);
});
test('storyboard editing and type switching preserve content, resources and continuous timing',()=>{
 let e=demo();e.extension={keep:true};e=duplicateStoryboard(e,1);assert.equal(e.scenes.length,6);e=moveScene(e,2,1);assert.deepEqual(e.direction.scenes.map(p=>p.sceneId),e.scenes.map(s=>s.id));e=deleteScene(e,3);
 const world=structuredClone(e.scenes[1].livingWorld);e=setStoryboardType(e,1,'text');assert.deepEqual(e.scenes[1].livingWorld,world);e=setStoryboardType(e,1,'voxel');assert.deepEqual(e.scenes[1].livingWorld,world);assert.deepEqual(e.extension,{keep:true});assert.deepEqual(compatibleCopy(e).scenes[1].livingWorld,world);assert.ok(validateEpisode(e).unknown.length>=1);
 e=resizeStoryboard(e,0,5);assert.equal(e.scenes[1].startFrame,150);assert.equal(e.format.durationFrames,e.scenes.reduce((n,s)=>n+s.durationFrames,0));assert.equal(addStoryboard(e,'graphic').scenes.at(-1).visual.type,'graphic');
});
test('six narrative templates retain every supplied paragraph and label What If',()=>{
 const paragraphs=Array.from({length:7},(_,i)=>'Supplied paragraph '+i+'.');for(const id of Object.keys(templateLabels)){const e=newHybridProject(id,paragraphs.join('\n\n'),'My topic');assert.equal(e.scenes.map(s=>s.narration).join('\n\n'),paragraphs.join('\n\n'));parse(e);if(id==='what-if')assert.equal(e.shorts.mode,'hypothesis');}
 const single=Array.from({length:80},(_,i)=>'word'+i).join(' '),split=newHybridProject('did-you-know',single);assert.equal(split.scenes.map(s=>s.narration).join(' '),single);
 const e=newHybridProject('what-if');e.shorts.mode='canonical';assert.equal(episodeSchema.safeParse(e).success,false);
});
test('caption timestamps, styles, scene bounds and incomplete fallback',()=>{
 const e=parse(demo()),words=estimatedWords(e);assert.equal(captionTiming(e,words).exact,true);assert.equal(captionTiming(e,words.slice(1)).exact,false);assert.equal(captionTiming(e).exact,false);e.shorts.alignedWords=words;assert.equal(captionTiming(e).exact,true);delete e.shorts.alignedWords;const bad=structuredClone(words);bad[0].end=100;assert.equal(captionTiming(e,bad).exact,false);
 for(const frame of [0,45,119,120,359,600,1049]){const s=e.scenes.find(s=>frame>=s.startFrame&&frame<s.startFrame+s.durationFrames),chunk=captionSegment(words,frame,s.startFrame,s.startFrame+s.durationFrames);assert.ok(chunk.length<=5);assert.ok(chunk.every(w=>w.start>=s.startFrame/30&&w.end<=(s.startFrame+s.durationFrames)/30+1e-6));}
 for(const style of ['clean-documentary','dynamic-shorts','cinematic-minimal'])assert.equal(shortsSchema.safeParse({...e.shorts,captions:{...e.shorts.captions,style}}).success,true);assert.equal(shortsSchema.safeParse({...e.shorts,captions:{...e.shorts.captions,bottomPx:50}}).success,false);
});
test('transition and motion evaluations are deterministic, bounded and respect reduced motion',()=>{
 for(const type of transitionTypes)for(const frame of [0,3,8,12,100]){const a=transitionMotion(type,frame,12);transitionMotion(type,2,12);assert.deepEqual(transitionMotion(type,frame,12),a);assert.ok(a.opacity>=0&&a.opacity<=1&&a.flash<=.12);assert.ok(Number.isFinite(a.scale));}
 assert.equal(transitionMotion('slide',0,12,true).x,0);assert.equal(transitionMotion('zoom',0,12,true).scale,1);assert.equal(transitionMotion('flash',0,12,true).flash,0);
});
test('audio provenance, fades, ducking, synchronization and forbidden external playback',()=>{
 const t=trackSchema.parse({id:'ambience',kind:'ambience',source:'assets/local.wav',startFrame:0,durationFrames:300,volume:.5,fadeInFrames:15,fadeOutFrames:15,ducking:.2,provenance:{title:'Original tone',creator:'Author',license:'original',attribution:''}}),words=[{text:'speech',start:2,end:3}];assert.equal(audioGain(t,0,words),0);assert.equal(audioGain(t,300,words),0);assert.ok(audioGain(t,75,words)<audioGain(t,150,words));assert.equal(audioGain(t,75,words),audioGain(t,75,words));
 for(const p of [{source:'https://external.example/audio.mp3'},{source:'../secret'},{fadeInFrames:250,fadeOutFrames:250},{provenance:{...t.provenance,license:'CC-BY'}}])assert.equal(trackSchema.safeParse({...t,...p}).success,false);const e=demo();e.shorts.audio.tracks=[{...t,startFrame:1040}];assert.equal(episodeSchema.safeParse(e).success,false);
});
test('pacing is editorial advice and JSON round trips retain storyboard resources',()=>{
 const e=demo(),s=pacing(parse(e));assert.equal(s.total,35);assert.equal(s.hook,4);assert.deepEqual(s.visualTypes,['text','voxel','map']);assert.ok(s.recommendations.some(x=>x.includes('viralité')));const c=compatibleCopy(JSON.parse(JSON.stringify(e)));assert.deepEqual(c.scenes,e.scenes);assert.deepEqual(c.shorts,e.shorts);assert.deepEqual(c.direction,e.direction);
});
