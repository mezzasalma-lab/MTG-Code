"""Gera as configs do A/B de Agent Frank Horrigan / The Master, Transcendent (lista do Stefano). Usa o simulador CONGELADO `codigo/mothman_goldfish_v1_HM.py` (cfg["sim"] relativo a wise-mothman-sultai/).
Triagem N=2.000: `Frank <- X` e `Master <- X` para os 20 finalistas de corte do Monument (resultados-ab/2026-10-07-riverchurn-monument/resumos/rank_final.txt) + Kozilek. Uso: python3 gera_config.py"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
SIM = "resultados-ab/2026-10-07-comparacao-stefano/codigo/mothman_goldfish_v1_HM.py"
F, M = "Agent Frank Horrigan", "The Master, Transcendent"
CORTES = ["An Offer You Can't Refuse", "Didn't Say Please", "Negate", "Muldrotha, the Gravetide", "Generous Patron", "Tear Asunder", "Agatha's Soul Cauldron", "Nuclear Fallout",
          "Toxic Deluge", "Arcane Denial", "Wave Goodbye", "Hedge Shredder", "Heroic Intervention", "Zellix, Sanity Flayer", "V.A.T.S.", "Bojuka Bog", "Yavimaya Hollow",
          "Evolution Witness", "Cold-Eyed Selkie", "Soul-Guide Lantern", "Kozilek, Butcher of Truth"]
DESTAQUE = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "decked", "opps_eliminated_total", "horrigan_etb_prolifs", "horrigan_attack_prolifs", "horrigan_attacks",
            "horrigan_attack_damage", "master_activations", "master_act_mine", "master_act_opp", "master_act_on_opp_turn", "master_etb_rad", "proliferates_total", "rad_counters_given_opp_total",
            "mothman_counters_placed_total", "counters_placed_total", "cards_milled_opp_total", "cards_milled_self_total", "library_min", "draws_total", "kozilek_shuffles_total"]
COMPACTO = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "horrigan_attacks", "master_activations", "master_act_opp", "proliferates_total",
            "rad_counters_given_opp_total", "mothman_counters_placed_total", "cards_milled_opp_total"]
def slug(n): return "".join(ch for ch in n.lower().replace("'", "").replace(",", "").replace(" ", "_") if ch.isalnum() or ch == "_")
def swap(*pares, **fl):
    d = {"SWAPS": [list(p) for p in pares], "SWAP_IN_PLACE": True}; d.update(fl); return d
def cfg(variantes, v10000=None, regressao=()):
    return {"sim": SIM, "turns": 12, "destaque": DESTAQUE, "compacto": COMPACTO, "variantes": variantes, "variantes_10000": v10000 or list(variantes), "regressao": list(regressao)}
if __name__ == "__main__":
    v = {"base": {}}
    for x in CORTES:
        v["frank__" + slug(x)] = swap((x, F))
        v["master__" + slug(x)] = swap((x, M))
    json.dump(cfg(v), open(os.path.join(AQUI, "config_triagem.json"), "w"), indent=1)
    print(len(v), "variantes na triagem")
