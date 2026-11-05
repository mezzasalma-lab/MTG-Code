"""Prova de LEGALIDADE DE MANA turno a turno da partida manual #2 (Gyre Sage, Kami, Henge, Eldrazi Spawn). Uso: python3 mana_por_turno.py > resumos/mana_por_turno.md
Fontes: lands normais; Strip Mine/Swarmyard {C}; Triome {B/G/U}; Gyre Sage: {G} POR CONTADOR +1/+1 (texto real: "{T}: Add {G} for each +1/+1 counter on this creature");
Kami: X de UMA cor, X = poder; The Great Henge: {T}: {G}{G}, e custa {7}{G}{G} menos X, X = MAIOR PODER entre as suas criaturas. O script testa cada turno sob duas leituras da Gyre Sage:
 (a) o TEXTO REAL (um G por contador) e (b) "um G por PONTO DE PODER" (a leitura que faria o T3 e o T4 fecharem). Limites: so' a viabilidade da conta (total e cores); nao prova a ordem de pagamento."""
import itertools, json, lzma, os, re
aqui = os.path.dirname(os.path.abspath(__file__))
ORC = json.load(open(os.path.join(aqui, "..", "..", "..", "scryfall-cache", "oracle-cache.json")))
P = lambda n: int(ORC[n]["power"])
def pips(c):
    return re.findall(r"\{([WUBRGC])\}", c), sum(int(x) for x in re.findall(r"\{(\d+)\}", c))
def viavel(unidades_flex, fixas, cores, gen):
    """unidades_flex: lista de listas de opcoes (cada fonte flexivel escolhe uma lista de unidades); fixas: unidades fixas"""
    for esc in itertools.product(*unidades_flex) if unidades_flex else [()]:
        un = list(fixas) + [u for e in esc for u in e]
        if len(un) < len(cores) + gen:
            continue
        if all(un.count(c) >= cores.count(c) for c in set(cores)):
            return un
    return None
# turno: dados das fontes e das magias. gyre = contadores da Gyre Sage no momento em que foi virada; moth = poder do Mothman ao conjurar o Henge
T3 = dict(t=3, lands=["Swarmyard", "Island", "Zagoth Triome"], gyre=0, spells=[("The Wise Mothman", "{1}{B}{G}{U}")])
T4 = dict(t=4, lands=["Zagoth Triome", "Island", "Swarmyard"], gyre=1, henge=True, spells=[("The Great Henge", None), ("Basking Broodscale", "{1}{G}")])
T5 = dict(t=5, lands=["Zagoth Triome", "Strip Mine", "Swarmyard"], gyre=1, henge_mana=True, spells=[("Winding Constrictor", "{B}{G}"), ("Kami of Whispered Hopes", "{2}{G}")])
T6 = dict(t=6, lands=["Strip Mine", "Swarmyard"], gyre=None, henge_mana=True, spells=[("Ouroboroid", "{2}{G}{G}")])
T2 = dict(t=2, lands=["Island", "Zagoth Triome"], gyre=None, spells=[("Gyre Sage", "{1}{G}")])
FONTE = {"Strip Mine": ["C"], "Swarmyard": ["C"], "Zagoth Triome": ["B", "G", "U"], "Island": ["U"]}
def henge_custo(poder_max):
    g = max(0, 7 - poder_max)
    return ["G", "G"], g
print("# Legalidade de mana por turno (partida manual #2)\n")
print("| T | magias pagas | custo | mana (texto real da Gyre Sage) | viavel (texto real) | mana (Gyre = poder) | viavel (Gyre = poder) |")
print("|---|---|---|---|---|---|---|")
resultado = {}
for D in (T2, T3, T4, T5, T6):
    linhas = []
    for leitura in ("real", "poder"):
        flex = [[[x] for x in FONTE[l]] for l in D["lands"]]
        fixas = []
        g = D.get("gyre")
        if g is not None:
            n = g if leitura == "real" else g + 1          # poder = 1 base + contadores
            if n > 0:
                flex.append([["G"] * n])
        if D.get("henge_mana"):
            fixas += ["G", "G"]                              # o Henge (conjurado antes) vira GG
        cores, gen, desc = [], 0, []
        for nome, custo in D["spells"]:
            if nome == "The Great Henge":
                poder = P("The Wise Mothman") + 1          # Mothman 3 + 1 contador no log
                c, g_ = henge_custo(poder); cores += c; gen += g_; desc.append(f"Henge (X={poder}: {g_}+GG = {g_ + 2})")
            else:
                c, g_ = pips(custo); cores += c; gen += g_; desc.append(nome)
        if D["t"] == 4:
            # o Henge precisa ser pago SO' com as fontes de antes; a Broodscale ({1}{G}) sai do GG que o proprio Henge produz
            c_h, g_h = henge_custo(P("The Wise Mothman") + 1)
            un = viavel(flex, [], c_h, g_h)
            ok = un is not None
            linhas.append((leitura, sum(len(max(f, key=len)) for f in flex), f"{g_h + 2} (Henge; a Broodscale sai do GG dele)", ok, un))
        else:
            un = viavel(flex, fixas, cores, gen)
            prod = sum(len(max(f, key=len)) for f in flex) + len(fixas)
            linhas.append((leitura, prod, f"{len(cores) + gen}", un is not None, un))
    a, b = linhas
    nomes = ", ".join(n for n, _ in D["spells"])
    print(f"| T{D['t']} | {nomes} | {a[2]} | {a[1]} | {'sim' if a[3] else '**NAO**'} | {b[1]} | {'sim' if b[3] else '**NAO**'} |")
    resultado[D["t"]] = (a[3], b[3])
assert not resultado[3][0] and resultado[3][1] and not resultado[4][0] and resultado[4][1], resultado
assert all(resultado[t][0] for t in (2, 5, 6)), resultado
print("\n**T3 e T4 NAO fecham com o texto real da Gyre Sage** (1 G por contador: 0 no T3 e 1 no T4); fecham as duas se a Gyre Sage der 1 G por PONTO DE PODER (1 e 2). T2, T5 e T6 fecham nas duas leituras.")
print("T3: Mothman custa 4 (`{1}{B}{G}{U}`); fontes: Swarmyard + Island + Triome = 3, Gyre Sage sem contador = 0. T4: o Henge custa `{7}{G}{G}` menos o maior poder (Mothman 3 + 1 contador = 4) = 5; fontes: Triome + Island + Swarmyard + Gyre Sage (1 contador) = 4; o log nao tem terreno jogado no T4 (a Takenuma estava na mao).")
