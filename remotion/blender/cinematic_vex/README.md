# Cinematic Vex Overhaul — 0.9.1

Refonte procédurale originale d’Athéon, du Templier et du Trône de verre, issue de PR #20. Les IDs Atlas et les fonctions `characters.vex_bosses.generate` / `pose` sont conservés ; les anciennes animations restent disponibles et `reveal` s’ajoute. Les épisodes, moteurs historiques, Kokoro et sous-titres ne changent pas.

[Direction artistique et sources](ART-DIRECTION.md) · [Comparatifs et vrais rendus](../../../docs/previews/cinematic-vex-0.9.1/README.md)

## Rendre un asset

Python 3.11.8+, Blender **4.3.2 officiel** avec Cycles/OpenImageDenoise, ffmpeg pour les clips. Depuis la racine :

```sh
python remotion/blender/render_venus_vault.py boss-atheon work/atheon-front --lod 0 --quality cinematic --camera front --width 640 --height 800
python remotion/blender/render_venus_vault.py boss-atheon work/atheon-profile --lod 0 --quality cinematic --camera profile
python remotion/blender/render_venus_vault.py boss-atheon work/atheon-mechanisms --lod 0 --quality cinematic --camera mechanism
python remotion/blender/render_venus_vault.py boss-templar work/templar-cinematic --lod 0 --quality cinematic --camera front
python remotion/blender/render_venus_vault.py boss-atheon work/atheon-walk --lod 0 --quality balanced --animation walk --camera orbit --width 480 --height 360 --fps 24 --frames 48 --video
python remotion/blender/render_venus_vault.py boss-atheon work/atheon-time --lod 0 --quality balanced --animation temporal --camera temporal --width 480 --height 360 --fps 24 --start-frame 12 --frames 36 --video
```

Chaque sortie doit être un dossier neuf. Les PNG, logs et rapports sont conservés en cas d’échec ; un clip interrompu n’est pas automatiquement repris. `--device auto` conserve OPTIX/CUDA si disponible, sinon CPU, et journalise le backend effectivement utilisé. `--threads`, `--timeout` et `--blender` restent disponibles. Les MP4 de validation sont muets et ne changent aucune timeline existante.

## LOD explicite et qualité

| Réglage | Rôle |
| --- | --- |
| `lod=0` | Modèle complet : plaques, rainures, fixations, câbles et particules articulées |
| `lod=1` | Moins de lamelles, fixations et subdivisions ; même anatomie et mêmes contrôles |
| `lod=2` | Grandes masses et silhouette pour plans éloignés ; mêmes articulations |
| Draft / Balanced / Cinematic | Samples maximum 16 / 48 / 128, rebonds 3 / 5 / 7, débruitage et atmosphère |
| Résolution | Nombre de pixels uniquement ; **ne change jamais le LOD** |

Le défaut est **LOD 0**, même à 320×240 ou en Draft. Les modèles des deux boss et la géométrie du Trône conservent leurs objets/joints entre qualités de rendu ; la poussière atmosphérique et la brume peuvent varier. Vénus et le décor du Puits restent les générateurs précédents ; leur refonte LOD complète n’est pas revendiquée.

L’échantillonnage adaptatif Cycles utilise un seuil de bruit de 0,12 / 0,06 / 0,025, minimum huit samples. Les nombres annoncés sont des plafonds, pas la garantie que chaque pixel atteint ce nombre. Le rendu reste réellement Cycles ; aucune image de substitution n’est générée.

Les voxels sont fusionnés par matériau et articulation. Les matériaux sont partagés, avec usure/rugosité procédurale sans textures d’images. `instancing.compile_linked_boxes` fournit en complément un compilateur optionnel d’accessoires à mesh lié ; le renderer normal utilise les lots fusionnés. Le test Blender vérifie le partage effectif du mesh et les matériaux par instance. Les géométries et matériaux ne sont pas reconstruits entre les frames.

## Contrôles et animation

Athéon : `idle`, `walk`, `combat`, `temporal`, `reveal`. Templier : `idle`, `rotate`, `move`, `attack`, `reveal`. Caméras conservées : `wide`, `reveal`, `orbit`, `low-angle`, `close-up` ; ajout de `front`, `profile`, `ground-reveal`, `mechanism`, `temporal`.

La marche utilise un solveur analytique à deux segments, avec abduction de hanche et compensation quaternion du pied. Les cibles d’appui sont fixes dans le monde pendant 65 % du cycle ; le pied en déplacement suit une courbe lisse et se soulève. Le cycle dure 1,8 s, le corps avance à 2,4 m/s et le transfert latéral de poids reste compensé par les jambes. Le parcours est borné à deux cycles (3,6 s), puis maintient les pieds plantés dans le décor réutilisable. Ce système place les articulations ; il ne simule ni masse, ni collisions de combat.

Le plan nominal est à 1,25 m ; les plaques décoratives du Trône culminent à 1,28 m. La validation mesure cette différence de 3 cm sur les surfaces réelles (tolérance 4 cm), en plus du glissement d’appui et de l’erreur IK. L’impact visuel est examiné sur les rendus ; ce n’est pas une affirmation de contact physique parfait sur tout terrain arbitraire.

Les poses sont calculées directement depuis la frame, sans accumulation ni simulation dépendante de l’ordre. L’idle anime le torse et les émissions ; combat/temporal/reveal articulent les bras et le canon ; l’énergie tourne et s’amplifie. Le Templier anime séparément coque, segments ventraux, bouclier et canons. Les éclats d’attaque sont graphiques, sans calcul de projectile ou de dégâts.

## Comparaisons reproductibles

```sh
python remotion/blender/cinematic_vex/render_validation.py work/cinematic-comparisons --phase before --blender /chemin/blender
python remotion/blender/cinematic_vex/render_validation.py work/cinematic-comparisons --phase after --blender /chemin/blender
python remotion/blender/cinematic_vex/render_validation.py work/cinematic-comparisons --phase clips --blender /chemin/blender
```

`validation_shots.json` définit six paires Cinematic et deux clips Balanced. Le code « avant » est extrait du commit exact `b1fd922` dans un dossier de travail ; aucune branche n’est modifiée. Le comparateur enregistre les matrices de caméra, la focale, le capteur, les paramètres, les hashes et les temps réels. Les quatre vues anatomiques emploient un studio commun ; les arènes gardent leurs décors complets. Les versions récentes des sorties peuvent être reprises avec `--resume` après validation des sources, du cadrage et du PNG ; les rapports antérieurs sans signature exigent un dossier neuf. Une modification de générateur appelle une nouvelle validation.

Les preuves 0.9.0 restent intactes. `venus_vault/verify_evidence.py` vérifie leur conservation puis rejoue leur validation avec le code gelé de PR #20 ; elle ne compare pas leurs images aux nouveaux modèles. Un clone superficiel peut nécessiter `git fetch origin feat/venus-vault-blender-0.9.0 --depth=1` pour obtenir ce commit historique.

## Colab et tests

[Cinematic-Vex-Colab-Pro.ipynb](../Cinematic-Vex-Colab-Pro.ipynb) ajoute le choix LOD et les contrôles de cette branche. Le notebook 0.9.0 reste intact. Les formulaires sont utilisables sans terminal ; T4/Colab Pro/Android restent à valider sur ce matériel. Les mesures livrées sont CPU, sans revendication de gain GPU ou de VRAM mesurée.

```sh
python -m unittest discover -s remotion/blender/tests
node --experimental-strip-types --test remotion/tests/venus-vault.test.mjs
blender --background --factory-startup --python-exit-code 1 --python remotion/blender/cinematic_vex/blender_check.py
```

La [galerie de validation](../../../docs/previews/cinematic-vex-0.9.1/README.md) expose les images réelles, paramètres, mesures et limites. Aucun épisode complet ni rendu de 35 secondes.
