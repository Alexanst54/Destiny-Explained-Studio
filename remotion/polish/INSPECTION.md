# Inspection avant changements 0.6

Base vérifiée : main `1a402fb764f71ee86870cf0e74c7c5cf856805a7`, fusion PR #11. Branche `feat/viral-editing-0.6`.

Composants réutilisés : `hybrid/CaptionLayer.tsx` et `captionSegment` pour les mots/segments ; `HybridShort.tsx` et le lecteur partagé pour toutes les surfaces ; `cinematic/motion.ts` et `FilmCameraRig` pour la caméra voxel ; `characters/animations/state.ts`, modèles et `LivingWorldLayer` pour les acteurs ; météo instanciée et Atlas pour les décors ; `editor/app.mjs` et son historique/localStorage pour l’UX ; pipeline Kokoro/Colab existant.

Contraintes : ne pas changer les calculs ou les valeurs par défaut des projets 0.1–0.5. Les améliorations sont des champs facultatifs 0.6, activés explicitement. Conserver la limite résolue de 32 acteurs, sans suppression de cast. Limiter les nouveaux détails/particules et dégrader uniquement les effets en aperçu. Aucune physique accumulée, position astronomique ou motivation canonique inventée.

Ordre suivi : captions → caméra → personnages → environnement → audio local → recommandations → UX → nouvelle démo et validations. Le fichier Riis 0.5 est immuable pour la comparaison. Les références de temps, tailles, mémoire et réussite des tests proviendront uniquement d’exécutions enregistrées. Android physique et Colab distant ne seront pas assimilés aux tests Chromium/CPU locaux.
