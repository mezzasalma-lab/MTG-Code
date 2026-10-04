"""Utilitarios comuns: carrega o simulador do Vihaan ANTES (commit b30ef1f) e DEPOIS (arquivo vivo) como modulos separados e gera a
impressao digital do estado final. O carregador faz chdir pro deck (o simulador le 'lista.md')."""
import hashlib, importlib.util, os, sys

DECK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LEGADO = os.path.join(DECK, "resultados-ab", "_lista_legada")   # 12a rodada: a lista de a17049f (com Blood Money); os snapshots ANTES leem ESTA, nao a lista viva (que tem a Mythos)
ANTES = None   # esta rodada NAO altera o simulador: so' o harness (sac_harness.py); o codigo medido e' o do commit a17049f
DEPOIS = os.path.join(DECK, "vihaan_goldfish_v1.py")
NOVOS = {"mythos_cast_total", "mythos_br_spent_total", "mythos_br_pending", "mythos_perm_lost_total", "interaction_rng", "super_nova_emblems", "seph_batch_active", "seph_batch_front_up", "seph_batch_emblems", "seph_batch_leaves",
         "sephiroth_extra_triggers_total", "impulse_lands", "impulse_lands_played_total", "impulse_spells_cast_total", "lotho_triggers_total",
         "treasures_sacrificed_this_turn", "storm_sac_baseline", "storm_pump_total", "sevinne_nonpermanent_returns_total",
         "dictate_triggers_total", "treasure_farm_total", "impulse_expiring_first_total", "impulse_all_first_total",
         "treasure_farm_dictate_total", "treasures_tapped", "own_wipes_cast_total", "blood_money_cast_total", "own_wipe_commander_destroyed_total",
         "own_wipe_tapped_treasures_total", "own_wipe_held_total", "own_wipe_held_this_turn",
         "own_wipe_mitigated_casts_total", "own_wipe_animated_paid_total", "own_wipe_pay_drain_total"}


def carrega(caminho, nome):
    os.chdir(DECK if caminho == DEPOIS else LEGADO)
    spec = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nome] = m
    spec.loader.exec_module(m)
    if caminho == DEPOIS and hasattr(m, "MYTHOS_REPLACES_BLOOD_MONEY_ENABLED"):  # 12a rodada (Mythos no lugar do Blood Money; cascade recusa wipe segurado): ligadas no arquivo vivo,
        m.MYTHOS_REPLACES_BLOOD_MONEY_ENABLED = False                              # desligadas aqui: esta pasta continua reproduzindo o simulador e a lista COMO ERAM no commit dela
        m.CASCADE_DECLINE_HELD_WIPES_ENABLED = False
        m.BASE_LIBRARY = m.build_library()
    return m


def flags(m, bats=True):
    """A correcao da 11a rodada: `bats` = Mirkwood Bats so' dispara em SACRIFICIO de ficha (oraculo: "create or sacrifice a token"). As chaves anteriores ficam
    ligadas como no repositorio. So' e' definida se existir no modulo (o snapshot antigo nao tem)."""
    if hasattr(m, "MIRKWOOD_BATS_SACRIFICE_ONLY_ENABLED"):
        m.MIRKWOOD_BATS_SACRIFICE_ONLY_ENABLED = bats
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
