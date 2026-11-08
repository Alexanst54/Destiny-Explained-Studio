# Validation du moteur — 8 novembre 2026

Environnement : Linux x64, Node 22.23.4, npm 11.9.0, Chromium système
156.0.8078.79. Remotion / CLI 4.0.541.

Vérifications effectuées :

- `npm ci --no-fund` : installation depuis le verrou réussie.
- `npm run typecheck` : réussi, aucune correction TypeScript nécessaire.
- `npm ls remotion @remotion/cli react react-dom` : versions cohérentes.
- `npm audit --omit=dev --audit-level=high` : aucune vulnérabilité signalée.
- `npm run still -- --browser-executable=/usr/bin/chromium` : PNG généré,
  dimensions 1080 × 1920 confirmées par ffprobe ; image inspectée visuellement.
- `npm run render -- --browser-executable=/usr/bin/chromium` : MP4 complet généré.
- ffprobe : H.264, 1080 × 1920, 30 fps, 300 images, durée 10 secondes.
  Le flux est signalé `yuvj420p` (4:2:0 pleine plage), malgré la demande CLI
  `yuv420p`. Le fichier est silencieux conformément à `voiceover: null`.
- Décodage intégral avec `ffmpeg -v error -i out/episode1.mp4 -f null -` : réussi.
- Syntaxe des cellules Python et Bash du guide Colab vérifiée.
- `git diff --check` : réussi. `index.html`, les animations dans `src/` et les
  workflows n'ont pas été modifiés. Vidéo et dépendances exclues de Git.

Limites : le téléchargement par `npm run browser:ensure` a échoué dans cet
environnement avec ECONNREFUSED / ENETUNREACH. Les commandes sans navigateur
explicite ont donc échoué ici ; les rendus ont ensuite réussi avec Chromium
système. Le parcours Headless Shell par défaut, l'exécution effective dans Colab,
le téléchargement sur Android et la lecture dans l'application YouTube restent
à valider. Aucun résultat audio n'est revendiqué.

Les fichiers produits restent dans `out/` localement et ne sont pas commités.
