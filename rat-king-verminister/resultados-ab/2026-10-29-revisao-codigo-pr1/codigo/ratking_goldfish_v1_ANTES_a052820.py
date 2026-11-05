"""
Goldfish simulator — Rat King, Verminister (Mono-Black Rat tribal / aristocrats)

Construido do zero em 2026-08-31, a pedido direto do usuario ("faca a
analise e crie o simulador sem erros do Verminister"). Passo 0 (regra de
`references/goldfish-sim-card-rules.md`): oraculo real de TODAS as 53
cartas unicas da lista consultado via `scryfall-cache/oracle-cache.json`
(2 cartas que faltavam no cache -- Fell the Profane // Fell Mire e Priest
of Forgotten Gods -- foram buscadas na API real da Scryfall e adicionadas
ao cache antes de este arquivo ser escrito, Regra 14/15).

ATENCAO -- 2 correcoes reais de grafia aplicadas em `lista.md` nesta
sessao (conferidas via Scryfall, mesmo padrao do erro ja corrigido antes
nesta mesma lista pra Emeritus of Woe/Demonic Tutor):
- "Priest of the Forgotten Gods" -> "Priest of Forgotten Gods" (nome real
  nao tem "the").
- "Fell the Profane" -> "Fell the Profane // Fell Mire" (e' uma MDFC
  verdadeira, Instant // Land -- o nome sem o verso nao e' o nome real
  completo da carta).

Lista: 100/100 desde 2026-08-31 (o Damnation foi a 100a carta, ver
auditoria.md secao 14). `BASE_LIBRARY` tem 99 cartas, o comandante fica
de fora, e `build_library()` faz `assert len==99`. (Ate 2026-08-31 a lista
tinha 99/100, `BASE_LIBRARY` tinha 98 e o assert era 98; ver goldfish-log.md.)

Mecanica central do comandante: Rat King, Verminister -- {1}{B}, 1/1.
"Disappear -- At the beginning of your end step, if a permanent left the
battlefield under your control this turn, create a 1/1 black Rat
creature token and put a +1/+1 counter on Rat King." + "{T}, Sacrifice
three Rats: Return target creature card and all other cards with the
same name as that card from your graveyard to the battlefield tapped."
A segunda habilidade e' devastadora com Rat Colony (24 copias na lista) --
sacrificar 3 Rats pra trazer de volta 1 Rat Colony do cemiterio TAMBEM
traz QUALQUER outra copia de Rat Colony que esteja no cemiterio junto,
tudo de graca e tapped.

Tema do deck: Rat tribal + aristocrats (sacrificio por valor). Motores
centrais implementados de verdade (nao so tag):
- Rat Colony (24x, "+1/+0 pra cada outro Rat que voce controla") --
  escala com `rat_count()` (cartas nomeadas Rat + tokens de Rat).
- Skullclamp + geradores de token de Rat/Esquilo -- motor de draw
  repetivel: equipar um token 1/1, ele vira 2/0, morre por regra de
  estado, compra 2. Modelado como loop real (Equip {1} + sacrificio
  implicito via P/T negativo), nao proxy.
- Cabal Coffers + Urborg, Tomb of Yawgmoth + Crypt Ghast -- o combo
  classico de mono-preto. Urborg faz TODO terreno virar Swamp (inclusive
  o proprio Cabal Coffers, que passa a contar como fonte de "tap a Swamp"
  pro Crypt Ghast dobrar). Modelado com `swamp_count()` reutilizavel.
- Thrumming Stone ("Spells you cast have ripple 4") + Rat Colony (24
  copias) -- a peca mais explosiva do deck (auditoria.md, secao 8):
  toda vez que uma magica e' conjurada com Thrumming Stone em campo,
  revela 4 do topo e conjura de graca toda copia do MESMO NOME revelada.
  Real bombas de Rat Colony saindo de graca quando a densidade de copias
  no deck e' alta.
- Aristocrats/dreno: Zulaport Cutthroat, Ayara, Pitiless Plunderer,
  Priest of Forgotten Gods, Dictate of Erebos, Syr Konrad -- todos
  disparados por um unico ponto central `on_creature_dies()`/
  `leave_battlefield()`, pra nao duplicar nem perder gatilho.
- Devocao ao preto (Gray Merchant, Nykthos) -- soma real de pips {B}
  entre os permanentes em campo (`devotion_black()`), nao aproximacao.
- The Soul Stone (Harness) -- ativacao unica (paga {6}{B}, T, exila uma
  criatura) liga um motor de reanimacao repetivel real todo upkeep
  depois disso.
- Emeritus of Woe // Demonic Tutor -- layout real `prepare` (Scryfall).
  Fica "prepared" se 2+ criaturas suas morreram no turno (end step);
  enquanto prepared, pode conjurar uma COPIA do Demonic Tutor (paga o
  custo real {1}{B}, nao e' de graca) -- "unprepara" depois de usar.
- Ninja Teen (Classe, 3 niveis reais implementados -- nivel 3 permite
  conjurar criaturas do cemiterio via sneak, motor de recursao real).

Simplificacoes documentadas (nao inventadas -- omissoes explicitas):
- Sem oponente real: qualquer efeito que exija "opponent"/"target
  player" (drenos de vida contra oponente real, edicts do Dictate of
  Erebos, toxic/poison do Karumonix, extort do Crypt Ghast, Lord
  Skitter exilar cemiterio do oponente) fica "disponivel" com um contador de "quantas
  vezes disparou" mas sem efeito numerico de vida/poison do lado do
  oponente -- mesma convencao ja usada em todos os outros simuladores
  desta sessao. O GANHO de vida do proprio jogador (Zulaport, Ayara,
  Valley Rotcaller, Gray Merchant) e' real e rastreado.
- Wipes (Kindred Dominance, Swarmyard Massacre, Damnation): SUPERADO em 2026-10-28 (rodada 5, pedido do usuario "Opcao B nos wipes, e meca no A/B"). A convencao antiga (paga o custo,
  conta como interacao, nenhum efeito no proprio campo, com a justificativa "nenhum piloto racional conjuraria") era julgamento de valor, vedado pela Regra #1. Hoje o efeito e' aplicado
  no MEU campo, com mortes simultaneas (CR 603.10), e o wipe so' e' conjurado quando a perda propria (criaturas minhas que morrem) fica <= WIPE_CAST_MAX_OWN_LOSS (politica minha,
  com sensibilidade no A/B). A metade do OPONENTE (as criaturas dele) continua N/A estrutural: "Destroy all creatures that aren't of the chosen type" / "-1/-1 to each creature that
  isn't an Insect, Rat, Spider, or Squirrel" / "Destroy all creatures" so' tem alvo do oponente num jogo com oponente; a conjuracao continua contando como interacao (proxy).
- Fell the Profane // Fell Mire: MDFC modal (layout `modal_dfc`, Scryfall
  confirmado). SUPERADO em 2026-10-28 (rodada 4, pedido do usuario "Modela
  sim ambas as faces"): a decisao antiga ("so' a face Instant, porque remocao
  e' o gap real") era julgamento de valor, vedado pela Regra #1. Hoje as DUAS
  faces existem: o feitico {2}{B}{B} (conta como interacao, sem alvo de
  oponente: proxy) e o terreno Fell Mire ("As this land enters, you may pay 3
  life. If you don't, it enters tapped. {T}: Add {B}"), jogado por `play_land`
  quando nao ha outro terreno na mao (chaves FELL_MIRE_*; politica numerica
  declarada, com variante de sensibilidade no A/B).
- Toxic 1 (Karumonix) -- sem oponente real recebendo dano de combate,
  contadores de veneno nunca acontecem neste modelo (N/A estrutural, nao
  omissao).
- Thornbite Staff -- SUPERADO em 2026-10-25 (rodada 3): a conferencia antiga
  ("nenhuma criatura Shaman na lista", so' pelo `type_line` das cartas)
  esquecia a FICHA: o Mercenary do Black Market Connections tem changeling
  (todo tipo de criatura) e e' Shaman. Hoje o auto-attach, o Equip {4}, o ping
  e o combo com Marrow-Gnawer sao modelados (chave THORNBITE_STAFF_ENABLED).
- Combate: "ataca" = nao esta com summoning sickness. Nenhum bloqueio,
  nenhum dano de combate real contra oponente -- mesma convencao de
  todos os simuladores desta sessao. Metricas de dano/dreno sao proxy
  agregado (NUM_OPPONENTS nao modelado individualmente -- um unico total
  "vida perdida pelo oponente" acumulado, sem dividir por jogador).
"""

import collections
import copy
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
    ctype: str  # 'land','artifact','creature','enchantment','sorcery','instant'
    tags: frozenset = field(default_factory=frozenset)
    pips_b: int = 0       # pips {B} reais no custo de mana (devocao) -- so face da frente conta
    base_power: int = 0   # poder base impresso (Rat Colony escala a partir daqui)


CARD_DB: dict[str, Card] = {}


def add(name, mv, ctype, tags=(), pips_b=0, base_power=0):
    CARD_DB[name] = Card(name=name, mv=mv, ctype=ctype, tags=frozenset(tags),
                          pips_b=pips_b, base_power=base_power)


COMMANDER = "Rat King, Verminister"

# =====================================================================================================================================================
# RODADA 3 (2026-10-25) -- conceitos compartilhados (Rat/Squirrel/Shaman por changeling, "black creature", Treasure, "each opponent"), rulings e os 2 combos que o
# Commander Spellbook acha na lista (Marrow-Gnawer + Thornbite Staff; Ayara + Plague of Vermin). Achados e provas em resultados-ab/2026-10-25-rodada3-spellbook-rulings-e-correcoes/.
# Cada chave DESLIGADA devolve o comportamento anterior, bit a bit (provado em 20.000 x 2 modos).
# =====================================================================================================================================================
TREASURE_MANA_ENABLED = True          # Treasure ("{T}, Sacrifice: Add one mana of any color") nunca era gasta como mana; gastar tambem dispara o Disappear do Rat King
THORNBITE_STAFF_ENABLED = True        # Equip {4}, ping {2},{T}, untap quando uma criatura morre, auto-attach em Shaman (o Mercenary de changeling E' Shaman) e o combo com Marrow-Gnawer
ROTCALLER_EXACT_X = True              # X = outros Squirrels/Bats/Lizards/Rats que voce controla (sem o "-1" que tirava um Rat de verdade; sem filtro de "pronto"; conta os Esquilos)
MARROW_X_AFTER_SACRIFICE = True       # ruling 2004-12-01: X conta os Rats quando resolve, sem o Rat sacrificado
BIG_APPLE_PER_OPPONENT = True         # "a 1/1 Rat for EACH OPPONENT you have": NUM_OPPONENTS fichas, nao 1
AYARA_TOKEN_TRIGGER = True            # "Whenever Ayara or another black creature you control enters": ficha de Rat e' preta (o codigo estava morto: `... if False else None`)
AYARA_SACRIFICE_TOKENS = True         # "Sacrifice another black creature": ficha de Rat primeiro (antes sacrificava carta nomeada mesmo havendo ficha)
PLAGUE_PAYS_WITH_AYARA = True         # com Ayara em campo cada ficha devolve 1 de vida: paga tudo menos 1 (combo Ayara + Plague of Vermin do Spellbook)
JET_MEDALLION_BLACK_SPELLS = True     # "Black spells you cast cost {1} less": instant/sorcery preto tambem (o CARD_DB tem pips_b=0 nas magias)
COST_REDUCTION_COLORED_FLOOR = True   # rulings Jet Medallion/Bontu's: a reducao so' tira mana GENERICA; Rat Colony {1}{B} com os dois em campo custava 0
GRAY_MERCHANT_ETB = True              # "each opponent loses X life, X = devotion to black; you gain life equal to the life lost": o ETB nao existia (so' o Nykthos lia a devocao)
NINJA_TEEN_LEVELS_AND_DRAIN = True    # entra no nivel 1 SEM pagar (o codigo cobrava {1}{B} fantasma) + nivel 1: "creature you control leaves the battlefield: each opponent loses 1"
RAT_KING_REANIMATE_COST = True        # "Sacrifice three Rats": o comandante entrava na conta dos 3, mas nunca e' sacrificado: pagava 2
SOUL_STONE_SHARED_TAP = True          # Harness custa {6}{B} + {T} da propria pedra: a pedra nao pode tambem render o {B} do mesmo turno
PRIEST_EXACT = True                   # "Any number of target players": sem a perda de 2 de vida PROPRIA; "sacrifice two OTHER creatures": nunca o proprio Priest
EMERITUS_ENTERS_PREPARED = True       # "This creature enters prepared": pode conjurar a copia do Demonic Tutor logo que entra
EXTORT_ENABLED = True                 # Crypt Ghast: "Whenever you cast a spell, you may pay {W/B}": 1 mana -> cada oponente perde 1 e voce ganha o total perdido
ZULAPORT_SELF_DEATH = True            # "Whenever this creature OR another creature you control dies": a morte do proprio Zulaport tambem dispara
SACRIFICE_COST_NEEDS_FODDER = True    # Deadly Dispute / Culling the Weak so' sao conjuradas com algo pra sacrificar (antes pagavam o custo adicional "de graca")
BONTU_TRIGGER_ONCE = True             # "Whenever you cast a creature spell": disparava 2x por criatura conjurada da mao (cast_card E resolve_cast chamavam creature_cast_trigger)
NINJA_TEEN_SNEAK_RULING = True        # CR 702.190a + rulings 2026-01-27: sneak so' no declare blockers, devolve um atacante nao bloqueado a mao, o custo {3}{B} substitui o custo de mana, entra virada e atacando
MARROW_STAFF_LOOP_RAT_TARGET = 40    # combo infinito: para quando ha tantos Rats (o loop real e' infinito; o simulador precisa de um teto)
MARROW_STAFF_LOOP_MAX_ITERS = 12
PLAGUE_COMBO_CAP = 60                 # teto de fichas do Plague of Vermin paga com Ayara em campo

# =====================================================================================================================================================
# RODADA 4 (2026-10-28) -- pedidos do usuario: (a) "Modela sim ambas as faces" do Fell the Profane // Fell Mire; (b) Black Market Connections: "o modo mais importante e' o 1o,
# com custo 1 de vida; os demais so' entram em cena se eu tiver algum mecanismo de lifegain rodando: Ayara, ou outro qq". Cada chave DESLIGADA devolve o comportamento da
# rodada 3, bit a bit. As constantes numericas sao POLITICA MINHA (o usuario nao as definiu): ficam declaradas e com variante de sensibilidade no A/B.
# =====================================================================================================================================================
FELL_MIRE_LAND_ENABLED = True         # a face de terreno: "As this land enters, you may pay 3 life. If you don't, it enters tapped. {T}: Add {B}." Jogada como terreno quando nao ha outro terreno na mao
FELL_MIRE_COUNTS_FOR_KEEP = True      # o 1o `should_keep` conta a MDFC como terreno (ela e' jogavel como terreno): 3 terrenos, ou 2 + uma abertura boa
FELL_MIRE_MAX_LANDS_IN_PLAY = 6       # politica minha: so' vira terreno enquanto ha menos de 6 terrenos em campo (depois disso a face de feitico e' mais util)
FELL_MIRE_LIFE_FLOOR = 10             # politica minha: so' paga os 3 de vida se a vida depois de pagar fica >= 10 (e so' se o ensaio a seco mostrar que o terreno desvirado gasta mais mana neste turno)
TAPPED_FIRST_COUNTS_MANA = True       # ACHADO desta rodada: o ensaio do "terreno virado primeiro" (T1/T2) media so' o MV que sai da MAO e ignorava o comandante (zona de comando): empate 0 x 0 => jogava o terreno virado e perdia o comandante no T2. Agora mede o mana gasto
FELL_MIRE_GHOST = False               # so' validacao: roda o ensaio a seco mas ignora o resultado (nunca paga). Com a chave ligada + GHOST == FELL_MIRE_LIFE_FLOOR=99 (que nem roda o ensaio) prova que o ensaio nao tem efeito colateral
BMC_MODES_NEED_LIFEGAIN = True        # Black Market Connections: Sell Contraband (-1 vida) sempre; Buy Information (-2) e Hire a Mercenary (-3) so' com um mecanismo de lifegain em campo; politica minha: nunca escolhe um modo que leve a vida a 0 ou menos
LIFEGAIN_ENGINES = frozenset({        # permanentes com gatilho de ganho de vida REPETIVEL (oraculo ao vivo: "you gain ... life" em habilidade que nao e' so' de ETB). Gray Merchant (so' ETB) fica fora
    "Ayara, First of Locthwain", "Zulaport Cutthroat", "Bontu's Monument", "Crypt Ghast", "Valley Rotcaller"})

# =====================================================================================================================================================
# RODADA 5 (2026-10-28) -- pedido do usuario: "Opcao B nos wipes, e meca no A/B" (Kindred Dominance, Swarmyard Massacre, Damnation). Antes: pagos e contados como interacao, sem efeito
# no proprio campo (justificativa de valor, vedada pela Regra #1). Agora o efeito e' aplicado no MEU campo, simultaneamente (LKI, CR 603.10), e o wipe so' e' conjurado quando a perda
# propria (criaturas minhas que morrem, cartas e fichas) fica <= WIPE_CAST_MAX_OWN_LOSS. Cada chave DESLIGADA devolve o comportamento da rodada 4, bit a bit.
# =====================================================================================================================================================
WIPE_EFFECT_KINDRED = True            # Kindred Dominance: "Choose a creature type. Destroy all creatures that aren't of the chosen type." (escolho o tipo que poupa mais; o Mercenary de changeling sempre sobrevive)
WIPE_EFFECT_SWARMYARD = True          # Swarmyard Massacre: 2 Esquilos, "then each creature that isn't an Insect, Rat, Spider, or Squirrel gets -1/-1 ... for each creature you control that's an Insect, Rat, Spider, or Squirrel"
WIPE_EFFECT_DAMNATION = True          # Damnation: "Destroy all creatures." (o comandante inclusive: morre e volta a zona de comando, CR 903.9a)
WIPE_CAST_MAX_OWN_LOSS = 0            # POLITICA MINHA ("conjurando so' quando o resultado compensa"): so' conjura se no maximo N das minhas criaturas morrem; None = conjura sempre (comportamento antigo). So' vale p/ o wipe com efeito ligado
WIPE_GATE_NET_OF_NEW_TOKENS = True    # POLITICA MINHA: a perda que o limite compara e' LIQUIDA (mortes minhas menos os corpos que o proprio wipe cria: os 2 Esquilos do Swarmyard); False = so' as mortes (1a versao, mediu -0,114 Esquilos por partida)
WIPE_CARDS = frozenset({"Kindred Dominance", "Swarmyard Massacre", "Damnation"})
SWARMYARD_PROTECTED_TYPES = frozenset({"Insect", "Rat", "Spider", "Squirrel"})

# Pips {B} reais das MAGIAS (instant/sorcery): o `pips_b` do CARD_DB so' vale pra permanentes (devocao). Lidos do oraculo ao vivo (carddb_vs_oraculo.py).
BLACK_SPELL_PIPS = {
    "Deadly Dispute": 1, "Culling the Weak": 1, "Dark Ritual": 1, "Deadly Rollick": 1, "Withering Torment": 1, "Reanimate": 1, "Echoing Return": 1,
    "Secret Salvage": 2, "Kindred Dominance": 2, "Swarmyard Massacre": 2, "Plague of Vermin": 1, "Fell the Profane // Fell Mire": 2, "Damnation": 2,
}

add(COMMANDER, 2, "creature", {"commander", "rat", "disappear_engine"}, pips_b=1, base_power=1)

# --- Rats / corpo tribal -------------------------------------------------
add("Rat Colony", 2, "creature", {"rat", "rat_colony"}, pips_b=1, base_power=2)
# "ashcoat_pump" ("attacks or blocks: other Rats get +X/+X until EOT") e'
# 📊 N/A estrutural, nao esquecimento: este arquivo nao soma poder de
# ataque cru como dano proxy em NENHUM lugar (a lista inteira de gatilhos
# de "proxy_damage_total" e' so' os drenos reais -- Zulaport/Ayara/Bontu's
# Monument/Priest/Valley Rotcaller/Syr Konrad, ver docstring do
# `run_batch`), entao um pump temporario de combate nao tem onde
# manifestar numericamente aqui, mesma classe de N/A ja documentada pro
# toxic do Karumonix e o "steal" do Piper of the Swarm.
add("Ashcoat of the Shadow Swarm", 4, "creature", {"rat", "ashcoat_pump", "mill_return"}, pips_b=1, base_power=3)
add("Marrow-Gnawer", 5, "creature", {"rat", "fear_granter", "rat_army_sac"}, pips_b=2, base_power=2)
add("Lord Skitter, Sewer King", 3, "creature", {"rat", "rat_etb_exile", "combat_token"}, pips_b=1, base_power=3)
add("Karumonix, the Rat King", 3, "creature", {"rat", "toxic_granter", "etb_dig_rat"}, pips_b=2, base_power=3)
add("Piper of the Swarm", 2, "creature", {"menace_granter", "rat_token_activated", "steal"}, pips_b=1, base_power=1)
add("Ratcatcher", 6, "creature", {"fear", "upkeep_tutor_rat"}, pips_b=2, base_power=4)
add("Species Specialist", 4, "creature", {"choose_type_etb", "death_draw_type"}, pips_b=2, base_power=2)
add("Valley Rotcaller", 2, "creature", {"menace", "attack_drain_scaling"}, pips_b=1, base_power=1)
add("Gray Merchant of Asphodel", 5, "creature", {"devotion_drain"}, pips_b=2, base_power=2)
add("Syr Konrad, the Grim", 5, "creature", {"konrad_damage_engine", "mill_activated"}, pips_b=2, base_power=5)
add("Crypt Ghast", 4, "creature", {"extort", "swamp_double"}, pips_b=1, base_power=2)
add("Zulaport Cutthroat", 2, "creature", {"death_drain"}, pips_b=1, base_power=1)
add("Priest of Forgotten Gods", 2, "creature", {"sac2_drain_mana_draw"}, pips_b=1, base_power=1)
add("Ayara, First of Locthwain", 3, "creature", {"black_etb_drain", "sac_black_draw"}, pips_b=3, base_power=2)
# Emeritus of Woe // Demonic Tutor: layout real "prepare" (Scryfall). So a
# face da frente (Emeritus of Woe) e' permanente em campo -- devocao conta
# so' o custo dela ({3}{B} = 1 pip B), nunca soma o lado Demonic Tutor
# (que nunca fica em campo, e' um sorcery conjurado como copia).
add("Emeritus of Woe // Demonic Tutor", 4, "creature", {"prepare_tutor"}, pips_b=1, base_power=5)
add("Pitiless Plunderer", 4, "creature", {"death_treasure"}, pips_b=1, base_power=1)

# --- Artefatos -------------------------------------------------------------
add("Sol Ring", 1, "artifact", {"rock2"})
add("Skullclamp", 1, "artifact", {"equipment_clamp"})
add("Jet Medallion", 2, "artifact", {"black_cost_reduction"})
add("Bontu's Monument", 3, "artifact", {"black_creature_cost_reduction", "creature_cast_drain"})
# Thornbite Staff: equipamento; o auto-attach dispara no Mercenary de changeling (Shaman) do Black Market Connections (rodada 3, ver docstring).
add("Thornbite Staff", 2, "artifact", {"equipment_generic"})
add("Thrumming Stone", 5, "artifact", {"ripple4"})
add("The Soul Stone", 2, "artifact", {"soul_stone"}, pips_b=1)

# --- Encantamentos -----------------------------------------------------------
add("Black Market Connections", 3, "enchantment", {"modal_treasure_draw_mercenary"}, pips_b=1)
add("Cover of Darkness", 2, "enchantment", {"fear_granter_choose_type"}, pips_b=1)
add("Dictate of Erebos", 5, "enchantment", {"edict_on_death"}, pips_b=2)
add("Ripples of Undeath", 2, "enchantment", {"mill3_impulse"}, pips_b=1)
add("Ninja Teen", 3, "enchantment", {"ninja_teen_class"}, pips_b=1)

# --- Instantes ---------------------------------------------------------------
add("Deadly Dispute", 2, "instant", {"sac_draw2_treasure"})
add("Culling the Weak", 1, "instant", {"sac_ritual4"})
add("Dark Ritual", 1, "instant", {"ritual3"})
add("Deadly Rollick", 4, "instant", {"free_removal_commander", "interaction"})
add("Withering Torment", 3, "instant", {"removal_life_loss", "interaction"})
# Fell the Profane // Fell Mire: na mao/biblioteca/cemiterio vale so' a face da frente (Instant, MV 4; ruling 2024-06-07). Nome completo mantido no CARD_DB pra
# bater com o nome real usado em `lista.md`. A face de terreno ("Fell Mire") e' registrada logo abaixo, junto dos terrenos (rodada 4).
add("Fell the Profane // Fell Mire", 4, "instant", {"interaction"})

# --- Feiticarias ---------------------------------------------------------------
add("Reanimate", 1, "sorcery", {"reanimate"})
add("Echoing Return", 1, "sorcery", {"return_all_copies_hand"})
add("Secret Salvage", 5, "sorcery", {"tutor_all_copies_hand"})
add("Kindred Dominance", 7, "sorcery", {"wipe_asymmetric_type", "interaction"})
add("Swarmyard Massacre", 5, "sorcery", {"squirrel_tokens_wipe_asymmetric", "interaction"})
add("Damnation", 4, "sorcery", {"wipe_symmetric_no_target", "interaction"})
add("Plague of Vermin", 7, "sorcery", {"life_for_rats"})

# --- Terrenos (35: 11 nao-basicos + 24 Swamp) ---------------------------------
add("Cabal Coffers", 0, "land", {"coffers"})
add("Urborg, Tomb of Yawgmoth", 0, "land", {"urborg"})
add("Nykthos, Shrine to Nyx", 0, "land", {"nykthos"})
add("Castle Locthwain", 0, "land", {"castle_locthwain"})
add("Crypt of Agadeem", 0, "land", {"etb_tapped", "crypt_of_agadeem"})
add("Takenuma, Abandoned Mire", 0, "land", {"takenuma"})
add("Swarmyard", 0, "land", set())
add("Three Tree City", 0, "land", {"three_tree_city"})
add("Bojuka Bog", 0, "land", {"etb_tapped"})
add("Big Apple, 3 a.m.", 0, "land", {"etb_tapped", "big_apple"})
add("Swamp", 0, "land", {"swamp_type"})
# Face de terreno do Fell the Profane // Fell Mire (rodada 4). So' entra em campo por `play_land`; na mao/biblioteca/cemiterio a carta continua sendo
# "Fell the Profane // Fell Mire" (ruling 2024-06-07: fora da pilha e do campo vale so' a face da frente). Nunca esta na biblioteca (a lista nao a cita).
FELL_CARD = "Fell the Profane // Fell Mire"
add("Fell Mire", 0, "land", {"fell_mire"})

ARTIFACT_ISH = {"artifact"}
CREATURE_ISH = {"creature"}
LAND_NAMES = {n for n, c in CARD_DB.items() if c.ctype == "land"}
LEGENDARY_CREATURES = {
    # Verificado via Scryfall (type_line contendo "Legendary Creature") --
    # usado so pro custo reduzido do Channel de Takenuma, Abandoned Mire.
    COMMANDER, "Ashcoat of the Shadow Swarm", "Marrow-Gnawer",
    "Lord Skitter, Sewer King", "Karumonix, the Rat King",
    "Syr Konrad, the Grim", "Ayara, First of Locthwain",
}

# Tipos de criatura e tenacidade das criaturas da lista (type_line / toughness da face da frente, oraculo ao vivo arquivado em
# resultados-ab/2026-10-25-rodada3-spellbook-rulings-e-correcoes/dados/scryfall_oraculo_rulings_2026-10-25.json; o teste WP0 compara com o JSON). Fichas: Rat 1/1, Squirrel 1/1, Mercenary 3/2 changeling.
CREATURE_TYPES = {
    'Rat King, Verminister': ('Rat', 'Avatar'),
    'Rat Colony': ('Rat',),
    'Ashcoat of the Shadow Swarm': ('Rat', 'Warlock'),
    'Marrow-Gnawer': ('Rat', 'Rogue'),
    'Lord Skitter, Sewer King': ('Rat', 'Noble'),
    'Karumonix, the Rat King': ('Phyrexian', 'Rat'),
    'Piper of the Swarm': ('Human', 'Warlock'),
    'Ratcatcher': ('Ogre', 'Rogue'),
    'Species Specialist': ('Human', 'Warrior'),
    'Valley Rotcaller': ('Squirrel', 'Warlock'),
    'Gray Merchant of Asphodel': ('Zombie',),
    'Syr Konrad, the Grim': ('Human', 'Knight'),
    'Crypt Ghast': ('Spirit',),
    'Zulaport Cutthroat': ('Human', 'Rogue', 'Ally'),
    'Priest of Forgotten Gods': ('Human', 'Cleric'),
    'Ayara, First of Locthwain': ('Elf', 'Noble'),
    'Emeritus of Woe // Demonic Tutor': ('Vampire', 'Warlock'),
    'Pitiless Plunderer': ('Human', 'Pirate'),
}
CREATURE_TOUGHNESS = {
    'Rat King, Verminister': 1,
    'Rat Colony': 1,
    'Ashcoat of the Shadow Swarm': 4,
    'Marrow-Gnawer': 3,
    'Lord Skitter, Sewer King': 3,
    'Karumonix, the Rat King': 3,
    'Piper of the Swarm': 3,
    'Ratcatcher': 4,
    'Species Specialist': 3,
    'Valley Rotcaller': 3,
    'Gray Merchant of Asphodel': 4,
    'Syr Konrad, the Grim': 4,
    'Crypt Ghast': 2,
    'Zulaport Cutthroat': 1,
    'Priest of Forgotten Gods': 2,
    'Ayara, First of Locthwain': 3,
    'Emeritus of Woe // Demonic Tutor': 4,
    'Pitiless Plunderer': 4,
}


def is_creature_card(name: str) -> bool:
    return CARD_DB[name].ctype in CREATURE_ISH


def is_artifact_card(name: str) -> bool:
    return CARD_DB[name].ctype in ARTIFACT_ISH


def is_enchantment_card(name: str) -> bool:
    return CARD_DB[name].ctype == "enchantment"


def is_rat(name: str) -> bool:
    return "rat" in CARD_DB[name].tags


def is_black_creature(name: str) -> bool:
    # Toda criatura desta lista e' preta (mono-B) -- checado direto pelo ctype.
    return is_creature_card(name)


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
    lands_played_total: int = 0
    mana_spent_this_turn: int = 0
    tapped_lands_this_turn: set = field(default_factory=set)
    tapped_land_first_plays_total: int = 0   # correcao de 2026-10-05: vezes em que T1/T2 jogou o terreno virado primeiro
    tapped_land_skipped_for_play_total: int = 0   # ... e vezes em que o ensaio mostrou que isso custaria uma jogada e jogou o desvirado

    rat_tokens: int = 0
    squirrel_tokens: int = 0
    treasure_tokens: int = 0
    mercenary_tokens: int = 0  # token 3/2 changeling do Black Market Connections -- conta como Rat via changeling

    creature_cast_turn: dict = field(default_factory=dict)
    commander_in_play: bool = False
    commander_cast_count: int = 0
    commander_cast_turn: Optional[int] = None
    rat_king_counters: int = 0  # +1/+1 permanentes via Disappear

    permanent_left_battlefield_this_turn: bool = False  # gatilho Disappear
    creatures_died_this_turn: int = 0                   # gatilho Emeritus of Woe (prepared)
    emeritus_prepared: bool = False

    life: int = 40

    # cover of darkness / species specialist / three tree city -- tipo
    # escolhido sempre "Rat" (tema tribal central do deck, mesma
    # convencao ja documentada no goldfish-sim-card-rules.md pro Roaming
    # Throne noutros decks).
    ninja_teen_level: int = 0

    soul_stone_harnessed: bool = False

    # --- Rodada 3 (2026-10-25): campos novos (todos neutros com as chaves desligadas) ---
    treasures_spent_this_turn: int = 0     # Treasures gastas como mana neste turno (continuam contando em total_mana, pra remaining_mana nao pular)
    treasure_mana_used_total: int = 0
    staff_holder: Optional[str] = None     # None | nome da criatura-carta equipada | "__mercenary__" (ficha de changeling)
    staff_attach_turn: int = -1
    staff_tapped: bool = False             # so' pro holder-ficha; pro holder-carta vale tapped_creatures_this_turn
    staff_equips_total: int = 0
    staff_auto_attach_total: int = 0
    staff_pings_total: int = 0
    marrow_staff_loop_iters_total: int = 0
    combo_marrow_staff_turn: Optional[int] = None
    combo_ayara_plague_turn: Optional[int] = None
    combo_any_turn: Optional[int] = None
    soul_stone_tapped: bool = False
    extort_paid_total: int = 0
    gray_merchant_drain_total: int = 0
    ayara_token_triggers_total: int = 0
    ninja_teen_drain_total: int = 0
    rotcaller_x_total: int = 0
    big_apple_activations_total: int = 0
    rat_tokens_created_this_turn: int = 0      # fichas de Rat que entraram NESTE turno (doentes de invocacao: nao atacam, nao podem ser devolvidas pelo sneak)
    sneak_casts_total: int = 0

    # --- Rodada 4 (2026-10-28): campos novos (todos neutros com as chaves desligadas) ---
    fell_mire_land_plays_total: int = 0        # vezes em que a MDFC entrou como terreno
    fell_mire_paid_total: int = 0              # ... pagando 3 de vida (entra desvirada)
    fell_mire_tapped_total: int = 0            # ... sem pagar (entra virada)
    bmc_triggers_total: int = 0                # turnos em que o Black Market Connections disparou (so' conta com a chave nova ligada)
    bmc_mode1_total: int = 0                   # Sell Contraband: Treasure, -1 vida
    bmc_mode2_total: int = 0                   # Buy Information: compra 1, -2 vida
    bmc_mode3_total: int = 0                   # Hire a Mercenary: ficha 3/2 changeling, -3 vida
    bmc_modes_skipped_total: int = 0           # modos 2/3 nao escolhidos (sem lifegain em campo, ou vida insuficiente)

    # --- Rodada 5 (2026-10-28): wipes no proprio campo (todos neutros com as chaves desligadas) ---
    wipe_casts_total: int = 0                  # wipes conjurados (os 3), com ou sem efeito ligado
    wipe_kindred_total: int = 0
    wipe_swarmyard_total: int = 0
    wipe_damnation_total: int = 0
    wipe_own_creatures_lost_total: int = 0     # criaturas MINHAS (cartas + fichas) mortas por wipe meu
    wipe_held_total: int = 0                   # turnos-carta em que um wipe estava conjuravel mas o limite de perda propria o reteve
    wipes_held_this_turn: set = field(default_factory=set)

    piper_used_this_turn: bool = False
    # Achado real 2026-09-13: main_phase() roda 2x por turno (pre- e
    # pos-combate), entao qualquer habilidade "{T}: ..." sem essa guarda
    # ativava 2x por turno. Rastreia quais criaturas com custo {T} ja
    # foram ativadas neste turno (Marrow-Gnawer, Ayara, Priest of
    # Forgotten Gods, Rat King reanimate).
    tapped_creatures_this_turn: set = field(default_factory=set)
    warmaster_placeholder: bool = False  # nao usado, mantido por simetria de outros arquivos

    # metrics -------------------------------------------------------------
    ramp_pieces_cast_total: int = 0
    cards_drawn_extra: int = 0
    interaction_spells_cast_total: int = 0
    recursion_events_total: int = 0
    tutors_used_total: int = 0
    tokens_created_total: int = 0
    proxy_damage_total: int = 0        # dreno/dano agregado contra oponente (proxy, sem vida real de oponente)
    skullclamp_draws_total: int = 0
    thrumming_stone_free_casts_total: int = 0
    rat_king_reanimations_total: int = 0
    library_emptied: bool = False

    # --- Modo de resiliencia (interacao de oponente), 2026-09-21 -------------
    # Porte do mesmo protocolo ja validado em Megatron/Ur-Dragon/Hei Bai/
    # Edgar Markov/Ulalek/Toph/Prismatic Bridge/Maralen. `interaction_rng`
    # fica `None` em modo padrao (`simulate_one`/`run_batch`) -- toda funcao
    # `try_smart_opponent_*` abaixo checa isso primeiro e retorna sem
    # efeito, garantindo que o modo padrao continua bit-identico.
    interaction_rng: Optional[random.Random] = None
    wiped_this_round: bool = False
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
    graveyard_wipe_used: bool = False
    smart_graveyard_snipes_total: int = 0
    smart_graveyard_snipe_log: list = field(default_factory=list)


def draw_cards(state: GameState, n: int):
    for _ in range(n):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1
        else:
            state.library_emptied = True


def rat_count(state: GameState) -> int:
    named = sum(1 for n in state.battlefield if is_rat(n))
    # Mercenary token (changeling) conta como Rat -- "It is every creature type."
    return named + state.rat_tokens + state.mercenary_tokens


def creature_count(state: GameState) -> int:
    named = sum(1 for n in state.battlefield if is_creature_card(n))
    return named + state.rat_tokens + state.squirrel_tokens + state.mercenary_tokens


def rat_colony_power(state: GameState) -> int:
    """Rat Colony: base 2/1, '+1/+0 pra cada OUTRO Rat que voce controla'."""
    others = rat_count(state) - 1  # exclui a propria copia sendo calculada
    return 2 + max(0, others)


# ---------------------------------------------------------------------------
# Devocao ao preto (Gray Merchant, Nykthos)
# ---------------------------------------------------------------------------

def devotion_black(state: GameState) -> int:
    return sum(CARD_DB[n].pips_b for n in state.battlefield)


# ---------------------------------------------------------------------------
# Terrenos / mana
# ---------------------------------------------------------------------------

def urborg_in_play(state: GameState) -> bool:
    return "Urborg, Tomb of Yawgmoth" in state.battlefield


def swamp_count(state: GameState) -> int:
    """Urborg faz TODO terreno virar Swamp -- inclusive o proprio Cabal
    Coffers (que passa a contar como fonte de 'tap a Swamp' pro Crypt
    Ghast dobrar). Sem Urborg, so os Swamp basicos reais contam (nenhum
    outro terreno da lista tem o subtipo Swamp)."""
    if urborg_in_play(state):
        return sum(1 for n in state.battlefield if n in LAND_NAMES)
    return sum(1 for n in state.battlefield if n == "Swamp")


def black_creatures_in_graveyard(state: GameState) -> int:
    return sum(1 for n in state.graveyard if is_creature_card(n))


def rocks_mana(state: GameState) -> int:
    total = 0
    if "Sol Ring" in state.battlefield:
        total += 2
    if "The Soul Stone" in state.battlefield and not (SOUL_STONE_SHARED_TAP and state.soul_stone_tapped):
        total += 1
    return total


def lands_mana(state: GameState) -> int:
    """Mana bruta de TODO terreno em campo (1 por terreno destapado) +
    Crypt Ghast dobrando cada 'tap de Swamp' (incluindo, sob Urborg, o
    proprio Cabal Coffers) + Cabal Coffers propriamente dito."""
    lands_in_play = [n for n in state.battlefield if n in LAND_NAMES]
    untapped_lands = [n for n in lands_in_play if n not in state.tapped_lands_this_turn]
    total = len(untapped_lands)

    ghast = "Crypt Ghast" in state.battlefield
    swamps = swamp_count(state)

    if ghast:
        # cada Swamp destapado (ou, sob Urborg, cada terreno destapado)
        # que tapa pra mana normal soma +1 B extra via Crypt Ghast.
        untapped_swamp_taps = swamps - len([n for n in state.tapped_lands_this_turn if n in LAND_NAMES])
        total += max(0, min(untapped_swamp_taps, len(untapped_lands)))

    if "Cabal Coffers" in state.battlefield and "Cabal Coffers" not in state.tapped_lands_this_turn:
        # {2}, T: Add B pra cada Swamp -- ativa quando ha mana sobrando
        # pro custo de {2} (mesma convencao "sempre ativa se compensa" ja
        # usada noutros simuladores desta sessao pra Nykthos/Crypt of
        # Agadeem). Coffers em si NAO conta a propria mana bruta (ela ja
        # foi contada em `untapped_lands` acima como land generica) --
        # aqui so somamos o BONUS de "por Swamp".
        total += max(0, swamps - 2)  # -2 aproxima o custo de ativacao pago do proprio pool
        if ghast and urborg_in_play(state):
            # sob Urborg, Cabal Coffers e' ela mesma um Swamp -- tapa-la
            # pra ativar a propria habilidade TAMBEM dispara Crypt Ghast.
            total += 1

    if "Crypt of Agadeem" in state.battlefield and "Crypt of Agadeem" not in state.tapped_lands_this_turn:
        total += max(0, black_creatures_in_graveyard(state) - 2)  # -2 aproxima custo {2}

    if "Nykthos, Shrine to Nyx" in state.battlefield and "Nykthos, Shrine to Nyx" not in state.tapped_lands_this_turn:
        total += max(0, devotion_black(state) - 2)  # -2 aproxima custo {2}

    if "Three Tree City" in state.battlefield and "Three Tree City" not in state.tapped_lands_this_turn:
        total += max(0, rat_count(state) - 2)  # tipo escolhido = Rat, -2 aproxima custo {2}

    return total


def colored_pips(name: str) -> int:
    """Mana COLORIDA do custo (a lista e' mono-preta: so' {B}). Permanentes: pips_b do CARD_DB; magias: BLACK_SPELL_PIPS."""
    c = CARD_DB[name]
    if c.ctype in ("instant", "sorcery"):
        return BLACK_SPELL_PIPS.get(name, 0)
    return c.pips_b


def cost_reduction(state: GameState, name: str) -> int:
    d = 0
    if JET_MEDALLION_BLACK_SPELLS and "Jet Medallion" in state.battlefield and CARD_DB[name].ctype in ("instant", "sorcery"):
        if BLACK_SPELL_PIPS.get(name, 0) > 0:
            d += 1
    elif "Jet Medallion" in state.battlefield and CARD_DB[name].ctype not in ("land",):
        # "Black spells you cast" -- toda carta desta lista e' preta
        # (mono-B), exceto artefatos incolores (Sol Ring/Skullclamp/Jet
        # Medallion/Thornbite Staff/Thrumming Stone/Soul Stone nao tem
        # pip colorido -- oraculo real deles nao e' preto).
        if CARD_DB[name].pips_b > 0 or is_creature_card(name):
            d += 1
    if "Bontu's Monument" in state.battlefield and is_creature_card(name):
        d += 1
    return d


def total_mana(state: GameState) -> int:
    t = lands_mana(state) + rocks_mana(state)
    if TREASURE_MANA_ENABLED:
        t += state.treasure_tokens + state.treasures_spent_this_turn
    return t


def remaining_mana(state: GameState) -> int:
    return max(0, total_mana(state) - state.mana_spent_this_turn)


def effective_cost(state: GameState, name: str) -> int:
    if name == "Deadly Rollick" and state.commander_in_play:
        # Achado real 2026-09-01 (leitura linha-a-linha, "compile TUDO"):
        # oraculo real "If you control a commander, you may cast this
        # spell without paying its mana cost. Exile target creature." --
        # tag "free_removal_commander" nunca lida em lugar nenhum, a
        # magica sempre pagava o custo cheio {3}{B} antes. Confirmado via
        # Scryfall que o texto NAO exige alvo atacando/bloqueando (so
        # "target creature").
        return 0
    if COST_REDUCTION_COLORED_FLOOR:
        return max(colored_pips(name), CARD_DB[name].mv - cost_reduction(state, name))
    return max(0, CARD_DB[name].mv - cost_reduction(state, name))


def can_cast(state: GameState, name: str) -> bool:
    return remaining_mana(state) >= effective_cost(state, name)


def _consume_treasures(state: GameState):
    """Treasure: '{T}, Sacrifice this artifact: Add one mana of any color'. A mana dos terrenos/pedras gasta primeiro; o que passar disso sai das Treasures (que SAEM do campo:
    o Disappear do Rat King dispara). `treasures_spent_this_turn` continua em total_mana, entao remaining_mana nao muda ao consumir."""
    base = lands_mana(state) + rocks_mana(state)
    novas = (state.mana_spent_this_turn - base) - state.treasures_spent_this_turn
    if novas > 0:
        novas = min(novas, state.treasure_tokens)
        if novas > 0:
            state.treasure_tokens -= novas
            state.treasures_spent_this_turn += novas
            state.treasure_mana_used_total += novas
            state.permanent_left_battlefield_this_turn = True


def spend_mana(state: GameState, n: int):
    state.mana_spent_this_turn += n
    if TREASURE_MANA_ENABLED:
        _consume_treasures(state)


# ---------------------------------------------------------------------------
# Sacrificio / morte -- ponto central de despacho (aristocrats)
# ---------------------------------------------------------------------------

def on_creature_dies(state: GameState, n: int = 1, is_token: bool = False, dying_is_rat: bool = True):
    """Disparado toda vez que N criaturas suas morrem (vao pro cemiterio
    a partir do campo). Despacha TODOS os gatilhos de morte reais da
    lista a partir de um unico ponto, pra nao duplicar nem esquecer."""
    if n <= 0:
        return
    state.creatures_died_this_turn += n
    if NINJA_TEEN_LEVELS_AND_DRAIN and "Ninja Teen" in state.battlefield:
        # nivel 1: "Whenever a creature you control leaves the battlefield, each opponent loses 1 life."
        state.proxy_damage_total += n
        state.ninja_teen_drain_total += n
    if THORNBITE_STAFF_ENABLED:
        staff_untap_on_death(state)
    if "Zulaport Cutthroat" in state.battlefield:
        state.life += n
        state.proxy_damage_total += n
    if "Pitiless Plunderer" in state.battlefield:
        state.treasure_tokens += n
    if "Syr Konrad, the Grim" in state.battlefield:
        # "Whenever another creature dies..." -- Syr Konrad tambem
        # dispara quando ELE MESMO morre (o oraculo diz "another
        # creature", mas o proprio dano dele so conta as OUTRAS -- como
        # ele e' quem dispara, isso e' automaticamente respeitado aqui
        # por ele estar em `state.battlefield` no momento da checagem).
        state.proxy_damage_total += n
    if "Dictate of Erebos" in state.battlefield:
        # Edict no oponente -- sem oponente real, so conta o gatilho.
        pass
    if "Species Specialist" in state.battlefield and dying_is_rat:
        # Achado real 2026-09-01 (leitura linha-a-linha, "compile TUDO"):
        # "Whenever a creature of the chosen type dies, you may draw a
        # card" -- tag "death_draw_type" nunca lida em lugar nenhum, so
        # o ETB de escolha de tipo (Rat, tema tribal central) estava
        # documentado. Como a esmagadora maioria das mortes deste deck
        # E' de Rats (24x Rat Colony + tokens de Rat), isso dispara com
        # frequencia real.
        draw_cards(state, n)


def konrad_gy_entered(state: GameState, card_name: str):
    """Syr Konrad, the Grim, clausula 2 de 3: '...or a creature card is put
    into a graveyard from anywhere OTHER THAN THE BATTLEFIELD, Syr Konrad
    deals 1 damage to each opponent.' Achado real (auditoria oraculo-por-
    oraculo): so' a clausula 1 (criatura morre, `on_creature_dies`) estava
    implementada -- esta e a clausula 3 (`konrad_gy_left`) nunca
    disparavam em lugar nenhum, apesar do deck ter mill pesado (Ashcoat,
    Ripples of Undeath, Takenuma) e recursao pesada (Reanimate, Echoing
    Return, Secret Salvage, Rat King, Ninja Teen, Soul Stone). So' chamar
    em cartas indo pra cemiterio via MILL/DESCARTE (biblioteca/mao -> GY),
    nunca em mortes de campo (isso e' a clausula 1, ja coberta)."""
    if "Syr Konrad, the Grim" in state.battlefield and is_creature_card(card_name):
        state.proxy_damage_total += 1


def konrad_gy_left(state: GameState, n: int = 1):
    """Syr Konrad, the Grim, clausula 3 de 3: '...or a creature card
    leaves your graveyard, Syr Konrad deals 1 damage to each opponent.'
    Chamado de todo ponto que remove carta(s) de criatura do cemiterio pra
    qualquer OUTRA zona (mao, campo, exilio)."""
    if n > 0 and "Syr Konrad, the Grim" in state.battlefield:
        state.proxy_damage_total += n


def leave_battlefield(state: GameState, name: str, to_graveyard: bool = True, is_token: bool = False):
    """Achado real (porte do modo de resiliencia, 2026-09-21): a versao
    anterior desta funcao so' mandava a carta pro cemiterio quando
    `is_creature_card(name)` era verdade -- os 3 call sites
    pre-existentes (`sacrifice_rats`/`sacrifice_any_creature`/
    `ayara_activation`) sempre passam criatura de verdade, entao esse
    gap nunca era exercitado. `remove_permanent()` do modo de
    resiliencia agora pode chamar isso com artefato/encantamento (wipe
    de qualquer um dos 3 tipos) -- corrigido pra sempre mandar carta
    NAO-token pro cemiterio quando `to_graveyard=True`, independente do
    tipo. O gatilho de morte (`on_creature_dies`) continua exclusivo de
    criatura, igual antes.

    CORRIGIDO 2026-09-21 (achado real do usuario, CR 903.9a -- ver
    `rules-cache/comprehensive-rules.txt` linhas 6888-6896, Regra 18 de
    `references/user-standing-rules.md`; mesma correcao do Toph/Maralen
    nesta sessao -- Regra #6 do CLAUDE.md, o tratamento do comandante
    tem que morar no CHOKEPOINT central, nao no caller): tratamento do
    comandante movido pra AQUI. Ela agora dispara `on_creature_dies`
    normalmente (Zulaport/Pitiless Plunderer/Syr Konrad/Species
    Specialist -- nenhum dos 4 e' ela mesma, e ela E' Rato de verdade,
    tag "rat" no CARD_DB) igual qualquer criatura, ja' que 903.9a e'
    ACAO BASEADA EM ESTADO (CR 704), nao substituicao -- ela vai pro
    cemiterio DE VERDADE primeiro (CR 700.4, "dies"), so' DEPOIS e'
    removida de la' pra representar a escolha do dono de move-la pra
    zona de comando (`commander_in_play=False`). Nenhum call site real
    hoje atinge o comandante por aqui (`sacrifice_rats`/`sacrifice_any_
    creature`/`ayara_activation`/`try_harness_soul_stone` excluem ela
    de proposito -- jogador racional nunca sacrifica o proprio
    comandante por fodder mais barato; `try_smart_opponent_removal`
    tambem a exclui de `INTERACTION_ENGINE_PRIORITY`; wipe de criatura
    usa `_wipe_remove_creature_no_trigger`, corrigido separadamente),
    mas corrigido por consistencia estrutural -- uma futura mudanca
    numa dessas exclusoes deliberadas nao herdaria o bug em silencio."""
    if not is_token and name in state.battlefield:
        state.battlefield.remove(name)
    state.permanent_left_battlefield_this_turn = True
    if to_graveyard and not is_token:
        state.graveyard.append(name)
    if is_creature_card(name) and to_graveyard:
        on_creature_dies(state, 1, is_token=is_token, dying_is_rat=is_rat(name))
        if ZULAPORT_SELF_DEATH and name == "Zulaport Cutthroat":
            state.life += 1                      # a morte do proprio Zulaport: ja saiu do campo antes do despacho acima
            state.proxy_damage_total += 1
    if name == COMMANDER:
        if name in state.graveyard:
            state.graveyard.remove(name)
        state.commander_in_play = False


def remove_permanent(state: GameState, name: str, source: str = "opponent"):
    """Ponto central de remocao de permanente do CAMPO por acao de
    OPONENTE (wipe/remocao do modo de resiliencia, 2026-09-21 -- porte
    do Megatron/Ur-Dragon/Hei Bai/Edgar Markov/Ulalek/Toph/Prismatic
    Bridge/Maralen). Reaproveita `leave_battlefield()` ja' existente
    (mesmos gatilhos reais de aristocrata -- Zulaport/Pitiless
    Plunderer/Syr Konrad/Species Specialist -- que uma morte por
    qualquer causa dispara, INCLUINDO o comandante agora -- CR 903.9a,
    ver docstring de `leave_battlefield`)."""
    if name not in state.battlefield:
        return
    leave_battlefield(state, name, to_graveyard=True)


def sacrifice_rats(state: GameState, n: int) -> int:
    """Sacrifica ate N Rats reais (token primeiro, depois carta nomeada
    mais barata -- menor perda de valor). Retorna quantos foram
    sacrificados de fato."""
    done = 0
    while done < n and rat_count(state) > 0:
        if state.rat_tokens > 0:
            state.rat_tokens -= 1
            state.permanent_left_battlefield_this_turn = True
            on_creature_dies(state, 1, is_token=True)
            done += 1
            continue
        if state.mercenary_tokens > 0:
            state.mercenary_tokens -= 1
            state.permanent_left_battlefield_this_turn = True
            on_creature_dies(state, 1, is_token=True)
            done += 1
            continue
        named_rats = [x for x in state.battlefield if is_rat(x) and x != COMMANDER]
        if not named_rats:
            break
        cheapest = min(named_rats, key=lambda x: CARD_DB[x].mv)
        leave_battlefield(state, cheapest, to_graveyard=True)
        done += 1
    return done


def sacrifice_any_creature(state: GameState, n: int, exclude: Optional[str] = None) -> int:
    """Sacrifica ate N criaturas (token generico primeiro, depois carta
    nomeada mais barata) -- usado por Deadly Dispute/Culling the
    Weak/Priest of Forgotten Gods."""
    done = 0
    while done < n:
        if state.rat_tokens > 0:
            state.rat_tokens -= 1
            state.permanent_left_battlefield_this_turn = True
            on_creature_dies(state, 1, is_token=True)
            done += 1
            continue
        if state.squirrel_tokens > 0:
            state.squirrel_tokens -= 1
            state.permanent_left_battlefield_this_turn = True
            on_creature_dies(state, 1, is_token=True, dying_is_rat=False)
            done += 1
            continue
        if state.mercenary_tokens > 0:
            state.mercenary_tokens -= 1
            state.permanent_left_battlefield_this_turn = True
            on_creature_dies(state, 1, is_token=True)
            done += 1
            continue
        creatures = [x for x in state.battlefield if is_creature_card(x) and x != COMMANDER and x != exclude]
        if not creatures:
            break
        cheapest = min(creatures, key=lambda x: CARD_DB[x].mv)
        leave_battlefield(state, cheapest, to_graveyard=True)
        done += 1
    return done


# ---------------------------------------------------------------------------
# ETB / cast
# ---------------------------------------------------------------------------

def best_missing_creature(state: GameState, pool: list) -> str:
    priority = [
        "Marrow-Gnawer", "Skullclamp", "Karumonix, the Rat King", "Ratcatcher",
        "Syr Konrad, the Grim", "Gray Merchant of Asphodel", "Ayara, First of Locthwain",
        COMMANDER,
    ]
    for p in priority:
        if p in pool:
            return p
    return max(pool, key=lambda n: CARD_DB[n].mv)


def resolve_etb(state: GameState, name: str):
    tags = CARD_DB[name].tags

    if "black_etb_drain" in tags:
        # Ayara -- "Whenever Ayara OR ANOTHER black creature you control
        # enters" -- disparado pelo proprio ETB dela tambem (checado no
        # caller via `black_etb_trigger`).
        pass

    if "rat_etb_exile" in tags:
        pass  # Lord Skitter: exila do cemiterio do OPONENTE -- sem efeito numerico real (Regra 1)

    if "etb_dig_rat" in tags:
        # Karumonix: olha as 5 do topo, revela Rats, poe na mao; resto no fundo em ordem aleatoria.
        top5 = state.library[:5]
        del state.library[:5]
        rats_found = [c for c in top5 if is_rat(c)]
        for r in rats_found:
            top5.remove(r)
            state.hand.append(r)
        state.library.extend(top5)
        state.tutors_used_total += len(rats_found)

    if "choose_type_etb" in tags:
        pass  # Species Specialist: tipo escolhido = Rat (documentado, tema tribal central)

    if GRAY_MERCHANT_ETB and "devotion_drain" in tags:
        # Gray Merchant: "each opponent loses X life, where X is your devotion to black. You gain life equal to the life lost this way." (ruling 2021-03-19: o TOTAL perdido)
        x = devotion_black(state)
        state.proxy_damage_total += x
        state.life += x * NUM_OPPONENTS
        state.gray_merchant_drain_total += x


def black_etb_trigger(state: GameState, entering_name: str):
    if "Ayara, First of Locthwain" not in state.battlefield:
        return
    if not is_black_creature(entering_name):
        return
    state.life += 1
    state.proxy_damage_total += 1


def creature_cast_trigger(state: GameState, name: str):
    """Bontu's Monument: 'Whenever you cast a creature spell, each
    opponent loses 1 life and you gain 1 life.'"""
    if "Bontu's Monument" in state.battlefield:
        state.life += 1
        state.proxy_damage_total += 1


def create_rat_token(state: GameState, source: str = ""):
    state.rat_tokens += 1
    state.rat_tokens_created_this_turn += 1
    state.tokens_created_total += 1
    black_etb_trigger(state, "__rat_token__") if False else None  # (devocao nao conta tokens: so' mana COSTS de permanentes contam. Isso NAO vale pra Ayara: ver abaixo)
    if AYARA_TOKEN_TRIGGER and "Ayara, First of Locthwain" in state.battlefield:
        # a ficha de Rat e' uma criatura PRETA: Ayara dispara (o Squirrel e' verde e o Mercenary e' incolor: nao disparam)
        state.life += 1
        state.proxy_damage_total += 1
        state.ayara_token_triggers_total += 1


def note_combo(state: GameState, campo: str):
    if getattr(state, campo) is None:
        setattr(state, campo, state.turn)
    if state.combo_any_turn is None:
        state.combo_any_turn = state.turn


def create_squirrel_tokens(state: GameState, n: int, source: str = ""):
    state.squirrel_tokens += n
    state.tokens_created_total += n


def _types_of(name: str) -> tuple:
    return CREATURE_TYPES.get(name, ())


def _wipe_effect_on(name: str) -> bool:
    return {"Kindred Dominance": WIPE_EFFECT_KINDRED, "Swarmyard Massacre": WIPE_EFFECT_SWARMYARD, "Damnation": WIPE_EFFECT_DAMNATION}.get(name, False)


def wipe_plan(state: GameState, name: str) -> dict:
    """Quem das MINHAS criaturas morre se `name` resolver agora (nao muta o estado). Devolve `named` (cartas em campo que morrem), `rat`/`sq`/`mc` (fichas de Rat, Esquilo e Mercenary que morrem),
    `loss` (total que morre), `new_squirrels` (Esquilos que o Swarmyard cria ANTES do -1/-1) e `type` (tipo escolhido pelo Kindred Dominance).
    - Damnation: "Destroy all creatures": tudo morre (o comandante tambem).
    - Kindred Dominance: "Choose a creature type. Destroy all creatures that aren't of the chosen type." Escolho o tipo que menos mata (empate: menos MV perdido, depois Rat, depois ordem alfabetica);
      o Mercenary (changeling = todo tipo) nunca morre.
    - Swarmyard Massacre: cria 2 Esquilos, depois cada criatura que nao e' Insect/Rat/Spider/Squirrel recebe -1/-1 por criatura MINHA que e' (cada criatura conta uma vez, ruling 2024-07-26).
      Morre a carta nao protegida com tenacidade <= N. Todas as fichas (Rat, Squirrel, Mercenary changeling) sao protegidas."""
    named = [n for n in state.battlefield if is_creature_card(n)]
    rt, sq, mc = state.rat_tokens, state.squirrel_tokens, state.mercenary_tokens
    if name == "Damnation":
        return {"named": named, "rat": rt, "sq": sq, "mc": mc, "loss": len(named) + rt + sq + mc, "new_squirrels": 0, "type": None}
    if name == "Kindred Dominance":
        best = None
        for t in sorted({x for n in named for x in _types_of(n)} | {"Rat", "Squirrel"}):
            dn = [n for n in named if t not in _types_of(n)]
            r = rt if t != "Rat" else 0
            q = sq if t != "Squirrel" else 0
            key = (len(dn) + r + q, sum(CARD_DB[n].mv for n in dn), t != "Rat", t)
            if best is None or key < best[0]:
                best = (key, t, dn, r, q)
        _, t, dn, r, q = best
        return {"named": dn, "rat": r, "sq": q, "mc": 0, "loss": len(dn) + r + q, "new_squirrels": 0, "type": t}
    if name == "Swarmyard Massacre":
        prot = [n for n in named if SWARMYARD_PROTECTED_TYPES & set(_types_of(n))]
        n_prot = len(prot) + rt + (sq + 2) + mc
        dn = [n for n in named if not (SWARMYARD_PROTECTED_TYPES & set(_types_of(n))) and CREATURE_TOUGHNESS.get(n, 99) <= n_prot]
        return {"named": dn, "rat": 0, "sq": 0, "mc": 0, "loss": len(dn), "new_squirrels": 2, "type": None}
    raise KeyError(name)


def wipe_held(state: GameState, name: str) -> bool:
    """True se o wipe, com o efeito proprio ligado, tem perda propria (liquida dos corpos que ele cria, se WIPE_GATE_NET_OF_NEW_TOKENS) acima de WIPE_CAST_MAX_OWN_LOSS: nao e' conjurado (e conta 1 retencao por turno)."""
    if WIPE_CAST_MAX_OWN_LOSS is None or name not in WIPE_CARDS or not _wipe_effect_on(name):
        return False
    plan = wipe_plan(state, name)
    if plan["loss"] - (plan["new_squirrels"] if WIPE_GATE_NET_OF_NEW_TOKENS else 0) <= WIPE_CAST_MAX_OWN_LOSS:
        return False
    if name not in state.wipes_held_this_turn:
        state.wipes_held_this_turn.add(name)
        state.wipe_held_total += 1
    return True


def apply_own_wipe(state: GameState, name: str):
    """Resolve o efeito do wipe no MEU campo. As mortes sao SIMULTANEAS (CR 603.10, last known information): cada fonte de gatilho de morte (Zulaport, Pitiless Plunderer, Syr Konrad,
    Species Specialist, Ninja Teen) ve o campo de ANTES, mesmo se ela propria morrer junto; mesma contabilidade de `try_smart_opponent_wipe`."""
    plan = wipe_plan(state, name)
    if plan["new_squirrels"]:
        create_squirrel_tokens(state, plan["new_squirrels"], source=name)
    named_dying, rt, sq, mc = plan["named"], plan["rat"], plan["sq"], plan["mc"]
    total_dying = len(named_dying) + rt + sq + mc
    total_rat_dying = sum(1 for n in named_dying if is_rat(n)) + rt + mc
    zulaport_present = "Zulaport Cutthroat" in state.battlefield
    plunderer_present = "Pitiless Plunderer" in state.battlefield
    konrad_present = "Syr Konrad, the Grim" in state.battlefield
    species_present = "Species Specialist" in state.battlefield
    for n in named_dying:
        _wipe_remove_creature_no_trigger(state, n)
    state.rat_tokens -= rt
    state.squirrel_tokens -= sq
    state.mercenary_tokens -= mc
    if not total_dying:
        return
    state.permanent_left_battlefield_this_turn = True          # Disappear: "left the battlefield" (mais amplo que "dies")
    state.creatures_died_this_turn += total_dying
    state.wipe_own_creatures_lost_total += total_dying
    if zulaport_present:
        state.life += total_dying
        state.proxy_damage_total += total_dying
    if NINJA_TEEN_LEVELS_AND_DRAIN and "Ninja Teen" in state.battlefield:
        state.proxy_damage_total += total_dying
        state.ninja_teen_drain_total += total_dying
    if plunderer_present:
        other = total_dying - (1 if "Pitiless Plunderer" in named_dying else 0)
        if other:
            state.treasure_tokens += other
            state.tokens_created_total += other
    if konrad_present:
        other = total_dying - (1 if "Syr Konrad, the Grim" in named_dying else 0)
        if other:
            state.proxy_damage_total += other
    if species_present and total_rat_dying:
        draw_cards(state, total_rat_dying)


def enter_battlefield(state: GameState, name: str, from_hand: bool = True, tapped: bool = False):
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
    if CARD_DB[name].tags & {"rock2", "coffers", "urborg", "nykthos", "castle_locthwain",
                              "crypt_of_agadeem", "swamp_double", "soul_stone"}:
        state.ramp_pieces_cast_total += 1
    black_etb_trigger(state, name)
    resolve_etb(state, name)
    if EMERITUS_ENTERS_PREPARED and name == "Emeritus of Woe // Demonic Tutor":
        state.emeritus_prepared = True       # "This creature enters prepared."
    if THORNBITE_STAFF_ENABLED and state.staff_holder == name:
        state.staff_holder = None            # o holder saiu e voltou: e' um objeto novo, o Staff nao continua preso a ele


def resolve_cast(state: GameState, name: str, free: bool = False, trigger_done: bool = False):
    if not free and name in state.hand:
        state.hand.remove(name)
    if name in LAND_NAMES:
        state.battlefield.append(name)
        return
    if EXTORT_ENABLED and "Crypt Ghast" in state.battlefield:
        extort_trigger(state)
    ctype = CARD_DB[name].ctype
    if ctype in ("instant", "sorcery"):
        if "interaction" in CARD_DB[name].tags:
            state.interaction_spells_cast_total += 1
        resolve_instant_sorcery(state, name)
        state.graveyard.append(name)
        return
    if is_creature_card(name) and not trigger_done:
        creature_cast_trigger(state, name)
    enter_battlefield(state, name, from_hand=False)
    thrumming_stone_ripple(state, name, free=free)


def extort_trigger(state: GameState):
    """Crypt Ghast: 'Whenever you cast a spell, you may pay {W/B}. If you do, each opponent loses 1 life and you gain that much life.' O gatilho resolve ANTES da magia.
    Politica: paga se o mana restante ainda cobre a proxima jogada que a mao tem (pagar nao tira uma conjuracao)."""
    rem = remaining_mana(state)
    if rem < 1:
        return
    prox = [effective_cost(state, n) for n in state.hand if n not in LAND_NAMES and can_cast(state, n)]
    if prox and rem - 1 < min(prox):
        return
    spend_mana(state, 1)
    state.life += NUM_OPPONENTS              # ruling 2024-01-12: o ganho e' o TOTAL perdido por todos os oponentes
    state.proxy_damage_total += 1
    state.extort_paid_total += 1


def thrumming_stone_ripple(state: GameState, name: str, free: bool):
    """'Spells you cast have ripple 4' -- revela 4 do topo, conjura de
    graca toda copia do MESMO NOME revelada. So dispara pra magica REAL
    conjurada (nao pro proprio ripple recursivo -- cada carta conjurada
    de graca aqui NAO dispara ripple de novo, regra real: ripple e' uma
    habilidade da magica original na pilha, as copias reveladas nao tem
    ripple proprio)."""
    if "Thrumming Stone" not in state.battlefield:
        return
    if not state.library:
        return
    top4 = state.library[:4]
    del state.library[:4]
    matches = [c for c in top4 if c == name]
    for m in matches:
        top4.remove(m)
        state.thrumming_stone_free_casts_total += 1
        resolve_cast(state, m, free=True)
    state.library.extend(top4)  # "put the rest on the bottom"


def resolve_instant_sorcery(state: GameState, name: str):
    tags = CARD_DB[name].tags

    if "sac_draw2_treasure" in tags:  # Deadly Dispute
        if state.treasure_tokens > 0:
            state.treasure_tokens -= 1
            state.permanent_left_battlefield_this_turn = True
        else:
            sacrifice_any_creature(state, 1)
        draw_cards(state, 2)
        state.treasure_tokens += 1
        state.tokens_created_total += 1

    elif "sac_ritual4" in tags:  # Culling the Weak
        sacrifice_any_creature(state, 1)

    elif "removal_life_loss" in tags:  # Withering Torment
        state.life -= 2

    elif "wipe_asymmetric_type" in tags:  # Kindred Dominance
        state.wipe_casts_total += 1
        state.wipe_kindred_total += 1
        if WIPE_EFFECT_KINDRED:
            apply_own_wipe(state, name)
        # chave desligada: so' "conjuravel"/metrica de interacao, sem efeito no proprio board (rodada 4 e anteriores; ver a justificativa antiga no git)

    elif "squirrel_tokens_wipe_asymmetric" in tags:  # Swarmyard Massacre
        state.wipe_casts_total += 1
        state.wipe_swarmyard_total += 1
        if WIPE_EFFECT_SWARMYARD:
            apply_own_wipe(state, name)           # os 2 Esquilos primeiro, depois o -1/-1
        else:
            create_squirrel_tokens(state, 2, source="Swarmyard Massacre")

    elif "wipe_symmetric_no_target" in tags:  # Damnation
        state.wipe_casts_total += 1
        state.wipe_damnation_total += 1
        if WIPE_EFFECT_DAMNATION:
            apply_own_wipe(state, name)

    elif "life_for_rats" in tags:  # Plague of Vermin
        pay = min(10, max(0, state.life - 20))  # paga vida sobrando acima de 20, teto defensivo de 10
        if PLAGUE_PAYS_WITH_AYARA and AYARA_TOKEN_TRIGGER and "Ayara, First of Locthwain" in state.battlefield:
            # combo (Commander Spellbook 884-5035): cada ficha de Rat dispara Ayara (+1 de vida): paga tudo menos 1 e a vida volta
            pay = min(PLAGUE_COMBO_CAP, max(0, state.life - 1))
            if pay > 0:
                note_combo(state, "combo_ayara_plague_turn")
        if pay > 0:
            state.life -= pay
            for _ in range(pay):
                create_rat_token(state, source="Plague of Vermin")

    elif "reanimate" in tags:  # Reanimate
        pool = [n for n in state.graveyard if is_creature_card(n)]
        if pool:
            best = max(pool, key=lambda n: CARD_DB[n].mv)
            state.graveyard.remove(best)
            state.life -= CARD_DB[best].mv
            enter_battlefield(state, best, from_hand=False)
            state.recursion_events_total += 1
            konrad_gy_left(state, 1)

    elif "return_all_copies_hand" in tags:  # Echoing Return
        pool = [n for n in state.graveyard if is_creature_card(n)]
        if pool:
            best = max(pool, key=lambda n: CARD_DB[n].mv)
            copies = [n for n in state.graveyard if n == best]
            for c in copies:
                state.graveyard.remove(c)
                state.hand.append(c)
            state.recursion_events_total += len(copies)
            konrad_gy_left(state, len(copies))

    elif "tutor_all_copies_hand" in tags:  # Secret Salvage
        pool = state.graveyard[:]
        if pool:
            target = max(pool, key=lambda n: state.library.count(n) + (1 if n == "Rat Colony" else 0))
            state.graveyard.remove(target)
            # So o `target` sai do cemiterio de verdade (as copias vem da
            # BIBLIOTECA via busca, nao do cemiterio) -- Konrad so' conta
            # se o proprio `target` exilado for carta de criatura.
            if is_creature_card(target):
                konrad_gy_left(state, 1)
            copies = [n for n in state.library if n == target]
            for c in copies:
                state.library.remove(c)
                state.hand.append(c)
            state.tutors_used_total += len(copies)


# ---------------------------------------------------------------------------
# Skullclamp -- motor de draw repetivel
# ---------------------------------------------------------------------------

def skullclamp_loop(state: GameState):
    """Equipar Skullclamp num token 1/1 (Rat ou Esquilo) vira 2/0 -- morre
    por regra de estado (0 de toughness), compra 2. Equip {1}. Repete
    enquanto houver mana E token disponivel -- motor de draw quase sem
    fim documentado na auditoria.md (secao 6)."""
    if "Skullclamp" not in state.battlefield:
        return
    while remaining_mana(state) >= 1 and (state.rat_tokens > 0 or state.squirrel_tokens > 0 or state.mercenary_tokens > 0):
        spend_mana(state, 1)
        if state.rat_tokens > 0:
            state.rat_tokens -= 1
            was_rat = True
        elif state.squirrel_tokens > 0:
            state.squirrel_tokens -= 1
            was_rat = False
        else:
            state.mercenary_tokens -= 1
            was_rat = True  # changeling -- Mercenary Token e' todo tipo de criatura, Rat incluso
        state.permanent_left_battlefield_this_turn = True
        on_creature_dies(state, 1, is_token=True, dying_is_rat=was_rat)
        draw_cards(state, 2)
        state.skullclamp_draws_total += 2


# ---------------------------------------------------------------------------
# Ninja Teen -- Classe (3 niveis reais)
# ---------------------------------------------------------------------------

def ninja_teen_level_up(state: GameState):
    if "Ninja Teen" not in state.battlefield:
        return
    # Nivel 1 -> 2 custa {1}{B} (mv=2), nivel 2 -> 3 custa {B} (mv=1) --
    # "as a sorcery", qualquer main phase com prioridade e mana sobrando.
    if NINJA_TEEN_LEVELS_AND_DRAIN and state.ninja_teen_level == 0:
        state.ninja_teen_level = 1           # a Classe entra no nivel 1, sem pagar nada
    if state.ninja_teen_level == 0 and remaining_mana(state) >= 2:
        spend_mana(state, 2)
        state.ninja_teen_level = 1
    if state.ninja_teen_level == 1 and remaining_mana(state) >= 2:
        spend_mana(state, 2)
        state.ninja_teen_level = 2
    if state.ninja_teen_level == 2 and remaining_mana(state) >= 1:
        spend_mana(state, 1)
        state.ninja_teen_level = 3


def ninja_teen_sneak(state: GameState):
    """Nivel 3: 'Creature cards in your graveyard have sneak {3}{B}. You
    may cast creature spells from your graveyard using their sneak
    abilities.' Motor de recursao real -- conjura do cemiterio pagando
    {3}{B} (nao de graca)."""
    if state.ninja_teen_level < 3:
        return
    if NINJA_TEEN_SNEAK_RULING:
        return                               # (novo) o sneak so' existe no declare blockers: ninja_teen_sneak_combat, chamado por combat_step
    pool = [n for n in state.graveyard if is_creature_card(n)]
    while pool and remaining_mana(state) >= 4:
        best = max(pool, key=lambda n: CARD_DB[n].mv)
        spend_mana(state, 4)
        state.graveyard.remove(best)
        enter_battlefield(state, best, from_hand=False)
        state.recursion_events_total += 1
        konrad_gy_left(state, 1)
        pool = [n for n in state.graveyard if is_creature_card(n)]


def sneak_returnable(state: GameState) -> Optional[str]:
    """Atacante NAO bloqueado (goldfish: ninguem bloqueia) que posso devolver a mao: ficha de Rat que nao entrou neste turno (a ficha de agora tem doenca de invocacao e nao ataca);
    senao a carta nomeada pronta mais barata (nunca o comandante)."""
    if state.rat_tokens - state.rat_tokens_created_this_turn > 0:
        return "__rat_token__"
    cands = [n for n in ready_creatures(state) if n != COMMANDER]
    return min(cands, key=lambda n: CARD_DB[n].mv) if cands else None


def ninja_teen_sneak_combat(state: GameState):
    """Ninja Teen nivel 3 + CR 702.190a: 'Sneak {3}{B}: any time you could cast an instant during your declare blockers step, you may cast this spell by paying {3}{B} and RETURNING AN
    UNBLOCKED CREATURE you control to its owner's hand rather than paying its mana cost.' Rulings 2026-01-27: so' no declare blockers do meu turno, tem de pagar o custo inteiro (inclusive
    devolver o atacante); a criatura entra virada e atacando (702.190b). A magia e' CONJURADA (Bontu's, extort e ripple disparam) e o atacante devolvido 'leaves the battlefield' (Disappear, Ninja Teen)."""
    if state.ninja_teen_level < 3 or "Ninja Teen" not in state.battlefield:
        return
    guard = 0
    while guard < 20:
        guard += 1
        pool = [n for n in state.graveyard if is_creature_card(n)]
        if not pool:
            return
        ret = sneak_returnable(state)
        if ret is None:
            return
        best = max(pool, key=lambda n: CARD_DB[n].mv)
        cost = max(1, 4 - cost_reduction(state, best))        # {3}{B}: as reducoes cortam so' o generico; o piso e' o {B}
        if remaining_mana(state) < cost:
            return
        spend_mana(state, cost)
        if ret == "__rat_token__":
            state.rat_tokens -= 1                              # a ficha devolvida a mao deixa de existir
        else:
            state.battlefield.remove(ret)
            state.hand.append(ret)
            state.creature_cast_turn.pop(ret, None)
        state.permanent_left_battlefield_this_turn = True
        if NINJA_TEEN_LEVELS_AND_DRAIN:
            state.proxy_damage_total += 1                      # Ninja Teen nivel 1: a criatura devolvida saiu do campo
            state.ninja_teen_drain_total += 1
        state.graveyard.remove(best)
        konrad_gy_left(state, 1)
        resolve_cast(state, best, free=True)                   # conjura (gatilhos de conjuracao) e entra em campo
        state.recursion_events_total += 1
        state.sneak_casts_total += 1


# ---------------------------------------------------------------------------
# Rat King -- reanimacao (sac 3 Rats)
# ---------------------------------------------------------------------------

def rat_king_reanimate(state: GameState):
    # Achados reais: (1) "{T}, Sacrifice three Rats: ..." tem {T} no
    # custo -- precisa nao estar com doenca de invocacao (nunca era
    # checado, o Rat King podia reanimar no mesmo turno em que era
    # conjurado) E so' pode ativar 1x por turno (mesma classe de bug do
    # Ayara/Marrow-Gnawer/Priest acima). (2) linha morta
    # `state.tapped_lands_this_turn` (leitura sem efeito) removida.
    if not state.commander_in_play or COMMANDER not in ready_creatures(state):
        return
    if COMMANDER in state.tapped_creatures_this_turn:
        return
    if (rat_count(state) - (1 if (RAT_KING_REANIMATE_COST and COMMANDER in state.battlefield and is_rat(COMMANDER)) else 0)) < 3:
        return
    pool = [n for n in state.graveyard if is_creature_card(n)]
    if not pool:
        return
    # Prioriza o nome com MAIS copias no cemiterio (Rat Colony e' o alvo
    # ideal -- traz TODAS as copias de volta de uma vez, tapped).
    best = max(pool, key=lambda n: state.graveyard.count(n))
    sacrifice_rats(state, 3)
    copies = [n for n in state.graveyard if n == best]
    for c in copies:
        state.graveyard.remove(c)
        enter_battlefield(state, c, from_hand=False)
    konrad_gy_left(state, len(copies))
    state.tapped_creatures_this_turn.add(COMMANDER)
    state.rat_king_reanimations_total += len(copies)
    state.recursion_events_total += len(copies)


# ---------------------------------------------------------------------------
# The Soul Stone -- ativacao unica + motor de upkeep
# ---------------------------------------------------------------------------

def try_harness_soul_stone(state: GameState):
    if state.soul_stone_harnessed or "The Soul Stone" not in state.battlefield:
        return
    if remaining_mana(state) < (8 if SOUL_STONE_SHARED_TAP else 7):    # {6}{B} + {T} da propria pedra: ela nao rende o {B} do turno
        return
    if state.rat_tokens == 0 and state.squirrel_tokens == 0 and state.mercenary_tokens == 0 \
            and not [n for n in state.battlefield if is_creature_card(n) and n != COMMANDER]:
        return  # precisa de uma criatura pra exilar
    spend_mana(state, 7)
    if state.rat_tokens > 0:
        state.rat_tokens -= 1
    elif state.squirrel_tokens > 0:
        state.squirrel_tokens -= 1
    elif state.mercenary_tokens > 0:
        state.mercenary_tokens -= 1
    else:
        creatures = [n for n in state.battlefield if is_creature_card(n) and n != COMMANDER]
        cheapest = min(creatures, key=lambda n: CARD_DB[n].mv)
        state.battlefield.remove(cheapest)  # exilada, nao vai pro cemiterio
    state.permanent_left_battlefield_this_turn = True
    state.soul_stone_harnessed = True
    if SOUL_STONE_SHARED_TAP:
        state.soul_stone_tapped = True
    if NINJA_TEEN_LEVELS_AND_DRAIN and "Ninja Teen" in state.battlefield:
        state.proxy_damage_total += 1        # a criatura exilada "leaves the battlefield"
        state.ninja_teen_drain_total += 1


def try_takenuma_channel(state: GameState):
    # Achado real 2026-09-01 (leitura linha-a-linha, "compile TUDO"):
    # oraculo real "Channel -- {3}{B}, Discard this card: Mill three
    # cards, then return a creature or planeswalker card from your
    # graveyard to your hand. This ability costs {1} less to activate for
    # each legendary creature you control." -- tag "takenuma" nunca lida
    # em lugar nenhum; so o `{T}: Add {B}` era coberto (generico, via
    # LAND_NAMES em lands_mana()). So vale descartar o terreno em vez de
    # jogar (play_land ja rodou antes de main_phase) quando sobra OUTRO
    # terreno na mao pra nao perder o land drop do turno.
    if "Takenuma, Abandoned Mire" not in state.hand:
        return
    other_lands_in_hand = [n for n in state.hand if n in LAND_NAMES and n != "Takenuma, Abandoned Mire"]
    if not other_lands_in_hand:
        return
    legendary_ct = sum(1 for n in state.battlefield if n in LEGENDARY_CREATURES)
    cost = max(0, 4 - legendary_ct)
    if remaining_mana(state) < cost:
        return
    state.hand.remove("Takenuma, Abandoned Mire")
    spend_mana(state, cost)
    if state.library:
        milled = state.library[:3]
        del state.library[:3]
        state.graveyard.extend(milled)
        for m in milled:
            konrad_gy_entered(state, m)
    pool = [n for n in state.graveyard if is_creature_card(n) or CARD_DB[n].ctype == "planeswalker"]
    if pool:
        best = max(pool, key=lambda n: CARD_DB[n].mv)
        state.graveyard.remove(best)
        state.hand.append(best)
        state.recursion_events_total += 1
        if is_creature_card(best):
            konrad_gy_left(state, 1)


def soul_stone_upkeep_reanimate(state: GameState):
    if not state.soul_stone_harnessed:
        return
    pool = [n for n in state.graveyard if is_creature_card(n)]
    if not pool:
        return
    best = max(pool, key=lambda n: CARD_DB[n].mv)
    state.graveyard.remove(best)
    enter_battlefield(state, best, from_hand=False)
    state.recursion_events_total += 1
    konrad_gy_left(state, 1)


# ---------------------------------------------------------------------------
# Motores adicionais (dorks/rocks/rituais/loops de token)
# ---------------------------------------------------------------------------

def cast_rituals(state: GameState):
    if "Dark Ritual" in state.hand and can_cast(state, "Dark Ritual"):
        spend_mana(state, effective_cost(state, "Dark Ritual"))
        resolve_cast(state, "Dark Ritual")
        state.mana_spent_this_turn -= 3  # ritual adiciona 3 B liquido (custou 1)
        state.ramp_pieces_cast_total += 1
    if "Culling the Weak" in state.hand and can_cast(state, "Culling the Weak") \
            and (sum(1 for x in state.battlefield if is_creature_card(x) and x != COMMANDER) + state.rat_tokens + state.squirrel_tokens
                 + (state.mercenary_tokens if SACRIFICE_COST_NEEDS_FODDER else 0)) > 2:
        spend_mana(state, effective_cost(state, "Culling the Weak"))
        resolve_cast(state, "Culling the Weak")
        state.mana_spent_this_turn -= 4
        state.ramp_pieces_cast_total += 1


def piper_activations(state: GameState):
    # Achado real: oraculo tem {T} no custo ("{1}{B}, {T}: Create a Rat
    # token" / "{2}{B}{B}, {T}, Sacrifice three Rats: Gain control of
    # target creature") -- as 2 habilidades competem pelo MESMO tap, entao
    # so uma pode ser ativada por turno, uma unica vez (nao um loop
    # repetivel gastando mana toda vez que sobra 2). O `while` anterior
    # criava tokens ilimitados por turno enquanto houvesse mana, o que
    # nunca foi legal (mesma classe de bug ja documentada em
    # `tapped_creatures_this_turn` pra Ayara/Marrow-Gnawer/Priest/Rat King).
    if "Piper of the Swarm" not in state.battlefield:
        return
    if "Piper of the Swarm" not in ready_creatures(state):
        return
    if "Piper of the Swarm" in state.tapped_creatures_this_turn:
        return
    # Modo "roubar criatura" (2BB, sac 3 Rats) precisa de alvo do oponente
    # -- 📊 estrutural (Regra 1), nunca a escolha real disponivel aqui.
    # Sobra so' o modo de token, ativado no maximo 1x por turno.
    if remaining_mana(state) >= 2:
        spend_mana(state, 2)
        create_rat_token(state, source="Piper of the Swarm")
        state.tapped_creatures_this_turn.add("Piper of the Swarm")


def ready_creatures(state: GameState):
    return [n for n in state.battlefield if is_creature_card(n)
            and state.creature_cast_turn.get(n, -1) < state.turn]


def syr_konrad_mill_activation(state: GameState):
    """Achado real: Syr Konrad tem uma 2a habilidade real, "{1}{B}: Each
    player mills a card" -- a tag "mill_activated" existia no `add()` mas
    nunca era despachada em lugar nenhum (fantasma completo). SEM {T} no
    custo -- genuinamente repetivel varias vezes por turno enquanto sobrar
    mana (regra real, nao aproximacao). "Each player" modelado so' pra nos
    mesmos (unico jogador real neste goldfish solo, mesma convencao do
    Storm Fleet Negotiator/Parley noutros decks). Cada carta de criatura
    minada dessa forma dispara a propria clausula 2 do Konrad
    (`konrad_gy_entered`, "put into a graveyard from anywhere other than
    the battlefield") -- sinergia real com sua propria segunda ativacao."""
    if "Syr Konrad, the Grim" not in state.battlefield:
        return
    while remaining_mana(state) >= 2 and state.library:
        spend_mana(state, 2)
        milled = state.library.pop(0)
        state.graveyard.append(milled)
        konrad_gy_entered(state, milled)


def priest_activation(state: GameState):
    # Achado real: "{T}, Sacrifice two other creatures: ..." tem {T} no
    # custo -- so' pode ativar 1x por turno (main_phase roda 2x, antes e
    # depois do combate, e nada impedia a 2a chamada de ativar de novo).
    if "Priest of Forgotten Gods" not in state.battlefield:
        return
    if "Priest of Forgotten Gods" not in ready_creatures(state):
        return
    if "Priest of Forgotten Gods" in state.tapped_creatures_this_turn:
        return
    if creature_count(state) - 1 < 2:  # precisa de 2 OUTRAS criaturas
        return
    sacrifice_any_creature(state, 2, exclude="Priest of Forgotten Gods" if PRIEST_EXACT else None)
    state.mana_spent_this_turn = max(0, state.mana_spent_this_turn - 2)  # {B}{B} liquido
    draw_cards(state, 1)
    if not PRIEST_EXACT:
        state.life -= 2                      # (antigo) perda de vida PROPRIA que o oraculo nao tem: "any number of target players"
    state.proxy_damage_total += 2
    state.tapped_creatures_this_turn.add("Priest of Forgotten Gods")


def ayara_activation(state: GameState):
    # Achado real: mesma classe de bug -- "{T}, Sacrifice another black
    # creature: Draw a card" tem {T} no custo, so' 1x por turno.
    if "Ayara, First of Locthwain" not in state.battlefield:
        return
    if "Ayara, First of Locthwain" not in ready_creatures(state):
        return
    if "Ayara, First of Locthwain" in state.tapped_creatures_this_turn:
        return
    if AYARA_SACRIFICE_TOKENS and state.rat_tokens > 0:
        state.rat_tokens -= 1                # "Sacrifice another black creature": a ficha de Rat e' preta e custa menos que uma carta
        state.permanent_left_battlefield_this_turn = True
        on_creature_dies(state, 1, is_token=True)
        draw_cards(state, 1)
        state.tapped_creatures_this_turn.add("Ayara, First of Locthwain")
        return
    other_black = [n for n in state.battlefield if is_black_creature(n) and n != "Ayara, First of Locthwain" and n != COMMANDER]
    if other_black:
        cheapest = min(other_black, key=lambda n: CARD_DB[n].mv)
        leave_battlefield(state, cheapest, to_graveyard=True)
        draw_cards(state, 1)
        state.tapped_creatures_this_turn.add("Ayara, First of Locthwain")


def marrow_gnawer_activation(state: GameState):
    # Achado real: mesma classe de bug -- "{T}, Sacrifice a Rat: ..." tem
    # {T} no custo, so' 1x por turno.
    if "Marrow-Gnawer" not in state.battlefield or "Marrow-Gnawer" not in ready_creatures(state):
        return
    if "Marrow-Gnawer" in state.tapped_creatures_this_turn:
        return
    if rat_count(state) < 2:
        return
    if THORNBITE_STAFF_ENABLED and state.staff_holder == "Marrow-Gnawer" and staff_valid(state):
        marrow_staff_loop(state)
        return
    if MARROW_X_AFTER_SACRIFICE:
        outros = state.rat_tokens + state.mercenary_tokens + sum(1 for n in state.battlefield if is_rat(n) and n != COMMANDER and n != "Marrow-Gnawer")
        if outros < 1:
            return                           # so' restaria sacrificar o proprio Marrow-Gnawer ou o comandante
        sacrifice_rats(state, 1)
        x = rat_count(state)                 # ruling 2004-12-01: conta os Rats quando resolve, SEM o sacrificado
    else:
        x = rat_count(state)
        sacrifice_rats(state, 1)
    for _ in range(x):
        create_rat_token(state, source="Marrow-Gnawer")
    state.tapped_creatures_this_turn.add("Marrow-Gnawer")


def castle_locthwain_activation(state: GameState):
    if "Castle Locthwain" not in state.battlefield or "Castle Locthwain" in state.tapped_lands_this_turn:
        return
    if remaining_mana(state) >= 3:
        spend_mana(state, 3)
        draw_cards(state, 1)
        state.life -= len(state.hand)
        state.tapped_lands_this_turn.add("Castle Locthwain")


def big_apple_activation(state: GameState):
    # Achado real: "{5}, {T}: Create a 1/1 black Rat for each opponent you
    # have" so' era checado dentro de `play_land()`, ou seja, so' no
    # PROPRIO turno em que a carta era jogada -- nunca mais de novo em
    # nenhum turno seguinte (bug real, terreno repetivel tratado como
    # ativacao unica). Corrigido pra checar toda vez que `main_phase` roda
    # com mana sobrando, igual a Castle Locthwain/Nykthos. "For each
    # opponent" modelado como 1 token por ativacao (mesma convencao de
    # proxy de oponente unico ja usada nesta sessao pra efeitos
    # beneficios que dependem de contagem de oponentes nao modelada).
    if "Big Apple, 3 a.m." not in state.battlefield or "Big Apple, 3 a.m." in state.tapped_lands_this_turn:
        return
    if remaining_mana(state) >= 5:
        spend_mana(state, 5)
        for _ in range(NUM_OPPONENTS if BIG_APPLE_PER_OPPONENT else 1):     # "for each opponent you have"
            create_rat_token(state, source="Big Apple, 3 a.m.")
        state.big_apple_activations_total += 1
        state.tapped_lands_this_turn.add("Big Apple, 3 a.m.")


def staff_valid(state: GameState) -> bool:
    """O Staff esta em campo e o holder ainda existe. Os tokens sao contadores agregados: o holder-ficha vale enquanto houver Mercenary."""
    if state.staff_holder is None:
        return False
    if "Thornbite Staff" not in state.battlefield:
        state.staff_holder = None
        return False
    h = state.staff_holder
    if (h == "__mercenary__" and state.mercenary_tokens <= 0) or (h != "__mercenary__" and h not in state.battlefield):
        state.staff_holder = None
        return False
    return True


def staff_untap_on_death(state: GameState):
    """'Equipped creature has: Whenever a creature dies, untap this creature.'"""
    if state.staff_holder is not None and staff_valid(state):
        if state.staff_holder == "__mercenary__":
            state.staff_tapped = False
        else:
            state.tapped_creatures_this_turn.discard(state.staff_holder)


def staff_holder_ready_to_tap(state: GameState) -> bool:
    if not staff_valid(state):
        return False
    if state.staff_holder == "__mercenary__":
        return (not state.staff_tapped) and state.staff_attach_turn < state.turn      # a ficha tem doenca de invocacao no turno em que entra
    h = state.staff_holder
    return h in ready_creatures(state) and h not in state.tapped_creatures_this_turn


def staff_equip_policy(state: GameState):
    """Equip {4}. Politica (minha): o unico alvo de Equip e' o Marrow-Gnawer (a peca do combo do Spellbook), se ele esta em campo e o Staff ainda nao esta nele."""
    if "Thornbite Staff" not in state.battlefield or "Marrow-Gnawer" not in state.battlefield:
        return
    if state.staff_holder == "Marrow-Gnawer" and staff_valid(state):
        return
    if remaining_mana(state) < 4:
        return
    spend_mana(state, 4)
    state.staff_holder = "Marrow-Gnawer"
    state.staff_attach_turn = state.turn
    state.staff_equips_total += 1


def staff_ping_policy(state: GameState):
    """'{2},{T}: This creature deals 1 damage to any target' com o mana que sobrou na 2a fase principal (proxy de dano; nunca tira jogada). Um ping por chamada: as desviradas por morte
    acontecem em outros pontos do turno."""
    if staff_holder_ready_to_tap(state) and remaining_mana(state) >= 2:
        spend_mana(state, 2)
        state.proxy_damage_total += 1
        state.staff_pings_total += 1
        if state.staff_holder == "__mercenary__":
            state.staff_tapped = True
        else:
            state.tapped_creatures_this_turn.add(state.staff_holder)


def marrow_staff_loop(state: GameState):
    """Combo Marrow-Gnawer + Thornbite Staff (Spellbook 2178-3126; prerequisito: "um Rat adicional"): {T}, sacrifica um Rat -> o Rat morre -> o Staff desvira o Marrow -> X fichas.
    Cada volta faz R -> 2R-2: com R=2 o numero de Rats nao cresce (mas cada volta e' uma morte + uma entrada: payoffs infinitos), com 3+ cresce. O loop real e' infinito;
    o simulador para em MARROW_STAFF_LOOP_RAT_TARGET Rats (ou MARROW_STAFF_LOOP_MAX_ITERS voltas)."""
    iters = 0
    while iters < MARROW_STAFF_LOOP_MAX_ITERS and rat_count(state) < MARROW_STAFF_LOOP_RAT_TARGET:
        if "Marrow-Gnawer" not in state.battlefield or "Marrow-Gnawer" in state.tapped_creatures_this_turn:
            break
        outros = state.rat_tokens + state.mercenary_tokens + sum(1 for n in state.battlefield if is_rat(n) and n != COMMANDER and n != "Marrow-Gnawer")
        if outros < 1 or rat_count(state) < 2:
            break
        state.tapped_creatures_this_turn.add("Marrow-Gnawer")
        sacrifice_rats(state, 1)             # on_creature_dies -> staff_untap_on_death: o Marrow desvira
        x = rat_count(state)
        for _ in range(x):
            create_rat_token(state, source="Marrow-Gnawer + Thornbite Staff")
        iters += 1
        state.marrow_staff_loop_iters_total += 1
        if iters >= 2:
            note_combo(state, "combo_marrow_staff_turn")      # uma volta so' = a ativacao normal do Marrow-Gnawer; a 2a so' acontece porque o Staff desvirou


def lifegain_engine_in_play(state: GameState) -> bool:
    return any(n in LIFEGAIN_ENGINES for n in state.battlefield)


def mercenary_enters(state: GameState):
    """A ficha 3/2 changeling entra: e' Shaman (changeling), entao o Thornbite Staff se anexa a ela."""
    state.mercenary_tokens += 1
    state.tokens_created_total += 1
    if THORNBITE_STAFF_ENABLED and "Thornbite Staff" in state.battlefield and not staff_valid(state):
        # Thornbite Staff: "Whenever a Shaman creature enters, you may attach this Equipment to it." O Mercenary tem changeling (todo tipo de criatura): e' Shaman.
        state.staff_holder = "__mercenary__"
        state.staff_attach_turn = state.turn
        state.staff_tapped = False
        state.staff_auto_attach_total += 1


def black_market_connections_policy_step(state: GameState):
    """Black Market Connections (oraculo ao vivo): "At the beginning of your first main phase, choose one or more -- Sell Contraband: create a Treasure. You lose 1 life. / Buy Information:
    draw a card. You lose 2 life. / Hire a Mercenary: create a 3/2 colorless Shapeshifter with changeling. You lose 3 life." A perda de vida e' EFEITO do modo, nao custo (CR 119.4 nao se aplica;
    nao ha ruling). Pedido do usuario (2026-10-28): o modo 1 e' o que importa; 2 e 3 so' com um mecanismo de lifegain em campo. POLITICA MINHA (nao do oraculo): nunca escolher um modo que leve
    a vida a 0 ou menos (a regra permitiria; um jogador real nao faria)."""
    state.bmc_triggers_total += 1
    engine = lifegain_engine_in_play(state)
    if state.life - 1 >= 1:
        state.life -= 1
        state.treasure_tokens += 1
        state.tokens_created_total += 1
        state.bmc_mode1_total += 1
    if engine and state.life - 2 >= 1:
        state.life -= 2
        draw_cards(state, 1)
        state.bmc_mode2_total += 1
    else:
        state.bmc_modes_skipped_total += 1
    if engine and state.life - 3 >= 1:
        state.life -= 3
        mercenary_enters(state)
        state.bmc_mode3_total += 1
    else:
        state.bmc_modes_skipped_total += 1


def black_market_connections_step(state: GameState):
    if "Black Market Connections" not in state.battlefield:
        return
    if BMC_MODES_NEED_LIFEGAIN:
        black_market_connections_policy_step(state)
        return
    state.life -= 1
    state.treasure_tokens += 1
    state.tokens_created_total += 1
    state.life -= 2
    draw_cards(state, 1)
    state.life -= 3
    state.mercenary_tokens += 1
    state.tokens_created_total += 1
    if THORNBITE_STAFF_ENABLED and "Thornbite Staff" in state.battlefield and not staff_valid(state):
        # Thornbite Staff: "Whenever a Shaman creature enters, you may attach this Equipment to it." O Mercenary tem changeling (todo tipo de criatura): e' Shaman.
        state.staff_holder = "__mercenary__"
        state.staff_attach_turn = state.turn
        state.staff_tapped = False
        state.staff_auto_attach_total += 1


def ripples_of_undeath_step(state: GameState):
    if "Ripples of Undeath" not in state.battlefield or not state.library:
        return
    milled = state.library[:3]
    del state.library[:3]
    state.graveyard.extend(milled)
    for m in milled:
        konrad_gy_entered(state, m)
    if milled and remaining_mana(state) >= 1 and state.life > 3:
        best = max(milled, key=lambda n: CARD_DB[n].mv)
        state.graveyard.remove(best)
        state.hand.append(best)
        spend_mana(state, 1)
        state.life -= 3
        if is_creature_card(best):
            konrad_gy_left(state, 1)


def ashcoat_end_step(state: GameState):
    if "Ashcoat of the Shadow Swarm" not in state.battlefield or not state.library:
        return
    milled = state.library[:4]
    del state.library[:4]
    state.graveyard.extend(milled)
    for m in milled:
        konrad_gy_entered(state, m)
    rats_in_gy = [n for n in state.graveyard if is_rat(n)]
    returned = rats_in_gy[:2]
    for r in returned:
        state.graveyard.remove(r)
        state.hand.append(r)
    if returned:
        state.recursion_events_total += len(returned)
        konrad_gy_left(state, len(returned))  # todo Rat e' carta de criatura


def lord_skitter_combat_token(state: GameState):
    if "Lord Skitter, Sewer King" in state.battlefield:
        create_rat_token(state, source="Lord Skitter (combate)")


# ---------------------------------------------------------------------------
# Loop principal de conjuracao
# ---------------------------------------------------------------------------

def cast_card(state: GameState, name: str):
    cost = effective_cost(state, name)
    if name == COMMANDER:
        cost += 2 * (state.commander_cast_count)
    spend_mana(state, cost)
    if is_creature_card(name):
        creature_cast_trigger(state, name)
    resolve_cast(state, name, trigger_done=BONTU_TRIGGER_ONCE)
    if is_rat(name):
        pass  # Lord Skitter ETB-exile ja tratado em resolve_etb


def emeritus_demonic_tutor(state: GameState):
    if not state.emeritus_prepared:
        return
    if remaining_mana(state) < 2:
        return
    spend_mana(state, 2)  # {1}{B}
    if state.library:
        # Demonic Tutor real: busca QUALQUER carta.
        best = best_missing_creature(state, state.library) if any(is_creature_card(c) for c in state.library) else state.library[0]
        state.library.remove(best)
        state.hand.append(best)
        state.tutors_used_total += 1
    state.emeritus_prepared = False


def main_phase(state: GameState, is_first_main: bool = True):
    if is_first_main:
        black_market_connections_step(state)
        ripples_of_undeath_step(state)

    if not state.commander_in_play and can_cast(state, COMMANDER):
        # Contraataque (`try_smart_opponent_counter`, categoria do modo de
        # resiliencia -- so' faz sentido no exato momento do cast, mesmo
        # padrao ja' validado nos outros 8 decks): mana e taxa contam
        # ANTES do counter (CR 903.10a conta "cast", nao "resolved") --
        # mesma formula de custo que `cast_card` ja' usava, replicada
        # aqui (inclusive o `creature_cast_trigger` que `cast_card` ja'
        # disparava antes de resolver, pra manter o modo padrao 100%
        # identico) pra poder interceptar entre o pagamento e a entrada
        # em campo. So' entra em campo se NAO for counterada.
        cost = effective_cost(state, COMMANDER) + 2 * state.commander_cast_count
        spend_mana(state, cost)
        creature_cast_trigger(state, COMMANDER)
        if try_smart_opponent_counter(state):
            # CR 903.10a: a taxa aumenta a cada CONJURACAO, resolvendo ou
            # nao -- `enter_battlefield()` so' incrementa `commander_cast_
            # count` no caminho de sucesso (nunca chamado aqui), entao o
            # incremento pelo counter precisa ser manual.
            state.commander_cast_count += 1
        else:
            resolve_cast(state, COMMANDER, trigger_done=BONTU_TRIGGER_ONCE)  # enter_battlefield() incrementa commander_cast_count

    cast_rituals(state)
    emeritus_demonic_tutor(state)

    while True:
        castables = [n for n in state.hand if n not in LAND_NAMES and can_cast(state, n)]
        if SACRIFICE_COST_NEEDS_FODDER:
            # custo adicional "sacrifice": sem o que sacrificar a magica nao pode ser conjurada; Culling the Weak so' vale como ritual (cast_rituals)
            castables = [n for n in castables if not (n == "Culling the Weak" or (n == "Deadly Dispute" and not dispute_fodder(state)))]
        if WIPE_CAST_MAX_OWN_LOSS is not None:
            castables = [n for n in castables if not wipe_held(state, n)]     # wipe so' quando a perda propria compensa (rodada 5)
        if not castables:
            break
        # Prioriza motores baratos primeiro (curva real, maximiza corpos em campo cedo).
        castables.sort(key=lambda n: effective_cost(state, n))
        cast_card(state, castables[0])

    if THORNBITE_STAFF_ENABLED:
        staff_equip_policy(state)            # linha de vitoria: Equip {4} no Marrow-Gnawer antes de gastar o mana em utilidades (o combo pode sair na mesma fase)
    if EMERITUS_ENTERS_PREPARED:
        emeritus_demonic_tutor(state)        # Emeritus recem-conjurado "enters prepared": a copia do Demonic Tutor ja pode ser conjurada
    skullclamp_loop(state)
    piper_activations(state)
    priest_activation(state)
    ayara_activation(state)
    marrow_gnawer_activation(state)
    castle_locthwain_activation(state)
    big_apple_activation(state)
    ninja_teen_level_up(state)
    ninja_teen_sneak(state)
    rat_king_reanimate(state)
    try_harness_soul_stone(state)
    try_takenuma_channel(state)
    syr_konrad_mill_activation(state)
    if THORNBITE_STAFF_ENABLED and not is_first_main:
        staff_ping_policy(state)             # so' na 2a fase principal: o mana que sobrou de verdade


def dispute_fodder(state: GameState) -> bool:
    return state.treasure_tokens > 0 or state.rat_tokens > 0 or state.squirrel_tokens > 0 or state.mercenary_tokens > 0 \
        or any(is_creature_card(n) and n != COMMANDER for n in state.battlefield)


def combat_step(state: GameState):
    lord_skitter_combat_token(state)
    attackers_rats = [n for n in ready_creatures(state) if is_rat(n)]
    n_rat_attackers = len(attackers_rats) + state.rat_tokens + state.mercenary_tokens
    if "Valley Rotcaller" in ready_creatures(state):
        x = max(0, n_rat_attackers - 1)
        if ROTCALLER_EXACT_X:
            # "X is the number of OTHER Squirrels, Bats, Lizards, and Rats you control": todos os Rats que controlo (nao so' os prontos), mais os Esquilos; o Mercenary conta uma vez
            x = rat_count(state) + state.squirrel_tokens
            state.rotcaller_x_total += x
        state.life += x
        state.proxy_damage_total += x
    if "Karumonix, the Rat King" in ready_creatures(state):
        pass  # toxic -- sem oponente real, sem efeito numerico (Regra 1)
    if NINJA_TEEN_SNEAK_RULING:
        ninja_teen_sneak_combat(state)       # declare blockers: ninguem bloqueia no goldfish


# ---------------------------------------------------------------------------
# Terreno virado primeiro em T1/T2 -- correcao de 2026-10-05 (mesma regra do Vihaan/Megatron)
# ---------------------------------------------------------------------------
# Antes: `play_land` jogava SEMPRE o primeiro terreno da ordem propria do deck (desvirado antes de virado); a mana de um turno sem jogada era desperdicada e o
# terreno virado ficava pra um turno em que ele custa desenvolvimento. Agora, em T1..TAPPED_LAND_FIRST_MAX_TURN, havendo terreno virado E desvirado na mao, joga o
# virado, salvo se isso custar desenvolvimento: o teste e' um ENSAIO a seco da propria fase de conjuracao pre-combate (copia profunda do estado), comparando o MV
# total das cartas que saem da mao com cada candidato. Empate -> o virado. Com a chave em False o comportamento e' o antigo, bit a bit.
TAPPED_LAND_FIRST_ENABLED = True
TAPPED_LAND_FIRST_MAX_TURN = 2
TAPPED_LAND_FIRST_GHOST = False   # so' validacao: roda o ensaio mas ignora o resultado (joga o padrao). Com a chave ligada + GHOST == chave desligada prova que o ensaio nao tem efeito colateral
_TL_FORCED = None   # terreno imposto a play_land durante o ensaio a seco
_TL_BUSY = False    # trava de recursao: o ensaio chama play_land de novo


def _tl_is_tapped(state, name: str) -> bool:
    return "etb_tapped" in CARD_DB[name].tags or (name == "Castle Locthwain" and "Swamp" not in state.battlefield and not urborg_in_play(state))


def _tl_develop(sim, log: list):
    """Fase de conjuracao pre-combate do turno: a mesma sequencia que o turno roda logo depois de `play_land`."""
    main_phase(sim, is_first_main=True)


def _tl_dry_run_mv(state, land: str) -> int:
    """MV total das cartas que SAEM da mao se `land` for o terreno jogado e o resto da fase pre-combate rodar. Copia profunda (CARD_DB compartilhado; RNG do estado
    copiado e `random` global restaurado): nao muta `state`."""
    global _TL_FORCED, _TL_BUSY
    memo = {id(c): c for c in CARD_DB.values()}
    saved = random.getstate()
    sim = copy.deepcopy(state, memo)
    ficam = collections.Counter(sim.hand)
    ficam[land] -= 1
    _TL_FORCED, _TL_BUSY = land, True
    try:
        play_land(sim)
        _tl_develop(sim, None)
    finally:
        _TL_FORCED, _TL_BUSY = None, False
        random.setstate(saved)
    saiu = ficam - collections.Counter(sim.hand)
    return sum(CARD_DB[c].mv for c in saiu.elements() if c in CARD_DB)


def _tl_dry_run_mana(state, land: str) -> int:
    """Como `_tl_dry_run_mv`, mas devolve o MANA GASTO no turno (`mana_spent_this_turn`): conta o comandante (que nao esta na mao) e as habilidades pagas com mana."""
    global _TL_FORCED, _TL_BUSY
    memo = {id(c): c for c in CARD_DB.values()}
    saved = random.getstate()
    sim = copy.deepcopy(state, memo)
    _TL_FORCED, _TL_BUSY = land, True
    try:
        play_land(sim)
        _tl_develop(sim, None)
    finally:
        _TL_FORCED, _TL_BUSY = None, False
        random.setstate(saved)
    return sim.mana_spent_this_turn


def tapped_first_pick(state, lands_in_hand: list) -> str:
    """`lands_in_hand` ja' vem ordenada pelo criterio do proprio deck: a 1a e' o padrao (comportamento antigo)."""
    if _TL_FORCED is not None and _TL_FORCED in lands_in_hand:
        return _TL_FORCED
    default = lands_in_hand[0]
    if not TAPPED_LAND_FIRST_ENABLED or _TL_BUSY or state.turn > TAPPED_LAND_FIRST_MAX_TURN:
        return default
    tapped = [n for n in lands_in_hand if _tl_is_tapped(state, n)]
    untapped = [n for n in lands_in_hand if not _tl_is_tapped(state, n)]
    if not tapped or not untapped:
        return default
    dry = _tl_dry_run_mana if TAPPED_FIRST_COUNTS_MANA else _tl_dry_run_mv
    mv_virado, mv_desvirado = dry(state, tapped[0]), dry(state, untapped[0])
    if TAPPED_LAND_FIRST_GHOST:
        return default
    if mv_virado >= mv_desvirado:
        state.tapped_land_first_plays_total += 1
        return tapped[0]
    state.tapped_land_skipped_for_play_total += 1
    return untapped[0]


_FM_FORCED_PAY = None   # durante o ensaio a seco do Fell Mire: True/False impoe a decisao de pagar os 3 de vida


def _fm_dry_run_mv(state, pay: bool) -> int:
    """Ensaio a seco da decisao de pagar (ou nao) os 3 de vida do Fell Mire: roda o resto da fase pre-combate numa copia profunda e devolve o MANA GASTO no turno
    (`mana_spent_this_turn`). Nao e' o MV que sai da mao, como em `_tl_dry_run_mv`: o comandante vem da zona de comando (nao esta na mao), e conjura-lo no T2 e' justamente o que
    um terreno desvirado compra."""
    global _FM_FORCED_PAY, _TL_BUSY
    memo = {id(c): c for c in CARD_DB.values()}
    saved = random.getstate()
    sim = copy.deepcopy(state, memo)
    _FM_FORCED_PAY, _TL_BUSY = pay, True
    try:
        play_land(sim)
        _tl_develop(sim, None)
    finally:
        _FM_FORCED_PAY, _TL_BUSY = None, False
        random.setstate(saved)
    return sim.mana_spent_this_turn


def play_fell_mire(state: GameState):
    """Joga a MDFC pela face de terreno. Paga os 3 de vida so' quando (a) a vida depois de pagar fica >= FELL_MIRE_LIFE_FLOOR e (b) o ensaio a seco mostra que entrar desvirado
    gasta MAIS mana neste turno do que entrar virado (empate: nao paga)."""
    pay = _FM_FORCED_PAY
    if pay is None:
        pay = False
        if not _TL_BUSY and state.life - 3 >= FELL_MIRE_LIFE_FLOOR:
            pay = _fm_dry_run_mv(state, True) > _fm_dry_run_mv(state, False)
            if FELL_MIRE_GHOST:
                pay = False
    state.hand.remove(FELL_CARD)
    state.battlefield.append("Fell Mire")
    state.lands_played_this_turn += 1
    state.lands_played_total += 1
    state.fell_mire_land_plays_total += 1
    if pay:
        state.life -= 3
        state.fell_mire_paid_total += 1
    else:
        state.tapped_lands_this_turn.add("Fell Mire")
        state.fell_mire_tapped_total += 1


def play_land(state: GameState):
    if state.lands_played_this_turn >= 1:
        return
    lands_in_hand = [n for n in state.hand if n in LAND_NAMES]
    if not lands_in_hand:
        if (FELL_MIRE_LAND_ENABLED and FELL_CARD in state.hand
                and sum(1 for n in state.battlefield if n in LAND_NAMES) < FELL_MIRE_MAX_LANDS_IN_PLAY):
            play_fell_mire(state)
        return
    priority = ["Urborg, Tomb of Yawgmoth", "Cabal Coffers", "Nykthos, Shrine to Nyx",
                "Castle Locthwain", "Swamp"]
    ordered = sorted(lands_in_hand, key=lambda n: priority.index(n) if n in priority else len(priority))   # estavel: o 1o e' o mesmo `next(...)` de antes
    choice = tapped_first_pick(state, ordered)
    state.hand.remove(choice)
    state.battlefield.append(choice)
    state.lands_played_this_turn += 1
    state.lands_played_total += 1
    if "etb_tapped" in CARD_DB[choice].tags:
        state.tapped_lands_this_turn.add(choice)
    elif choice == "Castle Locthwain" and "Swamp" not in state.battlefield and not urborg_in_play(state):
        state.tapped_lands_this_turn.add(choice)
        state.tokens_created_total += 1


def upkeep_step(state: GameState):
    if "Ratcatcher" in state.battlefield and state.library:
        rats = [n for n in state.library if is_rat(n)]
        if rats:
            best = max(rats, key=lambda n: CARD_DB[n].mv)
            state.library.remove(best)
            state.hand.append(best)
            state.tutors_used_total += 1
    soul_stone_upkeep_reanimate(state)


def end_step(state: GameState):
    if "Rat King, Verminister" in state.battlefield and state.permanent_left_battlefield_this_turn:
        create_rat_token(state, source="Rat King (Disappear)")
        state.rat_king_counters += 1
    if "Emeritus of Woe // Demonic Tutor" in state.battlefield and state.creatures_died_this_turn >= 2:
        state.emeritus_prepared = True
    ashcoat_end_step(state)


# ---------------------------------------------------------------------------
# Mulligan / turno / batch
# ---------------------------------------------------------------------------

def should_keep(hand: list) -> bool:
    lands = sum(1 for n in hand if n in LAND_NAMES)
    if FELL_MIRE_COUNTS_FOR_KEEP and FELL_CARD in hand:
        lands += 1          # MDFC jogavel como terreno (Fell Mire)
    good_early = {"Sol Ring", COMMANDER, "Dark Ritual", "Rat Colony"}
    if lands >= 3:
        return True
    if lands == 2 and any(n in good_early for n in hand):
        return True
    return False


def build_library(names_override=None):
    if names_override is not None:
        for n in names_override:
            assert n in CARD_DB, f"faltando no CARD_DB: {n}"
        return list(names_override)
    lib = []
    text = open("lista.md").read()
    text = text.split("## Comandante")[1]
    text = text.split("## Links")[0] if "## Links" in text else text
    for l in text.split("\n"):
        l = l.strip()
        m = re.match(r"^(\d+)\s+(.+)$", l)
        if not m:
            continue
        qty, name = int(m.group(1)), m.group(2).strip()
        if name == COMMANDER:
            continue  # comandante fica de fora da biblioteca de goldfish
        assert name in CARD_DB, f"faltando no CARD_DB: {name}"
        for _ in range(qty):
            lib.append(name)
    # lista.md tem 100 cartas: o comandante (fora da biblioteca) + 99 de
    # biblioteca (100a carta = Damnation, 2026-08-31; auditoria.md secao 14).
    assert len(lib) == 99, f"esperado 99 (lista completa desde 2026-08-31, Damnation adicionado), achou {len(lib)}"
    return lib


BASE_LIBRARY = build_library()


# Correcao de 2026-10-05 (varredura das classes de erro das rodadas do Vihaan/Megatron nos outros decks): o London Mulligan deste arquivo SORTEAVA as cartas do fundo
# (`rng.shuffle(hand)`), devolvendo com a mesma chance uma carta-chave e um terreno sobrando. Com a chave em False o arquivo se comporta bit-a-bit como antes.
MULLIGAN_SMART_BOTTOM_ENABLED = True   # o jogador ESCOLHE as cartas do fundo (mesma regra do Vihaan/Megatron)
MULLIGAN_PROTECTED = frozenset({"Sol Ring", COMMANDER, "Dark Ritual", "Rat Colony"})   # as cartas que `should_keep` ja' trata como "boa abertura": nao sao devolvidas se houver outra


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
    base = library if library is not None else BASE_LIBRARY
    mulls = 0
    hand, lib = [], []
    while mulls < max_mulls:
        lib = base[:]
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


UPKEEP_BEFORE_DRAW_ENABLED = True   # CR 502-504: upkeep antes do draw step (antes: comprava e so' depois rodava o upkeep)


def play_turn(state: GameState, is_first_turn: bool, on_play: bool):
    state.turn += 1
    state.lands_played_this_turn = 0
    state.mana_spent_this_turn = 0
    state.tapped_lands_this_turn = set()
    state.tapped_creatures_this_turn = set()
    state.permanent_left_battlefield_this_turn = False
    state.creatures_died_this_turn = 0
    state.treasures_spent_this_turn = 0
    state.rat_tokens_created_this_turn = 0
    state.wipes_held_this_turn = set()
    state.soul_stone_tapped = False
    state.staff_tapped = False

    # Achado real 2026-09-18: "skip the draw step" no 1o turno de quem
    # comeca so' existe na regra 1x1 (CR 103.8a). Commander e' sempre
    # multiplayer -- sempre compra, mesmo no T1.
    # Correcao de 2026-10-05 (Regra #6, ordem das fases): o upkeep vem ANTES do draw step (CR 502-504). O codigo comprava primeiro e depois rodava o upkeep, entao o
    # tutor do Ratcatcher ("at the beginning of your upkeep, search for a Rat") buscava com a carta do topo ja' fora da biblioteca.
    if UPKEEP_BEFORE_DRAW_ENABLED:
        upkeep_step(state)
    if state.library:
        state.hand.append(state.library.pop(0))
    else:
        state.library_emptied = True

    if not UPKEEP_BEFORE_DRAW_ENABLED:
        upkeep_step(state)
    play_land(state)
    main_phase(state, is_first_main=True)
    combat_step(state)
    main_phase(state, is_first_main=False)
    end_step(state)


def simulate_one(seed: int, turns: int = 8, library=None):
    rng = random.Random(seed)
    hand, lib, mulls = mulligan(rng, library=library)
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
    print(f"Turno medio de conjuracao do Rat King: {avg(cmd_turn):.2f} | mediana: {statistics.median(cmd_turn) if cmd_turn else float('nan'):.1f}")
    print(f"Nunca conjurado em {turns} turnos: {100*sum(1 for s in states if s.commander_cast_turn is None)/n:.1f}%")
    print(f"Avg Rats totais em campo (final): {avg([rat_count(s) for s in states]):.2f}")
    print(f"Avg tokens criados: {avg([s.tokens_created_total for s in states]):.2f}")
    print(f"Avg reanimacoes via Rat King (sac 3 Rats): {avg([s.rat_king_reanimations_total for s in states]):.2f}")
    print(f"Avg casts gratis via Thrumming Stone (ripple 4): {avg([s.thrumming_stone_free_casts_total for s in states]):.2f}")
    print(f"Avg compras via Skullclamp: {avg([s.skullclamp_draws_total for s in states]):.2f}")
    print(f"Avg nivel final do Ninja Teen: {avg([s.ninja_teen_level for s in states]):.2f}")
    print(f"Soul Stone harnessed: {100*sum(1 for s in states if s.soul_stone_harnessed)/n:.1f}% dos jogos")
    print(f"Avg tutores usados: {avg([s.tutors_used_total for s in states]):.2f}")
    print(f"Avg vida final: {avg([s.life for s in states]):.2f}")
    print(f"Avg mao final: {avg([len(s.hand) for s in states]):.2f}")

    print("--- Metricas basicas (checklist obrigatorio) ---")
    print(f"RAMP: avg pecas de rampa conjuradas (Sol Ring/Soul Stone, Cabal Coffers/Urborg/Nykthos/Crypt Ghast/"
          f"Castle Locthwain/Crypt of Agadeem entrando em campo, Dark Ritual/Culling the Weak): {avg([s.ramp_pieces_cast_total for s in states]):.2f}")
    print(f"DRAW: avg compras extras totais (Skullclamp, Deadly Dispute, Priest of Forgotten Gods, Ayara, "
          f"Black Market Connections, Castle Locthwain, Ripples of Undeath): {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"INTERACTION: avg spells de interacao conjurados (Deadly Rollick, Withering Torment, Kindred "
          f"Dominance, Swarmyard Massacre, Fell the Profane, Damnation): {avg([s.interaction_spells_cast_total for s in states]):.2f}")
    print(f"RECURSION: avg eventos de recursao (Reanimate, Echoing Return, Secret Salvage, Rat King sac-3-Rats, "
          f"Soul Stone harnessed, Ashcoat mill+return, Ninja Teen nivel 3 sneak, Takenuma Channel): {avg([s.recursion_events_total for s in states]):.2f}")
    print(f"FINISHER/LETHALITY: avg dano/dreno proxy total acumulado (Zulaport, Ayara, Bontu's Monument, "
          f"Priest of Forgotten Gods, Valley Rotcaller, Syr Konrad -- SEM vida real de oponente, goldfish solo): "
          f"{avg([s.proxy_damage_total for s in states]):.2f}")
    return states


# ---------------------------------------------------------------------------
# Modo de resiliencia (interacao de oponente) -- 2026-09-21
# ---------------------------------------------------------------------------
# Porte do protocolo ja' validado em Megatron/Ur-Dragon/Hei Bai/Edgar Markov/
# Ulalek/Toph/Prismatic Bridge/Maralen (nesta ordem, mesma sessao). Camada
# 100% ADITIVA/OPCIONAL: `simulate_one`/`run_batch` continuam bit-identicos
# porque `state.interaction_rng` fica `None` em modo padrao e toda funcao
# `try_smart_opponent_*` abaixo checa isso primeiro.
#
# Achado real ESPECIFICO deste deck (aristocrats): um wipe de CRIATURA que
# destroi meu proprio board tambem dispara os gatilhos de morte reais do
# deck (Zulaport Cutthroat, Pitiless Plunderer, Syr Konrad, Species
# Specialist) -- diferente de decks sem payoff de morte, aqui um wrath
# sofrido NAO e' so' perda pura, tem um bonus real de drain/treasure/draw
# embutido. `try_smart_opponent_wipe` chama `on_creature_dies` pra CADA
# criatura destruida (nomeada via `remove_permanent`, ou token via contador
# agregado) -- exceto o proprio comandante, que nunca "morre" de verdade
# (CR 903.9 manda pra zona de comando, CR 700.4 exige ir pro cemiterio pra
# contar como "dies"; ver docstring de `remove_permanent`). Rat/Esquilo/
# Mercenary token nao vivem como entrada nomeada em `state.battlefield` --
# sao contadores agregados (`rat_tokens`/`squirrel_tokens`/
# `mercenary_tokens`/`treasure_tokens`), entao o wipe zera esses contadores
# TAMBEM quando o tipo escolhido e' "creature" (token de criatura) ou
# "artifact" (Treasure token).

NUM_OPPONENTS = 3  # premissa declarada (mesa de 4), mesma convencao dos outros 8 decks

INTERACTION_SETUP_TURNS = 2
# Turnos 1-2 sao sempre setup, sem chance de reacao nenhuma -- o
# oponente ainda nao tem motivo/mana pra reagir.


def interaction_chance(state: GameState) -> float:
    """Formula compartilhada de 'chance do oponente reagir esse turno' --
    identica aos outros 8 decks: escala com o impacto do meu proprio
    board (permanentes nao-terreno em campo). Tokens agregados (rat/
    squirrel/mercenary/treasure) somam ao impacto tambem -- sao
    permanentes reais na mesa, so' nao tem entrada nomeada em
    `state.battlefield`."""
    board_impact = (sum(1 for n in state.battlefield if n not in LAND_NAMES)
                     + state.rat_tokens + state.squirrel_tokens
                     + state.mercenary_tokens + state.treasure_tokens)
    return min(0.10 + 0.03 * board_impact, 0.75)


OPPONENT_ATTENTION_CHANCE = 1.0 / NUM_OPPONENTS
# Gate de "esse oponente esta' de olho em mim esse turno" (achado real
# do usuario nos outros 8 decks, 2026-09-20: "se sempre for 3 contra 1,
# ai' nao consigo fazer nada, nunca!") -- chance BASE de que um turno de
# oponente qualquer seja sobre MIM, antes de qualquer ajuste por ameaca
# de board (que ja' fica dentro de `interaction_chance()`). Rolado 1x no
# INICIO de `try_smart_opponent_turn`, antes de qualquer categoria.

POST_WIPE_ATTACK_HASTE_FACTOR = 0.15
# Board wipe e' SIMETRICO -- acerta TODA criatura da mesa, nao so' as
# minhas. Se um wipe ja' aconteceu NESTA RODADA (`state.wiped_this_
# round`), TODOS os turnos de oponente restantes na mesma rodada tambem
# ficam sem criaturas de verdade pra atacar -- exceto por haste (Regra
# #1 do CLAUDE.md: so' impossibilidade estrutural justifica nao
# modelar, nunca zerar por completo).

BOARD_WIPE_CHANCE_FACTOR = 0.4
ARTIFACT_WIPE_CHANCE_FACTOR = 0.2
ENCHANTMENT_WIPE_CHANCE_FACTOR = 0.15
GRAVEYARD_WIPE_CHANCE_FACTOR = 0.4
GRAVEYARD_SNIPE_CHANCE_FACTOR = 0.5
COUNTERSPELL_CHANCE_FACTOR = 0.5
# Pesos relativos de cada TIPO de sweeper (criatura/artefato/
# encantamento) -- design final ja' corrigido nos outros 8 decks
# (achado real do usuario 2026-09-20: rolagens INDEPENDENTES permitiam
# 2 sweepers no mesmo turno de oponente, irreal, e tratavam os 3 tipos
# como igualmente provaveis quando wipe de criatura e' muito mais comum
# numa lista real). `try_smart_opponent_wipe` rola 1x se ALGUM wipe
# acontece (soma dos 3 pesos) e SO' DEPOIS escolhe 1 TIPO, ponderado.
WIPE_TYPE_WEIGHTS = {
    "creature": BOARD_WIPE_CHANCE_FACTOR,
    "artifact": ARTIFACT_WIPE_CHANCE_FACTOR,
    "enchantment": ENCHANTMENT_WIPE_CHANCE_FACTOR,
}
TOTAL_WIPE_CHANCE_FACTOR = sum(WIPE_TYPE_WEIGHTS.values())

INTERACTION_ENGINE_PRIORITY = [
    "Skullclamp",
    "Thrumming Stone",
    "Ayara, First of Locthwain",
    "Cabal Coffers",
    "Crypt Ghast",
    "Priest of Forgotten Gods",
    "Marrow-Gnawer",
    "Pitiless Plunderer",
    "Zulaport Cutthroat",
    "Syr Konrad, the Grim",
]
# Lista curada por prioridade (a mais critica primeiro) -- so' cartas
# que sao motor RECORRENTE de valor (draw/mana/drain/token repetivel),
# nao corpos grandes isolados. O proprio Rat King fica DE FORA de
# proposito -- ja' tem categoria dedicada (`try_smart_opponent_counter`,
# mira o CAST dele especificamente) e remocao nao o mata de verdade
# mesmo (vai pra zona de comando via `remove_permanent`), entao um
# oponente esperto prefere gastar a remocao pontual numa peca
# irrecuperavel.

OPPONENT_ATTACKER_PROFILES = [
    ("Knight Token", 2), ("Saproling Token", 1), ("Vampire Token", 1),
    ("Zombie Token", 2), ("Soldier Token", 1), ("Goblin Token", 1),
    ("Elemental Token", 3),
]
# Mesmos perfis genericos ja' validados nos outros 8 decks -- sem
# toughness, este arquivo nao modela combate/bloqueio real. Todo ataque
# conecta.


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
    """Discard aleatorio -- mesma logica dos outros 8 decks (alvo
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


def _wipe_remove_creature_no_trigger(state: GameState, name: str):
    """Remove fisicamente uma criatura NOMEADA do campo sem disparar
    `on_creature_dies` individualmente -- usado SO' por `try_smart_
    opponent_wipe`, que calcula os 4 gatilhos reais de aristocrata
    (Zulaport/Pitiless Plunderer/Syr Konrad/Species Specialist) a partir
    de um snapshot ÚNICO de ANTES do wipe comecar (ver comentario de
    `try_smart_opponent_wipe` abaixo pro motivo -- mortes simultaneas
    exigem 'last known information', CR 603.10, nao o caminho normal
    remove-um-por-vez de `remove_permanent`).

    CORRIGIDO 2026-09-21 (achado real do usuario, CR 903.9a -- ver
    `rules-cache/comprehensive-rules.txt` linhas 6888-6896, Regra 18 de
    `references/user-standing-rules.md`): comandante indo pro
    cemiterio/exilio NAO e' substituicao, e' ACAO BASEADA EM ESTADO (CR
    704) que roda DEPOIS do evento real -- ela vai pro cemiterio DE
    VERDADE primeiro (CR 700.4, "dies"), so' DEPOIS o dono PODE
    escolher move-la pra zona de comando. A versao anterior pulava o
    cemiterio inteiramente E excluia ela dos 4 payoffs de aristocrata em
    `try_smart_opponent_wipe` (corrigido la' tambem, ver docstring
    daquela funcao) -- achado real NUMERICO: Rat King e' Rato de
    verdade (tag "rat" no CARD_DB), entao Species Specialist deveria
    contar a morte dela, e Zulaport/Pitiless Plunderer/Syr Konrad
    tambem (nenhum dos 3 e' ela mesma). Resto vai pro cemiterio
    normalmente, como antes."""
    if name not in state.battlefield:
        return
    state.battlefield.remove(name)
    if name == COMMANDER:
        state.graveyard.append(name)
        if name in state.graveyard:
            state.graveyard.remove(name)
        state.commander_in_play = False
        return
    state.graveyard.append(name)


def try_smart_opponent_wipe(state: GameState) -> Optional[list]:
    """Board wipe ('destroy all creatures'/'destroy all artifacts'/
    'destroy all enchantments') -- destroi TODOS os meus permanentes do
    tipo escolhido de uma vez. O Rat King nunca e' artefato/encantamento
    (Legendary Creature -- Rat Avatar, confirmado via Scryfall), entao
    nunca e' alvo dos 2 tipos novos.

    Design de 2 passos (nao 3 rolagens independentes -- ver comentario
    de `WIPE_TYPE_WEIGHTS` acima): 1) rola 1x se ALGUM wipe acontece
    esse turno de oponente, chance = `interaction_chance() *
    TOTAL_WIPE_CHANCE_FACTOR`; 2) SO' se isso disparar, escolhe qual
    TIPO de sweeper via escolha ponderada (`state.interaction_rng.
    choices`) restrita aos tipos que tem pelo menos 1 alvo legal em
    campo (incluindo tokens agregados).

    Achado real de regra (aristocrats, CR 603.10 "last known
    information"): TODAS as mortes de um wipe sao SIMULTANEAS -- cada
    fonte de gatilho de morte (Zulaport/Pitiless Plunderer/Syr Konrad)
    precisa ver o board de ANTES do wipe comecar, mesmo se ela propria
    estiver entre as mortas, e mesmo se outra fonte tambem morrer no
    mesmo wipe. O caminho generico (`remove_permanent`->`leave_
    battlefield`->`on_creature_dies`, checando `state.battlefield` AO
    VIVO num loop sequencial) SUBCONTA nesse cenario especifico -- uma
    fonte ja removida no meio do loop nao dispara mais pras mortes que
    vem depois dela no MESMO wipe, mesmo sendo tecnicamente
    simultaneas (bug generico pre-existente em `on_creature_dies`, fora
    de escopo consertar aqui porque e' compartilhado com varios call
    sites de modo PADRAO -- ver checklist-oraculo.md). Corrigido SO'
    dentro desta funcao (sem tocar `on_creature_dies`/`leave_
    battlefield` compartilhados, preservando bit-identidade do modo
    padrao): tira um SNAPSHOT de quem esta' em campo ANTES de remover
    qualquer coisa, calcula os 4 payoffs manualmente a partir dele --
    Zulaport ('this creature or another creature', SELF-inclusiva,
    conta ate' a propria morte dela), Pitiless Plunderer/Syr Konrad
    ('another creature', excluem a propria morte de cada um -- 1 a
    menos SO' se a propria fonte estiver entre as mortas), Species
    Specialist (conta so' Ratos, tipo escolhido, nunca ela mesma que
    e' Human).

    Wipe de ARTEFATO/ENCANTAMENTO nao precisa dessa correcao -- nenhuma
    carta desta lista reage a artefato/encantamento saindo de campo, o
    caminho generico via `remove_permanent` continua correto.

    CORRIGIDO 2026-09-21 (achado real do usuario, CR 903.9a -- ver
    `rules-cache/comprehensive-rules.txt` linhas 6888-6896, Regra 18 de
    `references/user-standing-rules.md`): o comandante AGORA conta pros
    4 payoffs. 903.9a (cemiterio/exilio, o caso de MORTE) e' ACAO
    BASEADA EM ESTADO (CR 704), NAO substituicao -- o Rat King vai pro
    cemiterio DE VERDADE primeiro (CR 700.4, "dies"), disparando
    Zulaport/Pitiless Plunderer/Syr Konrad/Species Specialist
    normalmente (nenhum dos 4 e' ela mesma), so' DEPOIS o dono PODE
    escolher move-lo pra zona de comando. Achado real NUMERICO: o Rat
    King tem a tag "rat" (Legendary Creature -- Rat Noble, confirmado
    Scryfall), entao Species Specialist tambem deveria contar -- a
    versao anterior excluia ele de TODOS os 4, nao so' de Species
    Specialist. Ainda conta pra `permanent_left_battlefield_this_turn`
    (Disappear usa 'left the battlefield', termo mais amplo que
    'dies'), como antes. Sem nenhum alvo legal de tipo nenhum, retorna
    None sem fazer nada."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * TOTAL_WIPE_CHANCE_FACTOR:
        return None
    has_creature_tokens = (state.rat_tokens + state.squirrel_tokens + state.mercenary_tokens) > 0
    has_artifact_tokens = state.treasure_tokens > 0
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

    if wipe_type == "creature":
        # Snapshot ANTES de remover qualquer coisa (LKI real, ver docstring
        # acima). CORRIGIDO 2026-09-21 (CR 903.9a): o comandante CONTA pros
        # 4 payoffs de aristocrata agora -- ele morre de verdade primeiro
        # (CR 700.4/704), so' depois vai pra zona de comando por escolha do
        # dono. `named_dying_real_deaths` nao exclui mais o comandante.
        named_dying = targets[:]
        named_dying_real_deaths = named_dying[:]
        rat_like_tokens_dying = state.rat_tokens + state.mercenary_tokens
        squirrel_tokens_dying = state.squirrel_tokens
        total_dying = len(named_dying_real_deaths) + rat_like_tokens_dying + squirrel_tokens_dying
        total_rat_dying = sum(1 for n in named_dying_real_deaths if is_rat(n)) + rat_like_tokens_dying
        zulaport_present = "Zulaport Cutthroat" in state.battlefield
        plunderer_present = "Pitiless Plunderer" in state.battlefield
        konrad_present = "Syr Konrad, the Grim" in state.battlefield
        species_present = "Species Specialist" in state.battlefield

        for n in named_dying:
            _wipe_remove_creature_no_trigger(state, n)
        state.rat_tokens = 0
        state.squirrel_tokens = 0
        state.mercenary_tokens = 0

        log_targets = named_dying[:]
        if named_dying or rat_like_tokens_dying or squirrel_tokens_dying:
            # Disappear usa "left the battlefield" (mais amplo que "dies") --
            # dispara mesmo se so' o comandante saiu, ver docstring.
            state.permanent_left_battlefield_this_turn = True
            if rat_like_tokens_dying or squirrel_tokens_dying:
                log_targets = named_dying + [f"{rat_like_tokens_dying + squirrel_tokens_dying} token(s)"]
        if total_dying:
            state.creatures_died_this_turn += total_dying
        if zulaport_present and total_dying:
            state.life += total_dying
            state.proxy_damage_total += total_dying
        if NINJA_TEEN_LEVELS_AND_DRAIN and total_dying and "Ninja Teen" in state.battlefield:
            state.proxy_damage_total += total_dying      # nivel 1: cada criatura que sai do campo (aqui, num wipe simultaneo) drena 1
            state.ninja_teen_drain_total += total_dying
        if plunderer_present:
            other_dying = total_dying - (1 if "Pitiless Plunderer" in named_dying_real_deaths else 0)
            if other_dying:
                state.treasure_tokens += other_dying
                state.tokens_created_total += other_dying
        if konrad_present:
            other_dying = total_dying - (1 if "Syr Konrad, the Grim" in named_dying_real_deaths else 0)
            if other_dying:
                state.proxy_damage_total += other_dying
        if species_present and total_rat_dying:
            draw_cards(state, total_rat_dying)

        state.smart_wipes_total += 1
        state.smart_wipe_log.append((state.turn, log_targets))
        state.wiped_this_round = True
        return log_targets

    for n in targets:
        remove_permanent(state, n, source=f"opponent_{wipe_type}_wipe")
    log_targets = targets[:]
    if wipe_type == "artifact":
        state.smart_artifact_wipes_total += 1
        if state.treasure_tokens:
            state.permanent_left_battlefield_this_turn = True
            log_targets = targets + [f"{state.treasure_tokens} treasure token(s)"]
        state.treasure_tokens = 0
        state.smart_artifact_wipe_log.append((state.turn, log_targets))
    else:
        state.smart_enchantment_wipes_total += 1
        state.smart_enchantment_wipe_log.append((state.turn, log_targets))
    return log_targets


def try_smart_opponent_graveyard_wipe(state: GameState) -> Optional[list]:
    """Graveyard hate, modelo MASS EXILE (Bojuka Bog/Soul-Guide
    Lantern-style) -- dispara NO MAXIMO 1x por partida inteira
    (`state.graveyard_wipe_used`). Achado real deste deck: exilar o
    cemiterio tambem dispara `konrad_gy_left` pra cada carta de
    criatura exilada (Syr Konrad, clausula 3, "or a creature card
    leaves your graveyard")."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if state.graveyard_wipe_used or not state.graveyard:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * GRAVEYARD_WIPE_CHANCE_FACTOR:
        return None
    exiled = state.graveyard[:]
    creature_count_exiled = sum(1 for c in exiled if is_creature_card(c))
    state.graveyard.clear()
    state.graveyard_wipe_used = True
    konrad_gy_left(state, creature_count_exiled)
    state.smart_graveyard_wipes_total += 1
    state.smart_graveyard_wipe_log.append((state.turn, exiled))
    return exiled


def try_smart_opponent_graveyard_snipe(state: GameState) -> Optional[str]:
    """Graveyard hate, modelo EXILIO DE CARTA UNICA (Scavenging
    Ooze/Cease-style) -- repetivel todo turno. Alvo SMART: maior MV
    entre criatura no cemiterio -- mesmo criterio que `best_missing_
    creature`/recursao real do deck ja' usam pra escolher alvo (o
    oponente esperto sniparia igual). Dispara `konrad_gy_left` (clausula
    3 do Syr Konrad) igual a qualquer outra saida de criatura do
    cemiterio."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    candidates = [c for c in state.graveyard if is_creature_card(c)]
    if not candidates:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * GRAVEYARD_SNIPE_CHANCE_FACTOR:
        return None
    target = max(candidates, key=lambda n: CARD_DB[n].mv)
    state.graveyard.remove(target)
    konrad_gy_left(state, 1)
    state.smart_graveyard_snipes_total += 1
    state.smart_graveyard_snipe_log.append((state.turn, target))
    return target


def try_smart_opponent_counter(state: GameState) -> bool:
    """Counterspell -- so' mira a conjuracao do proprio Rat King (mesma
    logica dos outros 8 decks: o motor inteiro do deck depende do
    comandante resolver). Chamada de dentro de `main_phase()`, nao do
    loop de `simulate_one_with_interaction` -- so' faz sentido no exato
    momento do cast, dentro do MEU turno."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return False
    if state.interaction_rng.random() >= interaction_chance(state) * COUNTERSPELL_CHANCE_FACTOR:
        return False
    state.smart_counters_total += 1
    state.smart_counter_log.append(state.turn)
    return True


def try_smart_opponent_turn(state: GameState):
    """Simula O TURNO DE UM oponente dentro da rodada entre os meus
    turnos (mesmo design final ja' validado nos outros 8 decks, Regra
    #6 do CLAUDE.md: bug de orquestracao de turno que auditoria
    carta-a-carta nao pega). Chamada `NUM_OPPONENTS` vezes por rodada --
    um wipe de um oponente ANTERIOR na rodada continua afetando
    corretamente o ataque de um oponente POSTERIOR na MESMA rodada
    (chamadas em sequencia, mesmo `state`).

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


def simulate_one_with_interaction(seed: int, turns: int = 8) -> GameState:
    """Mesmo goldfish de `simulate_one`, mas com `NUM_OPPONENTS` turnos
    de oponente de verdade simulados (`try_smart_opponent_turn`) a cada
    rodada entre os meus turnos. Counterspell (7a categoria) NAO mora
    neste loop -- ver `try_smart_opponent_counter`, chamada de dentro de
    `main_phase` no exato momento do cast do comandante.

    NUNCA chamado por `run_batch`/`simulate_one` padrao (nem o loop
    aqui, nem o counter dentro de `main_phase` -- ambos ficam inertes
    sem `interaction_rng`). Retorna o `GameState` bruto (nao um
    resumo), mesma convencao dos outros 8 decks."""
    rng = random.Random(seed)
    hand, lib, mulls = mulligan(rng)
    state = GameState(hand=hand, library=lib, mulligans=mulls,
                       interaction_rng=random.Random(seed + 999_999))
    for t in range(turns):
        play_turn(state, is_first_turn=(t == 0), on_play=True)
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

    print(f"n={n}, seed_base={seed_base}, turns={turns} (MODO RESILIENCIA)")
    print(f"Avg counterspells sofridos (so' mira a conjuracao do Rat King): "
          f"{avg([s.smart_counters_total for s in states]):.2f}")
    rk_cast = [s.commander_cast_turn for s in states if s.commander_cast_turn is not None]
    print(f"  -- Turno medio de conjuracao do Rat King QUE RESOLVEU: "
          f"{avg(rk_cast):.2f} | nunca resolveu em {turns} turnos: "
          f"{100*(n-len(rk_cast))/n:.1f}%")
    print(f"Avg board wipes sofridos: {avg([s.smart_wipes_total for s in states]):.2f}")
    print(f"Avg artifact wipes sofridos: {avg([s.smart_artifact_wipes_total for s in states]):.2f}")
    print(f"Avg enchantment wipes sofridos: {avg([s.smart_enchantment_wipes_total for s in states]):.2f}")
    gy_wiped = sum(1 for s in states if s.smart_graveyard_wipes_total > 0)
    print(f"Partidas com graveyard wipe sofrido (no maximo 1x/partida): {100*gy_wiped/n:.1f}%")
    print(f"Avg graveyard snipes sofridos: {avg([s.smart_graveyard_snipes_total for s in states]):.2f}")
    print(f"Avg remocoes inteligentes sofridas: {avg([s.smart_removals_total for s in states]):.2f}")
    hit_counts = {}
    for s in states:
        for _, target in s.smart_removal_log:
            hit_counts[target] = hit_counts.get(target, 0) + 1
    for name in INTERACTION_ENGINE_PRIORITY:
        pct = 100 * hit_counts.get(name, 0) / n
        if pct > 0:
            print(f"  -- {name} removido em {pct:.1f}% dos jogos")
    print(f"Avg ataques de oponente sofridos: {avg([s.smart_attacks_taken_total for s in states]):.2f}")
    print(f"Avg descartes forcados sofridos: {avg([s.smart_discards_total for s in states]):.2f}")
    print(f"Avg proxy_damage_total (inclui bonus de morte real disparado pelos wipes sofridos): "
          f"{avg([s.proxy_damage_total for s in states]):.2f}")
    print(f"Avg vida final: {avg([s.life for s in states]):.2f}")
    return states


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    states = run_batch(n=3000, seed_base=9300000, turns=8)

    with open("ratking_v1_runs.jsonl", "w") as f:
        for s in states:
            f.write(json.dumps({
                "mulligans": s.mulligans,
                "commander_cast_turn": s.commander_cast_turn,
                "tokens_created_total": s.tokens_created_total,
                "rat_king_reanimations_total": s.rat_king_reanimations_total,
                "thrumming_stone_free_casts_total": s.thrumming_stone_free_casts_total,
                "skullclamp_draws_total": s.skullclamp_draws_total,
                "cards_drawn_extra": s.cards_drawn_extra,
                "proxy_damage_total": s.proxy_damage_total,
            }) + "\n")
