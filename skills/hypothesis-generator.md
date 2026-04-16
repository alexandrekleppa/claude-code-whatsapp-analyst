# Skill: Hypothesis Generator — Geração de Novas Hipóteses

Esta skill gera novas hipóteses de análise baseadas em sinais fracos nos dados, que não foram cobertas pelas hipóteses pré-carregadas do Agente 05.

---

## Quando é Ativada

Ativada pelo **Agente 05 (Correlation Hunter)** APÓS testar todas as 6 hipóteses pré-carregadas.

---

## Input Esperado

| Dado | Descrição |
|------|-----------|
| Dataset completo | Todas as mensagens do batch filtrado |
| Resultados das 6 hipóteses | Quais foram confirmadas, refutadas, inconclusivas |
| Observações do agente | Padrões incomuns notados durante a análise |

---

## Método de Geração de Hipóteses

### 1. Procurar Sinais Fracos

Explorar os dados buscando:

**Distribuições assimétricas inesperadas**:
- Algum template tem performance muito diferente em horários específicos?
- Algum DDD tem comportamento oposto ao padrão (ex: performa mal com o WINNER e bem com o LOSER)?
- Algum dia da semana tem um pico ou vale que não se explica pelo volume?

**Outliers de alta performance**:
- Alguma combinação específica (template × DDD × horário) tem performance > 2x a média?
- Alguma thread teve interação excepcionalmente longa ou rápida?
- Algum template com poucos envios (< 10) mostra sinais promissores que justificam mais testes?

**Padrões minoritários**:
- Algo que aparece em < 20% dos dados mas com performance muito acima da média
- Subgrupos pequenos que quebram o padrão geral (ex: leads que respondem de madrugada)

**Padrões temporais**:
- O READ rate muda ao longo do período analisado? (tendência crescente ou decrescente?)
- Há diferença entre início e fim do mês?
- Há diferença entre a primeira e a última semana do período?

**Padrões de sequência**:
- Leads que receberam template A seguido de template B respondem mais do que os que receberam A seguido de C?
- A ordem dos templates na cadência importa?

**Padrões de interação**:
- Leads que leem rapidamente (< 5 min) mas não respondem: são diferentes dos que leem devagar e respondem?
- Leads que respondem com mensagens curtas ("sim", "oi") vs. longas: são perfis diferentes?
- Há padrão no `profileName` dos leads que respondem? (ex: nomes que sugerem cargo/profissão)

### 2. Formular Hipóteses

Para cada sinal fraco encontrado, formular uma hipótese testável seguindo RIGOROSAMENTE este formato:

```
- **Hipótese**: [afirmação clara e testável sobre o que pode ser verdade]
- **Evidência nos dados**: [qual dado específico sugere isso — com números]
- **Experimento sugerido**: [como testar no próximo batch — ação concreta]
- **Impacto potencial**: Alto / Médio / Baixo
  - Alto: pode mudar > 10pp em READ rate ou response rate se confirmada
  - Médio: pode mudar 5-10pp
  - Baixo: pode mudar < 5pp ou afetar subgrupo pequeno
- **Tempo para validar**: [estimativa de dias e/ou volume de disparos necessários]
  - Calcular: para ter 10+ amostras por variante com o volume atual de disparos
```

### 3. Critérios de Qualidade

Cada hipótese DEVE:
- Ser **falsificável** (possível provar que é errada com dados)
- Ser **acionável** (se confirmada, leva a uma mudança concreta)
- Ter **evidência nos dados atuais** (não pode ser pura especulação)
- Ser **diferente** das 6 hipóteses pré-carregadas (não repetir o que já foi testado)
- Ser **específica** ("o ângulo X performa melhor no DDD Y" e não "copy importa")

### 4. Priorização

Ordenar as 3 hipóteses por impacto potencial × facilidade de teste:
1. Impacto Alto + Fácil de testar → prioridade máxima
2. Impacto Alto + Difícil de testar → segunda prioridade
3. Impacto Médio + Fácil de testar → terceira prioridade

---

## Output Esperado

```
### Novas Hipóteses Geradas

#### Hipótese 1: [título curto e descritivo]
- **Hipótese**: [descrição completa]
- **Evidência nos dados**: [dado específico com números — ex: "Templates enviados entre 13h-14h 
  para DDD 11 têm 78% de READ rate vs. 52% geral. Amostra: 23 mensagens."]
- **Experimento sugerido**: [ação concreta — ex: "No próximo ciclo, criar uma janela específica 
  13h-14h para leads DDD 11 com o template jan_2. Volume: 30 envios. Duração: 1 semana."]
- **Impacto potencial**: [Alto/Médio/Baixo] — [justificativa: "Se confirmada, pode aumentar 
  response rate em ~XX pp para XX% do volume de envios"]
- **Tempo para validar**: [X dias com volume atual de Y envios/dia. Necessário Z envios no total.]

#### Hipótese 2: [título]
- **Hipótese**: [...]
- **Evidência nos dados**: [...]
- **Experimento sugerido**: [...]
- **Impacto potencial**: [...]
- **Tempo para validar**: [...]

#### Hipótese 3: [título]
- **Hipótese**: [...]
- **Evidência nos dados**: [...]
- **Experimento sugerido**: [...]
- **Impacto potencial**: [...]
- **Tempo para validar**: [...]

---

#### Priorização

| # | Hipótese | Impacto | Facilidade | Prioridade |
|---|----------|---------|------------|------------|
| 1 | [título] | [Alto/Médio] | [Fácil/Média/Difícil] | 🔴 Máxima |
| 2 | [título] | [...] | [...] | 🟡 Alta |
| 3 | [título] | [...] | [...] | 🟢 Média |

→ O que fazer com isso: incluir a Hipótese 1 como experimento prioritário no próximo ciclo de disparos.
Reservar XX% do volume semanal para testar as 3 hipóteses em paralelo.
Reavaliar após [X dias / Y disparos].
```
