# Skill: Funnel Builder — Construção de Funil de Cadência

Esta skill constrói o funil de conversão entre steps de uma rotina de prospecção e identifica gargalos.

---

## Quando é Ativada

Ativada pelos **Agentes 08 (Multichannel Cadence)** e **09 (Lead Journey)**.

---

## Input Esperado

1. **Definição da rotina** (`routine_steps[]`):
   - `step_id`, `step_order`, `day`, `time`, `channel` (CALL / WHATSAPP), `template_or_script`

2. **Execuções** (`executions[]`):
   - `lead_id`, `step_id`, `executed` (bool), `status` (DONE / FAILED / SKIPPED), `executed_at`, `produced_response` (bool — houve INCOMING / call meaningful depois)

3. **Outcomes finais** (`outcomes[]`):
   - `lead_id`, `final_status` (WON_LEAD / DISCARDED / IN_PROGRESS)

---

## Cálculos a Realizar

### 1. Por Step
Para cada step na ordem:
- `n_entered` — quantos leads chegaram a esse step
- `n_executed` — quantos efetivamente executaram (status DONE)
- `n_failed`, `n_skipped`
- `n_responded` — quantos responderam depois desse step e antes do próximo
- `pct_advanced` — `n_entered_next_step / n_entered_this_step`
- `drop_off` — `1 - pct_advanced`

### 2. Identificação de Gargalo
Gargalo = step com **maior `drop_off`** (>20% acima da média) E volume ≥ 10 leads.

### 3. Funnel ASCII
Gerar visualização:
```
Day 0 CALL        ████████████████████ 100 leads
                  ↓ 78% conectaram
Day 0 WHATSAPP    ███████████████░░░░░  78
                  ↓ 35% leram
Day 1 WHATSAPP    ██████░░░░░░░░░░░░░░  27
                  ↓ 18% responderam
Day 2 WHATSAPP    █░░░░░░░░░░░░░░░░░░░   5  ← GARGALO
...
WON_LEAD          ░░░░░░░░░░░░░░░░░░░░   2 (2%)
```

Largura proporcional à `n_entered`. Setas mostram % de avanço. Marcador `← GARGALO` no pior step.

### 4. Conversão Geral
```
overall_conversion = leads com final_status=WON_LEAD / total leads iniciais
```

### 5. Tempo Médio entre Steps
Para cada par (step_n → step_n+1), calcular delta entre `executed_at` real. Comparar com `time` planejado da rotina.

---

## Output Esperado

```
### Funil — Rotina [name]
[Visualização ASCII]

### Métricas por Step
| Order | Step | Canal | Entered | Executed | Failed | Skipped | Responded | % Avançou | Drop-off |

### Gargalo Identificado
**Step**: [nome]
**Drop-off**: XX% (vs média XX%)
**Hipótese**: [...]

### Conversão Geral
- Leads iniciais: X
- WON_LEAD: X (XX%)
- DISCARDED: X (XX%)
- IN_PROGRESS: X (XX%)

### Drift Temporal
| Step | Planejado | Real (mediana) | Drift |

### ⚠️ Steps com < 10 amostras
[...]
```

---

## Notas Técnicas

- Se `n_entered_next_step > n_entered_this_step` (anomalia), reportar erro de integridade.
- Para rotinas com branches (ex: step depende de outcome), tratar como funis paralelos.
- ASCII width = 20 caracteres, escalado proporcionalmente ao maior bucket.
