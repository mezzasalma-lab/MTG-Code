"""Diferencas pareadas (mesma semente) entre as variantes do A/B de 10.000 partidas, em pares que a tabela do fx_ab.py (sempre contra `antes`) nao mostra:
`animados` - `tudo` (metade dos animados contra sacrificar todos os animados, regra da 6a rodada) e `animados` - `sem` (custo/ganho do farm com Dictate com a reserva de
metade dos animados). IC95% = 1,96*dp/raiz(N) da diferenca pareada. Le so' os brutos (.json.xz). Uso: python3 comparar_pares.py"""
import math, os, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
from raw_io import carregar_raw

TURNS = 8
METRICAS = (("win<=8 (pp)", lambda r: 100.0 if (r["win_turn"] and r["win_turn"] <= TURNS) else 0.0), ("estoque no fim", lambda r: float(r["tend"])),
            ("mortes de criatura", lambda r: float(r["creature_deaths"])), ("gatilhos do Dictate", lambda r: float(r["dictate"])),
            ("Treasures-criatura so' pelo Dictate", lambda r: float(r["farm_dic"])))


def ic(a, b):
    d = [y - x for x, y in zip(a, b)]
    return st.mean(d), (1.96 * st.stdev(d) / math.sqrt(len(d)) if len(set(d)) > 1 else 0.0)


for sufixo, rotulo in (("", "padrao"), ("_resiliencia", "resiliencia")):
    bruto = carregar_raw(os.path.join(F.HERE, "dados", "raw_ab_10000%s" % sufixo))
    print("N=10000 sementes 3000000..3009999, modo %s (diferenca pareada A - B, IC95%%)" % rotulo)
    print("%-38s %-22s %-22s" % ("metrica", "animados - tudo", "animados - sem"))
    for nome, f in METRICAS:
        v = {k: [f(r) for r in rs] for k, rs in bruto.items()}
        m1, h1 = ic(v["tudo"], v["animados"])
        m2, h2 = ic(v["sem"], v["animados"])
        print("%-38s %+8.3f ±%-10.3f %+8.3f ±%-10.3f" % (nome, m1, h1, m2, h2))
    print()
