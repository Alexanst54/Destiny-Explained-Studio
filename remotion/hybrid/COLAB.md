# Rendre un Short avec Colab gratuit

Utiliser le [notebook Editor-Colab sur main](https://colab.research.google.com/github/Alexanst54/Destiny-Explained-Studio/blob/main/remotion/tts/Editor-Colab.ipynb). Aucun GPU ou compte de service payant n’est nécessaire. GitHub Pages reste main /docs.

Pendant la revue de la PR 0.7, utiliser [le notebook de la branche 0.7](https://colab.research.google.com/github/Alexanst54/Destiny-Explained-Studio/blob/feat/voxel-animation-0.7/remotion/tts/Editor-Colab.ipynb) et sélectionner `feat/voxel-animation-0.7` dans le formulaire REF. Après fusion humaine, le choix par défaut reste `main`.

1. Choisir l’environnement **CPU** et exécuter les cellules dans l’ordre.
2. La cellule d’installation prépare Node 22.23.4, FFmpeg, Kokoro/PyTorch CPU, les dépendances JavaScript, le navigateur et les trois ressources Kokoro verrouillées par la révision du projet. Cette phase nécessite Internet.
3. Importer un seul JSON, maximum 2 Mio, exporté par l’éditeur. Aucune modification manuelle du JSON n’est nécessaire.
4. Le parcours conserve les commandes `import-editor.mjs`, `narration.py` et `render:episode`. La composition est choisie depuis le projet : HybridShort pour 0.5–0.7, compositions historiques pour les anciens fichiers.
5. La cellule de traitement vérifie le cache Kokoro puis utilise `HF_HUB_OFFLINE=1`. Les médias facultatifs doivent être embarqués ou déjà présents localement ; aucun téléchargement audio externe ne se produit pendant le rendu.
6. Si Kokoro dépasse une durée, corriger le texte ou la durée dans le storyboard puis réexporter. Aucun raccourci par coupe ou accélération automatique.
7. Télécharger le MP4, le rapport d’import et le JSON prêt, qui embarque les mots alignés des projets 0.5–0.7. Les démos n’ont besoin d’aucune musique.

Sortie : H.264/AAC, 1080×1920 à 30 fps. Les paquets AAC peuvent ajouter quelques millisecondes de fin ; le contrôle vérifie la durée et la corrélation avec le WAV source. Le réglage CPU par défaut reste une concurrence de 1, avec SwiftShader. Réduire la population et les particules dans l’éditeur si la session est lente ; l’aperçu brouillon réduit uniquement sa résolution interne, pas le format final.

**Validation réalisée** : rendu CPU local dans l’environnement Linux géré, avec le pipeline et les dépendances du dépôt. **Non réalisé** : exécution dans une session Google Colab distante ou sur Android physique. Les limites de durée et mémoire des sessions Colab gratuites varient.

Le notebook conserve la réparation `virtualenv` de main. Les sorties d’exécution anciennes des cellules modifiées sont vidées pour ne pas laisser croire que le nouveau code a déjà été exécuté dans Colab.

## Qualité 0.6 et voix locale

Les paramètres finaux `shorts.polish.quality`, `particleBudget` et `detailBudget` sont importés avec le projet. Draft réduit les effets sans retirer de personnage ; la limite de 32 reste une erreur bloquante si dépassée. Le WAV/MP3 de prévisualisation mobile reste uniquement dans le navigateur : le notebook génère sa propre narration Kokoro. Le JSON prêt peut ensuite être réimporté avec ses timestamps. [Guide 0.6](../polish/MOBILE.md).

## Animation 0.7

Le rig, les relations et les caméras sont facultatifs et importés avec le JSON. Les groupes vocaux contigus sont synthétisés sans couper ni accélérer la narration ; les frontières des mots restent validées contre chaque plan. [Guide 0.7](../animation/MOBILE.md).
