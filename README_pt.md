![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-DeepAgents-4B8BBE)
![CI](https://github.com/<SEU_USER>/<SEU_REPO>/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)

# Remote AI Engineer Scout

<img width="608" height="605" alt="image" src="https://github.com/user-attachments/assets/3c2cd325-c458-4cf1-a49c-92be0fb34fd5" />

> Construído sobre [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) e adaptado para mapear vagas remotas de AI Engineer em tempo real.  
> Idiomas: [English](README.md) · Português (este arquivo)

## Visão Geral

Este repositório traz um agente autônomo “deep” desenvolvido com **DeepAgents + LangChain**, utilizando por padrão o modelo **Google Gemini (`gemini:gemini-4-argon`)** através de um roteador extensível de LLMs, subagentes especializados e a API do **Tavily** para buscas na web em tempo real. Cada execução mapeia vagas remotas de Engenharia de IA, valida critérios de elegibilidade para o Brasil/LATAM, cruza requisitos técnicos, salários em dólar, regimes tributários (PJ) e fusos horários, gerando um dossiê executivo em Markdown.

Principais destaques:
- **Roteador Multi-LLM**: Alterne facilmente entre Google Gemini (`gemini:gemini-4-argon`), OpenAI (`gpt-4o-mini`) e ZhipuAI (`glm-4`) via variável de ambiente `LLM_MODEL`.
- **Tabela Resumo Executiva**: Cada relatório inicia com um painel rápido contendo as vagas mais recentes ordenadas de forma crescente por dias em aberto.
- **Coordenação Multi-Agente**: O supervisor coordena subagentes de **pesquisa** e **crítica** para garantir profundidade técnica e qualidade editorial.
- **Notificação Automática via Telegram**: Envia o resumo e o arquivo `.md` completo diretamente para seu chat do Telegram com alertas de falha.
- **Execução Agendada na Nuvem**: Roda automaticamente segundas, quartas e sextas às 08:00 BRT pelo GitHub Actions sem precisar manter o PC ligado.

## Arquitetura em Alto Nível

```
Usuário / GitHub Actions → research_agent.py
                                 ├─ llm_router.py (Gemini 4 Argon, OpenAI, ZhipuAI)
                                 ├─ create_deep_agent(...)
                                 │     ├─ Subagente “research-agent” (usa Tavily)
                                 │     └─ Subagente “critique-agent”
                                 ├─ Ferramentas: internet_search, filesystem middleware
                                 ├─ Saídas: final_report.md + question.txt
                                 └─ Entrega: send_report_telegram.py (Mensagem + Anexo .md)
```

## Pré-requisitos

- Python 3.10+
- Dependências listadas em `pyproject.toml` / `requirements.txt`
- Variáveis de ambiente configuradas no arquivo `.env` (duplique a partir de `.env.example`):
  - `GEMINI_API_KEY` (Obrigatória para o modelo padrão `gemini:gemini-4-argon`)
  - `TAVILY_API_KEY` (Obrigatória para busca web)
  - `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` (Obrigatórias para entrega e alertas no Telegram)
  - `OPENAI_API_KEY` (Opcional, apenas se for usar modelos da OpenAI)
  - `ZHIPUAI_API_KEY` (Opcional, apenas se for usar modelos da ZhipuAI)
  - `LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_PROJECT` (Opcionais, para tracing no LangSmith)

### Configuração do Arquivo de Ambiente

Copie o arquivo de exemplo para iniciar o seu `.env`:

```bash
cp .env.example .env
```

| Variável | Obrigatória | Exemplo | Uso |
|---|---|---|---|
| `LLM_MODEL` | Não | `gemini:gemini-4-argon` | Provedor e modelo alvo |
| `GEMINI_API_KEY` | Sim (p/ padrão) | `AQ...` | Chave da Google AI Studio |
| `TAVILY_API_KEY` | Sim | `tvly-...` | Ferramenta de busca Tavily |
| `TELEGRAM_BOT_TOKEN` | Sim | `123456:ABC...` | Token do bot via @BotFather |
| `TELEGRAM_CHAT_ID` | Sim | `809564944` | ID numérico do seu chat/canal |
| `OPENAI_API_KEY` | Opcional | `sk-...` | Chave da OpenAI (se usar GPT) |
| `ZHIPUAI_API_KEY` | Opcional | `435...` | Chave ZhipuAI (se usar GLM) |

## Instalação

Utilizando `uv` (recomendado):

```bash
uv sync --frozen
```

Ou utilizando `venv` + `pip` padrão:

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

Fluxo de execução:
1. Lê `question.txt` (ou o prompt padrão voltado a profissionais do Brasil).
2. Dispara o agente profundo com Gemini 4 Argon, consultando a web em tempo real via Tavily.
3. O subagente de crítica audita a completude do relatório e a ordem crescente da tabela resumo.
4. Grava `final_report.md` e envia automaticamente a notificação e o anexo para o seu Telegram.

## Estrutura do Repositório

```
.
├─ research_agent.py            # Orquestração do agente principal e subagentes
├─ llm_router.py                # Roteador multi-provedor (Gemini, OpenAI, ZhipuAI)
├─ send_report_telegram.py      # Módulo de envio de relatórios via Telegram Bot
├─ question.txt                 # Prompt base utilizado na pesquisa
├─ final_report.md              # Último relatório gerado
├─ reports/                     # Histórico versionado de relatórios diários
├─ .env.example                 # Modelo base para variáveis de ambiente
├─ .github/workflows/
│  └─ daily-report.yml          # Pipeline de automação do GitHub Actions
├─ pyproject.toml / uv.lock     # Gerenciamento de dependências
├─ README.md                    # Documentação em inglês
└─ README_pt.md                 # Documentação em português
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

## Automação e Entrega via Telegram

> ⚠️ **AVISO DE SEGURANÇA**: Este é um repositório **público**. Nunca commite chaves de API nem o seu arquivo `.env` no código!
> Todas as chaves devem ser armazenadas em [GitHub Secrets](https://docs.github.com/pt/actions/security-guides/using-secrets-in-github-actions).

O repositório inclui um workflow do GitHub Actions (`.github/workflows/daily-report.yml`) que automaticamente:

1. **Executa às segundas, quartas e sextas às 08:00 BRT (11:00 UTC)**
2. **Roda o agente de pesquisa** com o Gemini 4 Argon para mapear vagas verificadas
3. **Valida o relatório** através do subagente de crítica
4. **Salva relatórios com timestamp** no diretório `reports/`
5. **Envia a notificação diretamente para o seu Telegram** (resumo em texto + anexo `.md` completo)

### Instruções de Configuração

#### 1. Secrets Necessários no GitHub

Configure estes secrets nas configurações do repositório (`Settings > Secrets and variables > Actions`):

| Secret | Obrigatório | Descrição |
|---|---|---|
| `GEMINI_API_KEY` | Sim (p/ padrão) | Chave da Google AI Studio |
| `TAVILY_API_KEY` | Sim | Chave API do Tavily para busca web |
| `TELEGRAM_BOT_TOKEN` | Sim | Token do bot via [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | Sim | ID do chat ou canal para recebimento |
| `LLM_MODEL` | Opcional | Identificador do modelo (padrão: `gemini:gemini-4-argon`) |
| `OPENAI_API_KEY` | Opcional | Necessário se for rodar modelos da OpenAI |
| `ZHIPUAI_API_KEY` | Opcional | Necessário se for rodar modelos da ZhipuAI |
| `LANGCHAIN_API_KEY` | Opcional | Para rastreamento LangSmith |
| `LANGCHAIN_TRACING_V2` | Opcional | Defina como `true` para ativar rastreamento |
| `LANGCHAIN_PROJECT` | Opcional | Nome do projeto no LangSmith |

#### 2. Configuração do Bot do Telegram

1. Abra o Telegram e inicie uma conversa com [@BotFather](https://t.me/BotFather) para criar seu bot (`/newbot`).
2. Copie o token HTTP gerado e cadastre como `TELEGRAM_BOT_TOKEN`.
3. Obtenha seu Chat ID enviando uma mensagem para [@userinfobot](https://t.me/userinfobot) ou acessando `https://api.telegram.org/bot<TOKEN>/getUpdates`.
4. Cadastre o número retornado como `TELEGRAM_CHAT_ID`.

#### 3. Execução Manual

Você pode executar o workflow manualmente a qualquer momento:
- Vá para **Actions > Daily AI Engineer Scout Report** no seu repositório GitHub
- Clique em **Run workflow**

### Formato de Entrega no Telegram

O envio para o Telegram contém:
- **Tabela Resumo Executiva** listando as oportunidades mais recentes ordenadas por idade do post.
- **Resumo formatado em texto** com destaques de mercado, faixas salariais e stack técnica.
- **Arquivo anexo em Markdown (`final_report.md`)** com o dossiê completo e todas as fontes citadas.

## Segurança e Proteção de Chaves

Como este é um **repositório público**, siga estas regras estritas:

### ✅ SEGURO - Use GitHub Secrets
Chaves de API são armazenadas criptografadas no GitHub e expostas apenas aos Actions em tempo de execução:

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}  # ✅ Seguro
```

### ❌ NUNCA FAÇA ISSO
```python
# Hardcoding de chaves no código
openai.api_key = "sk-..."  # ❌ NUNCA!

# Commitar arquivos .env
OPENAI_API_KEY=sk-...  # ❌ NUNCA commite .env!
```

### Protegido pelo .gitignore
Os seguintes padrões estão bloqueados de serem commitados:
- `.env`, `.envrc`, `.env*.local`
- `*.pem`, `*.key`
- `secrets/`, `secrets.*`
- `config.local.json`, `credentials.json`

### Se Você Expor uma Chave Acidentalmente
1. **Revogue imediatamente** no painel do provedor:
   - [OpenAI](https://platform.openai.com/api-keys)
   - [Anthropic](https://console.anthropic.com/settings/keys)
   - [Tavily](https://app.tavily.com/home)
2. Gere uma nova chave
3. Atualize o GitHub Secret
4. Considere a chave antiga comprometida (mesmo removida do git, está no histórico)

## Roadmap

- [x] Persistir relatórios diários em `reports/`.
- [x] Automatizar execução diária + envio por email
- Adicionar testes de regressão para os middlewares customizados.
- Adicionar roteamento de LLM para melhor ROI

## Créditos

- Baseado em [DeepAgents](https://github.com/langchain-ai/deepagents) e sua arquitetura de agentes profundos.
- Inspirado por ferramentas como Claude Code, Anthropic Deep Research e Manus.
