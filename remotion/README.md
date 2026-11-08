# Moteur vidéo Remotion

Ce moteur est indépendant de `index.html`. Il rend l'épisode existant avec toutes
ses animations SVG : 10 secondes, 300 images, 30 fps, **1080 × 1920**.
L'épisode 2D est actuellement silencieux (`voiceover: null`). Une composition
voxel indépendante est disponible ; voir la section correspondante ci-dessous.

## Environnement reproductible

- Node.js **22.23.4** (`.nvmrc` à la racine et dans ce dossier).
- Remotion et CLI **4.0.541**, React **18.3.1**.
- Utiliser `npm ci` avec le `package-lock.json` suivi, pas une installation globale
  de Remotion. Node 22 fournit npm 10 ; npm 10 ou 11 est accepté.
- Linux avec Chromium Headless Shell et ses bibliothèques système. Le premier
  téléchargement du navigateur demande un accès Internet et de l'espace disque.

Avec nvm déjà installé :

```bash
cd remotion
nvm install
nvm use
npm ci
npm run typecheck
npm run browser:ensure
npm run still
npm run render
```

Résultats : `out/frame.png` (image 150, à 5 secondes) et `out/episode1.mp4`
(H.264, yuv420p, compatible avec les lecteurs mobiles). Dimensions et fréquence
sont définies dans `src/project/timeline.ts`, puis utilisées par `Root.tsx`.
Le rendu utilise deux tâches concurrentes pour limiter la mémoire ; ajouter
`-- --concurrency=1` au rendu en cas de mémoire insuffisante. Les sorties sont
remplacées lors d'un nouveau rendu et ne sont pas versionnées.

`npm run dev` ouvre le Studio pour un environnement permettant l'accès à son port.
Le Studio n'est pas nécessaire pour les commandes de rendu.

## Audio facultatif

Placer un fichier dans `public/`, puis remplacer `voiceover: null` dans
`src/project/episode1.ts` par son chemin relatif, par exemple `'voiceover.mp3'`.
La durée de l'épisode dépend des scènes, pas du fichier audio : adapter les scènes
et les sous-titres pour éviter de couper la narration. Aucun alignement automatique
ni service de synthèse vocale n'est inclus.

## Rendu depuis Android, sans ordinateur personnel

Suivre [le guide Google Colab](COLAB.md). GitHub ne sert que de dépôt de sources :
aucun workflow GitHub Actions n'est nécessaire au rendu.

## Navigateur système en solution de repli

Si le téléchargement du navigateur échoue mais qu'un Chromium compatible est déjà
installé, fournir son chemin explicitement (sans modifier la configuration) :

```bash
npm run still -- --browser-executable=/usr/bin/chromium
npm run render -- --browser-executable=/usr/bin/chromium
```

Le navigateur système dépend de la machine ; le Headless Shell téléchargé par
Remotion reste le parcours par défaut. Les restrictions réseau de l'environnement
peuvent empêcher son téléchargement sans indiquer une erreur dans le projet.

## Prototype voxel 3D

La composition `VoxelResurrection` ajoute une résurrection procédurale de
15 secondes avec Three.js, React Three Fiber et `@remotion/three`, sans remplacer
`Episode1`. Voir [la scène voxel et ses commandes](src/voxel/README.md).

## Épisode JSON : le Voyageur

`VoxelEpisode` accepte le format strict fourni dans
`episodes/traveler_episode_002.json`, avec six scènes sur 60 secondes.
Voir [le guide JSON, la validation et le rendu de test](src/voxel/episode/README.md).
Le JSON source annonce la voix et l'alignement en attente. Le moteur Kokoro
ci-dessous génère les ressources et un JSON prêt pour le rendu final ; le test
JSON initial reste un aperçu silencieux.

## Narration gratuite par défaut

Kokoro génère la voix anglaise `af_heart` à vitesse 1×, les WAV par scène et les
sous-titres mot par mot. Voir [le guide Kokoro et Colab](tts/COLAB-TTS.md) et
[le notebook Android](tts/Kokoro-Colab.ipynb). OpenAI TTS reste une option
explicitement activable, sans appel payant dans le parcours par défaut.
