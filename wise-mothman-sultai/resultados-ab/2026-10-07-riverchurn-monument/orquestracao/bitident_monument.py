"""Bit-identidade do Riverchurn Monument no simulador do Mothman (Regra #1 de CLAUDE.md).
(1) SWAPS=() (Monument fora do baralho): o simulador NOVO == o snapshot `codigo/mothman_goldfish_v1_ANTES_cd5d453.py`, campo a campo, N sementes x 2 modos (campos `riverchurn_*` e
    `riverchurn_enter_turn` ignorados: so' existem no novo). As chaves RIVERCHURN_* nao podem mexer em nada se a carta nao existe.
(2) Monument NO baralho (`Negate -> Monument`, no lugar): partida em que o Monument NUNCA entrou em campo (riverchurn_enter_turn None) e' IDENTICA com RIVERCHURN_ACTIVATE ligado e desligado
    (a chave so' pode mexer se a carta entra em jogo). Confere que ha > 0 partidas em cada grupo (verificacao vacua e' bug).
Uso: python3 bitident_monument.py N [semente0]   (sai com codigo != 0 se algo diverge)"""
import importlib.util, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(aqui, "..", "..", ".."))
def load(path, tag):
    os.chdir(DECK)
    spec = importlib.util.spec_from_file_location(tag, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
ANTES = load(os.path.join(aqui, "..", "codigo", "mothman_goldfish_v1_ANTES_cd5d453.py"), "antes")
NOVO = load(os.path.join(DECK, "mothman_goldfish_v1.py"), "novo")
N = int(sys.argv[1]); S0 = int(sys.argv[2]) if len(sys.argv) > 2 else 6_000_000
def snap(st):
    d = {k: v for k, v in vars(st).items() if isinstance(v, (int, float, bool, str, type(None))) and not k.startswith("riverchurn_")}
    d["_bf"] = sorted(p.card.name + ":" + str(p.counters) + ":" + str(p.tapped) + ":" + str(sorted(p.ctr.items())) for p in st.battlefield)
    d["_gy"] = sorted(st.graveyard); d["_hand"] = sorted(st.hand); d["_lib"] = list(st.library)
    d["_opp"] = [(o.life, list(o.library), list(o.graveyard), o.rad, o.eliminated) for o in st.opps]
    d["_mill_src"] = sorted(st.opp_mill_by_source.items())
    return d
def run(m, sd, resil):
    return (m.simulate_one_with_interaction if resil else m.simulate_one)(sd, 12)
bad1 = ok1 = 0; bad2 = ok2 = 0; entrou = 0
for resil in (False, True):
    for i in range(N):
        sd = S0 + i
        a = snap(run(ANTES, sd, resil))
        NOVO.SWAPS = (); NOVO.SWAP_IN_PLACE = False
        for flags in ({"RIVERCHURN_ACTIVATE": True, "RIVERCHURN_SELF": False}, {"RIVERCHURN_ACTIVATE": False, "RIVERCHURN_SELF": True, "RIVERCHURN_TAP_FIRST": True, "RIVERCHURN_OPP_END_STEP": True}):
            for k, v in flags.items():
                if hasattr(NOVO, k): setattr(NOVO, k, v)
            b = snap(run(NOVO, sd, resil))
            if a != b:
                bad1 += 1; print("DIVERGE (1) SWAPS=()", sd, resil, flags, [k for k in a if a[k] != b.get(k)][:5])
            else:
                ok1 += 1
        for k, v in {"RIVERCHURN_ACTIVATE": True, "RIVERCHURN_SELF": False, "RIVERCHURN_TAP_FIRST": False, "RIVERCHURN_OPP_END_STEP": False}.items():
            if hasattr(NOVO, k): setattr(NOVO, k, v)
        NOVO.SWAPS = (("Negate", "Riverchurn Monument"),); NOVO.SWAP_IN_PLACE = True
        s_on = run(NOVO, sd, resil); on = snap(s_on)
        if s_on.riverchurn_enter_turn is None:
            NOVO.RIVERCHURN_ACTIVATE = False
            s_off = run(NOVO, sd, resil); off = snap(s_off)
            NOVO.RIVERCHURN_ACTIVATE = True
            if on != off:
                bad2 += 1; print("DIVERGE (2) Monument nunca entrou", sd, resil, [k for k in on if on[k] != off.get(k)][:5])
            else:
                ok2 += 1
        else:
            entrou += 1
NOVO.SWAPS = ()
print(f"N = {N} x 2 modos (sementes {S0}..{S0 + N - 1}): (1) SWAPS=() identico ao snapshot ANTES (cd5d453) em {ok1} de {2 * 2 * N} comparacoes (2 conjuntos de chaves); divergencias {bad1} | "
      f"(2) Monument no baralho: {ok2} partidas em que ele nunca entrou em campo, identicas com ACTIVATE ligado/desligado (divergencias {bad2}); {entrou} partidas em que ele entrou (podem diferir)")
assert ok1 > 0 and ok2 > 0 and entrou > 0, "grupo vazio: verificacao vacua"
sys.exit(1 if (bad1 or bad2) else 0)
