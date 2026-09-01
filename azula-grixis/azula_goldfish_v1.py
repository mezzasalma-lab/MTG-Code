"""
Goldfish simulator — Fire Lord Azula (Grixis — U/B/R)

Construido do zero em 2026-09-02, mesma disciplina de "compile TUDO" desta
sessao (Kutzil foi o primeiro dos 4 decks sem simulador, este e' o segundo).

Fonte de dados: oraculo real das 84 cartas nao-basicas + comandante,
buscado ao vivo via Scryfall (`POST /cards/collection` em 2 lotes +
`/cards/named` pros 2 MDFCs e pra "Seething Song" isolada — a mesma
ambiguidade de nome ja documentada em `auditoria.md`: a lista tem
"Seething Song" classica E "Blazing Firesinger // Seething Song", IDs
diferentes, cartas fisicas distintas), nao memoria nem so' a `auditoria.md`
anterior (que e' boa, mas foi escrita antes desta leitura linha-a-linha).

======================================================================
MOTOR REAL DESTE DECK (verificado via Scryfall, nao decorado)
======================================================================
Fire Lord Azula ({1}{U}{B}{R}, 4/4): Firebending 2 ("whenever this
attacks, add RR, dura ate fim de combate") + "whenever you cast a spell
while Azula is attacking, copy that spell, pode escolher novos alvos".

Este e' um deck spellslinger/storm de verdade, nao um deck de criaturas —
CMC medio 2.35, 41/62 nao-terrenos custam 1-2 mana. O motor central tem
3 camadas que se multiplicam:

1. **Storm real** (Grapeshot): copia a magica pra cada spell conjurada
   ANTES dela no turno — implementado com contador real
   `spells_cast_this_turn`, incrementado em `on_spell_event(..., "cast")`.

2. **Magecraft** (Archmage Emeritus compra, Storm-Kiln Artist cria
   Treasure, Veyran se buffa +1/+1) — dispara em CAST **e** em COPY.

3. **Motor de copia composto** (a parte mais complexa e mais real deste
   deck): Zada, Hedron Grinder ("magica que alveja SO' Zada -> copia pra
   cada OUTRA criatura que a magica poderia alvejar") + Azula ("magica
   conjurada enquanto ataca -> copia") sao ambas "triggered abilities de
   um permanente que controlo, causadas por conjurar/copiar instant ou
   sorcery" — e Veyran diz exatamente isso: "If you casting or copying an
   instant or sorcery spell causes a triggered ability of a permanent you
   control to trigger, that ability triggers an additional time." Ou
   seja, **Veyran DOBRA os gatilhos do Zada e da Azula tambem**, nao so' o
   proprio Magecraft dela (e dobra o proprio Magecraft dela tambem — e'
   uma interacao real conhecida, confirmada por ruling: a habilidade dela
   e' ela mesma um "triggered ability de um permanente que controlo").
   Implementado como `veyran_multiplier(state)` (2 se Veyran em campo, 1
   caso contrario), aplicado a: draws do Archmage Emeritus, Treasures do
   Storm-Kiln Artist, o proprio +1/+1 da Veyran, o numero de copias do
   Zada, e o numero de copias da Azula. NAO aplicado ao Storm (Storm e'
   uma habilidade da MAGICA, nao de um permanente) nem a gatilhos que nao
   vem de conjurar/copiar instant/sorcery.

Como o combate deste deck e' goldfish (sem bloqueio), "qual criatura
especifica recebeu qual bonus" nunca importa pro dano total — so' o poder
agregado do ataque importa. Por isso as magicas de alvo unico (cantrips e
combat tricks) sao resolvidas com um dicionario `creature_power_mods`
(nome -> {"add", "mult"}) em vez de objetos `Permanent` completos (que o
Kutzil/Toph precisam pra contadores +1/+1 persistentes — este deck nao
tem contadores persistentes reais em criaturas, so' pump-ate-fim-de-turno
e o dobro-de-poder pontual do Bulk Up/Unleash Fury).

Simplificacoes documentadas (nao inventadas — omissoes explicitas):
- Sem oponente real: todo dano e' `proxy_damage_total` agregado (numero
  flat, sem multiplicador de N-oponentes — convencao da MAIORIA dos
  simuladores desta sessao, ex.: Kutzil/Toph/Beorn, nao a convencao
  especifica do Megatron que assumia mesa de 4 pra suas proprias magicas
  "each opponent"; este deck nao tem premissa de tamanho de mesa
  declarada na auditoria).
- Innocent Blood ("each player sacrifices a creature") — Regra 1 da
  sessao: wipe simetrico sem oponente real modelado = so' conta como
  `interaction_plays`, sem sacrificio real executado (mesmo quando o
  efeito tecnicamente nos atingiria sozinhos tambem).
- Chandra's Ignition ("target creature you control deals damage equal to
  its power to each OTHER creature and each opponent") — mesma logica:
  atinge nossas proprias outras criaturas tambem (sem oponente pra
  tambem atingir), Regra 1 aplica, so' conta o dano proxy (representando
  "each opponent"), sem destruir as proprias criaturas.
- Kediss, Emberclaw Familiar ("replica dano de combate do comandante pra
  cada OUTRO oponente") — sem contagem de N-oponentes neste arquivo (ver
  acima), fica 📊 estrutural: o corpo 1/1 dele e' real (soma poder de
  ataque), a clausula de replicacao nao tem numero pra manifestar no
  modelo flat.
- Contramagicas (Counterspell, Wash Away, An Offer You Can't Refuse) e
  remocao pontual sem alvo (Chaos Warp, Path-style) — 📊 `interaction_plays`,
  precisam de spell/permanente de oponente real.
- Exotic Orchard — leitura literal do oraculo ("mana de uma cor que um
  terreno que um oponente controla PODERIA produzir"): sem terrenos de
  oponente modelados, produz 0 mana de verdade (nao e' julgamento de
  valor, e' a leitura correta da regra com 0 terrenos qualificando).
- Firebender Ascension (quest counters via "ataque causa uma triggered
  ability disparar") e Fire Nation Palace (firebending 4 concedido) —
  implementados de forma real mas aproximada (ver comentarios inline nos
  pontos de despacho) — mesmo padrao de aproximacao documentada usado em
  Ba Sing Se/Tale of Katara no Kutzil.
- Narset's Reversal / Reiterate — cast real (copiam Grapeshot no fim do
  turno pra empilhar mais um lote de dano de storm), mas sem loop
  recursivo de buyback indefinido (aplicado no maximo 1x cada por turno,
  decisao de escopo documentada, nao valor).
- Combate: "ataca" = sem doenca de invocacao pra permanentes que ja
  estavam em campo no inicio do turno (convencao de todos os simuladores
  desta biblioteca). Sem bloqueio real modelado.
"""

import json
import random
import statistics
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Card database
# ---------------------------------------------------------------------------

@dataclass
class Card:
    name: str
    mv: int
    ctype: str
    tags: frozenset = field(default_factory=frozenset)
    power: int = 0
    pips: dict = field(default_factory=dict)
    produces: frozenset = field(default_factory=frozenset)


CARD_DB: dict[str, Card] = {}


def add(name, mv, ctype, tags=(), power=0, pips=None, produces=None):
    CARD_DB[name] = Card(name=name, mv=mv, ctype=ctype, tags=frozenset(tags), power=power,
                          pips=dict(pips or {}), produces=frozenset(produces or ()))


COMMANDER = "Fire Lord Azula"
add(COMMANDER, 4, "creature", {"commander", "firebending2", "azula_copy_trigger"}, power=4,
    pips={"U": 1, "B": 1, "R": 1})

# --- Rampa/mana ------------------------------------------------------------
add("Arcane Signet", 2, "artifact", {"rock_identity"})
add("Sol Ring", 1, "artifact", {"rock_cc"})
add("Talisman of Dominance", 2, "artifact", {"rock_pain_ub"})
add("Tablet of Discovery", 3, "artifact", {"tablet_discovery", "rock_r_or_rr_instsorc"})

# --- Treasure/draw (spellslinger) -------------------------------------------
add("Abandon Attachments", 2, "instant", {"discard_opt_draw2"}, pips={"U/R": 1})
add("An Offer You Can't Refuse", 1, "instant", {"interaction_counter_noncreature"}, pips={"U": 1})
add("Ancestors' Aid", 2, "instant", {"single_target_pump", "make_treasure1"}, pips={"R": 1})
add("Big Score", 4, "instant", {"discard_cost_draw2_treasure2"}, pips={"R": 1})
add("Demand Answers", 2, "instant", {"sac_artifact_or_discard_draw2"}, pips={"R": 1})
add("Unexpected Windfall", 4, "instant", {"discard_cost_draw2_treasure2"}, pips={"R": 2})
add("Storm-Kiln Artist", 4, "creature", {"magecraft_treasure", "pump_per_artifact"}, power=2, pips={"R": 1})
add("Frantic Search", 3, "instant", {"draw2_discard2_untap3"}, pips={"U": 1})
add("Borne Upon a Wind", 2, "instant", {"draw1_flat"}, pips={"U": 1})
add("Thought Scour", 1, "instant", {"mill2_draw1"}, pips={"U": 1})
add("Thrill of Possibility", 2, "instant", {"discard_cost_draw2"}, pips={"R": 1})
add("Sazacap's Brew", 2, "instant", {"discard_cost_draw2_gift"}, pips={"R": 1})

# --- Cantrips de alvo unico (motor de Zada) ---------------------------------
add("Crimson Wisps", 1, "instant", {"single_target_haste", "cantrip_draw"}, pips={"R": 1})
add("Expedite", 1, "instant", {"single_target_haste", "cantrip_draw"}, pips={"R": 1})
add("Leap", 1, "instant", {"single_target_cosmetic", "cantrip_draw"}, pips={"U": 1})
add("Shadow Rift", 1, "instant", {"single_target_cosmetic", "cantrip_draw"}, pips={"U": 1})
add("Fists of Flame", 2, "instant", {"single_target_trample_scaling", "cantrip_draw"}, pips={"R": 1})
add("Titan's Strength", 1, "instant", {"single_target_pump_31", "single_target"}, pips={"R": 1})
add("Brute Force", 1, "instant", {"single_target_pump_33", "single_target"}, pips={"R": 1})
add("Flashback", 1, "instant", {"grant_flashback"}, pips={"R": 1})

# --- Combat tricks (alvo: criatura ATACANTE, casts durante combate) --------
add("Dreadmaw's Ire", 1, "instant", {"attack_trick_pump_22_trample"}, pips={"R": 1})
add("Run Amok", 2, "instant", {"attack_trick_pump_33_trample"}, pips={"R": 1})
add("Temur Battle Rage", 2, "instant", {"single_target_double_strike"}, pips={"R": 1})
add("Lunar Frenzy", 1, "instant", {"single_target_pump_x_fs"}, pips={"R": 1}, )
add("Invigorated Rampage", 2, "instant", {"single_target_pump_40_trample"}, pips={"R": 1})
add("Unleash Fury", 2, "instant", {"single_target_double_power"}, pips={"R": 1})
add("Bulk Up", 2, "instant", {"single_target_double_power", "grant_flashback_big"}, pips={"R": 1})

# --- Copia de magica ---------------------------------------------------------
add("Narset's Reversal", 2, "instant", {"copy_bounce_spell"}, pips={"U": 2})
add("Reiterate", 3, "instant", {"copy_buyback_spell"}, pips={"R": 2})

# --- Dano/remocao -------------------------------------------------------------
add("Chaos Warp", 3, "instant", {"interaction"}, pips={"R": 1})
add("Counterspell", 2, "instant", {"interaction_counter"}, pips={"U": 2})
add("Wash Away", 1, "instant", {"interaction_counter"}, pips={"U": 1})
add("Innocent Blood", 1, "sorcery", {"interaction_edict_symmetric"}, pips={"B": 1})
add("Lightning Bolt", 1, "instant", {"burn3_any"}, pips={"R": 1})
add("Electrodominance", 2, "instant", {"electrodominance"}, pips={"R": 2}, )
add("Chandra's Ignition", 5, "sorcery", {"chandras_ignition"}, pips={"R": 2})
add("Soul's Fire", 3, "instant", {"souls_fire"}, pips={"R": 1})
add("Grapeshot", 2, "sorcery", {"storm_burn"}, pips={"R": 1})
add("Geth's Summons", 4, "sorcery", {"reanimate_own_creature"}, pips={"B": 2})
add("Snap", 2, "instant", {"interaction_bounce_untap2"}, pips={"U": 1})
add("Invoke Calamity", 5, "instant", {"invoke_calamity"}, pips={"R": 4})

# --- Criaturas de valor -------------------------------------------------------
add("Archmage Emeritus", 4, "creature", {"magecraft_draw"}, power=2, pips={"U": 2})
add("Archmage of Runes", 5, "creature", {"cost_reduce_instsorc", "cast_draw_instsorc"}, power=3, pips={"U": 2})
add("Baral, Chief of Compliance", 2, "creature", {"cost_reduce_instsorc", "baral_counter_draw"}, power=1,
    pips={"U": 1})
add("Goblin Electromancer", 2, "creature", {"cost_reduce_instsorc"}, power=2, pips={"U": 1, "R": 1})
add("Nightscape Familiar", 2, "creature", {"cost_reduce_ur"}, power=1, pips={"B": 1})
add("Stormcatch Mentor", 2, "creature", {"cost_reduce_instsorc", "haste", "prowess"}, power=1, pips={"U": 1, "R": 1})
add("Veyran, Voice of Duality", 3, "creature", {"magecraft_selfpump", "veyran_doubler"}, power=2,
    pips={"U": 1, "R": 1})
add("Zada, Hedron Grinder", 4, "creature", {"zada_copy_engine"}, power=3, pips={"R": 1})
add("Giggling Skitterspike", 4, "creature", {"indestructible", "skitterspike_ping", "monstrosity5"}, power=1,
    pips={})
add("Gingerbrute", 1, "creature", {"haste", "gingerbrute_sac"}, power=1, pips={})
add("Kediss, Emberclaw Familiar", 2, "creature", {"kediss_replicate"}, power=1, pips={"R": 1})
add("Torrential Gearhulk", 6, "creature", {"flash", "gearhulk_etb_free_instant"}, power=5, pips={"U": 2})
add("Blazing Firesinger // Seething Song", 3, "creature", {"prepare_seething_song"}, power=2, pips={"R": 1})

# --- Encantamentos -------------------------------------------------------------
add("Firebender Ascension", 2, "enchantment", {"ascension_etb_token", "ascension_quest"}, pips={"R": 1})
add("Frostcliff Siege", 3, "enchantment", {"frostcliff_jeskai_draw"}, pips={"U": 1, "R": 1})
add("Leyline of Anticipation", 4, "enchantment", {"leyline_free_from_hand"}, pips={"U": 2})

# --- MDFC ------------------------------------------------------------------
add("Waterlogged Teachings // Inundated Archive", 4, "instant", {"mdfc_tutor_instant"}, pips={"U/B": 1},
    produces={"U", "B"})
MDFC_LAND_FACES = {"Waterlogged Teachings // Inundated Archive"}

# --- Terrenos --------------------------------------------------------------
LAND_BASIC_TYPES = {
    "Sunken Hollow": {"Island", "Swamp"}, "Watery Grave": {"Island", "Swamp"},
    "Island": {"Island"}, "Mountain": {"Mountain"}, "Swamp": {"Swamp"},
}
add("Choked Estuary", 0, "land", {"revealland_ub"}, produces={"U", "B"})
add("Command Tower", 0, "land", set(), produces={"U", "B", "R"})
add("Darkwater Catacombs", 0, "land", {"filter_ub"}, produces=set())
add("Dragonskull Summit", 0, "land", {"checkland_br"}, produces={"B", "R"})
add("Drowned Catacomb", 0, "land", {"checkland_ub"}, produces={"U", "B"})
add("Emergence Zone", 0, "land", set(), produces=set())
add("Exotic Orchard", 0, "land", {"opponent_dependent"}, produces=set())
add("Fire Nation Palace", 0, "land", {"basicland_tapped", "fire_nation_firebending"}, produces={"R"})
add("Frostboil Snarl", 0, "land", {"revealland_ur"}, produces={"U", "R"})
add("Grixis Panorama", 0, "land", {"sac_fetch_ubr"}, produces=set())
add("Lava Tubes", 0, "land", {"depletion_br"}, produces={"B", "R"})
add("Opal Palace", 0, "land", {"filter_identity_opal"}, produces=set())
add("Secret Tunnel", 0, "land", set(), produces=set())
add("Seething Landscape", 0, "land", {"sac_fetch_ubr"}, produces=set())
add("Shadowblood Ridge", 0, "land", {"filter_br"}, produces=set())
add("Shivan Reef", 0, "land", set(), produces={"U", "R"})
add("Soaring Seacliff", 0, "land", {"etb_tapped"}, produces={"U"})
add("Sunken Hollow", 0, "land", {"battleland2_ub"}, produces={"U", "B"})
add("Underground River", 0, "land", set(), produces={"U", "B"})
add("Watery Grave", 0, "land", {"shockland_ub"}, produces={"U", "B"})
add("Island", 0, "land", set(), produces={"U"})
add("Mountain", 0, "land", set(), produces={"R"})
add("Swamp", 0, "land", set(), produces={"B"})
add("Seething Song", 3, "instant", {"ritual_rrrrr"}, pips={"R": 1})

LAND_NAMES = {n for n, c in CARD_DB.items() if c.ctype == "land"}


def is_creature_card(name: str) -> bool:
    return CARD_DB[name].ctype == "creature"


def is_artifact_card(name: str) -> bool:
    return CARD_DB[name].ctype == "artifact"


def is_instant_sorcery(name: str) -> bool:
    return CARD_DB[name].ctype in ("instant", "sorcery")


SINGLE_TARGET_TAGS = {
    "single_target_haste", "single_target_cosmetic", "single_target_trample_scaling",
    "single_target_pump_31", "single_target_pump_33", "single_target", "single_target_double_strike",
    "single_target_pump_x_fs", "single_target_double_power",
}
ATTACK_ONLY_TAGS = {"attack_trick_pump_22_trample", "attack_trick_pump_33_trample",
                     "single_target_pump_40_trample"}


# ---------------------------------------------------------------------------
# Game state
# ---------------------------------------------------------------------------

@dataclass
class GameState:
    turn: int = 0
    hand: list = field(default_factory=list)
    battlefield: list = field(default_factory=list)
    graveyard: list = field(default_factory=list)
    library: list = field(default_factory=list)
    mulligans: int = 0

    lands_played_this_turn: int = 0
    tapped_land_this_turn: Optional[str] = None
    mana_spent_this_turn: int = 0
    bonus_mana_pool: int = 0  # mana flutuante que expira no fim do turno (Firebending, rituais)
    treasures: int = 0  # persistente entre turnos, so' consumido quando de fato gasto
    creature_cast_turn: dict = field(default_factory=dict)

    commander_in_play: bool = False
    commander_cast_count: int = 0
    commander_cast_turn: Optional[int] = None
    azula_attacking_this_combat: bool = False

    creature_power_mods: dict = field(default_factory=dict)  # nome -> {"add":int,"mult":int}
    spells_cast_this_turn: int = 0

    skitterspike_counters: int = 0
    skitterspike_monstrous: bool = False
    firesinger_prepared: bool = False
    frostcliff_mode: Optional[str] = None
    ascension_quest_counters: int = 0
    lava_tubes_depleted: bool = False
    haste_grants_this_turn: set = field(default_factory=set)
    reiterate_used_this_turn: bool = False
    narset_used_this_turn: bool = False

    # metrics -----------------------------------------------------------------
    proxy_damage_total: int = 0
    cards_drawn_extra: int = 0
    treasures_created_total: int = 0
    interaction_plays: int = 0
    ramp_pieces_cast_total: int = 0
    recursion_events_total: int = 0
    zada_copy_events_total: int = 0
    zada_extra_draws_total: int = 0
    azula_copy_events_total: int = 0
    veyran_doubles_total: int = 0
    storm_grapeshot_events_total: int = 0
    storm_grapeshot_max_damage: int = 0
    ascension_copies_total: int = 0
    skitterspike_pings_total: int = 0
    library_emptied: bool = False


def draw_cards(state: GameState, n: int):
    for _ in range(n):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1
        else:
            state.library_emptied = True


def proxy_burn(state: GameState, n: int):
    state.proxy_damage_total += n


# ---------------------------------------------------------------------------
# Mana
# ---------------------------------------------------------------------------

def ready_creatures(state: GameState):
    return [n for n in state.battlefield if is_creature_card(n)
            and (state.creature_cast_turn.get(n, -1) < state.turn or "haste" in CARD_DB[n].tags
                 or n in state.haste_grants_this_turn)]


def rocks_mana(state: GameState) -> int:
    total = 0
    if "Sol Ring" in state.battlefield:
        total += 2
    if "Arcane Signet" in state.battlefield:
        total += 1
    if "Talisman of Dominance" in state.battlefield:
        total += 1
    if "Tablet of Discovery" in state.battlefield:
        total += 1
    return total


def lands_available(state: GameState) -> int:
    lands = sum(1 for n in state.battlefield if n in LAND_NAMES or n in MDFC_LAND_FACES)
    if state.tapped_land_this_turn is not None:
        lands -= 1
    if "Lava Tubes" in state.battlefield and state.lava_tubes_depleted:
        lands -= 1
    return lands


def total_mana(state: GameState) -> int:
    return lands_available(state) + rocks_mana(state) + state.treasures + state.bonus_mana_pool


def remaining_mana(state: GameState) -> int:
    return max(0, total_mana(state) - state.mana_spent_this_turn)


def color_sources(state: GameState, color: str) -> int:
    n = 0
    for card in state.battlefield:
        if card not in CARD_DB:
            continue
        if card == state.tapped_land_this_turn:
            continue
        if card == "Lava Tubes" and state.lava_tubes_depleted:
            continue
        c = CARD_DB[card]
        if color in c.produces:
            n += 1
        elif "filter_ub" in c.tags and color in ("U", "B"):
            n += 1  # Darkwater Catacombs: {1},{T}: Add UB -- conta como fonte fixa das 2 cores
        elif "filter_br" in c.tags and color in ("B", "R"):
            n += 1  # Shadowblood Ridge
        elif "filter_identity_opal" in c.tags and color in ("U", "B", "R"):
            n += 1  # Opal Palace: {1},{T}: qualquer cor da identidade do comandante
    if state.treasures > 0 or state.bonus_mana_pool > 0:
        n += 1  # Treasure/mana flutuante fixam qualquer cor
    return n


def has_color_sources_for(state: GameState, name: str) -> bool:
    for color, needed in CARD_DB[name].pips.items():
        if "/" in color:  # hibrida (U/R, U/B) -- qualquer uma das duas cobre
            a, b = color.split("/")
            if color_sources(state, a) < needed and color_sources(state, b) < needed:
                return False
            continue
        if color_sources(state, color) < needed:
            return False
    return True


def cost_reduction(state: GameState, name: str) -> int:
    c = CARD_DB[name]
    if c.ctype not in ("instant", "sorcery"):
        return 0
    reduce = 0
    for reducer in ("Baral, Chief of Compliance", "Goblin Electromancer", "Archmage of Runes",
                     "Stormcatch Mentor"):
        if reducer in state.battlefield:
            reduce += 1
    if "Nightscape Familiar" in state.battlefield:
        colors = set(c.pips.keys())
        if colors & {"U", "R", "U/R"} or not colors:
            reduce += 1
    return reduce


def effective_cost(state: GameState, name: str) -> int:
    return max(0, CARD_DB[name].mv - cost_reduction(state, name))


def can_cast(state: GameState, name: str) -> bool:
    return remaining_mana(state) >= effective_cost(state, name) and has_color_sources_for(state, name)


def spend_mana(state: GameState, n: int):
    state.mana_spent_this_turn += n


def crack_fetch(state: GameState):
    candidates = [n for n in state.library if n in LAND_BASIC_TYPES]
    if not candidates:
        return

    def score(land):
        colors = LAND_BASIC_TYPES.get(land, set())
        produces = CARD_DB[land].produces if land in CARD_DB else set()
        want = produces or colors
        return min((color_sources(state, c) for c in want), default=99)

    candidates.sort(key=score)
    pick = candidates[0]
    state.library.remove(pick)
    state.battlefield.append(pick)
    state.tapped_land_this_turn = pick


def land_enters_tapped(state: GameState, name: str) -> bool:
    tags = CARD_DB[name].tags
    if "etb_tapped" in tags:
        return True
    if "revealland_ub" in tags:
        return not any(n in ("Island", "Swamp") for n in state.hand)
    if "revealland_ur" in tags:
        return not any(n in ("Island", "Mountain") for n in state.hand)
    if "checkland_br" in tags:
        return not any(n in ("Swamp", "Mountain") for n in state.battlefield)
    if "checkland_ub" in tags:
        return not any(n in ("Island", "Swamp") for n in state.battlefield)
    if "battleland2_ub" in tags:
        basics = sum(1 for n in state.battlefield if n in ("Island", "Mountain", "Swamp"))
        return basics < 2
    if "basicland_tapped" in tags:
        return not any(n in ("Island", "Mountain", "Swamp") for n in state.battlefield)
    if "shockland_ub" in tags:
        if state.life if hasattr(state, "life") else True:
            pass
        return False  # sempre paga 2 de vida por entrar destapado (premissa: velocidade > vida, mesma de outros sims)
    return False


# ---------------------------------------------------------------------------
# Veyran, Voice of Duality -- multiplicador central de gatilhos
# ---------------------------------------------------------------------------

def veyran_multiplier(state: GameState) -> int:
    return 2 if "Veyran, Voice of Duality" in state.battlefield else 1


# ---------------------------------------------------------------------------
# Evento central de conjurar/copiar instant ou sorcery
# ---------------------------------------------------------------------------

def on_spell_event(state: GameState, name: str, log: list, kind: str = "cast"):
    """Despacha os gatilhos de Magecraft (Archmage Emeritus/Storm-Kiln
    Artist/Veyran) em CAST e em COPY -- 'whenever you cast OR COPY'. Storm
    (contador de spells_cast_this_turn) so' incrementa em CAST real (Storm
    conta magicas CONJURADAS antes dela, nao copias)."""
    mult = veyran_multiplier(state)
    if kind == "cast":
        state.spells_cast_this_turn += 1
    if "Archmage Emeritus" in state.battlefield:
        draw_cards(state, 1 * mult)
    if kind == "cast" and "Archmage of Runes" in state.battlefield:
        # Achado real (varredura de tags orfas): "Whenever you cast an
        # instant or sorcery spell, draw a card" -- so' em CAST (nao em
        # copy, ao contrario do Magecraft), mas ainda e' uma triggered
        # ability de um permanente que controlo causada por conjurar
        # instant/sorcery -- Veyran dobra tambem.
        draw_cards(state, 1 * mult)
    if "Storm-Kiln Artist" in state.battlefield:
        state.treasures += 1 * mult
        state.treasures_created_total += 1 * mult
    if "Veyran, Voice of Duality" in state.battlefield:
        add_pump(state, "Veyran, Voice of Duality", add=1 * mult)
    if mult == 2 and ("Archmage Emeritus" in state.battlefield or "Storm-Kiln Artist" in state.battlefield
                       or "Veyran, Voice of Duality" in state.battlefield
                       or (kind == "cast" and "Archmage of Runes" in state.battlefield)):
        state.veyran_doubles_total += 1


def trigger_prowess(state: GameState, name: str, log: list, is_instsorc: bool):
    # Achado real (varredura de tags orfas): Stormcatch Mentor tem Prowess
    # ("whenever you cast a NONCREATURE spell, +1/+1 until end of turn")
    # -- dispara pra QUALQUER spell nao-criatura (nao so' instant/sorcery),
    # entao e' chamado tanto do caminho de permanentes (artefato/
    # encantamento) quanto do de instant/sorcery. So' e' "triggered
    # ability causada por conjurar/copiar instant OU sorcery" quando
    # `is_instsorc` -- so' nesse caso o dobro da Veyran se aplica.
    if "Stormcatch Mentor" not in state.battlefield or name == "Stormcatch Mentor":
        return
    if CARD_DB[name].ctype == "creature":
        return
    mult = veyran_multiplier(state) if is_instsorc else 1
    add_pump(state, "Stormcatch Mentor", add=1 * mult)


def add_pump(state: GameState, name: str, add: int = 0, mult: int = 1):
    m = state.creature_power_mods.setdefault(name, {"add": 0, "mult": 1})
    m["add"] += add
    m["mult"] *= mult


def creature_power(state: GameState, name: str) -> int:
    base = CARD_DB[name].power
    if name == "Storm-Kiln Artist":
        base += sum(1 for n in state.battlefield if is_artifact_card(n))
    if name == "Giggling Skitterspike":
        base += state.skitterspike_counters
    mod = state.creature_power_mods.get(name, {"add": 0, "mult": 1})
    return max(0, (base + mod["add"]) * mod["mult"])


# ---------------------------------------------------------------------------
# Motor de conjuracao de magica de alvo unico (Zada + Azula, dobrados por
# Veyran) -- o coracao deste deck.
# ---------------------------------------------------------------------------

def other_creatures_count(state: GameState, exclude: str) -> int:
    return sum(1 for n in state.battlefield if is_creature_card(n) and n != exclude)


def resolve_single_target_effect(state: GameState, name: str, target: str, log: list, x_value: int = None):
    tags = CARD_DB[name].tags
    if "cantrip_draw" in tags:
        draw_cards(state, 1)
    if "single_target_haste" in tags:
        state.haste_grants_this_turn.add(target)
    if "single_target_pump_31" in tags:
        add_pump(state, target, add=3)
    if "single_target_pump_33" in tags:
        add_pump(state, target, add=3)
    if "single_target_trample_scaling" in tags:
        add_pump(state, target, add=1)  # aproximado: +1/0 por carta comprada este turno, ver docstring do topo
    if "attack_trick_pump_22_trample" in tags:
        add_pump(state, target, add=2)
    if "attack_trick_pump_33_trample" in tags:
        add_pump(state, target, add=3)
    if "single_target_pump_40_trample" in tags:
        add_pump(state, target, add=4)
    if "single_target_double_strike" in tags:
        add_pump(state, target, mult=2)  # double strike = dano de combate 2x (mesma agregacao)
    if "single_target_double_power" in tags:
        add_pump(state, target, mult=2)
    if "single_target_pump_x_fs" in tags:
        # Achado real (regra 706.10): X e' uma caracteristica da magica,
        # escolhida UMA VEZ ao conjurar -- uma copia (Zada/Azula) usa o
        # MESMO X da original, nao recalcula a mana disponivel no momento
        # de cada copia (isso causava um bug real de crescimento
        # descontrolado: cada copia gerava mais Treasure via Storm-Kiln
        # Artist, inflando `remaining_mana` pra proxima copia na mesma
        # cadeia). `x_value` e' calculado 1x em `cast_single_target_spell`
        # e propagado pra todas as copias da mesma conjuracao.
        x = x_value if x_value is not None else max(0, remaining_mana(state))
        add_pump(state, target, add=x)
    if name == "Giggling Skitterspike" == target:
        pass  # nunca alveja a si mesmo com essas magicas
    if target == "Giggling Skitterspike":
        # Achado real: "whenever this becomes the target of a spell, deals
        # damage = power to each opponent" -- QUALQUER spell, inclusive as
        # nossas proprias, retrigger real ao alveja-lo de proposito.
        proxy_burn(state, creature_power(state, "Giggling Skitterspike"))
        state.skitterspike_pings_total += 1


def cast_single_target_spell(state: GameState, name: str, log: list, prefer_zada: bool = True):
    """Conjura uma magica de alvo unico real, aplicando o motor composto
    Zada (copia pra cada OUTRA criatura, se a magica alvejar SO' Zada) +
    Azula (copia se ela esta atacando), ambos multiplicados por Veyran."""
    spend_mana(state, effective_cost(state, name))
    state.hand.remove(name)
    on_spell_event(state, name, log, kind="cast")
    trigger_prowess(state, name, log, is_instsorc=True)

    has_zada = "Zada, Hedron Grinder" in state.battlefield
    others = other_creatures_count(state, "Zada, Hedron Grinder")
    attack_only = CARD_DB[name].tags & ATTACK_ONLY_TAGS
    can_target_zada = has_zada and others > 0 and not attack_only  # Zada nao ataca (sem tag de ataque valido aqui)

    mult = veyran_multiplier(state)
    x_value = max(0, remaining_mana(state)) if "single_target_pump_x_fs" in CARD_DB[name].tags else None
    if prefer_zada and can_target_zada:
        target = "Zada, Hedron Grinder"
        resolve_single_target_effect(state, name, target, log, x_value=x_value)
        zada_copies = others * mult
        state.zada_copy_events_total += 1
        drawn_before = state.cards_drawn_extra
        other_names = [n for n in state.battlefield if is_creature_card(n) and n != "Zada, Hedron Grinder"]
        for i in range(zada_copies):
            copy_target = other_names[i % len(other_names)] if other_names else target
            on_spell_event(state, name, log, kind="copy")
            resolve_single_target_effect(state, name, copy_target, log, x_value=x_value)
        state.zada_extra_draws_total += state.cards_drawn_extra - drawn_before
    else:
        target = COMMANDER if COMMANDER in state.battlefield else best_pump_target(state)
        resolve_single_target_effect(state, name, target, log, x_value=x_value)

    if state.azula_attacking_this_combat and COMMANDER in state.battlefield:
        azula_copies = 1 * mult
        state.azula_copy_events_total += 1
        for _ in range(azula_copies):
            on_spell_event(state, name, log, kind="copy")
            copy_target = target
            resolve_single_target_effect(state, name, copy_target, log, x_value=x_value)

    state.graveyard.append(name)


BULK_UP_FLASHBACK_COST = 6  # {4}{R}{R} -- diferente do custo impresso ({1}{R}), tratado a parte


def try_bulk_up_flashback(state: GameState, log: list):
    # "Flashback {4}{R}{R}." Distinto da carta "Flashback" (que concede a
    # OUTRA carta um flashback = seu proprio mana cost) -- este e' o
    # flashback IMPRESSO do proprio Bulk Up, custo fixo {4}{R}{R}=6,
    # dispara so' se ja estiver no cemiterio (foi conjurado normalmente
    # antes, possivelmente no mesmo turno via engine Zada/Veyran) e ainda
    # sobrar mana real depois de tudo o mais.
    if "Bulk Up" not in state.graveyard or remaining_mana(state) < BULK_UP_FLASHBACK_COST:
        return
    spend_mana(state, BULK_UP_FLASHBACK_COST)
    state.graveyard.remove("Bulk Up")
    on_spell_event(state, "Bulk Up", log, kind="cast")
    trigger_prowess(state, "Bulk Up", log, is_instsorc=True)
    has_zada = "Zada, Hedron Grinder" in state.battlefield
    others = other_creatures_count(state, "Zada, Hedron Grinder")
    mult = veyran_multiplier(state)
    if has_zada and others > 0:
        resolve_single_target_effect(state, "Bulk Up", "Zada, Hedron Grinder", log)
        other_names = [n for n in state.battlefield if is_creature_card(n) and n != "Zada, Hedron Grinder"]
        for i in range(others * mult):
            on_spell_event(state, "Bulk Up", log, kind="copy")
            resolve_single_target_effect(state, "Bulk Up", other_names[i % len(other_names)], log)
    else:
        target = COMMANDER if COMMANDER in state.battlefield else best_pump_target(state)
        resolve_single_target_effect(state, "Bulk Up", target, log)
    # exilado apos flashback (regra real), nao volta pro cemiterio


def best_pump_target(state: GameState) -> Optional[str]:
    creatures = [n for n in state.battlefield if is_creature_card(n)]
    if not creatures:
        return None
    return max(creatures, key=lambda n: creature_power(state, n))


# ---------------------------------------------------------------------------
# ETBs de permanentes
# ---------------------------------------------------------------------------

def resolve_etb(state: GameState, name: str, log: list):
    tags = CARD_DB[name].tags
    if "ascension_etb_token" in tags:
        # Firebender Ascension: "create a 2/2 red Soldier creature token
        # with firebending 1."
        token = "Soldier Token (Firebending)"
        if token not in CARD_DB:
            add(token, 0, "creature", {"firebending1"}, power=2)
        state.battlefield.append(token)
        state.creature_cast_turn[token] = state.turn
    if "gearhulk_etb_free_instant" in tags:
        # "you may cast target instant card from your graveyard without
        # paying its mana cost" -- prioriza o de maior valor real (Grapeshot
        # se disponivel, pra reaproveitar o storm count atual; senao o de
        # maior mv).
        pool = [c for c in state.graveyard if c in CARD_DB and CARD_DB[c].ctype == "instant"]
        if pool:
            pick = "Grapeshot" if "Grapeshot" in pool else max(pool, key=lambda n: CARD_DB[n].mv)
            state.graveyard.remove(pick)
            cast_free_instant_sorcery(state, pick, log)
    if "leyline_free_from_hand" in tags:
        pass  # tratado no keep/mulligan (entra de graca antes do turno 1)
    if "prepare_seething_song" in tags:
        # Achado real (varredura de tags orfas no proprio rascunho): a tag
        # existia e o motor de "usar Firesinger preparada" ja estava
        # escrito em `try_cast_nontarget_value()`, mas a ETB NUNCA setava
        # `firesinger_prepared = True` -- o motor inteiro era codigo morto.
        state.firesinger_prepared = True
    if "frostcliff_jeskai_draw" in tags:
        # "As this enchantment enters, choose Jeskai or Temur." Escolhe
        # Jeskai (compra ao causar dano de combate) por padrao -- deck de
        # draw engine denso, dano de combate acontece quase todo turno
        # (ataque sem bloqueio), Temur (+1/0 trample haste estatico) e'
        # so' cosmetico sem bloqueadores de oponente pra atravessar.
        state.frostcliff_mode = "jeskai"
    if "tablet_discovery" in tags:
        # "When this artifact enters, mill a card. You may play that card
        # this turn." Se for terreno e ainda nao jogamos terreno, joga
        # direto; se for magica castavel, tenta conjurar (usa a mesma
        # dispatch geral) -- senao fica so' no cemiterio (perdido, real).
        if state.library:
            milled = state.library.pop(0)
            state.graveyard.append(milled)
            if milled in LAND_NAMES and state.lands_played_this_turn < 1:
                state.graveyard.remove(milled)
                state.battlefield.append(milled)
                state.lands_played_this_turn += 1
                if land_enters_tapped(state, milled):
                    state.tapped_land_this_turn = milled
            elif milled in CARD_DB and CARD_DB[milled].ctype != "land" and can_cast(state, milled):
                state.graveyard.remove(milled)
                state.hand.append(milled)
                cast_card(state, milled, log)


def cast_free_instant_sorcery(state: GameState, name: str, log: list):
    """Conjura `name` sem pagar custo (Torrential Gearhulk, Invoke
    Calamity, Electrodominance). Ainda e' um CAST real -- storm,
    magecraft, Zada, Azula, tudo dispara normalmente."""
    tags = CARD_DB[name].tags
    if tags & SINGLE_TARGET_TAGS:
        on_spell_event(state, name, log, kind="cast")
        trigger_prowess(state, name, log, is_instsorc=True)
        has_zada = "Zada, Hedron Grinder" in state.battlefield
        others = other_creatures_count(state, "Zada, Hedron Grinder")
        mult = veyran_multiplier(state)
        x_value = max(0, remaining_mana(state)) if "single_target_pump_x_fs" in tags else None
        if has_zada and others > 0:
            resolve_single_target_effect(state, name, "Zada, Hedron Grinder", log, x_value=x_value)
            other_names = [n for n in state.battlefield if is_creature_card(n) and n != "Zada, Hedron Grinder"]
            for i in range(others * mult):
                on_spell_event(state, name, log, kind="copy")
                resolve_single_target_effect(state, name, other_names[i % len(other_names)], log, x_value=x_value)
        else:
            target = COMMANDER if COMMANDER in state.battlefield else best_pump_target(state)
            resolve_single_target_effect(state, name, target, log, x_value=x_value)
    else:
        on_spell_event(state, name, log, kind="cast")
        trigger_prowess(state, name, log, is_instsorc=True)
        resolve_instant_sorcery(state, name, log, free=True)
    state.graveyard.append(name)


# ---------------------------------------------------------------------------
# Magicas nao-de-alvo-unico (instant/sorcery gerais)
# ---------------------------------------------------------------------------

def resolve_instant_sorcery(state: GameState, name: str, log: list, free: bool = False):
    tags = CARD_DB[name].tags

    if "discard_opt_draw2" in tags:
        # Abandon Attachments: "may discard a card. If you do, draw two."
        if len(state.hand) >= 1:
            discard_worst_and_draw(state, discard_n=1, draw_n=2)

    elif "single_target_pump" in tags and "make_treasure1" in tags:
        # Ancestors' Aid: pump +2/+0 first strike (alvo com maior poder) + Treasure incondicional
        t = best_pump_target(state)
        if t:
            add_pump(state, t, add=2)
        state.treasures += 1
        state.treasures_created_total += 1

    elif "discard_cost_draw2_treasure2" in tags:
        # Big Score / Unexpected Windfall: descarta 1 (custo adicional), compra 2, cria 2 Treasure
        discard_worst_and_draw(state, discard_n=1, draw_n=2)
        state.treasures += 2
        state.treasures_created_total += 2

    elif "sac_artifact_or_discard_draw2" in tags:
        # Demand Answers: sac artefato OU descarta, compra 2 -- prioriza sacrificar
        # um artefato sem valor continuo (Treasure nao existe como permanente
        # aqui, entao sempre descarta -- nenhum artefato "sacrificavel sem perda"
        # nesta lista alem de Treasures, ja tratados como contador).
        discard_worst_and_draw(state, discard_n=1, draw_n=2)

    elif "discard_cost_draw2_gift" in tags:
        # Sazacap's Brew: descarta 1, compra 2 (gift recusado por padrao -- dar
        # um Fish 1/1 tapped ao oponente por +2/0 nosso e' 📊, sem oponente real
        # pra receber o token nem pra medir a troca).
        discard_worst_and_draw(state, discard_n=1, draw_n=2)

    elif "draw2_discard2_untap3" in tags:
        # Frantic Search: compra 2, descarta 2 (liquido zero em cartas), destapa
        # ate 3 terrenos -- ganho real e' MANA (reembolsa ate 3 do custo gasto).
        for _ in range(2):
            if state.library:
                state.hand.append(state.library.pop(0))
        untap_refund = min(3, lands_available(state))
        state.mana_spent_this_turn = max(0, state.mana_spent_this_turn - untap_refund)
        if len(state.hand) >= 2:
            worst = sorted(state.hand, key=lambda c: -CARD_DB[c].mv if c in CARD_DB else 0)[:2]
            for c in worst:
                state.hand.remove(c)
                state.graveyard.append(c)

    elif "draw1_flat" in tags:
        # Borne Upon a Wind: "cast spells this turn as though they had
        # flash" (irrelevante mecanicamente num goldfish -- nunca ha
        # necessidade real de segurar magica pra timing de oponente) +
        # "draw a card" (efeito numerico real).
        draw_cards(state, 1)

    elif "mill2_draw1" in tags:
        for _ in range(2):
            if state.library:
                state.graveyard.append(state.library.pop(0))
        draw_cards(state, 1)

    elif "discard_cost_draw2" in tags:
        discard_worst_and_draw(state, discard_n=1, draw_n=2)

    elif "interaction_counter_noncreature" in tags or "interaction_counter" in tags:
        state.interaction_plays += 1  # precisa spell de oponente real -- 📊

    elif "interaction" in tags:
        state.interaction_plays += 1

    elif "interaction_edict_symmetric" in tags:
        state.interaction_plays += 1  # Regra 1: simetrico sem oponente = so' metrica

    elif "interaction_bounce_untap2" in tags:
        state.interaction_plays += 1  # Snap precisa alvo de criatura (nossa ou de oponente) -- 📊 por padrao

    elif "burn3_any" in tags:
        proxy_burn(state, 3)

    elif "electrodominance" in tags:
        # "X damage to any target. You may cast a spell mv<=X from hand free."
        x = max(0, remaining_mana(state))
        if not free:
            spend_mana(state, x)
        proxy_burn(state, x)
        castable = [c for c in state.hand if c in CARD_DB and CARD_DB[c].mv <= x
                    and CARD_DB[c].ctype not in ("land",)]
        if castable:
            pick = max(castable, key=lambda n: CARD_DB[n].mv)
            state.hand.remove(pick)
            if CARD_DB[pick].ctype in ("instant", "sorcery"):
                cast_free_instant_sorcery(state, pick, log)
            else:
                enter_battlefield(state, pick, log, free=True)

    elif "chandras_ignition" in tags:
        # Regra 1: atinge nossas outras criaturas tambem (sem oponente pra
        # tambem sofrer) -- so' conta o dano proxy representando "each
        # opponent", nao destroi nossas proprias criaturas.
        t = best_pump_target(state)
        if t:
            proxy_burn(state, creature_power(state, t))

    elif "souls_fire" in tags:
        t = best_pump_target(state)
        if t:
            proxy_burn(state, creature_power(state, t))

    elif "storm_burn" in tags:
        # Storm real: "copy for each spell cast BEFORE it this turn."
        # `spells_cast_this_turn` ja foi incrementado (inclui o proprio
        # Grapeshot) por `on_spell_event()` antes deste dispatch rodar --
        # dano total = 1 (original) + copias = o proprio contador.
        damage = state.spells_cast_this_turn
        proxy_burn(state, damage)
        state.storm_grapeshot_events_total += 1
        state.storm_grapeshot_max_damage = max(state.storm_grapeshot_max_damage, damage)

    elif "reanimate_own_creature" in tags:
        pool = [c for c in state.graveyard if is_creature_card(c)]
        if pool:
            best = max(pool, key=lambda n: CARD_DB[n].mv)
            state.graveyard.remove(best)
            enter_battlefield(state, best, log, free=True)
            state.recursion_events_total += 1

    elif "invoke_calamity" in tags:
        # "cast up to two instant/sorcery mv total <=6 from GY/hand free"
        pool = [c for c in (state.graveyard + state.hand)
                if c in CARD_DB and CARD_DB[c].ctype in ("instant", "sorcery") and c != name]
        pool.sort(key=lambda n: -CARD_DB[n].mv)
        chosen, total = [], 0
        for c in pool:
            if total + CARD_DB[c].mv <= 6 and len(chosen) < 2:
                chosen.append(c)
                total += CARD_DB[c].mv
        for c in chosen:
            if c in state.graveyard:
                state.graveyard.remove(c)
            elif c in state.hand:
                state.hand.remove(c)
            cast_free_instant_sorcery(state, c, log)

    elif "ritual_rrrrr" in tags:
        state.bonus_mana_pool += 5

    elif "grant_flashback" in tags:
        # Achado real (varredura de tags orfas): a carta "Flashback"
        # ({R} instant, "target instant/sorcery in your graveyard gains
        # flashback until end of turn, flashback cost = mana cost") era
        # so' um dreno de mana sem efeito nenhum -- nunca concedia nem
        # conjurava nada. Corrigido: concede + conjura de imediato (mesmo
        # turno, unica janela em que a flashback concedida existe) o
        # instant/sorcery de maior mv castavel no cemiterio.
        pool = [c for c in state.graveyard if c in CARD_DB and CARD_DB[c].ctype in ("instant", "sorcery")
                and c != "Flashback" and remaining_mana(state) >= effective_cost(state, c)]
        if pool:
            pick = max(pool, key=lambda n: CARD_DB[n].mv)
            state.graveyard.remove(pick)
            cast_via_flashback(state, pick, log)


def cast_via_flashback(state: GameState, name: str, log: list):
    """Conjura `name` do cemiterio pagando seu custo normal (flashback
    concedida pela carta 'Flashback'), exilando ao final em vez de voltar
    ao cemiterio (regra real de flashback)."""
    cost = effective_cost(state, name)
    if remaining_mana(state) < cost:
        return
    spend_mana(state, cost)
    tags = CARD_DB[name].tags
    on_spell_event(state, name, log, kind="cast")
    trigger_prowess(state, name, log, is_instsorc=True)
    if tags & SINGLE_TARGET_TAGS:
        has_zada = "Zada, Hedron Grinder" in state.battlefield
        others = other_creatures_count(state, "Zada, Hedron Grinder")
        mult = veyran_multiplier(state)
        x_value = max(0, remaining_mana(state)) if "single_target_pump_x_fs" in tags else None
        if has_zada and others > 0:
            resolve_single_target_effect(state, name, "Zada, Hedron Grinder", log, x_value=x_value)
            other_names = [n for n in state.battlefield if is_creature_card(n) and n != "Zada, Hedron Grinder"]
            for i in range(others * mult):
                on_spell_event(state, name, log, kind="copy")
                resolve_single_target_effect(state, name, other_names[i % len(other_names)], log, x_value=x_value)
        else:
            target = COMMANDER if COMMANDER in state.battlefield else best_pump_target(state)
            resolve_single_target_effect(state, name, target, log, x_value=x_value)
    else:
        resolve_instant_sorcery(state, name, log)
    # exilado (regra real de flashback) -- nao volta pro cemiterio


def discard_worst_and_draw(state: GameState, discard_n: int, draw_n: int):
    draw_cards(state, draw_n)
    for _ in range(discard_n):
        if not state.hand:
            break
        worst = min(state.hand, key=lambda c: CARD_DB[c].mv if c in CARD_DB else 0)
        state.hand.remove(worst)
        state.graveyard.append(worst)


# ---------------------------------------------------------------------------
# Entrar em campo (criaturas/artefatos/encantamentos)
# ---------------------------------------------------------------------------

def enter_battlefield(state: GameState, name: str, log: list, free: bool = False):
    state.battlefield.append(name)
    if is_creature_card(name):
        state.creature_cast_turn[name] = state.turn
    resolve_etb(state, name, log)


def cast_permanent(state: GameState, name: str, log: list):
    cost = effective_cost(state, name)
    spend_mana(state, cost)
    state.hand.remove(name)
    if name == COMMANDER:
        state.commander_in_play = True
        state.commander_cast_count += 1
        if state.commander_cast_turn is None:
            state.commander_cast_turn = state.turn
    enter_battlefield(state, name, log)
    if CARD_DB[name].ctype != "creature":
        trigger_prowess(state, name, log, is_instsorc=False)


def cast_card(state: GameState, name: str, log: list):
    ctype = CARD_DB[name].ctype
    if ctype == "land":
        return
    if ctype in ("creature", "artifact", "enchantment"):
        cast_permanent(state, name, log)
        return
    tags = CARD_DB[name].tags
    if tags & SINGLE_TARGET_TAGS:
        cast_single_target_spell(state, name, log)
        return
    cost = effective_cost(state, name)
    spend_mana(state, cost)
    state.hand.remove(name)
    on_spell_event(state, name, log, kind="cast")
    trigger_prowess(state, name, log, is_instsorc=True)
    resolve_instant_sorcery(state, name, log)
    if "invoke_calamity" not in tags:
        state.graveyard.append(name)


# ---------------------------------------------------------------------------
# Terreno
# ---------------------------------------------------------------------------

def play_land(state: GameState, log: list):
    if state.lands_played_this_turn >= 1:
        return
    hand_lands = [n for n in state.hand if n in LAND_NAMES or n in MDFC_LAND_FACES]
    if not hand_lands:
        return

    def score(n):
        if n in MDFC_LAND_FACES:
            return 1
        return 1 if land_enters_tapped(state, n) else 0

    hand_lands.sort(key=score)
    pick = hand_lands[0]
    state.hand.remove(pick)
    state.lands_played_this_turn += 1
    if pick in MDFC_LAND_FACES:
        state.battlefield.append(pick)
        state.tapped_land_this_turn = pick
        return
    if "sac_fetch_ubr" in CARD_DB[pick].tags:
        crack_fetch(state)
        return
    tapped = land_enters_tapped(state, pick)
    state.battlefield.append(pick)
    if tapped:
        state.tapped_land_this_turn = pick


# ---------------------------------------------------------------------------
# Rampa/permanentes/valor-nao-alvo-unico (main phase 1 e sobra do main 2)
# ---------------------------------------------------------------------------

ROCK_TAGS = {"rock_identity", "rock_cc", "rock_pain_ub", "tablet_discovery"}
ENGINE_CREATURES = {
    "Zada, Hedron Grinder", "Veyran, Voice of Duality", "Baral, Chief of Compliance",
    "Goblin Electromancer", "Archmage of Runes", "Stormcatch Mentor", "Nightscape Familiar",
    "Archmage Emeritus", "Storm-Kiln Artist",
}
NONTARGET_VALUE_TAGS = {
    "discard_opt_draw2", "discard_cost_draw2_treasure2", "sac_artifact_or_discard_draw2",
    "discard_cost_draw2_gift", "draw2_discard2_untap3", "mill2_draw1", "discard_cost_draw2",
    "reanimate_own_creature",
}


def try_cast_permanents(state: GameState, log: list):
    changed = True
    while changed:
        changed = False
        candidates = [n for n in state.hand if CARD_DB[n].ctype in ("creature", "artifact", "enchantment")
                      and can_cast(state, n)]
        if not candidates:
            break

        def prio(n):
            if n == COMMANDER:
                return 0
            if CARD_DB[n].tags & ROCK_TAGS:
                return 1
            if n in ENGINE_CREATURES:
                return 2
            return 3

        pick = min(candidates, key=lambda n: (prio(n), effective_cost(state, n)))
        cast_permanent(state, pick, log)
        changed = True


def try_cast_nontarget_value(state: GameState, log: list):
    changed = True
    while changed:
        changed = False
        candidates = [n for n in state.hand if CARD_DB[n].tags & NONTARGET_VALUE_TAGS and can_cast(state, n)]
        if state.firesinger_prepared and remaining_mana(state) >= 3:
            # Blazing Firesinger preparada: "cast a copy" de Seething Song
            # (leitura literal do oraculo -- reminder text NAO diz "without
            # paying its mana cost", diferente do padrao usado noutras
            # mecanicas free-cast -- entao paga o custo normal {2}{R}).
            # Ritual real: +2 de mana liquido, e' um CAST de verdade (conta
            # pra storm/magecraft).
            spend_mana(state, 3)
            state.firesinger_prepared = False
            on_spell_event(state, "Seething Song", log, kind="cast")
            state.bonus_mana_pool += 5
            changed = True
            continue
        if not candidates:
            break
        pick = min(candidates, key=lambda n: effective_cost(state, n))
        cast_card(state, pick, log)
        changed = True


def try_cast_mdfc_instant_side(state: GameState, log: list):
    name = "Waterlogged Teachings // Inundated Archive"
    if name in state.hand and can_cast(state, name):
        spend_mana(state, effective_cost(state, name))
        state.hand.remove(name)
        on_spell_event(state, name, log, kind="cast")
        pool = [c for c in state.library if c in CARD_DB
                and (CARD_DB[c].ctype == "instant" or "flash" in CARD_DB[c].tags)]
        if pool:
            pick = max(pool, key=lambda n: CARD_DB[n].mv)
            state.library.remove(pick)
            state.hand.append(pick)
        state.graveyard.append(name)


# ---------------------------------------------------------------------------
# Combate
# ---------------------------------------------------------------------------

def try_cast_single_target_tricks(state: GameState, log: list):
    changed = True
    while changed:
        changed = False
        candidates = [n for n in state.hand if (CARD_DB[n].tags & SINGLE_TARGET_TAGS) and can_cast(state, n)]
        if not candidates:
            break
        pick = min(candidates, key=lambda n: effective_cost(state, n))
        cast_single_target_spell(state, pick, log)
        changed = True


def combat_step(state: GameState, log: list):
    attackers = ready_creatures(state)
    if not attackers:
        return
    state.azula_attacking_this_combat = COMMANDER in attackers

    if state.azula_attacking_this_combat:
        state.bonus_mana_pool += 2  # Firebending 2
        if ("Fire Nation Palace" in state.battlefield and remaining_mana(state) >= 2
                and color_sources(state, "R") >= 1):
            spend_mana(state, 2)
            state.bonus_mana_pool += 4  # firebending 4 concedida, dispara junto com o ataque

    try_cast_single_target_tricks(state, log)

    total_power = sum(creature_power(state, n) for n in attackers)
    proxy_burn(state, total_power)

    if state.frostcliff_mode == "jeskai" and total_power > 0:
        draw_cards(state, 1)

    if "Giggling Skitterspike" in attackers:
        proxy_burn(state, creature_power(state, "Giggling Skitterspike"))
        state.skitterspike_pings_total += 1

    fb_attackers = [n for n in attackers if CARD_DB[n].tags & {"firebending2", "firebending1"}]
    if "Firebender Ascension" in state.battlefield and fb_attackers:
        # "whenever a creature you control attacking causes a triggered
        # ability of that creature to trigger, put a quest counter. At 4+,
        # copy that ability." Aproximado: cada permanente com Firebending
        # que ataca conta 1 quest counter (o proprio gatilho de Firebending
        # e' a triggered ability em questao); ao acumular 4, "copia" um
        # desses gatilhos -- aproximado como +2 de dano proxy (equivalente
        # a mais uma rodada pequena de Firebending convertida em valor),
        # mesmo padrao de aproximacao documentada do Ba Sing Se no Kutzil.
        state.ascension_quest_counters += len(fb_attackers)
        while state.ascension_quest_counters >= 4:
            state.ascension_quest_counters -= 4
            state.ascension_copies_total += 1
            proxy_burn(state, 2)

    state.azula_attacking_this_combat = False


# ---------------------------------------------------------------------------
# Finalizador de storm (Grapeshot + Narset's Reversal/Reiterate)
# ---------------------------------------------------------------------------

def try_storm_finish(state: GameState, log: list):
    if "Grapeshot" in state.hand and can_cast(state, "Grapeshot"):
        cast_card(state, "Grapeshot", log)
        grapeshot_damage = state.storm_grapeshot_max_damage
        for copier, flagname in (("Narset's Reversal", "narset_used_this_turn"),
                                  ("Reiterate", "reiterate_used_this_turn")):
            if (copier in state.hand and can_cast(state, copier) and not getattr(state, flagname)
                    and "Grapeshot" in state.graveyard):
                spend_mana(state, effective_cost(state, copier))
                state.hand.remove(copier)
                on_spell_event(state, copier, log, kind="cast")
                on_spell_event(state, "Grapeshot", log, kind="copy")
                proxy_burn(state, grapeshot_damage)
                state.graveyard.append(copier)
                setattr(state, flagname, True)


def try_cast_remaining_value(state: GameState, log: list):
    changed = True
    while changed:
        changed = False
        candidates = [n for n in state.hand if CARD_DB[n].ctype in ("instant", "sorcery")
                      and n != "Grapeshot" and not (CARD_DB[n].tags & SINGLE_TARGET_TAGS)
                      and can_cast(state, n)]
        if not candidates:
            break
        pick = min(candidates, key=lambda n: effective_cost(state, n))
        cast_card(state, pick, log)
        changed = True


# ---------------------------------------------------------------------------
# Ativacoes diversas (Skitterspike monstrosity)
# ---------------------------------------------------------------------------

def try_activated_abilities(state: GameState, log: list):
    if ("Giggling Skitterspike" in state.battlefield and not state.skitterspike_monstrous
            and remaining_mana(state) >= 5):
        spend_mana(state, 5)
        state.skitterspike_counters += 5
        state.skitterspike_monstrous = True


# ---------------------------------------------------------------------------
# Turno completo
# ---------------------------------------------------------------------------

def cleanup_lava_tubes(state: GameState):
    if "Lava Tubes" not in state.battlefield:
        return
    if state.lava_tubes_depleted:
        state.lava_tubes_depleted = False
        return
    if state.mana_spent_this_turn >= lands_available(state) + rocks_mana(state) + state.treasures:
        state.lava_tubes_depleted = True


def try_cast_commander(state: GameState, log: list):
    """Azula vem da zona de comando, NAO da biblioteca (BASE_LIBRARY tem
    so' as 99 cartas de deck, sem o comandante -- mesmo padrao usado no
    Kutzil/Megatron desta sessao). Achado real (varredura de conjuracao
    fim-a-fim): sem este passo dedicado, `try_cast_permanents()` nunca
    conjura Azula (ela nunca esta em `state.hand`), entao ela NUNCA entra
    em campo -- bug real que zerava o motor inteiro do comandante (sem
    Azula em campo, Firebending e o gatilho de copia dela nunca disparam)."""
    if state.commander_in_play or not can_cast(state, COMMANDER):
        return
    cost = effective_cost(state, COMMANDER)
    spend_mana(state, cost)
    state.commander_in_play = True
    state.commander_cast_count += 1
    if state.commander_cast_turn is None:
        state.commander_cast_turn = state.turn
    enter_battlefield(state, COMMANDER, log)


def run_turn(state: GameState, log: list):
    state.turn += 1
    state.lands_played_this_turn = 0
    state.tapped_land_this_turn = None
    state.mana_spent_this_turn = 0
    state.bonus_mana_pool = 0
    state.creature_power_mods = {}
    state.spells_cast_this_turn = 0
    state.haste_grants_this_turn = set()
    state.reiterate_used_this_turn = False
    state.narset_used_this_turn = False

    draw_cards(state, 1)
    play_land(state, log)
    try_cast_commander(state, log)
    try_cast_permanents(state, log)
    try_cast_nontarget_value(state, log)
    try_cast_mdfc_instant_side(state, log)
    try_activated_abilities(state, log)
    try_cast_commander(state, log)  # pode ter ficado castavel so' depois dos rituais/rocks acima
    try_cast_permanents(state, log)  # mana liberada por rituais pode abrir mais permanentes

    combat_step(state, log)

    try_cast_nontarget_value(state, log)
    try_cast_remaining_value(state, log)
    try_cast_single_target_tricks(state, log)
    try_bulk_up_flashback(state, log)
    try_storm_finish(state, log)
    try_cast_remaining_value(state, log)

    while len(state.hand) > 7:
        worst = min(state.hand, key=lambda c: CARD_DB[c].mv if c in CARD_DB else 0)
        state.hand.remove(worst)
        state.graveyard.append(worst)

    cleanup_lava_tubes(state)


# ---------------------------------------------------------------------------
# Decklist
# ---------------------------------------------------------------------------

DECKLIST_TEXT = """
1 Abandon Attachments
1 An Offer You Can't Refuse
1 Ancestors' Aid
1 Arcane Signet
1 Archmage Emeritus
1 Archmage of Runes
1 Baral, Chief of Compliance
1 Big Score
1 Blazing Firesinger // Seething Song
1 Borne Upon a Wind
1 Brute Force
1 Bulk Up
1 Chandra's Ignition
1 Chaos Warp
1 Counterspell
1 Crimson Wisps
1 Demand Answers
1 Dreadmaw's Ire
1 Electrodominance
1 Expedite
1 Firebender Ascension
1 Fists of Flame
1 Flashback
1 Frantic Search
1 Frostcliff Siege
1 Geth's Summons
1 Giggling Skitterspike
1 Gingerbrute
1 Goblin Electromancer
1 Grapeshot
1 Innocent Blood
1 Invigorated Rampage
1 Invoke Calamity
1 Kediss, Emberclaw Familiar
1 Leap
1 Leyline of Anticipation
1 Lightning Bolt
1 Lunar Frenzy
1 Narset's Reversal
1 Nightscape Familiar
1 Reiterate
1 Run Amok
1 Sazacap's Brew
1 Seething Song
1 Shadow Rift
1 Snap
1 Sol Ring
1 Soul's Fire
1 Storm-Kiln Artist
1 Stormcatch Mentor
1 Tablet of Discovery
1 Talisman of Dominance
1 Temur Battle Rage
1 Thought Scour
1 Thrill of Possibility
1 Titan's Strength
1 Torrential Gearhulk
1 Unexpected Windfall
1 Unleash Fury
1 Veyran, Voice of Duality
1 Wash Away
1 Waterlogged Teachings // Inundated Archive
1 Zada, Hedron Grinder
1 Choked Estuary
1 Command Tower
1 Darkwater Catacombs
1 Dragonskull Summit
1 Drowned Catacomb
1 Emergence Zone
1 Exotic Orchard
1 Fire Nation Palace
1 Frostboil Snarl
1 Grixis Panorama
6 Island
1 Lava Tubes
5 Mountain
1 Opal Palace
1 Secret Tunnel
1 Seething Landscape
1 Shadowblood Ridge
1 Shivan Reef
1 Soaring Seacliff
1 Sunken Hollow
5 Swamp
1 Underground River
1 Watery Grave
"""


def parse_decklist(text: str) -> list:
    cards = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        n, name = line.split(" ", 1)
        cards.extend([name] * int(n))
    return cards


BASE_LIBRARY = parse_decklist(DECKLIST_TEXT)
assert len(BASE_LIBRARY) == 99, f"esperado 99 cartas na biblioteca, achei {len(BASE_LIBRARY)}"
for _card_name in set(BASE_LIBRARY):
    assert _card_name in CARD_DB, f"carta na decklist sem entrada no CARD_DB: {_card_name}"

KEEPERS = {"Sol Ring", "Arcane Signet", "Talisman of Dominance", COMMANDER}


def should_keep(hand: list, mulligans: int) -> bool:
    lands = sum(1 for c in hand if c in LAND_NAMES or c in MDFC_LAND_FACES)
    if mulligans >= 3:
        return True
    if lands < 2 or lands > 5:
        return False
    return True


def bottom_priority(card: str) -> int:
    if card in LAND_NAMES or card in MDFC_LAND_FACES:
        return 0
    if card == COMMANDER:
        return 5
    return CARD_DB[card].mv if card in CARD_DB else 1


def mulligan(state: GameState):
    mulls = 0
    while True:
        hand = state.library[:7]
        rest = state.library[7:]
        if should_keep(hand, mulls) or mulls >= 4:
            ordered = sorted(hand, key=bottom_priority, reverse=True)
            bottom = ordered[:mulls]
            keep = ordered[mulls:]
            state.hand = keep
            state.library = rest + bottom
            state.mulligans = mulls
            return
        mulls += 1
        random.shuffle(state.library)


# ---------------------------------------------------------------------------
# Simulacao
# ---------------------------------------------------------------------------

def simulate_one(seed: int, turns: int = 10) -> GameState:
    rnd = random.Random(seed)
    state = GameState()
    state.library = BASE_LIBRARY[:]
    rnd.shuffle(state.library)
    mulligan(state)

    if "Leyline of Anticipation" in state.hand:
        state.hand.remove("Leyline of Anticipation")
        state.battlefield.append("Leyline of Anticipation")

    log = []
    for _ in range(turns):
        run_turn(state, log)
    return state


def run_batch(n: int, seed_base: int = 1_000_000, turns: int = 10, out_path: str = None):
    results = []
    exceptions = 0
    for i in range(n):
        try:
            state = simulate_one(seed_base + i, turns=turns)
            results.append(state)
        except Exception as e:
            exceptions += 1
            if exceptions <= 5:
                print(f"EXCEPTION seed={seed_base + i}: {e}")
    print(f"Rodadas: {n}, excecoes: {exceptions}")
    if not results:
        return results

    def avg(fn):
        return statistics.mean(fn(s) for s in results)

    print(f"Dano proxy medio: {avg(lambda s: s.proxy_damage_total):.1f}")
    print(f"Dano proxy mediano: {statistics.median(s.proxy_damage_total for s in results):.1f}")
    print(f"Dano proxy max: {max(s.proxy_damage_total for s in results)}")
    print(f"Cartas compradas extra (media): {avg(lambda s: s.cards_drawn_extra):.1f}")
    print(f"Treasures criados (media): {avg(lambda s: s.treasures_created_total):.1f}")
    print(f"Eventos de copia Zada (media): {avg(lambda s: s.zada_copy_events_total):.1f}")
    print(f"Draws extra via Zada (media): {avg(lambda s: s.zada_extra_draws_total):.1f}")
    print(f"Copias via Azula atacando (media): {avg(lambda s: s.azula_copy_events_total):.1f}")
    print(f"Dobras via Veyran (media): {avg(lambda s: s.veyran_doubles_total):.1f}")
    print(f"Grapeshots conjurados (media): {avg(lambda s: s.storm_grapeshot_events_total):.2f}")
    print(f"Maior dano de 1 Grapeshot (max entre partidas): {max(s.storm_grapeshot_max_damage for s in results)}")
    print(f"Interacao jogada (media): {avg(lambda s: s.interaction_plays):.1f}")
    print(f"Mulligans (media): {avg(lambda s: s.mulligans):.2f}")
    print(f"Biblioteca esgotada em: {sum(1 for s in results if s.library_emptied)}/{n}")

    if out_path:
        with open(out_path, "w") as f:
            for s in results:
                row = {
                    "proxy_damage_total": s.proxy_damage_total,
                    "cards_drawn_extra": s.cards_drawn_extra,
                    "treasures_created_total": s.treasures_created_total,
                    "zada_copy_events_total": s.zada_copy_events_total,
                    "zada_extra_draws_total": s.zada_extra_draws_total,
                    "azula_copy_events_total": s.azula_copy_events_total,
                    "veyran_doubles_total": s.veyran_doubles_total,
                    "storm_grapeshot_events_total": s.storm_grapeshot_events_total,
                    "storm_grapeshot_max_damage": s.storm_grapeshot_max_damage,
                    "interaction_plays": s.interaction_plays,
                    "mulligans": s.mulligans,
                    "library_emptied": s.library_emptied,
                }
                f.write(json.dumps(row) + "\n")
    return results


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "azula_v1_runs.jsonl")
    run_batch(3000, seed_base=1_000_000, turns=8, out_path=out)
