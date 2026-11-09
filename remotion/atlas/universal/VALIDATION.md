# Validation de l’Atlas et de l’extension Vénus/Caveau

Vérifications exécutées le 9 novembre 2026. Node **22.23.4** installé depuis l’archive officielle et son SHA-256 publié ; Python **3.12.14**. Le détail, les commandes et les empreintes des entrées validées sont dans [validation.json](validation.json).

| Vérification exécutée | Résultat |
| --- | --- |
| Tests Node — nouveau schéma/API/audit et suites Atlas/library/living/animation/hybrid/polish/Blender/editor existantes | 96 passés, 0 échec |
| Tests Python Blender historiques + extension | 29 passés |
| Import de manifest hors ligne | 4 passés |
| TypeScript historique et configuration dédiée universal | Passé |
| Régénération exacte ASSET-AUDIT, ATLAS-COVERAGE et JSON associés | Passée |
| Rapport historique Atlas 0.3 et bundle statique éditeur | Inchangés, vérifications passées |
| Clone superficiel de la seule nouvelle branche, sans objets Git de PR #17 | Audit et couverture régénérés au checkpoint 3a49b50 |
| Compatibilité depuis la branche PR #19 à eb6c4de | 136 entrées historiques et 12 épisodes inchangés ; aucun commit de PR #17 |

Les 19 tests universal et les six tests de sélection Blender couvrent notamment les listes Bungie par ensemble d’IDs, les doublons, dates et sources, les parents/cycles, les liens de jeu, les arènes par activité, les variantes de boss appartenant à la bonne identité, les reprises D1/D2, les cycles à embranchements, les chemins/symboles/sélecteurs d’assets et les restrictions du générateur Riis. Les 12 épisodes historiques passent le schéma ; leur copie de rendu par l’éditeur conserve tous leurs champs, et leurs empreintes restent identiques.

Les contrôles supplémentaires protègent les ensembles relus des 19 raids de base et des 11 donjons, les étapes conditionnelles, les membres de collectifs, les issues sans mort, les révisions wiki épinglées, les 314 plans de réemploi et leurs composants, les recettes historiques exactes et les IDs de la livraison initiale. Les autres boss restent placeholders ; seuls les deux plans dédiés d’Athéon et du Templier sont implémentés.

Les documents générés déclarent explicitement la couverture partielle et les références héritées non re-téléchargées. Les 11 donjons correspondent à la liste primaire consultée ; aucune règle globale « toujours 11 » n’est imposée au schéma. L’édition Epic du Désert perpétuel est recensée séparément et reste partielle ; les modes et variantes ne sont pas exhaustifs et ne sont pas comptés comme nouveaux raids de base.

L’extension Vénus/Caveau ajoute trois décors et deux modèles de boss originaux, validés par de vrais rendus CPU ; voir [la validation visuelle](../../blender/venus_vault/VALIDATION.md). Elle ne transfère pas toute la géométrie historique. Aucune migration d’épisode, aucune édition du bundle UI, aucun téléchargement de modèle du jeu et aucun rendu de 35 secondes. La PR #17 reste indépendante ; rien n’a été fusionné.

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

La commande complète des 96 tests Node est conservée dans le JSON. Aucun service externe n’est nécessaire pour les tests de catalogue ; les URLs des sources ont été lues pendant la revue initiale, pas téléchargées automatiquement par les tests.

Les nouveaux tests Python portent sur la génération indépendante de l’état aléatoire global, la variation par graine, la hiérarchie et les composants des boss, les animations sans dérive, les chemins caméra et les requêtes bornées. Une exécution réelle de Blender vérifie 156 poses/projections et la stabilité des ressources entre images. Les médias livrés sont vérifiés par `python remotion/blender/venus_vault/verify_evidence.py` depuis la racine.

## Refonte 0.9.1

Six paires Cinematic et deux clips Balanced réellement rendus sur CPU sont livrés dans [la galerie](../../../docs/previews/cinematic-vex-0.9.1/README.md). Le contrôle natif supplémentaire vérifie 136 évaluations, les cibles IK, les caméras, l’accès hors ordre et le partage des meshes. Les 96 tests Node et 33 tests Python passent. [Mesures, commandes et limites](../../blender/cinematic_vex/VALIDATION.md). La vérification de clone superficiel ci-dessus reste une observation historique de la fondation ; elle n’a pas été répétée pour 0.9.1.
