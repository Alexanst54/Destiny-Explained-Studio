# Atlas universel : contrat documentaire 0.9.0

Première étape de l’[issue #18](https://github.com/Alexanst54/Destiny-Explained-Studio/issues/18). Le catalogue 0.3, les épisodes et le moteur restent inchangés. `0.9.0` est la version de cette couche documentaire séparée, **pas une nouvelle version imposée aux épisodes**.

- [Audit des assets](../../../docs/ASSET-AUDIT.md), produit par `scripts/asset-audit.mjs` ; le JSON inclut les empreintes des 136 entrées suivies et les usages explicites dans 12 épisodes.
- [Couverture sourcée](../../../docs/ATLAS-COVERAGE.md), produite par `scripts/atlas-coverage.mjs` ; les lacunes restent visibles.
- `schema.ts` : tables strictes et intégrité relationnelle.
- `index.ts` : validation, listes de sources et API de lecture, **aucun branchement automatique dans l’éditeur ou Remotion**.
- `catalog.json` : catalogue étendu des rencontres, avec références aux assets procéduraux existants ; les 468 lieux historiques restent dans leur catalogue d’origine.
- `source-evidence.json` : listes Bungie normalisées, ensembles de rencontres relus et 186 révisions wiki épinglées (URL, numéro de révision et empreinte du texte consulté).
- `audit-context.json` : branche initialement observée et base main, afin de ne pas incorporer la PR #17.

## Tables et relations

| Table | Rôle |
| --- | --- |
| locations | Lieux, sous-zones, dimensions, vaisseaux, arènes ; parentId uniquement entre lieux |
| locationVariants | Variante historique, locationId ; legacyVariantId préserve l’ID local 0.3 |
| activities | Raids D1/D2 séparés, donjons, assauts, missions exotiques/campagne et activités saisonnières |
| encounters | Étape ordonnée d’une activité ; type combat/mechanic/traversal, objectif éditorial signalé |
| bosses | Identité distincte du lieu et de l’activité ; characterId optionnel, vérifié contre le registre existant |
| bossVariants | Forme/transformation reliée à une identité ; exemple Taniks Reborn/Abomination |
| activityLocations | Activité ↔ lieux, plusieurs-à-plusieurs, rôle et source |
| encounterLocations | Rencontre ↔ arènes, plusieurs-à-plusieurs ; lieu déjà sourcé pour l’activité |
| encounterBosses | Rencontre ↔ boss + variante facultative, rôle primary/secondary/pursuer |
| activityRelations | Reprise D2 → D1 ou variante d’activité ; cycles interdits |
| sources | URL HTTPS, section, date, statut retrieved/inherited et capacités documentaires |
| assets | Pointeurs vers fonctions/modèles existants, moteur, famille, fidélité et restrictions de lieu/variante |

Les entités portent `game` (D1/D2/both), `type`, `enName`, `frName`, statut de traduction, alias, `expansion`, `firstSeen`, `appearanceEvidence`, `canonStatus`, `visualStatus`, disponibilité datée, sources et pointeurs d’assets. `parentId` est réservé à la hiérarchie des lieux : une rencontre appartient à `activityId`, une forme à `bossId`. Les liens d’activité et de boss ne sont jamais déduits d’une proximité de noms.

`availabilityEvidence.asOf` date l’état attesté, tandis que `sources.checkedAt` date la consultation. Les retraits An 4 sont datés du 10 novembre 2020 ; ne pas les présenter comme une nouvelle mesure de disponibilité en 2026.

`firstSeen=null` signifie non vérifié ; une association à une extension ne prouve pas la première apparition. Les dates exactes ne sont renseignées que lorsque consultées. `expansion` est une ère de sortie, pas une exigence de possession. Les sites historiques qui portent un nom d’activité conservent leur ID comme lieu documentaire et sont reliés à de nouvelles activités `activity-…-d1/d2`. Aucune ancienne référence n’est renommée.

`visualStatus=dedicated` décrit une réalisation stylisée existante, pas une carte officielle. `modular-reconstruction` réutilise une famille, pas un nouveau modèle individuel. `placeholder` ne peut déclarer d’asset implémenté. Les boss absents du registre restent placeholders ; un Vex générique ne devient pas Atheon par renommage. Les arènes nommées dans les sources utilisent les familles existantes sans prétendre à leur géométrie exacte.

## Recensement des rencontres et réemploi

Les 19 raids de base (éditions D1/D2 séparées) et les 11 donjons ont leurs rencontres principales relues. Le catalogue compte 213 étapes, 128 entrées de boss (dont collectifs et mécanismes), 25 formes, huit éditions d’assauts et neuf éditions de missions exotiques. Les routes d’assauts/missions, variantes, modes et certains noms d’arènes restent partiels ; l’édition Epic du Désert perpétuel est recensée séparément. La Ménagerie reste à commencer.

`category` distingue rencontres principales, traversées et étapes optionnelles ; `conditions` conserve les catalyseurs, quêtes et Rite of Nine. `encounterOrdering` distingue ordre fixe, rotation hebdomadaire et sélection libre. Les relations portent leur issue (`cleanse`, `repel`, `escape`, etc.) : rencontrer un boss ne prouve pas sa mort. `composition`/`members` distinguent collectifs et individus, `nature` distingue formes, automates, projections et configurations de combat.

Les 314 `assetReusePlans` couvrent chaque boss, forme, lieu et variante de lieu. Ils pointent vers 52 `reuseProfiles` : familles, modules, personnages candidats, rigs et fonctions réellement présents, parties réutilisables, adaptations et limites. Les recettes `existingRecipe` des références historiques sont vérifiées contre `atlasRecipe` ; les nouvelles arènes n’en inventent aucune. Ces plans ne sont pas des affectations de modèles. Tous les boss restent placeholders et aucune nouvelle géométrie Blender n’est créée.

`activityReviews` conserve les ensembles exacts de rencontres et boss relus, avec des axes distincts rencontres/boss/arènes/variantes et des lacunes obligatoires. `retrievals` permet de retrouver les versions wiki inspectées sans télécharger leur contenu pendant les tests. `foundation-ids.json` protège les IDs de la première livraison. La correction sourcée du parent du Désert perpétuel (Périphérie inconnue, au lieu de Kepler) est inscrite dans `legacyCorrections` pour cette couche uniquement ; le catalogue historique reste intact.

## Extension et compatibilité

Pour une prochaine tranche : ajouter une source inspectée, conserver les IDs existants, ajouter des fiches et relations vérifiables, conserver les incertitudes et regénérer les rapports. `validateUniversalCatalog` vérifie les liens et IDs historiques, les sources héritées et les releases. `validateAssetFiles` vérifie les chemins/symboles/sélecteurs réels et l’empreinte du catalogue 0.3. Un changement intentionnel de ce catalogue demandera une nouvelle revue et une empreinte mise à jour, jamais une substitution silencieuse.

Le moteur historique continue d’utiliser `atlas/index.ts`, pas cette nouvelle entrée. Les fixtures d’épisodes vont de 0.1.0-draft à 0.7.0 ; le pipeline Blender 0.8 utilise des snapshots de format v1 et ne définit pas un tag d’épisode 0.8. Aucun changement à `AtlasReference`, aux formats historiques, aux timelines, à Kokoro, aux captions, aux schémas Blender ou au bundle de l’éditeur. Les tests parse/round-trip couvrent les anciennes fixtures. L’import incrémental avec dédoublonnage et les filtres éditeur sont des étapes suivantes.

Les vérifications demandent un checkout Git et fonctionnent hors ligne. L’observation initiale de PR #17 est conservée dans audit-context.json ; sa branche et ses objets Git ne sont pas nécessaires pour régénérer les rapports. Les téléchargements de manifests, rendu GPU, Colab/Android et modèles Blender paramétriques généraux ne sont pas prétendus réalisés. Les fonctions de la PR #17 ne sont ni copiées ni requises. Aucun rendu intégral ni fusion automatique.
