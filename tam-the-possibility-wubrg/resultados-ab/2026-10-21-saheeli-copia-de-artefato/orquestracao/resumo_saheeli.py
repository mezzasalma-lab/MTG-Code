#!/usr/bin/env python3
"""Efeito da copia de artefato de mana da Saheeli (`depois` = simulador vivo com SAHEELI_COPY_MANA_ARTIFACT=True) contra `antes` (snapshot e01054f: so' copia de P/T), N = 10.000, sementes 3.000.000+i, 12 turnos, por modo.
Lido SO' dos brutos arquivados (dados/raw_ab_10000[_resiliencia].json.xz). Uso: python3 resumo_saheeli.py > ../resumos/resumo_saheeli.md"""
import os, sys, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
R = {md: A.carregar_raw(os.path.join(ARQ, "dados", f"raw_ab_10000{suf}")) for md, suf in (("padrao", ""), ("resiliencia", "_resiliencia"))}
def col(rs, c): return [y[1].get(c, 0.0) for y in rs]
print("## Saheeli -2 como copia de artefato de mana (N = 10.000 pareado, sementes 3.000.000+i, 12 turnos; depois / antes / diferenca pareada ± IC95%; `*` = excede o IC)\n")
print("| métrica | modo padrão | modo resiliência |\n|---|---|---|")
LIN = [("partidas com resultado IDÊNTICO ao anterior (%)", None, 100), ("partidas com >= 1 cópia de mana da Saheeli (%)", "m_saheeli_mana_copies>0", 100), ("cópias de mana por partida", "m_saheeli_mana_copies", 1), ("mana extra por partida", "m_saheeli_mana_copy_extra", 1),
       ("ativações da Saheeli por partida", "m_pw_act_by_Saheeli, Sublime Artificer", 1), ("mana disponível no início do T6", "mana_T6", 1), ("mana disponível no início do T8", "mana_T8", 1), ("planeswalkers em campo no fim do T6", "pws_T6", 1),
       ("planeswalkers em campo no fim do T8", "pws_T8", 1), ("mesa limpa até T8 (%)", "cleared_T8", 100), ("mesa limpa até T10 (%)", "cleared_T10", 100), ("1º oponente fora até T6 (%)", "first_elim_T6", 100)]
for rot, c, esc in LIN:
    cel = []
    for md in ("padrao", "resiliencia"):
        B, N = R[md]["antes"], R[md]["depois"]
        assert len(B) == len(N) == 10000
        if c is None:
            n = sum(1 for x, y in zip(B, N) if x[0] == y[0]); cel.append(f"{100 * n / len(B):.2f}% ({n} de {len(B)})"); continue
        if c.endswith(">0"):
            k = c[:-2]; cel.append(f"{esc * st.mean(1.0 if v > 0 else 0.0 for v in col(N, k)):.2f} / 0 (campo não existe no anterior)"); continue
        if c in ("m_saheeli_mana_copies", "m_saheeli_mana_copy_extra"):
            cel.append(f"{st.mean(col(N, c)):.4f} / 0 (campo não existe no anterior)"); continue
        d, h = A.ic(col(B, c), col(N, c))
        cel.append("%.4f / %.4f / %+.4f ± %.4f%s" % (esc * st.mean(col(N, c)), esc * st.mean(col(B, c)), esc * d, esc * h, " \\*" if abs(d) > h else ""))
    print(f"| {rot} | {cel[0]} | {cel[1]} |")
