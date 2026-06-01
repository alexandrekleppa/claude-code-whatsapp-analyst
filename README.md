# Sales Analyst — Análise de Cadência Multi-Canal B2B

> Sistema multi-agente que analisa prospecção via **WhatsApp + VoIP** exportada do GS Engage.
> 11 agentes especializados rodam em paralelo, geram relatórios por canal e uma síntese executiva com ações concretas.

```
> /sales-analysis

  Carregando dados de input/whatsapp-conversations/...
  1.247 mensagens, 156 ligações, 89 leads (07/04/2026 a 08/04/2026)

  ? Qual intervalo deseja analisar? > últimos 7 dias

  Disparando 11 agentes em paralelo...
    ✓ Template Analyst       — 8 templates classificados
    ✓ Timing Analyst         — Heatmap gerado, janelas otimizadas
    ✓ Copy & Angle Analyst   — 8 ângulos analisados, top 3 rankeados
    ✓ Lead & DDD Analyst     — 67 DDDs mapeados, perfil ideal construído
    ✓ Correlation Hunter     — 6 hipóteses testadas, 3 novas geradas
    ✓ Call Analyst           — 156 ligações scored (0-100), outcomes mapeados
    ✓ Transcription Analyst  — Talk time, objeções, sinais de compra
    ✓ Multichannel Cadence   — Fluxo WPP→Call mapeado, gargalos identificados
    ✓ Lead Journey Analyst   — Cohorts de lead, lifecycle por DDD
    ✓ Playbook Adherence     — Aderência do agente AI ao playbook (95%)
    ✓ Notes Signal Analyzer  — Sinais em notas dos SDRs (123 relevantes)

  Compilando síntese executiva...
  Gerando PDFs...

  11 relatórios + síntese executiva salvos em output/reports/
```

---

## O que é

Pipeline **totalmente em Markdown** — sem código tradicional. Cada arquivo `.md` instrui o Claude Code a agir como um analista especializado. O orquestrador coordena **11 agentes em paralelo** (WhatsApp, VoIP, multi-canal, lifecycle, playbook, sinais) e compila uma síntese executiva cruzando todos os achados.

Entrada: JSON array do GS Engage (conversas, chamadas, transcricoes, lead, notas, playbook).
Saída: Relatório por agente (`.md`) + síntese consolidada + PDFs opcionais.

---

## Arquitetura

```
                  Dados GS Engage (12 tipos)
                            |
                    +-------v--------+
                    |  Orquestrador  |
                    |  (loadData →   |
                    |   filterByDate |
                    |    → dispatch) |
                    +-------+--------+
                            |
         +------------------+------------------+
         |                  |                  |
    [WhatsApp]         [VoIP]            [Multi-canal]
         |                  |                  |
    +----+----+    +--------+-------+   +------+------+
    | 01      | 02 | 06     | 07    | 08| 09    | 10|11
    |Template |    | Call   |Trans. |MC |Journey|PB |Notes
    |Timing   | 03 | Analyst|Analyst|Cd |       |   |
    |Copy     | 04 | (parallel)     |   | Analyst    |
    |Lead     | 05 |        |       |   |           |
    |Corr.    |    |        |       |   |           |
    +---+-----+    +---+----+---+---+   +------+-----+
        |              |          |            |
        +---[SKILLS]---+    +-----[SKILLS]-----+
            |                      |
            v                      v
        +--------+            +--------+
        |Síntese |            |Output: |
        |Exec.   |            |11 .md  |
        +--------+            |1 síntese|
                              +--------+
```

---

## Os 11 Agentes

### WhatsApp (5 agentes)

| # | Nome | Foco | Skills usadas |
|---|------|------|---|
| **01** | Template Analyst | Classifica templates (WINNER/NEUTRO/LOSER) por READ rate, response rate, velocidade de leitura | `data-scorer`, `pattern-detector` |
| **02** | Timing Analyst | Heatmap horário×dia semana, top 3 janelas ótimas, calendário semanal | `timing-strategist` |
| **03** | Copy & Angle Analyst | 6 ângulos de copy (prova social, exclusividade, urgência, curiosidade, direto, reciprocidade), DNA vencedor, 3 variações A/B | `copywriter`, `pattern-detector` |
| **04** | Lead & DDD Analyst | Performance por DDD/região (67 DDDs), perfil do lead ideal, score de priorização | `lead-profiler` |
| **05** | Correlation Hunter | 6 hipóteses pré-carregadas testadas + 3 novas hipóteses geradas a partir de sinais fracos | `hypothesis-generator` |

### VoIP (2 agentes)

| # | Nome | Foco | Skills usadas |
|---|------|------|---|
| **06** | Call Analyst | Score 0–100 por ligação (duração, outcome, metadata), distribuição de outcomes, janelas ótimas para ligar | `call-scorer`, `data-scorer` |
| **07** | Transcription Analyst | Segmentação speaker (SDR/lead), turnos de fala, talk time ratio, objeções categorizadas, sinais de compra | `transcription-analyzer`, `objection-extractor` |

### Multi-canal (2 agentes)

| # | Nome | Foco | Skills usadas |
|---|------|------|---|
| **08** | Multichannel Cadence Analyst | Fluxo end-to-end WhatsApp→Call, gargalos (taxa de avanço), tempo entre steps, funil de conversão | `funnel-builder` |
| **09** | Lead Journey Analyst | Ciclo de vida completo (DDD, cohort, estágio atual), performance de leads por região, probabilidade de WON | `lead-profiler` |

### Playbook & Sinais (2 agentes)

| # | Nome | Foco | Skills usadas |
|---|------|------|---|
| **10** | Playbook Adherence Analyst | Aderência do agente AI ao playbook (persona, pain points, guardrails), desvios e gaps | `playbook-adherence` |
| **11** | Notes Signal Analyzer | Sinais qualitativos em notas dos SDRs (objeções, contexto, intent), padrões emergentes | (análise textual pura) |

---

## As 11 Skills

Skills são capacidades compartilhadas — módulos que agentes "ativam" lendo o arquivo.

| Skill | Usada por | O que faz |
|-------|-----------|-----------|
| **copywriter** | 01, 03 | Reescrita de templates LOSER + geração de 3 variações A/B. Regras: max 3 frases, CTA em pergunta, 100–250 chars |
| **data-scorer** | 01, 06 | Normalização 0–100, Wilson Score Lower Bound (penaliza amostras pequenas), score composto |
| **pattern-detector** | 03, 05 | Análise linguística e estrutural. Checklist "DNA da mensagem vencedora" com impacto de cada elemento |
| **timing-strategist** | 02 | Transforma heatmap em calendário semanal acionável. Score por janela, regras de bom senso |
| **lead-profiler** | 04, 09 | Compara respondentes vs não-respondentes. Perfil ideal, score de priorização, segmentos a deprioritizar |
| **hypothesis-generator** | 05 | Gera 3 hipóteses novas a partir de sinais fracos (distribuições assimétricas, outliers, padrões minoritários) |
| **call-scorer** | 06 | Score de buckets de ligação (duração, outcome, metadata). Penalidades por dados faltantes |
| **transcription-analyzer** | 07 | Calcula talk time, turnos, interrupções, ratio lead:sdr, categoriza speakers |
| **objection-extractor** | 07 | Categorização de objeções e sinais em pt-BR (objeção de preço, timing, autoridade, concorrência, outro) |
| **funnel-builder** | 08 | Monta funil ASCII, identifica gargalos, calcula taxa de avanço por stage |
| **playbook-adherence** | 10 | Compara execução vs playbook (persona, pains, openings, CTAs, guardrails), score de aderência |

---

## Dados de Entrada

A pasta `input/whatsapp-conversations/` aceita **export completo do GS Engage** (não apenas mensagens). Cada arquivo é um JSON array. Arquivos opcionais — agentes consomem subsets conforme sua especialidade.

### 12 Tipos de Arquivo Suportados

| Arquivo (sufixo) | Descrição | Consumido por |
|---|---|---|
| `conversation_messages.json` | Mensagens WhatsApp (direção, status, texto, template, thread, timestamps) | Agentes 01–05, 08, 10 |
| `conversation_threads.json` | Metadados de thread (lastIncoming, status, updated) | Agente 09 |
| `voip_calls.json` | Ligações: duração, outcome (ANSWERED/MISSED/REJECTED), startedAt, recordingUrl | Agentes 06, 08 |
| `voip_call_transcriptions.json` | Segmentos com speaker (sdr/lead), timestamps, text | Agentes 07, 10 |
| `voip_call_analysis.json` | Score 0–1, feedback SPIN, próximos passos | Agentes 06, 07 |
| `lead.json` | Firmografia (empresa, indústria, DDD, custom fields, createdAt) | Agente 09 |
| `lead_notes.json` | Notas registradas pelos SDRs (conteúdo, createdAt, author) | Agente 11 |
| `ai_agents.json` | Playbook do agente AI (persona, pain points, openings, CTAs, guardrails) | Agente 10 |
| `prospection.json` | Status do ciclo (WON_LEAD, DISCARDED, IN_PROGRESS, stageId) | Agentes 08, 09 |
| `prospection_routine.json` | Desenho da rotina multi-canal (steps, timing, rules) | Agente 08 |
| `prospection_task.json` | Tarefas da cadência (type, channelType, templateId, executedAt) | Agentes 08, 09 |
| `task_execution.json` | Execução de cada task (executedAt, status, result) | Agentes 08, 09 |

**Nota:** Não é necessário que todos os 12 arquivos estejam presentes. Agentes funcionam com subsets (ex: só WhatsApp, só VoIP, etc.).

### Schema — conversation_messages.json (exemplo)

```json
[
  {
    "ID": "msg-123",
    "Thread ID": "thread-456",
    "Direction": "OUTGOING",
    "Status": "READ",
    "Text": "Olá! Tudo bem?",
    "Message Type": "TEMPLATE",
    "Template Name": "abertura_1",
    "From": "+5585987654321",
    "To": "+5585998765432",
    "Created At": "2026-04-07, 09:15",
    "Sent At": "2026-04-07, 09:15",
    "Updated At": "2026-04-07, 09:22",
    "Metadata": "{\"profileName\": \"João Silva\"}"
  }
]
```

---

## Como Usar

### 1. Exportar dados do GS Engage

Faça login em [growthstation.app](https://growthstation.app) e exporte os JSONs. Coloque em:

```bash
mkdir -p input/whatsapp-conversations
cp seu-export/*.json input/whatsapp-conversations/
```

Pode ter subpastas por cliente:
```
input/whatsapp-conversations/
├── cliente-a/
│   ├── conversation_messages.json
│   └── voip_calls.json
└── cliente-b/
    └── conversation_messages.json
```

### 2. Rodar análise no Claude Code

```
/sales-analysis
```

O orquestrador:
1. Lê todos os JSONs recursivamente
2. Identifica datas min/max nos dados
3. Pergunta qual intervalo analisar
4. Filtra e valida dados
5. **Dispara 11 agentes em paralelo**
6. Compila síntese executiva

### 3. Gerar PDFs (opcional)

```bash
# Instalar dependências
pip install markdown weasyprint

# Converter todos os relatórios
python scripts/md2pdf.py output/reports/

# Ou um arquivo específico
python scripts/md2pdf.py output/reports/report-template-2026-04-07.md
```

---

## Estrutura do Repositório

```
sales-analyst/
├── CLAUDE.md                      # Regras globais: schema, amostras mínimas, tom
├── SKILL.md                       # Entry point do /sales-analysis
├── orchestrator.md                # Orquestrador (6 passos, dispara 11 agentes)
│
├── agents/                        # 11 agentes especializados
│   ├── 01-template-analyst.md
│   ├── 02-timing-analyst.md
│   ├── 03-copy-analyst.md
│   ├── 04-lead-analyst.md
│   ├── 05-correlation-hunter.md
│   ├── 06-call-analyst.md
│   ├── 07-transcription-analyst.md
│   ├── 08-multichannel-cadence-analyst.md
│   ├── 09-lead-journey-analyst.md
│   ├── 10-playbook-adherence-analyst.md
│   └── 11-notes-signal-analyst.md
│
├── skills/                        # 11 skills compartilhadas
│   ├── copywriter.md
│   ├── data-scorer.md
│   ├── pattern-detector.md
│   ├── timing-strategist.md
│   ├── lead-profiler.md
│   ├── hypothesis-generator.md
│   ├── call-scorer.md
│   ├── transcription-analyzer.md
│   ├── objection-extractor.md
│   ├── funnel-builder.md
│   └── playbook-adherence.md
│
├── scripts/
│   └── md2pdf.py                  # Markdown → PDF (weasyprint/mdpdf)
│
├── install.sh                     # ⚠️ DESATUALIZADO: só cobre 5 agentes + 6 skills
├── uninstall.sh
│
└── README.md (este arquivo)
```

> `input/whatsapp-conversations/` e `output/reports/` são criados automaticamente, não versionados (`.gitignore`).

---

## Instalação

### ⚠️ Aviso: install.sh está desatualizado

O `install.sh` original foi feito para a versão legada (**5 agentes, 6 skills**). Ele **não instala** os agentes 06–11 nem as skills `call-scorer`, `funnel-builder`, `objection-extractor`, `playbook-adherence`, `transcription-analyzer`.

**Recomendação:** Cópia manual ou atualização do script.

### Cópia Manual (seguro)

```bash
# Cópia para ~/.claude/skills/sales-analysis/
mkdir -p ~/.claude/skills/sales-analysis
cp CLAUDE.md SKILL.md orchestrator.md ~/.claude/skills/sales-analysis/

# Cópia de agentes para ~/.claude/agents/
mkdir -p ~/.claude/agents
cp agents/*.md ~/.claude/agents/

# Cópia de skills para ~/.claude/skills/
mkdir -p ~/.claude/skills
cp skills/*.md ~/.claude/skills/
```

Após isso, `/sales-analysis` estará disponível no Claude Code.

### Desinstalar

```bash
rm -rf ~/.claude/skills/sales-analysis
rm ~/.claude/agents/0{1..11}-*.md
rm ~/.claude/skills/{copywriter,data-scorer,pattern-detector,timing-strategist,lead-profiler,hypothesis-generator,call-scorer,transcription-analyzer,objection-extractor,funnel-builder,playbook-adherence}.md
```

---

## Requisitos

| Requisito | Obrigatório | Notas |
|-----------|-------------|-------|
| [Claude Code](https://claude.ai/code) | ✅ Sim | Web, CLI, desktop ou IDE extension |
| Dados GS Engage (.json) | ✅ Sim | `input/whatsapp-conversations/` |
| Python 3.9+ | ⚠️ Apenas para PDFs | Para `md2pdf.py` |
| `markdown` + `weasyprint` | ⚠️ Apenas para PDFs | `pip install markdown weasyprint` |

---

## Relatórios de Saída

Após rodar `/sales-analysis`, serão gerados arquivos `.md` em `output/reports/`:

- `report-01-template-{DATE}.md` — Templates WINNER/NEUTRO/LOSER + reescritas
- `report-02-timing-{DATE}.md` — Heatmap + calendário semanal
- `report-03-copy-{DATE}.md` — Ângulos + DNA vencedor + 3 variações A/B
- `report-04-lead-{DATE}.md` — Mapa regional (DDDs) + perfil ideal
- `report-05-correlation-{DATE}.md` — 6 hipóteses testadas + 3 novas
- `report-06-call-{DATE}.md` — Outcomes + scores + janelas ótimas
- `report-07-transcription-{DATE}.md` — Talk time, objeções, sinais
- `report-08-cadence-{DATE}.md` — Fluxo WPP→Call, gargalos, funil
- `report-09-journey-{DATE}.md` — Lifecycle, cohorts, probabilidade WON
- `report-10-playbook-{DATE}.md` — Aderência AI ao playbook (%)
- `report-11-notes-{DATE}.md` — Sinais qualitativos em notas
- `report-executive-{DATE}.md` — Síntese consolidada com top 3 insights + 3 ações

**Versioning:** Se `report-template-2026-04-07.md` já existir, salva como `report-template-2026-04-07_v2.md`, etc.

---

## Licença

MIT
