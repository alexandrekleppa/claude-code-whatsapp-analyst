# Skill: Playbook Adherence — Aderência do Agente AI ao Playbook

Esta skill compara mensagens/falas reais do agente AI com o playbook definido em `wellz_ai_agents.json` e produz score de aderência + lista de violações.

---

## Quando é Ativada

Ativada pelo **Agente 10 (Playbook Adherence Analyst)**.

---

## Input Esperado

1. **Playbook estruturado** (extraído de `wellz_ai_agents.json`):
   - `persona_name` (ex: "Mariana")
   - `company_name` (ex: "Wellz")
   - `intent` (ex: qualification)
   - `approach` (ex: reactivation)
   - `pains[]` — `{description, resolution, keywords}`
   - `opening_template` — estrutura esperada de abertura (extraída do `additionalContext` / `description`)
   - `guardrails[]` — lista de regras (ex: "não prometer desconto", "não interromper")
   - `spin_enabled` (bool)

2. **Amostras**:
   - `conversation_samples[]` — primeiras N mensagens OUTGOING de uma conversa
   - `call_samples[]` — primeiros segmentos com `speaker=sdr` de uma call

---

## Cálculos a Realizar

### 1. Score de Aderência à Abertura (por conversa/call)
Checklist de elementos esperados na abertura:
- [ ] Saudação ("Olá", "Oi", "Bom dia/tarde")
- [ ] Apresentação com nome da persona ("Mariana")
- [ ] Menção do nome da empresa
- [ ] Vocativo personalizado (primeiro nome do lead)
- [ ] Gancho/motivo do contato
- [ ] Pergunta aberta (não yes/no)

Score = (itens presentes / 6) × 100.

### 2. Cobertura de Pains
Para cada `pain.keywords[]`, contar ocorrências em todas as mensagens/falas do agente.
- `pain_coverage[pain_id] = n_ocorrencias`
- Pain "morta" se `n_ocorrencias = 0`.
- Pain "viva forte" se `n_ocorrencias / total_amostras > 0.10`.

### 3. Violações de Guardrails
Para cada guardrail, definir detector:
| Guardrail | Detector |
|---|---|
| Não prometer desconto | regex: `desconto|brinde|grátis|free` + contexto positivo |
| Não interromper | (vem do `transcription-analyzer`: `sdr_interrupts_lead > 2`) |
| Não falar de funcionalidades antes da dor | menção a `feature/funcionalidade` antes de qualquer pain keyword na mesma conversa |
| Não pressionar | regex: `precisa decidir agora\|última chance\|tem que ser hoje` |

Contar violações + capturar trecho verbatim.

### 4. Aderência SPIN (calls)
Se `spin_enabled = true`, verificar presença de:
- **S (Situation)**: perguntas sobre contexto atual ("como vocês fazem hoje", "quantos colaboradores")
- **P (Problem)**: perguntas sobre dor ("qual o maior desafio", "o que incomoda")
- **I (Implication)**: perguntas sobre consequência ("e isso impacta como")
- **N (Need-payoff)**: perguntas sobre solução ideal ("e se resolvesse isso")

Por call, marcar quais etapas apareceram.

### 5. Consistência da Persona
Verificar uso consistente do nome da persona, saudação padrão, despedida padrão. Detectar variações.

---

## Output Esperado

```
### Aderência Geral
- Conversas analisadas: X
- Calls analisadas: X
- Score médio de abertura: XX/100
- Distribuição:
  - Total (90-100): XX%
  - Parcial (50-89): XX%
  - Nula (<50): XX%

### Cobertura de Pains
| Pain | Ocorrências | Status |
| pain A | X | ✅ Viva forte |
| pain B | X | 🟡 Viva fraca |
| pain C | 0 | 💀 Morta |

### Violações de Guardrails
| Guardrail | Qtd | % Conversas | Exemplo verbatim |

### SPIN Coverage (calls)
| Etapa | % calls presente |
| S | XX% |
| P | XX% |
| I | XX% |
| N | XX% |

### Consistência da Persona
[Variações detectadas]

### Itens Críticos para o Prompt do Agente
1. [trecho a adicionar/remover do prompt]
2. ...
```

---

## Notas Técnicas

- Heurísticas em pt-BR. Tolerar variações ortográficas e gírias.
- Se playbook não definir explicitamente guardrails, derivar do `additionalContext` (instruções negativas como "não faça X").
- Detectores baseados em regex podem ter falsos positivos — sempre acompanhar com exemplo verbatim para validação humana.
