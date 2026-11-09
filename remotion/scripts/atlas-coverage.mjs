import {readFileSync,writeFileSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {universalAtlas as c,sourceInventories as proof,encountersForActivity,bossesForActivity} from '../atlas/universal/index.ts';
import {atlas} from '../atlas/index.ts';
const ROOT=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const count=(rows,field)=>Object.fromEntries([...new Set(rows.map(r=>r[field]))].sort().map(k=>[k,rows.filter(r=>r[field]===k).length]));
const variants=new Set(c.activityRelations.filter(r=>r.relation==='variant-of').map(r=>r.fromId));
const reviewById=new Map(proof.activityReviews.map(r=>[r.activityId,r]));
const profileById=new Map(c.reuseProfiles.map(p=>[p.id,p]));
const sourceById=new Map(c.sources.map(s=>[s.id,s]));
const retrievalById=new Map(proof.retrievals.map(s=>[s.sourceId,s]));
const linkSource=id=>{const source=sourceById.get(id),snapshot=retrievalById.get(id);return `[${source.title}](${snapshot?.pinnedUrl??source.url})`;};
export const coverage=()=>({
 reviewedAt:c.reviewedAt,status:'partial',legacyLocationsPreserved:atlas.locations.length,
 locations:c.locations.length,legacyLocationsLinked:c.locations.filter(l=>l.legacyLocationId).length,newNamedLocations:c.locations.filter(l=>!l.legacyLocationId).length,locationVariants:c.locationVariants.length,
 activities:c.activities.length,activityTypes:count(c.activities,'type'),baseRaids:c.activities.filter(a=>a.type==='raid'&&!variants.has(a.id)).length,variantActivities:[...variants],
 encounters:c.encounters.length,encounterCategories:count(c.encounters,'category'),bossIdentities:c.bosses.length,bossCompositions:count(c.bosses,'composition'),bossVariants:c.bossVariants.length,variantNatures:count(c.bossVariants,'nature'),
 activitiesWithEncounters:proof.activityReviews.length,activitiesWithoutEncounters:c.activities.filter(a=>!encountersForActivity(a.id).length).map(a=>a.id),
 encounterCoverage:count(c.activities,'encounterCoverage'),baseRaidsWithReviewedMainEncounters:c.activities.filter(a=>a.type==='raid'&&!variants.has(a.id)&&a.encounterCoverage==='reviewed-main-encounters').length,dungeonsWithReviewedMainEncounters:c.activities.filter(a=>a.type==='dungeon'&&a.encounterCoverage==='reviewed-main-encounters').length,
 bossCoverage:count(proof.activityReviews,'bossCoverage'),arenaCoverage:count(proof.activityReviews,'arenaCoverage'),
 bossesWithoutAssets:c.bosses.filter(b=>b.visualStatus==='placeholder').length,missingPlayableBossModels:c.bosses.filter(b=>b.visualStatus==='placeholder').map(b=>b.id),
 reusePlans:c.assetReusePlans.length,exactLegacyRecipes:c.assetReusePlans.filter(p=>p.existingRecipe).length,reuseProfiles:c.reuseProfiles.length,reuseStatuses:count(c.assetReusePlans,'status'),
 retrievedSources:c.sources.filter(s=>s.verification==='retrieved').length,inheritedSources:c.sources.filter(s=>s.kind==='inherited').length,pinnedRevisions:proof.retrievals.length,
 legacyCorrections:c.legacyCorrections,inventories:proof.inventories,activityReviews:proof.activityReviews,
});
export function coverageMarkdown() {
 const stats=coverage();
 return [
  '# Atlas universel D1/D2 — rencontres, boss et réemploi des assets','',
  `Revue : ${c.reviewedAt}. Issue [#18](https://github.com/Alexanst54/Destiny-Explained-Studio/issues/18), fondation PR #19, extension PR #20 et refonte visuelle 0.9.1. **Couverture encore partielle** : une revue des rencontres principales ne signifie ni inventaire de tous les ennemis/défis, ni arènes modélisées, ni variantes exhaustives.`,
  '', '## Périmètre vérifié','',
  `**${stats.baseRaidsWithReviewedMainEncounters}/${stats.baseRaids} raids de base** par jeu/version et **${stats.dungeonsWithReviewedMainEncounters}/11 donjons D2** ont leurs rencontres principales relues. Le Désert perpétuel Epic reste une édition séparée et partielle, comme la documentation de sa source. Les autres assauts et missions exotiques sont ajoutés progressivement et gardent leur statut partial.`,
  '', `Le catalogue contient **${stats.activities} activités**, **${stats.encounters} étapes** (${Object.entries(stats.encounterCategories).map(([k,v])=>`${v} ${k}`).join(', ')}), **${stats.bossIdentities} entrées de boss** et **${stats.bossVariants} formes/variantes**. Les boss comprennent des identités, des collectifs et des mécanismes : pas ${stats.bossIdentities} personnes distinctes. Les membres de Raneiks ou des Bêtes royales ne sont pas des variantes d’un individu.`,
  '', `Les **${stats.legacyLocationsPreserved} lieux historiques et 17 variantes** restent intacts. Cette couche relie ${stats.legacyLocationsLinked} IDs existants, documente ${stats.newNamedLocations} lieux/arènes supplémentaires et ${stats.locationVariants} variantes historiques. Les ${stats.reusePlans} plans de réemploi couvrent chaque lieu, variante de lieu, boss et forme ; **deux boss et trois décors Blender dédiés sont implémentés dans l’extension Vénus/Caveau** (interprétations voxel originales, pas cartes exactes).`,
  '', '| Liste primaire de noms | Nombre | État attesté au | Source |','| --- | ---: | --- | --- |',
  ...proof.inventories.map(g=>`| ${g.game} — ${g.type} — ${g.availability} | ${g.activityIds.length} | ${g.asOf} | ${linkSource(g.sourceId)} |`),
  '', 'Les reprises D1/D2 et l’édition Epic ont des IDs différents. Les raid lairs sont inclus comme dans les listes Bungie. Le nombre 11 décrit la liste primaire consultée, pas une limite permanente du schéma. current ne garantit ni droits, rotation ou accessibilité d’un compte ; le retrait An 4 reste daté de 2020-11-10, distinct de la consultation en 2026.',
  '', '## Couverture par activité','',
  '| Activité / ID | Jeu | Principales / parcours / conditionnelles | Rencontres | Boss listés | Arènes | Ordre | Source de revue |','| --- | --- | ---: | --- | --- | --- | --- | --- |',
  ...c.activities.map(a=>{const r=reviewById.get(a.id);return `| ${a.enName} · ${a.id} | ${a.game} | ${r?[r.mainEncounterIds.length,r.traversalEncounterIds.length,r.optionalEncounterIds.length].join(' / '):'0 / 0 / 0'} | ${a.encounterCoverage} | ${r?.bossCoverage??'not-started'} | ${r?.arenaCoverage??'not-started'} | ${a.encounterOrdering} | ${r?r.sources.map(linkSource).join('; '):'à revoir'} |`;}),
  '', '`reviewed-main-encounters` est limité aux étapes principales des sources indiquées. `reviewed-listed-bosses` porte sur la liste relue, pas tous les Champions/Majors du jeu. Les arènes mixed ou site-only gardent leurs limites : un rattachement large à un lieu d’activité n’est pas un nom de salle officiel. Les détails et lacunes par activité sont conservés dans source-evidence.json et coverage.json.',
  '', '## Rencontres, arènes et adversaires','',
  '| ID / étape | Catégorie / condition | Lieux sourcés | Boss / forme — rôle, résultat |','| --- | --- | --- | --- |',
  ...c.activities.flatMap(a=>encountersForActivity(a.id).map(e=>`| ${e.id} · ${e.enName} | ${e.category}${e.conditions.length?' · '+e.conditions.join('; '):''} | ${c.encounterLocations.filter(r=>r.encounterId===e.id).map(r=>r.locationId).join(', ')} | ${c.encounterBosses.filter(r=>r.encounterId===e.id).map(r=>(r.bossVariantId??r.bossId)+` (${r.role}, ${r.outcome}${r.conditions.length?'; '+r.conditions.join('; '):''})`).join('; ')||'pas de boss individuel attribué'} |`)),
  '', 'Le cœur de Riven est une escorte, pas un boss inventé. Kalli, Shuro Chi et Sedia sont libérées/soignées, pas tuées. Le Léviathan détruit un automate de Calus ; Duality combat des Cauchemars de Gahlran/Caiatl, pas leurs corps physiques. Taniks Reborn poursuit les joueurs pendant la descente ; le Témoin est repoussé dans le raid, sa conclusion appartient à Excision. Les objectifs et configurations libellés éditorialement sont signalés, sans inventer de nom propre officiel.',
  '', 'Les conditions Prestige, quête, catalyseur et Rite of the Nine ne sont pas appliquées aux versions standard. La reprise de Zero Hour est décrite comme simulation ; elle ne devient pas un nouvel événement de la chronologie. L’ordre des épreuves du Léviathan dépend de la semaine ; les trois premiers boss du Désert perpétuel sont sélectionnables. `order` est documentaire, jamais une timeline vidéo.',
  '', '## Identités, formes et collectifs','',
  '| Forme / ID | Identité | Nature | Limite |','| --- | --- | --- | --- |',
  ...c.bossVariants.map(v=>`| ${v.enName} · ${v.id} | ${v.bossId} | ${v.nature} | ${v.note} |`),
  '', '| Collectif | Membres / conditions |','| --- | --- |',
  ...c.bosses.filter(b=>b.composition==='collective').map(b=>`| ${b.enName} | ${b.members.length?b.members.map(m=>m.enName+(m.condition?' ('+m.condition+')':'')).join('; '):b.compositionNote} |`),
  '', 'Le Puppeteer est conservé comme une identité distincte d’Atraks-1 malgré le corps utilisé. Ecthar, Vorlog, Praksis, Taniks et les autres formes documentées restent reliés à leurs identités ; cela ne fusionne pas les rencontres de leurs différentes éditions. Les classes et silhouettes proviennent des biographies inspectées ; les familles artistiques ne remplacent pas une classification canonique.',
  '', '## Familles et composants réutilisables par boss / forme','',
  '| Boss ou forme | Profil(s) | Templates / rigs historiques | État de réemploi |','| --- | --- | --- | --- |',
  ...c.assetReusePlans.filter(p=>p.target.startsWith('boss')).map(p=>{const profiles=p.profileIds.map(id=>profileById.get(id));return `| ${p.entityId} | ${profiles.map(x=>x.label).join('; ')} | ${[...new Set(profiles.flatMap(x=>x.characterTemplateIds))].join(', ')||'aucun template fidèle'} / ${[...new Set(profiles.flatMap(x=>x.rigArchetypes))].join(', ')||(p.status==='implemented-stylized'?'nouveau rig Blender dédié':'aucun rig historique adapté')} | ${p.status} |`;}),
  '', 'Les plans ordinaires sont des possibilités d’adaptation ; implemented-stylized signale un générateur Blender original réellement affecté, avec ses limites restantes. Exemples : Servitor et rig servitor pour les composants de Raneiks ; quatre bras/Exo pour Atraks/Puppeteer ; blocs/écrans Bray pour Crypt Security ; conventions Vex pour Hydres/Harpies/Wyvernes avec deux silhouettes originales implémentées pour Athéon et le Templier seulement. Kerrev est un Tisseur, Harrow un Gladiateur Cabal et Dredgen Sere un Humain d’après leurs infobox : ils ne sont pas tous affectés au même personnage. Riven et le Témoin n’ont pas de template adapté ; les apparences unknown ne peuvent pas servir de modèle.',
  '', 'Chaque profil indique fichiers/symboles existants, familles, modules, templates, rigs, composants réutilisables, travaux requis et limites. Chaque plan indique silhouette attribuée, sources et statut. Les recettes historiques exactes (baseEnvironment et modules, y compris overrides) sont capturées depuis le vrai atlasRecipe et comparées au moteur existant. Les nouveaux lieux n’inventent pas d’AtlasReference directement résoluble. Les détails sont dans catalog.json (reuseProfiles / assetReusePlans), vérifiés hors ligne ; Athéon et le Templier ont un blenderAssetId dédié ; les autres boss et toutes les formes restent placeholders. Les plans décrivent les besoins d’adaptation ; la disponibilité effective est indiquée par le blenderAssetId et son registre.',
  '', '## Environnements réutilisés','',
  '| Lieu / variante | Famille / profil | Référence existante | Recette historique exacte | Fidélité |','| --- | --- | --- | --- | --- |',
  ...[...c.locations,...c.locationVariants].map(l=>`| ${l.id} | ${l.environmentFamily} / ${c.assetReusePlans.find(p=>p.entityId===l.id)?.profileIds.join(', ')} | ${l.remotionAssetId??'aucune'}${l.blenderAssetId?' ; '+l.blenderAssetId:''} | ${c.assetReusePlans.find(p=>p.entityId===l.id)?.existingRecipe?'oui':l.blenderAssetId?'non — générateur Blender séparé':'non — famille candidate seulement'} | ${l.visualStatus} |`),
  '', 'Le décor dédié existant est une évocation voxel, pas une carte exacte. Les autres arènes partagent les recettes de famille. Aucun fichier propriétaire ni transfert complet de géométrie historique. Riis reste inchangé ; Vénus, le Puits du Templier et le Trône de verre ont des générateurs séparés et deux rigs dédiés. La refonte 0.9.1 conserve les IDs et ajoute anatomie détaillée, IK et LOD indépendants de la résolution. Voir blender/cinematic_vex/README.md et docs/previews/cinematic-vex-0.9.1 pour les comparatifs et limites.',
  '', '## Corrections sourcées sans migration du catalogue historique','',
  ...c.legacyCorrections.map(r=>`- ${r.locationId} : ${r.field} = ${r.originalValue} dans le catalogue historique, ${r.correctedValue} dans universal. ${r.note} Sources : ${r.sources.map(linkSource).join('; ')}.`),
  '', 'Pour Equilibrium, les objectifs/transcript placent Harrow sur Imperium Carrier puis Sere dans Malphas Contemptus ; une phrase du walkthrough mélange l’ordre d’embarquement. Le désaccord est conservé dans la revue plutôt que masqué. Les noms français non vérifiés restent untranslated ; aucune traduction officielle n’est inventée.',
  '', '## Provenance et sources vérifiables','',
  `${stats.pinnedRevisions} révisions MediaWiki inspectées sont épinglées par oldid, titre et SHA-256 du wikitext ; ${stats.retrievedSources} références sont marquées retrieved au total et ${stats.inheritedSources} références restent inherited-not-rechecked. Les sources primaires de noms/disponibilité restent prioritaires. Le texte intégral des guides et les fichiers de modèles externes ne sont pas embarqués.`,
  '', 'Source-evidence.json conserve les inventaires primaires, les ensembles exacts d’étapes/boss relus par activité, les sources, les statuts et les lacunes ; retrievals permet de retrouver chaque révision consultée. Les tests comparent ces ensembles au catalogue. Une source secondaire avec une section partielle (notamment Epic) ne reçoit pas artificiellement un statut complet.',
  '', '## Lacunes maintenues','',...c.knownGaps.map(g=>'- '+g),
  '', '## Vérification et indépendance','',
  'Depuis remotion/ : `npm run test:atlas:universal`, `npm run typecheck:atlas:universal`, `npm run audit:assets -- --check`, `npm run report:atlas:coverage -- --check`. Voir atlas/universal/VALIDATION.md pour les commandes réellement exécutées. Les contrôles n’ont pas besoin du réseau.',
  '', 'Chantier v1.0 basé sur la refonte validée de PR #21 ; PR #17, #19, #20 et #21 restent indépendantes. Les anciens épisodes, le moteur vidéo, les assets existants et la PR #17 restent inchangés ; aucune fusion automatique. Les anciens IDs de la fondation sont conservés et testés. Le registre additionnel conserve les boss manquants et les formes séparées ; dix études de familles ne valident pas leurs arènes nommées. Voir docs/universal-library/WORKSTREAM.md ; aucun rendu de 35 secondes.', '',
 ].join('\n');
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
 for(const [file,text]of [['docs/ATLAS-COVERAGE.md',coverageMarkdown()],['remotion/atlas/universal/coverage.json',JSON.stringify(coverage(),null,2)+'\n']]) {const path=resolve(ROOT,file);if(process.argv.includes('--check')){if(readFileSync(path,'utf8')!==text)throw Error('Coverage report stale: '+file);}else writeFileSync(path,text);}
 console.log(JSON.stringify({activities:c.activities.length,encounters:c.encounters.length,bosses:c.bosses.length,forms:c.bossVariants.length,reusePlans:c.assetReusePlans.length,pinnedSources:proof.retrievals.length}));
}
