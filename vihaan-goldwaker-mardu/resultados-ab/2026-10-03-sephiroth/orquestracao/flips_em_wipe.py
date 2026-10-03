"""Mede, no simulador ANTES (ba74496), de onde vinham as viradas do Sephiroth no modo resiliencia: durante um wipe (do oponente ou
meu Blood Money/Blasphemous Act) com o Sephiroth morrendo junto, durante um wipe com ele sobrevivendo, ou fora de wipe.
Uso: python3 flips_em_wipe.py [N] [semente0]"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
S0 = int(sys.argv[2]) if len(sys.argv) > 2 else 3_000_000
V = F.carrega(F.ANTES, "vih_antes_flips")
SEPH = "Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel"
cont = collections.Counter()
cur = {"onde": None, "morre_junto": None}

def envolve(nome):
    orig = getattr(V, nome)
    def f(state, *a, **k):
        antes_bf = SEPH in state.battlefield
        antes_flag = state.has_super_nova_emblem
        r = orig(state, *a, **k)
        if (not antes_flag) and state.has_super_nova_emblem:
            cont["virou em wipe (%s), Sephiroth %s" % (nome, "MORREU junto" if (antes_bf and SEPH not in state.battlefield) else "sobreviveu")] += 1
            cur["wipe"] = True
        return r
    setattr(V, nome, f)

envolve("try_smart_opponent_wipe")
orig_ris = V.resolve_instant_sorcery
def ris(state, name, *a, **k):
    if name in ("Blood Money", "Blasphemous Act"):
        antes_bf = SEPH in state.battlefield
        antes_flag = state.has_super_nova_emblem
        r = orig_ris(state, name, *a, **k)
        if (not antes_flag) and state.has_super_nova_emblem:
            cont["virou em wipe proprio (%s), Sephiroth %s" % (name, "MORREU junto" if (antes_bf and SEPH not in state.battlefield) else "sobreviveu")] += 1
            cur["wipe"] = True
        return r
    return orig_ris(state, name, *a, **k)
V.resolve_instant_sorcery = ris
total = 0
for i in range(N):
    cur["wipe"] = False
    s = V.simulate_one_with_interaction(S0 + i, 8)
    if s.has_super_nova_emblem:
        total += 1
        if not cur["wipe"]:
            cont["virou fora de wipe"] += 1
print("ANTES (ba74496), modo resiliencia, N=%d sementes %d..%d: jogos com o Sephiroth virado = %d (%.2f%%)" % (N, S0, S0 + N - 1, total, 100 * total / N))
for k, v in sorted(cont.items()):
    print("  %-70s %5d jogos(eventos)" % (k, v))
