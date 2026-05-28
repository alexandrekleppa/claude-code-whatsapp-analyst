# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> Este arquivo tem duplo papel: é a **fonte** versionada no repo **e** um **artefato de runtime** — o `install.sh` o copia para `~/.claude/skills/sales-analysis/CLAUDE.md`, e o `orchestrator.md` referencia suas seções por número (ex: "header/footer de CLAUDE.md §6/§7") e o schema de dados abaixo. **Não renumere nem reestruture as seções existentes** — apenas adicione conteúdo de forma aditiva, sob risco de quebrar o orquestrador.

## Natureza do projeto

Não há código de aplicação, build, lint ou testes. O sistema é **inteiramente prompts em Markdown**: cada `.md` instrui o Claude Code a agir como um analista. Os únicos artefatos executáveis são scripts Python utilitários de pós-processamento (PDF). Para "rodar" o sistema, leia e siga `orchestrator.md`.

## Fluxo de execução

`SKILL.md` (entry point de `/sales-analysis`) → `orchestrator.md` (fluxo de 6 passos) → dispara **11 agentes** (`agents/01-…` a `11-…`) **em paralelo** via `Task()` numa única mensagem → cada agente lê as **skills** (`skills/*.md`) listadas em seu prompt → orquestrador compila a síntese executiva. As skills são módulos de capacidade reutilizáveis, "ativados" quando um agente lê o arquivo. O mapa agente→skill→dataset é a tabela do Passo 3 do `orchestrator.md`.

## ⚠️ Documentação desatualizada

`README.md`, `SKILL.md` e `install.sh` descrevem a versão **legada de 5 agentes / 6 skills**. O sistema atual tem **11 agentes e 11 skills** — `orchestrator.md` e o conteúdo de `agents/` + `skills/` são a fonte da verdade. Consequência prática: **`install.sh` está quebrado** — ele só instala os agentes 01-05 e 6 skills; não instala os agentes 06-11 nem as skills `call-scorer`, `funnel-builder`, `objection-extractor`, `playbook-adherence`, `transcription-analyzer`. Corrija `install.sh` (e `SKILL.md`/`README.md`) antes de confiar na instalação.

## Diretórios

- `input/whatsapp-conversations/` — export completo do GS Engage (JSON arrays). Pode ter subpastas por cliente (ex: `wellz/`, com prefixo no nome do arquivo: `wellz_conversation_messages.json`). Git-ignorado (dados sensíveis).
- `output/<cliente>/` e `output/reports/` — relatórios gerados (`.md` + `.pdf`). Git-ignorado.
- `analysis/` — `run_analysis.py` é um script **one-off hardcoded para o cliente `wellz`** (lê `input/whatsapp-conversations/wellz/`), não faz parte do pipeline genérico. `findings.json` é a saída dele. Não generalize sem ser pedido.

## Comandos

```bash
python scripts/md2pdf.py output/reports/        # converte todos os .md de uma pasta em PDF
python scripts/md2pdf.py relatorio.md -o x.pdf  # arquivo único, nome customizado
pip install markdown weasyprint                 # dependências (fallback: pip install mdpdf)
```

---

# Sales Analyst — Sistema de Análise de Cadência de Prospecção

Este projeto analisa mensagens de WhatsApp exportadas do GS Engage (growthstation.app) para otimizar cadências de prospecção B2B.

## Estrutura do Projeto

```
sales-analyst/
├── CLAUDE.md              ← Este arquivo (regras globais)
├── orchestrator.md        ← Agente orquestrador principal (dispara 11 agentes em paralelo)
├── agents/                ← Agentes especializados de análise
│   ├── 01-template-analyst.md         (WhatsApp — performance de templates)
│   ├── 02-timing-analyst.md           (WhatsApp — janelas de horário)
│   ├── 03-copy-analyst.md             (WhatsApp — ângulos e copy)
│   ├── 04-lead-analyst.md             (WhatsApp — DDD/região)
│   ├── 05-correlation-hunter.md       (WhatsApp — correlações e hipóteses)
│   ├── 06-call-analyst.md             (VoIP — outcomes, score, janelas)
│   ├── 07-transcription-analyst.md    (VoIP — objeções, aberturas, talk:listen)
│   ├── 08-multichannel-cadence-analyst.md (rotina end-to-end CALL+WPP)
│   ├── 09-lead-journey-analyst.md     (lifecycle/cohort do lead)
│   ├── 10-playbook-adherence-analyst.md (aderência do agente AI ao playbook)
│   └── 11-notes-signal-analyst.md     (sinais qualitativos das notas)
├── skills/                ← Skills compartilhadas entre agentes
│   ├── copywriter.md
│   ├── data-scorer.md
│   ├── pattern-detector.md
│   ├── timing-strategist.md
│   ├── lead-profiler.md
│   ├── hypothesis-generator.md
│   ├── call-scorer.md            (score de buckets de call)
│   ├── transcription-analyzer.md (talk-time, turnos, interrupções)
│   ├── objection-extractor.md    (categorização de objeções/sinais em pt-BR)
│   ├── funnel-builder.md         (funil ASCII + gargalo)
│   └── playbook-adherence.md     (aderência ao playbook AI)
├── input/
│   └── whatsapp-conversations/   ← Pode conter EXPORT COMPLETO do GS Engage (não só mensagens):
│                                   conversation_messages, conversation_threads, voip_calls,
│                                   voip_call_transcriptions, voip_call_analysis, lead,
│                                   lead_notes, ai_agents, prospection, prospection_routine,
│                                   prospection_task, task_execution, people, custom_fields.
│                                   Pode ter subpastas por cliente (ex: wellz/).
└── output/
    └── reports/                  ← Relatórios gerados
```

---

## Schema dos Dados de Entrada (GS Engage)

A pasta `input/whatsapp-conversations/` aceita o **export completo do GS Engage**, não apenas mensagens. Cada arquivo é um JSON array. Os agentes consomem subsets conforme sua especialidade.

### Visão geral dos arquivos

| Arquivo (sufixo) | Descrição | Consumido por |
|---|---|---|
| `conversation_messages.json` | Mensagens WhatsApp (schema detalhado abaixo) | Agentes 01-05, 08, 10 |
| `conversation_threads.json` | Metadados de thread (lastIncoming, status) | Agente 09 |
| `voip_calls.json` | Ligações: duração, outcome, recording, hangup | Agentes 06, 08 |
| `voip_call_transcriptions.json` | `segments[]` com speaker (sdr/lead), timestamps | Agentes 07, 10 |
| `voip_call_analysis.json` | Score 0–1, feedback SPIN, próximos passos | Agentes 06, 07 |
| `lead.json` | Firmografia (empresa, indústria, custom fields) | Agente 09 |
| `lead_notes.json` | Notas registradas pelos SDRs | Agente 11 |
| `ai_agents.json` | Playbook do agente AI (persona, pains, guardrails) | Agente 10 |
| `prospection.json` | Status do ciclo (WON_LEAD / DISCARDED / IN_PROGRESS) | Agentes 08, 09 |
| `prospection_routine.json` | Desenho da rotina (steps multi-canal) | Agente 08 |
| `prospection_task.json` + `task_execution.json` | Execução de cada step | Agentes 08, 09 |
| `people.json`, `custom_fields.json` | Metadados (time, schemas) | Auxiliares |

### Schema detalhado — `conversation_messages.json`

Cada registro representa uma mensagem de WhatsApp com os seguintes campos:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `ID` | string | Identificador único da mensagem |
| `Project ID` | string | ID do projeto no GS Engage |
| `Thread ID` | string | ID da thread/conversa (agrupa mensagens de um mesmo lead) |
| `Sender ID` | string | ID do remetente no sistema |
| `Agent ID` | string | ID do agente AI que gerou a mensagem |
| `Prospection ID` | string | ID da prospecção (vazio em mensagens de follow-up manual) |
| `Task Execution ID` | string | ID da execução da tarefa na cadência |
| `Channel` | string | Sempre `WHATSAPP` |
| `Direction` | string | `OUTGOING` (enviada) ou `INCOMING` (recebida do lead) |
| `Status` | string | `DELIVERED`, `READ`, `SENT`, `UNDELIVERED`, `FAILED` |
| `Text` | string | Corpo da mensagem |
| `Message Type` | string | `TEMPLATE` (mensagem padronizada) ou `TEXT` (sessão/manual) |
| `From` | string | Telefone remetente no formato `+55XXXXXXXXXXX` |
| `To` | string | Telefone destinatário no formato `+55XXXXXXXXXXX` |
| `Created At` | string | Data de criação no formato `YYYY-M-DD, HH:MM` |
| `Updated At` | string | Data de atualização no formato `YYYY-M-DD, HH:MM` |
| `Sent At` | string | Data de envio no formato `YYYY-M-DD, HH:MM` |
| `Template Name` | string | Nome do template usado (ex: `jan_2`, `abertura_de_portas_1`) |
| `Template Parameters` | string | JSON com parâmetros (ex: `{"1":"{{firstName}}"}`) |
| `Provider` | string | Provedor de envio (ex: `TWILIO`) |
| `Whasapp Message ID` | string | ID da mensagem no WhatsApp/Twilio |
| `Metadata` | string | Metadados adicionais (inclui `profileName` em INCOMING) |

### Notas sobre os dados

- Mensagens `INCOMING` sempre têm `Direction: "INCOMING"` e o campo `From` é o número do lead.
- Mensagens `OUTGOING` com `Status: "READ"` foram lidas pelo lead.
- O campo `Template Name` só é preenchido em mensagens `Message Type: "TEMPLATE"`.
- Mensagens `TEXT` são respostas manuais do agente AI dentro de uma sessão ativa.
- O `Thread ID` conecta todas as mensagens de uma conversa com um lead específico.
- `Updated At` quando `Status = READ` indica o momento da leitura.
- `Metadata` em mensagens INCOMING contém `profileName` do lead no WhatsApp.

---

## Regras Globais do Sistema

### 1. Seleção de Intervalo de Datas (OBRIGATÓRIO)

Antes de iniciar qualquer análise:

1. Ler todos os arquivos `.json` em `input/whatsapp-conversations/`
2. Identificar a data mais antiga e a mais recente nos dados (`Created At`)
3. Perguntar ao usuário:

> "Temos conversas de DD/MM/AAAA até DD/MM/AAAA. Qual intervalo deseja analisar? (ex: últimos 7 dias, semana passada, 01/01 a 15/01, ou 'tudo')"

4. Filtrar os dados pelo intervalo selecionado antes de passá-los aos agentes.

### 2. Nunca Sobrescrever Relatórios

Antes de salvar qualquer output em `output/reports/`:

1. Listar arquivos existentes no diretório
2. Se o nome base já existir, incrementar versão:
   - Primeiro: `report-template-2026-01-15.md`
   - Se existir: `report-template-2026-01-15_v2.md`
   - Se existir: `report-template-2026-01-15_v3.md`
   - E assim por diante

### 3. Paralelismo Obrigatório

O orquestrador DEVE disparar todos os 11 subagentes em paralelo usando `Task()` em uma única mensagem com múltiplas chamadas. Nunca rodar agentes em sequência. A única exceção é a síntese final, que depende dos resultados de todos os agentes.

### 4. Mínimo de Amostras

Nenhum agente deve emitir veredicto definitivo sobre um template, padrão ou correlação com menos de **10 amostras**. Abaixo disso:

- Sinalizar como **"⚠️ Dados insuficientes (N amostras)"**
- Não incluir na classificação WINNER/NEUTRO/LOSER
- Não usar para calcular médias ou rankings
- Reportar o dado, mas com ressalva explícita

### 5. Tom dos Relatórios

- **Direto e orientado a ação** — sem rodeios, sem disclaimers genéricos
- Cada seção deve terminar com **"→ O que fazer com isso:"** seguido de recomendação concreta
- Usar dados numéricos sempre que possível
- Evitar linguagem vaga ("parece que", "talvez", "possivelmente")
- Quando há incerteza, quantificar: "com 67% de confiança" ou "baseado em apenas 12 amostras"

### 6. Header Padrão dos Relatórios

Todo relatório gerado por qualquer agente DEVE começar com:

```markdown
# [Nome do Agente] Report
**Data de geração**: DD/MM/AAAA HH:MM
**Intervalo analisado**: DD/MM/AAAA a DD/MM/AAAA
**Total de mensagens no período**: X
**Mensagens OUTGOING**: X | **Mensagens INCOMING**: X
**Templates únicos**: X
**Threads únicas**: X
---
```

### 7. Footer Padrão dos Relatórios

Todo relatório DEVE terminar com:

```markdown
---
## → Ações Recomendadas
1. [ação concreta, responsável sugerido, prazo]
2. ...
3. ...

## → Próxima análise sugerida
[o que observar no próximo batch para validar os achados deste]
```

---

## Como Executar uma Análise

1. Copie os JSONs exportados do GS Engage para `input/whatsapp-conversations/`
2. Leia o arquivo `orchestrator.md` e siga as instruções nele contidas
3. O orquestrador cuidará de disparar os agentes e compilar o relatório final
4. Os relatórios serão salvos em `output/reports/`

---

## Convenções de Nomenclatura

- Relatórios individuais: `report-[agente]-YYYY-MM-DD.md`
- Relatório consolidado: `report-YYYY-MM-DD.md`
- Versionamento: `_v2`, `_v3`, etc. quando já existir arquivo com mesmo nome
