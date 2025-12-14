#!/bin/bash
# Script pour démarrer l'application Agentic Medical Assistant
# Ce script démarre automatiquement tout ce qui est nécessaire

cd "$(dirname "$0")"

echo "🚀 Démarrage de l'Assistant Médical..."
echo "======================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info() {
    echo -e "${GREEN}✅ $1${NC}"
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérifier si l'installation a été faite
if [ ! -d "venv" ]; then
    error "L'environnement virtuel n'existe pas."
    echo ""
    echo "Veuillez d'abord exécuter le script d'installation :"
    echo "  ./install.sh"
    echo ""
    echo "Ou double-cliquez sur 'install.sh' dans le Finder"
    exit 1
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier que les dépendances sont installées
if ! python -c "import streamlit" 2>/dev/null; then
    warn "Dépendances manquantes. Installation..."
    pip install -r requirements.txt --quiet
    info "Dépendances installées"
fi

# Démarrer Ollama automatiquement en arrière-plan si nécessaire
if ! curl -s http://localhost:11434 > /dev/null 2>&1; then
    warn "Démarrage d'Ollama..."
    ollama serve > /tmp/ollama.log 2>&1 &
    OLLAMA_PID=$!
    sleep 3
    
    if curl -s http://localhost:11434 > /dev/null 2>&1; then
        info "Ollama démarré automatiquement (PID: $OLLAMA_PID)"
    else
        error "Impossible de démarrer Ollama automatiquement"
        echo "   Veuillez démarrer Ollama manuellement dans un autre terminal:"
        echo "   ollama serve"
        exit 1
    fi
else
    info "Ollama est déjà en cours d'exécution"
fi

# Vérifier que le modèle existe
if ! ollama list | grep -q "llama3.1:8b"; then
    warn "Modèle d'IA non trouvé. Téléchargement..."
    ollama pull llama3.1:8b
    info "Modèle téléchargé"
fi

# Démarrer l'application
echo ""
info "Démarrage de l'application..."
echo "   L'application s'ouvrira automatiquement dans votre navigateur"
echo "   URL: http://localhost:8501"
echo ""
echo "   Pour arrêter: Ctrl+C ou utilisez le bouton dans l'interface"
echo "   (Ollama continuera de tourner en arrière-plan)"
echo ""

# Fonction de nettoyage à l'arrêt
cleanup() {
    echo ""
    warn "Arrêt de l'application..."
    if [ ! -z "$OLLAMA_PID" ]; then
        kill $OLLAMA_PID 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

python main.py

