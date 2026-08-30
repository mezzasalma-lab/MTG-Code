"""
Mede a mana incolor {C} DE VERDADE disponivel turno a turno no deck da
Ulalek, separada do pool generico/fungivel que o simulador principal usa
pra tudo o mais. Pergunta do usuario (2026-08-30), depois de reportar que
"nao sobrava mana pra ativar o Strionic Resonator" em jogo real: o aperto
de {C} e' sistematico do deck, ou so' de maos especificas?

Usa a instrumentacao nova adicionada em `ulalek_goldfish_v1.py`
(`true_colorless_capacity()`, `state.true_c_capacity_samples`,
`state.ulalek_cc_payments_safe/risky/declined_but_had_true_c`) - ver os
comentarios la pra metodologia completa. Resumo: o modelo principal so
sabe "quanto mana total sobra", nao de qual fonte especifica ela veio: as
metricas aqui sao uma medida PARALELA e aproximada (teto otimista de {C}
real em campo, independente de quanto ja foi "gasto" genericamente nesse
turno), nao uma reescrita completa do modelo de mana pip a pip.
"""

import statistics

import ulalek_goldfish_v1 as sim


def avg(vals):
    return sum(vals) / len(vals) if vals else 0.0


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    N = 10000
    SEED_BASE = 7100000
    TURNS = 8

    states = [sim.simulate_one(SEED_BASE + i, turns=TURNS) for i in range(N)]

    print(f"n={N}, seed_base={SEED_BASE}, turns={TURNS}")
    print()

    # --- curva turno a turno: capacidade real de {C} vs mana total ---
    print("--- Mana {C} real disponivel vs. mana total, por turno (inicio da fase principal) ---")
    print(f"{'Turno':>6} | {'Avg true-C':>11} | {'Avg mana total':>15} | {'% do total que e true-C':>24} | {'% turnos com true-C < 2':>24}")
    for t in range(TURNS):
        true_c_vals = [s.true_c_capacity_samples[t] for s in states if len(s.true_c_capacity_samples) > t]
        total_vals = [s.total_mana_samples[t] for s in states if len(s.total_mana_samples) > t]
        avg_true_c = avg(true_c_vals)
        avg_total = avg(total_vals)
        pct = 100 * avg_true_c / avg_total if avg_total else 0.0
        pct_below2 = 100 * sum(1 for v in true_c_vals if v < 2) / len(true_c_vals) if true_c_vals else 0.0
        print(f"{t+1:>6} | {avg_true_c:>11.2f} | {avg_total:>15.2f} | {pct:>23.1f}% | {pct_below2:>23.1f}%")
    print()

    # --- pagamentos do CC da Ulalek: seguro vs arriscado vs recusado-mas-podia ---
    safe = sum(s.ulalek_cc_payments_safe for s in states)
    risky = sum(s.ulalek_cc_payments_risky for s in states)
    declined_but_had = sum(s.ulalek_cc_declined_but_had_true_c for s in states)
    total_paid = safe + risky

    print("--- Pagamentos do {C}{C} da Ulalek (todas as partidas, todos os turnos) ---")
    print(f"Total de vezes que o modelo PAGOU (mana generica total >= 2): {total_paid} ({avg([s.ulalek_copies_total for s in states]):.3f}/partida)")
    print(f"  -> 'seguro' (capacidade real de {{C}} tambem >= 2 no momento): {safe} ({100*safe/total_paid:.1f}% dos pagamentos)" if total_paid else "  -> n/a")
    print(f"  -> 'arriscado' (capacidade real de {{C}} < 2 - modelo generico permitiu, {{C}}{{C}} de verdade pode nao caber): {risky} ({100*risky/total_paid:.1f}% dos pagamentos)" if total_paid else "  -> n/a")
    print(f"Vezes que o modelo NAO pagou (mana total < 2) mas a capacidade real de {{C}} ja' era >= 2: {declined_but_had} ({avg([s.ulalek_cc_declined_but_had_true_c for s in states]):.3f}/partida)")
    print()
    print("Leitura: 'arriscado' e' o numero que responde a pergunta do usuario -")
    print("quantos dos pagamentos que o simulador (mana generica) considerou legais")
    print("dependeriam, numa mesa real com pips de verdade, de sorte na ordem de quais")
    print("fontes especificas ja tinham sido gastas em outras coisas nesse turno.")
    print()

    # --- mana generica sobrando depois do loop de conjuracao (relevante pra
    # ativacoes tipo Strionic Resonator/Camera, {2} generico, nao {C}{C}) ---
    print("--- Mana generica (qualquer cor) sobrando DEPOIS do loop de conjuracao, por turno ---")
    print("(relevante pra ativar algo tipo Strionic Resonator/Peter Parker's Camera, {2} generico -")
    print(" diferente da pergunta do {C}{C} especifico da Ulalek acima)")
    print(f"{'Turno':>6} | {'Avg mana sobrando':>18} | {'% turnos com 0 sobrando':>24} | {'% turnos com >=2 sobrando':>26}")
    for t in range(TURNS):
        vals = [s.leftover_mana_samples[t] for s in states if len(s.leftover_mana_samples) > t]
        avg_v = avg(vals)
        pct_zero = 100 * sum(1 for v in vals if v == 0) / len(vals) if vals else 0.0
        pct_ge2 = 100 * sum(1 for v in vals if v >= 2) / len(vals) if vals else 0.0
        print(f"{t+1:>6} | {avg_v:>18.2f} | {pct_zero:>23.1f}% | {pct_ge2:>25.1f}%")
