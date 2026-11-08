# Éditeur mobile Destiny Explained

Site statique français, sans API, CDN, backend ou compte payant. Ouvrir l’adresse GitHub Pages dans Chrome Android. Les vidéos restent calculées dans Colab avec le moteur existant.

## Publication depuis main /docs

1. Relire et fusionner cette PR lorsque vous le déciderez. Aucun changement n’est fusionné automatiquement.
2. Dépôt GitHub → **Settings → Pages → Build and deployment → Source: Deploy from a branch**.
3. Choisir **main**, dossier **/docs**, puis **Save**. Ne pas choisir la source « GitHub Actions ».
4. Ouvrir `https://alexanst54.github.io/Destiny-Explained-Studio/`.

Le JavaScript compilé est versionné : aucun build utilisateur ni workflow de dépôt n’est nécessaire. GitHub peut afficher son propre traitement interne de publication Pages dans Actions ; cela ne nécessite pas de fichier workflow dans ce dépôt. Les workflows préexistants ne sont pas modifiés. Pages doit être disponible pour la visibilité et l’offre actuelles du dépôt.

## Sur Android

- Charger **Modèle Voyageur** (copie exacte de `traveler_episode_002_cinematic.json`) ou **Nouveau**, ou importer un JSON ≤ 2 Mo.
- Modifier titre, narration anglaise, durée, intensité, scènes, plans, caméras, personnages, animations et effets. Les options viennent des schémas du moteur. Le décor classique reste `the-tower` ; les plans proposent les quatre environnements cinématiques compatibles.
- Monter/descendre réorganise les scènes et recalcule leurs débuts. Réorganiser les plans conserve leurs ancrages narratifs : corriger les erreurs de chronologie, ou choisir explicitement **Répartir les plans** pour remplacer leurs ancrages par des temps régulièrement espacés.
- Les durées sont arrondies à l’image à 30 fps. Le total change avec les scènes ; le modèle fait 60 secondes. La chronologie des plans liés à des mots reste une estimation avant Kokoro.
- **JSON avancé** donne accès à tous les champs. Appliquer ou annuler un brouillon avant de revenir au mode débutant ou d’exporter. Les erreurs de schéma, durées et actions sont affichées.
- La sauvegarde locale conserve plusieurs projets et les brouillons JSON invalides. Elle dépend du navigateur et de cette adresse, peut être effacée et n’est pas une sauvegarde cloud. Exporter régulièrement, surtout en navigation privée. Un refus/quota de stockage est signalé.

### Champs avancés et inconnus

Les formulaires changent uniquement les champs visés, sauf le recalcul explicite des durées/débuts et l’invalidation des voix après modification du texte ou du temps. **Exporter JSON** conserve tous les champs, y compris ceux que le schéma strict Remotion refuse. **Copie pour rendu** est une opération distincte : elle retire uniquement les champs inconnus listés par la validation et laisse le projet complet intact. Les champs connus invalides bloquent cette copie. Garder aussi l’export complet comme archive.

### JSON → Colab → MP4, sans modifier le dépôt

Ouvrir [Editor-Colab](https://colab.research.google.com/github/Alexanst54/Destiny-Explained-Studio/blob/feat/voxel-environment-library/remotion/tts/Editor-Colab.ipynb) depuis le bouton du site. Avant fusion, le notebook référence cette branche de PR ; après fusion, `main` peut remplacer `feat/voxel-environment-library` dans le lien et `REF`.

1. Session CPU Python 3.12 ; exécuter l’installation.
2. Choisir le JSON exporté dans les téléchargements Android. L’original est conservé dans `remotion/out/editor-upload.json` ; la copie stricte dans `out/editor-episode.json`, avec rapport des champs écartés.
3. Générer Kokoro `af_heart`, 1×, puis le rendu : les scripts génériques existants produisent la voix par scène, les mots alignés, puis le MP4 vertical avec audio. Aucun script de préparation spécifique à l’ancien épisode n’est utilisé.
4. Télécharger le MP4 et les rapports avant la fin de session. Une narration trop longue ou un ancrage invalide après alignement arrête le traitement : corriger le projet et réimporter. Le navigateur ne mesure pas la durée réelle de Kokoro.

Colab demande un compte Google ; la disponibilité des ressources gratuites n’est pas garantie. L’éditeur ne contacte aucun service lors de l’édition et ne génère ni voix ni vidéo. Ne pas importer de secrets dans les projets.

## Développement et validation

Depuis `remotion/`, Node **22.23.4** :

```sh
npm ci
npm run editor:build
npm run editor:check
npm run test:editor
npm run typecheck
npm run test:episode
npm run test:cinematic
```

Sources : `editor/model.mjs` et `editor/app.mjs`. `editor:build` utilise esbuild local pour compiler les vrais schémas Zod et le résolveur de chronologie dans `docs/assets/editor.js`. `docs/engine-contract.json` contient leurs empreintes et celle du modèle. `editor:check` échoue si le site versionné n’a pas été régénéré après une modification du contrat. Le site publié n’a aucune dépendance d’exécution à npm.

Import CLI réutilisable (depuis `remotion/`) :

```sh
node --experimental-strip-types scripts/import-editor.mjs mon-episode.json
# Seulement pour créer explicitement une copie sans les champs inconnus :
node --experimental-strip-types scripts/import-editor.mjs mon-episode.json --compatible-copy
python scripts/narration.py out/editor-episode.json
npm run render:episode -- out/editor-episode-ready.json
```

Le notebook a été vérifié structurellement ; l’exécution complète dans une session Google Colab réelle reste à valider. Les compositions, styles voxel et scripts TTS/rendu existants restent inchangés.

Tests navigateur reproductibles (Chromium installé séparément) :

```sh
CHROMIUM_EXECUTABLE=/usr/bin/chromium npm run test:editor:browser
```

Le test sert les fichiers statiques via le routage Playwright, sans lancer de serveur. Il couvre quatre largeurs (320, 360, 393 et 1280 pixels), import/export, champs inconnus, texte HTML inerte, sauvegarde/rechargement, brouillon invalide, ajout de plans, durées, import mal structuré et refus du stockage. Dans l’environnement géré, la politique Chromium interdit les téléchargements `blob:` : le test capture le vrai contenu du Blob et neutralise uniquement le clic de téléchargement. L’enregistrement effectif du fichier reste à vérifier sur Chrome Android réel ; aucune politique navigateur n’est contournée.

## Bibliothèque de décors et d’éléments voxel

Le bouton **Démo 4 décors** charge un épisode de 16 secondes (Tour/Dernière Cité, Europe, Jardin noir, Pyramide). Le décor de scène se choisit dans les réglages de scène. Les nouveaux plans suivent ce choix avec **Décor de la scène** ; les anciens plans conservent leur décor explicite. Changer le décor ajoute sa déclaration compatible au JSON.

Déplier **Éléments voxel de la scène** pour ajouter Gardien décoratif, Spectre, structure vex, fragments de Lumière, cristaux, neige ou particules, puis régler animation, position, échelle et graine. Les personnages principaux restent animés dans l’onglet Animations. Pour un plan, **Éléments voxel de ce plan** permet de conserver l’héritage de scène ou de créer une liste propre (qui remplace la liste de scène). Les limites sont de 12 éléments, 64 particules par élément et 256 particules par liste ; les erreurs bloquent la copie pour rendu.

Exporter et importer le fichier dans **Editor-Colab** suffit ; les nouveaux champs sont acceptés par le même adaptateur et la même chaîne Kokoro → Remotion. Le [contrat JSON complet](../remotion/src/voxel/library/README.md) se consulte dans le dépôt GitHub. Aucun service ni workflow n’est ajouté au site statique.
