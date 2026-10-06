"""Quantas partidas o Kozilek (unica fonte de 'oponente sacrifica' na lista) chega a ATACAR? = teto de quantas partidas a Tergrid poderia disparar por sacrificio.
Instrumenta `pick_attackers` do simulador (sem editar o arquivo). Uso: python3 frequencia_annihilator.py N modo"""
import importlib.util, os, sys, collections
DECK = "/home/user/MTG-Code/wise-mothman-sultai"
os.chdir(DECK)
spec = importlib.util.spec_from_file_location("mm", f"{DECK}/mothman_goldfish_v1.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
N = int(sys.argv[1]); modo = sys.argv[2]
fn = m.simulate_one if modo == "padrao" else m.simulate_one_with_interaction
orig = m.pick_attackers
cont = {"ataques": 0}
def wrap(state):
    r = orig(state)
    if any(m.eff_name(p) == "Kozilek, Butcher of Truth" for p in r):
        cont["ataques"] += 1
    return r
m.pick_attackers = wrap
jogos_com_ataque = 0; ataques_tot = 0; cast = 0; viva_depois = 0
for sd in range(3_000_000, 3_000_000 + N):
    cont["ataques"] = 0
    st = fn(sd, 12)
    ataques_tot += cont["ataques"]
    if cont["ataques"] > 0:
        jogos_com_ataque += 1
    if st.kozilek_cast_turn is not None:
        cast += 1
print(f"modo {modo}: N={N} | Kozilek conjurado em {100*cast/N:.2f}% | Kozilek ATACA ao menos 1x em {100*jogos_com_ataque/N:.2f}% ({jogos_com_ataque} partidas, > 0) | ataques totais {ataques_tot} ({ataques_tot/max(1,jogos_com_ataque):.2f} por partida em que ataca)")
