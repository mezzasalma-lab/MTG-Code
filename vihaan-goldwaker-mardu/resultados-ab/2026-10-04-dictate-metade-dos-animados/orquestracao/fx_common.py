"""Utilitarios comuns: carrega o simulador do Vihaan ANTES (commit 9e613ea; ANTES0 = 8e9ab6e) e DEPOIS (arquivo vivo) como modulos separados e gera a
impressao digital do estado final. O carregador faz chdir pro deck (o simulador le 'lista.md')."""
import hashlib, importlib.util, os, sys

DECK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ANTES = os.path.join(HERE, "codigo", "vihaan_goldfish_v1_ANTES_9e613ea.py")    # 7a rodada: metade do ESTOQUE
ANTES0 = os.path.join(HERE, "codigo", "vihaan_goldfish_v1_ANTES_8e9ab6e.py")   # 6a rodada: o Dictate sacrifica TODOS os animados
DEPOIS = os.path.join(DECK, "vihaan_goldfish_v1.py")
NOVOS = {"interaction_rng", "super_nova_emblems", "seph_batch_active", "seph_batch_front_up", "seph_batch_emblems", "seph_batch_leaves",
         "sephiroth_extra_triggers_total", "impulse_lands", "impulse_lands_played_total", "impulse_spells_cast_total", "lotho_triggers_total",
         "treasures_sacrificed_this_turn", "storm_sac_baseline", "storm_pump_total", "sevinne_nonpermanent_returns_total",
         "dictate_triggers_total", "treasure_farm_total", "impulse_expiring_first_total", "impulse_all_first_total",
         "treasure_farm_dictate_total"}


def carrega(caminho, nome):
    os.chdir(DECK)
    spec = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nome] = m
    spec.loader.exec_module(m)
    return m


def flags(m, half=True, animados=True, dictate=True):
    """A correcao da 8a rodada (a metade conta so' os ANIMADOS, nao o estoque). `half` = chave da 7a rodada (reserva de metade), `animados` = chave da 8a
    (base da metade), `dictate` liga/desliga o farm com Dictate (variante 'sem'). Cada chave so' e' definida se existir no modulo (snapshots antigos nao tem as novas)."""
    if hasattr(m, "TREASURE_FARM_DICTATE_HALF_RESERVE_ENABLED"):
        m.TREASURE_FARM_DICTATE_HALF_RESERVE_ENABLED = half
    if hasattr(m, "TREASURE_FARM_DICTATE_HALF_OF_ANIMATED_ENABLED"):
        m.TREASURE_FARM_DICTATE_HALF_OF_ANIMATED_ENABLED = animados
    if hasattr(m, "TREASURE_FARM_WITH_DICTATE_ENABLED"):
        m.TREASURE_FARM_WITH_DICTATE_ENABLED = dictate
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
