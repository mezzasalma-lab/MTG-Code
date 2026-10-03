"""Achado lateral (nao corrigido): o London Mulligan do simulador poe as cartas devolvidas no TOPO da biblioteca.
(1) demonstracao em runtime com rng de shuffle-identidade e should_keep forcado (mulligans=2 -> penalidade de 1 carta);
(2) frequencia de 2+ mulligans em 20.000 maos reais. Uso: python3 mulligan_topo.py"""
import inspect, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
M = F.carrega(F.DEPOIS, "mega_mull")

class Identidade(random.Random):
    def shuffle(self, x):  # baralho fica na ordem de BASE_LIBRARY
        return None

decisoes = iter([False, False, True])           # 2 mulligans, mantem a 3a mao
M.should_keep, real_keep = (lambda hand: next(decisoes)), M.should_keep
hand, library, mulls = M.mulligan(Identidade(1))
M.should_keep = real_keep
sete_primeiras = M.BASE_LIBRARY[:7]
devolvida = [c for c in sete_primeiras if c not in hand or sete_primeiras.count(c) > hand.count(c)]
print("mulligans =", mulls, "| mao final:", len(hand), "cartas | carta devolvida:", devolvida, "| topo da biblioteca (proxima compra):", library[0])
print("a carta devolvida e' a PROXIMA a ser comprada:", devolvida[0] == library[0])
print("linha em mulligan():", [l.strip() for l in inspect.getsource(M.mulligan).splitlines() if "insert" in l])
print("linha em draw_cards():", [l.strip() for l in inspect.getsource(M.draw_cards).splitlines() if "pop" in l])
cont = {}
for i in range(20000):
    _, _, m = M.mulligan(random.Random(9_000_000 + i))
    cont[m] = cont.get(m, 0) + 1
print("mulligans por mao (N=20000, sementes 9.000.000+i):", {k: "%.1f%%" % (100 * v / 20000) for k, v in sorted(cont.items())},
      "| com 2+ mulligans (penalidade de 1+ carta devolvida ao topo): %.1f%%" % (100 * sum(v for k, v in cont.items() if k >= 2) / 20000))
