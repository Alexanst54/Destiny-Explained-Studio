# Moteur de mise en scène voxel

Le moteur ajoute `VoxelCinematicEpisode` et `VoxelMotionLab` sans remplacer
`Episode1`, `VoxelResurrection` ou `VoxelEpisode`. Le Gardien, le Spectre, la Tour,
le Voyageur, les matériaux mats et la palette sont conservés. Le Gardien accepte
un jeu d'articulations optionnel ; sans celui-ci son rendu reste identique.

## Épisode 002 : 16 plans sur 60 secondes

`episodes/traveler_episode_002_cinematic.json` conserve intégralement le texte,
les départs et les durées des six scènes d'origine. Il ajoute `direction` :

| Scène | Plans | Intention |
| --- | ---: | --- |
| 01 | 2 | Marche vers le balcon puis révélation du Voyageur lorsqu'il est nommé |
| 02 | 2 | Orbite lente puis consultation d'un hologramme pendant l'Âge d'or |
| 03 | 4 | Vision illustrative de la ville, impact et débris, puis longue révélation du Voyageur resté sur Terre |
| 04 | 3 | Spectre dans la Lumière, recherche d'un compagnon, puis entrée du Gardien |
| 05 | 3 | Gardien tombé, résurrection sur « return », puis gros plan sur la vulnérabilité du Spectre |
| 06 | 2 | Révélation calme du mystère puis recul sur la Cité et le Gardien |

Les plans courts de l'Effondrement durent environ 1–1,5 seconde ; les révélations
restent plusieurs secondes. Ce sont des choix écrits dans le JSON, jamais une
sélection aléatoire ou un montage automatique basé sur un quota de coupes.
`purpose` documente obligatoirement le rôle narratif de chaque plan, action et effet.
Le champ ne remplace pas une revue éditoriale : le moteur ne juge pas le sens du texte.

Les visions historiques sont signalées comme illustrations ; aucun Gardien ne
combat pendant l'Effondrement, avant la création des Spectres. Le moteur sait
courir, sauter et combattre, mais l'épisode n'impose pas ces actions à ce récit.
La galerie de mouvements les démontre séparément.

## Génération et rendu

Depuis `remotion/`, avec l'environnement Python Kokoro et Node 22.23.4 :

```bash
npm ci
npm run narrate:episode
npm run prepare:cinematic
npm run render:cinematic
npm run verify:cinematic
```

`prepare:cinematic` réutilise la voix prête de l'épisode original. Il refuse toute
différence de texte, format ou minutage entre l'épisode source et sa variante,
valide les mots et résout tous les plans/événements. Aucun nouvel appel TTS n'est
nécessaire lorsque les WAV Kokoro sont déjà en cache. Le fichier source original
et les fichiers audio ne sont pas modifiés.

Sorties :

- `out/traveler_episode_002_cinematic-ready.json` : épisode et voix prête.
- `out/cinematic-shot-report.json` : départ/fin réels des plans, actions et effets.
- `out/episode-002-traveler-cinematic.mp4` : vidéo complète avec voix Kokoro et mots synchronisés.

En cas de téléchargement Chromium bloqué, ajouter
`-- --browser-executable=/usr/bin/chromium` à la commande de rendu. Avec assez de
mémoire, `-- --concurrency=2` accélère potentiellement le rendu ; le défaut reste
une tâche. SwiftShader via ANGLE (`swangle`) est utilisé, sans GPU dédié.

Pour tester les mouvements, sélectionner `VoxelMotionLab` dans Remotion Studio
ou lancer `npm run still:motion`. Cette composition silencieuse de 24 secondes
présente successivement marche, course, saut, chute, résurrection, combat,
interaction et regard vers le ciel.

## Intensité

```bash
npm run prepare:cinematic -- --intensity=calm
npm run prepare:cinematic -- --intensity=balanced
npm run prepare:cinematic -- --intensity=cinematic
```

Les valeurs correspondent à **calme**, **équilibrée** (défaut) et **cinématique**.
Elles modulent les gestes, les secousses et la densité maximale des particules
(16 / 28 / 40 instances par effet). Elles ne déplacent pas les coupes ou les mots
et ne changent pas arbitrairement le cadrage narratif. Modifier le rythme exige
un choix de plans dans le JSON, pas une intensification automatique du montage.

## Format JSON réutilisable

Une entrée de `direction.scenes` doit correspondre à chaque scène, dans le même
ordre. Chaque scène contient `shots`, `actions` et `events`.

Exemple de déclencheur lié à la voix :

```json
{"phrase":"return from death","occurrence":1,"offsetFrames":0}
```

Il se résout au début du mot correspondant dans le fichier aligné Kokoro.
`occurrence` est indexé à partir de 1 ; la ponctuation est ignorée. Un déclencheur
`{"sceneFrame":0}` est relatif au début de la scène. Les images de début de plans
sont donc soit éditoriales et explicites, soit liées à une phrase du récit.

Le premier plan commence à l'image 0 de sa scène. Les fins sont déduites du plan
suivant et de la durée de scène : aucun trou ou chevauchement n'est possible.
Une phrase introuvable, un effet trop long, des actions simultanées contradictoires,
un identifiant dupliqué ou un suivi d'acteur invisible provoquent une erreur.
Les plans durent au moins 12 images et les transitions sont bornées par leurs voisins.
Le mode aperçu utilise des mots estimés et le signale ; seul le mode final avec
les horodatages réels constitue la référence de synchronisation.

Chaque caméra contient explicitement :

- `mode` : `dolly`, `orbit`, `zoom`, `follow`, `close-up`, `perspective`.
- `from`, `to` : positions 3D ; `targetFrom`, `targetTo` : points visés.
- `fovFrom`, `fovTo` : angle de champ entre 25° et 65°.
- `track` : `guardian` ou `ghost` pour viser un personnage ; en mode `follow`,
  les positions deviennent des offsets relatifs à sa position.
- `angleFrom`, `angleTo` : angles d'orbite en radians, requis pour `orbit`.

Les modes rapproché et perspective utilisent les positions et l'angle de champ
écrits par l'auteur ; aucun zoom surprise n'est ajouté. Les trajectoires qui
traversent le point visé sont rejetées. Le suivi est analytique, sans retard accumulé.

Chaque action contient un acteur, une animation, `at`, `durationFrames`, `from`,
`to`, une hauteur de saut optionnelle et son intention. Les positions finales sont
conservées jusqu'à l'action suivante dans la même scène. Une chute reste au sol jusqu'à la résurrection.
Le Gardien dispose de `idle`, `walk`, `run`, `jump`, `fall`, `resurrect`, `combat`,
`interact`, `look-up` ; le Spectre de `hover`, `orbit`, `interact`, `scan`.
Les animations sont stylisées : il ne s'agit pas d'un solveur physique ou d'IK.

Chaque effet contient `type`, `at`, `durationFrames`, `position`, `strength` et
`purpose`. Les types sont `particles`, `explosion`, `hologram`, `beam`, `shake`.
Un rayon exige `to`, distinct de son point de départ. Les débris suivent une
trajectoire balistique analytique ; les particules utilisent un hash d'indice,
sans générateur aléatoire mutable. Les explosions restent illustratives.

## Transitions et décors

Les décors disponibles sont `tower`, `golden-age-vision`, `collapse-vision` et
`light-space`. Les deux visions réutilisent la Tour et ses cubes, avec des ajouts
symboliques et une lumière adaptée. L'espace de Lumière sert à isoler le Spectre.
Les acteurs visibles sont indiqués dans chaque plan, indépendamment de leur pose.

Transitions entrantes :

- `cut` : coupe franche, durée nulle.
- `fade` : passage par le fond sombre, appliqué aux deux côtés de la coupe.
- `wipe` : volet sombre sur les deux côtés de la coupe.
- `match` : continuité de caméra depuis le point final du plan précédent.

Les transitions ne doublent pas les canvases WebGL. Le changement de décor se
fait à la coupe, masqué par le fondu/volet si sélectionné ; `match` n'est pas un
fondu croisé de deux décors. Les sous-titres restent lisibles au-dessus du masque.

## Déterminisme, performances et tests

`timeline.ts` résout les données ; `motion.ts` calcule les poses et caméras ;
`Effects.tsx` et `Stage.tsx` affichent la scène. Aucune animation ne lit une horloge
murale ou n'accumule une simulation via `useFrame`. Un accès direct à une image
donne le même état qu'une lecture séquentielle. Les particules sont instanciées,
sans ombres temps réel, post-traitement ou asset distant obligatoire.

```bash
npm run typecheck
npm run test:voxel
npm run test:episode
npm run test:narration
npm run test:cinematic
```

La reproductibilité des pixels se vérifie sur la même pile Chromium/GL ; les
pilotes et versions peuvent modifier légèrement le rendu. Les caméras, débits et
positions ne changent pas en fonction de la puissance de la machine.

## Android / Colab

Ouvrir [le notebook dans Google Colab](https://colab.research.google.com/github/Alexanst54/Destiny-Explained-Studio/blob/feat/cinematic-staging/remotion/tts/Cinematic-Colab.ipynb)
ou télécharger [le fichier du notebook](../../../tts/Cinematic-Colab.ipynb).
Il reprend l'installation Kokoro gratuite, génère ou réutilise l'audio, prépare
les plans puis rend et télécharge le MP4. Il n'active pas OpenAI et n'exige pas
GitHub Actions. Avant fusion, la branche utilisée est `feat/cinematic-staging`.
