#!/bin/bash
# Script pour arrêter l'application Docker

cd "$(dirname "$0")"

echo "🛑 Arrêt de l'application Docker..."
echo ""

# Utiliser docker compose ou docker-compose selon la version
if docker compose version &> /dev/null; then
    docker compose down
else
    docker-compose down
fi

echo ""
echo "✅ Application arrêtée"

