# Validation de la première étape #18

Vérifications exécutées le 9 novembre 2026. Node **22.23.4** installé depuis l’archive officielle et son SHA-256 publié ; Python **3.12.14**. Le détail, les commandes et les empreintes des entrées validées sont dans [validation.json](validation.json).

| Vérification exécutée | Résultat |
| --- | --- |
| Tests Node — nouveau schéma/API/audit et suites Atlas/library/living/animation/hybrid/polish/Blender/editor existantes | 81 passés, 0 échec |
| Tests Python Blender historiques | 12 passés |
| Import de manifest hors ligne | 4 passés |
| TypeScript historique et configuration dédiée universal | Passé |
| Régénération exacte ASSET-AUDIT, ATLAS-COVERAGE et JSON associés | Passée |
| Rapport historique Atlas 0.3 et bundle statique éditeur | Inchangés, vérifications passées |
| Clone superficiel de la seule nouvelle branche, sans objets Git de PR #17 | Audit et couverture régénérés au checkpoint 3a49b50 |
| Diff des fichiers existants vs main | Seul package.json reçoit quatre commandes npm supplémentaires |

Les 10 nouveaux tests couvrent notamment les listes Bungie par ensemble d’IDs, les doublons, dates et sources, les parents/cycles, les liens de jeu, les arènes par activité, les variantes de boss appartenant à la bonne identité, les reprises D1/D2, les cycles à embranchements, les chemins/symboles/sélecteurs d’assets et les restrictions du générateur Riis. Les 12 épisodes historiques passent le schéma ; leur copie de rendu par l’éditeur conserve tous leurs champs, et leurs empreintes restent identiques.

Les documents générés déclarent explicitement la couverture partielle et les références héritées non re-téléchargées. Les 11 donjons correspondent à la liste primaire consultée ; aucune règle globale « toujours 11 » n’est imposée au schéma. Les modes de difficulté (dont la variante Epic du Désert perpétuel mentionnée par Bungie) demandent une tranche ultérieure ; ils ne sont pas comptés comme nouveaux raids de base.

Cette validation ne prétend pas avoir créé des assets de boss ni transféré toute la géométrie voxel dans Blender. Aucun rendu, aucune migration d’épisode, aucune édition du bundle UI, aucun téléchargement de modèle 3D, aucun rendu de 35 secondes. La PR #17 reste indépendante ; rien n’a été fusionné.

Commandes courtes depuis `remotion/` :

```sh
npm run test:atlas:universal
npm run typecheck:atlas:universal
npm run typecheck
npm run audit:assets -- --check
npm run report:atlas:coverage -- --check
node --experimental-strip-types scripts/atlas-report.mjs --check
node scripts/build-editor.mjs --check
python -m unittest discover -s blender/tests
python -m unittest discover -s tests -p 'test_manifest_import.py'
```

La commande complète des 81 tests Node est conservée dans le JSON. Aucun service externe n’est nécessaire pour les tests de catalogue ; les URLs des sources ont été lues pendant la revue initiale, pas téléchargées automatiquement par les tests.
