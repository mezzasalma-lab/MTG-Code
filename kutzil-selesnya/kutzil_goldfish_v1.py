"""
Goldfish simulator — Kutzil, Malamet Exemplar (Selesnya, G/W, +1/+1 counters)

Construido do zero em 2026-09-02, a pedido direto do usuario ("Pode
comecar com o Kutzil" -- um dos 4 decks desta pasta sem simulador ainda).
Passo 0 (regra de `references/goldfish-sim-card-rules.md`, mesma
disciplina aplicada em toda a auditoria "compile TUDO" desta sessao):
oraculo real de TODAS as 92 cartas (91 nao-basicas + comandante)
consultado ao vivo via Scryfall (`POST /cards/collection` em 2 lotes +
`/cards/named?fuzzy=` pros 4 MDFCs que nao resolveram no lote), nao
memoria nem a `auditoria.md` anterior (que ja e boa, mas foi escrita
antes desta leitura linha-a-linha e nao e a fonte de verdade aqui).

======================================================================
ARQUITETURA -- por que Permanent-objetos (nao lista de nomes)
======================================================================
Ao contrario da maioria dos simuladores desta sessao (que representam
o campo como uma lista de strings de nome), este deck tem contadores
+1/+1 como o proprio motor central -- praticamente toda carta relevante
poe, multiplica, move ou consulta contadores por CRIATURA especifica, e
o proprio gatilho de compra da comandante ("creatures... with power
greater than its base power") exige saber o poder atual PERMANENTE vs.
poder impresso de cada criatura individual. Um modelo de nomes puros
nao suportaria isso sem gambiarra. Copiei o padrao ja usado no
`toph_goldfish_v1.py` desta mesma sessao (Permanent = card + counters +
tapped + entered_turn + campos extras), que resolve exatamente esse
mesmo problema (earthbend la, counters aqui).

======================================================================
MOTOR CENTRAL -- empilhamento de multiplicadores de contador
======================================================================
6 fontes reais alteram QUANTOS contadores +1/+1 sao colocados de cada
vez que "um ou mais contadores +1/+1 seriam colocados":
- Hardened Scales: "+1" (aditivo)
- Michelangelo, Weirdness to 11: "+1" (aditivo, mesmo texto)
- Ozolith, the Shattered Spire (estatica, separada da ativada dele):
  "+1" (aditivo)
- Branching Evolution: "dobra" (multiplicativo)
- The Earth Crystal: "dobra" (multiplicativo)
- Innkeeper's Talent nivel 3: "dobra de TODO tipo de contador" (multiplicativo)

Regra real (CR 616): quando multiplos efeitos de substituicao se
aplicam ao mesmo evento, o CONTROLADOR DO PERMANENTE escolhe a ordem.
Um piloto racional sempre aplica os ADITIVOS primeiro e so DEPOIS os
MULTIPLICATIVOS -- (base+k)*2^m >= base*2^m+k pra qualquer k,m>=0 -- que
e estritamente igual ou melhor que qualquer outra ordem. Implementado
em `place_counters()`, usado por TODA fonte de contador do arquivo (mais
de 20 gatilhos diferentes), pra nao duplicar a logica de multiplicador
em cada um.

Proliferate (Metastatic Evangel) tambem passa pelos MESMOS
multiplicadores (CR 121.5, proliferate poe contadores via o mesmo
mecanismo de "put a counter on", sujeito a efeitos de substituicao) --
implementado chamando `place_counters()` pra cada permanente
proliferado, nao um `+1` cru.

======================================================================
SEM OPONENTE REAL (convencao identica a TODOS os outros 13 simuladores
desta sessao)
======================================================================
Combate: toda criatura apta ataca e conecta sem bloqueio (nenhum
simulador desta biblioteca modela bloqueadores de oponente). Dano vira
`proxy_damage_total`, nunca vida real de ninguem. Remocao/interacao
(Path to Exile, Swords to Plowshares, Damning Verdict [ver nota
especial abaixo], Knight of Autumn modo destroy, Hopeful Initiate,
Requisition Raid, Witch Enchanter, Kabira Takedown, District Mascot,
Wakka [modo destruir artefato]) conta como metrica de interacao
(`interaction_plays`), sem alvo de oponente real pra destruir de
verdade -- mesma convencao usada em toda a sessao (Toph, Beorn,
Megatron, etc).

Excecao real: **Damning Verdict** ("Destroy all creatures with no
counters on them") NAO e simetrica pra nos -- destroi as PROPRIAS
criaturas sem contador (dorks ja gastos, criatura recem-conjurada sem
buff ainda). Diferente dos wipes simetricos-sem-excecao de outros decks
(Kindred Dominance etc, sempre 📊 por Regra 1), aqui a carta foi
desenhada pelo proprio piloto pra ser quase-assimetrica ("como o board
vive coberto de contadores, isso tende a ser um wrath quase uma via so
contra o oponente" -- auditoria.md secao 6). Implementada de verdade:
destroi toda criatura com 0 contadores, mas so' e' conjurada quando a
perda e' pequena o bastante pra valer a pena (heuristica documentada no
dispatch, nao um "nunca conjura").

Protecao (Teferi's Protection, Mother of Runes, Swiftfoot Boots,
Dauntless Escort, Akroma's Will modo indestructible, Delighted
Halfling's "can't be countered", Clever Concealment, Galadriel's
Dismissal) -- 📊 estrutural (sem oponente/contramagica/remocao alheia
pra proteger contra), exceto onde ha efeito ESTATICO real sem depender
de oponente (Delighted Halfling reduz o CUSTO de spells legendarias
mesmo sem contramagica no jogo -- isso E implementado).

Saddle (District Mascot, Ornery Tumblewagg) e Warp/Plot (Broodguard
Elite, Railway Brawler) sao mecanicas novas nesta sessao -- ver
comentarios nos pontos de implementacao especificos.
"""

import random
import statistics
import json
from dataclasses import dataclass, field
from typing import Optional


# =========================================================
# CARD DATABASE
# =========================================================

@dataclass
class Card:
    name: str
    mv: int
    ctype: str  # "creature","land","artifact","enchantment","instant","sorcery","aura"
    tags: frozenset = field(default_factory=frozenset)
    power: int = 0
    toughness: int = 0
    pips: dict = field(default_factory=dict)      # {"G":1,"W":1} generic nao contado
    produces: frozenset = field(default_factory=frozenset)  # cores que land/dork produz
    is_x: bool = False


CARD_DB: dict[str, Card] = {}


def add(name, mv, ctype, tags=(), power=0, toughness=0, pips=None, produces=None, is_x=False):
    CARD_DB[name] = Card(name=name, mv=mv, ctype=ctype, tags=frozenset(tags), power=power,
                          toughness=toughness, pips=dict(pips or {}),
                          produces=frozenset(produces or ()), is_x=is_x)


COMMANDER = "Kutzil, Malamet Exemplar"
add(COMMANDER, 3, "creature", {"commander"}, power=3, toughness=3, pips={"G": 1, "W": 1})

# --- Terrenos (32) --------------------------------------------------------
# Achado real 2026-09-02 (leitura linha-a-linha real, Scryfall): classificacao
# de "enters tapped" checada carta a carta, nao presumida por semelhanca.
add("Command Tower", 0, "land", set(), produces={"G", "W"})
add("Exotic Orchard", 0, "land", set(), produces={"G", "W"})  # sem oponente real: simplificado pra qualquer cor da nossa propria identidade (G/W), documentado
add("Sol Ring", 1, "artifact", {"rock2"})
add("War Room", 0, "land", {"war_room_draw"})
add("Windswept Heath", 0, "land", {"fetch_gw"})
add("Boseiju, Who Endures", 0, "land", {"legendary_land", "boseiju_channel"}, produces={"G"})
add("Eiganjo, Seat of the Empire", 0, "land", {"legendary_land", "eiganjo_channel"}, produces={"W"})
add("Brushland", 0, "land", set(), produces={"G", "W"})  # painland: sempre destapada, sem custo de vida modelado (mesma convencao de Ur-Dragon)
add("Horizon Canopy", 0, "land", {"horizon_canopy_sac"}, produces={"G", "W"})
add("Sunpetal Grove", 0, "land", {"checkland_gw"}, produces={"G", "W"})
add("Canopy Vista", 0, "land", {"battleland_gw"}, produces={"G", "W"})
add("Temple Garden", 0, "land", set(), produces={"G", "W"})  # shockland: sempre paga 2 (premissa ja usada em Ur-Dragon/Thranduil)
add("Overgrown Farmland", 0, "land", {"slowland_gw"}, produces={"G", "W"})
add("Bountiful Promenade", 0, "land", set(), produces={"G", "W"})  # battleland "2+ oponentes": sempre destapada, CR 103.8a multiplayer
add("Fortified Village", 0, "land", {"revealland_gw"}, produces={"G", "W"})
add("Hushwood Verge", 0, "land", {"hushwood_verge"}, produces={"G"})  # W condicional, ver white_sources()
add("Gavony Township", 0, "land", {"gavony_township"}, produces=set())
add("Mosswort Bridge", 0, "land", {"mosswort_bridge", "etb_tapped"}, produces={"G"})
add("Field of the Dead", 0, "land", {"field_of_the_dead", "etb_tapped"}, produces=set())
add("Abandoned Air Temple", 0, "land", {"tapped_unless_basic", "air_temple_anthem"}, produces={"W"})
add("Ba Sing Se", 0, "land", {"tapped_unless_basic", "ba_sing_se_earthbend"}, produces={"G"})
add("Branchloft Pathway // Boulderloft Pathway", 0, "land", {"pathway_gw"}, produces={"G", "W"})
add("Bridgeworks Battle // Tanglespan Bridgeworks", 3, "sorcery", {"bridgeworks_battle", "mdfc_land_g"}, pips={"G": 1}, produces={"G"})
add("Kabira Takedown // Kabira Plateau", 2, "instant", {"kabira_takedown", "mdfc_land_tapped_w"}, pips={"W": 1}, produces={"W"})
add("Witch Enchanter // Witch-Blessed Meadow", 4, "creature", {"witch_enchanter", "mdfc_land_w"}, power=2, toughness=2, pips={"W": 1}, produces={"W"})

BASIC_LAND_NAMES = {"Forest", "Plains", "Snow-Covered Forest", "Snow-Covered Plains"}
add("Forest", 0, "land", {"basic"}, produces={"G"})
add("Plains", 0, "land", {"basic"}, produces={"W"})
add("Snow-Covered Forest", 0, "land", {"basic"}, produces={"G"})
add("Snow-Covered Plains", 0, "land", {"basic"}, produces={"W"})

# --- Ramp / mana dorks ------------------------------------------------------
add("Avacyn's Pilgrim", 1, "creature", {"dork_flat1_w"}, power=1, toughness=1, pips={"G": 1}, produces={"W"})
add("Birds of Paradise", 1, "creature", {"dork_flatX"}, power=0, toughness=1, pips={"G": 1}, produces={"G", "W"})
add("Fyndhorn Elves", 1, "creature", {"dork_flat1_g"}, power=1, toughness=1, pips={"G": 1}, produces={"G"})
add("Llanowar Elves", 1, "creature", {"dork_flat1_g"}, power=1, toughness=1, pips={"G": 1}, produces={"G"})
add("Delighted Halfling", 1, "creature", {"dork_flatX", "legendary_fixer_free"}, power=1, toughness=2, pips={"G": 1})  # produces vazio de proposito -- {T}: Add {C} e' incolor; a fixacao de cor so vale pra spell legendario, ver color_sources()
add("Biophagus", 2, "creature", {"dork_flatX", "biophagus_bonus"}, power=1, toughness=3, pips={"G": 1}, produces={"G", "W"})

# --- Base / criaturas geradoras/pagadoras de contador ------------------------------------------------------
add("Agent Bishop, Man in Black", 3, "creature", {"legendary", "combat_counter_2targets"}, power=1, toughness=2, pips={"W": 1})
add("Beast Whisperer", 4, "creature", {"creature_cast_draw"}, power=2, toughness=3, pips={"G": 2})
add("Botanical Brawler", 2, "creature", {"botanical_brawler"}, power=0, toughness=0, pips={"G": 1, "W": 1})
add("Broodguard Elite", 2, "creature", {"etb_counters_x", "warp", "leaves_counters_move"}, power=0, toughness=0, pips={"G": 2}, is_x=True)
add("Champion of Lambholt", 3, "creature", {"champion_lambholt"}, power=1, toughness=1, pips={"G": 2})
add("Collector's Cage", 2, "artifact", {"hideaway5", "collectors_cage_activate"}, pips={"W": 1})
add("Craterhoof Behemoth", 8, "creature", {"finisher", "haste", "craterhoof_etb"}, power=5, toughness=5, pips={"G": 3})
add("Dauntless Escort", 3, "creature", {"protection_unused"}, power=3, toughness=3, pips={"G": 1, "W": 1})
add("District Mascot", 1, "creature", {"etb_counter1", "saddle1_attack_counter", "district_mascot_activate"}, power=0, toughness=0, pips={"G": 1})
add("Duskshell Crawler", 2, "creature", {"etb_counter_target1", "trample_grant_countered"}, power=0, toughness=3, pips={"G": 1})
add("Dyadrine, Synthesis Amalgam", 2, "creature", {"etb_counters_x", "attack_remove2_draw_token"}, power=0, toughness=1, pips={"G": 1, "W": 1}, is_x=True)
add("Esper Sentinel", 1, "creature", {"opponent_dependent"}, power=1, toughness=1, pips={"W": 1})
add("Generous Pup", 2, "creature", {"generous_pup"}, power=2, toughness=2, pips={"W": 1})
add("Goldvein Hydra", 1, "creature", {"etb_counters_x", "dies_treasure"}, power=0, toughness=0, pips={"G": 1}, is_x=True)
add("Hopeful Initiate", 1, "creature", {"training", "hopeful_initiate_activate"}, power=1, toughness=2, pips={"W": 1})
add("Knight of Autumn", 3, "creature", {"knight_of_autumn"}, power=2, toughness=1, pips={"G": 1, "W": 1})
add("Kodama of the West Tree", 3, "creature", {"legendary", "kodama_land_tutor", "modified_trample"}, power=3, toughness=3, pips={"G": 1})
add("Lion Sash", 2, "creature", {"lion_sash"}, power=1, toughness=1, pips={"W": 1})
add("Luminarch Aspirant", 2, "creature", {"combat_counter_target1"}, power=1, toughness=1, pips={"W": 1})
add("Maester Seymour", 3, "creature", {"legendary", "maester_seymour_combat", "maester_seymour_monstrosity"}, power=1, toughness=3, pips={"G": 1})
add("Managorger Hydra", 3, "creature", {"managorger"}, power=1, toughness=1, pips={"G": 1})
add("Metastatic Evangel", 2, "creature", {"metastatic_evangel"}, power=3, toughness=1, pips={"W": 1})
add("Michelangelo, Weirdness to 11", 2, "creature", {"legendary", "counter_bonus1", "michelangelo_etb"}, power=1, toughness=1, pips={"G": 1})
add("Mikey & Leo, Chaos & Order", 2, "creature", {"legendary", "mikey_leo_draw"}, power=2, toughness=2, pips={})
add("Mother of Runes", 1, "creature", {"protection_unused"}, power=1, toughness=1, pips={"W": 1})
add("Ornery Tumblewagg", 3, "creature", {"combat_counter_target1", "saddle2_attack_double"}, power=2, toughness=2, pips={"G": 1})
add("Ouroboroid", 4, "creature", {"ouroboroid_combat"}, power=1, toughness=3, pips={"G": 2})
add("Railway Brawler", 5, "creature", {"railway_brawler_etb", "plot"}, power=5, toughness=5, pips={"G": 2})
add("Rishkar, Peema Renegade", 3, "creature", {"legendary", "rishkar_etb", "rishkar_mana"}, power=2, toughness=2, pips={"G": 1})
add("Selvala, Heart of the Wilds", 3, "creature", {"legendary", "selvala_etb_draw", "selvala_mana"}, power=2, toughness=3, pips={"G": 2})
add("Stonecoil Serpent", 0, "creature", {"etb_counters_x"}, power=0, toughness=0, pips={}, is_x=True)
add("Summon: Fenrir", 3, "creature", {"saga_fenrir"}, power=3, toughness=2, pips={"G": 1})
add("The Earth King", 4, "creature", {"legendary", "earth_king_etb", "earth_king_attack"}, power=2, toughness=2, pips={"G": 1})
add("Urdnan, Dromoka Warrior", 2, "creature", {"legendary", "etb_counter_target1", "urdnan_attack"}, power=1, toughness=1, pips={"W": 1})
add("Wakka, Devoted Guardian", 4, "creature", {"legendary", "wakka_combat_damage", "wakka_endstep"}, power=4, toughness=4, pips={"G": 1, "W": 1})
add("Walking Ballista", 0, "creature", {"etb_counters_x", "ballista_ping"}, power=0, toughness=0, pips={}, is_x=True)

# --- Enchantments / artefatos de suporte -----------------------------------
add("Akroma's Will", 4, "instant", {"protection_unused"}, pips={"W": 1})
add("Branching Evolution", 3, "enchantment", {"counter_double"}, pips={"G": 1})
add("Clever Concealment", 4, "instant", {"protection_unused"}, pips={"W": 2})
add("Damning Verdict", 5, "sorcery", {"damning_verdict"}, pips={"W": 2})
add("Galadriel's Dismissal", 1, "instant", {"protection_unused"}, pips={"W": 1})
add("Hardened Scales", 1, "enchantment", {"counter_bonus1"}, pips={"G": 1})
add("Innkeeper's Talent", 2, "enchantment", {"innkeepers_talent"}, pips={"G": 1})
add("Ozolith, the Shattered Spire", 2, "artifact", {"ozolith"}, pips={"G": 1})
add("Path to Exile", 1, "instant", {"interaction"}, pips={"W": 1})
add("Puca's Covenant", 3, "enchantment", {"pucas_covenant"}, pips={"G": 1})
add("Rancor", 1, "aura", {"rancor"}, pips={"G": 1})
add("Requisition Raid", 1, "sorcery", {"interaction", "requisition_raid_counters"}, pips={"W": 1})
add("Restoration Seminar", 7, "sorcery", {"restoration_seminar"}, pips={"W": 2})
add("Sphere Grid", 2, "enchantment", {"sphere_grid"}, pips={"G": 1})
add("Swiftfoot Boots", 2, "artifact", {"protection_unused"}, pips={})
add("Swords to Plowshares", 1, "instant", {"interaction"}, pips={"W": 1})
add("Tale of Katara and Toph", 3, "enchantment", {"tale_katara_toph"}, pips={"G": 1})
add("Teferi's Protection", 3, "instant", {"protection_unused"}, pips={"W": 1})
add("Terrasymbiosis", 3, "enchantment", {"terrasymbiosis"}, pips={"G": 1})
add("The Earth Crystal", 4, "artifact", {"legendary", "counter_double", "green_cost_reduce"}, pips={"G": 2})
add("The Great Henge", 9, "artifact", {"legendary", "great_henge_power_reduce", "great_henge_etb"}, pips={"G": 2})

# --- Tokens ------------------------------------------------------------
add("Bear Token", 0, "creature", {"token"}, power=4, toughness=4)        # The Earth King
add("Robot Token", 0, "creature", {"token"}, power=2, toughness=2)       # Dyadrine
add("Zombie Token", 0, "creature", {"token"}, power=2, toughness=2)      # Field of the Dead
add("Mutagen Token", 0, "artifact", {"token", "mutagen_token"})          # Michelangelo (nao e' criatura)
add("The Ozolith", 1, "artifact", {"legendary", "ozolith_hoard"}, pips={})
add("Training Regimen", 4, "enchantment", {"combat_counter_target1", "trample_grant_countered"}, pips={"G": 1})


LAND_NAMES = {n for n, c in CARD_DB.items() if c.ctype == "land"}
NONBASIC_REAL_LAND_NAMES = LAND_NAMES - BASIC_LAND_NAMES  # inclui MDFC land-sides tratadas como land aqui
# cartas com "land" so' num dos 2 lados (MDFC) tambem contam pra "terreno em campo" quando jogadas como terreno
MDFC_LAND_SPELLS = {"Bridgeworks Battle // Tanglespan Bridgeworks", "Kabira Takedown // Kabira Plateau",
                    "Witch Enchanter // Witch-Blessed Meadow"}


def is_creature_card(name: str) -> bool:
    return CARD_DB[name].ctype == "creature"


def is_land_card(name: str) -> bool:
    return CARD_DB[name].ctype == "land"


def has_tag(name: str, tag: str) -> bool:
    return tag in CARD_DB[name].tags


# =========================================================
# GAME STATE
# =========================================================

@dataclass
class Permanent:
    card: Card
    tapped: bool = False
    counters: int = 0
    entered_turn: int = 0
    uid: int = 0
    is_token: bool = False
    saddled: bool = False
    temp_power: int = 0          # bonus "until end of turn" (Bridgeworks Battle, Akroma's Will)
    temp_trample: bool = False
    aura_power: int = 0          # bonus PERMANENTE de aura (Rancor +2/+0), nao reseta no fim do turno
    has_rancor: bool = False     # Rancor: "when put into graveyard from battlefield, return to hand"
    saga_chapter: int = 0        # Summon: Fenrir
    level: int = 1               # Innkeeper's Talent (Class)
    monstrous: bool = False      # Maester Seymour
    warp_pending: bool = False   # Broodguard Elite
    plot_pending: bool = False   # Railway Brawler
    exile_return_turn: Optional[int] = None
    equipped_to: Optional[int] = None  # Lion Sash reconfigure -> uid do alvo


@dataclass
class GameState:
    turn: int = 0
    hand: list = field(default_factory=list)
    battlefield: list = field(default_factory=list)   # list[Permanent]
    graveyard: list = field(default_factory=list)      # list[str]
    library: list = field(default_factory=list)        # list[str]
    exile_warp: list = field(default_factory=list)     # list[Permanent] exiladas por warp/plot/hideaway, esperando recast
    hideaway_cards: dict = field(default_factory=dict)  # uid_do_permanente_com_hideaway -> nome da carta exilada
    mulligans: int = 0

    lands_played_this_turn: int = 0
    mana_spent_this_turn: int = 0
    bonus_mana_pool: int = 0
    next_uid: int = 1
    tapped_land_this_turn: Optional[int] = None  # uid do land que entrou tapped este turno (nao conta pra mana)

    commander_in_play: bool = False
    commander_cast_count: int = 0
    commander_cast_turn: Optional[int] = None
    commander_uid: Optional[int] = None

    life_total: int = 40

    green_used_generic: bool = False  # nao usado, placeholder de simetria

    # metrics -------------------------------------------------------------
    proxy_damage_total: int = 0
    kutzil_draws_total: int = 0
    cards_drawn_extra: int = 0
    interaction_plays: int = 0
    tokens_created: int = 0
    ramp_pieces_in_play: int = 0
    finisher_resolved_total: int = 0
    first_finisher_turn: Optional[int] = None
    recursion_events_total: int = 0

    mikey_leo_drawn_this_turn: bool = False
    terrasymbiosis_drawn_this_turn: bool = False
    generous_pup_triggered_this_turn: bool = False
    botanical_brawler_first_counter_this_turn: set = field(default_factory=set)  # uids que ja ganharam 1o contador este turno

    counters_placed_total: int = 0
    great_henge_cast: bool = False
    craterhoof_cast: bool = False
    damning_verdict_cast_total: int = 0
    saddle_activations_total: int = 0
    warp_plot_free_casts_total: int = 0
    library_emptied: bool = False
    pending_x: int = 0                       # X escolhido pro spell/permanente sendo resolvido agora (etb_counters_x)
    fenrir_chapter2_pending: bool = False     # Summon: Fenrir capitulo II: proxima criatura ganha +1 contador extra
    biophagus_pending: bool = False           # Biophagus: mana gasta nele -> criatura conjurada ganha +1 contador extra
    wakka_counter_this_turn: bool = False     # Wakka: "if a counter was put on Wakka this turn" (Blitzball Captain, end step)
    plot_exile: dict = field(default_factory=dict)   # turno-em-que-plotou -> [nomes] (Railway Brawler)
    pucas_covenant_triggered_this_turn: bool = False  # Puca's Covenant: "once each turn"
    tale_katara_toph_first_tap_this_turn: set = field(default_factory=set)  # uids ja tapados (1a vez) este turno


def mk_perm(state: GameState, name: str, is_token: bool = False) -> Permanent:
    p = Permanent(card=CARD_DB[name], entered_turn=state.turn, uid=state.next_uid, is_token=is_token)
    state.next_uid += 1
    return p


def find_perm(state: GameState, uid: int) -> Optional[Permanent]:
    return next((p for p in state.battlefield if p.uid == uid), None)


def is_creature(perm: Permanent) -> bool:
    return perm.card.ctype == "creature"


def base_power(perm: Permanent) -> int:
    return perm.card.power


def effective_power(perm: Permanent) -> int:
    """Poder atual real: base + contadores + bonus de aura permanente (Rancor) + bonus temporario ate o fim do turno (Bridgeworks Battle/Akroma's Will)."""
    p = perm.card.power + perm.counters + perm.aura_power + perm.temp_power
    return max(0, p)


def is_buffed_beyond_base(perm: Permanent) -> bool:
    """Kutzil: 'creatures... each with power greater than its base power'."""
    return effective_power(perm) > base_power(perm)


# =========================================================
# MANA MODEL (G/W, pip-a-pip)
# =========================================================

def land_enters_tapped(state: GameState, name: str) -> bool:
    lands_in_play = [p for p in state.battlefield if is_land_card(p.card.name) or p.card.name in MDFC_LAND_SPELLS]
    n_lands = len(lands_in_play)
    basics_in_play = any(p.card.name in BASIC_LAND_NAMES for p in state.battlefield)
    if has_tag(name, "etb_tapped"):
        return True
    if name == "Temple Garden":
        return False  # shockland: sempre paga 2 de vida (premissa ja usada em Ur-Dragon/Thranduil)
    if has_tag(name, "checkland_gw"):
        return not any(p.card.name in ("Forest", "Snow-Covered Forest", "Plains", "Snow-Covered Plains") for p in state.battlefield)
    if has_tag(name, "battleland_gw"):
        return n_lands < 2 or not any(p.card.name in BASIC_LAND_NAMES for p in state.battlefield)
    if has_tag(name, "slowland_gw"):
        return n_lands < 2  # "unless you control two or more OTHER lands" -- antes de contar esta
    if has_tag(name, "revealland_gw"):
        return not any(c in ("Forest", "Snow-Covered Forest", "Plains", "Snow-Covered Plains") for c in state.hand if c != name)
    if has_tag(name, "tapped_unless_basic"):
        return not basics_in_play
    if name == "Kabira Takedown // Kabira Plateau":
        return True  # Kabira Plateau: "This land enters tapped." incondicional
    if name in ("Bridgeworks Battle // Tanglespan Bridgeworks", "Witch Enchanter // Witch-Blessed Meadow"):
        return False  # pagam 3 de vida (mesma premissa dos shocklands: sempre paga)
    return False


def green_sources(state: GameState) -> int:
    n = 0
    for p in state.battlefield:
        if p.tapped or p.uid == state.tapped_land_this_turn:
            continue
        if "G" in p.card.produces:
            n += 1
    return n


def white_sources(state: GameState) -> int:
    n = 0
    has_forest_or_plains = any(p.card.name in ("Forest", "Snow-Covered Forest", "Plains", "Snow-Covered Plains")
                                for p in state.battlefield)
    for p in state.battlefield:
        if p.tapped or p.uid == state.tapped_land_this_turn:
            continue
        if "W" in p.card.produces:
            n += 1
        elif p.card.name == "Hushwood Verge" and has_forest_or_plains:
            # "{T}: Add {W}. Activate only if you control a Forest or a
            # Plains." Achado real 2026-09-02: estava tratada como
            # incondicional (produces={"G","W"} generico) -- corrigido
            # pra checar a condicao real.
            n += 1
    return n


def is_legendary(name: str) -> bool:
    return has_tag(name, "legendary") or has_tag(name, "commander") or has_tag(name, "legendary_land")


def color_sources(state: GameState, color: str, spell_name: Optional[str] = None) -> int:
    n = green_sources(state) if color == "G" else white_sources(state)
    if spell_name is not None and is_legendary(spell_name):
        halfling = next((p for p in state.battlefield if p.card.name == "Delighted Halfling" and not p.tapped), None)
        if halfling is not None:
            # "{T}: Add one mana of any color. Spend this mana only to
            # cast a legendary spell, and that spell can't be
            # countered." -- ja contada genericamente em total_mana()
            # via dork_flatX (o modo {T}: Add {C}); aqui so cobre a
            # restricao de COR quando o spell e' legendario de verdade.
            n += 1
    return n


def rishkar_mana_bonus(state: GameState) -> int:
    """Rishkar, Peema Renegade: 'Each creature you control with a counter on
    it has "{T}: Add {G}."' -- so' conta criaturas destapadas com >=1
    contador (nao inclui a propria Rishkar salvo se ela mesma tiver
    contador)."""
    if not any(p.card.name == "Rishkar, Peema Renegade" for p in state.battlefield):
        return 0
    return sum(1 for p in state.battlefield if is_creature(p) and not p.tapped and p.counters > 0)


def total_mana(state: GameState) -> int:
    lands = sum(1 for p in state.battlefield
                if (is_land_card(p.card.name) or p.card.name in MDFC_LAND_SPELLS)
                and not p.tapped and p.uid != state.tapped_land_this_turn)
    rocks = sum(1 for p in state.battlefield if has_tag(p.card.name, "rock2") and not p.tapped) * 2
    dorks_flat = sum(1 for p in state.battlefield
                      if is_creature(p) and not p.tapped
                      and (has_tag(p.card.name, "dork_flat1_g") or has_tag(p.card.name, "dork_flat1_w") or has_tag(p.card.name, "dork_flatX")))
    return lands + rocks + dorks_flat + rishkar_mana_bonus(state) + state.bonus_mana_pool


def remaining_mana(state: GameState) -> int:
    return max(0, total_mana(state) - state.mana_spent_this_turn)


def spend_mana(state: GameState, n: int):
    state.mana_spent_this_turn += n


def selvala_mana_available(state: GameState) -> int:
    """Selvala, Heart of the Wilds: '{G}, {T}: Add X mana in any combination
    of colors, where X is the greatest power among creatures you control.'
    So conta se ela mesma esta destapada e ha mana pra pagar o {G}."""
    selvala = next((p for p in state.battlefield if p.card.name == "Selvala, Heart of the Wilds" and not p.tapped), None)
    if selvala is None:
        return 0
    creatures = [p for p in state.battlefield if is_creature(p)]
    if not creatures:
        return 0
    return max(effective_power(p) for p in creatures)


def legendary_creatures_count(state: GameState) -> int:
    return sum(1 for p in state.battlefield if is_creature(p) and has_tag(p.card.name, "legendary"))


def effective_cost(state: GameState, name: str) -> int:
    mv = CARD_DB[name].mv
    d = 0
    if any(p.card.name == "The Earth Crystal" for p in state.battlefield) and "G" in CARD_DB[name].pips:
        d += 1  # "Green spells you cast cost {1} less to cast."
    if name == "The Great Henge":
        # Achado real 2026-09-02 (leitura linha-a-linha, testes automatizados
        # depois do 1o draft): "This spell costs {X} less to cast, where X
        # is the greatest power among creatures you control." Tag
        # `great_henge_power_reduce` tinha ficado orfa no primeiro rascunho
        # -- a carta so' tinha o custo cheio {7}{G}{G}=9, praticamente
        # incastavel numa lista com curva baixa. Maior poder entre as
        # PROPRIAS criaturas em campo no momento da conjuracao.
        creatures = [p for p in state.battlefield if is_creature(p)]
        if creatures:
            d += max(effective_power(p) for p in creatures)
    return max(0, mv - d)


def can_cast(state: GameState, name: str) -> bool:
    cost = effective_cost(state, name)
    if remaining_mana(state) + selvala_mana_available(state) < cost:
        return False
    for color, needed in CARD_DB[name].pips.items():
        if color_sources(state, color, spell_name=name) < needed:
            return False
    return True


# =========================================================
# MOTOR CENTRAL DE CONTADORES (place_counters)
# =========================================================

def place_counters(state: GameState, perm: Permanent, base_amount: int, log: list, source: str = "") -> int:
    """Ponto UNICO de entrada pra "put N +1/+1 counters" -- aplica os 3
    aditivos (+1 cada) e depois os 3 multiplicativos (x2 cada), na ordem
    que maximiza o total (ver docstring do cabecalho, CR 616). So aceita
    criatura ou artefato (Ozolith em si, Walking Ballista, Stonecoil,
    Lion Sash) -- oraculo real de cada multiplicador confirma que todos
    valem pra "a creature you control" exceto Ozolith que e "an artifact
    or creature you control" (mais amplo, mas nunca prejudica aqui)."""
    if base_amount <= 0:
        return 0
    total = base_amount
    if any(p.card.name == "Hardened Scales" for p in state.battlefield):
        total += 1
    if any(p.card.name == "Michelangelo, Weirdness to 11" for p in state.battlefield):
        total += 1
    if any(p.card.name == "Ozolith, the Shattered Spire" for p in state.battlefield):
        total += 1
    doublers = 0
    if any(p.card.name == "Branching Evolution" for p in state.battlefield):
        doublers += 1
    if any(p.card.name == "The Earth Crystal" for p in state.battlefield):
        doublers += 1
    talent = next((p for p in state.battlefield if p.card.name == "Innkeeper's Talent"), None)
    if talent is not None and talent.level >= 3:
        doublers += 1
    total = total * (2 ** doublers)

    before = perm.counters
    perm.counters += total
    state.counters_placed_total += total
    log.append(f"  [+{total} counters] {perm.card.name} ({before}->{perm.counters}) via {source}")

    # Botanical Brawler: "Whenever one or more +1/+1 counters are put on
    # ANOTHER permanent you control, if it's the FIRST time this turn,
    # put a +1/+1 counter on this creature." -- recursivo (chama
    # place_counters de novo), mas guardado por permanente-por-turno pra
    # nao ser a fonte do seu proprio gatilho infinito.
    brawler = next((p for p in state.battlefield if p.card.name == "Botanical Brawler"), None)
    if brawler is not None and perm.uid != brawler.uid and perm.uid not in state.botanical_brawler_first_counter_this_turn:
        state.botanical_brawler_first_counter_this_turn.add(perm.uid)
        place_counters(state, brawler, 1, log, source="Botanical Brawler (gatilho)")

    # Generous Pup: "Whenever one or more +1/+1 counters are put on THIS
    # creature, put a +1/+1 counter on each OTHER creature you control.
    # Once each turn."
    pup = next((p for p in state.battlefield if p.card.name == "Generous Pup"), None)
    if pup is not None and perm.uid == pup.uid and not state.generous_pup_triggered_this_turn:
        state.generous_pup_triggered_this_turn = True
        for other in list(state.battlefield):
            if is_creature(other) and other.uid != pup.uid:
                place_counters(state, other, 1, log, source="Generous Pup (gatilho)")

    # Mikey & Leo: "Whenever you put a counter on a creature you control,
    # draw a card. Once each turn."
    if is_creature(perm) and any(p.card.name == "Mikey & Leo, Chaos & Order" for p in state.battlefield) and not state.mikey_leo_drawn_this_turn:
        state.mikey_leo_drawn_this_turn = True
        draw_cards(state, 1, log, source="Mikey & Leo")

    # Terrasymbiosis: "Whenever you put one or more +1/+1 counters on a
    # creature you control, you may draw that many cards. Once each turn."
    if is_creature(perm) and any(p.card.name == "Terrasymbiosis" for p in state.battlefield) and not state.terrasymbiosis_drawn_this_turn:
        state.terrasymbiosis_drawn_this_turn = True
        draw_cards(state, total, log, source="Terrasymbiosis")

    return total


def draw_cards(state: GameState, n: int, log: list, source: str = ""):
    for _ in range(n):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1
        else:
            state.library_emptied = True
    if n > 0:
        log.append(f"  [draw {n}] via {source}")


def gain_life(state: GameState, n: int, log: list, source: str = ""):
    state.life_total += n


def proliferate_own_board(state: GameState, log: list, source: str = ""):
    """CR 121.5: proliferate poe MAIS UM contador de cada tipo ja presente
    -- passa pelos mesmos multiplicadores de place_counters(), nao um +1
    cru (Metastatic Evangel)."""
    for p in list(state.battlefield):
        if p.counters > 0:
            place_counters(state, p, 1, log, source=source)


# =========================================================
# ENTRAR EM CAMPO -- dispatch central
# =========================================================

def enter_battlefield(state: GameState, perm: Permanent, log: list, from_cast: bool = True):
    state.battlefield.append(perm)
    if perm.card.name == COMMANDER:
        state.commander_in_play = True
        state.commander_uid = perm.uid
        if state.commander_cast_turn is None:
            state.commander_cast_turn = state.turn
    if is_creature(perm):
        on_creature_enters(state, perm, log, from_cast=from_cast)
    apply_etb(state, perm, log)
    if (has_tag(perm.card.name, "rock2") or has_tag(perm.card.name, "dork_flat1_g")
            or has_tag(perm.card.name, "dork_flat1_w") or has_tag(perm.card.name, "dork_flatX")):
        state.ramp_pieces_in_play += 1


def on_creature_enters(state: GameState, perm: Permanent, log: list, from_cast: bool = True):
    """Gatilhos de 'outra criatura sua entra' que dependem do que ja esta
    em campo -- chamado ANTES do proprio ETB de perm ser processado (a
    entrada em si ja aconteceu, a ordem entre gatilhos simultaneos nao
    importa aqui pois sao fontes independentes)."""
    is_nontoken = not perm.is_token

    for other in list(state.battlefield):
        if other.uid == perm.uid:
            continue
        if other.card.name == "Champion of Lambholt" and is_creature(other):
            place_counters(state, other, 1, log, source="Champion of Lambholt (outra criatura entrou)")
        if other.card.name == "Railway Brawler" and is_creature(other) and not other.tapped:
            # "Whenever another creature you control enters, put X +1/+1
            # counters on it, where X is its power." -- X = poder da
            # criatura QUE ENTROU (perm), no momento em que entra (ja
            # inclui contadores proprios que ela tenha trazido via ETB
            # antes desse ponto? Nao -- este hook roda ANTES do ETB de
            # perm, entao X = poder BASE aqui. Real: a entrada e o ETB
            # sao o mesmo evento; se ambos dessem contador simultaneamente
            # a ordem seria escolhida pelo controlador -- heuristica:
            # aplicar Railway Brawler ANTES maximiza X (menor), mas como
            # X so conta poder e nao contadores recebidos por ETB
            # simultaneo neste modelo simplificado, a ordem nao muda o
            # resultado pratico aqui.
            if effective_power(perm) > 0:
                place_counters(state, perm, effective_power(perm), log, source="Railway Brawler (outra criatura entrou)")
        if other.card.name == "The Great Henge" and is_nontoken:
            place_counters(state, perm, 1, log, source="The Great Henge (ETB)")
            draw_cards(state, 1, log, source="The Great Henge (ETB)")
        if other.card.name == "Metastatic Evangel" and is_nontoken:
            proliferate_own_board(state, log, source="Metastatic Evangel (outra criatura nao-token entrou)")

    # Selvala: "Whenever another creature enters, its controller may draw
    # a card if its power is greater than each other creature's power."
    # -- verifica DEPOIS de todos os +1/+1 acima terem sido aplicados
    # (poder final da criatura que entrou), contra o poder de TODAS as
    # outras (Selvala precisa estar em campo).
    if any(p.card.name == "Selvala, Heart of the Wilds" for p in state.battlefield):
        others = [p for p in state.battlefield if p.uid != perm.uid and is_creature(p)]
        if not others or effective_power(perm) > max(effective_power(o) for o in others):
            draw_cards(state, 1, log, source="Selvala, Heart of the Wilds (maior poder)")


def apply_etb(state: GameState, perm: Permanent, log: list):
    name = perm.card.name
    tags = perm.card.tags

    if "etb_counters_x" in tags:
        x = state.pending_x if hasattr(state, "pending_x") else 0
        if x > 0:
            place_counters(state, perm, x, log, source=f"{name} (ETB, X={x})")

    if name == "District Mascot":
        place_counters(state, perm, 1, log, source="District Mascot (ETB)")

    if name == "Duskshell Crawler":
        target = best_counter_target(state, exclude_uid=None)
        if target is not None:
            place_counters(state, target, 1, log, source="Duskshell Crawler (ETB)")

    if name == "Knight of Autumn":
        # Modal ETB -- sem oponente real pra destruir artefato/encantamento
        # alheio, entao o modo de valor real e' sempre "2 counters"
        # (alimenta o motor) em vez de "ganha 4 de vida" (estritamente
        # pior pra esse deck, que nao precisa de vida).
        place_counters(state, perm, 2, log, source="Knight of Autumn (ETB, modo contadores)")

    if name == "Michelangelo, Weirdness to 11":
        token = mk_perm(state, "Mutagen Token", is_token=True)
        state.battlefield.append(token)
        state.tokens_created += 1
        log.append("  [token] Mutagen Token (Michelangelo ETB)")

    if name == "Rishkar, Peema Renegade":
        targets = [p for p in state.battlefield if is_creature(p) and p.uid != perm.uid][:2]
        if not targets:
            targets = [perm]
        for t in targets[:2]:
            place_counters(state, t, 1, log, source="Rishkar, Peema Renegade (ETB)")

    if name == "The Earth King":
        token = mk_perm(state, "Bear Token", is_token=True)
        state.battlefield.append(token)
        state.tokens_created += 1
        log.append("  [token] Bear Token 4/4 (The Earth King ETB)")

    if name == "Urdnan, Dromoka Warrior":
        target = best_counter_target(state, exclude_uid=perm.uid) or perm
        place_counters(state, target, 1, log, source="Urdnan, Dromoka Warrior (ETB)")

    if name == "Craterhoof Behemoth":
        n = sum(1 for p in state.battlefield if is_creature(p))
        for p in state.battlefield:
            if is_creature(p):
                p.temp_power += n
                p.temp_trample = True
        state.craterhoof_cast = True
        if state.first_finisher_turn is None:
            state.first_finisher_turn = state.turn
        state.finisher_resolved_total += 1
        log.append(f"  [Craterhoof Behemoth] time +{n}/+{n} trample ate o fim do turno")

    if name == "Witch Enchanter // Witch-Blessed Meadow":
        state.interaction_plays += 1  # ETB destroy artifact/enchantment de oponente -- sem alvo real

    if name == "The Great Henge":
        state.great_henge_cast = True

    if name == "Summon: Fenrir":
        perm.saga_chapter = 1
        do_saga_fenrir_chapter(state, perm, log)

    if name == "Collector's Cage":
        # Hideaway 5: olha topo 5, exila 1 face-down, resto vai pro fundo
        # em ordem aleatoria. Heuristica: exila a melhor criatura (maior
        # mv) entre as 5, ja que a habilidade ativada so libera criatura
        # via "play the exiled card" sem restricao de tipo -- mas so vale
        # a pena esconder algo com custo real (nao um terreno, que nao
        # precisaria de graca nenhuma).
        top5 = state.library[:5]
        del state.library[:5]
        castable = [c for c in top5 if not is_land_card(c)]
        if castable:
            best = max(castable, key=lambda c: CARD_DB[c].mv)
            top5.remove(best)
            state.hideaway_cards[perm.uid] = best
            log.append(f"  [Collector's Cage] hideaway exila {best}")
        state.library.extend(top5)  # resto no fundo (ordem exata nao importa pro motor)

    if name == "Mosswort Bridge":
        top4 = state.library[:4]
        del state.library[:4]
        castable = [c for c in top4 if not is_land_card(c)]
        if castable:
            best = max(castable, key=lambda c: CARD_DB[c].mv)
            top4.remove(best)
            state.hideaway_cards[perm.uid] = best
            log.append(f"  [Mosswort Bridge] hideaway exila {best}")
        state.library.extend(top4)


def best_counter_target(state: GameState, exclude_uid: Optional[int]) -> Optional[Permanent]:
    """Heuristica generica de 'target creature you control' pra contador:
    prioriza a comandante (Kutzil se beneficia diretamente do gatilho de
    poder>base), senao a criatura de maior poder atual (mais perto de já
    ser relevante em combate)."""
    candidates = [p for p in state.battlefield if is_creature(p) and p.uid != exclude_uid]
    if not candidates:
        return None
    cmd = next((p for p in candidates if p.card.name == COMMANDER), None)
    if cmd is not None:
        return cmd
    return max(candidates, key=lambda p: effective_power(p))


def do_saga_fenrir_chapter(state: GameState, perm: Permanent, log: list):
    ch = perm.saga_chapter
    if ch == 1:
        basics = [n for n in state.library if n in BASIC_LAND_NAMES]
        if basics:
            found = basics[0]
            state.library.remove(found)
            land_perm = mk_perm(state, found)
            land_perm.tapped = True
            enter_battlefield(state, land_perm, log, from_cast=False)
            log.append(f"  [Summon: Fenrir I] busca {found} tapped")
    elif ch == 2:
        state.fenrir_chapter2_pending = True
        log.append("  [Summon: Fenrir II] proxima criatura conjurada este turno entra com +1/+1 extra")
    elif ch == 3:
        # "Draw a card if you control the creature with the greatest
        # power or tied for the greatest power" -- compara contra TODAS
        # as criaturas em jogo; sem oponente real, so' as nossas existem,
        # entao a condicao e' trivialmente sempre verdadeira se tivermos
        # ao menos 1 criatura (sempre "empatados" com nos mesmos).
        if any(is_creature(p) for p in state.battlefield):
            draw_cards(state, 1, log, source="Summon: Fenrir III")
        leave_battlefield(state, perm, log, to_graveyard=True)  # sacrifice apos capitulo III (regra real de Saga)


# =========================================================
# CONJURAR CARTAS
# =========================================================

def choose_x(state: GameState, name: str, budget: int) -> int:
    """Custo generico das X-spells desta lista e {X}{G} ou {X}{X} (Walking
    Ballista) ou {X}{G}{G} (Broodguard Elite) ou {X}{G}{W} (Dyadrine) --
    generic_pips = mv impresso MENOS os pips coloridos fixos, ja que mv
    aqui e' registrado como o "custo minimo" (X=0) mais os pips fixos.
    Walking Ballista ({X}{X}) e' o unico caso onde X conta em dobro no
    custo generico."""
    fixed = sum(CARD_DB[name].pips.values())
    if name == "Walking Ballista":
        x = max(0, budget // 2)
    else:
        x = max(0, budget - fixed)
    return min(x, 12)  # teto defensivo, sem custo real acima disso nesta lista


def on_spell_cast(state: GameState, name: str, log: list):
    """Managorger Hydra: 'Whenever a player casts a spell, put a +1/+1
    counter on this creature.' Sem oponente real, so' as PROPRIAS magias
    contam -- mas isso inclui QUALQUER spell (comandante, criatura,
    instant, sorcery), nao so' criaturas. Achado real 2026-09-02: tag
    `managorger` tinha ficado orfa no primeiro rascunho."""
    managorger = next((p for p in state.battlefield if p.card.name == "Managorger Hydra"), None)
    if managorger is not None:
        place_counters(state, managorger, 1, log, source="Managorger Hydra (spell conjurada)")

    # Beast Whisperer: "Whenever you cast a creature spell, draw a card."
    # Achado real 2026-09-02 (2a passada de verificacao de tags orfas):
    # 100% ausente no primeiro rascunho -- um motor de draw real (a
    # maioria dos spells desta lista sao criaturas).
    if is_creature_card(name) and any(p.card.name == "Beast Whisperer" for p in state.battlefield):
        draw_cards(state, 1, log, source="Beast Whisperer (criatura conjurada)")


def cast_card(state: GameState, name: str, log: list):
    on_spell_cast(state, name, log)
    card = CARD_DB[name]
    cost = effective_cost(state, name)
    x = 0
    if card.is_x:
        avail = remaining_mana(state) + selvala_mana_available(state)
        x = choose_x(state, name, avail)
        cost = x + sum(card.pips.values())

    use_selvala = remaining_mana(state) < cost
    if use_selvala:
        selvala = next((p for p in state.battlefield if p.card.name == "Selvala, Heart of the Wilds" and not p.tapped), None)
        if selvala is not None:
            selvala.tapped = True
            state.bonus_mana_pool += selvala_mana_available(state)
            log.append(f"  [Selvala] tapa por {state.bonus_mana_pool} mana bonus")

    spend_mana(state, cost)
    if name in state.hand:
        state.hand.remove(name)

    if card.is_x:
        state.pending_x = x

    biophagus_bonus = 0
    if is_creature_card_type(card) and any(p.card.name == "Biophagus" and not p.tapped for p in state.battlefield):
        biophagus = next(p for p in state.battlefield if p.card.name == "Biophagus" and not p.tapped)
        biophagus.tapped = True
        biophagus_bonus = 1
        log.append("  [Biophagus] mana gasta nele -- criatura vai entrar com +1 contador extra")

    if is_creature_card_type(card):
        resolve_permanent(state, name, log)
        fresh = state.battlefield[-1]
        if biophagus_bonus:
            place_counters(state, fresh, biophagus_bonus, log, source="Biophagus")
        if state.fenrir_chapter2_pending:
            state.fenrir_chapter2_pending = False
            place_counters(state, fresh, 1, log, source="Summon: Fenrir II")
    elif card.ctype == "aura":
        resolve_aura(state, name, log)
    elif card.ctype in ("land",):
        pass  # tratado em play_land
    else:
        resolve_instant_sorcery(state, name, log)

    state.pending_x = 0


def is_creature_card_type(card: Card) -> bool:
    return card.ctype == "creature"


def resolve_permanent(state: GameState, name: str, log: list):
    perm = mk_perm(state, name)
    enter_battlefield(state, perm, log)


def cast_free(state: GameState, name: str, log: list):
    """Conjura uma carta sem pagar custo (Collector's Cage hideaway)."""
    on_spell_cast(state, name, log)
    if CARD_DB[name].is_x:
        state.pending_x = 0  # X=0 quando conjurada de graca sem custo pago (regra real)
    if is_creature_card(name):
        resolve_permanent(state, name, log)
    elif CARD_DB[name].ctype == "aura":
        resolve_aura(state, name, log)
    else:
        resolve_instant_sorcery(state, name, log)


def resolve_aura(state: GameState, name: str, log: list):
    if name == "Rancor":
        target = best_counter_target(state, exclude_uid=None)
        if target is not None:
            target.aura_power += 2
            target.has_rancor = True
            log.append(f"  [Rancor] anexada a {target.card.name} (+2/+0 trample, permanente)")
        else:
            # sem criatura pra anexar -- carta e' descartada de fato (regra
            # real: Aura sem alvo legal vai direto pro cemiterio).
            state.graveyard.append(name)


def leave_battlefield(state: GameState, perm: Permanent, log: list, to_graveyard: bool = True):
    """Ponto central de saida de campo -- trata Rancor voltando pra mao
    ('When this Aura is put into a graveyard from the battlefield, return
    it to its owner's hand') e The Ozolith recebendo os contadores da
    criatura que morre."""
    if perm not in state.battlefield:
        return
    state.battlefield.remove(perm)
    if to_graveyard and not perm.is_token:
        state.graveyard.append(perm.card.name)

    if perm.has_rancor and to_graveyard:
        if "Rancor" in state.graveyard:
            state.graveyard.remove("Rancor")
        state.hand.append("Rancor")
        log.append(f"  [Rancor] volta pra mao (criatura enchant morreu: {perm.card.name})")

    # Goldvein Hydra: "When this creature dies, create a number of tapped
    # Treasure tokens equal to its power." Achado real 2026-09-02 (2a
    # passada de verificacao de tags orfas): 100% ausente. Poder no
    # momento da morte (antes de qualquer realocacao de contador abaixo).
    if to_graveyard and perm.card.name == "Goldvein Hydra" and effective_power(perm) > 0:
        n = effective_power(perm)
        state.bonus_mana_pool += n  # Treasure tapped -- valor equivalente a mana extra disponivel (simplificacao: sacrificado de imediato pro pool, ja que nao ha um "banco" de Treasures nao-sacrificados rastreado neste motor)
        log.append(f"  [Goldvein Hydra] morre, cria {n} Treasure(s) tapped")

    # Puca's Covenant: "Whenever a creature you control with a counter on
    # it dies, you may return another target permanent card with mana
    # value <= counters on that creature from your graveyard to your
    # hand. Once each turn." Achado real 2026-09-02.
    if (to_graveyard and perm.counters > 0
            and any(p.card.name == "Puca's Covenant" for p in state.battlefield)
            and not state.pucas_covenant_triggered_this_turn):
        pool = [c for c in state.graveyard if c != perm.card.name and CARD_DB[c].mv <= perm.counters]
        if pool:
            best = max(pool, key=lambda c: CARD_DB[c].mv)
            state.graveyard.remove(best)
            state.hand.append(best)
            state.pucas_covenant_triggered_this_turn = True
            state.recursion_events_total += 1
            log.append(f"  [Puca's Covenant] {perm.card.name} morreu ({perm.counters} contadores) -> devolve {best} pra mao")

    if perm.counters > 0 and to_graveyard:
        ozolith = next((p for p in state.battlefield if p.card.name == "The Ozolith"), None)
        if ozolith is not None:
            ozolith.counters += perm.counters
            log.append(f"  [The Ozolith] recebe {perm.counters} contadores de {perm.card.name}")
        elif perm.card.name == "Broodguard Elite":
            # so move via a propria habilidade se o Ozolith nao ja tiver
            # capturado os contadores (mesmo pool fisico, so uma das duas
            # habilidades pode realmente "pegar" -- piloto racional
            # escolhe a ordem, Ozolith primeiro nao muda o resultado
            # liquido (ambas so realocam pra outro permanente proprio).
            target = best_counter_target(state, exclude_uid=None)
            if target is not None:
                target.counters += perm.counters
                log.append(f"  [Broodguard Elite] move {perm.counters} contadores pra {target.card.name}")


def resolve_instant_sorcery(state: GameState, name: str, log: list):
    tags = CARD_DB[name].tags

    if "interaction" in tags:
        state.interaction_plays += 1
        if name in ("Path to Exile", "Swords to Plowshares"):
            pass  # exilio de criatura de oponente -- sem alvo real

    if name == "Requisition Raid":
        # Spree -- sem oponente real pros modos "destroy artifact/enchantment";
        # o modo "put a +1/+1 counter on each creature TARGET PLAYER
        # controls" so' vale a pena escolhido em NOS MESMOS.
        for p in state.battlefield:
            if is_creature(p):
                place_counters(state, p, 1, log, source="Requisition Raid")

    if name == "Damning Verdict":
        no_counter = [p for p in state.battlefield if is_creature(p) and p.counters == 0]
        state.damning_verdict_cast_total += 1
        for p in list(no_counter):
            leave_battlefield(state, p, log, to_graveyard=True)
        log.append(f"  [Damning Verdict] destroi {len(no_counter)} criatura(s) sem contador")

    if name == "Kabira Takedown // Kabira Plateau":
        state.interaction_plays += 1  # dano = numero de criaturas -- sem alvo de oponente real

    if name == "Bridgeworks Battle // Tanglespan Bridgeworks":
        target = best_counter_target(state, exclude_uid=None)
        if target is not None:
            target.temp_power += 2
            log.append(f"  [Bridgeworks Battle] +2/+2 ate o fim do turno em {target.card.name}")
        state.interaction_plays += 1  # fight -- sem alvo de oponente real

    if name == "Akroma's Will":
        for p in state.battlefield:
            if is_creature(p):
                p.temp_trample = True
        state.interaction_plays += 1

    if name == "Restoration Seminar":
        pool = [n for n in state.graveyard if n != name and (is_creature_card(n) or CARD_DB[n].ctype in ("artifact", "enchantment"))]
        if pool:
            best = max(pool, key=lambda n: CARD_DB[n].mv)
            state.graveyard.remove(best)
            if is_creature_card(best):
                resolve_permanent(state, best, log)
            else:
                perm = mk_perm(state, best)
                enter_battlefield(state, perm, log)
            state.recursion_events_total += 1
            log.append(f"  [Restoration Seminar] reanima {best}")


# =========================================================
# COMBATE
# =========================================================

def can_attack(perm: Permanent, state: GameState) -> bool:
    if not is_creature(perm):
        return False
    if perm.tapped:
        return False
    if "haste" in perm.card.tags:
        return True
    return perm.entered_turn < state.turn


def beginning_of_combat_triggers(state: GameState, log: list):
    for p in list(state.battlefield):
        name = p.card.name
        if name == "Agent Bishop, Man in Black":
            targets = sorted([q for q in state.battlefield if is_creature(q)], key=effective_power, reverse=True)[:2]
            for t in targets:
                place_counters(state, t, 1, log, source="Agent Bishop, Man in Black")
        elif name == "Innkeeper's Talent" and p.level >= 1:
            t = best_counter_target(state, exclude_uid=None)
            if t is not None:
                place_counters(state, t, 1, log, source="Innkeeper's Talent")
        elif name == "Luminarch Aspirant":
            t = best_counter_target(state, exclude_uid=None)
            if t is not None:
                place_counters(state, t, 1, log, source="Luminarch Aspirant")
        elif name == "Maester Seymour":
            t = best_counter_target(state, exclude_uid=p.uid)
            if t is not None and effective_power(p) > 0:
                place_counters(state, t, effective_power(p), log, source="Maester Seymour")
        elif name == "Ornery Tumblewagg":
            t = best_counter_target(state, exclude_uid=None)
            if t is not None:
                place_counters(state, t, 1, log, source="Ornery Tumblewagg")
        elif name == "Ouroboroid" and effective_power(p) > 0:
            for q in list(state.battlefield):
                if is_creature(q):
                    place_counters(state, q, effective_power(p), log, source="Ouroboroid")
        elif name == "The Ozolith" and p.counters > 0:
            t = best_counter_target(state, exclude_uid=None)
            if t is not None:
                moved = p.counters
                t.counters += moved
                p.counters = 0
                log.append(f"  [The Ozolith] move {moved} contadores pra {t.card.name}")
        elif name == "Training Regimen":
            t = best_counter_target(state, exclude_uid=None)
            if t is not None:
                place_counters(state, t, 1, log, source="Training Regimen")


def try_saddle(state: GameState, mount: Permanent, requirement: int, log: list) -> bool:
    """Saddle N: 'Tap any number of OTHER creatures you control with total
    power >= N.' Heuristica: usa as criaturas de MENOR poder disponiveis
    primeiro (preserva os maiores atacantes destapados), so tapa o que
    for necessario pra bater o requisito."""
    others = sorted([p for p in state.battlefield if is_creature(p) and p.uid != mount.uid and not p.tapped
                      and can_attack(p, state)], key=effective_power)
    total = 0
    used = []
    for p in others:
        if total >= requirement:
            break
        used.append(p)
        total += effective_power(p)
    if total < requirement:
        return False
    for p in used:
        p.tapped = True
    mount.saddled = True
    state.saddle_activations_total += 1
    log.append(f"  [Saddle] {mount.card.name} saddled (tapou {[u.card.name for u in used]})")
    return True


def combat_step(state: GameState, log: list):
    beginning_of_combat_triggers(state, log)

    if any(p.card.name == "District Mascot" and can_attack(p, state) and not p.saddled for p in state.battlefield):
        mascot = next(p for p in state.battlefield if p.card.name == "District Mascot")
        try_saddle(state, mascot, 1, log)
    if any(p.card.name == "Ornery Tumblewagg" and can_attack(p, state) and not p.saddled for p in state.battlefield):
        wagg = next(p for p in state.battlefield if p.card.name == "Ornery Tumblewagg")
        try_saddle(state, wagg, 2, log)

    attackers = [p for p in state.battlefield if can_attack(p, state)]
    if not attackers:
        return

    # Dyadrine: "Whenever you attack, you may remove a +1/+1 counter from
    # each of two creatures. If you do, draw a card and create a 2/2
    # Robot token." So vale a pena se sobrar >=2 criaturas com >=1
    # contador que nao ficam em 0 poder util (heuristica: so remove de
    # criaturas com 2+ contadores, nunca deixa nenhuma zerada).
    dyadrine = next((p for p in state.battlefield if p.card.name == "Dyadrine, Synthesis Amalgam"), None)
    if dyadrine is not None and dyadrine in attackers:
        donors = [p for p in state.battlefield if is_creature(p) and p.counters >= 2][:2]
        if len(donors) == 2:
            for d in donors:
                d.counters -= 1
            draw_cards(state, 1, log, source="Dyadrine, Synthesis Amalgam (ataque)")
            token = mk_perm(state, "Robot Token", is_token=True)
            state.battlefield.append(token)
            state.tokens_created += 1
            log.append("  [Dyadrine] remove 1 contador de 2 criaturas -> draw + Robot Token 2/2")

    # Urdnan: "Whenever you attack, target attacking creature with a
    # counter gains first strike (double strike if 2+ counters)." --
    # double strike dobra o dano de combate dessa criatura especifica no
    # proxy (first strike sozinho nao muda o total nesse modelo sem
    # bloqueio real).
    urdnan_bonus_uid = None
    if any(p.card.name == "Urdnan, Dromoka Warrior" for p in state.battlefield):
        countered_attackers = [p for p in attackers if p.counters >= 2]
        if countered_attackers:
            best = max(countered_attackers, key=effective_power)
            urdnan_bonus_uid = best.uid
            log.append(f"  [Urdnan] {best.card.name} ganha double strike (dobra dano proxy)")

    # The Earth King: "Whenever one or more creatures with power 4 or
    # greater attack, search for that many basic lands, tapped."
    big_attackers = [p for p in attackers if effective_power(p) >= 4]
    if big_attackers and any(p.card.name == "The Earth King" for p in state.battlefield):
        n = len(big_attackers)
        fetched = 0
        for _ in range(n):
            basics = [c for c in state.library if c in BASIC_LAND_NAMES]
            if not basics:
                break
            found = basics[0]
            state.library.remove(found)
            land_perm = mk_perm(state, found)
            land_perm.tapped = True
            enter_battlefield(state, land_perm, log, from_cast=False)
            fetched += 1
        if fetched:
            log.append(f"  [The Earth King] busca {fetched} terreno(s) basico(s) tapped (ataque poder 4+)")

    total_damage = 0
    kutzil_condition_met = False
    for p in attackers:
        p.tapped = True
        if (any(q.card.name == "Tale of Katara and Toph" for q in state.battlefield)
                and p.uid not in state.tale_katara_toph_first_tap_this_turn):
            # "Creatures you control have 'whenever this creature becomes
            # tapped for the first time during each of your turns, put a
            # +1/+1 counter on it.'" Achado real 2026-09-02: 100% ausente.
            # Implementado pro caso mais comum e valioso (atacar, aqui) --
            # outras fontes de tap (dorks pra mana, saddle, ativadas com
            # {T}) nao re-hookam este gatilho (exigiria envolver TODO
            # lugar que seta `perm.tapped = True` neste arquivo, custo
            # desproporcional pra uma unica carta -- documentado, nao
            # esquecido).
            state.tale_katara_toph_first_tap_this_turn.add(p.uid)
            place_counters(state, p, 1, log, source="Tale of Katara and Toph (1a vez tapada, ataque)")
        dmg = effective_power(p)
        if p.uid == urdnan_bonus_uid:
            dmg *= 2
        total_damage += dmg
        if is_buffed_beyond_base(p):
            kutzil_condition_met = True

        if any(q.card.name == "Sphere Grid" for q in state.battlefield):
            place_counters(state, p, 1, log, source="Sphere Grid (dano de combate)")
        if p.card.name == "Wakka, Devoted Guardian":
            place_counters(state, p, 1, log, source="Wakka, Devoted Guardian (dano de combate)")
            state.interaction_plays += 1  # destroy artifact -- sem alvo real
            state.wakka_counter_this_turn = True
        if p.counters > 0 and any(q.card.name == "Kodama of the West Tree" for q in state.battlefield):
            basics = [c for c in state.library if c in BASIC_LAND_NAMES]
            if basics:
                found = basics[0]
                state.library.remove(found)
                land_perm = mk_perm(state, found)
                land_perm.tapped = True
                enter_battlefield(state, land_perm, log, from_cast=False)
                log.append(f"  [Kodama of the West Tree] {p.card.name} modificada conecta -> busca {found} tapped")

    state.proxy_damage_total += total_damage
    if kutzil_condition_met and state.commander_in_play:
        draw_cards(state, 1, log, source="Kutzil, Malamet Exemplar (dano de combate, poder>base)")
        state.kutzil_draws_total += 1
    log.append(f"  [combate] {len(attackers)} atacante(s), {total_damage} dano proxy total")


# =========================================================
# TERRENOS
# =========================================================

def play_land(state: GameState, log: list):
    if state.lands_played_this_turn >= 1:
        return
    lands_in_hand = [n for n in state.hand if is_land_card(n) or n in MDFC_LAND_SPELLS]
    if not lands_in_hand:
        return

    def missing_score(name):
        score = 0
        for color in ("G", "W"):
            if color_sources(state, color) < 2 and color in CARD_DB[name].produces:
                score += 1
        return -score
    lands_in_hand.sort(key=missing_score)
    choice = lands_in_hand[0]
    state.hand.remove(choice)
    perm = mk_perm(state, choice)
    tapped = land_enters_tapped(state, choice)
    perm.tapped = tapped
    if tapped:
        state.tapped_land_this_turn = perm.uid
    state.battlefield.append(perm)
    state.lands_played_this_turn += 1
    log.append(f"  [land] {choice}{' (tapped)' if tapped else ''}")

    if any(p.card.name == "Field of the Dead" for p in state.battlefield):
        distinct_names = len(set(p.card.name for p in state.battlefield if is_land_card(p.card.name) or p.card.name in MDFC_LAND_SPELLS))
        if distinct_names >= 7:
            token = mk_perm(state, "Zombie Token", is_token=True)
            state.battlefield.append(token)
            state.tokens_created += 1
            log.append("  [Field of the Dead] 7+ terrenos com nomes diferentes -> Zombie Token 2/2")


def try_windswept_heath(state: GameState, log: list):
    if "Windswept Heath" not in [p.card.name for p in state.battlefield if not p.tapped]:
        return
    perm = next((p for p in state.battlefield if p.card.name == "Windswept Heath" and not p.tapped), None)
    if perm is None:
        return
    basics = [c for c in state.library if c in ("Forest", "Plains", "Snow-Covered Forest", "Snow-Covered Plains")]
    if not basics:
        return
    found = basics[0]
    state.library.remove(found)
    state.battlefield.remove(perm)
    found_perm = mk_perm(state, found)
    state.battlefield.append(found_perm)
    log.append(f"  [Windswept Heath] sacrifica, busca {found}")


# =========================================================
# HABILIDADES ATIVADAS / TERRENO
# =========================================================

def activate_abilities(state: GameState, log: list):
    # Abandoned Air Temple: "{3}{W}, {T}: Put a +1/+1 counter on each
    # creature you control." Achado real 2026-09-02: 100% ausente (afeta
    # o board inteiro, mesma classe do Gavony Township).
    air_temple = next((p for p in state.battlefield if p.card.name == "Abandoned Air Temple" and not p.tapped), None)
    if air_temple is not None and remaining_mana(state) >= 4 and color_sources(state, "W") >= 1:
        spend_mana(state, 4)
        air_temple.tapped = True
        for q in list(state.battlefield):
            if is_creature(q):
                place_counters(state, q, 1, log, source="Abandoned Air Temple")

    # Ba Sing Se: "{2}{G}, {T}: Earthbend 2. Activate only as a sorcery."
    # (target land voce controla vira criatura 0/0 com haste, +2
    # contadores, ainda e' terreno). Achado real 2026-09-02: 100% ausente.
    # Simplificacao documentada: sem o motor completo de earthbend
    # (land-vira-criatura-com-morte-retorna-tapped) usado no
    # `toph_goldfish_v1.py` -- essa e' a UNICA carta desta lista com esse
    # texto, escopo desproporcional pra construir a infraestrutura
    # inteira por 1 carta. Aproximado como: poe 2 contadores no melhor
    # alvo (Kutzil se ja em campo, senao a criatura de maior poder) --
    # ganho real de contadores preservado, so a nuance "ainda e' terreno /
    # morre-e-volta" fica de fora.
    ba_sing_se = next((p for p in state.battlefield if p.card.name == "Ba Sing Se" and not p.tapped), None)
    if ba_sing_se is not None and remaining_mana(state) >= 3 and color_sources(state, "G") >= 1:
        target = best_counter_target(state, exclude_uid=None)
        if target is not None:
            spend_mana(state, 3)
            ba_sing_se.tapped = True
            place_counters(state, target, 2, log, source="Ba Sing Se (earthbend, aproximado)")

    # Lion Sash: "{W}: Exile target card from a graveyard. If it was a
    # permanent card, put a +1/+1 counter on this permanent." Sem
    # cemiterio de oponente real -- exila do PROPRIO cemiterio (unica
    # fonte real disponivel). So vale a pena exilar a carta de MENOR mv
    # (preserva os melhores alvos de recursao pro Restoration Seminar/
    # Puca's Covenant).
    lion_sash = next((p for p in state.battlefield if p.card.name == "Lion Sash"), None)
    if lion_sash is not None and remaining_mana(state) >= 1 and state.graveyard:
        permanent_cards = [c for c in state.graveyard if CARD_DB[c].ctype in ("creature", "artifact", "enchantment", "land", "aura")]
        if permanent_cards:
            worst = min(permanent_cards, key=lambda c: CARD_DB[c].mv)
            spend_mana(state, 1)
            state.graveyard.remove(worst)
            place_counters(state, lion_sash, 1, log, source=f"Lion Sash (exila {worst} do proprio cemiterio)")

    # Mosswort Bridge: Hideaway 4 (ETB, ver apply_etb) + "{G}, {T}: You may
    # play the exiled card without paying its mana cost if creatures you
    # control have total power 10 or greater." Achado real 2026-09-02.
    bridge = next((p for p in state.battlefield if p.card.name == "Mosswort Bridge" and not p.tapped), None)
    if bridge is not None and bridge.uid in state.hideaway_cards and remaining_mana(state) >= 1 and color_sources(state, "G") >= 1:
        total_power = sum(effective_power(q) for q in state.battlefield if is_creature(q))
        if total_power >= 10:
            spend_mana(state, 1)
            bridge.tapped = True
            free_name = state.hideaway_cards.pop(bridge.uid)
            log.append(f"  [Mosswort Bridge] libera {free_name} de graca (poder total >= 10)")
            cast_free(state, free_name, log)

    # Walking Ballista: "{4}: Put a +1/+1 counter on this creature." (mana
    # sink real) + "Remove a +1/+1 counter from this creature: It deals 1
    # damage to any target." Achado real 2026-09-02: tag `ballista_ping`
    # tinha ficado orfa no primeiro rascunho. So' converte contadores em
    # dano proxy quando ha um EXCEDENTE (>=5) -- mantem o suficiente pra
    # ela continuar sendo uma ameaca real de combate/gatilho da Kutzil.
    ballista = next((p for p in state.battlefield if p.card.name == "Walking Ballista"), None)
    if ballista is not None:
        if remaining_mana(state) >= 4:
            spend_mana(state, 4)
            place_counters(state, ballista, 1, log, source="Walking Ballista ({4} ativada)")
        if ballista.counters >= 5:
            to_ping = ballista.counters - 4
            ballista.counters -= to_ping
            state.proxy_damage_total += to_ping
            log.append(f"  [Walking Ballista] remove {to_ping} contador(es), {to_ping} dano proxy")

    # Mutagen Token (Michelangelo ETB): "{1}, {T}, Sacrifice this token:
    # Put a +1/+1 counter on target creature. Activate only as a
    # sorcery." Uso unico (sacrifica-se).
    mutagen = next((p for p in state.battlefield if p.card.name == "Mutagen Token" and not p.tapped), None)
    if mutagen is not None and remaining_mana(state) >= 1:
        target = best_counter_target(state, exclude_uid=None)
        if target is not None:
            spend_mana(state, 1)
            state.battlefield.remove(mutagen)
            place_counters(state, target, 1, log, source="Mutagen Token (sacrificio)")

    # Innkeeper's Talent: sobe de nivel como sorcery, {G} pro nivel 2,
    # {3}{G} pro nivel 3 -- sempre vale a pena assim que sobrar mana,
    # ja que ambos os niveis sao estritamente bons pro motor de contador.
    talent = next((p for p in state.battlefield if p.card.name == "Innkeeper's Talent"), None)
    if talent is not None:
        if talent.level == 1 and remaining_mana(state) >= 1:
            spend_mana(state, 1)
            talent.level = 2
            log.append("  [Innkeeper's Talent] sobe pro nivel 2 (ward 1 em permanentes com contador)")
        elif talent.level == 2 and remaining_mana(state) >= 4:
            spend_mana(state, 4)
            talent.level = 3
            log.append("  [Innkeeper's Talent] sobe pro nivel 3 (dobra contadores)")

    # Ozolith, the Shattered Spire: "{1}{G}, {T}: Put a +1/+1 counter on
    # target artifact or creature you control. Activate only as a sorcery."
    ozolith = next((p for p in state.battlefield if p.card.name == "Ozolith, the Shattered Spire" and not p.tapped), None)
    if ozolith is not None and remaining_mana(state) >= 2:
        target = best_counter_target(state, exclude_uid=None)
        if target is not None:
            spend_mana(state, 2)
            ozolith.tapped = True
            place_counters(state, target, 1, log, source="Ozolith, the Shattered Spire (ativada)")

    # Rishkar mana ja contado em total_mana(); a habilidade de ETB dele ja
    # foi tratada em apply_etb.

    # Maester Seymour: "{3}{G}{G}: Monstrosity X, X = numero de contadores
    # entre criaturas que voce controla." Uso unico (so' pode ficar
    # "monstrous" 1x). So vale quando ha um X real pra ganhar.
    seymour = next((p for p in state.battlefield if p.card.name == "Maester Seymour" and not p.monstrous), None)
    if seymour is not None and remaining_mana(state) >= 5:
        x = sum(q.counters for q in state.battlefield if is_creature(q))
        if x > 0:
            spend_mana(state, 5)
            seymour.monstrous = True
            place_counters(state, seymour, x, log, source="Maester Seymour (monstrosity)")

    # Horizon Canopy: "{1}, {T}, Sacrifice: Draw a card." So' vale a pena
    # quando a mao esta baixa (< 3 cartas) -- descartar uma fonte de mana
    # permanente por 1 carta so compensa numa situacao de aperto real.
    if len(state.hand) < 3:
        canopy = next((p for p in state.battlefield if p.card.name == "Horizon Canopy" and not p.tapped), None)
        if canopy is not None and remaining_mana(state) >= 1:
            spend_mana(state, 1)
            state.battlefield.remove(canopy)
            draw_cards(state, 1, log, source="Horizon Canopy (sacrificio)")

    # War Room: "{3}, {T}, pay life = numero de cores na identidade do
    # comandante (2, G/W): Draw a card." Sempre vale (vida nunca e' um
    # recurso escasso rastreado nesse motor -- mesma premissa ja usada em
    # outros decks da sessao).
    war_room = next((p for p in state.battlefield if p.card.name == "War Room" and not p.tapped), None)
    if war_room is not None and remaining_mana(state) >= 3:
        spend_mana(state, 3)
        war_room.tapped = True
        state.life_total -= 2
        draw_cards(state, 1, log, source="War Room")

    # Gavony Township: "{2}{G}{W}, {T}: Put a +1/+1 counter on each
    # creature you control." Sempre vale (afeta o board inteiro).
    township = next((p for p in state.battlefield if p.card.name == "Gavony Township" and not p.tapped), None)
    if township is not None and remaining_mana(state) >= 4 and color_sources(state, "G") >= 1 and color_sources(state, "W") >= 1:
        spend_mana(state, 4)
        township.tapped = True
        for q in list(state.battlefield):
            if is_creature(q):
                place_counters(state, q, 1, log, source="Gavony Township")

    # The Earth Crystal: "{4}{G}{G}, {T}: Distribute two +1/+1 counters
    # among one or two target creatures you control."
    crystal = next((p for p in state.battlefield if p.card.name == "The Earth Crystal" and not p.tapped), None)
    if crystal is not None and remaining_mana(state) >= 6 and color_sources(state, "G") >= 2:
        target = best_counter_target(state, exclude_uid=None)
        if target is not None:
            spend_mana(state, 6)
            crystal.tapped = True
            place_counters(state, target, 2, log, source="The Earth Crystal (ativada)")

    # The Great Henge: "{T}: Add {G}{G}. You gain 2 life." -- mana real,
    # ja contado como land generico? NAO -- e' um artefato, precisa de
    # entrada propria em total_mana(). Simplificado: soma ao pool de bonus.
    henge = next((p for p in state.battlefield if p.card.name == "The Great Henge" and not p.tapped), None)
    if henge is not None:
        henge.tapped = True
        state.bonus_mana_pool += 2
        state.life_total += 2

    # District Mascot: "{1}{G}, remove 2 counters: Destroy target
    # artifact." Sem oponente real -- so conta como interacao quando ha
    # 2+ contadores sobrando (nao vale tirar counters uteis por nada).
    mascot = next((p for p in state.battlefield if p.card.name == "District Mascot" and p.counters >= 4), None)
    if mascot is not None and remaining_mana(state) >= 2:
        spend_mana(state, 2)
        mascot.counters -= 2
        state.interaction_plays += 1

    # Hopeful Initiate: "{2}{W}, remove 2 counters from among creatures
    # you control: Destroy target artifact or enchantment." Mesma logica.
    initiate = next((p for p in state.battlefield if p.card.name == "Hopeful Initiate"), None)
    total_counters_pool = sum(q.counters for q in state.battlefield if is_creature(q))
    if initiate is not None and remaining_mana(state) >= 3 and total_counters_pool >= 4:
        spend_mana(state, 3)
        removed = 0
        for q in state.battlefield:
            if removed >= 2:
                break
            take = min(2 - removed, q.counters)
            q.counters -= take
            removed += take
        state.interaction_plays += 1

    # Lion Sash: "{W}: Exile target card from a graveyard. If it was a
    # permanent card, put a +1/+1 counter on this permanent." Sem
    # cemiterio de oponente real -- so' o proprio (nao vale exilar o
    # proprio cemiterio, perderia recursao). 📊, nao ativado.

    # Collector's Cage: "{1}, {T}: Put a +1/+1 counter on target creature.
    # Then if you control 3+ creatures with different powers, you may
    # play the exiled card for free."
    cage = next((p for p in state.battlefield if p.card.name == "Collector's Cage" and not p.tapped), None)
    if cage is not None and remaining_mana(state) >= 1:
        target = best_counter_target(state, exclude_uid=None)
        if target is not None:
            spend_mana(state, 1)
            cage.tapped = True
            place_counters(state, target, 1, log, source="Collector's Cage (ativada)")
            powers = set(effective_power(q) for q in state.battlefield if is_creature(q))
            if len(powers) >= 3 and cage.uid in state.hideaway_cards:
                free_name = state.hideaway_cards.pop(cage.uid)
                log.append(f"  [Collector's Cage] libera {free_name} de graca (3+ criaturas com poderes diferentes)")
                cast_free(state, free_name, log)


# =========================================================
# PLOT (Railway Brawler)
# =========================================================

def try_plot_railway_brawler(state: GameState, log: list):
    """Plot {3}{G}: paga agora, exila da mao; conjuravel de graca como
    sorcery num turno POSTERIOR (nao no mesmo turno que plotou -- regra
    real). Vale a pena porque o custo de Plot (4 mana) e' MENOR que o
    hardcast ({3}{G}{G}=5) -- distribui o custo em 2 turnos."""
    if "Railway Brawler" not in state.hand:
        return
    if remaining_mana(state) < 4:
        return
    state.hand.remove("Railway Brawler")
    spend_mana(state, 4)
    state.plot_exile[state.turn] = state.plot_exile.get(state.turn, []) + ["Railway Brawler"]
    log.append("  [Plot] Railway Brawler exilada por {3}{G}, conjuravel de graca num turno futuro")


def resolve_plotted_cards(state: GameState, log: list):
    for plotted_turn, names in list(state.plot_exile.items()):
        if plotted_turn >= state.turn:
            continue
        for name in names:
            on_spell_cast(state, name, log)
            state.warp_plot_free_casts_total += 1
            log.append(f"  [Plot] conjura {name} de graca (plotada no turno {plotted_turn})")
            resolve_permanent(state, name, log)
        del state.plot_exile[plotted_turn]


# =========================================================
# HEURISTICAS DE PRIORIDADE / GATES
# =========================================================

def cast_priority(state: GameState, name: str) -> tuple:
    if has_tag(name, "dork_flat1_g") or has_tag(name, "dork_flat1_w") or has_tag(name, "dork_flatX"):
        return (0, effective_cost(state, name))
    if name == COMMANDER:
        return (1, 0)
    if is_creature_card(name):
        return (2, effective_cost(state, name))
    return (3, effective_cost(state, name))


def should_cast_damning_verdict(state: GameState) -> bool:
    """'Destroy all creatures with no counters on them' -- so vale a pena
    se a perda propria for pequena (poucas criaturas sem contador) E
    houver de fato algo pra destruir (nao gasta a carta a toa)."""
    creatures = [p for p in state.battlefield if is_creature(p)]
    if not creatures:
        return False
    no_counter = [p for p in creatures if p.counters == 0]
    if not no_counter:
        return False
    return len(no_counter) <= 2 and len(no_counter) < len(creatures)


# =========================================================
# FASE PRINCIPAL / TURNO
# =========================================================

def main_phase(state: GameState, log: list):
    if not state.commander_in_play and can_cast(state, COMMANDER):
        cast_card(state, COMMANDER, log)

    try_windswept_heath(state, log)
    resolve_plotted_cards(state, log)

    while True:
        castables = [n for n in state.hand if not is_land_card(n) and can_cast(state, n)]
        castables = [n for n in castables if n != "Damning Verdict" or should_cast_damning_verdict(state)]
        if not castables:
            break
        castables.sort(key=lambda n: cast_priority(state, n))
        cast_card(state, castables[0], log)

    try_plot_railway_brawler(state, log)
    activate_abilities(state, log)


def upkeep_draw_step(state: GameState, log: list, is_first_turn: bool, on_play: bool):
    fenrir = next((p for p in state.battlefield if p.card.name == "Summon: Fenrir"), None)
    draw_this_turn = not (is_first_turn and on_play)
    if draw_this_turn:
        draw_cards(state, 1, log, source="draw normal")
    if fenrir is not None and fenrir.saga_chapter < 3:
        fenrir.saga_chapter += 1
        do_saga_fenrir_chapter(state, fenrir, log)


def end_step(state: GameState, log: list):
    if state.wakka_counter_this_turn:
        wakka = next((p for p in state.battlefield if p.card.name == "Wakka, Devoted Guardian"), None)
        if wakka is not None:
            for q in list(state.battlefield):
                if is_creature(q) and q.uid != wakka.uid:
                    place_counters(state, q, 1, log, source="Wakka, Devoted Guardian (Blitzball Captain)")


def cleanup_turn(state: GameState):
    for p in state.battlefield:
        p.temp_power = 0
        p.temp_trample = False
        if p.card.name in ("District Mascot", "Ornery Tumblewagg"):
            p.saddled = False
    state.mana_spent_this_turn = 0
    state.bonus_mana_pool = 0
    state.tapped_land_this_turn = None
    state.lands_played_this_turn = 0
    state.mikey_leo_drawn_this_turn = False
    state.terrasymbiosis_drawn_this_turn = False
    state.generous_pup_triggered_this_turn = False
    state.botanical_brawler_first_counter_this_turn = set()
    state.wakka_counter_this_turn = False
    state.pucas_covenant_triggered_this_turn = False
    state.tale_katara_toph_first_tap_this_turn = set()
    for p in state.battlefield:
        p.tapped = False


def play_turn(state: GameState, is_first_turn: bool, on_play: bool):
    state.turn += 1
    log = []
    upkeep_draw_step(state, log, is_first_turn, on_play)
    play_land(state, log)
    main_phase(state, log)
    combat_step(state, log)
    end_step(state, log)
    cleanup_turn(state)
    return log


# =========================================================
# DECKLIST (fonte: lista.md)
# =========================================================

DECKLIST_TEXT = """
1 Abandoned Air Temple
1 Agent Bishop, Man in Black
1 Akroma's Will
1 Avacyn's Pilgrim
1 Ba Sing Se
1 Beast Whisperer
1 Biophagus
1 Birds of Paradise
1 Botanical Brawler
1 Boseiju, Who Endures
1 Bountiful Promenade
1 Branching Evolution
1 Branchloft Pathway // Boulderloft Pathway
1 Bridgeworks Battle // Tanglespan Bridgeworks
1 Broodguard Elite
1 Brushland
1 Canopy Vista
1 Champion of Lambholt
1 Clever Concealment
1 Collector's Cage
1 Command Tower
1 Craterhoof Behemoth
1 Damning Verdict
1 Dauntless Escort
1 Delighted Halfling
1 District Mascot
1 Duskshell Crawler
1 Dyadrine, Synthesis Amalgam
1 Eiganjo, Seat of the Empire
1 Esper Sentinel
1 Exotic Orchard
1 Field of the Dead
3 Forest
1 Fortified Village
1 Fyndhorn Elves
1 Galadriel's Dismissal
1 Gavony Township
1 Generous Pup
1 Goldvein Hydra
1 Hardened Scales
1 Horizon Canopy
1 Hopeful Initiate
1 Hushwood Verge
1 Innkeeper's Talent
1 Kabira Takedown // Kabira Plateau
1 Knight of Autumn
1 Kodama of the West Tree
1 Lion Sash
1 Llanowar Elves
1 Luminarch Aspirant
1 Maester Seymour
1 Managorger Hydra
1 Metastatic Evangel
1 Michelangelo, Weirdness to 11
1 Mikey & Leo, Chaos & Order
1 Mother of Runes
1 Mosswort Bridge
1 Ornery Tumblewagg
1 Ouroboroid
1 Overgrown Farmland
1 Ozolith, the Shattered Spire
1 Path to Exile
2 Plains
1 Puca's Covenant
1 Railway Brawler
1 Rancor
1 Requisition Raid
1 Restoration Seminar
1 Rishkar, Peema Renegade
1 Selvala, Heart of the Wilds
2 Snow-Covered Forest
2 Snow-Covered Plains
1 Sol Ring
1 Sphere Grid
1 Stonecoil Serpent
1 Summon: Fenrir
1 Sunpetal Grove
1 Swiftfoot Boots
1 Swords to Plowshares
1 Tale of Katara and Toph
1 Teferi's Protection
1 Temple Garden
1 Terrasymbiosis
1 The Earth Crystal
1 The Earth King
1 The Great Henge
1 The Ozolith
1 Training Regimen
1 Urdnan, Dromoka Warrior
1 Walking Ballista
1 Wakka, Devoted Guardian
1 War Room
1 Windswept Heath
1 Witch Enchanter // Witch-Blessed Meadow
"""


def parse_decklist(text: str) -> list:
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


BASE_LIBRARY = parse_decklist(DECKLIST_TEXT)
assert len(BASE_LIBRARY) == 99, f"esperava 99 cartas de biblioteca (+ comandante = 100), achei {len(BASE_LIBRARY)}"


# =========================================================
# MULLIGAN
# =========================================================

KEEPERS = {"Avacyn's Pilgrim", "Birds of Paradise", "Fyndhorn Elves", "Llanowar Elves",
           "Delighted Halfling", "Biophagus", "Sol Ring"}


def should_keep(hand: list) -> bool:
    lands = sum(1 for c in hand if is_land_card(c) or c in MDFC_LAND_SPELLS)
    keepers = sum(1 for c in hand if c in KEEPERS)
    if lands < 2 or lands > 5:
        return False
    if keepers >= 1:
        return True
    return lands >= 3


def bottom_priority(card: str) -> tuple:
    if is_land_card(card) or card in MDFC_LAND_SPELLS:
        return (3, 0)
    if card in KEEPERS:
        return (0, CARD_DB[card].mv)
    if card == "Craterhoof Behemoth" or CARD_DB[card].mv >= 7:
        return (4, -CARD_DB[card].mv)
    return (2, CARD_DB[card].mv)


def mulligan(rng: random.Random):
    max_mulls = 3
    mulls = 0
    while True:
        lib = list(BASE_LIBRARY)
        rng.shuffle(lib)
        hand = lib[:7]
        lib = lib[7:]
        if should_keep(hand) or mulls >= max_mulls:
            if mulls > 0:
                # London mulligan: compra 7, devolve `mulls` cartas ao
                # fundo da biblioteca (as de menor prioridade primeiro).
                ordered = sorted(hand, key=bottom_priority, reverse=True)
                bottom = ordered[:mulls]
                hand = ordered[mulls:]
                lib = lib + bottom
            return hand, lib, mulls
        mulls += 1


# =========================================================
# SIMULATION
# =========================================================

def simulate_one(seed: int, turns: int = 8) -> GameState:
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
    print(f"Turno medio de conjuracao da Kutzil: {avg(cmd_turn):.2f} | mediana: {statistics.median(cmd_turn) if cmd_turn else float('nan'):.1f}")
    print(f"Nunca conjurada em {turns} turnos: {100*sum(1 for s in states if s.commander_cast_turn is None)/n:.1f}%")
    print(f"Avg dano proxy total de combate: {avg([s.proxy_damage_total for s in states]):.2f}")
    print(f"Avg compras via Kutzil (poder>base em combate): {avg([s.kutzil_draws_total for s in states]):.2f}")
    print(f"Avg contadores +1/+1 colocados no total (com multiplicadores): {avg([s.counters_placed_total for s in states]):.2f}")
    print(f"Avg cartas compradas extra (todos os motores): {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"Avg tokens criados: {avg([s.tokens_created for s in states]):.2f}")
    print(f"Avg pecas de rampa em campo: {avg([s.ramp_pieces_in_play for s in states]):.2f}")
    print(f"Avg spells de interacao conjurados (proxy, sem alvo real): {avg([s.interaction_plays for s in states]):.2f}")
    print(f"Damning Verdict conjurada em {100*sum(1 for s in states if s.damning_verdict_cast_total>0)/n:.1f}% dos jogos")
    print(f"Avg ativacoes de saddle: {avg([s.saddle_activations_total for s in states]):.2f}")
    print(f"Avg Plot->free cast (Railway Brawler): {avg([s.warp_plot_free_casts_total for s in states]):.2f}")
    print(f"Craterhoof Behemoth resolvido em {100*sum(1 for s in states if s.craterhoof_cast)/n:.1f}% dos jogos")
    finisher_turns = [s.first_finisher_turn for s in states if s.first_finisher_turn is not None]
    if finisher_turns:
        print(f"Avg turno do 1o finisher: {avg(finisher_turns):.2f}")
    print(f"Avg eventos de recursao: {avg([s.recursion_events_total for s in states]):.2f}")
    print(f"Avg vida final: {avg([s.life_total for s in states]):.2f}")
    print(f"Avg mao final: {avg([len(s.hand) for s in states]):.2f}")
    print(f"Avg battlefield final: {avg([len(s.battlefield) for s in states]):.2f}")

    print("--- Metricas basicas (checklist obrigatorio) ---")
    print(f"RAMP: avg pecas de rampa em campo: {avg([s.ramp_pieces_in_play for s in states]):.2f}")
    print(f"DRAW: avg compras extras totais: {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"INTERACTION: avg spells de interacao conjurados: {avg([s.interaction_plays for s in states]):.2f}")
    print(f"RECURSION: avg eventos de recursao (Restoration Seminar, Rancor voltando pra mao): {avg([s.recursion_events_total for s in states]):.2f}")
    print(f"FINISHER/LETHALITY: dano proxy total {avg([s.proxy_damage_total for s in states]):.2f}, Craterhoof em {100*sum(1 for s in states if s.craterhoof_cast)/n:.1f}% dos jogos")

    return states


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    states = run_batch(n=3000, seed_base=1000000, turns=8)

    with open("kutzil_v1_runs.jsonl", "w") as f:
        for s in states:
            f.write(json.dumps({
                "mulligans": s.mulligans,
                "commander_cast_turn": s.commander_cast_turn,
                "proxy_damage_total": s.proxy_damage_total,
                "kutzil_draws_total": s.kutzil_draws_total,
                "counters_placed_total": s.counters_placed_total,
                "cards_drawn_extra": s.cards_drawn_extra,
                "tokens_created": s.tokens_created,
                "interaction_plays": s.interaction_plays,
                "damning_verdict_cast_total": s.damning_verdict_cast_total,
                "saddle_activations_total": s.saddle_activations_total,
                "warp_plot_free_casts_total": s.warp_plot_free_casts_total,
                "craterhoof_cast": s.craterhoof_cast,
                "first_finisher_turn": s.first_finisher_turn,
                "recursion_events_total": s.recursion_events_total,
                "life_total": s.life_total,
            }) + "\n")
