![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-DeepAgents-4B8BBE)
![CI](https://github.com/<SEU_USER>/<SEU_REPO>/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)

# Remote AI Engineer Scout

<img width="608" height="605" alt="image" src="https://github.com/user-attachments/assets/3c2cd325-c458-4cf1-a49c-92be0fb34fd5" />

> Construído sobre [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) e adaptado para mapear vagas remotas de AI Engineer em tempo real.  
> Idiomas: [English](README.md) · Português (este arquivo)

## Visão Geral

Este repositório traz um agente “deep” feito com **DeepAgents + LangChain**, usando o modelo `openai:gpt-4o-mini`, subagentes especializados e **Tavily** para buscas ao vivo. Cada execução coleta vagas remotas de Engenharia de IA, cruza requisitos (skills, senioridade, stack, salários, restrições geográficas) e gera um relatório em Markdown pronto para divulgar.

Principais destaques:
- O agente supervisor coordena subagentes de **pesquisa** e **crítica** para garantir qualidade.
- Middleware de filesystem armazena o relatório (`final_report.md`) e o prompt base (`question.txt`).
- Tracing opcional via LangSmith (`LANGCHAIN_TRACING_V2=true`) cria histórico auditável de consultas, ferramentas e custo.

## Arquitetura em Alto Nível

```
Usuário → research_agent.py
                 ├─ create_deep_agent(...)
                 │     ├─ Subagente “research-agent” (usa Tavily)
                 │     └─ Subagente “critique-agent”
                 ├─ Ferramentas: internet_search, filesystem middleware
                 └─ Saídas: final_report.md + question.txt
```

## Pré-requisitos

- Python 3.10+
- Dependências listadas em `requirements.txt`
- Variáveis de ambiente:
  - `OPENAI_API_KEY`
  - `TAVILY_API_KEY`
  - `LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_PROJECT` (opcionais, apenas para LangSmith)

### Configuração no PowerShell

| Variável             | Obrigatória | Exemplo            | Uso                                    |
|----------------------|-------------|--------------------|----------------------------------------|
| OPENAI_API_KEY       | Sim         | `sk-...`           | Modelo `openai:gpt-4o-mini`            |
| TAVILY_API_KEY       | Sim         | `tvly-...`         | Ferramenta de busca                    |
| LANGCHAIN_API_KEY    | Não         | `ls-...`           | Chave do LangSmith                     |
| LANGCHAIN_TRACING_V2 | Não         | `true`             | Habilita tracing                       |
| LANGCHAIN_PROJECT    | Não         | `remote-ai-scout`  | Projeto dentro do LangSmith            |

Persistindo para novas sessões:

```powershell
setx OPENAI_API_KEY "sk-..."
setx TAVILY_API_KEY "tvly-..."
setx LANGCHAIN_API_KEY "ls-..."
setx LANGCHAIN_TRACING_V2 "true"
setx LANGCHAIN_PROJECT "remote-ai-scout"
```

Para uso apenas na sessão atual, utilize `$env:OPENAI_API_KEY = "..."`.

## Instalação

```bash
python -m venv .venv
.\.venv\Scripts\activate        # Windows (PowerShell)
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
```

## Como Executar

```bash
python research_agent.py
```

Fluxo:
1. Lê `question.txt` (padrão: “Find remote AI Engineer roles hiring now aligned with my profile.”).
2. Dispara o agente profundo, que convoca os subagentes de pesquisa/crítica e usa Tavily para obter vagas atualizadas.
3. Sobrescreve `final_report.md` com o briefing mais recente (adapte o script para salvar `final_report_<YYYYMMDD>.md` caso queira histórico).

## Estrutura do Repositório

```
.
├─ research_agent.py            # Configuração principal do agente
├─ question.txt                 # Prompt base
├─ final_report.md              # Último relatório gerado
├─ libs/
│  ├─ deepagents-cli/...        # Ajustes do middleware de memória
│  └─ deepagents/...            # Filesystem + subagents customizados
├─ requirements.txt
├─ README.md                    # Em inglês
└─ README_pt.md                 # Em português
```

## Personalização

```
Find remote AI Engineer roles hiring now aligned with my profile.

# Scope
- Focus: Senior AI/ML Engineer roles
- Region: Americas (Remote, LATAM-friendly)
- Tech: Python, LangChain, Vector DBs, LLM Ops
- Exclude: Onsite-only, internships
```

- **Prompt & escopo** – ajuste `question.txt` para focar em LATAM, vagas júnior, stacks específicas etc.
- **Busca fresca** – passe `time_range="day"` ao Tavily em `internet_search` para priorizar posts do dia.
- **Histórico de relatórios** – salve cada corrida em `reports/final_report_YYYYMMDD.md`.
- **Novas fontes** – conecte APIs de job boards, Slack, Google Sheets via middleware customizado.
- **Metadados no LangSmith** – use `agent.invoke(..., config={"metadata": {...}})` para etiquetar execuções.

## Problemas Comuns

- `KeyError: 'TAVILY_API_KEY'` – exporte a variável antes de executar.
- `Failed to POST https://api.smith.langchain.com...` – credenciais/projeto do LangSmith ausentes; desligue o tracing se não precisar.
- Avisos `typing.NotRequired` – já substituídos por tipos opcionais padrão nos middlewares customizados.

## Rastreamento e Custos

### LangSmith
1. Exporte `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_API_KEY` e `LANGCHAIN_PROJECT`.
2. Rode `python research_agent.py`; cada execução gera um trace completo com ferramentas, prompts e tokens.
3. No painel do LangSmith, registre:
   - Horário + descrição (adicione `metadata` para rotular automaticamente).
   - `prompt_tokens`, `completion_tokens`, `total_tokens` e custo estimado.
4. Compartilhe screenshots ou use **Export CSV**. Exemplo:

| Execução     | Consulta                               | Prompt Tokens | Completion Tokens | Custo (USD) |
|--------------|----------------------------------------|---------------|-------------------|-------------|
| 2024-06-30 AM | Find remote AI Engineer roles...        | 6.245         | 4.108             | $0,21       |
| 2024-06-30 PM | Senior AI roles LATAM-friendly          | 7.002         | 4.887             | $0,24       |

### Portal da OpenAI / Usage API

- Confira [https://platform.openai.com/usage](https://platform.openai.com/usage) para os números oficiais.
- Capture `result["usage"]` após `agent.invoke(...)` e salve em `reports/usage_logs/YYYYMMDD.json`.
- Publique resumos mensais neste README ou em `docs/usage.md`.

## Resultado Esperado (exemplo)

```
# Remote AI Engineer Opportunities Brief

## Market Snapshot
Mercado remoto segue aquecido, com empresas exigindo ownership de ML fim a fim, experiência com LLMs em produção e alguma sobreposição com fusos das Américas.

## Active Remote Employers
- Tech.co – squads distribuídos com foco em IA.
- Hiring Agents – vagas mid/senior chegando a US$ 282K.
- Indeed – cerca de 1.900 anúncios remotos atualizados diariamente.
- Remote Rocketship – curadoria para engenheiros de IA (incluindo júnior).
- LinkedIn – mais de 74 mil oportunidades remotas em IA.

## Representative Openings
1. Staff AI Engineer – Curai Health (EUA, remoto).
2. Senior AI Engineer – Jitterbit (Índia, remoto).
3. AI Engineer Level IV – Premera (EUA, remoto).
4. AI Developer – BambooWorks (EUA, remoto).

## Required Skills & Stack
Python/Java para serviços em produção, modelagem de dados, deploy/monitoramento de ML, MLOps em AWS/GCP, bancos vetoriais e práticas de ética/bias.

## Compensation & Location Notes
Faixa típica entre US$ 100K–240K; algumas vagas aceitam candidatos globais e outras pedem sobreposição com EUA/Europa.

## Application Strategy
Faça networking no LinkedIn, monitore job boards remotos, personalize o CV por vaga e destaque projetos ou contribuições OSS.

## Sources
1. Tech.co – Remote Jobs
2. Hiring Agents – AI Engineer listings
3. Indeed – Remote AI Engineer jobs
4. Remote Rocketship – Junior AI Engineer feed
5. LinkedIn – Remote AI jobs
```

## Roadmap

- Persistir relatórios diários em `reports/`.
- Adicionar testes de regressão para os middlewares customizados.
- Automatizar execução/publicação diária (ex.: GitHub Actions que dá commit no relatório mais recente).

## Créditos

- Baseado em [DeepAgents](https://github.com/langchain-ai/deepagents) e sua arquitetura de agentes profundos.
- Inspirado por ferramentas como Claude Code, Anthropic Deep Research e Manus.
