# Validation — Atlas of Destiny 0.3

Travail démarré depuis `main` après fusion de la PR #8 (`55634ac`), sur `feat/atlas-of-destiny`. Node 22.23.4, Remotion 4.0.541, Python 3.12, Kokoro et dépendances existantes. Aucun workflow Actions, backend, bibliothèque 3D externe ou dépendance supplémentaire ajouté.

## Catalogue et provenance

- **468 fiches**, **159 références** : 93 définitions Bungie citées, une archive primaire du lore (Books of Sorrow I: Predators) et 65 références communautaires secondaires récupérées.
- **321 fiches manifest-attested** : seuls le nom et le rattachement de ces zones sont vérifiés dans les tables. L’existence d’un nom ne prouve pas une carte publiée ni un accès actuel.
- **17 variantes historiques** imbriquées, **39 lignes de couverture** par jeu/extension/saison/épisode, toutes annoncées partielles. Répartition complète dans `REPORT.md`, générée depuis les données validées.
- Les bulles de zones issues du manifest D2 ne reçoivent pas automatiquement une disponibilité D1 parce que leur destination existait déjà dans le premier jeu ; ce cas est vérifié par un test de provenance.
- D1 et D2 : téléchargements réels anglais/français des tables publiques `DestinyPlaceDefinition`, `DestinyDestinationDefinition`, `DestinyActivityDefinition`. La version D2 observée est `245114.26.10.13.2000-1-bnet.66137` ; versions, sélecteurs et empreintes des fichiers sont conservés dans le catalogue et `manifest-evidence.json`.
- Import réel hors ligne des trois composants D2 : **3 884 candidates techniques** ; import réel des bases SQLite D1 compressées `.content` : **680 candidates**. Les lignes techniques ne sont pas comptées comme des lieux inventoriés et aucune promotion automatique n’a été effectuée.
- Les sources manuelles ont été consultées pour l’existence/contexte des lieux et variantes. Les liens absents initialement ont été corrigés ; les traductions françaises non confirmées par Bungie sont marquées éditoriales. Les contextes ambigus sont signalés. Aucune garantie d’exhaustivité des lieux ou de toutes les affirmations secondaires.

## Tests exécutés et réussis

- `npm run typecheck`.
- **38 tests Node** : voxel (3), épisodes (6), cinématique (6), bibliothèque (6), éditeur (9), Atlas (8).
- **10 tests Python** : narration (6), importeur de manifest (4).
- Atlas : schéma et provenance, parents inconnus, cycles, doublons, références, versions de JSON existantes, variantes inconnues, recherche FR/EN/accents/alias, filtres et tous les modules.
- Toutes les recettes du catalogue et toutes leurs variantes ont des coordonnées finies, une géométrie bornée et un résultat identique après des sauts arbitraires d’images. Les anciens tests de caméra, actions, transitions, résurrection et sous-titres continuent de passer.
- Importeur : D1/D2, hashes unsigned, traductions manquantes, liens non résolus, définitions masquées, JSON/composants/gzip, SQLite en lecture seule, ZIP Bungie avec extension `.content`, noms de fichiers ZIP non extraits et refus des archives ambiguës. Tests également effectués sur les vrais fichiers publics, hors fixtures.
- Chromium / Playwright : **320, 360, 393 et 1280 px**. Onglet Atlas sans débordement, recherche et filtres, navigation Europe/zones, variante Riis avant le Tourbillon pour la scène, variante Fundament pour le plan, consultation des liens de sources, sauvegarde/rechargement et export final. Les tests existants couvrent toujours champs inconnus, HTML inerte, import invalide, refus du stockage, plans/éléments/durées et contenu des exports. Aucune erreur JavaScript de page.
- `npm run editor:build` puis `npm run editor:check` : bundle `docs/assets/editor.js` et contrat régénérés. Catalogue intégré localement dans le bundle ; aucun appel réseau du site pendant les tests. Chargement par lots de 20 fiches.
- `npm run report:atlas` et contrôle de cohérence du rapport.
- `Editor-Colab.ipynb` : JSON et syntaxe Python/bash valides, `REF = "main"`, liens actifs du source, bundle, GUIDE et README vers `/blob/main/remotion/tts/Editor-Colab.ipynb`. Notebook inchangé depuis la PR #8. Les nouveaux champs seront disponibles dans Colab après fusion de cette PR sur main.
- Parcours exact d’import : `scripts/import-editor.mjs episodes/atlas_demo.json`, puis `narration.py out/editor-episode.json` (cache de la génération réelle Kokoro) et validation de `out/editor-episode-ready.json`. Aucun champ Atlas écarté. Les exemples du dépôt n’ont pas besoin d’être modifiés manuellement.
- `git diff --check`.

## Rendu CPU réel

```sh
npm run narrate:atlas
npm run render:atlas -- --browser-executable=/usr/bin/chromium
python scripts/verify_narration.py --episode out/atlas_demo-ready.json --video out/atlas-of-destiny-demo.mp4
```

Le CLI conserve `--gl=swangle`, concurrence 1. Rendu complet : **720 images**, **24,000 secondes**, **1080 × 1920**, **30 fps**, H.264/AAC. Le MP4 mesure **5 161 026 octets**. Les quatre décors ont été inspectés sur des images extraites du MP4 à 1, 7, 13 et 19 secondes. Les mentions de reconstitution sont visibles ; aucun protagoniste moderne n’apparaît dans les trois scènes anciennes.

Kokoro **af_heart, 1×**, **43 mots horodatés** :

| Scène | Parole réelle | Budget |
| --- | ---: | ---: |
| Riis avant le Tourbillon | 5,200 s | 6,000 s |
| Mercure pendant l’Âge d’or | 5,075 s | 6,000 s |
| Fundament / origines de la Ruche | 4,900 s | 6,000 s |
| Europe et les installations Bray | 5,100 s | 6,000 s |

Total parlé : **20,275 secondes** ; piste complétée à **24 secondes**. Une première narration Europe trop longue a été refusée par le moteur : texte raccourci, sans accélération ni coupe. Les 43 mots ont un signal audio mesurable, restent ordonnés dans leur scène et correspondent à la narration. Les flux audio et vidéo encodés mesurent tous deux 24 secondes. Contrôle WAV/AAC sur les fenêtres existantes des quatre scènes : **0 ms** de décalage mesuré, corrélations **0,99905–0,99992**.

Le MP4, les WAV, les images et les rapports détaillés sont dans `remotion/out/` et `remotion/public/assets/narration/`, ignorés par Git. Aucun binaire de rendu n’est ajouté au dépôt.

## Limites

- **Inventaire partiel**. Les 39 contenus ont des associations documentées, mais leurs zones/activités ne sont pas toutes auditées. D1 n’expose pas de listes de bulles équivalentes aux destinations D2 ; ses sous-zones demandent davantage de fiches manuelles. Raids/activités sont distingués des lieux physiques ; toutes les cartes compétitives, secteurs oubliés, missions, événements et mondes seulement évoqués ne sont pas couverts.
- **4 décors dédiés**, 16 modules de composition et des palettes partagés, pas 468 modèles cartographiques uniques. Les substitutions et variantes sont artistiques. Même les décors dédiés sont stylisés. Riis n’a pas de plan pré-Tourbillon précisément établi ici ; le passé de Mercure s’appuie en partie sur une simulation ; Fundament s’appuie sur un récit interne à l’univers.
- Sources secondaires consultées et assertions limitées ne valent pas revue experte exhaustive du canon. Les champs vides signifient « inconnu/non revu ». La présence dans le manifest ne prouve pas l’accessibilité actuelle, et les sources en ligne peuvent évoluer.
- L’alignement des mots vient des durées phonémiques Kokoro. La comparaison WAV/AAC confirme l’encodage sans dérive ; elle ne constitue pas une annotation humaine indépendante des frontières de mots.
- Rendu et parcours de préparation exécutés ici, **pas dans une session Google Colab réelle**. La disponibilité et la vitesse des sessions gratuites restent variables. Les liens restent sur main et requièrent la fusion volontaire pour charger ce nouveau moteur.
- Interface vérifiée par émulation Chromium, **pas sur Android physique**. Sa politique de téléchargement `blob:` est restrictive : les tests capturent le Blob réellement produit et neutralisent seulement le clic ; l’enregistrement du fichier sur téléphone reste à vérifier.
- Chromium système a été utilisé avec SwiftShader. Les avertissements Node préexistants sur le type de module et les avertissements Torch non bloquants ne sont pas modifiés. Aucun nouveau GPU, modèle 3D externe ou service payant requis.
