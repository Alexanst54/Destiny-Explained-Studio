# Import Claude depuis Android (sans GitHub Actions)

Le fichier `claude-project.zip` est une archive, pas un projet exploitable directement par Remotion.

1. Télécharge `claude-project.zip` depuis le dépôt (ou réutilise le ZIP original).
2. Ouvre-le dans l'application **Fichiers** de ton téléphone, puis choisis **Extraire**.
3. Dans le dossier extrait `destiny-explained-studio`, tu trouveras `package.json`, `src/`, `public/` et plusieurs fichiers de configuration.
4. Depuis le navigateur mobile, ouvre le dépôt GitHub, puis le dossier `remotion`.
5. Utilise **Add file → Upload files** pour envoyer **le contenu du dossier extrait** dans `remotion/`, et non l'archive ZIP. Selon le navigateur Android, l'envoi de dossiers entiers peut être indisponible ; il faudra alors passer par l'éditeur de fichiers GitHub, un outil Git mobile ou un navigateur qui prend en charge l'envoi de dossiers.
6. Vérifie que le dépôt contient `remotion/package.json` et `remotion/src/index.ts`.

Le site mobile actuel reste dans `index.html` à la racine et ne doit pas être remplacé.

Le rendu MP4 sera configuré séparément une fois les sources présentes.