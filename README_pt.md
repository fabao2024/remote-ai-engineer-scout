![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-DeepAgents-4B8BBE)
![CI](https://github.com/fabao2024/remote-ai-engineer-scout/actions/workflows/daily-report.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)

# 🧠🤖 Remote AI Engineer Scout

<img width="608" height="605" alt="image" src="https://github.com/user-attachments/assets/3c2cd325-c458-4cf1-a49c-92be0fb34fd5" />

> Construído sobre [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) e adaptado para mapear, validar deterministamente e entregar vagas remotas de Engenharia de IA abertas para profissionais no Brasil/LATAM em tempo real.  
> Idiomas: [English](README.md) · **Português** (este arquivo)

---

## Visão Geral

O **Remote AI Engineer Scout** é um agente autônomo de pesquisa profunda construído com **DeepAgents + LangChain**, operando por padrão com modelos Google Gemini (`gemini:gemini-4-argon` / `gemini:gemini-2.5-flash`) por meio de um roteador multi-provedor extensível, subagentes especializados e a API do **Tavily** para buscas web em tempo real.

A cada execução, o agente descobre vagas remotas abertas para o cargo configurado, valida a elegibilidade geográfica na fonte (priorizando Brasil, LATAM e Worldwide Remote), analisa stacks técnicas, faixas salariais em dólar e regimes contratuais (PJ/CLT), e emite um dossiê executivo em Markdown entregue diretamente no seu Telegram.

### Principais Destaques

- 🎯 **Customização do Cargo Alvo**: Pesquise qualquer posição (ex.: `Applied AI Engineer`, `Agentic AI Engineer`, `Forward Deployed AI Engineer`, `Data Engineer`, `MLOps`) simplesmente alterando `TARGET_ROLE` no `.env`, via linha de comando ou via GitHub Actions.
- 🛡️ **Validador Determinístico de URLs com Detecção por ATS**: Auditor assíncrono (`url_validator.py`) com `httpx` que elimina 404s, detecta vagas encerradas e trata peculiaridades de ATS (como cascas vazias de SPA no Ashby, redirecionamentos para `/oops` no Workable e erros no Greenhouse).
- 🧠 **Memória Persistente e Deduplicação**: Registra as vagas já descobertas em `seen_jobs.json` com normalização de URLs, priorizando oportunidades inéditas e impedindo repetições entre execuções.
- ⚡ **Middleware Resiliente de Estado no LangGraph**: Implementa o `ResilientTodoListMiddleware` em `libs/deepagents/graph.py` com canal redutor de estado (`take_last`) para suportar chamadas concorrentes/paralelas a ferramentas sem colisões de estado no LangGraph.
- 🚫 **Guardrails de Tolerância Zero para Alucinação de Links**: Regras estritas nos prompts do supervisor e do pesquisador garantem que todo link citado no relatório venha exclusivamente de resultados reais de busca de ATS—sem UUIDs fabricados.
- 🔄 **Roteador Multi-LLM**: Alterne facilmente entre Google Gemini (`gemini:gemini-4-argon`, `gemini:gemini-2.5-flash`), OpenAI (`gpt-4o-mini`) e ZhipuAI (`glm-4`), com retry automático (`max_retries=6`).
- 📊 **Tabela Resumo Executiva**: Todo relatório se inicia com um painel rápido ordenado de forma estritamente crescente por dias em aberto (vagas mais recentes primeiro).
- 📱 **Notificação Automática via Telegram**: Envia a prévia da tabela em Markdown e anexa o relatório completo (`final_report.md`) diretamente no chat do seu Telegram.
- ☁️ **Execução em Nuvem via GitHub Actions**: Roda automaticamente segundas, quartas e sextas às 08:00 BRT (11:00 UTC), versionando e sincronizando relatórios e memórias no repositório.

---

## Arquitetura em Alto Nível

```
Usuário / GitHub Actions
        │
        ▼
   research_agent.py
        ├─ llm_router.py (Gemini 4 Argon / 2.5 Flash com fallbacks OpenAI/ZhipuAI)
        ├─ create_deep_agent(...) [libs/deepagents]
        │     ├─ ResilientTodoListMiddleware (Redutor de estado para chamadas paralelas)
        │     ├─ Subagente "research-agent" (Busca Tavily + Regras Anti-Alucinação)
        │     └─ Subagente "critique-agent" (Auditoria editorial + Ordenação da tabela)
        ├─ url_validator.py (Auditor assíncrono HTTP e de elegibilidade por ATS)
        ├─ job_tracker.py (Memória e deduplicação via seen_jobs.json)
        ├─ Saídas: final_report.md + question.txt
        └─ Entrega: send_report_telegram.py (Alerta no Telegram + Anexo .md)
```

---

## Pré-requisitos

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recomendado) ou `pip` + `venv` padrão
- Variáveis de ambiente configuradas no arquivo `.env` (duplique a partir de `.env.example`):
  - `GEMINI_API_KEY` (Obrigatória para os modelos Gemini padrão)
  - `TAVILY_API_KEY` (Obrigatória para buscas em tempo real)
  - `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` (Obrigatórias para entrega e alertas no Telegram)
  - `OPENAI_API_KEY` (Opcional, apenas se for usar modelos da OpenAI)
  - `ZHIPUAI_API_KEY` (Opcional, apenas se for usar modelos da ZhipuAI)
  - `LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2=false`, `LANGCHAIN_PROJECT` (Opcionais, para tracing no LangSmith)

### Configuração do Arquivo de Ambiente

Copie o arquivo de exemplo para iniciar o seu `.env`:

```bash
cp .env.example .env
```

| Variável | Obrigatória | Padrão / Exemplo | Uso |
|---|---|---|---|
| `TARGET_ROLE` | Não | `Applied AI Engineer` | Cargo/posição a ser pesquisada |
| `LLM_MODEL` | Não | `gemini:gemini-4-argon` | Provedor e modelo principal |
| `LLM_FALLBACK_MODELS` | Não | `gemini:gemini-2.5-flash,openai:gpt-4o-mini` | Cadeia de fallback em caso de falha |
| `GEMINI_API_KEY` | Sim (p/ padrão) | `AIzaSy...` | Chave de API da Google AI Studio |
| `TAVILY_API_KEY` | Sim | `tvly-...` | Chave da ferramenta de busca Tavily |
| `TELEGRAM_BOT_TOKEN` | Sim | `123456:ABC...` | Token do bot via [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | Sim | `809564944` | ID numérico do seu usuário ou chat no Telegram |
| `OPENAI_API_KEY` | Opcional | `sk-...` | Chave de API da OpenAI |
| `ZHIPUAI_API_KEY` | Opcional | `435...` | Chave de API da ZhipuAI |

---

## Instalação

Utilizando `uv` (recomendado pela rapidez):

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

---

## Como Executar

Execute o agente localmente:

```bash
uv run python research_agent.py
# ou: python research_agent.py
```

### Ciclo de Execução

1. **Injeção de Cargo e Memória**: Lê `TARGET_ROLE` e injeta a lista de URLs recentes de `seen_jobs.json` no prompt do supervisor para evitar repetições.
2. **Pesquisa Autônoma**: O agente profundo consulta o Tavily buscando vagas publicadas nas últimas 1 a 3 semanas que atendam aos critérios de trabalho remoto a partir do Brasil.
3. **Crítica Editorial**: O subagente de crítica avalia a profundidade técnica, estrutura do texto e ordenação da tabela.
4. **Auditoria Determinística de URLs**: O módulo `url_validator.py` realiza requisições assíncronas para cada link, expurgando 404s, vagas fechadas e cascas vazias de ATS.
5. **Persistência na Memória**: O `job_tracker.py` registra as vagas ativas validadas no `seen_jobs.json`.
6. **Disparo no Telegram**: Envia a tabela executiva e anexa o arquivo `final_report.md` no seu chat.

---

## 🎯 Como Customizar o Cargo Buscado

Você pode pesquisar qualquer cargo simplesmente definindo `TARGET_ROLE` no seu arquivo `.env`:

```env
TARGET_ROLE=Applied AI Engineer
```

### Exemplos de Cargos Suportados
- `TARGET_ROLE=Applied AI Engineer`
- `TARGET_ROLE=Agentic AI Engineer`
- `TARGET_ROLE=Forward Deployed AI Engineer`
- `TARGET_ROLE=Machine Learning Engineer`
- `TARGET_ROLE=Data Engineer`
- `TARGET_ROLE=MLOps Engineer`

### Alterando o Cargo em Execução Única via Terminal

Você pode sobrepor o cargo temporariamente sem precisar editar o `.env`:

```bash
# Windows (PowerShell)
$env:TARGET_ROLE="Agentic AI Engineer"; uv run python research_agent.py

# Linux / macOS
TARGET_ROLE="Agentic AI Engineer" uv run python research_agent.py
```

### Alterando o Cargo no GitHub Actions

Ao disparar manualmente o workflow no GitHub Actions (**Actions** → **Daily AI Engineer Scout Report** → **Run workflow**), informe o cargo desejado no campo **Target job title to search for**.

---

## 🛡️ Validador Determinístico de URLs com Detecção por ATS

Plataformas de recrutamento e ATS (Applicant Tracking Systems) costumam lidar com vagas encerradas de formas singulares que enganam verificações HTTP comuns. O nosso validador aprimorado em `url_validator.py` aplica heurísticas específicas:

- **Ashby (`jobs.ashbyhq.com`)**: Quando uma vaga é excluída, o Ashby responde com **HTTP 200**, mas entrega uma casca de SPA vazia com `<title>Jobs</title>` e sem metatags `og:title`. O validador detecta essa assinatura e descarta a vaga.
- **Workable (`apply.workable.com`)**: Vagas fechadas são redirecionadas para `/oops` ou `?not_found=true`. O validador intercepta esses redirecionamentos e purga a linha da tabela.
- **Greenhouse (`boards.greenhouse.io`)**: Vagas expiradas redirecionam com `?error=true` ou retornam status 404.
- **Lever (`jobs.lever.co`) / Teamtailor / InHire**: Detecta status 404, avisos de vaga inativa no corpo da página e redirecionamentos para a raiz de carreiras.
- **Filtro Geográfico Estrito**: Identifica restrições rígidas para os EUA sem exceção para o Brasil/LATAM e remove a oportunidade da lista.

Você pode rodar o auditor diretamente em qualquer relatório a qualquer momento:

```bash
uv run python url_validator.py
```

---

## ⚡ Middleware de Estado Resiliente no LangGraph

Modelos de linguagem modernos (como o Gemini 4 Argon) frequentemente executam múltiplas chamadas a ferramentas em paralelo no mesmo passo. O middleware padrão `TodoListMiddleware` do LangGraph não definia um redutor para o canal `todos`, gerando o erro:

```
InvalidUpdateError: At key 'todos': Can receive only one value per step.
```

Em [`libs/deepagents/graph.py`](libs/deepagents/graph.py), introduzimos o `ResilientTodoListMiddleware` com um canal anotado e função redutora:

```python
def _take_last_todos(a: Any, b: Any) -> Any:
    return b

class ResilientPlanningState(PlanningState):
    todos: Annotated[list[Todo], _take_last_todos]

class ResilientTodoListMiddleware(TodoListMiddleware):
    state_schema = ResilientPlanningState
```

Essa modificação garante execução paralela estável e livre de falhas de concorrência.

---

## 📂 Estrutura do Repositório

```
.
├─ libs/
│  └─ deepagents/               # Engine customizada do DeepAgents com ResilientTodoListMiddleware
├─ research_agent.py            # Orquestração do agente principal, prompts e subagentes
├─ url_validator.py             # Validador HTTP de URLs com heurísticas de ATS e sanitizador
├─ job_tracker.py               # Utilitário de memória e deduplicação de vagas
├─ seen_jobs.json               # Registro persistente de vagas já reportadas
├─ llm_router.py                # Roteador multi-provedor (Gemini, OpenAI, ZhipuAI)
├─ send_report_telegram.py      # Módulo de envio de relatórios via Telegram Bot
├─ question.txt                 # Prompt base utilizado na pesquisa atual
├─ final_report.md              # Último relatório gerado com vagas 100% ativas
├─ reports/                     # Histórico versionado de relatórios diários
├─ .env.example                 # Modelo base para variáveis de ambiente
├─ .github/workflows/
│  └─ daily-report.yml          # Pipeline de automação do GitHub Actions
├─ pyproject.toml / uv.lock     # Gerenciamento de dependências
├─ README.md                    # Documentação em inglês
└─ README_pt.md                 # Documentação em português (este arquivo)
```

---

## 📱 Automação e Entrega via Telegram

O workflow do GitHub Actions (`.github/workflows/daily-report.yml`) opera de forma automatizada:

1. **Agendamento**: Segundas, quartas e sextas às 08:00 BRT (11:00 UTC).
2. **Execução do Agente**: Pesquisa, filtra e gera o arquivo `final_report.md`.
3. **Sanitização de URLs e Memória**: Audita todos os links, remove vagas fechadas e salva o `seen_jobs.json` atualizado.
4. **Disparo no Telegram**: Envia a tabela executiva formatada e o anexo completo do relatório para o chat configurado.

### Secrets Necessárias no GitHub Actions

Configure estas secrets em seu repositório (`Settings > Secrets and variables > Actions`):

| Secret | Obrigatória | Descrição |
|---|---|---|
| `GEMINI_API_KEY` | Sim (padrão) | Chave de API da Google AI Studio |
| `TAVILY_API_KEY` | Sim | Chave de API do Tavily |
| `TELEGRAM_BOT_TOKEN` | Sim | Token do bot fornecido pelo [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | Sim | ID numérico do chat via [@userinfobot](https://t.me/userinfobot) |
| `OPENAI_API_KEY` | Opcional | Chave da OpenAI (se usar GPT) |
| `ZHIPUAI_API_KEY` | Opcional | Chave da ZhipuAI (se usar GLM) |

---

## 🔒 Boas Práticas de Segurança

> ⚠️ **AVISO DE SEGURANÇA**: Nunca commite arquivos `.env` ou chaves de API no repositório.

- Chaves de API devem ser injetadas exclusivamente via variáveis de ambiente ou GitHub Secrets.
- O `.gitignore` está configurado para barrar credenciais e arquivos sensíveis (`.env`, `*.pem`, `credentials.json`).
- Se expuser uma chave acidentalmente, revogue-a imediatamente no console do provedor.

---

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).
