"""Bit-identidade das tres remocoes novas (Atomize, Casualties of War, Assassin's Trophy) no simulador do Mothman (Regra #1 de CLAUDE.md).
(1) SWAPS=(): o simulador NOVO (arquivo vivo) == o snapshot `codigo/mothman_goldfish_v1_ANTES.py`, campo a campo (campos atomize_/casualties_/trophy_ ignorados: so' existem no novo), N sementes x 2 modos.
(2) As tres NO baralho (no lugar de Offer / Negate / Didn't Say Please): a partida em que NENHUMA das tres e NENHUMA das tres que sairam e' vista (mao, campo, cemiterio, exilio) e' IDENTICA ao
    ANTES com SWAPS=() (a biblioteca difere so' na identidade das cartas trocadas: `_lib` fora da comparacao). Mostra que a presenca das cartas novas nao muda o jogo quando elas nao aparecem.
Confere que ha > 0 partidas em cada grupo (verificacao vacua e' bug). Uso: python3 bitident_rem.py N [semente0]"""
import importlib.util, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(aqui, "..", "..", ".."))
def load(path, tag):
    os.chdir(DECK)
    spec = importlib.util.spec_from_file_location(tag, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
ANTES = load(os.path.join(aqui, "..", "codigo", "mothman_goldfish_v1_ANTES.py"), "antes")
NOVO = load(os.path.join(DECK, "mothman_goldfish_v1.py"), "novo")
N = int(sys.argv[1]); S0 = int(sys.argv[2]) if len(sys.argv) > 2 else 9_000_000
NOVAS = ["Atomize", "Casualties of War", "Assassin's Trophy"]
OUT = ["An Offer You Can't Refuse", "Negate", "Didn't Say Please"]
IGN = ("atomize_", "casualties_", "trophy_")
def snap(st, lib=True):
    d = {k: v for k, v in vars(st).items() if isinstance(v, (int, float, bool, str, type(None))) and not k.startswith(IGN)}
    d["_bf"] = sorted(p.card.name + ":" + str(p.counters) + ":" + str(p.tapped) + ":" + str(sorted(p.ctr.items())) for p in st.battlefield)
    d["_gy"] = sorted(st.graveyard); d["_hand"] = sorted(st.hand); d["_ex"] = sorted(st.exile)
    if lib: d["_lib"] = list(st.library)
    d["_opp"] = [(o.life, list(o.library), list(o.graveyard), o.rad, o.eliminated, o.lands) for o in st.opps]
    d["_mill_src"] = sorted(st.opp_mill_by_source.items())
    return d
def run(m, sd, resil):
    """Devolve (estado final, conjunto de nomes VISTOS: mao + cemiterio + campo + exilio no inicio e no fim de cada turno meu; pega a mao inicial e a carta descartada/gasta depois)."""
    visto = set()
    orig = m.play_turn
    def snap_nomes(st):
        visto.update(st.hand); visto.update(st.graveyard); visto.update(st.exile); visto.update(p.card.name for p in st.battlefield)
    def w(st):
        snap_nomes(st)
        r = orig(st)
        snap_nomes(st)
        return r
    m.play_turn = w
    try:
        st = (m.simulate_one_with_interaction if resil else m.simulate_one)(sd, 12)
    finally:
        m.play_turn = orig
    snap_nomes(st)
    return st, visto
bad1 = ok1 = bad2 = ok2 = visto_n = 0
for resil in (False, True):
    for i in range(N):
        sd = S0 + i
        sa, vis_a = run(ANTES, sd, resil)
        a = snap(sa)
        NOVO.SWAPS = (); NOVO.SWAP_IN_PLACE = False
        b = snap(run(NOVO, sd, resil)[0])
        if a != b:
            bad1 += 1; print("DIVERGE (1) SWAPS=()", sd, resil, [k for k in a if a[k] != b.get(k)][:5])
        else:
            ok1 += 1
        NOVO.SWAPS = tuple(zip(OUT, NOVAS)); NOVO.SWAP_IN_PLACE = True
        s_on, vis_n = run(NOVO, sd, resil)
        NOVO.SWAPS = (); NOVO.SWAP_IN_PLACE = False
        # decisoes pela IDENTIDADE da carta (scry do Palantir, mulligan, Kozilek devolvendo o cemiterio ao baralho) so' importam se a carta foi VISTA; `vis_*` acumula tudo que passou por mao/cemiterio/campo/exilio
        if any(c in vis_a for c in OUT) or any(c in vis_n for c in NOVAS) or s_on.interaction_plays != sa.interaction_plays or "Palantír of Orthanc" in vis_a or sa.kozilek_shuffles_total > 0 or sa.mulligans > 0:
            visto_n += 1
            continue
        if snap(sa, lib=False) != snap(s_on, lib=False):
            bad2 += 1; print("DIVERGE (2) nenhuma das seis vista", sd, resil, [k for k, v in snap(sa, lib=False).items() if v != snap(s_on, lib=False).get(k)][:5])
        else:
            ok2 += 1
print(f"(1) SWAPS=() == ANTES: {ok1} identicas, {bad1} divergencias | (2) nenhuma das 6 vista (n={ok2 + bad2}): {ok2} identicas, {bad2} divergencias | partidas com alguma das seis vista (fora de (2)): {visto_n}")
assert ok1 > 0 and ok2 > 0, "verificacao vacua"
sys.exit(1 if (bad1 or bad2) else 0)
