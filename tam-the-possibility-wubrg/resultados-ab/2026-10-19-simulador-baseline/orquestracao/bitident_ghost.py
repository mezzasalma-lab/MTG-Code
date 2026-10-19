"""Bit-identidade do ensaio a seco do 'terreno virado primeiro' (CLAUDE.md Regra #10, item 2): com a chave ligada em modo GHOST (roda o ensaio mas joga o padrao) o resultado tem que ser
IDENTICO, campo a campo, ao da chave desligada, partida a partida. Prova que o ensaio nao tem efeito colateral (copia do estado, uid restaurado).
Uso: python3 bitident_ghost.py [N]   (sementes 9_000_000+i, 2 modos)."""
import os, sys
os.environ["PYTHONHASHSEED"] = os.environ.get("PYTHONHASHSEED", "0")
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
SIM = os.path.join(DECK, "tam_goldfish_v1.py")
for modo in ("padrao", "resiliencia"):
    mA = A.carrega(SIM, "g_off_" + modo, DECK); mA.TAPPED_LAND_FIRST_ENABLED = False
    mB = A.carrega(SIM, "g_ghost_" + modo, DECK); mB.TAPPED_LAND_FIRST_ENABLED = True; mB.TAPPED_LAND_FIRST_GHOST = True
    dif = []
    for sd in range(9_000_000, 9_000_000 + N):
        a = A.impressao(A.chama(mA, modo, sd, 12)); b = A.impressao(A.chama(mB, modo, sd, 12))
        if a != b:
            dif.append(sd)
    print(f"{modo:12s} N={N}: partidas com resultado diferente (ghost x desligado) = {len(dif)} {dif[:5]}")
