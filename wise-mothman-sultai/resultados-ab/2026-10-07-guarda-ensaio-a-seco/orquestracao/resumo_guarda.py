"""Tabela do A/B da guarda do payoff-primeiro do Mothman (so' le os brutos arquivados): `aritmetica` (guarda aritmetica do comandante, a de 2026-10-06) e `ensaio` (ensaio a seco do resto da fase) contra `base`
(ordem antiga), e a diferenca pareada `ensaio - aritmetica`. N=10.000 (3 variantes) e, para o pacote de 5 trocas + Master, N=2.000.  Uso: python3 resumo_guarda.py   (de dentro de orquestracao/)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abgen as A
ARQ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CAMPOS = ["payoff_first_casts", "ruin_crab_mills", "icetill_replays", "mothman_counters_placed_total", "cards_milled_opp_total", "cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost"]
def cel(a, b, campo, res):
    m, h = A.ic([x[1].get(campo, 0.0) for x in res[a]], [x[1].get(campo, 0.0) for x in res[b]])
    return f"{m:+.3f} ± {h:.3f}{' *' if abs(m) > h else ''}"
for suf, modo in (("", "padrao"), ("_resiliencia", "resiliencia")):
    res = A.carregar_raw(os.path.join(ARQ, "dados", "raw_ab_10000" + suf))
    assert sum(x[1]["payoff_first_casts"] for x in res["ensaio"]) > 0
    print(f"### N=10.000, modo {modo} (12 turnos; diferenca pareada, `*` = excede o IC95%)\n")
    print("| campo | media da base | aritmetica - base | ensaio - base | ensaio - aritmetica |\n|---|---|---|---|---|")
    for c in CAMPOS:
        mb = sum(x[1].get(c, 0.0) for x in res["base"]) / len(res["base"])
        print(f"| `{c}` | {mb:.4f} | {cel('base', 'aritmetica', c, res)} | {cel('base', 'ensaio', c, res)} | {cel('aritmetica', 'ensaio', c, res)} |")
    print()
    r2 = A.carregar_raw(os.path.join(ARQ, "dados", "raw_ab_2000" + suf))
    print(f"### N=2.000, modo {modo}: efeito do pacote de 5 trocas + Master DENTRO de cada guarda (pacote+guarda - guarda)\n")
    print("| campo | pacote - aritmetica | pacote - ensaio |\n|---|---|---|")
    for c in ("cleared_T7", "cleared_T8", "cleared_T10", "self_lost"):
        print(f"| `{c}` | {cel('aritmetica', 'pacote5+master+aritmetica', c, r2)} | {cel('ensaio', 'pacote5+master+ensaio', c, r2)} |")
    print()
