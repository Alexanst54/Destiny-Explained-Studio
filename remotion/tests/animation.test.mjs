import {PerspectiveCamera,Vector3} from 'three';
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {rigSchema,studioSchema,rigAnimations,composerModes} from '../animation/schema.ts';
import {rigBones,rigPose,animationPose,armCount,jointPositions} from '../animation/rig.ts';
import {eliksniPack,packRig} from '../animation/pack.ts';
import {evaluateStudio,separateActors,studioReferences,lodFor} from '../animation/director.ts';
import {composeCamera} from '../animation/camera.ts';
import {episodeSchema} from '../src/voxel/episode/schema.ts';
import {directWorld} from '../living/director.ts';
import {characterState,expandGroup} from '../characters/animations/state.ts';
import {compatibleCopy,setAtlasReference} from '../../editor/model.mjs';
import {enablePolish} from '../../editor/polish-model.mjs';
import {enableStudio,addPackActor,addRigClip,blockingPreset,rigForCharacter} from '../../editor/animation-model.mjs';
import {setStoryboardType} from '../../editor/hybrid-model.mjs';
const load=name=>JSON.parse(readFileSync(new URL('../episodes/'+name,import.meta.url))),demo=()=>episodeSchema.parse(load('hybrid_riis_07.json'));
test('rig hierarchy has independent elbow, knee, hands, feet and four shoulders',()=>{
 for(const p of eliksniPack){const r=packRig(p.id),bones=rigBones(r),ids=new Set();for(const b of bones){assert.ok(!b.parent||ids.has(b.parent));assert.ok(!ids.has(b.id));ids.add(b.id);}assert.equal(bones.filter(b=>b.id.startsWith('shoulder-')).length,armCount(r));assert.equal(armCount(r),p.id==='dreg'?2:p.id==='servitor'?0:4);if(p.id==='servitor')assert.equal(bones.some(b=>b.id.startsWith('hip')),false);}
 const r=packRig('civilian'),bones=rigBones(r),idle=jointPositions(bones,animationPose('idle',0,42)),point=jointPositions(bones,animationPose('point',20,42));assert.notDeepEqual(point['hand-upperR'],idle['hand-upperR']);assert.deepEqual(point['hand-lowerR'],idle['hand-lowerR']);
});
test('six sourced pack archetypes preserve canonical arm counts and unknown dates',()=>{
 const e=demo();for(const p of eliksniPack){let next=addPackActor(e,1,p.id);episodeSchema.parse(next);const a=next.scenes[1].livingWorld.cast.at(-1);assert.equal(a.rig.archetype,p.id);assert.equal(rigForCharacter({...a,rig:undefined}).archetype,p.id);}
 const invalid=addPackActor(e,1,'dreg');invalid.scenes[1].livingWorld.cast.at(-1).rig.archetype='four-arm';assert.equal(episodeSchema.safeParse(invalid).success,false);const bad=demo();bad.scenes[1].livingWorld.cast[0].rig.archetype='dreg';assert.equal(episodeSchema.safeParse(bad).success,false);
});
test('16 animations and clip transitions are deterministic at arbitrary frames',()=>{
 for(const animation of rigAnimations){const r=rigSchema.parse({version:1,archetype:'four-arm',animation,clips:[{animation:'point',startFrame:30,durationFrames:60,transitionFrames:12}]});for(const frame of [0,29,30,31,45,88,89,90,200]){const a=rigPose(r,frame);rigPose(r,7);assert.deepEqual(rigPose(r,frame),a);assert.ok(Object.values(a.rotation).flat().every(Number.isFinite));}const at=rigPose(r,30),plain=rigPose({...r,clips:[]},30);assert.deepEqual(jointPositions(rigBones(r),at),jointPositions(rigBones(r),plain));const end=rigPose(r,90);assert.deepEqual(end,rigPose({...r,clips:[]},90));}
 assert.notDeepEqual(animationPose('run',20,42),animationPose('sprint',20,42));
});
test('old actors keep their exact position and pose when rig/studio absent',()=>{
 const e=episodeSchema.parse(load('hybrid_riis_06.json')),w=e.scenes[1].livingWorld;for(const frame of [0,30,120,200]){const a=directWorld(w)[0],before=characterState(a,frame),s=evaluateStudio(w,undefined,frame)[0];assert.deepEqual(s.position,before.position);assert.equal(s.yaw,before.yaw);assert.equal(a.rig,undefined);}
});
test('interaction references, durations, targets and resolved shot inheritance fail explicitly',()=>{
 for(const modify of [e=>e.scenes[1].livingWorld.studio.interactions[0].targetId='missing',e=>e.scenes[1].livingWorld.studio.interactions[0].actors=['missing'],e=>e.scenes[1].livingWorld.studio.camera.targets=['missing'],e=>e.scenes[1].livingWorld.studio.interactions[0].durationFrames=999,e=>e.scenes[1].livingWorld.cast[0].rig.clips.push({animation:'idle',startFrame:200,durationFrames:30,transitionFrames:12}),e=>e.direction.scenes[1].shots[0].livingWorld={cast:[],groups:[]}]){const e=load('hybrid_riis_07.json');modify(e);assert.equal(episodeSchema.safeParse(e).success,false);}
});
test('follow, event reactions, groups and avoidance are pure and bounded',()=>{
 const w=demo().scenes[3].livingWorld;for(const f of [0,30,90,150,250,299]){const s=evaluateStudio(w,undefined,f);evaluateStudio(w,undefined,44);assert.deepEqual(evaluateStudio(w,undefined,f),s);assert.ok(s.every(a=>a.position.every(v=>Math.abs(v)<=18)));}
 const s=evaluateStudio(w,undefined,100),same=s.slice(0,2).map(f=>({...f,position:[0,0,0]})),out=separateActors(same,.65);assert.ok(Math.hypot(out[0].position[0]-out[1].position[0],out[0].position[2]-out[1].position[2])>=1.29);assert.deepEqual(same.map(f=>f.position),[[0,0,0],[0,0,0]]);
 const g={id:'g',member:w.cast[1],count:3,seed:42,formation:'line',spacing:1.4,behavior:'flee',sizeVariation:.1};const expanded=expandGroup(g);assert.notEqual(expanded[0].rig.seed,expanded[1].rig.seed);assert.notEqual(expanded[0].rig.phaseOffset,expanded[1].rig.phaseOffset);
});
test('all composer modes are deterministic, bounded and freeze with reduced motion',()=>{
 const w=demo().scenes[1].livingWorld,states=evaluateStudio(w,undefined,60),base={position:[2,4,13],target:[0,1.5,-3],fov:46};for(const mode of composerModes){const c={...w.studio.camera,mode,targets:states.slice(0,['two-shot','reverse'].includes(mode)?2:3).map(a=>a.actor.id)};const a=composeCamera(base,c,states,60);assert.deepEqual(composeCamera(base,c,states,60),a);assert.deepEqual(composeCamera(base,c,states,60,true),base);assert.ok([...a.position,...a.target].every(Number.isFinite));assert.ok(a.position[2]>a.target[2]);}
 assert.equal(lodFor('draft',2),0);assert.equal(lodFor('balanced',5),1);assert.equal(lodFor('final',5),2);assert.equal(lodFor('final',30),0);
});
test('blocking editor preserves unknowns, versions, visual drafts, undo snapshots and bounds',()=>{
 const legacy=enableStudio(load('hybrid_riis_06.json'),1);assert.deepEqual(legacy.scenes[1].livingWorld.props,[]);
 const e=demo();e.extension={keep:true};const changed=addRigClip(e,3,0);assert.equal(e.scenes[3].livingWorld.cast[0].rig.clips.length,0);assert.equal(changed.scenes[3].livingWorld.cast[0].rig.clips.length,1);const switched=setStoryboardType(e,1,'text'),restored=setStoryboardType(switched,1,'voxel');assert.deepEqual(restored.scenes[1].livingWorld,e.scenes[1].livingWorld);assert.deepEqual(restored.extension,e.extension);assert.equal(enablePolish(e).schemaVersion,'0.7.0');assert.equal(setAtlasReference(e,['scenes',1,'atlas'],'riis','before-whirlwind').schemaVersion,'0.7.0');episodeSchema.parse(compatibleCopy(e));assert.ok(blockingPreset(e,1,'sky').scenes[1].livingWorld.studio.interactions.length>e.scenes[1].livingWorld.studio.interactions.length);
});
test('Riis keeps 35 seconds, 64 original words and source IDs while showing all five types',()=>{
 const a=load('hybrid_riis.json'),b=demo();assert.equal(b.format.durationFrames,1050);assert.equal(b.scenes.map(s=>s.narration).join(' '),a.scenes.map(s=>s.narration).join(' '));assert.equal(b.scenes.map(s=>s.narration).join(' ').split(/\s+/).length,64);assert.deepEqual(new Set(b.scenes.map(s=>s.visual.type)),new Set(['text','voxel','map','timeline','graphic']));assert.deepEqual(b.shorts.sources,a.shorts.sources);assert.equal(b.scenes.filter(s=>s.visual.type==='voxel').length,2);
});

test('targeted interaction vocabulary stays deterministic and points with the selected upper arm',()=>{
 const original=demo().scenes[1].livingWorld;
 for(const kind of ['look-at','face','walk-together','follow','react','point','form','disperse','flee']){
  const w=structuredClone(original);w.studio.interactions=[{id:'test',kind,actors:kind==='follow'||kind==='face'||kind==='look-at'?['resident-1']:['guide','resident-1'],...(['follow','face','look-at'].includes(kind)?{targetId:'guide'}:{targetPoint:[3,4,-5]}),startFrame:0,durationFrames:210,transitionFrames:12,spacing:1.4,intensity:1}];
  const a=evaluateStudio(w,undefined,70);evaluateStudio(w,undefined,9);assert.deepEqual(evaluateStudio(w,undefined,70),a);if(kind==='point')assert.ok(a[0].pose.rotation['shoulder-upperR'][0]<-.4);
 }
});
test('composer keeps selected heads, hands and feet inside frame and above caption reserve',()=>{
 const w=demo().scenes[1].livingWorld,frames=evaluateStudio(w,undefined,100),base={position:[2,4,13],target:[0,1.5,-3],fov:46};
 for(const mode of composerModes){const targets=frames.slice(0,['two-shot','reverse'].includes(mode)?2:mode==='group'?6:1),c={...w.studio.camera,mode,targets:targets.map(a=>a.actor.id)},pose=composeCamera(base,c,frames,100),camera=new PerspectiveCamera(pose.fov,1080/1920,.1,400);camera.position.set(...pose.position);camera.lookAt(new Vector3(...pose.target));camera.updateMatrixWorld();
  for(const a of targets){const joints=jointPositions(rigBones(a.actor.rig),a.pose);for(const key of ['head','hand-upperL','hand-upperR','hand-lowerL','hand-lowerR','footL','footR']){const local=joints[key],point=new Vector3(local[0]*a.scale,local[1]*a.scale+a.pose.lift,local[2]*a.scale).applyAxisAngle(new Vector3(0,1,0),a.yaw).add(new Vector3(...a.position)).project(camera);assert.ok(Math.abs(point.x)<.96&&point.y<.95&&point.y>-.52,mode+' '+key+' '+point.toArray());}}
 }
});
test('grouped narration validates contiguous unique ids and retains archived settings',()=>{
 for(const groups of [[['hook','exodus']],[['missing','conclusion']],[['history-timeline','reading-graphic'],['reading-graphic','conclusion']]]){const e=demo();e.audio.voiceover.groups=groups;assert.equal(episodeSchema.safeParse(e).success,false);}
});

test('shot animation overrides blend into rig base and composer respects its period',()=>{
 const w=demo().scenes[1].livingWorld;w.cast[0].rig.clips=[];const shot={animations:[{id:'guide',animation:'walk',transitionFrames:20}]};const a=evaluateStudio(w,shot,50,false,50)[0],b=evaluateStudio(w,undefined,50)[0];assert.deepEqual(jointPositions(rigBones(w.cast[0].rig),a.pose),jointPositions(rigBones(w.cast[0].rig),b.pose));assert.equal(a.pose.lift,b.pose.lift);assert.notDeepEqual(evaluateStudio(w,shot,70,false,50)[0].pose,evaluateStudio(w,undefined,70)[0].pose);
 const base={position:[2,4,13],target:[0,1.5,-3],fov:46},c={...w.studio.camera,startFrame:30,durationFrames:60};assert.deepEqual(composeCamera(base,c,evaluateStudio(w,undefined,10),10),base);assert.deepEqual(composeCamera(base,c,evaluateStudio(w,undefined,100),100),base);
});

test('Servitor adapts poses to an orb without ignored humanoid joints',()=>{
 for(const animation of rigAnimations){const pose=rigPose({...packRig('servitor'),animation},40);assert.deepEqual(Object.keys(pose.rotation).sort(),['head','pelvis']);assert.ok(Object.values(pose.rotation).flat().every(Number.isFinite));}
 assert.notDeepEqual(rigPose({...packRig('servitor'),animation:'celebrate'},40),rigPose(packRig('servitor'),40));const clip={animation:'celebrate',startFrame:0,durationFrames:90,transitionFrames:12};assert.notDeepEqual(rigPose({...packRig('servitor'),clips:[clip]},40),rigPose(packRig('servitor'),40));
});
