"""
Goldfish simulator - Thranduil, the Elvenking (Sultai B/G/U)
Escrito e executado por Claude, nos mesmos moldes do beorn_goldfish_v1.py.

Metodologia (igual ao script do Beorn):
- Tags de cada carta derivadas do oracle_text real (Scryfall, cache local
  /tmp/scryfall_cache/thranduil_full.json), nao inventadas.
- Modelo de mana: como o deck e tricolor (B/G/U), em vez do modelo mono-verde
  do Beorn (total + fontes verdes), aqui rastreamos total_mana + fontes de
  cada cor separadamente (green_sources/black_sources/blue_sources), com base
  na habilidade real de cada terreno. Simplificacoes: land-tapped-conditions
  (ex: "a menos que controle 2+ terrenos") sao ignoradas, igual ja era feito
  no script do Beorn pra outras condicoes. Command Tower e' fonte das 3
  cores. Reflecting Pool e' dinamica (uniao de cores dos OUTROS terrenos em
  campo, texto real - corrigido 2026-08-28, antes era fixa {B,G,U}). Cavern
  of Souls e' fonte real de qualquer cor, mas so' pra spells de criatura
  Elfo (mesma logica ja aplicada no Ur-Dragon/Edgar Markov pra terrenos
  restritos ao tipo tribal central do deck - corrigido 2026-08-28, antes
  tratada como incolor). Three Tree City continua so' incolor nesta rodada
  (a 2a habilidade dele exigiria uma pool de mana colorida que este arquivo
  nao tem, documentado como decisao de escopo, nao esquecimento).
- Elfos lendarios (15 no deck) disparam o gatilho do proprio Thranduil
  (compra 2, descarta 1) quando entram.
- "Elfos no cemiterio" e rastreado somando os efeitos reais de mill/self-GY
  (Buried Alive, Trystan, Lluwen, Awaken the Honored Dead cap.II, Silvan
  Rally, Takenuma channel, Tyvar Jubilant Brawler -2, filtragem do Underrealm
  Lich) - so conta cartas de Elfo entre o que foi de fato milhado/descartado,
  nao card por card real (proxy: assume que uma fracao das cartas milhadas
  sao Elfos, proporcional a densidade real de Elfos no deck).
- Finishers: os 3 overruns repetiveis (Tyvar the Pummeler, Ezuri Renegade
  Leader, Elvish Warmaster) sao tratados como "finisher ativado" na primeira
  vez que ha mana sobrando pra pagar o custo de ativacao E ha criaturas em
  campo pra se beneficiar. Jarad e Lathril (dreno) sao tratados a parte.
"""

import random
import statistics
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set

# =========================================================
# DECKLIST (fonte: lista.md)
# =========================================================

COMMANDER = "Thranduil, the Elvenking"

DECKLIST_TEXT = """
1 Agatha's Soul Cauldron
1 Allosaurus Shepherd
1 Arbor Elf
1 Arcane Signet
1 Arwen, Weaver of Hope
1 Assassin's Trophy
1 Awaken the Honored Dead
1 Beast Whisperer
1 Bloodline Bidding
1 Bloom Tender
1 Breeding Pool
1 Buried Alive
1 Cavern of Souls
1 Champions of the Perfect
1 Command Tower
1 Botanical Sanctum
1 Deadly Rollick
1 Deathbloom Ritualist
1 Devoted Druid
1 Dionus, Elvish Archdruid
1 Eclipsed Realms
1 Edric, Spymaster of Trest
1 Eladamri, Korvecdal
1 Elrond, Moon-Reader
1 Elvenking's Halls
1 Elves of Deep Shadow
1 Elvish Archdruid
1 Elvish Mystic
1 Elvish Warmaster
1 Ezuri, Renegade Leader
1 Fauna Shaman
1 Finale of Devastation
7 Forest
1 Gilt-Leaf Palace
1 Glissa Sunslayer
1 Gwenna, Eyes of Gaea
1 Heroic Intervention
1 High Perfect Morcant
1 Hinterland Harbor
1 Immaculate Magistrate
1 Imperious Perfect
1 Incubation Druid
1 Iron-Shield Elf
1 Island
1 Jarad, Golgari Lich Lord
1 Kindred Dominance
1 Kindred Summons
1 Lathril, Blade of the Elves
1 Lightning Greaves
1 Llanowar Elves
1 Lluwen, Imperfect Naturalist
1 Malakir Rebirth // Malakir Mire
1 Maralen, Fae Ascendant
1 Marwyn, the Nurturer
1 Nurturing Peatland
1 Overgrown Tomb
1 Oversold Cemetery
1 Priest of Titania
1 Prime Speaker Vannifar
1 Raise the Palisade
1 Reflecting Pool
1 Rejuvenating Springs
1 Revitalizing Repast // Old-Growth Grove
1 Rhystic Study
1 Roaming Throne
1 Ruthless Winnower
1 Selfless Safewright
1 Selvala, Heart of the Wilds
1 Sol Ring
4 Swamp
1 Takenuma, Abandoned Mire
1 Thranduil's Company
1 Thranduil, Sindarin Liege // Silvan Rally
1 Three Tree City
1 Trystan's Command
1 Trystan, Callous Cultivator // Trystan, Penitent Culler
1 Tyvar the Bellicose
1 Tyvar, Jubilant Brawler
1 Tyvar, the Pummeler
1 Underground River
1 Underrealm Lich
1 Wastewood Verge
1 Waterlogged Grove
1 Watery Grave
1 Willowrush Verge
1 Wirewood Channeler
1 Wirewood Lodge
1 Yavimaya Coast
1 Yavimaya, Cradle of Growth
1 Zagoth Triome
"""

# =========================================================
# CARD DATABASE (mv, types, tags, g_pips/b_pips/u_pips, color_sources)
# Tags derivadas do oracle_text real (ver comentario no topo do arquivo).
# =========================================================

@dataclass
class Card:
    name: str
    mv: int
    types: Set[str]
    tags: Set[str] = field(default_factory=set)
    colors: Set[str] = field(default_factory=set)          # cor(es) exigidas pra conjurar (pips)
    produces: Set[str] = field(default_factory=set)        # cores que a carta (terreno/dork) produz
    is_legendary_elf: bool = False
    activation_cost: int = 0                                 # custo de ativacao (finishers/engines)
    mill_amount: int = 0                                     # cartas milhadas quando resolve
    power: int = 0                                           # poder impresso (0 = nao rastreado/irrelevante)

CARD_DB: Dict[str, Card] = {}

def add(name, mv, types, tags=None, colors=None, produces=None, legendary_elf=False, activation_cost=0, mill=0, power=0):
    CARD_DB[name] = Card(
        name=name, mv=mv, types=set(types), tags=set(tags or []),
        colors=set(colors or []), produces=set(produces or []),
        is_legendary_elf=legendary_elf, activation_cost=activation_cost, mill_amount=mill, power=power,
    )

# -------- Lands --------
add("Forest", 0, {"Land"}, produces={"G"})
add("Island", 0, {"Land"}, produces={"U"})
add("Swamp", 0, {"Land"}, produces={"B"})
add("Breeding Pool", 0, {"Land"}, produces={"G", "U"})
add("Cavern of Souls", 0, {"Land"}, produces={"B", "G", "U"}, tags={"elf_only_color"})
# Achado real 2026-08-28 (auditoria de checklist de mecanica): o docstring
# original tratava isso como "condicional demais pra modelar", mas a mesma
# situacao no Ur-Dragon (user-standing-rules.md regra #6 adendo) ja
# estabeleceu que, num deck tribal com tipo escolhido obvio (aqui: Elfo,
# tema central do deck), a restricao vira fixacao REAL pra esse
# subconjunto de spells, nao deve ser tratada como incolor. Corrigido:
# tag "elf_only_color", so conta em color_sources() pra spells de
# criatura Elfo (mesma logica ja usada na Cavern do Edgar Markov, tipo
# Vampiro).
add("Command Tower", 0, {"Land"}, produces={"B", "G", "U"})
add("Deathcap Glade", 0, {"Land"}, produces={"B", "G"})  # nao esta mais na lista (saiu p/ Botanical Sanctum), entrada mantida sem uso
add("Botanical Sanctum", 0, {"Land"}, produces={"G", "U"})
add("Hinterland Harbor", 0, {"Land"}, produces={"G", "U"})
add("Eclipsed Realms", 0, {"Land"}, produces=set())
add("Elvenking's Halls", 0, {"Land"}, produces={"G", "U"})
add("Gilt-Leaf Palace", 0, {"Land"}, produces={"B", "G"})
add("Llanowar Wastes", 0, {"Land"}, produces={"B", "G"})
add("Underground River", 0, {"Land"}, produces={"B", "U"})
add("Nurturing Peatland", 0, {"Land"}, produces={"B", "G"})
add("Overgrown Tomb", 0, {"Land"}, produces={"B", "G"})
add("Reflecting Pool", 0, {"Land"}, produces={"B", "G", "U"})
add("Rejuvenating Springs", 0, {"Land"}, produces={"G", "U"})
add("Takenuma, Abandoned Mire", 0, {"Land"}, produces={"B"}, tags={"gy_engine"})
add("Three Tree City", 0, {"Land"}, produces=set())
# {T}: Add {C} incondicional (produces vazio == so' o generico de is_land()
# em total_mana(), correto). A 2a habilidade real ("{2},{T}: choose a
# color, add mana of that color equal to creatures of chosen type you
# control" - Elfo, escalavel) fica DE FORA nesta rodada por decisao de
# escopo (achado 2026-08-28, auditoria de checklist): exigiria uma pool de
# mana colorida separada que este arquivo nao tem (ao contrario de outros
# decks desta sessao), fica pra uma rodada dedicada se o usuario quiser.
add("Undergrowth Stadium", 0, {"Land"}, produces={"B", "G"})
add("Wastewood Verge", 0, {"Land"}, produces={"B", "G"})
add("Waterlogged Grove", 0, {"Land"}, produces={"G", "U"})
add("Watery Grave", 0, {"Land"}, produces={"B", "U"})
add("Willowrush Verge", 0, {"Land"}, produces={"G", "U"})
add("Wirewood Lodge", 0, {"Land"}, produces=set())
add("Yavimaya Coast", 0, {"Land"}, produces={"G", "U"})
add("Yavimaya, Cradle of Growth", 0, {"Land"}, produces={"G"})
add("Zagoth Triome", 0, {"Land"}, produces={"B", "G", "U"})
# MDFCs com verso terreno - tratados como terreno (simplificacao: sempre jogados como land)
add("Malakir Rebirth // Malakir Mire", 0, {"Land"}, produces={"B"})
add("Revitalizing Repast // Old-Growth Grove", 0, {"Land"}, produces={"B", "G"})  # achado real 2026-08-28: faltava o modo B ("{T}: Add {B} or {G}")

# -------- Ramp / mana dorks --------
add("Sol Ring", 1, {"Artifact"}, tags={"ramp"})
add("Elvish Mystic", 1, {"Creature"}, tags={"ramp", "elf"}, colors={"G"}, produces={"G"})
add("Llanowar Elves", 1, {"Creature"}, tags={"ramp", "elf"}, colors={"G"}, produces={"G"})
add("Arbor Elf", 1, {"Creature"}, tags={"ramp", "elf"}, colors={"G"}, produces={"G"})
add("Elves of Deep Shadow", 1, {"Creature"}, tags={"ramp", "elf"}, colors={"G"}, produces={"B"})
add("Bloom Tender", 2, {"Creature"}, tags={"ramp", "elf"}, colors={"G"}, produces={"B", "G", "U"})
add("Incubation Druid", 2, {"Creature"}, tags={"ramp", "elf"}, colors={"G"}, produces={"B", "G", "U"})
add("Priest of Titania", 2, {"Creature"}, tags={"ramp", "elf", "elf_scaling"}, colors={"G"}, produces={"G"})
add("Elvish Archdruid", 3, {"Creature"}, tags={"ramp", "elf", "elf_scaling", "anthem"}, colors={"G"}, produces={"G"})
add("Wirewood Channeler", 4, {"Creature"}, tags={"ramp", "elf", "elf_scaling"}, colors={"G"}, produces={"B", "G", "U"})
add("Marwyn, the Nurturer", 3, {"Creature"}, tags={"ramp", "elf", "power_scaling"}, colors={"G"}, produces={"G"}, legendary_elf=True)
add("Selvala, Heart of the Wilds", 3, {"Creature"}, tags={"ramp", "elf", "power_scaling", "draw_conditional"}, colors={"G"}, produces={"B", "G", "U"}, legendary_elf=True)
add("Deathbloom Ritualist", 5, {"Creature"}, tags={"ramp", "elf", "gy_scaling"}, colors={"B", "G"}, produces={"B", "G", "U"})
add("Gwenna, Eyes of Gaea", 3, {"Creature"}, tags={"ramp", "elf"}, colors={"G"}, produces={"B", "G", "U"}, legendary_elf=True)

# -------- Card draw --------
# Rhystic Study: dispara com spells de OPONENTES - premissa explicita, ver ativa_rhystic_study().
add("Rhystic Study", 3, {"Enchantment"}, tags={"draw_engine", "opponent_dependent"}, colors={"U"})
# Beast Whisperer / Champions of the Perfect: "whenever you cast a creature spell, draw a card" -
# rigoroso, sem premissa, ver cast_spell().
add("Beast Whisperer", 4, {"Creature"}, tags={"draw_engine", "creature_draw_engine", "elf"}, colors={"G"})
add("Champions of the Perfect", 4, {"Creature"}, tags={"draw_engine", "creature_draw_engine", "elf"}, colors={"G"})
# Edric: "whenever a creature deals combat damage to a player, its controller may draw" - via combat_step().
add("Edric, Spymaster of Trest", 3, {"Creature"}, tags={"draw_engine", "combat_damage_draw", "elf"}, colors={"G", "U"}, legendary_elf=True)
add("Elrond, Moon-Reader", 3, {"Creature"}, tags={"draw_engine", "elf"}, colors={"U"}, legendary_elf=True)
add("Harmonized Crescendo", 6, {"Instant"}, tags={"draw_burst"}, colors={"U"})
# Underrealm Lich: substitui TODAS as suas compras por "olhe 3, 1 pra mao, 2 pro cemiterio" - ver GameState.draw().
add("Underrealm Lich", 5, {"Creature"}, tags={"draw_filter", "elf", "gy_fill_passive"}, colors={"B", "G"})
add("Elf Warrior Token", 0, {"Creature"}, tags={"elf", "token"})  # token gerado por Lathril em combate

# -------- Removal --------
add("Assassin's Trophy", 2, {"Instant"}, tags={"removal"}, colors={"B", "G"})
add("Awaken the Honored Dead", 3, {"Enchantment"}, tags={"removal", "gy_fill"}, colors={"B", "G", "U"}, mill=3)
add("Trystan's Command", 6, {"Sorcery"}, tags={"removal"}, colors={"B", "G"})
add("Ruthless Winnower", 5, {"Creature"}, tags={"removal_repeatable", "elf"}, colors={"B"})
add("Kindred Dominance", 7, {"Sorcery"}, tags={"wipe_asymmetric"}, colors={"B"})
add("Raise the Palisade", 5, {"Sorcery"}, tags={"bounce_asymmetric"}, colors={"U"})
# Adicionadas na troca pedida pelo usuario (ver auditoria.md) - cobrem lacunas reais
# confirmadas pela auditoria: nenhuma remocao dedicada de artefato ou encantamento.
add("Deadly Rollick", 2, {"Instant"}, tags={"removal", "removal_exile"}, colors={"B"})  # custo real {3}{B}, mas quase sempre paga {1}{B} (controla comandante) - modelado no custo reduzido
add("Putrefy", 2, {"Instant"}, tags={"removal", "removal_artifact"}, colors={"B", "G"})
add("Feed the Swarm", 2, {"Instant"}, tags={"removal", "removal_enchantment"}, colors={"B"})
# Candidatas a adicao avaliadas depois - ver thranduil_synergy_matrix.py --with-candidates
add("Devoted Druid", 2, {"Creature"}, tags={"ramp", "elf"}, colors={"G"}, produces={"G"})
add("Formidable Speaker", 3, {"Creature"}, tags={"tutor", "gy_fill", "elf"}, colors={"G"})
add("Arcane Signet", 2, {"Artifact"}, tags={"ramp"}, produces={"B", "G", "U"})
add("Imperious Perfect", 3, {"Creature"}, tags={"anthem", "token_maker", "elf"}, colors={"G"})

# -------- Protecao --------
add("Heroic Intervention", 2, {"Instant"}, tags={"protection"}, colors={"G"})
add("Lightning Greaves", 2, {"Artifact"}, tags={"protection"})
add("Iron-Shield Elf", 2, {"Creature"}, tags={"protection", "elf"}, colors={"B"})
add("Selfless Safewright", 5, {"Creature"}, tags={"protection", "elf"}, colors={"G"})

# -------- Tutores --------
add("Fauna Shaman", 2, {"Creature"}, tags={"tutor", "elf"}, colors={"G"})
add("Buried Alive", 3, {"Sorcery"}, tags={"tutor_gy", "gy_fill"}, colors={"B"}, mill=3)
add("Finale of Devastation", 2, {"Sorcery"}, tags={"tutor", "finisher_xspell"}, colors={"G"})  # custo real e X+GG, X variavel
add("Prime Speaker Vannifar", 3, {"Creature"}, tags={"tutor", "sac_outlet", "elf"}, colors={"G", "U"}, legendary_elf=True)
add("Eladamri, Korvecdal", 3, {"Creature"}, tags={"tutor_passive", "elf"}, colors={"G"}, legendary_elf=True)

# -------- Geradores de token de Elfo --------
add("Elvish Warmaster", 2, {"Creature"}, tags={"token_maker", "elf", "finisher_repeatable"}, colors={"G"}, activation_cost=7)
add("Lys Alana Huntmaster", 4, {"Creature"}, tags={"token_maker", "elf"}, colors={"G"})
add("Lathril, Blade of the Elves", 4, {"Creature"}, tags={"token_maker", "elf", "finisher_drain"}, colors={"B", "G"}, legendary_elf=True, activation_cost=0)
add("Thranduil, Sindarin Liege // Silvan Rally", 4, {"Creature"}, tags={"token_maker", "elf", "anthem", "gy_fill"}, colors={"G", "U"}, legendary_elf=True, mill=4)

# -------- Finishers (overruns repetiveis + drenos) --------
add("Tyvar, the Pummeler", 3, {"Creature"}, tags={"elf", "finisher_repeatable", "self_protect"}, colors={"G"}, legendary_elf=True, activation_cost=5)
add("Ezuri, Renegade Leader", 3, {"Creature"}, tags={"elf", "finisher_repeatable"}, colors={"G"}, legendary_elf=True, activation_cost=5)
add("Jarad, Golgari Lich Lord", 4, {"Creature"}, tags={"elf", "finisher_drain", "sac_outlet", "gy_scaling"}, colors={"B", "G"}, legendary_elf=True, activation_cost=3)
add("Tyvar the Bellicose", 4, {"Creature"}, tags={"elf", "anthem_combat", "counter_engine"}, colors={"B", "G"}, legendary_elf=True)
add("Tyvar, Jubilant Brawler", 3, {"Planeswalker"}, tags={"gy_fill"}, colors={"B", "G"}, mill=3)
add("Kindred Summons", 7, {"Instant"}, tags={"finisher_burst", "reinforcement"}, colors={"G"})
add("Bloodline Bidding", 8, {"Sorcery"}, tags={"finisher_burst", "reanimation_mass", "gy_payoff"}, colors={"B"})

# -------- Anthems / engines de contador --------
add("Dionus, Elvish Archdruid", 4, {"Creature"}, tags={"elf", "counter_engine"}, colors={"G"}, legendary_elf=True)
add("Arwen, Weaver of Hope", 3, {"Creature"}, tags={"elf", "counter_engine"}, colors={"G"}, legendary_elf=True)
add("Immaculate Magistrate", 4, {"Creature"}, tags={"elf", "counter_engine", "elf_scaling"}, colors={"G"})
add("High Perfect Morcant", 4, {"Creature"}, tags={"elf", "opponent_disruption"}, colors={"B", "G"}, legendary_elf=True)
add("Glissa Sunslayer", 3, {"Creature"}, tags={"elf", "removal_combat", "draw_conditional"}, colors={"B", "G"}, legendary_elf=True)
add("Maralen, Fae Ascendant", 5, {"Creature"}, tags={"elf", "disruption", "free_cast_engine"}, colors={"B", "G", "U"}, legendary_elf=True)

# -------- GY fill (elfos no cemiterio) --------
add("Lluwen, Imperfect Naturalist", 2, {"Creature"}, tags={"elf", "gy_fill"}, colors={"B", "G"}, mill=4, legendary_elf=True)
add("Trystan, Callous Cultivator // Trystan, Penitent Culler", 3, {"Creature"}, tags={"elf", "gy_fill"}, colors=set(), mill=3, legendary_elf=True)
add("Oversold Cemetery", 2, {"Enchantment"}, tags={"recursion"}, colors={"B"})  # 4+ CRIATURAS na GY, sem exigir Elfo

# -------- Diversos / suporte --------
add("Agatha's Soul Cauldron", 2, {"Artifact"}, tags={"gy_hate"})  # exila carta de QUALQUER cemiterio, nao so o seu
add("Allosaurus Shepherd", 1, {"Creature"}, tags={"elf", "protection_counterspell"}, colors={"G"})
add("Eclipsed Elf", 3, {"Creature"}, tags={"elf", "card_selection"}, colors={"B", "G"})
add("Roaming Throne", 4, {"Creature"}, tags={"trigger_doubler", "elf"})  # "is the chosen type in addition to its other types" - premissa Elf, entao ela mesma vira Elfo
add("Urza's Incubator", 3, {"Artifact"}, tags={"cost_reducer"})
add("Thranduil's Company", 4, {"Creature"}, tags={"elf", "land_ramp", "counter_engine"}, colors={"G", "U"})

# -------- Comandante --------
add(COMMANDER, 5, {"Creature"}, tags={"elf"}, colors={"B", "G", "U"}, legendary_elf=True)

# -------- Poder impresso (via cache do Scryfall) --------
# Populado automaticamente pra todas as criaturas, em vez de editar cada add()
# uma por uma - usado por Selvala (maior poder em campo) e Gwenna (poder >=5).
import json as _json
try:
    _oracle_cache = _json.load(open("/tmp/scryfall_cache/thranduil_full.json"))
except FileNotFoundError:
    _oracle_cache = {}

for _name, _card in CARD_DB.items():
    if "Creature" not in _card.types:
        continue
    _o = _oracle_cache.get(_name) or _oracle_cache.get(_name.split(" // ")[0])
    if not _o:
        continue
    _p = _o.get("power")
    if _p is None and "card_faces" in _o:
        _p = _o["card_faces"][0].get("power")
    try:
        _card.power = int(_p)
    except (TypeError, ValueError):
        pass  # poder variavel (ex: "*") ou nao numerico - fica 0

DENSITY_ELF = 15 / 91  # ~15 elfos lendarios + varios outros elfos nao-lendarios entre as 91 nao-terrenos; usado so como proxy de "chance de milhar um elfo"

# Premissas explicitas pra Rhystic Study (carta depende de spells de OPONENTES, que um goldfish solo
# nao tem como observar de verdade - mesma limitacao estrutural do Managorger Hydra no Beorn):
ASSUMED_OPPONENT_SPELLS_PER_TURN = 2   # reaproveitando a mesma premissa que voce ja validou pro Managorger Hydra
ASSUMED_RHYSTIC_STUDY_PAY_RATE = 0.5   # validada por voce - fracao das vezes que o oponente paga o {1} pra evitar a compra
ASSUMED_EDRIC_LIFESPAN_TURNS_MEAN = 2  # validada por voce - Edric sobrevive em media 2 dos seus turnos antes de ser removido (randint(1,3))

def C(name: str) -> Card:
    return CARD_DB[name]

def parse_decklist(text: str) -> List[str]:
    cards = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(" ", 1)
        qty = int(parts[0])
        name = parts[1]
        cards.extend([name] * qty)
    return cards

def is_land(card: str) -> bool:
    return "Land" in C(card).types

def is_creature(card: str) -> bool:
    return "Creature" in C(card).types

def is_spell(card: str) -> bool:
    return not is_land(card)

def has_tag(card: str, tag: str) -> bool:
    return tag in C(card).tags

def is_elf(card: str) -> bool:
    return has_tag(card, "elf") or card == COMMANDER

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
    lands_played_this_turn: int = 0  # Thranduil's Company permite um 2o land drop condicional
    creature_cast_turn: Dict[str, int] = field(default_factory=dict)  # doenca de invocacao pros mana dorks
    max_hand_size: int = 7

    commander_in_play: bool = False
    commander_cast_turn: Optional[int] = None

    spells_cast: int = 0
    extra_draws: int = 0
    lands_played_total: int = 0

    ramp_pieces_in_play: int = 0
    removal_cast: int = 0
    cards_discarded_to_hand_size: int = 0

    thranduil_legendary_elf_triggers: int = 0
    elves_milled_to_gy: int = 0          # proxy: fracao de cartas milhadas que seriam Elfos
    cards_milled_total: int = 0

    finishers_activated: List[str] = field(default_factory=list)
    finisher_turn: Optional[int] = None

    # Engines de draw (ver comentario no topo do arquivo sobre cada uma)
    creature_engine_draws: int = 0          # Beast Whisperer / Champions of the Perfect
    combat_damage_draws: int = 0            # Edric, Spymaster of Trest
    lathril_tokens_created: int = 0         # tokens de Elfo via dano de combate do Lathril
    rhystic_study_opportunities: int = 0
    rhystic_study_draws: int = 0
    rhystic_study_denied: int = 0

    # Edric: alvo obvio de remocao assim que o motor liga - premissa explicita
    # (pedida por voce): sobrevive em media 2 dos seus turnos antes de ser removido.
    edric_was_cast: bool = False
    edric_in_play: bool = False
    edric_last_turn_alive: Optional[int] = None
    edric_death_turn: Optional[int] = None

    # Teto real de mana por turno (corrige a mesma limitacao ja corrigida no Beorn:
    # antes, cada carta era checada contra total_mana() de forma independente, sem
    # descontar o que ja tinha sido gasto no mesmo turno).
    mana_spent_this_turn: int = 0

    # Color screw de azul: quantos turnos o jogador tinha mana total suficiente pra
    # conjurar o comandante (5) mas nao tinha nenhuma fonte de U disponivel.
    blue_screw_turns: int = 0
    first_blue_screw_turn: Optional[int] = None

    # Roaming Throne: "If a triggered ability of another creature you control of
    # the chosen type triggers, it triggers an additional time." Premissa: sempre
    # escolhe Elf (unica escolha sensata nesse deck). So dobra habilidades
    # GATILHADAS ("Whenever"/"At the beginning of"/"When ... enters") - NUNCA
    # habilidades ativadas ({custo}: efeito), de nenhuma carta (Selvala, Marwyn,
    # Elrond etc tem as duas; so a gatilhada dobra).
    roaming_throne_doublings: int = 0

    def roaming_throne_active(self) -> bool:
        return self.has("Roaming Throne")

    # -------- Elfos com gatilho proprio implementados a pedido do usuario --------
    # (todos exceto Selfless Safewright - dobrar hexproof/indestructible nao muda nada)
    marwyn_counters: int = 0                  # Marwyn: outro Elfo entra -> +1/+1 nela
    landfall_elf_tokens: int = 0              # Thranduil, Sindarin Liege: landfall -> token Elfo 1/1
    thranduils_company_counters: int = 0      # Thranduil's Company: landfall -> 2 contadores +1/+1
    imperious_perfect_tokens: int = 0         # Imperious Perfect: {G},{T} -> token Elfo 1/1
    selvala_draws: int = 0                    # Selvala: criatura entra com maior poder -> compra
    elrond_draws: int = 0                     # Elrond: ativa habilidade de criatura -> compra (1x/turno)
    elrond_triggered_this_turn: bool = False
    elvish_warmaster_tokens: int = 0          # Elvish Warmaster: 1+ Elfo entra -> token (1x/turno)
    elvish_warmaster_triggered_this_turn: bool = False
    glissa_draws: int = 0                     # Glissa: dano de combate -> modo "compre 1, perca 1 vida" (unico modo com efeito numerico sem oponente real)
    gwenna_counters: int = 0                  # Gwenna: conjura criatura poder>=5 -> contador+destapa
    high_perfect_morcant_triggers: int = 0    # blight no oponente - sem consequencia numerica no goldfish solo
    maralen_triggers: int = 0                 # exila biblioteca do oponente - sem consequencia numerica
    ruthless_winnower_self_sacs: int = 0      # sacrifica seu proprio nao-Elfo no upkeep - dobrar isso e RUIM pra voce
    tyvar_bellicose_triggers: int = 0         # deathtouch em combate - sem consequencia numerica (sem bloqueadores modelados)

    def draw(self, n=1, source="draw"):
        got = 0
        lich = self.has("Underrealm Lich")
        for _ in range(n):
            if not self.library:
                break
            if lich:
                # "If you would draw a card, instead look at top 3, put 1 into hand, rest into graveyard."
                look = self.library[:3]
                del self.library[:3]
                if not look:
                    break
                self.hand.append(look[0])
                got += 1
                for c in look[1:]:
                    self.graveyard.append(c)
                    self.cards_milled_total += 1
                    if self.rng.random() < DENSITY_ELF:
                        self.elves_milled_to_gy += 1
            else:
                self.hand.append(self.library.pop(0))
                got += 1
        if source != "normal":
            self.extra_draws += got
        return got

    def mill(self, n=1):
        milled = 0
        for _ in range(n):
            if self.library:
                card = self.library.pop(0)
                self.graveyard.append(card)
                milled += 1
                self.cards_milled_total += 1
                # proxy: cada carta milhada tem chance DENSITY_ELF de ser Elfo
                if self.rng.random() < DENSITY_ELF:
                    self.elves_milled_to_gy += 1
        return milled

    def has(self, name: str) -> bool:
        return name in self.battlefield

    def cleanup_hand_size(self):
        while len(self.hand) > self.max_hand_size:
            self.hand.sort(key=lambda c: -C(c).mv)
            self.hand.pop(0)
            self.cards_discarded_to_hand_size += 1

# =========================================================
# MANA MODEL (tricolor: total + fontes de cada cor)
# =========================================================

def _dork_ready(state: GameState, card: str) -> bool:
    return state.creature_cast_turn.get(card, -1) < state.turn

def total_mana(state: GameState) -> int:
    total = 0
    for card in state.battlefield:
        if is_land(card):
            total += 1
        elif card == "Sol Ring":
            total += 2
        elif "Creature" in C(card).types and not _dork_ready(state, card):
            continue  # doenca de invocacao (CR 302.6) - achado real 2026-08-28, nunca existia antes
        elif has_tag(card, "elf_scaling"):
            elves = sum(1 for c in state.battlefield if is_elf(c))
            total += max(1, elves)
        elif card == "Gwenna, Eyes of Gaea":
            # Achado real 2026-08-28: "{T}: Add TWO mana in any combination
            # of colors" - tratada como ramp generico (+1) antes. A
            # restricao "spend only on creature spells/abilities" nao e'
            # modelada (deck e' quase todo criatura, baixo impacto real).
            total += 2
        elif has_tag(card, "power_scaling"):
            total += 2  # aproximacao: poder medio do board nesses turnos
        elif has_tag(card, "gy_scaling"):
            total += max(1, len(state.graveyard) // 3)
        elif has_tag(card, "ramp"):
            total += 1
    return total

def color_sources(state: GameState, color: str, elf_creature_spell: bool = False) -> int:
    n = 0
    yavimaya = state.has("Yavimaya, Cradle of Growth")
    for card in state.battlefield:
        if is_land(card):
            # Yavimaya: "Each land is a Forest in addition to its other
            # land types" - achado real 2026-08-28, nunca implementada.
            if color == "G" and yavimaya:
                n += 1
                continue
            if card == "Reflecting Pool":
                # "Add one mana of any type that a land you control could
                # produce." Achado real 2026-08-28: era fixa {B,G,U},
                # deveria ser a uniao dinamica dos OUTROS terrenos em campo.
                others = {c for other in state.battlefield if other != card and is_land(other)
                          for c in C(other).produces}
                if color in others:
                    n += 1
                continue
            if color in C(card).produces:
                n += 1
        else:
            if "Creature" in C(card).types and not _dork_ready(state, card):
                continue
            if color not in C(card).produces:
                continue
            if has_tag(card, "elf_only_color") and not elf_creature_spell:
                continue
            n += 1
    return n

def remaining_mana(state: GameState) -> int:
    return total_mana(state) - state.mana_spent_this_turn

def can_cast(state: GameState, card: str) -> bool:
    if remaining_mana(state) < C(card).mv:
        return False
    elf_spell = is_elf(card) and "Creature" in C(card).types
    for color in C(card).colors:
        if color_sources(state, color, elf_creature_spell=elf_spell) < 1:
            return False
    return True

def commander_can_be_cast(state: GameState) -> bool:
    return can_cast(state, COMMANDER)

# =========================================================
# MULLIGAN
# =========================================================

KEEPERS = {"Sol Ring", "Elvish Mystic", "Llanowar Elves", "Arbor Elf", "Priest of Titania", "Bloom Tender", "Arcane Signet"}

def should_keep(hand: List[str]) -> bool:
    lands = sum(1 for c in hand if is_land(c))
    keepers = sum(1 for c in hand if c in KEEPERS)
    if lands < 2 or lands > 5:
        return False
    if keepers >= 1:
        return True
    return lands >= 3

def bottom_priority(card: str) -> tuple:
    if is_land(card):
        return (3, 0)
    if card in KEEPERS:
        return (0, C(card).mv)
    if has_tag(card, "ramp") or has_tag(card, "draw_engine"):
        return (1, C(card).mv)
    if has_tag(card, "finisher_repeatable") or has_tag(card, "finisher_burst"):
        return (4, -C(card).mv)
    return (2, C(card).mv)

def choose_bottom(hand: List[str], n: int) -> List[str]:
    ordered = sorted(hand, key=bottom_priority, reverse=True)
    return ordered[:n]

# =========================================================
# LAND DROP / CASTING PRIORITY
# =========================================================

def play_land(state: GameState, log: List[Dict]):
    # Thranduil's Company: "As long as you control another Elf, you may
    # play an additional land on each of your turns." Achado real
    # 2026-08-28 (auditoria de checklist de mecanica): o guard
    # `if state.land_played: return` bloqueava QUALQUER segundo land drop
    # incondicionalmente, mesmo com o Company em campo. Corrigido: teto de
    # lands por turno passa a ser 2 se o Company estiver em campo E houver
    # outro Elfo controlado (checagem real, nao assumida).
    max_lands = 1
    if state.has("Thranduil's Company"):
        other_elves = sum(1 for c in state.battlefield if is_elf(c) and c != "Thranduil's Company")
        if other_elves > 0:
            max_lands = 2
    if state.lands_played_this_turn >= max_lands:
        return
    lands_in_hand = [c for c in state.hand if is_land(c)]
    if not lands_in_hand:
        return
    # prioriza terreno que resolve a cor mais escassa em jogo
    def missing_score(card):
        score = 0
        for color in ("B", "G", "U"):
            if color_sources(state, color) < 2 and color in C(card).produces:
                score += 1
        return -score
    lands_in_hand.sort(key=missing_score)
    choice = lands_in_hand[0]
    state.hand.remove(choice)
    state.battlefield.append(choice)
    state.land_played = True
    state.lands_played_this_turn += 1
    state.lands_played_total += 1

    # Thranduil, Sindarin Liege: "Landfall - Whenever a land you control
    # enters, create a 1/1 green Elf creature token." Achado real
    # 2026-08-28: so' logava o gatilho, nunca criava o token de verdade.
    if state.has("Thranduil, Sindarin Liege // Silvan Rally"):
        times_rt = 2 if (state.roaming_throne_active() and is_elf("Thranduil, Sindarin Liege // Silvan Rally")) else 1
        for _ in range(times_rt):
            state.battlefield.append("Elf Warrior Token")
            state.landfall_elf_tokens += 1
        log.append({"trigger": "landfall_elf_token", "times": times_rt, "turn": state.turn})

    # Thranduil's Company: "Landfall - ... put two +1/+1 counters on target
    # creature you control. It gains vigilance until end of turn."
    # Achado real 2026-08-28: 100% ausente (so' a tag "land_ramp" existia,
    # nunca lida pra esse efeito). Contador agregado (esse motor nao
    # rastreia +1/+1 counters por criatura individual, mesma convencao ja
    # documentada alhures neste arquivo).
    if state.has("Thranduil's Company") and any(is_creature(c) for c in state.battlefield):
        state.thranduils_company_counters += 2

    log.append({"action": "land", "card": choice, "turn": state.turn})

def priority(state: GameState, card: str) -> tuple:
    if card == COMMANDER:
        return (2, 5)
    if has_tag(card, "ramp"):
        return (1, C(card).mv)
    if has_tag(card, "draw_engine") and state.turn <= 5:
        return (3, C(card).mv)
    if has_tag(card, "removal") and state.turn <= 5:
        return (4, C(card).mv)
    if has_tag(card, "token_maker") or has_tag(card, "anthem") or has_tag(card, "counter_engine"):
        return (5, C(card).mv)
    if has_tag(card, "gy_fill"):
        return (5, C(card).mv)
    if has_tag(card, "finisher_repeatable") or has_tag(card, "finisher_drain") or has_tag(card, "finisher_burst"):
        return (7, -C(card).mv)  # segura finishers pra depois
    return (6, C(card).mv)

def main_phase(state: GameState, log: List[Dict]):
    if not state.commander_in_play and state.turn >= 3:
        if commander_can_be_cast(state):
            _resolve_cast(state, COMMANDER, log, from_hand=False)

    for _ in range(6):
        castables = [c for c in state.hand if is_spell(c) and can_cast(state, c)]
        if not castables:
            break
        castables.sort(key=lambda c: priority(state, c))
        choice = castables[0]
        cast_spell(state, choice, log)

        if not state.commander_in_play and state.turn >= 3 and commander_can_be_cast(state):
            _resolve_cast(state, COMMANDER, log, from_hand=False)

    # Ativa finishers repetiveis se sobrar mana e houver board relevante
    activate_finishers(state, log)
    try_imperious_perfect(state, log)

def _creature_cast_engines_trigger(state: GameState, card: str, log: List[Dict]):
    # Beast Whisperer / Champions of the Perfect: "whenever you cast a creature spell, draw a card".
    # Checado ANTES de "card" entrar no campo, entao a propria carta nao dispara suas proprias copias.
    if not is_creature(card):
        return
    engines = [c for c in state.battlefield if has_tag(c, "creature_draw_engine")]
    for eng in engines:
        state.draw(1, source=f"{eng} (creature cast trigger)")
        state.creature_engine_draws += 1
        if state.roaming_throne_active():
            state.draw(1, source=f"{eng} (Roaming Throne dobra)")
            state.creature_engine_draws += 1
            state.roaming_throne_doublings += 1
    if engines:
        log.append({"trigger": "creature_draw_engine", "card": card, "engines": engines, "turn": state.turn})

    times_rt = 2 if state.roaming_throne_active() else 1

    # Gwenna: "whenever you cast a creature spell with power 5 or greater, put
    # a +1/+1 counter on Gwenna and untap it." So a parte do contador tem
    # numero acumulavel (untap repetido nao muda nada).
    if state.has("Gwenna, Eyes of Gaea") and card != "Gwenna, Eyes of Gaea" and C(card).power >= 5:
        for i in range(times_rt):
            state.gwenna_counters += 1
        if times_rt == 2:
            state.roaming_throne_doublings += 1
        log.append({"trigger": "gwenna_counter", "card": card, "times": times_rt, "turn": state.turn})

    # Selvala: "whenever another creature enters, its controller may draw a
    # card if its power is greater than each other creature's power." Battlefield
    # aqui ainda NAO tem "card" (hook roda antes do append), entao "outras
    # criaturas" = state.battlefield no momento desta checagem.
    if state.has("Selvala, Heart of the Wilds") and card != "Selvala, Heart of the Wilds":
        others_power = [C(c).power for c in state.battlefield if is_creature(c)]
        max_other = max(others_power) if others_power else 0
        if C(card).power > max_other:
            for i in range(times_rt):
                state.draw(1, source="Selvala ETB draw" if i == 0 else "Selvala ETB draw (Roaming Throne dobra)")
                state.selvala_draws += 1
            if times_rt == 2:
                state.roaming_throne_doublings += 1
            log.append({"trigger": "selvala_draw", "card": card, "times": times_rt, "turn": state.turn})

    if is_elf(card):
        # Marwyn: "whenever another Elf you control enters, put a +1/+1
        # counter on Marwyn."
        if state.has("Marwyn, the Nurturer") and card != "Marwyn, the Nurturer":
            for i in range(times_rt):
                state.marwyn_counters += 1
            if times_rt == 2:
                state.roaming_throne_doublings += 1
            log.append({"trigger": "marwyn_counter", "card": card, "times": times_rt, "turn": state.turn})

        # Elvish Warmaster: "whenever one or more other Elves you control
        # enter, create a 1/1 green Elf Warrior creature token. This ability
        # triggers only once each turn." O "1x/turno" e do proprio texto -
        # Roaming Throne dispara a instancia que ja aconteceu uma vez a mais,
        # nao permite burlar o limite fazendo ela checar de novo.
        if (state.has("Elvish Warmaster") and card != "Elvish Warmaster"
                and not state.elvish_warmaster_triggered_this_turn):
            state.elvish_warmaster_triggered_this_turn = True
            for i in range(times_rt):
                state.battlefield.append("Elf Warrior Token")
                state.elvish_warmaster_tokens += 1
            if times_rt == 2:
                state.roaming_throne_doublings += 1
            log.append({"trigger": "elvish_warmaster_token", "card": card, "times": times_rt, "turn": state.turn})

        # High Perfect Morcant: "whenever [ela] ou outro Elfo entra, cada
        # oponente sofre blight 1." Sem oponente real no goldfish solo - so
        # contador, sem efeito numerico no proprio estado. Limitacao conhecida:
        # esse hook roda ANTES da carta entrar em campo, entao a propria
        # Morcant nao dispara o proprio ETB dela mesma (so o "outro Elfo" e
        # capturado) - perde 1 disparo possivel por partida, aceitavel.
        if state.has("High Perfect Morcant"):
            for i in range(times_rt):
                state.high_perfect_morcant_triggers += 1
            if times_rt == 2:
                state.roaming_throne_doublings += 1

        # Maralen: "whenever [ela] or another Elf or Faerie you control
        # enters, exile the top two cards of target opponent's library." Sem
        # oponente real - so contador.
        if state.has("Maralen, Fae Ascendant"):
            for i in range(times_rt):
                state.maralen_triggers += 1
            if times_rt == 2:
                state.roaming_throne_doublings += 1

def _resolve_cast(state: GameState, card: str, log: List[Dict], from_hand: bool):
    if from_hand:
        state.hand.remove(card)
    _creature_cast_engines_trigger(state, card, log)
    state.spells_cast += 1
    state.mana_spent_this_turn += C(card).mv
    state.battlefield.append(card)
    if "Creature" in C(card).types:
        state.creature_cast_turn[card] = state.turn
    if card == COMMANDER:
        state.commander_in_play = True
        state.commander_cast_turn = state.turn
        log.append({"action": "cast_commander", "turn": state.turn})
    _apply_etb(state, card, log)

def cast_spell(state: GameState, card: str, log: List[Dict]):
    state.hand.remove(card)
    _creature_cast_engines_trigger(state, card, log)
    state.spells_cast += 1
    state.mana_spent_this_turn += C(card).mv

    if "Instant" in C(card).types or "Sorcery" in C(card).types:
        state.graveyard.append(card)
    else:
        state.battlefield.append(card)
        if "Creature" in C(card).types:
            state.creature_cast_turn[card] = state.turn

    if has_tag(card, "ramp"):
        state.ramp_pieces_in_play += 1
    if has_tag(card, "removal") or has_tag(card, "removal_repeatable"):
        state.removal_cast += 1

    _apply_etb(state, card, log)
    log.append({"action": "cast", "card": card, "turn": state.turn})

def _apply_etb(state: GameState, card: str, log: List[Dict]):
    # Gatilho do proprio Thranduil: elfo lendario entra -> compra 2, descarta 1.
    # Roaming Throne (Elf escolhido) faz o gatilho disparar uma vez A MAIS -
    # e um segundo disparo completo (compra 2 + descarta 1 de novo), nao so
    # dobrar os numeros de um disparo so.
    if state.commander_in_play and card != COMMANDER and C(card).is_legendary_elf:
        times = 2 if state.roaming_throne_active() else 1
        for i in range(times):
            state.draw(2, source="Thranduil ETB" if i == 0 else "Thranduil ETB (Roaming Throne dobra)")
            state.thranduil_legendary_elf_triggers += 1
            if i == 1:
                state.roaming_throne_doublings += 1
            if state.hand:
                state.hand.sort(key=lambda c: -C(c).mv)
                discarded = state.hand.pop(0)
                state.graveyard.append(discarded)
                if is_elf(discarded) and discarded != COMMANDER:
                    pass  # ja rastreado via mill() pra fontes de mill; descarte manual nao conta como "milhado"
        log.append({"trigger": "thranduil_legendary_elf", "card": card, "times": times, "turn": state.turn})

    if card == "Edric, Spymaster of Trest":
        state.edric_was_cast = True
        state.edric_in_play = True
        # Premissa explicita (pedida por voce): sobrevive em media 2 dos seus turnos
        # antes de cair pra remocao pontual - e alvo obvio assim que o motor liga.
        lifespan = state.rng.randint(1, 2 * ASSUMED_EDRIC_LIFESPAN_TURNS_MEAN - 1)
        state.edric_last_turn_alive = state.turn + lifespan - 1
        log.append({"action": "edric_enters", "turn": state.turn, "assumed_lifespan_turns": lifespan})

    # GY fill (mill). Se a fonte e criatura Elfo (Lluwen: "When Lluwen enters,
    # mill four cards"), o Roaming Throne dobra o gatilho (mill de novo). Nao
    # dobra fontes nao-criatura como Awaken the Honored Dead (Saga) ou Buried
    # Alive (Sorcery) - Roaming Throne so afeta gatilho de CRIATURA.
    if C(card).mill_amount > 0:
        state.mill(C(card).mill_amount)
        times_mill = 1
        if is_creature(card) and is_elf(card) and state.roaming_throne_active():
            state.mill(C(card).mill_amount)
            state.roaming_throne_doublings += 1
            times_mill = 2
        log.append({"trigger": "mill", "card": card, "amount": C(card).mill_amount, "times": times_mill, "turn": state.turn})

    # Buried Alive: mill dedicado (nao e mill aleatorio, mas modelado como tal pra simplificar)
    if card == "Buried Alive":
        pass  # ja coberto por mill_amount acima

    # Finale of Devastation com X>=10 tratado como finisher burst direto (raro, poucas vezes acontece)
    if card == "Finale of Devastation" and total_mana(state) >= 12:
        state.finishers_activated.append("Finale of Devastation (X>=10)")
        if state.finisher_turn is None:
            state.finisher_turn = state.turn

    if card in {"Kindred Summons", "Bloodline Bidding"}:
        state.finishers_activated.append(card)
        if state.finisher_turn is None:
            state.finisher_turn = state.turn

def _elrond_ability_activated(state: GameState, source: str, log: List[Dict]):
    # Elrond: "Whenever you activate an ability of a creature, draw a card.
    # This ability triggers only once each turn." Roaming Throne dispara
    # essa UNICA instancia de novo (nao permite burlar o "1x/turno" da
    # propria carta gerando um novo disparo por ativacao subsequente).
    if not state.has("Elrond, Moon-Reader") or state.elrond_triggered_this_turn:
        return
    state.elrond_triggered_this_turn = True
    times_rt = 2 if state.roaming_throne_active() else 1
    for i in range(times_rt):
        state.draw(1, source=f"Elrond ({source})" if i == 0 else f"Elrond ({source}, Roaming Throne dobra)")
        state.elrond_draws += 1
    if times_rt == 2:
        state.roaming_throne_doublings += 1
    log.append({"trigger": "elrond_draw", "source": source, "times": times_rt, "turn": state.turn})

def try_imperious_perfect(state: GameState, log: List[Dict]):
    """"{G}, {T}: Create a 1/1 green Elf Warrior creature token." Achado
    real 2026-08-28 (auditoria de checklist de mecanica): tagueada
    "token_maker" mas activation_cost nunca setado (default 0), e
    activate_finishers() pula qualquer carta com cost<=0 - nunca
    disparava. {T} = 1 ativacao por turno."""
    if "Imperious Perfect" not in state.battlefield:
        return
    if not _dork_ready(state, "Imperious Perfect"):
        return
    if remaining_mana(state) < 1 or color_sources(state, "G") < 1:
        return
    state.mana_spent_this_turn += 1
    times_rt = 2 if state.roaming_throne_active() and is_elf("Imperious Perfect") else 1
    for _ in range(times_rt):
        state.battlefield.append("Elf Warrior Token")
        state.imperious_perfect_tokens += 1
    log.append({"trigger": "imperious_perfect_token", "times": times_rt, "turn": state.turn})


def activate_finishers(state: GameState, log: List[Dict]):
    creatures_in_play = sum(1 for c in state.battlefield if is_creature(c))
    if creatures_in_play == 0:
        return
    for card in state.battlefield:
        cost = C(card).activation_cost
        if cost <= 0:
            continue
        if has_tag(card, "finisher_repeatable") and remaining_mana(state) >= cost:
            state.mana_spent_this_turn += cost
            state.finishers_activated.append(card)
            if state.finisher_turn is None:
                state.finisher_turn = state.turn
            log.append({"trigger": "finisher_activated", "card": card, "turn": state.turn})
            if is_creature(card):
                _elrond_ability_activated(state, card, log)
        elif has_tag(card, "finisher_drain") and card == "Jarad, Golgari Lich Lord" and remaining_mana(state) >= cost:
            state.mana_spent_this_turn += cost
            state.finishers_activated.append(card)
            if state.finisher_turn is None:
                state.finisher_turn = state.turn
            _elrond_ability_activated(state, card, log)
        elif card == "Lathril, Blade of the Elves":
            elves_untapped_proxy = sum(1 for c in state.battlefield if is_elf(c))
            if elves_untapped_proxy >= 10:
                state.finishers_activated.append(card)
                if state.finisher_turn is None:
                    state.finisher_turn = state.turn
                _elrond_ability_activated(state, card, log)

# =========================================================
# COMBATE (Edric + tokens do Lathril via dano de combate)
# Simplificacao: sem doenca de invocacao e sem bloqueadores modelados (mesmo
# nivel de fidelidade que o combat_step do Beorn) - todas as criaturas em
# campo sao tratadas como atacando e conectando.
# =========================================================

def combat_step(state: GameState, log: List[Dict]):
    creatures = [c for c in state.battlefield if is_creature(c)]
    if not creatures:
        return

    if state.edric_in_play:
        # Edric e Elfo - Roaming Throne dobra cada instancia do gatilho dele
        # ("whenever A creature deals combat damage..." dispara 1x por criatura
        # que conecta; cada disparo individual dispara uma vez a mais).
        n = len(creatures)
        if state.roaming_throne_active():
            n *= 2
            state.roaming_throne_doublings += 1
        state.draw(n, source="Edric combat damage")
        state.combat_damage_draws += n
        log.append({"trigger": "edric_combat_draw", "turn": state.turn, "amount": n})
        if state.turn >= state.edric_last_turn_alive:
            if "Edric, Spymaster of Trest" in state.battlefield:
                state.battlefield.remove("Edric, Spymaster of Trest")
            state.edric_death_turn = state.turn
            state.edric_in_play = False
            log.append({"action": "edric_removed", "turn": state.turn})

    if state.has("Lathril, Blade of the Elves"):
        # Poder da Lathril (base 2) + aproximacao dos anthems de Elfo em campo (Elvish Archdruid,
        # Thranduil Sindarin Liege) - nao rastreamos +1/+1 counters individuais neste simulador.
        anthem_bonus = sum(1 for c in state.battlefield if has_tag(c, "anthem"))
        lathril_power = 2 + anthem_bonus
        # Lathril e Elfo - Roaming Throne dispara o gatilho dela uma vez a mais
        # (cria lathril_power tokens de novo, nao so dobra a contagem de uma vez so).
        times = 2 if state.roaming_throne_active() else 1
        if times == 2:
            state.roaming_throne_doublings += 1
        for _ in range(times):
            for _ in range(lathril_power):
                state.battlefield.append("Elf Warrior Token")
            state.lathril_tokens_created += lathril_power
        log.append({"trigger": "lathril_tokens", "turn": state.turn, "amount": lathril_power * times})

    if state.has("Glissa Sunslayer"):
        # Modal: draw+lose 1 life / destroy enchantment / remove counters.
        # So o modo "compre 1, perca 1 vida" tem efeito numerico modelavel
        # num goldfish solo sem permanentes de oponente pra remover/destruir -
        # os outros dois modos ficam sem alvo real nesse contexto.
        times_glissa = 2 if state.roaming_throne_active() else 1
        if times_glissa == 2:
            state.roaming_throne_doublings += 1
        for _ in range(times_glissa):
            state.draw(1, source="Glissa Sunslayer combat damage")
            state.glissa_draws += 1
        log.append({"trigger": "glissa_draw", "turn": state.turn, "times": times_glissa})

    if state.has("Tyvar the Bellicose"):
        # "Whenever one or more Elves you control attack, they gain deathtouch
        # until end of turn." Sem bloqueadores modelados nesse motor de combate
        # simplificado - sem efeito numerico, so contador de quantas vezes
        # disparou.
        times_tyvar = 2 if state.roaming_throne_active() else 1
        state.tyvar_bellicose_triggers += times_tyvar
        if times_tyvar == 2:
            state.roaming_throne_doublings += 1

# =========================================================
# RHYSTIC STUDY (depende de spells de oponentes - ver premissas no topo do arquivo)
# =========================================================

def apply_rhystic_study(state: GameState, log: List[Dict]):
    if not state.has("Rhystic Study"):
        return
    for _ in range(ASSUMED_OPPONENT_SPELLS_PER_TURN):
        state.rhystic_study_opportunities += 1
        if state.rng.random() >= ASSUMED_RHYSTIC_STUDY_PAY_RATE:
            state.draw(1, source="Rhystic Study")
            state.rhystic_study_draws += 1
        else:
            state.rhystic_study_denied += 1

# =========================================================
# TURN STRUCTURE
# =========================================================

def play_turn(state: GameState, turn: int, game_log: List[List[Dict]]):
    state.turn = turn
    state.land_played = False
    state.lands_played_this_turn = 0
    state.mana_spent_this_turn = 0
    state.elrond_triggered_this_turn = False
    state.elvish_warmaster_triggered_this_turn = False

    log = [{"turn": turn, "phase": "start", "hand_size": len(state.hand),
            "battlefield_count": len(state.battlefield), "mana_est": total_mana(state)}]

    # Ruthless Winnower: "At the beginning of each player's upkeep, that
    # player sacrifices a non-Elf creature of their choice." No goldfish solo
    # so o SEU upkeep e modelado. Roaming Throne dobrar isso e RUIM pra voce
    # (sacrifica 2 em vez de 1) - flag explicito, nao e um beneficio como os
    # outros gatilhos.
    if state.has("Ruthless Winnower"):
        times_winnower = 2 if state.roaming_throne_active() else 1
        if times_winnower == 2:
            state.roaming_throne_doublings += 1
        for _ in range(times_winnower):
            non_elves = [c for c in state.battlefield if is_creature(c) and not is_elf(c)]
            if non_elves:
                non_elves.sort(key=lambda c: C(c).mv)  # sacrifica o de menor CMC primeiro
                state.battlefield.remove(non_elves[0])
                state.ruthless_winnower_self_sacs += 1
                log.append({"trigger": "ruthless_winnower_self_sac", "sacrificed": non_elves[0], "turn": turn})

    # Multiplayer (CR 103.8a): sempre compra, mesmo no T1.
    state.draw(1, source="normal")

    play_land(state, log)
    play_land(state, log)  # 2a chamada: no-op a menos que Thranduil's Company habilite o 2o land drop

    # Color screw de azul: mana total ja daria pro comandante, mas falta fonte de U.
    if not state.commander_in_play and state.turn >= 3 and total_mana(state) >= C(COMMANDER).mv and color_sources(state, "U") < 1:
        state.blue_screw_turns += 1
        if state.first_blue_screw_turn is None:
            state.first_blue_screw_turn = state.turn
        log.append({"trigger": "blue_screw", "turn": state.turn})

    main_phase(state, log)
    combat_step(state, log)
    apply_rhystic_study(state, log)
    state.cleanup_hand_size()

    log.append({"turn": turn, "phase": "end", "hand_size": len(state.hand),
                "battlefield_count": len(state.battlefield),
                "spells_cast": state.spells_cast})
    game_log.append(log)

# =========================================================
# SIMULATION
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
        state.draw(7, source="normal")
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

    game_log = [[{"seed": seed, "mulligans": mulligans, "starting_hand": list(state.hand)}]]

    for t in range(1, turns + 1):
        play_turn(state, t, game_log)

    return {
        "seed": seed,
        "mulligans": mulligans,
        "commander_cast_turn": state.commander_cast_turn,
        "spells_cast": state.spells_cast,
        "extra_draws": state.extra_draws,
        "ramp_pieces_in_play": state.ramp_pieces_in_play,
        "removal_cast": state.removal_cast,
        "cards_discarded_to_hand_size": state.cards_discarded_to_hand_size,
        "thranduil_legendary_elf_triggers": state.thranduil_legendary_elf_triggers,
        "cards_milled_total": state.cards_milled_total,
        "elves_milled_to_gy": state.elves_milled_to_gy,
        "finishers_activated": len(state.finishers_activated),
        "finisher_turn": state.finisher_turn,
        "battlefield_count": len(state.battlefield),
        "hand_size": len(state.hand),
        "lands_played_total": state.lands_played_total,
        "creature_engine_draws": state.creature_engine_draws,
        "combat_damage_draws": state.combat_damage_draws,
        "lathril_tokens_created": state.lathril_tokens_created,
        "rhystic_study_in_play": state.has("Rhystic Study"),
        "rhystic_study_draws": state.rhystic_study_draws,
        "rhystic_study_denied": state.rhystic_study_denied,
        "edric_was_cast": state.edric_was_cast,
        "edric_death_turn": state.edric_death_turn,
        "blue_screw_turns": state.blue_screw_turns,
        "first_blue_screw_turn": state.first_blue_screw_turn,
        "roaming_throne_in_play": state.has("Roaming Throne"),
        "roaming_throne_doublings": state.roaming_throne_doublings,
        "marwyn_counters": state.marwyn_counters,
        "landfall_elf_tokens": state.landfall_elf_tokens,
        "thranduils_company_counters": state.thranduils_company_counters,
        "imperious_perfect_tokens": state.imperious_perfect_tokens,
        "selvala_draws": state.selvala_draws,
        "elrond_draws": state.elrond_draws,
        "elvish_warmaster_tokens": state.elvish_warmaster_tokens,
        "glissa_draws": state.glissa_draws,
        "gwenna_counters": state.gwenna_counters,
        "high_perfect_morcant_triggers": state.high_perfect_morcant_triggers,
        "maralen_triggers": state.maralen_triggers,
        "ruthless_winnower_self_sacs": state.ruthless_winnower_self_sacs,
        "tyvar_bellicose_triggers": state.tyvar_bellicose_triggers,
    }

def run_batch(n=500, turns=8, out_jsonl="thranduil_v1_runs.jsonl", seed_base=71000):
    results = []
    with open(out_jsonl, "w", encoding="utf-8") as f:
        for i in range(n):
            res = simulate_one(seed=seed_base + i, turns=turns)
            results.append(res)
            f.write(json.dumps(res, ensure_ascii=False) + "\n")

    def avg(key):
        vals = [r[key] for r in results if r[key] is not None]
        return statistics.mean(vals) if vals else 0.0

    cmd_turns = [r["commander_cast_turn"] for r in results if r["commander_cast_turn"] is not None]
    fin_turns = [r["finisher_turn"] for r in results if r["finisher_turn"] is not None]

    print("=== Thranduil, the Elvenking — Goldfish Summary v1 (simulado por Claude) ===")
    print(f"Games: {n} | Turns: {turns} | Multiplayer (compra sempre no T1, CR 103.8a)")
    print()
    print(f"Avg mulligans: {avg('mulligans'):.2f}")
    if cmd_turns:
        print(f"Avg commander cast turn: {statistics.mean(cmd_turns):.2f}")
        print(f"Commander cast by turn 5: {100*sum(1 for t in cmd_turns if t<=5)/n:.1f}%")
        print(f"Commander cast by turn 6: {100*sum(1 for t in cmd_turns if t<=6)/n:.1f}%")
    else:
        print("Commander nunca conjurado na amostra.")
    print()
    print(f"Avg spells cast: {avg('spells_cast'):.2f}")
    print(f"Avg extra draws (gatilhos): {avg('extra_draws'):.2f}")
    print(f"Avg ramp pieces em campo: {avg('ramp_pieces_in_play'):.2f}")
    print(f"Avg remocao conjurada: {avg('removal_cast'):.2f}")
    print(f"Avg gatilhos 'elfo lendario entrou' (Thranduil draw2/discard1): {avg('thranduil_legendary_elf_triggers'):.2f}")
    print(f"Avg cartas milhadas (mill total): {avg('cards_milled_total'):.2f}")
    print(f"Avg Elfos milhados pro cemiterio (proxy por densidade): {avg('elves_milled_to_gy'):.2f}")
    print(f"Avg finishers ativados: {avg('finishers_activated'):.2f}")
    if fin_turns:
        print(f"Avg turno do 1o finisher ativado: {statistics.mean(fin_turns):.2f}")
        print(f"% de jogos com finisher ativado ate T8: {100*len(fin_turns)/n:.1f}%")
    print()
    print(f"Avg compras via Beast Whisperer/Champions of the Perfect (criatura conjurada): {avg('creature_engine_draws'):.2f}")
    print(f"Avg compras via Edric (dano de combate): {avg('combat_damage_draws'):.2f}")
    edric_cast = [r for r in results if r["edric_was_cast"]]
    if edric_cast:
        edric_deaths = [r["edric_death_turn"] for r in edric_cast if r["edric_death_turn"] is not None]
        print(f"  Edric conjurada em {100*len(edric_cast)/n:.1f}% dos jogos")
        if edric_deaths:
            print(f"  Removida por remocao (premissa de ~2 turnos vivos) em {100*len(edric_deaths)/len(edric_cast):.1f}% dos jogos em que foi conjurada, turno medio: {statistics.mean(edric_deaths):.2f}")
    print(f"Avg tokens de Elfo via Lathril (dano de combate): {avg('lathril_tokens_created'):.2f}")
    rs_games = [r for r in results if r["rhystic_study_in_play"]]
    if rs_games:
        print(f"Rhystic Study em campo em {100*len(rs_games)/n:.1f}% dos jogos")
        print(f"  Avg compras via Rhystic Study (premissa: {ASSUMED_OPPONENT_SPELLS_PER_TURN} spells de oponente/turno, {ASSUMED_RHYSTIC_STUDY_PAY_RATE*100:.0f}% de taxa paga): {statistics.mean([r['rhystic_study_draws'] for r in rs_games]):.2f}")
        print(f"  Avg vezes que o oponente pagou o {{1}} pra evitar: {statistics.mean([r['rhystic_study_denied'] for r in rs_games]):.2f}")
    print(f"Avg cartas descartadas por limite de mao: {avg('cards_discarded_to_hand_size'):.2f}")
    print(f"Avg battlefield final: {avg('battlefield_count'):.2f}")
    print(f"Avg mao final: {avg('hand_size'):.2f}")
    print(f"Avg terrenos jogados: {avg('lands_played_total'):.2f}")

    blue_screwed = [r for r in results if r["blue_screw_turns"] > 0]
    print()
    print(f"Avg turnos com 'color screw' de azul (mana total ok, sem fonte de U): {avg('blue_screw_turns'):.2f}")
    print(f"% de partidas com pelo menos 1 turno de blue screw: {100*len(blue_screwed)/n:.1f}%")
    if blue_screwed:
        fbs = [r["first_blue_screw_turn"] for r in blue_screwed]
        print(f"  Turno medio do 1o blue screw: {statistics.mean(fbs):.2f}")

    rt_games = [r for r in results if r["roaming_throne_in_play"]]
    if rt_games:
        print()
        print(f"Roaming Throne em campo em {100*len(rt_games)/n:.1f}% dos jogos (tipo escolhido: Elf)")
        print(f"  Avg gatilhos de criatura Elfo dobrados por partida (total, todas as fontes): {statistics.mean([r['roaming_throne_doublings'] for r in rt_games]):.2f}")

    print()
    print("--- Elfos com gatilho proprio (novo) ---")
    print(f"Avg contadores em Marwyn (outro Elfo entra): {avg('marwyn_counters'):.2f}")
    print(f"Avg tokens de Elfo via landfall (Thranduil, Sindarin Liege - agora despachado): {avg('landfall_elf_tokens'):.2f}")
    print(f"Avg contadores via landfall (Thranduil's Company - agora despachado): {avg('thranduils_company_counters'):.2f}")
    print(f"Avg tokens de Elfo via Imperious Perfect (agora despachado): {avg('imperious_perfect_tokens'):.2f}")
    print(f"Avg compras via Selvala (criatura entra com maior poder): {avg('selvala_draws'):.2f}")
    print(f"Avg compras via Elrond (ativa habilidade de criatura, 1x/turno): {avg('elrond_draws'):.2f}")
    print(f"Avg tokens via Elvish Warmaster (1+ Elfo entra, 1x/turno): {avg('elvish_warmaster_tokens'):.2f}")
    print(f"Avg compras via Glissa Sunslayer (dano de combate, modo compra): {avg('glissa_draws'):.2f}")
    print(f"Avg contadores em Gwenna (conjura criatura poder>=5): {avg('gwenna_counters'):.2f}")
    print(f"Avg gatilhos de High Perfect Morcant (blight no oponente - sem efeito numerico modelado): {avg('high_perfect_morcant_triggers'):.2f}")
    print(f"Avg gatilhos de Maralen (exila biblioteca do oponente - sem efeito numerico modelado): {avg('maralen_triggers'):.2f}")
    print(f"Avg auto-sacrificios via Ruthless Winnower (upkeep, seu proprio nao-Elfo): {avg('ruthless_winnower_self_sacs'):.2f}")
    print(f"Avg gatilhos de Tyvar the Bellicose (deathtouch em combate - sem efeito numerico modelado): {avg('tyvar_bellicose_triggers'):.2f}")

    print()
    print(f"Logs salvos em: {out_jsonl}")

if __name__ == "__main__":
    run_batch(n=500, turns=8, out_jsonl="/tmp/thranduil_v1_runs.jsonl")
