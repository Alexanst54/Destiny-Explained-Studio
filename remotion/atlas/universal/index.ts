/** Additive documentary API. Deliberately not imported by the legacy renderer/editor. */
import {z} from 'zod';
import raw from './catalog.json' with {type: 'json'};
import evidence from './source-evidence.json' with {type: 'json'};
import {atlas, locationsById} from '../index.ts';
import {atlasRecipe} from '../recipes.ts';
import {charactersById} from '../../characters/index.ts';
import {environmentDefinitions} from '../../src/voxel/library/catalog.ts';
import {universalCatalogSchema} from './schema.ts';
import type {UniversalCatalog} from './schema.ts';

export function validateUniversalCatalog(input: unknown): UniversalCatalog {
  const catalog = universalCatalogSchema.parse(input);
  for (const place of catalog.locations) {
    if (place.legacyLocationId !== null) {
      const legacy = locationsById.get(place.legacyLocationId);
      if (!legacy || place.id !== legacy.id) throw new Error('Legacy location ID changed: ' + place.id);
      const correction = catalog.legacyCorrections.find(c => c.locationId === place.id);
      if (place.parentId !== legacy.parentId && (!correction || correction.originalValue !== legacy.parentId || correction.correctedValue !== place.parentId)) throw new Error('Legacy parent change needs explicit inspected correction: ' + place.id);
      if (correction && correction.originalValue !== legacy.parentId) throw new Error('Correction misstates the original parent: ' + place.id);
    } else if (locationsById.has(place.id)) throw new Error('Existing location must declare its legacy identity: ' + place.id);
  }
  for (const variant of catalog.locationVariants) {
    const place = catalog.locations.find(p => p.id === variant.locationId);
    if (variant.legacyVariantId !== null && (!place?.legacyLocationId || !locationsById.get(place.legacyLocationId)?.variants.some(v => v.id === variant.legacyVariantId))) throw new Error('Unknown legacy location variant: ' + variant.id);
  }
  for (const boss of catalog.bosses) if (boss.characterId !== null && !charactersById.has(boss.characterId)) throw new Error('Unknown legacy character asset: ' + boss.id);
  for (const source of catalog.sources) if (source.legacySourceId !== null) {
    const original = atlas.sources.find(s => s.id === source.legacySourceId);
    if (!original || source.kind !== 'inherited' || source.url !== original.url || source.checkedAt !== original.checkedAt) throw new Error('Legacy source provenance changed: ' + source.id);
  }
  for (const entity of [...catalog.locations, ...catalog.locationVariants, ...catalog.activities, ...catalog.encounters, ...catalog.bosses, ...catalog.bossVariants]) {
    for (const release of [entity.expansion, entity.firstSeen?.releaseId].filter(Boolean)) if (!atlas.coverage.some(r => r.id === release)) throw new Error('Unknown release: ' + release);
  }
  for (const profile of catalog.reuseProfiles) for (const id of profile.characterTemplateIds) {
    const character = charactersById.get(id);
    if (!character || character.visual.model === 'unknown') throw new Error('Reuse template missing or unknown appearance: ' + id);
  }
  for (const plan of catalog.assetReusePlans) {
    const location = plan.target === 'location' ? catalog.locations.find(l => l.id === plan.entityId) : null;
    const variant = plan.target === 'location-variant' ? catalog.locationVariants.find(v => v.id === plan.entityId) : null;
    const variantLocation = variant ? catalog.locations.find(l => l.id === variant.locationId) : null;
    const legacyId = location?.legacyLocationId ?? variantLocation?.legacyLocationId;
    if (!legacyId || (variant && !variant.legacyVariantId)) {
      if (plan.existingRecipe) throw new Error('New/unmodeled entity cannot claim a legacy recipe: ' + plan.entityId);
      continue;
    }
    const reference = {locationId: legacyId, ...(variant?.legacyVariantId ? {variantId: variant.legacyVariantId} : {})};
    const actual = atlasRecipe(reference);
    const expected = {locationId: legacyId, variantId: variant?.legacyVariantId ?? null, baseEnvironment: actual.baseEnvironment ?? null, moduleIds: actual.modules};
    if (JSON.stringify(plan.existingRecipe) !== JSON.stringify(expected)) throw new Error('Existing recipe metadata differs from the actual renderer: ' + plan.entityId);
  }
  const models = new Set<string>(Object.values(environmentDefinitions).map(d => d.model));
  for (const asset of catalog.assets) if (asset.kind === 'remotion-environment' && !models.has(asset.id)) throw new Error('Unknown existing environment: ' + asset.id);
  return catalog;
}

const inventorySchema = z.object({
  reviewedAt: z.iso.date(), method: z.string().min(1),
  inventories: z.array(z.object({sourceId: z.string().min(1), locator: z.string().min(1), type: z.enum(['raid', 'dungeon']), game: z.enum(['D1', 'D2']), availability: z.enum(['current', 'vaulted', 'historical']), asOf: z.iso.date(), activityIds: z.array(z.string().min(1)).min(1)}).strict()),
  activityReviews: z.array(z.object({activityId: z.string().min(1), sources: z.array(z.string()).min(1), mainEncounterIds: z.array(z.string()).min(1), traversalEncounterIds: z.array(z.string()), optionalEncounterIds: z.array(z.string()), bossIds: z.array(z.string()), encounterCoverage: z.enum(['partial', 'reviewed-main-encounters']), bossCoverage: z.enum(['partial', 'reviewed-listed-bosses']), arenaCoverage: z.enum(['named', 'mixed', 'site-only']), variantCoverage: z.literal('partial'), gaps: z.array(z.string()).min(1)}).strict()),
  retrievals: z.array(z.object({sourceId: z.string().min(1), pageTitle: z.string().min(1), revisionId: z.number().int().positive(), url: z.url(), pinnedUrl: z.url(), wikitextSha256: z.string().regex(/^[a-f0-9]{64}$/), checkedAt: z.iso.date(), sections: z.array(z.string()).min(1)}).strict()),
  relationshipReview: z.array(z.object({sourceId: z.string().min(1), locator: z.string().min(1), note: z.string().min(1)}).strict()),
}).strict();
export function validateSourceInventories(input: unknown, catalog: UniversalCatalog) {
  const proof = inventorySchema.parse(input);
  if (proof.reviewedAt !== catalog.reviewedAt) throw new Error('Inventory review date mismatch');
  const groups = new Set<string>();
  for (const group of proof.inventories) {
    const source = catalog.sources.find(s => s.id === group.sourceId);
    if (!source || source.verification !== 'retrieved' || !source.supports.includes('availability')) throw new Error('Inventory needs a retrieved availability source');
    if (group.asOf > proof.reviewedAt) throw new Error('Future inventory status date');
    const key = [group.game, group.type, group.availability].join(':');
    if (groups.has(key)) throw new Error('Duplicate inventory group'); groups.add(key);
    if (new Set(group.activityIds).size !== group.activityIds.length) throw new Error('Duplicate inventory membership');
    const actual = catalog.activities.filter(a => a.type === group.type && a.game === group.game && a.availability === group.availability).map(a => a.id).sort();
    if (JSON.stringify(actual) !== JSON.stringify([...group.activityIds].sort())) throw new Error('Activity inventory differs from reviewed source list: ' + key);
    if (group.activityIds.some(id => catalog.activities.find(a => a.id === id)?.availabilityEvidence?.asOf !== group.asOf)) throw new Error('Inventory availability date mismatch');
    if (group.activityIds.some(id => !catalog.activities.find(a => a.id === id)?.availabilityEvidence?.sources.includes(source.id))) throw new Error('Inventory membership missing its primary availability citation');
  }
  for (const activity of catalog.activities) {
    if (['raid', 'dungeon'].includes(activity.type) && activity.availability !== 'unknown' && !groups.has([activity.game, activity.type, activity.availability].join(':'))) throw new Error('Reviewed inventory group missing for ' + activity.id);
  }
  const reviewed = new Set<string>();
  for (const review of proof.activityReviews) {
    if (reviewed.has(review.activityId)) throw new Error('Duplicate activity review'); reviewed.add(review.activityId);
    const activity = catalog.activities.find(a => a.id === review.activityId);
    if (!activity || activity.encounterCoverage !== review.encounterCoverage) throw new Error('Activity coverage/review mismatch');
    if (!review.sources.every(id => catalog.sources.some(s => s.id === id && s.verification === 'retrieved' && s.supports.includes('relationship')))) throw new Error('Activity review needs inspected relationship sources');
    for (const [category, expected] of [['main', review.mainEncounterIds], ['traversal', review.traversalEncounterIds], ['optional', review.optionalEncounterIds]] as const) {
      const actual = catalog.encounters.filter(e => e.activityId === review.activityId && e.category === category).map(e => e.id).sort();
      if (new Set(expected).size !== expected.length || JSON.stringify([...expected].sort()) !== JSON.stringify(actual)) throw new Error('Encounter review membership differs: ' + review.activityId + '/' + category);
    }
    const encounters = new Set(catalog.encounters.filter(e => e.activityId === review.activityId).map(e => e.id));
    const bosses = [...new Set(catalog.encounterBosses.filter(r => encounters.has(r.encounterId)).map(r => r.bossId))].sort();
    if (new Set(review.bossIds).size !== review.bossIds.length || JSON.stringify([...review.bossIds].sort()) !== JSON.stringify(bosses)) throw new Error('Boss review membership differs: ' + review.activityId);
    if (review.arenaCoverage === 'named' && catalog.encounterLocations.some(r => encounters.has(r.encounterId) && catalog.locations.find(l => l.id === r.locationId)?.type === 'activity-site')) throw new Error('Activity-site fallback cannot claim all named arenas');
  }
  for (const activity of catalog.activities) if (activity.encounterCoverage !== 'not-started' && !reviewed.has(activity.id)) throw new Error('Missing activity review');
  const fetched = new Set<string>();
  for (const r of proof.retrievals) {
    if (fetched.has(r.sourceId)) throw new Error('Duplicate source retrieval'); fetched.add(r.sourceId);
    const source = catalog.sources.find(s => s.id === r.sourceId);
    if (!source || source.verification !== 'retrieved' || source.url !== r.url || source.checkedAt !== r.checkedAt) throw new Error('Retrieval/source provenance mismatch');
    const url = new URL(r.pinnedUrl);
    if (url.protocol !== 'https:' || url.hostname !== new URL(source.url).hostname || url.searchParams.get('oldid') !== String(r.revisionId)) throw new Error('Pinned revision URL mismatch');
  }
  for (const source of catalog.sources) if (source.kind === 'secondary' && source.verification === 'retrieved' && new URL(source.url).hostname === 'www.destinypedia.com' && !fetched.has(source.id)) throw new Error('Inspected wiki source needs a pinned retrieval: ' + source.id);
  for (const review of proof.relationshipReview) if (!catalog.sources.some(s => s.id === review.sourceId && s.verification === 'retrieved' && s.supports.includes('relationship'))) throw new Error('Unknown relationship review source');
  return proof;
}
export const universalAtlas = validateUniversalCatalog(raw);
export const sourceInventories = validateSourceInventories(evidence, universalAtlas);
export const encountersForActivity = (id: string) => universalAtlas.encounters.filter(e => e.activityId === id).sort((a, b) => a.order - b.order);
export const bossesForActivity = (id: string) => {
  const encounters = new Set(encountersForActivity(id).map(e => e.id));
  return universalAtlas.encounterBosses.filter(r => encounters.has(r.encounterId)).map(r => ({...r, boss: universalAtlas.bosses.find(b => b.id === r.bossId)!, variant: universalAtlas.bossVariants.find(v => v.id === r.bossVariantId) ?? null}));
};
