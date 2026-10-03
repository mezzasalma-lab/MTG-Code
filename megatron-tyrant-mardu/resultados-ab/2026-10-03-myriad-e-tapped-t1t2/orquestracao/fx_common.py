"""Utilitarios comuns: carrega o simulador ANTES (commit 22d0ed2) e o DEPOIS
(arquivo vivo) como modulos separados, e gera a impressao digital de um estado
final de partida. Rodar de qualquer pasta: o carregador faz chdir pro deck
(o simulador le 'lista.md' por caminho relativo)."""
import hashlib, importlib.util, os, random, sys

DECK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ANTES = os.path.join(HERE, "codigo", "megatron_goldfish_v1_ANTES_22d0ed2.py")
DEPOIS = os.path.join(DECK, "megatron_goldfish_v1.py")


def carrega(caminho, nome):
    os.chdir(DECK)
    spec = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nome] = m  # o @dataclass do simulador consulta sys.modules
    spec.loader.exec_module(m)
    return m


def flags(m, tapped=True, myriad=True, tapped_max_turn=None, skip_if_loses_play=True):
    """Liga/desliga as duas correcoes (so' existe no modulo DEPOIS)."""
    if hasattr(m, "FETCHLANDS_ENABLED"):
        # Nota posterior (2026-10-03, 2a rodada): o simulador vivo ganhou fetch lands e mulligan com escolha
        # (resultados-ab/2026-10-03-mulligan-e-fetches/). Esta pasta mede o simulador do commit 3dae6ba: desliga as duas.
        m.FETCHLANDS_ENABLED = False
        m.MULLIGAN_BOTTOM_MODE = "legacy"
    if hasattr(m, "TAPPED_LAND_FIRST_ENABLED"):
        m.TAPPED_LAND_FIRST_ENABLED = tapped
        m.MYRIAD_ABILITY_ENABLED = myriad
        m.TAPPED_LAND_FIRST_SKIP_IF_LOSES_PLAY = skip_if_loses_play
        if tapped_max_turn is not None:
            m.TAPPED_LAND_FIRST_MAX_TURN = tapped_max_turn
    return m


def impressao(state):
    """Hash de TODO o estado final (menos objetos Random e os 4 contadores novos
    que so' existem no DEPOIS)."""
    ignora = {"rng", "interaction_rng", "myriad_activations_total", "myriad_basics_fetched_total",
              "tapped_land_first_plays_total", "tapped_land_skipped_for_play_total",
              # campos da 2a rodada (2026-10-03), inexistentes no simulador ANTES:
              "extra_tapped_lands_this_turn", "land_played_this_turn_name", "fetch_cracks_total",
              "fetch_duals_fetched_total", "fetch_untapped_total"}
    partes = []
    for k in sorted(vars(state)):
        if k in ignora:
            continue
        v = getattr(state, k)
        if isinstance(v, set):
            v = sorted(v)
        partes.append(f"{k}={v!r}")
    return hashlib.sha1("|".join(partes).encode()).hexdigest()
