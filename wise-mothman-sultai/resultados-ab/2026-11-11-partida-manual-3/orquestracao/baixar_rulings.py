"""Baixa as rulings (Scryfall, ao vivo) das cartas da partida manual #3 do Wise Mothman (nomes lidos do próprio log).
Uso (da raiz do repositório): python3 -I <esta pasta>/orquestracao/baixar_rulings.py <saida.json>
Fichas e cartas sem ruling entram com lista vazia; erro de rede entra como {"erro": ...} (nunca silencioso)."""
import json, lzma, os, sys, time, urllib.parse, urllib.request
aqui = os.path.dirname(os.path.abspath(__file__))
T = json.load(lzma.open(os.path.join(aqui, "..", "dados", "partida.json.xz")))
nomes = sorted({r["name"].split(" // ")[0] for t in T for r in t if not r["token"]} - {"Forest"})
H = {"User-Agent": "MTG-Code-audit/1.0", "Accept": "application/json"}
out = {}
for n in nomes:
    u = "https://api.scryfall.com/cards/named?" + urllib.parse.urlencode({"exact": n})
    try:
        c = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H)))
        r = json.load(urllib.request.urlopen(urllib.request.Request(c["rulings_uri"], headers=H)))
        out[n] = {"oracle_id": c.get("oracle_id"), "rulings": [(x["published_at"], x["comment"]) for x in r["data"]]}
    except Exception as e:
        out[n] = {"erro": str(e)}
    time.sleep(0.12)
json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
print(len(out), "cartas;", sum(1 for v in out.values() if "erro" in v), "com erro;", sum(len(v.get("rulings", [])) for v in out.values()), "rulings")
