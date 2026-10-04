"""Bit-identidade, partida a partida, modos padrao e resiliencia: DEPOIS com a chave da 12a rodada (Mythos no lugar do Blood Money) desligada == ANTES (commit a17049f).
Com a chave desligada a lista do repositorio volta a ter o Blood Money na posicao antiga (build_library), e o snapshot le a lista legada (`resultados-ab/_lista_legada`).
Uso: python3 bitident.py [N] [semente0]"""
import os, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1_000_000


def job(modo):
    A = F.carrega(F.ANTES, "vih_antes_%s" % modo)
    D = F.flags(F.carrega(F.DEPOIS, "vih_depois_%s" % modo), mythos=False)
    assert A.BASE_LIBRARY == D.BASE_LIBRARY, "biblioteca diferente com a chave desligada"
    fa = A.simulate_one if modo == "padrao" else A.simulate_one_with_interaction
    fd = D.simulate_one if modo == "padrao" else D.simulate_one_with_interaction
    dif = sum(1 for i in range(N) if F.impressao(fa(SEED + i)) != F.impressao(fd(SEED + i)))
    return modo, dif


if __name__ == "__main__":
    with Pool(2) as p:
        for modo, dif in p.map(job, ["padrao", "resiliencia"]):
            print(f"{modo}: N={N} seed_base={SEED} partidas diferentes={dif} -> {'BIT-IDENTICO' if dif == 0 else 'DIVERGE'}")
