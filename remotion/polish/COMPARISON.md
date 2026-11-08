# Riis 0.5 / 0.6 — comparaison reproductible

L’original `episodes/hybrid_riis.json` reste inchangé. `episodes/hybrid_riis_06.json` conserve ses cinq plans, textes, sources, populations, trajectoires de base et durées : **35 s, 1050 frames**. Les nouveaux paramètres sont facultatifs. Retirer le polish dans la projection interne du bouton Avant reproduit les anciennes données visuelles ; l’archive complète n’est jamais réécrite.

| Plan | Amélioration 0.6 |
| --- | --- |
| 0–4 s | Question inchangée ; push-in progressif |
| 4–11 s | Orbite douce ; trois couches de ville, brume, costumes déterministes, curiosité/regard |
| 11–17 s | Carte explicitement schématique ; rapprochement sur la destination, sans coordonnées canoniques |
| 17–27 s | Tourbillon artistique ; lumière sombre, particules, tremblement subtil, peur/fuite et départs décalés |
| 27–35 s | Révélation finale ; captions cinétiques, emphase choisie sur les mots déjà présents |

Les Éliksni et l’architecture sont des abstractions voxel. Leur détail accru n’établit aucune apparence canonique. La conclusion conserve l’incertitude sur la motivation du Voyageur.

## Reproduire depuis remotion/

```sh
# Une seule voix pour les deux versions ; poids Kokoro installés au préalable.
HF_HUB_OFFLINE=1 python scripts/narration.py episodes/hybrid_riis.json
npm run prepare:polish:comparison
npm run verify:polish:render
python scripts/render-riis-comparison.py --node node --browser /usr/bin/chromium
python scripts/verify_narration.py --episode out/hybrid_riis_06-ready.json --video out/hybrid-riis-06.mp4
```

Node 22.23.4 ; dépendances verrouillées du projet. `prepare-riis-comparison.mjs` vérifie les textes, timings et références avant de réutiliser le WAV et les timestamps 0.5. Le script lance les rendus séquentiellement, même Chromium, concurrence 1, SwiftShader, H.264/AAC et qualité finale. La mesure comprend la commande complète, pas uniquement l’encodage.

Résultats locaux : `out/riis-comparison/index.html` présente les vidéos et cinq paires de PNG aux frames 45, 210, 420, 660 et 990. Les médias restent ignorés par Git. `performance.json` enregistre durées, octets, SHA-256 et ffprobe. Le RSS est le maximum observé des processus enfants, **pas** la somme de toute la mémoire Chromium ; la machine partagée n’est pas un banc de mesure isolé. Lors de la validation livrée, la référence 0.5 est achevée avant 0.6 ; un redémarrage de l’environnement a imposé de relancer 0.6 sur la même configuration matérielle exposée. Il ne s’agit donc pas d’un benchmark statistique à charge contrôlée.

Les preuves textuelles sont archivées dans [validation-evidence.json](validation-evidence.json) et les mesures sont interprétées dans le [rapport](REPORT.md). Les empreintes PNG testent la stabilité sur cette pile logicielle, sans promettre l’identité bit à bit entre systèmes ou versions de navigateur.
