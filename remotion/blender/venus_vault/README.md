# Vénus et le Caveau de verre — livraison historique 0.9.0

Ce document décrit la PR #20 au commit `b1fd922`. La version courante de cette branche est la [refonte cinématographique 0.9.1](../cinematic_vex/README.md) ; les limites de modèles et d’IK ci-dessous décrivent la version historique. Les preuves et le notebook 0.9.0 sont conservés.

Trois décors indépendants et deux boss voxel originaux, sélectionnés par les IDs de l’Atlas universel. Aucun modèle, texture, carte ou animation propriétaire importé. Les sources épinglées de l’Atlas attestent les identités et les lieux ; cette géométrie est une interprétation artistique, pas une mesure de la carte du jeu.

## Lancer un rendu

Depuis la racine du dépôt, avec Python 3.11+, Blender **4.3.2 officiel** (Cycles et OpenImageDenoise) et ffmpeg pour les clips :

```sh
python remotion/blender/render_venus_vault.py venus work/venus-general --quality balanced
python remotion/blender/render_venus_vault.py arena-templars-well work/templars-well --quality balanced
python remotion/blender/render_venus_vault.py boss-templar work/templar --camera reveal --animation attack --start-frame 12
python remotion/blender/render_venus_vault.py arena-glass-throne work/glass-throne --quality balanced
python remotion/blender/render_venus_vault.py boss-atheon work/atheon --camera reveal --animation temporal --start-frame 30
python remotion/blender/render_venus_vault.py boss-atheon work/atheon-walk --camera orbit --animation walk --quality draft --width 480 --height 270 --frames 48 --fps 24 --video
```

Le dossier de sortie doit être nouveau pour éviter une fausse preuve issue d’un ancien rendu. `--blender /chemin/blender`, `--device auto|cpu`, `--threads 3` et `--timeout 1800` sont configurables. `auto` réutilise la détection du bridge historique (OPTIX puis CUDA et autres backends, sinon CPU), avec une tentative CPU si le rendu GPU échoue. Le rapport indique le backend effectivement retenu et les éventuels replis. Les performances GPU, la mémoire GPU et Colab ne sont pas présumées validées par les mesures CPU.

Une image : `frames=1`. Clip court : 2 à 120 images, 24 ou 30 FPS ; aucune commande ne lance un épisode complet. `--check-only` construit la scène et évalue les poses sans produire de PNG. `--start-frame` choisit la pose initiale ; les PNG sont numérotés à partir de zéro pour ffmpeg, le rapport conserve les vrais numéros de poses.

Sorties : `request.json`, `frame-0000.png`…, `render-report.json` (paramètres, géométrie SHA-256, PNG SHA-256, temps par image, pic RSS du processus), `run-report.json`, `blender.log`, puis `sequence.mp4` si demandé. Le MP4 H.264/yuv420p de validation est muet. Il ne remplace aucune timeline, voix Kokoro ou caption.

## Sélection Atlas

| Sélection existante | Générateur / arène |
| --- | --- |
| `venus` | Ruines Ishtar, avenue envahie, falaises, architecture vex enfouie |
| `vault-of-glass` | Alias d’entrée vers le Puits du Templier, sans nouveau lieu |
| `arena-templars-well` | Plateformes, colonnades, conflux et oracles |
| `arena-glass-throne` | Trône, deux portails temporels et halo |
| `boss-templar` | Hydre, coque, œil, canons, bouclier segmenté ; Puits du Templier |
| `boss-atheon` | Minotaure, armure, cornes, radiolaria, canon et énergie ; Trône de verre |

Vénus représente une portion artistique de l’Académie Ishtar et de sa jungle ; le site Caveau sélectionne par défaut le Puits du Templier, sans prétendre couvrir les autres salles.

Le sélecteur Python et `atlas/universal/blender.ts` vérifient les IDs, assets et relations boss → rencontre → arène. Ils lisent le même registre `atlas-bindings.json`. Exemple API Node 22.23.4, depuis `remotion/` :

```sh
mkdir -p ../work
node --experimental-strip-types scripts/select-blender-asset.mjs boss-atheon ../work/atheon-request.json '{"animation":"temporal","startFrame":30}'
```

L’API émet la même requête JSON que Python ; `renderer.py` peut la lire directement via Blender. La sélection est disponible par API/CLI et le formulaire Colab. Le menu de l’éditeur historique n’est pas modifié ; ses environnements Remotion restent modulaires. Le statut `dedicated` signifie qu’au moins un moteur possède un asset dédié ; chaque asset garde sa propre fidélité (le fallback Remotion n’est pas promu).

## Qualité, animation et caméra

| Profil | Samples Cycles | Rebonds | Végétation / particules | Brume |
| --- | ---: | ---: | ---: | ---: |
| Draft | 16 | 3 | 25 / 24 | 0.002 |
| Balanced | 48 | 5 | 65 / 65 | 0.0035 |
| Cinematic | 128 | 7 | 120 / 120 | 0.0045 |

Débruitage si OpenImageDenoise est présent ; sinon absence signalée, sans prétendre à la même propreté visuelle. AgX, matériaux métalliques Principled, lumière chaude/cyan, volume borné et léger glow du compositeur. Les détails de silhouette des boss restent identiques dans les trois profils.

Caméras `wide`, `reveal`, `orbit`, `low-angle`, `close-up` : respectivement plan d’ensemble, rapprochement progressif, travelling circulaire, contre-plongée et gros plan lumineux. Chemins continus, déterministes, sans simulation ni bruit aléatoire par image. Athéon : `idle`, `walk`, `combat`, `temporal`. Templier : `idle`, `rotate`, `move`, `attack`. Les rigs reprennent les conventions de noms pelvis/torso/head/hip/knee/foot/shoulder de `animation/rig.ts` quand la topologie correspond ; proportions, coque d’Hydre, bouclier et articulation sont nouveaux. Les rigs quatre bras/humanoïdes historiques ne sont pas présentés comme des boss existants.

Les objets statiques sont fusionnés par matériau ; les pièces du boss par articulation/matériau. Une scène est construite une fois par invocation, puis seuls poses, caméra, poussières et émission sont actualisés. Ce chemin est propre à cette extension : aucun commit ni remplacement du moteur de PR #17. Le générateur utilise un `random.Random(seed)` local ; la même requête produit la même géométrie. L’identité des pixels entre versions de Blender, CPU/GPU et débruiteurs n’est pas garantie.

## Colab et vérifications

Ouvrir [Venus-Vault-Colab-Pro.ipynb](../Venus-Vault-Colab-Pro.ipynb) dans Colab. Trois cellules : installation vérifiée par SHA-256, formulaire de sélection, aperçu/téléchargement. Compatible avec les contrôles de formulaire Colab sur mobile ; aucun terminal de bureau ou Drive requis. Une validation réelle sur Android/T4 reste à effectuer. La branche ne contient ni ne dépend des commits de PR #17.

```sh
python -m unittest discover -s remotion/blender/tests -p 'test_venus_vault.py'
node --experimental-strip-types --test remotion/tests/venus-vault.test.mjs
blender --background --factory-startup --python-exit-code 1 --python remotion/blender/venus_vault/blender_check.py
```

Voir [VALIDATION.md](VALIDATION.md) et les [prévisualisations](../../../docs/previews/venus-vault/README.md) pour les preuves mesurées.

Limites : pas de topographie exacte, de mécanique jouable, d’IK de contact au sol, de collision, de projectile simulé ou de capture d’animation officielle. L’attaque du Templier est une animation de recul/visée, pas une simulation de dégâts. Le bouclier est une cage énergétique segmentée ; les portails sont un cadre lumineux et un champ en grille, sans vue récursive d’une autre époque. La poussière et la brume sont procédurales, sans simulation météo. Pas de reprise automatique d’une invocation interrompue ; les PNG/logs terminés restent inspectables. Les épisodes, anciens contrats Blender/Remotion, Kokoro, sous-titres et notebooks existants sont conservés.
