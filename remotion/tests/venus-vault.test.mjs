import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {selectBlenderAsset,blenderSelections} from '../atlas/universal/blender.ts';
import {universalAtlas as atlas,validateUniversalCatalog} from '../atlas/universal/index.ts';
import {validateAssetFiles} from '../scripts/asset-audit.mjs';
const root=fileURLToPath(new URL('../..',import.meta.url));

test('Atlas selections resolve dedicated generators and actual encounter arenas',()=>{
 assert.equal(blenderSelections.length,6);
 for(const id of blenderSelections){const r=selectBlenderAsset(id);assert.equal(r.selectionId,id);assert.equal(r.version,1);}
 assert.equal(selectBlenderAsset('boss-atheon').environmentId,'arena-glass-throne');
 assert.equal(selectBlenderAsset('boss-templar').environmentId,'arena-templars-well');
 assert.equal(selectBlenderAsset('vault-of-glass').environmentId,'arena-templars-well');
 validateAssetFiles(atlas);
});

test('Python and Node produce identical requests for all selections',()=>{
 for(const id of blenderSelections){
  const actual=execFileSync('python',['-c','import sys,json;sys.path.insert(0,"remotion/blender");from venus_vault.request import select;print(json.dumps(select(sys.argv[1])))',id],{cwd:root,encoding:'utf8'});
  assert.deepEqual(JSON.parse(actual),selectBlenderAsset(id));
 }
});

test('bounded options reject unsupported models, animation, dimensions and timings',()=>{
 for(const [id,o]of [['boss-riven',{}],['boss-atheon',{animation:'attack'}],['boss-templar',{animation:'walk'}],['venus',{animation:'temporal'}],['venus',{frames:121}],['venus',{seed:true}],['venus',{width:961}],['venus',{quality:'ultra'}],['venus',{unrecognized:true}]])assert.throws(()=>selectBlenderAsset(id,o));
 assert.equal(selectBlenderAsset('boss-atheon',{animation:'temporal',frames:48}).frames,48);
});

test('boss generator scope cannot be used as another boss, environment or Remotion asset',()=>{
 for(const mutate of [c=>c.bosses.find(b=>b.id==='boss-templar').blenderAssetId='blender-atheon-v1',c=>c.locations.find(b=>b.id==='venus').blenderAssetId='blender-atheon-v1',c=>c.assets.find(a=>a.id==='blender-atheon-v1').bossIds=[],c=>c.bosses.find(b=>b.id==='boss-atheon').remotionAssetId='blender-atheon-v1']){
  const c=structuredClone(atlas);mutate(c);assert.throws(()=>validateUniversalCatalog(c));
 }
 // A dedicated Blender set retains its modular Remotion fallback, without upgrading its fidelity.
 assert.equal(atlas.locations.find(l=>l.id==='venus').remotionAssetId,'atlas-family-vex');
 assert.equal(atlas.assets.find(a=>a.id==='atlas-family-vex').fidelity,'modular-reconstruction');
});
