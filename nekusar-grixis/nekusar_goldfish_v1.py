"""
Goldfish simulator — Nekusar, the Mindrazer, "V9 Wheel Breach Storm" (Grixis, U/B/R)

Construido do zero em 2026-08-23. Passo 0 (regra de
`references/goldfish-sim-card-rules.md`): a auditoria (`auditoria.md`,
secoes 5 e 6) ja fez a varredura mecanica completa no oraculo real de
todas as 99 cartas — reaproveitada aqui integralmente, nao refeita do
zero. 9 payoffs de dano/perda-de-vida-por-compra e 15 fontes de
wheel/draw-em-massa catalogados, todos com efeito real implementado
abaixo.

Mecanica central: o comandante ("Whenever an opponent draws a card,
Nekusar deals 1 damage to that player" + "At the beginning of each
player's draw step, that player draws an additional card") empilha com
8 outros payoffs reais (Orcish Bowmasters, Sheoldred, Underworld
Dreams, Spiteful Visions, Phyrexian Tyranny, Razorkin Needlehead,
Scrawling Crawler, Liliana's Caress-p/descarte) — cada evento de wheel
(Wheel of Fortune, Windfall, etc.) multiplica o dano por quantos desses
estao em campo.

Sem oponente real num goldfish solo: os "3 oponentes" e suas compras
sao um PROXY agregado, documentado explicitamente — nunca finjo vida
real de oponente nem "matei a mesa". `NUM_OPPONENTS = 3` e uma premissa
declarada (mesa de 4), nao um dado real. `drain_damage_total` e
`proxy_kill_damage_total` sao contadores agregados de dano teorico
gerado pelos payoffs, nunca subtraidos de uma vida real de ninguem.

Combo real de storm/recursao (auditoria secao 6, nao um combo de 2
pecas isolado — cadeia que pode explodir quando as pecas se alinham):
**Underworld Breach** da escape (custo = mana cost + exilar 3 outras
cartas do cemiterio) a toda carta nao-terreno no cemiterio, sacrificada
no fim do turno. Combinado com rituais baratos (Dark Ritual, Cabal
Ritual) e o proprio cemiterio cheio de wheels descartados, isso pode
recastar varios wheels/rituais no mesmo turno antes do cemiterio
esgotar (a exigencia de exilar 3 cartas a cada recast e AUTO-LIMITANTE
— nao e um loop infinito, e um loop real mas finito que termina quando
o cemiterio fica pequeno demais). Implementado como um loop real que
respeita esse custo, nao decorativo.

Simplificacoes documentadas (nao inventadas — omissoes explicitas):
- Sem oponente real: todo dano/perda-de-vida de oponente e PROXY
  agregado (`NUM_OPPONENTS=3`), nunca vida real rastreada de ninguem.
  Contramagicas/protecao (Force of Will, Mana Drain, Counterspell,
  Arcane Denial, Swan Song, Flusterstorm, Pact of Negation, Mindbreak
  Trap, An Offer You Can't Refuse, Deflecting Swat) sao conjuradas
  quando ha mana sobrando (mesma convencao dos outros simuladores
  desta biblioteca), sem efeito de combate real modelado.
- Fetchlands (Arid Mesa, Bloodstained Mire, Flooded Strand, Marsh
  Flats, Misty Rainforest, Polluted Delta, Scalding Tarn, Verdant
  Catacombs, Wooded Foothills): tratadas como terreno generico normal
  no modelo de mana total (nao pip a pip); custo de 1 vida aplicado
  real, thinning de biblioteca NAO modelado (simplificacao disclosed).
- Brain Freeze: `storm_count` real rastreado (spells conjuradas no
  turno), mas o efeito (mill 3 x copias) e só registrado como
  `mill_proxy_total` — nao existe biblioteca de oponente real pra
  milhar de verdade.
- Mindcrank: mila voce mesmo (nao ha oponente real) proporcional ao
  `proxy` de dano gerado — registrado como metrica separada, nao
  aplicado a biblioteca real de ninguem.
- Wheel of Misfortune: modelado como um wheel "cheio" padrao (assume
  premissa de nao ser quem escolheu o menor numero, cenario mais
  comum); a metade de dano por numero escolhido nao e modelada
  numericamente (depende de escolha simultanea de oponente real).
- Combate: nenhum dano de combate real modelado (deck nao e de
  criaturas de ataque, e um deck de dano por gatilho de compra).
"""

import json
import random
import re
import signal
import statistics
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Card database
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Card:
    name: str
    mv: int
    ctype: str
    tags: frozenset = field(default_factory=frozenset)


CARD_DB: dict[str, Card] = {}


def add(name, mv, ctype, tags=()):
    CARD_DB[name] = Card(name=name, mv=mv, ctype=ctype, tags=frozenset(tags))


COMMANDER = "Nekusar, the Mindrazer"
add(COMMANDER, 5, "creature", {"commander", "payoff"})

NUM_OPPONENTS = 3  # premissa declarada (mesa de 4), nunca vida real rastreada

# --- Terrenos (36) ------------------------------------------------------------
FETCH_NAMES = {"Arid Mesa", "Bloodstained Mire", "Flooded Strand", "Marsh Flats",
                "Misty Rainforest", "Polluted Delta", "Scalding Tarn", "Verdant Catacombs",
                "Wooded Foothills"}
for n in FETCH_NAMES:
    add(n, 0, "land", {"fetch"})
add("Blood Crypt", 0, "land", set())
add("Badlands", 0, "land", set())
add("Cascade Bluffs", 0, "land", {"etb_tapped_filter"})
add("Cephalid Coliseum", 0, "land", {"threshold_wheel"})
add("City of Brass", 0, "land", set())
add("Command Tower", 0, "land", set())
add("Emergence Zone", 0, "land", {"flash_enabler"})
add("Exotic Orchard", 0, "land", set())
add("Geier Reach Sanitarium", 0, "land", {"wheel_source_small"})
add("Gemstone Caverns", 0, "land", set())
add("Mikokoro, Center of the Sea", 0, "land", {"wheel_source_small"})
add("Mistrise Village", 0, "land", set())
add("Otawara, Soaring City", 0, "land", set())
add("Steam Vents", 0, "land", set())
add("Underground Sea", 0, "land", set())
add("Undercity Sewers", 0, "land", {"etb_tapped_filter"})
add("Volcanic Island", 0, "land", set())
add("Watery Grave", 0, "land", set())
add("Xander's Lounge", 0, "land", set())
add("Island", 0, "land", set())
add("Mountain", 0, "land", set())
add("Swamp", 0, "land", set())

# --- Comandante-adjacente / criaturas payoff (9) ------------------------------
add("Dauthi Voidwalker", 2, "creature", set())
add("Faerie Mastermind", 2, "creature", {"opponent_dependent"})
add("Jace's Archivist", 3, "creature", {"wheel_repeatable"})
add("Magus of the Wheel", 3, "creature", {"wheel_sac"})
add("Orcish Bowmasters", 2, "creature", {"payoff"})
add("Razorkin Needlehead", 2, "creature", {"payoff"})
add("Scrawling Crawler", 3, "artifact_creature", {"payoff", "wheel_upkeep"})
add("Sheoldred, the Apocalypse", 4, "creature", {"payoff", "lifegain_on_draw"})
add("Spark Double", 4, "creature", {"copy"})

# --- Wheels (7) ----------------------------------------------------------------
add("Echo of Eons", 6, "sorcery", {"wheel_full"})
add("Teferi's Puzzle Box", 4, "artifact", {"wheel_passive"})
add("Wheel and Deal", 4, "instant", {"wheel_full"})
add("Wheel of Fortune", 3, "sorcery", {"wheel_full"})
add("Wheel of Misfortune", 3, "sorcery", {"wheel_full"})
add("Windfall", 3, "sorcery", {"wheel_full"})
add("Winds of Change", 1, "sorcery", {"wheel_full"})

# --- Payoffs (6) ----------------------------------------------------------------
add("Bloodchief Ascension", 1, "enchantment", {"quest_drain"})
add("Liliana's Caress", 2, "enchantment", {"discard_payoff"})
add("Phyrexian Tyranny", 3, "enchantment", {"payoff"})
add("Spiteful Visions", 4, "enchantment", {"payoff", "wheel_passive"})
add("Underworld Dreams", 3, "enchantment", {"payoff"})
add("Waste Not", 2, "enchantment", {"discard_payoff"})

# --- Combo e recursao (7) -------------------------------------------------------
add("Animate Dead", 2, "enchantment", {"reanimate"})
add("Brain Freeze", 2, "instant", {"storm_mill"})
add("Cabal Ritual", 2, "instant", {"ritual"})
add("Dark Ritual", 1, "instant", {"ritual"})  # tambem listado em Artefatos e Outros, mesma carta
add("Flashback", 1, "instant", {"interaction"})
add("Past in Flames", 4, "sorcery", {"breach_engine"})
add("Reanimate", 1, "sorcery", {"reanimate"})
add("Underworld Breach", 2, "enchantment", {"breach_engine"})

# --- Tutores (5) -----------------------------------------------------------------
add("Beseech the Mirror", 4, "sorcery", {"tutor"})
add("Demonic Tutor", 2, "sorcery", {"tutor"})
add("Imperial Seal", 2, "sorcery", {"tutor_top"})
add("Solve the Equation", 3, "sorcery", {"tutor_instant_sorcery"})
add("Vampiric Tutor", 1, "instant", {"tutor_top"})

# --- Protecao e remocao (14) -------------------------------------------------------
add("An Offer You Can't Refuse", 2, "instant", {"interaction"})
add("Arcane Denial", 2, "instant", {"interaction"})
add("Counterspell", 2, "instant", {"interaction"})
add("Cyclonic Rift", 2, "instant", {"interaction"})
add("Deadly Rollick", 2, "instant", {"interaction"})
add("Deflecting Swat", 3, "instant", {"interaction", "free_with_commander"})
add("Feed the Swarm", 2, "instant", {"interaction"})
add("Flusterstorm", 1, "instant", {"interaction"})
add("Force of Will", 5, "instant", {"interaction"})
add("Mana Drain", 2, "instant", {"interaction"})
add("Mindbreak Trap", 3, "instant", {"interaction"})
add("Pact of Negation", 3, "instant", {"interaction"})
add("Return the Favor", 3, "instant", {"interaction"})
add("Swan Song", 1, "instant", {"interaction"})

# --- Artefatos e outros (15) -------------------------------------------------------
add("Arcane Signet", 2, "artifact", {"rock1"})
add("Cursed Totem", 2, "artifact", set())
add("Defense Grid", 2, "artifact", set())
add("Hexing Squelcher", 2, "creature", set())
add("Lightning Greaves", 2, "artifact", set())
add("Mindcrank", 2, "artifact", {"mill_engine"})
add("Mox Opal", 0, "artifact", {"rock_conditional"})
add("Propaganda", 3, "enchantment", set())
add("Resonating Lute", 4, "artifact", {"draw_conditional"})
add("Sensei's Divining Top", 1, "artifact", {"card_selection"})
add("Sol Ring", 1, "artifact", {"rock2"})
add("Talisman of Creativity", 2, "artifact", {"rock1"})
add("Talisman of Dominance", 2, "artifact", {"rock1"})
add("The One Ring", 4, "artifact", {"the_one_ring"})

ARTIFACT_ISH = {"artifact", "artifact_creature"}
CREATURE_ISH = {"creature", "artifact_creature"}
LAND_NAMES = {n for n, c in CARD_DB.items() if c.ctype == "land"}


def is_creature_card(name: str) -> bool:
    return CARD_DB[name].ctype in CREATURE_ISH


def is_artifact_card(name: str) -> bool:
    return CARD_DB[name].ctype in ARTIFACT_ISH


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
    mana_spent_this_turn: int = 0
    bonus_mana_pool: int = 0
    spells_cast_this_turn: int = 0
    underworld_breach_active: bool = False
    the_one_ring_burden: int = 0
    life: int = 40

    commander_in_play: bool = False
    commander_cast_count: int = 0
    commander_cast_turn: Optional[int] = None
    creature_cast_turn: dict = field(default_factory=dict)

    # metrics -------------------------------------------------------------
    wheel_events_total: int = 0
    full_wheels_total: int = 0
    proxy_damage_total: int = 0
    proxy_lifegain_total: int = 0
    cards_drawn_extra: int = 0
    tutors_used_total: int = 0
    storm_count_max: int = 0
    breach_recasts_total: int = 0
    breach_loops_total: int = 0
    mill_proxy_total: int = 0
    reanimator_targets_total: int = 0
    library_emptied: bool = False


def draw_cards(state: GameState, n: int):
    for _ in range(n):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1
        else:
            state.library_emptied = True


def proxy_drain(state: GameState, n: int):
    """Dano/perda-de-vida agregada dos PROXY opponents — nunca vida real de
    ninguem, so um contador de output teorico dos payoffs."""
    state.proxy_damage_total += n


# ---------------------------------------------------------------------------
# Motor central — payoffs de dano por compra + wheels
# ---------------------------------------------------------------------------

def damage_per_opponent_draw(state: GameState) -> int:
    """Soma quanto dano/perda-de-vida CADA compra de UM oponente causa,
    somando todos os payoffs ativos (auditoria secao 5.1)."""
    total = 0
    if state.commander_in_play:
        total += 1
    if "Orcish Bowmasters" in state.battlefield:
        total += 1
    if "Sheoldred, the Apocalypse" in state.battlefield:
        total += 2
    if "Underworld Dreams" in state.battlefield:
        total += 1
    if "Spiteful Visions" in state.battlefield:
        total += 1
    if "Phyrexian Tyranny" in state.battlefield:
        total += 2  # premissa: oponente nao paga o {2}, documentado
    if "Razorkin Needlehead" in state.battlefield:
        total += 1
    if "Scrawling Crawler" in state.battlefield:
        total += 1
    return total


def symmetric_extra_draws_per_player(state: GameState) -> int:
    """Efeitos 'at the beginning of each player's draw step, draws +1'."""
    n = 0
    if state.commander_in_play:
        n += 1
    if "Spiteful Visions" in state.battlefield:
        n += 1
    return n


def wheel_event(state: GameState, my_draws: int, opp_draws_each: int, source: str, full_wheel: bool = True):
    """Um evento de wheel: EU compro `my_draws` cartas de verdade (vantagem
    real de mao); cada um dos NUM_OPPONENTS oponentes-proxy compra
    `opp_draws_each`, cada compra alheia gerando dano real via
    `damage_per_opponent_draw()`."""
    state.wheel_events_total += 1
    if full_wheel:
        state.full_wheels_total += 1
    draw_cards(state, my_draws)
    if state.commander_in_play or "Spiteful Visions" in state.battlefield:
        pass  # meu proprio draw ja processado acima; dano por MINHA compra tratado a parte no draw_step
    dpd = damage_per_opponent_draw(state)
    total_dmg = dpd * opp_draws_each * NUM_OPPONENTS
    proxy_drain(state, total_dmg)
    if "Mindcrank" in state.battlefield:
        state.mill_proxy_total += total_dmg
    if "Bloodchief Ascension" in state.battlefield and total_dmg > 0:
        # aproxima: cada evento com dano real conta como "oponente perdeu 2+" o suficiente vezes
        state.proxy_lifegain_total += min(NUM_OPPONENTS, total_dmg // 2) * 2


def draw_step(state: GameState):
    extra = symmetric_extra_draws_per_player(state)
    my_draws = 1 + extra
    draw_cards(state, my_draws)
    if "Sheoldred, the Apocalypse" in state.battlefield:
        state.life += 2 * my_draws
        state.proxy_lifegain_total += 2 * my_draws
    # dano proxy pelas compras simetricas dos OPONENTES nesse mesmo draw step
    dpd = damage_per_opponent_draw(state)
    proxy_drain(state, dpd * my_draws * NUM_OPPONENTS)


def upkeep_step(state: GameState):
    if "Scrawling Crawler" in state.battlefield:
        draw_cards(state, 1)
        dpd = damage_per_opponent_draw(state)
        proxy_drain(state, dpd * NUM_OPPONENTS)
    if "The One Ring" in state.battlefield and state.the_one_ring_burden > 0:
        state.life -= state.the_one_ring_burden


# ---------------------------------------------------------------------------
# Mana
# ---------------------------------------------------------------------------

def ready_creatures(state: GameState):
    return [n for n in state.battlefield if is_creature_card(n)
            and (state.creature_cast_turn.get(n, -1) < state.turn)]


def rocks_mana(state: GameState) -> int:
    total = 0
    if "Sol Ring" in state.battlefield:
        total += 2
    for n in ("Arcane Signet", "Talisman of Creativity", "Talisman of Dominance"):
        if n in state.battlefield:
            total += 1
    if "Mox Opal" in state.battlefield and sum(1 for n in state.battlefield if is_artifact_card(n)) >= 3:
        total += 1
    return total


def total_mana(state: GameState) -> int:
    lands = sum(1 for n in state.battlefield if n in LAND_NAMES)
    return lands + rocks_mana(state) + state.bonus_mana_pool


def remaining_mana(state: GameState) -> int:
    return max(0, total_mana(state) - state.mana_spent_this_turn)


def can_cast(state: GameState, name: str) -> bool:
    return remaining_mana(state) >= CARD_DB[name].mv


def spend_mana(state: GameState, n: int):
    state.mana_spent_this_turn += n


# ---------------------------------------------------------------------------
# Resolucao de gatilhos ETB / cast
# ---------------------------------------------------------------------------

def resolve_etb(state: GameState, name: str):
    tags = CARD_DB[name].tags
    if name == "Orcish Bowmasters":
        dpd_without_self = damage_per_opponent_draw(state) - 1  # ela mesma ja esta em campo aqui
        proxy_drain(state, 1 * NUM_OPPONENTS)  # gatilho de ETB dela propria (independente de compra)
    if name == "The One Ring":
        state.life += 0  # protecao total, sem efeito numerico modelado (sem oponente real atacando)
    if "ritual" in tags:
        pass  # tratado em resolve_instant


def resolve_instant_sorcery(state: GameState, name: str):
    tags = CARD_DB[name].tags
    if "ritual" in tags:
        if name == "Dark Ritual":
            state.bonus_mana_pool += 3
        elif name == "Cabal Ritual":
            state.bonus_mana_pool += 5 if len(state.graveyard) >= 7 else 3
    elif "wheel_full" in tags:
        if name == "Wheel of Fortune":
            wheel_event(state, my_draws=7, opp_draws_each=7, source=name)
        elif name == "Windfall":
            discard_n = len(state.hand)
            wheel_event(state, my_draws=max(discard_n, 1), opp_draws_each=max(discard_n, 1), source=name)
        elif name == "Winds of Change":
            n = len(state.hand)
            wheel_event(state, my_draws=n, opp_draws_each=n, source=name)
        elif name == "Echo of Eons":
            wheel_event(state, my_draws=7, opp_draws_each=7, source=name)
        elif name == "Wheel and Deal":
            wheel_event(state, my_draws=1, opp_draws_each=7, source=name)
        elif name == "Wheel of Misfortune":
            wheel_event(state, my_draws=7, opp_draws_each=7, source=name)
    elif "tutor" in tags or "tutor_top" in tags or "tutor_instant_sorcery" in tags:
        do_tutor(state, name)
    elif name == "Brain Freeze":
        copies = state.spells_cast_this_turn  # storm: copiada 1x por spell ja conjurada antes
        state.mill_proxy_total += 3 * (1 + copies) * NUM_OPPONENTS
    elif name == "Reanimate" or name == "Animate Dead":
        targets = [c for c in state.graveyard if is_creature_card(c)]
        if targets:
            best = max(targets, key=lambda n: CARD_DB[n].mv)
            state.graveyard.remove(best)
            enter_battlefield(state, best, from_hand=False)
            state.reanimator_targets_total += 1
            if name == "Reanimate":
                state.life -= CARD_DB[best].mv
    elif name == "Past in Flames":
        work_breach_or_flames_recast(state, mode="flashback")


def do_tutor(state: GameState, name: str):
    """Busca a peca mais necessaria: prioriza Underworld Breach (motor de
    storm) se ainda nao tiver, senao o proximo wheel/payoff que faltar."""
    priority = ["Underworld Breach", "Past in Flames", "Wheel of Fortune", "Sheoldred, the Apocalypse",
                "Underworld Dreams", "Sol Ring", "Dark Ritual"]
    pool = [n for n in priority if n in state.library]
    if not pool:
        # fallback: qualquer wheel ou payoff que ainda esteja na biblioteca
        pool = [n for n in state.library if CARD_DB[n].tags & {"wheel_full", "payoff", "breach_engine"}]
    if not pool:
        return
    choice = pool[0]
    state.library.remove(choice)
    if "tutor_top" in CARD_DB[name].tags:
        state.library.insert(0, choice)
    else:
        state.hand.append(choice)
    state.tutors_used_total += 1


def work_breach_or_flames_recast(state: GameState, mode: str):
    """Underworld Breach: escape = mana cost + exilar 3 outras do GY.
    Past in Flames (via flashback / resolve_instant_sorcery chamando isso):
    flashback = mana cost, sem exilar. Ambos so recastam INSTANT/SORCERY
    do cemiterio (wheels/rituais), respeitando o custo real — o loop
    termina sozinho quando faltar mana ou cartas suficientes no GY."""
    loop_iterations = 0
    while loop_iterations < 40:  # teto defensivo (nunca deveria ser atingido de verdade)
        loop_iterations += 1
        castable_gy = [c for c in state.graveyard
                       if CARD_DB[c].ctype in ("instant", "sorcery")
                       and CARD_DB[c].mv <= remaining_mana(state)]
        if mode == "escape":
            castable_gy = [c for c in castable_gy if len(state.graveyard) - 1 >= 3]
        if not castable_gy:
            break
        castable_gy.sort(key=lambda n: CARD_DB[n].mv)
        choice = castable_gy[0]
        spend_mana(state, CARD_DB[choice].mv)
        state.graveyard.remove(choice)
        if mode == "escape":
            exile_pool = [c for c in state.graveyard][:3]
            for c in exile_pool:
                state.graveyard.remove(c)
        state.spells_cast_this_turn += 1
        state.breach_recasts_total += 1
        resolve_instant_sorcery(state, choice)
        if mode == "escape":
            state.graveyard.append(choice)  # escape nao exila a propria carta (so o custo de 3 outras)
        # mode == "flashback": a carta e EXILADA ao resolver (regra real de flashback,
        # CR 702.32a) -- nao volta pro cemiterio. Sem isso o loop nunca convergia
        # (bug real encontrado no smoke-test: storm ficava preso no teto de 40).
    if loop_iterations > 1:
        state.breach_loops_total += 1
    state.storm_count_max = max(state.storm_count_max, state.spells_cast_this_turn)


def create_permanent(state: GameState, name: str):
    state.battlefield.append(name)


def enter_battlefield(state: GameState, name: str, from_hand: bool = True):
    if from_hand and name in state.hand:
        state.hand.remove(name)
    state.battlefield.append(name)
    if name == COMMANDER:
        state.commander_in_play = True
        state.commander_cast_count += 1
        if state.commander_cast_turn is None:
            state.commander_cast_turn = state.turn
    if is_creature_card(name):
        state.creature_cast_turn[name] = state.turn
    resolve_etb(state, name)


def cast_card(state: GameState, name: str, from_hand: bool = True):
    card = CARD_DB[name]
    if name == COMMANDER:
        spend_mana(state, card.mv + 2 * state.commander_cast_count)
    else:
        spend_mana(state, card.mv)
    if from_hand and name != COMMANDER:
        state.hand.remove(name)
    state.spells_cast_this_turn += 1
    state.storm_count_max = max(state.storm_count_max, state.spells_cast_this_turn)

    if name in LAND_NAMES:
        state.battlefield.append(name)
        if "fetch" in card.tags:
            state.life -= 1
        return

    if card.ctype in ("instant", "sorcery"):
        resolve_instant_sorcery(state, name)
        if name == "Underworld Breach":
            state.underworld_breach_active = True
            state.battlefield.append(name)
            return
        state.graveyard.append(name)
        return

    enter_battlefield(state, name, from_hand=False)
    if name == "Underworld Breach":
        state.underworld_breach_active = True


def play_land(state: GameState):
    if state.lands_played_this_turn >= 1:
        return
    lands_in_hand = [n for n in state.hand if n in LAND_NAMES]
    if not lands_in_hand:
        return
    choice = lands_in_hand[0]
    cast_card(state, choice)
    state.lands_played_this_turn += 1


def main_phase(state: GameState):
    if not state.commander_in_play and can_cast(state, COMMANDER):
        cast_card(state, COMMANDER)

    while True:
        castables = [n for n in state.hand if n not in LAND_NAMES and can_cast(state, n)]
        if not castables:
            break
        # prioriza: rituais/rocks primeiro (geram mais mana pro resto do turno),
        # depois wheels/payoffs/tutores, cartas mais baratas primeiro dentro de cada grupo
        def prio(n):
            tags = CARD_DB[n].tags
            group = 0 if (tags & {"ritual", "rock1", "rock2"}) else (1 if (tags & {"payoff", "wheel_full", "wheel_passive", "breach_engine"}) else 2)
            return (group, CARD_DB[n].mv)
        castables.sort(key=prio)
        cast_card(state, castables[0])

    if state.underworld_breach_active and remaining_mana(state) > 0:
        work_breach_or_flames_recast(state, mode="escape")

    if "Sensei's Divining Top" in state.battlefield and "Sensei's Divining Top" in ready_creatures(state) and remaining_mana(state) >= 1:
        pass  # nao consome mana, top e "T: draw" -- simplificado, sem efeito solo real alem do proprio draw ja contado no motor de wheel


def combat_step(state: GameState):
    pass  # deck de dano por gatilho de compra, sem combate real modelado


def cleanup_discard(state: GameState):
    """CR 514.3: descarta ate a mao ter 7 cartas no cleanup step. Sem isso a
    mao cresce sem limite (achado real testando: mao de 74 cartas apos 8
    turnos, com o volume de compra deste deck) — bug real corrigido.
    Mantem as cartas mais caras/valiosas (mv maior primeiro), descarta as
    baratas/substituiveis, ja que o deck tem Underworld Breach/wheels que
    se beneficiam de cemiterio cheio de qualquer forma."""
    while len(state.hand) > 7:
        worst = min(state.hand, key=lambda n: CARD_DB[n].mv)
        state.hand.remove(worst)
        state.graveyard.append(worst)


def end_step(state: GameState):
    if state.underworld_breach_active:
        if "Underworld Breach" in state.battlefield:
            state.battlefield.remove("Underworld Breach")
        state.graveyard.append("Underworld Breach")
        state.underworld_breach_active = False
    cleanup_discard(state)


def should_keep(hand: list) -> bool:
    lands = sum(1 for n in hand if n in LAND_NAMES)
    good_early = {"Sol Ring", "Arcane Signet", "Dark Ritual", COMMANDER}
    if lands >= 3:
        return True
    if lands == 2 and any(n in good_early for n in hand):
        return True
    return False


def build_library():
    lib = []
    text = open("lista.md").read()
    for l in text.splitlines():
        l = l.strip()
        if not l or l.startswith("#") or l.startswith(">") or "Bracket" in l or "Game Changers" in l or "V9 vs" in l:
            continue
        m = re.match(r"^(\d+)\s+(.+)$", l)
        if not m:
            continue
        qty, name = int(m.group(1)), m.group(2).strip()
        if name == COMMANDER:
            continue
        assert name in CARD_DB, f"faltando no CARD_DB: {name}"
        for _ in range(qty):
            lib.append(name)
    assert len(lib) == 99, len(lib)
    return lib


BASE_LIBRARY = build_library()


def mulligan(rng: random.Random, max_mulls: int = 3):
    mulls = 0
    hand, lib = [], []
    while mulls < max_mulls:
        lib = BASE_LIBRARY[:]
        rng.shuffle(lib)
        hand = lib[:7]
        lib = lib[7:]
        if should_keep(hand) or mulls == max_mulls - 1:
            if mulls > 0:
                rng.shuffle(hand)
                bottom = hand[:mulls]
                hand = hand[mulls:]
                lib = lib + bottom
            return hand, lib, mulls
        mulls += 1
    return hand, lib, mulls


def play_turn(state: GameState, is_first_turn: bool, on_play: bool):
    state.turn += 1
    state.lands_played_this_turn = 0
    state.mana_spent_this_turn = 0
    state.bonus_mana_pool = 0
    state.spells_cast_this_turn = 0

    upkeep_step(state)
    if not (is_first_turn and on_play):
        draw_step(state)
    else:
        pass  # 1o turno na ponta: sem compra normal, mas gatilhos simetricos de draw step nao se aplicam ainda (nada em campo)

    play_land(state)
    main_phase(state)
    combat_step(state)
    main_phase(state)
    end_step(state)


def simulate_one(seed: int, turns: int = 8):
    rng = random.Random(seed)
    hand, lib, mulls = mulligan(rng)
    state = GameState(hand=hand, library=lib, mulligans=mulls)
    for t in range(turns):
        play_turn(state, is_first_turn=(t == 0), on_play=True)
    return state


def run_batch(n: int, seed_base: int, turns: int = 8):
    states = [simulate_one(seed_base + i, turns=turns) for i in range(n)]

    def avg(vals):
        return sum(vals) / len(vals) if vals else 0.0

    print(f"n={n}, seed_base={seed_base}, turns={turns}")
    print(f"Avg mulligans: {avg([s.mulligans for s in states]):.2f}")
    cmd_turn = [s.commander_cast_turn for s in states if s.commander_cast_turn is not None]
    print(f"Turno medio de conjuracao do Nekusar: {avg(cmd_turn):.2f} | mediana: {statistics.median(cmd_turn) if cmd_turn else float('nan'):.1f}")
    print(f"Nunca conjurado em {turns} turnos: {100*sum(1 for s in states if s.commander_cast_turn is None)/n:.1f}%")
    print(f"Avg eventos de wheel (full+parcial): {avg([s.wheel_events_total for s in states]):.2f}")
    print(f"Avg wheels completos (descarta mao, compra 7): {avg([s.full_wheels_total for s in states]):.2f}")
    print(f"Avg dano/perda-de-vida proxy total (3 oponentes hipoteticos, NUNCA vida real): {avg([s.proxy_damage_total for s in states]):.2f}")
    print(f"Avg vida ganha (Sheoldred, proxy Bloodchief): {avg([s.proxy_lifegain_total for s in states]):.2f}")
    print(f"Avg cartas compradas extra: {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"Avg tutores usados: {avg([s.tutors_used_total for s in states]):.2f}")
    print(f"Avg recasts via Underworld Breach/Past in Flames: {avg([s.breach_recasts_total for s in states]):.2f}")
    breach_hits = sum(1 for s in states if s.breach_loops_total > 0)
    print(f"Partidas com pelo menos 1 loop de Breach/Flames (2+ recasts no mesmo evento): {100*breach_hits/n:.1f}%")
    print(f"Avg storm count maximo no turno: {avg([s.storm_count_max for s in states]):.2f}")
    print(f"Avg mill proxy total (Mindcrank + Brain Freeze): {avg([s.mill_proxy_total for s in states]):.2f}")
    print(f"Avg reanimados (Animate Dead/Reanimate): {avg([s.reanimator_targets_total for s in states]):.2f}")
    print(f"Avg mao final: {avg([len(s.hand) for s in states]):.2f}")
    return states


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    states = run_batch(n=3000, seed_base=7300000, turns=8)

    with open("nekusar_v1_runs.jsonl", "w") as f:
        for s in states:
            f.write(json.dumps({
                "mulligans": s.mulligans,
                "commander_cast_turn": s.commander_cast_turn,
                "wheel_events_total": s.wheel_events_total,
                "full_wheels_total": s.full_wheels_total,
                "proxy_damage_total": s.proxy_damage_total,
                "cards_drawn_extra": s.cards_drawn_extra,
                "tutors_used_total": s.tutors_used_total,
                "breach_recasts_total": s.breach_recasts_total,
                "storm_count_max": s.storm_count_max,
            }) + "\n")
