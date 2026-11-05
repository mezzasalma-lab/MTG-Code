"""Compara a lista atual do Mothman (lista.md) com a do Stefano (dados/lista_stefano_resolvida.json), por NOME REAL (Scryfall, set+numero; Regra #2).
Saida: resumos/diff_listas.md + dados/diff_listas.json. Uso: python3 diff_listas.py"""
import json, os, re, collections
AQUI = os.path.dirname(os.path.abspath(__file__)); DADOS = os.path.join(AQUI, "..", "dados"); RES = os.path.join(AQUI, "..", "resumos")
LISTA = os.path.join(AQUI, "..", "..", "..", "lista.md")
cache = json.load(open(os.path.join(AQUI, "..", "..", "..", "..", "scryfall-cache", "oracle-cache.json"), encoding="utf-8"))
nossa = collections.Counter(); sec = None
for l in open(LISTA, encoding="utf-8"):
    l = l.rstrip("\n")
    if l.startswith("#"): sec = l.lstrip("# ").strip().lower(); continue
    m = re.match(r"^(\d+)\s+(.+)$", l)
    if m and sec: nossa[m.group(2).strip()] += int(m.group(1))
st = json.load(open(os.path.join(DADOS, "lista_stefano_resolvida.json"), encoding="utf-8"))
dele = collections.Counter()
info = {}
for x in st:
    dele[x["name"]] += x["qtd"]; info[x["name"]] = x
BAS = {"Forest", "Island", "Swamp"}
def norm(n): return n.replace(" // ", " / ")
nossa_n = {norm(k): v for k, v in nossa.items()}; dele_n = {norm(k): v for k, v in dele.items()}
comuns = sorted(k for k in nossa_n if k in dele_n and k not in BAS)
so_dele = sorted(k for k in dele_n if k not in nossa_n and k not in BAS)
so_nosso = sorted(k for k in nossa_n if k not in dele_n and k not in BAS)
def tipo(n):
    x = info.get(n) or info.get(n.replace(" / ", " // "))
    if x: return x["type_line"]
    c = cache.get(n) or cache.get(n.replace(" / ", " // ")) or {}
    return c.get("type_line", "?")
linhas = []
P = linhas.append
P(f"# Mothman: nossa lista × lista do Stefano (por nome REAL, Scryfall set+número)\n")
P(f"- Nossa lista: {sum(nossa.values())} cartas ({len(nossa)} nomes distintos); Stefano: {sum(dele.values())} cartas ({len(dele)} nomes distintos).")
P(f"- Básicos: nossa {dict((b, nossa.get(b, 0)) for b in sorted(BAS))}; Stefano {dict((b, dele.get(b, 0)) for b in sorted(BAS))}.")
P(f"- **Em comum (não-básicos): {len(comuns)}**; só no Stefano: {len(so_dele)}; só na nossa: {len(so_nosso)}.\n")
P("## Em comum\n"); P(", ".join(comuns) + "\n")
def terra(n): return "Land" in tipo(n)
for titulo, lst in (("Só no Stefano", so_dele), ("Só na nossa", so_nosso)):
    P(f"## {titulo} ({len(lst)}; terrenos {sum(terra(n) for n in lst)}, não-terrenos {sum(not terra(n) for n in lst)})\n")
    P("| carta | tipo | custo |\n|---|---|---|")
    for n in sorted(lst, key=lambda n: (terra(n), n)):
        x = info.get(n) or info.get(n.replace(" / ", " // ")) or {}
        c = cache.get(n) or cache.get(n.replace(" / ", " // ")) or {}
        P(f"| {n} | {tipo(n)} | {x.get('mana_cost') or c.get('mana_cost', '')} |")
    P("")
open(os.path.join(RES, "diff_listas.md"), "w", encoding="utf-8").write("\n".join(linhas) + "\n")
json.dump(dict(comuns=comuns, so_dele=so_dele, so_nosso=so_nosso, nossa=dict(nossa), dele=dict(dele)), open(os.path.join(DADOS, "diff_listas.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("\n".join(linhas))
