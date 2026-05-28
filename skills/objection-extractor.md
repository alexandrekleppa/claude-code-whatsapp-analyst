# Skill: Objection Extractor — Extração e Categorização de Objeções e Sinais

Esta skill identifica objeções, dores e sinais de interesse em texto livre (transcrições de calls, mensagens INCOMING, notas de lead).

---

## Quando é Ativada

Ativada pelos **Agentes 07 (Transcription)** e **11 (Notes Signal)**.

---

## Input Esperado

Lista de textos com metadados:
- `text` — string em pt-BR
- `source` — `transcription_segment` | `lead_note` | `incoming_message`
- `lead_id` (opcional, para correlacionar com outcome)
- `outcome` (opcional — `WON_LEAD` / `DISCARDED` / `IN_PROGRESS`)

---

## Categorias e Heurísticas

### Categorias de OBJEÇÃO
| Categoria | Keywords / padrões |
|---|---|
| `PREÇO` | "caro", "valor", "investimento", "orçamento", "custo", "muito dinheiro", "barato", "desconto" |
| `TIMING` | "agora não", "depois", "mais pra frente", "mês que vem", "ano que vem", "ocupado", "sem tempo", "não é momento" |
| `AUTORIDADE` | "não sou eu", "preciso falar com", "diretor", "sócio", "marketing", "RH", "decide" |
| `NECESSIDADE` | "não precisa", "já temos", "resolvido", "não é prioridade", "não faz sentido" |
| `CONFIANÇA` | "nunca ouvi falar", "quem é vocês", "referências", "garantia", "como funciona mesmo" |
| `CONCORRÊNCIA` | nome de concorrente, "já uso", "já contratei" |

### Categorias de SINAL DE INTERESSE
| Categoria | Keywords / padrões |
|---|---|
| `PEDIU_MATERIAL` | "manda", "envia", "apresentação", "link", "PDF", "case", "deck" |
| `PERGUNTOU_PREÇO` | "quanto", "valor", "investimento", "mensalidade" |
| `AGENDOU` | "marcar", "reunião", "call", "encontro", "amanhã às", "que dia", "horário" |
| `DOR_CONFIRMADA` | "exatamente isso", "é nosso problema", "tenho esse pain", "isso me incomoda" |
| `QUALIFICOU_DECISOR` | "sou o responsável", "eu decido", "minha mesa" |

### Categoria fallback
`OUTROS` — quando nenhuma keyword bate.

---

## Algoritmo

1. **Tokenizar** o texto (lowercase, normalizar acentos).
2. **Match** com cada lista de keywords/padrões (regex simples; aceitar variações).
3. **Atribuir todas as categorias que casarem** (texto pode ter múltiplas).
4. **Frequência** — contar ocorrências por categoria.
5. **Lift por outcome** (quando `outcome` disponível):
   ```
   lift(cat, outcome) = P(outcome | cat presente) / P(outcome global)
   ```
   Lift > 1.5 = forte preditor positivo. Lift < 0.7 = forte preditor negativo.
6. **Amostras** — só emitir veredicto para categorias com ≥ 10 ocorrências.

---

## Output Esperado

```
### Distribuição de Categorias

| Categoria | Tipo | Qtd | % Total | Lift WON | Lift DISC |
| PREÇO | OBJ | X | XX% | 0.6 | 1.4 |
| AGENDOU | SINAL | X | XX% | 2.8 | 0.3 |

### Top 10 Objeções (por frequência)
| Categoria | Qtd | Exemplo verbatim | Outcome típico |

### Top 10 Sinais de Interesse
| Categoria | Qtd | Exemplo verbatim | Outcome típico |

### ⚠️ Categorias com < 10 ocorrências
[...]
```

---

## Notas Técnicas

- pt-BR — toda heurística em português brasileiro.
- Negações ("não é caro") não invertem a categoria; apenas marcam que o tema foi tocado. O agente que consome a skill deve interpretar contexto se quiser polaridade.
- Para volumes muito altos (>10k textos), processar em batch e agregar.
