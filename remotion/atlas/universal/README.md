# Atlas universel : contrat documentaire 0.9.0

Première étape de l’[issue #18](https://github.com/Alexanst54/Destiny-Explained-Studio/issues/18). Le catalogue 0.3, les épisodes et le moteur restent inchangés. `0.9.0` est la version de cette couche documentaire séparée, **pas une nouvelle version imposée aux épisodes**.

- [Audit des assets](../../../docs/ASSET-AUDIT.md), produit par `scripts/asset-audit.mjs` ; le JSON inclut les empreintes des 136 entrées suivies et les usages explicites dans 12 épisodes.
- [Couverture sourcée](../../../docs/ATLAS-COVERAGE.md), produite par `scripts/atlas-coverage.mjs` ; les lacunes restent visibles.
- `schema.ts` : tables strictes et intégrité relationnelle.
- `index.ts` : validation, listes de sources et API de lecture, **aucun branchement automatique dans l’éditeur ou Remotion**.
- `catalog.json` : première tranche, avec références aux assets procéduraux existants ; les 468 lieux historiques restent dans leur catalogue d’origine.
- `source-evidence.json` : listes Bungie normalisées et notes de revue des rencontres.
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

`firstSeen=null` signifie non vérifié ; une association à une extension ne prouve pas la première apparition. Les dates exactes ne sont renseignées que lorsque consultées. `expansion` est une ère de sortie, pas une exigence de possession. Les sites historiques qui portent un nom d’activité conservent leur ID comme lieu documentaire et sont reliés à de nouvelles activités `activity-…-d1/d2`. Aucune ancienne référence n’est renommée.

`visualStatus=dedicated` décrit une réalisation stylisée existante, pas une carte officielle. `modular-reconstruction` réutilise une famille, pas un nouveau modèle individuel. `placeholder` ne peut déclarer d’asset implémenté. Les boss absents du registre restent placeholders ; un Vex générique ne devient pas Atheon par renommage. Les arènes nommées dans les sources utilisent les familles existantes sans prétendre à leur géométrie exacte.

## Extension et compatibilité

Pour une prochaine tranche : ajouter une source inspectée, conserver les IDs existants, ajouter des fiches et relations vérifiables, conserver les incertitudes et regénérer les rapports. `validateUniversalCatalog` vérifie les liens et IDs historiques, les sources héritées et les releases. `validateAssetFiles` vérifie les chemins/symboles/sélecteurs réels et l’empreinte du catalogue 0.3. Un changement intentionnel de ce catalogue demandera une nouvelle revue et une empreinte mise à jour, jamais une substitution silencieuse.

Le moteur historique continue d’utiliser `atlas/index.ts`, pas cette nouvelle entrée. Aucun changement à `AtlasReference`, aux formats JSON 0.3–0.8, aux timelines, à Kokoro, aux captions, aux schémas Blender ou au bundle de l’éditeur. Les tests parse/round-trip couvrent les anciennes fixtures. L’import incrémental avec dédoublonnage et les filtres éditeur sont des étapes suivantes.

Les vérifications sont hors ligne. Les téléchargements de manifests, rendu GPU, Colab/Android et modèles Blender paramétriques généraux ne sont pas prétendus réalisés. Les fonctions de la PR #17 ne sont ni copiées ni requises. Aucun rendu intégral ni fusion automatique.
