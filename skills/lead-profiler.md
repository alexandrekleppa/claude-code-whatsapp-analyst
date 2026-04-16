# Skill: Lead Profiler — Perfil do Lead Ideal

Esta skill constrói o perfil do lead ideal com base nos dados reais de quem respondeu às cadências de prospecção, e gera critérios de priorização para próximos disparos.

---

## Quando é Ativada

Ativada pelo **Agente 04 (Lead & DDD Analyst)** após calcular métricas de performance por região.

---

## Input Esperado

Dois grupos de dados para comparação:

### Grupo A — Leads que avançaram (responderam)
Para cada Thread ID que teve pelo menos 1 mensagem INCOMING:

| Campo | Descrição |
|-------|-----------|
| `thread_id` | ID da thread |
| `ddd` | DDD extraído do número do lead |
| `first_template` | Template Name da primeira mensagem OUTGOING |
| `first_contact_hour` | Hora do primeiro contato (faixa de horário) |
| `first_contact_day` | Dia da semana do primeiro contato |
| `time_to_response_min` | Tempo em minutos entre primeiro contato e primeira resposta |
| `outgoing_count_before_response` | Nº de mensagens OUTGOING antes da primeira INCOMING |
| `total_outgoing` | Total de mensagens OUTGOING na thread |
| `lead_profile_name` | Nome do lead (do Metadata, se disponível) |

### Grupo B — Leads que NÃO avançaram
Mesmos campos, mas para threads sem nenhuma mensagem INCOMING.
Para esses, `time_to_response_min` e `outgoing_count_before_response` não se aplicam.

---

## Análise a Realizar

### 1. Comparação de Distribuições

Para cada variável, comparar a distribuição entre Grupo A (responderam) e Grupo B (não responderam):

**DDD / Região**:
- Quais DDDs têm proporcionalmente mais leads no Grupo A vs. Grupo B?
- Calcular: `% do DDD no Grupo A` vs `% do DDD no Grupo B`
- Um DDD é "favorável" se sua representação no Grupo A é significativamente maior que no Grupo B

**Template do primeiro contato**:
- Qual template está mais presente no Grupo A?
- Calcular taxa de conversão por template: `leads Grupo A com template X / total de leads com template X`

**Horário do primeiro contato**:
- Qual faixa de horário domina no Grupo A?
- Calcular taxa de conversão por faixa

**Dia da semana**:
- Qual dia da semana domina no Grupo A?
- Calcular taxa de conversão por dia

**Posição na cadência**:
- Leads do Grupo A respondem mais na 1ª, 2ª ou 3ª tentativa?
- Média de `outgoing_count_before_response` no Grupo A
- A partir de qual tentativa a taxa de resposta incremental cai para quase zero?

### 2. Construção do Perfil Ideal

Com base nas análises acima, descrever o "lead ideal" como um conjunto de atributos que maximizam a chance de resposta.

Formato:
```
O lead com maior probabilidade de responder tem:
- DDD: [lista dos melhores DDDs]
- Contactado com: template [nome]
- No horário: [faixa]
- No dia: [dia da semana]
- Responde geralmente na: [Xª tentativa]
- Tempo típico de resposta: [X horas/min]
```

### 3. Score de Priorização

Criar um sistema de pontuação para priorizar leads antes do disparo:

| Critério | Condição | Pontos |
|----------|----------|--------|
| DDD favorável | DDD está no top 5 de response rate | +X pontos |
| DDD desfavorável | DDD está no bottom 5 | -X pontos |
| Já teve interação | Thread tem histórico de INCOMING | +X pontos |
| Sem interação após 3+ tentativas | 3+ OUTGOING sem INCOMING | -X pontos |

Os pontos devem ser proporcionais ao impacto observado nos dados. O critério de maior impacto na taxa de conversão ganha mais pontos.

### 4. Segmentos a Deprioritizar

Identificar combinações de atributos que consistentemente NÃO convertem:

- DDDs com 0% de response rate e volume > 20
- Templates com 0% de response rate e volume > 20
- Faixas de horário com performance muito abaixo da média
- Leads com 4+ tentativas sem resposta

Para cada segmento, calcular o "custo de oportunidade": quantos envios estão sendo desperdiçados.

---

## Output Esperado

```
### Perfil do Lead Ideal

#### Características do lead que responde:
- **Região**: DDDs [X, Y, Z] (representam XX% dos respondentes mas apenas YY% do total)
- **Primeiro contato**: template [nome] (taxa de conversão XX% vs média de YY%)
- **Horário**: [faixa] (taxa de conversão XX% vs média de YY%)
- **Dia**: [dia] (taxa de conversão XX% vs média de YY%)
- **Cadência**: responde na [Xª] tentativa em média (XX% na 1ª, YY% na 2ª, ZZ% na 3ª+)
- **Velocidade**: tempo médio de resposta [X horas] (mediana: [Y horas])

#### Score de Priorização

| Critério | Condição favorável | Pontos | Impacto observado |
|----------|--------------------|--------|-------------------|
| Região | DDD em [X, Y, Z] | +X | +XX pp em response rate |
| Template 1º contato | [template nome] | +X | +XX pp |
| Horário | [faixa] | +X | +XX pp |
| Dia | [dia] | +X | +XX pp |
| Histórico | Já respondeu antes | +X | +XX pp |
| Saturação | 3+ tentativas sem resposta | -X | -XX pp |

**Como usar**: somar pontos para cada lead. Priorizar leads com score mais alto para o próximo batch.
- Score > X: prioridade alta — disparar primeiro
- Score X a Y: prioridade média — disparar no volume restante
- Score < Y: deprioritizar — considerar remover da cadência

#### Segmentos a Deprioritizar

| Segmento | Volume atual | Response rate | Custo de oportunidade | Recomendação |
|----------|-------------|---------------|-----------------------|-------------|
| [descrição] | X envios | 0% | X envios desperdiçados | Remover da cadência |
| [descrição] | X envios | X% | X envios desperdiçados | Reduzir volume |

→ O que fazer com isso: aplicar o score de priorização como filtro antes dos próximos disparos.
Leads com score negativo devem ser removidos ou movidos para uma cadência de baixa prioridade.
Redirecionar o volume economizado para leads de score alto.
```
