# Blender Bridge 0.8.1

Pont additif vers des images Blender : les projets 0.7, l’éditeur mobile, Kokoro, Remotion et les sous-titres restent inchangés. Le bridge évalue une frame et exporte des primitives originales, pas des modèles propriétaires.

L’inspection et les checkpoints sont dans [le journal de reprise](../../docs/BLENDER-BRIDGE-PROGRESS.md). Le premier périmètre vise les rigs 0.7, leurs accessoires, une caméra, des lumières, un sol et des bâtiments procéduraux bornés. Il ne promet pas une copie visuelle identique à Three.js ni un export complet de l’Atlas, des effets, du son et des captions.

Les coordonnées source sont droites, Y vers le haut. Blender utilise Z vers le haut ; la conversion choisie est `(x, y, z) → (x, -z, y)`, rotation propre préservant les distances. Les matrices JSON seront colonne majeure, comme Three.js. Les transformations seront figées à la frame demandée, sans simulation accumulée ni armature Blender animable dans cette première version.

## Exporter et rendre

Depuis la racine du dépôt, Node **22.23.4** et Blender installé :

```sh
node --experimental-strip-types remotion/blender/export.mjs remotion/episodes/hybrid_riis_07.json 210 remotion/out/blender/frame-210.json standard
blender --background --factory-startup --python-exit-code 1 --python remotion/blender/import_scene.py -- remotion/out/blender/frame-210.json remotion/out/blender/frame-210.png --device cpu --threads 2
```

Ou importer directement `examples/riis-frame-210.json` : six Éliksni, 176 primitives, décor volontairement réduit à six structures. L’exemple est régénéré par `node --experimental-strip-types remotion/blender/examples/generate.mjs`. Le CLI utilise les chemins depuis le répertoire courant. Aucun fichier de projet n’est modifié.

Les matrices de pose sont calculées par `evaluateStudio` et la hiérarchie `rigBones` à la frame globale demandée. Le plan effectif, la caméra 0.6 puis le cadrage 0.7 et les LOD suivent les fonctions existantes. Les timestamps embarqués sont utilisés lorsqu’ils existent ; sinon `source.timing: estimated` et une omission explicite signalent les cues caméra estimées. La frame et les déplacements restent des fonctions du numéro d’image, sans horloge physique.

Le contrat `schema.ts` / `contract.py` est **indépendant** du schéma d’épisode : `format: destiny-blender-scene`, `version: 1`, `exporterVersion: 0.8.1`. Il contient provenance, sources, mode narratif, frame, caméra, lumières, matériaux, acteurs/joints, primitives et `omissions`. Les couleurs sont sRGB hex ; l’importeur les convertit en valeurs linéaires. Matrices non finies/singulières, références absentes, doublons et versions inconnues sont refusés. Import limité à 4 Mio, 32 acteurs et 4096 primitives. Les objets gardent leur ID complet en propriété `bridge_id`, même si Blender abrège leur nom d’affichage.

L’import crée une **nouvelle scène Blender**, sans effacer celles déjà ouvertes. Les cubes/sphères unitaires sont partagés. Blender ne stocke pas tout cisaillement affine dans ses propriétés position/rotation/échelle : le résidu est alors conservé dans une copie des sommets, avec compteur `bakedAffineCount`. Les transformations sont figées ; il n’y a pas encore d’armature animable ni de keyframes Blender.

## Qualité et matériel

| Profil | Cycles | Rebonds | Débruitage |
| --- | ---: | ---: | --- |
| standard | 16 samples | 2 | Non |
| cinematic | 64 samples | 4 | OpenImageDenoise si compilé/annoncé ; sinon désactivation explicite |

`--scale 25` produit 270×480 ; le défaut 100 conserve 1080×1920. `--device auto` cherche un backend Cycles compatible et utilise CPU si aucun n’est disponible. Si un GPU sélectionné échoue au rendu, un seul repli CPU est tenté et noté dans le rapport. `--device cpu` force CPU. `--check-only` construit/valide la scène sans image. Chaque PNG reçoit un fichier `.report.json` avec paramètres effectifs, limitations et ressources ; un build sans Cycles est refusé clairement.

Les énergies des lumières et le fond sont des approximations de conversion, **pas une équivalence photométrique Three.js/Blender**. Les profils ne promettent pas une qualité cinématographique avancée. Standard à 16 samples peut être bruité. Les scènes d’exemple sont des reconstitutions artistiques, pas des représentations officielles.

## Périmètre et suite

- Export des rigs 0.7 actifs, palette/variation, accessoires déjà définis dans le rig, sol, bâtiments procéduraux et terminaux simples.
- Les panneaux d’équipement supplémentaires du renderer, Atlas complet, éléments legacy, météo géométrique, brouillard, dégradé de ciel et effets visuels sont signalés comme non exportés. Aucun personnage legacy actif n’est supprimé silencieusement : l’export échoue et indique son ID. Les plans non voxel sont refusés.
- Narration, montage, transitions et captions restent dans Remotion. **Aucun branchement automatique des PNG dans le montage ou l’éditeur mobile dans cette version.** L’éditeur et les projets historiques ne sont pas modifiés.
- Le fingerprint du projet porte sur `JSON.stringify(input)` (objet minifié avec ordre de propriétés), pas les octets/espaces du fichier original.

[Notebook Colab Pro](Blender-Colab-Pro.ipynb) : installation/détection Blender et Node, choix d’une à trois frames, upload projet/snapshot, ressources CPU/GPU, repli CPU, rendu PNG et ZIP. Pendant la revue sélectionner REF `feat/blender-bridge-0.8.1` dans le notebook de la branche ; après fusion humaine, `main`. L’installation requiert Internet. Une fois les dépendances présentes, aucun réseau n’est nécessaire au rendu. Aucun Kokoro ni service de génération n’est installé pour ces images.

Tests et mesures réellement exécutés : [REPORT.md](REPORT.md). Pour reprendre demain, lire [le journal](../../docs/BLENDER-BRIDGE-PROGRESS.md). GPU et Colab Pro distant restent à tester ; aucun succès n’est supposé à partir du CPU local.

## Cinematic environments 0.8.2

[Riis environment guide](ENVIRONMENTS.md): deterministic modular city, three detail levels, optional atmosphere, mobile Colab live progress/timeout and CPU/GPU benchmark procedure. Existing 0.8.1 snapshots remain valid. See [validation report](ENVIRONMENTS-REPORT.md).
