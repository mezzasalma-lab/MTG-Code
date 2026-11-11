"""Tabela do A/B da correcao PLAZA_ENABLES_COMMANDER do Mothman (so' le os brutos arquivados em ../dados): `plaza - base`, N=10.000 e N=2.000, modos padrao e resiliencia.
Uso: python3 resumo_plaza.py   (de qualquer pasta)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abgen as A
ARQ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CAMPOS = ["commander_land_overrides_total", "commander_cast_turn__ate_T3", "commander_cast_turn__ate_T4", "commander_cast_turn__ate_T5", "commander_cast_turn__ate_T6", "commander_cast_turn__nunca",
          "cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "cards_milled_opp_total", "mothman_counters_placed_total", "opps_eliminated_total"]
def cel(res, campo):
    m, h = A.ic([x[1].get(campo, 0.0) for x in res["base"]], [x[1].get(campo, 0.0) for x in res["plaza"]])
    return f"{m:+.4f} ± {h:.4f}{' *' if abs(m) > h else ''}"
for N in (10000, 2000):
    for suf, modo in (("", "padrao"), ("_resiliencia", "resiliencia")):
        p = os.path.join(ARQ, "dados", f"raw_ab_{N}{suf}")
        if not os.path.exists(p + ".json.xz"):
            continue
        res = A.carregar_raw(p)
        assert sum(x[1]["commander_land_overrides_total"] for x in res["plaza"]) > 0 and sum(x[1]["commander_land_overrides_total"] for x in res["base"]) == 0
        print(f"### N={format(N, ',').replace(',', '.')}, modo {modo} (12 turnos; diferenca pareada plaza - base, `*` = excede o IC95%)\n")
        print("| campo | media da base | plaza - base |\n|---|---|---|")
        for c in CAMPOS:
            mb = sum(x[1].get(c, 0.0) for x in res["base"]) / len(res["base"])
            print(f"| `{c}` | {mb:.4f} | {cel(res, c)} |")
        iguais = sum(1 for a, b in zip(res["base"], res["plaza"]) if a[0] == b[0])
        print(f"\nPartidas IDENTICAS entre base e plaza (impressao digital do estado final): {iguais} de {N} ({100 * iguais / N:.2f}%)\n")
