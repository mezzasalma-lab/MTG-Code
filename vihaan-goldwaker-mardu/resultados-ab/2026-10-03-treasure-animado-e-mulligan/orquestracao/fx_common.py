"""Utilitarios comuns: carrega o simulador do Vihaan ANTES (commit 6e623d3) e DEPOIS (arquivo vivo) como modulos separados
e gera a impressao digital do estado final de uma partida. O carregador faz chdir pro deck (o simulador le 'lista.md')."""
import hashlib, importlib.util, os, sys

DECK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ANTES = os.path.join(HERE, "codigo", "vihaan_goldfish_v1_ANTES_6e623d3.py")
DEPOIS = os.path.join(DECK, "vihaan_goldfish_v1.py")
NOVOS = {"treasures_animated_alive", "animated_treasures_sacrificed_any_total", "tapped_land_first_plays_total",
         "tapped_land_skipped_for_play_total", "interaction_rng"}


def carrega(caminho, nome):
    os.chdir(DECK)
    spec = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nome] = m  # o @dataclass consulta sys.modules
    spec.loader.exec_module(m)
    return m


def flags(m, treasure=True, bottom=True, tapped=True, tapped_max_turn=None, skip_if_loses_play=True):
    if hasattr(m, "ANIMATED_TREASURE_ROUTING_ENABLED"):
        m.ANIMATED_TREASURE_ROUTING_ENABLED = treasure
        m.MULLIGAN_SMART_BOTTOM_ENABLED = bottom
        m.TAPPED_LAND_FIRST_ENABLED = tapped
        m.TAPPED_LAND_FIRST_SKIP_IF_LOSES_PLAY = skip_if_loses_play
        if tapped_max_turn is not None:
            m.TAPPED_LAND_FIRST_MAX_TURN = tapped_max_turn
    return m


def impressao(state):
    """Hash de TODO o estado final (menos objetos Random e os contadores novos, que so' existem no DEPOIS)."""
    partes = []
    for k in sorted(vars(state)):
        if k in NOVOS:
            continue
        v = getattr(state, k)
        if isinstance(v, set):
            v = sorted(v)
        partes.append(f"{k}={v!r}")
    return hashlib.sha1("|".join(partes).encode()).hexdigest()
