"""
Teste pontual pedido pelo usuario (2026-08-23): qual a probabilidade do
"motor de flash em criaturas" estar online nos turnos 4-8, COM e SEM
Radagast of Rhosgobel na lista?

Metodologia:
- "Motor de flash universal" = pelo menos 1 destre Leyline of Anticipation,
  Vedalken Orrery, High Fae Trickster, Alchemist's Refuge em campo no fim
  do turno (FLASH_SOURCES em maralen_goldfish_v1.py).
- Radagast of Rhosgobel NAO concede flash universal -- so a primeira
  magica de criatura do turno, com reducao de {2}. Por isso reporto os
  dois numeros separados: (a) o motor universal puro (deve ser
  estatisticamente igual nas duas listas, ja que a troca foi Radagast <->
  Elves of Deep Shadow, nenhuma das duas e fonte de flash universal --
  serve de checagem de sanidade), e (b) "flash em criaturas disponivel"
  incluindo Radagast como fonte parcial (so a 1a criatura/turno), que E
  o numero que isola o valor real de incluir o Radagast.

Duas variantes de biblioteca, 99 cartas cada, testadas com as MESMAS
seeds (comparacao pareada, nao amostras independentes):
- "Com Radagast": a lista atual real (lista.md).
- "Sem Radagast": lista atual com Radagast of Rhosgobel trocado de volta
  por Elves of Deep Shadow (a carta que ele substituiu).
"""

import maralen_goldfish_v1 as sim

N = 3000
SEED_BASE = 9500000
TURNS = 8
CHECKPOINTS = [4, 5, 6, 7, 8]


def build_without_radagast():
    lib = sim.BASE_LIBRARY[:]
    idx = lib.index("Radagast of Rhosgobel")
    lib[idx] = "Elves of Deep Shadow"
    return lib


def run_variant(label, library):
    universal_hits = {t: 0 for t in CHECKPOINTS}
    combined_hits = {t: 0 for t in CHECKPOINTS}
    for i in range(N):
        s = sim.simulate_one(seed=SEED_BASE + i, turns=TURNS, library=library)
        for t in CHECKPOINTS:
            if any(s.flash_universal_by_turn.get(tt, False) for tt in range(1, t + 1)):
                universal_hits[t] += 1
            if any(s.flash_with_radagast_by_turn.get(tt, False) for tt in range(1, t + 1)):
                combined_hits[t] += 1
    print(f"=== {label} (n={N}) ===")
    print("Turno | motor universal online | motor universal+Radagast online")
    for t in CHECKPOINTS:
        pu = 100 * universal_hits[t] / N
        pc = 100 * combined_hits[t] / N
        print(f"  T{t}  |  {pu:5.1f}%                 |  {pc:5.1f}%")
    print()
    return universal_hits, combined_hits


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print(f"n={N} por variante, seeds pareadas (mesmo seed_base={SEED_BASE}), {TURNS} turnos\n")

    u_with, c_with = run_variant("COM Radagast (lista atual)", sim.BASE_LIBRARY)
    u_without, c_without = run_variant("SEM Radagast (Elves of Deep Shadow no lugar)", build_without_radagast())

    print("=== Resumo — 'motor de flash em criaturas disponivel' (universal + Radagast quando presente) ===")
    print("Turno | COM Radagast | SEM Radagast | Delta (pontos percentuais)")
    for t in CHECKPOINTS:
        pc_with = 100 * c_with[t] / N
        pc_without = 100 * c_without[t] / N
        print(f"  T{t}  |  {pc_with:5.1f}%      |  {pc_without:5.1f}%      |  {pc_with - pc_without:+.1f}pp")

    print()
    print("=== Checagem de sanidade — motor universal PURO (deve ser ~igual nas duas listas) ===")
    print("Turno | COM Radagast na lista | SEM Radagast na lista")
    for t in CHECKPOINTS:
        print(f"  T{t}  |  {100*u_with[t]/N:5.1f}%                |  {100*u_without[t]/N:5.1f}%")
