"""O que a Arena Rector entrega de verdade no simulador (e o que acontece com a Sisay no mesmo slot).
Uso: python3 arena_uso.py <idx_part> <nparts> <N> <saida.json>
Instrumenta (so' neste harness) creature_enters e _our_creature_leaves; conta por partida:
entrada da Arena Rector/Sisay, morte por FONTE (combate, wipe proprio, Liliana -4, Wanderer -4, remocao de oponente),
disparo do gatilho da Arena Rector e qual PW ela buscou. Duas listas: base (Arena Rector) e Sisay no lugar dela."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prismatic_bridge_goldfish_v1 as pb

AR, SIS = "Arena Rector", pb.SISAY
REC = None
_orig_enters, _orig_leaves = pb.creature_enters, pb._our_creature_leaves


def enters(state, name, log, is_copy=False):
    if REC is not None and name in (AR, SIS) and not is_copy:
        REC.setdefault("entered_turns", {}).setdefault(name, []).append(state.turn)
    return _orig_enters(state, name, log, is_copy=is_copy)


def leaves(state, name, log, exiled=False, source="", inst=None):
    before = state.arena_rector_triggers_total
    n_log = len(log)
    r = _orig_leaves(state, name, log, exiled=exiled, source=source, inst=inst)
    if REC is not None and name in (AR, SIS):
        REC.setdefault("left", []).append((name, source or "?", bool(exiled), state.turn))
        if state.arena_rector_triggers_total > before:
            found = [e for e in log[n_log:] if e.get("trigger") == "arena_rector_dies"]
            REC.setdefault("triggers", []).append((source or "?", found[-1]["found"] if found else "?", state.turn))
    return r


pb.creature_enters, pb._our_creature_leaves = enters, leaves

if __name__ == "__main__":
    part, nparts, N, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    LISTAS = {"base": None, "sisay": [("Arena Rector", SIS)]}
    res = {}
    for nome, sw in LISTAS.items():
        res[nome] = {"std": [], "res": []}
        for i in range(part, N, nparts):
            REC = {}
            pb.simulate_one(3_000_000 + i, 10, False, swap=sw)
            res[nome]["std"].append(REC)
            REC = {}
            pb.simulate_one_with_interaction(6_000_000 + i, turns=10, attack_profile="mixed", swap=sw)
            res[nome]["res"].append(REC)
    json.dump(res, open(out, "w"))
    print("ok", part, flush=True)
