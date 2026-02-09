#!/bin/bash
# Script de inicialização para Linux/Mac
# Equivalente ao start.ps1 para PowerShell

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funções
info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Verificar Docker
check_docker() {
    info "Verificando Docker..."
    if command -v docker &> /dev/null; then
        docker --version
        success "Docker encontrado"
        return 0
    else
        error "Docker não encontrado! Instale em https://www.docker.com/products/docker-desktop"
        return 1
    fi
}

# Verificar Docker Compose
check_compose() {
    info "Verificando Docker Compose..."
    if command -v docker-compose &> /dev/null; then
        docker-compose --version
        success "Docker Compose encontrado"
        return 0
    elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
        docker compose version
        success "Docker Compose v2 encontrado"
        return 0
    else
        error "Docker Compose não encontrado!"
        return 1
    fi
}

# Criar .env
create_env() {
    info "Verificando arquivo .env..."
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            info "Criando .env a partir de .env.example..."
            cp .env.example .env
            success "Arquivo .env criado"
        else
            warning "Arquivo .env.example não encontrado"
        fi
    else
        success "Arquivo .env já existe"
    fi
}

# Iniciar serviços
start_services() {
    info "Iniciando serviços..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        docker compose up -d
    fi
    
    success "Serviços iniciados"
    echo ""
    show_status
}

# Parar serviços
stop_services() {
    info "Parando serviços..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        docker compose down
    fi
    
    success "Serviços parados"
}

# Status dos serviços
show_status() {
    info "Status dos serviços:"
    echo ""
    
    if command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        docker compose ps
    fi
    
    echo ""
    info "📊 Dashboard URLs:"
    echo "  Orchestrator:      http://localhost:8010/health"
    echo "  LLM Service:       http://localhost:8001/health"
    echo "  News Service:      http://localhost:8002/health"
    echo "  Script Service:    http://localhost:8003/health"
    echo "  TTS Service:       http://localhost:8004/health"
    echo "  Memory Service:    http://localhost:8005/health"
    echo ""
    info "🔍 Admin Consoles:"
    echo "  Grafana:           http://localhost:3000 (admin/admin)"
    echo "  Prometheus:        http://localhost:9090"
    echo "  RabbitMQ:          http://localhost:15672 (jarvis/jarvis_queue_pwd)"
    echo "  Minio:             http://localhost:9001 (minioadmin/minioadmin)"
    echo ""
}

# Ver logs
show_logs() {
    local service=$1
    
    if [ -n "$service" ]; then
        info "Mostrando logs de: $service"
        if command -v docker-compose &> /dev/null; then
            docker-compose logs -f "$service"
        else
            docker compose logs -f "$service"
        fi
    else
        info "Mostrando logs de todos os serviços..."
        if command -v docker-compose &> /dev/null; then
            docker-compose logs -f
        else
            docker compose logs -f
        fi
    fi
}

# Main
main() {
    clear
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║        JARVIS - Microservices Platform Manager         ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    
    # Verificações
    if ! check_docker; then exit 1; fi
    if ! check_compose; then exit 1; fi
    
    create_env
    echo ""
    
    # Parse arguments
    case "${1:-start}" in
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            sleep 2
            start_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$2"
            ;;
        *)
            warning "Ação desconhecida: $1"
            echo ""
            info "Uso:"
            echo "  ./start.sh start           # Iniciar todos os serviços"
            echo "  ./start.sh stop            # Parar serviços"
            echo "  ./start.sh restart         # Reiniciar serviços"
            echo "  ./start.sh status          # Ver status"
            echo "  ./start.sh logs            # Ver logs"
            echo "  ./start.sh logs orchestrator  # Ver logs de um serviço"
            echo ""
            ;;
    esac
}

# Executar
main "$@"
