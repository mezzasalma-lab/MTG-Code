"""Bit-identidade do Jace, Wielder of Mysteries no simulador do Mothman (Regra #1 de CLAUDE.md).
(1) SWAPS=() (Jace fora do baralho): o simulador NOVO == o snapshot `codigo/mothman_goldfish_v1_ANTES_1c18475.py`, campo a campo, N sementes x 2 modos, com as chaves JACE_* nos dois extremos
    (campos `jace_*` ignorados: so' existem no novo). As chaves nao podem mexer em nada se a carta nao existe.
(2) Jace NO baralho (`Kozilek -> Jace`, no lugar): partida em que ele NUNCA e' conjurado (nenhum `jace_*` positivo e carta fora de campo/cemiterio no fim) e' IDENTICA com a linha de vitoria
    ligada e desligada e com JACE_REMOVAL_PROB 0 e 0.5 (as chaves so' podem mexer se a carta entra em jogo). Confere que ha > 0 partidas em cada grupo (verificacao vacua e' bug).
Uso: python3 bitident_jace.py N [semente0]"""
import importlib.util, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(aqui, "..", "..", ".."))
def load(path, tag):
    os.chdir(DECK)
    spec = importlib.util.spec_from_file_location(tag, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
ANTES = load(os.path.join(aqui, "..", "codigo", "mothman_goldfish_v1_ANTES_1c18475.py"), "antes")
NOVO = load(os.path.join(DECK, "mothman_goldfish_v1.py"), "novo")
N = int(sys.argv[1]); S0 = int(sys.argv[2]) if len(sys.argv) > 2 else 7_000_000
J = "Jace, Wielder of Mysteries"
def snap(st):
    d = {k: v for k, v in vars(st).items() if isinstance(v, (int, float, bool, str, type(None))) and not k.startswith("jace_")}
    d["_bf"] = sorted(p.card.name + ":" + str(p.counters) + ":" + str(p.tapped) + ":" + str(sorted(p.ctr.items())) for p in st.battlefield)
    d["_gy"] = sorted(st.graveyard); d["_hand"] = sorted(st.hand); d["_lib"] = list(st.library)
    d["_opp"] = [(o.life, list(o.library), list(o.graveyard), o.rad, o.eliminated) for o in st.opps]
    d["_mill_src"] = sorted(st.opp_mill_by_source.items())
    return d
def run(m, sd, resil):
    return (m.simulate_one_with_interaction if resil else m.simulate_one)(sd, 12)
def flags(**kw):
    base = {"JACE_WIN_LINE": True, "JACE_REMOVAL_PROB": 0.0, "JACE_STATIC_ENABLED": True}; base.update(kw)
    for k, v in base.items(): setattr(NOVO, k, v)
bad1 = ok1 = bad2 = ok2 = entrou = 0
for resil in (False, True):
    for i in range(N):
        sd = S0 + i
        a = snap(run(ANTES, sd, resil))
        NOVO.SWAPS = (); NOVO.SWAP_IN_PLACE = False
        for fl in ({}, {"JACE_WIN_LINE": False, "JACE_REMOVAL_PROB": 0.5, "JACE_STATIC_ENABLED": False}):
            flags(**fl)
            b = snap(run(NOVO, sd, resil))
            if a != b:
                bad1 += 1; print("DIVERGE (1) SWAPS=()", sd, resil, fl, [k for k in a if a[k] != b.get(k)][:5])
            else:
                ok1 += 1
        flags()
        NOVO.SWAPS = (("Kozilek, Butcher of Truth", J),); NOVO.SWAP_IN_PLACE = True
        s_on = run(NOVO, sd, resil)
        vista = s_on.jace_plus_uses > 0 or s_on.jace_wins > 0 or any(p.card.name == J for p in s_on.battlefield) or J in s_on.graveyard or J in s_on.hand
        if not vista:
            on = snap(s_on)
            flags(JACE_WIN_LINE=False, JACE_REMOVAL_PROB=0.5)
            off = snap(run(NOVO, sd, resil))
            flags()
            if on != off:
                bad2 += 1; print("DIVERGE (2) Jace nunca visto", sd, resil, [k for k in on if on[k] != off.get(k)][:5])
            else:
                ok2 += 1
        else:
            entrou += 1
NOVO.SWAPS = ()
print(f"N = {N} x 2 modos (sementes {S0}..{S0 + N - 1}): (1) SWAPS=() identico ao snapshot ANTES (1c18475) em {ok1} de {2 * 2 * N} comparacoes (chaves nos 2 extremos); divergencias {bad1} | "
      f"(2) Jace no baralho: {ok2} partidas em que ele nunca foi visto (mao/campo/cemiterio), identicas com as chaves nos 2 extremos (divergencias {bad2}); {entrou} partidas em que ele apareceu (podem diferir)")
assert ok1 > 0 and ok2 > 0 and entrou > 0, "grupo vazio: verificacao vacua"
sys.exit(1 if (bad1 or bad2) else 0)
