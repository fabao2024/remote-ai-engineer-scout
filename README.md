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

```powershell
setx OPENAI_API_KEY "sk-..."
setx TAVILY_API_KEY "tvly-..."
setx LANGCHAIN_API_KEY "ls-..."          # opcional
setx LANGCHAIN_TRACING_V2 "true"         # opcional
setx LANGCHAIN_PROJECT "remote-ai-scout" # opcional
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

- **Prompt e consulta**: altere `question.txt` para direcionar o agente (ex.: focar em vagas sênior, LATAM etc.).
- **Busca fresca**: em `research_agent.py`, ajuste `internet_search` para passar `time_range="day"` ao Tavily e garantir resultados do dia.
- **Histórico de relatórios**: troque `Path("final_report.md").write_text(...)` por escrita com timestamps.
- **Novas fontes**: adicione ferramentas extras (APIs de job boards, Slack, Google Sheets) e inclua nos subagentes.
- **LangSmith**: monitore execuções habilitando `LANGCHAIN_TRACING_V2=true` e conferindo o projeto definido em `LANGCHAIN_PROJECT`.

## Problemas Comuns

- `KeyError: 'TAVILY_API_KEY'`: defina a variável antes de rodar.
- `Failed to POST https://api.smith.langchain.com...`: `LANGCHAIN_API_KEY` ausente ou sem permissão; remova tracing se não for usar.
- `typing.NotRequired` warnings: já eliminados nos middlewares (state schemas agora usam tipos opcionais padrão).

## Roadmap

- Persistir histórico diário em uma pasta `reports/`.
- Adicionar testes de regressão para os middlewares customizados.
- Automatizar publicação (ex.: GitHub Actions que roda o agente e faz commit do relatório diário).

## Créditos

- Baseado em [DeepAgents](https://github.com/langchain-ai/deepagents) e sua arquitetura de agentes profundos.
- Inspiração de produtos como Claude Code, Deep Research e Manus.

Sinta-se à vontade para abrir issues ou PRs com melhorias!
