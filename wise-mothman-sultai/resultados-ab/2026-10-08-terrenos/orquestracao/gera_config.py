"""Config do A/B da BASE DE MANA do Mothman (2026-10-08, pergunta do usuario: "como ajustaria os terrenos?"). Simulador CONGELADO `codigo/mothman_goldfish_v1_lista_atual.py` (== o vivo apos aplicar as cinco entradas).
N=10.000 pareado, `no lugar` (SWAP_IN_PLACE), sementes 3.000.000+i, 12 turnos, dois modos. Cada variante troca terrenos da lista atual por BASICOS (mede o valor marginal de trocar um terreno incolor / um Island por uma fonte
de B ou G; um dual real vale >= um basico da cor, com o custo do seu ETB). Uso: python3 gera_config.py"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
SIM = "resultados-ab/2026-10-08-terrenos/codigo/mothman_goldfish_v1_lista_atual.py"
DESTAQUE = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "decked", "commander_cast_turn__ate_T3", "commander_cast_turn__ate_T4", "commander_cast_turn__ate_T5", "commander_cast_turn__ate_T6",
            "commander_cast_turn__nunca", "casualties_casts", "atomize_casts", "trophy_casts", "regenerations_used", "protection_used_total", "smart_removals_total", "interaction_plays", "lands_entered_total",
            "mana_spent_total", "prox_mana_wasted_total", "mothman_counters_placed_total", "cards_milled_opp_total", "rad_counters_given_opp_total"]
COMPACTO = ["cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "commander_cast_turn__ate_T4", "commander_cast_turn__ate_T5", "casualties_casts", "atomize_casts", "regenerations_used", "mana_spent_total"]
def swap(*pares, **fl):
    d = {"SWAPS": [list(p) for p in pares], "SWAP_IN_PLACE": True}; d.update(fl); return d
SW, HO, PL, IS = "Swarmyard", "Yavimaya Hollow", "Plaza of Heroes", "Island"
V = {"base": {},
     "t1_swarmyard_swamp": swap((SW, "Swamp")),
     "t2_hollow_forest": swap((HO, "Forest")),
     "t3_ambos_swamp_forest": swap((SW, "Swamp"), (HO, "Forest")),
     "t4_ambos_swamp_swamp": swap((SW, "Swamp"), (HO, "Swamp")),
     "t5_island_swamp": swap((IS, "Swamp")),
     "t6_t3_mais_island_swamp": swap((SW, "Swamp"), (HO, "Forest"), (IS, "Swamp")),
     "t7_plaza_swamp": swap((PL, "Swamp"))}
cfg = {"sim": SIM, "turns": 12, "destaque": DESTAQUE, "compacto": COMPACTO, "variantes": V, "variantes_10000": list(V), "regressao": ["t3_ambos_swamp_forest"]}
json.dump(cfg, open(os.path.join(AQUI, "config_terrenos.json"), "w"), indent=1)
print(len(V), "variantes")
