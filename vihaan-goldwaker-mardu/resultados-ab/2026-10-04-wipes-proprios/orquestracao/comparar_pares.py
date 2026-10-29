"""Diferencas pareadas (mesma semente) entre as variantes do A/B de 10.000 partidas, em pares que a tabela do fx_ab.py (sempre contra `antes`) nao mostra:
`todas` - `sem_hold` (o efeito da retencao, linha do usuario, sobre a destruicao de verdade + virado + custo + imposto) e `sem_hold` - `oraculo` (o efeito do
custo da Blasphemous Act + imposto do comandante, dado a destruicao). IC95% = 1,96*dp/raiz(N) da diferenca pareada. Le so' os brutos (.json.xz).
Uso: python3 comparar_pares.py"""
import math, os, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
from raw_io import carregar_raw

TURNS = 8
METRICAS = (("win<=8 (pp)", lambda r: 100.0 if (r["win_turn"] and r["win_turn"] <= TURNS) else 0.0), ("estoque no fim", lambda r: float(r["tend"])),
            ("Treasures criados", lambda r: float(r["treasures"])), ("mortes de criatura", lambda r: float(r["creature_deaths"])),
            ("Blood Money conjurada", lambda r: float(r["bm"])), ("Blasphemous Act conjurada", lambda r: float(r["act"])),
            ("wipe c/ Vihaan ou Mahadi em campo", lambda r: float(r["eng"])), ("Vihaan conjurado (cast)", lambda r: float(r["cmd_casts"])))


def ic(a, b):
    d = [y - x for x, y in zip(a, b)]
    return st.mean(d), (1.96 * st.stdev(d) / math.sqrt(len(d)) if len(set(d)) > 1 else 0.0)


for sufixo, rotulo in (("", "padrao"), ("_resiliencia", "resiliencia")):
    bruto = carregar_raw(os.path.join(F.HERE, "dados", "raw_ab_10000%s" % sufixo))
    print("N=10000 sementes 3000000..3009999, modo %s (diferenca pareada A - B, IC95%%)" % rotulo)
    print("%-38s %-22s %-22s" % ("metrica", "todas - sem_hold", "sem_hold - oraculo"))
    for nome, f in METRICAS:
        v = {k: [f(r) for r in rs] for k, rs in bruto.items()}
        m1, h1 = ic(v["sem_hold"], v["todas"])
        m2, h2 = ic(v["oraculo"], v["sem_hold"])
        print("%-38s %+8.3f ±%-10.3f %+8.3f ±%-10.3f" % (nome, m1, h1, m2, h2))
    print()
