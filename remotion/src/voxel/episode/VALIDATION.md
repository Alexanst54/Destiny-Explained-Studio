# Validation de l'intégration JSON

Environnement : Linux x64, Node 22.23.4, npm 11.9.0, Chromium système
156.0.8078.79, backend `swangle` (SwiftShader via ANGLE, sans GPU dédié).
Remotion et @remotion/three : 4.0.541 ; Zod : 4.6.7, version demandée par Remotion.

## Données et tests

Le JSON fourni est conservé à l'identique (SHA-256) :
`1783dc2778b2d569e9bcdb493dd6d925e35e856c33fba1d4fe791503929b8299`.
Six scènes contiguës : 240 + 300 + 300 + 360 + 300 + 300 = 1800 images,
soit 60 secondes à 30 fps. Métadonnées de composition vérifiées par le renderer :
1080 × 1920, 30 fps, 1800 images.

- Réinstallation depuis le verrou final (`npm ci --no-fund`) réussie, puis
  compilation TypeScript et neuf tests repassés.
- Trois tests existants de chronologie voxel réussis.
- Six tests JSON réussis : schéma et scènes ; rejets des actions, références et
  chemins invalides ; états et caméras finis sur les 1800 images ; accès aux
  images dans un ordre différent ; alignement des mots ; CLI et disponibilité
  des ressources ; contrôle de véritables durées WAV avec ffprobe.
- Le dernier test emploie des fichiers WAV silencieux temporaires, supprimés à
  la fin. Ces fichiers vérifient le validateur, pas une narration générée.
- Le rendu final est refusé avec le JSON fourni, car la voix et l'alignement
  sont explicitement en attente. Le mode aperçu annonce le silence et les
  sous-titres estimés.

## Contrôles visuels

Une image par scène a été produite et inspectée aux images 120, 390, 615, 1020,
1350 et 1650. Les six caméras, la Tour, la sphère voxel du Voyageur, le halo,
les personnages et la résurrection sont visibles dans les plans correspondants.
Une image supplémentaire a été produite à l'image 1310 pour le test npm.

Les compositions `Episode1` (300 images) et `VoxelResurrection` (450 images) ont
été sélectionnées et leurs images de référence rendues. L'image 165 de l'ancienne
composition voxel conserve exactement le SHA-256 antérieur :
`f235ed9b46b2557cdf024ce713a786a63c156073ce1637eadc0ee32dc803ce67`.
Les fichiers 2D, l'interface `index.html` et les workflows ne sont pas modifiés.

## MP4 de test

`npm run render:episode:test -- --browser-executable=/usr/bin/chromium` a produit
`out/episode-002-traveler-preview.mp4`. ffprobe confirme H.264, 1080 × 1920,
30 fps, 180 images et 6 secondes. Le flux est signalé yuvj420p (4:2:0 pleine plage).
Le décodage intégral par ffmpeg réussit. Cet extrait couvre les images globales
1140 à 1319 incluses (fin du scan et début de la résurrection), pas les 60 secondes
complètes. La voix est volontairement absente en mode aperçu.

Audit npm des dépendances de production : aucune vulnérabilité signalée.

## Limites

Les images testées ne remplacent pas une revue éditoriale du lore. Aucune voix ni
véritable synchronisation audio n'a été générée : les ressources référencées dans
le JSON ne sont pas jointes. Le rendu intégral de 60 secondes, le parcours Colab
sur Android et le téléchargement du navigateur Remotion par défaut ne sont pas
revendiqués. Les sorties ne sont pas ajoutées à Git.

La PR s'appuie sur la branche voxel de la PR #2 et la cible tant que celle-ci
n'est pas fusionnée. Aucune fusion automatique n'est effectuée.
