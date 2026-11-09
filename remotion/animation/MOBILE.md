# Créer une séquence voxel depuis Android

1. Ouvrir **Storyboard Shorts**, puis **Démo Riis 0.7**. Les démos 0.5 et 0.6 restent disponibles.
2. Choisir un plan voxel. Déplier **Voxel Animation Studio 0.7** ; sur un projet ancien, toucher **Activer le Blocking Studio**. Cette activation conserve les personnages historiques.
3. Ajouter un civil, ancien ou archétype moderne du pack. Sur Riis ancien, garder les civils et l’ancien ; les rangs modernes déclenchent des avertissements de cohérence. Les silhouettes et costumes sont des reconstitutions.
4. Sélectionner un personnage, saisir position X/Y/Z, orientation, début et durée en images. Aucun glisser-déposer n’est requis. Les boutons et champs fonctionnent au toucher ; annuler/rétablir conserve les essais.
5. Choisir l’animation du rig, ses proportions et sa seed. **Ajouter une action rig** utilise une période libre ; régler animation, début, durée et fondu. Les actions ne doivent pas se chevaucher.
6. **Créer un déplacement**, régler sa vitesse puis les points et pauses. Une trajectoire de base reste nécessaire pour guider un suivi. Le mouvement est déterministe, pas une navigation autour du décor.
7. Ajouter une relation, cocher ses participants et choisir une cible dans la liste ou un point numérique. Les périodes doivent tenir dans la vie des participants et de la cible. Les relations sont évaluées dans l’ordre affiché. Une relation de regard vise la tête ; une relation « faire face » tourne le corps.
8. Choisir le cadrage, cocher les personnages importants, régler marge et côté. Pour un champ/contrechamp, dupliquer le plan puis inverser gauche/droite. Les personnages non sélectionnés peuvent rester hors champ.
9. Saisir **Frame locale à prévisualiser**, toucher **Prévisualiser cette frame**. Le lecteur partagé se place à la bonne frame globale, avec les mêmes poses que le rendu. Recharger après une édition. L’aperçu réduit les mouvements selon la préférence système et peut alléger les détails.
10. Enregistrer localement puis exporter régulièrement le JSON complet. Les rigs et relations restent archivés lorsqu’un plan devient graphique, et sont restaurés au retour au voxel. La copie pour rendu annonce les champs de brouillon écartés ; aucune suppression silencieuse.

## Voix et plusieurs plans

La démo garde 35 secondes, le script anglais, les 64 mots et les sources historiques. La conclusion occupe maintenant trois plans (timeline, graphique et texte) avec un **groupe vocal continu** : Kokoro synthétise la phrase complète, puis les timestamps restent contrôlés plan par plan.

Le panneau **Narration continue entre plusieurs plans** montre les groupes, permet de les dissocier ou de regrouper le plan courant et le suivant. Les groupes doivent être contigus et sans doublons. Réordonner/supprimer un plan peut demander de refaire le groupe ; une erreur est signalée. Aucun audio n’est coupé ni accéléré pour masquer une durée insuffisante.

Le WAV/MP3 local d’aperçu 0.6 reste facultatif et en mémoire uniquement. Il ne part sur aucun serveur et n’est pas dans le JSON. Pour un aperçu exact, importer le WAV correspondant au JSON prêt aligné. Après rechargement du site, sélectionner de nouveau le fichier audio.

## Colab gratuit

Ouvrir [Editor-Colab sur main](https://colab.research.google.com/github/Alexanst54/Destiny-Explained-Studio/blob/main/remotion/tts/Editor-Colab.ipynb). Pendant la revue, choisir la branche **feat/voxel-animation-0.7** dans le notebook de cette branche. Le défaut reste main après fusion humaine ; Pages reste main /docs.

Exporter la copie pour rendu, importer le fichier dans Colab, générer Kokoro puis le MP4. Le regroupement vocal est pris en charge par le même script Python, sans service externe. Télécharger MP4, JSON prêt et rapports avant la fin de session.

Sortie : 1080×1920, 30 fps, H.264/AAC, SwiftShader CPU. Commencer par un petit cast et le profil draft, puis vérifier balanced/final. Les recommandations mesurées et la portée des mesures se trouvent dans [REPORT.md](REPORT.md). L’aperçu n’est pas un estimateur garanti de temps ou mémoire Colab.

Android physique et Colab distant ne sont pas assimilés aux tests Chromium tactiles et au rendu Linux local. Les limites réelles de validation figurent dans le rapport.
