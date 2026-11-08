# Living Worlds 0.4 — rapport de livraison

Base initiale : `main`, fusion Atlas 0.3 `f6f7b9d`. Le commit Colab `f9b23e2`, ajouté à `main` pendant le développement, a ensuite été intégré par rebase sans conflit et son notebook a été conservé intégralement. Branche : `feat/living-worlds-0.4`. Publication prévue après revue humaine, sans fusion automatique. Les paramètres GitHub Pages et les liens Colab `main` n’ont pas été modifiés.

## Couverture livrée

| Élément | Résultat |
| --- | --- |
| Entrées de personnages / unités / archétypes | 28 |
| Identités et unités prioritaires | 17, dont Spectre générique |
| Archétypes de population supplémentaires | 11, dont Précurseur masqué |
| Civilisations / catégories représentées dans les variantes | 13 ; 12 disposent d’au moins une silhouette affichable |
| Recettes voxel réutilisables | 11 visibles + catégorie `unknown` masquée |
| Animations procédurales | 17 |
| Conditions météo | 12 |
| Variantes, référence comprise | 36 ; 8 variantes supplémentaires au-delà d’une par entrée |
| Références documentaires | 29 consultées : 28 articles secondaires + Livres du Malheur |
| Démonstrations JSON | 3 × 720 images, 24 s, 1080 × 1920 à 30 fps |
| Limites CPU | 32 personnages et 128 particules météo par état résolu |

Identités / unités prioritaires : Cayde-6, Zavala, Ikora, Saint-14, Osiris, Eris, Mara, Uldren/Crow, Éramis, Mithrax, Aurash/Auryx/Oryx, Sathona/Savathûn, Xi Ro/Xivu Arath, Clovis Bray, Voyageur, Raspoutine et Spectres. Les archétypes incluent scientifiques humains et exos, garde éveillé, civil éliksni, Krill, acolyte, soldat cabal, gobelin vex, esclave corrompu et créature infâme. Le Précurseur reste une entrée sans corps inventé.

Les familles visibles sont humanoïde, quatre bras, lourd, Krill, Ruche, Vex, quadrupède, drone, géant, sphère et terminal. Certaines partagent des composants ; ce nombre ne désigne pas 11 maillages externes ni des portraits canoniques exacts.

## Variantes et fidélité

- Aurash → Auryx → Oryx et les deux autres sœurs : transformation, avec changement Krill/Ruche et de recette.
- Uldren → Crow : résurrection explicitement distincte d’un changement de nom ou de costume.
- Osiris : même personne avant/après la mort de Sagira, sans nouvelle résurrection affirmée.
- Éramis : Voleuse de vaisseaux et Maison du Salut ; affiliations historiques séparées.
- Clovis : humain et copie IA, avec passage à un modèle machine.
- Aucune année numérique inventée : les dates précises sont `null` et les périodes sont des étiquettes documentaires.

Les sources sont résolues par ID, ainsi que les liens vers l’Atlas. `characters/source-evidence.json` conserve URL, titre de page, taille et SHA-256 des pages consultées. Cela documente la consultation et non une vérification exhaustive de chaque détail du lore. Les Livres du Malheur sont un récit interne à l’univers, dont les limites restent indiquées.

La structure de contrôle historique compare seulement des ordres partiels explicites, signale les personnages tardifs et les civilisations incompatibles avec Fundament Krill, ainsi que les apparences non officielles. Elle vérifie aussi les acteurs modernes hérités. Elle ne confond pas l’histoire de Riis avec une chronologie humaine supposée. Les contradictions restent des avertissements, permettant la reconstitution et l’histoire alternative. Le cartouche `ALTERNATE HISTORY · NOT CANON` est imposé par le mode narratif dans les deux compositions.

Les modèles sont des illustrations originales très simplifiées. Les vêtements des scientifiques, les corps Krill et les gestes sont des reconstitutions. Le corps adulte de Xivu Arath et celui des Précurseurs sont masqués dans cette version. La météo du Tourbillon est une métaphore visuelle explicitement annoncée par la narration.

## Tests

Environnement de validation : Linux, Node **22.23.4** pour la suite moteur, Python 3.12, Chromium système, Remotion **4.0.541**, Three **0.170.0**, PyTorch **2.6.0+cpu**, Kokoro **0.9.4**. Les dépendances JavaScript et les requirements TTS du projet sont conservés.

- **46 tests Node réussis** : 38 existants et 8 nouveaux tests Living Worlds. Schémas, doublons, sources, variantes, références Atlas, animations, transitions, trajectoires, pauses, orientation, groupes, seeds, limites, météo, cycle jour/nuit, priorités scène/plan et import/export avec champs inconnus.
- **10 tests Python réussis** : narration, assemblage/cache et import de manifest existants.
- `typecheck`, `editor:build`, `editor:check`, `git diff --check` réussis.
- Ancien test navigateur : import/export, champs inconnus, XSS textuel, sauvegarde/rechargement, JSON incomplet, plans, bibliothèque et Atlas, sans erreur de page.
- Nouveau test navigateur : recherche FR/EN, ajout de personnage, animation, transition météo, avertissement d’incompatibilité, sauvegarde/rechargement et copie stricte pour rendu.
- **320, 360, 393 et 1280 px**, émulation tactile, sans débordement horizontal dans les panneaux testés.
- Test hors ligne : première visite sur HTTP local, installation du service worker, désactivation du réseau, rechargement et recherche dans le catalogue avec projet sauvegardé.
- Rendus CPU d’images des **trois nouvelles démos** et de **quatre épisodes existants** : Traveler 0.1, cinématique 0.2, bibliothèque voxel et Atlas 0.3. Pas de régénération complète des anciens MP4.
- Rendu PNG réel hors séquence `120 → 600 → 120` : les deux images 120 ont le même SHA-256. Les poses et particules sont aussi testées en ordre inverse.

Les premières tentatives de tests CLI/navigateur dans le bac à sable étaient perturbées par les restrictions des sous-processus et sockets. Les suites ont ensuite été exécutées avec succès hors de ce bac à sable. Ce n’était pas une régression du moteur. Les tests tactiles sont une émulation Chromium, pas une validation sur un téléphone Android physique ; la boîte de téléchargement du système demande encore un essai appareil.

## Démonstrations

1. **The Whirlwind of Riis** : civils éliksni, marche puis fuite, changement progressif d’éclairage et tempête métaphorique. Aucun Gardien moderne.
2. **Europa: The Legacy of Clovis Bray** : scientifiques humains/exos à l’Âge d’or, déplacements, terminal et blizzard progressif. Cette démo sert au MP4 complet avec Kokoro.
3. **Fundament: Before the Hive** : Aurash, Sathona, Xi Ro et figurants Krill, interactions, océan et atmosphère surnaturelle. Aucun chevalier de la Ruche moderne.

Tous les fichiers JSON sont importables dans l’éditeur et le parcours Colab existant. Les voix, alignements, captures et vidéos générés restent ignorés par Git. Aucune dépendance payante ni modèle 3D téléchargé n’est requis pour les visuels.

## Performances CPU

Démo Europe complète rendue en **606.02 secondes** (10 min 06 s), avec Chromium système et SwiftShader (`swangle`), concurrence **1**. Allocation de la session : quota **2 CPU**, mémoire **8 Gio** ; d’autres tests et rendus d’images ont tourné pendant une partie de la mesure. Ce temps n’est donc pas un benchmark isolé de Google Colab.

Le maximum RSS mesuré pour les enfants suivis atteint **832952 Kio**, environ **813 Mio**. Cette mesure ne somme pas les processus Chromium simultanés/détachés ; elle ne prétend pas mesurer le pic mémoire total du rendu. Les temps user/system de l’enveloppe suivie ne couvrent pas fiablement tous les processus du navigateur.

Contrôle `ffprobe` : **H.264**, **1080 × 1920**, **30/1 fps**, **720 images**, durée vidéo **24,000 s** ; audio **AAC**, **48 kHz**, stéréo, **24,000 s**. Taille : **7962116 octets**.

Kokoro `af_heart`, vitesse 1, modèle verrouillé à la révision du projet : **23,175 s de parole**, puis silence de complément, **46 mots alignés**. Le vérificateur existant confirme **46/46 mots avec audio**, corrélation WAV/AAC **0,999660**, décalage **0 ms**. L’alignement vient des durées phonémiques prédites par Kokoro ; il ne s’agit pas d’une annotation indépendante des frontières de mots.

Le contrôle visuel des images montre personnages, terminal, marche/interactions et changement de visibilité météo. Le rendu PNG hors séquence a reproduit le SHA-256 `4434d67392d6d08770112f1880a63b132a3cdf1fa18eb7fc88259891fc1572df` pour les deux évaluations de l’image 120. Les artefacts complets restent dans `remotion/out/` (ignoré). Pour reproduire les mesures, relancer le parcours documenté ; les performances dépendent du CPU et de Chromium.

## Limites et suite 0.5

Le catalogue est un premier ensemble fonctionnel, pas toute la liste prioritaire demandée. Les autres alliés, Éveillés, Éliksni, dirigeants cabals, Témoin, disciples et unités spécialisées demandent une revue documentaire et des silhouettes dédiées. Les pièces disponibles ne reproduisent pas tous les équipements historiques. Les palettes et vêtements sont des approximations stylisées ; aucun modèle inconnu n’est présenté comme officiel.

Pas de collisions ni d’évitement des obstacles, pas de navigation temps réel, pas de physique accumulée, pas de météo volumétrique. La vitesse d’une trajectoire est constante par placement ; les déplacements sont indépendants du tempo des membres. Les unités d’un groupe peuvent se croiser : la disposition et les chemins doivent être relus visuellement. Les nuages, vent, spores et effets surnaturels sont des abstractions particulaires, sans simulation climatique.

L’éditeur expose les réglages usuels et les animations de plan. Les remplacements complets de cast/groupes par plan, les accessoires/palettes détaillés et les trajectoires de plus de deux points restent éditables dans le JSON avancé. L’aperçu météo mobile est une validation des paramètres ; le rendu animé reste dans Colab. La première mise en cache nécessite une connexion et les liens documentaires externes ne sont pas embarqués.

Pour 0.5 : développer des modèles nommés plus reconnaissables après revue des références, renforcer les périodes attestées et leurs bornes, ajouter davantage de profils de morphologie, enrichir les outils de trajectoire/groupes, améliorer le contrôle du placement devant la caméra et réaliser des essais sur Android physique. Profiler les cas proches du budget de 32 personnages avant de relever les plafonds.
