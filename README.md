# Destiny Explained Studio

Mobile-first, unofficial fan-made 2D animation storyboard for educational Destiny lore shorts.

## Prototype v0.1
- Vertical 9:16 scene preview
- Animated SVG Ghost and CSS cartoon Void Hunter
- Play/pause and scrubbable timeline
- Editable English captions and scene title
- Local browser save

## Run
Open `index.html` in a browser, or enable GitHub Pages in **Settings → Pages → Deploy from a branch → main / (root)**.

No dependencies, no build, no PC required.

## Next milestones
1. Scene-specific backgrounds and character poses
2. Audio voiceover import and caption timings
3. Android rendering workflow with Google Colab (GitHub Actions optional)
4. Mobile scene editor

**Not affiliated with Bungie.** All visuals in this prototype are original simplified illustrations.

## Moteur Remotion et export MP4

Le moteur est dans [`remotion/`](remotion/README.md), indépendamment du prototype
HTML. Il exporte l'épisode existant en 1080 × 1920 à 30 fps, avec Node 22.23.4 et
des dépendances verrouillées. Voir les commandes d'installation, de vérification,
d'image fixe et de rendu dans [le guide du moteur](remotion/README.md).

Pour rendre depuis un téléphone Android sans ordinateur personnel et sans
GitHub Actions : [guide Google Colab](remotion/COLAB.md).
Les textes saisis dans le prototype HTML ne sont pas transmis au moteur.

## Éditeur JSON mobile (GitHub Pages)

Un éditeur français statique est disponible dans `docs/`. Publication : Settings → Pages → Deploy from a branch → **main /docs**. Aucun workflow Actions à créer. [Guide, stockage local, champs inconnus et parcours Android → Colab](docs/README.md). Sources dans `editor/` ; build et vérification depuis `remotion/` avec `npm run editor:build` et `npm run editor:check`.

La [bibliothèque voxel procédurale](remotion/src/voxel/library/README.md) ajoute quatre décors et des éléments sélectionnables dans le JSON et l’éditeur. Démonstration : `remotion/episodes/voxel_worlds_demo.json`, bouton **Démo 4 décors**, puis import dans Editor-Colab.

## Atlas of Destiny 0.3

L’[Atlas sourcé et extensible](remotion/atlas/README.md) ajoute des références de lieux/variantes au JSON, un onglet mobile et des décors modulaires CPU. [Couverture, sources et lacunes](remotion/atlas/REPORT.md). Le catalogue est partiel : les lignes du manifest ne constituent pas une preuve d’exhaustivité ni de disponibilité actuelle. Démonstration : `remotion/episodes/atlas_demo.json` (24 secondes), bouton **Démo Atlas**, puis parcours Colab existant depuis main après fusion.

## Living Worlds 0.4

[Personnages, populations, animations et météo CPU](remotion/living/README.md) étendent l’Atlas sans changer ses identifiants. L’éditeur `docs/` ajoute **Personnages**, **Météo**, trois démos historiques et une réouverture hors ligne après la première visite. [Rapport, fidélité visuelle et limites](remotion/living/REPORT.md). Publication GitHub Pages toujours **main /docs**, avec le même parcours Android → Colab.

## Hybrid Shorts Director 0.5

Le [storyboard hybride](remotion/hybrid/README.md) réunit voxel, cartes schématiques, timelines, graphiques et texte, avec captions dynamiques et aperçu partagé dans le navigateur. [Guide mobile sans code](remotion/hybrid/MOBILE.md), [parcours Colab CPU](remotion/hybrid/COLAB.md) et [rapport des tests/rendu](remotion/hybrid/REPORT.md). Démo de référence : `remotion/episodes/hybrid_riis.json`, 35 secondes avec Kokoro. Les projets précédents restent accessibles dans l’éditeur existant ; aucune fusion ou publication n’est automatisée.

## Viral Editing & Visual Polish 0.6

[Extensions cinématographiques](remotion/polish/README.md) : quatre nouveaux styles de captions, caméras, personnages expressifs, atmosphères à budgets CPU et narration locale facultative en aperçu. [Guide téléphone](remotion/polish/MOBILE.md), [comparaison Riis 0.5/0.6](remotion/polish/COMPARISON.md) et [rapport de validation](remotion/polish/REPORT.md). La démo `hybrid_riis_06.json` conserve le scénario prudent et les 35 secondes de 0.5.

## Voxel Animation Studio 0.7

[Rigs procéduraux et relations](remotion/animation/README.md), pack éliksni, blocking tactile et cadrage des personnages animés. La démo Riis 0.7 conserve 35 secondes et les 64 mots Kokoro, avec les cinq types hybrides. [Guide téléphone/Colab](remotion/animation/MOBILE.md), [comparaison](remotion/animation/COMPARISON.md) et [validation mesurée](remotion/animation/REPORT.md).

## Blender Bridge 0.8.1

[Exporter une frame 0.7 vers Blender](remotion/blender/README.md), [notebook Colab Pro PNG](remotion/blender/Blender-Colab-Pro.ipynb), [rapport exécuté](remotion/blender/REPORT.md) et [journal de reprise](docs/BLENDER-BRIDGE-PROGRESS.md). Le pont reste indépendant de l’éditeur et du montage Remotion ; aucun rendu vidéo complet n’est lancé.

Cinematic Voxel Environments 0.8.2: [procedural Riis, quality controls and Colab guide](remotion/blender/ENVIRONMENTS.md), with [CPU results and preview comparison](remotion/blender/ENVIRONMENTS-REPORT.md).

## Studio Colab autonome

[Ouvrir Destiny Studio dans Colab Pro](https://colab.research.google.com/github/Alexanst54/Destiny-Explained-Studio/blob/feat/standalone-colab-production-studio/remotion/blender/Destiny-Studio-Colab-Pro.ipynb) : sélection Atlas, Blender, narration française Kokoro, sous-titres alignés et export Remotion H.264/AAC dans Google Drive. Aucun rendu ni téléchargement ne dépend de GitHub Actions. Voir le [guide de production et de reprise](docs/production-studio/README.md) et les limites de validation CPU/T4/Android.
