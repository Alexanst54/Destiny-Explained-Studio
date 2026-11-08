# Viral Editing & Visual Polish 0.6

Cette extension facultative réutilise HybridShort, Living Worlds, l’Atlas et Kokoro. Les projets 0.1–0.5 gardent leurs calculs et valeurs par défaut. Aucun service, dépendance, asset Destiny ou workflow Actions ajouté.

[Guide mobile](MOBILE.md) · [Validation](REPORT.md) · [Comparaison reproductible](COMPARISON.md) · [Inspection](INSPECTION.md)

## Contrat et composants

Les schémas Zod de `schema.ts` sont composés avec le validateur existant. Les erreurs bloquent la copie pour rendu ; l’export d’archive conserve les champs inconnus.

| Champ facultatif | Usage |
| --- | --- |
| `shorts.polish` | `version: 1`, `quality`, `previewQuality`, `previewEffectScale`, budgets, ombres de contact, profil éditorial |
| `shorts.captions` | Quatre nouveaux styles, `fontSize`, `color`, `accent`, `leftPx`, `rightPx`, `bottomPx`, `emphasis` |
| `scene.polish.camera` | Préréglage, période locale en frames, intensité, courbe, cible écran/monde et seed |
| `scene.polish.environment` | Ambiance artistique, intensité, profondeur, parallaxe, variation lumineuse et seed ; voxel uniquement |
| `livingWorld.cast[].director` ou `groups[].member.director` | Émotion, geste, cible, variation, seed, fenêtre expressive, arrêt et rotation, exode |

L’activation depuis les formulaires marque le projet `schemaVersion: "0.6.0"`. Le moteur n’exige aucune conversion d’un projet historique. Changer un plan voxel en graphique archive son atmosphère dans `editorEnvironmentDraft` et la restaure au retour ; la copie pour rendu annonce l’exclusion de ce brouillon inactif. La caméra artistique s’ajoute à la caméra voxel résolue par les règles scène/plan existantes. Les champs 0.6 restent au niveau scène ; les overrides d’animation Living Worlds par plan restent prioritaires pour l’animation de base. Le director ajoute ensuite sa pose expressive et son déplacement adouci. Les fenêtres sont relatives au plan hybride ou au début de vie de l’acteur et sont validées contre leur durée.

`PolishedCaptions` partage le lecteur et le MP4. Documentary Clean, Kinetic Words, Cinematic Reveal et High Impact utilisent les mots et timestamps sans réécrire le texte. Les segments restent présents entre deux mots ; aucun mot n’est annoncé actif dans un silence. Sans timestamps complets, le repli estimé reste explicitement affiché. L’emphase est une liste de mots choisie par l’auteur, comparés sans casse ni ponctuation. Les marges sont bornées ; vérifier aussi les surimpressions TikTok, susceptibles d’évoluer.

`camera.ts` calcule push/pull, panoramiques, travelling, orbite, focus simulé, shake, révélation et rapprochement carte→voxel à partir de la frame. Le focus est un cadrage, sans flou optique. La transition carte→voxel rapproche les deux plans ; elle ne crée pas une continuité géographique 3D. Les préréglages écran s’appliquent aux cinq types ; les vrais mouvements 3D concernent le voxel. L’aperçu respecte la préférence de réduction des mouvements pour les nouveaux mouvements et conserve les animations de personnage nécessaires à la lecture de la scène.

`characters.ts` ajoute démarrage/arrêt, orientation interpolée par l’angle court, cible de tête fixe, quatre réactions et cinq gestes. L’exode décale les départs par seed et prolonge les chemins au plus de 6 m, dans les limites du monde. Ce n’est pas une navigation : aucun évitement de collision. Les trajectoires adoucies s’appliquent pendant la vie de l’acteur ; la fenêtre `startFrame/durationFrames` contrôle l’expression, pour éviter les sauts de position aux frontières. Les variations de costume/silhouette sont artistiques et signalées, pas des apparences canoniques nouvelles.

`EnvironmentLayer` ajoute ciel en six bandes, brume, lumières, particules et trois couches de bâtiments procéduraux. Ambiances : Riis calme, Tourbillon, poussière, neige, pluie, mystère. Leur choix est explicite, sans prétention de cartographie canonique. Le propriétaire de l’atmosphère 0.6 est la scène React ; aucune météo ne remplace son brouillard à partir d’un état accumulé. Les anciens chemins de météo restent actifs sans polish.

## Budgets CPU

`quality` concerne le rendu ; `previewQuality` et `previewEffectScale` concernent l’aperçu. Particules nouvelles + météo : 0–128, dont au plus 60 % pour la météo ; structures : 0–48 (trois boîtes instanciées chacune). Draft réduit continûment ces comptes, retire les détails de visage supplémentaires et conserve les personnages. Les budgets historiques d’éléments/décors restent indépendants : ce n’est pas un plafond global de tous les triangles du projet. La population résolue reste limitée à **32**, avec erreur explicite, jamais troncature.

Les ombres sont des disques de contact peu coûteux, sans shadow maps. Pas de physique, simulation volumétrique ni post-traitement obligatoire. Le bouton avant/après crée seulement une projection interne sans les effets 0.6 ; le JSON original reste intact.

## Développement

Depuis `remotion/`, Node 22.23.4 :

```sh
npm run typecheck
npm run editor:build
npm run editor:check
npm run test:polish
npm run test:polish:browser
```

Les tests navigateur nécessitent Chromium. Le pipeline voix/rendu reste celui du [guide Colab](../hybrid/COLAB.md). Les fichiers locaux d’audio d’aperçu ne remplacent jamais la narration Kokoro du rendu final.
