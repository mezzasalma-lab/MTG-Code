"""A/B pareado das candidatas de Reality Fracture no Prismatic Bridge (2026-09-25).
Resultado em goldfish-log.md. Resumo: python3 ab_reality_fracture_sum.py <prefixo> [prefixo_com_base]
Uso: python3 ab_reality_fracture.py <idx_part> <nparts> <N> <out_prefix> [variantes...]
Variante = "base" ou "ENTRA|SAI" ou "ENTRA|SAI+ENTRA2|SAI2+..." (troca posicional)."""
import sys, json
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prismatic_bridge_goldfish_v1 as pb

def parse(v):
    if v == "base":
        return None
    return [(p.split("|")[1], p.split("|")[0]) for p in v.split("+")]

def std_metrics(r):
    return {"ults": r["pw_ultimates_used_total"], "acts": r["pw_activations_total"], "pw_end": r["planeswalkers_in_play_end"],
            "opp_elim": r["opp_eliminated_total"], "gauntlet": r["gauntlet_extra_turns_total"], "pw_hits": r["bridge_hits_planeswalker"],
            "draws": r["pw_draws_total"], "first_pw": r["first_pw_hit_turn"] or 11, "bridge_1st": r["bridge_first_cast_turn"] or 11,
            "tam_acts": r["tam_activations_total"], "tam_saved": r["tam_mana_saved_total"], "lt_bridge": r["loyal_tutor_bridge_total"],
            "lt_draw": r["loyal_tutor_draw_total"], "entrust": r["entrust_casts_total"], "interaction": r["interaction_spells_cast_total"],
            "first_ult": r["first_ult_turn"] or 11, "turns_ult": r["turns_with_ult"], "tam_dyn": r["tam_dynamo_copies_total"],
            "late_acts": r["late_pw_activations_total"]}

def res_metrics(s):
    return {"died": 1 if s.died_turn is not None else 0, "ults": s.pw_ultimates_used_total, "acts": s.pw_activations_total,
            "pw_turns_alive": s.pw_turns_alive_total, "pw_end": len(s.loyalty), "life": min(s.life, 200),
            "opp_elim": s.opp_eliminated_total, "pw_combat_deaths": s.pw_combat_deaths_total,
            "removals_suffered": s.smart_removals_total, "stopped": s.opp_spells_stopped_total,
            "bridge_countered": s.smart_counters_total, "tam_acts": s.tam_activations_total,
            "lt_bridge": s.loyal_tutor_bridge_total, "entrust": s.entrust_casts_total,
            "first_ult": s.first_ult_turn or 11, "turns_ult": s.turns_with_ult, "died_turn": s.died_turn or 11}

part, nparts, N, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
variants = sys.argv[5:]
res = {}
for k, v in enumerate(variants):
    if k % nparts != part:
        continue
    sw = parse(v)
    res[v] = {"std": [std_metrics(pb.simulate_one(3_000_000 + i, 10, False, swap=sw)) for i in range(N)],
              "res": [res_metrics(pb.simulate_one_with_interaction(6_000_000 + i, turns=10, attack_profile="mixed", swap=sw))
                      for i in range(N)]}
    print("ok", v, flush=True)
json.dump(res, open(f"{out}_{part}.json", "w"))
