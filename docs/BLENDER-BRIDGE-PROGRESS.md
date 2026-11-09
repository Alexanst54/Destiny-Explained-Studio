# Blender Bridge 0.8.1 — journal de reprise

Branche : `feat/blender-bridge-0.8.1`. Base main vérifiée : `baf79ed8a32957ed2359334f376bbc89c46971ae` (fusion #13). Aucun changement de publication Pages ; aucune fusion automatique.

## Étape 1 — inspection ciblée terminée

Interfaces réutilisables :

- `episodeSchema`, `validateWords`, `resolveDirection`, `atFrame` : projet validé, scène/plan effectif et frame locale ; les timestamps embarqués 0.7 évitent toute dépendance audio pour une image.
- `evaluateStudio` : poses et déplacements déterministes après héritage et interactions ; `rigBones` : hiérarchie originale des géométries. Les accessoires présents dans rigBones sont exportés ; les panneaux d’équipement additionnels du renderer sont signalés comme omis. Aucun module fonctionnel n’est réécrit.
- `cameraState`, `directCamera`, `composeCamera`, `lodFor` : caméra effective et niveaux de détail, conservés dans cet ordre.
- `environmentBlocks`, `atmosphere`, `environmentStyle` : décor procédural borné et couleurs. Le premier pont n’exportera pas tout l’Atlas : sol et bâtiments procéduraux, avec omissions explicites.
- `episode.mjs` : conventions Node 22, chemins locaux, rendu Remotion conservé. Le nouveau CLI sera indépendant et ne lancera aucune vidéo.
- `Editor-Colab.ipynb` : clone via REF/main, installation Node et dépendances. Un notebook Blender dédié conservera ce principe, sans installer Kokoro inutilement pour des PNG.

Environnement constaté : Blender 4.3.2 présent, Node 22.23.4 disponible dans le cache existant ; aucun paquet installé. Pas de test Chromium, pas de rendu vidéo.

## Étapes suivantes

2. Export JSON versionné et tests ciblés : terminé. Contrat v1 / exporterVersion 0.8.1 indépendant des versions de projet ; matrices colonne majeure, caméra réelle 0.7 et omissions explicites. Exemple compact Riis avec six acteurs et détail de décor réduit à 6.
3. Importeur Blender, axes/caméras/lumières et premier PNG CPU : à faire.
4. Notebook Pro avec détection GPU et repli CPU, guides et rapport : à faire.
5. Vérification finale ciblée et PR : à faire. Le contrat/exporteur constitue le premier ensemble cohérent ; publication en PR brouillon maintenant, avant le rendu Blender.

## Reprise

`git switch feat/blender-bridge-0.8.1`, puis `git status --short`. Lire ce fichier avant tout essai. Les commandes et résultats seront ajoutés à chaque checkpoint. Ne pas lancer toutes les suites Chromium ni un film complet. Après deux échecs d’une approche, analyser avant nouvel essai.

## Checkpoint 2 — commandes exécutées

- `node --experimental-strip-types --test remotion/blender/tests/export.test.mjs` (Node 22.23.4) : **4 tests réussis**, incluant validation Python, export/import JSON, immutabilité, frames hors ordre et positions des articulations (tolérance 1e-9).
- `node remotion/node_modules/typescript/bin/tsc --noEmit --project remotion/tsconfig.json` : réussi.
- `blender --background --factory-startup --python-expr ...` : Blender 4.3.2, Cycles compilé disponible. Aucun rendu encore exécuté.
- `node --experimental-strip-types remotion/blender/examples/generate.mjs` : exemple généré.
- Aucun paquet installé ; aucune suite Chromium ni vidéo relancée.
