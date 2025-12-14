#!/bin/bash
# Script d'installation automatique pour Agentic Medical Assistant
# Ce script installe tout ce qui est nécessaire automatiquement

set -e  # Arrêter en cas d'erreur

echo "🚀 Installation Automatique - Assistant Médical"
echo "================================================"
echo ""

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
info() {
    echo -e "${GREEN}✅ $1${NC}"
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérifier si on est sur macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    error "Ce script est conçu pour macOS. Pour Linux/Windows, utilisez Docker."
    exit 1
fi

# 1. Vérifier et installer Python
echo "📦 Étape 1/6 : Vérification de Python..."
if ! command -v python3 &> /dev/null; then
    warn "Python 3 n'est pas installé."
    echo "   Téléchargez Python depuis : https://www.python.org/downloads/"
    echo "   Après installation, relancez ce script."
    exit 1
else
    PYTHON_VERSION=$(python3 --version)
    info "Python trouvé : $PYTHON_VERSION"
fi

# 2. Vérifier et installer Homebrew (pour Ollama)
echo ""
echo "📦 Étape 2/6 : Vérification de Homebrew..."
if ! command -v brew &> /dev/null; then
    warn "Homebrew n'est pas installé. Installation..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    info "Homebrew installé"
else
    info "Homebrew trouvé"
fi

# 3. Vérifier et installer Ollama
echo ""
echo "📦 Étape 3/6 : Vérification d'Ollama..."
if ! command -v ollama &> /dev/null; then
    warn "Ollama n'est pas installé. Installation..."
    brew install ollama
    info "Ollama installé"
else
    info "Ollama trouvé"
fi

# 4. Créer l'environnement virtuel Python
echo ""
echo "📦 Étape 4/6 : Création de l'environnement virtuel..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    info "Environnement virtuel créé"
else
    info "Environnement virtuel existe déjà"
fi

# 5. Installer les dépendances Python
echo ""
echo "📦 Étape 5/6 : Installation des dépendances Python..."
echo "   (Cela peut prendre 5-10 minutes la première fois)"
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt
info "Dépendances installées"

# 6. Télécharger le modèle Ollama
echo ""
echo "📦 Étape 6/6 : Téléchargement du modèle d'IA..."
echo "   (Cela peut prendre plusieurs minutes selon votre connexion)"

# Démarrer Ollama en arrière-plan si ce n'est pas déjà fait
if ! curl -s http://localhost:11434 > /dev/null 2>&1; then
    warn "Démarrage d'Ollama..."
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!
    sleep 3
    info "Ollama démarré"
fi

# Vérifier si le modèle existe
if ollama list | grep -q "llama3.1:8b"; then
    info "Modèle llama3.1:8b déjà installé"
else
    warn "Téléchargement du modèle llama3.1:8b..."
    ollama pull llama3.1:8b
    info "Modèle téléchargé"
fi

echo ""
echo "================================================"
info "🎉 Installation terminée avec succès !"
echo ""
echo "Pour démarrer l'application, utilisez :"
echo "  ./start.sh"
echo ""
echo "Ou double-cliquez sur 'start.sh' dans le Finder"
echo "================================================"

