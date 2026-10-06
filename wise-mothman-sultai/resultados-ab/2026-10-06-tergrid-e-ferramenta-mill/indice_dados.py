"""Lista os dados brutos desta pasta: para cada dados/*.json.xz do mill_oponentes, modo, N, sementes, variantes (com flags) e partidas. Uso: python3 indice_dados.py"""
import glob, json, lzma, os
aqui = os.path.dirname(os.path.abspath(__file__))
print("| arquivo | modo | N | sementes | variantes (flags; partidas) |")
print("|---|---|---|---|---|")
for f in sorted(glob.glob(os.path.join(aqui, "dados", "*.json.xz"))):
    d = json.load(lzma.open(f, "rt"))
    vs = "; ".join(f"`{n}` {json.dumps(v['flags'], ensure_ascii=False)} ({len(v['partidas'])})" for n, v in d["variantes"].items())
    assert d["n"] > 0 and all(len(v["partidas"]) == d["n"] for v in d["variantes"].values())
    print(f"| {os.path.basename(f)} | {d['modo']} | {d['n']} | {d['semente0']}..{d['semente0'] + d['n'] - 1} | {vs} |")
for f in sorted(glob.glob(os.path.join(aqui, "dados", "*.json"))):
    d = json.load(open(f))
    print(f"| {os.path.basename(f)} | (JSON simples: Scryfall/Spellbook) | - | - | chaves: {', '.join(list(d)[:6]) if isinstance(d, dict) else str(len(d)) + ' itens'} |")
