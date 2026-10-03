"""Utilitarios comuns: carrega o simulador do Vihaan ANTES (commit ba74496) e DEPOIS (arquivo vivo) como modulos separados
e gera a impressao digital do estado final. O carregador faz chdir pro deck (o simulador le 'lista.md')."""
import hashlib, importlib.util, os, sys

DECK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ANTES = os.path.join(HERE, "codigo", "vihaan_goldfish_v1_ANTES_ba74496.py")
DEPOIS = os.path.join(DECK, "vihaan_goldfish_v1.py")
NOVOS = {"interaction_rng", "super_nova_emblems", "seph_batch_active", "seph_batch_front_up", "seph_batch_emblems",
         "seph_batch_leaves", "sephiroth_extra_triggers_total"}


def carrega(caminho, nome):
    os.chdir(DECK)
    spec = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nome] = m
    spec.loader.exec_module(m)
    return m


def flags(m, emblema=True, simultaneas=True, fronteira=True):
    """Os tres ajustes do Sephiroth. As outras tres chaves do Vihaan (Treasure animado, mulligan, terreno tapped) ficam ligadas, como no repositorio."""
    if hasattr(m, "SEPHIROTH_EMBLEM_STACKING_ENABLED"):
        m.SEPHIROTH_EMBLEM_STACKING_ENABLED = emblema
        m.SEPHIROTH_SIMULTANEOUS_DEATH_ENABLED = simultaneas
        m.SEPHIROTH_TURN_BOUNDARY_ENABLED = fronteira
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
