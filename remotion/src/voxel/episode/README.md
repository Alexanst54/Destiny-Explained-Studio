# Épisodes voxel pilotés par JSON

`VoxelEpisode` utilise le fichier fourni, conservé à l'identique dans
`remotion/episodes/traveler_episode_002.json`. Il ajoute une composition ; les
compositions `Episode1` et `VoxelResurrection` restent disponibles.

## Épisode fourni

| Scène | Images (fin exclue) | Durée | Caméra / action |
| --- | --- | --- | --- |
| 01 | 0–240 | 8 s | plan large et inclinaison vers le ciel / idle |
| 02 | 240–540 | 10 s | orbite lente du Voyageur / hover |
| 03 | 540–840 | 10 s | travelling vers le ciel / look-up |
| 04 | 840–1200 | 12 s | gros plan du Spectre / hover + scan |
| 05 | 1200–1500 | 10 s | plan moyen / resurrect + hover |
| 06 | 1500–1800 | 10 s | recul large / idle + hover |

Total : **1800 images, 60 secondes, 1080 × 1920, 30 fps**. Les plages sont
contiguës ; une durée différente dans le JSON recalcule les métadonnées Remotion.

La Tour comprend un balcon, des garde-corps et une silhouette de la Dernière Cité.
Le Voyageur est une sphère discrétisée en cubes instanciés, avec cicatrices et halo.
Ils réutilisent la palette, les matériaux mats et l'éclairage du prototype.
Gardien, Spectre, rayon et particules sont réutilisés ; seule une inclinaison de tête
optionnelle a été ajoutée au Gardien, à zéro dans l'ancienne composition.
Aucun asset externe ni service payant n'est requis.

## Aperçu et rendu final

Le JSON annonce une voix `to-generate` et des sous-titres
`pending-voiceover-alignment`. Ces ressources ne sont pas fournies. L'aperçu est
**silencieux**, porte un bandeau explicite et affiche le texte en groupes de six
mots sur deux lignes, avec un minutage estimé. Ce n'est pas un alignement audio.

Depuis `remotion/`, avec Node 22.23.4 :

```bash
npm ci
npm run typecheck
npm run test:voxel
npm run test:episode
npm run validate:episode -- --preview
npm run still:episode
npm run render:episode:test
```

L'image est à l'image 1310. Le test MP4 rend les images **1140 à 1319 incluses**,
soit six secondes à cheval sur les scènes 04 et 05, en pleine résolution.
Le JSON reste un épisode de 60 secondes ; cet extrait ne constitue pas le rendu
intégral. Sortie : `out/episode-002-traveler-preview.mp4`.

Pour rendre les 60 secondes d'aperçu :

```bash
npm run render:episode -- episodes/traveler_episode_002.json --preview
```

Pour un autre épisode compatible, fournir son chemin après `render:episode` ou
`validate:episode`. Le format actuel accepte les modèles, caméras, actions et effets
listés ci-dessous ; de nouveaux identifiants nécessitent une implémentation.

Si le navigateur téléchargé par Remotion n'est pas accessible :

```bash
npm run still:episode -- --browser-executable=/usr/bin/chromium
npm run render:episode:test -- --browser-executable=/usr/bin/chromium
```

Le rendu 3D utilise SwiftShader via ANGLE (`swangle`) et une tâche concurrente.
Le temps de calcul varie selon la machine attribuée.

## Narration et véritable alignement

1. Fournir `public/assets/audio/traveler-en.wav` et passer son statut à `ready`.
2. Fournir `public/assets/subtitles/traveler-en.words.json`, un tableau de mots :
   `[{"text":"Above","start":0.2,"end":0.6}, ...]`, temps globaux en secondes.
3. Passer le statut des sous-titres à `ready`. Le texte aligné doit correspondre
   à l'intégralité de la narration, avec des intervalles ordonnés sans chevauchement.
4. Installer `ffprobe` (paquet système `ffmpeg`), puis lancer :

```bash
npm run validate:episode -- episodes/traveler_episode_002.json
npm run render:episode -- episodes/traveler_episode_002.json
```

Le wrapper vérifie les fichiers audio et d'alignement ainsi que la durée audio :
la voix doit couvrir le dernier mot et tenir dans les 60 secondes. Il refuse un
rendu final si les ressources sont encore en attente, au lieu de produire un MP4
final silencieux. Le fichier final porte le nom `render.output` du JSON ;
l'aperçu porte le suffixe `-preview`. Ne pas contourner ces vérifications avec une
commande CLI directe pour un export final.

Le moteur n'intègre ni TTS ni alignement forcé automatique. Le texte source reste
un brouillon à vérifier éditorialement, notamment ses références temporelles au
Voyageur, avant de produire la voix. Les durées par scène ne sont pas ajustées
automatiquement à la diction ; le validateur signale les scènes dépassant 180 mots/min.

## Validation et actions

Le schéma Zod strict (`schema.ts`) rejette les champs inconnus, versions et modèles
non pris en charge, références invalides, identifiants dupliqués, actions en conflit,
trous, chevauchements, durées non entières ou total incohérent. Les chemins d'assets
sont relatifs à `public/`, sans traversée de répertoires. Le format est limité à
1080 × 1920 et 30 fps ; les scènes durent au moins 30 images.

- Gardien : `idle`, `look-up`, `resurrect` (minimum 120 images).
- Spectre : `hover`, `scan` (combinables).
- Le rayon `resurrection-beam` exige l'action `resurrect`, et réciproquement.
- Les personnages persistent entre les scènes ; sans action particulière, le
  Gardien reste debout et le Spectre conserve son flottement de base.
- Caméras : les six noms du JSON sont implémentés dans `cameraPose`.
- Effets : `soft-daylight` reprend l'éclairage de base ; `golden-glow` ajoute une
  lumière chaude ; `sky-darken` et `distant-lightning` modifient le ciel ;
  `light-particles`, `voxel-particles`, `resurrection-beam`, `traveler-halo`
  activent les effets correspondants.

Tous les états visuels dépendent du numéro d'image. La résurrection réutilise la
chronologie du prototype, normalisée à la durée de la scène. La caméra et les
particules restent déterministes, sans simulation cumulée. Les plans sont reliés
par des coupes franches. Les deux lignes de sous-titres respectent la marge basse
du JSON ; les mots très longs peuvent demander une révision éditoriale.

## Android / Colab

Suivre [le guide Colab](../../../COLAB.md). Avant fusion de cette PR, sélectionner
`REF = "feat/json-voxel-episodes"` dans une session neuve. Après installation,
remplacer les commandes de rendu par celles ci-dessus, en conservant le `PATH`
Node 22 dans chaque cellule Bash. Pour récupérer l'extrait :

```python
from google.colab import files
files.download('/content/Destiny-Explained-Studio/remotion/out/episode-002-traveler-preview.mp4')
```

Aucun workflow GitHub Actions n'est nécessaire. Les MP4 ne sont pas versionnés.
Cette branche s'appuie sur `feat/voxel-resurrection` (PR #2) tant que celle-ci
n'est pas fusionnée : la PR JSON cible cette branche pour isoler ses changements.
