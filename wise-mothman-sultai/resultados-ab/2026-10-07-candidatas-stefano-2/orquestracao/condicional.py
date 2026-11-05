#!/usr/bin/env python3
"""Efeito CONDICIONAL das 6 candidatas (le SO' do bruto dados/raw_final_10000[_resiliencia].json.xz): na subpartida em que a carta ENTROU em campo ATE T6 (campo `*_enter_turn__ate_T6`) ou, para a
Fractured Sanity (feitico, sem turno de entrada), em que foi CONJURADA OU CICLADA ao menos uma vez (selecao por um evento da partida: o IC mostra o ruido). Uso: python3 condicional.py > ../resumos/condicional.txt"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
N = 10000
CAMPO = {"scorch": "scorch_enter_turn__ate_T6", "tide": "tide_enter_turn__ate_T6", "branching": "branching_enter_turn__ate_T6", "loading": "loading_enter_turn__ate_T6", "crystal": "crystal_enter_turn__ate_T6"}
print("Condicional: diferenca pareada (variante - base) em pontos percentuais, so' nas partidas em que a carta ENTROU ate T6 (Fractured: conjurada ou ciclada alguma vez); n = partidas selecionadas; `*` = excede o IC95%.\n")
for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
    res = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_final_{N}{suf}")); base = res["base"]
    print(f"## {modo}")
    print("%-40s %-6s | %-18s %-18s %-18s" % ("variante", "n", "T8", "T10", "deck-out"))
    for nome, rs in res.items():
        k = nome.split("__")[0].replace("sens_", "")
        if nome == "base" or nome.startswith("seis_") or nome == "sens_base_persist_antigo": continue
        if k.startswith("scorch"): k = "scorch"
        if k == "fractured": idx = [i for i, x in enumerate(rs) if x[1].get("fractured_casts", 0) + x[1].get("fractured_cycles", 0) > 0]
        else: idx = [i for i, x in enumerate(rs) if x[1].get(CAMPO[k], 0.0) == 1.0]
        if len(idx) < 30: print("%-40s %-6d | amostra pequena" % (nome, len(idx))); continue
        out = []
        for c in ("cleared_T8", "cleared_T10", "self_lost"):
            m, h = A.ic([base[i][1].get(c, 0.0) for i in idx], [rs[i][1].get(c, 0.0) for i in idx]); out.append("%+.1f ± %.1f%s" % (100 * m, 100 * h, " *" if abs(m) > h else ""))
        print("%-40s %-6d | %-18s %-18s %-18s" % (nome, len(idx), *out))
    print()
