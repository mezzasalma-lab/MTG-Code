"""Baixa o oraculo (Scryfall `POST /cards/collection` por NOME) de toda carta distinta das listas de referencia (Moxfield) + das candidatas, grava em dados/oraculos_referencia.json.xz e acrescenta no `scryfall-cache/oracle-cache.json` o que faltar (Regra 15).
Uso: python3 oraculos_referencia.py <decks.jsonl> <saida.json.xz> <cache.json>"""
import json, lzma, os, sys, time, urllib.request
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
decks = [json.loads(l) for l in (lzma.open(sys.argv[1], "rt", encoding="utf-8") if sys.argv[1].endswith(".xz") else open(sys.argv[1], encoding="utf-8"))]; mox = [r for r in decks if "moxfield" in (r.get("url") or "")]
nomes = sorted({n for r in mox for tipo, l in r["cards"].items() for n, q in l})
print("cartas distintas nos", len(mox), "decks Moxfield:", len(nomes), flush=True)
def post(ids):
    rq = urllib.request.Request("https://api.scryfall.com/cards/collection", data=json.dumps({"identifiers": ids}).encode(), headers={"Content-Type": "application/json", "User-Agent": "MTG-Code-audit/1.0", "Accept": "application/json"})
    for t in range(4):
        try: return json.load(urllib.request.urlopen(rq, timeout=90))
        except Exception: time.sleep(2 * (t + 1))
    raise RuntimeError("scryfall")
dados = {}; nf = []
for i in range(0, len(nomes), 70):
    r = post([{"name": n.split(" // ")[0] if " // " in n else n} for n in nomes[i:i + 70]])
    for c in r["data"]: dados[c["name"]] = c
    nf += [x.get("name") for x in r.get("not_found", [])]; time.sleep(0.15)
print("resolvidas:", len(dados), "| nao encontradas:", nf, flush=True)
CAMPOS = ['cmc', 'collector_number', 'color_identity', 'colors', 'keywords', 'legalities', 'loyalty', 'mana_cost', 'name', 'oracle_text', 'power', 'prices', 'released_at', 'scryfall_uri', 'set', 'toughness', 'type_line']
slim = {}
for n, c in dados.items():
    txt = c.get("oracle_text") or " // ".join(f.get("oracle_text", "") for f in c.get("card_faces", []))
    slim[n] = {f: c.get(f) for f in CAMPOS}; slim[n]["oracle_text"] = txt; slim[n]["game_changer"] = c.get("game_changer"); slim[n]["layout"] = c.get("layout")
    slim[n]["type_line"] = c.get("type_line")
json.dump(slim, lzma.open(sys.argv[2], "wt", preset=9), ensure_ascii=False)
cache = json.load(open(sys.argv[3], encoding="utf-8")); add = 0
for n, e in slim.items():
    if n not in cache and e["oracle_text"]:
        cache[n] = {f: e.get(f) for f in CAMPOS}; add += 1
open(sys.argv[3], "w", encoding="utf-8").write(json.dumps(cache, indent=2, ensure_ascii=False) + "\n")
print("acrescentadas ao cache:", add, "| cache:", len(cache), flush=True)
