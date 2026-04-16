# Arquitetura do Sistema — Sales Analyst

Este documento explica o que cada componente do sistema faz e como eles se comunicam entre si.

---

## Visão Geral

O Sales Analyst é um sistema de análise de cadência de prospecção B2B via WhatsApp. Ele é composto por **prompts em markdown** que instruem o Claude a agir como 5 analistas especializados trabalhando em paralelo.

**Não é código tradicional** — são instruções estruturadas que transformam o Claude em uma máquina de análise de dados de prospecção.

### Fluxo resumido

```
JSON do GS Engage → Orquestrador → 5 Agentes (paralelo) → 6 Relatórios
```

---

## Componentes Principais

O sistema tem 3 camadas:

| Camada | Arquivos | Função |
|--------|----------|--------|
| **Orquestrador** | `orchestrator.md` | Coordena tudo: lê dados, pergunta datas, dispara agentes, compila síntese |
| **Agentes** (5) | `agents/*.md` | Analistas especializados que rodam em paralelo |
| **Skills** (6) | `skills/*.md` | Capacidades reutilizáveis que os agentes ativam quando precisam |

---

## O Orquestrador

**Arquivo**: `orchestrator.md`

É o cérebro do sistema. Quando você pede uma análise, ele executa 6 passos em sequência:

| Passo | O que faz |
|-------|-----------|
| 1. Carregar dados | Lê todos os JSONs de `input/whatsapp-conversations/` |
| 2. Filtrar | Pergunta qual intervalo de datas analisar e filtra os registros |
| 3. Disparar agentes | Lança os 5 agentes **em paralelo** via `Task()`, cada um com o dataset completo |
| 4. Aguardar | Espera todos os 5 agentes retornarem seus relatórios |
| 5. Sintetizar | Cruza os achados dos 5 agentes num relatório executivo final |
| 6. Salvar | Grava os 6 relatórios em `output/reports/` (sem sobrescrever existentes) |

---

## Os 5 Agentes

Cada agente recebe o dataset completo e foca em uma dimensão diferente da análise. Todos rodam ao mesmo tempo (em paralelo), sem dependência entre si.

### Agente 01 — Template Analyst

**Arquivo**: `agents/01-template-analyst.md`
**Pergunta que responde**: "Quais templates de mensagem estão funcionando e quais devem ser eliminados?"

**O que faz**:
- Agrupa mensagens por `Template Name`
- Calcula 4 métricas por template:
  - **READ rate** — % de mensagens lidas (READ / (READ + DELIVERED))
  - **Response rate** — % de threads que geraram resposta do lead
  - **Velocidade de leitura** — quanto tempo entre envio e leitura
  - **Volume** — quantas mensagens foram enviadas com aquele template
- Classifica cada template:
  - **WINNER**: READ rate > 60% ou response rate > 15%
  - **NEUTRO**: READ rate entre 30-60%
  - **LOSER**: READ rate < 30% ou sem respostas com volume > 20
- Para cada LOSER, gera uma reescrita sugerida

**Skills que ativa**:
- `data-scorer` — normaliza métricas em score 0-100 com intervalo de confiança
- `copywriter` — reescreve os templates LOSERs

---

### Agente 02 — Timing Analyst

**Arquivo**: `agents/02-timing-analyst.md`
**Pergunta que responde**: "Qual o melhor dia e horário para disparar mensagens?"

**O que faz**:
- Divide o dia em 7 faixas horárias (madrugada, manhã cedo, comercial manhã, almoço, comercial tarde, noite, noite tarde)
- Calcula READ rate para cada combinação de **faixa horária x dia da semana** (matriz 7x7)
- Mede o tempo médio entre envio e leitura por faixa
- Identifica as 3 melhores janelas para enviar e as 3 piores
- Gera um calendário semanal otimizado de disparos

**Skill que ativa**:
- `timing-strategist` — transforma o heatmap em calendário acionável com distribuição de volume

---

### Agente 03 — Copy & Angle Analyst

**Arquivo**: `agents/03-copy-analyst.md`
**Pergunta que responde**: "Qual ângulo de copy gera mais engajamento?"

**O que faz**:
- Classifica cada mensagem em 1 dos 6 ângulos de copy:
  1. **Prova Social** — "pessoas com perfil parecido com o seu..."
  2. **Exclusividade/Seleção** — "sua conta chamou atenção..."
  3. **Urgência/Escassez** — "não deixar essa oportunidade passar..."
  4. **Curiosidade/Mistério** — "identifiquei uma possível otimização..."
  5. **Direto/Consultivo** — pergunta direta sobre a situação do lead
  6. **Reciprocidade** — "separei opções para você..."
- Rankeia os ângulos por READ rate e response rate
- Identifica quais ângulos dominam nos WINNERs vs LOSERs
- Monta o "DNA da mensagem vencedora" (checklist de elementos de alta performance)
- Gera 3 novas variações de mensagem para teste A/B

**Skills que ativa**:
- `pattern-detector` — analisa padrões linguísticos e estruturais
- `copywriter` — gera 3 novas variações de mensagem

---

### Agente 04 — Lead & DDD Analyst

**Arquivo**: `agents/04-lead-analyst.md`
**Pergunta que responde**: "Quais regiões e perfis de lead respondem melhor?"

**O que faz**:
- Extrai o DDD do número de telefone de cada lead (+55**11**985718882 → DDD 11 = São Paulo)
- Calcula READ rate, response rate e tempo de resposta **por DDD/região**
- Identifica quais prospecções avançaram (lead respondeu após o contato)
- Mapeia padrões dos leads que respondem vs. os que não respondem
- Constrói o perfil do "lead ideal" com critérios mensuráveis
- Gera um score de priorização para próximos disparos

**Skill que ativa**:
- `lead-profiler` — constrói o perfil do lead ideal e identifica segmentos a deprioritizar

---

### Agente 05 — Correlation Hunter

**Arquivo**: `agents/05-correlation-hunter.md`
**Pergunta que responde**: "Que correlações ocultas existem nos dados que ninguém procurou?"

**O que faz**:
- Testa 6 hipóteses pré-carregadas:
  1. Leitura rápida (< 30min) prevê resposta?
  2. Dias de alto volume (> 50 envios) têm READ rate menor? (saturação)
  3. Certos templates funcionam melhor em certas regiões? (DDD x Template)
  4. Primeira mensagem performa melhor que follow-ups? (posição na cadência)
  5. Mensagens curtas performam melhor que longas? (tamanho)
  6. Leads com histórico de conversa respondem mais? (reutilização de thread)
- Cada hipótese recebe veredicto: Confirmada, Refutada ou Inconclusiva
- Tem liberdade para explorar padrões adicionais além das 6 hipóteses
- Gera 3 novas hipóteses para testar no próximo ciclo

**Skills que ativa**:
- `hypothesis-generator` — gera 3 novas hipóteses a partir de sinais fracos
- `pattern-detector` — análise complementar de padrões linguísticos (quando necessário)

---

## As 6 Skills

Skills são **capacidades reutilizáveis** compartilhadas entre agentes. Um agente "ativa" uma skill lendo o arquivo e seguindo suas instruções. Pense nelas como ferramentas especializadas que os agentes pegam emprestadas quando precisam.

### Copywriter

**Arquivo**: `skills/copywriter.md`
**Usada por**: Agentes 01 e 03

Tem dois modos de operação:

| Modo | Quando | O que faz |
|------|--------|-----------|
| **Reescrita** | Ativado pelo Agente 01 | Recebe templates LOSERs + 2 WINNERs de referência. Reescreve o LOSER seguindo regras rígidas de copy. |
| **Geração** | Ativado pelo Agente 03 | Recebe o ângulo vencedor + DNA da mensagem. Cria 3 variações novas para A/B test. |

Regras de copy que a skill impõe:
- Máximo 3 frases (gancho + contexto + CTA)
- Nome próprio obrigatório no início
- CTA sempre em formato de pergunta
- Tom conversacional (nunca vendedor)
- Palavras proibidas: "oportunidade", "solução", "alavancar", "imperdível", etc.
- Entre 100 e 250 caracteres

---

### Data Scorer

**Arquivo**: `skills/data-scorer.md`
**Usada por**: Agente 01

Normaliza métricas brutas em scores comparáveis de 0 a 100, corrigindo distorções de volume.

| Etapa | O que faz |
|-------|-----------|
| Normalização | Converte READ rate, response rate e velocidade para escala 0-100 (min-max) |
| Wilson Score | Aplica intervalo de confiança de Wilson para penalizar templates com poucas amostras |
| Score composto | Combina: 40% READ rate + 40% response rate + 20% velocidade |
| Confiança | Classifica: < 10 amostras = insuficiente, 10-29 = baixa, 30-49 = moderada, 50+ = alta |

---

### Pattern Detector

**Arquivo**: `skills/pattern-detector.md`
**Usada por**: Agentes 03 e 05

Analisa padrões linguísticos e estruturais nas mensagens para encontrar o que diferencia mensagens de alta performance.

| Análise | O que faz |
|---------|-----------|
| Métricas estruturais | Conta palavras, caracteres, frases, presença de nome, CTA em pergunta, emojis, etc. |
| Correlação com performance | Para cada elemento, calcula o impacto em READ rate e response rate |
| Comprimento ideal | Identifica a faixa de caracteres com melhor performance |
| Palavras de alta/baixa performance | Lista as 10 palavras mais associadas a WINNERs e LOSERs |
| Análise do gancho | Examina a primeira frase: tamanho, formato, palavras usadas |

O output principal é o **"DNA da mensagem vencedora"** — uma checklist de elementos que toda mensagem deveria ter.

---

### Timing Strategist

**Arquivo**: `skills/timing-strategist.md`
**Usada por**: Agente 02

Transforma dados de timing em estratégia acionável.

| Etapa | O que faz |
|-------|-----------|
| Ranking de janelas | Calcula score por célula (dia x horário): 60% READ rate + 25% velocidade + 15% volume |
| Top 3 / Bottom 3 | Identifica as 3 melhores e 3 piores janelas para enviar |
| Regras de bom senso | Cruza dados com regras padrão (ex: evitar madrugada). Se os dados contradizem a regra, os dados vencem |
| Distribuição de volume | Sugere como distribuir os envios semanais entre as janelas (máx 40% numa única janela) |
| Calendário visual | Gera grade semanal com marcações: ENVIAR / TESTAR / EVITAR |

---

### Lead Profiler

**Arquivo**: `skills/lead-profiler.md`
**Usada por**: Agente 04

Constrói o perfil do lead ideal comparando leads que responderam vs. os que não responderam.

| Etapa | O que faz |
|-------|-----------|
| Comparação de grupos | Compara distribuição de DDD, template, horário, dia e posição na cadência entre respondentes vs. não-respondentes |
| Perfil ideal | Descreve o lead com maior probabilidade de responder (região, template, horário, dia, tentativa) |
| Score de priorização | Cria sistema de pontos para classificar leads antes do disparo (DDD favorável +X, saturado -X, etc.) |
| Segmentos a cortar | Identifica combinações que nunca convertem e calcula o custo de oportunidade |

---

### Hypothesis Generator

**Arquivo**: `skills/hypothesis-generator.md`
**Usada por**: Agente 05

Gera novas hipóteses a partir de sinais fracos nos dados que ninguém procurou explicitamente.

| Etapa | O que faz |
|-------|-----------|
| Procurar sinais fracos | Busca distribuições assimétricas, outliers, padrões minoritários, tendências temporais, efeitos de sequência |
| Formular hipóteses | Para cada sinal: hipótese testável + evidência + experimento + impacto estimado + tempo para validar |
| Priorizar | Ordena por impacto x facilidade de teste |

Cada hipótese deve ser falsificável, acionável, baseada em evidência, diferente das 6 pré-carregadas e específica.

---

## Como os Componentes se Comunicam

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ORQUESTRADOR                                │
│  orchestrator.md                                                    │
│                                                                     │
│  1. Lê JSONs de input/                                              │
│  2. Pergunta intervalo de datas ao usuário                          │
│  3. Filtra e valida os dados                                        │
│  4. Dispara 5 Task() em paralelo ─────────────────────────┐        │
│                                                            │        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │        │
│  │  Agente 01   │  │  Agente 02   │  │  Agente 03   │     │        │
│  │  Template     │  │  Timing      │  │  Copy &      │     │        │
│  │  Analyst      │  │  Analyst     │  │  Angle       │     │        │
│  │              │  │              │  │              │     │        │
│  │ ativa:       │  │ ativa:       │  │ ativa:       │     │        │
│  │ • data-scorer│  │ • timing-    │  │ • pattern-   │     │        │
│  │ • copywriter │  │   strategist │  │   detector   │     │        │
│  │              │  │              │  │ • copywriter │     │        │
│  │ output:      │  │ output:      │  │              │     │        │
│  │ relatório    │  │ relatório    │  │ output:      │     │        │
│  │ template     │  │ timing       │  │ relatório    │     │        │
│  └──────┬───────┘  └──────┬───────┘  │ copy         │     │        │
│         │                 │          └──────┬───────┘     │        │
│         │                 │                 │             │        │
│  ┌──────┴───────┐  ┌──────┴───────┐        │             │        │
│  │  Agente 04   │  │  Agente 05   │        │             │        │
│  │  Lead & DDD  │  │  Correlation │        │             │        │
│  │  Analyst     │  │  Hunter      │        │             │        │
│  │              │  │              │        │             │        │
│  │ ativa:       │  │ ativa:       │        │             │        │
│  │ • lead-      │  │ • hypothesis-│        │             │        │
│  │   profiler   │  │   generator  │        │             │        │
│  │              │  │ • pattern-   │        │             │        │
│  │ output:      │  │   detector   │        │             │        │
│  │ relatório    │  │              │        │             │        │
│  │ lead         │  │ output:      │        │             │        │
│  └──────┬───────┘  │ relatório    │        │             │        │
│         │          │ correlation  │        │             │        │
│         │          └──────┬───────┘        │             │        │
│         │                 │                │             │        │
│  5. Recebe 5 relatórios ←─┴─────────────────┘             │        │
│  6. Cruza achados entre agentes                                     │
│  7. Compila relatório executivo final                               │
│  8. Salva 6 arquivos em output/reports/                             │
└─────────────────────────────────────────────────────────────────────┘
```

### Fluxo de dados detalhado

| De | Para | O que passa |
|----|------|-------------|
| Usuário | Orquestrador | Intervalo de datas desejado |
| `input/*.json` | Orquestrador | Mensagens brutas do GS Engage |
| Orquestrador | Cada Agente | Dataset filtrado completo (mesmo dado para todos) |
| Agente 01 | `data-scorer` | Métricas brutas por template → recebe scores normalizados |
| Agente 01 | `copywriter` (modo reescrita) | Templates LOSERs → recebe reescritas |
| Agente 02 | `timing-strategist` | Heatmap de READ rate → recebe calendário otimizado |
| Agente 03 | `pattern-detector` | Textos + métricas → recebe DNA da mensagem vencedora |
| Agente 03 | `copywriter` (modo geração) | Ângulo vencedor + DNA → recebe 3 variações novas |
| Agente 04 | `lead-profiler` | Leads que responderam vs. não → recebe perfil ideal + score |
| Agente 05 | `hypothesis-generator` | Resultados das 6 hipóteses → recebe 3 hipóteses novas |
| Agente 05 | `pattern-detector` | Dados para análise complementar (quando necessário) |
| Cada Agente | Orquestrador | Relatório individual em markdown |
| Orquestrador | `output/reports/` | 5 relatórios individuais + 1 relatório executivo |

### Regras de comunicação

1. **Agentes não se comunicam entre si** — cada um recebe o dataset bruto e trabalha independentemente
2. **Skills são ativadas pelos agentes** — o agente lê o arquivo da skill e segue as instruções dela
3. **O orquestrador é o único ponto de integração** — ele cruza os achados dos 5 agentes na síntese final
4. **Tudo roda em paralelo** — os 5 agentes são disparados ao mesmo tempo via `Task()`

---

## Arquivos de Entrada e Saída

### Entrada

```
input/whatsapp-conversations/*.json
```

JSONs exportados do GS Engage. Cada registro é uma mensagem de WhatsApp com campos como `Direction`, `Status`, `Text`, `Template Name`, `Thread ID`, `To`, `From`, `Sent At`, etc.

### Saída

```
output/reports/
├── report-template-YYYY-MM-DD.md    ← Agente 01: classificação de templates
├── report-timing-YYYY-MM-DD.md      ← Agente 02: heatmap + calendário
├── report-copy-YYYY-MM-DD.md        ← Agente 03: ângulos + DNA vencedor + variações
├── report-lead-YYYY-MM-DD.md        ← Agente 04: análise regional + perfil ideal
├── report-correlation-YYYY-MM-DD.md ← Agente 05: hipóteses testadas + novas
└── report-YYYY-MM-DD.md             ← Síntese executiva (cruzamento de todos)
```

Relatórios nunca são sobrescritos — se já existir, recebe sufixo `_v2`, `_v3`, etc.

---

## Outros Arquivos

| Arquivo | Função |
|---------|--------|
| `CLAUDE.md` | Regras globais do sistema: schema dos dados, amostra mínima (10), tom dos relatórios, formato de header/footer |
| `SKILL.md` | Entry point — é o que o Claude lê primeiro quando você pede uma análise |
| `install.sh` | Copia os arquivos para `~/.claude/` para uso global no Claude Code |
| `uninstall.sh` | Remove os arquivos de `~/.claude/` |
| `README.md` | Documentação do projeto com instruções de uso |
