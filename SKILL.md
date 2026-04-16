# Sales Analysis — Análise de Cadência de Prospecção B2B

Você é o ponto de entrada do sistema de análise de cadências de prospecção B2B via WhatsApp para o Claude Code.

## Comando

| Comando | Descrição |
|---------|-----------|
| `/sales-analysis` | Executa análise completa da cadência de prospecção — 5 agentes em paralelo |

## Lógica de Roteamento

Quando o usuário invocar `/sales-analysis`:

1. **Leia as regras globais** em `~/.claude/skills/sales-analysis/CLAUDE.md` — contém o schema dos dados, regras de amostras mínimas, tom dos relatórios, padrões de header/footer, e regra de versionamento de arquivos.

2. **Leia e execute o orquestrador** em `~/.claude/skills/sales-analysis/orchestrator.md` — ele contém o fluxo completo de 6 passos: carregar dados, filtrar por datas, disparar os 5 agentes em paralelo, aguardar resultados, compilar síntese executiva e salvar relatórios.

3. **Siga as instruções do orquestrador à risca.** O SKILL.md é apenas o ponto de entrada. Toda a lógica de análise, coordenação de agentes e geração de relatórios está no orquestrador.

## Localização dos Arquivos

Após instalação, os arquivos ficam em:

```
~/.claude/skills/sales-analysis/
├── SKILL.md              ← Este arquivo (entry point)
├── CLAUDE.md             ← Regras globais do sistema
├── orchestrator.md       ← Orquestrador (fluxo principal de 6 passos)
├── skills/               ← Skills compartilhadas entre agentes
│   ├── copywriter.md
│   ├── data-scorer.md
│   ├── pattern-detector.md
│   ├── timing-strategist.md
│   ├── lead-profiler.md
│   └── hypothesis-generator.md

~/.claude/agents/
├── cadence-template.md       ← Agente 01: Template Analyst
├── cadence-timing.md         ← Agente 02: Timing Analyst
├── cadence-copy.md           ← Agente 03: Copy & Angle Analyst
├── cadence-lead.md           ← Agente 04: Lead & DDD Analyst
└── cadence-correlation.md    ← Agente 05: Correlation Hunter
```

## Diretórios de Trabalho

O orquestrador espera encontrar os dados e salvar relatórios nos seguintes diretórios relativos ao projeto do usuário:

- **Input**: `input/whatsapp-conversations/` — JSONs exportados do GS Engage
- **Output**: `output/reports/` — relatórios gerados

Se esses diretórios não existirem, crie-os antes de prosseguir.
