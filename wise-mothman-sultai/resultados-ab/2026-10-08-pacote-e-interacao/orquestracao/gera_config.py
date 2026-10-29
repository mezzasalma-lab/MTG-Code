"""Config do A/B do PACOTE (Agent Frank Horrigan + Branching Evolution) e de QUAL interacao cortar (2026-10-08, pergunta do usuario: "o que vc me sugere? Abrir mao de interacao por Remocao?").
Simulador CONGELADO `codigo/mothman_goldfish_v1_estado_2026-10-08.py` (== o vivo de 2026-10-07, 194 testes). N=10.000 pareado, `no lugar` (SWAP_IN_PLACE), sementes 3.000.000+i, 12 turnos, dois modos.
Cada variante e' um par de trocas (Horrigan <- Offer sempre; Branching <- X) para ver o que muda quando o 2o corte e' contramagica, varredor (Wave Goodbye, Toxic Deluge) ou remocao pontual (Tear Asunder).
Uso: python3 gera_config.py"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
SIM = "resultados-ab/2026-10-08-pacote-e-interacao/codigo/mothman_goldfish_v1_estado_2026-10-08.py"
H, B = "Agent Frank Horrigan", "Branching Evolution"
OFFER, NEG, DSP, ARC, WAVE, DEL, TEAR = "An Offer You Can't Refuse", "Negate", "Didn't Say Please", "Arcane Denial", "Wave Goodbye", "Toxic Deluge", "Tear Asunder"
DESTAQUE = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "decked", "opps_eliminated_total", "proliferates_total", "rad_counters_given_opp_total",
            "mothman_counters_placed_total", "counters_placed_total", "cards_milled_opp_total", "cards_milled_self_total", "library_min", "draws_total",
            "counterspells_cast", "opp_spells_countered_total", "protection_used_total", "commander_countered_total", "smart_removals_total", "smart_wipes_total",
            "smart_artifact_wipes_total", "smart_enchantment_wipes_total", "wipes_cast"]
COMPACTO = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "counterspells_cast", "protection_used_total", "smart_removals_total", "smart_wipes_total",
            "proliferates_total", "mothman_counters_placed_total", "cards_milled_opp_total"]
def swap(*pares, **fl):
    d = {"SWAPS": [list(p) for p in pares], "SWAP_IN_PLACE": True}; d.update(fl); return d
V = {"base": {},
     "h__offer": swap((OFFER, H)),
     "b__negate": swap((NEG, B)),
     "p1_offer_negate": swap((OFFER, H), (NEG, B)),
     "p2_offer_dsp": swap((OFFER, H), (DSP, B)),
     "p3_offer_wave": swap((OFFER, H), (WAVE, B)),
     "p4_offer_deluge": swap((OFFER, H), (DEL, B)),
     "p5_offer_tear": swap((OFFER, H), (TEAR, B)),
     "p6_offer_arcane": swap((OFFER, H), (ARC, B))}
cfg = {"sim": SIM, "turns": 12, "destaque": DESTAQUE, "compacto": COMPACTO, "variantes": V, "variantes_10000": list(V), "regressao": ["p1_offer_negate", "p3_offer_wave"]}
json.dump(cfg, open(os.path.join(AQUI, "config_pacote.json"), "w"), indent=1)
print(len(V), "variantes")
