"""Utilitarios comuns: carrega o simulador do Vihaan ANTES (commit 7cd3f55) e DEPOIS (arquivo vivo) como modulos separados e gera a
impressao digital do estado final. O carregador faz chdir pro deck (o simulador le 'lista.md')."""
import hashlib, importlib.util, os, sys

DECK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ANTES = os.path.join(HERE, "codigo", "vihaan_goldfish_v1_ANTES_7cd3f55.py")
DEPOIS = os.path.join(DECK, "vihaan_goldfish_v1.py")
NOVOS = {"interaction_rng", "super_nova_emblems", "seph_batch_active", "seph_batch_front_up", "seph_batch_emblems", "seph_batch_leaves",
         "sephiroth_extra_triggers_total", "impulse_lands", "impulse_lands_played_total", "impulse_spells_cast_total", "lotho_triggers_total",
         "treasures_sacrificed_this_turn", "storm_sac_baseline", "storm_pump_total", "sevinne_nonpermanent_returns_total",
         "dictate_triggers_total", "treasure_farm_total", "impulse_expiring_first_total"}


def carrega(caminho, nome):
    os.chdir(DECK)
    spec = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nome] = m
    spec.loader.exec_module(m)
    return m


def flags(m, first=True, farm=True):
    """As duas correcoes desta rodada (exilio expirando primeiro; Treasure animado como saida propria com Mahadi/Plunderer). As demais chaves do
    Vihaan (inclusive as 5 de 'fora da mao') ficam como no repositorio."""
    if hasattr(m, "IMPULSE_EXPIRING_FIRST_ENABLED"):
        m.IMPULSE_EXPIRING_FIRST_ENABLED = first
        m.TREASURE_SELF_OUTLET_FARM_ENABLED = farm
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
