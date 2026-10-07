"""Resume o A/B pareado de `LANDFALL_PAYOFF_FIRST` de um deck em tabela markdown (so' le o texto das tabelas `ab_*.txt` da pasta de resultados; as tabelas em si saem so' dos brutos `.json.xz` via `driver.py sum`).
Uso: python3 resume_ab_landfall.py <pasta-resultados> campo1,campo2,...   (campos como aparecem na tabela; 'cmd' = todos os `*cast_turn__ate_T*` e `*first_*_turn__*`)"""
import re, sys, os
pasta, campos = sys.argv[1], sys.argv[2].split(",")
def le(nome):
    t = open(os.path.join(pasta, "resumos", nome)).read()
    bloco = t.split("\n\n")
    rows = {}
    for b in bloco[1:2] if False else bloco:
        for l in b.split("\n"):
            m = re.match(r"\s*(\*?)(\S+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+([+-][\d.]+) ±([\d.]+)", l)
            if m:
                rows.setdefault(m.group(2), (m.group(1) == "*", float(m.group(3)), float(m.group(4)), float(m.group(5)), float(m.group(6))))
    ident = re.search(r"IDENTICO ao da base: (\d+) \(([\d.]+)%\)", t)
    return rows, ident.group(2) if ident else "?"
saida = []
for modo, nome in (("padrao", "ab_10000.txt"), ("resiliencia", "ab_10000_resiliencia.txt")):
    rows, ident = le(nome)
    saida.append((modo, rows, ident))
print(f"| campo (N=10.000 pareado) | padrao: base -> depois (dif ± IC95%) | resiliencia: base -> depois (dif ± IC95%) |")
print("|---|---|---|")
def fmt(r):
    if r is None: return "-"
    est, a, b, d, h = r
    return f"{a:.3f} -> {b:.3f} ({d:+.3f} ± {h:.3f}){' *' if est else ''}"
for c in campos:
    print(f"| `{c}` | {fmt(saida[0][1].get(c))} | {fmt(saida[1][1].get(c))} |")
print(f"| partidas com resultado idêntico ao da base | {saida[0][2]}% | {saida[1][2]}% |")
