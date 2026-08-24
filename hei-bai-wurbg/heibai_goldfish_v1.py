"""
Goldfish simulator — Hei Bai, Forest Guardian (5 cores, WUBRG, Shrine tribal)

Construido do zero em 2026-08-24. Passo 0 (regra de
`references/goldfish-sim-card-rules.md`): a `auditoria.md` deste deck ja
tinha uma categorizacao boa das 17 Shrines, mas nao um catalogo
carta-a-carta de todo gatilho real — a varredura mecanica completa no
oraculo das 94 cartas unicas foi feita aqui (ver /tmp/heibai_full.txt).

======================================================================
MOTOR CENTRAL — Shrines escalando com contagem de Shrines
======================================================================
17 Shrines (12 `Legendary Enchantment — Shrine` + 5 `Legendary Enchantment
Creature — Shrine`, os Go-Shintai). A maioria tem DOIS gatilhos distintos:
um "when THIS Shrine enters" (X = Shrines que voce controla NAQUELE
momento, inclusive a que acabou de entrar) e um "whenever ANOTHER Shrine
you control enters" (efeito fixo, 1 unidade, disparado por toda outra
Shrine ja em campo). Implementado via `shrine_enters()`, um dispatch
central chamado toda vez que QUALQUER Shrine entra (nomeada, token, ou
reentrada via blink), que dispara os dois grupos corretamente.

Go-Shintai of Life's Origin e um caso a parte: seu gatilho e "Whenever
Go-Shintai of Life's Origin OR ANOTHER NONTOKEN Shrine you control enters,
create a token" — uma unica habilidade cobrindo os dois casos (ela mesma
OU outra Shrine nontoken), com o qualificador "nontoken" que impede o
proprio token criado de re-disparar a criacao de mais tokens (mesma
convencao de "nontoken" ja usada pra evitar loop infinito no Ur-Dragon
com Miirym/Lathliss — regra real da carta, nao um teto artificial).

======================================================================
Dois dobradores DISTINTOS de gatilho — nao confundir
======================================================================
- **Elesh Norn, Mother of Machines**: "If a permanent entering causes a
  triggered ability of a permanent you control to trigger, that ability
  triggers an additional time." Incondicional, amplo — dobra QUALQUER
  gatilho causado por ALGO entrando (nao so Shrine): o proprio ETB de uma
  Shrine, o gatilho reativo de outra Shrine, E o gatilho de Purphoros
  (dispara quando OUTRA criatura entra — tambem e "causado por permanente
  entrando"). NAO dobra gatilhos de conjuracao (cast triggers), so os de
  entrada.
- **Sanctum of All**: "If a triggered ability of another Shrine you
  control triggers while you control six or more Shrines, that ability
  triggers an additional time." Condicional (6+ Shrines) E escopado
  (só Shrine, não Purphoros) — mas cobre tanto gatilhos de ETB quanto os
  gatilhos pagos de end step dos Go-Shintai (que tambem sao "triggered
  ability of another Shrine").
- **Annie Joins Up**: "If a triggered ability of a legendary creature you
  control triggers, that ability triggers an additional time." Nao e
  sobre ETB nem sobre Shrine — e sobre a FONTE ser uma criatura lendaria.
  Cobre: o proprio ETB da Hei Bai, os 5 Go-Shintai (ETB de Life's Origin +
  as 5 habilidades pagas de end step), e o gatilho de conjuracao da
  Sythis (Legendary Enchantment CREATURE, ao contrario de Argothian
  Enchantress/Enchantress's Presence, que NAO sao lendarias e por isso
  NUNCA sao dobradas por nada neste deck).

As tres dobras empilham de forma independente quando aplicaveis
simultaneamente (times = 1 + cada dobra que se aplica), implementado via
`resolve_times()`.

======================================================================
Motor de blink — a segunda maior fonte de valor real
======================================================================
Re-piscar (exile + return) uma Shrine ja em campo dispara o gatilho
"when THIS enters" dela de novo (e' uma nova entrada real, nao e' o
"another Shrine enters" — ela mesma reentrando). Com Deadeye Navigator
pareado numa Shrine (soulbond), isso vira `{1}{U}: repisca a Shrine`,
repetivel enquanto houver mana — nao e' infinito (custa mana), mas e' um
motor real de escalada. Implementado: `blink_permanent()` remove e
re-adiciona a permanente, re-chamando `shrine_enters()` se for Shrine
(sempre como "self", nunca como token). Fontes de blink modeladas com
efeito real: Deadeye Navigator (soulbond, ativa quando ha mana sobrando),
Ephemerate (com rebound = 2 usos reais), Waterbender's Restoration,
Teleportation Circle, The Mind Stone (harnessed), Thassa Deep-Dwelling —
todas tentam escolher a Shrine com maior "self ETB" de valor disponivel em
campo (greedy).

======================================================================
Motor de conjuracao de encantamento (Enchantress package)
======================================================================
Argothian Enchantress, Enchantress's Presence (compra 1, NAO lendarias,
nunca dobradas), Sythis (compra 1 + ganha 1 vida, lendaria — dobrada pela
Annie), Herald of the Pantheon (ganha 1 vida + reduz custo de encantamento
em {1}), Hallowed Haunting (cria Spirit token X/X=Spirits controlados) —
disparam pra QUALQUER encantamento conjurado, Shrines inclusas (Shrines
sao encantamentos).

Skybind e DIFERENTE — seu gatilho e "Constellation: whenever this
enchantment or ANOTHER enchantment you control ENTERS" (nao "cast"),
entao dispara junto do dispatch de ETB, nao do dispatch de conjuracao.
Implementado com efeito modesto e documentado (ver Simplificacoes).

======================================================================
Purphoros — dano por criatura entrando
======================================================================
"Whenever another creature you control enters, Purphoros deals 2 damage
to each opponent." Sem condicao de devocao pra ativar (a clausula de
devocao so afeta se a PROPRIA Purphoros e uma criatura, irrelevante pro
gatilho de dano em si — por isso devocao NAO precisa ser rastreada aqui).
Com os varios geradores de token de Shrine (Honden of Life's Web, Southern
Air Temple, Go-Shintai of Shared Purpose, Crescent Island Temple, a
propria Hei Bai) isso pode disparar muitas vezes por turno. Dobrado por
Elesh Norn (e' causado por permanente entrando), NAO por Sanctum of All
(Purphoros nao e Shrine), conservadoramente NAO por Annie (nao rastreio
devocao pra saber se Purphoros e "criatura" no momento do gatilho —
simplificacao documentada, ver abaixo).

======================================================================
Simplificacoes documentadas (nao inventadas — omissoes explicitas)
======================================================================
- Modelo de mana GENERICO/TOTAL (mesma convencao dos outros simuladores
  desta biblioteca) — nao rastreia pip a pip. Devocao a vermelho/azul
  (Purphoros/Thassa) nao e rastreada porque nenhuma das duas depende de
  devocao pra sua habilidade DISPARADA/ATIVADA funcionar (so pra saber se
  a propria carta e uma criatura, irrelevante aqui sem combate real).
- Removal/contramagica proxy (Path to Exile, Swords to Plowshares, An
  Offer You Can't Refuse, Arcane Denial, Dovin's Veto, Swan Song, Touch
  the Spirit Realm, Farewell, Go-Shintai of Hidden Cruelty/Lost Wisdom's
  efeitos contra oponente) — sem alvo real, contadas como interacao usada,
  sem efeito colateral no nosso campo.
- Skybind: implementado de forma modesta — ao entrar um encantamento,
  se houver uma criatura NAO-token propria em campo sem Shrine (evita
  reentrar Shrine com Skybind competindo com o motor de blink dedicado),
  ela e re-piscada (sem efeito extra relevante, ja que nenhuma criatura
  nao-Shrine deste deck tem ETB proprio de peso) — documentado como valor
  quase nulo neste build especifico, nao inflado artificialmente.
- Weaver of Harmony: so o buff estatico (+1/+1 pra outras enchantment
  creatures) e considerado; a habilidade de copiar ativada/disparada de
  fonte de encantamento (`{G}, {T}: copy target...`) NAO e modelada —
  generica demais pra um efeito de valor claro e deterministico.
- Destiny Spinner: so o "can't be countered" (sem efeito, nao modelamos
  contra-magica contra nos); a ativada de virar terreno em criatura nao e
  modelada (baixo valor esperado, land destruction nao existe aqui).
- Devocao a preto pros Go-Shintai (nenhuma tem essa clausula, N/A).
- Dryad of the Ilysian Grove / Yavimaya Cradle of Growth: fixacao de mana
  tratada via modelo generico total (nao pip a pip), sem efeito numerico
  direto alem de permitir 1 terreno extra por turno (Dryad) — implementado.
- Farewell: modal, mas sem oponente real todos os 4 modos (exile
  artifacts/creatures/enchantments/graveyards) sao proxy — mesmo que
  "exile enchantments" tecnicamente afetaria nossas proprias Shrines, a
  convencao desta biblioteca e nunca simular decisao simetrica/assimetrica
  sem oponente real, entao e tratada como interacao pura.
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


COMMANDER = "Hei Bai, Forest Guardian"
add(COMMANDER, 4, "creature", {"commander", "legendary_creature"})

LEGENDARY_CREATURES = {
    COMMANDER, "Elesh Norn, Mother of Machines", "Sythis, Harvest's Hand",
    "Go-Shintai of Ancient Wars", "Go-Shintai of Hidden Cruelty",
    "Go-Shintai of Life's Origin", "Go-Shintai of Lost Wisdom",
    "Go-Shintai of Shared Purpose",
}

# --- Terrenos (35) ----------------------------------------------------------
FETCH_NAMES = {"Arid Mesa", "Bloodstained Mire", "Flooded Strand", "Marsh Flats",
               "Misty Rainforest", "Scalding Tarn", "Verdant Catacombs", "Windswept Heath"}
for n in FETCH_NAMES:
    add(n, 0, "land", {"fetch"})
for n in ["Abandoned Air Temple", "Badlands", "Bayou", "City of Brass", "Command Tower",
          "Hall of Heliod's Generosity", "Indatha Triome", "Ketria Triome", "Plateau",
          "Savannah", "Scrubland", "Taiga", "Tropical Island", "Tundra", "Underground Sea",
          "Yavimaya, Cradle of Growth", "Forest", "Island", "Mountain", "Plains", "Swamp"]:
    add(n, 0, "land", set())

# --- As 17 Shrines -----------------------------------------------------------
SHRINE_NAMES = {
    "Crescent Island Temple", "Honden of Life's Web", "Honden of Seeing Winds",
    "Kyoshi Island Plaza", "Northern Air Temple", "Sanctum of All",
    "Sanctum of Calm Waters", "Sanctum of Fruitful Harvest", "Sanctum of Shattered Heights",
    "Sanctum of Stone Fangs", "Southern Air Temple", "The Spirit Oasis",
    "Go-Shintai of Ancient Wars", "Go-Shintai of Hidden Cruelty", "Go-Shintai of Life's Origin",
    "Go-Shintai of Lost Wisdom", "Go-Shintai of Shared Purpose",
}
add("Crescent Island Temple", 4, "enchantment", {"shrine"})
add("Honden of Life's Web", 5, "enchantment", {"shrine"})
add("Honden of Seeing Winds", 5, "enchantment", {"shrine"})
add("Kyoshi Island Plaza", 4, "enchantment", {"shrine"})
add("Northern Air Temple", 1, "enchantment", {"shrine"})
add("Sanctum of All", 5, "enchantment", {"shrine"})
add("Sanctum of Calm Waters", 4, "enchantment", {"shrine"})
add("Sanctum of Fruitful Harvest", 3, "enchantment", {"shrine"})
add("Sanctum of Shattered Heights", 3, "enchantment", {"shrine"})
add("Sanctum of Stone Fangs", 2, "enchantment", {"shrine"})
add("Southern Air Temple", 4, "enchantment", {"shrine"})
add("The Spirit Oasis", 3, "enchantment", {"shrine"})
add("Go-Shintai of Ancient Wars", 3, "enchantment_creature", {"shrine", "legendary_creature"})
add("Go-Shintai of Hidden Cruelty", 4, "enchantment_creature", {"shrine", "legendary_creature"})
add("Go-Shintai of Life's Origin", 4, "enchantment_creature", {"shrine", "legendary_creature"})
add("Go-Shintai of Lost Wisdom", 2, "enchantment_creature", {"shrine", "legendary_creature"})
add("Go-Shintai of Shared Purpose", 4, "enchantment_creature", {"shrine", "legendary_creature"})

# --- Criaturas / payoffs ------------------------------------------------------
add("Argothian Enchantress", 2, "creature", {"enchant_cast_draw1"})
add("Birds of Paradise", 1, "creature", {"dork_flat1"})
add("Bloom Tender", 2, "creature", {"dork_vivid"})
add("Deadeye Navigator", 6, "creature", {"blink_soulbond"})
add("Displacer Kitten", 4, "creature", {"blink_on_noncreature_cast"})
add("Dryad of the Ilysian Grove", 3, "enchantment_creature", {"extra_land"})
add("Elesh Norn, Mother of Machines", 5, "creature", {"legendary_creature", "etb_doubler"})
add("Enduring Vitality", 3, "enchantment_creature", {"creatures_tap_any_color"})
add("Herald of the Pantheon", 2, "creature", {"enchant_cast_life1", "enchant_cost_reduce1"})
add("Purphoros, God of the Forge", 4, "enchantment_creature", {"creature_etb_damage"})
add("Sanctum Weaver", 2, "enchantment_creature", {"dork_scale_enchantments"})
add("Seedborn Muse", 5, "creature", {"untap_all"})
add("Sythis, Harvest's Hand", 2, "enchantment_creature", {"enchant_cast_draw1", "enchant_cast_life1", "legendary_creature"})
add("Thassa, Deep-Dwelling", 4, "enchantment_creature", {"blink_endstep"})
add("Weaver of Harmony", 2, "enchantment_creature", set())

# --- Encantamentos -------------------------------------------------------------
add("Annie Joins Up", 4, "enchantment", {"legendary_creature_doubler", "interaction"})
add("Destiny Spinner", 2, "enchantment_creature", set())
add("Enchantress's Presence", 3, "enchantment", {"enchant_cast_draw1"})
add("Greater Auramancy", 2, "enchantment", {"shroud_enchantments"})
add("Hallowed Haunting", 4, "enchantment", {"enchant_cast_spirit_token"})
add("In Search of Greatness", 2, "enchantment", {"upkeep_free_cast"})
add("Skybind", 5, "enchantment", {"skybind"})
add("Sphere of Safety", 5, "enchantment", {"defense"})
add("Sterling Grove", 2, "enchantment", {"shroud_enchantments", "enchant_tutor_sac"})
add("Teleportation Circle", 4, "enchantment", {"blink_endstep"})

# --- Interacao / protecao (proxy) ----------------------------------------------
add("An Offer You Can't Refuse", 1, "instant", {"interaction"})
add("Arcane Denial", 2, "instant", {"interaction"})
add("Dovin's Veto", 2, "instant", {"interaction"})
add("Ephemerate", 1, "instant", {"blink_rebound"})
add("Heroic Intervention", 2, "instant", {"interaction"})
add("Path to Exile", 1, "instant", {"interaction"})
add("Swan Song", 1, "instant", {"interaction"})
add("Swords to Plowshares", 1, "instant", {"interaction"})
add("Teferi's Protection", 3, "instant", {"interaction"})
add("Touch the Spirit Realm", 3, "enchantment", {"interaction"})
add("Waterbender's Restoration", 2, "instant", {"blink_x"})

# --- Ramp / tutores --------------------------------------------------------------
add("Aang's Journey", 2, "sorcery", {"land_tutor_kicker_shrine"})
add("Cultivate", 3, "sorcery", {"land_tutor2"})
add("Farewell", 6, "sorcery", {"interaction"})
add("Farseek", 2, "sorcery", {"land_tutor1"})
add("Idyllic Tutor", 3, "sorcery", {"enchant_tutor_hand"})
add("Nature's Lore", 2, "sorcery", {"land_tutor1"})
add("Replenish", 4, "sorcery", {"replenish"})
add("Three Visits", 2, "sorcery", {"land_tutor1"})

# --- Rocks -----------------------------------------------------------------------
add("Arcane Signet", 2, "artifact", {"rock1"})
add("Sol Ring", 1, "artifact", {"rock2"})
add("The Mind Stone", 2, "artifact", {"rock1", "blink_endstep_harnessed"})

# --- Token sintetico -------------------------------------------------------------
add("Shrine Token", 0, "creature", {"shrine", "token"})
add("Monk Token", 0, "creature", {"token"})
add("Spirit Token", 0, "creature", {"token"})


LAND_NAMES = {n for n, c in CARD_DB.items() if c.ctype == "land"}
CREATURE_ISH = {"creature", "enchantment_creature"}


def is_creature_card(name: str) -> bool:
    return CARD_DB[name].ctype in CREATURE_ISH


def is_enchantment_card(name: str) -> bool:
    return CARD_DB[name].ctype in ("enchantment", "enchantment_creature")


def is_shrine(name: str) -> bool:
    return "shrine" in CARD_DB[name].tags


def is_legendary_creature(name: str) -> bool:
    return name in LEGENDARY_CREATURES


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
    lands_played_cap: int = 1
    mana_spent_this_turn: int = 0
    bonus_mana_pool: int = 0

    commander_in_play: bool = False
    commander_cast_turn: Optional[int] = None

    ephemerate_rebound_pending: bool = False
    mind_stone_harnessed: bool = False

    # metrics -------------------------------------------------------------
    cards_drawn_extra: int = 0
    proxy_drain_total: int = 0
    proxy_damage_total: int = 0
    tokens_created_total: int = 0
    doubles_elesh_norn_total: int = 0
    doubles_sanctum_of_all_total: int = 0
    doubles_annie_total: int = 0
    blinks_total: int = 0
    shrine_reblinks_total: int = 0
    tutors_used_total: int = 0
    interaction_spells_cast_total: int = 0
    proxy_life_gained_total: int = 0
    library_emptied: bool = False


def draw_cards(state: GameState, n: int):
    for _ in range(n):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1
        else:
            state.library_emptied = True


def shrine_count(state: GameState) -> int:
    return sum(1 for n in state.battlefield if is_shrine(n))


def gain_life(state: GameState, n: int):
    state.proxy_life_gained_total += n


def proxy_drain(state: GameState, n: int):
    state.proxy_drain_total += n


def proxy_damage(state: GameState, n: int):
    state.proxy_damage_total += n


def create_tokens(state: GameState, token_name: str, n: int):
    for _ in range(n):
        state.battlefield.append(token_name)
        state.tokens_created_total += 1
        if is_shrine(token_name):
            shrine_enters(state, token_name, is_token=True)
        if is_creature_card(token_name):
            creature_enters_hook(state, token_name, is_token=True)


# ---------------------------------------------------------------------------
# Dobras de gatilho — tres fontes distintas, nao confundir
# ---------------------------------------------------------------------------

def resolve_times(state: GameState, source_name: str, is_etb_caused: bool,
                   is_shrine_triggered: bool, is_legendary_creature_triggered: bool) -> int:
    times = 1
    if is_etb_caused and "Elesh Norn, Mother of Machines" in state.battlefield:
        times += 1
        state.doubles_elesh_norn_total += 1
    if (is_shrine_triggered and source_name != "Sanctum of All"
            and "Sanctum of All" in state.battlefield and shrine_count(state) >= 6):
        times += 1
        state.doubles_sanctum_of_all_total += 1
    if is_legendary_creature_triggered and "Annie Joins Up" in state.battlefield:
        times += 1
        state.doubles_annie_total += 1
    return times


# ---------------------------------------------------------------------------
# Motor central de Shrine — dispatch de ETB
# ---------------------------------------------------------------------------

def _monk_tokens(state, n):
    create_tokens(state, "Monk Token", n)


def _spirit_tokens(state, n):
    create_tokens(state, "Spirit Token", n)


def _tutor_basics_tapped(state, n):
    for _ in range(n):
        candidates = [c for c in state.library if c in {"Forest", "Island", "Mountain", "Plains", "Swamp"}]
        if candidates:
            pick = candidates[0]
            state.library.remove(pick)
            state.battlefield.append(pick)


SHRINE_SELF_ETB = {
    "Crescent Island Temple": lambda state, sc: _monk_tokens(state, sc),
    "Honden of Life's Web": None,  # gatilho de upkeep, nao de ETB (ver upkeep_step)
    "Honden of Seeing Winds": None,  # idem
    "Kyoshi Island Plaza": lambda state, sc: _tutor_basics_tapped(state, sc),
    "Northern Air Temple": lambda state, sc: proxy_drain(state, sc),
    "Sanctum of All": None,  # so tem gatilho de upkeep (tutor) + o dobrador estatico
    "Sanctum of Calm Waters": None,  # gatilho de main phase
    "Sanctum of Fruitful Harvest": None,  # gatilho de main phase
    "Sanctum of Shattered Heights": None,  # habilidade ativada, nao ETB
    "Sanctum of Stone Fangs": None,  # gatilho de main phase
    "Southern Air Temple": lambda state, sc: None,  # +1/+1 counters, sem efeito numerico relevante pro goldfish (sem combate real)
    "The Spirit Oasis": lambda state, sc: draw_cards(state, sc),
    "Go-Shintai of Ancient Wars": None,  # habilidade paga de end step
    "Go-Shintai of Hidden Cruelty": None,  # idem
    "Go-Shintai of Lost Wisdom": None,  # idem
    "Go-Shintai of Shared Purpose": None,  # idem
}

SHRINE_OTHER_REACT = {
    "Crescent Island Temple": lambda state: _monk_tokens(state, 1),
    "Kyoshi Island Plaza": lambda state: _tutor_basics_tapped(state, 1),
    "Northern Air Temple": lambda state: proxy_drain(state, 1),
    "Southern Air Temple": lambda state: None,
    "The Spirit Oasis": lambda state: draw_cards(state, 1),
}


def shrine_enters(state: GameState, name: str, is_token: bool = False):
    """Chamado toda vez que UMA Shrine entra em campo (nomeada, token, ou
    reentrada via blink). `name` ja foi adicionado a state.battlefield
    antes desta chamada. sc (shrine_count) ja inclui a que entrou agora."""
    sc = shrine_count(state)

    fn = SHRINE_SELF_ETB.get(name)
    if fn is not None:
        times = resolve_times(state, name, True, True, is_legendary_creature(name))
        for _ in range(times):
            fn(state, sc)

    for reactor in set(state.battlefield):
        if reactor == name:
            continue
        fn2 = SHRINE_OTHER_REACT.get(reactor)
        if fn2 is not None:
            times = resolve_times(state, reactor, True, True, is_legendary_creature(reactor))
            for _ in range(times):
                fn2(state)

    # Go-Shintai of Life's Origin: "Whenever ~ or another NONTOKEN Shrine
    # you control enters, create a token" — condicao propria (self OU
    # outra shrine nontoken), diferente do padrao generico acima.
    if "Go-Shintai of Life's Origin" in state.battlefield:
        self_trigger = (name == "Go-Shintai of Life's Origin")
        other_nontoken_trigger = (name != "Go-Shintai of Life's Origin" and not is_token and is_shrine(name))
        if self_trigger or other_nontoken_trigger:
            times = resolve_times(state, "Go-Shintai of Life's Origin", True, True, True)
            for _ in range(times):
                create_tokens(state, "Shrine Token", 1)

    if is_creature_card(name):
        creature_enters_hook(state, name, is_token)


def creature_enters_hook(state: GameState, name: str, is_token: bool):
    """Purphoros: 'Whenever another creature you control enters, deals 2
    damage to each opponent.' Sem condicao de devocao pro gatilho em si
    (so afeta se a propria Purphoros e criatura, irrelevante aqui)."""
    if "Purphoros, God of the Forge" in state.battlefield and name != "Purphoros, God of the Forge":
        times = resolve_times(state, "Purphoros, God of the Forge", True, False, False)
        for _ in range(times):
            proxy_damage(state, 2)


# ---------------------------------------------------------------------------
# Motor de conjuracao de encantamento
# ---------------------------------------------------------------------------

def on_cast_enchantment(state: GameState, name: str):
    for source in ("Argothian Enchantress", "Enchantress's Presence"):
        if source in state.battlefield:
            draw_cards(state, 1)  # nunca lendaria, nunca dobrada neste deck
    if "Sythis, Harvest's Hand" in state.battlefield:
        times = resolve_times(state, "Sythis, Harvest's Hand", False, False, True)
        for _ in range(times):
            gain_life(state, 1)
            draw_cards(state, 1)
    if "Herald of the Pantheon" in state.battlefield:
        gain_life(state, 1)
    if "Hallowed Haunting" in state.battlefield:
        spirits = sum(1 for n in state.battlefield if n == "Spirit Token")
        create_tokens(state, "Spirit Token", 1)
        # o token criado ja conta a si mesmo (X/X = spirits controlados no
        # momento em que RESOLVE, simplificado como "quantos ja tinha + 1")


def on_any_enchantment_enters(state: GameState, name: str):
    """Skybind — 'Constellation: whenever this or another enchantment you
    control ENTERS' (nao 'cast'). Implementado com valor modesto e
    documentado (ver Simplificacoes no topo do arquivo)."""
    if "Skybind" not in state.battlefield:
        return
    targets = [n for n in state.battlefield if is_creature_card(n) and not is_shrine(n) and n not in ("token",)]
    if targets:
        blink_permanent(state, targets[0], source="Skybind")


# ---------------------------------------------------------------------------
# Motor de blink
# ---------------------------------------------------------------------------

def best_shrine_to_reblink(state: GameState) -> Optional[str]:
    """Escolhe greedy a Shrine em campo com maior valor esperado de
    'self ETB' pra repiscar (prioriza as que escalam com shrine_count)."""
    candidates = [n for n in state.battlefield if is_shrine(n) and SHRINE_SELF_ETB.get(n) is not None]
    if not candidates:
        return None
    priority = ["The Spirit Oasis", "Kyoshi Island Plaza", "Northern Air Temple", "Crescent Island Temple"]
    for p in priority:
        if p in candidates:
            return p
    return candidates[0]


def blink_permanent(state: GameState, name: str, source: str = ""):
    if name not in state.battlefield:
        return
    state.battlefield.remove(name)
    state.blinks_total += 1
    state.battlefield.append(name)
    if is_shrine(name):
        state.shrine_reblinks_total += 1
        shrine_enters(state, name, is_token=False)
    elif is_creature_card(name):
        creature_enters_hook(state, name, is_token=False)


# ---------------------------------------------------------------------------
# Mana
# ---------------------------------------------------------------------------

def enchantment_count(state: GameState) -> int:
    return sum(1 for n in state.battlefield if is_enchantment_card(n))


def rocks_mana(state: GameState) -> int:
    total = 0
    if "Sol Ring" in state.battlefield:
        total += 2
    if "Arcane Signet" in state.battlefield:
        total += 1
    if "The Mind Stone" in state.battlefield:
        total += 1
    return total


def dork_mana(state: GameState) -> int:
    total = 0
    if "Birds of Paradise" in state.battlefield:
        total += 1
    if "Bloom Tender" in state.battlefield:
        total += 1  # aproximado: 1 mana (real escala com cores em campo, simplificado)
    if "Sanctum Weaver" in state.battlefield:
        total += max(1, enchantment_count(state) // 2)  # aproximacao conservadora (real = enchantment_count exato)
    return total


def total_mana(state: GameState) -> int:
    lands = sum(1 for n in state.battlefield if n in LAND_NAMES)
    return lands + rocks_mana(state) + dork_mana(state) + state.bonus_mana_pool


def remaining_mana(state: GameState) -> int:
    return max(0, total_mana(state) - state.mana_spent_this_turn)


def effective_cost(state: GameState, name: str) -> int:
    mv = CARD_DB[name].mv
    if is_enchantment_card(name) and "Herald of the Pantheon" in state.battlefield:
        mv = max(0, mv - 1)
    return mv


def can_cast(state: GameState, name: str) -> bool:
    return remaining_mana(state) >= effective_cost(state, name)


def spend_mana(state: GameState, n: int):
    state.mana_spent_this_turn += n


# ---------------------------------------------------------------------------
# Resolucao de ETB / cast
# ---------------------------------------------------------------------------

def resolve_instant_sorcery(state: GameState, name: str):
    tags = CARD_DB[name].tags
    if "land_tutor1" in tags:
        candidates = [n for n in state.library if n in LAND_NAMES]
        if candidates:
            pick = candidates[0]
            state.library.remove(pick)
            state.battlefield.append(pick)
    elif "land_tutor2" in tags:
        candidates = [n for n in state.library if n in LAND_NAMES]
        got = 0
        while candidates and got < 2:
            pick = candidates.pop(0)
            state.library.remove(pick)
            if got == 0:
                state.battlefield.append(pick)
            else:
                state.hand.append(pick)
            got += 1
    elif "land_tutor_kicker_shrine" in tags:
        candidates = [n for n in state.library if n in LAND_NAMES]
        if candidates:
            pick = candidates[0]
            state.library.remove(pick)
            state.hand.append(pick)
        if remaining_mana(state) >= 2:  # kicker
            shrines_in_lib = [n for n in state.library if is_shrine(n)]
            if shrines_in_lib:
                pick = shrines_in_lib[0]
                state.library.remove(pick)
                state.hand.append(pick)
                state.tutors_used_total += 1
        gain_life(state, 2)
    elif "enchant_tutor_hand" in tags:
        pool = [n for n in state.library if is_enchantment_card(n)]
        if pool:
            best = max(pool, key=lambda n: CARD_DB[n].mv)
            state.library.remove(best)
            state.hand.append(best)
            state.tutors_used_total += 1
    elif "replenish" in tags:
        ench_in_gy = [n for n in state.graveyard if is_enchantment_card(n)]
        for n in ench_in_gy:
            state.graveyard.remove(n)
            enter_battlefield(state, n, from_hand=False)
    elif "interaction" in tags:
        state.interaction_spells_cast_total += 1
    elif "blink_x" in tags:
        target = best_shrine_to_reblink(state)
        if target:
            blink_permanent(state, target, source=name)


def enter_battlefield(state: GameState, name: str, from_hand: bool = True):
    if from_hand and name in state.hand:
        state.hand.remove(name)
    state.battlefield.append(name)
    if name == COMMANDER:
        state.commander_in_play = True
        if state.commander_cast_turn is None:
            state.commander_cast_turn = state.turn
        # ETB: revela ate achar Shrine, pode colocar em campo, "then
        # shuffle" — as cartas reveladas que NAO eram Shrine voltam pra
        # biblioteca (nao vao pro cemiterio; mesma convencao ja usada
        # nesta biblioteca pra "search... then shuffle": sem RNG real, so
        # devolvidas deterministicamente).
        revealed = []
        found_shrine = None
        while state.library:
            top = state.library.pop(0)
            if is_shrine(top):
                found_shrine = top
                break
            revealed.append(top)
        state.library.extend(revealed)
        if found_shrine:
            enter_battlefield(state, found_shrine, from_hand=False)
    if is_enchantment_card(name):
        on_any_enchantment_enters(state, name)
    if is_shrine(name):
        shrine_enters(state, name, is_token=False)
    elif is_creature_card(name):
        creature_enters_hook(state, name, is_token=False)


def cast_card(state: GameState, name: str):
    card = CARD_DB[name]
    cost = effective_cost(state, name)
    spend_mana(state, cost)
    if name != COMMANDER and name in state.hand:
        state.hand.remove(name)

    if is_enchantment_card(name):
        on_cast_enchantment(state, name)

    if "enchant_tutor_sac" in card.tags:
        pass  # Sterling Grove: sacrificio e a ativada, nao o cast — tratado a parte

    if name in LAND_NAMES:
        state.battlefield.append(name)
        return

    if card.ctype in ("instant", "sorcery"):
        resolve_instant_sorcery(state, name)
        state.graveyard.append(name)
        return

    enter_battlefield(state, name, from_hand=False)


def play_land(state: GameState):
    cap = 2 if "Dryad of the Ilysian Grove" in state.battlefield else 1
    if state.lands_played_this_turn >= cap:
        return
    lands_in_hand = [n for n in state.hand if n in LAND_NAMES]
    while lands_in_hand and state.lands_played_this_turn < cap:
        choice = lands_in_hand.pop(0)
        state.hand.remove(choice)
        state.battlefield.append(choice)
        state.lands_played_this_turn += 1


def do_sterling_grove_tutor(state: GameState):
    if "Sterling Grove" not in state.battlefield or remaining_mana(state) < 1:
        return
    pool = [n for n in state.library if is_enchantment_card(n)]
    if not pool:
        return
    best = max(pool, key=lambda n: CARD_DB[n].mv)
    state.library.remove(best)
    state.library.insert(0, best)
    spend_mana(state, 1)
    state.battlefield.remove("Sterling Grove")
    state.tutors_used_total += 1


def do_deadeye_navigator(state: GameState):
    if "Deadeye Navigator" not in state.battlefield or remaining_mana(state) < 2:
        return
    target = best_shrine_to_reblink(state)
    if target:
        spend_mana(state, 2)
        blink_permanent(state, target, source="Deadeye Navigator")


def do_endstep_blinks(state: GameState):
    for source, cost in (("Thassa, Deep-Dwelling", 0), ("Teleportation Circle", 0),
                          ("The Mind Stone", 0)):
        if source == "The Mind Stone" and not state.mind_stone_harnessed:
            continue
        if source in state.battlefield:
            target = best_shrine_to_reblink(state)
            if target:
                blink_permanent(state, target, source=source)


def do_ephemerate(state: GameState):
    if state.ephemerate_rebound_pending:
        target = best_shrine_to_reblink(state)
        if target:
            blink_permanent(state, target, source="Ephemerate (rebound)")
        state.ephemerate_rebound_pending = False


def do_shrine_upkeep_triggers(state: GameState):
    sc = shrine_count(state)
    if "Honden of Life's Web" in state.battlefield:
        times = resolve_times(state, "Honden of Life's Web", False, True, False)
        for _ in range(times):
            create_tokens(state, "Spirit Token", sc)
    if "Honden of Seeing Winds" in state.battlefield:
        times = resolve_times(state, "Honden of Seeing Winds", False, True, False)
        for _ in range(times):
            draw_cards(state, sc)
    if "Sanctum of All" in state.battlefield:
        pool = [n for n in state.library if is_shrine(n)]
        pool_gy = [n for n in state.graveyard if is_shrine(n)]
        times = resolve_times(state, "Sanctum of All", False, True, False)
        for _ in range(times):
            if pool:
                pick = pool[0]
                state.library.remove(pick)
                enter_battlefield(state, pick, from_hand=False)
                state.tutors_used_total += 1
            elif pool_gy:
                pick = pool_gy[0]
                state.graveyard.remove(pick)
                enter_battlefield(state, pick, from_hand=False)
                state.tutors_used_total += 1


def do_shrine_mainphase_triggers(state: GameState):
    sc = shrine_count(state)
    if "Sanctum of Calm Waters" in state.battlefield:
        times = resolve_times(state, "Sanctum of Calm Waters", False, True, False)
        for _ in range(times):
            draw_cards(state, sc)
            if state.hand:
                worst = min(state.hand, key=lambda n: effective_cost(state, n) if n not in LAND_NAMES else 0)
                state.hand.remove(worst)
                state.graveyard.append(worst)
    if "Sanctum of Fruitful Harvest" in state.battlefield:
        times = resolve_times(state, "Sanctum of Fruitful Harvest", False, True, False)
        for _ in range(times):
            state.bonus_mana_pool += sc
    if "Sanctum of Stone Fangs" in state.battlefield:
        times = resolve_times(state, "Sanctum of Stone Fangs", False, True, False)
        for _ in range(times):
            proxy_drain(state, sc)


def do_go_shintai_endstep(state: GameState):
    sc = shrine_count(state)
    for name in ("Go-Shintai of Ancient Wars", "Go-Shintai of Hidden Cruelty",
                 "Go-Shintai of Lost Wisdom", "Go-Shintai of Shared Purpose"):
        if name not in state.battlefield or remaining_mana(state) < 1:
            continue
        spend_mana(state, 1)
        times = resolve_times(state, name, False, True, True)
        for _ in range(times):
            if name == "Go-Shintai of Ancient Wars":
                proxy_damage(state, sc)
            elif name == "Go-Shintai of Hidden Cruelty":
                state.interaction_spells_cast_total += 1
            elif name == "Go-Shintai of Lost Wisdom":
                pass  # mill de oponente, proxy sem efeito no nosso lado
            elif name == "Go-Shintai of Shared Purpose":
                create_tokens(state, "Spirit Token", sc)


def do_sanctum_shattered_heights(state: GameState):
    if "Sanctum of Shattered Heights" not in state.battlefield or remaining_mana(state) < 1:
        return
    discardable = [n for n in state.hand if n in LAND_NAMES or is_shrine(n)]
    if not discardable:
        return
    spend_mana(state, 1)
    state.hand.remove(discardable[0])
    state.graveyard.append(discardable[0])
    times = resolve_times(state, "Sanctum of Shattered Heights", False, True, False)
    for _ in range(times):
        state.interaction_spells_cast_total += 1


def do_in_search_of_greatness(state: GameState):
    if "In Search of Greatness" not in state.battlefield:
        return
    permanents_on_bf = [n for n in state.battlefield if n not in LAND_NAMES]
    highest_mv = max((CARD_DB[n].mv for n in permanents_on_bf), default=0)
    target_mv = highest_mv + 1
    pool = [n for n in state.hand if n not in LAND_NAMES and CARD_DB[n].mv == target_mv]
    if pool:
        pick = pool[0]
        state.hand.remove(pick)
        enter_battlefield(state, pick, from_hand=False)


def main_phase(state: GameState):
    if not state.commander_in_play and can_cast(state, COMMANDER):
        cast_card(state, COMMANDER)

    do_sanctum_shattered_heights(state)
    do_deadeye_navigator(state)

    while True:
        castables = [n for n in state.hand if n not in LAND_NAMES and can_cast(state, n)]
        if not castables:
            break
        def prio(n):
            tags = CARD_DB[n].tags
            group = 0 if (tags & {"rock1", "rock2", "land_tutor1", "land_tutor2", "dork_flat1"}) else 1
            return (group, effective_cost(state, n))
        castables.sort(key=prio)
        cast_card(state, castables[0])

    do_sterling_grove_tutor(state)
    do_shrine_mainphase_triggers(state)


def end_step(state: GameState):
    do_go_shintai_endstep(state)
    do_endstep_blinks(state)
    do_ephemerate(state)
    while len(state.hand) > 7:
        worst = min(state.hand, key=lambda n: effective_cost(state, n) if n not in LAND_NAMES else 0)
        state.hand.remove(worst)
        state.graveyard.append(worst)


def upkeep_step(state: GameState):
    do_shrine_upkeep_triggers(state)
    do_in_search_of_greatness(state)
    if "The Mind Stone" in state.battlefield and not state.mind_stone_harnessed and remaining_mana(state) >= 6:
        spend_mana(state, 6)
        state.mind_stone_harnessed = True


def should_keep(hand: list) -> bool:
    lands = sum(1 for n in hand if n in LAND_NAMES)
    good_early = {"Sol Ring", "Arcane Signet", "Birds of Paradise", "Farseek",
                  "Nature's Lore", "Three Visits", COMMANDER}
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
    print(f"Turno medio de conjuracao da Hei Bai: {avg(cmd_turn):.2f} | mediana: {statistics.median(cmd_turn) if cmd_turn else float('nan'):.1f}")
    print(f"Nunca conjurada em {turns} turnos: {100*sum(1 for s in states if s.commander_cast_turn is None)/n:.1f}%")
    print(f"Avg contagem de Shrines em campo (fim de jogo): {avg([shrine_count(s) for s in states]):.2f}")
    print(f"Avg cartas compradas extra: {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"Avg drain proxy total: {avg([s.proxy_drain_total for s in states]):.2f}")
    print(f"Avg dano proxy total (Purphoros/Go-Shintai Ancient Wars): {avg([s.proxy_damage_total for s in states]):.2f}")
    print(f"Avg tokens criados: {avg([s.tokens_created_total for s in states]):.2f}")
    print(f"Avg dobras via Elesh Norn: {avg([s.doubles_elesh_norn_total for s in states]):.2f}")
    print(f"Avg dobras via Sanctum of All (6+ Shrines): {avg([s.doubles_sanctum_of_all_total for s in states]):.2f}")
    print(f"Avg dobras via Annie Joins Up: {avg([s.doubles_annie_total for s in states]):.2f}")
    print(f"Avg blinks totais: {avg([s.blinks_total for s in states]):.2f} | dos quais em Shrine: {avg([s.shrine_reblinks_total for s in states]):.2f}")
    print(f"Avg tutores usados: {avg([s.tutors_used_total for s in states]):.2f}")
    print(f"Avg vida ganha proxy: {avg([s.proxy_life_gained_total for s in states]):.2f}")
    print(f"Avg spells de interacao conjurados (proxy): {avg([s.interaction_spells_cast_total for s in states]):.2f}")
    print(f"Avg mao final: {avg([len(s.hand) for s in states]):.2f}")
    return states


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    states = run_batch(n=3000, seed_base=9100000, turns=8)

    with open("heibai_v1_runs.jsonl", "w") as f:
        for s in states:
            f.write(json.dumps({
                "mulligans": s.mulligans,
                "commander_cast_turn": s.commander_cast_turn,
                "shrine_count_final": shrine_count(s),
                "cards_drawn_extra": s.cards_drawn_extra,
                "proxy_drain_total": s.proxy_drain_total,
                "proxy_damage_total": s.proxy_damage_total,
                "tokens_created_total": s.tokens_created_total,
                "doubles_elesh_norn_total": s.doubles_elesh_norn_total,
                "doubles_sanctum_of_all_total": s.doubles_sanctum_of_all_total,
                "doubles_annie_total": s.doubles_annie_total,
                "blinks_total": s.blinks_total,
                "shrine_reblinks_total": s.shrine_reblinks_total,
            }) + "\n")
