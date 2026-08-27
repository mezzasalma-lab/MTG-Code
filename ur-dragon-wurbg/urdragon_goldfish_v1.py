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

======================================================================
MODELO DE MANA POR COR (2026-08-27) — substitui o modelo generico/total
======================================================================
Reescrito depois de uma auditoria de pips real mostrar que vermelho e
42,7% de toda a demanda de pips do deck mas so 19,8% das fontes (gap de
+23,0pp, o maior desequilibrio ja medido nesta biblioteca) — o modelo
generico anterior era cego a isso (documentado explicitamente como tal
na versao anterior deste docstring). Arquitetura igual ao
thranduil_goldfish_v1.py: `Card.pips: dict[str,int]` (custo colorido
real, INDEPENDENTE de desconto — desconto de custo reduz mana generica,
nunca pips coloridos, regra real) + `Card.produces: frozenset` (cores
que aquele terreno/rock/dork produz) + `color_sources(state, color)`
(conta permanentes em campo cuja `produces` inclui aquela cor) +
`can_cast()` agora checa TANTO mana total quanto fontes de cada cor
pip a pip.

**Fetch lands tratadas com o mecanismo real, nao mais como terreno
generico** (Regra 6 de `references/user-standing-rules.md`, estabelecida
depois de eu ter cometido esse erro no Hei Bai): ao jogar uma fetch,
`crack_fetch()` busca de verdade na biblioteca por um terreno com um dos
2 tipos basicos buscados (cruzando contra `LAND_BASIC_TYPES`, que inclui
os duais/triomes, nao so as basicas) e poe em campo o que resolve a cor
mais escassa no momento — a fetch em si nunca fica em `state.battlefield`
com produces proprio, ela vira o terreno buscado de verdade.

**Fontes tratadas como incolor mesmo tendo "any color"** (mesma
convencao ja usada no Thranduil pra Cavern of Souls/Three Tree City):
Cavern of Souls, Secluded Courtyard, Haven of the Spirit Dragon —
produzem "any color" mas SO pra conjurar criatura do tipo
escolhido/Dragao, uma restricao real demais pra modelar aqui sem
inflar artificialmente a fixacao pro resto do deck (Anguished Unmaking,
Austere Command etc. nao se beneficiam). Tratadas como incolor puro no
`produces` — simplificacao conservadora documentada, nao inventada.
Exotic Orchard e dependente de oponente (imprevisivel) — tambem incolor
aqui, mesma logica de "nao presumir dado nao verificavel" (Regra 1).

**Orb of Dragonkind** ("Add two mana in any combination of colors,
spend only on Dragon spells") continua contribuindo pro total generico
via `dragon_mana_pool` quando o alvo e Dragao (ja implementado antes),
mas NAO conta pra checagem de pip por cor individual — simplificacao
conservadora documentada: como o pool e compartilhado entre ate 2 mana
por turno, deixar ele "cobrir" qualquer cor em qualquer checagem
simultanea inflaria o poder real dele (double-counting entre cores
diferentes na mesma verificacao). Subestima o Orb, nao superestima.

Roaming Throne: tipo escolhido = **Dragon** (obvio e central pro tema,
documentado ainda assim). Dobra qualquer gatilho de criatura Dragao —
inclui o proprio gatilho de ataque da Ur-Dragon (que e ela mesma um
Dragao), os gatilhos de dano-por-Dragao-em-campo (Scourge of Valkas,
Dragon Tempest), os de token (Lathliss, Utvara Hellkite, Miirym), e os
de mana (Klauth, Savage Ventmaw).

Simplificacoes documentadas (nao inventadas — omissoes explicitas):
- Klauth/Savage Ventmaw (mana no ataque): X = poder total dos
  atacantes — aproximado como poder do proprio Dragao que ataca (sem
  modelar poder exato de toda a equipe), documentado. A mana gerada
  entra no pool generico (`bonus_mana_pool`), sem cor especifica
  atribuida (real: "add X mana in any combination of colors" — aqui
  simplificado pra generico, nao pip a pip, documentado).
- Ramos, Dragon Engine: contadores por spell conjurada rastreados de
  forma simplificada (+1 contador fixo por spell, nao por numero de
  cores exatas de cada uma), pra nao exigir rastrear cores pip a pip
  de CADA spell conjurada (so das cartas do proprio CARD_DB).
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

@dataclass
class Card:
    name: str
    mv: int
    ctype: str
    tags: frozenset = field(default_factory=frozenset)
    power: int = 0
    pips: dict = field(default_factory=dict)          # custo colorido real (nunca reduzido por desconto)
    produces: frozenset = field(default_factory=frozenset)  # cores que este terreno/rock/dork produz


CARD_DB: dict[str, Card] = {}


def add(name, mv, ctype, tags=(), power=0, pips=None, produces=None):
    CARD_DB[name] = Card(name=name, mv=mv, ctype=ctype, tags=frozenset(tags), power=power,
                          pips=dict(pips or {}), produces=frozenset(produces or ()))


COMMANDER = "The Ur-Dragon"
add(COMMANDER, 9, "creature", {"commander", "dragon", "roaming_throne_type"}, power=9,
    pips={"W": 1, "U": 1, "B": 1, "R": 1, "G": 1})

ROAMING_THRONE_TYPE = "dragon"

# --- Terrenos (36) — produces real por carta (auditoria de pips 2026-08-27) -----
FETCH_TARGETS = {
    "Arid Mesa": {"Mountain", "Plains"},
    "Bloodstained Mire": {"Swamp", "Mountain"},
    "Marsh Flats": {"Plains", "Swamp"},
    "Misty Rainforest": {"Forest", "Island"},
    "Windswept Heath": {"Forest", "Plains"},
    "Wooded Foothills": {"Mountain", "Forest"},
}
for n in FETCH_TARGETS:
    add(n, 0, "land", {"fetch"})  # produces vazio de proposito: vira o terreno buscado de verdade (crack_fetch)

LAND_PRODUCES = {
    "Ancient Tomb": set(),               # incolor (2 mana, sem cor)
    "Bayou": {"B", "G"},
    "Blood Crypt": {"B", "R"},
    "Breeding Pool": {"G", "U"},
    "Cavern of Souls": set(),            # produces "base" = incolor; "any color" real pra creature spell Dragao tratado a parte (DRAGON_ANY_COLOR_LANDS, color_sources)
    "Command Tower": set("WUBRG"),
    "Exotic Orchard": set(),             # dependente de oponente, nao presumido (Regra 1)
    "Godless Shrine": {"W", "B"},
    "Hallowed Fountain": {"W", "U"},
    "Haven of the Spirit Dragon": set(), # idem Cavern — "any color" real pra Dragon creature spell tratado a parte
    "Jetmir's Garden": {"W", "R", "G"},
    "Ketria Triome": {"G", "U", "R"},
    "Overgrown Tomb": {"B", "G"},
    "Path of Ancestry": set("WUBRG"),
    "Sacred Foundry": {"R", "W"},
    "Savannah": {"W", "G"},
    "Secluded Courtyard": set(),         # idem Cavern — "any color" real pra creature spell do tipo escolhido tratado a parte
    "Steam Vents": {"R", "U"},
    "Stomping Ground": {"R", "G"},
    "Taiga": {"R", "G"},
    "Temple Garden": {"W", "G"},
    "Tropical Island": {"G", "U"},
    "Watery Grave": {"B", "U"},
    "Zagoth Triome": {"B", "G", "U"},
    "Ziatora's Proving Ground": {"B", "R", "G"},
    "Forest": {"G"}, "Island": {"U"}, "Swamp": {"B"}, "Mountain": {"R"}, "Plains": {"W"},
}
for n, colors in LAND_PRODUCES.items():
    add(n, 0, "land", set(), produces=colors)

# Correcao real 2026-08-27 (usuario apontou: "elas geram mana de qualquer
# cor para o tipo de criatura escolhida (Dragao)" — eu tinha essas 3
# tratadas como puramente incolores, um erro de simplificacao real demais.
# Oraculo conferido via Scryfall:
#   Cavern of Souls: "As this land enters, choose a creature type. {T}: Add
#   {C}. {T}: Add one mana of any color. Spend this mana only to cast a
#   creature spell of the chosen type, and that spell can't be countered."
#   Secluded Courtyard: mesma estrutura (sem o "can't be countered"), tambem
#   cobre ativar habilidade de creature source do tipo escolhido.
#   Haven of the Spirit Dragon: fixo em Dragao, sem escolha: "{T}: Add one
#   mana of any color. Spend this mana only to cast a Dragon creature
#   spell."
# Nesse deck o tipo escolhido em Cavern/Courtyard e obviamente Dragao (comandante
# e ~20 Dragoes na lista) — nao e generico "qualquer cor pra qualquer spell"
# (por isso continuam produces=set() acima, correto pro caso geral), mas E
# real e nada desprezivel: 21 criaturas Dragao no deck carregam 49% de TODOS
# os pips coloridos do deck (70,7% da demanda de R especificamente). Checado
# a parte em color_sources()/has_color_sources_for(), nao no produces geral,
# pra nao inflar fixacao pra spells nao-Dragao (Anguished Unmaking, Austere
# Command, Farseek, Sol Ring etc. continuam sem se beneficiar dessas 3 —
# real, o oraculo restringe a "creature spell").
DRAGON_ANY_COLOR_LANDS = {"Cavern of Souls", "Secluded Courtyard", "Haven of the Spirit Dragon"}

# Karplusan Forest: NAO esta na lista.md — cadastrada so pra permitir o
# teste comparativo de troca de Watery Grave (candidato de corte real,
# unica terra cujas 2 cores sao as mais sobre-representadas frente a
# demanda de pips: U -11,2pp, B -10,4pp) por uma fonte de R/G (as 2 mais
# sub-representadas). Oraculo real: "{T}: Add {C}. / {T}: Add {R} or
# {G}. This land deals 1 damage to you." — sem tapped, untapped de
# verdade.
add("Karplusan Forest", 0, "land", set(), produces={"R", "G"})

# Battlefield Forge: NAO esta na lista.md — cadastrada pra testar o 2o
# corte de B/U (candidato: Island, U puro, a cor com o pior gap depois
# de R). Diversifica de proposito em vez de dobrar R/G com a Karplusan —
# cobre R (o maior gap, +23,0pp) e W (+7,0/+8,6pp), sem inflar mais
# ainda verde (que ja tem o menor gap dos 3 sub-representados). Oraculo
# real: "{T}: Add {C}. / {T}: Add {R} or {W}. This land deals 1 damage
# to you." — sem tapped.
add("Battlefield Forge", 0, "land", set(), produces={"R", "W"})

# Talisman of Impulse: NAO esta na lista.md — cadastrada pra testar corte
# de rock/dork de R/G (pedido do usuario 2026-08-27, seguindo a auditoria
# de pips: vermelho +23,0pp, verde +5,5pp). Oraculo real: "{T}: Add {C}.
# / {T}: Add {R} or {G}. This artifact deals 1 damage to you."
add("Talisman of Impulse", 2, "artifact", {"rock1"}, produces={"R", "G"})

# Ruby, Daring Tracker: NAO esta na lista.md — mesmo motivo. Oraculo real
# (Scryfall, 2026-08-27): "{R}{G}, Legendary Creature — Human Scout, 1/2.
# Haste. Whenever Ruby attacks while you control a creature with power 4
# or greater, Ruby gets +2/+2 until end of turn. {T}: Add {R} or {G}."
add("Ruby, Daring Tracker", 2, "creature", {"dork_flat1", "haste"}, pips={"R": 1, "G": 1}, produces={"R", "G"})

# LAND_BASIC_TYPES: tipos basicos reais de cada terreno nao-fetch, usado por
# crack_fetch() pra achar todo alvo que compartilha um dos 2 tipos buscados
# pela fetch (nao so as basicas — Regra 6, achado real no Hei Bai: uma fetch
# alcanca qualquer dual/triome que carregue o tipo, nao so o par nomeado).
LAND_BASIC_TYPES = {
    "Bayou": {"Forest", "Swamp"}, "Blood Crypt": {"Mountain", "Swamp"},
    "Breeding Pool": {"Forest", "Island"}, "Forest": {"Forest"},
    "Godless Shrine": {"Plains", "Swamp"}, "Hallowed Fountain": {"Plains", "Island"},
    "Island": {"Island"}, "Jetmir's Garden": {"Plains", "Forest", "Mountain"},
    "Ketria Triome": {"Island", "Forest", "Mountain"}, "Mountain": {"Mountain"},
    "Overgrown Tomb": {"Forest", "Swamp"}, "Plains": {"Plains"},
    "Sacred Foundry": {"Plains", "Mountain"}, "Savannah": {"Plains", "Forest"},
    "Steam Vents": {"Island", "Mountain"}, "Stomping Ground": {"Forest", "Mountain"},
    "Swamp": {"Swamp"}, "Taiga": {"Forest", "Mountain"}, "Temple Garden": {"Plains", "Forest"},
    "Tropical Island": {"Forest", "Island"}, "Watery Grave": {"Island", "Swamp"},
    "Zagoth Triome": {"Forest", "Island", "Swamp"},
    "Ziatora's Proving Ground": {"Forest", "Mountain", "Swamp"},
}

# --- Ramp (busca terreno real) --------------------------------------------------
add("Cultivate", 3, "sorcery", {"land_tutor2"}, pips={"G": 1})
add("Farseek", 2, "sorcery", {"land_tutor1"}, pips={"G": 1})
add("Kodama's Reach", 3, "sorcery", {"land_tutor2"}, pips={"G": 1})
add("Nature's Lore", 2, "sorcery", {"land_tutor1"}, pips={"G": 1})
add("Three Visits", 2, "sorcery", {"land_tutor1"}, pips={"G": 1})
add("Skyshroud Claim", 4, "sorcery", {"land_tutor2_direct"}, pips={"G": 1})
add("Birds of Paradise", 1, "creature", {"dork_flat1"}, pips={"G": 1}, produces=set("WUBRG"))
add("Delighted Halfling", 1, "creature", {"dork_flat1"}, produces=set("WUBRG"))
add("Arcane Signet", 2, "artifact", {"rock1"}, produces=set("WUBRG"))
add("Sol Ring", 1, "artifact", {"rock2"})  # {C}{C} — sem cor

# --- Custo de Dragao / tutores -------------------------------------------------
add("Dragonlord's Servant", 2, "creature", {"dragon_discount1"}, pips={"R": 1})
add("Dragonspeaker Shaman", 3, "creature", {"dragon_discount2"}, pips={"R": 2})
add("Sarkhan, Soul Aflame", 3, "creature", {"dragon_discount1"}, pips={"U": 1, "R": 1})
add("Herald's Horn", 3, "artifact", {"dragon_discount1", "tribal_impulse"})
add("Sarkhan's Triumph", 3, "instant", {"dragon_tutor_hand"}, pips={"R": 1})
add("Orb of Dragonkind", 2, "artifact", {"dragon_tutor_sac"}, pips={"R": 1})
add("Urza's Incubator", 3, "artifact", {"dragon_discount2"})

# --- Dragoes com gatilho real ----------------------------------------------------
add("Ancient Copper Dragon", 6, "creature", {"dragon", "combat_treasure_d20"}, power=6, pips={"R": 2})
add("Ancient Gold Dragon", 7, "creature", {"dragon", "combat_token_d20"}, power=7, pips={"W": 2})
add("Atarka, World Render", 7, "creature", {"dragon", "attack_double_strike"}, power=7, pips={"R": 1, "G": 1})
add("Balefire Dragon", 7, "creature", {"dragon", "combat_wipe_proxy"}, power=6, pips={"R": 2})
add("Bladewing the Risen", 7, "creature", {"dragon", "reanimate_dragon_etb"}, power=6, pips={"B": 2, "R": 2})
add("Dragon Broodmother", 6, "creature", {"dragon", "upkeep_dragon_token"}, power=4, pips={"R": 3, "G": 1})
add("Dragonlord Dromoka", 6, "creature", {"dragon"}, power=4, pips={"G": 1, "W": 1})
add("Goldspan Dragon", 5, "creature", {"dragon", "attack_treasure", "goldspan", "haste"}, power=4, pips={"R": 2})
add("Hellkite Charger", 6, "creature", {"dragon", "extra_combat_paid", "haste"}, power=6, pips={"R": 2})
add("Hellkite Courser", 6, "creature", {"dragon"}, power=4, pips={"R": 2})
add("Klauth, Unrivaled Ancient", 7, "creature", {"dragon", "attack_mana_power", "haste"}, power=7, pips={"R": 1, "G": 1})
add("Lathliss, Dragon Queen", 6, "creature", {"dragon", "dragon_etb_token"}, power=6, pips={"R": 2})
add("Miirym, Sentinel Wyrm", 6, "creature", {"dragon", "dragon_etb_copy"}, power=3, pips={"G": 1, "U": 1, "R": 1})
add("Old Gnawbone", 7, "creature", {"dragon"}, power=7, pips={"G": 2})
add("Ramos, Dragon Engine", 6, "artifact_creature", {"dragon", "ramos_counters"}, power=2)
add("Savage Ventmaw", 6, "creature", {"dragon", "attack_mana_flat"}, power=5, pips={"R": 1, "G": 1})
add("Scourge of Valkas", 5, "creature", {"dragon", "dragon_etb_damage"}, power=4, pips={"R": 3})
add("Terror of the Peaks", 5, "creature", {"creature_etb_damage_power"}, power=4, pips={"R": 2})
add("Twinflame Tyrant", 5, "creature", {"dragon", "damage_doubler"}, power=4, pips={"R": 2})
add("Utvara Hellkite", 8, "creature", {"dragon"}, power=6, pips={"R": 2})

# --- Outras criaturas / suporte tribal --------------------------------------------
add("Dragon Tempest", 2, "enchantment", {"dragon_etb_damage"}, pips={"R": 1})
add("Magda, Brazen Outlaw", 2, "creature", {"treasure_tutor_dragon"}, pips={"R": 1})
# Firdoch Core: Kindred Artifact — Shapeshifter, Changeling ("This card is
# every creature type") — tem o tipo Dragao em toda zona, inclusive como
# spell. Bug real corrigido em 2026-08-23 (achado pelo usuario): faltava a
# tag 'dragon', entao nunca pegava desconto de Eminence/Dragonlord's
# Servant/Dragonspeaker Shaman/Sarkhan Soul Aflame (todas dizem "Dragon
# spells", nao exigem carta de criatura) nem disparava dragon_enters()
# (Scourge of Valkas/Dragon Tempest/Miirym/Lathliss reagem a QUALQUER
# Dragao entrando, criatura ou nao). Continua sendo Artifact, nao Creature,
# ate pagar {4} pra animar (nao modelado — ver docstring do arquivo) —
# entao is_creature_card() continua False pra ele, o que corretamente o
# exclui de Herald's Horn/Urza's Incubator (essas exigem "Creature
# spells... of the chosen type" de verdade). {3} sem pip colorido no custo,
# real ({T}: Add one mana of any color).
add("Firdoch Core", 3, "artifact", {"dork_flat1_any", "dragon"}, produces=set("WUBRG"))

# Radagast of Rhosgobel: NAO esta na lista.md — cadastrado so pra permitir
# o teste comparativo `urdragon_radagast_test.py`. {2}{G}{G}, verde real
# (colors=['G']), NAO e Dragao (Avatar Wizard — nao participa de
# dragon_discount_self/others nem de dragon_enters()). Oraculo real: "The
# first creature spell you cast each turn costs {2} less to cast and can
# be cast as though it had flash."
add("Radagast of Rhosgobel", 4, "creature", {"first_creature_discount"}, pips={"G": 2})

# --- Draw engines de poder / spells caras -----------------------------------------
add("Elemental Bond", 3, "enchantment", {"power3_draw"}, pips={"G": 1})
add("Garruk's Uprising", 3, "enchantment", {"power4_draw"}, pips={"G": 1})
add("Temur Ascendancy", 3, "enchantment", {"power4_draw_optional"}, pips={"G": 1, "U": 1, "R": 1})
add("The Great Henge", 9, "artifact", {"nontoken_etb_counter_draw", "cost_reduce_power"}, pips={"G": 2})
add("Up the Beanstalk", 2, "enchantment", {"bigspell_draw"}, pips={"G": 1})
add("Return of the Wildspeaker", 5, "instant", {"power_draw_instant"}, pips={"G": 1})
add("Sylvan Library", 2, "enchantment", {"card_selection"}, pips={"G": 1})

# --- Removal / interacao / protecao -----------------------------------------------
add("An Offer You Can't Refuse", 2, "instant", {"interaction"}, pips={"U": 1})
add("Anguished Unmaking", 3, "instant", {"interaction"}, pips={"W": 1, "B": 1})
add("Arcane Denial", 2, "instant", {"interaction"}, pips={"U": 1})
add("Assassin's Trophy", 2, "instant", {"interaction"}, pips={"B": 1, "G": 1})
add("Austere Command", 6, "sorcery", {"wipe"}, pips={"W": 2})
add("Beast Within", 3, "instant", {"interaction"}, pips={"G": 1})
add("Crux of Fate", 5, "sorcery", {"wipe"}, pips={"B": 2})
add("Heroic Intervention", 2, "instant", {"interaction"}, pips={"G": 1})
add("Lightning Greaves", 2, "artifact", {"interaction"})
add("Rhythm of the Wild", 2, "enchantment", {"riot"}, pips={"R": 1, "G": 1})
add("Smothering Tithe", 4, "enchantment", {"opponent_dependent"}, pips={"W": 1})
add("Swan Song", 1, "instant", {"interaction"}, pips={"U": 1})
add("Swords to Plowshares", 1, "instant", {"interaction"}, pips={"W": 1})
add("Teferi's Protection", 3, "instant", {"interaction"}, pips={"W": 1})
add("Haunting Voyage", 6, "sorcery", {"mass_reanimate"}, pips={"B": 2})
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


# Achado em 2026-08-27 (mesma classe de bug que a tag morta da Magda):
# "haste_all" (Temur Ascendancy) e "haste_flying" (Dragon Tempest) existiam
# como tags decorativas desde que essas cartas entraram no CARD_DB, mas
# ready_creatures() nunca as checava — so olhava a tag "haste" na propria
# criatura. Oraculo real conferido via Scryfall:
#   Temur Ascendancy: "Creatures you control have haste." (estatico, todas)
#   Dragon Tempest: "Whenever a creature you control with flying enters, it
#   gains haste until end of turn." (so no turno em que entra, so voadoras)
# Todos os Dragoes do deck (e Birds of Paradise) tem Flying real — conferido
# carta a carta via oraculo, nao assumido por serem Dragoes.
FLYING_CREATURES = {
    "The Ur-Dragon", "Birds of Paradise", "Ancient Copper Dragon",
    "Ancient Gold Dragon", "Atarka, World Render", "Balefire Dragon",
    "Bladewing the Risen", "Dragon Broodmother", "Dragonlord Dromoka",
    "Goldspan Dragon", "Hellkite Charger", "Hellkite Courser",
    "Klauth, Unrivaled Ancient", "Lathliss, Dragon Queen",
    "Miirym, Sentinel Wyrm", "Old Gnawbone", "Savage Ventmaw",
    "Scourge of Valkas", "Terror of the Peaks", "Twinflame Tyrant",
    "Utvara Hellkite",
}


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
    mana_spent_this_turn: int = 0
    bonus_mana_pool: int = 0
    dragon_mana_pool: int = 0
    orb_dragonkind_used_this_turn: bool = False
    first_creature_used_this_turn: bool = False
    first_creature_discount_events_total: int = 0
    dragon_tokens: int = 0
    other_tokens: int = 0
    ramos_counters: int = 0
    magda_treasures: int = 0
    magda_tutors_total: int = 0
    dragons_free_entry_total: int = 0

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
    orb_mana_activations_total: int = 0
    library_emptied: bool = False
    color_screw_turns: int = 0          # turnos em que havia mana total mas faltou a cor certa pra algo na mao
    first_color_screw_turn: Optional[int] = None
    fetches_cracked_total: int = 0


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
# Mana — modelo por cor (2026-08-27)
# ---------------------------------------------------------------------------

def ready_creatures(state: GameState):
    """Bug real corrigido em 2026-08-27 (achado ao registrar Ruby, Daring
    Tracker pra teste, que tem haste real): Hellkite Charger, Klauth e
    Goldspan Dragon TAMBEM tem 'Flying, haste' no oraculo real, mas nunca
    tinham sido marcadas — ficavam presas pela doenca de invocacao tanto
    pra atacar quanto pra ativar habilidades de mana, quando o texto real
    remove essa restricao. Criaturas tagueadas 'haste' ignoram o gate de
    turno de conjuracao (real: haste remove summoning sickness tanto pra
    atacar quanto pra ativar {T}).

    Segundo bug real corrigido no mesmo dia (mesma classe da tag morta da
    Magda): "haste_all" (Temur Ascendancy, estatico pra qualquer criatura)
    e "haste_flying" (Dragon Tempest, so pras que tem flying, so no turno
    em que entram) existiam como tags decorativas desde que essas cartas
    foram registradas — nunca eram checadas aqui."""
    temur_ascendancy = "Temur Ascendancy" in state.battlefield
    dragon_tempest = "Dragon Tempest" in state.battlefield

    def is_ready(n):
        if "haste" in CARD_DB[n].tags:
            return True
        if state.creature_cast_turn.get(n, -1) < state.turn:
            return True
        if temur_ascendancy:
            return True
        if dragon_tempest and has_flying(n) and state.creature_cast_turn.get(n, -1) == state.turn:
            return True
        return False

    return [n for n in state.battlefield if is_creature_card(n) and is_ready(n)]


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


def color_sources(state: GameState, color: str, dragon_creature_spell: bool = False) -> int:
    """Conta fontes de mana em campo que produzem `color` — terrenos
    incondicionalmente, rocks/dorks so se prontos (sem doenca de invocacao,
    mesmo gate ja usado em dork_mana). Sol Ring/Ancient Tomb/etc contribuem
    pro total generico mas NUNCA aqui (produces vazio), documentado em cada
    entrada do CARD_DB.

    Cavern of Souls/Secluded Courtyard/Haven of the Spirit Dragon (correcao
    real 2026-08-27): produces vazio no CARD_DB (correto pro caso geral),
    mas SE `dragon_creature_spell=True` (a carta sendo conjurada e um
    Dragao de verdade) elas contam como fonte de QUALQUER cor — oraculo
    real, tipo escolhido = Dragao nesse deck."""
    n = 0
    ready = set(ready_creatures(state))
    for card in state.battlefield:
        base = card.split(" (copia)")[0]
        if base not in CARD_DB:
            continue
        c = CARD_DB[base]
        produces = set("WUBRG") if (dragon_creature_spell and base in DRAGON_ANY_COLOR_LANDS) else c.produces
        if color not in produces:
            continue
        if is_creature_card(base) and card not in ready and base not in LAND_NAMES:
            continue
        n += 1
    return n


def remaining_mana_for(state: GameState, name: str) -> int:
    """Mana disponivel considerando o pool restrito da Orb of Dragonkind
    ('{1}, {T}: Add two mana in any combination of colors. Spend this mana
    only to cast Dragon spells or activate abilities of Dragons') — soma ao
    pool generico SO quando a carta em questao e um Dragao. O texto real NAO
    tem qualificador 'other', entao vale pra propria Ur-Dragon tambem (ela e
    Legendary Creature — Dragon Avatar) — bug real corrigido em 2026-08-23
    junto com dragon_discount_self()/dragon_discount_others() abaixo (essa
    funcao antes excluia a comandante sem base no oraculo)."""
    base = remaining_mana(state)
    if is_dragon(name):
        base += state.dragon_mana_pool
    return base


def has_color_sources_for(state: GameState, name: str) -> bool:
    """Checa pips coloridos reais (independentes de desconto de custo —
    'costs {1} less' reduz mana generica, nunca pip colorido, regra real).
    Orb of Dragonkind NAO conta aqui por simplificacao conservadora
    documentada (ver docstring do arquivo).

    Passa dragon_creature_spell=True pra color_sources quando `name` e um
    Dragao de verdade (creature, tag dragon) — libera Cavern of
    Souls/Secluded Courtyard/Haven of the Spirit Dragon como fonte de
    qualquer cor so nesse caso (correcao real 2026-08-27)."""
    pips = CARD_DB[name].pips
    dragon_creature = is_dragon(name) and is_creature_card(name)
    for color, needed in pips.items():
        if color_sources(state, color, dragon_creature_spell=dragon_creature) < needed:
            return False
    return True


def dragon_discount_self(state: GameState) -> int:
    """Desconto aplicavel a PROPRIA Ur-Dragon sendo conjurada — soma so as
    fontes cujo oraculo real NAO tem qualificador 'other': Dragonlord's
    Servant ('Dragon spells you cast cost {1} less'), Dragonspeaker Shaman
    ('... {2} less'), Sarkhan Soul Aflame ('... {1} less'), Herald's Horn
    ('Creature spells you cast of the chosen type cost {1} less'),
    Urza's Incubator ('Creature spells of the chosen type cost {2}
    less'). NAO inclui a Eminence da propria comandante, que diz
    explicitamente 'OTHER Dragon spells you cast' — nunca desconta a si
    mesma. Bug real corrigido em 2026-08-23: o script excluia a comandante
    de TODOS os 6 redutores (inclusive esses 5 sem 'other' no texto),
    quando so a Eminence deveria excluir."""
    d = 0
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


def dragon_discount_others(state: GameState, name: str) -> int:
    """Desconto aplicavel a QUALQUER outro Dragao (nao a comandante).
    Eminence da propria Ur-Dragon ('As long as The Ur-Dragon is in the
    command zone or on the battlefield, other Dragon spells you cast cost
    {1} less') + Dragonlord's Servant/Dragonspeaker Shaman/Sarkhan Soul
    Aflame ('Dragon spells you cast cost less') SEMPRE se aplicam a
    qualquer spell com o tipo de criatura Dragao, seja carta de criatura
    ou nao. Ja Herald's Horn/Urza's Incubator dizem 'Creature spells... of
    the chosen type' — EXIGEM carta de criatura de verdade."""
    d = 1  # Eminence, sempre ativa
    if "Dragonlord's Servant" in state.battlefield:
        d += 1
    if "Dragonspeaker Shaman" in state.battlefield:
        d += 2
    if "Sarkhan, Soul Aflame" in state.battlefield:
        d += 1
    if is_creature_card(name):
        if "Herald's Horn" in state.battlefield:
            d += 1
        if "Urza's Incubator" in state.battlefield:
            d += 2
    return d


def effective_cost(state: GameState, name: str) -> int:
    """Custo generico total, JA com desconto — pips coloridos ficam de
    fora dessa conta de proposito (checados a parte em
    has_color_sources_for, porque desconto de custo NUNCA reduz pip
    colorido, so mana generica — regra real)."""
    mv = CARD_DB[name].mv
    if name == "The Great Henge":
        powers = [CARD_DB[n].power for n in state.battlefield if is_creature_card(n)]
        x = max(powers) if powers else 0
        return max(0, mv - x)
    first_creature_d = 0
    if (is_creature_card(name) and "Radagast of Rhosgobel" in state.battlefield
            and not state.first_creature_used_this_turn):
        first_creature_d = 2
    if name == COMMANDER:
        return max(0, mv - dragon_discount_self(state) - first_creature_d)
    if is_dragon(name):
        return max(0, mv - dragon_discount_others(state, name) - first_creature_d)
    return max(0, mv - first_creature_d)


def can_cast(state: GameState, name: str) -> bool:
    if remaining_mana_for(state, name) < effective_cost(state, name):
        return False
    return has_color_sources_for(state, name)


def spend_mana(state: GameState, n: int):
    state.mana_spent_this_turn += n


# ---------------------------------------------------------------------------
# Fetch lands — mecanismo real (Regra 6)
# ---------------------------------------------------------------------------

def crack_fetch(state: GameState, fetch_name: str):
    """Sacrifica a fetch (ja removida da mao em play_land), busca de
    verdade na biblioteca um terreno com um dos 2 tipos basicos buscados
    (cruzando contra LAND_BASIC_TYPES — inclui duais/triomes, nao so
    basicas), poe em campo o que resolve a cor mais escassa AGORA. Sem
    'tapped' no oraculo real dessas 6 fetches (Arid Mesa etc.), entra
    destravado."""
    searched = FETCH_TARGETS[fetch_name]
    candidates = [n for n in state.library if n in LAND_BASIC_TYPES and (LAND_BASIC_TYPES[n] & searched)]
    if not candidates:
        return  # sem alvo (nao deveria acontecer com esta manabase, mas nao trava o jogo)

    def score(land):
        colors = CARD_DB[land].produces
        if not colors:
            return 99
        return min(color_sources(state, c) for c in colors)

    candidates.sort(key=score)
    pick = candidates[0]
    state.library.remove(pick)
    state.battlefield.append(pick)
    state.fetches_cracked_total += 1


# ---------------------------------------------------------------------------
# Resolucao de ETB / cast
# ---------------------------------------------------------------------------

def create_treasures(state: GameState, n: int):
    state.treasures_created_total += n
    state.bonus_mana_pool += 0  # tesouros so viram mana quando sacrificados (nao modelado tick a tick; ver create_and_spend_treasures)


def create_and_use_treasures(state: GameState, n: int):
    """Cria e imediatamente converte em mana disponivel neste turno —
    aproximacao real (o deck nao tem motivo pra segurar Treasure parado).
    Goldspan Dragon: 'Treasures you control have "{T}, Sacrifice this
    artifact: Add two mana of any one color."' — com Goldspan em campo,
    todo Treasure vale 2 mana, nao 1. Entra no pool generico (a cor do
    Treasure e escolhida livremente no jogo real, nao modelado pip a pip
    aqui — simplificacao documentada, mesma logica do Klauth/Savage
    Ventmaw)."""
    state.treasures_created_total += n
    per_treasure = 2 if "Goldspan Dragon" in state.battlefield else 1
    state.bonus_mana_pool += n * per_treasure


def resolve_etb(state: GameState, name: str):
    tags = CARD_DB[name].tags

    if name == "Bladewing the Risen":
        targets = [c for c in state.graveyard if is_dragon(c)]
        if targets:
            best = max(targets, key=lambda n: CARD_DB[n].mv)
            state.graveyard.remove(best)
            enter_battlefield(state, best, from_hand=False)
            state.dragons_free_entry_total += 1

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
    elif "mass_reanimate" in tags:
        # Haunting Voyage: "Choose a creature type. Return up to two
        # creature cards of that type from your graveyard to the
        # battlefield." (tipo = Dragao, obvio nesse deck). NAO modela o
        # modo foretold ("return ALL" — custo/timing de 2 turnos
        # separado, {2} pra exilar + {5}{B}{B} depois — fora de escopo
        # aqui, mesma simplificacao conservadora documentada de outras
        # cartas complexas). Achado real 2026-08-27: essa tag nunca tinha
        # sido checada em lugar nenhum — Haunting Voyage era 6 mana que
        # nao faziam nada no simulador.
        targets = sorted([c for c in state.graveyard if is_dragon(c) and is_creature_card(c)],
                          key=lambda n: CARD_DB[n].mv, reverse=True)[:2]
        for t in targets:
            state.graveyard.remove(t)
            enter_battlefield(state, t, from_hand=False)
            state.dragons_free_entry_total += 1


def do_orb_dragonkind(state: GameState):
    """Orb of Dragonkind: '{1}, {T}: Add two mana in any combination of
    colors. Spend this mana only to cast Dragon spells or activate
    abilities of Dragons.' + '{R}, {T}, Sacrifice this artifact: look at
    top 7, pode revelar um Dragao e por na mao.' Duas habilidades
    mutuamente exclusivas no mesmo turno (a segunda sacrifica o artefato).
    Prioridade: usa a mana se ha Dragao na mao pra aproveitar (repetivel,
    mais valioso a longo prazo); so sacrifica pelo tutor se nao ha Dragao
    nenhum na mao."""
    if "Orb of Dragonkind" not in state.battlefield or state.orb_dragonkind_used_this_turn:
        return
    if remaining_mana(state) < 1:
        return
    dragons_in_hand = [n for n in state.hand if is_dragon(n)]
    if dragons_in_hand:
        spend_mana(state, 1)
        state.dragon_mana_pool += 2
        state.orb_mana_activations_total += 1
    else:
        pool = [n for n in state.library if is_dragon(n)]
        if not pool:
            return
        best = max(pool, key=lambda n: CARD_DB[n].mv)
        state.library.remove(best)
        state.hand.append(best)
        spend_mana(state, 1)
        state.battlefield.remove("Orb of Dragonkind")
        state.tutors_used_total += 1
    state.orb_dragonkind_used_this_turn = True


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
    if is_creature_card(name) and not state.first_creature_used_this_turn:
        if "Radagast of Rhosgobel" in state.battlefield:
            state.first_creature_discount_events_total += 1
        state.first_creature_used_this_turn = True
    if name == COMMANDER:
        if state.dragon_mana_pool > 0:
            use = min(cost, state.dragon_mana_pool)
            state.dragon_mana_pool -= use
            cost -= use
        spend_mana(state, cost + 2 * state.commander_cast_count)
    else:
        if is_dragon(name) and state.dragon_mana_pool > 0:
            use = min(cost, state.dragon_mana_pool)
            state.dragon_mana_pool -= use
            cost -= use
        spend_mana(state, cost)
    if name != COMMANDER:
        state.hand.remove(name)

    if "Ramos, Dragon Engine" in state.battlefield and name != "Ramos, Dragon Engine":
        state.ramos_counters += 1

    if name in LAND_NAMES:
        state.battlefield.append(name)
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

    # prioriza terreno que resolve a cor mais escassa em campo (mesma
    # logica do Thranduil) — entre fetches e terrenos diretos, uma fetch
    # SEMPRE pode alcancar a cor mais escassa (todas as 6 alcancam as 5
    # cores nesta manabase, auditado em 2026-08-27), entao so desempata
    # por ordem de mao quando nao ha diferenca clara.
    def missing_score(card):
        if card in FETCH_TARGETS:
            return -1  # fetch e sempre pelo menos tao boa quanto a melhor alternativa
        score = 0
        for color in "WUBRG":
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


def do_orb_dragonkind_wrapper(state: GameState):
    do_orb_dragonkind(state)


def check_color_screw(state: GameState):
    """Metrica nova: havia mana TOTAL suficiente pra algo na mao, mas
    faltou a cor certa? So conta se sobrou pelo menos 1 carta assim
    depois do main_phase resolver tudo que dava pra pagar."""
    for n in state.hand:
        if n in LAND_NAMES:
            continue
        if remaining_mana_for(state, n) >= effective_cost(state, n) and not has_color_sources_for(state, n):
            state.color_screw_turns += 1
            if state.first_color_screw_turn is None:
                state.first_color_screw_turn = state.turn
            return


def main_phase(state: GameState):
    if not state.commander_in_play and can_cast(state, COMMANDER):
        cast_card(state, COMMANDER)

    do_orb_dragonkind(state)

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

    check_color_screw(state)

    if "Ramos, Dragon Engine" in state.battlefield and "Ramos, Dragon Engine" in ready_creatures(state) and state.ramos_counters >= 5:
        state.ramos_counters -= 5
        state.bonus_mana_pool += 10


def do_magda_treasures(state: GameState):
    """Magda, Brazen Outlaw: 'Whenever a Dwarf you control becomes tapped,
    create a Treasure token.' + 'Sacrifice five Treasures: search library
    for an artifact or Dragon card, put onto the battlefield.'

    Bug real corrigido em 2026-08-27 (achado pelo usuario): a tag
    'treasure_tutor_dragon' existia no CARD_DB mas NUNCA tinha sido
    implementada em lugar nenhum — Magda era um corpo puramente
    decorativo. Alem disso, Firdoch Core E' um Dwarf de verdade
    (Changeling: 'This card is every creature type', em toda zona) —
    quando ele tapa pra mana (dork_flat1_any), isso TAMBEM dispara o
    gatilho da Magda, nao so ela mesma atacando. As duas fontes de tap
    contam aqui: a propria Magda (assume que ataca todo turno que esta
    pronta, mesma abstracao de combate ja usada pros Dragoes) e Firdoch
    Core (assume que tapa pra mana todo turno que esta pronto, mesma
    abstracao ja usada em dork_mana()).

    Os Treasures da Magda sao guardados (nao convertidos em mana na
    hora, ao contrario de create_and_use_treasures) — decisao real: vale
    mais guardar rumo aos 5 pro tutor gratis de Dragao/artefato do que
    gastar 1 a 1 em mana."""
    if "Magda, Brazen Outlaw" not in state.battlefield:
        return
    ready = set(ready_creatures(state))
    taps = 0
    if "Magda, Brazen Outlaw" in ready:
        taps += 1
    if "Firdoch Core" in state.battlefield and "Firdoch Core" in ready:
        taps += 1
    if taps == 0:
        return
    state.magda_treasures += taps
    state.treasures_created_total += taps
    while state.magda_treasures >= 5:
        state.magda_treasures -= 5
        pool = [n for n in state.library if is_dragon(n) or is_artifact_card(n)]
        if not pool:
            break
        best = max(pool, key=lambda n: CARD_DB[n].mv)
        state.library.remove(best)
        enter_battlefield(state, best, from_hand=False)
        state.tutors_used_total += 1
        state.magda_tutors_total += 1
        if is_dragon(best):
            state.dragons_free_entry_total += 1


def combat_step(state: GameState):
    do_magda_treasures(state)
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
                        if is_dragon(best):
                            state.dragons_free_entry_total += 1
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
            if "attack_mana_power" in tags:
                for _ in range(times):
                    state.bonus_mana_pool += CARD_DB[n].power
            if "attack_mana_flat" in tags:
                for _ in range(times):
                    state.bonus_mana_pool += 6

        # Correcao real 2026-08-27: Utvara Hellkite ("Whenever A Dragon you
        # control attacks, create a 6/6...") e Old Gnawbone ("Whenever A
        # creature you control deals combat damage to a player, create
        # THAT MANY Treasures") NAO sao gatilhos auto-referentes — ao
        # contrario de Goldspan/Klauth/Savage Ventmaw/etc ("Whenever ~ [esta
        # carta] attacks..."), essas 2 disparam pra QUALQUER Dragao
        # atacando, nao so quando a propria Utvara/Old Gnawbone ataca. O
        # loop acima (checagem por tag da propria carta atacante) so
        # cobria o caso self-referente — Utvara/Old Gnawbone ficavam sem
        # gatilho nenhum se elas mesmas nao estivessem no grupo atacando,
        # quando o oraculo real nao exige isso (so precisam estar em
        # campo). Corrigido: checagem de presenca em campo, escala com
        # `n_attacking` (Utvara, 1 token por Dragao atacando) e com a soma
        # de poder dos atacantes (Old Gnawbone, "that many" = poder de
        # cada criatura que causou dano — batching a soma total e
        # matematicamente equivalente a somar token-a-token).
        if "Utvara Hellkite" in state.battlefield:
            utvara_times = 2 if "Roaming Throne" in state.battlefield else 1
            for _ in range(n_attacking * utvara_times):
                state.dragon_tokens += 1
        if "Old Gnawbone" in state.battlefield:
            total_attack_power = sum(CARD_DB[n].power for n in attacking_dragons)
            gnawbone_times = 2 if "Roaming Throne" in state.battlefield else 1
            for _ in range(gnawbone_times):
                create_and_use_treasures(state, total_attack_power)


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
    state.dragon_mana_pool = 0
    state.orb_dragonkind_used_this_turn = False
    state.first_creature_used_this_turn = False

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
    print(f"Avg ativacoes da habilidade de mana da Orb of Dragonkind: {avg([s.orb_mana_activations_total for s in states]):.2f}")
    print(f"Avg fetches cracked: {avg([s.fetches_cracked_total for s in states]):.2f}")
    print(f"Avg tutores via Magda (Treasure sac): {avg([s.magda_tutors_total for s in states]):.2f}")
    print(f"Avg Dragoes que entraram SEM pagar custo (Bladewing/Haunting Voyage/Magda tutor/Ur-Dragon free permanent): {avg([s.dragons_free_entry_total for s in states]):.2f}")
    print(f"Avg Dragon tokens (Lathliss/Miirym/Broodmother/Utvara): {avg([s.dragon_tokens for s in states]):.2f}")
    print(f"Avg turnos com color screw (mana total ok, cor errada): {avg([s.color_screw_turns for s in states]):.2f}")
    screwed = [s.first_color_screw_turn for s in states if s.first_color_screw_turn is not None]
    print(f"% de jogos com pelo menos 1 turno de color screw: {100*len(screwed)/n:.1f}% | turno medio do 1o screw: {avg(screwed):.2f}" if screwed else "% de jogos com color screw: 0.0%")
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
                "orb_mana_activations_total": s.orb_mana_activations_total,
                "cards_drawn_extra": s.cards_drawn_extra,
                "fetches_cracked_total": s.fetches_cracked_total,
                "color_screw_turns": s.color_screw_turns,
                "first_color_screw_turn": s.first_color_screw_turn,
            }) + "\n")
