"""Baixa ao vivo do Scryfall o oraculo + rulings de cada carta que aparece no log da partida manual (nomes lidos de dados/oraculo_ao_vivo.json
e do proprio log). Salva dados/oraculo_rulings_ao_vivo.json. Uso: python3 oraculo_com_rulings.py"""
import json, os, time, urllib.parse, urllib.request
AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, "..", "dados")
nomes = [n for n in json.load(open(os.path.join(DADOS, "oraculo_ao_vivo.json"))) if n != "Pentavite"]  # Pentavite e' ficha do oponente (marcador)
extra = ["Vihaan, Goldwaker"]


def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "mtg-code-audit/1.0", "Accept": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))

out = {}
for n in dict.fromkeys(nomes + extra):
    c = get("https://api.scryfall.com/cards/named?exact=" + urllib.parse.quote(n))
    time.sleep(0.12)
    r = get(c["rulings_uri"])["data"]
    time.sleep(0.12)
    out[n] = {"name": c["name"], "type_line": c.get("type_line"), "mana_cost": c.get("mana_cost"), "oracle_text": c.get("oracle_text"),
              "card_faces": c.get("card_faces"), "power": c.get("power"), "toughness": c.get("toughness"),
              "rulings": [{"published_at": x["published_at"], "comment": x["comment"]} for x in r]}
json.dump(out, open(os.path.join(DADOS, "oraculo_rulings_ao_vivo.json"), "w"), ensure_ascii=False, indent=1)
print(len(out), "cartas,", sum(len(v["rulings"]) for v in out.values()), "rulings")
