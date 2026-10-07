"""Bit-identidade das 6 candidatas (Fractured Sanity, Screeching Scorchbeast, Inexorable Tide, Branching Evolution, Loading Zone, The Earth Crystal) no simulador do Mothman (Regra #1 de CLAUDE.md).
(1) SWAPS=() (as seis fora do baralho): o simulador NOVO == o snapshot `codigo/mothman_goldfish_v1_ANTES_HM.py` (Horrigan/Master ja' dentro), campo a campo, N sementes x 2 modos, com a chave
    PERSIST_ZERO_TOUGHNESS_DIES = False (a correcao do persist MUDA o comportamento da lista base quando a Glen Elendra volta com tenacidade 0: com a chave ligada a diferenca e' esperada e e' medida
    a parte) e SCORCH_MIN_X nos dois extremos (campos fractured_/scorch_/tide_/branching_/loading_/crystal_/warp_/persist_zero_ ignorados: so' existem no novo).
(2) As seis NO baralho (no lugar): partida em que NENHUMA das seis e' vista (mao, campo, cemiterio, exilio, exilio de Warp) e' IDENTICA com SCORCH_MIN_X nos 2 extremos.
Confere que ha > 0 partidas em cada grupo (verificacao vacua e' bug). Uso: python3 bitident_c2.py N [semente0]"""
import importlib.util, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(aqui, "..", "..", ".."))
def load(path, tag):
    os.chdir(DECK)
    spec = importlib.util.spec_from_file_location(tag, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
ANTES = load(os.path.join(aqui, "..", "codigo", "mothman_goldfish_v1_ANTES_HM.py"), "antes")
NOVO = load(os.path.join(DECK, "mothman_goldfish_v1.py"), "novo")
N = int(sys.argv[1]); S0 = int(sys.argv[2]) if len(sys.argv) > 2 else 9_000_000
SEIS = ["Fractured Sanity", "Screeching Scorchbeast", "Inexorable Tide", "Branching Evolution", "Loading Zone", "The Earth Crystal"]
OUT = ["An Offer You Can't Refuse", "Negate", "Arcane Denial", "Toxic Deluge", "Cold-Eyed Selkie", "Didn't Say Please"]
IGN = ("jace_", "horrigan_", "master_", "fractured_", "scorch_", "tide_", "branching_", "loading_", "crystal_", "warp_", "persist_zero_")
def snap(st):
    d = {k: v for k, v in vars(st).items() if isinstance(v, (int, float, bool, str, type(None))) and not k.startswith(IGN)}
    d["_bf"] = sorted(p.card.name + ":" + str(p.counters) + ":" + str(p.tapped) + ":" + str(sorted(p.ctr.items())) for p in st.battlefield)
    d["_gy"] = sorted(st.graveyard); d["_hand"] = sorted(st.hand); d["_lib"] = list(st.library); d["_ex"] = sorted(st.exile)
    d["_opp"] = [(o.life, list(o.library), list(o.graveyard), o.rad, o.eliminated) for o in st.opps]
    d["_mill_src"] = sorted(st.opp_mill_by_source.items())
    return d
def run(m, sd, resil):
    return (m.simulate_one_with_interaction if resil else m.simulate_one)(sd, 12)
def flags(**kw):
    base = {"SCORCH_MIN_X": 3, "PERSIST_ZERO_TOUGHNESS_DIES": False}; base.update(kw)
    for k, v in base.items(): setattr(NOVO, k, v)
EXTREMO = {"SCORCH_MIN_X": 1}
bad1 = ok1 = bad2 = ok2 = entrou = 0
for resil in (False, True):
    for i in range(N):
        sd = S0 + i
        a = snap(run(ANTES, sd, resil))
        NOVO.SWAPS = (); NOVO.SWAP_IN_PLACE = False
        for fl in ({}, EXTREMO):
            flags(**fl)
            b = snap(run(NOVO, sd, resil))
            if a != b:
                bad1 += 1; print("DIVERGE (1) SWAPS=()", sd, resil, fl, [k for k in a if a[k] != b.get(k)][:5])
            else:
                ok1 += 1
        flags()
        NOVO.SWAPS = tuple(zip(OUT, SEIS)); NOVO.SWAP_IN_PLACE = True
        s_on = run(NOVO, sd, resil)
        zonas = lambda s: list(s.hand) + list(s.graveyard) + list(s.exile) + [p.card.name for p in s.battlefield]
        zonas2 = zonas(s_on) + [n for n, _ in s_on.warp_exile]
        visto = any(c in zonas2 for c in SEIS) or any(getattr(s_on, k) is not None for k in ("scorch_enter_turn", "tide_enter_turn", "branching_enter_turn", "loading_enter_turn", "crystal_enter_turn"))
        if not visto:
            on = snap(s_on)
            flags(**EXTREMO)
            off = snap(run(NOVO, sd, resil))
            flags()
            if on != off:
                bad2 += 1; print("DIVERGE (2) nenhuma das duas vista", sd, resil, [k for k in on if on[k] != off.get(k)][:5])
            else:
                ok2 += 1
        else:
            entrou += 1
NOVO.SWAPS = ()
print(f"N = {N} x 2 modos (sementes {S0}..{S0 + N - 1}): (1) SWAPS=() identico ao snapshot ANTES (HM) em {ok1} de {2 * 2 * N} comparacoes (chaves nos 2 extremos); divergencias {bad1} | "
      f"(2) as seis no baralho: {ok2} partidas em que nenhuma das seis foi vista (mao/campo/cemiterio/exilio), identicas com as chaves nos 2 extremos (divergencias {bad2}); {entrou} partidas em que alguma apareceu (podem diferir)")
assert ok1 > 0 and ok2 > 0 and entrou > 0, "grupo vazio: verificacao vacua"
sys.exit(1 if (bad1 or bad2) else 0)
