"""Tabela de ARITMETICA (📊, NAO medida: o simulador nao modela campo de oponente) a partir do bruto do ensaio a seco: para as variantes em que cada oponente sacrifica N criaturas (N fixo ou
escolhido por mim), se CADA um dos 3 oponentes tiver `c` criaturas, ele sacrifica min(N, c); com Mayhem Devil em campo cada uma vale +1 de dano (de qualquer jogador). Compara com o que ESTA
variante tira de MIM (medido). Nada aqui diz qual e' o `c` real das suas mesas: so' mostra como o resultado muda com `c`.
Uso: python3 paridade_oponente.py ../dados/raw_dry_run_padrao_10000.json.xz"""
import json, lzma, statistics as st, sys
d = json.load(lzma.open(sys.argv[1], "rt"))
V = d["variantes"]
n = len(d["amostras"]["turno"])
print(f"Bruto: modo={d['modo']} N={d['N']} sementes {d['S0']}..{d['S0'] + d['N'] - 1}; {n} estados. Cenarios de oponente: cada um dos 3 oponentes com c criaturas (c = 2, 4, 6, 10).")
print("Colunas (por estado onde a variante e' conjuravel por mana E cor): minhas = minhas criaturas/fichas/animados perdidas (MEDIDO); opp = criaturas que os 3 oponentes sacrificam = 3 x min(N, c) (📊);")
print("opp/minhas = razao. Com Mayhem Devil em campo cada criatura sacrificada por um oponente vale +1 de dano (simultaneo: dispara mesmo se ele morrer no evento); com Revel in Riches, +1 Treasure.\n")
for c in (2, 4, 6, 10):
    print(f"### cada oponente com {c} criaturas")
    print("%-47s %8s %8s %8s %12s" % ("variante (so' as que tem N por oponente)", "N medio", "minhas", "opp", "opp/minhas"))
    for v in V:
        r = d["resultados"][v]
        idx = [i for i in range(n) if r["cast"][i] and r["cor"][i] and r["n_opp"][i] is not None]
        if not idx:
            continue
        N = [r["n_opp"][i] for i in idx]
        perd = [r["perdidas"][i] for i in idx]
        opp = [3 * min(x, c) for x in N]
        print("%-47s %8.2f %8.2f %8.2f %12s" % (v[:47], st.mean(N), st.mean(perd), st.mean(opp), ("%.2f" % (st.mean(opp) / st.mean(perd))) if st.mean(perd) > 0.005 else "-"))
    print()
