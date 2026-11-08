# Validation du moteur cinématique

Environnement : Linux x64, Node 22.23.4, Remotion / @remotion/three 4.0.541,
Three.js 0.170.0, React Three Fiber 8.18.0, Chromium système 156 et backend
`swangle` (SwiftShader via ANGLE), sans GPU dédié.

## Épisode de test

La nouvelle variante conserve les six scènes, leurs textes et leurs durées :
1800 images, 60 secondes, 1080 × 1920 à 30 fps. La voix Kokoro `af_heart` à 1×
est réutilisée sans nouvel appel de synthèse ni modification des fichiers audio.
126 mots conservent leurs horodatages. Le montage équilibré contient 16 plans.

| Plan | Image de début | Image de fin exclue | Durée |
| --- | ---: | ---: | ---: |
| arrival | 0 | 110 | 3.667 s |
| traveler-reveal | 110 | 240 | 4.333 s |
| ancient-arrival | 240 | 415 | 5.833 s |
| golden-age | 415 | 540 | 4.167 s |
| collapse-context | 540 | 618 | 2.600 s |
| collapse-impact | 618 | 663 | 1.500 s |
| collapse-aftermath | 663 | 705 | 1.400 s |
| traveler-remains | 705 | 840 | 4.500 s |
| ghost-release | 840 | 970 | 4.333 s |
| ghost-companion | 970 | 1106 | 4.533 s |
| guardian-defender | 1106 | 1200 | 3.133 s |
| fallen-guardian | 1200 | 1286 | 2.867 s |
| return-to-life | 1286 | 1356 | 2.333 s |
| ghost-vulnerable | 1356 | 1500 | 4.800 s |
| mystery-reveal | 1500 | 1649 | 4.967 s |
| hope-pullback | 1649 | 1800 | 5.033 s |

Les quatre plans de l’Effondrement sont présentés comme des visions illustratives,
sans Gardien historique avant les Spectres. Les coupes d’impact durent 1,5 et
1,4 seconde ; les révélations et la conclusion durent environ 4 à 6 secondes.

## Tests et rendus de contrôle

- Compilation TypeScript : réussie.
- 21 tests : trois voxel, six JSON, six narration Python et six cinématiques.
- Les nouveaux tests couvrent la résolution des mots, les 1800 images sur trois
  intensités, les chemins de caméra, les actions et les transitions invalides,
  les états finis, les conflits d’acteurs et les accès aux images hors séquence.
- Un rendu PNG par plan a été produit et la planche de 16 images inspectée.
- Les huit mouvements de `VoxelMotionLab` ont été rendus en PNG. Les profils
  calme et cinématique ont également été rendus au plan d’impact.
- Deux rendus indépendants de l’image 640 ont le même SHA-256 :
  `76b2716487072426597d0661e0afc05b908945fd6d497fdd4ac065731121b5fe`.
- `Episode1` et `VoxelResurrection` ont été rendus après la modification du rig.
  L’image 165 du prototype voxel garde exactement son SHA-256 antérieur :
  `f235ed9b46b2557cdf024ce713a786a63c156073ce1637eadc0ee32dc803ce67`.
- Syntaxes JSON, Python et Bash du notebook Colab vérifiées ; aucun résultat
  audio/vidéo ni secret n’est enregistré dans le notebook.

## Rendu final

Le MP4 intégral a été généré avec `npm run render:cinematic` et Chromium système,
`swangle`, deux tâches de rendu : H.264, **1080 × 1920, 30 fps, 1800 images et
60 secondes**, avec **AAC 48 kHz de 60,011 secondes**. Le décodage intégral par
ffmpeg réussit.

`npm run verify:cinematic` confirme 126 mots avec signal audio et une comparaison
WAV/AAC sur une fenêtre d'une seconde par scène : **décalage nul dans les six
fenêtres**, corrélation de 0,99816 à 0,99996. Les durées et le placement de la voix
Kokoro d'origine sont donc conservés. Cela ne remplace pas une annotation humaine
des frontières phonétiques.

Deux images extraites du MP4 final ont été inspectées : impact à 21,333 s avec
« catastrophe » surligné et résurrection à 44 s. Le bandeau d'aperçu est absent,
et la vision de l'Effondrement porte son indication illustrative.

## Limites

Les personnages utilisent des animations articulées stylisées, sans IK ni moteur
physique. Les visions sont symboliques et le choix de plans reste une décision
éditoriale explicite. La galerie de mouvements a été contrôlée par images, pas
par un export intégral de ses 24 secondes. Le parcours Colab/Android n’a pas été
exécuté sur un appareil dans cette tâche. Les captures et MP4 sont exclus de Git.
Les sous-titres et la voix conservent les limites de la synthèse Kokoro native.
