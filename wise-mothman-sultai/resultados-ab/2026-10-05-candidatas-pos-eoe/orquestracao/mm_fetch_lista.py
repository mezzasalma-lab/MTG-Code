"""Baixa do Scryfall as cartas da lista do usuario (Mothman) por SET + NUMERO DE COLECIONADOR (resolve flavor_name, Regra #2),
grava dados brutos (carta + rulings) e atualiza o scryfall-cache/oracle-cache.json (Regras 14/15).
Uso: python3 mm_fetch_lista.py <lista-original-usuario.txt> <saida_dir>"""
import json, re, sys, time, urllib.request, os
sys.path.insert(0, "/home/user/MTG-Code/scryfall-cache/sets")
import fetch_set as F
H = F.H
lista, saida = sys.argv[1], sys.argv[2]
os.makedirs(saida, exist_ok=True)
rows = []
for ln in open(lista, encoding="utf-8"):
    ln = ln.strip()
    if not ln:
        continue
    m = re.match(r"(\d+) (.+?) \((\w+)\) (\S+?)(?: \*F\*)?$", ln)
    assert m, ln
    n, nome, st, num = m.groups()
    rows.append((int(n), nome, st.lower(), num))
print(len(rows), "linhas;", sum(r[0] for r in rows), "cartas")

def post(ids):
    req = urllib.request.Request("https://api.scryfall.com/cards/collection", data=json.dumps({"identifiers": ids}).encode(),
                                 headers={**H, "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))

res, miss = {}, []
for i in range(0, len(rows), 40):
    lote = rows[i:i + 40]
    d = post([{"set": r[2], "collector_number": r[3]} for r in lote])
    got = {(c["set"], c["collector_number"]): c for c in d["data"]}
    for r in lote:
        c = got.get((r[2], r[3]))
        if c is None:
            miss.append(r)
        else:
            res[r] = c
    time.sleep(0.15)
print("achadas por set+numero:", len(res), "| faltando:", miss)
# falhas: tenta pelo nome (face da frente) e sem o simbolo de estrela
for r in miss:
    nome = r[1].split(" / ")[0]
    url = "https://api.scryfall.com/cards/named?fuzzy=" + urllib.request.quote(nome)
    try:
        res[r] = F.get(url)
        print("  por nome:", r, "->", res[r]["name"], res[r]["set"], res[r]["collector_number"])
    except Exception as e:
        print("  FALHOU:", r, e)
    time.sleep(0.12)
out = []
for r, c in res.items():
    rul = F.get(c["rulings_uri"])["data"]; time.sleep(0.1)
    out.append({"linha": {"n": r[0], "nome_usuario": r[1], "set": r[2], "num": r[3]}, "carta": c, "rulings": rul})
json.dump(out, open(os.path.join(saida, "lista_bruto.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
cache = json.load(open(F.CACHE, encoding="utf-8"))
novas = 0
for o in out:
    c = o["carta"]
    e = F.entry(c)
    if c.get("layout") == "reversible_card":   # ex.: Overgrown Tomb (ECL 350): as duas faces sao a mesma carta; a chave do cache e' o nome da carta real
        c = {**c, "name": c["card_faces"][0]["name"]}
        e["name"] = c["name"]
    if c["name"] not in cache or not (cache[c["name"]].get("oracle_text") or "").strip():
        cache[c["name"]] = e
        novas += 1
json.dump(cache, open(F.CACHE, "w", encoding="utf-8"), indent=2, ensure_ascii=False); open(F.CACHE, "a").write("\n")
print("cache: +", novas, "| total", len(cache))
