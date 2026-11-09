# Blender Bridge 0.8.1

Pont additif vers des images Blender : les projets 0.7, l’éditeur mobile, Kokoro, Remotion et les sous-titres restent inchangés. Le bridge évalue une frame et exporte des primitives originales, pas des modèles propriétaires.

L’inspection et les checkpoints sont dans [le journal de reprise](../../docs/BLENDER-BRIDGE-PROGRESS.md). Le premier périmètre vise les rigs 0.7, leurs accessoires, une caméra, des lumières, un sol et des bâtiments procéduraux bornés. Il ne promet pas une copie visuelle identique à Three.js ni un export complet de l’Atlas, des effets, du son et des captions.

Les coordonnées source sont droites, Y vers le haut. Blender utilise Z vers le haut ; la conversion choisie est `(x, y, z) → (x, -z, y)`, rotation propre préservant les distances. Les matrices JSON seront colonne majeure, comme Three.js. Les transformations seront figées à la frame demandée, sans simulation accumulée ni armature Blender animable dans cette première version.
