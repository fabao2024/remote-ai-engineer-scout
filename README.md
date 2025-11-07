![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-DeepAgents-4B8BBE)
![CI](https://github.com/<SEU_USER>/<SEU_REPO>/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)

# Remote AI Engineer Scout

> Projeto baseado em [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) e adaptado para mapear vagas remotas de AI Engineer em tempo real.

## Visão Geral

Este repositório traz um agente “deep” construído com **DeepAgents + LangChain**, usando o modelo `openai:gpt-4o-mini`, subagentes especializados e busca web via **Tavily**. A cada execução, ele coleta vagas remotas de Engenharia de IA, cruza requisitos (skills, senioridade, stack, salários, restrições geográficas) e gera um relatório em Markdown pronto para compartilhar.

Principais destaques:
- Supervisão única com subagentes de **pesquisa** e **crítica** para garantir qualidade.
- Middleware de **filesystem** customizado para armazenar o relatório (`final_report.md`) e o prompt base (`question.txt`).
- Integração opcional com LangSmith para rastrear execuções (`LANGCHAIN_TRACING_V2=true`).

## Arquitetura em Alto Nível

```
Usuário → research_agent.py
                  ├─ create_deep_agent(...)
                  │     ├─ Subagent “research-agent” (usa Tavily)
                  │     └─ Subagent “critique-agent”
                  ├─ Ferramentas: internet_search (Tavily), filesystem middleware
                  └─ Saídas: final_report.md + question.txt
```

## Pré-requisitos

- Python 3.10+
- Dependências listadas em `requirements.txt`
- Chaves/variáveis de ambiente:
  - `OPENAI_API_KEY`
  - `TAVILY_API_KEY`
  - `LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_PROJECT` (opcionais, apenas se quiser enviar traces ao LangSmith)

### Exemplo de configuração no PowerShell

| Variável                | Obrigatória | Exemplo                  | Uso                                     |
|-------------------------|-------------|--------------------------|------------------------------------------|
| OPENAI_API_KEY          | Sim         | sk-...                   | Modelo `openai:gpt-4o-mini`              |
| TAVILY_API_KEY          | Sim         | tvly-...                 | Busca Web                                |
| LANGCHAIN_API_KEY       | Não         | ls-...                   | Tracing (LangSmith)                      |
| LANGCHAIN_TRACING_V2    | Não         | true                     | Ativa tracing                            |
| LANGCHAIN_PROJECT       | Não         | remote-ai-scout          | Nome do projeto no LangSmith             |

```

Reabra o terminal ou execute `,& $PROFILE` para carregar as variáveis persistidas.  
Para uso apenas na sessão atual, utilize `$env:OPENAI_API_KEY = "..."`.

## Instalação

```bash
python -m venv .venv
.\.venv\Scripts\activate        # Windows (PowerShell)
# source .venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

## Como Executar

```bash
python research_agent.py
```

O script:
1. Lê o prompt em `question.txt` (por padrão “Find remote AI Engineer roles hiring now aligned with my profile.”).
2. Invoca o deep agent, que dispara os subagentes de pesquisa/crítica e usa Tavily para coletar vagas atuais.
3. Sobrescreve `final_report.md` com o relatório atualizado e, se necessário, atualiza `question.txt`.

> Quer manter um histórico em vez de sobrescrever? Ajuste o trecho final de `research_agent.py` para salvar com timestamp (ex.: `final_report_YYYYMMDD.md`).

## Estrutura do Repositório

```
.
├─ research_agent.py            # Configuração principal do agente
├─ question.txt                 # Prompt base
├─ final_report.md              # Último relatório gerado
├─ libs/
│  ├─ deepagents-cli/...        # Ajustes no middleware de memória
│  └─ deepagents/...            # Middlewares customizados (filesystem, subagents)
├─ requirements.txt
└─ README.md
```

## Personalização

Find remote AI Engineer roles hiring now aligned with my profile.

# Scope
- Focus: Senior AI/ML Engineer roles
- Region: Americas (Remote, LATAM-friendly)
- Tech: Python, LangChain, Vector DBs, LLM Ops
- Exclude: Onsite-only, internships

----------------------------------------------------------------------------------------------------------------------------

- **Prompt e consulta**: altere `question.txt` para direcionar o agente (ex.: focar em vagas sênior, LATAM etc.).
- **Busca fresca**: em `research_agent.py`, ajuste `internet_search` para passar `time_range="day"` ao Tavily e garantir resultados do dia.
- **Histórico de relatórios**: troque `Path("final_report.md").write_text(...)` por escrita com timestamps.
- **Novas fontes**: adicione ferramentas extras (APIs de job boards, Slack, Google Sheets) e inclua nos subagentes.
- **LangSmith**: monitore execuções habilitando `LANGCHAIN_TRACING_V2=true` e conferindo o projeto definido em `LANGCHAIN_PROJECT`.

## Problemas Comuns

- `KeyError: 'TAVILY_API_KEY'`: defina a variável antes de rodar.
- `Failed to POST https://api.smith.langchain.com...`: `LANGCHAIN_API_KEY` ausente ou sem permissão; remova tracing se não for usar.
- `typing.NotRequired` warnings: já eliminados nos middlewares (state schemas agora usam tipos opcionais padrão).

# Resultados Esperados (exemplo de 1 execução)

# Remote AI Engineer Opportunities Brief

## Market Snapshot
Based on the latest searches for remote AI Engineer roles, there is a significant demand for skilled professionals in this field. The market reflects an enthusiastic hiring climate, as employers actively seek talent across various sectors. The typical salary for remote AI Engineers ranges widely due to differences in experience levels and specific job requirements. Many organizations are embracing remote work, allowing for a larger talent pool across different geographic regions.

## Active Remote Employers
1. **Remote Rocketship**  
   - **Type**: Job aggregator platform listing various remote opportunities.  
   - **Focus**: Variety of roles including AI Engineers, Data Scientists, and Machine Learning Engineers.  
   - **Hiring Stage**: Actively hiring, with thousands of openings in the AI domain.  

2. **Crossover**  
   - **Type**: Recruitment platform focused on finding top talent for tech positions.  
   - **Focus**: AI Engineer roles, with a keen interest in high-performance candidates.  
   - **Hiring Stage**: Actively searching for engineers, allowing candidates to apply easily.  

3. **Indeed & ZipRecruiter**  
   - **Type**: Job listing platforms aggregating postings from various companies.  
   - **Focus**: Broad range of positions in AI engineering across different sectors.  
   - **Hiring Stage**: Continuously updated job listings, ensuring the latest opportunities are available.  

## Representative Openings
1. **AI Engineer at Remote Rocketship**  
   - **URL**: [Remote Rocketship](https://www.remoterocketship.com/jobs/ai-engineer/)  
   - **Compensation**: Average salary around $159,120/year based on several openings.  
   - **Skills Required**: Deep learning, machine learning algorithms, programming in Python/R.

2. **AI Engineer at Crossover**  
   - **URL**: [Crossover](https://www.crossover.com/jobs/ai-engineer)  
   - **Compensation**: Positions starting around $60,000/year; varies with experience.  
   - **Skills Required**: Knowledge in AI frameworks, algorithms, and software development.  

3. **AI Engineer Roles on Indeed**  
   - **URL**: [Indeed](https://www.indeed.com/q-artificial-intelligence-engineer-l-remote-jobs.html)  
   - **Compensation**: Ranges from $188,000 to $238,000/year; varies extensively by listing.  
   - **Skills Required**: Strong coding skills in modern programming languages and experience with AI tools.  

## Required Skills & Tech Stack
- **Programming Languages**: Python, R, Java, C++.
- **Frameworks**: TensorFlow, PyTorch, Keras for deep learning and neural networks.
- **Algos**: Understanding of machine learning algorithms, including regression, classification, and clustering.
- **DevOps**: Familiarity with cloud platforms like AWS and Google Cloud for AI deployments.
- **Software Development**: Version control (Git), agile methodologies, and general software engineering practices.

## Compensation & Location Notes
- **Salary Insights**: Average salaries generally range from $100,000 to $245,000/year. Entry-level positions start around $60,000, while senior roles can command salaries over $200,000.
- **Location**: While roles are remote, be mindful of company stipulations on time zones or geographical locations that may not be eligible for all roles.
- **Visa/Contractual**: Some positions may require you to be in specific jurisdictions due to legal and tax compliance issues.

## Application Strategy
- Leverage job boards like Indeed and ZipRecruiter for targeted applications.  
- Tailor your resume to highlight relevant experiences and accomplishments in AI engineering.  
- Networking through LinkedIn can help establish connections that may lead to referrals.  
- Consider obtaining certifications in AI to differentiate yourself from other candidates.

## Sources
1. [Remote AI Engineer Jobs – Remote Rocketship](https://www.remoterocketship.com/jobs/ai-engineer/)
2. [AI Engineer jobs in Remote - Indeed](https://www.indeed.com/q-artificial-intelligence-engineer-l-remote-jobs.html)
3. [2025 AI Engineer Salary in Remote - Built In](https://builtin.com/salaries/us/remote/ai-engineer)
4. [Remote Ai Engineer Jobs - ZipRecruiter](https://www.ziprecruiter.com/Jobs/Remote-Ai-Engineer)
5. [Remote AI Engineer Jobs - Crossover](https://www.crossover.com/jobs/ai-engineer)



## Roadmap

- Persistir histórico diário em uma pasta `reports/`.
- Adicionar testes de regressão para os middlewares customizados.
- Automatizar publicação (ex.: GitHub Actions que roda o agente e faz commit do relatório diário).

## Créditos

- Baseado em [DeepAgents](https://github.com/langchain-ai/deepagents) e sua arquitetura de agentes profundos.
- Inspiração de produtos como Claude Code, Deep Research e Manus.

Sinta-se à vontade para abrir issues ou PRs com melhorias!
