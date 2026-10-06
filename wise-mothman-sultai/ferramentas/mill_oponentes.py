#!/usr/bin/env python3
"""Ferramenta: efeito do MILL nos oponentes (The Wise Mothman). Roda o simulador `mothman_goldfish_v1.py` (3 oponentes passivos com biblioteca/vida/rad reais) e mostra:
  1. por TURNO: cartas milladas das bibliotecas dos oponentes, % da biblioteca deles ja' milada, biblioteca restante, partidas com algum oponente fora por biblioteca vazia;
  2. por FONTE: de onde vem cada carta milada (rad, Ruin Crab, Altar of the Brood, Mesmeric Orb, Memory Erosion, Psychic Corrosion, Zellix, Ashiok, Mindcrank, ...);
  3. o que o mill RENDE: gatilhos do Mothman por mill de oponente, contadores, vida perdida por rad, fichas, pings de Konrad, como os oponentes saem;
  4. com 2+ variantes: diferenca PAREADA (mesma semente) da primeira (referencia) para cada outra, com IC95%.
Uso (de qualquer pasta):
  python3 ferramentas/mill_oponentes.py                                   # lista atual, 3.000 partidas, modo padrao
  python3 ferramentas/mill_oponentes.py -n 5000 --modo resiliencia
  python3 ferramentas/mill_oponentes.py -v base -v pacote5 -v "meu:Negate=>The Master of Lake-town,Strip Mine=>Bruvac the Grandiloquent"
  python3 ferramentas/mill_oponentes.py -v base -v "sem_kozilek:flag:KOZILEK_SHUFFLE_ENABLED=false"
Variante = `nome` (predefinida) ou `nome:Sai=>Entra,Sai2=>Entra2` e/ou `flag:NOME=valor` (valor json). Predefinidas: `base`, `pacote5`, `pacote5+master`, `master_negate`, `bruvac`, `sem_kozilek`.
Premissas: oponentes passivos (sem tabuleiro), biblioteca de 99 por TIPO (37 terrenos/28 criaturas/34 outras), compram 1 por turno; so' o que o deck faz neles e' simulado.
Auto-verificacao: as primeiras sementes sao comparadas campo a campo com `simulate_one` (o laco da ferramenta reproduz o do simulador)."""
import argparse, collections, importlib.util, json, math, multiprocessing as mp, os, random, statistics as st, sys

DECK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIM = os.path.join(DECK, "mothman_goldfish_v1.py")
PACOTE5 = [["Cold-Eyed Selkie", "Evolution Sage"], ["Swarmyard", "Karn's Bastion"], ["Soul-Guide Lantern", "Bruvac the Grandiloquent"],
           ["An Offer You Can't Refuse", "Garruk's Uprising"], ["Bojuka Bog", "Opulent Palace"]]
PRESETS = {"base": {}, "pacote5": {"SWAPS": PACOTE5}, "pacote5+master": {"SWAPS": PACOTE5 + [["Negate", "The Master of Lake-town"]]},
           "master_negate": {"SWAPS": [["Negate", "The Master of Lake-town"]]}, "bruvac": {"SWAPS": [["Soul-Guide Lantern", "Bruvac the Grandiloquent"]]},
           "sem_kozilek": {"KOZILEK_SHUFFLE_ENABLED": False}}
CARTA_DA_FONTE = {"mindcrank": "Mindcrank", "altar_of_the_brood": "Altar of the Brood", "ruin_crab": "Ruin Crab", "psychic_corrosion": "Psychic Corrosion", "mesmeric_orb": "Mesmeric Orb",
                  "memory_erosion": "Memory Erosion", "zellix": "Zellix, Sanity Flayer", "ashiok": "Ashiok, Dream Render", "deepmuck": "Deepmuck Desperado",
                  "altar_of_dementia": "Altar of Dementia", "konrad": "Syr Konrad, the Grim", "undead_alchemist": "Undead Alchemist",
                  "master_of_lake_town": "The Master of Lake-town"}
FONTES = {"rad": "rad counters do oponente (CR 728.1, no main dele)", "ruin_crab": "Ruin Crab (landfall: 3 em cada oponente)", "altar_of_the_brood": "Altar of the Brood (1 por permanente que entra)",
          "mesmeric_orb": "Mesmeric Orb (1 por permanente DELE que desvira)", "memory_erosion": "Memory Erosion (2 por magia dele)", "psychic_corrosion": "Psychic Corrosion (2 por compra minha)",
          "zellix": "Zellix ({1},{T}: 3)", "ashiok": "Ashiok (-1: 4)", "deepmuck": "Deepmuck Desperado (crime: 3 em cada)", "mindcrank": "Mindcrank (vida perdida -> mill)",
          "altar_of_dementia": "Altar of Dementia (poder da criatura sacrificada)", "konrad": "Syr Konrad ({1}{B}: cada jogador 1)", "undead_alchemist": "Undead Alchemist (dano de Zumbi vira mill)",
          "didnt_say_please": "Didn't Say Please (3 no dono da magia)",
          "ascension_loop": "combo Ascension + Mindcrank/Master: mila a biblioteca inteira do oponente (loop; nao passa por mill_event)", "master_of_lake_town": "The Master of Lake-town (vida perdida -> mill)", "palantir": "-", "angel_of_suffering": "-"}


def carrega(flags):
    spec = importlib.util.spec_from_file_location("mm_tool_%d" % os.getpid(), SIM)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    for k, v in flags.items():
        if not hasattr(m, k):
            raise AttributeError(f"{k} nao existe no simulador")
        setattr(m, k, v)
    return m


def rodar(m, seed, turns, resil):
    """Mesmo laco de `simulate_one`/`simulate_one_with_interaction`, amostrando o estado dos oponentes ao fim de cada rodada."""
    state = m.new_state(seed)
    if resil:
        state.interaction_rng = random.Random(seed + 999_999)
    snaps = []
    prev_src = collections.Counter()
    prev_cards = 0
    for _ in range(turns):
        m.play_turn(state)
        if not state.game_over:
            if resil:
                state.wiped_this_round = False
            for o in list(state.opps):
                if o.eliminated:
                    continue
                m.opponent_turn(state, o)
                if state.game_over:
                    break
                if resil:
                    m.try_smart_opponent_turn(state)
                    if state.game_over:
                        break
        cur = collections.Counter(state.opp_mill_by_source)
        snaps.append({"t": state.turn, "milled": state.cards_milled_opp_total - prev_cards,
                      "src": {k: cur[k] - prev_src.get(k, 0) for k in cur if cur[k] - prev_src.get(k, 0)},
                      "lib": [None if o.eliminated else len(o.library) for o in state.opps],
                      "elim_decked": sum(1 for o in state.opps if o.eliminated and o.elim_reason == "decked")})
        prev_src = cur
        prev_cards = state.cards_milled_opp_total
        if state.game_over:
            break
    m.finalize(state)
    return state, snaps


def trabalho(args):
    flags, seeds, turns, resil = args
    m = carrega(flags)
    out = []
    for sd in seeds:
        state, snaps = rodar(m, sd, turns, resil)
        num = {k: (float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else float(v) if isinstance(v, bool) else None) for k, v in vars(state).items()}
        num = {k: v for k, v in num.items() if v is not None}
        out.append({"seed": sd, "snaps": snaps, "num": num, "src_total": dict(state.opp_mill_by_source), "casts": dict(state.casts_by_card), "decked_opps": sum(1 for o in state.opps if o.elim_reason == "decked"),
                    "elim": [o.elim_reason or "vivo" for o in state.opps]})
    return out


def parse_variante(txt):
    nome, flags = txt, {}
    if txt in PRESETS:
        return txt, dict(PRESETS[txt])
    if ":" in txt:
        nome, resto = txt.split(":", 1)
        for parte in resto.split(":flag:"):
            parte = parte.strip()
            if parte.startswith("flag:"):
                parte = parte[5:]
                k, v = parte.split("=", 1)
                flags[k] = json.loads(v)
            elif "=>" in parte:
                flags["SWAPS"] = [p.split("=>") for p in parte.split(",") if p]
            elif parte.startswith("flag"):
                pass
        if nome in PRESETS and not flags:
            return nome, dict(PRESETS[nome])
        return nome, flags
    raise SystemExit(f"variante desconhecida: {txt} (predefinidas: {', '.join(PRESETS)})")


def ic(a, b):
    d = [y - x for x, y in zip(a, b)]
    if len(d) < 2 or len(set(d)) == 1:
        return (st.mean(d) if d else 0.0), 0.0
    return st.mean(d), 1.96 * st.stdev(d) / math.sqrt(len(d))


def autoverifica(flags, turns, resil, k=8):
    m = carrega(flags)
    fn = m.simulate_one_with_interaction if resil else m.simulate_one
    n_ok = 0
    for sd in range(7_000_000, 7_000_000 + k):
        a, _ = rodar(m, sd, turns, resil)
        b = fn(sd, turns)
        for f in ("turn", "cards_milled_opp_total", "cards_milled_self_total", "mothman_triggers_total", "opps_eliminated_total", "draws_total", "life"):
            assert getattr(a, f) == getattr(b, f), f"laco da ferramenta diverge do simulador em {f} (semente {sd})"
        assert dict(a.opp_mill_by_source) == dict(b.opp_mill_by_source)
        n_ok += 1
    assert n_ok > 0
    return n_ok


def resumo(nome, res, turns, resil):
    N = len(res)
    L = []
    L.append(f"\n{'=' * 100}\nVARIANTE `{nome}`: N={N} partidas, modo {'resiliencia' if resil else 'padrao'}, {turns} turnos\n{'=' * 100}")
    # 1. por turno
    L.append("\n1) POR TURNO (media sobre as N partidas; partida encerrada conta 0 mill nos turnos seguintes)")
    L.append("%4s %14s %16s %18s %22s %24s" % ("T", "cartas milladas", "acumulado/oponente", "% da biblioteca", "biblioteca media do", "oponentes fora por"))
    L.append("%4s %14s %16s %18s %22s %24s" % ("", "(3 oponentes)", "(media)", "dos oponentes", "oponente vivo", "biblioteca vazia (acum.)"))
    cum = 0.0
    for t in range(1, turns + 1):
        milled = [next((s["milled"] for s in r["snaps"] if s["t"] == t), 0) for r in res]
        cum += st.mean(milled)
        libs = [x for r in res for s in r["snaps"] if s["t"] == t for x in s["lib"] if x is not None]
        dk = [next((s["elim_decked"] for s in r["snaps"] if s["t"] == t), r["snaps"][-1]["elim_decked"] if r["snaps"] else 0) for r in res]
        L.append("%4d %14.2f %16.1f %17.1f%% %22.1f %24.3f" % (t, st.mean(milled), cum / 3, 100 * cum / (3 * 92), st.mean(libs) if libs else 0.0, st.mean(dk)))
    # 2. por fonte
    L.append("\n2) POR FONTE: cartas milladas das bibliotecas dos oponentes por partida")
    tot = collections.Counter()
    for r in res:
        tot.update(r["src_total"])
        # o loop do combo Ascension + Mindcrank/Master mila a biblioteca inteira de uma vez, fora de `mill_event` (nao entra em opp_mill_by_source): o residuo so' pode vir dele
        sem_fonte = r["num"]["cards_milled_opp_total"] - sum(r["src_total"].values())
        assert sem_fonte >= 0 and (sem_fonte == 0 or r["num"].get("ascension_loops", 0) > 0), f"mill sem fonte fora do combo Ascension (semente {r['seed']})"
        if sem_fonte:
            tot["ascension_loop"] += sem_fonte
    soma = sum(tot.values()) or 1
    assert abs(soma / N - st.mean(r["num"]["cards_milled_opp_total"] for r in res)) < 1e-9 and soma > 0, "a soma das fontes nao fecha com o total de cartas milladas"
    L.append("%-22s %12s %8s %14s %20s   %s" % ("fonte", "cartas/jogo", "%", "conjurada em", "cartas/jogo QUANDO", "o que e'"))
    L.append("%-22s %12s %8s %14s %20s" % ("", "(todas)", "", "(% das partidas)", "a carta foi conjurada"))
    for k, v in sorted(tot.items(), key=lambda kv: -kv[1]):
        carta = CARTA_DA_FONTE.get(k)
        if carta:
            com = [r for r in res if r["casts"].get(carta, 0) > 0]
            cond = (sum(r["src_total"].get(k, 0) for r in com) / len(com)) if com else float("nan")
            L.append("%-22s %12.2f %7.1f%% %13.1f%% %20.2f   %s" % (k, v / N, 100 * v / soma, 100 * len(com) / N, cond, FONTES.get(k, "")))
        else:
            L.append("%-22s %12.2f %7.1f%% %14s %20s   %s" % (k, v / N, 100 * v / soma, "(sem carta)", "-", FONTES.get(k, "")))
    L.append("%-22s %12.2f" % ("TOTAL", soma / N))
    L.append("   (a coluna 'QUANDO' mistura o efeito da carta com o resto do deck: uma partida em que ela sai tende a ser uma partida em que o motor inteiro girou)")
    # 3. o que rende
    L.append("\n3) O QUE O MILL RENDE (media por partida)")
    mean = lambda f: st.mean(r["num"].get(f, 0.0) for r in res)
    for rot, f in (("cartas milladas dos oponentes", "cards_milled_opp_total"), ("... das quais NAO-terreno (alimentam o Mothman)", "nonland_milled_opp_total"),
                   ("gatilhos do Mothman por mill de oponente", "mothman_trigger_opp_mill"), ("contadores +1/+1 postos pelo Mothman", "mothman_counters_placed_total"),
                   ("rad counters dados aos oponentes", "rad_counters_given_opp_total"), ("vida que os oponentes perdem por rad", "rad_life_lost_opp_total"),
                   ("fichas Horror/Zumbi (Zellix/Alchemist)", "tokens_created"), ("pings do Syr Konrad", "konrad_pings_total"),
                   ("crimes (Deepmuck/Freestrider)", "crimes_total"), ("oponentes eliminados", "opps_eliminated_total"), ("... por biblioteca vazia", "opps_decked_total"),
                   ("... por perda de vida", "opps_burned_total"), ("... por dano de comandante", "opps_cmd_total")):
        L.append("   %-52s %8.3f" % (rot, mean(f)))
    L.append("   %-52s %8.2f%%" % ("partidas em que pelo menos 1 oponente sai por biblioteca vazia", 100 * sum(1 for r in res if r["decked_opps"] > 0) / N))
    L.append("   %-52s %8.2f%%" % ("partidas com a mesa inteira limpa ate T8", 100 * mean("cleared_T8")))
    L.append("   %-52s %8.2f%%" % ("partidas com a mesa inteira limpa ate T10", 100 * mean("cleared_T10")))
    return "\n".join(L)


def comparacao(base_nome, base, nome, var):
    campos = ["cards_milled_opp_total", "nonland_milled_opp_total", "mothman_trigger_opp_mill", "mothman_counters_placed_total", "rad_life_lost_opp_total", "opps_decked_total",
              "opps_eliminated_total", "cleared_T7", "cleared_T8", "cleared_T10", "first_elim_T6", "self_lost", "cards_milled_self_total"]
    L = [f"\nDIFERENCA PAREADA `{nome}` - `{base_nome}` (mesma semente; IC95%; * = |dif| > IC)"]
    for c in campos:
        m_, h = ic([r["num"].get(c, 0.0) for r in base], [r["num"].get(c, 0.0) for r in var])
        L.append("   %-34s base %9.4f   dif %+9.4f ± %-8.4f %s" % (c, st.mean(r["num"].get(c, 0.0) for r in base), m_, h, "*" if abs(m_) > h else " "))
    fb, fv = collections.Counter(), collections.Counter()
    for rs, f in ((base, fb), (var, fv)):
        for r in rs:
            f.update(r["src_total"])
            f["ascension_loop"] += r["num"]["cards_milled_opp_total"] - sum(r["src_total"].values())
    L.append("   por fonte (cartas/jogo, dif): " + "; ".join(f"{k} {(fv[k] - fb[k]) / len(base):+.2f}" for k in sorted(set(fb) | set(fv), key=lambda k: (-abs(fv[k] - fb[k]), k)) if abs(fv[k] - fb[k]) / len(base) >= 0.05))
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-n", type=int, default=3000, help="partidas por variante (padrao 3000)")
    ap.add_argument("--modo", choices=["padrao", "resiliencia"], default="padrao")
    ap.add_argument("--turnos", type=int, default=12)
    ap.add_argument("--semente0", type=int, default=3_000_000)
    ap.add_argument("-v", "--variante", action="append", help="variante (repetivel); a 1a e' a referencia. padrao: base")
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("-o", "--saida", help="grava o texto neste arquivo alem de imprimir")
    ap.add_argument("--bruto", help="grava o bruto por partida (json comprimido .xz) para auditoria")
    ap.add_argument("--do-bruto", help="NAO simula: refaz o texto so' a partir de um bruto gravado por --bruto (sem as linhas de auto-verificacao, que exigem o simulador)")
    a = ap.parse_args()
    if a.do_bruto:
        import lzma
        d = json.load(lzma.open(a.do_bruto, "rt"))
        resil, turns = d["modo"] == "resiliencia", d["turnos"]
        nomes = list(d["variantes"])
        res = {n: d["variantes"][n]["partidas"] for n in nomes}
        assert all(len(v) > 0 for v in res.values())
        out = [f"Ferramenta mill_oponentes: {len(nomes)} variante(s), N={d['n']}, sementes {d['semente0']}..{d['semente0'] + d['n'] - 1}, modo {d['modo']}"]
        for n in nomes:
            out.append(resumo(n, res[n], turns, resil))
        for n in nomes[1:]:
            out.append(comparacao(nomes[0], res[nomes[0]], n, res[n]))
        txt = "\n".join(out)
        print(txt)
        if a.saida:
            open(a.saida, "w").write(txt + "\n")
        return
    resil = a.modo == "resiliencia"
    vs = [parse_variante(v) for v in (a.variante or ["base"])]
    out = [f"Ferramenta mill_oponentes: {len(vs)} variante(s), N={a.n}, sementes {a.semente0}..{a.semente0 + a.n - 1}, modo {a.modo}"]
    resultados = {}
    for nome, flags in vs:
        k = autoverifica(flags, a.turnos, resil)
        out.append(f"auto-verificacao `{nome}`: {k} sementes identicas ao simulador (> 0)")
        seeds = list(range(a.semente0, a.semente0 + a.n))
        blocos = [seeds[i::a.procs * 4] for i in range(a.procs * 4)]
        with mp.Pool(a.procs) as p:
            partes = p.map(trabalho, [(flags, b, a.turnos, resil) for b in blocos])
        res = sorted([r for pt in partes for r in pt], key=lambda r: r["seed"])
        resultados[nome] = res
        out.append(resumo(nome, res, a.turnos, resil))
    nomes = [n for n, _ in vs]
    for n in nomes[1:]:
        out.append(comparacao(nomes[0], resultados[nomes[0]], n, resultados[n]))
    txt = "\n".join(out)
    print(txt)
    if a.bruto:
        import lzma
        with lzma.open(a.bruto, "wt", preset=9) as f:
            json.dump({"modo": a.modo, "turnos": a.turnos, "semente0": a.semente0, "n": a.n, "variantes": {n: {"flags": dict(vs)[n], "partidas": resultados[n]} for n in nomes}}, f, separators=(",", ":"))
    if a.saida:
        open(a.saida, "w").write(txt + "\n")


if __name__ == "__main__":
    main()
