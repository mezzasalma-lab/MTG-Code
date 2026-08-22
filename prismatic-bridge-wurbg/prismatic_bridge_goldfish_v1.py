"""
Goldfish simulator - Esika, God of the Tree // The Prismatic Bridge (5 cores - WUBRG)
Escrito e executado por Claude.

Metodologia:
- Tags de cada carta derivadas de oracle_text real (Scryfall,
  /tmp/scryfall_cache/prismatic_bridge_full.json), nao inventadas.
- Este e um simulador FOCADO, nao um goldfish completo de curva geral como
  o do Thranduil/Beorn. Escopo deliberadamente restrito ao que a pergunta
  do usuario pede: turno em que a Bridge resolve, taxa de acerto da Bridge
  em criatura/planeswalker, e sobrevivencia da Bridge/protetores sob
  remocao do oponente - especificamente pra decidir se vale incluir
  Greater Auramancy.
- NAO modelado (limitacao documentada, nao e um bug): a frente do
  comandante (Esika, God of the Tree) e sua habilidade de conceder mana de
  qualquer cor a outras lendarias; habilidades individuais de cada um dos
  17 planeswalkers (loyalty abilities especificas); efeitos dos 11
  criaturas que nao sejam ramp/draw/removal/counter-doubler ja tageados.
  O simulador so joga a carta "The Prismatic Bridge" (verso do MDFC) como
  comandante, direto do zone de comando.
- PREMISSA NAO VALIDADA (usuario nao tem dado real, deck nunca jogado):
  taxa de tentativa de remocao por oponente por turno mirando a Bridge ou
  seus protetores. Default usado: 12% por oponente por turno, 3 oponentes
  (confirmado pelo usuario). Isso e um CHUTE razoavel pra Bracket 3
  upgraded, NAO um dado real - o resultado do teste Greater Auramancy deve
  ser lido como "dado esse chute, o efeito e X", nao como "X e a resposta
  definitiva". Ajustar REMOVAL_CHANCE_PER_OPPONENT se o usuario validar um
  numero diferente depois de jogar partidas reais.
"""

import random
from dataclasses import dataclass, field
from typing import Set, List, Dict, Optional

COMMANDER = "The Prismatic Bridge"
N_OPPONENTS = 3
REMOVAL_CHANCE_PER_OPPONENT = 0.12  # premissa assumida, ver docstring

# Politica de conjuracao da Bridge:
# False (default) = "cast ASAP" - conjura normal na main phase assim que
#   fica pagavel, nunca espera pra flashar (comportamento historico).
# True = "hold for flash" - se um habilitador de flash JA esta em campo,
#   segura a Bridge de proposito (nao conjura normal, mesmo pagavel) e
#   espera a janela de flash no end step alheio, especificamente pra
#   pular a rodada de remocao antes do 1o gatilho de upkeep (o plano de
#   jogo real do usuario). So muda comportamento nos jogos em que um
#   habilitador chega a estar em campo (~17% das partidas, ver auditoria).
HOLD_FOR_FLASH_POLICY = False

DECKLIST_TEXT = """
1 Alchemist's Refuge
1 All Will Be One
1 Aminatou, the Fateshifter
1 Anguished Unmaking
1 Arcane Signet
1 Arena Rector
1 Ashiok, Dream Render
1 Atraxa, Praetors' Voice
1 Blasphemous Act
1 Bloom Tender
1 Carth the Lion
1 Chromatic Lantern
1 Counterspell
1 Damn
1 Deepglow Skate
1 Delighted Halfling
1 Doubling Season
1 Dovin's Veto
1 Elspeth, Sun's Champion
1 Evolution Sage
1 Farseek
1 Farewell
1 Flux Channeler
1 Ichormoon Gauntlet
1 Inexorable Tide
1 Innkeeper's Talent
1 Kaya, Intangible Slayer
1 Liliana, Dreadhorde General
1 Mana Drain
1 Mutational Advantage
1 Narset, Parter of Veils
1 Nature's Lore
1 Nesting Grounds
1 Nicol Bolas, Dragon-God
1 Oath of Nissa
1 Oath of Teferi
1 Oko, the Ringleader
1 Paradox Haze
1 Path to Exile
1 Rhystic Study
1 Ripples of Potential
1 Sol Ring
1 Sphinx of the Second Sun
1 Sterling Grove
1 Supreme Verdict
1 Swan Song
1 Swords to Plowshares
1 Tamiyo, Compleated Sage
1 Tamiyo, Field Researcher
1 Teferi, Hero of Dominaria
1 Teferi, Temporal Archmage
1 Teferi, Time Raveler
1 Teferi, Who Slows the Sunset
1 The Chain Veil
1 The Eternal Wanderer
1 The Peregrine Dynamo
1 The World Tree
1 Three Visits
1 Toxic Deluge
1 Ugin, the Spirit Dragon
1 Urza Assembles the Titans
1 Veil of Summer
1 Void Rend
1 Vorinclex, Monstrous Raider
1 Vraska, Betrayal's Sting
1 Badlands
1 Bayou
1 Blood Crypt
1 Breeding Pool
1 Brushland
1 City of Brass
1 Command Tower
1 Emergence Zone
1 Exotic Orchard
1 Fabled Passage
1 Godless Shrine
1 Hallowed Fountain
1 Interplanar Beacon
1 Mana Confluence
1 Overgrown Tomb
1 Plateau
1 Plaza of Heroes
1 Sacred Foundry
1 Savannah
1 Scrubland
1 Snow-Covered Forest
1 Snow-Covered Island
1 Snow-Covered Mountain
1 Snow-Covered Plains
1 Snow-Covered Swamp
1 Steam Vents
1 Stomping Ground
1 Taiga
1 Temple Garden
1 Tropical Island
1 Tundra
1 Underground Sea
1 Volcanic Island
1 Watery Grave
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

# -------- Comandante (so o verso - ver limitacao no docstring) --------
add("The Prismatic Bridge", 5, "Enchantment", colors={"B", "G", "R", "U", "W"}, tags={"bridge_engine"})
add("Greater Auramancy", 2, "Enchantment", colors={"W"}, tags={"protection_shroud"})

# -------- Deck (99 cartas, geradas via Scryfall cards/collection) --------
add("Alchemist's Refuge", 0, "Land", colors={"G", "U"}, produces={"C"}, tags={"flash_enabler"})
add("All Will Be One", 5, "Enchantment", colors={"R"}, produces=set(), tags=set())
add("Aminatou, the Fateshifter", 3, "Planeswalker", colors={"B", "U", "W"}, produces=set(), tags={"draw", "planeswalker"})
add("Anguished Unmaking", 3, "Instant", colors={"B", "W"}, produces=set(), tags={"removal"})
add("Arcane Signet", 2, "Artifact", colors=set(), produces={"B", "G", "R", "U", "W"}, tags={"ramp"})
add("Arena Rector", 4, "Creature", colors={"W"}, produces=set(), tags={"creature"})
add("Ashiok, Dream Render", 3, "Planeswalker", colors={"B", "U"}, produces=set(), tags={"planeswalker"})
add("Atraxa, Praetors' Voice", 4, "Creature", colors={"B", "G", "U", "W"}, produces=set(), tags={"creature", "proliferate"})
add("Blasphemous Act", 9, "Sorcery", colors={"R"}, produces=set(), tags={"wipe"})
add("Bloom Tender", 2, "Creature", colors={"G"}, produces={"B", "G", "R", "U", "W"}, tags={"creature", "ramp"})
add("Carth the Lion", 4, "Creature", colors={"B", "G"}, produces=set(), tags={"creature"})
add("Chromatic Lantern", 3, "Artifact", colors=set(), produces={"B", "G", "R", "U", "W"}, tags={"ramp"})
add("Counterspell", 2, "Instant", colors={"U"}, produces=set(), tags={"counterspell"})
add("Damn", 2, "Sorcery", colors={"B", "W"}, produces=set(), tags={"removal"})
add("Deepglow Skate", 5, "Creature", colors={"U"}, produces=set(), tags={"counter_doubler", "creature"})
add("Delighted Halfling", 1, "Creature", colors={"G"}, produces={"B", "C", "G", "R", "U", "W"}, tags={"creature", "ramp"})
add("Doubling Season", 5, "Enchantment", colors={"G"}, produces=set(), tags={"counter_doubler"})
add("Dovin's Veto", 2, "Instant", colors={"U", "W"}, produces=set(), tags=set())
add("Elspeth, Sun's Champion", 6, "Planeswalker", colors={"W"}, produces=set(), tags={"planeswalker", "wipe"})
add("Evolution Sage", 3, "Creature", colors={"G"}, produces=set(), tags={"creature", "proliferate"})
add("Farseek", 2, "Sorcery", colors={"G"}, produces=set(), tags={"ramp"})
add("Farewell", 6, "Sorcery", colors={"W"}, produces=set(), tags={"wipe"})
add("Flux Channeler", 3, "Creature", colors={"U"}, produces=set(), tags={"creature", "proliferate"})
add("Ichormoon Gauntlet", 3, "Artifact", colors={"U"}, produces=set(), tags={"proliferate"})
add("Inexorable Tide", 5, "Enchantment", colors={"U"}, produces=set(), tags={"proliferate"})
add("Innkeeper's Talent", 2, "Enchantment", colors={"G"}, produces=set(), tags={"counter_doubler"})
add("Kaya, Intangible Slayer", 7, "Planeswalker", colors={"B", "W"}, produces=set(), tags={"draw", "planeswalker", "removal"})
add("Liliana, Dreadhorde General", 6, "Planeswalker", colors={"B"}, produces=set(), tags={"draw", "planeswalker", "wipe"})
add("Mana Drain", 2, "Instant", colors={"U"}, produces=set(), tags={"counterspell"})
add("Mutational Advantage", 3, "Instant", colors={"G", "U"}, produces=set(), tags={"proliferate"})
add("Narset, Parter of Veils", 3, "Planeswalker", colors={"U"}, produces=set(), tags={"planeswalker"})
add("Nature's Lore", 2, "Sorcery", colors={"G"}, produces=set(), tags={"ramp"})
add("Nesting Grounds", 0, "Land", colors=set(), produces={"C"}, tags=set())
add("Nicol Bolas, Dragon-God", 5, "Planeswalker", colors={"B", "R", "U"}, produces=set(), tags={"draw", "planeswalker", "removal"})
add("Oath of Nissa", 1, "Enchantment", colors={"G"}, produces=set(), tags=set())
add("Oath of Teferi", 5, "Enchantment", colors={"U", "W"}, produces=set(), tags=set())
add("Oko, the Ringleader", 4, "Planeswalker", colors={"G", "U"}, produces=set(), tags={"draw", "planeswalker"})
add("Paradox Haze", 3, "Enchantment", colors={"U"}, produces=set(), tags={"extra_upkeep"})
add("Path to Exile", 1, "Instant", colors={"W"}, produces=set(), tags={"removal"})
add("Rhystic Study", 3, "Enchantment", colors={"U"}, produces=set(), tags={"draw"})
add("Ripples of Potential", 2, "Instant", colors={"U"}, produces=set(), tags={"proliferate"})
add("Sol Ring", 1, "Artifact", colors=set(), produces={"C"}, tags={"ramp"})
add("Sphinx of the Second Sun", 8, "Creature", colors={"U"}, produces=set(), tags={"creature"})
add("Sterling Grove", 2, "Enchantment", colors={"G", "W"}, produces=set(), tags={"protection_shroud"})
add("Supreme Verdict", 4, "Sorcery", colors={"U", "W"}, produces=set(), tags={"wipe"})
add("Swan Song", 1, "Instant", colors={"U"}, produces=set(), tags=set())
add("Swords to Plowshares", 1, "Instant", colors={"W"}, produces=set(), tags={"removal"})
add("Tamiyo, Compleated Sage", 5, "Planeswalker", colors={"G", "U"}, produces=set(), tags={"draw", "planeswalker", "removal"})
add("Tamiyo, Field Researcher", 4, "Planeswalker", colors={"G", "U", "W"}, produces=set(), tags={"draw", "planeswalker"})
add("Teferi, Hero of Dominaria", 5, "Planeswalker", colors={"U", "W"}, produces=set(), tags={"draw", "planeswalker", "removal"})
add("Teferi, Temporal Archmage", 6, "Planeswalker", colors={"U"}, produces=set(), tags={"planeswalker"})
add("Teferi, Time Raveler", 3, "Planeswalker", colors={"U", "W"}, produces=set(), tags={"draw", "planeswalker"})
add("Teferi, Who Slows the Sunset", 4, "Planeswalker", colors={"U", "W"}, produces=set(), tags={"draw", "planeswalker"})
add("The Chain Veil", 4, "Artifact", colors=set(), produces=set(), tags=set())
add("The Eternal Wanderer", 6, "Planeswalker", colors={"W"}, produces=set(), tags={"planeswalker", "wipe"})
add("The Peregrine Dynamo", 3, "Creature", colors=set(), produces=set(), tags={"creature"})
add("The World Tree", 0, "Land", colors={"B", "G", "R", "U", "W"}, produces={"B", "G", "R", "U", "W"}, tags=set())
add("Three Visits", 2, "Sorcery", colors={"G"}, produces=set(), tags={"ramp"})
add("Toxic Deluge", 3, "Sorcery", colors={"B"}, produces=set(), tags={"wipe"})
add("Ugin, the Spirit Dragon", 8, "Planeswalker", colors=set(), produces=set(), tags={"draw", "planeswalker", "removal"})
add("Urza Assembles the Titans", 5, "Enchantment", colors={"W"}, produces=set(), tags=set())
add("Veil of Summer", 1, "Instant", colors={"G"}, produces=set(), tags={"draw"})
add("Void Rend", 3, "Instant", colors={"B", "U", "W"}, produces=set(), tags={"removal"})
add("Vorinclex, Monstrous Raider", 6, "Creature", colors={"G"}, produces=set(), tags={"counter_doubler", "creature"})
add("Vraska, Betrayal's Sting", 6, "Planeswalker", colors={"B"}, produces={"B", "G", "R", "U", "W"}, tags={"draw", "planeswalker", "proliferate", "ramp"})
add("Badlands", 0, "Land", colors={"B", "R"}, produces={"B", "R"}, tags=set())
add("Bayou", 0, "Land", colors={"B", "G"}, produces={"B", "G"}, tags=set())
add("Blood Crypt", 0, "Land", colors={"B", "R"}, produces={"B", "R"}, tags=set())
add("Breeding Pool", 0, "Land", colors={"G", "U"}, produces={"G", "U"}, tags=set())
add("Brushland", 0, "Land", colors={"G", "W"}, produces={"C", "G", "W"}, tags=set())
add("City of Brass", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())
add("Command Tower", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())
add("Emergence Zone", 0, "Land", colors=set(), produces={"C"}, tags={"flash_enabler"})
add("Exotic Orchard", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())
add("Fabled Passage", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())  # busca qualquer basica
add("Godless Shrine", 0, "Land", colors={"B", "W"}, produces={"B", "W"}, tags=set())
add("Hallowed Fountain", 0, "Land", colors={"U", "W"}, produces={"U", "W"}, tags=set())
add("Interplanar Beacon", 0, "Land", colors=set(), produces={"B", "C", "G", "R", "U", "W"}, tags=set())
add("Mana Confluence", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())
add("Overgrown Tomb", 0, "Land", colors={"B", "G"}, produces={"B", "G"}, tags=set())
add("Plateau", 0, "Land", colors={"R", "W"}, produces={"R", "W"}, tags=set())
add("Plaza of Heroes", 0, "Land", colors=set(), produces={"B", "C", "G", "R", "U", "W"}, tags=set())
add("Sacred Foundry", 0, "Land", colors={"R", "W"}, produces={"R", "W"}, tags=set())
add("Savannah", 0, "Land", colors={"G", "W"}, produces={"G", "W"}, tags=set())
add("Scrubland", 0, "Land", colors={"B", "W"}, produces={"B", "W"}, tags=set())
add("Snow-Covered Forest", 0, "Land", colors={"G"}, produces={"G"}, tags=set())
add("Snow-Covered Island", 0, "Land", colors={"U"}, produces={"U"}, tags=set())
add("Snow-Covered Mountain", 0, "Land", colors={"R"}, produces={"R"}, tags=set())
add("Snow-Covered Plains", 0, "Land", colors={"W"}, produces={"W"}, tags=set())
add("Snow-Covered Swamp", 0, "Land", colors={"B"}, produces={"B"}, tags=set())
add("Steam Vents", 0, "Land", colors={"R", "U"}, produces={"R", "U"}, tags=set())
add("Stomping Ground", 0, "Land", colors={"G", "R"}, produces={"G", "R"}, tags=set())
add("Taiga", 0, "Land", colors={"G", "R"}, produces={"G", "R"}, tags=set())
add("Temple Garden", 0, "Land", colors={"G", "W"}, produces={"G", "W"}, tags=set())
add("Tropical Island", 0, "Land", colors={"G", "U"}, produces={"G", "U"}, tags=set())
add("Tundra", 0, "Land", colors={"U", "W"}, produces={"U", "W"}, tags=set())
add("Underground Sea", 0, "Land", colors={"B", "U"}, produces={"B", "U"}, tags=set())
add("Volcanic Island", 0, "Land", colors={"R", "U"}, produces={"R", "U"}, tags=set())
add("Watery Grave", 0, "Land", colors={"B", "U"}, produces={"B", "U"}, tags=set())

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

def has_tag(card: str, tag: str) -> bool:
    return tag in C(card).tags

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
    mana_spent_this_turn: int = 0
    mana_held_back: int = 0  # mana nao gasta no ultimo turno, disponivel pra flash no end step alheio (untap so acontece no MEU untap step - CR 500.1 - entao isso NAO reseta pra total_mana entre meus turnos)
    lands_played_total: int = 0

    bridge_in_play: bool = False
    bridge_cast_turn: Optional[int] = None
    bridge_first_cast_turn: Optional[int] = None
    bridge_cast_count: int = 0
    bridge_removed_count: int = 0
    bridge_flash_cast: bool = False
    bridge_triggers: int = 0
    bridge_hits_creature: int = 0
    bridge_hits_planeswalker: int = 0
    bridge_no_hit_empty_library: int = 0
    first_pw_hit_turn: Optional[int] = None

    protectors_removed_count: int = 0
    removal_attempts_total: int = 0
    removal_attempts_wasted: int = 0

    with_greater_auramancy: bool = False

    def draw(self, n: int = 1):
        for _ in range(n):
            if self.library:
                self.hand.append(self.library.pop(0))

    def has(self, name: str) -> bool:
        return name in self.battlefield

# =========================================================
# MANA MODEL
# =========================================================

def total_mana(state: GameState) -> int:
    total = 0
    for card in state.battlefield:
        if is_land(card):
            total += 1
        elif card == "Sol Ring":
            total += 2
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

def bridge_effective_mv(state: GameState) -> int:
    return C(COMMANDER).mv + 2 * state.bridge_cast_count

def can_cast(state: GameState, card: str) -> bool:
    mv = bridge_effective_mv(state) if card == COMMANDER else C(card).mv
    if remaining_mana(state) < mv:
        return False
    for color in C(card).colors:
        if color_sources(state, color) < 1:
            return False
    return True

# =========================================================
# MULLIGAN (simplificado - so garante mao jogavel de terrenos)
# =========================================================

# Rocks/dorks reais que aceleram de verdade (validado por analise de
# correlacao, n=8000 maos, 2026-08-21): Sol Ring/Arcane Signet/Bloom
# Tender/Delighted Halfling/Chromatic Lantern reduzem o turno medio da
# 1a conjuracao da Bridge de ~4,1-4,2 pra ~3,2-3,8 quando estao na mao
# inicial. Farseek/Nature's Lore/Three Visits (tutores de terreno) NAO
# entram aqui de proposito - a mesma analise mostrou que eles pioram a
# velocidade (custam carta+2 mana pra fazer o que 1 land drop ja faz de
# graca), entao nao contam como equivalente a um rock pra decisao de
# mulligan.
FAST_RAMP_ROCKS_DORKS = {"Sol Ring", "Arcane Signet", "Chromatic Lantern", "Bloom Tender", "Delighted Halfling"}

def should_keep(hand: List[str]) -> bool:
    # Heuristico validado por dados (n=8000, 2026-08-21): 2 terrenos sem
    # rock e uma mao ruim de verdade (turno medio 5,72, 31,8% nunca
    # conjura a Bridge) - pior que 3 terrenos sozinhos (4,50/14,0%), que
    # por sua vez e pior que 2 terrenos + 1 rock (4,32/12,2%). Exige 3+
    # terrenos OU 2 terrenos + pelo menos 1 rock/dork real.
    lands = sum(1 for c in hand if is_land(c))
    if lands > 5:
        return False
    if lands >= 3:
        return True
    if lands == 2:
        return any(c in FAST_RAMP_ROCKS_DORKS for c in hand)
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
    # prioriza terreno que cobre cor que falta
    have_colors = set()
    for c in state.battlefield:
        have_colors |= C(c).produces
    missing = {"W", "U", "B", "R", "G"} - have_colors
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
# BRIDGE ENGINE
# =========================================================

def bridge_upkeep_trigger(state: GameState, log: List[Dict]):
    state.bridge_triggers += 1
    revealed_nonhit = []
    hit = None
    while state.library:
        card = state.library.pop(0)
        if C(card).type in ("Creature", "Planeswalker"):
            hit = card
            break
        revealed_nonhit.append(card)
    state.rng.shuffle(revealed_nonhit)
    state.library.extend(revealed_nonhit)
    if hit:
        state.battlefield.append(hit)
        if C(hit).type == "Creature":
            state.bridge_hits_creature += 1
        else:
            state.bridge_hits_planeswalker += 1
            if state.first_pw_hit_turn is None:
                state.first_pw_hit_turn = state.turn
        log.append({"trigger": "bridge_hit", "card": hit, "type": C(hit).type, "turn": state.turn})
    else:
        state.bridge_no_hit_empty_library += 1
        log.append({"trigger": "bridge_no_hit", "reason": "biblioteca vazia", "turn": state.turn})

# Custo pra ativar cada habilitador de flash (generico, simplificacao - o
# Alchemist's Refuge exige G+U especificamente, tratado aqui so como 2
# generico ja que color_sources ja garante que essas cores existem no
# manabase). Emergence Zone se sacrifica ao ser usado (perde a fonte de
# mana permanentemente, nao so tapa).
FLASH_ENABLER_COST = {"Alchemist's Refuge": 2, "Emergence Zone": 1}

def choose_flash_enabler(state: GameState) -> Optional[str]:
    candidates = [c for c in state.battlefield if has_tag(c, "flash_enabler")]
    if not candidates:
        return None
    # prioriza o mais barato
    candidates.sort(key=lambda c: FLASH_ENABLER_COST.get(c, 0))
    return candidates[0]

def can_flash_bridge(state: GameState) -> bool:
    # A Bridge vem da zona de comando, nao precisa estar na mao (mesma
    # convencao do simulador do Thranduil: comandante sempre "disponivel").
    # IMPORTANTE: untap so acontece no MEU untap step (CR 500.1 - untap,
    # upkeep, draw). Terrenos ficam tapados do jeito que ficaram no meu
    # ultimo turno durante os turnos dos oponentes - entao a mana
    # disponivel pra flashar no end step alheio e o que sobrou NAO GASTO
    # do meu ultimo turno (state.mana_held_back), nao o total_mana atual.
    if state.bridge_in_play:
        return False
    enabler = choose_flash_enabler(state)
    if enabler is None:
        return False
    needed = FLASH_ENABLER_COST[enabler] + bridge_effective_mv(state)
    if state.mana_held_back < needed:
        return False
    for color in C(COMMANDER).colors:
        if color_sources(state, color) < 1:
            return False
    return True

def cast_bridge(state: GameState, log: List[Dict], via_flash: bool):
    if COMMANDER in state.hand:
        state.hand.remove(COMMANDER)
    mv = bridge_effective_mv(state)
    if via_flash:
        enabler = choose_flash_enabler(state)
        cost = FLASH_ENABLER_COST[enabler] + mv
        state.mana_held_back -= cost
        if enabler == "Emergence Zone":
            state.battlefield.remove(enabler)  # se sacrifica ao ativar
        log.append({"action": "flash_enabler_used", "card": enabler, "turn": state.turn})
    else:
        state.mana_spent_this_turn += mv
    state.battlefield.append(COMMANDER)
    state.bridge_in_play = True
    state.bridge_cast_turn = state.turn
    if state.bridge_first_cast_turn is None:
        state.bridge_first_cast_turn = state.turn
    state.bridge_cast_count += 1
    state.bridge_flash_cast = via_flash
    log.append({"action": "cast_bridge", "via_flash": via_flash, "turn": state.turn, "effective_mv": mv})

# =========================================================
# REMOCAO DO OPONENTE (premissa assumida - ver docstring)
# =========================================================

def protectors_in_play(state: GameState) -> List[str]:
    prot = ["Sterling Grove"]
    if state.with_greater_auramancy:
        prot.append("Greater Auramancy")
    return [p for p in prot if state.has(p)]

def resolve_removal_round(state: GameState, log: List[Dict]):
    if not state.bridge_in_play and not protectors_in_play(state):
        return
    for _ in range(N_OPPONENTS):
        if state.rng.random() >= REMOVAL_CHANCE_PER_OPPONENT:
            continue
        state.removal_attempts_total += 1
        prot = protectors_in_play(state)
        if prot:
            target = state.rng.choice(prot)
            state.battlefield.remove(target)
            state.graveyard.append(target)  # simplificacao: remocao = destroy (maioria dos casos reais)
            state.protectors_removed_count += 1
            log.append({"trigger": "removal", "target": target, "turn": state.turn})
        elif state.bridge_in_play:
            state.battlefield.remove(COMMANDER)
            state.bridge_in_play = False
            state.bridge_removed_count += 1
            log.append({"trigger": "removal", "target": COMMANDER, "turn": state.turn})
        else:
            state.removal_attempts_wasted += 1

# =========================================================
# TURNO
# =========================================================

def main_phase(state: GameState, log: List[Dict]):
    # protetores primeiro (sao baratos e habilitam a Bridge)
    protection_cards = [c for c in state.hand if has_tag(c, "protection_shroud") and can_cast(state, c)]
    for c in sorted(protection_cards, key=lambda c: C(c).mv):
        state.hand.remove(c)
        state.mana_spent_this_turn += C(c).mv
        state.battlefield.append(c)
        log.append({"action": "cast", "card": c, "turn": state.turn})

    # Bridge via main phase normal, se nao foi flashada nesse ciclo.
    # Sob HOLD_FOR_FLASH_POLICY, se um habilitador de flash ja esta em
    # campo, o jogador segura a Bridge de proposito (nao conjura normal
    # mesmo pagavel) e espera a janela de flash no end step alheio.
    skip_normal_cast = HOLD_FOR_FLASH_POLICY and choose_flash_enabler(state) is not None
    if not state.bridge_in_play and not skip_normal_cast and can_cast(state, COMMANDER):
        cast_bridge(state, log, via_flash=False)

    # Se ja tem habilitador de flash em campo e a Bridge ainda nao saiu,
    # o jogador segura mana de proposito pra linha de flash no end step
    # alheio (plano de jogo explicito do usuario) - nao gasta tudo no
    # resto da mao.
    reserved = 0
    if not state.bridge_in_play:
        enabler = choose_flash_enabler(state)
        if enabler is not None:
            reserved = FLASH_ENABLER_COST[enabler] + bridge_effective_mv(state)

    # resto da mao, ordem generica por CMC crescente, respeitando a reserva
    for _ in range(8):
        budget = remaining_mana(state) - reserved
        castables = [c for c in state.hand if c != COMMANDER and can_cast(state, c) and C(c).mv <= budget]
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
        log.append({"action": "cast", "card": choice, "turn": state.turn})

def play_turn(state: GameState, turn: int, game_log: List[List[Dict]]):
    state.turn = turn
    state.land_played = False
    state.mana_spent_this_turn = 0
    log = []

    # Linha de flash no end step do oponente anterior (ver docstring: modelado
    # como acontecendo ANTES da rodada de remocao deste turno, entao a Bridge
    # flashada escapa da rodada de remocao que precede seu primeiro gatilho)
    if can_flash_bridge(state):
        cast_bridge(state, log, via_flash=True)

    resolve_removal_round(state, log)

    if state.bridge_in_play:
        n_triggers = 2 if state.has("Paradox Haze") else 1
        for _ in range(n_triggers):
            bridge_upkeep_trigger(state, log)

    state.draw(1)
    play_land(state, log)
    main_phase(state, log)

    # Mana nao gasta neste turno fica destapada ate o MEU proximo untap
    # step (CR 500.1) - e a mana real disponivel pra flashar algo no end
    # step de um oponente antes do meu proximo turno.
    state.mana_held_back = max(0, total_mana(state) - state.mana_spent_this_turn)

    game_log.append(log)

# =========================================================
# SIMULACAO
# =========================================================

def build_decklist(with_greater_auramancy: bool) -> str:
    if not with_greater_auramancy:
        return DECKLIST_TEXT
    # troca 1 carta de baixo synergy score/pouco impacto pela Greater Auramancy
    # (The Peregrine Dynamo - unica criatura sem nenhuma tag de sinergia)
    return DECKLIST_TEXT.replace("1 The Peregrine Dynamo\n", "1 Greater Auramancy\n")

def simulate_one(seed: int, turns: int, with_greater_auramancy: bool) -> Dict:
    rng = random.Random(seed)
    decklist = build_decklist(with_greater_auramancy)
    deck = parse_decklist(decklist)
    assert len(deck) == 99, f"Mainboard deveria ser 99, deu {len(deck)}"
    rng.shuffle(deck)
    state = GameState(rng=rng, library=deck, with_greater_auramancy=with_greater_auramancy)

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
        "bridge_cast_turn": state.bridge_cast_turn,
        "bridge_first_cast_turn": state.bridge_first_cast_turn,
        "bridge_flash_cast": state.bridge_flash_cast,
        "bridge_cast_count": state.bridge_cast_count,
        "bridge_in_play_end": state.bridge_in_play,
        "bridge_removed_count": state.bridge_removed_count,
        "bridge_triggers": state.bridge_triggers,
        "bridge_hits_creature": state.bridge_hits_creature,
        "bridge_hits_planeswalker": state.bridge_hits_planeswalker,
        "first_pw_hit_turn": state.first_pw_hit_turn,
        "bridge_no_hit": state.bridge_no_hit_empty_library,
        "protectors_removed_count": state.protectors_removed_count,
        "removal_attempts_total": state.removal_attempts_total,
        "lands_played_total": state.lands_played_total,
    }

def run_batch(n=2000, turns=10, with_greater_auramancy=False, seed_base=3000000, label=""):
    import statistics
    results = [simulate_one(seed_base + i, turns, with_greater_auramancy) for i in range(n)]

    bridge_turns = [r["bridge_cast_turn"] for r in results if r["bridge_cast_turn"] is not None]
    first_cast_turns = [r["bridge_first_cast_turn"] for r in results if r["bridge_first_cast_turn"] is not None]
    never = n - len(bridge_turns)
    flash_casts = sum(1 for r in results if r["bridge_flash_cast"])
    total_triggers = sum(r["bridge_triggers"] for r in results)
    total_hits_creature = sum(r["bridge_hits_creature"] for r in results)
    total_hits_pw = sum(r["bridge_hits_planeswalker"] for r in results)
    end_in_play = sum(1 for r in results if r["bridge_in_play_end"])
    avg_removed = sum(r["bridge_removed_count"] for r in results) / n
    avg_protectors_removed = sum(r["protectors_removed_count"] for r in results) / n
    avg_attempts = sum(r["removal_attempts_total"] for r in results) / n

    print(f"=== Prismatic Bridge Goldfish v1 ({label}) — n={n}, turns={turns} ===")
    print(f"Greater Auramancy no deck: {with_greater_auramancy}")
    print(f"Avg mulligans: {sum(r['mulligans'] for r in results)/n:.2f}")
    print(f"Bridge nunca conjurada em {turns} turnos: {100*never/n:.1f}%")
    if first_cast_turns:
        print(f"Turno medio da PRIMEIRA conjuracao da Bridge: {statistics.mean(first_cast_turns):.2f} | mediana: {statistics.median(first_cast_turns)}")
    if bridge_turns:
        print(f"Turno medio da ULTIMA conjuracao (inclui recasts pos-remocao, taxa de comandante +2 cada vez): {statistics.mean(bridge_turns):.2f} | mediana: {statistics.median(bridge_turns)}")
    print(f"Conjurada via flash (end step anterior): {100*flash_casts/n:.1f}% das partidas")
    print(f"Avg gatilhos de upkeep da Bridge por partida: {total_triggers/n:.2f}")
    print(f"  Acertos em criatura: {total_hits_creature} | em planeswalker: {total_hits_pw} | total: {total_hits_creature+total_hits_pw}")
    print(f"% da Bridge ainda em campo no fim da simulacao: {100*end_in_play/n:.1f}%")
    print(f"Avg vezes que a Bridge foi removida por partida: {avg_removed:.2f}")
    print(f"Avg vezes que um protetor (Sterling Grove/Greater Auramancy) foi removido: {avg_protectors_removed:.2f}")
    print(f"Avg tentativas de remocao do oponente por partida (premissa: {REMOVAL_CHANCE_PER_OPPONENT*100:.0f}%/oponente/turno, {N_OPPONENTS} oponentes): {avg_attempts:.2f}")

    pw_hit_turns = [r["first_pw_hit_turn"] for r in results if r["first_pw_hit_turn"] is not None]
    from collections import Counter
    c = Counter(pw_hit_turns)
    print(f"\n--- Bridge colocou planeswalker em jogo (1o acerto de PW via gatilho de upkeep) ---")
    for t in [6, 7, 8]:
        cum = sum(v for k, v in c.items() if k <= t)
        print(f"  Chance acumulada ate o turno {t}: {100*cum/n:.1f}%")
    never_pw = n - len(pw_hit_turns)
    print(f"  Nunca acertou planeswalker em {turns} turnos: {100*never_pw/n:.1f}%")
    print()
    return results

if __name__ == "__main__":
    run_batch(n=2000, turns=10, with_greater_auramancy=False, label="SEM Greater Auramancy (lista atual)")
    run_batch(n=2000, turns=10, with_greater_auramancy=True, label="COM Greater Auramancy (troca The Peregrine Dynamo)")
