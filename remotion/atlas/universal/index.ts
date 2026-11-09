/** Additive documentary API. Deliberately not imported by the legacy renderer/editor. */
import {z} from 'zod';
import raw from './catalog.json' with {type: 'json'};
import evidence from './source-evidence.json' with {type: 'json'};
import {atlas, locationsById} from '../index.ts';
import {charactersById} from '../../characters/index.ts';
import {environmentDefinitions} from '../../src/voxel/library/catalog.ts';
import {universalCatalogSchema} from './schema.ts';
import type {UniversalCatalog} from './schema.ts';

export function validateUniversalCatalog(input: unknown): UniversalCatalog {
  const catalog = universalCatalogSchema.parse(input);
  for (const place of catalog.locations) {
    if (place.legacyLocationId !== null) {
      const legacy = locationsById.get(place.legacyLocationId);
      if (!legacy || place.id !== legacy.id || place.parentId !== legacy.parentId) throw new Error('Legacy location ID/parent changed: ' + place.id);
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
  const models = new Set(Object.values(environmentDefinitions).map(d => d.model));
  for (const asset of catalog.assets) if (asset.kind === 'remotion-environment' && !models.has(asset.id as typeof environmentDefinitions.europa.model)) throw new Error('Unknown existing environment: ' + asset.id);
  return catalog;
}

const inventorySchema = z.object({
  reviewedAt: z.iso.date(), method: z.string().min(1),
  inventories: z.array(z.object({sourceId: z.string().min(1), locator: z.string().min(1), type: z.enum(['raid', 'dungeon']), game: z.enum(['D1', 'D2']), availability: z.enum(['current', 'vaulted', 'historical']), activityIds: z.array(z.string().min(1)).min(1)}).strict()),
  relationshipReview: z.array(z.object({sourceId: z.string().min(1), locator: z.string().min(1), note: z.string().min(1)}).strict()),
}).strict();
export function validateSourceInventories(input: unknown, catalog: UniversalCatalog) {
  const proof = inventorySchema.parse(input);
  if (proof.reviewedAt !== catalog.reviewedAt) throw new Error('Inventory review date mismatch');
  const groups = new Set<string>();
  for (const group of proof.inventories) {
    const source = catalog.sources.find(s => s.id === group.sourceId);
    if (!source || source.verification !== 'retrieved' || !source.supports.includes('availability')) throw new Error('Inventory needs a retrieved availability source');
    const key = [group.game, group.type, group.availability].join(':');
    if (groups.has(key)) throw new Error('Duplicate inventory group'); groups.add(key);
    if (new Set(group.activityIds).size !== group.activityIds.length) throw new Error('Duplicate inventory membership');
    const actual = catalog.activities.filter(a => a.type === group.type && a.game === group.game && a.availability === group.availability).map(a => a.id).sort();
    if (JSON.stringify(actual) !== JSON.stringify([...group.activityIds].sort())) throw new Error('Activity inventory differs from reviewed source list: ' + key);
    if (group.activityIds.some(id => !catalog.activities.find(a => a.id === id)?.availabilityEvidence?.sources.includes(source.id))) throw new Error('Inventory membership missing its primary availability citation');
  }
  for (const activity of catalog.activities) {
    if (['raid', 'dungeon'].includes(activity.type) && activity.availability !== 'unknown' && !groups.has([activity.game, activity.type, activity.availability].join(':'))) throw new Error('Reviewed inventory group missing for ' + activity.id);
  }
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
