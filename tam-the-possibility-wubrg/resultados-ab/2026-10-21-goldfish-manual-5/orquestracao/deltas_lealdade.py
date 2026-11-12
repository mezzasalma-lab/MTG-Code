"""Deltas de lealdade/Vow do goldfish manual #5, SO' do bruto: para cada bloco, a sequencia de mudancas de contador por permanente, em ordem de evento,
com o delta em relacao ao valor anterior visto (o do fim do bloco anterior no inicio do bloco). Nao interpreta: 'o que foi' fica no LEIAME.md."""
import json, os, collections
AQUI = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(AQUI, "..", "dados", "goldfish_manual_5_bruto.json")))
last = {}
for t, blk in enumerate(data, 1):
    print(f"=== T{t}")
    seq = []
    for j, e in enumerate(blk):
        for k, v in (e.get("counters") or {}).items():
            key = (e["name"], k)
            n = v["count"]
            old = last.get(key, 0)
            if n != old:
                seq.append((j, e["name"].split(",")[0], k[0], old, n))
            last[key] = n
        # carta que sai do campo / volta a zero
        if e.get("fromZone") == "battlefield" and e.get("toZone") in ("graveyard", "exile", "commandZone"):
            for key in list(last):
                if key[0] == e["name"]:
                    pass
    for j, nm, k, old, n in seq:
        print(f"  ev{j:3d} {nm:12s} {k}: {old:2d} -> {n:2d}  ({n-old:+d})")
