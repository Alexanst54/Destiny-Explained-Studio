# Blender Bridge 0.8.1 — journal de reprise

Branche : `feat/blender-bridge-0.8.1`. Base main vérifiée : `baf79ed8a32957ed2359334f376bbc89c46971ae` (fusion #13). Aucun changement de publication Pages ; aucune fusion automatique.

## Étape 1 — inspection ciblée terminée

Interfaces réutilisables :

- `episodeSchema`, `validateWords`, `resolveDirection`, `atFrame` : projet validé, scène/plan effectif et frame locale ; les timestamps embarqués 0.7 évitent toute dépendance audio pour une image.
- `evaluateStudio` : poses et déplacements déterministes après héritage et interactions ; `rigBones` : hiérarchie originale des géométries. La petite définition d’équipement du renderer sera extraite en fonction partagée, sans changer ses résultats.
- `cameraState`, `directCamera`, `composeCamera`, `lodFor` : caméra effective et niveaux de détail, conservés dans cet ordre.
- `environmentBlocks`, `atmosphere`, `environmentStyle` : décor procédural borné et couleurs. Le premier pont n’exportera pas tout l’Atlas : sol et bâtiments procéduraux, avec omissions explicites.
- `episode.mjs` : conventions Node 22, chemins locaux, rendu Remotion conservé. Le nouveau CLI sera indépendant et ne lancera aucune vidéo.
- `Editor-Colab.ipynb` : clone via REF/main, installation Node et dépendances. Un notebook Blender dédié conservera ce principe, sans installer Kokoro inutilement pour des PNG.

Environnement constaté : Blender 4.3.2 présent, Node 22.23.4 disponible dans le cache existant ; aucun paquet installé. Pas de test Chromium, pas de rendu vidéo.

## Étapes suivantes

2. Export JSON versionné et tests ciblés : à faire.
3. Importeur Blender, axes/caméras/lumières et premier PNG CPU : à faire.
4. Notebook Pro avec détection GPU et repli CPU, guides et rapport : à faire.
5. Vérification finale ciblée et PR : à faire. Ouvrir une PR dès le premier ensemble cohérent.

## Reprise

`git switch feat/blender-bridge-0.8.1`, puis `git status --short`. Lire ce fichier avant tout essai. Les commandes et résultats seront ajoutés à chaque checkpoint. Ne pas lancer toutes les suites Chromium ni un film complet. Après deux échecs d’une approche, analyser avant nouvel essai.
