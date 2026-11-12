"""Gera a lista completa (markdown) de candidatas por etiqueta a partir do indice. Uso: python3 mm_listas_por_etiqueta.py <dados_dir> <saida.md>"""
import json, re, sys
idx = json.load(open(sys.argv[1] + "/candidatas_indice.json"))
TAGS = [
 ("rad", "Rad counters", r"rad counter"),
 ("prolif", "Proliferate", r"proliferate"),
 ("dobra", "Amplificadores/dobradores de contador", r"that many plus|twice that many|plus one of each|double the number of (\+1/\+1 )?counters|that many more (\+1/\+1 )?counters|one additional (\+1/\+1 )?counter|additional \+1/\+1 counter|put(s)? (twice|double)|triple the number|would put .{0,40}counters?.{0,40}instead"),
 ("mill", "Mill", r"\bmills?\b|\bmilled\b|\bmilling\b"),
 ("contador_gatilho", "Gatilhos de 'quando um contador e' colocado'", r"whenever (one or more )?(.{0,40})counters? (is|are|would be) (put|placed)|whenever you put (one or more )?(.{0,30})counters?|for the first time each turn"),
]
KW_ONLY = re.compile(r"\s*((flying|trample|vigilance|haste|reach|menace|deathtouch|lifelink|first strike|double strike|hexproof|indestructible|ward \{?\d\}?|defender|flash)[, ]*)+\s*", re.I)
def tem_trample_concedido(t):
    t2 = re.sub(r"\([^)]*\)", "", t)
    ls = [l for l in t2.split("\n") if re.search("trample", l, re.I) and not KW_ONLY.fullmatch(l) and not re.fullmatch(r"\s*[A-Za-z' ,]+\s*", l)]
    return bool(ls)
def linha(v):
    sets = ",".join(sorted({s for _, s in v["sets"]}))
    flags = ("INEDITA " if v["inedita"] else "") + ("GC " if v["game_changer"] else "") + ("NAO-LANCADA" if v["nao_lancada"] else "")
    pt = f" {v['pt'][0]}/{v['pt'][1]}" if v["pt"][0] is not None else ""
    return f"| {v['nome']} | {v['custo'] or ''} | {v['tipo']}{pt} | {v['ci'] or 'C'} | {sets} | {flags.strip()} | {v['usd_min'] if v['usd_min'] is not None else '-'} | {v['edhrec'] or '-'} |"
out = ["# Candidatas pos-EOE por etiqueta (gerado por `mm_listas_por_etiqueta.py` a partir de `dados/candidatas_indice.json`)\n",
       "Filtro de origem: Scryfall `f:commander id<=bug date>=2025-08-01`, `unique=prints`, agrupado por `oracle_id`. "
       "As etiquetas sao regex sobre o oraculo (triagem, nao julgamento): conferir o texto antes de concluir. `INEDITA` = alguma impressao nao e' reimpressao; "
       "`NAO-LANCADA` = todas as impressoes tem data futura (hoje 2026-10-05). Preco = menor USD (foil ou nao) entre as impressoes da janela.\n"]
cab = "| Carta | Custo | Tipo | Id | Sets | Flags | USD | EDHREC |\n|---|---|---|---|---|---|---|---|"
for tag, titulo, rx in TAGS:
    sel = [v for v in idx.values() if re.search(rx, v["oraculo"], re.I)]
    sel.sort(key=lambda v: (v["cmc"] or 0, v["nome"]))
    out += [f"\n## {titulo} ({len(sel)})\n", cab] + [linha(v) for v in sel]
sel = [v for v in idx.values() if tem_trample_concedido(v["oraculo"])]
sel.sort(key=lambda v: (v["cmc"] or 0, v["nome"]))
out += [f"\n## Trample concedido/condicional (linhas de oraculo com 'trample' que nao sao so' a palavra-chave) ({len(sel)})\n", cab] + [linha(v) for v in sel]
terr = [v for v in idx.values() if re.search(r"\bLand\b", v["tipo"].split("//")[0]) and not v["tipo"].startswith("Basic") and len(set(v["produced"] or []) & set("BGU")) >= 2 and "Spend this mana only" not in v["oraculo"]]
terr.sort(key=lambda v: v["nome"])
out += [f"\n## Terrenos que produzem 2+ de B/G/U sem restricao de gasto ({len(terr)})\n", cab] + [linha(v) for v in terr]
open(sys.argv[2], "w").write("\n".join(out) + "\n")
print("linhas:", len(out))
