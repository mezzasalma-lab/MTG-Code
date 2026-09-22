"""
Goldfish simulator — Tom Bombadil (WUBRG — Sagas + movimentacao de marcadores)

Construido do zero em 2026-09-22 junto com a lista (`lista.md`,
`construcao.md`), mesma disciplina de todos os simuladores desta
biblioteca (CLAUDE.md, Regras #1-#6): oraculo real das 100 cartas
consultado ao vivo no Scryfall (cache em `scryfall_oracle.json`), rulings
das pecas-chave lidas, TODAS as habilidades de TODAS as cartas
implementadas ou documentadas como 📊 estrutural (so' quando dependem de
estado real de oponente que um goldfish solo nao modela), varredura de
tags orfas antes de considerar pronto.

======================================================================
MOTOR REAL DESTE DECK (verificado via Scryfall + CR 714, nao decorado)
======================================================================
Tom Bombadil ({W}{U}{B}{R}{G}, 4/4): "As long as there are four or more
lore counters among Sagas you control, Tom Bombadil has hexproof and
indestructible. Whenever the final chapter ability of a Saga you control
resolves, reveal cards from the top of your library until you reveal a
Saga card. Put that card onto the battlefield and the rest on the bottom
of your library in a random order. This ability triggers only once each
turn."

Regras de Saga usadas literalmente (`rules-cache/comprehensive-rules.txt`):
- 714.2b: capitulo N dispara "when one or more lore counters are put onto
  this Saga, if the number of lore counters on it was less than N and
  became at least N" -- por isso TODA colocacao de marcador de saber
  (turno normal, proliferate, Satsuki, Clockspinning, mover marcador,
  Resourceful Defense, read ahead) passa por uma unica funcao
  `add_counters()`, que empilha TODOS os capitulos atravessados. Remover
  marcador nao dispara nada (e' so' `remove_counters()`), mas o capitulo
  dispara de novo quando o marcador volta -- o motor de "repetir
  capitulo".
- 714.3b: o marcador do turno entra "as a player's precombat main phase
  begins" (NAO no draw step) -- `precombat_lore_step()` roda no inicio da
  fase principal pre-combate, depois do draw (Regra #6: ordem de fases
  conferida em `run_turn`).
- 714.4: a Saga e' sacrificada (acao baseada em estado) quando tem
  marcadores >= capitulo final E nao e' a fonte de um capitulo que
  disparou e ainda nao saiu da pilha. Por isso existe uma pilha real
  (`state.stack`) e a checagem de SBA (`check_sba`) roda entre CADA
  resolucao -- remover 1 marcador EM RESPOSTA ao capitulo final
  (`try_save_final`) mantem a Saga viva e repete o capitulo final no
  turno seguinte (e o gatilho do Tom de novo).
- Ruling do Tom: o gatilho dele e' depois que o capitulo final termina de
  resolver (`on_final_chapter_resolved`) -- funciona ate' se o proprio
  capitulo final devolve o Tom ao campo.
- Ruling da Satsuki: por marcador numa Saga que ja' esta' no capitulo
  final nao dispara nada (714.2b literal: "was less than N").
- Ruling do Estrid's Invocation: cada re-entrada e' um objeto novo (sem
  marcadores), so' copia encantamento que JA' esta' no campo; copiando
  Saga que transforma, o capitulo III exila e ela fica no exilio.
- Ruling do Urza's Saga: capitulo III so' acha custo de mana EXATO {0} ou
  {1} -- nesta lista, Sol Ring ({1}) e Hex Parasite (custo impresso {1};
  o {B/P} e' da habilidade, nao do custo).

Simplificacoes documentadas (omissoes explicitas, nunca inventadas):
- Sem oponente real: todo dano/perda de vida de oponente e'
  `proxy_damage_total` agregado; "each opponent loses X" = X *
  NUM_OPPONENTS (mesma convencao do Megatron/Nekusar).
- 📊 `interaction_plays`: capitulos/magicas que so' miram permanente,
  mao ou cemiterio de OPONENTE (Kami War I/II, Binding I, Helvault I/II,
  Bahamut I/II, Awaken I, Galactus I e ataque, ECD I/II, Eldest Reborn
  I/II, Birth II, Primal Odin I, Yojimbo I-III, Cruelty I, Kiora II/III,
  In the Darkness IV, There and Back Again I (can't block), Swords,
  Leyline Binding ETB). Nunca fabrico board de oponente.
- 📊 condicoes que comparam com o board de oponente: Birth of the
  Imperium III ("each opponent who controls fewer creatures than you"),
  Summon: Fenrir III ("the creature with the greatest power"), Summon:
  Yojimbo IV ("opponents who control a creature with power 4+"), Scholar
  of New Horizons ("if an opponent controls more lands" -- sempre vai pra
  mao), Exotic Orchard (cores de terreno de oponente -- mesma convencao
  do Bumbleflower, produz 1 mana sem cor definida).
- Combate: "ataca" = sem doenca de invocacao, sem bloqueio modelado
  (convencao de todos os simuladores). Por isso Summon: Primal Odin II
  ("that player loses the game") vira a metrica `odin_eliminations`
  (limitada a NUM_OPPONENTS), nunca uma vitoria automatica.
- Teferi's Protection: 📊 no goldfish (sem nada pra proteger contra);
  no modo de resiliencia e' usada DE VERDADE, reativa, se sobrou mana
  aberta no fim do meu turno (`try_teferis_protection_response`).
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
    types: frozenset
    tags: frozenset = field(default_factory=frozenset)
    power: int = 0
    toughness: int = 0
    pips: dict = field(default_factory=dict)
    produces: frozenset = field(default_factory=frozenset)
    chapters: int = 0          # capitulo final (0 = nao e' Saga)
    colors: frozenset = field(default_factory=frozenset)  # cor do permanente (Bloom Tender/Faeburrow)

    @property
    def ctype(self) -> str:
        for t in ("land", "creature", "planeswalker", "artifact", "enchantment", "instant", "sorcery"):
            if t in self.types:
                return t
        return "sorcery"


CARD_DB: dict[str, Card] = {}


def add(name, mv, types, tags=(), power=0, toughness=0, pips=None, produces=None, chapters=0, colors=None):
    pips = dict(pips or {})
    if colors is None:
        colors = {c for c in pips if c in "WUBRG"}
    CARD_DB[name] = Card(name=name, mv=mv, types=frozenset(types), tags=frozenset(tags), power=power,
                         toughness=toughness, pips=pips, produces=frozenset(produces or ()), chapters=chapters,
                         colors=frozenset(colors))


WUBRG = ("W", "U", "B", "R", "G")
COMMANDER = "Tom Bombadil"
add(COMMANDER, 5, {"creature", "legendary"}, set(), power=4, toughness=4,
    pips={"W": 1, "U": 1, "B": 1, "R": 1, "G": 1})

SAGA = {"enchantment", "saga"}
SUMMON = {"enchantment", "creature", "saga"}

# --- Sagas (24 magicas + Urza's Saga no slot de terreno) ---------------------
add("The Kami War // O-Kagachi Made Manifest", 6, SAGA, {"transform_saga"}, chapters=3,
    pips={"W": 1, "U": 1, "B": 1, "R": 1, "G": 1})
add("Binding the Old Gods", 4, SAGA, chapters=3, pips={"B": 1, "G": 1})
add("There and Back Again", 5, SAGA, chapters=3, pips={"R": 2})
add("Kiora Bests the Sea God", 7, SAGA, chapters=3, pips={"U": 2})
add("Summon: Bahamut", 9, SUMMON, {"flying"}, power=9, toughness=9, chapters=4, colors=set())
add("Battle at the Helvault", 6, SAGA, chapters=3, pips={"W": 2})
add("War of the Last Alliance", 4, SAGA, chapters=3, pips={"W": 1})
add("Song of Eärendil", 5, SAGA, chapters=3, pips={"G": 1, "U": 1})
add("The Creation of Avacyn", 3, SAGA, chapters=3, pips={"B": 2})
add("Awaken the Honored Dead", 3, SAGA, chapters=3, pips={"B": 1, "G": 1, "U": 1})
add("The Coming of Galactus", 5, SAGA, chapters=4, pips={"B": 2, "G": 1})
add("Jugan Defends the Temple // Remnant of the Rising Star", 3, SAGA, {"transform_saga"}, chapters=3,
    pips={"G": 1})
add("Elspeth Conquers Death", 5, SAGA, chapters=3, pips={"W": 2})
add("The Eldest Reborn", 5, SAGA, chapters=3, pips={"B": 1})
add("The Bath Song", 4, SAGA, chapters=3, pips={"U": 1})
add("The Cruelty of Gix", 5, SAGA, {"read_ahead"}, chapters=3, pips={"B": 2})
add("Birth of the Imperium", 5, SAGA, chapters=3, pips={"W": 1, "U": 1, "B": 1})
add("In the Darkness Bind Them", 6, SAGA, chapters=4, pips={"U": 1, "B": 1, "R": 1})
add("Summon: Knights of Round", 8, SUMMON, {"indestructible"}, power=3, toughness=3, chapters=5, pips={"W": 2})
add("Summon: Primal Odin", 6, SUMMON, power=5, toughness=3, chapters=3, pips={"B": 2})
add("Summon: Fenrir", 3, SUMMON, power=3, toughness=2, chapters=3, pips={"G": 1})
add("Fable of the Mirror-Breaker // Reflection of Kiki-Jiki", 3, SAGA, {"transform_saga"}, chapters=3,
    pips={"R": 1})
add("The First Iroan Games", 3, SAGA, chapters=4, pips={"G": 1})
add("Summon: Yojimbo", 4, SUMMON, {"vigilance"}, power=5, toughness=5, chapters=4, pips={"W": 1})

# Faces de tras (so' existem no campo, depois do capitulo III transformar).
# CR 712.8e / ruling da Kami War: valor de mana da face de tras = da frente.
add("O-Kagachi Made Manifest", 6, {"enchantment", "creature"}, {"flying", "trample"},
    power=6, toughness=6, colors=set(WUBRG))
add("Remnant of the Rising Star", 3, {"enchantment", "creature"}, {"flying"},
    power=2, toughness=2, colors={"G"})
add("Reflection of Kiki-Jiki", 3, {"enchantment", "creature"}, set(),
    power=2, toughness=2, colors={"R"})
BACK_FACE = {
    "The Kami War // O-Kagachi Made Manifest": "O-Kagachi Made Manifest",
    "Jugan Defends the Temple // Remnant of the Rising Star": "Remnant of the Rising Star",
    "Fable of the Mirror-Breaker // Reflection of Kiki-Jiki": "Reflection of Kiki-Jiki",
}

# --- Motor de marcadores (M2-M5 do construcao.md) ---------------------------
add("Resourceful Defense", 3, {"enchantment"}, set(), pips={"W": 1})
add("Goldberry, River-Daughter", 2, {"creature", "legendary"}, set(), power=1, toughness=3, pips={"U": 1})
add("Nexus Mentality", 4, {"instant"}, set(), pips={"U": 1})
add("Power Conduit", 2, {"artifact"}, {"power_conduit"})
add("Scholar of New Horizons", 2, {"creature"}, set(), power=1, toughness=1, pips={"W": 1})
add("O'aka, Traveling Merchant", 2, {"creature", "legendary"}, set(), power=1, toughness=2, pips={"U": 1})
add("Hex Parasite", 1, {"artifact", "creature"}, {"hex_parasite"}, power=1, toughness=1, colors=set())
add("Clockspinning", 1, {"instant"}, set(), pips={"U": 1})
add("Satsuki, the Living Lore", 2, {"creature", "legendary"}, set(), power=1, toughness=3,
    pips={"G": 1, "W": 1})
add("Barbara Wright", 2, {"creature", "legendary"}, set(), power=1, toughness=3, pips={"W": 1})
add("Flux Channeler", 3, {"creature"}, set(), power=2, toughness=2, pips={"U": 1})
add("Ripples of Potential", 2, {"instant"}, set(), pips={"U": 1})
add("Weaver of Harmony", 2, {"enchantment", "creature"}, set(), power=2, toughness=2,
    pips={"G": 1})
add("Strionic Resonator", 2, {"artifact"}, set())
add("Estrid's Invocation", 3, {"enchantment"}, set(), pips={"U": 1})

# --- Retorno por Saga terminada (M6) ----------------------------------------
add("Narci, Fable Singer", 4, {"creature", "legendary"}, {"lifelink"}, power=3, toughness=3,
    pips={"W": 1, "B": 1, "G": 1})
add("Historian's Boon", 4, {"enchantment"}, set(), pips={"W": 1})
add("Femeref Enchantress", 2, {"creature"}, set(), power=1, toughness=2, pips={"G": 1, "W": 1})

# --- Enchantress (M7) ---------------------------------------------------------
add("Sythis, Harvest's Hand", 2, {"enchantment", "creature", "legendary"}, set(), power=1, toughness=2,
    pips={"G": 1, "W": 1})
add("Enchantress's Presence", 3, {"enchantment"}, set(), pips={"G": 1})
add("Setessan Champion", 3, {"creature"}, set(), power=1, toughness=3, pips={"G": 1})
add("Eidolon of Blossoms", 4, {"enchantment", "creature"}, set(), power=2, toughness=2, pips={"G": 2})

# --- Rampa ------------------------------------------------------------------
add("Sol Ring", 1, {"artifact"}, set())
add("Arcane Signet", 2, {"artifact"}, set())
add("Utopia Sprawl", 1, {"enchantment", "aura"}, set(), pips={"G": 1})
add("Fertile Ground", 2, {"enchantment", "aura"}, set(), pips={"G": 1})
add("Sanctum Weaver", 2, {"enchantment", "creature"}, set(), power=0, toughness=2, pips={"G": 1})
add("Bloom Tender", 2, {"creature"}, set(), power=1, toughness=1, pips={"G": 1})
add("Faeburrow Elder", 3, {"creature"}, {"vigilance"}, power=0, toughness=0,
    pips={"G": 1, "W": 1})
add("Enduring Vitality", 3, {"enchantment", "creature"}, {"vigilance"}, power=3, toughness=3,
    pips={"G": 2})
add("Farseek", 2, {"sorcery"}, set(), pips={"G": 1})
add("Prismatic Omen", 2, {"enchantment"}, set(), pips={"G": 1})

# --- Recursao -----------------------------------------------------------------
add("Replenish", 4, {"sorcery"}, set(), pips={"W": 1})
add("Resurgent Belief", 0, {"sorcery"}, {"suspend_only"}, pips={"W": 1})
add("Starfield of Nyx", 5, {"enchantment"}, set(), pips={"W": 1})

# --- Interacao / protecao / tutor ---------------------------------------------
add("Swords to Plowshares", 1, {"instant"}, set(), pips={"W": 1})
add("Leyline Binding", 6, {"enchantment"}, {"flash"}, pips={"W": 1})
add("Teferi's Protection", 3, {"instant"}, {"teferis_protection"}, pips={"W": 1})
add("Enlightened Tutor", 1, {"instant"}, set(), pips={"W": 1})

# --- Tokens -------------------------------------------------------------------
TOKEN = {"creature", "token"}
add("Kraken Token", 0, TOKEN, {"hexproof"}, power=8, toughness=8, colors={"U"})
add("Smaug", 0, TOKEN | {"legendary"}, {"flying", "haste"}, power=6, toughness=6, colors={"R"})
add("Avacyn", 0, TOKEN | {"legendary"}, {"flying", "vigilance", "indestructible"}, power=8, toughness=8,
    colors={"W"})
add("Galactus", 0, TOKEN | {"legendary"}, {"flying", "trample"}, power=16, toughness=16, colors={"B"})
add("Human Monk Token", 0, TOKEN, set(), power=1, toughness=1, colors={"G"})
add("Bird Token", 0, TOKEN, {"flying"}, power=2, toughness=2, colors={"U"})
add("Wraith Token", 0, TOKEN, {"menace"}, power=3, toughness=3, colors={"B"})
add("Knight Token", 0, TOKEN, set(), power=2, toughness=2, colors={"W"})
add("Astartes Warrior Token", 0, TOKEN, {"vigilance"}, power=2, toughness=2, colors={"W"})
add("Goblin Shaman Token", 0, TOKEN, set(), power=2, toughness=2, colors={"R"})
add("Human Soldier Token", 0, TOKEN, set(), power=1, toughness=1, colors={"W"})
add("Soldier Token", 0, TOKEN, set(), power=1, toughness=1, colors={"W"})
add("Angel Token", 0, TOKEN, {"flying", "vigilance"}, power=4, toughness=4, colors={"W"})
add("Construct Token", 0, TOKEN | {"artifact"}, set(), power=0, toughness=0, colors=set())

# --- Terrenos -----------------------------------------------------------------
# LAND_TYPES: tipos basicos IMPRESSOS (Farseek/Binding/There and Back/
# Scholar/fetches/Leyline Binding domain leem isso -- Prismatic Omen so'
# muda terreno NO CAMPO, nunca carta na biblioteca).
LAND_TYPES: dict[str, frozenset] = {}
TYPE_COLOR = {"Plains": "W", "Island": "U", "Swamp": "B", "Mountain": "R", "Forest": "G"}


def add_land(name, basic_types=(), tags=(), produces=None, types=None):
    basic_types = frozenset(basic_types)
    LAND_TYPES[name] = basic_types
    if produces is None:
        produces = {TYPE_COLOR[t] for t in basic_types}
    add(name, 0, types or {"land"}, tags, produces=produces)


for _b in ("Forest", "Plains", "Island", "Swamp", "Mountain"):
    add_land(_b, {_b}, {"basic"})
for _n, _t in {"Indatha Triome": ("Plains", "Swamp", "Forest"), "Ketria Triome": ("Forest", "Island", "Mountain"),
               "Raugrin Triome": ("Island", "Mountain", "Plains"), "Savai Triome": ("Mountain", "Plains", "Forest"),
               "Zagoth Triome": ("Swamp", "Forest", "Island")}.items():
    add_land(_n, _t, {"etb_tapped", "cycling3"})
# Duals originais (ABUR) -- 2026-09-22, pedido do usuario: substituem os 6
# shocks e as 4 tri-lands de Nova Capenna (que entravam viradas). Oraculo:
# so' os tipos basicos (mana implicita), entram desviradas, sem vida.
for _n, _t in {"Savannah": ("Forest", "Plains"), "Tropical Island": ("Forest", "Island"),
               "Bayou": ("Swamp", "Forest"), "Tundra": ("Plains", "Island"),
               "Scrubland": ("Plains", "Swamp"), "Taiga": ("Mountain", "Forest"),
               "Underground Sea": ("Island", "Swamp"), "Badlands": ("Swamp", "Mountain"),
               "Volcanic Island": ("Island", "Mountain"), "Plateau": ("Mountain", "Plains")}.items():
    add_land(_n, _t, set())
FETCHES = {"Windswept Heath": ("Forest", "Plains"), "Flooded Strand": ("Plains", "Island"),
           "Wooded Foothills": ("Mountain", "Forest"), "Verdant Catacombs": ("Swamp", "Forest"),
           "Misty Rainforest": ("Forest", "Island")}
for _n in FETCHES:
    add_land(_n, (), {"fetch"}, produces=set())
add_land("Command Tower", (), set(), produces=set(WUBRG))           # identidade do comandante = WUBRG
add_land("Exotic Orchard", (), set(), produces=set())
add_land("City of Brass", (), {"pain_any"}, produces=set(WUBRG))
add_land("Mana Confluence", (), {"pain_any"}, produces=set(WUBRG))
add_land("Reflecting Pool", (), set(), produces=set())
add_land("The World Tree", (), {"etb_tapped"}, produces={"G"})
add_land("Nesting Grounds", (), {"nesting_grounds"}, produces=set())
add_land("Karn's Bastion", (), set(), produces=set())
add_land("Serra's Sanctum", (), set(), produces={"W"}, types={"land", "legendary"})
add_land("Hall of Heliod's Generosity", (), set(), produces=set(), types={"land", "legendary"})
# Urza's Saga: Enchantment Land — Urza's Saga. E' Saga de verdade (conta pro
# Tom, pro limiar de 4 marcadores e pro Serra's Sanctum/Sanctum Weaver);
# a habilidade de mana ({T}: Add {C}) so' existe depois do capitulo I.
add_land("Urza's Saga", (), set(), produces=set(), types={"land", "enchantment", "saga"})
CARD_DB["Urza's Saga"].chapters = 3

# Palavras-chave cadastradas no oraculo mas SEM efeito num goldfish solo
# (📊 estrutural, nunca julgamento de valor): trample/menace so' importam
# contra bloqueador; hexproof so' contra alvo de oponente (o modo de
# resiliencia so' mira INTERACTION_ENGINE_PRIORITY); flash (Leyline Binding)
# so' importa respondendo no turno de oponente.
KEYWORDS_NO_EFFECT_IN_GOLDFISH = {"trample", "menace", "hexproof", "flash"}
assert all(k in {t for c in CARD_DB.values() for t in c.tags} for k in KEYWORDS_NO_EFFECT_IN_GOLDFISH)

LAND_NAMES = {n for n, c in CARD_DB.items() if "land" in c.types}
SAGA_CARD_NAMES = {n for n, c in CARD_DB.items() if "saga" in c.types and "token" not in c.types}


# ---------------------------------------------------------------------------
# Permanent / GameState
# ---------------------------------------------------------------------------

@dataclass
class Permanent:
    card: str                     # nome da carta (ou do token); DFC transformada mantem o nome completo
    uid: int
    tapped: bool = False
    counters: dict = field(default_factory=dict)   # tipo -> quantidade ("lore", "+1/+1", "flying", ...)
    entered_turn: int = 0
    is_token: bool = False
    copy_of: Optional[str] = None     # Estrid's Invocation: nome do encantamento copiado
    transformed: bool = False         # DFC com a face de tras pra cima
    attached_to: Optional[int] = None # Auras (Utopia Sprawl/Fertile Ground) -> uid do terreno
    chosen_color: str = ""            # Utopia Sprawl ("As this Aura enters, choose a color")
    exiled_card: Optional[str] = None # The Creation of Avacyn I (carta exilada virada pra baixo, ligada)
    temp_power: int = 0               # bonus "ate o fim do turno"
    noncreature: bool = False         # Enduring Vitality voltou como encantamento nao-criatura
    ability_used_turn: int = -1       # {T}/"once each turn" de habilidade ativada
    urza_mana: bool = False           # Urza's Saga ganhou "{T}: Add {C}" (capitulo I)
    urza_construct: bool = False      # Urza's Saga ganhou a habilidade de Construct (capitulo II)
    odin_lethal: bool = False         # Summon: Primal Odin II (Zantetsuken)
    phased_out: bool = False          # Teferi's Protection (modo de resiliencia)
    sac_at_end: bool = False          # token do Reflection of Kiki-Jiki
    haste_until_eot: bool = False


@dataclass
class GameState:
    turn: int = 0
    hand: list = field(default_factory=list)
    battlefield: list = field(default_factory=list)
    graveyard: list = field(default_factory=list)
    library: list = field(default_factory=list)
    exile: list = field(default_factory=list)
    suspended: list = field(default_factory=list)  # [{"card": nome, "time": n}] (Resurgent Belief)
    stack: list = field(default_factory=list)
    mulligans: int = 0
    next_uid: int = 1
    rng: Optional[random.Random] = None

    lands_played_this_turn: int = 0
    mana_spent_this_turn: int = 0
    bonus_mana_pool: int = 0
    bonus_mana_colors: set = field(default_factory=set)
    mana_reserve: int = 0          # modo de resiliencia: mana guardada pro Teferi's Protection

    commander_in_play: bool = False
    commander_uid: Optional[int] = None
    commander_cast_count: int = 0
    commander_cast_turn: Optional[int] = None
    commander_damage_dealt: int = 0
    commander_damage_win: bool = False

    tom_triggered_this_turn: bool = False
    weaver_used_turn: int = -1
    fenrir_next_creature_bonus: int = 0
    double_strike_this_turn: bool = False
    ring_level: int = 0
    ring_bearer_uid: Optional[int] = None
    treasures: int = 0
    gold_tokens: int = 0
    life: int = 40

    # metricas ---------------------------------------------------------------
    proxy_damage_total: int = 0
    narci_drain_total: int = 0
    mega_flare_total: int = 0
    cards_drawn_extra: int = 0
    interaction_plays: int = 0
    structural_unmeasured: int = 0   # 📊 condicoes que dependem do board de oponente
    tom_triggers: int = 0
    tom_sagas_put: int = 0
    tom_sagas_mv: int = 0
    tom_protected_turns: int = 0
    chapters_resolved: int = 0
    final_chapters_resolved: int = 0
    sagas_cast: int = 0
    lore_added_total: int = 0
    lore_removed_total: int = 0
    counters_moved_total: int = 0
    finals_saved: int = 0
    resourceful_triggers: int = 0
    resourceful_chain_max: int = 0
    chain_current: int = 0
    tokens_created: int = 0
    treasures_created_total: int = 0
    recursion_events_total: int = 0
    odin_eliminations: int = 0
    lethal_turn: Optional[int] = None   # 1o turno com dano proxy acumulado >= 40 * NUM_OPPONENTS
    taba_iii_this_turn: int = 0
    infinite_combo_turn: Optional[int] = None   # loop de mana infinita (ver `on_final_chapter_resolved`)
    library_emptied: bool = False
    usage: dict = field(default_factory=dict)   # contadores por carta/habilidade (testes dirigidos)
    mana_by_turn: list = field(default_factory=list)  # mana total disponivel na fase principal 1 (metrica de rampa)

    # Modo de resiliencia (interacao de oponente) -- mesmo design final dos
    # outros 18 decks. `interaction_rng` None = modo padrao, totalmente inerte.
    interaction_rng: Optional[random.Random] = None
    wiped_this_round: bool = False
    graveyard_wipe_used: bool = False
    tp_active: bool = False
    tp_ready: bool = False
    smart_removals_total: int = 0
    smart_removal_log: list = field(default_factory=list)
    smart_attacks_taken_total: int = 0
    smart_attack_log: list = field(default_factory=list)
    smart_discards_total: int = 0
    smart_discard_log: list = field(default_factory=list)
    smart_wipes_total: int = 0
    smart_wipe_log: list = field(default_factory=list)
    smart_artifact_wipes_total: int = 0
    smart_artifact_wipe_log: list = field(default_factory=list)
    smart_enchantment_wipes_total: int = 0
    smart_enchantment_wipe_log: list = field(default_factory=list)
    smart_counters_total: int = 0
    smart_counter_log: list = field(default_factory=list)
    smart_graveyard_wipes_total: int = 0
    smart_graveyard_wipe_log: list = field(default_factory=list)
    smart_graveyard_snipes_total: int = 0
    smart_graveyard_snipe_log: list = field(default_factory=list)
    tp_saves_total: int = 0


def use(state: GameState, key: str, n: int = 1):
    state.usage[key] = state.usage.get(key, 0) + n


def new_uid(state: GameState) -> int:
    u = state.next_uid
    state.next_uid += 1
    return u


def find_perm(state: GameState, uid: int) -> Optional[Permanent]:
    return next((p for p in state.battlefield if p.uid == uid), None)


def perms_named(state: GameState, name: str) -> list:
    return [p for p in state.battlefield if p.card == name and not p.phased_out]


def has(state: GameState, name: str) -> bool:
    return any(p.card == name and not p.phased_out for p in state.battlefield)


# ---------------------------------------------------------------------------
# Caracteristicas efetivas (copia / transformada / Starfield of Nyx)
# ---------------------------------------------------------------------------

def eff_name(perm: Permanent) -> str:
    if perm.copy_of:
        return perm.copy_of
    if perm.transformed:
        return BACK_FACE[perm.card]
    return perm.card


def eff(perm: Permanent) -> Card:
    return CARD_DB[eff_name(perm)]


def perm_mv(perm: Permanent) -> int:
    # Token = MV 0; copia (Estrid's Invocation) = MV do copiado; face de tras
    # = MV da frente (ja' cadastrado assim no CARD_DB).
    if perm.is_token:
        return 0
    return eff(perm).mv


def is_land(perm: Permanent) -> bool:
    return "land" in eff(perm).types


def is_enchantment(perm: Permanent) -> bool:
    return "enchantment" in eff(perm).types


def is_artifact(perm: Permanent) -> bool:
    return "artifact" in eff(perm).types


def is_aura(perm: Permanent) -> bool:
    return "aura" in eff(perm).types


def is_saga(perm: Permanent) -> bool:
    return "saga" in eff(perm).types


def is_legendary(perm: Permanent) -> bool:
    return "legendary" in eff(perm).types


def enchantment_count(state: GameState) -> int:
    return sum(1 for p in state.battlefield if is_enchantment(p) and not p.phased_out)


def starfield_active(state: GameState) -> bool:
    # "As long as you control five or more enchantments, each other non-Aura
    # enchantment you control is a creature ... base P/T = its mana value."
    return has(state, "Starfield of Nyx") and enchantment_count(state) >= 5


def starfield_animated(state: GameState, perm: Permanent) -> bool:
    return (perm.card != "Starfield of Nyx" and is_enchantment(perm) and not is_aura(perm)
            and starfield_active(state))


def is_creature(state: GameState, perm: Permanent) -> bool:
    if perm.phased_out:
        return False
    if perm.noncreature:
        # Enduring Vitality voltou como encantamento nao-criatura -- mas o
        # Starfield ainda anima qualquer encantamento nao-Aura.
        return starfield_animated(state, perm)
    if "creature" in eff(perm).types:
        return True
    return starfield_animated(state, perm)


def creatures(state: GameState) -> list:
    return [p for p in state.battlefield if is_creature(state, p)]


def colors_among_permanents(state: GameState) -> set:
    cols = set()
    for p in state.battlefield:
        if p.phased_out:
            continue
        cols |= set(eff(p).colors)
    return cols


def artifact_count(state: GameState) -> int:
    # Treasure e Gold sao artefatos de verdade (Construct do Urza's Saga conta).
    return sum(1 for p in state.battlefield if is_artifact(p) and not p.phased_out) + state.treasures + state.gold_tokens


def is_modified(state: GameState, perm: Permanent) -> bool:
    if any(v > 0 for v in perm.counters.values()):
        return True
    return any(a.attached_to == perm.uid for a in state.battlefield)


def creature_power(state: GameState, perm: Permanent) -> int:
    c = eff(perm)
    if starfield_animated(state, perm):
        base = perm_mv(perm)       # "base power ... equal to its mana value" (layer 7b, sobrescreve)
    elif c.name == "Faeburrow Elder":
        base = len(colors_among_permanents(state))   # +1/+1 por cor entre permanentes (0/0 base)
    elif c.name == "Construct Token":
        base = artifact_count(state)
    else:
        base = c.power
    p = base + perm.counters.get("+1/+1", 0) + perm.temp_power
    if (is_enchantment(perm) and has(state, "Weaver of Harmony") and perm.card != "Weaver of Harmony"
            and is_creature(state, perm)):
        p += 1   # Weaver of Harmony: "Other enchantment creatures you control get +1/+1."
    if c.name == "Remnant of the Rising Star":
        modified = sum(1 for x in creatures(state) if is_modified(state, x))
        if modified >= 5:
            p += 5
    return max(0, p)


def sick(state: GameState, perm: Permanent) -> bool:
    # Doenca de invocacao: vale pra criatura (inclusive encantamento animado
    # pelo Starfield -- ruling: "controlled continuously since the beginning
    # of their most recent turn").
    return perm.entered_turn >= state.turn and "haste" not in eff(perm).tags and not perm.haste_until_eot


def tom_protected(state: GameState) -> bool:
    lore_total = sum(p.counters.get("lore", 0) for p in state.battlefield if is_saga(p) and not p.phased_out)
    return lore_total >= 4


def is_indestructible(state: GameState, perm: Permanent) -> bool:
    if "indestructible" in eff(perm).tags or perm.counters.get("indestructible", 0) > 0:
        return True
    if perm.card == COMMANDER and tom_protected(state):
        return True
    return False


# ---------------------------------------------------------------------------
# Vida / compra / dano proxy
# ---------------------------------------------------------------------------

def draw_cards(state: GameState, n: int):
    for _ in range(n):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1
        else:
            state.library_emptied = True


def gain_life(state: GameState, n: int):
    if n > 0:
        state.life += n


def lose_life(state: GameState, n: int):
    if n > 0:
        state.life -= n


def proxy_drain(state: GameState, per_opponent: int):
    # "each opponent loses X life" -- X * NUM_OPPONENTS (convencao do Megatron).
    state.proxy_damage_total += per_opponent * NUM_OPPONENTS


def create_token(state: GameState, name: str, log: list, n: int = 1, tapped: bool = False) -> list:
    made = []
    for _ in range(n):
        perm = Permanent(card=name, uid=new_uid(state), entered_turn=state.turn, is_token=True, tapped=tapped)
        state.battlefield.append(perm)
        state.tokens_created += 1
        made.append(perm)
        on_creature_enters(state, perm, log)
    apply_legend_rule(state, log)
    return made


def create_treasure(state: GameState, n: int = 1):
    state.treasures += n
    state.treasures_created_total += n


# ---------------------------------------------------------------------------
# Nucleo de marcadores + pilha (CR 714.2b / 714.4)
# ---------------------------------------------------------------------------

def lore(perm: Permanent) -> int:
    return perm.counters.get("lore", 0)


def final_chapter(perm: Permanent) -> int:
    return eff(perm).chapters


def add_counters(state: GameState, perm: Permanent, kind: str, n: int, log: list, source: str = ""):
    """UNICO ponto de 'por marcador' do arquivo. Lore em Saga empilha TODOS
    os capitulos atravessados (714.2b: 'was less than N and became at least
    N'), em ordem de resolucao I -> II -> III (o menor fica no topo)."""
    if n <= 0 or perm not in state.battlefield:
        return
    old = perm.counters.get(kind, 0)
    perm.counters[kind] = old + n
    if kind == "lore":
        state.lore_added_total += n
    if kind == "lore" and is_saga(perm):
        fc = final_chapter(perm)
        crossed = [c for c in range(old + 1, old + n + 1) if c <= fc]
        for c in reversed(crossed):
            push_chapter(state, perm, c, log)


def remove_counters(state: GameState, perm: Permanent, kind: str, n: int) -> int:
    have = perm.counters.get(kind, 0)
    k = min(have, n)
    if k <= 0:
        return 0
    perm.counters[kind] = have - k
    if perm.counters[kind] == 0:
        del perm.counters[kind]
    if kind == "lore":
        state.lore_removed_total += k
    return k


def move_counters(state: GameState, src: Permanent, dst: Permanent, kind: str, n: int, log: list, source: str = ""):
    # Ruling (Nesting Grounds/Goldberry): mover = remover de um + por no
    # outro; tudo que reage a 'por marcador' vale no destino.
    k = remove_counters(state, src, kind, n)
    if k > 0:
        state.counters_moved_total += k
        add_counters(state, dst, kind, k, log, source=source)
    return k


def push_chapter(state: GameState, perm: Permanent, n: int, log: list):
    item = {"kind": "chapter", "uid": perm.uid, "n": n, "saga": eff_name(perm), "mv": perm_mv(perm),
            "final": n == final_chapter(perm), "copy": False}
    state.stack.append(item)
    if item["final"]:
        on_final_chapter_triggered(state, perm, log)


def on_final_chapter_triggered(state: GameState, perm: Permanent, log: list):
    # Historian's Boon: "Whenever the final chapter ability of a Saga you
    # control TRIGGERS, create a 4/4 white Angel ... flying and vigilance."
    for _ in perms_named(state, "Historian's Boon"):
        create_token(state, "Angel Token", log)
        use(state, "historians_boon_angel")
    # Resposta: remover 1 lore com o capitulo final na pilha (714.4).
    try_save_final(state, perm, log)


def pending_chapter_uids(state: GameState) -> set:
    return {it["uid"] for it in state.stack if it["kind"] == "chapter" and not it["copy"]}


def resolve_stack(state: GameState, log: list):
    guard = 0
    check_sba(state, log)
    while state.stack:
        guard += 1
        if guard > 2000 or state.infinite_combo_turn is not None:
            state.stack.clear()
            break
        item = state.stack.pop()
        resolve_item(state, item, log)
        check_sba(state, log)


def resolve_item(state: GameState, item: dict, log: list):
    kind = item["kind"]
    # Janela de resposta: copias (Strionic/Weaver) e o Enlightened Tutor/Hall
    # of Heliod em resposta ao Tom entram ACIMA do gatilho original e
    # resolvem antes dele -- o original volta pra baixo delas na pilha.
    if not item["copy"] and not item.get("responded"):
        item["responded"] = True
        depth = len(state.stack)
        if kind in ("chapter", "resourceful"):
            try_copy_trigger(state, item, log)
        elif kind == "tom":
            try_respond_to_tom_trigger(state, item, log)
        if len(state.stack) > depth:
            state.stack.insert(depth, item)
            return
    if kind == "chapter":
        perm = find_perm(state, item["uid"])
        resolve_chapter(state, perm, item["saga"], item["n"], log, is_copy=item["copy"])
        state.chapters_resolved += 1
        use(state, f"chapter:{item['saga']}:{item['n']}")
        if item["final"] and not item["copy"]:
            on_final_chapter_resolved(state, item, log)
    elif kind == "tom":
        resolve_tom_trigger(state, log)
    elif kind == "resourceful":
        resolve_resourceful(state, item, log)
    elif kind == "flux":
        proliferate(state, log, source="Flux Channeler")
    elif kind == "spell":
        resolve_spell(state, item, log)


INFINITE_LOOP_THRESHOLD = 3


def on_final_chapter_resolved(state: GameState, item: dict, log: list):
    state.final_chapters_resolved += 1
    # Loop de mana INFINITA real (legal no Bracket 3: 3+ cartas, nao e'
    # combo de 2 cartas cedo): There and Back Again no II + um jeito
    # repetivel de por lore (Clockspinning com buyback, ou Flux Channeler
    # proliferando a cada magica) + um jeito repetivel de tirar lore em
    # resposta ao III (Hex Parasite, sem {T}). Cada volta: novo Smaug -> regra
    # da lenda -> o antigo morre -> 14 Treasures, por ~6 de custo. O III
    # resolvendo 3x no mesmo turno so' acontece dentro desse loop; a partir
    # dai' e' mana infinita por construcao (-> Mega Flare/Narci infinitos),
    # entao a partida e' encerrada como vitoria por combo em vez de rodar
    # centenas de voltas (mesma logica de vitoria alternativa dos outros
    # simuladores).
    if item["saga"] == "There and Back Again":
        state.taba_iii_this_turn += 1
        if state.taba_iii_this_turn >= INFINITE_LOOP_THRESHOLD and state.infinite_combo_turn is None:
            state.infinite_combo_turn = state.turn
            use(state, "infinite_combo_smaug")
    # Narci: "Whenever the final chapter ability of a Saga you control
    # resolves, each opponent loses X life and you gain X life, X = that
    # Saga's mana value." (LKI: MV guardado no item.)
    for _ in perms_named(state, "Narci, Fable Singer"):
        x = item["mv"]
        if x > 0:
            proxy_drain(state, x)
            state.narci_drain_total += x * NUM_OPPONENTS
            gain_life(state, x * NUM_OPPONENTS)
            use(state, "narci_drain")
    # Tom: "triggers only once each turn" (ruling: depois de resolver por completo).
    if state.commander_in_play and has(state, COMMANDER) and not state.tom_triggered_this_turn:
        state.tom_triggered_this_turn = True
        state.stack.append({"kind": "tom", "copy": False})
        use(state, "tom_trigger")


def check_sba(state: GameState, log: list):
    changed = True
    while changed:
        changed = False
        pending = pending_chapter_uids(state)
        for p in list(state.battlefield):
            if p.phased_out:
                continue
            if is_saga(p) and final_chapter(p) > 0 and lore(p) >= final_chapter(p) and p.uid not in pending:
                # 714.4 -- sacrificio (Narci compra, Femeref compra, Resourceful move).
                leave_battlefield(state, p, log, to="graveyard", sacrificed=True)
                use(state, "saga_sacrificed")
                changed = True
                break
            if p.card == "Urza's Saga" and starfield_active(state):
                # Starfield anima o Urza's Saga (encantamento nao-Aura, MV 0)
                # como 0/0 -> morre por SBA de resistencia 0 (704.5f).
                leave_battlefield(state, p, log, to="graveyard")
                use(state, "urza_starfield_0_0")
                changed = True
                break
        if apply_legend_rule(state, log):
            changed = True


def apply_legend_rule(state: GameState, log: list) -> bool:
    by_name = {}
    for p in state.battlefield:
        if is_legendary(p) and not p.phased_out:
            by_name.setdefault(eff_name(p), []).append(p)
    removed = False
    for name, ps in by_name.items():
        if len(ps) > 1:
            # Mantem o mais antigo (ja' pode atacar); o resto vai pro
            # cemiterio (704.5j, nao e' sacrificio). Smaug morrendo assim
            # gera os 14 Treasures (linha real de repetir o capitulo III).
            keep = min(ps, key=lambda x: x.entered_turn)
            for p in ps:
                if p is not keep:
                    leave_battlefield(state, p, log, to="graveyard")
                    use(state, "legend_rule")
                    removed = True
    return removed


# ---------------------------------------------------------------------------
# Entrar / sair do campo
# ---------------------------------------------------------------------------

def on_enchantment_enters(state: GameState, perm: Permanent, log: list):
    # Constellation / "enchantment enters" -- vale pra QUALQUER entrada
    # (conjurada, Tom, Replenish, Starfield, Estrid re-entrando, face de tras
    # voltando transformada), nunca so' conjurada.
    for sc in perms_named(state, "Setessan Champion"):
        add_counters(state, sc, "+1/+1", 1, log, source="Setessan Champion")
        draw_cards(state, 1)
        use(state, "setessan_draw")
    for _ in perms_named(state, "Eidolon of Blossoms"):
        draw_cards(state, 1)
        use(state, "eidolon_draw")
    # Historian's Boon: "Whenever this enchantment or another NONTOKEN
    # enchantment you control enters, create a 1/1 white Soldier."
    if not perm.is_token:
        for _ in perms_named(state, "Historian's Boon"):
            create_token(state, "Soldier Token", log)
            use(state, "historians_boon_soldier")


def on_creature_enters(state: GameState, perm: Permanent, log: list):
    # Remnant of the Rising Star: "Whenever another creature you control
    # enters, you may pay {X}. When you do, put X +1/+1 counters on that
    # creature." Politica: paga X = 1 se sobrar mana depois do que esta'
    # reservado (mana sink real, nunca de graca).
    if not is_creature(state, perm):
        return
    for rem in state.battlefield:
        if eff_name(rem) == "Remnant of the Rising Star" and rem.uid != perm.uid and not rem.phased_out:
            if remaining_mana(state) >= 1:
                spend_mana(state, 1)
                add_counters(state, perm, "+1/+1", 1, log, source="Remnant of the Rising Star")
                use(state, "remnant_pay_x")


def enter_battlefield(state: GameState, name: str, log: list, tapped: bool = False, lore_start: Optional[int] = None,
                      copy_of: Optional[str] = None, transformed: bool = False, entering_counters: dict = None,
                      cast: bool = False, noncreature: bool = False) -> Permanent:
    perm = Permanent(card=name, uid=new_uid(state), entered_turn=state.turn, tapped=tapped, copy_of=copy_of,
                     transformed=transformed, noncreature=noncreature)
    state.battlefield.append(perm)
    for k, v in (entering_counters or {}).items():
        add_counters(state, perm, k, v, log)
    if name == "Scholar of New Horizons":
        add_counters(state, perm, "+1/+1", 1, log)   # "enters with a +1/+1 counter on it"
    if name == "Utopia Sprawl" or name == "Fertile Ground":
        attach_land_aura(state, perm)
    if is_creature(state, perm) and cast and state.fenrir_next_creature_bonus > 0 and eff_name(perm) != COMMANDER:
        add_counters(state, perm, "+1/+1", state.fenrir_next_creature_bonus, log, source="Summon: Fenrir II")
        state.fenrir_next_creature_bonus = 0
    if is_saga(perm) and not transformed:
        # 714.3a: sem read ahead, entra com 1 marcador; com read ahead (Barbara
        # Wright da read ahead a TODAS as Sagas; Cruelty of Gix tem nativo),
        # escolhe o capitulo e os anteriores nao disparam.
        start = lore_start if lore_start is not None else choose_saga_start(state, perm)
        saga_enter_lore(state, perm, start, log)
    if is_enchantment(perm):
        on_enchantment_enters(state, perm, log)
    on_creature_enters(state, perm, log)
    if eff_name(perm) == "Leyline Binding":
        state.interaction_plays += 1   # 📊 "exile target nonland permanent an opponent controls"
    apply_legend_rule(state, log)
    return perm


def saga_enter_lore(state: GameState, perm: Permanent, start: int, log: list):
    """714.3a + read ahead (702.155): entra com `start` marcadores; so' o
    capitulo escolhido dispara -- 'Skipped chapters don't trigger.' Achado
    real no teste dirigido: somar `start` de uma vez via add_counters
    disparava TODOS os capitulos de 1 ate' `start`."""
    if start > 1:
        perm.counters["lore"] = start - 1
        state.lore_added_total += start - 1
        use(state, "read_ahead_skip")
    add_counters(state, perm, "lore", 1, log, source="Saga ETB")


def attach_land_aura(state: GameState, aura: Permanent):
    lands = [p for p in state.battlefield if is_land(p) and not p.phased_out]
    if aura.card == "Utopia Sprawl":
        # "Enchant Forest" -- Prismatic Omen/Forest impressa/tipos de terreno.
        lands = [p for p in lands if "Forest" in land_types_in_play(state, p)]
        aura.chosen_color = scarcest_color(state)
    taken = {a.attached_to for a in state.battlefield if a.attached_to is not None}
    free = [p for p in lands if p.uid not in taken] or lands
    aura.attached_to = free[0].uid if free else None


def land_types_in_play(state: GameState, perm: Permanent) -> frozenset:
    if has(state, "Prismatic Omen"):
        return frozenset(TYPE_COLOR)
    return LAND_TYPES.get(perm.card, frozenset())


def leave_battlefield(state: GameState, perm: Permanent, log: list, to: str = "graveyard", sacrificed: bool = False):
    """Todo permanente saindo do campo passa por aqui (sacrificio de Saga,
    lenda, SBA, remocao do modo de resiliencia, exilio de Saga que
    transforma, blink do Estrid's Invocation)."""
    if perm not in state.battlefield:
        return
    was_enchantment = is_enchantment(perm)
    was_creature = is_creature(state, perm)
    snapshot = {k: v for k, v in perm.counters.items() if v > 0}
    rd_present = has(state, "Resourceful Defense")
    state.battlefield.remove(perm)
    # Auras presas no terreno que saiu vao pro cemiterio (SBA 704.5m).
    for a in [a for a in state.battlefield if a.attached_to == perm.uid]:
        leave_battlefield(state, a, log, to="graveyard")
    card_for_zone = perm.card    # Estrid's Invocation copiando = "Estrid's Invocation"
    if not perm.is_token:
        if to == "graveyard":
            state.graveyard.append(card_for_zone)
        elif to == "exile":
            state.exile.append(card_for_zone)
        elif to == "hand":
            state.hand.append(card_for_zone)
    if to == "graveyard" and was_enchantment:
        # Femeref Enchantress: "Whenever an enchantment is put into a graveyard
        # from the battlefield, draw a card."
        for _ in perms_named(state, "Femeref Enchantress"):
            draw_cards(state, 1)
            use(state, "femeref_draw")
    if sacrificed and was_enchantment:
        # Narci: "Whenever you sacrifice an enchantment, draw a card."
        for _ in perms_named(state, "Narci, Fable Singer"):
            draw_cards(state, 1)
            use(state, "narci_draw")
    if rd_present and snapshot:
        # Resourceful Defense: "Whenever a permanent you control leaves the
        # battlefield, if it had counters on it, put those counters on target
        # permanent you control."
        state.stack.append({"kind": "resourceful", "counters": snapshot, "from": eff_name(perm), "copy": False})
        state.resourceful_triggers += 1
    if to == "graveyard" and was_creature:
        on_creature_dies(state, perm, log)
    if perm.uid == state.commander_uid:
        # CR 903.9a -- ver remove_permanent (o dono move pra zona de comando).
        state.commander_in_play = False
        state.commander_uid = None
        if COMMANDER in state.graveyard:
            state.graveyard.remove(COMMANDER)
        if COMMANDER in state.exile:
            state.exile.remove(COMMANDER)
        if COMMANDER in state.hand:
            state.hand.remove(COMMANDER)
    if perm.uid == state.ring_bearer_uid:
        state.ring_bearer_uid = None


def on_creature_dies(state: GameState, perm: Permanent, log: list):
    name = eff_name(perm)
    if name == "Smaug":
        create_treasure(state, 14)    # "When Smaug dies, create fourteen Treasure tokens."
        use(state, "smaug_treasures")
    if name == "Enduring Vitality" and not perm.noncreature:
        # "When Enduring Vitality dies, if it was a creature, return it to the
        # battlefield under its owner's control. It's an enchantment. (It's not
        # a creature.)"
        if "Enduring Vitality" in state.graveyard:
            state.graveyard.remove("Enduring Vitality")
            enter_battlefield(state, "Enduring Vitality", log, noncreature=True)
            use(state, "enduring_vitality_return")
    if name == "Satsuki, the Living Lore":
        # "When Satsuki dies, choose up to one -- Return target Saga or
        # enchantment creature you control to its owner's hand; or Return
        # target Saga card from your graveyard to your hand."
        gy_sagas = [c for c in state.graveyard if c in SAGA_CARD_NAMES and c != "Urza's Saga"]
        if gy_sagas:
            best = max(gy_sagas, key=saga_value)
            state.graveyard.remove(best)
            state.hand.append(best)
            state.recursion_events_total += 1
            use(state, "satsuki_death")


def remove_permanent(state: GameState, perm: Permanent, log: list = None, source: str = "opponent"):
    """Remocao por acao de OPONENTE (modo de resiliencia). CR 903.9a: o Tom
    vai pro cemiterio de verdade primeiro (morre -- dispara Resourceful
    Defense se tivesse marcador, etc.), depois o dono o move pra zona de
    comando (`leave_battlefield` ja' limpa `commander_in_play`/`uid`), e a
    taxa CR 903.8 entra via `effective_cost`."""
    leave_battlefield(state, perm, log if log is not None else [], to="graveyard")


# ---------------------------------------------------------------------------
# Valores (so' orientam ESCOLHAS da IA do goldfish -- nunca viram numero
# medido). Escala 0-10 por capitulo; 📊 conta o valor real do jogo (Regra #5).
# ---------------------------------------------------------------------------

CHAPTER_VALUE = {
    "The Kami War // O-Kagachi Made Manifest": {1: 4, 2: 3, 3: 5},
    "Binding the Old Gods": {1: 4, 2: 3, 3: 0},
    "There and Back Again": {1: 1, 2: 3, 3: 7},
    "Kiora Bests the Sea God": {1: 6, 2: 2, 3: 5},
    "Summon: Bahamut": {1: 3, 2: 3, 3: 4, 4: 9},
    "Battle at the Helvault": {1: 4, 2: 4, 3: 7},
    "War of the Last Alliance": {1: 4, 2: 4, 3: 3},
    "Song of Eärendil": {1: 5, 2: 3, 3: 1},
    "The Creation of Avacyn": {1: 3, 2: 0, 3: 7},
    "Awaken the Honored Dead": {1: 4, 2: 1, 3: 2},
    "The Coming of Galactus": {1: 4, 2: 2, 3: 2, 4: 9},
    "Jugan Defends the Temple // Remnant of the Rising Star": {1: 2, 2: 2, 3: 3},
    "Elspeth Conquers Death": {1: 5, 2: 1, 3: 5},
    "The Eldest Reborn": {1: 3, 2: 2, 3: 5},
    "The Bath Song": {1: 4, 2: 4, 3: 2},
    "The Cruelty of Gix": {1: 2, 2: 6, 3: 6},
    "Birth of the Imperium": {1: 4, 2: 3, 3: 5},
    "In the Darkness Bind Them": {1: 4, 2: 4, 3: 4, 4: 3},
    "Summon: Knights of Round": {1: 5, 2: 5, 3: 5, 4: 5, 5: 5},
    "Summon: Primal Odin": {1: 4, 2: 6, 3: 4},
    "Summon: Fenrir": {1: 3, 2: 1, 3: 1},
    "Fable of the Mirror-Breaker // Reflection of Kiki-Jiki": {1: 3, 2: 2, 3: 5},
    "The First Iroan Games": {1: 1, 2: 3, 3: 4, 4: 2},
    "Summon: Yojimbo": {1: 4, 2: 2, 3: 2, 4: 1},
    "Urza's Saga": {1: 2, 2: 3, 3: 4},
}
LEGENDARY_TOKEN_FINAL = {"Battle at the Helvault": "Avacyn", "The Coming of Galactus": "Galactus"}


def chapter_value(state: GameState, saga: str, n: int) -> int:
    v = CHAPTER_VALUE.get(saga, {}).get(n, 1)
    tok = LEGENDARY_TOKEN_FINAL.get(saga)
    if tok and n == CARD_DB[saga].chapters and any(eff_name(p) == tok for p in state.battlefield):
        return 0    # regra da lenda: o 2o Avacyn/Galactus some na hora
    return v


def saga_value(name: str) -> int:
    return sum(CHAPTER_VALUE.get(name, {}).values())


def scarcest_color(state: GameState) -> str:
    need = {c: 0 for c in WUBRG}
    for n in state.hand:
        for c, k in CARD_DB[n].pips.items():
            if c in need:
                need[c] += k
    return min(WUBRG, key=lambda c: (color_sources(state, c) - need[c], c))


# ---------------------------------------------------------------------------
# Capitulos -- TODAS as 25 Sagas, clausula por clausula do oraculo
# ---------------------------------------------------------------------------

def ring_tempts(state: GameState, log: list):
    # "The Ring tempts you": escolhe um Ring-bearer (melhor atacante) e
    # ganha o proximo nivel (1: lendario + so' bloqueado por poder menor;
    # 2: ao atacar, compra e descarta; 3: bloqueador sacrificado (📊 sem
    # bloqueio); 4: dano de combate -> cada oponente perde 3).
    state.ring_level = min(4, state.ring_level + 1)
    cands = creatures(state)
    if cands:
        state.ring_bearer_uid = max(cands, key=lambda p: (not sick(state, p), creature_power(state, p))).uid
    use(state, "ring_tempts")


def best_creature_card_in_graveyard(state: GameState) -> Optional[str]:
    cands = [c for c in state.graveyard if "creature" in CARD_DB[c].types]
    if not cands:
        return None
    return max(cands, key=lambda c: (saga_value(c) if c in SAGA_CARD_NAMES else 0) + CARD_DB[c].mv
               + (6 if c in ENGINE_PRIORITY_CARDS else 0))


def reanimate(state: GameState, name: str, log: list, counters: dict = None) -> Permanent:
    state.graveyard.remove(name)
    state.recursion_events_total += 1
    return enter_battlefield(state, name, log, entering_counters=counters)


def search_land_to_battlefield(state: GameState, allowed_types: set, log: list, tapped: bool, basic_only=False,
                               to_hand: bool = False) -> Optional[str]:
    cands = [c for c in state.library if c in LAND_NAMES and (LAND_TYPES.get(c, frozenset()) & allowed_types)]
    if basic_only:
        cands = [c for c in cands if "basic" in CARD_DB[c].tags]
    if not cands:
        return None
    missing = [c for c in WUBRG if color_sources(state, c) == 0]
    best = max(cands, key=lambda c: (len(set(CARD_DB[c].produces) & set(missing)), len(CARD_DB[c].produces)))
    state.library.remove(best)
    state.rng.shuffle(state.library)    # "then shuffle"
    if to_hand:
        state.hand.append(best)
    else:
        tags = CARD_DB[best].tags
        if "etb_tapped" in tags:
            tapped = True          # tríome/World Tree entram virados mesmo buscados
        enter_battlefield(state, best, log, tapped=tapped)
    return best


def tutor_to_hand(state: GameState, pred, key, log: list) -> Optional[str]:
    cands = [c for c in state.library if pred(c)]
    if not cands:
        return None
    best = max(cands, key=key)
    state.library.remove(best)
    state.rng.shuffle(state.library)
    state.hand.append(best)
    return best


def tutor_priority(state: GameState, c: str) -> float:
    # O que falta de motor primeiro; depois Sagas grandes.
    on_bf = {p.card for p in state.battlefield}
    if c in ENGINE_PRIORITY_CARDS and c not in on_bf and c not in state.hand:
        return 100 - ENGINE_PRIORITY_CARDS.index(c)
    if c in SAGA_CARD_NAMES:
        return 20 + saga_value(c)
    return CARD_DB[c].mv


def resolve_chapter(state: GameState, perm: Optional[Permanent], saga: str, n: int, log: list, is_copy: bool = False):
    s = saga
    # --- The Kami War --------------------------------------------------------
    if s == "The Kami War // O-Kagachi Made Manifest":
        if n == 1:
            state.interaction_plays += 1   # 📊 exile target nonland permanent an opponent controls
        elif n == 2:
            state.interaction_plays += 1   # 📊 bounce + each opponent discards
        elif n == 3 and perm is not None and not is_copy:
            transform_saga(state, perm, log)
    # --- Binding the Old Gods -------------------------------------------------
    elif s == "Binding the Old Gods":
        if n == 1:
            state.interaction_plays += 1   # 📊 destroy target nonland permanent an opponent controls
        elif n == 2:
            search_land_to_battlefield(state, {"Forest"}, log, tapped=True)   # "Forest card", tapped
        elif n == 3:
            pass  # "creatures gain deathtouch until EOT" -- 📊 sem bloqueio modelado
    # --- There and Back Again -------------------------------------------------
    elif s == "There and Back Again":
        if n == 1:
            state.interaction_plays += 1   # 📊 "target creature can't block" (criatura de oponente)
            ring_tempts(state, log)
        elif n == 2:
            search_land_to_battlefield(state, {"Mountain"}, log, tapped=False)  # sem "tapped" no oraculo
        elif n == 3:
            create_token(state, "Smaug", log)
    # --- Kiora Bests the Sea God ----------------------------------------------
    elif s == "Kiora Bests the Sea God":
        if n == 1:
            create_token(state, "Kraken Token", log)
        else:
            state.interaction_plays += 1   # 📊 II tap/nao desvira; III rouba permanente de oponente
    # --- Summon: Bahamut ------------------------------------------------------
    elif s == "Summon: Bahamut":
        if n in (1, 2):
            state.interaction_plays += 1   # 📊 destroy up to one target nonland permanent
        elif n == 3:
            draw_cards(state, 2)
        elif n == 4:
            # Mega Flare: dano = soma do MV dos OUTROS permanentes que controlo,
            # a cada oponente. Fonte = a propria criatura (LKI se ja' saiu).
            src_uid = perm.uid if perm is not None else None
            total = sum(perm_mv(p) for p in state.battlefield if p.uid != src_uid and not p.phased_out)
            proxy_drain(state, total)
            state.mega_flare_total += total * NUM_OPPONENTS
            use(state, "mega_flare")
    # --- Battle at the Helvault -----------------------------------------------
    elif s == "Battle at the Helvault":
        if n in (1, 2):
            state.interaction_plays += 1   # 📊 exile up to one non-Saga nonland permanent de cada oponente
        elif n == 3:
            create_token(state, "Avacyn", log)
    # --- War of the Last Alliance ---------------------------------------------
    elif s == "War of the Last Alliance":
        if n in (1, 2):
            got = tutor_to_hand(state, lambda c: "creature" in CARD_DB[c].types and "legendary" in CARD_DB[c].types,
                                lambda c: tutor_priority(state, c), log)
            if got:
                use(state, "war_tutor")
        elif n == 3:
            state.double_strike_this_turn = True   # creatures you control gain double strike until EOT
            ring_tempts(state, log)
    # --- Song of Eärendil -----------------------------------------------------
    elif s == "Song of Eärendil":
        if n == 1:
            scry(state, 2)
            draw_cards(state, 2)
        elif n == 2:
            create_treasure(state, 1)
            create_token(state, "Bird Token", log)
        elif n == 3:
            for c in creatures(state):
                if "flying" not in eff(c).tags and c.counters.get("flying", 0) == 0:
                    add_counters(state, c, "flying", 1, log, source="Song of Eärendil III")
    # --- The Creation of Avacyn -----------------------------------------------
    elif s == "The Creation of Avacyn":
        if perm is None:
            return
        if n == 1:
            pick = choose_creation_target(state)
            if pick:
                state.library.remove(pick)
                state.rng.shuffle(state.library)
                perm.exiled_card = pick
                use(state, "creation_exile")
        elif n == 2:
            c = perm.exiled_card
            if c and "creature" in CARD_DB[c].types:
                lose_life(state, CARD_DB[c].mv)
        elif n == 3:
            c = perm.exiled_card
            perm.exiled_card = None
            if c:
                if "creature" in CARD_DB[c].types:
                    enter_battlefield(state, c, log)
                    use(state, "creation_put")
                else:
                    state.hand.append(c)
    # --- Awaken the Honored Dead ----------------------------------------------
    elif s == "Awaken the Honored Dead":
        if n == 1:
            state.interaction_plays += 1   # 📊 destroy target nonland permanent
        elif n == 2:
            mill(state, 3)
        elif n == 3:
            awaken_iii(state, log)
    # --- The Coming of Galactus -----------------------------------------------
    elif s == "The Coming of Galactus":
        if n == 1:
            state.interaction_plays += 1   # 📊 destroy up to one target nonland permanent
        elif n in (2, 3):
            proxy_drain(state, 2)          # each opponent loses 2 life
        elif n == 4:
            create_token(state, "Galactus", log)
    # --- Jugan Defends the Temple ---------------------------------------------
    elif s == "Jugan Defends the Temple // Remnant of the Rising Star":
        if n == 1:
            create_token(state, "Human Monk Token", log)
        elif n == 2:
            for c in sorted(creatures(state), key=lambda p: -creature_power(state, p))[:2]:
                add_counters(state, c, "+1/+1", 1, log, source="Jugan II")
        elif n == 3 and perm is not None and not is_copy:
            transform_saga(state, perm, log)
    # --- Elspeth Conquers Death -----------------------------------------------
    elif s == "Elspeth Conquers Death":
        if n in (1, 2):
            state.interaction_plays += 1   # 📊 I exile MV>=3 de oponente; II taxa magias de oponente
        elif n == 3:
            best = best_creature_card_in_graveyard(state)   # creature/planeswalker card do MEU cemiterio
            if best:
                reanimate(state, best, log, counters={"+1/+1": 1})
                use(state, "ecd_reanimate")
    # --- The Eldest Reborn ----------------------------------------------------
    elif s == "The Eldest Reborn":
        if n in (1, 2):
            state.interaction_plays += 1   # 📊 edict / discard de oponente
        elif n == 3:
            best = best_creature_card_in_graveyard(state)   # "from a graveyard" -- so' o meu e' modelado
            if best:
                reanimate(state, best, log)
                use(state, "eldest_reanimate")
    # --- The Bath Song --------------------------------------------------------
    elif s == "The Bath Song":
        if n in (1, 2):
            draw_cards(state, 2)
            discard_worst(state, 1)
        elif n == 3:
            bath_song_iii(state)
            state.bonus_mana_pool += 2
            state.bonus_mana_colors |= {"U"}
    # --- The Cruelty of Gix ---------------------------------------------------
    elif s == "The Cruelty of Gix":
        if n == 1:
            state.interaction_plays += 1   # 📊 opponent reveals hand, discard creature/planeswalker
        elif n == 2:
            got = tutor_to_hand(state, lambda c: True, lambda c: tutor_priority(state, c), log)
            lose_life(state, 3)
            if got:
                use(state, "cruelty_tutor")
        elif n == 3:
            best = best_creature_card_in_graveyard(state)
            if best:
                reanimate(state, best, log)
                use(state, "cruelty_reanimate")
    # --- Birth of the Imperium ------------------------------------------------
    elif s == "Birth of the Imperium":
        if n == 1:
            create_token(state, "Astartes Warrior Token", log, n=NUM_OPPONENTS)   # um por oponente
        elif n == 2:
            state.interaction_plays += 1   # 📊 each opponent sacrifices a creature
        elif n == 3:
            state.structural_unmeasured += 1   # 📊 "each opponent who controls fewer creatures than you"
    # --- In the Darkness Bind Them --------------------------------------------
    elif s == "In the Darkness Bind Them":
        if n in (1, 2, 3):
            create_token(state, "Wraith Token", log)
            ring_tempts(state, log)
        elif n == 4:
            state.interaction_plays += 1   # 📊 rouba criaturas de oponente ate o fim do turno
            ring_tempts(state, log)
    # --- Summon: Knights of Round ---------------------------------------------
    elif s == "Summon: Knights of Round":
        if n in (1, 2, 3, 4):
            create_token(state, "Knight Token", log, n=3)
        elif n == 5:
            src_uid = perm.uid if perm is not None else None
            for c in creatures(state):
                if c.uid != src_uid:
                    c.temp_power += 2
                    add_counters(state, c, "indestructible", 1, log, source="Knights of Round V")
    # --- Summon: Primal Odin --------------------------------------------------
    elif s == "Summon: Primal Odin":
        if n == 1:
            state.interaction_plays += 1   # 📊 destroy target creature an opponent controls
        elif n == 2:
            if perm is not None:
                perm.odin_lethal = True
        elif n == 3:
            draw_cards(state, 2)
            proxy_drain(state, 2)          # "Each player loses 2 life" -- oponentes...
            lose_life(state, 2)            # ...e eu tambem
    # --- Summon: Fenrir -------------------------------------------------------
    elif s == "Summon: Fenrir":
        if n == 1:
            search_land_to_battlefield(state, set(TYPE_COLOR), log, tapped=True, basic_only=True)
        elif n == 2:
            state.fenrir_next_creature_bonus += 1
        elif n == 3:
            state.structural_unmeasured += 1   # 📊 "if you control the creature with the greatest power"
    # --- Fable of the Mirror-Breaker ------------------------------------------
    elif s == "Fable of the Mirror-Breaker // Reflection of Kiki-Jiki":
        if n == 1:
            create_token(state, "Goblin Shaman Token", log)
        elif n == 2:
            fable_ii(state)
        elif n == 3 and perm is not None and not is_copy:
            transform_saga(state, perm, log)
    # --- The First Iroan Games ------------------------------------------------
    elif s == "The First Iroan Games":
        if n == 1:
            create_token(state, "Human Soldier Token", log)
        elif n == 2:
            cs = creatures(state)
            if cs:
                add_counters(state, max(cs, key=lambda p: creature_power(state, p)), "+1/+1", 3, log,
                             source="First Iroan Games II")
        elif n == 3:
            if any(creature_power(state, c) >= 4 for c in creatures(state)):
                draw_cards(state, 2)
        elif n == 4:
            state.gold_tokens += 1
    # --- Summon: Yojimbo ------------------------------------------------------
    elif s == "Summon: Yojimbo":
        if n in (1, 2, 3):
            state.interaction_plays += 1   # 📊 I exile de oponente; II/III Propaganda contra ataques
        elif n == 4:
            state.structural_unmeasured += 1   # 📊 X = oponentes com criatura de poder 4+
    # --- Urza's Saga ----------------------------------------------------------
    elif s == "Urza's Saga":
        if perm is None:
            return
        if n == 1:
            perm.urza_mana = True
        elif n == 2:
            perm.urza_construct = True
        elif n == 3:
            # "artifact card with mana cost {0} or {1}" (ruling: custo exato)
            cands = [c for c in state.library if c in ("Sol Ring", "Hex Parasite")]
            if cands:
                pick = "Sol Ring" if "Sol Ring" in cands else cands[0]
                state.library.remove(pick)
                state.rng.shuffle(state.library)
                enter_battlefield(state, pick, log)
                use(state, "urza_tutor")


def transform_saga(state: GameState, perm: Permanent, log: list):
    """'Exile this Saga, then return it to the battlefield transformed under
    your control.' Ruling: copia de face unica (Estrid's Invocation) fica no
    exilio. Sair do campo com 3 lore dispara Resourceful Defense."""
    if perm not in state.battlefield:
        return
    if perm.copy_of:
        leave_battlefield(state, perm, log, to="exile")
        use(state, "estrid_copy_exiled_by_transform")
        return
    name = perm.card
    leave_battlefield(state, perm, log, to="exile")
    if name in state.exile:
        state.exile.remove(name)
    enter_battlefield(state, name, log, transformed=True)
    use(state, f"transform:{name}")


def choose_creation_target(state: GameState) -> Optional[str]:
    # I: "Search your library for a card, exile it face down." II: se for
    # criatura, perco vida = MV. III: criatura vai pro campo; senao, mao.
    # Linha real: Summon: Bahamut/Knights (Saga-criatura) de graca pro campo.
    for big in ("Summon: Bahamut", "Summon: Knights of Round", "Summon: Primal Odin"):
        if big in state.library and state.life - CARD_DB[big].mv >= 15:
            return big
    cands = [c for c in state.library if c not in LAND_NAMES]
    if not cands:
        return None
    return max(cands, key=lambda c: tutor_priority(state, c))


def mill(state: GameState, n: int):
    for _ in range(n):
        if state.library:
            state.graveyard.append(state.library.pop(0))


def scry(state: GameState, n: int):
    top = state.library[:n]
    lands_in_play = sum(1 for p in state.battlefield if is_land(p))
    keep, bottom = [], []
    for c in top:
        if c in LAND_NAMES and lands_in_play >= 6:
            bottom.append(c)
        else:
            keep.append(c)
    state.library = keep + state.library[n:] + bottom


def card_keep_value(state: GameState, c: str) -> float:
    lands_in_play = sum(1 for p in state.battlefield if is_land(p))
    if c in LAND_NAMES:
        return 8 if lands_in_play < 6 else 1
    if c == "Teferi's Protection":
        return 9 if state.interaction_rng is not None else 0.5
    if c in ("Swords to Plowshares",):
        return 1
    if c in SAGA_CARD_NAMES:
        return 4 + saga_value(c) / 5
    if c in ENGINE_PRIORITY_CARDS:
        return 6
    return 3


def discard_worst(state: GameState, n: int):
    for _ in range(n):
        if not state.hand:
            return
        worst = min(state.hand, key=lambda c: card_keep_value(state, c))
        state.hand.remove(worst)
        state.graveyard.append(worst)


def fable_ii(state: GameState):
    # "You may discard up to two cards. If you do, draw that many cards."
    bad = sorted([c for c in state.hand if card_keep_value(state, c) <= 1], key=lambda c: card_keep_value(state, c))[:2]
    for c in bad:
        state.hand.remove(c)
        state.graveyard.append(c)
    draw_cards(state, len(bad))


def awaken_iii(state: GameState, log: list):
    # "You may discard a card. When you do, return target creature or land
    # card from your graveyard to your hand."
    gy = [c for c in state.graveyard if "creature" in CARD_DB[c].types or c in LAND_NAMES]
    if not gy or not state.hand:
        return
    best = max(gy, key=lambda c: card_keep_value(state, c))
    worst = min(state.hand, key=lambda c: card_keep_value(state, c))
    if card_keep_value(state, best) > card_keep_value(state, worst):
        state.hand.remove(worst)
        state.graveyard.append(worst)
        state.graveyard.remove(best)
        state.hand.append(best)
        state.recursion_events_total += 1
        use(state, "awaken_return")


def bath_song_iii(state: GameState):
    # "Shuffle any number of target cards from your graveyard into your
    # library." Escolha: nao-terrenos de valor; encantamentos ficam no
    # cemiterio se ha' recursao de encantamento (Starfield/Replenish/
    # Resurgent/Hall of Heliod) contando com eles.
    enchant_recursion = (has(state, "Starfield of Nyx") or "Replenish" in state.hand
                         or any(s["card"] == "Resurgent Belief" for s in state.suspended)
                         or has(state, "Hall of Heliod's Generosity"))
    back = []
    for c in list(state.graveyard):
        if c in LAND_NAMES:
            continue
        if enchant_recursion and "enchantment" in CARD_DB[c].types:
            continue
        back.append(c)
    for c in back:
        state.graveyard.remove(c)
        state.library.append(c)
    if back:
        state.rng.shuffle(state.library)
        use(state, "bath_song_shuffle", len(back))


# ---------------------------------------------------------------------------
# Tom Bombadil -- revelar ate' achar Saga (1x por turno)
# ---------------------------------------------------------------------------

def resolve_tom_trigger(state: GameState, log: list):
    state.tom_triggers += 1
    revealed = []
    hit = None
    while state.library:
        c = state.library.pop(0)
        if c in SAGA_CARD_NAMES:
            hit = c
            break
        revealed.append(c)
    state.rng.shuffle(revealed)          # "the rest on the bottom ... in a random order"
    state.library.extend(revealed)
    if hit:
        state.tom_sagas_put += 1
        state.tom_sagas_mv += CARD_DB[hit].mv
        use(state, f"tom_hit:{hit}")
        enter_battlefield(state, hit, log)   # "put onto the battlefield" -- nao e' conjurada


def try_respond_to_tom_trigger(state: GameState, item: dict, log: list):
    """Com o gatilho do Tom na pilha: (1) Enlightened Tutor (instantanea)
    poe a melhor Saga da biblioteca no topo -> o Tom revela exatamente ela;
    (2) senao, Hall of Heliod's Generosity poe a melhor Saga do cemiterio no
    topo; (3) Strionic Resonator copia o gatilho (2 Sagas)."""
    lib_sagas = [c for c in state.library if c in SAGA_CARD_NAMES]
    if "Enlightened Tutor" in state.hand and lib_sagas and can_pay(state, "Enlightened Tutor"):
        best = max(lib_sagas, key=saga_value)
        cast_instant(state, "Enlightened Tutor", log, et_target=best, in_response=True)
    else:
        hall = next((p for p in perms_named(state, "Hall of Heliod's Generosity") if not p.tapped), None)
        gy_sagas = [c for c in state.graveyard if c in SAGA_CARD_NAMES]
        if hall is not None and gy_sagas and land_ability_affordable(state, hall, 2, {"W"}):
            best = max(gy_sagas, key=saga_value)
            if saga_value(best) >= 12:
                activate_land(state, hall, 2)
                state.graveyard.remove(best)
                state.library.insert(0, best)
                use(state, "hall_of_heliod_tom")
    sr = next((p for p in perms_named(state, "Strionic Resonator") if not p.tapped), None)
    if sr is not None and remaining_mana(state) >= 2:
        spend_mana(state, 2)
        sr.tapped = True
        state.stack.append({"kind": "tom", "copy": True})
        use(state, "strionic_copy_tom")


# ---------------------------------------------------------------------------
# Copiar gatilho (Strionic Resonator / Weaver of Harmony)
# ---------------------------------------------------------------------------

def trigger_value(state: GameState, item: dict) -> float:
    if item["kind"] == "chapter":
        v = chapter_value(state, item["saga"], item["n"])
        if item["saga"] == "There and Back Again" and item["n"] == 3:
            v = 6   # 2o Smaug -> regra da lenda -> um morre -> 14 Treasures
        return v
    if item["kind"] == "resourceful":
        return 6 if item["counters"].get("lore", 0) >= 2 else 2
    return 0


def try_copy_trigger(state: GameState, item: dict, log: list):
    # Strionic: reservado pro gatilho do Tom enquanto ele ainda pode disparar
    # neste turno, a nao ser que o gatilho atual valha quase o mesmo.
    v = trigger_value(state, item)
    sr = next((p for p in perms_named(state, "Strionic Resonator") if not p.tapped), None)
    tom_pending = state.commander_in_play and not state.tom_triggered_this_turn
    if sr is not None and remaining_mana(state) >= 2 and (v >= 9 or (v >= 6 and not tom_pending)):
        spend_mana(state, 2)
        sr.tapped = True
        state.stack.append(dict(item, copy=True))
        use(state, "strionic_copy")
        return
    # Weaver of Harmony: "{G}, {T}: Copy target activated or triggered ability
    # you control from an ENCHANTMENT source." Capitulo (Saga) e Resourceful
    # Defense sao de fonte encantamento.
    wv = next((p for p in perms_named(state, "Weaver of Harmony")
               if not p.tapped and not sick(state, p) and is_creature(state, p)), None)
    if wv is not None and v >= 4 and remaining_mana(state) >= 1 and color_sources(state, "G") >= 1:
        spend_mana(state, 1)
        wv.tapped = True
        state.stack.append(dict(item, copy=True))
        use(state, "weaver_copy")


# ---------------------------------------------------------------------------
# Salvar o capitulo final (714.4) -- removedores de marcador em resposta
# ---------------------------------------------------------------------------

REMOVER_ORDER = ("Power Conduit", "O'aka, Traveling Merchant", "Scholar of New Horizons",
                 "Goldberry, River-Daughter")


def free_remover(state: GameState, allow_goldberry: bool = True) -> Optional[Permanent]:
    for name in REMOVER_ORDER:
        if name == "Goldberry, River-Daughter" and not allow_goldberry:
            continue
        for p in perms_named(state, name):
            if p.tapped or p.ability_used_turn == state.turn:
                continue
            if is_creature(state, p) and sick(state, p):
                continue    # {T} de criatura: doenca de invocacao
            if name == "Goldberry, River-Daughter" and p.counters.get("lore", 0) > 0:
                continue    # "a counter of each kind NOT on Goldberry"
            return p
    return None


def use_remover(state: GameState, remover: Permanent, target: Permanent, kind: str, log: list):
    """Paga o custo/efeito real de cada removedor tirando 1 marcador `kind`
    de `target`."""
    remover.tapped = True
    remover.ability_used_turn = state.turn
    name = remover.card
    if name == "Goldberry, River-Daughter":
        # {T}: move um marcador de CADA tipo que ela nao tem do alvo pra ela.
        for k in list(target.counters):
            if target.counters.get(k, 0) > 0 and remover.counters.get(k, 0) == 0:
                move_counters(state, target, remover, k, 1, log, source="Goldberry (puxa)")
        use(state, "goldberry_pull")
        return
    removed = remove_counters(state, target, kind, 1)
    if not removed:
        return
    if name == "Power Conduit":
        # "Put a +1/+1 counter on target creature" (modo util aqui).
        cs = creatures(state)
        if cs:
            add_counters(state, max(cs, key=lambda p: creature_power(state, p)), "+1/+1", 1, log,
                         source="Power Conduit")
        state.counters_moved_total += 1
        use(state, "power_conduit")
    elif name == "O'aka, Traveling Merchant":
        draw_cards(state, 1)
        use(state, "oaka_draw")
    elif name == "Scholar of New Horizons":
        # "Search for a Plains card ... If an opponent controls more lands than
        # you, you may put it onto the battlefield tapped" -- 📊 (terrenos de
        # oponente), vai pra mao.
        if search_land_to_battlefield(state, {"Plains"}, log, tapped=True, to_hand=True):
            use(state, "scholar_plains")


def final_worth_saving(state: GameState, perm: Permanent) -> int:
    name = eff_name(perm)
    if "transform_saga" in CARD_DB[name].tags and not perm.copy_of:
        return 0        # III exila e volta transformada -- nao ha' Saga pra manter
    if name == "Urza's Saga":
        return 6        # manter o terreno (e a fabrica de Construct)
    if name == "The Creation of Avacyn":
        return 0        # "the exiled card" ja' saiu na 1a vez
    v = chapter_value(state, name, final_chapter(perm))
    if name == "There and Back Again":
        v = 6           # repetir III: 2o Smaug, lenda, 14 Treasures
    if state.commander_in_play:
        v += 2          # repetir capitulo final = Tom de novo no turno seguinte
    return v


def try_save_final(state: GameState, perm: Permanent, log: list):
    if perm not in state.battlefield or lore(perm) < final_chapter(perm):
        return
    v = final_worth_saving(state, perm)
    if v < 5:
        return
    rem = free_remover(state)
    # Removedor PAGO nunca come a mana do Tom enquanto ele esta' na zona de
    # comando e daria pra conjura-lo neste turno (achado real: 3 ativacoes
    # de Hex Parasite no 714.3b gastavam 6 mana antes do Tom).
    tom_budget = 0
    if not state.commander_in_play and pips_payable(state, CARD_DB[COMMANDER].pips):
        tom_budget = effective_cost(state, COMMANDER)
    if rem is not None:
        use_remover(state, rem, perm, "lore", log)
    elif ("Clockspinning" in state.hand and v >= 6
          and can_pay(state, "Clockspinning", extra=tom_budget)):
        # Fica na pilha acima do capitulo final; o salvamento e' contado
        # quando ela resolve (`resolve_spell`).
        cast_instant(state, "Clockspinning", log, clock_target=perm, clock_mode="remove", in_response=True,
                     save_final=True)
        return
    elif (has(state, "Hex Parasite") and v >= 6
          and remaining_mana(state) - state.mana_reserve - tom_budget >= (1 if state.life > 20 else 2)
          and (state.life > 20 or color_sources(state, "B") >= 1)):
        hex_parasite_remove(state, perm, 1, log)
    else:
        return
    if lore(perm) < final_chapter(perm):
        state.finals_saved += 1
        use(state, f"saved:{eff_name(perm)}")


def hex_parasite_remove(state: GameState, target: Permanent, x: int, log: list):
    # "{X}{B/P}: Remove up to X counters from target permanent. For each
    # counter removed this way, this creature gets +1/+0 until end of turn."
    hp = perms_named(state, "Hex Parasite")[0]
    if state.life > 20:
        spend_mana(state, x)
        lose_life(state, 2)        # {B/P} pago com 2 de vida (vida alta = recurso)
    else:
        spend_mana(state, x + 1)   # {B/P} pago com {B}
    k = remove_counters(state, target, "lore", x)
    hp.temp_power += k
    use(state, "hex_parasite")


# ---------------------------------------------------------------------------
# Resourceful Defense / proliferate / read ahead
# ---------------------------------------------------------------------------

def lore_gain_value(state: GameState, saga_perm: Permanent, k: int) -> float:
    cur = lore(saga_perm)
    fc = final_chapter(saga_perm)
    name = eff_name(saga_perm)
    v = sum(chapter_value(state, name, c) for c in range(cur + 1, min(fc, cur + k) + 1))
    if cur < fc <= cur + k and state.commander_in_play and not state.tom_triggered_this_turn:
        v += 6   # capitulo final agora = gatilho do Tom neste turno
    return v


def resolve_resourceful(state: GameState, item: dict, log: list):
    counters = item["counters"]
    state.chain_current += 1
    state.resourceful_chain_max = max(state.resourceful_chain_max, state.chain_current)
    target = None
    if counters.get("lore", 0) > 0:
        sagas = [p for p in state.battlefield if is_saga(p) and not p.phased_out and lore(p) < final_chapter(p)]
        if sagas:
            target = max(sagas, key=lambda p: lore_gain_value(state, p, counters["lore"]))
    if target is None:
        cs = creatures(state)
        if cs:
            target = max(cs, key=lambda p: creature_power(state, p))
    if target is None:
        return
    use(state, "resourceful_resolve")
    for k, v in counters.items():
        add_counters(state, target, k, v, log, source="Resourceful Defense")
        state.counters_moved_total += v


def proliferate(state: GameState, log: list, source: str = ""):
    """'Choose any number of permanents and/or players, then give each
    another counter of each kind already there.' Escolha: toda Saga abaixo
    do capitulo final (menos a que tem capitulo ainda na pilha -- acabou de
    ser salva -- e Urza's Saga indo pro III sem artefato {0}/{1} na
    biblioteca e sem removedor pra salva-la) + toda criatura com marcador +
    Goldberry."""
    use(state, f"proliferate:{source}")
    targets = []
    pending = pending_chapter_uids(state)
    for p in list(state.battlefield):
        if p.phased_out or not p.counters:
            continue
        if is_saga(p):
            if lore(p) >= final_chapter(p):
                continue
            if p.uid in pending:
                continue    # capitulo dela ainda na pilha (ex.: acabou de ser salva) -- nao escolhe
            if (eff_name(p) == "Urza's Saga" and lore(p) + 1 >= final_chapter(p)
                    and not any(c in ("Sol Ring", "Hex Parasite") for c in state.library)
                    and free_remover(state) is None):
                continue
        targets.append(p)
    for p in targets:
        for k in list(p.counters):
            if p.counters.get(k, 0) > 0:
                add_counters(state, p, k, 1, log, source=source)


READ_AHEAD_FINAL_OK = {"Battle at the Helvault", "The Coming of Galactus", "There and Back Again",
                       "Summon: Bahamut", "Elspeth Conquers Death", "The Eldest Reborn", "The Cruelty of Gix"}


def choose_saga_start(state: GameState, perm: Permanent) -> int:
    name = eff_name(perm)
    read_ahead = has(state, "Barbara Wright") or "read_ahead" in CARD_DB[name].tags
    if not read_ahead:
        return 1
    use(state, "read_ahead_choice")
    fc = final_chapter(perm)
    # Pular pro capitulo final so' quando o Tom ainda pode disparar neste
    # turno e o final vale mais que os capitulos pulados (a maioria 📊).
    if state.commander_in_play and not state.tom_triggered_this_turn and name in READ_AHEAD_FINAL_OK:
        if name in ("Elspeth Conquers Death", "The Eldest Reborn", "The Cruelty of Gix"):
            if best_creature_card_in_graveyard(state) is None:
                return 2 if name == "The Cruelty of Gix" else 1
        if name == "Summon: Bahamut":
            other = sum(perm_mv(p) for p in state.battlefield if p.uid != perm.uid)
            if other < 15:
                return 1
        if chapter_value(state, name, fc) == 0:
            return 1
        return fc
    if name == "The Cruelty of Gix":
        return 2    # I e' 📊 (mao de oponente); II tutor ja'
    return 1


# ---------------------------------------------------------------------------
# Mana (abstrata, mesmo modelo dos outros simuladores: total disponivel no
# turno - gasto; cores checadas por pareamento de fontes -> simbolos)
# ---------------------------------------------------------------------------

MANA_CREATURES = {"Bloom Tender", "Faeburrow Elder", "Sanctum Weaver", "Human Monk Token", "Enduring Vitality"}
TAP_ABILITY_CREATURES = {"O'aka, Traveling Merchant", "Scholar of New Horizons", "Goldberry, River-Daughter",
                         "Satsuki, the Living Lore", "Weaver of Harmony", "Reflection of Kiki-Jiki"}


def vitality_mana_creatures(state: GameState) -> list:
    """Enduring Vitality: 'Creatures you control have {T}: Add one mana of any
    color.' (estatica -- vale mesmo com a Vitality como encantamento nao-
    criatura). Convencao deterministica: criaturas de poder <= 1 sem outra
    habilidade de {T} viram fonte de mana e NAO atacam."""
    if not has(state, "Enduring Vitality"):
        return []
    out = []
    for p in creatures(state):
        name = eff_name(p)
        if name in MANA_CREATURES or name in TAP_ABILITY_CREATURES or p.card == COMMANDER:
            continue
        if p.tapped or sick(state, p):
            continue
        if creature_power(state, p) <= 1:
            out.append(p)
    return out


def land_value(state: GameState, p: Permanent) -> int:
    if p.card == "Serra's Sanctum":
        return enchantment_count(state)
    if p.card == "Urza's Saga":
        return 1 if (p.urza_mana or has(state, "Prismatic Omen") or world_tree_active(state)) else 0
    if p.card in FETCHES:
        return 0
    return 1


def world_tree_active(state: GameState) -> bool:
    return has(state, "The World Tree") and sum(1 for p in state.battlefield if is_land(p)) >= 6


def _mana_fingerprint(state: GameState) -> tuple:
    # Tudo que `mana_units` le: composicao/estado de cada permanente + pools.
    # O gasto (`mana_spent_this_turn`) NAO entra -- e' abstrato, subtraido
    # depois em `remaining_mana`.
    return (state.turn, state.treasures, state.gold_tokens, state.bonus_mana_pool,
            tuple(sorted(state.bonus_mana_colors)),
            tuple((p.uid, p.card, p.tapped, p.phased_out, p.noncreature, p.transformed, p.copy_of,
                   p.entered_turn, p.attached_to, p.urza_mana, p.haste_until_eot, p.chosen_color,
                   p.counters.get("+1/+1", 0), p.temp_power) for p in state.battlefield))


def mana_units(state: GameState) -> list:
    """Cache por estado do campo (achado de desempenho: era 70% do tempo de
    execucao -- recalculada a cada 'posso pagar?' sem nada ter mudado)."""
    fp = _mana_fingerprint(state)
    cached = getattr(state, "_mana_cache", None)
    if cached is not None and cached[0] == fp:
        return cached[1]
    units = _mana_units_uncached(state)
    state._mana_cache = (fp, units)
    return units


def _mana_units_uncached(state: GameState) -> list:
    """Lista de unidades de mana disponiveis NESTE turno (ignorando o que ja'
    foi gasto -- o gasto e' abstrato). Cada unidade = conjunto de cores que
    ela pode pagar ("C" = so' generico)."""
    units = []
    omen = has(state, "Prismatic Omen")
    wt = world_tree_active(state)
    land_colors = set()
    for p in state.battlefield:
        if is_land(p) and not p.phased_out:
            land_colors |= set(CARD_DB[p.card].produces)
    for p in state.battlefield:
        if p.phased_out or p.tapped:
            continue
        name = eff_name(p)
        if is_land(p):
            n = land_value(state, p)
            if n <= 0:
                continue
            cols = set(CARD_DB[p.card].produces)
            if p.card == "Reflecting Pool":
                cols = set(land_colors)
            if omen or wt:
                cols = set(WUBRG)
            if p.card == "Serra's Sanctum":
                cols = {"W"} | (set(WUBRG) if (omen or wt) else set())
            units += [frozenset(cols) or frozenset({"C"})] * n
            continue
        if name == "Sol Ring":
            units += [frozenset({"C"})] * 2
        elif name == "Arcane Signet":
            units.append(frozenset(WUBRG))
        elif name in ("Utopia Sprawl", "Fertile Ground"):
            land = find_perm(state, p.attached_to) if p.attached_to else None
            if land is not None and not land.tapped:
                units.append(frozenset({p.chosen_color}) if name == "Utopia Sprawl" else frozenset(WUBRG))
        elif is_creature(state, p) and not sick(state, p):
            if name in ("Bloom Tender", "Faeburrow Elder"):
                units += [frozenset({c}) for c in colors_among_permanents(state) if c in WUBRG]
            elif name == "Sanctum Weaver":
                units += [frozenset(WUBRG)] * enchantment_count(state)
            elif name == "Human Monk Token":
                units.append(frozenset({"G"}))
            elif name == "Enduring Vitality" and has(state, "Enduring Vitality"):
                units.append(frozenset(WUBRG))
    if has(state, "Enduring Vitality"):
        units += [frozenset(WUBRG)] * len(vitality_mana_creatures(state))
    units += [frozenset(WUBRG)] * (state.treasures + state.gold_tokens)
    if state.bonus_mana_pool > 0:
        units += [frozenset(state.bonus_mana_colors or {"C"})] * state.bonus_mana_pool
    return units


def total_mana(state: GameState) -> int:
    return len(mana_units(state))


def remaining_mana(state: GameState) -> int:
    return max(0, total_mana(state) - state.mana_spent_this_turn)


def spend_mana(state: GameState, n: int):
    state.mana_spent_this_turn += n


def color_sources(state: GameState, color: str) -> int:
    return sum(1 for u in mana_units(state) if color in u)


def pips_payable(state: GameState, pips: dict) -> bool:
    """Pareamento bipartido EXATO simbolo colorido -> unidade de mana
    (caminhos aumentantes). Achado real na 1a rodada: um pareamento guloso
    falhava em casos resolviveis (ex.: GU, BGR, R, GW, UW pagam WUBRG, mas o
    guloso gastava a GW no W e ficava sem G), deixando o Tom na zona de
    comando com mana de todas as cores disponivel."""
    need = []
    for c, k in pips.items():
        if c in WUBRG:
            need += [c] * k
    if not need:
        return True
    units = [u for u in mana_units(state) if u != frozenset({"C"})]
    if len(units) < len(need):
        return False
    match_of_unit = [-1] * len(units)

    def try_assign(i: int, seen: list) -> bool:
        for j, u in enumerate(units):
            if need[i] in u and not seen[j]:
                seen[j] = True
                if match_of_unit[j] == -1 or try_assign(match_of_unit[j], seen):
                    match_of_unit[j] = i
                    return True
        return False

    for i in range(len(need)):
        if not try_assign(i, [False] * len(units)):
            return False
    return True


def domain_count(state: GameState) -> int:
    types = set()
    for p in state.battlefield:
        if is_land(p) and not p.phased_out:
            types |= set(land_types_in_play(state, p))
    return len(types)


def effective_cost(state: GameState, name: str) -> int:
    mv = CARD_DB[name].mv
    if name == COMMANDER:
        return mv + 2 * state.commander_cast_count    # CR 903.8
    if name == "Leyline Binding":
        # "Domain -- This spell costs {1} less for each basic land type among
        # lands you control." {5}{W}: so' o generico reduz.
        return 1 + max(0, 5 - domain_count(state))
    return mv


def can_pay(state: GameState, name: str, extra: int = 0, ignore_reserve: bool = False) -> bool:
    if "suspend_only" in CARD_DB[name].tags:
        return False
    reserve = 0 if ignore_reserve else state.mana_reserve
    return (remaining_mana(state) - reserve >= effective_cost(state, name) + extra
            and pips_payable(state, CARD_DB[name].pips))


def land_ability_affordable(state: GameState, land: Permanent, cost: int, colors: set = frozenset()) -> bool:
    if land.tapped or land.phased_out:
        return False
    # Virar o proprio terreno pra habilidade abre mao da mana dele.
    if remaining_mana(state) - state.mana_reserve < cost + land_value(state, land):
        return False
    return all(color_sources(state, c) >= 1 for c in colors)


def activate_land(state: GameState, land: Permanent, cost: int):
    land.tapped = True
    spend_mana(state, cost)


# ---------------------------------------------------------------------------
# Conjuracao
# ---------------------------------------------------------------------------

def on_cast(state: GameState, name: str, log: list, resolve: bool = True):
    c = CARD_DB[name]
    if "enchantment" in c.types:
        # Sythis: "Whenever you cast an enchantment spell, you gain 1 life and
        # draw a card." Enchantress's Presence: "... draw a card."
        for _ in perms_named(state, "Sythis, Harvest's Hand"):
            gain_life(state, 1)
            draw_cards(state, 1)
            use(state, "sythis_draw")
        for _ in perms_named(state, "Enchantress's Presence"):
            draw_cards(state, 1)
            use(state, "presence_draw")
    if "creature" not in c.types:
        # Flux Channeler: "Whenever you cast a noncreature spell, proliferate."
        # Ruling: resolve ANTES da magica (e mesmo se ela for contramagicada).
        for _ in perms_named(state, "Flux Channeler"):
            state.stack.append({"kind": "flux", "copy": False})
    if resolve:
        resolve_stack(state, log)


def best_copy_target(state: GameState, exclude_uid: Optional[int] = None) -> Optional[str]:
    """Estrid's Invocation: 'You may have this enchantment enter as a copy of
    an enchantment you control.' Prefere a Saga de maior valor (a copia
    comeca do capitulo I, ou do final com read ahead + Tom); senao o motor
    de encantamento mais util. Nunca copia lendario (regra da lenda)."""
    sagas = [p for p in state.battlefield if is_saga(p) and not p.phased_out and p.uid != exclude_uid
             and eff_name(p) != "Urza's Saga" and not is_legendary(p)]
    if sagas:
        return eff_name(max(sagas, key=lambda p: saga_value(eff_name(p))))
    for name in ("Enchantress's Presence", "Resourceful Defense", "Historian's Boon", "Starfield of Nyx",
                 "Eidolon of Blossoms", "Enduring Vitality", "Weaver of Harmony", "Sanctum Weaver"):
        if any(eff_name(p) == name and p.uid != exclude_uid and not p.phased_out for p in state.battlefield):
            return name
    return None


def resolve_permanent_spell(state: GameState, name: str, log: list):
    if name == "Estrid's Invocation":
        target = best_copy_target(state)
        perm = enter_battlefield(state, name, log, copy_of=target, cast=True)
        use(state, "estrid_cast_copy" if target else "estrid_cast_nocopy")
    else:
        enter_battlefield(state, name, log, cast=True)
    resolve_stack(state, log)


def cast_permanent(state: GameState, name: str, log: list):
    spend_mana(state, effective_cost(state, name))
    state.hand.remove(name)
    if name in SAGA_CARD_NAMES:
        state.sagas_cast += 1
    on_cast(state, name, log)
    resolve_permanent_spell(state, name, log)


def try_cast_commander(state: GameState, log: list):
    # Tom vem da zona de comando (BASE_LIBRARY tem so' as 99).
    if state.commander_in_play or not can_pay(state, COMMANDER):
        return
    spend_mana(state, effective_cost(state, COMMANDER))
    state.commander_cast_count += 1
    if try_smart_opponent_counter(state):
        # CR 903.8/601.2: taxa ja' paga; o cast conta mesmo contramagicado.
        log.append({"action": "cast_commander_countered", "turn": state.turn})
        return
    on_cast(state, COMMANDER, log)
    perm = enter_battlefield(state, COMMANDER, log, cast=True)
    state.commander_in_play = True
    state.commander_uid = perm.uid
    if state.commander_cast_turn is None:
        state.commander_cast_turn = state.turn
    resolve_stack(state, log)


def cast_instant(state: GameState, name: str, log: list, et_target: Optional[str] = None,
                 clock_target: Optional[Permanent] = None, clock_mode: str = "remove",
                 nexus_move: tuple = None, nexus_remove: Optional[Permanent] = None, in_response: bool = False,
                 save_final: bool = False):
    """Instantaneas/feiticos. A magica vira um item REAL da pilha, empilhado
    ANTES dos gatilhos de conjuracao dela (Flux Channeler) -- entao os
    gatilhos resolvem primeiro e a magica depois, como na regra.

    `in_response=True` = conjurada EM RESPOSTA a algo que esta' na pilha
    (Clockspinning salvando capitulo final, Enlightened Tutor no gatilho do
    Tom): NAO resolve a pilha por dentro. Achados reais (Regra #6):
    (1) o resolve aninhado resolvia o capitulo final ANTES do Clockspinning
    tirar o marcador (Saga sacrificada em vez de salva); (2) a 1a correcao
    aplicava o efeito na hora e devolvia o Clockspinning pra mao (buyback)
    com o gatilho do Flux ainda na pilha -- a mesma copia salvava varias
    Sagas numa cascata so' (partida com ~490 capitulos). Agora a carta fica
    na pilha ate' resolver."""
    cost = effective_cost(state, name)
    buyback = name == "Clockspinning" and remaining_mana(state) - state.mana_reserve >= cost + 3
    spend_mana(state, cost + (3 if buyback else 0))
    state.hand.remove(name)
    use(state, f"cast:{name}")
    item = {"kind": "spell", "name": name, "copy": False, "responded": True, "buyback": buyback,
            "et_target": et_target, "clock_uid": clock_target.uid if clock_target is not None else None,
            "clock_mode": clock_mode, "save_final": save_final,
            "nexus_move": (nexus_move[0].uid, nexus_move[1].uid) if nexus_move else None,
            "nexus_remove": nexus_remove.uid if nexus_remove is not None else None,
            "commander_at_cast": state.commander_in_play}
    state.stack.append(item)
    on_cast(state, name, log, resolve=not in_response)
    if not in_response:
        resolve_stack(state, log)


def resolve_spell(state: GameState, item: dict, log: list):
    name = item["name"]
    to_gy = True
    if name == "Enlightened Tutor":
        # "Search your library for an artifact or enchantment card, reveal it,
        # then shuffle and put that card on top."
        pick = item["et_target"] or best_enlightened_target(state)
        if pick and pick in state.library:
            state.library.remove(pick)
            state.rng.shuffle(state.library)
            state.library.insert(0, pick)
    elif name == "Clockspinning":
        mode = item["clock_mode"]
        if mode == "suspend":
            for sp in state.suspended:
                if sp["time"] > 0:
                    sp["time"] -= 1
                    use(state, "clockspinning_suspend")
                    break
            cast_ready_suspended(state, log)
        else:
            tgt = find_perm(state, item["clock_uid"]) if item["clock_uid"] is not None else None
            if tgt is None:
                # Alvo ilegal na resolucao: a magica nao resolve (608.2b) --
                # sem efeito e sem buyback.
                state.graveyard.append(name)
                use(state, "clockspinning_fizzle")
                return
            if mode == "remove":
                remove_counters(state, tgt, "lore", 1)
                if item["save_final"] and lore(tgt) < final_chapter(tgt):
                    state.finals_saved += 1
                    use(state, f"saved:{eff_name(tgt)}")
            else:
                add_counters(state, tgt, "lore", 1, log, source="Clockspinning")
        if item["buyback"]:
            state.hand.append(name)       # buyback: volta pra mao ao resolver
            to_gy = False
            use(state, "clockspinning_buyback")
    elif name == "Nexus Mentality":
        # "Choose one. If you control a commander as you cast this spell, you
        # may choose both instead." (1) move todos os marcadores de A pra B;
        # (2) remove todos de C e compra 1 por marcador removido.
        both = item["commander_at_cast"]
        mv = item["nexus_move"]
        if mv:
            a, b = find_perm(state, mv[0]), find_perm(state, mv[1])
            if a is not None and b is not None:
                for k in list(a.counters):
                    move_counters(state, a, b, k, a.counters.get(k, 0), log, source="Nexus Mentality")
                use(state, "nexus_move")
        c = find_perm(state, item["nexus_remove"]) if item["nexus_remove"] is not None else None
        if c is not None and (both or not mv):
            n = 0
            for k in list(c.counters):
                n += remove_counters(state, c, k, c.counters.get(k, 0))
            draw_cards(state, n)
            use(state, "nexus_draw", n)
    elif name == "Ripples of Potential":
        # Proliferate, depois phase out de quem ganhou marcador. No goldfish
        # nao ha' o que evitar -> nao fasa nada (fasar tiraria a criatura do
        # combate e a Saga do campo sem ganho).
        proliferate(state, log, source="Ripples of Potential")
    elif name == "Farseek":
        search_land_to_battlefield(state, {"Plains", "Island", "Swamp", "Mountain"}, log, tapped=True)
    elif name == "Replenish":
        replenish_effect(state, log)
    elif name == "Swords to Plowshares":
        state.interaction_plays += 1   # 📊 exile target creature (de oponente)
    elif name == "Teferi's Protection":
        to_gy = False
        state.exile.append(name)       # "Exile Teferi's Protection."
    if to_gy:
        state.graveyard.append(name)


def best_enlightened_target(state: GameState) -> Optional[str]:
    cands = [c for c in state.library if CARD_DB[c].types & {"artifact", "enchantment"}]
    if not cands:
        return None
    return max(cands, key=lambda c: tutor_priority(state, c))


def replenish_effect(state: GameState, log: list):
    """'Return all enchantment cards from your graveyard to the battlefield.
    (Auras with nothing to enchant remain in your graveyard.)' Tudo entra
    ao mesmo tempo: Estrid's Invocation voltando junto so' copia o que JA'
    estava no campo (ruling)."""
    before = {p.uid for p in state.battlefield}
    ench = [c for c in state.graveyard if "enchantment" in CARD_DB[c].types and c not in LAND_NAMES]
    for c in ench:
        if c in ("Utopia Sprawl", "Fertile Ground"):
            lands = [p for p in state.battlefield if is_land(p)]
            if c == "Utopia Sprawl":
                lands = [p for p in lands if "Forest" in land_types_in_play(state, p)]
            if not lands:
                continue
        state.graveyard.remove(c)
        state.recursion_events_total += 1
        if c == "Estrid's Invocation":
            olds = [p for p in state.battlefield if p.uid in before]
            tgt = None
            if olds:
                saved = state.battlefield
                state.battlefield = olds
                tgt = best_copy_target(state)
                state.battlefield = saved
            enter_battlefield(state, c, log, copy_of=tgt)
        else:
            enter_battlefield(state, c, log)
    use(state, "replenish_returned", len(ench))
    resolve_stack(state, log)


RAMP = ("Sol Ring", "Arcane Signet", "Utopia Sprawl", "Fertile Ground", "Sanctum Weaver", "Bloom Tender",
        "Faeburrow Elder", "Enduring Vitality", "Farseek", "Prismatic Omen")
DRAW_ENGINES = ("Sythis, Harvest's Hand", "Enchantress's Presence", "Setessan Champion", "Eidolon of Blossoms",
                "Narci, Fable Singer", "Femeref Enchantress", "Historian's Boon")
COUNTER_ENGINES = ("Resourceful Defense", "Barbara Wright", "Satsuki, the Living Lore", "Goldberry, River-Daughter",
                   "O'aka, Traveling Merchant", "Scholar of New Horizons", "Power Conduit", "Flux Channeler",
                   "Weaver of Harmony", "Strionic Resonator", "Hex Parasite", "Estrid's Invocation")
ENGINE_PRIORITY_CARDS = ["Resourceful Defense", "Narci, Fable Singer", "Barbara Wright", "Sythis, Harvest's Hand",
                         "Enchantress's Presence", "Satsuki, the Living Lore", "Strionic Resonator",
                         "Goldberry, River-Daughter", "Power Conduit", "Setessan Champion", "Eidolon of Blossoms",
                         "Historian's Boon", "Starfield of Nyx", "Weaver of Harmony", "Flux Channeler",
                         "Estrid's Invocation", "Femeref Enchantress", "O'aka, Traveling Merchant",
                         "Scholar of New Horizons", "Sanctum Weaver"]
NOT_IN_CAST_LOOP = {"Teferi's Protection", "Enlightened Tutor", "Clockspinning", "Nexus Mentality",
                    "Ripples of Potential", "Swords to Plowshares", "Resurgent Belief"}


def castable_now(state: GameState, c: str) -> bool:
    if c in LAND_NAMES or c in NOT_IN_CAST_LOOP or not can_pay(state, c):
        return False
    if c == "Utopia Sprawl" and not any("Forest" in land_types_in_play(state, p)
                                          for p in state.battlefield if is_land(p)):
        return False
    if c == "Fertile Ground" and not any(is_land(p) for p in state.battlefield):
        return False
    if c == "Estrid's Invocation" and best_copy_target(state) is None:
        return False
    if c == "Replenish":
        return sum(1 for g in state.graveyard if "enchantment" in CARD_DB[g].types) >= 3
    if c == "Leyline Binding":
        return effective_cost(state, c) <= 3
    return True


def cast_priority(state: GameState, c: str) -> tuple:
    # Peca de motor de marcador sem Saga nenhuma em campo nao faz nada: ai'
    # a Saga vem antes (tier 3 vs 4 se inverte).
    engines_first = len(sagas_in_play(state)) >= 1
    if c in RAMP:
        tier = 1
    elif c in DRAW_ENGINES:
        tier = 2
    elif c in COUNTER_ENGINES:
        tier = 3 if engines_first else 4
    elif c in SAGA_CARD_NAMES:
        tier = 4 if engines_first else 3
        return (tier, -saga_value(c), effective_cost(state, c), c)
    else:
        tier = 5
    return (tier, effective_cost(state, c), 0, c)


def try_cast_loop(state: GameState, log: list):
    guard = 0
    while guard < 60:
        guard += 1
        # Tom primeiro, sempre -- e re-tentado depois de CADA magica (rampa
        # conjurada no mesmo turno pode liberar a cor que faltava).
        try_cast_commander(state, log)
        cands = [c for c in state.hand if castable_now(state, c)]
        if not cands:
            break
        pick = min(cands, key=lambda c: cast_priority(state, c))
        if CARD_DB[pick].ctype in ("instant", "sorcery"):
            cast_instant(state, pick, log)
        else:
            cast_permanent(state, pick, log)


def try_suspend_resurgent(state: GameState, log: list):
    # Suspend 2--{1}{W}: acao especial (nao e' conjurar), so' quando daria
    # pra conjurar um feitico (fase principal, pilha vazia).
    if "Resurgent Belief" in state.hand and remaining_mana(state) - state.mana_reserve >= 2 \
            and color_sources(state, "W") >= 1:
        gy_ench = sum(1 for g in state.graveyard if "enchantment" in CARD_DB[g].types)
        if gy_ench >= 2 or state.turn >= 5:
            spend_mana(state, 2)
            state.hand.remove("Resurgent Belief")
            state.suspended.append({"card": "Resurgent Belief", "time": 2})
            use(state, "resurgent_suspend")


def resolve_suspended(state: GameState, log: list):
    # "At the beginning of your upkeep, remove a time counter. When the last
    # is removed, you may cast it without paying its mana cost."
    for s in state.suspended:
        if s["time"] > 0:
            s["time"] -= 1
    cast_ready_suspended(state, log)


def cast_ready_suspended(state: GameState, log: list):
    # Ruling: o gatilho de conjurar dispara quando o ULTIMO marcador de tempo
    # sai, nao importa por qual efeito (upkeep ou Clockspinning).
    for s in list(state.suspended):
        if s["time"] == 0:
            state.suspended.remove(s)
            name = s["card"]
            on_cast(state, name, log)
            if name == "Resurgent Belief":
                replenish_effect(state, log)
                use(state, "resurgent_cast")
            state.graveyard.append(name)


# ---------------------------------------------------------------------------
# Habilidades ativadas / motor de marcadores no turno
# ---------------------------------------------------------------------------

def sagas_in_play(state: GameState) -> list:
    return [p for p in state.battlefield if is_saga(p) and not p.phased_out]


def tom_can_still_trigger(state: GameState) -> bool:
    return state.commander_in_play and has(state, COMMANDER) and not state.tom_triggered_this_turn


def repeat_value(state: GameState, p: Permanent) -> int:
    """Valor de TIRAR 1 lore de uma Saga agora: o capitulo atual volta a
    disparar no proximo turno. 0 se ela nao tem lore ou se o capitulo atual
    nao vale repetir."""
    cur = lore(p)
    if cur <= 0:
        return 0
    return chapter_value(state, eff_name(p), cur)


def try_satsuki(state: GameState, log: list):
    # "{T}: Put a lore counter on each Saga you control. Activate only as a sorcery."
    for sat in perms_named(state, "Satsuki, the Living Lore"):
        if sat.tapped or sick(state, sat) or not is_creature(state, sat):
            continue
        targets = [p for p in sagas_in_play(state) if lore(p) < final_chapter(p)]
        if not targets:
            return
        sat.tapped = True
        for p in targets:
            add_counters(state, p, "lore", 1, log, source="Satsuki")
        use(state, "satsuki_activate")
        resolve_stack(state, log)


def try_goldberry(state: GameState, log: list):
    for gb in perms_named(state, "Goldberry, River-Daughter"):
        if gb.tapped or sick(state, gb) or gb.ability_used_turn == state.turn:
            continue
        if gb.counters.get("lore", 0) > 0:
            # "{U}, {T}: Move one or more counters from Goldberry onto another
            # target permanent you control. If you do, draw a card."
            targets = [p for p in sagas_in_play(state) if lore(p) < final_chapter(p)]
            if targets and remaining_mana(state) - state.mana_reserve >= 1 and color_sources(state, "U") >= 1:
                best = max(targets, key=lambda p: lore_gain_value(state, p, 1))
                spend_mana(state, 1)
                gb.tapped = True
                gb.ability_used_turn = state.turn
                move_counters(state, gb, best, "lore", 1, log, source="Goldberry (empurra)")
                draw_cards(state, 1)
                use(state, "goldberry_push")
                resolve_stack(state, log)
        else:
            # "{T}: Move a counter of each kind not on Goldberry from another
            # target permanent you control onto Goldberry." -- puxa de uma Saga
            # cujo capitulo atual vale repetir (e guarda pra empurrar depois).
            srcs = [p for p in sagas_in_play(state) if repeat_value(state, p) >= 3 and lore(p) < final_chapter(p)]
            if srcs:
                src = max(srcs, key=lambda p: repeat_value(state, p))
                use_remover(state, gb, src, "lore", log)


def try_nesting_grounds(state: GameState, log: list, need_tom: bool = False) -> bool:
    """'{1}, {T}: Move a counter from target permanent you control onto a
    second target permanent. Activate only as a sorcery.' Tira 1 lore de A
    (repete o capitulo atual de A) e poe em B (avanca B)."""
    ng = next((p for p in perms_named(state, "Nesting Grounds") if not p.tapped), None)
    if ng is None or not land_ability_affordable(state, ng, 1):
        return False
    sagas = sagas_in_play(state)
    dests = [p for p in sagas if lore(p) < final_chapter(p)]
    srcs = [p for p in state.battlefield if p.counters.get("lore", 0) > 0 and not p.phased_out
            and (not is_saga(p) or lore(p) < final_chapter(p))]
    best = None
    for b in dests:
        gain = lore_gain_value(state, b, 1)
        for a in srcs:
            if a.uid == b.uid:
                continue
            loss = 0 if not is_saga(a) else max(0, 2 - repeat_value(state, a))
            score = gain - loss
            if best is None or score > best[0]:
                best = (score, a, b)
    if best is None or best[0] < (5 if need_tom else 4):
        return False
    _, a, b = best
    activate_land(state, ng, 1)
    move_counters(state, a, b, "lore", 1, log, source="Nesting Grounds")
    use(state, "nesting_grounds")
    resolve_stack(state, log)
    return True


def try_resourceful_move(state: GameState, log: list) -> bool:
    """'{4}{W}: Move any number of counters from target permanent you control
    onto a second target permanent you control.' Usado pra fechar uma Saga
    no capitulo final (gatilho do Tom) tirando os lore de outra Saga."""
    if not has(state, "Resourceful Defense") or not tom_can_still_trigger(state):
        return False
    if remaining_mana(state) - state.mana_reserve < 5 or color_sources(state, "W") < 1:
        return False
    sagas = sagas_in_play(state)
    best = None
    for b in sagas:
        need = final_chapter(b) - lore(b)
        if need <= 0:
            continue
        for a in sagas:
            if a.uid == b.uid or lore(a) < need or lore(a) >= final_chapter(a):
                continue
            score = lore_gain_value(state, b, need)
            if best is None or score > best[0]:
                best = (score, a, b, need)
    if best is None or best[0] < 8:
        return False
    _, a, b, need = best
    spend_mana(state, 5)
    move_counters(state, a, b, "lore", need, log, source="Resourceful Defense ({4}{W})")
    use(state, "resourceful_activated")
    resolve_stack(state, log)
    return True


def try_force_final_chapter(state: GameState, log: list):
    """Busca ativa do gatilho do Tom no turno (linha de jogo real): se o Tom
    esta' em campo e ainda nao disparou, leva uma Saga ao capitulo final com
    o recurso mais barato disponivel."""
    for _ in range(4):
        if not tom_can_still_trigger(state):
            return
        near = [p for p in sagas_in_play(state) if final_chapter(p) - lore(p) == 1
                and chapter_value(state, eff_name(p), final_chapter(p)) >= 1]
        if near:
            b = max(near, key=lambda p: lore_gain_value(state, p, 1))
            gb = next((g for g in perms_named(state, "Goldberry, River-Daughter")
                       if not g.tapped and not sick(state, g) and g.counters.get("lore", 0) > 0
                       and g.ability_used_turn != state.turn), None)
            if gb is not None and remaining_mana(state) - state.mana_reserve >= 1 and color_sources(state, "U"):
                spend_mana(state, 1)
                gb.tapped = True
                gb.ability_used_turn = state.turn
                move_counters(state, gb, b, "lore", 1, log, source="Goldberry (Tom)")
                draw_cards(state, 1)
                use(state, "goldberry_push")
                resolve_stack(state, log)
                continue
            if try_nesting_grounds(state, log, need_tom=True):
                continue
            if "Clockspinning" in state.hand and can_pay(state, "Clockspinning"):
                cast_instant(state, "Clockspinning", log, clock_target=b, clock_mode="add")
                continue
            if "Ripples of Potential" in state.hand and can_pay(state, "Ripples of Potential"):
                cast_instant(state, "Ripples of Potential", log)
                continue
            kb = next((p for p in perms_named(state, "Karn's Bastion") if not p.tapped), None)
            if kb is not None and land_ability_affordable(state, kb, 4):
                activate_land(state, kb, 4)
                proliferate(state, log, source="Karn's Bastion")
                resolve_stack(state, log)
                continue
        if try_resourceful_move(state, log):
            continue
        if "Nexus Mentality" in state.hand and can_pay(state, "Nexus Mentality"):
            sagas = sagas_in_play(state)
            pair = None
            for b in sagas:
                need = final_chapter(b) - lore(b)
                for a in sagas:
                    if a.uid != b.uid and need > 0 and lore(a) >= need and lore(a) < final_chapter(a):
                        if pair is None or lore_gain_value(state, b, lore(a)) > pair[0]:
                            pair = (lore_gain_value(state, b, lore(a)), a, b)
            if pair and pair[0] >= 8:
                cast_instant(state, "Nexus Mentality", log, nexus_move=(pair[1], pair[2]))
                continue
        return


def try_reflection_kiki(state: GameState, log: list):
    # "{1}, {T}: Create a token that's a copy of another target nonlegendary
    # creature you control, except it has haste. Sacrifice it at the beginning
    # of the next end step."
    for rk in state.battlefield:
        if eff_name(rk) != "Reflection of Kiki-Jiki" or rk.tapped or sick(state, rk) or rk.phased_out:
            continue
        cands = [p for p in creatures(state) if p.uid != rk.uid and not is_legendary(p)
                 and eff_name(p) not in ("Reflection of Kiki-Jiki",)]
        if not cands or remaining_mana(state) - state.mana_reserve < 1:
            continue

        def score(p):
            n = eff_name(p)
            if n in SAGA_CARD_NAMES:
                return 10 + chapter_value(state, n, 1)   # copia de Summon entra no capitulo I
            return creature_power(state, p)
        tgt = max(cands, key=score)
        spend_mana(state, 1)
        rk.tapped = True
        tok = Permanent(card=eff_name(tgt) if not tgt.is_token else tgt.card, uid=new_uid(state),
                        entered_turn=state.turn, is_token=True, haste_until_eot=True, sac_at_end=True)
        state.battlefield.append(tok)
        state.tokens_created += 1
        if is_saga(tok):
            saga_enter_lore(state, tok, choose_saga_start(state, tok), log)
        if is_enchantment(tok):
            on_enchantment_enters(state, tok, log)
        on_creature_enters(state, tok, log)
        use(state, "kiki_copy")
        resolve_stack(state, log)


def try_urza_construct(state: GameState, log: list):
    # Urza's Saga II: "{2}, {T}: Create a 0/0 colorless Construct artifact
    # creature token with 'This token gets +1/+1 for each artifact you control.'"
    for us in perms_named(state, "Urza's Saga"):
        if us.urza_construct and not us.tapped and land_ability_affordable(state, us, 2):
            activate_land(state, us, 2)
            create_token(state, "Construct Token", log)
            use(state, "urza_construct")


def try_karns_bastion_value(state: GameState, log: list):
    # "{4}, {T}: Proliferate." -- so' com mana sobrando no fim da fase.
    kb = next((p for p in perms_named(state, "Karn's Bastion") if not p.tapped), None)
    if kb is None or not land_ability_affordable(state, kb, 4):
        return
    if not any(p.counters for p in state.battlefield if not p.phased_out):
        return
    activate_land(state, kb, 4)
    proliferate(state, log, source="Karn's Bastion")
    resolve_stack(state, log)


def try_ripples_value(state: GameState, log: list):
    if "Ripples of Potential" not in state.hand or not can_pay(state, "Ripples of Potential"):
        return
    if sum(1 for p in sagas_in_play(state) if lore(p) < final_chapter(p)) >= 2:
        cast_instant(state, "Ripples of Potential", log)


def try_value_removers(state: GameState, log: list):
    """Fim do turno: O'aka (compra), Scholar (Plains na mao), Power Conduit
    (+1/+1) que nao foram usados pra salvar capitulo final tiram 1 marcador
    de valor: lore de Saga cujo capitulo atual vale repetir; senao +1/+1 da
    criatura com mais marcadores (Scholar entra com o dele)."""
    for name in ("O'aka, Traveling Merchant", "Scholar of New Horizons", "Power Conduit"):
        for rem in perms_named(state, name):
            if rem.tapped or rem.ability_used_turn == state.turn:
                continue
            if is_creature(state, rem) and sick(state, rem):
                continue
            nonland_only = name == "O'aka, Traveling Merchant"
            sagas = [p for p in sagas_in_play(state) if lore(p) < final_chapter(p) and repeat_value(state, p) >= 4
                     and not (nonland_only and is_land(p))]
            if sagas:
                use_remover(state, rem, max(sagas, key=lambda p: repeat_value(state, p)), "lore", log)
                continue
            if name == "Power Conduit":
                continue   # mover +1/+1 de criatura pra criatura nao ganha nada
            withc = [p for p in creatures(state) if p.counters.get("+1/+1", 0) > 0]
            if withc:
                use_remover(state, rem, max(withc, key=lambda p: p.counters.get("+1/+1", 0)), "+1/+1", log)


def try_nexus_value(state: GameState, log: list):
    """Nexus Mentality fora da busca pelo Tom (fim do turno, instantanea):
    modo 2 -- 'Remove all counters from target nonland permanent you
    control. Draw a card for each counter removed.' Alvo: Saga cujos
    capitulos valem repetir (zerar = recomeca do I) ou o permanente com mais
    marcadores; so' com 3+ marcadores (3+ cartas). Com comandante em campo,
    o modo 1 junto move os marcadores de outra Saga pra fechar uma
    (achado real na tabela de uso: 0,6% das partidas usavam a carta)."""
    if "Nexus Mentality" not in state.hand or not can_pay(state, "Nexus Mentality"):
        return
    def removal_score(p):
        n = sum(p.counters.values())
        if is_saga(p):
            rep = sum(chapter_value(state, eff_name(p), c) for c in range(1, lore(p) + 1)) / max(1, lore(p))
            return n + (1 if rep >= 4 else 0)
        return n
    cands = [p for p in state.battlefield if not is_land(p) and not p.phased_out and sum(p.counters.values()) >= 3
             and not (is_saga(p) and lore(p) >= final_chapter(p))]
    if not cands:
        return
    c = max(cands, key=removal_score)
    move = None
    if state.commander_in_play:
        sagas = [p for p in sagas_in_play(state) if p.uid != c.uid]
        for b in sagas:
            need = final_chapter(b) - lore(b)
            for a in sagas:
                if a.uid != b.uid and need > 0 and 0 < lore(a) and lore(a) >= need and lore(a) < final_chapter(a):
                    if move is None or lore_gain_value(state, b, lore(a)) > move[0]:
                        move = (lore_gain_value(state, b, lore(a)), a, b)
    cast_instant(state, "Nexus Mentality", log, nexus_move=(move[1], move[2]) if move and move[0] >= 6 else None,
                 nexus_remove=c)


def try_hall_of_heliod_end(state: GameState, log: list):
    # "{1}{W}, {T}: Put target enchantment card from your graveyard on top of
    # your library." -- no fim do turno, se sobrou mana: compra no proximo.
    hall = next((p for p in perms_named(state, "Hall of Heliod's Generosity") if not p.tapped), None)
    gy = [c for c in state.graveyard if "enchantment" in CARD_DB[c].types]
    if hall is None or not gy or not land_ability_affordable(state, hall, 2, {"W"}):
        return
    best = max(gy, key=lambda c: tutor_priority(state, c))
    activate_land(state, hall, 2)
    state.graveyard.remove(best)
    state.library.insert(0, best)
    state.recursion_events_total += 1
    use(state, "hall_of_heliod_end")


def try_enlightened_end(state: GameState, log: list):
    if "Enlightened Tutor" in state.hand and can_pay(state, "Enlightened Tutor") and state.turn >= 3:
        cast_instant(state, "Enlightened Tutor", log)


def try_cycling(state: GameState, log: list):
    # Tríomes/SNC: "Cycling {3}" -- troca terreno sobrando por carta.
    lands_in_play = sum(1 for p in state.battlefield if is_land(p))
    for c in [c for c in state.hand if "cycling3" in CARD_DB[c].tags]:
        if lands_in_play >= 7 and remaining_mana(state) - state.mana_reserve >= 3:
            spend_mana(state, 3)
            state.hand.remove(c)
            state.graveyard.append(c)
            draw_cards(state, 1)
            use(state, "cycling")


def try_swords(state: GameState, log: list):
    if "Swords to Plowshares" in state.hand and can_pay(state, "Swords to Plowshares") and state.turn >= 3:
        cast_instant(state, "Swords to Plowshares", log)


def try_clockspinning_suspend(state: GameState, log: list):
    if state.suspended and "Clockspinning" in state.hand and can_pay(state, "Clockspinning"):
        cast_instant(state, "Clockspinning", log, clock_mode="suspend")


# ---------------------------------------------------------------------------
# Terreno
# ---------------------------------------------------------------------------

def land_enters_tapped(state: GameState, name: str) -> bool:
    tags = CARD_DB[name].tags
    if "etb_tapped" in tags:
        return True
    return False


def spendable_this_turn(state: GameState) -> int:
    """Quanto da mao (e do Tom na zona de comando) daria pra conjurar agora,
    guloso por prioridade -- usado so' pra decidir QUAL terreno jogar."""
    budget = remaining_mana(state)
    spent = 0
    if not state.commander_in_play and pips_payable(state, CARD_DB[COMMANDER].pips) \
            and budget >= effective_cost(state, COMMANDER):
        spent += effective_cost(state, COMMANDER)
        budget -= effective_cost(state, COMMANDER)
    for c in sorted([c for c in state.hand if c not in LAND_NAMES and c not in NOT_IN_CAST_LOOP],
                    key=lambda c: cast_priority(state, c)):
        cost = effective_cost(state, c)
        if cost <= budget and pips_payable(state, CARD_DB[c].pips):
            budget -= cost
            spent += cost
    return spent


def fetch_target(state: GameState, fetch: str) -> Optional[str]:
    cands = [c for c in state.library if c in LAND_NAMES and (LAND_TYPES.get(c, frozenset()) & set(FETCHES[fetch]))]
    if not cands:
        return None
    return max(cands, key=lambda c: land_option_score(state, c, from_fetch=True))


def land_option_score(state: GameState, name: str, from_fetch: bool = False) -> tuple:
    """Joga o terreno 'de mentira' e mede: (mana que da' pra gastar neste
    turno, cores que faltavam e ele traz, entra virado?). Empate de gasto ->
    prefere o que entra VIRADO (guarda o desvirado pra quando fizer falta)."""
    if name in FETCHES and not from_fetch:
        tgt = fetch_target(state, name)
        if tgt is None:
            return (-1, 0, 0, 0)
        name = tgt
    missing = {c for c in WUBRG if color_sources(state, c) == 0}
    tapped = land_enters_tapped(state, name)
    fake = Permanent(card=name, uid=-1, entered_turn=state.turn, tapped=tapped)
    state.battlefield.append(fake)
    try:
        spend = spendable_this_turn(state)
    finally:
        state.battlefield.remove(fake)
    fix = len(set(CARD_DB[name].produces) & missing)
    urza = 1 if name == "Urza's Saga" else 0
    return (spend, fix, urza, 1 if tapped else 0, len(CARD_DB[name].produces))


def play_land(state: GameState, log: list):
    if state.lands_played_this_turn >= 1:
        return
    lands = [c for c in state.hand if c in LAND_NAMES]
    if not lands:
        return
    pick = max(lands, key=lambda n: land_option_score(state, n))
    state.hand.remove(pick)
    state.lands_played_this_turn += 1
    tags = CARD_DB[pick].tags
    if "fetch" in tags:
        # "{T}, Pay 1 life, Sacrifice this land: Search your library for a X or
        # Y card, put it onto the battlefield, then shuffle." (desvirado)
        state.graveyard.append(pick)
        lose_life(state, 1)
        use(state, "fetch")
        tgt = fetch_target(state, pick)
        if tgt:
            state.library.remove(tgt)
            state.rng.shuffle(state.library)
            enter_battlefield(state, tgt, log, tapped=land_enters_tapped(state, tgt))
            resolve_stack(state, log)
        return
    enter_battlefield(state, pick, log, tapped=land_enters_tapped(state, pick))
    resolve_stack(state, log)


# ---------------------------------------------------------------------------
# Upkeep / fase principal (714.3b) / combate / fim de turno
# ---------------------------------------------------------------------------

def upkeep_step(state: GameState, log: list):
    resolve_suspended(state, log)
    # Starfield of Nyx: "At the beginning of your upkeep, you may return
    # target enchantment card from your graveyard to the battlefield."
    for _ in perms_named(state, "Starfield of Nyx"):
        gy = [c for c in state.graveyard if "enchantment" in CARD_DB[c].types and c not in LAND_NAMES
              and not (c in ("Utopia Sprawl", "Fertile Ground") and not any(is_land(p) for p in state.battlefield))]
        if gy:
            best = max(gy, key=lambda c: tutor_priority(state, c))
            state.graveyard.remove(best)
            state.recursion_events_total += 1
            if best == "Estrid's Invocation":
                enter_battlefield(state, best, log, copy_of=best_copy_target(state))
            else:
                enter_battlefield(state, best, log)
            use(state, "starfield_return")
            resolve_stack(state, log)
    # Estrid's Invocation (copia): "At the beginning of your upkeep, you may
    # exile this enchantment. If you do, return it to the battlefield under
    # its owner's control." -- volta como objeto novo, escolhe de novo o que
    # copiar (Saga recomeca do capitulo I ou do escolhido com read ahead).
    for inv in [p for p in state.battlefield if p.card == "Estrid's Invocation" and p.copy_of and not p.phased_out]:
        if is_saga(inv) and final_chapter(inv) - lore(inv) == 1 and \
                chapter_value(state, eff_name(inv), final_chapter(inv)) >= 6:
            continue   # deixa fechar o capitulo final (vale mais que recomecar)
        leave_battlefield(state, inv, log, to="exile")
        if "Estrid's Invocation" in state.exile:
            state.exile.remove("Estrid's Invocation")
        enter_battlefield(state, "Estrid's Invocation", log, copy_of=best_copy_target(state))
        use(state, "estrid_blink")
        resolve_stack(state, log)


def precombat_lore_step(state: GameState, log: list):
    """714.3b: 'As a player's precombat main phase begins, that player puts a
    lore counter on each Saga they control with one or more chapter
    abilities.' Tudo ao mesmo tempo; eu ordeno os gatilhos pra que os
    capitulos finais resolvam por ultimo."""
    sagas = sagas_in_play(state)
    sagas.sort(key=lambda p: 0 if final_chapter(p) - lore(p) == 1 else 1)
    for p in sagas:
        if final_chapter(p) > 0:
            add_counters(state, p, "lore", 1, log, source="turno (714.3b)")
    resolve_stack(state, log)


def burn_unspent_bonus(state: GameState):
    # Mana que sobra esvazia entre etapas/fases (The Bath Song III: {U}{U}).
    # Supoe que a mana bonus foi gasta primeiro: o que foi gasto dela sai do
    # gasto junto com o pool; o que sobrou dela simplesmente some.
    if state.bonus_mana_pool > 0:
        state.mana_spent_this_turn = max(0, state.mana_spent_this_turn - state.bonus_mana_pool)
        state.bonus_mana_pool = 0
        state.bonus_mana_colors = set()


def combat_step(state: GameState, log: list):
    reserved = {p.uid for p in vitality_mana_creatures(state)}
    attackers = []
    for p in creatures(state):
        name = eff_name(p)
        if p.tapped or sick(state, p) or p.uid in reserved or name in MANA_CREATURES:
            continue
        attackers.append(p)
    if not attackers:
        return
    for p in attackers:
        if "vigilance" not in eff(p).tags:
            p.tapped = True
    total = 0
    for p in attackers:
        name = eff_name(p)
        if name == "O-Kagachi Made Manifest":
            # "defending player chooses a nonland card in your graveyard. Return
            # that card to your hand. +X/+0 (X = MV)." Oponente escolhe o PIOR
            # pra mim: menor MV.
            gy = [c for c in state.graveyard if c not in LAND_NAMES]
            if gy:
                pick = min(gy, key=lambda c: CARD_DB[c].mv)
                state.graveyard.remove(pick)
                state.hand.append(pick)
                p.temp_power += CARD_DB[pick].mv
                use(state, "okagachi_return")
        if name == "Goblin Shaman Token":
            create_treasure(state, 1)   # "Whenever this token attacks, create a Treasure token."
        if name == "Galactus":
            state.interaction_plays += 1   # 📊 "destroy target land" (de oponente)
        if p.uid == state.ring_bearer_uid and state.ring_level >= 2:
            draw_cards(state, 1)          # Ring nivel 2: ataca -> compra e descarta
            discard_worst(state, 1)
    for p in attackers:
        dmg = creature_power(state, p) * (2 if state.double_strike_this_turn else 1)
        total += dmg
        if "lifelink" in eff(p).tags:
            gain_life(state, dmg)
        if p.uid == state.commander_uid:
            state.commander_damage_dealt += dmg     # CR 903.10a (por uid)
            if state.commander_damage_dealt >= 21:
                state.commander_damage_win = True
        if p.odin_lethal and dmg > 0 and state.odin_eliminations < NUM_OPPONENTS:
            state.odin_eliminations += 1           # Zantetsuken (sem bloqueio modelado)
        if p.uid == state.ring_bearer_uid and state.ring_level >= 4 and dmg > 0:
            proxy_drain(state, 3)                  # Ring nivel 4
    state.proxy_damage_total += total
    use(state, "combat_damage", total)


def end_step(state: GameState, log: list):
    try_nexus_value(state, log)
    try_value_removers(state, log)
    try_hall_of_heliod_end(state, log)
    try_enlightened_end(state, log)
    try_cycling(state, log)
    resolve_stack(state, log)
    # Tokens do Reflection of Kiki-Jiki: "Sacrifice it at the beginning of the
    # next end step." (copia de Saga com lore -> Resourceful Defense.)
    for p in [p for p in state.battlefield if p.sac_at_end]:
        leave_battlefield(state, p, log, to="graveyard", sacrificed=True)
    resolve_stack(state, log)
    # Limpeza: "ate o fim do turno" acaba; mao maxima 7.
    for p in state.battlefield:
        p.temp_power = 0
        p.haste_until_eot = False
    state.double_strike_this_turn = False
    state.fenrir_next_creature_bonus = 0
    while len(state.hand) > 7:
        discard_worst(state, 1)


def pay_pain_and_sac_tokens(state: GameState):
    # City of Brass/Mana Confluence: usadas por ultimo -- perde 1 por cada uma
    # que o gasto do turno obrigou a usar.
    pains = [p for p in state.battlefield if "pain_any" in CARD_DB[p.card].tags and is_land(p)]
    if pains:
        non_pain = total_mana(state) - len(pains) - state.treasures - state.gold_tokens
        lose_life(state, max(0, min(len(pains), state.mana_spent_this_turn - non_pain)))
    # Treasure/Gold: sacrificados so' se o gasto passou das outras fontes.
    other = total_mana(state) - state.treasures - state.gold_tokens
    over = max(0, state.mana_spent_this_turn - other)
    g = min(state.gold_tokens, over)
    state.gold_tokens -= g
    over -= g
    state.treasures = max(0, state.treasures - over)


def run_turn(state: GameState, log: list, is_last_turn: bool = False):
    state.turn += 1
    state.lands_played_this_turn = 0
    state.mana_spent_this_turn = 0
    state.bonus_mana_pool = 0
    state.bonus_mana_colors = set()
    state.tom_triggered_this_turn = False
    state.taba_iii_this_turn = 0
    state.chain_current = 0
    state.mana_reserve = 0
    # Untap (Teferi's Protection: fases voltam antes de desvirar).
    state.tp_active = False
    for p in state.battlefield:
        p.phased_out = False
        p.tapped = False

    upkeep_step(state, log)
    draw_cards(state, 1)
    state.cards_drawn_extra -= 1   # compra normal do turno nao conta como "extra"

    # Fase principal pre-combate: 714.3b primeiro, depois as acoes.
    precombat_lore_step(state, log)
    play_land(state, log)
    state.mana_by_turn.append(total_mana(state))
    try_cast_commander(state, log)
    try_cast_loop(state, log)
    try_satsuki(state, log)
    try_goldberry(state, log)
    try_reflection_kiki(state, log)
    try_force_final_chapter(state, log)
    try_nesting_grounds(state, log)
    try_suspend_resurgent(state, log)
    try_clockspinning_suspend(state, log)
    try_cast_loop(state, log)
    try_force_final_chapter(state, log)
    burn_unspent_bonus(state)

    combat_step(state, log)

    # Fase principal pos-combate.
    if state.interaction_rng is not None and "Teferi's Protection" in state.hand and state.turn >= 4:
        state.mana_reserve = 3    # segura {2}{W} aberto pros turnos dos oponentes
    try_cast_loop(state, log)
    try_ripples_value(state, log)
    try_urza_construct(state, log)
    try_karns_bastion_value(state, log)
    try_swords(state, log)
    try_cast_loop(state, log)

    end_step(state, log)
    if state.lethal_turn is None and state.proxy_damage_total >= 40 * NUM_OPPONENTS:
        state.lethal_turn = state.turn
    if state.commander_in_play and tom_protected(state):
        state.tom_protected_turns += 1
    state.tp_ready = (state.mana_reserve > 0 and "Teferi's Protection" in state.hand
                      and remaining_mana(state) >= 3 and color_sources(state, "W") >= 1)
    pay_pain_and_sac_tokens(state)


# ---------------------------------------------------------------------------
# Decklist (99 + Tom na zona de comando) -- identica a lista.md
# ---------------------------------------------------------------------------

DECKLIST_TEXT = """
1 Arcane Signet
1 Awaken the Honored Dead
1 Badlands
1 Barbara Wright
1 Battle at the Helvault
1 Bayou
1 Binding the Old Gods
1 Birth of the Imperium
1 Bloom Tender
1 City of Brass
1 Clockspinning
1 Command Tower
1 Eidolon of Blossoms
1 Elspeth Conquers Death
1 Enchantress's Presence
1 Enduring Vitality
1 Enlightened Tutor
1 Estrid's Invocation
1 Exotic Orchard
1 Fable of the Mirror-Breaker // Reflection of Kiki-Jiki
1 Faeburrow Elder
1 Farseek
1 Femeref Enchantress
1 Fertile Ground
1 Flooded Strand
1 Flux Channeler
1 Forest
1 Goldberry, River-Daughter
1 Hall of Heliod's Generosity
1 Hex Parasite
1 Historian's Boon
1 In the Darkness Bind Them
1 Indatha Triome
1 Island
1 Jugan Defends the Temple // Remnant of the Rising Star
1 Karn's Bastion
1 Ketria Triome
1 Kiora Bests the Sea God
1 Leyline Binding
1 Mana Confluence
1 Misty Rainforest
1 Mountain
1 Narci, Fable Singer
1 Nesting Grounds
1 Nexus Mentality
1 O'aka, Traveling Merchant
1 Plains
1 Plateau
1 Power Conduit
1 Prismatic Omen
1 Raugrin Triome
1 Reflecting Pool
1 Replenish
1 Resourceful Defense
1 Resurgent Belief
1 Ripples of Potential
1 Sanctum Weaver
1 Satsuki, the Living Lore
1 Savai Triome
1 Savannah
1 Scholar of New Horizons
1 Scrubland
1 Serra's Sanctum
1 Setessan Champion
1 Sol Ring
1 Song of Eärendil
1 Starfield of Nyx
1 Strionic Resonator
1 Summon: Bahamut
1 Summon: Fenrir
1 Summon: Knights of Round
1 Summon: Primal Odin
1 Summon: Yojimbo
1 Swamp
1 Swords to Plowshares
1 Sythis, Harvest's Hand
1 Taiga
1 Teferi's Protection
1 The Bath Song
1 The Coming of Galactus
1 The Creation of Avacyn
1 The Cruelty of Gix
1 The Eldest Reborn
1 The First Iroan Games
1 The Kami War // O-Kagachi Made Manifest
1 The World Tree
1 There and Back Again
1 Tropical Island
1 Tundra
1 Underground Sea
1 Urza's Saga
1 Utopia Sprawl
1 Verdant Catacombs
1 Volcanic Island
1 War of the Last Alliance
1 Weaver of Harmony
1 Windswept Heath
1 Wooded Foothills
1 Zagoth Triome
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
assert len(set(BASE_LIBRARY)) == 99, "singleton violado"
for _card_name in set(BASE_LIBRARY):
    assert _card_name in CARD_DB, f"carta na decklist sem entrada no CARD_DB: {_card_name}"


# ---------------------------------------------------------------------------
# Mulligan (1o gratis, London a partir do 2o -- convencao da biblioteca)
# ---------------------------------------------------------------------------

def should_keep(hand: list, mulligans: int) -> bool:
    lands = sum(1 for c in hand if c in LAND_NAMES)
    if mulligans >= 3:
        return True
    return 2 <= lands <= 5


def bottom_priority(card: str) -> float:
    if card in LAND_NAMES:
        return 0
    return CARD_DB[card].mv


def mulligan(state: GameState):
    mulls = 0
    while True:
        hand = state.library[:7]
        rest = state.library[7:]
        if should_keep(hand, mulls) or mulls >= 4:
            penalty = max(0, mulls - 1)
            ordered = sorted(hand, key=bottom_priority, reverse=True)
            state.hand = ordered[penalty:]
            state.library = rest + ordered[:penalty]
            state.mulligans = mulls
            return
        mulls += 1
        state.rng.shuffle(state.library)


# ---------------------------------------------------------------------------
# MODO DE RESILIENCIA (interacao de oponente) -- porte do design final dos
# outros 18 decks (7 categorias, 1 rolagem de "algum wipe" + tipo ponderado,
# gate de atencao, supressao de ataque pos-wipe). Diferencas reais deste
# deck, todas vindas do oraculo:
# - Tom com 4+ lore nas Sagas e' INDESTRUTIVEL: wipe de criatura
#   ("destroy") nao o mata (`is_indestructible`). Idem Summon: Knights of
#   Round, Avacyn e criatura com marcador de indestrutivel (Knights V).
# - Teferi's Protection reativa: se sobrou {2}{W} aberto no fim do meu turno
#   (`state.tp_ready`), a 1a remocao/wipe/ataque da rodada contra mim e'
#   anulada -- todos os meus permanentes fasam ate' o meu proximo turno e
#   minha vida nao muda.
# - Wipe de encantamento acerta Sagas, Summons, auras, Sythis etc. (e dispara
#   Femeref por encantamento que vai pro cemiterio, e Resourceful Defense
#   pelos marcadores de quem saiu).
# ---------------------------------------------------------------------------

NUM_OPPONENTS = 3
INTERACTION_SETUP_TURNS = 2


def interaction_chance(state: GameState) -> float:
    board_impact = sum(1 for p in state.battlefield if not is_land(p) and not p.phased_out)
    return min(0.10 + 0.03 * board_impact, 0.75)


OPPONENT_ATTENTION_CHANCE = 1.0 / NUM_OPPONENTS
POST_WIPE_ATTACK_HASTE_FACTOR = 0.15
BOARD_WIPE_CHANCE_FACTOR = 0.4
ARTIFACT_WIPE_CHANCE_FACTOR = 0.2
ENCHANTMENT_WIPE_CHANCE_FACTOR = 0.15
GRAVEYARD_WIPE_CHANCE_FACTOR = 0.4
GRAVEYARD_SNIPE_CHANCE_FACTOR = 0.5
COUNTERSPELL_CHANCE_FACTOR = 0.5
WIPE_TYPE_WEIGHTS = {
    "creature": BOARD_WIPE_CHANCE_FACTOR,
    "artifact": ARTIFACT_WIPE_CHANCE_FACTOR,
    "enchantment": ENCHANTMENT_WIPE_CHANCE_FACTOR,
}
TOTAL_WIPE_CHANCE_FACTOR = sum(WIPE_TYPE_WEIGHTS.values())

INTERACTION_ENGINE_PRIORITY = [
    "Resourceful Defense",
    "Narci, Fable Singer",
    "Barbara Wright",
    "Enchantress's Presence",
    "Sythis, Harvest's Hand",
    "Starfield of Nyx",
    "Satsuki, the Living Lore",
    "Strionic Resonator",
    "Estrid's Invocation",
    "Goldberry, River-Daughter",
    "Setessan Champion",
    "Eidolon of Blossoms",
    "Historian's Boon",
    "Weaver of Harmony",
    "Flux Channeler",
    "Sanctum Weaver",
]
# Curada por prioridade: so' motores RECORRENTES (a cadeia de marcadores,
# compra por encantamento, recursao, copia de gatilho). O Tom fica DE FORA
# (convencao: comandante tem a categoria de counterspell dedicada, e
# remocao pontual so' o manda pra zona de comando -- alem de ele ter
# hexproof com 4+ lore). Sagas em campo tambem ficam de fora: sao
# efemeras por construcao (se sacrificam sozinhas).

OPPONENT_ATTACKER_PROFILES = [
    ("Knight Token", 2), ("Saproling Token", 1), ("Vampire Token", 1),
    ("Zombie Token", 2), ("Soldier Token", 1), ("Goblin Token", 1),
    ("Elemental Token", 3),
]


def try_teferis_protection_response(state: GameState) -> bool:
    """Teferi's Protection de verdade: 'Until your next turn, your life total
    can't change and you gain protection from everything. All permanents you
    control phase out.' So' se o {2}{W} ficou aberto no fim do meu turno."""
    if state.tp_active:
        return True
    if not state.tp_ready or "Teferi's Protection" not in state.hand:
        return False
    state.hand.remove("Teferi's Protection")
    state.exile.append("Teferi's Protection")
    state.tp_ready = False
    state.tp_active = True
    for p in state.battlefield:
        p.phased_out = True
    state.tp_saves_total += 1
    use(state, "teferis_protection")
    return True


def try_smart_opponent_removal(state: GameState) -> Optional[str]:
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    target_name = next((n for n in INTERACTION_ENGINE_PRIORITY if has(state, n)), None)
    if target_name is None:
        return None
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    if try_teferis_protection_response(state):
        return None
    target_perm = next(p for p in state.battlefield if p.card == target_name and not p.phased_out)
    remove_permanent(state, target_perm, source="opponent_removal")
    resolve_stack(state, [])
    state.smart_removals_total += 1
    state.smart_removal_log.append((state.turn, target_name))
    return target_name


def try_smart_opponent_attack(state: GameState) -> Optional[str]:
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    chance = interaction_chance(state) * (POST_WIPE_ATTACK_HASTE_FACTOR if state.wiped_this_round else 1.0)
    if state.interaction_rng.random() >= chance:
        return None
    name, power = state.interaction_rng.choice(OPPONENT_ATTACKER_PROFILES)
    if state.tp_active:
        return None      # "your life total can't change" + protecao de tudo
    state.life -= power
    state.smart_attacks_taken_total += 1
    state.smart_attack_log.append((state.turn, name))
    return name


def try_smart_opponent_discard(state: GameState) -> Optional[str]:
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if not state.hand:
        return None
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    target = state.interaction_rng.choice(state.hand)
    state.hand.remove(target)
    state.graveyard.append(target)
    state.smart_discards_total += 1
    state.smart_discard_log.append((state.turn, target))
    return target


def try_smart_opponent_wipe(state: GameState) -> Optional[list]:
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * TOTAL_WIPE_CHANCE_FACTOR:
        return None
    candidates = {
        "creature": [p for p in state.battlefield if is_creature(state, p)],
        "artifact": [p for p in state.battlefield if is_artifact(p) and not p.phased_out],
        "enchantment": [p for p in state.battlefield if is_enchantment(p) and not p.phased_out],
    }
    available = [t for t in candidates if candidates[t]]
    if not available:
        return None
    wipe_type = state.interaction_rng.choices(available, weights=[WIPE_TYPE_WEIGHTS[t] for t in available])[0]
    if wipe_type == "creature":
        state.wiped_this_round = True    # simetrico: acerta a mesa inteira
    if try_teferis_protection_response(state):
        return None
    targets = [p for p in candidates[wipe_type] if not is_indestructible(state, p)]
    names = [p.card for p in targets]
    for p in list(targets):
        if p in state.battlefield:
            remove_permanent(state, p, source=f"opponent_{wipe_type}_wipe")
    resolve_stack(state, [])
    if wipe_type == "creature":
        state.smart_wipes_total += 1
        state.smart_wipe_log.append((state.turn, names))
    elif wipe_type == "artifact":
        state.smart_artifact_wipes_total += 1
        state.smart_artifact_wipe_log.append((state.turn, names))
    else:
        state.smart_enchantment_wipes_total += 1
        state.smart_enchantment_wipe_log.append((state.turn, names))
    return names


def try_smart_opponent_graveyard_wipe(state: GameState) -> Optional[list]:
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if state.graveyard_wipe_used or not state.graveyard:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * GRAVEYARD_WIPE_CHANCE_FACTOR:
        return None
    exiled = state.graveyard[:]
    state.graveyard.clear()
    state.graveyard_wipe_used = True
    state.smart_graveyard_wipes_total += 1
    state.smart_graveyard_wipe_log.append((state.turn, exiled))
    return exiled


def try_smart_opponent_graveyard_snipe(state: GameState) -> Optional[str]:
    """Alvo SMART deste deck: a carta de ENCANTAMENTO de maior valor no
    cemiterio (o que Starfield/Replenish/Resurgent/Hall de Heliod trariam de
    volta) -- nao so' criatura."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    candidates = [c for c in state.graveyard if "enchantment" in CARD_DB[c].types or "creature" in CARD_DB[c].types]
    if not candidates:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * GRAVEYARD_SNIPE_CHANCE_FACTOR:
        return None
    target = max(candidates, key=lambda c: tutor_priority(state, c))
    state.graveyard.remove(target)
    state.smart_graveyard_snipes_total += 1
    state.smart_graveyard_snipe_log.append((state.turn, target))
    return target


def try_smart_opponent_counter(state: GameState) -> bool:
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return False
    if state.interaction_rng.random() >= interaction_chance(state) * COUNTERSPELL_CHANCE_FACTOR:
        return False
    state.smart_counters_total += 1
    state.smart_counter_log.append(state.turn)
    return True


def try_smart_opponent_turn(state: GameState):
    if state.turn > INTERACTION_SETUP_TURNS and state.interaction_rng.random() >= OPPONENT_ATTENTION_CHANCE:
        return
    try_smart_opponent_wipe(state)
    try_smart_opponent_attack(state)
    try_smart_opponent_graveyard_wipe(state)
    try_smart_opponent_graveyard_snipe(state)
    try_smart_opponent_removal(state)
    try_smart_opponent_discard(state)


# ---------------------------------------------------------------------------
# Simulacao
# ---------------------------------------------------------------------------

def new_game(seed: int, interaction: bool = False) -> GameState:
    rnd = random.Random(seed)
    state = GameState(rng=rnd, interaction_rng=random.Random(seed + 999_999) if interaction else None)
    state.library = BASE_LIBRARY[:]
    rnd.shuffle(state.library)
    mulligan(state)
    return state


def simulate_one(seed: int, turns: int = 10) -> GameState:
    state = new_game(seed)
    log = []
    for i in range(turns):
        run_turn(state, log, is_last_turn=(i == turns - 1))
        if state.infinite_combo_turn is not None:
            break
    return state


def simulate_one_with_interaction(seed: int, turns: int = 10) -> GameState:
    state = new_game(seed, interaction=True)
    log = []
    for i in range(turns):
        run_turn(state, log, is_last_turn=(i == turns - 1))
        if state.infinite_combo_turn is not None:
            break
        state.wiped_this_round = False
        for _ in range(NUM_OPPONENTS):
            try_smart_opponent_turn(state)
    return state


def summarize(states: list, n: int, turns: int):
    def avg(fn):
        return statistics.mean(fn(s) for s in states)
    cast = [s.commander_cast_turn for s in states if s.commander_cast_turn is not None]
    print(f"Tom conjurado: {100*len(cast)/n:.1f}% | turno medio {statistics.mean(cast) if cast else 0:.2f} | "
          f"ate' T5: {100*sum(1 for t in cast if t <= 5)/n:.1f}%")
    print(f"Gatilhos do Tom (media): {avg(lambda s: s.tom_triggers):.2f} | Sagas de graca: "
          f"{avg(lambda s: s.tom_sagas_put):.2f} (MV medio somado {avg(lambda s: s.tom_sagas_mv):.1f})")
    print(f"Turnos com Tom hexproof/indestrutivel (4+ lore): {avg(lambda s: s.tom_protected_turns):.2f}")
    print(f"Sagas conjuradas: {avg(lambda s: s.sagas_cast):.2f} | capitulos resolvidos: "
          f"{avg(lambda s: s.chapters_resolved):.1f} | capitulos FINAIS: {avg(lambda s: s.final_chapters_resolved):.2f}")
    print(f"Marcadores de saber: +{avg(lambda s: s.lore_added_total):.1f} / -{avg(lambda s: s.lore_removed_total):.1f}"
          f" | marcadores MOVIDOS: {avg(lambda s: s.counters_moved_total):.2f}"
          f" | finais salvos (714.4): {avg(lambda s: s.finals_saved):.2f}")
    print(f"Resourceful Defense: gatilhos {avg(lambda s: s.resourceful_triggers):.2f} | "
          f"maior cadeia {avg(lambda s: s.resourceful_chain_max):.2f}")
    print(f"Dano proxy medio: {avg(lambda s: s.proxy_damage_total):.1f} (mediana "
          f"{statistics.median(s.proxy_damage_total for s in states):.1f}) | Narci: "
          f"{avg(lambda s: s.narci_drain_total):.1f} | Mega Flare: {avg(lambda s: s.mega_flare_total):.1f}")
    ramp = {tt: statistics.mean(s.mana_by_turn[tt - 1] for s in states if len(s.mana_by_turn) >= tt)
            for tt in (2, 3, 4, 5, 6, 8) if tt <= turns}
    print("RAMPA -- mana disponivel na fase principal 1: " + " | ".join(f"T{k} {v:.1f}" for k, v in ramp.items()))
    print(f"RECURSAO -- eventos (cemiterio -> mao/campo/topo): {avg(lambda s: s.recursion_events_total):.2f}")
    print(f"Cartas compradas extra: {avg(lambda s: s.cards_drawn_extra):.1f} | tokens: "
          f"{avg(lambda s: s.tokens_created):.1f} | treasures: {avg(lambda s: s.treasures_created_total):.1f}")
    print(f"Interacao 📊 (miraria oponente): {avg(lambda s: s.interaction_plays):.1f} | 📊 nao medivel: "
          f"{avg(lambda s: s.structural_unmeasured):.2f} | eliminacoes Odin (sem bloqueio): "
          f"{avg(lambda s: s.odin_eliminations):.2f}")
    print(f"Vida final: {avg(lambda s: s.life):.1f} | mulligans: {avg(lambda s: s.mulligans):.2f} | "
          f"dano de comandante: {avg(lambda s: s.commander_damage_dealt):.1f} "
          f"({100*sum(1 for s in states if s.commander_damage_win)/n:.1f}% com 21+)")
    ic = [s.infinite_combo_turn for s in states if s.infinite_combo_turn is not None]
    print(f"COMBO INFINITO (There and Back Again + Clockspinning/Flux + Hex Parasite): {100*len(ic)/n:.1f}% "
          f"das partidas | turno medio {statistics.mean(ic) if ic else 0:.2f}")
    lt = [s.lethal_turn for s in states if s.lethal_turn is not None]
    print(f"Dano proxy >= {40 * NUM_OPPONENTS} (letal pros {NUM_OPPONENTS} oponentes, sem bloqueio): "
          f"{100*len(lt)/n:.1f}% das partidas | turno medio {statistics.mean(lt) if lt else 0:.2f}")
    print(f"Biblioteca esgotada: {sum(1 for s in states if s.library_emptied)}/{n}")


def run_batch(n: int, seed_base: int = 1_000_000, turns: int = 10, out_path: str = None):
    results = []
    exceptions = 0
    for i in range(n):
        try:
            results.append(simulate_one(seed_base + i, turns=turns))
        except Exception as e:
            exceptions += 1
            if exceptions <= 5:
                import traceback
                print(f"EXCEPTION seed={seed_base + i}: {e!r}")
                traceback.print_exc()
    print(f"Rodadas: {n}, excecoes: {exceptions}, turnos: {turns}, seed_base: {seed_base}")
    if results:
        summarize(results, len(results), turns)
    if out_path and results:
        with open(out_path, "w") as f:
            for s in results:
                f.write(json.dumps({
                    "tom_cast_turn": s.commander_cast_turn, "tom_triggers": s.tom_triggers,
                    "tom_sagas_put": s.tom_sagas_put, "tom_protected_turns": s.tom_protected_turns,
                    "sagas_cast": s.sagas_cast, "chapters_resolved": s.chapters_resolved,
                    "final_chapters_resolved": s.final_chapters_resolved,
                    "lore_added_total": s.lore_added_total, "lore_removed_total": s.lore_removed_total,
                    "counters_moved_total": s.counters_moved_total, "finals_saved": s.finals_saved,
                    "resourceful_chain_max": s.resourceful_chain_max,
                    "proxy_damage_total": s.proxy_damage_total, "cards_drawn_extra": s.cards_drawn_extra,
                    "interaction_plays": s.interaction_plays, "life": s.life, "mulligans": s.mulligans,
                    "lethal_turn": s.lethal_turn, "recursion_events_total": s.recursion_events_total,
                    "mana_by_turn": s.mana_by_turn, "infinite_combo_turn": s.infinite_combo_turn,
                }) + "\n")
    return results


def run_batch_with_interaction(n: int = 2000, turns: int = 10, seed_base: int = 6_000_000):
    states = []
    exceptions = 0
    for i in range(n):
        try:
            states.append(simulate_one_with_interaction(seed_base + i, turns=turns))
        except Exception as e:
            exceptions += 1
            if exceptions <= 5:
                import traceback
                print(f"EXCEPTION seed={seed_base + i}: {e!r}")
                traceback.print_exc()

    def avg(vals):
        return sum(vals) / len(vals) if vals else 0.0

    print(f"n={n}, seed_base={seed_base}, turns={turns}, excecoes={exceptions} (MODO RESILIENCIA)")
    print(f"Avg counterspells sofridos (so' no Tom): {avg([s.smart_counters_total for s in states]):.2f}")
    cast = [s.commander_cast_turn for s in states if s.commander_cast_turn is not None]
    print(f"  -- Turno medio de conjuracao do Tom que resolveu: {avg(cast):.2f} | nunca resolveu: "
          f"{100*(len(states)-len(cast))/max(1, len(states)):.1f}%")
    print(f"Avg commander_cast_count (recasts pagando CR 903.8): {avg([s.commander_cast_count for s in states]):.2f}")
    print(f"Avg wipes sofridos -- criatura {avg([s.smart_wipes_total for s in states]):.2f} | artefato "
          f"{avg([s.smart_artifact_wipes_total for s in states]):.2f} | encantamento "
          f"{avg([s.smart_enchantment_wipes_total for s in states]):.2f}")
    print(f"Teferi's Protection usada (anulou wipe/remocao/ataque): {avg([s.tp_saves_total for s in states]):.2f}")
    print(f"Avg remocoes {avg([s.smart_removals_total for s in states]):.2f} | ataques "
          f"{avg([s.smart_attacks_taken_total for s in states]):.2f} | descartes "
          f"{avg([s.smart_discards_total for s in states]):.2f} | snipes de cemiterio "
          f"{avg([s.smart_graveyard_snipes_total for s in states]):.2f}")
    ic = [s.infinite_combo_turn for s in states if s.infinite_combo_turn is not None]
    print(f"Combo infinito (Smaug): {100*len(ic)/max(1, len(states)):.1f}% | turno medio {avg(ic):.2f}")
    print(f"Avg gatilhos do Tom: {avg([s.tom_triggers for s in states]):.2f} | capitulos finais: "
          f"{avg([s.final_chapters_resolved for s in states]):.2f} | dano proxy: "
          f"{avg([s.proxy_damage_total for s in states]):.1f} | vida final: {avg([s.life for s in states]):.1f}")
    # Conta o Tom mesmo fora de fase (Teferi's Protection): fase-out nao tira
    # do campo (702.26), entao `has()` (que ignora fase-out) nao serve aqui.
    on_bf = lambda st: any(p.card == COMMANDER for p in st.battlefield)
    stuck = sum(1 for s in states if s.commander_in_play and not on_bf(s))
    ghost = sum(1 for s in states if not s.commander_in_play and on_bf(s))
    print(f"Consistencia do comandante: stuck={stuck} ghost={ghost}")
    return states


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tom_v1_runs.jsonl")
    run_batch(3000, seed_base=1_000_000, turns=8, out_path=out)
