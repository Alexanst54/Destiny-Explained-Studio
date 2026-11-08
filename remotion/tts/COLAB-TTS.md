# Narration Kokoro et vidéo depuis Android

Le parcours par défaut est **Kokoro 0.9.4**, voix américaine **af_heart**, vitesse
**1×**, sur CPU. Il ne demande aucune clé API et n'appelle pas OpenAI. Le modèle
Kokoro-82M public est fixé à une révision précise dans `config/narration.json`.
Le premier lancement télécharge PyTorch CPU, le modèle, sa voix et le modèle
linguistique anglais spaCy. Prévoir plusieurs Go libres et un accès Internet.

[Ouvrir le notebook dans Google Colab](https://colab.research.google.com/github/Alexanst54/Destiny-Explained-Studio/blob/feat/kokoro-narration/remotion/tts/Kokoro-Colab.ipynb)
depuis Chrome Android. Le fichier [Kokoro-Colab.ipynb](Kokoro-Colab.ipynb) est
également téléchargeable depuis le dépôt. Avant fusion, il clone `feat/kokoro-narration`.
Après fusion, `REF` peut être remplacé par `main` dans la première cellule.
Choisir une session Python 3.12 / CPU ; aucun GPU dédié n'est nécessaire.
Colab peut interrompre ses sessions et ses quotas gratuits ne sont pas garantis.
Le mode « Version pour ordinateur » de Chrome peut faciliter les manipulations.

## Installation Linux / Colab

Suivre d'abord [l'installation Node et navigateur](../COLAB.md). Pour la voix,
utiliser un environnement Python isolé afin de conserver les versions testées :

```bash
python3 -m venv /content/destiny-tts
/content/destiny-tts/bin/pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu
/content/destiny-tts/bin/pip install -r /content/Destiny-Explained-Studio/remotion/tts/requirements-kokoro.txt
```

`misaki[en]` fournit espeak-ng via `espeakng-loader` : les noms hors dictionnaire
ne nécessitent pas de droits administrateur. `ffmpeg` et `ffprobe` restent requis
pour le contrôle audio et le rendu final (paquet système `ffmpeg`). Le modèle
spaCy est installé explicitement, évitant son téléchargement caché au premier appel.

Dans chaque cellule Bash, redéfinir le PATH, car il ne persiste pas entre cellules :

```bash
export PATH="/content/destiny-tts/bin:/content/node-v22.23.4-linux-x64/bin:$PATH"
cd /content/Destiny-Explained-Studio/remotion
npm ci
npm run narrate:episode
npm run render:episode:voiced
npm run verify:narration
```

Sur une machine disposant de Chromium système, fournir son chemin :

```bash
npm run render:episode:voiced -- --browser-executable=/usr/bin/chromium
```

Le rendu utilise une tâche par défaut. Avec assez de mémoire, deux tâches sont
possibles : `npm run render:episode:voiced -- --concurrency=2`.

## Fichiers produits

Le JSON fourni reste inchangé. La commande génère :

- Un WAV mono PCM16 à 24 kHz par scène, et ses mots horodatés localement.
- Une piste `narration.wav` assemblée aux départs exacts des scènes, complétée
  de silence jusqu'à 60 secondes, et `words.json` aux temps globaux.
- Un manifeste et `out/narration-report.json` avec les durées réellement mesurées.
- `out/traveler_episode_002-ready.json`, qui référence les ressources prêtes.
- Avec Remotion : `out/episode-002-traveler.mp4`, avec voix et surbrillance des mots.

Les ressources audio, modèles, sous-titres générés, JSON prêt et MP4 ne sont pas
commités. Les fichiers réutilisables sont sous
`public/assets/narration/<episode>/<provider>-<empreinte>/`. Le cache vérifie
l'empreinte du WAV ; modifier le texte, la voix, la révision ou la vitesse change
l'identifiant de cache. `--force` force une nouvelle synthèse :

```bash
npm run narrate:episode -- --force
```

Pour un autre JSON compatible :

```bash
python scripts/narration.py episodes/mon-episode.json
npm run render:episode -- out/mon-episode-ready.json
```

Aucun ajustement automatique du texte, de la vitesse ou de la durée des scènes
n'est effectué. Si une narration dépasse sa scène, la génération échoue avec la
durée mesurée et ne laisse pas de JSON prêt obsolète. Il faut alors raccourcir le
texte ou revoir les durées dans le JSON, en conservant leur total si nécessaire.
Le script n'ajoute pas de pause initiale par défaut ; les pauses de Kokoro restent
présentes. Les silences de fin de scène conservent les 60 secondes originales.

## Synchronisation des mots

Kokoro prédit les durées des phonèmes utilisées pour produire le son. Ces durées
fournissent les horodatages des tokens, qui sont associés aux mots exacts du texte,
y compris les contractions. Les segments Kokoro éventuels sont concaténés avec
leurs offsets audio réels. Aucun minutage uniforme n'est substitué en cas d'erreur.

Les mots sont validés contre la narration, la durée du WAV et leur scène ; ils ne
peuvent ni se chevaucher, ni déborder sur le plan suivant. Remotion affiche les
mots du plan courant et surligne celui qui correspond au temps de l'image.
Les horodatages sont ceux du synthétiseur, pas une annotation humaine ni une
mesure indépendante de la précision acoustique. Vérifier à l'écoute les noms
propres et les sous-titres avant publication.

## Télécharger depuis Android

Après le rendu, dans une cellule Python :

```python
from google.colab import files
files.download('/content/Destiny-Explained-Studio/remotion/out/episode-002-traveler.mp4')
```

Le notebook propose aussi un ZIP contenant les six WAV, leurs sous-titres,
la piste assemblée, les mots globaux et le manifeste. Télécharger les résultats
avant de fermer la session Colab. Si Chrome bloque plusieurs téléchargements,
les lancer séparément ou utiliser le panneau Fichiers de Colab.

La commande `npm run verify:narration` contrôle la présence de H.264/AAC, les
60 secondes des deux flux, les limites des mots et le signal audio de chaque mot.
Elle compare aussi une fenêtre audio par scène entre le WAV source et l'AAC du
MP4 pour détecter un décalage d'encodage. Ce contrôle ne remplace pas l'écoute
pour juger la précision phonétique ou la prononciation.

## OpenAI TTS : option payante, désactivée

Le moteur reste disponible mais ne s'active jamais en secours automatique.
Il utilise `gpt-4o-mini-tts`, voix `alloy`, vitesse 1× : `af_heart` est propre à Kokoro.
Installer seulement pour ce parcours les dépendances d'alignement local :

```bash
pip install torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu
pip install -r tts/requirements-openai.txt
```

Configurer `OPENAI_API_KEY` dans l'environnement sécurisé (dans Colab, utiliser
Secrets et `google.colab.userdata`, sans afficher la clé). Puis sélectionner
explicitement le fournisseur et autoriser ses appels :

```bash
python scripts/narration.py --provider openai --enable-openai
```

Le drapeau active OpenAI uniquement pour cet appel ; le fichier de configuration
conserve `enabled: false`. L'alignement utilise localement `stable-ts` et Whisper
`base.en` sur le texte fourni. Il ne s'agit pas d'un appel OpenAI de transcription.
Cette option peut entraîner des frais TTS ; elle n'a pas été exécutée dans le
test Kokoro et n'est pas nécessaire à celui-ci.

## Tests et limites

```bash
npm run typecheck
npm run test:voxel
npm run test:episode
npm run test:narration
```

Les tests Python demandent numpy/soundfile, installés dans l'environnement Kokoro.
Les tests simulant une voix servent à contrôler les silences, le cache et les
erreurs ; le rapport de validation distingue ces tests de la synthèse réelle.
La chaîne ne publie pas sur YouTube et ne dépend pas de GitHub Actions.
