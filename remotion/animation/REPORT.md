# Rapport 0.7 — Voxel Animation Studio

Base vérifiée : main après PR #12, `da07baab103b5b1b9534bdd03bb22528ec1f1e62`. Branche `feat/voxel-animation-0.7`. [Inspection avant changements](INSPECTION.md). Aucune fusion automatique et aucun changement de publication Pages.

## Fonctions livrées

- Rig hiérarchique facultatif à deux/quatre bras, proportions, bassin/torse/tête et articulations indépendantes. Modèles historiques conservés sans activation.
- Six archétypes éliksni fonctionnels : Dreg, Vandal, Captain, Servitor, civil et ancien. Cinq nouvelles entrées de registre ; total réel **33 personnages, 33 références**. Quatre références nouvelles consultées ; le civil et la référence générale Fallen préexistaient. Les costumes, proportions et le rôle d’ancien sont artistiques.
- 16 animations, clips interpolés, phases/seed et adaptation non humanoïde du Servitor.
- Neuf relations ciblées avec références/périodes validées après héritage. Suivi en rangées et séparation spatiale bornée ; pas de moteur physique.
- Blocking mobile avec sélection, positions/orientation, début/fin des actions, cibles, trajectoires, frame précise et préréglages. Participants et cibles caméra sélectionnables au toucher ; annuler/rétablir, archive JSON, brouillons et stockage local conservés.
- Huit cadrages de personnages et réserve pour les captions. Profils draft/balanced/final, géométries partagées, matériaux et hiérarchies mémorisés, LOD selon distance.
- Groupes vocaux contigus facultatifs, sans altérer le texte, et prise en charge de plans courts dans la vérification audio.

## Riis et cohérence

La démo 0.7 garde le script, les sources, 35 secondes et les 64 mots de 0.5. Elle utilise six habitants civils/ancien dans chaque scène voxel, pas les archétypes militaires modernes. L’Atlas et les démos 0.5/0.6 sont inchangés.

La conclusion a été subdivisée à 30,2 s et 33,1 s, dans des silences existants, pour obtenir sept plans et les cinq types hybrides. Un premier essai Kokoro par nouveau plan produisait une phrase de 3,3 s pour un budget de 3,2 s : il a été refusé. Le groupe vocal explicite conserve la phrase complète. Une nouvelle synthèse **réelle** CPU/hors ligne de 0.7 a ensuite produit un WAV et des timestamps **identiques** à ceux de référence (comparaison binaire et JSON, 64 mots), sans accélération ni coupe. Le manifeste contient cinq unités de synthèse pour sept plans : le dernier groupe couvre les trois plans de conclusion.

Les nouvelles apparences portent les avertissements de reconstitution. Aucune motivation du Voyageur, date précise ou apparence inconnue n’est inventée. Les modèles non humanoïdes connus ne peuvent pas être remplacés arbitrairement par le rig humanoïde.

## Tests exécutés

- Baseline : 65 tests Node, 11 Python réussis avant modification.
- Suite finale : 79 tests Node et 14 Python réussis ; TypeScript et contrôle du site statique.
- Nouveaux tests : hiérarchie/kinématique, quatre bras, six archétypes, 16 animations, transitions et overrides, neuf relations, références/périodes, suivi, groupes/seeds, séparation, huit cadrages, projection des têtes/mains/pieds hors zone de captions sur la fixture testée, profils/LOD, préservation de version/JSON/brouillons et groupes vocaux.
- Six suites Chromium : éditeur, Living Worlds, hors ligne, hybride, polish et animation. Largeurs 320, 360, 393, 1280 px ; pas de débordement horizontal observé. Les tests tactiles utilisent Chromium Linux, pas Android physique. Le clic de téléchargement est neutralisé et le vrai Blob contrôlé ; le gestionnaire de fichiers Android n’est pas validé.
- Six références visuelles : quatre images des épisodes historiques et deux images voxel de 0.6 comparées aux SHA-256 archivés. Les nouveaux rigs n’altèrent pas leurs chemins par défaut.
- Huit triplets de comparaison 0.5/0.6/0.7 ; frames hors séquence, aperçu voxel aligné/final et réduction des mouvements vérifiés. Les médias restent dans `out/animation-comparison/`, hors Git. Les empreintes portent sur cette pile Linux/Chromium ; l’identité pixel par pixel entre navigateurs, versions et polices n’est pas garantie.

Les premiers contrôles ont détecté des cas corrigés pendant l’intégration : conservation de `schemaVersion: 0.7.0` lors d’une sélection Atlas, activation d’un rig conforme au nombre de bras du registre (y compris Dreg ajouté par le catalogue historique), conservation des saisies numériques lors d’ajouts/retraits de listes et changements de cible, message d’erreur d’action sans période libre, places distinctes pour les suiveurs, argument d’atmosphère rejeté par TypeScript et comparaison des transitions par positions d’articulations plutôt que par présence de clés de rotation nulles. Les chiffres ci-dessus décrivent les suites finales, pas ces premiers essais.

## Mesures CPU et mémoire

Rendu complet 0.7 réussi : **536,22 s**, **1 050 frames**, **12 496 448 octets**, vidéo **1080×1920 à 30 fps, H.264, 35,000 s**, audio **AAC 48 kHz stéréo, 35,008 s**. Configuration : Linux, Xeon Platinum 8370C, 3 CPU logiques exposés, environ 9,7 Gio RAM, Node 22.23.4, Chromium 156.0.8078.79, Remotion 4.0.541, SwiftShader swangle, concurrence 1. Six personnages actifs dans chaque scène voxel, profil final, budgets d’atmosphère 0.6 inchangés.

Le pic **simultané** observé est **1 870 301 Kio PSS (1,78 Gio)** et **2 222 420 Kio RSS additionnés (2,12 Gio)**. 1 067 échantillons ; PSS disponible pour les processus suivis à chaque lecture. Le lecteur de /proc ajoute un coût au test ; le délai de 250 ms est une cible entre lectures, pas une fréquence garantie. La préparation Kokoro a tourné séparément et sa mémoire n’est pas incluse dans ce relevé du rendu.

| Catégorie au pic total PSS | RSS Kio | PSS Kio |
| --- | ---: | ---: |
| Node (2 processus) | 754 956 | 706 911 |
| Chromium (7 processus) | 908 440 | 605 941 |
| Autres enfants (2 processus) | 559 024 | 557 449 |

Les pics propres à chaque catégorie sont aussi conservés dans les preuves ; ils ne coïncident pas forcément avec ce tableau.

**Comparaison fraîche**, mêmes 12 frames 210–221, même moniteur et mêmes paramètres CPU :

| Version | Temps commande | PSS totale maximale observée |
| --- | ---: | ---: |
| 0.5 | 16.03 s | 1416.9 Mio |
| 0.6 | 15.77 s | 1280.7 Mio |
| 0.7 | 16.10 s | 1298.9 Mio |

Ces temps sont dominés par lancement/bundling/encodage ; les petites différences ne prouvent pas un gain ou une perte de débit du renderer. Un seul essai par cas, caches et machine partagés.

Les films 0.5 et 0.6 conservés localement proviennent des rendus complets archivés lors de 0.6 : **292,40 s / 7 005 278 octets** et **371,91 s / 11 926 108 octets**. Les deux rendus complets 0.7 ont duré **393,13 s puis 536,22 s** et produit un MP4 **identique octet par octet**, SHA-256 `4405db1cfcb0cad7cbbf9786da371b7a3d271e6a885d0ee9fc291392c0742f8a`. La seconde exécution correspond au code final du regard. La variation de temps de 36,4 % entre ces deux essais interdit un classement fiable. La dernière mesure dépasse de 44,2 % la mesure historique 0.6, **sans pouvoir attribuer cet écart aux rigs** : le moniteur mémoire, les caches et le moment de mesure diffèrent. Les anciens chiffres RSS enfant ne sont pas une mesure totale comparable à la PSS 0.7. Les films 0.5/0.6 n’ont pas été recalculés intégralement pendant cette livraison ; leurs références et les nouveaux échantillons ont été vérifiés.

**Profils**, 12 frames pour chaque population :

| Profil | 4 personnages | 8 personnages | 16 personnages | Point de départ conseillé |
| --- | ---: | ---: | ---: | ---: |
| draft | 15.11 s | 15.34 s | 16.03 s | 8 |
| balanced | 15.08 s | 15.15 s | 15.29 s | 8 |
| final | 14.07 s | 14.09 s | 14.73 s | 6 |

Les neuf essais ont fini, avec 12 frames réellement encodées chacun et une PSS observée de 1 242,8 à 1 302,4 Mio. Les propositions 8/8/6 sont des points de départ prudents, **pas des capacités maximales démontrées** : seuls six acteurs en final ont été vérifiés sur le film complet. Le cadrage large et les LOD de distance limitent les détails dans les fixtures à 16 ; ces résultats ne prouvent pas que 16 personnages proches et détaillés seront aussi légers. Aucun essai à 32 ni classement statistique des profils. Final n’est pas intrinsèquement plus rapide malgré ces échantillons courts ; le lancement et les caches peuvent inverser les écarts. La limite logicielle de 32 ne vaut pas recommandation de production.

**Audio** : 64/64 mots avec signal ; décalage mesuré de **0 ms** dans chacune des sept fenêtres, corrélation minimale **0,9972**. Les fenêtres des plans courts restent dans leur durée. Le padding AAC de 8 ms en fin est attendu. Le contrôle ne prétend pas mesurer une annotation humaine des phonèmes.

Une première commande du banc a été refusée avant rendu parce que son chemin MP4 imbriqué ne respectait pas le contrat historique `out/nom.mp4`. Les chemins du banc ont été corrigés ; cet essai échoué n’est pas compté parmi les résultats réussis. Les preuves conservent aussi ce diagnostic.


Le moniteur distingue Node, Chromium et autres descendants. Somme RSS et PSS totale observable sont échantillonnées avec un délai cible de 250 ms entre lectures. RSS compte certaines pages partagées plusieurs fois ; PSS les répartit. Ce sont des pics observés, pas une garantie de maximum absolu. Les processus devenus inobservables et les pointes brèves peuvent échapper à l’échantillonnage ; le moniteur lui-même est exclu. Les pics de catégories ne doivent pas être additionnés comme s’ils étaient simultanés.

## Limites et suite

- Android physique et Google Colab distant : **non exécutés**. Le pipeline complet est testé sur CPU Linux local avec les scripts utilisés dans Colab.
- Séparation de centres en deux passes, pas de collision de membres/décors ni garantie pour des foules denses ou des proportions extrêmes. Les relations ont une enveloppe et reviennent à la trajectoire de base à leur fin. Le suivi utilise la trajectoire analytique du guide, pas un graphe récursif d’autres relations.
- Le cadrage vise les personnages sélectionnés ; les autres peuvent rester hors champ. Les bornes géométriques sont conservatrices et demandent une relecture pour des gestes/proportions extrêmes. Champ/contrechamp simple, sans règle des 180° automatique.
- Les modèles restent des abstractions voxel. Les nouvelles entrées militaires ne constituent pas des fiches historiques exhaustives ; dates de première apparition inconnues.
- Le preset de regard vise une position fixe ; pas de capture de mouvement ni de synchronisation labiale. Les animations du Servitor sont des équivalents de machine, sans membres.
- Les LOD réduisent les détails, jamais le cast. La limite résolue de 32 reste bloquante. Les budgets de décor/particules 0.6 restent distincts de ceux des rigs.
- Les groupes vocaux peuvent demander une correction après réorganisation des plans. Si les mots débordent, le pipeline s’arrête ; aucun alignement factice ou raccourci automatique.
- Les contrôles audio comparent la forme d’onde Kokoro à l’AAC ; ils ne sont pas une annotation humaine indépendante des frontières de mots.

Pour 0.8 : essais Android/Colab réels, ciblage tactile dans le viewport, composition plus fine des voies d’interaction, géométrie éliksni plus expressive, évitement de segments de décor simples et profils CPU mesurés sur davantage de machines.

[Architecture et schémas](README.md) · [Guide mobile/Colab](MOBILE.md) · [Comparaison reproductible](COMPARISON.md) · [Preuves JSON](validation-evidence.json) · [Inventaire](FILES.md)
