# Programme de travail v1.0

Un même programme couvre les lots A à F ; aucune nouvelle instruction par boss n’est nécessaire. Les PR sont des points de revue, sans fusion automatique. Une implémentation n’est promue que sur preuves spécifiques, jamais sur l’existence d’un template partagé.

| Lot | État initial de cette livraison | Critère de sortie |
| --- | --- | --- |
| A — Infrastructure | Registre, jointures Atlas, sélection, cache/reprise et dix études implémentés ; validation GPU restante | Tests, intégrité des médias, relations et absence de fallback générique |
| B — Emblématiques | Cropta : prototype dédié partiel, grille de rendu en revue ; Oryx, Rhulk, Nezarec, Témoin, Riven restent manquants | Chaque identité : géométrie/rig propres, quatre vues et animation, inspection de silhouette, arène sourcée |
| C — Autres raids | Backlog issu des rencontres ; Taniks/formes, Aksis, Calus, Atraks-1, Golgoroth, Gahlran, Insurrection Prime prioritaires | Formes physiques, projections, mécanismes et collectifs traités distinctement |
| D — Donjons | 11 donjons documentés ; modèles et arènes manquants visibles dans l’index | Géométrie propre et preuves par rencontre principale |
| E — Autres activités | Assauts/missions exotiques documentés partiellement ; campagnes à étendre | Sources relues et vrais assets, pas de couverture déclarative |
| F — Intégration | Galerie/sélection JSON additionnelles, grilles Vex et prototype Cropta ; éditeur historique intact | Export vidéo intégré, grille complète et test réel T4/Colab/Android |

Pour chaque boss : lire les sources épinglées et les liens Atlas, examiner des références visuelles sans importer de ressources propriétaires, définir les repères de silhouette et morphologie, construire un générateur dédié avec LOD explicite, rig adapté et poses déterministes, développer l’arène, rendre face/trois-quarts/silhouette/environnement/animation dans Blender, inspecter les images et consigner les limites. L’index conserve les manquants et les preuves incomplètes.

Le backlog n’assimile pas 128 entrées à 128 individus. Les 25 formes ont leur propre statut ; aucune n’hérite silencieusement du modèle parent. Les relations conditionnelles et les sources du catalogue restent disponibles dans les exports. **Savathûn n’a pas d’entrée actuelle** : recensement sourcé à effectuer, sans inventer un ID de binding.

Limites de ressources : environnement de travail CPU seulement (3 threads). Les lots progressent dans l’ordre des preuves disponibles ; le programme reste explicitement incomplet tant que tous les critères ci-dessus ne sont pas atteints. Ne pas produire des dizaines de robots génériques pour gonfler artificiellement la couverture.

## Suite du lot B

Cropta est développé sur `feat/library-crota-lot-b-1.0`, en PR empilée ciblant la branche d’intégration du lot A. Sa grille technique ne constitue pas une approbation artistique : le statut reste partiel et les autres boss restent manquants. Les limites de morphologie, d’enveloppe spectrale et de mouvement sont consignées dans la galerie. Le planificateur `universal/batch.py` produit automatiquement la grille des modèles enregistrés et le backlog des 150 autres entrées boss/formes ; les prototypes demandent un opt-in explicite.
