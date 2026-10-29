"""Salva no scryfall-cache/oracle-cache.json (regra permanente: toda carta mencionada/sugerida) as cartas da lista do Stefano que faltam la',
e baixa as RULINGS (rulings_uri) de Agent Frank Horrigan e The Master, Transcendent para dados/rulings_candidatas.json.
Uso: python3 cache_stefano.py (da raiz do repositorio)"""
import json, os, sys, time, urllib.request
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
PAST = os.path.join(RAIZ, "wise-mothman-sultai", "resultados-ab", "2026-10-07-comparacao-stefano", "dados")
CACHE = os.path.join(RAIZ, "scryfall-cache", "oracle-cache.json")
def http(url, data=None, tries=4):
    for t in range(tries):
        try:
            rq = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "Accept": "application/json;q=0.9,*/*;q=0.8", "User-Agent": "MTG-Code-audit/1.0"})
            return json.load(urllib.request.urlopen(rq, timeout=120))
        except Exception as e:
            err = e; time.sleep(2 * (t + 1))
    raise RuntimeError((url, err))
cache = json.load(open(CACHE, encoding="utf-8"))
res = json.load(open(os.path.join(PAST, "lista_stefano_resolvida.json"), encoding="utf-8"))
falta = [x for x in res if x["name"] not in cache]
print("faltam no cache:", len(falta))
if falta:
    r = http("https://api.scryfall.com/cards/collection", json.dumps({"identifiers": [{"id": x["scryfall_id"]} for x in falta]}).encode())
    assert not r.get("not_found"), r.get("not_found")
    for c in r["data"]:
        f = c.get("card_faces") or []
        if f and "oracle_text" not in c:
            txt = "\n // \n".join(f"{ff['name']} ({ff.get('mana_cost', '')}): {ff.get('oracle_text', '')}\n" if False else ff.get("oracle_text", "") for ff in f)
        else:
            txt = c.get("oracle_text", "")
        cache[c["name"]] = dict(cmc=c.get("cmc"), collector_number=c.get("collector_number"), color_identity=c.get("color_identity"), colors=c.get("colors") or (f[0].get("colors") if f else []),
                                keywords=c.get("keywords"), legalities=c.get("legalities"), loyalty=c.get("loyalty"), mana_cost=c.get("mana_cost") or (f[0].get("mana_cost") if f else ""),
                                name=c["name"], oracle_text=txt, power=c.get("power"), prices=c.get("prices"), released_at=c.get("released_at"), scryfall_uri=c.get("scryfall_uri"),
                                set=c.get("set"), toughness=c.get("toughness"), type_line=c.get("type_line"))
    open(CACHE, "w", encoding="utf-8").write(json.dumps(cache, indent=2, ensure_ascii=False) + "\n")
    print("gravadas:", [c["name"] for c in r["data"]])
out = {}
for x in res:
    if x["name"] in ("Agent Frank Horrigan", "The Master, Transcendent"):
        card = http("https://api.scryfall.com/cards/" + x["scryfall_id"])
        out[x["name"]] = dict(carta=card, rulings=http(card["rulings_uri"])["data"], impressoes=http(card["prints_search_uri"] + "&unique=prints")["data"] and [(p["set"], p["collector_number"], p.get("flavor_name")) for p in http(card["prints_search_uri"] + "&unique=prints")["data"]])
        time.sleep(0.2)
json.dump(out, open(os.path.join(PAST, "rulings_candidatas.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for n, v in out.items():
    print("\n==", n, v["carta"]["mana_cost"], v["carta"]["type_line"], v["carta"].get("power"), v["carta"].get("toughness"), "| flavor_name:", v["carta"].get("flavor_name"), "| impressoes:", v["impressoes"])
    print(v["carta"].get("oracle_text") or [ff.get("oracle_text") for ff in v["carta"]["card_faces"]])
    for r in v["rulings"]: print("  *", r["published_at"], r["comment"])
