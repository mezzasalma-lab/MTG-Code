"""
Goldfish simulator — Captain Storm, Cosmium Raider (Izzet — U/R)

Construido do zero em 2026-09-02, terceiro dos 4 decks sem simulador
desta sessao (depois de Kutzil e Azula), mesma disciplina de "compile
TUDO": oraculo real via Scryfall (leitura linha-a-linha das 75 cartas
unicas + comandante), implementacao completa, varredura automatizada de
tags orfas no proprio rascunho antes de considerar pronto.

⚠️ Lista incompleta (documentado em `auditoria.md`, nao inventado aqui):
a lista enviada pelo usuario soma 98 cartas de biblioteca (99 com o
comandante) -- falta 1 carta pro total padrao de 100. `BASE_LIBRARY`
reflete a lista real como enviada.

======================================================================
MOTOR REAL DESTE DECK (verificado via Scryfall, nao decorado)
======================================================================
Captain Storm ({U}{R}, 2/2): "Whenever an artifact you control enters,
put a +1/+1 counter on target Pirate you control." Esse motor central
tem 3 camadas que se multiplicam entre si:

1. **Denso pacote de Treasure/Clue/Food** (12+ fontes reais, a maioria
   ETBs de criatura/artefato) -- CADA token de Treasure/Clue/Food criado
   e' ele mesmo um ARTEFATO entrando, o que retrigger a propria Captain
   Storm (+1/+1 num Pirata) de novo.
2. **Academy Manufactor** ("if you would create a Clue, Food, or
   Treasure token, instead create one of each") -- transforma UMA
   criacao de Treasure em 3 tokens simultaneos (Treasure+Clue+Food),
   CADA um retriggerando a Captain Storm separadamente (3x os contadores
   de uma unica fonte de Treasure, se Academy Manufactor em campo).
3. **Panharmonicon + Starfield Vocalist** (ambos "if a permanent
   entering causes a triggered ability of a permanent you control to
   trigger, that ability triggers an additional time") -- dobram
   QUALQUER gatilho de ETB, inclusive a propria Captain Storm e os
   proprios geradores de Treasure. Dois dobradores simultaneos
   MULTIPLICAM (nao somam) -- mesmo principio ja documentado noutros
   decks desta sessao (ex.: Roaming Throne + segunda fonte de copia no
   Beorn/Hei Bai) -- implementado como `etb_trigger_multiplier(state)`.

Arquitetura: **objetos `Permanent`** (nao lista de nomes) -- ao contrario
do Azula/Megatron, este deck precisa rastrear contadores +1/+1
PERSISTENTES (a propria habilidade da Captain Storm, ao contrario dos
pumps ate-fim-de-turno da Azula) e equipamentos anexados (qual criatura
tem qual Equipment, pra calculo de combate e gatilhos de dano de
combate). Mesmo padrao arquitetural do Kutzil/Toph.

Simplificacoes documentadas (nao inventadas -- omissoes explicitas):
- Sem oponente real: todo dano e' `proxy_damage_total` agregado, flat
  (mesma convencao da maioria dos simuladores desta sessao).
- **Encore** (Fathom Fleet Swordjack, Impulsive Pilferer) -- "for each
  OPPONENT, create a token copy that attacks" -- com 0 oponentes reais
  modelados, 0 copias, nenhum piloto racional ativaria por {3}{R}/{5}{R}
  pra gerar 0 valor -- nunca ativado neste sim, 📊 estrutural.
- **Kitesail Larcenist** -- "for each player, choose target artifact or
  creature THAT PLAYER controls" -- o uso real (transformar permanente de
  OPONENTE em Treasure) precisa de alvo de oponente -- 📊. Pode escolher
  0 alvos pra nos mesmos tambem (opcional), sem ganho real de fazer isso
  ao proprio board.
- **Fellwar Stone / Chaos Warp / contramagicas (Counterspell/Mana
  Leak/Ionize/Spell Rupture)** -- precisam de terreno/spell de oponente
  real -- 📊 `interaction_plays`.
- **Chain Reaction / Blasphemous Act** -- Regra 1 da sessao: wipe
  simetrico sem oponente modelado = so' conta como `interaction_plays`,
  sem destruir as proprias criaturas.
- **Storm Fleet Negotiator (Parley)** -- "each player reveals top card...
  each player draws" -- modelado so' pra nos mesmos (1 jogador real
  neste goldfish solo): olha o topo, cria Map se nao-terreno, compra 1.
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


COMMANDER = "Captain Storm, Cosmium Raider"
add(COMMANDER, 2, "creature", {"commander", "pirate", "storm_counter_engine"}, power=2, toughness=2,
    pips={"U": 1, "R": 1})

# --- Rampa/mana ------------------------------------------------------------
add("Arcane Signet", 2, "artifact", {"rock_identity"}, produces={"U", "R"})
add("Sol Ring", 1, "artifact", {"rock_cc"})
add("Fellwar Stone", 2, "artifact", {"rock_opponent_dependent"})
add("Izzet Signet", 2, "artifact", {"rock_filter_ur"}, produces={"U", "R"})
add("Izzet Locket", 3, "artifact", {"rock_ur", "locket_sac_draw2"}, produces={"U", "R"})
add("Lotus Petal", 0, "artifact", {"petal_sac"}, produces={"U", "R"})
add("Decanter of Endless Water", 3, "artifact", {"rock_any", "no_max_hand"}, produces={"U", "R"})
add("Bender's Waterskin", 3, "artifact", {"rock_any_untap_opp"}, produces={"U", "R"})
add("Thought Vessel", 2, "artifact", {"rock_c", "no_max_hand"})

# --- Treasure/Clue/Food (motor central, combina com Captain Storm) ---------
add("Academy Manufactor", 3, "creature", {"pirate_no", "manufactor_triple"}, power=1, toughness=3)
add("Captain Lannery Storm", 3, "creature", {"pirate", "haste", "attack_treasure", "treasure_sac_pump"},
    power=2, toughness=2, pips={"R": 1})
add("Careening Mine Cart", 3, "artifact", {"vehicle", "attack_treasure"}, power=3, toughness=3)
add("Corsair Captain", 3, "creature", {"pirate", "etb_treasure", "pirate_anthem"}, power=2, toughness=2,
    pips={"U": 1})
add("Enterprising Scallywag", 2, "creature", {"pirate", "descended_treasure_endstep"}, power=2, toughness=2,
    pips={"R": 1})
add("Impulsive Pilferer", 1, "creature", {"pirate", "death_treasure", "encore"}, power=1, toughness=1, pips={"R": 1})
add("Plundering Pirate", 3, "creature", {"pirate", "etb_treasure"}, power=3, toughness=2, pips={"R": 1})
add("Sailor of Means", 3, "creature", {"pirate", "etb_treasure"}, power=1, toughness=4, pips={"U": 1})
add("Seize the Spoils", 3, "sorcery", {"discard_cost_draw2_treasure1"}, pips={"R": 1})
add("Brass's Bounty", 7, "sorcery", {"brass_bounty"}, pips={"R": 1})
add("Storm the Vault // Vault of Catlacan", 4, "enchantment", {"storm_vault"}, pips={"U": 1, "R": 1})

# --- Piratas de valor --------------------------------------------------------
add("Captain Vargus Wrath", 2, "creature", {"pirate", "vargus_anthem_attack"}, power=1, toughness=1,
    pips={"U": 1, "R": 1})
add("Deadeye Quartermaster", 4, "creature", {"pirate", "tutor_equip_vehicle"}, power=2, toughness=2, pips={"U": 1})
add("Fathom Fleet Swordjack", 4, "creature", {"pirate", "swordjack_attack_artifacts", "encore"}, power=4,
    toughness=3, pips={"R": 1})
add("Gleaming Geardrake", 2, "creature", {"artifact_creature", "etb_clue", "sac_artifact_counter"}, power=1,
    toughness=1, pips={"U": 1, "R": 1})
add("Jackdaw", 3, "artifact", {"vehicle", "jackdaw_wheel"}, power=4, toughness=4, pips={"U": 1, "R": 1})
add("Jhoira, Ageless Innovator", 2, "creature", {"jhoira_ingenuity"}, power=2, toughness=3, pips={"U": 1, "R": 1})
add("Kitesail Larcenist", 3, "creature", {"pirate", "flying", "larcenist_etb"}, power=2, toughness=3, pips={"U": 1})
add("Malcolm, the Eyes", 2, "creature", {"pirate", "flying", "haste", "malcolm_clue"}, power=2, toughness=2,
    pips={"U": 1, "R": 1})
add("Oaken Siren", 2, "creature", {"artifact_creature", "pirate_no", "flying"}, power=1, toughness=2, pips={"U": 1})
add("Port Razer", 5, "creature", {"pirate_no", "port_razer"}, power=4, toughness=4, pips={"R": 2})
add("Spyglass Siren", 1, "creature", {"pirate", "flying", "etb_map"}, power=1, toughness=1, pips={"U": 1})
add("Staunch Crewmate", 2, "creature", {"pirate", "staunch_dig"}, power=2, toughness=1, pips={"U": 1})
add("Storm Fleet Negotiator", 3, "creature", {"pirate", "flying", "parley_attack"}, power=2, toughness=2,
    pips={"U": 1})
add("Starfield Vocalist", 4, "creature", {"etb_doubler", "warp"}, power=3, toughness=4, pips={"U": 1})
add("Panharmonicon", 4, "artifact", {"etb_doubler"})

# --- Draw/filtragem ------------------------------------------------------------
add("Brainstorm", 1, "instant", {"brainstorm"}, pips={"U": 1})
add("Frantic Search", 3, "instant", {"draw2_discard2_untap3"}, pips={"U": 1})
add("Curious Inquiry", 1, "enchantment", {"aura_pump_investigate"}, pips={"U": 1})
add("Rune of Flight", 2, "enchantment", {"aura_draw_flying"}, pips={"U": 1})
add("Mystic Remora", 1, "enchantment", {"remora"}, pips={"U": 1})
add("Sensei's Divining Top", 1, "artifact", {"top"})
add("Ghostly Flicker", 3, "instant", {"ghostly_flicker"}, pips={"U": 1})
add("Dramatic Reversal", 2, "instant", {"dramatic_reversal"}, pips={"U": 1})
add("Planar Incision", 2, "instant", {"planar_incision"}, pips={"U": 1})

# --- Interacao -------------------------------------------------------------
add("Counterspell", 2, "instant", {"interaction_counter"}, pips={"U": 2})
add("Mana Leak", 2, "instant", {"interaction_counter"}, pips={"U": 1})
add("Ionize", 3, "instant", {"interaction_counter"}, pips={"U": 1, "R": 1})
add("Spell Rupture", 2, "instant", {"interaction_counter"}, pips={"U": 1})
add("Chaos Warp", 3, "instant", {"interaction"}, pips={"R": 1})
add("Blasphemous Act", 9, "sorcery", {"wipe_reduces_creatures"}, pips={"R": 1})
add("Chain Reaction", 4, "sorcery", {"wipe_scales_creatures"}, pips={"R": 2})
add("Vapor Snag", 1, "instant", {"interaction_bounce"}, pips={"U": 1})
add("Magic Damper", 1, "instant", {"pump_untap_11"}, pips={"U": 1})

# --- Equipment (11 pecas) ------------------------------------------------------
add("Bloodforged Battle-Axe", 1, "artifact", {"equipment", "eq_pump_20", "eq_dmg_token_copy"})
add("Cloak of the Bat", 2, "artifact", {"equipment", "eq_flying_haste"})
add("Dragonfire Blade", 1, "artifact", {"equipment", "eq_pump_22_hexproof_mono"})
add("Embercleave", 6, "artifact", {"equipment", "eq_pump_11_ds_trample", "flash", "embercleave_cost_reduce"},
    pips={"R": 2})
add("Goldvein Pick", 2, "artifact", {"equipment", "eq_pump_11", "eq_dmg_treasure"})
add("Swiftfoot Boots", 2, "artifact", {"equipment", "eq_hexproof_haste"})
add("Sword of Once and Future", 3, "artifact", {"equipment", "eq_pump_22_protection", "eq_dmg_surveil_gy_cast"})
add("Tarrian's Soulcleaver", 1, "artifact", {"equipment", "eq_vigilance", "soulcleaver_death_counter"})
add("Trickster's Talisman", 1, "artifact", {"equipment", "eq_pump_11", "eq_dmg_token_copy_creature"})
add("Twin Blades", 3, "artifact", {"equipment", "eq_pump_11", "eq_etb_double_strike", "flash"}, pips={"R": 1})
add("Two-Handed Axe // Sweeping Cleave", 3, "artifact", {"equipment", "eq_attack_double_power"}, pips={"R": 1})

# --- Valor diverso -----------------------------------------------------------
add("The Ozolith", 1, "artifact", {"ozolith"})
add("Reliquary Tower", 0, "land", {"no_max_hand"}, produces=set())

# --- Terrenos --------------------------------------------------------------
add("Command Tower", 0, "land", set(), produces={"U", "R"})
add("Izzet Boilerworks", 0, "land", {"bounceland_ur"}, produces={"U", "R"})
add("Seat of the Synod", 0, "land", {"artifact_land"}, produces={"U"})
add("Silverbluff Bridge", 0, "land", {"artifact_land", "etb_tapped"}, produces={"U", "R"})
add("Swiftwater Cliffs", 0, "land", {"etb_tapped_gain1"}, produces={"U", "R"})
add("Temple of Epiphany", 0, "land", {"etb_tapped_scry1"}, produces={"U", "R"})
add("Island", 0, "land", set(), produces={"U"})
add("Mountain", 0, "land", set(), produces={"R"})

LAND_NAMES = {n for n, c in CARD_DB.items() if c.ctype == "land"}


def enters_tapped(name: str) -> bool:
    # Achado real (varredura de tags orfas): `"etb_tapped" in tags` e' um
    # match EXATO de string num frozenset -- "etb_tapped_gain1" (Swiftwater
    # Cliffs) e "etb_tapped_scry1" (Temple of Epiphany) nunca batiam,
    # entao essas 2 lands entravam destapadas (errado -- oraculo real diz
    # "enters tapped" nas duas). Corrigido com prefixo.
    return any(t.startswith("etb_tapped") for t in CARD_DB[name].tags) or name == "Silverbluff Bridge"
EQUIPMENT_NAMES = {n for n, c in CARD_DB.items() if "equipment" in c.tags}
ARTIFACT_LAND_NAMES = {n for n, c in CARD_DB.items() if "artifact_land" in c.tags}


def is_creature_card(name: str) -> bool:
    return CARD_DB[name].ctype == "creature" or "vehicle" in CARD_DB[name].tags


def is_pirate(name: str) -> bool:
    return "pirate" in CARD_DB[name].tags


def is_artifact_card(name: str) -> bool:
    return (CARD_DB[name].ctype == "artifact" or "artifact_creature" in CARD_DB[name].tags
            or name in ARTIFACT_LAND_NAMES)


def is_equipment(name: str) -> bool:
    return name in EQUIPMENT_NAMES


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
    equipped_to: Optional[int] = None  # uid da criatura, se este for um Equipment anexado
    is_token: bool = False


@dataclass
class GameState:
    turn: int = 0
    hand: list = field(default_factory=list)
    battlefield: list = field(default_factory=list)  # list[Permanent]
    graveyard: list = field(default_factory=list)  # list[str]
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
    descended_this_turn: bool = False
    jhoira_ingenuity: int = 0
    storm_vault_transformed: bool = False
    temp_pumps: dict = field(default_factory=dict)  # uid -> bonus de poder ate fim de turno
    double_strike_this_turn: set = field(default_factory=set)  # uids com double strike ate fim de turno

    # metrics -----------------------------------------------------------------
    proxy_damage_total: int = 0
    cards_drawn_extra: int = 0
    treasures_created_total: int = 0
    clues_created_total: int = 0
    food_created_total: int = 0
    counters_placed_total: int = 0
    equip_activations_total: int = 0
    etb_doubler_triggers_total: int = 0
    interaction_plays: int = 0
    recursion_events_total: int = 0
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


def new_uid(state: GameState) -> int:
    u = state.next_uid
    state.next_uid += 1
    return u


def find_perm(state: GameState, uid: int) -> Optional[Permanent]:
    return next((p for p in state.battlefield if p.uid == uid), None)


def creatures_in_play(state: GameState):
    return [p for p in state.battlefield if is_creature_card(p.card)]


def pirates_in_play(state: GameState):
    return [p for p in state.battlefield if is_pirate(p.card)]


EQUIPMENT_STATIC_BONUS = {
    "Bloodforged Battle-Axe": (2, 0),
    "Dragonfire Blade": (2, 2),
    "Embercleave": (1, 1),
    "Goldvein Pick": (1, 1),
    "Sword of Once and Future": (2, 2),
    "Trickster's Talisman": (1, 1),
    "Twin Blades": (1, 1),
    "Curious Inquiry": (1, 1),
}


def equipment_on(state: GameState, uid: int):
    return [p for p in state.battlefield if p.equipped_to == uid]


def equipment_power_bonus(state: GameState, perm: Permanent) -> int:
    return sum(EQUIPMENT_STATIC_BONUS.get(eq.card, (0, 0))[0] for eq in equipment_on(state, perm.uid))


def creature_power(state: GameState, perm: Permanent) -> int:
    base = CARD_DB[perm.card].power + perm.counters + equipment_power_bonus(state, perm)
    base += state.temp_pumps.get(perm.uid, 0)
    if (is_pirate(perm.card) and perm.card != "Corsair Captain"
            and any(p.card == "Corsair Captain" for p in state.battlefield)):
        base += 1  # "Other Pirates you control get +1/+1."
    return max(0, base)


# ---------------------------------------------------------------------------
# Mana
# ---------------------------------------------------------------------------

def ready_permanents(state: GameState, filter_fn=None):
    out = [p for p in state.battlefield if p.entered_turn < state.turn or "haste" in CARD_DB[p.card].tags]
    if filter_fn:
        out = [p for p in out if filter_fn(p)]
    return out


def rocks_mana(state: GameState) -> int:
    names = [p.card for p in state.battlefield]
    total = 0
    if "Sol Ring" in names:
        total += 2
    if "Arcane Signet" in names:
        total += 1
    if "Izzet Signet" in names:
        total += 1
    if "Izzet Locket" in names:
        total += 1
    if "Decanter of Endless Water" in names:
        total += 1
    if "Bender's Waterskin" in names:
        total += 1
    if "Thought Vessel" in names:
        total += 1
    if state.storm_vault_transformed:
        total += sum(1 for n in names if is_artifact_card(n))  # Vault of Catlacan: {T}: Add U per artifact
    return total


def lands_available(state: GameState) -> int:
    lands = sum(1 for p in state.battlefield if p.card in LAND_NAMES)
    if state.tapped_land_this_turn is not None:
        lands -= 1
    return lands


def total_mana(state: GameState) -> int:
    return lands_available(state) + rocks_mana(state) + state.bonus_mana_pool


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
    if state.storm_vault_transformed and color == "U":
        n += 1  # Vault of Catlacan: {T}: Add one mana of any color -- cobre U tambem
    if state.bonus_mana_pool > 0:
        n += 1  # Treasure/mana flutuante fixam qualquer cor
    return n


def has_color_sources_for(state: GameState, name: str) -> bool:
    for color, needed in CARD_DB[name].pips.items():
        if color_sources(state, color) < needed:
            return False
    return True


def effective_cost(state: GameState, name: str) -> int:
    mv = CARD_DB[name].mv
    if name == "Embercleave":
        attackers = sum(1 for p in state.battlefield if is_creature_card(p.card) and p.tapped)
        return max(0, mv - attackers)
    if name == "Blasphemous Act":
        return max(0, mv - len(creatures_in_play(state)))
    if name == "Chain Reaction":
        return mv  # X e' o dano, nao reduz o custo -- custo fixo
    return mv


def can_cast(state: GameState, name: str) -> bool:
    return remaining_mana(state) >= effective_cost(state, name) and has_color_sources_for(state, name)


def spend_mana(state: GameState, n: int):
    state.mana_spent_this_turn += n


# ---------------------------------------------------------------------------
# Motor central: Captain Storm + Treasure/Clue/Food + dobradores de ETB
# ---------------------------------------------------------------------------

def etb_trigger_multiplier(state: GameState) -> int:
    """Panharmonicon + Starfield Vocalist: cada um diz 'triggers an
    additional time' -- dois dobradores simultaneos MULTIPLICAM (2 gatilhos
    cada um dobrando os outros -> 2^n), nao somam. Mesmo principio de
    'dobradores empilham multiplicativamente' documentado noutros decks
    desta sessao (Beorn/Hei Bai, Roaming Throne + 2a fonte de copia)."""
    n = sum(1 for p in state.battlefield if p.card in ("Panharmonicon", "Starfield Vocalist"))
    return 2 ** n


def best_pirate_target(state: GameState) -> Optional[Permanent]:
    """'put a +1/+1 counter on TARGET Pirate you control' -- heuristica
    racional: prioriza quem tem Equipment relevante ou maior poder atual
    (empilha valor no atacante mais forte), cai pra propria Captain Storm
    se nao houver outro Pirata."""
    pirates = pirates_in_play(state)
    if not pirates:
        return None
    return max(pirates, key=lambda p: creature_power(state, p))


def on_artifact_enters(state: GameState, log: list):
    """Dispara a habilidade da propria Captain Storm ('whenever an
    artifact you control enters') -- chamada centralmente sempre que
    QUALQUER artefato entra em campo (permanentes reais E tokens de
    Treasure/Clue/Food), multiplicada pelos dobradores de ETB."""
    if not state.commander_in_play:
        return
    mult = etb_trigger_multiplier(state)
    for _ in range(mult):
        target = best_pirate_target(state)
        if target is not None:
            target.counters += 1
            state.counters_placed_total += 1
    if mult > 1:
        state.etb_doubler_triggers_total += mult - 1


def create_tokens(state: GameState, log: list, treasure: int = 0, clue: int = 0, food: int = 0):
    """Cria os tokens pedidos -- se Academy Manufactor esta em campo,
    'if you would create a Clue, Food, or Treasure token, instead create
    one of each' substitui CADA criacao individual por um trio completo
    (Treasure+Clue+Food), nao so' soma 1 de cada por chamada. Cada token
    criado e' um artefato entrando -- dispara `on_artifact_enters()`
    (multiplicado pelos dobradores de ETB) pra CADA token individual."""
    has_manufactor = any(p.card == "Academy Manufactor" for p in state.battlefield)
    requests = ["treasure"] * treasure + ["clue"] * clue + ["food"] * food
    for kind in requests:
        kinds_to_make = ("treasure", "clue", "food") if has_manufactor else (kind,)
        for k in kinds_to_make:
            perm = Permanent(card=f"{k.title()} Token", uid=new_uid(state), entered_turn=state.turn, is_token=True)
            if f"{k.title()} Token" not in CARD_DB:
                add(f"{k.title()} Token", 0, "artifact", {"sac_token", k})
            state.battlefield.append(perm)
            if k == "treasure":
                state.treasures_created_total += 1
            elif k == "clue":
                state.clues_created_total += 1
            else:
                state.food_created_total += 1
            on_artifact_enters(state, log)


def sac_treasures(state: GameState, n: int) -> int:
    """Sacrifica ate `n` Treasures em campo por 1 mana cada (mana de
    qualquer cor -- ja contado via `bonus_mana_pool`/`color_sources`).
    Devolve quantos foram sacrificados de verdade."""
    treasures = [p for p in state.battlefield if p.card == "Treasure Token"]
    n = min(n, len(treasures))
    for p in treasures[:n]:
        state.battlefield.remove(p)
        if "Captain Lannery Storm" in [q.card for q in state.battlefield]:
            lannery = next(q for q in state.battlefield if q.card == "Captain Lannery Storm")
            # "Whenever you sacrifice a Treasure, gets +1/+0 until end of
            # turn" -- aproximado como contador permanente pequeno neste
            # modelo (sem estado ate-fim-de-turno separado por permanente
            # aqui); documentado como leve superestimativa de duracao,
            # zerado no cleanup do turno via `state.temp_pumps`.
            state.temp_pumps[lannery.uid] = state.temp_pumps.get(lannery.uid, 0) + 1
        geardrake = next((q for q in state.battlefield if q.card == "Gleaming Geardrake"), None)
        if geardrake is not None:
            # "Whenever you sacrifice an artifact, put a +1/+1 counter on
            # this creature." Treasure e' um artefato -- dispara aqui.
            geardrake.counters += 1
            state.counters_placed_total += 1
    state.bonus_mana_pool += n
    return n


# ---------------------------------------------------------------------------
# ETB de permanentes reais (nao-token)
# ---------------------------------------------------------------------------

def resolve_etb(state: GameState, perm: Permanent, log: list):
    tags = CARD_DB[perm.card].tags
    if "etb_treasure" in tags:
        create_tokens(state, log, treasure=1)
    if "etb_clue" in tags:
        create_tokens(state, log, clue=1)
    if "etb_map" in tags:
        create_map_tokens(state, log, 1)
    if "tutor_equip_vehicle" in tags:
        pool = [c for c in state.library if c in CARD_DB
                and ("equipment" in CARD_DB[c].tags or "vehicle" in CARD_DB[c].tags)]
        if pool:
            best = max(pool, key=lambda n: CARD_DB[n].mv)
            state.library.remove(best)
            state.hand.append(best)
    if "staunch_dig" in tags:
        top4 = state.library[:4]
        state.library = state.library[4:]
        pool = [c for c in top4 if c in CARD_DB and (is_artifact_card(c) or is_pirate(c))]
        if pool:
            best = max(pool, key=lambda n: CARD_DB[n].mv)
            top4.remove(best)
            state.hand.append(best)
        state.library = state.library + top4
    if "bounceland_ur" in tags:
        other_lands = [p for p in state.battlefield if p.card in LAND_NAMES and p.uid != perm.uid]
        if other_lands:
            bounced = other_lands[0]
            state.battlefield.remove(bounced)
            state.hand.append(bounced.card)


def create_map_tokens(state: GameState, log: list, n: int):
    for _ in range(n):
        perm = Permanent(card="Map Token", uid=new_uid(state), entered_turn=state.turn, is_token=True)
        if "Map Token" not in CARD_DB:
            add("Map Token", 0, "artifact", {"sac_token", "map"})
        state.battlefield.append(perm)
        on_artifact_enters(state, log)


def enter_battlefield(state: GameState, name: str, log: list, tapped: bool = False, is_token: bool = False) -> Permanent:
    perm = Permanent(card=name, uid=new_uid(state), entered_turn=state.turn, tapped=tapped, is_token=is_token)
    state.battlefield.append(perm)
    mult = etb_trigger_multiplier(state) if is_artifact_card(name) or is_creature_card(name) else 1
    for _ in range(mult):
        resolve_etb(state, perm, log)
    if is_artifact_card(name):
        on_artifact_enters(state, log)
    return perm


def leave_battlefield(state: GameState, perm: Permanent, log: list, to_graveyard: bool = True):
    if perm in state.battlefield:
        state.battlefield.remove(perm)
    # devolve equipamentos anexados pro estado "solto" (nao anexados)
    for eq in state.battlefield:
        if eq.equipped_to == perm.uid:
            eq.equipped_to = None
    # The Ozolith: "whenever a creature you control leaves the battlefield,
    # if it had counters on it, put those counters on The Ozolith."
    ozolith = next((p for p in state.battlefield if p.card == "The Ozolith"), None)
    if ozolith is not None and perm.counters > 0 and is_creature_card(perm.card):
        ozolith.counters += perm.counters
        perm.counters = 0
    if "death_treasure" in CARD_DB[perm.card].tags:
        create_tokens(state, log, treasure=1)
    # Tarrian's Soulcleaver: "whenever another artifact or creature is put
    # into a graveyard from the battlefield, put a +1/+1 counter on
    # equipped creature."
    soulcleaver = next((p for p in state.battlefield if p.card == "Tarrian's Soulcleaver"
                         and p.equipped_to is not None), None)
    if soulcleaver is not None and to_graveyard and (is_artifact_card(perm.card) or is_creature_card(perm.card)):
        equipped = find_perm(state, soulcleaver.equipped_to)
        if equipped is not None:
            equipped.counters += 1
            state.counters_placed_total += 1
    if to_graveyard and not perm.is_token:
        state.graveyard.append(perm.card)


# ---------------------------------------------------------------------------
# Conjuracao de permanentes / comandante / equip
# ---------------------------------------------------------------------------

def cast_permanent(state: GameState, name: str, log: list):
    spend_mana(state, effective_cost(state, name))
    state.hand.remove(name)
    tapped = enters_tapped(name)
    perm = enter_battlefield(state, name, log, tapped=tapped)
    tags = CARD_DB[name].tags
    if "equipment" in tags:
        try_equip(state, perm, log, free=True)
    elif "aura_pump_investigate" in tags or "aura_draw_flying" in tags:
        try_equip(state, perm, log, free=True)  # reaproveita equipped_to pra rastrear o alvo do Aura
        if "aura_draw_flying" in tags:
            draw_cards(state, 1)  # Rune of Flight: "when this Aura enters, draw a card"
    state.spells_cast_this_turn += 1
    try_malcolm_clue(state, log)


def try_cast_commander(state: GameState, log: list):
    if state.commander_in_play or not can_cast(state, COMMANDER):
        return
    spend_mana(state, effective_cost(state, COMMANDER))
    perm = enter_battlefield(state, COMMANDER, log)
    state.commander_in_play = True
    state.commander_uid = perm.uid
    state.commander_cast_count += 1
    if state.commander_cast_turn is None:
        state.commander_cast_turn = state.turn
    state.spells_cast_this_turn += 1
    try_malcolm_clue(state, log)


def try_malcolm_clue(state: GameState, log: list):
    # Malcolm, the Eyes: "whenever you cast your SECOND spell each turn,
    # investigate."
    if "Malcolm, the Eyes" not in [p.card for p in state.battlefield]:
        return
    if state.spells_cast_this_turn == 2:
        create_tokens(state, log, clue=1)


def try_equip(state: GameState, eq_perm: Permanent, log: list, free: bool = False):
    """Anexa um Equipment recem-conjurado (ou ja em campo, via ativacao
    paga) na melhor criatura disponivel -- heuristica racional: prioriza
    o comandante (fonte do motor de contadores), senao o Pirata de maior
    poder atual."""
    creatures = creatures_in_play(state)
    if not creatures:
        return
    target = next((p for p in creatures if p.card == COMMANDER), None) or max(
        creatures, key=lambda p: creature_power(state, p))
    eq_perm.equipped_to = target.uid
    state.equip_activations_total += 1
    tags = CARD_DB[eq_perm.card].tags
    if "eq_etb_double_strike" in tags:
        state.temp_pumps[target.uid] = state.temp_pumps.get(target.uid, 0)  # so' documenta o double strike no combate
        state.double_strike_this_turn.add(target.uid)


def cast_instant_sorcery(state: GameState, name: str, log: list):
    spend_mana(state, effective_cost(state, name))
    state.hand.remove(name)
    tags = CARD_DB[name].tags
    state.spells_cast_this_turn += 1

    if "brainstorm" in tags:
        draw_cards(state, 3)
        for _ in range(min(2, len(state.hand))):
            worst = min(state.hand, key=lambda c: CARD_DB[c].mv if c in CARD_DB else 0)
            state.hand.remove(worst)
            state.library.insert(0, worst)

    elif "draw2_discard2_untap3" in tags:
        for _ in range(2):
            if state.library:
                state.hand.append(state.library.pop(0))
        refund = min(3, lands_available(state))
        state.mana_spent_this_turn = max(0, state.mana_spent_this_turn - refund)
        for _ in range(min(2, len(state.hand))):
            worst = min(state.hand, key=lambda c: CARD_DB[c].mv if c in CARD_DB else 0)
            state.hand.remove(worst)
            state.graveyard.append(worst)

    elif "discard_cost_draw2_treasure1" in tags:
        if state.hand:
            worst = min(state.hand, key=lambda c: CARD_DB[c].mv if c in CARD_DB else 0)
            state.hand.remove(worst)
            state.graveyard.append(worst)
        draw_cards(state, 2)
        create_tokens(state, log, treasure=1)

    elif "brass_bounty" in tags:
        n = sum(1 for p in state.battlefield if p.card in LAND_NAMES)
        create_tokens(state, log, treasure=n)

    elif "ghostly_flicker" in tags:
        targets = [p for p in state.battlefield if is_creature_card(p.card) or is_artifact_card(p.card)
                   or p.card in LAND_NAMES]
        targets.sort(key=lambda p: -CARD_DB[p.card].mv)
        for p in targets[:2]:
            leave_battlefield(state, p, log, to_graveyard=False)
            enter_battlefield(state, p.card, log)

    elif "dramatic_reversal" in tags:
        for p in state.battlefield:
            if p.card not in LAND_NAMES:
                p.tapped = False

    elif "planar_incision" in tags:
        candidates = [p for p in state.battlefield if is_creature_card(p.card) or is_artifact_card(p.card)]
        if candidates:
            best = max(candidates, key=lambda p: CARD_DB[p.card].mv)
            leave_battlefield(state, best, log, to_graveyard=False)
            new_perm = enter_battlefield(state, best.card, log)
            new_perm.counters += 1

    elif "pump_untap_11" in tags:
        # Magic Damper: "+1/+1 and hexproof until EOT, untap it." Hexproof
        # e' 📊 (protecao contra remocao de oponente, sem oponente
        # modelado), pump e untap sao reais (untap = pode atacar de novo
        # se ja tinha atacado, ou destravar mana de uma criatura-mana).
        creatures = creatures_in_play(state)
        if creatures:
            target = max(creatures, key=lambda p: creature_power(state, p))
            state.temp_pumps[target.uid] = state.temp_pumps.get(target.uid, 0) + 1
            target.tapped = False

    elif "interaction_counter" in tags or "interaction" in tags or "interaction_bounce" in tags:
        state.interaction_plays += 1

    elif "wipe_reduces_creatures" in tags or "wipe_scales_creatures" in tags:
        state.interaction_plays += 1  # Regra 1: simetrico sem oponente = so' metrica

    state.graveyard.append(name)


# ---------------------------------------------------------------------------
# Combate
# ---------------------------------------------------------------------------

def try_cast_embercleave(state: GameState, attackers: list, log: list):
    if "Embercleave" not in state.hand or not attackers:
        return
    if remaining_mana(state) < effective_cost(state, "Embercleave") or not has_color_sources_for(state, "Embercleave"):
        return
    spend_mana(state, effective_cost(state, "Embercleave"))
    state.hand.remove("Embercleave")
    perm = enter_battlefield(state, "Embercleave", log)
    best = max(attackers, key=lambda p: creature_power(state, p))
    perm.equipped_to = best.uid
    state.equip_activations_total += 1
    state.spells_cast_this_turn += 1


def equipment_combat_damage_triggers(state: GameState, attacker: Permanent, log: list):
    for eq in equipment_on(state, attacker.uid):
        tags = CARD_DB[eq.card].tags
        if "eq_dmg_token_copy" in tags:
            enter_battlefield(state, eq.card, log, is_token=True)
        elif "eq_dmg_treasure" in tags:
            create_tokens(state, log, treasure=1)
        elif "eq_dmg_surveil_gy_cast" in tags:
            pool = [c for c in state.graveyard if c in CARD_DB and CARD_DB[c].ctype in ("instant", "sorcery")
                    and CARD_DB[c].mv <= 2]
            if pool:
                pick = max(pool, key=lambda n: CARD_DB[n].mv)
                state.graveyard.remove(pick)
                cast_instant_sorcery_free(state, pick, log)
        elif "eq_dmg_token_copy_creature" in tags:
            new_perm = enter_battlefield(state, attacker.card, log, is_token=True)
            state.battlefield.remove(eq)
            state.recursion_events_total += 1
        elif "aura_pump_investigate" in tags:
            create_tokens(state, log, clue=1)  # Curious Inquiry: investigate ao causar dano de combate


def cast_instant_sorcery_free(state: GameState, name: str, log: list):
    tags = CARD_DB[name].tags
    state.spells_cast_this_turn += 1
    if "brainstorm" in tags:
        draw_cards(state, 3)
    elif "draw2_discard2_untap3" in tags:
        draw_cards(state, 2)


def try_ozolith_move(state: GameState):
    ozolith = next((p for p in state.battlefield if p.card == "The Ozolith"), None)
    if ozolith is None or ozolith.counters == 0:
        return
    creatures = creatures_in_play(state)
    if not creatures:
        return
    target = max(creatures, key=lambda p: creature_power(state, p))
    target.counters += ozolith.counters
    state.counters_placed_total += ozolith.counters
    ozolith.counters = 0


def combat_step(state: GameState, log: list, second_phase: bool = False, exclude_uid: Optional[int] = None):
    if not second_phase:
        try_ozolith_move(state)
    haste_equipment = {"Cloak of the Bat", "Swiftfoot Boots"}
    attackers = [p for p in creatures_in_play(state)
                 if (p.entered_turn < state.turn or "haste" in CARD_DB[p.card].tags
                     or any(eq.card in haste_equipment for eq in equipment_on(state, p.uid)))
                 and p.uid != exclude_uid]
    if not attackers:
        return
    for p in attackers:
        p.tapped = True

    try_cast_embercleave(state, attackers, log)

    if any(p.card == "Captain Vargus Wrath" for p in attackers) and state.commander_cast_count > 0:
        for p in pirates_in_play(state):
            state.temp_pumps[p.uid] = state.temp_pumps.get(p.uid, 0) + state.commander_cast_count

    total_power = 0
    port_razer_connected = False
    for p in attackers:
        power = creature_power(state, p)
        if p.card == "Two-Handed Axe":
            continue
        if any(eq.card == "Two-Handed Axe" for eq in equipment_on(state, p.uid)):
            power *= 2
        if p.uid in state.double_strike_this_turn or any(
                eq.card in ("Twin Blades", "Embercleave") and eq.equipped_to == p.uid for eq in state.battlefield):
            power *= 2  # double strike ~= dano de combate 2x (mesma agregacao usada nos outros sims da sessao)
        total_power += power
        equipment_combat_damage_triggers(state, p, log)
        if p.card == "Fathom Fleet Swordjack":
            proxy_burn(state, sum(1 for q in state.battlefield if is_artifact_card(q.card)))
        if p.card == "Port Razer" and not second_phase:
            port_razer_connected = True
        if p.card == "Jackdaw":
            artifact_count = sum(1 for q in state.battlefield if is_artifact_card(q.card))
            if artifact_count > len(state.hand):
                for c in state.hand[:]:
                    state.graveyard.append(c)
                state.hand = []
                draw_cards(state, artifact_count)

    proxy_burn(state, total_power)

    if any(p.card in ("Captain Lannery Storm", "Careening Mine Cart") for p in attackers):
        create_tokens(state, log, treasure=1)
    if any(p.card == "Storm Fleet Negotiator" for p in attackers):
        if state.library and state.library[0] in CARD_DB and CARD_DB[state.library[0]].ctype != "land":
            create_map_tokens(state, log, 1)
        draw_cards(state, 1)
    if total_power > 0 and any(p.card == "Storm the Vault // Vault of Catlacan" for p in state.battlefield):
        create_tokens(state, log, treasure=1)

    if port_razer_connected:
        razer = next(p for p in attackers if p.card == "Port Razer")
        for p in state.battlefield:
            if is_creature_card(p.card):
                p.tapped = False
        combat_step(state, log, second_phase=True, exclude_uid=razer.uid)


# ---------------------------------------------------------------------------
# Ativacoes / gatilhos de fim de turno
# ---------------------------------------------------------------------------

def try_activated_abilities(state: GameState, log: list):
    names = [p.card for p in state.battlefield]

    if "Jhoira, Ageless Innovator" in names:
        jhoira = next(p for p in state.battlefield if p.card == "Jhoira, Ageless Innovator")
        if jhoira.entered_turn < state.turn and not jhoira.tapped:
            jhoira.tapped = True
            state.jhoira_ingenuity += 2
            pool = [c for c in state.hand if c in CARD_DB and is_artifact_card(c)
                    and CARD_DB[c].mv <= state.jhoira_ingenuity]
            if pool:
                best = max(pool, key=lambda n: CARD_DB[n].mv)
                state.hand.remove(best)
                enter_battlefield(state, best, log)

    top = next((p for p in state.battlefield if p.card == "Sensei's Divining Top"), None)
    if top is not None and not top.tapped:
        # "{T}: Draw a card, then put this artifact on top of its owner's
        # library." Mais valioso que o modo "{1}: olha as 3 do topo" --
        # prioriza a compra real. Sai do campo (vai pro topo da
        # biblioteca de verdade, sera' comprado nos proximos turnos).
        state.battlefield.remove(top)
        state.library.insert(0, "Sensei's Divining Top")
        draw_cards(state, 1)

    remora = next((p for p in state.battlefield if p.card == "Mystic Remora"), None)
    if remora is not None and remora.entered_turn < state.turn:
        # Cumulative upkeep real, mas sem oponente conjurando spells pra
        # disparar o gatilho de compra -- nenhum valor a ganhar segurando,
        # so' custo crescente. Sacrificada na 1a oportunidade apos entrar
        # (achado real, nao decidido por "vale a pena" -- e' a matematica
        # real: 0 gatilhos possiveis neste modelo solo).
        state.battlefield.remove(remora)
        state.graveyard.append(remora.card)

    if "Izzet Locket" in names and remaining_mana(state) >= 4:
        top = next(p for p in state.battlefield if p.card == "Izzet Locket")
        spend_mana(state, 4)
        state.battlefield.remove(top)
        draw_cards(state, 2)

    if "Lotus Petal" in names:
        petal = next(p for p in state.battlefield if p.card == "Lotus Petal")
        state.battlefield.remove(petal)
        state.bonus_mana_pool += 1

    for eq_name, static_bonus in list(EQUIPMENT_STATIC_BONUS.items()) + [
            ("Cloak of the Bat", None), ("Swiftfoot Boots", None), ("Tarrian's Soulcleaver", None)]:
        for perm in [p for p in state.battlefield if p.card == eq_name and p.equipped_to is None]:
            try_equip(state, perm, log)


def try_storm_vault_transform(state: GameState):
    if state.storm_vault_transformed:
        return
    if "Storm the Vault // Vault of Catlacan" not in [p.card for p in state.battlefield]:
        return
    artifact_count = sum(1 for p in state.battlefield if is_artifact_card(p.card))
    if artifact_count >= 5:
        state.storm_vault_transformed = True


def try_end_step(state: GameState, log: list):
    if state.descended_this_turn and "Enterprising Scallywag" in [p.card for p in state.battlefield]:
        create_tokens(state, log, treasure=1)
    try_storm_vault_transform(state)


# ---------------------------------------------------------------------------
# Loop de conjuracao / turno
# ---------------------------------------------------------------------------

ROCK_NAMES = {"Sol Ring", "Arcane Signet", "Izzet Signet", "Izzet Locket", "Decanter of Endless Water",
              "Bender's Waterskin", "Thought Vessel", "Lotus Petal"}


def try_cast_loop(state: GameState, log: list):
    changed = True
    while changed:
        changed = False
        candidates = [c for c in state.hand if c in CARD_DB and CARD_DB[c].ctype != "land" and can_cast(state, c)
                      and c != "Embercleave"]
        if not candidates:
            break

        def prio(c):
            if c in ROCK_NAMES:
                return 0
            if CARD_DB[c].ctype == "creature":
                return 1
            if CARD_DB[c].ctype in ("artifact", "enchantment"):
                return 2
            return 3

        pick = min(candidates, key=lambda c: (prio(c), effective_cost(state, c)))
        if CARD_DB[pick].ctype in ("creature", "artifact", "enchantment"):
            cast_permanent(state, pick, log)
        else:
            cast_instant_sorcery(state, pick, log)
        changed = True


def play_land(state: GameState, log: list):
    if state.lands_played_this_turn >= 1:
        return
    hand_lands = [c for c in state.hand if c in LAND_NAMES]
    if not hand_lands:
        return

    def score(n):
        return 1 if enters_tapped(n) else 0

    hand_lands.sort(key=score)
    pick = hand_lands[0]
    state.hand.remove(pick)
    state.lands_played_this_turn += 1
    tapped = enters_tapped(pick)
    perm = enter_battlefield(state, pick, log, tapped=tapped)
    if tapped:
        state.tapped_land_this_turn = perm.uid


def convert_treasures_to_mana(state: GameState):
    """Sacrifica Treasures em campo pra cobrir o deficit de mana desta
    fase de conjuracao, ate o limite existente -- feito sob demanda antes
    de cada tentativa de conjurar algo mais caro que a mana de
    lands/rocks/bonus_mana_pool atual."""
    treasures = sum(1 for p in state.battlefield if p.card == "Treasure Token")
    if treasures > 0:
        sac_treasures(state, treasures)


def run_turn(state: GameState, log: list):
    state.turn += 1
    state.lands_played_this_turn = 0
    state.tapped_land_this_turn = None
    state.mana_spent_this_turn = 0
    state.bonus_mana_pool = 0
    state.spells_cast_this_turn = 0
    state.descended_this_turn = False
    state.temp_pumps = {}
    state.double_strike_this_turn = set()
    for p in state.battlefield:
        p.tapped = False
    if "Jhoira, Ageless Innovator" in [p.card for p in state.battlefield]:
        jhoira = next(p for p in state.battlefield if p.card == "Jhoira, Ageless Innovator")
        jhoira.tapped = False

    draw_cards(state, 1)
    play_land(state, log)
    try_cast_commander(state, log)
    convert_treasures_to_mana(state)
    try_cast_loop(state, log)
    try_activated_abilities(state, log)
    convert_treasures_to_mana(state)
    try_cast_loop(state, log)
    try_cast_commander(state, log)

    combat_step(state, log)

    convert_treasures_to_mana(state)
    try_cast_loop(state, log)

    while len(state.hand) > (99 if state.hand_size_no_max else 7):
        worst = min(state.hand, key=lambda c: CARD_DB[c].mv if c in CARD_DB else 0)
        state.hand.remove(worst)
        state.graveyard.append(worst)
        state.descended_this_turn = True

    state.hand_size_no_max = any("no_max_hand" in CARD_DB[p.card].tags for p in state.battlefield)
    try_end_step(state, log)


# ---------------------------------------------------------------------------
# Decklist
# ---------------------------------------------------------------------------

DECKLIST_TEXT = """
1 Academy Manufactor
1 Arcane Signet
1 Bender's Waterskin
1 Blasphemous Act
1 Bloodforged Battle-Axe
1 Brainstorm
1 Brass's Bounty
1 Captain Lannery Storm
1 Captain Vargus Wrath
1 Careening Mine Cart
1 Chain Reaction
1 Chaos Warp
1 Cloak of the Bat
1 Command Tower
1 Corsair Captain
1 Counterspell
1 Curious Inquiry
1 Deadeye Quartermaster
1 Decanter of Endless Water
1 Dragonfire Blade
1 Dramatic Reversal
1 Embercleave
1 Enterprising Scallywag
1 Fathom Fleet Swordjack
1 Fellwar Stone
1 Frantic Search
1 Ghostly Flicker
1 Gleaming Geardrake
1 Goldvein Pick
1 Impulsive Pilferer
1 Ionize
13 Island
1 Izzet Boilerworks
1 Izzet Locket
1 Izzet Signet
1 Jackdaw
1 Jhoira, Ageless Innovator
1 Kitesail Larcenist
1 Lotus Petal
1 Magic Damper
1 Malcolm, the Eyes
1 Mana Leak
13 Mountain
1 Mystic Remora
1 Oaken Siren
1 Panharmonicon
1 Planar Incision
1 Plundering Pirate
1 Port Razer
1 Reliquary Tower
1 Rune of Flight
1 Sailor of Means
1 Seat of the Synod
1 Seize the Spoils
1 Sensei's Divining Top
1 Silverbluff Bridge
1 Sol Ring
1 Spell Rupture
1 Spyglass Siren
1 Starfield Vocalist
1 Staunch Crewmate
1 Storm Fleet Negotiator
1 Storm the Vault // Vault of Catlacan
1 Swiftfoot Boots
1 Swiftwater Cliffs
1 Sword of Once and Future
1 Tarrian's Soulcleaver
1 Temple of Epiphany
1 The Ozolith
1 Thought Vessel
1 Trickster's Talisman
1 Twin Blades
1 Two-Handed Axe // Sweeping Cleave
1 Vapor Snag
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
# ⚠️ 98 cartas (nao 99) -- lista enviada pelo usuario ja vem faltando 1
# carta pro total padrao de 100 (ver `auditoria.md`, secao 1). Nao
# inventado aqui.
assert len(BASE_LIBRARY) == 98, f"esperado 98 cartas na biblioteca (lista incompleta, documentado), achei {len(BASE_LIBRARY)}"
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
    print(f"Clues criados (media): {avg(lambda s: s.clues_created_total):.1f}")
    print(f"Food criado (media): {avg(lambda s: s.food_created_total):.1f}")
    print(f"Contadores colocados pela Captain Storm (media): {avg(lambda s: s.counters_placed_total):.1f}")
    print(f"Gatilhos extra via dobradores de ETB (media): {avg(lambda s: s.etb_doubler_triggers_total):.1f}")
    print(f"Equip/attach ativados (media): {avg(lambda s: s.equip_activations_total):.1f}")
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
                    "clues_created_total": s.clues_created_total,
                    "food_created_total": s.food_created_total,
                    "counters_placed_total": s.counters_placed_total,
                    "etb_doubler_triggers_total": s.etb_doubler_triggers_total,
                    "equip_activations_total": s.equip_activations_total,
                    "interaction_plays": s.interaction_plays,
                    "mulligans": s.mulligans,
                    "library_emptied": s.library_emptied,
                }
                f.write(json.dumps(row) + "\n")
    return results


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "captainstorm_v1_runs.jsonl")
    run_batch(3000, seed_base=1_000_000, turns=8, out_path=out)
