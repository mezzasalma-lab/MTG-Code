"""Teto do elo Tergrid's Lantern -> crime -> Deepmuck Desperado / Freestrider Lookout (Regra #4/#5): a Lantern mira um jogador (`{T}: Target player loses 3 life unless...`);
mirar oponente e' crime (ruling 2024-04), e Deepmuck/Freestrider disparam 1x por turno. Quanto espaco a Lantern teria? = turnos em que o Deepmuck JA' esta em campo e NAO houve crime.
Instrumenta `play_turn` (sem editar o simulador): ao fim de cada turno meu le `crime_this_turn`. Uso: python3 crime_deepmuck.py N modo"""
import importlib.util, os, sys
DECK = "/home/user/MTG-Code/wise-mothman-sultai"
os.chdir(DECK)
spec = importlib.util.spec_from_file_location("mm", f"{DECK}/mothman_goldfish_v1.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
if hasattr(m, "LANDFALL_PAYOFF_FIRST"):
    m.LANDFALL_PAYOFF_FIRST = False        # estes numeros foram gerados ANTES da chave (simulador 91b1a3d); False e' bit-identico a ele (resultados-ab/2026-10-06-landfall-payoff-primeiro)
N = int(sys.argv[1]); modo = sys.argv[2]
fn = m.simulate_one if modo == "padrao" else m.simulate_one_with_interaction
orig = m.play_turn
acc = {"dm_turnos": 0, "dm_sem_crime": 0, "fr_turnos": 0, "fr_sem_crime": 0}
jogo = {"dm": 0, "fr": 0}
def wrap(state):
    orig(state)
    if m.has_perm(state, "Deepmuck Desperado"):
        acc["dm_turnos"] += 1; jogo["dm"] += 1
        if not state.crime_this_turn.get("deepmuck"):
            acc["dm_sem_crime"] += 1
    if m.has_perm(state, "Freestrider Lookout"):
        acc["fr_turnos"] += 1; jogo["fr"] += 1
        if not state.crime_this_turn.get("freestrider"):
            acc["fr_sem_crime"] += 1
m.play_turn = wrap
com_dm = com_fr = 0
for sd in range(3_000_000, 3_000_000 + N):
    jogo["dm"] = jogo["fr"] = 0
    fn(sd, 12)
    com_dm += jogo["dm"] > 0; com_fr += jogo["fr"] > 0
assert acc["dm_turnos"] > 0 and acc["fr_turnos"] > 0
print(f"modo {modo}: N={N} | Deepmuck em campo em {100*com_dm/N:.2f}% das partidas: {acc['dm_turnos']} turnos-com-Deepmuck, dos quais {acc['dm_sem_crime']} SEM crime ({100*acc['dm_sem_crime']/acc['dm_turnos']:.1f}%) = {acc['dm_sem_crime']/N:.3f} turnos/partida em que a Lantern teria espaco (3 cartas x oponentes vivos cada)")
print(f"modo {modo}: Freestrider em campo em {100*com_fr/N:.2f}% das partidas: {acc['fr_turnos']} turnos-com-Freestrider, dos quais {acc['fr_sem_crime']} SEM crime ({100*acc['fr_sem_crime']/acc['fr_turnos']:.1f}%)")
