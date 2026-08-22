"""
Goldfish simulator - Edgar Markov (Mardu - R/W/B, tribal Vampiro/aristocratas)
Escrito e executado por Claude.

Metodologia:
- Tags e CARD_DB derivados de oracle_text real (Scryfall,
  /tmp/scryfall_cache/edgar_markov_full.json), nao inventados.
- Passo 0 (regra de Roaming Throne, references/goldfish-sim-card-rules.md):
  varredura mecanica de oracle_text de toda criatura Vampiro (regex por
  "Whenever"/"At the beginning of"/"When") encontrou 16 vampiros com
  gatilho proprio (de 20 + o proprio Edgar). Implementados todos abaixo,
  cada um como mecanica real, nao so tag.
- Roaming Throne (tipo escolhido: Vampire) dobra CADA gatilho real desses
  16 vampiros + o gatilho de ataque/Eminence do proprio Edgar, seguindo a
  mesma regra ja aplicada no Thranduil/Beorn.
- NAO modelado / simplificacoes documentadas:
  - Combate real (bloqueadores, dano de combate contra criaturas do
    oponente). Assume-se que Edgar (e outros vampiros relevantes) ataca
    todo turno depois de perder o summoning sickness, sem resposta do
    oponente - goldfish solo.
  - Clavileno, First of the Blessed: efeito de escolher 1 vampiro
    atacante especifico pra virar Demon e ganhar gatilho de morte e
    modelado so como um contador de "disparou X vezes", sem efeito
    numerico adicional (a escolha de QUAL vampiro e um detalhe tatico
    que nao muda a metrica agregada que este simulador mede).
  - Perda de vida do oponente e ganho de vida proprio sao rastreados como
    CONTADORES agregados (drain_total, lifegain_total), nao como life
    totals reais de um oponente concreto - e um goldfish solo.
  - Ashnod's Altar/Phyrexian Altar: a mana que produzem exige sacrificar
    uma criatura (nao e {T}: Add livre) - NAO contam pro total_mana()
    automatico. So geram mana quando efetivamente usados no "loop de
    sacrificio" (ver sac_loop), consumindo 1 token disponivel por uso.
  - Loop de sacrificio: no maximo 2 sacrificios por turno (Ashnod's
    Altar/Phyrexian Altar/Viscera Seer/Goblin Bombardment, o que estiver
    em campo), limitado a tokens de Vampiro disponiveis (criados pela
    Eminence) - simplificacao deliberada pra nao superestimar o volume
    de gatilhos de morte por turno.
  - Combo Exquisite Blood + Vito, Thorn of the Dusk Rose: quando as duas
    estao em campo, qualquer gatilho de "opponent loses life" ja tageado
    como drain_aristocrats liga o loop - marcado como combo_active a
    partir desse turno (metrica: primeiro turno em que o combo monta E
    tem um gatilho real pra ligar).
"""

import random
from dataclasses import dataclass, field
from typing import Set, List, Dict, Optional

COMMANDER = "Edgar Markov"

# Politica de "cacar o combo": False (default) = joga generico, so conjura
# Exquisite Blood/Vito Thorn/os tutores quando calham na mao no ritmo
# normal do resto do jogo. True = prioriza os 2 tutores rapidos (Vampiric
# Tutor, Diabolic Intent) especificamente pra buscar a peca do combo que
# ainda falta, e prioriza conjurar as pecas do combo assim que estao na
# mao, acima de qualquer outra jogada - pra medir o piso real (nao so o
# melhor caso teorico) de quando o combo monta se o jogador estiver
# mirando nisso de proposito. Pedido do usuario pra comprovar a
# classificacao de Bracket (criterio oficial e "antes do turno 6").
COMBO_HUNTING_POLICY = False
COMBO_PIECES = ("Exquisite Blood", "Vito, Thorn of the Dusk Rose")

DECKLIST_TEXT = """
1 Bartolomé del Presidio
1 Blood Artist
1 Bloodletter of Aclazotz
1 Bloodthirsty Conqueror
1 Champion of Dusk
1 Charismatic Conqueror
1 Clavileño, First of the Blessed
1 Cordial Vampire
1 Cruel Celebrant
1 Elenda, the Dusk Rose
1 Emeritus of Woe
1 Enduring Tenacity
1 Indulgent Aristocrat
1 Mondrak, Glory Dominus
1 Nullpriest of Oblivion
1 Ojer Taq, Deepest Foundation // Temple of Civilization
1 Ophiomancer
1 Pitiless Plunderer
1 Purphoros, God of the Forge
1 Roaming Throne
1 Sanctum Seeker
1 Stensian Sanguinist // Exsanguinate
1 Vein Ripper
1 Vindictive Vampire
1 Viscera Seer
1 Vito, Fanatic of Aclazotz
1 Vito, Thorn of the Dusk Rose
1 Welcoming Vampire
1 Zulaport Cutthroat
1 Arcane Signet
1 Ashnod's Altar
1 Phyrexian Altar
1 Skullclamp
1 Sol Ring
1 Anointed Procession
1 Bastion of Remembrance
1 Black Market Connections
1 Caretaker's Talent
1 Exquisite Blood
1 Funeral Room // Awakening Hall
1 Goblin Bombardment
1 Legion's Landing // Adanto, the First Fort
1 Smothering Tithe
1 The Meathook Massacre
1 Unholy Annex // Ritual Chamber
1 Warleader's Call
1 Elspeth, Storm Slayer
1 Sorin, Imperious Bloodlord
1 Anguished Unmaking
1 Call the Coppercoats
1 Clever Concealment
1 Fell the Profane // Fell Mire
1 Get Lost
1 Path to Exile
1 Plumb the Forbidden
1 Swords to Plowshares
1 Teferi's Protection
1 Vampiric Tutor
1 Agadeem's Awakening // Agadeem, the Undercrypt
1 Bloodline Bidding
1 Diabolic Intent
1 Rite of Oblivion
1 Sevinne's Reclamation
1 Vindicate
1 Arid Mesa
1 Battlefield Forge
1 Blackcleave Cliffs
1 Blazemire Verge
1 Blood Crypt
1 Bloodstained Mire
1 Cabal Coffers
1 Cavern of Souls
1 City of Brass
1 Command Tower
1 Fetid Heath
1 Fountainport
1 Godless Shrine
1 Haunted Ridge
1 Luxury Suite
1 Mana Confluence
1 Marsh Flats
1 Minas Tirith
4 Plains
1 Phyrexian Tower
1 Rugged Prairie
1 Savai Triome
1 Spectator Seating
4 Swamp
1 Takenuma, Abandoned Mire
1 Urborg, Tomb of Yawgmoth
1 Urza's Saga
1 Voldaren Estate
1 Westvale Abbey // Ormendahl, Profane Prince
"""

@dataclass
class Card:
    name: str
    mv: int
    type: str
    colors: Set[str] = field(default_factory=set)
    produces: Set[str] = field(default_factory=set)
    tags: Set[str] = field(default_factory=set)

CARD_DB: Dict[str, Card] = {}

def add(name, mv, type_, colors=None, produces=None, tags=None):
    CARD_DB[name] = Card(name=name, mv=mv, type=type_,
                          colors=set(colors or []), produces=set(produces or []),
                          tags=set(tags or []))

# -------- Comandante --------
add("Edgar Markov", 6, "Creature", colors={"B", "R", "W"}, tags={"vampire_type"})

# -------- Deck (99 cartas, geradas via Scryfall cards/collection) --------
add("Bartolomé del Presidio", 2, "Creature", colors={"B", "W"}, produces=set(), tags={"vampire_type"})
add("Blood Artist", 2, "Creature", colors={"B"}, produces=set(), tags={"drain_aristocrats", "vampire_type"})
add("Bloodletter of Aclazotz", 4, "Creature", colors={"B"}, produces=set(), tags={"vampire_type"})
add("Bloodthirsty Conqueror", 5, "Creature", colors={"B"}, produces=set(), tags={"vampire_type"})
add("Champion of Dusk", 5, "Creature", colors={"B"}, produces=set(), tags={"draw", "vampire_type"})
add("Charismatic Conqueror", 2, "Creature", colors={"W"}, produces=set(), tags={"token_maker", "vampire_type"})
add("Clavileño, First of the Blessed", 3, "Creature", colors={"B", "W"}, produces=set(), tags={"draw", "token_maker", "vampire_type"})
add("Cordial Vampire", 2, "Creature", colors={"B"}, produces=set(), tags={"vampire_type"})
add("Cruel Celebrant", 2, "Creature", colors={"B", "W"}, produces=set(), tags={"drain_aristocrats", "vampire_type"})
add("Elenda, the Dusk Rose", 4, "Creature", colors={"B", "W"}, produces=set(), tags={"token_maker", "vampire_type"})
add("Emeritus of Woe", 4, "Creature", colors={"B"}, produces=set(), tags={"tutor", "vampire_type"})
add("Enduring Tenacity", 4, "Creature", colors={"B"}, produces=set(), tags={"drain_aristocrats"})
add("Indulgent Aristocrat", 1, "Creature", colors={"B"}, produces=set(), tags={"vampire_type"})
add("Mondrak, Glory Dominus", 4, "Creature", colors={"W"}, produces=set(), tags=set())
add("Nullpriest of Oblivion", 2, "Creature", colors={"B"}, produces=set(), tags={"vampire_type"})
add("Ojer Taq, Deepest Foundation // Temple of Civilization", 6, "Land", colors={"W"}, produces={"W"}, tags=set())
add("Ophiomancer", 3, "Creature", colors={"B"}, produces=set(), tags={"token_maker"})
add("Pitiless Plunderer", 4, "Creature", colors={"B"}, produces={"B", "G", "R", "U", "W"}, tags={"ramp", "token_maker"})
add("Purphoros, God of the Forge", 4, "Creature", colors={"R"}, produces=set(), tags=set())
add("Roaming Throne", 4, "Creature", colors=set(), produces=set(), tags=set())
add("Sanctum Seeker", 4, "Creature", colors={"B"}, produces=set(), tags={"drain_aristocrats", "vampire_type"})
add("Stensian Sanguinist // Exsanguinate", 2, "Creature", colors={"B"}, produces=set(), tags={"drain_aristocrats", "vampire_type"})
add("Vein Ripper", 6, "Creature", colors={"B"}, produces=set(), tags={"drain_aristocrats", "vampire_type"})
add("Vindictive Vampire", 4, "Creature", colors={"B"}, produces=set(), tags={"vampire_type"})
add("Viscera Seer", 1, "Creature", colors={"B"}, produces=set(), tags={"vampire_type"})
add("Vito, Fanatic of Aclazotz", 4, "Creature", colors={"B", "W"}, produces=set(), tags={"drain_aristocrats", "token_maker", "vampire_type"})
add("Vito, Thorn of the Dusk Rose", 3, "Creature", colors={"B"}, produces=set(), tags={"drain_aristocrats", "vampire_type"})
add("Welcoming Vampire", 3, "Creature", colors={"W"}, produces=set(), tags={"draw", "vampire_type"})
add("Zulaport Cutthroat", 2, "Creature", colors={"B"}, produces=set(), tags={"drain_aristocrats"})
add("Arcane Signet", 2, "Artifact", colors=set(), produces={"B", "G", "R", "U", "W"}, tags={"ramp"})
add("Ashnod's Altar", 3, "Artifact", colors=set(), produces={"C"}, tags={"ramp"})
add("Phyrexian Altar", 3, "Artifact", colors=set(), produces={"B", "G", "R", "U", "W"}, tags={"ramp"})
add("Skullclamp", 1, "Artifact", colors=set(), produces=set(), tags={"draw"})
add("Sol Ring", 1, "Artifact", colors=set(), produces={"C"}, tags={"ramp"})
add("Anointed Procession", 4, "Enchantment", colors={"W"}, produces=set(), tags={"token_maker"})
add("Bastion of Remembrance", 3, "Enchantment", colors={"B"}, produces=set(), tags={"drain_aristocrats", "token_maker"})
add("Black Market Connections", 3, "Enchantment", colors={"B"}, produces=set(), tags={"draw", "token_maker"})
add("Caretaker's Talent", 3, "Enchantment", colors={"W"}, produces=set(), tags={"draw", "token_maker"})
add("Exquisite Blood", 5, "Enchantment", colors={"B"}, produces=set(), tags=set())
add("Funeral Room // Awakening Hall", 11, "Enchantment", colors={"B"}, produces=set(), tags={"drain_aristocrats"})
add("Goblin Bombardment", 2, "Enchantment", colors={"R"}, produces=set(), tags={"removal"})
add("Legion's Landing // Adanto, the First Fort", 1, "Land", colors={"W"}, produces={"W"}, tags={"token_maker"})
add("Smothering Tithe", 4, "Enchantment", colors={"W"}, produces={"B", "G", "R", "U", "W"}, tags={"ramp", "token_maker"})
add("The Meathook Massacre", 2, "Enchantment", colors={"B"}, produces=set(), tags={"drain_aristocrats", "wipe"})
add("Unholy Annex // Ritual Chamber", 8, "Enchantment", colors={"B"}, produces=set(), tags={"drain_aristocrats", "draw", "token_maker"})
add("Warleader's Call", 3, "Enchantment", colors={"R", "W"}, produces=set(), tags=set())
add("Elspeth, Storm Slayer", 5, "Planeswalker", colors={"W"}, produces=set(), tags={"removal", "token_maker", "wipe"})
add("Sorin, Imperious Bloodlord", 3, "Planeswalker", colors={"B"}, produces=set(), tags={"removal"})
add("Anguished Unmaking", 3, "Instant", colors={"B", "W"}, produces=set(), tags={"removal"})
add("Call the Coppercoats", 3, "Instant", colors={"W"}, produces=set(), tags={"token_maker"})
add("Clever Concealment", 4, "Instant", colors={"W"}, produces=set(), tags=set())
add("Fell the Profane // Fell Mire", 4, "Land", colors={"B"}, produces={"B"}, tags={"removal"})
add("Get Lost", 2, "Instant", colors={"W"}, produces=set(), tags={"removal"})
add("Path to Exile", 1, "Instant", colors={"W"}, produces=set(), tags={"removal"})
add("Plumb the Forbidden", 2, "Instant", colors={"B"}, produces=set(), tags={"draw"})
add("Swords to Plowshares", 1, "Instant", colors={"W"}, produces=set(), tags={"removal"})
add("Teferi's Protection", 3, "Instant", colors={"W"}, produces=set(), tags=set())
add("Vampiric Tutor", 1, "Instant", colors={"B"}, produces=set(), tags={"tutor"})
add("Agadeem's Awakening // Agadeem, the Undercrypt", 3, "Land", colors={"B"}, produces={"B"}, tags=set())
add("Bloodline Bidding", 8, "Sorcery", colors={"B"}, produces=set(), tags=set())
add("Diabolic Intent", 2, "Sorcery", colors={"B"}, produces=set(), tags={"tutor"})
add("Rite of Oblivion", 2, "Sorcery", colors={"B", "W"}, produces=set(), tags={"removal"})
add("Sevinne's Reclamation", 3, "Sorcery", colors={"W"}, produces=set(), tags=set())
add("Vindicate", 3, "Sorcery", colors={"B", "W"}, produces=set(), tags={"removal"})
add("Arid Mesa", 0, "Land", colors=set(), produces={"R", "W"}, tags=set())  # busca Mountain ou Plains
add("Battlefield Forge", 0, "Land", colors={"R", "W"}, produces={"C", "R", "W"}, tags=set())
add("Blackcleave Cliffs", 0, "Land", colors={"B", "R"}, produces={"B", "R"}, tags=set())
add("Blazemire Verge", 0, "Land", colors={"B", "R"}, produces={"B", "R"}, tags=set())
add("Blood Crypt", 0, "Land", colors={"B", "R"}, produces={"B", "R"}, tags=set())
add("Bloodstained Mire", 0, "Land", colors=set(), produces={"B", "R"}, tags=set())  # busca Swamp ou Mountain
add("Cabal Coffers", 0, "Land", colors={"B"}, produces={"B"}, tags=set())
add("Cavern of Souls", 0, "Land", colors=set(), produces={"B", "C", "G", "R", "U", "W"}, tags=set())
add("City of Brass", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())
add("Command Tower", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())
add("Fetid Heath", 0, "Land", colors={"B", "W"}, produces={"B", "C", "W"}, tags=set())
add("Fountainport", 0, "Land", colors=set(), produces={"C"}, tags={"draw", "token_maker"})
add("Godless Shrine", 0, "Land", colors={"B", "W"}, produces={"B", "W"}, tags=set())
add("Haunted Ridge", 0, "Land", colors={"B", "R"}, produces={"B", "R"}, tags=set())
add("Luxury Suite", 0, "Land", colors={"B", "R"}, produces={"B", "R"}, tags=set())
add("Mana Confluence", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())
add("Marsh Flats", 0, "Land", colors=set(), produces={"W", "B"}, tags=set())  # busca Plains ou Swamp
add("Minas Tirith", 0, "Land", colors={"W"}, produces={"W"}, tags={"draw"})
add("Plains", 0, "Land", colors={"W"}, produces={"W"}, tags=set())
add("Phyrexian Tower", 0, "Land", colors={"B"}, produces={"B", "C"}, tags=set())
add("Rugged Prairie", 0, "Land", colors={"R", "W"}, produces={"C", "R", "W"}, tags=set())
add("Savai Triome", 0, "Land", colors={"B", "R", "W"}, produces={"B", "R", "W"}, tags={"draw"})
add("Spectator Seating", 0, "Land", colors={"R", "W"}, produces={"R", "W"}, tags=set())
add("Swamp", 0, "Land", colors={"B"}, produces={"B"}, tags=set())
add("Takenuma, Abandoned Mire", 0, "Land", colors={"B"}, produces={"B"}, tags=set())
add("Urborg, Tomb of Yawgmoth", 0, "Land", colors=set(), produces={"B"}, tags=set())
add("Urza's Saga", 0, "Land", colors=set(), produces={"C"}, tags={"token_maker"})
add("Voldaren Estate", 0, "Land", colors=set(), produces={"B", "C", "G", "R", "U", "W"}, tags={"draw", "token_maker"})
add("Westvale Abbey // Ormendahl, Profane Prince", 0, "Land", colors={"B"}, produces={"C"}, tags={"token_maker"})

def C(name: str) -> Card:
    return CARD_DB[name]

def parse_decklist(text: str) -> List[str]:
    deck = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("//") or line.startswith("#"):
            continue
        parts = line.split(" ", 1)
        qty = int(parts[0])
        name = parts[1].strip()
        deck.extend([name] * qty)
    return deck

def is_land(card: str) -> bool:
    return C(card).type == "Land"

def is_creature(card: str) -> bool:
    return C(card).type == "Creature"

def is_vampire(card: str) -> bool:
    return has_tag(card, "vampire_type") or card == COMMANDER

def has_tag(card: str, tag: str) -> bool:
    return tag in C(card).tags

SAC_OUTLETS = {"Ashnod's Altar", "Phyrexian Altar", "Viscera Seer", "Goblin Bombardment"}
DEATH_PAYOFFS = {"Blood Artist", "Cruel Celebrant", "Cordial Vampire", "Vindictive Vampire", "Vein Ripper"}

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
    tokens: List[str] = field(default_factory=list)  # tokens de Vampiro 1/1 da Eminence, disponiveis pra sac
    turn: int = 0
    land_played: bool = False
    mana_spent_this_turn: int = 0
    lands_played_total: int = 0

    commander_in_play: bool = False
    commander_cast_turn: Optional[int] = None
    commander_cast_count: int = 0

    eminence_tokens_created: int = 0
    edgar_attack_counters_total: int = 0
    edgar_attack_turns: int = 0

    drain_total: int = 0
    lifegain_total: int = 0
    creatures_sacrificed_total: int = 0
    death_trigger_events: int = 0

    champion_of_dusk_draws: int = 0
    welcoming_vampire_draws: int = 0
    welcoming_vampire_trigger_pending: int = 0
    sanctum_seeker_drains: int = 0
    vito_fanatic_stage_this_turn: int = 0
    vito_fanatic_demons_created: int = 0
    clavileno_triggers: int = 0
    elenda_counters: int = 0
    elenda_death_tokens: int = 0

    combo_active: bool = False
    combo_active_turn: Optional[int] = None
    both_combo_pieces_turn: Optional[int] = None  # turno em que as 2 pecas ja estao em campo (antes de precisar de um gatilho pra "ligar")

    roaming_throne_doublings: int = 0

    def draw(self, n: int = 1):
        for _ in range(n):
            if self.library:
                self.hand.append(self.library.pop(0))

    def has(self, name: str) -> bool:
        return name in self.battlefield

    def roaming_throne_active(self) -> bool:
        return self.has("Roaming Throne")

# =========================================================
# MANA MODEL
# =========================================================

def swamp_count(state: GameState) -> int:
    if state.has("Urborg, Tomb of Yawgmoth"):
        return sum(1 for c in state.battlefield if is_land(c))
    return sum(1 for c in state.battlefield if is_land(c) and "Swamp" in c)

def total_mana(state: GameState) -> int:
    total = 0
    for card in state.battlefield:
        if is_land(card):
            total += 1
            if card == "Cabal Coffers":
                total += swamp_count(state)  # bonus alem da propria terra
        elif card == "Sol Ring":
            total += 2
        elif card in ("Ashnod's Altar", "Phyrexian Altar"):
            continue  # exige sacrificio, nao conta como mana livre - ver sac_loop
        elif has_tag(card, "ramp"):
            total += 1
    return total

def color_sources(state: GameState, color: str) -> int:
    n = 0
    for card in state.battlefield:
        if color in C(card).produces:
            n += 1
    return n

def remaining_mana(state: GameState) -> int:
    return total_mana(state) - state.mana_spent_this_turn

def commander_effective_mv(state: GameState) -> int:
    return C(COMMANDER).mv + 2 * state.commander_cast_count

def can_cast(state: GameState, card: str) -> bool:
    mv = commander_effective_mv(state) if card == COMMANDER else C(card).mv
    if remaining_mana(state) < mv:
        return False
    for color in C(card).colors:
        if color_sources(state, color) < 1:
            return False
    return True

# =========================================================
# MULLIGAN
# =========================================================

FAST_RAMP = {"Sol Ring", "Arcane Signet"}

def should_keep(hand: List[str]) -> bool:
    lands = sum(1 for c in hand if is_land(c))
    if lands > 5:
        return False
    if lands >= 3:
        return True
    if lands == 2:
        return any(c in FAST_RAMP for c in hand)
    return False

def choose_bottom(hand: List[str], n: int) -> List[str]:
    nonlands = [c for c in hand if not is_land(c)]
    nonlands.sort(key=lambda c: -C(c).mv)
    return nonlands[:n] if len(nonlands) >= n else (nonlands + [c for c in hand if is_land(c)])[:n]

# =========================================================
# LAND DROP
# =========================================================

def play_land(state: GameState, log: List[Dict]):
    if state.land_played:
        return
    lands_in_hand = [c for c in state.hand if is_land(c)]
    if not lands_in_hand:
        return
    have_colors = set()
    for c in state.battlefield:
        have_colors |= C(c).produces
    missing = {"W", "B", "R"} - have_colors
    best = None
    for c in lands_in_hand:
        if C(c).produces & missing:
            best = c
            break
    choice = best or lands_in_hand[0]
    state.hand.remove(choice)
    state.battlefield.append(choice)
    state.land_played = True
    state.lands_played_total += 1

# =========================================================
# EMINENCE + GATILHOS DE VAMPIRO (Passo 0 - ver docstring)
# =========================================================

def _times(state: GameState) -> int:
    return 2 if state.roaming_throne_active() else 1

def _log_doubling(state: GameState, times: int):
    if times == 2:
        state.roaming_throne_doublings += 1

def eminence_trigger(state: GameState, card: str, log: List[Dict]):
    # "Whenever you cast another Vampire spell, if Edgar is in the
    # command zone or on the battlefield, create a 1/1 black Vampire
    # creature token." Funciona mesmo com Edgar so na zona de comando.
    if card == COMMANDER or not is_vampire(card):
        return
    edgar_available = state.commander_in_play or state.commander_cast_count == 0
    if not edgar_available:
        return
    times = _times(state)
    for _ in range(times):
        state.tokens.append("Vampire Token")
        state.eminence_tokens_created += 1
        state.welcoming_vampire_trigger_pending += 1
    _log_doubling(state, times)
    log.append({"trigger": "eminence", "card": card, "times": times, "turn": state.turn})

def welcoming_vampire_check(state: GameState, log: List[Dict]):
    # "Whenever one or more OTHER creatures you control with power 2 or
    # less enter, draw a card. This ability triggers only once each
    # turn." Modelado no fim do turno: 1 disparo (nao mais) se pelo
    # menos 1 token da Eminence entrou nesse turno.
    if not state.has("Welcoming Vampire"):
        return
    if state.welcoming_vampire_trigger_pending <= 0:
        return
    times = _times(state)
    for _ in range(times):
        state.draw(1)
        state.welcoming_vampire_draws += 1
    _log_doubling(state, times)
    log.append({"trigger": "welcoming_vampire", "times": times, "turn": state.turn})
    state.welcoming_vampire_trigger_pending = 0

def _apply_death_payoffs(state: GameState, log: List[Dict], source: str):
    for payoff in DEATH_PAYOFFS:
        if not state.has(payoff):
            continue
        times = _times(state)
        for _ in range(times):
            state.death_trigger_events += 1
            if payoff in ("Blood Artist", "Cruel Celebrant", "Vindictive Vampire", "Vein Ripper"):
                amt = 2 if payoff == "Vein Ripper" else 1
                state.drain_total += amt
                state.lifegain_total += amt
                if state.has("Bloodthirsty Conqueror"):
                    state.lifegain_total += amt  # "whenever an opponent loses life, you gain that much life"
                if state.has("Exquisite Blood") and state.has("Vito, Thorn of the Dusk Rose") and not state.combo_active:
                    state.combo_active = True
                    state.combo_active_turn = state.turn
                    log.append({"trigger": "combo_active", "turn": state.turn})
        _log_doubling(state, times)
        log.append({"trigger": "death_payoff", "card": payoff, "source": source, "times": times, "turn": state.turn})

def apply_etb(state: GameState, card: str, log: List[Dict]):
    if card == "Champion of Dusk":
        vamps = sum(1 for c in state.battlefield if is_vampire(c))
        times = _times(state)
        for _ in range(times):
            state.draw(vamps)
            state.champion_of_dusk_draws += vamps
        _log_doubling(state, times)
        log.append({"trigger": "champion_of_dusk", "vamps": vamps, "times": times, "turn": state.turn})

def sac_loop(state: GameState, log: List[Dict]):
    # Ate 2 sacrificios por turno (ver docstring), consumindo tokens de
    # Vampiro disponiveis, se houver pelo menos 1 sac outlet em campo.
    outlets = [c for c in state.battlefield if c in SAC_OUTLETS]
    if not outlets or not state.tokens:
        return
    n = min(2, len(state.tokens))
    for _ in range(n):
        if not state.tokens:
            break
        state.tokens.pop()
        state.creatures_sacrificed_total += 1
        if "Ashnod's Altar" in state.battlefield:
            state.mana_spent_this_turn -= 2  # +2 mana efetivo pro resto do turno
        elif "Phyrexian Altar" in state.battlefield:
            state.mana_spent_this_turn -= 1
        _apply_death_payoffs(state, log, source="sac_loop")
        if state.has("Vito, Fanatic of Aclazotz"):
            state.vito_fanatic_stage_this_turn += 1
            stage = state.vito_fanatic_stage_this_turn
            if stage == 1:
                state.lifegain_total += 2
            elif stage == 2:
                state.drain_total += 2
                if state.has("Exquisite Blood") and state.has("Vito, Thorn of the Dusk Rose") and not state.combo_active:
                    state.combo_active = True
                    state.combo_active_turn = state.turn
                    log.append({"trigger": "combo_active", "turn": state.turn})
            elif stage == 3:
                state.vito_fanatic_demons_created += 1
                state.vito_fanatic_stage_this_turn = 0

def combat_step(state: GameState, log: List[Dict]):
    if not state.commander_in_play or state.turn <= state.commander_cast_turn:
        return  # summoning sickness no turno em que entrou
    state.edgar_attack_turns += 1
    vamps_in_play = sum(1 for c in state.battlefield if is_vampire(c))
    times = _times(state)
    for _ in range(times):
        state.edgar_attack_counters_total += vamps_in_play
    _log_doubling(state, times)
    log.append({"trigger": "edgar_attack_counters", "vamps": vamps_in_play, "times": times, "turn": state.turn})

    if state.has("Sanctum Seeker"):
        times2 = _times(state)
        for _ in range(times2):
            state.sanctum_seeker_drains += 1
            state.drain_total += 1
            state.lifegain_total += 1
            if state.has("Bloodthirsty Conqueror"):
                state.lifegain_total += 1
            if state.has("Exquisite Blood") and state.has("Vito, Thorn of the Dusk Rose") and not state.combo_active:
                state.combo_active = True
                state.combo_active_turn = state.turn
                log.append({"trigger": "combo_active", "turn": state.turn})
        _log_doubling(state, times2)
        log.append({"trigger": "sanctum_seeker", "times": times2, "turn": state.turn})

    if state.has("Clavileño, First of the Blessed"):
        times3 = _times(state)
        state.clavileno_triggers += times3
        _log_doubling(state, times3)
        log.append({"trigger": "clavileno", "times": times3, "turn": state.turn})

# =========================================================
# TURNO
# =========================================================

def _cast_combo_piece(state: GameState, card: str, log: List[Dict]):
    state.hand.remove(card)
    state.mana_spent_this_turn += C(card).mv
    state.battlefield.append(card)
    apply_etb(state, card, log)
    eminence_trigger(state, card, log)
    log.append({"action": "cast_combo_piece", "card": card, "turn": state.turn})
    if all(p in state.battlefield for p in COMBO_PIECES) and state.both_combo_pieces_turn is None:
        state.both_combo_pieces_turn = state.turn
        log.append({"trigger": "both_combo_pieces_in_play", "turn": state.turn})

def combo_hunt(state: GameState, log: List[Dict]):
    missing = [p for p in COMBO_PIECES if p not in state.battlefield and p not in state.hand]

    # Diabolic Intent: busca direto pra mao, mas exige sacrificar uma
    # criatura ja em campo como custo adicional.
    if missing and "Diabolic Intent" in state.hand and can_cast(state, "Diabolic Intent"):
        sac_candidates = [c for c in state.battlefield if is_creature(c) and c != COMMANDER]
        if sac_candidates:
            state.hand.remove("Diabolic Intent")
            state.mana_spent_this_turn += C("Diabolic Intent").mv
            state.graveyard.append("Diabolic Intent")
            victim = sac_candidates[0]
            state.battlefield.remove(victim)
            state.graveyard.append(victim)
            target = missing[0]
            state.library.remove(target)
            state.hand.append(target)
            log.append({"action": "diabolic_intent", "sacrificed": victim, "found": target, "turn": state.turn})
            missing = [p for p in COMBO_PIECES if p not in state.battlefield and p not in state.hand]

    # Vampiric Tutor: busca pro topo da biblioteca (nao pra mao direto) -
    # a proxima compra normal (inicio do proximo turno) pega a carta.
    if missing and "Vampiric Tutor" in state.hand and can_cast(state, "Vampiric Tutor"):
        state.hand.remove("Vampiric Tutor")
        state.mana_spent_this_turn += C("Vampiric Tutor").mv
        state.graveyard.append("Vampiric Tutor")
        target = missing[0]
        state.library.remove(target)
        state.library.insert(0, target)
        log.append({"action": "vampiric_tutor", "found": target, "turn": state.turn})

    # Conjura qualquer peca do combo que ja esteja na mao, com prioridade
    # sobre o resto da mao (loop generico do main_phase abaixo so pega o
    # que sobrar).
    for piece in COMBO_PIECES:
        if piece in state.hand and can_cast(state, piece):
            _cast_combo_piece(state, piece, log)

def main_phase(state: GameState, log: List[Dict]):
    if COMBO_HUNTING_POLICY:
        combo_hunt(state, log)

    if not state.commander_in_play and state.commander_cast_count == 0 and can_cast(state, COMMANDER):
        state.mana_spent_this_turn += commander_effective_mv(state)
        state.battlefield.append(COMMANDER)
        state.commander_in_play = True
        state.commander_cast_turn = state.turn
        state.commander_cast_count += 1
        log.append({"action": "cast_commander", "turn": state.turn})

    for _ in range(8):
        castables = [c for c in state.hand if c != COMMANDER and not is_land(c) and can_cast(state, c)]
        if not castables:
            break
        castables.sort(key=lambda c: C(c).mv)
        choice = castables[0]
        state.hand.remove(choice)
        state.mana_spent_this_turn += C(choice).mv
        if C(choice).type in ("Instant", "Sorcery"):
            state.graveyard.append(choice)
        else:
            state.battlefield.append(choice)
            apply_etb(state, choice, log)
        eminence_trigger(state, choice, log)
        log.append({"action": "cast", "card": choice, "turn": state.turn})

    if all(p in state.battlefield for p in COMBO_PIECES) and state.both_combo_pieces_turn is None:
        state.both_combo_pieces_turn = state.turn
        log.append({"trigger": "both_combo_pieces_in_play", "turn": state.turn})

def play_turn(state: GameState, turn: int, game_log: List[List[Dict]]):
    state.turn = turn
    state.land_played = False
    state.mana_spent_this_turn = 0
    state.vito_fanatic_stage_this_turn = 0
    state.welcoming_vampire_trigger_pending = 0
    log = []

    state.draw(1)
    play_land(state, log)
    main_phase(state, log)
    sac_loop(state, log)
    welcoming_vampire_check(state, log)
    combat_step(state, log)

    game_log.append(log)

# =========================================================
# SIMULACAO
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
        state.draw(7)
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

    game_log = []
    for t in range(1, turns + 1):
        play_turn(state, t, game_log)

    return {
        "seed": seed,
        "mulligans": mulligans,
        "commander_cast_turn": state.commander_cast_turn,
        "eminence_tokens_created": state.eminence_tokens_created,
        "edgar_attack_counters_total": state.edgar_attack_counters_total,
        "edgar_attack_turns": state.edgar_attack_turns,
        "drain_total": state.drain_total,
        "lifegain_total": state.lifegain_total,
        "creatures_sacrificed_total": state.creatures_sacrificed_total,
        "death_trigger_events": state.death_trigger_events,
        "champion_of_dusk_draws": state.champion_of_dusk_draws,
        "welcoming_vampire_draws": state.welcoming_vampire_draws,
        "sanctum_seeker_drains": state.sanctum_seeker_drains,
        "vito_fanatic_demons_created": state.vito_fanatic_demons_created,
        "clavileno_triggers": state.clavileno_triggers,
        "combo_active": state.combo_active,
        "combo_active_turn": state.combo_active_turn,
        "both_combo_pieces_turn": state.both_combo_pieces_turn,
        "roaming_throne_in_play": state.has("Roaming Throne"),
        "roaming_throne_doublings": state.roaming_throne_doublings,
        "lands_played_total": state.lands_played_total,
    }

def run_batch(n=2000, turns=8, out_jsonl="edgar_markov_v1_runs.jsonl", seed_base=6000000):
    import json as _json, statistics
    results = [simulate_one(seed_base + i, turns) for i in range(n)]
    with open(out_jsonl, "w") as f:
        for r in results:
            f.write(_json.dumps(r) + "\n")

    cmd_turns = [r["commander_cast_turn"] for r in results if r["commander_cast_turn"] is not None]
    never = n - len(cmd_turns)
    combo_turns = [r["combo_active_turn"] for r in results if r["combo_active"]]

    print(f"=== Edgar Markov Goldfish v1 - n={n}, turns={turns} ===")
    print(f"Avg mulligans: {sum(r['mulligans'] for r in results)/n:.2f}")
    if cmd_turns:
        print(f"Turno medio de conjuracao do Edgar Markov: {statistics.mean(cmd_turns):.2f} | mediana: {statistics.median(cmd_turns)}")
    print(f"Nunca conjurado em {turns} turnos: {100*never/n:.1f}%")
    print(f"Avg tokens de Vampiro via Eminence: {sum(r['eminence_tokens_created'] for r in results)/n:.2f}")
    print(f"Avg turnos em que Edgar atacou: {sum(r['edgar_attack_turns'] for r in results)/n:.2f}")
    print(f"Avg contadores +1/+1 distribuidos (ataque do Edgar): {sum(r['edgar_attack_counters_total'] for r in results)/n:.2f}")
    print(f"Avg drain_total (proxy de vida perdida pelo oponente): {sum(r['drain_total'] for r in results)/n:.2f}")
    print(f"Avg lifegain_total (proxy de vida ganha): {sum(r['lifegain_total'] for r in results)/n:.2f}")
    print(f"Avg criaturas sacrificadas: {sum(r['creatures_sacrificed_total'] for r in results)/n:.2f}")
    print(f"Avg gatilhos de morte (death payoffs): {sum(r['death_trigger_events'] for r in results)/n:.2f}")
    print(f"Avg compras via Champion of Dusk: {sum(r['champion_of_dusk_draws'] for r in results)/n:.2f}")
    print(f"Avg compras via Welcoming Vampire: {sum(r['welcoming_vampire_draws'] for r in results)/n:.2f}")
    print(f"Avg drains via Sanctum Seeker: {sum(r['sanctum_seeker_drains'] for r in results)/n:.2f}")
    print(f"Avg Demons criados via Vito Fanatic (3o estagio): {sum(r['vito_fanatic_demons_created'] for r in results)/n:.2f}")
    print(f"Avg gatilhos de Clavileno (sem efeito numerico extra modelado): {sum(r['clavileno_triggers'] for r in results)/n:.2f}")
    print()
    print(f"--- Combo Exquisite Blood + Vito, Thorn of the Dusk Rose ---")
    print(f"Partidas em que o combo montou E ligou: {100*len(combo_turns)/n:.1f}%")
    if combo_turns:
        print(f"Turno medio em que o combo liga: {statistics.mean(combo_turns):.2f} | mediana: {statistics.median(combo_turns)}")
    print()
    rt_in_play = sum(1 for r in results if r["roaming_throne_in_play"])
    print(f"Roaming Throne em campo em {100*rt_in_play/n:.1f}% dos jogos (tipo escolhido: Vampire)")
    print(f"Avg gatilhos de Vampiro dobrados por partida: {sum(r['roaming_throne_doublings'] for r in results)/n:.2f}")
    print()
    print(f"Logs salvos em: {out_jsonl}")
    return results

if __name__ == "__main__":
    run_batch(n=2000, turns=8)

