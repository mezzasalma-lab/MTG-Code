"""A/B pareado das 4 candidatas pedidas em 2026-09-29 (Dihada, Commodore Guff, Vronos,
Sarkhan the Masterless) no Prismatic Bridge. Resultado em goldfish-log.md.
Resumo: python3 ab_candidatas_sum.py <prefixo> [prefixo_com_base]
Uso:    python3 ab_candidatas.py <idx_part> <nparts> <N> <out_prefix> [--profile P] [variantes...]
Variante = "base" ou "ENTRA|SAI" ou "ENTRA|SAI+ENTRA2|SAI2+..." (troca posicional: a carta nova
entra NA LINHA da cortada, entao a partida so' diverge quando essa posicao e' comprada/revelada)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prismatic_bridge_goldfish_v1 as pb


CONTROL_PW = "Control PW (inerte)"


def _register_control():
    """CONTROLE do lado da entrada: um planeswalker de lealdade 5 sem NENHUMA habilidade (so' o corpo:
    entra pela Bridge/mao, ganha marcadores, absorve ataque). Separa o que a candidata faz por ser
    "mais um PW" do que ela faz pelas habilidades. So' existe no harness (nao entra no simulador)."""
    pb.add(CONTROL_PW, 4, "Planeswalker", colors={"U"}, produces=set(), tags={"planeswalker"})
    pb.PLANESWALKER_STARTING_LOYALTY[CONTROL_PW] = 5
    pb.GENERIC_MANA[CONTROL_PW] = 3
    pb.PW_TYPES[CONTROL_PW] = "Control"
    pb.LEGENDARY_CARD_NAMES.add(CONTROL_PW)
    if CONTROL_PW not in pb.CANDIDATE_PWS:
        pb.CANDIDATE_PWS = tuple(pb.CANDIDATE_PWS) + (CONTROL_PW,)  # registra "entered_" nas estatisticas


_register_control()

CONTROL_BODY = "Control Body (2/2 lendaria sem texto)"


def _register_control_body():
    """CONTROLE do lado da entrada pra CRIATURA candidata (Sisay): {2}{W}, Legendary Creature 2/2 sem NENHUM texto
    (mesmo custo, cor, tipo e corpo base; lendaria pra Halfling/Plaza pagarem igual). Candidata - corpo = valor do TEXTO.
    Nao ataca (mesmo tratamento da Sisay)."""
    pb.add(CONTROL_BODY, 3, "Creature", colors={"W"}, produces=set(), tags={"creature"})
    pb.CREATURE_STATS[CONTROL_BODY] = (2, 2, set())
    pb.GENERIC_MANA[CONTROL_BODY] = 2
    pb.LEGENDARY_CARD_NAMES.add(CONTROL_BODY)
    pb.NON_ATTACKING_NAMES.add(CONTROL_BODY)
    if CONTROL_BODY not in pb.CANDIDATE_CREATURES:
        pb.CANDIDATE_CREATURES = tuple(pb.CANDIDATE_CREATURES) + (CONTROL_BODY,)


_register_control_body()


def parse(v):
    """Retorna (swap, flags_desligadas). "ENTRA|SAI@dihada_minus3,guff_minus3" INVERTE o padrao dessas
    chaves de `pb.CAND_POLICY` so' durante a variante (sensibilidade)."""
    flags = []
    if "@" in v:
        v, f = v.split("@")
        flags = f.split(",")
    if v == "base":
        return None, flags
    return [(p.split("|")[1], p.split("|")[0]) for p in v.split("+")], flags


def std_metrics(r):
    return {"acts": r["pw_activations_total"], "pw_end": r["planeswalkers_in_play_end"],
            "opp_elim": r["opp_eliminated_total"], "gauntlet": r["gauntlet_extra_turns_total"],
            "draws": r["pw_draws_total"], "first_pw": r["first_pw_hit_turn"] or 11,
            "bridge_1st": r["bridge_first_cast_turn"] or 11, "interaction": r["interaction_spells_cast_total"],
            "first_ult": r["first_ult_turn"] or 11, "turns_ult": r["turns_with_ult"],
            "cs": r["cand_stats"]}


def res_metrics(s):
    return {"died": 1 if s.died_turn is not None else 0, "died_turn": s.died_turn or 11,
            "acts": s.pw_activations_total, "pw_turns_alive": s.pw_turns_alive_total, "pw_end": len(s.loyalty),
            "life": max(-50, min(s.life, 200)), "opp_elim": s.opp_eliminated_total,
            "pw_combat_deaths": s.pw_combat_deaths_total, "pw_combat_damage": s.pw_combat_damage_total,
            "removals": s.smart_removals_total, "first_ult": s.first_ult_turn or 11, "turns_ult": s.turns_with_ult,
            "our_dmg": min(s.our_combat_damage_proxy_total, 100000), "draws": s.pw_draws_total,
            "opp_killed": s.opp_creatures_killed_total, "loy_end": sum(s.loyalty.values()),
            "cs": dict(s.cand_stats)}


if __name__ == "__main__":
    args = sys.argv[1:]
    profile = "mixed"
    res_only = "--res-only" in args
    if res_only:
        args.remove("--res-only")
    if "--profile" in args:
        k = args.index("--profile")
        profile = args[k + 1]
        del args[k:k + 2]
    part, nparts, N, out = int(args[0]), int(args[1]), int(args[2]), args[3]
    variants = args[4:]
    res = {}
    for k, v in enumerate(variants):
        if k % nparts != part:
            continue
        sw, off = parse(v)
        for flag in pb.CAND_POLICY:
            dflt = pb.CAND_POLICY_DEFAULTS[flag]
            pb.CAND_POLICY[flag] = (not dflt) if flag in off else dflt   # "@chave" inverte o padrao da chave
        d = {"res": [res_metrics(pb.simulate_one_with_interaction(6_000_000 + i, turns=10, attack_profile=profile, swap=sw))
                     for i in range(N)]}
        if profile == "mixed" and not res_only:
            d["std"] = [std_metrics(pb.simulate_one(3_000_000 + i, 10, False, swap=sw)) for i in range(N)]
        res[v] = d
        print("ok", v, flush=True)
    json.dump(res, open(f"{out}_{part}.json", "w"))
