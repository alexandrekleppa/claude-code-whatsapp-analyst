# Sales Analyst — WhatsApp Cadence Intelligence for Claude Code

> Sistema multi-agente que analisa cadencias de prospeccao B2B via WhatsApp.
> 5 agentes especializados rodam em paralelo dentro do Claude Code, geram 7 relatorios (Markdown + PDF) e entregam acoes concretas para otimizar templates, timing, copy, regioes e correlacoes.

```
> /sales-analysis

  Carregando dados de input/whatsapp-conversations/...
  91 mensagens encontradas (07/04/2026 a 08/04/2026)

  ? Qual intervalo deseja analisar? > tudo

  Disparando 5 agentes em paralelo...
    + Template Analyst      -- 2 templates classificados (ambos NEUTRO)
    + Timing Analyst        -- Heatmap gerado, 2 janelas identificadas
    + Copy & Angle Analyst  -- 2 angulos rankeados, 3 variacoes geradas
    + Lead & DDD Analyst    -- 36 DDDs mapeados, perfil ideal construido
    + Correlation Hunter    -- 1 hipotese confirmada, 3 novas geradas

  Compilando sintese executiva...
  Gerando PDFs...

  7 relatorios salvos em output/invest-smart/
```

---

## Como funciona

O sistema e composto inteiramente por **prompts em Markdown** — nao ha codigo tradicional. Cada arquivo `.md` instrui o Claude Code a agir como um analista especializado. O orquestrador coordena 5 agentes em paralelo e compila uma sintese executiva cruzando os achados.

```
           Dados JSON (GS Engage)
                    |
            +-------v--------+
            |  Orquestrador  |
            +---+--+--+--+--+
                |  |  |  |  |
     +----------+  |  |  |  +----------+
     v             v  v  v             v
+---------+  +------+ +------+ +------+ +-----------+
| Template |  |Timing| | Copy | | Lead | |Correlation|
| Analyst  |  |Analyst| |Analyst| |Analyst| |  Hunter  |
+----+-----+  +--+---+ +--+---+ +--+---+ +-----+----+
     |           |        |        |            |
     v           v        v        v            v
  [skills]    [skills]  [skills]  [skills]    [skills]
     |           |        |        |            |
     +-----------+-+------+-+------+------------+
                   |
            +------v-------+
            |   Sintese    |
            |  Executiva   |
            +--------------+
                   |
          7 relatorios (.md + .pdf)
```

---

## Quick Start

### 1. Clonar e instalar

```bash
git clone https://github.com/seu-usuario/sales-analyst.git
cd sales-analyst
chmod +x install.sh
./install.sh
```

O `install.sh` copia os agentes e skills para `~/.claude/` — onde o Claude Code os encontra automaticamente.

### 2. Adicionar dados

Coloque os JSONs exportados do [GS Engage](https://growthstation.app) na pasta de input:

```bash
cp seus-dados.json input/whatsapp-conversations/
```

### 3. Rodar analise

No Claude Code:

```
/sales-analysis
```

### 4. Gerar PDFs (opcional)

```bash
pip install markdown weasyprint
python scripts/md2pdf.py output/reports/
```

---

## Estrutura do Repositorio

```
sales-analyst/
|
|-- CLAUDE.md                  # Regras globais: schema dos dados, amostras minimas, tom
|-- SKILL.md                   # Entry point do /sales-analysis
|-- orchestrator.md            # Logica do orquestrador (6 passos)
|-- ARQUITETURA.md             # Documentacao detalhada da arquitetura
|
|-- agents/                    # 5 agentes especializados
|   |-- 01-template-analyst.md
|   |-- 02-timing-analyst.md
|   |-- 03-copy-analyst.md
|   |-- 04-lead-analyst.md
|   +-- 05-correlation-hunter.md
|
|-- skills/                    # 6 skills compartilhadas
|   |-- copywriter.md
|   |-- data-scorer.md
|   |-- pattern-detector.md
|   |-- timing-strategist.md
|   |-- lead-profiler.md
|   +-- hypothesis-generator.md
|
|-- scripts/                   # Utilitarios
|   +-- md2pdf.py              # Markdown -> PDF
|
|-- install.sh                 # Instala agentes/skills em ~/.claude/
+-- uninstall.sh               # Remove do ~/.claude/
```

> `input/` e `output/` sao criados pelo `install.sh` mas nao versionados (`.gitignore`). Dados de conversas contem telefones reais e nunca devem ser commitados.

---

## Os 5 Agentes

### 01 — Template Analyst

Classifica cada template como **WINNER**, **NEUTRO** ou **LOSER**.

| Metrica | Formula |
|---------|---------|
| READ rate | `READ / (READ + DELIVERED)` |
| Response rate | Threads com INCOMING / Total de threads |
| Velocidade de leitura | `Updated At - Sent At` quando Status = READ |

Classificacao: WINNER (READ > 60% ou response > 15%) · NEUTRO (READ 30-60%) · LOSER (READ < 30% ou zero respostas com volume > 20).

Gera reescritas automaticas para LOSERs usando a skill **copywriter**.

### 02 — Timing Analyst

Gera heatmap de READ rate por **faixa horaria x dia da semana** (7x7), identifica top 3 janelas para enviar e top 3 para evitar, e monta um calendario semanal otimizado com distribuicao de volume.

### 03 — Copy & Angle Analyst

Classifica cada template em 6 angulos de copy (prova social, exclusividade, urgencia, curiosidade, direto/consultivo, reciprocidade), monta o "DNA da mensagem vencedora" e gera 3 novas variacoes para A/B test.

### 04 — Lead & DDD Analyst

Analisa performance por DDD/regiao (67 DDDs mapeados), identifica prospeccoes que avancaram, constroi o perfil do lead ideal e gera um score de priorizacao para proximos disparos.

### 05 — Correlation Hunter

Testa 6 hipoteses pre-carregadas (velocidade de leitura, saturacao, DDD x template, posicao na cadencia, tamanho de mensagem, reutilizacao de thread) e gera 3 novas hipoteses a partir de sinais fracos nos dados.

---

## As 6 Skills

Skills sao capacidades compartilhadas entre agentes — modulos reutilizaveis que os agentes "ativam" lendo o arquivo.

| Skill | Agentes | O que faz |
|-------|---------|-----------|
| **copywriter** | 01, 03 | Reescrita de LOSERs (modo 1) + geracao de variacoes A/B (modo 2). Regras rigidas: max 3 frases, CTA em pergunta, 100-250 chars, palavras proibidas |
| **data-scorer** | 01 | Normalizacao 0-100, Wilson Score Lower Bound para penalizar amostras pequenas, score composto (40% read + 40% response + 20% velocidade) |
| **pattern-detector** | 03, 05 | Analise linguistica e estrutural. Gera checklist "DNA da mensagem vencedora" com impacto de cada elemento |
| **timing-strategist** | 02 | Transforma heatmap em calendario semanal acionavel. Score por janela, regras de bom senso (dados vencem), distribuicao de volume |
| **lead-profiler** | 04 | Compara respondentes vs nao-respondentes. Perfil ideal, score de priorizacao, segmentos a deprioritizar |
| **hypothesis-generator** | 05 | Gera 3 hipoteses novas a partir de sinais fracos: distribuicoes assimetricas, outliers, padroes minoritarios, tendencias temporais |

---

## Dados de Entrada

Arquivos JSON exportados do [GS Engage](https://growthstation.app). Cada arquivo e um array onde cada objeto e uma mensagem de WhatsApp.

### Campos principais

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `Direction` | `OUTGOING` / `INCOMING` | Mensagem enviada ou recebida |
| `Status` | `READ` / `DELIVERED` / `SENT` / `UNDELIVERED` | Estado da entrega |
| `Text` | string | Corpo da mensagem |
| `Template Name` | string | Nome do template (so em `Message Type = "TEMPLATE"`) |
| `Thread ID` | string | Agrupa mensagens da mesma conversa |
| `To` / `From` | `+55XXXXXXXXXXX` | Telefones (DDD = digitos 3-4) |
| `Created At` / `Sent At` / `Updated At` | `YYYY-M-DD, HH:MM` | Timestamps |
| `Metadata` | string | Contem `profileName` em INCOMING |

### Regras dos dados

- **READ rate** = `READ / (READ + DELIVERED)` — exclui SENT, UNDELIVERED, FAILED
- **Response rate** = threads com INCOMING / total threads iniciadas
- **Minimo 10 amostras** para qualquer classificacao; abaixo disso: "Dados insuficientes"

---

## Relatorios de Saida

Cada analise gera 7 relatorios em Markdown e, opcionalmente, PDF:

| Relatorio | Conteudo |
|-----------|----------|
| **Executivo** | Sintese cruzada dos 5 agentes, top 3 insights, top 3 acoes |
| **Top 10 Recomendacoes** | Acoes priorizadas por impacto com metricas de sucesso |
| **Template Analyst** | Classificacao WINNER/NEUTRO/LOSER + reescritas |
| **Timing Analyst** | Heatmap + calendario semanal otimizado |
| **Copy Analyst** | Ranking de angulos + DNA vencedor + 3 variacoes A/B |
| **Lead & DDD Analyst** | Mapa regional + perfil do lead ideal + score |
| **Correlation Hunter** | 6 hipoteses testadas + 3 novas hipoteses |

Relatorios nunca sao sobrescritos — versoes incrementais `_v2`, `_v3`, etc.

---

## Script: md2pdf.py

Converte relatorios Markdown em PDF com estilo profissional.

```bash
# Converter todos os .md de uma pasta
python scripts/md2pdf.py output/reports/

# Converter um arquivo especifico
python scripts/md2pdf.py relatorio.md

# Nome customizado
python scripts/md2pdf.py relatorio.md -o saida.pdf
```

### Dependencias

```bash
# Opcao 1 (recomendada) — weasyprint
pip install markdown weasyprint

# Opcao 2 (fallback) — mdpdf
pip install mdpdf
```

---

## Instalacao e Desinstalacao

### Instalar

```bash
chmod +x install.sh
./install.sh
```

Copia os arquivos para `~/.claude/`:

```
~/.claude/
|-- skills/sales-analysis/
|   |-- SKILL.md, CLAUDE.md, orchestrator.md
|   +-- skills/ (6 sub-skills)
+-- agents/
    +-- cadence-{template,timing,copy,lead,correlation}.md
```

### Desinstalar

```bash
chmod +x uninstall.sh
./uninstall.sh
```

---

## Requisitos

| Requisito | Obrigatorio |
|-----------|-------------|
| [Claude Code](https://claude.ai/code) | Sim |
| Dados GS Engage (JSON) | Sim |
| Python 3.9+ | Apenas para gerar PDFs |
| `markdown` + `weasyprint` | Apenas para gerar PDFs |

---

## Licenca

MIT
