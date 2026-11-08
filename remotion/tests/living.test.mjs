import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {characterCatalogSchema,animations} from '../characters/schema.ts';
import {characterCatalog,characterVisual,searchCharacters} from '../characters/index.ts';
import {castSchema,groupSchema,livingWorldSchema} from '../living/schema.ts';
import {directWorld,loreWarnings,narrativeLabel} from '../living/director.ts';
import {characterState,pathState,expandGroup} from '../characters/animations/state.ts';
import {weatherSchema,weatherTypes,weatherWarnings} from '../weather/schema.ts';
import {weatherState,weatherParticles} from '../weather/state.ts';
import {episodeSchema} from '../src/voxel/episode/schema.ts';
import {resolveDirection,estimatedWords,atFrame} from '../src/voxel/cinematic/timeline.ts';
import {compatibleCopy,validateEpisode,setAtlasReference} from '../../editor/model.mjs';
const load=name=>JSON.parse(readFileSync(new URL('../episodes/'+name,import.meta.url)));
const demo=()=>load('living_europa.json');
const actor=()=>castSchema.parse({id:'a',characterId:'eliksni-civilian',position:[0,0,-3],durationFrames:720,animation:'walk',path:{speed:1,waypoints:[{position:[0,0,-3],pauseFrames:30},{position:[3,0,-3],pauseFrames:15},{position:[3,0,-6],pauseFrames:0}]}});
const weather=()=>weatherSchema.parse(demo().scenes[0].weather);
test('registry sources, variants, identity and unknown appearance',()=>{
 assert.equal(characterCatalogSchema.safeParse(characterCatalog).success,true);
 for(const mutate of [c=>c.characters.push(c.characters[0]),c=>c.characters[0].sources.push('missing'),c=>c.characters[0].variants.push(c.characters[0].variants[0]),c=>c.characters[0].visual.certainty='unknown']){const c=structuredClone(characterCatalog);mutate(c);assert.equal(characterCatalogSchema.safeParse(c).success,false);}
 assert.equal(characterVisual('aurash','auryx').variant.change,'transformation');assert.equal(characterVisual('uldren-sov','crow').variant.change,'resurrection');assert.equal(characterVisual('precursor').visual.model,'unknown');assert.throws(()=>characterVisual('aurash','crow'));assert.ok(searchCharacters('eramis').length);assert.ok(searchCharacters('scientist','exo').length);
});
test('all animations seek deterministically, transition and remain finite',()=>{
 const a=actor();for(const name of animations){a.animation=name;const frames=[0,1,12,39,90,250,719],forward=frames.map(f=>characterState(a,f));for(let i=frames.length-1;i>=0;i--){const s=characterState(a,frames[i]);assert.deepEqual(s,forward[i]);assert.ok(Object.values(s.pose).every(Number.isFinite));}assert.equal(characterState(a,720).active,false);}
 const c=actor();c.clips=[{animation:'terminal',startFrame:100,durationFrames:120,transitionFrames:12}];assert.deepEqual(characterState(c,100).pose,characterState({...c,clips:[]},100).pose);assert.ok(Math.abs(characterState(c,219).pose.armR-characterState(c,220).pose.armR)<.3);
});
test('paths honor speed, pauses, endpoints and orientation',()=>{
 const a=actor();for(const [f,p]of [[29,[0,0,-3]],[60,[1,0,-3]],[130,[3,0,-3]],[1000,[3,0,-6]]])assert.deepEqual(pathState(a,f).position,p);assert.equal(pathState(a,60).yaw,Math.PI/2);assert.equal(Math.abs(pathState(a,200).yaw),Math.PI);
});
test('seeded group placement and paths stay bounded; CPU budget enforced',()=>{
 const g=groupSchema.parse({id:'g',member:actor(),count:24,seed:42,formation:'scatter',spacing:3,behavior:'flee'}),initial=expandGroup(g);expandGroup({...g,seed:3});assert.deepEqual(expandGroup(g),initial);assert.notDeepEqual(expandGroup({...g,seed:3}),initial);assert.equal(new Set(initial.map(a=>a.id)).size,24);
 for(const a of initial){assert.equal(a.animation,'flee');for(const p of [a.position,...a.path.waypoints.map(p=>p.position)])assert.ok(p.every(v=>Math.abs(v)<=18));}
 assert.equal(livingWorldSchema.safeParse({cast:Array.from({length:9},(_,i)=>({...actor(),id:'x'+i})),groups:[g]}).success,false);
});
test('resolved scene/shot population never silently truncates or bypasses CPU budget',()=>{
 const a=actor(),member={...a,id:'member'};
 const group=(id,count)=>groupSchema.parse({id,member,count,seed:42,formation:'line',spacing:1,behavior:'idle'});
 const base=livingWorldSchema.parse({cast:[{...a,id:'base'}],groups:[group('scene',24)]});
 const replacement=Array.from({length:9},(_,i)=>({...a,id:'shot'+i}));
 // Valid scene and valid shot overrides can still exceed the effective combined limit.
 assert.equal(livingWorldSchema.safeParse(base).success,true);
 assert.equal(directWorld(base).length,25);
 assert.throws(()=>directWorld(base,{cast:replacement}),/CPU population budget exceeds 32.*resolved 33/);
 assert.equal(directWorld(base,{cast:replacement,groups:[]}).length,9);
 assert.equal(directWorld(base,{cast:[],groups:[]}).length,0);
 assert.equal(directWorld(base,{groups:[group('new',24)]}).length,25);
 assert.throws(()=>directWorld(base,{groups:[group('new',24)],cast:replacement}),/CPU population budget exceeds 32/);
 assert.throws(()=>directWorld(base,{cast:[{...a,id:'scene'}]}),/Duplicate living world id/);
 const e=demo();
 e.scenes[0].livingWorld={mode:'reconstruction',cast:[{...a,id:'base'}],groups:[group('scene',24)],props:[]};
 e.direction.scenes[0].shots[0].livingWorld={cast:replacement};
 assert.equal(episodeSchema.safeParse(e).success,false,'episode schema rejects inherited over-budget shot');
 e.direction.scenes[0].shots[0].livingWorld={cast:replacement,groups:[]};
 assert.equal(episodeSchema.safeParse(e).success,true,'explicit empty group override restores valid budget');
});
test('weather types, transitions, particles, day cycle and out-of-order seeking',()=>{
 for(const type of weatherTypes){const w={...weather(),type,to:undefined,particleBudget:128};const saved=weatherParticles(w,330);weatherParticles(w,10);assert.deepEqual(weatherParticles(w,330),saved);assert.ok(saved.length<=128);assert.ok(saved.every(p=>p.position.every(Number.isFinite)));assert.equal(weatherParticles(w,720).length,0);}
 const w=weather();assert.equal(weatherState(w,0).mix,0);assert.equal(weatherState(w,600).mix,1);assert.ok(weatherState(w,300).intensity<weatherState(w,600).intensity);assert.ok(weatherState({...w,dayCycleFrames:720},360).daylight<weatherState(w,0).daylight);
 for(const p of [{intensity:2},{windSpeed:31},{visibility:0},{particleBudget:129},{seed:-1},{durationFrames:10,transitionFrames:60}])assert.equal(weatherSchema.safeParse({...w,...p}).success,false);
 assert.ok(weatherWarnings('mars',{...w,type:'snow'}).length);assert.equal(weatherWarnings('europa',w).length,0);
});
test('scene/shot priority, timeline and validation of lifetimes and targets',()=>{
 const e=episodeSchema.parse(demo()),s=e.scenes[0];assert.equal(directWorld(s.livingWorld).length,9);assert.equal(directWorld(s.livingWorld,{cast:[]}).length,8);assert.equal(directWorld(s.livingWorld,{cast:[],groups:[]}).length,0);
 assert.equal(atFrame(resolveDirection(e,estimatedWords(e)),400).shot.start,360);
 for(const mutate of [e=>e.scenes[0].livingWorld.cast[0].durationFrames=721,e=>e.scenes[0].weather.durationFrames=721,e=>e.direction.scenes[0].shots[0].livingWorld={animations:[{id:'missing',animation:'run'}]},e=>e.scenes[0].livingWorld.cast[0].clips=[{animation:'talk',startFrame:700,durationFrames:40}]]){const e=demo();mutate(e);assert.equal(episodeSchema.safeParse(e).success,false);}
});
test('lore warnings flag anachronisms, preserve alternatives and disclose unknowns',()=>{
 const w=livingWorldSchema.parse({mode:'canonical',cast:[{...actor(),characterId:'hive-acolyte'}]});assert.ok(loreWarnings(w,{locationId:'fundament',variantId:'krill-origins'}).some(x=>x.includes('incompatible')));assert.ok(loreWarnings({...w,era:'golden-age',cast:[{...actor(),characterId:'cayde-6'}]}).some(x=>x.includes('postérieure')));
 const a={...w,mode:'alternate-history'};assert.match(narrativeLabel(a),/NOT CANON/);assert.ok(loreWarnings(a).some(x=>x.includes('ALTERNATIVE')));assert.equal(livingWorldSchema.safeParse(a).success,true);
});
test('all demos and legacy episodes; editor retains unknown fields and new contracts',()=>{
 for(const file of readdirSync(new URL('../episodes/',import.meta.url)).filter(x=>x.endsWith('.json'))){const e=episodeSchema.parse(load(file));if(e.direction)resolveDirection(e,estimatedWords(e));}
 const e=demo();e.extension={keep:true};e.scenes[0].livingWorld.cast[0].extension='retain';assert.equal(JSON.parse(JSON.stringify(e)).scenes[0].livingWorld.cast[0].extension,'retain');
 const copy=compatibleCopy(e);assert.equal(copy.scenes[0].livingWorld.cast[0].extension,undefined);assert.equal(validateEpisode(e).unknown.length,2);assert.equal(copy.scenes[0].livingWorld.cast[0].characterId,'human-scientist');assert.equal(setAtlasReference(e,['scenes',0,'atlas'],'riis').schemaVersion,'0.4.0');
});
