# Destiny Studio — production autonome Colab Pro

[Ouvrir le notebook dans Colab](https://colab.research.google.com/github/Alexanst54/Destiny-Explained-Studio/blob/feat/standalone-colab-production-studio/remotion/blender/Destiny-Studio-Colab-Pro.ipynb)

Une seule interface, sans PC local ni terminal : Atlas → Blender → Kokoro anglais/français → horodatages des mots → Remotion → MP4 H.264/AAC. **GitHub Actions est facultatif et ne participe à aucune étape de production, de validation ou de téléchargement.** Les outils et modèles sont téléchargés depuis leurs distributions officielles, pas depuis des artefacts Actions.

## Épisode Atheon complet ce soir

Le nouveau parcours **Render Complete Atheon Episode** réutilise les six voix et le plan de 89,067 secondes. [Instructions exactes de lancement et de reprise](COMPLETE-ATHEON.md) : installation rapide, préflight, première scène complète comme smoke-test, rendu reprenable des six scènes, assemblage Remotion et téléchargement.

## Du boss au MP4

1. Ouvrir Colab dans Android Chrome, se connecter et choisir un runtime GPU T4 si disponible. Exécuter la cellule 1, autoriser le montage de son Drive. Elle installe Blender officiel 4.3.2, Node 22.23.4, les dépendances npm verrouillées et un environnement vocal isolé (Torch/torchaudio CPU 2.6, Kokoro 0.9.4, stable-ts). L’installation initiale et les modèles nécessitent plusieurs Go libres et une connexion réseau.
2. Exécuter le formulaire. Les six boss réellement disponibles sont proposés : Athéon, Templier, Cropta, Oryx, Rhulk, Nezarec. Les quatre derniers restent des prototypes, sans nouvelle approbation artistique. Les listes d’animation/caméra/arène changent avec le boss. Une seule arène est proposée si le générateur n’en implémente qu’une. Aucun modèle générique ne remplace un boss absent.
3. Choisir qualité, durée (2–600 secondes, arrondie à une frame), texte dans la langue choisie, langue `fr-FR`/voix `ff_siwis` ou `en-US`/voix `af_heart`, sous-titres, résolution, 24/30 FPS et dossier Drive. Un fichier musical fourni est facultatif ; renseigner sa provenance/licence. Aucune musique du jeu n’est téléchargée. Enregistrer le projet.
4. Lancer le **smoke-test de deux secondes** : même boss/animation/caméra, Draft, résolution réduite conservant le ratio de sortie (320×240 pour Preview), LOD0, phrase française « Voici ce boss. ». Vérifier visuellement et écouter le MP4. Le smoke-test ne constitue pas une validation du rendu final HD ou de toutes les animations.
5. Cocher l’inspection du smoke et lancer la production. Kokoro utilise le chargeur et la révision déjà épinglés du pipeline existant ; un adaptateur séparé sélectionne le français ou l’anglais. Le français utilise Whisper `base`/stable-ts pour l’alignement sur la parole réelle ; l’anglais réutilise les timestamps natifs de synthèse du pipeline Kokoro existant. Les légendes n’utilisent pas des durées uniformes inventées. Les épisodes historiques et leur voix anglaise restent inchangés.
6. Si la narration dépasse la durée demandée, le studio refuse avant les images de production. Augmenter la durée dans **un nouveau projet**, ou raccourcir le texte. La parole n’est jamais tronquée ni accélérée. Après les images, Remotion assemble une vraie séquence, la voix et les sous-titres ; la musique fournie est mixée à faible volume et bouclée.
7. Le dernier formulaire vérifie de nouveau le fichier, affiche la vidéo et permet son téléchargement. Une copie permanente est déjà dans Drive. Les vérifications portent sur codec H.264/yuv420p, AAC, FPS, dimensions, nombre de frames décodées, durées audio/vidéo, décodage complet et audio non silencieux.

## Fichiers Drive et reprise

Chaque projet conserve `selection.json`, `project.json`, `speech.wav`/`speech.json`, `blender/chunk-*/progress.json`, les frames, `public/`, `props.json`, `logs/`, `video.mp4` et `validation.json`. Le smoke est dans `smoke/`. Les sources et la configuration sont liées au manifeste immuable. Conserver ce dossier et le même commit ; une nouvelle session n’a pas besoin de l’ancienne RAM.

Après interruption, renseigner le chemin Drive dans `projet_a_reprendre` de la cellule 1. Elle restaure le commit `sourceCommit` du manifeste (uniquement si les sources enregistrées étaient propres), puis relancer installation/montage, restaurer le dossier avec la cellule 2b et relancer la même étape. Les PNG sont décodés et vérifiés par CRC/SHA avant réemploi ; les frames corrompues sont recalculées. Les blocs de **120 frames maximum** réutilisent le moteur universel existant : un Blender par bloc, pas par frame. `startFrame` reste global et continu, y compris aux frontières des blocs. Le cache intersession contient de la géométrie JSON et des PNG, pas un `.blend` sauvegardé. Remotion peut réexporter le MP4 après reprise, mais les frames Blender valides restent réutilisées.

Changer paramètres ou source requiert un nouveau dossier, pour éviter de mélanger des rendus incompatibles. Le notebook ne fait pas de `git pull` automatique dans un projet actif. Pour reprendre après modification de la branche distante, utiliser ce champ du notebook pour rétablir le commit indiqué par le projet ; sinon créer un nouveau projet. Aucun terminal n’est nécessaire. Un échec garde les journaux et n’est jamais annoncé comme une réussite.

L’estimation de temps apparaît après des frames mesurables ; elle reste indicative. Les backends/appareils effectifs sont consignés par frame dans les rapports Blender. Le rapport global ne déclare un rendu GPU que lorsque toutes ses frames ont réellement été rendues sur GPU. OPTIX est essayé avant CUDA par le détecteur existant ; le CPU reste disponible avec avertissement explicite. Aucun commit de PR #17 n’est intégré.

## Contrôles locaux, indépendants de GitHub

```sh
python -m unittest discover -s remotion/studio -p 'test_*.py'
python -m unittest discover -s remotion/blender/tests
node --experimental-strip-types --test remotion/studio/studio.test.mjs
node remotion/node_modules/typescript/bin/tsc --noEmit -p remotion/studio/tsconfig.json
python remotion/blender/universal/lot_c_evidence.py --check
```

CLI équivalente : `python remotion/studio/production.py selection.json /chemin/projet --smoke --blender /chemin/blender`, puis la même commande sans `--smoke`. Node 22 doit être dans le PATH, ou fourni avec `--node`. `--chrome` permet un Chromium local ; Colab installe le navigateur Remotion officiel. La production sans smoke validé pour la même sélection est refusée.

## Acceptation réelle Colab/T4 et Android

La cellule 6 du notebook peut vérifier les backends/appareils réels et une reprise chaude, puis enregistrer `t4-acceptance.json`. La lecture Android est une confirmation humaine distincte, jamais déduite du test GPU. Ces vérifications doivent être exécutées sur le matériel, pas déduites de tests CPU :

- Installer depuis un runtime neuf avec Drive, sans exécuter ni attendre Actions. Noter commit, GPU, version Blender et espace libre.
- Sur T4, lancer le smoke, vérifier dans les rapports les noms NVIDIA et backend `OPTIX` ou `CUDA`, puis visionner et écouter depuis Android Chrome. Un simple résultat `nvidia-smi` ne prouve pas l’utilisation GPU.
- Produire d’abord un court projet Balanced, puis vérifier H.264/AAC, FPS, nombre de frames, durées et lecture Android. Inspecter synchronisation des mots, identité, cadrage et contacts au sol. Ne pas confondre succès technique et approbation artistique.
- Interrompre après quelques frames, reconnecter Drive, reprendre à source/réglages identiques. Vérifier les `cacheHits` et l’absence de nouvelles frames pour les PNG valides. Sur une copie de test, corrompre un PNG et vérifier qu’un seul est recalculé.
- Tester un petit projet de plus de 120 frames pour confirmer la frontière de blocs, puis seulement une longue production. Contrôler les gestes : certaines animations de boss sont des actions ponctuelles qui terminent en posture de repos, pas une chorégraphie de dix minutes.
- Tester sous-titres désactivés, autre voix seulement si ajoutée et validée, et une musique fournie avec crédit. Tester le repli CPU et les messages d’erreur ; ne pas prétendre qu’une panne/OOM GPU a été validée sans la provoquer réellement.
- Archiver les rapports et le résultat de revue humaine dans Drive.

Les tests Colab/T4/Android et les performances GPU restent non validés tant qu’ils n’ont pas été exécutés. Le rendu local et son rapport sont documentés dans [VALIDATION.md](VALIDATION.md). La facturation GitHub Actions ne peut pas bloquer ce notebook : aucune API Actions ni attente de statut CI n’est utilisée.

## Pilote anglais — Atheon

[Who Is Atheon, Time’s Conflux?](../../episodes/atheon-explained-en/README.md) : six scènes fournies, `en-US`, `af_heart`, titres et sous-titres anglais, format vertical 9:16. La cellule dédiée du notebook prépare uniquement la voix et les sélections de scènes dans Drive. Le plan mesuré fait 89,067 secondes sans accélération ni coupe. Le rendu complet est différé à la session Colab Tesla T4 de l’utilisateur. Le français reste disponible et ses preuves antérieures sont conservées.

## Performance investigation and directed Atheon edition

The opt-in [performance/cinematic guide](PERFORMANCE-CINEMATIC.md) documents the paired 30–60-frame T4 benchmark and separate cinematic project controls. Run that benchmark before recommending a complete rerender. Existing validated outputs and their saved source commits remain usable.

For `atheon-smoke` route confusion, use [R0 and M1–M3](SMOKE-ROUTE-AND-MOTION.md) to inspect the old project read-only and render a separate three-second moving-camera diagnostic.

The [standalone GPU Optimization Lab](GPU-OPTIMIZATION-LAB.md) provides O1–O4 in a **separate notebook**, with local-only temporary storage and a downloadable report ZIP. The production notebook is unchanged by this lab extension.
