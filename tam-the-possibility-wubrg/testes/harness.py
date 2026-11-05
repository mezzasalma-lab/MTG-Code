"""Harness dos testes dirigidos do simulador do Tam: monta um GameState deterministico (mao, campo, cemiterio, biblioteca) e roda UMA mecanica por vez.
Cada teste confirma que a clausula especifica do oraculo dispara de verdade (CLAUDE.md Regra #1: teste unitario dirigido)."""
import os, sys, random, traceback
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
import tam_goldfish_v1 as T

TESTS = []


def test(name):
    def deco(fn):
        TESTS.append((name, fn))
        return fn
    return deco


def filler_library(exclude=()):
    lib = [c for c in T.current_library() if c not in exclude]
    random.Random(7).shuffle(lib)
    return lib


def mk(hand=(), bf=(), gy=(), lib=None, cz=True, turn=6, life=40, res=False, seed=1, opps=3, phase="main1"):
    """bf: nomes ou (nome, {"loyalty": n, "tapped": bool, "sick": bool, "ctr": {...}}). Permanentes entram 'ha' um turno' (sem doenca de invocacao) salvo sick=True."""
    st = T.GameState(rng=random.Random(seed))
    st.proxy_rng = random.Random(seed + 1)
    st.interaction_rng = random.Random(seed + 2)
    st.opps = [T.make_opp(seed, i) for i in range(1, 4)]
    st.opp_rngs = [None] + [random.Random(seed * 100 + i) for i in range(1, 4)]
    for o in st.opps[opps:]:
        o.eliminated = True
    st.turn = turn
    st.turn_id = turn * 4
    st.life = life
    st.resilience = res
    st.phase = phase
    st.hand = list(hand)
    st.graveyard = list(gy)
    used = set(hand) | set(gy) | {b if isinstance(b, str) else b[0] for b in bf}
    st.library = list(lib) if lib is not None else filler_library(used)
    st.commander_in_cz = cz
    for b in bf:
        name, opt = (b, {}) if isinstance(b, str) else b
        p = T.mk_perm(st, name, token=opt.get("token", False))
        p.entered_turn = turn if opt.get("sick") else turn - 1
        p.tapped = bool(opt.get("tapped"))
        if "planeswalker" in p.card.types:
            p.ctr["loyalty"] = opt.get("loyalty", p.card.loyalty)
        for k, v in opt.get("ctr", {}).items():
            p.ctr[k] = v
        if opt.get("attached_to") is not None:
            p.attached_to = opt["attached_to"]
        st.battlefield.append(p)
        if name == "Tam, the Possibility":
            st.commander_in_cz = False
            st.commander_uid = p.uid
    return st


def perm(st, name):
    for p in st.battlefield:
        if p.card.name == name:
            return p
    return None


def count(st, name):
    return sum(1 for p in st.battlefield if p.card.name == name)


def loy(st, name):
    p = perm(st, name)
    return None if p is None else T.loyalty(p)


def act(st, host_name, src, key, x=0):
    h = perm(st, host_name)
    assert h is not None, f"{host_name} nao esta em campo"
    return T.activate_ability(st, h, src, key, x)


def add_opp_creature(st, idx, p=3, t=3, **kw):
    c = T.new_opp_creature(p, t, **kw)
    c["sick"] = False
    st.opps[idx - 1].board.append(c)
    return c


class Fail(Exception):
    pass


def check(cond, msg="falhou"):
    if not cond:
        raise Fail(msg)


def run_all(verbose=True):
    ok = bad = 0
    fails = []
    for name, fn in TESTS:
        try:
            fn()
            ok += 1
        except Fail as e:
            bad += 1
            fails.append((name, str(e)))
        except Exception as e:
            bad += 1
            fails.append((name, "EXCECAO " + traceback.format_exc().strip().splitlines()[-1] + " | " + traceback.format_exc().strip().splitlines()[-3].strip()))
    if verbose:
        for n, m in fails:
            print("FALHOU:", n, "->", m)
        print(f"{ok} passaram, {bad} falharam, {len(TESTS)} no total")
    return ok, bad, fails
