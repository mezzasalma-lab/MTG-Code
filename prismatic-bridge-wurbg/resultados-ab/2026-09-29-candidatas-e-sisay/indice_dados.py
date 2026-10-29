"""Lista, para cada prefixo de dados brutos (dados/*.json.xz), as variantes, os modos e o N por modo. Uso: python3 indice_dados.py"""
import glob
import json
import lzma
import os
import re
from collections import defaultdict

aqui = os.path.dirname(os.path.abspath(__file__))
grupos = defaultdict(list)
for f in sorted(glob.glob(os.path.join(aqui, "dados", "*.json.xz"))):
    nome = os.path.basename(f)[:-8]
    m = re.match(r"(.+)_(\d+)$", nome)
    grupos[m.group(1) if m else nome].append(f)
print("| prefixo | partes | variantes (modo: N) |")
print("|---|---|---|")
for pref, fs in grupos.items():
    try:
        dados = [json.load(lzma.open(f)) for f in fs]
    except Exception as e:
        print(f"| {pref} | {len(fs)} | (não é resultado de A/B: {type(e).__name__}) |")
        continue
    if not isinstance(dados[0], dict):
        print(f"| {pref} | {len(fs)} | (formato próprio) |")
        continue
    if "oracle_text" in dados[0]:
        print(f"| {pref} | {len(fs)} | JSON da carta no Scryfall (oráculo lido ao vivo) |")
        continue
    if "std" in dados[0] and "errors" in dados[0]:   # regressão
        std = sum(d["std"] for d in dados)
        res = sum(d["res"] for d in dados)
        err = sum(len(d["errors"]) for d in dados)
        print(f"| {pref} | {len(fs)} | regressão: std {std}, res {res}, exceções {err} |")
        continue
    var = defaultdict(lambda: defaultdict(int))
    for d in dados:
        for v, modos in d.items():
            if not isinstance(modos, dict):
                continue
            for modo, jogos in modos.items():
                var[v][modo] += len(jogos) if isinstance(jogos, list) else 0
    if not var:
        rot = "resposta do Commander Spellbook (`find-my-combos`)" if pref.startswith("csb_") else "JSON da carta no Scryfall (oráculo lido ao vivo)"
        print(f"| {pref} | {len(fs)} | {rot} |")
        continue
    print(f"| {pref} | {len(fs)} | " + "<br>".join(f"`{v.replace('|', chr(92) + '|')}` — " + ", ".join(f"{m}: {n}" for m, n in sorted(modos.items())) for v, modos in var.items()) + " |")
