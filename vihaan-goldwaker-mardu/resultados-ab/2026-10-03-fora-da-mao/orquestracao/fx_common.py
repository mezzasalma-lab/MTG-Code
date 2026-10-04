"""Utilitarios comuns: carrega o simulador do Vihaan ANTES (commit c04840d) e DEPOIS (arquivo vivo) como modulos separados e gera a
impressao digital do estado final. O carregador faz chdir pro deck (o simulador le 'lista.md')."""
import hashlib, importlib.util, os, sys

DECK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ANTES = os.path.join(HERE, "codigo", "vihaan_goldfish_v1_ANTES_c04840d.py")
DEPOIS = os.path.join(DECK, "vihaan_goldfish_v1.py")
NOVOS = {"impulse_all_first_total", "treasure_farm_dictate_total", "dictate_triggers_total", "treasure_farm_total", "impulse_expiring_first_total", "interaction_rng", "super_nova_emblems", "seph_batch_active", "seph_batch_front_up", "seph_batch_emblems", "seph_batch_leaves",
         "sephiroth_extra_triggers_total", "impulse_lands", "impulse_lands_played_total", "impulse_spells_cast_total", "lotho_triggers_total",
         "treasures_sacrificed_this_turn", "storm_sac_baseline", "storm_pump_total", "sevinne_nonpermanent_returns_total"}


def carrega(caminho, nome):
    os.chdir(DECK)
    spec = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nome] = m
    spec.loader.exec_module(m)
    return m


def flags(m, land=True, cast=True, count=True, storm=True, sevinne=True):
    """As cinco correcoes de 'fora da mao'. As demais chaves do Vihaan (Treasure animado, mulligan, tapped, Sephiroth) ficam como no repositorio."""
    if hasattr(m, "IMPULSE_LAND_PLAY_ENABLED"):
        m.IMPULSE_LAND_PLAY_ENABLED = land
        m.IMPULSE_CAST_PIPELINE_ENABLED = cast
        m.SPELL_CAST_COUNT_ALL_PATHS_ENABLED = count
        m.STORM_SACRIFICE_PUMP_ENABLED = storm
        m.SEVINNE_PERMANENT_TARGET_ENABLED = sevinne
    if hasattr(m, "IMPULSE_EXPIRING_FIRST_ENABLED"):  # 5a rodada (Prosper expirando primeiro; farm de Treasure animado): ligadas no arquivo vivo, desligadas aqui (esta pasta reproduz o simulador do commit dela)
        m.IMPULSE_EXPIRING_FIRST_ENABLED = False
        m.TREASURE_SELF_OUTLET_FARM_ENABLED = False
    if hasattr(m, "IMPULSE_ALL_FIRST_ENABLED"):  # 6a rodada (exilio sempre primeiro; farm tambem com Dictate): ligadas no arquivo vivo, desligadas aqui
        m.IMPULSE_ALL_FIRST_ENABLED = False
        m.TREASURE_FARM_WITH_DICTATE_ENABLED = False
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
