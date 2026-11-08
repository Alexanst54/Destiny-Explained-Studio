# Monter Riis 0.6 sur téléphone

1. Ouvrir **Storyboard Shorts**, puis **Démo Riis 0.6**. L’ancienne démo Riis reste disponible pour comparer les 35 secondes et le script inchangés.
2. Sélectionner un plan avec ses boutons numérotés. Les panneaux repliables conservent leur état. Monter/descendre remplace le glisser-déposer ; annuler/rétablir couvre aussi les effets.
3. Déplier **Captions** : choisir un des quatre styles 0.6, taille, couleurs, marges et mots à souligner. La narration et ses timestamps restent inchangés. La validation du contraste et les conseils de densité aident à relire, sans certifier une interface TikTok future.
4. Déplier **Caméra cinématique** : préréglage, intensité, période et courbe. Les cibles écran sont des pourcentages ; les cibles monde sont des coordonnées artistiques locales, jamais astronomiques.
5. Pour un plan voxel, régler **Personnages expressifs** et **Atmosphère**. Les animations marche/course/fuite et trajectoires de base restent celles de Living Worlds. Réduire la variation de costume à zéro pour garder sa palette de base.
6. Régler les budgets et la qualité d’aperçu. Draft allège les effets, sans retirer de personnage. **Avant effets / Après effets** conserve la position de lecture et n’efface aucun paramètre.
7. Choisir documentaire, mystérieux, épique ou explicatif dans les conseils. Ils ne changent rien au scénario et ne prédisent aucune viralité.
8. Sauvegarder localement et exporter régulièrement le JSON complet. Les brouillons de type de plan et champs inconnus restent archivés.

## Entendre la narration localement

Importer facultativement un **WAV ou MP3** depuis le téléphone (50 Mio maximum). Le lecteur utilise un URL `blob:` en mémoire, sans envoi réseau, sans insertion dans le JSON ni sauvegarde du fichier. L’import est facultatif ; l’aperçu silencieux reste disponible.

Charger l’aperçu, toucher Lecture/Pause, choisir un temps ou aller au début du plan. La voix suit l’horloge du même lecteur Remotion. Le contrôle Silence coupe toutes les pistes de l’aperçu. Un écart entre durée du fichier et durée du projet est signalé ; le studio n’étire pas le fichier. Pour une synchronisation exacte, importer la narration Kokoro correspondant au **même script** et réimporter le JSON prêt contenant ses mots alignés. Un fichier arbitraire ne réaligne pas les captions. Le navigateur peut demander un toucher pour autoriser la lecture.

Le fichier doit être resélectionné après rechargement. Un MP3 peut présenter une latence de décodage propre au navigateur ; les essais exécutés sont Chromium Linux tactile, pas Android physique. Kokoro Python ne tourne jamais dans Pages.

## Colab et export

Utiliser [Editor-Colab sur main](https://colab.research.google.com/github/Alexanst54/Destiny-Explained-Studio/blob/main/remotion/tts/Editor-Colab.ipynb). Pendant la revue, ouvrir le même notebook sur la branche `feat/viral-editing-0.6` et choisir cette valeur dans REF. Le défaut reste main, sans changement de publication Pages.

Importer la copie pour rendu, générer Kokoro, rendre puis télécharger MP4 et JSON prêt. La voix d’aperçu locale n’est pas transférée : Kokoro produit la narration finale. Le rendu reste 1080×1920, 30 fps, H.264/AAC, CPU SwiftShader. Les démonstrations n’exigent ni musique, ni ressource externe. Voir le [parcours Colab existant](../hybrid/COLAB.md) pour l’installation et le cache hors réseau.
