"""Configs do A/B da troca Swarmyard -> Tropical Island (2026-10-09, pedido do usuario: "Troca o Swarmyard pela Tropical"). Simulador CONGELADO `codigo/mothman_goldfish_v1_ANTES.py` (= o vivo ANTES da troca; lista = d1 de
`../2026-10-09-terrenos-proxy`). Base = a lista atual (com a Swarmyard). e1 = Swarmyard -> Tropical Island (a troca aplicada); e2 = e1 + Bojuka Bog -> Underground Sea (a proposta anterior, NAO aplicada: so' para dizer o que
ela rende por cima da troca). Lote W (`swtrop`): N=10.000 pareado, `no lugar`, dois modos, comandante NAO e' alvo de remocao pontual. Lote V (`swtrop50`): so' resiliencia, `COMMANDER_REMOVAL_SHARE=0.5` (metade das remocoes pontuais
mira o comandante), para valorizar a regeneracao que sai junto com a Swarmyard. Uso: python3 gera_config.py"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
SIM = "resultados-ab/2026-10-09-swarmyard-tropical/codigo/mothman_goldfish_v1_ANTES.py"
DESTAQUE = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "decked", "commander_cast_turn__ate_T3", "commander_cast_turn__ate_T4", "commander_cast_turn__ate_T5", "commander_cast_turn__ate_T6",
            "commander_cast_turn__nunca", "regenerations_used", "protection_used_total", "smart_removals_total", "smart_wipes_total", "commander_countered_total", "commander_cast_count",
            "interaction_plays", "lands_entered_total", "mana_spent_total", "life_min", "mothman_counters_placed_total", "cards_milled_opp_total", "rad_counters_given_opp_total", "fetches_cracked_total"]
COMPACTO = ["cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "commander_cast_turn__ate_T4", "commander_cast_turn__ate_T5", "regenerations_used", "smart_removals_total", "protection_used_total"]
def swap(*pares, **fl):
    d = {"SWAPS": [list(p) for p in pares], "SWAP_IN_PLACE": True}; d.update(fl); return d
SW, TROP, BOG, SEA = "Swarmyard", "Tropical Island", "Bojuka Bog", "Underground Sea"
V = {"base": {}, "e1_swarmyard_tropical": swap((SW, TROP)), "e2_e1_mais_bog_sea": swap((SW, TROP), (BOG, SEA))}
def cfg(v, reg=()): return {"sim": SIM, "turns": 12, "destaque": DESTAQUE, "compacto": COMPACTO, "variantes": v, "variantes_10000": list(v), "regressao": list(reg)}
json.dump(cfg(V, ["e1_swarmyard_tropical"]), open(os.path.join(AQUI, "config_w.json"), "w"), indent=1)
json.dump(cfg({k: dict(v, COMMANDER_REMOVAL_SHARE=0.5) for k, v in V.items()}), open(os.path.join(AQUI, "config_v.json"), "w"), indent=1)
print("ok")
