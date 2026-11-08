# Prototype voxel : VoxelResurrection

Composition autonome de **15 secondes, 450 images, 1080 × 1920, 30 fps**.
L'épisode SVG `Episode1` et les commandes 2D existantes restent disponibles.

Le Gardien et son Spectre sont des illustrations originales procédurales inspirées
de Destiny 2, assemblées à partir de cubes. Aucun modèle, texture, API, police ou
asset payant n'est téléchargé. Le rayon et son anneau utilisent des primitives
Three.js à faible nombre de segments. Ce prototype est silencieux : les phrases
anglaises affichées expliquent l'action, sans narration ni alignement audio.

## Chronologie

- 0–2 s : Gardien allongé, arrivée du Spectre.
- 2–4 s : rayon lumineux et particules cubiques.
- 4–8 s : redressement du Gardien et dissipation progressive du rayon.
- 8–15 s : Gardien debout, Spectre flottant, fin du mouvement de caméra.

`timeline.ts` calcule la pose depuis le numéro d'image, avec interpolation douce.
Les particules utilisent un hash entier indexé et une phase analytique. La caméra,
le flottement et les mouvements ne dépendent ni de l'horloge, ni de Math.random,
ni d'une simulation accumulée via useFrame. `ThreeCanvas` de `@remotion/three`
coordonne React Three Fiber avec les images Remotion. La reproductibilité des
pixels doit être évaluée avec le même navigateur, backend GL et environnement ;
une autre pile graphique peut modifier légèrement les pixels.

## Commandes

Depuis `remotion/`, avec Node 22.23.4 :

```bash
npm ci
npm run typecheck
npm run test:voxel
npm run browser:ensure
npm run still:voxel
npm run render:voxel
```

Sorties : `out/voxel-frame.png` à l'image 165 (5,5 secondes) et
`out/voxel-resurrection.mp4`. Les tests de chronologie utilisent le support
TypeScript expérimental de Node 22 ; un avertissement de détection du module
peut apparaître sans affecter les tests ou le rendu.

Les commandes voxel utilisent `--gl=swangle` : SwiftShader via ANGLE, pour rendre
sur CPU sans GPU dédié. Le rendu 3D peut être sensiblement plus lent que la 2D.
Une seule tâche de rendu est utilisée pour limiter la consommation mémoire.

Si Chromium est déjà installé et que le téléchargement du navigateur est bloqué :

```bash
npm run still:voxel -- --browser-executable=/usr/bin/chromium
npm run render:voxel -- --browser-executable=/usr/bin/chromium
```

Pour choisir un autre backend GL, appeler directement la CLI afin de ne pas
répéter le même paramètre dans une commande npm :

```bash
npx remotion still src/index.ts VoxelResurrection out/voxel-angle.png --frame=165 --gl=angle
```

Sur Android, suivre les installations du [guide Colab](../../COLAB.md), puis
remplacer les commandes 2D par celles ci-dessus. Pour télécharger le MP4 :

```python
from google.colab import files
files.download('/content/Destiny-Explained-Studio/remotion/out/voxel-resurrection.mp4')
```

Avant fusion, choisir la branche `feat/voxel-resurrection` dans la cellule de
clonage Colab, depuis une session neuve. WebGL 2 est requis. Sa disponibilité et
les quotas de Colab doivent être vérifiés sur la machine attribuée.
