"""Bit-identidade do ensaio a seco do 'terreno virado primeiro' (CLAUDE.md Regra #10, item 2): com a chave ligada em modo GHOST (roda o ensaio mas joga o padrao) o resultado tem que ser
IDENTICO, campo a campo, ao da chave desligada, partida a partida. Prova que o ensaio nao tem efeito colateral (copia do estado, uid restaurado).
Uso: python3 bitident_ghost.py [N]   (sementes 9_000_000+i, 2 modos, 4 processos; a impressao digital do estado inteiro custa ~0,4 s por partida)."""
import os, sys
os.environ["PYTHONHASHSEED"] = os.environ.get("PYTHONHASHSEED", "0")
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
from multiprocessing import Pool
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
SIM = os.path.join(DECK, "tam_goldfish_v1.py")


def job(args):
    modo, seeds, k = args
    mA = A.carrega(SIM, f"g_off_{modo}_{k}", DECK); mA.TAPPED_LAND_FIRST_ENABLED = False
    mB = A.carrega(SIM, f"g_ghost_{modo}_{k}", DECK); mB.TAPPED_LAND_FIRST_ENABLED = True; mB.TAPPED_LAND_FIRST_GHOST = True
    # o ensaio a seco INCREMENTA 2 contadores de metrica (`tapped_land_first_plays`, `tapped_land_skipped_for_play`) mesmo no modo ghost; eles (e o Counter `m` que os contem) ficam fora da comparacao:
    # o resto do estado (campo, mao, cemiterio, biblioteca, vida, todos os outros m_*) tem que ser IDENTICO
    ign = ("m", "ghost", "m_tapped_land_first_plays", "m_tapped_land_skipped_for_play")
    return [sd for sd in seeds if A.impressao(A.chama(mA, modo, sd, 12), ign) != A.impressao(A.chama(mB, modo, sd, 12), ign)]


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    for modo in ("padrao", "resiliencia"):
        seeds = list(range(9_000_000, 9_000_000 + N))
        blocos = [(modo, seeds[i::8], i) for i in range(8)]
        with Pool(4) as p:
            dif = sorted(x for r in p.map(job, blocos) for x in r)
        print(f"{modo:12s} N={N}: partidas com resultado diferente (ghost x desligado) = {len(dif)} {dif[:5]}", flush=True)
