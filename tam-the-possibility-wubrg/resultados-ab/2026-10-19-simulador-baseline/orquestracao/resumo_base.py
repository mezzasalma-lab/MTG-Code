"""Resumo DESCRITIVO da linha de base do Tam (uma variante so', sem A/B): refeito SO' dos brutos arquivados (`dados/raw_<TAG>_<N>[_resiliencia].json.xz`).
Uso: python3 resumo_base.py <TAG> <N> [padrao|resiliencia]   (saida em stdout; o driver grava em resumos/)
Para cada campo numerico: media, IC95% (1,96*dp/raiz(N)) e, nos indicadores 0/1, a proporcao em %."""
import os, sys, math, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A

TAG, N = sys.argv[1], int(sys.argv[2])
MODOS = [sys.argv[3]] if len(sys.argv) > 3 else ["padrao", "resiliencia"]
ARQ = os.path.abspath(os.path.join(AQUI, ".."))

GRUPOS = [
    ("Mesa limpa (todos os oponentes fora) ate' o turno", ["cleared_T6", "cleared_T7", "cleared_T8", "cleared_T9", "cleared_T10", "cleared_T12"]),
    ("1o oponente fora ate' o turno", ["first_elim_T6", "first_elim_T8"]),
    ("Eu morri (vida <= 0; a partida continua) ate' o turno / deck-out", ["died_T6", "died_T8", "died_T10", "died_T12", "died_any", "self_lost"]),
    ("Tam em campo / combo", ["commander_cast_turn_v", "m_tam_activations", "m_tam_x_total", "m_combo_assembled", "m_combo_wins"]),
    ("Planeswalkers (T3/T4/T5/T6/T8/T10)", [f"pws_T{t}" for t in (3, 4, 5, 6, 8, 10)] + ["m_pw_entered", "m_pw_died", "m_ultimates_used"]),
    ("Lealdade total / tipos de PW (T6/T8)", ["loyalty_T6", "loyalty_T8", "pw_types_T6", "pw_types_T8"]),
    ("Mana disponivel (T3/T4/T5/T6/T8)", [f"mana_T{t}" for t in (3, 4, 5, 6, 8)] + [f"lands_T{t}" for t in (4, 6, 8)]),
    ("Fontes de dano ao oponente (total por partida)", ["m_opp_damage_total", "m_combat_damage_total", "m_awbo_triggers"]),
    ("Interacao do oponente (resiliencia)", ["m_smart_removals", "m_smart_wipes", "m_smart_counters", "m_smart_discards", "m_pw_combat_deaths", "m_opp_attackers_total", "m_face_combat_damage_total", "life_min"]),
    ("Proliferate por fonte", ["m_proliferates_total", "m_prolif_by_tam", "m_prolif_by_flux_channeler", "m_prolif_by_vraska", "m_prolif_by_gauntlet_zero", "m_prolif_by_peacemaker", "m_prolif_by_dreamtide_whale", "m_prolif_by_staff", "m_prolif_by_ripples"]),
]


def linha(nome, xs):
    n = len(xs)
    m = st.mean(xs)
    h = 1.96 * st.stdev(xs) / math.sqrt(n) if n > 1 and len(set(xs)) > 1 else 0.0
    ind = set(xs) <= {0, 1, 0.0, 1.0}
    return f"   {nome:34s} {m:10.4f} ±{h:8.4f}" + (f"   ({100 * m:5.1f}%)" if ind else "")


for modo in MODOS:
    suf = "" if modo == "padrao" else "_resiliencia"
    res = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_{TAG}_{N}{suf}"))["base"]
    print(f"\n=== LINHA DE BASE DO TAM, modo {modo}, N={len(res)} ({TAG}) ===")
    for tit, cs in GRUPOS:
        print(tit)
        for c in cs:
            xs = [x[1].get(c, 0.0) for x in res]
            if any(xs):
                print(linha(c, xs))
            else:
                print(f"   {c:34s}  (sempre 0 nesta bateria)")
