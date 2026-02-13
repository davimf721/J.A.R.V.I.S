#!/bin/bash

################################################################################
# JARVIS - Sistema de Podcast Inteligente
# Script de Inicialização Único para macOS
# Instala e configura TUDO automaticamente
################################################################################

set -e

# ==================== CORES & FORMATAÇÃO ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# ==================== FUNÇÕES DE LOG ====================
log_header() {
    clear
    echo -e "${BOLD}${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║     JARVIS - Sistema de Podcast Inteligente                    ║"
    echo "║     Setup Completo para macOS                                  ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

info() {
    echo -e "${CYAN}[↳]${NC} $1"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

loading() {
    echo -ne "${CYAN}[⏳]${NC} $1"
}

done_loading() {
    echo -e "\r${GREEN}[✓]${NC} $1"
}

section() {
    echo ""
    echo -e "${BLUE}━━━ $1 ━━━${NC}"
}

# ==================== VERIFICAÇÕES ====================
check_os() {
    log_header
    section "🔍 Verificando Sistema Operacional"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        success "macOS detectado"
        ARCH=$(uname -m)
        if [[ "$ARCH" == "arm64" ]]; then
            success "Arquitetura: Apple Silicon (M1/M2/M3)"
        else
            success "Arquitetura: Intel"
        fi
    else
        error "Este script é apenas para macOS!"
        exit 1
    fi
}

check_xcode() {
    section "🔍 Verificando Xcode Command Line Tools"
    
    if ! xcode-select -p &> /dev/null; then
        warning "Xcode Command Line Tools não encontrado"
        info "Instalando Xcode Command Line Tools..."
        xcode-select --install
        echo -e "${YELLOW}Por favor, complete a instalação no popup e execute o script novamente.${NC}"
        exit 1
    else
        success "Xcode Command Line Tools já instalado"
    fi
}

check_homebrew() {
    section "🔍 Verificando Homebrew"
    
    if ! command -v brew &> /dev/null; then
        warning "Homebrew não encontrado"
        info "Instalando Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Adicionar ao PATH (para Apple Silicon)
        if [[ $(uname -m) == "arm64" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
        
        success "Homebrew instalado"
    else
        success "Homebrew já instalado"
    fi
}

check_docker() {
    section "🔍 Verificando Docker Desktop"
    
    if ! command -v docker &> /dev/null; then
        warning "Docker não encontrado"
        
        info "Instalando Docker via Homebrew..."
        brew install docker docker-compose
        
        warning "Docker Desktop requer inicialização manual"
        warning "Por favor, as seguintes opções:"
        echo "  1. Instalar via Homebrew Cask (recomendado):"
        echo "     brew install --cask docker"
        echo ""
        echo "  2. Ou baixar manualmente:"
        echo "     https://www.docker.com/products/docker-desktop"
        echo ""
        error "Aguardando Docker Desktop estar instalado..."
        read -p "Pressione Enter após instalar Docker Desktop..." _
        
        if ! command -v docker &> /dev/null; then
            error "Docker ainda não está disponível!"
            exit 1
        fi
    fi
    
    success "Docker encontrado"
    docker --version
}

verify_docker_running() {
    section "🔍 Verificando Docker Daemon"
    
    if ! docker info &> /dev/null; then
        warning "Docker não está rodando"
        info "Iniciando Docker Desktop..."
        
        # Tentar iniciar Docker no macOS
        if [ -f /Applications/Docker.app/Contents/MacOS/Docker ]; then
            open -a Docker
            sleep 5
            
            # Aguardar Docker ficar pronto
            loading "Aguardando Docker ficar pronto..."
            for i in {1..30}; do
                if docker info &> /dev/null; then
                    done_loading "Docker está pronto!"
                    return 0
                fi
                sleep 2
            done
            
            error "Docker não iniciou dentro do tempo esperado"
            exit 1
        else
            error "Docker Desktop não encontrado em /Applications/Docker.app"
            exit 1
        fi
    else
        success "Docker está rodando"
    fi
}

check_disk_space() {
    section "🔍 Verificando Espaço em Disco"
    
    available_gb=$(df -H /Users | awk 'NR==2 {print $4}' | sed 's/Gi//' | sed 's/Ti/0/')
    available_gb=$(echo "$available_gb" | sed 's/[^0-9]*//g')
    
    if [ "$available_gb" -lt 20 ]; then
        warning "Apenas ${available_gb}GB disponível (20GB recomendado)"
        warning "Continuando mesmo assim..."
    else
        success "Espaço em disco OK (${available_gb}GB disponível)"
    fi
}

diagnose_arm64() {
    section "🔍 Diagnóstico de Compatibilidade (Apple Silicon)"
    
    ARCH=$(uname -m)
    
    if [[ "$ARCH" == "arm64" ]]; then
        success "Apple Silicon (arm64) detectado"
        
        info "Verificando Docker para suporte arm64..."
        if docker info 2>/dev/null | grep -q "linux/arm64"; then
            success "Docker suporta linux/arm64"
        else
            warning "Docker pode não estar otimizado para arm64"
            info "Pode haver degradação de performance"
        fi
        
        # Remover imagens antigas incompatíveis
        info "Limpando imagens antigas..."
        docker rmi ghcr.io/chroma-core/chroma:0.3.23 2>/dev/null || true
        
    else
        success "Arquitetura Intel detectada"
    fi
}

# ==================== CONFIGURAÇÃO ====================
setup_env() {
    section "⚙️  Configurando Variáveis de Ambiente"
    
    if [ ! -f ".env" ]; then
        info "Criando arquivo .env..."
        cp .env.example .env
        success "Arquivo .env criado com configurações padrão"
        
        warning "Por favor, revise o arquivo .env se necessário:"
        info "  - Modelos LLM (OLLAMA_MODEL)"
        info "  - Credenciais dos bancos de dados"
        info "  - Chaves de API externas"
    else
        success "Arquivo .env já existe"
    fi
}

create_directories() {
    section "📁 Criando Diretórios Necessários"
    
    mkdir -p data/postgres
    mkdir -p data/redis
    mkdir -p data/chromadb
    mkdir -p data/minio
    mkdir -p data/ollama
    mkdir -p outputs/podcasts
    mkdir -p outputs/logs
    
    success "Diretórios criados"
}

# ==================== DOCKER ====================
build_and_start() {
    section "🐳 Construindo e Iniciando Contêineres"
    
    loading "Verificando compatibilidade do docker-compose..."
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    done_loading "Usando: $COMPOSE_CMD"
    
    # Limpar containers anteriores com erro
    info "Limpando containers anteriores com erro..."
    $COMPOSE_CMD down &> /dev/null || true
    
    info "Construindo imagens (primeira vez pode levar 5-10 minutos)..."
    if ! $COMPOSE_CMD build --no-cache 2>&1 | tail -20; then
        error "Erro ao construir imagens"
        warning "Tente:"
        echo "  1. Verifique conexão de internet"
        echo "  2. Limpe Docker: docker system prune -a"
        echo "  3. Execute novamente: ./setup-mac.sh"
        exit 1
    fi
    
    success "Imagens construídas"
    
    info "Iniciando contêineres..."
    if ! $COMPOSE_CMD up -d; then
        error "Erro ao iniciar contêineres"
        warning "Verifique erros acima e tente:"
        echo "  docker-compose logs"
        exit 1
    fi
    
    success "Contêineres iniciados"
}

wait_services() {
    section "⏳ Aguardando Serviços Ficarem Prontos"
    
    services=(
        "http://localhost:11435/api/tags:Ollama LLM"
        "http://localhost:5432:PostgreSQL"
        "http://localhost:6379:Redis"
        "http://localhost:8000:ChromaDB"
        "http://localhost:8001/health:LLM Service"
        "http://localhost:8002/health:News Service"
        "http://localhost:8003/health:Script Service"
        "http://localhost:8004/health:TTS Service"
        "http://localhost:8005/health:Memory Service"
        "http://localhost:8010/health:Orchestrator"
    )
    
    for service in "${services[@]}"; do
        url="${service%:*}"
        name="${service#*:}"
        
        loading "Aguardando $name..."
        
        max_attempts=60
        attempt=1
        
        while ! curl -sf "$url" &> /dev/null; do
            if [ $attempt -ge $max_attempts ]; then
                error "Timeout aguardando $name"
                return 1
            fi
            sleep 2
            attempt=$((attempt + 1))
        done
        
        done_loading "$name está pronto ✓"
    done
}

show_status() {
    section "📊 Status dos Serviços"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        docker compose ps
    fi
}

# ==================== INSTRUÇÕES FINAIS ====================
show_instructions() {
    section "✨ Setup Completo!"
    
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║              JARVIS está pronto para uso!                       ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo ""
    echo -e "${BOLD}🎯 Próximos Passos:${NC}"
    echo ""
    
    echo -e "${BOLD}1. Gerar um Podcast:${NC}"
    echo "   ${CYAN}./run-podcast.sh${NC}"
    echo ""
    
    echo -e "${BOLD}2. Ou use curl para chamar a API diretamente:${NC}"
    echo ""
    echo "   ${CYAN}curl -X POST http://localhost:8010/api/podcast/generate \\${NC}"
    echo "   ${CYAN}  -H 'Content-Type: application/json' \\${NC}"
    echo "   ${CYAN}  -d '{${NC}"
    echo "   ${CYAN}    \"id\": \"podcast_001\",${NC}"
    echo "   ${CYAN}    \"agent_name\": \"JARVIS\",${NC}"
    echo "   ${CYAN}    \"agent_type\": \"news_anchor\",${NC}"
    echo "   ${CYAN}    \"language\": \"pt-BR\"${NC}"
    echo "   ${CYAN}  }'${NC}"
    echo ""
    
    echo -e "${BOLD}3. Verificar Status do Job:${NC}"
    echo "   ${CYAN}curl http://localhost:8010/api/podcast/status/podcast_001${NC}"
    echo ""
    
    echo -e "${BOLD}4. Gerenciar Contêineres:${NC}"
    echo "   ${CYAN}docker-compose ps${NC}           # Ver status"
    echo "   ${CYAN}docker-compose logs -f          # Ver logs em tempo real"
    echo "   ${CYAN}docker-compose logs -f llm-service  # Ver logs de um serviço"
    echo "   ${CYAN}docker-compose down            # Parar tudo"
    echo "   ${CYAN}docker-compose down -v         # Parar e limpar dados"
    echo ""
    
    echo -e "${BOLD}🔗 Dashboards & Ferramentas:${NC}"
    echo "   ${CYAN}Ollama:${NC}      http://localhost:11435"
    echo "   ${CYAN}RabbitMQ:${NC}     http://localhost:15672 (admin/jarvis_queue_pwd)"
    echo "   ${CYAN}MinIO:${NC}        http://localhost:9001 (minioadmin/minioadmin)"
    echo "   ${CYAN}Grafana:${NC}      http://localhost:3000 (admin/admin)"
    echo "   ${CYAN}Prometheus:${NC}   http://localhost:9090"
    echo ""
    
    echo -e "${BOLD}📚 Documentação:${NC}"
    echo "   ${CYAN}README.md${NC}          - Visão geral"
    echo "   ${CYAN}QUICKSTART.md${NC}      - Início rápido"
    echo "   ${CYAN}TROUBLESHOOTING.md${NC} - Resolução de problemas"
    echo "   ${CYAN}API_GUIDE.md${NC}       - Guia da API (será criado)"
    echo ""
}

cleanup_on_exit() {
    if [ $? -ne 0 ]; then
        echo ""
        error "Setup foi interrompido"
        warning "Execute o script novamente para continuar"
        exit 1
    fi
}

# ==================== MAIN ====================
main() {
    trap cleanup_on_exit EXIT
    
    check_os
    check_xcode
    check_homebrew
    check_docker
    verify_docker_running
    diagnose_arm64
    check_disk_space
    setup_env
    create_directories
    build_and_start
    
    section "⏳ Etapa Final - Aguardando Serviços"
    if wait_services; then
        show_status
        show_instructions
        
        section "🎉 Sucesso! Tudo está pronto!"
        success "JARVIS foi instalado e está rodando"
        
        echo ""
        echo -e "${BOLD}Dica:${NC} Para parar os serviços, execute:"
        echo "  ${CYAN}docker-compose down${NC}"
        echo ""
        echo -e "Obrigado por usar ${BOLD}JARVIS${NC}! 🎙️"
        echo ""
    else
        error "Alguns serviços não ficaram prontos"
        warning "Verifique os logs com: docker-compose logs"
        warning "Tente:"
        echo "  1. docker-compose down"
        echo "  2. docker system prune -a"
        echo "  3. ./setup-mac.sh"
        exit 1
    fi
}

# ==================== ENTRY POINT ====================
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
