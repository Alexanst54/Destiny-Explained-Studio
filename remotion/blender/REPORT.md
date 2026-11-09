# Blender Bridge 0.8.1 — validation et limites

Base main : `baf79ed8a32957ed2359334f376bbc89c46971ae`, fusion PR #13. Branche `feat/blender-bridge-0.8.1`. PR ouverte tôt en brouillon : https://github.com/Alexanst54/Destiny-Explained-Studio/pull/14 . [Journal de reprise et checkpoints](../../docs/BLENDER-BRIDGE-PROGRESS.md).

## Résultat opérationnel

Un projet voxel 0.7 est échantillonné à une frame donnée, validé en JSON versionné, importé dans Blender et rendu en PNG headless. Les poses/interactions/caméras viennent des fonctions existantes. L’exemple Riis contient six Éliksni, 176 primitives, un sol et un décor borné. Le projet original, les schémas 0.7, les modèles, l’éditeur et Remotion ne sont pas réécrits.

Contrat v1 / exporterVersion 0.8.1 ; matrices colonne majeure en Y-up, conversion Blender `(x,-z,y)`, préservation des cisaillements par sommets si nécessaire. La caméra conserve le FOV vertical. Les matériaux n’emploient aucune texture ni modèle externe. Les profils standard/cinematic règlent Cycles et gardent un repli CPU ; ils ne promettent pas la parité visuelle avec Three.js.

## Tests pertinents exécutés

- 4 tests Node bridge : version/JSON, immutabilité, export hors séquence, matrices des articulations sur cinq frames (tolérance 1e-9), refus explicite des acteurs/plans non pris en charge, validation Python et rejets des versions/matrices/références invalides.
- 14 tests 0.7 de rigs/animations/relations/cadrage repris, sans relancer les suites sans rapport avec le bridge : **18 tests Node réussis au total**.
- 3 tests Python : contrat, mauvais types/non-finis/singularités/hiérarchie, compilation AST de toutes les cellules du notebook et absence de sorties d’exécution enregistrées.
- TypeScript global et `editor:check` : réussis. Aucun changement de source/asset d’éditeur, aucune suite Chromium relancée.
- Test dans Blender 4.3.2 réel : 176 objets, toutes les matrices, axes, caméra et FOV, géométrie partagée, préservation des scènes déjà ouvertes, réglages des deux profils, sphère et cisaillement affine. Réussi sans rendu supplémentaire.

## PNG réellement rendus

Linux, Blender 4.3.2/Cycles CPU, 3 CPU logiques disponibles, 2 threads sélectionnés. Mesure Python `time.monotonic` autour du processus Blender, puis `resource.getrusage(RUSAGE_CHILDREN)` ; mémoire maximale RSS du processus enfant, **pas mémoire totale GPU/driver**.

| Profil | Image | Samples | Temps processus | RSS maximale | PNG |
| --- | --- | ---: | ---: | ---: | ---: |
| standard | 1080×1920 | 16 | 31,312 s | 390 620 Kio | 2 932 803 octets |
| cinematic | 270×480 (25 %) | 64 | 8,057 s | 273 188 Kio | 158 244 octets |

Ces tailles différentes interdisent une comparaison de débit entre profils. Les images sont locales sous `remotion/out/blender/`, ignorées par Git. Le PNG standard a été inspecté visuellement ; il est volontairement bruité à 16 samples. Le second PNG utilise le code final de préservation affine et le compteur Blender aligné sur la frame source. Le premier conserve les transformations figées de la frame 210 ; aucun shader/objet animé ne dépend de l’horloge Blender.

Le premier essai cinematic a échoué : OpenImageDenoise absent du build. Après analyse des propriétés Cycles installées (`_cycles.with_openimagedenoise`), le débruitage est devenu conditionnel et une seule relance miniature a réussi. Le rapport signale explicitement sa désactivation. Aucun GPU compatible détecté en mode auto : le second PNG valide le choix CPU automatique, **pas un rendu GPU** ni le chemin de récupération après panne GPU.

`/usr/bin/time` n’étant pas installé, sa première invocation n’a pas lancé Blender. Aucun paquet n’a été ajouté ; la mesure a été faite avec Python standard. Aucune approche de rendu n’a été relancée en boucle. Deux images réussies, un essai cinematic refusé, **aucune vidéo**.

Les paramètres effectifs, empreintes PNG et rapports bruts sont dans [validation-evidence.json](validation-evidence.json).

## Notebook Colab Pro

Le notebook dédié installe/détecte Blender et Node, affiche les ressources CPU/GPU, accepte un projet Studio ou un snapshot, exporte au plus trois frames distinctes, sélectionne Cycles et télécharge un ZIP. Le code est compilé/inspecté mais **n’a pas été exécuté sur Colab Pro distant**. Les GPU, versions APT et bibliothèques du runtime Google restent à valider. La présence de nvidia-smi ne remplace pas la détection réelle des devices Cycles.

La branche de revue doit être choisie dans REF avant fusion ; `main` reste le défaut. Le notebook vidéo/Kokoro existant et les paramètres Pages main /docs ne sont pas modifiés. Les installations nécessitent le réseau ; le rendu d’un snapshot n’en nécessite plus.

## Limites et prochaines étapes

- Snapshot figé, pas encore d’armature Blender ni de keyframes ; les animations sont réévaluées par le moteur 0.7 pour chaque export.
- Atlas/stage réduit explicitement à sol + bâtiments, pas d’environnement gigantesque. Panneaux d’équipement additionnels, météo géométrique, fog, ciel en dégradé, éléments et événements legacy omis et listés. Les accessoires déjà présents dans rigBones sont conservés.
- Les acteurs actifs sans rig 0.7 et les plans non voxel sont refusés ; aucun personnage n’est supprimé silencieusement.
- Lumières/couleurs : conversion approximative, pas calibration photométrique. Débruitage indisponible sur le build local.
- Sans mots alignés embarqués, les cues caméra utilisent le timing estimé, signalé dans le snapshot. Les poses à la frame demandée restent déterministes.
- Pas encore d’insertion automatique des images Blender dans l’éditeur ou le montage Remotion ; narration et sous-titres restent dans le pipeline historique.
- Aucun test Android physique, GPU réel ou Colab Pro distant revendiqué.

Pour la prochaine session : exécuter trois petites frames dans Colab Pro, conserver les rapports devices/version, puis ajouter un connecteur d’images dans Remotion et étendre progressivement les éléments exportés. Ne pas lancer de film complet avant ces contrôles.
