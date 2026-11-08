# Destiny Explained Studio

Mobile-first, unofficial fan-made 2D animation storyboard for educational Destiny lore shorts.

## Prototype v0.1
- Vertical 9:16 scene preview
- Animated SVG Ghost and CSS cartoon Void Hunter
- Play/pause and scrubbable timeline
- Editable English captions and scene title
- Local browser save

## Run
Open `index.html` in a browser, or enable GitHub Pages in **Settings → Pages → Deploy from a branch → main / (root)**.

No dependencies, no build, no PC required.

## Next milestones
1. Scene-specific backgrounds and character poses
2. Audio voiceover import and caption timings
3. Android rendering workflow with Google Colab (GitHub Actions optional)
4. Mobile scene editor

**Not affiliated with Bungie.** All visuals in this prototype are original simplified illustrations.

## Moteur Remotion et export MP4

Le moteur est dans [`remotion/`](remotion/README.md), indépendamment du prototype
HTML. Il exporte l'épisode existant en 1080 × 1920 à 30 fps, avec Node 22.23.4 et
des dépendances verrouillées. Voir les commandes d'installation, de vérification,
d'image fixe et de rendu dans [le guide du moteur](remotion/README.md).

Pour rendre depuis un téléphone Android sans ordinateur personnel et sans
GitHub Actions : [guide Google Colab](remotion/COLAB.md).
Les textes saisis dans le prototype HTML ne sont pas transmis au moteur.
