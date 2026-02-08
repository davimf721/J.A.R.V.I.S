from tools.news_fetcher import fetch_news
from llm.llama import ask_llama
from datetime import datetime
import locale

def generate_podcast_script():
    news = fetch_news()

    # Formatar notícias com fonte
    news_text = "\n".join(
        f"- [{n['source']}] {n['title']}: {n['summary']}" for n in news
    )

    # Obter data e dia da semana atual
    # Definir locale para português
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR')
        except:
            pass  # Usar locale padrão se português não disponível
    
    agora = datetime.now()
    dia_semana = agora.strftime('%A')  # Nome do dia em português
    data_formatada = agora.strftime('%d/%m/%Y')  # DD/MM/YYYY
    
    # Mapeamento de dias da semana em português
    dias_pt = {
        'Monday': 'segunda-feira',
        'Tuesday': 'terça-feira',
        'Wednesday': 'quarta-feira',
        'Thursday': 'quinta-feira',
        'Friday': 'sexta-feira',
        'Saturday': 'sábado',
        'Sunday': 'domingo'
    }
    
    dia_semana_pt = dias_pt.get(agora.strftime('%A'), agora.strftime('%A'))

    prompt = f"""
Você é um locutor de podcast de tecnologia experiente e entusiasmado. 
Crie um roteiro de podcast APENAS COM O TEXTO da fala, sem nenhuma marcação de tempo, horários, seções ou instruções técnicas.

DATA E CONTEXTO:
- Data de hoje: {data_formatada} ({dia_semana_pt})

REQUISITOS IMPORTANTES:
- Apenas o texto que será falado
- SEM marcações de tempo (00:00, 01:30, etc)
- SEM indicações de seções ou capítulos
- SEM marcações técnicas ou notas de produção
- SEM asteriscos ou símbolos especiais
- Texto fluido, conversacional e naturalmente segmentado
- Comprimento: 8-10 minutos de leitura em voz alta
- Tom: Informativo mas descontraído, como falando para um amigo
- Use pausas naturais (quebras de linha) para respiração
- Mencione as fontes das notícias de forma natural

ESTRUTURA SUGERIDA:
1. Uma introdução descontraída mencionando que é {dia_semana_pt} ({data_formatada}) e que é horário de podcast
2. Transição natural para as notícias de forma agrupada por tema
3. Explore as notícias com curiosidade, fazendo conexões entre elas
4. Dê insights pessoais sobre o impacto das tecnologias
5. Destaque as tendências que você identifica
6. Uma conclusão motivadora

NOTÍCIAS PARA COBRIR:
{news_text}

IMPORTANTE: Responda APENAS com o texto do podcast. Nada mais. Seja conversacional e natural, como se estivesse falando com amigos. USE A DATA CORRETA NA INTRODUÇÃO: {dia_semana_pt}, {data_formatada}."""

    return ask_llama(prompt)
