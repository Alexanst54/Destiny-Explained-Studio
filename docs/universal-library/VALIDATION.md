# Validation du checkpoint v1.0 — bibliothèque encore incomplète

Node 22.23.4, Python 3.12.14, Blender officiel 4.3.2 (32f5fdce0a0a). CPU AMD EPYC 9V74, trois threads par rendu ; pas de GPU.

| Vérification locale | Résultat |
| --- | --- |
| Suites Node universal, sélection, bibliothèque et historiques | 102 passés, 0 échec |
| Python Blender historiques et bibliothèque | 43 passés |
| Import de manifest | 4 passés |
| TypeScript historique et universal | Passés |
| Chromium mobile simulé, 412×915 | Filtres, variantes, images, JSON, absence de débordement/erreurs |
| Blender natif Vex | 136 + 156 évaluations passées |
| Blender natif Cropta | 192 évaluations passées ; appuis physiques non validés |
| Cache et reprise sur Blender réel | Hits, seed différent refusé, verrou, design et PNG corrompus récupérés |
| Conservation historique | 136 fichiers et 12 épisodes inchangés ; anciennes preuves vérifiées |

Les [résultats structurés](validation.json), [métriques natives](native-checks.json) et [résultats de reprise](reliability/result.json) conservent les limites. Le test d’interruption forcée du lot A reste enregistré au checkpoint e3a7e2c : SIGKILL après une frame, puis 1 hit / 3 nouveaux rendus. La reprise finale complète ces vérifications avec la cache de design JSON et le verrou de writer.

Les dix études de familles restent partielles. Les deux modèles Vex validés sont inchangés et possèdent une grille de validation technique. Cropta possède une grille réelle, mais reste un prototype artistique partiel ; les autres boss ne sont pas déclarés réalisés. Les fixes et clips sont des sorties Blender réelles, vérifiées par empreintes, décodage, dimensions, géométrie, caméras et ffprobe. Les clips sont muets ; aucun épisode, audio Kokoro ou sous-titre n’est modifié.

```sh
python -m unittest discover -s remotion/blender/tests
python -m unittest discover -s remotion/tests -p test_manifest_import.py
node --test remotion/tests/universal-library.test.mjs
python remotion/blender/universal/build_index.py --check
python remotion/blender/universal/verify_media.py
python remotion/blender/universal/verify_crota.py
python remotion/blender/universal/approved_gallery.py --check
python remotion/blender/cinematic_vex/verify_evidence.py
python remotion/blender/venus_vault/verify_evidence.py
node editor/universal-library.browser.test.cjs
```

Le test navigateur exige un serveur du dépôt sur 8000 et Chromium ; ses captures locales sont des contrôles d’interface, pas des rendus 3D. La suite Node complète est celle du checkpoint 0.9.1, augmentée de `tests/universal-library.test.mjs` (six tests) : les 102 tests ne sont pas une affirmation d’exécution de tous les tests possibles du dépôt. Les contrôles natifs exigent Blender, voir le guide.

Le workflow GitHub Actions additionnel vérifie les tests purs, l’index généré et les médias livrés ; il ne génère pas de nouvelles images, ne teste aucun GPU et ne fusionne rien. Les résultats CI sont consultables sur la PR. La syntaxe des cellules du nouveau notebook est compilée localement ; Colab, T4 et Android restent non testés. Les mesures de temps peuvent inclure une contention CPU et ne constituent pas un benchmark comparatif contrôlé.
