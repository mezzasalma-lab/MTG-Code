#!/usr/bin/env python3
"""Resumo da medicao da Muldrotha (le SO' dos brutos em ../dados). Uso: python3 resume_muldrotha.py > ../resumos/muldrotha.md"""
import os, sys, json, statistics as st
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
N = 10000
TIPOS = ("creature", "artifact", "enchantment", "planeswalker")
M = ["cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "opps_eliminated_total", "mothman_counters_placed_total", "cards_milled_opp_total", "self_lost"]
def f(t, pts=False):
    m, h = t
    return ("%+.2f ± %.2f%s" % (100 * m, 100 * h, " *" if abs(m) > h else "")) if pts else ("%+.2f ± %.2f%s" % (m, h, " *" if abs(m) > h else ""))
nomes = json.load(open(os.path.join(ARQ, "dados", "recasts_por_nome.json")))
print("# Muldrotha por partida (lista atual, sem trocas; N = 10.000 por modo, sementes 3.000.000+i, 12 turnos)\n")
print("`base` = Muldrotha normal; `sem_habilidade` = a mesma carta como corpo 6/6 sem a habilidade do cemitério (mesmo baralho, mesma semente). `*` = excede o IC95% pareado.\n")
for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
    res = A.carregar_raw(os.path.join(ARQ, "dados", f"raw_muldrotha_{N}{suf}"))
    a, b = res["base"], res["sem_habilidade"]
    assert len(a) == N and len(b) == N and all("mul_primeiro_turno" in x[1] for x in a), "campo ausente: verificacao vacua"
    entrou = [x[1] for x in a if x[1]["mul_primeiro_turno"] >= 0]
    assert len(entrou) > 0 and sum(x[1]["mul_recasts_total"] for x in a) > 0, "sem Muldrotha em campo ou sem recasts: verificacao vacua"
    assert sum(x[1]["mul_recasts_total"] for x in b) == 0 and sum(x[1]["muldrotha_plays"] for x in b) == 0, "o ensaio sem_habilidade vazou"
    print(f"## Modo {modo}\n")
    print("### Quando ela entra em campo (acumulado, % das partidas)\n")
    print("| até T5 | T6 | T7 | T8 | T10 | T12 |\n|---|---|---|---|---|---|")
    print("| " + " | ".join("%.1f%%" % (100 * sum(1 for x in a if 0 < x[1]["mul_primeiro_turno"] <= T) / N) for T in (5, 6, 7, 8, 10, 12)) + " |\n")
    n = len(entrou)
    mean = lambda k: st.mean(x[k] for x in entrou)
    print(f"### O que ela faz nas {n} partidas ({100 * n / N:.1f}%) em que entra\n")
    print("| métrica | valor |\n|---|---|")
    print("| turnos meus com ela em campo (média) | %.2f |" % mean("mul_turnos_ativa"))
    print("| jogadas do cemitério por partida (terreno + magias) | %.2f |" % mean("muldrotha_plays"))
    print("| ... magias recastadas por partida | %.2f |" % mean("mul_recasts_total"))
    print("| ... terrenos jogados do cemitério por ela | %.2f |" % mean("mul_jogadas_terreno"))
    for t in TIPOS:
        print("| ... recasts de %s | %.2f |" % (t, mean("mul_recasts_" + t)))
    ativ = sum(x["mul_turnos_ativa"] for x in entrou)
    print("| magias recastadas por turno com ela em campo | %.2f |" % (sum(x["mul_recasts_total"] for x in entrou) / ativ))
    print("| partidas com 1+ / 3+ / 5+ recasts (entre as que ela entra) | %.0f%% / %.0f%% / %.0f%% |" % tuple(100 * sum(1 for x in entrou if x["mul_recasts_total"] >= k) / n for k in (1, 3, 5)))
    print("| peças-chave recompradas por partida (lista no script: Henge, Altars, Mindcrank, Orb, Psychic Corrosion, Memory Erosion, Palantír, Scales, Constrictor, Kami, Ruin Crab, Hollowmurk, Danny, Cauldron, Shredder, Ballista, Boots) | %.2f (%.0f%% dos recasts) |" % (mean("mul_recasts_chave"), 100 * sum(x["mul_recasts_chave"] for x in entrou) / sum(x["mul_recasts_total"] for x in entrou)))
    tot = sum(nomes[modo]["base"].values())
    print(f"\n### O que ela recompra (top 12 de {tot} recasts em {N} partidas)\n")
    print("| carta | recasts | % |\n|---|---|---|")
    for nm, k in sorted(nomes[modo]["base"].items(), key=lambda kv: (-kv[1], kv[0]))[:12]:
        print(f"| {nm} | {k} | {100 * k / tot:.1f}% |")
    print("\n### Fontes de recursão no deck (por partida, TODAS as partidas da `base`; o que cada peça devolve ao jogo)\n")
    print("| fonte | por partida |\n|---|---|")
    print("| Muldrotha: magias recastadas (criatura, artefato, encantamento, planeswalker) | %.2f |" % (sum(x[1]["mul_recasts_total"] for x in a) / N))
    print("| Muldrotha: terrenos jogados do cemitério (quando o Icetill não está em campo) | %.2f |" % (sum(x[1]["mul_jogadas_terreno"] for x in a) / N))
    print("| Six: retraces (cada um descarta um terreno) | %.2f |" % (sum(x[1]["six_retraces"] for x in a) / N))
    print("| Icetill Explorer: terrenos jogados do cemitério | %.2f |" % (sum(x[1]["icetill_replays"] for x in a) / N))
    print("| `recursion_events_total` (inclui as linhas acima + Evolution Witness, Takenuma, Agadeem, Woodland...) | %.2f |" % (sum(x[1]["recursion_events_total"] for x in a) / N))
    print("\n### Valor da HABILIDADE (base − sem_habilidade, mesmas sementes; pontos percentuais de partidas, exceto onde indicado)\n")
    print("| amostra | n | mesa limpa T7 | T8 | T10 | 1º oponente fora até T6 | oponentes eliminados (média) | contadores +1/+1 | cartas milladas dos oponentes | eu perco por deck-out |\n|---|---|---|---|---|---|---|---|---|---|")
    def linha(rot, idx):
        aa = [a[i][1] for i in idx]; bb = [b[i][1] for i in idx]
        cel = []
        for c in M:
            t = A.ic([x.get(c, 0.0) for x in bb], [x.get(c, 0.0) for x in aa])
            cel.append(f(t, pts=c in ("cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost")))
        print(f"| {rot} | {len(idx)} | " + " | ".join(cel) + " |")
    todos = list(range(N))
    linha("todas as partidas", todos)
    for T in (6, 8):
        linha(f"ela entra até T{T}", [i for i in todos if 0 < a[i][1]["mul_primeiro_turno"] <= T])
    ident = sum(1 for i in todos if all(abs(a[i][1].get(c, 0.0) - b[i][1].get(c, 0.0)) < 1e-9 for c in M))
    print(f"\nPartidas com todas as métricas acima idênticas entre `base` e `sem_habilidade`: {ident} de {N} ({100 * ident / N:.0f}%).\n")
