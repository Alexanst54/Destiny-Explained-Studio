# Inspection préalable — Hybrid Shorts 0.5

Base inspectée avant modification du code : `main` à `3e120df` (fusion PR #10). La branche 0.5 conserve également les corrections de `directWorld` qui refusent les populations résolues >32 et les identifiants dupliqués.

## Réutilisation

- `src/voxel/episode/schema.ts` : enveloppe JSON versionnée, format 1080×1920/30 fps, scènes continues, validation de narration et mots alignés.
- `src/voxel/cinematic/CinematicEpisode.tsx`, `timeline.ts`, `motion.ts` : caméra, acteurs, événements, transitions et rendu Three.js existants.
- `atlas/` : 468 lieux et variantes, sources et recettes ; aucune coordonnée astronomique n’est fournie par le catalogue.
- `characters/`, `living/`, `weather/` : personnages, variantes, trajectoires, groupes et météo déterministes. L’héritage scène/plan doit continuer à passer par le validateur et `directWorld`, sans découpe de listes.
- `scripts/narration.py` : synthèse Kokoro CPU, cache, budgets audio par scène, alignement phonémique, WAV assemblé et JSON prêt. Le script dépend de l’enveloppe et des champs `scenes[].narration/startFrame/durationFrames`.
- `scripts/episode.mjs`, `import-editor.mjs`, `verify_narration.py` et Editor-Colab : validation stricte, rendu CPU et récupération du MP4 ; conserver leurs commandes publiques.
- `editor/model.mjs`, `app.mjs`, build statique et service worker : sauvegarde locale, projection explicite des champs inconnus, export complet et fonctionnement hors ligne après installation.

## Contraintes constatées et décisions

1. Un changement d’enveloppe indépendant casserait Colab/Kokoro : ajouter une version 0.5 à l’enveloppe, un contrat de contenu visuel par scène et une composition dédiée. Les épisodes anciens restent sur leurs compositions inchangées.
2. Le rendu cinématique mélange actuellement décor et habillage. Ajouter des options internes pour réutiliser son visuel voxel sans recopier l’implémentation ni afficher son ancien habillage dans les Shorts.
3. Le navigateur ne peut pas charger gratuitement Kokoro Python : l’aperçu partagé restera explicitement silencieux/minuté approximativement avant génération Colab. Les données d’alignement importées permettent l’aperçu exact des captions ; un minutage incomplet ne sera jamais qualifié d’exact.
4. Le lecteur Remotion est nécessaire pour partager le composant final dans le navigateur. Il sera verrouillé à la même version Remotion et chargé à la demande, sans CDN ni backend.
5. Les dispositions de carte seront des pourcentages schématiques et porteront un cartouche explicite ; les dates inconnues resteront des périodes ou des valeurs nulles.
6. Les pistes facultatives doivent être locales/embarquées et accompagnées d’une provenance/licence. Aucun asset commercial ni téléchargement audio obligatoire.
7. 15–60 secondes par Short ; recommandations 20–45. CPU : plafond hérité de 32 personnages, 128 particules météo, concurrence 1 par défaut. Qualité brouillon seulement pour l’aperçu ; sortie finale 1080×1920.
8. Préserver la publication Pages main /docs, les liens Colab main, les projets historiques et les champs inconnus des archives. Aucun workflow Actions ajouté. Tester Chromium séparément d’Android physique et de Colab réel.
