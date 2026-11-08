# Validation Kokoro — épisode 002

Environnement : Linux x64, Python 3.12, PyTorch 2.6.0+cpu, Kokoro 0.9.4,
Misaki 0.9.4, Node 22.23.4, Remotion 4.0.541 et Chromium système 156.
Voix `af_heart`, vitesse 1×, modèle public à la révision
`f3ff3571791e39611d31c381e3a41a3af07b4987`. Aucun appel OpenAI effectué.

## Synthèse réellement exécutée

| Scène | WAV synthétisé | Budget de scène | Silence ajouté en fin | Mots |
| --- | ---: | ---: | ---: | ---: |
| scene-01 | 6.325 s | 8.000 s | 1.675 s | 16 |
| scene-02 | 10.000 s | 10.000 s | 0.000 s | 23 |
| scene-03 | 9.675 s | 10.000 s | 0.325 s | 19 |
| scene-04 | 11.750 s | 12.000 s | 0.250 s | 26 |
| scene-05 | 7.800 s | 10.000 s | 2.200 s | 23 |
| scene-06 | 8.150 s | 10.000 s | 1.850 s | 19 |

Les six WAV totalisent **53,700 secondes** (pauses natives comprises). La piste
assemblée contient exactement 1 440 000 échantillons à 24 kHz, soit **60 secondes**.
Le texte, les départs de scènes et leur durée totale sont conservés. Aucun
rééchantillonnage temporel, accélération ou découpage de parole n’a été effectué.
La scène 02 occupe exactement son budget ; un autre texte ou modèle peut dépasser
ce budget et sera alors refusé. Aucun silence initial artificiel n’est ajouté.

## Synchronisation

126 mots provenant des tokens horodatés de Kokoro ont été associés au texte exact.
Les contractions sont conservées. Les intervalles restent ordonnés et dans leur
scène. Les durées des mots varient de 0,050 à 1,200 seconde : elles ne sont pas
réparties uniformément. Les 126 intervalles contiennent un signal audio mesurable
(RMS minimal ≈ 0,00964). Ces horodatages sont dérivés des durées phonétiques de
la synthèse ; ils ne constituent pas une annotation humaine indépendante.

## Tests automatisés

- TypeScript : réussi ; trois tests voxel et six tests JSON : réussis.
- Six tests Python : réussis (mapping des tokens, absence de timings estimés,
  offsets et débordements, blocage OpenAI, chemins sûrs, cache et assemblage).
- Les voix simulées des tests unitaires servent uniquement à contrôler la chaîne ;
  les durées du tableau proviennent de la synthèse Kokoro réelle.
- `pip check` : aucun conflit de dépendances.
- Syntaxes Python, Bash et JSON du notebook Colab : vérifiées.

## Rendu intégral avec audio

`npm run render:episode:voiced -- --browser-executable=/usr/bin/chromium --concurrency=2`
a produit le MP4 complet de l'épisode 002 : **H.264, 1080 × 1920, 30 fps,
1800 images, 60 secondes**, avec une piste **AAC 48 kHz de 60,011 secondes**.
Le faible surplus audio correspond aux paquets d'encodage AAC. Le décodage
intégral par ffmpeg réussit. Le rendu utilise `swangle` sur CPU.

`npm run verify:narration` a comparé une seconde audio par scène entre le WAV
source et l'AAC décodé : **décalage de 0 ms sur les six fenêtres**, corrélations
comprises entre 0,99816 et 0,99996. Il s'agit d'un contrôle du transfert audio
et de son placement dans la vidéo, pas d'une annotation phonétique indépendante.

Une image extraite du MP4 à 14,2 secondes a été inspectée : « Golden » est
surligné, conformément à l'intervalle 13,8375–14,275 s du JSON des mots ; le
bandeau d'aperçu est absent. Le style voxel et le décor de la Tour restent présents.
Une relance réelle de la génération a réutilisé les six WAV validés en cache,
sans initialiser de nouveau le modèle ni effectuer d'appel payant.

## Périmètre

Le style et les modèles voxel, le décor de la Tour et le Voyageur, les caméras,
les compositions existantes et `index.html` sont conservés. Seule la gestion
des sous-titres alignés est renforcée pour éviter les mots d’une autre scène.
Les modèles, WAV, sous-titres générés et MP4 sont ignorés par Git.

Le notebook Colab n’a pas été exécuté sur un téléphone Android dans cette tâche.
Le fournisseur OpenAI et son alignement stable-ts restent optionnels et non
testés avec un appel payant. La prononciation des noms propres et le contenu
du script doivent être revus à l’écoute avant publication.
