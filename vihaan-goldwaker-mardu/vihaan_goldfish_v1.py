"""
Goldfish simulator — Vihaan, Goldwaker (Mardu, R/W/B)

Construido do zero em 2026-08-22. Passo 0 (regra de
`references/goldfish-sim-card-rules.md`, aplicada de forma ampla, nao so
pro Roaming Throne): varredura mecanica no oraculo completo achou 40
cartas com gatilho real ("Whenever"/"At the beginning of"/"When"). Cada
uma tem o efeito real implementado abaixo, exceto onde depende de um
oponente real (permanente/spell/vida adversaria) — documentado como
simplificacao explicita, nunca fingido.

Contexto: o usuario trouxe um script pronto (ChatGPT) pra essa mesma
decklist. Revisao encontrou problemas reais que impediram reaproveitar a
logica de jogo (mantive so a decklist, que ja bate com a auditoria):
1. Mana nunca era gasta de verdade — `pay_mana()` so descontava Treasure,
   terreno/rock eram recalculados do zero a cada carta conjurada, sem
   nunca subtrair o que ja tinha sido gasto no turno. Permitia conjurar
   mais mágicas do que a mana real do turno pagaria.
2. Um "combo" Jan Jansen + Ashnod's Altar + Pitiless Plunderer que nao
   existe de verdade (as duas habilidades da Jan Jansen custam {T}, sem
   forma de destapar — no maximo 1 ativacao de cada por turno, sem loop),
   chegando a "matar" os 3 oponentes fictícios instantaneamente em 0,4%
   das partidas.
3. Combate contra 3 oponentes fictícios de 40 de vida que nunca bloqueiam
   nem interagem, usado pra reportar "39,6% mata pelo menos 1 oponente".
   Nenhum outro simulador desta biblioteca faz isso — combate real de
   oponente nunca e modelado, so os gatilhos de ataque/dano que geram
   recurso pro proprio jogador.
4. Gatilhos reais e rastreaveis (Lotho: "2a magica do turno"; Orochi:
   "criaturas causam dano de combate") substituidos por sorteio de
   probabilidade arbitraria em vez do texto real da carta.
5. Mahadi tem timing errado — o gatilho real e em lote no final do turno
   ("para cada criatura que morreu ESTE turno"), o script disparava por
   morte individual na hora.
Esses 5 pontos foram corrigidos/refeitos aqui do zero.

Mecanica central: a economia de Treasure. Empilhamento dos 3
multiplicadores (Xorn +1 por evento, Anointed Procession dobra, Academy
Manufactor cria Clue+Food junto) segue uma ORDEM ESCOLHIDA (documentada
abaixo em `create_treasures()`), já que nas regras reais quem controla os
3 replacement effects escolhe a ordem — a ordem usada aqui é a que
maximiza Treasures (Xorn antes de Anointed Procession), consistente com
o padrão de "jogada racional" já usado nos outros simuladores desta
biblioteca.

Simplificacoes documentadas (nao inventadas — omissoes explicitas):
- Sem oponente real: nenhum permanente, spell ou vida adversaria de
  verdade. Gatilhos que dependem disso (Mari matando criatura do
  oponente, Grenzo/Laughing Jasper Flint exilando da biblioteca do
  oponente, Smothering Tithe/Monologue Tax reagindo a compra/2a magica do
  OPONENTE, Revel in Riches matando criatura do oponente, Kellogg
  roubando criatura) sao contados como "disponivel" mas sem efeito
  numerico solo, OU (Grenzo/Laughing Jasper Flint) aproximados puxando
  da PROPRIA biblioteca como fonte substituta, documentado no código.
- Drain/dano/vida sao contadores agregados (proxy), nao vida real de
  oponente — nunca uso isso pra fingir "matou o oponente", so reporto o
  total de dano/drain gerado.
- Combate: "ataca" = nao esta com summoning sickness (ou tem haste).
  Nenhum bloqueio, nenhuma remocao de oponente durante o combate.
"""

import json
import math
import random
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
    ctype: str  # 'land','artifact','creature','artifact_creature','enchantment','sorcery','instant'
    tags: frozenset = field(default_factory=frozenset)


CARD_DB: dict[str, Card] = {}


def add(name, mv, ctype, tags=()):
    CARD_DB[name] = Card(name=name, mv=mv, ctype=ctype, tags=frozenset(tags))


COMMANDER = "Vihaan, Goldwaker"
add(COMMANDER, 3, "creature", {"commander", "outlaw"})

OUTLAW_TYPES = {"Assassin", "Mercenary", "Pirate", "Rogue", "Warlock"}

# --- Lands (35) -------------------------------------------------------------
add("Battlefield Forge", 0, "land", set())
add("Blackcleave Cliffs", 0, "land", {"fastland"})
add("Blood Crypt", 0, "land", {"shockland"})
add("Bojuka Bog", 0, "land", {"etb_tapped", "gy_hate"})
# Achado real 2026-08-31 (rodada ampliada, categoria 11 - multi-face):
# `layout` real confirmado via API Scryfall = "modal_dfc" (Brightclimb: "{T}:
# Add {W}."; Grimclimb: "{T}: Add {B}."). E' um pathway simples - o jogador
# escolhe UM dos dois lados no momento em que a carta entra, e aquele lado
# fica sendo o terreno pro resto do jogo (nao pode virar depois).
# Decisao de arquitetura ja existente neste arquivo (nao inventada agora pra
# esta carta so): o motor de mana inteiro deste simulador (`lands_in_play`,
# `rocks_mana`, `total_mana`) NUNCA rastreia cor por fonte individual - so
# soma mana total agregada, sem distincao de W/U/B/R/G em nenhum terreno,
# rock ou Treasure. Isso ja era verdade pra TODOS os 35 terrenos da lista
# antes desta rodada (nenhum "W_sources"/"B_sources" existe no codigo). Por
# isso a Pathway como land generico de 1 mana (igual qualquer outro terreno)
# e' consistente com o resto do arquivo, nao uma simplificacao nova so pra
# esta carta - implementar rastreamento de cor so pra 1 carta quebraria essa
# consistencia sem mudar o resultado de nenhuma metrica reportada (nenhuma
# metrica deste simulador depende de cor especifica).
add("Brightclimb Pathway // Grimclimb Pathway", 0, "land", set())
add("Caves of Koilos", 0, "land", set())
add("Clifftop Retreat", 0, "land", {"checkland_rw"})
add("Command Beacon", 0, "land", set())
add("Command Tower", 0, "land", set())
add("Demolition Field", 0, "land", set())
add("Desolate Mire", 0, "land", set())
add("Dragonskull Summit", 0, "land", {"checkland_br"})
add("Exotic Orchard", 0, "land", set())
add("Fetid Heath", 0, "land", set())
add("High Market", 0, "land", {"sac_outlet_life"})
add("Isolated Chapel", 0, "land", {"checkland_wb"})
add("Luxury Suite", 0, "land", {"multiplayer_untapped"})
add("Mountain", 0, "land", set())
add("Path of Ancestry", 0, "land", {"etb_tapped"})
add("Phyrexian Tower", 0, "land", {"sac_outlet_bb"})
add("Plains", 0, "land", set())
add("Rogue's Passage", 0, "land", set())
add("Rugged Prairie", 0, "land", set())
add("Shadowblood Ridge", 0, "land", set())
add("Spectator Seating", 0, "land", {"multiplayer_untapped"})
add("Sulfurous Springs", 0, "land", set())
add("Swamp", 0, "land", set())
add("Tainted Peak", 0, "land", set())
add("Treasure Vault", 0, "land", {"treasure_land"})

# --- Ramp (mana rocks reais) -------------------------------------------------
add("Arcane Signet", 2, "artifact", {"rock1"})
add("Sol Ring", 1, "artifact", {"rock2"})

# --- O motor de Treasures -----------------------------------------------------
add("Academy Manufactor", 3, "artifact_creature", {"manufactor"})
add("Anointed Procession", 4, "enchantment", {"token_doubler"})
add("Xorn", 3, "creature", {"xorn"})
add("Goldspan Dragon", 5, "creature", {"goldspan", "treasure_attack"})
add("Captain Lannery Storm", 3, "creature", {"treasure_attack", "haste"})
add("Smothering Tithe", 4, "enchantment", {"opponent_dependent"})
add("Big Score", 4, "instant", {"draw_treasure"})
add("Unexpected Windfall", 4, "instant", {"draw_treasure"})
add("Deadly Dispute", 2, "instant", {"sac_draw_treasure"})
add("Inspired Tinkering", 5, "sorcery", {"impulse_treasure"})
add("Black Market Connections", 3, "enchantment", {"modal_treasure"})
add("Monologue Tax", 3, "enchantment", {"opponent_dependent"})
add("Rain of Riches", 5, "enchantment", {"etb_treasure", "cascade_treasure"})
add("Treasure Vault", 0, "land", {"treasure_land"})  # ja adicionada acima
add("Kellogg, Dangerous Mind", 3, "creature", {"treasure_attack", "haste", "outlaw", "sac_steal_unused"})
add("Lotho, Corrupt Shirriff", 2, "creature", {"second_spell_treasure"})
add("Magda, the Hoardmaster", 2, "creature", {"crime_treasure", "outlaw"})
add("Mahadi, Emporium Master", 3, "creature", {"treasure_death_batch"})
add("Olivia, Opulent Outlaw", 4, "creature", {"outlaw_combat_treasure", "outlaw"})
add("Orochi Soul-Reaver", 4, "creature", {"combat_treasure_manifest", "outlaw"})
add("Pitiless Plunderer", 4, "creature", {"creature_death_treasure"})
add("Professional Face-Breaker", 3, "creature", {"combat_treasure", "impulse_treasure_sac"})
add("Prosper, Tome-Bound", 4, "creature", {"impulse_end_step", "play_exile_treasure", "outlaw"})
add("Revel in Riches", 5, "enchantment", {"opponent_dependent", "alt_win"})
add("The Reaver Cleaver", 3, "artifact", {"equipment_combat_treasure"})
add("Gleaming Splendor", 2, "enchantment", {"opponent_dependent"})  # trocada por Rakdos Signet
add("Smaug the Magnificent", 4, "creature", {"upkeep_treasure", "treasure_attack_damage", "haste"})  # trocada por Insatiable Avarice

# --- Aristocratas / drain -----------------------------------------------------
add("Zulaport Cutthroat", 2, "creature", {"creature_death_drain"})
add("Nadier's Nightblade", 3, "creature", {"token_leave_drain"})
add("Mirkwood Bats", 4, "creature", {"token_create_or_sac_drain"})
add("Kambal, Profiteering Mayor", 3, "creature", {"token_etb_drain"})
add("Agent of the Iron Throne", 3, "enchantment", {"death_drain_background"})
add("Dictate of Erebos", 5, "enchantment", {"death_edict_unused"})
add("Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel", 3, "creature", {"death_drain_transform", "sac_draw"})
add("Witch of the Moors", 5, "creature", {"lifegain_recursion"})
add("Marionette Master", 6, "creature", {"artifact_death_drain", "fabricate3"})
add("Mayhem Devil", 3, "creature", {"sac_damage"})
add("Life Insurance", 5, "enchantment", {"nontoken_death_treasure", "extort"})
add("Mari, the Killing Quill", 3, "creature", {"opponent_dependent"})

# --- Sac outlets ---------------------------------------------------------
add("Ashnod's Altar", 3, "artifact", {"sac_outlet_cc"})
add("Krark-Clan Ironworks", 4, "artifact", {"sac_outlet_artifact_cc"})
add("Jan Jansen, Chaos Crafter", 3, "creature", {"jan_jansen", "outlaw"})

# --- Card draw / interacao -----------------------------------------------
add("Caretaker's Talent", 3, "enchantment", {"token_draw"})
add("Path to Exile", 1, "instant", {"removal"})
add("Shoot the Sheriff", 2, "instant", {"removal"})
add("Council's Judgment", 3, "sorcery", {"removal"})
add("Deadly Derision", 4, "instant", {"removal_treasure"})
add("Requisition Raid", 1, "sorcery", {"removal"})
add("Blasphemous Act", 9, "sorcery", {"wipe"})
add("Blood Money", 7, "sorcery", {"wipe_treasure"})
add("Demolition Field", 0, "land", set())  # ja adicionada
add("Boros Charm", 2, "instant", {"protection_unused"})
add("Teferi's Protection", 3, "instant", {"protection_unused"})

# --- Recursao / exilar e jogar ---------------------------------------------
add("Sevinne's Reclamation", 3, "sorcery", {"recursion"})
add("Phyrexian Reclamation", 1, "enchantment", {"recursion_repeat"})
add("Back in Town", 6, "sorcery", {"recursion_x"})
add("Lich-Knights' Conquest", 5, "sorcery", {"recursion_sac"})
add("Grenzo, Havoc Raiser", 2, "creature", {"combat_impulse", "outlaw"})
add("Laughing Jasper Flint", 3, "creature", {"upkeep_impulse", "outlaw"})

# --- Combate / anthem / outros ---------------------------------------------
add("Aya of Alexandria", 4, "creature", {"historic_combat_token", "outlaw"})
add("Sentinel Sarah Lyons", 5, "creature", {"anthem_artifact"})
add("Shared Animosity", 3, "enchantment", {"anthem_tribal"})
add("Urabrask's Forge", 3, "artifact", {"forge_token"})
add("Grim Hireling", 4, "creature", {"combat_treasure2", "sac_debuff_unused"})

ARTIFACT_ISH = {"artifact", "artifact_creature"}
CREATURE_ISH = {"creature", "artifact_creature"}
LAND_NAMES = {n for n, c in CARD_DB.items() if c.ctype == "land"}

# Categoria 10 (metricas basicas obrigatorias) — achado real 2026-08-31
# (rodada ampliada): nao havia linha formal "INTERACTION"/"RECURSION" no
# relatorio, apesar do deck ter 5 pecas de remocao pontual + 2 wipes (seção
# 7 da auditoria) e 4 fontes de recursao real (Sevinne's Reclamation,
# Phyrexian Reclamation, Back in Town, Lich-Knights' Conquest) + Witch of
# the Moors (recursao condicional). Tags usadas pra contar de forma
# auditavel em cast_card()/nos pontos de resolucao de cada efeito.
REMOVAL_TAGS = {"removal", "removal_treasure", "wipe", "wipe_treasure"}

# Politica opcional (2026-08-22, pedido do usuario): maximizar CRIACAO e
# DESTRUICAO de Treasure como mecanica principal, nao so usa-los como mana
# reserva. Dois efeitos:
# 1. Criacao: cartas que geram Treasure ganham prioridade de conjuracao
#    sobre outras de mesmo custo (ver TREASURE_SOURCE_TAGS/is_treasure_source).
# 2. Destruicao: no combate, se o Vihaan animou os Treasures em criaturas
#    3/3 (outlaw) ate o final do turno, sacrifica todos os que sobrarem
#    depois dos gatilhos de ataque — preferindo o Ashnod's Altar quando
#    disponivel, porque um Treasure animado sacrificado ali conta como
#    morte de CRIATURA + morte de ARTEFATO + token saindo AO MESMO TEMPO
#    (Zulaport/Sephiroth/Pitiless Plunderer + Marionette Master/Agent of
#    the Iron Throne + Nadier's Nightblade/Mirkwood Bats, tudo no mesmo
#    evento) — o Krark-Clan Ironworks so pega artefato+token (nao e
#    criatura fora do combate). Mana gerada entra num pool avulso do
#    turno (`bonus_mana_pool`), disponivel pro resto do main phase.
TREASURE_MAXIMIZE_POLICY = True

TREASURE_SOURCE_TAGS = {
    "goldspan", "treasure_attack", "draw_treasure", "sac_draw_treasure",
    "impulse_treasure", "modal_treasure", "etb_treasure", "cascade_treasure",
    "manufactor", "xorn", "token_doubler", "second_spell_treasure",
    "crime_treasure", "treasure_death_batch", "outlaw_combat_treasure",
    "combat_treasure_manifest", "creature_death_treasure", "combat_treasure",
    "impulse_treasure_sac", "play_exile_treasure", "equipment_combat_treasure",
    "nontoken_death_treasure", "combat_treasure2", "jan_jansen", "upkeep_treasure",
}


def is_treasure_source(name: str) -> bool:
    return bool(CARD_DB[name].tags & TREASURE_SOURCE_TAGS)


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
    bonus_mana_pool: int = 0  # mana gerada mid-turn por sac outlets (Ashnod's Altar/KCI)
    tapped_lands_this_turn: set = field(default_factory=set)  # terrenos "enters tapped" jogados este turno - ver ETB_TAPPED_LANDS
    treasures_animated_this_combat: int = 0
    animated_treasures_sacrificed_total: int = 0
    bonus_mana_generated_total: int = 0
    jan_jansen_used_this_turn: bool = False
    spells_cast_this_turn: int = 0
    commits_crime_this_turn: bool = False
    treasure_spent_this_turn: bool = False
    cascade_used_this_turn: bool = False
    caretaker_drawn_this_turn: bool = False
    kambal_drawn_this_turn: bool = False
    black_market_connections_triggered_this_turn: bool = False
    life_gained_this_turn: int = 0

    commander_in_play: bool = False
    commander_cast_count: int = 0
    commander_cast_turn: Optional[int] = None

    creature_cast_turn: dict = field(default_factory=dict)  # nome -> turno em que entrou
    deaths_this_turn: int = 0

    treasures: int = 0
    clues: int = 0
    foods: int = 0
    constructs: int = 0  # 1/1 artifact creature tokens (Jan Jansen)
    other_tokens: int = 0  # criaturas token genericas (changeling, manifest, Scorpion Dragon...)
    other_tokens_sick: int = 0
    constructs_sick: int = 0
    forge_oil: int = 0
    impulse_pool: list = field(default_factory=list)  # cartas exiladas jogaveis
    life: int = 40

    sephiroth_deaths_this_turn: int = 0
    sephiroth_transformed: bool = False
    # Achado real 2026-08-31 (rodada ampliada, categoria 11): o emblem Super
    # Nova e um objeto INDEPENDENTE de Sephiroth (persiste mesmo se a
    # criatura sair de campo depois) - campo separado do "transformed" da
    # propria carta, nunca resetado no resto da partida.
    has_super_nova_emblem: bool = False
    caretaker_level: int = 1  # Classes sempre entram no nivel 1

    # metrics --------------------------------------------------------------
    treasures_created_total: int = 0
    treasures_sacrificed_total: int = 0
    clues_created_total: int = 0
    foods_created_total: int = 0
    constructs_created_total: int = 0
    other_tokens_created_total: int = 0
    creature_deaths_total: int = 0
    artifact_deaths_total: int = 0
    token_leaves_total: int = 0
    drain_damage_total: int = 0
    life_gained_total: int = 0
    cards_drawn_extra: int = 0
    cascades_triggered: int = 0
    revel_condition_met_turn: Optional[int] = None
    combat_attacks_total: int = 0

    # Metricas novas — achados reais 2026-08-31 (rodada ampliada, categorias
    # 10-13): metricas basicas obrigatorias (recursion/interaction) que nao
    # tinham linha propria no relatorio, mais os efeitos novos implementados.
    removal_cast_total: int = 0  # categoria "interaction" — remocao/wipe conjurado
    recursion_events_total: int = 0  # categoria "recursion" — carta recuperada do cemiterio
    phyrexian_reclamation_activations_total: int = 0
    sephiroth_sac_draws_total: int = 0  # cartas compradas via sac do Sephiroth (as 2 faces)
    caretaker_level2_reached: bool = False
    caretaker_level3_reached: bool = False
    caretaker_tokens_copied_total: int = 0


def draw_cards(state: GameState, n: int):
    for _ in range(n):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1


def gain_life(state: GameState, n: int):
    state.life += n
    state.life_gained_total += n
    state.life_gained_this_turn += n


def drain(state: GameState, n: int):
    """Dano/drena agregado — proxy, nunca vida real de oponente."""
    state.drain_damage_total += n


# ---------------------------------------------------------------------------
# Type helpers
# ---------------------------------------------------------------------------

def is_artifact_card(name: str) -> bool:
    return CARD_DB[name].ctype in ARTIFACT_ISH


def is_creature_card(name: str) -> bool:
    return CARD_DB[name].ctype in CREATURE_ISH


def is_outlaw(name: str) -> bool:
    return "outlaw" in CARD_DB[name].tags


def is_historic(name: str) -> bool:
    """Artefato, lendaria ou Saga."""
    return is_artifact_card(name) or "Legendary" in name or name in (
        "Aya of Alexandria", "Captain Lannery Storm", "Goldspan Dragon",
        "Grenzo, Havoc Raiser", "Jan Jansen, Chaos Crafter", "Kambal, Profiteering Mayor",
        "Kellogg, Dangerous Mind", "Laughing Jasper Flint", "Lotho, Corrupt Shirriff",
        "Magda, the Hoardmaster", "Mahadi, Emporium Master", "Mari, the Killing Quill",
        "Olivia, Opulent Outlaw", "Prosper, Tome-Bound", COMMANDER,
        "Sentinel Sarah Lyons", "Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel",
    )


# ---------------------------------------------------------------------------
# Motor de Treasure — criacao com os 3 multiplicadores empilhaveis
# ---------------------------------------------------------------------------

def create_treasures(state: GameState, n: int, source: str = ""):
    """Ordem escolhida (o controlador escolhe, nas regras reais): Xorn
    primeiro (+1 flat por evento), Anointed Procession depois (dobra o
    total), Academy Manufactor por ultimo (cada Treasure resultante TAMBEM
    cria 1 Clue + 1 Food — interpretacao escalando com N, documentada no
    docstring do modulo). Essa ordem maximiza Treasures (ver docstring)."""
    if n <= 0:
        return
    total = n
    if "Xorn" in state.battlefield:
        total += 1
    if "Anointed Procession" in state.battlefield:
        total *= 2
    state.treasures += total
    state.treasures_created_total += total

    if "Academy Manufactor" in state.battlefield:
        state.clues += total
        state.foods += total
        state.clues_created_total += total
        state.foods_created_total += total

    on_tokens_created(state, total, kind="treasure")


def create_constructs(state: GameState, n: int, source: str = ""):
    if n <= 0:
        return
    total = n * (2 if "Anointed Procession" in state.battlefield else 1)
    state.constructs += total
    state.constructs_sick += total
    state.constructs_created_total += total
    on_tokens_created(state, total, kind="construct")


def create_other_tokens(state: GameState, n: int, source: str = ""):
    if n <= 0:
        return
    total = n * (2 if "Anointed Procession" in state.battlefield else 1)
    state.other_tokens += total
    state.other_tokens_sick += total
    state.other_tokens_created_total += total
    on_tokens_created(state, total, kind="creature")


def on_tokens_created(state: GameState, n: int, kind: str):
    if n <= 0:
        return
    if "Mirkwood Bats" in state.battlefield:
        drain(state, n)
    if kind != "treasure_component" and not state.kambal_drawn_this_turn and "Kambal, Profiteering Mayor" in state.battlefield:
        drain(state, 1)
        gain_life(state, 1)
        state.kambal_drawn_this_turn = True
    if not state.caretaker_drawn_this_turn and "Caretaker's Talent" in state.battlefield:
        draw_cards(state, 1)
        state.caretaker_drawn_this_turn = True


# ---------------------------------------------------------------------------
# Sacrificio — funcoes centrais (aristocratas reagem aqui)
# ---------------------------------------------------------------------------

def sacrifice_treasures(state: GameState, n: int, for_mana: bool = False, as_creature: bool = False):
    n = min(n, state.treasures)
    if n <= 0:
        return 0
    state.treasures -= n
    state.treasures_sacrificed_total += n
    if for_mana:
        state.treasure_spent_this_turn = True
    on_permanent_sacrificed(state, n, is_artifact=True, is_creature=as_creature, is_token=True)
    return n


def aggressive_treasure_destruction(state: GameState):
    """TREASURE_MAXIMIZE_POLICY: sacrifica os Treasures que sobraram do
    combate pelo melhor outlet disponivel. Se o Vihaan os animou em
    criaturas ate o final do turno, o Ashnod's Altar pega TODOS os
    gatilhos de uma vez (criatura+artefato+token); sem animacao ou sem
    Ashnod's Altar, cai pro Krark-Clan Ironworks (so artefato+token)."""
    if state.treasures <= 0:
        return
    animated = state.treasures_animated_this_combat > 0
    if animated and "Ashnod's Altar" in state.battlefield:
        n = sacrifice_treasures(state, state.treasures, as_creature=True)
        state.bonus_mana_pool += 2 * n
        state.bonus_mana_generated_total += 2 * n
        state.animated_treasures_sacrificed_total += n
    elif "Krark-Clan Ironworks" in state.battlefield:
        n = sacrifice_treasures(state, state.treasures, as_creature=False)
        state.bonus_mana_pool += 2 * n
        state.bonus_mana_generated_total += 2 * n


def sacrifice_constructs(state: GameState, n: int):
    n = min(n, state.constructs)
    if n <= 0:
        return 0
    state.constructs -= n
    on_permanent_sacrificed(state, n, is_artifact=True, is_creature=True, is_token=True)
    return n


def sacrifice_other_tokens(state: GameState, n: int):
    n = min(n, state.other_tokens)
    if n <= 0:
        return 0
    state.other_tokens -= n
    on_permanent_sacrificed(state, n, is_artifact=False, is_creature=True, is_token=True)
    return n


def sacrifice_named_creature(state: GameState, name: str):
    if name not in state.battlefield:
        return False
    state.battlefield.remove(name)
    state.creature_cast_turn.pop(name, None)
    state.graveyard.append(name)
    on_permanent_sacrificed(state, 1, is_artifact=is_artifact_card(name), is_creature=True, is_token=False)
    return True


def on_permanent_sacrificed(state: GameState, n: int, is_artifact: bool, is_creature: bool, is_token: bool):
    """Dispara os gatilhos de sacrificio/morte reais. Chamado por toda via
    de sacrificio (Treasure, Construct, token generico, criatura nomeada)."""
    if "Mayhem Devil" in state.battlefield:
        drain(state, n)
    if is_creature:
        on_creature_dies(state, n, is_token=is_token)
    if is_artifact:
        on_artifact_dies(state, n)
    if is_token:
        on_token_leaves(state, n)


def on_creature_dies(state: GameState, n: int, is_token: bool):
    if n <= 0:
        return
    state.creature_deaths_total += n
    state.deaths_this_turn += n
    if "Zulaport Cutthroat" in state.battlefield:
        drain(state, n)
        gain_life(state, n)
    if "Pitiless Plunderer" in state.battlefield:
        create_treasures(state, n, source="Pitiless Plunderer")

    # Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel — achado real
    # 2026-08-31 (rodada ampliada, categoria 11): `state.sephiroth_transformed`
    # ja existia e era SETADO na 4a morte do turno, mas nunca era LIDO em
    # lugar nenhum - uma tag morta de estado sem efeito. Oraculo real
    # (layout `transform`, confirmado via API):
    #   Frente ({2}{B}): "Whenever another creature dies, target opponent
    #   loses 1 life and you gain 1 life. If this is the fourth time this
    #   ability has resolved this turn, transform Sephiroth."
    #   Verso: "Flying / Super Nova - As this creature transforms..., you
    #   get an emblem with 'Whenever a creature dies, target opponent loses
    #   1 life and you gain 1 life.' / Whenever Sephiroth attacks, you may
    #   sacrifice any number of other creatures. If you do, draw that many
    #   cards."
    # 3 coisas corrigidas: (1) o emblem Super Nova e' uma 2a fonte
    # INDEPENDENTE de drain 1/vida 1 por morte - nao substitui a habilidade
    # da frente, ela deixa de existir (o VERSO nao tem mais "whenever
    # another creature dies", so' o emblem tem, com texto "a creature dies"
    # sem "another" - inclui a morte do proprio Sephiroth). O emblem e'
    # permanente e independente da carta (drena mesmo se Sephiroth sair de
    # campo depois). (2) sem limite de 4x/turno depois de transformado (o
    # limite so' existia na habilidade da FRENTE, pra disparar o transform).
    # (3) a habilidade de ataque muda de escala - ver try_sephiroth_sac_draw.
    sephiroth_on_bf = "Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel" in state.battlefield
    for _ in range(n):
        if state.has_super_nova_emblem:
            drain(state, 1)
            gain_life(state, 1)
        elif sephiroth_on_bf and not state.sephiroth_transformed:
            drain(state, 1)
            gain_life(state, 1)
            state.sephiroth_deaths_this_turn += 1
            if state.sephiroth_deaths_this_turn == 4:
                state.sephiroth_transformed = True
                state.has_super_nova_emblem = True

    if not is_token and "Life Insurance" in state.battlefield:
        state.life -= 1
        create_treasures(state, 1, source="Life Insurance")


def on_artifact_dies(state: GameState, n: int):
    if n <= 0:
        return
    state.artifact_deaths_total += n
    if "Agent of the Iron Throne" in state.battlefield:
        drain(state, n)
    if "Marionette Master" in state.battlefield:
        # Poder base real (Scryfall): 1/3. Fabricate 3 aqui sempre escolhe
        # criar 3 Servos (ver resolve_permanent_etb), nao contadores — entao
        # o poder fica sempre 1, nunca 4 (valor antigo aqui estava chutado
        # sem checar a carta real, corrigido).
        drain(state, n * 1)


def on_token_leaves(state: GameState, n: int):
    if n <= 0:
        return
    state.token_leaves_total += n
    if "Nadier's Nightblade" in state.battlefield:
        drain(state, n)
        gain_life(state, n)
    if "Mirkwood Bats" in state.battlefield:
        # Achado real 2026-08-28 (auditoria de checklist de mecanica):
        # "Whenever you create OR SACRIFICE a token" - so a metade
        # "create" (via on_tokens_created) disparava; a metade
        # "sacrifice"/leaves-the-battlefield nunca era checada aqui,
        # apesar de ser o motor central de sacrificio do deck
        # (aggressive_treasure_destruction chama isso toda hora).
        drain(state, n)


# ---------------------------------------------------------------------------
# Mana model — rastreado de verdade turno a turno (correcao do bug do
# script original: land/rock nunca eram descontados entre casts)
# ---------------------------------------------------------------------------

# Desolate Mire ({1},{T}: Add {W}{B}) e Shadowblood Ridge ({1},{T}: Add
# {B}{R}) sao FILTER LANDS - sem NENHUMA habilidade de mana gratuita (ao
# contrario de um terreno normal). So funcionam com uma fonte de mana JA
# disponivel pra pagar o {1} (liquido +1, igual Fetid Heath/Rugged Prairie
# no Edgar Markov). Achado real 2026-08-28 (auditoria de checklist de
# mecanica): eram contadas como +1 gratis incondicional, igual qualquer
# terreno normal, mesmo sem nenhuma outra fonte de mana em campo.
FILTER_LANDS = {"Desolate Mire", "Shadowblood Ridge"}


def lands_in_play(state: GameState) -> int:
    total = sum(1 for n in state.battlefield if n in LAND_NAMES)
    total -= len(state.tapped_lands_this_turn)  # terrenos "enters tapped" jogados este turno
    filter_count = sum(1 for n in state.battlefield if n in FILTER_LANDS)
    if filter_count and (total - filter_count) <= 0 and rocks_mana(state) <= 0 and state.treasures <= 0:
        total -= filter_count  # sem fonte nenhuma pra "semear" o filtro - contribuem 0
    return total


def rocks_mana(state: GameState) -> int:
    total = 0
    if "Sol Ring" in state.battlefield:
        total += 2
    if "Arcane Signet" in state.battlefield:
        total += 1
    return total


def treasure_value(state: GameState) -> int:
    return 2 if "Goldspan Dragon" in state.battlefield else 1


def total_mana(state: GameState) -> int:
    return (lands_in_play(state) + rocks_mana(state)
            + state.treasures * treasure_value(state) + state.bonus_mana_pool)


def remaining_mana(state: GameState) -> int:
    return max(0, total_mana(state) - state.mana_spent_this_turn)


def can_cast(state: GameState, name: str) -> bool:
    return remaining_mana(state) >= CARD_DB[name].mv


def spend_mana(state: GameState, n: int):
    """So desconta Treasure real quando o gasto ultrapassa o que terreno+
    rock ja cobrem no turno — terreno/rock sao um teto fixo por turno, nao
    um poco infinito (era o bug do script original)."""
    land_rock_cap = lands_in_play(state) + rocks_mana(state)
    already_used_land_rock = min(state.mana_spent_this_turn, land_rock_cap)
    remaining_land_rock = max(0, land_rock_cap - already_used_land_rock)
    from_land_rock = min(n, remaining_land_rock)
    from_treasure = n - from_land_rock
    if from_treasure > 0:
        tv = treasure_value(state)
        needed = math.ceil(from_treasure / tv)
        sacrifice_treasures(state, needed, for_mana=True)
    state.mana_spent_this_turn += n


# ---------------------------------------------------------------------------
# ETB e gatilhos de conjuracao
# ---------------------------------------------------------------------------

def try_sephiroth_sac_draw(state: GameState):
    """"Whenever Sephiroth enters or attacks, you may sacrifice another
    creature. If you do, draw a card." Achado real 2026-08-28 (auditoria
    de checklist de mecanica): so' a metade passiva de dano ("whenever
    another creature dies...") estava modelada - essa metade (ETB/ataque)
    100% ausente. So sacrifica fodder barato (token generico ou
    Construct), nunca uma criatura nomeada de verdade.

    Achado real 2026-08-31 (rodada ampliada, categoria 11): depois de
    transformar, o VERSO tem uma habilidade DIFERENTE (so' em ataque, sem
    ETB - nao teria como, ja estava em campo): "Whenever Sephiroth attacks,
    you may sacrifice any number of other creatures. If you do, draw that
    many cards." - mudanca real de escala (1 sacrificio -> QUALQUER NUMERO),
    nao so' cosmetica. Corrigido pra sacrificar TODO o fodder disponivel
    (tokens + constructs) de uma vez quando `state.sephiroth_transformed`."""
    if "Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel" not in state.battlefield:
        return
    if state.sephiroth_transformed:
        n = state.other_tokens + state.constructs
        if n <= 0:
            return
        sacrifice_other_tokens(state, state.other_tokens)
        sacrifice_constructs(state, state.constructs)
        draw_cards(state, n)
        state.sephiroth_sac_draws_total += n
    else:
        if state.other_tokens > 0:
            sacrifice_other_tokens(state, 1)
            draw_cards(state, 1)
            state.sephiroth_sac_draws_total += 1
        elif state.constructs > 0:
            sacrifice_constructs(state, 1)
            draw_cards(state, 1)
            state.sephiroth_sac_draws_total += 1


def try_phyrexian_reclamation(state: GameState) -> bool:
    """Achado real 2026-08-31 (rodada ampliada, categoria 7 - ativadas
    repetiveis / categoria 10 - metrica RECURSION): so' existia a entrada no
    CARD_DB (tag `recursion_repeat`), ZERO logica de ativacao em lugar
    nenhum - a UNICA fonte repetivel de recursao do deck ficava sempre de
    fora do goldfish. Oraculo real (Scryfall): '{1}{B}, Pay 2 life: Return
    target creature card from your graveyard to your hand.' Sem 'activate
    only as a sorcery' no texto - repetivel livremente (inclusive em
    resposta), mas este simulador so' tem timing de main phase, entao ativa
    quantas vezes mana+material do cemiterio permitirem dentro do main
    phase. Vida nao e' recurso escasso rastreado neste arquivo pra custos
    de ativacao (mesma convencao ja usada pros shock/pain lands - so' a
    mana e o material do cemiterio limitam). Prioriza devolver a criatura
    de MAIOR mv (mais valor de board por ativacao) - heuristica
    documentada."""
    if "Phyrexian Reclamation" not in state.battlefield:
        return False
    if remaining_mana(state) < 2:
        return False
    creatures_gy = [n for n in state.graveyard if is_creature_card(n)]
    if not creatures_gy:
        return False
    best = max(creatures_gy, key=lambda n: CARD_DB[n].mv)
    state.graveyard.remove(best)
    state.life -= 2
    spend_mana(state, 2)
    state.hand.append(best)
    state.phyrexian_reclamation_activations_total += 1
    state.recursion_events_total += 1
    return True


def resolve_permanent_etb(state: GameState, name: str):
    if name == "Rain of Riches":
        create_treasures(state, 2, source="Rain of Riches ETB")
    elif name == "Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel":
        try_sephiroth_sac_draw(state)
    elif name == "Marionette Master":
        # Fabricate 3: fichas (reforca o motor de artefato-morte) em vez de contadores.
        create_other_tokens(state, 0)  # Servo tokens sao artefato-criatura; tratados como constructs
        create_constructs(state, 3, source="Marionette Master fabricate")
    elif name == "Urabrask's Forge":
        state.forge_oil = 0


def resolve_instant_sorcery(state: GameState, name: str):
    if name in ("Big Score", "Unexpected Windfall"):
        if state.hand:
            discard = min(state.hand, key=lambda n: CARD_DB[n].mv)
            state.hand.remove(discard)
            state.graveyard.append(discard)
        draw_cards(state, 2)
        create_treasures(state, 2, source=name)
    elif name == "Deadly Dispute":
        if state.treasures > 0:
            sacrifice_treasures(state, 1)
        elif state.constructs > 0:
            sacrifice_constructs(state, 1)
        elif state.other_tokens > 0:
            sacrifice_other_tokens(state, 1)
        else:
            candidates = [n for n in state.battlefield if is_creature_card(n) or is_artifact_card(n)]
            if candidates:
                sacrifice_named_creature(state, candidates[0])
        draw_cards(state, 2)
        create_treasures(state, 1, source=name)
    elif name == "Inspired Tinkering":
        pull_impulse(state, 3, deadline_turns=2)
        create_treasures(state, 3, source=name)
    elif name == "Blood Money":
        real_creatures = [n for n in state.battlefield if is_creature_card(n) and n != COMMANDER]
        n_dead = len(real_creatures) + state.constructs + state.other_tokens
        for c in real_creatures:
            sacrifice_named_creature(state, c)
        sacrifice_constructs(state, state.constructs)
        sacrifice_other_tokens(state, state.other_tokens)
        create_treasures(state, len(real_creatures), source="Blood Money (nontoken)")
    elif name == "Blasphemous Act":
        real_creatures = [n for n in state.battlefield if is_creature_card(n) and n != COMMANDER]
        for c in real_creatures:
            sacrifice_named_creature(state, c)
        sacrifice_constructs(state, state.constructs)
        sacrifice_other_tokens(state, state.other_tokens)
    elif name in ("Path to Exile", "Shoot the Sheriff", "Council's Judgment",
                  "Deadly Derision", "Requisition Raid", "Boros Charm", "Teferi's Protection"):
        state.commits_crime_this_turn = True
        if name == "Deadly Derision":
            create_treasures(state, 1, source=name)
    elif name == "Sevinne's Reclamation":
        cheap = [n for n in state.graveyard if CARD_DB[n].mv <= 3 and CARD_DB[n].ctype != "land"]
        if cheap:
            best = max(cheap, key=lambda n: CARD_DB[n].mv)
            state.graveyard.remove(best)
            enter_battlefield(state, best)
            state.recursion_events_total += 1
    elif name == "Back in Town":
        x = min(2, remaining_mana(state))
        outlaws_in_gy = [n for n in state.graveyard if is_outlaw(n) and is_creature_card(n)][:x]
        for n in outlaws_in_gy:
            state.graveyard.remove(n)
            enter_battlefield(state, n)
            state.recursion_events_total += 1
    elif name == "Lich-Knights' Conquest":
        fodder = state.constructs + state.foods + state.clues
        n_return = min(fodder, len([n for n in state.graveyard if is_creature_card(n)]))
        sacrifice_constructs(state, min(state.constructs, n_return))
        creatures_gy = [n for n in state.graveyard if is_creature_card(n)][:n_return]
        for n in creatures_gy:
            state.graveyard.remove(n)
            enter_battlefield(state, n)
            state.recursion_events_total += 1


def pull_impulse(state: GameState, n: int, deadline_turns: int):
    for _ in range(n):
        if state.library:
            state.impulse_pool.append((state.library.pop(0), state.turn + deadline_turns))


def play_from_impulse(state: GameState):
    """Joga a carta mais barata disponivel no pool de exilio, se der."""
    valid = [entry for entry in state.impulse_pool if entry[1] >= state.turn]
    valid = [e for e in valid if e[0] != "land" and CARD_DB.get(e[0]) and CARD_DB[e[0]].ctype != "land"]
    castable = [e for e in valid if can_cast(state, e[0])]
    if not castable:
        return False
    castable.sort(key=lambda e: CARD_DB[e[0]].mv)
    card, deadline = castable[0]
    state.impulse_pool.remove((card, deadline))
    spend_mana(state, CARD_DB[card].mv)
    enter_battlefield(state, card, from_hand=False)
    if "Prosper, Tome-Bound" in state.battlefield:
        create_treasures(state, 1, source="Prosper Pact Boon")
    return True


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
    if name == "Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel":
        # Achado real 2026-08-31: se esta carta morreu ja transformada e foi
        # recuperada do cemiterio (Sevinne's Reclamation, mv<=3, alcanca
        # ela), a copia fisica NOVA que entra em campo e' sempre a FRENTE
        # (transform e' propriedade do objeto fisico, nao do jogador) - reset
        # do flag por-carta. O emblem Super Nova (`has_super_nova_emblem`)
        # NAO reseta - e' um objeto independente, permanente pro resto do
        # jogo mesmo que Sephiroth morra e volte sem estar transformado.
        state.sephiroth_transformed = False
    resolve_permanent_etb(state, name)


def cast_card(state: GameState, name: str):
    card = CARD_DB[name]
    if name == COMMANDER:
        spend_mana(state, card.mv + 2 * (state.commander_cast_count))
    else:
        spend_mana(state, card.mv)
    state.spells_cast_this_turn += 1

    # A carta sai da mao (ou vai a campo) ANTES de qualquer efeito
    # colateral (cascade, Lotho) rodar — senao um cascade que descarta
    # carta (ex: Big Score) pode acabar descartando a propria carta que
    # esta sendo conjurada, ainda "presa" na mao.
    is_spell = card.ctype in ("instant", "sorcery")
    if is_spell:
        state.hand.remove(name)
        state.graveyard.append(name)
    else:
        enter_battlefield(state, name)

    treasure_funded = state.treasure_spent_this_turn
    if (treasure_funded and "Rain of Riches" in state.battlefield
            and not state.cascade_used_this_turn):
        do_cascade(state, card.mv)
        state.cascade_used_this_turn = True

    if "Lotho, Corrupt Shirriff" in state.battlefield and state.spells_cast_this_turn == 2:
        state.life -= 1
        create_treasures(state, 1, source="Lotho (2a magica)")

    if is_spell:
        if card.tags & REMOVAL_TAGS:
            state.removal_cast_total += 1
        resolve_instant_sorcery(state, name)


def do_cascade(state: GameState, mv_cutoff: int):
    """Cascade real: exila do topo ate achar nao-terreno mais barato, pode
    conjurar de graca."""
    state.cascades_triggered += 1
    exiled = []
    hit = None
    while state.library:
        c = state.library.pop(0)
        exiled.append(c)
        if CARD_DB[c].ctype != "land" and CARD_DB[c].mv < mv_cutoff:
            hit = c
            break
    if hit:
        exiled.remove(hit)
        enter_battlefield(state, hit, from_hand=False)
        if CARD_DB[hit].ctype in ("instant", "sorcery"):
            if CARD_DB[hit].tags & REMOVAL_TAGS:
                state.removal_cast_total += 1
            resolve_instant_sorcery(state, hit)
            state.battlefield.remove(hit)
            state.graveyard.append(hit)
    random.Random(state.turn).shuffle(exiled)
    state.library.extend(exiled)


# ---------------------------------------------------------------------------
# Deck / mulligan
# ---------------------------------------------------------------------------

def build_library():
    lib = []
    lines = open("lista.md").read().split("## Lista completa")[1].strip().split("\n")
    import re
    for l in lines:
        l = l.strip()
        if not l:
            continue
        m = re.match(r"^(\d+)\s+(.+)$", l)
        qty, name = int(m.group(1)), m.group(2).strip()
        assert name in CARD_DB, f"faltando no CARD_DB: {name}"
        for _ in range(qty):
            lib.append(name)
    assert len(lib) == 99, len(lib)
    return lib


BASE_LIBRARY = build_library()

GOOD_KEEP = {"Sol Ring", "Arcane Signet", "Smothering Tithe", "Big Score"}


def should_keep(hand: list) -> bool:
    lands = sum(1 for n in hand if n in LAND_NAMES)
    if lands >= 3:
        return True
    if lands == 2 and any(n in GOOD_KEEP for n in hand):
        return True
    return False


def mulligan(rng: random.Random, max_mulls: int = 3):
    mulls = 0
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


# ---------------------------------------------------------------------------
# Turno
# ---------------------------------------------------------------------------

# Achado real 2026-08-28 (auditoria de checklist de mecanica): as tags
# "etb_tapped"/"checkland_*"/"fastland"/"shockland" existiam no CARD_DB mas
# nunca eram lidas em lugar nenhum - todo terreno produzia mana no proprio
# turno em que era jogado, mesmo os que entram tapped de verdade.
CHECKLAND_TYPES = {
    "Clifftop Retreat": {"Mountain", "Plains"},
    "Dragonskull Summit": {"Swamp", "Mountain"},
    "Isolated Chapel": {"Plains", "Swamp"},
}
BASIC_TYPE_LANDS = {
    "Mountain": {"Mountain", "Blood Crypt"},
    "Plains": {"Plains"},
    "Swamp": {"Swamp", "Blood Crypt"},
}
FASTLAND_MAX_OTHER_LANDS = {"Blackcleave Cliffs": 2}


def _controls_basic_type(state: GameState, basic_type: str) -> bool:
    carriers = BASIC_TYPE_LANDS.get(basic_type, set())
    return any(n in carriers for n in state.battlefield)


def play_land(state: GameState):
    if state.lands_played_this_turn >= 1:
        return
    lands_in_hand = [n for n in state.hand if n in LAND_NAMES]
    if not lands_in_hand:
        return
    choice = lands_in_hand[0]
    state.hand.remove(choice)
    other_lands_before = sum(1 for n in state.battlefield if n in LAND_NAMES)
    state.battlefield.append(choice)
    state.lands_played_this_turn += 1

    tags = CARD_DB[choice].tags
    enters_tapped = False
    if "etb_tapped" in tags:
        enters_tapped = True
    elif choice in CHECKLAND_TYPES:
        enters_tapped = not any(_controls_basic_type(state, t) for t in CHECKLAND_TYPES[choice])
    elif "fastland" in tags:
        enters_tapped = other_lands_before > FASTLAND_MAX_OTHER_LANDS.get(choice, 0)
    # "shockland" (Blood Crypt): assume sempre paga os 2 de vida, mesma
    # convencao ja usada nesse arquivo pra outros custos de vida nao
    # rastreados (sem vida propria modelada) - nunca entra tapped aqui.
    if enters_tapped:
        state.tapped_lands_this_turn.add(choice)


def try_black_market_connections(state: GameState):
    """"At the beginning of your first main phase, choose one or more -
    Sell Contraband (Treasure, -1 life) / Buy Information (draw, -2 life) /
    Hire a Mercenary (3/2 Shapeshifter changeling token, -3 life)." Achado
    real 2026-08-28 (auditoria de checklist de mecanica): so' existia a
    entrada no CARD_DB, NENHUM gatilho real em lugar nenhum. Esse arquivo
    rastreia vida de verdade (ao contrario de varios outros decks desta
    sessao) - a IA sempre escolhe os 3 modos (mesma filosofia agressiva ja
    usada no resto do motor, sem dano de combate real recebido pra punir
    perder vida).

    Achado real 2026-08-31 (rodada ampliada): oraculo diz "your FIRST main
    phase" - so' 1x por turno - mas `main_phase()` e' chamada 2x por turno
    (pre e pos-combate, pra usar mana bonus dos sac outlets) e esta funcao
    nao tinha nenhuma guarda contra a 2a chamada, dobrando Treasure/draw/
    token/perda de vida todo turno desde a correcao de 2026-08-28. Corrigido
    com o mesmo padrao de flag per-turno ja usado em
    caretaker_drawn_this_turn/kambal_drawn_this_turn."""
    if "Black Market Connections" not in state.battlefield:
        return
    if state.black_market_connections_triggered_this_turn:
        return
    state.black_market_connections_triggered_this_turn = True
    create_treasures(state, 1, source="Black Market Connections")
    state.life -= 1
    draw_cards(state, 1)
    state.life -= 2
    state.other_tokens += 1
    on_tokens_created(state, 1, kind="creature")
    state.life -= 3


def try_level_caretakers_talent(state: GameState):
    """Achado real 2026-08-31 (rodada ampliada, categoria 13 - Classes):
    so' o nivel 1 (draw 1x/turno quando token entra) estava implementado.
    Oraculo real (Scryfall, type_line "Enchantment — Class"):
      Nivel 1: "Whenever one or more tokens you control enter, draw a
      card. This ability triggers only once each turn."
      {W}: Level 2 - "When this Class becomes level 2, create a token
      that's a copy of target token you control."
      {3}{W}: Level 3 - "Creature tokens you control get +2/+2."
    Niveis sao ganhos "as a sorcery" (so' em main phase, pilha vazia - ja'
    e' onde esta funcao e' chamada) e sao CUMULATIVOS (nivel 3 nao substitui
    nivel 1/2, todos ficam ativos). Precisa passar por nivel 2 antes do 3
    (nao da' pra pular).

    Heuristica de gasto de mana (documentada, nao ha' "certo" formal no
    texto da carta): subir de nivel tem prioridade BAIXA em relacao a
    conjurar qualquer carta da mao (o main_phase ja gastou tudo que dava
    antes de chegar aqui) - mas prioridade ALTA sobre so' deixar mana
    sobrando, porque o nivel 3 e' um anthem de campo inteiro (mesmo padrao
    do Innkeeper's Talent que motivou a Regra 13 de
    goldfish-sim-card-rules.md). Chamada no fim de main_phase(), depois do
    loop de castables e da recursao da Phyrexian Reclamation - so' usa mana
    que sobrou depois de tudo mais.

    O anthem do nivel 3 (+2/+2 em criaturas-token) NAO tem onde se aplicar
    numericamente neste simulador especifico: este arquivo nao rastreia
    poder/resistencia de criatura em NENHUM lugar (nem antes desta correcao,
    nem depois - nenhum outro efeito do deck depende de poder de token,
    Marionette Master usa o proprio poder DELA, nao de token, ver
    on_artifact_dies). Documentar isso como decisao de arquitetura honesta
    (nao inventar um motor de combate novo so' pra 1 carta) - a metrica
    reportada em run_batch() e' um PROXY explicito (tokens em campo x
    anthem), nao dano real calculado."""
    if "Caretaker's Talent" not in state.battlefield:
        return
    if state.caretaker_level == 1 and remaining_mana(state) >= 1:
        spend_mana(state, 1)
        state.caretaker_level = 2
        state.caretaker_level2_reached = True
        # "create a token that's a copy of target token you control" -
        # so' aplica se ja' controlamos algum token; prioriza copiar o token
        # de maior valor (Treasure > Construct > outro), heuristica
        # documentada (maximiza valor da copia).
        if state.treasures > 0:
            create_treasures(state, 1, source="Caretaker's Talent nivel 2 (copia)")
            state.caretaker_tokens_copied_total += 1
        elif state.constructs > 0:
            create_constructs(state, 1, source="Caretaker's Talent nivel 2 (copia)")
            state.caretaker_tokens_copied_total += 1
        elif state.other_tokens > 0:
            create_other_tokens(state, 1, source="Caretaker's Talent nivel 2 (copia)")
            state.caretaker_tokens_copied_total += 1
    if state.caretaker_level == 2 and remaining_mana(state) >= 4:
        spend_mana(state, 4)
        state.caretaker_level = 3
        state.caretaker_level3_reached = True


def main_phase(state: GameState):
    if not state.commander_in_play and can_cast(state, COMMANDER):
        cast_card(state, COMMANDER)

    try_black_market_connections(state)

    while True:
        castables = [n for n in state.hand if n not in LAND_NAMES and can_cast(state, n)]
        if castables:
            if TREASURE_MAXIMIZE_POLICY:
                castables.sort(key=lambda n: (not is_treasure_source(n), CARD_DB[n].mv))
            else:
                castables.sort(key=lambda n: CARD_DB[n].mv)
            cast_card(state, castables[0])
            continue
        # Achado real 2026-08-31 (rodada ampliada): Phyrexian Reclamation
        # (recursao repetivel) usa a mana que sobrar depois de tudo
        # castable na mao - pode devolver uma criatura que vira castable de
        # novo no proximo giro deste loop (`continue`), por isso entra
        # dentro do mesmo while.
        if try_phyrexian_reclamation(state):
            continue
        break

    # Achado real 2026-08-31 (rodada ampliada, categoria 13): engine de
    # nivel do Caretaker's Talent - so' depois de esgotar tudo que da' pra
    # conjurar/recuperar (heuristica: desenvolver board novo > subir nivel
    # de uma carta ja' resolvida).
    try_level_caretakers_talent(state)

    # Jan Jansen: 2 modos, 1x cada por turno (tap) — prioriza Constructs se
    # tiver artefato nao-criatura descartavel, senao Treasure de artefato-criatura.
    if "Jan Jansen, Chaos Crafter" in state.battlefield and not state.jan_jansen_used_this_turn:
        if state.treasures > 0:
            sacrifice_treasures(state, 1)
            create_constructs(state, 2, source="Jan Jansen")
            state.jan_jansen_used_this_turn = True
        elif state.constructs > 0:
            sacrifice_constructs(state, 1)
            create_treasures(state, 2, source="Jan Jansen")
            state.jan_jansen_used_this_turn = True

    # Impulse pool: tenta jogar o que der
    while play_from_impulse(state):
        pass


def combat_step(state: GameState):
    animated = 0
    if state.commander_in_play and state.treasures > 0:
        animated = state.treasures  # Vihaan: Treasures viram 3/3 outlaw ate o final do turno
    state.treasures_animated_this_combat = animated

    ready_creatures = [n for n in state.battlefield
                       if is_creature_card(n) and n != COMMANDER
                       and (state.creature_cast_turn.get(n, -1) < state.turn or "haste" in CARD_DB[n].tags)]
    ready_constructs = max(0, state.constructs - state.constructs_sick)
    ready_other = max(0, state.other_tokens - state.other_tokens_sick)

    total_attackers = animated + len(ready_creatures) + ready_constructs + ready_other
    if total_attackers <= 0:
        return
    state.combat_attacks_total += 1

    outlaw_attacking = animated > 0 or any(is_outlaw(n) for n in ready_creatures)
    any_creature_attacking = len(ready_creatures) + ready_constructs + ready_other + animated > 0

    if "Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel" in ready_creatures:
        try_sephiroth_sac_draw(state)

    if "Captain Lannery Storm" in state.battlefield and "Captain Lannery Storm" in ready_creatures:
        create_treasures(state, 1, source="Captain Lannery Storm ataca")
    if "Goldspan Dragon" in state.battlefield and "Goldspan Dragon" in ready_creatures:
        create_treasures(state, 1, source="Goldspan Dragon ataca")
    if "Kellogg, Dangerous Mind" in state.battlefield and "Kellogg, Dangerous Mind" in ready_creatures:
        create_treasures(state, 1, source="Kellogg ataca")
    if "Smaug the Magnificent" in state.battlefield and "Smaug the Magnificent" in ready_creatures:
        # "he deals damage equal to the number of Treasures you control to any target" —
        # proxy agregado (drain_damage_total), nunca vida real de oponente.
        drain(state, state.treasures)

    if any_creature_attacking:
        if "Olivia, Opulent Outlaw" in state.battlefield and outlaw_attacking:
            create_treasures(state, 1, source="Olivia (outlaw dano)")
        if "Professional Face-Breaker" in state.battlefield:
            create_treasures(state, 1, source="Professional Face-Breaker")
        if "Grim Hireling" in state.battlefield:
            create_treasures(state, 2, source="Grim Hireling")
        if "Orochi Soul-Reaver" in state.battlefield:
            create_treasures(state, 1, source="Orochi Soul-Reaver")
            if state.library:
                state.library.pop(0)
                create_other_tokens(state, 1, source="Orochi manifest")
        if "Aya of Alexandria" in state.battlefield and any(is_historic(n) for n in ready_creatures):
            create_other_tokens(state, 1, source="Aya of Alexandria")
        if "Grenzo, Havoc Raiser" in state.battlefield:
            pull_impulse(state, 1, deadline_turns=0)
        if "The Reaver Cleaver" in state.battlefield:
            create_treasures(state, 1, source="The Reaver Cleaver")

    if "Urabrask's Forge" in state.battlefield:
        state.forge_oil += 1
        create_other_tokens(state, 1, source="Urabrask's Forge")
        state.other_tokens -= 0  # token e sacrificado no end step, ver end_step

    if TREASURE_MAXIMIZE_POLICY:
        aggressive_treasure_destruction(state)


def end_step(state: GameState):
    if "Mahadi, Emporium Master" in state.battlefield:
        create_treasures(state, state.deaths_this_turn, source="Mahadi (fim do turno)")

    if "Prosper, Tome-Bound" in state.battlefield:
        pull_impulse(state, 1, deadline_turns=2)

    if "Laughing Jasper Flint" in state.battlefield:
        outlaws = sum(1 for n in state.battlefield if is_outlaw(n))
        pull_impulse(state, outlaws, deadline_turns=0)

    # Achado real 2026-08-31 (rodada ampliada): oraculo real e' "if you
    # gained life THIS TURN" - o codigo checava `life_gained_total`
    # (acumulado do JOGO INTEIRO), entao depois de qualquer 1 ponto de vida
    # ganho em qualquer turno anterior, a condicao ficava permanentemente
    # satisfeita pro resto da partida (recursao livre todo turno, sem
    # depender de ganhar vida DE NOVO). Corrigido pra usar o contador
    # per-turno (`life_gained_this_turn`, resetado em play_turn()).
    if "Witch of the Moors" in state.battlefield and state.life_gained_this_turn > 0:
        creatures_gy = [n for n in state.graveyard if is_creature_card(n)]
        if creatures_gy:
            best = max(creatures_gy, key=lambda n: CARD_DB[n].mv)
            state.graveyard.remove(best)
            state.hand.append(best)
            state.recursion_events_total += 1

    if "Urabrask's Forge" in state.battlefield and state.other_tokens > 0:
        sacrifice_other_tokens(state, 1)  # sacrifica o token X/1 do proprio turno

    if ("Revel in Riches" in state.battlefield and state.treasures >= 10
            and state.revel_condition_met_turn is None):
        state.revel_condition_met_turn = state.turn

    if state.constructs_sick or state.other_tokens_sick:
        state.constructs_sick = 0
        state.other_tokens_sick = 0


def play_turn(state: GameState, is_first_turn: bool, on_play: bool):
    state.turn += 1
    state.lands_played_this_turn = 0
    state.mana_spent_this_turn = 0
    state.tapped_lands_this_turn = set()
    state.spells_cast_this_turn = 0
    state.commits_crime_this_turn = False
    state.treasure_spent_this_turn = False
    state.cascade_used_this_turn = False
    state.caretaker_drawn_this_turn = False
    state.kambal_drawn_this_turn = False
    state.black_market_connections_triggered_this_turn = False
    state.life_gained_this_turn = 0
    state.bonus_mana_pool = 0
    state.treasures_animated_this_combat = 0
    state.jan_jansen_used_this_turn = False
    state.deaths_this_turn = 0
    state.sephiroth_deaths_this_turn = 0

    if "Smaug the Magnificent" in state.battlefield:
        create_treasures(state, 1, source="Smaug the Magnificent (upkeep)")

    if not (is_first_turn and on_play):
        if state.library:
            state.hand.append(state.library.pop(0))  # compra normal do turno, nao conta como "extra"

    play_land(state)
    main_phase(state)
    combat_step(state)
    main_phase(state)  # pos-combate — usa mana bonus gerada por sac outlets no combate

    # Magda: gatilho "whenever you commit a crime" (1x/turno) so pode ser
    # checado depois das main phases, que e quando as magicas que cometem
    # crime (Path to Exile, Council's Judgment etc) sao de fato conjuradas.
    # BUG CORRIGIDO (2026-08-22): antes essa checagem rodava logo apos o
    # reset de commits_crime_this_turn=False, ou seja, sempre lia False —
    # o gatilho da Magda nunca disparava em nenhuma partida simulada.
    if "Magda, the Hoardmaster" in state.battlefield and state.commits_crime_this_turn:
        create_treasures(state, 1, source="Magda (crime)")

    end_step(state)


def simulate_one(seed: int, turns: int = 8):
    rng = random.Random(seed)
    hand, lib, mulls = mulligan(rng)
    state = GameState(hand=hand, library=lib, mulligans=mulls)
    for t in range(turns):
        play_turn(state, is_first_turn=(t == 0), on_play=True)
        if state.revel_condition_met_turn is not None:
            break
    return state


def run_batch(n: int, seed_base: int, turns: int = 8):
    states = [simulate_one(seed_base + i, turns=turns) for i in range(n)]

    def avg(vals):
        return sum(vals) / len(vals) if vals else 0.0

    print(f"n={n}, seed_base={seed_base}, turns={turns}")
    print(f"Avg mulligans: {avg([s.mulligans for s in states]):.2f}")
    cmd_turn = [s.commander_cast_turn for s in states if s.commander_cast_turn is not None]
    print(f"Turno medio de conjuracao do Vihaan: {avg(cmd_turn):.2f} | mediana: {statistics.median(cmd_turn) if cmd_turn else float('nan'):.1f}")
    print(f"Nunca conjurado em {turns} turnos: {100*sum(1 for s in states if s.commander_cast_turn is None)/n:.1f}%")
    print(f"Avg Treasures criados (total no jogo): {avg([s.treasures_created_total for s in states]):.2f}")
    print(f"Avg Treasures em campo no fim: {avg([s.treasures for s in states]):.2f}")
    print(f"Avg Treasures sacrificados (total): {avg([s.treasures_sacrificed_total for s in states]):.2f}")
    print(f"Avg Constructs criados: {avg([s.constructs_created_total for s in states]):.2f}")
    print(f"Avg outros tokens criados: {avg([s.other_tokens_created_total for s in states]):.2f}")
    print(f"Avg mortes de criatura: {avg([s.creature_deaths_total for s in states]):.2f}")
    print(f"Avg mortes de artefato: {avg([s.artifact_deaths_total for s in states]):.2f}")
    print(f"Avg drain/dano agregado (proxy, NAO vida real de oponente): {avg([s.drain_damage_total for s in states]):.2f}")
    print(f"Avg vida ganha: {avg([s.life_gained_total for s in states]):.2f}")
    print(f"Avg cartas compradas extra: {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"Avg cascades via Rain of Riches: {avg([s.cascades_triggered for s in states]):.2f}")
    print(f"Avg combates com pelo menos 1 atacante: {avg([s.combat_attacks_total for s in states]):.2f}")
    print(f"Avg Treasures sacrificados ANIMADOS via Ashnod's Altar (criatura+artefato+token junto): {avg([s.animated_treasures_sacrificed_total for s in states]):.2f}")
    print(f"Avg mana bonus gerada por sac outlets pos-combate (total no jogo): {avg([s.bonus_mana_generated_total for s in states]):.2f}")

    # Achado real 2026-08-31 (rodada ampliada) — Sephiroth transform, agora
    # que `sephiroth_transformed` e' de fato lido em algum lugar.
    seph_transform_pct = 100 * sum(1 for s in states if s.sephiroth_transformed) / n
    print(f"Sephiroth transformado (4 mortes no mesmo turno, emblem Super Nova ativo) — % de jogos: {seph_transform_pct:.1f}%")
    print(f"Avg cartas compradas via sac do Sephiroth (as 2 faces somadas): {avg([s.sephiroth_sac_draws_total for s in states]):.2f}")

    # Achado real 2026-08-31 (rodada ampliada) — Caretaker's Talent, engine
    # de nivel nova.
    car_lvl2_pct = 100 * sum(1 for s in states if s.caretaker_level2_reached) / n
    car_lvl3_pct = 100 * sum(1 for s in states if s.caretaker_level3_reached) / n
    print(f"Caretaker's Talent nivel 2 alcancado — % de jogos: {car_lvl2_pct:.1f}% | nivel 3: {car_lvl3_pct:.1f}%")
    # Proxy explicito (documentado em try_level_caretakers_talent): nao ha'
    # motor de poder/resistencia de criatura neste simulador pra aplicar o
    # anthem +2/+2 do nivel 3 numa metrica de dano real - reporta so' o
    # bonus de poder agregado IMPLICADO (2 * criaturas-token em campo no fim
    # do jogo, so' nos jogos em que o nivel 3 foi alcancado), nao dano
    # calculado de fato.
    anthem_states = [s for s in states if s.caretaker_level3_reached]
    if anthem_states:
        avg_tokens_at_lvl3 = avg([s.constructs + s.other_tokens for s in anthem_states])
        print(f"  Proxy anthem nivel 3 (so' jogos com nivel 3): Avg criaturas-token em campo no fim: {avg_tokens_at_lvl3:.2f}"
              f" -> bonus agregado implicado: +{2*avg_tokens_at_lvl3:.2f}/+{2*avg_tokens_at_lvl3:.2f} no total do board (NAO dano calculado - proxy)")

    revel_hits = sum(1 for s in states if s.revel_condition_met_turn is not None)

    # -----------------------------------------------------------------
    # Categoria 10 (goldfish-sim-card-rules.md) — as 5 metricas basicas
    # obrigatorias, reportadas de forma auditavel e separada. Achado real
    # 2026-08-31 (rodada ampliada): RECURSION e INTERACTION nao tinham
    # linha formal propria antes desta correcao (existiam so' como tags
    # decorativas/efeitos individuais sem contador agregado).
    # -----------------------------------------------------------------
    print()
    print("--- Metricas basicas obrigatorias (categoria 10) ---")
    rocks_final = avg([sum(1 for c in ("Sol Ring", "Arcane Signet") if c in s.battlefield) for s in states])
    print(f"RAMP: Avg mana rocks resolvidos no fim (Sol Ring + Arcane Signet, max 2): {rocks_final:.2f}"
          f" | Avg Treasures criados no jogo (motor de ramp central do deck, ver secao 3/5 da auditoria): {avg([s.treasures_created_total for s in states]):.2f}")
    print(f"DRAW: Avg cartas compradas extra (alem da compra normal do turno): {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"INTERACTION: Avg remocao/wipe conjurados por jogo (Path to Exile, Shoot the Sheriff, Council's Judgment,"
          f" Deadly Derision, Requisition Raid, Blasphemous Act, Blood Money): {avg([s.removal_cast_total for s in states]):.2f}")
    print(f"RECURSION: Avg cartas recuperadas do cemiterio por jogo (Sevinne's Reclamation, Phyrexian Reclamation,"
          f" Back in Town, Lich-Knights' Conquest, Witch of the Moors): {avg([s.recursion_events_total for s in states]):.2f}"
          f" | das quais via Phyrexian Reclamation (repetivel): {avg([s.phyrexian_reclamation_activations_total for s in states]):.2f}")
    print(f"FINISHER/LETHALITY: Revel in Riches (10+ Treasures, alt-win) — condicao satisfeita: {100*revel_hits/n:.1f}% dos jogos"
          + (f" | turno medio: {avg([s.revel_condition_met_turn for s in states if s.revel_condition_met_turn is not None]):.2f}" if revel_hits else "")
          + f" | Avg drain/dano agregado proxy (NAO vida real de oponente, sem lethality de combate direta modelada neste sim): {avg([s.drain_damage_total for s in states]):.2f}")
    return states


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    states = run_batch(n=3000, seed_base=6000000, turns=8)

    with open("vihaan_v1_runs.jsonl", "w") as f:
        for s in states:
            f.write(json.dumps({
                "mulligans": s.mulligans,
                "commander_cast_turn": s.commander_cast_turn,
                "treasures_created_total": s.treasures_created_total,
                "treasures_final": s.treasures,
                "creature_deaths_total": s.creature_deaths_total,
                "drain_damage_total": s.drain_damage_total,
                "cards_drawn_extra": s.cards_drawn_extra,
                "revel_condition_met_turn": s.revel_condition_met_turn,
            }) + "\n")
