# Riis 0.5 / 0.6 / 0.7

Les trois JSON restent distincts : `hybrid_riis.json`, `hybrid_riis_06.json`, `hybrid_riis_07.json`. Les originaux 0.5/0.6 ne sont pas modifiés.

| Élément | 0.5 | 0.6 | 0.7 |
| --- | --- | --- | --- |
| Voix / script | Kokoro, 64 mots | Identiques | Identiques, vérifiés après nouvelle synthèse CPU |
| Durée | 35 s / 1050 frames | Identique | Identique |
| Storyboard | 5 plans, 3 types | Identique | 7 plans, 5 types ; conclusion subdivisée aux silences |
| Personnages | Blocs rigides | Poses/costumes expressifs | Articulations hiérarchiques, conversation, regards, réaction et suivi |
| Caméra | Cinématique existante | Director 0.6 | Cadrage sur les participants animés |
| Atmosphère / captions | Systèmes 0.5 | Polish 0.6 | Réutilisés, sans nouvelle motivation canonique du Voyageur |

La première scène voxel montre des habitants disposés pour une conversation, puis regardant le ciel. La seconde montre une réaction collective et des suiveurs derrière un guide, avec séparation spatiale. Architecture, costumes et blocking sont artistiques, pas des données historiques attestées.

## Reproduire depuis remotion/

```sh
# Node 22.23.4, environnement Python Kokoro CPU et poids préparés.
HF_HUB_OFFLINE=1 python scripts/narration.py episodes/hybrid_riis.json
npm run prepare:polish:comparison
HF_HUB_OFFLINE=1 python scripts/narration.py episodes/hybrid_riis_07.json
# Comparaison strictement identique du WAV/timestamps de référence :
node --experimental-strip-types scripts/prepare-animation-demo.mjs
node scripts/verify-animation-render.mjs
python scripts/benchmark-animation.py --mode comparison --node node --browser /usr/bin/chromium
python scripts/benchmark-animation.py --mode profiles --node node --browser /usr/bin/chromium
python scripts/benchmark-animation.py --mode full --node node --browser /usr/bin/chromium
python scripts/verify_narration.py --episode out/hybrid_riis_07-ready.json --video out/hybrid-riis-07.mp4
```

Le script de comparaison produit `out/animation-comparison/index.html`, avec les trois MP4 locaux et huit triplets de PNG aux mêmes frames. Les médias et JSON prêts restent ignorés par Git. Six images anciennes sont vérifiées par SHA-256 ; les rigs sont rendus 660→210→660 pour vérifier l’accès hors séquence. L’aperçu aligné voxel en qualité finale est comparé au PNG final ; un aller-retour sous réduction des mouvements est aussi vérifié.

Les mesures `comparison` couvrent les mêmes 12 frames (210–221) pour les trois versions, à paramètres CPU identiques. `profiles` teste 4/8/16 civils pour chaque profil sur ces 12 frames ; ce sont des échantillons, pas des films complets ni des prédictions de fluidité Android. `full` rend les 1050 frames de 0.7. Les temps comprennent le lancement et le bundling.

Le moniteur échantillonne le processus de rendu et ses descendants avec un délai cible de 250 ms entre lectures. RSS additionné compte plusieurs fois certaines pages partagées ; PSS les répartit. Les pics par catégorie Node/Chromium/autres ne surviennent pas nécessairement ensemble. Le pic total provient d’un même échantillon. Les pointes plus courtes que l’échantillonnage et les processus devenus inobservables ne sont pas garantis capturés. Voir [rapport](REPORT.md) et [preuves](validation-evidence.json).
