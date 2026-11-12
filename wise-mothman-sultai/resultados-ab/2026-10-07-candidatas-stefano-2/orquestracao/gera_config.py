"""Configs do A/B das 6 candidatas do Stefano (Fractured Sanity, Screeching Scorchbeast, Inexorable Tide, Branching Evolution, Loading Zone, The Earth Crystal), com o simulador CONGELADO
`codigo/mothman_goldfish_v1_C2.py`. Triagem N=2.000: `carta <- X` para os 6 cortes que o Monument/Jace/Horrigan ja' disputam. Uso: python3 gera_config.py"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
SIM = "resultados-ab/2026-10-07-candidatas-stefano-2/codigo/mothman_goldfish_v1_C2.py"
CARTAS = {"fractured": "Fractured Sanity", "scorch": "Screeching Scorchbeast", "tide": "Inexorable Tide", "branching": "Branching Evolution", "loading": "Loading Zone", "crystal": "The Earth Crystal"}
CORTES = ["An Offer You Can't Refuse", "Negate", "Arcane Denial", "Toxic Deluge", "Cold-Eyed Selkie", "Didn't Say Please"]
DESTAQUE = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "decked", "opps_eliminated_total", "fractured_casts", "fractured_cycles", "scorch_attacks", "scorch_token_events",
            "scorch_tokens", "scorch_skipped", "scorch_rad_self", "tide_triggers", "crystal_activations", "crystal_counters", "warp_casts", "warp_exiled", "warp_recasts", "persist_zero_deaths",
            "proliferates_total", "rad_counters_given_opp_total", "mothman_counters_placed_total", "counters_placed_total", "cards_milled_opp_total", "cards_milled_self_total", "library_min", "draws_total", "tokens_created"]
COMPACTO = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "scorch_tokens", "tide_triggers", "fractured_casts", "crystal_activations", "warp_casts", "proliferates_total",
            "rad_counters_given_opp_total", "mothman_counters_placed_total", "cards_milled_opp_total"]
def slug(n): return "".join(ch for ch in n.lower().replace("'", "").replace(",", "").replace(" ", "_") if ch.isalnum() or ch == "_")
def swap(*pares, **fl):
    d = {"SWAPS": [list(p) for p in pares], "SWAP_IN_PLACE": True}; d.update(fl); return d
def cfg(variantes, v10000=None, regressao=()):
    return {"sim": SIM, "turns": 12, "destaque": DESTAQUE, "compacto": COMPACTO, "variantes": variantes, "variantes_10000": v10000 or list(variantes), "regressao": list(regressao)}
if __name__ == "__main__":
    v = {"base": {}}
    for k, n in CARTAS.items():
        for x in CORTES: v[f"{k}__{slug(x)}"] = swap((x, n))
    json.dump(cfg(v), open(os.path.join(AQUI, "config_triagem.json"), "w"), indent=1)
    print(len(v), "variantes na triagem")
