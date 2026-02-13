#!/bin/bash

################################################################################
# JARVIS - Gerenciador de Serviços
# Facilita operações comuns com docker-compose
################################################################################

set -e

# ==================== CORES ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

# ==================== FUNÇÕES ====================
info() { echo -e "${CYAN}[↳]${NC} $1"; }
success() { echo -e "${GREEN}[✓]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }
warning() { echo -e "${YELLOW}[⚠]${NC} $1"; }

show_usage() {
    cat << EOF
${BOLD}JARVIS - Gerenciador de Serviços${NC}

${BOLD}Uso:${NC}
    ./manage.sh <comando> [opções]

${BOLD}Comandos:${NC}
    start           Inicia todos os serviços
    stop            Para todos os serviços
    restart         Reinicia todos os serviços
    status          Mostra status dos serviços
    logs            Monitora logs em tempo real
    logs <service>  Logs de um serviço específico
    health          Verifica saúde de todos os serviços
    clean           Remove containers e volumes (CUIDADO!)
    rebuild         Reconstrói todas as imagens
    shell <service> Abre shell em um container
    exec <service> <cmd>  Executa comando em um container

${BOLD}Serviços Disponíveis:${NC}
    ollama
    postgres
    redis
    rabbitmq
    chromadb
    minio
    llm-service
    news-service
    script-service
    tts-service
    memory-service
    orchestrator
    prometheus
    grafana

${BOLD}Exemplos:${NC}
    ./manage.sh start
    ./manage.sh logs orchestrator
    ./manage.sh shell llm-service
    ./manage.sh health
    ./manage.sh exec llm-service python -c "print('test')"

EOF
}

# ==================== OPERAÇÕES ====================
start_services() {
    section "Iniciando serviços..."
    docker-compose up -d
    success "Serviços iniciados"
    sleep 3
    status_services
}

stop_services() {
    section "Parando serviços..."
    docker-compose down
    success "Serviços parados"
}

restart_services() {
    case ${1:-all} in
        all)
            section "Reiniciando todos os serviços..."
            docker-compose restart
            success "Todos os serviços reiniciados"
            ;;
        *)
            info "Reiniciando $1..."
            docker-compose restart "$1"
            success "$1 reiniciado"
            ;;
    esac
    sleep 2
    status_services
}

status_services() {
    echo ""
    info "Status dos Serviços:"
    docker-compose ps
    echo ""
}

show_logs() {
    if [ -z "$1" ]; then
        info "Mostrando logs de todos os serviços (Ctrl+C para parar)..."
        docker-compose logs -f --tail=50
    else
        info "Mostrando logs de $1 (Ctrl+C para parar)..."
        docker-compose logs -f "$1"
    fi
}

check_health() {
    echo ""
    info "Verificando saúde dos serviços..."
    echo ""
    
    services=(
        "http://localhost:11435/api/tags:Ollama"
        "http://localhost:5432:PostgreSQL"
        "http://localhost:6379:Redis"
        "http://localhost:8000/api/v1/heartbeat:ChromaDB"
        "http://localhost:8001/health:LLM Service"
        "http://localhost:8002/health:News Service"
        "http://localhost:8003/health:Script Service"
        "http://localhost:8004/health:TTS Service"
        "http://localhost:8005/health:Memory Service"
        "http://localhost:8010/health:Orchestrator"
    )
    
    healthy=0
    total=${#services[@]}
    
    for service in "${services[@]}"; do
        url="${service%:*}"
        name="${service#*:}"
        
        if curl -sf "$url" &> /dev/null; then
            success "$name"
            ((healthy++))
        else
            error "$name"
        fi
    done
    
    echo ""
    info "Saúde: $healthy/$total serviços prontos"
    
    if [ $healthy -eq $total ]; then
        success "Todos os serviços estão saudáveis!"
        return 0
    else
        warning "Alguns serviços não estão prontos"
        warning "Verifique logs com: ./manage.sh logs"
        return 1
    fi
}

clean_services() {
    warning "Isto vai remover containers e volumes!"
    read -p "Tem certeza? (s/n): " confirm
    
    if [ "$confirm" != "s" ] && [ "$confirm" != "S" ]; then
        info "Cancelado"
        return 1
    fi
    
    section "Limpando containers e volumes..."
    docker-compose down -v
    success "Limpeza completa"
    success "Para recomeçar, execute: ./setup-mac.sh"
}

rebuild_images() {
    section "Reconstruindo imagens..."
    docker-compose build --no-cache
    success "Imagens reconstruídas"
    
    read -p "Deseja iniciar os serviços? (s/n): " start
    if [ "$start" = "s" ] || [ "$start" = "S" ]; then
        start_services
    fi
}

shell_service() {
    if [ -z "$1" ]; then
        error "Especifique um serviço"
        return 1
    fi
    
    info "Abrindo shell em $1..."
    docker-compose exec "$1" /bin/bash || docker-compose exec "$1" /bin/sh
}

exec_command() {
    local service=$1
    shift
    local cmd="$@"
    
    if [ -z "$service" ] || [ -z "$cmd" ]; then
        error "Sintaxe: manage.sh exec <service> <comando>"
        return 1
    fi
    
    info "Executando em $service: $cmd"
    docker-compose exec "$service" bash -c "$cmd"
}

section() {
    echo ""
    echo -e "${BLUE}━━━ $1 ━━━${NC}"
    echo ""
}

# ==================== MAIN ====================
main() {
    case ${1:-help} in
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services "$2"
            ;;
        status)
            status_services
            ;;
        logs)
            show_logs "$2"
            ;;
        health)
            check_health
            ;;
        clean)
            clean_services
            ;;
        rebuild)
            rebuild_images
            ;;
        shell)
            shell_service "$2"
            ;;
        exec)
            shift
            exec_command "$@"
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            error "Comando desconhecido: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# ==================== ENTRY POINT ====================
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
