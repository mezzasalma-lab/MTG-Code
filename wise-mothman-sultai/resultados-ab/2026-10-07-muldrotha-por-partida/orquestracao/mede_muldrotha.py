#!/usr/bin/env python3
"""Muldrotha por partida (pergunta do usuario, 2026-10-07: 'Muldrotha nao e' a melhor recursao do deck?'). Mede, na lista ATUAL (sem trocas), N=10.000 partidas (sementes 3.000.000+i, 12 turnos, modos padrao e
resiliencia): (A) `base`: Muldrotha normal; (B) `sem_habilidade`: a mesma carta como corpo 6/6 SEM a habilidade do cemiterio (o ensaio pre-preenche `muldrotha_used` com todos os tipos apos o upkeep, sem editar o simulador).
A e B tem o mesmo baralho e a mesma semente: partida em que ela nao entra e' IDENTICA (pareamento maximo); a diferenca A - B e' o valor da HABILIDADE. Em A tambem registra, so' no estado REAL (os ensaios
a seco do simulador copiam o estado; contar nas copias inflaria): turno em que entrou, turnos ativa, o que foi rejogado do cemiterio (nome, tipo, turno), jogadas de terreno.
Uso: python3 mede_muldrotha.py   (grava ../dados/*.json.xz)"""
import os, sys
if os.environ.get("PYTHONHASHSEED") != "0":
    os.environ["PYTHONHASHSEED"] = "0"
    os.execv(sys.executable, [sys.executable] + sys.argv)
import json, collections
from multiprocessing import Pool
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import abgen as A
ARQ = os.path.abspath(os.path.join(AQUI, ".."))
DECK = os.path.abspath(os.path.join(ARQ, "..", ".."))
SIM = os.path.join(DECK, "mothman_goldfish_v1.py")
MUL = "Muldrotha, the Gravetide"
TIPOS = ("land", "creature", "artifact", "enchantment", "planeswalker")
# pecas de motor/recompra que importam neste deck (ESCOLHA minha, declarada; a tabela completa de nomes e' arquivada)
CHAVE = ("The Great Henge", "Altar of Dementia", "Altar of the Brood", "Mindcrank", "Mesmeric Orb", "Psychic Corrosion", "Memory Erosion", "Palantír of Orthanc", "Hardened Scales",
         "Winding Constrictor", "Kami of Whispered Hopes", "Ruin Crab", "Hollowmurk Siege", "Danny Pink", "Agatha's Soul Cauldron", "Hedge Shredder", "Walking Ballista", "Swiftfoot Boots")
N = 10000; SEED0 = 3_000_000; TURNS = 12
OUT = os.path.abspath(os.environ.get("MEDIDA_OUT") or ARQ)      # re-execucao da verificacao grava numa pasta temporaria

def bloco(args):
    modo, seeds, desliga, tag = args
    m = A.carrega(SIM, f"mul_{tag}_{modo}_{seeds[0]}", DECK)
    g = {}
    o_play, o_exec, o_up = m.play_turn, m.execute_cast, m.upkeep_step
    def pt(state):
        g["st"] = state
        o_play(state)
        if m.has_perm(state, MUL):
            g["ativa"] += 1
            if g["primeiro"] is None:
                g["primeiro"] = state.turn
    def ex(state, best):
        ok = o_exec(state, best)
        if ok and state is g.get("st") and best[1] == "graveyard:muldrotha":
            g["recasts"].append((best[0], best[2], state.turn))
        return ok
    def up(state):
        o_up(state)
        if desliga:
            state.muldrotha_used = list(TIPOS)          # nenhum tipo livre: a habilidade do cemiterio nao faz nada
    m.play_turn, m.execute_cast, m.upkeep_step = pt, ex, up
    fn = m.simulate_one if modo == "padrao" else m.simulate_one_with_interaction
    out, nomes = [], collections.Counter()
    for sd in seeds:
        g.clear(); g.update(st=None, ativa=0, primeiro=None, recasts=[])
        r = fn(sd, TURNS)
        d = dict(A.numericos(r))
        rc = g["recasts"]
        d["mul_primeiro_turno"] = float(g["primeiro"]) if g["primeiro"] is not None else -1.0
        d["mul_turnos_ativa"] = float(g["ativa"])
        d["mul_recasts_total"] = float(len(rc))
        for t in TIPOS[1:]:
            d["mul_recasts_" + t] = float(sum(1 for _, face, _ in rc if face == t))
        d["mul_recasts_chave"] = float(sum(1 for nm, _, _ in rc if nm in CHAVE))
        d["mul_jogadas_terreno"] = float(r.muldrotha_plays - len(rc))
        for nm, _, _ in rc:
            nomes[nm] += 1
        out.append((A.impressao(r), d))
    return out, dict(nomes)

def roda(modo, desliga, tag):
    seeds = list(range(SEED0, SEED0 + N)); k = 625
    blocos = [(modo, seeds[i:i + k], desliga, tag) for i in range(0, N, k)]
    with Pool(4) as p:
        partes = p.map(bloco, blocos)
    res = [x for part, _ in partes for x in part]
    nomes = collections.Counter()
    for _, n in partes: nomes.update(n)
    return res, nomes

if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "dados"), exist_ok=True)
    nomes_all = {}
    for modo, suf in (("padrao", ""), ("resiliencia", "_resiliencia")):
        a, na = roda(modo, False, "A"); print("feito", modo, "base", flush=True)
        b, nb = roda(modo, True, "B"); print("feito", modo, "sem_habilidade", flush=True)
        A.salvar_raw(os.path.join(OUT, "dados", f"raw_muldrotha_{N}{suf}"), {"base": a, "sem_habilidade": b})
        nomes_all[modo] = {"base": dict(na), "sem_habilidade": dict(nb)}
    json.dump(nomes_all, open(os.path.join(OUT, "dados", "recasts_por_nome.json"), "w"), ensure_ascii=False, indent=1, sort_keys=True)
    print("fim")
