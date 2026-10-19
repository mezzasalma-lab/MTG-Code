"""Rulings (Scryfall, `rulings_uri`) de TODAS as cartas do deck do Tam (comandante + 99), lidos ANTES de codificar (Regras #1/#3 de CLAUDE.md).
Grava dados/rulings_deck.json (oraculo + game_changer + rulings por carta). Uso: python3 rulings_deck.py <lista.md> <saida.json>   (consulta API ao vivo; o bruto fica arquivado)"""
import json, os, re, sys, time, urllib.request
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
H = {"User-Agent": "MTG-Code-audit/1.0", "Accept": "application/json", "Content-Type": "application/json"}
def get(url, data=None):
    for t in range(5):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, data=data, headers=H), timeout=90))
        except Exception: time.sleep(2 * (t + 1))
    raise RuntimeError(url)
lista, saida = sys.argv[1], sys.argv[2]
txt = open(lista, encoding="utf-8").read()
nomes = ["Tam, the Possibility"] + [m.group(1).strip() for m in re.finditer(r"^1 (.+)$", txt.split("## Deck (99)")[1].split("## Sideboard")[0], re.M)]
out = {}
for i in range(0, len(nomes), 70):
    r = get("https://api.scryfall.com/cards/collection", json.dumps({"identifiers": [{"name": n} for n in nomes[i:i + 70]]}).encode())
    assert not r.get("not_found"), r["not_found"]
    for c in r["data"]:
        rul = get(c["rulings_uri"])["data"]
        out[c["name"]] = {"id": c["id"], "layout": c.get("layout"), "oracle_text": c.get("oracle_text") or " // ".join(f.get("oracle_text", "") for f in c.get("card_faces", [])),
                          "type_line": c["type_line"], "mana_cost": c.get("mana_cost"), "loyalty": c.get("loyalty"), "game_changer": c.get("game_changer"),
                          "rulings": [[x["published_at"], x["comment"]] for x in rul]}
        time.sleep(0.08)
json.dump(out, open(saida, "w"), ensure_ascii=False, indent=1)
print(len(out), "cartas;", sum(len(v["rulings"]) for v in out.values()), "rulings;", sum(1 for v in out.values() if v["rulings"]), "cartas com ruling")
