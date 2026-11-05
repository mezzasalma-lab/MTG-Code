"""
Goldfish simulator — The Wise Mothman (Sultai, B/G/U): mill + rad counters + contadores +1/+1

Construido do zero em 2026-10-05, a pedido direto do usuario ("Sim, construa o simulador do Mothman. Leve em conta que ele da
Counters toda vez que alguem milla cartas"). Passo 0 (CLAUDE.md, Regras #1/#3): oraculo e rulings de TODAS as 91 cartas distintas
(100 com o comandante e os basicos) lidos do `scryfall-cache/oracle-cache.json` e de `resultados-ab/2026-10-05-candidatas-pos-eoe/dados/lista_bruto.json`
(JSON do Scryfall + `rulings`), nao de memoria. Clausula-a-clausula: `checklist-oraculo.md`.

======================================================================
O QUE ESTE DECK FAZ — e como o motor reflete isso
======================================================================
The Wise Mothman: "Whenever one or more nonland cards are milled, put a +1/+1 counter on each of up to X target creatures, where X is the number
of nonland cards milled this way." QUALQUER jogador, QUALQUER evento de mill (rulings 2024-03-08: cartas milladas de uma vez = UM gatilho; varios jogadores
instruidos ao mesmo tempo = UM gatilho). Por isso TODO mill do arquivo passa por `mill_event()`, que e' o unico ponto onde uma carta sai da
biblioteca para o cemiterio por efeito de mill, e que despacha TODOS os gatilhos de "milled" / "put into a graveyard" / "land cards put into your graveyard"
(Mothman, Mirelurk Queen, Zellix, Undead Alchemist, Syr Konrad, Bloodchief Ascension, Gitrog, Hedge Shredder, Kozilek).
Rad counters: inerente ("at the beginning of the precombat main phase of a player with rad counters, that player mills cards equal to the number of rad
counters; for each nonland card milled this way, that player loses 1 life and removes one rad counter" — CR 728.1) disparado no main de CADA jogador,
inclusive dos 3 oponentes (cujas bibliotecas, vida e rad counters sao modelados: e' o proprio motor do deck, nao tabuleiro fabricado).

======================================================================
CONVENCOES DECLARADAS (premissas explicitas, nao ausencia de checagem)
======================================================================
- Mesa de 4 (NUM_OPPONENTS = 3). Oponentes PASSIVOS no modo padrao: compram, jogam terreno/magias de forma estatistica (so' o que importa pro deck:
  quantas magias, de que tipo e MV — Memory Erosion, Pollywog Prodigy, contramagicas), tomam rad counters e mill, e perdem por vida 0, biblioteca vazia
  ao comprar, ou 21 de dano de comandante. NAO ha tabuleiro de oponente (sem bloqueio): todo atacante conecta (convencao de todos os simuladores do repositorio).
- Biblioteca de cada oponente: 99 cartas, 37 terrenos / 28 criaturas / 34 outras (tipos, nao nomes). Parametros em `OPP_*`.
- Habilidade que precisa de ALVO no tabuleiro do oponente (Tear Asunder, V.A.T.S., Boseiju channel, Strip Mine, Cankerbloom destruir, Wave Goodbye) so' conta
  como metrica proxy `interaction_plays` quando `OPP_TARGET_PROB` diz que existe alvo; o efeito no oponente nao e' simulado (estrutural, citado no checklist).
  O efeito PROPRIO continua real: Strip Mine/channel/cycling mandam terreno ao SEU cemiterio (Gitrog compra, Icetill rejoga), alvo de oponente conta como "crime"
  (Deepmuck Desperado, Freestrider Lookout) — CR dos rulings 2024.
- Regras de motor ja' validadas em outras rodadas (CLAUDE.md Regra #10): mulligan ESCOLHE o fundo (CR 103.5), imposto do comandante conta no cast, upkeep antes do
  draw, terreno que entra virado jogado primeiro em T1/T2 quando nao custa desenvolvimento (ensaio a seco com copia profunda), fetch real inclusive a devolvida
  do cemiterio, todo gatilho de "land enters" em TODO ponto de entrada.
- Determinismo: nenhuma iteracao de set/dict de str com ordem importando (usar listas/sorted); `PYTHONHASHSEED` nao pode mudar o resultado.
"""

import collections
import copy
import itertools
import json
import math
import random
import statistics
from dataclasses import dataclass, field
from typing import Optional

# =========================================================
# CHAVES DE VARIANTE / PARAMETROS (A/B e sensibilidade)
# =========================================================
FETCH_LANDS_ENABLED = True
LAND_ENTER_TRIGGERS_ALL_ENABLED = True
TAPPED_LAND_FIRST_ENABLED = True
TAPPED_LAND_FIRST_MAX_TURN = 2
TAPPED_LAND_FIRST_GHOST = False

NUM_OPPONENTS = 3
OPP_START_LIFE = 40
OPP_DECK_SIZE = 99
OPP_LANDS_IN_DECK = 37
OPP_CREATURES_IN_DECK = 28            # o resto (34) e' nao-criatura nao-terreno
OPP_HAND_START = 7
OPP_SPELLS_PROB = {0: 0.10, 1: 0.55, 2: 0.35}   # a partir do 2o turno do oponente: P(0, 1, 2 magias por turno)
OPP_CREATURE_SPELL_FRACTION = 0.45
OPP_SPELL_MV = [1, 2, 3, 4, 5, 6]
OPP_SPELL_MV_W = [0.15, 0.25, 0.25, 0.17, 0.12, 0.06]
OPP_TAP_FRACTION = 0.7                # fracao dos terrenos do oponente tapados no turno dele (Mesmeric Orb mill no untap seguinte)
OPP_TARGET_PROB = 0.7                 # a partir do T3: P(o oponente tem alvo legal pra efeito que mira o tabuleiro dele)
OPP_TARGET_FROM_TURN = 3
OPP_CREATURE_TARGETS = 0              # criaturas de oponente que existem pra mirar (Generous Patron / Mothman mirando criatura de oponente). 0 = goldfish puro
PALANTIR_OPP_LETS_DRAW = 0.5          # P(o oponente escolhe "voce compra" no Palantir) — sensibilidade
SHIFTING_WOODLAND_ENABLED = True
MINAMO_ENABLED = True
CAULDRON_ABILITIES_ENABLED = True
SAGE_PROLIFERATE_OWN_RAD = False      # proliferate nos rad counters PROPRIOS? (padrao: nao; so' os dos oponentes)
ALL_ATTACKERS_COMBAT = True
KOZILEK_SHUFFLE_ENABLED = True        # chave de teste do "seguro contra self-mill": False = Kozilek sem o embaralhar
LANDFALL_PAYOFF_FIRST = True          # conjura Ruin Crab / Icetill Explorer / Evolution Sage ANTES de jogar o terreno quando o mana de agora ja' paga (o terreno entao dispara o landfall); False = ordem do commit 91b1a3d (terreno primeiro)
LANDFALL_PAYOFFS = frozenset({"Ruin Crab", "Icetill Explorer", "Evolution Sage"})
LANDFALL_GUARD_DRYRUN = True             # True (padrao desde 2026-10-07) = o payoff so' passa na frente do terreno se um ensaio a seco do resto da fase mostrar que nenhuma jogada nao-terreno se perde (comandante, rocha, ...), como nos outros 5 simuladores; False = guarda ARITMETICA do comandante (custo <= mana de agora + 1), cega a cor/landfall/land drop extra: foi a arquivada em 2026-10-06 e superestimou o efeito (Ruin Crab +21% contra +13%)

# =========================================================
# CARD DATABASE
# =========================================================

@dataclass
class Card:
    name: str
    mv: int
    types: frozenset
    tags: frozenset = field(default_factory=frozenset)
    power: int = 0
    toughness: int = 0
    generic: int = 0
    pips: tuple = ()              # tuple de frozensets de cores aceitas por pip (hibrido = 2 cores)
    produces: frozenset = field(default_factory=frozenset)
    is_x: bool = False            # custo tem {X}
    x_mult: int = 1               # 2 para {X}{X}
    legendary: bool = False
    subtypes: frozenset = field(default_factory=frozenset)
    land_types: frozenset = field(default_factory=frozenset)   # subtipos de terreno (Forest, Island, Swamp)
    token: bool = False

    @property
    def ctype(self) -> str:
        for t in ("creature", "land", "planeswalker", "artifact", "enchantment", "instant", "sorcery"):
            if t in self.types:
                return t
        return "other"


CARD_DB: dict = {}


def parse_cost(cost: str):
    generic, pips, is_x, mult = 0, [], False, 0
    for sym in __import__("re").findall(r"\{([^}]+)\}", cost or ""):
        if sym == "X":
            is_x = True
            mult += 1
        elif sym.isdigit():
            generic += int(sym)
        elif "/" in sym:
            pips.append(frozenset(sym.split("/")))
        else:
            pips.append(frozenset(sym))
    return generic, tuple(pips), is_x, max(mult, 1)


def add(name, cost, types, tags=(), power=0, toughness=0, produces=(), legendary=False, subtypes=(), land_types=(), token=False, mv=None):
    g, pips, is_x, mult = parse_cost(cost)
    m = mv if mv is not None else g + len(pips)
    CARD_DB[name] = Card(name=name, mv=m, types=frozenset(types), tags=frozenset(tags), power=power, toughness=toughness, generic=g, pips=pips,
                         produces=frozenset(produces), is_x=is_x, x_mult=mult, legendary=legendary, subtypes=frozenset(subtypes),
                         land_types=frozenset(land_types), token=token)


COMMANDER = "The Wise Mothman"
add(COMMANDER, "{1}{B}{G}{U}", {"creature"}, {"commander", "flying"}, 3, 3, legendary=True, subtypes={"Insect", "Mutant"})

# --- Terrenos ---------------------------------------------------------------
for _n, _t, _c in (("Forest", "Forest", "G"), ("Island", "Island", "U"), ("Swamp", "Swamp", "B")):
    add(_n, "", {"land"}, {"basic"}, produces={_c}, land_types={_t})
add("Bojuka Bog", "", {"land"}, {"etb_tapped", "bog"}, produces={"B"})
add("Boseiju, Who Endures", "", {"land"}, {"boseiju"}, produces={"G"}, legendary=True)
add("Breeding Pool", "", {"land"}, {"shock"}, produces={"G", "U"}, land_types={"Forest", "Island"})
add("Command Tower", "", {"land"}, {"command_tower"}, produces={"B", "G", "U"})
add("Fabled Passage", "", {"land"}, {"fetch", "fabled_passage"})
add("Minamo, School at Water's Edge", "", {"land"}, {"minamo"}, produces={"U"}, legendary=True)
add("Misty Rainforest", "", {"land"}, {"fetch"})
add("Morphic Pool", "", {"land"}, {"slow_opp"}, produces={"B", "U"})
add("Overgrown Tomb", "", {"land"}, {"shock"}, produces={"B", "G"}, land_types={"Swamp", "Forest"})
add("Plaza of Heroes", "", {"land"}, {"plaza"}, produces={"C"})
add("Polluted Delta", "", {"land"}, {"fetch"})
add("Rejuvenating Springs", "", {"land"}, {"slow_opp"}, produces={"G", "U"})
add("Shifting Woodland", "", {"land"}, {"shifting_woodland"}, produces={"G"})
add("Strip Mine", "", {"land"}, {"strip_mine"}, produces={"C"})
add("Swarmyard", "", {"land"}, {"swarmyard"}, produces={"C"})
add("Takenuma, Abandoned Mire", "", {"land"}, {"takenuma"}, produces={"B"}, legendary=True)
add("Undergrowth Stadium", "", {"land"}, {"slow_opp"}, produces={"B", "G"})
add("Urza's Saga", "", {"land", "enchantment"}, {"urzas_saga", "saga"}, produces=set())
add("Verdant Catacombs", "", {"land"}, {"fetch"})
add("Waterlogged Grove", "", {"land"}, {"waterlogged_grove"}, produces={"G", "U"})
add("Watery Grave", "", {"land"}, {"shock"}, produces={"U", "B"}, land_types={"Island", "Swamp"})
add("Yavimaya Hollow", "", {"land"}, {"yavimaya_hollow"}, produces={"C"}, legendary=True)
add("Zagoth Triome", "", {"land"}, {"etb_tapped", "triome", "cycling3"}, produces={"B", "G", "U"}, land_types={"Swamp", "Forest", "Island"})
# MDFC verdadeiro (layout modal_dfc): as duas faces sao jogaveis da mao. Chave = nome completo, como no cache.
add("Agadeem's Awakening // Agadeem, the Undercrypt", "{X}{B}{B}{B}", {"sorcery", "land"}, {"mdfc", "agadeem"}, produces={"B"}, mv=3)

# --- Criaturas -----------------------------------------------------------------
add("Angel of Suffering", "{3}{B}{B}", {"creature"}, {"flying", "angel_suffering"}, 5, 3)
add("Basking Broodscale", "{1}{G}", {"creature"}, {"broodscale"}, 2, 2, subtypes={"Eldrazi", "Lizard"})
add("Bramble Familiar // Fetch Quest", "{1}{G}", {"creature", "adventure"}, {"bramble"}, 2, 2, subtypes={"Elemental", "Raccoon"})
add("Cankerbloom", "{1}{G}", {"creature"}, {"cankerbloom"}, 3, 2)
add("Cold-Eyed Selkie", "{1}{G/U}{G/U}", {"creature"}, {"selkie"}, 1, 1)
add("Danny Pink", "{3}{U}", {"creature"}, {"danny_pink", "mentor"}, 4, 3, legendary=True, subtypes={"Human", "Soldier", "Advisor"})
add("Deepmuck Desperado", "{2}{U}", {"creature"}, {"deepmuck"}, 2, 4)
add("Evolution Witness", "{2}{G}", {"creature"}, {"evo_witness"}, 2, 1, subtypes={"Elf", "Shaman", "Mutant"})
add("Fathom Mage", "{2}{G}{U}", {"creature"}, {"evolve", "fathom_mage"}, 1, 1)
add("Freestrider Lookout", "{2}{G}", {"creature"}, {"freestrider", "reach"}, 3, 3)
add("Generous Patron", "{2}{G}", {"creature"}, {"generous_patron"}, 1, 4, subtypes={"Elf", "Advisor"})
add("Glen Elendra Archmage", "{3}{U}", {"creature"}, {"flying", "persist", "glen_elendra"}, 2, 2)
add("Gyre Sage", "{1}{G}", {"creature"}, {"evolve", "gyre_sage"}, 1, 2, subtypes={"Elf", "Druid"})
add("Herd Baloth", "{3}{G}{G}", {"creature"}, {"herd_baloth"}, 4, 4)
add("Icetill Explorer", "{2}{G}{G}", {"creature"}, {"icetill"}, 2, 4, subtypes={"Insect", "Scout"})
add("Kami of Whispered Hopes", "{2}{G}", {"creature"}, {"kami"}, 1, 1)
add("Kodama of the West Tree", "{2}{G}", {"creature"}, {"kodama", "reach"}, 3, 3, legendary=True)
add("Kozilek, Butcher of Truth", "{10}", {"creature"}, {"kozilek", "annihilator"}, 12, 12, legendary=True)
add("Mirelurk Queen", "{4}{U}", {"creature"}, {"mirelurk_queen", "vigilance"}, 4, 4, subtypes={"Crab", "Mutant"})
add("Muldrotha, the Gravetide", "{3}{B}{G}{U}", {"creature"}, {"muldrotha"}, 6, 6, legendary=True)
add("Ouroboroid", "{2}{G}{G}", {"creature"}, {"ouroboroid"}, 1, 3)
add("Pollywog Prodigy", "{1}{U}", {"creature"}, {"evolve", "pollywog"}, 1, 3)
add("Rampant Frogantua", "{2}{G}", {"creature"}, {"frogantua", "trample"}, 3, 3)
add("Ruin Crab", "{U}", {"creature"}, {"ruin_crab"}, 0, 3, subtypes={"Crab"})
add("Six", "{2}{G}", {"creature"}, {"six", "reach"}, 2, 4, legendary=True)
add("Syr Konrad, the Grim", "{3}{B}{B}", {"creature"}, {"syr_konrad"}, 5, 4, legendary=True)
add("The Gitrog Monster", "{3}{B}{G}", {"creature"}, {"gitrog", "deathtouch"}, 6, 6, legendary=True)
add("Undead Alchemist", "{3}{U}", {"creature"}, {"undead_alchemist"}, 4, 2, subtypes={"Zombie"})
add("Walking Ballista", "{X}{X}", {"artifact", "creature"}, {"ballista"}, 0, 0)
add("Winding Constrictor", "{B}{G}", {"creature"}, {"constrictor"}, 2, 3)
add("Zellix, Sanity Flayer", "{2}{U}", {"creature"}, {"zellix"}, 2, 3, legendary=True)

# --- Artefatos / encantamentos / planeswalker --------------------------------------
add("Agatha's Soul Cauldron", "{2}", {"artifact"}, {"cauldron"}, legendary=True)
add("Altar of Dementia", "{2}", {"artifact"}, {"altar_dementia"})
add("Altar of the Brood", "{1}", {"artifact"}, {"altar_brood"})
add("Bloodchief Ascension", "{B}", {"enchantment"}, {"ascension"})
add("Hardened Scales", "{G}", {"enchantment"}, {"scales"})
add("Hedge Shredder", "{2}{G}{G}", {"artifact", "vehicle"}, {"hedge_shredder"}, 5, 5)
add("Hollowmurk Siege", "{B}{G}", {"enchantment"}, {"hollowmurk"})
add("Memory Erosion", "{1}{U}{U}", {"enchantment"}, {"memory_erosion"})
add("Mesmeric Orb", "{2}", {"artifact"}, {"orb"})
add("Mindcrank", "{2}", {"artifact"}, {"mindcrank"})
add("Palantír of Orthanc", "{3}", {"artifact"}, {"palantir"}, legendary=True)
add("Psychic Corrosion", "{2}{U}", {"enchantment"}, {"psychic_corrosion"})
add("Sol Ring", "{1}", {"artifact"}, {"sol_ring"})
add("Soul-Guide Lantern", "{1}", {"artifact"}, {"lantern"})
add("Swiftfoot Boots", "{2}", {"artifact", "equipment"}, {"boots"})
add("The Great Henge", "{7}{G}{G}", {"artifact"}, {"henge"}, legendary=True)
add("Ashiok, Dream Render", "{1}{U/B}{U/B}", {"planeswalker"}, {"ashiok"}, legendary=True)

# --- Instantaneas / feiticos -------------------------------------------------------
add("An Offer You Can't Refuse", "{U}", {"instant"}, {"counter", "offer"})
add("Arcane Denial", "{1}{U}", {"instant"}, {"counter", "arcane_denial"})
add("Didn't Say Please", "{1}{U}{U}", {"instant"}, {"counter", "didnt_say_please"})
add("Fierce Guardianship", "{2}{U}", {"instant"}, {"counter", "fierce_guardianship"})
add("Heroic Intervention", "{1}{G}", {"instant"}, {"protect", "heroic_intervention"})
add("Negate", "{1}{U}", {"instant"}, {"counter", "negate"})
add("Nature's Lore", "{1}{G}", {"sorcery"}, {"ramp_forest", "natures_lore"})
add("Nuclear Fallout", "{X}{B}{B}", {"sorcery"}, {"wipe", "nuclear_fallout"})
add("Repulsive Mutation", "{X}{G}{U}", {"instant"}, {"repulsive_mutation"})
add("Smuggler's Surprise", "{G}", {"instant"}, {"smugglers_surprise"})
add("Tear Asunder", "{1}{G}", {"instant"}, {"tear_asunder"})
add("Three Visits", "{1}{G}", {"sorcery"}, {"ramp_forest", "three_visits"})
add("Toxic Deluge", "{2}{B}", {"sorcery"}, {"wipe", "toxic_deluge"})
add("V.A.T.S.", "{2}{B}{B}", {"instant"}, {"vats"})
add("Wave Goodbye", "{2}{U}{U}", {"sorcery"}, {"wipe", "wave_goodbye"})

# --- Candidatas (pacote de 5 trocas + Master of Lake-town; ver candidatas-pos-eoe.md) — so' entram na biblioteca por `SWAPS` ---------------------
add("Evolution Sage", "{2}{G}", {"creature"}, {"evo_sage"}, 3, 2, subtypes={"Elf", "Druid"})
add("Karn's Bastion", "", {"land"}, {"karns_bastion"}, produces={"C"})
add("Bruvac the Grandiloquent", "{2}{U}", {"creature"}, {"bruvac"}, 1, 4, legendary=True, subtypes={"Human", "Advisor"})
add("The Master of Lake-town", "{1}{B}{B}", {"creature"}, {"master", "deathtouch"}, 3, 2, legendary=True, subtypes={"Human", "Advisor"})
add("Garruk's Uprising", "{2}{G}", {"enchantment"}, {"garruk"})
add("Opulent Palace", "", {"land"}, {"etb_tapped", "palace"}, produces={"B", "G", "U"})
add("Jace, Wielder of Mysteries", "{1}{U}{U}{U}", {"planeswalker"}, {"jace_wom"}, legendary=True)      # candidata de 2026-10-07 (oraculo ao vivo: resultados-ab/2026-10-07-jace-no-lugar-do-kozilek)
add("Riverchurn Monument", "{1}{U}", {"artifact"}, {"riverchurn"})      # candidata de 2026-10-07 (oraculo ao vivo: resultados-ab/2026-10-07-riverchurn-monument)
add("Agent Frank Horrigan", "{5}{B}{G}", {"creature"}, {"horrigan", "trample"}, 8, 6, legendary=True, subtypes={"Mutant", "Warrior"})      # candidata de 2026-10-07 (resultados-ab/2026-10-07-comparacao-stefano)
add("The Master, Transcendent", "{1}{B}{G}{U}", {"artifact", "creature"}, {"master_t"}, 2, 4, legendary=True, subtypes={"Mutant"})        # candidata de 2026-10-07 (resultados-ab/2026-10-07-comparacao-stefano)
add("Fractured Sanity", "{U}{U}{U}", {"sorcery"}, {"fractured_sanity"})        # candidatas de 2026-10-07 (lista do Stefano): resultados-ab/2026-10-07-candidatas-stefano-2
add("Screeching Scorchbeast", "{4}{B}{B}", {"creature"}, {"scorchbeast", "flying", "menace"}, 5, 5, subtypes={"Bat", "Mutant"})
add("Inexorable Tide", "{3}{U}{U}", {"enchantment"}, {"inex_tide"})
add("Branching Evolution", "{2}{G}", {"enchantment"}, {"branching_evo"})
add("Loading Zone", "{3}{G}", {"enchantment"}, {"loading_zone"})
add("The Earth Crystal", "{2}{G}{G}", {"artifact"}, {"earth_crystal"}, legendary=True)
add("Atomize", "{2}{B}{G}", {"instant"}, {"atomize"})      # candidatas de 2026-10-08 (pedido do usuario): resultados-ab/2026-10-08-cinco-entradas-remocao
add("Casualties of War", "{2}{B}{B}{G}{G}", {"sorcery"}, {"casualties"})
add("Assassin's Trophy", "{B}{G}", {"instant"}, {"trophy"})
add("Opponent Creature Card", "", {"creature"}, {"opp_card"}, 3, 3, subtypes={"Mutant"})   # ficticia: a carta de criatura de oponente que a Master levou (corpo 3/3 generico; volta ao cemiterio dele)

# --- Fichas -----------------------------------------------------------------------
add("Horror Token", "", {"creature"}, {"token"}, 1, 1, token=True, subtypes={"Horror"})
add("Zombie Token", "", {"creature"}, {"token"}, 2, 2, token=True, subtypes={"Zombie"})
add("Zombie Mutant Token", "", {"creature"}, {"token"}, 2, 2, token=True, subtypes={"Zombie", "Mutant"})
add("Beast Token", "", {"creature"}, {"token"}, 4, 4, token=True, subtypes={"Beast"})
add("Eldrazi Spawn Token", "", {"creature"}, {"token", "spawn"}, 0, 1, token=True, subtypes={"Eldrazi", "Spawn"})
add("Construct Token", "", {"artifact", "creature"}, {"token", "construct"}, 0, 0, token=True, subtypes={"Construct"})
add("Treasure Token", "", {"artifact"}, {"token", "treasure"}, token=True)
add("Fractal Token", "", {"creature"}, {"token"}, 0, 0, token=True)


# =========================================================
# ESTADO
# =========================================================

@dataclass
class Permanent:
    card: Card
    uid: int = 0
    tapped: bool = False
    counters: int = 0                 # contadores +1/+1
    ctr: dict = field(default_factory=dict)   # outros contadores: lore, quest, influence, loyalty, minus1, charge
    entered_turn: int = 0
    is_token: bool = False
    temp_power: int = 0               # "ate o fim do turno"
    temp_trample: bool = False
    attached_to: Optional[int] = None  # uid da criatura equipada (Swiftfoot Boots)
    copy_of: Optional[str] = None      # Shifting Woodland: nome da carta copiada ate o fim do turno
    crewed: bool = False               # Hedge Shredder virou criatura neste turno
    last_counter_turn: int = -1        # Danny Pink: "primeira vez a cada turno" por criatura
    used_ability_turn: int = -1        # ativadas "uma vez por turno" (Muldrotha etc. nao usam)
    level: int = 0
    exhausted: bool = False
    attacked_turn_id: int = -1         # Horrigan: "indestructible as long as it attacked this turn"
    base_pt: Optional[tuple] = None    # The Master, Transcendent: "base power and toughness 3/3" (sobrepoe CDA, ruling 2024-03-08)
    mutant: bool = False               # The Master: "It's a green Mutant ... It loses its other colors and creature types"
    owner_idx: int = 0                 # Opponent Creature Card: de qual oponente veio (volta ao cemiterio dele)
    warped: bool = False               # Loading Zone conjurada com Warp {G}: exila no proximo end step


@dataclass
class Opp:
    idx: int
    life: int = OPP_START_LIFE
    library: list = field(default_factory=list)      # 'L' terreno, 'C' criatura, 'N' outra
    graveyard: list = field(default_factory=list)    # tipos
    rad: int = 0
    lands: int = 0
    tapped_last_turn: int = 0
    eliminated: bool = False
    elim_turn: Optional[int] = None
    elim_reason: str = ""
    cmd_damage: int = 0
    lost_life_this_turn: int = 0
    spells_total: int = 0
    turns_taken: int = 0
    hand_size: int = OPP_HAND_START
    pending_denial_draw: int = 0                      # Arcane Denial: pode comprar ate 2 no proximo upkeep


@dataclass
class GameState:
    turn: int = 0
    turn_id: int = 0                  # +1 a cada turno de QUALQUER jogador (meu e dos oponentes): 'once each turn' / 'first time each turn' contam por aqui
    rng: Optional[random.Random] = None
    on_play: bool = True
    library: list = field(default_factory=list)
    hand: list = field(default_factory=list)
    graveyard: list = field(default_factory=list)
    exile: list = field(default_factory=list)
    adventure_exile: list = field(default_factory=list)     # Fetch Quest conjurada: a criatura pode ser conjurada do exilio
    battlefield: list = field(default_factory=list)
    opps: list = field(default_factory=list)
    next_uid: int = 1
    mulligans: int = 0

    life: int = 40
    rad: int = 0
    commander_in_cz: bool = True
    commander_cast_count: int = 0
    commander_uid: Optional[int] = None
    commander_first_cast_turn: Optional[int] = None
    mothman_attacks_total: int = 0

    # turno corrente
    lands_played_this_turn: int = 0
    mana_floating: int = 0
    tapped_land_this_turn: Optional[int] = None
    pool: dict = field(default_factory=dict)               # mana flutuante da fase corrente {cor: n}
    cauldron_exiled: list = field(default_factory=list)    # cartas de criatura exiladas com a Agatha's Soul Cauldron
    muldrotha_used: list = field(default_factory=list)     # tipos ja jogados do cemiterio neste turno
    crime_this_turn: dict = field(default_factory=dict)    # {'deepmuck': bool, 'freestrider': bool}
    queen_triggered_this_turn: bool = False
    terrasymbiosis_used: bool = False
    pending_modes: Optional[tuple] = None
    hollowmurk_triggered_this_turn: bool = False
    spells_cast_this_turn: int = 0
    attackers_this_turn: list = field(default_factory=list)
    opp_lost_life_this_turn: bool = False

    # modos
    interaction_rng: Optional[random.Random] = None
    opp_rngs: list = field(default_factory=list)
    proxy_rng: Optional[random.Random] = None
    ghost: bool = False
    verbose: bool = False
    log: list = field(default_factory=list)

    # fim de jogo
    decked: bool = False
    decked_turn: Optional[int] = None
    died_life: bool = False
    game_over: bool = False
    combo_win: Optional[str] = None
    table_cleared_turn: Optional[int] = None
    first_opp_elim_turn: Optional[int] = None

    # ---- metricas (todas numericas, lidas pelo harness) ----
    commander_cast_turn: Optional[int] = None
    mothman_triggers_total: int = 0          # vezes que o gatilho do Mothman resolveu (algum mill de nao-terreno)
    mothman_x_total: int = 0                 # soma dos X
    mothman_counters_placed_total: int = 0   # contadores +1/+1 efetivamente postos pelo gatilho
    mothman_trigger_my_mill: int = 0
    mothman_trigger_opp_mill: int = 0
    mill_events_total: int = 0
    cards_milled_self_total: int = 0
    cards_milled_opp_total: int = 0
    nonland_milled_self_total: int = 0
    nonland_milled_opp_total: int = 0
    rad_triggers_self: int = 0
    rad_counters_given_opp_total: int = 0
    rad_counters_got_self_total: int = 0
    rad_life_lost_self_total: int = 0
    rad_life_lost_opp_total: int = 0
    counters_placed_total: int = 0           # contadores +1/+1 no total (qualquer fonte)
    counter_events_total: int = 0
    proliferates_total: int = 0
    cards_drawn_extra: int = 0
    draws_total: int = 0
    interaction_plays: int = 0
    atomize_casts: int = 0
    casualties_casts: int = 0
    trophy_casts: int = 0
    trophy_lands_given: int = 0
    counterspells_cast: int = 0
    recursion_events_total: int = 0
    ramp_pieces_in_play: int = 0
    finisher_resolved_total: int = 0
    first_finisher_turn: Optional[int] = None
    tokens_created: int = 0
    horror_tokens_total: int = 0
    zombie_tokens_total: int = 0
    konrad_pings_total: int = 0
    gitrog_draws_total: int = 0
    hedge_lands_total: int = 0
    kodama_lands_total: int = 0
    landfall_events_total: int = 0
    lands_entered_total: int = 0
    crimes_total: int = 0
    deepmuck_triggers: int = 0
    freestrider_triggers: int = 0
    cauldron_exiles_total: int = 0
    fetches_cracked_total: int = 0
    fetch_no_target_total: int = 0
    kozilek_shuffles_total: int = 0
    kozilek_cast_turn: Optional[int] = None
    library_min: int = 99
    library_at_end: int = 0
    turn_library_emptied: Optional[int] = None
    life_min: int = 40
    commander_dmg_total: int = 0
    proxy_damage_total: int = 0
    opps_eliminated_total: int = 0
    opps_decked_total: int = 0
    opps_burned_total: int = 0
    opps_cmd_total: int = 0
    opp_cards_milled_by_turn: dict = field(default_factory=dict)
    mothman_power_turn: dict = field(default_factory=dict)
    max_creature_power: int = 0
    max_creatures_in_play: int = 0
    creature_count_by_turn: dict = field(default_factory=dict)
    counters_on_board_by_turn: dict = field(default_factory=dict)
    mana_by_turn: dict = field(default_factory=dict)
    lands_in_play_by_turn: dict = field(default_factory=dict)
    cards_in_hand_by_turn: dict = field(default_factory=dict)
    library_by_turn: dict = field(default_factory=dict)
    tapped_land_first_plays_total: int = 0
    tapped_land_skipped_for_play_total: int = 0
    orb_mills_total: int = 0
    ascension_loops: int = 0
    palantir_draws: int = 0
    palantir_mills: int = 0
    palantir_life_loss_total: int = 0
    altar_dementia_sacs: int = 0
    altar_brood_mills: int = 0
    jace_plus_uses: int = 0                       # Jace +1 (alvo mila 2, depois compro)
    jace_plus_self: int = 0                       # ... das quais mirando EU (biblioteca <= 2: a compra seguinte e' vitoria)
    jace_minus8_uses: int = 0
    jace_draws: int = 0
    jace_wins: int = 0                            # partidas vencidas por comprar com a biblioteca vazia (estatico) ou pelo -8
    jace_win_turn: Optional[int] = None
    jace_win_T8: int = 0
    jace_win_T10: int = 0
    jace_removed: int = 0                         # sensibilidade JACE_REMOVAL_PROB
    riverchurn_tap_activations: int = 0
    riverchurn_exhaust_activations: int = 0
    riverchurn_exhaust_cards_opp: int = 0         # cartas milladas dos oponentes pelo Exhaust (soma dos cemiterios no momento)
    riverchurn_exhaust_lethal: int = 0            # oponentes cujo cemiterio >= biblioteca quando o Exhaust foi ativado
    riverchurn_exhaust_turn: Optional[int] = None
    horrigan_enter_turn: Optional[int] = None     # turno em que o Horrigan entrou pela 1a vez (indicadores ate' T6..T8)
    horrigan_etb_prolifs: int = 0
    horrigan_attack_prolifs: int = 0
    horrigan_attacks: int = 0
    horrigan_attack_damage: int = 0
    master_enter_turn: Optional[int] = None
    master_activations: int = 0
    master_act_mine: int = 0                      # alvo: criatura MINHA milada neste turno
    master_act_opp: int = 0                       # alvo: criatura de OPONENTE milada neste turno (corpo generico 3/3)
    master_act_on_opp_phase: int = 0
    master_etb_rad: int = 0
    master_no_target_checks: int = 0              # varreduras da habilidade sem alvo (Master pronta, nada milado)
    master_names: dict = field(default_factory=dict)
    milled_mine: list = field(default_factory=list)            # [(nome, turn_id)]: criaturas MINHAS milladas (alvo legal da Master no mesmo turno)
    milled_opp_creatures: dict = field(default_factory=dict)   # {idx: (turn_id, n)}: criaturas milladas do oponente neste turn_id
    prolif_by_source: dict = field(default_factory=dict)
    fractured_casts: int = 0
    fractured_cycles: int = 0
    scorch_enter_turn: Optional[int] = None
    scorch_attacks: int = 0
    scorch_rad_self: int = 0
    scorch_token_events: int = 0
    scorch_tokens: int = 0
    scorch_skipped: int = 0
    scorch_used: dict = field(default_factory=dict)            # uid -> turn_id em que criou os Zumbis ("only once each turn")
    tide_enter_turn: Optional[int] = None
    tide_triggers: int = 0
    branching_enter_turn: Optional[int] = None
    loading_enter_turn: Optional[int] = None
    crystal_enter_turn: Optional[int] = None
    crystal_activations: int = 0
    crystal_counters: int = 0
    crystal_discount_total: int = 0
    warp_casts: int = 0
    warp_exiled: int = 0
    warp_recasts: int = 0
    warp_exile: list = field(default_factory=list)             # [(nome, turno em que foi exilada)]: pode ser conjurada do exilio em turno posterior
    prolif_counters_by_source: dict = field(default_factory=dict)
    prolif_rad_by_source: dict = field(default_factory=dict)
    riverchurn_enter_turn: Optional[int] = None   # turno em que o Monument entrou em campo pela 1a vez (indicadores ate' T3..T6)
    riverchurn_tap_cards_opp: int = 0
    riverchurn_exhaust_ascension: int = 0         # ativacoes do Exhaust com a Bloodchief Ascension armada (3+ marcadores): cada carta milada tira 2 de vida
    memory_erosion_mills: int = 0
    psychic_corrosion_mills: int = 0
    ruin_crab_mills: int = 0
    payoff_first_casts: int = 0       # vezes em que um payoff de landfall foi conjurado ANTES do terreno do turno (LANDFALL_PAYOFF_FIRST)
    zellix_activations: int = 0
    minamo_untaps: int = 0
    shifting_woodland_copies: int = 0
    saga_chapters: int = 0
    adventure_casts: int = 0
    muldrotha_plays: int = 0
    six_retraces: int = 0
    icetill_replays: int = 0
    persist_returns: int = 0
    persist_zero_deaths: int = 0
    combo_loops: int = 0
    wipes_cast: int = 0
    pending_denial_me: int = 0               # Arcane Denial: "You draw a card at the beginning of the next turn's upkeep"
    konrad_activations: int = 0
    zellix_minamo_second: int = 0
    cauldron_exiles_opp: int = 0
    woodland_copy_as: dict = field(default_factory=dict)
    boots_equips: int = 0
    adapt_total: int = 0
    cankerbloom_prolif: int = 0
    channel_total: int = 0
    triome_cycles: int = 0
    grove_sacs: int = 0
    strip_mine_uses: int = 0
    lantern_draws: int = 0
    ashiok_uses: int = 0
    ballista_pumps: int = 0
    construct_tokens: int = 0
    konrad_graveyard_leave_pings: int = 0
    casts_by_card: dict = field(default_factory=dict)           # instrumentacao: quantas vezes cada carta foi conjurada
    draws_by_source: dict = field(default_factory=dict)         # instrumentacao: de onde vieram as compras
    self_mill_by_source: dict = field(default_factory=dict)     # instrumentacao: de onde vieram os mills na MINHA biblioteca
    opp_mill_by_source: dict = field(default_factory=dict)
    orb_untap_triggers: int = 0
    self_mill_blocked_total: int = 0         # mills voluntarios que a guarda de biblioteca impediu
    cauldron_counters_total: int = 0
    ballista_pings_total: int = 0
    altar_loop_iters: int = 0
    mana_spent_total: int = 0
    opp_turns_total: int = 0
    opp_spells_total: int = 0
    opp_spells_countered_total: int = 0
    opp_noncreature_spells_total: int = 0
    pollywog_draws: int = 0
    memory_erosion_events: int = 0
    prox_mana_wasted_total: int = 0
    # modo resiliencia
    konrad_batch: bool = False
    cleared_T6: int = 0                      # a mesa inteira (3 oponentes) eliminada ate o turno N (indicadores 0/1 pro A/B)
    cleared_T7: int = 0
    cleared_T8: int = 0
    cleared_T9: int = 0
    cleared_T10: int = 0
    first_elim_T6: int = 0
    first_elim_T8: int = 0
    self_lost: int = 0                       # eu perdi (decado ou vida <= 0)
    smart_artifact_wipes_total: int = 0
    smart_enchantment_wipes_total: int = 0
    smart_graveyard_snipes_total: int = 0
    smart_discards_total: int = 0
    smart_attack_damage_total: int = 0
    wiped_this_round: bool = False
    graveyard_wipe_used: bool = False
    angel_prevented_total: int = 0
    regenerations_used: int = 0
    protections_by_kind: dict = field(default_factory=dict)
    commander_countered_total: int = 0
    smart_removals_total: int = 0
    smart_wipes_total: int = 0
    smart_counters_total: int = 0
    smart_graveyard_hate_total: int = 0
    smart_attacks_taken_total: int = 0
    protection_used_total: int = 0


def new_uid(state: GameState) -> int:
    u = state.next_uid
    state.next_uid += 1
    return u


def mk_perm(state: GameState, name: str, is_token: bool = False) -> Permanent:
    return Permanent(card=CARD_DB[name], uid=new_uid(state), entered_turn=state.turn, is_token=is_token or CARD_DB[name].token)


def find_perm(state: GameState, uid) -> Optional[Permanent]:
    return next((p for p in state.battlefield if p.uid == uid), None)


def perms_named(state: GameState, name: str) -> list:
    return [p for p in state.battlefield if eff_name(p) == name]


def has_perm(state: GameState, name: str) -> bool:
    return any(eff_name(p) == name for p in state.battlefield)


def count_named(state: GameState, name: str) -> int:
    return sum(1 for p in state.battlefield if eff_name(p) == name)


def has_tag_perm(state: GameState, tag: str) -> list:
    return [p for p in state.battlefield if tag in eff_card(p).tags]


def eff_name(p: Permanent) -> str:
    return p.copy_of or p.card.name


def eff_card(p: Permanent) -> Card:
    return CARD_DB[p.copy_of] if p.copy_of else p.card


def is_land_perm(p: Permanent) -> bool:
    return "land" in p.card.types


def is_creature(p: Permanent) -> bool:
    c = eff_card(p)
    if "creature" in c.types:
        return True
    if "vehicle" in c.types and p.crewed:
        return True
    if p.copy_of and "creature" in CARD_DB[p.copy_of].types:
        return True
    return False


def creatures(state: GameState) -> list:
    return [p for p in state.battlefield if is_creature(p)]


def is_artifact(p: Permanent) -> bool:
    return "artifact" in eff_card(p).types


def lands_in_play(state: GameState) -> list:
    return [p for p in state.battlefield if "land" in p.card.types]


def n_lands(state: GameState) -> int:
    return sum(1 for p in state.battlefield if "land" in p.card.types)


def is_legendary(p: Permanent) -> bool:
    return eff_card(p).legendary


def equipped_by(state: GameState, p: Permanent) -> list:
    return [q for q in state.battlefield if "equipment" in q.card.types and q.attached_to == p.uid]


def is_modified(state: GameState, p: Permanent) -> bool:
    """Kodama (ruling 2022-02-18): criatura modificada = com contador de QUALQUER tipo, equipada (Equipamento de qualquer jogador) ou com Aura sua."""
    return p.counters > 0 or any(v > 0 for v in p.ctr.values()) or bool(equipped_by(state, p))


def players_lost(state: GameState) -> int:
    return sum(1 for o in state.opps if o.eliminated) + (1 if state.died_life or state.decked else 0)


def perm_subtypes(p: Permanent):
    """Subtipos de criatura do permanente: a Master, Transcendent troca todos por Mutant."""
    return {"Mutant"} if p.mutant else eff_card(p).subtypes


def power(state: GameState, p: Permanent) -> int:
    c = eff_card(p)
    m1 = p.ctr.get("minus1", 0)
    if p.base_pt is not None:
        return max(0, p.base_pt[0] + p.counters + p.temp_power - m1)
    if "construct" in c.tags:
        base = sum(1 for q in state.battlefield if is_artifact(q))
        return max(0, base + p.counters + p.temp_power - m1)
    if "frogantua" in c.tags:
        return max(0, c.power + 10 * players_lost(state) + p.counters + p.temp_power - m1)
    return max(0, c.power + p.counters + p.temp_power - m1)


def toughness(state: GameState, p: Permanent) -> int:
    c = eff_card(p)
    m1 = p.ctr.get("minus1", 0)
    if p.base_pt is not None:
        return max(0, p.base_pt[1] + p.counters - m1)
    if "construct" in c.tags:
        base = sum(1 for q in state.battlefield if is_artifact(q))
        return max(0, base + p.counters - m1)
    if "frogantua" in c.tags:
        return max(0, c.toughness + 10 * players_lost(state) + p.counters - m1)
    return max(0, c.toughness + p.counters - m1)


def can_attack(state: GameState, p: Permanent) -> bool:
    if not is_creature(p) or p.tapped:
        return False
    if p.entered_turn == state.turn and not has_haste(state, p):
        return False
    c = eff_card(p)
    if "defender" in c.tags:
        return False
    return True


def has_haste(state: GameState, p: Permanent) -> bool:
    return any(q.card.name == "Swiftfoot Boots" for q in equipped_by(state, p))


def has_trample(state: GameState, p: Permanent) -> bool:
    c = eff_card(p)
    if "trample" in c.tags or p.temp_trample:
        return True
    if has_perm(state, "Kodama of the West Tree") and is_modified(state, p):
        return True
    if has_perm(state, "Garruk's Uprising"):
        return True
    return False


def has_flying(p: Permanent) -> bool:
    return "flying" in eff_card(p).tags


def mk_log(state: GameState, msg: str):
    if state.verbose:
        state.log.append(f"T{state.turn}: {msg}")


# =========================================================
# MODELO DE MANA (pip a pip, correspondencia exata das cores)
# =========================================================
ANY_BGU = frozenset({"B", "G", "U"})


@dataclass
class Src:
    perm: Optional[Permanent]
    colors: frozenset
    amount: int = 1
    bundle: bool = False        # Kami: X mana de UMA cor
    life: int = 0               # vida paga ao tocar (Waterlogged Grove)
    gain: int = 0               # vida ganha (The Great Henge)
    sac: bool = False           # uso unico (Eldrazi Spawn, Treasure)
    rank: int = 0               # menor = gasta primeiro (menos flexivel)
    plaza: bool = False


def _src_rank(colors, amount, sac, creature):
    n = len(colors - {"C"})
    r = n * 10 + (0 if "C" in colors and n == 0 else 0)
    if sac:
        r += 50
    if creature:
        r -= 5            # dorks primeiro (raramente atacam)
    if amount > 1:
        r -= 3
    return r


def _tapped_unavailable(state, p):
    return p.tapped


def legendary_colors(state: GameState) -> frozenset:
    """Plaza of Heroes, 3a habilidade: 'Add one mana of any color among legendary permanents you control.' Cor = simbolos de mana no custo (pips; hibrido conta as duas)
    de cada permanente lendario meu (terrenos lendarios sao incolores; ficha nao e' lendaria)."""
    cols = set()
    for p in state.battlefield:
        c = eff_card(p)
        if not c.legendary:
            continue
        for pip in c.pips:
            cols |= (set(pip) & {"B", "G", "U"})
    return frozenset(cols)


def mana_sources(state: GameState, spell: Optional[Card] = None) -> list:
    out = []
    legendary_spell = bool(spell and spell.legendary)
    exiled = state.cauldron_exiled if CAULDRON_ABILITIES_ENABLED else []
    for p in state.battlefield:
        if p.tapped:
            continue
        c = eff_card(p)
        tags = c.tags
        creature = is_creature(p)
        if creature and p.entered_turn == state.turn and not has_haste(state, p) and "land" not in p.card.types:
            sick = True
        elif creature and p.entered_turn == state.turn and "land" in p.card.types and not has_haste(state, p):
            sick = True    # terreno que virou criatura (Shifting Woodland) no turno em que entrou
        else:
            sick = False
        if "land" in p.card.types and p.copy_of is None:
            if "urzas_saga" in tags:
                if p.ctr.get("lore", 0) >= 1:
                    out.append(Src(p, frozenset({"C"}), rank=_src_rank({"C"}, 1, False, False)))
                continue
            if "plaza" in tags:
                cols = {"C"} | (set(ANY_BGU) if legendary_spell else set()) | set(legendary_colors(state))
                out.append(Src(p, frozenset(cols), plaza=True, rank=_src_rank(cols, 1, False, False)))
                continue
            if "waterlogged_grove" in tags:
                out.append(Src(p, frozenset({"G", "U"}), life=1, rank=_src_rank({"G", "U"}, 1, False, False) + 6))
                continue
            if "fetch" in tags:
                continue
            cols = set(c.produces)
            if not cols:
                continue
            out.append(Src(p, frozenset(cols), rank=_src_rank(cols, 1, False, False)))
            continue
        if p.copy_of is not None and "land" in p.card.types:
            # Shifting Woodland copiando uma carta: perde a habilidade de terreno, assume a da copia
            pass
        if sick and creature:
            continue
        if "sol_ring" in tags:
            out.append(Src(p, frozenset({"C"}), amount=2, rank=_src_rank({"C"}, 2, False, False)))
        elif "henge" in tags:
            out.append(Src(p, frozenset({"G"}), amount=2, gain=2, rank=_src_rank({"G"}, 2, False, False)))
        elif "bramble" in tags and creature:
            out.append(Src(p, frozenset({"G"}), rank=_src_rank({"G"}, 1, False, True)))
        elif "gyre_sage" in tags and creature and p.counters > 0:
            out.append(Src(p, frozenset({"G"}), amount=p.counters, rank=_src_rank({"G"}, p.counters, False, True)))
        elif "kami" in tags and creature:
            pw = power(state, p)
            if pw > 0:
                out.append(Src(p, ANY_BGU, amount=pw, bundle=True, rank=_src_rank(ANY_BGU, pw, False, True)))
        elif "spawn" in tags:
            out.append(Src(p, frozenset({"C"}), sac=True, rank=_src_rank({"C"}, 1, True, False)))
        elif "treasure" in tags:
            out.append(Src(p, ANY_BGU, sac=True, rank=_src_rank(ANY_BGU, 1, True, False)))
        # habilidades concedidas pela Agatha's Soul Cauldron (so' ativadas; so' criaturas com +1/+1 e sem doenca de invocacao)
        if exiled and creature and p.counters > 0 and not sick and not any(k in tags for k in ("kami", "gyre_sage", "bramble")):
            if "Kami of Whispered Hopes" in exiled:
                pw = power(state, p)
                if pw > 0:
                    out.append(Src(p, ANY_BGU, amount=pw, bundle=True, rank=_src_rank(ANY_BGU, pw, False, True) + 1))
            elif "Gyre Sage" in exiled:
                out.append(Src(p, frozenset({"G"}), amount=p.counters, rank=_src_rank({"G"}, p.counters, False, True) + 1))
            elif "Bramble Familiar // Fetch Quest" in exiled:
                out.append(Src(p, frozenset({"G"}), rank=_src_rank({"G"}, 1, False, True) + 1))
    out.sort(key=lambda s: (s.rank, s.perm.uid if s.perm else 0))
    return out


def _pool_units(state):
    u = []
    for col in ("C", "B", "G", "U"):
        for _ in range(state.pool.get(col, 0)):
            u.append((None, frozenset({col})))
    return u


def _plan(state: GameState, generic: int, pips: tuple, spell: Optional[Card] = None, srcs: Optional[list] = None):
    """Procura uma atribuicao de unidades de mana que paga `generic` + `pips`. Devolve plano ou None.
    plano = (usadas: list[(Src|None, colors_escolhidas|None, n)], sobra: list de (cor)) — a cor efetiva de cada unidade."""
    if srcs is None:
        srcs = mana_sources(state, spell)
    units = []                       # (src_or_None, colors)
    for col in ("C", "B", "G", "U"):
        for _ in range(state.pool.get(col, 0)):
            units.append((None, frozenset({col})))
    bundles = []
    for s in srcs:
        if s.bundle:
            bundles.append(s)
            continue
        for _ in range(s.amount):
            units.append((s, s.colors))
    # ordem por flexibilidade crescente (pool primeiro)
    order = sorted(range(len(units)), key=lambda i: (0 if units[i][0] is None else 1, len(units[i][1] - {"C"}), units[i][0].rank if units[i][0] else -1, i))
    units = [units[i] for i in order]
    need = list(pips)
    # Kuhn: pips -> unidades
    adj = [[j for j, (_, cols) in enumerate(units) if cols & pip] for pip in need]
    match_u = [-1] * len(units)

    def try_pip(i, seen):
        for j in adj[i]:
            if j in seen:
                continue
            seen.add(j)
            if match_u[j] == -1 or try_pip(match_u[j], seen):
                match_u[j] = i
                return True
        return False
    unmatched_pips = []
    for i in range(len(need)):
        if not try_pip(i, set()):
            unmatched_pips.append(i)
    # bundles cobrem os pips restantes (uma cor por bundle)
    bundle_choice = {}
    leftover_bundle_units = 0
    rem = [need[i] for i in unmatched_pips]
    for b in sorted(bundles, key=lambda s: -s.amount):
        if not rem:
            leftover_bundle_units += b.amount
            bundle_choice[id(b)] = (None, 0)
            continue
        # cor mais pedida entre os pips restantes que o bundle aceita
        cnt = collections.Counter()
        for pip in rem:
            for col in sorted(pip & b.colors):
                cnt[col] += 1
        if not cnt:
            leftover_bundle_units += b.amount
            bundle_choice[id(b)] = (None, 0)
            continue
        col = max(sorted(cnt), key=lambda k: cnt[k])
        used = 0
        newrem = []
        for pip in rem:
            if col in pip and used < b.amount:
                used += 1
            else:
                newrem.append(pip)
        rem = newrem
        leftover_bundle_units += b.amount - used
        bundle_choice[id(b)] = (col, used)
    if rem:
        return None
    free_units = [j for j in range(len(units)) if match_u[j] == -1]
    if len(free_units) + leftover_bundle_units < generic:
        return None
    return units, match_u, free_units, bundles, bundle_choice


def can_pay(state: GameState, generic: int, pips: tuple, spell: Optional[Card] = None) -> bool:
    return _plan(state, generic, pips, spell) is not None


def pay_mana(state: GameState, generic: int, pips: tuple, spell: Optional[Card] = None) -> bool:
    """Paga: toca as fontes escolhidas; unidades extras de fonte multi-mana (Sol Ring, Henge) vao pro `state.pool` (vale ate o fim da fase)."""
    plan = _plan(state, generic, pips, spell)
    if plan is None:
        return False
    units, match_u, free_units, bundles, bundle_choice = plan
    used_src = collections.OrderedDict()   # id(src) -> (src, unidades usadas)
    pool_used = collections.Counter()

    def use(unit_idx):
        src, cols = units[unit_idx]
        if src is None:
            pool_used[next(iter(cols))] += 1
        else:
            if id(src) not in used_src:
                used_src[id(src)] = [src, 0]
            used_src[id(src)][1] += 1
    for j, i in enumerate(match_u):
        if i != -1:
            use(j)
    g = generic
    for j in free_units:
        if g <= 0:
            break
        use(j)
        g -= 1
    # bundles: unidades usadas pelos pips + genericas restantes
    for b in bundles:
        col, used = bundle_choice[id(b)]
        extra = 0
        if g > 0:
            avail = b.amount - used
            extra = min(avail, g)
            g -= extra
        if used + extra > 0:
            used_src[id(b)] = [b, used + extra]
            if used + extra < b.amount:
                state.pool[col or "C"] = state.pool.get(col or "C", 0) + (b.amount - used - extra)
    for col, n in pool_used.items():
        state.pool[col] -= n
    for s, n in used_src.values():
        if s.perm is not None:
            if s.sac:
                _sacrifice_for_mana(state, s.perm)
            else:
                s.perm.tapped = True
        if s.life:
            lose_life_self(state, s.life, "pay_life")
        if s.gain:
            state.life += s.gain
        if not s.bundle and n < s.amount:
            # unidades nao usadas de fonte multi-mana (Sol Ring: segundo {C}; Henge: segundo {G}) ficam no pool
            col = "C" if "C" in s.colors else sorted(s.colors)[0]
            state.pool[col] = state.pool.get(col, 0) + (s.amount - n)
    return True


def _sacrifice_for_mana(state, perm):
    if perm in state.battlefield:
        state.battlefield.remove(perm)
        # Treasure/Spawn tokens deixam de existir; Spawn e' criatura: gatilhos de "dies" (Syr Konrad) -> via creature_leaves
        if "spawn" in perm.card.tags:
            creature_dies(state, perm, sacrificed=True)


def available_mana(state: GameState, spell: Optional[Card] = None) -> int:
    n = sum(state.pool.values())
    for s in mana_sources(state, spell):
        n += s.amount
    return n


def max_x(state: GameState, generic: int, pips: tuple, mult: int = 1, spell: Optional[Card] = None, cap: int = 20) -> int:
    lo = 0
    for x in range(0, cap + 1):
        if can_pay(state, generic + x * mult, pips, spell):
            lo = x
        else:
            break
    return lo


# =========================================================
# OPONENTES (so' o que o motor do deck precisa: biblioteca, vida, rad, graveyard por tipo)
# =========================================================

def make_opp(seed: int, idx: int) -> Opp:
    rng = random.Random(seed * 1_000_003 + idx * 7919 + 13)
    deck = ["L"] * OPP_LANDS_IN_DECK + ["C"] * OPP_CREATURES_IN_DECK + ["N"] * (OPP_DECK_SIZE - OPP_LANDS_IN_DECK - OPP_CREATURES_IN_DECK)
    rng.shuffle(deck)
    o = Opp(idx=idx)
    o.library = deck[OPP_HAND_START:]
    o.hand_size = OPP_HAND_START
    return o


def alive_opps(state: GameState) -> list:
    return [o for o in state.opps if not o.eliminated]


def opp_rng(state: GameState, o: Opp) -> random.Random:
    return state.opp_rngs[o.idx]


def target_available(state: GameState) -> bool:
    """O oponente tem alvo legal pra efeito que mira o tabuleiro dele? (estrutural: tabuleiro de oponente nao e' simulado)."""
    if state.turn < OPP_TARGET_FROM_TURN or not alive_opps(state):
        return False
    return state.proxy_rng.random() < OPP_TARGET_PROB


# =========================================================
# VIDA, COMPRA, CRIME
# =========================================================

def lose_life_self(state: GameState, n: int, reason: str = ""):
    if n <= 0:
        return
    state.life -= n
    state.life_min = min(state.life_min, state.life)
    if state.life <= 0 and not state.died_life:
        state.died_life = True
        state.game_over = True
    # Master of Lake-town: "Whenever a player loses life, that player mills that many cards" (candidata)
    for _ in range(count_named(state, "The Master of Lake-town")):
        if state.game_over:
            break
        mill_event(state, [(0, n)], source="master_of_lake_town")


def lose_life_opp(state: GameState, idx: int, n: int, reason: str = "", combat: bool = False):
    o = state.opps[idx - 1]
    if n <= 0 or o.eliminated:
        return
    o.life -= n
    o.lost_life_this_turn += n
    state.opp_lost_life_this_turn = True
    if reason == "rad":
        state.rad_life_lost_opp_total += n
    # Mindcrank: "Whenever an opponent loses life, that player mills that many cards."  (um gatilho por Mindcrank por evento de perda de vida)
    for _ in range(count_named(state, "Mindcrank")):
        if o.eliminated or state.game_over:
            break
        mill_event(state, [(idx, n)], source="mindcrank")
    for _ in range(count_named(state, "The Master of Lake-town")):
        if o.eliminated or state.game_over:
            break
        mill_event(state, [(idx, n)], source="master_of_lake_town")
    check_opp_elim(state, o)


def check_opp_elim(state: GameState, o: Opp):
    if o.eliminated:
        return
    if o.life <= 0:
        eliminate_opp(state, o, "life")


def eliminate_opp(state: GameState, o: Opp, reason: str):
    if o.eliminated:
        return
    o.eliminated = True
    o.elim_turn = state.turn
    o.elim_reason = reason
    state.opps_eliminated_total += 1
    if reason == "decked":
        state.opps_decked_total += 1
    elif reason == "life":
        state.opps_burned_total += 1
    elif reason == "commander":
        state.opps_cmd_total += 1
    if state.first_opp_elim_turn is None:
        state.first_opp_elim_turn = state.turn
    if all(x.eliminated for x in state.opps):
        state.table_cleared_turn = state.turn
        state.game_over = True


def jace_line(state: GameState) -> bool:
    """Jace em campo e a linha de vitoria por biblioteca vazia ligada (JACE_WIN_LINE)."""
    return JACE_WIN_LINE and JACE_STATIC_ENABLED and has_perm(state, "Jace, Wielder of Mysteries")


def jace_win(state: GameState):
    """Eu venci: os oponentes vivos perdem (`eliminate_opp`, motivo "jace"): a mesa fica limpa neste turno, como nas outras vitorias por combo."""
    state.jace_wins += 1
    if state.jace_win_turn is None:
        state.jace_win_turn = state.turn
    state.combo_win = state.combo_win or "jace"
    for o in list(alive_opps(state)):
        eliminate_opp(state, o, "jace")
    state.game_over = True


OPTIONAL_DRAW_SOURCES = frozenset({"fathom_mage", "selkie", "terrasymbiosis", "lantern", "waterlogged_grove", "cycling"})   # 'you may draw': nao compro com a biblioteca no fim


def draw_cards(state: GameState, n: int, source: str = "normal"):
    if source in OPTIONAL_DRAW_SOURCES and SELF_MILL_GUARD_ENABLED and not jace_line(state):
        n = max(0, min(n, library_budget(state)))
    for _ in range(n):
        if state.game_over:
            return
        if not state.library:
            if JACE_STATIC_ENABLED and has_perm(state, "Jace, Wielder of Mysteries"):
                jace_win(state)                                  # comprar com a biblioteca vazia = vitoria (a compra e' substituida; ruling 2019-05-03)
                return
            state.decked = True
            state.decked_turn = state.turn
            state.game_over = True
            return
        c = state.library.pop(0)
        state.hand.append(c)
        state.draws_total += 1
        state.draws_by_source[source] = state.draws_by_source.get(source, 0) + 1
        if source != "normal":
            state.cards_drawn_extra += 1
        state.library_min = min(state.library_min, len(state.library))
        if not state.library and state.turn_library_emptied is None:
            state.turn_library_emptied = state.turn
        # Psychic Corrosion: "Whenever you draw a card, each opponent mills two cards."
        for _ in range(count_named(state, "Psychic Corrosion")):
            opp_parts = [(o.idx, 2) for o in alive_opps(state)]
            if opp_parts:
                state.psychic_corrosion_mills += 1
                mill_event(state, opp_parts, source="psychic_corrosion")


def commit_crime(state: GameState, source: str = ""):
    """Crime (rulings 2024-04): conjurar/ativar/gatilho que mira oponente, permanente/magia/habilidade de oponente ou carta no cemiterio de oponente.
    Um crime por magia/habilidade. Deepmuck Desperado e Freestrider Lookout disparam 1x por turno cada."""
    state.crimes_total += 1
    if has_perm(state, "Deepmuck Desperado") and not state.crime_this_turn.get("deepmuck"):
        state.crime_this_turn["deepmuck"] = True
        state.deepmuck_triggers += 1
        parts = [(o.idx, 3) for o in alive_opps(state)]
        if parts:
            mill_event(state, parts, source="deepmuck")
    if has_perm(state, "Freestrider Lookout") and not state.crime_this_turn.get("freestrider"):
        state.crime_this_turn["freestrider"] = True
        state.freestrider_triggers += 1
        freestrider_trigger(state)


# =========================================================
# MILL: o ponto unico por onde cartas saem da biblioteca por efeito de mill
# =========================================================

def _opp_take(state: GameState, o: Opp, n: int) -> list:
    k = min(n, len(o.library))
    cards = o.library[:k]
    del o.library[:k]
    o.graveyard.extend(cards)
    return cards


def mill_event(state: GameState, parts: list, source: str = "", before_triggers=None, depth: int = 0):
    """UM evento de mill simultaneo. `parts` = [(jogador, n)], jogador 0 = eu, 1..3 = oponentes. Devolve {jogador: [cartas]}.
    Gatilhos (ordem escolhida por mim; Kozilek por ultimo pra nao embaralhar antes de Hedge Shredder/Gitrog resolverem):
    Hedge Shredder, Gitrog, Mothman, Mirelurk Queen, Zellix, Undead Alchemist, Syr Konrad, Bloodchief Ascension, Kozilek.
    `before_triggers(result)` roda depois das cartas se moverem e antes dos gatilhos (o texto dos rad counters faz a perda de vida/remocao primeiro)."""
    if state.game_over:
        return {}
    depth += 1
    if depth > 60:
        return {}
    result = {}
    nonland_total = 0
    creature_cards = 0
    my_cards = []
    opp_creature_cards = 0
    opp_cards_total = 0
    for pl, n in parts:
        if n <= 0:
            continue
        if pl == 0:
            k = min(n, len(state.library))
            cards = state.library[:k]
            del state.library[:k]
            state.graveyard.extend(cards)
            result[0] = cards
            my_cards = cards
            state.cards_milled_self_total += len(cards)
            state.self_mill_by_source[source] = state.self_mill_by_source.get(source, 0) + len(cards)
            # MDFC com face terreno: na biblioteca/cemiterio so' a frente conta (modal_dfc: Agadeem's Awakening e' FEITICO)
            nl = sum(1 for c in cards if not is_land_card_name(c))
            state.nonland_milled_self_total += nl
            nonland_total += nl
            creature_cards += sum(1 for c in cards if "creature" in CARD_DB[c].types)
            for c in cards:
                if "creature" in CARD_DB[c].types and not CARD_DB[c].token:
                    state.milled_mine.append((c, state.turn_id))
            state.library_min = min(state.library_min, len(state.library))
            if not state.library and state.turn_library_emptied is None and cards:
                state.turn_library_emptied = state.turn
        else:
            o = state.opps[pl - 1]
            if o.eliminated:
                continue
            n = n * (2 ** count_named(state, "Bruvac the Grandiloquent"))       # Bruvac: substituicao, so' oponentes
            cards = _opp_take(state, o, n)
            result[pl] = cards
            state.cards_milled_opp_total += len(cards)
            state.opp_mill_by_source[source] = state.opp_mill_by_source.get(source, 0) + len(cards)
            nl = sum(1 for c in cards if c != "L")
            state.nonland_milled_opp_total += nl
            nonland_total += nl
            cc = sum(1 for c in cards if c == "C")
            creature_cards += cc
            opp_creature_cards += cc
            if cc:
                tid, n0 = state.milled_opp_creatures.get(pl, (-1, 0))
                state.milled_opp_creatures[pl] = (state.turn_id, (n0 if tid == state.turn_id else 0) + cc)
            opp_cards_total += len(cards)
            state.opp_cards_milled_by_turn[state.turn] = state.opp_cards_milled_by_turn.get(state.turn, 0) + len(cards)
    if not result:
        return result
    state.mill_events_total += 1
    my_land_cards = [c for c in my_cards if is_land_card_name(c)]
    if before_triggers is not None:
        before_triggers(result)
        if state.game_over:
            return result
    # --- Hedge Shredder: "Whenever one or more land cards are put into your graveyard from your library, put them onto the battlefield tapped."
    if my_land_cards and has_perm(state, "Hedge Shredder"):
        for lc in list(my_land_cards):
            if lc in state.graveyard:
                state.graveyard.remove(lc)
                state.hedge_lands_total += 1
                put_land_onto_battlefield(state, lc, tapped=True, source="hedge_shredder")
    # --- The Gitrog Monster: "Whenever one or more land cards are put into your graveyard from anywhere, draw a card." (1 gatilho por evento)
    if my_land_cards and has_perm(state, "The Gitrog Monster"):
        state.gitrog_draws_total += 1
        draw_cards(state, 1, source="gitrog")
    if state.game_over:
        return result
    # --- The Wise Mothman
    if nonland_total > 0:
        for _ in range(count_named(state, COMMANDER)):
            mothman_trigger(state, nonland_total, my_mill=(0 in result and any(not is_land_card_name(c) for c in result[0])), opp_mill=any(k != 0 for k in result))
    # --- Mirelurk Queen: "Whenever one or more nonland cards are milled, draw a card, then put a +1/+1 counter on this creature. Once each turn."
    if nonland_total > 0 and not state.queen_triggered_this_turn:
        queens = perms_named(state, "Mirelurk Queen")
        if queens:
            state.queen_triggered_this_turn = True
            draw_cards(state, 1, source="mirelurk_queen")
            place_counters(state, queens[0], 1, source="mirelurk_queen")
    # --- Screeching Scorchbeast: "Whenever one or more nonland cards are milled, you may create that many 2/2 black Zombie Mutant creature tokens. Do this only once each turn." (qualquer jogador;
    #     ruling: "you may" na resolucao: se nao criar, o gatilho volta a disparar; politica: crio quando o evento tem >= SCORCH_MIN_X cartas)
    if nonland_total > 0:
        for sb in perms_named(state, "Screeching Scorchbeast"):
            if state.scorch_used.get(sb.uid) == state.turn_id:
                continue
            if nonland_total >= SCORCH_MIN_X:
                state.scorch_used[sb.uid] = state.turn_id
                state.scorch_token_events += 1
                for _ in range(nonland_total):
                    if state.game_over:
                        break
                    create_token(state, "Zombie Mutant Token")
                    state.scorch_tokens += 1
            else:
                state.scorch_skipped += 1
    # --- Zellix: "Whenever a player mills one or more creature cards, you create a 1/1 black Horror creature token."
    if creature_cards > 0:
        for _ in range(count_named(state, "Zellix, Sanity Flayer")):
            create_token(state, "Horror Token")
            state.horror_tokens_total += 1
    # --- Undead Alchemist: criatura da biblioteca do OPONENTE -> exila e cria Zumbi 2/2 (cada Alchemist, cada carta)
    if opp_creature_cards > 0:
        nalch = count_named(state, "Undead Alchemist")
        if nalch:
            for pl, cards in result.items():
                if pl == 0:
                    continue
                o = state.opps[pl - 1]
                for c in cards:
                    if c == "C":
                        if "C" in o.graveyard:
                            o.graveyard.remove("C")
                        for _ in range(nalch):
                            create_token(state, "Zombie Token")
                            state.zombie_tokens_total += 1
    # --- Syr Konrad: "a creature card is put into a graveyard from anywhere other than the battlefield": 1 dano a cada oponente, por carta
    if creature_cards > 0:
        nk = count_named(state, "Syr Konrad, the Grim")
        for _ in range(nk * creature_cards):
            if state.game_over:
                break
            konrad_ping(state, 1)
    # --- Bloodchief Ascension: carta posta no cemiterio de um OPONENTE, com 3+ marcadores: perde 2, eu ganho 2 (por carta)
    asc = [p for p in perms_named(state, "Bloodchief Ascension") if p.ctr.get("quest", 0) >= 3]
    if asc:
        for pl, cards in result.items():
            if pl == 0 or state.game_over:
                continue
            for _ in cards:
                if state.opps[pl - 1].eliminated or state.game_over:
                    break
                ascension_hit(state, pl)
    # --- Kozilek: "When Kozilek is put into a graveyard from anywhere, its owner shuffles their graveyard into their library." (por ultimo)
    if "Kozilek, Butcher of Truth" in my_cards and KOZILEK_SHUFFLE_ENABLED:
        kozilek_shuffle(state)
    return result


def is_land_card_name(name: str) -> bool:
    c = CARD_DB.get(name)
    if c is None:
        return False
    # carta MDFC (Agadeem's Awakening // Agadeem): no cemiterio/biblioteca so' a FRENTE conta (feiticio) — modal_dfc, ruling 2020
    if "mdfc" in c.tags:
        return False
    return "land" in c.types


def kozilek_shuffle(state: GameState):
    state.kozilek_shuffles_total += 1
    gone = list(state.graveyard)
    state.library.extend(state.graveyard)
    state.graveyard.clear()
    state.rng.shuffle(state.library)
    graveyard_leave(state, gone)          # Syr Konrad: 'a creature card leaves your graveyard'


def konrad_ping(state: GameState, n: int):
    state.konrad_pings_total += 1
    for o in list(alive_opps(state)):
        if state.game_over:
            return
        lose_life_opp(state, o.idx, n, "konrad")


def ascension_hit(state: GameState, pl: int):
    """Carta no cemiterio do oponente `pl` com a Ascension armada: ele perde 2, eu ganho 2. Com Mindcrank/Master of Lake-town isso e' o combo (mill infinito, Spellbook 936-1290)."""
    state.life += 2
    mc = count_named(state, "Mindcrank") + count_named(state, "The Master of Lake-town")
    if mc > 0:
        # Ascension (3+ marcadores) + Mindcrank/Master: cada carta no cemiterio -> perde 2 -> mill 2 (ou 2 por peca) -> ... ciclo que so' termina com a biblioteca vazia
        state.ascension_loops += 1
        state.combo_win = state.combo_win or "ascension_mindcrank"
        o = state.opps[pl - 1]
        k = len(o.library)
        o.graveyard.extend(o.library)
        state.cards_milled_opp_total += k
        state.opp_cards_milled_by_turn[state.turn] = state.opp_cards_milled_by_turn.get(state.turn, 0) + k
        o.library = []
        o.life -= 2 * max(1, k)
        o.lost_life_this_turn += 2 * max(1, k)
        state.opp_lost_life_this_turn = True
        eliminate_opp(state, o, "decked")
        return
    lose_life_opp(state, pl, 2, "ascension")


# =========================================================
# CONTADORES (+1/+1, outros, rad), PROLIFERATE
# =========================================================

def counter_modifiers(state: GameState, perm: Permanent, kind: str):
    """Efeitos de substituicao de contador: devolve (aditivo, multiplicador). O dono do permanente escolhe a ordem (CR 616.1; rulings de Hardened Scales/Kami):
    aditivos ANTES dos multiplicativos, que e' estritamente melhor ou igual: (n + k) * 2^m >= n * 2^m + k."""
    c = eff_card(perm)
    creature = is_creature(perm) or "creature" in c.types
    artcre = creature or is_artifact(perm)
    plus = 0
    mult = 1
    if kind == "+1/+1":
        if creature:
            plus += count_named(state, "Hardened Scales") + count_named(state, "Michelangelo, Weirdness to 11") + count_named(state, "High Score")
        plus += count_named(state, "Kami of Whispered Hopes")                         # "a permanent you control"
        plus += count_named(state, "Doc Samson, Super Psychiatrist") + count_named(state, "Solid Ground")
        if artcre:
            plus += count_named(state, "Winding Constrictor") + count_named(state, "Ozolith, the Shattered Spire")
        if creature:
            mult *= 2 ** (count_named(state, "Corpsejack Menace") + count_named(state, "Loading Zone") + count_named(state, "Primal Vigor") + count_named(state, "Shang-Chi, Martial Mentor")
                           + count_named(state, "Branching Evolution") + count_named(state, "The Earth Crystal"))
        mult *= 2 ** count_named(state, "Doubling Season")
    else:
        if artcre:
            plus += count_named(state, "Winding Constrictor")
        plus += count_named(state, "Doc Samson, Super Psychiatrist")
        mult *= 2 ** count_named(state, "Doubling Season")
        if creature:
            mult *= 2 ** count_named(state, "Loading Zone")
    return plus, mult


def place_counters(state: GameState, perm: Permanent, n: int, kind: str = "+1/+1", source: str = "") -> int:
    """Poe contadores num permanente MEU, passando pelos substituidores (Hardened Scales, Kami, Winding Constrictor, dobradores)."""
    if n <= 0 or perm not in state.battlefield:
        return 0
    plus, mult = counter_modifiers(state, perm, kind)
    total = (n + plus) * mult
    if kind == "+1/+1":
        perm.counters += total
        normalize_counters(perm)
        state.counters_placed_total += total
    else:
        perm.ctr[kind] = perm.ctr.get(kind, 0) + total
    state.counter_events_total += 1
    on_counters_placed(state, perm, total, kind, source)
    return total


def on_counters_placed(state: GameState, perm: Permanent, total: int, kind: str, source: str):
    c = eff_card(perm)
    creature = is_creature(perm)
    # Danny Pink: criaturas minhas tem "primeira vez a cada turno que contadores sao postos nesta criatura: compre"
    if creature and has_perm(state, "Danny Pink") and perm.last_counter_turn != state.turn_id:
        perm.last_counter_turn = state.turn_id
        draw_cards(state, 1, source="danny_pink")
    # Hollowmurk Siege (modo Sultai): "Whenever a counter is put on a creature you control, draw a card. Once each turn."
    if creature and not state.hollowmurk_triggered_this_turn:
        for h in perms_named(state, "Hollowmurk Siege"):
            if h.ctr.get("sultai"):
                state.hollowmurk_triggered_this_turn = True
                draw_cards(state, 1, source="hollowmurk")
                break
    # Terrasymbiosis (candidata): +1/+1 em criatura minha: compre essa quantidade, 1x por turno
    if kind == "+1/+1" and creature and has_perm(state, "Terrasymbiosis") and not state.terrasymbiosis_used:
        state.terrasymbiosis_used = True
        draw_cards(state, total, source="terrasymbiosis")
    if kind != "+1/+1":
        return
    tags = c.tags
    if "fathom_mage" in tags:
        # ruling: dispara UMA VEZ POR CONTADOR (varios contadores ao mesmo tempo = varios gatilhos)
        draw_cards(state, total, source="fathom_mage")
    if "broodscale" in tags:
        create_token(state, "Eldrazi Spawn Token")
    if "herd_baloth" in tags:
        create_token(state, "Beast Token")
    if "evo_witness" in tags:
        evolution_witness_return(state)


def give_rad(state: GameState, idx: int, n: int):
    if n <= 0:
        return
    if idx == 0:
        # Winding Constrictor: "If you would get one or more counters, you get that many plus one of each of those kinds."
        n = n + count_named(state, "Winding Constrictor")
        state.rad += n
        state.rad_counters_got_self_total += n
    else:
        o = state.opps[idx - 1]
        if o.eliminated:
            return
        o.rad += n
        state.rad_counters_given_opp_total += n


def create_token(state: GameState, name: str, tapped: bool = False, counters: int = 0) -> Permanent:
    p = mk_perm(state, name, is_token=True)
    p.tapped = tapped
    state.battlefield.append(p)
    state.tokens_created += 1
    if counters:
        # entra com contadores: substituicao (Scales, Kami, Constrictor...)
        plus, mult = counter_modifiers(state, p, "+1/+1")
        p.counters = (counters + plus) * mult
        state.counters_placed_total += p.counters
    enter_permanent_triggers(state, p, from_cast=False)
    return p


def proliferate(state: GameState, source: str = "", times: int = 1):
    """CR 701.34a: escolho qualquer numero de permanentes e/ou jogadores com contador e dou +1 de cada tipo. Politica: tudo que me ajuda;
    NAO os rad counters PROPRIOS (a menos que SAGE_PROLIFERATE_OWN_RAD), nem lore da Urza's Saga, nem -1/-1 do persist."""
    state.proliferates_total += 1
    state.prolif_by_source[source] = state.prolif_by_source.get(source, 0) + 1
    times = times * (1 + count_named(state, "Tekuthal, Inquiry Dominus"))      # Tekuthal (candidata): "proliferate twice instead"; Horrigan: "proliferate twice" (2 escolhas independentes, ruling 2024-03-08)
    for _ in range(times):
        for p in list(state.battlefield):
            if p not in state.battlefield:
                continue
            if p.counters > 0 and is_creature(p):
                k = place_counters(state, p, 1, source="proliferate")
                state.prolif_counters_by_source[source] = state.prolif_counters_by_source.get(source, 0) + k
            for kind in ("quest", "influence", "loyalty", "charge"):
                if p.ctr.get(kind, 0) > 0:
                    if kind == "loyalty" and "planeswalker" in p.card.types:
                        place_counters(state, p, 1, kind=kind, source="proliferate")
                    elif kind != "loyalty":
                        place_counters(state, p, 1, kind=kind, source="proliferate")
        for o in alive_opps(state):
            if o.rad > 0:
                o.rad += 1
                state.rad_counters_given_opp_total += 1
                state.prolif_rad_by_source[source] = state.prolif_rad_by_source.get(source, 0) + 1
        if SAGE_PROLIFERATE_OWN_RAD and state.rad > 0:
            give_rad(state, 0, 1)


def evolution_witness_return(state: GameState):
    """Evolution Witness: 'return target permanent card from your graveyard to your hand' — melhor carta."""
    perm_cards = [c for c in state.graveyard if any(t in CARD_DB[c].types for t in ("creature", "artifact", "enchantment", "land", "planeswalker")) and not CARD_DB[c].token]
    if not perm_cards:
        return
    best = max(perm_cards, key=lambda c: (graveyard_value(state, c), c))
    state.graveyard.remove(best)
    state.hand.append(best)
    state.recursion_events_total += 1
    graveyard_leave(state, [best])


def graveyard_value(state: GameState, name: str) -> float:
    """Valor de recuperar `name` do cemiterio (recursao): engines > corpos > terrenos."""
    pr = CAST_PRIORITY.get(name)
    if pr is not None:
        return float(pr)
    c = CARD_DB[name]
    if "land" in c.types:
        return 1.0 if n_lands(state) >= 6 else 5.0
    return float(c.mv)


# =========================================================
# TERRENOS: entrada, fetch, busca
# =========================================================

def forests(state: GameState) -> list:
    return [p for p in state.battlefield if "Forest" in p.card.land_types and p.card.name != "Shifting Woodland"]


def land_enters_tapped(state: GameState, name: str, forced_tapped: bool = False) -> bool:
    """Arquetipo de entrada de CADA terreno da lista, conferido no oraculo (Regra 12 de user-standing-rules):
    Bojuka Bog/Zagoth Triome sempre virados; shocks (Breeding Pool, Overgrown Tomb, Watery Grave): pago 2 de vida se a vida permitir (vida e' rastreada);
    Agadeem (MDFC, lado terreno): pago 3 de vida se a vida permitir; slowlands (Morphic Pool, Rejuvenating Springs, Undergrowth Stadium): desvirados com 2+ OPONENTES vivos
    (contagem atual de oponentes, ruling); Shifting Woodland: desvirado so' se ja controlo uma Floresta (subtipo Forest)."""
    c = CARD_DB[name]
    if forced_tapped:
        return True
    tags = c.tags
    if "etb_tapped" in tags:
        return True
    if "shock" in tags:
        return state.life < 10
    if "slow_opp" in tags:
        return len(alive_opps(state)) < 2
    if "shifting_woodland" in tags:
        return not forests(state)
    if "agadeem" in tags:
        return state.life < 20
    return False


def land_cost_life(state: GameState, name: str, tapped: bool) -> int:
    tags = CARD_DB[name].tags
    if "shock" in tags and not tapped:
        return 2
    if "agadeem" in tags and not tapped:
        return 3
    return 0


def put_land_onto_battlefield(state: GameState, name: str, tapped: Optional[bool] = None, source: str = "", forced_tapped: bool = False) -> Permanent:
    """TODO ponto de entrada de terreno passa por aqui (play_land, fetch, ramp, Hedge Shredder, Kodama, Icetill/Muldrotha, Fetch Quest, Freestrider...).
    `tapped=True`/`forced_tapped`: o efeito poe o terreno virado (shock ainda pode pagar 2, mas continua virado: nao paga)."""
    if forced_tapped or tapped is True:
        t = True
    else:
        t = land_enters_tapped(state, name)
    cost = land_cost_life(state, name, t)
    if cost:
        lose_life_self(state, cost, "land_cost")
    p = mk_perm(state, name)
    p.tapped = bool(t)
    state.battlefield.append(p)
    land_enters(state, p, source)
    return p


def land_enters(state: GameState, p: Permanent, source: str = ""):
    state.lands_entered_total += 1
    state.landfall_events_total += 1
    tags = p.card.tags
    if "urzas_saga" in tags:
        saga_add_lore(state, p)
    # Altar of the Brood: "Whenever another permanent you control enters, each opponent mills a card."
    for _ in range(count_named(state, "Altar of the Brood")):
        parts = [(o.idx, 1) for o in alive_opps(state)]
        if parts:
            state.altar_brood_mills += 1
            mill_event(state, parts, source="altar_of_the_brood")
    if "bog" in tags:
        bojuka_bog_etb(state)
    if not LAND_ENTER_TRIGGERS_ALL_ENABLED and source not in ("play",):
        return
    landfall(state)


def landfall(state: GameState):
    # Ruin Crab: "Landfall — Whenever a land you control enters, each opponent mills three cards." (cada Ruin Crab)
    for _ in range(count_named(state, "Ruin Crab")):
        parts = [(o.idx, 3) for o in alive_opps(state)]
        if parts:
            state.ruin_crab_mills += 1
            mill_event(state, parts, source="ruin_crab")
    # Icetill Explorer: "Landfall — mill a card."
    for _ in range(count_named(state, "Icetill Explorer")):
        mill_event(state, [(0, 1)], source="icetill")
    # Evolution Sage (candidata): "Landfall — proliferate."
    for _ in range(count_named(state, "Evolution Sage")):
        proliferate(state, "evolution_sage")
    # Mole Man / Oko etc. nao estao na lista base


def search_land(state: GameState, predicate, prefer_untapped=True):
    """Procura na biblioteca um terreno que satisfaz `predicate(name)`. Devolve nome ou None (nao remove)."""
    seen = []
    for c in state.library:
        if c in seen:
            continue
        seen.append(c)
    cands = [c for c in seen if is_land_card_name(c) and predicate(c)]
    if not cands:
        return None
    have = collections.Counter()
    for p in lands_in_play(state):
        for col in eff_card(p).produces:
            have[col] += 1
    best = None
    best_score = None
    for c in cands:
        card = CARD_DB[c]
        score = 0.0
        for col in sorted(card.produces & ANY_BGU):
            score += 10.0 / (1 + have[col])
        if len(card.produces & ANY_BGU) >= 2:
            score += 3
        tapped = land_enters_tapped(state, c)
        if tapped:
            score -= 4 if state.turn <= 6 else 1
        if "shock" in card.tags and not tapped:
            score -= 0.5
        if "basic" in card.tags:
            score -= 0.2
        if best_score is None or score > best_score or (score == best_score and c < best):
            best, best_score = c, score
    return best


def take_from_library(state: GameState, name: str):
    state.library.remove(name)


def basic_land_search(state: GameState):
    return search_land(state, lambda c: "basic" in CARD_DB[c].tags)


def forest_search(state: GameState):
    return search_land(state, lambda c: "Forest" in CARD_DB[c].land_types)


FETCH_TYPES = {"Misty Rainforest": {"Forest", "Island"}, "Polluted Delta": {"Island", "Swamp"}, "Verdant Catacombs": {"Swamp", "Forest"}}
LAND_BASIC_TYPES = {n: set(c.land_types) for n, c in CARD_DB.items() if "land" in c.types and c.land_types}


def crack_fetch(state: GameState, perm: Permanent) -> bool:
    """Fetch real: sacrifica e paga 1 de vida (CUSTO; a fetch vai ao cemiterio: Gitrog compra, Icetill rejoga), depois a habilidade RESOLVE: busca por SUBTIPO, thinning, embaralha.
    A busca e' depois dos gatilhos do cemiterio (a compra da Gitrog pode tirar o alvo da biblioteca). So' quebro se existe alvo agora (politica)."""
    name = perm.card.name
    fabled = "fabled_passage" in perm.card.tags
    if fabled:
        pred = lambda c: "basic" in CARD_DB[c].tags
    else:
        types = FETCH_TYPES[name]
        pred = lambda c: bool(CARD_DB[c].land_types & types)
    if search_land(state, pred) is None:
        state.fetch_no_target_total += 1
        return False
    state.battlefield.remove(perm)
    if not fabled:
        lose_life_self(state, 1, "fetch")
    put_card_into_graveyard(state, name, "battlefield", sacrificed=True)
    if state.game_over:
        return True
    target = search_land(state, pred)           # a busca acontece na resolucao, depois dos gatilhos (Gitrog)
    state.rng.shuffle(state.library)
    state.fetches_cracked_total += 1
    if target is None:
        state.fetch_no_target_total += 1
        return True
    take_from_library(state, target)
    if fabled:
        newp = put_land_onto_battlefield(state, target, tapped=True, source="fabled_passage", forced_tapped=True)
        if n_lands(state) >= 4:
            newp.tapped = False           # ruling: o terreno buscado conta pras 4; entra virado e desvira
    else:
        put_land_onto_battlefield(state, target, source="fetch")
    return True


def put_card_into_graveyard(state: GameState, name: str, from_zone: str, sacrificed: bool = False):
    """Carta (nao-ficha) MINHA indo ao cemiterio por qualquer via que nao seja mill. Gitrog (terreno), Syr Konrad (criatura vinda de fora do campo),
    Kozilek (de qualquer lugar)."""
    c = CARD_DB[name]
    if c.token:
        return
    state.graveyard.append(name)
    if is_land_card_name(name) and has_perm(state, "The Gitrog Monster"):
        state.gitrog_draws_total += 1
        draw_cards(state, 1, source="gitrog")
    if "creature" in c.types and from_zone != "battlefield":
        for _ in range(count_named(state, "Syr Konrad, the Grim")):
            konrad_ping(state, 1)
    if "kozilek" in c.tags and KOZILEK_SHUFFLE_ENABLED:
        kozilek_shuffle(state)


# =========================================================
# GATILHO DO MOTHMAN, ALVOS, ENTRADA/SAIDA DE PERMANENTES
# =========================================================

def counter_target_value(state: GameState, p: Permanent) -> float:
    t = eff_card(p).tags
    v = 0.0
    if "commander" in t:
        v += 95
    for tag, val in (("fathom_mage", 100), ("herd_baloth", 90), ("broodscale", 80), ("evo_witness", 70), ("kami", 60), ("gyre_sage", 55), ("danny_pink", 50),
                     ("ouroboroid", 45), ("evolve", 20), ("ballista", 15)):
        if tag in t:
            v += val
    if p.entered_turn < state.turn:
        v += 10
    v += 0.1 * power(state, p)
    return v


def counter_draw_cost(state: GameState, p: Permanent) -> int:
    """Compras OBRIGATORIAS que um contador neste alvo dispara (Danny Pink: 1a vez no turno por criatura)."""
    return 1 if (has_perm(state, "Danny Pink") and is_creature(p) and p.last_counter_turn != state.turn_id) else 0


def choose_counter_targets(state: GameState, x: int) -> list:
    """'up to X target creatures': posso escolher MENOS alvos. Com a biblioteca curta, pulo alvo que dispararia compra obrigatoria alem do orcamento."""
    cs = creatures(state)
    cs.sort(key=lambda p: (-counter_target_value(state, p), p.uid))
    if not SELF_MILL_GUARD_ENABLED:
        return cs[:x]
    budget = library_budget(state)
    hol = (not state.hollowmurk_triggered_this_turn) and any(h.ctr.get("sultai") for h in perms_named(state, "Hollowmurk Siege"))
    out, used = [], 0
    for p in cs:
        if len(out) >= x:
            break
        cost = counter_draw_cost(state, p)
        if cost and used + cost + (1 if hol and not out else 0) > budget:
            continue
        used += cost + (1 if hol and not out else 0)
        out.append(p)
    return out


def mothman_trigger(state: GameState, x: int, my_mill: bool = False, opp_mill: bool = False):
    """The Wise Mothman: "Whenever one or more nonland cards are milled, put a +1/+1 counter on each of up to X target creatures, where X is the number of
    nonland cards milled this way." Cada alvo recebe UM contador (+ substituidores); X > corpos e' desperdicio; criatura de oponente e' alvo legal (Generous Patron compra; crime)."""
    state.mothman_triggers_total += 1
    state.mothman_x_total += x
    if my_mill:
        state.mothman_trigger_my_mill += 1
    if opp_mill:
        state.mothman_trigger_opp_mill += 1
    targets = choose_counter_targets(state, x)
    placed = 0
    for p in targets:
        if p in state.battlefield:
            placed += place_counters(state, p, 1, source="mothman")
    state.mothman_counters_placed_total += placed
    extra = x - len(targets)
    if extra > 0 and OPP_CREATURE_TARGETS > 0 and alive_opps(state):
        k = min(extra, OPP_CREATURE_TARGETS)
        commit_crime(state, "mothman_target_opp_creature")
        for _ in range(k):
            for _ in range(count_named(state, "Generous Patron")):
                draw_cards(state, 1, source="generous_patron")


def enter_permanent_triggers(state: GameState, p: Permanent, from_cast: bool = True):
    """Gatilhos de 'um permanente entra' (nao-terreno; terrenos usam land_enters) + ETB proprio."""
    c = eff_card(p)
    if "riverchurn" in c.tags and state.riverchurn_enter_turn is None:
        state.riverchurn_enter_turn = state.turn
    for alt in list(state.battlefield):
        if alt is not p and "altar_brood" in alt.card.tags:
            parts = [(o.idx, 1) for o in alive_opps(state)]
            if parts:
                state.altar_brood_mills += 1
                mill_event(state, parts, source="altar_of_the_brood")
    if is_creature(p):
        # evolve (Gyre Sage, Pollywog Prodigy, Fathom Mage): o que entrou tem poder ou resistencia MAIOR que o da criatura com evolve
        for e in list(state.battlefield):
            if e is p or "evolve" not in e.card.tags or e not in state.battlefield:
                continue
            if power(state, p) > power(state, e) or toughness(state, p) > toughness(state, e):
                place_counters(state, e, 1, source="evolve")
        # The Great Henge: "Whenever a nontoken creature you control enters, put a +1/+1 counter on it and draw a card."
        if not p.is_token:
            for _ in range(count_named(state, "The Great Henge")):
                place_counters(state, p, 1, source="henge")
                draw_cards(state, 1, source="henge")
        # Garruk's Uprising (candidata): criatura com poder >= 4 entra: compre
        if power(state, p) >= 4:
            for _ in range(count_named(state, "Garruk's Uprising")):
                draw_cards(state, 1, source="garruk")
    apply_etb(state, p)


def apply_etb(state: GameState, p: Permanent):
    t = eff_card(p).tags
    if "commander" in t:
        # "Whenever The Wise Mothman enters or attacks, each player gets a rad counter."
        give_rad(state, 0, 1)
        for o in alive_opps(state):
            give_rad(state, o.idx, 1)
    if "mirelurk_queen" in t:
        o = pick_rad_target(state)
        if o is not None:
            commit_crime(state, "mirelurk_queen_etb")
            give_rad(state, o.idx, 2)
    if "generous_patron" in t:
        others = [q for q in creatures(state) if q is not p]
        others.sort(key=lambda q: (-counter_target_value(state, q), q.uid))
        for q in others[:2]:
            place_counters(state, q, 1, source="support")
        if OPP_CREATURE_TARGETS > 0 and len(others) < 2 and alive_opps(state):
            commit_crime(state, "patron_support_opp")
            for _ in range(min(2 - len(others), OPP_CREATURE_TARGETS)):
                draw_cards(state, 1, source="generous_patron")
    if "garruk" in t:
        if any(is_creature(q) and power(state, q) >= 4 for q in state.battlefield):
            draw_cards(state, 1, source="garruk")
    if "hollowmurk" in t:
        # "As this enchantment enters, choose Sultai or Abzan": Sultai compra (1x por turno); com a biblioteca curta, Abzan (contador no atacante + menace)
        if SELF_MILL_GUARD_ENABLED and library_budget(state) < 12:
            p.ctr["abzan"] = 1
        else:
            p.ctr["sultai"] = 1
    if "ashiok" in t:
        p.ctr["loyalty"] = 5
    if "jace_wom" in t:
        p.ctr["loyalty"] = 4
    if "horrigan" in t:
        # "Whenever Agent Frank Horrigan enters or attacks, proliferate twice."
        if state.horrigan_enter_turn is None:
            state.horrigan_enter_turn = state.turn
        state.horrigan_etb_prolifs += 1
        if HORRIGAN_PROLIF_TIMES > 0:
            proliferate(state, "horrigan_etb", times=HORRIGAN_PROLIF_TIMES)
    for _tag, _campo in (("scorchbeast", "scorch_enter_turn"), ("inex_tide", "tide_enter_turn"), ("branching_evo", "branching_enter_turn"), ("loading_zone", "loading_enter_turn"), ("earth_crystal", "crystal_enter_turn")):
        if _tag in t and getattr(state, _campo) is None:
            setattr(state, _campo, state.turn)
    if "master_t" in t:
        # "When The Master enters, target player gets two rad counters."
        if state.master_enter_turn is None:
            state.master_enter_turn = state.turn
        o = pick_rad_target(state)
        if o is not None:
            commit_crime(state, "master_t_etb")
            give_rad(state, o.idx, 2)
            state.master_etb_rad += 1
    if "urzas_saga" in t:
        pass
    if "boseiju" in t or "minamo" in t:
        pass


def pick_rad_target(state: GameState) -> Optional[Opp]:
    """Rad counters no oponente com mais biblioteca (mais mill util) e menos rad ja' (mill e perda de vida)."""
    al = alive_opps(state)
    if not al:
        return None
    return max(al, key=lambda o: (len(o.library), -o.rad, -o.idx))


def bojuka_bog_etb(state: GameState):
    al = [o for o in alive_opps(state) if o.graveyard]
    commit_crime(state, "bojuka_bog")          # "target player's graveyard": mira o do oponente (crime)
    state.interaction_plays += 1
    if al:
        tgt = max(al, key=lambda o: (len(o.graveyard), -o.idx))
        tgt.graveyard.clear()


def freestrider_trigger(state: GameState):
    top = state.library[:5]
    del state.library[:5]
    cands = [c for c in top if is_land_card_name(c)]
    pick = None
    if cands:
        have = collections.Counter()
        for lp in lands_in_play(state):
            for col in eff_card(lp).produces:
                have[col] += 1
        pick = max(cands, key=lambda c: (sum(10.0 / (1 + have[col]) for col in sorted(CARD_DB[c].produces & ANY_BGU)), c))
        top.remove(pick)
    # o resto vai pro fundo em ordem aleatoria
    state.rng.shuffle(top)
    state.library.extend(top)
    if pick:
        put_land_onto_battlefield(state, pick, tapped=True, source="freestrider")


def saga_add_lore(state: GameState, p: Permanent):
    """Urza's Saga: I — ganha '{T}: Add {C}'; II — ganha '{2},{T}: Construct'; III — busca artefato com custo {0}/{1}, poe em campo, embaralha; depois sacrifica.
    O lore entra com o terreno e depois de cada compra minha (CR 714.2b)."""
    p.ctr["lore"] = p.ctr.get("lore", 0) + 1
    state.saga_chapters += 1
    if p.ctr["lore"] == 3:
        urza_chapter_iii(state, p)


def urza_chapter_iii(state: GameState, p: Permanent):
    target = None
    for name in ("Sol Ring", "Altar of the Brood", "Soul-Guide Lantern"):
        if name in state.library and not has_perm(state, name):
            target = name
            break
    if target is None:
        for name in ("Sol Ring", "Altar of the Brood", "Soul-Guide Lantern"):
            if name in state.library:
                target = name
                break
    if target:
        state.library.remove(target)
        state.rng.shuffle(state.library)
        q = mk_perm(state, target)
        state.battlefield.append(q)
        enter_permanent_triggers(state, q, from_cast=False)
        if target == "Soul-Guide Lantern":
            lantern_etb(state)
    # sacrifica a Saga (terreno: vai pro cemiterio; Gitrog compra; Icetill/Muldrotha podem rejogar)
    if p in state.battlefield:
        state.battlefield.remove(p)
        put_card_into_graveyard(state, p.card.name, "battlefield", sacrificed=True)


def lantern_etb(state: GameState):
    """Soul-Guide Lantern: 'When this artifact enters, exile target card from a graveyard.' — mira o cemiterio do oponente (crime) quando ha carta."""
    al = [o for o in alive_opps(state) if o.graveyard]
    if al:
        commit_crime(state, "lantern")
        tgt = max(al, key=lambda o: (len(o.graveyard), -o.idx))
        if tgt.graveyard:                         # o gatilho de crime (Deepmuck) pode ter mexido no cemiterio
            tgt.graveyard.pop()


def normalize_counters(p: Permanent):
    m = p.ctr.get("minus1", 0)
    if m and p.counters:
        k = min(m, p.counters)
        p.counters -= k
        p.ctr["minus1"] = m - k


def creature_dies(state: GameState, perm: Permanent, sacrificed: bool = False):
    """Efeitos de 'uma criatura morre' que nao dependem de onde ela vai: Syr Konrad (outra criatura). Em mortes SIMULTANEAS (`kill_group`) o ping e' contado la' (ruling 2019-10-04)."""
    if state.konrad_batch:
        return
    for k in [q for q in state.battlefield if "syr_konrad" in q.card.tags and q is not perm]:
        konrad_ping(state, 1)


def kill_group(state: GameState, perms: list, reason: str = "dies"):
    """Mortes simultaneas (wipes): cada Syr Konrad que estava em campo dispara uma vez por OUTRA criatura que morre junto (ruling 2019-10-04: 'if one or more creatures die at the same
    time as Syr Konrad, its first ability triggers for each of those creatures')."""
    group = [p for p in perms if p in state.battlefield]
    konrads = [q for q in state.battlefield if "syr_konrad" in q.card.tags]
    dying = [p for p in group if is_creature(p)]
    state.konrad_batch = True
    try:
        for p in group:
            remove_permanent(state, p, reason)
    finally:
        state.konrad_batch = False
    for k in konrads:
        for c in dying:
            if c is not k:
                konrad_ping(state, 1)


def remove_permanent(state: GameState, perm: Permanent, reason: str = "dies", sacrificed: bool = False):
    if perm not in state.battlefield:
        return
    was_creature = is_creature(perm)
    state.battlefield.remove(perm)
    for q in list(state.battlefield):
        if q.attached_to == perm.uid:
            q.attached_to = None
    name = perm.card.name
    if perm.is_token:
        if was_creature:
            creature_dies(state, perm, sacrificed)
        return
    if "commander" in perm.card.tags:
        state.commander_in_cz = True
        state.commander_uid = None
        if was_creature:
            creature_dies(state, perm, sacrificed)
        return
    if was_creature:
        creature_dies(state, perm, sacrificed)
    if "opp_card" in perm.card.tags:
        state.opps[max(0, perm.owner_idx - 1)].graveyard.append("C")        # a carta e' DO OPONENTE: vai ao cemiterio dele, nao ao meu
        return
    had_minus = perm.ctr.get("minus1", 0) > 0
    put_card_into_graveyard(state, name, "battlefield", sacrificed=sacrificed)
    if "master" in perm.card.tags:
        n7 = (1 if len(state.graveyard) >= 7 else 0) + sum(1 for o in state.opps if len(o.graveyard) >= 7)
        draw_cards(state, n7, source="master_of_lake_town")
    # Persist (Glen Elendra Archmage): volta com um contador -1/-1 se nao tinha
    if "persist" in perm.card.tags and not had_minus and name in state.graveyard:
        state.graveyard.remove(name)
        q = mk_perm(state, name)
        _pl, _mu = counter_modifiers(state, q, "-1/-1")
        q.ctr["minus1"] = (1 + _pl) * _mu      # Constrictor: +1 de cada tipo de contador; Loading Zone: dobra (igual a 1 + Constrictor sem esse dobrador)
        state.battlefield.append(q)
        state.persist_returns += 1
        on_counters_placed(state, q, q.ctr["minus1"], "-1/-1", "persist")     # Hollowmurk Sultai / Danny: 'a counter is put on a creature you control' (de qualquer tipo)
        if PERSIST_ZERO_TOUGHNESS_DIES and toughness(state, q) <= 0:
            state.persist_zero_deaths += 1
            remove_permanent(state, q, "dies")                                 # 0/0: morre como ESB, antes dos gatilhos de entrada (Henge ainda compra; o contador +1/+1 se perde)
        enter_permanent_triggers(state, q, from_cast=False)


# =========================================================
# CUSTO, CONJURACAO E EFEITOS
# =========================================================

CAST_PRIORITY = {
    "The Great Henge": 110, "Sol Ring": 100, "Nature's Lore": 90, "Three Visits": 89, "Hardened Scales": 84, "Winding Constrictor": 82, "Hollowmurk Siege": 78,
    "Bramble Familiar // Fetch Quest": 74, "Kami of Whispered Hopes": 72, "Ruin Crab": 75, "Gitrog": 0, "The Gitrog Monster": 76, "Muldrotha, the Gravetide": 80,
    "Icetill Explorer": 72, "Six": 70, "Danny Pink": 74, "Ouroboroid": 66, "Basking Broodscale": 65, "Psychic Corrosion": 62, "Mesmeric Orb": 58, "Mindcrank": 55,
    "Memory Erosion": 56, "Zellix, Sanity Flayer": 68, "Kodama of the West Tree": 69, "Generous Patron": 63, "Mirelurk Queen": 67, "Syr Konrad, the Grim": 62,
    "Hedge Shredder": 61, "Undead Alchemist": 59, "Fathom Mage": 66, "Herd Baloth": 64, "Evolution Witness": 60, "Pollywog Prodigy": 55, "Deepmuck Desperado": 57,
    "Cold-Eyed Selkie": 40, "Cankerbloom": 35, "Rampant Frogantua": 50, "Glen Elendra Archmage": 45, "Angel of Suffering": 52, "Kozilek, Butcher of Truth": 30,
    "Walking Ballista": 48, "Agatha's Soul Cauldron": 58, "Altar of Dementia": 40, "Soul-Guide Lantern": 30, "Swiftfoot Boots": 45, "Ashiok, Dream Render": 63,
    "Palantír of Orthanc": 64, "Bloodchief Ascension": 60, "Altar of the Brood": 50, "Gyre Sage": 62, "Freestrider Lookout": 52,
    "Riverchurn Monument": 57, "Jace, Wielder of Mysteries": 66, "Agent Frank Horrigan": 71, "The Master, Transcendent": 67,
    "Fractured Sanity": 64, "Screeching Scorchbeast": 70, "Inexorable Tide": 60, "Branching Evolution": 70, "Loading Zone": 58, "The Earth Crystal": 61,
    "Evolution Sage": 70, "Terrasymbiosis": 66, "Corpsejack Menace": 71, "Bruvac the Grandiloquent": 63, "The Master of Lake-town": 62, "Garruk's Uprising": 61,
}
FINISHERS = frozenset({"Kozilek, Butcher of Truth", "Rampant Frogantua", "Syr Konrad, the Grim", "Mindcrank", "Bloodchief Ascension"})
INSTANT_HOLD = {"Negate", "Arcane Denial", "Didn't Say Please", "Fierce Guardianship", "An Offer You Can't Refuse", "Heroic Intervention"}


def commander_tax(state: GameState) -> int:
    return 2 * state.commander_cast_count


def effective_cost(state: GameState, name: str, x: int = 0, face: str = "front"):
    """(generico, pips) de uma conjuracao da mao, com X, imposto do comandante (CR 903.8: conta conjuracoes, inclusive contra-atacadas) e The Great Henge."""
    c = CARD_DB[name]
    g, pips = c.generic, c.pips
    if face == "adventure":                                  # Fetch Quest {5}{G}{G}
        g, pips = 5, (frozenset("G"), frozenset("G"))
    elif face == "warp":                                     # Loading Zone: Warp {G}
        g, pips = 0, (frozenset("G"),)
    if c.is_x and face != "adventure":
        g += x * c.x_mult
    if "commander" in c.tags:
        g += commander_tax(state)
    if "henge" in c.tags:
        red = max([power(state, p) for p in creatures(state)] + [0])
        g = max(0, g - red)
    n_ec = count_named(state, "The Earth Crystal")
    if n_ec and g > 0 and any("G" in pp for pp in pips):
        # "Green spells you cast cost {1} less to cast." (ruling 2025-06-06: so' o generico do custo total; uma carta com pip hibrido {G/U} e' verde)
        g = max(0, g - n_ec)
    return g, pips


def free_cast_possible(state: GameState, name: str) -> bool:
    if name == "Fierce Guardianship":
        return any("commander" in p.card.tags for p in state.battlefield)
    return False


def can_cast_name(state: GameState, name: str, x: int = 0, face: str = "front") -> bool:
    c = CARD_DB[name]
    if "land" in c.types and "mdfc" not in c.tags:
        return False
    if "commander" in c.tags and not state.commander_in_cz:
        return False
    g, pips = effective_cost(state, name, x, face)
    return can_pay(state, g, pips, c)


def choose_x(state: GameState, name: str) -> int:
    c = CARD_DB[name]
    if not c.is_x:
        return 0
    g, pips = effective_cost(state, name, 0)
    mx = max_x(state, g, pips, c.x_mult, c)
    if "ballista" in c.tags:
        return mx
    if "nuclear_fallout" in c.tags:
        return fallout_x(state, mx)
    if "repulsive_mutation" in c.tags:
        return mx
    if "agadeem" in c.tags:
        return agadeem_x(state, mx)[0]
    return mx


def spare_after(state: GameState, generic: int, pips: tuple, spell=None) -> int:
    """Mana restante se eu pagasse esse custo (aprox.: total disponivel - custo)."""
    return available_mana(state, spell) - generic - len(pips)


def reserve_needed(state: GameState) -> int:
    """Mana a deixar aberta pras contramagicas da mao (so' a partir do turno 3 e com oponentes vivos)."""
    if state.turn < 3 or not alive_opps(state):
        return 0
    costs = []
    for c in state.hand:
        if c in INSTANT_HOLD and c != "Heroic Intervention":
            g, pips = effective_cost(state, c)
            if c == "Fierce Guardianship" and free_cast_possible(state, c):
                continue
            costs.append(g + len(pips))
    return min(costs) if costs else 0


def cast_commander(state: GameState) -> bool:
    name = COMMANDER
    g, pips = effective_cost(state, name)
    if not state.commander_in_cz or not pay_mana(state, g, pips, CARD_DB[name]):
        return False
    state.commander_cast_count += 1
    state.commander_in_cz = False
    state.spells_cast_this_turn += 1
    on_my_spell_cast(state, name)
    state.casts_by_card[name] = state.casts_by_card.get(name, 0) + 1
    if state.interaction_rng is not None and try_smart_opponent_counter(state):
        state.commander_countered_total += 1
        state.commander_in_cz = True                  # anulado: volta pra zona de comando (o imposto de comandante ja' conta a conjuracao, CR 903.8)
        return True
    if state.commander_cast_turn is None:
        state.commander_cast_turn = state.turn
    p = mk_perm(state, name)
    state.battlefield.append(p)
    state.commander_uid = p.uid
    enter_permanent_triggers(state, p, from_cast=True)
    return True


def cast_card(state: GameState, name: str, x: int = 0, free: bool = False, face: str = "front", zone: str = "hand") -> bool:
    """Conjura `name` (da mao, do exilio de aventura ou do cemiterio via Muldrotha/Six). Paga custo, dispara gatilhos de conjuracao, resolve."""
    if name == COMMANDER:
        return cast_commander(state)
    c = CARD_DB[name]
    if not free:
        g, pips = effective_cost(state, name, x, face)
        if not pay_mana(state, g, pips, c):
            return False
    if zone == "hand":
        if name in state.hand:
            state.hand.remove(name)
    state.spells_cast_this_turn += 1
    on_my_spell_cast(state, name)
    key = name if face == "front" else name + (" [warp]" if face == "warp" else " [aventura]")
    state.casts_by_card[key] = state.casts_by_card.get(key, 0) + 1
    resolve_spell(state, name, x=x, face=face, zone=zone)
    if name in FINISHERS and face == "front":
        state.finisher_resolved_total += 1
        if state.first_finisher_turn is None:
            state.first_finisher_turn = state.turn
    return True


def resolve_spell(state: GameState, name: str, x: int = 0, face: str = "front", zone: str = "hand"):
    c = CARD_DB[name]
    tags = c.tags
    if "kozilek" in tags:
        draw_cards(state, 4, source="kozilek")                  # "When you cast this spell, draw four cards": resolve mesmo se a magia for anulada
        state.kozilek_cast_turn = state.turn
    if face == "adventure":
        resolve_fetch_quest(state, name)
        return
    types = c.types
    if "instant" in types or "sorcery" in types:
        resolve_instant_sorcery(state, name, x)
        if "mdfc" not in tags and name not in state.exile:
            if zone == "graveyard":
                pass
            put_card_into_graveyard(state, name, "stack")
        elif "mdfc" in tags:
            put_card_into_graveyard(state, name, "stack")
        return
    if "land" in types and "mdfc" in tags:
        return
    # permanente
    p = mk_perm(state, name)
    if face == "warp":
        p.warped = True
        state.warp_casts += 1
    if "ballista" in tags:
        plus, mult = counter_modifiers(state, p, "+1/+1")
        p.counters = (x + plus) * mult if x > 0 else 0
        state.counters_placed_total += p.counters
    state.battlefield.append(p)
    if "ballista" in tags and p.counters > 0:
        on_counters_placed(state, p, p.counters, "+1/+1", "enters")      # Hollowmurk/Danny: 'enters with counters' conta como 'counters put on' (ruling Hollowmurk 2025-04-04)
    if "artifact" in types and "sol_ring" in tags or "henge" in tags or "kami" in tags or "gyre_sage" in tags or "bramble" in tags:
        state.ramp_pieces_in_play += 1
    if "kozilek" in tags and state.first_finisher_turn is None:
        pass
    enter_permanent_triggers(state, p, from_cast=True)
    if "ballista" in tags and p.counters == 0 and p in state.battlefield:
        remove_permanent(state, p)           # 0/0: morre (X=0)
    if "soul_guide" in tags:
        pass
    if "lantern" in tags:
        lantern_etb(state)
    if "ashiok" in tags:
        pass
    if "boots" in tags:
        pass


def resolve_instant_sorcery(state: GameState, name: str, x: int):
    tags = CARD_DB[name].tags
    if "fractured_sanity" in tags:
        # "Each opponent mills fourteen cards." (nao mira: nao e' crime) - UM evento de mill simultaneo (um gatilho do Mothman, uma do Scorchbeast...)
        state.fractured_casts += 1
        parts = [(o.idx, 14) for o in alive_opps(state)]
        if parts:
            mill_event(state, parts, source="fractured_sanity")
        return
    if "natures_lore" in tags or "three_visits" in tags:
        t = forest_search(state)
        if t:
            take_from_library(state, t)
            state.rng.shuffle(state.library)
            put_land_onto_battlefield(state, t, source="ramp")
            state.ramp_pieces_in_play += 1
        return
    if "nuclear_fallout" in tags:
        state.wipes_cast += 1
        # "Each creature gets twice -X/-X until end of turn. Each player gets X rad counters."
        kill_group(state, [p for p in creatures(state) if toughness(state, p) <= 2 * x])
        give_rad(state, 0, x)
        for o in alive_opps(state):
            give_rad(state, o.idx, x)
        return
    if "toxic_deluge" in tags:
        state.wipes_cast += 1
        kill_group(state, [p for p in creatures(state) if toughness(state, p) <= x])
        return
    if "wave_goodbye" in tags:
        state.wipes_cast += 1
        for p in list(creatures(state)):
            if p.counters == 0 and "opp_card" in p.card.tags:
                state.battlefield.remove(p)
                state.opps[max(0, p.owner_idx - 1)].hand_size += 1            # "to its owner's hand": o dono e' o oponente
            elif p.counters == 0 and not p.is_token and "commander" not in p.card.tags:
                state.battlefield.remove(p)
                state.hand.append(p.card.name)
            elif p.counters == 0 and "commander" in p.card.tags:
                state.battlefield.remove(p)
                state.commander_in_cz = True
        return
    if "repulsive_mutation" in tags:
        cs = creatures(state)
        if cs:
            tgt = max(cs, key=lambda q: (counter_target_value(state, q), -q.uid))
            place_counters(state, tgt, x, source="repulsive_mutation")
        return
    if "smugglers_surprise" in tags:
        resolve_smugglers_surprise(state)
        return
    if "tear_asunder" in tags or "vats" in tags:
        state.interaction_plays += 1
        commit_crime(state, "removal")
        return
    if "atomize" in tags:
        # "Destroy target nonland permanent. Proliferate.": o destroy mira permanente de OPONENTE (estrutural: crime + metrica proxy); o proliferate e' REAL (o crime vem antes: o gatilho do Deepmuck resolve antes da magia)
        state.atomize_casts += 1
        state.interaction_plays += 1
        commit_crime(state, "removal")
        proliferate(state, "atomize")
        return
    if "casualties" in tags:
        # "Choose one or more": artefato / criatura / encantamento / terreno / planeswalker, alvos de OPONENTE (estrutural); uma magia que mira = UM crime; sem inventar quantos modos haveria
        state.casualties_casts += 1
        state.interaction_plays += 1
        commit_crime(state, "removal")
        return
    if "trophy" in tags:
        # "Destroy target permanent an opponent controls. Its controller may search their library for a basic land card, put it onto the battlefield, then shuffle."
        # destroy: estrutural (crime + metrica proxy). A busca e' REAL no que o simulador rastreia: o oponente alvo (o 1o vivo) tira 1 terreno da biblioteca (-1 carta) e ganha 1 terreno em campo (`Opp.lands`);
        # o embaralhar nao tem efeito observavel (a biblioteca ja' e' uma permutacao aleatoria e nada aqui depende de ordem conhecida).
        state.trophy_casts += 1
        state.interaction_plays += 1
        commit_crime(state, "removal")
        al = alive_opps(state)
        if al and "L" in al[0].library:
            al[0].library.remove("L")
            al[0].lands += 1
            state.trophy_lands_given += 1
        return
    if "heroic_intervention" in tags:
        state.protection_used_total += 1
        return
    if "agadeem" in tags:
        agadeem_resolve(state, x)
        return
    # contramagicas conjuradas sem alvo: nao acontece (so' em resposta); aqui nada
    return


def resolve_smugglers_surprise(state: GameState):
    """Spree. Modos escolhidos na conjuracao (decididos em `try_smugglers_surprise`): A mill 4 + ate 2 criatura/terreno pra mao; B ate 2 criaturas da mao pro campo."""
    modes = state.pending_modes or ("A",)
    state.pending_modes = None
    if "A" in modes:
        res = mill_event(state, [(0, 4)], source="smugglers_surprise")
        cards = res.get(0, [])
        picks = [c for c in cards if ("creature" in CARD_DB[c].types or is_land_card_name(c)) and c in state.graveyard]
        picks.sort(key=lambda c: (-graveyard_value(state, c), c))
        taken = 0
        for c in picks:
            if taken >= 2:
                break
            if c not in state.graveyard:
                continue
            taken += 1
            state.graveyard.remove(c)
            state.hand.append(c)
            state.recursion_events_total += 1
            graveyard_leave(state, [c])
    if "B" in modes:
        creatures_h = [c for c in state.hand if "creature" in CARD_DB[c].types and "commander" not in CARD_DB[c].tags and "mdfc" not in CARD_DB[c].tags]
        creatures_h.sort(key=lambda c: (-CARD_DB[c].mv, c))
        for c in creatures_h[:2]:
            state.hand.remove(c)
            q = mk_perm(state, c)
            state.battlefield.append(q)
            enter_permanent_triggers(state, q, from_cast=False)


def resolve_fetch_quest(state: GameState, name: str):
    """Fetch Quest (aventura de Bramble Familiar): 'Mill seven cards. Then put a creature, enchantment, or land card from among the milled cards onto the battlefield.'
    A carta vai pro exilio (aventura) e a criatura pode ser conjurada de la depois."""
    state.adventure_casts += 1
    res = mill_event(state, [(0, 7)], source="fetch_quest")
    cards = [c for c in res.get(0, []) if c in state.graveyard]
    opts = [c for c in cards if any(t in CARD_DB[c].types for t in ("creature", "enchantment", "land")) and not "mdfc" in CARD_DB[c].tags]
    if opts:
        def val(c):
            cc = CARD_DB[c]
            if "land" in cc.types and "enchantment" not in cc.types:
                return (1.0 if n_lands(state) >= 5 else 6.0, c)
            return (float(CAST_PRIORITY.get(c, cc.mv)), c)
        best = max(opts, key=val)
        state.graveyard.remove(best)
        state.recursion_events_total += 1
        graveyard_leave(state, [best])
        if "land" in CARD_DB[best].types and "creature" not in CARD_DB[best].types:
            put_land_onto_battlefield(state, best, source="fetch_quest")
        else:
            q = mk_perm(state, best)
            state.battlefield.append(q)
            enter_permanent_triggers(state, q, from_cast=False)
    state.adventure_exile.append(CARD_DB[name].name)


def fallout_x(state: GameState, mx: int) -> int:
    """Nuclear Fallout: X rad counters para cada jogador e -2X/-2X. Escolhe o maior X que NAO mata criatura minha relevante (nao-ficha e nao-dork de 1 de resistencia
    nao conta como relevante) e que nao me pese: ate 3."""
    best = 0
    for x in range(1, min(mx, 3) + 1):
        losses = [p for p in creatures(state) if toughness(state, p) <= 2 * x and not p.is_token]
        if len(losses) <= 1 and not any("commander" in p.card.tags for p in losses):
            best = x
    return best


def agadeem_x(state: GameState, mx: int):
    """Agadeem's Awakening (lado feitico): devolve do cemiterio criaturas de MV DIFERENTES, todas <= X. Escolhe X e a lista que maximiza valor."""
    best = (0, [])
    byv = collections.defaultdict(list)
    for c in state.graveyard:
        cc = CARD_DB[c]
        if "creature" in cc.types and not cc.token and cc.mv <= max(mx, 0):
            byv[cc.mv].append(c)
    for x in range(0, mx + 1):
        chosen = []
        for mvv in sorted(byv):
            if mvv <= x:
                chosen.append(max(byv[mvv], key=lambda c: (CAST_PRIORITY.get(c, 0), c)))
        val = sum(CAST_PRIORITY.get(c, 10) for c in chosen)
        if val > sum(CAST_PRIORITY.get(c, 10) for c in best[1]):
            best = (x, chosen)
    return best


def agadeem_resolve(state: GameState, x: int):
    _, chosen = agadeem_x(state, x)
    for c in chosen:
        if c in state.graveyard:
            state.graveyard.remove(c)
            graveyard_leave(state, [c])
            q = mk_perm(state, c)
            state.battlefield.append(q)
            state.recursion_events_total += 1
            enter_permanent_triggers(state, q, from_cast=False)


# =========================================================
# TERRENO DA VEZ (jogada, T1/T2 virado primeiro, fetch, cemiterio)
# =========================================================

def land_drops_available(state: GameState) -> int:
    # "You may play an additional land on each of your turns": Icetill Explorer e The Gitrog Monster (cada um soma 1)
    return 1 + count_named(state, "Icetill Explorer") + count_named(state, "The Gitrog Monster")


def colors_in_play(state: GameState) -> collections.Counter:
    have = collections.Counter()
    for p in lands_in_play(state):
        for col in eff_card(p).produces & ANY_BGU:
            have[col] += 1
        if "fetch" in p.card.tags:
            if p.card.name in FETCH_TYPES:
                for t in sorted(FETCH_TYPES[p.card.name]):
                    have[{"Forest": "G", "Island": "U", "Swamp": "B"}[t]] += 1
            else:
                for col in "BGU":
                    have[col] += 1
    return have


def land_play_score(state: GameState, name: str) -> float:
    c = CARD_DB[name]
    have = colors_in_play(state)
    sc = 0.0
    if "fetch" in c.tags:
        if name in FETCH_TYPES:
            cols = {"Forest": "G", "Island": "U", "Swamp": "B"}
            for t in sorted(FETCH_TYPES[name]):
                sc += 6.0 / (1 + have[cols[t]])
        else:
            for col in "BGU":
                sc += 5.0 / (1 + have[col])
        sc += 2.0 if state.turn >= 3 else 0.0         # fetch cedo thina e vai ao cemiterio (Gitrog/Icetill)
        return sc
    for col in sorted(c.produces & ANY_BGU):
        sc += 10.0 / (1 + have[col])
    if len(c.produces & ANY_BGU) >= 2:
        sc += 2.0
    if land_enters_tapped(state, name):
        sc -= 3.0 if state.turn <= 5 else 0.5
    if "basic" in c.tags:
        sc -= 0.5
    if c.tags & {"strip_mine", "swarmyard", "yavimaya_hollow", "plaza", "bog"}:
        sc -= 4.0
    if "urzas_saga" in c.tags:
        sc += 3.0 if state.turn >= 2 else 0.0
    return sc


def count_castable(state: GameState) -> int:
    n = 0
    seen = []
    for name in state.hand:
        if name in seen:
            continue
        seen.append(name)
        c = CARD_DB[name]
        if "land" in c.types and "mdfc" not in c.tags:
            continue
        if name in INSTANT_HOLD:
            continue
        if can_cast_name(state, name, 0):
            n += 1
    return n


def tapped_first_pick(state: GameState, cands: list) -> Optional[str]:
    """T1/T2: se existe terreno que entra virado, so' o jogo ele primeiro quando o ensaio a seco mostra que isso NAO custa nenhuma conjuracao (CLAUDE.md Regra #10)."""
    tapped = [c for c in cands if land_enters_tapped(state, c) or "fabled_passage" in CARD_DB[c].tags]
    if not tapped:
        return None
    untapped = [c for c in cands if c not in tapped]
    if not untapped:
        return None
    base = count_castable(state)
    best_un = max(untapped, key=lambda c: (land_play_score(state, c), c))
    uid0 = state.next_uid
    tmp = mk_perm(state, best_un)
    state.battlefield.append(tmp)
    with_un = count_castable(state)
    state.battlefield.remove(tmp)
    state.next_uid = uid0                    # ensaio a seco sem efeito colateral (Regra #10)
    if with_un > base:
        state.tapped_land_skipped_for_play_total += 1
        return None
    pick = max(tapped, key=lambda c: (land_play_score(state, c), c))
    state.tapped_land_first_plays_total += 1
    return pick


def graveyard_land_candidates(state: GameState) -> list:
    """Terrenos que posso jogar do cemiterio: Icetill Explorer (todos) e Muldrotha (1 por turno, tipo terreno). MDFC (Agadeem): jogavel como terreno de qualquer zona."""
    ok = has_perm(state, "Icetill Explorer") or (has_perm(state, "Muldrotha, the Gravetide") and "land" not in state.muldrotha_used)
    if not ok:
        return []
    out = []
    for c in state.graveyard:
        if c in out:
            continue
        if "land" in CARD_DB[c].types:
            out.append(c)
    return out


def land_play_candidates(state: GameState):
    """(terrenos da mao jogaveis, todos os candidatos = mao + cemiterio via Icetill/Muldrotha). Usado por `play_land_phase` e por `cast_landfall_payoffs_first`."""
    hand_lands = []
    for c in state.hand:
        cc = CARD_DB[c]
        if "land" not in cc.types:
            continue
        if "mdfc" in cc.tags:
            # MDFC: so' como terreno se estou curto de terrenos (senao fica como feiticio)
            if n_lands(state) >= 6:
                continue
            if n_lands(state) >= 5 and any("land" in CARD_DB[x].types and "mdfc" not in CARD_DB[x].tags for x in state.hand):
                continue
        if c not in hand_lands:
            hand_lands.append(c)
    gy = graveyard_land_candidates(state)
    cands = list(hand_lands)
    for g in gy:
        if g not in cands:
            cands.append(g)
    return hand_lands, cands


def play_land_phase(state: GameState):
    while state.lands_played_this_turn < land_drops_available(state) and not state.game_over:
        hand_lands, cands = land_play_candidates(state)
        if not cands:
            break
        pick = None
        if TAPPED_LAND_FIRST_ENABLED and state.turn <= TAPPED_LAND_FIRST_MAX_TURN:
            pick = tapped_first_pick(state, cands)
            if state.ghost:
                pick = None
        if pick is None:
            pick = max(cands, key=lambda c: (land_play_score(state, c), c))
        if pick in hand_lands:
            state.hand.remove(pick)
        else:
            state.graveyard.remove(pick)
            if has_perm(state, "Icetill Explorer"):
                state.icetill_replays += 1
            else:
                state.muldrotha_used.append("land")
                state.muldrotha_plays += 1
        state.lands_played_this_turn += 1
        p = put_land_onto_battlefield(state, pick, source="play")
        if "fetch" in p.card.tags and FETCH_LANDS_ENABLED:
            crack_fetch(state, p)


# =========================================================
# FASE PRINCIPAL: conjuracao, ativadas, mana ociosa
# =========================================================

def graveyard_cast_options(state: GameState) -> list:
    """Conjuracoes do cemiterio: Muldrotha (uma magia de cada tipo permanente por turno) e Six (retrace: descartar um terreno)."""
    out = []
    has_mul = has_perm(state, "Muldrotha, the Gravetide")
    has_six = has_perm(state, "Six")
    if not has_mul and not has_six:
        return out
    seen = []
    for name in state.graveyard:
        if name in seen:
            continue
        seen.append(name)
        c = CARD_DB[name]
        if c.token or "commander" in c.tags:
            continue
        if "land" in c.types or "instant" in c.types or "sorcery" in c.types or "mdfc" in c.tags:
            continue
        types_perm = [t for t in ("creature", "artifact", "enchantment", "planeswalker") if t in c.types]
        if not types_perm:
            continue
        if has_mul:
            free_types = [t for t in types_perm if t not in state.muldrotha_used]
            if free_types:
                out.append((name, "muldrotha", free_types[0]))
                continue
        if has_six and any("land" in CARD_DB[h].types and "mdfc" not in CARD_DB[h].tags for h in state.hand):
            out.append((name, "six", None))
    return out


def castable_candidates(state: GameState, phase: str) -> list:
    cands = []
    seen = []
    for name in state.hand:
        if name in seen:
            continue
        seen.append(name)
        c = CARD_DB[name]
        if "land" in c.types and "mdfc" not in c.tags:
            continue
        if name in INSTANT_HOLD:
            continue
        tags = c.tags
        if tags & {"wipe", "tear_asunder", "vats", "repulsive_mutation", "smugglers_surprise", "agadeem", "atomize", "casualties", "trophy"}:
            continue          # tratadas em `use_spare_mana` / modos
        if "kozilek" in tags and len(state.library) <= 6:
            continue          # 'When you cast this spell, draw four cards': nao conjuro com a biblioteca no fim
        if "orb" in tags and SELF_MILL_GUARD_ENABLED and len(state.library) < ORB_CAST_MIN_LIBRARY:
            continue          # Mesmeric Orb me mila a cada permanente que desvira
        if c.is_x:
            x = choose_x(state, name)
            if x >= 1 and can_cast_name(state, name, x):
                cands.append((name, "hand", "front"))
            continue
        if can_cast_name(state, name):
            cands.append((name, "hand", "front"))
        elif "loading_zone" in tags and creatures(state) and can_pay(state, 0, (frozenset("G"),), c):
            cands.append((name, "hand", "warp"))                  # Warp {G} (politica: so' quando o custo cheio nao cabe e ha criatura para receber contador)
        if "bramble" in tags and safe_self_mill(state, 7):
            g, pips = effective_cost(state, name, 0, "adventure")        # Fetch Quest {5}{G}{G}: mila 7 e poe criatura/encantamento/terreno em campo
            if can_pay(state, g, pips, c) and n_lands(state) >= 6:
                cands.append((name, "hand", "adventure"))
    if state.commander_in_cz and can_cast_name(state, COMMANDER):
        cands.append((COMMANDER, "cz", "front"))
    for name in state.adventure_exile:
        if can_cast_name(state, name):
            cands.append((name, "exile", "front"))
    for name, t_exiled in state.warp_exile:
        if t_exiled < state.turn and can_cast_name(state, name):
            cands.append((name, "warpexile", "front"))             # Warp: "you may cast it from exile on a later turn" (custo cheio)
    for name, perm, slot in graveyard_cast_options(state):
        g, pips = effective_cost(state, name)
        if can_pay(state, g, pips, CARD_DB[name]):
            cands.append((name, "graveyard:" + perm, slot))
    return cands


def cast_blocked(state: GameState, name: str, face: str = "front") -> bool:
    """Politica de biblioteca: nao conjurar engine que me compra/mila OBRIGATORIAMENTE alem do que a biblioteca aguenta (o jogador humano para)."""
    if not SELF_MILL_GUARD_ENABLED or name == COMMANDER or face == "adventure":
        return False
    c = CARD_DB[name]
    b = library_budget(state)
    if "henge" in c.tags and b < 8:
        return True                                                 # a Henge compra a cada criatura nao-ficha que entra
    if "danny_pink" in c.tags and b < 12:
        return True                                                 # toda criatura com contador compra, 1x por turno
    if "ouroboroid" in c.tags and has_perm(state, "Danny Pink") and b < len(creatures(state)) + 4:
        return True
    if "creature" in c.types and has_perm(state, "The Great Henge") and not c.token and b < 1:
        return True
    return False


def cast_score(state: GameState, name: str, zone: str, face: str = "front") -> float:
    if name == COMMANDER:
        return 200.0
    if face == "adventure":
        return 58.0
    if face == "warp":
        return 44.0
    sc = float(CAST_PRIORITY.get(name, 20))
    c = CARD_DB[name]
    ramp = {"sol_ring", "natures_lore", "three_visits", "kami", "bramble", "gyre_sage", "henge"}
    if c.tags & ramp and n_lands(state) <= 6:
        sc += 12
    if "creature" in c.types and not creatures(state):
        sc += 6
    if state.turn <= 3 and c.mv <= 2:
        sc += 4
    if zone.startswith("graveyard"):
        sc -= 3
    sc += 0.05 * c.mv
    return sc


def cast_loop(state: GameState, phase: str = "main1"):
    failed = []
    for _ in range(60):
        if state.game_over:
            return
        cands = [t for t in castable_candidates(state, phase) if t[0] + t[1] + str(t[2]) not in failed and not cast_blocked(state, t[0], t[2])]
        if not cands:
            return
        res = reserve_needed(state)
        best = None
        for t in sorted(cands, key=lambda t: (-cast_score(state, t[0], t[1], t[2]), t[0], t[2])):
            name, zone, face = t
            sc = cast_score(state, name, zone, face)
            g, pips = effective_cost(state, name, choose_x(state, name) if (CARD_DB[name].is_x and face != "adventure") else 0, face if face in ("adventure", "warp") else "front")
            if res and sc < 60 and available_mana(state, CARD_DB[name]) - g - len(pips) < res:
                continue
            best = t
            break
        if best is None:
            return
        if not execute_cast(state, best):
            failed.append(best[0] + best[1] + str(best[2]))


def execute_cast(state: GameState, best: tuple) -> bool:
    """Executa UMA conjuracao escolhida (name, zone, face) de `castable_candidates`: mao, comandante, exilio de aventura, retrace da Six ou Muldrotha. Devolve se resolveu."""
    name, zone, face = best
    ok = False
    if zone == "hand":
        ok = cast_card(state, name, x=choose_x(state, name) if CARD_DB[name].is_x else 0, zone="hand", face=face if face in ("adventure", "warp") else "front")
    elif zone == "cz":
        ok = cast_commander(state)
    elif zone == "warpexile":
        item = next(i for i in state.warp_exile if i[0] == name)
        state.warp_exile.remove(item)
        ok = cast_card(state, name, zone="exile")
        if ok:
            state.warp_recasts += 1
        else:
            state.warp_exile.append(item)
    elif zone == "exile":
        state.adventure_exile.remove(name)
        ok = cast_card(state, name, zone="exile")
        if not ok:
            state.adventure_exile.append(name)
    elif zone.startswith("graveyard"):
        perm = zone.split(":")[1]
        g, pips = effective_cost(state, name)
        if perm == "six":
            lands_h = [h for h in state.hand if "land" in CARD_DB[h].types and "mdfc" not in CARD_DB[h].tags]
            if lands_h and can_pay(state, g, pips, CARD_DB[name]):
                d = min(lands_h, key=lambda h: land_play_score(state, h))
                state.graveyard.remove(name)              # CR 601.2a: a carta vai pra pilha ANTES de pagar o custo (descartar o terreno nao pode devolve-la)
                graveyard_leave(state, [name])
                state.hand.remove(d)
                put_card_into_graveyard(state, d, "hand")
                ok = cast_card(state, name, zone="graveyard")
                state.six_retraces += 1
                state.recursion_events_total += 1
        else:
            state.graveyard.remove(name)
            graveyard_leave(state, [name])
            state.muldrotha_used.append(face)
            state.muldrotha_plays += 1
            state.recursion_events_total += 1
            ok = cast_card(state, name, zone="graveyard")
    return ok


def landfall_payoff_options(state: GameState) -> list:
    """Payoffs de landfall que posso conjurar AGORA (mao, ou retrace da Six/Muldrotha), no formato de `castable_candidates`. Funcao pura: nao mexe em nenhum contador de estatistica
    (por isso nao chama `castable_candidates`, que conta mills voluntarios bloqueados)."""
    opts = []
    for name in sorted(LANDFALL_PAYOFFS):
        if name in state.hand and can_cast_name(state, name):
            opts.append((name, "hand", "front"))
    for name, perm, slot in graveyard_cast_options(state):
        if name in LANDFALL_PAYOFFS:
            g, pips = effective_cost(state, name)
            if can_pay(state, g, pips, CARD_DB[name]):
                opts.append((name, "graveyard:" + perm, slot))
    return opts


def _hoist_loses_a_play(state: GameState, t: tuple, phase: str) -> bool:
    """Ensaio a seco (copia profunda; `random` global restaurado) do RESTO da fase nas duas ordens: ANTIGA (terreno, depois o loop de conjuracao) e NOVA (`t` conjurado antes do terreno, depois o mesmo resto).
    Perde jogada se algo que a ordem antiga tiraria da mao (terrenos nao contam: o Icetill troca terreno da mao pelo do cemiterio) deixa de sair na nova, ou se o comandante deixa de ser conjurado."""
    def resto(s):
        play_land_phase(s)
        for _ in range(12):
            if s.game_over:
                return
            fp = _fingerprint(s)
            cast_loop(s, phase)
            play_land_phase(s)
            use_spare_mana(s, phase)
            if _fingerprint(s) == fp:
                break
    saved = random.getstate()
    try:
        mao0 = collections.Counter(state.hand)
        antiga = copy.deepcopy(state)
        resto(antiga)
        nova = copy.deepcopy(state)
        execute_cast(nova, t)
        resto(nova)
        sai_a, sai_n = mao0 - collections.Counter(antiga.hand), mao0 - collections.Counter(nova.hand)
        perdeu = {c: k for c, k in (sai_a - sai_n).items() if "Land" not in CARD_DB[c].types}
        return bool(perdeu) or (not antiga.commander_in_cz and nova.commander_in_cz)
    finally:
        random.setstate(saved)


def cast_landfall_payoffs_first(state: GameState, phase: str):
    """Ordem real de jogo: com um terreno ainda por jogar, conjura ANTES o payoff de landfall (Ruin Crab, Icetill Explorer, Evolution Sage) se o mana de AGORA ja' o paga,
    para que o terreno do turno (e o buscado por ele, e os do cemiterio) dispare o landfall. Achado na partida manual #1 (2026-10-06): o simulador jogava sempre o terreno primeiro.
    NAO mexe no que o jogador conjuraria no turno: so' muda a ORDEM de um payoff que o turno ja' pagaria com o mana de agora; o comandante tem prioridade (nao o deslocamos);
    o retrace da Six so' conta se sobra outro terreno para jogar depois do descarte."""
    if not LANDFALL_PAYOFF_FIRST:
        return
    failed = []
    for _ in range(4):
        if state.game_over or state.lands_played_this_turn >= land_drops_available(state):
            return
        hand_lands, cands = land_play_candidates(state)
        if not cands:
            return
        opts = [t for t in landfall_payoff_options(state)
                if t[0] + t[1] + str(t[2]) not in failed and not cast_blocked(state, t[0], t[2])
                and not (t[1].startswith("graveyard") and len(hand_lands) < 2)]
        if not opts:
            return
        t = max(opts, key=lambda t: (cast_score(state, t[0], t[1], t[2]), t[0]))
        if LANDFALL_GUARD_DRYRUN:
            if _hoist_loses_a_play(state, t, phase):
                return                    # o payoff antes do terreno faria o turno perder uma jogada nao-terreno (comandante, rocha, ...): fica na ordem antiga
        elif state.commander_in_cz:
            g_c, pips_c = effective_cost(state, COMMANDER)
            g_p, pips_p = effective_cost(state, t[0])
            cmd_cost, pay_cost, mana_now = g_c + len(pips_c), g_p + len(pips_p), available_mana(state)
            if cmd_cost <= mana_now + 1 and pay_cost + cmd_cost > mana_now + 1:
                return                    # o comandante seria conjurado neste turno e o payoff o impediria: nao desloca o comandante
        if execute_cast(state, t):
            state.payoff_first_casts += 1
        else:
            failed.append(t[0] + t[1] + str(t[2]))


# =========================================================
# BIBLIOTECA: guarda contra self-deck voluntario
# =========================================================
SELF_MILL_GUARD_ENABLED = True
SELF_MILL_RESERVE = 8                 # nao fazer mill VOLUNTARIO que deixe menos que isso na biblioteca
ORB_CAST_MIN_LIBRARY = 30             # nao conjurar Mesmeric Orb com biblioteca menor que isso (ele me mila a cada untap)
PALANTIR_OPP_SMART = True             # oponente recusa o Palantir quando o X deixaria minha biblioteca vazia
JACE_STATIC_ENABLED = True            # "If you would draw a card while your library has no cards in it, you win the game instead." (regra da carta; so' age com o Jace em campo)
JACE_WIN_LINE = True                  # linha de jogo com o Jace em campo: reserva de auto-mill vira 0, +1 em MIM com biblioteca <= 2, -8 com biblioteca <= 7, Kozilek nao e' descartado/embaralhado. False = Jace so' como motor (guarda de biblioteca intacta, +1 so' em oponente)
JACE_REMOVAL_PROB = 0.0               # sensibilidade: chance por rodada de oponentes do Jace sair (ataque/remocao de oponente nao e' simulado); 0 = nunca
RIVERCHURN_ACTIVATE = True            # False: o Monument so' entra em campo (artefato, Altar of the Brood, Mesmeric Orb); nenhuma das duas ativadas e' usada
RIVERCHURN_SELF = False               # alvos: tambem EU (so' quando `safe_self_mill` deixa); "any number of target players" inclui o proprio controlador
RIVERCHURN_OPP_END_STEP = False       # linha real: a mana que SOBROU do meu turno (inclusive a segurada pras contramagicas) paga o Monument no fim do ultimo turno de oponente, antes do meu untap (instante)
RIVERCHURN_TAP_FIRST = False         # limite SUPERIOR: o {1} do Monument e' pago ANTES do laco de conjuracao (so' com o comandante ja' em campo); padrao: so' com mana sobrando (limite inferior)
RIVERCHURN_EXHAUST_MIN = 24           # Exhaust (uma vez por objeto): so' quando a soma dos cemiterios dos oponentes vivos >= isto, ou quando algum oponente morre (cemiterio >= biblioteca)


def library_budget(state: GameState) -> int:
    """Quantas cartas ainda posso 'gastar' (mill voluntario, compra opcional, atacante a mais) sem me decar: biblioteca - reserva - o que JA esta a caminho
    (Orb: um mill por permanente meu virado, no proximo untap; rad counters; proximo Palantir)."""
    pend = 0
    if has_perm(state, "Mesmeric Orb"):
        pend += sum(1 for p in state.battlefield if p.tapped)
    pend += state.rad
    for pal in perms_named(state, "Palantír of Orthanc"):
        pend += pal.ctr.get("influence", 0) + 1
    return len(state.library) - (0 if jace_line(state) else SELF_MILL_RESERVE) - pend


def safe_self_mill(state: GameState, n: int) -> bool:
    if not SELF_MILL_GUARD_ENABLED:
        return True
    ok = library_budget(state) - n >= 0
    if not ok:
        state.self_mill_blocked_total += 1
    return ok


# =========================================================
# UNTAP, UPKEEP, RAD, COMPRA
# =========================================================

def untap_my_permanents(state: GameState):
    """Untap step. Mesmeric Orb: 'Whenever a permanent becomes untapped, that permanent's controller mills a card.' Um gatilho POR permanente (cada um e' um
    evento de mill separado: o Mothman dispara em cada um)."""
    tapped = [p for p in state.battlefield if p.tapped]
    for p in tapped:
        p.tapped = False
    orbs = count_named(state, "Mesmeric Orb")
    if orbs and tapped:
        for _ in range(len(tapped) * orbs):
            if state.game_over:
                return
            state.orb_untap_triggers += 1
            state.orb_mills_total += 1
            mill_event(state, [(0, 1)], source="mesmeric_orb")


def gitrog_upkeep(state: GameState):
    """The Gitrog Monster: 'At the beginning of your upkeep, sacrifice The Gitrog Monster unless you sacrifice a land.' Sacrificar terreno e' bom (compra 1 pela propria Gitrog, e
    Icetill/Muldrotha rejogam) a nao ser que eu esteja curto de terrenos."""
    for g in perms_named(state, "The Gitrog Monster"):
        lands = lands_in_play(state)
        if len(lands) >= 4:
            victim = min(lands, key=lambda p: (land_play_score_perm(state, p), p.uid))
            state.battlefield.remove(victim)
            if victim.card.name == "Urza's Saga" or victim.copy_of:
                pass
            put_card_into_graveyard(state, victim.card.name, "battlefield", sacrificed=True)
        else:
            remove_permanent(state, g, "sacrificed", sacrificed=True)


def land_play_score_perm(state: GameState, p: Permanent) -> float:
    """Valor de MANTER um terreno em campo (menor = sacrifico primeiro)."""
    c = p.card
    sc = 0.0
    have = colors_in_play(state)
    for col in sorted(c.produces & ANY_BGU):
        sc += 8.0 / max(1, have[col])
    if c.tags & {"strip_mine", "swarmyard", "yavimaya_hollow", "plaza"}:
        sc -= 3.0
    if "fetch" in c.tags:
        sc -= 6.0
    if "urzas_saga" in c.tags:
        sc -= 5.0
    if "basic" in c.tags and len(c.produces) == 1:
        sc += 0.5
    if p.tapped:
        sc -= 0.2
    return sc


def draw_step(state: GameState):
    if state.turn == 1 and state.on_play:
        return
    draw_cards(state, 1, source="normal")


def begin_any_turn(state: GameState):
    """Inicio de QUALQUER turno (meu ou de oponente): zera os limites 'uma vez a cada turno' (Mirelurk Queen, Deepmuck, Freestrider, Hollowmurk Sultai, Terrasymbiosis, Danny Pink)."""
    state.turn_id += 1
    state.crime_this_turn = {}
    state.queen_triggered_this_turn = False
    state.hollowmurk_triggered_this_turn = False
    state.terrasymbiosis_used = False


def upkeep_step(state: GameState):
    state.lands_played_this_turn = 0
    state.muldrotha_used = []
    state.spells_cast_this_turn = 0
    state.attackers_this_turn = []
    state.pool = {}
    for o in state.opps:
        o.lost_life_this_turn = 0
    state.opp_lost_life_this_turn = False
    for p in state.battlefield:
        p.temp_power = 0
        p.temp_trample = False
        p.crewed = False
        if p.copy_of is not None:
            p.copy_of = None          # Shifting Woodland: a copia durou so' ate o fim do turno anterior
    gitrog_upkeep(state)
    for _ in range(state.pending_denial_me):
        draw_cards(state, 1, source="arcane_denial")
    state.pending_denial_me = 0


def saga_lore_step(state: GameState):
    """CR 714.2b: o contador de conhecimento entra no INICIO da fase principal 1, depois da compra, para cada Saga."""
    for p in list(state.battlefield):
        if "urzas_saga" in p.card.tags and p in state.battlefield and p.ctr.get("lore", 0) < 3:
            saga_add_lore(state, p)


def rad_trigger_self(state: GameState):
    """CR 728.1: no inicio da fase principal 1 do jogador com rad counters, ele mila cartas = numero de rad counters; para cada carta NAO-terreno milada, perde 1 de vida e remove 1 rad counter."""
    n = state.rad
    if n <= 0 or state.game_over:
        return
    state.rad_triggers_self += 1

    def before(res):
        cards = res.get(0, [])
        nl = sum(1 for c in cards if not is_land_card_name(c))
        if nl:
            state.rad = max(0, state.rad - nl)
            state.rad_life_lost_self_total += nl
            lose_life_self(state, nl, "rad")
    mill_event(state, [(0, n)], source="rad", before_triggers=before)


def rad_trigger_opp(state: GameState, o: Opp):
    n = o.rad
    if n <= 0 or o.eliminated or state.game_over:
        return

    def before(res):
        cards = res.get(o.idx, [])
        nl = sum(1 for c in cards if c != "L")
        if nl:
            o.rad = max(0, o.rad - nl)
            lose_life_opp(state, o.idx, nl, "rad")
    mill_event(state, [(o.idx, n)], source="rad", before_triggers=before)


# =========================================================
# FIM DE TURNO
# =========================================================

def scry_value(state: GameState, c: str) -> float:
    """Quanto quero comprar `c` (scry do Palantir): terreno enquanto me faltam; Kozilek so' com mana pra conjurar; resto pela prioridade."""
    cc = CARD_DB[c]
    held_lands = sum(1 for h in state.hand if "land" in CARD_DB[h].types and "mdfc" not in CARD_DB[h].tags)
    if "land" in cc.types and "mdfc" not in cc.tags:
        return 60.0 if n_lands(state) + held_lands < 6 else 5.0
    if "kozilek" in cc.tags:
        return 55.0 if n_lands(state) >= 9 else 5.0
    return float(CAST_PRIORITY.get(c, 25))


def palantir_end_step(state: GameState):
    for pal in perms_named(state, "Palantír of Orthanc"):
        if state.game_over:
            return
        place_counters(state, pal, 1, kind="influence", source="palantir")
        # scry 2: cada carta fica no topo se vale mais que 30, senao vai pro fundo
        top = state.library[:2]
        del state.library[:2]
        keep = [c for c in top if scry_value(state, c) >= 30]
        bottom = [c for c in top if scry_value(state, c) < 30]
        state.library = keep + state.library + bottom
        al = alive_opps(state)
        if not al:
            return
        tgt = max(al, key=lambda o: (len(o.library), -o.idx))
        commit_crime(state, "palantir")                    # "target opponent"
        x = pal.ctr.get("influence", 0)
        lets_draw = state.proxy_rng.random() < PALANTIR_OPP_LETS_DRAW
        if PALANTIR_OPP_SMART and x >= len(state.library):
            lets_draw = False
        if lets_draw:
            state.palantir_draws += 1
            draw_cards(state, 1, source="palantir")
        else:
            state.palantir_mills += x

            def before(res, tgt=tgt):
                tot = sum(CARD_DB[c].mv for c in res.get(0, []) if not is_land_card_name(c))
                state.palantir_life_loss_total += tot
                lose_life_opp(state, tgt.idx, tot, "palantir")
            mill_event(state, [(0, x)], source="palantir", before_triggers=before)


def ascension_end_step(state: GameState):
    """Bloodchief Ascension: 'At the beginning of each end step, if an opponent lost 2 or more life this turn, you may put a quest counter.' (cada fim de turno, o meu e o dos oponentes)."""
    if any(o.lost_life_this_turn >= 2 for o in state.opps):
        for p in perms_named(state, "Bloodchief Ascension"):
            place_counters(state, p, 1, kind="quest", source="ascension")


def discard_value(state: GameState, c: str) -> float:
    cc = CARD_DB[c]
    if "kozilek" in cc.tags:
        if jace_line(state):
            return 90.0                                   # com o Jace em campo o embaralhar do Kozilek DESFAZ a biblioteca vazia: nao descarto
        # descartar o Kozilek e' o seguro: ele embaralha o cemiterio na biblioteca
        return -10.0 if len(state.library) < 25 else (10.0 if n_lands(state) < 9 else 55.0)
    if "land" in cc.types and "mdfc" not in cc.tags:
        return 6.0 if n_lands(state) >= 7 else 45.0
    return float(CAST_PRIORITY.get(c, 25)) + 0.1 * cc.mv


def discard_to_hand_size(state: GameState):
    while len(state.hand) > 7:
        c = min(state.hand, key=lambda x: (discard_value(state, x), x))
        state.hand.remove(c)
        put_card_into_graveyard(state, c, "hand")


def end_step(state: GameState):
    for _w in [q for q in state.battlefield if q.warped]:
        state.battlefield.remove(_w)                                      # "Exile this permanent at the beginning of the next end step"
        state.warp_exile.append((_w.card.name, state.turn))
        state.warp_exiled += 1
    palantir_end_step(state)
    if state.game_over:
        return
    ascension_end_step(state)
    discard_to_hand_size(state)
    for p in state.battlefield:
        if p.copy_of is not None:
            p.copy_of = None               # Shifting Woodland: 'until end of turn' acaba no cleanup
        p.temp_power = 0
        p.temp_trample = False
        p.crewed = False                   # Crew: 'until end of turn'


# =========================================================
# OPONENTES (passivos): untap/Orb, compra, rad, magias, contramagica
# =========================================================

COUNTER_MIN_MV = 3          # so' contra-mágica magias com MV >= isto (ameacas); o resto passa
OPP_NONPERMANENT_FRACTION = 0.6      # das magias NAO-criatura do oponente, fracao que e' instantanea/feitico (vai ao cemiterio dele ao resolver; as outras sao permanentes)


def opp_card_to_graveyard(state: GameState, o: Opp, kind: str):
    """Carta do oponente `o` vai ao cemiterio dele por causa que NAO e' mill (magia anulada, instantanea/feitico resolvida). Bloodchief Ascension (3+ marcadores): 'whenever a card is put
    into an opponent's graveyard from anywhere' — perde 2 / eu ganho 2 (ruling 2009-10-01: de qualquer zona)."""
    if o.eliminated:
        return
    o.graveyard.append(kind)
    if any(p.ctr.get("quest", 0) >= 3 for p in perms_named(state, "Bloodchief Ascension")) and not state.game_over:
        ascension_hit(state, o.idx)


def respond_to_opp_spell(state: GameState, o: Opp, noncreature: bool, mv: int) -> bool:
    """Tenta anular a magia do oponente `o`. Devolve True se anulou. Ordem: gratis (Fierce Guardianship) -> Glen Elendra (persist, so' {U}) -> contramagicas da mao."""
    if mv < COUNTER_MIN_MV or not state.hand and not has_perm(state, "Glen Elendra Archmage"):
        return False
    # Glen Elendra Archmage: {U}, sacrifice: counter target noncreature spell (persist devolve; Great Henge cancela o -1/-1)
    if noncreature:
        glens = [p for p in perms_named(state, "Glen Elendra Archmage") if p.ctr.get("minus1", 0) == 0]
        if glens and can_pay(state, 0, (frozenset("U"),)):
            pay_mana(state, 0, (frozenset("U"),))
            state.counterspells_cast += 1
            state.opp_spells_countered_total += 1
            commit_crime(state, "counter_glen")
            remove_permanent(state, glens[0], "sacrificed", sacrificed=True)
            opp_card_to_graveyard(state, o, "N" if noncreature else "C")
            return True
    order = ["Fierce Guardianship", "An Offer You Can't Refuse", "Negate", "Arcane Denial", "Didn't Say Please", "Repulsive Mutation"]
    for name in order:
        if name not in state.hand:
            continue
        if name in ("Fierce Guardianship", "An Offer You Can't Refuse", "Negate") and not noncreature:
            continue
        free = (name == "Fierce Guardianship" and free_cast_possible(state, name))
        xr = 0
        if name == "Repulsive Mutation":
            # {X}{G}{U}: X contadores numa criatura minha + 'counter up to one target spell unless its controller pays mana equal to the greatest power among creatures you control'
            if not creatures(state):
                continue
            g0, p0 = effective_cost(state, name, 0)
            xr = max_x(state, g0, p0, 1, CARD_DB[name])
            if xr < 1:
                continue
        g, pips = effective_cost(state, name, xr)
        if not free and not can_pay(state, g, pips, CARD_DB[name]):
            continue
        if not free:
            pay_mana(state, g, pips, CARD_DB[name])
        state.hand.remove(name)
        state.spells_cast_this_turn += 1
        on_my_spell_cast(state, name)
        if name == "Repulsive Mutation":
            tgt = max(creatures(state), key=lambda q: (counter_target_value(state, q), -q.uid))
            place_counters(state, tgt, xr, source="repulsive_mutation")
            greatest = max(power(state, q) for q in creatures(state))
            put_card_into_graveyard(state, name, "stack")
            commit_crime(state, "counter")
            if o.lands - mv >= greatest:
                return False               # o oponente paga o imposto: a magia dele resolve (os contadores ficam)
        state.counterspells_cast += 1
        state.opp_spells_countered_total += 1
        opp_card_to_graveyard(state, o, "N" if noncreature else "C")      # a magia anulada vai ao cemiterio do dono
        if name != "Repulsive Mutation":
            put_card_into_graveyard(state, name, "stack")
            commit_crime(state, "counter")                     # alvo: magia de oponente
        if name == "Didn't Say Please":
            mill_event(state, [(o.idx, 3)], source="didnt_say_please")
        elif name == "Arcane Denial":
            o.pending_denial_draw = 2
            state.pending_denial_me += 1
        return True
    return False


def opp_untap_and_orb(state: GameState, o: Opp):
    n = o.tapped_last_turn
    o.tapped_last_turn = 0
    if n > 0 and has_perm(state, "Mesmeric Orb"):
        # "Whenever a permanent becomes untapped, that permanent's controller mills a card": um gatilho por permanente do OPONENTE
        for _ in range(n):
            if o.eliminated or state.game_over:
                return
            state.orb_untap_triggers += 1
            mill_event(state, [(o.idx, 1)], source="mesmeric_orb")


def opponent_turn(state: GameState, o: Opp):
    if o.eliminated or state.game_over:
        return
    o.turns_taken += 1
    state.opp_turns_total += 1
    begin_any_turn(state)
    rng = opp_rng(state, o)
    for x in state.opps:
        x.lost_life_this_turn = 0          # "this turn" = o turno ATUAL (Bloodchief Ascension olha qualquer oponente)
    state.opp_lost_life_this_turn = False
    # upkeep: Arcane Denial
    if o.pending_denial_draw:
        for _ in range(o.pending_denial_draw):
            if o.library:
                o.library.pop(0)
                o.hand_size += 1
        o.pending_denial_draw = 0
    opp_untap_and_orb(state, o)
    if o.eliminated or state.game_over:
        return
    # compra (nao pula: o primeiro jogador sou eu)
    if not o.library:
        eliminate_opp(state, o, "decked")
        return
    o.library.pop(0)
    o.hand_size += 1
    # rad no inicio da fase principal 1
    rad_trigger_opp(state, o)
    if o.eliminated or state.game_over:
        return
    if MASTER_OPP_TURN and has_perm(state, "The Master, Transcendent") and act_master(state):
        state.master_act_on_opp_phase += 1
    # terreno
    if o.hand_size > 0 and rng.random() < (0.8 if o.turns_taken <= 8 else 0.35):
        o.lands += 1
        o.hand_size -= 1
    # magias
    if o.turns_taken == 1:
        nspells = 1 if rng.random() < 0.15 else 0
    else:
        r = rng.random()
        nspells = 0 if r < OPP_SPELLS_PROB[0] else (1 if r < OPP_SPELLS_PROB[0] + OPP_SPELLS_PROB[1] else 2)
    mana = o.lands
    spent = 0
    for _ in range(nspells):
        if o.hand_size <= 0 or o.eliminated or state.game_over:
            break
        mv = rng.choices(OPP_SPELL_MV, weights=OPP_SPELL_MV_W)[0]
        creature = rng.random() < OPP_CREATURE_SPELL_FRACTION
        if mv > mana - spent:
            mv = max(0, mana - spent)
            if mv == 0:
                break
        spent += mv
        o.hand_size -= 1
        o.spells_total += 1
        state.opp_spells_total += 1
        if not creature:
            state.opp_noncreature_spells_total += 1
        # gatilhos de "whenever an opponent casts": Memory Erosion e Pollywog Prodigy
        for _ in range(count_named(state, "Memory Erosion")):
            state.memory_erosion_mills += 1
            state.memory_erosion_events += 1
            mill_event(state, [(o.idx, 2)], source="memory_erosion")
        if o.eliminated or state.game_over:
            break
        if not creature:
            for pw in perms_named(state, "Pollywog Prodigy"):
                if mv < power(state, pw):
                    state.pollywog_draws += 1
                    draw_cards(state, 1, source="pollywog")
        if not respond_to_opp_spell(state, o, noncreature=not creature, mv=mv):
            if not creature and rng.random() < OPP_NONPERMANENT_FRACTION and not o.eliminated and not state.game_over:
                opp_card_to_graveyard(state, o, "N")            # instantanea/feitico resolvido vai ao cemiterio
    o.tapped_last_turn = min(o.lands, int(round(o.lands * OPP_TAP_FRACTION)))
    # fim do turno do oponente: Bloodchief Ascension
    if not state.game_over:
        ascension_end_step(state)


# =========================================================
# HABILIDADES ATIVADAS (mana ociosa e acoes sem custo de mana)
# =========================================================

def ability_pips(state: GameState, pips: tuple, creature_ability: bool) -> tuple:
    """Agatha's Soul Cauldron: 'You may spend mana as though it were mana of any color to activate abilities of creatures you control.' (mana incolor NAO e' uma cor)."""
    if creature_ability and has_perm(state, "Agatha's Soul Cauldron"):
        return tuple(ANY_BGU for _ in pips)
    return pips


def afford(state: GameState, generic: int, pips: tuple = (), creature: bool = False, ignore_reserve: bool = False) -> bool:
    pp = ability_pips(state, pips, creature)
    if not can_pay(state, generic, pp):
        return False
    if ignore_reserve:
        return True
    r = reserve_needed(state)
    return not r or available_mana(state) - generic - len(pp) >= r


def spend(state: GameState, generic: int, pips: tuple = (), creature: bool = False) -> bool:
    pp = ability_pips(state, pips, creature)
    ok = pay_mana(state, generic, pp)
    if ok:
        state.mana_spent_total += generic + len(pp)
    return ok


def has_granted(state: GameState, p: Permanent, name: str) -> bool:
    """Agatha's Soul Cauldron: criaturas minhas COM contador +1/+1 tem todas as ativadas das cartas de criatura exiladas com ela."""
    return CAULDRON_ABILITIES_ENABLED and has_perm(state, "Agatha's Soul Cauldron") and p.counters > 0 and name in state.cauldron_exiled


def can_tap_creature(state: GameState, p: Permanent) -> bool:
    return is_creature(p) and not p.tapped and (p.entered_turn < state.turn or has_haste(state, p))


def orb_untap(state: GameState, n: int = 1):
    """Mesmeric Orb: cada permanente MEU que desvira por efeito (Minamo) me mila 1."""
    for _ in range(n * count_named(state, "Mesmeric Orb")):
        if state.game_over:
            return
        state.orb_untap_triggers += 1
        state.orb_mills_total += 1
        mill_event(state, [(0, 1)], source="mesmeric_orb")


def graveyard_leave(state: GameState, names: list):
    """Syr Konrad, 3a clausula: 'or a creature card leaves your graveyard' — 1 de dano a cada oponente por carta de criatura que sai do MEU cemiterio (para qualquer zona)."""
    n_c = sum(1 for c in names if "creature" in CARD_DB[c].types and not CARD_DB[c].token)
    if n_c:
        for _ in range(count_named(state, "Syr Konrad, the Grim") * n_c):
            if state.game_over:
                return
            state.konrad_graveyard_leave_pings += 1
            konrad_ping(state, 1)


def best_opp_library(state: GameState) -> Optional[Opp]:
    al = [o for o in alive_opps(state) if o.library]
    if not al:
        return None
    return max(al, key=lambda o: (len(o.library), -o.idx))


def lowest_life_opp(state: GameState) -> Optional[Opp]:
    al = alive_opps(state)
    if not al:
        return None
    return min(al, key=lambda o: (o.life, o.idx))


# --- Saga: construct -----------------------------------------------------------
def act_saga_construct(state: GameState) -> bool:
    for p in state.battlefield:
        if "urzas_saga" in p.card.tags and p.ctr.get("lore", 0) >= 2 and not p.tapped:
            if afford(state, 2):
                # o proprio terreno e' o {T}: marcar antes pra que o pagamento nao o use como fonte
                p.tapped = True
                if spend(state, 2):
                    state.construct_tokens += 1
                    create_token(state, "Construct Token")
                    return True
                p.tapped = False
    return False


# --- Ashiok ---------------------------------------------------------------------
def act_ashiok(state: GameState) -> bool:
    for p in perms_named(state, "Ashiok, Dream Render"):
        if p.used_ability_turn == state.turn or p.ctr.get("loyalty", 0) <= 0:
            continue
        tgt = best_opp_library(state)
        if tgt is None:
            continue
        p.used_ability_turn = state.turn
        p.ctr["loyalty"] -= 1
        state.ashiok_uses += 1
        commit_crime(state, "ashiok")                      # "Target player" = oponente
        mill_event(state, [(tgt.idx, 4)], source="ashiok")
        for o in state.opps:
            o.graveyard.clear()                            # "Then exile each opponent's graveyard."
        if p.ctr["loyalty"] <= 0 and p in state.battlefield:
            state.battlefield.remove(p)
            put_card_into_graveyard(state, p.card.name, "battlefield")
        return True
    return False


# --- Jace, Wielder of Mysteries (2026-10-07) ---------------------------------------------------------------------------
def act_jace(state: GameState) -> bool:
    """Uma habilidade de lealdade por turno (sorcery speed). +1: "Target player mills two cards. Draw a card." (ordem do texto: mila, depois compro; alvo ilegal = nao resolve e nao compro, ruling 2019-05-03).
    -8: "Draw seven cards. Then if your library has no cards in it, you win the game." (Jace ja' saiu de campo quando resolve: compro o que der e venco, ruling; vence com biblioteca <= 7).
    Linha de vitoria (JACE_WIN_LINE): com biblioteca <= 2 o +1 em MIM esvazia a biblioteca e a compra seguinte vence; sem a linha, so' mirando oponente e so' com biblioteca acima da reserva."""
    for p in perms_named(state, "Jace, Wielder of Mysteries"):
        if p.used_ability_turn == state.turn or p.ctr.get("loyalty", 0) <= 0:
            continue
        lib = len(state.library)
        if JACE_WIN_LINE and p.ctr.get("loyalty", 0) >= 8 and lib <= 7:
            p.used_ability_turn = state.turn
            p.ctr["loyalty"] -= 8
            state.jace_minus8_uses += 1
            if p in state.battlefield and p.ctr["loyalty"] <= 0:
                state.battlefield.remove(p)
                put_card_into_graveyard(state, p.card.name, "battlefield")      # sai antes de resolver: o estatico nao vale mais, quem vence e' o proprio -8
            k = min(7, len(state.library))
            for _ in range(k):
                draw_cards(state, 1, source="jace")
                state.jace_draws += 1
                if state.game_over:
                    return True
            if not state.library:
                jace_win(state)
            return True
        self_target = JACE_WIN_LINE and lib <= 2
        if self_target:
            parts = [(0, 2)]
        else:
            tgt = best_opp_library(state)
            if tgt is None or (not JACE_WIN_LINE and lib <= SELF_MILL_RESERVE):
                continue
            parts = [(tgt.idx, 2)]
            commit_crime(state, "jace")                                     # "Target player" = oponente
        p.used_ability_turn = state.turn
        p.ctr["loyalty"] = p.ctr.get("loyalty", 0) + 1
        state.jace_plus_uses += 1
        if self_target:
            state.jace_plus_self += 1
        mill_event(state, parts, source="jace")
        if state.game_over:
            return True
        draw_cards(state, 1, source="jace")                                  # biblioteca vazia + Jace em campo: vitoria (draw_cards)
        state.jace_draws += 1
        return True
    return False


HORRIGAN_PROLIF_TIMES = 2    # "proliferate twice" (oraculo). 0 = sensibilidade: so' o corpo (8/6 trample, indestrutivel ao atacar), sem proliferate
MASTER_OPP_TURN = True       # usa a habilidade tambem no turno dos oponentes (instante; a Master so' desvira no meu untap)
MASTER_TAKE_OPP = True       # pode levar criatura milada do cemiterio de OPONENTE (corpo generico 3/3 sem habilidades: piso)


def master_ready(state: GameState, p: Permanent) -> bool:
    if p.tapped or p not in state.battlefield or not is_creature(p):
        return False
    return p.entered_turn < state.turn or has_haste(state, p)       # criatura com {T}: doenca de invocacao (Swiftfoot Boots da' haste)


def master_candidates(state: GameState) -> list:
    out = []
    for name, tid in state.milled_mine:
        if tid == state.turn_id and name in state.graveyard:
            out.append(("mine", name, graveyard_value(state, name)))
    if MASTER_TAKE_OPP:
        for pl, (tid, n) in sorted(state.milled_opp_creatures.items()):
            if tid == state.turn_id and state.opps[pl - 1].graveyard.count("C") > 0 and n > 0 and not state.opps[pl - 1].eliminated:
                out.append(("opp", pl, 50.0))
    return out


def act_master(state: GameState) -> bool:
    """The Master, Transcendent: "{T}: Put target creature card in a graveyard that was milled this turn onto the battlefield under your control. It's a green Mutant with base
    power and toughness 3/3. (It loses its other colors and creature types.)" Alvo em QUALQUER cemiterio; so' 'mill' (ruling 2024-03-08)."""
    ms = [p for p in perms_named(state, "The Master, Transcendent") if master_ready(state, p)]
    if not ms or state.game_over:
        return False
    cands = master_candidates(state)
    if not cands:
        state.master_no_target_checks += 1
        return False
    kind, who, _ = max(cands, key=lambda c: (c[2], str(c[1])))
    m_perm = ms[0]
    m_perm.tapped = True
    state.master_activations += 1
    if state.turn_id != getattr(state, "_my_turn_id", state.turn_id):
        pass
    if kind == "mine":
        state.graveyard.remove(who)
        graveyard_leave(state, [who])
        q = mk_perm(state, who)
        state.master_act_mine += 1
        state.master_names[who] = state.master_names.get(who, 0) + 1
    else:
        o = state.opps[who - 1]
        o.graveyard.remove("C")
        tid, n = state.milled_opp_creatures[who]
        state.milled_opp_creatures[who] = (tid, n - 1)
        q = mk_perm(state, "Opponent Creature Card")
        q.owner_idx = who
        state.master_act_opp += 1
        state.master_names["(oponente)"] = state.master_names.get("(oponente)", 0) + 1
    q.base_pt = (3, 3)
    q.mutant = True
    state.battlefield.append(q)
    enter_permanent_triggers(state, q, from_cast=False)
    return True


PERSIST_ZERO_TOUGHNESS_DIES = True   # Glen Elendra volta do persist com tenacidade 0 (Constrictor: 2 contadores; Loading Zone: 2): morre (CR 704.5f). False = o 0/0 ficava em campo (antigo)
SCORCH_MIN_X = 3             # Scorchbeast: cria os Zumbis no 1o evento de mill do turno com >= X cartas nao-terreno (senao espera: o gatilho volta)


def on_my_spell_cast(state: GameState, name: str):
    """"Whenever you cast a spell": Inexorable Tide ("proliferate"); o gatilho resolve ANTES da magia (ruling 2011-01-01). Chamada nos 4 pontos de conjuracao."""
    for _ in range(count_named(state, "Inexorable Tide")):
        state.tide_triggers += 1
        proliferate(state, "inexorable_tide")


def act_fractured_cycle(state: GameState) -> bool:
    """Fractured Sanity: Cycling {1}{U}; "When you cycle this card, each opponent mills four cards." (resolve ANTES da compra, ruling 2021-06-18). Politica: cicla quando o UUU nao fecha
    (menos de 3 fontes de {U} em campo) e ha mana de sobra; senao a conjuro (sorcery) no loop de conjuracao."""
    if "Fractured Sanity" not in state.hand or not alive_opps(state) or state.game_over:
        return False
    if can_cast_name(state, "Fractured Sanity"):
        return False
    n_u = sum(1 for q in lands_in_play(state) if "U" in eff_card(q).produces)
    if n_u >= 3 and state.turn < 9:
        return False
    if SELF_MILL_GUARD_ENABLED and library_budget(state) < 1:
        return False
    U = frozenset("U")
    if not afford(state, 1, (U,)):
        return False
    spend(state, 1, (U,))
    state.hand.remove("Fractured Sanity")
    state.fractured_cycles += 1
    put_card_into_graveyard(state, "Fractured Sanity", "hand")
    mill_event(state, [(o.idx, 4) for o in alive_opps(state)], source="fractured_cycle")
    if not state.game_over:
        draw_cards(state, 1, source="cycling")
    return True


def act_earth_crystal(state: GameState) -> bool:
    """The Earth Crystal: "{4}{G}{G}, {T}: Distribute two +1/+1 counters among one or two target creatures you control." (cada alvo recebe pelo menos 1; ruling 2025-06-06).
    Dois alvos quando ha (cada um passa pelos amplificadores/dobradores), um so' se so' ha uma criatura."""
    for c in perms_named(state, "The Earth Crystal"):
        if c.tapped or not creatures(state):
            continue
        G = frozenset("G")
        c.tapped = True
        if not afford(state, 4, (G, G)):
            c.tapped = False
            continue
        spend(state, 4, (G, G))
        alvos = sorted(creatures(state), key=lambda q: (-counter_target_value(state, q), q.uid))[:2]
        state.crystal_activations += 1
        if len(alvos) == 1:
            state.crystal_counters += place_counters(state, alvos[0], 2, source="earth_crystal")
        else:
            for q in alvos:
                state.crystal_counters += place_counters(state, q, 1, source="earth_crystal")
        return True
    return False


def jace_removal_roll(state: GameState):
    """Sensibilidade JACE_REMOVAL_PROB: depois da rodada dos oponentes, chance de o Jace sair (ataque/remocao nao simulados). Usa `proxy_rng` so' com a chave > 0 e o Jace em campo."""
    if JACE_REMOVAL_PROB <= 0 or state.game_over:
        return
    for p in perms_named(state, "Jace, Wielder of Mysteries"):
        if state.proxy_rng.random() < JACE_REMOVAL_PROB:
            state.battlefield.remove(p)
            put_card_into_graveyard(state, p.card.name, "battlefield")
            state.jace_removed += 1


# --- Cauldron (+ Minamo) -------------------------------------------------------------
CAULDRON_VALUE = ["Kami of Whispered Hopes", "Gyre Sage", "Zellix, Sanity Flayer", "Syr Konrad, the Grim", "Cankerbloom", "Walking Ballista", "Bramble Familiar // Fetch Quest",
                  "Evolution Witness", "Basking Broodscale"]


def cauldron_target(state: GameState):
    """Devolve ('opp', Opp) | ('own', nome) | None. Preferencia: criatura do cemiterio de OPONENTE (crime + contador); senao uma criatura MINHA cuja ativada vale a pena."""
    cands = [o for o in alive_opps(state) if "C" in o.graveyard]
    if cands:
        return ("opp", max(cands, key=lambda o: (o.graveyard.count("C"), -o.idx)))
    if CAULDRON_ABILITIES_ENABLED and any(p.counters > 0 and is_creature(p) for p in state.battlefield):
        for nm in CAULDRON_VALUE:
            if nm in state.graveyard and nm not in state.cauldron_exiled:
                return ("own", nm)
    return None


def cauldron_use(state: GameState, perm: Permanent) -> bool:
    tgt = cauldron_target(state)
    if tgt is None or perm.tapped:
        return False
    perm.tapped = True
    kind, what = tgt
    if kind == "opp":
        commit_crime(state, "cauldron")
        if "C" not in what.graveyard:
            return True                                    # o gatilho de crime (Deepmuck) mexeu no cemiterio: a habilidade e' anulada na resolucao
        what.graveyard.remove("C")
        state.cauldron_exiles_opp += 1
        state.cauldron_exiles_total += 1
        cs = creatures(state)
        if cs:
            best = max(cs, key=lambda q: (counter_target_value(state, q), -q.uid))
            place_counters(state, best, 1, source="cauldron")
            state.cauldron_counters_total += 1
    else:
        state.graveyard.remove(what)
        state.cauldron_exiled.append(what)
        state.cauldron_exiles_total += 1
        graveyard_leave(state, [what])
        cs = creatures(state)
        if cs:
            best = max(cs, key=lambda q: (counter_target_value(state, q), -q.uid))
            place_counters(state, best, 1, source="cauldron")
            state.cauldron_counters_total += 1
    return True


def act_cauldron(state: GameState) -> bool:
    for c in perms_named(state, "Agatha's Soul Cauldron"):
        if not c.tapped and cauldron_use(state, c):
            return True
    return False


def minamo_untap(state: GameState, target: Permanent) -> bool:
    """Minamo: '{U}, {T}: Untap target legendary permanent.' O proprio {T} de Minamo e' custo (nao pode ser a fonte do {U})."""
    if not MINAMO_ENABLED or not target.tapped:
        return False
    for m in perms_named(state, "Minamo, School at Water's Edge"):
        if m.tapped or m is target:
            continue
        m.tapped = True
        if afford(state, 0, (frozenset("U"),)) and spend(state, 0, (frozenset("U"),)):
            target.tapped = False
            state.minamo_untaps += 1
            orb_untap(state, 1)
            return True
        m.tapped = False
    return False


def act_minamo_henge(state: GameState) -> bool:
    """Minamo -> The Great Henge (lendaria): '{U},{T}: Untap target legendary permanent'. Saldo de mana ~0 (Minamo deixa de dar o proprio {U}); ganho: {T}: GG + 2 de vida. So' vale com vida baixa
    e sem Mesmeric Orb (cada desvirar me mila)."""
    if state.life >= 25 or has_perm(state, "Mesmeric Orb"):
        return False
    for h in perms_named(state, "The Great Henge"):
        if h.tapped and minamo_untap(state, h):
            return True
    return False


def act_cauldron_minamo(state: GameState) -> bool:
    for c in perms_named(state, "Agatha's Soul Cauldron"):
        if c.tapped and cauldron_target(state) is not None and minamo_untap(state, c):
            return True
    return False


# --- Zellix ---------------------------------------------------------------------------
def zellix_sources(state: GameState) -> list:
    out = []
    for p in state.battlefield:
        if not can_tap_creature(state, p):
            continue
        if "zellix" in eff_card(p).tags or has_granted(state, p, "Zellix, Sanity Flayer"):
            out.append(p)
    return out


def act_zellix(state: GameState) -> bool:
    srcs = zellix_sources(state)
    if not srcs or not afford(state, 1, (), creature=True):
        return False
    tgt = best_opp_library(state)
    if tgt is None:
        return False
    src = srcs[0]
    src.tapped = True                                      # {T} e' custo
    if not spend(state, 1, (), creature=True):
        src.tapped = False
        return False
    state.zellix_activations += 1
    commit_crime(state, "zellix")                          # "Target player": oponente
    mill_event(state, [(tgt.idx, 3)], source="zellix")
    return True


def act_zellix_minamo(state: GameState) -> bool:
    for z in state.battlefield:
        if z.tapped and is_creature(z) and ("zellix" in eff_card(z).tags) and z.entered_turn < state.turn:
            if best_opp_library(state) is not None and afford(state, 1, (frozenset("U"),), creature=False):
                if minamo_untap(state, z):
                    state.zellix_minamo_second += 1
                    return True
    return False


# --- Syr Konrad --------------------------------------------------------------------------
def konrad_available(state: GameState) -> bool:
    if has_perm(state, "Syr Konrad, the Grim"):
        return True
    return CAULDRON_ABILITIES_ENABLED and "Syr Konrad, the Grim" in state.cauldron_exiled and any(p.counters > 0 and is_creature(p) for p in state.battlefield)


def act_konrad(state: GameState) -> bool:
    if not konrad_available(state):
        return False
    if not afford(state, 1, (frozenset("B"),), creature=True):
        return False
    parts = [(0, 1)] + [(o.idx, 1) for o in alive_opps(state)]
    if len(parts) == 1 or not safe_self_mill(state, 1):
        return False
    spend(state, 1, (frozenset("B"),), creature=True)
    state.konrad_activations += 1
    mill_event(state, parts, source="konrad")
    return True


# --- Adapt (Broodscale, Evolution Witness) ----------------------------------------------------
def act_adapt(state: GameState) -> bool:
    for p in state.battlefield:
        t = eff_card(p).tags
        if p.counters > 0 or not is_creature(p):
            continue
        n = 1 if "broodscale" in t else (2 if "evo_witness" in t else 0)
        if n == 0:
            continue
        if afford(state, 1, (frozenset("G"),), creature=True):
            spend(state, 1, (frozenset("G"),), creature=True)
            state.adapt_total += 1
            place_counters(state, p, n, source="adapt")
            return True
    return False


# --- Cankerbloom ------------------------------------------------------------------------------------
def proliferate_value(state: GameState) -> float:
    v = sum(1.0 for p in state.battlefield if p.counters > 0 and is_creature(p))
    v += sum(2.0 for o in alive_opps(state) if o.rad > 0)
    v += sum(3.0 for p in perms_named(state, "Palantír of Orthanc") if p.ctr.get("influence", 0) > 0)
    v += sum(2.0 for p in perms_named(state, "Bloodchief Ascension") if 0 < p.ctr.get("quest", 0) < 3)
    v += sum(1.0 for p in perms_named(state, "Ashiok, Dream Render") if p.ctr.get("loyalty", 0) > 0)
    return v


def act_cankerbloom(state: GameState) -> bool:
    pf = proliferate_value(state)
    for p in state.battlefield:
        t = eff_card(p).tags
        has_it = "cankerbloom" in t or has_granted(state, p, "Cankerbloom")
        if not has_it or not is_creature(p) or p not in state.battlefield:
            continue
        if not afford(state, 1, (), creature=True):
            continue
        if pf >= 6:
            spend(state, 1, (), creature=True)
            state.cankerbloom_prolif += 1
            if "cankerbloom" in t:
                remove_permanent(state, p, "sacrificed", sacrificed=True)
            else:
                remove_permanent(state, p, "sacrificed", sacrificed=True)
            proliferate(state, "cankerbloom")
            return True
        # modo destruir artefato/encantamento: alvo de oponente = crime (so' com pagadores de crime e alvo disponivel)
        if (has_perm(state, "Deepmuck Desperado") or has_perm(state, "Freestrider Lookout")) and not all(state.crime_this_turn.get(k) for k in ("deepmuck", "freestrider")) and target_available(state):
            spend(state, 1, (), creature=True)
            state.interaction_plays += 1
            commit_crime(state, "cankerbloom_destroy")
            remove_permanent(state, p, "sacrificed", sacrificed=True)
            return True
    return False


# --- Equipamento: Swiftfoot Boots ------------------------------------------------------------------------
def act_equip_boots(state: GameState) -> bool:
    boots = [p for p in state.battlefield if "boots" in p.card.tags]
    if not boots or not afford(state, 1):
        return False
    b = boots[0]
    cs = creatures(state)
    if not cs:
        return False
    sick = [p for p in cs if p.entered_turn == state.turn and not p.tapped and "defender" not in eff_card(p).tags]
    kod = has_perm(state, "Kodama of the West Tree")
    target = None
    if sick:
        cand = max(sick, key=lambda p: (power(state, p), -p.uid))
        if power(state, cand) >= 3:
            target = cand
    if target is None and kod:
        unmod = [p for p in cs if p.counters == 0 and can_attack(state, p) and not any(v > 0 for v in p.ctr.values())]
        if unmod:
            target = max(unmod, key=lambda p: (power(state, p), -p.uid))
    if target is None or b.attached_to == target.uid:
        return False
    if b.attached_to is not None and find_perm(state, b.attached_to) is not None and not sick:
        return False
    if not spend(state, 1):
        return False
    b.attached_to = target.uid
    state.boots_equips += 1
    return True


# --- Walking Ballista ---------------------------------------------------------------------------------------
def act_ballista_ping(state: GameState) -> bool:
    ball = [p for p in perms_named(state, "Walking Ballista") if p.counters > 0]
    if not ball:
        return False
    tot = sum(p.counters for p in ball)
    for o in sorted(alive_opps(state), key=lambda o: (o.life, o.idx)):
        if o.life <= tot:
            commit_crime(state, "ballista")
            for p in ball:
                while p.counters > 0 and not o.eliminated:
                    p.counters -= 1
                    state.ballista_pings_total += 1
                    lose_life_opp(state, o.idx, 1, "ballista")
            return True
    return False


def act_ballista_pump(state: GameState) -> bool:
    ball = perms_named(state, "Walking Ballista")
    if not ball or not afford(state, 4, (), creature=True):
        return False
    spend(state, 4, (), creature=True)
    state.ballista_pumps += 1
    place_counters(state, ball[0], 1, source="ballista")
    return True


# --- Altar of Dementia ------------------------------------------------------------------------------------------
def altar_sac(state: GameState, victim: Permanent, tgt: Opp):
    pw = power(state, victim)
    state.altar_dementia_sacs += 1
    commit_crime(state, "altar_of_dementia")               # "Target player"
    remove_permanent(state, victim, "sacrificed", sacrificed=True)
    mill_event(state, [(tgt.idx, pw)], source="altar_of_dementia")


def altar_henge_loop(state: GameState) -> bool:
    """Altar of Dementia + The Great Henge + Glen Elendra Archmage (Spellbook): sacrifica a Glen (persist devolve com -1/-1; o +1/+1 da Henge cancela o -1/-1; a Henge compra 1),
    mila `poder` do oponente, e repete. A compra da Henge e' OBRIGATORIA, entao o laco e' limitado pela MINHA biblioteca (paro antes de me decar)."""
    iters = 0
    last_delta = 1
    while not state.game_over and iters < 250:
        glens = [p for p in perms_named(state, "Glen Elendra Archmage") if p.ctr.get("minus1", 0) == 0]
        if not glens or not has_perm(state, "The Great Henge") or not has_perm(state, "Altar of Dementia"):
            break
        tgt = best_opp_library(state)
        if tgt is None:
            break
        if len(state.library) <= 2 * last_delta + 3:
            break
        before = len(state.library)
        iters += 1
        state.altar_loop_iters += 1
        altar_sac(state, glens[0], tgt)
        last_delta = max(1, before - len(state.library))
    if iters:
        state.combo_loops += 1
        if state.combo_win is None and (state.table_cleared_turn is not None):
            state.combo_win = "altar_henge_glen"
    return iters > 0


def act_altar_loop(state: GameState) -> bool:
    if not (has_perm(state, "Altar of Dementia") and has_perm(state, "The Great Henge")):
        return False
    glens = [p for p in perms_named(state, "Glen Elendra Archmage") if p.ctr.get("minus1", 0) == 0]
    if not glens or best_opp_library(state) is None:
        return False
    return altar_henge_loop(state)


def act_altar_finisher(state: GameState) -> bool:
    """Altar sem laco: sacrificar quando UMA criatura (nao o comandante) zera a biblioteca de um oponente; ou o Kozilek em campo quando a minha biblioteca esta curta (o gatilho
    de cemiterio dele me devolve o cemiterio)."""
    if not has_perm(state, "Altar of Dementia"):
        return False
    al = [o for o in alive_opps(state) if o.library]
    sacable = [p for p in creatures(state) if "commander" not in p.card.tags]
    for o in sorted(al, key=lambda o: (len(o.library), o.idx)):
        fit = [p for p in sacable if power(state, p) >= len(o.library)]
        if fit:
            v = min(fit, key=lambda p: (power(state, p), p.uid))
            altar_sac(state, v, o)
            return True
    koz = [p for p in perms_named(state, "Kozilek, Butcher of Truth")]
    if koz and len(state.library) < 20 and al:
        altar_sac(state, koz[0], max(al, key=lambda o: (len(o.library), -o.idx)))
        return True
    return False


# --- Terrenos com habilidade: canais, ciclo, sacrificios ----------------------------------------------------------
def legend_discount(state: GameState) -> int:
    return sum(1 for p in creatures(state) if eff_card(p).legendary)


def other_lands_in_hand(state: GameState, name: str) -> int:
    return sum(1 for h in state.hand if h != name and "land" in CARD_DB[h].types and "mdfc" not in CARD_DB[h].tags)


def act_takenuma(state: GameState) -> bool:
    if "Takenuma, Abandoned Mire" not in state.hand:
        return False
    if n_lands(state) + other_lands_in_hand(state, "Takenuma, Abandoned Mire") < 6:
        return False
    g = max(0, 3 - legend_discount(state))
    if not afford(state, g, (frozenset("B"),)) or not safe_self_mill(state, 3):
        return False
    gy_has = any(("creature" in CARD_DB[c].types or "planeswalker" in CARD_DB[c].types) and not CARD_DB[c].token for c in state.graveyard)
    if not gy_has and len(state.library) < 20:
        pass
    spend(state, g, (frozenset("B"),))
    state.hand.remove("Takenuma, Abandoned Mire")
    state.channel_total += 1
    put_card_into_graveyard(state, "Takenuma, Abandoned Mire", "hand")      # descartar: Gitrog compra, Icetill rejoga
    mill_event(state, [(0, 3)], source="takenuma")
    cands = [c for c in state.graveyard if ("creature" in CARD_DB[c].types or "planeswalker" in CARD_DB[c].types) and not CARD_DB[c].token and "commander" not in CARD_DB[c].tags]
    if cands:
        best = max(cands, key=lambda c: (graveyard_value(state, c), c))
        state.graveyard.remove(best)
        state.hand.append(best)
        state.recursion_events_total += 1
        graveyard_leave(state, [best])
    return True


def act_boseiju(state: GameState) -> bool:
    if "Boseiju, Who Endures" not in state.hand or n_lands(state) + other_lands_in_hand(state, "Boseiju, Who Endures") < 7:
        return False
    g = max(0, 1 - legend_discount(state))
    if not afford(state, g, (frozenset("G"),)) or not target_available(state):
        return False
    spend(state, g, (frozenset("G"),))
    state.hand.remove("Boseiju, Who Endures")
    state.channel_total += 1
    state.interaction_plays += 1
    commit_crime(state, "boseiju")
    put_card_into_graveyard(state, "Boseiju, Who Endures", "hand")
    return True


def act_triome_cycle(state: GameState) -> bool:
    if "Zagoth Triome" not in state.hand:
        return False
    if n_lands(state) + other_lands_in_hand(state, "Zagoth Triome") < 6 and not has_perm(state, "The Gitrog Monster"):
        return False
    if not afford(state, 3):
        return False
    spend(state, 3)
    state.hand.remove("Zagoth Triome")
    state.triome_cycles += 1
    put_card_into_graveyard(state, "Zagoth Triome", "hand")
    draw_cards(state, 1, source="cycling")
    return True


def act_waterlogged_grove(state: GameState) -> bool:
    gv = [p for p in perms_named(state, "Waterlogged Grove") if not p.tapped]
    if not gv:
        return False
    loops = has_perm(state, "Icetill Explorer") or has_perm(state, "The Gitrog Monster") or has_perm(state, "Muldrotha, the Gravetide")
    if not (n_lands(state) >= 9 or (loops and n_lands(state) >= 6)):
        return False
    g = gv[0]
    if not afford(state, 1):
        return False
    g.tapped = True
    if not spend(state, 1):
        g.tapped = False
        return False
    state.battlefield.remove(g)
    state.grove_sacs += 1
    put_card_into_graveyard(state, g.card.name, "battlefield", sacrificed=True)
    draw_cards(state, 1, source="waterlogged_grove")
    return True


def act_strip_mine(state: GameState) -> bool:
    sm = [p for p in perms_named(state, "Strip Mine") if not p.tapped]
    if not sm or not target_available(state):
        return False
    pay = (has_perm(state, "Deepmuck Desperado") or has_perm(state, "Freestrider Lookout") or has_perm(state, "The Gitrog Monster"))
    loops = has_perm(state, "Icetill Explorer") or has_perm(state, "Muldrotha, the Gravetide")
    if n_lands(state) < 6 or not (pay and loops or n_lands(state) >= 9):
        return False
    s0 = sm[0]
    state.battlefield.remove(s0)
    state.strip_mine_uses += 1
    state.interaction_plays += 1
    commit_crime(state, "strip_mine")
    put_card_into_graveyard(state, s0.card.name, "battlefield", sacrificed=True)
    return True


def act_lantern_exile(state: GameState) -> bool:
    """Soul-Guide Lantern, 2a ativada: '{T}, Sacrifice: Exile each opponent's graveyard.' O efeito (tirar recursao do oponente) e' estrutural; so' uso quando os cemiterios deles tem
    material (>= 6 cartas somadas) e o oponente tem algo pra recuperar (`target_available`): conta como interacao proxy. Nao mira (nao e' crime)."""
    ls = [p for p in perms_named(state, "Soul-Guide Lantern") if not p.tapped]
    if not ls or len(state.hand) <= 5:           # com a mao cheia prefiro a compra (act_lantern)
        return False
    if sum(len(o.graveyard) for o in alive_opps(state)) < 6 or not target_available(state):
        return False
    state.battlefield.remove(ls[0])
    state.interaction_plays += 1
    for o in state.opps:
        o.graveyard.clear()
    return True


def act_lantern(state: GameState) -> bool:
    ls = [p for p in perms_named(state, "Soul-Guide Lantern") if not p.tapped]
    if not ls:
        return False
    if len(state.hand) >= 6 or not afford(state, 1):
        return False
    l0 = ls[0]
    l0.tapped = True
    if not spend(state, 1):
        l0.tapped = False
        return False
    state.battlefield.remove(l0)
    state.lantern_draws += 1
    draw_cards(state, 1, source="lantern")
    return True


# --- Riverchurn Monument (2026-10-07) -------------------------------------------------------------------------------------
def _riverchurn_parts(state: GameState, n_opp, n_self) -> list:
    """Alvos de 'any number of target players': todo oponente vivo com biblioteca (n_opp(o) cartas); eu so' com RIVERCHURN_SELF e `safe_self_mill`. UM evento de mill (um gatilho do Mothman)."""
    parts = [(o.idx, n_opp(o)) for o in alive_opps(state) if o.library and n_opp(o) > 0]
    if parts and RIVERCHURN_SELF:
        k = n_self()
        if k > 0 and len(state.library) >= k and safe_self_mill(state, k):
            parts.append((0, k))
    return parts


def act_riverchurn_exhaust(state: GameState, ignore_reserve: bool = False) -> bool:
    """Exhaust -- {2}{U}{U}, {T}: 'Any number of target players each mill cards equal to the number of cards in their graveyard. (Activate each exhaust ability only once.)'
    Uma vez POR OBJETO (ruling 2025-02-07: se sair e voltar e' objeto novo; aqui `Permanent.exhausted`). Qualquer momento em que eu poderia ativar uma habilidade. Politica: gasto quando a soma dos cemiterios dos oponentes
    vivos chega a RIVERCHURN_EXHAUST_MIN ou quando algum oponente morreria (cemiterio >= biblioteca); o numero e' lido na resolucao (antes de milar)."""
    if not RIVERCHURN_ACTIVATE:
        return False
    ms = [p for p in perms_named(state, "Riverchurn Monument") if not p.tapped and not p.exhausted]
    if not ms:
        return False
    al = [o for o in alive_opps(state) if o.library and o.graveyard]
    if not al:
        return False
    lethal = sum(1 for o in al if len(o.graveyard) >= len(o.library))
    if not lethal and sum(len(o.graveyard) for o in al) < RIVERCHURN_EXHAUST_MIN:
        return False
    pips = (frozenset("U"), frozenset("U"))
    if not afford(state, 2, pips, ignore_reserve=ignore_reserve):
        return False
    m = ms[0]
    m.tapped = True
    if not spend(state, 2, pips):
        m.tapped = False
        return False
    m.exhausted = True
    state.riverchurn_exhaust_activations += 1
    state.riverchurn_exhaust_lethal += lethal
    if any(q.ctr.get("quest", 0) >= 3 for q in perms_named(state, "Bloodchief Ascension")):
        state.riverchurn_exhaust_ascension += 1
    if state.riverchurn_exhaust_turn is None:
        state.riverchurn_exhaust_turn = state.turn
    parts = _riverchurn_parts(state, lambda o: len(o.graveyard), lambda: len(state.graveyard))
    state.riverchurn_exhaust_cards_opp += sum(n for pl, n in parts if pl != 0)
    mill_event(state, parts, source="riverchurn_exhaust")
    return True


def act_riverchurn_tap(state: GameState, ignore_reserve: bool = False) -> bool:
    """{1}, {T}: 'Any number of target players each mill two cards.' Artefato: sem doenca de invocacao. Um {T} por desvirar: o Exhaust (acima) tem prioridade quando vale a pena."""
    if not RIVERCHURN_ACTIVATE:
        return False
    ms = [p for p in perms_named(state, "Riverchurn Monument") if not p.tapped]
    if not ms:
        return False
    parts = _riverchurn_parts(state, lambda o: 2, lambda: 2)
    if not parts or not afford(state, 1, ignore_reserve=ignore_reserve):
        return False
    m = ms[0]
    m.tapped = True
    if not spend(state, 1):
        m.tapped = False
        return False
    state.riverchurn_tap_activations += 1
    state.riverchurn_tap_cards_opp += sum(n for pl, n in parts if pl != 0)
    mill_event(state, parts, source="riverchurn_tap")
    return True


def riverchurn_opp_end_step(state: GameState):
    """Fim do ultimo turno de oponente da rodada (instante, antes do meu untap): sobrou mana (a que eu segurava pras contramagicas ja' nao tem pra que servir)? Paga o Exhaust ou a 1a ativada, se o
    Monument ainda esta desvirado. So' com RIVERCHURN_OPP_END_STEP (linha real que o padrao do simulador nao joga)."""
    if not RIVERCHURN_OPP_END_STEP or state.game_over or not has_perm(state, "Riverchurn Monument"):
        return
    act_riverchurn_exhaust(state, ignore_reserve=True) or act_riverchurn_tap(state, ignore_reserve=True)


# --- Shifting Woodland --------------------------------------------------------------------------------------------
def card_types_in_graveyard(state: GameState) -> int:
    ts = set()
    for c in state.graveyard:
        for t in CARD_DB[c].types:
            if t in ("artifact", "creature", "enchantment", "instant", "land", "planeswalker", "sorcery", "battle"):
                ts.add(t)
    return len(ts)


def act_woodland(state: GameState) -> bool:
    """Delirium {2}{G}{G}: o terreno vira copia de um permanente do cemiterio ate o fim do turno (ruling: NAO dispara 'enters'). So' vale quando a copia faz algo agora:
    Muldrotha (jogar do cemiterio), Icetill Explorer (terreno extra e do cemiterio), Kami (+1 em todo contador), Winding Constrictor, The Great Henge (GG)."""
    ws = [p for p in perms_named(state, "Shifting Woodland") if p.copy_of is None and not p.tapped]
    if not ws or card_types_in_graveyard(state) < 4:
        return False
    w = ws[0]
    w.tapped = True                    # reservado: nao pode pagar o proprio custo
    ok_pay = afford(state, 2, (frozenset("G"), frozenset("G")))
    w.tapped = False
    if not ok_pay:
        return False
    options = []
    gy = state.graveyard
    if "Muldrotha, the Gravetide" in gy and not has_perm(state, "Muldrotha, the Gravetide") and graveyard_cast_options_if_muldrotha(state):
        options.append(("Muldrotha, the Gravetide", 90))
    if "Icetill Explorer" in gy and not has_perm(state, "Icetill Explorer") and any("land" in CARD_DB[c].types for c in gy):
        options.append(("Icetill Explorer", 80))
    if "Kami of Whispered Hopes" in gy and not has_perm(state, "Kami of Whispered Hopes") and creatures(state):
        options.append(("Kami of Whispered Hopes", 40))
    if "Winding Constrictor" in gy and not has_perm(state, "Winding Constrictor") and creatures(state):
        options.append(("Winding Constrictor", 39))
    if "The Great Henge" in gy and not has_perm(state, "The Great Henge"):
        options.append(("The Great Henge", 70))
    if not options:
        return False
    pick = max(options, key=lambda t: (t[1], t[0]))[0]
    w.tapped = True
    spend(state, 2, (frozenset("G"), frozenset("G")))
    w.tapped = False
    w.copy_of = pick
    state.shifting_woodland_copies += 1
    state.woodland_copy_as[pick] = state.woodland_copy_as.get(pick, 0) + 1
    return True


def graveyard_cast_options_if_muldrotha(state: GameState) -> bool:
    for name in state.graveyard:
        c = CARD_DB[name]
        if c.token or "land" in c.types or "instant" in c.types or "sorcery" in c.types or "commander" in c.tags:
            continue
        if any(t in c.types for t in ("creature", "artifact", "enchantment", "planeswalker")):
            return True
    return False


def act_karns_bastion(state: GameState) -> bool:
    """Karn's Bastion: '{4}, {T}: Proliferate.' (o proprio {T} e' custo: o terreno nao paga o {4})."""
    for b in perms_named(state, "Karn's Bastion"):
        if b.tapped or proliferate_value(state) < 5:
            continue
        b.tapped = True
        if afford(state, 4):
            spend(state, 4)
            proliferate(state, "karns_bastion")
            return True
        b.tapped = False
    return False


# --- Fim das acoes: prioridade --------------------------------------------------------------------------------
ACTIONS = (act_saga_construct, act_ashiok, act_jace, act_master, act_fractured_cycle, act_earth_crystal, act_cauldron, act_altar_loop, act_cauldron_minamo, act_zellix, act_zellix_minamo, act_ballista_ping, act_cankerbloom,
           act_takenuma, act_boseiju, act_adapt, act_equip_boots, act_woodland, act_konrad, act_triome_cycle, act_waterlogged_grove, act_strip_mine,
           act_altar_finisher, act_lantern, act_ballista_pump)


def use_spare_mana(state: GameState, phase: str = "main1"):
    for _ in range(60):
        if state.game_over:
            return
        acted = False
        for fn in ACTIONS:
            if fn(state):
                acted = True
                break
        if not acted:
            return


# --- Kozilek como seguro: devolver o cemiterio pra biblioteca ---------------------------------------------------------
def act_bramble_refill(state: GameState) -> bool:
    """Bramble Familiar: '{1}{G}, {T}, Discard a card: Return this creature to its owner's hand.' Descartar o Kozilek poe ele no cemiterio -> embaralha o cemiterio na biblioteca."""
    if len(state.library) >= 14 or jace_line(state):
        return False
    koz = [c for c in state.hand if "kozilek" in CARD_DB[c].tags]
    if not koz:
        return False
    for p in perms_named(state, "Bramble Familiar // Fetch Quest"):
        if can_tap_creature(state, p) and afford(state, 1, (frozenset("G"),), creature=True, ignore_reserve=True):
            p.tapped = True
            if not spend(state, 1, (frozenset("G"),), creature=True):
                p.tapped = False
                continue
            state.hand.remove(koz[0])
            state.battlefield.remove(p)
            state.hand.append(p.card.name)
            put_card_into_graveyard(state, koz[0], "hand")
            return True
    return False


ACTIONS = (act_bramble_refill,) + ACTIONS


# =========================================================
# COMBATE
# =========================================================
NON_ATTACKERS = frozenset({"kami", "gyre_sage", "bramble", "zellix"})      # criaturas cuja {T} vale mais que o ataque (mana / habilidade)


def crew_shredder(state: GameState):
    """Hedge Shredder, Crew 1: viro o Veiculo em criatura (encarar o ataque exige que ele nao tenha entrado neste turno)."""
    for sh in perms_named(state, "Hedge Shredder"):
        if sh.crewed or not (sh.entered_turn < state.turn or has_haste(state, sh)):
            continue
        cands = [p for p in creatures(state) if not p.tapped and p is not sh and power(state, p) >= 1]
        if not cands:
            continue
        cands.sort(key=lambda p: (0 if not can_attack(state, p) else 1, power(state, p), p.uid))
        crew = cands[0]
        if can_attack(state, crew) and power(state, crew) >= power(state, sh):
            continue
        crew.tapped = True
        sh.crewed = True


def beginning_of_combat(state: GameState):
    crew_shredder(state)
    # Ouroboroid: "At the beginning of combat on your turn, put X +1/+1 counters on each creature you control, where X is this creature's power."
    for ou in perms_named(state, "Ouroboroid"):
        x = power(state, ou)
        if x <= 0:
            continue
        for p in list(creatures(state)):
            if p in state.battlefield and not state.game_over:
                place_counters(state, p, x, source="ouroboroid")


def pick_attackers(state: GameState) -> list:
    out = []
    for p in creatures(state):
        if not can_attack(state, p):
            continue
        t = eff_card(p).tags
        if t & NON_ATTACKERS:
            continue
        if power(state, p) <= 0:
            continue
        out.append(p)
    if SELF_MILL_GUARD_ENABLED and has_perm(state, "Mesmeric Orb"):
        keep = max(1, library_budget(state))
        if len(out) > keep:
            out.sort(key=lambda p: (0 if "commander" in eff_card(p).tags else 1, -power(state, p), p.uid))
            out = out[:keep]
    return out


def assign_targets(state: GameState, attackers: list) -> dict:
    """Cada atacante -> oponente. Gulosamente: do maior poder pro menor, no oponente de menor vida restante que ainda nao esta coberto; Zumbis (Undead Alchemist) vao pro de maior biblioteca."""
    al = alive_opps(state)
    if not al:
        return {}
    rem = {o.idx: o.life for o in al}
    out = {}
    zomb = has_perm(state, "Undead Alchemist")
    ml = best_opp_library(state)
    for p in sorted(attackers, key=lambda q: (-power(state, q), q.uid)):
        if zomb and "Zombie" in perm_subtypes(p) and ml is not None:
            out[p.uid] = ml.idx
            continue
        alive_rem = [o for o in al if rem[o.idx] > 0]
        tgt = min(alive_rem, key=lambda o: (rem[o.idx], o.idx)) if alive_rem else max(al, key=lambda o: (o.life, -o.idx))
        out[p.uid] = tgt.idx
        rem[tgt.idx] -= power(state, p)
    return out


def combat_step(state: GameState):
    if state.game_over:
        return
    beginning_of_combat(state)
    if state.game_over:
        return
    al = alive_opps(state)
    if not al:
        return
    attackers = pick_attackers(state)
    if not attackers:
        return
    state.attackers_this_turn = list(attackers)
    for p in attackers:
        if "vigilance" not in eff_card(p).tags:
            p.tapped = True
    # --- gatilhos de ataque
    for p in attackers:
        t = eff_card(p).tags
        if "commander" in t:
            state.mothman_attacks_total += 1
            give_rad(state, 0, 1)
            for o in alive_opps(state):
                give_rad(state, o.idx, 1)
    for p in attackers:
        if p not in state.battlefield:
            continue
        t = eff_card(p).tags
        if "scorchbeast" in t:
            # "Whenever this creature attacks, each player gets two rad counters." (eu tambem: Constrictor soma +1 nos MEUS)
            state.scorch_attacks += 1
            give_rad(state, 0, 2)
            state.scorch_rad_self += 2
            for o in alive_opps(state):
                give_rad(state, o.idx, 2)
        if "horrigan" in t:
            # "Whenever Agent Frank Horrigan enters or attacks, proliferate twice." + "has indestructible as long as it attacked this turn" (vale desde que e' declarado atacante, ruling)
            p.attacked_turn_id = state.turn_id
            state.horrigan_attacks += 1
            state.horrigan_attack_prolifs += 1
            if HORRIGAN_PROLIF_TIMES > 0:
                proliferate(state, "horrigan_attack", times=HORRIGAN_PROLIF_TIMES)
            if state.game_over or p not in state.battlefield:
                continue
            state.horrigan_attack_damage += power(state, p)
        if "mentor" in t:
            lesser = [q for q in attackers if q is not p and q in state.battlefield and power(state, q) < power(state, p)]
            if lesser:
                best = max(lesser, key=lambda q: (counter_target_value(state, q), -q.uid))
                place_counters(state, best, 1, source="mentor")
        if "six" in t and safe_self_mill(state, 3):
            res = mill_event(state, [(0, 3)], source="six")
            lands = [c for c in res.get(0, []) if is_land_card_name(c) and c in state.graveyard]
            if lands:
                pick = max(lands, key=lambda c: (graveyard_value(state, c), c))
                state.graveyard.remove(pick)
                state.hand.append(pick)
        if eff_name(p) == "Hedge Shredder" and safe_self_mill(state, 2):
            mill_event(state, [(0, 2)], source="hedge_shredder_attack")
        if state.game_over:
            return
    attackers = [p for p in attackers if p in state.battlefield]
    if state.game_over or not alive_opps(state):
        return                                  # os gatilhos de ataque (Konrad, mill) podem ter eliminado a mesa antes do dano
    for h in perms_named(state, "Hollowmurk Siege"):
        if h.ctr.get("abzan") and attackers:
            best = max(attackers, key=lambda q: (counter_target_value(state, q), -q.uid))
            place_counters(state, best, 1, source="hollowmurk_abzan")
    # --- dano de combate (simultaneo)
    if state.game_over or not alive_opps(state):
        return                                  # Hollowmurk Abzan / compras podem ter eliminado a mesa (ex.: Psychic Corrosion + Ascension + Mindcrank)
    targets = assign_targets(state, attackers)
    dmg = collections.defaultdict(int)
    zombie_mill = collections.defaultdict(int)
    dealers = []
    for p in attackers:
        pw = power(state, p)
        if pw <= 0:
            continue
        idx = targets.get(p.uid)
        if idx is None:
            continue
        if has_perm(state, "Undead Alchemist") and "Zombie" in perm_subtypes(p):
            zombie_mill[idx] += pw                 # 'instead that player mills that many cards'
            dealers.append((p, idx, pw, True))
            continue
        dmg[idx] += pw
        dealers.append((p, idx, pw, False))
    if zombie_mill:
        mill_event(state, [(i, n) for i, n in sorted(zombie_mill.items())], source="undead_alchemist")
    for idx, n in sorted(dmg.items()):
        if state.game_over:
            return
        o = state.opps[idx - 1]
        if o.eliminated:
            continue
        state.proxy_damage_total += n
        lose_life_opp(state, idx, n, "combat", combat=True)
    for p, idx, pw, replaced in dealers:
        if state.game_over:
            return
        t = eff_card(p).tags
        o = state.opps[idx - 1]
        if "commander" in t and not replaced:
            state.commander_dmg_total += pw
            o.cmd_damage += pw
            if o.cmd_damage >= 21 and not o.eliminated:
                eliminate_opp(state, o, "commander")
        if "selkie" in t and not replaced:
            draw_cards(state, pw, source="selkie")
        if "frogantua" in t and not replaced:
            k = pw if (len(state.library) >= pw and safe_self_mill(state, pw)) else 0      # ruling: se a biblioteca tem menos que o dano, nao posso escolher milar (tudo ou nada)
            if k > 0:
                res = mill_event(state, [(0, k)], source="frogantua")
                for lc in [c for c in res.get(0, []) if is_land_card_name(c)]:
                    if lc in state.graveyard:                       # duplicatas / ja' movido por outro gatilho (Hedge Shredder)
                        state.graveyard.remove(lc)
                        put_land_onto_battlefield(state, lc, tapped=True, source="frogantua")
        if p in state.battlefield and is_modified(state, p) and has_perm(state, "Kodama of the West Tree") and not replaced:
            tgt = basic_land_search(state)
            if tgt is not None:
                take_from_library(state, tgt)
                state.rng.shuffle(state.library)
                state.kodama_lands_total += 1
                put_land_onto_battlefield(state, tgt, tapped=True, source="kodama")
    for o in list(state.opps):
        if not o.eliminated:
            check_opp_elim(state, o)


# =========================================================
# FASE PRINCIPAL E TURNO
# =========================================================

def _fingerprint(state: GameState):
    return (len(state.hand), len(state.battlefield), len(state.graveyard), len(state.library), state.spells_cast_this_turn, state.lands_played_this_turn,
            sum(p.counters for p in state.battlefield), sum(1 for p in state.battlefield if p.tapped), state.mana_spent_total)


def main_phase(state: GameState, phase: str):
    if state.game_over:
        return
    cast_landfall_payoffs_first(state, phase)
    play_land_phase(state)
    for _ in range(12):
        if state.game_over:
            return
        fp = _fingerprint(state)
        if RIVERCHURN_TAP_FIRST and not state.commander_in_cz:
            act_riverchurn_exhaust(state) or act_riverchurn_tap(state)
        cast_loop(state, phase)
        play_land_phase(state)
        use_spare_mana(state, phase)
        if _fingerprint(state) == fp:
            break


def record_turn_metrics(state: GameState):
    t = state.turn
    mm = [p for p in state.battlefield if "commander" in p.card.tags]
    state.mothman_power_turn[t] = power(state, mm[0]) if mm else 0
    state.creature_count_by_turn[t] = len(creatures(state))
    state.counters_on_board_by_turn[t] = sum(p.counters for p in state.battlefield)
    state.lands_in_play_by_turn[t] = n_lands(state)
    state.cards_in_hand_by_turn[t] = len(state.hand)
    state.library_by_turn[t] = len(state.library)
    state.max_creature_power = max([state.max_creature_power] + [power(state, p) for p in creatures(state)])
    state.max_creatures_in_play = max(state.max_creatures_in_play, len(creatures(state)))


def play_turn(state: GameState):
    state.turn += 1
    begin_any_turn(state)                       # ANTES do untap: os mills do Mesmeric Orb ja' sao deste turno
    if state.turn > 1:
        untap_my_permanents(state)
    if state.game_over:
        return
    upkeep_step(state)
    if state.game_over:
        return
    draw_step(state)
    if state.game_over:
        return
    mana_probe = available_mana(state)
    state.mana_by_turn[state.turn] = mana_probe
    saga_lore_step(state)
    rad_trigger_self(state)                           # inicio da fase principal 1 (CR 728.1)
    if state.game_over:
        return
    main_phase(state, "main1")
    if state.game_over:
        return
    combat_step(state)
    if state.game_over:
        return
    main_phase(state, "main2")
    if state.game_over:
        return
    end_step(state)
    record_turn_metrics(state)


# =========================================================
# MULLIGAN (London; 1o gratis — mesma convencao dos outros simuladores; o jogador ESCOLHE o fundo, CR 103.5)
# =========================================================

def _hand_lands(hand):
    return [c for c in hand if "land" in CARD_DB[c].types and "mdfc" not in CARD_DB[c].tags]


def should_keep(hand: list, mulls: int) -> bool:
    L = len(_hand_lands(hand))
    mdfc = sum(1 for c in hand if "mdfc" in CARD_DB[c].tags)
    cheap = sum(1 for c in hand if "land" not in CARD_DB[c].types and CARD_DB[c].mv <= 3)
    if mulls >= 3:
        return L + mdfc >= 1
    if mulls == 2:
        return 2 <= L + mdfc and L <= 5
    if L + mdfc < 2 or L > 5:
        return False
    if L + mdfc == 2 and cheap < 2:
        return False
    if L == 5 and cheap < 2:
        return False
    return True


def bottom_priority(c: str, hand: list) -> float:
    """Maior = vai pro fundo primeiro."""
    cc = CARD_DB[c]
    lands = len(_hand_lands(hand))
    if "land" in cc.types and "mdfc" not in cc.tags:
        return 80.0 if lands >= 5 else (30.0 if lands == 4 else -5.0)
    if "kozilek" in cc.tags:
        return 100.0
    if cc.mv >= 7:
        return 70.0
    return 50.0 - float(CAST_PRIORITY.get(c, 25)) * 0.4 + 0.5 * cc.mv


def mulligan(state: GameState):
    mulls = 0
    while True:
        hand = state.library[:7]
        rest = state.library[7:]
        if should_keep(hand, mulls) or mulls >= 4:
            penalty = max(0, mulls - 1)
            keep = list(hand)
            bottom = []
            for _ in range(penalty):
                worst = max(keep, key=lambda c: (bottom_priority(c, keep), c))
                keep.remove(worst)
                bottom.append(worst)
            state.hand = keep
            state.library = rest + bottom
            state.mulligans = mulls
            return
        mulls += 1
        state.rng.shuffle(state.library)


# =========================================================
# LISTA DO DECK (fonte: lista.md; nomes REAIS do Scryfall, Regra #2) E BIBLIOTECA
# =========================================================
DECKLIST_TEXT = """
1 Agadeem's Awakening // Agadeem, the Undercrypt
1 Agatha's Soul Cauldron
1 Altar of Dementia
1 Altar of the Brood
1 An Offer You Can't Refuse
1 Angel of Suffering
1 Arcane Denial
1 Ashiok, Dream Render
1 Basking Broodscale
1 Bloodchief Ascension
1 Bojuka Bog
1 Boseiju, Who Endures
1 Bramble Familiar // Fetch Quest
1 Breeding Pool
1 Cankerbloom
1 Cold-Eyed Selkie
1 Command Tower
1 Danny Pink
1 Deepmuck Desperado
1 Didn't Say Please
1 Evolution Witness
1 Fabled Passage
1 Fathom Mage
1 Fierce Guardianship
5 Forest
1 Freestrider Lookout
1 Generous Patron
1 Glen Elendra Archmage
1 Gyre Sage
1 Hardened Scales
1 Hedge Shredder
1 Herd Baloth
1 Heroic Intervention
1 Hollowmurk Siege
1 Icetill Explorer
4 Island
1 Kami of Whispered Hopes
1 Kodama of the West Tree
1 Kozilek, Butcher of Truth
1 Memory Erosion
1 Mesmeric Orb
1 Minamo, School at Water's Edge
1 Mindcrank
1 Mirelurk Queen
1 Misty Rainforest
1 Morphic Pool
1 Muldrotha, the Gravetide
1 Nature's Lore
1 Negate
1 Nuclear Fallout
1 Ouroboroid
1 Overgrown Tomb
1 Palantír of Orthanc
1 Plaza of Heroes
1 Polluted Delta
1 Pollywog Prodigy
1 Psychic Corrosion
1 Rampant Frogantua
1 Rejuvenating Springs
1 Repulsive Mutation
1 Ruin Crab
1 Shifting Woodland
1 Six
1 Smuggler's Surprise
1 Sol Ring
1 Soul-Guide Lantern
1 Strip Mine
3 Swamp
1 Swarmyard
1 Swiftfoot Boots
1 Syr Konrad, the Grim
1 Takenuma, Abandoned Mire
1 Tear Asunder
1 The Gitrog Monster
1 The Great Henge
1 Three Visits
1 Toxic Deluge
1 Undead Alchemist
1 Undergrowth Stadium
1 Urza's Saga
1 V.A.T.S.
1 Verdant Catacombs
1 Walking Ballista
1 Waterlogged Grove
1 Watery Grave
1 Wave Goodbye
1 Winding Constrictor
1 Yavimaya Hollow
1 Zagoth Triome
1 Zellix, Sanity Flayer
"""


def parse_decklist(text: str) -> list:
    out = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("//") or line.startswith("#"):
            continue
        n, name = line.split(" ", 1)
        out.extend([name.strip()] * int(n))
    return out


BASE_LIBRARY = parse_decklist(DECKLIST_TEXT)       # 99 cartas (o comandante fica na zona de comando)
SWAPS = ()                                          # variante de A/B: tupla de (carta_que_sai, carta_que_entra)
SWAP_IN_PLACE = False                               # True: a carta que entra ocupa o LUGAR da que sai (mesma permutacao da semente => partida em que nenhuma das duas aparece e' IDENTICA: pareamento muito mais forte). Padrao False = remove+append (todos os numeros ja' arquivados)


def current_library() -> list:
    lib = list(BASE_LIBRARY)
    for out_c, in_c in SWAPS:
        if SWAP_IN_PLACE:
            lib[lib.index(out_c)] = in_c
        else:
            lib.remove(out_c)
            lib.append(in_c)
    return lib


# =========================================================
# PARTIDA
# =========================================================

def new_state(seed: int) -> GameState:
    rnd = random.Random(seed)
    st = GameState(rng=rnd)
    st.proxy_rng = random.Random(seed * 1_000_033 + 17)
    st.library = current_library()
    rnd.shuffle(st.library)
    st.opps = [make_opp(seed, i) for i in range(1, NUM_OPPONENTS + 1)]
    st.opp_rngs = [None] + [random.Random(seed * 1_000_037 + i * 104729 + 7) for i in range(1, NUM_OPPONENTS + 1)]
    st.life = 40
    st.life_min = 40
    st.library_min = len(st.library)
    mulligan(st)
    return st


def finalize(state: GameState):
    state.library_at_end = len(state.library)
    state.life_min = min(state.life_min, state.life)
    t = state.table_cleared_turn
    for n in (6, 7, 8, 9, 10):
        setattr(state, f"cleared_T{n}", 1 if (t is not None and t <= n) else 0)
    f = state.first_opp_elim_turn
    state.first_elim_T6 = 1 if (f is not None and f <= 6) else 0
    state.first_elim_T8 = 1 if (f is not None and f <= 8) else 0
    state.self_lost = 1 if (state.decked or state.died_life) else 0
    state.jace_win_T8 = 1 if (state.jace_win_turn is not None and state.jace_win_turn <= 8) else 0
    state.jace_win_T10 = 1 if (state.jace_win_turn is not None and state.jace_win_turn <= 10) else 0


def simulate_one(seed: int, turns: int = 12) -> GameState:
    state = new_state(seed)
    for _ in range(turns):
        play_turn(state)
        if state.game_over:
            break
        for o in list(state.opps):
            if o.eliminated:
                continue
            opponent_turn(state, o)
            if state.game_over:
                break
        if state.game_over:
            break
        jace_removal_roll(state)
        riverchurn_opp_end_step(state)
    finalize(state)
    return state


# =========================================================
# MAGIAS QUE O cast_loop NAO ESCOLHE SOZINHO (modos, X, kicker, proxies de interacao)
# =========================================================

def cast_custom(state: GameState, name: str, generic: int, pips: tuple, x: int = 0) -> bool:
    c = CARD_DB[name]
    if not pay_mana(state, generic, pips, c):
        return False
    state.mana_spent_total += generic + len(pips)
    if name in state.hand:
        state.hand.remove(name)
    state.spells_cast_this_turn += 1
    on_my_spell_cast(state, name)
    state.casts_by_card[name] = state.casts_by_card.get(name, 0) + 1
    resolve_spell(state, name, x=x)
    return True


AGADEEM = "Agadeem's Awakening // Agadeem, the Undercrypt"


def act_agadeem(state: GameState) -> bool:
    """Agadeem's Awakening, lado FEITICO: X BBB — devolve do cemiterio, pro campo, criaturas de MVs diferentes <= X. So' quando devolve valor e nao me falta terreno."""
    if AGADEEM not in state.hand:
        return False
    if n_lands(state) + other_lands_in_hand(state, AGADEEM) < 6:
        return False
    c = CARD_DB[AGADEEM]
    g, pips = effective_cost(state, AGADEEM, 0)
    mx = max_x(state, g, pips, 1, c)
    x, chosen = agadeem_x(state, mx)
    if not chosen:
        return False
    if len(chosen) < 2 and CAST_PRIORITY.get(chosen[0], 0) < 60:
        return False
    return cast_card(state, AGADEEM, x=x, zone="hand")


def act_smugglers(state: GameState) -> bool:
    """Smuggler's Surprise (Spree): +{2} mill 4 e ate 2 criatura/terreno pra mao; +{4}{G} ate 2 criaturas da mao pro campo; +{1} hexproof (so' no modo resiliencia)."""
    name = "Smuggler's Surprise"
    if name not in state.hand:
        return False
    c = CARD_DB[name]
    G = frozenset("G")
    big = [h for h in state.hand if "creature" in CARD_DB[h].types and "commander" not in CARD_DB[h].tags and "mdfc" not in CARD_DB[h].tags and CARD_DB[h].mv >= 4]
    want_a = safe_self_mill(state, 4)
    options = []
    if big and want_a:
        options.append((("A", "B"), 1 + 2 + 4, (G, G)))
    if big:
        options.append((("B",), 1 + 4, (G, G)))
    if want_a and len(state.hand) <= 5:
        options.append((("A",), 1 + 2, (G,)))
    for modes, g, pips in options:
        # custo total = pips + generico (o {1}, {2}, {4} somam no generico)
        generic = g - len(pips)
        if afford(state, generic, pips):
            state.pending_modes = modes
            return cast_custom(state, name, generic, pips)
    return False


def act_repulsive(state: GameState) -> bool:
    name = "Repulsive Mutation"
    if name not in state.hand or not creatures(state):
        return False
    c = CARD_DB[name]
    g, pips = effective_cost(state, name, 0)
    mx = max_x(state, g, pips, 1, c) - reserve_needed(state)
    if mx < 2:
        return False
    return cast_card(state, name, x=mx, zone="hand")


def act_fallout(state: GameState) -> bool:
    """Nuclear Fallout: X rad counters pra cada jogador (os oponentes milam e perdem vida no main deles) e -2X/-2X pra todas as criaturas. X que nao me custa corpo relevante."""
    name = "Nuclear Fallout"
    if name not in state.hand or not alive_opps(state):
        return False
    c = CARD_DB[name]
    g, pips = effective_cost(state, name, 0)
    mx = max_x(state, g, pips, 1, c) - reserve_needed(state)
    x = fallout_x(state, mx)
    if x < 1:
        return False
    if SELF_MILL_GUARD_ENABLED and library_budget(state) < 2 * x + count_named(state, "Winding Constrictor"):
        return False
    return cast_card(state, name, x=x, zone="hand")


def act_removal_proxy(state: GameState) -> bool:
    """Tear Asunder / V.A.T.S. (+ candidatas Atomize / Casualties of War / Assassin's Trophy): precisam de alvo no tabuleiro do oponente (nao simulado) -> metrica proxy `interaction_plays` + crime, so' quando `target_available`."""
    if state.crime_this_turn.get("removal_proxy"):
        return False
    for name in ("Casualties of War", "Atomize", "Assassin's Trophy", "Tear Asunder", "V.A.T.S."):
        if name not in state.hand:
            continue
        g, pips = effective_cost(state, name, 0)
        if name == "Tear Asunder":
            kg, kp = g + 1, pips + (frozenset("B"),)           # kicker {1}{B}: exila qualquer permanente nao-terreno
            gen = kg - len(kp) + 0
            if afford(state, g + 1, pips + (frozenset("B"),)) and target_available(state):
                state.crime_this_turn["removal_proxy"] = True
                return cast_custom(state, name, g + 1, pips + (frozenset("B"),))
        if afford(state, g, pips) and target_available(state):
            state.crime_this_turn["removal_proxy"] = True
            return cast_custom(state, name, g, pips)
    return False


def act_wipe_proxy(state: GameState) -> bool:
    """Toxic Deluge / Wave Goodbye: o efeito no tabuleiro do OPONENTE e' estrutural (nao simulado); conta como interacao quando `target_available`, escolhendo X / o momento de modo
    que o meu tabuleiro (criaturas com contador) nao sofra."""
    if state.crime_this_turn.get("wipe_proxy"):
        return False
    mine = creatures(state)
    # Toxic Deluge: X = menor resistencia entre minhas criaturas COM contador - 1 (as sem contador e fichas fracas morrem; no maximo 2 corpos nao-ficha)
    if "Toxic Deluge" in state.hand:
        g, pips = effective_cost(state, "Toxic Deluge", 0)
        if afford(state, g, pips):
            withc = [toughness(state, p) for p in mine if p.counters > 0]
            x = min(withc) - 1 if withc else 0
            x = max(0, min(x, 6, state.life - 15))
            lost = [p for p in mine if toughness(state, p) <= x and not p.is_token]
            if x >= 1 and len(lost) <= 1 and target_available(state):
                state.crime_this_turn["wipe_proxy"] = True
                lose_life_self(state, x, "toxic_deluge")
                return cast_custom(state, "Toxic Deluge", g, pips, x=x)
    if "Wave Goodbye" in state.hand:
        g, pips = effective_cost(state, "Wave Goodbye", 0)
        nocnt = [p for p in mine if p.counters == 0 and not p.is_token and "commander" not in p.card.tags]
        if afford(state, g, pips) and len(nocnt) <= 1 and target_available(state):
            state.crime_this_turn["wipe_proxy"] = True
            return cast_custom(state, "Wave Goodbye", g, pips)
    return False


ACTIONS = ACTIONS[:-1] + (act_karns_bastion, act_agadeem, act_smugglers, act_fallout, act_repulsive, act_removal_proxy, act_wipe_proxy, act_minamo_henge, act_lantern_exile) + ACTIONS[-1:]
_i_lantern = ACTIONS.index(act_lantern)
ACTIONS = ACTIONS[:_i_lantern] + (act_riverchurn_exhaust, act_riverchurn_tap) + ACTIONS[_i_lantern:]      # antes da compra do Lantern (que e' uso unico) e do ping do Ballista


# =========================================================
# MODO DE RESILIENCIA (interacao de oponente) — mesmo design dos outros decks do repositorio
# (7 categorias: remocao pontual, ataque, discard, wipe [criatura/artefato/encantamento], graveyard wipe [1x], graveyard snipe, counterspell no comandante;
# gate de atencao por oponente; supressao de ataque pos-wipe) + as DEFESAS reais deste deck: contramagicas/Glen Elendra, Heroic Intervention,
# Smuggler's Surprise (modo +{1}), Swiftfoot Boots (hexproof), regeneracao (Swarmyard, Yavimaya Hollow), Plaza of Heroes, Angel of Suffering (previne e mila).
# =========================================================
INTERACTION_SETUP_TURNS = 2
OPPONENT_ATTENTION_CHANCE = 1.0 / 3
POST_WIPE_ATTACK_HASTE_FACTOR = 0.15
WIPE_TYPE_WEIGHTS = {"creature": 0.4, "artifact": 0.2, "enchantment": 0.15}
TOTAL_WIPE_CHANCE_FACTOR = sum(WIPE_TYPE_WEIGHTS.values())
GRAVEYARD_WIPE_CHANCE_FACTOR = 0.4
GRAVEYARD_SNIPE_CHANCE_FACTOR = 0.5
COUNTERSPELL_CHANCE_FACTOR = 0.5
INTERACTION_ENGINE_PRIORITY = ["Fathom Mage", "Danny Pink", "Winding Constrictor", "Hardened Scales", "Ouroboroid", "Mirelurk Queen", "Kami of Whispered Hopes", "Muldrotha, the Gravetide", "The Master, Transcendent", "Agent Frank Horrigan", "Screeching Scorchbeast", "Branching Evolution", "The Earth Crystal", "Loading Zone", "Inexorable Tide",
                               "The Gitrog Monster", "Icetill Explorer", "Syr Konrad, the Grim", "Zellix, Sanity Flayer", "Hollowmurk Siege", "Mindcrank", "Mesmeric Orb",
                               "Psychic Corrosion", "Memory Erosion", "The Great Henge", "Palantír of Orthanc", "Agatha's Soul Cauldron", "Altar of Dementia",
                               "Bloodchief Ascension", "Ruin Crab", "Altar of the Brood", "Deepmuck Desperado"]
OPPONENT_ATTACKER_PROFILES = [("Knight Token", 2), ("Saproling Token", 1), ("Vampire Token", 1), ("Zombie Token", 2), ("Soldier Token", 1), ("Goblin Token", 1), ("Elemental Token", 3)]


def interaction_chance(state: GameState) -> float:
    board_impact = sum(1 for p in state.battlefield if "land" not in p.card.types)
    return min(0.10 + 0.03 * board_impact, 0.75)


def _prot(state: GameState, kind: str):
    state.protection_used_total += 1
    state.protections_by_kind[kind] = state.protections_by_kind.get(kind, 0) + 1


def regenerate_sources(state: GameState) -> list:
    """Swarmyard ({T}: regenerar Inseto/Rato/Aranha/Esquilo — Mothman e Icetill sao Insetos) e Yavimaya Hollow ({G},{T}: regenerar qualquer criatura)."""
    out = []
    for p in perms_named(state, "Swarmyard"):
        if not p.tapped:
            out.append(("swarmyard", p))
    for p in perms_named(state, "Yavimaya Hollow"):
        if not p.tapped and afford(state, 0, (frozenset("G"),), ignore_reserve=True):
            out.append(("hollow", p))
    return out


def is_indestructible(state: GameState, p: Permanent) -> bool:
    """Horrigan: indestrutivel enquanto atacou NESTE turno (turn_id); nos turnos dos oponentes nao vale (ele atacou no meu)."""
    return "horrigan" in eff_card(p).tags and p.attacked_turn_id == state.turn_id


def try_protect_from_destroy(state: GameState, victims: list, spell_mv: int, noncreature: bool = True) -> set:
    indestr = {p.uid for p in victims if is_indestructible(state, p)}
    if not indestr:
        return _try_protect_from_destroy(state, victims, spell_mv, noncreature)
    rest = [p for p in victims if p.uid not in indestr]
    if not rest:
        return indestr
    return _try_protect_from_destroy(state, rest, spell_mv, noncreature) | indestr


def _try_protect_from_destroy(state: GameState, victims: list, spell_mv: int, noncreature: bool = True) -> set:
    """Devolve o conjunto de uids que SOBREVIVEM a um 'destroy' do oponente: 1) anular a magia; 2) Heroic Intervention; 3) Smuggler's (+{1}): so' poder >= 4;
    4) Plaza of Heroes: 1 lendaria; 5) regeneracao (Swarmyard so' Inseto; Hollow qualquer)."""
    saved = set()
    if respond_to_opp_spell(state, alive_opps(state)[0] if alive_opps(state) else state.opps[0], noncreature=noncreature, mv=max(spell_mv, COUNTER_MIN_MV)):
        _prot(state, "counter")
        return {p.uid for p in victims}
    if "Heroic Intervention" in state.hand:
        g, pips = effective_cost(state, "Heroic Intervention")
        if can_pay(state, g, pips, CARD_DB["Heroic Intervention"]):
            pay_mana(state, g, pips, CARD_DB["Heroic Intervention"])
            state.hand.remove("Heroic Intervention")
            put_card_into_graveyard(state, "Heroic Intervention", "stack")
            _prot(state, "heroic_intervention")
            return {p.uid for p in victims}
    if "Smuggler's Surprise" in state.hand and any(is_creature(p) and power(state, p) >= 4 for p in victims):
        G = frozenset("G")
        if can_pay(state, 1, (G,), CARD_DB["Smuggler's Surprise"]):
            pay_mana(state, 1, (G,), CARD_DB["Smuggler's Surprise"])
            state.hand.remove("Smuggler's Surprise")
            put_card_into_graveyard(state, "Smuggler's Surprise", "stack")
            _prot(state, "smugglers_surprise")
            return {p.uid for p in victims if is_creature(p) and power(state, p) >= 4}
    for pl in perms_named(state, "Plaza of Heroes"):
        if not pl.tapped and afford(state, 3, (), ignore_reserve=True):
            leg = [p for p in victims if eff_card(p).legendary and is_creature(p)]
            if leg:
                best = max(leg, key=lambda p: (counter_target_value(state, p), -p.uid))
                pl.tapped = True
                spend(state, 3, ())
                state.battlefield.remove(pl)                      # {3},{T}, exile this land
                saved.add(best.uid)
                _prot(state, "plaza")
                break
    for kind, src in regenerate_sources(state):
        if kind == "swarmyard":
            cands = [p for p in victims if "Insect" in perm_subtypes(p) and p.uid not in saved and is_creature(p)]
        else:
            cands = [p for p in victims if is_creature(p) and p.uid not in saved]
        if not cands:
            continue
        tgt = max(cands, key=lambda p: (counter_target_value(state, p), -p.uid))
        if kind == "hollow":
            src.tapped = True
            spend(state, 0, (frozenset("G"),))
        else:
            src.tapped = True
        state.regenerations_used += 1
        saved.add(tgt.uid)
        _prot(state, "regenerate")
    return saved


def try_smart_opponent_removal(state: GameState) -> Optional[str]:
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    target_name = next((n for n in INTERACTION_ENGINE_PRIORITY if any(eff_name(p) == n for p in state.battlefield)), None)
    if target_name is None:
        return None
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    perm = next(p for p in state.battlefield if eff_name(p) == target_name)
    # Swiftfoot Boots: a criatura equipada tem hexproof (remocao pontual nao pode mira-la)
    if any(q.attached_to == perm.uid for q in state.battlefield if "boots" in q.card.tags):
        _prot(state, "boots_hexproof")
        return None
    if is_creature(perm):
        saved = try_protect_from_destroy(state, [perm], spell_mv=3)
    else:
        saved = try_protect_from_destroy(state, [perm], spell_mv=3)
    if perm.uid in saved:
        return None
    remove_permanent(state, perm, "opponent_removal")
    state.smart_removals_total += 1
    return target_name


def try_smart_opponent_attack(state: GameState) -> Optional[str]:
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    chance = interaction_chance(state) * (POST_WIPE_ATTACK_HASTE_FACTOR if state.wiped_this_round else 1.0)
    if state.interaction_rng.random() >= chance:
        return None
    name, pw = state.interaction_rng.choice(OPPONENT_ATTACKER_PROFILES)
    state.smart_attacks_taken_total += 1
    state.smart_attack_damage_total += pw
    if has_perm(state, "Angel of Suffering"):
        # "If damage would be dealt to you, prevent that damage and mill twice that many cards."
        state.angel_prevented_total += pw
        mill_event(state, [(0, 2 * pw)], source="angel_of_suffering")
    else:
        lose_life_self(state, pw, "opponent_attack")
    return name


def try_smart_opponent_discard(state: GameState) -> Optional[str]:
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS or not state.hand:
        return None
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    target = state.interaction_rng.choice(state.hand)
    state.hand.remove(target)
    put_card_into_graveyard(state, target, "hand")
    state.smart_discards_total += 1
    return target


def try_smart_opponent_wipe(state: GameState) -> Optional[list]:
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * TOTAL_WIPE_CHANCE_FACTOR:
        return None
    candidates = {"creature": [p for p in state.battlefield if is_creature(p)],
                  "artifact": [p for p in state.battlefield if is_artifact(p) and "land" not in p.card.types],
                  "enchantment": [p for p in state.battlefield if "enchantment" in eff_card(p).types and "land" not in p.card.types]}
    available = [t for t in ("creature", "artifact", "enchantment") if candidates[t]]
    if not available:
        return None
    wipe_type = state.interaction_rng.choices(available, weights=[WIPE_TYPE_WEIGHTS[t] for t in available])[0]
    victims = list(candidates[wipe_type])
    saved = try_protect_from_destroy(state, victims, spell_mv=4)
    names = [eff_name(p) for p in victims if p.uid not in saved and p in state.battlefield]
    kill_group(state, [p for p in victims if p.uid not in saved], "opponent_wipe")
    if wipe_type == "creature":
        state.smart_wipes_total += 1
        state.wiped_this_round = True
    elif wipe_type == "artifact":
        state.smart_artifact_wipes_total += 1
    else:
        state.smart_enchantment_wipes_total += 1
    return names


def try_smart_opponent_graveyard_wipe(state: GameState) -> Optional[list]:
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS or state.graveyard_wipe_used or not state.graveyard:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * GRAVEYARD_WIPE_CHANCE_FACTOR:
        return None
    exiled = list(state.graveyard)
    state.graveyard.clear()                       # exilio em massa: NAO dispara o gatilho do Kozilek (nao vai ao cemiterio) e tira o combustivel de Muldrotha/Icetill/Six
    state.graveyard_wipe_used = True
    state.smart_graveyard_hate_total += 1
    graveyard_leave(state, exiled)
    return exiled


def try_smart_opponent_graveyard_snipe(state: GameState) -> Optional[str]:
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    cands = [c for c in state.graveyard if "creature" in CARD_DB[c].types and not CARD_DB[c].token]
    if not cands or state.interaction_rng.random() >= interaction_chance(state) * GRAVEYARD_SNIPE_CHANCE_FACTOR:
        return None
    target = max(cands, key=lambda c: (CARD_DB[c].mv, c))
    state.graveyard.remove(target)
    state.smart_graveyard_snipes_total += 1
    graveyard_leave(state, [target])
    return target


def try_smart_opponent_counter(state: GameState) -> bool:
    """Counterspell que mira a conjuracao do comandante (o motor inteiro depende do Mothman resolver)."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return False
    if state.interaction_rng.random() >= interaction_chance(state) * COUNTERSPELL_CHANCE_FACTOR:
        return False
    state.smart_counters_total += 1
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


def simulate_one_with_interaction(seed: int, turns: int = 12) -> GameState:
    state = new_state(seed)
    state.interaction_rng = random.Random(seed + 999_999)
    for _ in range(turns):
        play_turn(state)
        if state.game_over:
            break
        state.wiped_this_round = False
        for o in list(state.opps):
            if o.eliminated:
                continue
            opponent_turn(state, o)
            if state.game_over:
                break
            try_smart_opponent_turn(state)
            if state.game_over:
                break
        if state.game_over:
            break
        jace_removal_roll(state)
        riverchurn_opp_end_step(state)
    finalize(state)
    return state
