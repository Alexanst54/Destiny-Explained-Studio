# Living Worlds 0.4

Extension additive de l’Atlas 0.3, des deux compositions voxel et de l’éditeur français. Aucun nouveau service, modèle externe ou paquet JavaScript. Les anciens `location`, `environment`, `elements`, `actors` et `actions` conservent leur rôle. Les quatre décors dédiés et le pipeline Kokoro restent utilisés.

## Contrat

Un lieu Atlas ne sélectionne jamais de personnages. Exemple de champs **dans une scène existante** (les autres champs obligatoires restent présents) :

```json
{
  "atlas": {"locationId":"riis","variantId":"before-whirlwind"},
  "livingWorld": {
    "mode":"reconstruction",
    "era":"pre-whirlwind",
    "cast":[{
      "id":"citizen-01","characterId":"eliksni-civilian",
      "position":[0,0,-4],"animation":"walk",
      "startFrame":0,"durationFrames":720,
      "path":{"speed":0.5,"waypoints":[
        {"position":[0,0,-4],"pauseFrames":30},
        {"position":[3,0,-6],"pauseFrames":0}
      ]},
      "clips":[{"animation":"flee","startFrame":360,"durationFrames":360,"transitionFrames":18}]
    }],
    "groups":[]
  },
  "weather": {
    "type":"clear","intensity":0.2,"windDirection":30,"windSpeed":2,
    "visibility":1,"startFrame":0,"durationFrames":720,"seed":42,
    "transitionFrames":600,"particleBudget":64,"dayPhase":0.5,
    "to":{"type":"thunderstorm","intensity":0.9,"windDirection":60,"windSpeed":16,"visibility":0.4}
  }
}
```

Les valeurs hors bornes sont refusées, jamais silencieusement transformées. Les positions sont dans `[-18,18]` pour X/Z et `[0,12]` pour Y. Identifiants de placement : lettres ASCII, chiffres, `_`, `-` ; `:` est réservé aux membres générés. Une trajectoire utilise une vitesse en unités/s et des pauses aux points ; le dernier point est maintenu. Elle ne dépend pas de l’animation des membres. Pour faire accélérer un départ, choisir une nouvelle trajectoire au plan suivant. L’orientation suit le segment ; pas de navigation ni d’évitement des obstacles.

`groups` contient `id`, `member` (même contrat qu’un placement), `count` (1–24), `seed`, `formation` (`grid`, `line`, `scatter`), `spacing`, `behavior` (`idle`, `walk`, `flee`), `sizeVariation`. Les variations de taille et de position sont déterministes. Palette, accessoires et animation se règlent sur `member`. Les positions générées sont bornées. **32 personnages maximum**, groupes compris, après résolution de chaque plan ; pas de foule implicite.

## Héritage et temps

- Scène : `livingWorld.cast`, `groups`, `props` (terminaux), `mode`, `era`, plus `weather`.
- Plan : `livingWorld.cast` et `groups` remplacent **chacune leur liste entière**. Champ absent = hériter ; `[]` = masquer la liste. `props`, `mode`, `era` restent ceux de la scène.
- `livingWorld.animations` dans un plan remplace la pose d’un placement par son **ID d’instance**, y compris `population:0`. L’override commence au début du plan et prime sur les clips ; il disparaît au plan suivant. Les déplacements et la période de présence restent ceux du placement.
- Ordre de pose : override du plan > clip actif > animation de base. Entrées et sorties de clip interpolées ; pas de chevauchement de clips.
- Les temps des personnages et de la météo sont **relatifs au début de la scène**, même dans un override de plan. Les clips sont relatifs au début du personnage. Le changement de plan ne remet pas les trajectoires ni la météo à zéro.
- `weather` du plan remplace l’objet météo complet. Absence = hériter. Pour une météo visuellement neutre, utiliser `clear` avec intensité 0 (les autres paramètres d’éclairage restent explicites).
- L’Atlas suit sa priorité existante : Atlas du plan > Atlas de la scène seulement si `environment: "scene"`.
- Les acteurs historiques `guardian`/`ghost` restent commandés par `shot.actors` dans la composition cinématique. Dans la composition classique avec Living Worlds, leur présence suit `scene.actions` ; sans Living Worlds, leur comportement historique est préservé.

## Météo et modèles

12 conditions : clair, nuages, pluie, orage, neige, blizzard, brouillard, sable, vent, spores, énergie, surnaturel. La transition interpole intensité, visibilité, vent, teinte et densité des types de particules. Les éclairs viennent d’un hash du seed et de l’intervalle d’image. `dayPhase` : 0/minuit, .25/aube, .5/midi, .75/crépuscule ; `dayCycleFrames` est optionnel. La météo ne simule pas un climat canonique.

Un seul `InstancedMesh` météo, 128 instances maximum, sans ombres dynamiques ni post-traitement obligatoire. Les décors et leurs particules existantes ont leur propre budget (256 éléments particulaires maximum par liste). Les modèles de personnages sont des blocs simples ; 11 recettes visibles, plus une catégorie inconnue qui n’affiche rien. La silhouette humanoïde n’est pas utilisée pour les Spectres, machines, Voyageur ou créatures quadrupèdes. Les animations de drone et de machine utilisent flottement, rotation ou visibilité plutôt que des membres humains. Pas de simulation accumulée.

## Histoire et sources

Le registre est dans `../characters/`, indépendant de `../atlas/`. Il contient les sources, lieux, affiliations et variantes ; les dates restent `null` lorsqu’aucune date précise n’est établie. Les objets de variante distinguent transformation, résurrection, changement de nom et équipement. Une variante peut changer de civilisation ou de famille de modèle. Exemple : Aurash → Auryx → Oryx, Uldren → Crow, humain Clovis → copie IA.

`canonical` ne transforme jamais une illustration en asset officiel. `reconstruction` indique une interprétation ; `alternate-history` impose un cartouche **ALTERNATE HISTORY · NOT CANON** dans les deux compositions. Les contrôles ne bloquent pas les alternatives. Ils signalent les anachronismes connus, les modèles inconnus/reconstitués et les météos hors préréglages. Les relations entre époques sont des **ordres partiels** : aucune datation relative Riis/Âge d’or n’est inventée. L’absence d’avertissement ne prouve pas la canonicité. L’histoire doit être relue par un humain.

Les premiers modèles ne sont pas des portraits exacts. Les précursors restent invisibles. Xivu Arath adulte est aussi masquée en attendant une recette visuelle revue ; Xi Ro Krill est une reconstitution affichable. Le Tourbillon est illustré par une tempête métaphorique, jamais présenté comme une observation météorologique.

## Éditeur et Colab

Onglets **Personnages** et **Météo**, recherche FR/EN, civilisation/faction, variantes, placements multiples, groupes, trajectoires à deux points, clips, overrides d’animation de plan et météo progressive. Réglages avancés supplémentaires disponibles dans le JSON. Recherche limitée à 16 fiches visibles. Sauvegarde locale et export intégral conservent les champs inconnus ; la copie de rendu projette le schéma strict. Un service worker met en cache le site et les catalogues embarqués pour le rouvrir hors ligne après une première visite réussie. Les liens de sources externes nécessitent le réseau.

Depuis `remotion/`, utiliser Node **22.23.4**, `npm ci`, puis :

```bash
npm run typecheck
npm run test:living
npm run test:living:browser
node ../editor/offline.browser.test.cjs
npm run editor:build
npm run editor:check
python scripts/narration.py episodes/living_europa.json
node --experimental-strip-types scripts/episode.mjs render out/living_europa-ready.json --browser-executable=/usr/bin/chromium --concurrency=1
node scripts/verify-living-render.mjs
```

Installer Kokoro CPU selon le guide TTS existant. Les trois démos sont `living_whirlwind.json`, `living_europa.json`, `living_fundament.json`. Le notebook Editor-Colab existant importe leur copie de rendu ; conserver les liens sur `main` après fusion humaine. Les MP4, voix, sous-titres générés et captures restent ignorés dans `out/` / `public/assets/narration/`.

Voir [le rapport de livraison](REPORT.md) pour les résultats et les limites de cette première couverture.
