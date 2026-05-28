"""
Gera PDF com Top 20 insights — Wellz.
"""
import json, os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, PageBreak)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output/reports")

# Cores
NAVY = HexColor("#0F2A4F")
ACCENT = HexColor("#1F77B4")
GREEN = HexColor("#2BA84A")
RED = HexColor("#D62728")
GREY = HexColor("#6B7280")
LIGHT = HexColor("#F3F4F6")

# Top 20 insights — sintetizados dos findings.json
INSIGHTS = [
    {
        "n": 1, "tag": "TEMPLATES", "color": GREEN,
        "title": "Os 4 templates ativos são todos WINNERS — sem loser na operação",
        "body": "Os templates fup1 (70.6%), abertura_v2 (66.2%), db (66.2%) e fup_2 (59.2%) têm READ rates acima de 59%, todos com 75+ envios. A taxa de leitura média da operação é 54%, muito acima da média de mercado para WhatsApp B2B (15–25%).",
        "action": "Não tem template para matar — o foco deve ser ESCALAR volume nos 4 e introduzir A/B controlado de novas variações. Não trocar o que funciona.",
        "source": "Agente 01 (Template Analyst)",
    },
    {
        "n": 2, "tag": "TEMPLATES", "color": ACCENT,
        "title": "fup_2 é o campeão de resposta: 26% dos threads que recebem respondem",
        "body": "fup_2 tem a maior response rate (26.1%) e leitura rápida (mediana 22min). abertura_v2 vem em segundo (24.9%). Os follow-ups estão convertendo melhor que a abertura — sinal de que a sequência importa mais que o primeiro contato.",
        "action": "Reforçar a CADÊNCIA de follow-up (não só a abertura). Aumentar o número de leads que recebem ao menos 2 follow-ups antes do descarte automático.",
        "source": "Agente 01",
    },
    {
        "n": 3, "tag": "TIMING", "color": GREEN,
        "title": "Terça 12h–15h é a janela de ouro do WhatsApp",
        "body": "Terças entre 12h–15h: 100% READ em 10+10 envios. Quartas 12h–15h: 89% READ em 19 envios. Segundas 21h–00h: 75% READ em 88 envios (alto volume + alta taxa = janela forte).",
        "action": "Concentrar disparos de templates de abertura nas janelas terça-meio e quarta-meio. Priorizar segunda-noite para follow-ups.",
        "source": "Agente 02 (Timing Analyst)",
    },
    {
        "n": 4, "tag": "TIMING", "color": RED,
        "title": "Segunda 12h–15h é o pior horário — 2.4% READ em 42 envios",
        "body": "Apesar de ser horário comercial, esse slot tem performance catastrófica: 1 leitura em 42 envios. Hipótese: leads voltando do almoço com fila de mensagens, sua mensagem fica sepultada.",
        "action": "EVITAR completamente segunda 12h–15h. Mover esses envios para terça-manhã ou segunda-noite.",
        "source": "Agente 02",
    },
    {
        "n": 5, "tag": "CALLS", "color": RED,
        "title": "73.7% das ligações terminam em caixa postal — 1.399 de 1.899 calls perdidas",
        "body": "Outcome NO_CONTACT domina (1399). Apenas 49 calls foram MEANINGFUL (2.6%). Hangup cause: VOICEMAIL_DETECTED em 251 calls. Esforço enorme com ROI mínimo.",
        "action": "Repensar o canal CALL como atual está desenhado. Ou (a) reduzir drasticamente o volume de calls, ou (b) testar segunda chamada no mesmo dia, ou (c) usar CALL apenas após resposta no WhatsApp.",
        "source": "Agente 06 (Call Analyst)",
    },
    {
        "n": 6, "tag": "CALLS", "color": ACCENT,
        "title": "Calls que duram >120s convertem 50.7% em MEANINGFUL",
        "body": "Quando a call passa de 2 minutos, metade vira meaningful. Em < 30s, virtualmente zero (0.9%). A mediana atual é 13s — vasta maioria mal começa.",
        "action": "Métrica de coaching da IA: aumentar a duração média da call. Treinar abertura para passar dos primeiros 20s (script que segura o lead ao telefone).",
        "source": "Agente 06",
    },
    {
        "n": 7, "tag": "CALLS", "color": ACCENT,
        "title": "Melhor horário de ligação: Terça e Quinta 12h–15h (90%+ de connect rate)",
        "body": "Segunda 12h (90% conexão em 285 calls, alto volume e alta taxa) e terça 12h (98% em 61 calls) são as melhores janelas para conexão. Score médio fica em 0.60–0.65 nesses slots.",
        "action": "Concentrar 70% do volume de calls nas janelas dia útil 12h–15h. Reduzir disparos fora dessa janela.",
        "source": "Agente 06",
    },
    {
        "n": 8, "tag": "CADÊNCIA", "color": ACCENT,
        "title": "Esforço médio: 5 ligações + 2 mensagens por prospecção — mas só 13% finalizam",
        "body": "Mediana de 5 calls e 2 mensagens OUTGOING por prospecção. Apenas 52 prospections (13%) chegaram a FINISHED; 305 (78%) seguem IN_PROGRESS. A rotina está LONGA demais antes do descarte.",
        "action": "Reduzir limite de ligações antes de mover lead para WhatsApp-only. Definir corte mais cedo: se 3 calls sem MEANINGFUL → para de ligar e migra para cadência WhatsApp.",
        "source": "Agente 08 (Multichannel Cadence)",
    },
    {
        "n": 9, "tag": "CADÊNCIA", "color": ACCENT,
        "title": "100% das prospections começam por CALL — desenho da rotina não testa outra ordem",
        "body": "Todas as 5 rotinas ativas têm CALL como primeiro touchpoint do Day 0. Não há cohort comparativa de leads que começaram por WhatsApp para A/B test.",
        "action": "Criar rotina experimental que comece por WhatsApp (template + sequência) e comparar 30 dias com a cohort CALL-first. Atual NO_CONTACT de 73% sugere que WhatsApp-first pode ser melhor.",
        "source": "Agente 08",
    },
    {
        "n": 10, "tag": "JORNADA", "color": GREEN,
        "title": "Ciclo de quem CONVERTE: 1 dia. Ciclo de quem DESCARTA: 24 dias",
        "body": "Mediana de tempo de ciclo: FINISHED em 1 dia vs DISCARDED em 24 dias. Quem converte, converte rápido; quem demora, é descarte.",
        "action": "Critério de descarte agressivo: se lead não engajar nos primeiros 5 dias, mover para fila de baixa prioridade (não gastar mais 20 dias com ele).",
        "source": "Agente 09 (Lead Journey)",
    },
    {
        "n": 11, "tag": "JORNADA", "color": RED,
        "title": "95% dos leads não têm setor preenchido — gap crítico de qualificação",
        "body": "Apenas 16 dos 360 leads têm companyIndustry preenchido. Impossível segmentar performance por setor, fazer ICP firmográfico ou priorizar verticais.",
        "action": "Tornar setor um campo obrigatório no GS Engage ou rodar enrichment via Apify/Clearbit antes de iniciar prospecção. Sem isso, agente 09 fica cego.",
        "source": "Agente 09",
    },
    {
        "n": 12, "tag": "DDD", "color": GREEN,
        "title": "DDD 41 (Curitiba) e 31 (BH) são as melhores regiões com volume",
        "body": "DDD 41: 89.1% READ em 46 envios. DDD 31: 69.5% READ em 95 envios. DDD 11 (SP, base 298 envios): 64% READ. Sul/Sudeste dominam em performance + volume.",
        "action": "Aumentar 30% o ICP em PR, MG e SP. DDD 27 (ES) tem 100% READ em 18 envios — testar expansão.",
        "source": "Agente 04 (Lead/DDD Analyst)",
    },
    {
        "n": 13, "tag": "DDD", "color": RED,
        "title": "DDDs 37, 65, 75, 83, 92 têm 0% de leitura — Norte/Nordeste/MG interior",
        "body": "Esses DDDs somam ~25 envios com zero READ. Wilson lower bound = 0. Sinal de que o ICP atual não casa com essas regiões.",
        "action": "Deprioritizar (não eliminar) esses DDDs. Confirmar com mais dados antes de remover. Investigar se há fit cultural/comercial diferente.",
        "source": "Agente 04",
    },
    {
        "n": 14, "tag": "COPY", "color": ACCENT,
        "title": "Mensagens de 200–400 caracteres performam 27% melhor que 100–200",
        "body": "200–400 chars: 56.8% READ. 100–200: 44.7%. 0–100: 44.2%. No B2B WhatsApp, mensagens MAIS DETALHADAS estão ganhando — não o contrário.",
        "action": "Padronizar templates para 200–400 caracteres. Não cortar copy buscando 'concisão' a qualquer preço — o lead B2B quer contexto.",
        "source": "Agente 05 (Correlation Hunter)",
    },
    {
        "n": 15, "tag": "COPY", "color": ACCENT,
        "title": "'Prova social' é o ângulo de copy com mais volume (638 envios) e ótima performance (58% READ)",
        "body": "Menções a 'empresa', 'clientes', 'cases' aparecem em 58% das mensagens OUTGOING. 'Direto' (42 envios) tem 60% READ — mas amostra pequena.",
        "action": "Manter prova social como ângulo principal. Testar variações 'direto' em A/B com volume controlado (alvo: 100 envios) para validar.",
        "source": "Agente 03 (Copy Analyst)",
    },
    {
        "n": 16, "tag": "PLAYBOOK", "color": RED,
        "title": "Apenas 41% das mensagens templates seguem o protocolo de abertura (Mariana + Wellz)",
        "body": "578 mensagens templates avaliadas: só 238 (41%) mencionam tanto a persona 'Mariana' quanto a empresa 'Wellz'. As outras 340 estão fora do padrão definido.",
        "action": "Revisar templates: incluir 'Mariana da Wellz' explicitamente no primeiro parágrafo. É reforço de marca + aderência ao playbook.",
        "source": "Agente 10 (Playbook Adherence)",
    },
    {
        "n": 17, "tag": "PLAYBOOK", "color": RED,
        "title": "3 pains do playbook nunca foram mencionadas em conversas reais",
        "body": "'Presenteísmo', 'horas extras por sobrecarga' e 'cultura de silêncio' têm ZERO menções nas 1.106 mensagens OUTGOING. Já 'absenteísmo' foi citado 576x — virou tema dominante.",
        "action": "Decidir: remover as 3 pains mortas do playbook OU forçar uso em variações de copy. A concentração em 'absenteísmo' está deixando 30% do arsenal sem uso.",
        "source": "Agente 10",
    },
    {
        "n": 18, "tag": "NOTAS", "color": RED,
        "title": "Só 38% dos leads têm notas registradas — perda massiva de contexto",
        "body": "290 notas para 360 leads, mas cobertura é só 138 leads (38%). Sem nota, é impossível reconstruir o que aconteceu na conversa para o próximo SDR ou ciclo.",
        "action": "Tornar registro de nota obrigatório ao encerrar interação (call ou WhatsApp). Sugerir 3 templates mínimos: 'Pós-call', 'Pós-WhatsApp', 'Decisão de descarte'.",
        "source": "Agente 11 (Notes Signal)",
    },
    {
        "n": 19, "tag": "NOTAS", "color": GREEN,
        "title": "'AGENDOU' nas notas é o maior preditor de conversão — 17% dos FINISHED têm essa marca",
        "body": "9 dos 52 leads FINISHED têm notas com sinal 'AGENDOU' (17%) vs 3 dos descartados. Em segundo: PEDIU_MATERIAL (5/52). CONCORRENCIA também aparece (3/52) — não bloqueia conversão.",
        "action": "Quando a nota mencionar 'AGENDOU', subir prioridade do lead automaticamente. Quando mencionar 'CONCORRENCIA' sem ser combinado com PEDIU_MATERIAL, treinar resposta específica.",
        "source": "Agente 11",
    },
    {
        "n": 20, "tag": "CONTEÚDO", "color": ACCENT,
        "title": "Calls têm mediana de 2 turnos — IA está fazendo monólogos curtos, não diálogo",
        "body": "Mediana de 2 turnos por call transcrita (1628 calls com segments). Combinado com duração mediana de 13s, isso indica que a IA está abrindo, o lead responde 'alô?' e desliga. Não há diálogo real.",
        "action": "Crítico: refazer a abertura do agente de voz para gerar 2º turno do LEAD (pergunta-gancho nos primeiros 5 segundos). Sem isso, o canal CALL é desperdiçado.",
        "source": "Agente 07 (Transcription Analyst)",
    },
]

# === META ===
f = json.load(open(os.path.join(ROOT,"analysis/findings.json")))
meta = f["meta"]
period_min = datetime.fromisoformat(meta["data_min"]).strftime("%d/%m/%Y")
period_max = datetime.fromisoformat(meta["data_max"]).strftime("%d/%m/%Y")
today = datetime.now().strftime("%d/%m/%Y")
DATE = datetime.now().strftime("%Y-%m-%d")

# === Build PDF ===
pdf_path = os.path.join(OUT, f"report-top20-insights-wellz-{DATE}.pdf")
doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                        leftMargin=1.8*cm, rightMargin=1.8*cm,
                        topMargin=1.5*cm, bottomMargin=1.5*cm,
                        title=f"Top 20 Insights — Wellz — {DATE}",
                        author="Sales Analyst (Growth Edge)")

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=22, textColor=NAVY,
                    spaceAfter=6, leading=26)
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, textColor=NAVY,
                    spaceAfter=4, leading=16)
SUB = ParagraphStyle("SUB", parent=styles["Normal"], fontSize=10, textColor=GREY, leading=13)
BODY = ParagraphStyle("BODY", parent=styles["Normal"], fontSize=10, leading=14,
                       alignment=TA_JUSTIFY)
ACTION = ParagraphStyle("ACT", parent=styles["Normal"], fontSize=10, leading=14,
                         textColor=NAVY, alignment=TA_JUSTIFY)
SRC = ParagraphStyle("SRC", parent=styles["Normal"], fontSize=8, textColor=GREY, leading=10,
                      alignment=TA_LEFT)
TITLE_I = ParagraphStyle("TI", parent=styles["Heading3"], fontSize=12, textColor=NAVY,
                          spaceAfter=2, leading=15)

elements = []

# Capa
elements.append(Paragraph("Top 20 Insights — Wellz", H1))
elements.append(Paragraph(f"Síntese da análise multicanal de cadência B2B", SUB))
elements.append(Spacer(1, 0.4*cm))

# Header table
header_data = [
    ["Cliente", "Wellz (parte do grupo Wellhub)"],
    ["Período analisado", f"{period_min} a {period_max}"],
    ["Data de geração", today],
    ["Volume de dados", f"{meta['total_messages']:,} mensagens · {meta['total_calls']:,} ligações · {meta['total_leads']} leads · {meta['total_notes']} notas"],
    ["Cobertura", f"OUTGOING: {meta['outgoing']:,} · INCOMING: {meta['incoming']:,} · Calls SUCCESS: {meta['calls_success']:,} · Prospecções: {meta['total_prosp']}"],
    ["Metodologia", "11 agentes especializados (template, timing, copy, lead/DDD, correlação, calls, transcrição, cadência, jornada, playbook, notas) + síntese executiva"],
]
ht = Table(header_data, colWidths=[3.6*cm, 12.6*cm])
ht.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(0,-1),LIGHT),
    ("TEXTCOLOR",(0,0),(0,-1),NAVY),
    ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
    ("FONTSIZE",(0,0),(-1,-1),9),
    ("VALIGN",(0,0),(-1,-1),"TOP"),
    ("LEFTPADDING",(0,0),(-1,-1),6),
    ("RIGHTPADDING",(0,0),(-1,-1),6),
    ("TOPPADDING",(0,0),(-1,-1),5),
    ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("GRID",(0,0),(-1,-1),0.5,HexColor("#D1D5DB")),
]))
elements.append(ht)
elements.append(Spacer(1, 0.5*cm))

# Resumo executivo
elements.append(Paragraph("Resumo executivo", H2))
elements.append(Paragraph(
    "Os 4 templates de WhatsApp da operação Wellz performam acima da média de mercado (READ médio 54%, "
    "vs benchmark B2B 15–25%), mas o canal de <b>ligações está em colapso silencioso</b>: 74% das chamadas "
    "vão para caixa postal e a duração mediana é de 13 segundos. O perfil de conversão tem assinatura clara — "
    "quem fecha, fecha em <b>1 dia</b>; quem demora, é descartado em ~24 dias. As três frentes prioritárias "
    "para os próximos 30 dias são (1) <b>reorganizar o canal de calls</b> (menos volume, melhor horário, "
    "abertura redesenhada), (2) <b>escalar volume nos templates que já são WINNERS</b> nas janelas terça/quarta "
    "12h–15h, e (3) <b>fechar o gap de qualificação</b> (setor faltando em 95% dos leads + notas faltando "
    "em 62% das prospecções).", BODY))
elements.append(Spacer(1, 0.5*cm))

# Quick wins
elements.append(Paragraph("Quick wins (próximos 7 dias)", H2))
quickwins = [
    "Parar disparos WhatsApp segunda 12h–15h (0% READ em 42 envios). Mover para segunda-noite ou terça-manhã.",
    "Concentrar 70% do volume de calls em terça e quinta 12h–15h (connect rate 90%+).",
    "Adicionar 'Mariana da Wellz' no primeiro parágrafo de todos os templates (só 41% seguem hoje).",
    "Reduzir limite de calls antes de migração para WhatsApp-only: 3 calls sem MEANINGFUL → cadência WPP.",
    "Tornar registro de nota obrigatório ao encerrar interação (cobertura atual: 38%).",
]
for q in quickwins:
    elements.append(Paragraph(f"• {q}", BODY))
elements.append(PageBreak())

# Top 20
elements.append(Paragraph("Os 20 Insights", H1))
elements.append(Spacer(1, 0.3*cm))

for ins in INSIGHTS:
    tag_table = Table(
        [[Paragraph(f"<b>#{ins['n']:02d}</b>", ParagraphStyle("n",fontSize=12,textColor=ins["color"],fontName="Helvetica-Bold")),
          Paragraph(f"<b>{ins['tag']}</b>", ParagraphStyle("t",fontSize=8,textColor=ins["color"],fontName="Helvetica-Bold"))]],
        colWidths=[1.2*cm, 14.5*cm]
    )
    tag_table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,0),LIGHT),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),2),
        ("TOPPADDING",(0,0),(-1,-1),2),
    ]))
    elements.append(tag_table)
    elements.append(Paragraph(ins["title"], TITLE_I))
    elements.append(Paragraph(ins["body"], BODY))
    elements.append(Spacer(1, 0.15*cm))
    elements.append(Paragraph(f"<b>→ O que fazer com isso:</b> {ins['action']}", ACTION))
    elements.append(Paragraph(f"Fonte: {ins['source']}", SRC))
    elements.append(Spacer(1, 0.35*cm))

# Próxima análise
elements.append(PageBreak())
elements.append(Paragraph("Próxima análise sugerida", H2))
elements.append(Paragraph(
    "Rodar nova análise em 30 dias (12/06/2026) com foco em: (a) validar se a redução de calls "
    "fora da janela 12h–15h melhorou o NO_CONTACT rate; (b) medir impacto da remoção das 3 pains "
    "mortas do playbook; (c) confirmar se cohort WhatsApp-first supera CALL-first em conversão; "
    "(d) reaplicar este relatório uma vez que setor (companyIndustry) tenha cobertura > 50% para "
    "validar o ICP firmográfico. Recomenda-se rodar também análise quinzenal de templates novos em "
    "A/B test com volume ≥ 100 envios para garantir significância estatística.", BODY))

elements.append(Spacer(1, 0.4*cm))
elements.append(Paragraph("Limitações conhecidas desta análise", H2))
elements.append(Paragraph(
    "(1) Transcrições com speaker discriminado tiveram dados parciais — talk:listen ratio mediano não pôde "
    "ser calculado nesta rodada. (2) companyIndustry preenchido em apenas 16/360 leads — análise de cohort "
    "firmográfico não significativa. (3) task_execution (76MB) não foi processado linha-a-linha; usou-se "
    "amostragem por prospecção. (4) Categorização de objeções via regex pt-BR — pode ter falsos positivos.",
    BODY))

doc.build(elements)
print(f"✓ PDF gerado em: {pdf_path}")
print(f"  Tamanho: {os.path.getsize(pdf_path)/1024:.1f} KB")
