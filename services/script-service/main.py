"""
Script Service - Microserviço para geração de roteiros de podcast
Integra com LLM Service para gerar conteúdo
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
from datetime import datetime
import logging
from locale import setlocale, LC_ALL

# Adicionar shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from shared.utils import get_logger, ServiceClient, cache
from shared.config import SERVICE_URLS
from shared.models import AgentType

# ==================== SETUP ====================
app = FastAPI(
    title="JARVIS Script Service",
    description="Serviço de geração de roteiros de podcast",
    version="1.0.0"
)

logger = get_logger(__name__)
llm_client = ServiceClient(SERVICE_URLS["llm_service"])


# ==================== MODELS ====================
class ScriptRequest(BaseModel):
    """Requisição para gerar roteiro"""
    agent_name: str
    agent_type: str
    news: List[dict]
    memory_context: str = ""
    language: str = "pt-BR"
    podcast_duration_minutes: int = 8


class ScriptResponse(BaseModel):
    """Resposta com roteiro gerado"""
    script: str
    word_count: int
    estimated_duration_seconds: float
    agent_name: str
    language: str


# ==================== HEALTH CHECK ====================
@app.get("/health")
async def health_check():
    """Verifica saúde do serviço"""
    return {
        "status": "healthy",
        "service": "script-service",
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================== HELPER FUNCTIONS ====================
def get_current_date_info(language: str = "pt-BR") -> tuple:
    """Retorna data e dia da semana em formato apropriado"""
    from datetime import datetime
    
    now = datetime.now()
    
    if language == "pt-BR":
        # Configurar locale para português
        try:
            setlocale(LC_ALL, 'pt_BR.UTF-8')
        except:
            pass
        
        weekday_names = [
            "segunda-feira", "terça-feira", "quarta-feira",
            "quinta-feira", "sexta-feira", "sábado", "domingo"
        ]
        
        day_name = weekday_names[now.weekday()]
        date_str = now.strftime("%d/%m/%Y")
        return day_name, date_str
    else:
        weekday_names = [
            "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"
        ]
        day_name = weekday_names[now.weekday()]
        date_str = now.strftime("%m/%d/%Y")
        return day_name, date_str


def format_news_for_prompt(news_list: List[dict]) -> str:
    """Formata notícias para inclusão no prompt"""
    if not news_list:
        return "Nenhuma notícia disponível."
    
    formatted = "NOTÍCIAS DO DIA:\n\n"
    for i, news in enumerate(news_list, 1):
        title = news.get("title", "")
        summary = news.get("summary", "")
        source = news.get("source", "")
        
        formatted += f"{i}. {title}\n"
        formatted += f"   Resumo: {summary}\n"
        formatted += f"   Fonte: {source}\n\n"
    
    return formatted


def get_agent_prompt(agent_type: str, agent_name: str, day_name: str, date_str: str, 
                     duration: int, news_formatted: str, memory_context: str = "") -> str:
    """Retorna o prompt apropriado para cada tipo de agente"""
    
    memory_section = ""
    if memory_context:
        memory_section = f"\n\nCONTEXTO DE MEMÓRIA ANTERIOR (use para referências):\n{memory_context}\n"
    
    # Base de personalidade
    personality = f"""Você é {agent_name}, uma IA com personalidade própria.
Você NÃO é um robô lendo notícias - você é um COMENTARISTA e ANALISTA.

REGRAS IMPORTANTES:
- NÃO repita os títulos das notícias literalmente
- NÃO leia as notícias como se fossem um teleprompter
- ANALISE, COMENTE e DÊ SUA OPINIÃO sobre cada assunto
- Faça conexões entre os assuntos
- Use exemplos do dia-a-dia para explicar conceitos técnicos
- Seja crítico quando necessário
- Adicione contexto histórico ou comparações
- Faça perguntas retóricas para engajar o ouvinte
- Use humor quando apropriado

Data: {date_str} ({day_name})
Duração alvo: ~{duration} minutos
"""

    prompts = {
        "podcast_daily": f"""{personality}

TIPO: Podcast Diário de Tecnologia

{news_formatted}{memory_section}

Crie um podcast CONVERSACIONAL e OPINATIVO que:

1. ABERTURA (20 segundos):
   - Cumprimente de forma natural e pessoal
   - Mencione algo interessante sobre o dia (ex: "sexta-feira, dia de lançamentos!")
   - Gere expectativa sobre o conteúdo

2. DESENVOLVIMENTO (cada notícia - 1.5 a 2 min):
   - Introduza o tema COM SUA PERSPECTIVA, não o título
   - Explique POR QUE isso importa para o ouvinte
   - Adicione CONTEXTO (o que levou a isso? o que vem depois?)
   - Dê sua OPINIÃO ou ANÁLISE crítica
   - Faça comparações com situações conhecidas
   - Use frases como: "O que me chamou atenção foi...", "Isso me lembra de...", "Na minha visão..."

3. CONEXÕES:
   - Relacione as notícias entre si quando possível
   - Identifique tendências maiores

4. ENCERRAMENTO (30 segundos):
   - Resuma o "mood" do dia em tecnologia
   - Deixe uma reflexão ou pergunta para o ouvinte pensar
   - Despedida pessoal

FORMATO: Texto corrido, sem marcações, pronto para ser lido em voz alta.
""",

        "market_analysis": f"""{personality}

TIPO: Análise de Mercado e Investimentos em Tech

{news_formatted}{memory_section}

Crie uma ANÁLISE DE MERCADO profunda que:

1. ABERTURA (15 segundos):
   - Cumprimento profissional
   - "Vamos analisar o que movimentou o mercado de tecnologia hoje"

2. ANÁLISE DE CADA NOTÍCIA:
   - Impacto no mercado e em ações
   - Quais empresas são afetadas (positiva ou negativamente)
   - Oportunidades ou riscos para investidores
   - Comparação com movimentos anteriores do setor
   - Previsões de curto e médio prazo

3. VISÃO MACRO:
   - Como essas notícias se conectam com tendências maiores
   - O que isso significa para o setor de tecnologia
   - Sinais de alta ou baixa no mercado

4. CONCLUSÃO:
   - Resumo dos pontos-chave para investidores
   - O que observar nos próximos dias

Tom: Analítico, informativo, sem sensacionalismo.
FORMATO: Texto corrido, sem marcações.
""",

        "content_generator": f"""{personality}

TIPO: Conteúdo Criativo e Educativo

{news_formatted}{memory_section}

Crie conteúdo EDUCATIVO e ENGAJANTE que:

1. GANCHO INICIAL:
   - Comece com uma pergunta intrigante ou fato surpreendente
   - Capture a atenção imediatamente

2. EXPLICAÇÃO PROFUNDA:
   - Pegue os temas das notícias e EXPLIQUE os conceitos por trás
   - Use analogias do dia-a-dia
   - "Pense nisso como...", "É como se..."
   - Explique termos técnicos de forma acessível

3. EXEMPLOS PRÁTICOS:
   - Como isso afeta a vida das pessoas?
   - Demonstrações conceituais
   - Cases de uso real

4. APRENDIZADO:
   - O que o ouvinte pode aprender com isso?
   - Dicas práticas relacionadas
   - Recursos para aprofundamento

5. FECHAMENTO:
   - Resumo do que foi aprendido
   - Incentivo para explorar mais

Tom: Professor amigável, curioso, entusiasmado.
FORMATO: Texto corrido, sem marcações.
""",

        "email_summary": f"""{personality}

TIPO: Resumo Executivo Rápido

{news_formatted}{memory_section}

Crie um BRIEFING EXECUTIVO conciso:

1. HEADLINE do dia (uma frase)

2. TOP 3 NOTÍCIAS em formato bullet:
   - Fato + impacto + ação recomendada
   
3. MÉTRICAS/DADOS relevantes mencionados

4. O QUE OBSERVAR essa semana

5. CONCLUSÃO em uma frase

Tom: Direto, executivo, sem floreios.
Duração: Máximo 3 minutos de leitura.
FORMATO: Texto corrido, sem marcações.
""",

        "code_assistant": f"""{personality}

TIPO: Dev Talk - Podcast para Desenvolvedores

{news_formatted}{memory_section}

Crie um podcast TÉCNICO para desenvolvedores:

1. INTRO:
   - "E aí, devs! Bora ver o que rolou no mundo do código?"

2. PARA CADA NOTÍCIA TÉCNICA:
   - Implicações para desenvolvedores
   - Mudanças em workflows ou ferramentas
   - Código ou conceitos mencionados
   - "Se você usa X, precisa saber que..."
   - Links mentais com outras tecnologias

3. DICAS PRÁTICAS:
   - O que isso muda no dia-a-dia de dev
   - Ferramentas ou bibliotecas relacionadas
   - Padrões ou anti-padrões

4. HOT TAKES:
   - Sua opinião sobre a direção da tecnologia
   - Previsões técnicas

5. FECHAMENTO:
   - "Bora codar!"

Tom: Dev falando com devs, técnico mas acessível, com humor de programador.
FORMATO: Texto corrido, sem marcações.
"""
    }
    
    # Retorna o prompt do tipo ou o padrão (podcast_daily)
    return prompts.get(agent_type, prompts["podcast_daily"])


# ==================== ENDPOINTS ====================
@app.post("/api/script/generate")
async def generate_script(request: ScriptRequest) -> ScriptResponse:
    """
    Gera roteiro de podcast baseado em notícias
    """
    try:
        logger.info(f"📝 Gerando roteiro para: {request.agent_name} (tipo: {request.agent_type})")
        
        # Verificar cache
        cache_key = f"script:{request.agent_name}:{request.agent_type}:{hash(str(request.news))}"
        cached = cache.get(cache_key)
        if cached:
            logger.info("📦 Roteiro retornado do cache")
            return ScriptResponse(**cached)
        
        # Obter data e dia
        day_name, date_str = get_current_date_info(request.language)
        
        # Formatar notícias
        news_formatted = format_news_for_prompt(request.news)
        
        # Obter prompt específico para o tipo de agente
        prompt = get_agent_prompt(
            agent_type=request.agent_type,
            agent_name=request.agent_name,
            day_name=day_name,
            date_str=date_str,
            duration=request.podcast_duration_minutes,
            news_formatted=news_formatted,
            memory_context=request.memory_context
        )
        
        logger.info(f"🎯 Usando prompt para tipo: {request.agent_type}")

        # Chamar LLM Service
        llm_response = await llm_client.post(
            "/api/llm/generate",
            data={
                "prompt": prompt,
                "context": f"Agent: {request.agent_name}, Type: {request.agent_type}",
                "temperature": 0.85,
                "max_tokens": 4000
            }
        )
        
        if not llm_response:
            raise Exception("LLM Service indisponível")
        
        script = llm_response.get("text", "")
        
        if not script:
            raise Exception("LLM não retornou um script válido")
        
        # Calcular estatísticas
        word_count = len(script.split())
        # Estimativa: ~130 palavras por minuto em português
        estimated_duration = (word_count / 130) * 60  # em segundos
        
        logger.info(f"✅ Roteiro gerado ({word_count} palavras, ~{estimated_duration/60:.1f} minutos)")
        
        result = {
            "script": script,
            "word_count": word_count,
            "estimated_duration_seconds": estimated_duration,
            "agent_name": request.agent_name,
            "language": request.language
        }
        
        # Cachear por 24 horas
        cache.set(cache_key, result, expire_seconds=86400)
        
        return ScriptResponse(**result)
    
    except Exception as e:
        logger.error(f"❌ Erro ao gerar roteiro: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/script/preview")
async def preview_script(agent_name: str, language: str = "pt-BR"):
    """
    Retorna um exemplo de roteiro gerado
    Útil para debug e visualização
    """
    day_name, date_str = get_current_date_info(language)
    
    example = f"""
E aí, pessoal! {day_name.capitalize()}, {date_str}.

Aqui é o {agent_name}, seu assistente de IA preferido! Hoje temos notícias incríveis do mundo da tecnologia.

Primeiro assunto: Uma descoberta revolucionária em inteligência artificial que está mudando o mundo.
Este avanço promete transformar como trabalhamos e nos relacionamos com a tecnologia.

Segundo assunto: Novos desenvolvimentos em hardware que prometem melhorar a performance dos seus dispositivos.
As últimas inovações estão tornando nossos computadores mais rápidos e eficientes.

Terceiro assunto: Atualizações importantes em segurança cibernética que você precisa saber.
Especialistas alertam para novas ameaças e as melhores práticas para se proteger.

Nesses tempos incríveis de transformação tecnológica, uma coisa é certa:
o futuro está sendo construído agora, e você pode fazer parte dessa revolução!

Obrigado por ouvir o podcast de hoje. Nos vemos amanhã!
"""
    
    return {
        "preview": example,
        "word_count": len(example.split()),
        "estimated_duration_seconds": (len(example.split()) / 130) * 60
    }


# ==================== MAIN ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info"
    )
