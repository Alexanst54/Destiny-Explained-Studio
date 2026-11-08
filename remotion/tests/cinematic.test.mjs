import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync} from 'node:fs';
import {episodeSchema} from '../src/voxel/episode/schema.ts';
import {resolveDirection,estimatedWords,resolveCue,atFrame,profiles} from '../src/voxel/cinematic/timeline.ts';
import {actorPose,cameraState,transitionState} from '../src/voxel/cinematic/motion.ts';
const raw=JSON.parse(readFileSync(new URL('../episodes/traveler_episode_002_cinematic.json',import.meta.url)));
const parse=()=>episodeSchema.parse(structuredClone(raw));
const resolve=e=>resolveDirection(e,estimatedWords(e));

test('six scenes and sixteen contiguous purpose-driven shots cover exactly 60 seconds',()=>{
 const e=parse(),t=resolve(e),shots=t.scenes.flatMap(s=>s.shots);
 assert.equal(shots.length,16);assert.equal(shots[0].start,0);assert.equal(shots.at(-1).end,1800);
 for(let i=1;i<shots.length;i++)assert.equal(shots[i].start,shots[i-1].end);
 assert.ok(shots.every(s=>s.purpose.length>=8));
 assert.ok(shots.some(s=>s.end-s.start<50));assert.ok(shots.some(s=>s.end-s.start>=150));
});

test('narration anchors use word timestamps, offsets and occurrence rather than a clock',()=>{
 const e=parse(),s=e.scenes[0];
 const words=[{text:'the',start:1,end:1.2},{text:'Traveler.',start:1.2,end:1.6},
  {text:'the',start:3,end:3.2},{text:'Traveler',start:3.2,end:3.8}];
 assert.equal(resolveCue({phrase:'the Traveler',occurrence:2,offsetFrames:3},s,words),93);
 assert.throws(()=>resolveCue({phrase:'unknown'},s,words));
});

test('invalid shot coverage, impossible references and conflicting actions are rejected',()=>{
 const mutate=[
 e=>e.direction.scenes[0].shots[0].at={sceneFrame:1},
 e=>e.direction.scenes[0].shots[1].at={sceneFrame:1},
 e=>e.direction.scenes[0].shots[1].at={phrase:'not in narration'},
 e=>e.direction.scenes[0].actions[0].durationFrames=500,
 e=>e.direction.scenes[0].actions[1].at={sceneFrame:20},
 e=>e.direction.scenes[0].shots[0].camera.track=undefined,
 e=>e.direction.scenes[0].shots[0].actors.guardian=false,
 e=>e.direction.scenes[0].shots[1].id=e.direction.scenes[0].shots[0].id,
 e=>e.direction.scenes[1].events[0].durationFrames=600,
 e=>e.direction.scenes[0].shots[0].camera.from=e.direction.scenes[0].shots[0].camera.targetFrom,
 e=>e.direction.scenes[0].sceneId='missing-scene',
 e=>e.direction.scenes[0].shots[0].purpose='',
 e=>e.direction.scenes[0].shots[0].camera.mode='random',
 e=>e.direction.scenes[0].shots[0].transition={type:'fade',durationFrames:0},
 e=>e.direction.scenes[0].shots[1].at={phrase:'!!!'},
 e=>{const c=e.direction.scenes[0].shots[0].camera;c.from=[1,0,0];c.to=[-1,0,0];c.targetFrom=c.targetTo=[0,0,0];},
 e=>{const fx=e.direction.scenes[3].events[1];fx.to=fx.position;},
 ];
 for(const change of mutate){const e=structuredClone(raw);change(e);assert.throws(()=>resolve(episodeSchema.parse(e)));}
});

test('all frames, all intensities and seeking produce finite deterministic states',()=>{
 for(const intensity of Object.keys(profiles)){
  const e=parse();e.direction.intensity=intensity;const t=resolve(e);
  for(let f=0;f<1800;f++){
   const {scene,shot,events}=atFrame(t,f),cam=cameraState(t,scene,shot,f,events);
   assert.ok([...cam.position,...cam.target,cam.fov].every(Number.isFinite));
   assert.ok(cam.fov>=25&&cam.fov<=65);
   for(const actor of ['guardian','ghost']){
    const p=actorPose(actor,scene.actions,f,intensity);
    assert.ok([...p.position,...p.rotation,...Object.values(p.joints),p.rise].every(Number.isFinite));
    assert.ok(p.rise>=0&&p.rise<=1);
   }
  }
  const state=f=>{const a=atFrame(t,f);return cameraState(t,a.scene,a.shot,f,a.events);};
  const before=state(640);state(3);state(1799);assert.deepEqual(state(640),before);
 }
});

test('walk, run, jump, fall, resurrection, combat and interaction have distinct poses',()=>{
 const base={id:'test',actor:'guardian',start:0,end:90,durationFrames:90,from:[0,.02,0],to:[1,.02,0],height:1.3,purpose:'Test procedural motion',at:{sceneFrame:0}};
 const poses={};
 for(const animation of ['walk','run','jump','fall','resurrect','combat','interact','look-up'])poses[animation]=actorPose('guardian',[{...base,animation}],35,'cinematic');
 assert.notEqual(poses.walk.joints.legL,0);assert.notEqual(poses.run.joints.legL,poses.walk.joints.legL);
 assert.ok(poses.jump.position[1]>.8);assert.ok(poses.fall.rotation[2]<0);
 assert.ok(poses.resurrect.rise>0&&poses.resurrect.rise<1);assert.notEqual(poses.combat.joints.armL,0);
 assert.notEqual(poses.interact.joints.armR,0);assert.ok(poses['look-up'].joints.head<0);
 const fallen=actorPose('guardian',[{...base,animation:'fall'}],150,'balanced');
 assert.equal(fallen.rotation[2],-Math.PI/2);
});

test('fade is opaque across a scene/environment cut and shake only exists on explicit events',()=>{
 const t=resolve(parse()),s=t.scenes[2].shots[0],prior=t.scenes[1].shots.at(-1);
 assert.equal(transitionState(t,s,s.start).opacity,1);
 assert.ok(transitionState(t,prior,prior.end-1).opacity>.9);
 const action=atFrame(t,640),a=cameraState(t,action.scene,action.shot,640,[]);
 const b=cameraState(t,action.scene,action.shot,640,[{type:'shake',start:630,end:660,durationFrames:30,strength:1}]);
 assert.notDeepEqual(a.position,b.position);
});
