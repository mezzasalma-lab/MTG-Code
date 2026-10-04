"""Bit-identidade, partida a partida, modos padrao e resiliencia:
  (a) DEPOIS com a chave DESTA rodada desligada (base da metade volta a ser o estoque) == ANTES (commit 9e613ea)
  (b) DEPOIS com as chaves da 7a e da 8a desligadas == ANTES0 (commit 8e9ab6e, o Dictate sacrifica todos os animados)
Uso: python3 bitident.py [N] [semente0]"""
import os, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1_000_000


def job(args):
    rotulo, base, modo = args
    A = F.carrega(F.ANTES if base == "9e613ea" else F.ANTES0, "vih_antes_%s_%s" % (base, modo))
    D = F.carrega(F.DEPOIS, "vih_depois_%s_%s" % (base, modo))
    F.flags(D, half=(base == "9e613ea"), animados=False)
    fa = A.simulate_one if modo == "padrao" else A.simulate_one_with_interaction
    fd = D.simulate_one if modo == "padrao" else D.simulate_one_with_interaction
    dif = sum(1 for i in range(N) if F.impressao(fa(SEED + i)) != F.impressao(fd(SEED + i)))
    return rotulo, modo, dif


if __name__ == "__main__":
    jobs = [("(a) chave desta rodada desligada x 9e613ea", "9e613ea", "padrao"), ("(a) chave desta rodada desligada x 9e613ea", "9e613ea", "resiliencia"),
            ("(b) chaves da 7a e 8a desligadas x 8e9ab6e", "8e9ab6e", "padrao"), ("(b) chaves da 7a e 8a desligadas x 8e9ab6e", "8e9ab6e", "resiliencia")]
    with Pool(4) as p:
        for rotulo, modo, dif in p.map(job, jobs):
            print(f"{rotulo} | {modo}: N={N} seed_base={SEED} partidas diferentes={dif} -> {'BIT-IDENTICO' if dif == 0 else 'DIVERGE'}")
