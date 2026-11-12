"""Complementos da linha de base, SO' dos brutos: fracao de partidas em que um teto por turno apertou; distribuicao do turno da mesa limpa; quartis de planeswalkers/mana por turno.
Uso: python3 resumo_extra.py baseline 10000"""
import os, sys, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
TAG, N = sys.argv[1], int(sys.argv[2])
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
q = lambda x, f: sorted(x)[int(f * (len(x) - 1))]
for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
    r = [x[1] for x in A.carregar_raw(os.path.join(ARQ, "dados", f"raw_{TAG}_{N}{suf}"))["base"]]
    n = len(r)
    print(f"\n== modo {modo}, N={n} ==")
    print(f"partidas em que o teto de ativacoes de lealdade por turno apertou: {sum(1 for x in r if x.get('m_turn_cap_activations', 0) > 0)} ({100 * sum(1 for x in r if x.get('m_turn_cap_activations', 0) > 0) / n:.2f}%); teto de magias: {sum(1 for x in r if x.get('m_turn_cap_spells', 0) > 0)}")
    print(f"combo Orrery+Tezzeret+Chain Veil montado: {sum(1 for x in r if x.get('m_combo_assembled', 0) > 0)} partidas; fechou a partida (com pagamento em campo): {sum(1 for x in r if x.get('m_combo_wins', 0) > 0)}")
    turnos = [x["game_turns"] for x in r if x.get("cleared_T12", 0) == 1]
    print(f"mesa limpa ate' T12: {len(turnos)} partidas; turno da mesa limpa (mediana / Q1-Q3): {st.median(turnos) if turnos else '-'} / {q(turnos, .25) if turnos else '-'}-{q(turnos, .75) if turnos else '-'}")
    for campo in ("pws_T4", "pws_T6", "pws_T8", "pws_T10", "mana_T4", "mana_T6", "mana_T8", "loyalty_T8", "m_pw_entered", "m_ultimates_used"):
        v = [x.get(campo, 0) for x in r]
        print(f"   {campo:18s} mediana {st.median(v):6.1f}  Q1-Q3 {q(v, .25)}-{q(v, .75)}  max {max(v)}")
    print(f"mulligans: {st.mean(x.get('mulligans_v', 0) for x in r):.3f} por partida; maos sem Tam ate' T6: {100 * sum(1 for x in r if x.get('tam_cast_by_T6', 0) == 0) / n:.1f}%")
