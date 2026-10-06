"""Ledger da partida manual do Mothman (2026-10-06): o que o LOG mostra x o que as REGRAS exigem, em tres frentes. Uso: python3 ledger_mill.py > resumos/ledger_mill.md
 (1) mill MEU: fontes esperadas por turno (rad, landfall do Icetill, ataque da Six / do Hedge Shredder) x cartas milladas no log;
 (2) contadores +1/+1: cada gatilho do Mothman ("one or more nonland cards are milled": X = nao-terrenos milados) e cada "support" x contadores postos no log, COM a substituicao
     do Kami of Whispered Hopes ("that many plus one") e do Hardened Scales ("that many plus one");
 (3) mill de OPONENTE reconstruido (o log nao o contem, como o usuario avisou): Ruin Crab (landfall: cada oponente milla 3) e Memory Erosion (oponente conjura: milla 2),
     com o Mothman que isso dispara. Como o log nao diz quais cartas sairam, X e' uma DISTRIBUICAO (Monte Carlo, semente fixa), nao um valor.
SUPOSICOES (leitura minha do trace; cada uma e' conferida contra o log por `assert` abaixo, quando o log permite):
 - a ordem dos registros do log e' a ordem real dos eventos; 3 oponentes; biblioteca de oponente com 37 terrenos / 99 (a mesma convencao do simulador `mothman_goldfish_v1.py`);
 - gatilhos do Mothman por evento de mill (os mills simultaneos de varios jogadores contam como UM evento: ruling de 2024-03-08);
 - criaturas-alvo = as que estao em campo no momento (Veiculo so' conta enquanto tripulado); Kami e Scales: +1 cada, aditivos (CR 616.1; rulings de ambos);
 - o rad do jogador so' e' contado como CAPACIDADE (limite inferior), porque o log nao registra vida nem marcadores de rad."""
import json, lzma, os, random, statistics as st
aqui = os.path.dirname(os.path.abspath(__file__))
T = json.load(lzma.open(os.path.join(aqui, "dados", "partida.json.xz")))
ORC = json.load(open(os.path.join(aqui, "..", "..", "..", "scryfall-cache", "oracle-cache.json")))
def is_land(n):
    return "Land" in (ORC.get(n, {}).get("type_line") or "").split(" // ")[0]
P_NONLAND = 62 / 99          # 37 terrenos / 99 (convencao do simulador)
def ctr_total(e):
    """soma dos marcadores +1/+1 do registro"""
    return sum(v["count"] for k, v in (e.get("counters") or {}).items() if k.startswith("+1"))

# ---- dados medidos direto do log ----
milled = {i: [e["name"] for e in t if e.get("fromZone") == "library" and e.get("toZone") == "graveyard"] for i, t in enumerate(T, 1)}
est = {}
inc = {i: 0 for i in range(1, len(T) + 1)}
for i, t in enumerate(T, 1):
    for e in t:
        prev = est.get(e["id"])
        a = ctr_total(prev) if prev else 0
        b = ctr_total(e)
        if b > a:
            inc[i] += b - a
        est[e["id"]] = e

# ---- eventos (leitura minha) ----
# self: lista de cartas milladas (do log) | opp: (n_oponentes, cartas_cada) | support: n alvos
# alvos = criaturas em campo (sem contar o proprio Patron no support); kami/scales = 1 se em campo no momento; log = contadores postos no log por esse evento
EV = [
 dict(t=4, r="Six ataca (mill 3)", k="self", cards=["Bramble Familiar // Fetch Quest", "Icetill Explorer", "Forest"], alvos=3, kami=1, scales=0, log=0, nota="Mothman ja' em campo (conjurado antes do ataque); alvos: Mothman, Six, Kami"),
 dict(t=5, r="mill de 1 carta com nao-terreno (Ashiok); a outra (Waterlogged Grove) e' terreno", k="self", cards=["Ashiok, Dream Render"], alvos=4, kami=1, scales=0, log=1, nota="Kami recebeu o contador; alvos: Mothman, Six, Kami, Icetill"),
 dict(t=6, r="landfall do Icetill (Overgrown Tomb): Ruin Crab milado", k="self", cards=["Ruin Crab"], alvos=4, kami=1, scales=0, log=1, nota="Mothman recebeu o contador; alvos: Mothman, Six, Kami, Icetill"),
 dict(t=6, r="Hedge Shredder ataca (mill 2)", k="self", cards=["Hardened Scales", "Smuggler's Surprise"], alvos=6, kami=1, scales=0, log=2, nota="Kami e Mothman receberam 1 cada; alvos: Mothman, Six, Kami, Icetill, Ruin Crab, Shredder (tripulado)"),
 dict(t=6, r="Memory Erosion: o oponente simulado conjura Aven Mindcensor (milla 2)", k="opp", n_opp=1, cada=2, alvos=6, kami=1, scales=0, log=0, nota="nao esta no log"),
 dict(t=7, r="Generous Patron: support 2 (nao e' gatilho do Mothman)", k="support", n=2, alvos=5, kami=1, scales=0, log=2, nota="Icetill e Ruin Crab receberam 1 cada"),
 dict(t=7, r="Agatha's Soul Cauldron milado (fonte nao identificada: rad?)", k="self", cards=["Agatha's Soul Cauldron"], alvos=6, kami=1, scales=0, log=1, nota="Six recebeu o contador"),
 dict(t=7, r="Hedge Shredder ataca (mill 2: Hollowmurk Siege + Forest)", k="self", cards=["Hollowmurk Siege", "Forest"], alvos=7, kami=1, scales=0, log=0, nota="NENHUM contador no log depois deste mill"),
 dict(t=7, r="Ruin Crab: Forest entra (Shredder) e cada oponente milla 3", k="opp", n_opp=3, cada=3, alvos=7, kami=1, scales=0, log=0, nota="nao esta no log"),
 dict(t=7, r="Memory Erosion: o oponente simulado conjura Evacuation (milla 2); resolve ANTES da Evacuation", k="opp", n_opp=1, cada=2, alvos=5, kami=1, scales=1, log=0, nota="Scales ja' em campo (retrace); contadores iriam para criaturas que a Evacuation devolve em seguida"),
 dict(t=8, r="landfall do Icetill (Urza's Saga do cemiterio): Palantir milado", k="self", cards=["Palantír of Orthanc"], alvos=3, kami=0, scales=1, log=0, nota="Kami esta na mao (devolvido pela Evacuation); NENHUM contador no log"),
 dict(t=8, r="Ruin Crab: Urza's Saga entra e cada oponente milla 3", k="opp", n_opp=3, cada=3, alvos=3, kami=0, scales=1, log=0, nota="nao esta no log"),
]
# conferencias contra o log
for e in EV:
    if e["k"] == "self":
        for c in e["cards"]:
            assert c in milled[e["t"]], (e["t"], c)
for t_ in range(1, len(T) + 1):
    soma = sum(e["log"] for e in EV if e["t"] == t_)
    assert soma == inc[t_], f"T{t_}: atribuicao minha {soma} != contadores no log {inc[t_]}"
assert sum(inc.values()) > 0

rng = random.Random(20261006)
def mc_X(n_opp, cada, N=200000):
    xs = []
    for _ in range(N):
        xs.append(sum(1 for _ in range(n_opp * cada) if rng.random() < P_NONLAND))
    return xs

def contadores(X, alvos, kami, scales):
    return min(X, alvos) * (1 + kami + scales)

print("# Ledger da partida manual do Mothman (2026-10-06)\n")
print("Leitura minha do trace (`resumos/trace.md`); cada atribuicao de contadores por evento foi conferida por `assert` contra os contadores do log por turno. **Limites:** o log nao registra vida, marcadores de rad, mana flutuante nem a ordem da pilha.\n")

# ---------- (1) mill meu ----------
print("## 1. Mill meu: fontes que as regras exigem x cartas milladas no log\n")
print("| T | no log (cartas milladas) | fontes esperadas | esperado (min) | diferenca |")
print("|---|---|---|---|---|")
FONTES = {
 3: ("Six ataca (3)", 3), 4: ("Six ataca (3)", 3),
 5: ("rad (>= 1: Mothman entrou no T4) + landfall do Icetill (Swamp do cemiterio) (1)", 2),
 6: ("rad (>= 1: ataque do Mothman no T5 deu +1) + landfall do Icetill (Overgrown Tomb) + Hedge Shredder ataca (2)", 4),
 7: ("landfall do Icetill (Forest posta pelo Shredder) + Hedge Shredder ataca (2) + rad (0 a 2, depende dos mills do T6)", 3),
 8: ("landfall do Icetill (Urza's Saga) + rad (>= 1: o ataque do Mothman no T7 deu +1 e a Evacuation nao tira marcador de rad)", 2),
 9: ("rad (>= 1: o ETB do Mothman no T8 deu +1; nenhum terreno entrou)", 1),
}
tot_log = tot_esp = 0
for t_ in range(1, len(T) + 1):
    n = len(milled[t_])
    if t_ in FONTES:
        f, esp = FONTES[t_]
        print(f"| T{t_} | {n} ({', '.join(milled[t_])}) | {f} | {'>= ' if t_ in (5, 6, 8, 9) else ''}{esp} | {'**faltam >= %d**' % (esp - n) if esp > n else ('ok' if esp == n else f'+{n - esp}')} |")
        tot_log += n; tot_esp += esp
    else:
        print(f"| T{t_} | {n} | nenhuma | 0 | ok |")
print(f"\nTotal T3-T9: **{tot_log} no log x >= {tot_esp} esperadas**. T5 bate (o usuario contou rad E landfall: 2 cartas). **T6 e T8 ficam abaixo, e e' limite inferior firme** (T6: o ataque do Mothman no T5 garante rad >= 1; T8: o ataque do T7 garante rad >= 1): "
      "falta pelo menos 1 mill meu em cada um, rad ou landfall do Icetill (a posicao das cartas no log nao permite dizer qual). T7 bate so' se o rad estava em 0 (depende de quais cartas o mill do rad do T6 tirou).\n")

# ---------- (2)+(3) contadores ----------
print("## 2. Contadores +1/+1: regras x log (com Kami e Hardened Scales)\n")
print("Regra: cada gatilho do Mothman poe um contador em ate X criaturas-alvo (X = nao-terrenos milados); o Kami (e o Scales, quando em campo) somam +1 a CADA colocacao, inclusive no proprio Kami.")
print("`esperado` = min(X, alvos) x (1 + Kami + Scales). Para mill de oponente, X vem de Monte Carlo (200.000 amostras, 62 nao-terrenos em 99).\n")
print("| T | evento | X (nao-terrenos) | alvos | Kami / Scales | contadores esperados | no log | observacao |")
print("|---|---|---|---|---|---|---|---|")
tot_esp_c = tot_log_c = 0.0
tot_unlogged_opp = 0.0
res_opp = []
for e in EV:
    if e["k"] == "self":
        X = sum(1 for c in e["cards"] if not is_land(c))
        esp = contadores(X, e["alvos"], e["kami"], e["scales"]) if X else 0
        xs = f"{X}"
    elif e["k"] == "support":
        X = e["n"]
        esp = contadores(X, e["alvos"], e["kami"], e["scales"])
        xs = f"{X} (support)"
    else:
        xs_list = mc_X(e["n_opp"], e["cada"])
        esp_list = [contadores(x, e["alvos"], e["kami"], e["scales"]) for x in xs_list]
        X = st.mean(xs_list); esp = st.mean(esp_list)
        p0 = sum(1 for x in xs_list if x == 0) / len(xs_list)
        xs = f"{X:.2f} medio (P(X=0) = {100 * p0:.1f}%)"
        res_opp.append((e["t"], e["r"], e["n_opp"] * e["cada"], X, esp))
        tot_unlogged_opp += esp
    tot_esp_c += esp; tot_log_c += e["log"]
    print(f"| T{e['t']} | {e['r']} | {xs} | {e['alvos']} | {e['kami']} / {e['scales']} | {esp:.1f} | {e['log']} | {e['nota']} |")
print(f"\n**Total: {tot_log_c:.0f} contadores no log x {tot_esp_c:.1f} esperados pelas regras.** Desta diferenca, {tot_unlogged_opp:.1f} vem dos eventos de mill de OPONENTE (que o log nao registra: o usuario ja' avisou); o resto "
      f"({tot_esp_c - tot_unlogged_opp - tot_log_c:.1f}) sao colocacoes que o log mostra **sem** a substituicao do Kami / sem o gatilho.\n")

# so' o que o log permite provar (sem mill de oponente)
prova = [e for e in EV if e["k"] != "opp"]
esp_p = sum((contadores(sum(1 for c in e["cards"] if not is_land(c)), e["alvos"], e["kami"], e["scales"]) if e["k"] == "self" else contadores(e["n"], e["alvos"], e["kami"], e["scales"])) for e in prova)
print("### O que o log PROVA sozinho (so' mill meu e Patron; zero dependencia do mill de oponente)\n")
print(f"- {len(prova)} eventos; contadores exigidos pelas regras: **{esp_p}**; postos no log: **{sum(e['log'] for e in prova)}**.")
kami_placements = sum(e["log"] for e in prova if e["kami"])
print(f"- Colocacoes feitas com o Kami em campo: **{kami_placements}** (T5: 1, T6: 3, T7: 3); em todas o log mostra +1 onde a regra manda +2 (Kami). Diferenca so' do Kami: {kami_placements} contadores.")
print("- Gatilhos do Mothman por mill MEU **sem nenhum contador no log**: T4 (X = 2), T7 (Hollowmurk Siege, X = 1) e T8 (Palantir, X = 1).\n")

# ---------- (3) mill de oponente ----------
print("## 3. Mill de oponente reconstruido (o log nao o contem)\n")
print("| T | fonte | cartas milladas (todos os oponentes) | nao-terrenos esperados |")
print("|---|---|---|---|")
tc = tn = 0
for t_, r, cards, X, esp in res_opp:
    print(f"| T{t_} | {r} | {cards} | {X:.1f} |"); tc += cards; tn += X
print(f"| | **total** | **{tc}** | **{tn:.1f}** |")
print("\nO log nao mostra essas cartas nem os 4 gatilhos extras do Mothman. Cada gatilho do Ruin Crab milla 3 de CADA oponente (3 oponentes) e dispara o Mothman uma vez.\n")

# ---------- (4) jogadas de terreno ----------
print("## 4. Jogadas de terreno (Icetill Explorer: +1 jogada e terrenos do cemiterio) x Ruin Crab em campo\n")
print("| T | jogadas disponiveis | usadas (mao / cemiterio) | Ruin Crab em campo na hora | terrenos disponiveis nao jogados | gatilhos do Crab perdidos |")
print("|---|---|---|---|---|---|")
LINHAS = [
 (1, 1, "1 (Misty)", "nao", "(todas usadas)", 0), (2, 1, "1 (Strip Mine)", "nao", "(todas usadas)", 0), (3, 1, "1 (Watery Grave)", "nao", "(todas usadas)", 0), (4, 1, "1 (Island)", "nao", "(todas usadas)", 0),
 (5, 2, "2 (Forest da mao; Swamp do cemiterio)", "nao", "(todas usadas)", 0),
 (6, 2, "1 (Overgrown Tomb)", "so' depois (retrace do Crab)", "Takenuma (mao); Misty, Waterlogged Grove, Urza's Saga (cemiterio)", 1),
 (7, 2, "0 (a Forest veio do Shredder: nao e' jogada)", "sim", "Takenuma (mao); Misty, Waterlogged Grove, Urza's Saga (cemiterio)", 2),
 (8, 2, "1 (Urza's Saga do cemiterio)", "sim (recem-conjurado)", "Agadeem (MDFC, mao); Misty, Waterlogged Grove, Takenuma (cemiterio)", 1),
 (9, 2, "0 ate o fim do log (o log termina apos o ataque)", "sim", "Agadeem (mao); Misty, Waterlogged Grove, Takenuma, Polluted Delta (cemiterio)", 2)]
perd = 0
for t_, disp, usadas, crab, nao, p in LINHAS:
    print(f"| T{t_} | {disp} | {usadas} | {crab} | {nao} | {p} |"); perd += p
print(f"\nGatilhos do Ruin Crab que **ocorreram** na partida (reconstruidos): 2 (T7, T8). Perdidos por jogada de terreno nao usada com o Crab em campo: **{perd}** (T6-T9; no T9 o log para antes da fase principal 2). "
      "Cada um valeria 9 cartas milladas e 1 gatilho do Mothman, alem de 1 mill meu do Icetill; jogar a Misty do cemiterio e quebra-la ainda somaria 1 landfall extra (a Misty entra, depois o terreno buscado entra).")

# ---------- (5) ataques que nao aconteceram ----------
print("\n## 5. Six em campo e desvirada que nao atacou\n")
SIX = [(5, "desvirou no inicio; so' o Mothman virou (ataque)"), (6, "desvirada o turno inteiro (Hedge Shredder atacou, tripulado pelo Icetill)"), (7, "com 1 contador; so' Mothman e Shredder atacaram")]
for t_, nota in SIX:
    atk = any(e["name"] == "Six" and e["id"] and not e.get("fromZone") and e["tapped"] for e in T[t_ - 1])
    assert not atk, f"T{t_}: o log mostra a Six virada"
    print(f"- T{t_}: {nota}.")
print("\nCada ataque da Six = 1 evento de mill meu de 3 cartas (gatilho do Mothman com X = nao-terrenos), mais 1 terreno para a mao; com o Hedge Shredder em campo, terreno milado ainda entra em campo (landfall do Crab/Icetill). "
      "Foram 3 turnos (T5-T7) sem esse ataque. **Nao e' erro de regra** (atacar e' escolha); fica como pergunta ao usuario.")
