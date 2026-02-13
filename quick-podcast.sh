#!/bin/bash

################################################################################
# JARVIS - Quick Podcast Generator
# Script rápido para gerar um podcast em 3 linhas
################################################################################

# Cores
CYAN='\033[0;36m'
GREEN='\033[0;32m'
NC='\033[0m'
BOLD='\033[1m'

show_help() {
    cat << EOF
${BOLD}${CYAN}JARVIS - Gerador Rápido de Podcast${NC}

${BOLD}Uso:${NC}
    $0 [opções]

${BOLD}Opções:${NC}
    --name STRING       Nome do agente (padrão: JARVIS)
    --type TYPE         Tipo de agente: news_anchor, storyteller, analyst
                       (padrão: news_anchor)
    --duration MINUTOS  Duração em minutos (padrão: 8)
    --category CAT      Categoria de notícias (padrão: general)
    --language LANG     Idioma pt-BR, en-US, es-ES (padrão: pt-BR)
    --wait              Aguardar conclusão e baixar áudio
    --help              Mostrar esta mensagem

${BOLD}Exemplos:${NC}
    # Criar podcast padrão
    $0

    # Podcast de 10 minutos do tipo storyteller
    $0 --type storyteller --duration 10

    # Podcast com categoria tech e aguardar conclusão
    $0 --category tech --wait

    # Podcast em inglês
    $0 --language en-US

EOF
}

# Defaults
AGENT_NAME="JARVIS"
AGENT_TYPE="news_anchor"
DURATION=8
CATEGORY="general"
LANGUAGE="pt-BR"
WAIT=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --name)
            AGENT_NAME="$2"
            shift 2
            ;;
        --type)
            AGENT_TYPE="$2"
            shift 2
            ;;
        --duration)
            DURATION="$2"
            shift 2
            ;;
        --category)
            CATEGORY="$2"
            shift 2
            ;;
        --language)
            LANGUAGE="$2"
            shift 2
            ;;
        --wait)
            WAIT=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Opção desconhecida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Generate podcast ID
PODCAST_ID="podcast_$(date +%s)"

echo -e "${CYAN}╔═══════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  JARVIS - Gerador de Podcast        ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════╝${NC}"
echo ""

# Check connectivity
echo -e "${CYAN}[↳]${NC} Verificando conexão com Orchestrator..."
if ! curl -sf http://localhost:8010/health > /dev/null 2>&1; then
    echo -e "${RED}[✗]${NC} Orchestrator não está acessível"
    echo ""
    echo "Inicie os serviços com:"
    echo "  docker-compose up -d"
    exit 1
fi
echo -e "${GREEN}[✓]${NC} Conectado"

# Generate podcast
echo ""
echo -e "${CYAN}📝 Parâmetros:${NC}"
echo "  ID:        $PODCAST_ID"
echo "  Agente:    $AGENT_NAME"
echo "  Tipo:      $AGENT_TYPE"
echo "  Duração:   ${DURATION} min"
echo "  Categoria: $CATEGORY"
echo "  Idioma:    $LANGUAGE"
echo ""

echo -e "${CYAN}[↳]${NC} Enviando para fila..."

# Send request
RESPONSE=$(curl -s -X POST http://localhost:8010/api/podcast/generate \
    -H "Content-Type: application/json" \
    -d "{
        \"id\": \"$PODCAST_ID\",
        \"agent_name\": \"$AGENT_NAME\",
        \"agent_type\": \"$AGENT_TYPE\",
        \"language\": \"$LANGUAGE\",
        \"podcast_duration_minutes\": $DURATION,
        \"category\": \"$CATEGORY\"
    }")

STATUS=$(echo "$RESPONSE" | jq -r '.status // "error"' 2>/dev/null)

if [ "$STATUS" = "pending" ]; then
    echo -e "${GREEN}[✓]${NC} Podcast enfileirado!"
    echo ""
    echo -e "${GREEN}ID do Job: ${BOLD}$PODCAST_ID${NC}"
    echo ""
    
    if [ "$WAIT" = true ]; then
        echo -e "${CYAN}[↳]${NC} Aguardando conclusão..."
        echo ""
        
        # Monitor status
        COMPLETED=false
        MAX_WAIT=600  # 10 minutos
        ELAPSED=0
        
        while [ "$COMPLETED" = false ]; do
            STATUS_RESPONSE=$(curl -s http://localhost:8010/api/podcast/status/$PODCAST_ID)
            CURRENT_STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status // "unknown"' 2>/dev/null)
            PROGRESS=$(echo "$STATUS_RESPONSE" | jq -r '.progress // 0' 2>/dev/null)
            
            echo -ne "\r${CYAN}[⏳]${NC} Status: ${BOLD}$CURRENT_STATUS${NC} (${PROGRESS}%)  "
            
            if [ "$CURRENT_STATUS" = "completed" ]; then
                echo ""
                echo ""
                echo -e "${GREEN}[✓]${NC} Podcast concluído!"
                
                # Extract audio URL
                AUDIO_URL=$(echo "$STATUS_RESPONSE" | jq -r '.result.audio_url // ""' 2>/dev/null)
                if [ ! -z "$AUDIO_URL" ]; then
                    echo ""
                    echo -e "${GREEN}🎙️  Áudio gravado:${NC}"
                    echo "  $AUDIO_URL"
                fi
                COMPLETED=true
            elif [ "$CURRENT_STATUS" = "failed" ]; then
                echo ""
                echo -e "${RED}[✗]${NC} Podcast falhou"
                ERROR=$(echo "$STATUS_RESPONSE" | jq -r '.error // "Erro desconhecido"' 2>/dev/null)
                echo "Erro: $ERROR"
                COMPLETED=true
            else
                ELAPSED=$((ELAPSED + 2))
                if [ $ELAPSED -gt $MAX_WAIT ]; then
                    echo ""
                    echo -e "${YELLOW}[⚠]${NC} Timeout aguardando (>10 min)"
                    echo "Continuar monitorando com:"
                    echo "  curl http://localhost:8010/api/podcast/status/$PODCAST_ID"
                    COMPLETED=true
                fi
                sleep 2
            fi
        done
    else
        echo -e "${CYAN}[↳]${NC} Monitorar com:"
        echo "  ${BOLD}./quick-podcast.sh --wait${NC}"
        echo ""
        echo "Ou verificar status manualmente:"
        echo "  ${BOLD}curl http://localhost:8010/api/podcast/status/$PODCAST_ID${NC}"
    fi
else
    echo -e "${RED}[✗]${NC} Erro ao criar podcast"
    echo ""
    echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
    exit 1
fi

echo ""
echo -e "${GREEN}Pronto!${NC} 🎉"
echo ""
