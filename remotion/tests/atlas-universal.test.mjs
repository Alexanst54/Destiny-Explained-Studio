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
  assert.equal(atlas.activities.find(a=>a.id==='activity-menagerie-d2').availabilityEvidence.asOf,'2020-11-10');
});

test('source inventories reject wrong membership, duplicates, removed groups and unverified sources',()=>{
  for(const change of [p=>p.inventories[0].activityIds.pop(),p=>p.inventories[0].activityIds.push(p.inventories[0].activityIds[0]),p=>p.inventories=[],p=>p.inventories[0].sourceId='legacy-wiki-riis',p=>p.reviewedAt='2026-11-08',p=>p.inventories[0].asOf='2020-01-01',p=>p.inventories[0].asOf='2099-01-01']) {
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

test('Taniks is one identity with four linked forms; descent is a pursuer encounter, not a kill objective',()=>{
  assert.equal(atlas.bosses.filter(b=>b.id==='boss-taniks').length,1);
  assert.equal(atlas.bossVariants.filter(v=>v.bossId==='boss-taniks').length,4);
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
  for(const change of [c=>c.locations[0].remotionAssetId='imaginary-mesh',c=>c.locations[0].visualStatus='dedicated',c=>c.bosses.find(b=>b.visualStatus==='placeholder').remotionAssetId='atlas-family-vex',c=>c.locations[0].blenderAssetId=c.locations[0].remotionAssetId])rejected(change);
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

test('all 19 base raids and 11 dungeons have reviewed main encounters; Epic and route samples stay partial',()=>{
 const primary=sourceInventories.inventories.flatMap(g=>g.activityIds);
 assert.equal(new Set(primary).size,30);
 for(const id of primary){
  const activity=atlas.activities.find(a=>a.id===id),review=sourceInventories.activityReviews.find(r=>r.activityId===id);
  assert.equal(activity.encounterCoverage,'reviewed-main-encounters',id);assert.ok(review.mainEncounterIds.length>0,id);
  assert.ok(bossesForActivity(id).some(r=>r.role==='primary'),id);
 }
 const epic=atlas.activities.find(a=>a.id==='activity-desert-perpetual-epic-d2');assert.equal(epic.encounterCoverage,'partial');assert.equal(epic.availability,'unknown');
 assert.ok(atlas.activityRelations.some(r=>r.fromId===epic.id&&r.toId==='activity-desert-perpetual-d2'&&r.relation==='variant-of'));
 assert.equal(atlas.activities.find(a=>a.id==='activity-leviathan-raid-d2').encounterOrdering,'weekly-rotation');
 assert.equal(atlas.activities.find(a=>a.id==='activity-desert-perpetual-d2').encounterOrdering,'selectable');
 for(const a of atlas.activities.filter(a=>a.type==='strike'||a.type==='exotic-mission'))assert.equal(a.encounterCoverage,'partial');
});

test('all 11 dungeon final bosses and important grouped fights are explicitly related',()=>{
 const finals={'shattered-throne':'boss-dul-incaru','pit-of-heresy':'boss-zulmak','prophecy':'boss-kell-echo','grasp-of-avarice':'boss-avarokk','duality':'boss-caiatl','spire-of-watcher':'boss-persys','ghosts-of-deep':'boss-simmumah','warlords-ruin':'boss-hefnd-vengeance','vespers-host':'boss-corrupted-puppeteer','sundered-doctrine':'boss-kerrev','equilibrium':'boss-sere'};
 for(const [activity,boss]of Object.entries(finals))assert.ok(bossesForActivity('activity-'+activity+'-d2').some(r=>r.boss.id===boss&&r.role==='primary'),activity);
 const daughters=bossesForActivity('activity-kings-fall-d1').filter(r=>r.encounterId.endsWith('-daughters'));
 assert.deepEqual(daughters.map(r=>r.bossId).sort(),['boss-ir-anuk','boss-ir-halak']);
 assert.ok(encountersForActivity('activity-last-wish-d2').some(e=>e.id.endsWith('-queenswalk')));
 assert.equal(bossesForActivity('activity-last-wish-d2').filter(r=>r.encounterId.endsWith('-queenswalk')).length,0);
});

test('catalysts, quests and Rite opponents remain conditional and collective members are not variants',()=>{
 const optional=atlas.encounters.filter(e=>e.category==='optional');assert.ok(optional.length>=15);assert.ok(optional.every(e=>e.conditions.length));
 const rite=optional.filter(e=>e.conditions.includes('Rite of the Nine'));assert.equal(rite.length,4);
 for(const e of rite)assert.ok(e.conditions.includes('Eternity or Ultimatum difficulty'));
 assert.ok(optional.some(e=>e.conditions.some(x=>x.includes('Xenophage'))));
 assert.ok(optional.some(e=>e.conditions.some(x=>x.includes('Buried Bloodline'))));
 const beasts=atlas.bosses.find(b=>b.id==='boss-royal-beasts');assert.equal(beasts.members.filter(m=>m.condition===null).length,6);assert.equal(beasts.members.filter(m=>m.condition==='Prestige only').length,2);
 const raneiks=atlas.bosses.find(b=>b.id==='boss-raneiks');assert.equal(raneiks.members.length,10);assert.equal(new Set(raneiks.members.map(m=>m.id)).size,10);
 assert.equal(atlas.bossVariants.filter(v=>v.bossId==='boss-raneiks').length,2);
 rejected(c=>{c.encounters.find(e=>e.category==='optional').conditions=[];});
 rejected(c=>{c.bosses.find(b=>b.id==='boss-raneiks').members.push(c.bosses.find(b=>b.id==='boss-raneiks').members[0]);});
});

test('representations and outcomes do not invent deaths or conflate physical identities',()=>{
 for(const [activity,id]of [['last-wish','boss-kalli'],['last-wish','boss-shuro-chi'],['corrupted','boss-sedia']])assert.equal(bossesForActivity('activity-'+activity+'-d2').find(r=>r.bossId===id).outcome,'cleanse');
 assert.equal(bossesForActivity('activity-salvations-edge-d2').find(r=>r.bossId==='boss-witness').outcome,'repel');
 assert.equal(bossesForActivity('activity-leviathan-raid-d2').find(r=>r.bossId==='boss-calus').variant.nature,'automaton');
 assert.equal(bossesForActivity('activity-duality-d2').find(r=>r.bossId==='boss-caiatl').variant.nature,'nightmare');
 assert.notEqual(atlas.bosses.find(b=>b.id==='boss-corrupted-puppeteer').id,atlas.bosses.find(b=>b.id==='boss-atraks').id);
 assert.ok(atlas.bossVariants.find(v=>v.id==='boss-siriks-variant-brig').appearanceEvidence.every(e=>e.kind==='simulation'));
 assert.ok(bossesForActivity('activity-lake-of-shadows-original-d2').some(r=>r.bossId==='boss-grask'));
 assert.ok(bossesForActivity('activity-lake-of-shadows-d2').some(r=>r.bossId==='boss-gorath'));
});

test('curated activity review sets reject deleted bosses, wrong coverage and unreviewed steps',()=>{
 for(const change of [p=>p.activityReviews[0].mainEncounterIds.pop(),p=>p.activityReviews[0].bossIds.pop(),p=>p.activityReviews.push(p.activityReviews[0]),p=>p.activityReviews=[],p=>p.activityReviews[0].sources=['bungie-activities'],p=>p.activityReviews[0].encounterCoverage='partial']){
  const p=structuredClone(sourceInventories);change(p);assert.throws(()=>validateSourceInventories(p,atlas));
 }
 const catalog=mutate(c=>{c.encounterBosses=c.encounterBosses.filter(r=>r.bossId!=='boss-kerrev');});
 assert.throws(()=>validateSourceInventories(sourceInventories,catalog));
});

test('pinned revisions validate source identity, date, host, revision ID and coverage of inspected wikis',()=>{
 assert.ok(sourceInventories.retrievals.length>=100);
 for(const change of [p=>p.retrievals[0].revisionId++,p=>p.retrievals[0].pinnedUrl='https://example.com/?oldid='+p.retrievals[0].revisionId,p=>p.retrievals[0].checkedAt='2026-11-08',p=>p.retrievals.push(p.retrievals[0]),p=>p.retrievals.pop(),p=>p.retrievals[0].wikitextSha256='wrong']){
  const p=structuredClone(sourceInventories);change(p);assert.throws(()=>validateSourceInventories(p,atlas));
 }
});

test('reuse plans cover every boss, form and environment without promoting them to implemented models',()=>{
 const targets=[...atlas.bosses,...atlas.bossVariants,...atlas.locations,...atlas.locationVariants];assert.equal(atlas.assetReusePlans.length,targets.length);
 for(const target of targets)assert.equal(atlas.assetReusePlans.filter(p=>p.entityId===target.id).length,1);
 for(const b of [...atlas.bosses,...atlas.bossVariants]){assert.equal(b.remotionAssetId,null);if(['boss-atheon','boss-templar'].includes(b.id)){assert.equal(b.visualStatus,'dedicated');assert.ok(b.blenderAssetId);}else{assert.equal(b.visualStatus,'placeholder');assert.equal(b.blenderAssetId,null);}}
 const plan=id=>atlas.assetReusePlans.find(p=>p.entityId===id),profiles=id=>plan(id).profileIds.map(p=>atlas.reuseProfiles.find(r=>r.id===p));
 assert.ok(profiles('boss-sere').some(p=>p.characterTemplateIds.includes('human-scientist')));
 assert.ok(profiles('boss-harrow').some(p=>p.characterTemplateIds.includes('cabal-soldier')));
 assert.ok(plan('boss-kerrev').silhouette.includes('Weaver'));
 assert.ok(plan('boss-digital-tracker').silhouette.includes('Wyvern'));
 assert.equal(plan('boss-riven').status,'no-suitable-model');assert.equal(plan('boss-witness').status,'no-suitable-model');
 for(const change of [c=>c.assetReusePlans.pop(),c=>c.assetReusePlans[0].profileIds=['missing'],c=>c.assetReusePlans.push(c.assetReusePlans[0]),c=>c.assetReusePlans.find(p=>p.target==='boss').status='proxy-only',c=>c.reuseProfiles.find(p=>p.kind==='boss').requiredWork=[]])rejected(change);
 assert.throws(()=>validateUniversalCatalog(mutate(c=>c.reuseProfiles.find(p=>p.kind==='boss').characterTemplateIds=['precursor'])));
 assert.throws(()=>validateAssetFiles(mutate(c=>c.reuseProfiles[0].reusableFiles[0].path='remotion/missing.ts')));
 assert.throws(()=>validateAssetFiles(mutate(c=>c.reuseProfiles[0].reusableFiles[0].symbol='Missing')));
});

test('legacy recipe metadata matches actual modules, historical overrides and Europa/Bray reuse',()=>{
 const plans=atlas.assetReusePlans.filter(p=>p.existingRecipe);assert.ok(plans.length>80);
 const riis=plans.find(p=>p.entityId==='riis-variant-after-whirlwind');assert.ok(riis.existingRecipe.moduleIds.includes('weather'));
 const europa=plans.find(p=>p.entityId==='europa');assert.equal(europa.existingRecipe.baseEnvironment,'europa');
 const bray=plans.find(p=>p.entityId==='deep-stone-site');assert.equal(bray.existingRecipe.baseEnvironment,'europa');assert.deepEqual(bray.existingRecipe.moduleIds,['bray']);
 assert.throws(()=>validateUniversalCatalog(mutate(c=>c.assetReusePlans.find(p=>p.existingRecipe).existingRecipe.moduleIds=['weather'])));
 assert.throws(()=>validateUniversalCatalog(mutate(c=>c.assetReusePlans.find(p=>p.target==='boss').existingRecipe=plans[0].existingRecipe)));
});

test('foundation IDs survive and parent corrections are explicit, sourced and isolated from legacy JSON',()=>{
 const baseline=JSON.parse(read('../atlas/universal/foundation-ids.json'));
 for(const [table,ids]of Object.entries(baseline.ids)){const actual=new Set(atlas[table].map(r=>r.id));for(const id of ids)assert.ok(actual.has(id),table+'/'+id);}
 assert.equal(legacy.locations.find(l=>l.id==='desert-perpetual').parentId,'kepler');
 assert.equal(atlas.locations.find(l=>l.id==='desert-perpetual').parentId,'unknown-periphery');
 const correction=atlas.legacyCorrections.find(r=>r.locationId==='desert-perpetual');assert.equal(correction.originalValue,'kepler');assert.ok(correction.sources.includes('wiki-desert'));
 assert.throws(()=>validateUniversalCatalog(mutate(c=>c.legacyCorrections=[])));
 assert.throws(()=>validateUniversalCatalog(mutate(c=>c.legacyCorrections[0].originalValue='venus')));
 rejected(c=>c.legacyCorrections[0].sources=['legacy-wiki-riis']);
});
