# Validation du studio autonome — 2026-11-10

Base inspectée avant développement : PR #22 `e3a7e2c`, PR #23 `2baffff`, dernière tête de PR #24 **`a87446182441e4b4e7652f637fe740a58118c279`**. Branche dédiée empilée sur la branche Lot C. Aucun merge/cherry-pick de PR #17 ; aucun modèle, épisode historique, contrat ou narration existante n’est modifié.

## Vidéos réellement produites

- [Smoke narré et sous-titré](smoke/video.mp4) : Rhulk, arène `vow-of-disciple`, combat, caméra cinematic, Draft, **LOD0**, 320×240, **48 frames à 24 FPS / 2 secondes**, H.264/yuv420p BT.709 + AAC. Les frames proviennent réellement du renderer Blender universel, puis de la nouvelle composition Remotion. Aucun mockup ni frame interpolée.
- [Variante sans sous-titres et avec son de test bouclé](smoke/music-no-captions.mp4) : même séquence Blender, voix française et signal original 440 Hz fourni au pipeline, créé pour ce test. Ce signal n’est pas une musique de Destiny ni une recommandation musicale. La source dure une seconde ; son énergie est effectivement mesurée à 1,9 seconde, après la voix, pour contrôler la boucle et le mixage à faible volume.
- [Aperçu des sous-titres](smoke/caption-preview.png), [voix brute](smoke/speech.wav), [alignement réel](smoke/speech.json), [rapport vidéo](smoke/validation.json), [rapport Blender](smoke/blender-report.json), [empreintes](smoke/evidence.json).

Kokoro 0.9.4, chargeur existant et révision `f3ff3571791e39611d31c381e3a41a3af07b4987`, voix française `ff_siwis`, langue `f`, vitesse 1×. La phrase « Voici ce boss. » produit **1,775 seconde** ; stable-ts/Whisper multilingue `base` aligne les trois mots sur la vraie parole. Les bornes enregistrées sont 0,54–0,76 ; 0,76–0,94 ; 0,94–1,24 seconde. Pas de durées uniformes inventées. Les exports incluent le complément silencieux jusqu’à deux secondes ; AAC dure environ 2,005 secondes avec son padding de codec, dans la tolérance contrôlée.

Le premier export diagnostic a été rejeté : les réglages JPEG historiques donnaient du `yuvj420p` pleine plage. Seul le nouveau studio force PNG/BT.709/yuv420p ; les réglages historiques ne changent pas. Les 48 frames Blender déjà terminées ont été conservées, puis copiées dans des dossiers de validation neufs après les corrections de l’orchestrateur. Leur manifeste renderer, configuration et SHA ont été vérifiés par le renderer avant réemploi : **aucun nouveau rendu Blender** n’était nécessaire pour corriger l’encodage Remotion. Il ne s’agit pas de frames simulées.

Sur la version source propre `bb3cc119b670c67fd13c6a935e0e073ff1480ffb`, le smoke, le chemin CLI de production normal et une nouvelle invocation de reprise passent. [Reprise mesurée](smoke/resume-proof.json) : **48 cache hits, zéro nouvelle frame**, empreintes identiques, cache de design utilisé et fichier de parole inchangé. Les rapports finaux contiennent le commit et les sources ; des commits documentaires ultérieurs n’altèrent pas le code de production testé. Le MP4 est réexporté par Remotion à la reprise, ce qui est distinct du recalcul Blender.

## Contrôles locaux passés

| Contrôle | Résultat |
| --- | --- |
| Node : suite Remotion existante, export/séquences Blender et captions du studio | **113/113** |
| Python : studio (options, identités, arènes, chunks continus, cache incompatible, découpage français, ratio smoke, notebook compilable) | **7/7** |
| Python : régression Blender | **56/56** |
| Python : import manifeste | **4/4** |
| Python : narrations historiques | **10/10** |
| TypeScript | Trois configurations : studio, application historique, Atlas universel |
| Blender natif 4.3.2 | 240 poses LOD0 + 36 projections par boss Lot C, LOD1/2 et sept yeux visibles de Nezarec ; aucune régression détectée |
| Intégrité Lot C | 15 fixes, 108 frames et **121 fichiers protégés** inchangés |
| Chromium desktop, viewport 390×844 | Lecture réelle H.264/AAC, durée et dimensions correctes, horloge de lecture avançant au-delà de 0,7 s |
| Audit / couverture | Rapports régénérés ; aucune référence d’asset manquante |
| Vérification autonome de la preuve livrée | `python remotion/studio/verify_smoke.py` passe, sans Torch, téléchargement vocal, Blender ni Actions |

Exécuter le test navigateur après `python -m http.server 8011 --bind 127.0.0.1` à la racine : `node remotion/studio/browser.test.cjs`. Ce lecteur desktop à largeur mobile ne prouve **pas** le fonctionnement du formulaire Colab sur Android.

## Limites et tests restant à exécuter

Matériel local : CPU AMD EPYC, Blender 4.3.2, Cycles, trois threads configurés. Torch/torchaudio 2.6 CPU et Python 3.12. Aucun GPU réel utilisé ; **aucune validation T4/CUDA/OptiX, Colab Pro ou Android réelle**. Aucune amélioration GPU ni performance de production longue n’est revendiquée. Les cellules Colab sont compilées et leurs composants sont testés localement ; l’installation complète sur un runtime Colab neuf reste à exécuter.

Le notebook propose une cellule d’acceptation qui refuse de déclarer T4 si une frame est CPU ou si le nom d’appareil/backend ne correspond pas. La lecture Android est une confirmation humaine séparée. L’interruption matérielle Colab et l’OOM GPU restent à tester selon le [protocole](README.md#acceptation-réelle-colabt4-et-android). La reprise chaude du studio a été exécutée ; le test de crash forcé du renderer existant demeure dans les preuves Lot C, sans être présenté comme un nouveau test d’interruption Colab.

Le découpage de longues vidéos est testé aux frontières (120 + 120 + 3 frames sans trou ni doublon). Aucune vidéo longue ni épisode de 35 secondes n’a été lancé ; le rendu local démonstratif dure deux secondes. Les presets de boss restent ceux de la bibliothèque, avec leurs limites artistiques et gestes parfois ponctuels. Le smoke conserve le ratio de sortie pour permettre d’inspecter le cadrage avant production. Une prononciation parfaite des noms propres, tous les longs textes et l’inspection humaine de toutes les résolutions ne sont pas revendiqués.

GitHub Actions n’est utilisé ni attendu à aucun stade. La facturation/indisponibilité de runners ne bloque pas la production Colab : installation, narration, rendu, composition, validation et export sont tous locaux au runtime et aux fichiers Drive. Le CI d’une PR reste un contrôle facultatif, distinct des résultats locaux ci-dessus.

## Mise à jour linguistique du pilote anglais

Les preuves françaises ci-dessus restent inchangées. Le Studio prend désormais aussi `en-US` avec `af_heart` et les timestamps natifs du pipeline Kokoro anglais. Le [pilote Atheon](../../episodes/atheon-explained-en/README.md) dispose de six mesures audio et d’un plan de 89,067 secondes en 9:16. Aucun épisode complet n’est rendu pendant ce travail ; le français est vérifié par un nouveau WAV identique à la référence. La version vocale anglaise est testée en préparation audio seule, sans nouvelle validation GPU, Colab ou Android.
