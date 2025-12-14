# Agentic Medical Assistant

An agentic application for doctors to record, summarize, and analyze patient conversations with AI assistance.

## 🚀 Options d'Installation

Choisissez la méthode qui vous convient le mieux :

### 🥇 Option 1 : Docker (RECOMMANDÉ - Le Plus Simple) 🐳

**Idéal pour** : Utilisateurs qui veulent la solution la plus simple, sans rien installer sur leur système.

**Prérequis** : Docker Desktop (installez-le une fois depuis https://www.docker.com/products/docker-desktop)

**Étapes** :
1. Double-cliquez sur `docker-start.sh` pour démarrer
2. Double-cliquez sur `docker-stop.sh` pour arrêter

**Avantages** :
- ✅ Pas besoin d'installer Python, Ollama, ou quoi que ce soit
- ✅ Tout est isolé et ne modifie pas votre système
- ✅ Fonctionne sur macOS, Linux, et Windows
- ✅ Un seul clic pour démarrer

---

### 🥈 Option 2 : Installation Automatique (macOS) 🍎

**Idéal pour** : Utilisateurs macOS qui préfèrent une installation native sans Docker.

**Étapes** :
1. Double-cliquez sur `install.sh` - Installe tout automatiquement (Python, Ollama, dépendances, modèle IA)
2. Double-cliquez sur `start.sh` - Démarre l'application

**Avantages** :
- ✅ Installation automatique de tout ce qui est nécessaire
- ✅ Démarrage automatique d'Ollama
- ✅ Pas besoin de Terminal (juste double-cliquer)

---

### 🥉 Option 3 : Installation Manuelle via Terminal 💻

**Idéal pour** : Utilisateurs qui préfèrent contrôler chaque étape ou qui ont déjà Python/Ollama installés.

**Étapes** : Voir la section [Installation Manuelle](#installation-manuelle-via-terminal) ci-dessous.

**Avantages** :
- ✅ Contrôle total sur chaque étape
- ✅ Compréhension de ce qui se passe
- ✅ Peut personnaliser l'installation

## 📋 Guides Détaillés par Option

### 🐳 Option 1 : Docker (Recommandé)

#### Installation

1. **Installez Docker Desktop** : https://www.docker.com/products/docker-desktop
   - Téléchargez et installez Docker Desktop
   - Démarrez Docker Desktop (l'icône Docker doit être visible dans la barre de menu)

2. **Démarrez l'application** :
   - **Méthode A** : Double-cliquez sur `docker-start.sh` dans le Finder
   - **Méthode B** : Dans Terminal :
     ```bash
     cd /chemin/vers/agentic-medical-assistant
     ./docker-start.sh
     ```

3. **L'application s'ouvrira automatiquement** sur http://localhost:8501

#### Arrêter l'application

- **Méthode A** : Double-cliquez sur `docker-stop.sh` dans le Finder
- **Méthode B** : Dans Terminal :
  ```bash
  ./docker-stop.sh
  ```

#### Avantages Docker

- ✅ Pas besoin d'installer Python, Ollama, ou quoi que ce soit
- ✅ Tout est isolé et ne modifie pas votre système
- ✅ Fonctionne sur macOS, Linux, et Windows
- ✅ Un seul clic pour démarrer
- ✅ Facile à mettre à jour (juste relancer docker-start.sh)

---

### 🍎 Option 2 : Installation Automatique (macOS)

#### Installation

1. **Installez l'application** :
   - **Méthode A** : Double-cliquez sur `install.sh` dans le Finder
   - **Méthode B** : Dans Terminal :
     ```bash
     cd /chemin/vers/agentic-medical-assistant
     ./install.sh
     ```
   
   Le script installe automatiquement :
   - Python (si nécessaire)
   - Homebrew (si nécessaire)
   - Ollama
   - Toutes les dépendances Python
   - Le modèle d'IA

2. **Démarrez l'application** :
   - **Méthode A** : Double-cliquez sur `start.sh` dans le Finder
   - **Méthode B** : Dans Terminal :
     ```bash
     ./start.sh
     ```
   
   Le script démarre automatiquement :
   - Ollama (en arrière-plan)
   - L'application Streamlit

#### Arrêter l'application

- **Dans l'interface** : Utilisez le bouton "🛑 Arrêter le Serveur" dans la sidebar
- **Dans Terminal** : Appuyez sur `Ctrl+C` (ou `Cmd+C`)

#### Avantages Installation Automatique

- ✅ Installation automatique de tout ce qui est nécessaire
- ✅ Démarrage automatique d'Ollama
- ✅ Pas besoin de Terminal (juste double-cliquer)
- ✅ Performance native (pas de conteneur Docker)

---

### 💻 Option 3 : Installation Manuelle via Terminal

**Idéal pour** : Utilisateurs qui préfèrent contrôler chaque étape, qui ont déjà Python/Ollama installés, ou qui veulent comprendre ce qui se passe.

#### Étape 1 : Installer Python

1. **Ouvrez votre navigateur** et allez sur : https://www.python.org/downloads/
2. **Téléchargez Python** (cliquez sur le gros bouton jaune "Download Python")
3. **Ouvrez le fichier téléchargé** (il devrait être dans votre dossier Téléchargements)
4. **Suivez les instructions d'installation** :
   - Cliquez sur "Continuer" plusieurs fois
   - Acceptez les conditions
   - **IMPORTANT** : Cochez la case "Add Python to PATH" si elle apparaît
   - Cliquez sur "Installer"
   - Entrez votre mot de passe si demandé
5. **Vérifiez l'installation** :
   - Ouvrez l'application "Terminal" (cherchez "Terminal" dans Spotlight avec Cmd+Espace)
   - Tapez : `python3 --version`
   - Vous devriez voir quelque chose comme "Python 3.10.x" ou supérieur

#### Étape 2 : Installer Ollama (pour l'intelligence artificielle)

1. **Ouvrez votre navigateur** et allez sur : https://ollama.ai
2. **Téléchargez Ollama** pour macOS (bouton "Download")
3. **Ouvrez le fichier téléchargé** et suivez les instructions d'installation
4. **Démarrez Ollama** :
   - Ouvrez l'application "Terminal"
   - Tapez : `ollama serve`
   - **Laissez cette fenêtre ouverte** (c'est normal, ne la fermez pas)
   - Si vous voyez "Ollama is running", c'est bon !

5. **Dans une NOUVELLE fenêtre Terminal** (ouvrez-en une autre), installez le modèle d'IA :
   - Tapez : `ollama pull llama3.1:8b`
   - Attendez que le téléchargement se termine (cela peut prendre plusieurs minutes)

#### Étape 3 : Télécharger l'Application

1. **Téléchargez l'application** depuis GitHub :
   - Allez sur : https://github.com/youcefjd/agentic-medical-assistant
   - Cliquez sur le bouton vert "Code"
   - Cliquez sur "Download ZIP"
   - Décompressez le fichier ZIP (double-cliquez dessus)
   - Déplacez le dossier décompressé où vous voulez (par exemple sur le Bureau)

#### Étape 4 : Installer l'Application

1. **Ouvrez l'application Terminal**
2. **Naviguez vers le dossier de l'application** :
   - Tapez : `cd ` (avec un espace à la fin)
   - Faites glisser le dossier de l'application dans la fenêtre Terminal
   - Appuyez sur Entrée

3. **Créez l'environnement virtuel** (cela installe tout ce dont l'application a besoin) :
   ```bash
   python3 -m venv venv
   ```
   Attendez quelques secondes...

4. **Activez l'environnement virtuel** :
   ```bash
   source venv/bin/activate
   ```
   Vous devriez voir `(venv)` apparaître au début de votre ligne de commande

5. **Installez toutes les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```
   ⏳ **Cela peut prendre 5-10 minutes** la première fois. C'est normal, attendez que ce soit terminé.

#### Étape 5 : Démarrer l'Application

**IMPORTANT** : Vous devez avoir **2 fenêtres Terminal ouvertes** :

#### Terminal 1 - Ollama (doit être en cours d'exécution)
```bash
ollama serve
```

#### Terminal 2 - L'Application

**Option A - Utiliser le script de démarrage (RECOMMANDÉ)** :
```bash
./start.sh
```

**Option B - Démarrer manuellement** :
```bash
source venv/bin/activate
python main.py
```

#### Étape 6 : Utiliser l'Application

1. **L'application s'ouvrira automatiquement** dans votre navigateur
2. **L'URL sera** : http://localhost:8501
3. Si elle ne s'ouvre pas automatiquement, copiez cette URL dans votre navigateur

</details>

---

## ⚠️ Problèmes Courants

**"command not found: docker"**
- Docker Desktop n'est pas installé
- Installez-le depuis : https://www.docker.com/products/docker-desktop

**"command not found: python3"**
- Python n'est pas installé ou n'est pas dans le PATH
- Réinstallez Python et assurez-vous de cocher "Add Python to PATH"

**"ModuleNotFoundError"**
- Vous n'utilisez pas l'environnement virtuel
- Utilisez toujours : `./start.sh` ou `./docker-start.sh`

**"Ollama connection error"**
- Ollama n'est pas en cours d'exécution
- Avec Docker : Relancez `./docker-start.sh`
- Sans Docker : Ouvrez Terminal et tapez : `ollama serve`

**"Port 8501 already in use"**
- L'application est déjà en cours d'exécution
- Arrêtez-la d'abord avec `./docker-stop.sh` ou `Ctrl+C`

---

## 🛑 Arrêter l'Application

### Avec Docker
- **Double-cliquez sur `docker-stop.sh`** ou :
  ```bash
  ./docker-stop.sh
  ```

### Sans Docker
1. **Dans l'interface** : Utilisez le bouton "🛑 Arrêter le Serveur" dans la sidebar
2. **Dans Terminal** : Appuyez sur `Ctrl+C` (ou `Cmd+C` sur Mac)
3. **Fermez Ollama** : Dans la fenêtre Terminal où Ollama tourne, appuyez sur `Ctrl+C`

---

## 📋 Résumé des Fichiers et Scripts

### Scripts Docker 🐳
- **`docker-start.sh`** - Démarre tout avec Docker (1 clic)
- **`docker-stop.sh`** - Arrête l'application Docker
- **`docker-compose.yml`** - Configuration Docker
- **`Dockerfile`** - Image Docker de l'application

### Scripts Installation Automatique 🍎
- **`install.sh`** - Installation automatique complète (macOS)
- **`start.sh`** - Démarre l'application (démarre Ollama automatiquement)

### Fichiers de Configuration
- **`requirements.txt`** - Dépendances Python
- **`config.py`** - Configuration de l'application
- **`main.py`** - Point d'entrée de l'application

### Documentation
- **`README.md`** - Ce fichier (instructions complètes)
- **`CREATE_APP.md`** - Guide pour créer une app macOS cliquable

---

## Features

- 🎤 **Conversation Recording**: Record and transcribe doctor-patient conversations
- 📝 **AI Summarization**: Automatically summarize conversations and extract key information
- 🗂️ **Patient Management**: Organize patient records and visit history
- 📊 **Pattern Analysis**: Identify patterns in patient history, medication changes, and pathology evolution
- 🏥 **Test Integration**: Upload and parse MRIs, CT scans, blood tests, and other medical tests
- 📄 **PDF Generation**: Generate professional PDF summaries of visits
- 🔍 **Semantic Search**: Search conversations and notes using natural language

## Architecture

- **LLM**: Ollama with Llama 3.1 8B (local)
- **Transcription**: Faster-Whisper (local)
- **Database**: SQLite (structured data) + ChromaDB (semantic search)
- **UI**: Streamlit

## Usage

1. **Create a Patient**: Register a new patient in the system
2. **Record a Visit**: Upload audio of a conversation, get automatic transcription and summarization
3. **View History**: Browse patient visit history and generate PDF summaries
4. **Upload Tests**: Upload DICOM files (MRIs, scans) or lab results
5. **Pattern Analysis**: Analyze patient evolution over time
6. **Semantic Search**: Search across all conversations and notes using natural language

## Configuration

Edit `config.py` to customize:
- Ollama model and URL
- Whisper model size
- Database paths
- Output directories

## Data Storage

All data is stored locally:
- `data/patients.db` - SQLite database
- `data/chromadb/` - Vector database for semantic search
- `data/patients/` - Patient files and PDFs
- `data/conversations/` - Audio recordings
- `data/tests/` - Medical test files

## Security Note

This is a local-first application. For production use with real patient data:
- Implement encryption at rest
- Add access controls
- Ensure HIPAA compliance
- Use secure authentication

## License

MIT
