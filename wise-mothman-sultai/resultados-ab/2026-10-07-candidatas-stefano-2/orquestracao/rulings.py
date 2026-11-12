"""Baixa oraculo + RULINGS ao vivo (Scryfall, por set+numero da lista do Stefano) das 6 candidatas: Fractured Sanity, Screeching Scorchbeast, Inexorable Tide, Branching Evolution, Loading Zone,
The Earth Crystal. Regra #3 (reincidencia 2026-09-29): ler as rulings ANTES de escrever o codigo. Grava dados/rulings_candidatas2.json. Uso: python3 rulings.py"""
import json, os, time, urllib.request
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
AQUI = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(AQUI, "..", "dados")
st = json.load(open(os.path.join(AQUI, "..", "..", "2026-10-07-comparacao-stefano", "dados", "lista_stefano_resolvida.json"), encoding="utf-8"))
NOMES = ["Fractured Sanity", "Screeching Scorchbeast", "Inexorable Tide", "Branching Evolution", "Loading Zone", "The Earth Crystal"]
def http(url):
    for t in range(4):
        try:
            rq = urllib.request.Request(url, headers={"Accept": "application/json;q=0.9,*/*;q=0.8", "User-Agent": "MTG-Code-audit/1.0"})
            return json.load(urllib.request.urlopen(rq, timeout=120))
        except Exception as e:
            err = e; time.sleep(2 * (t + 1))
    raise RuntimeError(err)
out = {}
for n in NOMES:
    x = next(c for c in st if c["name"] == n)
    card = http("https://api.scryfall.com/cards/" + x["scryfall_id"])
    out[n] = dict(card={k: card.get(k) for k in ("name", "flavor_name", "mana_cost", "type_line", "oracle_text", "power", "toughness", "keywords", "set", "collector_number", "game_changer")},
                  rulings=http(card["rulings_uri"])["data"])
    time.sleep(0.15)
json.dump(out, open(os.path.join(D, "rulings_candidatas2.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for n, v in out.items():
    print("\n==", n, v["card"]["mana_cost"], "|", v["card"]["type_line"], "| flavor_name:", v["card"]["flavor_name"], "| game_changer:", v["card"]["game_changer"])
    print(v["card"]["oracle_text"])
    for r in v["rulings"]: print("  *", r["published_at"], r["comment"])
