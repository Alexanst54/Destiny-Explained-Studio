# Validation 0.9.1 — 9 novembre 2026

Node 22.23.4, Python 3.12.14, Blender officiel 4.3.2, CPU AMD EPYC 9V74 (3 threads), aucun GPU.

| Vérification | Résultat |
| --- | --- |
| Node universal, sélection et suites historiques | 96 passés, 0 échec |
| Python Blender et import de manifest | 29 + 4 passés |
| TypeScript historique et universal | Passés |
| Blender natif refonte | 136 évaluations passées |
| Blender natif compatibilité | 156 évaluations passées |
| Rapports audit/couverture, rapport Atlas et bundle éditeur | Régénération/vérification passée |
| Médias 0.9.1 | 6 paires Cinematic + 2 clips Balanced vérifiés |
| Conservation historique | 136 fichiers, 12 épisodes et galerie 0.9.0 inchangés |

Les tests couvrent le LOD indépendant de la résolution/qualité, la hiérarchie stable entre LOD, les anciens contrôles, la normalisation des requêtes, le déterminisme par graine et par temps, les quaternions, les phases d’appui, la projection caméra et le réemploi des ressources Blender. Le contrôle natif mesure 1,20e−6 m d’erreur IK et 1,72e−6 m de glissement maximal. Les surfaces décoratives ajoutent 0,030001 m d’écart au plan nominal : tolérance 0,04 m, pas de contact physique parfait revendiqué.

Les [comparatifs, clips et temps réellement mesurés](../../../docs/previews/cinematic-vex-0.9.1/README.md) constituent la preuve visuelle. Les anciens médias restent vérifiés contre leur code gelé. Les MP4 sont H.264/yuv420p, 48 et 36 images à 24 FPS, muets. Les épisodes et leurs pistes audio/sous-titres ne changent pas.

```sh
python remotion/blender/cinematic_vex/verify_evidence.py
python remotion/blender/venus_vault/verify_evidence.py
python -m unittest discover -s remotion/blender/tests
python -m unittest discover -s remotion/tests -p 'test_manifest_import.py'
blender --background --factory-startup --python-exit-code 1 --python remotion/blender/cinematic_vex/blender_check.py
blender --background --factory-startup --python-exit-code 1 --python remotion/blender/venus_vault/blender_check.py
```

Les commandes Node complètes figurent dans `atlas/universal/validation.json`. Pour reproduire les images, suivre le README et le notebook dédié. Les mesures CPU subissent une possible contention ; aucune comparaison de vitesse contrôlée ni mesure GPU/VRAM n’est annoncée. T4, Colab Pro et Android restent à tester. La marche se borne à deux cycles ; les portails et attaques sont des effets graphiques sans simulation physique. La géométrie voxel reste une interprétation artistique originale, pas une copie exacte du jeu. Aucun rendu de 35 secondes n’a été lancé.
