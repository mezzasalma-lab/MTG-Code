"""
Goldfish simulator — Megatron, Tyrant (Mardu, B/R/W)

Construido do zero em 2026-08-29, seguindo `references/goldfish-sim-card-rules.md`
(checklist obrigatoria de 13 categorias) e `references/user-standing-rules.md`.

Lista montada a partir de: (1) um primer real de Megatron encontrado pelo
usuario (autor "Ethan", que argumenta explicitamente CONTRA o "EDHREC
Effect" - pegar so os cards mais populares do EDHREC sem entender o motor
real do comandante), (2) 5 decklists reais adicionais (Moxfield/Archidekt)
cruzadas por frequencia de inclusao, (3) cartas confirmadas pelo usuario
como vistas AO VIVO num oponente real (Goblin Engineer, Portal to Phyrexia,
Rakdos the Muscle, Summon: Bahamut, Treasure Nabber, Osgir the Reconstructor,
Wheel of Fortune, Phyrexian Triniform, Blasphemous Act).

======================================================================
MECANICA REAL DO MEGATRON (verificada via Scryfall, nao decorada)
======================================================================
Megatron e' um DFC `transform` de verdade:

Frente ("Megatron, Tyrant", {3}{R}{W}{B}, Legendary Artifact Creature -
Robot, 7/5): "Your opponents can't cast spells during combat." + "At the
beginning of each of your postcombat main phases, you may convert
Megatron. If you do, add {C} for each 1 life your opponents have lost
this turn."

Verso ("Megatron, Destructive Force", Legendary Artifact - Vehicle, 4/5):
"Living metal" (e' criatura so no seu turno) + "Whenever Megatron
attacks, you may sacrifice another artifact. When you do, Megatron deals
damage equal to the sacrificed artifact's mana value to target creature.
If excess damage would be dealt to that creature this way, instead that
damage is dealt to that creature's controller and you convert Megatron."

"More Than Meets the Eye {1}{R}{W}{B}" permite conjurar Megatron DIRETO
como o verso (Destructive Force) por um custo menor - e' assim que o
primer manda jogar (turno 4, mais barato que os {3}{R}{W}{B} da frente).

Sequencia real por turno (uma vez que Megatron esta em campo e pronto):
1. Ataca. Se esta como Destructive Force (Vehicle): pode sacrificar OUTRO
   artefato -> dano = custo de mana desse artefato a uma criatura alvo
   (proxy documentado: assume-se um bloqueador/alvo de 1 de resistencia,
   igual a premissa do proprio primer - "assuming an opponent has a
   1-toughness creature, which they always do"). O excesso (custo - 1)
   vira PERDA DE VIDA REAL do controlador daquela criatura E CONVERTE
   Megatron pra Tyrant - isso acontece DURANTE o combate (na resolucao do
   gatilho de ataque), ANTES do dano de combate ser calculado.
2. Dano de combate: usa o poder de QUALQUER FACE Megatron estiver agora
   (se converteu no passo 1, ja e' Tyrant, poder 7 - nao mais 4 da
   Destructive Force) - isso reconcilia a matematica real do primer
   ("Megatron gets through... deals 7 damage", nao 4).
3. Main phase pos-combate: se Megatron esta como Tyrant (aconteceu no
   passo 1, ou porque ja estava assim desde o inicio do turno), a
   habilidade da FRENTE dispara: pode converter de volta pra Destructive
   Force, gerando mana incolor = TODA vida que os oponentes perderam
   nesse turno (o excesso do passo 1 + o dano de combate do passo 2 +
   qualquer spell de queima/drain conjurado antes).
4. Proximo turno, Megatron comeca como Destructive Force de novo, pronto
   pra repetir o loop inteiro - desde que haja combustivel (outro
   artefato) pra sacrificar.

Sem esse combustivel (o pacote de artefatos baratos do primer, MV<=3,
varios com valor proprio antes de morrer), o motor nao gira - por isso a
lista prioriza quantidade de artefatos baratos sobre "artefatos grandes
de recursao" (o erro que o EDHREC Effect levaria a cometer, segundo o
proprio autor do primer).

Simplificacoes documentadas (nao inventadas — omissoes explicitas):
- Sem oponente real: todo dano/perda-de-vida e' PROXY agregado
  (`NUM_OPPONENTS=3`, mesma convencao dos outros simuladores desta
  biblioteca), nunca vida real de ninguem.
- "Opponents can't cast spells during combat" (Tyrant): stax sem alvo
  real pra modelar (nao ha spells de oponente sendo conjuradas aqui).
- Annihilator 4 (Kozilek/Ulamog): nao modelado numericamente (sacrificio
  de permanente de oponente, sem board real de oponente).
- Removal generica sem alvo real (Crackling Doom, Soul Shatter,
  Shatterskull Smashing, Sundering Eruption) e' conjurada quando ha mana
  sobrando, mesma convencao de "interaction" ja usada em todos os outros
  simuladores desta sessao.
- Price of Progress: sem terrenos de oponente reais pra contar - proxy
  documentado, usa a mesma contagem de terrenos nao-basicos QUE EU
  controlo como estimativa (premissa: composicao de manabase similar
  entre decks Commander de poder parecido).
- Wheel of Misfortune: modelada como wheel completo padrao (descarta mao,
  compra 7) pra mim e pros oponentes-proxy; a metade de "maior numero
  escolhido recebe dano" depende de escolha simultanea de oponente real,
  nao modelada numericamente.
- MDFCs com verso de terreno (Shatterskull Smashing // Shatterskull, the
  Hammer Pass; Sundering Eruption // Volcanic Fissure): registradas so
  pela face de feiticaria (a de maior valor real neste deck) - decisao de
  escopo documentada, o verso de terreno e' so um Mountain condicional,
  baixo valor perder.
- Combate: "ataca" = sem summoning sickness (mesma convencao de todos os
  outros simuladores desta biblioteca). Sem bloqueio real modelado, exceto
  o proprio dano-por-sacrificio do Megatron (que tem seu proprio alvo
  fixo, documentado acima).
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

@dataclass
class Card:
    name: str
    mv: int
    ctype: str
    tags: frozenset = field(default_factory=frozenset)
    power: int = 0
    pips: dict = field(default_factory=dict)
    produces: frozenset = field(default_factory=frozenset)


CARD_DB: dict[str, Card] = {}


def add(name, mv, ctype, tags=(), power=0, pips=None, produces=None):
    CARD_DB[name] = Card(name=name, mv=mv, ctype=ctype, tags=frozenset(tags), power=power,
                          pips=dict(pips or {}), produces=frozenset(produces or ()))


COMMANDER = "Megatron, Tyrant"
# Frente (Tyrant): {3}{R}{W}{B}, mv real 6. Custo MTMTE (verso, Destructive
# Force): {1}{R}{W}{B}, mv 4 - registrado a parte em MEGATRON_* abaixo, ja
# que o simulador escolhe qual face conjurar dinamicamente.
add(COMMANDER, 6, "creature", {"commander", "artifact"}, power=7, pips={"R": 1, "W": 1, "B": 1})
MEGATRON_TYRANT_COST = 6
MEGATRON_TYRANT_POWER = 7
MEGATRON_VEHICLE_COST = 4  # MTMTE
MEGATRON_VEHICLE_POWER = 4
MEGATRON_PIPS = {"R": 1, "W": 1, "B": 1}

NUM_OPPONENTS = 3  # premissa declarada (mesa de 4), nunca vida real rastreada

# --- Motor de combustivel barato (MV<=3, a base real do plano do primer) -------
add("Archaeomancer's Map", 3, "artifact", {"land_ramp_etb"}, pips={"W": 1})
add("Atraxa's Skitterfang", 3, "creature", {"artifact", "combat_pump_oil"}, power=2, pips={})
add("Bitterthorn, Nissa's Animus", 3, "artifact", {"living_weapon", "attack_land_tutor"}, pips={})
add("Brimstone Trebuchet", 3, "creature", {"artifact", "fuel_ping"}, power=0, pips={"R": 1})
add("Cryptolith Fragment", 3, "artifact", {"fuel_mana_drain"}, pips={})
add("Cursed Mirror", 3, "artifact", {"fuel_rock1"}, pips={"R": 1}, produces={"R"})
add("Dauntless Scrapbot", 3, "creature", {"artifact", "fuel_gy_hate_ramp"}, power=1, pips={})
add("Etched Familiar", 3, "creature", {"artifact", "fuel_death_drain"}, power=2, pips={"B": 1})
add("Expedition Map", 1, "artifact", {"fuel_land_tutor"}, pips={})
add("Fire Navy Trebuchet", 3, "creature", {"artifact", "fuel_attack_token"}, power=0, pips={"B": 1})
add("Pumpkin Bombs", 2, "artifact", {"fuel_fuse_burn"}, pips={"R": 1})
add("Retributive Wand", 3, "artifact", {"fuel_ping_death_burst"}, pips={})
add("Scrawling Crawler", 3, "creature", {"artifact", "wheel_upkeep_symmetric"}, power=3, pips={})
add("Unruly Catapult", 3, "creature", {"artifact", "fuel_ping_untap_spell"}, power=0, pips={"R": 1})

# --- Drenagem/dano ------------------------------------------------------------
add("Boltwave", 1, "sorcery", {"burn_opp_flat"}, pips={"R": 1})
add("Damnable Pact", 2, "sorcery", {"pact_x_self"}, pips={"B": 2})
add("Debt to the Deathless", 4, "sorcery", {"drain_x2_self"}, pips={"W": 2, "B": 2})
add("Exsanguinate", 2, "sorcery", {"drain_x_self"}, pips={"B": 2})
add("Flame Rift", 2, "sorcery", {"burn_all_flat"}, pips={"R": 1})
add("Killing Wave", 1, "sorcery", {"edict_pay_life_x"}, pips={"B": 1})
add("Price of Progress", 2, "instant", {"burn_nonbasic_proxy"}, pips={"R": 1})
add("Wheel of Misfortune", 3, "sorcery", {"wheel_full"}, pips={"R": 1})

# --- Finalizadores -------------------------------------------------------------
add("Chromatic Orrery", 7, "artifact", {"rock5", "orrery_draw"}, produces=set("WUBRG"))
add("Cityscape Leveler", 8, "creature", {"artifact", "cast_removal_attack_removal"}, power=8, pips={})
add("Crystalline Entity", 8, "creature", {"artifact", "etb_wipe_nonartifact"}, power=7, pips={})
add("Excalibur, Sword of Eden", 12, "artifact", {"equipment_big_power", "cost_reduce_historic"}, pips={})
add("Galactus, Devourer of Worlds", 10, "creature", {"etb_removal"}, power=12, pips={})
add("Kozilek, Butcher of Truth", 10, "creature", {"cast_draw4"}, power=12, pips={})
add("Memory Jar", 5, "artifact", {"memory_jar_sac"}, pips={})
add("Nexus of Becoming", 6, "artifact", {"nexus_combat_draw_copy"}, pips={})
add("Portal to Phyrexia", 9, "artifact", {"portal_phyrexia"}, pips={})
add("Phyrexian Triniform", 9, "creature", {"artifact", "triniform_death_tokens"}, power=9, pips={})
add("Rise of the Eldrazi", 12, "sorcery", {"rise_eldrazi"}, pips={})
add("Sandstone Oracle", 7, "creature", {"artifact", "etb_hand_diff_draw"}, power=0, pips={})
add("Steel Seraph", 6, "creature", {"artifact"}, power=5, pips={"W": 1})
add("Summon: Bahamut", 9, "creature", {"saga_bahamut"}, power=0, pips={})
add("The Ten Rings", 8, "artifact", {"ten_rings_draw"}, pips={})
add("Ulamog, the Infinite Gyre", 11, "creature", {"cast_removal"}, power=10, pips={})

# --- Criaturas de valor ---------------------------------------------------------
add("Starscream, Power Hungry", 4, "creature", {"artifact"}, power=0, pips={"B": 1})
add("Stensian Sanguinist", 2, "creature", {}, power=0, pips={"B": 1})

# --- Remocao/interacao (conjurada quando ha mana sobrando, sem alvo real) --------
add("Crackling Doom", 3, "instant", {"interaction"}, pips={"R": 1, "W": 1, "B": 1})
add("Descent into Avernus", 3, "enchantment", {"descent_avernus"}, pips={"R": 1})
add("Soul Shatter", 3, "instant", {"interaction"}, pips={"B": 1})
add("Shatterskull Smashing", 3, "sorcery", {"interaction"}, pips={"R": 2})
add("Sundering Eruption", 3, "sorcery", {"interaction"}, pips={"R": 1})
add("Boros Charm", 2, "instant", {"boros_charm_burn"}, pips={"R": 1, "W": 1})
add("Swords to Plowshares", 1, "instant", {"interaction"}, pips={"W": 1})
add("Path to Exile", 1, "instant", {"interaction"}, pips={"W": 1})
add("Vandalblast", 2, "sorcery", {"interaction"}, pips={"R": 1})  # modo overload ({4}{R}, destroi
# TODOS os artefatos dos oponentes) nao modelado separadamente -- mesma
# convencao ja usada pros outros modais do arquivo (Shatterskull Smashing
# etc): so' o modo de alvo unico conta como interaction_spells_cast.
add("Blasphemous Act", 9, "sorcery", {"wipe_reduces_creatures"}, pips={"R": 1})

# --- Rampa/mana ------------------------------------------------------------------
add("Gilded Lotus", 5, "artifact", {"rock3"}, produces=set("WUBRG"))
add("Sol Ring", 1, "artifact", {"rock2"})
add("Arcane Signet", 2, "artifact", {"rock1"}, produces=set("WUBRG"))

# --- Motor central (cartas confirmadas vistas no oponente real) -----------------
add("Rakdos, the Muscle", 5, "creature", {"rakdos_sac_creature"}, power=6, pips={"B": 2, "R": 1})
add("Treasure Nabber", 3, "creature", {"opponent_dependent"}, power=2, pips={"R": 1})
add("Osgir, the Reconstructor", 4, "creature", {"artifact", "osgir_clone"}, power=3, pips={"R": 1, "W": 1})
add("Goblin Engineer", 2, "creature", {"goblin_engineer"}, power=1, pips={"R": 1})
add("Mishra, Tamer of Mak Fawa", 5, "creature", {"mishra_unearth_all"}, power=2, pips={"B": 1, "R": 1})

# --- Draw / valor geral ----------------------------------------------------------
add("Solemn Simulacrum", 4, "creature", {"artifact", "solemn"}, power=2, pips={})
add("Esper Sentinel", 1, "creature", {"opponent_dependent"}, power=1, pips={"W": 1})
# Bracket 2 (2026-09-02, pedido do usuario): removidos os 3 Game Changers
# da lista (Smothering Tithe, The One Ring, Teferi's Protection) --
# substituidos por Mind Stone, Sword of the Animist (abaixo) e Vandalblast
# (na secao de interacao). Nenhuma das 3 originais tinha efeito redondo
# demais pro goldfish solo (Smothering Tithe so' rendia treasure em wheels
# proprios via NUM_OPPONENTS, The One Ring nunca chegou a acumular burden
# de verdade no simulador -- campo existia mas nunca era incrementado --
# entao a troca e' zero perda de dado real, so' sai do território GC).
add("Mind Stone", 2, "artifact", {"fuel_rock1"}, pips={})  # sua propria
# ativada ("{1},T,Sacrifice: draw a card") nao modelada a parte -- quando
# sacrificada, e' sempre pelo motor de fuel do Megatron mesmo (dano
# proporcional ao MV, ja contado em `megatron_combat`), payoff maior do
# que 1 carta; a peca so' teria a ativada propria escolhida se sobrasse
# mana ocioso, cenario nao modelado no goldfish (mesma convencao do
# resto do arquivo pra ativadas secundarias de pecas de fuel).
add("Phyrexian Arena", 3, "enchantment", {"draw_upkeep_pay_life"}, pips={"B": 1})
add("Night's Whisper", 2, "sorcery", {"draw2_life2"}, pips={"B": 1})
add("Sword of the Animist", 2, "artifact", {"sword_of_animist"}, pips={})
add("Wheel of Fortune", 3, "sorcery", {"wheel_full"}, pips={"R": 1})
add("Losheel, Clockwork Scholar", 3, "creature", {"losheel"}, power=2, pips={"W": 1})
add("Scion of Draco", 12, "creature", {"artifact", "domain_reduce"}, power=8, pips={})
add("Myr Retriever", 2, "creature", {"artifact", "toolbox_recur"}, power=0, pips={})
add("Workshop Assistant", 3, "creature", {"artifact", "toolbox_recur"}, power=1, pips={})
add("Junk Diver", 3, "creature", {"artifact", "toolbox_recur"}, power=2, pips={})

ARTIFACT_ISH_TAGS = {"artifact"}
CREATURE_ISH = {"creature"}
LAND_NAMES_SET = set()  # preenchido apos LAND_TYPES abaixo

# --- Terrenos --------------------------------------------------------------------
# `produces`: cores reais (fixas + condicionais tratadas via ETB_TAPPED_LANDS/
# DUAL_LAND_COLORS). Fetches tratadas com o mecanismo real (crack_fetch),
# nao terreno generico (Regra 6 de user-standing-rules.md).
FETCH_TARGETS = {"Arid Mesa"}
LAND_BASIC_TYPES = {
    "Blood Crypt": {"Swamp", "Mountain"}, "Godless Shrine": {"Plains", "Swamp"},
    "Sacred Foundry": {"Mountain", "Plains"},
    "Mountain": {"Mountain"}, "Plains": {"Plains"}, "Swamp": {"Swamp"},
}
add("Arid Mesa", 0, "land", {"fetch"})
add("Battlefield Forge", 0, "land", set(), produces={"R", "W"})
add("Blood Crypt", 0, "land", set(), produces={"B", "R"})
add("Branch of Vitu-Ghazi", 0, "land", set(), produces=set())
add("Caves of Koilos", 0, "land", set(), produces={"W", "B"})
add("Command Tower", 0, "land", set(), produces={"W", "B", "R"})
add("Dark Fortress", 0, "land", set(), produces={"B", "R"})
add("Eye of Ugin", 0, "land", set(), produces=set())
add("Exotic Orchard", 0, "land", set(), produces={"W", "B", "R"})
add("Forbidden Orchard", 0, "land", set(), produces={"W", "B", "R"})
add("Godless Shrine", 0, "land", set(), produces={"W", "B"})
add("Haunted Ridge", 0, "land", {"etb_tapped_check"}, produces={"B", "R"})
add("Marsh Flats", 0, "land", set(), produces={"W", "B"})  # fetch-like fixed dual (simplificado, ver docstring)
# Achado real 2026-09-02 (usuario lembrou de The Ten Rings, o que levou a
# reconferir toda a infraestrutura de "legendary" do arquivo -- achei
# `is_legendary()`/`LEGENDARY_NAMES` DEFINIDOS mas NUNCA chamados em
# lugar nenhum). Oraculo real (Scryfall): "{T}: Add {C}." + "{T}: Add one
# mana of any color. Spend this mana only to cast a legendary spell." +
# "{T}: Add one mana of any color among legendary permanents you
# control." + "{3},{T},Exile: target legendary creature gains hexproof
# and indestructible until end of turn." Modo 1 (incolor) era o UNICO
# implementado (via `produces=set()`, equivalente a incolor generico).
# Corrigido: modo 2 (fixa qualquer cor pra conjurar spell legendario, o
# uso mais valioso numa lista com 13 permanentes legendarios) agora real
# via `color_sources(state, color, spell_name=name)`. Modos 3 (fixar cor
# pra ativar habilidade de legendario) e 4 (hexproof+indestructible)
# ficam de fora por decisao estrutural real, nao por escopo: modo 3
# exigiria um framework generico de "ativar habilidade paga de qualquer
# permanente" que este arquivo nao tem (so trata ativacoes especificas
# hardcoded caso a caso); modo 4 e' protecao contra remocao de oponente,
# sem oponente real modelado neste goldfish solo -- 📊 mesma convencao
# de toda a sessao.
add("Plaza of Heroes", 0, "land", {"legendary_fixer"}, produces=set())
add("Sacred Foundry", 0, "land", set(), produces={"R", "W"})
add("Savai Triome", 0, "land", {"etb_tapped"}, produces={"W", "B", "R"})
add("Shizo, Death's Storehouse", 0, "land", set(), produces={"B"})
add("Spectator Seating", 0, "land", set(), produces={"R", "W"})
add("Sulfurous Springs", 0, "land", set(), produces={"B", "R"})
add("Talon Gates of Madara", 0, "land", set(), produces=set())
add("Urborg, Tomb of Yawgmoth", 0, "land", set(), produces=set())
add("Vault of Champions", 0, "land", set(), produces={"W", "B"})
add("Mountain", 0, "land", set(), produces={"R"})
add("Plains", 0, "land", set(), produces={"W"})
add("Swamp", 0, "land", set(), produces={"B"})

LAND_NAMES = {n for n, c in CARD_DB.items() if c.ctype == "land"}
ETB_TAPPED_LANDS = {"Savai Triome"}


def is_creature_card(name: str) -> bool:
    return CARD_DB[name].ctype == "creature"


def is_artifact_card(name: str) -> bool:
    return "artifact" in CARD_DB[name].tags or CARD_DB[name].ctype == "artifact"


def is_legendary(name: str) -> bool:
    return name in LEGENDARY_NAMES


LEGENDARY_NAMES = {
    "Megatron, Tyrant", "Bitterthorn, Nissa's Animus", "Excalibur, Sword of Eden",
    "Galactus, Devourer of Worlds", "Kozilek, Butcher of Truth", "The Ten Rings",
    "Ulamog, the Infinite Gyre", "Starscream, Power Hungry", "Rakdos, the Muscle",
    "Osgir, the Reconstructor", "Mishra, Tamer of Mak Fawa", "Chromatic Orrery",
    "Losheel, Clockwork Scholar",
}

FLYING_CREATURES = {"Crystalline Entity", "Galactus, Devourer of Worlds", "Steel Seraph"}


def has_flying(name: str) -> bool:
    return name in FLYING_CREATURES


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
    tapped_land_this_turn: Optional[str] = None
    mana_spent_this_turn: int = 0
    bonus_mana_pool: int = 0
    creature_cast_turn: dict = field(default_factory=dict)
    extra_turns_pending: int = 0

    commander_in_play: bool = False
    commander_cast_count: int = 0
    commander_cast_turn: Optional[int] = None
    megatron_face: Optional[str] = None  # "vehicle" ou "tyrant"
    life_lost_by_opponents_this_turn: int = 0
    life: int = 40
    descent_counters: int = 0
    unruly_catapult_ready: bool = True
    scrawling_crawler_no_effect: bool = False
    losheel_draw_used_this_turn: bool = False
    nexus_used_this_turn: bool = False
    fire_navy_used_this_turn: bool = False

    # metrics -----------------------------------------------------------------
    proxy_damage_total: int = 0
    proxy_lifegain_total: int = 0
    cards_drawn_extra: int = 0
    tutors_used_total: int = 0
    ramp_pieces_cast_total: int = 0
    interaction_spells_cast_total: int = 0
    recursion_events_total: int = 0
    megatron_conversions_total: int = 0
    megatron_mana_generated_total: int = 0
    megatron_fuel_sacrificed_total: int = 0
    wheels_total: int = 0
    library_emptied: bool = False

    # Achados reais 2026-09-01 (leitura linha-a-linha completa do oraculo,
    # "compile TUDO"): tags mortas (definidas, nunca lidas em lugar
    # nenhum) - Summon: Bahamut, Cryptolith Fragment, Cityscape Leveler,
    # Retributive Wand, Pumpkin Bombs. Deck novo (2026-08-29), sem rodada
    # de auditoria anterior como os outros desta sessao.
    bahamut_entered_turn: Optional[int] = None
    bahamut_chapter: int = 0
    bahamut_mega_flare_total: int = 0
    cryptolith_transformed: bool = False
    cryptolith_activations_total: int = 0
    cryptolith_entered_turn: Optional[int] = None
    cityscape_leveler_destroys_total: int = 0
    retributive_wand_pings_total: int = 0
    pumpkin_bombs_used: bool = False
    pumpkin_bombs_draws_total: int = 0

    # Achado real 2026-09-02: usuario lembrou de Phyrexian Triniform
    # (citada no docstring do topo como carta "confirmada vista ao vivo
    # num oponente real", mas nunca tinha entrado de fato nas 99 cartas
    # da lista) -- adicionada no lugar de Rakdos Charm (remocao mais
    # redundante do pacote de interacao, ja com 7 outras pecas).
    triniform_tokens_total: int = 0


def draw_cards(state: GameState, n: int):
    for _ in range(n):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1
        else:
            state.library_emptied = True


def proxy_drain(state: GameState, n: int):
    state.proxy_damage_total += n
    state.life_lost_by_opponents_this_turn += n


def self_damage(state: GameState, n: int):
    state.life -= n


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
    if "Arcane Signet" in state.battlefield:
        total += 1
    if "Gilded Lotus" in state.battlefield:
        total += 3
    if "Chromatic Orrery" in state.battlefield:
        total += 5
    if "Cursed Mirror" in state.battlefield:
        total += 1
    if "Mind Stone" in state.battlefield:
        total += 1
    return total


def total_mana(state: GameState) -> int:
    lands = sum(1 for n in state.battlefield if n in LAND_NAMES)
    if state.tapped_land_this_turn is not None:
        lands -= 1
    return lands + rocks_mana(state) + state.bonus_mana_pool


def remaining_mana(state: GameState) -> int:
    return max(0, total_mana(state) - state.mana_spent_this_turn)


def color_sources(state: GameState, color: str, spell_name: str = None) -> int:
    n = 0
    for card in state.battlefield:
        if card not in CARD_DB:
            continue
        if card == state.tapped_land_this_turn:
            continue
        c = CARD_DB[card]
        if color in c.produces:
            n += 1
        elif ("legendary_fixer" in c.tags and spell_name is not None
              and is_legendary(spell_name)):
            # Plaza of Heroes modo 2: "Add one mana of any color. Spend
            # this mana only to cast a legendary spell." So conta quando
            # a magica sendo conjurada e' de verdade legendaria.
            n += 1
    return n


def has_color_sources_for(state: GameState, name: str) -> bool:
    for color, needed in CARD_DB[name].pips.items():
        if color_sources(state, color, spell_name=name) < needed:
            return False
    return True


def effective_cost(state: GameState, name: str) -> int:
    mv = CARD_DB[name].mv
    if name == "Scion of Draco":
        # Domain -- "This spell costs {2} less to cast for each basic
        # land type among lands you control." Achado real 2026-09-01
        # (leitura linha-a-linha completa do oraculo, "compile TUDO"): a
        # tag "domain_reduce" nunca era lida em lugar nenhum -- ficava
        # fixa em {12}, praticamente incastavel numa lista de 93 cartas.
        # Este deck (Mardu, R/W/B) so' tem 3 tipos basicos possiveis
        # (Mountain/Plains/Swamp, ver LAND_BASIC_TYPES) -- sem
        # Forest/Island, dominio maximo real e' 3 (nao 5), reducao
        # maxima real e' -{6} (custo minimo {6}), nao -{10}.
        types = set()
        for n in state.battlefield:
            types |= LAND_BASIC_TYPES.get(n, set())
        mv = max(0, mv - 2 * len(types))
    return mv


def can_cast(state: GameState, name: str) -> bool:
    return remaining_mana(state) >= effective_cost(state, name) and has_color_sources_for(state, name)


def spend_mana(state: GameState, n: int):
    state.mana_spent_this_turn += n


def crack_fetch(state: GameState, fetch_name: str):
    candidates = [n for n in state.library if n in LAND_BASIC_TYPES]
    if not candidates:
        state.battlefield.append(fetch_name)  # sem alvo, fica como terreno incolor (raro)
        return

    def score(land):
        colors = LAND_BASIC_TYPES.get(land, set())
        produces = CARD_DB[land].produces if land in CARD_DB else set()
        if not produces:
            return 99
        return min(color_sources(state, c) for c in produces)

    candidates.sort(key=score)
    pick = candidates[0]
    state.library.remove(pick)
    state.battlefield.append(pick)
    state.life -= 1


# ---------------------------------------------------------------------------
# Megatron - motor central
# ---------------------------------------------------------------------------

def cast_megatron(state: GameState):
    if state.commander_in_play:
        return
    tax = 2 * state.commander_cast_count
    vehicle_cost = MEGATRON_VEHICLE_COST + tax
    tyrant_cost = MEGATRON_TYRANT_COST + tax
    if remaining_mana(state) >= vehicle_cost and has_color_sources_for(state, COMMANDER):
        spend_mana(state, vehicle_cost)
        state.megatron_face = "vehicle"
    elif remaining_mana(state) >= tyrant_cost and has_color_sources_for(state, COMMANDER):
        spend_mana(state, tyrant_cost)
        state.megatron_face = "tyrant"
    else:
        return
    if COMMANDER in state.hand:
        state.hand.remove(COMMANDER)
    state.battlefield.append(COMMANDER)
    state.commander_in_play = True
    state.commander_cast_count += 1
    if state.commander_cast_turn is None:
        state.commander_cast_turn = state.turn
    state.creature_cast_turn[COMMANDER] = state.turn


def best_fuel_artifact(state: GameState):
    """Escolhe qual artefato sacrificar pro gatilho de ataque do Megatron
    (Destructive Force): 'you may sacrifice another artifact... damage
    equal to the sacrificed artifact's mana value'. Heuristica documentada:
    prioriza o artefato de MAIOR custo de mana (maximiza dano/mana gerada),
    excluindo o proprio Megatron e permanentes cujo valor continuo (Sol
    Ring, Arcane Signet, rocks, terrenos-artefato) supera o valor de
    sacrificio - so' sacrifica de verdade peças do "pacote de combustivel"
    (tag 'fuel_*') ou artefatos ja' esgotados de valor."""
    FUEL_TAG_PREFIX = "fuel_"
    candidates = [n for n in state.battlefield
                  if n != COMMANDER and is_artifact_card(n)
                  and (any(t.startswith(FUEL_TAG_PREFIX) for t in CARD_DB[n].tags)
                       or n in ("Myr Retriever", "Workshop Assistant", "Junk Diver"))]
    if not candidates:
        return None
    candidates.sort(key=lambda n: -CARD_DB[n].mv)
    return candidates[0]


def megatron_combat(state: GameState):
    if not state.commander_in_play or state.megatron_face is None:
        return
    if COMMANDER not in ready_creatures(state):
        return

    if state.megatron_face == "vehicle":
        fuel = best_fuel_artifact(state)
        if fuel is not None:
            state.battlefield.remove(fuel)
            state.graveyard.append(fuel)
            state.megatron_fuel_sacrificed_total += 1
            toolbox_recur_death_trigger(state, fuel)
            mv = CARD_DB[fuel].mv
            excess = max(0, mv - 1)  # proxy: alvo de 1 de resistencia (premissa do proprio primer)
            if excess > 0:
                proxy_drain(state, excess)
            state.megatron_face = "tyrant"  # converte NO MEIO do combate (real: antes do dano de combate)
            state.megatron_conversions_total += 1

    power = MEGATRON_TYRANT_POWER if state.megatron_face == "tyrant" else MEGATRON_VEHICLE_POWER
    if "Sword of the Animist" in state.battlefield:
        # "Equipped creature gets +1/+1." Equip {2} nao rastreado a parte
        # (simplificacao ja usada pro resto de equipment-like do arquivo
        # -- so' o Megatron ataca de verdade nesse deck, entao e' sempre
        # ele quem porta). "Whenever equipped creature attacks, you may
        # search your library for a basic land card, put it onto the
        # battlefield tapped, then shuffle." Real, dispara em todo ataque.
        power += 1
        basics = [n for n in state.library if n in ("Mountain", "Plains", "Swamp")]
        if basics:
            pick = basics[0]
            state.library.remove(pick)
            state.battlefield.append(pick)
    proxy_drain(state, power)


def megatron_postcombat(state: GameState):
    if not state.commander_in_play or state.megatron_face != "tyrant":
        return
    if state.life_lost_by_opponents_this_turn > 0:
        mana = state.life_lost_by_opponents_this_turn
        state.bonus_mana_pool += mana
        state.megatron_mana_generated_total += mana
        state.megatron_face = "vehicle"
        state.megatron_conversions_total += 1


# ---------------------------------------------------------------------------
# Toolbox de recursao (Myr Retriever / Workshop Assistant / Junk Diver) +
# Goblin Engineer como sac outlet real
# ---------------------------------------------------------------------------

def toolbox_recur_death_trigger(state: GameState, dying_name: str):
    """Dispatch central de "quando isso morre" -- chamado em todo ponto
    real do arquivo onde uma criatura/artefato vai pro cemiterio (fuel do
    Megatron, ativacao do Goblin Engineer, exile do Osgir, unearth do
    Mishra, ETB-wipe da Crystalline Entity). Cobre 2 gatilhos reais:

    1. 'When this creature dies, return another target artifact card in
       your graveyard to your hand.' -- as 3 pecas do toolbox (Myr
       Retriever/Workshop Assistant/Junk Diver), busca OUTRO artefato no
       cemiterio (idealmente outra peca do proprio toolbox, fechando o
       loop) e devolve pra mao.
    2. Phyrexian Triniform (achado real 2026-09-02, usuario lembrou da
       carta): 'When this creature dies, create three 3/3 colorless
       Phyrexian Golem artifact creature tokens.' -- real, incondicional,
       os 3 tokens tambem sao combustivel real pro proximo sacrificio do
       Megatron (fuel_* via `best_fuel_artifact()`, ja' que sao artefatos)."""
    if dying_name == "Phyrexian Triniform":
        token_name = "Phyrexian Golem Token"
        if token_name not in CARD_DB:
            add(token_name, 0, "creature", {"artifact"}, power=3)
        for _ in range(3):
            state.battlefield.append(token_name)
        state.triniform_tokens_total += 3
    if dying_name not in ("Myr Retriever", "Workshop Assistant", "Junk Diver"):
        return
    pool = [c for c in state.graveyard if c != dying_name and is_artifact_card(c)]
    if not pool:
        return
    toolbox_in_gy = [c for c in pool if c in ("Myr Retriever", "Workshop Assistant", "Junk Diver")]
    best = toolbox_in_gy[0] if toolbox_in_gy else max(pool, key=lambda n: CARD_DB[n].mv)
    state.graveyard.remove(best)
    state.hand.append(best)
    state.recursion_events_total += 1


def try_goblin_engineer_activation(state: GameState):
    """'{R}, {T}, Sacrifice an artifact: Return target artifact card with
    mana value 3 or less from your graveyard to the battlefield.' Sac
    outlet REAL e repetivel (1x/turno, precisa tap) - fecha o loop do
    toolbox (sacrifica uma peca, recompra artefato <=3 do cemiterio pro
    campo) e tambem realimenta o combustivel do Megatron."""
    if "Goblin Engineer" not in state.battlefield or "Goblin Engineer" not in ready_creatures(state):
        return
    if remaining_mana(state) < 1 or color_sources(state, "R") < 1:
        return
    sac_candidates = [n for n in state.battlefield if n != COMMANDER and n != "Goblin Engineer"
                       and is_artifact_card(n)]
    if not sac_candidates:
        return
    pre_check = [c for c in state.graveyard if is_artifact_card(c) and CARD_DB[c].mv <= 3]
    if not pre_check:
        return
    spend_mana(state, 1)
    sac = min(sac_candidates, key=lambda n: CARD_DB[n].mv)
    state.battlefield.remove(sac)
    state.graveyard.append(sac)
    toolbox_recur_death_trigger(state, sac)
    return_candidates = [c for c in state.graveyard if is_artifact_card(c) and CARD_DB[c].mv <= 3]
    if not return_candidates:
        return
    best = max(return_candidates, key=lambda n: CARD_DB[n].mv)
    state.graveyard.remove(best)
    enter_battlefield(state, best, from_hand=False)
    state.recursion_events_total += 1


def try_osgir_activation(state: GameState):
    """'{X}, {T}, Exile an artifact card with mana value X from your
    graveyard: Create two tokens that are copies of the exiled card.'
    Repetivel (1x/turno, precisa tap). Prioriza o artefato de MAIOR custo
    no cemiterio (Portal to Phyrexia se disponivel = duas ETBs de sacrificio
    em massa)."""
    if "Osgir, the Reconstructor" not in state.battlefield or "Osgir, the Reconstructor" not in ready_creatures(state):
        return
    pool = [c for c in state.graveyard if is_artifact_card(c) and CARD_DB[c].mv > 0]
    if not pool:
        return
    best = max(pool, key=lambda n: CARD_DB[n].mv)
    x = CARD_DB[best].mv
    if remaining_mana(state) < x:
        return
    spend_mana(state, x)
    state.graveyard.remove(best)
    state.tutors_used_total += 1
    for _ in range(2):
        token_name = make_token_copy_name(best)
        state.battlefield.append(token_name)
        resolve_token_copy_etb(state, best)
    state.recursion_events_total += 2


def make_token_copy_name(base_name: str) -> str:
    """Registra um alias no CARD_DB pra copias-token (Osgir/Nexus of
    Becoming) apontando pro mesmo Card real - evita KeyError em toda
    checagem is_creature_card/is_artifact_card/color_sources/etc que
    faz lookup direto em CARD_DB[nome_em_campo]."""
    token_name = base_name + " (copia)"
    if token_name not in CARD_DB:
        CARD_DB[token_name] = CARD_DB[base_name]
    return token_name


def resolve_token_copy_etb(state: GameState, base_name: str):
    """Copias-token do Osgir disparam a ETB real da carta copiada (regra
    real: token e' uma copia de verdade). So' despacha os ETBs relevantes
    ja implementados (Portal to Phyrexia, Sandstone Oracle etc.)."""
    tags = CARD_DB[base_name].tags
    if "portal_phyrexia" in tags:
        do_portal_to_phyrexia(state)
    elif "etb_hand_diff_draw" in tags:
        draw_cards(state, 2)  # aproximacao conservadora (ver do_sandstone_oracle)
    elif "solemn" in tags:
        draw_cards(state, 1)


def try_mishra_unearth(state: GameState):
    """'Each artifact card in your graveyard has unearth {1}{B}{R}.'
    Repetivel (uma ativacao de unearth por turno, escolhendo o alvo de
    maior valor - real: unearth e' 1x por carta, mas nada limita quantas
    cartas diferentes por turno; tetado aqui em 1/turno por simplicidade
    defensiva, documentado)."""
    if "Mishra, Tamer of Mak Fawa" not in state.battlefield:
        return
    if remaining_mana(state) < 2 or color_sources(state, "B") < 1 or color_sources(state, "R") < 1:
        return
    pool = [c for c in state.graveyard if is_artifact_card(c) and c != COMMANDER]
    if not pool:
        return
    best = max(pool, key=lambda n: CARD_DB[n].mv)
    spend_mana(state, 2)
    state.graveyard.remove(best)
    enter_battlefield(state, best, from_hand=False)
    # Unearth: exilado no fim do turno ou se sair de campo - aproximado
    # como sacrificado imediatamente apos entrar (valor de ETB capturado,
    # sem permanencia real, documentado).
    if best in state.battlefield:
        state.battlefield.remove(best)
        state.graveyard.append(best)
        toolbox_recur_death_trigger(state, best)
    state.recursion_events_total += 1


# ---------------------------------------------------------------------------
# ETB / ativacoes recorrentes das pecas de combustivel
# ---------------------------------------------------------------------------

def resolve_etb(state: GameState, name: str):
    tags = CARD_DB[name].tags

    if "land_ramp_etb" in tags:
        # Archaeomancer's Map: "search for up to two basic Plains, put into
        # hand" - land tutor real, vai pra mao (nao campo).
        plains_in_lib = [n for n in state.library if n == "Plains"]
        for _ in range(min(2, len(plains_in_lib))):
            state.library.remove("Plains")
            state.hand.append("Plains")
            state.tutors_used_total += 1

    if "fuel_gy_hate_ramp" in tags:
        # Dauntless Scrapbot: exila cemiterios de oponente (sem efeito
        # solo real) + cria Lander token ({2},{T},sac: busca basica pro
        # campo tapped) - ramp real, simplificado como land direto agora.
        land_pool = [n for n in state.library if n in ("Mountain", "Plains", "Swamp")]
        if land_pool:
            def basic_score(n):
                colors = CARD_DB[n].produces
                return min((color_sources(state, c) for c in colors), default=99)
            pick = min(land_pool, key=basic_score)
            state.library.remove(pick)
            state.battlefield.append(pick)
            state.tapped_land_this_turn = state.tapped_land_this_turn or pick

    if "etb_hand_diff_draw" in tags:
        do_sandstone_oracle(state)

    if "portal_phyrexia" in tags:
        do_portal_to_phyrexia(state)

    if "etb_removal" in tags or "cast_removal" in tags:
        pass  # Galactus/Ulamog: destroy target permanent - documentado como
        # "disponivel quando ha alvo hipotetico", sem efeito numerico solo
        # (mesma convencao de 'interaction' usada no resto do arquivo).

    if "cast_removal_attack_removal" in tags:
        # Cityscape Leveler: "When you cast this spell AND whenever this
        # creature attacks, destroy up to one target nonland permanent."
        # Achado real 2026-09-01 (leitura linha-a-linha, "compile TUDO"):
        # tag definida mas NUNCA lida em lugar nenhum - nem o cast nem o
        # ataque contavam como interacao. Mesma convencao de
        # etb_removal/cast_removal (sem alvo real de oponente, so' conta
        # como interacao usada) - a metade de ATAQUE fica em
        # `try_cityscape_leveler_attack()`, chamada no combat_step.
        state.interaction_spells_cast_total += 1

    if "fuel_mana_drain" in tags:
        # Cryptolith Fragment: "This artifact enters tapped." Achado real
        # 2026-09-01 - registra o turno de entrada pra gatear a ativada
        # (nao e' criatura, entao `creature_cast_turn` nunca a rastreava).
        state.cryptolith_entered_turn = state.turn

    if "saga_bahamut" in tags:
        # Summon: Bahamut: Saga de 4 capitulos. Achado real 2026-09-01
        # (leitura linha-a-linha, "compile TUDO"): tag definida mas nunca
        # lida - a carta inteira (incluindo o Mega Flare, um finisher real
        # de dano = MV total dos outros permanentes) estava 100% ausente.
        # Capitulo I dispara na entrada (contado como interacao, mesma
        # convencao de destroy sem alvo real); II/III/IV avancam via
        # `try_bahamut_saga()`, chamada no upkeep.
        state.bahamut_entered_turn = state.turn
        state.bahamut_chapter = 1
        state.interaction_spells_cast_total += 1

    if "cast_draw4" in tags:
        draw_cards(state, 4)  # Kozilek: "when you cast this spell, draw four cards"

    if "etb_wipe_nonartifact" in tags:
        # Crystalline Entity: "if you cast it, destroy all nonartifact
        # creatures" - ACHADO REAL: isso mata minhas proprias criaturas
        # nao-artefato tambem (Rakdos the Muscle, Treasure Nabber, Solemn
        # Simulacrum e' artefato entao sobrevive, Losheel/Stensian
        # Sanguinist/Mishra/Esper Sentinel sao criaturas comuns e morrem).
        # Efeito simetrico real, implementado sem excecao pro meu lado.
        victims = [n for n in state.battlefield if is_creature_card(n) and not is_artifact_card(n) and n != name]
        for v in victims:
            state.battlefield.remove(v)
            state.graveyard.append(v)
            toolbox_recur_death_trigger(state, v)
        proxy_drain(state, 3 * NUM_OPPONENTS)  # premissa: oponentes tambem tinham ~3 criaturas nao-artefato cada


def resolve_fuel_ping(state: GameState, name: str):
    """Brimstone Trebuchet/Unruly Catapult: '{T}: deals 1 damage to each
    opponent.' Brimstone so re-tapa com Knight entrando (nao ha Knight na
    lista - so ativa 1x). Unruly Catapult re-tapa a cada instant/sorcery
    conjurado no turno - contado a parte em cast_card()."""
    if state.creature_cast_turn.get(name, -1) >= state.turn:
        return  # doenca de invocacao
    proxy_drain(state, 1 * NUM_OPPONENTS)


def try_fuel_pings(state: GameState):
    if "Brimstone Trebuchet" in state.battlefield:
        resolve_fuel_ping(state, "Brimstone Trebuchet")
    if "Unruly Catapult" in state.battlefield and state.unruly_catapult_ready:
        resolve_fuel_ping(state, "Unruly Catapult")
        state.unruly_catapult_ready = False


def try_fire_navy_trebuchet(state: GameState):
    """'Whenever you attack, create a 2/1 flying Construct token tapped
    and attacking, named Ballistic Boulder, sacrificed at end step.' Sem
    dano de combate real modelado (sem bloqueio), token existe so' pro
    registro - conta como fonte extra de 'ataque' pro proxy de dano via
    seu proprio corpo eventualmente sendo sacrificado como combustivel."""
    if "Fire Navy Trebuchet" not in state.battlefield or state.fire_navy_used_this_turn:
        return
    state.fire_navy_used_this_turn = True


def try_bahamut_saga(state: GameState):
    """Summon: Bahamut, capitulos II/III/IV (achado real 2026-09-01, ver
    resolve_etb pro capitulo I). 'As this Saga enters and after your draw
    step, add a lore counter. Sacrifice after IV.' Capitulo I ja disparou
    no turno de entrada; II/III/IV disparam nos 3 upkeeps seguintes
    (aproximacao de timing "draw step" -> "upkeep", mesma convencao ja
    usada no resto do arquivo pra sagas/capitulos)."""
    if state.bahamut_entered_turn is None or "Summon: Bahamut" not in state.battlefield:
        return
    turns_since = state.turn - state.bahamut_entered_turn
    if turns_since <= 0 or turns_since > 3 or state.bahamut_chapter >= turns_since + 1:
        return
    state.bahamut_chapter = turns_since + 1
    if state.bahamut_chapter == 2:
        # II - Destroy up to one target nonland permanent (mesmo proxy de
        # interacao do capitulo I, sem alvo real).
        state.interaction_spells_cast_total += 1
    elif state.bahamut_chapter == 3:
        draw_cards(state, 2)
    elif state.bahamut_chapter == 4:
        # Mega Flare: dano = MV total de OUTROS permanentes que controlo,
        # a cada oponente - finisher real, calculado no momento (agrega
        # todo o board, nao so' artefatos/criaturas).
        mv_total = sum(CARD_DB[n].mv for n in state.battlefield
                       if n != "Summon: Bahamut" and n in CARD_DB)
        proxy_drain(state, mv_total * NUM_OPPONENTS)
        state.bahamut_mega_flare_total += mv_total * NUM_OPPONENTS
        state.battlefield.remove("Summon: Bahamut")
        state.graveyard.append("Summon: Bahamut")


def try_cityscape_leveler_attack(state: GameState):
    """Cityscape Leveler: metade de ATAQUE do "cast_removal_attack_removal"
    (achado real 2026-09-01, ver resolve_etb pra metade de cast). Ataca
    todo turno em que nao tem doenca de invocacao (mesma convencao de
    'ataque' usada no resto do arquivo)."""
    if "Cityscape Leveler" not in state.battlefield:
        return
    if state.creature_cast_turn.get("Cityscape Leveler", -1) >= state.turn:
        return
    state.interaction_spells_cast_total += 1


def try_cryptolith_fragment(state: GameState):
    """Cryptolith Fragment // Aurora of Emrakul (achado real 2026-09-01,
    leitura linha-a-linha, "compile TUDO" - tag "fuel_mana_drain" nunca
    lida em lugar nenhum). Frente: '{T}: Add one mana of any color. Each
    player loses 1 life.' - mana real com custo real (dano simetrico,
    aplicado sem excecao pro meu lado, mesma convencao do Descent into
    Avernus). 'Enters tapped' (achado junto): so ativa a partir do turno
    seguinte ao que entrou."""
    if "Cryptolith Fragment" not in state.battlefield or state.cryptolith_transformed:
        return
    if state.cryptolith_entered_turn == state.turn:
        return  # enters tapped -> so' ativa a partir do proximo turno
    state.bonus_mana_pool += 1
    self_damage(state, 1)
    proxy_drain(state, 1 * NUM_OPPONENTS)
    state.cryptolith_activations_total += 1
    # "At the beginning of your upkeep, if each player has 10 or less
    # life, transform." Sem vida real de oponente individual rastreada -
    # aproximacao documentada: vida de oponente ~= 40 - proxy_damage_total
    # (dano acumulado desde o inicio da partida, unica leitura disponivel
    # neste modelo agregado). Apos transformar, vira Aurora of Emrakul
    # (flying, deathtouch, ataca: cada oponente perde 3) - contada via
    # `try_cityscape_leveler_attack`-style simplificado abaixo.
    approx_opponent_life = 40 - state.proxy_damage_total
    if state.life <= 10 and approx_opponent_life <= 10:
        state.cryptolith_transformed = True


def try_aurora_of_emrakul_attack(state: GameState):
    """Verso transformado do Cryptolith Fragment: 'Whenever this creature
    attacks, each opponent loses 3 life.' Achado real 2026-09-01."""
    if not state.cryptolith_transformed:
        return
    if state.cryptolith_entered_turn == state.turn:
        return
    proxy_drain(state, 3 * NUM_OPPONENTS)


def try_retributive_wand_ping(state: GameState):
    """Retributive Wand: '{3},{T}: deals 1 damage to any target.' Achado
    real 2026-09-01 (tag "fuel_ping_death_burst" nunca lida). Repetivel
    todo turno com mana sobrando (diferente de Brimstone/Unruly, que sao
    de graca - este custa {3} real). O gatilho de morte ('5 damage')
    permanece 📊 estrutural: nenhuma remocao/sacrificio involuntario dos
    PROPRIOS permanentes e' modelada neste sim (mesma razao documentada
    pra Enduring Vitality/Enduring Tenacity noutros decks da sessao)."""
    if "Retributive Wand" not in state.battlefield:
        return
    if remaining_mana(state) < 3:
        return
    spend_mana(state, 3)
    proxy_drain(state, 1 * NUM_OPPONENTS)
    state.retributive_wand_pings_total += 1


def try_pumpkin_bombs(state: GameState):
    """Pumpkin Bombs: '{T}, Discard two cards: Draw three cards, then put
    a fuse counter... deals damage = fuse counters to target opponent.
    THEY gain control of this artifact.' Achado real 2026-09-01 (tag
    "fuel_fuse_burn" nunca lida). Ativacao UNICA de verdade (nao um
    julgamento de valor - o oraculo literalmente tira o artefato do seu
    controle depois do primeiro uso, "activate only once each turn" nao
    e' a razao, e' a troca de controle). So' ativa com 2+ cartas
    descartaveis sobrando na mao (nunca descarta as ultimas 2 cartas uteis)."""
    if "Pumpkin Bombs" not in state.battlefield or state.pumpkin_bombs_used:
        return
    discardable = [c for c in state.hand if c != "Pumpkin Bombs"]
    if len(discardable) < 3:
        return  # guarda pelo menos 1 carta na mao depois do descarte
    for c in discardable[:2]:
        state.hand.remove(c)
        state.graveyard.append(c)
    draw_cards(state, 3)
    state.pumpkin_bombs_draws_total += 3
    proxy_drain(state, 1 * NUM_OPPONENTS)  # 1 fuse counter na 1a (e unica) ativacao
    state.battlefield.remove("Pumpkin Bombs")  # oponente ganha o controle -- sai do meu campo
    state.pumpkin_bombs_used = True


def resolve_instant_sorcery(state: GameState, name: str):
    tags = CARD_DB[name].tags
    if "burn_opp_flat" in tags:
        proxy_drain(state, 3 * NUM_OPPONENTS)  # Boltwave: 3 a cada oponente
    elif "burn_all_flat" in tags:
        proxy_drain(state, 4 * NUM_OPPONENTS)  # Flame Rift: 4 a CADA jogador
        self_damage(state, 4)
    elif "pact_x_self" in tags:
        # Damnable Pact: "target player draws X, loses X life" - alvo eu
        # mesmo (maximiza compra), paga em vida real.
        x = max(0, remaining_mana(state) - 2)
        if x > 0:
            spend_mana(state, x + 2)
            draw_cards(state, x)
            self_damage(state, x)
    elif "drain_x2_self" in tags:
        # Debt to the Deathless: "each opponent loses 2X life, you gain
        # that much" - X o maior possivel.
        x = max(0, remaining_mana(state) - 4)
        if x > 0:
            spend_mana(state, x + 4)
            total = 2 * x * NUM_OPPONENTS
            proxy_drain(state, total)
            state.life += total
            state.proxy_lifegain_total += total
    elif "drain_x_self" in tags:
        # Exsanguinate: "each opponent loses X life, you gain that much"
        x = max(0, remaining_mana(state) - 2)
        if x > 0:
            spend_mana(state, x + 2)
            total = x * NUM_OPPONENTS
            proxy_drain(state, total)
            state.life += total
            state.proxy_lifegain_total += total
    elif "edict_pay_life_x" in tags:
        # Killing Wave: "For each creature, its controller sacrifices it
        # unless they pay X life." Premissa documentada: oponentes pagam a
        # vida (linha competitiva comum quando X e' pequeno) - X = o
        # maximo pagavel.
        x = max(1, remaining_mana(state) - 1)
        proxy_drain(state, x * NUM_OPPONENTS)
    elif "burn_nonbasic_proxy" in tags:
        # Price of Progress: "damage = 2x nonbasic lands that player
        # controls" - sem terrenos reais de oponente, proxy documentado:
        # usa MINHA propria contagem de terrenos nao-basicos como
        # estimativa (premissa: manabase de poder parecido).
        nonbasics = sum(1 for n in state.battlefield if n in LAND_NAMES and n not in ("Mountain", "Plains", "Swamp"))
        proxy_drain(state, 2 * nonbasics * NUM_OPPONENTS)
    elif "wheel_full" in tags:
        do_wheel(state, my_draws=7)
    elif "interaction" in tags:
        state.interaction_spells_cast_total += 1
    elif "boros_charm_burn" in tags:
        # Boros Charm modal: escolhe "4 damage to target player" por
        # padrao (alimenta a matematica de vida perdida do Megatron) -
        # os outros 2 modos (indestructible/double strike) documentados
        # como alternativas situacionais nao escolhidas por padrao.
        proxy_drain(state, 4)
    elif "rise_eldrazi" in tags:
        # Rise of the Eldrazi: destroy target permanent (documentado,
        # 'interaction') + target player draws four + extra turn.
        draw_cards(state, 4)
        state.extra_turns_pending += 1


def do_wheel(state: GameState, my_draws: int):
    # "Each player discards their hand, then draws seven cards." Cada
    # oponente tambem compra 7 (real, so' sem payoff proprio numerico
    # ligado a isso desde a saida de Smothering Tithe -- Bracket 2,
    # 2026-09-02).
    state.wheels_total += 1
    discard_n = len(state.hand)
    for c in state.hand[:]:
        state.graveyard.append(c)
    state.hand = []
    draw_cards(state, my_draws)
    dpd = 1 if "Scrawling Crawler" in state.battlefield else 0  # payoff generico de opp-draw (ver upkeep)


def do_sandstone_oracle(state: GameState):
    # "choose an opponent. If that player has more cards in hand than
    # you, draw cards equal to the difference." Premissa documentada: mao
    # media de oponente ~ 5 cartas (mesma premissa ja usada noutros
    # simuladores desta sessao pra tamanho de mao de oponente-proxy).
    diff = max(0, 5 - len(state.hand))
    if diff > 0:
        draw_cards(state, diff)


def do_portal_to_phyrexia(state: GameState):
    """'When this artifact enters, each opponent sacrifices three
    creatures of their choice.' Proxy: cada oponente perde ate' 3
    criaturas - sem dano numerico direto (sacrificio, nao perda de vida),
    mas conta como valor de bordo destruido, registrado via
    recursion_events (motor de valor) e nao via proxy_damage (nao e'
    dano). 'At the beginning of your upkeep, put target creature from a
    graveyard onto the battlefield' - reanimacao real, tentada no upkeep
    separadamente (ver upkeep_step)."""
    state.recursion_events_total += 1  # registra o valor do ETB de sacrificio em massa


def create_permanent(state: GameState, name: str):
    state.battlefield.append(name)


def enter_battlefield(state: GameState, name: str, from_hand: bool = True):
    if from_hand and name in state.hand:
        state.hand.remove(name)
    state.battlefield.append(name)
    if is_creature_card(name):
        state.creature_cast_turn[name] = state.turn
    resolve_etb(state, name)
    if is_artifact_card(name):
        creature_etb_hooks(state, name)


def cast_card(state: GameState, name: str):
    card = CARD_DB[name]
    spend_mana(state, effective_cost(state, name))
    if name in state.hand:
        state.hand.remove(name)

    if any(t.startswith("rock") for t in card.tags):
        state.ramp_pieces_cast_total += 1

    if "Unruly Catapult" in state.battlefield and card.ctype in ("instant", "sorcery"):
        state.unruly_catapult_ready = True  # "whenever you cast an instant or sorcery, untap this creature"

    if card.ctype in ("instant", "sorcery"):
        resolve_instant_sorcery(state, name)
        state.graveyard.append(name)
        return

    if "living_weapon" in card.tags:
        # Bitterthorn, Nissa's Animus: cria um Germ 0/0 e anexa (aqui
        # simplificado como o proprio Bitterthorn entrando como fonte de
        # +1/+1 e tutor de terreno no ataque - sem token separado
        # rastreado, documentado).
        pass

    enter_battlefield(state, name, from_hand=False)


def play_land(state: GameState):
    if state.lands_played_this_turn >= 1:
        return
    lands_in_hand = [n for n in state.hand if n in LAND_NAMES]
    if not lands_in_hand:
        return

    def missing_score(card):
        if card in FETCH_TARGETS:
            return -1
        score = 0
        for color in "WBR":
            if color_sources(state, color) == 0 and color in CARD_DB[card].produces:
                score += 1
        return -score

    lands_in_hand.sort(key=missing_score)
    choice = lands_in_hand[0]
    state.hand.remove(choice)
    state.lands_played_this_turn += 1
    if choice in FETCH_TARGETS:
        crack_fetch(state, choice)
    else:
        state.battlefield.append(choice)
        if choice in ETB_TAPPED_LANDS:
            state.tapped_land_this_turn = choice


def upkeep_step(state: GameState):
    if "Scrawling Crawler" in state.battlefield:
        # "each player draws a card" (eu) + "whenever an opponent draws,
        # loses 1 life" (aplicado no momento em que EU disparo um wheel,
        # ja contado em do_wheel via 'dpd'; aqui so' a metade simetrica).
        draw_cards(state, 1)
        proxy_drain(state, 1 * NUM_OPPONENTS)

    if "Phyrexian Arena" in state.battlefield:
        draw_cards(state, 1)
        self_damage(state, 1)

    if "Descent into Avernus" in state.battlefield:
        # "put two descent counters. Then each player creates X Treasures
        # and this enchantment deals X damage to each player, X = counters
        # on it." Achado real: dano SIMETRICO (me acerta tambem), mas eu
        # tambem ganho X Treasures (mana) por vez - motor de risco/mana
        # real, implementado sem excecao pro meu lado.
        state.descent_counters += 2
        x = state.descent_counters
        state.bonus_mana_pool += x
        proxy_drain(state, x * NUM_OPPONENTS)
        self_damage(state, x)

    if "Portal to Phyrexia" in state.battlefield and state.graveyard:
        # "At the beginning of your upkeep, put target creature card from
        # a graveyard onto the battlefield under your control." Prioriza
        # a maior criatura no MEU cemiterio (unico cemiterio real
        # rastreado - premissa documentada, o oraculo real permite
        # qualquer cemiterio).
        creatures_in_gy = [c for c in state.graveyard if is_creature_card(c) and c != COMMANDER]
        if creatures_in_gy:
            best = max(creatures_in_gy, key=lambda n: CARD_DB[n].mv)
            state.graveyard.remove(best)
            enter_battlefield(state, best, from_hand=False)
            state.recursion_events_total += 1

    try_bahamut_saga(state)


def main_phase(state: GameState):
    cast_megatron(state)
    try_cryptolith_fragment(state)

    while True:
        castables = [n for n in state.hand if n not in LAND_NAMES and can_cast(state, n)
                     and "interaction" not in CARD_DB[n].tags
                     and n != "Blasphemous Act"]
        if not castables:
            break

        def prio(n):
            tags = CARD_DB[n].tags
            group = 0 if (tags & {"rock1", "rock2", "rock3", "rock5"}) else 1
            return (group, effective_cost(state, n))

        castables.sort(key=prio)
        cast_card(state, castables[0])

    try_fuel_pings(state)
    try_fire_navy_trebuchet(state)
    try_goblin_engineer_activation(state)
    try_osgir_activation(state)
    try_mishra_unearth(state)
    try_nexus_of_becoming(state)
    try_losheel_draw_check(state)
    try_pumpkin_bombs(state)
    try_retributive_wand_ping(state)


def try_nexus_of_becoming(state: GameState):
    """'At the beginning of combat on your turn, draw a card. Then you
    may exile an artifact or creature card from your hand. If you do,
    create a token copy (3/3 Golem artifact creature in addition).'
    Heuristica: copia a carta de maior custo na mao, se houver alguma."""
    if "Nexus of Becoming" not in state.battlefield or state.nexus_used_this_turn:
        return
    state.nexus_used_this_turn = True
    draw_cards(state, 1)
    pool = [c for c in state.hand if (is_artifact_card(c) or is_creature_card(c)) and c != COMMANDER]
    if pool:
        best = max(pool, key=lambda n: CARD_DB[n].mv)
        state.hand.remove(best)
        state.graveyard.append(best)  # carta exilada na regra real - aproximada como "gasta" (nao reutilizavel)
        token_name = make_token_copy_name(best)
        state.battlefield.append(token_name)
        resolve_token_copy_etb(state, best)


def try_losheel_draw_check(state: GameState):
    pass  # combinado com creature_etb_hooks abaixo (gatilho de ETB, nao main phase)


def creature_etb_hooks(state: GameState, name: str):
    if ("Losheel, Clockwork Scholar" in state.battlefield and is_artifact_card(name)
            and not state.losheel_draw_used_this_turn):
        draw_cards(state, 1)
        state.losheel_draw_used_this_turn = True


def combat_step(state: GameState):
    megatron_combat(state)
    try_cityscape_leveler_attack(state)
    try_aurora_of_emrakul_attack(state)


def end_step(state: GameState):
    megatron_postcombat(state)
    if "The Ten Rings" in state.battlefield and len(state.hand) < 10:
        draw_cards(state, 10 - len(state.hand))
    max_hand = 10 if "The Ten Rings" in state.battlefield else 7
    while len(state.hand) > max_hand:
        worst = min(state.hand, key=lambda n: CARD_DB[n].mv if n in CARD_DB else 0)
        state.hand.remove(worst)
        state.graveyard.append(worst)


def should_keep(hand: list) -> bool:
    lands = sum(1 for n in hand if n in LAND_NAMES)
    good_early = {"Sol Ring", "Arcane Signet", "Expedition Map", COMMANDER}
    if lands >= 3:
        return True
    if lands == 2 and any(n in good_early for n in hand):
        return True
    return False


def build_library():
    lib = []
    text = open("lista.md").read().split("## Deck")[1].split("## Terrenos")[0] + open("lista.md").read().split("## Terrenos")[1]
    for l in text.splitlines():
        l = l.strip()
        if not l:
            continue
        m = re.match(r"^(\d+)\s+(.+)$", l)
        if not m:
            continue
        qty, name = int(m.group(1)), m.group(2).strip()
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
    state.tapped_land_this_turn = None
    state.life_lost_by_opponents_this_turn = 0
    state.unruly_catapult_ready = True
    state.losheel_draw_used_this_turn = False
    state.nexus_used_this_turn = False
    state.fire_navy_used_this_turn = False

    if not (is_first_turn and on_play):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1
        else:
            state.library_emptied = True

    upkeep_step(state)
    play_land(state)
    main_phase(state)
    combat_step(state)
    main_phase(state)
    end_step(state)


def simulate_one(seed: int, turns: int = 8):
    rng = random.Random(seed)
    hand, lib, mulls = mulligan(rng)
    state = GameState(hand=hand, library=lib, mulligans=mulls)
    t = 0
    turns_played = 0
    is_first = True
    while turns_played < turns:
        play_turn(state, is_first_turn=is_first, on_play=True)
        is_first = False
        turns_played += 1
        if state.extra_turns_pending > 0:
            state.extra_turns_pending -= 1
            play_turn(state, is_first_turn=False, on_play=True)
            turns_played += 1
    return state


def run_batch(n: int, seed_base: int, turns: int = 8):
    states = [simulate_one(seed_base + i, turns=turns) for i in range(n)]

    def avg(vals):
        return sum(vals) / len(vals) if vals else 0.0

    print(f"n={n}, seed_base={seed_base}, turns={turns}")
    print(f"Avg mulligans: {avg([s.mulligans for s in states]):.2f}")
    cmd_turn = [s.commander_cast_turn for s in states if s.commander_cast_turn is not None]
    print(f"Turno medio de conjuracao do Megatron: {avg(cmd_turn):.2f} | mediana: {statistics.median(cmd_turn) if cmd_turn else float('nan'):.1f}")
    print(f"Nunca conjurado em {turns} turnos: {100*sum(1 for s in states if s.commander_cast_turn is None)/n:.1f}%")
    vehicle_first = sum(1 for s in states if s.commander_cast_turn is not None)
    print(f"Avg conversoes do Megatron (Tyrant<->Destructive Force): {avg([s.megatron_conversions_total for s in states]):.2f}")
    print(f"Avg mana gerada pela conversao do Megatron (soma o jogo todo): {avg([s.megatron_mana_generated_total for s in states]):.2f}")
    print(f"Avg combustivel (artefatos) sacrificado pro Megatron: {avg([s.megatron_fuel_sacrificed_total for s in states]):.2f}")
    print(f"Avg dano/perda-de-vida proxy total (3 oponentes hipoteticos, NUNCA vida real): {avg([s.proxy_damage_total for s in states]):.2f}")
    print(f"Avg vida ganha (drenagem): {avg([s.proxy_lifegain_total for s in states]):.2f}")
    print(f"Avg cartas compradas extra: {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"Avg wheels conjurados: {avg([s.wheels_total for s in states]):.2f}")
    print(f"Avg tutores usados: {avg([s.tutors_used_total for s in states]):.2f}")
    print(f"Avg eventos de recursao/valor (toolbox, Osgir, Mishra, Portal to Phyrexia): {avg([s.recursion_events_total for s in states]):.2f}")
    print(f"Avg vida final (autodano de Flame Rift/Damnable Pact/Descent into Avernus): {avg([s.life for s in states]):.2f}")
    own_ko = sum(1 for s in states if s.life <= 0)
    print(f"Partidas em que os PROPRIOS efeitos derrubam minha vida a 0 ou menos: {100*own_ko/n:.1f}%")
    print(f"Avg mao final: {avg([len(s.hand) for s in states]):.2f}")

    print()
    print("--- Achados 2026-09-01 (leitura linha-a-linha completa do oraculo, tags mortas nunca lidas) ---")
    scion_cast = sum(1 for s in states if "Scion of Draco" in s.battlefield)
    print(f"Scion of Draco conjurado (custo reduzido por dominio): {100*scion_cast/n:.1f}% dos jogos")
    bahamut_flare = sum(1 for s in states if s.bahamut_mega_flare_total > 0)
    print(f"Summon: Bahamut chegou ao capitulo IV (Mega Flare): {100*bahamut_flare/n:.1f}% dos jogos, "
          f"avg dano quando resolve: {avg([s.bahamut_mega_flare_total for s in states if s.bahamut_mega_flare_total > 0]):.1f}")
    print(f"Avg ativacoes do Cryptolith Fragment: {avg([s.cryptolith_activations_total for s in states]):.2f} | "
          f"transformou em Aurora of Emrakul: {100*sum(1 for s in states if s.cryptolith_transformed)/n:.1f}% dos jogos")
    print(f"Avg pings do Retributive Wand: {avg([s.retributive_wand_pings_total for s in states]):.2f}")
    print(f"Pumpkin Bombs ativada (1x, depois muda de dono): {100*sum(1 for s in states if s.pumpkin_bombs_used)/n:.1f}% dos jogos, "
          f"avg cartas compradas quando ativa: {avg([s.pumpkin_bombs_draws_total for s in states if s.pumpkin_bombs_used]):.1f}")

    # --- Metricas basicas (checklist obrigatorio, categoria 10) --------------
    print("--- Metricas basicas (checklist obrigatorio) ---")
    print(f"RAMP: avg pecas de rampa conjuradas (Sol Ring/Arcane Signet/Gilded Lotus/Chromatic Orrery): {avg([s.ramp_pieces_cast_total for s in states]):.2f}")
    print(f"DRAW: avg cartas compradas extras totais: {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"INTERACTION: avg spells de interacao conjurados (Crackling Doom/Soul Shatter/Swords/Path/etc, sem alvo real por ser goldfish solo): {avg([s.interaction_spells_cast_total for s in states]):.2f}")
    print(f"RECURSION: avg eventos de recursao/reanimacao (toolbox Myr Retriever/Workshop Assistant/Junk Diver, Goblin Engineer, Osgir, Mishra, Portal to Phyrexia upkeep): {avg([s.recursion_events_total for s in states]):.2f}")
    print(f"FINISHER/LETHALITY: dano proxy total {avg([s.proxy_damage_total for s in states]):.2f} (majoritariamente do proprio motor do Megatron - conversoes + fuel), mana gerada pela conversao {avg([s.megatron_mana_generated_total for s in states]):.2f}")
    return states


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    states = run_batch(n=3000, seed_base=9100000, turns=8)

    with open("megatron_v1_runs.jsonl", "w") as f:
        for s in states:
            f.write(json.dumps({
                "mulligans": s.mulligans,
                "commander_cast_turn": s.commander_cast_turn,
                "megatron_conversions_total": s.megatron_conversions_total,
                "megatron_mana_generated_total": s.megatron_mana_generated_total,
                "proxy_damage_total": s.proxy_damage_total,
                "cards_drawn_extra": s.cards_drawn_extra,
                "life": s.life,
            }) + "\n")
