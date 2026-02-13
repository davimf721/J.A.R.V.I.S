#!/bin/bash

################################################################################
# JARVIS - Gerador de Podcasts
# Script para facilitar geração de podcasts via CLI
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

show_menu() {
    clear
    echo -e "${BOLD}${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║     JARVIS - Gerador de Podcasts                              ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo "Escolha uma opção:"
    echo ""
    echo "  1) 📰 Gerar Podcast com Notícias"
    echo "  2) 🎙️  Gerar Podcast Personalizado"
    echo "  3) ⚙️  Configurar Parâmetros"
    echo "  4) 📊 Ver Status do Último Podcast"
    echo "  5) 🔍 Verificar Saúde dos Serviços"
    echo "  6) 📚 Ver Documentação da API"
    echo "  7) ❌ Sair"
    echo ""
    read -p "Escolha [1-7]: " choice
}

# ==================== VERIFICAÇÕES ====================
check_services() {
    info "Verificando serviços..."
    
    services=(
        "http://localhost:8010/health:Orchestrator"
        "http://localhost:8001/health:LLM Service"
        "http://localhost:8002/health:News Service"
        "http://localhost:8004/health:TTS Service"
    )
    
    all_healthy=true
    
    for service in "${services[@]}"; do
        url="${service%:*}"
        name="${service#*:}"
        
        if curl -sf "$url" &> /dev/null; then
            success "$name"
        else
            error "$name"
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = false ]; then
        warning "Alguns serviços não estão saudáveis"
        warning "Execute: docker-compose restart"
        return 1
    fi
    
    return 0
}

# ==================== GERAÇÃO DE PODCASTS ====================
generate_news_podcast() {
    echo ""
    echo -e "${BLUE}━━━ Parâmetros de Podcast com Notícias ━━━${NC}"
    echo ""
    
    read -p "Nome do Agente [JARVIS]: " agent_name
    agent_name=${agent_name:-JARVIS}
    
    echo ""
    echo "Tipo de Agente:"
    echo "  1) news_anchor (Âncora de Notícias)"
    echo "  2) storyteller (Contador de Histórias)"
    echo "  3) analyst (Analista)"
    read -p "Escolha [1-3] [1]: " agent_type_choice
    agent_type_choice=${agent_type_choice:-1}
    
    case $agent_type_choice in
        1) agent_type="news_anchor" ;;
        2) agent_type="storyteller" ;;
        3) agent_type="analyst" ;;
        *) agent_type="news_anchor" ;;
    esac
    
    read -p "Duração em minutos [8]: " duration
    duration=${duration:-8}
    
    read -p "Categoria de Notícias (tech,business,health,general) [general]: " category
    category=${category:-general}
    
    # Gerar ID único
    podcast_id="podcast_$(date +%s)"
    
    echo ""
    info "Enviando para fila de processamento..."
    
    # Fazer chamada à API
    response=$(curl -s -X POST http://localhost:8010/api/podcast/generate \
        -H "Content-Type: application/json" \
        -d "{
            \"id\": \"$podcast_id\",
            \"agent_name\": \"$agent_name\",
            \"agent_type\": \"$agent_type\",
            \"language\": \"pt-BR\",
            \"podcast_duration_minutes\": $duration,
            \"category\": \"$category\"
        }")
    
    echo ""
    success "Podcast enfileirado!"
    echo ""
    echo -e "${BOLD}📌 Informações:${NC}"
    echo "  ID do Job: $podcast_id"
    echo "  Agente: $agent_name"
    echo "  Tipo: $agent_type"
    echo "  Duração: ${duration} minutos"
    echo "  Categoria: $category"
    echo ""
    echo -e "${BOLD}Resposta da API:${NC}"
    echo "$response" | jq . 2>/dev/null || echo "$response"
    echo ""
    
    read -p "Verificar status? (s/n) [s]: " check_status
    check_status=${check_status:-s}
    if [ "$check_status" = "s" ] || [ "$check_status" = "S" ]; then
        check_podcast_status "$podcast_id"
    fi
}

generate_custom_podcast() {
    echo ""
    echo -e "${BLUE}━━━ Criar Podcast Personalizado ━━━${NC}"
    echo ""
    
    read -p "Nome do Agente: " agent_name
    if [ -z "$agent_name" ]; then
        error "Nome do Agente é obrigatório"
        return 1
    fi
    
    read -p "Tipo de Agente: " agent_type
    
    # Permitir input de notícias
    echo ""
    echo "Insira título da notícia (ou deixe em branco para pular):"
    read -p "Notícia 1: " news1
    read -p "Notícia 2: " news2
    read -p "Notícia 3: " news3
    
    news_array="["
    if [ ! -z "$news1" ]; then
        news_array="$news_array{\"title\": \"$news1\"},"
    fi
    if [ ! -z "$news2" ]; then
        news_array="$news_array{\"title\": \"$news2\"},"
    fi
    if [ ! -z "$news3" ]; then
        news_array="$news_array{\"title\": \"$news3\"}"
    fi
    news_array="${news_array%,}]"
    
    podcast_id="custom_$(date +%s)"
    
    echo ""
    info "Enviando para processamento..."
    
    response=$(curl -s -X POST http://localhost:8010/api/podcast/generate \
        -H "Content-Type: application/json" \
        -d "{
            \"id\": \"$podcast_id\",
            \"agent_name\": \"$agent_name\",
            \"agent_type\": \"$agent_type\",
            \"language\": \"pt-BR\",
            \"news\": $news_array
        }")
    
    echo ""
    success "Podcast enfileirado!"
    echo ""
    echo -e "${BOLD}ID do Job:${NC} $podcast_id"
    echo ""
    echo -e "${BOLD}Resposta da API:${NC}"
    echo "$response" | jq . 2>/dev/null || echo "$response"
    echo ""
}

# ==================== CONFIGURAÇÕES ====================
configure_parameters() {
    echo ""
    echo -e "${BLUE}━━━ Configurar Parâmetros ━━━${NC}"
    echo ""
    
    echo "Modelos e Configurações Disponíveis:"
    echo ""
    
    # Obter modelos disponíveis do Ollama
    echo "Modelos Ollama disponíveis:"
    curl -s http://localhost:11435/api/tags 2>/dev/null | jq -r '.models[].name' 2>/dev/null || {
        warning "Ollama não está respondendo"
        return 1
    }
    echo ""
    
    read -p "Configurar modelo LLM? (s/n) [n]: " configure_model
    if [ "$configure_model" = "s" ] || [ "$configure_model" = "S" ]; then
        read -p "Nome do modelo: " model_name
        info "Para usar este modelo, edite o arquivo .env:"
        info "  OLLAMA_MODEL=$model_name"
        info "Depois execute: docker-compose restart llm-service"
    fi
    
    read -p "Configurar voz TTS? (s/n) [n]: " configure_voice
    if [ "$configure_voice" = "s" ] || [ "$configure_voice" = "S" ]; then
        echo "Vozes disponíveis em português:"
        echo "  - pt-BR-FranciscaNeural (padrão)"
        echo "  - pt-BR-AntonioNeural"
        echo "  ou outras vozes do Azure"
        read -p "Voz para próximos podcasts: " voice_name
        info "Use 'voice: \"$voice_name\"' nas requisições da API"
    fi
}

# ==================== STATUS E MONITORAMENTO ====================
check_podcast_status() {
    local podcast_id=$1
    
    if [ -z "$podcast_id" ]; then
        read -p "ID do Podcast: " podcast_id
    fi
    
    if [ -z "$podcast_id" ]; then
        error "ID do Podcast não fornecido"
        return 1
    fi
    
    echo ""
    info "Verificando status de $podcast_id..."
    echo ""
    
    for i in {1..10}; do
        status=$(curl -s http://localhost:8010/api/podcast/status/$podcast_id)
        
        current_status=$(echo "$status" | jq -r '.status // "unknown"' 2>/dev/null)
        
        clear
        echo -e "${BOLD}Status do Podcast: $podcast_id${NC}"
        echo ""
        echo "$status" | jq . 2>/dev/null || echo "$status"
        echo ""
        
        if [ "$current_status" = "completed" ]; then
            success "Podcast concluído com sucesso!"
            
            # Tenta encontrar o arquivo de áudio
            audio_url=$(echo "$status" | jq -r '.result.audio_url // "N/A"' 2>/dev/null)
            if [ "$audio_url" != "N/A" ]; then
                echo ""
                info "Arquivo de áudio: $audio_url"
            fi
            return 0
        elif [ "$current_status" = "processing" ]; then
            echo "Processando... (tentativa $i/10)"
            sleep 6
        elif [ "$current_status" = "failed" ]; then
            error "Podcast falhou!"
            error_msg=$(echo "$status" | jq -r '.error // "Erro desconhecido"' 2>/dev/null)
            echo "Erro: $error_msg"
            return 1
        fi
    done
    
    warning "Podcasts ainda estão processando"
    info "Continue verificando com: ./run-podcast.sh"
}

show_service_health() {
    echo ""
    echo -e "${BLUE}━━━ Saúde dos Serviços ━━━${NC}"
    echo ""
    
    echo "Status do Docker:"
    docker-compose ps
    echo ""
    
    echo "Verificando endpoints..."
    echo ""
    
    services=(
        "http://localhost:8010/health:Orchestrator"
        "http://localhost:8001/health:LLM Service"
        "http://localhost:8002/health:News Service"
        "http://localhost:8003/health:Script Service"
        "http://localhost:8004/health:TTS Service"
        "http://localhost:8005/health:Memory Service"
        "http://localhost:11435/api/tags:Ollama"
        "http://localhost:5432:PostgreSQL"
    )
    
    for service in "${services[@]}"; do
        url="${service%:*}"
        name="${service#*:}"
        
        if curl -sf "$url" &> /dev/null; then
            success "$name"
        else
            error "$name - indisponível"
        fi
    done
    echo ""
}

show_api_docs() {
    echo ""
    echo -e "${BLUE}━━━ Documentação da API ━━━${NC}"
    echo ""
    
    echo -e "${BOLD}🔗 Endpoints Principais:${NC}"
    echo ""
    
    echo "1️⃣  POST /api/podcast/generate"
    echo "    Gera um novo podcast"
    echo ""
    echo "    Exemplo:"
    echo "    ${CYAN}curl -X POST http://localhost:8010/api/podcast/generate \\${NC}"
    echo "    ${CYAN}  -H 'Content-Type: application/json' \\${NC}"
    echo "    ${CYAN}  -d '{${NC}"
    echo "    ${CYAN}    \"id\": \"podcast_001\",${NC}"
    echo "    ${CYAN}    \"agent_name\": \"JARVIS\",${NC}"
    echo "    ${CYAN}    \"agent_type\": \"news_anchor\",${NC}"
    echo "    ${CYAN}    \"language\": \"pt-BR\",${NC}"
    echo "    ${CYAN}    \"podcast_duration_minutes\": 8${NC}"
    echo "    ${CYAN}  }'${NC}"
    echo ""
    
    echo "2️⃣  GET /api/podcast/status/{job_id}"
    echo "    Verifica status de um podcast"
    echo ""
    echo "    Exemplo:"
    echo "    ${CYAN}curl http://localhost:8010/api/podcast/status/podcast_001${NC}"
    echo ""
    
    echo "3️⃣  GET /api/services/status"
    echo "    Verifica status de todos os serviços"
    echo ""
    
    echo "4️⃣  GET /api/agents"
    echo "    Lista agentes disponíveis"
    echo ""
    
    echo -e "${BOLD}📊 Dashboards:${NC}"
    echo ""
    echo "  📈 Grafana:       http://localhost:3000"
    echo "  🐇 RabbitMQ:      http://localhost:15672"
    echo "  🗄️  MinIO:         http://localhost:9001"
    echo "  🔍 Prometheus:    http://localhost:9090"
    echo ""
    
    echo -e "${BOLD}📚 Logs:${NC}"
    echo ""
    echo "  Todos os logs:      ${CYAN}docker-compose logs -f${NC}"
    echo "  Logs de um serviço: ${CYAN}docker-compose logs -f llm-service${NC}"
    echo "  Últimas 100 linhas: ${CYAN}docker-compose logs --tail=100${NC}"
    echo ""
}

# ==================== MAIN LOOP ====================
main() {
    while true; do
        show_menu
        
        case $choice in
            1)
                check_services && generate_news_podcast || warning "Verifique a conexão"
                ;;
            2)
                check_services && generate_custom_podcast || warning "Verifique a conexão"
                ;;
            3)
                configure_parameters
                ;;
            4)
                check_podcast_status
                ;;
            5)
                show_service_health
                ;;
            6)
                show_api_docs
                ;;
            7)
                echo ""
                success "Até logo! 👋"
                echo ""
                exit 0
                ;;
            *)
                error "Opção inválida"
                sleep 2
                ;;
        esac
        
        read -p "Pressione Enter para continuar..." _
    done
}

# ==================== ENTRY POINT ====================
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
