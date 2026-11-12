"""Harness A/B do Kingpin, Wilson Fisk no simulador do Vihaan, SEM alterar vihaan_goldfish_v1.py (usa o `swap` que o simulador já tem + monkeypatch).

Oráculo (Scryfall ao vivo, 2026-10-03; Marvel Super Heroes Commander): {3}{B}, Legendary Creature — Human Villain 3/6, Menace.
"Whenever you sacrifice Kingpin or another creature, create two Treasure tokens. This ability triggers only once each turn."  Rulings: nenhum.
Leitura das rulings do Vihaan (2024-04-12): os Treasures animados "mantêm as habilidades" enquanto são criaturas, então sacrificar um Treasure animado
(para mana ou em qualquer saída) é sacrificar UMA CRIATURA. Kingpin não é "outlaw" (Human Villain): sem vigilância/haste do Vihaan.

Onde o simulador roteia sacrifício: `on_permanent_sacrificed(n, is_artifact, is_creature, is_token)` ("chamado por toda via de sacrifício": Constructs,
fichas, criatura nomeada, Treasure). O gatilho do Kingpin é ligado AÍ (is_creature=True), uma vez por turno, e cria 2 Treasures por `create_treasures`
(Xorn +1, Anointed Procession ×2, Academy Manufactor, tudo como o simulador já faz para qualquer criação de Treasure).

POLÍTICA (KP_POLICY):
- sim   : só o que o simulador já roteia como sacrifício de CRIATURA (Constructs, fichas, criaturas nomeadas, Treasure animado via Ashnod's Altar).
- anim  : + sacrificar um Treasure ANIMADO (depois do início do combate, até o fim do turno) por qualquer via conta como sacrificar uma criatura
          (mana no 2º main, Krark-Clan Ironworks, Magda). Regra: Treasures animados são criaturas. O simulador original passa `as_creature=False` nesses
          caminhos para TODOS os gatilhos de criatura (Zulaport, Nadier's…): lacuna conhecida; aqui só o Kingpin a enxerga, para a base ficar intacta.
- delib : anim + linha deliberada: no end step, se o Kingpin ainda não disparou no turno e há Treasure animado, sacrifica UM Treasure animado por nada
          (o mana some) para disparar o Kingpin: -1 Treasure, +2 (ou +3/+4/+6 com Xorn/Procession).
Cor: o simulador não modela cor; o {B} do Kingpin é medido à parte (`b4_turn`: 1º turno com fonte de B e >=4 de mana)."""
import os
import sys

REPO = "/home/user/MTG-Code"
DADOS = os.path.join(REPO, "vihaan-goldwaker-mardu", "resultados-ab", "2026-10-03-kingpin", "dados")
os.chdir(os.path.join(REPO, "vihaan-goldwaker-mardu"))
sys.path.insert(0, os.path.join(REPO, "vihaan-goldwaker-mardu"))
import vihaan_goldfish_v1 as V  # noqa: E402

# 12a rodada (Mythos no lugar do Blood Money): o arquivo vivo agora tem a Mythos na lista; aqui as chaves novas ficam desligadas, a lista volta a ter o Blood Money (bit-identico a a17049f)
# e esta pasta continua reproduzindo o simulador COMO ERA no commit dela.
if hasattr(V, "MYTHOS_REPLACES_BLOOD_MONEY_ENABLED"):
    V.MYTHOS_REPLACES_BLOOD_MONEY_ENABLED = False
    V.CASCADE_DECLINE_HELD_WIPES_ENABLED = False
    V.BASE_LIBRARY = V.build_library()

KINGPIN = "Kingpin, Wilson Fisk"
BLANK = "Blank Card"
V.add(KINGPIN, 4, "creature", {"kingpin"})
V.add(BLANK, 99, "instant", set())
V.CREATURE_POWER[KINGPIN] = 3
V.TREASURE_SOURCE_TAGS.add("kingpin")      # gera Treasure: prioridade de conjuração como as demais fontes do simulador
V.LAND_NAMES = {n for n, c in V.CARD_DB.items() if c.ctype == "land"}
ORIG_LIBRARY = list(V.BASE_LIBRARY)
POLICY = {"mode": os.environ.get("KP_POLICY", "sim")}


def _kp_trigger(state):
    if getattr(state, "kp_triggered_this_turn", False):
        return
    state.kp_triggered_this_turn = True
    state.kp_triggers = getattr(state, "kp_triggers", 0) + 1
    antes = state.treasures_created_total
    V.create_treasures(state, 2, source="Kingpin")
    state.kp_treasures = getattr(state, "kp_treasures", 0) + (state.treasures_created_total - antes)


def _kp_active(state):
    return KINGPIN in state.battlefield or getattr(state, "_kp_self", False)


_orig_perm_sac = V.on_permanent_sacrificed


def _perm_sac(state, n, is_artifact, is_creature, is_token):
    _orig_perm_sac(state, n, is_artifact, is_creature, is_token)
    if is_creature and _kp_active(state):
        _kp_trigger(state)


V.on_permanent_sacrificed = _perm_sac

_orig_sac_named = V.sacrifice_named_creature


def _sac_named(state, name):
    state._kp_self = (name == KINGPIN)       # "Whenever you sacrifice Kingpin": o gatilho enxerga o próprio Kingpin saindo
    try:
        return _orig_sac_named(state, name)
    finally:
        state._kp_self = False


V.sacrifice_named_creature = _sac_named

_orig_sac_treasures = V.sacrifice_treasures


def _animated_left(state):
    return max(0, state.treasures_animated_this_combat - getattr(state, "_kp_anim_sac", 0))


def _sac_treasures(state, n, for_mana=False, as_creature=False):
    antes = state.treasures
    left = _animated_left(state)
    got = _orig_sac_treasures(state, n, for_mana=for_mana, as_creature=as_creature)
    if got and left > 0:
        state._kp_anim_sac = getattr(state, "_kp_anim_sac", 0) + min(got, left)
        if POLICY["mode"] in ("anim", "delib") and not as_creature and KINGPIN in state.battlefield:
            _kp_trigger(state)             # Treasure animado = criatura sacrificada (as_creature=True já passou por on_permanent_sacrificed)
    return got


V.sacrifice_treasures = _sac_treasures

_orig_play_turn = V.play_turn


def _play_turn(state, is_first_turn, on_play):
    state.kp_triggered_this_turn = False
    state._kp_anim_sac = 0
    _orig_play_turn(state, is_first_turn, on_play)


V.play_turn = _play_turn

_orig_end_step = V.end_step


def _end_step(state):
    if (POLICY["mode"] == "delib" and KINGPIN in state.battlefield and not getattr(state, "kp_triggered_this_turn", False)
            and state.treasures > 0 and _animated_left(state) > 0):
        state.kp_deliberate = getattr(state, "kp_deliberate", 0) + 1
        V.sacrifice_treasures(state, 1)    # mana descartado de propósito: o que interessa é a criatura sacrificada
    _orig_end_step(state)


V.end_step = _end_step

_orig_enter = V.enter_battlefield


def _enter(state, name, from_hand=True):
    _orig_enter(state, name, from_hand)
    if name == KINGPIN and getattr(state, "kp_cast_turn", None) is None:
        state.kp_cast_turn = state.turn


V.enter_battlefield = _enter

# ---- instrumentação só-leitura: o {B} do Kingpin (o simulador não modela cor) -------------------
B_LANDS = {"Blackcleave Cliffs", "Blood Crypt", "Bojuka Bog", "Brightclimb Pathway // Grimclimb Pathway", "Caves of Koilos", "Command Tower",
           "Desolate Mire", "Dragonskull Summit", "Exotic Orchard", "Fetid Heath", "Isolated Chapel", "Luxury Suite", "Path of Ancestry",
           "Shadowblood Ridge", "Sulfurous Springs", "Swamp", "Tainted Peak"}
_orig_pt2 = V.play_turn


def _play_turn_b(state, is_first_turn, on_play):
    _orig_pt2(state, is_first_turn, on_play)
    if getattr(state, "b4_turn", None) is None and V.total_mana(state) >= 4:
        if any(n in B_LANDS for n in state.battlefield) or "Arcane Signet" in state.battlefield or state.treasures > 0:
            state.b4_turn = state.turn


V.play_turn = _play_turn_b


def apply_swap(pairs):
    return pairs or None


def summarize(s):
    return {
        "win_turn": s.win_turn,
        "revel_turn": s.revel_condition_met_turn,
        "cmd_turn": s.commander_cast_turn,
        "treasures": s.treasures_created_total,
        "treasures_sacrificed": s.treasures_sacrificed_total,
        "drain": s.drain_damage_total,
        "table_dmg": s.table_damage_total,
        "combat": s.combat_damage_proxy_total,
        "removal": s.removal_cast_total,
        "life_gained": s.life_gained_total,
        "cards_extra": s.cards_drawn_extra,
        "magda_dragons": s.magda_dragons_created_total,
        "clues": s.clues_created_total,
        "foods": s.foods_created_total,
        "treasures_end": s.treasures,
        "kp_cast_turn": getattr(s, "kp_cast_turn", None),
        "kp_triggers": getattr(s, "kp_triggers", 0),
        "kp_treasures": getattr(s, "kp_treasures", 0),
        "kp_deliberate": getattr(s, "kp_deliberate", 0),
        "b4_turn": getattr(s, "b4_turn", None),
        "mulligans": s.mulligans,
    }


def run_variant(args):
    pairs, seeds, turns = args
    return [summarize(V.simulate_one(sd, turns, swap=(pairs or None))) for sd in seeds]
