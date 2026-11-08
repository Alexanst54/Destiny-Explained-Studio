# Rapport 0.6 — Viral Editing & Visual Polish

Base : `main` après PR #11, `1a402fb764f71ee86870cf0e74c7c5cf856805a7`. Branche : `feat/viral-editing-0.6`. Inspection avant changements : [INSPECTION.md](INSPECTION.md). Aucune fusion automatique.

## Livraison

Quatre styles supplémentaires de captions partagés aperçu/MP4 ; onze choix de caméra dont « aucun » ; quatre réactions et cinq gestes dont « aucun » ; trajectoires adoucies et exode ; costumes déterministes ; six ambiances artistiques à budgets et ombres de contact. Le storyboard ajoute panneaux persistants, préréglages, annuler/rétablir, avant/après, conseils selon quatre profils et narration locale WAV/MP3. Le catalogue documentaire, l’Atlas et les démos 0.1–0.5 sont conservés.

Riis 0.6 reprend chaque mot et chaque durée de 0.5. Les sources restent celles du projet d’origine ; aucune motivation nouvelle du Voyageur ni fiche historique n’est ajoutée. La reconstitution et les modes hypothèse/alternative conservent leurs indications dans la vidéo.

## Tests exécutés

- Baseline avant changements : 56 tests Node et 11 Python réussis.
- Suite finale : 65 tests Node, 11 Python ; TypeScript et cohérence du build statique.
- Cinq suites Chromium : éditeur historique, Living Worlds, hors ligne, Hybrid Shorts et Polish. Les suites tactiles couvrent 320, 360, 393 et 1280 px ; pas de débordement horizontal ni erreur de page observés. Boutons principaux ≥44 px. Le téléchargement est capturé sous forme de Blob, pas enregistré par le gestionnaire Android.
- WAV local réel : lecture/pause/reprise/seek/mute ; MP3 décodé ; durée et recherche dans le média observées. Aucun téléversement, URL audio absente du JSON, fichier non restauré après reload. Le fichier de test est un son original généré, pas une ressource externe.
- Schémas, bornes, compatibilité, budget de 32 acteurs, identifiants, héritage, export/import et champs inconnus : suites existantes + neuf tests 0.6. Les options de scène 0.6 sur une composition qui ne les rend pas sont refusées explicitement.
- Les sept styles de captions sont aussi testés dans le DOM Chromium à 320 px avec un mot de 100 caractères, sans débordement observé. Tous les préréglages caméra et styles de captions sont testés par frame ; poses, particules, budgets et groupes déterministes. Réduction des mouvements et transitions historiques couvertes.
- Quatre PNG historiques identiques aux SHA-256 de 0.5 : Riis hybride, Voyageur, Atlas, Europe Living Worlds. Cinq paires avant/après produites ; rendu 660→45→660 identique ; aperçu aligné/final carte identiques ; Avant reproduit l’image 0.5.

Un premier rendu 0.6 s’est arrêté à la frame 120 après 27,75 s : le nouveau refus de paramètres hybrides non rendus interceptait aussi la projection interne voxel. L’adaptateur retire désormais ces champs de sa copie historique et les transmet séparément au renderer partagé ; un test couvre cette projection. La tentative est conservée dans les preuves. Un second essai a été interrompu à la frame 226 par le redémarrage de l’environnement, sans résultat MP4 validé. Le rendu final est donc relancé intégralement ; seules les exécutions achevées alimentent les mesures ci-dessous. Les contrôles de build ont aussi détecté des bundles périmés pendant les modifications ; ils ont été régénérés avant la validation finale.

Commandes reproductibles : [README](README.md) et [COMPARISON](COMPARISON.md). Les tests Python utilisent des doublures pour certaines préparations de voix ; le rendu de référence utilise le véritable WAV Kokoro de la chaîne existante, réutilisé sans régénération puisque script et timings sont identiques.

## Mesures CPU

Deux rendus complets réussis sur Linux, Intel Xeon Platinum 8370C (3 processeurs logiques exposés, environ 9,7 Gio RAM), Node 22.23.4, Chromium 156.0.8078.79, Remotion 4.0.541, SwiftShader `swangle`, concurrence 1. Même voix et timestamps ; qualité finale 0.6 avec 96 particules au budget, 30 structures et 6 figurants sur les plans voxel.

| Mesure réelle | Riis 0.5 | Riis 0.6 |
| --- | ---: | ---: |
| Commande complète | 292,40 s | 371,91 s |
| Images | 1050 | 1050 |
| MP4 | 7 005 278 octets | 11 926 108 octets |
| Maximum RSS enfant observé | 639 304 Kio | 630 308 Kio |
| Vidéo | 1080×1920, 30 fps, H.264, 35,000 s | identique |
| Audio | AAC, 48 kHz stéréo, 35,008 s | identique |

Le surcoût de temps observé est **+27,2 %**. Ces valeurs proviennent d’une seule exécution achevée de chaque version sur machine partagée ; quelques tests ont utilisé le CPU pendant les rendus et l’environnement a redémarré entre les tentatives 0.6. Elles ne constituent pas un benchmark statistique ni une prévision de temps Colab. Le RSS est un maximum de processus enfant, **pas la mémoire totale simultanée de Chromium** ; son léger écart ne prouve pas un gain mémoire.

Les contrôles audio comparent le WAV source à l’AAC décodé sur cinq fenêtres, et vérifient le signal des 64 mots alignés. Décalage mesuré : 0 ms dans chacune des cinq fenêtres, pour les deux versions ; corrélation minimale 0,9702. Les 64 mots ont un signal mesurable. Le padding AAC de 8 ms en fin de fichier est attendu. Voir les valeurs détaillées, empreintes MP4, PNG et fichiers voix dans [validation-evidence.json](validation-evidence.json). Les mots conservent strictement les timestamps Kokoro ; ce contrôle ne remplace pas une annotation humaine des frontières phonétiques.

Les MP4 et la galerie sont disponibles localement sous `out/hybrid-riis.mp4`, `out/hybrid-riis-06.mp4` et `out/riis-comparison/index.html`, sans ajout à Git.

## Limites et suites possibles

- Android physique et Colab distant **non exécutés**. Chromium tactile et CPU Linux ne les remplacent pas.
- Voix locale uniquement en mémoire, à resélectionner ; pas de Kokoro dans le navigateur ni d’alignement automatique d’un fichier arbitraire. Les timestamps phonémiques Kokoro ne sont pas une annotation humaine indépendante.
- Focus simulé, transition carte→voxel par cadrage ; pas de profondeur de champ optique, correspondance spatiale universelle ni vraie reconstruction astronomique.
- Cibles de tête fixes ; expressions et exode stylisés, sans collisions ni navigation. Les silhouettes ne sont pas des modèles canoniques détaillés.
- Les budgets des effets 0.6 ne plafonnent pas tous les éléments historiques de l’Atlas. Les particules baissent en draft, jamais les acteurs. L’aperçu voxel peut perdre en fluidité sur un téléphone ancien.
- Les conseils analysent la structure et la densité, pas le sens du lore ou la qualité d’une explication. Ils ne prédisent aucune viralité et ne modifient rien automatiquement.
- Les régressions visuelles sont contrôlées par quatre images représentatives, pas par un nouveau rendu intégral de tous les anciens épisodes.

Pour 0.7 : essais Android/Colab réels, sélection tactile des cibles de caméra/personnages, édition fine de l’emphase par occurrence et enveloppes d’expression, amélioration des silhouettes, profilage CPU/mémoire agrégé et réglage automatique facultatif de l’aperçu.

## Inventaire

Voir [FILES.md](FILES.md) pour chaque fichier modifié. Aucun MP4/WAV/PNG généré ni poids Kokoro versionné. Aucune dépendance supplémentaire, aucun changement de publication Pages et aucun workflow Actions ajouté.
