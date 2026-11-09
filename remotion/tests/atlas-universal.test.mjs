import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {universalAtlas as atlas,sourceInventories,validateUniversalCatalog,validateSourceInventories,encountersForActivity,bossesForActivity} from '../atlas/universal/index.ts';
import {universalCatalogSchema} from '../atlas/universal/schema.ts';
import {auditAssets,validateAssetFiles,auditMarkdown} from '../scripts/asset-audit.mjs';
import {coverageMarkdown,coverage} from '../scripts/atlas-coverage.mjs';
import {episodeSchema} from '../src/voxel/episode/schema.ts';
import {atlas as legacy,resolveAtlas} from '../atlas/index.ts';
import {atlasRecipe} from '../atlas/recipes.ts';
import {compatibleCopy} from '../../editor/model.mjs';
const read=path=>readFileSync(new URL(path,import.meta.url),'utf8');
const mutate=fn=>{const copy=structuredClone(atlas);fn(copy);return copy;};
const rejected=fn=>assert.equal(universalCatalogSchema.safeParse(mutate(fn)).success,false);

test('reviewed inventories contain 11 Bungie dungeons, 4 D1 raids, 10 current and 5 vaulted D2 raids',()=>{
  assert.equal(atlas.schemaVersion,'0.9.0');assert.equal(legacy.locations.length,468);
  for(const [game,type,status,n]of [['D2','dungeon','current',11],['D1','raid','historical',4],['D2','raid','current',10],['D2','raid','vaulted',5]]) {
    const rows=atlas.activities.filter(a=>a.game===game&&a.type===type&&a.availability===status);assert.equal(rows.length,n);
    const list=sourceInventories.inventories.find(g=>g.game===game&&g.type===type&&g.availability===status);
    assert.deepEqual([...list.activityIds].sort(),rows.map(r=>r.id).sort());
  }
  assert.ok(atlas.activities.some(a=>a.id==='activity-equilibrium-d2'));
});

test('source inventories reject wrong membership, duplicates, removed groups and unverified sources',()=>{
  for(const change of [p=>p.inventories[0].activityIds.pop(),p=>p.inventories[0].activityIds.push(p.inventories[0].activityIds[0]),p=>p.inventories=[],p=>p.inventories[0].sourceId='legacy-wiki-riis',p=>p.reviewedAt='2026-11-08']) {
    const copy=structuredClone(sourceInventories);change(copy);assert.throws(()=>validateSourceInventories(copy,atlas));
  }
});

test('IDs, sources, game scopes, dates and availability cannot be fabricated structurally',()=>{
  for(const change of [
    c=>c.locations.push(c.locations[0]),c=>c.activities[0].id='La Chute de Cropta',
    c=>c.encounters[0].id=c.bosses[0].id,c=>c.sources.push(c.sources[0]),
    c=>c.bosses[0].sources=['missing-source'],c=>c.bosses[0].sources=[],
    c=>c.sources[0].url='http://example.com',c=>c.sources[0].checkedAt='2099-01-01',
    c=>c.activities[0].availabilityEvidence=null,c=>c.activities[0].availabilityEvidence.asOf='2099-01-01',
    c=>c.activities[0].firstSeen.releaseId='d2-base',c=>c.activities[0].firstSeen.date='2026-02-30',
    c=>c.activities[0].firstSeen.date='2099-01-01',
    c=>{c.activities[0].availability='current';c.activities[0].availabilityEvidence.sources=['legacy-wiki-age-of-triumph'];},
    c=>c.bosses[0].appearanceEvidence[0].sources=['bungie-activities'],
    c=>c.activities[0].aliases=['Crota','crota'],
  ])rejected(change);
});

test('unknown parents, cycles, lore-to-game promotion and unsupported playable settings are rejected',()=>{
  for(const change of [
    c=>c.locations[0].parentId='does-not-exist',c=>c.locations[0].parentId=c.locations[0].id,
    c=>{c.locations.find(l=>l.id==='destiny-universe').parentId='earth';},
    c=>c.locations.find(l=>l.id==='fundament').appearanceEvidence[0].kind='gameplay',
    c=>c.locations.find(l=>l.canonStatus==='manifest-attested').appearanceEvidence[0].kind='gameplay',
    c=>c.activityLocations[0].locationId='fundament',c=>c.encounterLocations[0].locationId='destiny-universe',
    c=>c.locationVariants[0].locationId='unknown',
  ])rejected(change);
});

test('relationships validate endpoints, ordering, games, encounter arenas and duplicate edges',()=>{
  for(const change of [
    c=>c.encounters[0].activityId='unknown',c=>c.encounters[0].game='both',
    c=>c.encounters[1].order=c.encounters[0].order,
    c=>c.encounterLocations[0].locationId='mars',c=>c.encounterLocations[0].encounterId='missing',
    c=>c.encounterBosses[0].bossId='missing',c=>c.encounterBosses[0].encounterId='missing',
    c=>c.encounterBosses.push(c.encounterBosses[0]),c=>c.activityLocations.push(c.activityLocations[0]),
    c=>c.encounterLocations.push(c.encounterLocations[0]),
    c=>c.encounterBosses[0].sources=['bungie-activities'],c=>c.encounterBosses[0].sources=['legacy-wiki-age-of-triumph'],
    c=>c.activities[0].encounterCoverage='not-started',c=>c.bossVariants[0].bossId='missing',
  ])rejected(change);
});

test('Taniks is one identity with two linked forms; descent is a pursuer encounter, not a kill objective',()=>{
  assert.equal(atlas.bosses.filter(b=>b.id==='boss-taniks').length,1);
  assert.equal(atlas.bossVariants.filter(v=>v.bossId==='boss-taniks').length,2);
  const links=bossesForActivity('activity-deep-stone-crypt-d2').filter(r=>r.boss.id==='boss-taniks');
  assert.deepEqual(links.map(r=>[r.variant.id,r.role]),[['boss-taniks-variant-reborn','pursuer'],['boss-taniks-variant-abomination','primary']]);
  rejected(c=>{c.encounterBosses.find(r=>r.bossVariantId).bossId='boss-atheon';});
  rejected(c=>{c.bossVariants[0].game='both';c.bosses.find(b=>b.id==='boss-taniks').game='D2';});
  assert.equal(atlas.encounterLocations.filter(r=>r.encounterId==='encounter-deep-stone-crypt-d2-atraks').length,2);
});

test('D1/D2 reprises retain separate encounters and branching derivation cycles fail',()=>{
  assert.notEqual(encountersForActivity('activity-vault-of-glass-d1')[0].id,encountersForActivity('activity-vault-of-glass-d2')[0].id);
  assert.ok(atlas.activityRelations.some(r=>r.fromId==='activity-vault-of-glass-d2'&&r.toId==='activity-vault-of-glass-d1'));
  rejected(c=>c.activityRelations[0].toId=c.activityRelations[0].fromId);
  rejected(c=>c.activityRelations[0].toId='activity-shattered-throne-d2');
  rejected(c=>{const r=c.activityRelations[0];c.activityRelations.push({...r,fromId:r.toId,toId:r.fromId,relation:'variant-of'});});
  rejected(c=>{
    const ids=['activity-last-wish-d2','activity-garden-of-salvation-d2','activity-deep-stone-crypt-d2'];const escape='activity-salvations-edge-d2';
    for(let i=0;i<3;i++)c.activityRelations.push({fromId:ids[i],toId:escape,relation:'variant-of',sources:['wiki-vog'],note:'test'},{fromId:ids[i],toId:ids[(i+1)%3],relation:'variant-of',sources:['wiki-vog'],note:'test'});
  });
});

test('asset reuse checks actual files, entry points, selectors, family and Riis variant restrictions',()=>{
  validateAssetFiles(atlas);
  for(const change of [c=>c.locations[0].remotionAssetId='imaginary-mesh',c=>c.locations[0].visualStatus='dedicated',c=>c.bosses[0].remotionAssetId='atlas-family-vex',c=>c.locations[0].blenderAssetId=c.locations[0].remotionAssetId])rejected(change);
  rejected(c=>c.locationVariants.find(v=>v.blenderAssetId).legacyVariantId='after-whirlwind');
  for(const change of [c=>c.assets[0].path='remotion/missing.ts',c=>c.assets[0].symbol='MissingComponent',c=>c.assets[0].selector='location=made-up'])assert.throws(()=>validateAssetFiles(mutate(change)));
  assert.throws(()=>validateAssetFiles(mutate(c=>c.legacy.catalogSha256='0'.repeat(64))));
});

test('legacy IDs, scoped variants, releases, characters and source provenance remain valid references',()=>{
  for(const change of [c=>c.locations.find(l=>l.legacyLocationId).legacyLocationId='unknown',c=>c.locations.find(l=>l.legacyLocationId).legacyLocationId=null,c=>c.locationVariants[0].legacyVariantId='invented',c=>c.bosses[0].characterId='imaginary-character',c=>c.activities[0].expansion='d1-imaginary',c=>c.sources.find(s=>s.kind==='inherited').url='https://example.com/wrong'])assert.throws(()=>validateUniversalCatalog(mutate(change)));
  assert.equal(resolveAtlas({locationId:'riis',variantId:'before-whirlwind'}).location.id,'riis');assert.equal(atlasRecipe({locationId:'europa'}).baseEnvironment,'europa');
});

test('reports regenerate exactly; historical fixture hashes and editor render copies preserve all fields',()=>{
  const audit=auditAssets();assert.equal(audit.missingReferences.length,0);assert.equal(audit.versioned3dModels.length,0);assert.equal(audit.legacy.locationCount,468);assert.equal(audit.characters.count,33);assert.ok(audit.context.sharedInputs.every(f=>f.unchangedBetweenBranches));
  assert.equal(auditMarkdown(audit),read('../../docs/ASSET-AUDIT.md'));assert.deepEqual(audit,JSON.parse(read('../atlas/universal/asset-audit.json')));
  assert.equal(coverageMarkdown(),read('../../docs/ATLAS-COVERAGE.md'));assert.deepEqual(coverage(),JSON.parse(read('../atlas/universal/coverage.json')));
  assert.equal(audit.fixtures.length,12);
  for(const fixture of audit.fixtures) {
    const content=read('../../'+fixture.path),raw=JSON.parse(content),parsed=episodeSchema.parse(raw);
    assert.equal(createHash('sha256').update(content).digest('hex'),fixture.sha256);assert.deepEqual(compatibleCopy(raw),raw);assert.equal(parsed.format.durationFrames,raw.format.durationFrames);assert.equal(parsed.schemaVersion,raw.schemaVersion);
  }
});
