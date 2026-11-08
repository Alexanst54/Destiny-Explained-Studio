import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {episodeSchema} from '../src/voxel/episode/schema.ts';
import {elementSchema,elementsSchema,locations,resolveEnvironment,environmentStyle} from '../src/voxel/library/catalog.ts';
import {environmentBoxes,elementParticle} from '../src/voxel/library/layout.ts';
import {resolveDirection,estimatedWords,atFrame} from '../src/voxel/cinematic/timeline.ts';
import {cameraState,transitionState} from '../src/voxel/cinematic/motion.ts';
const load=name=>JSON.parse(readFileSync(new URL(`../episodes/${name}.json`,import.meta.url)));
const demo=()=>episodeSchema.parse(load('voxel_worlds_demo'));
test('old episodes keep their scenes, duration and existing cue defaults',()=>{
 for(const name of ['traveler_episode_002','traveler_episode_002_cinematic']){
  const raw=load(name),e=episodeSchema.parse(raw);for(const plan of raw.direction?.scenes??[])for(const item of [...plan.shots,...plan.actions,...plan.events])if('phrase' in item.at)item.at={occurrence:1,offsetFrames:0,...item.at};assert.deepEqual(e,raw);assert.equal(e.format.durationFrames,1800);
 }
});
test('demo covers four declared worlds, eight continuous shots, valid captions and camera paths',()=>{
 const e=demo(),t=resolveDirection(e,estimatedWords(e));assert.equal(e.format.durationFrames,480);
 assert.deepEqual(e.scenes.map(s=>s.location),locations);
 assert.equal(t.scenes.flatMap(s=>s.shots).length,8);
 for(let frame=0;frame<480;frame++){
  const {scene,shot,events}=atFrame(t,frame),source=e.scenes.find(s=>s.id===scene.sceneId);
  assert.ok(locations.includes(resolveEnvironment(shot.environment,source.location).replace(/^tower$/,'the-tower')));
  const camera=cameraState(t,scene,shot,frame,events);assert.ok([...camera.position,...camera.target,camera.fov].every(Number.isFinite));
 }
 const incoming=t.scenes[1].shots[0];assert.equal(transitionState(t,incoming,incoming.start).opacity,1);
});
test('scene defaults and shot overrides remain distinct and invalid declarations fail',()=>{
 assert.equal(resolveEnvironment('scene','europa'),'europa');assert.equal(resolveEnvironment('tower','europa'),'tower');
 for(const change of [e=>e.environments.pop(),e=>e.environments.push(e.environments[0]),e=>e.scenes[0].location='mars',e=>e.direction.scenes[0].shots[0].environment='unknown',e=>e.environments[1].model='voxel-tower-v1']){
  const e=load('voxel_worlds_demo');change(e);assert.equal(episodeSchema.safeParse(e).success,false);
 }
});
test('all environments contain distinct bounded, finite procedural geometry',()=>{
 const layouts=locations.map(environmentBoxes);
 assert.equal(new Set(layouts.map(x=>JSON.stringify(x))).size,4);
 for(const [i,boxes] of layouts.entries()){
  assert.ok(boxes.length>30&&boxes.length<350,locations[i]);
  for(const b of boxes){assert.ok([...b.position,...b.size].every(Number.isFinite));assert.ok(b.size.every(s=>s>0));assert.ok(b.position.every(p=>Math.abs(p)<40));}
  const style=environmentStyle(locations[i]);assert.ok(style.ambient>.5);assert.ok(style.fogFar>style.fogNear);
 }
});
test('particle motion is bounded and deterministic across seeks, seeds and storm intensity',()=>{
 for(const type of ['snow','particles','light-fragments'])for(const animation of type==='snow'?['drift','blizzard','still']:['pulse','still']){
  const item=elementSchema.parse({id:'test',type,animation,position:[0,0,0],seed:42,count:64});
  const initial=elementParticle(item,3,147);elementParticle(item,3,0);elementParticle(item,3,479);assert.deepEqual(elementParticle(item,3,147),initial);
  for(let frame=0;frame<480;frame++)for(let i=0;i<64;i++){
   const p=elementParticle(item,i,frame);assert.ok([...p.position,p.scale].every(Number.isFinite));assert.ok(p.scale>0&&p.scale<.3);assert.ok(p.position.every(n=>Math.abs(n)<=8));
  }
  if(animation==='still')assert.deepEqual(elementParticle(item,3,0),initial);
 }
 const item={id:'snow',type:'snow',position:[0,0,0]};assert.notDeepEqual(elementParticle({...item,seed:1},0,42),elementParticle({...item,seed:2},0,42));
 assert.notDeepEqual(elementParticle({...item,animation:'drift'},0,42),elementParticle({...item,animation:'blizzard'},0,42));
});
test('reject unsupported element animations, extreme positions and excess particle budgets',()=>{
 const base={id:'a',type:'crystal',position:[0,0,0]};
 for(const extra of [{animation:'walk'},{position:[Infinity,0,0]},{position:[100,0,0]},{scale:0},{seed:-1},{count:65},{type:'external-model'}])assert.equal(elementSchema.safeParse({...base,...extra}).success,false);
 assert.equal(elementsSchema.safeParse([base,base]).success,false);
 assert.equal(elementsSchema.safeParse(Array.from({length:13},(_,i)=>({...base,id:String(i)}))).success,false);
 assert.equal(elementsSchema.safeParse(Array.from({length:5},(_,i)=>({...base,id:String(i),type:'snow',count:64}))).success,false);
 assert.ok(elementsSchema.safeParse(Array.from({length:4},(_,i)=>({...base,id:String(i),type:'snow',count:64}))).success);
});
