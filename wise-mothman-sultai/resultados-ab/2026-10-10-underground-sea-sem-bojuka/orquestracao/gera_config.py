"""Config do A/B 'quem sai pelo Underground Sea' (2026-10-10; o usuario: "Nao queria tirar a Bojuka nao, tem outra opcao?"). Simulador CONGELADO `codigo/mothman_goldfish_v1_ANTES.py` (= o vivo depois da troca Swarmyard -> Tropical
Island, commit af2bbb7). Base = a lista atual. Cada variante troca UM terreno pelo Underground Sea, `no lugar` (a permutacao do baralho nao muda), N=10.000 pareado, dois modos. u0 e' a proposta anterior (Bojuka Bog), so' como referencia
no MESMO lote. Uso: python3 gera_config.py"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
SIM = "resultados-ab/2026-10-10-underground-sea-sem-bojuka/codigo/mothman_goldfish_v1_ANTES.py"
DESTAQUE = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "decked", "commander_cast_turn__ate_T3", "commander_cast_turn__ate_T4", "commander_cast_turn__ate_T5", "commander_cast_turn__ate_T6",
            "commander_cast_turn__nunca", "regenerations_used", "protection_used_total", "smart_removals_total", "smart_wipes_total", "commander_countered_total", "commander_cast_count",
            "interaction_plays", "lands_entered_total", "mana_spent_total", "life_min", "mothman_counters_placed_total", "cards_milled_opp_total", "rad_counters_given_opp_total", "fetches_cracked_total"]
COMPACTO = ["cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "commander_cast_turn__ate_T4", "commander_cast_turn__ate_T5", "life_min", "fetches_cracked_total", "protection_used_total"]
SEA = "Underground Sea"
CAND = [("u0_bojuka_bog", "Bojuka Bog"), ("u1_watery_grave", "Watery Grave"), ("u2_morphic_pool", "Morphic Pool"), ("u3_swamp", "Swamp"), ("u4_island", "Island"), ("u5_minamo", "Minamo, School at Water's Edge"),
        ("u6_shifting_woodland", "Shifting Woodland"), ("u7_zagoth_triome", "Zagoth Triome"), ("u8_strip_mine", "Strip Mine"), ("u9_takenuma", "Takenuma, Abandoned Mire"), ("u10_boseiju", "Boseiju, Who Endures")]
V = {"base": {}}
for nome, sai in CAND: V[nome] = {"SWAPS": [[sai, SEA]], "SWAP_IN_PLACE": True}
json.dump({"sim": SIM, "turns": 12, "destaque": DESTAQUE, "compacto": COMPACTO, "variantes": V, "variantes_10000": list(V), "regressao": []}, open(os.path.join(AQUI, "config_u.json"), "w"), indent=1)
print(len(V), "variantes")
