#!/usr/bin/env python3
"""Efeito CONDICIONAL de Horrigan e Master (le SO' do bruto dados/raw_final_10000[_resiliencia].json.xz): na subpartida em que a carta entrou em campo ATE T6 (campo `*_enter_turn__ate_T6`, que o
medidor grava no estado final), diferenca pareada (variante - base) de mesa limpa T8/T10 e deck-out. Cuidado: condicionar na entrada seleciona partidas diferentes (o IC mostra o ruido).
Uso: python3 condicional.py > ../resumos/condicional.txt"""
import os, sys, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
N = 10000
print("Condicional: diferenca pareada (variante - base) em pontos percentuais, so' nas partidas em que a carta ENTROU ate T6 (n = partidas selecionadas); `*` = excede o IC95%.\n")
for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
    res = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_final_{N}{suf}")); base = res["base"]
    print(f"## {modo}")
    print("%-46s %-6s | %-18s %-18s %-18s" % ("variante", "n", "T8", "T10", "deck-out"))
    for nome, rs in res.items():
        if nome == "base": continue
        campo = "horrigan_enter_turn__ate_T6" if (nome.startswith("frank") or nome.startswith("sens_frank")) else ("master_enter_turn__ate_T6" if (nome.startswith("master") or nome.startswith("sens_master")) else None)
        if campo is None: continue
        idx = [i for i, x in enumerate(rs) if x[1].get(campo, 0.0) == 1.0]
        if len(idx) < 30: print("%-46s %-6d | amostra pequena" % (nome, len(idx))); continue
        out = []
        for c in ("cleared_T8", "cleared_T10", "self_lost"):
            m, h = A.ic([base[i][1].get(c, 0.0) for i in idx], [rs[i][1].get(c, 0.0) for i in idx]); out.append("%+.1f ± %.1f%s" % (100 * m, 100 * h, " *" if abs(m) > h else ""))
        print("%-46s %-6d | %-18s %-18s %-18s" % (nome, len(idx), *out))
    print()
