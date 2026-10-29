"""Bit-identidade: DEPOIS com as DUAS correcoes desligadas == ANTES (commit 22d0ed2),
partida a partida (impressao digital do estado final inteiro), modo padrao e modo
de resiliencia. Uso: python3 bitident.py [N] [seed_base]"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fx_common as F

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1_000_000
A = F.carrega(F.ANTES, "mega_antes")
D = F.flags(F.carrega(F.DEPOIS, "mega_depois"), tapped=False, myriad=False)
for nome, fa, fd in (("padrao", A.simulate_one, D.simulate_one),
                     ("resiliencia", A.simulate_one_with_interaction, D.simulate_one_with_interaction)):
    dif = 0
    for i in range(N):
        if F.impressao(fa(SEED + i)) != F.impressao(fd(SEED + i)):
            dif += 1
    print(f"{nome}: N={N} seed_base={SEED} partidas diferentes={dif} -> {'BIT-IDENTICO' if dif == 0 else 'DIVERGE'}")
