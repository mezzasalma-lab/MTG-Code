"""Eventos do goldfish manual #5, um por linha, SO' de dados/goldfish_manual_5_bruto.json (sem interpretar).
Colunas: indice, carta, id (6 primeiros), movimento de zona ('.' = sem movimento: so' mudou estado), TAP se virada,
contadores (L = lealdade, V = Vow), TOKEN se ficha, imposto do comandante."""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(AQUI, "..", "dados", "goldfish_manual_5_bruto.json")))
for i, blk in enumerate(data, 1):
    print(f"=== T{i} ({len(blk)} eventos)")
    for j, e in enumerate(blk):
        fz, tz = e.get("fromZone"), e.get("toZone")
        mov = f"{fz}→{tz}" if (fz or tz) else "·"
        extra = []
        if e.get("tapped"): extra.append("TAP")
        for k, v in (e.get("counters") or {}).items():
            extra.append(f"{k[0]}{v['count']}")
        if e.get("token"): extra.append("TOKEN")
        if e.get("commandTax"): extra.append(f"imposto{e['commandTax']}")
        print(f"{j:4d} {e['name'][:34]:34s} {e['id'][:6]:6s}  {mov:26s} {' '.join(extra)}")
