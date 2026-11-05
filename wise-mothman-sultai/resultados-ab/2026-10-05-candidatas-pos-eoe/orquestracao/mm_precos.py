"""Menor preco USD (nao-foil e foil) entre TODAS as impressoes (nao so' as pos-EOE) das cartas principais. Uso: python3 mm_precos.py <saida.json> nome1 nome2 ..."""
import json, sys, time, urllib.parse
sys.path.insert(0, "/home/user/MTG-Code/scryfall-cache/sets")
import fetch_set as F
out = {}
for n in sys.argv[2:]:
    q = '!"' + n + '"'
    url = "https://api.scryfall.com/cards/search?" + urllib.parse.urlencode({"q": q, "unique": "prints", "order": "released"})
    ps = []
    while url:
        d = F.get(url); ps += d["data"]; url = d.get("next_page"); time.sleep(0.1)
    rows = sorted((float(p["prices"]["usd"]), p["set"], p["collector_number"], p["released_at"]) for p in ps if p["prices"].get("usd"))
    rows_f = sorted((float(p["prices"]["usd_foil"]), p["set"], p["collector_number"], p["released_at"]) for p in ps if p["prices"].get("usd_foil"))
    out[n] = {"n_impressoes": len(ps), "mais_barata_nao_foil": rows[0] if rows else None, "mais_barata_foil": rows_f[0] if rows_f else None, "sets": sorted({p["set"] for p in ps})}
    print(n, "|", len(ps), "impressoes | nao-foil", rows[0] if rows else None, "| foil", rows_f[0] if rows_f else None)
json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
