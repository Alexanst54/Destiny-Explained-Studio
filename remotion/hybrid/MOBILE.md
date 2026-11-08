# Créer un Short sur téléphone

Le [guide de l’interface Pages](../../docs/HYBRID-GUIDE.html) décrit le parcours sans code. L’éditeur est toujours publié depuis **main /docs**.

1. Ouvrir **Storyboard Shorts**. Choisir un modèle parmi Did You Know?, The Story of…, Destiny Mysteries, Timeline, What If? et Character Origins ; saisir un sujet et un script anglais. Un script en un seul paragraphe est réparti sans ajouter de faits ; plusieurs paragraphes deviennent les passages éditables. Remplacer toutes les invites de modèle avant publication.
2. **Créer le storyboard**, puis sélectionner les plans avec les boutons numérotés. **Monter**, **Descendre**, **Dupliquer**, **Ajouter** et **Supprimer** fonctionnent au toucher. La suppression exige confirmation ; les données d’un ancien type restent dans l’archive lors d’un changement de type.
3. Régler durée, narration, texte et transition. Pour un voxel, ouvrir les boutons Atlas, personnages/animations et météo existants. Pour les caméras détaillées, revenir à l’éditeur Épisode. Le bouton Storyboard Shorts ramène au montage.
4. Pour une carte, sélectionner les lieux Atlas, étiquettes, positions schématiques, trajets et zooms. Pour une timeline, renseigner périodes, dates attestées seulement, confiance et références. Pour un graphique, éditer les cartes d’information.
5. Associer les sources existantes depuis leur sélecteur, ou ajouter une référence HTTPS. Vérifier le statut canon/reconstitution/hypothèse et tous les avertissements historiques. Les références peuvent nécessiter une consultation externe en ligne.
6. Choisir un style de captions et une zone sûre. Les pistes audio locales sont facultatives : renseigner auteur/licence, volume, période et ducking. Tout fonctionne sans elles.
7. **Charger l’aperçu** : lecture et déplacement dans le film par les contrôles du lecteur. La narration reste silencieuse avant Colab ; les captions sans timestamps sont explicitement estimées. Modifier puis recharger l’aperçu pour prendre en compte les changements.
8. **Enregistrer le Short**, **Exporter Short JSON** pour l’archive, puis **Copie Short pour rendu**. Corriger toute erreur avant le transfert. Les champs supplémentaires de l’archive ne sont pas supprimés du projet enregistré.
9. Ouvrir Colab, exécuter l’installation CPU puis importer la copie pour rendu. Kokoro remplit les budgets de chaque plan ; si le texte dépasse, raccourcir ce passage ou allonger le plan dans le formulaire. Le moteur refuse de couper ou d’accélérer la voix pour masquer ce dépassement.
10. Télécharger le MP4 et le JSON prêt. Réimporter le JSON prêt sur le téléphone pour prévisualiser les captions horodatées. Le WAV Colab n’est pas automatiquement hébergé dans Pages : la prévisualisation de la narration reste silencieuse ; la voix est présente dans le MP4.

Les exemples **Démo Riis**, **Démo Oryx** et **Démo Jardin noir** sont disponibles directement dans le storyboard. Riis dure 35 s ; les deux autres durent 20 s et ne sont pas des démonstrations de motivations non attestées.

Après une première installation en ligne réussie, le service worker conserve les formulaires, catalogues et lecteur pour le rechargement hors ligne. Exporter régulièrement : la suppression des données du navigateur supprime aussi la sauvegarde locale. Ne pas confondre les tests tactiles Chromium réalisés avec un essai sur un téléphone physique.

## Extensions 0.6

Les nouveaux panneaux restent facultatifs. Voir le [guide Visual Polish](../polish/MOBILE.md) pour les captions, caméras, personnages, atmosphères, voix locale d’aperçu et comparaison avant/après. La démo 0.5 et les projets historiques sont conservés.
