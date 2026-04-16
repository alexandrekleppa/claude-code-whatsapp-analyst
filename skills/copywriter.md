# Skill: Copywriter — Reescrita e Criação de Mensagens WhatsApp B2B

Esta skill é ativada por agentes que precisam reescrever templates de baixa performance ou criar novas variações de mensagens para cadências de prospecção B2B via WhatsApp.

---

## Contexto

As mensagens são enviadas via WhatsApp para leads B2B de uma assessoria de investimentos (Genial Investimentos / Ritmo Assessoria). O objetivo é agendar uma consultoria gratuita com um assessor. A persona que envia é "Júlia", consultora de investimentos.

---

## Regras de Copy (OBRIGATÓRIAS)

### Estrutura da mensagem

Toda mensagem DEVE seguir esta estrutura em 3 partes:

1. **Gancho** (1 frase) — Primeira frase que captura atenção. Deve ser específica, personalizada ou intrigante.
2. **Contexto** (1 frase) — Conecta o gancho ao motivo do contato. Explica brevemente por que o lead deveria se importar.
3. **CTA** (1 pergunta) — Call-to-action OBRIGATORIAMENTE em formato de pergunta. Deve ser fácil de responder com "sim" ou "não".

### Regras obrigatórias

| Regra | Detalhe |
|-------|---------|
| Máximo 3 frases | Gancho + Contexto + CTA. Sem exceções. |
| Nome próprio no início | Usar `{{firstName}}` na primeira linha. Sempre. |
| CTA em pergunta | Última frase DEVE ser uma pergunta. Nunca imperativo. |
| Tom conversacional | Conversa entre conhecidos, não vendedor vs. cliente. |
| Sem jargões | Proibido: "oportunidade", "solução", "agregar valor", "potencializar", "rentabilidade", "otimizar", "alavancar" |
| Sem urgência falsa | Proibido: pressão explícita, contagem regressiva inventada, escassez artificial |
| Sem emojis excessivos | Máximo 1 emoji por mensagem, e apenas se natural no contexto |
| Sem bullet points | WhatsApp template não suporta bem listas longas. Manter texto corrido. |
| Comprimento ideal | Entre 100 e 200 caracteres. Máximo absoluto: 250 caracteres. |

### Palavras proibidas

Nunca usar estas palavras/expressões nos templates:
- "oportunidade"
- "solução"
- "agregar valor"
- "potencializar"
- "rentabilidade" (substituir por "rendimento" ou "seus investimentos")
- "otimizar" / "otimização"
- "alavancar"
- "imperdível"
- "exclusivo" (quando usado como adjetivo genérico — ok quando factual: "assessor exclusivo")
- "não perca"
- "última chance"

### Palavras recomendadas (alta performance observada)

- "perfil parecido" (prova social)
- "chamou atenção" (exclusividade)
- "conversa rápida" (baixo comprometimento)
- "faz sentido pra você?" (CTA suave)
- "vale a pena" (validação)
- "me conta" (tom consultivo)

---

## Modo 1: Reescrita de Template LOSER

### Quando ativada pelo Agente 01 (Template Analyst)

**Input que você recebe**:
- Texto original do template classificado como LOSER
- Métricas: READ rate, response rate, volume
- Ângulo de copy identificado (se houver)
- 2 exemplos de templates WINNER como referência

**O que fazer**:

1. Analisar o texto original e identificar os problemas:
   - Gancho genérico ou fraco?
   - Muitas frases? Texto longo demais?
   - CTA não é pergunta?
   - Usa palavras proibidas?
   - Tom de vendedor em vez de conversa?
   - Falta de personalização?

2. Analisar os WINNERs de referência:
   - Qual ângulo usam?
   - Qual estrutura seguem?
   - O que os diferencia do LOSER?

3. Reescrever o template seguindo TODAS as regras acima.

4. Justificar cada mudança linha a linha.

**Output esperado**:

```
### Reescrita do Template: [nome]

**Problemas identificados**:
- [problema 1]
- [problema 2]

**Texto original**:
> [texto original]

**Texto reescrito**:
> [texto novo — máximo 3 frases, com {{firstName}}]

**Justificativa linha a linha**:
- **Gancho**: [o que mudou e por quê — referência ao que funciona nos WINNERs]
- **Contexto**: [o que mudou e por quê]
- **CTA**: [o que mudou e por quê — garantir que é pergunta]

**Ângulo utilizado**: [qual ângulo de copy foi aplicado e por que foi escolhido]
```

---

## Modo 2: Geração de Novas Variações

### Quando ativada pelo Agente 03 (Copy & Angle Analyst)

**Input que você recebe**:
- Ângulo vencedor (o que teve melhor READ rate)
- Checklist "DNA da mensagem vencedora" (output da skill pattern-detector)
- Exemplos dos templates com melhor performance

**O que fazer**:

1. Analisar o ângulo vencedor e os padrões do DNA vencedor
2. Criar 3 variações DIFERENTES que:
   - Usam o ângulo vencedor como base
   - Seguem TODAS as regras de copy
   - Incorporam os elementos do DNA vencedor (nome, pergunta CTA, tamanho ideal, etc.)
   - São suficientemente diferentes entre si para funcionar como A/B test
3. Para cada variação, explicar qual aspecto está testando

**Output esperado**:

```
### 3 Novas Variações para A/B Test

**Ângulo base**: [ângulo vencedor]
**Elementos do DNA vencedor aplicados**: [lista]

---

#### Variação 1 — [nome descritivo, ex: "Gancho direto + CTA suave"]
> {{firstName}}, [frase 1 — gancho]
> [frase 2 — contexto]
> [frase 3 — CTA em pergunta]

**O que testa**: [ex: gancho mais curto que o winner atual]
**Diferencial**: [o que é diferente das outras variações]

---

#### Variação 2 — [nome descritivo]
> {{firstName}}, [frase 1 — gancho]
> [frase 2 — contexto]
> [frase 3 — CTA em pergunta]

**O que testa**: [...]
**Diferencial**: [...]

---

#### Variação 3 — [nome descritivo]
> {{firstName}}, [frase 1 — gancho]
> [frase 2 — contexto]
> [frase 3 — CTA em pergunta]

**O que testa**: [...]
**Diferencial**: [...]

---

**Recomendação de teste**: Rodar variações 1 e 3 contra o WINNER atual. Volume mínimo: 50 envios por variação. Duração: 2 semanas. Métrica primária: READ rate. Métrica secundária: response rate.
```

---

## Validação Final

Antes de entregar qualquer texto, faça esta checklist:

- [ ] Tem exatamente 3 frases (gancho + contexto + CTA)?
- [ ] Usa `{{firstName}}` na primeira linha?
- [ ] CTA é uma pergunta?
- [ ] Não contém palavras proibidas?
- [ ] Tom é conversacional (não vendedor)?
- [ ] Tem entre 100 e 250 caracteres?
- [ ] Não tem urgência falsa ou pressão?
- [ ] Não tem mais de 1 emoji?

Se qualquer item falhar, reescrever até passar.
