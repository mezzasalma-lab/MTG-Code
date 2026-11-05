"""Bit-identidade: a base do harness (sem a Pride na lista, PRIDE_MODE=off) tem de bater com o simulador ORIGINAL sem patch (módulo separado):
(1) `simulate_one` do original x `simulate_one` remendado; (2) `sim_state` do harness (cópia de simulate_one que devolve o estado) x original, em 12 campos.
Uso: python3 bitident.py [N] [turnos]"""
import importlib.util, os, sys
sys.path.insert(0, '.')
import thr_harness as H
N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
TURNS = int(sys.argv[2]) if len(sys.argv) > 2 else 8
spec = importlib.util.spec_from_file_location("thranduil_pristine", os.path.join(H.REPO, "thranduil-sultai", "thranduil_goldfish_v1.py"))
P = importlib.util.module_from_spec(spec); sys.modules["thranduil_pristine"] = P; spec.loader.exec_module(P)
assert P.DECKLIST_TEXT == H.ORIG_DECKLIST
H.T.DECKLIST_TEXT = H.ORIG_DECKLIST; H.PRIDE_MODE["mode"] = "off"
campos = ["commander_cast_turn", "finisher_turn", "extra_draws", "spells_cast", "thranduil_legendary_elf_triggers", "combat_damage_draws",
          "creature_engine_draws", "hand_size", "blue_screw_turns", "mulligans", "lands_played_total", "cards_discarded_to_hand_size"]
d1 = d2 = 0
for i in range(N):
    sd = 3_000_000 + i
    a = P.simulate_one(sd, TURNS)
    b = H.T.simulate_one(sd, TURNS)
    if a != b: d1 += 1
    s = H.sim_state(sd, TURNS, H.ORIG_DECKLIST)
    c = {"commander_cast_turn": s.commander_cast_turn, "finisher_turn": s.finisher_turn, "extra_draws": s.extra_draws, "spells_cast": s.spells_cast,
         "thranduil_legendary_elf_triggers": s.thranduil_legendary_elf_triggers, "combat_damage_draws": s.combat_damage_draws,
         "creature_engine_draws": s.creature_engine_draws, "hand_size": len(s.hand), "blue_screw_turns": s.blue_screw_turns, "mulligans": s.mulligans,
         "lands_played_total": s.lands_played_total, "cards_discarded_to_hand_size": s.cards_discarded_to_hand_size}
    if any(a[k] != c[k] for k in campos): d2 += 1
print(f"Thranduil: simulate_one original x remendado: {N - d1}/{N} idênticas (dict completo); sim_state do harness x original: {N - d2}/{N} idênticas em {len(campos)} campos")
