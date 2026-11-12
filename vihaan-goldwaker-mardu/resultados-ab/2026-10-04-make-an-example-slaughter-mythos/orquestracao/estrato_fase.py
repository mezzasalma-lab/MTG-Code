"""Slaughter the Strong e Mythos of Snapdax (e as referencias Act / Blood Money) separadas por FASE: 1a main (antes do combate: os Treasures AINDA nao foram animados pelo Vihaan, entao nao sao criaturas
e nao morrem) x 2a main (depois do combate: os animados sao criaturas ate' o fim do turno). Le o bruto do ensaio a seco da rodada 2026-10-04-wipes-de-sacrificio (so' o MEU lado; 📊 o dos oponentes).
Colunas: perdidas = minhas criaturas/fichas/animados que saem; perm- = TODOS os meus permanentes nao-terreno que saem (negativo = ganhei mais do que perdi); estoqueD = variacao liquida do estoque
de Treasures; dreno = proxy de dano do meu lado; Vihaan† = % dos casos em que o Vihaan morre. Uso: python3 estrato_fase.py [modo: padrao|resiliencia]"""
import json, lzma, os, statistics as st, sys
modo = sys.argv[1] if len(sys.argv) > 1 else "padrao"
raw = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "2026-10-04-wipes-de-sacrificio", "dados", f"raw_dry_run_{modo}_10000.json.xz")
d = json.load(lzma.open(raw, "rt"))
n = len(d["amostras"]["turno"])
fase, mayhem = d["amostras"]["fase"], d["amostras"]["mayhem"]
VAR = ["Blasphemous Act", "Blood Money", "Slaughter the Strong", "Mythos of Snapdax [B+R pagos]", "By Invitation Only [N=motores]", "Blasphemous Edict"]
print(f"Bruto: {raw.split('/')[-1]} | modo={d['modo']} N={d['N']} | {n} estados | so' o MEU lado; castavel = mana E cor; medias por estado onde a carta e' castavel")
for rotulo, sel in (("1a main (antes do combate; sem Treasures animados)", lambda i: fase[i].startswith("1a")),
                    ("2a main (depois do combate; com animados vivos)", lambda i: fase[i].startswith("2a")),
                    ("1a main, com Mayhem Devil em campo", lambda i: fase[i].startswith("1a") and mayhem[i]),
                    ("2a main, com Mayhem Devil em campo", lambda i: fase[i].startswith("2a") and mayhem[i])):
    idx = [i for i in range(n) if sel(i)]
    print(f"\n### {rotulo}: {len(idx)} estados")
    print("%-34s %9s %6s %9s %7s %9s %8s %8s" % ("carta", "castavel", "custo", "perdidas", "perm-", "estoqueD", "dreno", "Vihaan†"))
    for v in VAR:
        r = d["resultados"][v]
        ok = [i for i in idx if r["cast"][i] and r["cor"][i]]
        if not ok:
            print("%-34s %8.1f%%   (nunca)" % (v[:34], 0.0)); continue
        m = lambda k: st.mean(r[k][i] for i in ok)
        print("%-34s %8.1f%% %6.1f %9.2f %7.2f %+9.2f %8.2f %7.1f%%" % (v[:34], 100.0 * len(ok) / len(idx), m("custo"), m("perdidas"), -m("perm"), m("estoque"), m("dreno"), 100.0 * m("vihaan_morre")))
