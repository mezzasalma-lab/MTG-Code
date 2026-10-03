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
# Achado real 2026-09-14 (leitura clausula-a-clausula, ronda final da
# campanha): "Flying, haste" no oraculo real (Scryfall) - tag "haste"
# faltava, o Dragon nao conseguia atacar/disparar seu proprio gatilho de
# Treasure no turno em que entrava em campo.
add("Goldspan Dragon", 5, "creature", {"goldspan", "treasure_attack", "haste"})
# Achado real 2026-09-14: tipo real "Human Pirate" (Scryfall) - Pirate e'
# um outlaw type (OUTLAW_TYPES), mas a tag "outlaw" nunca tinha sido
# aplicada aqui. Afeta Back in Town (alvo em pilha), o gatilho da Olivia
# ("um ou mais outlaws causam dano"), o X do Laughing Jasper Flint e o
# novo anthem de haste do Vihaan (ver combat_step).
add("Captain Lannery Storm", 3, "creature", {"treasure_attack", "haste", "outlaw"})
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
# Achado real 2026-09-14: "Halfling Rogue" - Rogue e' outlaw type, tag
# faltava.
add("Lotho, Corrupt Shirriff", 2, "creature", {"second_spell_treasure", "outlaw"})
# Achado real 2026-09-14: "Dwarf Berserker" (Scryfall) - Berserker NAO
# e' outlaw type. Tag "outlaw" estava presente por engano (mesma classe
# de bug de Jan Jansen acima).
add("Magda, the Hoardmaster", 2, "creature", {"crime_treasure"})
add("Mahadi, Emporium Master", 3, "creature", {"treasure_death_batch"})
add("Olivia, Opulent Outlaw", 4, "creature", {"outlaw_combat_treasure", "outlaw"})
add("Orochi Soul-Reaver", 4, "creature", {"combat_treasure_manifest", "outlaw"})
# Achado real 2026-09-14: "Human Pirate" - Pirate e' outlaw type, tag
# faltava (mesma classe de bug do Captain Lannery Storm acima).
add("Pitiless Plunderer", 4, "creature", {"creature_death_treasure", "outlaw"})
add("Professional Face-Breaker", 3, "creature", {"combat_treasure", "impulse_treasure_sac"})
add("Prosper, Tome-Bound", 4, "creature", {"impulse_end_step", "play_exile_treasure", "outlaw"})
add("Revel in Riches", 5, "enchantment", {"opponent_dependent", "alt_win"})
add("The Reaver Cleaver", 3, "artifact", {"equipment_combat_treasure"})
add("Gleaming Splendor", 2, "enchantment", {"opponent_dependent"})  # trocada por Rakdos Signet
add("Smaug the Magnificent", 4, "creature", {"upkeep_treasure", "treasure_attack_damage", "haste"})  # trocada por Insatiable Avarice

# --- Aristocratas / drain -----------------------------------------------------
# Achado real 2026-09-14: "Human Rogue Ally" - Rogue e' outlaw type, tag
# faltava.
add("Zulaport Cutthroat", 2, "creature", {"creature_death_drain", "outlaw"})
add("Nadier's Nightblade", 3, "creature", {"token_leave_drain"})
add("Mirkwood Bats", 4, "creature", {"token_create_or_sac_drain"})
add("Kambal, Profiteering Mayor", 3, "creature", {"token_etb_drain"})
add("Agent of the Iron Throne", 3, "enchantment", {"death_drain_background"})
add("Dictate of Erebos", 5, "enchantment", {"death_edict_unused"})
add("Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel", 3, "creature", {"death_drain_transform", "sac_draw"})
# Achado real 2026-09-14: "Human Warlock" - Warlock e' outlaw type, tag
# faltava.
add("Witch of the Moors", 5, "creature", {"lifegain_recursion", "outlaw"})
add("Marionette Master", 6, "creature", {"artifact_death_drain", "fabricate3"})
add("Mayhem Devil", 3, "creature", {"sac_damage"})
add("Life Insurance", 5, "enchantment", {"nontoken_death_treasure", "extort"})
# Achado real 2026-09-14: "Vampire Assassin" - Assassin e' outlaw type,
# tag faltava.
add("Mari, the Killing Quill", 3, "creature", {"opponent_dependent", "outlaw"})

# --- Sac outlets ---------------------------------------------------------
add("Ashnod's Altar", 3, "artifact", {"sac_outlet_cc"})
add("Krark-Clan Ironworks", 4, "artifact", {"sac_outlet_artifact_cc"})
# Achado real 2026-09-14: tipo real "Gnome Artificer" (Scryfall) -
# Artificer NAO e' outlaw type (OUTLAW_TYPES = Assassin/Mercenary/
# Pirate/Rogue/Warlock) - tag "outlaw" estava presente por engano,
# fazendo Jan Jansen contar erroneamente pro X do Laughing Jasper
# Flint, pro gatilho da Olivia e pro anthem de haste do Vihaan. Ao
# mesmo tempo faltava a tag "haste" real dela ("Haste" no oraculo,
# primeira linha) - sem ela Jan Jansen nao conseguia usar nenhuma das
# 2 habilidades de {T} no turno em que entrava.
add("Jan Jansen, Chaos Crafter", 3, "creature", {"jan_jansen", "haste"})

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
# Achado real 2026-09-14: mv=6 estava ERRADO - custo real (Scryfall) e'
# {X}{2}{B}, cmc=3 (X conta 0 pra CMC, regra padrao). O custo fixo real
# e' so' {2}{B}=3, nao 6 - ver resolve_instant_sorcery pro X pago de
# verdade (era tratado como gratis, capado arbitrariamente em 2).
add("Back in Town", 3, "sorcery", {"recursion_x"})
add("Lich-Knights' Conquest", 5, "sorcery", {"recursion_sac"})
add("Grenzo, Havoc Raiser", 2, "creature", {"combat_impulse", "outlaw"})
add("Laughing Jasper Flint", 3, "creature", {"upkeep_impulse", "outlaw"})

# --- Combate / anthem / outros ---------------------------------------------
add("Aya of Alexandria", 4, "creature", {"historic_combat_token", "outlaw"})
# Achado real 2026-09-14: primeira linha do oraculo real e' "Haste" -
# tag faltava, impedindo o Battalion (ja implementado em combat_step)
# de disparar no turno em que ela entrava em campo.
add("Sentinel Sarah Lyons", 5, "creature", {"anthem_artifact", "haste"})
add("Shared Animosity", 3, "enchantment", {"anthem_tribal"})
add("Urabrask's Forge", 3, "artifact", {"forge_token"})
# Achado real 2026-09-14: tipo real "Tiefling Rogue" (Scryfall) - Rogue
# e' outlaw type, tag faltava.
add("Grim Hireling", 4, "creature", {"combat_treasure2", "sac_debuff_unused", "outlaw"})

# --- Candidata de Reality Fracture (so' via swap, NAO esta na lista) -------
# Draconic Visitor (FRA #80, lanca 2026-10-02; oraculo ao vivo Scryfall
# 2026-09-25, salvo no oracle-cache): "{3}{R}{R}, Creature — Dragon 5/5.
# Flying. If one or more artifact tokens would be created under your
# control, that many 5/5 red Dragon creature tokens with flying are created
# instead." Dragon nao e' outlaw (sem haste do Vihaan). Ver
# `create_treasures`/`create_constructs`/`check_visitor_combo`.
add("Draconic Visitor", 5, "creature", {"draconic_visitor"})

# Poder impresso real (Scryfall, oracle-cache 2026-09-25) de cada criatura --
# usado so' pela metrica nova de dano de combate (proxy, sem bloqueio).
CREATURE_POWER = {
    "Vihaan, Goldwaker": 3, "Academy Manufactor": 1, "Xorn": 3, "Goldspan Dragon": 4,
    "Captain Lannery Storm": 2, "Kellogg, Dangerous Mind": 3, "Lotho, Corrupt Shirriff": 2,
    "Magda, the Hoardmaster": 2, "Mahadi, Emporium Master": 3, "Olivia, Opulent Outlaw": 3,
    "Orochi Soul-Reaver": 5, "Pitiless Plunderer": 1, "Professional Face-Breaker": 2,
    "Prosper, Tome-Bound": 1, "Smaug the Magnificent": 4, "Zulaport Cutthroat": 1,
    "Nadier's Nightblade": 1, "Mirkwood Bats": 2, "Kambal, Profiteering Mayor": 2,
    "Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel": 3, "Witch of the Moors": 4,
    "Marionette Master": 1, "Mayhem Devil": 3, "Mari, the Killing Quill": 3,
    "Jan Jansen, Chaos Crafter": 3, "Grenzo, Havoc Raiser": 2, "Laughing Jasper Flint": 4,
    "Aya of Alexandria": 4, "Sentinel Sarah Lyons": 4, "Grim Hireling": 3, "Draconic Visitor": 5,
}
OTHER_TOKEN_POWER = 2  # 📝 media das fichas genericas (Shapeshifter 3/2, manifesto 2/2, Assassin 1/1...) -- o motor so' guarda contagem
LETHAL_PROXY = 120     # 3 oponentes x 40 de vida -- premissa da metrica limitada, nao vida real

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
    black_market_connections_triggered_this_turn: bool = False
    life_gained_this_turn: int = 0
    face_breaker_used_this_turn: bool = False
    forge_tokens_this_turn: int = 0  # quantos tokens do Urabrask's Forge nasceram este turno (p/ sac exato no end_step)
    reaver_cleaver_equipped: bool = False
    reaver_cleaver_host: Optional[str] = None  # criatura equipada (2026-09-25: "that many" = poder dela)
    reaver_cleaver_treasures_total: int = 0

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
    table_damage_total: int = 0  # vida total da mesa (each opponent x NUM_OPPONENTS) -- so' pra win_turn
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
    magda_dragons_created_total: int = 0
    face_breaker_impulse_total: int = 0
    extort_paid_total: int = 0
    sevinne_flashback_total: int = 0

    # Modo de resiliencia (interacao de oponente) — 2026-09-21, porte do
    # Megatron/Ur-Dragon/Hei Bai/Edgar Markov/Ulalek/Toph/Prismatic
    # Bridge/Maralen/Rat King Verminister. `interaction_rng` None =
    # modo padrao, totalmente inerte (bit-identico ao motor sem estas
    # categorias).
    interaction_rng: Optional[random.Random] = None
    wiped_this_round: bool = False
    graveyard_wipe_used: bool = False

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

    # ---- Rodada Draconic Visitor (2026-09-25) ----
    dragons: int = 0                     # fichas 5/5 voadoras da Draconic Visitor (candidata)
    dragons_sick: int = 0
    dragons_created_total: int = 0
    visitor_replaced_artifact_tokens: int = 0
    visitor_combo_turn: Optional[int] = None   # Visitor + Pitiless Plunderer + Ashnod's Altar juntos em campo
    combat_damage_proxy_total: int = 0
    artifact_entered_this_turn: bool = False   # Sentinel Sarah Lyons (+2/+2)
    win_turn: Optional[int] = None             # 1o turno de vitoria (proxy): dano >= 120, Revel in Riches ou combo


def draw_cards(state: GameState, n: int):
    for _ in range(n):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1


def gain_life(state: GameState, n: int):
    state.life += n
    state.life_gained_total += n
    state.life_gained_this_turn += n


def drain(state: GameState, n: int, each_opp: bool = False):
    """Dano/drena agregado — proxy, nunca vida real de oponente.
    `drain_damage_total` segue a convencao historica do arquivo (1 por
    gatilho, seja "each opponent" ou "target"). `table_damage_total` (novo
    2026-09-25, so' pra metrica limitada `win_turn`) pesa pelo alcance real:
    "each opponent loses N" = N x NUM_OPPONENTS de vida total da mesa;
    "target opponent"/"any target" = N."""
    state.drain_damage_total += n
    state.table_damage_total += n * (NUM_OPPONENTS if each_opp else 1)


# ---------------------------------------------------------------------------
# Type helpers
# ---------------------------------------------------------------------------

def is_artifact_card(name: str) -> bool:
    return CARD_DB[name].ctype in ARTIFACT_ISH


def is_creature_card(name: str) -> bool:
    return CARD_DB[name].ctype in CREATURE_ISH


def is_enchantment_card(name: str) -> bool:
    return CARD_DB[name].ctype == "enchantment"


def is_outlaw(name: str) -> bool:
    return "outlaw" in CARD_DB[name].tags


def artifacts_in_play(state: GameState) -> int:
    """Contagem real de artefatos que o jogador controla -- inclui
    permanentes nomeados de tipo artifact/artifact_creature, Treasures
    (tokens de artefato) e Constructs (tokens de artefato-criatura via
    Jan Jansen)."""
    n = sum(1 for c in state.battlefield if is_artifact_card(c))
    n += state.treasures
    n += state.constructs
    return n


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
    if "Draconic Visitor" in state.battlefield:
        # Draconic Visitor: "If one or more artifact tokens would be created
        # under your control, that many 5/5 red Dragon creature tokens with
        # flying are created instead." O controlador escolhe a ordem dos
        # efeitos de substituicao (CR 616.1): Xorn (+1) e Anointed (x2)
        # antes, Academy Manufactor (cada Treasure vira Clue+Food+Treasure =
        # 3 fichas de artefato) e so' entao a Visitor -- ordem que maximiza
        # Dragoes. Nenhum Treasure/Clue/Food chega a existir.
        n_art = total * (3 if "Academy Manufactor" in state.battlefield else 1)
        _create_visitor_dragons(state, n_art)
        return
    state.treasures += total
    state.treasures_created_total += total
    state.artifact_entered_this_turn = True

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
    if "Draconic Visitor" in state.battlefield:
        # Construct/Servo sao "artifact creature" -- ficha de artefato, vira Dragao.
        _create_visitor_dragons(state, total)
        return
    state.constructs += total
    state.constructs_sick += total
    state.constructs_created_total += total
    state.artifact_entered_this_turn = True
    on_tokens_created(state, total, kind="construct")


def _create_visitor_dragons(state: GameState, n: int):
    """Fichas 5/5 voadoras da Draconic Visitor (o dobro da Anointed ja' foi
    aplicado no evento original). Sao fichas de criatura: Kambal, Mirkwood
    Bats e Caretaker's Talent reagem. Nao sao artefato."""
    if n <= 0:
        return
    state.dragons += n
    state.dragons_sick += n
    state.dragons_created_total += n
    state.visitor_replaced_artifact_tokens += n
    on_tokens_created(state, n, kind="creature")


def create_other_tokens(state: GameState, n: int, source: str = "", haste: bool = False):
    """`haste=True`: achado real 2026-09-14 (Urabrask's Forge/Magda's
    Scorpion Dragon token, ambos com "haste" impresso de verdade) - sem
    isso o token nascia sempre com doenca de invocacao, mesmo tendo
    haste real, e nunca conseguia atacar no turno em que era criado."""
    if n <= 0:
        return 0
    total = n * (2 if "Anointed Procession" in state.battlefield else 1)
    state.other_tokens += total
    if not haste:
        state.other_tokens_sick += total
    state.other_tokens_created_total += total
    on_tokens_created(state, total, kind="creature")
    return total


def on_tokens_created(state: GameState, n: int, kind: str):
    if n <= 0:
        return
    if "Mirkwood Bats" in state.battlefield:
        drain(state, n, each_opp=True)
    # Kambal, Profiteering Mayor -- 2a habilidade: "Whenever one or more
    # tokens you control enter, each opponent loses 1 life and you gain 1
    # life." CORRIGIDO 2026-09-25: o codigo limitava a 1x/turno, mas o
    # "This ability triggers only once each turn" do oraculo pertence a 1a
    # habilidade (copiar fichas de OPONENTE), nao a esta. drain() segue a
    # convencao do arquivo (1 por gatilho, igual Zulaport/Mirkwood Bats).
    if kind != "treasure_component" and "Kambal, Profiteering Mayor" in state.battlefield:
        drain(state, 1, each_opp=True)
        gain_life(state, 1)
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
    """CORRIGIDO 2026-09-21 (achado real durante a validacao do porte do
    modo de resiliencia, 20k regressao -- nao e' bug de OPONENTE, e' o
    proprio motor do deck: `resolve_instant_sorcery`'s fallback do
    Deadly Dispute podia escolher o comandante como sacrificio quando
    nenhum Treasure/Construct/token generico sobrava, e esta funcao
    NUNCA tratava o caso -- ela ficava presa no cemiterio pra sempre,
    `commander_in_play` travado em True, achado em ~1.6% das seeds).
    Comandante sacrificada passa pelo cemiterio de verdade (CR 903.9a e'
    acao baseada em estado -- CR 704 -- nao substituicao: ela vai pro
    cemiterio DE VERDADE primeiro, disparando `on_creature_dies`
    normalmente -- Zulaport/Pitiless Plunderer/Agent of the Iron
    Throne/Sephiroth/Life Insurance, e Mayhem Devil TAMBEM dispara aqui,
    ja' que 'you sacrifice' e' literalmente o que este evento e' --
    diferente do `remove_permanent` de oponente, que exclui Mayhem
    Devil), so' DEPOIS e' removida de la' pra representar a escolha do
    dono de move-la pra zona de comando."""
    if name not in state.battlefield:
        return False
    state.battlefield.remove(name)
    state.creature_cast_turn.pop(name, None)
    state.graveyard.append(name)
    on_permanent_sacrificed(state, 1, is_artifact=is_artifact_card(name), is_creature=True, is_token=False)
    if name == COMMANDER:
        if name in state.graveyard:
            state.graveyard.remove(name)
        state.commander_in_play = False
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


def on_permanent_destroyed(state: GameState, n: int, is_artifact: bool, is_creature: bool, is_token: bool):
    """Porte do modo de resiliencia (2026-09-21): mesmos gatilhos reais de
    'dies'/'put into a graveyard from the battlefield' que `on_permanent_
    sacrificed` dispara, MENOS Mayhem Devil -- oraculo real e' 'Whenever
    YOU SACRIFICE...', e destruicao/wipe por acao de OPONENTE nunca e'
    sacrificio feito por mim (mesma distincao ja aplicada ao Vito
    Fanatic no Edgar Markov e ao Vito-style de outros decks desta
    sessao). Zulaport/Pitiless Plunderer/Agent of the Iron Throne/
    Sephiroth/Nadier's Nightblade/Marionette Master/Mirkwood Bats/Life
    Insurance (dentro de on_creature_dies/on_artifact_dies/
    on_token_leaves) reagem normalmente -- nenhum deles e' 'sacrifice'-
    restrito no oraculo real."""
    if is_creature:
        on_creature_dies(state, n, is_token=is_token)
    if is_artifact:
        on_artifact_dies(state, n)
    if is_token:
        on_token_leaves(state, n)


def remove_permanent(state: GameState, name: str, source: str = "opponent"):
    """Ponto central de remocao de permanente NOMEADO do campo por acao de
    OPONENTE (wipe/remocao do modo de resiliencia, 2026-09-21 -- porte do
    Megatron/Ur-Dragon/Hei Bai/Edgar Markov/Ulalek/Toph/Prismatic
    Bridge/Maralen/Rat King Verminister, ja' incorporando desde o inicio
    a correcao de CR 903.9a validada nesta sessao -- nunca implementado
    do jeito errado aqui pra depois precisar de retrofit).

    Comandante: CR 903.9a (cemiterio/exilio, o caso de MORTE) e' ACAO
    BASEADA EM ESTADO (CR 704), NAO substituicao -- ver
    `rules-cache/comprehensive-rules.txt` linhas 6888-6896, Regra 18 de
    `references/user-standing-rules.md`. Vihaan vai pro cemiterio DE
    VERDADE primeiro (CR 700.4, 'dies'), disparando `on_creature_dies`
    normalmente (Zulaport/Pitiless Plunderer/Agent of the Iron
    Throne/Sephiroth/Life Insurance -- nenhum deles e' ele mesmo; ele
    NUNCA e' artefato, so' creature+outlaw, entao `on_artifact_dies`
    nunca dispara pra ele), so' DEPOIS e' removido de la' pra
    representar a escolha do dono de move-lo pra zona de comando
    (`commander_in_play = False`). Mayhem Devil fica de fora (via
    `on_permanent_destroyed`, nao `on_permanent_sacrificed`) -- oraculo
    real e' sacrifice-only, nunca destruicao/wipe de oponente.

    Token agregado (Treasure/Construct/other_tokens) nao passa por
    aqui -- os contadores sao zerados diretamente por
    `try_smart_opponent_wipe`, que tambem chama `on_permanent_destroyed`
    pra eles. Esta funcao e' so' pra permanente NOMEADO (entrada real em
    `state.battlefield`)."""
    if name not in state.battlefield:
        return
    state.battlefield.remove(name)
    state.creature_cast_turn.pop(name, None)
    is_art = is_artifact_card(name)
    is_creat = is_creature_card(name)
    state.graveyard.append(name)
    on_permanent_destroyed(state, 1, is_artifact=is_art, is_creature=is_creat, is_token=False)
    if name == COMMANDER:
        if name in state.graveyard:
            state.graveyard.remove(name)
        state.commander_in_play = False


def on_creature_dies(state: GameState, n: int, is_token: bool):
    if n <= 0:
        return
    state.creature_deaths_total += n
    state.deaths_this_turn += n
    # Achado real 2026-09-14: oraculo real da Agent of the Iron Throne
    # (Background) e' "Commander creatures you own have 'Whenever an
    # ARTIFACT OR CREATURE you control is put into a graveyard from the
    # battlefield, each opponent loses 1 life.'" - so' a metade artefato
    # estava coberta (on_artifact_dies); a metade CRIATURA (provavelmente
    # a mais comum das duas neste deck aristocrata) nunca disparava. A
    # habilidade e' concedida ao proprio Vihaan (a unica criatura-
    # comandante deste deck) - so' existe enquanto ele estiver em campo
    # (`state.commander_in_play`), igual ao texto real.
    if state.commander_in_play and "Agent of the Iron Throne" in state.battlefield:
        drain(state, n, each_opp=True)
    if "Zulaport Cutthroat" in state.battlefield:
        drain(state, n, each_opp=True)
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
    if state.commander_in_play and "Agent of the Iron Throne" in state.battlefield:
        drain(state, n, each_opp=True)
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
        drain(state, n, each_opp=True)
        gain_life(state, n)
    if "Mirkwood Bats" in state.battlefield:
        # Achado real 2026-08-28 (auditoria de checklist de mecanica):
        # "Whenever you create OR SACRIFICE a token" - so a metade
        # "create" (via on_tokens_created) disparava; a metade
        # "sacrifice"/leaves-the-battlefield nunca era checada aqui,
        # apesar de ser o motor central de sacrificio do deck
        # (aggressive_treasure_destruction chama isso toda hora).
        drain(state, n, each_opp=True)


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


def try_sevinne_flashback(state: GameState) -> bool:
    """Achado real 2026-09-14: 'Flashback {4}{W}' (Scryfall, MV5 - custo
    alternativo pra conjurar do cemiterio, depois exila) 100% ausente -
    so' o cast normal da mao estava implementado. Oraculo completo:
    'Return target permanent card with mana value 3 or less from your
    graveyard to the battlefield. If this spell was cast from a
    graveyard, you may copy this spell and may choose a new target for
    the copy.' - uma ativacao via flashback resolve DUAS vezes (original
    + copia, cada uma podendo escolher um alvo MV<=3 diferente), nao so'
    uma. Mesma heuristica de alvo (maior mv<=3, nao-terreno) ja usada no
    cast normal."""
    if "Sevinne's Reclamation" not in state.graveyard:
        return False
    if remaining_mana(state) < 5:
        return False
    spend_mana(state, 5)
    state.graveyard.remove("Sevinne's Reclamation")
    for _ in range(2):  # original + copia real (a copia nao existiria sem o flashback)
        cheap = [n for n in state.graveyard if CARD_DB[n].mv <= 3 and CARD_DB[n].ctype != "land"]
        if not cheap:
            continue
        best = max(cheap, key=lambda n: CARD_DB[n].mv)
        state.graveyard.remove(best)
        enter_battlefield(state, best)
        state.recursion_events_total += 1
    state.sevinne_flashback_total += 1
    return True


def try_face_breaker_impulse(state: GameState) -> bool:
    """Achado real 2026-09-14: 'Sacrifice a Treasure: Exile the top card
    of your library. You may play that card this turn.' (Scryfall) -
    tag `impulse_treasure_sac` nunca lida, 100% ausente. Sem {T}/'as a
    sorcery' no oraculo real (repetivel livremente), mas heuristica
    conservadora aqui: 1x/turno (mesmo padrao ja usado pra Jan Jansen),
    pra nao brigar demais pelas Treasures que o proprio Vihaan anima em
    combate e que Ashnod's Altar/KCI consomem depois (TREASURE_MAXIMIZE_
    POLICY)."""
    if "Professional Face-Breaker" not in state.battlefield:
        return False
    if state.face_breaker_used_this_turn:
        return False
    if state.treasures <= 0:
        return False
    sacrifice_treasures(state, 1)
    pull_impulse(state, 1, deadline_turns=0)
    state.face_breaker_used_this_turn = True
    state.face_breaker_impulse_total += 1
    return True


def try_equip_reaver_cleaver(state: GameState):
    """Achado real 2026-09-14: 'Equip {3}' (Scryfall) - custo real nunca
    pago; o bonus de combate ('Whenever this creature deals combat
    damage..., create that many Treasure tokens', ja modelado como proxy
    de +1 Treasure por combate, dado que este arquivo nao rastreia P/T
    por criatura pra calcular 'that many' de verdade) disparava de graca
    pra qualquer ataque, sem nunca ter sido equipado em ninguem. Paga o
    Equip 1x (fica equipado o resto da partida - este simulador nunca
    reequipa), so' se houver ao menos 1 criatura real em campo.

    CORRIGIDO 2026-09-25 (Regra #1, "formula dinamica achatada"): o
    oraculo real e' "Equipped creature gets +1/+1 and has trample and
    'Whenever this creature deals combat damage to a player or
    planeswalker, create THAT MANY Treasure tokens.'" -- o arquivo agora
    rastreia poder impresso (`CREATURE_POWER`), entao "that many" = poder
    do portador + 1 (o proprio +1/+1), +2 com Sentinel Sarah Lyons ativa.
    Equipa a criatura nao-comandante de maior poder (o Vihaan nunca ataca
    neste simulador -- `ready_creatures` o exclui). Se o portador sai de
    campo o Equipamento fica solto (CR 301.5c) e reequipar custa {3} de
    novo."""
    if "The Reaver Cleaver" not in state.battlefield:
        return
    if state.reaver_cleaver_host is not None and state.reaver_cleaver_host in state.battlefield:
        return
    state.reaver_cleaver_host = None
    state.reaver_cleaver_equipped = False
    if remaining_mana(state) < 3:
        return
    hosts = [n for n in state.battlefield if is_creature_card(n) and n != COMMANDER]
    if not hosts:
        return
    spend_mana(state, 3)
    state.reaver_cleaver_host = max(hosts, key=lambda n: CREATURE_POWER.get(n, 0))
    state.reaver_cleaver_equipped = True


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
            # Achado real 2026-09-21 (mesma rodada do fix de CR 903.9a):
            # candidates incluia o comandante sem preferencia nenhuma --
            # um jogador racional nunca sacrifica o proprio comandante de
            # 3 mana como custo adicional do Deadly Dispute quando
            # qualquer outro artefato/criatura real serve (a taxa de
            # recast so' cresce a cada vez). So' o usa se for
            # genuinamente o UNICO artefato/criatura em campo (Deadly
            # Dispute exige o sacrificio como custo adicional pra
            # conjurar -- nao e' opcional).
            candidates = [n for n in state.battlefield if is_creature_card(n) or is_artifact_card(n)]
            non_commander = [n for n in candidates if n != COMMANDER]
            target = non_commander[0] if non_commander else (candidates[0] if candidates else None)
            if target:
                sacrifice_named_creature(state, target)
        draw_cards(state, 2)
        create_treasures(state, 1, source=name)
    elif name == "Inspired Tinkering":
        # Achado real 2026-09-14: "Until the end of your NEXT turn" (nao
        # "until end of turn") - exilado no turno T, jogavel durante T e
        # inteiro T+1, expira em T+2. deadline_turns=2 guardava
        # `state.turn + 2` no momento da conjuracao (turno T), ou seja
        # deadline=T+2 - ainda valido (`entry[1] >= state.turn`) no
        # PROPRIO turno T+2, 1 turno alem do real. deadline_turns=1 e' o
        # valor correto (mesma correcao pro Prosper em end_step, ver
        # abaixo).
        pull_impulse(state, 3, deadline_turns=1)
        create_treasures(state, 3, source=name)
    elif name == "Blood Money":
        real_creatures = [n for n in state.battlefield if is_creature_card(n) and n != COMMANDER]
        n_dead = len(real_creatures) + state.constructs + state.other_tokens
        for c in real_creatures:
            sacrifice_named_creature(state, c)
        sacrifice_constructs(state, state.constructs)
        sacrifice_other_tokens(state, state.other_tokens)
        _destroy_dragons(state)
        create_treasures(state, len(real_creatures), source="Blood Money (nontoken)")
    elif name == "Blasphemous Act":
        real_creatures = [n for n in state.battlefield if is_creature_card(n) and n != COMMANDER]
        for c in real_creatures:
            sacrifice_named_creature(state, c)
        sacrifice_constructs(state, state.constructs)
        sacrifice_other_tokens(state, state.other_tokens)
        _destroy_dragons(state)
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
        # Achado real 2026-09-14: custo real (Scryfall) e' {X}{2}{B} - X e'
        # de verdade pago em mana, nao gratis/capado arbitrariamente em 2
        # (CARD_DB.mv ja corrigido pra 3, o custo fixo real). X = min(mana
        # que sobrou depois do custo fixo ja pago em cast_card, outlaws de
        # verdade disponiveis no cemiterio) - sem cap artificial.
        outlaws_in_gy = [n for n in state.graveyard if is_outlaw(n) and is_creature_card(n)]
        x = min(len(outlaws_in_gy), remaining_mana(state))
        if x > 0:
            spend_mana(state, x)
            for n in outlaws_in_gy[:x]:
                state.graveyard.remove(n)
                enter_battlefield(state, n)
                state.recursion_events_total += 1
    elif name == "Lich-Knights' Conquest":
        # Achado real 2026-09-14: oraculo real e' "Sacrifice any number of
        # ARTIFACTS, ENCHANTMENTS, and/or TOKENS" - o fodder so' contava
        # Constructs+Food+Clue, ignorando Treasures e other_tokens (AMBOS
        # sao tokens de verdade, Treasure tambem e' artefato) - o maior
        # reservatorio de fodder do deck inteiro ficava fora da conta.
        creatures_gy = [n for n in state.graveyard if is_creature_card(n)]
        fodder = state.treasures + state.constructs + state.other_tokens + state.foods + state.clues
        n_return = min(fodder, len(creatures_gy))
        if n_return > 0:
            remaining = n_return
            take = min(state.treasures, remaining)
            sacrifice_treasures(state, take)
            remaining -= take
            take = min(state.constructs, remaining)
            sacrifice_constructs(state, take)
            remaining -= take
            take = min(state.other_tokens, remaining)
            sacrifice_other_tokens(state, take)
            remaining -= take
            take = min(state.foods, remaining)
            if take:
                state.foods -= take
                on_permanent_sacrificed(state, take, is_artifact=True, is_creature=False, is_token=True)
                remaining -= take
            take = min(state.clues, remaining)
            if take:
                state.clues -= take
                on_permanent_sacrificed(state, take, is_artifact=True, is_creature=False, is_token=True)
                remaining -= take
            for n in creatures_gy[:n_return]:
                state.graveyard.remove(n)
                enter_battlefield(state, n)
                state.recursion_events_total += 1


def _destroy_dragons(state: GameState):
    """Fichas de Dragao da Visitor morrendo num "destroy all creatures"
    (nosso ou de oponente) -- destruicao, nao sacrificio (sem Mayhem Devil)."""
    n = state.dragons
    if n <= 0:
        return
    state.dragons = 0
    state.dragons_sick = 0
    on_permanent_destroyed(state, n, is_artifact=False, is_creature=True, is_token=True)


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
    if is_artifact_card(name):
        state.artifact_entered_this_turn = True
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
    # Achado real 2026-09-14: "Extort (Whenever you cast a spell, you may
    # pay {W/B}. If you do, each opponent loses 1 life and you gain that
    # much life.)" (Life Insurance) - tag `extort` nunca lida em lugar
    # nenhum. Mesma convencao ja usada pra TODO drain/vida deste arquivo
    # (Zulaport/Mayhem Devil/Agent of the Iron Throne/etc): e' um drain
    # disparado pela SUA PROPRIA acao (conjurar uma magica), nao por um
    # evento do oponente que precisaria ser simulado - entao e'
    # modelavel de verdade (drain()+gain_life() proxy), diferente de
    # efeitos "opponent_dependent" que exigem um alvo/evento do oponente
    # pra sequer acontecer. Snapshot ANTES do enter_battlefield desta
    # propria carta (senao a propria Life Insurance "pagaria extort" na
    # sua propria conjuracao - a habilidade so' existe em campo, nao
    # ainda na pilha). IA sempre paga se sobrar mana (filosofia agressiva
    # ja padrao no resto do arquivo).
    extort_available = "Life Insurance" in state.battlefield
    if name == COMMANDER:
        spend_mana(state, card.mv + 2 * (state.commander_cast_count))
    else:
        spend_mana(state, card.mv)
    if extort_available and remaining_mana(state) >= 1:
        spend_mana(state, 1)
        drain(state, 1, each_opp=True)
        gain_life(state, 1)
        state.extort_paid_total += 1
    state.spells_cast_this_turn += 1

    # Contra-ataque (`try_smart_opponent_counter`, 7a categoria do modo de
    # resiliencia -- so' faz sentido no exato momento do cast, mesma
    # logica do Megatron/Ur-Dragon/Hei Bai/Edgar Markov): mana e taxa ja'
    # foram gastos ACIMA (CR 903.10a/608.2b contam "cast", nao
    # "resolved") -- so' mira o comandante, e' o motor do deck inteiro.
    # `interaction_rng is None` (modo padrao) faz isso ser sempre False,
    # sem custo nenhum de bit-identidade.
    countered = name == COMMANDER and try_smart_opponent_counter(state)

    # A carta sai da mao (ou vai a campo) ANTES de qualquer efeito
    # colateral (cascade, Lotho) rodar — senao um cascade que descarta
    # carta (ex: Big Score) pode acabar descartando a propria carta que
    # esta sendo conjurada, ainda "presa" na mao. Comandante contra-atacada
    # nunca chega a `enter_battlefield` -- ela nunca esteve fisicamente em
    # `state.hand` (command zone), entao nao ha' zona nenhuma pra mover
    # (nem cemiterio: CR 903.9a so' se aplica a permanente que JA' foi a
    # campo, "dies" exige "from the battlefield" -- um cast contra-atacado
    # nunca resolveu, nunca chegou la').
    is_spell = card.ctype in ("instant", "sorcery")
    if countered:
        pass
    elif is_spell:
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

    if is_spell and not countered:
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


def library_with_swap(swap) -> list:
    """`swap` = (sai, entra) ou lista de pares: troca NA MESMA POSICAO da
    lista (pareamento de seed). A `lista.md` real nao muda."""
    if swap is None:
        return BASE_LIBRARY
    pairs = [swap] if isinstance(swap[0], str) else list(swap)
    lib = BASE_LIBRARY[:]
    for out_card, in_card in pairs:
        assert out_card in lib, f"{out_card} nao esta' na lista"
        assert in_card in CARD_DB and in_card not in lib, in_card
        lib[lib.index(out_card)] = in_card
    return lib


def mulligan(rng: random.Random, max_mulls: int = 3, library=None):
    mulls = 0
    while mulls < max_mulls:
        lib = (library or BASE_LIBRARY)[:]
        rng.shuffle(lib)
        hand = lib[:7]
        lib = lib[7:]
        if should_keep(hand) or mulls == max_mulls - 1:
            # Achado real 2026-09-18 (mesma convencao dos goldfishes
            # manuais do usuario no Archidekt): 1o mulligan e' GRATIS.
            penalty = max(0, mulls - 1)
            if penalty > 0:
                rng.shuffle(hand)
                bottom = hand[:penalty]
                hand = hand[penalty:]
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
    caretaker_drawn_this_turn."""
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
        if try_sevinne_flashback(state):
            continue
        if try_face_breaker_impulse(state):
            continue
        break

    # Achado real 2026-09-14: "Sacrifice three Treasures: Create a 4/4 red
    # Scorpion Dragon creature token with flying and haste. Activate only
    # as a sorcery." (Magda, the Hoardmaster) - 100% ausente do codigo (so'
    # citada em comentario, NUNCA implementada de verdade - so' a 1a
    # habilidade, "whenever you commit a crime", estava coberta). Sem
    # {T} no custo real - repetivel livremente enquanto sobrar Treasure,
    # priorizada aqui antes do Jan Jansen (um corpo real 4/4 voador com
    # haste vale mais que 2 Constructs 1/1).
    while "Magda, the Hoardmaster" in state.battlefield and state.treasures >= 3:
        sacrifice_treasures(state, 3)
        create_other_tokens(state, 1, source="Magda (Scorpion Dragon)", haste=True)
        state.magda_dragons_created_total += 1

    # Achado real 2026-08-31 (rodada ampliada, categoria 13): engine de
    # nivel do Caretaker's Talent - so' depois de esgotar tudo que da' pra
    # conjurar/recuperar (heuristica: desenvolver board novo > subir nivel
    # de uma carta ja' resolvida).
    try_level_caretakers_talent(state)

    # Achado real 2026-09-14: "Equip {3}" - o custo real nunca era pago em
    # lugar nenhum (ver try_equip_reaver_cleaver).
    try_equip_reaver_cleaver(state)

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
    # Achado real 2026-09-14: "At the beginning of combat on your turn,
    # put an oil counter on this artifact, then create an X/1 red
    # Phyrexian Horror creature token with trample and HASTE... Sacrifice
    # that token at the beginning of the next end step." (Urabrask's
    # Forge) - o token era criado no FINAL desta funcao, DEPOIS de
    # `ready_other`/`total_attackers` ja terem sido calculados - mesmo
    # tendo haste real, o token NUNCA contava como atacante no proprio
    # combate em que nascia (e era sacrificado no end_step sem nunca ter
    # feito nada). Corrigido: criado AQUI, antes do snapshot de
    # atacantes, com `haste=True` (nao fica sick) - e' literalmente o
    # motivo do gatilho disparar "at the beginning of combat". Conta
    # exatamente quantos tokens nasceram este turno (Anointed Procession
    # pode dobrar) pra sacrificar a quantidade certa no end_step.
    if "Urabrask's Forge" in state.battlefield:
        state.forge_oil += 1
        made = create_other_tokens(state, 1, source="Urabrask's Forge", haste=True)
        state.forge_tokens_this_turn += made

    animated = 0
    if state.commander_in_play and state.treasures > 0:
        animated = state.treasures  # Vihaan: Treasures viram 3/3 outlaw ate o final do turno
    state.treasures_animated_this_combat = animated

    # Achado real 2026-09-14: 2a habilidade real do Vihaan (a 1a, animar
    # Treasures, ja estava implementada acima) - "Other outlaws you
    # control have vigilance and haste." Vigilance e' 📊 (sem bloqueio
    # modelado, nao muda nada aqui). Haste NUNCA estava propagado pra
    # `ready_creatures` - toda criatura outlaw sem haste impressa
    # (Grenzo/Laughing Jasper Flint/Lotho/Magda-nao-e-outlaw/Mari/Olivia/
    # Orochi/Pitiless Plunderer/Prosper/Witch of the Moors/Zulaport/Aya)
    # ficava presa com doenca de invocacao no turno em que entrava, mesmo
    # com Vihaan em campo concedendo haste de verdade.
    ready_creatures = [n for n in state.battlefield
                       if is_creature_card(n) and n != COMMANDER
                       and (state.creature_cast_turn.get(n, -1) < state.turn
                            or "haste" in CARD_DB[n].tags
                            or (state.commander_in_play and is_outlaw(n)))]
    ready_constructs = max(0, state.constructs - state.constructs_sick)
    ready_other = max(0, state.other_tokens - state.other_tokens_sick)
    ready_dragons = max(0, state.dragons - state.dragons_sick)  # Draconic Visitor (candidata): sem haste

    total_attackers = animated + len(ready_creatures) + ready_constructs + ready_other + ready_dragons
    if total_attackers <= 0:
        return
    state.combat_attacks_total += 1
    _combat_damage_proxy(state, animated, ready_creatures, ready_constructs, ready_other, ready_dragons)

    outlaw_attacking = animated > 0 or any(is_outlaw(n) for n in ready_creatures)
    any_creature_attacking = len(ready_creatures) + ready_constructs + ready_other + animated + ready_dragons > 0

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

    if ("Sentinel Sarah Lyons" in ready_creatures
            and "Sentinel Sarah Lyons" in state.battlefield
            and total_attackers >= 3):
        # Achado real 2026-09-01 (leitura linha-a-linha, "compile TUDO"):
        # tag "anthem_artifact" nunca lida. Oraculo real tem 2
        # habilidades: (1) "creatures you control get +2/+2 as long as an
        # artifact entered this turn" -- estatico numerico sem P/T por
        # criatura neste modelo (sem combate individual em lugar nenhum
        # do arquivo) -- 📊 estrutural, consistente com o resto. (2)
        # "Battalion -- whenever Sarah Lyons and at least two other
        # creatures attack, she deals damage equal to the number of
        # artifacts you control to target player" -- gatilho real e
        # quantificavel (proxy de dano, mesma convencao do Smaug acima),
        # nunca implementado.
        drain(state, artifacts_in_play(state))

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
        if "Aya of Alexandria" in state.battlefield:
            # Achado real 2026-09-14: oraculo real e' "Whenever A HISTORIC
            # creature you control deals combat damage..." (singular, SEM
            # "one or more") - ao contrario de Olivia/Face-Breaker/Grim
            # Hireling/Orochi (todas "one or more...", 1 gatilho em lote
            # de verdade), este dispara UMA VEZ POR criatura historica que
            # ataca - `any(...)` achatava pra 1 token fixo, ignorando o
            # numero real de fontes historicas atacando. Inclui Constructs
            # (artefato) e Treasures animados pelo Vihaan (viram artefato-
            # criatura, tambem historico).
            historic_attackers = (sum(1 for n in ready_creatures if is_historic(n))
                                   + ready_constructs + animated)
            if historic_attackers > 0:
                create_other_tokens(state, historic_attackers, source="Aya of Alexandria")
        if "Grenzo, Havoc Raiser" in state.battlefield:
            # Achado real 2026-09-14: oraculo real e' "Whenever A creature
            # you control deals combat damage..." (singular, sem "one or
            # more") - mesma classe de bug da Aya acima. `total_attackers`
            # ja e' a contagem real de fontes atacando neste combate.
            pull_impulse(state, total_attackers, deadline_turns=0)
        host = state.reaver_cleaver_host
        if ("The Reaver Cleaver" in state.battlefield and state.reaver_cleaver_equipped
                and host in state.battlefield and host in ready_creatures):
            n_dmg = CREATURE_POWER.get(host, 0) + 1
            if "Sentinel Sarah Lyons" in state.battlefield and state.artifact_entered_this_turn:
                n_dmg += 2
            state.reaver_cleaver_treasures_total += n_dmg
            create_treasures(state, n_dmg, source="The Reaver Cleaver")

    if TREASURE_MAXIMIZE_POLICY:
        aggressive_treasure_destruction(state)


def _combat_damage_proxy(state: GameState, animated: int, ready_creatures: list, ready_constructs: int,
                         ready_other: int, ready_dragons: int):
    """Metrica nova 2026-09-25 (so' leitura, nao muda nenhuma decisao):
    dano de combate dos atacantes, sem bloqueio (mesma premissa "ataca
    livre" do resto do arquivo). Antes o arquivo so' media drain -- uma
    carta que troca Treasure (mana) por corpo atacante ficava com valor
    zero. Poder impresso (`CREATURE_POWER`), Treasure animado pelo Vihaan
    3/3, Construct/Servo 1/1, ficha generica 2 (📝 media), Dragao da
    Visitor 5/5. Bonus reais: Caretaker's Talent nivel 3 (+2/+2 em ficha de
    criatura), Sentinel Sarah Lyons (+2/+2 em todas se um artefato entrou
    neste turno), Shared Animosity (+1/+0 por outro atacante que divide
    tipo -- calculado so' nos 2 grupos homogeneos que esta carta troca:
    Constructs/Treasures animados [Construct] e Dragoes)."""
    power = sum(CREATURE_POWER.get(n, 0) for n in ready_creatures)
    if (state.reaver_cleaver_equipped and state.reaver_cleaver_host in ready_creatures
            and "The Reaver Cleaver" in state.battlefield):
        power += 1  # The Reaver Cleaver: +1/+1
    power += 3 * animated + 1 * ready_constructs + OTHER_TOKEN_POWER * ready_other + 5 * ready_dragons
    tokens_attacking = animated + ready_constructs + ready_other + ready_dragons
    if state.caretaker_level >= 3:
        power += 2 * tokens_attacking
    if "Sentinel Sarah Lyons" in state.battlefield and state.artifact_entered_this_turn:
        power += 2 * (len(ready_creatures) + tokens_attacking)
    if "Shared Animosity" in state.battlefield:
        construct_group = animated + ready_constructs
        dragon_group = ready_dragons + sum(1 for n in ready_creatures if n in ("Goldspan Dragon", "Smaug the Magnificent", "Draconic Visitor"))
        for k in (construct_group, dragon_group):
            if k > 1:
                power += k * (k - 1)
    state.combat_damage_proxy_total += power


def check_visitor_combo(state: GameState):
    """Draconic Visitor + Pitiless Plunderer + Ashnod's Altar = loop
    infinito (Regra #7: combo novo, fora do Commander Spellbook -- derivado
    das regras): sacrifica um Dragao no Altar ({C}{C}); o Plunderer ("Whenever
    another creature you control dies, create a Treasure token") cria um
    Treasure, que a Visitor substitui por um Dragao 5/5; repete. Mana
    incolor, mortes, fichas criadas e sacrificadas infinitas. Qualquer
    pagador da lista fecha o jogo na hora: Zulaport Cutthroat, Mirkwood Bats,
    Nadier's Nightblade, Kambal (2a habilidade, sem limite), Sephiroth
    (transforma na 4a e o emblema drena sem limite), Mayhem Devil, Agent of
    the Iron Throne (com o Vihaan em campo). Precisa de 1 criatura pra
    comecar o loop."""
    if state.visitor_combo_turn is not None:
        return
    need = ("Draconic Visitor", "Pitiless Plunderer", "Ashnod's Altar")
    if not all(n in state.battlefield for n in need):
        return
    fodder = state.dragons + state.constructs + state.other_tokens + sum(
        1 for n in state.battlefield if is_creature_card(n) and n not in (COMMANDER, "Pitiless Plunderer", "Draconic Visitor"))
    if fodder <= 0:
        return
    state.visitor_combo_turn = state.turn
    payoffs = ("Zulaport Cutthroat", "Mirkwood Bats", "Nadier's Nightblade", "Kambal, Profiteering Mayor",
               "Sephiroth, Fabled SOLDIER // Sephiroth, One-Winged Angel", "Mayhem Devil")
    if any(n in state.battlefield for n in payoffs) or (
            state.commander_in_play and "Agent of the Iron Throne" in state.battlefield) or state.has_super_nova_emblem:
        if state.win_turn is None:
            state.win_turn = state.turn


def try_sac_land_outlets(state: GameState):
    """Achado real 2026-09-01 (leitura linha-a-linha, "compile TUDO"):
    High Market ({T}, Sacrifice a creature: gain 1 life) e Phyrexian
    Tower ({T}, Sacrifice a creature: Add {B}{B}) -- 2 terrenos com tags
    reais (sac_outlet_life/sac_outlet_bb) nunca lidas em lugar nenhum.
    So sacrifica TOKENS descartaveis (Constructs/other_tokens), nunca uma
    criatura nomeada real -- trocar uma criatura de verdade por 1 vida ou
    1 mana extra e' valor claramente ruim, nenhum piloto racional faria
    isso. Chamado no end_step (depois do combate, quando os tokens do
    turno ja atacaram e nao tem mais uso pendente) -- reusa
    sacrifice_constructs()/sacrifice_other_tokens(), que ja disparam
    todos os gatilhos reais de morte (Zulaport/Pitiless Plunderer/Mahadi/
    Sephiroth/Mayhem Devil) via on_permanent_sacrificed(), sem duplicar
    logica."""
    if "Phyrexian Tower" in state.battlefield:
        if state.constructs > 0:
            sacrifice_constructs(state, 1)
            state.bonus_mana_pool += 1  # BB no lugar do {C} generico normal -> +1 liquido
            state.bonus_mana_generated_total += 1
        elif state.other_tokens > 0:
            sacrifice_other_tokens(state, 1)
            state.bonus_mana_pool += 1
            state.bonus_mana_generated_total += 1

    if "High Market" in state.battlefield:
        if state.constructs > 0:
            sacrifice_constructs(state, 1)
            gain_life(state, 1)
        elif state.other_tokens > 0:
            sacrifice_other_tokens(state, 1)
            gain_life(state, 1)


def end_step(state: GameState):
    try_sac_land_outlets(state)
    if "Mahadi, Emporium Master" in state.battlefield:
        create_treasures(state, state.deaths_this_turn, source="Mahadi (fim do turno)")

    if "Prosper, Tome-Bound" in state.battlefield:
        # Achado real 2026-09-14: "Until the end of YOUR NEXT TURN" (nao
        # "until end of turn") - exilado no end_step do turno T, jogavel
        # durante T+1 inteiro, expira em T+2. deadline_turns=2 guardava
        # `state.turn + 2` = T+2 no momento do trigger (T), ainda "valido"
        # (`entry[1] >= state.turn`) no PROPRIO turno T+2 - 1 turno alem
        # do real. deadline_turns=1 (=T+1) e' o correto (mesma correcao
        # aplicada na Inspired Tinkering, texto identico).
        pull_impulse(state, 1, deadline_turns=1)

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

    # Achado real 2026-09-14: sacrificava sempre exatamente 1, mesmo
    # quando Anointed Procession dobrava a criacao pra 2 tokens no mesmo
    # turno (ambas as copias tem "sacrifice that token" - a ruling padrao
    # pra efeitos de duplicacao de token e' que AMBAS as copias contam
    # como "that token" pro delayed trigger) - `forge_tokens_this_turn`
    # (setado em combat_step, ja considerando o dobro) sacrifica a
    # quantidade certa.
    if "Urabrask's Forge" in state.battlefield and state.forge_tokens_this_turn > 0:
        sacrifice_other_tokens(state, state.forge_tokens_this_turn)

    if ("Revel in Riches" in state.battlefield and state.treasures >= 10
            and state.revel_condition_met_turn is None):
        state.revel_condition_met_turn = state.turn

    if state.constructs_sick or state.other_tokens_sick:
        state.constructs_sick = 0
        state.other_tokens_sick = 0
    state.dragons_sick = 0
    check_visitor_combo(state)
    if state.win_turn is None and state.table_damage_total + state.combat_damage_proxy_total >= LETHAL_PROXY:
        state.win_turn = state.turn


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
    state.black_market_connections_triggered_this_turn = False
    state.life_gained_this_turn = 0
    state.bonus_mana_pool = 0
    state.treasures_animated_this_combat = 0
    state.jan_jansen_used_this_turn = False
    state.deaths_this_turn = 0
    state.sephiroth_deaths_this_turn = 0
    state.face_breaker_used_this_turn = False
    state.forge_tokens_this_turn = 0
    state.artifact_entered_this_turn = False

    if "Smaug the Magnificent" in state.battlefield:
        create_treasures(state, 1, source="Smaug the Magnificent (upkeep)")
    # Revel in Riches: "At the beginning of your upkeep, if you control ten
    # or more Treasures, you win the game." (so' metrica win_turn; o
    # contador historico `revel_condition_met_turn` segue marcado no end_step)
    if state.win_turn is None and "Revel in Riches" in state.battlefield and state.treasures >= 10:
        state.win_turn = state.turn

    # Achado real 2026-09-14: oraculo real da Laughing Jasper Flint e' "At
    # the beginning of your UPKEEP" (nao end step!) - "exile the top X
    # cards..., where X is the number of outlaws you control. UNTIL END
    # OF TURN, you may cast spells from among those cards...". Estava
    # implementada no end_step (fase que so' roda DEPOIS das 2 main
    # phases do turno) - as cartas exiladas la' nunca tinham como ser
    # jogadas (play_from_impulse so' e' chamado dentro de main_phase(),
    # que ja tinha passado 2x quando end_step roda), tornando a
    # habilidade inteira 100% inutil (nenhum valor gerado, so' lixo
    # acumulando em impulse_pool). Corrigida pra rodar aqui, na mesma
    # posicao de upkeep real do Smaug logo acima - "until end of turn"
    # com deadline_turns=0 agora funciona de verdade (cartas jogaveis nas
    # 2 main phases DESTE MESMO turno).
    if "Laughing Jasper Flint" in state.battlefield:
        outlaws = sum(1 for n in state.battlefield if is_outlaw(n))
        pull_impulse(state, outlaws, deadline_turns=0)

    # Achado real 2026-09-18: "skip the draw step" no 1o turno de quem
    # comeca so' existe na regra 1x1 (CR 103.8a). Commander e' sempre
    # multiplayer -- sempre compra, mesmo no T1.
    if state.library:
        state.hand.append(state.library.pop(0))  # compra normal do turno, nao conta como "extra"

    play_land(state)
    main_phase(state)
    check_visitor_combo(state)
    combat_step(state)
    main_phase(state)  # pos-combate — usa mana bonus gerada por sac outlets no combate
    check_visitor_combo(state)

    # Magda: gatilho "whenever you commit a crime" (1x/turno) so pode ser
    # checado depois das main phases, que e quando as magicas que cometem
    # crime (Path to Exile, Council's Judgment etc) sao de fato conjuradas.
    # BUG CORRIGIDO (2026-08-22): antes essa checagem rodava logo apos o
    # reset de commits_crime_this_turn=False, ou seja, sempre lia False —
    # o gatilho da Magda nunca disparava em nenhuma partida simulada.
    if "Magda, the Hoardmaster" in state.battlefield and state.commits_crime_this_turn:
        create_treasures(state, 1, source="Magda (crime)")

    end_step(state)


# ---------------------------------------------------------------------------
# Modo de resiliencia (interacao de oponente) — 2026-09-21
# ---------------------------------------------------------------------------
# Porte completo do design FINAL ja' validado nos outros 9 decks desta
# sessao (Megatron/Ur-Dragon/Hei Bai/Edgar Markov/Ulalek/Toph/Prismatic
# Bridge/Maralen/Rat King Verminister). 7 categorias padronizadas
# (removal/attack/discard/wipe/graveyard-wipe/graveyard-snipe/
# counterspell), 1 rolagem "algum wipe acontece" + escolha ponderada de
# 1 TIPO so' (nao 3 rolagens independentes), gate de atencao por
# oponente (`OPPONENT_ATTENTION_CHANCE`), supressao de ataque pos-wipe
# simetrico (`state.wiped_this_round`).
#
# Diferente dos outros 9 decks (todos retrofits, corrigidos DEPOIS de
# implementados do jeito errado): este ja' nasce com a correcao de CR
# 903.9a aplicada desde a 1a linha (`remove_permanent`, ver docstring) —
# Vihaan DISPARA `on_creature_dies` de verdade quando morre (Zulaport/
# Pitiless Plunderer/Agent of the Iron Throne/Sephiroth/Life Insurance),
# exatamente como qualquer outra criatura, porque CR 903.9a e' acao
# baseada em estado (CR 704), nao substituicao -- ela vai pro cemiterio
# DE VERDADE primeiro (CR 700.4, "dies"), so' DEPOIS o dono PODE
# escolher move-la pra zona de comando. Mayhem Devil ("whenever you
# SACRIFICE...") fica de fora de proposito (`on_permanent_destroyed`,
# nao `on_permanent_sacrificed`) -- destruicao/wipe de oponente nunca e'
# sacrificio feito por mim.

NUM_OPPONENTS = 3  # premissa declarada (mesa de 4), mesma convencao dos outros 9 decks

INTERACTION_SETUP_TURNS = 2
# Turnos 1-2 sao sempre setup, sem chance de reacao nenhuma -- o
# oponente ainda nao tem motivo/mana pra reagir.


def interaction_chance(state: GameState) -> float:
    """Formula compartilhada de 'chance do oponente reagir esse turno' --
    identica aos outros 9 decks: escala com o impacto do meu proprio
    board (permanentes nao-terreno em campo). Treasures/Constructs/
    other_tokens/Clues/Foods somam ao impacto tambem -- sao permanentes
    reais na mesa, so' nao tem entrada nomeada em `state.battlefield`."""
    board_impact = (sum(1 for n in state.battlefield if n not in LAND_NAMES)
                     + state.treasures + state.constructs + state.other_tokens
                     + state.clues + state.foods)
    return min(0.10 + 0.03 * board_impact, 0.75)


OPPONENT_ATTENTION_CHANCE = 1.0 / NUM_OPPONENTS
# Gate de "esse oponente esta' de olho em mim esse turno" (achado real
# do usuario nos outros 9 decks, 2026-09-20: "se sempre for 3 contra 1,
# ai' nao consigo fazer nada, nunca!") -- chance BASE de que um turno de
# oponente qualquer seja sobre MIM, antes de qualquer ajuste por ameaca
# de board (que ja' fica dentro de `interaction_chance()`). Rolado 1x no
# INICIO de `try_smart_opponent_turn`, antes de qualquer categoria.

POST_WIPE_ATTACK_HASTE_FACTOR = 0.15
# Board wipe e' SIMETRICO -- acerta TODA criatura da mesa, nao so' as
# minhas. Se um wipe ja' aconteceu NESTA RODADA (`state.wiped_this_
# round`), TODOS os turnos de oponente restantes na mesma rodada tambem
# ficam sem criaturas de verdade pra atacar -- exceto por haste.

BOARD_WIPE_CHANCE_FACTOR = 0.4
ARTIFACT_WIPE_CHANCE_FACTOR = 0.2
ENCHANTMENT_WIPE_CHANCE_FACTOR = 0.15
GRAVEYARD_WIPE_CHANCE_FACTOR = 0.4
GRAVEYARD_SNIPE_CHANCE_FACTOR = 0.5
COUNTERSPELL_CHANCE_FACTOR = 0.5
# Pesos relativos de cada TIPO de sweeper (criatura/artefato/
# encantamento) -- design final ja' validado nos outros 9 decks: 1
# rolagem "algum wipe acontece" (soma dos 3 pesos) + SO' DEPOIS escolha
# ponderada de qual TIPO, restrita aos tipos com pelo menos 1 alvo legal
# em campo (incluindo tokens agregados). Wipe de criatura muito mais
# comum numa lista real que artefato/encantamento.
WIPE_TYPE_WEIGHTS = {
    "creature": BOARD_WIPE_CHANCE_FACTOR,
    "artifact": ARTIFACT_WIPE_CHANCE_FACTOR,
    "enchantment": ENCHANTMENT_WIPE_CHANCE_FACTOR,
}
TOTAL_WIPE_CHANCE_FACTOR = sum(WIPE_TYPE_WEIGHTS.values())

INTERACTION_ENGINE_PRIORITY = [
    "Black Market Connections",
    "Mahadi, Emporium Master",
    "Pitiless Plunderer",
    "Zulaport Cutthroat",
    "Agent of the Iron Throne",
    "Caretaker's Talent",
    "Krark-Clan Ironworks",
    "Ashnod's Altar",
    "Prosper, Tome-Bound",
    "Mayhem Devil",
]
# Lista curada por prioridade (a mais critica primeiro) -- so' cartas
# que sao motor RECORRENTE de valor (Treasure/drain/mana por
# sacrificio/draw repetivel), nao corpos grandes isolados. O proprio
# Vihaan fica DE FORA de proposito -- ja' tem categoria dedicada
# (`try_smart_opponent_counter`, mira o CAST dele especificamente) e
# remocao pontual nao o mata de verdade mesmo (vai pra zona de comando
# via `remove_permanent`, recastavel depois pagando a taxa de novo),
# entao um oponente esperto prefere gastar a remocao pontual numa peca
# irrecuperavel.

OPPONENT_ATTACKER_PROFILES = [
    ("Knight Token", 2), ("Saproling Token", 1), ("Vampire Token", 1),
    ("Zombie Token", 2), ("Soldier Token", 1), ("Goblin Token", 1),
    ("Elemental Token", 3),
]
# Mesmos perfis genericos ja' validados nos outros 9 decks -- sem
# toughness, este arquivo nao modela combate/bloqueio de um oponente de
# verdade. Todo ataque conecta.


def try_smart_opponent_removal(state: GameState) -> Optional[str]:
    """Remocao 'inteligente' -- mira sempre a peca-motor de maior
    prioridade presente em campo (`INTERACTION_ENGINE_PRIORITY`), nunca
    aleatorio."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    present = [n for n in INTERACTION_ENGINE_PRIORITY if n in state.battlefield]
    if not present:
        return None
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    target = present[0]
    remove_permanent(state, target, source="opponent_removal")
    state.smart_removals_total += 1
    state.smart_removal_log.append((state.turn, target))
    return target


def try_smart_opponent_attack(state: GameState) -> Optional[str]:
    """Ataque de oponente -- SEM bloqueio (limitacao estrutural: este
    arquivo nao modela combate/bloqueio de nenhum tipo). Sempre conecta
    em `state.life`.

    Se `state.wiped_this_round` (algum wipe ja' disparou nesta rodada,
    de qualquer oponente, incluindo este mesmo turno) a chance cai pra
    `POST_WIPE_ATTACK_HASTE_FACTOR` -- representa so' um atacante com
    haste conjurado DEPOIS do wipe."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    chance = interaction_chance(state) * (POST_WIPE_ATTACK_HASTE_FACTOR if state.wiped_this_round else 1.0)
    if state.interaction_rng.random() >= chance:
        return None
    name, power = state.interaction_rng.choice(OPPONENT_ATTACKER_PROFILES)
    state.life -= power
    state.smart_attacks_taken_total += 1
    state.smart_attack_log.append((state.turn, name))
    return name


def try_smart_opponent_discard(state: GameState) -> Optional[str]:
    """Discard aleatorio -- mesma logica dos outros 9 decks (alvo
    puramente ao acaso na mao, sem filtro nenhum)."""
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
    """Board wipe ('destroy all creatures'/'destroy all artifacts'/
    'destroy all enchantments') -- destroi TODOS os meus permanentes do
    tipo escolhido de uma vez via `remove_permanent` (que ja' trata
    comandante->zona de comando, gatilhos reais de morte pra cada um).
    Vihaan nunca e' artefato/encantamento (Legendary Creature, tags
    {"commander", "outlaw"}, confirmado no CARD_DB), entao so' e' alvo
    do wipe de criatura -- exatamente como deveria (CR 903.9a: ele
    genuinamente morre nesse caso, so' depois volta pra zona de comando).

    Design de 2 passos (nao 3 rolagens independentes): 1) rola 1x se
    ALGUM wipe acontece esse turno de oponente, chance =
    `interaction_chance() * TOTAL_WIPE_CHANCE_FACTOR`; 2) SO' se isso
    disparar, escolhe qual TIPO de sweeper via escolha ponderada
    (`state.interaction_rng.choices`) restrita aos tipos que tem pelo
    menos 1 alvo legal em campo (incluindo tokens agregados).

    Tokens agregados (Treasure/Construct/other_tokens/Clue/Food) nao
    vivem como entrada nomeada em `state.battlefield` -- o wipe zera os
    contadores relevantes TAMBEM, disparando `on_permanent_destroyed`
    pra cada bucket. Construct e' artifact_creature (Fabricate) -- conta
    pros DOIS tipos de wipe (criatura E artefato) quando destruido,
    disparando os 2 gatilhos certos em qualquer um dos 2 casos."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * TOTAL_WIPE_CHANCE_FACTOR:
        return None
    has_creature_tokens = (state.constructs + state.other_tokens + state.dragons) > 0
    has_artifact_tokens = (state.treasures + state.constructs + state.clues + state.foods) > 0
    candidates = {
        "creature": [n for n in state.battlefield if is_creature_card(n)],
        "artifact": [n for n in state.battlefield if is_artifact_card(n)],
        "enchantment": [n for n in state.battlefield if is_enchantment_card(n)],
    }
    available = [t for t in candidates if candidates[t]]
    if has_creature_tokens and "creature" not in available:
        available.append("creature")
    if has_artifact_tokens and "artifact" not in available:
        available.append("artifact")
    if not available:
        return None
    wipe_type = state.interaction_rng.choices(available, weights=[WIPE_TYPE_WEIGHTS[t] for t in available])[0]
    targets = candidates[wipe_type]
    hit_creature = any(is_creature_card(n) for n in targets)
    for n in targets:
        remove_permanent(state, n, source=f"opponent_{wipe_type}_wipe")
    log_targets = targets[:]

    if wipe_type == "creature":
        if state.constructs:
            on_permanent_destroyed(state, state.constructs, is_artifact=True, is_creature=True, is_token=True)
            hit_creature = True
        if state.other_tokens:
            on_permanent_destroyed(state, state.other_tokens, is_artifact=False, is_creature=True, is_token=True)
            hit_creature = True
        token_n = state.constructs + state.other_tokens + state.dragons
        if token_n:
            log_targets = targets + [f"{token_n} token(s)"]
        if state.dragons:
            hit_creature = True
        _destroy_dragons(state)
        state.constructs = 0
        state.constructs_sick = 0
        state.other_tokens = 0
        state.other_tokens_sick = 0
        state.smart_wipes_total += 1
        state.smart_wipe_log.append((state.turn, log_targets))
    elif wipe_type == "artifact":
        if state.treasures:
            on_permanent_destroyed(state, state.treasures, is_artifact=True, is_creature=False, is_token=True)
        if state.constructs:
            on_permanent_destroyed(state, state.constructs, is_artifact=True, is_creature=True, is_token=True)
            hit_creature = True
        if state.clues:
            on_permanent_destroyed(state, state.clues, is_artifact=True, is_creature=False, is_token=True)
        if state.foods:
            on_permanent_destroyed(state, state.foods, is_artifact=True, is_creature=False, is_token=True)
        token_n = state.treasures + state.constructs + state.clues + state.foods
        if token_n:
            log_targets = targets + [f"{token_n} token(s)"]
        state.treasures = 0
        state.constructs = 0
        state.constructs_sick = 0
        state.clues = 0
        state.foods = 0
        state.smart_artifact_wipes_total += 1
        state.smart_artifact_wipe_log.append((state.turn, log_targets))
    else:
        state.smart_enchantment_wipes_total += 1
        state.smart_enchantment_wipe_log.append((state.turn, log_targets))

    if hit_creature:
        state.wiped_this_round = True
    return log_targets


def try_smart_opponent_graveyard_wipe(state: GameState) -> Optional[list]:
    """Graveyard hate, modelo MASS EXILE (Bojuka Bog/Soul-Guide
    Lantern-style) -- dispara NO MAXIMO 1x por partida inteira
    (`state.graveyard_wipe_used`)."""
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
    """Graveyard hate, modelo EXILIO DE CARTA UNICA (Scavenging
    Ooze/Cease-style) -- repetivel todo turno. Alvo SMART: maior MV
    entre criatura no cemiterio -- mesmo criterio que Sevinne's
    Reclamation/Phyrexian Reclamation ja' usam pra escolher alvo real de
    recursao."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    candidates = [c for c in state.graveyard if is_creature_card(c)]
    if not candidates:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * GRAVEYARD_SNIPE_CHANCE_FACTOR:
        return None
    target = max(candidates, key=lambda n: CARD_DB[n].mv)
    state.graveyard.remove(target)
    state.smart_graveyard_snipes_total += 1
    state.smart_graveyard_snipe_log.append((state.turn, target))
    return target


def try_smart_opponent_counter(state: GameState) -> bool:
    """Counterspell -- so' mira a conjuracao do proprio Vihaan (mesma
    logica dos outros 9 decks: o motor inteiro do deck depende do
    comandante resolver e atacar/animar Treasures). Chamada de dentro de
    `cast_card()`, nao do loop de `simulate_one_with_interaction` -- so'
    faz sentido no exato momento do cast, dentro do MEU turno."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return False
    if state.interaction_rng.random() >= interaction_chance(state) * COUNTERSPELL_CHANCE_FACTOR:
        return False
    state.smart_counters_total += 1
    state.smart_counter_log.append(state.turn)
    return True


def try_smart_opponent_turn(state: GameState):
    """Simula O TURNO DE UM oponente dentro da rodada entre os meus
    turnos (Regra #6 do CLAUDE.md: bug de orquestracao de turno que
    auditoria carta-a-carta nao pega). Chamada `NUM_OPPONENTS` vezes por
    rodada -- um wipe de um oponente ANTERIOR na rodada continua
    afetando corretamente o ataque de um oponente POSTERIOR na MESMA
    rodada (chamadas em sequencia, mesmo `state`).

    Gate de atencao: antes de rolar QUALQUER categoria, este turno de
    oponente precisa passar em `OPPONENT_ATTENTION_CHANCE`. Wipe e
    ataque nao precisam de exclusao mutua manual aqui: `try_smart_
    opponent_attack` ja' se auto-regula via `state.wiped_this_round`
    (setado por `try_smart_opponent_wipe`, que roda antes, dentro desta
    mesma chamada)."""
    if state.turn > INTERACTION_SETUP_TURNS and state.interaction_rng.random() >= OPPONENT_ATTENTION_CHANCE:
        return
    try_smart_opponent_wipe(state)
    try_smart_opponent_attack(state)
    try_smart_opponent_graveyard_wipe(state)
    try_smart_opponent_graveyard_snipe(state)
    try_smart_opponent_removal(state)
    try_smart_opponent_discard(state)


def simulate_one_with_interaction(seed: int, turns: int = 8, swap=None) -> GameState:
    """Mesmo goldfish de `simulate_one`, mas com `NUM_OPPONENTS` turnos
    de oponente de verdade simulados (`try_smart_opponent_turn`) a cada
    rodada entre os meus turnos. Counterspell (7a categoria) NAO mora
    neste loop -- ver `try_smart_opponent_counter`, chamada de dentro de
    `cast_card()` no exato momento do cast do comandante.

    NUNCA chamado por `run_batch`/`simulate_one` padrao (nem o loop
    aqui, nem o counter dentro de `cast_card` -- ambos ficam inertes sem
    `interaction_rng`). Retorna o `GameState` bruto (nao um resumo),
    mesma convencao dos outros 9 decks, pra inspecao detalhada das
    metricas de resiliencia."""
    rng = random.Random(seed)
    hand, lib, mulls = mulligan(rng, library=library_with_swap(swap))
    state = GameState(hand=hand, library=lib, mulligans=mulls,
                       interaction_rng=random.Random(seed + 999_999))
    for t in range(turns):
        play_turn(state, is_first_turn=(t == 0), on_play=True)
        if state.revel_condition_met_turn is not None:
            break
        state.wiped_this_round = False
        for _ in range(NUM_OPPONENTS):
            try_smart_opponent_turn(state)
    return state


def run_batch_with_interaction(n=2000, turns=8, seed_base=6000000):
    """Batch do modo de resiliencia -- reporta so' as metricas
    relevantes pra 'o motor aguenta perder a peca central?', nao
    duplica o relatorio inteiro do `run_batch` padrao."""
    states = [simulate_one_with_interaction(seed_base + i, turns=turns) for i in range(n)]

    def avg(vals):
        return sum(vals) / len(vals) if vals else 0.0

    print(f"n={n}, seed_base={seed_base}, turns={turns} (MODO RESILIENCIA -- wipe + graveyard hate + "
          f"remocao + ataque + discard aleatorio + counterspell de oponente)")
    print(f"Avg counterspells sofridos (so' mira a conjuracao do Vihaan): "
          f"{avg([s.smart_counters_total for s in states]):.2f}")
    cmd_cast = [s.commander_cast_turn for s in states if s.commander_cast_turn is not None]
    print(f"  -- Turno medio de conjuracao QUE RESOLVEU: {avg(cmd_cast):.2f} | "
          f"nunca resolveu em {turns} turnos: {100*(n-len(cmd_cast))/n:.1f}%")
    print(f"Avg board wipes sofridos: {avg([s.smart_wipes_total for s in states]):.2f}")
    print(f"Avg artifact wipes sofridos: {avg([s.smart_artifact_wipes_total for s in states]):.2f}")
    print(f"Avg enchantment wipes sofridos: {avg([s.smart_enchantment_wipes_total for s in states]):.2f}")
    gy_wiped = sum(1 for s in states if s.smart_graveyard_wipes_total > 0)
    print(f"Partidas com graveyard wipe sofrido (no maximo 1x/partida): {100*gy_wiped/n:.1f}%")
    print(f"Avg graveyard snipes sofridos (sempre a maior MV criatura): "
          f"{avg([s.smart_graveyard_snipes_total for s in states]):.2f}")
    print(f"Avg remocoes inteligentes sofridas: {avg([s.smart_removals_total for s in states]):.2f}")
    print(f"Avg ataques sofridos: {avg([s.smart_attacks_taken_total for s in states]):.2f}")
    print(f"Avg descartes sofridos: {avg([s.smart_discards_total for s in states]):.2f}")
    return states


def simulate_one(seed: int, turns: int = 8, swap=None):
    rng = random.Random(seed)
    hand, lib, mulls = mulligan(rng, library=library_with_swap(swap))
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

    # Achado real 2026-09-14 (auditoria oraculo-por-oraculo final) — novas
    # habilidades implementadas nesta rodada.
    print(f"Avg Scorpion Dragons da Magda (Sacrifice 3 Treasures, 4/4 flying haste): {avg([s.magda_dragons_created_total for s in states]):.2f}")
    print(f"Avg impulsos via Professional Face-Breaker (Sac Treasure: exile+play): {avg([s.face_breaker_impulse_total for s in states]):.2f}")
    print(f"Avg Extort pago (Life Insurance, drain/vida proxy): {avg([s.extort_paid_total for s in states]):.2f}")
    print(f"Avg flashbacks de Sevinne's Reclamation: {avg([s.sevinne_flashback_total for s in states]):.2f}")

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
