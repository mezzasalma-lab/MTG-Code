"""Game Changers (campo `game_changer` do Scryfall, ao vivo) e legalidade em Commander das duas listas; grava dados/game_changers.json. Uso: python3 game_changers.py"""
import json, os, time, urllib.request
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
AQUI = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(AQUI, "..", "dados")
st = json.load(open(os.path.join(D, "lista_stefano_resolvida.json"), encoding="utf-8"))
dif = json.load(open(os.path.join(D, "diff_listas.json"), encoding="utf-8"))
nomes_nossos = sorted(dif["nossa"]); 
def http(url, data=None):
    for t in range(4):
        try:
            rq = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "Accept": "application/json;q=0.9,*/*;q=0.8", "User-Agent": "MTG-Code-audit/1.0"})
            return json.load(urllib.request.urlopen(rq, timeout=120))
        except Exception as e:
            err = e; time.sleep(2 * (t + 1))
    raise RuntimeError(err)
out = {"stefano": {}, "nossa": {}}
r = http("https://api.scryfall.com/cards/collection", json.dumps({"identifiers": [{"id": x["scryfall_id"]} for x in st[:75]]}).encode())
cards = r["data"]
r = http("https://api.scryfall.com/cards/collection", json.dumps({"identifiers": [{"id": x["scryfall_id"]} for x in st[75:]]}).encode())
cards += r["data"]
for c in cards: out["stefano"][c["name"]] = dict(game_changer=c.get("game_changer"), commander=c["legalities"]["commander"], prices=c.get("prices", {}).get("usd"))
nn = [n for n in nomes_nossos if n not in ("Forest", "Island", "Swamp")]
for i in range(0, len(nn), 70):
    lote = nn[i:i + 70]
    r = http("https://api.scryfall.com/cards/collection", json.dumps({"identifiers": [{"name": n.split(" / ")[0] if " / " in n else n} for n in lote]}).encode())
    for c in r["data"]: out["nossa"][c["name"]] = dict(game_changer=c.get("game_changer"), commander=c["legalities"]["commander"], prices=c.get("prices", {}).get("usd"))
    print("nao encontradas:", r.get("not_found"))
json.dump(out, open(os.path.join(D, "game_changers.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for k in ("nossa", "stefano"):
    gc = [n for n, v in out[k].items() if v["game_changer"]]
    ilegal = [n for n, v in out[k].items() if v["commander"] != "legal"]
    print(k, "cartas:", len(out[k]), "Game Changers:", gc, "nao legais:", ilegal)
