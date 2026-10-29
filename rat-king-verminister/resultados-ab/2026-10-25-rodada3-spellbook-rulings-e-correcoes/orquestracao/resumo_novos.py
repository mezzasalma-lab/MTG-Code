"""Resumo dos campos NOVOS da Rodada 3 (que o snapshot `antes` nao tem, entao a tabela pareada nao os mostra), SO' a partir dos brutos arquivados (dados/raw_ab_*.json.xz).
Mostra, por variante: media dos contadores novos e, pros combos, P(combo montado ate o turno T) = 1 - media(combo__nunca) e media(combo__ate_Tn).
Uso: python3 -I resumo_novos.py <dados/raw_ab_N[_resiliencia]> ..."""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
NOVOS = ["treasure_mana_used_total", "staff_equips_total", "staff_auto_attach_total", "staff_pings_total", "marrow_staff_loop_iters_total", "extort_paid_total",
         "gray_merchant_drain_total", "ayara_token_triggers_total", "ninja_teen_drain_total", "rotcaller_x_total", "big_apple_activations_total"]
COMBOS = ["combo_marrow_staff_turn", "combo_ayara_plague_turn", "combo_any_turn"]
for base in sys.argv[1:]:
    res = A.carregar_raw(base)
    N = None
    print(f"=== {os.path.basename(base)}")
    for nome, v in res.items():
        if nome == "antes": continue
        campos = {c: [x[1].get(c, 0.0) for x in v] for c in set().union(*(x[1].keys() for x in v))}
        N = len(v)
        m = lambda c: (sum(campos[c]) / len(campos[c])) if c in campos else float("nan")
        linhas = [f"  {k}={m(k):.4f}" for k in NOVOS if k in campos and m(k) != 0]
        for c in COMBOS:
            if c + "__nunca" in campos:
                p = 1 - m(c + "__nunca")
                if p > 0:
                    linhas.append(f"  P({c} montado em 8 turnos)={p*100:.2f}% | ate T3={m(c+'__ate_T3')*100:.2f}% T4={m(c+'__ate_T4')*100:.2f}% T5={m(c+'__ate_T5')*100:.2f}% T6={m(c+'__ate_T6')*100:.2f}%")
        print(f"[{nome}] N={N}" + ("" if linhas else "  (nenhum campo novo diferente de zero)"))
        for l in linhas: print(l)
