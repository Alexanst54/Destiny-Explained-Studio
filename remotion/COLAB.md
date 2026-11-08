# Rendre depuis Google Colab sur Android

Ouvrir https://colab.research.google.com dans Chrome Android, créer un notebook,
choisir un environnement **Python 3 / CPU**, puis copier les cellules ci-dessous.
Le mode « Version pour ordinateur » de Chrome peut faciliter les manipulations.
Aucun GPU, abonnement payant ou GitHub Actions n'est requis par ce parcours.
La disponibilité gratuite de Colab, ses quotas et la durée des sessions ne sont
pas garantis. Télécharger les sorties avant la fermeture de la session.

Ce guide n'installe rien sur le téléphone. Les commandes s'exécutent sur la machine
Linux temporaire de Colab. Le dépôt doit être accessible publiquement ; ne jamais
coller de jeton GitHub dans un notebook partagé.

## 1. Télécharger les sources

Cellule Python (sans `%%bash`) :

```python
import os
import subprocess

# Avant fusion de la PR, garder cette branche ; après fusion, utiliser "main".
REF = "fix/stable-remotion-render"
PROJECT = "/content/Destiny-Explained-Studio"
if not os.path.exists(PROJECT):
    subprocess.run([
        "git", "clone", "--branch", REF, "--single-branch",
        "https://github.com/Alexanst54/Destiny-Explained-Studio.git", PROJECT
    ], check=True)
subprocess.run(["git", "-C", PROJECT, "rev-parse", "HEAD"], check=True)
```

Pour tester une autre révision, repartir d'une nouvelle session et changer `REF`.
La cellule réutilise un clone existant sans effacer les fichiers de travail.

## 2. Installer Node et les bibliothèques du navigateur

Cellule Bash :

```bash
%%bash
set -euo pipefail
cd /content
NODE_VERSION=22.23.4
NODE_ARCHIVE="node-v${NODE_VERSION}-linux-x64.tar.xz"
curl -fsSLO "https://nodejs.org/dist/v${NODE_VERSION}/${NODE_ARCHIVE}"
curl -fsSLo node-SHASUMS256.txt "https://nodejs.org/dist/v${NODE_VERSION}/SHASUMS256.txt"
awk -v f="$NODE_ARCHIVE" '$2 == f' node-SHASUMS256.txt | sha256sum --check -
tar -xJf "$NODE_ARCHIVE"
apt-get update -qq
AUDIO_PACKAGE=libasound2
if apt-cache show libasound2t64 >/dev/null 2>&1; then
  AUDIO_PACKAGE=libasound2t64
fi
apt-get install -y libnss3 libatk-bridge2.0-0 libx11-xcb1 libxcomposite1 \
  libxdamage1 libxrandr2 libgbm1 "$AUDIO_PACKAGE" fonts-liberation
```

Colab accorde normalement les droits système nécessaires. Si l'installation est
refusée, le notebook doit être exécuté dans un environnement autorisant ces paquets.

## 3. Installer et vérifier le projet

```bash
%%bash
set -euo pipefail
export PATH="/content/node-v22.23.4-linux-x64/bin:$PATH"
cd /content/Destiny-Explained-Studio/remotion
node --version
npm --version
npm ci
npm run typecheck
npm run browser:ensure
npm run still
```

`PATH` est redéfini dans chaque cellule Bash : les exports ne persistent pas entre
les cellules. Ne pas lancer `npm audit fix` : cela modifierait les versions testées.

Cellule Python pour voir l'image :

```python
from IPython.display import display, Image
display(Image(filename="/content/Destiny-Explained-Studio/remotion/out/frame.png"))
```

## 4. Produire le MP4

```bash
%%bash
set -euo pipefail
export PATH="/content/node-v22.23.4-linux-x64/bin:$PATH"
cd /content/Destiny-Explained-Studio/remotion
npm run render
```

En cas de manque de mémoire, relancer avec `npm run render -- --concurrency=1`.
Le temps de rendu varie selon la machine attribuée. Une déconnexion ou la fin de
session peut interrompre le travail ; aucun service permanent n'est installé.

## 5. Télécharger sur le téléphone

Cellule Python :

```python
from google.colab import files
files.download("/content/Destiny-Explained-Studio/remotion/out/episode1.mp4")
# Facultatif :
# files.download("/content/Destiny-Explained-Studio/remotion/out/frame.png")
```

Si le téléchargement ne démarre pas, utiliser le panneau Fichiers de Colab,
ouvrir `Destiny-Explained-Studio/remotion/out`, puis le menu de téléchargement.
Vérifier la vidéo sur Android avant publication. Elle est silencieuse tant qu'une
narration n'a pas été ajoutée ; le guide ne génère pas de voix.

## Dépannage

- Erreur Node : vérifier que chaque cellule Bash utilise le `PATH` ci-dessus.
- Navigateur absent : relancer `npm run browser:ensure` dans `remotion/`.
- Bibliothèque `.so` manquante : vérifier la cellule d'installation système et
  conserver le nom exact de la bibliothèque signalée pour le diagnostic.
- Échec réseau : Colab doit joindre GitHub, le registre npm, nodejs.org, les dépôts
  Ubuntu et le serveur de téléchargement Chromium utilisé par Remotion.
- Sortie absente : vérifier que la cellule de rendu s'est terminée sans erreur.

Ces cellules documentent le parcours Colab ; un test dans un autre environnement
Linux ne constitue pas une validation de l'interface Android ou des quotas Colab.
