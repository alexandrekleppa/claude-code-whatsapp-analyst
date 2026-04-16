# Skill: Pattern Detector — Análise de Padrões Linguísticos

Esta skill identifica padrões linguísticos e estruturais nas mensagens de WhatsApp de alta performance, gerando um checklist do "DNA da mensagem vencedora".

---

## Quando é Ativada

- **Agente 03 (Copy & Angle Analyst)**: para construir o DNA da mensagem vencedora
- **Agente 05 (Correlation Hunter)**: como skill secundária para análises adicionais de padrões

---

## Input Esperado

Para cada mensagem OUTGOING com `Message Type = "TEMPLATE"`:

| Campo | Descrição |
|-------|-----------|
| `text` | Corpo da mensagem |
| `template_name` | Nome do template |
| `read_rate` | READ rate do template (calculado pelo agente) |
| `response_rate` | Response rate do template |
| `classification` | WINNER / NEUTRO / LOSER (se disponível) |

---

## Análises a Realizar

### 1. Métricas Estruturais por Mensagem

Para cada mensagem, extrair:

| Métrica | Como calcular |
|---------|---------------|
| **Número de palavras** | Contar palavras separadas por espaço |
| **Número de caracteres** | `len(text)` |
| **Número de frases** | Contar separadores: `.`, `!`, `?`, `\n` |
| **Número de parágrafos** | Contar blocos separados por `\n\n` ou `\n` |
| **Presença de nome próprio** | Verificar se `{{firstName}}` ou um nome capitalizado aparece nas primeiras 30 chars |
| **CTA em pergunta** | Última frase termina com `?` |
| **Presença de número/dado** | Regex: presença de dígitos ou "%" no texto |
| **Presença de emoji** | Verificar caracteres emoji |
| **Uso de bullet points** | Presença de `•`, `-` ou `*` como marcadores de lista |
| **Comprimento do gancho** | Número de palavras da primeira frase (até primeiro `.`, `!`, `?` ou `\n`) |

### 2. Correlação de Cada Métrica com Performance

Para cada métrica estrutural, calcular a diferença de performance entre mensagens que possuem o atributo vs. as que não possuem:

```
Impacto em READ rate = READ rate médio (com atributo) - READ rate médio (sem atributo)
Impacto em Response rate = Response rate médio (com atributo) - Response rate médio (sem atributo)
```

Exemplo:
- Mensagens com nome próprio no início: READ rate médio 58%
- Mensagens sem nome próprio no início: READ rate médio 46%
- Impacto: +12 pontos percentuais em READ rate

### 3. Análise de Comprimento Ideal

Dividir mensagens em faixas de comprimento e calcular READ rate por faixa:

| Faixa | Caracteres |
|-------|------------|
| Muito curta | < 100 |
| Curta | 100–150 |
| Média | 150–200 |
| Longa | 200–300 |
| Muito longa | > 300 |

Identificar a faixa com melhor READ rate.

### 4. Análise de Palavras

**Palavras de alta performance (Winners)**:
1. Pegar os textos dos templates WINNER (ou top 25% por READ rate)
2. Tokenizar em palavras (lowercase, remover stopwords comuns do português)
3. Calcular frequência relativa de cada palavra
4. Comparar com a frequência nos templates LOSER (ou bottom 25%)
5. Listar as 10 palavras com maior diferença positiva (mais frequentes nos winners)

**Palavras de baixa performance (Losers)**:
1. Mesmo processo, mas identificar palavras mais frequentes nos losers
2. Listar as 10 palavras com maior diferença negativa

**Stopwords a ignorar** (não informativas):
"a", "o", "e", "é", "de", "do", "da", "em", "um", "uma", "que", "para", "pra", "com", "por", "se", "no", "na", "os", "as", "ao", "dos", "das", "seu", "sua", "você", "vc", "te", "me", "eu", "aqui", "isso", "esse", "essa", "este", "esta", "como", "mais", "mas", "já", "não", "nos", "nas", "bem", "tudo"

### 5. Análise do Gancho (Primeira Frase)

O gancho é a primeira frase da mensagem (até o primeiro `.`, `!`, `?` ou `\n`).

Analisar:
- Comprimento médio do gancho nos winners vs. losers
- Palavras mais comuns no gancho dos winners
- O gancho começa com nome próprio? (correlação com READ rate)
- O gancho faz uma afirmação ou pergunta?

---

## Output Esperado

```
### DNA da Mensagem Vencedora

#### Checklist de Elementos de Alta Performance

| # | Elemento | Presente nos Winners | Presente nos Losers | Impacto READ rate | Impacto Response rate | Recomendação |
|---|----------|---------------------|--------------------|--------------------|----------------------|-------------|
| 1 | Nome próprio no início | XX% | XX% | +XX pp | +XX pp | ✅ Usar sempre |
| 2 | CTA em pergunta | XX% | XX% | +XX pp | +XX pp | ✅ Usar sempre |
| 3 | Corpo 2-3 frases | XX% | XX% | +XX pp | +XX pp | ✅ Preferir |
| 4 | Comprimento 100-200 chars | XX% | XX% | +XX pp | +XX pp | ✅ Preferir |
| 5 | Número/dado concreto | XX% | XX% | +XX pp | +XX pp | 🟡 Testar |
| 6 | Emoji | XX% | XX% | +XX pp | +XX pp | ❌/✅ Depende |
| 7 | Bullet points | XX% | XX% | +XX pp | +XX pp | ❌ Evitar |

(pp = pontos percentuais)

#### Comprimento Ideal

| Faixa | READ rate | Response rate | Volume | Recomendação |
|-------|-----------|---------------|--------|-------------|
| < 100 chars | XX% | XX% | X | ... |
| 100-150 chars | XX% | XX% | X | ... |
| 150-200 chars | XX% | XX% | X | ... |
| 200-300 chars | XX% | XX% | X | ... |
| > 300 chars | XX% | XX% | X | ... |

**Comprimento ótimo**: [faixa] — [justificativa]

#### Gancho Ideal

- Comprimento médio nos winners: X palavras
- Comprimento médio nos losers: X palavras
- Começa com nome próprio nos winners: XX% dos casos
- Gancho em pergunta nos winners: XX% dos casos
- **Recomendação**: [gancho com X-Y palavras, começando com nome, formato declarativo/pergunta]

#### Top 10 Palavras de Alta Performance
1. "[palavra]" — XX% nos winners vs XX% nos losers (delta: +XX pp)
2. ...

#### Top 10 Palavras a Evitar
1. "[palavra]" — XX% nos losers vs XX% nos winners (delta: +XX pp nos losers)
2. ...

→ O que fazer com isso: usar esta checklist como critério de QA para novos templates.
Todo template novo deve passar em pelo menos 5 dos 7 itens antes de entrar em produção.
```
