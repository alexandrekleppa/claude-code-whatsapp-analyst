# Skill: Data Scorer — Cálculo e Normalização de Scores de Templates

Esta skill é responsável por calcular, normalizar e rankear scores de performance de templates de mensagens WhatsApp, garantindo comparação justa entre templates com volumes diferentes.

---

## Quando é Ativada

Ativada pelo **Agente 01 (Template Analyst)** antes da classificação WINNER/NEUTRO/LOSER. Recebe métricas brutas e retorna scores normalizados com indicador de confiança.

---

## Input Esperado

Para cada template, você receberá:

| Métrica | Descrição |
|---------|-----------|
| `template_name` | Nome do template |
| `read_rate` | Taxa de leitura (0.0 a 1.0) |
| `response_rate` | Taxa de resposta (0.0 a 1.0) |
| `avg_read_speed_min` | Velocidade média de leitura em minutos |
| `volume` | Número total de envios OUTGOING |
| `delivered_count` | Mensagens que chegaram (READ + DELIVERED) |

---

## Cálculos a Realizar

### 1. Normalização dos Scores (0–100)

Normalizar cada métrica para a escala 0–100 usando normalização min-max relativa ao batch:

```
score_normalizado = ((valor - min_do_batch) / (max_do_batch - min_do_batch)) × 100
```

Se `max == min` (todos os valores iguais), atribuir 50 a todos.

Aplicar para:
- READ rate → `read_score` (0–100)
- Response rate → `response_score` (0–100)
- Velocidade de leitura → `speed_score` (0–100) — INVERTER: menor tempo = maior score

### 2. Penalidade de Confiança (Wilson Score Interval)

Para templates com poucas amostras, o READ rate e response rate brutos são pouco confiáveis. Aplicar o **lower bound do intervalo de confiança de Wilson** com z = 1.96 (95% de confiança).

Fórmula do Wilson Score Lower Bound:

```
wilson_lower = (p + z²/(2n) - z × sqrt((p(1-p) + z²/(4n)) / n)) / (1 + z²/n)

onde:
  p = proporção observada (ex: read_rate)
  n = número de observações (ex: delivered_count)
  z = 1.96 (para 95% de confiança)
```

Usar `wilson_lower` em vez do `p` bruto para:
- READ rate → calcular `read_rate_adjusted`
- Response rate → calcular `response_rate_adjusted`

Isso automaticamente penaliza templates com poucas amostras.

### 3. Score Composto Final

```
score_final = (read_rate_adjusted_norm × 0.4) + (response_rate_adjusted_norm × 0.4) + (speed_score_norm × 0.2)
```

Onde:
- `read_rate_adjusted_norm` = normalização 0-100 do `read_rate` ajustado por Wilson
- `response_rate_adjusted_norm` = normalização 0-100 do `response_rate` ajustado por Wilson
- `speed_score_norm` = normalização 0-100 da velocidade (invertida)

Pesos:
- **40% READ rate** — métrica mais confiável e de maior volume
- **40% Response rate** — métrica de maior valor (conversão real)
- **20% Velocidade** — indicador de engajamento, menor peso por ter mais ruído

### 4. Indicador de Confiança

| Volume | Indicador |
|--------|-----------|
| < 10 | ❌ **Insuficiente** — não classificar |
| 10–29 | ⚠️ **Baixa confiança** — classificar com ressalva |
| 30–49 | 🟡 **Confiança moderada** |
| 50+ | ✅ **Alta confiança** |

---

## Output Esperado

```
### Scoring de Templates

| Template | Volume | READ rate bruto | READ rate Wilson | Resp. rate bruto | Resp. rate Wilson | Vel. média | Score Final | Confiança |
|----------|--------|-----------------|------------------|------------------|-------------------|------------|-------------|-----------|
| [nome]   | X      | XX%             | XX%              | XX%              | XX%               | XXmin      | XX/100      | ✅/⚠️/🟡/❌ |

**Ranking por Score Final** (apenas templates com confiança ≥ ⚠️):
1. [template] — Score: XX/100
2. [template] — Score: XX/100
3. [template] — Score: XX/100
...

**Templates excluídos por dados insuficientes** (< 10 amostras):
- [template] — X amostras — READ rate bruto: XX% (não confiável)

**Nota metodológica**: Scores ajustados por Wilson Score Interval (z=1.96, 95% IC).
Templates com menos amostras são penalizados automaticamente, garantindo que rankings
reflitam performance real e não artefatos de baixo volume.
```

---

## Notas Técnicas

- Se um template tem 0 respostas e 0 leituras, o Wilson lower bound é 0 — score final será muito baixo, como esperado.
- A velocidade de leitura deve ser invertida antes da normalização: se a média de leitura é 120min (lento), o speed_score deve ser baixo; se é 5min (rápido), deve ser alto.
- Para a inversão: `speed_score_raw = max_speed_do_batch - avg_read_speed`, depois normalizar.
- Templates sem dados de velocidade (nenhum READ) devem receber speed_score = 0.
