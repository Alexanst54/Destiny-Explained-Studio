# Validation de la bibliothèque voxel — 8 novembre 2026

Branche `feat/voxel-environment-library`, issue de `main` (`70bd74e`). Node 22.23.4, Remotion 4.0.541, Python 3.12 / dépendances Kokoro existantes. Aucun changement de dépendance, de workflow Actions, de serveur ou de service requis.

## Vérifications réussies

- `npm run typecheck`.
- **30 tests Node** : `test:voxel` (3), `test:episode` (6), `test:cinematic` (6), `test:library` (6), `test:editor` (9).
- **6 tests Python** : `npm run test:narration`.
- `npm run test:editor:browser` avec Chromium système : largeurs 320, 360, 393 et 1280 ; import/export, stockage/rechargement, JSON invalide, champs inconnus, refus du stockage, sélection Europe au niveau scène puis Jardin noir au niveau plan, ajout de neige/tempête, nombre de particules, déclaration automatique des décors, copie de rendu, liste de plan vide et retour à l’héritage. Aucune erreur JavaScript de page.
- `npm run editor:build`, puis `npm run editor:check` : bundle `docs/assets/editor.js` régénéré ; empreintes des schémas, du catalogue et des deux modèles mises à jour.
- Les deux anciens épisodes JSON restent acceptés avec leurs 1800 images et leurs champs historiques. Les tests comparent également les anciennes données parsées en tenant compte des valeurs par défaut d’ancrage déjà présentes avant cette PR.
- L’adaptateur `scripts/import-editor.mjs` accepte le JSON de démonstration sans écarter de champ. Sa sortie est acceptée par `scripts/episode.mjs validate --preview`.
- `Editor-Colab.ipynb` : JSON et syntaxe de chaque cellule Python/bash vérifiés. La logique d’import/narration/rendu reste générique ; seule la référence de checkout est actualisée pour tester la branche avant fusion.
- Image réelle de la composition historique `VoxelEpisode` à l’image 1310 : rendu réussi avec l’ancien épisode 002.
- `git diff --check`.

## Rendu réel avec narration

```sh
npm run narrate:worlds
npm run render:worlds -- --browser-executable=/usr/bin/chromium
python scripts/verify_narration.py --episode out/voxel_worlds_demo-ready.json --video out/voxel-worlds-demo.mp4
```

Le CLI conserve `--gl=swangle` (SwiftShader logiciel), concurrence 1. Les quatre décors ont été inspectés dans des images réelles ; Tour en preview à l’image 30, puis images extraites du MP4 pour Europe (5 s), Jardin (9 s) et Pyramide (13 s).

Résultat : `remotion/out/voxel-worlds-demo.mp4`, **7 191 311 octets**, **1080 × 1920**, **30 fps**, **480 images**, **16,000 s**, vidéo H.264 et audio AAC. Le MP4, les WAV, les images et les rapports restent dans les chemins générés ignorés par Git ; aucun binaire de rendu ajouté au dépôt.

Kokoro `af_heart`, vitesse **1×**, quatre WAV de scène et **27 mots horodatés** :

| Scène | Durée parlée réelle | Budget |
| --- | ---: | ---: |
| Tour / Dernière Cité | 2,900 s | 4,000 s |
| Europe | 3,350 s | 4,000 s |
| Jardin noir | 3,350 s | 4,000 s |
| Intérieur de Pyramide | 3,325 s | 4,000 s |

Total parlé : **12,925 s**. La piste complétée mesure **16,000 s**, comme le flux vidéo et l’audio encodé. Les 27 mots ont un signal audio mesurable ; validation de leur ordre et de leur appartenance à chaque scène réussie. Comparaison WAV source / AAC décodé sur les fenêtres du vérificateur existant : décalage mesuré **0 ms** dans les quatre scènes, corrélations **0,99738–0,99970**.

## Limites

- Rendu et génération Kokoro exécutés dans l’environnement de travail, **pas dans une session Google Colab réelle**. Le notebook et son pipeline générique ont été vérifiés, mais la disponibilité et la vitesse d’une session gratuite restent variables.
- L’alignement mot à mot vient des durées phonémiques prédites par Kokoro, comme avant cette PR. La comparaison AAC confirme l’absence de dérive de l’encodage ; elle ne constitue pas une annotation humaine indépendante de chaque frontière de mot.
- Tests mobiles effectués par émulation Chromium, pas sur téléphone physique. Sa politique bloque les téléchargements `blob:` : le test capture le véritable contenu du Blob et neutralise le clic, sans contourner la politique. L’enregistrement effectif sur Android reste à vérifier.
- `remotion browser ensure` n’a pas pu télécharger son navigateur par sa connexion directe dans cet environnement. Le rendu a effectivement fonctionné avec `/usr/bin/chromium` et SwiftShader ; aucune modification du moteur n’a été nécessaire pour ce choix. Le notebook conserve son installation Remotion habituelle.
- Les avertissements Node `MODULE_TYPELESS_PACKAGE_JSON` préexistants restent non bloquants. Les ressources 3D sont procédurales et bornées, mais multiplier les personnages et les effets allonge les rendus CPU. Les décors et accessoires sont stylisés et n’utilisent pas de modèles officiels Destiny.
