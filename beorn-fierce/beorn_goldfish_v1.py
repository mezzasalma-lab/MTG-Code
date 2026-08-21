#!/usr/bin/env python3
"""
Beorn the Fierce — Goldfish Simulator v1
Escrito por Claude (nao pelo usuario). Heuristico, nao e um motor de regras completo.
Tags derivadas de oracle_text real (Scryfall), nao inventadas.
Modelo de mana simplificado por ser mono-verde: total de fontes de mana (contagem),
mais uma checagem separada de "fontes verdes" pra cartas com pip GG/GGG/GGGG,
ja que 4 terrenos do deck (War Room, Scavenger Grounds, Nykthos, Reliquary Tower)
so produzem incolor a menos que Yavimaya (que faz todo terreno virar Floresta) esteja em campo.
"""

from __future__ import annotations
import random, json, statistics
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional

COMMANDER = "Beorn the Fierce"

DECKLIST_TEXT = r"""
1 Ambush Viper
1 Archdruid's Charm
1 Ayula, Queen Among Bears
1 Ayula's Influence
1 Bala Ged Recovery // Bala Ged Sanctuary
1 Beast Whisperer
1 Beast Within
1 Beorn, Reluctant Host
1 Beorn's Hospitality
1 Birds of Paradise
1 Chameleon Colossus
1 Chronicle of Victory
1 Cultivate
1 Craterhoof Behemoth
1 Dancing from Dark to Dawn
1 Emerald Medallion
1 Eternal Witness
1 Ezuri's Predation
1 Firdoch Core
1 Forgotten Ancient
1 Lumra, Bellow of the Woods
1 Garruk's Uprising
1 Genji Glove
1 Germination Practicum
1 The Great Henge
1 Ghalta, Primal Hunger
1 Gigantic Big Bear
1 Goreclaw, Terror of Qal Sisma
1 Haywire Mite
1 Heroic Intervention
1 Allosaurus Shepherd
1 Last March of the Ents
1 Lightning Greaves
1 Little Bear
1 Llanowar Elves
1 Lotus Cobra
1 Managorger Hydra
1 Maskwood Nexus
1 Necklace of Girion
1 Natural Order
1 Obscuring Haze
1 Ohran Frostfang
1 Patchwork Banner
1 Radagast of Rhosgobel
1 Defiler of Vigor
1 Return of the Wildspeaker
1 Roaming Throne
1 Sakura-Tribe Elder
1 Selvala, Heart of the Wilds
1 Shamanic Revelation
1 Sol Ring
1 Solemn Simulacrum
1 Song of the Dryads
1 Thought Vessel
1 Springleaf Parade
1 Three Visits
1 Tireless Provisioner
1 Tireless Tracker
1 Titania's Command
1 Toski, Bearer of Secrets
1 Tribute to the World Tree
1 Unnatural Growth
1 War Room
1 Scavenger Grounds
1 Nykthos, Shrine to Nyx
1 Yavimaya, Cradle of Growth
1 Reliquary Tower
1 Boseiju, Who Endures
31 Forest
"""

# =========================================================
# CARD MODEL
# =========================================================

@dataclass
class Card:
    name: str
    mv: int
    types: Set[str]
    tags: Set[str] = field(default_factory=set)
    g_pips: int = 0          # quantos simbolos {G} no custo (0 pra terrenos/rocks incolores)
    notes: Dict = field(default_factory=dict)

CARD_DB: Dict[str, Card] = {}

def add(name, mv, types, tags=None, g_pips=0, notes=None):
    CARD_DB[name] = Card(name, mv, set(types), set(tags or []), g_pips, dict(notes or {}))

def C(name: str) -> Card:
    return CARD_DB.get(name, Card(name, 3, {"Spell"}))

def is_land(name): return "Land" in C(name).types
def is_creature(name): return "Creature" in C(name).types
def is_spell(name): return not is_land(name)
def has_tag(name, tag): return tag in C(name).tags

# Commander — Beorn the Fierce {3}{G}{G}
add(COMMANDER, 5, {"Creature"}, {"commander","bear"}, g_pips=2,
    notes={"anthem_bear": True})

# -------- Lands --------
# green_source: produz G diretamente. c_only: so incolor a menos que Yavimaya esteja em campo.
land_defs = [
    ("War Room", {"c_only"}),
    ("Scavenger Grounds", {"c_only"}),
    ("Nykthos, Shrine to Nyx", {"c_only"}),
    ("Yavimaya, Cradle of Growth", {"green_source","makes_all_forests"}),
    ("Reliquary Tower", {"c_only","no_max_hand"}),
    ("Boseiju, Who Endures", {"green_source","removal_channel"}),
    ("Forest", {"green_source","basic"}),
    ("Bala Ged Recovery // Bala Ged Sanctuary", {"green_source"}),  # land side (Sanctuary)
]
for name, tags in land_defs:
    add(name, 0, {"Land"}, tags)

# -------- Ramp / mana --------
ramp_defs = [
    ("Birds of Paradise", 1, {"Creature"}, {"ramp","green_source_any"}),
    ("Llanowar Elves", 1, {"Creature"}, {"ramp","green_source"}),
    ("Sol Ring", 1, {"Artifact"}, {"ramp","fast_mana","c_only"}),
    ("Lotus Cobra", 2, {"Creature"}, {"ramp","landfall_mana"}),
    ("Selvala, Heart of the Wilds", 3, {"Creature"}, {"ramp","green_source_any","legendary","draw_engine_conditional"}),
    ("Thought Vessel", 2, {"Artifact"}, {"ramp","c_only","no_max_hand"}),
    ("Firdoch Core", 3, {"Artifact"}, {"ramp","green_source_any","changeling","bear_type"}),
    ("Necklace of Girion", 3, {"Artifact"}, {"ramp","green_source","legendary","counters_engine"}),
    ("Patchwork Banner", 3, {"Artifact"}, {"ramp","green_source_any","anthem_tribal"}),
    ("Cultivate", 3, {"Sorcery"}, {"ramp","land_ramp"}),
    ("Sakura-Tribe Elder", 1, {"Creature"}, {"ramp","land_ramp","chump"}),
    ("Three Visits", 2, {"Sorcery"}, {"ramp","land_ramp"}),
    ("Solemn Simulacrum", 4, {"Creature"}, {"ramp","land_ramp","draw_on_death"}),
    ("Emerald Medallion", 2, {"Artifact"}, {"cost_reducer"}),
    ("Radagast of Rhosgobel", 4, {"Creature"}, {"cost_reducer","legendary"}),
]
for name, mv, typ, tags in ramp_defs:
    add(name, mv, typ, tags, g_pips=(1 if "green_source" in tags and "green_source_any" not in tags else 0))

# -------- Card draw --------
draw_defs = [
    ("Beast Whisperer", 4, {"Creature"}, {"draw_engine"}),
    ("Garruk's Uprising", 3, {"Enchantment"}, {"draw_engine","trample_anthem"}),
    ("Ohran Frostfang", 5, {"Creature"}, {"draw_engine","deathtouch_anthem"}),
    ("Toski, Bearer of Secrets", 4, {"Creature"}, {"draw_engine","legendary","indestructible"}),
    ("Return of the Wildspeaker", 5, {"Instant"}, {"burst_draw"}),
    ("Shamanic Revelation", 5, {"Sorcery"}, {"burst_draw"}),
    ("The Great Henge", 9, {"Artifact"}, {"draw_engine","legendary","cost_reducer_power","counters_engine"}),
    ("Tireless Tracker", 3, {"Creature"}, {"draw_engine","landfall"}),
    ("Last March of the Ents", 8, {"Sorcery"}, {"burst_draw","cheat_into_play","finisher_setup"}),
]
for name, mv, typ, tags in draw_defs:
    add(name, mv, typ, tags, g_pips=1)

# -------- Removal --------
removal_defs = [
    ("Beast Within", 3, {"Instant"}, {"removal"}),
    ("Song of the Dryads", 3, {"Enchantment"}, {"removal"}),
    ("Archdruid's Charm", 3, {"Instant"}, {"removal","tutor_modal"}),
    ("Ezuri's Predation", 8, {"Sorcery"}, {"removal","mass_removal","finisher_adjacent"}),
    ("Haywire Mite", 1, {"Creature"}, {"removal","narrow"}),
]
for name, mv, typ, tags in removal_defs:
    add(name, mv, typ, tags, g_pips=1)

# -------- Protection --------
protection_defs = [
    ("Heroic Intervention", 2, {"Instant"}, {"protection"}),
    ("Lightning Greaves", 2, {"Artifact"}, {"protection","c_only"}),
    ("Obscuring Haze", 3, {"Instant"}, {"protection","fog","free_with_commander"}),
    ("Gigantic Big Bear", 7, {"Creature"}, {"protection_self","hexproof","bear"}),
    ("Allosaurus Shepherd", 1, {"Creature"}, {"protection_spells"}),
]
for name, mv, typ, tags in protection_defs:
    add(name, mv, typ, tags, g_pips=1)

# -------- Bear makers / tribal enablers --------
bear_defs = [
    ("Ayula, Queen Among Bears", 2, {"Creature"}, {"bear","bear_payoff","legendary"}),
    ("Ayula's Influence", 3, {"Enchantment"}, {"bear_maker"}),
    ("Beorn, Reluctant Host", 5, {"Creature"}, {"bear","legendary"}),
    ("Beorn's Hospitality", 2, {"Enchantment"}, {"landfall_counters","bear_late"}),
    ("Chameleon Colossus", 4, {"Creature"}, {"changeling","bear_type"}),
    ("Chronicle of Victory", 6, {"Artifact"}, {"anthem_tribal","draw_engine_conditional"}),
    ("Dancing from Dark to Dawn", 5, {"Enchantment"}, {"bear_maker","counters_engine","landfall"}),
    ("Little Bear", 3, {"Creature"}, {"bear","counters_engine","untap"}),
    ("Maskwood Nexus", 4, {"Artifact"}, {"changeling_global","token_maker"}),
    ("Roaming Throne", 4, {"Artifact"}, {"anthem_tribal","double_trigger"}),
    ("Springleaf Parade", 3, {"Enchantment"}, {"token_maker","changeling"}),
    ("Titania's Command", 6, {"Sorcery"}, {"bear_maker","counters_engine","land_ramp","graveyard_hate"}),
    ("Tribute to the World Tree", 4, {"Enchantment"}, {"counters_engine","draw_engine_conditional"}),
    ("Tireless Provisioner", 3, {"Creature"}, {"landfall","treasure"}),
]
for name, mv, typ, tags in bear_defs:
    add(name, mv, typ, tags, g_pips=1)

# -------- Counters engine (nao-bear-specific) --------
counters_defs = [
    ("Managorger Hydra", 3, {"Creature"}, {"counters_engine","trample"}),
    ("Forgotten Ancient", 4, {"Creature"}, {"counters_engine"}),
    ("Germination Practicum", 5, {"Sorcery"}, {"counters_engine","recast"}),
]
for name, mv, typ, tags in counters_defs:
    add(name, mv, typ, tags, g_pips=1)

# -------- Finishers / win conditions --------
finisher_defs = [
    ("Craterhoof Behemoth", 8, {"Creature"}, {"finisher","haste","team_pump"}),
    ("Unnatural Growth", 5, {"Enchantment"}, {"finisher","team_pump_repeatable"}),
    ("Genji Glove", 5, {"Artifact"}, {"finisher","extra_combat_equip"}),
    ("Ghalta, Primal Hunger", 12, {"Creature"}, {"finisher","cost_reduction_power"}),
    ("Goreclaw, Terror of Qal Sisma", 4, {"Creature"}, {"finisher_support","cost_reducer","legendary"}),
    ("Lumra, Bellow of the Woods", 6, {"Creature"}, {"finisher_support","land_ramp","legendary"}),
    ("Defiler of Vigor", 5, {"Creature"}, {"counters_engine","cost_reducer_life"}),
    ("Eternal Witness", 3, {"Creature"}, {"recursion"}),
    ("Ambush Viper", 2, {"Creature"}, {"removal_creature_only","flash"}),
    ("Natural Order", 4, {"Sorcery"}, {"tutor_cheat","finisher_setup"}),
]
for name, mv, typ, tags in finisher_defs:
    add(name, mv, typ, tags, g_pips=1)

# =========================================================
# PARSING
# =========================================================

def parse_decklist(text: str) -> List[str]:
    deck = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        qty, name = line.split(" ", 1)
        deck.extend([name.strip()] * int(qty))
    return deck

# =========================================================
# GAME STATE
# =========================================================

@dataclass
class GameState:
    rng: random.Random
    library: List[str]
    hand: List[str] = field(default_factory=list)
    battlefield: List[str] = field(default_factory=list)
    graveyard: List[str] = field(default_factory=list)

    turn: int = 0
    land_played: bool = False
    max_hand_size: int = 7

    commander_in_play: bool = False
    commander_cast_turn: Optional[int] = None

    spells_cast: int = 0
    extra_draws: int = 0
    lands_played_total: int = 0

    bear_count: int = 0
    beorn_bear_draws: int = 0          # vezes que o gatilho "3+ Bears -> draw 2" disparou
    beorn_combat_triggers: int = 0     # vezes que Beorn converteu uma criatura em Bear
    counters_on_board: int = 0         # soma aproximada de +1/+1 counters distribuidos

    finishers_resolved: List[str] = field(default_factory=list)
    finisher_turn: Optional[int] = None

    ramp_pieces_in_play: int = 0
    removal_cast: int = 0

    cards_discarded_to_hand_size: int = 0

    # Managorger Hydra: "Whenever a player casts a spell, put a +1/+1 counter on this creature."
    # Premissa explicita (pedida pelo usuario, nao e dado real): 2 spells de oponentes por turno em media,
    # e sobrevive em media 4 dos seus turnos antes de virar alvo de remocao pontual (e um corpo gigante e obvio).
    managorger_in_play: bool = False
    managorger_counters: int = 0
    managorger_last_turn_alive: Optional[int] = None
    managorger_death_turn: Optional[int] = None
    managorger_was_cast: bool = False

    # Roaming Throne: "If a triggered ability of another creature you control of
    # the chosen type triggers, it triggers an additional time." Premissa: tipo
    # escolhido sempre "Bear" (unica escolha sensata nesse deck). A propria Beorn
    # e do tipo Bear (Legendary Creature - Bear Shapeshifter Warrior), entao o
    # proprio gatilho de combate dela (converte criatura em Urso + checa 3+ Ursos)
    # dispara uma segunda vez completa quando o Roaming Throne esta em campo.
    # Regra permanente pra qualquer simulador com essa carta: ver
    # references/goldfish-sim-card-rules.md
    roaming_throne_doublings: int = 0

    # Germination Practicum: "Put two +1/+1 counters on each creature you control."
    # Paradigm: recast de graca do exilio no inicio de cada primeiro main phase seu, a partir do turno seguinte.
    germination_practicum_active: bool = False
    germination_practicum_cast_turn: Optional[int] = None

    # Genji Glove: {5} pra conjurar, Equip {3} separado. So da o combate extra
    # quando efetivamente equipada numa criatura que ataca - nao no momento do cast.
    genji_glove_in_play: bool = False
    genji_glove_equipped: bool = False
    genji_glove_equipped_turn: Optional[int] = None

    def draw(self, n=1, source="draw"):
        got = 0
        for _ in range(n):
            if self.library:
                self.hand.append(self.library.pop(0))
                got += 1
        if source != "normal":
            self.extra_draws += got

    def has(self, name: str) -> bool:
        return name in self.battlefield

    def roaming_throne_active(self) -> bool:
        return self.has("Roaming Throne")

    def cleanup_hand_size(self):
        if self.has("Reliquary Tower") or self.has("Thought Vessel"):
            return
        while len(self.hand) > self.max_hand_size:
            # descarta a carta de menor prioridade (maior CMC, heuristica simples)
            self.hand.sort(key=lambda c: -C(c).mv)
            self.hand.pop(0)
            self.cards_discarded_to_hand_size += 1

# =========================================================
# MANA MODEL (mono-verde: contagem total + contagem de fontes verdes)
# =========================================================

def total_mana(state: GameState) -> int:
    total = 0
    for card in state.battlefield:
        if is_land(card):
            total += 1
        elif card == "Sol Ring":
            total += 2
        elif has_tag(card, "ramp") and not is_land(card):
            total += 1
    return total

def green_sources(state: GameState) -> int:
    yavimaya = state.has("Yavimaya, Cradle of Growth")
    g = 0
    for card in state.battlefield:
        if is_land(card):
            if has_tag(card, "green_source") or yavimaya:
                g += 1
        elif has_tag(card, "green_source") or has_tag(card, "green_source_any"):
            g += 1
    return g

def can_cast(state: GameState, card: str) -> bool:
    if total_mana(state) < C(card).mv:
        return False
    pips = C(card).g_pips
    if pips >= 2:
        return green_sources(state) >= pips
    if pips == 1:
        return green_sources(state) >= 1
    return True

def commander_can_be_cast(state: GameState) -> bool:
    return can_cast(state, COMMANDER)

# =========================================================
# MULLIGAN
# =========================================================

KEEPERS = {"Sol Ring", "Llanowar Elves", "Birds of Paradise", "Thought Vessel", "Cultivate", "Three Visits", "Sakura-Tribe Elder"}

def should_keep(hand: List[str]) -> bool:
    lands = sum(1 for c in hand if is_land(c))
    keepers = sum(1 for c in hand if c in KEEPERS)
    if lands < 2 or lands > 5:
        return False
    if keepers >= 1:
        return True
    return lands >= 3

def bottom_priority(card: str) -> tuple:
    if is_land(card):
        return (3, 0)
    if card in KEEPERS:
        return (0, C(card).mv)
    if has_tag(card, "ramp") or has_tag(card, "draw_engine"):
        return (1, C(card).mv)
    if has_tag(card, "finisher"):
        return (4, -C(card).mv)
    return (2, C(card).mv)

def choose_bottom(hand: List[str], n: int) -> List[str]:
    ordered = sorted(hand, key=bottom_priority, reverse=True)
    return ordered[:n]

# =========================================================
# LAND PLAY
# =========================================================

LAND_PRIORITY = [
    "Forest", "Bala Ged Recovery // Bala Ged Sanctuary", "Yavimaya, Cradle of Growth",
    "Boseiju, Who Endures", "War Room", "Scavenger Grounds", "Nykthos, Shrine to Nyx", "Reliquary Tower",
]

def choose_land_to_play(state: GameState) -> Optional[str]:
    lands = [c for c in state.hand if is_land(c)]
    if not lands:
        return None
    g_in_play = green_sources(state)
    if g_in_play == 0:
        for name in ["Forest", "Bala Ged Recovery // Bala Ged Sanctuary", "Yavimaya, Cradle of Growth", "Boseiju, Who Endures"]:
            if name in lands:
                return name
    for p in LAND_PRIORITY:
        if p in lands:
            return p
    return lands[0]

def play_land(state: GameState, log: List[Dict]):
    card = choose_land_to_play(state)
    if card:
        state.hand.remove(card)
        state.battlefield.append(card)
        state.land_played = True
        state.lands_played_total += 1
        log.append({"action":"play_land","card":card})

# =========================================================
# CASTING PRIORITY
# =========================================================

def priority(state: GameState, card: str) -> tuple:
    if card == "Sol Ring":
        return (0, 0)
    if has_tag(card, "ramp") and C(card).mv <= 2:
        return (1, C(card).mv)
    if card == COMMANDER:
        return (2, 5)
    if has_tag(card, "ramp"):
        return (3, C(card).mv)
    if has_tag(card, "draw_engine"):
        return (4, C(card).mv)
    if has_tag(card, "bear_maker") or has_tag(card, "bear"):
        return (5, C(card).mv)
    if has_tag(card, "removal") and state.turn <= 4:
        return (5, C(card).mv)
    if has_tag(card, "finisher"):
        return (7, -C(card).mv)  # segura finishers pra depois, prioriza os mais baratos primeiro dentro do grupo
    return (6, C(card).mv)

def main_phase(state: GameState, log: List[Dict]):
    # Paradigm da Germination Practicum: a partir do turno SEGUINTE ao cast original,
    # recasta de graca do exilio no inicio de cada primeiro main phase seu.
    if state.germination_practicum_active and state.turn > state.germination_practicum_cast_turn:
        creatures_now = sum(1 for c in state.battlefield if is_creature(c))
        state.counters_on_board += 2 * creatures_now
        state.spells_cast += 1  # e uma copia sendo conjurada de verdade, conta pra Managorger etc.
        if state.managorger_in_play:
            state.managorger_counters += 1
        log.append({"trigger": "germination_practicum_paradigm", "turn": state.turn, "creatures_buffed": creatures_now})

    if not state.commander_in_play and state.turn >= 3:
        if commander_can_be_cast(state):
            state.commander_in_play = True
            state.commander_cast_turn = state.turn
            state.spells_cast += 1
            state.battlefield.append(COMMANDER)
            log.append({"action":"cast_commander","turn":state.turn})

    for _ in range(5):
        castables = [c for c in state.hand if is_spell(c) and can_cast(state, c)]
        if not castables:
            break
        castables.sort(key=lambda c: priority(state, c))
        choice = castables[0]
        cast_spell(state, choice, log)

        if not state.commander_in_play and state.turn >= 3 and commander_can_be_cast(state):
            state.commander_in_play = True
            state.commander_cast_turn = state.turn
            state.spells_cast += 1
            state.battlefield.append(COMMANDER)
            log.append({"action":"cast_commander","turn":state.turn})

    # Genji Glove: Equip {3} e um custo separado do cast ({5}). O motor nao rastreia mana
    # gasta ao longo do turno (mesma simplificacao que ja existia pra tudo mais), entao modelamos:
    # equipa no MESMO turno do cast se total_mana >= 8 (cobre cast+equip juntos sob o teto do modelo),
    # senao equipa automaticamente no turno seguinte (mana total ja cobre os 3 de equip sozinho).
    if state.genji_glove_in_play and not state.genji_glove_equipped and any(is_creature(c) for c in state.battlefield):
        cast_this_turn = state.turn == next((e.get("turn") for e in log if e.get("action")=="cast" and e.get("card")=="Genji Glove"), None)
        if (cast_this_turn and total_mana(state) >= 8) or (not cast_this_turn and total_mana(state) >= 3):
            state.genji_glove_equipped = True
            state.genji_glove_equipped_turn = state.turn
            log.append({"action": "genji_glove_equipped", "turn": state.turn})

def cast_spell(state: GameState, card: str, log: List[Dict]):
    # Managorger Hydra ja em campo: cresce com QUALQUER spell seu conjurado depois dela
    # (nao conta o proprio cast dela, que ainda nao esta em campo nesse momento).
    if state.managorger_in_play:
        state.managorger_counters += 1

    state.hand.remove(card)
    state.spells_cast += 1

    if "Instant" in C(card).types or "Sorcery" in C(card).types:
        if card != "Germination Practicum":  # ela e exilada, nao vai pro cemiterio
            state.graveyard.append(card)
    else:
        state.battlefield.append(card)

    if card == "Managorger Hydra":
        state.managorger_in_play = True
        state.managorger_was_cast = True
        # Premissa explicita: sobrevive em media 4 dos seus turnos (randint(1,7), media=4)
        # antes de cair pra remocao pontual - e um alvo grande e obvio na mesa.
        lifespan = state.rng.randint(1, 7)
        state.managorger_last_turn_alive = state.turn + lifespan - 1
        log.append({"action": "managorger_enters", "turn": state.turn, "assumed_lifespan_turns": lifespan})

    if card == "Germination Practicum":
        creatures_now = sum(1 for c in state.battlefield if is_creature(c))
        state.counters_on_board += 2 * creatures_now
        state.germination_practicum_active = True
        state.germination_practicum_cast_turn = state.turn
        log.append({"action": "germination_practicum_cast", "turn": state.turn, "creatures_buffed": creatures_now})

    if card == "Genji Glove":
        state.genji_glove_in_play = True

    if has_tag(card, "ramp"):
        state.ramp_pieces_in_play += 1

    if has_tag(card, "removal"):
        state.removal_cast += 1

    if has_tag(card, "bear") or has_tag(card, "bear_type") or has_tag(card, "changeling"):
        state.bear_count += 1

    if card in {"Cultivate", "Three Visits", "Sakura-Tribe Elder"}:
        target = next((c for c in state.library if is_land(c)), None)
        if target:
            state.library.remove(target)
            state.battlefield.append(target)
            log.append({"action":"land_ramp_proxy","card":card,"target":target})
        if card == "Cultivate":
            target2 = next((c for c in state.library if is_land(c)), None)
            if target2:
                state.library.remove(target2)
                state.hand.append(target2)
                log.append({"action":"land_ramp_proxy_to_hand","card":card,"target":target2})

    if card == "Solemn Simulacrum":
        target = next((c for c in state.library if is_land(c)), None)
        if target:
            state.library.remove(target)
            state.battlefield.append(target)

    if card == "The Great Henge" and state.bear_count > 0:
        state.draw(1, source="Great Henge ETB proxy")

    if card in {"Return of the Wildspeaker", "Shamanic Revelation"}:
        creatures = sum(1 for c in state.battlefield if is_creature(c))
        state.draw(max(1, creatures), source=card)

    if card == "Last March of the Ents":
        toughness_proxy = 6
        state.draw(toughness_proxy, source="Last March of the Ents")

    if card != "Genji Glove" and (has_tag(card, "finisher") or card in {"Craterhoof Behemoth", "Ghalta, Primal Hunger"}):
        # Genji Glove nao resolve no cast: precisa ser equipada (Equip {3}, custo separado) e
        # atacar de verdade pra valer como finisher - tratado em main_phase/combat_step.
        state.finishers_resolved.append(card)
        if state.finisher_turn is None and card in {"Craterhoof Behemoth", "Ghalta, Primal Hunger", "Unnatural Growth"}:
            state.finisher_turn = state.turn

    log.append({"action":"cast","card":card,"turn":state.turn})

# =========================================================
# COMBAT (gatilho do Beorn)
# =========================================================

def combat_step(state: GameState, log: List[Dict]):
    # Genji Glove: so entrega o combate extra quando equipada (Equip {3} pago) E existe
    # criatura pra atacar. Independente da Beorn estar em campo ou nao.
    if state.genji_glove_equipped and any(is_creature(c) for c in state.battlefield):
        if "Genji Glove" not in state.finishers_resolved:
            state.finishers_resolved.append("Genji Glove")
            if state.finisher_turn is None:
                state.finisher_turn = state.turn
        log.append({"trigger": "genji_glove_extra_combat", "turn": state.turn})

    if not state.commander_in_play:
        return

    # Beorn e do tipo Bear - Roaming Throne (tipo escolhido: Bear) dispara o
    # gatilho de combate dela uma segunda vez completa (converte outra criatura
    # em Urso, recheca 3+ Ursos de novo). Ver references/goldfish-sim-card-rules.md.
    times = 2 if state.roaming_throne_active() else 1
    if times == 2:
        state.roaming_throne_doublings += 1
    for _ in range(times):
        creatures_not_bear = [c for c in state.battlefield if is_creature(c) and not (has_tag(c,"bear") or has_tag(c,"bear_type") or has_tag(c,"changeling"))]
        if creatures_not_bear:
            target = max(creatures_not_bear, key=lambda c: C(c).mv)
            state.bear_count += 1
            state.beorn_combat_triggers += 1
            log.append({"trigger":"Beorn combat","made_bear":target})

        if state.bear_count >= 3:
            state.draw(2, source="Beorn 3+ Bears")
            state.beorn_bear_draws += 1
            log.append({"trigger":"Beorn draw2","bear_count":state.bear_count})

# =========================================================
# TURN STRUCTURE
# =========================================================

def play_turn(state: GameState, turn: int, game_log: List[List[Dict]]):
    state.turn = turn
    state.land_played = False

    log = [{"turn": turn, "phase": "start", "hand_size": len(state.hand),
            "battlefield_count": len(state.battlefield), "mana_est": total_mana(state)}]

    # Commander e sempre multiplayer (3+ jogadores) - a regra que pula a 1a compra de quem
    # comeca (CR 103.8a) so vale em jogos de 2 jogadores. Aqui sempre compra, mesmo no T1.
    state.draw(1, source="normal")

    play_land(state, log)
    main_phase(state, log)
    combat_step(state, log)
    state.cleanup_hand_size()

    if state.managorger_in_play:
        # Premissa explicita (nao e dado real): 2 spells de oponentes por turno em media,
        # representando a rodada dos outros jogadores ate o seu proximo turno.
        state.managorger_counters += 2
        if state.turn >= state.managorger_last_turn_alive:
            if "Managorger Hydra" in state.battlefield:
                state.battlefield.remove("Managorger Hydra")
            state.managorger_death_turn = state.turn
            log.append({"action": "managorger_removed", "turn": state.turn,
                        "final_counters": state.managorger_counters})
            state.managorger_in_play = False

    log.append({"turn": turn, "phase": "end", "hand_size": len(state.hand),
                "battlefield_count": len(state.battlefield), "bear_count": state.bear_count,
                "spells_cast": state.spells_cast, "beorn_bear_draws": state.beorn_bear_draws})
    game_log.append(log)

# =========================================================
# SIMULATION
# =========================================================

def simulate_one(seed: int, turns: int = 8) -> Dict:
    rng = random.Random(seed)
    deck = parse_decklist(DECKLIST_TEXT)
    assert len(deck) == 99, f"Mainboard deveria ser 99, deu {len(deck)}"

    rng.shuffle(deck)
    state = GameState(rng=rng, library=deck)

    mulligans = 0
    while True:
        state.hand = []
        state.draw(7, source="normal")
        if should_keep(state.hand) or mulligans >= 2:
            break
        mulligans += 1
        state.library.extend(state.hand)
        state.hand = []
        rng.shuffle(state.library)

    if mulligans:
        bottoms = choose_bottom(state.hand, mulligans)
        for c in bottoms:
            state.hand.remove(c)
            state.library.append(c)
        rng.shuffle(state.library)

    game_log = [[{"seed": seed, "mulligans": mulligans, "starting_hand": list(state.hand)}]]

    for t in range(1, turns + 1):
        play_turn(state, t, game_log)

    return {
        "seed": seed,
        "mulligans": mulligans,
        "commander_cast_turn": state.commander_cast_turn,
        "spells_cast": state.spells_cast,
        "extra_draws": state.extra_draws,
        "bear_count_final": state.bear_count,
        "beorn_bear_draws": state.beorn_bear_draws,
        "beorn_combat_triggers": state.beorn_combat_triggers,
        "ramp_pieces_in_play": state.ramp_pieces_in_play,
        "removal_cast": state.removal_cast,
        "finishers_resolved": len(state.finishers_resolved),
        "finisher_turn": state.finisher_turn,
        "cards_discarded_to_hand_size": state.cards_discarded_to_hand_size,
        "battlefield_count": len(state.battlefield),
        "hand_size": len(state.hand),
        "lands_played_total": state.lands_played_total,
        "managorger_was_cast": state.managorger_was_cast,
        "managorger_final_counters": state.managorger_counters if state.managorger_was_cast else None,
        "managorger_death_turn": state.managorger_death_turn,
        "counters_on_board_final": state.counters_on_board,
        "germination_practicum_cast": state.germination_practicum_active,
        "genji_glove_cast": state.genji_glove_in_play,
        "genji_glove_equipped": state.genji_glove_equipped,
        "genji_glove_equipped_turn": state.genji_glove_equipped_turn,
        "roaming_throne_in_play": state.has("Roaming Throne"),
        "roaming_throne_doublings": state.roaming_throne_doublings,
    }

def run_batch(n=500, turns=8, out_jsonl="beorn_v1_runs.jsonl", seed_base=91000):
    results = []
    with open(out_jsonl, "w", encoding="utf-8") as f:
        for i in range(n):
            res = simulate_one(seed=seed_base + i, turns=turns)
            results.append(res)
            f.write(json.dumps(res, ensure_ascii=False) + "\n")

    def avg(key):
        vals = [r[key] for r in results if r[key] is not None]
        return statistics.mean(vals) if vals else 0.0

    cmd_turns = [r["commander_cast_turn"] for r in results if r["commander_cast_turn"] is not None]
    fin_turns = [r["finisher_turn"] for r in results if r["finisher_turn"] is not None]

    print("=== Beorn the Fierce — Goldfish Summary v1 (simulado por Claude) ===")
    print(f"Games: {n} | Turns: {turns} | Multiplayer (compra sempre no T1, CR 103.8a)")
    print()
    print(f"Avg mulligans: {avg('mulligans'):.2f}")
    if cmd_turns:
        print(f"Avg commander cast turn: {statistics.mean(cmd_turns):.2f}")
        print(f"Commander cast by turn 4: {100*sum(1 for t in cmd_turns if t<=4)/n:.1f}%")
        print(f"Commander cast by turn 5: {100*sum(1 for t in cmd_turns if t<=5)/n:.1f}%")
    else:
        print("Commander nunca conjurado na amostra.")
    print()
    print(f"Avg spells cast: {avg('spells_cast'):.2f}")
    print(f"Avg extra draws (gatilhos): {avg('extra_draws'):.2f}")
    print(f"Avg Bear count final: {avg('bear_count_final'):.2f}")
    print(f"Avg Beorn 'draw 2' triggers (3+ Bears): {avg('beorn_bear_draws'):.2f}")
    print(f"Avg Beorn combat triggers (converteu em Bear): {avg('beorn_combat_triggers'):.2f}")
    print(f"Avg ramp pieces em campo: {avg('ramp_pieces_in_play'):.2f}")
    print(f"Avg remocao conjurada: {avg('removal_cast'):.2f}")
    print(f"Avg finishers resolvidos: {avg('finishers_resolved'):.2f}")
    if fin_turns:
        print(f"Avg turno do 1o finisher relevante: {statistics.mean(fin_turns):.2f}")
        print(f"% de jogos com finisher ate T8: {100*len(fin_turns)/n:.1f}%")
    print(f"Avg cartas descartadas por limite de mao: {avg('cards_discarded_to_hand_size'):.2f}")
    print(f"Avg battlefield final: {avg('battlefield_count'):.2f}")

    mg_cast = [r for r in results if r["managorger_was_cast"]]
    if mg_cast:
        mg_counters = [r["managorger_final_counters"] for r in mg_cast]
        mg_deaths = [r["managorger_death_turn"] for r in mg_cast if r["managorger_death_turn"] is not None]
        print()
        print(f"Managorger Hydra conjurada em {100*len(mg_cast)/n:.1f}% dos jogos")
        print(f"  Avg contadores +1/+1 finais (spells seus + 2/turno de oponentes assumido): {statistics.mean(mg_counters):.2f}")
        if mg_deaths:
            print(f"  Removida por remocao (premissa de ~4 turnos vivos) em {100*len(mg_deaths)/len(mg_cast):.1f}% dos jogos em que foi conjurada, turno medio: {statistics.mean(mg_deaths):.2f}")

    gp_cast = [r for r in results if r["germination_practicum_cast"]]
    print()
    print(f"Germination Practicum conjurada em {100*len(gp_cast)/n:.1f}% dos jogos")
    print(f"Avg contadores +1/+1 totais no board (Germination Practicum, soma de todos os recasts via Paradigm): {avg('counters_on_board_final'):.2f}")

    gg_cast = [r for r in results if r["genji_glove_cast"]]
    gg_equipped = [r for r in results if r["genji_glove_equipped"]]
    if gg_cast:
        print()
        print(f"Genji Glove conjurada em {100*len(gg_cast)/n:.1f}% dos jogos")
        print(f"  Equipada de fato (Equip {{3}} pago) em {100*len(gg_equipped)/len(gg_cast):.1f}% dos jogos em que foi conjurada")
        if gg_equipped:
            eq_turns = [r["genji_glove_equipped_turn"] for r in gg_equipped]
            print(f"  Avg turno em que equipou: {statistics.mean(eq_turns):.2f}")

    print(f"Avg mao final: {avg('hand_size'):.2f}")
    print(f"Avg terrenos jogados: {avg('lands_played_total'):.2f}")

    rt_games = [r for r in results if r["roaming_throne_in_play"]]
    if rt_games:
        print()
        print(f"Roaming Throne em campo em {100*len(rt_games)/n:.1f}% dos jogos (tipo escolhido: Bear)")
        print(f"  Avg gatilhos de combate da Beorn dobrados por partida: {statistics.mean([r['roaming_throne_doublings'] for r in rt_games]):.2f}")

    print()
    print(f"Logs salvos em: {out_jsonl}")

if __name__ == "__main__":
    run_batch(n=500, turns=8, out_jsonl="/tmp/beorn_v1_runs.jsonl")
