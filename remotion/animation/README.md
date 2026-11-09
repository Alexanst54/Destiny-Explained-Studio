# Voxel Animation Studio 0.7

Extension facultative de Living Worlds, Hybrid Shorts et Visual Polish, sans changement de moteur, dépendance, asset propriétaire, backend ou GPU obligatoire.

[Guide téléphone/Colab](MOBILE.md) · [Rapport](REPORT.md) · [Comparaison](COMPARISON.md) · [Inspection](INSPECTION.md) · [Inventaire](FILES.md)

## Rig et animation

`livingWorld.cast[].rig` et `groups[].member.rig` activent un modèle distinct. Sans rig, le composant historique et ses calculs restent utilisés. Les entités dont la forme est inconnue ne peuvent pas recevoir un rig inventé. Les modèles non humanoïdes historiques conservent leur renderer ; seul le Servitor bénéficie ici d’un nouveau rig dédié.

`rig.ts` définit une hiérarchie parent/enfant : bassin → torse → tête/épaules ; bassin → hanches → genoux → pieds ; épaules → coudes → mains. Deux chaînes de bras pour Dreg/humanoïde, quatre pour les autres Éliksni. Chaque chaîne est indépendante. Le Servitor est une sphère flottante à œil et anneau, sans membres. Ses gestes sont adaptés en orientation, inclinaison, flottement et descente ; « kneel » signifie une descente stylisée, jamais des genoux inventés. La cinématique directe pure fournit les positions d’articulations pour les tests et futurs outils d’attache.

16 animations : idle, walk, run, sprint, stop, turn, look-around, point, talk-gesture, react, fear, flee, fall, kneel, celebrate, look-at-sky. Les frames sont locales à l’acteur, à 30 fps. Les clips sont ordonnés, sans chevauchement ; leur entrée et sortie interpolent vers l’animation de base. Aucune horloge indépendante ni intégration physique. Le chemin réutilise les pauses et l’interpolation 0.6 ; le cycle locomoteur s’atténue à l’arrêt, sans éteindre un geste de tête indépendant. Seeds et phases donnent des décalages reproductibles aux groupes.

Les proportions `height`, `width`, `limbLength`, la taille du cast, la palette et les équipements sont conservés. Les réglages 0.6 de director apportent leurs différences de pose et de costume au nouveau rig. Les overrides d’animation de plan existants sont traduits vers les animations homologues du rig ; les clips explicites du rig restent prioritaires. Les noms non homologues utilisent un geste stylisé documenté dans `director.ts` (ex. terminal → talk-gesture), sans prétendre ajouter une interaction détaillée avec un terminal. Les personnages sans rig conservent leur comportement exact.

## Pack éliksni et fidélité

| Archétype | Morphologie | Sources / portée |
| --- | --- | --- |
| Dreg | Deux bras | Destinypedia Dreg, docking ; modèle moderne, ne pas projeter ce traitement social automatiquement sur Riis ancien |
| Vandal | Quatre bras | Destinypedia Vandal et Fallen ; silhouette de soldat, équipement artistique |
| Captain | Quatre bras, silhouette large | Destinypedia Captain et Fallen ; aucune taille numérique canonique revendiquée |
| Servitor | Machine sphérique flottante | Destinypedia Servitor ; pas un humanoïde |
| Civil | Quatre bras, tenue simple | Référence Fallen, reconstruction artistique |
| Ancien | Quatre bras, manteau et bâton | Rôle communautaire artistique ; aucun grade ni costume officiel affirmé |

Les cinq nouvelles entrées du registre réutilisent son contrat 0.4 ; le civil existait déjà. Les références ont été consultées le 2026-11-08. Les nouvelles fiches militaires emploient une variante de reconstitution moderne ; les dates de première apparition restent inconnues. Les liens Atlas ne sont pas remplis artificiellement. La démo de Riis n’emploie que civils et ancien, jamais les rangs militaires modernes. Tous les personnages restent des abstractions originales signalées comme telles.

## Relations et héritage

`livingWorld.studio` : version 1, profil, séparation, interactions et caméra. Un `shot.livingWorld.studio` remplace l’objet de scène en entier ; omission = héritage, `interactions: []` = aucune relation dans cet objet. Les cast/groupes continuent d’obéir aux règles 0.4. La validation vérifie les identifiants et périodes **après résolution scène/plan**, y compris les membres générés `groupe:0`.

Neuf relations : look-at, face, walk-together, follow, react, point, form, disperse, flee. `actors` contient des IDs de personnages munis du rig. `targetId` désigne un autre acteur ; look-at/point acceptent aussi un prop ou `targetPoint`. `startFrame`, `durationFrames`, `transitionFrames`, `spacing`, `intensity` sont bornés. Une cible manquante/inactive ou une période hors scène/acteur provoque une erreur explicite.

Les relations sont appliquées dans l’ordre du tableau ; les dernières affinent/remplacent les canaux précédents. Elles ont une enveloppe d’entrée/sortie et reviennent aux trajectoires de base à la fin. Le suivi échantillonne la trajectoire analytique du guide avec 12 frames de retard ; les suiveurs prennent des places latérales et des rangées derrière lui. Ce n’est pas un graphe récursif de simulation : le guide est évalué sur sa trajectoire de base. Pour une chaîne complexe, définir explicitement les chemins de chaque guide.

Deux passes spatiales repoussent les rigs trop proches, depuis les positions de cette frame seulement. Les acteurs historiques sans rig restent des obstacles fixes, pas des personnages déplacés implicitement. Aux bords, dans un groupe dense ou pour de très grandes silhouettes, des chevauchements restent possibles. Pas de navmesh, détection d’obstacles du décor, collision de membres ou garantie d’absence totale de pénétration.

## Cadrage

Huit modes : actor, two-shot, follow, group, reaction, reverse, reveal, wide-close. Cibles explicites, période, marge, intensité et côté. Les boîtes conservatrices incluent tête/bras et une réserve basse pour les captions. Le cadrage 0.7 prend progressivement la priorité sur position/cible de la caméra 0.6 pendant sa fenêtre, conserve son FOV et revient à sa base aux bords. Les anciens réglages restent dans le JSON ; leurs offsets de position ne s’additionnent pas une fois le cadrage pleinement actif. Il ne garantit pas tous les gestes et proportions extrêmes. Les personnages hors sélection peuvent rester hors champ. Le champ/contrechamp est un choix gauche/droite, pas une règle des 180° automatique. Pour une coupe, dupliquer le plan puis choisir l’autre côté.

La réduction des mouvements fige le nouveau cadrage et la caméra de base pendant le plan, et réduit les mouvements secondaires du rig ; marche et actions nécessaires au récit restent lisibles. Les captions utilisent toujours les mêmes composants et timestamps.

## CPU et qualité

Une géométrie de cube et de sphère partagée, matériaux mémorisés par personnage/palette et hiérarchie mise en cache dans React. Aucun chargement de modèle externe. Les poses sont calculées une fois pour la population courante puis partagées avec la caméra et le renderer. Les relations ne parcourent que leurs participants ; la séparation est bornée à 32 acteurs et deux passes quadratiques. Les deux passes sont spatiales, indépendantes de l’ordre de rendu des frames.

Draft : géométrie principale. Balanced : visage, vêtements et accessoires simples. Final : petits détails de mains/yeux quand proche. À plus de 13 unités caméra, final passe au détail balanced ; à plus de 22, les deux passent au principal. La qualité d’aperçu 0.6 peut imposer draft. Aucun personnage supprimé. La limite effective de 32 reste une erreur bloquante, pas une troncature. Les recommandations mesurées figurent dans le rapport, pas dans une limite prétendument universelle pour Colab.

## Voix sur plusieurs plans

`audio.voiceover.groups` est une liste facultative de listes d’IDs de plans contigus. Le pipeline Kokoro synthétise chaque groupe comme une phrase continue, puis valide toujours chaque mot contre son plan. Les anciens projets sans groupe sont inchangés. Un changement de montage peut rendre les groupes invalides : le studio indique l’erreur au lieu de les supprimer. Aucun mot coupé, accéléré ou retimé automatiquement.

## Exemple de fragment JSON

À placer dans `scene.livingWorld` d’un plan voxel de 210 frames ; les valeurs par défaut du schéma complètent les champs omis. Les frames sont locales à la scène. Les animations sont des poses : le déplacement et l’arrêt spatial se règlent par les trajectoires et leurs pauses.

```json
{
  "mode": "reconstruction",
  "era": "pre-whirlwind",
  "cast": [
    {
      "id": "guide",
      "characterId": "eliksni-elder",
      "variantId": "reconstruction",
      "position": [-1, 0, -3],
      "durationFrames": 210,
      "rig": {"version": 1, "archetype": "elder", "animation": "point"}
    },
    {
      "id": "resident",
      "characterId": "eliksni-civilian",
      "position": [1, 0, -3],
      "durationFrames": 210,
      "rig": {"version": 1, "archetype": "civilian", "animation": "talk-gesture"}
    }
  ],
  "studio": {
    "version": 1,
    "profile": "balanced",
    "interactions": [
      {
        "id": "conversation",
        "kind": "face",
        "actors": ["resident"],
        "targetId": "guide",
        "startFrame": 0,
        "durationFrames": 210
      }
    ],
    "camera": {
      "mode": "two-shot",
      "targets": ["guide", "resident"],
      "durationFrames": 210
    }
  }
}
```
