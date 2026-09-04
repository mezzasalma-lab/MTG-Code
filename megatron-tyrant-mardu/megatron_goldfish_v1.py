"""
Goldfish simulator — Megatron, Tyrant (Mardu, B/R/W)
RECONSTRUCAO COMPLETA 2026-09-02.

A versao anterior deste arquivo (motor "Megatron sacrifica combustivel
barato todo turno") foi montada a partir de frequencia entre decklists
publicas + primer de comunidade. O dono real do deck (o oponente citado
nas partidas presenciadas pelo usuario) passou a lista inicial dele, e
comparando ficou claro que o plano de jogo real e' outro por completo:

    SOLDA/RECUPERA ARTEFATO (Goblin Welder, Trash for Treasure, Scrap
    Welder, Scrap Trawler, Daretti Scrap Savant, Daretti Rocketeer
    Engineer) + CHEAT PRA CAMPO (Sneak Attack, Anrakyr the Traveller,
    Feldon of the Third Path) + WARSTORM SURGE como motor de dano
    ("whenever a creature you control enters, it deals damage equal to
    its power to any target" -- dispara em TODO ETB de criatura, nao so'
    em ataque).

Ver `references/goldfish-sim-card-rules.md` (checklist de 13 categorias)
e `references/user-standing-rules.md`. Lista final e a decisao carta a
carta (8 cortes da lista original + 8 adicoes confirmadas + terrenos
premium ABUR) em `lista.md`, `checklist-oraculo.md` e `goldfish-log.md`.

======================================================================
MECANICA REAL DO MEGATRON (inalterada da versao anterior, ja verificada
via Scryfall)
======================================================================
Megatron e' um DFC `transform`: frente ("Tyrant", {3}{R}{W}{B} ou MTMTE
{1}{R}{W}{B}, 7/5) "opponents can't cast spells during combat" +
converte no postcombat main gerando mana = vida perdida pelos
oponentes no turno; verso ("Destructive Force", Vehicle 4/5) ataca e
pode sacrificar OUTRO artefato pra causar dano = MV desse artefato,
convertendo pra Tyrant no meio do combate. So' o Megatron ataca de
verdade nesse motor (mesma convencao da versao anterior) -- o resto do
dano real vem do motor NOVO: Warstorm Surge disparando em cada ETB de
criatura gerado pelos efeitos de cheat/solda/reanimacao.

Simplificacoes documentadas (nao inventadas -- omissoes explicitas):
- Sem oponente real: todo dano/perda-de-vida direcionado a oponente e'
  PROXY agregado (`NUM_OPPONENTS=3`, mesma convencao de todos os
  simuladores desta biblioteca).
- So' o Megatron ataca de verdade (combate real, sem bloqueio) -- as
  outras criaturas geram valor via ETB (Warstorm Surge) e sacrificio,
  nao via combate. Isso e' uma escolha de escopo, nao um limite do
  oraculo: nada na lista real do dono exige uma segunda criatura
  atacando pra funcionar (o motor de dano e' Warstorm Surge, nao
  combate multiplo).
- Efeitos "target opponent"/"each opponent" sempre multiplicados por
  NUM_OPPONENTS quando o oraculo diz "each opponent"; mantidos como
  valor unico quando diz "target opponent" (so' 1 oponente).
- Remocao/interacao sem alvo real de oponente (Path to Exile, Swords to
  Plowshares, Chaos Warp, Vandalblast) conjurada quando ha mana sobrando
  e conta como interaction_spells_cast, mesma convencao de toda a sessao.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import random

# ---------------------------------------------------------------------------
# Infra de cartas
# ---------------------------------------------------------------------------

@dataclass
class Card:
    name: str
    mv: int
    ctype: str  # "creature" | "artifact" | "enchantment" | "sorcery" | "instant" | "land" | "planeswalker"
    tags: frozenset = field(default_factory=frozenset)
    power: int = 0
    toughness: int = 0
    pips: dict = field(default_factory=dict)
    produces: frozenset = field(default_factory=frozenset)


CARD_DB: dict = {}


def add(name, mv, ctype, tags=(), power=0, toughness=0, pips=None, produces=None):
    CARD_DB[name] = Card(name=name, mv=mv, ctype=ctype, tags=frozenset(tags),
                          power=power, toughness=toughness,
                          pips=dict(pips or {}), produces=frozenset(produces or ()))


COMMANDER = "Megatron, Tyrant"
# Frente (Tyrant): {3}{R}{W}{B}, mv real 6. Custo MTMTE (verso, Destructive
# Force): {1}{R}{W}{B}, mv 4 -- registrado a parte em MEGATRON_* abaixo,
# ja' que o simulador escolhe qual face conjurar dinamicamente (mesmo
# padrao da versao anterior).
add(COMMANDER, 6, "creature", {"commander", "artifact"}, power=7, toughness=5, pips={"R": 1, "W": 1, "B": 1})
MEGATRON_TYRANT_COST = 6
MEGATRON_TYRANT_POWER = 7
MEGATRON_VEHICLE_COST = 4  # MTMTE
MEGATRON_VEHICLE_POWER = 4
MEGATRON_PIPS = {"R": 1, "W": 1, "B": 1}

NUM_OPPONENTS = 3  # premissa declarada (mesa de 4), nunca vida real rastreada

# --- Mana / rampa ------------------------------------------------------------
add("Sol Ring", 1, "artifact", {"rock2"})
add("Arcane Signet", 2, "artifact", {"rock1"}, produces=set("WUBRG"))
add("Fellwar Stone", 2, "artifact", {"rock1"}, produces=set("WUBRG"))
add("Mind Stone", 2, "artifact", {"rock1", "fuel_rock1"})
add("Talisman of Conviction", 2, "artifact", {"rock1"}, produces={"R", "W"})
add("Talisman of Hierarchy", 2, "artifact", {"rock1"}, produces={"W", "B"})
add("Talisman of Indulgence", 2, "artifact", {"rock1"}, produces={"B", "R"})
add("Gilded Lotus", 5, "artifact", {"rock3"}, produces=set("WUBRG"))
add("The Eternity Elevator", 5, "artifact", {"rock3", "station"}, pips={})

# --- Motor central: solda / recuperacao de artefato --------------------------
add("Goblin Welder", 1, "creature", {"welder"}, power=1, toughness=1, pips={"R": 1})
add("Goblin Engineer", 2, "creature", {"goblin_engineer"}, power=1, toughness=2, pips={"R": 1})
add("Myr Retriever", 2, "creature", {"artifact", "toolbox_recur"}, power=1, toughness=1, pips={})
add("Junk Diver", 3, "creature", {"artifact", "toolbox_recur"}, power=1, toughness=1, pips={})
add("Scrap Trawler", 3, "creature", {"artifact", "scrap_trawler"}, power=3, toughness=2, pips={})
add("Scrap Welder", 3, "creature", {"scrap_welder"}, power=3, toughness=3, pips={"R": 1})
add("Feldon of the Third Path", 3, "creature", {"feldon"}, power=2, toughness=3, pips={"R": 2})
add("Trash for Treasure", 3, "sorcery", {"trash_for_treasure"}, pips={"R": 1})
add("Daretti, Scrap Savant", 4, "planeswalker", {"daretti_savant"}, pips={"R": 1})
add("Anrakyr the Traveller", 5, "creature", {"artifact", "anrakyr"}, power=4, toughness=4, pips={"B": 1})
add("Daretti, Rocketeer Engineer", 5, "creature", {"daretti_rocketeer"}, power=0, toughness=5, pips={"R": 1})
add("Mishra, Tamer of Mak Fawa", 5, "creature", {"mishra_unearth_all"}, power=4, toughness=4, pips={"B": 1, "R": 1})
add("Osgir, the Reconstructor", 4, "creature", {"osgir_clone"}, power=4, toughness=4, pips={"R": 1, "W": 1})  # Achado real 2026-09-04: NAO e' artefato (Legendary Creature -- Giant Artificer), so' cuida de artefato

# --- Cheat pra campo -----------------------------------------------------------
add("Sneak Attack", 4, "enchantment", {"sneak_attack"}, pips={"R": 1})

# --- Sacrificio / payoff -------------------------------------------------------
add("Ayara, Widow of the Realm", 3, "creature", {"ayara"}, power=3, toughness=3, pips={"B": 2})
add("Rakdos, the Muscle", 5, "creature", {"rakdos_sac_creature"}, power=6, toughness=5, pips={"B": 2, "R": 1})
add("Pia's Revolution", 3, "enchantment", {"pia_revolution"}, pips={"R": 1})  # Achado real 2026-09-04 (EDHREC)

# --- Corpo grande / finalizadores (fodder real pro motor de solda/cheat) ------
add("Cursed Mirror", 3, "artifact", {"fuel_rock1", "cursed_mirror_clone"}, pips={"R": 1}, produces={"R"})
add("Solemn Simulacrum", 4, "creature", {"artifact", "solemn"}, power=2, toughness=2, pips={})
add("Ironsoul Enforcer", 5, "creature", {"artifact", "ironsoul"}, power=4, toughness=4, pips={"W": 1})
add("Combustible Gearhulk", 6, "creature", {"artifact", "combustible_gearhulk"}, power=6, toughness=6, pips={"R": 2})
add("Noxious Gearhulk", 6, "creature", {"artifact", "noxious_gearhulk"}, power=5, toughness=4, pips={"B": 2})
add("Steel Seraph", 6, "creature", {"artifact", "steel_seraph"}, power=5, toughness=4, pips={"W": 1})
add("Demonic Junker", 7, "creature", {"artifact", "demonic_junker"}, power=4, toughness=3, pips={"B": 1})
add("Bygone Colossus", 9, "creature", {"artifact", "warp3"}, power=9, toughness=9, pips={})
add("Phyrexian Triniform", 9, "creature", {"artifact", "triniform_death_tokens"}, power=9, toughness=9, pips={})
add("Skitterbeam Battalion", 9, "creature", {"artifact", "skitterbeam"}, power=4, toughness=4, pips={})
add("Summon: Bahamut", 9, "creature", {"saga_bahamut"}, power=9, toughness=9, pips={})
add("Metalwork Colossus", 11, "creature", {"artifact", "metalwork_colossus"}, power=10, toughness=10, pips={})

# --- Artefatos de valor continuo ----------------------------------------------
add("Nexus of Becoming", 6, "artifact", {"nexus_combat_draw_copy"}, pips={})
add("God-Pharaoh's Statue", 6, "artifact", {"god_pharaoh_statue"}, pips={})
add("Mirrorworks", 5, "artifact", {"mirrorworks"}, pips={})
add("Portal to Phyrexia", 9, "artifact", {"portal_phyrexia"}, pips={})
add("Warstorm Surge", 6, "enchantment", {"warstorm_surge"}, pips={"R": 1})
add("Brass's Tunnel-Grinder", 3, "artifact", {"tunnel_grinder"}, pips={"R": 1})
add("Cosmic Cube", 5, "artifact", {"cosmic_cube"}, pips={})  # Achado real 2026-09-03

# --- Draw / filtragem ----------------------------------------------------------
add("Faithless Looting", 1, "sorcery", {"loot2_2_flashback"}, pips={"R": 1})
add("Demand Answers", 2, "instant", {"demand_answers"}, pips={"R": 1})
add("Laughing Mad", 3, "instant", {"loot1_2_flashback"}, pips={"R": 1})
add("Wheel of Fortune", 3, "sorcery", {"wheel_full"}, pips={"R": 1})
add("Black Market Connections", 3, "enchantment", {"black_market"}, pips={"B": 1})
add("Saheeli's Directive", 3, "sorcery", {"saheeli_directive"}, pips={"R": 3})
add("Phyrexian Arena", 3, "enchantment", {"phyrexian_arena"}, pips={"B": 2})  # Achado real 2026-09-03

# --- Removal / interacao (sem alvo real de oponente) ---------------------------
add("Path to Exile", 1, "instant", {"interaction"}, pips={"W": 1})
add("Swords to Plowshares", 1, "instant", {"interaction"}, pips={"W": 1})
add("Vandalblast", 1, "sorcery", {"interaction"}, pips={"R": 1})
add("Chaos Warp", 3, "instant", {"interaction"}, pips={"R": 1})
add("Decree of Pain", 8, "sorcery", {"decree_of_pain"}, pips={"B": 2})
add("Heartless Conscription", 8, "sorcery", {"heartless_conscription"}, pips={"B": 2})
add("Blasphemous Act", 9, "sorcery", {"wipe_reduces_creatures"}, pips={"R": 1})
add("Chandra's Ignition", 5, "sorcery", {"chandras_ignition"}, pips={"R": 2})

# --- Protecao / equipment --------------------------------------------------------
add("Lightning Greaves", 2, "artifact", {"haste_shroud_equip"}, pips={})
add("Swiftfoot Boots", 2, "artifact", {"hexproof_haste_equip"}, pips={})
add("Clever Concealment", 4, "instant", {"clever_concealment"}, pips={"W": 2})  # Achado real
# 2026-09-02: Shields Up! e' do set Star Trek, lancamento 2026-11-13 --
# usuario apontou que ainda nao foi lancada (nao e' legal em Commander
# ainda). Substituida primeiro por Loran's Escape (protege so' 1
# permanente), depois trocada de novo por pedido direto do usuario pra
# Clever Concealment (Marvel Super Heroes Commander, 2026-06-26, real e
# legal): "{2}{W}{W}, Convoke -- any number of target nonland permanents
# you control phase out." Protege o board INTEIRO contra wrath (nao so'
# 1 peca), custo efetivo baixo na pratica ja' que Convoke tapa fodder que
# ia ser sacrificado no fim do turno mesmo (Sneak Attack/Feldon).
add("Blacksmith's Skill", 1, "instant", {"blacksmiths_skill"}, pips={"W": 1})

# --- Ataque solo -------------------------------------------------------------
add("Ragavan, Nimble Pilferer", 1, "creature", {"ragavan"}, power=2, toughness=1, pips={"R": 1})
add("Treasure Nabber", 3, "creature", {"opponent_dependent"}, power=3, toughness=2, pips={"R": 1})

# --- Terrenos --------------------------------------------------------------------
LAND_BASIC_TYPES = {
    "Plateau": {"Mountain", "Plains"}, "Scrubland": {"Plains", "Swamp"}, "Badlands": {"Swamp", "Mountain"},
    "Smoldering Marsh": {"Swamp", "Mountain"},
    "Mountain": {"Mountain"}, "Plains": {"Plains"}, "Swamp": {"Swamp"},
}
add("Adagia, Windswept Bastion", 0, "land", {"station", "adagia_copy"}, produces={"W"})
add("Ash Barrens", 0, "land", {"ash_barrens"}, produces=set())
add("Badlands", 0, "land", set(), produces={"B", "R"})
add("Command Tower", 0, "land", set(), produces={"W", "B", "R"})
add("Exotic Orchard", 0, "land", set(), produces={"W", "B", "R"})
add("Forbidden Orchard", 0, "land", set(), produces={"W", "B", "R"})
add("Plateau", 0, "land", set(), produces={"R", "W"})
add("Scrubland", 0, "land", set(), produces={"W", "B"})
add("Smoldering Marsh", 0, "land", {"etb_tapped_check"}, produces={"B", "R"})
add("Susur Secundi, Void Altar", 0, "land", {"station", "etb_tapped"}, produces={"B"})
add("Mountain", 0, "land", set(), produces={"R"})
add("Plains", 0, "land", set(), produces={"W"})
add("Swamp", 0, "land", set(), produces={"B"})

LAND_NAMES = {n for n, c in CARD_DB.items() if c.ctype == "land"}
ETB_TAPPED_LANDS = {"Smoldering Marsh", "Susur Secundi, Void Altar"}  # Smoldering so' se <2 terrenos; Susur sempre


def is_creature_card(name: str) -> bool:
    return CARD_DB[name].ctype == "creature"


def is_artifact_card(name: str) -> bool:
    return "artifact" in CARD_DB[name].tags or CARD_DB[name].ctype == "artifact"


LEGENDARY_NAMES = {
    "Megatron, Tyrant", "Ayara, Widow of the Realm", "Feldon of the Third Path",
    "Daretti, Scrap Savant", "Daretti, Rocketeer Engineer", "Anrakyr the Traveller",
    "Mishra, Tamer of Mak Fawa", "Osgir, the Reconstructor", "Rakdos, the Muscle",
    "Brass's Tunnel-Grinder", "God-Pharaoh's Statue", "The Eternity Elevator",
    "Ragavan, Nimble Pilferer", "Adagia, Windswept Bastion", "Susur Secundi, Void Altar",
}


def is_legendary(name: str) -> bool:
    return name in LEGENDARY_NAMES


def is_historic(name: str) -> bool:
    return is_artifact_card(name) or is_legendary(name) or "saga_bahamut" in CARD_DB[name].tags


def build_library():
    import re
    entries = []
    section = None
    with open("lista.md") as f:
        for line in f:
            s = line.strip()
            if s.startswith("## Comandante"):
                section = "cmd"
                continue
            if s.startswith("## Deck"):
                section = "deck"
                continue
            if s.startswith("## Terrenos"):
                section = "land"
                continue
            m = re.match(r'^(\d+)\s+(.+)$', s)
            if not m or section == "cmd":
                continue
            n, name = int(m.group(1)), m.group(2)
            entries.extend([name] * n)
    return entries


BASE_LIBRARY = build_library()


# ---------------------------------------------------------------------------
# Estado de jogo
# ---------------------------------------------------------------------------

@dataclass
class GameState:
    turn: int = 0
    hand: list = field(default_factory=list)
    battlefield: list = field(default_factory=list)
    graveyard: list = field(default_factory=list)
    library: list = field(default_factory=list)
    exile: list = field(default_factory=list)
    mulligans: int = 0

    lands_played_this_turn: int = 0
    tapped_land_this_turn: Optional[str] = None
    mana_spent_this_turn: int = 0
    bonus_mana_pool: int = 0
    creature_cast_turn: dict = field(default_factory=dict)
    extra_turns_pending: int = 0

    commander_in_play: bool = False
    commander_cast_count: int = 0
    commander_cast_turn: Optional[int] = None
    megatron_face: Optional[str] = None  # "vehicle" ou "tyrant"
    life_lost_by_opponents_this_turn: int = 0
    life: int = 40

    # --- motor novo: solda/cheat/sacrificio/Warstorm Surge --------------------
    daretti_savant_loyalty: int = 0
    daretti_savant_ultimate_active: bool = False
    ayara_transformed: bool = False
    ayara_recur_used_this_turn: bool = False
    goblin_welder_used_this_turn: bool = False
    scrap_welder_used_this_turn: bool = False
    feldon_used_this_turn: bool = False
    sneak_attack_used_this_turn: bool = False
    anrakyr_attack_used_this_turn: bool = False
    goblin_engineer_used_this_turn: bool = False
    mishra_unearth_used_this_turn: bool = False
    osgir_used_this_turn: bool = False
    nexus_used_this_turn: bool = False
    black_market_used_this_turn: bool = False
    losheel_draw_used_this_turn: bool = False
    adagia_copy_used_this_turn: bool = False
    susur_secundi_used_this_turn: bool = False
    god_pharaoh_statue_pinged_this_turn: bool = False
    attackers_this_combat: int = 0
    attackers_total_all_turns: int = 0  # soma de todos os combates, pra metrica de run_batch
    max_attacker_power_this_combat: int = 0  # pro gatilho do Cosmic Cube
    charge_counters: dict = field(default_factory=dict)  # nome do Planet -> contadores
    bygone_colossus_exiled_warp: bool = False
    daretti_rocketeer_mv_seen: int = 0
    temp_creatures_pending_sacrifice: list = field(default_factory=list)
    temp_creatures_pending_exile: list = field(default_factory=list)
    daretti_emblem_pending_return: list = field(default_factory=list)
    triniform_tokens_total: int = 0

    # metrics -----------------------------------------------------------------
    proxy_damage_total: int = 0
    proxy_lifegain_total: int = 0
    cards_drawn_extra: int = 0
    tutors_used_total: int = 0
    ramp_pieces_cast_total: int = 0
    interaction_spells_cast_total: int = 0
    recursion_events_total: int = 0
    megatron_conversions_total: int = 0
    megatron_mana_generated_total: int = 0
    megatron_fuel_sacrificed_total: int = 0
    wheels_total: int = 0
    library_emptied: bool = False
    warstorm_surge_damage_total: int = 0
    warstorm_surge_triggers_total: int = 0
    weld_activations_total: int = 0
    creatures_cheated_in_total: int = 0
    sacrifice_payoff_damage_total: int = 0
    sacrifice_payoff_draws_total: int = 0
    artifacts_sacrificed_total: int = 0
    creatures_sacrificed_total: int = 0
    daretti_savant_minus10_active: bool = False
    cosmic_cube_free_casts_total: int = 0
    phyrexian_arena_life_lost_total: int = 0
    nexus_tokens_created_total: int = 0
    equip_haste_activations_total: int = 0
    pia_revolution_returns_total: int = 0


def draw_cards(state: GameState, n: int):
    for _ in range(n):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1
        else:
            state.library_emptied = True


def proxy_drain(state: GameState, n: int):
    state.proxy_damage_total += n
    state.life_lost_by_opponents_this_turn += n


def self_damage(state: GameState, n: int):
    state.life -= n


def gain_life(state: GameState, n: int):
    state.life += n
    state.proxy_lifegain_total += n


def worst_discard_target(state: GameState, pool: list = None):
    """Escolhe a pior carta pra descartar (Faithless Looting/Laughing Mad/
    limite de mao no fim do turno). Achado real ao testar: escolher so'
    por MENOR mana value (como o resto do arquivo faz em varios lugares)
    tratava terrenos (MV 0) como sempre "a pior carta" -- looting
    descartava os proprios terrenos da mao antes de conseguirem ser
    jogados, travando o desenvolvimento de mana da partida inteira.
    Corrigido: nunca descarta terreno enquanto houver menos de 6 em campo
    E houver alguma carta nao-terreno pra descartar no lugar; alagado
    (6+ terrenos), terreno volta a ser descartavel normalmente."""
    candidates = pool if pool is not None else state.hand
    if not candidates:
        return None
    lands_in_play = sum(1 for n in state.battlefield if n in LAND_NAMES)
    nonlands = [c for c in candidates if c not in LAND_NAMES]
    if nonlands and lands_in_play < 6:
        return min(nonlands, key=lambda n: CARD_DB[n].mv if n in CARD_DB else 0)
    return min(candidates, key=lambda n: CARD_DB[n].mv if n in CARD_DB else 0)


def rocks_mana(state: GameState) -> int:
    total = 0
    if "Sol Ring" in state.battlefield:
        total += 2
    for n in ("Arcane Signet", "Fellwar Stone", "Mind Stone",
              "Talisman of Conviction", "Talisman of Hierarchy", "Talisman of Indulgence"):
        if n in state.battlefield:
            total += 1
    if "Gilded Lotus" in state.battlefield:
        total += 3
    if "Cursed Mirror" in state.battlefield:
        total += 1
    if "The Eternity Elevator" in state.battlefield:
        total += 3
    return total


def total_mana(state: GameState) -> int:
    lands = sum(1 for n in state.battlefield if n in LAND_NAMES)
    if state.tapped_land_this_turn is not None:
        lands -= 1
    return lands + rocks_mana(state) + state.bonus_mana_pool


def remaining_mana(state: GameState) -> int:
    return max(0, total_mana(state) - state.mana_spent_this_turn)


def color_sources(state: GameState, color: str, spell_name: str = None) -> int:
    n = 0
    for card in state.battlefield:
        if card not in CARD_DB:
            continue
        if card == state.tapped_land_this_turn:
            continue
        c = CARD_DB[card]
        if color in c.produces:
            n += 1
    return n


def has_color_sources_for(state: GameState, name: str) -> bool:
    for color, needed in CARD_DB[name].pips.items():
        if color_sources(state, color) < needed:
            return False
    return True


def effective_cost(state: GameState, name: str) -> int:
    mv = CARD_DB[name].mv
    return mv


def can_cast(state: GameState, name: str) -> bool:
    return remaining_mana(state) >= effective_cost(state, name) and has_color_sources_for(state, name)


def spend_mana(state: GameState, n: int):
    state.mana_spent_this_turn += n


def ready_creatures(state: GameState):
    return [n for n in state.battlefield if is_creature_card(n)
            and (state.creature_cast_turn.get(n, -1) < state.turn)]



# ---------------------------------------------------------------------------
# Infra central: ETB (com Warstorm Surge), sacrificio, gatilhos de morte
# ---------------------------------------------------------------------------

def get_power(state: GameState, name: str) -> int:
    """Poder real de uma criatura, com override pras dinamicas (Daretti,
    Rocketeer Engineer: 'power is equal to the greatest mana value among
    artifacts you control')."""
    if name == "Daretti, Rocketeer Engineer":
        mvs = [CARD_DB[n].mv for n in state.battlefield if is_artifact_card(n) and n != name]
        return max(mvs, default=0)
    return CARD_DB[name].power


def creature_enters(state: GameState, name: str, from_hand: bool = True, token: bool = False):
    """Ponto central de TODA criatura entrando em campo -- cast normal,
    token (Feldon/Skitterbeam/Osgir/Triniform), ou reanimacao (Trash for
    Treasure/Ayara-flip/Anrakyr/Mishra unearth/Portal to Phyrexia). Dispara
    Warstorm Surge aqui, no unico lugar real do arquivo onde ETB de
    criatura acontece -- garante que NENHUM ponto de entrada escape do
    gatilho ('whenever a creature you control enters, it deals damage
    equal to its power to any target')."""
    if from_hand and name in state.hand:
        state.hand.remove(name)
    state.battlefield.append(name)
    if is_creature_card(name):
        state.creature_cast_turn[name] = state.turn
        if "Warstorm Surge" in state.battlefield:
            power = get_power(state, name)
            if power > 0:
                proxy_drain(state, power)
                state.warstorm_surge_damage_total += power
                state.warstorm_surge_triggers_total += 1
    resolve_etb(state, name, token=token)
    if is_artifact_card(name):
        artifact_etb_hooks(state, name, token=token)


def sacrifice(state: GameState, name: str):
    """Ponto central de TODO sacrificio do arquivo -- remove de
    battlefield, poe no graveyard, dispara os gatilhos reais de morte
    (Scrap Trawler, toolbox Junk Diver, Phyrexian Triniform, Solemn
    Simulacrum) e os payoffs que disparam em QUALQUER
    sacrificio de criatura (Rakdos, the Muscle -- 'whenever you sacrifice
    another creature', gatilho automatico, nao e' escolha)."""
    if name not in state.battlefield:
        return
    state.battlefield.remove(name)
    state.graveyard.append(name)
    if name in state.temp_creatures_pending_sacrifice:
        state.temp_creatures_pending_sacrifice.remove(name)
    was_creature = is_creature_card(name)
    was_artifact = is_artifact_card(name)
    if was_artifact:
        state.artifacts_sacrificed_total += 1
        scrap_trawler_trigger(state, name)
        daretti_ultimate_recursion_check(state, name)
        pia_revolution_trigger(state, name)
    if was_creature:
        state.creatures_sacrificed_total += 1
    death_trigger(state, name)
    if was_creature and name != "Rakdos, the Muscle" and "Rakdos, the Muscle" in state.battlefield:
        rakdos_muscle_trigger(state, name)


def pia_revolution_trigger(state: GameState, dying_name: str):
    """Pia's Revolution: 'Whenever a nontoken artifact is put into your
    graveyard from the battlefield, return that card to your hand unless
    target opponent has this enchantment deal 3 damage to them.' Achado
    real 2026-09-04 (EDHREC: card mais jogado com o Megatron entre as
    enchantments, 41,6% dos decks -- validado por dado real de jogadores,
    nao so' por oraculo). Sempre escolhe devolver pra mao: vantagem de
    cartas > 3 de dano proxy aqui, ja que o deck reaproveita fartamente
    artefato reciclado (fuel do Megatron/fodder de solda de novo), e o
    combate ja alimenta `life_lost_by_opponents_this_turn` de sobra sem
    precisar desses 3 pontos extras. So' dispara pra artefato NAO-token
    (token deixa de existir ao mudar de zona pelas regras reais -- ver
    `is_token_name`)."""
    if "Pia's Revolution" not in state.battlefield or is_token_name(dying_name):
        return
    if dying_name not in state.graveyard:
        return
    state.graveyard.remove(dying_name)
    state.hand.append(dying_name)
    state.pia_revolution_returns_total += 1


def scrap_trawler_trigger(state: GameState, dying_name: str):
    """'Whenever this creature dies or another artifact you control is
    put into a graveyard from the battlefield, return to your hand
    target artifact card in your graveyard with lesser mana value.'"""
    if dying_name != "Scrap Trawler" and "Scrap Trawler" not in state.battlefield:
        return
    dying_mv = CARD_DB[dying_name].mv
    pool = [c for c in state.graveyard if c != dying_name and is_artifact_card(c) and CARD_DB[c].mv < dying_mv]
    if not pool:
        return
    best = max(pool, key=lambda n: CARD_DB[n].mv)
    state.graveyard.remove(best)
    state.hand.append(best)
    state.recursion_events_total += 1


def rakdos_muscle_trigger(state: GameState, dying_name: str):
    """'Whenever you sacrifice another creature, exile cards equal to its
    mana value from the top of target player's library. Until your next
    end step, you may play those cards, and mana of any type can be
    spent to cast those spells.' Alvo = minha propria biblioteca (premissa
    documentada: maximiza valor pra mim). Aproximado como impulso de
    compra direta -- mesma convencao ja usada nesta sessao pra efeitos de
    'exile and may play' (Sandstone Oracle, Portal to Phyrexia etc), ja
    que o arquivo nao rastreia uma 'mao exilada temporaria' separada em
    lugar nenhum."""
    mv = CARD_DB[dying_name].mv
    if mv <= 0:
        return
    draw_cards(state, mv)
    state.sacrifice_payoff_draws_total += mv


def death_trigger(state: GameState, dying_name: str):
    """Gatilhos reais de 'quando isso morre' que nao sao o Scrap Trawler
    nem o Rakdos (esses sao genericos, ja tratados em `sacrifice()`)."""
    if dying_name == "Phyrexian Triniform":
        token_name = "Phyrexian Golem Token"
        if token_name not in CARD_DB:
            add(token_name, 0, "creature", {"artifact"}, power=3, toughness=3)
        for _ in range(3):
            creature_enters(state, token_name, from_hand=False, token=True)
        state.triniform_tokens_total += 3
    if dying_name == "Solemn Simulacrum":
        draw_cards(state, 1)
    if dying_name in ("Myr Retriever", "Junk Diver"):
        pool = [c for c in state.graveyard if c != dying_name and is_artifact_card(c)]
        if pool:
            best = max(pool, key=lambda n: CARD_DB[n].mv)
            state.graveyard.remove(best)
            state.hand.append(best)
            state.recursion_events_total += 1


def best_weld_fodder(state: GameState, min_mv: int = 0):
    """Escolha de qual artefato sacrificar quando o objetivo e' 'trocar
    algo barato por algo melhor do cemiterio' (Goblin Welder/Trash for
    Treasure/Scrap Welder/Daretti/Metalwork Colossus). Prioriza SEMPRE
    uma criatura temporaria pendente de sacrificio no fim do turno
    (Sneak Attack/Feldon -- e' literalmente gratis, ela ia morrer de
    qualquer jeito); senao, o artefato de MENOR custo de mana disponivel
    (mantem os grandes em campo), excluindo o Megatron e o proprio
    Warstorm Surge/rocks continuos de valor alto."""
    for n in state.temp_creatures_pending_sacrifice:
        if n in state.battlefield and is_artifact_card(n):
            return n
    KEEP_ALWAYS = {COMMANDER, "Warstorm Surge", "Sneak Attack", "Daretti, Scrap Savant"}
    candidates = [n for n in state.battlefield
                  if n not in KEEP_ALWAYS and is_artifact_card(n) and CARD_DB[n].mv >= min_mv]
    if not candidates:
        return None
    candidates.sort(key=lambda n: CARD_DB[n].mv)
    return candidates[0]


def best_megatron_fuel(state: GameState):
    """Escolha de qual artefato o proprio Megatron sacrifica como fuel
    (Destructive Force: 'deals damage equal to the sacrificed artifact's
    mana value'). Achado real 2026-09-02 (revendo o log de goldfish real
    do usuario -- ele sacrificou o God-Pharaoh's Statue, MV 6, o maior
    artefato disponivel, maximizando o dano): `megatron_combat()` estava
    reaproveitando `best_weld_fodder()`, que faz o OPOSTO de proposito
    (pega o MENOR MV, pra sobrar os grandes em campo pra solda) --
    fazendo o Megatron sacrificar sempre o artefato MAIS FRACO como fuel,
    ao contrario da estrategia real do primer ("prioriza o artefato de
    MAIOR custo de mana"). Corrigido com selecao propria, descendente."""
    for n in state.temp_creatures_pending_sacrifice:
        if n in state.battlefield and is_artifact_card(n):
            return n
    KEEP_ALWAYS = {COMMANDER, "Warstorm Surge", "Sneak Attack", "Daretti, Scrap Savant"}
    candidates = [n for n in state.battlefield if n not in KEEP_ALWAYS and is_artifact_card(n)]
    if not candidates:
        return None
    candidates.sort(key=lambda n: -CARD_DB[n].mv)
    return candidates[0]


def best_payoff_fodder(state: GameState):
    """Fodder pros payoffs de sacrificio 'livres' (Ayara, Susur Secundi,
    Altar of the Wretched) -- so' consome criaturas temporarias que iam
    morrer de qualquer jeito no fim do turno (nunca sacrifica board real
    por esses payoffs; a decisao de trocar valor permanente por dano/
    vida/compra fica fora de escopo de uma heuristica de goldfish)."""
    for n in state.temp_creatures_pending_sacrifice:
        if n in state.battlefield:
            return n
    return None


def artifact_etb_hooks(state: GameState, name: str, token: bool = False):
    """Mirrorworks: 'whenever another NONTOKEN artifact you control
    enters, you may pay {2}. If you do, create a token that's a copy of
    that artifact.' Escolhe pagar sempre que sobra mana e o artefato tem
    valor real de copia (MV>=3 -- nao vale a pena copiar coisa barata tipo
    Sol Ring/talisman por 2 mana). `token=True` (a propria entrada e' de
    um token, ex: copia do Mirrorworks/Osgir/Feldon/Skitterbeam) precisa
    ficar de fora -- senao um token de MV alto copiando a si mesmo via
    Mirrorworks entra em recursao infinita (achado real ao testar)."""
    if token or name == "Mirrorworks" or "Mirrorworks" not in state.battlefield:
        return
    if CARD_DB[name].mv < 3:
        return
    if remaining_mana(state) < 2:
        return
    spend_mana(state, 2)
    token_name = make_token_copy_name(name)
    if is_creature_card(name):
        creature_enters(state, token_name, from_hand=False, token=True)
    else:
        state.battlefield.append(token_name)
        resolve_etb(state, token_name)
    state.recursion_events_total += 1


def make_token_copy_name(base_name: str) -> str:
    token_name = base_name + " (copia)"
    if token_name not in CARD_DB:
        CARD_DB[token_name] = CARD_DB[base_name]
    return token_name


TOKEN_FIXED_NAMES = {"Phyrexian Golem Token", "Nexus Golem Token", "Shapeshifter Token"}


def is_token_name(name: str) -> bool:
    """Distingue token de carta real -- necessario pro Pia's Revolution
    ('nontoken artifact'). Cobre tanto os tokens-copia dinamicos
    (`make_token_copy_name`, sufixo ' (copia)') quanto os tokens de nome
    fixo (Phyrexian Golem/Nexus Golem/Shapeshifter)."""
    return name.endswith(" (copia)") or name in TOKEN_FIXED_NAMES


def resolve_etb(state: GameState, name: str, token: bool = False):
    tags = CARD_DB[name].tags

    if "combustible_gearhulk" in tags:
        # "target opponent may have you draw three cards. If the player
        # doesn't, you mill three cards, then this deals damage = total MV
        # of those cards." Premissa: oponente NUNCA deixa eu comprar
        # (pior escolha pra ele), entao sempre milha e' dano real.
        milled = state.library[:3]
        state.library = state.library[3:]
        state.graveyard.extend(milled)
        dmg = sum(CARD_DB[c].mv for c in milled if c in CARD_DB)
        if dmg > 0:
            proxy_drain(state, dmg)

    if "noxious_gearhulk" in tags:
        # "may destroy another target creature; if destroyed, gain life
        # equal to its toughness." Sem criatura real de oponente pra
        # destruir -- 📊 estrutural (mesma convencao de etb_removal em
        # toda a sessao), sem efeito numerico.
        pass

    if "demonic_junker" in tags:
        # "for each player, destroy up to one target creature that player
        # controls. If a creature you controlled was destroyed, put two
        # +1/+1 counters." Nunca destruo a minha propria por escolha
        # (perde mais do que ganha) -- 📊, sem efeito numerico.
        pass

    if "skitterbeam" in tags and not token:
        # "When this creature enters, if you cast it [pelo custo cheio,
        # nao Prototype], create two tokens that are copies of it." O "if
        # you cast it" e' real e importante: um TOKEN copia de Skitterbeam
        # (por Mirrorworks/Osgir/Feldon/etc) nao foi CONJURADO, entao nao
        # dispara de novo -- sem o `and not token` aqui, um token copiando
        # a si mesmo entra em recursao infinita (achado real ao testar).
        # Premissa: sempre conjurado pelo custo cheio ({9}), nunca a
        # versao Prototype barata ({3}{R}{R}, 2/2) -- mesma convencao de
        # 'escolhe sempre a linha de maior valor' ja usada pro Boros
        # Charm/etc no arquivo anterior.
        for _ in range(2):
            creature_enters(state, make_token_copy_name(name), from_hand=False, token=True)

    if "saga_bahamut" in tags:
        state.bahamut_entered_turn = state.turn
        state.bahamut_chapter = 1
        # Capitulo I: destroy up to one target nonland permanent -- sem
        # alvo real de oponente, conta como interacao (mesma convencao).
        state.interaction_spells_cast_total += 1

    if "portal_phyrexia" in tags:
        # "each opponent sacrifices three creatures" -- sem board real de
        # oponente, conta como valor de bordo destruido (recursion_events,
        # nao dano numerico, mesma convencao ja usada nesta sessao).
        state.recursion_events_total += 1

    if "cursed_mirror_clone" in tags:
        # "may have it become a copy of any creature on the battlefield
        # until end of turn, except it has haste." Copia o Megatron (unica
        # criatura que ataca de verdade) e credita uma rajada extra
        # equivalente ao poder atual dele -- mesma logica ja usada na
        # versao anterior deste arquivo.
        if state.commander_in_play and COMMANDER in ready_creatures(state):
            power = MEGATRON_TYRANT_POWER if state.megatron_face == "tyrant" else MEGATRON_VEHICLE_POWER
            proxy_drain(state, power)

    if "tunnel_grinder" in tags:
        # "discard any number of cards, then draw that many plus one."
        # Premissa: descarta 0 (mantem a mao), compra so' o +1 garantido
        # -- sem avaliacao real de quais cartas valem descartar.
        draw_cards(state, 1)

    if "daretti_rocketeer" in tags:
        # "Whenever Daretti enters or attacks, choose target artifact
        # card in your graveyard. You may sacrifice an artifact. If you
        # do, return the chosen card to the battlefield." Metade de ETB
        # -- achado real 2026-09-02 (reauditoria pos-jogo real do
        # usuario): nunca tinha dispatch nenhum, nem essa nem a de
        # ataque (`daretti_rocketeer_attack_ability`, chamada em
        # `all_attackers_combat`).
        daretti_rocketeer_attack_ability(state)


# ---------------------------------------------------------------------------
# Solda / recuperacao de artefato
# ---------------------------------------------------------------------------

def try_goblin_welder(state: GameState):
    """'{T}: Choose target artifact a player controls and target artifact
    card in that player's graveyard. If both targets are still legal,
    that player simultaneously sacrifices the artifact and returns the
    artifact card to the battlefield.' So' faz sentido quando o artefato
    no cemiterio vale mais que o sacrificado -- so' ativa se achar um
    upgrade real (MV do alvo do cemiterio > MV do fodder)."""
    if "Goblin Welder" not in state.battlefield or "Goblin Welder" not in ready_creatures(state):
        return
    if state.goblin_welder_used_this_turn:
        return
    fodder = best_weld_fodder(state)
    if fodder is None:
        return
    gy_artifacts = [c for c in state.graveyard if is_artifact_card(c) and CARD_DB[c].mv > CARD_DB[fodder].mv]
    if not gy_artifacts:
        return
    target = max(gy_artifacts, key=lambda n: CARD_DB[n].mv)
    state.goblin_welder_used_this_turn = True
    sacrifice(state, fodder)
    if target not in state.graveyard:
        return  # o proprio sacrificio (ex: morte do toolbox) ja consumiu o alvo
    state.graveyard.remove(target)
    if is_creature_card(target):
        creature_enters(state, target, from_hand=False)
    else:
        state.battlefield.append(target)
        resolve_etb(state, target)
    state.weld_activations_total += 1


def try_scrap_welder(state: GameState):
    """'{T}, Sacrifice an artifact with mana value X: Return target
    artifact card with mana value less than X from your graveyard to the
    battlefield. It gains haste until end of turn.' Volta PERMANENTE
    (nao e' sacrificada de novo no fim do turno -- so' ganha haste)."""
    if "Scrap Welder" not in state.battlefield or "Scrap Welder" not in ready_creatures(state):
        return
    if state.scrap_welder_used_this_turn:
        return
    fodder = best_weld_fodder(state)
    if fodder is None:
        return
    gy_artifacts = [c for c in state.graveyard if is_artifact_card(c) and CARD_DB[c].mv < CARD_DB[fodder].mv]
    if not gy_artifacts:
        return
    target = max(gy_artifacts, key=lambda n: CARD_DB[n].mv)
    state.scrap_welder_used_this_turn = True
    sacrifice(state, fodder)
    if target not in state.graveyard:
        return
    state.graveyard.remove(target)
    if is_creature_card(target):
        creature_enters(state, target, from_hand=False)
        state.creature_cast_turn[target] = state.turn - 1  # haste: pronta ja'
    else:
        state.battlefield.append(target)
        resolve_etb(state, target)
    state.weld_activations_total += 1


def try_trash_for_treasure(state: GameState):
    """'As an additional cost to cast this spell, sacrifice an artifact.
    Return target artifact card from your graveyard to the battlefield.'
    Sorcery, sem limite de 1x/turno alem de estar na mao e' castavel."""
    if "Trash for Treasure" not in state.hand or not can_cast(state, "Trash for Treasure"):
        return
    fodder = best_weld_fodder(state)
    if fodder is None:
        return
    gy_artifacts = [c for c in state.graveyard if is_artifact_card(c) and c != fodder]
    if not gy_artifacts:
        return
    target = max(gy_artifacts, key=lambda n: CARD_DB[n].mv)
    if CARD_DB[target].mv <= CARD_DB[fodder].mv:
        return  # so' vale a pena se for upgrade real
    spend_mana(state, effective_cost(state, "Trash for Treasure"))
    state.hand.remove("Trash for Treasure")
    state.graveyard.append("Trash for Treasure")
    sacrifice(state, fodder)
    if target not in state.graveyard:
        return
    state.graveyard.remove(target)
    if is_creature_card(target):
        creature_enters(state, target, from_hand=False)
    else:
        state.battlefield.append(target)
        resolve_etb(state, target)
    state.weld_activations_total += 1


def try_metalwork_colossus_recursion(state: GameState):
    """'Sacrifice two artifacts: Return this card from your graveyard to
    your hand.' Confirma 2 candidatos ANTES de sacrificar (evita o caso
    do primeiro sacrificio consumir o unico candidato disponivel)."""
    if "Metalwork Colossus" not in state.graveyard:
        return
    KEEP_ALWAYS = {COMMANDER, "Warstorm Surge", "Sneak Attack", "Daretti, Scrap Savant"}
    candidates = sorted(
        [n for n in state.battlefield if n not in KEEP_ALWAYS and is_artifact_card(n)],
        key=lambda n: CARD_DB[n].mv,
    )
    if len(candidates) < 2:
        return
    sacrifice(state, candidates[0])
    sacrifice(state, candidates[1])
    if "Metalwork Colossus" not in state.graveyard:
        return  # um dos sacrificios (ex: morte do toolbox) ja devolveu ela pra mao
    state.graveyard.remove("Metalwork Colossus")
    state.hand.append("Metalwork Colossus")
    state.recursion_events_total += 1


def try_goblin_engineer_activation(state: GameState):
    """'{R}, {T}, Sacrifice an artifact: Return target artifact card with
    mana value 3 or less from your graveyard to the battlefield.'"""
    if "Goblin Engineer" not in state.battlefield or "Goblin Engineer" not in ready_creatures(state):
        return
    if state.goblin_engineer_used_this_turn or remaining_mana(state) < 1:
        return
    fodder = best_weld_fodder(state)
    if fodder is None:
        return
    gy_artifacts = [c for c in state.graveyard if is_artifact_card(c) and c != fodder and CARD_DB[c].mv <= 3]
    if not gy_artifacts:
        return
    target = max(gy_artifacts, key=lambda n: CARD_DB[n].mv)
    if CARD_DB[target].mv <= CARD_DB[fodder].mv:
        return
    state.goblin_engineer_used_this_turn = True
    spend_mana(state, 1)
    sacrifice(state, fodder)
    if target not in state.graveyard:
        return
    state.graveyard.remove(target)
    if is_creature_card(target):
        creature_enters(state, target, from_hand=False)
    else:
        state.battlefield.append(target)
        resolve_etb(state, target)
    state.weld_activations_total += 1


def try_mishra_unearth(state: GameState):
    """'Each artifact card in your graveyard has unearth {1}{B}{R}.'
    Unearth: {1}{B}{R}, return da GY pro campo, ganha haste, exilada no
    fim do turno (ou se sair do campo). So' unearth-a a maior MV
    disponivel, uma vez por turno (limite real de mana pratico)."""
    if "Mishra, Tamer of Mak Fawa" not in state.battlefield:
        return
    if state.mishra_unearth_used_this_turn or remaining_mana(state) < 3:
        return
    gy_artifacts = [c for c in state.graveyard if is_artifact_card(c)]
    if not gy_artifacts:
        return
    target = max(gy_artifacts, key=lambda n: CARD_DB[n].mv)
    state.mishra_unearth_used_this_turn = True
    spend_mana(state, 3)
    state.graveyard.remove(target)
    if is_creature_card(target):
        creature_enters(state, target, from_hand=False)
        state.creature_cast_turn[target] = state.turn - 1  # haste
    else:
        state.battlefield.append(target)
        resolve_etb(state, target)
    state.temp_creatures_pending_exile.append(target)
    state.recursion_events_total += 1


def try_osgir_activation(state: GameState):
    """Osgir, the Reconstructor: '{X}, {T}, Exile an artifact card with
    mana value X from your graveyard: Create two tokens that are copies
    of the exiled card. Activate only as a sorcery.'"""
    if "Osgir, the Reconstructor" not in state.battlefield or "Osgir, the Reconstructor" not in ready_creatures(state):
        return
    if state.osgir_used_this_turn:
        return
    gy_artifacts = [c for c in state.graveyard if is_artifact_card(c)]
    affordable = [c for c in gy_artifacts if CARD_DB[c].mv <= remaining_mana(state)]
    if not affordable:
        return
    target = max(affordable, key=lambda n: CARD_DB[n].mv)
    state.osgir_used_this_turn = True
    spend_mana(state, CARD_DB[target].mv)
    state.graveyard.remove(target)
    state.exile.append(target)
    for _ in range(2):
        token_name = make_token_copy_name(target)
        if is_creature_card(target):
            creature_enters(state, token_name, from_hand=False, token=True)
        else:
            state.battlefield.append(token_name)
            resolve_etb(state, token_name)
    state.recursion_events_total += 1


# ---------------------------------------------------------------------------
# Cheat pra campo (temporario) + sacrificio-payoff
# ---------------------------------------------------------------------------

def try_feldon(state: GameState):
    """'{2}{R}, {T}: Create a token that's a copy of target creature card
    in your graveyard, except it's an artifact in addition to its other
    types. It gains haste. Sacrifice it at the beginning of the next end
    step.' Escolhe a maior MV disponivel no cemiterio."""
    if "Feldon of the Third Path" not in state.battlefield or "Feldon of the Third Path" not in ready_creatures(state):
        return
    if state.feldon_used_this_turn or remaining_mana(state) < 3:
        return
    creatures_in_gy = [c for c in state.graveyard if is_creature_card(c)]
    if not creatures_in_gy:
        return
    target = max(creatures_in_gy, key=lambda n: CARD_DB[n].mv)
    state.feldon_used_this_turn = True
    spend_mana(state, 3)
    token_name = make_token_copy_name(target)
    creature_enters(state, token_name, from_hand=False, token=True)
    state.creature_cast_turn[token_name] = state.turn - 1  # haste
    state.temp_creatures_pending_sacrifice.append(token_name)
    state.creatures_cheated_in_total += 1


def try_sneak_attack(state: GameState):
    """'{R}: You may put a creature card from your hand onto the
    battlefield. That creature gains haste. Sacrifice the creature at the
    beginning of the next end step.' Sem limite de ativacoes/turno no
    oraculo -- ativa repetidamente enquanto houver mana E criatura na
    mao, priorizando a de maior poder (maximiza Warstorm Surge + dano de
    combate do proprio Anrakyr, se for ele)."""
    if "Sneak Attack" not in state.battlefield:
        return
    guard = 0
    while remaining_mana(state) >= 1 and guard < 6:
        guard += 1
        creatures_in_hand = [c for c in state.hand if is_creature_card(c) and c != COMMANDER]
        if not creatures_in_hand:
            return
        target = max(creatures_in_hand, key=lambda n: get_power(state, n))
        spend_mana(state, 1)
        creature_enters(state, target, from_hand=True)
        state.creature_cast_turn[target] = state.turn - 1  # haste
        state.temp_creatures_pending_sacrifice.append(target)
        state.creatures_cheated_in_total += 1


def try_ayara(state: GameState):
    """Ayara, Widow of the Realm: '{T}, Sacrifice another creature or
    artifact: Ayara deals X damage to target opponent and you gain X
    life, where X is the sacrificed permanent's mana value.' So' consome
    fodder que ia morrer de qualquer jeito (`best_payoff_fodder`) -- nunca
    sacrifica board real por essa ativada (ver docstring da funcao)."""
    if "Ayara, Widow of the Realm" not in state.battlefield or state.ayara_transformed:
        return
    if "Ayara, Widow of the Realm" not in ready_creatures(state):
        return
    if state.ayara_recur_used_this_turn:
        return
    fodder = best_payoff_fodder(state)
    if fodder is None:
        return
    mv = CARD_DB[fodder].mv
    if mv <= 0:
        return
    state.ayara_recur_used_this_turn = True
    sacrifice(state, fodder)
    proxy_drain(state, mv)
    gain_life(state, mv)
    state.sacrifice_payoff_damage_total += mv


def try_ayara_flip_reanimate(state: GameState):
    """Ayara, Furnace Queen (verso, apos transformar): 'At the beginning
    of combat on your turn, return up to one target artifact or creature
    card from your graveyard to the battlefield. It gains haste. Exile it
    at the beginning of the next end step.'"""
    if not state.ayara_transformed:
        return
    candidates = [c for c in state.graveyard if is_creature_card(c) or is_artifact_card(c)]
    if not candidates:
        return
    target = max(candidates, key=lambda n: CARD_DB[n].mv)
    state.graveyard.remove(target)
    if is_creature_card(target):
        creature_enters(state, target, from_hand=False)
        state.creature_cast_turn[target] = state.turn - 1
    else:
        state.battlefield.append(target)
        resolve_etb(state, target)
    state.temp_creatures_pending_exile.append(target)
    state.recursion_events_total += 1


def try_ayara_transform(state: GameState):
    """'{5}{R/P}: Transform Ayara. Activate only as a sorcery.' Paga com
    mana real (nunca vida, {R/P} tratado como {R} aqui -- premissa
    documentada: vida e' recurso mais valioso que 1 mana extra)."""
    if "Ayara, Widow of the Realm" not in state.battlefield or state.ayara_transformed:
        return
    if remaining_mana(state) < 6 or color_sources(state, "R") < 1:
        return
    spend_mana(state, 6)
    state.ayara_transformed = True


def try_altar_of_the_wretched(state: GameState):
    """ETB: 'you may sacrifice a nontoken creature. If you do, draw X
    cards, then mill X cards, where X is that creature's power.' So'
    dispara no momento em que ela entra -- ver `resolve_etb`."""
    pass


def try_susur_secundi(state: GameState):
    """'12+ | {1}{B}, {T}, Pay 2 life, Sacrifice a creature: Draw cards
    equal to the sacrificed creature's power.' So' liga com 12+ contadores
    de carga (station) -- ver `try_station_lands`."""
    if "Susur Secundi, Void Altar" not in state.battlefield:
        return
    if state.charge_counters.get("Susur Secundi, Void Altar", 0) < 12:
        return
    if state.susur_secundi_used_this_turn or remaining_mana(state) < 1 or state.life <= 2:
        return
    fodder = best_payoff_fodder(state)
    if fodder is None or not is_creature_card(fodder):
        return
    power = get_power(state, fodder)
    if power <= 0:
        return
    state.susur_secundi_used_this_turn = True
    spend_mana(state, 1)
    self_damage(state, 2)
    sacrifice(state, fodder)
    draw_cards(state, power)
    state.sacrifice_payoff_draws_total += power


def try_station_lands(state: GameState):
    """Station (Adagia, Windswept Bastion / Susur Secundi, Void Altar /
    The Eternity Elevator): 'Tap another creature you control: Put charge
    counters equal to its power on this [Planet/Spacecraft]. Station only
    as a sorcery.' Estaciona com a MAIOR criatura pronta disponivel que
    nao seja essencial pro combate desse turno (nunca o Megatron -- ele
    precisa atacar)."""
    for land_name in ("Adagia, Windswept Bastion", "Susur Secundi, Void Altar", "The Eternity Elevator"):
        if land_name not in state.battlefield:
            continue
        candidates = [n for n in ready_creatures(state) if n != COMMANDER and get_power(state, n) > 0]
        if not candidates:
            continue
        best = max(candidates, key=lambda n: get_power(state, n))
        state.charge_counters[land_name] = state.charge_counters.get(land_name, 0) + get_power(state, best)
        state.creature_cast_turn[best] = state.turn  # simplificacao: "tapped" ~ nao ataca esse turno


def try_adagia_copy(state: GameState):
    """Adagia, Windswept Bastion: '12+ | {3}{W}, {T}: Create a token
    that's a copy of target artifact or enchantment you control, except
    it's legendary.' Copia sempre o artefato de maior MV em campo
    (retrigger real do Warstorm Surge se for criatura)."""
    if "Adagia, Windswept Bastion" not in state.battlefield:
        return
    if state.charge_counters.get("Adagia, Windswept Bastion", 0) < 12:
        return
    if state.adagia_copy_used_this_turn or remaining_mana(state) < 4 or color_sources(state, "W") < 1:
        return
    candidates = [n for n in state.battlefield if (is_artifact_card(n) or CARD_DB[n].ctype == "enchantment") and n != COMMANDER]
    if not candidates:
        return
    target = max(candidates, key=lambda n: CARD_DB[n].mv)
    state.adagia_copy_used_this_turn = True
    spend_mana(state, 4)
    token_name = make_token_copy_name(target)
    if is_creature_card(target):
        creature_enters(state, token_name, from_hand=False, token=True)
    else:
        state.battlefield.append(token_name)
        resolve_etb(state, token_name)
    state.recursion_events_total += 1


# ---------------------------------------------------------------------------
# Daretti (planeswalker + criatura), Megatron, Anrakyr, Ironsoul
# ---------------------------------------------------------------------------

DARETTI_SAVANT_STARTING_LOYALTY = 5


def try_daretti_savant(state: GameState):
    """Daretti, Scrap Savant: +2 discard-ate-2/draw-mesmo-numero; -2
    sacrifica artefato, devolve outro do cemiterio pro campo; -10
    emblema ('whenever an artifact is put into your graveyard from the
    battlefield, return it at the beginning of the next end step' --
    tratado como flag permanente que faz TODO artefato que morre voltar
    automaticamente). Prioriza -2 quando ha' upgrade real disponivel
    (motor principal do deck), senao +2 pra filtrar e chegar no -10."""
    if "Daretti, Scrap Savant" not in state.battlefield:
        return
    if state.daretti_savant_ultimate_active:
        return
    fodder = best_weld_fodder(state)
    gy_upgrade = None
    if fodder is not None:
        gy_artifacts = [c for c in state.graveyard if is_artifact_card(c) and CARD_DB[c].mv > CARD_DB[fodder].mv]
        if gy_artifacts:
            gy_upgrade = max(gy_artifacts, key=lambda n: CARD_DB[n].mv)
    if gy_upgrade is not None and state.daretti_savant_loyalty >= 2:
        state.daretti_savant_loyalty -= 2
        sacrifice(state, fodder)
        if gy_upgrade not in state.graveyard:
            return
        state.graveyard.remove(gy_upgrade)
        if is_creature_card(gy_upgrade):
            creature_enters(state, gy_upgrade, from_hand=False)
        else:
            state.battlefield.append(gy_upgrade)
            resolve_etb(state, gy_upgrade)
        state.weld_activations_total += 1
    elif state.daretti_savant_loyalty >= 10:
        state.daretti_savant_loyalty = 0
        state.daretti_savant_ultimate_active = True
    else:
        discard_n = min(2, len(state.hand))
        for c in state.hand[:discard_n]:
            state.hand.remove(c)
            state.graveyard.append(c)
        draw_cards(state, discard_n)
        state.daretti_savant_loyalty += 2


def daretti_ultimate_recursion_check(state: GameState, dying_artifact_name: str):
    """Emblema do -10: 'whenever an artifact is put into your graveyard
    from the battlefield, return that card to the battlefield at the
    beginning of the next end step.' Fila propria (`daretti_emblem_
    pending_return`), processada no fim do turno em `end_step` -- nao
    reaproveita a fila de exilio (semantica oposta: essa VOLTA pro
    campo, nao sai dele)."""
    if state.daretti_savant_ultimate_active and dying_artifact_name in state.graveyard:
        state.daretti_emblem_pending_return.append(dying_artifact_name)


def anrakyr_attack_ability(state: GameState):
    """'Whenever Anrakyr the Traveller attacks, you may cast an artifact
    spell from your hand or graveyard by paying life equal to its mana
    value rather than paying its mana cost.' O dano de combate dele em si
    ja' e' contado por `all_attackers_combat` (achado real do usuario
    jogando 2026-09-02: TODO mundo ataca agora, nao so' Megatron/Anrakyr
    -- ver essa funcao pra a mudanca completa) -- aqui so' o efeito extra
    exclusivo de Anrakyr, disparado de dentro do loop generico quando ele
    e' quem esta' atacando."""
    pool = [c for c in (state.hand + state.graveyard) if is_artifact_card(c) and c != COMMANDER]
    if not pool:
        return
    affordable = [c for c in pool if CARD_DB[c].mv < state.life]
    if not affordable:
        return
    target = max(affordable, key=lambda n: CARD_DB[n].mv)
    life_cost = CARD_DB[target].mv
    if life_cost <= 0:
        return
    self_damage(state, life_cost)
    if target in state.hand:
        state.hand.remove(target)
    else:
        state.graveyard.remove(target)
    if is_creature_card(target):
        creature_enters(state, target, from_hand=False)
    else:
        state.battlefield.append(target)
        resolve_etb(state, target)
    state.creatures_cheated_in_total += 1


def ironsoul_enforcer_trigger(state: GameState):
    """'Whenever this creature or a commander you control attacks alone,
    return target artifact card from your graveyard to the battlefield.'
    So' dispara quando exatamente 1 criatura atacou nesse combate."""
    if "Ironsoul Enforcer" not in state.battlefield or state.attackers_this_combat != 1:
        return
    gy_artifacts = [c for c in state.graveyard if is_artifact_card(c)]
    if not gy_artifacts:
        return
    target = max(gy_artifacts, key=lambda n: CARD_DB[n].mv)
    state.graveyard.remove(target)
    if is_creature_card(target):
        creature_enters(state, target, from_hand=False)
    else:
        state.battlefield.append(target)
        resolve_etb(state, target)
    state.recursion_events_total += 1


def steel_seraph_combat(state: GameState):
    """'At the beginning of combat on your turn, target creature you
    control gains your choice of flying, vigilance, or lifelink until end
    of turn.' Escolhe sempre lifelink no Megatron -- unica opcao com
    efeito numerico neste motor (mesma logica ja usada na versao
    anterior deste arquivo)."""
    if "Steel Seraph" not in state.battlefield:
        return False
    return True


def cast_megatron(state: GameState):
    # O comandante vem da zona de comando, nao da mao/biblioteca --
    # castavel a qualquer main phase desde o turno 1 (nao depende de ter
    # sido "comprado"). Achado real ao testar a reconstrucao 2026-09-02:
    # BASE_LIBRARY exclui o comandante de proposito (nunca entra na mao
    # via draw_cards), mas o cast_megatron original checava "COMMANDER
    # not in state.hand" -- nunca era verdade, Megatron nunca era
    # conjurado em partida nenhuma. Corrigido pra so' depender de mana.
    if state.commander_in_play:
        return
    tax = 2 * state.commander_cast_count
    vehicle_cost = MEGATRON_VEHICLE_COST + tax
    tyrant_cost = MEGATRON_TYRANT_COST + tax
    if remaining_mana(state) >= vehicle_cost and has_color_sources_for(state, COMMANDER):
        spend_mana(state, vehicle_cost)
        state.megatron_face = "vehicle"
    elif remaining_mana(state) >= tyrant_cost and has_color_sources_for(state, COMMANDER):
        spend_mana(state, tyrant_cost)
        state.megatron_face = "tyrant"
    else:
        return
    state.battlefield.append(COMMANDER)
    state.commander_in_play = True
    state.commander_cast_count += 1
    if state.commander_cast_turn is None:
        state.commander_cast_turn = state.turn
    state.creature_cast_turn[COMMANDER] = state.turn


def try_phyrexian_arena_upkeep(state: GameState):
    """Phyrexian Arena: 'At the beginning of your upkeep, you draw a card
    and you lose 1 life.' Achado real 2026-09-03 (usuario: 'impressao de
    que falta draw no deck') -- unico draw incondicional/repetivel todo
    turno da lista inteira, sem depender de sacrificio nem de combate."""
    if "Phyrexian Arena" not in state.battlefield:
        return
    draw_cards(state, 1)
    self_damage(state, 1)
    state.phyrexian_arena_life_lost_total += 1


def try_nexus_of_becoming(state: GameState):
    """Nexus of Becoming: 'At the beginning of combat on your turn, draw
    a card. Then you may exile an artifact or creature card from your
    hand. If you do, create a token that's a copy of the exiled card,
    except it's a 3/3 Golem artifact creature in addition to its other
    types.' Achado real 2026-09-04 (auditoria sistematica pedida pelo
    usuario depois de eu ter esquecido esta carta 2x): a tag
    `nexus_combat_draw_copy` nunca foi lida em lugar nenhum do arquivo --
    mecanica fantasma pura, igual Ragavan/Daretti Rocketeer antes dela.
    Exila sempre a carta artefato/criatura de MENOR MV da mao (perder a
    mais barata e' sempre lucro liquido por um corpo 3/3 gratis + gatilho
    do Warstorm Surge). Simplificacao documentada: o token nao herda os
    'outros tipos' do card original (mesma convencao ja usada pro
    Phyrexian Golem Token/Shapeshifter Token)."""
    if "Nexus of Becoming" not in state.battlefield:
        return
    draw_cards(state, 1)
    candidates = [c for c in state.hand if c in CARD_DB and (is_artifact_card(c) or is_creature_card(c))]
    if not candidates:
        return
    exiled = min(candidates, key=lambda n: CARD_DB[n].mv)
    state.hand.remove(exiled)
    state.exile.append(exiled)
    token_name = "Nexus Golem Token"
    if token_name not in CARD_DB:
        add(token_name, 0, "creature", {"artifact"}, power=3, toughness=3)
    creature_enters(state, token_name, from_hand=False, token=True)
    state.nexus_tokens_created_total += 1


def try_equip_haste(state: GameState):
    """Lightning Greaves ('equipped creature has haste and shroud') e
    Swiftfoot Boots ('equipped creature has hexproof and haste') --
    achado real 2026-09-04 (mesma auditoria): as 2 sao conjuradas
    normalmente (confirmado com instrumentacao: 345x e 267x em 2000
    jogos) mas NUNCA equipadas em nada -- nenhuma logica de equip existia
    no arquivo inteiro, mana e carta gastos por zero efeito. A metade de
    protecao (shroud/hexproof) nao tem efeito mecanico possivel aqui
    (sem oponente real com remocao pra proteger contra -- mesma convencao
    ja documentada pra Clever Concealment/Blacksmith's Skill). A metade
    que TEM efeito real e' o haste: uma criatura com doenca de invocacao
    nao ataca esse turno em `ready_creatures()`. Equipa na criatura de
    maior poder que entrou esse turno e ainda nao tem haste -- gratuito
    pro Greaves (Equip {0}), custa 1 mana pro Boots (Equip {1}, so' se
    sobrar mana)."""
    equip_cost = 0 if "Lightning Greaves" in state.battlefield else (
        1 if "Swiftfoot Boots" in state.battlefield else None)
    if equip_cost is None:
        return
    if equip_cost > 0 and remaining_mana(state) < equip_cost:
        return
    sick = [n for n in state.battlefield if is_creature_card(n) and n != COMMANDER
            and state.creature_cast_turn.get(n, -1) == state.turn and get_power(state, n) > 0]
    if not sick:
        return
    target = max(sick, key=lambda n: get_power(state, n))
    if equip_cost > 0:
        spend_mana(state, equip_cost)
    state.creature_cast_turn[target] = state.turn - 1
    state.equip_haste_activations_total += 1


def try_cosmic_cube_attack_trigger(state: GameState):
    """Cosmic Cube: 'Whenever you attack, look at the top six cards of
    your library. You may cast a spell from among them with mana value
    less than or equal to the greatest power among attacking creatures
    you control without paying its mana cost. Put the rest on the bottom
    of your library in a random order.' Dispara 1x por combate (nao por
    atacante), usando `state.max_attacker_power_this_combat` (acumulado
    por Megatron + `all_attackers_combat`, ja' que aqui TODO mundo ataca
    de verdade). 'Without paying its mana cost' -- sem gate de mana/cor
    nenhum, dispatch direto igual `cast_card` mas sem `spend_mana`. Mesma
    simplificacao de nao embaralhar o resto ja documentada nos reveals de
    Combustible Gearhulk/Saheeli's Directive."""
    if "Cosmic Cube" not in state.battlefield:
        return
    max_power = state.max_attacker_power_this_combat
    if max_power <= 0 or not state.library:
        return
    top = state.library[:6]
    state.library = state.library[6:]
    castable = [c for c in top if c in CARD_DB and c not in LAND_NAMES
                and c not in NO_SELF_HARM_EXCLUDE and CARD_DB[c].mv <= max_power]
    if castable:
        chosen = max(castable, key=lambda n: CARD_DB[n].mv)
        top.remove(chosen)
        if is_creature_card(chosen):
            creature_enters(state, chosen, from_hand=False)
        elif CARD_DB[chosen].ctype in ("instant", "sorcery"):
            resolve_instant_sorcery(state, chosen)
            state.graveyard.append(chosen)
        elif CARD_DB[chosen].ctype == "planeswalker":
            state.battlefield.append(chosen)
            state.daretti_savant_loyalty = DARETTI_SAVANT_STARTING_LOYALTY
        else:
            state.battlefield.append(chosen)
            resolve_etb(state, chosen)
            if is_artifact_card(chosen):
                artifact_etb_hooks(state, chosen)
        state.cosmic_cube_free_casts_total += 1
        state.recursion_events_total += 1
    state.library.extend(top)


def megatron_combat(state: GameState):
    if not state.commander_in_play or state.megatron_face is None:
        return
    if COMMANDER not in ready_creatures(state):
        return
    state.attackers_this_combat += 1

    if state.megatron_face == "vehicle":
        fuel = best_megatron_fuel(state)
        if fuel is not None:
            mv = CARD_DB[fuel].mv
            sacrifice(state, fuel)
            state.megatron_fuel_sacrificed_total += 1
            excess = max(0, mv - 1)  # proxy: alvo de 1 de resistencia (premissa do proprio primer)
            if excess > 0:
                proxy_drain(state, excess)
            state.megatron_face = "tyrant"
            state.megatron_conversions_total += 1

    power = MEGATRON_TYRANT_POWER if state.megatron_face == "tyrant" else MEGATRON_VEHICLE_POWER
    lifelink_this_combat = steel_seraph_combat(state)
    proxy_drain(state, power)
    state.max_attacker_power_this_combat = max(state.max_attacker_power_this_combat, power)
    if lifelink_this_combat:
        gain_life(state, power)


def megatron_postcombat(state: GameState):
    if not state.commander_in_play or state.megatron_face != "tyrant":
        return
    if state.life_lost_by_opponents_this_turn > 0:
        mana = state.life_lost_by_opponents_this_turn
        state.bonus_mana_pool += mana
        state.megatron_mana_generated_total += mana
        state.megatron_face = "vehicle"
        state.megatron_conversions_total += 1


def try_bygone_colossus_warp(state: GameState):
    """Bygone Colossus: 'Warp {3} (cast for {3}, exile at next end step,
    may cast from exile later for warp again).' Repetivel enquanto
    houver mana sobrando -- cada cast dispara Warstorm Surge de novo
    (9 de dano por ativacao, se Warstorm Surge estiver em campo)."""
    in_hand = "Bygone Colossus" in state.hand
    in_exile = "Bygone Colossus" in state.exile
    if not (in_hand or in_exile) or remaining_mana(state) < 3:
        return
    spend_mana(state, 3)
    if in_hand:
        state.hand.remove("Bygone Colossus")
    else:
        state.exile.remove("Bygone Colossus")
    creature_enters(state, "Bygone Colossus", from_hand=False)
    state.creature_cast_turn["Bygone Colossus"] = state.turn - 1
    state.temp_creatures_pending_exile.append("Bygone Colossus")
    state.creatures_cheated_in_total += 1


# ---------------------------------------------------------------------------
# Custo efetivo / cast / terrenos
# ---------------------------------------------------------------------------

def effective_cost(state: GameState, name: str) -> int:
    mv = CARD_DB[name].mv
    if name == "Metalwork Colossus":
        # "This spell costs {X} less to cast, where X is the total mana
        # value of noncreature artifacts you control."
        reduction = sum(CARD_DB[n].mv for n in state.battlefield
                         if is_artifact_card(n) and not is_creature_card(n))
        mv = max(0, mv - reduction)
    elif name == "Demonic Junker":
        # "Affinity for artifacts (costs {1} less for each artifact you control)."
        reduction = sum(1 for n in state.battlefield if is_artifact_card(n))
        mv = max(0, mv - reduction)
    return mv


def can_cast(state: GameState, name: str) -> bool:
    return remaining_mana(state) >= effective_cost(state, name) and has_color_sources_for(state, name)


NO_SELF_HARM_EXCLUDE = {
    # Wipes/dano simetrico que so' machucariam o proprio board -- sem
    # oponente real pra tambem atingir, nunca vale a pena conjurar
    # (mesma convencao ja usada pro Blasphemous Act em toda a sessao).
    "Blasphemous Act", "Decree of Pain", "Heartless Conscription", "Chandra's Ignition",
    # Protecao (hexproof/indestructible/phase out) sem remocao/wrath real
    # de oponente pra proteger contra -- conjurar so' desperdicaria mana
    # (achado real ao testar: sem essa exclusao, Blacksmith's Skill era
    # auto-conjurada todo turno que sobrava 1 mana, sem efeito nenhum,
    # mesma categoria de simplificacao estrutural de sempre, nao e'
    # fantasma -- a tag continua definida e documentada).
    "Blacksmith's Skill", "Clever Concealment",
}


def resolve_instant_sorcery(state: GameState, name: str):
    tags = CARD_DB[name].tags
    if "interaction" in tags:
        state.interaction_spells_cast_total += 1
    elif "loot2_2_flashback" in tags:
        # Faithless Looting: "draw two cards, then discard two cards."
        draw_cards(state, 2)
        for _ in range(min(2, len(state.hand))):
            worst = worst_discard_target(state)
            state.hand.remove(worst)
            state.graveyard.append(worst)
    elif "loot1_2_flashback" in tags:
        # Laughing Mad: "discard a card. Draw two cards."
        if state.hand:
            worst = worst_discard_target(state)
            state.hand.remove(worst)
            state.graveyard.append(worst)
        draw_cards(state, 2)
    elif "demand_answers" in tags:
        # "As an additional cost, sacrifice an artifact or discard a
        # card. Draw two cards." Prefere sacrificar fodder gratis; senao
        # descarta a pior carta.
        fodder = best_payoff_fodder(state)
        if fodder is not None and is_artifact_card(fodder):
            sacrifice(state, fodder)
        elif state.hand:
            worst = worst_discard_target(state)
            state.hand.remove(worst)
            state.graveyard.append(worst)
        draw_cards(state, 2)
    elif "wheel_full" in tags:
        state.wheels_total += 1
        for c in state.hand[:]:
            state.graveyard.append(c)
        state.hand = []
        draw_cards(state, 7)
    elif "saheeli_directive" in tags:
        # "Improvise. Reveal the top X cards of your library. You may put
        # any number of artifact cards with mana value X or less from
        # among them onto the battlefield. Then put the rest into your
        # graveyard." X = o maximo pagavel (Improvise nao modelado a
        # parte -- paga so' com mana real, documentado).
        x = max(0, remaining_mana(state) - 3)
        if x <= 0:
            return
        spend_mana(state, x + 3)
        revealed = state.library[:x]
        state.library = state.library[x:]
        for c in revealed:
            if c in CARD_DB and is_artifact_card(c) and CARD_DB[c].mv <= x:
                if is_creature_card(c):
                    creature_enters(state, c, from_hand=False)
                else:
                    state.battlefield.append(c)
                    resolve_etb(state, c)
            else:
                state.graveyard.append(c)


def try_cast_flashback(state: GameState, name: str, flashback_cost: int):
    """Faithless Looting {2}{R} / Laughing Mad {3}{R} flashback, do
    cemiterio, exilada depois de resolver."""
    if name not in state.graveyard or remaining_mana(state) < flashback_cost:
        return
    spend_mana(state, flashback_cost)
    state.graveyard.remove(name)
    resolve_instant_sorcery(state, name)
    state.exile.append(name)


def cast_card(state: GameState, name: str):
    card = CARD_DB[name]
    spend_mana(state, effective_cost(state, name))
    if name in state.hand:
        state.hand.remove(name)

    if any(t.startswith("rock") for t in card.tags):
        state.ramp_pieces_cast_total += 1

    if card.ctype in ("instant", "sorcery"):
        resolve_instant_sorcery(state, name)
        state.graveyard.append(name)
        return

    if card.ctype == "planeswalker":
        state.battlefield.append(name)
        state.daretti_savant_loyalty = DARETTI_SAVANT_STARTING_LOYALTY
        return

    if card.ctype == "creature":
        creature_enters(state, name, from_hand=False)
        return

    state.battlefield.append(name)
    resolve_etb(state, name)
    if is_artifact_card(name):
        artifact_etb_hooks(state, name)


def play_land(state: GameState):
    if state.lands_played_this_turn >= 1:
        return
    lands_in_hand = [n for n in state.hand if n in LAND_NAMES]
    if not lands_in_hand:
        return

    def missing_score(card):
        score = 0
        for color in "WBR":
            if color_sources(state, color) == 0 and color in CARD_DB[card].produces:
                score += 1
        return -score

    lands_in_hand.sort(key=missing_score)
    choice = lands_in_hand[0]
    state.hand.remove(choice)
    state.lands_played_this_turn += 1
    state.battlefield.append(choice)
    if choice in ETB_TAPPED_LANDS:
        if choice == "Smoldering Marsh":
            basics_in_play = sum(1 for n in state.battlefield if n in ("Mountain", "Plains", "Swamp"))
            if basics_in_play < 2:
                state.tapped_land_this_turn = choice
        else:
            state.tapped_land_this_turn = choice


def try_ash_barrens_cycle(state: GameState):
    """'Basic landcycling {1} ({1}, Discard this card: Search your
    library for a basic land card, put it into your hand.)' So' cicla se
    ja' joguei terreno esse turno E tenho mana sobrando (senao e' melhor
    so' jogar ela normal como terreno incolor)."""
    if "Ash Barrens" not in state.hand or state.lands_played_this_turn == 0:
        return
    if remaining_mana(state) < 1:
        return
    basics = [n for n in state.library if n in ("Mountain", "Plains", "Swamp")]
    if not basics:
        return
    spend_mana(state, 1)
    state.hand.remove("Ash Barrens")
    state.graveyard.append("Ash Barrens")
    pick = basics[0]
    state.library.remove(pick)
    state.hand.append(pick)
    state.tutors_used_total += 1


# ---------------------------------------------------------------------------
# Loop de turno
# ---------------------------------------------------------------------------

def try_black_market_connections(state: GameState):
    """'At the beginning of your first main phase, choose one or more --
    Sell Contraband (Treasure, lose 1 life) / Buy Information (draw,
    lose 2 life) / Hire a Mercenary (3/2 token, lose 3 life).' Escolhe as
    3 (maximiza valor por ativacao), paga 6 de vida total -- so' se tiver
    vida sobrando."""
    if state.life <= 10:
        return
    state.black_market_used_this_turn = True
    state.bonus_mana_pool += 1
    self_damage(state, 1)
    draw_cards(state, 1)
    self_damage(state, 2)
    token = "Shapeshifter Token"
    if token not in CARD_DB:
        add(token, 0, "creature", set(), power=3, toughness=2)
    creature_enters(state, token, from_hand=False, token=True)
    self_damage(state, 3)


def main_phase(state: GameState):
    cast_megatron(state)
    if "Black Market Connections" in state.battlefield and not state.black_market_used_this_turn:
        try_black_market_connections(state)

    try_station_lands(state)
    try_ash_barrens_cycle(state)

    while True:
        castables = [n for n in state.hand if n not in LAND_NAMES and can_cast(state, n)
                     and n not in NO_SELF_HARM_EXCLUDE]
        if not castables:
            break

        def prio(n):
            tags = CARD_DB[n].tags
            group = 0 if (tags & {"rock1", "rock2", "rock3"}) else 1
            return (group, effective_cost(state, n))

        castables.sort(key=prio)
        cast_card(state, castables[0])

    try_goblin_welder(state)
    try_scrap_welder(state)
    try_trash_for_treasure(state)
    try_goblin_engineer_activation(state)
    try_mishra_unearth(state)
    try_osgir_activation(state)
    try_metalwork_colossus_recursion(state)
    try_daretti_savant(state)
    try_feldon(state)
    try_sneak_attack(state)
    try_ayara(state)
    try_ayara_transform(state)
    try_susur_secundi(state)
    try_adagia_copy(state)
    try_bygone_colossus_warp(state)
    try_cast_flashback(state, "Faithless Looting", 3)
    try_cast_flashback(state, "Laughing Mad", 4)


def ragavan_attack_ability(state: GameState):
    """'Whenever Ragavan deals combat damage to a player, create a
    Treasure token and exile the top card of that player's library.
    Until end of turn, you may cast that card.' Achado real 2026-09-02:
    a tag "ragavan" nunca foi lida em lugar nenhum, porque ate' agora so'
    Megatron/Anrakyr atacavam de verdade -- agora que todo mundo ataca
    (ver `all_attackers_combat`), o gatilho fica real. Alvo = minha
    propria biblioteca (premissa documentada, mesma convencao de "target
    player" usada pro Rakdos the Muscle/Sandstone Oracle/etc); a
    Treasure vira +1 de mana solta, e a carta exilada e' conjurada na
    hora se der pra pagar (senao fica perdida, mesma simplificacao de
    nao rastrear "mao exilada temporaria" usada pro Rakdos)."""
    state.bonus_mana_pool += 1
    if not state.library:
        return
    exiled = state.library.pop(0)
    state.exile.append(exiled)
    if exiled not in CARD_DB or exiled in LAND_NAMES:
        return
    if effective_cost(state, exiled) > remaining_mana(state) or not has_color_sources_for(state, exiled):
        return
    spend_mana(state, effective_cost(state, exiled))
    state.exile.remove(exiled)
    if is_creature_card(exiled):
        creature_enters(state, exiled, from_hand=False)
    else:
        state.battlefield.append(exiled)
        resolve_etb(state, exiled)
    state.creatures_cheated_in_total += 1


def daretti_rocketeer_attack_ability(state: GameState):
    """'Whenever Daretti enters or attacks, choose target artifact card
    in your graveyard. You may sacrifice an artifact. If you do, return
    the chosen card to the battlefield.' Achado real 2026-09-02: nem a
    metade de ETB nem a de ataque tinham dispatch nenhum (so' o poder
    dinamico estava implementado) -- mesmo padrao de "so Megatron/Anrakyr
    atacam" escondendo o gatilho de ataque; a de ETB nao tinha nem essa
    desculpa, era fantasma puro. Corrigido as 2 aqui (chamada tanto do
    ETB quanto do loop de ataque generico)."""
    gy_artifacts = [c for c in state.graveyard if is_artifact_card(c)]
    if not gy_artifacts:
        return
    target = max(gy_artifacts, key=lambda n: CARD_DB[n].mv)
    fodder = best_weld_fodder(state)
    if fodder is None or CARD_DB[fodder].mv >= CARD_DB[target].mv:
        return
    sacrifice(state, fodder)
    if target not in state.graveyard:
        return
    state.graveyard.remove(target)
    if is_creature_card(target):
        creature_enters(state, target, from_hand=False)
    else:
        state.battlefield.append(target)
        resolve_etb(state, target)
    state.weld_activations_total += 1


def all_attackers_combat(state: GameState):
    """Achado real 2026-09-02 (usuario jogou no Archidekt e reportou:
    "Os dois geraram mana, ataquei 2 jogadores diferentes e gerei 17 de
    mana incolor" -- Metalwork Colossus atacou um oponente DIFERENTE do
    que o Megatron, e o dano dele TAMBEM alimentou o gatilho pos-combate
    do Megatron via `state.life_lost_by_opponents_this_turn`, que e' um
    pool COMPARTILHADO -- o oraculo diz "life your opponents have lost
    THIS TURN", nao "life lost to Megatron"). Ate' aqui o motor so'
    modelava Megatron (+ Anrakyr, pela propria habilidade dele) atacando
    de verdade -- os outros finalizadores grandes (Metalwork Colossus,
    Bygone Colossus, Skitterbeam Battalion, os Gearhulks, Ironsoul
    Enforcer, Ayara, Daretti Rocketeer, Ragavan, Treasure Nabber) nunca
    atacavam. Corrigido: TODA criatura pronta (sem doenca de invocacao)
    com poder > 0 ataca de verdade, cada uma contribuindo pro mesmo pool
    de dano/vida-perdida via `proxy_drain()` -- sem bloqueio real
    modelado pra ninguem (mesma convencao de sempre), entao atacar com
    tudo e' sempre a jogada correta aqui."""
    for name in ready_creatures(state):
        if name == COMMANDER:
            continue  # ja' tratado em megatron_combat (fuel/conversao propria)
        power = get_power(state, name)
        if power <= 0:
            continue
        state.attackers_this_combat += 1
        proxy_drain(state, power)
        state.max_attacker_power_this_combat = max(state.max_attacker_power_this_combat, power)
        if name == "Anrakyr the Traveller":
            anrakyr_attack_ability(state)
        elif name == "Ragavan, Nimble Pilferer":
            ragavan_attack_ability(state)
        elif name == "Daretti, Rocketeer Engineer":
            daretti_rocketeer_attack_ability(state)


def combat_step(state: GameState):
    state.attackers_this_combat = 0
    state.max_attacker_power_this_combat = 0
    try_nexus_of_becoming(state)
    try_ayara_flip_reanimate(state)
    megatron_combat(state)
    all_attackers_combat(state)
    ironsoul_enforcer_trigger(state)
    try_cosmic_cube_attack_trigger(state)
    state.attackers_total_all_turns += state.attackers_this_combat


def end_step(state: GameState):
    megatron_postcombat(state)
    if "God-Pharaoh's Statue" in state.battlefield:
        proxy_drain(state, 1 * NUM_OPPONENTS)

    for n in state.temp_creatures_pending_sacrifice[:]:
        if n in state.battlefield:
            sacrifice(state, n)
    state.temp_creatures_pending_sacrifice = []

    for n in state.temp_creatures_pending_exile[:]:
        if n in state.battlefield:
            state.battlefield.remove(n)
            state.exile.append(n)
    state.temp_creatures_pending_exile = []

    for n in state.daretti_emblem_pending_return[:]:
        if n in state.graveyard:
            state.graveyard.remove(n)
            if is_creature_card(n):
                creature_enters(state, n, from_hand=False)
            else:
                state.battlefield.append(n)
                resolve_etb(state, n)
    state.daretti_emblem_pending_return = []

    max_hand = 7
    while len(state.hand) > max_hand:
        worst = worst_discard_target(state)
        state.hand.remove(worst)
        state.graveyard.append(worst)


def play_turn(state: GameState, is_first_turn: bool, on_play: bool):
    state.turn += 1
    state.lands_played_this_turn = 0
    state.mana_spent_this_turn = 0
    state.bonus_mana_pool = 0
    state.tapped_land_this_turn = None
    state.life_lost_by_opponents_this_turn = 0
    state.ayara_recur_used_this_turn = False
    state.goblin_welder_used_this_turn = False
    state.scrap_welder_used_this_turn = False
    state.feldon_used_this_turn = False
    state.goblin_engineer_used_this_turn = False
    state.mishra_unearth_used_this_turn = False
    state.osgir_used_this_turn = False
    state.black_market_used_this_turn = False
    state.adagia_copy_used_this_turn = False
    state.susur_secundi_used_this_turn = False

    try_phyrexian_arena_upkeep(state)
    if not (is_first_turn and on_play):
        draw_cards(state, 1)

    play_land(state)
    main_phase(state)
    try_equip_haste(state)
    combat_step(state)
    main_phase(state)
    end_step(state)


# ---------------------------------------------------------------------------
# Mulligan / build / batch
# ---------------------------------------------------------------------------

def should_keep(hand: list) -> bool:
    lands = sum(1 for n in hand if n in LAND_NAMES)
    good_early = {"Sol Ring", "Arcane Signet", "Fellwar Stone", "Mind Stone", COMMANDER}
    if lands >= 3:
        return True
    if lands == 2 and any(n in good_early for n in hand):
        return True
    return False


def mulligan(rng: random.Random):
    mulligans = 0
    while True:
        deck = BASE_LIBRARY[:]
        rng.shuffle(deck)
        hand = deck[:7]
        library = deck[7:]
        if should_keep(hand) or mulligans >= 3:
            for _ in range(mulligans):
                worst = min(hand, key=lambda n: CARD_DB[n].mv if n in CARD_DB else 0)
                hand.remove(worst)
                library.insert(0, worst)
            return hand, library, mulligans
        mulligans += 1


def simulate_one(seed: int, turns: int = 8):
    rng = random.Random(seed)
    hand, lib, mulls = mulligan(rng)
    state = GameState(hand=hand, library=lib, mulligans=mulls)
    turns_played = 0
    is_first = True
    while turns_played < turns:
        play_turn(state, is_first_turn=is_first, on_play=True)
        is_first = False
        turns_played += 1
        if state.extra_turns_pending > 0:
            state.extra_turns_pending -= 1
            play_turn(state, is_first_turn=False, on_play=True)
            turns_played += 1
    return state


def run_batch(n: int, seed_base: int, turns: int = 8):
    states = [simulate_one(seed_base + i, turns=turns) for i in range(n)]

    def avg(vals):
        return sum(vals) / len(vals) if vals else 0.0

    print(f"n={n}, seed_base={seed_base}, turns={turns}")
    print(f"Avg mulligans: {avg([s.mulligans for s in states]):.2f}")
    megatron_cast = [s.commander_cast_turn for s in states if s.commander_cast_turn is not None]
    print(f"Turno medio de conjuracao do Megatron: {avg(megatron_cast):.2f} | "
          f"mediana: {sorted(megatron_cast)[len(megatron_cast)//2] if megatron_cast else 0}")
    print(f"Nunca conjurado em {turns} turnos: {100*(n-len(megatron_cast))/n:.1f}%")
    print(f"Avg conversoes do Megatron: {avg([s.megatron_conversions_total for s in states]):.2f}")
    print(f"Avg mana gerada pela conversao do Megatron: {avg([s.megatron_mana_generated_total for s in states]):.2f}")
    print(f"Avg combustivel sacrificado pro Megatron: {avg([s.megatron_fuel_sacrificed_total for s in states]):.2f}")
    print(f"Avg dano/perda-de-vida proxy total (3 oponentes hipoteticos, NUNCA vida real): "
          f"{avg([s.proxy_damage_total for s in states]):.2f}")
    print(f"  -- dos quais via Warstorm Surge: {avg([s.warstorm_surge_damage_total for s in states]):.2f} "
          f"({avg([s.warstorm_surge_triggers_total for s in states]):.2f} gatilhos/partida)")
    print(f"Avg atacantes por partida (soma de todos os combates -- Megatron + todo o resto do "
          f"board pronto, achado real 2026-09-02): {avg([s.attackers_total_all_turns for s in states]):.2f}")
    print(f"Avg vida ganha: {avg([s.proxy_lifegain_total for s in states]):.2f}")
    print(f"Avg cartas compradas extra: {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"  -- dos quais via Phyrexian Arena: {avg([s.phyrexian_arena_life_lost_total for s in states]):.2f} "
          f"draws/partida ({avg([s.phyrexian_arena_life_lost_total for s in states]):.2f} vida perdida)")
    print(f"Avg conjuracoes gratis via Cosmic Cube: {avg([s.cosmic_cube_free_casts_total for s in states]):.2f}")
    print(f"Avg tokens 3/3 criados via Nexus of Becoming: {avg([s.nexus_tokens_created_total for s in states]):.2f}")
    print(f"Avg ativacoes de haste via Lightning Greaves/Swiftfoot Boots: "
          f"{avg([s.equip_haste_activations_total for s in states]):.2f}")
    print(f"Avg artefatos devolvidos pra mao via Pia's Revolution: "
          f"{avg([s.pia_revolution_returns_total for s in states]):.2f}")
    print(f"Avg ativacoes de solda (Welder/Scrap Welder/Trash for Treasure/Engineer/Osgir/Daretti): "
          f"{avg([s.weld_activations_total for s in states]):.2f}")
    print(f"Avg criaturas cheatadas pra campo (Sneak Attack/Feldon/Anrakyr/Bygone Colossus warp): "
          f"{avg([s.creatures_cheated_in_total for s in states]):.2f}")
    print(f"Avg eventos de recursao/valor totais: {avg([s.recursion_events_total for s in states]):.2f}")
    print(f"Avg artefatos sacrificados: {avg([s.artifacts_sacrificed_total for s in states]):.2f} | "
          f"Avg criaturas sacrificadas: {avg([s.creatures_sacrificed_total for s in states]):.2f}")
    print(f"Avg dano via payoff de sacrificio (Ayara/Susur Secundi): "
          f"{avg([s.sacrifice_payoff_damage_total for s in states]):.2f}")
    print(f"Avg compras via payoff de sacrificio (Rakdos/Susur Secundi): "
          f"{avg([s.sacrifice_payoff_draws_total for s in states]):.2f}")
    print(f"Avg wheels conjurados: {avg([s.wheels_total for s in states]):.2f}")
    print(f"Avg vida final: {avg([s.life for s in states]):.2f}")
    own_ko = sum(1 for s in states if s.life <= 0)
    print(f"Partidas em que os PROPRIOS efeitos derrubam minha vida a 0 ou menos: {100*own_ko/n:.1f}%")
    print(f"Avg mao final: {avg([len(s.hand) for s in states]):.2f}")
    daretti_ult = sum(1 for s in states if s.daretti_savant_ultimate_active)
    print(f"Daretti, Scrap Savant chegou ao -10 (emblema): {100*daretti_ult/n:.1f}% dos jogos")
    ayara_flip = sum(1 for s in states if s.ayara_transformed)
    print(f"Ayara transformou (Furnace Queen): {100*ayara_flip/n:.1f}% dos jogos")
    return states


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run_batch(2000, seed_base=1_000_000, turns=8)
