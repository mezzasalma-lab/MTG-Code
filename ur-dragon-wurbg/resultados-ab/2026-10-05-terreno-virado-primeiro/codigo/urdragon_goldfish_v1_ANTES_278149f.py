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
agregado (`proxy_damage_total`), nunca vida real de ninguem. Remocao e
contramagica ficam na mao ate ter alvo (📊); a cada 3 turnos uma e'
conjurada como proxy de uso (`try_use_own_interaction`). No modo de
resiliencia, Swan Song/Arcane Denial/An Offer respondem a contramagica do
oponente e Heroic Intervention/Teferi's Protection respondem a wipe e
remocao.

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

**Fontes de cor restrita:** Cavern of Souls, Secluded Courtyard e Haven
of the Spirit Dragon pagam pip de qualquer cor so' em magia de criatura
Dragao (Courtyard tambem em habilidade de Dragao); a mana da Orb, em
magia ou habilidade de Dragao; Treasure/Klauth/+1 do Sarkhan Unbroken,
qualquer cor; Savage Ventmaw, {R}{R}{R}{G}{G}{G}. Exotic Orchard fica
incolor (📊: depende dos terrenos dos oponentes).

Roaming Throne: tipo escolhido = **Dragon** (obvio e central pro tema,
documentado ainda assim). Dobra qualquer gatilho de criatura Dragao —
inclui o proprio gatilho de ataque da Ur-Dragon (que e ela mesma um
Dragao), os gatilhos de dano-por-Dragao-em-campo (Scourge of Valkas,
Dragon Tempest), os de token (Lathliss, Utvara Hellkite, Miirym), e os
de mana (Klauth, Savage Ventmaw).

Simplificacoes (📝 politica/aproximacao) -- revistas na varredura de 2026-09-28
(detalhe por carta em `checklist-oraculo.md`, secao de mesma data):
- Checagem de cor: fontes prontas, sem saber quais ja' viraram no turno
  (mana total e cor sao contadas separadas).
- Klauth: a mana entra no pool comum (o "only to cast spells" nao e'
  separado de habilidades).
- Smothering Tithe: 1 Treasure por rodada (estimativa de quantos
  oponentes nao pagam {2}).
- Sarkhan Unbroken: +1 ate' 8 de lealdade e entao -8; nunca -2.
- Dragon Broodmother: nunca devora.
- Hellkite Charger: no maximo 1 combate extra por turno.
- Sarkhan, Soul Aflame: copia decidida no fim da main 1, so' entre Dragoes
  nomeados que entraram no turno.
- Combate: sem bloqueio (convencao do repo); atacam os Dragoes prontos,
  a Magda e o Firdoch Core animado; utilitarios (Servant, Dragonspeaker,
  Sarkhan sem copiar, Birds) ficam em casa.
- Vida e' metrica: nao ha' condicao de derrota.
"""

import json
import random
import re
import signal
import statistics
from collections import Counter
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

# Shocks: "As this land enters, you may pay 2 life. If you don't, it enters
# tapped." Premissa antiga (sempre destravada) mantida; CORRIGIDO 2026-09-28:
# agora os 2 de vida sao cobrados (`land_enters`).
SHOCK_LANDS = {"Blood Crypt", "Breeding Pool", "Godless Shrine", "Hallowed Fountain", "Overgrown Tomb",
               "Sacred Foundry", "Steam Vents", "Stomping Ground", "Temple Garden", "Watery Grave"}
CYCLING_TRIOMES = {"Jetmir's Garden", "Ketria Triome", "Zagoth Triome", "Ziatora's Proving Ground"}

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
# CORRIGIDO 2026-09-28 (auditoria de custo contra o Scryfall ao vivo): mv era 2,
# custo real {1}{R}{G} = 3.
add("Rhythm of the Wild", 3, "enchantment", {"opponent_dependent"}, pips={"R": 1, "G": 1})
add("Smothering Tithe", 4, "enchantment", {"treasure_tax"}, pips={"W": 1})
# Achado 2026-08-30 (pedido explicito do usuario): estava opponent_dependent
# com zero efeito. Implementada em upkeep_step() com a mesma premissa fixa
# "1 Treasure por turno" usada na Rhystic Study do Thranduil.
add("Swan Song", 1, "instant", {"interaction"}, pips={"U": 1})
add("Swords to Plowshares", 1, "instant", {"interaction"}, pips={"W": 1})
add("Teferi's Protection", 3, "instant", {"interaction"}, pips={"W": 1})
add("Haunting Voyage", 6, "sorcery", {"mass_reanimate"}, pips={"B": 2})
add("Roaming Throne", 4, "artifact_creature", {ROAMING_THRONE_TYPE, "roaming_throne"}, power=4)

# --- Candidata de Reality Fracture (so' via swap, NAO esta na lista) ------------
# Draconic Visitor (FRA #80, lanca 2026-10-02; oraculo ao vivo Scryfall
# 2026-09-25, salvo no oracle-cache): "{3}{R}{R}, Creature — Dragon 5/5.
# Flying. If one or more artifact tokens would be created under your
# control, that many 5/5 red Dragon creature tokens with flying are created
# instead." Neste deck as fichas de artefato sao todas Treasure (Ancient
# Copper Dragon, Old Gnawbone, Goldspan Dragon, Smothering Tithe, Magda) --
# ver `create_and_use_treasures`/`do_magda_treasures`.
add("Draconic Visitor", 5, "creature", {"dragon", "draconic_visitor"}, power=5, pips={"R": 2})
# Tiamat (candidata, 2026-09-28, NAO esta na lista.md -- so' via swap):
# {2}{W}{U}{B}{R}{G} Legendary Creature -- Dragon God 7/7, Flying. "When
# Tiamat enters, if you cast it, search your library for up to five Dragon
# cards not named Tiamat that each have different names, reveal them, put
# them into your hand, then shuffle." (oraculo ao vivo + rulings: dispara se
# conjurada de qualquer zona; "Dragon card" = tipo Dragon na linha de tipo).
# 📝 Ordem de conjuracao: fila normal (ramp e comandante antes). Testado
# 2026-09-28 contra "Tiamat antes de tudo": mesmo ganho de letal, sem
# atrasar a comandante (goldfish-log, secao Tiamat).
add("Tiamat", 7, "creature", {"dragon", "tiamat"}, power=7, pips={"W": 1, "U": 1, "B": 1, "R": 1, "G": 1})

ARTIFACT_ISH = {"artifact", "artifact_creature"}
CREATURE_ISH = {"creature", "artifact_creature"}
LAND_NAMES = {n for n, c in CARD_DB.items() if c.ctype == "land"}


def is_creature_card(name: str) -> bool:
    return CARD_DB[name].ctype in CREATURE_ISH


def is_artifact_card(name: str) -> bool:
    return CARD_DB[name].ctype in ARTIFACT_ISH


def is_enchantment_card(name: str) -> bool:
    return CARD_DB[name].ctype == "enchantment"


def is_dragon(name: str) -> bool:
    return "dragon" in CARD_DB[name].tags


def is_dragon_card(name: str) -> bool:
    """Achado real 2026-09-14 (mesma classe de bug encontrada e corrigida
    hoje no Beorn/Edgar Markov/Maralen pra Roaming Throne): is_dragon()
    reconhece Roaming Throne como Dragao porque "as this creature enters,
    choose a creature type" e' um efeito de ETB - correto pra checagens de
    BATALHA (a propria dobra do gatilho dela, contagem de Dragoes em
    campo), mas ERRADO pra busca/tutor de biblioteca ou mao: uma carta
    parada la ainda nao resolveu, ainda nao escolheu tipo nenhum, nao e'
    "a Dragon creature card" de verdade. Usado nos tutores reais do deck
    (Sarkhan's Triumph, Orb of Dragonkind, ultimate do Sarkhan Unbroken)
    que buscam Dragao fora do campo de batalha."""
    return is_dragon(name) and name != "Roaming Throne"


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
    "Utvara Hellkite", "Draconic Visitor", "Tiamat",
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
    "Morophon, the Boundless", "Tiamat",
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
    # CORRIGIDO 2026-09-28: era UM slot (`tapped_land_this_turn`). Triome jogado
    # + Farseek no mesmo turno: o 2o sobrescrevia o 1o, que virava mana.
    tapped_lands_this_turn: list = field(default_factory=list)
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
    magda_treasures: int = 0                  # (legado) nao usado: Treasure agora e' `treasure_stock`
    # CORRIGIDO 2026-09-28 (Regra #3, conceito "Treasure que voce controla"):
    # Treasure e' um PERMANENTE -- persiste entre turnos, conta pro "Sacrifice
    # five Treasures" da Magda qualquer que seja a fonte (Goldspan, Old
    # Gnawbone, Ancient Copper, Smothering Tithe, a propria Magda, o Firdoch).
    # Antes: mana instantanea perdida no fim do turno + contador separado da
    # Magda que so' contava os Treasures dela.
    treasure_stock: int = 0
    magda_sources: dict = field(default_factory=dict)   # de onde vieram os Treasures da Magda (metrica)
    magda_tutors_total: int = 0
    dragons_free_entry_total: int = 0
    haven_recursion_total: int = 0
    dragon_hoard_gold_counters: int = 0
    dragon_hoard_draws_total: int = 0
    hellkite_charger_extra_combats: int = 0
    phase: str = "main1"                      # main1 / combat / main2 (Regra #6: politicas por fase)
    life_paid: dict = field(default_factory=dict)   # vida paga por motivo (fetch, shock, Tomb, Confluence, Sylvan, Unmaking)
    life_gained: dict = field(default_factory=dict)
    path_scry_turn: int = -1
    path_scries_total: int = 0
    path_scry_bottoms_total: int = 0
    triome_cycles_total: int = 0
    sarkhan_copy_of: Optional[str] = None      # Sarkhan, Soul Aflame virou copia disto ate o fim do turno
    sarkhan_copies_chosen_total: int = 0
    dragons_entered_this_turn: list = field(default_factory=list)
    firdoch_token_copies: int = 0              # copia da Miirym de Firdoch Core: artefato, nao criatura
    # CORRIGIDO 2026-09-28: mana de Treasure / Klauth / Savage Ventmaw / +1 do
    # Sarkhan Unbroken entrava so' como QUANTIDADE (`bonus_mana_pool`); a cor
    # dela nunca pagava pip. Uma entrada por mana, com as cores possiveis.
    bonus_colored: list = field(default_factory=list)
    dice_rng: Optional[random.Random] = None   # d20 do Ancient Copper/Gold (separado do embaralhamento)
    in_bladewing_loop: bool = False
    bladewing_loop_turn: Optional[int] = None
    bladewing_loop_iterations_total: int = 0
    riot_haste: set = field(default_factory=set)     # Rhythm of the Wild: escolheu haste
    riot_counters: dict = field(default_factory=dict)  # Rhythm of the Wild: escolheu +1/+1
    firdoch_animated_turn: int = -1
    firdoch_entered_turn: int = -1
    magda_firdoch_tap_turn: int = -1
    rotw_pumps_total: int = 0
    balefire_hits_total: int = 0
    pending_upkeep_draws: int = 0             # Arcane Denial: compra no upkeep do proximo turno
    arcane_denial_draws_total: int = 0
    hoard_tapped_turn: int = -1               # Dragon's Hoard: {T} compartilhado (mana OU compra)

    commander_in_play: bool = False
    commander_cast_count: int = 0
    commander_cast_turn: Optional[int] = None
    hellkite_courser_commander_temp: bool = False
    hellkite_courser_free_commander_total: int = 0
    creature_cast_turn: dict = field(default_factory=dict)
    lightning_greaves_equipped_to: Optional[str] = None

    # metrics -------------------------------------------------------------
    proxy_damage_total: int = 0
    commander_damage_dealt: int = 0
    commander_damage_win: bool = False
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
    great_henge_counters: dict = field(default_factory=dict)  # por nome: +1/+1 contadores reais do Great Henge ("put a +1/+1 counter on it")
    great_henge_counters_total: int = 0
    # Fichas de Dragao com poder e turno de entrada (2026-09-25). Antes eram so'
    # o contador `dragon_tokens` -- nunca atacavam. Cada item: [poder base,
    # turno em que entrou, tem flying]. `dragon_tokens` continua sendo o
    # tamanho desta lista (mantido pelo helper `create_dragon_tokens`).
    dragon_token_list: list = field(default_factory=list)
    dragon_tokens_created_total: int = 0
    combat_damage_proxy_total: int = 0        # dano de combate dos Dragoes atacantes (sem bloqueio), proxy
    dragon_pump_bonus_this_turn: int = 0      # Lathliss {1}{R} / Bladewing {B}{R} ativados neste turno
    scourge_pump_this_turn: int = 0           # Scourge of Valkas {R}: +1/+0 so' nela
    visitor_dragons_total: int = 0            # candidata Draconic Visitor (so' via swap)
    visitor_mana_lost_total: int = 0          # mana de Treasure que deixou de existir (virou Dragao)
    tiamat_casts: int = 0                     # candidata Tiamat (so' via swap)
    tiamat_tutored_total: int = 0
    dragon_token_cap_hits: int = 0
    decked_turn: Optional[int] = None         # CR 704.5b: comprou de grimorio vazio (derrota)
    game_over: bool = False
    attackers_held_back_total: int = 0        # Dragoes que o piloto segurou pra nao decar
    lethal_proxy_turn: Optional[int] = None   # 1o turno com dano acumulado (ETB + combate) >= 120 (3 oponentes x 40), proxy

    # --- Modo opcional de resiliencia (portado do Megatron, 2026-09-20) --------
    # `life` nunca e' lido/escrito pelo goldfish padrao (documentado no
    # proprio play_turn: "Vida nao e rastreada no simulador") -- existe
    # aqui SO' pro modo de resiliencia (`try_smart_opponent_attack`), sem
    # tocar a convencao do goldfish padrao.
    interaction_rng: Optional[random.Random] = None
    life: int = 40
    smart_wipes_total: int = 0
    smart_wipe_log: list = field(default_factory=list)
    smart_artifact_wipes_total: int = 0
    smart_artifact_wipe_log: list = field(default_factory=list)
    smart_enchantment_wipes_total: int = 0
    smart_enchantment_wipe_log: list = field(default_factory=list)
    smart_removals_total: int = 0
    smart_removal_log: list = field(default_factory=list)
    smart_attacks_taken_total: int = 0
    smart_attack_log: list = field(default_factory=list)
    smart_discards_total: int = 0
    smart_discard_log: list = field(default_factory=list)
    smart_counters_total: int = 0
    counters_prevented_total: int = 0         # Dromoka / Rhythm / Cavern impediram
    counters_prevented_by: dict = field(default_factory=dict)
    counters_answered_total: int = 0          # Swan Song / Arcane Denial / An Offer responderam
    dromoka_lifelink_total: int = 0
    smart_counter_log: list = field(default_factory=list)
    smart_graveyard_wipes_total: int = 0
    smart_graveyard_wipe_log: list = field(default_factory=list)
    graveyard_wipe_used: bool = False
    smart_graveyard_snipes_total: int = 0
    smart_graveyard_snipe_log: list = field(default_factory=list)
    opp_attacks_on_pw_total: int = 0
    sarkhan_killed_by_attack_total: int = 0
    teferi_protected: bool = False            # Teferi's Protection: "until your next turn"
    protection_responses: dict = field(default_factory=dict)
    wiped_this_round: bool = False  # achado real do usuario 2026-09-20 (2a rodada): board wipe e' simetrico -- vale pra toda a rodada, nao so' o turno do oponente que fez o wipe. Reset em simulate_one_with_interaction() no inicio de cada rodada. Mesmo padrao do Megatron.


def draw_cards(state: GameState, n: int):
    for _ in range(n):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1
        else:
            state.library_emptied = True
            deck_out(state)
            return


LOW_LIBRARY = 10
# 📝 Com o grimorio abaixo disto o piloto recusa compra OPCIONAL (Temur
# Ascendancy "may", Dragon's Hoard, Sylvan Library, Return of the Wildspeaker
# no modo compra, cycling, +1 do Sarkhan Unbroken) -- o gatilho da Ur-Dragon e
# os de Elemental Bond/Garruk's Uprising/Great Henge sao obrigatorios.


def library_low(state: GameState) -> bool:
    return len(state.library) < LOW_LIBRARY


def deck_out(state: GameState):
    """CR 704.5b: quem tentou comprar de grimorio vazio perde. CORRIGIDO
    2026-09-28: `library_emptied` era so' uma flag; o jogo seguia e o letal
    proxy era marcado no fim do turno, depois do combate -- mas o gatilho da
    Ur-Dragon ("draw that many cards", obrigatorio) resolve ANTES do dano.
    Se o dano acumulado ja' passou do letal antes desta compra, os oponentes
    ja' morreram (vitoria); senao e' derrota e a partida para."""
    if state.game_over:
        return
    if state.lethal_proxy_turn is None and state.proxy_damage_total + state.combat_damage_proxy_total >= LETHAL_PROXY:
        state.lethal_proxy_turn = state.turn
    if state.lethal_proxy_turn is None:
        state.decked_turn = state.turn
    state.game_over = True


def pay_life(state: GameState, n: int, why: str):
    """CORRIGIDO 2026-09-28: `life` ja' existia (modo de resiliencia) mas nenhum
    custo de vida da lista era cobrado -- taxonomia "custo (mana ou VIDA) nunca
    deduzido". Sem condicao de derrota (so' metrica, igual antes)."""
    if n <= 0:
        return
    state.life -= n
    state.life_paid[why] = state.life_paid.get(why, 0) + n


def gain_life(state: GameState, n: int, why: str):
    if n <= 0:
        return
    state.life += n
    state.life_gained[why] = state.life_gained.get(why, 0) + n


def dragon_count(state: GameState) -> int:
    # Firdoch Core e a copia dele sao Dragoes (Changeling) mesmo fora de criatura.
    return (sum(1 for n in state.battlefield if is_dragon_perm(state, n)) + state.dragon_tokens
            + state.firdoch_token_copies)


def effective_power(state: GameState, name: str) -> int:
    """Morophon, the Boundless: "Other creatures you control of the chosen
    type [Dragon] get +1/+1." Primeiro anthem ESTATICO desta decklist —
    todo lugar que le `CARD_DB[name].power` cru precisa passar por aqui em
    vez disso (mesmo padrao ja usado noutros simuladores desta sessao pra
    anthems dinamicos, ex: Caretaker's Talent no Hei Bai). "Other" exclui
    a propria Morophon do proprio bonus.

    Bug real corrigido 2026-09-14: The Great Henge ("Whenever a nontoken
    creature you control enters, put a +1/+1 counter on it AND draw a
    card") so tinha a metade do draw implementada (creature_etb_hooks) —
    o +1/+1 contador real, que aumenta o poder daquela criatura pro resto
    do jogo, nunca era rastreado em lugar nenhum. Isso subestimava poder
    em TODO gatilho escalavel por poder do arquivo (Elemental
    Bond/Garruk's Uprising/Temur Ascendancy — thresholds de poder, Terror
    of the Peaks — dano = poder, Klauth/attack_mana_power — soma de poder
    dos atacantes, Return of the Wildspeaker — maior poder). Corrigido com
    `state.great_henge_counters` (contadores reais por nome, mesmo padrao
    ja usado pra Marwyn/Immaculate Magistrate no arquivo irmao
    thranduil_goldfish_v1.py), somado aqui igual ao anthem da Morophon."""
    power = CARD_DB[name].power
    base = name.split(" (copia)")[0]
    if base == SARKHAN_SA and state.sarkhan_copy_of:
        power = CARD_DB[state.sarkhan_copy_of].power  # copia: P/T do Dragao copiado
    if is_dragon_perm(state, base):
        # Morophon: "Other creatures ... get +1/+1" -- 1 por Morophon (copias inclusas)
        power += sources(state, "Morophon, the Boundless") - (1 if base == "Morophon, the Boundless" else 0)
    power += state.great_henge_counters.get(base, 0)
    power += state.riot_counters.get(base, 0)
    if base != "Magda, Brazen Outlaw" and is_dwarf_perm(state, base):
        # Magda: "Other Dwarves you control get +1/+0" (uma por Magda em campo)
        power += state.battlefield.count("Magda, Brazen Outlaw")
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
    n *= twinflame_factor(state)
    state.proxy_damage_total += n


# ---------------------------------------------------------------------------
# Fichas de Dragao (2026-09-25) -- ponto UNICO de criacao
# ---------------------------------------------------------------------------
# Achado real (Regra #3, conceito compartilhado "Dragao que voce controla"):
# as fichas de Dragao (Lathliss 5/5, Utvara 6/6, Broodmother 1/1, copia da
# Miirym, Faerie Dragon 1/1 do Ancient Gold Dragon) eram so' um contador --
# (1) nunca atacavam (o "draw that many cards" da Ur-Dragon, a Kindred
# Discovery, a Utvara e o dano da Old Gnawbone so' viam Dragao NOMEADO), (2)
# as da Lathliss/Utvara/Broodmother nunca disparavam os gatilhos de "um
# Dragao/criatura entra" (Scourge of Valkas, Dragon Tempest, Terror of the
# Peaks, Kindred Discovery, Dragon's Hoard, Elemental Bond/Garruk's
# Uprising/Temur Ascendancy), (3) os Faerie Dragons do Ancient Gold ("1/1
# blue Faerie Dragon creature tokens with flying") nem eram Dragao.

def all_creature_powers(state: GameState) -> list:
    """Poder de TODA criatura que eu controlo, nomeada ou ficha (Regra #3:
    Garruk's Uprising "if you control a creature with power 4 or greater",
    Great Henge "greatest power among creatures you control" e Return of
    the Wildspeaker liam so' carta nomeada -- CORRIGIDO 2026-09-28)."""
    return ([effective_power(state, n) for n in state.battlefield if is_creature_card(n)]
            + [token_effective_power(state, t[0], t[3] if len(t) > 3 else None) for t in state.dragon_token_list])


def token_effective_power(state: GameState, base: int, copy_of: Optional[str] = None) -> int:
    """Poder atual de uma ficha de Dragao: Morophon (+1/+1 em outras
    criaturas do tipo escolhido) e pumps de Lathliss/Bladewing do turno.
    Contador do Great Henge nao se aplica (so' nontoken)."""
    p = base + state.dragon_pump_bonus_this_turn
    # Morophon: "OTHER creatures you control of the chosen type get +1/+1" --
    # a ficha-copia de Morophon nao se da' o proprio bonus (CORRIGIDO 2026-09-28).
    p += sources(state, "Morophon, the Boundless") - (1 if copy_of == "Morophon, the Boundless" else 0)
    if copy_of in DWARF_CARDS:
        p += state.battlefield.count("Magda, Brazen Outlaw")  # ficha-copia de Changeling e' Dwarf
    return p


def token_creature_etb_hooks(state: GameState, power: int, copy_of: Optional[str] = None):
    """Mesmos gatilhos de `creature_etb_hooks` que valem pra FICHA (nenhum
    deles diz "nontoken"): Elemental Bond (poder >= 3), Garruk's Uprising e
    Temur Ascendancy (poder >= 4), Terror of the Peaks (dano = poder). The
    Great Henge fica de fora ("nontoken creature")."""
    if "Elemental Bond" in state.battlefield and power >= 3:
        draw_cards(state, 1)
    if "Garruk's Uprising" in state.battlefield and power >= 4:
        draw_cards(state, 1)
    if "Temur Ascendancy" in state.battlefield and power >= 4 and not library_low(state):  # "you may draw"
        draw_cards(state, 1)
    # "Whenever ANOTHER creature you control enters": cada Terror (copias
    # inclusas), menos a propria ficha se ela for copia da Terror.
    for _ in range((sources(state, "Terror of the Peaks") - (1 if copy_of == "Terror of the Peaks" else 0))
                   * roaming_throne_times(state)):
        proxy_drain(state, power)


SARKHAN_SA = "Sarkhan, Soul Aflame"


DWARF_CARDS = {"Firdoch Core", "Morophon, the Boundless"}   # Changeling: e' todo tipo de criatura, em toda zona


def is_dwarf_perm(state: GameState, name: str) -> bool:
    """Dwarf em campo: Magda (tipo impresso), Firdoch Core e Morophon
    (Changeling -- Kindred permite tipo de criatura fora de criatura, ruling
    2025-11-17), e o Sarkhan, Soul Aflame enquanto copia um deles."""
    if name == "Magda, Brazen Outlaw" or name in DWARF_CARDS:
        return True
    return name == SARKHAN_SA and state.sarkhan_copy_of in DWARF_CARDS


def sources(state: GameState, name: str) -> int:
    """Quantos objetos em campo TEM a habilidade da carta `name`: a carta
    nomeada + fichas-copia da Miirym + o Sarkhan, Soul Aflame copiando ela.
    CORRIGIDO 2026-09-28 (Regra #3, conceito "quem tem esta habilidade"): as
    copias eram corpos sem habilidade nenhuma ("limitacao do motor" -- nao
    era estrutural). Copia da Scourge/Terror/Lathliss/Utvara/Old Gnawbone/
    Twinflame/Morophon/Roaming Throne/Ur-Dragon dispara e soma de verdade."""
    n = state.battlefield.count(name)
    n += sum(1 for t in state.dragon_token_list if len(t) > 3 and t[3] == name)
    if state.sarkhan_copy_of == name and SARKHAN_SA in state.battlefield:
        n += 1
    return n


def roaming_throne_times(state: GameState) -> int:
    """Roaming Throne (tipo = Dragon): "If a triggered ability of another
    creature you control of the chosen type triggers, it triggers an
    additional time." CORRIGIDO 2026-09-25: Terror of the Peaks e Dragon
    Broodmother sao criaturas Dragao com gatilho proprio e nunca eram
    dobradas. CORRIGIDO 2026-09-28: cada Throne (copia da Miirym inclusa)
    soma 1 disparo a mais."""
    return 1 + sources(state, "Roaming Throne")


def twinflame_factor(state: GameState) -> int:
    """Twinflame Tyrant: "it deals double that damage instead" -- cada copia
    dobra de novo (substituicoes se aplicam uma de cada vez)."""
    return 2 ** sources(state, "Twinflame Tyrant")


def is_dragon_perm(state: GameState, name: str) -> bool:
    """Dragao EM CAMPO, incluindo o Sarkhan, Soul Aflame enquanto copia de um."""
    if name == SARKHAN_SA and state.sarkhan_copy_of:
        return True
    return is_dragon(name)


DRAGON_TOKEN_CAP = 400
# Teto do SIMULADOR (nao regra do jogo), mesma convencao do BOARD_CAP do
# Prismatic Bridge: Utvara Hellkite ("Whenever a Dragon you control attacks,
# create a 6/6") dobra os Dragoes a cada ataque (triplica com Roaming
# Throne) -- crescimento exponencial real. Acima de 400 fichas a partida ja'
# esta' decidida; o motor para de criar e conta quantas vezes bateu no teto.


def create_dragon_tokens(state: GameState, n: int, power: int, source: str, flying: bool = True,
                         born_turn: Optional[int] = None, copy_of: Optional[str] = None):
    """Cria `n` fichas de Dragao, uma de cada vez (cada uma e' um evento de
    "entra" separado pra Scourge/Tempest/Terror -- CR 603.2, cada ficha
    criada dispara "whenever a creature enters" sozinha). `born_turn`: turno
    em que a ficha entrou, quando o gatilho real acontece no turno de um
    oponente (Smothering Tithe) -- sem doenca de invocacao no meu turno."""
    room = max(0, DRAGON_TOKEN_CAP - len(state.dragon_token_list))
    if n > room:
        state.dragon_token_cap_hits += 1
        n = room
    for _ in range(n):
        # [poder, turno em que entrou, voa, copia de (nome) ou None]
        state.dragon_token_list.append([power, state.turn if born_turn is None else born_turn, flying, copy_of])
        state.dragon_tokens += 1
        state.dragon_tokens_created_total += 1
        if copy_of in ("Hellkite Courser", "Bladewing the Risen"):
            # ficha-copia entra e o gatilho de ETB DELA dispara (copia tem o texto).
            # Com o loop Miirym + Bladewing + matador montado, o ETB da copia e'
            # usado pra devolver a propria Bladewing (`try_bladewing_loop`).
            if not (copy_of == "Bladewing the Risen" and bladewing_loop_ready(state)):
                resolve_etb(state, copy_of)
        dragon_enters(state, copy_of or f"{source} token", is_token=True)
        token_creature_etb_hooks(state, token_effective_power(state, power, copy_of), copy_of=copy_of)


def ready_dragon_tokens(state: GameState) -> list:
    """Fichas que podem atacar: entraram antes deste turno (CR 302.6), ou
    tem haste -- Temur Ascendancy (todas) ou Dragon Tempest (voadora, no
    turno em que entra). Rhythm of the Wild so' vale pra nontoken."""
    temur = "Temur Ascendancy" in state.battlefield
    tempest = "Dragon Tempest" in state.battlefield
    return [t for t in state.dragon_token_list
            if t[1] < state.turn or temur or (tempest and t[2] and t[1] == state.turn)]


def clear_dragon_tokens(state: GameState):
    state.dragon_token_list = []
    state.dragon_tokens = 0


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
    throne = roaming_throne_times(state)

    # Bug real corrigido 2026-09-14: Scourge of Valkas (criatura) e' dobrada
    # pela Roaming Throne; Dragon Tempest (encantamento) nunca. CORRIGIDO
    # 2026-09-28: cada Scourge em campo (copia da Miirym / Sarkhan copiando)
    # dispara -- "this creature or another Dragon", entao a propria entrando
    # tambem conta.
    for _ in range(sources(state, "Scourge of Valkas") * throne):
        proxy_drain(state, dragon_count(state))
        state.dragon_etb_damage_events_total += 1
        if throne > 1:
            state.roaming_throne_doubles_total += 1
    if "Dragon Tempest" in state.battlefield:
        proxy_drain(state, dragon_count(state))
        state.dragon_etb_damage_events_total += 1

    if not is_token:
        # Miirym: "Whenever ANOTHER nontoken Dragon you control enters, create
        # a token that's a copy of it, except the token isn't legendary."
        # CORRIGIDO 2026-09-28: a ficha agora E' copia (habilidades inclusas,
        # via `sources`); copia de Firdoch Core e' artefato, nao criatura.
        miirym = sources(state, "Miirym, Sentinel Wyrm") - (1 if name == "Miirym, Sentinel Wyrm" else 0)
        for _ in range(miirym * throne):
            if is_creature_card(name):
                create_dragon_tokens(state, 1, CARD_DB[name].power, source="miirym_copy",
                                     flying=has_flying(name), copy_of=name)
            elif name == "Firdoch Core":
                state.firdoch_token_copies += 1
            if throne > 1:
                state.roaming_throne_doubles_total += 1
        # Lathliss: "Whenever ANOTHER nontoken Dragon you control enters, create
        # a 5/5 red Dragon creature token with flying."
        lathliss = sources(state, "Lathliss, Dragon Queen") - (1 if name == "Lathliss, Dragon Queen" else 0)
        for _ in range(lathliss * throne):
            create_dragon_tokens(state, 1, 5, source="lathliss")
            if throne > 1:
                state.roaming_throne_doubles_total += 1

    # Sarkhan, Soul Aflame: "Whenever a Dragon you control enters, you may
    # have Sarkhan become a copy of it until end of turn, except its name is
    # Sarkhan, Soul Aflame and it's legendary." CORRIGIDO 2026-09-28: era so'
    # um contador ("sem poder numerico que este simulador nao calcula" -- o
    # simulador ja' calcula combate por criatura desde 2026-09-25). A escolha
    # e' feita no fim da main 1 (`choose_sarkhan_copy`) entre os Dragoes
    # NOMEADOS de criatura que entraram neste turno (📝 o piloto ordena as
    # conjuracoes pra copiar o melhor por ultimo).
    if SARKHAN_SA in state.battlefield and name != SARKHAN_SA:
        state.sarkhan_soul_aflame_copies += 1
        if not is_token and name in CARD_DB and is_creature_card(name):
            state.dragons_entered_this_turn.append(name)


SARKHAN_COPY_ATTACK_VALUE = {  # habilidade que rende ATACANDO (ou no resto do turno)
    "Utvara Hellkite": 12, "Old Gnawbone": 10, "Twinflame Tyrant": 10, "Atarka, World Render": 8,
    "Klauth, Unrivaled Ancient": 8, "Savage Ventmaw": 8, "Ancient Copper Dragon": 8, "Ancient Gold Dragon": 8,
    "Goldspan Dragon": 6, "Scourge of Valkas": 6, "Terror of the Peaks": 6, "Lathliss, Dragon Queen": 6,
    "Miirym, Sentinel Wyrm": 6, "Dragonlord Dromoka": 3, "The Ur-Dragon": 12,
}


def choose_sarkhan_copy(state: GameState):
    """Fim da main 1: se o Sarkhan, Soul Aflame pode atacar, vira copia do
    melhor Dragao nomeado que entrou neste turno (poder + valor da
    habilidade no combate). 📝 So' antes do combate; copia feita durante o
    combate/main 2 nao e' modelada."""
    if SARKHAN_SA not in state.battlefield or state.sarkhan_copy_of or not state.dragons_entered_this_turn:
        return
    if SARKHAN_SA not in ready_creatures(state):
        return
    best = max(state.dragons_entered_this_turn,
               key=lambda n: CARD_DB[n].power + SARKHAN_COPY_ATTACK_VALUE.get(n, 0))
    if CARD_DB[best].power + SARKHAN_COPY_ATTACK_VALUE.get(best, 0) <= CARD_DB[SARKHAN_SA].power:
        return
    state.sarkhan_copy_of = best
    state.sarkhan_copies_chosen_total += 1


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
        if n in state.riot_haste and state.creature_cast_turn.get(n, -1) == state.turn:
            return True  # Rhythm of the Wild: escolheu haste ao entrar (ver `apply_riot`)
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
    total += state.firdoch_token_copies  # copia da Miirym: "{T}: Add one mana of any color"
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


def total_mana(state: GameState, include_stock: bool = True) -> int:
    lands = sum(1 for n in state.battlefield if n in LAND_NAMES)
    # Achado real 2026-08-27: Triomes entram tapped incondicionalmente
    # (oraculo real) -- a terra que entrou virada neste turno nao produz mana
    # ainda. So' conta a partir do proximo turno (reset em play_turn()).
    lands -= sum(1 for n in state.tapped_lands_this_turn if n in state.battlefield)
    if "Ancient Tomb" in state.battlefield and "Ancient Tomb" not in state.tapped_lands_this_turn:
        # CORRIGIDO 2026-09-28: "{T}: Add {C}{C}" -- contava 1 como todo terreno.
        lands += 1
    base = lands + rocks_mana(state) + dork_mana(state) + state.bonus_mana_pool
    if include_stock:
        base += state.treasure_stock * treasure_mana_each(state)
    return base


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
        if base in state.tapped_lands_this_turn:
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
    if is_dragon_card(name):  # magia: Roaming Throne na pilha e' Golem (tipo escolhido so' ao entrar)
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
    k = sources(state, "Morophon, the Boundless")
    if k == 0 or not is_dragon_card(name):
        return {}
    pips = CARD_DB[name].pips
    return {c: min(k, pips.get(c, 0)) for c in "WUBRG" if pips.get(c, 0) > 0}


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
    dragon_creature = is_dragon_card(name) and is_creature_card(name)
    legendary = is_legendary(name)
    need = {c: n - discount.get(c, 0) for c, n in pips.items() if n - discount.get(c, 0) > 0}
    if not need:
        return True
    # CORRIGIDO 2026-09-28: antes cada cor era checada SOZINHA -- um Command
    # Tower contava como fonte de W, U, B, R e G ao mesmo tempo, entao {W}{U}{B}{R}{G}
    # (Ur-Dragon, Tiamat) passava com 1 fonte de 5 cores + 4 basicos iguais.
    # Uma fonte paga UM pip: condicao de Hall -- pra todo subconjunto S das
    # cores exigidas, pips(S) <= fontes que produzem alguma cor de S.
    sets = (source_color_sets(state, dragon_creature, legendary) + state.bonus_colored
            + [set("WUBRG")] * (treasure_unspent(state) * treasure_mana_each(state)))
    if is_dragon_card(name):
        # CORRIGIDO 2026-09-28: Orb of Dragonkind "Add two mana in any
        # combination of colors. Spend this mana only to cast Dragon spells"
        # -- cada mana do pool paga um pip de qualquer cor.
        sets += [set("WUBRG")] * state.dragon_mana_pool
    colors = list(need)
    for mask in range(1, 1 << len(colors)):
        sub = {colors[i] for i in range(len(colors)) if mask >> i & 1}
        if sum(need[c] for c in sub) > sum(1 for src in sets if src & sub):
            return False
    return True


def source_color_sets(state: GameState, dragon_creature_spell: bool = False, legendary_spell: bool = False) -> list:
    """Uma entrada por fonte de mana COLORIDA pronta (mesmos filtros de
    `color_sources`): o conjunto de cores que ela pode produzir."""
    out = []
    ready = set(ready_creatures(state))
    for card in state.battlefield:
        base = card.split(" (copia)")[0]
        if base not in CARD_DB or base in state.tapped_lands_this_turn:
            continue
        c = CARD_DB[base]
        if dragon_creature_spell and base in DRAGON_ANY_COLOR_LANDS:
            produces = set("WUBRG")
        elif legendary_spell and base == "Delighted Halfling":
            produces = set("WUBRG")
        else:
            produces = set(c.produces)
        if not produces:
            continue
        if is_creature_card(base) and card not in ready and base not in LAND_NAMES:
            continue
        out.append(produces)
    return out


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
    if SARKHAN_SA in state.battlefield and not state.sarkhan_copy_of:
        d += 1  # copiando outro Dragao, o Sarkhan perde o proprio texto ate o fim do turno
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
    # ficha-copia da Ur-Dragon (Miirym): o nome dela e' The Ur-Dragon e ela esta'
    # em campo -> a Eminence dela tambem vale.
    d += sum(1 for t in state.dragon_token_list if len(t) > 3 and t[3] == COMMANDER)
    if "Dragonlord's Servant" in state.battlefield:
        d += 1
    if "Dragonspeaker Shaman" in state.battlefield:
        d += 2
    if SARKHAN_SA in state.battlefield and not state.sarkhan_copy_of:
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
    # CORRIGIDO 2026-09-28 (CR 601.2f, `references/goldfish-sim-card-rules.md`
    # "Reducao de custo so' abate mana GENERICO"): os redutores (Eminence,
    # Dragonlord's Servant, Dragonspeaker Shaman, Sarkhan Soul Aflame, Herald's
    # Horn, Urza's Incubator, Radagast, Great Henge) eram descontados do valor
    # de mana INTEIRO -- Scourge of Valkas ({2}{R}{R}{R}) com Eminence +
    # Dragonspeaker custava 2 em vez de 3; a Ur-Dragon podia sair por menos
    # que {W}{U}{B}{R}{G}. Agora: pips sempre pagos (menos o que o Morophon
    # tira), desconto so' no generico.
    card = CARD_DB[name]
    pip_total = sum(card.pips.values())
    generic = card.mv - pip_total
    morophon_d = sum(morophon_pip_discount(state, name).values())
    colored = pip_total - morophon_d
    if name == "The Great Henge":
        powers = all_creature_powers(state)
        x = max(powers) if powers else 0
        return max(0, generic - x) + colored
    first_creature_d = 0
    if (is_creature_card(name) and "Radagast of Rhosgobel" in state.battlefield
            and not state.first_creature_used_this_turn):
        first_creature_d = 2
    if name == COMMANDER:
        # CORRIGIDO 2026-09-28: a taxa (CR 903.8, {2} por conjuracao anterior
        # da zona de comando) ficava fora daqui -- `can_cast` aprovava a
        # comandante sem a taxa e `cast_card` cobrava mais do que havia.
        return (max(0, generic - dragon_discount_self(state) - first_creature_d) + colored
                + 2 * state.commander_cast_count)
    if is_dragon_card(name):
        return max(0, generic - dragon_discount_others(state, name) - first_creature_d) + colored
    return max(0, generic - first_creature_d) + colored


def can_cast(state: GameState, name: str) -> bool:
    if remaining_mana_for(state, name) < effective_cost(state, name):
        return False
    return has_color_sources_for(state, name)


def spend_mana(state: GameState, n: int):
    state.mana_spent_this_turn += n


# ---------------------------------------------------------------------------
# Fetch lands — mecanismo real (Regra 6)
# ---------------------------------------------------------------------------

def land_enters(state: GameState, land: str, force_tapped: bool = False):
    """Ponto UNICO de terreno entrando no campo (CORRIGIDO 2026-09-28): antes
    cada caminho aplicava (ou esquecia) o "enters tapped" por conta propria --
    o terreno que a Ur-Dragon poe da mao entrava sempre destravado, mesmo
    Triome/Path/slow land; o shock nunca cobrava os 2 de vida."""
    other_lands = sum(1 for n in state.battlefield if n in LAND_NAMES)
    state.battlefield.append(land)
    if force_tapped or land in ETB_TAPPED_LANDS or (land in SLOW_LANDS and other_lands < 2):
        state.tapped_lands_this_turn.append(land)
    elif land in SHOCK_LANDS:
        pay_life(state, 2, "shock")


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
    pay_life(state, 1, "fetch")  # "{T}, Pay 1 life, Sacrifice this land"
    state.fetches_cracked_total += 1
    # Triome buscado entra virado por texto proprio; shock cobra 2 de vida.
    land_enters(state, pick)


# ---------------------------------------------------------------------------
# Resolucao de ETB / cast
# ---------------------------------------------------------------------------

def visitor_replaces_treasures(state: GameState, n: int, mana_each: int, on_opp_turn: bool = False) -> bool:
    """Draconic Visitor (candidata FRA): "If one or more artifact tokens
    would be created under your control, that many 5/5 red Dragon creature
    tokens with flying are created instead." Efeito de substituicao
    obrigatorio (CR 614.1a, "instead"). Retorna True se substituiu -- entao
    nao existe Treasure nenhum (nem mana, nem contagem pra Magda)."""
    if n <= 0 or "Draconic Visitor" not in state.battlefield:
        return False
    state.visitor_mana_lost_total += n * mana_each
    before = state.dragon_tokens_created_total
    create_dragon_tokens(state, n, 5, source="draconic_visitor",
                         born_turn=state.turn - 1 if on_opp_turn else None)
    state.visitor_dragons_total += state.dragon_tokens_created_total - before  # criadas de fato (teto)
    return True


def treasure_mana_each(state: GameState) -> int:
    """Goldspan Dragon: 'Treasures you control have "{T}, Sacrifice this
    artifact: Add two mana of any one color."' (copias inclusas)."""
    return 2 if sources(state, "Goldspan Dragon") else 1


def treasure_nonstock_mana(state: GameState) -> int:
    return total_mana(state, include_stock=False)


def treasure_unspent(state: GameState) -> int:
    """Treasures que NAO estao comprometidos com mana ja' gasta neste turno
    (o piloto gasta terrenos/rocks primeiro e guarda o Treasure)."""
    each = treasure_mana_each(state)
    spent_from_stock = max(0, state.mana_spent_this_turn - treasure_nonstock_mana(state))
    return max(0, state.treasure_stock - (spent_from_stock + each - 1) // each)


def create_treasures(state: GameState, n: int):
    create_and_use_treasures(state, n)


def create_and_use_treasures(state: GameState, n: int, on_opp_turn: bool = False):
    """Cria `n` Treasures (CORRIGIDO 2026-09-28: antes viravam mana na hora e
    o que sobrava sumia no fim do turno; agora ficam em `treasure_stock`,
    gastam como mana quando ha' o que conjurar e sobrevivem ao turno).
    Goldspan em campo: cada Treasure vale 2 mana de UMA cor."""
    if visitor_replaces_treasures(state, n, treasure_mana_each(state), on_opp_turn=on_opp_turn):
        return
    state.treasures_created_total += n
    state.treasure_stock += n


def settle_treasures(state: GameState):
    """Fim do turno: tira do estoque o que foi gasto como mana."""
    each = treasure_mana_each(state)
    spent_from_stock = max(0, state.mana_spent_this_turn - treasure_nonstock_mana(state))
    used = min(state.treasure_stock, (spent_from_stock + each - 1) // each)
    state.treasure_stock -= used


def try_magda_sacrifice(state: GameState):
    """Magda, Brazen Outlaw: "Sacrifice five Treasures: Search your library for
    an artifact or Dragon card, put that card onto the battlefield." Vale
    QUALQUER Treasure. Politica (📝): so' com Treasure que sobrou depois de
    conjurar tudo que da' (nao troca mana usavel por tutor)."""
    if "Magda, Brazen Outlaw" not in state.battlefield:
        return
    while treasure_unspent(state) >= 5:
        pool = [n for n in state.library if is_dragon_card(n) or is_artifact_card(n)]
        if not pool:
            return
        state.treasure_stock -= 5
        # Tiamat: "put onto the battlefield" nao e' conjurar -> so' como ultima opcao.
        best = max(pool, key=lambda n: (n != "Tiamat", CARD_DB[n].mv))
        state.library.remove(best)
        enter_battlefield(state, best, from_hand=False)
        state.tutors_used_total += 1
        state.magda_tutors_total += 1
        if is_dragon(best):
            state.dragons_free_entry_total += 1


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
        # "return target Dragon permanent card from your graveyard" --
        # CORRIGIDO 2026-09-28: (1) `is_dragon_card` (Roaming Throne no
        # cemiterio e' Golem); (2) Roaming Throne dobra este gatilho de
        # criatura Dragao -> 2 alvos.
        for _ in range(roaming_throne_times(state)):
            targets = [c for c in state.graveyard if is_dragon_card(c)]
            if not targets:
                break
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
        if any(p >= 4 for p in all_creature_powers(state)):
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
    if "Temur Ascendancy" in state.battlefield and power >= 4 and not library_low(state):  # "you may draw"
        draw_cards(state, 1)
    if "The Great Henge" in state.battlefield and "token" not in name:
        draw_cards(state, 1)
        # Bug real corrigido 2026-09-14: faltava a metade "put a +1/+1
        # counter on it" do gatilho — so o draw estava implementado (ver
        # docstring de effective_power()). `power` acima ainda nao reflete
        # este contador (calculado antes desta linha), entao o proximo
        # gatilho power-dependente ja ve o valor atualizado.
        state.great_henge_counters[name] = state.great_henge_counters.get(name, 0) + 1
        state.great_henge_counters_total += 1
    # "damage equal to that creature's power" e' lido na RESOLUCAO: o
    # controlador ordena o gatilho do Great Henge pra resolver antes
    # (CORRIGIDO 2026-09-28, antes usava o poder sem o contador). Cada Terror
    # (copias inclusas), menos a que acabou de entrar.
    terrors = sources(state, "Terror of the Peaks") - (1 if name == "Terror of the Peaks" else 0)
    for _ in range(terrors * roaming_throne_times(state)):
        proxy_drain(state, effective_power(state, name))


def reanimate_dragons_from_graveyard(state: GameState, limit: int = None):
    """Compartilhado por Haunting Voyage hardcast (limit=2) e foretold
    (limit=None, 'return ALL'). Prioriza maior mv primeiro. Bug real
    corrigido 2026-08-27 (achado em 20k jogos de robustez, seed
    22401654): se um dos alvos e' a propria Bladewing the Risen, o
    gatilho de ETB dela ('return target Dragon permanent card from your
    graveyard') dispara ao entrar via ESTA reanimacao tambem, e pode
    consumir outro alvo do cemiterio antes deste loop chegar nele —
    checar presenca no cemiterio antes de cada remocao."""
    targets = sorted([c for c in state.graveyard if is_dragon_card(c) and is_creature_card(c)],
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
                 force_tapped: bool = False, to_hand: bool = False):
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
    if to_hand:
        state.hand.append(pick)
        return pick
    land_enters(state, pick, force_tapped=force_tapped)
    return pick


def resolve_instant_sorcery(state: GameState, name: str):
    tags = CARD_DB[name].tags
    if name in ("Cultivate", "Kodama's Reach"):
        # "Search for up to two BASIC land cards... put one onto the
        # battlefield TAPPED and the other into your HAND." CORRIGIDO
        # 2026-09-28: a "simplificacao" antiga punha as duas no campo,
        # destravadas -- 2 mana a mais no mesmo turno. Agora: a 1a (cor mais
        # escassa) entra virada, a 2a vai pra mao (vira o land drop seguinte).
        search_land(state, basics_only=True, force_tapped=True)
        search_land(state, basics_only=True, to_hand=True)
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
            if not any(is_dragon_card(c) and is_creature_card(c) for c in state.hand):
                state.sarkhan_triumph_hand_had_no_dragon += 1
        # CORRIGIDO 2026-09-28: "Dragon CREATURE card" -- Firdoch Core
        # (Kindred Artifact com Changeling) e' Dragon card mas nao criatura.
        pool = [n for n in state.library if is_dragon_card(n) and is_creature_card(n)]
        if pool:
            best = max(pool, key=lambda n: CARD_DB[n].mv)
            # Candidata Tiamat (so' via swap): a linha real e' Triumph ->
            # Tiamat -> +5 Dragoes, quando as 5 cores ja estao disponiveis.
            if "Tiamat" in pool and has_color_sources_for(state, "Tiamat"):
                best = "Tiamat"
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
        powers = ([effective_power(state, n) for n in state.battlefield
                   if is_creature_card(n) and n.split(" (copia)")[0] not in HUMAN_CREATURE_NAMES]
                  + [token_effective_power(state, t[0], t[3] if len(t) > 3 else None) for t in state.dragon_token_list])
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


def try_orb_mana_for_commander(state: GameState):
    """CORRIGIDO 2026-09-28 (Regra #6, ordem de chamadas): a Orb so' era
    ativada DEPOIS da checagem da comandante, e so' com Dragao na MAO (a
    comandante fica na zona de comando). A mana dela ("Spend this mana only
    to cast Dragon spells" -- sem "other", vale pra Ur-Dragon) nunca ajudava
    a conjurar a comandante na 1a fase principal. Agora: ativa antes, e so'
    se isso torna a comandante conjuravel."""
    if ("Orb of Dragonkind" not in state.battlefield or state.orb_dragonkind_used_this_turn
            or remaining_mana(state) < 1):
        return
    spend_mana(state, 1)
    state.dragon_mana_pool += 2
    if can_cast(state, COMMANDER):
        state.orb_dragonkind_used_this_turn = True
        state.orb_mana_activations_total += 1
    else:
        state.dragon_mana_pool -= 2
        state.mana_spent_this_turn -= 1


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
    dragons_in_hand = [n for n in state.hand if is_dragon_card(n)]
    if dragons_in_hand:
        spend_mana(state, 1)
        state.dragon_mana_pool += 2
        state.orb_mana_activations_total += 1
    else:
        # CORRIGIDO 2026-09-28: "Look at the top SEVEN cards of your library.
        # You may reveal a Dragon card from among them ... Put the rest on the
        # bottom of your library in a random order." Antes buscava na
        # biblioteca inteira (tutor completo). Sem Dragao no topo 7, a Orb
        # e' sacrificada por nada -- risco real da linha.
        if not state.library:
            return
        top = state.library[:7]
        del state.library[:7]
        pool = [n for n in top if is_dragon_card(n)]
        if pool:
            best = max(pool, key=lambda n: CARD_DB[n].mv)
            top.remove(best)
            state.hand.append(best)
            state.tutors_used_total += 1
        random.Random(state.turn * 7919 + len(state.library)).shuffle(top)
        state.library.extend(top)
        spend_mana(state, 1)
        state.battlefield.remove("Orb of Dragonkind")
    state.orb_dragonkind_used_this_turn = True


def create_permanent(state: GameState, name: str):
    state.battlefield.append(name)


def apply_riot(state: GameState, name: str, has_haste_now: bool = False):
    """Rhythm of the Wild: "Nontoken creatures you control have riot (They
    enter with your choice of a +1/+1 counter or haste.)" CORRIGIDO
    2026-09-28: era sempre haste. Escolha real: haste so' quando ela vai
    atacar AGORA (entra na main 1 sem outra fonte de haste); senao o
    contador (+1 de poder pro resto do jogo -- conta ja' na entrada pra
    Elemental Bond/Garruk's/Temur/Terror, porque "enters with")."""
    if "Rhythm of the Wild" not in state.battlefield:
        return
    own_haste = (has_haste_now or "haste" in CARD_DB[name].tags or "Temur Ascendancy" in state.battlefield
                 or ("Dragon Tempest" in state.battlefield and has_flying(name)))
    if state.phase == "main1" and not own_haste and effective_power(state, name) > 0:
        state.riot_haste.add(name)
    else:
        state.riot_counters[name] = state.riot_counters.get(name, 0) + 1


def bladewing_killer(state: GameState) -> Optional[str]:
    """Quem mata a Bladewing (4/4) no loop. Terror of the Peaks: dano = poder
    da propria Bladewing, que e' igual a' resistencia (buffs de Morophon/
    Henge/riot sao +1/+1). Scourge of Valkas e Dragon Tempest: "deals X
    damage to any target" -- X = Dragoes em campo, precisa X >= resistencia
    (📝 variante pela regra; o Commander Spellbook lista so' a da Terror)."""
    toughness = effective_power(state, "Bladewing the Risen") if "Bladewing the Risen" in state.battlefield else 4
    if sources(state, "Terror of the Peaks"):
        return "Terror of the Peaks"
    if sources(state, "Scourge of Valkas") and dragon_count(state) >= toughness:
        return "Scourge of Valkas"
    if "Dragon Tempest" in state.battlefield and dragon_count(state) >= toughness:
        return "Dragon Tempest"
    return None


def bladewing_loop_ready(state: GameState) -> bool:
    return (sources(state, "Miirym, Sentinel Wyrm") > 0 and "Bladewing the Risen" in state.battlefield
            and bladewing_killer(state) is not None and not state.game_over)


def try_bladewing_loop(state: GameState):
    """Infinito Miirym, Sentinel Wyrm + Bladewing the Risen + Terror of the
    Peaks (Commander Spellbook 380-1110-3362; na auditoria.md desde
    2026-08-27 e NUNCA modelado -- a Terror so' mirava oponente, entao a
    Bladewing nunca morria). CORRIGIDO 2026-09-28. Passos (Spellbook):
    Bladewing entra -> a Terror mira a PROPRIA Bladewing (dano = poder = 4)
    -> ela morre -> a copia-ficha da Miirym entra -> Terror dispara de novo
    (no oponente) -> o ETB da copia devolve a Bladewing -> repete.
    Cada volta: a Bladewing volta (gatilhos de entrada dela, menos o que a
    mata), +1 copia-ficha 4/4 por gatilho da Miirym (gatilhos de entrada no
    oponente), fichas da Lathliss, e as compras OBRIGATORIAS (Elemental
    Bond, Garruk's Uprising, Great Henge). Para no letal, no deck-out, ou
    quando a proxima volta decaria (o piloto mira o oponente em vez da
    Bladewing e encerra). 📝 A entrada que abre o loop ja' foi processada
    pelo caminho normal com o gatilho do matador indo no oponente (1 gatilho
    a mais de dano, uma vez); o ETB da propria carta (devolver OUTRO Dragao)
    nao e' usado dentro do loop."""
    if not bladewing_loop_ready(state):
        return
    state.in_bladewing_loop = True
    if state.bladewing_loop_turn is None:
        state.bladewing_loop_turn = state.turn
    throne = roaming_throne_times(state)
    copies = sources(state, "Miirym, Sentinel Wyrm") * throne
    lathliss = sources(state, "Lathliss, Dragon Queen") * throne
    bond = 1 if "Elemental Bond" in state.battlefield else 0
    uprising = 1 if "Garruk's Uprising" in state.battlefield else 0
    henge = 1 if "The Great Henge" in state.battlefield else 0
    draws_per_loop = (bond + uprising) * (1 + copies + lathliss) + henge

    def entry_triggers(power: int, killer: Optional[str]):
        """Gatilhos de 1 Dragao entrando; `killer` = o gatilho que vai na
        Bladewing (nao no oponente)."""
        used = killer is None
        x = dragon_count(state)
        for _ in range(sources(state, "Scourge of Valkas") * throne):
            if not used and killer == "Scourge of Valkas":
                used = True
            else:
                proxy_drain(state, x)
        if "Dragon Tempest" in state.battlefield:
            if not used and killer == "Dragon Tempest":
                used = True
            else:
                proxy_drain(state, x)
        for _ in range(sources(state, "Terror of the Peaks") * throne):
            if not used and killer == "Terror of the Peaks":
                used = True
            else:
                proxy_drain(state, power)
        if "Dragon's Hoard" in state.battlefield:
            state.dragon_hoard_gold_counters += 1
        if bond and power >= 3:
            draw_cards(state, 1)
        if uprising and power >= 4:
            draw_cards(state, 1)

    for _ in range(400):
        if state.proxy_damage_total + state.combat_damage_proxy_total >= LETHAL_PROXY or state.game_over:
            break
        killer = bladewing_killer(state)
        if killer is None or len(state.library) - 1 < draws_per_loop:
            break
        # 1) o gatilho do matador (da entrada anterior) mata a Bladewing
        state.battlefield.remove("Bladewing the Risen")
        state.graveyard.append("Bladewing the Risen")
        # 2) o ETB da copia-ficha devolve a Bladewing; ela entra de novo
        state.graveyard.remove("Bladewing the Risen")
        state.battlefield.append("Bladewing the Risen")
        state.creature_cast_turn["Bladewing the Risen"] = state.turn
        if henge:
            draw_cards(state, 1)
            state.great_henge_counters["Bladewing the Risen"] = state.great_henge_counters.get("Bladewing the Risen", 0) + 1
        entry_triggers(effective_power(state, "Bladewing the Risen"), killer)
        for _ in range(lathliss):
            create_dragon_tokens(state, 1, 5, source="lathliss")
        # 3) a Miirym copia a Bladewing que entrou: cada ficha dispara no oponente
        for _ in range(copies):
            p = 4 + sources(state, "Morophon, the Boundless")
            if len(state.dragon_token_list) < DRAGON_TOKEN_CAP:
                state.dragon_token_list.append([4, state.turn, True, "Bladewing the Risen"])
                state.dragon_tokens += 1
                state.dragon_tokens_created_total += 1
            entry_triggers(p, None)
        state.bladewing_loop_iterations_total += 1
    state.in_bladewing_loop = False


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
            #
            # Achado 2026-09-20 (modo de resiliencia/counterspell): o
            # incremento de `commander_cast_count` (taxa) MOVEU pra
            # `cast_card()`, ANTES do check de counterspell -- CR 903.10a
            # conta "vezes CONJURADO", nao "vezes RESOLVIDO", entao a
            # taxa tem que subir mesmo se este `enter_battlefield` nunca
            # chegar a rodar (spell contra-atacado). So' resta aqui
            # marcar o turno da PRIMEIRA resolucao real.
            if state.commander_cast_turn is None:
                state.commander_cast_turn = state.turn
    if is_creature_card(name):
        state.creature_cast_turn[name] = state.turn
        apply_riot(state, name, has_haste_now=(name == COMMANDER and not count_as_cast))
    if name == "Firdoch Core":
        state.firdoch_entered_turn = state.turn
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
    if name == "Bladewing the Risen" and not state.in_bladewing_loop:
        try_bladewing_loop(state)


# Tiamat: quais 5 Dragoes buscar -- pelos motores do deck (Regra #4): dano de
# ETB que escala com Dragoes primeiro, depois geradores de ficha/copia, depois
# mana/valor em ataque, depois corpos. 📝 politica fixa (nao olha a mao/campo
# alem de "ainda esta' na biblioteca").
TIAMAT_TUTOR_PRIORITY = (
    "Scourge of Valkas", "Terror of the Peaks", "Lathliss, Dragon Queen", "Miirym, Sentinel Wyrm",
    "Utvara Hellkite", "Old Gnawbone", "Goldspan Dragon", "Atarka, World Render",
    "Ancient Copper Dragon", "Klauth, Unrivaled Ancient", "Twinflame Tyrant", "Hellkite Charger",
    "Ancient Gold Dragon", "Savage Ventmaw", "Balefire Dragon", "Dragon Broodmother",
    "Morophon, the Boundless", "Bladewing the Risen", "Dragonlord Dromoka", "Hellkite Courser",
)


def tiamat_tutor(state: GameState):
    """"search your library for up to five Dragon cards not named Tiamat
    that each have different names ... put them into your hand" -- so' quando
    CONJURADA (cast_card). Entrada gratis (ataque da Ur-Dragon, Magda,
    Bladewing, Haunting Voyage, Sarkhan Unbroken -8, copia da Miirym) NAO
    dispara."""
    order = [n for n in TIAMAT_TUTOR_PRIORITY if n in state.library]
    order += sorted({n for n in state.library if is_dragon_card(n) and n != "Tiamat"} - set(order),
                    key=lambda n: -CARD_DB[n].mv)
    picked = []
    for n in order:
        if n != "Tiamat" and n not in picked:
            picked.append(n)
        if len(picked) == 5:
            break
    for n in picked:
        state.library.remove(n)
        state.hand.append(n)
    state.tiamat_tutored_total += len(picked)
    state.tutors_used_total += 1


def path_scry(state: GameState):
    """Path of Ancestry: "When that mana is spent to cast a creature spell that
    shares a creature type with your commander, scry 1." CORRIGIDO
    2026-09-28: estava fora "por valor baixo" (julgamento de valor, Regra
    #1). O Path vira 1x por turno; assume-se que a mana dele vai pra 1a
    magia de criatura Dragao do turno. Politica de scry (📝): manda terreno
    pro fundo com 8+ terrenos (campo + mao); manda magia pro fundo com menos
    de 4."""
    state.path_scry_turn = state.turn
    state.path_scries_total += 1
    if not state.library:
        return
    lands = sum(1 for n in state.battlefield if n in LAND_NAMES) + sum(1 for n in state.hand if n in LAND_NAMES)
    top = state.library[0]
    if (top in LAND_NAMES and lands >= 8) or (top not in LAND_NAMES and lands < 4):
        state.library.append(state.library.pop(0))
        state.path_scry_bottoms_total += 1


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
        spend_mana(state, cost)  # `effective_cost` ja' inclui a taxa
        # Modo opcional de resiliencia (counterspell, 2026-09-20): a taxa
        # conta "vezes CONJURADO" (CR 903.10a), entao sobe aqui, ANTES do
        # check de counter -- mana e taxa ja' foram cobradas de verdade
        # mesmo se o spell for contra-atacado a seguir (mesmo padrao do
        # Megatron). Sem `interaction_rng` (goldfish padrao),
        # `try_smart_opponent_counter` retorna False sempre, 0 impacto.
        state.commander_cast_count += 1
        if try_smart_opponent_counter(state):
            return
    else:
        if is_dragon_card(name) and state.dragon_mana_pool > 0:
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
        land_enters(state, name)
        return

    if (is_creature_card(name) and is_dragon_card(name) and "Path of Ancestry" in state.battlefield
            and "Path of Ancestry" not in state.tapped_lands_this_turn and state.path_scry_turn != state.turn):
        path_scry(state)

    if "Up the Beanstalk" in state.battlefield and card.mv >= 5:
        # Achado real 2026-08-27: gatilho recorrente de Up the Beanstalk
        # ("whenever you cast a spell with mana value 5 or greater, draw
        # a card") — usa mv REAL impresso, nao o custo com desconto (MV
        # nao muda com desconto de custo, regra real).
        draw_cards(state, 1)

    if name == "Anguished Unmaking":
        pay_life(state, 3, "anguished_unmaking")  # "You lose 3 life."
    if name == "Arcane Denial":
        # "You draw a card at the beginning of the next turn's upkeep." -- o
        # proximo turno e' de um oponente; a carta chega antes do meu turno.
        state.pending_upkeep_draws += 1
    if card.ctype in ("instant", "sorcery"):
        resolve_instant_sorcery(state, name)
        state.graveyard.append(name)
        return

    enter_battlefield(state, name, from_hand=False)
    if name == "Tiamat":
        state.tiamat_casts += 1
        # Roaming Throne (tipo Dragon): Tiamat e' "another creature you
        # control of the chosen type" -> o gatilho de busca dispara 2x
        # (cada resolucao busca ate' 5 nomes diferentes de novo).
        for _ in range(roaming_throne_times(state)):
            tiamat_tutor(state)


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
        # slow land: "enters tapped unless you control two or more OTHER
        # lands" -- contado em `land_enters` antes do append.
        land_enters(state, choice)


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
    if not state.commander_in_play and not can_cast(state, COMMANDER):
        try_orb_mana_for_commander(state)
    if not state.commander_in_play and can_cast(state, COMMANDER):
        cast_card(state, COMMANDER)

    do_orb_dragonkind(state)
    try_sarkhan_unbroken(state)

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
            and remaining_mana(state) >= 7 and has_color_sources_for(state, "Haunting Voyage")):
        # CORRIGIDO 2026-09-28: {5}{B}{B} -- o {B}{B} nunca era checado; e' uma
        # magia de MV 6 conjurada (dispara Up the Beanstalk).
        state.haunting_voyage_foretold_turn = None
        spend_mana(state, 7)
        if "Up the Beanstalk" in state.battlefield:
            draw_cards(state, 1)
        reanimate_dragons_from_graveyard(state, limit=None)
        state.graveyard.append("Haunting Voyage")

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
        if not state.commander_in_play and can_cast(state, COMMANDER):
            # CORRIGIDO 2026-09-28 (Regra #6): a comandante so' era checada no
            # INICIO de cada fase principal. Sol Ring/Treasure/Orb conjurados no
            # loop a deixavam conjuravel, mas o loop gastava a mana em outra
            # coisa e ela so' saia na main 2 (ou no turno seguinte).
            cast_card(state, COMMANDER)
            continue
        castables = [n for n in state.hand if n not in LAND_NAMES and can_cast(state, n)
                     and not (CARD_DB[n].tags & REACTIVE_NO_TARGET)
                     and not (n == "Return of the Wildspeaker" and (state.phase == "main1" or library_low(state)))]
        if not castables:
            break
        def prio(n):
            tags = CARD_DB[n].tags
            group = 0 if (tags & {"rock1", "rock2", "rock_any", "land_tutor1", "land_tutor2", "land_tutor2_direct", "dork_flat1"}) else 1
            return (group, effective_cost(state, n))
        castables.sort(key=prio)
        cast_card(state, castables[0])
        if castables[0] == "Sarkhan Unbroken":
            try_sarkhan_unbroken(state)  # planeswalker ativa no turno em que entra

    check_color_screw(state)

    if "Ramos, Dragon Engine" in state.battlefield and state.ramos_counters >= 5:
        # Achado real 2026-08-28 (auditoria de checklist): "Remove five
        # +1/+1 counters from Ramos: Add..." - SEM {T} no custo real. Doenca
        # de invocacao so afeta habilidades com {T} (CR 302.6); o gate por
        # ready_creatures() estava errado, bloqueava a ativacao no proprio
        # turno em que Ramos entra mesmo com 5+ contadores.
        state.ramos_counters -= 5
        state.bonus_mana_pool += 10

    try_magda_sacrifice(state)
    try_haven_recursion(state)
    try_dragon_hoard_draw(state)
    if state.phase == "main1":
        # CORRIGIDO 2026-09-28: os pumps rodavam tambem no fim da main 2, depois
        # do combate -- mana gasta em nada.
        try_firdoch_animate(state)
        try_dragon_pumps(state)
        choose_sarkhan_copy(state)
    try_lightning_greaves_equip(state)
    if state.phase == "main2":
        try_triome_cycling(state)


def try_sarkhan_unbroken(state: GameState):
    """CORRIGIDO 2026-09-28 (Regra #6): a ativacao rodava DEPOIS do loop de
    conjuracao -- o "+1: Draw a card, then add one mana of any color" so'
    ficava gastavel na 2a fase principal. Agora ativa antes do loop."""
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
                targets = [n for n in state.library if is_dragon_card(n) and is_creature_card(n)]
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
            elif library_low(state) and loyalty >= 2:
                # 📝 grimorio baixo: o +1 compra (obrigatorio na habilidade) -> -2.
                state.sarkhan_loyalty = loyalty - 2
                create_dragon_tokens(state, 1, 4, source="sarkhan_unbroken")
                if state.sarkhan_loyalty <= 0:
                    state.battlefield.remove("Sarkhan Unbroken")
                    state.graveyard.append("Sarkhan Unbroken")
            else:
                state.sarkhan_loyalty = loyalty + 1
                draw_cards(state, 1)
                state.bonus_mana_pool += 1
                state.bonus_colored.append(set("WUBRG"))  # "add one mana of any color"


def has_pips_for_dragon_ability(state: GameState, pips: dict) -> bool:
    """Custo colorido de habilidade ATIVADA de Dragao (Lathliss {1}{R},
    Bladewing {B}{R}, Scourge {R}). CORRIGIDO 2026-09-28: a cor nunca era
    checada. Secluded Courtyard ("...or activate an ability of a creature
    source of the chosen type") e a mana da Orb ("or activate abilities of
    Dragons") pagam qualquer cor aqui; Cavern e Haven nao."""
    sets = (source_color_sets(state) + state.bonus_colored
            + [set("WUBRG")] * (treasure_unspent(state) * treasure_mana_each(state)))
    if "Secluded Courtyard" in state.battlefield and "Secluded Courtyard" not in state.tapped_lands_this_turn:
        sets.append(set("WUBRG"))
    sets += [set("WUBRG")] * state.dragon_mana_pool
    colors = list(pips)
    for mask in range(1, 1 << len(colors)):
        sub = {colors[i] for i in range(len(colors)) if mask >> i & 1}
        if sum(pips[c] for c in sub) > sum(1 for src in sets if src & sub):
            return False
    return True


def try_dragon_pumps(state: GameState):
    """3 ativacoes repetiveis de pump de Dragao, achado 2026-08-30 (pedido
    explicito do usuario: "efeito de todas as criaturas implementado").
    Cada uma rastreada como sua propria ativacao (nao dano de combate
    calculado - este simulador nao modela combate individual criatura a
    criatura em nenhum outro lugar, mesmo tratamento ja usado pros
    finishers repetiveis de Beorn/Thranduil nesta sessao). 1x/turno cada,
    quando ha mana sobrando e um alvo real pra beneficiar."""
    if ("Lathliss, Dragon Queen" in state.battlefield and remaining_mana(state) >= 2 and dragon_count(state) >= 1
            and has_pips_for_dragon_ability(state, {"R": 1})):
        spend_mana(state, 2)
        state.lathliss_pumps += 1
        state.dragon_pump_bonus_this_turn += 1  # "Dragons you control get +1/+0 until end of turn"

    if ("Bladewing the Risen" in state.battlefield and remaining_mana(state) >= 2 and dragon_count(state) >= 1
            and has_pips_for_dragon_ability(state, {"B": 1, "R": 1})):
        spend_mana(state, 2)
        state.bladewing_pumps += 1
        state.dragon_pump_bonus_this_turn += 1  # "Dragons you control get +1/+1 until end of turn"

    if ("Scourge of Valkas" in state.battlefield and remaining_mana(state) >= 1
            and has_pips_for_dragon_ability(state, {"R": 1})):
        spend_mana(state, 1)
        state.scourge_self_pumps += 1
        state.scourge_pump_this_turn += 1       # "{R}: This creature gets +1/+0 until end of turn"


def try_triome_cycling(state: GameState):
    """Jetmir's Garden / Ketria / Zagoth / Ziatora's: "Cycling {3} ({3},
    Discard this card: Draw a card.)" -- CORRIGIDO 2026-09-28: custo
    alternativo real, nunca modelado. Politica (📝): so' na main 2, com a
    mana que sobrou, e so' com 7+ terrenos em campo ou outro terreno na mao
    pro proximo land drop."""
    while remaining_mana(state) >= 3 and not library_low(state):
        triomes = [n for n in state.hand if n in CYCLING_TRIOMES]
        lands_in_play = sum(1 for n in state.battlefield if n in LAND_NAMES)
        other_lands = sum(1 for n in state.hand if n in LAND_NAMES) - 1
        if not triomes or not (lands_in_play >= 7 or other_lands >= 1):
            return
        state.hand.remove(triomes[0])
        state.graveyard.append(triomes[0])
        spend_mana(state, 3)
        draw_cards(state, 1)
        state.triome_cycles_total += 1


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
    # CORRIGIDO 2026-09-28: so' re-equipava se o alvo antigo saisse de campo --
    # equipada num Birds no T2, nunca ia pra Ur-Dragon. Equip {0} e'
    # repetivel na velocidade de feitico: a cada fase principal vai pra
    # criatura que mais ganha com haste AGORA (entrou neste turno, sem
    # haste propria, maior poder; a comandante empata na frente); sem
    # ninguem assim, fica na comandante (shroud contra remocao).
    fresh = [n for n in state.battlefield if is_creature_card(n) and state.creature_cast_turn.get(n, -1) == state.turn
             and "haste" not in CARD_DB[n].tags and n not in state.riot_haste]
    if fresh and state.phase == "main1":
        state.lightning_greaves_equipped_to = max(fresh, key=lambda n: (n == COMMANDER, effective_power(state, n)))
        return
    if COMMANDER in state.battlefield:
        state.lightning_greaves_equipped_to = COMMANDER
        return
    if state.lightning_greaves_equipped_to not in state.battlefield:
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
    targets = [c for c in state.graveyard if is_dragon_card(c) and is_creature_card(c)]
    if not targets:
        return
    lands_in_play = sum(1 for n in state.battlefield if n in LAND_NAMES)
    if lands_in_play < 3 or remaining_mana(state) < 2:
        return
    spend_mana(state, 2)
    state.battlefield.remove(HAVEN_RECURSION_LAND)
    best = max(targets, key=lambda n: CARD_DB[n].mv)
    if "Tiamat" in targets and any(is_dragon_card(n) and n != "Tiamat" for n in state.library):
        # Candidata (so' via swap): volta pra MAO -> reconjurar busca mais 5.
        best = "Tiamat"
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
    if state.dragon_hoard_gold_counters <= 0 or state.hoard_tapped_turn == state.turn or library_low(state):
        return
    if remaining_mana(state) < 1:
        return
    # CORRIGIDO 2026-09-28: main_phase roda 2x por turno e a Hoard comprava nas
    # duas -- o {T} e' um so'. E a mana dela (contada no total) sai do turno.
    state.hoard_tapped_turn = state.turn
    spend_mana(state, 1)
    state.dragon_hoard_gold_counters -= 1
    draw_cards(state, 1)
    state.dragon_hoard_draws_total += 1


def do_magda_treasures(state: GameState, bodies: Optional[list] = None):
    """Magda, Brazen Outlaw: "Whenever a Dwarf you control becomes tapped,
    create a Treasure token." (ruling 2021-02-05: precisa mudar de virado pra
    desvirado, e o gatilho nao deixa VOCE virar nada -- atacar e' a via.)

    CORRIGIDO 2026-09-28 (Regra #3, conceito "Dwarf que voce controla"): so'
    a Magda e o Firdoch Core contavam. Todo Dwarf que fica virado gera 1
    Treasure por vez:
    - a Magda atacando (2/1);
    - **Firdoch Core** virando pra mana, 1x por turno (Changeling = Dwarf em
      toda zona; e' artefato: sem doenca de invocacao) -- se ele foi animado
      e ataca, o ataque e' o tap (ainda 1x por turno);
    - **Morophon** (Changeling) atacando, e fichas-copia dele/do Firdoch da
      Miirym; o Sarkhan, Soul Aflame copiando Morophon;
    - cada combate EXTRA (Hellkite Charger "untap all attacking creatures"):
      os Dwarves atacantes desviram e viram de novo.
    Os Treasures vao pro estoque compartilhado (`treasure_stock`) e o tutor
    ("Sacrifice five Treasures") e' `try_magda_sacrifice`."""
    if "Magda, Brazen Outlaw" not in state.battlefield:
        return
    if bodies is None:
        bodies = attacking_bodies(state)
    magdas = state.battlefield.count("Magda, Brazen Outlaw")  # cada Magda dispara por Dwarf que vira
    attackers = [b[3] for b in bodies]
    by_src = {"magda": 0, "morophon": 0, "firdoch": 0}
    if "Magda, Brazen Outlaw" in attackers:
        by_src["magda"] += 1
    by_src["morophon"] += sum(1 for n in attackers if n == "Morophon, the Boundless")
    by_src["morophon"] += sum(1 for n in attackers if n == SARKHAN_SA and state.sarkhan_copy_of == "Morophon, the Boundless")
    by_src["morophon"] += sum(1 for t in state.dragon_token_list
                              if len(t) > 3 and t[3] == "Morophon, the Boundless" and t in ready_dragon_tokens(state))
    if state.magda_firdoch_tap_turn != state.turn:
        # Firdoch Core (e copias): {T}: Add one mana of any color -- 1x por turno.
        state.magda_firdoch_tap_turn = state.turn
        by_src["firdoch"] += (1 if "Firdoch Core" in state.battlefield else 0) + state.firdoch_token_copies
    taps = sum(by_src.values()) * magdas
    if taps == 0:
        return
    for k, v in by_src.items():
        if v:
            state.magda_sources[k] = state.magda_sources.get(k, 0) + v * magdas
    create_and_use_treasures(state, taps)


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
    runaway.

    CORRIGIDO 2026-09-28: o teto de 1 combate extra cortava o infinito
    Old Gnawbone + Hellkite Charger (Commander Spellbook 1800-3398,
    registrado na auditoria.md desde 2026-08-27): cada combate da' Treasure
    = dano da Gnawbone + Charger (>= 12), que paga o {5}{R}{R} do proximo.
    O teto natural e' o letal (ou a mana acabar / o deck-out -- o gatilho da
    Ur-Dragon compra a cada combate, e `limit_attackers_for_library` segura
    atacantes). 60 combates e' so' trava de seguranca do simulador."""
    for _ in range(60):
        if "Hellkite Charger" not in state.battlefield or state.game_over:
            return
        if "Hellkite Charger" not in ready_creatures(state):
            return
        if remaining_mana(state) < 7 or color_sources(state, "R") < 2:
            return
        if state.proxy_damage_total + state.combat_damage_proxy_total >= LETHAL_PROXY:
            return  # ja' e' letal: o piloto para
        state.mana_spent_this_turn += 7
        state.hellkite_charger_extra_combats += 1
        combat_step(state)


def attacking_bodies(state: GameState):
    """Todo corpo que ataca neste combate: (tags da habilidade, poder, e'
    Dragao, nome). Nomeados prontos que sao Dragao (Sarkhan copiando conta),
    fichas prontas (copia da Miirym leva as tags da carta copiada), Magda
    (o gatilho de Treasure dela ja' assumia que ela ataca -- CORRIGIDO
    2026-09-28: o dano dela nunca era somado) e Firdoch Core animado."""
    pump = state.dragon_pump_bonus_this_turn
    bodies = []
    for n in ready_creatures(state):
        if is_dragon_perm(state, n):
            tag_src = state.sarkhan_copy_of if n == SARKHAN_SA else n
            p = effective_power(state, n) + pump + (state.scourge_pump_this_turn if n == "Scourge of Valkas" else 0)
            bodies.append((CARD_DB[tag_src].tags, p, True, n))
        elif n == "Magda, Brazen Outlaw":
            bodies.append((CARD_DB[n].tags, effective_power(state, n), False, n))
    for t in ready_dragon_tokens(state):
        copy_of = t[3] if len(t) > 3 else None
        tags = CARD_DB[copy_of].tags if copy_of else frozenset()
        bodies.append((tags, token_effective_power(state, t[0], copy_of), True, copy_of or "token"))
    if state.firdoch_animated_turn == state.turn:
        # "{4}: This artifact becomes a 4/4 artifact creature until end of turn"
        # (Changeling: Dragao). Morophon da' +1/+1 (criatura do tipo escolhido).
        p = 4 + sources(state, "Morophon, the Boundless") + pump
        bodies.append((frozenset(), p, True, "Firdoch Core"))
    return bodies


def roll_d20(state: GameState) -> int:
    """d20 de verdade (CORRIGIDO 2026-09-28: era 10 fixo, abaixo da media 10,5
    e sem variancia). RNG proprio, separado do embaralhamento."""
    if state.dice_rng is None:
        return 10
    return state.dice_rng.randint(1, 20)


def limit_attackers_for_library(state: GameState, bodies: list) -> list:
    """CR 704.5b + "draw that many cards" obrigatorio: o piloto escolhe os
    atacantes. Cada Dragao atacando custa `d` compras obrigatorias (gatilho da
    Ur-Dragon x fontes x Throne, + fichas da Utvara x Elemental Bond/Garruk's
    Uprising). Ataca com no maximo (grimorio - 1) / d Dragoes -- guarda 1 pro
    proximo passo de compra -- os mais fortes primeiro. CORRIGIDO 2026-09-28:
    antes atacava com tudo e marcava letal em partida que decaria."""
    throne = roaming_throne_times(state)
    d = sources(state, COMMANDER) * throne
    per_token = (1 if "Elemental Bond" in state.battlefield else 0) + (1 if "Garruk's Uprising" in state.battlefield else 0)
    d += sources(state, "Utvara Hellkite") * throne * per_token
    dragons = [b for b in bodies if b[2]]
    if d == 0 or not dragons:
        return bodies
    n_max = max(0, (len(state.library) - 1) // d)
    if n_max >= len(dragons):
        return bodies
    keep = sorted(dragons, key=lambda b: (b[1] + (5 if b[0] & {"attack_treasure", "combat_treasure_d20", "combat_token_d20",
                                                                 "attack_mana_power", "attack_mana_flat"} else 0)),
                  reverse=True)[:n_max]
    state.attackers_held_back_total += len(dragons) - n_max
    return [b for b in bodies if not b[2]] + keep


def combat_step(state: GameState):
    bodies = limit_attackers_for_library(state, attacking_bodies(state))
    do_magda_treasures(state, bodies)
    dragon_bodies = [b for b in bodies if b[2]]
    if not bodies:
        return
    n_attacking = len(dragon_bodies)
    throne = roaming_throne_times(state)
    atarka = sources(state, "Atarka, World Render") > 0
    tf = twinflame_factor(state)

    def ds(is_dragon_body):  # Atarka: "Whenever a DRAGON you control attacks, it gains double strike"
        return 2 if (atarka and is_dragon_body) else 1

    if n_attacking and "Kindred Discovery" in state.battlefield:
        draw_cards(state, n_attacking)

    # The Ur-Dragon: "Whenever one or more Dragons you control attack, draw that
    # many cards, then you may put a permanent card from your hand onto the
    # battlefield." CORRIGIDO 2026-09-28: (1) a Roaming Throne dobra este
    # gatilho sempre que a Ur-Dragon esta' em campo -- antes so' se ELA
    # atacasse; (2) ficha-copia da Ur-Dragon (Miirym) tem o mesmo gatilho.
    ur_sources = sources(state, COMMANDER)
    if n_attacking:
        for _ in range(ur_sources * throne):
            draw_cards(state, n_attacking)
            state.urdragon_attack_draws_total += n_attacking
            permanents_in_hand = [c for c in state.hand if CARD_DB[c].ctype != "instant" and CARD_DB[c].ctype != "sorcery"]
            # Tiamat so' busca os 5 Dragoes se CONJURADA: por de graca aqui joga o
            # tutor fora. So' entra por aqui se for a unica opcao e nao der pra
            # conjura-la neste turno (linha deliberada, Regra #5).
            if "Tiamat" in permanents_in_hand and (len(permanents_in_hand) > 1 or can_cast(state, "Tiamat")):
                permanents_in_hand = [c for c in permanents_in_hand if c != "Tiamat"]
            if permanents_in_hand:
                best = max(permanents_in_hand, key=lambda n: effective_cost(state, n) if n not in LAND_NAMES else 0)
                state.hand.remove(best)
                if best in LAND_NAMES:
                    if best in FETCH_TARGETS:
                        crack_fetch(state, best)
                    else:
                        land_enters(state, best)
                else:
                    enter_battlefield(state, best, from_hand=False)
                    if is_dragon(best):
                        state.dragons_free_entry_total += 1
                state.urdragon_free_permanents_total += 1

    # Return of the Wildspeaker, 2o modo: "Non-Human creatures you control get
    # +3/+3 until end of turn." CORRIGIDO 2026-09-28: so' o modo de compra
    # existia. Instantanea: depois de declarar ataque, se o +3 fecha o letal
    # proxy neste turno, e' a linha (📝); senao fica pro modo de compra na main 2.
    rotw_bonus = 0
    if "Return of the Wildspeaker" in state.hand and can_cast(state, "Return of the Wildspeaker"):
        non_human = [b for b in bodies if not (b[3] in HUMAN_CREATURE_NAMES and not (b[3] == SARKHAN_SA and state.sarkhan_copy_of))]
        base_dmg = sum(b[1] * ds(b[2]) for b in bodies) * tf
        pump_dmg = sum(3 * ds(b[2]) for b in non_human) * tf
        done = state.proxy_damage_total + state.combat_damage_proxy_total
        if done + base_dmg < LETHAL_PROXY <= done + base_dmg + pump_dmg:
            spend_mana(state, effective_cost(state, "Return of the Wildspeaker"))
            state.hand.remove("Return of the Wildspeaker")
            state.graveyard.append("Return of the Wildspeaker")
            if "Up the Beanstalk" in state.battlefield:
                draw_cards(state, 1)
            state.rotw_pumps_total += 1
            rotw_bonus = 3
            bodies = [(b[0], b[1] + (3 if b in non_human else 0), b[2], b[3]) for b in bodies]

    total_attack_power = sum(b[1] for b in bodies)

    # CR 903.10a - dano de combate da propria comandante (Atarka dobra por
    # double strike; CORRIGIDO 2026-09-28: pumps da Lathliss/Bladewing e a
    # Twinflame -- "deals double that damage" -- tambem contam).
    if COMMANDER in state.battlefield and COMMANDER in [b[3] for b in bodies]:
        cmd = next(b for b in bodies if b[3] == COMMANDER)
        state.commander_damage_dealt += cmd[1] * ds(True) * tf
        if state.commander_damage_dealt >= 21:
            state.commander_damage_win = True

    for tags, power, is_dragon_body, name in bodies:
        # gatilhos do PROPRIO atacante ("Whenever THIS creature attacks / deals
        # combat damage"); ficha-copia e Sarkhan copiando levam as tags da carta.
        times = throne if is_dragon_body and name != "Roaming Throne" else 1
        dmg_times = times * ds(is_dragon_body)
        if "attack_treasure" in tags:
            for _ in range(times):
                create_and_use_treasures(state, 1)
        if "combat_treasure_d20" in tags:
            for _ in range(dmg_times):
                create_and_use_treasures(state, roll_d20(state))
        if "combat_token_d20" in tags:
            # "create a number of 1/1 blue Faerie Dragon creature tokens with flying"
            for _ in range(dmg_times):
                create_dragon_tokens(state, roll_d20(state), 1, source="faerie_dragon")
        if "attack_mana_power" in tags:
            # Klauth: X = poder TOTAL das criaturas atacantes.
            for _ in range(times):
                state.bonus_mana_pool += total_attack_power
                state.bonus_colored.extend([set("WUBRG")] * total_attack_power)  # "any combination of colors"
        if "attack_mana_flat" in tags:
            for _ in range(times):
                state.bonus_mana_pool += 6
                state.bonus_colored.extend([{"R"}] * 3 + [{"G"}] * 3)  # {R}{R}{R}{G}{G}{G}
        if name == "Balefire Dragon" or (name == SARKHAN_SA and state.sarkhan_copy_of == "Balefire Dragon"):
            state.balefire_hits_total += 1  # 📊 wipe unilateral: board de oponente nao modelado

    # Utvara Hellkite: "Whenever a Dragon you control attacks, create a 6/6" --
    # cada Utvara (copias inclusas) dispara por Dragao atacante.
    utvara = sources(state, "Utvara Hellkite")
    if utvara and n_attacking:
        create_dragon_tokens(state, n_attacking * utvara * throne, 6, source="utvara")
    # Old Gnawbone: "Whenever a creature you control deals combat damage to a
    # player, create THAT MANY Treasure tokens" -- "that many" = dano causado:
    # double strike e Twinflame (CORRIGIDO 2026-09-28) contam.
    gnawbone = sources(state, "Old Gnawbone")
    damage_dealt = sum(b[1] * ds(b[2]) for b in bodies) * tf
    if gnawbone:
        for _ in range(gnawbone * throne):
            create_and_use_treasures(state, damage_dealt)

    state.combat_damage_proxy_total += damage_dealt
    # Dragonlord Dromoka: "Flying, lifelink" (copias inclusas).
    for tags, power, is_dragon_body, name in bodies:
        if name == "Dragonlord Dromoka" or (name == SARKHAN_SA and state.sarkhan_copy_of == "Dragonlord Dromoka"):
            gain = power * ds(True) * tf
            gain_life(state, gain, "dromoka_lifelink")
            state.dromoka_lifelink_total += gain


def try_firdoch_animate(state: GameState):
    """Firdoch Core: "{4}: This artifact becomes a 4/4 artifact creature until
    end of turn." CORRIGIDO 2026-09-28: nunca modelado ("nao modelado" no
    docstring). Com Changeling ele e' Dragao: conta no "draw that many" da
    Ur-Dragon, dispara Utvara, ganha double strike da Atarka. Politica (📝):
    fim da main 1, so' com 5+ de mana sobrando (4 + a mana do proprio
    Firdoch, que precisa ficar desvirado pra atacar), so' se ele esta' em
    campo desde o inicio do turno, e so' com a Ur-Dragon ou a Utvara em
    campo (onde 1 atacante a mais rende carta/ficha)."""
    if "Firdoch Core" not in state.battlefield or state.firdoch_entered_turn >= state.turn:
        return
    if state.firdoch_animated_turn == state.turn or remaining_mana(state) < 5:
        return
    if not (state.commander_in_play or sources(state, "Utvara Hellkite")):
        return
    spend_mana(state, 5)
    state.firdoch_animated_turn = state.turn


# Ramp e redutores de custo de Dragao: o que leva a comandante de 9 pra mesa.
SETUP_TAGS = {"rock1", "rock2", "rock_any", "land_tutor1", "land_tutor2", "land_tutor2_direct",
              "dork_flat1", "dragon_discount1", "dragon_discount2"}


def settle_mana_life(state: GameState):
    """Vida das fontes de mana no fim do turno (CORRIGIDO 2026-09-28):
    - The Great Henge "{T}: Add {G}{G}. You gain 2 life." -- vira todo turno;
    - Ancient Tomb ("deals 2 damage to you") e Mana Confluence ("Pay 1
      life") so' quando a mana gasta passou das fontes sem dor (📝 piloto
      vira as sem dor primeiro): 1 de vida por mana de excesso."""
    if "The Great Henge" in state.battlefield:
        gain_life(state, 2, "great_henge")
    painful = 0
    if "Ancient Tomb" in state.battlefield and "Ancient Tomb" not in state.tapped_lands_this_turn:
        painful += 2
    if "Mana Confluence" in state.battlefield and "Mana Confluence" not in state.tapped_lands_this_turn:
        painful += 1
    if painful:
        painless = total_mana(state) - painful
        pay_life(state, min(painful, max(0, state.mana_spent_this_turn - painless)), "ancient_tomb_confluence")


def end_step(state: GameState):
    state.sarkhan_copy_of = None  # "until end of turn" (cleanup)
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

    if sources(state, "Dragon Broodmother"):
        # "At the beginning of EACH upkeep, create a 1/1 red and green Dragon
        # creature token with flying and devour 2." CORRIGIDO 2026-09-25: era
        # 1 ficha por rodada (e sem gatilho de entrada). A do MEU upkeep sai
        # em `upkeep_step`; aqui as dos upkeeps dos oponentes antes do meu
        # proximo turno (entram "neste" turno, prontas pra atacar no
        # proximo). Devour: politica nunca devora (📝, nao sacrifica corpo).
        create_dragon_tokens(state, NUM_OPPONENTS * sources(state, "Dragon Broodmother") * roaming_throne_times(state), 1,
                             source="broodmother_opp_upkeep")
    # CORRIGIDO 2026-09-28 (achado na avaliacao da Tiamat, Regra #5): o
    # descarte de cleanup pegava sempre o de menor custo, terreno primeiro --
    # inclusive ANTES da comandante de 9 estar em campo, jogando fora terreno,
    # ramp e redutor de custo pra guardar Dragao de 6-8 que ainda nao da' pra
    # pagar. Nenhum piloto faz isso. Enquanto a comandante nao esta' em campo,
    # terreno/ramp/redutor so' saem se nao sobrar outra carta; fora isso a
    # ordem antiga (menor custo primeiro) continua.
    def discard_key(n):
        protected = (not state.commander_in_play
                     and (n in LAND_NAMES or bool(CARD_DB[n].tags & SETUP_TAGS) or n == "Orb of Dragonkind"))
        return (protected, effective_cost(state, n) if n not in LAND_NAMES else 0)
    while len(state.hand) > 7:
        worst = min(state.hand, key=discard_key)
        state.hand.remove(worst)
        state.graveyard.append(worst)


def upkeep_step(state: GameState):
    if sources(state, "Dragon Broodmother"):
        create_dragon_tokens(state, sources(state, "Dragon Broodmother") * roaming_throne_times(state), 1,
                             source="broodmother_my_upkeep")
    if "Herald's Horn" in state.battlefield and state.library:
        # "If it's a CREATURE card of the chosen type" -- CORRIGIDO 2026-09-28:
        # `is_dragon` aceitava Firdoch Core (Kindred Artifact) e Roaming Throne
        # (Golem na biblioteca).
        top = state.library[0]
        if is_dragon_card(top) and is_creature_card(top):
            state.library.pop(0)
            state.hand.append(top)

    # Smothering Tithe: "Whenever an opponent draws a card, that player may
    # pay {2}. If the player doesn't, you create a Treasure token." Achado
    # 2026-08-30 (pedido explicito do usuario, mesma premissa da Rhystic
    # Study no Thranduil): media fixa de 1 Treasure por turno em que a
    # Smothering Tithe esta em campo (1 oponente falhando em pagar {2} no
    # draw normal do turno, sem tentar modelar draw extra de oponentes).
    if "Smothering Tithe" in state.battlefield:
        # O gatilho real acontece no turno do OPONENTE: com a Draconic Visitor
        # a ficha de Dragao nasce la' (pronta pra atacar neste turno).
        create_and_use_treasures(state, 1, on_opp_turn=True)
        state.smothering_tithe_treasures += 1


# ---------------------------------------------------------------------------
# Modo opcional de resiliencia -- portado do Megatron (megatron-tyrant-mardu/
# megatron_goldfish_v1.py) a pedido do usuario 2026-09-20, depois de avaliar
# o esforco real num deck sem motor de sacrificio (Hei Bai) antes de decidir
# fazer no Ur-Dragon. Modo SEPARADO e OPCIONAL -- `simulate_one`/`run_batch`
# continuam exatamente como sempre foram (goldfish puro, sem oponente real,
# premissa documentada no topo do arquivo). Nenhuma funcao abaixo e' chamada
# pelo goldfish padrao.
#
# Diferencas reais vs. o port original do Megatron (nao e' copy-paste):
# 1. Sem `sacrifice()` preexistente aqui (motor do Ur-Dragon e' ETB/ataque,
#    nao sacrificio) -- `remove_permanent()` abaixo e' uma versao NOVA e mais
#    simples: sem gatilhos de morte pra replicar (grep confirmou 0 cartas
#    "whenever ~ dies" neste deck), so' precisa saber mandar o comandante pra
#    zona de comando em vez do cemiterio (mesmo padrao ja usado em `end_step`
#    pro retorno do Hellkite Courser) e o resto pro cemiterio normal.
# 2. Sem `toughness` rastreado por criatura no `Card` (so' `power`, motor do
#    deck so' precisa de poder pra calcular dano de saida) -- ataque de
#    oponente aqui NUNCA e' bloqueado (estrutural, nao e' escolha de design:
#    nao ha' dado de resistencia pra decidir se um bloqueador sobrevive).
#    Mesma convencao "sem bloqueio real modelado" que o proprio goldfish
#    padrao ja usa pro lado do jogador, agora tambem pro lado do oponente.
# 3. Sem `state.rng` guardado no state (nada neste deck precisa embaralhar
#    de volta pra biblioteca -- nenhum card tipo Blightsteel Colossus
#    encontrado na auditoria rapida desta rodada; `put_into_graveyard()`
#    abaixo fica como rede de seguranca central, sem caso especial nenhum
#    por enquanto -- diferente do Megatron, essa NAO e' uma auditoria
#    completa de "would be put into a graveyard from anywhere" nas 99
#    cartas, so' um ponto central pronto se algum caso for achado depois).
# 4. Alvo do graveyard snipe usa o MESMO criterio de
#    `reanimate_dragons_from_graveyard()` (maior MV entre Dragao-criatura no
#    cemiterio) em vez do MV entre criatura/artefato do Megatron -- a
#    recursao real deste deck (Haunting Voyage) e' Dragao-especifica, nao
#    artefato-especifica.

INTERACTION_SETUP_TURNS = 2
# Mesmo achado do Megatron: turnos 1-2 sao sempre setup, sem chance de
# reacao nenhuma -- o oponente ainda nao tem motivo/mana pra reagir.

NUM_OPPONENTS = 3
# Achado real do usuario 2026-09-20 (Regra #6 do CLAUDE.md -- bug de
# orquestracao de turno): board wipe e' sorcery, main phase de UM
# oponente; ataque vem de criatura em campo DAQUELE MESMO oponente --
# se o wipe for simetrico, ele nao ataca no mesmo turno ("nao ha
# ataques normalmente nos turnos em que ha wipes"). Mesma convencao
# `NUM_OPPONENTS=3` ja' estabelecida e documentada no Megatron (mesa
# de 4) -- ver `try_smart_opponent_turn`.

INTERACTION_ENGINE_PRIORITY = [
    "Roaming Throne",
    "Dragon Tempest",
    "Scourge of Valkas",
    "Herald's Horn",
    "Smothering Tithe",
    "Dragon's Hoard",
    "Up the Beanstalk",
    "Elemental Bond",
    "Garruk's Uprising",
    "Sylvan Library",
]
# Lista curada por prioridade (a mais critica primeiro) -- so' pecas que sao
# motor RECORRENTE de valor a cada turno/combate (dobra de gatilho, dano
# escalavel, draw todo turno, treasure todo turno), nao corpos grandes
# isolados nem bombas de 1 uso so'. Roaming Throne primeiro: dobra TODOS os
# outros gatilhos de Dragao da lista, e' o multiplicador central do deck.


def put_into_graveyard(state: GameState, name: str):
    """Ponto central pra 'vai pro cemiterio' fora do campo (descarte da
    mao, limite de mao no fim do turno) -- rede de seguranca pronta pra
    um caso tipo Blightsteel Colossus (Megatron) se algum for achado
    depois nesta lista; nenhum conhecido ainda nesta rodada."""
    state.graveyard.append(name)


def remove_permanent(state: GameState, name: str, from_battlefield: bool = True):
    """Ponto central de remocao de permanente do CAMPO (wipe/remocao do
    modo de resiliencia) -- equivalente simplificado do `sacrifice()` do
    Megatron: sem gatilhos de morte pra replicar (0 cartas 'whenever ~
    dies' neste deck, confirmado por grep -- reconfirmado 2026-09-21).

    CORRIGIDO 2026-09-21 (achado real do usuario, CR 903.9a -- ver
    `rules-cache/comprehensive-rules.txt` linhas 6888-6896, Regra 18 de
    `references/user-standing-rules.md`): comandante indo pro
    cemiterio/exilio NAO e' substituicao, e' ACAO BASEADA EM ESTADO (CR
    704) que roda DEPOIS do evento real -- ele vai pro cemiterio DE
    VERDADE primeiro (CR 700.4, "dies"), so' DEPOIS o dono PODE
    escolher move-lo pra zona de comando. A versao anterior pulava o
    cemiterio inteiramente. Sem efeito NUMERICO observavel aqui (0
    cartas 'creature dies' neste deck pra reagir), mas corrigido pra
    ficar estruturalmente certo -- uma futura troca de carta com
    gatilho de morte nao herdaria esse bug em silencio."""
    if from_battlefield and name in state.battlefield:
        state.battlefield.remove(name)
    if name == COMMANDER:
        put_into_graveyard(state, name)
        if name in state.graveyard:
            state.graveyard.remove(name)
        state.commander_in_play = False
        return
    put_into_graveyard(state, name)


def interaction_chance(state: GameState) -> float:
    """Formula compartilhada de 'chance do oponente reagir esse turno' --
    identica ao Megatron: escala com o impacto do meu proprio board
    (permanentes nao-terreno em campo)."""
    board_impact = sum(1 for n in state.battlefield if n not in LAND_NAMES)
    return min(0.10 + 0.03 * board_impact, 0.75)


BOARD_WIPE_CHANCE_FACTOR = 0.4
ARTIFACT_WIPE_CHANCE_FACTOR = 0.2
ENCHANTMENT_WIPE_CHANCE_FACTOR = 0.15
# Pesos relativos de cada TIPO de sweeper (criatura/artefato/
# encantamento) -- nao sao 3 chances INDEPENDENTES (achado real do
# usuario 2026-09-20, mesma correcao feita primeiro no Megatron: "Vandalblast,
# Farewell, Austere Command, etc" tem que existir, MAS "Obviamente tem
# que ter uma alternancia de remocoes, aleatoria, ate pq wipes de
# criaturas sao muito mais comuns que remocao de artefatos e
# encantamentos"). Um oponente real, num turno so', conjura NO MAXIMO 1
# sweeper -- nunca "destroy all creatures" E "destroy all artifacts" no
# mesmo turno. `try_smart_opponent_wipe` rola 1x se ALGUM wipe acontece
# (chance = soma dos 3 pesos) e SO' DEPOIS escolhe qual tipo, com
# escolha ponderada pelos mesmos 3 fatores -- criatura continua a mais
# comum, artefato/encantamento mais raros (Vandalblast overloaded/By
# Force/Austere Command/Farewell). Chutes razoaveis documentados,
# ajustaveis se o usuario tiver dado real de mesa.
WIPE_TYPE_WEIGHTS = {
    "creature": BOARD_WIPE_CHANCE_FACTOR,
    "artifact": ARTIFACT_WIPE_CHANCE_FACTOR,
    "enchantment": ENCHANTMENT_WIPE_CHANCE_FACTOR,
}
TOTAL_WIPE_CHANCE_FACTOR = sum(WIPE_TYPE_WEIGHTS.values())


def try_smart_opponent_wipe(state: GameState) -> Optional[list]:
    """Board wipe ("destroy all creatures"/"destroy all artifacts"/
    "destroy all enchantments") -- mesma logica do Megatron, adaptada:
    The Ur-Dragon nunca e' artefato/encantamento (Legendary Creature --
    Dragon Avatar, confirmado via Scryfall), entao nunca e' alvo dos 2
    tipos novos -- sem excecao de face necessaria (diferente do
    Megatron/Vehicle).

    Design de 2 passos (nao 3 rolagens independentes -- ver comentario
    de `WIPE_TYPE_WEIGHTS` acima): 1) rola 1x se ALGUM wipe acontece
    esse turno de oponente, chance = `interaction_chance() *
    TOTAL_WIPE_CHANCE_FACTOR`; 2) SO' se isso disparar, escolhe qual
    TIPO de sweeper via escolha ponderada (`state.interaction_rng.
    choices`) restrita aos tipos que tem pelo menos 1 alvo legal em
    campo. Se o tipo escolhido nao for "creature" mas algum alvo
    destruido TAMBEM for uma criatura de verdade (artifact/enchantment
    creature), `state.wiped_this_round` e' setado igual."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * TOTAL_WIPE_CHANCE_FACTOR:
        return None
    candidates = {
        "creature": [n for n in state.battlefield if is_creature_card(n)],
        "artifact": [n for n in state.battlefield if is_artifact_card(n)],
        "enchantment": [n for n in state.battlefield if is_enchantment_card(n)],
    }
    # CORRIGIDO 2026-09-25: fichas de Dragao sao criaturas -- "destroy all
    # creatures" tambem as leva (antes sobreviviam a todo wipe).
    available = [t for t in candidates if candidates[t] or (t == "creature" and state.dragon_token_list)]
    if not available:
        return None
    wipe_type = state.interaction_rng.choices(available, weights=[WIPE_TYPE_WEIGHTS[t] for t in available])[0]
    targets = candidates[wipe_type]
    if try_protection_response(state, "wipe", targets):
        state.wiped_this_round = state.wiped_this_round or wipe_type == "creature"
        return []
    hit_creature = any(is_creature_card(n) for n in targets)
    for n in targets:
        remove_permanent(state, n)
    if wipe_type == "creature" and state.dragon_token_list:
        clear_dragon_tokens(state)
        hit_creature = True
    if wipe_type == "creature":
        state.smart_wipes_total += 1
        state.smart_wipe_log.append((state.turn, targets))
    elif wipe_type == "artifact":
        state.smart_artifact_wipes_total += 1
        state.smart_artifact_wipe_log.append((state.turn, targets))
    else:
        state.smart_enchantment_wipes_total += 1
        state.smart_enchantment_wipe_log.append((state.turn, targets))
    if hit_creature:
        state.wiped_this_round = True
    return targets


def try_protection_response(state: GameState, kind: str, targets: list) -> bool:
    """CORRIGIDO 2026-09-28 (Regra #7, item 2): Heroic Intervention e
    Teferi's Protection estavam tageadas 'interaction' e fora do loop
    guloso (REACTIVE_NO_TARGET) E fora de `TRUE_INTERACTION_CARDS` -- nunca
    saiam da mao. Desde 2026-09-20 o modo de resiliencia tem wipe e remocao
    de oponente; agora elas respondem, com a mana que sobrou do meu turno
    (`remaining_mana`, o que ficou desvirado).
    - Heroic Intervention ({1}{G}): "Permanents you control gain hexproof
      and indestructible until end of turn." Todo wipe/remocao do modelo e'
      "destroy" -> nada morre.
    - Teferi's Protection ({2}{W}): "Until your next turn, your life total
      can't change and you gain protection from everything. All permanents
      you control phase out. Exile Teferi's Protection." -> salva e ainda
      anula ataques/remocao ate' o meu proximo turno.
    Politica (📝): wipe so' e' respondido se leva a comandante ou 3+
    permanentes; remocao pontual so' com Heroic (Teferi's fica pro wipe)."""
    if state.teferi_protected:
        state.protection_responses["teferi_ongoing"] = state.protection_responses.get("teferi_ongoing", 0) + 1
        return True
    if kind == "wipe" and not (COMMANDER in targets or len(targets) >= 3):
        return False
    options = ["Heroic Intervention"] + (["Teferi's Protection"] if kind == "wipe" else [])
    for card in options:
        if card in state.hand and remaining_mana(state) >= effective_cost(state, card) and has_color_sources_for(state, card):
            spend_mana(state, effective_cost(state, card))
            state.hand.remove(card)
            if card == "Teferi's Protection":
                state.teferi_protected = True  # "Exile Teferi's Protection": nao vai pro cemiterio
            else:
                state.graveyard.append(card)
            state.protection_responses[card] = state.protection_responses.get(card, 0) + 1
            return True
    return False


def try_smart_opponent_removal(state: GameState) -> Optional[str]:
    """Rola 1x por turno (a partir do turno 3) se o oponente "esperto"
    destroi a peca-motor de maior prioridade presente em campo -- mesma
    logica do Megatron, `INTERACTION_ENGINE_PRIORITY` curada pra esse
    deck."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    present = [n for n in INTERACTION_ENGINE_PRIORITY if n in state.battlefield]
    if not present:
        return None
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    # CORRIGIDO 2026-09-28: Lightning Greaves "Equipped creature has shroud"
    # -- o oponente esperto mira a proxima peca da lista.
    present = [n for n in present if n != state.lightning_greaves_equipped_to]
    if not present or try_protection_response(state, "removal", present[:1]):
        return None
    target = present[0]
    remove_permanent(state, target)
    state.smart_removals_total += 1
    state.smart_removal_log.append((state.turn, target))
    return target


OPPONENT_ATTACKER_PROFILES = [
    ("Knight Token", 2), ("Saproling Token", 1), ("Vampire Token", 1),
    ("Zombie Token", 2), ("Soldier Token", 1), ("Goblin Token", 1),
    ("Elemental Token", 3),
]
# Mesmos perfis do Megatron (validados por playtest real dele no
# Archidekt), so' sem toughness -- este arquivo nunca rastreou
# resistencia de criatura nenhuma (nem a minha, nem a de ninguem), entao
# nao ha' decisao de bloqueio possivel aqui (ver nota estrutural no topo
# da secao). Todo ataque conecta.


POST_WIPE_ATTACK_HASTE_FACTOR = 0.15
# Achado real do usuario 2026-09-20 (2a rodada da mesma correcao de
# orquestracao de turno, mesmo padrao do Megatron): board wipe e'
# SIMETRICO de verdade -- acerta TODA criatura em campo, nao so' a
# minha. Se um wipe ja' aconteceu NESTA RODADA (por qualquer um dos
# oponentes simulados), TODOS os outros oponentes tambem perderam as
# criaturas deles no mesmo golpe -- "se jogador A faz wipe, jogador C
# nao tem como atacar ate' voltar ao turno do jogador A, a nao ser no
# caso de haste" (citacao direta). Nao suprime o ataque por completo
# (Regra #1 do CLAUDE.md: so' impossibilidade estrutural e' motivo
# valido pra nao implementar, e um atacante com haste conjurado DEPOIS
# do wipe e' fisicamente possivel) -- reduz a chance pra so' esse
# cenario residual.


def try_smart_opponent_attack(state: GameState) -> Optional[str]:
    """Ataque de oponente -- SEM bloqueio (limitacao estrutural: este
    arquivo nunca rastreou toughness de criatura nenhuma, nem minha nem
    de ninguem, entao nao ha' dado pra decidir se um bloqueador mataria
    o atacante e sobreviveria). Sempre conecta em `state.life`.

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
    if state.teferi_protected:
        return None  # "your life total can't change and you gain protection from everything"
    if "Sarkhan Unbroken" in state.battlefield:
        # CORRIGIDO 2026-09-28: o oponente nunca atacava planeswalker neste
        # arquivo -- o Sarkhan Unbroken subia de lealdade sem risco. Mesma
        # convencao do Prismatic Bridge: o atacante vai no planeswalker primeiro.
        state.sarkhan_loyalty = getattr(state, "sarkhan_loyalty", 4) - power
        state.opp_attacks_on_pw_total += 1
        if state.sarkhan_loyalty <= 0:
            state.battlefield.remove("Sarkhan Unbroken")
            state.graveyard.append("Sarkhan Unbroken")
            state.sarkhan_killed_by_attack_total += 1
        state.smart_attacks_taken_total += 1
        state.smart_attack_log.append((state.turn, name))
        return name
    state.life -= power
    state.smart_attacks_taken_total += 1
    state.smart_attack_log.append((state.turn, name))
    return name


def try_smart_opponent_discard(state: GameState) -> Optional[str]:
    """Discard aleatorio -- mesma logica do Megatron (alvo puramente ao
    acaso na mao, sem filtro nenhum)."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if not state.hand:
        return None
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    target = state.interaction_rng.choice(state.hand)
    state.hand.remove(target)
    put_into_graveyard(state, target)
    state.smart_discards_total += 1
    state.smart_discard_log.append((state.turn, target))
    return target


def try_smart_opponent_counter(state: GameState) -> bool:
    """Counterspell -- so' mira a conjuracao do proprio Ur-Dragon (mesma
    logica do Megatron: o motor inteiro do deck depende do comandante
    resolver e atacar). Chamada de dentro de `cast_card()`, nao do loop
    de `simulate_one_with_interaction` -- so' faz sentido no exato
    momento do cast, dentro do MEU turno."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return False
    if state.interaction_rng.random() >= interaction_chance(state) * 0.5:
        return False
    # CORRIGIDO 2026-09-28 (Regra #7, item 2): estas clausulas estavam 📊
    # "sem contramagica de oponente modelada" desde 2026-08-29. Desde
    # 2026-09-20 o modo de resiliencia TEM essa contramagica, e nenhuma
    # delas tinha sido ligada. O sorteio acima fica antes das checagens pra
    # nao mudar a sequencia do `interaction_rng`.
    # - Dragonlord Dromoka: "Your opponents can't cast spells during your turn."
    # - Rhythm of the Wild: "Creature spells you control can't be countered."
    # - Cavern of Souls (Dragao): "...and that spell can't be countered" -- a
    #   Ur-Dragon precisa de WUBRG, a Cavern paga um dos pips.
    for prot in ("Dragonlord Dromoka", "Rhythm of the Wild", "Cavern of Souls"):
        if prot in state.battlefield:
            state.counters_prevented_total += 1
            state.counters_prevented_by[prot] = state.counters_prevented_by.get(prot, 0) + 1
            return False
    # Contramagica propria contra a contramagica deles: Swan Song ("Counter
    # target enchantment, instant, or sorcery spell"), Arcane Denial
    # ("Counter target spell"), An Offer You Can't Refuse ("Counter target
    # noncreature spell"). Mais barata primeiro; o bonus pro oponente (2/2,
    # 2 cartas, 2 Treasures) fica 📊 (board de oponente nao modelado).
    for answer in ("Swan Song", "Arcane Denial", "An Offer You Can't Refuse"):
        if answer in state.hand and can_cast(state, answer):
            cast_card(state, answer)
            state.counters_answered_total += 1
            return False
    state.smart_counters_total += 1
    state.smart_counter_log.append(state.turn)
    return True


GRAVEYARD_WIPE_CHANCE_FACTOR = 0.4
GRAVEYARD_SNIPE_CHANCE_FACTOR = 0.5


def try_smart_opponent_graveyard_wipe(state: GameState) -> Optional[list]:
    """Graveyard hate, modelo MASS EXILE (Bojuka Bog/Soul-Guide
    Lantern) -- carta fisica unica, dispara NO MAXIMO 1x por partida
    inteira (`state.graveyard_wipe_used`), nunca de novo depois disso."""
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
    Ooze/Cease) -- repetivel todo turno, sem flag de uso unico. Alvo
    SMART: maior MV entre Dragao-criatura no cemiterio -- MESMO
    criterio que `reanimate_dragons_from_graveyard()` ja usa pra
    escolher alvo de reanimacao (Haunting Voyage), nao MV entre
    criatura/artefato generico (isso e' recursao de Dragao, nao de
    artefato)."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    candidates = [c for c in state.graveyard if is_dragon_card(c) and is_creature_card(c)]
    if not candidates:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * GRAVEYARD_SNIPE_CHANCE_FACTOR:
        return None
    target = max(candidates, key=lambda n: CARD_DB[n].mv)
    state.graveyard.remove(target)
    state.smart_graveyard_snipes_total += 1
    state.smart_graveyard_snipe_log.append((state.turn, target))
    return target


OPPONENT_ATTENTION_CHANCE = 1.0 / NUM_OPPONENTS
# Achado real do usuario 2026-09-20 (3a rodada da mesma correcao de
# orquestracao, depois de eu medir que 79-88% das rodadas nos 3 decks
# tinham PELO MENOS 1 evento de interacao contra mim -- "se sempre for
# 3 contra 1, ai' nao consigo fazer nada, nunca", citacao direta).
# Antes disso, CADA um dos `NUM_OPPONENTS` turnos de oponente simulados
# por rodada tentava as 6 categorias sem excecao -- o modelo assumia
# que 100% da mesa mira em mim, todo turno de todo oponente, sempre.
# Gate NOVO e SEPARADO das 6 categorias, rolado 1x no INICIO de `try_
# smart_opponent_turn`: representa a chance de que ESTE oponente
# especifico esteja de olho em mim neste turno (ha' 3 alvos possiveis
# pra atencao dele -- eu e os outros 2 oponentes que este simulador nao
# modela), em vez de ocupado com o proprio board/outro oponente. Ver
# mesma constante/raciocinio no Megatron.


def try_smart_opponent_turn(state: GameState):
    """Simula O TURNO DE UM oponente dentro da rodada entre os meus
    turnos -- achado real do usuario 2026-09-20 (Regra #6 do CLAUDE.md):
    board wipe e' sorcery, conjurado na main phase de UM oponente
    especifico; ataque vem de criatura em campo DAQUELE MESMO oponente.
    Se o wipe for simetrico, as criaturas dele tambem morrem, entao ele
    nao ataca NESSE MESMO turno ("nao ha ataques normalmente nos turnos
    em que ha wipes", citacao direta do usuario). Wipe de um oponente
    ANTERIOR na rodada continua afetando corretamente o ataque de um
    oponente POSTERIOR na MESMA rodada (chamadas em sequencia, mesmo
    `state`). Ver `try_smart_opponent_turn` do Megatron, mesmo padrao.

    2a rodada da mesma correcao (achado real do usuario 2026-09-20,
    "se jogador A faz wipe, jogador C nao tem como atacar ate' voltar
    ao turno do jogador A, a nao ser no caso de haste"): um board wipe
    e' SIMETRICO -- acerta TODA criatura da mesa, nao so' as minhas.
    Entao nao e' so' o PROPRIO turno do oponente que fez o wipe que
    fica sem ataque -- TODOS os turnos de oponente restantes NESTA
    MESMA RODADA tambem ficam sem criaturas de verdade pra atacar. Por
    isso o gate manual daqui foi removido: `try_smart_opponent_attack`
    agora le' `state.wiped_this_round` (setado por `try_smart_opponent_
    wipe` e resetado 1x por rodada em `simulate_one_with_interaction`)
    e SOZINHO reduz a propria chance via `POST_WIPE_ATTACK_HASTE_
    FACTOR` -- cobre uniformemente tanto o turno do proprio wiper
    quanto qualquer oponente posterior na mesma rodada.

    3a rodada da mesma correcao (achado real do usuario 2026-09-20):
    antes de rolar QUALQUER categoria, este turno de oponente precisa
    passar no gate de `OPPONENT_ATTENTION_CHANCE` -- ver comentario da
    constante acima."""
    if state.turn > INTERACTION_SETUP_TURNS and state.interaction_rng.random() >= OPPONENT_ATTENTION_CHANCE:
        return
    try_smart_opponent_wipe(state)
    try_smart_opponent_attack(state)
    try_smart_opponent_graveyard_wipe(state)
    try_smart_opponent_graveyard_snipe(state)
    try_smart_opponent_removal(state)
    try_smart_opponent_discard(state)


def simulate_one_with_interaction(seed: int, turns: int = 8, swap=None):
    """Mesmo goldfish de `simulate_one`, mas com `NUM_OPPONENTS` turnos
    de oponente de verdade simulados (`try_smart_opponent_turn`) a cada
    rodada entre os meus turnos. Counterspell (7a categoria) NAO mora
    neste loop -- ver `try_smart_opponent_counter`, chamada de dentro
    de `cast_card`. NUNCA chamado por `run_batch`/`simulate_one`
    padrao.

    `state.wiped_this_round` e' resetado pra False aqui, no INICIO de
    cada rodada (antes do loop de `NUM_OPPONENTS`) -- mesmo padrao do
    Megatron: um wipe so' suprime ataque ate' a rodada em que aconteceu,
    nunca vaza pra rodada seguinte."""
    rng = random.Random(seed)
    hand, lib, mulls = mulligan(rng, library=library_with_swap(swap))
    state = GameState(hand=hand, library=lib, mulligans=mulls,
                       interaction_rng=random.Random(seed + 999_999), dice_rng=random.Random(seed + 424_242))
    for t in range(turns):
        state.teferi_protected = False  # "Until your next turn": acaba quando o meu turno comeca
        play_turn(state, is_first_turn=(t == 0), on_play=True)
        state.wiped_this_round = False
        for _ in range(NUM_OPPONENTS):
            try_smart_opponent_turn(state)
    return state


def run_batch_with_interaction(n: int, seed_base: int, turns: int = 8):
    """Batch do modo de resiliencia -- reporta so' as metricas
    relevantes pra "o motor aguenta perder a peca central?", nao
    duplica o relatorio inteiro do `run_batch` padrao."""
    states = [simulate_one_with_interaction(seed_base + i, turns=turns) for i in range(n)]

    def avg(vals):
        return sum(vals) / len(vals) if vals else 0.0

    print(f"n={n}, seed_base={seed_base}, turns={turns} (MODO RESILIENCIA -- wipe + graveyard hate + "
          f"remocao + ataque + discard aleatorio + counterspell de oponente)")
    print(f"Avg counterspells sofridos (so' mira a conjuracao da Ur-Dragon): "
          f"{avg([s.smart_counters_total for s in states]):.2f}")
    cmd_cast = [s.commander_cast_turn for s in states if s.commander_cast_turn is not None]
    print(f"  -- Turno medio de conjuracao QUE RESOLVEU: {avg(cmd_cast):.2f} | "
          f"nunca resolveu em {turns} turnos: {100*(n-len(cmd_cast))/n:.1f}%")
    print(f"Avg board wipes sofridos: {avg([s.smart_wipes_total for s in states]):.2f}")
    print(f"Avg artifact wipes sofridos: {avg([s.smart_artifact_wipes_total for s in states]):.2f}")
    print(f"Avg enchantment wipes sofridos: {avg([s.smart_enchantment_wipes_total for s in states]):.2f}")
    if sum(len(k) for s in states for _, k in s.smart_wipe_log):
        print(f"  -- Avg criaturas perdidas por wipe (quando dispara): "
              f"{avg([len(k) for s in states for _, k in s.smart_wipe_log]):.2f}")
    gy_wiped = sum(1 for s in states if s.smart_graveyard_wipes_total > 0)
    print(f"Partidas com graveyard wipe sofrido (no maximo 1x/partida): {100*gy_wiped/n:.1f}%")
    print(f"Avg graveyard snipes sofridos (sempre a maior MV Dragao): "
          f"{avg([s.smart_graveyard_snipes_total for s in states]):.2f}")
    print(f"Avg remocoes inteligentes sofridas: {avg([s.smart_removals_total for s in states]):.2f}")
    hit_counts = Counter()
    for s in states:
        for _, target in s.smart_removal_log:
            hit_counts[target] += 1
    for name in INTERACTION_ENGINE_PRIORITY:
        pct = 100 * hit_counts[name] / n
        if pct > 0:
            print(f"  -- {name} removido em {pct:.1f}% dos jogos")
    print(f"Avg ataques de oponente sofridos (sem bloqueio, ver nota estrutural): "
          f"{avg([s.smart_attacks_taken_total for s in states]):.2f}")
    print(f"Avg descartes forcados sofridos (alvo aleatorio na mao): "
          f"{avg([s.smart_discards_total for s in states]):.2f}")
    print(f"Avg dano/perda-de-vida proxy total (motor de ataque proprio): "
          f"{avg([s.proxy_damage_total for s in states]):.2f}")
    print(f"Avg cartas compradas extra: {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"Avg vida final (so' rastreada neste modo): {avg([s.life for s in states]):.2f}")
    return states


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


def library_with_swap(swap) -> list:
    """`swap` = (sai, entra) ou lista de pares: troca NA MESMA POSICAO da
    lista (pareamento de seed, `goldfish-sim-card-rules.md` "Teste
    comparativo pareado"). A `lista.md` real nao muda."""
    if swap is None:
        return BASE_LIBRARY
    pairs = [swap] if isinstance(swap[0], str) else list(swap)
    lib = BASE_LIBRARY[:]
    for out_card, in_card in pairs:
        assert out_card in lib, f"{out_card} nao esta' na lista"
        assert in_card in CARD_DB and in_card not in lib, in_card
        lib[lib.index(out_card)] = in_card
    return lib


# Correcao de 2026-10-05 (varredura das classes de erro das rodadas do Vihaan/Megatron nos outros decks): o London Mulligan deste arquivo SORTEAVA as cartas do fundo
# (`rng.shuffle(hand)`), devolvendo com a mesma chance uma carta-chave e um terreno sobrando. Com a chave em False o arquivo se comporta bit-a-bit como antes.
MULLIGAN_SMART_BOTTOM_ENABLED = True   # o jogador ESCOLHE as cartas do fundo (mesma regra do Vihaan/Megatron)
MULLIGAN_PROTECTED = frozenset({"Sol Ring", "Arcane Signet", "Birds of Paradise", "Delighted Halfling", "Farseek", "Nature's Lore", "Three Visits", COMMANDER})   # as cartas que `should_keep` ja' trata como "boa abertura": nao sao devolvidas se houver outra


def choose_bottom(hand: list, n: int) -> list:
    """London Mulligan: o jogador ESCOLHE as `n` cartas do fundo. So' desfaz de terreno quando sobram MAIS de 4 (e entao o que entra tapped primeiro, se o CARD_DB marcar);
    fora isso devolve a carta nao-terreno de MAIOR custo, protegendo `MULLIGAN_PROTECTED`."""
    hand = list(hand)
    bottom = []
    for _ in range(n):
        lands = [c for c in hand if c in LAND_NAMES]
        nonlands = [c for c in hand if c not in LAND_NAMES]
        if len(lands) > 4 or not nonlands:
            pick = min(lands, key=lambda c: (0 if "etb_tapped" in CARD_DB[c].tags else 1))
        else:
            pool = [c for c in nonlands if c not in MULLIGAN_PROTECTED] or nonlands
            pick = max(pool, key=lambda c: CARD_DB[c].mv)
        hand.remove(pick)
        bottom.append(pick)
    return bottom


def mulligan(rng: random.Random, max_mulls: int = 3, library=None):
    mulls = 0
    hand, lib = [], []
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
                if MULLIGAN_SMART_BOTTOM_ENABLED:
                    bottom = choose_bottom(hand, penalty)
                    for c in bottom:
                        hand.remove(c)
                else:
                    rng.shuffle(hand)
                    bottom = hand[:penalty]
                    hand = hand[penalty:]
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
    if state.decked_turn is not None:
        return  # perdeu por grimorio vazio (CR 704.5b)
    state.turn += 1
    state.lands_played_this_turn = 0
    state.mana_spent_this_turn = 0
    state.bonus_mana_pool = 0
    state.bonus_colored = []
    state.dragon_mana_pool = 0
    state.orb_dragonkind_used_this_turn = False
    state.first_creature_used_this_turn = False
    state.tapped_lands_this_turn = []  # os terrenos virados do turno passado desviram agora
    state.dragon_pump_bonus_this_turn = 0
    state.scourge_pump_this_turn = 0
    state.dragons_entered_this_turn = []

    if state.pending_upkeep_draws:
        # Arcane Denial: "You draw a card at the beginning of the next turn's
        # upkeep" -- esse upkeep ja' passou (turno do oponente seguinte).
        state.arcane_denial_draws_total += state.pending_upkeep_draws
        draw_cards(state, state.pending_upkeep_draws)
        state.pending_upkeep_draws = 0
    upkeep_step(state)
    # Achado real 2026-09-18: "skip the draw step" no 1o turno de quem
    # comeca so' existe na regra 1x1 (CR 103.8a). Commander e' sempre
    # multiplayer -- sempre compra, mesmo no T1.
    if state.library:
        state.hand.append(state.library.pop(0))
    else:
        state.library_emptied = True
        deck_out(state)
    if state.game_over:
        return
    if "Sylvan Library" in state.battlefield and not library_low(state):
        # Achado real 2026-08-27: tag 'card_selection' nunca tinha sido
        # implementada — Sylvan Library era 100% decorativa. Oraculo
        # real: compra 2 extras, escolhe 2 cartas compradas esse turno
        # pra devolver ao topo (cada uma custa 4 vida se ficar com
        # ela). Linha assumida: paga 4 vida por 1 extra e devolve a
        # outra (+1 carta liquida por turno). CORRIGIDO 2026-09-28: os 4 de
        # vida agora sao cobrados; 📝 com menos de 14 de vida devolve as 2.
        if state.life >= 14:
            draw_cards(state, 1)
            pay_life(state, 4, "sylvan_library")

    play_land(state)
    try_use_own_interaction(state)
    state.phase = "main1"
    main_phase(state)
    if state.decked_turn is not None:
        return
    state.phase = "combat"
    combat_step(state)
    if state.decked_turn is None:
        try_hellkite_charger_extra_combat(state)
    if state.decked_turn is not None:
        return
    state.phase = "main2"
    main_phase(state)
    if state.decked_turn is not None:
        return
    settle_mana_life(state)
    settle_treasures(state)
    end_step(state)
    if state.lethal_proxy_turn is None and state.proxy_damage_total + state.combat_damage_proxy_total >= LETHAL_PROXY:
        state.lethal_proxy_turn = state.turn


LETHAL_PROXY = 120  # 3 oponentes x 40 de vida -- premissa da metrica limitada, nao vida real


def simulate_one(seed: int, turns: int = 8, swap=None):
    rng = random.Random(seed)
    hand, lib, mulls = mulligan(rng, library=library_with_swap(swap))
    state = GameState(hand=hand, library=lib, mulligans=mulls, dice_rng=random.Random(seed + 424_242))
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
    print(f"Avg dano de comandante acumulado (CR 903.10a, so' a Ur-Dragon atacando): {avg([s.commander_damage_dealt for s in states]):.2f}")
    print(f"Partidas com vitoria por dano de comandante (21+): {100*sum(1 for s in states if s.commander_damage_win)/n:.1f}%")
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
