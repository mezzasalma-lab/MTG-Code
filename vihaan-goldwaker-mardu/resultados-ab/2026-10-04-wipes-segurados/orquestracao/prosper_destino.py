"""O que acontece com cada carta que o Prosper exila no end step: terreno jogado (+Pact Boon), magia conjurada, expirou sem uso, ou ainda valida
no fim do jogo. Usa o simulador indicado (arquivo vivo por padrao; FX_SIM=caminho). Variaveis: FX_MODO=resiliencia. Uso: python3 prosper_destino.py [N] [semente0]"""
import collections, inspect, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
S0 = int(sys.argv[2]) if len(sys.argv) > 2 else 3_000_000
caminho = os.path.abspath(os.environ["FX_SIM"]) if os.environ.get("FX_SIM") else F.DEPOIS
V = F.flags(F.carrega(caminho, "vih_prosper"))
MODO = os.environ.get("FX_MODO", "padrao")
cont = collections.Counter()
por_carta = {"puxada": collections.Counter(), "jogada": collections.Counter(), "expirou": collections.Counter()}
cur = {"puxadas": collections.Counter(), "jogadas": collections.Counter()}

orig_pull = V.pull_impulse
def pull(state, n, deadline_turns, lands_ok=False):
    antes_pool, antes_land = list(state.impulse_pool), list(getattr(state, "impulse_lands", []))
    orig_pull(state, n, deadline_turns, lands_ok) if "lands_ok" in orig_pull.__code__.co_varnames else orig_pull(state, n, deadline_turns)
    if inspect.stack()[1].function == "end_step" and "Prosper, Tome-Bound" in state.battlefield:
        novas = [e for e in state.impulse_pool if e not in antes_pool or state.impulse_pool.count(e) > antes_pool.count(e)]
        novas += [e for e in getattr(state, "impulse_lands", []) if e not in antes_land or state.impulse_lands.count(e) > antes_land.count(e)]
        for e in novas:
            cur["puxadas"][e] += 1
V.pull_impulse = pull
if hasattr(V, "play_impulse_land"):
    orig_land = V.play_impulse_land
    def pil(state):
        antes = list(state.impulse_lands)
        ok = orig_land(state)
        if ok:
            for e in antes:
                if e not in state.impulse_lands or state.impulse_lands.count(e) < antes.count(e):
                    cur["jogadas"][e] += 1
                    break
        return ok
    V.play_impulse_land = pil
orig_pfi = V.play_from_impulse
def pfi(state, *a, **k):
    antes = list(state.impulse_pool)
    ok = orig_pfi(state, *a, **k)
    for e in antes:
        if state.impulse_pool.count(e) < antes.count(e):
            cur["jogadas"][e] += 1
            break
    return ok
V.play_from_impulse = pfi

fn = V.simulate_one if MODO == "padrao" else V.simulate_one_with_interaction
jogos_com_prosper = 0
for i in range(N):
    cur["puxadas"].clear(); cur["jogadas"].clear()
    s = fn(S0 + i, 8)
    if not cur["puxadas"]:
        continue
    jogos_com_prosper += 1
    for e, k in cur["puxadas"].items():
        tipo = "terreno" if V.CARD_DB[e[0]].ctype == "land" else "magia"
        jog = min(k, cur["jogadas"].get(e, 0))
        cont[(tipo, "jogada")] += jog
        por_carta["puxada"][e[0]] += k
        por_carta["jogada"][e[0]] += jog
        resto = k - jog
        if e[1] > s.turn:  # prazo = ultimo turno ja teve a sua chance de jogo
            cont[(tipo, "ainda valida no fim")] += resto
        else:
            cont[(tipo, "EXPIROU sem uso")] += resto
            por_carta["expirou"][e[0]] += resto
tot = sum(cont.values())
print("%s | modo %s | N=%d sementes %d..%d | jogos com pelo menos 1 exilio do Prosper: %d (%.1f%%) | exilios do Prosper: %d (%.2f por jogo)" % (
    os.path.basename(caminho), MODO, N, S0, S0 + N - 1, jogos_com_prosper, 100 * jogos_com_prosper / N, tot, tot / N))
for tipo in ("terreno", "magia"):
    t = sum(v for (a, b), v in cont.items() if a == tipo)
    for dest in ("jogada", "EXPIROU sem uso", "ainda valida no fim"):
        v = cont.get((tipo, dest), 0)
        print("  %-8s %-22s %6d  (%.1f%% dos %s exilados)" % (tipo, dest, v, 100 * v / t if t else 0, tipo))
print("  wipes proprios (Blood Money / Blasphemous Act) exilados pelo Prosper: puxados %d, jogados %d, expiraram sem uso %d" % (
    sum(por_carta["puxada"][c] for c in ("Blood Money", "Blasphemous Act")), sum(por_carta["jogada"][c] for c in ("Blood Money", "Blasphemous Act")),
    sum(por_carta["expirou"][c] for c in ("Blood Money", "Blasphemous Act"))))
print("  cartas (terreno ou magia) que mais expiraram sem uso (top 6): " + ", ".join("%s %d" % (c, k) for c, k in por_carta["expirou"].most_common(6)))
