# Bibliothèque voxel procédurale

Quatre décors légers pour `VoxelEpisode` et `VoxelCinematicEpisode`, sans assets, textures, modèles externes, simulation physique ni service tiers obligatoire.

| `location` de scène | Décor et géométrie | Identifiant `model` à déclarer |
| --- | --- | --- |
| `the-tower` | Balcon existant, Voyageur, Dernière Cité en profondeur, éclairage et bannières | `voxel-tower-v1` |
| `europa` | Sol enneigé, crêtes de glace en marches, avant-poste | `voxel-europa-v1` |
| `black-garden` | Terrasses végétales, fleurs rouges, porte vex carrée | `voxel-black-garden-v1` |
| `pyramid-interior` | Couloir à nervures triangulaires en marches, autel, lignes ambrées | `voxel-pyramid-v1` |

La Tour et le Voyageur originaux sont réutilisés. Le Gardien et le Spectre conservent leurs modèles et couleurs existants. Les autres environnements ont chacun une palette, un brouillard et un éclairage adaptés ; aucune ombre dynamique ni post-traitement GPU n’est ajouté.

## Contrat JSON partagé

`catalog.ts` exporte les identifiants, déclarations de décors, animations permises et schémas Zod utilisés par le moteur **et** l’éditeur. Les épisodes existants n’ont aucun champ à ajouter. Leurs décors explicites, durées, ancrages, transitions, voix et sous-titres conservent leur sens.

Un nouveau décor utilisé doit figurer dans `environments`. L’éditeur ajoute automatiquement sa déclaration lors d’un choix de décor ; les anciennes déclarations et leurs champs avancés restent conservés. Les déclarations attendues sont dans `environmentDefinitions` et dans `episodes/voxel_worlds_demo.json`. Chaque déclaration contient les trois `props` distincts de son décor, un modèle correspondant et un identifiant unique. `setting` doit aussi être déclaré.

```json
{
  "id": "europa",
  "model": "voxel-europa-v1",
  "props": ["ice-ridges", "snowfield", "research-outpost"]
}
```

Pour une scène, choisir `location: "europa"`. Pour un plan :

- `environment: "scene"` suit le décor de sa scène.
- `environment: "europa"`, `"black-garden"` ou `"pyramid-interior"` le remplace pour ce plan seulement.
- `"tower"`, `"golden-age-vision"`, `"collapse-vision"`, `"light-space"` gardent le comportement historique.

Les nouveaux plans de l’éditeur héritent du décor de scène. Les anciens plans explicitement réglés sur `tower` ne sont pas convertis automatiquement lorsque vous changez `location`.

### Éléments de scène et de plan

`scene.elements` est facultatif. Dans un plan, `elements` absent **hérite** de la scène ; une liste remplace entièrement ses éléments ; `[]` les masque. Les horloges restent locales à la scène, donc pas de redémarrage d’un effet hérité à chaque plan. Les identifiants sont uniques dans chaque liste. La transformation s’applique à l’ensemble de l’élément.

```json
"elements": [
  {
    "id": "snowstorm",
    "type": "snow",
    "position": [0, 0, -2],
    "animation": "blizzard",
    "count": 48,
    "strength": 0.8,
    "seed": 42,
    "scale": 1
  },
  {
    "id": "ice",
    "type": "crystal",
    "position": [3, 0, -3],
    "animation": "pulse"
  }
]
```

| `type` | Animations acceptées (première = défaut) |
| --- | --- |
| `guardian` | `idle`, `walk` (patrouille aller-retour locale de 1,6 unité) |
| `ghost` | `hover`, `still` |
| `vex-structure` | `still`, `pulse` |
| `light-fragments` | `pulse`, `still` |
| `crystal` | `pulse`, `still` |
| `snow` | `drift`, `blizzard`, `still` |
| `particles` | `drift`, `pulse`, `still` |

Champs : `id`, `type`, `position` obligatoires ; `rotation` en radians (défaut zéro), `scale` 0,25–3 (défaut 1), `animation`, `seed` 0–65535 (défaut 0), `count` 1–64 (défaut 24), `strength` 0–1 (défaut 0,65) facultatifs. `count` concerne neige, fragments et particules ; `strength` règle leur taille/vent et l’amplitude des pulsations de décor. La neige ne modifie pas la narration et n’introduit pas de secousse automatique de caméra.

Les éléments `guardian`/`ghost` sont des copies décoratives supplémentaires ; les protagonistes principaux restent contrôlés par les champs `actors` et les actions cinématiques existantes. Pour une marche précisément synchronisée au texte, utiliser les actions du Gardien principal, plutôt qu’une patrouille décorative. Les caméras existantes fonctionnent sans nouvelle commande.

## Budget et déterminisme CPU

- Maximum **12 éléments par liste**, **64 particules par élément** et **256 particules au total par liste** (neige, fragments, particules). Les effets narratifs existants gardent leur propre profil d’intensité.
- Blocs de décor regroupés en deux `InstancedMesh` : surface standard et accents lumineux. La Tour réutilise aussi son ancien balcon et son Voyageur. Les particules utilisent un seul lot par élément. Les personnages restent leurs assemblages existants : multiplier les personnages coûte davantage que les particules.
- `layout.ts` calcule la géométrie et les particules avec un hash indexé, la graine et l’image de scène ; aucune horloge, `Math.random`, `useFrame`, accumulation ou simulation.
- Éclairage lumineux obtenu par couleurs émissives ou matériaux simples, sans bloom, textures, assets réseau ni GPU dédié.
- `calm`, `balanced`, `cinematic` continuent de régler les actions/effets cinématiques existants. Les décors statiques restent identiques ; le vent et la densité de neige sont choisis explicitement par le JSON pour garder le contrôle narratif.

## Démonstration et Android → Colab

`episodes/voxel_worlds_demo.json` : **16 s, 480 images, 1080 × 1920, 30 fps**, quatre scènes et huit plans, marche, Spectre en orbite, copies décoratives, neige, cristaux, structures vex et fragments de Lumière. C’est une démonstration de bibliothèque, pas un remplacement de l’épisode 002.

Depuis `remotion/`, Node 22.23.4 :

```sh
npm ci
npm run typecheck
npm run test:library
npm run editor:build
npm run editor:check
npm run render:worlds:preview
# Après installation des dépendances Python Kokoro existantes :
npm run narrate:worlds
npm run render:worlds
python scripts/verify_narration.py --episode out/voxel_worlds_demo-ready.json --video out/voxel-worlds-demo.mp4
```

Sur Android : choisir **Démo 4 décors** dans l’éditeur, modifier si besoin, exporter, ouvrir `Editor-Colab.ipynb`, importer le JSON et exécuter le parcours existant. Le notebook reste générique et n’exige ni workflow Actions ni édition manuelle des épisodes du dépôt. Sa `REF` et les liens du site pointent sur cette PR pour permettre les tests avant fusion ; après fusion volontaire, `main` peut les remplacer.

Le rendu et la validation audio ont été effectués dans l’environnement de travail, pas dans une session Google Colab réelle. La durée CPU varie suivant la session. Voir `VALIDATION.md` pour les mesures et les limites.
