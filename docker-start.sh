#!/bin/bash
# Script pour démarrer l'application avec Docker
# Tout est automatique - pas besoin d'installer quoi que ce soit !

cd "$(dirname "$0")"

echo "🐳 Démarrage avec Docker - Assistant Médical"
echo "=============================================="
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

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    error "Docker n'est pas installé."
    echo ""
    echo "Installez Docker Desktop depuis :"
    echo "  https://www.docker.com/products/docker-desktop"
    echo ""
    echo "Après installation, relancez ce script."
    exit 1
fi

info "Docker trouvé"

# Vérifier si Docker Compose est disponible
if ! docker compose version &> /dev/null && ! docker-compose version &> /dev/null; then
    error "Docker Compose n'est pas disponible."
    exit 1
fi

info "Docker Compose trouvé"

# Démarrer les services
echo ""
warn "Démarrage des services (cela peut prendre quelques minutes la première fois)..."
echo ""

# Utiliser docker compose ou docker-compose selon la version
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

$COMPOSE_CMD up --build -d

if [ $? -eq 0 ]; then
    echo ""
    info "Services démarrés avec succès !"
    echo ""
    echo "L'application sera disponible dans quelques instants sur :"
    echo "  http://localhost:8501"
    echo ""
    echo "Pour voir les logs :"
    echo "  $COMPOSE_CMD logs -f app"
    echo ""
    echo "Pour arrêter l'application :"
    echo "  $COMPOSE_CMD down"
    echo ""
    echo "Ou double-cliquez sur 'docker-stop.sh'"
    echo ""
    
    # Attendre un peu et ouvrir le navigateur
    sleep 5
    if command -v open &> /dev/null; then
        open http://localhost:8501
    fi
else
    error "Erreur lors du démarrage des services"
    exit 1
fi

