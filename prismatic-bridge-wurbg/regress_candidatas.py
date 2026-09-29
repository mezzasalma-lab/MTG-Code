"""Regressao das 4 candidatas de 2026-09-29: milhares de partidas completas, contando excecoes e travamentos.
Uso: python3 regress_candidatas.py <idx_part> <nparts> <N_por_modo> <saida.json>
Cada partida: swap rotativo (base, cada candidata sozinha, as 4 juntas em slots diferentes) e, na
resiliencia, perfil de mesa rotativo. Alarme de 20 s por partida (travamento = erro)."""
import json
import signal
import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prismatic_bridge_goldfish_v1 as pb

D, G, V, S = pb.CANDIDATE_PWS
SIS = pb.SISAY
SWAPS = [None,
         [("Arena Rector", D)], [("Arena Rector", G)], [("Arena Rector", V)], [("Arena Rector", S)],
         [("Arena Rector", D), ("Swan Song", G), ("Veil of Summer", V), ("Oath of Nissa", S)],
         [("Farseek", D), ("Doubling Season", G), ("Swan Song", V), ("Arena Rector", S)],
         [("Oath of Nissa", D), ("Arena Rector", G), ("Farseek", V), ("Veil of Summer", S)],
         [("Arena Rector", SIS)], [("Swan Song", SIS)], [("Doubling Season", SIS)],
         [("Arena Rector", SIS), ("Swan Song", D), ("Veil of Summer", G), ("Oath of Nissa", S), ("Farseek", V)],
         [("Arena Rector", SIS), ("Swan Song", "Loyal Tutor")], [("Arena Rector", SIS), ("Swan Song", "Tam, the Possibility")],
         [("Arena Rector", "Tam, the Possibility"), ("Swan Song", "Loyal Tutor")]]
PROFILES = ("mixed", "go_wide", "voltron", "low")


class Timeout(Exception):
    pass


def alarm(_sig, _frm):
    raise Timeout()


signal.signal(signal.SIGALRM, alarm)
part, nparts, N, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
res = {"std": 0, "res": 0, "errors": [], "hangs": 0, "cast_or_entered": {c: 0 for c in pb.CANDIDATE_PWS + pb.CANDIDATE_CREATURES},
       "ults": {"dihada_ult": 0, "vronos_ult": 0, "sisay_activations": 0, "arena_rector_outlet_Damn": 0, "arena_rector_outlet_Void Rend": 0}}
for i in range(part, N, nparts):
    sw = SWAPS[i % len(SWAPS)]
    # chave de sensibilidade da linha deliberada da Arena Rector: 1 partida em 3 (o resto roda com o padrao, desligada)
    pb.CAND_POLICY["arena_rector_outlet"] = (i % 3 == 0)
    pb.CAND_POLICY["arena_rector_outlet_pre_hand"] = (i % 2 == 0)
    for mode in ("std", "res"):
        seed = (3_000_000 if mode == "std" else 6_000_000) + 100_000 + i
        signal.alarm(20)
        try:
            if mode == "std":
                r = pb.simulate_one(seed, 10, False, swap=sw)
                cs = r["cand_stats"]
            else:
                s = pb.simulate_one_with_interaction(seed, turns=10, attack_profile=PROFILES[(i // len(SWAPS)) % 4], swap=sw)
                cs = s.cand_stats
            for c in pb.CANDIDATE_PWS + pb.CANDIDATE_CREATURES:
                if cs.get("entered_" + c, 0) > 0:
                    res["cast_or_entered"][c] += 1
            for k in res["ults"]:
                res["ults"][k] += 1 if cs.get(k, 0) > 0 else 0
            res[mode] += 1
        except Timeout:
            res["hangs"] += 1
            res["errors"].append((mode, seed, "TRAVOU (>20s)"))
        except Exception:
            res["errors"].append((mode, seed, traceback.format_exc()[-400:]))
        finally:
            signal.alarm(0)
json.dump(res, open(out, "w"))
print(part, res["std"], res["res"], "erros:", len(res["errors"]), "travamentos:", res["hangs"], flush=True)
