"""Bit-identidade: DEPOIS com as chave desta rodada desligadas == ANTES (commit 8e9ab6e), partida a partida, modo padrao e resiliencia."""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fx_common as F

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1_000_000
A = F.carrega(F.ANTES, "vih_antes")
D = F.flags(F.carrega(F.DEPOIS, "vih_depois"), half=False)
for nome, fa, fd in (("padrao", A.simulate_one, D.simulate_one),
                     ("resiliencia", A.simulate_one_with_interaction, D.simulate_one_with_interaction)):
    dif = sum(1 for i in range(N) if F.impressao(fa(SEED + i)) != F.impressao(fd(SEED + i)))
    print(f"{nome}: N={N} seed_base={SEED} partidas diferentes={dif} -> {'BIT-IDENTICO' if dif == 0 else 'DIVERGE'}")
