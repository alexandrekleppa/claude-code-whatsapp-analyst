# Skill: Timing Strategist — Estratégia de Calendário de Disparos

Esta skill transforma dados brutos de timing em uma estratégia acionável de calendário semanal de disparos, com janelas otimizadas para cada dia.

---

## Quando é Ativada

Ativada pelo **Agente 02 (Timing Analyst)** após o cálculo de todas as métricas de timing.

---

## Input Esperado

| Dado | Formato |
|------|---------|
| Heatmap de READ rate | Matriz 7 faixas × 7 dias com READ rate (%) |
| Volume por célula | Matriz 7 faixas × 7 dias com volume de envios |
| Tempo médio até leitura | Por faixa de horário (em minutos) |
| READ rate por dia (agregado) | 7 valores (seg–dom) |
| READ rate por faixa (agregado) | 7 valores (uma por faixa) |

---

## Análise a Realizar

### 1. Identificar Top 3 Janelas de Envio

Critérios de ranking (em ordem de prioridade):
1. **READ rate** — principal indicador (peso 60%)
2. **Tempo até leitura** — quanto menor, melhor (peso 25%)
3. **Volume histórico** — preferir janelas já testadas com 10+ amostras (peso 15%)

Para cada célula da matriz (faixa × dia):
```
score_janela = (read_rate_normalizado × 0.6) + (velocidade_normalizada_invertida × 0.25) + (volume_normalizado × 0.15)
```

Selecionar as 3 janelas com maior score que tenham pelo menos 10 amostras.

Se nenhuma janela atingir 10 amostras, sinalizar e usar as melhores disponíveis com nota de baixa confiança.

### 2. Identificar Top 3 Janelas a Evitar

Mesma lógica invertida: as 3 janelas com menor score e pelo menos 10 amostras.

### 3. Regras de Bom Senso

Aplicar as seguintes regras antes de finalizar o calendário. Se os dados contradisem essas regras, **os dados vencem** — mas sinalizar a anomalia:

| Regra padrão | Ajuste se dados contradizem |
|-------------|----------------------------|
| Evitar envios na madrugada (00–06h) | Se READ rate for alto nessa faixa, sinalizar como anomalia e recomendar teste com cuidado |
| Evitar segunda-feira de manhã cedo (06–09h) | Se dados mostrarem boa performance, incluir com nota |
| Evitar sexta-feira à tarde (14–18h) | Se dados mostrarem boa performance, incluir com nota |
| Preferir horário comercial (09–18h) | Se fora do horário for melhor, recomendar teste gradual |
| Não enviar aos domingos | Se dados mostrarem boa performance, sinalizar como surpresa e recomendar teste pequeno |
| Concentrar volume nos dias úteis | Dados decidem a distribuição |

### 4. Distribuição de Volume

Com base nas janelas otimizadas, sugerir como distribuir o volume semanal:

- Se o volume total semanal é X, quanto alocar em cada janela?
- Regra: nunca colocar mais de 40% do volume numa única janela (diversificação)
- Priorizar as top 3 janelas mas manter 20-30% em janelas "exploratórias" para continuar coletando dados

---

## Output Esperado

```
### Estratégia de Timing — Calendário Semanal Otimizado

#### Top 3 Janelas de Envio (Recomendadas)

| Rank | Dia | Faixa | READ rate | Vel. leitura | Score | Volume histórico |
|------|-----|-------|-----------|-------------|-------|-----------------|
| 1 | [dia] | [faixa] | XX% | XXmin | XX | X envios |
| 2 | [dia] | [faixa] | XX% | XXmin | XX | X envios |
| 3 | [dia] | [faixa] | XX% | XXmin | XX | X envios |

**Justificativa**:
- Janela 1: [por que é a melhor — dados + contexto]
- Janela 2: [por que é a segunda — dados + contexto]
- Janela 3: [por que é a terceira — dados + contexto]

#### Top 3 Janelas a Evitar

| Rank | Dia | Faixa | READ rate | Motivo |
|------|-----|-------|-----------|--------|
| 1 | [dia] | [faixa] | XX% | [motivo com dados] |
| 2 | [dia] | [faixa] | XX% | [motivo com dados] |
| 3 | [dia] | [faixa] | XX% | [motivo com dados] |

#### Calendário Semanal

```
              SEGUNDA    TERÇA      QUARTA     QUINTA     SEXTA      SÁBADO     DOMINGO
06-09h       [---]      [---]      [---]      [---]      [---]      [---]      [---]
09-12h       [ENVIAR]   [ENVIAR]   [---]      [ENVIAR]   [---]      [---]      [---]
12-14h       [---]      [---]      [ENVIAR]   [---]      [---]      [---]      [---]
14-18h       [---]      [---]      [---]      [---]      [---]      [---]      [---]
18-22h       [---]      [---]      [---]      [---]      [---]      [---]      [---]

[ENVIAR] = janela recomendada para disparo
[TESTAR] = janela com potencial, testar com volume pequeno
[---]    = não enviar nesta janela
[⚠️]     = evitar especificamente
```

(Ajustar com base nos dados reais — o exemplo acima é apenas formato.)

#### Distribuição de Volume Sugerida

| Janela | % do volume semanal | Motivo |
|--------|---------------------|--------|
| [Dia + Faixa] | XX% | Melhor performance |
| [Dia + Faixa] | XX% | Segunda melhor |
| [Dia + Faixa] | XX% | Terceira melhor |
| Exploratório (outras janelas) | XX% | Coletar dados novos |

#### Anomalias Observadas

[Listar qualquer padrão que contradiz as regras de bom senso.
Ex: "Domingos 09-12h têm READ rate de 72%, acima da média semanal de 54%.
Recomendação: testar com 10% do volume por 2 semanas antes de escalar."]

→ O que fazer com isso: implementar este calendário no GS Engage.
Reavaliar em 2 semanas com os novos dados para confirmar que as janelas otimizadas mantêm performance.
```
