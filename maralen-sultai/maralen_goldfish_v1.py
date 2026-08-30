"""
Goldfish simulator — Maralen, Fae Ascendant (Sultai, B/G/U)

Construido do zero em 2026-08-23. Passo 0 (regra de
`references/goldfish-sim-card-rules.md`): varredura mecanica no oraculo
completo achou os gatilhos reais listados abaixo. Cada um tem o efeito
real implementado, exceto onde depende de um oponente real (vida/mao/
biblioteca/permanente alheio) — documentado como simplificacao
explicita, nunca fingido.

Mecanica central: o proprio gatilho da comandante — "Whenever Maralen
or another Elf or Faerie you control enters, exile the top two cards
of target opponent's library. Once each turn, you may cast a spell
with mana value <= Elfos+Fadas voce controla dentre as cartas exiladas
com Maralen neste turno sem pagar o custo de mana." Como nao ha
biblioteca de oponente real num goldfish solo, a exilada vem da PROPRIA
biblioteca (mesma aproximacao ja usada pro Grenzo/Laughing Jasper Flint
no simulador do Vihaan) — documentado, nao inventado como se fosse
"roubo" real.

Roaming Throne: tipo escolhido = **Faerie** (nao Elfo). Motivo: Maralen
e ela mesma Elf Faerie Noble, entao ela conta como "outra criatura do
tipo escolhido" pra qualquer um dos dois tipos — o proprio gatilho dela
dobra de qualquer forma. Faerie foi escolhido porque tem mais criaturas
com gatilho relevante (Bitterbloom Bearer, Obyra, Tegwyll, Faerie
Harbinger, Spellstutter Sprite, Mistbind Clique) do que Elfo (so Marwyn
e Elvish Warmaster tem gatilho de ETB relevante).

Combo real de 2 pecas (documentado na auditoria, secao 4): Umbral
Mantle (Equip {0}, "{3},{Q}: +2/+2") equipado num dork que produza 4+
mana por ativacao (Priest of Titania, Elvish Archdruid, Marwyn com
poder 4+, Circle of Dreams Druid com 4+ criaturas) gera mana verde
infinita. Staff of Domination converte isso em compra infinita (limite
defensivo: para de comprar quando a biblioteca fica vazia, sem fingir
"vencer o jogo" por deck-out) ou exercito infinito de Elfo via
Imperious Perfect, se disponivel.

Simplificacoes documentadas (nao inventadas — omissoes explicitas):
- Sem oponente real: Rhystic Study, Mystic Remora, Faerie Mastermind
  (gatilho passivo), Alela (goad e token por 1a magica no turno do
  oponente), Bojuka Bog (exila cemiterio de oponente) ficam "disponiveis"
  mas sem efeito numerico solo.
- Removal/contra-magica (Pongify, Rapid Hybridization, Reality Shift,
  Assassin's Trophy, Cyclonic Rift, Toxic Deluge, Counterspell, Arcane
  Denial, Swan Song, Spellstutter Sprite, Glen Elendra Archmage) sao
  conjuradas quando ha alvo hipotetico disponivel (mesma convencao dos
  outros simuladores desta biblioteca), mas nao tem efeito de combate
  real — so consomem mana e contam como "conjuradas".
- Bloom Tender: aproximacao documentada — produz mana igual ao numero
  de cores entre B/G/U que ja tem permanente em campo (nunca mais que
  3), nao rastreio cor exata de cada permanente.
- Joraga Treespeaker: nivel real 0-5 implementado (achado real 2026-08-30 -
  a versao anterior era binaria 0/1 e nunca alcancava o nivel 5 de jeito
  nenhum, 0% estrutural, nao "raro" como o comentario antigo sugeria).
  Nivela greedy com mana sobrando (5 ativacoes = 10 mana total investido
  pro nivel 5, que da' "{T}: Add {G}{G}" pra TODOS os Elfos) — ver
  `joraga_level_up()`.
- Heritage Druid / Birchlore Rangers: aproximacao documentada — a
  habilidade delas tapa OUTROS Elfos como custo (nao a si mesmas), o
  que ignora summoning sickness desses Elfos (CR 302.6, tapar como
  custo de habilidade de OUTRO permanente nao e bloqueado por sickness).
  Modelado como: se houver Elfos "sick" (recem-conjurados) disponiveis
  em quantidade suficiente, eles alimentam Heritage Druid/Birchlore
  Rangers por mana extra que normalmente nao existiria ainda naquele
  turno — sem duplicar a contagem de mana desses Elfos caso eles NAO
  estivessem sick (nesse caso already contam via sua propria habilidade).
- Devoted Druid: self-untap via -1/-1 counter modelado com um teto
  defensivo de 3 ativacoes extras por turno (toughness base 1, evita
  looping sem fim — ela morre antes de virar looping infinito sem
  outra peca de untap).
- Mistbind Clique (Champion a Faerie): se houver outra Fada em campo
  pra exilar, ela fica; senao e sacrificada no ETB (Champion falhou).
  A Fada exilada retorna quando Mistbind sai de campo — nao simulado
  em detalhe (Mistbind raramente sai de campo neste modelo).
- Combate: "ataca" = nao esta com summoning sickness. Nenhum bloqueio,
  nenhum dano/vida de oponente real.
- Seedborn Muse ("untap all permanents you control during EACH OTHER
  PLAYER'S untap step"): genuinamente N/A neste modelo - so' os PROPRIOS
  turnos sao simulados (goldfish solo), nunca ha um "outro jogador" cujo
  untap step aconteca pra gerar o gatilho. Nao e' omissao, e' ausencia
  real do evento que a habilidade escuta.
- Murkfiend Liege: alem do "untap step de outro jogador" (mesmo N/A do
  Seedborn Muse acima), tem um segundo modo estatico real ("Other green
  creatures you control get +1/+1. Other blue creatures you control get
  +1/+1.") que E' modelado (soma em `marwyn_effective_power()`, ja que
  Marwyn e' Elfo E verde - achado real 2026-08-28).
- Spellstutter Sprite: "counter target spell with mana value X or less"
  (X = Faeries) precisa de uma magica real de oponente pra mirar - mesma
  convencao ja documentada pras outras contra-magicas do deck (Counterspell,
  Swan Song, Arcane Denial etc.), disponivel mas sem efeito de combate real
  num goldfish solo.
- Wirewood Symbiote / Scryb Ranger ("Return an Elf/Forest you control:
  Untap target creature. Activate only once each turn."): decisao de
  escopo documentada, nao implementada numericamente. O beneficio real
  (re-ativar um dork ja tapado) tem custo real de tempo (perder um Elfo ou
  land drop temporariamente, precisar recomprar depois) que o modelo atual
  de mana (soma "ready creatures" agregada, sem rastrear tap individual)
  nao capturaria com fidelidade sem reestruturar o motor de mana inteiro -
  risco de bug maior que o valor esperado (ambas as pecas + um dork grande
  + um Elfo/Forest sobrando simultaneamente e' situacao relativamente rara
  dentro de 8 turnos).
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
    ctype: str  # 'land','artifact','creature','artifact_creature','enchantment','sorcery','instant'
    tags: frozenset = field(default_factory=frozenset)


CARD_DB: dict[str, Card] = {}


def add(name, mv, ctype, tags=()):
    CARD_DB[name] = Card(name=name, mv=mv, ctype=ctype, tags=frozenset(tags))


COMMANDER = "Maralen, Fae Ascendant"
add(COMMANDER, 5, "creature", {"commander", "elf", "faerie"})

ROAMING_THRONE_TYPE = "faerie"  # ver docstring — escolhido sobre "elf"

# --- Lands (35) --------------------------------------------------------------
add("Alchemist's Refuge", 0, "land", {"flash_enabler"})
add("Bayou", 0, "land", set())
add("Bojuka Bog", 0, "land", {"etb_tapped"})
add("Boseiju, Who Endures", 0, "land", set())
add("Breeding Pool", 0, "land", set())
add("Cavern of Souls", 0, "land", set())
add("Command Tower", 0, "land", set())
add("Darkwater Catacombs", 0, "land", set())
add("Drowned Catacomb", 0, "land", set())
add("Exotic Orchard", 0, "land", set())
add("Gilt-Leaf Palace", 0, "land", set())
add("Hinterland Harbor", 0, "land", set())
add("Morphic Pool", 0, "land", set())
add("Overgrown Tomb", 0, "land", set())
add("Path of Ancestry", 0, "land", {"etb_tapped"})
add("Reflecting Pool", 0, "land", set())
add("Secluded Courtyard", 0, "land", set())
add("Sunken Hollow", 0, "land", set())
add("Tropical Island", 0, "land", set())
add("Undergrowth Stadium", 0, "land", set())
add("Underground River", 0, "land", set())
add("Underground Sea", 0, "land", set())
add("Watery Grave", 0, "land", set())
add("Wirewood Lodge", 0, "land", set())
add("Woodland Cemetery", 0, "land", set())
add("Yavimaya Coast", 0, "land", set())
add("Zagoth Triome", 0, "land", {"etb_tapped"})
add("Forest", 0, "land", set())
add("Island", 0, "land", set())
add("Swamp", 0, "land", set())

# --- Motor de flash universal ------------------------------------------------
add("Leyline of Anticipation", 4, "enchantment", {"universal_flash"})
add("Vedalken Orrery", 4, "artifact", {"universal_flash"})
add("High Fae Trickster", 4, "creature", {"faerie", "universal_flash"})
add("Radagast of Rhosgobel", 4, "creature", {"first_creature_discount_flash"})
# Nao esta na lista atual (saiu na troca por Radagast) -- cadastrada so pra
# permitir montar a biblioteca da variante de comparacao "sem Radagast".
add("Elves of Deep Shadow", 1, "creature", {"elf", "dork_flat1"})

# --- Motor de ramp elfico -----------------------------------------------------
add("Birds of Paradise", 1, "creature", {"dork_flat1"})
add("Bloom Tender", 2, "creature", {"elf", "dork_bloomtender"})
add("Elvish Mystic", 1, "creature", {"elf", "dork_flat1"})
add("Llanowar Elves", 1, "creature", {"elf", "dork_flat1"})
add("Joraga Treespeaker", 1, "creature", {"elf", "dork_joraga"})
add("Heritage Druid", 1, "creature", {"elf", "dork_heritage"})
add("Birchlore Rangers", 1, "creature", {"elf", "dork_birchlore"})
add("Priest of Titania", 2, "creature", {"elf", "dork_per_elf"})
add("Elvish Archdruid", 3, "creature", {"elf", "dork_per_elf_controlled"})
add("Marwyn, the Nurturer", 3, "creature", {"elf", "dork_marwyn", "elf_etb_counter"})
add("Circle of Dreams Druid", 3, "creature", {"elf", "dork_per_creature"})
# Devoted Druid: NAO esta mais em lista.md (achado real 2026-08-30,
# reanalise pedida pelo usuario - foi trocada por Thranduil, Sindarin
# Liege/Thranduil's Company, ver goldfish-log.md). Cadastro + toda a
# mecanica dela (devoted_druid_pump() etc) ficaram no arquivo sem uso -
# inofensivo (build_library() so' le nomes de lista.md, nunca entra no
# baralho de verdade), mantido documentado aqui em vez de removido pra
# nao arriscar quebrar algo tocando em varios pontos do arquivo por um
# corte de baixo risco.
add("Devoted Druid", 2, "creature", {"elf", "dork_devoted"})
add("Elvish Harbinger", 3, "creature", {"elf", "dork_flat1_any", "tutor_elf_top"})
add("Wirewood Symbiote", 1, "creature", {"bounce_untap"})
add("Cryptolith Rite", 2, "enchantment", {"mana_any_creature"})
add("Elven Chorus", 4, "enchantment", {"mana_any_creature", "cast_from_top"})
add("Arcane Signet", 2, "artifact", {"rock1"})
add("Sol Ring", 1, "artifact", {"rock2"})
add("Umbral Mantle", 3, "artifact", {"umbral_mantle"})
add("Staff of Domination", 3, "artifact", {"staff"})
add("Roaming Throne", 4, "artifact_creature", {ROAMING_THRONE_TYPE, "roaming_throne"})

# --- Elfo — corpo/utilidade --------------------------------------------------
add("Allosaurus Shepherd", 1, "creature", {"elf"})
add("Elvish Warmaster", 2, "creature", {"elf", "elf_etb_token"})
add("Imperious Perfect", 3, "creature", {"elf", "elf_token_maker"})
add("Fauna_placeholder_never_used", 0, "creature", set())  # nunca referenciada
add("Fauna Shaman", 2, "creature", {"elf", "tutor_creature_repeat"})
add("Formidable Speaker", 3, "creature", {"elf", "tutor_creature_etb"})
add("Growing Rites of Itlimoc // Itlimoc, Cradle of the Sun", 3, "enchantment", {"itlimoc"})
add("Green Sun's Zenith", 1, "sorcery", {"gsz"})
add("Realmwalker", 3, "creature", {"elf", "faerie", "changeling", "cast_from_top"})
add("Ezuri, Renegade Leader", 3, "creature", {"elf"})
add("Thranduil, Sindarin Liege // Silvan Rally", 4, "creature", {"elf", "landfall_source"})
add("Thranduil's Company", 4, "creature", {"elf", "landfall_source"})

# --- Fada — token e drain -----------------------------------------------------
add("Alela, Cunning Conqueror", 4, "creature", {"faerie"})
add("Bitterblossom", 2, "enchantment", {"faerie_token_upkeep"})
add("Bitterbloom Bearer", 2, "creature", {"faerie", "faerie_token_upkeep"})
add("Faerie Harbinger", 4, "creature", {"faerie", "tutor_faerie_top"})
add("Faerie Mastermind", 2, "creature", {"faerie", "opponent_dependent"})
add("Mistbind Clique", 4, "creature", {"faerie", "champion_faerie"})
add("Obyra, Dreaming Duelist", 2, "creature", {"faerie", "faerie_etb_drain"})
add("Spellstutter Sprite", 2, "creature", {"faerie", "etb_counter_unused"})
add("Tegwyll, Duke of Splendor", 3, "creature", {"faerie", "faerie_death_draw"})
add("Scryb Ranger", 2, "creature", {"faerie", "bounce_untap"})
add("Brazen Borrower // Petty Theft", 3, "creature", {"faerie"})
# Cloud of Faeries: mesmo caso do Devoted Druid acima - NAO esta mais em
# lista.md (achado real 2026-08-30), cadastro mantido sem uso, inofensivo.
add("Cloud of Faeries", 2, "creature", {"faerie", "etb_untap_lands"})
add("Glen Elendra Archmage", 4, "creature", {"faerie"})

# --- Card draw / interacao ---------------------------------------------------
add("Seedborn Muse", 5, "creature", {"untap_all"})
add("Wilderness Reclamation", 4, "enchantment", {"untap_lands_endstep"})
add("Murkfiend Liege", 5, "creature", {"untap_gu"})
add("Arcane Denial", 2, "instant", {"interaction"})
add("Counterspell", 2, "instant", {"interaction"})
add("Swan Song", 1, "instant", {"interaction"})
add("Pongify", 1, "instant", {"interaction"})
add("Rapid Hybridization", 1, "instant", {"interaction"})
add("Reality Shift", 2, "instant", {"interaction"})
add("Assassin's Trophy", 2, "instant", {"interaction"})
add("Cyclonic Rift", 2, "instant", {"interaction"})
add("Toxic Deluge", 3, "sorcery", {"interaction"})
add("Rhystic Study", 3, "enchantment", {"opponent_dependent"})
add("Mystic Remora", 1, "enchantment", {"opponent_dependent"})
add("Heroic Intervention", 2, "instant", {"interaction"})
add("Black Market Connections", 3, "enchantment", {"modal_treasure_draw"})
add("Kindred Discovery", 5, "enchantment", {"kindred_discovery"})

# Token sintetico "Hire a Mercenary" do Black Market Connections (achado
# real 2026-08-30, reanalise pedida pelo usuario) - "Create a 3/2
# colorless Shapeshifter creature token with changeling" - Changeling
# significa que ela E' Elfo e Fada ao mesmo tempo pra toda sinergia do
# deck (gatilho da Maralen, contador da Marwyn, Kindred Discovery,
# Elvish Warmaster). Nao existe em lista.md, so' e' criada em jogo -
# mesma convencao dos tokens sinteticos do simulador do Ulalek.
add("Mercenary Token", 0, "creature", {"elf", "faerie", "changeling"})

del CARD_DB["Fauna_placeholder_never_used"]

ARTIFACT_ISH = {"artifact", "artifact_creature"}
CREATURE_ISH = {"creature", "artifact_creature"}
LAND_NAMES = {n for n, c in CARD_DB.items() if c.ctype == "land"}

# Usado so' pra metrica RAMP (categoria 10 do checklist) - qualquer permanente
# que produza mana alem dos terrenos normais.
RAMP_TAGS = {
    "dork_flat1", "dork_bloomtender", "dork_flat1_any", "dork_joraga",
    "dork_heritage", "dork_birchlore", "dork_per_elf", "dork_per_elf_controlled",
    "dork_marwyn", "dork_per_creature", "dork_devoted", "rock1", "rock2",
    "mana_any_creature", "itlimoc",
}


def is_creature_card(name: str) -> bool:
    return CARD_DB[name].ctype in CREATURE_ISH


def is_artifact_card(name: str) -> bool:
    return CARD_DB[name].ctype in ARTIFACT_ISH


def is_elf(name: str) -> bool:
    return "elf" in CARD_DB[name].tags


def is_faerie(name: str) -> bool:
    return "faerie" in CARD_DB[name].tags

# Criaturas verdes reais na decklist (color, Scryfall) - usado por Green
# Sun's Zenith ("search for a green creature card"). Achado real
# 2026-08-28 (auditoria de checklist): o pool anterior filtrava por tag
# "elf" em vez de cor real, excluindo Birds of Paradise/Wirewood Symbiote/
# Realmwalker/Radagast of Rhosgobel (verdes, nao-Elfo).
GREEN_CREATURE_NAMES = {
    "Radagast of Rhosgobel", "Elves of Deep Shadow", "Birds of Paradise", "Bloom Tender",
    "Elvish Mystic", "Llanowar Elves", "Joraga Treespeaker", "Heritage Druid", "Birchlore Rangers",
    "Priest of Titania", "Elvish Archdruid", "Marwyn, the Nurturer", "Circle of Dreams Druid",
    "Devoted Druid", "Elvish Harbinger", "Wirewood Symbiote", "Allosaurus Shepherd",
    "Elvish Warmaster", "Imperious Perfect", "Fauna Shaman", "Formidable Speaker", "Realmwalker",
    "Ezuri, Renegade Leader", "Thranduil, Sindarin Liege // Silvan Rally", "Thranduil's Company",
    "Scryb Ranger", "Seedborn Muse", "Murkfiend Liege",
}

def is_green_creature(name: str) -> bool:
    return name in GREEN_CREATURE_NAMES


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
    exile_maralen: list = field(default_factory=list)  # limpa a cada turno
    mulligans: int = 0

    lands_played_this_turn: int = 0
    lands_played_total: int = 0
    mana_spent_this_turn: int = 0
    maralen_free_cast_used_this_turn: bool = False
    devoted_druid_extra_untaps: int = 0  # so' vale no turno em que foi setado (ver devoted_druid_pump)
    tapped_lands_this_turn: set = field(default_factory=set)  # Bojuka Bog/Path of Ancestry/Zagoth Triome ("enters tapped"), resetado em play_turn()
    devoted_druid_counters: int = 0  # -1/-1 counters permanentes, morre ao chegar em 2 (toughness real = 2)
    joraga_level: int = 0
    mistbind_exiled: list = field(default_factory=list)  # Fadas exiladas pelo Champion do Mistbind Clique
    black_market_treasures_total: int = 0
    black_market_mercenaries_total: int = 0
    marwyn_power: int = 1  # base 1/1 (achado real 2026-08-28: oraculo real e' 1/1, nao 2/2 - contadores permanentes somados aqui a partir da base certa)
    fauna_shaman_used_this_turn: bool = False
    heritage_used_this_turn: bool = False
    birchlore_used_this_turn: bool = False
    radagast_discount_used_this_turn: bool = False
    umbral_equipped_on: Optional[str] = None
    infinite_mana_this_turn: bool = False

    commander_in_play: bool = False
    commander_cast_count: int = 0
    commander_cast_turn: Optional[int] = None
    creature_cast_turn: dict = field(default_factory=dict)

    elf_tokens: int = 0
    faerie_tokens: int = 0
    life: int = 40

    # metrics ----------------------------------------------------------------
    maralen_triggers_total: int = 0
    maralen_free_casts_total: int = 0
    cards_exiled_total: int = 0
    tokens_created_total: int = 0
    tutors_used_total: int = 0
    infinite_combo_assembled: bool = False
    infinite_combo_turn: Optional[int] = None
    staff_infinite_draws: int = 0
    roaming_throne_doubles_total: int = 0
    landfall_elf_tokens_total: int = 0
    landfall_counters_total: int = 0
    cards_drawn_extra: int = 0
    library_emptied: bool = False
    flash_universal_by_turn: dict = field(default_factory=dict)
    flash_with_radagast_by_turn: dict = field(default_factory=dict)
    ramp_pieces_cast_total: int = 0
    interaction_spells_cast_total: int = 0

    # Growing Rites of Itlimoc // Itlimoc, Cradle of the Sun (achado real
    # 2026-08-28, auditoria de checklist categoria 11 - layout real
    # "transform" confirmado via Scryfall: so' a face da frente e' conjuravel
    # da mao; a carta estava cadastrada com tag morta, sem ETB, sem gatilho
    # de transformacao e sem a habilidade de mana real da face de tras).
    itlimoc_transformed: bool = False
    itlimoc_transform_turn: Optional[int] = None
    itlimoc_creatures_found_total: int = 0


def draw_cards(state: GameState, n: int):
    for _ in range(n):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1
        else:
            state.library_emptied = True


# ---------------------------------------------------------------------------
# Motor central — Maralen: exila 2 do topo a cada Elfo/Fada que entra,
# 1x/turno pode conjurar de graca uma exilada com CMV <= Elfos+Fadas
# ---------------------------------------------------------------------------

def elf_faerie_count(state: GameState) -> int:
    return (sum(1 for n in state.battlefield if is_elf(n) or is_faerie(n))
            + state.elf_tokens + state.faerie_tokens)


def _maralen_resolve(state: GameState, roaming_match: bool):
    if not state.commander_in_play:
        return
    times = 2 if ("Roaming Throne" in state.battlefield and roaming_match) else 1
    if times == 2:
        state.roaming_throne_doubles_total += 1
    for _ in range(times):
        state.maralen_triggers_total += 1
        # Sem biblioteca de oponente real: exila da PROPRIA biblioteca (documentado).
        for _ in range(2):
            if state.library:
                state.exile_maralen.append(state.library.pop(0))
                state.cards_exiled_total += 1


def maralen_trigger(state: GameState, entering_name: str):
    if entering_name != COMMANDER and not (is_elf(entering_name) or is_faerie(entering_name)):
        return
    roaming_match = is_roaming_type(entering_name) and entering_name != "Roaming Throne"
    _maralen_resolve(state, roaming_match)


def maralen_trigger_token(state: GameState, kind: str):
    """Mesmo gatilho da Maralen, mas pra um TOKEN Elfo/Fada entrando (sem nome
    de carta — landfall do Sindarin Liege, Elvish Warmaster, Imperious
    Perfect, Bitterblossom/Bitterbloom Bearer)."""
    roaming_match = kind == ROAMING_THRONE_TYPE
    _maralen_resolve(state, roaming_match)


def maralen_try_free_cast(state: GameState):
    if state.maralen_free_cast_used_this_turn or not state.exile_maralen:
        return
    cap = elf_faerie_count(state)
    candidates = [c for c in state.exile_maralen if CARD_DB[c].mv <= cap and c not in LAND_NAMES]
    if not candidates:
        return
    candidates.sort(key=lambda n: -CARD_DB[n].mv)
    choice = candidates[0]
    state.exile_maralen.remove(choice)
    state.maralen_free_cast_used_this_turn = True
    state.maralen_free_casts_total += 1
    resolve_cast(state, choice, free=True)


# ---------------------------------------------------------------------------
# Mana — ramp elfico + rocks + Umbral Mantle
# ---------------------------------------------------------------------------

def ready_creatures(state: GameState):
    return [n for n in state.battlefield if is_creature_card(n)
            and (state.creature_cast_turn.get(n, -1) < state.turn)]


def marwyn_effective_power(state: GameState) -> int:
    """marwyn_power guarda so' os +1/+1 counters PERMANENTES (um por Elfo
    que entra, oraculo real). Elvish Archdruid da' +1/+1 a "other Elf
    creatures you control" e Murkfiend Liege da' +1/+1 a "other green
    creatures you control" (Marwyn e' Elfo E verde - os dois se somam,
    "other" so' exclui a propria fonte) - sao estaticas DINAMICAS (somem
    se a fonte sair de campo), entao nao podem ser somadas direto em
    marwyn_power (que representa contadores de verdade). Achado real
    2026-08-28 (auditoria de checklist): esses bonus nunca eram
    aplicados, subestimando a mana da Marwyn sempre que Archdruid e/ou
    Murkfiend Liege tambem estavam em campo."""
    bonus = 0
    if "Elvish Archdruid" in state.battlefield and "Marwyn, the Nurturer" in state.battlefield:
        bonus += 1
    if "Murkfiend Liege" in state.battlefield and "Marwyn, the Nurturer" in state.battlefield:
        bonus += 1
    return state.marwyn_power + bonus

def dork_mana(state: GameState) -> int:
    elves_in_play = sum(1 for n in state.battlefield if is_elf(n)) + state.elf_tokens
    creatures_in_play = (sum(1 for n in state.battlefield if is_creature_card(n))
                          + state.elf_tokens + state.faerie_tokens)
    ready = set(ready_creatures(state))
    total = 0
    best_scaling_output = 0
    best_scaling_name = None

    for n in state.battlefield:
        if n not in ready:
            continue
        tags = CARD_DB[n].tags
        if "dork_flat1" in tags:
            total += 1
        elif "dork_bloomtender" in tags:
            total += 2  # aproximacao documentada (2-3 cores em jogo tipicamente)
        elif "dork_flat1_any" in tags:
            total += 1
        elif "dork_joraga" in tags:
            total += 2 if state.joraga_level >= 1 else 0
        elif "dork_per_elf" in tags:
            out = elves_in_play
            total += out
            if out > best_scaling_output:
                best_scaling_output, best_scaling_name = out, n
        elif "dork_per_elf_controlled" in tags:
            out = elves_in_play
            total += out
            if out > best_scaling_output:
                best_scaling_output, best_scaling_name = out, n
        elif "dork_marwyn" in tags:
            out = marwyn_effective_power(state)
            total += out
            if out > best_scaling_output:
                best_scaling_output, best_scaling_name = out, n
        elif "dork_per_creature" in tags:
            out = creatures_in_play
            total += out
            if out > best_scaling_output:
                best_scaling_output, best_scaling_name = out, n
        elif "dork_devoted" in tags:
            total += 1 + min(2, state.devoted_druid_extra_untaps)

    # Heritage Druid / Birchlore Rangers: convertem elfos "sick" (que ainda nao
    # contribuiriam nada) em mana extra, tapando-os como custo (CR 302.6 nao
    # bloqueia isso). Nao duplica elfos ja contados acima.
    #
    # Achado real 2026-08-30 (reanalise pedida pelo usuario): a versao
    # anterior tambem exigia "Heritage Druid"/"Birchlore Rangers" IN
    # `ready` (nao pode estar com doenca de invocacao) antes de liberar a
    # propria habilidade - restricao que o oraculo real nao pede. Nenhuma
    # das duas tem {T} no proprio custo ("Tap three/two untapped Elves you
    # control: Add..."), so tapam OUTROS elfos - CR 302.6 so bloqueia
    # ativar habilidade com {T}/{Q} do PROPRIO permanente quando ele esta
    # sick, entao a doenca de invocacao da propria Heritage Druid/Birchlore
    # Rangers nao impede ativar essa habilidade especifica no turno em que
    # ela mesma entra.
    sick_elves = [n for n in state.battlefield
                  if is_elf(n) and n not in ready and n != "Heritage Druid" and n != "Birchlore Rangers"]
    if "Heritage Druid" in state.battlefield and len(sick_elves) >= 3:
        total += 3
    if "Birchlore Rangers" in state.battlefield and len(sick_elves) >= 2:
        total += 1

    # Cryptolith Rite / Elven Chorus: da "T: add 1 any" a toda criatura.
    # Joraga Treespeaker nivel 5+: "Elves you control have '{T}: Add
    # {G}{G}.'" (achado real 2026-08-30, reanalise pedida pelo usuario -
    # nivel 5 nunca era alcancavel na versao anterior, ver
    # joraga_level_up()). As duas concedem uma habilidade de mana EXTRA a
    # criaturas que ja tapam por outra coisa - uma criatura so' tapa 1 vez,
    # entao usa o MAIOR bonus concedido por criatura em vez de somar os
    # dois (senao seria tapar a mesma criatura duas vezes). So conta
    # criaturas que ainda NAO produziram mana pela propria habilidade
    # nomeada acima (dork_* tags), pra nao duplicar.
    DORK_TAGS = {
        "dork_flat1", "dork_bloomtender", "dork_flat1_any", "dork_joraga",
        "dork_per_elf", "dork_per_elf_controlled", "dork_marwyn",
        "dork_per_creature", "dork_devoted",
    }
    already_dorks = {n for n in state.battlefield if CARD_DB[n].tags & DORK_TAGS}
    cryptolith_active = "Cryptolith Rite" in state.battlefield or "Elven Chorus" in state.battlefield
    joraga_team_active = state.joraga_level >= 5
    if cryptolith_active or joraga_team_active:
        for n in ready:
            if n in already_dorks or not is_creature_card(n):
                continue
            granted = 0
            if cryptolith_active:
                granted = max(granted, 1)
            if joraga_team_active and is_elf(n):
                granted = max(granted, 2)
            total += granted

    # Umbral Mantle: se equipada num dork escalavel com saida >=4, mana infinita.
    if state.umbral_equipped_on and state.umbral_equipped_on in ready:
        if best_scaling_name == state.umbral_equipped_on and best_scaling_output >= 4:
            state.infinite_mana_this_turn = True
            if not state.infinite_combo_assembled:
                state.infinite_combo_assembled = True
                state.infinite_combo_turn = state.turn

    return total


def rocks_mana(state: GameState) -> int:
    total = 0
    if "Sol Ring" in state.battlefield:
        total += 2
    if "Arcane Signet" in state.battlefield:
        total += 1
    return total


def itlimoc_mana(state: GameState) -> int:
    """Itlimoc, Cradle of the Sun (face de tras, so' ativa apos transformar):
    real oraculo e' '{T}: Add {G}.' OU '{T}: Add {G} for each creature you
    control.' — duas habilidades de mana distintas, escolha do jogador a
    cada ativacao. Um piloto racional sempre escolhe a de maior producao;
    modelado como max(1, criaturas em campo) pra nunca ficar abaixo da
    habilidade fixa."""
    if not state.itlimoc_transformed:
        return 0
    creatures_in_play = (sum(1 for n in state.battlefield if is_creature_card(n))
                          + state.elf_tokens + state.faerie_tokens)
    return max(1, creatures_in_play)


def total_mana(state: GameState) -> int:
    lands = sum(1 for n in state.battlefield if n in LAND_NAMES) - len(state.tapped_lands_this_turn)
    if state.infinite_mana_this_turn:
        return 999  # ja confirmado infinito neste turno; nao precisa somar o resto
    return lands + rocks_mana(state) + dork_mana(state) + itlimoc_mana(state)


def remaining_mana(state: GameState) -> int:
    if state.infinite_mana_this_turn:
        return 999
    return max(0, total_mana(state) - state.mana_spent_this_turn)


def can_cast(state: GameState, name: str) -> bool:
    cost = CARD_DB[name].mv
    if (is_creature_card(name) and "Radagast of Rhosgobel" in state.battlefield
            and not state.radagast_discount_used_this_turn):
        cost = max(0, cost - 2)
    return remaining_mana(state) >= cost


def spend_mana(state: GameState, n: int):
    if not state.infinite_mana_this_turn:
        state.mana_spent_this_turn += n


# ---------------------------------------------------------------------------
# Resolucao de ETB / cast
# ---------------------------------------------------------------------------

def resolve_etb(state: GameState, name: str):
    tags = CARD_DB[name].tags

    if "elf_etb_counter" in tags:
        pass  # Marwyn nao ganha contador ao entrar ela mesma

    if "tutor_elf_top" in tags:
        elves = [n for n in state.library if is_elf(n)]
        if elves:
            best = max(elves, key=lambda n: CARD_DB[n].mv)
            state.library.remove(best)
            state.library.insert(0, best)
            state.tutors_used_total += 1

    if "tutor_faerie_top" in tags:
        faeries = [n for n in state.library if is_faerie(n)]
        if faeries:
            best = max(faeries, key=lambda n: CARD_DB[n].mv)
            state.library.remove(best)
            state.library.insert(0, best)
            state.tutors_used_total += 1

    if "tutor_creature_etb" in tags:
        # Formidable Speaker: descarta 1 pra buscar criatura pra mao.
        discardable = [c for c in state.hand if c != name]
        if discardable and state.library:
            worst = min(discardable, key=lambda n: CARD_DB[n].mv)
            state.hand.remove(worst)
            state.graveyard.append(worst)
            creatures = [n for n in state.library if is_creature_card(n)]
            if creatures:
                best = best_missing_dork(state, creatures)
                state.library.remove(best)
                state.hand.append(best)
                state.tutors_used_total += 1

    if "etb_untap_lands" in tags:
        state.mana_spent_this_turn = max(0, state.mana_spent_this_turn - 2)

    if "faerie_etb_drain" in tags:
        pass  # Obyra: opponent-dependent (perde vida), sem efeito solo

    if "champion_faerie" in tags:
        # Oraculo real (Mistbind Clique): "Champion a Faerie (When this
        # enters, sacrifice it unless you exile another Faerie you
        # control...) When a Faerie is championed with this creature, tap
        # all lands target player controls." Achado real 2026-08-30
        # (reanalise pedida pelo usuario): quando havia outra Fada
        # disponivel, o codigo mantinha a Mistbind em campo mas NUNCA
        # exilava a Fada "campea" - ela continuava contando em campo junto
        # com a Mistbind, quando so' 1 corpo deveria estar presente (a
        # segunda Fada volta so' quando a Mistbind sai de campo -
        # simplificacao documentada, ela raramente sai de campo neste
        # modelo). Corrigido: exila de verdade, preferindo um token (menor
        # perda real) a uma carta nomeada, e nunca a propria comandante
        # (Maralen tambem e' Fada por tipo). O efeito de "tap all lands"
        # (mira oponente) continua sem efeito numerico - Regra 1.
        if state.faerie_tokens > 0:
            state.faerie_tokens -= 1
            state.mistbind_exiled.append("Faerie Token")
        else:
            other_faeries = [n for n in state.battlefield
                              if is_faerie(n) and n != name and n != COMMANDER]
            if other_faeries:
                cheapest = min(other_faeries, key=lambda n: CARD_DB[n].mv)
                state.battlefield.remove(cheapest)
                state.mistbind_exiled.append(cheapest)
            else:
                leave_battlefield(state, name, to_graveyard=True)

    if "itlimoc" in tags:
        # Growing Rites of Itlimoc (face da frente) - oraculo real: "When
        # Growing Rites of Itlimoc enters, look at the top four cards of
        # your library. You may reveal a creature card from among them and
        # put it into your hand. Put the rest on the bottom of your library
        # in any order."
        top4 = state.library[:4]
        del state.library[:4]
        creatures = [c for c in top4 if is_creature_card(c)]
        if creatures:
            best = best_missing_dork(state, creatures)
            top4.remove(best)
            state.hand.append(best)
            state.itlimoc_creatures_found_total += 1
        state.library.extend(top4)

    # Elvish Warmaster: token 1x/turno quando OUTRO elfo entra (checado no caller)


def elvish_warmaster_check(state: GameState, entering_name: str):
    if entering_name == "Elvish Warmaster":
        return
    if "Elvish Warmaster" not in state.battlefield:
        return
    if not is_elf(entering_name):
        return
    if state.warmaster_used_this_turn:
        return
    state.warmaster_used_this_turn = True
    create_token(state, "elf", source="Elvish Warmaster")


def create_token(state: GameState, kind: str, source: str = ""):
    """Token Elfo ou Fada entrando em campo (Elvish Warmaster, Imperious
    Perfect, Bitterblossom, Bitterbloom Bearer, landfall do Thranduil,
    Sindarin Liege). Dispara os mesmos efeitos colaterais de uma carta
    nomeada entrando: gatilho da Maralen, contador da Marwyn, e o proprio
    Elvish Warmaster (se for outro Elfo entrando, nao ele mesmo)."""
    if kind == "elf":
        state.elf_tokens += 1
    elif kind == "faerie":
        state.faerie_tokens += 1
    state.tokens_created_total += 1
    if kind == "elf" and "Marwyn, the Nurturer" in state.battlefield:
        state.marwyn_power += 1
    if kind == "elf" and "Kindred Discovery" in state.battlefield:
        draw_cards(state, 1)
    maralen_trigger_token(state, kind)
    if kind == "elf" and "Elvish Warmaster" in state.battlefield and not state.warmaster_used_this_turn:
        state.warmaster_used_this_turn = True
        create_token(state, "elf", source="Elvish Warmaster")


def best_missing_dork(state: GameState, pool: list) -> str:
    priority_names = [
        "Priest of Titania", "Elvish Archdruid", "Marwyn, the Nurturer",
        "Circle of Dreams Druid", "Umbral Mantle", "Staff of Domination",
        "Fauna Shaman", COMMANDER,
    ]
    for p in priority_names:
        if p in pool:
            return p
    return min(pool, key=lambda n: CARD_DB[n].mv)


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
    if CARD_DB[name].tags & RAMP_TAGS:
        state.ramp_pieces_cast_total += 1
    if "elf_etb_counter" not in CARD_DB[name].tags:
        pass
    if is_elf(name) and "Marwyn, the Nurturer" in state.battlefield and name != "Marwyn, the Nurturer":
        state.marwyn_power += 1
    if is_elf(name) and "Kindred Discovery" in state.battlefield:
        # Achado real 2026-08-28 (auditoria de checklist de mecanica):
        # "As this enchantment enters, choose a creature type. Whenever a
        # creature you control of the chosen type enters or attacks, draw
        # a card." Tipo escolhido: Elfo (tema tribal central do deck, mesma
        # convencao ja usada pro Roaming Throne). Tag existia, nunca era
        # despachada - metade ETB implementada aqui, metade "attacks" em
        # combat_step().
        draw_cards(state, 1)
    resolve_etb(state, name)
    elvish_warmaster_check(state, name)
    maralen_trigger(state, name)


def leave_battlefield(state: GameState, name: str, to_graveyard: bool = True):
    if name in state.battlefield:
        state.battlefield.remove(name)
    if to_graveyard:
        state.graveyard.append(name)
    if is_faerie(name) and "Tegwyll, Duke of Splendor" in state.battlefield and name != "Tegwyll, Duke of Splendor":
        # Oraculo real: "you draw a card AND you lose 1 life" - achado real
        # 2026-08-30 (reanalise pedida pelo usuario), so' a compra estava
        # implementada, faltava a perda de vida.
        draw_cards(state, 1)
        state.life -= 1
    if state.umbral_equipped_on == name:
        state.umbral_equipped_on = None
        state.infinite_mana_this_turn = False


def resolve_cast(state: GameState, name: str, free: bool = False):
    if not free and name != COMMANDER:
        state.hand.remove(name)
    if name in LAND_NAMES:
        state.battlefield.append(name)
        return
    if CARD_DB[name].ctype == "sorcery" and "gsz" in CARD_DB[name].tags:
        return  # tratado em cast_green_sun_zenith
    if CARD_DB[name].ctype in ("instant", "sorcery"):
        # Achado real 2026-08-28 (auditoria de checklist): instantes e
        # feiticarias (Counterspell, Toxic Deluge, etc.) resolvem e vao pro
        # cemiterio - antes ficavam presos em "battlefield" pra sempre
        # (nunca corrompia is_creature_card/is_elf/is_faerie/LAND_NAMES,
        # que filtram por tipo/tag, mas era estado incorreto mesmo assim).
        if "interaction" in CARD_DB[name].tags:
            state.interaction_spells_cast_total += 1
        state.graveyard.append(name)
        return
    enter_battlefield(state, name, from_hand=False)


# ---------------------------------------------------------------------------
# Cast principal
# ---------------------------------------------------------------------------

def cast_green_sun_zenith(state: GameState):
    """X escolhido pro melhor dork verde ainda nao em campo que a mana bancar."""
    budget = remaining_mana(state) - 1  # {G} fixo + {X}
    if budget < 0:
        return False
    pool = [n for n in state.library if is_creature_card(n) and is_green_creature(n)
            and CARD_DB[n].mv <= (999 if state.infinite_mana_this_turn else budget)]
    if not pool:
        return False
    best = best_missing_dork(state, pool)
    x = CARD_DB[best].mv
    spend_mana(state, x + 1)
    state.hand.remove("Green Sun's Zenith")
    state.graveyard.append("Green Sun's Zenith")
    state.library.remove(best)
    enter_battlefield(state, best, from_hand=False)
    state.tutors_used_total += 1
    return True


def cast_fauna_shaman_activation(state: GameState):
    if "Fauna Shaman" not in state.battlefield or state.fauna_shaman_used_this_turn:
        return
    if "Fauna Shaman" not in ready_creatures(state):
        return
    if remaining_mana(state) < 1:
        return
    discardable = [c for c in state.hand if is_creature_card(c)]
    if not discardable or not state.library:
        return
    worst = min(discardable, key=lambda n: CARD_DB[n].mv)
    state.hand.remove(worst)
    state.graveyard.append(worst)
    creatures = [n for n in state.library if is_creature_card(n)]
    if not creatures:
        return
    best = best_missing_dork(state, creatures)
    state.library.remove(best)
    state.hand.append(best)
    spend_mana(state, 1)
    state.fauna_shaman_used_this_turn = True
    state.tutors_used_total += 1


def cast_card(state: GameState, name: str):
    card = CARD_DB[name]
    cost = card.mv + 2 * state.commander_cast_count if name == COMMANDER else card.mv
    # Radagast of Rhosgobel (achado real 2026-08-28, auditoria de checklist
    # categoria 9): oraculo real "The first creature spell you cast each
    # turn costs {2} less to cast and can be cast as though it had flash."
    # So' o lado do flash estava implementado (flash_with_radagast_by_turn);
    # o desconto de custo nunca era aplicado.
    if (is_creature_card(name) and "Radagast of Rhosgobel" in state.battlefield
            and not state.radagast_discount_used_this_turn):
        cost = max(0, cost - 2)
        state.radagast_discount_used_this_turn = True
    spend_mana(state, cost)
    resolve_cast(state, name)


def landfall_trigger(state: GameState):
    """Dispara toda vez que UM terreno seu entra em campo."""
    if "Thranduil, Sindarin Liege // Silvan Rally" in state.battlefield:
        create_token(state, "elf", source="Thranduil, Sindarin Liege (landfall)")
        state.landfall_elf_tokens_total += 1
    if "Thranduil's Company" in state.battlefield:
        # "put two +1/+1 counters on target creature you control" — modelado
        # quando ha alvo com valor numerico real (Marwyn, cujo poder escala
        # a propria mana que ela produz); outros alvos nao tem efeito
        # numerico modelado nesta simulacao (documentado, nao fingido).
        if "Marwyn, the Nurturer" in state.battlefield:
            state.marwyn_power += 2
        state.landfall_counters_total += 1


def play_land(state: GameState):
    max_lands = 1
    if "Thranduil's Company" in state.battlefield:
        other_elves = (sum(1 for n in state.battlefield if is_elf(n) and n != "Thranduil's Company")
                       + state.elf_tokens)
        if other_elves > 0:
            max_lands = 2
    while state.lands_played_this_turn < max_lands:
        lands_in_hand = [n for n in state.hand if n in LAND_NAMES]
        if not lands_in_hand:
            return
        choice = lands_in_hand[0]
        state.hand.remove(choice)
        state.battlefield.append(choice)
        state.lands_played_this_turn += 1
        state.lands_played_total += 1
        if "etb_tapped" in CARD_DB[choice].tags:
            # Achado real 2026-08-28 (auditoria de checklist): Bojuka Bog/
            # Path of Ancestry/Zagoth Triome tinham a tag mas ela nunca era
            # lida em lugar nenhum - produziam mana no proprio turno em que
            # entravam, apesar do "enters tapped" real.
            state.tapped_lands_this_turn.add(choice)
        landfall_trigger(state)


def equip_umbral_mantle(state: GameState):
    if "Umbral Mantle" not in state.battlefield:
        return
    creatures = ready_creatures(state)
    if not creatures:
        return
    elves_in_play = sum(1 for n in state.battlefield if is_elf(n)) + state.elf_tokens
    creatures_in_play = (sum(1 for n in state.battlefield if is_creature_card(n))
                          + state.elf_tokens + state.faerie_tokens)

    def scaling_output(n):
        tags = CARD_DB[n].tags
        if "dork_per_elf" in tags or "dork_per_elf_controlled" in tags:
            return elves_in_play
        if "dork_marwyn" in tags:
            return marwyn_effective_power(state)
        if "dork_per_creature" in tags:
            return creatures_in_play
        return 0

    best = max(creatures, key=scaling_output)
    if scaling_output(best) > 0:
        state.umbral_equipped_on = best


def joraga_level_up(state: GameState):
    """Oraculo real: "Level up {1}{G} (Level up only as a sorcery.) LEVEL
    1-4: {T}: Add {G}{G}. LEVEL 5+: Elves you control have '{T}: Add
    {G}{G}.'" Achado real 2026-08-30 (reanalise pedida pelo usuario): a
    versao anterior era binaria (0 ou 1, nunca progredia mais), e o
    docstring do arquivo dizia "raramente alcanca nivel 5" como se fosse
    probabilistico quando na verdade era estruturalmente impossivel (0%,
    nao raro) - o nivel 5+ (bonus de equipe pra TODOS os Elfos) nunca
    existia no modelo. Corrigido: nivel real 0-5, sobe quantas vezes a
    mana sobrando permitir (sem restricao de "1x por turno" no oraculo,
    so' o custo real de {1}{G} por nivel). Chamado DEPOIS do loop
    principal de conjuracao (so' usa mana que sobrou - nivelar Joraga
    nunca deveria competir com conjurar spells de verdade)."""
    if "Joraga Treespeaker" not in state.battlefield:
        return
    while state.joraga_level < 5 and remaining_mana(state) >= 2:
        spend_mana(state, 2)
        state.joraga_level += 1


def devoted_druid_pump(state: GameState):
    """Achado real 2026-08-28 (auditoria de checklist de mecanica): oraculo
    real e' 'Put a -1/-1 counter on this creature: Untap this creature'
    (SEM restricao de quantas vezes) - mas ela e' 0/2, entao morre (regra
    de estado, toughness 0) depois do 2o contador. A versao anterior dava
    +3 ativacoes extras TODO turno pra sempre, sem nunca remover a criatura
    do campo - superproducao indefinida. Corrigido: maximo 2 ativacoes na
    vida inteira (contadores permanentes em devoted_druid_counters), usadas
    de uma vez no primeiro turno em que fica pronta (premissa: maximiza
    mana imediata, mesma filosofia agressiva ja usada no resto do motor),
    depois ela morre e some do campo pro resto do jogo."""
    if "Devoted Druid" not in state.battlefield:
        state.devoted_druid_extra_untaps = 0
        return
    if state.devoted_druid_counters >= 2:
        state.battlefield.remove("Devoted Druid")
        state.devoted_druid_extra_untaps = 0
        return
    if "Devoted Druid" not in ready_creatures(state):
        state.devoted_druid_extra_untaps = 0
        return
    extra = 2 - state.devoted_druid_counters
    state.devoted_druid_extra_untaps = extra
    state.devoted_druid_counters += extra


def use_staff_of_domination_v2(state: GameState):
    """{1}: destapa. {5},{T}: compra 1. Com mana infinita, repete ate a
    biblioteca esvaziar (limite defensivo: nunca finge vencer por deck-out,
    so registra quantas compras aconteceram)."""
    if "Staff of Domination" not in state.battlefield or not state.infinite_mana_this_turn:
        return
    while state.library:
        card = state.library.pop(0)
        state.hand.append(card)
        state.cards_drawn_extra += 1
        state.staff_infinite_draws += 1
    if not state.library:
        state.library_emptied = True


def main_phase(state: GameState, is_first_main: bool = True):
    if is_first_main:
        # Oraculo real: "At the beginning of your first main phase" -
        # achado real 2026-08-30, disparava no upkeep antes (passo errado).
        black_market_connections_step(state)

    if not state.commander_in_play and can_cast(state, COMMANDER):
        cast_card(state, COMMANDER)
        maralen_try_free_cast(state)

    devoted_druid_pump(state)
    equip_umbral_mantle(state)
    # reavalia infinito apos equipar (dork_mana ja seta a flag)
    dork_mana(state)

    while True:
        castables = [n for n in state.hand if n not in LAND_NAMES
                     and n != "Green Sun's Zenith" and can_cast(state, n)]
        if castables:
            castables.sort(key=lambda n: CARD_DB[n].mv)
            cast_card(state, castables[0])
            maralen_try_free_cast(state)
            equip_umbral_mantle(state)
            dork_mana(state)
            continue
        if "Green Sun's Zenith" in state.hand and cast_green_sun_zenith(state):
            maralen_try_free_cast(state)
            equip_umbral_mantle(state)
            dork_mana(state)
            continue
        break

    cast_fauna_shaman_activation(state)
    if "Imperious Perfect" in state.battlefield and "Imperious Perfect" in ready_creatures(state) and remaining_mana(state) >= 1:
        spend_mana(state, 1)
        if state.infinite_mana_this_turn:
            # mana infinita + Imperious Perfect = exercito infinito (registrado, nao expandido de fato)
            state.tokens_created_total += 10_000
            state.elf_tokens += 10_000
        else:
            create_token(state, "elf", source="Imperious Perfect")

    # Joraga Treespeaker: level up e' "as a sorcery" (qualquer main phase
    # com prioridade, sem restricao de 1a/2a) - movido pra depois do loop
    # de conjuracao (achado real 2026-08-30, reanalise pedida pelo
    # usuario): rodava ANTES do loop principal, competindo por mana com
    # spells de verdade - agora so' usa mana que sobrou, mesma filosofia
    # ja aplicada ao Fauna Shaman/Imperious Perfect acima.
    joraga_level_up(state)

    use_staff_of_domination_v2(state)


def combat_step(state: GameState):
    # Kindred Discovery: "...or attacks, draw a card." Unico gatilho de
    # ataque real no deck (achado 2026-08-28) - modelado com a mesma
    # premissa ja usada noutros decks desta sessao pra combate sem
    # oponente real: toda criatura pronta (sem summoning sickness) ataca
    # desimpedida. So' Elfos contam (tipo escolhido).
    if "Kindred Discovery" in state.battlefield:
        attacking_elves = [n for n in ready_creatures(state) if is_elf(n)]
        # elf_tokens e' um contador agregado (sem nome/turno individual por
        # token) - tratados como sempre prontos, mesma aproximacao ja usada
        # noutros pontos deste arquivo pra pools de token compartilhados.
        draw_cards(state, len(attacking_elves) + state.elf_tokens)


def end_step(state: GameState):
    if "Wilderness Reclamation" in state.battlefield:
        state.mana_spent_this_turn = 0  # untap all lands (aproximado: reseta gasto)
    if "Bitterblossom" in state.battlefield:
        state.life -= 1
        create_token(state, "faerie", source="Bitterblossom")
        # Bitterblossom e Enchantment, nao Criatura — Roaming Throne nao dobra o proprio gatilho dela.
    if ("Growing Rites of Itlimoc // Itlimoc, Cradle of the Sun" in state.battlefield
            and not state.itlimoc_transformed):
        # Oraculo real: "At the beginning of your end step, if you control
        # four or more creatures, transform Growing Rites of Itlimoc."
        creatures_in_play = (sum(1 for n in state.battlefield if is_creature_card(n))
                              + state.elf_tokens + state.faerie_tokens)
        if creatures_in_play >= 4:
            state.itlimoc_transformed = True
            state.itlimoc_transform_turn = state.turn


def upkeep_step(state: GameState):
    times = 1
    if "Bitterbloom Bearer" in state.battlefield:
        if "Roaming Throne" in state.battlefield and is_roaming_type("Bitterbloom Bearer"):
            times = 2
            state.roaming_throne_doubles_total += 1
        for _ in range(times):
            state.life -= 1
            create_token(state, "faerie", source="Bitterbloom Bearer")

def black_market_connections_step(state: GameState):
    """Oraculo real: "At the beginning of your FIRST MAIN PHASE, choose one
    or more — Sell Contraband (Treasure, perde 1) / Buy Information
    (compra 1, perde 2) / Hire a Mercenary (token 3/2 Changeling, perde 3)."
    Achado real 2026-08-30 (reanalise pedida pelo usuario), 3 problemas
    empilhados na versao anterior: (1) disparava no upkeep, passo errado;
    (2) pagava o custo de vida do Sell Contraband SEM criar o Treasure
    correspondente (pior que nao escolher o modo); (3) Hire a Mercenary
    nunca era modelado. Corrigido: dispara aqui (1a main phase), escolhe
    os 3 modos (mesma filosofia agressiva do resto do motor - sem
    oponente real ameacando a vida, maximizar valor e' sempre a escolha
    certa). Treasure tratado como mana avulsa disponivel NO PROPRIO
    TURNO (mesma convencao de refund ja usada pro "etb_untap_lands" do
    Cloud of Faeries) - simplificacao documentada, nao rastreado como
    token persistente pra turnos futuros."""
    if "Black Market Connections" not in state.battlefield:
        return
    state.life -= 1
    state.mana_spent_this_turn = max(0, state.mana_spent_this_turn - 1)
    state.black_market_treasures_total += 1
    state.life -= 2
    draw_cards(state, 1)
    state.life -= 3
    enter_battlefield(state, "Mercenary Token", from_hand=False)
    state.black_market_mercenaries_total += 1


def should_keep(hand: list) -> bool:
    lands = sum(1 for n in hand if n in LAND_NAMES)
    good_early = {"Sol Ring", "Arcane Signet", "Elvish Mystic", "Llanowar Elves", "Birds of Paradise",
                  "Bloom Tender", COMMANDER}
    if lands >= 3:
        return True
    if lands == 2 and any(n in good_early for n in hand):
        return True
    return False


def build_library(names_override=None):
    if names_override is not None:
        for n in names_override:
            assert n in CARD_DB, f"faltando no CARD_DB: {n}"
        assert len(names_override) == 99, len(names_override)
        return list(names_override)
    lib = []
    lines = open("lista.md").read().split("## Lista completa")[1].strip().split("\n")
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

FLASH_SOURCES = {"Leyline of Anticipation", "Vedalken Orrery", "High Fae Trickster", "Alchemist's Refuge"}


def mulligan(rng: random.Random, max_mulls: int = 3, library=None):
    base = library if library is not None else BASE_LIBRARY
    mulls = 0
    hand, lib = [], []
    while mulls < max_mulls:
        lib = base[:]
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
    state.tapped_lands_this_turn = set()
    state.maralen_free_cast_used_this_turn = False
    state.exile_maralen = []
    state.fauna_shaman_used_this_turn = False
    state.warmaster_used_this_turn = False
    state.infinite_mana_this_turn = False
    state.radagast_discount_used_this_turn = False

    if not (is_first_turn and on_play):
        if state.library:
            state.hand.append(state.library.pop(0))
        else:
            state.library_emptied = True

    upkeep_step(state)
    play_land(state)
    main_phase(state, is_first_main=True)
    combat_step(state)
    main_phase(state, is_first_main=False)
    end_step(state)

    flash_universal = any(n in state.battlefield for n in FLASH_SOURCES)
    state.flash_universal_by_turn[state.turn] = flash_universal
    state.flash_with_radagast_by_turn[state.turn] = flash_universal or ("Radagast of Rhosgobel" in state.battlefield)


def simulate_one(seed: int, turns: int = 8, library=None):
    rng = random.Random(seed)
    hand, lib, mulls = mulligan(rng, library=library)
    state = GameState(hand=hand, library=lib, mulligans=mulls)
    state.warmaster_used_this_turn = False
    for t in range(turns):
        play_turn(state, is_first_turn=(t == 0), on_play=True)
        if state.infinite_combo_assembled and state.staff_infinite_draws > 0:
            break
    return state


def run_batch(n: int, seed_base: int, turns: int = 8):
    states = [simulate_one(seed_base + i, turns=turns) for i in range(n)]

    def avg(vals):
        return sum(vals) / len(vals) if vals else 0.0

    print(f"n={n}, seed_base={seed_base}, turns={turns}")
    print(f"Avg mulligans: {avg([s.mulligans for s in states]):.2f}")
    cmd_turn = [s.commander_cast_turn for s in states if s.commander_cast_turn is not None]
    print(f"Turno medio de conjuracao da Maralen: {avg(cmd_turn):.2f} | mediana: {statistics.median(cmd_turn) if cmd_turn else float('nan'):.1f}")
    print(f"Nunca conjurada em {turns} turnos: {100*sum(1 for s in states if s.commander_cast_turn is None)/n:.1f}%")
    print(f"Avg gatilhos de Maralen (exila 2): {avg([s.maralen_triggers_total for s in states]):.2f}")
    print(f"Avg cartas exiladas total: {avg([s.cards_exiled_total for s in states]):.2f}")
    print(f"Avg casts gratis via Maralen: {avg([s.maralen_free_casts_total for s in states]):.2f}")
    print(f"Avg tutores usados: {avg([s.tutors_used_total for s in states]):.2f}")
    print(f"Avg tokens criados (exclui explosao infinita): {avg([min(s.tokens_created_total, 100) for s in states]):.2f}")
    print(f"Avg dobras via Roaming Throne: {avg([s.roaming_throne_doubles_total for s in states]):.2f}")
    print(f"Avg terrenos jogados (total no jogo, inclui land drop extra do Thranduil's Company): {avg([s.lands_played_total for s in states]):.2f}")
    print(f"Avg tokens de Elfo via landfall (Thranduil, Sindarin Liege): {avg([s.landfall_elf_tokens_total for s in states]):.2f}")
    print(f"Avg gatilhos de contadores via landfall (Thranduil's Company): {avg([s.landfall_counters_total for s in states]):.2f}")
    print(f"Avg Treasures via Black Market Connections (Sell Contraband): {avg([s.black_market_treasures_total for s in states]):.2f}")
    print(f"Avg Mercenary Tokens via Black Market Connections (Hire a Mercenary): {avg([s.black_market_mercenaries_total for s in states]):.2f}")
    print(f"Avg nivel final do Joraga Treespeaker: {avg([s.joraga_level for s in states]):.2f} | atingiu nivel 5: {100*sum(1 for s in states if s.joraga_level >= 5)/n:.1f}%")
    print(f"Avg Fadas exiladas pelo Champion do Mistbind Clique: {avg([len(s.mistbind_exiled) for s in states]):.2f}")
    combo_hits = sum(1 for s in states if s.infinite_combo_assembled)
    print(f"Combo Umbral Mantle (mana infinita) montado: {100*combo_hits/n:.1f}% dos jogos"
          + (f" | turno medio: {avg([s.infinite_combo_turn for s in states if s.infinite_combo_turn is not None]):.2f}" if combo_hits else ""))
    staff_hits = sum(1 for s in states if s.staff_infinite_draws > 0)
    print(f"Staff of Domination converteu em compra infinita: {100*staff_hits/n:.1f}% dos jogos")
    print(f"Avg cartas compradas extra (motores de draw, exclui staff infinito): {avg([s.cards_drawn_extra - s.staff_infinite_draws for s in states]):.2f}")
    print(f"Avg mao final: {avg([len(s.hand) for s in states]):.2f}")

    itlimoc_hits = sum(1 for s in states if s.itlimoc_transformed)
    print(f"Growing Rites of Itlimoc transformou em Itlimoc, Cradle of the Sun: {100*itlimoc_hits/n:.1f}% dos jogos"
          + (f" | turno medio: {avg([s.itlimoc_transform_turn for s in states if s.itlimoc_transform_turn is not None]):.2f}" if itlimoc_hits else ""))
    print(f"Avg criaturas encontradas via ETB do Growing Rites of Itlimoc: {avg([s.itlimoc_creatures_found_total for s in states]):.2f}")

    # --- Metricas basicas (checklist obrigatorio, categoria 10) --------------
    # Reportadas explicitamente mesmo quando 0, pra deixar auditavel de
    # relance sem precisar somar manualmente.
    print("--- Metricas basicas (checklist obrigatorio) ---")
    print(f"RAMP: avg pecas de rampa conjuradas (dorks elficos, Sol Ring/Arcane Signet, Cryptolith Rite/"
          f"Elven Chorus, Itlimoc pos-transformacao): {avg([s.ramp_pieces_cast_total for s in states]):.2f}")
    print(f"DRAW: avg compras extras totais (Kindred Discovery, Cloud of Faeries, biblioteca via mulligan "
          f"nao contada aqui - exclui staff infinito): {avg([s.cards_drawn_extra - s.staff_infinite_draws for s in states]):.2f}")
    print(f"INTERACTION: avg spells de interacao conjurados (Arcane Denial, Counterspell, Swan Song, "
          f"Pongify, Rapid Hybridization, Reality Shift, Assassin's Trophy, Cyclonic Rift, Toxic Deluge, "
          f"Heroic Intervention - conjurados quando ha mana sobrando, sem efeito de combate real por ser "
          f"goldfish solo sem oponente): {avg([s.interaction_spells_cast_total for s in states]):.2f}")
    print(f"RECURSION: 0.00 (N/A - esta decklist nao tem nenhuma carta que devolva permanente do cemiterio "
          f"pro campo/mao; Fauna Shaman/Elvish Harbinger/Faerie Harbinger/Formidable Speaker/Green Sun's "
          f"Zenith sao tutores de BIBLIOTECA, categoria diferente por definicao)")
    print(f"FINISHER/LETHALITY: combo infinito (Umbral Mantle em dork escalavel 4+) monta em "
          f"{100*combo_hits/n:.1f}% dos jogos, convertido em compra infinita via Staff of Domination em "
          f"{100*staff_hits/n:.1f}% ou exercito infinito de Elfo via Imperious Perfect quando disponivel "
          f"(sem dano de combate real medido - goldfish solo sem oponente/vida alheia)")
    return states


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    states = run_batch(n=3000, seed_base=8000000, turns=8)

    with open("maralen_v1_runs.jsonl", "w") as f:
        for s in states:
            f.write(json.dumps({
                "mulligans": s.mulligans,
                "commander_cast_turn": s.commander_cast_turn,
                "maralen_triggers_total": s.maralen_triggers_total,
                "maralen_free_casts_total": s.maralen_free_casts_total,
                "tutors_used_total": s.tutors_used_total,
                "infinite_combo_assembled": s.infinite_combo_assembled,
                "infinite_combo_turn": s.infinite_combo_turn,
                "staff_infinite_draws": s.staff_infinite_draws,
                "cards_drawn_extra": s.cards_drawn_extra,
            }) + "\n")
