import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {episodeSchema,validateWords} from '../src/voxel/episode/schema.ts';
import {newCaptionStyles,cameraPresets,cameraDirectorSchema,projectPolishSchema} from '../polish/schema.ts';
import {wordMotion,contrastRatio} from '../polish/captions.ts';
import {screenCamera,directCamera} from '../polish/camera.ts';
import {characterState,expandGroup} from '../characters/animations/state.ts';
import {directedPath,costumeVariation} from '../polish/characters.ts';
import {effectBudget,environmentBlocks,atmosphereParticles,atmosphere} from '../polish/environment.ts';
import {withoutPolish} from '../polish/compare.ts';
import {editingAdvice} from '../polish/advice.ts';
import {captionSegment} from '../hybrid/state.ts';
import {estimatedWords} from '../src/voxel/cinematic/timeline.ts';
import {enablePolish,newPerformance} from '../../editor/polish-model.mjs';
import {createLocalNarration} from '../../editor/local-audio.mjs';
import {compatibleCopy,setAtlasReference,patch} from '../../editor/model.mjs';
import {voxelVisualEpisode} from '../hybrid/adapter.ts';
import {setStoryboardType} from '../../editor/hybrid-model.mjs';
import {directWorld} from '../living/director.ts';
const raw=file=>JSON.parse(readFileSync(new URL('../episodes/'+file,import.meta.url)));
const old=()=>raw('hybrid_riis.json'),demo=()=>raw('hybrid_riis_06.json'),parsed=()=>episodeSchema.parse(demo());
test('0.6 is additive, keeps exact 0.5 narration, timing and baseline visual data',()=>{
 const a=old(),b=demo(),plain=withoutPolish(b);assert.equal(b.format.durationFrames,1050);assert.equal(b.schemaVersion,'0.6.0');assert.deepEqual(b.scenes.map(s=>[s.narration,s.startFrame,s.durationFrames]),a.scenes.map(s=>[s.narration,s.startFrame,s.durationFrames]));assert.deepEqual(plain.scenes,a.scenes);assert.deepEqual(plain.shorts,a.shorts);episodeSchema.parse(a);episodeSchema.parse(b);const projected=voxelVisualEpisode(episodeSchema.parse(b));episodeSchema.parse(projected);assert.equal(projected.scenes[1].polish,undefined);assert.ok(b.scenes[1].polish.environment);
});
test('caption styles preserve timestamps and text with bounded deterministic word motion',()=>{
 const e=parsed(),words=estimatedWords(e),snapshot=structuredClone(words);validateWords(words,e);
 for(const style of newCaptionStyles)for(const frame of [0,1,7,15,29,45,90]){const a=wordMotion(style,0,1,frame,true);wordMotion(style,0,1,3,true);assert.deepEqual(wordMotion(style,0,1,frame,true),a);assert.ok(a.scale>=1&&a.scale<=1.1);assert.ok(a.opacity>=0&&a.opacity<=1);assert.equal(wordMotion(style,0,1,frame,true,true).scale,1);}
 assert.deepEqual(words,snapshot);assert.ok(contrastRatio('#ffffff')>4.5);
 const gap=[{text:'one',start:0,end:.2},{text:'two',start:.5,end:1}];assert.equal(captionSegment(gap,10,0,30,5,true).length,2);assert.equal(captionSegment(gap,10,0,30,5,true).some(w=>w.active),false);assert.equal(captionSegment(gap,10,0,30,5).length,0);
});
test('all camera presets seek deterministically and reduced motion freezes new direction',()=>{
 const base={position:[2,4,13],target:[0,2,-3],fov:48};
 for(const preset of cameraPresets){const c=cameraDirectorSchema.parse({preset,durationFrames:120,worldTarget:[2,2,-4]});for(const frame of [0,20,60,120,300]){const first=directCamera(base,c,frame);directCamera(base,c,9);assert.deepEqual(directCamera(base,c,frame),first);assert.ok([...first.position,...first.target,first.fov].every(Number.isFinite));assert.deepEqual(directCamera(base,c,frame,true),base);assert.equal(screenCamera(c,frame,true).scale,1);}assert.ok(screenCamera(c,60).scale<1.3);if(preset==='shake'){assert.deepEqual(directCamera(base,c,300),base);assert.equal(Math.abs(screenCamera(c,300).x),0);}}
});
test('characters stop, turn, follow a target and crowds vary without accumulated state',()=>{
 const e=parsed(),g=e.scenes[3].livingWorld.groups[0],actors=expandGroup(g),a=actors[0];assert.notDeepEqual(costumeVariation(actors[0]),costumeVariation(actors[1]));
 for(const frame of [0,30,90,150,299]){const first=characterState(a,frame);characterState(a,11);assert.deepEqual(characterState(a,frame),first);assert.ok(first.position.every(v=>Math.abs(v)<=18));assert.ok(Object.values(first.pose).every(Number.isFinite));}
 const short={...a,director:{...a.director,startFrame:50,durationFrames:30}};assert.ok(Math.hypot(...characterState(short,80).position.map((v,i)=>v-characterState(short,79).position[i]))<.3);
 const stopped={...a,director:{...a.director,exodus:false}};assert.equal(directedPath(stopped,1000).gait,0);assert.equal(directedPath(stopped,0).gait,0);assert.notDeepEqual(characterState(a,200).pose,characterState({...a,director:undefined},200).pose);
});
test('environment budgets degrade effects, never actors, and particles stay bounded',()=>{
 const e=parsed(),cfg=e.shorts.polish,env=e.scenes[3].polish.environment,final=effectBudget(cfg,'final',64),draft=effectBudget(cfg,'draft',64);
 assert.ok(final.weather+final.atmosphere<=cfg.particleBudget);assert.ok(draft.total<final.total);assert.ok(draft.details<final.details);assert.equal(directWorld(e.scenes[3].livingWorld).length,6);
 for(const frame of [0,90,600,300]){const p=atmosphereParticles(env,frame,128);assert.equal(p.length,128);assert.ok(p.every(p=>p.position.every(Number.isFinite)));assert.deepEqual(atmosphereParticles(env,frame,128),p);assert.ok(environmentBlocks(env,frame,48).length<=144);assert.ok(atmosphere(env,frame).light>=.2);}
 assert.equal(atmosphereParticles(env,0,0).length,0);
});
test('invalid bounds and unsupported visual parameters fail explicitly',()=>{
 for(const modify of [e=>{delete e.shorts;for(const s of e.scenes)delete s.visual;e.render.composition='VoxelCinematicEpisode';},e=>e.shorts.polish.particleBudget=129,e=>e.shorts.polish.detailBudget=49,e=>e.shorts.captions.fontSize=100,e=>e.shorts.captions.leftPx=0,e=>e.shorts.captions.accent='red',e=>e.scenes[0].polish.camera.durationFrames=121,e=>e.scenes[1].livingWorld.groups[0].member.director.durationFrames=999,e=>e.scenes[0].polish.environment=e.scenes[1].polish.environment]){const e=demo();modify(e);assert.equal(episodeSchema.safeParse(e).success,false);}
});
test('pacing recommendations do not change facts, sources, script or timestamps',()=>{
 const e=parsed();e.scenes[0].narration='word '.repeat(100);e.scenes[0].visual.body='x'.repeat(300);delete e.scenes[0].polish;const snapshot=structuredClone(e),advice=editingAdvice(e);assert.ok(advice.some(a=>a.code==='fast-narration'));assert.ok(advice.some(a=>a.code==='dense-text'));assert.deepEqual(e,snapshot);
 e.shorts.captions.color='#111111';assert.ok(editingAdvice(e).some(a=>a.code==='caption-contrast'));
});
test('local narration is a disposable in-memory blob, with no project or network mutation',()=>{
 const calls=[],api={createObjectURL:file=>{calls.push(file);return 'blob:local-test';},revokeObjectURL:url=>calls.push(url)},file={name:'voice.wav',type:'audio/wav',size:100};const p=demo(),before=structuredClone(p),local=createLocalNarration(file,api);assert.equal(local.url,'blob:local-test');local.dispose();local.dispose();assert.deepEqual(calls,[file,'blob:local-test']);assert.deepEqual(p,before);assert.throws(()=>createLocalNarration({name:'voice.exe',type:'',size:1},api));assert.throws(()=>createLocalNarration({...file,size:60*1024*1024},api));
});
test('exports, versioned edits, comparison and undo snapshots retain all known and unknown content',()=>{
 const e=demo();e.extension={keep:true};const copy=compatibleCopy(e);assert.deepEqual(copy.scenes,e.scenes);assert.deepEqual(copy.shorts,e.shorts);assert.equal(e.extension.keep,true);
 const v=setAtlasReference(e,['scenes',1,'atlas'],'riis','before-whirlwind');assert.equal(v.schemaVersion,'0.6.0');assert.deepEqual(v.scenes[1].livingWorld,e.scenes[1].livingWorld);
 const switched=setStoryboardType(e,1,'text');assert.deepEqual(switched.scenes[1].editorEnvironmentDraft,e.scenes[1].polish.environment);assert.equal(switched.scenes[1].polish.environment,undefined);episodeSchema.parse(compatibleCopy(switched));const restored=setStoryboardType(switched,1,'voxel');assert.deepEqual(restored.scenes[1].polish,e.scenes[1].polish);assert.deepEqual(restored.scenes[1].livingWorld,e.scenes[1].livingWorld);
 const prior=old(),next=enablePolish(prior);assert.equal(next.schemaVersion,'0.6.0');assert.deepEqual(prior,old());const changed=patch(next,['shorts','captions','fontSize'],54);assert.equal(next.shorts.captions.fontSize,undefined);assert.equal(changed.shorts.captions.fontSize,54);
});
