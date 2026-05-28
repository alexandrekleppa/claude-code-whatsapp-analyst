"""
Análise consolidada multicanal — Wellz.
Computa métricas para os 11 agentes e salva findings.json + reports markdown.
"""
import json, os, re, math
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from statistics import median, mean

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT = os.path.join(ROOT, "input/whatsapp-conversations/wellz")
OUT = os.path.join(ROOT, "output/reports")
ANALYSIS = os.path.join(ROOT, "analysis")

def load(name):
    with open(os.path.join(INPUT, f"wellz_{name}.json")) as f:
        return json.load(f)

def pdate(d):
    if not d: return None
    if isinstance(d, dict): d = d.get("$date")
    if not d: return None
    try: return datetime.fromisoformat(d.replace("Z","+00:00"))
    except: return None

def pid(d):
    if not d: return None
    if isinstance(d, dict): return d.get("$oid")
    return d

def wilson_lower(p, n, z=1.96):
    if n == 0: return 0
    return (p + z*z/(2*n) - z*math.sqrt((p*(1-p) + z*z/(4*n))/n)) / (1 + z*z/n)

print("Loading datasets…")
msgs = load("conversation_messages")
threads = load("conversation_threads")
calls = load("voip_calls")
trans = load("voip_call_transcriptions")
call_analysis = load("voip_call_analysis")
leads = load("lead")
notes = load("lead_notes")
ai_agents = load("ai_agents")
prosp = load("prospection")
routine = load("prospection_routine")
# task_execution é 76MB — vamos amostrar
print(f"  messages: {len(msgs)} | calls: {len(calls)} | trans: {len(trans)} | analysis: {len(call_analysis)}")
print(f"  leads: {len(leads)} | notes: {len(notes)} | prosp: {len(prosp)} | routines: {len(routine)}")

findings = {}

# === Date range ===
msg_dates = [pdate(m.get("sentAt") or m.get("createdAt")) for m in msgs]
msg_dates = [d for d in msg_dates if d]
date_min = min(msg_dates)
date_max = max(msg_dates)
findings["meta"] = {
    "data_min": date_min.isoformat(),
    "data_max": date_max.isoformat(),
    "total_messages": len(msgs),
    "outgoing": sum(1 for m in msgs if m.get("direction")=="OUTGOING"),
    "incoming": sum(1 for m in msgs if m.get("direction")=="INCOMING"),
    "total_calls": len(calls),
    "calls_success": sum(1 for c in calls if c.get("status")=="SUCCESS"),
    "total_leads": len(leads),
    "total_notes": len(notes),
    "total_prosp": len(prosp),
}

# === Agente 01 — Template Analyst ===
print("01 Template…")
tpl_stats = defaultdict(lambda: {"sent":0, "delivered":0, "read":0, "failed":0, "threads":set(), "read_speeds":[]})
for m in msgs:
    if m.get("direction") != "OUTGOING" or m.get("messageType") != "TEMPLATE": continue
    name = m.get("templateName") or "(no_name)"
    s = m.get("status")
    tpl_stats[name]["sent"] += 1
    if s == "READ": tpl_stats[name]["read"] += 1
    if s == "DELIVERED": tpl_stats[name]["delivered"] += 1
    if s in ("UNDELIVERED","FAILED"): tpl_stats[name]["failed"] += 1
    tid = pid(m.get("thread"))
    if tid: tpl_stats[name]["threads"].add(tid)
    sent_at = pdate(m.get("sentAt"))
    upd_at = pdate(m.get("updatedAt"))
    if s == "READ" and sent_at and upd_at:
        delta_min = (upd_at - sent_at).total_seconds() / 60
        if 0 < delta_min < 60*48:
            tpl_stats[name]["read_speeds"].append(delta_min)

# threads with incoming reply
threads_with_inc = set()
for m in msgs:
    if m.get("direction") == "INCOMING":
        tid = pid(m.get("thread"))
        if tid: threads_with_inc.add(tid)

tpl_rows = []
for name, st in tpl_stats.items():
    delivered_or_read = st["read"] + st["delivered"]
    read_rate = st["read"] / delivered_or_read if delivered_or_read else 0
    resp_threads = sum(1 for t in st["threads"] if t in threads_with_inc)
    resp_rate = resp_threads / len(st["threads"]) if st["threads"] else 0
    speed = median(st["read_speeds"]) if st["read_speeds"] else None
    wilson_read = wilson_lower(read_rate, delivered_or_read)
    wilson_resp = wilson_lower(resp_rate, len(st["threads"]))
    n = st["sent"]
    if n >= 20 and read_rate < 0.3: cls = "LOSER"
    elif n >= 10 and (read_rate > 0.6 or resp_rate > 0.15): cls = "WINNER"
    elif n >= 10: cls = "NEUTRO"
    else: cls = "⚠️ Insuf"
    tpl_rows.append({"name":name,"sent":n,"read_rate":read_rate,"resp_rate":resp_rate,
                     "speed_min":speed,"wilson_read":wilson_read,"wilson_resp":wilson_resp,
                     "classe":cls, "failed":st["failed"]})
tpl_rows.sort(key=lambda x: -x["wilson_read"])
findings["templates"] = tpl_rows

# === Agente 02 — Timing ===
print("02 Timing…")
slot_stats = defaultdict(lambda: {"sent":0,"read":0})
for m in msgs:
    if m.get("direction") != "OUTGOING": continue
    sent = pdate(m.get("sentAt"))
    if not sent: continue
    dow = sent.weekday()  # 0=Mon
    hour = sent.hour
    bucket = hour // 3 * 3  # 3-hour buckets
    key = (dow, bucket)
    slot_stats[key]["sent"] += 1
    if m.get("status") == "READ": slot_stats[key]["read"] += 1

timing_rows = []
for (dow,bucket), s in slot_stats.items():
    rate = s["read"]/s["sent"] if s["sent"] else 0
    timing_rows.append({"dow":dow,"bucket":bucket,"sent":s["sent"],"read":s["read"],"read_rate":rate,
                        "wilson":wilson_lower(rate, s["sent"])})
timing_rows.sort(key=lambda x: -x["wilson"])
findings["timing_slots"] = timing_rows

# === Agente 03 — Copy / Angle ===
print("03 Copy…")
angle_keywords = {
    "prova_social":["empresa","clientes","case","junto","parceiros"],
    "exclusividade":["exclusiv","selecionad","apenas","prioritár"],
    "urgencia":["hoje","amanhã","essa semana","agora","último","prazo"],
    "curiosidade":["surpres","novidade","interessante","tendência","você sabia"],
    "direto":["quero","posso","podemos","podemos conversar","tem 15"],
    "reciprocidade":["material","conteúdo","gratuito","sem custo","brinde"],
    "dor":["desafio","problema","dificuldade","gargalo","preocup"],
    "perguntas":["?"],
}
angle_perf = defaultdict(lambda: {"sent":0,"read":0,"resp_threads":set()})
for m in msgs:
    if m.get("direction") != "OUTGOING": continue
    txt = (m.get("text") or "").lower()
    for ang, kws in angle_keywords.items():
        if any(k in txt for k in kws):
            angle_perf[ang]["sent"] += 1
            if m.get("status") == "READ": angle_perf[ang]["read"] += 1
            tid = pid(m.get("thread"))
            if tid: angle_perf[ang]["resp_threads"].add(tid)

angle_rows = []
for ang, s in angle_perf.items():
    rate = s["read"]/s["sent"] if s["sent"] else 0
    resp = sum(1 for t in s["resp_threads"] if t in threads_with_inc) / max(len(s["resp_threads"]),1)
    angle_rows.append({"angle":ang,"sent":s["sent"],"read_rate":rate,"resp_rate":resp})
angle_rows.sort(key=lambda x: -x["read_rate"])
findings["angles"] = angle_rows

# === Agente 04 — Lead/DDD ===
print("04 Lead/DDD…")
ddd_stats = defaultdict(lambda: {"sent":0,"read":0,"resp_threads":set()})
for m in msgs:
    if m.get("direction") != "OUTGOING": continue
    to = m.get("to") or ""
    ddd = to[3:5] if to.startswith("+55") and len(to)>=5 else "??"
    ddd_stats[ddd]["sent"] += 1
    if m.get("status") == "READ": ddd_stats[ddd]["read"] += 1
    tid = pid(m.get("thread"))
    if tid: ddd_stats[ddd]["resp_threads"].add(tid)

ddd_rows = []
for ddd, s in ddd_stats.items():
    rate = s["read"]/s["sent"] if s["sent"] else 0
    resp_t = sum(1 for t in s["resp_threads"] if t in threads_with_inc)
    resp_rate = resp_t / max(len(s["resp_threads"]),1)
    ddd_rows.append({"ddd":ddd,"sent":s["sent"],"read_rate":rate,"resp_rate":resp_rate,
                     "threads":len(s["resp_threads"]),
                     "wilson":wilson_lower(rate, s["sent"])})
ddd_rows.sort(key=lambda x: -x["wilson"])
findings["ddd"] = ddd_rows

# === Agente 05 — Correlation Hunter (lite) ===
print("05 Correlation…")
# Hipótese 1: comprimento da mensagem vs read rate
length_buckets = defaultdict(lambda: {"sent":0,"read":0})
for m in msgs:
    if m.get("direction") != "OUTGOING": continue
    L = len(m.get("text") or "")
    b = "0-100" if L<100 else "100-200" if L<200 else "200-400" if L<400 else "400+"
    length_buckets[b]["sent"] += 1
    if m.get("status") == "READ": length_buckets[b]["read"] += 1
findings["len_buckets"] = {b:{"sent":s["sent"],"read_rate":s["read"]/s["sent"] if s["sent"] else 0}
                            for b,s in length_buckets.items()}

# === Agente 06 — Call Analyst ===
print("06 Call…")
analysis_by_call = {pid(a.get("voipCall")):a for a in call_analysis}
call_outcomes = Counter(c.get("outcome") for c in calls)
call_status = Counter(c.get("status") for c in calls)
call_hangup = Counter(c.get("hangupCause") for c in calls)
call_durations = [c.get("durationInSeconds",0) for c in calls if c.get("durationInSeconds")]
call_scores = []
for c in calls:
    a = analysis_by_call.get(pid(c.get("_id")))
    if a and a.get("score") is not None: call_scores.append(a["score"])

# Calls by day×hour
call_slot = defaultdict(lambda: {"total":0,"success":0,"meaningful":0,"scores":[]})
for c in calls:
    started = pdate(c.get("startedAt"))
    if not started: continue
    key = (started.weekday(), started.hour//3*3)
    call_slot[key]["total"] += 1
    if c.get("status") == "SUCCESS": call_slot[key]["success"] += 1
    if c.get("outcome") in ("MEANINGFUL","MEETING_SCHEDULED"): call_slot[key]["meaningful"] += 1
    a = analysis_by_call.get(pid(c.get("_id")))
    if a and a.get("score") is not None: call_slot[key]["scores"].append(a["score"])

call_slot_rows = []
for (dow,bucket), s in call_slot.items():
    cr = s["success"]/s["total"] if s["total"] else 0
    mr = s["meaningful"]/s["success"] if s["success"] else 0
    avg_score = mean(s["scores"]) if s["scores"] else 0
    call_slot_rows.append({"dow":dow,"bucket":bucket,"total":s["total"],"connect_rate":cr,
                           "meaningful_rate":mr,"avg_score":avg_score,
                           "wilson_connect":wilson_lower(cr,s["total"])})
call_slot_rows.sort(key=lambda x: -x["wilson_connect"])

findings["calls"] = {
    "outcomes":dict(call_outcomes),
    "statuses":dict(call_status),
    "hangups":dict(call_hangup.most_common(10)),
    "avg_duration": mean(call_durations) if call_durations else 0,
    "median_duration": median(call_durations) if call_durations else 0,
    "avg_score": mean(call_scores) if call_scores else 0,
    "scored_calls": len(call_scores),
    "slot_top10": call_slot_rows[:10],
    "slot_bot10": call_slot_rows[-10:],
}

# Duration vs outcome
dur_buckets = defaultdict(lambda: {"total":0,"meaningful":0})
for c in calls:
    d = c.get("durationInSeconds") or 0
    b = "0-10s" if d<10 else "10-30s" if d<30 else "30-60s" if d<60 else "60-120s" if d<120 else "120s+"
    dur_buckets[b]["total"] += 1
    if c.get("outcome") in ("MEANINGFUL","MEETING_SCHEDULED"): dur_buckets[b]["meaningful"] += 1
findings["calls"]["dur_buckets"] = {b:{"total":s["total"],"meaningful_rate":s["meaningful"]/s["total"] if s["total"] else 0}
                                     for b,s in dur_buckets.items()}

# === Agente 07 — Transcription ===
print("07 Transcription…")
trans_by_call = {pid(t.get("voipCall")):t for t in trans}
talk_ratios = []
turns_list = []
trans_calls_with_data = 0
all_lead_text = []
all_sdr_text = []
all_first_30s_sdr = []
for c in calls:
    t = trans_by_call.get(pid(c.get("_id")))
    if not t: continue
    segs = t.get("segments") or []
    if not segs: continue
    trans_calls_with_data += 1
    sdr_time = sum((s.get("end",0)-s.get("start",0)) for s in segs if s.get("speaker") in ("sdr","ai","agent"))
    lead_time = sum((s.get("end",0)-s.get("start",0)) for s in segs if s.get("speaker") == "lead")
    total = sdr_time + lead_time
    if total > 0:
        talk_ratios.append(sdr_time/total)
    turns_list.append(len(segs))
    for s in segs:
        sp = s.get("speaker")
        txt = s.get("text") or ""
        if sp == "lead": all_lead_text.append(txt)
        elif sp in ("sdr","ai","agent"): all_sdr_text.append(txt)
        if s.get("start",999) < 30 and sp in ("sdr","ai","agent"):
            all_first_30s_sdr.append(txt)

findings["transcription"] = {
    "calls_with_segs": trans_calls_with_data,
    "median_talk_ratio_sdr": median(talk_ratios) if talk_ratios else None,
    "median_turns": median(turns_list) if turns_list else None,
}

# Objection extraction
def categorize(text):
    text_low = text.lower()
    cats = []
    patterns = {
        "PRECO":["caro","valor","investimento","orçament","custo","desconto","preço"],
        "TIMING":["agora não","mais pra frente","mês que vem","ano que vem","ocupad","sem tempo","não é momento","depois"],
        "AUTORIDADE":["não sou eu","preciso falar","diretor","sócio","gestor decide","outra pessoa"],
        "NECESSIDADE":["não precisa","já temos","já tem","resolvido","não é prioridade"],
        "CONFIANCA":["nunca ouvi","quem é","referência","como funciona"],
        "CONCORRENCIA":["gympass","totalpass","wellhub","já uso","já contrat"],
        "AGENDOU":["marcar","reunião","call","encontro","amanhã às","que dia","horário"],
        "PEDIU_MATERIAL":["manda","envia","apresentação","link","pdf","material"],
        "PERGUNTOU_PRECO":["quanto","valor","investimento","mensalidade","preço"],
        "DOR_CONFIRMADA":["exatamente isso","é nosso problema","incomoda","desafio nosso"],
    }
    for c, kws in patterns.items():
        if any(k in text_low for k in kws): cats.append(c)
    return cats

lead_cat_counts = Counter()
for txt in all_lead_text:
    for c in categorize(txt):
        lead_cat_counts[c] += 1
findings["lead_signals"] = dict(lead_cat_counts)

# === Agente 08 — Multichannel Cadence ===
print("08 Cadence…")
# Routine steps
all_steps = []
for r in routine:
    for i, step in enumerate(r.get("steps") or []):
        for task in step.get("tasks") or []:
            all_steps.append({"routine":r.get("title"),"day":step.get("daysAfterStart"),
                              "order":i,"type":task.get("type")})

# Funnel by lead: count touchpoints
touchpoints_per_lead = defaultdict(lambda: {"msgs_out":0,"msgs_in":0,"calls":0,"calls_meaningful":0})
for m in msgs:
    p = pid(m.get("prospection"))
    if not p: continue
    if m.get("direction") == "OUTGOING": touchpoints_per_lead[p]["msgs_out"] += 1
    else: touchpoints_per_lead[p]["msgs_in"] += 1
for c in calls:
    p = pid(c.get("prospection"))
    if not p: continue
    touchpoints_per_lead[p]["calls"] += 1
    if c.get("outcome") in ("MEANINGFUL","MEETING_SCHEDULED"):
        touchpoints_per_lead[p]["calls_meaningful"] += 1

# Conversion by sequence: did the lead start with CALL or WPP?
prosp_status = {pid(p.get("_id")):p.get("status") for p in prosp}
seq_outcomes = defaultdict(lambda: Counter())
# For each prosp, find first touch type
first_touch = {}
events = []
for m in msgs:
    p = pid(m.get("prospection"))
    if p: events.append((pdate(m.get("sentAt") or m.get("createdAt")), p, "WPP", m.get("direction")))
for c in calls:
    p = pid(c.get("prospection"))
    if p: events.append((pdate(c.get("startedAt") or c.get("createdAt")), p, "CALL", "OUT"))
events = [(d,p,k,dr) for d,p,k,dr in events if d]
events.sort()
for d,p,k,dr in events:
    if p not in first_touch and dr == "OUT" and (dr=="OUT" or k=="CALL"):
        first_touch[p] = k

for p, ft in first_touch.items():
    seq_outcomes[ft][prosp_status.get(p, "?")] += 1

findings["cadence"] = {
    "first_touch": {k:dict(v) for k,v in seq_outcomes.items()},
    "touchpoint_stats": {
        "median_msgs_out": median([t["msgs_out"] for t in touchpoints_per_lead.values()]) if touchpoints_per_lead else 0,
        "median_calls": median([t["calls"] for t in touchpoints_per_lead.values()]) if touchpoints_per_lead else 0,
    },
    "routine_steps": all_steps[:30],
}

# Conversion by # calls before answering
calls_before_response = []
for p, t in touchpoints_per_lead.items():
    if t["msgs_in"] > 0:
        calls_before_response.append(t["calls"])
findings["cadence"]["calls_before_response_median"] = median(calls_before_response) if calls_before_response else None

# === Agente 09 — Lead Journey ===
print("09 Journey…")
status_by_lead = {}
for p in prosp:
    lid = pid(p.get("lead"))
    started = pdate(p.get("startedAt") or p.get("createdAt"))
    ended = pdate(p.get("endedAt") or p.get("updatedAt"))
    if lid and started:
        cycle = (ended - started).days if ended else None
        status_by_lead[lid] = {"status":p.get("status"), "cycle_days":cycle, "started":started.isoformat()}

# Outcome by industry
industry_by_lead = {pid(l.get("_id")): l.get("companyIndustry") for l in leads}
ind_outcomes = defaultdict(lambda: Counter())
for lid, info in status_by_lead.items():
    ind = industry_by_lead.get(lid) or "?"
    ind_outcomes[ind][info["status"]] += 1
ind_rows = []
for ind, c in ind_outcomes.items():
    total = sum(c.values())
    ind_rows.append({"industry":ind,"total":total,
                     "finished":c.get("FINISHED",0),
                     "discarded":c.get("DISCARDED",0),
                     "in_progress":c.get("IN_PROGRESS",0),
                     "finished_rate":c.get("FINISHED",0)/total if total else 0})
ind_rows.sort(key=lambda x: -x["finished_rate"])
findings["journey"] = {
    "status_breakdown": dict(Counter(s["status"] for s in status_by_lead.values())),
    "industry_outcomes": ind_rows,
    "cycle_finished_median": median([s["cycle_days"] for s in status_by_lead.values() if s["status"]=="FINISHED" and s["cycle_days"] is not None]) if any(s["status"]=="FINISHED" for s in status_by_lead.values()) else None,
    "cycle_discarded_median": median([s["cycle_days"] for s in status_by_lead.values() if s["status"]=="DISCARDED" and s["cycle_days"] is not None]) if any(s["status"]=="DISCARDED" for s in status_by_lead.values()) else None,
}

# === Agente 10 — Playbook Adherence ===
print("10 Playbook…")
agent_info = ai_agents[0] if ai_agents else {}
playbook_name = agent_info.get("persona") or agent_info.get("name") or "?"
playbook_pains = []
psf = agent_info.get("psfData") or {}
if isinstance(psf.get("pains"), list):
    for p in psf["pains"]:
        if isinstance(p, dict):
            playbook_pains.append({"desc":p.get("description") or p.get("name") or "?",
                                    "resolution":p.get("resolution") or ""})
# Count pain mentions in OUTGOING messages
pain_mentions = []
for pain in playbook_pains:
    desc = (pain["desc"] or "").lower()
    keywords = [w for w in re.findall(r"\w+", desc) if len(w) > 5][:3]
    if not keywords:
        pain_mentions.append({"pain":pain["desc"],"mentions":0})
        continue
    count = sum(1 for m in msgs if m.get("direction")=="OUTGOING" and
                any(k in (m.get("text") or "").lower() for k in keywords))
    pain_mentions.append({"pain":pain["desc"],"keywords":keywords,"mentions":count})

# Opening adherence: % messages with persona name + company name
opening_hits = 0
opening_total = 0
for m in msgs:
    if m.get("direction") != "OUTGOING" or m.get("messageType") != "TEMPLATE": continue
    txt = (m.get("text") or "").lower()
    opening_total += 1
    has_persona = "mariana" in txt
    has_company = "wellz" in txt
    if has_persona and has_company: opening_hits += 1

# Guardrail violations
guardrail_hits = {
    "promete_desconto": sum(1 for m in msgs if m.get("direction")=="OUTGOING" and any(k in (m.get("text") or "").lower() for k in ["desconto","grátis","gratuito"])),
    "pressao": sum(1 for m in msgs if m.get("direction")=="OUTGOING" and any(k in (m.get("text") or "").lower() for k in ["última chance","tem que ser hoje","precisa decidir agora"])),
}
findings["playbook"] = {
    "persona": playbook_name,
    "pain_mentions": pain_mentions,
    "opening_adherence": opening_hits/opening_total if opening_total else 0,
    "opening_sample": opening_total,
    "guardrail_violations": guardrail_hits,
}

# === Agente 11 — Notes Signal ===
print("11 Notes…")
# Categorize notes
note_cats = Counter()
note_by_lead = defaultdict(list)
for n in notes:
    txt = n.get("content") or n.get("text") or n.get("note") or ""
    if isinstance(txt, dict): txt = json.dumps(txt)
    cats = categorize(str(txt))
    for c in cats: note_cats[c] += 1
    lid = pid(n.get("lead"))
    if lid: note_by_lead[lid].append(str(txt))

# coverage
leads_with_note = sum(1 for l in leads if pid(l.get("_id")) in note_by_lead)
# correlation with outcome
won_with_signals = defaultdict(int)
disc_with_signals = defaultdict(int)
for lid, info in status_by_lead.items():
    texts = note_by_lead.get(lid, [])
    if not texts: continue
    all_txt = " ".join(texts).lower()
    cats = categorize(all_txt)
    for c in set(cats):
        if info["status"] == "FINISHED": won_with_signals[c] += 1
        elif info["status"] == "DISCARDED": disc_with_signals[c] += 1

findings["notes"] = {
    "total": len(notes),
    "coverage_pct": leads_with_note/len(leads) if leads else 0,
    "categories": dict(note_cats),
    "won_signals": dict(won_with_signals),
    "disc_signals": dict(disc_with_signals),
    "sample": [str((n.get("content") or n.get("text") or ""))[:200] for n in notes[:3]],
}

# Inspect note structure
if notes:
    findings["notes"]["fields_sample"] = list(notes[0].keys())[:10]

# === Save ===
with open(os.path.join(ANALYSIS, "findings.json"), "w") as f:
    json.dump(findings, f, indent=2, default=str)
print(f"\n✓ Saved findings to {ANALYSIS}/findings.json")
print(f"Period: {date_min.date()} → {date_max.date()}")
print(f"Templates: {len(tpl_rows)} | DDDs: {len(ddd_rows)} | Call slots: {len(call_slot_rows)}")
print(f"Pain mentions analysed: {len(pain_mentions)}")
