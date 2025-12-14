# Créer une Application macOS Cliquable

Pour créer une application macOS que les utilisateurs peuvent simplement double-cliquer (sans Terminal), suivez ces étapes :

## Option 1 : Automator (Le Plus Simple)

1. **Ouvrez Automator** (dans Applications > Utilitaires)
2. **Créez une nouvelle application** :
   - Choisissez "Application"
   - Cliquez sur "Choisir"
3. **Ajoutez une action "Exécuter un script shell"** :
   - Dans la bibliothèque, cherchez "Exécuter un script shell"
   - Glissez-le dans le workflow
   - Sélectionnez "shell: /bin/bash"
4. **Ajoutez ce code** :
   ```bash
   cd "/chemin/vers/agentic-medical-assistant"
   ./start.sh
   ```
   (Remplacez `/chemin/vers/agentic-medical-assistant` par le chemin réel)
5. **Enregistrez** :
   - Cmd+S
   - Nommez-le "Assistant Médical"
   - Choisissez "Format: Application"
   - Enregistrez dans Applications

## Option 2 : Script AppleScript

Créez un fichier `Assistant Medical.app` avec ce contenu :

```applescript
on run
    tell application "Terminal"
        activate
        do script "cd '/chemin/vers/agentic-medical-assistant' && ./start.sh"
    end tell
end run
```

## Option 3 : Platypus (Application Tiers)

1. Téléchargez Platypus : https://sveinbjorn.org/platypus
2. Créez une nouvelle application :
   - Script: `start.sh`
   - Type: Droplet
   - Interface: None
   - Icon: Choisissez une icône
3. Enregistrez comme application

## Recommandation

Pour la simplicité maximale, utilisez **Docker** avec `docker-start.sh` - c'est la solution la plus simple et portable.

