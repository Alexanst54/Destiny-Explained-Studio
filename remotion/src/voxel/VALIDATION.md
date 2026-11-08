# Validation du prototype voxel

Environnement : Linux x64, Node 22.23.4, npm 11.9.0, Chromium système
156.0.8078.79, Remotion et @remotion/three 4.0.541, React Three Fiber 8.18.0,
Three.js 0.170.0.

- MP4 complet produit avec `npm run render:voxel -- --browser-executable=/usr/bin/chromium`.
  ffprobe confirme H.264, 1080 × 1920, 30 fps, 450 images, 15 secondes.
  Le flux est signalé yuvj420p (4:2:0 pleine plage), comme pour le moteur 2D.
  Décodage intégral par ffmpeg réussi.
- Réinstallation depuis le verrou : `npm ci --no-fund` réussie, puis TypeScript
  et les trois tests repassés.
- TypeScript : `npm run typecheck` réussi.
- Tests : `npm run test:voxel`, trois tests réussis. Ils couvrent la durée, les
  bornes des phases, le redressement monotone, les valeurs finies sur les 450
  images et l'évaluation des images dans un ordre différent.
- Audit npm des dépendances de production : aucune vulnérabilité signalée.
- Images 0, 165 et 449 rendues avec Chromium et `--gl=swangle`, puis inspectées.
  Le Gardien est allongé au début, en cours de résurrection au milieu et debout
  à la fin ; rayon et particules sont présents pendant la résurrection.
- Deux rendus indépendants de l'image 165 produisent le même SHA-256 :
  `f235ed9b46b2557cdf024ce713a786a63c156073ce1637eadc0ee32dc803ce67`.
  Cela vérifie la reproductibilité sur cette pile graphique, sans garantir une
  égalité des pixels entre navigateurs ou GPU différents.
- L'image de test `Episode1` a également été rendue avec succès après l'ajout de
  la composition 3D. Les fichiers des animations 2D et `index.html` sont inchangés.

Le backend `swiftshader` direct a échoué à créer un contexte WebGL dans cette
version de Chromium ; les commandes utilisent `swangle` (SwiftShader via ANGLE),
qui fonctionne ici sans GPU dédié. Les tests Node ont été exécutés hors du
sandbox de processus, qui empêchait le lancement normal du test runner.

Le parcours Android/Colab et le téléchargement du navigateur Remotion par défaut
n'ont pas été revalidés. Le prototype ne contient pas de narration audio.
Les fichiers produits sont ignorés par Git et restent dans `remotion/out/`.
