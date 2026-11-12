"""Baixa AO VIVO do Scryfall o oraculo e as RULINGS de cada carta unica de rat-king-verminister/lista.md (Regra #1 item 1, Regra #3 item 2).
Saida: dados/scryfall_oraculo_rulings_2026-10-25.json  (nome da lista -> carta resolvida, oracle_id, type_line, keywords, oracle_text por face, rulings).
Regra #2: se o nome exato nao existe, busca `/cards/search?q="Nome"` e usa a carta cujo `flavor_name` bate. Registra como cada nome foi resolvido.
Uso: python3 -I scry_rulings.py <lista.md> <saida.json>"""
import json, os, re, sys, time, urllib.request, urllib.parse
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
def http(url, tries=5):
    for t in range(tries):
        try:
            rq = urllib.request.Request(url, headers={"User-Agent": "MTG-Code-audit/1.0", "Accept": "application/json"})
            return json.load(urllib.request.urlopen(rq, timeout=60))
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(2 * (t + 1))
        except Exception:
            time.sleep(2 * (t + 1))
    raise RuntimeError(url)
def parse(path):
    nomes = []; sec = None
    for l in open(path, encoding="utf-8"):
        l = l.rstrip("\n")
        if l.startswith("## "): sec = l[3:].strip(); continue
        m = re.match(r"^(\d+)\s+(.+)$", l)
        if m: nomes.append((sec, m.group(2).strip(), int(m.group(1))))
    return nomes
def resolve(n):
    q = urllib.parse.quote(n)
    c = http(f"https://api.scryfall.com/cards/named?exact={q}")
    how = "exact"
    if c is None:
        c = http(f"https://api.scryfall.com/cards/named?fuzzy={q}"); how = "fuzzy"
    if c is None or (how == "fuzzy" and c.get("name", "").lower().split(" // ")[0] != n.lower().split(" // ")[0]):
        s = http("https://api.scryfall.com/cards/search?q=" + urllib.parse.quote(f'"{n}"'))
        c = None; how = "flavor_name"
        for x in (s or {}).get("data", []):
            if (x.get("flavor_name") or "").lower() == n.lower(): c = x; break
    return c, how
if __name__ == "__main__":
    lista, out = sys.argv[1], sys.argv[2]
    itens = parse(lista); res = {}
    for sec, n, q in itens:
        time.sleep(0.12)
        c, how = resolve(n)
        if c is None: res[n] = {"secao": sec, "qtd": q, "resolvido": None, "como": how}; print("NAO RESOLVIDO:", n, flush=True); continue
        rul = http(c["rulings_uri"]) if c.get("rulings_uri") else {"data": []}
        time.sleep(0.12)
        faces = c.get("card_faces") or [c]
        res[n] = {"secao": sec, "qtd": q, "resolvido": c["name"], "como": how, "oracle_id": c.get("oracle_id"), "layout": c.get("layout"),
                  "type_line": c.get("type_line") or " // ".join(f.get("type_line", "") for f in faces), "keywords": c.get("keywords"),
                  "mana_cost": c.get("mana_cost") or " // ".join(f.get("mana_cost", "") for f in faces), "game_changer": c.get("game_changer"),
                  "faces": [{"name": f.get("name"), "type_line": f.get("type_line"), "oracle_text": f.get("oracle_text"), "power": f.get("power"), "toughness": f.get("toughness")} for f in faces],
                  "rulings": [{"published_at": r["published_at"], "comment": r["comment"]} for r in (rul or {}).get("data", [])]}
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
    nr = [n for n, v in res.items() if v["resolvido"] is None]
    print("cartas unicas:", len(res), "| nao resolvidas:", nr, "| total de rulings:", sum(len(v.get("rulings", [])) for v in res.values()))
