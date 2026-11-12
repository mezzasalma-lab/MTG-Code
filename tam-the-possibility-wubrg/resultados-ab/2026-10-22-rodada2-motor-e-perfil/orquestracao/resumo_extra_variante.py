"""Complementos do resumo descritivo de UMA variante, SO' dos brutos (`dados/raw_ab_<N>[_resiliencia].json.xz`): fracao de partidas em que um teto por turno apertou; combo Orrery+Tezzeret+Chain Veil; distribuicao do turno da mesa limpa;
quartis de planeswalkers/mana por turno; turnos extras. Uso: python3 resumo_extra_variante.py <variante> <N>"""
import os, sys, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
VAR, N = sys.argv[1], int(sys.argv[2])
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
q = lambda x, f: sorted(x)[int(f * (len(x) - 1))]
for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
    r = [x[1] for x in A.carregar_raw(os.path.join(ARQ, "dados", f"raw_ab_{N}{suf}"))[VAR]]
    n = len(r)
    print(f"\n== variante {VAR}, modo {modo}, N={n} ==")
    print(f"partidas em que o teto de ativacoes de lealdade por turno apertou: {sum(1 for x in r if x.get('m_turn_cap_activations', 0) > 0)} ({100 * sum(1 for x in r if x.get('m_turn_cap_activations', 0) > 0) / n:.2f}%); teto de magias: {sum(1 for x in r if x.get('m_turn_cap_spells', 0) > 0)} ({100 * sum(1 for x in r if x.get('m_turn_cap_spells', 0) > 0) / n:.2f}%)")
    print(f"combo Orrery+Tezzeret+Chain Veil montado: {sum(1 for x in r if x.get('m_combo_assembled', 0) > 0)} ({100 * sum(1 for x in r if x.get('m_combo_assembled', 0) > 0) / n:.2f}%); fechou a partida: {sum(1 for x in r if x.get('m_combo_wins', 0) > 0)} ({100 * sum(1 for x in r if x.get('m_combo_wins', 0) > 0) / n:.2f}%); pagamento conjurado da mao: {sum(1 for x in r if x.get('m_combo_payoff_cast_from_hand', 0) > 0)}")
    print(f"turnos extras (Gauntlet -12): tomados {sum(x.get('m_extra_turns_taken', 0) for x in r) / n:.3f} por partida; jogados {sum(x.get('m_extra_turns_played', 0) for x in r) / n:.3f}; partidas com >= 2 -12 no mesmo turno nao identificaveis no bruto")
    turnos = [x["game_turns"] for x in r if x.get("cleared_T12", 0) == 1]
    print(f"mesa limpa ate' T12: {len(turnos)} partidas; turno da mesa limpa (mediana / Q1-Q3): {st.median(turnos) if turnos else '-'} / {q(turnos, .25) if turnos else '-'}-{q(turnos, .75) if turnos else '-'}")
    for campo in ("pws_T4", "pws_T6", "pws_T8", "pws_T10", "mana_T4", "mana_T6", "mana_T8", "loyalty_T8", "m_pw_entered", "m_ultimates_used"):
        v = [x.get(campo, 0) for x in r]
        print(f"   {campo:18s} mediana {st.median(v):6.1f}  Q1-Q3 {q(v, .25)}-{q(v, .75)}  max {max(v)}")
