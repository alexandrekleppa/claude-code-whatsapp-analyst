# Sales Analyst — Sistema de Análise de Cadência de Prospecção

Este projeto analisa mensagens de WhatsApp exportadas do GS Engage (growthstation.app) para otimizar cadências de prospecção B2B.

## Estrutura do Projeto

```
sales-analyst/
├── CLAUDE.md              ← Este arquivo (regras globais)
├── orchestrator.md        ← Agente orquestrador principal
├── agents/                ← Agentes especializados de análise
│   ├── 01-template-analyst.md
│   ├── 02-timing-analyst.md
│   ├── 03-copy-analyst.md
│   ├── 04-lead-analyst.md
│   └── 05-correlation-hunter.md
├── skills/                ← Skills compartilhadas entre agentes
│   ├── copywriter.md
│   ├── data-scorer.md
│   ├── pattern-detector.md
│   ├── timing-strategist.md
│   ├── lead-profiler.md
│   └── hypothesis-generator.md
├── input/
│   └── whatsapp-conversations/   ← JSONs exportados do GS Engage
└── output/
    └── reports/                  ← Relatórios gerados
```

---

## Schema dos Dados de Entrada (GS Engage)

Cada registro no JSON representa uma mensagem de WhatsApp com os seguintes campos:

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

O orquestrador DEVE disparar todos os 5 subagentes em paralelo usando `Task()`. Nunca rodar agentes em sequência. A única exceção é a síntese final, que depende dos resultados de todos os agentes.

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
