"""
Teste dirigido do London mulligan (CR 103.5) nos 4 simuladores que tinham o
mesmo bug: as cartas postas no FUNDO do grimorio eram embaralhadas de volta
logo em seguida (`rng.shuffle` depois do bottom). Corrigido em 2026-09-24.

Forca 2 mulligans (o 1o e' gratis, o 2o poe 1 carta no fundo) e confere, no
inicio do turno 1, que a carta escolhida pelo `choose_bottom` e' a ULTIMA do
grimorio e nao esta' na mao -- no modo padrao e no modo de resiliencia.

Rodar: python3 test_london_mulligan.py
"""
import importlib.util
import sys
import traceback

DECKS = [
    ("beorn-fierce", "beorn_goldfish_v1"),
    ("edgar-markov-mardu", "edgar_markov_goldfish_v1"),
    ("thranduil-sultai", "thranduil_goldfish_v1"),
    ("prismatic-bridge-wurbg", "prismatic_bridge_goldfish_v1"),
]


class _Stop(Exception):
    pass


def _load(folder, module):
    sys.path.insert(0, folder)
    spec = importlib.util.spec_from_file_location(module, f"{folder}/{module}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[module] = m
    spec.loader.exec_module(m)
    return m


def _check(m, runner):
    """Roda `runner` com 2 mulligans forcados e para no 1o play_turn."""
    calls = {"keep": 0}
    seen = {}
    orig_keep, orig_bottom, orig_play = m.should_keep, m.choose_bottom, m.play_turn

    def keep(hand):
        calls["keep"] += 1
        return calls["keep"] >= 3

    def bottom(hand, n):
        out = orig_bottom(hand, n)
        seen["bottom"] = list(out)
        return out

    def play(state, *a, **k):
        seen["library_tail"] = state.library[-len(seen["bottom"]):]
        seen["hand"] = list(state.hand)
        raise _Stop()

    m.should_keep, m.choose_bottom, m.play_turn = keep, bottom, play
    try:
        runner()
    except _Stop:
        pass
    finally:
        m.should_keep, m.choose_bottom, m.play_turn = orig_keep, orig_bottom, orig_play
    assert len(seen["bottom"]) == 1, seen
    assert seen["library_tail"] == seen["bottom"], seen
    assert seen["bottom"][0] not in seen["hand"] or seen["hand"].count(seen["bottom"][0]) < 2, seen


def run_all():
    failed = 0
    for folder, module in DECKS:
        m = _load(folder, module)
        for label, runner in (("padrao", lambda: m.simulate_one(4242, 1) if module != "prismatic_bridge_goldfish_v1"
                               else m.simulate_one(4242, 1, False)),
                              ("resiliencia", lambda: m.simulate_one_with_interaction(4242, 1))):
            try:
                _check(m, runner)
                print(f"PASS {folder} ({label})")
            except Exception:
                failed += 1
                print(f"FAIL {folder} ({label})")
                traceback.print_exc()
    print(f"\n{2 * len(DECKS) - failed}/{2 * len(DECKS)} testes passaram")
    return failed


if __name__ == "__main__":
    raise SystemExit(1 if run_all() else 0)
