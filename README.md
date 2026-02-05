# Personal Daily Agent

Este projeto é um **agente pessoal inteligente** pensado para funcionar como um "bom dia automático": ele se atualiza com notícias relevantes, aprende gradualmente sobre seus interesses e organiza informações úteis para o seu dia a dia.

A ideia central não é apenas um bot de consulta, mas um **sistema de agentes** que compartilham memória e contexto, permitindo expandir funcionalidades no futuro (planilhas, relatórios, análises, automações, etc.).

---

## Visão Geral

O agente principal:

* Busca informações atualizadas na internet
* Resume notícias importantes
* Prioriza temas de interesse do usuário
* Mantém memória persistente
* Serve como base para outros agentes especializados

Arquiteturalmente, o projeto é modular: você pode adicionar novos agentes sem reescrever o núcleo.

---

## Funcionalidades Atuais

* 🔎 **Busca na internet** para notícias e informações recentes
* 🧠 **Memória persistente** (interesses, preferências, histórico)
* 📰 **Resumo diário de notícias**
* 🧩 **Arquitetura extensível por agentes**
* 🖥️ **Execução local** (sem dependência de TTS)

---

## Funcionalidades Planejadas

* 📊 Agente para criação e análise de planilhas
* 📅 Agente de organização pessoal (tarefas, agenda)
* 💻 Agente técnico (programação, DevOps, infraestrutura)
* 🧠 Aprendizado contínuo baseado no uso
* 🔗 Integração entre agentes via memória compartilhada

---

## Arquitetura do Sistema

```
core/
 ├─ agent.py           # Lógica base do agente
 ├─ memory.py          # Memória persistente
 ├─ context.py         # Contexto compartilhado
 ├─ web_search.py      # Busca de informações online
 └─ summarizer.py      # Resumo e filtragem de conteúdo

agents/
 ├─ daily_agent.py     # Agente de notícias e atualização diária
 ├─ planner_agent.py   # (futuro) Agente de planilhas e organização

storage/
 └─ memory.json        # Memória persistente local

main.py                # Ponto de entrada do sistema
```

---

## Memória Compartilhada

A memória é um componente central do projeto. Ela armazena:

* Interesses do usuário
* Preferências de conteúdo
* Histórico de interações
* Dados relevantes aprendidos ao longo do tempo

Todos os agentes acessam essa memória, permitindo comportamento consistente e personalizado.

---

## Exemplo de Uso

```bash
python agent.py
```

Saída esperada:

* Resumo das principais notícias do dia
* Destaque para temas de interesse
* Informações relevantes organizadas

---

## Filosofia do Projeto

Este projeto segue alguns princípios claros:

* **Automação consciente**: o agente ajuda, não distrai
* **Privacidade primeiro**: memória local, controle total
* **Extensibilidade**: novos agentes são cidadãos de primeira classe
* **Clareza**: respostas resumidas, úteis e acionáveis

---

## Próximos Passos Recomendados

1. Refinar o filtro de interesses
2. Criar sistema de prioridade de notícias
3. Adicionar logs e observabilidade
4. Implementar novos agentes especializados

---

## Status do Projeto

🚧 Em desenvolvimento ativo

Este README descreve a base do sistema. O projeto foi pensado para crescer de forma orgânica, conforme novas necessidades surgirem.

---

## Licença

Projeto pessoal. Use, modifique e evolua livremente.
