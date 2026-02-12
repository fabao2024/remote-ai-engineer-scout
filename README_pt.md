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
├─ send_report_email.py         # Utilitário de envio de email
├─ question.txt                 # Prompt base
├─ final_report.md              # Último relatório gerado
├─ reports/                     # Relatórios diários com timestamp (auto-criado)
├─ libs/
│  ├─ deepagents-cli/...        # Ajustes do middleware de memória
│  └─ deepagents/...            # Filesystem + subagents customizados
├─ .github/workflows/
│  └─ daily-report.yml          # Automação do GitHub Actions
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

## Automação e Relatórios Diários

> ⚠️ **AVISO DE SEGURANÇA**: Este é um repositório **público**. Nunca commite chaves de API no seu código!
> Todas as chaves devem ser armazenadas em [GitHub Secrets](https://docs.github.com/pt/actions/security-guides/using-secrets-in-github-actions). Veja a [seção de Segurança](#segurança-e-proteção-de-chaves) abaixo.

O repositório inclui um workflow do GitHub Actions (`.github/workflows/daily-report.yml`) que automaticamente:

1. **Executa diariamente às 8:00 UTC** (configurável)
2. **Roda o agente de pesquisa** para coletar vagas atualizadas
3. **Salva relatórios com timestamp** no diretório `reports/`
4. **Envia o relatório por email** para sua caixa de entrada

### Instruções de Configuração

#### 1. Secrets Necessários no GitHub

Configure estes secrets nas configurações do repositório (`Settings > Secrets and variables > Actions`):

| Secret | Obrigatório | Descrição |
|--------|-------------|-----------|
| `OPENAI_API_KEY` | Sim | Sua chave API da OpenAI |
| `TAVILY_API_KEY` | Sim | Chave API do Tavily para busca web |
| `EMAIL_TO` | Sim | Email do destinatário (padrão: `fabio.pettian@gmail.com`) |
| `EMAIL_FROM` | Sim | Email do remetente |
| `EMAIL_PASSWORD` | Sim | Senha de app do email remetente |
| `SMTP_SERVER` | Não | Servidor SMTP (padrão: `smtp.gmail.com`) |
| `SMTP_PORT` | Não | Porta SMTP (padrão: `587`) |
| `LANGCHAIN_API_KEY` | Não | Para rastreamento LangSmith |
| `LANGCHAIN_TRACING_V2` | Não | Defina como `true` para ativar rastreamento |
| `LANGCHAIN_PROJECT` | Não | Nome do projeto no LangSmith |

#### 2. Configuração de Senha de App do Gmail

Se usar Gmail como remetente:

1. Ative a Autenticação de 2 Fatores na sua conta Google
2. Gere uma **Senha de App** em [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Use esta senha de app como `EMAIL_PASSWORD` (não sua senha regular)

#### 3. Execução Manual

Você pode executar o workflow manualmente a qualquer momento:
- Vá para **Actions > Daily AI Engineer Scout Report** no seu repositório GitHub
- Clique em **Run workflow**

### Formato do Email

O email inclui:
- **Versão HTML** com conteúdo formatado do relatório
- **Versão texto** para compatibilidade
- **Anexo Markdown** para fácil salvamento/compartilhamento

**Nota sobre armazenamento de relatórios:** Por padrão, os relatórios são commitados no repositório. Se preferir não armazenar relatórios no git:
1. Descomente a linha `# reports/` no `.gitignore`
2. Modifique o workflow para remover o step "Commit report to repository"

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
