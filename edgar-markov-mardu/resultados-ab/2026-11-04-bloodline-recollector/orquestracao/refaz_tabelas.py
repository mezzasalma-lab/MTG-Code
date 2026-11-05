"""Refaz as tabelas ab_*.txt SO' dos brutos arquivados (dados/raw_ab_*.json.xz): a tabela publicada e' funcao so' do bruto (Regra #10, item 4). Uso: python3 -I refaz_tabelas.py <pasta dados/> <pasta de saida>"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
D, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
DEST = ["drain_total", "lifegain_total", "eminence_tokens_created", "death_trigger_events", "welcoming_vampire_draws", "creatures_sacrificed_total", "edgar_attack_counters_total", "commander_cast_turn__ate_T4",
        "commander_cast_turn__ate_T6", "tutors_used_total", "skullclamp_draws", "caretakers_talent_draws", "lands_played_total", "mulligans", "combo_active_turn__ate_T6"]
for N, seed0 in ((2000, 1_000_000), (10000, 3_000_000)):
    for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
        res = A.carregar_raw(os.path.join(D, f"raw_ab_{N}{suf}"))
        txt = [f"LOTE N={N} sementes {seed0}..{seed0 + N - 1}, 8 turnos, modo {modo} (BR = PROXY-PISO: so' o corpo de Vampiro)"]
        for n in res:
            if n != "antes": txt.append(A.tabela_pareada(res["antes"], res[n], DEST, rotulo=f"[{n} - antes]"))
        open(os.path.join(OUT, f"ab_{N}{suf}.txt"), "w").write("\n\n".join(txt) + "\n")
