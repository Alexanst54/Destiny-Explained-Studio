import {z} from 'zod';
import {families, modules} from '../schema.ts';
import {rigArchetypes} from '../../animation/schema.ts';

const text = z.string().trim().min(1);
const id = text.regex(/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/, 'Stable lowercase language-independent ID required');
const date = z.iso.date();
const ids = z.array(id).refine(xs => new Set(xs).size === xs.length, 'Duplicate references');
const sources = ids.min(1);
export const gameSchema = z.enum(['D1', 'D2', 'both']);
const firstSeen = z.object({game: z.enum(['D1', 'D2']), releaseId: id, date: date.nullable(), sources}).strict();
const evidence = z.object({kind: z.enum(['gameplay', 'cinematic', 'lore', 'simulation', 'manifest-only', 'editorial']), sources, note: text}).strict();
const base = {
  id, game: gameSchema, enName: text, frName: text,
  frNameStatus: z.enum(['official-manifest', 'editorial-translation', 'shortened-official-name', 'untranslated']),
  aliases: z.array(text).refine(xs => new Set(xs.map(x => x.normalize('NFKC').toLowerCase())).size === xs.length, 'Duplicate aliases'),
  expansion: id.nullable(), firstSeen: firstSeen.nullable(), appearanceEvidence: z.array(evidence).min(1),
  canonStatus: z.enum(['attested', 'manifest-attested', 'editorial-container']),
  visualStatus: z.enum(['dedicated', 'modular-reconstruction', 'placeholder']),
  availability: z.enum(['current', 'vaulted', 'historical', 'unknown']),
  availabilityEvidence: z.object({asOf: date, sources, note: text}).strict().nullable(),
  sources, environmentFamily: z.enum(families).nullable(), blenderAssetId: id.nullable(), remotionAssetId: id.nullable(), note: text,
};
export const locationSchema = z.object({...base, type: z.enum(['universe-realm', 'stellar-body', 'destination-region', 'zone', 'historical-site', 'activity-site', 'ship-station', 'lore-world', 'arena']), parentId: id.nullable(), legacyLocationId: id.nullable()}).strict();
const locationVariant = z.object({...base, type: z.literal('historical-variant'), locationId: id, legacyVariantId: id.nullable()}).strict();
export const activitySchema = z.object({...base, type: z.enum(['raid', 'dungeon', 'strike', 'exotic-mission', 'campaign-mission', 'seasonal-activity']), encounterCoverage: z.enum(['not-started', 'partial', 'reviewed-main-encounters']), encounterOrdering: z.enum(['fixed', 'weekly-rotation', 'selectable', 'partial']).default('fixed')}).strict();
export const encounterSchema = z.object({...base, type: z.enum(['combat', 'mechanic', 'traversal']), activityId: id, order: z.number().int().positive(), labelStatus: z.enum(['source-name', 'editorial-objective']), category: z.enum(['main', 'traversal', 'optional']).default('main'), conditions: z.array(text).default([])}).strict();
const boss = z.object({...base, type: z.literal('boss'), characterId: id.nullable(), composition: z.enum(['individual', 'collective', 'mechanism']).default('individual'), compositionNote: text.nullable().default(null), members: z.array(z.object({id, enName: text, condition: text.nullable(), sources}).strict()).default([])}).strict();
const bossVariant = z.object({...base, type: z.literal('boss-variant'), bossId: id, nature: z.enum(['physical-form', 'combat-configuration', 'nightmare', 'projection', 'automaton', 'taken-state', 'gameplay-edition']).default('physical-form')}).strict();
const edge = {sources, note: text};
const source = z.object({id, kind: z.enum(['primary', 'secondary', 'inherited']), title: text, url: z.url().refine(s => s.startsWith('https://'), 'HTTPS required'), checkedAt: date, verification: z.enum(['retrieved', 'inherited-not-rechecked']), locator: text,
  supports: z.array(z.enum(['identity', 'availability', 'release', 'appearance', 'relationship'])).min(1), legacySourceId: text.nullable(), note: text}).strict();
const asset = z.object({id, kind: z.enum(['remotion-environment', 'remotion-family', 'blender-generator', 'blender-boss']), path: text.regex(/^remotion\/(?!.*\.\.).+\.(?:tsx?|py)$/), symbol: text.regex(/^[A-Za-z_][A-Za-z0-9_]*$/), selector: text, families: z.array(z.enum(families)).min(1), locationIds: ids, variantIds: ids, bossIds: ids.default([]), fidelity: z.enum(['dedicated', 'modular-reconstruction'])}).strict();

export const universalCatalogSchema = z.object({
  schemaVersion: z.literal('0.9.0'), reviewedAt: date, scope: text,
  legacy: z.object({catalogPath: z.literal('remotion/atlas/catalog.json'), catalogSha256: text.regex(/^[a-f0-9]{64}$/), schemaVersion: z.literal('0.3.0')}).strict(),
  sources: z.array(source).min(1), assets: z.array(asset),
  locations: z.array(locationSchema).min(1), locationVariants: z.array(locationVariant), activities: z.array(activitySchema), encounters: z.array(encounterSchema), bosses: z.array(boss), bossVariants: z.array(bossVariant),
  activityLocations: z.array(z.object({...edge, activityId: id, locationId: id, role: z.enum(['setting', 'entry', 'arena', 'spans'])}).strict()),
  encounterLocations: z.array(z.object({...edge, encounterId: id, locationId: id}).strict()),
  encounterBosses: z.array(z.object({...edge, encounterId: id, bossId: id, bossVariantId: id.nullable(), role: z.enum(['primary', 'secondary', 'pursuer']), conditions: z.array(text).default([]), outcome: z.enum(['defeat', 'repel', 'escape', 'cleanse', 'disable', 'avoid', 'unknown']).default('unknown')}).strict()),
  activityRelations: z.array(z.object({...edge, fromId: id, toId: id, relation: z.enum(['reprisal-of', 'variant-of'])}).strict()),
  legacyCorrections: z.array(z.object({locationId: id, field: z.literal('parentId'), originalValue: id.nullable(), correctedValue: id.nullable(), sources, note: text}).strict()).default([]),
  reuseProfiles: z.array(z.object({id, label: text, kind: z.enum(['boss', 'environment']), familyIds: z.array(z.enum(families)).min(1), moduleIds: z.array(z.enum(modules)), characterTemplateIds: ids, rigArchetypes: z.array(z.enum(rigArchetypes)), reusableFiles: z.array(z.object({path: text.regex(/^remotion\/(?!.*\.\.).+\.(?:tsx?|py)$/), symbol: text.regex(/^[A-Za-z_][A-Za-z0-9_]*$/)}).strict()).min(1), reusableParts: z.array(text).min(1), requiredWork: z.array(text), limitations: z.array(text).min(1)}).strict()).default([]),
  assetReusePlans: z.array(z.object({entityId: id, target: z.enum(['location', 'location-variant', 'boss', 'boss-variant']), profileIds: ids.min(1), status: z.enum(['proxy-only', 'adaptation-required', 'no-suitable-model']), silhouette: text, existingRecipe: z.object({locationId: id, variantId: id.nullable(), baseEnvironment: z.enum(['the-tower', 'europa', 'black-garden', 'pyramid-interior']).nullable(), moduleIds: z.array(z.enum(modules))}).strict().nullable().default(null), sources, note: text}).strict()).default([]),
  knownGaps: z.array(text).min(1),
}).strict().superRefine((c, ctx) => {
  const fail = (path: (string | number)[], message: string) => ctx.addIssue({code: 'custom', path, message});
  const sourceMap = new Map(c.sources.map(s => [s.id, s]));
  const assetMap = new Map(c.assets.map(a => [a.id, a]));
  const locationMap = new Map(c.locations.map(l => [l.id, l]));
  const activityMap = new Map(c.activities.map(a => [a.id, a]));
  const encounterMap = new Map(c.encounters.map(e => [e.id, e]));
  const bossMap = new Map(c.bosses.map(b => [b.id, b]));
  const bossVariantMap = new Map(c.bossVariants.map(b => [b.id, b]));
  // A parent identity/game scope must cover every game asserted by its child.
  const covers = (parent: string, child: string) => parent === 'both' || parent === child;
  const cite = (refs: string[], path: (string | number)[], capability?: string) => {
    for (const ref of refs) if (!sourceMap.has(ref)) fail(path, 'Unknown source: ' + ref);
    if (capability && !refs.some(ref => sourceMap.get(ref)?.supports.some(s => s === capability))) fail(path, 'Source does not support ' + capability);
  };
  for (const table of ['sources', 'assets', 'locations', 'locationVariants', 'activities', 'encounters', 'bosses', 'bossVariants'] as const) {
    const seen = new Set<string>();
    c[table].forEach((row, i) => {if (seen.has(row.id)) fail([table, i, 'id'], 'Duplicate ID'); seen.add(row.id);});
  }
  const entityIds = new Set<string>();
  for (const table of ['locations', 'locationVariants', 'activities', 'encounters', 'bosses', 'bossVariants'] as const) c[table].forEach((row, i) => {
    const path = [table, i];
    if (entityIds.has(row.id)) fail([...path, 'id'], 'Cross-table entity ID collision');
    entityIds.add(row.id); cite(row.sources, [...path, 'sources'], 'identity');
    row.appearanceEvidence.forEach(e => cite(e.sources, [...path, 'appearanceEvidence'], 'appearance'));
    if (row.canonStatus === 'editorial-container' && row.appearanceEvidence.some(e => e.kind !== 'editorial')) fail(path, 'Editorial container cannot assert a canonical appearance');
    if (row.canonStatus === 'manifest-attested' && row.appearanceEvidence.some(e => e.kind === 'gameplay')) fail(path, 'Manifest alone does not prove gameplay appearance');
    if (row.firstSeen) {
      cite(row.firstSeen.sources, [...path, 'firstSeen'], 'release');
      if (!covers(row.game, row.firstSeen.game) || !row.firstSeen.releaseId.startsWith(row.firstSeen.game.toLowerCase() + '-')) fail(path, 'First-seen game/release mismatch');
      if (row.firstSeen.date && row.firstSeen.date > c.reviewedAt) fail(path, 'Future first-seen date');
    }
    if (row.expansion && row.game !== 'both' && !row.expansion.startsWith(row.game.toLowerCase() + '-')) fail(path, 'Expansion/game mismatch');
    if (row.availability !== 'unknown' && !row.availabilityEvidence) fail(path, 'Availability needs dated evidence');
    if (row.availabilityEvidence) {
      cite(row.availabilityEvidence.sources, [...path, 'availabilityEvidence'], 'availability');
      if (row.availabilityEvidence.asOf > c.reviewedAt) fail(path, 'Future availability observation');
      if (row.availability === 'current' && !row.availabilityEvidence.sources.some(ref => sourceMap.get(ref)?.kind === 'primary' && sourceMap.get(ref)?.verification === 'retrieved')) fail(path, 'Current availability needs retrieved primary evidence');
    }
    const activeAssets = [row.remotionAssetId, row.blenderAssetId].filter((a): a is string => a !== null);
    if (row.visualStatus === 'placeholder' && activeAssets.length) fail(path, 'Placeholder cannot claim an implemented asset');
    if (row.visualStatus !== 'placeholder' && !activeAssets.length) fail(path, 'Rendered visual status needs an existing asset');
    if (row.visualStatus === 'dedicated' && !activeAssets.some(id => assetMap.get(id)?.fidelity === 'dedicated')) fail(path, 'Dedicated status needs at least one dedicated renderer asset');
    for (const [field, ref] of [['remotionAssetId', row.remotionAssetId], ['blenderAssetId', row.blenderAssetId]] as const) {
      if (!ref) continue;
      const a = assetMap.get(ref);
      if (!a) {fail([...path, field], 'Unknown asset'); continue;}
      if ((field === 'blenderAssetId') !== (a.kind.startsWith('blender-'))) fail([...path, field], 'Asset renderer mismatch');
      if (!row.environmentFamily || !a.families.includes(row.environmentFamily)) fail([...path, field], 'Asset family mismatch');
      const locationId = table === 'locationVariants' ? (row as z.infer<typeof locationVariant>).locationId : row.id;
      if (a.locationIds.length && !a.locationIds.includes(locationId)) fail(path, 'Asset outside supported locations');
      if (a.kind === 'blender-boss' && (table !== 'bosses' || !a.bossIds.includes(row.id))) fail(path, 'Boss asset outside supported identity');
      if (a.variantIds.length && (table !== 'locationVariants' || !a.variantIds.includes((row as z.infer<typeof locationVariant>).legacyVariantId ?? ''))) fail(path, 'Asset outside supported variants');
    }
  });
  c.sources.forEach((s, i) => {if (s.checkedAt > c.reviewedAt) fail(['sources', i], 'Future source check'); if ((s.kind === 'inherited') !== (s.verification === 'inherited-not-rechecked')) fail(['sources', i], 'Inherited provenance mismatch');});
  c.assets.forEach((a, i) => {
    a.locationIds.forEach(ref => {if (!locationMap.has(ref)) fail(['assets', i, 'locationIds'], 'Unknown asset location scope');});
    a.bossIds.forEach(ref => {if (!bossMap.has(ref)) fail(['assets', i, 'bossIds'], 'Unknown asset boss scope');});
    if (a.kind === 'blender-boss' && (!a.bossIds.length || a.locationIds.length || a.variantIds.length)) fail(['assets', i], 'Boss generator requires an exclusive boss scope');
    if (a.kind !== 'blender-boss' && a.bossIds.length) fail(['assets', i], 'Only boss generators can declare boss scope');
  });
  c.locations.forEach((l, i) => {
    if (l.parentId && !locationMap.has(l.parentId)) fail(['locations', i, 'parentId'], 'Unknown parent');
    const seen = new Set([l.id]); let parent = l.parentId;
    while (parent) {if (seen.has(parent)) {fail(['locations', i, 'parentId'], 'Location parent cycle'); break;} seen.add(parent); parent = locationMap.get(parent)?.parentId ?? null;}
    if (l.type === 'lore-world' && l.appearanceEvidence.some(e => e.kind === 'gameplay')) fail(['locations', i], 'Lore-only world cannot become a playable destination');
  });
  c.locationVariants.forEach((v, i) => {const l = locationMap.get(v.locationId); if (!l || !covers(l.game, v.game)) fail(['locationVariants', i], 'Unknown or incompatible variant location');});
  uniqueReuseChecks();
  function uniqueReuseChecks() {
    const profiles = new Map(c.reuseProfiles.map(p => [p.id, p]));
    if (profiles.size !== c.reuseProfiles.length) fail(['reuseProfiles'], 'Duplicate reuse profile');
    const targets = new Map<string, {kind: string; family: string | null; placeholder: boolean}>([
      ...c.locations.map(x => [x.id, {kind: 'location', family: x.environmentFamily, placeholder: x.visualStatus === 'placeholder'}] as const),
      ...c.locationVariants.map(x => [x.id, {kind: 'location-variant', family: x.environmentFamily, placeholder: x.visualStatus === 'placeholder'}] as const),
      ...c.bosses.map(x => [x.id, {kind: 'boss', family: x.environmentFamily, placeholder: x.visualStatus === 'placeholder'}] as const),
      ...c.bossVariants.map(x => [x.id, {kind: 'boss-variant', family: x.environmentFamily, placeholder: x.visualStatus === 'placeholder'}] as const),
    ]);
    const planned = new Set<string>();
    c.assetReusePlans.forEach((p, i) => {
      const target = targets.get(p.entityId);
      if (!target || target.kind !== p.target) fail(['assetReusePlans', i], 'Unknown or wrong-kind reuse target');
      if (planned.has(p.entityId)) fail(['assetReusePlans', i], 'Duplicate reuse plan'); planned.add(p.entityId);
      cite(p.sources, ['assetReusePlans', i]);
      const selected = p.profileIds.map(id => profiles.get(id));
      if (selected.some(x => !x)) fail(['assetReusePlans', i], 'Unknown reuse profile');
      const bossTarget = p.target.startsWith('boss');
      if (selected.some(x => x && (x.kind === 'boss') !== bossTarget)) fail(['assetReusePlans', i], 'Reuse profile target mismatch');
      if (target?.family && !selected.some(x => x?.familyIds.includes(target.family as typeof families[number]))) fail(['assetReusePlans', i], 'Reuse family mismatch');
      if (bossTarget && p.status === 'proxy-only') fail(['assetReusePlans', i], 'Environment proxy is not a boss model');
      if (bossTarget && selected.some(x => x && x.requiredWork.length === 0)) fail(['assetReusePlans', i], 'Boss adaptation must declare remaining work');
    });
    for (const [id] of targets) if (!planned.has(id)) fail(['assetReusePlans'], 'Missing reuse plan for ' + id);
    c.bosses.forEach((b, i) => {
      if (b.composition === 'collective' && !b.members.length && !b.compositionNote) fail(['bosses', i], 'Collective boss requires sourced members');
      if (b.composition !== 'collective' && b.members.length) fail(['bosses', i], 'Only a collective may declare members');
      if (new Set(b.members.map(m => m.id)).size !== b.members.length) fail(['bosses', i], 'Duplicate collective member');
      b.members.forEach(m => cite(m.sources, ['bosses', i, 'members'], 'identity'));
    });
    const corrected = new Set<string>();
    c.legacyCorrections.forEach((r, i) => {
      if (corrected.has(r.locationId)) fail(['legacyCorrections', i], 'Duplicate legacy correction'); corrected.add(r.locationId);
      const location = locationMap.get(r.locationId);
      if (!location?.legacyLocationId || location.parentId !== r.correctedValue || r.originalValue === r.correctedValue) fail(['legacyCorrections', i], 'Correction does not match location');
      cite(r.sources, ['legacyCorrections', i], 'relationship');
      if (!r.sources.some(id => sourceMap.get(id)?.verification === 'retrieved')) fail(['legacyCorrections', i], 'Correction needs inspected evidence');
    });
  }
  const orders = new Set<string>();
  c.encounters.forEach((e, i) => {
    const a = activityMap.get(e.activityId);
    if (!a || !covers(a.game, e.game)) fail(['encounters', i], 'Unknown or incompatible activity');
    if (e.category === 'optional' && !e.conditions.length) fail(['encounters', i], 'Optional encounter needs an explicit condition');
    if ((e.category === 'traversal') !== (e.type === 'traversal')) fail(['encounters', i], 'Traversal category/type mismatch');
    const order = e.activityId + ':' + e.order;
    if (orders.has(order)) fail(['encounters', i, 'order'], 'Duplicate encounter order in activity'); orders.add(order);
  });
  c.bossVariants.forEach((v, i) => {const b = bossMap.get(v.bossId); if (!b || !covers(b.game, v.game)) fail(['bossVariants', i], 'Unknown or incompatible boss identity');});
  const uniqueEdges = <T,>(table: string, rows: T[], key: (r: T) => string) => {const seen = new Set<string>(); rows.forEach((row, i) => {const k = key(row); if (seen.has(k)) fail([table, i], 'Duplicate relationship'); seen.add(k);});};
  uniqueEdges('activityLocations', c.activityLocations, r => r.activityId + ':' + r.locationId + ':' + r.role);
  uniqueEdges('encounterLocations', c.encounterLocations, r => r.encounterId + ':' + r.locationId);
  uniqueEdges('encounterBosses', c.encounterBosses, r => r.encounterId + ':' + r.bossId + ':' + r.bossVariantId);
  uniqueEdges('activityRelations', c.activityRelations, r => r.fromId + ':' + r.toId + ':' + r.relation);
  c.activityLocations.forEach((e, i) => {
    const a = activityMap.get(e.activityId), l = locationMap.get(e.locationId);
    if (!a || !l || !covers(l.game, a.game)) fail(['activityLocations', i], 'Unknown or incompatible activity/location');
    if (l?.type === 'lore-world' || l?.canonStatus === 'editorial-container') fail(['activityLocations', i], 'Lore/editorial container cannot be a playable activity setting');
    cite(e.sources, ['activityLocations', i], 'relationship');
  });
  c.encounterLocations.forEach((e, i) => {
    const encounter = encounterMap.get(e.encounterId), l = locationMap.get(e.locationId);
    if (!encounter || !l || !covers(l.game, encounter.game)) fail(['encounterLocations', i], 'Unknown or incompatible encounter/location');
    if (l?.type === 'lore-world' || l?.canonStatus === 'editorial-container') fail(['encounterLocations', i], 'Encounter cannot occur in lore-only/editorial setting');
    if (encounter && !c.activityLocations.some(a => a.activityId === encounter.activityId && a.locationId === e.locationId)) fail(['encounterLocations', i], 'Encounter location must be sourced for its activity');
    cite(e.sources, ['encounterLocations', i], 'relationship');
  });
  c.encounterBosses.forEach((e, i) => {
    const encounter = encounterMap.get(e.encounterId), b = bossMap.get(e.bossId), v = e.bossVariantId ? bossVariantMap.get(e.bossVariantId) : null;
    if (!encounter || !b || !covers(b.game, encounter.game)) fail(['encounterBosses', i], 'Unknown or incompatible encounter/boss');
    if (e.bossVariantId && (!v || v.bossId !== e.bossId || (encounter && !covers(v.game, encounter.game)))) fail(['encounterBosses', i], 'Variant belongs to another boss or game');
    cite(e.sources, ['encounterBosses', i], 'relationship');
    if (!e.sources.some(ref => sourceMap.get(ref)?.verification === 'retrieved' && sourceMap.get(ref)?.supports.includes('relationship'))) fail(['encounterBosses', i], 'New boss relationship needs a retrieved relationship source');
  });
  c.activityRelations.forEach((r, i) => {
    const a = activityMap.get(r.fromId), b = activityMap.get(r.toId);
    if (!a || !b || a.id === b.id || a.type !== b.type) fail(['activityRelations', i], 'Invalid activity relation');
    if (r.relation === 'reprisal-of' && (a?.game !== 'D2' || b?.game !== 'D1')) fail(['activityRelations', i], 'Reprisal must link D2 to D1');
    cite(r.sources, ['activityRelations', i], 'relationship');
  });
  const visiting = new Set<string>(), visited = new Set<string>();
  const visit = (id: string): void => {
    if (visiting.has(id)) {fail(['activityRelations'], 'Activity relation cycle'); return;}
    if (visited.has(id)) return;
    visiting.add(id);
    for (const r of c.activityRelations.filter(r => r.fromId === id)) visit(r.toId);
    visiting.delete(id); visited.add(id);
  };
  for (const id of activityMap.keys()) visit(id);
  c.activities.forEach((a, i) => {
    const list = c.encounters.filter(e => e.activityId === a.id);
    if ((a.encounterCoverage === 'not-started') !== (list.length === 0)) fail(['activities', i], 'Encounter coverage disagrees with actual rows');
    if (!c.activityLocations.some(e => e.activityId === a.id)) fail(['activities', i], 'Activity needs a sourced setting');
  });
});
export type UniversalCatalog = z.infer<typeof universalCatalogSchema>;
