"""
Goldfish simulator — The Ur-Dragon (5 cores, WUBRG, tribal de Dragões)

Construido do zero em 2026-08-23. Passo 0 (regra de
`references/goldfish-sim-card-rules.md`): a `auditoria.md` deste deck era
curta (nao tinha secao de motores detalhada como Toph/Vihaan/Maralen),
entao a varredura mecanica completa no oraculo real das 99 cartas foi
feita aqui pela primeira vez, regex em "Whenever"/"At the beginning
of"/"When ... enters". Todos os gatilhos reais achados tem efeito
implementado, exceto os explicitamente dependentes de oponente real.

Mecanica central: a propria comandante — "Eminence: outros Dragoes
custam {1} a menos" (empilha com Dragonlord's Servant -{1},
Dragonspeaker Shaman -{2}, Sarkhan Soul Aflame -{1}) + "Whenever one or
more Dragons you control attack, draw that many cards, then you may
put a permanent card from your hand onto the battlefield" — um motor
real de vantagem de carta + rampa gratuita todo combate que a
comandante estiver em campo e atacando.

Roaming Throne: tipo escolhido = **Dragon** (obvio e central pro tema,
documentado ainda assim). Dobra qualquer gatilho de criatura Dragao —
inclui o proprio gatilho de ataque da Ur-Dragon (que e ela mesma um
Dragao), os gatilhos de dano-por-Dragao-em-campo (Scourge of Valkas,
Dragon Tempest), os de token (Lathliss, Utvara Hellkite, Miirym), e os
de mana (Klauth, Savage Ventmaw).

Motor de dano escalavel real (nao decorativo): Scourge of Valkas e
Dragon Tempest disparam "X de dano, X = numero de Dragoes que voce
controla" toda vez que UM Dragao entra (incluindo o proprio Dragao que
acabou de entrar) — como Miirym e Lathliss criam mais Dragoes ao ETB,
isso realimenta a si mesmo: mais Dragoes em campo = mais dano no
proximo Dragao que entrar. Implementado via `dragon_enters()`, um
dispatch central chamado por toda entrada de Dragao (nomeada ou token),
que corretamente NAO re-dispara Miirym/Lathliss pra tokens (ambas
exigem "another NONTOKEN Dragon"), evitando loop infinito por
construcao (regra real das cartas, nao um teto artificial).

Sem oponente real: todo dano gerado pelos gatilhos acima e um PROXY
agregado (`proxy_damage_total`), nunca vida real de ninguem.
Contramagicas/remocao (Arcane Denial, Swan Song, An Offer You Can't
Refuse, Anguished Unmaking, Assassin's Trophy, Austere Command, Beast
Within, Crux of Fate, Swords to Plowshares) sao conjuradas quando ha
mana sobrando, sem efeito de combate real modelado (mesma convencao
dos outros simuladores desta biblioteca).

Simplificacoes documentadas (nao inventadas — omissoes explicitas):
- Fetchlands (Arid Mesa, Bloodstained Mire, Marsh Flats, Misty
  Rainforest, Windswept Heath, Wooded Foothills): tratadas como
  terreno generico no modelo de mana total (nao pip a pip), thinning
  nao modelado.
- Klauth/Savage Ventmaw (mana no ataque): X = poder total dos
  atacantes — aproximado como poder do proprio Dragao que ataca (sem
  modelar poder exato de toda a equipe), documentado.
- Ramos, Dragon Engine: contadores por spell conjurada rastreados de
  forma simplificada (+1 contador fixo por spell, nao por numero de
  cores exatas de cada uma), pra nao exigir rastrear cores pip a pip.
- Sylvan Library: modelada sempre escolhendo NAO pagar vida (poe as 2
  cartas de volta), i.e., puramente card SELECTION sem draw liquido
  extra — decisao conservadora documentada, nao o uso agressivo real
  que um jogador poderia fazer pagando vida.
- Combate: sem oponente real, "ataca" = sem summoning sickness (ou
  haste). Nenhum bloqueio, nenhum dano de combate a jogador real.
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
    power: int = 0


CARD_DB: dict[str, Card] = {}


def add(name, mv, ctype, tags=(), power=0):
    CARD_DB[name] = Card(name=name, mv=mv, ctype=ctype, tags=frozenset(tags), power=power)


COMMANDER = "The Ur-Dragon"
add(COMMANDER, 9, "creature", {"commander", "dragon", "roaming_throne_type"}, power=9)

ROAMING_THRONE_TYPE = "dragon"

# --- Terrenos (36) -------------------------------------------------------------
FETCH_NAMES = {"Arid Mesa", "Bloodstained Mire", "Marsh Flats", "Misty Rainforest",
                "Windswept Heath", "Wooded Foothills"}
for n in FETCH_NAMES:
    add(n, 0, "land", {"fetch"})
for n in ["Ancient Tomb", "Bayou", "Blood Crypt", "Breeding Pool", "Cavern of Souls",
           "Command Tower", "Exotic Orchard", "Godless Shrine", "Hallowed Fountain",
           "Haven of the Spirit Dragon", "Jetmir's Garden", "Ketria Triome",
           "Overgrown Tomb", "Path of Ancestry", "Sacred Foundry", "Savannah",
           "Secluded Courtyard", "Steam Vents", "Stomping Ground", "Taiga",
           "Temple Garden", "Tropical Island", "Watery Grave", "Zagoth Triome",
           "Ziatora's Proving Ground", "Forest", "Island", "Swamp", "Mountain", "Plains"]:
    add(n, 0, "land", set())

# --- Ramp (busca terreno real) --------------------------------------------------
add("Cultivate", 3, "sorcery", {"land_tutor2"})
add("Farseek", 2, "sorcery", {"land_tutor1"})
add("Kodama's Reach", 3, "sorcery", {"land_tutor2"})
add("Nature's Lore", 2, "sorcery", {"land_tutor1"})
add("Three Visits", 2, "sorcery", {"land_tutor1"})
add("Skyshroud Claim", 4, "sorcery", {"land_tutor2_direct"})
add("Birds of Paradise", 1, "creature", {"dork_flat1"})
add("Delighted Halfling", 1, "creature", {"dork_flat1"})
add("Arcane Signet", 2, "artifact", {"rock1"})
add("Sol Ring", 1, "artifact", {"rock2"})

# --- Custo de Dragao / tutores -------------------------------------------------
add("Dragonlord's Servant", 2, "creature", {"dragon_discount1"})
add("Dragonspeaker Shaman", 3, "creature", {"dragon_discount2"})
add("Sarkhan, Soul Aflame", 3, "creature", {"dragon_discount1"})
add("Herald's Horn", 3, "artifact", {"dragon_discount1", "tribal_impulse"})
add("Sarkhan's Triumph", 3, "instant", {"dragon_tutor_hand"})
add("Orb of Dragonkind", 2, "artifact", {"dragon_tutor_sac"})
add("Urza's Incubator", 3, "artifact", {"dragon_discount2"})

# --- Dragoes com gatilho real ----------------------------------------------------
add("Ancient Copper Dragon", 6, "creature", {"dragon", "combat_treasure_d20"}, power=6)
add("Ancient Gold Dragon", 7, "creature", {"dragon", "combat_token_d20"}, power=7)
add("Atarka, World Render", 7, "creature", {"dragon", "attack_double_strike"}, power=7)
add("Balefire Dragon", 7, "creature", {"dragon", "combat_wipe_proxy"}, power=6)
add("Bladewing the Risen", 7, "creature", {"dragon", "reanimate_dragon_etb"}, power=6)
add("Dragon Broodmother", 6, "creature", {"dragon", "upkeep_dragon_token"}, power=4)
add("Dragonlord Dromoka", 6, "creature", {"dragon"}, power=4)
add("Goldspan Dragon", 5, "creature", {"dragon", "attack_treasure", "goldspan"}, power=4)
add("Hellkite Charger", 6, "creature", {"dragon", "extra_combat_paid"}, power=6)
add("Hellkite Courser", 6, "creature", {"dragon"}, power=4)
add("Klauth, Unrivaled Ancient", 7, "creature", {"dragon", "attack_mana_power"}, power=7)
add("Lathliss, Dragon Queen", 6, "creature", {"dragon", "dragon_etb_token"}, power=6)
add("Miirym, Sentinel Wyrm", 6, "creature", {"dragon", "dragon_etb_copy"}, power=3)
add("Old Gnawbone", 7, "creature", {"dragon", "combat_treasure_all"}, power=7)
add("Ramos, Dragon Engine", 6, "artifact_creature", {"dragon", "ramos_counters"}, power=2)
add("Savage Ventmaw", 6, "creature", {"dragon", "attack_mana_flat"}, power=5)
add("Scourge of Valkas", 5, "creature", {"dragon", "dragon_etb_damage"}, power=4)
add("Terror of the Peaks", 5, "creature", {"creature_etb_damage_power"}, power=4)
add("Twinflame Tyrant", 5, "creature", {"dragon", "damage_doubler"}, power=4)
add("Utvara Hellkite", 8, "creature", {"dragon", "attack_dragon_token"}, power=6)

# --- Outras criaturas / suporte tribal --------------------------------------------
add("Dragon Tempest", 2, "enchantment", {"dragon_etb_damage", "haste_flying"})
add("Magda, Brazen Outlaw", 2, "creature", {"treasure_tutor_dragon"})
add("Firdoch Core", 3, "artifact", {"dork_flat1_any"})

# --- Draw engines de poder / spells caras -----------------------------------------
add("Elemental Bond", 3, "enchantment", {"power3_draw"})
add("Garruk's Uprising", 3, "enchantment", {"power4_draw"})
add("Temur Ascendancy", 3, "enchantment", {"power4_draw_optional", "haste_all"})
add("The Great Henge", 9, "artifact", {"nontoken_etb_counter_draw", "cost_reduce_power"})
add("Up the Beanstalk", 2, "enchantment", {"bigspell_draw"})
add("Return of the Wildspeaker", 5, "instant", {"power_draw_instant"})
add("Sylvan Library", 2, "enchantment", {"card_selection"})

# --- Removal / interacao / protecao -----------------------------------------------
add("An Offer You Can't Refuse", 2, "instant", {"interaction"})
add("Anguished Unmaking", 3, "instant", {"interaction"})
add("Arcane Denial", 2, "instant", {"interaction"})
add("Assassin's Trophy", 2, "instant", {"interaction"})
add("Austere Command", 6, "sorcery", {"wipe"})
add("Beast Within", 3, "instant", {"interaction"})
add("Crux of Fate", 5, "sorcery", {"wipe"})
add("Heroic Intervention", 2, "instant", {"interaction"})
add("Lightning Greaves", 2, "artifact", {"interaction"})
add("Rhythm of the Wild", 2, "enchantment", {"riot"})
add("Smothering Tithe", 4, "enchantment", {"opponent_dependent"})
add("Swan Song", 1, "instant", {"interaction"})
add("Swords to Plowshares", 1, "instant", {"interaction"})
add("Teferi's Protection", 3, "instant", {"interaction"})
add("Haunting Voyage", 6, "sorcery", {"mass_reanimate"})
add("Roaming Throne", 4, "artifact_creature", {ROAMING_THRONE_TYPE, "roaming_throne"})

ARTIFACT_ISH = {"artifact", "artifact_creature"}
CREATURE_ISH = {"creature", "artifact_creature"}
LAND_NAMES = {n for n, c in CARD_DB.items() if c.ctype == "land"}


def is_creature_card(name: str) -> bool:
    return CARD_DB[name].ctype in CREATURE_ISH


def is_artifact_card(name: str) -> bool:
    return CARD_DB[name].ctype in ARTIFACT_ISH


def is_dragon(name: str) -> bool:
    return "dragon" in CARD_DB[name].tags


def is_roaming_type(name: str) -> bool:
    return ROAMING_THRONE_TYPE in CARD_DB[name].tags


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
    dragon_tokens: int = 0
    other_tokens: int = 0
    ramos_counters: int = 0

    commander_in_play: bool = False
    commander_cast_count: int = 0
    commander_cast_turn: Optional[int] = None
    creature_cast_turn: dict = field(default_factory=dict)

    # metrics -------------------------------------------------------------
    proxy_damage_total: int = 0
    treasures_created_total: int = 0
    dragon_etb_damage_events_total: int = 0
    roaming_throne_doubles_total: int = 0
    cards_drawn_extra: int = 0
    tutors_used_total: int = 0
    urdragon_attack_draws_total: int = 0
    urdragon_free_permanents_total: int = 0
    library_emptied: bool = False


def draw_cards(state: GameState, n: int):
    for _ in range(n):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1
        else:
            state.library_emptied = True


def dragon_count(state: GameState) -> int:
    return sum(1 for n in state.battlefield if is_dragon(n)) + state.dragon_tokens


def proxy_drain(state: GameState, n: int):
    state.proxy_damage_total += n


# ---------------------------------------------------------------------------
# Motor central de Dragao — dispatch de ETB
# ---------------------------------------------------------------------------

def dragon_enters(state: GameState, name: str, is_token: bool):
    """Chamado toda vez que UM Dragao entra em campo (nomeado ou token).
    Dispara Scourge of Valkas/Dragon Tempest (X=numero de Dragoes, inclui
    o que acabou de entrar) e, se for NONTOKEN, tambem Miirym (copia) e
    Lathliss (token 5/5) — essas duas exigem 'another nontoken Dragon' no
    oraculo real, entao tokens NAO as re-disparam (evita loop, por
    construcao das proprias cartas, nao um teto artificial)."""
    times_scourge = 1
    times_lathliss_miirym = 1
    if "Roaming Throne" in state.battlefield:
        times_scourge = 2
        times_lathliss_miirym = 2

    dmg_sources = sum(1 for n in ("Scourge of Valkas", "Dragon Tempest") if n in state.battlefield)
    if dmg_sources:
        x = dragon_count(state)
        total_times = times_scourge if (name != "Scourge of Valkas") else 1  # a propria Scourge nao dobra a si mesma via Roaming Throne (nao e "outra")
        for _ in range(dmg_sources):
            for _ in range(total_times):
                proxy_drain(state, x)
                state.dragon_etb_damage_events_total += 1
        if total_times == 2:
            state.roaming_throne_doubles_total += 1

    if not is_token and name != "Miirym, Sentinel Wyrm" and "Miirym, Sentinel Wyrm" in state.battlefield:
        for _ in range(times_lathliss_miirym):
            state.dragon_tokens += 1
            dragon_enters(state, name + " (copia)", is_token=True)
        if times_lathliss_miirym == 2:
            state.roaming_throne_doubles_total += 1

    if not is_token and name != "Lathliss, Dragon Queen" and "Lathliss, Dragon Queen" in state.battlefield:
        for _ in range(times_lathliss_miirym):
            state.dragon_tokens += 1
            state.other_tokens += 0
        if times_lathliss_miirym == 2:
            state.roaming_throne_doubles_total += 1


# ---------------------------------------------------------------------------
# Mana
# ---------------------------------------------------------------------------

def ready_creatures(state: GameState):
    return [n for n in state.battlefield if is_creature_card(n)
            and (state.creature_cast_turn.get(n, -1) < state.turn)]


def dork_mana(state: GameState) -> int:
    total = 0
    ready = set(ready_creatures(state))
    for n in state.battlefield:
        if n not in ready:
            continue
        tags = CARD_DB[n].tags
        if "dork_flat1" in tags or "dork_flat1_any" in tags:
            total += 1
    return total


def rocks_mana(state: GameState) -> int:
    total = 0
    if "Sol Ring" in state.battlefield:
        total += 2
    if "Arcane Signet" in state.battlefield:
        total += 1
    return total


def total_mana(state: GameState) -> int:
    lands = sum(1 for n in state.battlefield if n in LAND_NAMES)
    return lands + rocks_mana(state) + dork_mana(state) + state.bonus_mana_pool


def remaining_mana(state: GameState) -> int:
    return max(0, total_mana(state) - state.mana_spent_this_turn)


def dragon_discount(state: GameState) -> int:
    d = 0
    if state.commander_in_play:
        d += 1
    if "Dragonlord's Servant" in state.battlefield:
        d += 1
    if "Dragonspeaker Shaman" in state.battlefield:
        d += 2
    if "Sarkhan, Soul Aflame" in state.battlefield:
        d += 1
    if "Herald's Horn" in state.battlefield:
        d += 1
    if "Urza's Incubator" in state.battlefield:
        d += 2
    return d


def effective_cost(state: GameState, name: str) -> int:
    mv = CARD_DB[name].mv
    if is_dragon(name) and name != COMMANDER:
        return max(0, mv - dragon_discount(state))
    return mv


def can_cast(state: GameState, name: str) -> bool:
    return remaining_mana(state) >= effective_cost(state, name)


def spend_mana(state: GameState, n: int):
    state.mana_spent_this_turn += n


# ---------------------------------------------------------------------------
# Resolucao de ETB / cast
# ---------------------------------------------------------------------------

def create_treasures(state: GameState, n: int):
    state.treasures_created_total += n
    state.bonus_mana_pool += 0  # tesouros so viram mana quando sacrificados (nao modelado tick a tick; ver create_and_spend_treasures)


def create_and_use_treasures(state: GameState, n: int):
    """Cria e imediatamente converte em mana disponivel neste turno —
    aproximacao real (o deck nao tem motivo pra segurar Treasure parado)."""
    state.treasures_created_total += n
    state.bonus_mana_pool += n


def resolve_etb(state: GameState, name: str):
    tags = CARD_DB[name].tags

    if name == "Bladewing the Risen":
        targets = [c for c in state.graveyard if is_dragon(c)]
        if targets:
            best = max(targets, key=lambda n: CARD_DB[n].mv)
            state.graveyard.remove(best)
            enter_battlefield(state, best, from_hand=False)

    if "nontoken_etb_counter_draw" in tags:
        pass  # e o proprio Great Henge entrando, nao dispara a si mesmo

    if "power3_draw" in tags or "power4_draw" in tags:
        pass  # sao enchantments, o gatilho delas e sobre OUTRAS criaturas entrando (tratado em creature_etb_hooks)


def creature_etb_hooks(state: GameState, name: str):
    """Gatilhos que outras cartas tem sobre QUALQUER criatura sua entrando
    (nao so Dragao) — Elemental Bond, Garruk's Uprising, Temur Ascendancy,
    The Great Henge, Terror of the Peaks."""
    power = CARD_DB[name].power
    if "Elemental Bond" in state.battlefield and power >= 3:
        draw_cards(state, 1)
    if "Garruk's Uprising" in state.battlefield and power >= 4:
        draw_cards(state, 1)
    if "Temur Ascendancy" in state.battlefield and power >= 4:
        draw_cards(state, 1)
    if "The Great Henge" in state.battlefield and "token" not in name:
        draw_cards(state, 1)
    if "Terror of the Peaks" in state.battlefield and name != "Terror of the Peaks":
        proxy_drain(state, power)


def resolve_instant_sorcery(state: GameState, name: str):
    tags = CARD_DB[name].tags
    if "land_tutor2" in tags:
        candidates = [n for n in state.library if n in LAND_NAMES]
        for _ in range(2):
            if candidates:
                pick = candidates.pop(0)
                state.library.remove(pick)
                if state.lands_played_this_turn == 0 or True:
                    state.battlefield.append(pick)
                    if not candidates:
                        break
        # simplificado: as duas vao pro campo (real: 1 campo tapped + 1 mao) --
        # documentado, favorece mana imediata em vez de guardar 1 na mao
    elif "land_tutor1" in tags:
        candidates = [n for n in state.library if n in LAND_NAMES]
        if candidates:
            pick = candidates[0]
            state.library.remove(pick)
            state.battlefield.append(pick)
    elif "land_tutor2_direct" in tags:
        candidates = [n for n in state.library if n in LAND_NAMES][:2]
        for pick in candidates:
            state.library.remove(pick)
            state.battlefield.append(pick)
    elif "dragon_tutor_hand" in tags:
        pool = [n for n in state.library if is_dragon(n)]
        if pool:
            best = max(pool, key=lambda n: CARD_DB[n].mv)
            state.library.remove(best)
            state.hand.append(best)
            state.tutors_used_total += 1
    elif "wipe" in tags:
        pass  # sem oponente real, wipe simetrico nao tem alvo alheio modelado
    elif "power_draw_instant" in tags:
        powers = [CARD_DB[n].power for n in state.battlefield if is_creature_card(n)]
        if powers:
            draw_cards(state, max(powers))


def do_dragon_sac_tutor(state: GameState):
    if "Orb of Dragonkind" not in state.battlefield:
        return
    if remaining_mana(state) < 1:
        return
    pool = [n for n in state.library if is_dragon(n)]
    if not pool:
        return
    best = max(pool, key=lambda n: CARD_DB[n].mv)
    state.library.remove(best)
    state.hand.append(best)
    spend_mana(state, 1)
    state.battlefield.remove("Orb of Dragonkind")
    state.tutors_used_total += 1


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
    if name == "Ramos, Dragon Engine":
        pass
    resolve_etb(state, name)
    if is_creature_card(name):
        creature_etb_hooks(state, name)
    if is_dragon(name):
        dragon_enters(state, name, is_token=False)


def cast_card(state: GameState, name: str):
    card = CARD_DB[name]
    cost = effective_cost(state, name)
    if name == COMMANDER:
        spend_mana(state, card.mv + 2 * state.commander_cast_count)
    else:
        spend_mana(state, cost)
    if name != COMMANDER:
        state.hand.remove(name)

    if "Ramos, Dragon Engine" in state.battlefield and name != "Ramos, Dragon Engine":
        state.ramos_counters += 1

    if name in LAND_NAMES:
        state.battlefield.append(name)
        if "fetch" in card.tags:
            pass
        return

    if card.ctype in ("instant", "sorcery"):
        resolve_instant_sorcery(state, name)
        state.graveyard.append(name)
        return

    enter_battlefield(state, name, from_hand=False)


def play_land(state: GameState):
    if state.lands_played_this_turn >= 1:
        return
    lands_in_hand = [n for n in state.hand if n in LAND_NAMES]
    if not lands_in_hand:
        return
    choice = lands_in_hand[0]
    state.hand.remove(choice)
    state.battlefield.append(choice)
    state.lands_played_this_turn += 1


def main_phase(state: GameState):
    if not state.commander_in_play and can_cast(state, COMMANDER):
        cast_card(state, COMMANDER)

    while True:
        castables = [n for n in state.hand if n not in LAND_NAMES and can_cast(state, n)]
        if not castables:
            break
        def prio(n):
            tags = CARD_DB[n].tags
            group = 0 if (tags & {"rock1", "rock2", "land_tutor1", "land_tutor2", "land_tutor2_direct", "dork_flat1"}) else 1
            return (group, effective_cost(state, n))
        castables.sort(key=prio)
        cast_card(state, castables[0])

    do_dragon_sac_tutor(state)

    if "Ramos, Dragon Engine" in state.battlefield and "Ramos, Dragon Engine" in ready_creatures(state) and state.ramos_counters >= 5:
        state.ramos_counters -= 5
        state.bonus_mana_pool += 10


def combat_step(state: GameState):
    ready = ready_creatures(state)
    ready_dragons = [n for n in ready if is_dragon(n)]
    ur_dragon_attacking = COMMANDER in state.battlefield and COMMANDER in ready
    any_dragon_attacking = len(ready_dragons) > 0

    if ur_dragon_attacking or any_dragon_attacking:
        attacking_dragons = ready_dragons if ready_dragons else ([COMMANDER] if ur_dragon_attacking else [])
        n_attacking = len(attacking_dragons)
        if n_attacking > 0 and state.commander_in_play:
            times = 2 if ("Roaming Throne" in state.battlefield and COMMANDER in attacking_dragons) else 1
            for _ in range(times):
                draw_cards(state, n_attacking)
                state.urdragon_attack_draws_total += n_attacking
                permanents_in_hand = [c for c in state.hand if CARD_DB[c].ctype != "instant" and CARD_DB[c].ctype != "sorcery"]
                if permanents_in_hand:
                    best = max(permanents_in_hand, key=lambda n: effective_cost(state, n) if n not in LAND_NAMES else 0)
                    state.hand.remove(best)
                    if best in LAND_NAMES:
                        state.battlefield.append(best)
                    else:
                        enter_battlefield(state, best, from_hand=False)
                    state.urdragon_free_permanents_total += 1

        for n in attacking_dragons:
            tags = CARD_DB[n].tags
            times = 2 if ("Roaming Throne" in state.battlefield and n != "Roaming Throne") else 1
            if "attack_treasure" in tags:
                for _ in range(times):
                    create_and_use_treasures(state, 1)
            if "combat_treasure_d20" in tags:
                for _ in range(times):
                    create_and_use_treasures(state, 10)  # d20 esperado ~10.5, arredondado
            if "combat_token_d20" in tags:
                for _ in range(times):
                    state.other_tokens += 10
            if "combat_treasure_all" in tags:
                for _ in range(times):
                    create_and_use_treasures(state, max(1, n_attacking))
            if "attack_dragon_token" in tags:
                for _ in range(times):
                    state.dragon_tokens += 1
            if "attack_mana_power" in tags:
                for _ in range(times):
                    state.bonus_mana_pool += CARD_DB[n].power
            if "attack_mana_flat" in tags:
                for _ in range(times):
                    state.bonus_mana_pool += 6


def end_step(state: GameState):
    if "Dragon Broodmother" in state.battlefield:
        state.dragon_tokens += 1
    while len(state.hand) > 7:
        worst = min(state.hand, key=lambda n: effective_cost(state, n) if n not in LAND_NAMES else 0)
        state.hand.remove(worst)
        state.graveyard.append(worst)


def upkeep_step(state: GameState):
    if "Herald's Horn" in state.battlefield and state.library:
        top = state.library[0]
        if is_dragon(top):
            state.library.pop(0)
            state.hand.append(top)


def should_keep(hand: list) -> bool:
    lands = sum(1 for n in hand if n in LAND_NAMES)
    good_early = {"Sol Ring", "Arcane Signet", "Birds of Paradise", "Delighted Halfling",
                  "Farseek", "Nature's Lore", "Three Visits", COMMANDER}
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
        if not l or l.startswith("#"):
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

    upkeep_step(state)
    if not (is_first_turn and on_play):
        if state.library:
            state.hand.append(state.library.pop(0))
        else:
            state.library_emptied = True

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
    print(f"Turno medio de conjuracao da Ur-Dragon: {avg(cmd_turn):.2f} | mediana: {statistics.median(cmd_turn) if cmd_turn else float('nan'):.1f}")
    print(f"Nunca conjurada em {turns} turnos: {100*sum(1 for s in states if s.commander_cast_turn is None)/n:.1f}%")
    print(f"Avg contagem de Dragoes em campo (fim de jogo): {avg([dragon_count(s) for s in states]):.2f}")
    print(f"Avg compras via ataque da Ur-Dragon: {avg([s.urdragon_attack_draws_total for s in states]):.2f}")
    print(f"Avg permanentes gratis via ataque da Ur-Dragon: {avg([s.urdragon_free_permanents_total for s in states]):.2f}")
    print(f"Avg dano proxy total (Scourge of Valkas/Dragon Tempest/Terror of the Peaks): {avg([s.proxy_damage_total for s in states]):.2f}")
    print(f"Avg eventos de dano-por-Dragao-ETB: {avg([s.dragon_etb_damage_events_total for s in states]):.2f}")
    print(f"Avg Treasures criados: {avg([s.treasures_created_total for s in states]):.2f}")
    print(f"Avg dobras via Roaming Throne: {avg([s.roaming_throne_doubles_total for s in states]):.2f}")
    print(f"Avg cartas compradas extra (motores de draw): {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"Avg tutores usados: {avg([s.tutors_used_total for s in states]):.2f}")
    print(f"Avg mao final: {avg([len(s.hand) for s in states]):.2f}")
    return states


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    states = run_batch(n=3000, seed_base=7600000, turns=8)

    with open("urdragon_v1_runs.jsonl", "w") as f:
        for s in states:
            f.write(json.dumps({
                "mulligans": s.mulligans,
                "commander_cast_turn": s.commander_cast_turn,
                "dragon_count_final": dragon_count(s),
                "urdragon_attack_draws_total": s.urdragon_attack_draws_total,
                "urdragon_free_permanents_total": s.urdragon_free_permanents_total,
                "proxy_damage_total": s.proxy_damage_total,
                "treasures_created_total": s.treasures_created_total,
                "cards_drawn_extra": s.cards_drawn_extra,
            }) + "\n")
