"""Explica os jogos cujo estado final muda no A/B do Sephiroth sem mudar nenhuma metrica: compara campo a campo ANTES x variante
(mesma semente) e conta quais campos de GameState divergem. Uso: python3 explica_diferencas.py [variante] [N] [modo]"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
var = sys.argv[1] if len(sys.argv) > 1 else "emblema"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
modo = sys.argv[3] if len(sys.argv) > 3 else "padrao"
A = F.carrega(F.ANTES, "vih_antes_x")
D = F.flags(F.carrega(F.DEPOIS, "vih_depois_x"), emblema=var in ("emblema", "todas"), simultaneas=var in ("simultaneas", "todas"), fronteira=var in ("fronteira", "todas"))
fa = A.simulate_one if modo == "padrao" else A.simulate_one_with_interaction
fd = D.simulate_one if modo == "padrao" else D.simulate_one_with_interaction
campos, jogos = collections.Counter(), 0
for i in range(N):
    sd = 1_000_000 + i
    a, d = fa(sd, 8), fd(sd, 8)
    dif = [k for k in vars(a) if k not in F.NOVOS and getattr(a, k) != getattr(d, k)]
    if dif:
        jogos += 1
        campos.update(dif)
print(f"variante={var} modo={modo} N={N}: jogos com estado final diferente={jogos}")
for k, v in campos.most_common():
    print(f"  campo {k}: diverge em {v} jogos")
