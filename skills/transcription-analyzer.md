# Skill: Transcription Analyzer — Métricas Estruturais de Transcrição

Esta skill analisa `segments[]` de transcrições VoIP e devolve métricas estruturais (turn-taking, talk-time, interrupções, silêncios).

---

## Quando é Ativada

Ativada pelo **Agente 07 (Transcription Analyst)** e pelo **Agente 10 (Playbook Adherence)** quando precisa analisar tempo de fala da Mariana.

---

## Input Esperado

Para cada call, receber:
- `call_id`
- `segments[]` — cada segmento:
  - `text` — conteúdo falado
  - `speaker` — `sdr` (ou `ai`) ou `lead`
  - `start` — timestamp de início (segundos a partir do início da call)
  - `end` — timestamp de fim
  - `channel` (opcional)

---

## Métricas a Calcular

### 1. Talk Time Ratio
```
sdr_talk_time = soma de (end - start) onde speaker = sdr
lead_talk_time = soma de (end - start) onde speaker = lead
total_talk = sdr_talk_time + lead_talk_time

sdr_talk_ratio = sdr_talk_time / total_talk
```

Reportar:
- `sdr_talk_ratio` (0.0 a 1.0)
- Bucket interpretado:
  - `< 0.4` — SDR fala pouco (lead domina, geralmente bom)
  - `0.4 - 0.6` — equilibrado
  - `0.6 - 0.75` — SDR domina (aceitável em abertura)
  - `> 0.75` — SDR fala demais (red flag)

### 2. Número de Turnos
Contar quantas vezes o speaker muda. Mais turnos = conversa mais dinâmica.

### 3. Duração Média de Turno (por speaker)
Distinguir SDR-monólogo (turnos longos) vs SDR-dialógico (turnos curtos).

### 4. Interrupções
Detectar overlap temporal: quando um segmento de speaker X começa antes do segmento anterior de speaker Y terminar (`X.start < Y.end` para speakers diferentes).

Contar:
- `sdr_interrupts_lead` — SDR começou a falar enquanto lead falava
- `lead_interrupts_sdr` — lead cortou o SDR

### 5. Silêncios > 3s
Detectar gaps entre o fim de um segmento e o início do próximo: `next.start - prev.end > 3`.
Contar quantos e onde (quem deveria estar falando depois).

### 6. Primeiros 30s
Extrair todos os segmentos com `start < 30`. Usado pelo agente 07 para análise de aberturas.

### 7. Últimos 30s
Extrair segmentos finais. Usado para identificar como a call terminou (despedida, objeção final, agendamento).

---

## Output Esperado

Para cada call:

```
### Call [call_id]
- Talk ratio SDR: X.XX (bucket: [equilibrado/...])
- Turnos: X
- Duração média turno SDR: X.Xs | Lead: X.Xs
- Interrupções: SDR→Lead: X | Lead→SDR: X
- Silêncios > 3s: X
- Primeiros 30s — speakers: [sequência de speakers]
- Últimos 30s — speakers: [sequência de speakers]
```

E agregado:

```
### Métricas Agregadas
| Métrica | Mediana | p25 | p75 | p90 |
| Talk ratio SDR | ... | ... | ... | ... |
| Turnos por call | ... | ... | ... | ... |
| Interrupções SDR→Lead | ... | ... | ... | ... |
```

---

## Notas Técnicas

- Speaker labels podem variar (`sdr` / `ai` / `agent` / `0`). Normalizar antes de processar.
- Se `segments[]` estiver vazio ou `transcriptionProcessing != COMPLETED`, retornar `null` para essa call e sinalizar.
- Timestamps em segundos (não milissegundos). Validar amplitude antes de calcular.
