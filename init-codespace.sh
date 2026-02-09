#!/bin/bash

# JARVIS - Script de Inicializacao para GitHub Codespace

set -e

echo "======================================"
echo "  JARVIS Codespace Setup"
echo "======================================"
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Funcoes
info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar Docker
info "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    error "Docker nao encontrado"
    exit 1
fi
success "Docker OK: $(docker --version)"

# Verificar docker-compose
info "Verificando docker-compose..."
if ! command -v docker-compose &> /dev/null; then
    error "docker-compose nao encontrado"
    exit 1
fi
success "docker-compose OK"

# Iniciar servicos
info "Iniciando servicos (docker-compose up -d --build)..."
echo ""
docker-compose up -d --build
echo ""

# Aguardar inicializacao
info "Aguardando 30 segundos para servicos ficarem prontos..."
sleep 30

# Status
info "Verificando status dos containers..."
echo ""
docker-compose ps
echo ""

# Mensagem final
success "Servicos iniciados!"
echo ""
echo "Proximos passos:"
echo "  docker-compose logs -f          # Ver logs em tempo real"
echo "  docker-compose ps               # Ver status dos servicos"
echo "  curl http://localhost:8001/health  # Testar LLM Service"
echo ""
