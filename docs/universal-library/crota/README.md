# Cropta — lot B, prototype dédié partiel

Modèle original et arène `oversoul-throne`, reliés aux rencontres de Cropta D1/D2 dans l’Atlas existant. **Ce prototype n’est pas déclaré artistiquement terminé ni validé par l’utilisateur.** Athéon et le Templier ne changent pas.

Repères travaillés : trois yeux, crâne à épines, épaules osseuses dentelées, cage thoracique ouverte, âme verte, grandes griffes et énorme épée recourbée. Aucun modèle ni texture extrait du jeu. Les [références visuelles consultées](../../../remotion/blender/universal/crota-visual-references.json) sont des liens et empreintes ; leurs images restent hors du dépôt et ne sont jamais utilisées par les shaders.

| Vue | Vrai rendu Blender |
| --- | --- |
| Face | ![Cropta de face](front.png) |
| Trois quarts | ![Cropta de trois quarts](three-quarter.png) |
| Silhouette monochrome | ![Silhouette de Cropta](silhouette.png) |
| Trône de l’Âme | ![Cropta dans son arène](environment.png) |

**Animation Balanced en cours de rendu CPU.** Elle sera ajoutée avec ses preuves après validation des 24 frames ; aucune animation terminée n’est annoncée dans ce checkpoint.

Les quatre fixes sont Cinematic, 640×800, LOD0, Cycles128 maximum ; le clip utilise Balanced48 maximum. Graine 42, Blender officiel 4.3.2, débruitage OIDN, AgX. CPU AMD EPYC 9V74, trois threads, GPU absent. Les durées et pics RSS du processus sont dans les rapports techniques associés aux PNG (le manifeste final sera ajouté après le clip), avec matrices caméra, hashes et réglages effectifs. Pas de mesure VRAM ni gain GPU revendiqué.

Géométrie : **4143 / 922 / 294** pièces pour les LOD0/1/2, **18 articulations** stables. Arène : **2599 / 943 / 499** pièces. Matériaux de chitine/minéral/âme propres à Cropta, microrelief procédural sans texture d’image. Les grandes architectures en arcs et l’Âme suspendue constituent une interprétation artistique, pas une carte exacte.

Animations disponibles : `idle`, `move`, `attack`, `reveal`. `move` est un déplacement flottant de mise en scène, **pas une marche avec contact au sol ni un solveur IK**. Le test Blender vérifie 192 évaluations, l’accès hors ordre, la stabilité des ressources et l’absence de débordement du modèle dans les trois cadrages anatomiques. Aucun contact physique parfait ni combat simulé revendiqué.

Limites artistiques : volumes encore très anguleux ; épaule et casque demandent une passe supplémentaire de distinction osseuse, et l’enveloppe spectrale reste une interprétation par émissions et éclats géométriques, sans tissu/fluide simulé. Le ciel de l’arène est simplifié ; l’Âme est un assemblage géométrique lumineux, sans effet volumétrique spécifique de sphère. L’arène ne couvre pas les autres rencontres du raid. Les autres boss du lot B restent manquants ; ils ne reçoivent pas ce modèle par renommage.

```sh
python remotion/blender/render_universal.py boss-crota work/crota-front --view front --quality cinematic --lod 0 --width 640 --height 800
python remotion/blender/render_universal.py boss-crota work/crota-attack --view environment --animation attack --quality balanced --lod 0 --width 480 --height 360 --frames 24 --fps 24 --video
python remotion/blender/universal/verify_crota.py
blender --background --factory-startup --python-exit-code 1 --python remotion/blender/universal/crota_blender_check.py
```

Ajouter `--blender /chemin/blender` si nécessaire. Pour reprendre, conserver les sources et options puis ajouter `--resume`. Colab/T4/Android non exécutés ; le guide du lot A donne le protocole de test.
