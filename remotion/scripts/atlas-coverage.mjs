import {readFileSync,writeFileSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {universalAtlas as c,sourceInventories as proof,encountersForActivity,bossesForActivity} from '../atlas/universal/index.ts';
import {atlas} from '../atlas/index.ts';
const ROOT=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const count=(rows,field)=>Object.fromEntries([...new Set(rows.map(r=>r[field]))].sort().map(k=>[k,rows.filter(r=>r[field]===k).length]));
export const coverage=()=>({reviewedAt:c.reviewedAt,status:'partial',legacyLocationsPreserved:atlas.locations.length,locations:c.locations.length,legacyLocationsLinked:c.locations.filter(l=>l.legacyLocationId).length,newNamedLocations:c.locations.filter(l=>!l.legacyLocationId).length,locationVariants:c.locationVariants.length,activities:c.activities.length,activityTypes:count(c.activities,'type'),encounters:c.encounters.length,bossIdentities:c.bosses.length,bossVariants:c.bossVariants.length,activitiesWithEncounters:c.activities.filter(a=>encountersForActivity(a.id).length).length,activitiesWithoutEncounters:c.activities.filter(a=>!encountersForActivity(a.id).length).map(a=>a.id),bossesWithoutAssets:c.bosses.filter(b=>b.visualStatus==='placeholder').length,retrievedSources:c.sources.filter(s=>s.verification==='retrieved').length,inheritedSources:c.sources.filter(s=>s.kind==='inherited').length,missingPlayableBossModels:c.bosses.filter(b=>b.visualStatus==='placeholder').map(b=>b.id),inventories:proof.inventories});
export function coverageMarkdown() {
 const stats=coverage();
 return [
  '# Couverture de l’Atlas universel D1/D2 — première tranche','',
  `Revue : ${c.reviewedAt}. Issue [#18](https://github.com/Alexanst54/Destiny-Explained-Studio/issues/18). **Couverture partielle** : le mot « universel » désigne le schéma cible, pas l’exhaustivité du contenu ou des assets.`,
  '', '## Chiffres vérifiables','',
  `Le catalogue historique conserve **${stats.legacyLocationsPreserved} lieux et ${atlas.locations.reduce((n,p)=>n+p.variants.length,0)} variantes**. La nouvelle couche relie **${stats.legacyLocationsLinked} IDs existants**, ajoute **${stats.newNamedLocations} lieux nommés sourcés** et relie **${stats.locationVariants} variantes historiques** sans renommer leurs IDs locaux. Aucun JSON 0.3–0.8 n’est migré automatiquement.`,
  '', `Tranche : **${stats.activities} activités**, **${stats.encounters} rencontres**, **${stats.bossIdentities} identités de boss**, **${stats.bossVariants} variantes de boss**. **${stats.activitiesWithEncounters} activités** ont des rencontres pilotes ; les **${stats.activitiesWithoutEncounters.length} autres** restent explicitement not-started. Les activités pilotes restent partial, pas « exhaustives ».`,
  '', '| Inventaire de noms observé | Activités par jeu/version | Source |','| --- | ---: | --- |',
  ...proof.inventories.map(g=>`| ${g.game} — ${g.type} — ${g.availability} | ${g.activityIds.length} | [${g.sourceId}](${c.sources.find(s=>s.id===g.sourceId).url}) · ${g.locator} |`),
  '', 'Les raids repris en D2 sont des activités distinctes de leurs versions D1 ; les 19 lignes de raid ne signifient pas 19 raids narrativement uniques. Eater of Worlds et Spire of Stars sont inclus dans l’inventaire des raids, comme dans la liste historique Bungie. Les 11 donjons correspondent à la liste Bungie consultée à cette date, pas à une constante imposée à toutes les versions futures du schéma.',
  '', '## Destinations, dimensions, sous-zones et lieux historiques','',
  '| ID conservé ou ajouté | Nom | Jeu | Type | Parent | Apparence | Asset Remotion réutilisé |','| --- | --- | --- | --- | --- | --- | --- |',
  ...c.locations.filter(l=>l.type!=='activity-site').map(l=>`| ${l.id} | ${l.enName} | ${l.game} | ${l.type} | ${l.parentId??'—'} | ${l.appearanceEvidence.map(e=>e.kind).join(', ')} | ${l.remotionAssetId??'aucun'} |`),
  '', 'Les lieux classés lore-world, notamment Riis et Fundament, ne deviennent pas des destinations jouables. L’association d’une activité à un lieu ne transforme pas son parent entier en patrouille disponible. Les sources de provenance héritée restent marquées inherited-not-rechecked. La parenté d’une dimension exprime une organisation documentaire, pas des coordonnées astronomiques.',
  '', '## Raids, donjons et première tranche d’autres activités','',
  '| ID stable | Jeu | Activité | Type | Disponibilité sourcée | Rencontres | Boss / formes reliés |','| --- | --- | --- | --- | --- | ---: | --- |',
  ...c.activities.map(a=>`| ${a.id} | ${a.game} | ${a.enName} | ${a.type} | ${a.availability} | ${encountersForActivity(a.id).length} (${a.encounterCoverage}) | ${[...new Set(bossesForActivity(a.id).map(r=>r.variant?.enName??r.boss.enName))].join('; ')||'à recenser'} |`),
  '', 'current signifie présence dans la liste Bungie observée, sans promesse de droits d’accès, matchmaking ou rotation. vaulted est daté et sourcé par le document historique, sans affirmer un retrait permanent. historical pour D1 signifie sortie attestée, pas fermeture de ses serveurs. unknown conserve l’incertitude. `expansion` identifie une ère de sortie ; pour une reprise gratuite, ce champ n’est pas un prérequis de possession.',
  '', '## Rencontres et arènes pilotes','',
  '| Rencontre | Activité | Lieux / arènes attestés | Boss / forme |','| --- | --- | --- | --- |',
  ...c.encounters.map(e=>`| ${e.id} — ${e.enName} | ${e.activityId} | ${c.encounterLocations.filter(r=>r.encounterId===e.id).map(r=>r.locationId).join(', ')} | ${c.encounterBosses.filter(r=>r.encounterId===e.id).map(r=>(r.bossVariantId??r.bossId)+' ('+r.role+')').join(', ')||'pas de boss attribué'} |`),
  '', 'Les objectifs éditoriaux sont signalés par labelStatus=editorial-objective ; ils ne prétendent pas être des noms officiels d’arène. Crypt Security est classé comme entité de boss mécanique par la source ; cela ne lui invente pas une identité de personnage. Taniks est une identité unique : Reborn et Abomination sont deux variantes D2, avec relations séparées aux rencontres. Reborn est noté pursuer lors de la descente ; il n’est pas présenté comme un boss à tuer à cette étape. Atraks relie plusieurs emplacements (Clarity Control et Morning Star).',
  '', '## Sources et limites de vérification','',
  `**${stats.retrievedSources} sources consultées dans cette tranche**, **${stats.inheritedSources} références héritées non re-téléchargées**. Chaque référence comporte URL, section, date, capacité documentaire et statut de vérification. Les listes de contrôle sont dans [source-evidence.json](../remotion/atlas/universal/source-evidence.json). Les références de manifest et leur preuve 0.3 existante ne sont pas remplacées.`,
  '', '| Source consultée | Sections utilisées | Nature |','| --- | --- | --- |',
  ...c.sources.filter(s=>s.verification==='retrieved').map(s=>`| [${s.title}](${s.url}) | ${s.locator} | ${s.kind} |`),
  '', 'Les listes Bungie sont prioritaires pour les inventaires et disponibilités. Les articles Destinypedia ont servi aux relations de rencontres, arènes et boss ; ce sont des sources secondaires, pas des modèles géométriques officiels. Leurs références internes peuvent être incomplètes : la revue reste explicite et partielle. Les noms FR non vérifiés conservent l’anglais et le statut untranslated ; aucune traduction n’est présentée comme officielle par défaut.',
  '', 'La traduction FR du Coffre comporte une date d’An 8 différente du calendrier anglais de Years of Destiny. La tranche utilise la section historique An 4 pour les cinq raids retirés et ne reprend pas cette date contradictoire. Une ancienne liste de retraits ne prime pas sur une liste actuelle : The Whisper est actuel dans la page Activities, tandis que The Menagerie reste un exemple historique retiré.',
  '', '## Lacunes à traiter explicitement','',...c.knownGaps.map(g=>'- '+g),
  '', '## Contrôles et périmètre de livraison','',
  'Le schéma strict vérifie les IDs indépendants de la langue, sources, dates, jeux, parents/cycles, variantes, assets existants, cardinalités et relations plusieurs-à-plusieurs. Les listes de sources sont comparées aux ensembles d’activités, et non seulement à leur nombre. Les scènes de lore ne peuvent pas servir silencieusement de lieu jouable. Les assets sont vérifiés sur disque et leurs sélecteurs correspondent aux entrées procédurales existantes.',
  '', 'Depuis `remotion/` : `npm run test:atlas:universal`, `npm run typecheck:atlas:universal`, `npm run audit:assets -- --check`, `npm run report:atlas:coverage -- --check`. Les tests historiques restent à exécuter ; le rapport de validation liste ce qui a réellement été lancé.',
  '', 'Cette livraison n’ajoute ni filtres éditeur, ni import incrémental automatisé, ni boss/arènes modélisés, ni migration Blender générale. Ces étapes suivent l’audit et la revue documentaire. La PR #17 reste indépendante et non fusionnée. Aucun rendu de 35 secondes.', '',
 ].join('\n');
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
 const outputs=[['docs/ATLAS-COVERAGE.md',coverageMarkdown()],['remotion/atlas/universal/coverage.json',JSON.stringify(coverage(),null,2)+'\n']];
 for(const [file,text]of outputs) {const path=resolve(ROOT,file);if(process.argv.includes('--check')){if(readFileSync(path,'utf8')!==text)throw Error('Coverage report stale: '+file);}else writeFileSync(path,text);}
 console.log(JSON.stringify(coverage()));
}
