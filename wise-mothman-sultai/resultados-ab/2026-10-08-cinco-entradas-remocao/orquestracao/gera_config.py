"""Config do A/B das CINCO ENTRADAS pedidas pelo usuario em 2026-10-08 (Agent Frank Horrigan, Branching Evolution, Atomize, Casualties of War, Assassin's Trophy) e de QUAIS 5 CORTES.
Simulador CONGELADO `codigo/mothman_goldfish_v1_DEPOIS.py`. N=10.000 pareado, `no lugar` (SWAP_IN_PLACE), sementes 3.000.000+i, 12 turnos, dois modos.
Offer e Negate saem em todos os conjuntos (medido na rodada anterior: o par Horrigan + Branching <- Offer + Negate = +4,02 / +1,85); as outras 3 vagas variam entre V.A.T.S., Tear Asunder, Wave Goodbye, Toxic Deluge,
Arcane Denial e Didn't Say Please. Controles: p1 (so' o par de motor; tem de reproduzir a rodada anterior) e rem3 (so' as 3 remocoes, sem o par). Uso: python3 gera_config.py"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
SIM = "resultados-ab/2026-10-08-cinco-entradas-remocao/codigo/mothman_goldfish_v1_DEPOIS.py"
F, B, A, C, T = "Agent Frank Horrigan", "Branching Evolution", "Atomize", "Casualties of War", "Assassin's Trophy"
OFFER, NEG, DSP, ARC, WAVE, DEL, TEAR, VATS = "An Offer You Can't Refuse", "Negate", "Didn't Say Please", "Arcane Denial", "Wave Goodbye", "Toxic Deluge", "Tear Asunder", "V.A.T.S."
DESTAQUE = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "decked", "opps_eliminated_total", "proliferates_total", "rad_counters_given_opp_total",
            "mothman_counters_placed_total", "counters_placed_total", "cards_milled_opp_total", "cards_milled_self_total", "library_min", "draws_total",
            "atomize_casts", "casualties_casts", "trophy_casts", "trophy_lands_given", "interaction_plays", "crimes_total", "deepmuck_triggers",
            "counterspells_cast", "opp_spells_countered_total", "protection_used_total", "commander_countered_total", "smart_removals_total", "smart_wipes_total", "wipes_cast"]
COMPACTO = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "atomize_casts", "casualties_casts", "trophy_casts", "interaction_plays", "counterspells_cast",
            "protection_used_total", "smart_removals_total", "proliferates_total", "mothman_counters_placed_total"]
def swap(*pares, **fl):
    d = {"SWAPS": [list(p) for p in pares], "SWAP_IN_PLACE": True}; d.update(fl); return d
def cinco(a, b, c):
    """Offer->Frank, Negate->Branching; as 3 vagas variaveis a, b, c recebem Atomize, Casualties, Trophy nessa ordem."""
    return swap((OFFER, F), (NEG, B), (a, A), (b, C), (c, T))
V = {"base": {},
     "p1_so_o_par": swap((OFFER, F), (NEG, B)),
     "rem3_vats_wave_deluge": swap((VATS, A), (WAVE, C), (DEL, T)),
     "s1_vats_wave_deluge": cinco(VATS, WAVE, DEL),
     "s2_vats_arcane_dsp": cinco(VATS, ARC, DSP),
     "s3_vats_wave_arcane": cinco(VATS, WAVE, ARC),
     "s4_vats_wave_dsp": cinco(VATS, WAVE, DSP),
     "s5_vats_deluge_arcane": cinco(VATS, DEL, ARC),
     "s6_vats_deluge_dsp": cinco(VATS, DEL, DSP),
     "s7_tear_wave_deluge": cinco(TEAR, WAVE, DEL)}
cfg = {"sim": SIM, "turns": 12, "destaque": DESTAQUE, "compacto": COMPACTO, "variantes": V, "variantes_10000": list(V), "regressao": ["s1_vats_wave_deluge", "s2_vats_arcane_dsp"]}
json.dump(cfg, open(os.path.join(AQUI, "config_cinco.json"), "w"), indent=1)
print(len(V), "variantes")
