"""Utilitarios comuns: carrega o simulador do Vihaan ANTES (commit ba74496) e DEPOIS (arquivo vivo) como modulos separados
e gera a impressao digital do estado final. O carregador faz chdir pro deck (o simulador le 'lista.md')."""
import hashlib, importlib.util, os, sys

DECK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ANTES = os.path.join(HERE, "codigo", "vihaan_goldfish_v1_ANTES_ba74496.py")
DEPOIS = os.path.join(DECK, "vihaan_goldfish_v1.py")
NOVOS = {"dictate_triggers_total", "treasure_farm_total", "impulse_expiring_first_total", "impulse_lands", "impulse_lands_played_total", "impulse_spells_cast_total", "lotho_triggers_total",
         "treasures_sacrificed_this_turn", "storm_sac_baseline", "storm_pump_total", "sevinne_nonpermanent_returns_total", "interaction_rng", "super_nova_emblems", "seph_batch_active", "seph_batch_front_up", "seph_batch_emblems",
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
    # Rodada posterior ("fora da mao", commit seguinte): as 5 chaves novas vem LIGADAS no arquivo vivo; aqui ficam desligadas pra esta pasta
    # continuar reproduzindo o simulador como era no commit dela.
    if hasattr(m, "IMPULSE_LAND_PLAY_ENABLED"):
        m.IMPULSE_LAND_PLAY_ENABLED = False
        m.IMPULSE_CAST_PIPELINE_ENABLED = False
        m.SPELL_CAST_COUNT_ALL_PATHS_ENABLED = False
        m.STORM_SACRIFICE_PUMP_ENABLED = False
        m.SEVINNE_PERMANENT_TARGET_ENABLED = False
    if hasattr(m, "IMPULSE_EXPIRING_FIRST_ENABLED"):  # 5a rodada (Prosper expirando primeiro; farm de Treasure animado): ligadas no arquivo vivo, desligadas aqui
        m.IMPULSE_EXPIRING_FIRST_ENABLED = False
        m.TREASURE_SELF_OUTLET_FARM_ENABLED = False
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
