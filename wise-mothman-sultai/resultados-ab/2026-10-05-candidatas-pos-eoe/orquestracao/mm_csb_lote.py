"""Spellbook em lote: base + cada candidata (sem cortar), com resolucao de nome via /cards e registro dos nomes nao reconhecidos.
Uso: python3 mm_csb_lote.py <lista.md> <shortlist.json> <saida.json> [workers]"""
import json, os, re, sys, time, urllib.request, urllib.parse, collections, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mm_csb as C
lista, slf, out = sys.argv[1], sys.argv[2], sys.argv[3]
W = int(sys.argv[4]) if len(sys.argv) > 4 else 3
base = C.parse(lista)
sl = json.load(open(slf))
cands = []
for g, l in sl.items():
    for n in l:
        if n not in base and n != C.CMD and n not in [c for c, _ in cands]:
            cands.append((n, g))
def g(url):
    for t in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "MTG-Code-audit/1.0"}), timeout=90))
        except Exception as e:
            time.sleep(2 * (t + 1))
    raise RuntimeError(url)
def resolve(n):
    d = g("https://backend.commanderspellbook.com/cards/?" + urllib.parse.urlencode({"q": n, "limit": 10}))
    nomes = [x["name"] for x in d["results"]]
    for x in nomes:
        if x.lower() == n.lower(): return x
    for x in nomes:
        if x.split(" // ")[0].lower() == n.split(" // ")[0].lower(): return x
    return None
base_res = C.query(base); binc, balm = C.resumo(base_res)
print("base: incluidos", len(binc), "quase", len(balm), flush=True)
def um(item):
    n, grp = item
    nome_sb = resolve(n)
    if not nome_sb:
        return n, {"grupo": grp, "spellbook_reconhece": False}
    for t in range(3):
        try:
            r = C.query(base + [nome_sb]); break
        except Exception:
            time.sleep(3 * (t + 1))
    else:
        return n, {"grupo": grp, "spellbook_reconhece": True, "erro": "consulta falhou"}
    inc, alm = C.resumo(r)
    novos = {k: v for k, v in inc.items() if k not in binc}
    sumiram = [k for k in binc if k not in inc]
    alm_novos = sorted(set(alm) - set(balm))
    alm_com = [k for k in alm_novos if nome_sb in k]
    return n, {"grupo": grp, "spellbook_reconhece": True, "nome_spellbook": nome_sb, "incluidos_novos": novos, "incluidos_sumiram": sumiram,
               "n_quase_novos": len(alm_novos), "quase_novos_com_a_carta": alm_com[:40], "identidade": r.get("identity")}
res = {}
with cf.ThreadPoolExecutor(W) as ex:
    futs = {ex.submit(um, c): c for c in cands}
    for i, f in enumerate(cf.as_completed(futs), 1):
        n, v = f.result(); res[n] = v
        if i % 10 == 0: print(i, "/", len(cands), flush=True)
json.dump({"base": {"incluidos": binc, "quase": balm}, "candidatas": res}, open(out, "w"), ensure_ascii=False, indent=1)
print("fim:", len(res), "candidatas;", sum(1 for v in res.values() if not v["spellbook_reconhece"]), "nao reconhecidas pelo Spellbook")
