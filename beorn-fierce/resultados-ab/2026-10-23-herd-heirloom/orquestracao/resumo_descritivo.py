"""Resumo DESCRITIVO de UMA variante do A/B (media ± IC95% de cada campo numerico e proporcao em % dos indicadores 0/1), SO' dos brutos arquivados.
Uso: python3 resumo_descritivo.py <variante> <N>   (variante = antes | depois | so_gatilho_beorn | troca_* ...)"""
import os, sys, math, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
VAR, N = sys.argv[1], int(sys.argv[2])
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
GRUPOS = [
    ("Comandante conjurada (Beorn)", ["commander_cast_turn__ate_T3", "commander_cast_turn__ate_T4", "commander_cast_turn__ate_T5", "commander_cast_turn__ate_T6", "commander_cast_turn__nunca"]),
    ("Primeiro finisher relevante", ["finisher_turn__ate_T4", "finisher_turn__ate_T5", "finisher_turn__ate_T6", "finisher_turn__nunca", "finishers_resolved"]),
    ("Mesa (media no fim do turno 8)", ["bear_count_final", "counters_on_board_final", "battlefield_count", "hand_size", "lands_played_total", "ramp_pieces_in_play"]),
    ("Compra e gatilhos", ["extra_draws", "spells_cast", "beorn_bear_draws", "beorn_combat_triggers", "combat_damage_draws", "roaming_throne_doublings", "war_room_draws", "cards_discarded_to_hand_size"]),
    ("Interacao propria (proxy)", ["removal_cast", "own_interaction_used"]),
    ("Herd Heirloom", ["heirloom_cast_turn__ate_T3", "heirloom_cast_turn__ate_T4", "heirloom_cast_turn__ate_T5", "heirloom_cast_turn__ate_T6", "heirloom_cast_turn__nunca", "heirloom_mana_uses", "heirloom_draw_activations",
                       "heirloom_draws", "heirloom_mana_turns_reserved_for_draw"]),
    ("Modo de resiliencia (oponente)", ["smart_removals_total", "smart_wipes_total", "smart_artifact_wipes_total", "smart_enchantment_wipes_total", "smart_counters_total", "smart_discards_total", "smart_attacks_taken_total", "life"]),
]
for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
    r = [x[1] for x in A.carregar_raw(os.path.join(ARQ, "dados", f"raw_ab_{N}{suf}"))[VAR]]
    n = len(r)
    print(f"=== BEORN, variante {VAR}, modo {modo}, N={n} ===")
    for titulo, campos in GRUPOS:
        print(titulo)
        for c in campos:
            v = [x.get(c) for x in r]
            if all(y is None for y in v) or all(c not in x for x in r):
                continue
            v = [float(y or 0.0) for y in v]
            m = st.mean(v); h = 1.96 * st.stdev(v) / math.sqrt(n) if len(set(v)) > 1 else 0.0
            ind = set(v) <= {0.0, 1.0}
            print(f"   {c:42s} {m:9.4f} ± {h:7.4f}" + (f"   ({100 * m:5.1f}%)" if ind else ""))
    print()
