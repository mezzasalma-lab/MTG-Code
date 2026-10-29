"""Resolve a lista do Stefano por SET + NUMERO DE COLECIONADOR no Scryfall (Regra #2: o nome impresso pode ser flavor_name).
Grava dados/lista_stefano_resolvida.json: [{qtd, impresso, set, num, name, flavor_name, type_line, mana_cost, cmc, oracle_text, color_identity, scryfall_id, oracle_id}].
Uso: python3 resolve_stefano.py"""
import json, os, re, sys, time, urllib.request, urllib.error
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
AQUI = os.path.dirname(os.path.abspath(__file__)); DADOS = os.path.join(AQUI, "..", "dados")
linhas = []
for l in open(os.path.join(DADOS, "lista_stefano_original.txt"), encoding="utf-8"):
    m = re.match(r"^(\d+)\s+(.+?)\s+\((\w+)\)\s+(\S+?)(?:\s+\*F\*)?\s*$", l.strip())
    assert m, l
    linhas.append(dict(qtd=int(m.group(1)), impresso=m.group(2), set=m.group(3).lower(), num=m.group(4)))
def http(url, data=None, tries=4):
    for t in range(tries):
        try:
            rq = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "Accept": "application/json;q=0.9,*/*;q=0.8", "User-Agent": "MTG-Code-audit/1.0"})
            return json.load(urllib.request.urlopen(rq, timeout=120))
        except urllib.error.HTTPError as e:
            err = (e, e.read()[:300]); time.sleep(2 * (t + 1))
        except Exception as e:
            err = e; time.sleep(2 * (t + 1))
    raise RuntimeError((url, err))
out = []; nao = []
for i in range(0, len(linhas), 50):
    lote = linhas[i:i + 50]
    r = http("https://api.scryfall.com/cards/collection", json.dumps({"identifiers": [{"set": x["set"], "collector_number": x["num"]} for x in lote]}).encode())
    achados = {(c["set"], c["collector_number"]): c for c in r["data"]}
    for x in lote:
        c = achados.get((x["set"], x["num"]))
        if c is None:
            nao.append(x); continue
        f = c.get("card_faces") or []
        txt = c.get("oracle_text") or "\n//\n".join(ff.get("oracle_text", "") for ff in f)
        out.append(dict(x, name=c["name"], flavor_name=c.get("flavor_name"), type_line=c.get("type_line"), mana_cost=c.get("mana_cost") or (f[0].get("mana_cost") if f else ""),
                        cmc=c.get("cmc"), oracle_text=txt, color_identity=c.get("color_identity"), scryfall_id=c["id"], oracle_id=c.get("oracle_id"),
                        power=c.get("power"), toughness=c.get("toughness"), loyalty=c.get("loyalty")))
    time.sleep(0.2)
json.dump(out, open(os.path.join(DADOS, "lista_stefano_resolvida.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("resolvidas", len(out), "de", len(linhas), "| NAO resolvidas:", [(x["impresso"], x["set"], x["num"]) for x in nao])
print("com flavor_name:", [(x["impresso"], x["flavor_name"], x["name"]) for x in out if x["flavor_name"]])
print("impresso != name (sem flavor_name):", [(x["impresso"], x["name"]) for x in out if x["impresso"] != x["name"] and not x["flavor_name"]])
print("copias totais:", sum(x["qtd"] for x in out))
