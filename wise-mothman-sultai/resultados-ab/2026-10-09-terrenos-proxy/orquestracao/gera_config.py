"""Configs do A/B dos TERRENOS COM PROXY (2026-10-09). Simulador CONGELADO `codigo/mothman_goldfish_v1_DEPOIS.py` (Underground Sea, Bayou, Tropical Island, Prismatic Vista, COMMANDER_REMOVAL_SHARE).
A Swarmyard FICA (regenera o comandante, Inseto Mutante). Lote X (`terrenos3`): N=10.000 pareado, `no lugar`, dois modos, comandante NAO e' alvo de remocao pontual (chave 0.0). Lote Y (`cmd50`): so' resiliencia, com a chave em 0.5
(metade das remocoes pontuais do oponente mira o comandante quando ele esta em campo) para valorizar as regeneracoes. Uso: python3 gera_config.py"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
SIM = "resultados-ab/2026-10-09-terrenos-proxy/codigo/mothman_goldfish_v1_DEPOIS.py"
DESTAQUE = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "decked", "commander_cast_turn__ate_T3", "commander_cast_turn__ate_T4", "commander_cast_turn__ate_T5", "commander_cast_turn__ate_T6",
            "commander_cast_turn__nunca", "casualties_casts", "atomize_casts", "trophy_casts", "regenerations_used", "protection_used_total", "smart_removals_total", "smart_wipes_total", "commander_countered_total",
            "interaction_plays", "lands_entered_total", "mana_spent_total", "life_min", "mothman_counters_placed_total", "cards_milled_opp_total", "rad_counters_given_opp_total", "fetches_cracked_total"]
COMPACTO = ["cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "commander_cast_turn__ate_T4", "commander_cast_turn__ate_T5", "regenerations_used", "smart_removals_total", "protection_used_total"]
def swap(*pares, **fl):
    d = {"SWAPS": [list(p) for p in pares], "SWAP_IN_PLACE": True}; d.update(fl); return d
HO, SW, BOG, WOOD, GROVE, MINAMO, PASS = "Yavimaya Hollow", "Swarmyard", "Bojuka Bog", "Shifting Woodland", "Waterlogged Grove", "Minamo, School at Water's Edge", "Fabled Passage"
SEA, BAY, VIS = "Underground Sea", "Bayou", "Prismatic Vista"
V = {"base": {},
     "a1_hollow_sea": swap((HO, SEA)),
     "a2_hollow_bayou": swap((HO, BAY)),
     "a3_swarmyard_sea": swap((SW, SEA)),
     "s1_bog_swamp": swap((BOG, "Swamp")),
     "s2_woodland_forest": swap((WOOD, "Forest")),
     "s3_grove_island": swap((GROVE, "Island")),
     "s4_minamo_island": swap((MINAMO, "Island")),
     "v1_passage_vista": swap((PASS, VIS)),
     "c1_hollow_sea_bog_bayou": swap((HO, SEA), (BOG, BAY)),
     "c2_hollow_sea_woodland_bayou": swap((HO, SEA), (WOOD, BAY)),
     "c3_hollow_sea_grove_bayou": swap((HO, SEA), (GROVE, BAY)),
     "c4_hollow_sea_minamo_bayou": swap((HO, SEA), (MINAMO, BAY))}
def cfg(v, v10000, reg=()): return {"sim": SIM, "turns": 12, "destaque": DESTAQUE, "compacto": COMPACTO, "variantes": v, "variantes_10000": list(v10000), "regressao": list(reg)}
json.dump(cfg(V, V, ["c1_hollow_sea_bog_bayou", "v1_passage_vista"]), open(os.path.join(AQUI, "config_x.json"), "w"), indent=1)
Y = {k: dict(V[k], COMMANDER_REMOVAL_SHARE=0.5) for k in ("base", "a1_hollow_sea", "a2_hollow_bayou", "a3_swarmyard_sea", "c1_hollow_sea_bog_bayou", "c2_hollow_sea_woodland_bayou")}
json.dump(cfg(Y, Y, ["a3_swarmyard_sea"]), open(os.path.join(AQUI, "config_y.json"), "w"), indent=1)
# lote Z (`terrenos4`): as trocas que o usuario APROVOU (d1: Hollow -> Bayou e Fabled Passage -> Prismatic Vista, com a Swarmyard mantida) e as PROPOSTAS a mais (d2: + Bojuka Bog -> Underground Sea;
# d3: + Minamo -> Tropical Island; d4: + Shifting Woodland -> Tropical Island)
MIN, TRO = MINAMO, "Tropical Island"
Z = {"base": {},
     "d1_hollow_bayou_passage_vista": swap((HO, BAY), (PASS, VIS)),
     "d2_d1_mais_bog_sea": swap((HO, BAY), (PASS, VIS), (BOG, SEA)),
     "d3_d2_mais_minamo_tropical": swap((HO, BAY), (PASS, VIS), (BOG, SEA), (MIN, TRO)),
     "d4_d2_mais_woodland_tropical": swap((HO, BAY), (PASS, VIS), (BOG, SEA), (WOOD, TRO))}
json.dump(cfg(Z, Z, ["d3_d2_mais_minamo_tropical"]), open(os.path.join(AQUI, "config_z.json"), "w"), indent=1)
Z50 = {k: dict(Z[k], COMMANDER_REMOVAL_SHARE=0.5) for k in ("base", "d1_hollow_bayou_passage_vista", "d2_d1_mais_bog_sea")}
json.dump(cfg(Z50, Z50), open(os.path.join(AQUI, "config_z50.json"), "w"), indent=1)
print(len(V), "variantes no lote X;", len(Y), "no lote Y;", len(Z), "no lote Z;", len(Z50), "no lote Z50")
