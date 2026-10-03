"""Utilitarios comuns: carrega o simulador do Megatron ANTES (commit 3dae6ba) e DEPOIS (arquivo vivo) como modulos separados
e gera a impressao digital do estado final. O carregador faz chdir pro deck (o simulador le 'lista.md')."""
import hashlib, importlib.util, os, sys

DECK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ANTES = os.path.join(HERE, "codigo", "megatron_goldfish_v1_ANTES_3dae6ba.py")
DEPOIS = os.path.join(DECK, "megatron_goldfish_v1.py")
NOVOS = {"rng", "interaction_rng", "extra_tapped_lands_this_turn", "land_played_this_turn_name", "fetch_cracks_total",
         "fetch_duals_fetched_total", "fetch_untapped_total", "myriad_activations_total", "myriad_basics_fetched_total",
         "tapped_land_first_plays_total", "tapped_land_skipped_for_play_total"}


def carrega(caminho, nome):
    os.chdir(DECK)
    spec = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nome] = m
    spec.loader.exec_module(m)
    return m


def flags(m, mulligan="smart", fetch=True, tapped_max_turn=None):
    """Myriad e tapped T1/T2 ficam como no repositorio (ligados). `mulligan` in {legacy, bottom_only, smart}."""
    if hasattr(m, "FETCHLANDS_ENABLED"):
        m.MULLIGAN_BOTTOM_MODE = mulligan
        m.FETCHLANDS_ENABLED = fetch
        if tapped_max_turn is not None:
            m.TAPPED_LAND_FIRST_MAX_TURN = tapped_max_turn
    return m


def impressao(state):
    partes = []
    for k in sorted(vars(state)):
        if k in NOVOS:
            continue
        v = getattr(state, k)
        if isinstance(v, set):
            v = sorted(v)
        partes.append(f"{k}={v!r}")
    return hashlib.sha1("|".join(partes).encode()).hexdigest()
