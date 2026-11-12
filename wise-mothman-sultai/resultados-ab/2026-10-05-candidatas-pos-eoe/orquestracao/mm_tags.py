"""Etiquetas por regex sobre o oraculo do indice de candidatas. Uso: python3 mm_tags.py <dados_dir> <tag> [--so-ineditas]"""
import json, re, sys
idx = json.load(open(sys.argv[1] + "/candidatas_indice.json"))
TAGS = {
 "rad": r"rad counter",
 "prolif": r"proliferate",
 "dobra": r"that many plus|twice that many|plus one of each|double the number of (\+1/\+1 )?counters|that many more (\+1/\+1 )?counters|one additional (\+1/\+1 )?counter|additional \+1/\+1 counter|put(s)? (twice|double)|triple the number|would put .{0,40}counters?.{0,40}instead",
 "trample": r"trample",
 "mill": r"\bmills?\b|\bmilled\b|\bmilling\b",
 "p1p1": r"\+1/\+1 counter",
 "contador_gatilho": r"whenever (one or more )?(.{0,40})counters? (is|are|would be) (put|placed)|whenever you put (one or more )?(.{0,30})counters?|for the first time each turn",
}
tag = sys.argv[2]
so_ined = "--so-ineditas" in sys.argv
rx = re.compile(TAGS[tag], re.I)
out = []
for o, v in idx.items():
    if rx.search(v["oraculo"]):
        if so_ined and not v["inedita"]: continue
        out.append(v)
out.sort(key=lambda v: (v["cmc"] or 0, v["nome"]))
print(f"## tag={tag}: {len(out)} cartas ({sum(v['inedita'] for v in out)} ineditas)")
for v in out:
    sets = ",".join(sorted({s for _, s in v["sets"]}))
    pt = f" {v['pt'][0]}/{v['pt'][1]}" if v["pt"][0] is not None else ""
    print(f"### {v['nome']} {v['custo']} | {v['tipo']}{pt} | {v['ci'] or 'C'} | [{sets}]{' INEDITA' if v['inedita'] else ''}{' GC' if v['game_changer'] else ''}{' NAO-LANCADA' if v['nao_lancada'] else ''} ${v['usd_min']}")
    print("   " + v["oraculo"].replace("\n", "\n   "))
