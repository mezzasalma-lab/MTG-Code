"""Agrega as impressoes baixadas por oracle_id, calcula etiquetas por regex no oraculo e grava indice + listas por etiqueta.
Uso: python3 mm_candidatas.py <dados_dir> <resumos_dir>"""
import json, re, sys, collections, os, datetime
dados, resumos = sys.argv[1], sys.argv[2]
d = json.load(open(os.path.join(dados, "candidatas_impressoes_bruto.json")))["impressoes"]
HOJE = "2026-10-05"
sys.path.insert(0, "/home/user/MTG-Code/scryfall-cache/sets")
def oid(c): return c.get("oracle_id") or c["card_faces"][0].get("oracle_id")
def faces_text(c):
    if c.get("card_faces") and not (c.get("oracle_text") or "").strip():
        return "\n//\n".join(f"[{f['name']} {f.get('mana_cost','')} | {f.get('type_line','')}{(' '+f['power']+'/'+f['toughness']) if f.get('power') else ''}] {f.get('oracle_text','')}" for f in c["card_faces"])
    return c.get("oracle_text") or ""
by = collections.OrderedDict()
for c in d:
    by.setdefault(oid(c), []).append(c)
idx = {}
for o, ps in by.items():
    ps_sorted = sorted(ps, key=lambda c: (c["released_at"], c["set"]))
    c0 = ps_sorted[0]
    precos = [float(c["prices"]["usd"]) for c in ps if c["prices"].get("usd")] + [float(c["prices"]["usd_foil"]) for c in ps if c["prices"].get("usd_foil")]
    nome = c0["name"] if c0["layout"] != "reversible_card" else c0["card_faces"][0]["name"]
    idx[o] = dict(
        nome=nome, layout=c0["layout"], custo=c0.get("mana_cost") or " // ".join(f.get("mana_cost", "") for f in c0.get("card_faces", [])),
        cmc=c0.get("cmc"), tipo=c0.get("type_line") or " // ".join(f["type_line"] for f in c0.get("card_faces", [])),
        oraculo=faces_text(c0), pt=(c0.get("power"), c0.get("toughness")), ci="".join(c0["color_identity"]),
        sets=sorted({(c["released_at"], c["set"]) for c in ps}), primeiro_set=c0["set"], primeira_data=c0["released_at"],
        inedita=any(not c.get("reprint") for c in ps), game_changer=bool(c0.get("game_changer")), edhrec=c0.get("edhrec_rank"),
        usd_min=min(precos) if precos else None, produced=c0.get("produced_mana"), keywords=c0.get("keywords"),
        nao_lancada=all(c["released_at"] > HOJE for c in ps), set_names=sorted({c["set_name"] for c in ps}))
json.dump(idx, open(os.path.join(dados, "candidatas_indice.json"), "w"), ensure_ascii=False, indent=1)
print(len(idx), "cartas unicas;", sum(v["inedita"] for v in idx.values()), "ineditas;", sum(v["nao_lancada"] for v in idx.values()), "so' em sets ainda nao lancados")
