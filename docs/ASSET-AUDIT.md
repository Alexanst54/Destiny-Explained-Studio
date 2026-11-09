# Audit des assets — première étape de l’issue #18

Audit du 2026-11-09. Branche observée au départ : `feat/gpu-render-optimization-0.8.4` (`146d43e`, PR #17). Implémentation indépendante depuis `main` (`1effd88`). Aucun asset existant supprimé ou remplacé.

## Méthode et preuve reproductible

Exécuter depuis `remotion/` : `npm run audit:assets` ; vérifier sans réécriture : `npm run audit:assets -- --check`. [asset-audit.json](../remotion/atlas/universal/asset-audit.json) contient chemins, tailles, SHA-256 et références par épisode. Les schémas historiques sont exécutés. L’audit fonctionne hors ligne.

L’inventaire porte sur **136 fichiers suivis**, **12 épisodes JSON**, les catalogues, moteurs, bridges et assets compilés. Les médias Kokoro et caches ignorés ne sont pas des fichiers d’assets versionnés ; les références à générer sont signalées séparément. Un fichier présent ou une référence textuelle ne démontre pas son rendu ni sa fidélité canonique.

## Inventaire réel

| Élément | Présent | Interprétation |
| --- | ---: | --- |
| Lieux Atlas 0.3 | 468 | IDs et catalogue conservés intégralement |
| Variantes historiques imbriquées | 17 | IDs locaux conservés ; pas des modèles uniques |
| Décors dédiés stylisés | 4 | Bibliothèque voxel existante, pas des cartes officielles exactes |
| Lieux en reconstruction modulaire | 464 | Recettes partagées, pas 464 assets distincts |
| Familles / modules | 14 / 16 | Réutilisables dans Remotion |
| Personnages / variantes | 33 / 41 | Silhouettes partagées ; une apparence inconnue reste inconnue |
| Archétypes de rig / animations 0.7 | 8 / 16 | Fonctions déterministes existantes |
| Modèles .blend/.glb/.gltf/.fbx/.obj/.usd/.usdz versionnés | 0 | Bibliothèque actuelle procédurale, pas collection Blender native |

### Décors à réutiliser

| Lieu Atlas | Modèle / bibliothèque existante | Compatibilité Blender actuelle |
| --- | --- | --- |
| europa | voxel-europa-v1 — VoxelEnvironment | Export de scène limité ; géométrie complète de ce décor non transférée |
| europan-pyramid | voxel-pyramid-v1 — VoxelEnvironment | Export de scène limité ; géométrie complète de ce décor non transférée |
| black-garden | voxel-black-garden-v1 — VoxelEnvironment | Export de scène limité ; géométrie complète de ce décor non transférée |
| tower | voxel-tower-v1 — VoxelEnvironment | Export de scène limité ; géométrie complète de ce décor non transférée |

Les recettes sont dans `remotion/atlas/recipes.ts`, les 16 modules dans `geometry.ts`, les décors dans `src/voxel/library/Library.tsx` et `layout.ts`. Réutiliser ces familles pour Vénus/Caveau de verre, Mars et Lune/Cropta ; aucun nouveau décor fidèle n’est annoncé dans cette PR.

### Personnages, animation et composition

Styles utilisés par le registre : beast (1), drone (2), four-arm (6), heavy (3), hive (2), humanoid (11), krill (4), sphere (1), terminal (1), unknown (1), vex (1). Le style unknown est un marqueur, pas une apparence attestée. Rigs : humanoid, four-arm, dreg, vandal, captain, servitor, civilian, elder.

Réutiliser `characters/models/VoxelCharacter.tsx`, `living/` (cast/groupes), `animation/rig.ts`, `director.ts` et `camera.ts`, `polish/` (variation, environnement, caméra) et `hybrid/` (composition, sources, audio/captions). Une silhouette générique n’est pas un modèle de boss validé. Les neuf boss recensés dans cette tranche n’ont pas de modèle dédié assigné.

## Références réellement utilisées et manquantes

Les 12 épisodes suivis passent le schéma historique : 0.1.0-draft (3), 0.3.0 (1), 0.4.0 (3), 0.5.0 (3), 0.6.0 (1), 0.7.0 (1). Le JSON de chaque épisode est empreinté ; aucune timeline, voix ou caption n’est modifiée.

Références explicites dans ces fixtures : **5 lieux Atlas**, **8 personnages**, **4 décors** ; références catalogue inconnues : **0**. Détails fichier par fichier dans le JSON.

**463 lieux** et **25 personnages** n’ont pas de référence explicite dans ces épisodes. Cela ne prouve pas qu’ils sont inutilisés : l’éditeur et les sélections dynamiques peuvent les utiliser. Aucun nettoyage n’est proposé.

Assets de boss absents dans le nouveau registre : boss-templar, boss-atheon, boss-ir-yut, boss-crota, boss-crypt-security, boss-atraks, boss-taniks, boss-vorgeth, boss-dul-incaru. Ce sont des placeholders documentaires. Les arènes nouvellement nommées réutilisent des familles modulaires ; aucun modèle spécifique n’a été construit.

## Compatibilité Blender : limites constatées dans le code

- `blender/export.ts` exporte des primitives box/sphere et matrices de rigs 0.7 pour les plans voxel dirigés. Les Guardian/Ghost historiques et acteurs actifs sans rig sont rejetés explicitement ; aucun acteur n’est silencieusement supprimé.
- Le bridge n’exporte pas les `atlasBoxes` complets ni les décors dédiés : scène de base simplifiée, blocs polish, props terminal et rigs. La présence d’un lieu dans le catalogue ne prouve pas sa géométrie Blender.
- Sky gradient, brouillard, particules, decals, weather geometry et éléments voxel historiques ne sont pas transférés intégralement. Les omissions sont déclarées dans les snapshots. Kokoro, captions, labels et montage restent dans Remotion.
- `blender/environments/riis.py::generate` est un générateur réutilisable existant, limité à `riis/before-whirlwind`. Il utilise les primitives, matériaux, profils et haze existants ; ce n’est ni un fichier .blend ni un générateur universel Vex/Ruche/Cabal.
- Les exemples de snapshots, contrats TS/Python, importeur et deux notebooks existants sont conservés. Aucun test de rendu GPU/Colab/Android n’est ajouté ou revendiqué par cet audit statique.

## Branche initiale et indépendance de la PR #17

Les 6 entrées de catalogue/géométrie/export comparées sont identiques entre main et la branche initiale : **oui**. Les différences de PR #17 sont consignées, sans les importer.

PR #17 ajoute notamment le worker Blender persistant, CUDA/telemetry, les tests de reprise et la preuve MP4. Ces changements ne sont pas sur main. Cette fondation ne les recopie pas, ne les fusionne pas et ne dépend pas de leur exécution. La prise en charge GPU persistante reste un travail indépendant.

## Adaptations suivantes, après cette première étape

1. Relire et compléter les relations et la provenance ; dédoublonner par IDs stables, sans supprimer les fiches historiques homonymes.
2. Adapter les primitives et familles existantes pour les pilotes Vénus/Caveau, Mars et Lune/Cropta ; documenter les écarts visuels avant tout asset dédié.
3. Ajouter l’import incrémental puis les filtres éditeur ; conserver le contrat d’épisode et les timelines existants.

Voir [ATLAS-COVERAGE.md](ATLAS-COVERAGE.md) pour les sources, relations et lacunes de cette tranche. Aucun rendu intégral de 35 secondes ni remplacement destructif.
