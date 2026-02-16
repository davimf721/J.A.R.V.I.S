#!/bin/bash

################################################################################
# JARVIS - Script de Feedback Rápido
# Avalia o podcast e configura preferências de forma simples
################################################################################

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'
BOLD='\033[1m'

USER_ID="${JARVIS_USER:-davi}"
API_URL="http://localhost:8005"

show_help() {
    cat << EOF
${BOLD}${CYAN}JARVIS - Sistema de Feedback${NC}

${BOLD}Uso:${NC}
    $0 <comando> [argumentos]

${BOLD}Comandos de Feedback:${NC}
    rate <nota>              Avaliar último podcast (1-5)
    rate <nota> <liked> <disliked>
                             Avaliar com notícias específicas
                             Ex: rate 4 "1,3" "2"
    
${BOLD}Comandos de Preferências:${NC}
    add <tópico>             Adicionar interesse
    block <tópico>           Bloquear tópico
    show                     Ver suas preferências
    news                     Ver notícias do último podcast
    status                   Verificar status dos serviços
    sync                     Sincronizar histórico de notícias

${BOLD}Exemplos:${NC}
    $0 rate 5                # Podcast foi ótimo!
    $0 rate 4 "1,3" "2"      # Gostou das 1 e 3, não gostou da 2
    $0 add "inteligência artificial"
    $0 add python
    $0 block política
    $0 block futebol
    $0 show
    $0 news
    $0 status
    $0 sync                  # Sincronizar notícias para feedback

${BOLD}Tópicos comuns para adicionar:${NC}
    IA, machine learning, python, programação, startups,
    segurança, linux, cloud, kubernetes, games, mobile

${BOLD}Tópicos comuns para bloquear:${NC}
    política, futebol, celebridades, fofoca, economia

${BOLD}Importante:${NC}
    Para o feedback funcionar, você precisa gerar um podcast primeiro:
    ./quick-podcast.sh

EOF
}

# Verificar conectividade
check_connection() {
    if ! curl -sf "$API_URL/health" > /dev/null 2>&1; then
        echo -e "${RED}[✗]${NC} Serviço de memória não disponível"
        echo "Inicie os serviços com: docker compose up -d"
        exit 1
    fi
}

# Ver preferências
show_preferences() {
    check_connection
    echo -e "${CYAN}📊 Suas preferências:${NC}"
    echo ""
    
    RESPONSE=$(curl -s "$API_URL/api/interests/$USER_ID")
    
    INTERESTS=$(echo "$RESPONSE" | jq -r '.interests | join(", ")' 2>/dev/null)
    BLOCKED=$(echo "$RESPONSE" | jq -r '.blocked_topics | join(", ")' 2>/dev/null)
    SOURCES=$(echo "$RESPONSE" | jq -r '.favorite_sources | join(", ")' 2>/dev/null)
    RATED=$(echo "$RESPONSE" | jq -r '.total_podcasts_rated // 0' 2>/dev/null)
    AVG=$(echo "$RESPONSE" | jq -r '.average_rating // 0' 2>/dev/null)
    
    echo -e "${GREEN}✅ Interesses:${NC} ${INTERESTS:-Nenhum ainda}"
    echo -e "${RED}🚫 Bloqueados:${NC} ${BLOCKED:-Nenhum}"
    echo -e "${CYAN}⭐ Fontes favoritas:${NC} ${SOURCES:-Nenhuma}"
    echo ""
    echo -e "📻 Podcasts avaliados: ${BOLD}$RATED${NC}"
    if [ "$RATED" != "0" ] && [ "$RATED" != "null" ]; then
        echo -e "⭐ Média: ${BOLD}$AVG/5${NC}"
    fi
}

# Ver notícias do último podcast
show_news() {
    check_connection
    echo -e "${CYAN}📰 Notícias do último podcast:${NC}"
    echo ""
    
    RESPONSE=$(curl -s "$API_URL/api/podcast/last/$USER_ID")
    MESSAGE=$(echo "$RESPONSE" | jq -r '.message // ""' 2>/dev/null)
    
    if [ ! -z "$MESSAGE" ] && [ "$MESSAGE" != "null" ]; then
        echo -e "${YELLOW}$MESSAGE${NC}"
        echo ""
        echo -e "${CYAN}💡 Dica:${NC} Gere um novo podcast com ${BOLD}./quick-podcast.sh${NC}"
        echo "   As notícias serão salvas automaticamente para feedback."
        return
    fi
    
    NEWS_COUNT=$(echo "$RESPONSE" | jq -r '.news | length' 2>/dev/null)
    if [ "$NEWS_COUNT" == "0" ] || [ "$NEWS_COUNT" == "null" ]; then
        echo -e "${YELLOW}Nenhuma notícia encontrada${NC}"
        echo ""
        echo -e "${CYAN}💡 Dica:${NC} Gere um novo podcast com ${BOLD}./quick-podcast.sh${NC}"
        return
    fi
    
    PODCAST_ID=$(echo "$RESPONSE" | jq -r '.podcast_id // ""' 2>/dev/null)
    CREATED=$(echo "$RESPONSE" | jq -r '.created_at // ""' 2>/dev/null | cut -d'T' -f1)
    
    if [ ! -z "$PODCAST_ID" ] && [ "$PODCAST_ID" != "null" ]; then
        echo -e "${CYAN}Podcast:${NC} $PODCAST_ID (${CREATED})"
        echo ""
    fi
    
    echo "$RESPONSE" | jq -r '.news[] | "  \(.index). [\(.source)] \(.title)"' 2>/dev/null
    echo ""
    echo -e "${CYAN}Use os números para dar feedback:${NC}"
    echo "  $0 rate 4 \"1,3\" \"2\"  (gostou 1 e 3, não gostou 2)"
}

# Adicionar interesse
add_interest() {
    check_connection
    TOPIC="$1"
    
    if [ -z "$TOPIC" ]; then
        echo -e "${RED}[✗]${NC} Especifique o tópico"
        echo "Ex: $0 add python"
        exit 1
    fi
    
    RESPONSE=$(curl -s -X POST "$API_URL/api/interests/add" \
        -H "Content-Type: application/json" \
        -d "{\"user_id\": \"$USER_ID\", \"topic\": \"$TOPIC\"}")
    
    MESSAGE=$(echo "$RESPONSE" | jq -r '.message // "Erro"' 2>/dev/null)
    echo -e "${GREEN}[✓]${NC} $MESSAGE"
}

# Bloquear tópico
block_topic() {
    check_connection
    TOPIC="$1"
    
    if [ -z "$TOPIC" ]; then
        echo -e "${RED}[✗]${NC} Especifique o tópico"
        echo "Ex: $0 block política"
        exit 1
    fi
    
    RESPONSE=$(curl -s -X POST "$API_URL/api/interests/block" \
        -H "Content-Type: application/json" \
        -d "{\"user_id\": \"$USER_ID\", \"topic\": \"$TOPIC\"}")
    
    MESSAGE=$(echo "$RESPONSE" | jq -r '.message // "Erro"' 2>/dev/null)
    echo -e "${GREEN}[✓]${NC} $MESSAGE"
}

# Avaliar podcast
rate_podcast() {
    check_connection
    RATING="$1"
    LIKED="$2"
    DISLIKED="$3"
    
    if [ -z "$RATING" ]; then
        echo -e "${RED}[✗]${NC} Especifique a nota (1-5)"
        echo "Ex: $0 rate 4"
        exit 1
    fi
    
    if [ "$RATING" -lt 1 ] || [ "$RATING" -gt 5 ] 2>/dev/null; then
        echo -e "${RED}[✗]${NC} Nota deve ser entre 1 e 5"
        exit 1
    fi
    
    # Converter listas para JSON
    LIKED_JSON="[]"
    DISLIKED_JSON="[]"
    
    if [ ! -z "$LIKED" ]; then
        LIKED_JSON=$(echo "$LIKED" | tr ',' '\n' | jq -R 'tonumber' | jq -s '.')
    fi
    
    if [ ! -z "$DISLIKED" ]; then
        DISLIKED_JSON=$(echo "$DISLIKED" | tr ',' '\n' | jq -R 'tonumber' | jq -s '.')
    fi
    
    # Buscar último podcast_id
    LAST_PODCAST=$(curl -s "$API_URL/api/podcast/last/$USER_ID")
    PODCAST_ID=$(echo "$LAST_PODCAST" | jq -r '.podcast_id // "unknown"' 2>/dev/null)
    
    RESPONSE=$(curl -s -X POST "$API_URL/api/podcast/rate" \
        -H "Content-Type: application/json" \
        -d "{
            \"user_id\": \"$USER_ID\",
            \"podcast_id\": \"$PODCAST_ID\",
            \"rating\": $RATING,
            \"liked_news\": $LIKED_JSON,
            \"disliked_news\": $DISLIKED_JSON
        }")
    
    echo ""
    echo "$RESPONSE" | jq -r '.messages[]' 2>/dev/null | while read msg; do
        echo -e "${GREEN}[✓]${NC} $msg"
    done
    
    INTERESTS=$(echo "$RESPONSE" | jq -r '.current_interests | join(", ")' 2>/dev/null)
    if [ ! -z "$INTERESTS" ] && [ "$INTERESTS" != "null" ]; then
        echo ""
        echo -e "${CYAN}Seus interesses atuais:${NC} $INTERESTS"
    fi
}

# Main
case "${1:-help}" in
    rate)
        rate_podcast "$2" "$3" "$4"
        ;;
    add)
        add_interest "$2"
        ;;
    block)
        block_topic "$2"
        ;;
    show)
        show_preferences
        ;;
    news)
        show_news
        ;;
    status|debug)
        # Diagnóstico dos serviços
        echo -e "${CYAN}🔍 Verificando serviços...${NC}"
        echo ""
        
        # Memory service
        if curl -sf "$API_URL/health" > /dev/null 2>&1; then
            HEALTH=$(curl -s "$API_URL/health")
            CHROMADB=$(echo "$HEALTH" | jq -r '.chromadb_available' 2>/dev/null)
            echo -e "${GREEN}[✓]${NC} Memory Service: OK"
            if [ "$CHROMADB" == "true" ]; then
                echo -e "${GREEN}[✓]${NC} ChromaDB: Conectado"
            else
                echo -e "${YELLOW}[!]${NC} ChromaDB: Indisponível"
            fi
        else
            echo -e "${RED}[✗]${NC} Memory Service: Não disponível"
        fi
        
        # Redis (via preferências)
        PREFS=$(curl -s "$API_URL/api/interests/$USER_ID" 2>/dev/null)
        if [ ! -z "$PREFS" ]; then
            echo -e "${GREEN}[✓]${NC} Redis Cache: OK"
        else
            echo -e "${YELLOW}[!]${NC} Redis Cache: Possível problema"
        fi
        
        # Histórico
        HIST=$(curl -s "$API_URL/api/podcast/last/$USER_ID" 2>/dev/null)
        NEWS_COUNT=$(echo "$HIST" | jq -r '.news | length' 2>/dev/null)
        if [ ! -z "$NEWS_COUNT" ] && [ "$NEWS_COUNT" != "0" ] && [ "$NEWS_COUNT" != "null" ]; then
            echo -e "${GREEN}[✓]${NC} Histórico de podcast: $NEWS_COUNT notícias"
        else
            echo -e "${YELLOW}[!]${NC} Histórico de podcast: Nenhum (use: $0 sync)"
        fi
        
        echo ""
        echo -e "${CYAN}Dica:${NC} Se não há histórico, sincronize com:"
        echo "  $0 sync"
        ;;
    sync)
        # Sincronizar histórico buscando notícias atuais
        check_connection
        echo -e "${CYAN}🔄 Sincronizando histórico...${NC}"
        
        # Buscar notícias do news-service
        NEWS_RESPONSE=$(curl -s -X POST "http://localhost:8002/api/news/fetch" \
            -H "Content-Type: application/json" \
            -d '{"language": "pt-BR", "limit": 10}')
        
        if [ $? -ne 0 ] || [ -z "$NEWS_RESPONSE" ]; then
            echo -e "${RED}[✗]${NC} Falha ao buscar notícias"
            exit 1
        fi
        
        # Extrair lista de notícias
        NEWS=$(echo "$NEWS_RESPONSE" | jq -c '.news // []' 2>/dev/null)
        NEWS_COUNT=$(echo "$NEWS" | jq 'length' 2>/dev/null)
        
        if [ "$NEWS_COUNT" == "0" ] || [ "$NEWS_COUNT" == "null" ]; then
            echo -e "${YELLOW}[!]${NC} Nenhuma notícia disponível"
            exit 1
        fi
        
        # Gerar podcast_id baseado na data/hora
        PODCAST_ID="podcast_$(date +%Y%m%d_%H%M%S)"
        
        # Salvar no memory-service
        SAVE_RESPONSE=$(curl -s -X POST "$API_URL/api/podcast/save-news" \
            -H "Content-Type: application/json" \
            -d "{\"podcast_id\": \"$PODCAST_ID\", \"user_id\": \"$USER_ID\", \"news\": $NEWS}")
        
        STATUS=$(echo "$SAVE_RESPONSE" | jq -r '.status // "error"' 2>/dev/null)
        
        if [ "$STATUS" == "saved" ]; then
            echo -e "${GREEN}[✓]${NC} $NEWS_COUNT notícias sincronizadas!"
            echo ""
            show_news
        else
            echo -e "${RED}[✗]${NC} Erro ao salvar: $SAVE_RESPONSE"
        fi
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}[✗]${NC} Comando desconhecido: $1"
        show_help
        exit 1
        ;;
esac
