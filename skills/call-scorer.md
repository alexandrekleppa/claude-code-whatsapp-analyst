# Skill: Call Scorer — Score e Classificação de Ligações VoIP

Esta skill calcula, normaliza e rankeia performance de buckets de ligações (por horário, por outcome, por bucket de duração), com penalidade de confiança para amostras pequenas.

---

## Quando é Ativada

Ativada pelo **Agente 06 (Call Analyst)** e também pelo **Agente 08 (Multichannel Cadence)** quando precisa comparar cohorts de call.

---

## Input Esperado

Para cada bucket (ex: "terça 10h-12h" ou "0–30s de duração"), receber:

| Métrica | Descrição |
|---|---|
| `bucket_id` | Identificador (ex: "ter_10_12") |
| `total_calls` | Volume total de chamadas no bucket |
| `success_count` | Chamadas com `status = SUCCESS` |
| `meaningful_count` | Chamadas com `outcome = MEANINGFUL` ou `MEETING_SCHEDULED` |
| `avg_score` | Score médio do `voip_call_analysis` (0.0 a 1.0) |
| `avg_duration_s` | Duração média efetiva em segundos |

---

## Cálculos a Realizar

### 1. Taxas Brutas
```
connect_rate = success_count / total_calls
meaningful_rate = meaningful_count / success_count   (sobre as que conectaram)
```

### 2. Penalidade de Confiança (Wilson Lower Bound, z=1.96)
Aplicar Wilson lower bound em `connect_rate` e `meaningful_rate`:
```
wilson_lower = (p + z²/(2n) - z × sqrt((p(1-p) + z²/(4n)) / n)) / (1 + z²/n)
```
Onde `n = total_calls` para connect_rate e `n = success_count` para meaningful_rate.

### 3. Normalização Min-Max (0–100)
Normalizar dentro do batch:
- `connect_score` = norm(wilson_connect)
- `meaningful_score` = norm(wilson_meaningful)
- `quality_score` = norm(avg_score)

Se `max == min`, atribuir 50 a todos.

### 4. Score Composto
```
score_final = (connect_score × 0.25) + (meaningful_score × 0.45) + (quality_score × 0.30)
```

Pesos refletem que **meaningful** (resultado útil) > **quality** (score do analysis) > **connect** (conexão é só pré-requisito).

### 5. Indicador de Confiança
| Volume | Indicador |
|---|---|
| < 10 | ❌ Insuficiente — não classificar |
| 10–29 | ⚠️ Baixa confiança |
| 30–49 | 🟡 Moderada |
| 50+ | ✅ Alta |

### 6. Classificação
| Classe | Critério |
|---|---|
| **WINNER** | score_final ≥ 70 E confiança ≥ ⚠️ |
| **NEUTRO** | score_final entre 40 e 69 |
| **LOSER** | score_final < 40 E volume ≥ 20 |

---

## Output Esperado

```
### Scoring de Buckets de Call

| Bucket | Vol | Connect | Meaningful | Score análise | Score final | Confiança | Classe |
|---|---|---|---|---|---|---|---|

**Ranking WINNERS**:
1. ...
2. ...

**Ranking LOSERS**:
1. ...
2. ...

**Excluídos por dados insuficientes**: [...]

**Nota metodológica**: Wilson Score Interval (z=1.96), pesos 25/45/30 (connect/meaningful/quality).
```
