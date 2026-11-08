import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {atlas,atlasStatistics,locationsById,resolveAtlas,searchAtlas,atlasRefSchema} from '../atlas/index.ts';
import {atlasCatalogSchema,modules,families} from '../atlas/schema.ts';
import {atlasRecipe} from '../atlas/recipes.ts';
import {atlasBoxes,moduleBoxes} from '../atlas/geometry.ts';
import {episodeSchema,validateWords} from '../src/voxel/episode/schema.ts';
import {resolveDirection,estimatedWords,atFrame} from '../src/voxel/cinematic/timeline.ts';
import {cameraState,transitionState} from '../src/voxel/cinematic/motion.ts';
import {compatibleCopy,setAtlasReference,validateEpisode,newEpisode,patch} from '../../editor/model.mjs';
const load=name=>JSON.parse(readFileSync(new URL(`../episodes/${name}.json`,import.meta.url)));
const demo=()=>episodeSchema.parse(load('atlas_demo'));
test('catalog relations, sources, locale labels and coverage are internally consistent',()=>{
 assert.ok(atlasCatalogSchema.safeParse(atlas).success);
 const usedSources=new Set(atlas.locations.flatMap(p=>[...p.sources,...p.variants.flatMap(v=>v.sources)]));assert.ok(atlas.sources.every(s=>usedSources.has(s.id)));
 const stats=atlasStatistics();assert.equal(stats.locations,atlas.locations.length);assert.equal(Object.values(stats.categories).reduce((a,b)=>a+b,0),stats.locations);
 assert.equal(stats.sourcedLocations,stats.locations);assert.ok(stats.variants>=17);assert.equal(stats.dedicatedEnvironments.length,4);
 for(const p of atlas.locations){assert.ok(p.names.en&&p.names.fr);assert.ok(p.sources.length);assert.ok(p.appearance.note);assert.ok(p.parentId===null||locationsById.has(p.parentId));}
 for(const release of atlas.coverage){const count=atlas.locations.filter(p=>p.availability.some(a=>a.releases.includes(release.id))).length;assert.equal(count,release.locationCount);}
});
test('invalid parents, cycles, source IDs and variant IDs are rejected',()=>{
 for(const change of [c=>c.locations[0].parentId='does-not-exist',c=>c.locations[0].parentId=c.locations[1].id,c=>c.locations[0].sources=['missing-source'],c=>c.locations.push(c.locations[0]),c=>c.locations.find(p=>p.variants.length).variants.push(c.locations.find(p=>p.variants.length).variants[0])]){
  const c=structuredClone(atlas);change(c);assert.equal(atlasCatalogSchema.safeParse(c).success,false);
 }
 assert.equal(atlasRefSchema.safeParse({locationId:'fake-planet'}).success,false);
 assert.equal(atlasRefSchema.safeParse({locationId:'riis',variantId:'golden-age'}).success,false);
});
test('search supports French, English, accents, aliases, parent, civilization and historical variants',()=>{
 for(const q of ['Riis','Tourbillon','Néomuna','neomuna','EDZ','ZME','Fundament','Kepler'])assert.ok(searchAtlas({query:q}).length,q);
 assert.ok(searchAtlas({parentId:'europa-regions'}).every(p=>p.parentId==='europa-regions'));
 assert.ok(searchAtlas({civilization:'eliksni'}).some(p=>p.id==='riis'));
 assert.ok(searchAtlas({category:'historical-variant',era:'golden-age'}).some(p=>p.id==='mercury'));
});
test('old JSON and version tags preserve their fields and durations',()=>{
 for(const name of ['traveler_episode_002','traveler_episode_002_cinematic','voxel_worlds_demo']){
  const raw=load(name),e=episodeSchema.parse(raw);assert.equal(e.format.durationFrames,raw.format.durationFrames);assert.ok(!e.scenes.some(s=>'atlas'in s));
  for(const version of ['0.1.0-draft','0.1','0.1.0','0.2','0.2.0'])assert.ok(episodeSchema.safeParse({...raw,schemaVersion:version}).success);
 }
});
test('Atlas selection and export preserve advanced and unknown fields',()=>{
 let e=newEpisode();e.custom={preserve:1};e.scenes[0].atlas={locationId:'europa',custom:{keep:true}};
 e=setAtlasReference(e,['scenes',0,'atlas'],'riis','before-whirlwind');assert.equal(e.schemaVersion,'0.3.0');assert.deepEqual(e.scenes[0].atlas.custom,{keep:true});assert.deepEqual(e.custom,{preserve:1});
 e=setAtlasReference(e,['direction','scenes',0,'shots',0,'atlas'],'fundament','krill-origins');assert.equal(e.direction.scenes[0].shots[0].environment,'scene');
 const result=validateEpisode(e);assert.ok(result.valid);assert.ok(result.unknown.includes('scenes.0.atlas.custom'));
 const copy=compatibleCopy(e);assert.ok(episodeSchema.safeParse(copy).success);assert.equal(copy.scenes[0].atlas.custom,undefined);assert.equal(e.scenes[0].atlas.custom.keep,true);
 assert.throws(()=>setAtlasReference(e,['scenes',0,'atlas'],'fake-planet'));
});
test('all catalog recipes and variants have bounded deterministic geometry, all modules are usable',()=>{
 const refs=atlas.locations.flatMap(p=>[{locationId:p.id},...p.variants.map(v=>({locationId:p.id,variantId:v.id}))]);
 for(const ref of refs){
  const recipe=atlasRecipe(ref),boxes=atlasBoxes(recipe,73);assert.ok(boxes.length<=700,ref.locationId);
  for(const b of boxes){assert.ok([...b.position,...b.size].every(Number.isFinite));assert.ok(b.size.every(n=>n>0));assert.ok(b.position.every(n=>Math.abs(n)<45));}
  atlasBoxes(recipe,0);atlasBoxes(recipe,719);assert.deepEqual(atlasBoxes(recipe,73),boxes);
  if(!recipe.baseEnvironment)assert.ok(recipe.reconstructed);
 }
 const recipe=atlasRecipe({locationId:'riis',variantId:'before-whirlwind'});
 for(const module of modules)assert.ok(moduleBoxes(module,recipe,0).length,module);
 assert.ok(atlasRecipe({locationId:'europa',variantId:'bray-ruins'}).baseEnvironment==='europa');
 assert.ok(!atlasRecipe({locationId:'fundament',variantId:'krill-origins'}).modules.includes('hive'));
});
test('24-second demo is continuous, narrated, marked reconstruction and free of ancient Guardians',()=>{
 const e=demo(),words=estimatedWords(e);validateWords(words,e);const t=resolveDirection(e,words);
 assert.equal(e.format.durationFrames,720);assert.equal(e.scenes.length,4);
 const recipes=e.scenes.map(s=>atlasRecipe(s.atlas));assert.equal(new Set(recipes.map(r=>r.render.family)).size,4);assert.ok(recipes.every(r=>r.reconstructed));
 for(const scene of t.scenes.slice(0,3))assert.ok(scene.shots.every(s=>!s.actors.guardian&&!s.actors.ghost));
 for(let frame=0;frame<720;frame++){const {scene,shot,events}=atFrame(t,frame),c=cameraState(t,scene,shot,frame,events);assert.ok([...c.position,...c.target,c.fov].every(Number.isFinite));}
 for(const scene of t.scenes.slice(1))assert.equal(transitionState(t,scene.shots[0],scene.start).opacity,1);
});
test('Bungie references resolve to archived bilingual evidence, including exact bubble labels',()=>{
 const proof=JSON.parse(readFileSync(new URL('../atlas/manifest-evidence.json',import.meta.url)));
 for(const source of atlas.sources.filter(s=>s.kind==='primary-manifest')){
  const row=proof.definitions[source.id];assert.ok(row,source.id);assert.ok(row.en.name);assert.ok(row.fr.name);
 }
 for(const location of atlas.locations.filter(p=>p.canonStatus==='manifest-attested'))assert.ok(location.availability.every(a=>a.game==='D2'), 'D2 bubble must not imply D1 availability: '+location.id);
 for(const location of atlas.locations)for(const ref of location.manifestRefs??[]){
  const key=`bungie-${ref.game.toLowerCase()}-${ref.component}-${ref.hash}`;
  assert.ok(location.sources.includes(key),location.id);
  const rows=proof.definitions[key];assert.ok(rows,location.id);
  for(const lang of ['en','fr']){
   const record=ref.bubbleHash?rows[lang].bubbles.find(b=>String(b.hash)===ref.bubbleHash)?.displayProperties:rows[lang];
   assert.ok(record,location.id+' '+lang);
   if(location.frenchNameStatus==='official-manifest')assert.equal(location.names[lang],record.name,location.id+' '+lang);
  }
 }
});
