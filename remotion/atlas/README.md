# Destiny Explained Studio 0.3 — Atlas of Destiny

Catalogue éditorial et manifest, références JSON de lieux et moteur de décors modulaires. **L’inventaire est volontairement déclaré partiel** : aucune liste de données techniques ne prouve l’exhaustivité du canon. Le bilan chiffré et la couverture par sortie sont dans [REPORT.md](REPORT.md) ; les contrôles et le MP4 réel dans [VALIDATION.md](VALIDATION.md).

## Données et fiabilité

- `catalog.json` : fiches stables, noms anglais/français, statut de traduction, alias, catégorie/type, parent, civilisations/factions, époques/événements, sources, statut canonique, apparence, disponibilité, recette et variantes historiques.
- `schema.ts` : validation stricte des champs, parents inconnus, cycles, doublons, références documentaires, variantes et associations jeu/sortie.
- `index.ts` : recherche normalisée (FR/EN, accents, alias et noms de variantes), filtres, résolution des références et statistiques.
- `manifest-evidence.json` : extraits anglais/français des définitions citées, avec leurs hashes et liens techniques. Les bases complètes ne sont pas embarquées dans le site ni dans Git.
- `import_manifest.py` : importeur **hors ligne**, Python standard uniquement, sans téléchargement ni clé API. Les entrées importées restent des candidates de revue, jamais des fiches canoniques promues automatiquement.

La vérification s’appuie sur les manifests publics Bungie D1 et D2 téléchargés le 8 novembre 2026, en anglais et français, plus des pages documentaires et une archive primaire des Books of Sorrow. Chaque référence conserve son URL, son type, sa date de consultation, son sélecteur/hash et sa version si applicable. Les empreintes des fichiers d’origine sont dans `provenance`. Les références secondaires ont été récupérées ; cela ne remplace pas une expertise exhaustive de toutes les assertions du wiki.

### Trois dimensions à ne pas confondre

1. **Existence attestée** : `attested` pour les lieux décrits/montrés, `manifest-attested` pour les zones dont seuls le nom et le rattachement sont vérifiés, `editorial-container` pour le conteneur conceptuel de l’univers. Un titre d’activité peut être une activité couvrant plusieurs lieux, pas une nouvelle planète.
2. **Connaissance de l’apparence** : `game`, `lore`, `lore-and-cinematic`, `simulation` ou `manifest-only`, avec certitude `partial`/`unknown` et une note. Une simulation du passé de Mercure ne constitue pas un relevé historique direct. Les récits internes à l’univers peuvent être incomplets ou trompeurs.
3. **Fidélité du rendu** : `dedicated` signifie décor voxel stylisé existant, **pas carte officielle exacte**. `modular-reconstruction` signifie substitution artistique, affichée dans la vidéo comme **ARTISTIC RECONSTRUCTION**. Tous les lieux n’ont pas de modèle individuel.

`availability` ne promet pas un accès actuel : les manifests conservent du contenu retiré, des reprises, des activités tournantes et des définitions techniques. `historical-content` n’affirme pas que toute activité liée est définitivement supprimée. Les listes vides de factions/époques/événements signifient « non renseigné ou non vérifié », pas « inexistant ». Les noms français non confirmés par le manifest sont signalés comme traductions éditoriales.

Les parents dimensionnels restent abstraits lorsque la position physique est inconnue. Le monde natal du Témoin conserve un libellé descriptif ; aucun nom propre n’est inventé. Riis exclut les ajouts non canoniques de Destiny: Rising. L’Harmonie n’est pas présentée comme une planète : seul le monde Ana-Harmony attesté est inclus.

## Importer un manifest téléchargé, sans réseau

L’importeur accepte :

- un dossier de fichiers `en-DestinyPlaceDefinition.json`, `en-DestinyDestinationDefinition.json`, `en-DestinyActivityDefinition.json` et leurs équivalents `fr-*` ;
- un dossier par langue (`en/DestinyPlaceDefinition.json`…) ou un dossier contenant les trois fichiers sans préfixe ;
- un JSON combiné avec les trois noms de tables, éventuellement `.gz` ;
- un SQLite Bungie `.content` / `.sqlite` / `.db`, ou un ZIP qui en contient un seul. Les archives Bungie D1 portent une extension `.content` malgré leur format ZIP : ce cas réel est pris en charge.

Depuis `remotion/` :

```sh
python atlas/import_manifest.py \
  --en /chemin/manifest --fr /chemin/manifest \
  --game D2 --version VERSION_BUNGIE \
  --output out/atlas-candidates-d2.json

python atlas/import_manifest.py \
  --en /chemin/en.content --fr /chemin/fr.content \
  --game D1 --version VERSION_BUNGIE \
  --output out/atlas-candidates-d1.json
```

Le format de sortie contient noms, hashes unsigned stables, descriptions, références techniques, absence de traduction et liens non résolus. Les noms D1 utilisent `placeName`/`destinationName`/`activityName`, contrairement à `displayProperties` en D2. Les lignes masquées/sans nom sont exclues, mais une ligne restante peut toujours désigner un programme ou un doublon. Les hashes ne sont pas des identités éditoriales permanentes d’un lieu à travers toutes ses versions.

Aucun fichier de catalogue n’est écrasé : un chemin de sortie existant est refusé. SQLite est ouvert en lecture seule, les noms SQL viennent d’une liste fixe et aucun chemin de l’archive ZIP n’est extrait. La taille décompressée est bornée à 256 Mio. Le composant de manifest est une source, pas un export d’épisode à importer dans l’éditeur.

Pour ajouter une fiche : choisir un ID indépendant de la langue, consulter les sources et le contexte, distinguer lieu/activité/peuple, expliciter la traduction et l’apparence, vérifier le parent, remplir les métadonnées connues, choisir une famille de substitution et lancer les validateurs. Conserver les variantes dans `variants`, avec leurs propres sources et degré de certitude. Ne pas déduire automatiquement les factions de chaque zone à partir de la seule famille artistique du décor.

## Référencer un lieu dans un épisode

Les anciens champs sont conservés. Le champ facultatif suivant est reconnu sur une **scène** ou un **plan** :

```json
"atlas": {
  "locationId": "riis",
  "variantId": "before-whirlwind"
}
```

`variantId` est facultatif ; absent, il sélectionne l’état de référence du lieu. Les identifiants inconnus et les variantes rattachées à un autre lieu sont rejetés, sans substitution silencieuse d’un lieu inventé.

Priorité dans `VoxelCinematicEpisode` :

1. `shot.atlas` sélectionne explicitement un lieu pour le plan.
2. Sans `shot.atlas`, un plan `environment: "scene"` hérite de `scene.atlas`.
3. Un ancien décor explicite (`tower`, `europa`, une vision…) conserve sa priorité sur le lieu **de scène**. Sans référence Atlas applicable, le moteur historique fonctionne comme avant.

`VoxelEpisode` utilise directement `scene.atlas`. Les éléments de scène/plan, voix, sous-titres, actions, horloges et transitions restent indépendants du choix du lieu. Retirer une référence Atlas rétablit le décor générique. Une sélection Atlas ne modifie pas les coordonnées de caméra : chaque plan reste à composer selon la narration.

Les versions `0.1.0-draft`, `0.1`, `0.1.0`, `0.2`, `0.2.0` et `0.3.0` sont reconnues pour **la structure d’épisode existante**. Le dépôt contenait des exemples `0.1.0-draft`, même pour les fonctionnalités cinématiques ultérieures. Cette acceptation ne prétend pas migrer un autre format 0.2 inconnu. L’éditeur passe à `0.3.0` quand une référence Atlas est sélectionnée ; sans sélection, les anciens exports conservent leur version.

## Architecture de décors CPU

`recipes.ts` assemble une recette déterministe à partir de la famille, du lieu et de la variante. `geometry.ts` fournit 16 modules légers : terrain, humain, Âge d’or, Vex, Ruche, Cabale, Éliksni, Éveillés, Pyramides, Bray, cité futuriste, cosmos, végétation, océan, neige et météo.

- Les quatre décors déjà présents sont réutilisés via `baseEnvironment` ; les installations Bray d’Europe ajoutent un module à Europe.
- Une fiche sans décor spécifique compose des modules partagés et une palette. `render.modules`, facultatif dans le catalogue, peut remplacer le préréglage par au plus huit modules connus. Une recette différente ne prouve pas une architecture canonique différente.
- Les blocs émettent une géométrie bornée et sont regroupés en deux lots instanciés (surfaces / accents lumineux). La neige réutilise les éléments existants. Les tests parcourent toutes les recettes et toutes les variantes.
- Les mouvements atmosphériques dépendent uniquement de l’image locale de scène et d’une graine stable du lieu/variante. Pas de `Math.random`, `useFrame`, horloge réelle ou simulation accumulée.
- Aucun modèle externe, texture, bloom, ombre dynamique, GPU dédié ou dépendance lourde. Les limites des éléments et profils cinématiques existants restent applicables. Les badges sont en HTML Remotion, hors du contexte 3D.

## Utilisation Android et Colab

Dans l’onglet **Atlas**, rechercher en français/anglais, filtrer la catégorie, civilisation, époque ou parent, explorer les zones, choisir une variante puis **Utiliser pour la scène** ou **Utiliser pour le plan**. Les références sont stockées dans le projet local et son JSON. Les sources et le degré de fidélité sont consultables dans les fiches. Les filtres ne créent pas de modification du projet à eux seuls.

L’export complet conserve les champs inconnus ; la copie de rendu les écarte seulement comme déjà documenté dans l’éditeur. Une sélection ne remplace pas les autres champs de scène/plan. Les projets restent dans le navigateur : exporter régulièrement pour garder une sauvegarde indépendante.

**Editor-Colab.ipynb et tous les liens actifs restent sur `main`.** Les fonctionnalités Atlas dans Colab deviennent disponibles après fusion volontaire de cette PR vers `main`. Le notebook charge `main`, y compris dans une session réutilisée, sans écraser des modifications locales. Aucun workflow Actions à ajouter. GitHub Pages reste en mode **Deploy from a branch → main /docs** ; le JS compilé est versionné.

La démo **Démo Atlas** du nouvel onglet charge `episodes/atlas_demo.json` : 24 secondes, quatre scènes de six secondes, huit plans, Riis avant le Tourbillon, Mercure pendant l’Âge d’or, Fundament à l’époque des Krill, puis Europe/Bray. Les quatre vues sont explicitement des reconstitutions ; aucun Gardien/Spectre n’est présenté dans les trois scènes anciennes.

```sh
npm run typecheck
npm run test:atlas
npm run test:atlas:import
npm run report:atlas
npm run editor:build
npm run editor:check
npm run narrate:atlas
npm run render:atlas
python scripts/verify_narration.py --episode out/atlas_demo-ready.json --video out/atlas-of-destiny-demo.mp4
```

Les sorties MP4/WAV/images/rapports restent dans les répertoires générés ignorés par Git. Le notebook conserve son parcours générique import JSON → Kokoro af_heart 1× → mots alignés → Remotion SwiftShader, sans clé API payante.
