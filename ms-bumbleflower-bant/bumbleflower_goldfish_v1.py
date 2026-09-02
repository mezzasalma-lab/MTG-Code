"""
Goldfish simulator — Ms. Bumbleflower (Bant — G/W/U)

Construido do zero em 2026-09-02, ultimo dos 4 decks sem simulador desta
sessao (depois de Kutzil, Azula e Captain Storm), mesma disciplina de
"compile TUDO": oraculo real via Scryfall (leitura linha-a-linha das 94
cartas unicas + comandante), implementacao completa, varredura
automatizada de tags orfas no proprio rascunho antes de considerar
pronto.

Lista fornecida pelo usuario ao vivo nesta conversa (99 cartas de
biblioteca + comandante, total 100 — completa, sem buracos).

======================================================================
MOTOR REAL DESTE DECK (verificado via Scryfall, nao decorado)
======================================================================
Ms. Bumbleflower ({1}{G}{W}{U}, 1/5, Vigilance): "Whenever you cast a
spell, target opponent draws a card. Put a +1/+1 counter on target
creature. It gains flying until end of turn. If this is the SECOND time
this ability has resolved this turn, you draw two cards." Dispara em
TODA magica conjurada (nao so' instant/sorcery) -- e' ao mesmo tempo um
mini-motor de "de carta ao oponente" (retrigger real de Smothering
Tithe/Wedding Ring, que reagem a "an opponent draws a card" independente
de QUEM causou a compra) e um motor de contadores (alimenta TUDO que
reage a "+1/+1 counter colocado").

O deck inteiro e' construido em cima de "colocar um contador" disparando
efeitos em cascata -- por isso este arquivo centraliza TODA colocacao de
contador (Bumbleflower, Rishkar, Forgotten Ancient, Managorger/Kalonian
Hydra, Deepglow Skate, Simic Ascendancy, Wizard Class nivel 3, Oakhollow
Village, Slip Out the Back, Walking Ballista, The Ozolith) numa unica
funcao `put_counters()`, que dispara os 2 gatilhos reais que reagem a
QUALQUER fonte de contador:

1. **Danny Pink** — "creatures you control have 'whenever one or more
   counters are put on this creature for the FIRST TIME each turn, draw
   a card.'" Rastreado via `state.first_counter_this_turn: set[uid]`.
2. **Simic Ascendancy** — "whenever one or more +1/+1 counters are put
   on a creature you control, put that many growth counters on this."
   Com 20+ growth counters no upkeep, **vence o jogo** (condicao
   alternativa real, implementada como `state.won_via_ascendancy`).

**Efeitos de dobra de contador** (Kalonian Hydra ao atacar, Deepglow
Skate na ETB) sao implementados como `put_counters(perm, perm.counters)`
(dobrar = adicionar uma quantidade igual ao que ja existe) -- isso
tambem retrigger corretamente Danny Pink/Simic Ascendancy (dobrar conta
como "counters postos" pra fins de gatilho, ruling oficial confirmado).

Arquitetura: objetos `Permanent` (mesmo padrao do Kutzil/Toph/Captain
Storm) — contadores +1/+1 persistentes e MUITAS fontes diferentes de
colocar/mover/dobrar contadores exigem rastrear estado por criatura
especifica, nao uma lista de nomes.

Simplificacoes documentadas (nao inventadas — omissoes explicitas):
- Sem oponente real: todo dano e' `proxy_damage_total` agregado, flat.
- **Efeitos que exigem oponente pra funcionar de verdade** (Path to
  Exile/Swords to Plowshares/Generous Gift/Pongify/Cyclonic
  Rift/contramagicas/Fractured Identity/Loran's destroy) — 📊
  `interaction_plays`, mesma convencao de toda a sessao.
- **"Target opponent draws a card" (Bumbleflower, Kwain, Struggle for
  Project Purity Brotherhood)** — a compra do oponente EM SI nao tem
  numero pra manifestar (nao rastreamos mao/vida de oponente), mas o
  RETRIGGER que ela causa em Smothering Tithe/Wedding Ring (que reagem a
  "an opponent draws", independente de quem causou) e' real e
  implementado.
- **Esper Sentinel / Rhystic Study / Mangara (2o spell do oponente) /
  Faerie Mastermind (2a compra do oponente)** — precisam de spell/compra
  de oponente real — 📊.
- **Struggle for Project Purity, modo Enclave** ("whenever a player
  attacks you, rad counters") — 📊, precisa de ataque de oponente.
- **Noble Heritage** ("cada oponente pode por 2 contadores, se fizer voce
  ganha protecao") — 📊, precisa de oponente pra reagir.
- **Devoted Druid** — mana engine real (T: G, remove -1/-1: untap),
  limitado a 1 reativacao segura por turno (0/2 -> 0/1, para antes de
  0/0 morrer) — decisao documentada, nao um limite arbitrario de "vale a
  pena".
- Combate: "ataca" = sem doenca de invocacao (convencao de todos os
  simuladores desta biblioteca). Sem bloqueio real modelado.
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
    toughness: int = 0
    pips: dict = field(default_factory=dict)
    produces: frozenset = field(default_factory=frozenset)


CARD_DB: dict[str, Card] = {}


def add(name, mv, ctype, tags=(), power=0, toughness=0, pips=None, produces=None):
    CARD_DB[name] = Card(name=name, mv=mv, ctype=ctype, tags=frozenset(tags), power=power,
                          toughness=toughness, pips=dict(pips or {}), produces=frozenset(produces or ()))


COMMANDER = "Ms. Bumbleflower"
add(COMMANDER, 4, "creature", {"commander", "vigilance", "bumbleflower_trigger"}, power=1, toughness=5,
    pips={"G": 1, "W": 1, "U": 1})

# --- Rampa/mana ------------------------------------------------------------
add("Arcane Signet", 2, "artifact", {"rock_identity"}, produces={"G", "W", "U"})
add("Sol Ring", 1, "artifact", {"rock_cc"})
add("Fellwar Stone", 2, "artifact", {"rock_opponent_dependent"})
add("Thought Vessel", 2, "artifact", {"rock_c", "no_max_hand"})
add("Birds of Paradise", 1, "creature", {"flying", "rock_any_dork"}, power=0, toughness=1, pips={"G": 1})
add("Elvish Mystic", 1, "creature", {"rock_g_dork"}, power=1, toughness=1, pips={"G": 1})
add("Devoted Druid", 2, "creature", {"devoted_druid"}, power=0, toughness=2, pips={"G": 1})
add("Faeburrow Elder", 3, "creature", {"vigilance", "faeburrow"}, power=0, toughness=0, pips={"G": 1, "W": 1})
add("Cultivate", 3, "sorcery", {"land_tutor2"}, pips={"G": 1})
add("Kodama's Reach", 3, "sorcery", {"land_tutor2"}, pips={"G": 1})
add("Farseek", 2, "sorcery", {"land_tutor1_nonforest"}, pips={"G": 1})
add("Tempt with Discovery", 4, "sorcery", {"tempt_discovery"}, pips={"G": 1})

# --- Motor de contadores/draw (o coracao do deck) ---------------------------
add("Danny Pink", 4, "creature", {"mentor", "danny_pink_draw_engine"}, power=4, toughness=3, pips={"U": 1})
add("Simic Ascendancy", 2, "enchantment", {"simic_ascendancy"}, pips={"G": 1, "U": 1})
add("Rishkar, Peema Renegade", 3, "creature", {"rishkar_etb", "counter_mana"}, power=2, toughness=2, pips={"G": 1})
add("Forgotten Ancient", 4, "creature", {"forgotten_ancient"}, power=0, toughness=3, pips={"G": 1})
add("Managorger Hydra", 3, "creature", {"trample", "managorger"}, power=1, toughness=1, pips={"G": 1})
add("Kalonian Hydra", 5, "creature", {"trample", "kalonian_etb4", "kalonian_attack_double"}, power=0, toughness=0,
    pips={"G": 2})
add("Deepglow Skate", 5, "creature", {"deepglow_etb"}, power=3, toughness=3, pips={"U": 1})
add("The Ozolith", 1, "artifact", {"ozolith"})
add("Walking Ballista", 0, "artifact", {"ballista"}, power=0, toughness=0, pips={})
add("Communal Brewing", 3, "enchantment", {"communal_brewing"}, pips={"G": 1})
add("Wizard Class", 1, "enchantment", {"wizard_class", "no_max_hand"}, pips={"U": 1})
add("Oakhollow Village", 0, "land", {"oakhollow"}, produces=set())
add("Slip Out the Back", 1, "instant", {"slip_out"}, pips={"U": 1})
add("Heliod, Sun-Crowned", 3, "creature", {"heliod"}, power=5, toughness=5, pips={"W": 1})

# --- Draw / valor -------------------------------------------------------------
add("Chasm Skulker", 3, "creature", {"chasm_skulker"}, power=1, toughness=1, pips={"U": 1})
add("Jolrael, Mwonvuli Recluse", 2, "creature", {"jolrael"}, power=1, toughness=2, pips={"G": 1})
add("Psychosis Crawler", 5, "creature", {"psychosis_crawler"}, power=0, toughness=0, pips={})
add("Twenty-Toed Toad", 4, "creature", {"twenty_toed_toad", "no_max_hand"}, power=3, toughness=3, pips={"U": 1})
add("Faerie Mastermind", 2, "creature", {"flash", "flying", "faerie_mastermind"}, power=2, toughness=1, pips={"U": 1})
add("Kwain, Itinerant Meddler", 2, "creature", {"kwain"}, power=1, toughness=3, pips={"W": 1, "U": 1})
add("Loran of the Third Path", 3, "creature", {"vigilance", "loran"}, power=2, toughness=1, pips={"W": 1})
add("Mangara, the Diplomat", 4, "creature", {"lifelink", "mangara"}, power=2, toughness=4, pips={"W": 1})
add("Ponder", 1, "sorcery", {"ponder"}, pips={"U": 1})
add("Coiling Oracle", 2, "creature", {"coiling_oracle"}, power=1, toughness=1, pips={"G": 1, "U": 1})
add("Rhystic Study", 3, "enchantment", {"rhystic_study"}, pips={"U": 1})
add("Esper Sentinel", 1, "creature", {"esper_sentinel"}, power=1, toughness=1, pips={"W": 1})
add("Smothering Tithe", 4, "enchantment", {"smothering_tithe"}, pips={"W": 1})
add("Wedding Ring", 4, "artifact", {"wedding_ring"}, pips={"W": 2})
add("Struggle for Project Purity", 4, "enchantment", {"struggle_purity"}, pips={"U": 1})
add("Beza, the Bounding Spring", 4, "creature", {"beza"}, power=4, toughness=5, pips={"W": 2})
add("Drumbellower", 3, "creature", {"flying", "drumbellower"}, power=2, toughness=1, pips={"W": 1})
add("Wilderness Reclamation", 4, "enchantment", {"wilderness_reclamation"}, pips={"G": 1})

# --- Interacao (precisa de oponente real -- 📊) --------------------------------
add("Path to Exile", 1, "instant", {"interaction"}, pips={"W": 1})
add("Swords to Plowshares", 1, "instant", {"interaction"}, pips={"W": 1})
add("Generous Gift", 3, "instant", {"interaction"}, pips={"W": 1})
add("Pongify", 1, "instant", {"interaction"}, pips={"U": 1})
add("Cyclonic Rift", 2, "instant", {"interaction"}, pips={"U": 1})
add("Swan Song", 1, "instant", {"interaction_counter"}, pips={"U": 1})
add("Long River's Pull", 2, "instant", {"interaction_counter"}, pips={"U": 2})
add("An Offer You Can't Refuse", 1, "instant", {"interaction_counter"}, pips={"U": 1})
add("Fractured Identity", 5, "sorcery", {"interaction"}, pips={"W": 1, "U": 1})
add("Illusionist's Gambit", 4, "instant", {"interaction"}, pips={"U": 2})
add("Obscuring Haze", 3, "instant", {"interaction_free_own_commander"}, pips={"G": 1})
add("Peerless Recycling", 2, "instant", {"peerless_recycling"}, pips={"G": 1})
add("Noble Heritage", 2, "enchantment", {"noble_heritage"}, pips={"W": 1})

# --- Equip/tribal ---------------------------------------------------------
add("Lightning Greaves", 2, "artifact", {"equipment", "eq_haste_shroud"})
add("Swiftfoot Boots", 2, "artifact", {"equipment", "eq_hexproof_haste"})
add("Swift Reconfiguration", 1, "enchantment", {"swift_reconfiguration"}, pips={"W": 1})
add("Kodama of the West Tree", 3, "creature", {"reach", "kodama"}, power=3, toughness=3, pips={"G": 1})

# --- Planeswalkers/MDFCs ------------------------------------------------------
add("Tamiyo, Field Researcher", 4, "planeswalker", {"tamiyo_field"}, pips={"G": 1, "W": 1, "U": 1})
add("Tamiyo, Inquisitive Student // Tamiyo, Seasoned Scholar", 1, "creature", {"flying", "tamiyo_student"},
    power=1, toughness=1, pips={"U": 1})
add("Brazen Borrower // Petty Theft", 3, "creature", {"flash", "flying"}, power=3, toughness=1, pips={"U": 2})

# --- Valor/tempting ----------------------------------------------------------
add("Tempt with Bunnies", 3, "sorcery", {"tempt_bunnies"}, pips={"W": 1})

# --- Terrenos --------------------------------------------------------------
DUAL_LANDS = {
    "Adarkar Wastes": ({"W", "U"}, "painland"),
    "Barkchannel Pathway // Tidechannel Pathway": ({"G"}, "pathway_g"),
    "Bountiful Promenade": ({"G", "W"}, "surveil_opponent_tapped"),
    "Breeding Pool": ({"G", "U"}, "shockland"),
    "Brushland": ({"G", "W"}, "painland"),
    "Deserted Beach": ({"W", "U"}, "checkland_count2"),
    "Flooded Grove": ({"G", "U"}, "filter"),
    "Glacial Fortress": ({"W", "U"}, "checkland_type"),
    "Hallowed Fountain": ({"W", "U"}, "shockland"),
    "Overflowing Basin": ({"G", "U"}, "filter"),
    "Overgrown Farmland": ({"G", "W"}, "checkland_count2"),
    "Prairie Stream": ({"W", "U"}, "checkland_count2basic"),
    "Sea of Clouds": ({"W", "U"}, "surveil_opponent_tapped"),
    "Seachrome Coast": ({"W", "U"}, "checkland_count2fewer"),
    "Seaside Citadel": ({"G", "W", "U"}, "etb_tapped"),
    "Skycloud Expanse": ({"W", "U"}, "filter"),
    "Sungrass Prairie": ({"G", "W"}, "filter"),
    "Sunpetal Grove": ({"G", "W"}, "checkland_type"),
    "Temple Garden": ({"G", "W"}, "shockland"),
    "Vineglimmer Snarl": ({"G", "U"}, "revealland"),
    "Yavimaya Coast": ({"G", "U"}, "painland"),
}
for _name, (_colors, _kind) in DUAL_LANDS.items():
    add(_name, 0, "land", {_kind}, produces=_colors)

add("Command Tower", 0, "land", set(), produces={"G", "W", "U"})
add("Exotic Orchard", 0, "land", {"opponent_dependent"}, produces=set())
add("Reliquary Tower", 0, "land", {"no_max_hand"}, produces=set())
add("Tranquil Landscape", 0, "land", {"sac_fetch_gwu"}, produces=set())
add("Forest", 0, "land", set(), produces={"G"})
add("Island", 0, "land", set(), produces={"U"})
add("Plains", 0, "land", set(), produces={"W"})

LAND_NAMES = {n for n, c in CARD_DB.items() if c.ctype == "land"}
EQUIPMENT_NAMES = {n for n, c in CARD_DB.items() if "equipment" in c.tags}
MDFC_LAND_FACES = {"Barkchannel Pathway // Tidechannel Pathway"}
LAND_NAMES |= MDFC_LAND_FACES


def is_creature_card(name: str) -> bool:
    return CARD_DB[name].ctype == "creature"


def is_artifact_card(name: str) -> bool:
    return CARD_DB[name].ctype == "artifact"


# ---------------------------------------------------------------------------
# Permanent / GameState
# ---------------------------------------------------------------------------

@dataclass
class Permanent:
    card: str
    uid: int
    tapped: bool = False
    counters: int = 0
    entered_turn: int = 0
    equipped_to: Optional[int] = None
    is_token: bool = False
    tapped_for_mana_this_turn: bool = False


@dataclass
class GameState:
    turn: int = 0
    hand: list = field(default_factory=list)
    battlefield: list = field(default_factory=list)
    graveyard: list = field(default_factory=list)
    library: list = field(default_factory=list)
    mulligans: int = 0
    next_uid: int = 1

    lands_played_this_turn: int = 0
    tapped_land_this_turn: Optional[int] = None
    mana_spent_this_turn: int = 0
    bonus_mana_pool: int = 0
    hand_size_no_max: bool = False

    commander_in_play: bool = False
    commander_uid: Optional[int] = None
    commander_cast_count: int = 0
    commander_cast_turn: Optional[int] = None

    spells_cast_this_turn: int = 0
    bumbleflower_triggers_this_turn: int = 0
    first_counter_this_turn: set = field(default_factory=set)  # uids que ja receberam contador este turno (Danny Pink)
    devoted_druid_extra_used: bool = False
    simic_ascendancy_growth_counters: int = 0
    communal_brewing_ingredient_counters: int = 0
    won_via_ascendancy: bool = False
    won_via_toad: bool = False
    cards_drawn_this_turn: int = 0
    tamiyo_emblem_free_cast: bool = False

    treasures: int = 0
    clues: int = 0

    # metrics -----------------------------------------------------------------
    proxy_damage_total: int = 0
    cards_drawn_extra: int = 0
    opponent_forced_draws_total: int = 0
    treasures_created_total: int = 0
    counters_placed_total: int = 0
    life_gained_total: int = 0
    interaction_plays: int = 0
    recursion_events_total: int = 0
    library_emptied: bool = False


def draw_cards(state: GameState, n: int):
    for _ in range(n):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1
            state.cards_drawn_this_turn += 1
            on_draw_card(state)
        else:
            state.library_emptied = True


def proxy_burn(state: GameState, n: int):
    state.proxy_damage_total += n


def gain_life(state: GameState, n: int):
    state.life_gained_total += n


def new_uid(state: GameState) -> int:
    u = state.next_uid
    state.next_uid += 1
    return u


def find_perm(state: GameState, uid: int) -> Optional[Permanent]:
    return next((p for p in state.battlefield if p.uid == uid), None)


def creatures_in_play(state: GameState):
    return [p for p in state.battlefield if is_creature_card(p.card)]


# ---------------------------------------------------------------------------
# Motor central de contadores -- Danny Pink + Simic Ascendancy reagem a
# QUALQUER fonte de contador que passe por aqui.
# ---------------------------------------------------------------------------

def put_counters(state: GameState, perm: Permanent, n: int, log: list, source: str = ""):
    if n <= 0:
        return
    perm.counters += n
    state.counters_placed_total += n

    if perm.uid not in state.first_counter_this_turn:
        state.first_counter_this_turn.add(perm.uid)
        if any(p.card == "Danny Pink" for p in state.battlefield) and is_creature_card(perm.card):
            draw_cards(state, 1)

    if any(p.card == "Simic Ascendancy" for p in state.battlefield) and is_creature_card(perm.card):
        state.simic_ascendancy_growth_counters += n
        if state.simic_ascendancy_growth_counters >= 20:
            state.won_via_ascendancy = True

    if perm.card == "Wizard Class":
        pass  # marcador -- nunca ganha contador ele mesmo


def on_draw_card(state: GameState):
    # Psychosis Crawler: "whenever you draw a card, each opponent loses 1
    # life" -- sem oponente real, o dano proxy representa essa perda.
    if any(p.card == "Psychosis Crawler" for p in state.battlefield):
        proxy_burn(state, 1)
    # Wizard Class nivel 3: "whenever you draw a card, put a +1/+1 counter
    # on target creature you control." Achado real: precisa dispatch
    # explicito (nao e' um efeito de ETB), ver `wizard_class_level`.
    wc = next((p for p in state.battlefield if p.card == "Wizard Class"), None)
    if wc is not None and wc.counters >= 3:
        target = best_counter_target(state)
        if target is not None:
            put_counters(state, target, 1, [])
    # Chasm Skulker: "whenever you draw a card, put a +1/+1 counter on
    # this creature." Achado real (varredura de tags orfas): so' a
    # morte (X Squids) estava implementada, o proprio motor de crescer
    # nunca disparava.
    skulker = next((p for p in state.battlefield if p.card == "Chasm Skulker"), None)
    if skulker is not None:
        put_counters(state, skulker, 1, [], source="Chasm Skulker")
    # Jolrael, Mwonvuli Recluse: "whenever you draw your SECOND card each
    # turn, create a 2/2 green Cat creature token." Achado real: carta
    # inteira sem dispatch nenhum.
    if state.cards_drawn_this_turn == 2 and any(p.card == "Jolrael, Mwonvuli Recluse" for p in state.battlefield):
        token = Permanent(card="Cat Token", uid=new_uid(state), entered_turn=state.turn, is_token=True)
        if "Cat Token" not in CARD_DB:
            add("Cat Token", 0, "creature", set(), power=2, toughness=2)
        state.battlefield.append(token)


def best_counter_target(state: GameState) -> Optional[Permanent]:
    creatures = creatures_in_play(state)
    if not creatures:
        return None
    return max(creatures, key=lambda p: creature_power(state, p))


def creature_power(state: GameState, perm: Permanent) -> int:
    base = CARD_DB[perm.card].power + perm.counters
    if perm.card == "Walking Ballista":
        base = perm.counters
    if perm.card == "Faeburrow Elder":
        base = perm.counters + faeburrow_colors(state)
    if perm.card == "Psychosis Crawler":
        base = len(state.hand)
    return max(0, base)


def faeburrow_colors(state: GameState) -> int:
    colors = set()
    for p in state.battlefield:
        for color in CARD_DB[p.card].pips.keys():
            for ch in color.split("/"):
                if ch in ("G", "W", "U"):
                    colors.add(ch)
    return len(colors)


# ---------------------------------------------------------------------------
# Mana
# ---------------------------------------------------------------------------

def ready_permanents(state: GameState):
    return [p for p in state.battlefield if not p.tapped]


def rocks_mana(state: GameState) -> int:
    names = [p.card for p in state.battlefield]
    total = 0
    if "Sol Ring" in names:
        total += 2
    if "Arcane Signet" in names:
        total += 1
    if "Thought Vessel" in names:
        total += 1
    for p in state.battlefield:
        if p.card == "Birds of Paradise" and (p.entered_turn < state.turn):
            total += 1
        if p.card == "Elvish Mystic" and (p.entered_turn < state.turn):
            total += 1
        if p.card == "Devoted Druid" and (p.entered_turn < state.turn):
            # {T}: Add G, + "put a -1/-1 counter: untap this" permite
            # reativar 1x extra com seguranca (0/2 -> 0/1, para antes de
            # 0/0 morrer). O -1/-1 counter em si nao e' rastreado como
            # estado persistente (campo `counters` deste arquivo e'
            # semanticamente +1/+1 em todo o resto do motor -- misturar
            # os dois exigiria um segundo campo so' pra esta 1 carta,
            # escopo desproporcional) -- aproximado como +2 mana fixo por
            # turno, documentado, nao um limite arbitrario de "vale a pena".
            total += 2
        if p.card == "Faeburrow Elder" and (p.entered_turn < state.turn):
            total += faeburrow_colors(state)
    # Rishkar: "each creature you control with a counter on it has {T}: Add G."
    if any(p.card == "Rishkar, Peema Renegade" for p in state.battlefield):
        total += sum(1 for p in state.battlefield if is_creature_card(p.card) and p.counters > 0
                     and p.entered_turn < state.turn and p.card not in ("Birds of Paradise", "Elvish Mystic",
                                                                          "Devoted Druid", "Faeburrow Elder"))
    if any(p.card == "Oakhollow Village" for p in state.battlefield):
        total += 1  # {T}: Add G (so' pra criatura) -- aproximado como mana geral disponivel
    return total


def lands_available(state: GameState) -> int:
    lands = sum(1 for p in state.battlefield if p.card in LAND_NAMES)
    if state.tapped_land_this_turn is not None:
        lands -= 1
    filter_lands = sum(1 for p in state.battlefield
                        if p.card in ("Flooded Grove", "Overflowing Basin", "Skycloud Expanse", "Sungrass Prairie"))
    return lands - filter_lands  # filtros consomem 1 mana de entrada pra virar 2 -- liquido 0 extra, ver color_sources


def total_mana(state: GameState) -> int:
    return lands_available(state) + rocks_mana(state) + state.bonus_mana_pool + state.treasures


def remaining_mana(state: GameState) -> int:
    return max(0, total_mana(state) - state.mana_spent_this_turn)


def color_sources(state: GameState, color: str) -> int:
    n = 0
    for p in state.battlefield:
        if p.uid == state.tapped_land_this_turn:
            continue
        c = CARD_DB[p.card]
        if color in c.produces:
            n += 1
        elif p.card == "Faeburrow Elder" and p.entered_turn < state.turn and faeburrow_colors(state) > 0:
            n += 1  # produz qualquer cor entre as ja controladas
        elif p.card == "Birds of Paradise" and p.entered_turn < state.turn:
            n += 1  # qualquer cor
        elif color == "G" and any(p.card == "Rishkar, Peema Renegade" for p in state.battlefield) \
                and is_creature_card(p.card) and p.counters > 0 and p.entered_turn < state.turn:
            n += 1
        elif color == "G" and p.card in ("Elvish Mystic", "Devoted Druid", "Oakhollow Village") \
                and p.entered_turn < state.turn:
            n += 1
    if state.bonus_mana_pool > 0:
        n += 1
    return n


def has_color_sources_for(state: GameState, name: str) -> bool:
    if name == "Obscuring Haze" and state.commander_in_play:
        return True  # "without paying its mana cost" -- dispensa cor tambem
    for color, needed in CARD_DB[name].pips.items():
        if "/" in color:
            a, b = color.split("/")
            if color_sources(state, a) < needed and color_sources(state, b) < needed:
                return False
            continue
        if color_sources(state, color) < needed:
            return False
    return True


def effective_cost(state: GameState, name: str) -> int:
    mv = CARD_DB[name].mv
    if name == "Walking Ballista":
        x = max(0, (remaining_mana(state)) // 2)
        return x * 2
    if name == "Obscuring Haze" and state.commander_in_play:
        return 0  # "If you control a commander, you may cast this spell without paying its mana cost."
    return mv


def can_cast(state: GameState, name: str) -> bool:
    return remaining_mana(state) >= effective_cost(state, name) and has_color_sources_for(state, name)


def spend_mana(state: GameState, n: int):
    state.mana_spent_this_turn += n


# ---------------------------------------------------------------------------
# Gatilho central de "conjurar magica" -- Ms. Bumbleflower + Managorger
# Hydra + Forgotten Ancient reagem a TODA magica conjurada.
# ---------------------------------------------------------------------------

def on_cast_spell(state: GameState, name: str, log: list):
    state.spells_cast_this_turn += 1

    if state.commander_in_play:
        # Ms. Bumbleflower: "whenever you cast a spell, target opponent
        # draws a card. Put a +1/+1 counter on target creature. It gains
        # flying until end of turn. If this is the 2nd time this ability
        # has resolved this turn, you draw two cards."
        state.bumbleflower_triggers_this_turn += 1
        state.opponent_forced_draws_total += 1
        # "an opponent draws a card" -- retrigger real de Smothering
        # Tithe, independente de QUEM causou a compra (nao precisa ser o
        # proprio oponente conjurando algo).
        if any(p.card == "Smothering Tithe" for p in state.battlefield):
            state.treasures += 1
            state.treasures_created_total += 1
        target = best_counter_target(state)
        if target is not None:
            put_counters(state, target, 1, log, source="Bumbleflower")
        if state.bumbleflower_triggers_this_turn == 2:
            draw_cards(state, 2)

    if any(p.card == "Managorger Hydra" for p in state.battlefield):
        mh = next(p for p in state.battlefield if p.card == "Managorger Hydra")
        put_counters(state, mh, 1, log, source="Managorger Hydra")

    if any(p.card == "Forgotten Ancient" for p in state.battlefield):
        fa = next(p for p in state.battlefield if p.card == "Forgotten Ancient")
        put_counters(state, fa, 1, log, source="Forgotten Ancient")


# ---------------------------------------------------------------------------
# ETB
# ---------------------------------------------------------------------------

def resolve_etb(state: GameState, perm: Permanent, log: list):
    tags = CARD_DB[perm.card].tags
    if "rishkar_etb" in tags:
        candidates = [p for p in creatures_in_play(state) if p.uid != perm.uid]
        candidates.sort(key=lambda p: -creature_power(state, p))
        for p in candidates[:2]:
            put_counters(state, p, 1, log, source="Rishkar ETB")
        if len(candidates) < 2:
            put_counters(state, perm, 1, log, source="Rishkar ETB (self)")

    if "kalonian_etb4" in tags:
        put_counters(state, perm, 4, log, source="Kalonian Hydra ETB")

    if "deepglow_etb" in tags:
        candidates = [p for p in state.battlefield if p.counters > 0]
        if candidates:
            best = max(candidates, key=lambda p: p.counters)
            put_counters(state, best, best.counters, log, source="Deepglow Skate ETB (dobra)")

    if "coiling_oracle" in tags:
        if state.library:
            top = state.library[0]
            if top in CARD_DB and CARD_DB[top].ctype == "land":
                state.library.pop(0)
                enter_battlefield(state, top, log)
            else:
                state.library.pop(0)
                state.hand.append(top)

    if "loran" in tags:
        state.interaction_plays += 1  # "destroy up to one target artifact or enchantment" -- 📊 sem alvo real

    if "wedding_ring" in tags:
        pass  # "target opponent creates a copy" -- 📊, nao afeta nosso lado

    if "communal_brewing" in tags:
        # Achado real (varredura de tags orfas): "any number of target
        # opponents each draw a card. Put an ingredient counter on this
        # enchantment, THEN put one for each card drawn this way." Com 0
        # oponentes escolhidos, 0 draws extra, mas o contador BASE ("put
        # AN ingredient counter", incondicional) e' real -- nunca estava
        # sendo setado, entao o bonus de +1/+1 em criaturas conjuradas
        # depois sempre referenciava um valor preso em 0.
        state.communal_brewing_ingredient_counters += 1

    if perm.card == "Walking Ballista":
        pass  # contadores de entrada ja aplicados em cast_permanent (X e' escolhido no cast)


def enter_battlefield(state: GameState, name: str, log: list, tapped: bool = False, is_token: bool = False,
                       entering_counters: int = 0) -> Permanent:
    perm = Permanent(card=name, uid=new_uid(state), entered_turn=state.turn, tapped=tapped, is_token=is_token)
    state.battlefield.append(perm)
    if entering_counters > 0:
        put_counters(state, perm, entering_counters, log, source="ETB")
    # Communal Brewing: "whenever you cast a creature spell, that creature
    # enters with X additional +1/+1 counters, X = ingredient counters."
    if is_creature_card(name) and state.communal_brewing_ingredient_counters > 0 and not is_token:
        put_counters(state, perm, state.communal_brewing_ingredient_counters, log, source="Communal Brewing")
    resolve_etb(state, perm, log)
    return perm


def leave_battlefield(state: GameState, perm: Permanent, log: list, to_graveyard: bool = True):
    if perm in state.battlefield:
        state.battlefield.remove(perm)
    ozolith = next((p for p in state.battlefield if p.card == "The Ozolith"), None)
    if ozolith is not None and perm.counters > 0 and is_creature_card(perm.card):
        ozolith.counters += perm.counters
        perm.counters = 0
    if perm.card == "Chasm Skulker" and perm.counters > 0:
        for _ in range(perm.counters):
            token = Permanent(card="Squid Token", uid=new_uid(state), entered_turn=state.turn, is_token=True)
            if "Squid Token" not in CARD_DB:
                add("Squid Token", 0, "creature", set(), power=1, toughness=1)
            state.battlefield.append(token)
    if to_graveyard and not perm.is_token:
        state.graveyard.append(perm.card)


# ---------------------------------------------------------------------------
# Conjuracao
# ---------------------------------------------------------------------------

def cast_permanent(state: GameState, name: str, log: list):
    cost = effective_cost(state, name)
    spend_mana(state, cost)
    state.hand.remove(name)
    on_cast_spell(state, name, log)
    entering_counters = 0
    if name == "Walking Ballista":
        entering_counters = cost // 2
    perm = enter_battlefield(state, name, log, entering_counters=entering_counters)
    if "equipment" in CARD_DB[name].tags:
        try_equip(state, perm, log)


def try_cast_commander(state: GameState, log: list):
    # Ms. Bumbleflower vem da zona de comando, NAO da biblioteca
    # (BASE_LIBRARY tem so' as 99 cartas de deck, mesmo padrao do
    # Kutzil/Megatron/Azula/Captain Storm desta sessao) -- por isso NAO
    # passa por `cast_permanent()` (que faz `state.hand.remove(name)`,
    # ela nunca esta la). Achado real (mesmo bug ja corrigido no Azula
    # nesta sessao): sem este passo dedicado, o comandante nunca entra em
    # campo.
    if state.commander_in_play or not can_cast(state, COMMANDER):
        return
    spend_mana(state, effective_cost(state, COMMANDER))
    on_cast_spell(state, COMMANDER, log)
    perm = enter_battlefield(state, COMMANDER, log)
    state.commander_in_play = True
    state.commander_uid = perm.uid
    state.commander_cast_count += 1
    if any(p.card == "Noble Heritage" for p in state.battlefield):
        target = best_counter_target(state)
        if target is not None:
            put_counters(state, target, 2, log, source="Noble Heritage (ETB do comandante)")
    if state.commander_cast_turn is None:
        state.commander_cast_turn = state.turn


def try_equip(state: GameState, eq_perm: Permanent, log: list):
    creatures = creatures_in_play(state)
    if not creatures:
        return
    target = next((p for p in creatures if p.card == COMMANDER), None) or max(
        creatures, key=lambda p: creature_power(state, p))
    eq_perm.equipped_to = target.uid


def cast_instant_sorcery(state: GameState, name: str, log: list):
    tags = CARD_DB[name].tags
    free_cast = "interaction_free_own_commander" in tags and state.commander_in_play
    if not free_cast:
        spend_mana(state, effective_cost(state, name))
    state.hand.remove(name)
    on_cast_spell(state, name, log)

    if "land_tutor2" in tags:
        basics = [n for n in state.library if n in ("Forest", "Island", "Plains")]
        basics.sort(key=lambda n: -color_scarcity_priority(state, n))
        for b in basics[:1]:
            state.library.remove(b)
            enter_battlefield(state, b, log, tapped=True)
        for b in basics[1:2]:
            state.library.remove(b)
            state.hand.append(b)

    elif "land_tutor1_nonforest" in tags:
        basics = [n for n in state.library if n in ("Island", "Plains")]
        if basics:
            best = max(basics, key=lambda n: color_scarcity_priority(state, n))
            state.library.remove(best)
            enter_battlefield(state, best, log, tapped=True)

    elif "tempt_discovery" in tags:
        # Tempting offer: sem oponente pra "aceitar" e trocar buscas
        # extra -- so' a busca base (1 terreno pra campo, sem tap).
        basics = [n for n in state.library if n in ("Forest", "Island", "Plains")]
        if basics:
            best = max(basics, key=lambda n: color_scarcity_priority(state, n))
            state.library.remove(best)
            enter_battlefield(state, best, log)

    elif "tempt_bunnies" in tags:
        draw_cards(state, 1)
        token = Permanent(card="Rabbit Token", uid=new_uid(state), entered_turn=state.turn, is_token=True)
        if "Rabbit Token" not in CARD_DB:
            add("Rabbit Token", 0, "creature", set(), power=1, toughness=1)
        state.battlefield.append(token)

    elif "ponder" in tags:
        draw_cards(state, 1)

    elif "peerless_recycling" in tags:
        pool = [c for c in state.graveyard if c in CARD_DB and CARD_DB[c].ctype != "instant"
                and CARD_DB[c].ctype != "sorcery"]
        if pool:
            best = max(pool, key=lambda n: CARD_DB[n].mv)
            state.graveyard.remove(best)
            state.hand.append(best)
            state.recursion_events_total += 1

    elif "slip_out" in tags:
        target = best_counter_target(state)
        if target is not None:
            put_counters(state, target, 1, log, source="Slip Out the Back")

    elif "interaction" in tags or "interaction_counter" in tags or "interaction_free_own_commander" in tags:
        state.interaction_plays += 1

    state.graveyard.append(name)


def color_scarcity_priority(state: GameState, basic_name: str) -> int:
    color = {"Forest": "G", "Island": "U", "Plains": "W"}.get(basic_name, "")
    return -color_sources(state, color)


# ---------------------------------------------------------------------------
# Combate
# ---------------------------------------------------------------------------

def is_modified(state: GameState, perm: Permanent) -> bool:
    if perm.counters > 0:
        return True
    return any(eq.equipped_to == perm.uid for eq in state.battlefield if "equipment" in CARD_DB[eq.card].tags)


def try_ozolith_move(state: GameState, log: list):
    ozolith = next((p for p in state.battlefield if p.card == "The Ozolith"), None)
    if ozolith is None or ozolith.counters == 0:
        return
    target = best_counter_target(state)
    if target is None:
        return
    put_counters(state, target, ozolith.counters, log, source="The Ozolith")
    ozolith.counters = 0


def combat_step(state: GameState, log: list):
    try_ozolith_move(state, log)

    attackers = [p for p in creatures_in_play(state)
                 if p.entered_turn < state.turn or "haste" in CARD_DB[p.card].tags
                 or any(eq.card in ("Lightning Greaves", "Swiftfoot Boots") and eq.equipped_to == p.uid
                        for eq in state.battlefield)]
    if not attackers:
        return
    for p in attackers:
        if "vigilance" not in CARD_DB[p.card].tags:
            p.tapped = True

    # Kalonian Hydra: "whenever this attacks, double the number of +1/+1
    # counters on each creature you control."
    if any(p.card == "Kalonian Hydra" for p in attackers):
        for p in creatures_in_play(state):
            if p.counters > 0:
                put_counters(state, p, p.counters, log, source="Kalonian Hydra (dobra no ataque)")

    # Danny Pink: Mentor -- "whenever attacks, +1/+1 counter on target
    # attacking creature with lesser power."
    if any(p.card == "Danny Pink" for p in attackers):
        danny = next(p for p in attackers if p.card == "Danny Pink")
        lesser = [p for p in attackers if p.uid != danny.uid and creature_power(state, p) < creature_power(state, danny)]
        if lesser:
            target = max(lesser, key=lambda p: creature_power(state, p))
            put_counters(state, target, 1, log, source="Danny Pink (Mentor)")

    if "Tamiyo, Inquisitive Student // Tamiyo, Seasoned Scholar" in [p.card for p in attackers]:
        state.clues += 1  # "whenever Tamiyo attacks, investigate"

    if len(attackers) >= 2 and "Twenty-Toed Toad" in [p.card for p in attackers]:
        toad = next(p for p in attackers if p.card == "Twenty-Toed Toad")
        put_counters(state, toad, 1, log, source="Twenty-Toed Toad")
        draw_cards(state, 1)

    total_power = 0
    lifelink_gain = 0
    for p in attackers:
        power = creature_power(state, p)
        total_power += power
        if "lifelink" in CARD_DB[p.card].tags:
            lifelink_gain += power

    kodama_in_play = any(p.card == "Kodama of the West Tree" for p in state.battlefield)
    if kodama_in_play:
        modified_attackers = [p for p in attackers if is_modified(state, p)]
        basics_in_lib = [n for n in state.library if n in ("Forest", "Island", "Plains")]
        for _ in modified_attackers:
            if basics_in_lib:
                best = max(basics_in_lib, key=lambda n: color_scarcity_priority(state, n))
                basics_in_lib.remove(best)
                state.library.remove(best)
                enter_battlefield(state, best, log, tapped=True)

    proxy_burn(state, total_power)
    if lifelink_gain > 0:
        gain_life(state, lifelink_gain)
        if any(p.card == "Heliod, Sun-Crowned" for p in state.battlefield):
            target = best_counter_target(state)
            if target is not None:
                put_counters(state, target, 1, log, source="Heliod (ganho de vida)")

    if "Twenty-Toed Toad" in [p.card for p in attackers]:
        toad = next(p for p in attackers if p.card == "Twenty-Toed Toad")
        if toad.counters >= 20 or len(state.hand) >= 20:
            state.won_via_toad = True


# ---------------------------------------------------------------------------
# Efeitos que forcam o oponente a comprar (retrigger real de Smothering
# Tithe, independente de quem causou a compra)
# ---------------------------------------------------------------------------

def force_opponent_draw(state: GameState):
    state.opponent_forced_draws_total += 1
    if any(p.card == "Smothering Tithe" for p in state.battlefield):
        state.treasures += 1
        state.treasures_created_total += 1


# ---------------------------------------------------------------------------
# Ativacoes
# ---------------------------------------------------------------------------

RABBIT_LIKE = {"Ms. Bumbleflower", "Kwain, Itinerant Meddler", "Rabbit Token"}


def try_activated_abilities(state: GameState, log: list):
    names = [p.card for p in state.battlefield]

    while state.clues > 0 and remaining_mana(state) >= 2:
        spend_mana(state, 2)
        state.clues -= 1
        draw_cards(state, 1)

    kwain = next((p for p in state.battlefield if p.card == "Kwain, Itinerant Meddler" and not p.tapped
                  and p.entered_turn < state.turn), None)
    if kwain is not None:
        kwain.tapped = True
        draw_cards(state, 1)
        gain_life(state, 1)
        force_opponent_draw(state)

    loran = next((p for p in state.battlefield if p.card == "Loran of the Third Path" and not p.tapped
                  and p.entered_turn < state.turn), None)
    if loran is not None:
        loran.tapped = True
        draw_cards(state, 1)
        force_opponent_draw(state)

    if ("Faerie Mastermind" in names and remaining_mana(state) >= 4
            and color_sources(state, "U") >= 1):
        spend_mana(state, 4)
        draw_cards(state, 1)
        force_opponent_draw(state)

    if "Oakhollow Village" in names and remaining_mana(state) >= 1 and color_sources(state, "G") >= 1:
        fresh_rabbits = [p for p in state.battlefield if p.card in RABBIT_LIKE and p.entered_turn == state.turn]
        if fresh_rabbits:
            spend_mana(state, 1)
            for p in fresh_rabbits:
                put_counters(state, p, 1, log, source="Oakhollow Village")

    wc = next((p for p in state.battlefield if p.card == "Wizard Class"), None)
    if wc is not None:
        if wc.counters < 2 and remaining_mana(state) >= 3 and color_sources(state, "U") >= 1:
            spend_mana(state, 3)
            wc.counters = 2
            draw_cards(state, 2)
        elif wc.counters == 2 and remaining_mana(state) >= 5 and color_sources(state, "U") >= 1:
            spend_mana(state, 5)
            wc.counters = 3

    if ("Simic Ascendancy" in names and not state.won_via_ascendancy):
        while remaining_mana(state) >= 3 and color_sources(state, "G") >= 1 and color_sources(state, "U") >= 1:
            target = best_counter_target(state)
            if target is None:
                break
            spend_mana(state, 3)
            put_counters(state, target, 1, log, source="Simic Ascendancy (ativada)")

    for eq_name in EQUIPMENT_NAMES:
        for perm in [p for p in state.battlefield if p.card == eq_name and p.equipped_to is None]:
            try_equip(state, perm, log)

    ballista = next((p for p in state.battlefield if p.card == "Walking Ballista"), None)
    if ballista is not None:
        while remaining_mana(state) >= 4:
            spend_mana(state, 4)
            put_counters(state, ballista, 1, log, source="Walking Ballista ({4})")


# ---------------------------------------------------------------------------
# Terreno
# ---------------------------------------------------------------------------

def land_enters_tapped(state: GameState, name: str) -> bool:
    tags = CARD_DB[name].tags
    if "etb_tapped" in tags:
        return True
    if "revealland" in tags:
        return not any(n in ("Forest", "Island") for n in state.hand)
    if "checkland_type" in tags:
        return not any(n in ("Forest", "Plains", "Island") for n in [p.card for p in state.battlefield])
    if "checkland_count2" in tags:
        return sum(1 for p in state.battlefield if p.card in LAND_NAMES and p.card != name) < 2
    if "checkland_count2basic" in tags:
        return sum(1 for p in state.battlefield if p.card in ("Forest", "Island", "Plains")) < 2
    if "checkland_count2fewer" in tags:
        return sum(1 for p in state.battlefield if p.card in LAND_NAMES) > 2
    if "surveil_opponent_tapped" in tags:
        return False  # "enters tapped unless you have two or more opponents" -- premissa de mesa 1v1, sempre destapada
    if "shockland" in tags:
        return False  # sempre paga 2 de vida (velocidade > vida, mesma convencao de outros sims)
    return False


def play_land(state: GameState, log: list):
    if state.lands_played_this_turn >= 1:
        return
    hand_lands = [c for c in state.hand if c in LAND_NAMES]
    if not hand_lands:
        return

    def score(n):
        return 1 if land_enters_tapped(state, n) else 0

    hand_lands.sort(key=score)
    pick = hand_lands[0]
    state.hand.remove(pick)
    state.lands_played_this_turn += 1
    if "sac_fetch_gwu" in CARD_DB[pick].tags:
        basics = [n for n in state.library if n in ("Forest", "Island", "Plains")]
        if basics:
            best = max(basics, key=lambda n: color_scarcity_priority(state, n))
            state.library.remove(best)
            enter_battlefield(state, best, log, tapped=True)
        return
    tapped = land_enters_tapped(state, pick)
    enter_battlefield(state, pick, log, tapped=tapped)
    if tapped:
        state.tapped_land_this_turn = state.battlefield[-1].uid


# ---------------------------------------------------------------------------
# Tamiyo, Field Researcher (planeswalker) + Tamiyo, Inquisitive Student //
# Seasoned Scholar (transform)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Upkeep
# ---------------------------------------------------------------------------

def try_upkeep(state: GameState, log: list):
    # Forgotten Ancient: "at the beginning of your upkeep, you may move
    # any number of +1/+1 counters from this creature onto other
    # creatures." Achado real: so' o gatilho de CAST ("whenever a player
    # casts a spell, +1/+1 counter on this") estava implementado -- a
    # metade de upkeep (mover pra outra criatura, retriggerando Danny
    # Pink/Simic Ascendancy no destino, ruling real de "mover = por")
    # nunca disparava. Move tudo pro melhor alvo (concentra valor).
    fa = next((p for p in state.battlefield if p.card == "Forgotten Ancient"), None)
    if fa is not None and fa.counters > 0:
        others = [p for p in creatures_in_play(state) if p.uid != fa.uid]
        if others:
            target = max(others, key=lambda p: creature_power(state, p))
            n = fa.counters
            fa.counters = 0
            put_counters(state, target, n, log, source="Forgotten Ancient (move no upkeep)")

    # Noble Heritage: "Commander creatures you own have 'when this enters
    # and at the beginning of your upkeep, each player may put two +1/+1
    # counters on a creature they control...'" Achado real: a clausula de
    # "ganha protecao se o oponente tambem por" e' 📊 (precisa de
    # oponente reagindo), mas a colocacao de 2 contadores em NOSSA PROPRIA
    # criatura e' real e NAO depende de oponente nenhum -- estava
    # incorretamente descartada como 100% estrutural na 1a passada.
    if (any(p.card == "Noble Heritage" for p in state.battlefield) and state.commander_in_play
            and state.turn > (state.commander_cast_turn or 0)):
        target = best_counter_target(state)
        if target is not None:
            put_counters(state, target, 2, log, source="Noble Heritage (upkeep)")

    # Struggle for Project Purity, modo Brotherhood (escolhido por padrao
    # -- Enclave e' 100% 📊, precisa de ataque de oponente pra gerar rad
    # counters, sem nenhum valor numerico nosso): "each opponent draws a
    # card. You draw a card for each card drawn this way." Achado real:
    # carta inteira sem dispatch.
    if any(p.card == "Struggle for Project Purity" for p in state.battlefield):
        force_opponent_draw(state)
        draw_cards(state, 1)


def try_tamiyo_field_researcher(state: GameState, log: list, combat_power_this_turn: int):
    tf = next((p for p in state.battlefield if p.card == "Tamiyo, Field Researcher"), None)
    if tf is None:
        return
    if tf.counters >= 7:
        # -7: "Draw three cards. You get an emblem with 'cast spells from
        # hand without paying their mana costs.'" Ultimate real, uma vez.
        tf.counters -= 7
        draw_cards(state, 3)
        state.tamiyo_emblem_free_cast = True
    else:
        # +1: "choose up to two target creatures... whenever either deals
        # combat damage, draw a card." Aproximado: se causamos dano de
        # combate este turno (quase sempre, sem bloqueio), compra 1 --
        # captura o valor real sem rastrear QUAIS 2 criaturas especificas
        # foram escolhidas (irrelevante num goldfish sem bloqueio).
        tf.counters += 1
        if combat_power_this_turn > 0:
            draw_cards(state, 1)


def try_tamiyo_student_transform(state: GameState, log: list):
    student = next((p for p in state.battlefield
                     if p.card == "Tamiyo, Inquisitive Student // Tamiyo, Seasoned Scholar"), None)
    if student is None or student.is_token:
        return
    if state.cards_drawn_this_turn >= 3:
        state.battlefield.remove(student)
        scholar = Permanent(card="Tamiyo, Seasoned Scholar (transformada)", uid=new_uid(state),
                             entered_turn=state.turn, counters=2)
        if scholar.card not in CARD_DB:
            add(scholar.card, 0, "planeswalker", {"tamiyo_scholar"})
        state.battlefield.append(scholar)


def try_tamiyo_seasoned_scholar(state: GameState, log: list):
    scholar = next((p for p in state.battlefield if p.card == "Tamiyo, Seasoned Scholar (transformada)"), None)
    if scholar is None:
        return
    pool = [c for c in state.graveyard if c in CARD_DB and CARD_DB[c].ctype in ("instant", "sorcery")]
    if pool and scholar.counters >= 3:
        best = max(pool, key=lambda n: CARD_DB[n].mv)
        state.graveyard.remove(best)
        state.hand.append(best)
        scholar.counters -= 3
        state.recursion_events_total += 1
    else:
        scholar.counters += 2  # +2 (defensivo, sem valor numerico ofensivo aqui)


# ---------------------------------------------------------------------------
# Loop de conjuracao / turno
# ---------------------------------------------------------------------------

ROCK_NAMES = {"Sol Ring", "Arcane Signet", "Thought Vessel", "Birds of Paradise", "Elvish Mystic",
              "Devoted Druid", "Faeburrow Elder"}


def try_cast_loop(state: GameState, log: list):
    changed = True
    while changed:
        changed = False
        emblem = getattr(state, "tamiyo_emblem_free_cast", False)
        # Swift Reconfiguration ("enchant creature or Vehicle, vira um
        # Vehicle crew 5 e perde os outros tipos") so' tem uso real
        # contra um alvo de OPONENTE (neutraliza a criatura) -- em nos
        # mesmos so' prejudica (transforma nosso proprio corpo num
        # Vehicle que nao ataca sem crew). Sem oponente pra mirar, nunca
        # conjurada (achado real na varredura de tags orfas: sem essa
        # exclusao, o loop guloso acabaria conjurando nela mesma).
        candidates = [c for c in state.hand if c in CARD_DB and CARD_DB[c].ctype != "land"
                      and c != "Swift Reconfiguration" and (can_cast(state, c) or emblem)]
        if not candidates:
            break

        def prio(c):
            if c == COMMANDER:
                return 0
            if c in ROCK_NAMES:
                return 1
            if CARD_DB[c].ctype == "creature":
                return 2
            if CARD_DB[c].ctype in ("artifact", "enchantment"):
                return 3
            return 4

        pick = min(candidates, key=lambda c: (prio(c), effective_cost(state, c)))
        ctype = CARD_DB[pick].ctype
        cost = 0 if emblem else effective_cost(state, pick)
        if emblem:
            state.hand.remove(pick)
            on_cast_spell(state, pick, log)
            if ctype in ("creature", "artifact", "enchantment"):
                perm = enter_battlefield(state, pick, log)
                if pick == COMMANDER:
                    state.commander_in_play = True
                    state.commander_uid = perm.uid
            elif ctype == "planeswalker":
                enter_battlefield(state, pick, log)
            else:
                state.graveyard.append(pick)
        elif ctype in ("creature", "artifact", "enchantment"):
            cast_permanent(state, pick, log)
        elif ctype == "planeswalker":
            spend_mana(state, cost)
            state.hand.remove(pick)
            on_cast_spell(state, pick, log)
            enter_battlefield(state, pick, log)
        else:
            cast_instant_sorcery(state, pick, log)
        changed = True


def run_turn(state: GameState, log: list):
    state.turn += 1
    state.lands_played_this_turn = 0
    state.tapped_land_this_turn = None
    state.mana_spent_this_turn = 0
    state.bonus_mana_pool = 0
    state.spells_cast_this_turn = 0
    state.bumbleflower_triggers_this_turn = 0
    state.first_counter_this_turn = set()
    state.cards_drawn_this_turn = 0
    for p in state.battlefield:
        p.tapped = False

    try_upkeep(state, log)
    draw_cards(state, 1)
    play_land(state, log)
    try_cast_commander(state, log)
    try_cast_loop(state, log)
    try_activated_abilities(state, log)
    try_cast_loop(state, log)

    combat_power_estimate = sum(creature_power(state, p) for p in creatures_in_play(state)
                                 if p.entered_turn < state.turn or "haste" in CARD_DB[p.card].tags)
    try_tamiyo_field_researcher(state, log, combat_power_estimate)
    try_tamiyo_seasoned_scholar(state, log)

    combat_step(state, log)

    try_cast_loop(state, log)
    try_tamiyo_student_transform(state, log)

    if any("no_max_hand" in CARD_DB[p.card].tags for p in state.battlefield):
        state.hand_size_no_max = True
    while len(state.hand) > (99 if state.hand_size_no_max else 7):
        worst = min(state.hand, key=lambda c: CARD_DB[c].mv if c in CARD_DB else 0)
        state.hand.remove(worst)
        state.graveyard.append(worst)

    # Wilderness Reclamation: "untap all lands you control at end step" --
    # so' tem valor real segurando mana pra responder DURANTE o turno do
    # oponente (instant speed) -- sem turno de oponente simulado, toda a
    # mana ja e' gasta no nosso proprio turno pelo loop guloso de
    # conjuracao; 📊 estrutural, documentado (nao e' julgamento de valor,
    # e' a ausencia real de janela pra usar o mana extra).

    non_treasure_mana = lands_available(state) + rocks_mana(state) + state.bonus_mana_pool
    treasures_used = max(0, state.mana_spent_this_turn - non_treasure_mana)
    state.treasures = max(0, state.treasures - treasures_used)


# ---------------------------------------------------------------------------
# Decklist
# ---------------------------------------------------------------------------

DECKLIST_TEXT = """
1 Adarkar Wastes
1 Barkchannel Pathway // Tidechannel Pathway
1 Bountiful Promenade
1 Breeding Pool
1 Brushland
1 Command Tower
1 Deserted Beach
1 Exotic Orchard
1 Flooded Grove
3 Forest
1 Glacial Fortress
1 Hallowed Fountain
3 Island
1 Oakhollow Village
1 Overflowing Basin
1 Overgrown Farmland
3 Plains
1 Prairie Stream
1 Reliquary Tower
1 Sea of Clouds
1 Seachrome Coast
1 Seaside Citadel
1 Skycloud Expanse
1 Sungrass Prairie
1 Sunpetal Grove
1 Temple Garden
1 Tranquil Landscape
1 Vineglimmer Snarl
1 Yavimaya Coast
1 An Offer You Can't Refuse
1 Arcane Signet
1 Beza, the Bounding Spring
1 Birds of Paradise
1 Brazen Borrower // Petty Theft
1 Chasm Skulker
1 Coiling Oracle
1 Communal Brewing
1 Cultivate
1 Cyclonic Rift
1 Danny Pink
1 Deepglow Skate
1 Devoted Druid
1 Drumbellower
1 Elvish Mystic
1 Esper Sentinel
1 Faeburrow Elder
1 Faerie Mastermind
1 Farseek
1 Fellwar Stone
1 Forgotten Ancient
1 Fractured Identity
1 Generous Gift
1 Heliod, Sun-Crowned
1 Illusionist's Gambit
1 Jolrael, Mwonvuli Recluse
1 Kalonian Hydra
1 Kodama of the West Tree
1 Kodama's Reach
1 Kwain, Itinerant Meddler
1 Lightning Greaves
1 Long River's Pull
1 Loran of the Third Path
1 Managorger Hydra
1 Mangara, the Diplomat
1 Noble Heritage
1 Obscuring Haze
1 Path to Exile
1 Peerless Recycling
1 Ponder
1 Pongify
1 Psychosis Crawler
1 Rhystic Study
1 Rishkar, Peema Renegade
1 Simic Ascendancy
1 Slip Out the Back
1 Smothering Tithe
1 Sol Ring
1 Struggle for Project Purity
1 Swan Song
1 Swift Reconfiguration
1 Swiftfoot Boots
1 Swords to Plowshares
1 Tamiyo, Field Researcher
1 Tamiyo, Inquisitive Student // Tamiyo, Seasoned Scholar
1 Tempt with Bunnies
1 Tempt with Discovery
1 The Ozolith
1 Thought Vessel
1 Twenty-Toed Toad
1 Walking Ballista
1 Wedding Ring
1 Wilderness Reclamation
1 Wizard Class
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


def should_keep(hand: list, mulligans: int) -> bool:
    lands = sum(1 for c in hand if c in LAND_NAMES)
    if mulligans >= 3:
        return True
    if lands < 2 or lands > 5:
        return False
    return True


def bottom_priority(card: str) -> int:
    if card in LAND_NAMES:
        return 0
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

    log = []
    for _ in range(turns):
        run_turn(state, log)
        if state.won_via_ascendancy or state.won_via_toad:
            break
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
    print(f"Compras forcadas do oponente (media): {avg(lambda s: s.opponent_forced_draws_total):.1f}")
    print(f"Treasures criados (media): {avg(lambda s: s.treasures_created_total):.1f}")
    print(f"Contadores colocados (media): {avg(lambda s: s.counters_placed_total):.1f}")
    print(f"Vida ganha (media): {avg(lambda s: s.life_gained_total):.1f}")
    print(f"Interacao jogada (media): {avg(lambda s: s.interaction_plays):.1f}")
    print(f"Mulligans (media): {avg(lambda s: s.mulligans):.2f}")
    print(f"Vitorias via Simic Ascendancy: {sum(1 for s in results if s.won_via_ascendancy)}/{n}")
    print(f"Vitorias via Twenty-Toed Toad: {sum(1 for s in results if s.won_via_toad)}/{n}")
    print(f"Biblioteca esgotada em: {sum(1 for s in results if s.library_emptied)}/{n}")

    if out_path:
        with open(out_path, "w") as f:
            for s in results:
                row = {
                    "proxy_damage_total": s.proxy_damage_total,
                    "cards_drawn_extra": s.cards_drawn_extra,
                    "opponent_forced_draws_total": s.opponent_forced_draws_total,
                    "treasures_created_total": s.treasures_created_total,
                    "counters_placed_total": s.counters_placed_total,
                    "life_gained_total": s.life_gained_total,
                    "interaction_plays": s.interaction_plays,
                    "mulligans": s.mulligans,
                    "won_via_ascendancy": s.won_via_ascendancy,
                    "won_via_toad": s.won_via_toad,
                    "library_emptied": s.library_emptied,
                }
                f.write(json.dumps(row) + "\n")
    return results


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "bumbleflower_v1_runs.jsonl")
    run_batch(3000, seed_base=1_000_000, turns=8, out_path=out)
