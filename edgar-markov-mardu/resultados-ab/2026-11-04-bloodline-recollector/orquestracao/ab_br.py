"""A/B pareado (mesmas sementes) da Bloodline Recollector no Edgar Markov (2026-11-04). ATENCAO: a carta entra como PROXY-PISO (corpo 2/2 Vampiro: Eminence + Welcoming Vampire), SEM a habilidade
de "preparar" (o simulador nao a exerce: `sac_loop` sacrifica no maximo 2 tokens por turno, ver `medir_mortes_e_potencial.py`). O que o A/B mede e' o CUSTO de cada corte e o valor do CORPO da carta.
Variantes: `antes` = simulador vivo + lista atual; `ctrl_proxy_sem_troca` = arquivo-proxy + lista atual (tem de ser IDENTICO ao `antes`: controle); `BR_por_<X>` = arquivo-proxy com X trocado pela BR NA MESMA POSICAO da lista
(mesma ordem de baralho => pareamento limpo). `Plains`: "4 Plains" vira "1 BR + 3 Plains" na mesma posicao.
Uso: PYTHONHASHSEED=0 python3 -I ab_br.py   (grava dados/raw_ab_*.json.xz e resumos/ab_*.txt)"""
import os, sys, re
os.environ.setdefault("PYTHONHASHSEED", "0")
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, "..")); DECK = os.path.abspath(os.path.join(ARQ, "..", ".."))
OUT = os.path.abspath(os.environ.get("AB_OUT") or ARQ)   # AB_OUT: re-execucao sem sobrescrever o arquivo
os.makedirs(os.path.join(OUT, "dados"), exist_ok=True); os.makedirs(os.path.join(OUT, "resumos"), exist_ok=True)
VIVO = os.path.join(DECK, "edgar_markov_goldfish_v1.py"); PROXY = os.path.join(ARQ, "codigo", "edgar_markov_goldfish_v1_BR_PROXY.py")
BR = "Bloodline Recollector // Ancestral Craving"
m0 = A.carrega(VIVO, "ab_base", DECK); TXT = m0.DECKLIST_TEXT
def troca(x, qtd=1):
    pat = f"{qtd} {x}\n"
    assert TXT.count(pat) == 1, (x, TXT.count(pat))
    return TXT.replace(pat, f"1 {BR}\n" + (f"{qtd-1} {x}\n" if qtd > 1 else ""))
CAND = ["Zulaport Cutthroat", "Vindictive Vampire", "Cordial Vampire", "Funeral Room // Awakening Hall", "Sevinne's Reclamation", "Bloodline Bidding", "Call the Coppercoats", "Charismatic Conqueror", "Spectator Seating"]
VAR = {"antes": (VIVO, {}), "ctrl_proxy_sem_troca": (PROXY, {})}
for x in CAND: VAR["BR_por_" + re.sub(r"[^A-Za-z]+", "_", x).strip("_")] = (PROXY, {"DECKLIST_TEXT": troca(x)})
VAR["BR_por_Plains"] = (PROXY, {"DECKLIST_TEXT": troca("Plains", 4)})
for v, (_, fl) in VAR.items():
    if fl: assert BR in fl["DECKLIST_TEXT"] and len(m0.parse_decklist(fl["DECKLIST_TEXT"])) == 99, v
DEST = ["drain_total", "lifegain_total", "eminence_tokens_created", "death_trigger_events", "welcoming_vampire_draws", "creatures_sacrificed_total", "edgar_attack_counters_total", "commander_cast_turn__ate_T4",
        "commander_cast_turn__ate_T6", "tutors_used_total", "skullclamp_draws", "caretakers_talent_draws", "lands_played_total", "mulligans", "combo_active_turn__ate_T6"]
TURNS = 8
for N, seed0 in ((2000, 1_000_000), (10000, 3_000_000)):
    for modo in ("padrao", "resiliencia"):
        res = {n: A.serie_paralela(c, f"ab_{n}_{modo}_{N}", DECK, fl, modo, range(seed0, seed0 + N), TURNS) for n, (c, fl) in VAR.items()}
        suf = "" if modo == "padrao" else "_resiliencia"
        A.salvar_raw(os.path.join(OUT, "dados", f"raw_ab_{N}{suf}"), res)
        txt = [f"LOTE N={N} sementes {seed0}..{seed0 + N - 1}, {TURNS} turnos, modo {modo} (BR = PROXY-PISO: so' o corpo de Vampiro)"]
        for n in VAR:
            if n != "antes": txt.append(A.tabela_pareada(res["antes"], res[n], DEST, rotulo=f"[{n} - antes]"))
        open(os.path.join(OUT, "resumos", f"ab_{N}{suf}.txt"), "w").write("\n\n".join(txt) + "\n")
        print("ok", N, modo, flush=True)
print("FIM", flush=True)
