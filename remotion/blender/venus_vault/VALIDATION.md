# Validation de l’extension Vénus/Caveau

Extension issue de la branche de PR #19 au commit `eb6c4de`, sans ascendance des commits de PR #17. Les rendus sont produits par Blender, sans génération d’image externe, modèle ou texture du jeu.

## Tests exécutés

- **94 tests Node** : 19 Atlas universel, quatre nouveaux tests de sélection/contrat et 71 tests historiques. Les options bornées, scopes de boss, liens d’arènes et parité des requêtes Python/Node sont vérifiés.
- **25 tests Python** : neuf tests de design déterministe, composants, rigs, caméras et requêtes, 12 tests Blender historiques et quatre imports de manifest hors ligne.
- **111 poses/caméras évaluées dans Blender 4.3.2 officiel** : projection de l’œil du boss dans les cinq presets et de la silhouette complète pour wide/reveal/orbit, dont les 48 frames du clip à 24 FPS, transformations finies, tête animée, retour exact à la pose initiale après accès hors ordre, aucune reconstruction d’objet ni fuite de mesh entre les frames.
- TypeScript historique/universal, rapports générés et bundle éditeur : commandes et état final consignés dans `atlas/universal/validation.json`.

Les 136 fichiers historiques et les 12 épisodes audités sur la branche de PR #19 conservent leurs SHA-256. Les anciens contrats et notebooks sont inchangés. Les nouvelles cellules Colab ont été compilées syntaxiquement ; elles n’ont pas été exécutées dans Colab ou sur Android.

## Rendus et mesures

Les cinq vues demandées, les images du clip et les rapports bruts sont dans [docs/previews/venus-vault](../../../docs/previews/venus-vault/README.md). Le tableau y donne les temps effectivement mesurés, le nombre d’images, la résolution, les samples et le pic RSS du processus. Les SHA-256 des PNG et la géométrie y sont conservés.

Machine de validation : Linux x86_64, trois CPU logiques exposés, AMD EPYC 9V74, environ 9.7 GiB RAM ; Python 3.12.14, Node 22.23.4. Blender **4.3.2 officiel**, build `32f5fdce0a0a`, archive vérifiée avec le SHA-256 publié `4da1c956673c0485e63054e563ee69198cc8f80d8157dd7592dffc8a6a5592e6`. Le Blender système sans OpenImageDenoise a servi à un essai initial, écarté des prévisualisations finales à cause du bruit.

Les prévisualisations finales utilisent Cycles, AgX et OpenImageDenoise, avec `device=auto` ayant effectivement sélectionné **CPU**, trois threads. Les mesures sont des durées de validation, avec activité concurrente possible : aucun benchmark comparatif ni gain GPU revendiqué. Pic RSS = processus Blender sur Linux ; ce n’est ni la mémoire totale de l’environnement, ni la VRAM. Utilisation et mémoire GPU non mesurées. Le profil Cinematic est disponible et sa géométrie testée ; les vues livrées utilisent Balanced et le court clip Draft.

## Inspection et limites

Inspection des images réellement rendues : lisibilité de l’architecture, des silhouettes, des éléments lumineux et de leur placement. Le clip est inspecté sur plusieurs poses, avec vérification du codec et de la durée par ffprobe. Cela ne remplace pas une comparaison canonique de chaque pièce avec le jeu.

La réalisation est volontairement voxel et originale. Le Puits et le Trône ont une disposition artistique ; les portails sont une grille lumineuse, le bouclier une cage segmentée. La marche n’a pas d’IK de contact au sol ; aucun combat, projectile ou voyage temporel jouable n’est simulé. Les autres boss de l’Atlas ne sont pas promus en modèles implémentés.

La sélection fonctionne par API/CLI et formulaire Colab. L’éditeur historique conserve son menu et ses assets Remotion ; pas d’insertion automatique dans les anciens épisodes, pas de modification de Kokoro/captions. Le MP4 de test est muet. Aucun épisode complet ou rendu de 35 secondes n’a été lancé.

GPU T4, Colab Pro et Android **non testés sur ce matériel**. Les instructions et le notebook permettent une reproduction ; vérifier `configuration.selected`, `backend`, `devices` et `notes` du rapport avant toute affirmation GPU. Une interruption conserve les PNG/logs déjà écrits, mais cette extension n’implémente pas leur reprise automatique. Aucune intégration ni fusion de PR #17 ou PR #19.
