"""Detalha os combos 'quase' (falta 1 carta) da lista base cuja carta faltante existe no pool pos-EOE. Uso: python3 mm_quase_detalhe.py <lista.md> <dados_dir> <saida.json>"""
import json, os, re, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mm_csb as C
lista, dados, out = sys.argv[1:4]
base = C.parse(lista)
idx = json.load(open(os.path.join(dados, "candidatas_indice.json")))
pool = {v["nome"] for v in idx.values()}
r = C.query(base)
lista_set = set(base)
res = []
for c in r["almostIncluded"]:
    usos = [u["card"]["name"] for u in c["uses"]]
    faltam = [n for n in usos if n not in lista_set and n != C.CMD]
    if len(faltam) == 1 and faltam[0] in pool:
        res.append((faltam[0], c["id"], usos, [p["feature"]["name"] if "feature" in p else str(p) for p in c.get("produces", [])][:5]))
print(len(res), "combos 'quase' cuja carta faltante esta no pool pos-EOE")
det = {}
for falta, vid, usos, prod in sorted(res):
    try:
        x = json.load(urllib.request.urlopen(urllib.request.Request(f"https://backend.commanderspellbook.com/variants/{vid}/", headers={"User-Agent": "MTG-Code-audit/1.0"}), timeout=60))
    except Exception as e:
        x = {"erro": str(e)}
    det[vid] = {"falta": falta, "usos": usos, "produz": prod, "bracket": x.get("bracketTag"), "popularidade": x.get("popularity"), "requer_templates": [t["template"]["name"] for t in x.get("requires", [])],
                "prereq": ((x.get("easyPrerequisites") or "") + " | " + (x.get("notablePrerequisites") or "")).strip(" |"), "passos": x.get("description")}
    time.sleep(0.2)
json.dump(det, open(out, "w"), ensure_ascii=False, indent=1)
for vid, d in det.items():
    print(f"- falta {d['falta']} | usos {d['usos']} | templates {d['requer_templates']} | produz {d['produz']} | bracket {d['bracket']} | pop {d['popularidade']}")
