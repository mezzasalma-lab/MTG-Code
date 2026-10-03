"""Compara a partida manual (8 turnos) com o simulador do Vihaan vivo: (1) Treasures criados acumulados ao fim de cada turno T5..T8
(a partida: 2, 8, 15, 21), media e posicao no simulador; (2) por fonte (create_treasures(source=...)) ate' o T8; (3) terrenos exilados
pelo Prosper/impulso que o simulador nunca joga (play_from_impulse exclui terreno); (4) comandante T3, mana T2..T4.
Uso: [FX_MODO=resiliencia] python3 comparacao_simulador.py [N] [semente0]"""
import collections, importlib.util, os, statistics as st, sys
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(REPO)
SIM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "codigo", "vihaan_goldfish_v1_c04840d.py")  # simulador como estava no commit c04840d (antes de qualquer correcao do terreno do Prosper)
spec = importlib.util.spec_from_file_location("vih_cmp", SIM)
V = importlib.util.module_from_spec(spec); sys.modules["vih_cmp"] = V; spec.loader.exec_module(V)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
S0 = int(sys.argv[2]) if len(sys.argv) > 2 else 3_000_000
MODO = os.environ.get("FX_MODO", "padrao")
REAL = {5: 2, 6: 8, 7: 15, 8: 21}  # criados acumulados (ledger da partida: 2 + 6 + 7 + 6)

por_turno = collections.defaultdict(list)
fontes = collections.Counter()
impulso_terrenos = []
cmd_cast, mana = [], collections.defaultdict(list)
cur = {"fonte": collections.Counter(), "terrenos": 0, "prosper_terrenos": 0}

orig_ct = V.create_treasures
def ct(state, n, source=""):
    antes = state.treasures_created_total
    orig_ct(state, n, source)
    cur["fonte"][source or "?"] += state.treasures_created_total - antes
V.create_treasures = ct
orig_pi = V.pull_impulse
def pi(state, n, deadline_turns):
    antes = len(state.impulse_pool)
    orig_pi(state, n, deadline_turns)
    for card, _ in state.impulse_pool[antes:]:
        if V.CARD_DB[card].ctype == "land":
            cur["terrenos"] += 1
            if "Prosper, Tome-Bound" in state.battlefield:
                cur["prosper_terrenos"] += 1
V.pull_impulse = pi
orig_et = V.end_step
def et(state):
    orig_et(state)
    if state.turn >= 5:
        por_turno[state.turn].append(state.treasures_created_total)
V.end_step = et
orig_pl = V.play_land
def pl(state):
    orig_pl(state)
    if 2 <= state.turn <= 4:
        mana[state.turn].append(V.total_mana(state))
V.play_land = pl

fn = V.simulate_one if MODO == "padrao" else V.simulate_one_with_interaction
tot_t8 = []
for i in range(N):
    cur["fonte"].clear(); cur["terrenos"] = 0; cur["prosper_terrenos"] = 0
    s = fn(S0 + i, 8)
    fontes.update(cur["fonte"])
    impulso_terrenos.append((cur["terrenos"], cur["prosper_terrenos"]))
    cmd_cast.append(s.commander_cast_turn or 99)
    tot_t8.append(s.treasures_created_total)

print("SIMULADOR (snapshot c04840d), modo %s, N=%d sementes %d..%d, 8 turnos (partida manual: 8 turnos)" % (MODO, N, S0, S0 + N - 1))
print("Treasures criados ACUMULADOS ao fim do turno: media | partida | % de jogos do simulador com >= a partida")
for t in (5, 6, 7, 8):
    xs = por_turno[t]
    if len(xs) < N:  # jogo que terminou antes (win) nao tem o turno: completa com o ultimo valor
        xs = xs + [0] * (N - len(xs))
    print("  T%d: media %.2f | partida %d | %.2f%%" % (t, st.mean(xs), REAL[t], 100 * sum(1 for x in xs if x >= REAL[t]) / N))
q = sorted(tot_t8)
print("Criados ate' o T8: media %.2f, mediana %d, p90 %d, p99 %d, max %d; P(>=21) = %.3f%%" % (st.mean(tot_t8), q[N // 2], q[int(N * .9)], q[int(N * .99)], q[-1], 100 * sum(1 for x in tot_t8 if x >= 21) / N))
print("Por fonte (create_treasures source), media por jogo ate' o T8, maiores:")
for k, v in fontes.most_common(14):
    print("  %-44s %.3f" % (k, v / N))
print("Terrenos que entram no pool de exilio por jogo (play_from_impulse nunca os joga): media %.3f; com Prosper em campo na hora: %.3f; jogos com >=1: %.1f%%" % (
    st.mean(a for a, _ in impulso_terrenos), st.mean(b for _, b in impulso_terrenos), 100 * sum(1 for a, _ in impulso_terrenos if a) / N))
print("Comandante conjurado ate' o T3: %.1f%% (partida: T3)" % (100 * sum(1 for c in cmd_cast if c <= 3) / N))
print("Mana total (apos o terreno) T2 %.2f T3 %.2f T4 %.2f (partida: 2, 3, 5)" % tuple(st.mean(mana[t]) for t in (2, 3, 4)))
