"""Grava no oracle-cache.json as cartas lidas/consideradas (listas por etiqueta + shortlist) e baixa as rulings da shortlist.
Uso: python3 mm_rulings_cache.py <dados_dir> <shortlist.json>"""
import json, re, sys, os, time
sys.path.insert(0, "/home/user/MTG-Code/scryfall-cache/sets")
import fetch_set as F
dados, slf = sys.argv[1], sys.argv[2]
prints = json.load(open(os.path.join(dados, "candidatas_impressoes_bruto.json")))["impressoes"]
idx = json.load(open(os.path.join(dados, "candidatas_indice.json")))
def oid(c): return c.get("oracle_id") or c["card_faces"][0].get("oracle_id")
primeiro = {}
for c in prints:
    primeiro.setdefault(oid(c), c)
TAGS = {"rad": r"rad counter", "prolif": r"proliferate",
        "dobra": r"that many plus|twice that many|plus one of each|double the number of (\+1/\+1 )?counters|that many more (\+1/\+1 )?counters|one additional (\+1/\+1 )?counter|additional \+1/\+1 counter|put(s)? (twice|double)|triple the number|would put .{0,40}counters?.{0,40}instead",
        "trample": r"trample", "mill": r"\bmills?\b|\bmilled\b|\bmilling\b",
        "contador_gatilho": r"whenever (one or more )?(.{0,40})counters? (is|are|would be) (put|placed)|whenever you put (one or more )?(.{0,30})counters?|for the first time each turn"}
lidas = set()
for o, v in idx.items():
    for tg, rx in TAGS.items():
        if re.search(rx, v["oraculo"], re.I): lidas.add(o)
sl = json.load(open(slf))
nomes_sl = {n for l in sl.values() for n in l}
by = {v["nome"]: o for o, v in idx.items()}
sl_oids = {by[n] for n in nomes_sl if n in by}
lidas |= sl_oids
cache = json.load(open(F.CACHE, encoding="utf-8"))
novas = 0
for o in lidas:
    c = primeiro[o]; e = F.entry(c)
    if c.get("layout") == "reversible_card":
        e["name"] = c["card_faces"][0]["name"]
    nome = e["name"] if c.get("layout") != "reversible_card" else c["card_faces"][0]["name"]
    if nome not in cache or not (cache[nome].get("oracle_text") or "").strip():
        cache[nome] = e; novas += 1
json.dump(cache, open(F.CACHE, "w", encoding="utf-8"), indent=2, ensure_ascii=False); open(F.CACHE, "a").write("\n")
print("cartas lidas/consideradas:", len(lidas), "| novas no cache:", novas, "| total no cache:", len(cache))
rul = {}
for o in sorted(sl_oids, key=lambda o: idx[o]["nome"]):
    c = primeiro[o]
    try:
        rul[idx[o]["nome"]] = F.get(c["rulings_uri"])["data"]
    except Exception as ex:
        rul[idx[o]["nome"]] = f"ERRO {ex}"
    time.sleep(0.1)
json.dump(rul, open(os.path.join(dados, "rulings_shortlist.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("rulings baixadas:", sum(1 for v in rul.values() if isinstance(v, list)), "cartas;", sum(len(v) for v in rul.values() if isinstance(v, list)), "rulings no total")
