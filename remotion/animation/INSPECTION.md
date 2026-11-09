# Inspection 0.7

Base réelle : main `da07baab103b5b1b9534bdd03bb22528ec1f1e62`, fusion PR #12. Le moteur conserve les schémas d’épisode, l’Atlas, les catalogues, `characterState`, `directWorld`, `LivingWorldLayer`, la composition cinématique et le lecteur hybride partagé. La branche est `feat/voxel-animation-0.7`.

Le modèle historique déplace des blocs sans genoux/coudes indépendants. Le nouveau rig sera facultatif sur le cast et rendu par un composant distinct. Les interactions et caméras appartiendront au monde Living Worlds, avec héritage scène/plan explicite et validation après résolution. Aucun changement des animations ou des modèles historiques par défaut.

La démo existante comporte cinq plans, mais seulement trois types (texte, voxel, carte). Pour montrer les cinq types demandés sans altérer les 35 secondes ni les 64 mots, la conclusion sera subdivisée en timeline, graphique et texte aux silences déjà présents dans les timestamps. Le WAV et les mots resteront strictement identiques ; aucune datation ou motivation nouvelle.

Budgets : population effective 32 maximum, interactions ciblées et séparation spatiale déterministe, sans simulation accumulée. Profils draft/balanced/final ; pas de recommandation chiffrée avant mesure. Mémoire mesurée par échantillonnage du processus de rendu et de ses descendants, avec catégories Node/Chromium/autres, en distinguant somme RSS et PSS quand observable.
