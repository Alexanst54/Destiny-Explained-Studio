# Universal cinematic library — API additionnelle v1.0

[Programme et couverture réelle](../../../docs/universal-library/README.md). Athéon et le Templier utilisent directement leur renderer 0.9.1 inchangé. Les familles sont des études procédurales explicites ; un boss manquant provoque une erreur. Les formes ne récupèrent jamais automatiquement le modèle parent.

```sh
python remotion/blender/render_universal.py --index
python remotion/blender/render_universal.py boss-atheon --check-only --view front
python remotion/blender/render_universal.py boss-atheon work/library-atheon --lod 0 --quality balanced --view three-quarter --frames 24 --fps 24 --video
python remotion/blender/render_universal.py boss-templar work/library-templar --view silhouette --quality cinematic
python remotion/blender/render_universal.py oversoul-throne work/hive-study --family-study --family hive --lod 0 --quality draft --width 480 --height 360
```

Les commandes de rendu acceptent `--blender /chemin/blender`, `--device auto|cpu`, `--threads 3`, `--timeout 1800`. Blender officiel 4.3.2 avec Cycles/OIDN recommandé ; ffmpeg nécessaire seulement pour `--video`. Aucun GPU imposé. Auto réutilise la détection existante OPTIX/CUDA et le repli CPU ; le rapport conserve le backend effectif, y compris une éventuelle nouvelle tentative CPU après échec GPU. Pas de code ni commit importé de PR #17.

## Cache et reprise

Relancer exactement la même commande avec `--resume`. Le cache lie la requête, les sources, la version Blender, le choix device et les threads. Un changement exige un autre dossier. Les PNG sont contrôlés par SHA-256, CRC, dimensions et décompression des scanlines RGB avant réemploi. Une frame corrompue est recalculée seule. Les écritures PNG et progression deviennent visibles après remplacement atomique. Un verrou empêche deux writers simultanés. Les logs de chaque tentative restent distincts. Timeout/crash conservent les frames validées ; une interruption avant checkpoint rend seulement la frame en cours manquante.

Une scène Blender est construite une fois par invocation pour toutes les frames manquantes. Le cache de **design JSON** évite de recalculer les études de famille à la reprise. Pas de cache `.blend` entre sessions ; les ressources Blender doivent être reconstruites après un redémarrage. La mémoire reportée est le pic RSS du processus Linux ; la mémoire GPU et l’utilisation restent `null` tant que non mesurées. Les MP4 sont muets ; exporter une sélection n’affecte aucune timeline ni audio d’épisode.

## Familles et statut

`families.json` : dix familles, trois variantes chacune (`sanctum`, `causeway`, `courtyard`), modules de sol/colonnes/arche/plateforme/prop/atmosphère. Ce sont des candidats artistiques réutilisables, sans prétention de reproduire chaque destination. Plusieurs familles peuvent correspondre à un lieu ; `--family` tranche explicitement l’ambiguïté. Les familles non couvertes restent non résolues. Les matériaux partagés et lots statiques réemploient `Design` et `compile_design` existants. Les trois LOD concernent la géométrie ; résolution et qualité ne choisissent jamais silencieusement un autre LOD.

`models.json` enregistre seulement les vrais providers disponibles. Le statut de géométrie et celui de galerie sont séparés. Ne pas modifier le statut Atlas d’un boss uniquement parce qu’un plan de réemploi ou une étude de famille existe. `registry.index()` conserve composition, membres, formes, nature des projections, liens conditionnels et sources.

```sh
python remotion/blender/universal/build_index.py
python remotion/blender/universal/build_index.py --check
python -m unittest discover -s remotion/blender/tests -p test_universal_library.py
node --test remotion/tests/universal-library.test.mjs
```

## Colab Pro / T4

Le notebook [Cinematic-Vex-Colab-Pro.ipynb](../Cinematic-Vex-Colab-Pro.ipynb) garde son workflow historique. Pour cette bibliothèque : cloner la branche `feat/universal-cinematic-library-1.0`, installer Blender officiel 4.3.2 vérifié comme dans ce notebook, puis exécuter les commandes ci-dessus avec `--blender` pointant sur ce binaire. Sur une session T4 : lancer d’abord une seule frame Draft, vérifier `configuration.selected`, `backend`, `devices`, puis un clip court Balanced. Sauvegarder le dossier de sortie dans Drive et reprendre avec la même commande et `--resume`. Vérifier que les PNG sont intègres et que le nombre de cache hits correspond aux frames achevées. Ne pas annoncer un gain GPU à partir des mesures CPU. Colab/T4/Android non exécutés dans cette livraison ; pas de rendu complet de 35 secondes.

## Lots suivants et grille automatique

Cropta et `oversoul-throne` sont enregistrés sur la branche `feat/library-crota-lot-b-1.0` comme prototypes dédiés partiels, pas comme modèles terminés. [Rendus et limites](../../../docs/universal-library/crota/README.md). Les autres boss manquants restent bloqués.

```sh
# Produit seulement le plan, sans rendre une bibliothèque entière implicitement.
python remotion/blender/universal/batch.py work/library-grid
# Inclut les prototypes, toujours avec leurs statuts partiels.
python remotion/blender/universal/batch.py work/library-grid --include-prototypes
# Lance les jobs préparés ; reprend leurs sorties compatibles.
python remotion/blender/universal/batch.py work/library-grid --include-prototypes --execute --blender /chemin/blender
```

La grille fixe est face/trois-quarts/silhouette/environnement en Cinematic, plus une seconde Balanced. Le plan conserve les identités/formes manquantes et leurs activités. Une réussite technique n’approuve ni la fidélité ni la qualité artistique et ne promeut pas automatiquement les statuts.

Le notebook additionnel [Universal-Library-Colab-Pro.ipynb](../Universal-Library-Colab-Pro.ipynb) clone la branche du lot B et expose les options par formulaire. Son code est compilé localement ; aucune exécution distante ni compatibilité Android réelle n’est revendiquée. Les notebooks précédents restent intacts.

Le catalogue documentaire Atlas conserve son statut placeholder pour Cropta : le registre de la bibliothèque expose un prototype expérimental séparé et ne promeut aucun statut Atlas sans validation spécifique. Les autres identités et toutes les formes non implémentées restent manquantes.
