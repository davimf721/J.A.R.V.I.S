#!/bin/bash

################################################################################
# JARVIS - Quick Podcast Generator
# Script rápido para gerar um podcast em 3 linhas
################################################################################

# Cores
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'
BOLD='\033[1m'

show_help() {
    cat << EOF
${BOLD}${CYAN}JARVIS - Gerador Rápido de Podcast${NC}

${BOLD}Uso:${NC}
    $0 [opções]

${BOLD}Opções:${NC}
    --name STRING       Nome do agente/podcast (padrão: JARVIS)
    --type TYPE         Tipo: podcast_daily, market_analysis, content_generator,
                           email_summary, code_assistant (padrão: podcast_daily)
    --duration MINUTOS  Duração em minutos (padrão: 12)
    --category CAT      Categoria de notícias (padrão: general)
    --language LANG     Idioma pt-BR, en-US, es-ES (padrão: pt-BR)
    --output DIR        Diretório de saída (padrão: pasta atual)
    --wait              Aguardar conclusão e baixar áudio
    --help              Mostrar esta mensagem

${BOLD}Exemplos:${NC}
    # Criar podcast padrão
    $0 --wait

    # Podcast de 10 minutos
    $0 --duration 10 --wait

    # Podcast com nome personalizado
    $0 --name "MeuPodcast" --wait

    # Podcast em inglês
    $0 --language en-US --wait

${BOLD}Tipos disponíveis:${NC}
    podcast_daily      - Podcast com análise e opinião (padrão)
    market_analysis    - Análise de mercado para investidores tech
    content_generator  - Conteúdo educativo com explicações profundas
    email_summary      - Briefing executivo rápido (~3 min)
    code_assistant     - Dev Talk: podcast técnico para programadores

EOF
}

# Defaults
AGENT_NAME="JARVIS"
AGENT_TYPE="podcast_daily"
DURATION=12
CATEGORY="general"
LANGUAGE="pt-BR"
OUTPUT_DIR="."
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
        --output)
            OUTPUT_DIR="$2"
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
                
                # Extract audio path from result
                AUDIO_PATH=$(echo "$STATUS_RESPONSE" | jq -r '.result.audio_path // ""' 2>/dev/null)
                
                if [ ! -z "$AUDIO_PATH" ] && [ "$AUDIO_PATH" != "null" ]; then
                    echo ""
                    echo -e "${CYAN}[↳]${NC} Baixando áudio do container..."
                    
                    # Criar nome do arquivo de saída
                    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
                    OUTPUT_FILE="${OUTPUT_DIR}/${AGENT_NAME}_${TIMESTAMP}.mp3"
                    
                    # Extrair nome do arquivo do path
                    AUDIO_FILENAME=$(basename "$AUDIO_PATH")
                    
                    # Copiar do container para local
                    docker cp jarvis-tts-service:"$AUDIO_PATH" "$OUTPUT_FILE" 2>/dev/null
                    
                    if [ -f "$OUTPUT_FILE" ]; then
                        FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
                        echo -e "${GREEN}[✓]${NC} Áudio baixado com sucesso!"
                        echo ""
                        echo -e "${GREEN}🎙️  Arquivo salvo:${NC}"
                        echo -e "    ${BOLD}$OUTPUT_FILE${NC} ($FILE_SIZE)"
                        echo ""
                        
                        # Mostrar também o roteiro se disponível
                        SCRIPT_PREVIEW=$(echo "$STATUS_RESPONSE" | jq -r '.result.script // ""' 2>/dev/null | head -c 200)
                        if [ ! -z "$SCRIPT_PREVIEW" ] && [ "$SCRIPT_PREVIEW" != "null" ]; then
                            echo -e "${CYAN}📝 Preview do roteiro:${NC}"
                            echo "    ${SCRIPT_PREVIEW}..."
                            echo ""
                            
                            # Salvar roteiro também
                            SCRIPT_FILE="${OUTPUT_DIR}/${AGENT_NAME}_${TIMESTAMP}.txt"
                            echo "$STATUS_RESPONSE" | jq -r '.result.script // ""' > "$SCRIPT_FILE"
                            echo -e "${GREEN}[✓]${NC} Roteiro salvo em: ${BOLD}$SCRIPT_FILE${NC}"
                        fi
                    else
                        echo -e "${YELLOW}[⚠]${NC} Não foi possível baixar o áudio automaticamente"
                        echo "    Caminho no container: $AUDIO_PATH"
                        echo ""
                        echo "    Baixe manualmente com:"
                        echo "    docker cp jarvis-tts-service:$AUDIO_PATH ./${AGENT_NAME}.mp3"
                    fi
                else
                    echo ""
                    echo -e "${YELLOW}[⚠]${NC} Áudio não encontrado no resultado"
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
        echo "  ${BOLD}bash quick-podcast.sh --wait${NC}"
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
