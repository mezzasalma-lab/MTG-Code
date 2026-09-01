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
add(COMMANDER, 9, "creature", {"commander", "dragon", "roaming_throne_type"}, power=10,
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
    "Path of Ancestry": set("WUBRG"),  # scry 1 condicional (mana gasta em criatura que compartilha tipo com o comandante) nao modelado - achado 2026-08-30, valor real baixo demais pra justificar rastrear "qual mana especifica pagou o que" neste simulador
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

# Auditoria completa 2026-08-29 (Regra 13 - texto INTEIRO de carta via API
# real da Scryfall, nao resumo de busca): conferindo essas 3 de novo por
# completo, 2 clausulas menores ficam documentadas como fora de escopo
# (zero efeito numerico modelavel num goldfish solo, nunca inventadas):
# - Cavern of Souls: "...and that spell can't be countered" - protecao
#   contra contramagia de OPONENTE, mesma classe ja documentada em Rhythm
#   of the Wild/Scalelord Reckoner/Smothering Tithe.
# - Secluded Courtyard: "...or activate an ability of a creature source of
#   the chosen type" - nenhum Dragao desta lista tem habilidade ativada
#   que cobre mana colorida (checado contra a decklist atual), entao essa
#   clausula extra nunca teria alvo real aqui de qualquer forma.
# A 3a clausula da Haven of the Spirit Dragon NAO e' cosmetica - e'
# recursao de verdade, faltando ate 2026-08-29: "{2}, {T}, Sacrifice this
# land: Return target Dragon creature card or Ugin planeswalker card from
# your graveyard to your hand." (sem Ugin nesta lista, so' a metade
# Dragao se aplica). Implementada em `try_haven_recursion()`, chamada no
# fim de `main_phase()`.
HAVEN_RECURSION_LAND = "Haven of the Spirit Dragon"

# Achado real 2026-08-27 (revisao pedida pelo usuario): o simulador nunca
# modelou terreno entrando tapped — todo terreno virava mana disponivel
# no mesmo turno em que era jogado, mesmo os que o oraculo real diz que
# NAO entram destravados. Conferido carta a carta via Scryfall:
#   - Os 4 Triomes (Jetmir's Garden, Ketria Triome, Zagoth Triome,
#     Ziatora's Proving Ground): "This land enters tapped." Incondicional,
#     sem opcao de pagar vida — SEMPRE tapped. Contam aqui.
#   - Os 8 choques (Blood Crypt, Breeding Pool, Godless Shrine, Hallowed
#     Fountain, Overgrown Tomb, Sacred Foundry, Steam Vents, Stomping
#     Ground, Temple Garden): "As this land enters, you may pay 2 life. If
#     you don't, it enters tapped." TEM escolha — como vida nunca e' um
#     recurso escasso neste simulador (nunca rastreada/ameacada), a
#     premissa assumida e' que o jogador SEMPRE paga a vida pra destravar
#     (mesma logica ja usada em outras cartas com custo de vida
#     documentado). NAO contam aqui — ficam destravados, premissa
#     explicita, nao invisivel.
ETB_TAPPED_LANDS = {"Jetmir's Garden", "Ketria Triome", "Zagoth Triome", "Ziatora's Proving Ground",
                     "Path of Ancestry",
                     # Rugged Highlands (achado 2026-08-29, Regra 12): "Rugged
                     # Highlands enters the battlefield tapped. When Rugged
                     # Highlands enters the battlefield, you gain 1 life."
                     # Incondicional, sem opcao de vida pra destravar (vida
                     # nao rastreada, so a parte "tapped" conta aqui).
                     "Rugged Highlands",
                     # Raging Ravine (Worldwake, manland): "Raging Ravine
                     # enters the battlefield tapped." Incondicional. A
                     # ativacao "{2}{R}{G}: vira criatura 3/3 que ganha
                     # +1/+1 a cada ataque" NAO e modelada (fora de escopo
                     # documentado - decisao de quando ativar um manland
                     # exige julgamento de ameaca/bloqueio que este
                     # simulador solo sem oponente real nao tem base pra
                     # fazer) - conta so como fonte de mana R/G aqui.
                     "Raging Ravine"}  # achado real 2026-08-28 (auditoria de checklist): "This land enters tapped" incondicional, faltava

# "Slow lands" (Kaldheim, reimpressas em VOW/DBL/SOS/WHO/INR) — regra #12
# do user-standing-rules.md, citacao literal do usuario apos perguntar
# sobre Sundown Pass: "Sempre implemente a verificacao de todos os tipos
# de terrenos: fetch, checked, shock, triomas e etc!" Oraculo real
# (Scryfall, conferido 2026-08-29): "This land enters tapped unless you
# control two or more other lands." Diferente de check land classico
# (Innistrad 2011, checa TIPO basico de outro terreno, ex: Sunpetal
# Grove) - slow land checa CONTAGEM de terrenos, nao tipo. Condicao
# avaliada em play_land() ANTES do terreno entrar (conta os OUTROS
# terrenos ja em campo, nao inclui a propria entrando).
SLOW_LANDS = {"Sundown Pass", "Rockfall Vale"}

# Unicas 3 criaturas com o tipo Human na decklist (type_line real, Scryfall) -
# usado por Return of the Wildspeaker ("non-Human creatures you control").
HUMAN_CREATURE_NAMES = {"Dragonspeaker Shaman", "Ruby, Daring Tracker", "Sarkhan, Soul Aflame"}

# Terrenos BASICOS de verdade nesta lista — sem Island (a manabase nao
# roda nenhuma Island basica, so fontes de U vem de duais/triomes/CT).
# Usado por Cultivate/Kodama's Reach ("search for a basic land CARD" —
# nao alcanca duais/triomes mesmo com o tipo).
BASIC_LAND_NAMES = {"Forest", "Mountain", "Plains", "Swamp"}

# Karplusan Forest: NAO esta na lista.md — cadastrada so pra permitir o
# teste comparativo de troca de Watery Grave (candidato de corte real,
# unica terra cujas 2 cores sao as mais sobre-representadas frente a
# demanda de pips: U -11,2pp, B -10,4pp) por uma fonte de R/G (as 2 mais
# sub-representadas). Oraculo real: "{T}: Add {C}. / {T}: Add {R} or
# {G}. This land deals 1 damage to you." — sem tapped, untapped de
# verdade.
add("Karplusan Forest", 0, "land", set(), produces={"R", "G"})

# City of Brass: candidata levantada pelo usuario (Regra 12 - arquetipo
# verificado antes de cadastrar). Oraculo real (Scryfall): "Whenever this
# land becomes tapped, it deals 1 damage to you." + "{T}: Add one mana of
# any color." Painland-5-cores: nunca entra tapped, produz QUALQUER cor
# (nao so R/G como Karplusan) - a mesma premissa ja documentada pros
# outros painlands/shocks se aplica (vida nao rastreada no simulador,
# entao o custo real de vida fica invisivel aqui, ja um vies conhecido).
add("City of Brass", 0, "land", set(), produces=set("WUBRG"))

# Mana Confluence: mesmo arquetipo da City of Brass (Regra 12). Oraculo
# real (Scryfall): "{T}, Pay 1 life: Add one mana of any color." Nunca
# tapped, 5 cores, custo de vida por ativacao (nao rastreado, mesma
# premissa) - matematicamente identica a City of Brass neste simulador.
add("Mana Confluence", 0, "land", set(), produces=set("WUBRG"))

# Rockfall Vale: slow land R/G (mesmo arquetipo do Sundown Pass, ver
# SLOW_LANDS acima). Oraculo real (Scryfall, MID/INR/WHO): "This land
# enters tapped unless you control two or more other lands. {T}: Add {R}
# or {G}."
add("Rockfall Vale", 0, "land", set(), produces={"R", "G"})

# Rugged Highlands: tapland R/G incondicional + ganha 1 vida (nao
# rastreado). Ver ETB_TAPPED_LANDS acima.
add("Rugged Highlands", 0, "land", set(), produces={"R", "G"})

# Raging Ravine: manland R/G, sempre tapped (ver ETB_TAPPED_LANDS acima).
# Ativacao de virar criatura fora de escopo, documentado la.
add("Raging Ravine", 0, "land", set(), produces={"R", "G"})

# Battlefield Forge: NAO esta na lista.md — cadastrada pra testar o 2o
# corte de B/U (candidato: Island, U puro, a cor com o pior gap depois
# de R). Diversifica de proposito em vez de dobrar R/G com a Karplusan —
# cobre R (o maior gap, +23,0pp) e W (+7,0/+8,6pp), sem inflar mais
# ainda verde (que ja tem o menor gap dos 3 sub-representados). Oraculo
# real: "{T}: Add {C}. / {T}: Add {R} or {W}. This land deals 1 damage
# to you." — sem tapped.
add("Battlefield Forge", 0, "land", set(), produces={"R", "W"})

# Sundown Pass: candidata real levantada pelo usuario como possivel
# substituta de Battlefield Forge (mesmas 2 cores, R/W) - NAO esta na
# lista.md ainda, cadastrada so pra permitir o teste comparativo (mesmo
# padrao ja usado pro Karplusan Forest/Battlefield Forge/Talisman antes
# de entrarem). Oraculo real: "{T}: Add {R} or {W}." + slow land (ver
# SLOW_LANDS acima).
add("Sundown Pass", 0, "land", set(), produces={"R", "W"})

# Talisman of Impulse: ESTA na lista.md (linha 44) - comentario anterior
# desatualizado. Oraculo real: "{T}: Add {C}. / {T}: Add {R} or {G}. This
# artifact deals 1 damage to you." Achado real 2026-08-28 (auditoria de
# checklist de mecanica): tagueada "rock1" mas rocks_mana() so' checava
# Sol Ring/Arcane Signet/Great Henge por nome - Talisman nunca contribuia
# mana nenhuma pro total_mana(), so contava pra color_sources(). Corrigido
# em rocks_mana().
add("Talisman of Impulse", 2, "artifact", {"rock1"}, produces={"R", "G"})

# Ruby, Daring Tracker: ESTA na lista.md (linha 43) - comentario anterior
# desatualizado (mesmo caso do Talisman of Impulse acima). Oraculo real
# (Scryfall, 2026-08-27): "{R}{G}, Legendary Creature — Human Scout, 1/2.
# Haste. Whenever Ruby attacks while you control a creature with power 4
# or greater, Ruby gets +2/+2 until end of turn. {T}: Add {R} or {G}."
add("Ruby, Daring Tracker", 2, "creature", {"dork_flat1", "haste"}, power=1, pips={"R": 1, "G": 1}, produces={"R", "G"})

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
add("Delighted Halfling", 1, "creature", {"dork_flat1"}, power=1)  # produces=set() de proposito: "any color" real e' restrito a spell lendario (LEGENDARY_ANY_COLOR_SOURCES), checado a parte
add("Arcane Signet", 2, "artifact", {"rock1"}, produces=set("WUBRG"))
add("Sol Ring", 1, "artifact", {"rock2"})  # {C}{C} — sem cor

# --- Custo de Dragao / tutores -------------------------------------------------
add("Dragonlord's Servant", 2, "creature", {"dragon_discount1"}, power=1, pips={"R": 1})
add("Dragonspeaker Shaman", 3, "creature", {"dragon_discount2"}, power=2, pips={"R": 2})
add("Sarkhan, Soul Aflame", 3, "creature", {"dragon_discount1"}, power=2, pips={"U": 1, "R": 1})
# "Whenever a Dragon you control enters, you may have Sarkhan become a
# copy of it until end of turn" implementada em dragon_enters() (pedido
# explicito do usuario 2026-08-30, "efeito de todas as criaturas") -
# rastreada como evento real (sarkhan_soul_aflame_copies), sem inventar
# dano/poder numerico extra pra combate individual, que este simulador
# nao modela em nenhum outro lugar (copiar nao re-dispara ETB, regra real).
add("Herald's Horn", 3, "artifact", {"dragon_discount1", "tribal_impulse"})

# Commander's Sphere: candidata real pro slot vago (Regra 13, oraculo
# conferido via curl na API real): "{T}: Add one mana of any color in
# your commander's color identity. / Sacrifice this artifact: Draw a
# card." Ur-Dragon e' 5 cores (WUBRG), entao produces = todas as 5, igual
# Command Tower/Arcane Signet. Habilidade de sacrificar pra comprar
# NAO modelada (ability secundaria, so relevante quando a mana ja nao faz
# falta - fora de escopo documentado, nao inventada como draw automatico).
add("Commander's Sphere", 3, "artifact", {"rock1"}, produces=set("WUBRG"))

# Dragon's Hoard: candidata concorrente pro mesmo slot (usuario apontou,
# 2026-08-29: "e' mana fix e card draw, o deck e' de dragoes e gera
# tokens de dragoes" - argumento real, precisa teste, nao suposicao).
# Oraculo real (Scryfall, conferido antes na variante fisica): "{3},
# Artifact. Whenever a Dragon you control enters, put a gold counter on
# this artifact. {T}: Add one mana of any color. {T}, Remove a gold
# counter from this artifact: Draw a card." As 2 habilidades ativadas
# competem pelo MESMO {T} - heuristica MELHORADA nesta rodada (a versao
# anterior, testada so' na variante fisica, nunca gastava contador pra
# comprar, subestimando o valor real): ver `try_dragon_hoard_draw()`,
# chamada no fim de `main_phase()` - gasta 1 contador pra comprar quando
# sobra mana sem uso no turno (a mana da Hoard nao fez falta, entao vale
# mais como compra). Gold counters SEM "nontoken" no oraculo - contam
# tambem em tokens de Dragao (Lathliss/Miirym/Broodmother/Utvara), ver
# dragon_enters(). Artefato, nao criatura - Roaming Throne nunca dobra
# esse gatilho (so' dobra gatilho de CRIATURA do tipo escolhido).
add("Dragon's Hoard", 3, "artifact", {"rock1", "dragon_hoard"}, produces=set("WUBRG"))
add("Sarkhan's Triumph", 3, "instant", {"dragon_tutor_hand"}, pips={"R": 1})
add("Orb of Dragonkind", 2, "artifact", {"dragon_tutor_sac"}, pips={"R": 1})
add("Urza's Incubator", 3, "artifact", {"dragon_discount2"})

# Morophon, the Boundless — ADICIONADA ao lista.md em 2026-08-29, trocada
# por Ramos, Dragon Engine (corte validado no teste comparativo
# `urdragon_morophon_test.py`: Ramos era o corte estruturalmente melhor
# entre 6 candidatos, mantem contagem de Dragoes neutra e desloca a curva
# so' +1 CMC). Oraculo real (Scryfall,
# conferido 2026-08-28): {7}, Legendary Creature — Shapeshifter, 6/6,
# Changeling ("This card is every creature type" — em TODA zona, inclusive
# como spell na pilha, mesmo principio ja usado no Firdoch Core). "As
# Morophon enters, choose a creature type [Dragon, obvio/central pro
# tema]. Spells of the chosen type you cast cost {W}{U}{B}{R}{G} less to
# cast. This effect reduces only the amount of colored mana you pay.
# Other creatures you control of the chosen type get +1/+1."
# {7} sem pip colorido nenhum no custo impresso (pips={} correto) — a
# reducao de {W}{U}{B}{R}{G} e' ESTRUTURALMENTE DIFERENTE dos outros
# redutores de Dragao acima (Servant/Shaman/Sarkhan/Herald's Horn/Urza's
# Incubator, todos "custa {N} a menos" generico): reduz especificamente
# PIP COLORIDO, nunca mana generica (texto real: "reduces only the amount
# of colored mana you pay") — modelado a parte via `morophon_pip_discount()`,
# aplicado em `has_color_sources_for()` (menos pip exigido) e somado em
# `effective_cost()` (o total pago cai na mesma proporcao). O anthem
# "+1/+1 a outras criaturas do tipo escolhido" e' modelado via
# `effective_power()`, substituindo os 6 usos anteriores de
# `CARD_DB[name].power` cru (primeiro anthem estatico desta decklist —
# nenhuma carta ja registrada dependia de poder DINAMICO antes).
add("Morophon, the Boundless", 7, "creature", {"dragon"}, power=6, pips={})

# Kindred Discovery — ADICIONADA em 2026-08-29 (troca por Delighted
# Halfling, validada no teste `urdragon_primer3_test.py`: +42% dano proxy
# medio sozinha, o maior ganho isolado dos 3 candidatos testados —
# recomendada tambem pelo artigo draftsim.com sobre Ur-Dragon). Oraculo
# real (Scryfall, C17/CLB/LCC, conferido 2026-08-29 via WebSearch — a
# leitura inicial "combat damage to a player" estava ERRADA, corrigida
# antes de implementar, Regra 1): "As this enchantment enters, choose a
# creature type. Whenever a creature you control of the chosen type
# enters or attacks, draw a card." Tipo escolhido = Dragao. Implementado
# em 2 pontos: `dragon_enters()` (ETB, nomeado ou token, sem "nontoken" no
# oraculo) e `combat_step()` (1 compra por Dragao atacante, mesmo calculo
# de `attacking_dragons` ja usado la pro gatilho da propria Ur-Dragon).
# NAO e' dobrada por Roaming Throne — a habilidade pertence a Kindred
# Discovery (enchantment), nao a criatura Dragao em si (mesma distincao ja
# documentada pro Dragon's Hoard).
#
# ERRO REAL corrigido em 2026-08-29 (usuario cobrou uso de texto COMPLETO
# de carta, achado via auditoria em lote na API real da Scryfall
# — `curl https://api.scryfall.com/cards/collection` -, nao mais
# WebSearch): esta carta tinha sido cadastrada com mv=3 e pip VERDE
# (G:1) - dado inventado/lembrado errado, nunca conferido de verdade. O
# custo real e' `{3}{U}{U}`, mv=5, cor AZUL (2 pips U), sem nenhum pip
# verde. Corrigido - isso muda a castabilidade real da carta (precisa de
# 2 fontes de azul, nao 1 de verde) e exige re-teste de qualquer
# conclusao anterior que dependia do custo errado.
add("Kindred Discovery", 5, "enchantment", {"kindred_discovery"}, pips={"U": 2})

# Sarkhan Unbroken — ADICIONADA em 2026-08-29 (troca por Ruby, Daring
# Tracker, validada no teste `urdragon_primer3_test.py`: +12,8% dano
# proxy medio sozinha; confirmada em 3 fontes reais independentes — primer
# original do usuario, decklist do Brian Kibler, artigo draftsim.com).
# Oraculo real (Scryfall, DTK, conferido 2026-08-29): "{2}{G}{U}{R},
# Legendary Planeswalker — Sarkhan, lealdade inicial 4. +1: Draw a card,
# then add one mana of any color. -2: Create a 4/4 red Dragon creature
# token with flying. -8: Search your library for any number of Dragon
# creature cards, put them onto the battlefield, then shuffle."
# Categoria 12 do checklist (`goldfish-sim-card-rules.md`) — lealdade
# rastreada de verdade via `state.sarkhan_loyalty` (atributo dinamico,
# GameState e' dataclass sem __slots__), 1 ativacao por turno (guardado
# por `state.sarkhan_activated_turn`, ja que main_phase() e' chamada 2x
# por turno). Heuristica documentada, precisa validacao do usuario (Regra
# 1): sempre +1 ate lealdade >= 8, depois sempre ultimate na primeira
# chance — nunca usa o -2 (o token unico nao compensa desviar do caminho
# pro ultimate, que poe TODOS os Dragoes da biblioteca em campo de graca).
# Com lealdade inicial 4, o ultimate so' fica alcancavel num goldfish de 8
# turnos se Sarkhan for conjurado ate o turno 4 (4 ativacoes de +1 = turno
# de cast +4). Morre por regra de estado (lealdade chega a 0) assim que usa
# o ultimate.
add("Sarkhan Unbroken", 5, "planeswalker", {"sarkhan_unbroken"},
    pips={"G": 1, "U": 1, "R": 1})

# --- Dragoes com gatilho real ----------------------------------------------------
add("Ancient Copper Dragon", 6, "creature", {"dragon", "combat_treasure_d20"}, power=6, pips={"R": 2})
add("Ancient Gold Dragon", 7, "creature", {"dragon", "combat_token_d20"}, power=7, pips={"W": 2})
add("Atarka, World Render", 7, "creature", {"dragon"}, power=6, pips={"R": 1, "G": 1})
add("Balefire Dragon", 7, "creature", {"dragon", "interaction"}, power=6, pips={"R": 2})
# Balefire Dragon: "Whenever this creature deals combat damage to a
# player, it deals that much damage to each creature that player
# controls." Removal real, mas depende de criaturas de OPONENTE em
# campo — igual a Assassin's Trophy/Beast Within/etc (tag 'interaction'),
# nao modelavel num goldfish solo sem oponente. Tag antiga
# 'combat_wipe_proxy' nunca tinha sido checada (achado na revisao
# completa de 2026-08-27) — renomeado pra 'interaction' pra refletir a
# razao real de nao ter simulacao, em vez de parecer uma tag esquecida.
add("Bladewing the Risen", 7, "creature", {"dragon", "reanimate_dragon_etb"}, power=4, pips={"B": 2, "R": 2})
add("Dragon Broodmother", 6, "creature", {"dragon", "upkeep_dragon_token"}, power=4, pips={"R": 3, "G": 1})
add("Dragonlord Dromoka", 6, "creature", {"dragon"}, power=5, pips={"G": 1, "W": 1})
add("Goldspan Dragon", 5, "creature", {"dragon", "attack_treasure", "goldspan", "haste"}, power=4, pips={"R": 2})
add("Hellkite Charger", 6, "creature", {"dragon", "extra_combat_paid", "haste"}, power=5, pips={"R": 2})
add("Hellkite Courser", 6, "creature", {"dragon"}, power=6, pips={"R": 2})
add("Klauth, Unrivaled Ancient", 7, "creature", {"dragon", "attack_mana_power", "haste"}, power=4, pips={"R": 1, "G": 1})
add("Lathliss, Dragon Queen", 6, "creature", {"dragon", "dragon_etb_token"}, power=6, pips={"R": 2})
# "{1}{R}: Dragons you control get +1/+0 until end of turn" implementada
# em try_dragon_pumps() (pedido explicito do usuario 2026-08-30, "efeito
# de todas as criaturas") - rastreada como ativacao real (lathliss_pumps),
# 1x/turno quando ha mana sobrando e outros Dragoes em campo pra
# beneficiar, sem inventar dano de combate extra que este simulador nao
# calcula por criatura individual em nenhum outro lugar. Mesmo tratamento
# pra Bladewing the Risen ("{B}{R}: Dragons +1/+1") e Scourge of Valkas
# ("{R}: this creature +1/+0", so' ela mesma).
add("Miirym, Sentinel Wyrm", 6, "creature", {"dragon", "dragon_etb_copy"}, power=6, pips={"G": 1, "U": 1, "R": 1})
add("Old Gnawbone", 7, "creature", {"dragon"}, power=7, pips={"G": 2})
add("Ramos, Dragon Engine", 6, "artifact_creature", {"dragon", "ramos_counters"}, power=4)
add("Savage Ventmaw", 6, "creature", {"dragon", "attack_mana_flat"}, power=4, pips={"R": 1, "G": 1})
add("Scourge of Valkas", 5, "creature", {"dragon", "dragon_etb_damage"}, power=4, pips={"R": 3})
add("Terror of the Peaks", 5, "creature", {"creature_etb_damage_power", "dragon"}, power=5, pips={"R": 2})
# Achado real 2026-08-27 (verificando o combo Miirym+Bladewing+Terror of
# the Peaks do Commander Spellbook): type_line real e' "Creature —
# Dragon" (P/T 5/4) — faltava a tag 'dragon' (invisivel pra Eminence,
# dragon_count, tutores, Cavern of Souls/Courtyard/Haven, Roaming
# Throne, Herald's Horn/Urza's Incubator) e o poder estava errado (4 em
# vez de 5).
add("Twinflame Tyrant", 5, "creature", {"dragon"}, power=3, pips={"R": 2})
add("Utvara Hellkite", 8, "creature", {"dragon"}, power=6, pips={"R": 2})

# --- Outras criaturas / suporte tribal --------------------------------------------
add("Dragon Tempest", 2, "enchantment", {"dragon_etb_damage"}, pips={"R": 1})
add("Magda, Brazen Outlaw", 2, "creature", {"treasure_tutor_dragon"}, power=2, pips={"R": 1})
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
add("Firdoch Core", 3, "artifact", {"rock_any", "dragon"}, produces=set("WUBRG"))

# Radagast of Rhosgobel: NAO esta na lista.md — cadastrado so pra permitir
# o teste comparativo `urdragon_radagast_test.py`. {2}{G}{G}, verde real
# (colors=['G']), NAO e Dragao (Avatar Wizard — nao participa de
# dragon_discount_self/others nem de dragon_enters()). Oraculo real: "The
# first creature spell you cast each turn costs {2} less to cast and can
# be cast as though it had flash."
add("Radagast of Rhosgobel", 4, "creature", {"first_creature_discount"}, power=2, pips={"G": 2})

# --- Draw engines de poder / spells caras -----------------------------------------
add("Elemental Bond", 3, "enchantment", {"power3_draw"}, pips={"G": 1})
add("Garruk's Uprising", 3, "enchantment", {"power4_draw"}, pips={"G": 1})
add("Temur Ascendancy", 3, "enchantment", {"power4_draw_optional"}, pips={"G": 1, "U": 1, "R": 1})
add("The Great Henge", 9, "artifact", {"nontoken_etb_counter_draw", "cost_reduce_power"}, pips={"G": 2}, produces={"G"})
add("Up the Beanstalk", 2, "enchantment", set(), pips={"G": 1})
add("Return of the Wildspeaker", 5, "instant", {"power_draw_instant"}, pips={"G": 1})
add("Sylvan Library", 2, "enchantment", set(), pips={"G": 1})

# --- Removal / interacao / protecao -----------------------------------------------
add("An Offer You Can't Refuse", 1, "instant", {"interaction"}, pips={"U": 1})
add("Anguished Unmaking", 3, "instant", {"interaction"}, pips={"W": 1, "B": 1})
add("Arcane Denial", 2, "instant", {"interaction"}, pips={"U": 1})
add("Assassin's Trophy", 2, "instant", {"interaction"}, pips={"B": 1, "G": 1})
add("Austere Command", 6, "sorcery", {"wipe"}, pips={"W": 2})
add("Beast Within", 3, "instant", {"interaction"}, pips={"G": 1})
add("Crux of Fate", 5, "sorcery", {"wipe"}, pips={"B": 2})
add("Heroic Intervention", 2, "instant", {"interaction"}, pips={"G": 1})
add("Lightning Greaves", 2, "artifact", {"interaction"})
# Achado real 2026-08-29 (usuario apontou, ja depois desta carta ter sido
# cortada da lista.md pra Magda): oraculo real (Scryfall) e "Creature
# spells you control can't be countered. Nontoken creatures you control
# have riot." O riot (escolha de +1/+1 counter OU haste - aqui sempre
# haste, ver ready_creatures()) ja estava modelado, mas a 1a frase
# ("creature spells cant be countered") nunca tinha sido sequer
# registrada - nem como tag, nem como N/A documentado, violando a
# checklist do proprio projeto (categoria 9). Tag 'opponent_dependent'
# adicionada so pra documentar a existencia da habilidade - sem efeito
# numerico real no goldfish solo (sem oponente/contramagia modelada,
# mesma classe ja usada em Smothering Tithe/Scalelord Reckoner). Nao muda
# nenhum numero ja reportado, mas o corte anterior pra Magda foi
# justificado citando so' a redundancia do riot/haste - a protecao contra
# contramagia e' unica no deck (nenhuma outra carta faz isso) e nunca foi
# pesada na decisao, mesmo nao sendo mensuravel aqui.
add("Rhythm of the Wild", 2, "enchantment", {"opponent_dependent"}, pips={"R": 1, "G": 1})
add("Smothering Tithe", 4, "enchantment", {"treasure_tax"}, pips={"W": 1})
# Achado 2026-08-30 (pedido explicito do usuario): estava opponent_dependent
# com zero efeito. Implementada em upkeep_step() com a mesma premissa fixa
# "1 Treasure por turno" usada na Rhystic Study do Thranduil.
add("Swan Song", 1, "instant", {"interaction"}, pips={"U": 1})
add("Swords to Plowshares", 1, "instant", {"interaction"}, pips={"W": 1})
add("Teferi's Protection", 3, "instant", {"interaction"}, pips={"W": 1})
add("Haunting Voyage", 6, "sorcery", {"mass_reanimate"}, pips={"B": 2})
add("Roaming Throne", 4, "artifact_creature", {ROAMING_THRONE_TYPE, "roaming_throne"}, power=4)

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

# Achado real 2026-08-27 (revisao pedida pelo usuario, "revise tudo de
# novo"): Delighted Halfling produz qualquer cor SO pra conjurar spell
# lendario ("Spend this mana only to cast a legendary spell") — o
# CARD_DB tinha ela com produces=set("WUBRG") incondicional, superestimando
# a fixacao dela pra qualquer spell. Lista conferida via type_line real
# (Scryfall) de toda carta do deck.
LEGENDARY_SPELLS = {
    "The Ur-Dragon", "Atarka, World Render", "Bladewing the Risen",
    "Dragonlord Dromoka", "Klauth, Unrivaled Ancient", "Lathliss, Dragon Queen",
    "Ruby, Daring Tracker", "Miirym, Sentinel Wyrm", "Old Gnawbone",
    "Ramos, Dragon Engine", "Sarkhan, Soul Aflame", "The Great Henge",
    "Morophon, the Boundless",
}


def is_legendary(name: str) -> bool:
    return name in LEGENDARY_SPELLS


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
    tapped_land_this_turn: str = None
    haunting_voyage_foretold_turn: int = None
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
    haven_recursion_total: int = 0
    dragon_hoard_gold_counters: int = 0
    dragon_hoard_draws_total: int = 0
    hellkite_charger_extra_combats: int = 0

    commander_in_play: bool = False
    commander_cast_count: int = 0
    commander_cast_turn: Optional[int] = None
    hellkite_courser_commander_temp: bool = False
    hellkite_courser_free_commander_total: int = 0
    creature_cast_turn: dict = field(default_factory=dict)
    lightning_greaves_equipped_to: Optional[str] = None

    # metrics -------------------------------------------------------------
    proxy_damage_total: int = 0
    own_interaction_used: int = 0
    sarkhan_triumph_cast_total: int = 0
    sarkhan_triumph_hand_had_no_dragon: int = 0
    treasures_created_total: int = 0
    smothering_tithe_treasures: int = 0
    lathliss_pumps: int = 0
    bladewing_pumps: int = 0
    scourge_self_pumps: int = 0
    sarkhan_soul_aflame_copies: int = 0
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


def effective_power(state: GameState, name: str) -> int:
    """Morophon, the Boundless: "Other creatures you control of the chosen
    type [Dragon] get +1/+1." Primeiro anthem ESTATICO desta decklist —
    todo lugar que le `CARD_DB[name].power` cru precisa passar por aqui em
    vez disso (mesmo padrao ja usado noutros simuladores desta sessao pra
    anthems dinamicos, ex: Caretaker's Talent no Hei Bai). "Other" exclui
    a propria Morophon do proprio bonus."""
    power = CARD_DB[name].power
    base = name.split(" (copia)")[0]
    if ("Morophon, the Boundless" in state.battlefield and is_dragon(base)
            and base != "Morophon, the Boundless"):
        power += 1
    return power


def proxy_drain(state: GameState, n: int):
    """Achado real 2026-08-27 (revisao completa pedida pelo usuario):
    Twinflame Tyrant ("If a source you control would deal damage to an
    opponent or a permanent an opponent controls, it deals double that
    damage instead") tinha a tag 'damage_doubler' nunca checada em lugar
    nenhum — dobrador global de dano completamente ausente do metric
    'proxy_damage_total' reportado a sessao inteira. proxy_drain() e o
    unico ponto de entrada de dano-a-oponente no simulador (Scourge of
    Valkas, Dragon Tempest, Terror of the Peaks), entao dobrar aqui cobre
    os 3 corretamente."""
    if "Twinflame Tyrant" in state.battlefield:
        n *= 2
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
    if "Kindred Discovery" in state.battlefield:
        # "Whenever a creature you control of the chosen type [Dragon]
        # enters... draw a card." Sem "nontoken" no oraculo - dispara pra
        # token tambem (Miirym copia, Lathliss token). Nao dobrada por
        # Roaming Throne (pertence a Kindred Discovery, nao a criatura).
        draw_cards(state, 1)
    if "Dragon's Hoard" in state.battlefield:
        # "Whenever a Dragon you control enters, put a gold counter" -
        # sem "nontoken", conta token tambem. Artefato, nao dobrado por
        # Roaming Throne.
        state.dragon_hoard_gold_counters += 1
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

    # Sarkhan, Soul Aflame: "Whenever a Dragon you control enters, you may
    # have Sarkhan become a copy of it until end of turn..." Achado
    # 2026-08-30 (pedido explicito: "efeito de todas as criaturas
    # implementado"). Copiar NAO re-dispara o ETB do Dragao copiado (regra
    # real de copia) - so' conta como evento real (Sarkhan vira aquele
    # corpo ate o fim do turno), sem inventar dano/poder extra numerico
    # que este simulador nao calcula por combate individual.
    if "Sarkhan, Soul Aflame" in state.battlefield and name != "Sarkhan, Soul Aflame":
        state.sarkhan_soul_aflame_copies += 1


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
    foram registradas — nunca eram checadas aqui.

    Terceiro bug real corrigido na revisao completa de 2026-08-27: tag
    'riot' (Rhythm of the Wild, "Nontoken creatures you control have
    riot" — escolha de +1/+1 counter OU haste na entrada) tambem nunca
    tinha sido checada. Assumido: escolhe sempre haste (mesma logica
    agressiva ja usada no resto do simulador — ataca com tudo que esta
    pronto), nunca o counter. So vale pra criaturas NAO-token (real:
    "nontoken creatures")."""
    temur_ascendancy = "Temur Ascendancy" in state.battlefield
    dragon_tempest = "Dragon Tempest" in state.battlefield
    rhythm_of_the_wild = "Rhythm of the Wild" in state.battlefield

    def is_ready(n):
        if "haste" in CARD_DB[n].tags:
            return True
        if n == state.lightning_greaves_equipped_to:
            # Achado real 2026-09-01 (leitura linha-a-linha, "compile
            # TUDO"): Lightning Greaves ("Equipped creature has haste and
            # shroud. Equip {0}") so tinha a tag generica 'interaction',
            # sem NENHUM efeito real -- nem o haste, o ganho mais
            # relevante pra Ur-Dragon (comandante sem haste nativo, cujo
            # motor inteiro depende de atacar). Ver
            # try_lightning_greaves_equip().
            return True
        if state.creature_cast_turn.get(n, -1) < state.turn:
            return True
        if temur_ascendancy:
            return True
        if dragon_tempest and has_flying(n) and state.creature_cast_turn.get(n, -1) == state.turn:
            return True
        if (rhythm_of_the_wild and "(copia)" not in n
                and state.creature_cast_turn.get(n, -1) == state.turn):
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
        if "dork_flat1" in tags:
            total += 1
    return total


def rocks_mana(state: GameState) -> int:
    total = 0
    if "Sol Ring" in state.battlefield:
        total += 2
    if "Arcane Signet" in state.battlefield:
        total += 1
    if "Talisman of Impulse" in state.battlefield:
        # Achado real 2026-08-28 (auditoria de checklist de mecanica):
        # tagueada "rock1" mas nunca contribuia mana nenhuma - so'
        # Sol Ring/Arcane Signet/Great Henge eram checados aqui por nome.
        total += 1
    if "Firdoch Core" in state.battlefield:
        # Achado real 2026-08-28: Firdoch Core e' um ARTEFATO (Kindred
        # Artifact - Shapeshifter), nao uma criatura, a menos que animado
        # pelo {4}. Doenca de invocacao so vale pra criaturas (CR 302.6) -
        # a versao anterior tratava a mana dela como "dork_flat1_any",
        # gated por ready_creatures() (que exige is_creature_card()), entao
        # nunca contribuia mana nenhuma (nunca aparecia como criatura
        # "pronta" por default). Corrigido: rock incondicional, disponivel
        # no mesmo turno em que e' conjurada, igual Sol Ring.
        total += 1
    if "The Great Henge" in state.battlefield:
        # Achado real 2026-08-27: "{T}: Add {G}{G}. You gain 2 life." nunca
        # tinha sido implementada — so o desconto de custo (X less) e o
        # gatilho de +1/+1 contador/compra estavam no codigo. Vida nao e
        # rastreada no simulador (regra ja documentada em outro lugar),
        # entao so a mana conta aqui.
        total += 2
    if "Commander's Sphere" in state.battlefield:
        # Mesma classe de bug ja corrigido pro Talisman of Impulse: tag
        # 'rock1' sozinha nao contribui mana, precisa do check explicito
        # aqui tambem.
        total += 1
    if "Dragon's Hoard" in state.battlefield:
        total += 1
    return total


def total_mana(state: GameState) -> int:
    lands = sum(1 for n in state.battlefield if n in LAND_NAMES)
    if state.tapped_land_this_turn is not None:
        # Achado real 2026-08-27: Triomes entram tapped incondicionalmente
        # (oraculo real) — a terra jogada esse turno nao produz mana ainda
        # se for uma delas. So conta a partir do proximo turno (reset em
        # play_turn()).
        lands -= 1
    return lands + rocks_mana(state) + dork_mana(state) + state.bonus_mana_pool


def remaining_mana(state: GameState) -> int:
    return max(0, total_mana(state) - state.mana_spent_this_turn)


def color_sources(state: GameState, color: str, dragon_creature_spell: bool = False,
                   legendary_spell: bool = False) -> int:
    """Conta fontes de mana em campo que produzem `color` — terrenos
    incondicionalmente, rocks/dorks so se prontos (sem doenca de invocacao,
    mesmo gate ja usado em dork_mana). Sol Ring/Ancient Tomb/etc contribuem
    pro total generico mas NUNCA aqui (produces vazio), documentado em cada
    entrada do CARD_DB.

    Cavern of Souls/Secluded Courtyard/Haven of the Spirit Dragon (correcao
    real 2026-08-27): produces vazio no CARD_DB (correto pro caso geral),
    mas SE `dragon_creature_spell=True` (a carta sendo conjurada e um
    Dragao de verdade) elas contam como fonte de QUALQUER cor — oraculo
    real, tipo escolhido = Dragao nesse deck.

    Delighted Halfling (achado real 2026-08-27, revisao completa): mesma
    logica, mas `legendary_spell=True` (a carta sendo conjurada e' um
    permanente lendario de verdade) — "Spend this mana only to cast a
    legendary spell"."""
    n = 0
    ready = set(ready_creatures(state))
    for card in state.battlefield:
        base = card.split(" (copia)")[0]
        if base not in CARD_DB:
            continue
        if base == state.tapped_land_this_turn:
            continue  # Triome jogado este turno, ainda tapped (ver ETB_TAPPED_LANDS)
        c = CARD_DB[base]
        if dragon_creature_spell and base in DRAGON_ANY_COLOR_LANDS:
            produces = set("WUBRG")
        elif legendary_spell and base == "Delighted Halfling":
            produces = set("WUBRG")
        else:
            produces = c.produces
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


def morophon_pip_discount(state: GameState, name: str) -> dict:
    """Morophon, the Boundless: 'Spells of the chosen type [Dragon] you
    cast cost {W}{U}{B}{R}{G} less to cast. This effect reduces only the
    amount of colored mana you pay.' SEM qualificador 'other' no oraculo
    real (diferente da Eminence da propria Ur-Dragon) — vale pra QUALQUER
    spell Dragao, inclusive a propria comandante. Remove ate 1 pip de cada
    cor W/U/B/R/G presente no custo real da carta (nunca mais que o pip
    exigido, nunca cores que a carta nao tem). Estruturalmente diferente
    dos outros redutores de Dragao do deck (que reduzem mana GENERICA) —
    por isso e' checado a parte aqui (reduz `needed` antes de checar fontes)
    e somado separadamente em `effective_cost()` (reduz o total pago, nunca
    mana generica que sobraria pra outra coisa)."""
    if "Morophon, the Boundless" not in state.battlefield or not is_dragon(name):
        return {}
    pips = CARD_DB[name].pips
    return {c: min(1, pips.get(c, 0)) for c in "WUBRG" if pips.get(c, 0) > 0}


def has_color_sources_for(state: GameState, name: str) -> bool:
    """Checa pips coloridos reais (independentes de desconto de custo —
    'costs {1} less' reduz mana generica, nunca pip colorido, regra real).
    Orb of Dragonkind NAO conta aqui por simplificacao conservadora
    documentada (ver docstring do arquivo).

    Passa dragon_creature_spell=True pra color_sources quando `name` e um
    Dragao de verdade (creature, tag dragon) — libera Cavern of
    Souls/Secluded Courtyard/Haven of the Spirit Dragon como fonte de
    qualquer cor so nesse caso (correcao real 2026-08-27). Passa
    legendary_spell=True quando `name` e' lendario de verdade — libera
    Delighted Halfling do mesmo jeito."""
    pips = CARD_DB[name].pips
    discount = morophon_pip_discount(state, name)
    dragon_creature = is_dragon(name) and is_creature_card(name)
    legendary = is_legendary(name)
    for color, needed in pips.items():
        needed -= discount.get(color, 0)
        if needed <= 0:
            continue
        if color_sources(state, color, dragon_creature_spell=dragon_creature,
                          legendary_spell=legendary) < needed:
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
        powers = [effective_power(state, n) for n in state.battlefield if is_creature_card(n)]
        x = max(powers) if powers else 0
        return max(0, mv - x)
    first_creature_d = 0
    if (is_creature_card(name) and "Radagast of Rhosgobel" in state.battlefield
            and not state.first_creature_used_this_turn):
        first_creature_d = 2
    morophon_d = sum(morophon_pip_discount(state, name).values())
    if name == COMMANDER:
        return max(0, mv - dragon_discount_self(state) - first_creature_d - morophon_d)
    if is_dragon(name):
        return max(0, mv - dragon_discount_others(state, name) - first_creature_d - morophon_d)
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
    if pick in ETB_TAPPED_LANDS:
        # a fetch em si nunca entra tapped, mas se o alvo buscado for um
        # Triome, ELE entra tapped por texto proprio, independente de
        # como chegou ao campo.
        state.tapped_land_this_turn = pick


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

    if name == "Hellkite Courser" and not state.commander_in_play:
        # Achado real 2026-08-27 (revisao completa, cartas sem tag
        # nenhuma alem de 'dragon' passavam batido): "When this creature
        # enters, you may put a commander you own from the command zone
        # onto the battlefield. It gains haste. Return it to the command
        # zone at the beginning of the next end step." Coloca a Ur-Dragon
        # em campo DE GRACA (nao e' conjurar — nao incrementa
        # commander_cast_count/taxa, nao marca commander_cast_turn, regra
        # real). So dispara se ela ainda estiver na zona de comando (nao
        # conjurada ainda) — se ja esta em campo, a habilidade nao tem
        # alvo valido. Sai de campo nao no end_step deste MESMO turno
        # (ela entrou na primeira main_phase(), antes do combate — real:
        # "at the beginning of the next end step", que e' o fim deste
        # turno em play_turn()).
        # Via enter_battlefield() de verdade (nao so append) pra disparar
        # os mesmos gatilhos de ETB de qualquer entrada real (Dragon
        # Tempest, Scourge of Valkas, Lathliss, Miirym, Elemental
        # Bond/Garruk's Uprising/Great Henge/Terror of the Peaks).
        enter_battlefield(state, COMMANDER, from_hand=False, count_as_cast=False)
        state.hellkite_courser_commander_temp = True
        state.hellkite_courser_free_commander_total += 1

    if name == "Bladewing the Risen":
        targets = [c for c in state.graveyard if is_dragon(c)]
        if targets:
            best = max(targets, key=lambda n: CARD_DB[n].mv)
            state.graveyard.remove(best)
            enter_battlefield(state, best, from_hand=False)
            state.dragons_free_entry_total += 1

    if "nontoken_etb_counter_draw" in tags:
        pass  # e o proprio Great Henge entrando, nao dispara a si mesmo

    if name == "Up the Beanstalk":
        # Achado real 2026-08-27: tag 'bigspell_draw' nunca tinha sido
        # implementada — carta 100% decorativa. Oraculo: "When this
        # enchantment enters ... draw a card." (parte do ETB, aqui). O
        # gatilho recorrente "whenever you cast a spell with mana value 5
        # or greater" e' tratado em cast_card().
        draw_cards(state, 1)

    if name == "Garruk's Uprising":
        # Achado real 2026-08-27: oraculo tem 3 linhas, nao so a
        # recorrente ("whenever a creature power 4+ enters, draw", ja
        # coberta em creature_etb_hooks) — faltava a compra unica de ETB
        # da propria Garruk's Uprising ("When this enchantment enters, if
        # you control a creature with power 4 or greater, draw a card").
        if any(is_creature_card(c) and effective_power(state, c) >= 4
               for c in state.battlefield if c != name):
            draw_cards(state, 1)

    if "power3_draw" in tags or "power4_draw" in tags:
        pass  # gatilho recorrente delas e sobre OUTRAS criaturas entrando (tratado em creature_etb_hooks)


def creature_etb_hooks(state: GameState, name: str):
    """Gatilhos que outras cartas tem sobre QUALQUER criatura sua entrando
    (nao so Dragao) — Elemental Bond, Garruk's Uprising, Temur Ascendancy,
    The Great Henge, Terror of the Peaks."""
    power = effective_power(state, name)
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


def reanimate_dragons_from_graveyard(state: GameState, limit: int = None):
    """Compartilhado por Haunting Voyage hardcast (limit=2) e foretold
    (limit=None, 'return ALL'). Prioriza maior mv primeiro. Bug real
    corrigido 2026-08-27 (achado em 20k jogos de robustez, seed
    22401654): se um dos alvos e' a propria Bladewing the Risen, o
    gatilho de ETB dela ('return target Dragon permanent card from your
    graveyard') dispara ao entrar via ESTA reanimacao tambem, e pode
    consumir outro alvo do cemiterio antes deste loop chegar nele —
    checar presenca no cemiterio antes de cada remocao."""
    targets = sorted([c for c in state.graveyard if is_dragon(c) and is_creature_card(c)],
                      key=lambda n: CARD_DB[n].mv, reverse=True)
    if limit is not None:
        targets = targets[:limit]
    for t in targets:
        if t not in state.graveyard:
            continue
        state.graveyard.remove(t)
        enter_battlefield(state, t, from_hand=False)
        state.dragons_free_entry_total += 1


def search_land(state: GameState, eligible_types: set = None, basics_only: bool = False,
                 force_tapped: bool = False):
    """Busca real de terreno (Achado 2026-08-27, revisao completa: o
    codigo anterior pegava QUALQUER terreno da biblioteca sem checar tipo
    nenhum — Farseek/Nature's Lore/Three Visits/Skyshroud Claim tem
    restricoes de tipo REAIS e diferentes entre si, e nenhuma era
    respeitada. Cultivate/Kodama's Reach so buscam terreno BASICO de
    verdade, nao dual/triome com aquele tipo).

    eligible_types: tipos basicos aceitos (cruzado contra
    LAND_BASIC_TYPES, mesma logica de crack_fetch — alcanca duais/triomes
    com aquele tipo, nao so basicas). basics_only=True restringe a
    Forest/Mountain/Plains/Swamp de verdade. Prioriza, entre os
    elegiveis, o que resolve a cor mais escassa agora."""
    if basics_only:
        candidates = [n for n in state.library if n in BASIC_LAND_NAMES]
    else:
        candidates = [n for n in state.library if n in LAND_BASIC_TYPES and (LAND_BASIC_TYPES[n] & eligible_types)]
    if not candidates:
        return None

    def score(land):
        colors = CARD_DB[land].produces
        if not colors:
            return 99
        return min(color_sources(state, c) for c in colors)

    candidates.sort(key=score)
    pick = candidates[0]
    state.library.remove(pick)
    state.battlefield.append(pick)
    if force_tapped or pick in ETB_TAPPED_LANDS:
        state.tapped_land_this_turn = pick
    return pick


def resolve_instant_sorcery(state: GameState, name: str):
    tags = CARD_DB[name].tags
    if name in ("Cultivate", "Kodama's Reach"):
        # "Search for up to two BASIC land cards... put one onto the
        # battlefield tapped and the other into your hand." Simplificado
        # ha tempo (documentado): as duas vao pro campo em vez de 1 pra
        # mao, favorece mana imediata. So terrenos BASICOS de verdade
        # (nao duais/triomes com aquele tipo) — bug real corrigido agora,
        # buscava qualquer terreno antes. Tapped nao forcado aqui (a
        # simplificacao de "ambas pro campo" ja documentada torna a
        # semantica de qual das 2 seria a 'tapped' real ambigua).
        search_land(state, basics_only=True)
        search_land(state, basics_only=True)
    elif name == "Farseek":
        # "Search for a Plains, Island, Swamp, or Mountain card, put it
        # onto the battlefield TAPPED." Alcanca qualquer terreno com um
        # desses 4 tipos (duais/triomes inclusos), nao so basicas — mas
        # NUNCA Forest pura.
        search_land(state, eligible_types={"Plains", "Island", "Swamp", "Mountain"}, force_tapped=True)
    elif name in ("Nature's Lore", "Three Visits"):
        # "Search for a Forest card, put it onto the battlefield." Sem
        # 'tapped' no oraculo — destravado. Alcanca qualquer terreno
        # Forest-tipado (duais/triomes inclusos).
        search_land(state, eligible_types={"Forest"})
    elif name == "Skyshroud Claim":
        # "Search for up to two Forest cards, put them onto the
        # battlefield." Sem 'tapped' — destravadas, as duas.
        search_land(state, eligible_types={"Forest"})
        search_land(state, eligible_types={"Forest"})
    elif "dragon_tutor_hand" in tags:
        # Sarkhan's Triumph ({2}{R}): "Search your library for a Dragon
        # creature card, reveal it, put it into your hand, then shuffle."
        # Instrumentacao pedida pelo usuario 2026-08-30: rastrear se a mao
        # JA tinha algum Dragao antes deste tutor resolver (o proprio
        # Sarkhan's Triumph ja foi removido da mao em resolve_cast, nao
        # atrapalha a checagem).
        if name == "Sarkhan's Triumph":
            state.sarkhan_triumph_cast_total += 1
            if not any(is_dragon(c) and is_creature_card(c) for c in state.hand):
                state.sarkhan_triumph_hand_had_no_dragon += 1
        pool = [n for n in state.library if is_dragon(n)]
        if pool:
            best = max(pool, key=lambda n: CARD_DB[n].mv)
            state.library.remove(best)
            state.hand.append(best)
            state.tutors_used_total += 1
    elif "wipe" in tags:
        pass  # sem oponente real, wipe simetrico nao tem alvo alheio modelado
    elif "power_draw_instant" in tags:
        # Return of the Wildspeaker: "greatest power among NON-HUMAN
        # creatures you control" - achado real 2026-08-28 (auditoria de
        # checklist de mecanica): contava todas as criaturas, incluindo as
        # 3 Humanas do deck (Dragonspeaker Shaman, Ruby Daring Tracker,
        # Sarkhan Soul Aflame).
        powers = [effective_power(state, n) for n in state.battlefield
                  if is_creature_card(n) and n.split(" (copia)")[0] not in HUMAN_CREATURE_NAMES]
        if powers:
            draw_cards(state, max(powers))
    elif "mass_reanimate" in tags:
        # Haunting Voyage, modo hardcast: "Choose a creature type. Return
        # up to two creature cards of that type from your graveyard to
        # the battlefield." O modo foretold ("return ALL") e' tratado
        # separadamente em main_phase()/reanimate_dragons_from_graveyard,
        # ja que tem estrutura de custo/timing propria (foretell {2} +
        # cast {5}{B}{B} depois, nao e' esta chamada).
        reanimate_dragons_from_graveyard(state, limit=2)


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


def enter_battlefield(state: GameState, name: str, from_hand: bool = True, count_as_cast: bool = True):
    if from_hand and name in state.hand:
        state.hand.remove(name)
    state.battlefield.append(name)
    if name == COMMANDER:
        state.commander_in_play = True
        if count_as_cast:
            # count_as_cast=False: entrada gratis (Hellkite Courser) —
            # NAO e' conjurar, nao incrementa a taxa nem marca o turno de
            # "conjuracao" (regra real, essa habilidade poe em campo, nao
            # conjura).
            state.commander_cast_count += 1
            if state.commander_cast_turn is None:
                state.commander_cast_turn = state.turn
    if is_creature_card(name):
        state.creature_cast_turn[name] = state.turn
    if name == COMMANDER and not count_as_cast:
        # "It gains haste" — sem isso ficaria presa por doenca de
        # invocacao no combate deste mesmo turno.
        state.creature_cast_turn[name] = state.turn - 1
    if name == "Ramos, Dragon Engine":
        pass
    if name == "Sarkhan Unbroken" and not hasattr(state, "sarkhan_loyalty"):
        state.sarkhan_loyalty = 4
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
        # Bug real corrigido 2026-08-27: oraculo real e "put a +1/+1
        # counter on Ramos for EACH of that spell's colors" — nao 1 flat
        # por spell. len(pips) = numero de cores distintas do custo (ex:
        # comandante WUBRG = 5, nao 1). Spell incolor (Sol Ring) = 0,
        # correto (real: sem cor, sem counter).
        state.ramos_counters += len(CARD_DB[name].pips)

    if name in LAND_NAMES:
        state.battlefield.append(name)
        return

    if "Up the Beanstalk" in state.battlefield and card.mv >= 5:
        # Achado real 2026-08-27: gatilho recorrente de Up the Beanstalk
        # ("whenever you cast a spell with mana value 5 or greater, draw
        # a card") — usa mv REAL impresso, nao o custo com desconto (MV
        # nao muda com desconto de custo, regra real).
        draw_cards(state, 1)

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
        other_lands_in_play = sum(1 for n in state.battlefield if n in LAND_NAMES)
        state.battlefield.append(choice)
        if choice in ETB_TAPPED_LANDS:
            state.tapped_land_this_turn = choice
        elif choice in SLOW_LANDS and other_lands_in_play < 2:
            # "enters tapped unless you control two or more OTHER lands" -
            # contagem de terrenos ANTES desta entrar (other_lands_in_play
            # calculado antes do append acima).
            state.tapped_land_this_turn = choice


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

    # Haunting Voyage, modo foretold: "Foretell {5}{B}{B}" — acao especial
    # (paga {2}, exila a carta da mao virada pra baixo), separada de
    # conjurar, sem seguir custo/pips normais. Depois, em turno posterior,
    # pode ser conjurada da exilada por {5}{B}{B} pro modo "return ALL
    # creature cards" (em vez de so 2 no hardcast). Achado real
    # 2026-08-27 — eu tinha deixado de fora "por escopo" na Correcao #11;
    # usuario apontou que isso e' esquecer a carta de verdade, nao uma
    # simplificacao razoavel. Heuristica: foretell assim que possivel
    # (custo baixo, {2}), conjura da exilada assim que 7 mana sobrar —
    # sempre estritamente melhor que o hardcast de 6 mana limitado a 2
    # alvos.
    if ("Haunting Voyage" in state.hand and state.haunting_voyage_foretold_turn is None
            and remaining_mana(state) >= 2):
        state.hand.remove("Haunting Voyage")
        state.haunting_voyage_foretold_turn = state.turn
        spend_mana(state, 2)
    if (state.haunting_voyage_foretold_turn is not None
            and state.haunting_voyage_foretold_turn < state.turn  # regra real: "cast it on a LATER turn"
            and remaining_mana(state) >= 7):
        state.haunting_voyage_foretold_turn = None
        spend_mana(state, 7)
        reanimate_dragons_from_graveyard(state, limit=None)

    while True:
        # Achado real 2026-08-27 (revisao pedida pelo usuario): cartas
        # tageadas 'interaction' (remocao/protecao/contramagia — Swords to
        # Plowshares, Assassin's Trophy, Beast Within, Heroic
        # Intervention, Swan Song, Teferi's Protection etc.) e 'wipe'
        # (Crux of Fate, Austere Command) nunca tinham handling nenhum em
        # resolve_instant_sorcery — a IA gulosa conjurava mesmo assim
        # (can_cast so checa mana, nao alvo real), gastando carta+mana
        # de graca porque nao ha oponente/ameaca real modelada. Pior:
        # varias sao baratas (Swords to Plowshares {W}=1 mana) e
        # competiam por prioridade cedo contra Dragoes de verdade,
        # subestimando a curva real do deck a sessao inteira. Um piloto
        # de verdade SEGURA essas cartas ate ter alvo — excluidas do
        # auto-cast guloso, ficam na mao (aproximacao conservadora, nao
        # finge que sao inuteis, so nao finge um alvo que nao existe).
        REACTIVE_NO_TARGET = {"interaction", "wipe"}
        castables = [n for n in state.hand if n not in LAND_NAMES and can_cast(state, n)
                     and not (CARD_DB[n].tags & REACTIVE_NO_TARGET)]
        if not castables:
            break
        def prio(n):
            tags = CARD_DB[n].tags
            group = 0 if (tags & {"rock1", "rock2", "rock_any", "land_tutor1", "land_tutor2", "land_tutor2_direct", "dork_flat1"}) else 1
            return (group, effective_cost(state, n))
        castables.sort(key=prio)
        cast_card(state, castables[0])

    check_color_screw(state)

    if "Ramos, Dragon Engine" in state.battlefield and state.ramos_counters >= 5:
        # Achado real 2026-08-28 (auditoria de checklist): "Remove five
        # +1/+1 counters from Ramos: Add..." - SEM {T} no custo real. Doenca
        # de invocacao so afeta habilidades com {T} (CR 302.6); o gate por
        # ready_creatures() estava errado, bloqueava a ativacao no proprio
        # turno em que Ramos entra mesmo com 5+ contadores.
        state.ramos_counters -= 5
        state.bonus_mana_pool += 10

    if "Sarkhan Unbroken" in state.battlefield:
        # 1 ativacao por TURNO (CR 606.3) - main_phase() e' chamada 2x por
        # turno (pre e pos-combate), guardado via sarkhan_activated_turn.
        # Heuristica documentada (ver comentario do add()): sempre +1 ate
        # lealdade >= 8, entao sempre ultimate, nunca -2.
        if getattr(state, "sarkhan_activated_turn", None) != state.turn:
            state.sarkhan_activated_turn = state.turn
            loyalty = getattr(state, "sarkhan_loyalty", 4)
            if loyalty >= 8:
                state.sarkhan_loyalty = loyalty - 8
                targets = [n for n in state.library if is_dragon(n) and is_creature_card(n)]
                for t in targets:
                    if t not in state.library:
                        continue
                    state.library.remove(t)
                    enter_battlefield(state, t, from_hand=False)
                    state.dragons_free_entry_total += 1
                if state.sarkhan_loyalty <= 0:
                    # Regra de estado: lealdade 0 -> vai pro cemiterio.
                    state.battlefield.remove("Sarkhan Unbroken")
                    state.graveyard.append("Sarkhan Unbroken")
            else:
                state.sarkhan_loyalty = loyalty + 1
                draw_cards(state, 1)
                state.bonus_mana_pool += 1

    try_haven_recursion(state)
    try_dragon_hoard_draw(state)
    try_dragon_pumps(state)
    try_lightning_greaves_equip(state)


def try_dragon_pumps(state: GameState):
    """3 ativacoes repetiveis de pump de Dragao, achado 2026-08-30 (pedido
    explicito do usuario: "efeito de todas as criaturas implementado").
    Cada uma rastreada como sua propria ativacao (nao dano de combate
    calculado - este simulador nao modela combate individual criatura a
    criatura em nenhum outro lugar, mesmo tratamento ja usado pros
    finishers repetiveis de Beorn/Thranduil nesta sessao). 1x/turno cada,
    quando ha mana sobrando e um alvo real pra beneficiar."""
    if "Lathliss, Dragon Queen" in state.battlefield and remaining_mana(state) >= 2 and dragon_count(state) >= 1:
        spend_mana(state, 2)
        state.lathliss_pumps += 1

    if "Bladewing the Risen" in state.battlefield and remaining_mana(state) >= 2 and dragon_count(state) >= 1:
        spend_mana(state, 2)
        state.bladewing_pumps += 1

    if "Scourge of Valkas" in state.battlefield and remaining_mana(state) >= 1:
        spend_mana(state, 1)
        state.scourge_self_pumps += 1


def try_lightning_greaves_equip(state: GameState):
    """Achado real 2026-09-01 (leitura linha-a-linha, "compile TUDO"):
    Lightning Greaves estava so tageada 'interaction' (bucket generico de
    protecao do proprio board), sem nenhum efeito real implementado --
    nem sequer o haste, que e' o ganho mais relevante pra este deck
    especifico (Ur-Dragon nao tem haste nativo, e o motor inteiro de
    compra depende de atacar com Dragoes). Equip {0} = sem custo real,
    reequipa automaticamente todo turno se o alvo anterior saiu de campo.
    A comandante e' sempre o alvo obvio (maior valor de ataque
    destravado); "shroud" (protecao contra ser alvo) nao tem efeito
    modelavel aqui (sem oponente/remocao alheia neste goldfish solo)."""
    if "Lightning Greaves" not in state.battlefield:
        return
    if state.lightning_greaves_equipped_to in state.battlefield:
        return
    if state.commander_in_play and COMMANDER in state.battlefield:
        state.lightning_greaves_equipped_to = COMMANDER
        return
    targets = [n for n in state.battlefield if is_creature_card(n)]
    state.lightning_greaves_equipped_to = targets[0] if targets else None


def try_haven_recursion(state: GameState):
    """Haven of the Spirit Dragon, 3a habilidade (achado real 2026-08-29,
    faltava - ver comentario de HAVEN_RECURSION_LAND): '{2}, {T}, Sacrifice
    this land: Return target Dragon creature card or Ugin planeswalker
    card from your graveyard to your hand.' Sem Ugin nesta lista, so' a
    metade Dragao se aplica. Sacrifica a propria fonte de mana - heuristica
    documentada (Regra 1, precisa validacao do usuario): so ativa com pelo
    menos 3 terrenos em campo (nao compromete a manabase basica) E mana
    sobrando (>=2) depois do resto do main_phase ja ter resolvido - nunca
    compete com conjurar algo real."""
    if HAVEN_RECURSION_LAND not in state.battlefield:
        return
    targets = [c for c in state.graveyard if is_dragon(c) and is_creature_card(c)]
    if not targets:
        return
    lands_in_play = sum(1 for n in state.battlefield if n in LAND_NAMES)
    if lands_in_play < 3 or remaining_mana(state) < 2:
        return
    spend_mana(state, 2)
    state.battlefield.remove(HAVEN_RECURSION_LAND)
    best = max(targets, key=lambda n: CARD_DB[n].mv)
    state.graveyard.remove(best)
    state.hand.append(best)
    state.haven_recursion_total += 1


def try_dragon_hoard_draw(state: GameState):
    """Dragon's Hoard: '{T}, Remove a gold counter: Draw a card.' Compete
    pelo MESMO {T} da habilidade de mana ('{T}: Add one mana of any
    color'). Achado real 2026-08-29 (usuario apontou, comparando contra
    Commander's Sphere): a heuristica anterior (testada so' na variante
    fisica) nunca gastava contador pra comprar, o que SUBESTIMA o valor
    real da carta - um piloto de verdade gasta o {T} pra comprar quando a
    mana dela nao faz falta naquele turno. Heuristica melhorada: chamada
    no FIM de main_phase() (depois do loop de conjuracao ja ter gastado
    tudo que dava pra gastar) - se sobrou mana (remaining_mana >= 1) e ha
    contador de ouro disponivel, a mana da Hoard nao fez falta esse turno,
    entao vale mais como compra. Nao precisa desfazer nenhum gasto (a mana
    dela nunca foi de fato usada pra nada, so' contava pro total)."""
    if "Dragon's Hoard" not in state.battlefield:
        return
    if state.dragon_hoard_gold_counters <= 0:
        return
    if remaining_mana(state) < 1:
        return
    state.dragon_hoard_gold_counters -= 1
    draw_cards(state, 1)
    state.dragon_hoard_draws_total += 1


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
    Core (achado real 2026-08-28: e' artefato, nao criatura - sem doenca
    de invocacao, tapa pra mana todo turno que esta em campo, sem gate de
    "ready" - ver rocks_mana()).

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
    if "Firdoch Core" in state.battlefield:
        # Achado real 2026-08-28: Firdoch Core e' artefato, nao criatura -
        # doenca de invocacao nao se aplica (ver rocks_mana()). O gate por
        # "ready" (creature summoning sickness) estava errado aqui tambem.
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


def try_hellkite_charger_extra_combat(state: GameState):
    """Hellkite Charger: 'Whenever this creature attacks, you may pay
    {5}{R}{R}. If you do, untap all attacking creatures and after this
    phase, there is an additional combat phase.' Achado real 2026-08-28
    (auditoria de checklist de mecanica): tagueada 'extra_combat_paid',
    nunca implementada - Old Gnawbone + Hellkite Charger (combo citado na
    auditoria.md) nunca conseguia encadear porque o combate extra em si
    nao existia. Ela tem haste real (sempre pronta pra atacar); a IA
    sempre paga quando tem mana - todo combate extra so' adiciona valor
    nesse motor (sem risco/custo de vida modelado). Chamada UMA vez so' por
    turno (nao recursiva) - premissa conservadora deliberada: o proprio
    Hellkite Charger poderia re-pagar de novo dentro do combate extra que
    ele mesmo concedeu, mas isso abriria um loop sem teto natural nesse
    motor (mana pode crescer via Klauth/etc DURANTE o combate); 1 combate
    extra por turno ja captura a maior parte do valor real sem risco de
    runaway."""
    if "Hellkite Charger" not in state.battlefield:
        return
    if "Hellkite Charger" not in ready_creatures(state):
        return
    if remaining_mana(state) < 7 or color_sources(state, "R") < 2:
        return
    state.mana_spent_this_turn += 7
    state.hellkite_charger_extra_combats += 1
    combat_step(state)


def combat_step(state: GameState):
    do_magda_treasures(state)
    ready = ready_creatures(state)
    ready_dragons = [n for n in ready if is_dragon(n)]
    ur_dragon_attacking = COMMANDER in state.battlefield and COMMANDER in ready
    any_dragon_attacking = len(ready_dragons) > 0

    if ur_dragon_attacking or any_dragon_attacking:
        attacking_dragons = ready_dragons if ready_dragons else ([COMMANDER] if ur_dragon_attacking else [])
        if "Kindred Discovery" in state.battlefield:
            # "...or attacks, draw a card." 1 compra por Dragao atacante -
            # mesmo calculo de attacking_dragons do gatilho da propria
            # Ur-Dragon logo abaixo. Nao dobrada por Roaming Throne (ver
            # comentario do add()).
            draw_cards(state, len(attacking_dragons))
        n_attacking = len(attacking_dragons)
        total_attack_power = sum(effective_power(state, n) for n in attacking_dragons)
        # Atarka, World Render ("Whenever a Dragon you control attacks, it
        # gains double strike"): so afeta gatilhos de "deals combat
        # damage" (combat_treasure_d20/combat_token_d20, Old Gnawbone) —
        # NAO gatilhos de "whenever ~ attacks" (attack_treasure, Utvara),
        # que disparam 1x independente de double strike (regra real:
        # atacar acontece 1x, causar dano de combate acontece 2x com
        # double strike). Achado real 2026-08-27, tag 'attack_double_strike'
        # nunca tinha sido checada.
        atarka_double_strike = "Atarka, World Render" in state.battlefield
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
            dmg_times = times * (2 if atarka_double_strike else 1)
            if "attack_treasure" in tags:
                for _ in range(times):
                    create_and_use_treasures(state, 1)
            if "combat_treasure_d20" in tags:
                for _ in range(dmg_times):
                    create_and_use_treasures(state, 10)  # d20 esperado ~10.5, arredondado
            if "combat_token_d20" in tags:
                for _ in range(dmg_times):
                    state.other_tokens += 10
            if "attack_mana_power" in tags:
                # Klauth: "X e' o poder TOTAL das criaturas atacantes", nao
                # so o proprio poder de Klauth — bug real corrigido
                # 2026-08-27 (usava CARD_DB[n].power, so o poder da propria
                # Klauth).
                for _ in range(times):
                    state.bonus_mana_pool += total_attack_power
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
            # "that many" = dano de combate causado — com Atarka (double
            # strike) o dano efetivo dobra, entao os Treasures tambem.
            old_gnawbone_damage = total_attack_power * (2 if atarka_double_strike else 1)
            gnawbone_times = 2 if "Roaming Throne" in state.battlefield else 1
            for _ in range(gnawbone_times):
                create_and_use_treasures(state, old_gnawbone_damage)


def end_step(state: GameState):
    if state.hellkite_courser_commander_temp:
        # Hellkite Courser: "Return it to the command zone at the
        # beginning of the next end step." Ela ja atacou (se pronta) no
        # combate deste turno — agora sai de campo de verdade, volta
        # 'nao conjurada' (commander_in_play=False) pra poder ser
        # conjurada normalmente depois, pagando taxa do zero (nao foi
        # incrementada quando entrou de graca).
        if COMMANDER in state.battlefield:
            state.battlefield.remove(COMMANDER)
        state.commander_in_play = False
        state.hellkite_courser_commander_temp = False

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

    # Smothering Tithe: "Whenever an opponent draws a card, that player may
    # pay {2}. If the player doesn't, you create a Treasure token." Achado
    # 2026-08-30 (pedido explicito do usuario, mesma premissa da Rhystic
    # Study no Thranduil): media fixa de 1 Treasure por turno em que a
    # Smothering Tithe esta em campo (1 oponente falhando em pagar {2} no
    # draw normal do turno, sem tentar modelar draw extra de oponentes).
    if "Smothering Tithe" in state.battlefield:
        create_and_use_treasures(state, 1)
        state.smothering_tithe_treasures += 1


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


# Subconjunto de "interaction" que e' REALMENTE remocao/counterspell (exige
# alvo do oponente pra valer) - exclui protecao do proprio board (Heroic
# Intervention, Lightning Greaves, Teferi's Protection, ja tageadas
# "interaction" mas nao dependem de alvo alheio).
TRUE_INTERACTION_CARDS = {
    "An Offer You Can't Refuse", "Anguished Unmaking", "Arcane Denial",
    "Assassin's Trophy", "Beast Within", "Swan Song", "Swords to Plowshares",
}

def try_use_own_interaction(state: GameState):
    """Correcao 2026-08-30 (usuario apontou que eu tinha entendido errado
    o pedido anterior): "era para o goldfish usar a carta de interacao na
    NOSSA mao uma vez a cada tres turnos, seja counterspell ou remocao" -
    nao o oponente removendo NOSSAS permanentes (mecanica anterior,
    apply_opponent_interaction, removida). A cada 3 turnos, se a mao tiver
    uma carta de TRUE_INTERACTION_CARDS castavel, ela e conjurada de
    verdade (via cast_card). O resto do deck ja excluia essas cartas do
    loop guloso normal (REACTIVE_NO_TARGET, correcao anterior desta
    sessao) - continuam de fora dali, so' saem da mao aqui."""
    if state.turn % 3 != 0:
        return
    candidates = [c for c in state.hand if c in TRUE_INTERACTION_CARDS and can_cast(state, c)]
    if not candidates:
        return
    candidates.sort(key=lambda c: CARD_DB[c].mv)
    cast_card(state, candidates[0])
    state.own_interaction_used += 1


def play_turn(state: GameState, is_first_turn: bool, on_play: bool):
    state.turn += 1
    state.lands_played_this_turn = 0
    state.mana_spent_this_turn = 0
    state.bonus_mana_pool = 0
    state.dragon_mana_pool = 0
    state.orb_dragonkind_used_this_turn = False
    state.first_creature_used_this_turn = False
    state.tapped_land_this_turn = None  # a Triome do turno passado desamarra agora

    upkeep_step(state)
    if not (is_first_turn and on_play):
        if state.library:
            state.hand.append(state.library.pop(0))
        else:
            state.library_emptied = True
        if "Sylvan Library" in state.battlefield:
            # Achado real 2026-08-27: tag 'card_selection' nunca tinha sido
            # implementada — Sylvan Library era 100% decorativa. Oraculo
            # real: compra 2 extras, escolhe 2 cartas compradas esse turno
            # pra devolver ao topo (cada uma custa 4 vida se ficar com
            # ela). Vida nao e rastreada no simulador (mesma
            # simplificacao documentada em outras cartas) — assumida a
            # linha mais comum na pratica (paga 4 vida por 1 extra,
            # devolve a outra): +1 carta liquida por turno, nao +2.
            draw_cards(state, 1)

    play_land(state)
    try_use_own_interaction(state)
    main_phase(state)
    combat_step(state)
    try_hellkite_charger_extra_combat(state)
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
    print(f"Avg Treasures via Smothering Tithe (1/turno em campo): {avg([s.smothering_tithe_treasures for s in states]):.2f}")
    print(f"Avg vezes que usamos nossa propria remocao/interacao (1/3 turnos, premissa corrigida): {avg([s.own_interaction_used for s in states]):.2f}")
    triumph_cast = [s for s in states if s.sarkhan_triumph_cast_total > 0]
    print(f"Sarkhan's Triumph (tutor de Dragao {{2}}{{R}}) conjurada em {100*len(triumph_cast)/n:.1f}% dos jogos, avg {avg([s.sarkhan_triumph_cast_total for s in states]):.2f} vezes/partida")
    if triumph_cast:
        no_dragon_rate = sum(s.sarkhan_triumph_hand_had_no_dragon for s in triumph_cast) / sum(s.sarkhan_triumph_cast_total for s in triumph_cast)
        print(f"  Dessas ativacoes, {100*no_dragon_rate:.1f}% aconteceram com a mao SEM nenhum outro Dragao antes de resolver (uso genuinamente necessario)")
    print(f"Avg ativacoes de pump: Lathliss {avg([s.lathliss_pumps for s in states]):.2f} | Bladewing {avg([s.bladewing_pumps for s in states]):.2f} | Scourge of Valkas (self) {avg([s.scourge_self_pumps for s in states]):.2f}")
    print(f"Avg vezes que Sarkhan Soul Aflame copiou um Dragao: {avg([s.sarkhan_soul_aflame_copies for s in states]):.2f}")
    print(f"Avg dobras via Roaming Throne: {avg([s.roaming_throne_doubles_total for s in states]):.2f}")
    print(f"Avg cartas compradas extra (motores de draw): {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"Avg tutores usados: {avg([s.tutors_used_total for s in states]):.2f}")
    print(f"Avg ativacoes da habilidade de mana da Orb of Dragonkind: {avg([s.orb_mana_activations_total for s in states]):.2f}")
    print(f"Avg fetches cracked: {avg([s.fetches_cracked_total for s in states]):.2f}")
    print(f"Avg tutores via Magda (Treasure sac): {avg([s.magda_tutors_total for s in states]):.2f}")
    print(f"Avg recursao via Haven of the Spirit Dragon (sacrifica a terra, Dragao do cemiterio pra mao): {avg([s.haven_recursion_total for s in states]):.2f}")
    print(f"Avg compras via Dragon's Hoard (gasta contador de ouro quando mana sobra): {avg([s.dragon_hoard_draws_total for s in states]):.2f}")
    print(f"Avg Dragoes que entraram SEM pagar custo (Bladewing/Haunting Voyage/Magda tutor/Ur-Dragon free permanent): {avg([s.dragons_free_entry_total for s in states]):.2f}")
    print(f"Avg vezes que a Ur-Dragon entrou de graca via Hellkite Courser: {avg([s.hellkite_courser_free_commander_total for s in states]):.2f}")
    print(f"Avg Dragon tokens (Lathliss/Miirym/Broodmother/Utvara): {avg([s.dragon_tokens for s in states]):.2f}")
    print(f"Avg combates extras via Hellkite Charger (agora despachado): {avg([s.hellkite_charger_extra_combats for s in states]):.2f}")
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
                "smothering_tithe_treasures": s.smothering_tithe_treasures,
                "own_interaction_used": s.own_interaction_used,
                "sarkhan_triumph_cast_total": s.sarkhan_triumph_cast_total,
                "sarkhan_triumph_hand_had_no_dragon": s.sarkhan_triumph_hand_had_no_dragon,
                "lathliss_pumps": s.lathliss_pumps,
                "bladewing_pumps": s.bladewing_pumps,
                "scourge_self_pumps": s.scourge_self_pumps,
                "sarkhan_soul_aflame_copies": s.sarkhan_soul_aflame_copies,
                "orb_mana_activations_total": s.orb_mana_activations_total,
                "cards_drawn_extra": s.cards_drawn_extra,
                "fetches_cracked_total": s.fetches_cracked_total,
                "color_screw_turns": s.color_screw_turns,
                "first_color_screw_turn": s.first_color_screw_turn,
            }) + "\n")
