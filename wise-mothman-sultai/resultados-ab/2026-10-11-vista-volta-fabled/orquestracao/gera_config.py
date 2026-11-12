"""Config do A/B da volta da Fabled Passage (2026-10-11; o usuario: "Sim"). Simulador CONGELADO `codigo/mothman_goldfish_v1_ANTES.py` (= o vivo antes desta troca, commit 312356f). Base = a lista atual (com a Prismatic Vista);
w1 = Prismatic Vista -> Fabled Passage `no lugar` (a troca aplicada). N=10.000 pareado, dois modos. Uso: python3 gera_config.py"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
SIM = "resultados-ab/2026-10-11-vista-volta-fabled/codigo/mothman_goldfish_v1_ANTES.py"
DESTAQUE = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "decked", "commander_cast_turn__ate_T3", "commander_cast_turn__ate_T4", "commander_cast_turn__ate_T5", "commander_cast_turn__ate_T6",
            "commander_cast_turn__nunca", "regenerations_used", "protection_used_total", "smart_removals_total", "smart_wipes_total", "commander_countered_total", "commander_cast_count",
            "interaction_plays", "lands_entered_total", "mana_spent_total", "life_min", "mothman_counters_placed_total", "cards_milled_opp_total", "rad_counters_given_opp_total", "fetches_cracked_total"]
COMPACTO = ["cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "commander_cast_turn__ate_T3", "commander_cast_turn__ate_T4", "commander_cast_turn__ate_T5", "life_min", "fetches_cracked_total"]
V = {"base": {}, "w1_vista_fabled": {"SWAPS": [["Prismatic Vista", "Fabled Passage"]], "SWAP_IN_PLACE": True}}
json.dump({"sim": SIM, "turns": 12, "destaque": DESTAQUE, "compacto": COMPACTO, "variantes": V, "variantes_10000": list(V), "regressao": []}, open(os.path.join(AQUI, "config_w.json"), "w"), indent=1)
print("ok")
