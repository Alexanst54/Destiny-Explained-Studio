# Hybrid Shorts Director 0.5 — livraison pour revue

Base inspectée : `main` à `3e120dfc4e6a01fa7eaba03800d9ccce6eea439b`, après fusion Living Worlds 0.4 et ses garde-fous de budget. Branche : `feat/hybrid-shorts-0.5`. Aucune fusion automatique. GitHub Pages reste **main /docs** et les liens Colab publiés restent sur main.

## Fonctionnalités

- **5 types de plans** dans la même enveloppe versionnée : voxel, carte schématique, timeline, graphique et texte cinématique. Registre extensible et schémas TypeScript/Zod stricts.
- Réutilisation du rendu cinématique, de l’Atlas et de Living Worlds, sans duplication des modèles, trajectoires, populations, météo ou caméras. Les refus de dépassement de population et d’identifiants dupliqués restent actifs ; aucune liste n’est tronquée.
- Storyboard mobile avec ajout, duplication, suppression confirmée, réorganisation par boutons, durée, narration, textes, transitions, sources et accès aux réglages voxel existants.
- **6 modèles** éditables : Did You Know?, The Story of…, Destiny Mysteries, Timeline, What If?, Character Origins. Répartition d’un script fourni, sans invention automatique de faits. Indicateurs de rythme explicitement éditoriaux.
- **3 styles de captions**, segmentation, mot actif, zone sûre et mots longs. Timestamps complets validés ; repli estimé explicite. Le JSON prêt 0.5 embarque ses mots alignés.
- Lecteur Remotion chargé à la demande, composant de rendu partagé et typographie isolée du CSS de l’éditeur. Écoute de la narration dans le MP4 ; l’aperçu du téléphone reste silencieux pour cette piste.
- Audio facultatif local/embarqué, volume par piste, périodes, fondus et ducking déterministes ; manifeste de provenance/licence. Aucune musique externe dans les démos.
- **7 entrées de transition** légères ; flash plafonné, animations SVG/texte et progression narrative. Réduction des mouvements respectée dans l’aperçu.
- Modes canon/reconstitution/hypothèse/alternatif. What If? impose un statut hypothétique et un cartouche NOT CANON. Cartes explicitement schématiques, dates inconnues conservées, sources existantes réutilisées.

## Référence rendue

**Why Did the Traveler Leave Riis?**, anglais, **35 secondes**, 5 plans :

| Période | Plan |
| --- | --- |
| 0–4 s | Question/hook |
| 4–11 s | Riis avant le Tourbillon, voxel et civils éliksni |
| 11–17 s | Départ sur carte schématique |
| 17–27 s | Catastrophe et exode, voxel, fuite et météo illustrative |
| 27–35 s | Conclusion distinguant événements et motivations non établies |

Le script ne prétend pas établir une motivation unique du Voyageur. La météo et les silhouettes sont des reconstitutions. Les sources sont celles de l’Atlas. Deux démos supplémentaires de 20 s : **The Origins of Oryx** (Krill + timeline, Livres du Malheur) et **What Was the Black Garden?** (voxel + graphique, références vex existantes). Aucun fait historique supplémentaire n’a été ajouté au catalogue pour remplir ces projets.

## Validation réellement exécutée

- État initial de main : **47 tests Node réussis**.
- Dernière suite complète exécutée : **56 tests Node réussis**, soit 47 existants et 9 hybrides ; **11 tests Python réussis**, dont le retour du JSON prêt avec mots embarqués.
- Après les derniers ajustements du découpage de script, les **9 tests unitaires hybrides** ont de nouveau été exécutés avec succès dans le bac à sable.
- `typecheck`, reconstruction de l’éditeur, `editor:check` et contrôle des espaces Git réussis sur les sources finales.
- Quatre parcours Chromium réussis : ancien éditeur, Living Worlds, rechargement hors ligne et storyboard hybride. Réorganisation, duplication/suppression, contenu, persistence/import-export, lecteur partagé et absence d’erreur de page.
- Largeurs **320, 360, 393 et 1280 px**, émulation tactile, sans débordement horizontal dans les panneaux contrôlés. Les trois styles de captions ont été exercés à 320 px avec un mot de 100 caractères et des timestamps complets, sans débordement ni faux cartouche de repli.
- Les schémas, sources, connexions, périodes, IDs, héritages, budgets, refus de suppression silencieuse, transitions, cartes, timelines, captions, mixage et exports sont couverts par les tests.
- Rendus PNG réels des 3 nouvelles démos et de 3 projets anciens. Les PNG anciens Traveler, Atlas et Living Europa correspondent exactement aux SHA-256 de la validation 0.4.
- Rendu hors séquence `45 → 390 → 45` : images 45 identiques. Les PNG du plan graphique/captions avec timestamps réels sont également identiques entre mode aperçu et mode final.
- Synthèse Kokoro CPU réellement exécutée avec `HF_HUB_OFFLINE=1`, après disponibilité des ressources locales.
- Mixage AAC réel sur un extrait de **30 images / 1 s**, narration + oscillateur original 220 Hz. La différence RMS avec l’intervalle narration seule est **0,0388194** ; enveloppes et ducking couverts aussi par les tests unitaires. Aucune ressource commerciale ni binaire ajouté au dépôt.

**Limite de la dernière relance :** la relance finale supplémentaire des suites hors bac à sable n’a pas été exécutée. Le système d’approbation automatique a atteint une limite d’usage et n’a pas pu terminer sa revue ; ce n’était pas une décision indiquant que la commande était dangereuse. Les résultats réussis ci-dessus sont ceux des exécutions précédentes et du contrôle unitaire final, pas une relance supposée réussie. Les derniers ajouts de guide/cache ne bénéficient pas d’une nouvelle exécution complète du navigateur après cette interruption.

## Mesures CPU et synchronisation

Environnement Linux géré, Node **22.23.4** pour tests/rendu, Python 3.12, Remotion **4.0.541**, Three **0.170.0**, Kokoro **0.9.4**, PyTorch **2.6.0+cpu**, Chromium système et SwiftShader (`swangle`), concurrence **1**. Allocation de session : quota 2 CPU et 8 Gio. D’autres vérifications ont tourné pendant une partie du rendu : ce n’est pas un benchmark isolé de Google Colab.

- Rendu complet réussi : **298,16 s** (4 min 58 s).
- Vidéo : **1080 × 1920**, **30 fps**, **1 050 images**, **H.264**, **35,000 s**.
- Audio : **AAC**, 48 kHz, stéréo, **35,008 s** ; 8 ms de paquet final, pas de dérive mesurée.
- Taille du MP4 : **7 005 278 octets**.
- Maximum RSS des enfants suivis : **618 656 Kio**, environ **604 Mio**. Ce n’est pas la somme ni le pic total de tous les processus Chromium simultanés/détachés.
- **64/64 mots avec audio**. Les cinq fenêtres de comparaison WAV/AAC mesurent un décalage de **0 ms**, corrélations de **0,9702 à 0,99995**. Les frontières de mots proviennent des prédictions phonémiques de Kokoro, pas d’une annotation humaine indépendante.

Le MP4 et les captures restent dans `remotion/out/` ignoré par Git. Les hashes, sondes, mesures, comparaisons et résultats de mixage sont consignés dans [validation-evidence.json](validation-evidence.json). Le script `verify-hybrid-render.mjs` reproduit les contrôles PNG. Aucune vidéo n’a été téléchargée vers un service payant.

## Compatibilité et Colab

Les épisodes 0.1–0.4 gardent leur contrat et leur composition. La composition voxel reçoit seulement des options internes facultatives pour retirer son ancien habillage dans un Short ; les valeurs par défaut conservent le rendu historique. La preuve PNG couvre trois anciens projets, pas une régénération complète de tous leurs MP4.

La seule nouvelle dépendance directe est le lecteur Remotion, à la même version verrouillée que le moteur. L’Atlas et les registres Living Worlds restent inchangés. Aucun workflow GitHub Actions ni paramètre de publication n’est ajouté/modifié.

Editor-Colab conserve le parcours public et la correction `virtualenv`. Sa phase d’installation prépare dépendances, navigateur et poids Kokoro ; la phase de traitement utilise le cache hors ligne. Le formulaire REF garde `main` par défaut et permet la branche de revue. Les anciennes sorties d’exécution des cellules modifiées ont été effacées pour ne pas les présenter comme une validation du nouveau code.

**Non exécuté :** test sur Android physique et session Google Colab distante. Les essais tactiles Chromium et le rendu CPU local ne sont pas présentés comme ces validations.

## Limites et éléments reportés à 0.6

- Pas de synthèse Kokoro Python dans le navigateur ni d’hébergement automatique du WAV dans Pages. Le téléphone prévisualise les visuels et captions ; la voix complète s’écoute dans le MP4 Colab.
- Aperçu voxel allégé ; pas de garantie de performances sur chaque téléphone. Préchargement hors ligne du lecteur après une première visite réseau réussie ; il reste un bundle statique d’environ 2,4 Mo.
- Les conseils de rythme ne comprennent ni prédiction de viralité ni génération de faits. Les références et modes doivent être relus par un humain.
- Les timelines et cartes sont schématiques ; pas de géodésie, chronologie canonique exhaustive ou navigation de foule. Les caméras avancées restent dans l’éditeur Épisode existant. Les connexions graphiques complexes, courbes de trajectoire et compteurs détaillés ont un contrat JSON mais pas tous leurs outils de formulaire avancés.
- Les pistes facultatives ne bouclent pas automatiquement ; la licence est déclarée par l’utilisateur, sans vérification juridique automatique. Limite de transfert de projet 2 Mio ; chaque piste importée est limitée à 512 Kio.
- Une entrée de transition n’est pas une simulation de chevauchement de deux mondes. Le match cut simplifié garde un mouvement de cadrage, sans analyse sémantique des deux plans.
- Les changements de type conservent des brouillons dans l’archive ; leur omission de la copie de rendu est explicite et rapportée. Un projet ancien reste dans l’éditeur historique au lieu de subir une conversion automatique.

Priorités 0.6 : essais Android/Colab réels, aperçu vocal local optionnel, formulaires avancés de cartes/timelines/connexions, meilleure mise en page automatique des textes très longs et profilage CPU/mobile. Rejouer la dernière suite complète lorsque le système d’approbation redevient disponible avant décision de fusion humaine.

## Inventaire des fichiers

- `README.md`
- `docs/HYBRID-GUIDE.html`
- `docs/README.md`
- `docs/assets/editor.css`
- `docs/assets/editor.js`
- `docs/assets/hybrid-preview.js`
- `docs/engine-contract.json`
- `docs/index.html`
- `docs/sw.js`
- `editor/app.mjs`
- `editor/hybrid-model.mjs`
- `editor/hybrid-preview.jsx`
- `editor/hybrid.browser.test.cjs`
- `editor/model.mjs`
- `editor/service-worker.js`
- `remotion/episodes/hybrid_black_garden.json`
- `remotion/episodes/hybrid_oryx.json`
- `remotion/episodes/hybrid_riis.json`
- `remotion/hybrid/COLAB.md`
- `remotion/hybrid/CaptionLayer.tsx`
- `remotion/hybrid/HybridShort.tsx`
- `remotion/hybrid/INSPECTION.md`
- `remotion/hybrid/MOBILE.md`
- `remotion/hybrid/README.md`
- `remotion/hybrid/REPORT.md`
- `remotion/hybrid/Visuals.tsx`
- `remotion/hybrid/adapter.ts`
- `remotion/hybrid/schema.ts`
- `remotion/hybrid/state.ts`
- `remotion/hybrid/templates.ts`
- `remotion/hybrid/validation-evidence.json`
- `remotion/package-lock.json`
- `remotion/package.json`
- `remotion/scripts/build-editor.mjs`
- `remotion/scripts/cache-kokoro.py`
- `remotion/scripts/episode.mjs`
- `remotion/scripts/narration.py`
- `remotion/scripts/verify-hybrid-render.mjs`
- `remotion/src/Root.tsx`
- `remotion/src/voxel/cinematic/CinematicEpisode.tsx`
- `remotion/src/voxel/episode/VoxelEpisode.tsx`
- `remotion/src/voxel/episode/schema.ts`
- `remotion/tests/hybrid.test.mjs`
- `remotion/tests/test_hybrid_narration.py`
- `remotion/tts/Editor-Colab.ipynb`
