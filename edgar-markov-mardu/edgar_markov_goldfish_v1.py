"""
Goldfish simulator - Edgar Markov (Mardu - R/W/B, tribal Vampiro/aristocratas)
Escrito e executado por Claude.

Metodologia:
- Tags e CARD_DB derivados de oracle_text real (Scryfall,
  /tmp/scryfall_cache/edgar_markov_full.json), nao inventados.
- Passo 0 (regra de Roaming Throne, references/goldfish-sim-card-rules.md):
  varredura mecanica de oracle_text de toda criatura Vampiro (regex por
  "Whenever"/"At the beginning of"/"When") encontrou 16 vampiros com
  gatilho proprio (de 20 + o proprio Edgar). Implementados todos abaixo,
  cada um como mecanica real, nao so tag.
- Roaming Throne (tipo escolhido: Vampire) dobra CADA gatilho real desses
  16 vampiros + o gatilho de ataque/Eminence do proprio Edgar, seguindo a
  mesma regra ja aplicada no Thranduil/Beorn.
- NAO modelado / simplificacoes documentadas:
  - Combate real (bloqueadores, dano de combate contra criaturas do
    oponente). Assume-se que Edgar (e outros vampiros relevantes) ataca
    todo turno depois de perder o summoning sickness, sem resposta do
    oponente - goldfish solo.
  - Clavileno, First of the Blessed: efeito de escolher 1 vampiro
    atacante especifico pra virar Demon e ganhar gatilho de morte e
    modelado so como um contador de "disparou X vezes", sem efeito
    numerico adicional (a escolha de QUAL vampiro e um detalhe tatico
    que nao muda a metrica agregada que este simulador mede).
  - Perda de vida do oponente e ganho de vida proprio sao rastreados como
    CONTADORES agregados (drain_total, lifegain_total), nao como life
    totals reais de um oponente concreto - e um goldfish solo.
  - Ashnod's Altar/Phyrexian Altar: a mana que produzem exige sacrificar
    uma criatura (nao e {T}: Add livre) - NAO contam pro total_mana()
    automatico. So geram mana quando efetivamente usados no "loop de
    sacrificio" (ver sac_loop), consumindo 1 token disponivel por uso.
  - Loop de sacrificio: no maximo 2 sacrificios por turno (Ashnod's
    Altar/Phyrexian Altar/Viscera Seer/Goblin Bombardment, o que estiver
    em campo), limitado a tokens de Vampiro disponiveis (criados pela
    Eminence) - simplificacao deliberada pra nao superestimar o volume
    de gatilhos de morte por turno.
  - Combo Exquisite Blood/Bloodthirsty Conqueror + Vito, Thorn of the
    Dusk Rose: quando UM dos 2 habilitadores + Vito Thorn estao em
    campo, gain_life()/lose_life_opponent() detectam o loop e marcam
    combo_active (metrica: primeiro turno em que monta E tem um
    gatilho real pra ligar). Achado real 2026-08-27: Bloodthirsty
    Conqueror ("whenever an opponent loses life, you gain that much")
    forma o MESMO loop infinito com Vito Thorn que Exquisite Blood -
    so o segundo era detectado antes.

Revisao carta-a-carta completa - 2026-08-27 (usuario: "faca a carta por
carta do Markov", mesmo rigor ja aplicado no Ur-Dragon/Hei Bai):
conferido oracle_text de TODAS as 99 cartas + comandante contra o
codigo. Achados reais documentados em detalhe no goldfish-log.md
(Correcao #1) - resumo: Funeral Room/Unholy Annex tinham mv errado
(soma dos 2 lados do Room em vez do custo real de cada porta - ficavam
praticamente incastaveis); Purphoros, Warleader's Call, Skullclamp,
Ophiomancer, Pitiless Plunderer (tageado 'ramp' errado - nao tem
habilidade de mana propria), Anointed Procession/Mondrak (dobradores de
TOKEN, mecanica diferente do Roaming Throne que dobra o GATILHO),
Zulaport Cutthroat, e a propria Vito, Thorn of the Dusk Rose (so' usada
como string-match do combo, nunca com efeito proprio) estavam 100%
ausentes apesar de tageados/citados na auditoria.md. Corrigidos com
implementacao real, testados (25k+15k jogos de robustez, 0 erros) e
logados com impacto quantificado.

Deferido/documentado (nao implementado, motivo real por carta):
  - MDFCs land-primary (Ojer Taq, Legion's Landing, Agadeem's Awakening,
    Fell the Profane): so o verso Land e' jogado - o lado spell (Ojer
    Taq triplica token de criatura; Legion's Landing cria Vampiro;
    Agadeem's Awakening reanima em massa; Fell the Profane e' remocao,
    ja proxy) nunca e' conjurado. Westvale Abbey e' land-primary DE
    VERDADE (a maioria dos jogos so joga como terreno mesmo) - os
    outros 3 sao uma perda real de valor, mas modelar escolha dinamica
    entre face land/spell exigiria uma reforma arquitetural maior (nao
    so mais uma carta) - fora de escopo desta rodada, documentado aqui
    em vez de silencioso.
  - Cordial Vampire (+1/+1 counters em cada Vampiro) e o gatilho de
    MORTE da propria Elenda (X tokens = poder dela): sem payoff
    numerico modelavel - nenhuma criatura NOMEADA morre neste
    simulador (so tokens, decisao ja documentada acima), entao Elenda
    nunca teria chance real de morrer e os contadores de Cordial
    Vampire nunca teriam combate pra importar. O passivo de Elenda
    ("+1/+1 quando OUTRA criatura morre") em si E' rastreado agora
    (state.elenda_counters, so' por transparencia de dado).
  - Loyalty abilities de Elspeth Storm Slayer/Sorin, nivel 2/3 do
    Caretaker's Talent (a habilidade BASE do Class, que nao depende de
    nivel nenhum, ESTA implementada - achado real 2026-08-27, revisao
    da revisao: a Correcao #1 tinha lumped ela errado junto com o resto
    do Class deferido), ativada do Mondrak (indestructible counter),
    Cavern of Souls (escolha de tipo): nenhuma engine de "1 ativada por
    turno" existe neste simulador - mesma classe de simplificacao ja
    usada nos outros decks desta sessao pra
    planeswalkers/Classes.
  - Fetch lands (Arid Mesa/Bloodstained Mire/Marsh Flats): modeladas
    como duais estaticas de 2 cores (produces={cor1,cor2}), sem
    sacrificio/busca real - decisao consistente com o resto do
    simulador (nenhum land search existe aqui, diferente do Hei
    Bai/Ur-Dragon), sem efeito na CONTAGEM de mana (1 fetch = 1 land =
    1 mana, igual a already-fetched).

Auditoria do resto do deck - 2026-08-27 (usuario: "Audite o resto do
deck"): conferido oracle_text de TODAS as cartas ainda nao tocadas
diretamente pelo usuario nas rodadas anteriores. Achados reais
documentados em detalhe no goldfish-log.md (Correcao #6) - resumo:
removal/protecao (Anguished Unmaking, Get Lost, Path to Exile, Swords
to Plowshares, Vindicate, Rite of Oblivion, Call the Coppercoats,
Clever Concealment, Teferi's Protection) NUNCA era excluida do loop
generico de conjuracao, mesma classe de bug ja corrigida no Hei
Bai/Ur-Dragon mas nunca aplicada aqui - EXCLUDE_BLIND_CAST. Plumb the
Forbidden/Sevinne's Reclamation/Bloodline Bidding tinham 0% de efeito
(conjuradas as cegas). Bloodletter of Aclazotz (dobra TODO drain do
motor durante seu turno - e este simulador SO simula seus turnos, entao
e' um multiplicador universal) e Elspeth Storm Slayer (dobrador de
token, mesmo texto do Anointed Procession/Mondrak, nunca incluida na
tupla) estavam 100% ausentes. Smothering Tithe tinha a MESMA classe de
bug do Pitiless Plunderer (tag 'ramp' inventada - o unico gatilho real
dela exige o OPONENTE comprar carta, que nunca acontece neste
simulador so-do-proprio-turno). Bartolome del Presidio e Phyrexian
Tower sao sac outlets reais nunca incluidos em SAC_OUTLETS. Urza's Saga
(capitulo III - tutor de artefato <=1 mana) 100% ausente, tratada so
como terreno incolor fixo pro resto do jogo. Terrenos condicionalmente
tapados (Savai Triome sempre, Blackcleave Cliffs/Haunted Ridge
condicional a quantidade de OUTROS terrenos) nunca tinham NENHUM
rastreio de tapado neste simulador - novo tapped_lands_this_turn.

Deferido/documentado nesta rodada (nao implementado, motivo real):
  - Charismatic Conqueror: seu gatilho ("whenever an artifact or
    creature an OPPONENT controls enters untapped") nunca teria janela
    real pra disparar aqui - este simulador nao modela NENHUM
    permanente de oponente entrando, mesma classe de limitacao do
    Seedborn Muse/Smothering Tithe. Corpo 2/2 vigilance vanilla e' o
    resultado correto.
  - Nullpriest of Oblivion (kicker {3}{B}, reanima criatura da
    graveyard se kicked): baixo valor esperado pela mesma razao do
    Agadeem's Awakening/Sevinne's Reclamation - poucas criaturas
    NOMEADAS morrem neste simulador (so via custo do Diabolic Intent
    sem token disponivel), entao o pool de reanimacao geralmente esta
    vazio - nao vale pagar 6 mana por um efeito quase sempre nulo, o
    corpo base (2 mana, lifelink, menace) ja e' castado normalmente.
  - Voldaren Estate ({5},{T}: Blood token, custo reduzido por Vampiro)
    e Fountainport ({2}/{3}/{4} + tap: draw/token/Treasure): terrenos
    utilitarios com habilidades ativadas caras (mana ADICIONAL alem do
    proprio tap) - mesma classe de simplificacao ja aplicada a Mondrak
    (indestructible counter) e Westvale Abbey (sac 5 criaturas).
  - Urza's Saga capitulo II (Construct token, {2}+tap por ativacao):
    exigiria uma engine de "usar a terra pra isso EM VEZ de mana" que
    nao existe neste simulador - so o capitulo III (tutor, maior valor
    e mais simples de modelar corretamente) foi implementado.

Correcao #10 - checklist ampliada (2026-08-28, ver goldfish-log.md): 2
categorias novas na checklist obrigatoria (habilidades estaticas; metricas
basicas ramp/draw/interaction/finisher no relatorio). Achado real: Enduring
Tenacity tem o MESMO texto de Vito, Thorn of the Dusk Rose ("whenever you
gain life, target opponent loses that much life") - estava tageada
'drain_aristocrats' e tratada como death payoff (nao e', 100% ausente).
Corrigida junto com o anthem estatico do Warleader's Call (nunca aplicado a
nenhum calculo de poder) e um bloco novo de metricas basicas agregadas no
run_batch().
"""

import random
from dataclasses import dataclass, field
from typing import Set, List, Dict, Optional

COMMANDER = "Edgar Markov"

# Politica de "cacar o combo": False (default) = joga generico, so conjura
# Exquisite Blood/Vito Thorn/os tutores quando calham na mao no ritmo
# normal do resto do jogo. True = prioriza os 2 tutores rapidos (Vampiric
# Tutor, Diabolic Intent) especificamente pra buscar a peca do combo que
# ainda falta, e prioriza conjurar as pecas do combo assim que estao na
# mao, acima de qualquer outra jogada - pra medir o piso real (nao so o
# melhor caso teorico) de quando o combo monta se o jogador estiver
# mirando nisso de proposito. Pedido do usuario pra comprovar a
# classificacao de Bracket (criterio oficial e "antes do turno 6").
COMBO_HUNTING_POLICY = False
COMBO_PIECES = ("Exquisite Blood", "Vito, Thorn of the Dusk Rose")

DECKLIST_TEXT = """
1 Bartolomé del Presidio
1 Blood Artist
1 Bloodletter of Aclazotz
1 Bloodthirsty Conqueror
1 Champion of Dusk
1 Charismatic Conqueror
1 Clavileño, First of the Blessed
1 Cordial Vampire
1 Cruel Celebrant
1 Elenda, the Dusk Rose
1 Emeritus of Woe
1 Enduring Tenacity
1 Indulgent Aristocrat
1 Mondrak, Glory Dominus
1 Nullpriest of Oblivion
1 Ojer Taq, Deepest Foundation // Temple of Civilization
1 Ophiomancer
1 Pitiless Plunderer
1 Purphoros, God of the Forge
1 Roaming Throne
1 Sanctum Seeker
1 Stensian Sanguinist // Exsanguinate
1 Vein Ripper
1 Vindictive Vampire
1 Viscera Seer
1 Vito, Fanatic of Aclazotz
1 Vito, Thorn of the Dusk Rose
1 Welcoming Vampire
1 Zulaport Cutthroat
1 Arcane Signet
1 Ashnod's Altar
1 Phyrexian Altar
1 Skullclamp
1 Sol Ring
1 Anointed Procession
1 Bastion of Remembrance
1 Black Market Connections
1 Caretaker's Talent
1 Exquisite Blood
1 Funeral Room // Awakening Hall
1 Goblin Bombardment
1 Legion's Landing // Adanto, the First Fort
1 Smothering Tithe
1 The Meathook Massacre
1 Unholy Annex // Ritual Chamber
1 Warleader's Call
1 Elspeth, Storm Slayer
1 Sorin, Imperious Bloodlord
1 Anguished Unmaking
1 Call the Coppercoats
1 Clever Concealment
1 Fell the Profane // Fell Mire
1 Get Lost
1 Path to Exile
1 Plumb the Forbidden
1 Swords to Plowshares
1 Teferi's Protection
1 Vampiric Tutor
1 Agadeem's Awakening // Agadeem, the Undercrypt
1 Bloodline Bidding
1 Diabolic Intent
1 Rite of Oblivion
1 Sevinne's Reclamation
1 Vindicate
1 Arid Mesa
1 Battlefield Forge
1 Blackcleave Cliffs
1 Blazemire Verge
1 Blood Crypt
1 Bloodstained Mire
1 Cabal Coffers
1 Cavern of Souls
1 City of Brass
1 Command Tower
1 Fetid Heath
1 Fountainport
1 Godless Shrine
1 Haunted Ridge
1 Luxury Suite
1 Mana Confluence
1 Marsh Flats
1 Minas Tirith
4 Plains
1 Phyrexian Tower
1 Rugged Prairie
1 Savai Triome
1 Spectator Seating
4 Swamp
1 Takenuma, Abandoned Mire
1 Urborg, Tomb of Yawgmoth
1 Urza's Saga
1 Voldaren Estate
1 Westvale Abbey // Ormendahl, Profane Prince
"""

@dataclass
class Card:
    name: str
    mv: int
    type: str
    colors: Set[str] = field(default_factory=set)
    produces: Set[str] = field(default_factory=set)
    tags: Set[str] = field(default_factory=set)

CARD_DB: Dict[str, Card] = {}

def add(name, mv, type_, colors=None, produces=None, tags=None):
    CARD_DB[name] = Card(name=name, mv=mv, type=type_,
                          colors=set(colors or []), produces=set(produces or []),
                          tags=set(tags or []))

# -------- Comandante --------
add("Edgar Markov", 6, "Creature", colors={"B", "R", "W"}, tags={"vampire_type"})

# -------- Deck (99 cartas, geradas via Scryfall cards/collection) --------
add("Bartolomé del Presidio", 2, "Creature", colors={"B", "W"}, produces=set(), tags={"vampire_type"})
add("Blood Artist", 2, "Creature", colors={"B"}, produces=set(), tags={"drain_aristocrats", "vampire_type"})
add("Bloodletter of Aclazotz", 4, "Creature", colors={"B"}, produces=set(), tags={"vampire_type"})
add("Bloodthirsty Conqueror", 5, "Creature", colors={"B"}, produces=set(), tags={"vampire_type"})
add("Champion of Dusk", 5, "Creature", colors={"B"}, produces=set(), tags={"draw", "vampire_type"})
add("Charismatic Conqueror", 2, "Creature", colors={"W"}, produces=set(), tags={"token_maker", "vampire_type"})
add("Clavileño, First of the Blessed", 3, "Creature", colors={"B", "W"}, produces=set(), tags={"draw", "token_maker", "vampire_type"})
add("Cordial Vampire", 2, "Creature", colors={"B"}, produces=set(), tags={"vampire_type"})
add("Cruel Celebrant", 2, "Creature", colors={"B", "W"}, produces=set(), tags={"drain_aristocrats", "vampire_type"})
add("Elenda, the Dusk Rose", 4, "Creature", colors={"B", "W"}, produces=set(), tags={"token_maker", "vampire_type"})
add("Emeritus of Woe", 4, "Creature", colors={"B"}, produces=set(), tags={"tutor", "vampire_type"})
add("Enduring Tenacity", 4, "Creature", colors={"B"}, produces=set(), tags={"drain_aristocrats"})
add("Indulgent Aristocrat", 1, "Creature", colors={"B"}, produces=set(), tags={"vampire_type"})
add("Mondrak, Glory Dominus", 4, "Creature", colors={"W"}, produces=set(), tags=set())
add("Nullpriest of Oblivion", 2, "Creature", colors={"B"}, produces=set(), tags={"vampire_type"})
add("Ojer Taq, Deepest Foundation // Temple of Civilization", 6, "Land", colors={"W"}, produces={"W"}, tags=set())
add("Ophiomancer", 3, "Creature", colors={"B"}, produces=set(), tags={"token_maker"})
add("Pitiless Plunderer", 4, "Creature", colors={"B"}, produces=set(), tags={"token_maker"})
add("Purphoros, God of the Forge", 4, "Creature", colors={"R"}, produces=set(), tags=set())
add("Roaming Throne", 4, "Creature", colors=set(), produces=set(), tags=set())
add("Sanctum Seeker", 4, "Creature", colors={"B"}, produces=set(), tags={"drain_aristocrats", "vampire_type"})
add("Stensian Sanguinist // Exsanguinate", 2, "Creature", colors={"B"}, produces=set(), tags={"vampire_type"})
add("Vein Ripper", 6, "Creature", colors={"B"}, produces=set(), tags={"drain_aristocrats", "vampire_type"})
add("Vindictive Vampire", 4, "Creature", colors={"B"}, produces=set(), tags={"vampire_type"})
add("Viscera Seer", 1, "Creature", colors={"B"}, produces=set(), tags={"vampire_type"})
add("Vito, Fanatic of Aclazotz", 4, "Creature", colors={"B", "W"}, produces=set(), tags={"drain_aristocrats", "token_maker", "vampire_type"})
add("Vito, Thorn of the Dusk Rose", 3, "Creature", colors={"B"}, produces=set(), tags={"drain_aristocrats", "vampire_type"})
add("Welcoming Vampire", 3, "Creature", colors={"W"}, produces=set(), tags={"draw", "vampire_type"})
add("Zulaport Cutthroat", 2, "Creature", colors={"B"}, produces=set(), tags={"drain_aristocrats"})
add("Arcane Signet", 2, "Artifact", colors=set(), produces={"B", "R", "W"}, tags={"ramp"})
add("Ashnod's Altar", 3, "Artifact", colors=set(), produces={"C"}, tags={"ramp"})
add("Phyrexian Altar", 3, "Artifact", colors=set(), produces={"B", "G", "R", "U", "W"}, tags={"ramp"})
add("Skullclamp", 1, "Artifact", colors=set(), produces=set(), tags={"draw"})
add("Sol Ring", 1, "Artifact", colors=set(), produces={"C"}, tags={"ramp"})
add("Anointed Procession", 4, "Enchantment", colors={"W"}, produces=set(), tags={"token_maker"})
add("Bastion of Remembrance", 3, "Enchantment", colors={"B"}, produces=set(), tags={"drain_aristocrats", "token_maker"})
add("Black Market Connections", 3, "Enchantment", colors={"B"}, produces=set(), tags={"draw", "token_maker"})
add("Caretaker's Talent", 3, "Enchantment", colors={"W"}, produces=set(), tags={"draw", "token_maker"})
add("Exquisite Blood", 5, "Enchantment", colors={"B"}, produces=set(), tags=set())
add("Funeral Room // Awakening Hall", 3, "Enchantment", colors={"B"}, produces=set(), tags={"drain_aristocrats"})
add("Goblin Bombardment", 2, "Enchantment", colors={"R"}, produces=set(), tags={"removal"})
add("Legion's Landing // Adanto, the First Fort", 1, "Land", colors={"W"}, produces={"W"}, tags={"token_maker"})
add("Smothering Tithe", 4, "Enchantment", colors={"W"}, produces=set(), tags=set())
add("The Meathook Massacre", 2, "Enchantment", colors={"B"}, produces=set(), tags={"drain_aristocrats", "wipe"})
add("Unholy Annex // Ritual Chamber", 3, "Enchantment", colors={"B"}, produces=set(), tags={"drain_aristocrats", "draw"})
add("Warleader's Call", 3, "Enchantment", colors={"R", "W"}, produces=set(), tags=set())
add("Elspeth, Storm Slayer", 5, "Planeswalker", colors={"W"}, produces=set(), tags={"removal", "token_maker", "wipe"})
add("Sorin, Imperious Bloodlord", 3, "Planeswalker", colors={"B"}, produces=set(), tags={"removal"})
add("Anguished Unmaking", 3, "Instant", colors={"B", "W"}, produces=set(), tags={"removal"})
add("Call the Coppercoats", 3, "Instant", colors={"W"}, produces=set(), tags={"token_maker"})
add("Clever Concealment", 4, "Instant", colors={"W"}, produces=set(), tags=set())
add("Fell the Profane // Fell Mire", 4, "Land", colors={"B"}, produces={"B"}, tags={"removal"})
add("Get Lost", 2, "Instant", colors={"W"}, produces=set(), tags={"removal"})
add("Path to Exile", 1, "Instant", colors={"W"}, produces=set(), tags={"removal"})
add("Plumb the Forbidden", 2, "Instant", colors={"B"}, produces=set(), tags={"draw"})
add("Swords to Plowshares", 1, "Instant", colors={"W"}, produces=set(), tags={"removal"})
add("Teferi's Protection", 3, "Instant", colors={"W"}, produces=set(), tags=set())
add("Vampiric Tutor", 1, "Instant", colors={"B"}, produces=set(), tags={"tutor"})
add("Agadeem's Awakening // Agadeem, the Undercrypt", 3, "Land", colors={"B"}, produces={"B"}, tags=set())
add("Bloodline Bidding", 8, "Sorcery", colors={"B"}, produces=set(), tags=set())
add("Diabolic Intent", 2, "Sorcery", colors={"B"}, produces=set(), tags={"tutor"})
add("Rite of Oblivion", 2, "Sorcery", colors={"B", "W"}, produces=set(), tags={"removal"})
add("Sevinne's Reclamation", 3, "Sorcery", colors={"W"}, produces=set(), tags=set())
add("Vindicate", 3, "Sorcery", colors={"B", "W"}, produces=set(), tags={"removal"})
add("Arid Mesa", 0, "Land", colors=set(), produces={"R", "W"}, tags=set())  # busca Mountain ou Plains
add("Battlefield Forge", 0, "Land", colors={"R", "W"}, produces={"C", "R", "W"}, tags=set())
add("Blackcleave Cliffs", 0, "Land", colors={"B", "R"}, produces={"B", "R"}, tags=set())
add("Blazemire Verge", 0, "Land", colors={"B", "R"}, produces={"B", "R"}, tags={"verge_mountain_gate"})
add("Blood Crypt", 0, "Land", colors={"B", "R"}, produces={"B", "R"}, tags=set())
add("Bloodstained Mire", 0, "Land", colors=set(), produces={"B", "R"}, tags=set())  # busca Swamp ou Mountain
add("Cabal Coffers", 0, "Land", colors={"B"}, produces={"B"}, tags=set())
add("Cavern of Souls", 0, "Land", colors=set(), produces={"B", "R", "W"}, tags={"vampire_only_color"})
add("City of Brass", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())
add("Command Tower", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())
add("Fetid Heath", 0, "Land", colors={"B", "W"}, produces={"B", "W"}, tags={"filter_land"})
add("Fountainport", 0, "Land", colors=set(), produces={"C"}, tags={"draw", "token_maker"})
add("Godless Shrine", 0, "Land", colors={"B", "W"}, produces={"B", "W"}, tags=set())
add("Haunted Ridge", 0, "Land", colors={"B", "R"}, produces={"B", "R"}, tags=set())
add("Luxury Suite", 0, "Land", colors={"B", "R"}, produces={"B", "R"}, tags=set())
add("Mana Confluence", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())
add("Marsh Flats", 0, "Land", colors=set(), produces={"W", "B"}, tags=set())  # busca Plains ou Swamp
add("Minas Tirith", 0, "Land", colors={"W"}, produces={"W"}, tags={"draw"})
add("Plains", 0, "Land", colors={"W"}, produces={"W"}, tags=set())
add("Phyrexian Tower", 0, "Land", colors={"B"}, produces={"B", "C"}, tags=set())
add("Rugged Prairie", 0, "Land", colors={"R", "W"}, produces={"R", "W"}, tags={"filter_land"})
add("Savai Triome", 0, "Land", colors={"B", "R", "W"}, produces={"B", "R", "W"}, tags={"draw"})
add("Spectator Seating", 0, "Land", colors={"R", "W"}, produces={"R", "W"}, tags=set())
add("Swamp", 0, "Land", colors={"B"}, produces={"B"}, tags=set())
add("Takenuma, Abandoned Mire", 0, "Land", colors={"B"}, produces={"B"}, tags=set())
add("Urborg, Tomb of Yawgmoth", 0, "Land", colors=set(), produces={"B"}, tags=set())
add("Urza's Saga", 0, "Land", colors=set(), produces={"C"}, tags={"token_maker"})
add("Voldaren Estate", 0, "Land", colors=set(), produces={"B", "R", "W"}, tags={"vampire_only_color", "token_maker"})
add("Westvale Abbey // Ormendahl, Profane Prince", 0, "Land", colors={"B"}, produces={"C"}, tags={"token_maker"})

# Achado real 2026-08-27 (usuario: "Todas as cartas auditadas... tokens
# tb?"): TODOS os tokens deste deck viviam SO em state.tokens (pool
# separado, usado so como municao de sacrificio) e NUNCA eram
# adicionados a state.battlefield - ou seja, is_vampire()/is_creature()
# nem CONSEGUIRIAM ler esses nomes (KeyError em CARD_DB, nao existiam
# aqui) e qualquer contagem de "quantos Vampiros voce controla"
# (Champion of Dusk, Sanctum Seeker) NUNCA via os tokens da Eminence.
# Corrigido - tokens agora tem entrada real e sao adicionados aos DOIS
# (battlefield E tokens quando servem de fodder de sacrificio).
add("Vampire Token", 0, "Creature", colors={"B"}, produces=set(), tags={"vampire_type"})
add("Human Soldier Token", 0, "Creature", colors={"W"}, produces=set(), tags=set())
add("Snake Token", 0, "Creature", colors={"B"}, produces=set(), tags=set())
add("Vampire Demon Token", 0, "Creature", colors={"W", "B"}, produces=set(), tags={"vampire_type"})
add("Shapeshifter Token", 0, "Creature", colors=set(), produces=set(), tags={"vampire_type"})
# Achado real 2026-08-27 (usuario: "para disparar Caretaker's Talent e
# outros gatilhos de token/artefato"): Treasure ("T, Sacrifice: Add
# one mana of any color") precisa ser um token DE VERDADE (entrar em
# battlefield) pra disparar "whenever one or more tokens enter" do
# Caretaker's Talent - antes (Pitiless Plunderer, Black Market
# Connections) era so' um bonus de mana abstrato, nunca uma entrada
# real. Ver create_treasure_and_crack().
add("Treasure Token", 0, "Artifact", colors=set(), produces=set(), tags=set())
# Achado real 2026-08-28 (auditoria de checklist ampliada - varredura
# exaustiva de oracle_text das 94 cartas): Funeral Room // Awakening Hall e
# Unholy Annex // Ritual Chamber sao "Room" cards (Duskmourn) - depois de
# conjurar UM lado, "As a sorcery, you may pay the mana cost of a locked
# door to unlock it" tambem, ganhando o efeito do OUTRO lado no MESMO
# permanente. 100% ausente em 10 rodadas de correcao anteriores - so o lado
# inicialmente conjurado tinha efeito. Ritual Chamber cria um Demon 6/6
# flying - token novo, precisa de entrada real no CARD_DB.
add("Demon Token", 0, "Creature", colors={"B"}, produces=set(), tags=set())

def C(name: str) -> Card:
    return CARD_DB[name]

def parse_decklist(text: str) -> List[str]:
    deck = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("//") or line.startswith("#"):
            continue
        parts = line.split(" ", 1)
        qty = int(parts[0])
        name = parts[1].strip()
        deck.extend([name] * qty)
    return deck

def is_land(card: str) -> bool:
    return C(card).type == "Land"

def is_creature(card: str) -> bool:
    return C(card).type == "Creature"

def is_vampire(card: str) -> bool:
    return has_tag(card, "vampire_type") or card == COMMANDER

def has_tag(card: str, tag: str) -> bool:
    return tag in C(card).tags

# Achado real 2026-08-27 (auditoria do resto do deck): Bartolome del
# Presidio ("Sacrifice another creature or artifact: Put a +1/+1
# counter on Bartolome del Presidio") e' um outlet de sacrificio DE
# GRACA (sem custo de mana, igual Viscera Seer/Goblin Bombardment) que
# nunca tinha sido incluido aqui.
# Achado real 2026-08-27 (auditoria de terrenos): Minas Tirith
# ("enters tapped unless you control a legendary creature") nunca
# checava isso - conjunto de criaturas lendarias reais deste deck (nao
# inclui Ojer Taq, so' virar criatura via a face front que este
# simulador nunca conjura - Land-primary - nem Purphoros, que so e'
# criatura condicional a devocao, nao rastreada em lugar nenhum).
LEGENDARY_CREATURE_NAMES = {
    COMMANDER, "Bartolomé del Presidio", "Clavileño, First of the Blessed",
    "Elenda, the Dusk Rose", "Mondrak, Glory Dominus",
    "Vito, Fanatic of Aclazotz", "Vito, Thorn of the Dusk Rose",
}

SAC_OUTLETS = {"Ashnod's Altar", "Phyrexian Altar", "Viscera Seer", "Goblin Bombardment",
               "Bartolomé del Presidio", "Phyrexian Tower"}

# Achado real 2026-08-27 (usuario: "faca a carta por carta do Markov",
# mesmo rigor ja aplicado no Ur-Dragon/Hei Bai): a formula de cada
# death payoff NAO era uniforme no oraculo real, mas o codigo antigo
# tratava todo mundo em DEATH_PAYOFFS como "drain 1, gain 1" (exceto
# Vein Ripper, hardcoded 2). Conferido carta por carta contra o
# oraculo: (drain, gain) por evento de morte de UMA criatura.
# - Blood Artist / Cruel Celebrant / Vindictive Vampire / Bastion of
#   Remembrance / Funeral Room: "opponent loses 1, you gain 1" - (1, 1).
# - Vein Ripper: "opponent loses 2, you gain 2" - (2, 2).
# - Zulaport Cutthroat: MESMO texto do Blood Artist ("this or another
#   creature you control dies") - (1, 1) - estava 100% ausente do set
#   antigo, apesar de tageada drain_aristocrats e citada como
#   "habilitador redundante" na propria auditoria.md secao 6.
# - The Meathook Massacre: SO "opponent loses 1" quando morre criatura
#   NOSSA - sem ganho de vida nessa clausula (o "you gain 1" dela e' só
#   quando MORRE CRIATURA DO OPONENTE, que nao existe neste goldfish
#   solo) - (1, 0), assimetrico, NAO pode reusar a formula (1,1).
# - Cordial Vampire: "put a +1/+1 counter on each Vampire you control"
#   - NAO e' drain/lifegain, e' distribuicao de contador - (0, 0) aqui
#   de proposito (ver docstring "Simplificacoes" no topo do arquivo
#   pra por que contadores nao tem payoff numerico modelavel neste
#   simulador especifico).
DEATH_PAYOFF_FORMULAS = {
    "Blood Artist": (1, 1),
    "Cruel Celebrant": (1, 1),
    "Vindictive Vampire": (1, 1),
    "Bastion of Remembrance": (1, 1),
    "Funeral Room // Awakening Hall": (1, 1),
    "Vein Ripper": (2, 2),
    "Zulaport Cutthroat": (1, 1),
    "The Meathook Massacre": (1, 0),
    "Cordial Vampire": (0, 0),
}
DEATH_PAYOFFS = set(DEATH_PAYOFF_FORMULAS.keys())

# Anointed Procession / Mondrak, Glory Dominus / Elspeth, Storm Slayer:
# "If one or more tokens would be created under your control, twice
# that many... instead" - replacement effeitos reais, cada um dobra o
# numero de tokens (nao o gatilho como o Roaming Throne - sao mecanicas
# DIFERENTES, ver token_multiplier() abaixo). Achado real 2026-08-27
# (auditoria do resto do deck): Elspeth, Storm Slayer tem o MESMO texto
# estatico dos outros 2, mas nunca foi incluida na tupla (so' citada
# num comentario antigo, nunca de verdade adicionada aqui) - mesmo
# achado de "tag existe, dispatch nao" da Correcao #1.
TOKEN_DOUBLER_SOURCES = ("Anointed Procession", "Mondrak, Glory Dominus", "Elspeth, Storm Slayer")

# Achado real 2026-08-27 (auditoria do resto do deck): removal/protecao
# sem alvo real neste goldfish solo (mesma convencao ja aplicada no
# Hei Bai/Ur-Dragon) NUNCA era excluida do loop generico de conjuracao
# - Anguished Unmaking, Get Lost, Path to Exile, Swords to Plowshares,
# Vindicate, Rite of Oblivion eram conjuradas as cegas, gastando carta
# e mana de graca, competindo por prioridade cedo contra spells de
# valor real. Call the Coppercoats teria SEMPRE X=0 (conta criaturas de
# OPONENTE, que nao existem aqui). Clever Concealment/Teferi's
# Protection sao protecao pura, sem efeito de tabuleiro modelavel. Um
# piloto real segura essas cartas ate ter alvo/necessidade real.
EXCLUDE_BLIND_CAST = {
    "Anguished Unmaking", "Get Lost", "Path to Exile", "Swords to Plowshares",
    "Vindicate", "Rite of Oblivion", "Call the Coppercoats",
    "Clever Concealment", "Teferi's Protection",
}

# Poder real (Scryfall) das criaturas relevantes pro gatilho do
# Welcoming Vampire ("one or more OTHER creatures you control with
# power 2 or less enter"). So criaturas NOMEADAS deste deck - tokens
# (Vampire Token 1/1, Snake Token 1/1) sao tratados como poder <=2 na
# hora do gatilho (todos os tokens deste deck realmente tem poder
# baixo, ver goldfish-log.md).
CREATURE_POWER = {
    COMMANDER: 4, "Bartolomé del Presidio": 2, "Blood Artist": 0,
    "Bloodletter of Aclazotz": 2, "Bloodthirsty Conqueror": 5,
    "Champion of Dusk": 4, "Charismatic Conqueror": 2,
    "Clavileño, First of the Blessed": 2, "Cordial Vampire": 1,
    "Cruel Celebrant": 1, "Elenda, the Dusk Rose": 1,
    "Emeritus of Woe": 5, "Enduring Tenacity": 4, "Indulgent Aristocrat": 1,
    "Mondrak, Glory Dominus": 4, "Nullpriest of Oblivion": 2,
    "Ophiomancer": 2, "Pitiless Plunderer": 1, "Purphoros, God of the Forge": 6,
    "Roaming Throne": 4, "Sanctum Seeker": 3,
    "Stensian Sanguinist // Exsanguinate": 2, "Vein Ripper": 6,
    "Vindictive Vampire": 2, "Viscera Seer": 1, "Vito, Fanatic of Aclazotz": 4,
    "Vito, Thorn of the Dusk Rose": 1, "Welcoming Vampire": 2,
    "Zulaport Cutthroat": 1,
    # Tokens - poder real de cada um (achado real 2026-08-27: o
    # fallback generico `1 if "Token" in name else 3` dava poder 1 pra
    # QUALQUER token, incluindo o Vampire Demon Token 4/3 do Vito
    # Fanatic - qualificava errado pro gatilho do Welcoming Vampire,
    # "power 2 or less").
    "Vampire Token": 1, "Human Soldier Token": 1, "Snake Token": 1,
    "Vampire Demon Token": 4, "Shapeshifter Token": 3, "Demon Token": 6,
}

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
    tokens: List[str] = field(default_factory=list)  # tokens de Vampiro 1/1 da Eminence, disponiveis pra sac
    turn: int = 0
    land_played: bool = False
    mana_spent_this_turn: int = 0
    lands_played_total: int = 0

    commander_in_play: bool = False
    commander_cast_turn: Optional[int] = None
    commander_cast_count: int = 0

    eminence_tokens_created: int = 0
    edgar_attack_counters_total: int = 0
    edgar_attack_turns: int = 0

    adanto_tokens_created: int = 0
    minas_tirith_draws: int = 0

    drain_total: int = 0
    lifegain_total: int = 0
    creatures_sacrificed_total: int = 0
    death_trigger_events: int = 0

    champion_of_dusk_draws: int = 0
    welcoming_vampire_draws: int = 0
    welcoming_vampire_trigger_pending: int = 0
    caretakers_talent_trigger_pending: int = 0
    caretakers_talent_draws: int = 0

    # Black Market Connections: achado real 2026-08-27 (auditoria do
    # resto do deck) - "choose one or more" com 3 modos, cada um custa
    # vida (nao rastreada aqui). 100% ausente antes (lumped errado em
    # "modal deferido" junto com o Class do Caretaker's Talent - eram
    # cartas diferentes, achado incorreto na Correcao #1 nunca
    # revisitado ate agora). Implementado por DEFAULT so' o modo mais
    # barato (Sell Contraband, 1 Treasure) - Buy Information/Hire a
    # Mercenary ficam deferidos (o mesmo "greedy pega os 3 de graca"
    # nao e' um piloto realista so' porque vida nao e' rastreada aqui).
    black_market_treasures: int = 0
    # Achado real 2026-08-28 (auditoria de checklist - metricas basicas
    # obrigatorias: ramp/draw/interaction/finisher). Nao havia nenhuma
    # metrica agregada de ramp ate agora (so tags decorativas em Arcane
    # Signet/Sol Ring/Ashnod's Altar/Phyrexian Altar).
    ramp_pieces_cast: int = 0

    # Funeral Room // Awakening Hall e Unholy Annex // Ritual Chamber -
    # "unlock the other door" (ver comentario no add() do Demon Token acima).
    awakening_hall_unlocked: bool = False
    awakening_hall_reanimated: int = 0
    ritual_chamber_unlocked: bool = False
    ritual_chamber_demons_created: int = 0
    sanctum_seeker_drains: int = 0
    vito_fanatic_stage_this_turn: int = 0
    vito_fanatic_demons_created: int = 0
    clavileno_triggers: int = 0
    # elenda_counters / elenda_death_tokens: achado real 2026-08-27 -
    # estes 2 campos existiam mas NUNCA eram incrementados em lugar
    # nenhum (dead fields). Investigado: nao e' so um bug de "esqueci
    # de somar" - o gatilho de MORTE da propria Elenda ("when Elenda
    # dies, create X tokens where X is Elenda's power") nunca teria
    # janela real pra disparar neste simulador, porque o sac_loop so
    # sacrifica TOKENS de Vampiro (decisao ja documentada no docstring
    # do topo do arquivo, "Loop de sacrificio... limitado a tokens"),
    # nenhuma criatura NOMEADA (Elenda inclusa) jamais morre aqui. Os
    # campos ficam mantidos por transparencia de dado (elenda_counters
    # agora E' incrementado de verdade a cada morte de token, ver
    # _apply_death_payoffs - e' o passivo REAL dela, "whenever another
    # creature dies, put a +1/+1 counter on Elenda"), mas
    # elenda_death_tokens fica travado em 0 de proposito - documentado,
    # nao e' mais um buraco silencioso.
    elenda_counters: int = 0
    elenda_death_tokens: int = 0

    purphoros_damage_total: int = 0
    warleaders_call_damage_total: int = 0
    ophiomancer_snakes_created: int = 0
    skullclamp_draws: int = 0
    pitiless_plunderer_treasures: int = 0
    unholy_annex_draws: int = 0
    bastion_of_remembrance_tokens: int = 0
    token_doubler_events: int = 0

    # Achado real 2026-08-27 (usuario: "Vc contabilizou a eminence... e
    # o Emeritus of Woe tem o Demonic Tutor Prepared, mais um tutor!"):
    # Vampiric Tutor/Diabolic Intent so tinham busca de verdade DENTRO
    # de combo_hunt() (gated por COMBO_HUNTING_POLICY=False por
    # padrao) - na politica DEFAULT (o batch oficial), os 2 tutores
    # eram conjurados as cegas sem NENHUM efeito de busca. Emeritus of
    # Woe (mecanica "prepared": entra ja preparado = permissao de
    # conjurar 1 copia do Demonic Tutor na hora - AINDA pagando
    # {1}{B}=2, ver try_emeritus_prepared_tutor - e fica preparado de
    # novo toda vez que 2+ criaturas morrem no turno) era 100% ausente.
    tutors_used_total: int = 0
    emeritus_of_woe_tutors: int = 0
    emeritus_prepared: bool = False
    creatures_died_this_turn: int = 0

    # Achado real 2026-08-27 (usuario: "Vc contou o Exsanguinate
    # preparado do Sanguine Stensian como mana sink e um finalizador
    # potencial?"): Stensian Sanguinist tem a MESMA mecanica "prepared"
    # do Emeritus of Woe, mas com gatilho diferente - "whenever you
    # attack, target creature gains deathtouch... whenever that
    # creature deals combat damage to a player, becomes prepared" (nao
    # e' morte de criatura - a tag 'drain_aristocrats' antiga era
    # decorativa E errada, removida). 100% ausente antes.
    stensian_prepared: bool = False
    exsanguinate_casts: int = 0
    exsanguinate_x_total: int = 0

    # Achado real 2026-08-27 (auditoria do resto do deck, pedido do
    # usuario "Audite o resto do deck"): Plumb the Forbidden, Sevinne's
    # Reclamation e Bloodline Bidding eram conjuradas as cegas sem
    # NENHUM efeito - nem tagueadas certo (Plumb tinha 'draw' mas sem
    # dispatch) nem excluidas do auto-cast como as removals viraram.
    plumb_the_forbidden_draws: int = 0
    sevinnes_reclamation_returns: int = 0
    bloodline_bidding_returns: int = 0
    urzas_saga_entered_turn: Optional[int] = None
    urzas_saga_tutors: int = 0

    # Achado real 2026-08-27 (auditoria do resto do deck): este
    # simulador nao tinha NENHUM rastreio de terreno tapado - Savai
    # Triome ("enters tapped", sempre) e Blackcleave Cliffs/Haunted
    # Ridge (tapados condicional a quantidade de OUTROS terrenos ja em
    # campo) contribuiam mana no mesmo turno em que entravam, sem
    # restricao nenhuma. Corrigido - ver play_land().
    tapped_lands_this_turn: int = 0

    combo_active: bool = False
    combo_active_turn: Optional[int] = None
    combo_enabler: Optional[str] = None
    both_combo_pieces_turn: Optional[int] = None  # turno em que as 2 pecas ja estao em campo (antes de precisar de um gatilho pra "ligar")

    roaming_throne_doublings: int = 0

    def draw(self, n: int = 1):
        for _ in range(n):
            if self.library:
                self.hand.append(self.library.pop(0))

    def has(self, name: str) -> bool:
        return name in self.battlefield

    def roaming_throne_active(self) -> bool:
        return self.has("Roaming Throne")

def effective_power(state: GameState, name: str) -> int:
    # Warleader's Call: "Creatures you control get +1/+1" - habilidade
    # ESTATICA de anthem, achado real 2026-08-28 (auditoria de checklist -
    # habilidades estaticas). O gatilho de dano dela ja era modelado
    # (on_creature_enters), mas o anthem em si nunca era aplicado em
    # nenhum calculo de poder - importa pro limiar do Welcoming Vampire
    # ("power 2 or less"): uma criatura de poder 2 (ex. Bloodletter of
    # Aclazotz) vira poder 3 com o anthem ativo, deixando de qualificar.
    base = CREATURE_POWER.get(name, 1 if "Token" in name else 3)
    if state.has("Warleader's Call") and name != "Warleader's Call":
        base += 1
    return base

# =========================================================
# MANA MODEL
# =========================================================

# Achado real 2026-08-27 (auditoria de terrenos): swamp_count() checava
# `"Swamp" in c` (substring do NOME) - perde Blood Crypt e Godless
# Shrine, que tem o TIPO Swamp de verdade (`Land — Swamp Mountain` /
# `Land — Plains Swamp`) mas nao tem "Swamp" no proprio nome. Cabal
# Coffers ("Add B for each Swamp you control") ficava subcontando.
SWAMP_TYPED_LANDS = {"Swamp", "Blood Crypt", "Godless Shrine"}
MOUNTAIN_TYPED_LANDS = {"Mountain", "Blood Crypt", "Savai Triome"}

def swamp_count(state: GameState) -> int:
    if state.has("Urborg, Tomb of Yawgmoth"):
        return sum(1 for c in state.battlefield if is_land(c))
    return sum(1 for c in state.battlefield if c in SWAMP_TYPED_LANDS)

def total_mana(state: GameState) -> int:
    total = 0
    for card in state.battlefield:
        if card == "Cabal Coffers":
            # Achado real 2026-08-27 (auditoria de terrenos): Cabal
            # Coffers NAO tem "{T}: Add" nenhum - a UNICA habilidade
            # dela e' "{2}, {T}: Add B for each Swamp you control".
            # A versao anterior dava +1 (como terreno normal) MAIS o
            # bonus de swamps, de GRACA, sem nunca pagar o {2} real.
            # Corrigido - ver try_cabal_coffers(), chamada separada
            # (custo condicional, so vale a pena com Swamps o
            # suficiente pra compensar).
            continue
        if is_land(card):
            total += 1
        elif card == "Sol Ring":
            total += 2
        elif card in ("Ashnod's Altar", "Phyrexian Altar"):
            continue  # exige sacrificio, nao conta como mana livre - ver sac_loop
        elif has_tag(card, "ramp"):
            total += 1
    return total - state.tapped_lands_this_turn

def try_cabal_coffers(state: GameState, log: List[Dict]):
    if not state.has("Cabal Coffers"):
        return
    sc = swamp_count(state)
    if sc <= 2 or remaining_mana(state) < 2:
        return  # custa 2 pra ativar - so vale se devolver mais que 2
    net = sc - 2
    state.mana_spent_this_turn -= net
    log.append({"trigger": "cabal_coffers", "swamps": sc, "net": net, "turn": state.turn})

def try_adanto(state: GameState, log: List[Dict]):
    # Achado real 2026-08-28 (auditoria de checklist de mecanica): a
    # habilidade da Adanto ("{2}{W}, {T}: Create a 1/1 white Vampire
    # creature token with lifelink") estava so tagueada como
    # "token_maker", nunca despachada. {T} = uma ativacao por turno.
    if not state.has("Legion's Landing // Adanto, the First Fort"):
        return
    if remaining_mana(state) < 3 or color_sources(state, "W") < 1:
        return
    state.mana_spent_this_turn += 3
    n = token_multiplier(state)
    for _ in range(n):
        state.tokens.append("Vampire Token")
        state.battlefield.append("Vampire Token")
    state.adanto_tokens_created += n
    on_creature_enters(state, log, "Vampire Token", count=n)
    log.append({"trigger": "adanto_token", "count": n, "turn": state.turn})

def controls_a_demon(state: GameState) -> bool:
    return any("Demon" in c for c in state.battlefield)

def try_unlock_rooms(state: GameState, log: List[Dict]):
    # Achado real 2026-08-28 (auditoria de checklist ampliada): "Room" cards
    # (Duskmourn) permitem, "as a sorcery", pagar o custo de mana da porta
    # ainda trancada pra tambem destranca-la no MESMO permanente - nao e' um
    # cast de spell (nao dispara Eminence/gatilhos de conjuracao), e' uma
    # acao especial, igual subir de nivel de Class. 100% ausente antes.
    if state.has("Funeral Room // Awakening Hall") and not state.awakening_hall_unlocked:
        cost = 8  # Awakening Hall: {6}{B}{B}
        if remaining_mana(state) >= cost:
            state.mana_spent_this_turn += cost
            state.awakening_hall_unlocked = True
            targets = [c for c in state.graveyard if is_creature(c)]
            for target in targets:
                state.graveyard.remove(target)
                state.battlefield.append(target)
                apply_etb(state, target, log)
                on_creature_enters(state, log, target)
                state.awakening_hall_reanimated += 1
            log.append({"trigger": "awakening_hall_unlock", "reanimated": targets, "turn": state.turn})

    if state.has("Unholy Annex // Ritual Chamber") and not state.ritual_chamber_unlocked:
        cost = 5  # Ritual Chamber: {3}{B}{B}
        if remaining_mana(state) >= cost:
            state.mana_spent_this_turn += cost
            state.ritual_chamber_unlocked = True
            state.tokens.append("Demon Token")
            state.battlefield.append("Demon Token")
            state.ritual_chamber_demons_created += 1
            on_creature_enters(state, log, "Demon Token")
            log.append({"trigger": "ritual_chamber_unlock", "turn": state.turn})

def try_minas_tirith(state: GameState, log: List[Dict]):
    # Achado real 2026-08-28 (auditoria de checklist de mecanica): a
    # habilidade "{1}{W}, {T}: Draw a card. Activate only if you attacked
    # with two or more creatures this turn" estava so tagueada como
    # "draw", nunca despachada. Esse motor assume que TODAS as criaturas
    # atacam desimpedidas a cada combate (mesma premissa ja usada pro
    # contador de ataque do proprio Edgar) - "atacou com 2+" vira "2+
    # criaturas em campo no momento do combate". {T} = uma vez por turno,
    # chamado logo depois de combat_step().
    if not state.has("Minas Tirith") or not state.commander_in_play:
        return
    if state.turn <= state.commander_cast_turn:
        return  # sem combate ainda nesse turno (mesmo guard do combat_step)
    n_creatures = sum(1 for c in state.battlefield if is_creature(c))
    if n_creatures < 2:
        return
    if remaining_mana(state) < 2 or color_sources(state, "W") < 1:
        return
    state.mana_spent_this_turn += 2
    state.draw(1)
    state.minas_tirith_draws += 1
    log.append({"trigger": "minas_tirith_draw", "attackers_proxy": n_creatures, "turn": state.turn})

def color_sources(state: GameState, color: str, for_vampire: bool = False) -> int:
    """Conta fontes de mana colorida REAIS pra `color`, respeitando
    restricoes de uso do oraculo real (achado 2026-08-28, auditoria de
    checklist de mecanica):
    - Cavern of Souls / Voldaren Estate (tag "vampire_only_color"): a mana
      colorida so pode ser gasta pra conjurar um spell de criatura Vampiro
      (Cavern) / spell Vampiro (Voldaren) - nao vale pra qualquer spell.
    - Fetid Heath / Rugged Prairie (tag "filter_land"): sao filter lands -
      precisam de uma fonte de mana colorida JA existente (W/B ou R/W) pra
      "filtrar", nao produzem cor do nada. Aproximado aqui como: so contam
      se existir OUTRA fonte real da mesma cor em campo.
    - Blazemire Verge (tag "verge_mountain_gate"): {T}: Add {B} sempre, mas
      {T}: Add {R} so se controlar Swamp ou Mountain."""
    n = 0
    for card in state.battlefield:
        if color not in C(card).produces:
            continue
        if has_tag(card, "vampire_only_color") and not for_vampire:
            continue
        if has_tag(card, "verge_mountain_gate") and color == "R":
            if swamp_count(state) <= 0 and not any(m in state.battlefield for m in MOUNTAIN_TYPED_LANDS):
                continue
        if has_tag(card, "filter_land"):
            has_other_source = any(
                other != card and color in C(other).produces
                and not has_tag(other, "filter_land")
                and not (has_tag(other, "vampire_only_color") and not for_vampire)
                for other in state.battlefield
            )
            if not has_other_source:
                continue
        n += 1
    return n

def remaining_mana(state: GameState) -> int:
    return total_mana(state) - state.mana_spent_this_turn

def commander_effective_mv(state: GameState) -> int:
    return C(COMMANDER).mv + 2 * state.commander_cast_count

def can_cast(state: GameState, card: str) -> bool:
    mv = commander_effective_mv(state) if card == COMMANDER else C(card).mv
    if remaining_mana(state) < mv:
        return False
    vamp = is_vampire(card) and C(card).type == "Creature"
    for color in C(card).colors:
        if color_sources(state, color, for_vampire=vamp) < 1:
            return False
    return True

# =========================================================
# MULLIGAN
# =========================================================

FAST_RAMP = {"Sol Ring", "Arcane Signet"}

def should_keep(hand: List[str]) -> bool:
    lands = sum(1 for c in hand if is_land(c))
    if lands > 5:
        return False
    if lands >= 3:
        return True
    if lands == 2:
        return any(c in FAST_RAMP for c in hand)
    return False

def choose_bottom(hand: List[str], n: int) -> List[str]:
    nonlands = [c for c in hand if not is_land(c)]
    nonlands.sort(key=lambda c: -C(c).mv)
    return nonlands[:n] if len(nonlands) >= n else (nonlands + [c for c in hand if is_land(c)])[:n]

# =========================================================
# LAND DROP
# =========================================================

def play_land(state: GameState, log: List[Dict]):
    if state.land_played:
        return
    lands_in_hand = [c for c in state.hand if is_land(c)]
    if not lands_in_hand:
        return
    have_colors = set()
    for c in state.battlefield:
        have_colors |= C(c).produces
    missing = {"W", "B", "R"} - have_colors
    best = None
    for c in lands_in_hand:
        if C(c).produces & missing:
            best = c
            break
    choice = best or lands_in_hand[0]
    state.hand.remove(choice)
    state.battlefield.append(choice)
    state.land_played = True
    state.lands_played_total += 1

    other_lands = sum(1 for c in state.battlefield if is_land(c) and c != choice)
    has_legendary_creature = any(n in state.battlefield for n in LEGENDARY_CREATURE_NAMES)
    if choice == "Savai Triome" or \
            (choice == "Blackcleave Cliffs" and other_lands > 2) or \
            (choice == "Haunted Ridge" and other_lands < 2) or \
            (choice == "Minas Tirith" and not has_legendary_creature):
        state.tapped_lands_this_turn += 1
    if choice == "Urza's Saga":
        state.urzas_saga_entered_turn = state.turn

# =========================================================
# EMINENCE + GATILHOS DE VAMPIRO (Passo 0 - ver docstring)
# =========================================================

def _times(state: GameState, is_vampire_source: bool = True) -> int:
    # Roaming Throne: "If a triggered ability of ANOTHER CREATURE you
    # control OF THE CHOSEN TYPE triggers, it triggers an additional
    # time" - so vale pra gatilhos cuja FONTE e' uma criatura Vampiro
    # (tipo escolhido, ver docstring do topo). Achado real 2026-08-27
    # (usuario: "faca a carta por carta"): a versao antiga aplicava
    # `_times()` (dobra) globalmente em QUALQUER gatilho sem checar se
    # a fonte de fato e' uma criatura Vampiro - por coincidencia todos
    # os gatilhos ja implementados antes eram mesmo Vampiros, entao
    # nunca deu bug ate agora, mas os gatilhos novos desta rodada
    # (Purphoros, Warleader's Call, Ophiomancer, Skullclamp, Pitiless
    # Plunderer, Zulaport Cutthroat, Meathook Massacre, Bastion of
    # Remembrance, Funeral Room, Unholy Annex) tem fontes que NAO sao
    # criaturas Vampiro (algumas nem sao criaturas) - passar
    # is_vampire_source=False nesses evita dobrar errado.
    return 2 if (is_vampire_source and state.roaming_throne_active()) else 1

def _log_doubling(state: GameState, times: int):
    if times == 2:
        state.roaming_throne_doublings += 1

def token_multiplier(state: GameState) -> int:
    # Anointed Procession / Mondrak, Glory Dominus: replacement effects
    # reais e INDEPENDENTES do Roaming Throne (que dobra o GATILHO, nao
    # a contagem de token) - cada um "twice that many tokens created
    # instead", empilham multiplicativamente entre si (regra real: cada
    # efeito de substituicao se aplica na ordem escolhida pelo
    # controlador). Achado real 2026-08-27: nenhum dos dois era checado
    # em lugar nenhum, apesar de tageados 'token_maker'.
    n = sum(1 for c in TOKEN_DOUBLER_SOURCES if state.has(c))
    if n:
        state.token_doubler_events += 1
    return 2 ** n

def _check_combo(state: GameState, log: List[Dict]):
    if state.combo_active:
        return
    for enabler in ("Exquisite Blood", "Bloodthirsty Conqueror"):
        if not state.has(enabler):
            continue
        for partner in GAIN_LIFE_DRAIN_SOURCES:
            # Achado real 2026-08-27: so Exquisite Blood era checado
            # como habilitador do combo com Vito, Thorn of the Dusk
            # Rose. Bloodthirsty Conqueror ("whenever an opponent loses
            # life, you gain that much life") forma o MESMO loop
            # infinito com Vito Thorn - e' um habilitador alternativo
            # real que a auditoria original nunca detectou.
            #
            # Achado real 2026-08-28 (auditoria de checklist - habilidades
            # estaticas): Enduring Tenacity ("whenever you gain life,
            # target opponent loses that much life") e' um segundo
            # habilitador possivel pro MESMO loop (funcionalmente
            # identico a Vito Thorn pra esse proposito) - fecha o combo
            # de graca (sem precisar da propria Vito Thorn em campo).
            if state.has(partner):
                state.combo_active = True
                state.combo_active_turn = state.turn
                state.combo_enabler = f"{enabler}+{partner}"
                log.append({"trigger": "combo_active", "enabler": state.combo_enabler, "turn": state.turn})
                return

GAIN_LIFE_DRAIN_SOURCES = ("Vito, Thorn of the Dusk Rose", "Enduring Tenacity")

def gain_life(state: GameState, amt: int, log: List[Dict], source: str = ""):
    if amt <= 0:
        return
    state.lifegain_total += amt
    if not state.combo_active:
        # Achado real 2026-08-27 (usuario: "faca a carta por carta do
        # Markov"): Vito, Thorn of the Dusk Rose - a peca de combo mais
        # famosa da lista - tinha ZERO implementacao da PROPRIA
        # habilidade ("whenever you gain life, target opponent loses
        # that much life"). So era usado como string-match pra decidir
        # se o combo com Exquisite Blood estava montado, nunca gerava
        # valor real por conta propria (mesmo sem Exquisite Blood em
        # campo). 1 hop so (nao recursivo) - uma vez que o combo real
        # for detectado (ver _check_combo), o jogo e' tratado como
        # ganho e paramos de somar incrementos individuais infinitos.
        #
        # Achado real 2026-08-28 (auditoria de checklist - habilidades
        # estaticas): Enduring Tenacity tem O MESMO texto real de Vito
        # Thorn ("Whenever you gain life, target opponent loses that
        # much life") - estava tageada 'drain_aristocrats' e tratada
        # como se fosse um death payoff (nunca era - essa habilidade nao
        # tem nada a ver com morte de criatura), entao ficava 100%
        # ausente. Se as DUAS estiverem em campo, cada uma dispara
        # separadamente (2 fontes independentes do mesmo efeito, regra
        # real de Magic).
        for src in GAIN_LIFE_DRAIN_SOURCES:
            if state.has(src):
                state.drain_total += amt
                log.append({"trigger": "gain_to_drain", "amt": amt, "enabler": src, "source": source, "turn": state.turn})
    _check_combo(state, log)

def lose_life_opponent(state: GameState, amt: int, log: List[Dict], source: str = ""):
    if amt <= 0:
        return
    if state.has("Bloodletter of Aclazotz"):
        # Achado real 2026-08-27 (auditoria do resto do deck): "If an
        # opponent would lose life during YOUR TURN, they lose twice
        # that much life instead." Este simulador SO avanca os
        # PROPRIOS turnos (nunca simula turno de oponente), entao essa
        # condicao e' sempre verdadeira aqui - um multiplicador
        # universal sobre TODO drain do motor (Zulaport, Blood Artist,
        # Purphoros, Warleader's Call, Sanctum Seeker, Exsanguinate,
        # etc.), 100% ausente antes apesar de ser uma das criaturas
        # mais impactantes da lista pra esse exato pacote de
        # aristocratas. Replacement effect - dobra uma vez so, antes de
        # qualquer gatilho reagir (Bloodthirsty Conqueror abaixo ja
        # reage ao valor CORRETO, ja dobrado).
        amt *= 2
        log.append({"trigger": "bloodletter_of_aclazotz_double", "amt": amt, "source": source, "turn": state.turn})
    state.drain_total += amt
    if state.has("Bloodthirsty Conqueror") and not state.combo_active:
        state.lifegain_total += amt
        log.append({"trigger": "bloodthirsty_conqueror_gain", "amt": amt, "source": source, "turn": state.turn})
    _check_combo(state, log)

def on_creature_enters(state: GameState, log: List[Dict], name: str, count: int = 1):
    # Dispara pra QUALQUER criatura entrando (conjurada OU token) -
    # Purphoros e Warleader's Call NAO exigem fonte Vampiro (e' "a
    # creature"/"another creature" generico). Achado real 2026-08-27:
    # Purphoros e Warleader's Call tinham ZERO implementacao apesar de
    # serem motores de dano centrais num deck que cria muitos tokens
    # (cada Eminence, cada Snake do Ophiomancer, cada token do Bastion
    # of Remembrance conta).
    if count <= 0:
        return
    if state.has("Purphoros, God of the Forge") and name != "Purphoros, God of the Forge":
        amt = 2 * count
        state.purphoros_damage_total += amt
        lose_life_opponent(state, amt, log, source="purphoros")
    if state.has("Warleader's Call"):
        amt = count
        state.warleaders_call_damage_total += amt
        lose_life_opponent(state, amt, log, source="warleaders_call")
    if state.has("Welcoming Vampire") and name != "Welcoming Vampire":
        # "one or more OTHER creatures you control with power 2 or less
        # enter, draw a card. Triggers only once each turn." Achado
        # real 2026-08-27: a condicao antiga era ERRADA - checava se um
        # vampiro tinha sido CONJURADO (condicao da Eminence, gatilho
        # DIFERENTE), nao se uma criatura de poder baixo de fato ENTROU
        # (perdia criaturas nao-Vampiro de poder baixo, ex. Ophiomancer
        # 2/2, e so acertava por coincidencia quando a Eminence tambem
        # disparava).
        power = effective_power(state, name)
        if power <= 2:
            state.welcoming_vampire_trigger_pending = 1
    on_token_enters(state, log, name, count=count)

def on_token_enters(state: GameState, log: List[Dict], name: str, count: int = 1):
    # Achado real 2026-08-27 (usuario: "para disparar Caretaker's
    # Talent e outros gatilhos de token/artefato"): extraido de
    # on_creature_enters() pra tambem cobrir tokens NAO-criatura
    # (Treasure) - "whenever one or more tokens you control enter" nao
    # se restringe a criatura no oraculo real. Chamado tanto por
    # on_creature_enters() (tokens de criatura) quanto direto por
    # create_treasure_and_crack() (Treasure).
    if count <= 0 or "Token" not in name:
        return
    if state.has("Caretaker's Talent"):
        # Habilidade BASE do Class (antes de qualquer nivel) -
        # "Whenever one or more tokens you control enter, draw a card.
        # Triggers only once each turn" - nao depende de subir de
        # nivel (isso e' so' pros niveis 2/3, ja deferidos). Estava
        # 100% ausente, lumped errado junto com o resto do Class
        # deferido na Correcao #1.
        state.caretakers_talent_trigger_pending = 1

def create_treasure_and_crack(state: GameState, log: List[Dict], count: int, source: str):
    # Achado real 2026-08-27 (usuario pediu explicitamente): Treasure
    # ("T, Sacrifice: Add one mana of any color") agora e' um token DE
    # VERDADE - entra em battlefield (dispara on_token_enters, ex.
    # Caretaker's Talent), depois um jogador greedy racha na hora pra
    # mana (mesmo padrao de "usa a mana no mesmo turno" do resto do
    # motor). Compartilhado entre Pitiless Plunderer e Black Market
    # Connections - as 2 fontes de Treasure deste deck.
    if count <= 0:
        return
    for _ in range(count):
        state.battlefield.append("Treasure Token")
    on_token_enters(state, log, "Treasure Token", count=count)
    for _ in range(count):
        state.battlefield.remove("Treasure Token")
    state.mana_spent_this_turn -= count
    log.append({"trigger": "treasure_created_and_cracked", "count": count, "source": source, "turn": state.turn})

def eminence_trigger(state: GameState, card: str, log: List[Dict]):
    # "Whenever you cast another Vampire spell, if Edgar is in the
    # command zone or on the battlefield, create a 1/1 black Vampire
    # creature token." Funciona mesmo com Edgar so na zona de comando.
    if card == COMMANDER or not is_vampire(card):
        return
    edgar_available = state.commander_in_play or state.commander_cast_count == 0
    if not edgar_available:
        return
    times = _times(state)
    for _ in range(times):
        n = token_multiplier(state)
        for _ in range(n):
            state.tokens.append("Vampire Token")
            state.battlefield.append("Vampire Token")
            state.eminence_tokens_created += 1
        on_creature_enters(state, log, "Vampire Token", count=n)
    _log_doubling(state, times)
    log.append({"trigger": "eminence", "card": card, "times": times, "turn": state.turn})

def welcoming_vampire_check(state: GameState, log: List[Dict]):
    # "Whenever one or more OTHER creatures you control with power 2 or
    # less enter, draw a card. This ability triggers only once each
    # turn." O flag pending agora e' setado em on_creature_enters (ver
    # acima), checando poder de verdade em vez de piggyback na Eminence.
    if not state.has("Welcoming Vampire"):
        return
    if state.welcoming_vampire_trigger_pending <= 0:
        return
    times = _times(state)
    for _ in range(times):
        state.draw(1)
        state.welcoming_vampire_draws += 1
    _log_doubling(state, times)
    log.append({"trigger": "welcoming_vampire", "times": times, "turn": state.turn})
    state.welcoming_vampire_trigger_pending = 0

def caretakers_talent_check(state: GameState, log: List[Dict]):
    # Habilidade BASE do Class (nao depende de nivel): "Whenever one or
    # more tokens you control enter, draw a card. Triggers only once
    # each turn." Fonte nao-criatura (Enchantment - Class) -> sem
    # dobra do Roaming Throne.
    if not state.has("Caretaker's Talent"):
        return
    if state.caretakers_talent_trigger_pending <= 0:
        return
    state.draw(1)
    state.caretakers_talent_draws += 1
    log.append({"trigger": "caretakers_talent", "turn": state.turn})
    state.caretakers_talent_trigger_pending = 0

def _tutor_target(state: GameState) -> Optional[str]:
    # Heuristica generica de "melhor carta disponivel" pra qualquer
    # tutor deste deck (Vampiric Tutor, Diabolic Intent, Demonic Tutor
    # do Emeritus of Woe). Prioridade 1: fechar o combo se so falta 1
    # peca e a outra ja esta resolvida/na mao - motivo real: um
    # jogador de verdade sempre fecha o combo antes de buscar
    # qualquer outra coisa. Prioridade 2 (fallback generico, mesma
    # convencao "pega o melhor" usada nos outros decks desta sessao):
    # maior mana value ainda na biblioteca.
    have = [p for p in COMBO_PIECES if p in state.battlefield or p in state.hand]
    missing = [p for p in COMBO_PIECES if p not in state.battlefield and p not in state.hand]
    if have and missing and missing[0] in state.library:
        return missing[0]
    pool = [c for c in state.library if not is_land(c)]
    if not pool:
        return None
    return max(pool, key=lambda c: C(c).mv)

def _diabolic_intent_has_fodder(state: GameState) -> bool:
    return bool(state.tokens) or any(
        is_creature(c) and c != COMMANDER and c not in COMBO_PIECES for c in state.battlefield)

def _pay_diabolic_intent_cost(state: GameState, log: List[Dict]):
    # "As an additional cost to cast this spell, sacrifice a creature."
    # Achado real 2026-08-27 (usuario: "pode tb ser sacrificado pro
    # Diabolic Intent"): prioriza um token da Eminence disponivel
    # (fodder de graca, ja excedente) sobre uma criatura NOMEADA de
    # verdade - um jogador real sempre prefere isso. So chamar depois
    # de confirmar _diabolic_intent_has_fodder(state).
    if state.tokens:
        popped = state.tokens.pop()
        state.battlefield.remove(popped)
        state.creatures_died_this_turn += 1
        log.append({"action": "diabolic_intent_sac", "sacrificed": "token", "turn": state.turn})
        return
    sac_candidates = [c for c in state.battlefield
                       if is_creature(c) and c != COMMANDER and c not in COMBO_PIECES]
    victim = sac_candidates[0]
    state.battlefield.remove(victim)
    state.graveyard.append(victim)
    state.creatures_died_this_turn += 1
    log.append({"action": "diabolic_intent_sac", "sacrificed": victim, "turn": state.turn})

def _apply_death_payoffs(state: GameState, log: List[Dict], source: str):
    # Elenda, the Dusk Rose: "Whenever ANOTHER creature dies, put a
    # +1/+1 counter on Elenda." Passivo real dela, independente do set
    # DEATH_PAYOFFS (ela nao dreno/gancha vida por morte de outrem).
    # Sem payoff numerico modelavel alem do proprio contador (ver
    # comentario em GameState) - rastreado por transparencia de dado.
    if state.has("Elenda, the Dusk Rose"):
        state.elenda_counters += _times(state, is_vampire_source=True)
    for payoff in DEATH_PAYOFFS:
        if not state.has(payoff):
            continue
        is_vamp_source = is_vampire(payoff)
        times = _times(state, is_vampire_source=is_vamp_source)
        drain_amt, gain_amt = DEATH_PAYOFF_FORMULAS[payoff]
        for _ in range(times):
            state.death_trigger_events += 1
            if drain_amt:
                lose_life_opponent(state, drain_amt, log, source=payoff)
            if gain_amt:
                gain_life(state, gain_amt, log, source=payoff)
        _log_doubling(state, times)
        log.append({"trigger": "death_payoff", "card": payoff, "source": source, "times": times, "turn": state.turn})

def apply_etb(state: GameState, card: str, log: List[Dict]):
    if card == "Champion of Dusk":
        vamps = sum(1 for c in state.battlefield if is_vampire(c))
        times = _times(state)
        for _ in range(times):
            state.draw(vamps)
            state.champion_of_dusk_draws += vamps
        _log_doubling(state, times)
        log.append({"trigger": "champion_of_dusk", "vamps": vamps, "times": times, "turn": state.turn})
    elif card == "Bastion of Remembrance":
        # "When this enchantment enters, create a 1/1 white Human
        # Soldier creature token." Achado real 2026-08-27: o ETB nunca
        # era modelado (so o drain passivo, ja adicionado em
        # DEATH_PAYOFF_FORMULAS). Fonte nao-criatura -> sem dobra do
        # Roaming Throne, mas SUJEITO aos dobradores de token
        # (Anointed Procession/Mondrak).
        n = token_multiplier(state)
        for _ in range(n):
            state.tokens.append("Human Soldier Token")
            state.battlefield.append("Human Soldier Token")
        state.bastion_of_remembrance_tokens += n
        on_creature_enters(state, log, "Human Soldier Token", count=n)
        log.append({"trigger": "bastion_of_remembrance_etb", "tokens": n, "turn": state.turn})
    elif card == "Emeritus of Woe":
        # Achado real 2026-08-27 (usuario: "o Emeritus of Woe tem o
        # Demonic Tutor Prepared, mais um tutor!"): "This creature
        # enters prepared. (While it's prepared, you may cast a copy
        # of its spell.)" - a 1a implementacao tratou a copia como
        # GRATIS, mas o usuario corrigiu (2a rodada, achado real de
        # novo): "prepared" so' te DA PERMISSAO de conjurar a copia
        # (mesmo sem a carta fisica em maos) - o texto de lembrete NAO
        # diz "without paying its mana cost" (diferente de mecanicas
        # que sao free-cast de verdade, ex. o kicker do Aang's Journey
        # no Hei Bai) - ainda paga o custo REAL do Demonic Tutor,
        # {1}{B} = 2 mana generico neste modelo. So dispara se houver
        # mana sobrando.
        if remaining_mana(state) >= 2:
            target = _tutor_target(state)
            if target:
                state.mana_spent_this_turn += 2
                state.library.remove(target)
                state.hand.append(target)
                state.tutors_used_total += 1
                state.emeritus_of_woe_tutors += 1
                log.append({"trigger": "emeritus_of_woe_etb_tutor", "found": target, "turn": state.turn})

def do_upkeep(state: GameState, log: List[Dict]):
    # Ophiomancer: "At the beginning of each upkeep, if you control no
    # Snakes, create a 1/1 black Snake creature token with deathtouch."
    # Achado real 2026-08-27: 100% ausente apesar de tageada
    # 'token_maker' - a unica criatura deste deck com gatilho de upkeep
    # de verdade. "Each upkeep" inclui o do oponente num jogo real, mas
    # este simulador so avanca os PROPRIOS turnos (mesma limitacao ja
    # documentada pro Seedborn Muse no Hei Bai) - modelado 1x por
    # upkeep proprio, conservador.
    if state.has("Ophiomancer") and "Snake Token" not in state.battlefield:
        n = token_multiplier(state)
        for _ in range(n):
            state.tokens.append("Snake Token")
            state.battlefield.append("Snake Token")
        state.ophiomancer_snakes_created += n
        on_creature_enters(state, log, "Snake Token", count=n)
        log.append({"trigger": "ophiomancer_upkeep", "tokens": n, "turn": state.turn})

def do_urzas_saga_chapter_check(state: GameState, log: List[Dict]):
    # Urza's Saga: "As this Saga enters and after your draw step, add a
    # lore counter. Sacrifice after III." Capitulo I (na entrada) e II
    # (proximo draw step) so dao habilidades ativadas de baixo valor
    # (mana incolor de qualquer jeito, Construct que exige pagar {2}+
    # tap toda vez - engine de "1 ativada por turno" que este
    # simulador nao tem em lugar nenhum, deferido). Capitulo III
    # (2o draw step depois de entrar) e' um tutor real e alto valor:
    # "Search your library for an artifact card with mana cost {0} or
    # {1}, put it onto the battlefield, then shuffle" - e' o momento
    # em que a Saga se sacrifica (para de produzir mana a partir daqui).
    # Achado real 2026-08-27: 100% ausente, tratada so como terreno
    # incolor fixo pro resto do jogo (nunca parava de produzir mana,
    # nunca buscava nada).
    if state.urzas_saga_entered_turn is None:
        return
    if state.turn != state.urzas_saga_entered_turn + 2:
        return
    if "Urza's Saga" not in state.battlefield:
        return
    pool = [c for c in state.library if C(c).type == "Artifact" and C(c).mv <= 1]
    if pool:
        target = max(pool, key=lambda c: C(c).mv)
        state.library.remove(target)
        state.battlefield.append(target)
        state.urzas_saga_tutors += 1
        log.append({"trigger": "urzas_saga_chapter3", "found": target, "turn": state.turn})
    state.battlefield.remove("Urza's Saga")
    log.append({"trigger": "urzas_saga_sacrificed", "turn": state.turn})

def do_end_step(state: GameState, log: List[Dict]):
    # Unholy Annex (a metade barata do Room, ja corrigido o mv real
    # nesta rodada - achado real: estava 8, deveria ser 3): "At the
    # beginning of your end step, draw a card. If you control a Demon,
    # each opponent loses 2 life and you gain 2 life. Otherwise, you
    # lose 2 life." Achado real 2026-08-27: mesmo agora castavel (mv
    # corrigido), nunca tinha nenhum efeito implementado. "You lose 2
    # life" na clausula sem Demon nao tem onde acumular - este
    # simulador nao rastreia vida propria real (mesma convencao de
    # Champion of Dusk/Vampiric Tutor, ja documentada) - so a compra +
    # a clausula COM Demon sao modeladas (drain/gain reais).
    if state.has("Unholy Annex // Ritual Chamber"):
        state.draw(1)
        state.unholy_annex_draws += 1
        # Achado real 2026-08-28 (auditoria de checklist ampliada): a
        # condicao real e' "if you control a Demon" - a versao anterior so
        # checava vito_fanatic_demons_created (um contador CUMULATIVO,
        # nao "controla agora"), ignorando que a propria Ritual Chamber
        # (ver try_unlock_rooms) cria um Demon de verdade que satisfaz essa
        # condicao por si so, sem depender do Vito Fanatic.
        if controls_a_demon(state):
            lose_life_opponent(state, 2, log, source="unholy_annex")
            gain_life(state, 2, log, source="unholy_annex")
        log.append({"trigger": "unholy_annex_endstep", "turn": state.turn})

    # Emeritus of Woe: "At the beginning of your end step, if two or
    # more creatures died this turn, this creature becomes prepared."
    # A copia do Demonic Tutor (ainda pagando {1}{B}=2, ver
    # try_emeritus_prepared_tutor) e' consumida em ate 2 janelas do
    # proximo turno (fim do main_phase inicial, e de novo depois da
    # mana extra do sac_loop). Este deck sacrifica 2 tokens/turno com
    # facilidade (sac_loop), entao essa condicao e' bem alcancavel.
    if state.has("Emeritus of Woe") and state.creatures_died_this_turn >= 2:
        state.emeritus_prepared = True
        log.append({"trigger": "emeritus_of_woe_prepared", "turn": state.turn})

def sac_loop(state: GameState, log: List[Dict]):
    # Ate 2 sacrificios por turno (ver docstring), consumindo tokens de
    # Vampiro disponiveis, se houver pelo menos 1 sac outlet em campo.
    free_outlets = [c for c in state.battlefield if c in SAC_OUTLETS]
    # Achado real 2026-08-27 (auditoria do resto do deck): Indulgent
    # Aristocrat ("{2}, Sacrifice a creature: put a +1/+1 counter on
    # each Vampire you control") e' um outlet de sacrificio real, so
    # que PAGO (diferente de Viscera Seer/Goblin Bombardment, que sao
    # de graca) - nunca era considerado, mesmo so' importando no caso
    # estreito de nenhum outlet livre estar em campo (o proprio +1/+1
    # counter continua sem payoff numerico, ver Cordial Vampire -
    # o valor real aqui e' desbloquear os death payoffs via sacrificio
    # quando nao ha outro jeito).
    has_paid_outlet = state.has("Indulgent Aristocrat")
    if not free_outlets and not has_paid_outlet:
        return
    if not state.tokens:
        return
    n = min(2, len(state.tokens))
    for i in range(n):
        if not state.tokens:
            break
        if not free_outlets:
            if remaining_mana(state) < 2:
                break
            state.mana_spent_this_turn += 2
            log.append({"action": "indulgent_aristocrat_sac_cost", "turn": state.turn})
        popped = state.tokens.pop()
        state.battlefield.remove(popped)
        state.creatures_sacrificed_total += 1
        state.creatures_died_this_turn += 1
        if "Ashnod's Altar" in state.battlefield:
            state.mana_spent_this_turn -= 2  # +2 mana efetivo pro resto do turno
        elif "Phyrexian Altar" in state.battlefield:
            state.mana_spent_this_turn -= 1
        elif "Phyrexian Tower" in state.battlefield:
            # Achado real 2026-08-27: "{T}, Sacrifice a creature: Add
            # {B}{B}" - e' um terreno NORMAL (ja conta +1 mana generico
            # em total_mana() so por estar em campo), entao usar esta
            # habilidade EM VEZ do {T}: Add C normal (mesmo tap, mesma
            # terra) da um ganho LIQUIDO de +1 (2 ganhos - 1 perdido do
            # tap normal que nao rola mais esse turno), nao +2.
            state.mana_spent_this_turn -= 1
        # Skullclamp: achado real 2026-08-27 - "equipped creature gets
        # +1/-1. Whenever equipped creature dies, draw two cards." So
        # UM sacrificio por turno pode estar "equipado" (custo real de
        # reequipar {1} a cada novo corpo, ja que o Equipment sobrevive
        # a morte da criatura anterior) - modelado no PRIMEIRO
        # sacrificio do turno, se houver mana pro equip.
        if i == 0 and state.has("Skullclamp") and remaining_mana(state) >= 1:
            state.mana_spent_this_turn += 1
            state.draw(2)
            state.skullclamp_draws += 2
            log.append({"trigger": "skullclamp_draw", "turn": state.turn})
        # Pitiless Plunderer: achado real 2026-08-27 - "Whenever
        # ANOTHER creature you control dies, create a Treasure token."
        # Nao e' mana automatica (a tag 'ramp' + produces antiga
        # estava ERRADA, ele nao tem habilidade de mana propria) - so
        # gera valor quando algo MORRE de verdade. Treasure agora e' um
        # token DE VERDADE (create_treasure_and_crack, achado real
        # 2026-08-27 seguinte: dispara Caretaker's Talent tambem, antes
        # era so' um bonus de mana abstrato), fonte nao-criatura -> sem
        # dobra do Roaming Throne, mas sujeito ao dobrador de token.
        if state.has("Pitiless Plunderer"):
            t = token_multiplier(state)
            create_treasure_and_crack(state, log, t, source="pitiless_plunderer")
            state.pitiless_plunderer_treasures += t
        _apply_death_payoffs(state, log, source="sac_loop")
        if state.has("Vito, Fanatic of Aclazotz"):
            state.vito_fanatic_stage_this_turn += 1
            stage = state.vito_fanatic_stage_this_turn
            if stage == 1:
                gain_life(state, 2, log, source="vito_fanatic")
            elif stage == 2:
                lose_life_opponent(state, 2, log, source="vito_fanatic")
            elif stage == 3:
                n = token_multiplier(state)
                # So' state.battlefield, NAO state.tokens - achado real
                # 2026-08-27: um 4/3 flying e' o bode fodder ERRADO
                # (um jogador real prefere sacrificar Vampire Tokens
                # 1/1, ja disponiveis) - fica fora do pool descartavel
                # de proposito.
                for _ in range(n):
                    state.battlefield.append("Vampire Demon Token")
                state.vito_fanatic_demons_created += n
                state.vito_fanatic_stage_this_turn = 0
                on_creature_enters(state, log, "Vampire Demon Token", count=n)

def combat_step(state: GameState, log: List[Dict]):
    if not state.commander_in_play or state.turn <= state.commander_cast_turn:
        return  # summoning sickness no turno em que entrou
    state.edgar_attack_turns += 1
    vamps_in_play = sum(1 for c in state.battlefield if is_vampire(c))
    times = _times(state)
    for _ in range(times):
        state.edgar_attack_counters_total += vamps_in_play
    _log_doubling(state, times)
    log.append({"trigger": "edgar_attack_counters", "vamps": vamps_in_play, "times": times, "turn": state.turn})

    if state.has("Sanctum Seeker"):
        # Achado real 2026-08-27 (auditoria de tokens): "Whenever A
        # VAMPIRE you control attacks" - gatilho POR vampiro atacante,
        # nao um trigger unico por combate. Este simulador assume que
        # TODOS os vampiros atacam desimpedidos (mesma premissa que ja
        # escala o contador de ataque do proprio Edgar por
        # vamps_in_play) - a versao anterior disparava so 1x por
        # combate, ignorando essa escala (e' o mesmo bug que os tokens
        # da Eminence nunca contarem pra vamps_in_play - agora que
        # entram em state.battlefield, isso tambem corrige a contagem
        # aqui).
        times2 = _times(state)
        n_triggers = vamps_in_play * times2
        for _ in range(n_triggers):
            state.sanctum_seeker_drains += 1
            lose_life_opponent(state, 1, log, source="sanctum_seeker")
            gain_life(state, 1, log, source="sanctum_seeker")
        _log_doubling(state, times2)
        log.append({"trigger": "sanctum_seeker", "vamps": vamps_in_play, "times": times2, "turn": state.turn})

    if state.has("Clavileño, First of the Blessed"):
        times3 = _times(state)
        state.clavileno_triggers += times3
        _log_doubling(state, times3)
        log.append({"trigger": "clavileno", "times": times3, "turn": state.turn})

    if state.has("Stensian Sanguinist // Exsanguinate"):
        # "Whenever you attack, target attacking creature gains
        # deathtouch... whenever THAT creature deals combat damage to
        # a player, this creature becomes prepared." Achado real
        # 2026-08-27 (usuario perguntou direto): este simulador nao
        # modela bloqueadores (goldfish, "Edgar ataca livre" ja e' a
        # premissa de todo o combat_step) - qualquer criatura atacante
        # conecta sem oposicao, entao a condicao "dealt combat damage"
        # e' praticamente garantida sempre que ha combate. Nao precisa
        # da propria Stensian atacar - so precisa estar em campo quando
        # o ataque acontece.
        state.stensian_prepared = True
        log.append({"trigger": "stensian_sanguinist_prepared", "turn": state.turn})

# =========================================================
# TURNO
# =========================================================

def _cast_combo_piece(state: GameState, card: str, log: List[Dict]):
    state.hand.remove(card)
    state.mana_spent_this_turn += C(card).mv
    state.battlefield.append(card)
    apply_etb(state, card, log)
    if is_creature(card):
        on_creature_enters(state, log, card)
    eminence_trigger(state, card, log)
    log.append({"action": "cast_combo_piece", "card": card, "turn": state.turn})
    if all(p in state.battlefield for p in COMBO_PIECES) and state.both_combo_pieces_turn is None:
        state.both_combo_pieces_turn = state.turn
        log.append({"trigger": "both_combo_pieces_in_play", "turn": state.turn})

def combo_hunt(state: GameState, log: List[Dict]):
    missing = [p for p in COMBO_PIECES if p not in state.battlefield and p not in state.hand]

    # Diabolic Intent: busca direto pra mao, mas exige sacrificar uma
    # criatura ja em campo como custo adicional. Achado real 2026-08-27
    # (via teste de robustez, so aparece com COMBO_HUNTING_POLICY=True):
    # sac_candidates nao excluia as PROPRIAS pecas do combo - dava pra
    # sacrificar Vito, Thorn of the Dusk Rose (unica peca-criatura do
    # combo) buscando a OUTRA peca, autodestrutivo e causava crash
    # depois. Corrigido; e' o mesmo `_pay_diabolic_intent_cost()` usado
    # pela politica default agora (achado real 2026-08-27, usuario:
    # "pode tb ser sacrificado pro Diabolic Intent" - prioriza token da
    # Eminence disponivel sobre criatura nomeada de verdade).
    if missing and "Diabolic Intent" in state.hand and can_cast(state, "Diabolic Intent") \
            and _diabolic_intent_has_fodder(state):
        state.hand.remove("Diabolic Intent")
        state.mana_spent_this_turn += C("Diabolic Intent").mv
        state.graveyard.append("Diabolic Intent")
        _pay_diabolic_intent_cost(state, log)
        target = missing[0]
        state.library.remove(target)
        state.hand.append(target)
        state.tutors_used_total += 1
        log.append({"action": "diabolic_intent", "found": target, "turn": state.turn})
        missing = [p for p in COMBO_PIECES if p not in state.battlefield and p not in state.hand]

    # Vampiric Tutor: busca pro topo da biblioteca (nao pra mao direto) -
    # a proxima compra normal (inicio do proximo turno) pega a carta.
    if missing and "Vampiric Tutor" in state.hand and can_cast(state, "Vampiric Tutor"):
        state.hand.remove("Vampiric Tutor")
        state.mana_spent_this_turn += C("Vampiric Tutor").mv
        state.graveyard.append("Vampiric Tutor")
        target = missing[0]
        state.library.remove(target)
        state.library.insert(0, target)
        state.tutors_used_total += 1
        log.append({"action": "vampiric_tutor", "found": target, "turn": state.turn})

    # Conjura qualquer peca do combo que ja esteja na mao, com prioridade
    # sobre o resto da mao (loop generico do main_phase abaixo so pega o
    # que sobrar).
    for piece in COMBO_PIECES:
        if piece in state.hand and can_cast(state, piece):
            _cast_combo_piece(state, piece, log)

def cast_available_spells(state: GameState, log: List[Dict]):
    # Extraido de main_phase() (achado real 2026-08-27, usuario: "faca a
    # carta por carta do Markov") pra poder ser chamado de NOVO depois
    # do sac_loop() - a mana dos altares (Ashnod's/Phyrexian) e agora
    # tambem do Pitiless Plunderer (Treasures) so fica disponivel
    # DEPOIS que o sac_loop roda, mas o sac_loop so processa tokens
    # CRIADOS neste mesmo turno (pela Eminence durante o main_phase) -
    # ou seja, essa mana bonus nunca tinha CHANCE de ser gasta em nada:
    # o turno so tinha 1 passada de conjuracao, antes do sac_loop
    # sequer rodar. Corrigido chamando esta funcao de novo depois do
    # sac_loop em play_turn(), pra essa mana extra virar spells de
    # verdade em vez de ser descartada no reset do proximo turno.
    for _ in range(8):
        castables = [c for c in state.hand if c != COMMANDER and not is_land(c) and can_cast(state, c)
                     # Diabolic Intent exige sacrificio como custo
                     # ADICIONAL obrigatorio - sem fodder disponivel a
                     # magica nao pode ser conjurada de verdade.
                     and (c != "Diabolic Intent" or _diabolic_intent_has_fodder(state))
                     and c not in EXCLUDE_BLIND_CAST]
        if not castables:
            break
        castables.sort(key=lambda c: C(c).mv)
        choice = castables[0]
        if has_tag(choice, "ramp"):
            state.ramp_pieces_cast += 1
        state.hand.remove(choice)
        state.mana_spent_this_turn += C(choice).mv
        if C(choice).type in ("Instant", "Sorcery"):
            state.graveyard.append(choice)
            # Achado real 2026-08-27 (usuario: "Vc contabilizou a
            # eminence... o Emeritus of Woe tem o Demonic Tutor
            # Prepared, mais um tutor!"): reconferindo o resto do
            # motor de tutor, achei que Vampiric Tutor/Diabolic Intent
            # SO tinham busca de verdade dentro de combo_hunt() (gated
            # por COMBO_HUNTING_POLICY=False por padrao) - na politica
            # DEFAULT (o batch oficial reportado ao usuario), os 2
            # eram conjurados as cegas sem NENHUM efeito de busca.
            # Corrigido aqui tambem, pra qualquer politica.
            if choice == "Vampiric Tutor":
                target = _tutor_target(state)
                if target:
                    state.library.remove(target)
                    state.library.insert(0, target)
                    state.tutors_used_total += 1
                    log.append({"action": "vampiric_tutor", "found": target, "turn": state.turn})
            elif choice == "Diabolic Intent":
                _pay_diabolic_intent_cost(state, log)
                target = _tutor_target(state)
                if target:
                    state.library.remove(target)
                    state.hand.append(target)
                    state.tutors_used_total += 1
                    log.append({"action": "diabolic_intent", "found": target, "turn": state.turn})
            elif choice == "Plumb the Forbidden":
                # Achado real 2026-08-27 (auditoria do resto do deck):
                # "As an additional cost to cast this spell, you may
                # sacrifice one or more creatures. When you do, copy
                # this spell for each creature sacrificed. You draw a
                # card and lose 1 life [por copia]." 100% ausente -
                # tageada 'draw' mas nunca implementada, conjurada as
                # cegas sem nenhum efeito. Sacrifica TODOS os tokens
                # disponiveis (greedy, mesma logica do resto do motor)
                # - cada sacrificio TAMBEM dispara os death payoffs
                # (Zulaport/Blood Artist/etc), igual o sac_loop.
                n_sac = len(state.tokens)
                for _ in range(n_sac):
                    popped = state.tokens.pop()
                    state.battlefield.remove(popped)
                    state.creatures_sacrificed_total += 1
                    state.creatures_died_this_turn += 1
                    _apply_death_payoffs(state, log, source="plumb_the_forbidden")
                state.draw(1 + n_sac)
                state.plumb_the_forbidden_draws += 1 + n_sac
                log.append({"action": "plumb_the_forbidden", "sacrificed": n_sac, "drew": 1 + n_sac, "turn": state.turn})
            elif choice == "Sevinne's Reclamation":
                # Achado real 2026-08-27: "Return target permanent card
                # MV<=3 from graveyard to battlefield" - 100% ausente.
                # Baixo valor esperado (poucas criaturas morrem por
                # NOME neste simulador, so via custo do Diabolic Intent
                # sem token disponivel) mas nao devia ser conjurada as
                # cegas sem efeito - agora tenta de verdade.
                pool = [c for c in state.graveyard if C(c).type != "Instant" and C(c).type != "Sorcery" and C(c).mv <= 3]
                if pool:
                    target = max(pool, key=lambda c: C(c).mv)
                    state.graveyard.remove(target)
                    state.battlefield.append(target)
                    apply_etb(state, target, log)
                    if is_creature(target):
                        on_creature_enters(state, log, target)
                    state.sevinnes_reclamation_returns += 1
                    log.append({"action": "sevinnes_reclamation", "found": target, "turn": state.turn})
            elif choice == "Bloodline Bidding":
                # Achado real 2026-08-27: "Choose a creature type.
                # Return all creature cards of the chosen type from
                # your graveyard to the battlefield" - 100% ausente.
                # Escolhe Vampire (tema do deck) - baixo volume esperado
                # pela mesma razao do Sevinne's Reclamation, mas real
                # quando acontece (reanima TODOS de uma vez, sem limite
                # de MV).
                targets = [c for c in state.graveyard if is_creature(c) and is_vampire(c)]
                for target in targets:
                    state.graveyard.remove(target)
                    state.battlefield.append(target)
                    apply_etb(state, target, log)
                    on_creature_enters(state, log, target)
                    state.bloodline_bidding_returns += 1
                if targets:
                    log.append({"action": "bloodline_bidding", "found": targets, "turn": state.turn})
        else:
            state.battlefield.append(choice)
            apply_etb(state, choice, log)
            if is_creature(choice):
                on_creature_enters(state, log, choice)
        eminence_trigger(state, choice, log)
        log.append({"action": "cast", "card": choice, "turn": state.turn})

    if all(p in state.battlefield for p in COMBO_PIECES) and state.both_combo_pieces_turn is None:
        state.both_combo_pieces_turn = state.turn
        log.append({"trigger": "both_combo_pieces_in_play", "turn": state.turn})

def do_black_market_connections(state: GameState, log: List[Dict]):
    # "At the beginning of your first main phase, choose one or more -
    # Sell Contraband (Treasure, lose 1 life), Buy Information (draw,
    # lose 2 life), Hire a Mercenary (3/2 Shapeshifter changeling
    # token, lose 3 life)." Achado real 2026-08-27 (usuario pediu
    # explicitamente): por DEFAULT so' o modo mais barato (Sell
    # Contraband, 1 Treasure) - a versao anterior escolhia os 3 modos
    # de graca todo turno so' porque vida nao e' rastreada aqui, o que
    # e' otimista demais (perder 6 vida/turno de forma automatica nao
    # e' um piloto realista, mesmo sem numero exato de vida neste
    # modelo). O Treasure agora e' um token DE VERDADE (ver
    # create_treasure_and_crack) - dispara Caretaker's Talent e
    # qualquer outro gatilho de token, em vez de ser so' um bonus de
    # mana abstrato.
    if not state.has("Black Market Connections"):
        return
    t = token_multiplier(state)
    create_treasure_and_crack(state, log, t, source="black_market_connections")
    state.black_market_treasures += t

def main_phase(state: GameState, log: List[Dict]):
    do_black_market_connections(state, log)
    if COMBO_HUNTING_POLICY:
        combo_hunt(state, log)

    if not state.commander_in_play and state.commander_cast_count == 0 and can_cast(state, COMMANDER):
        state.mana_spent_this_turn += commander_effective_mv(state)
        state.battlefield.append(COMMANDER)
        state.commander_in_play = True
        state.commander_cast_turn = state.turn
        state.commander_cast_count += 1
        on_creature_enters(state, log, COMMANDER)
        log.append({"action": "cast_commander", "turn": state.turn})

    try_cabal_coffers(state, log)
    try_adanto(state, log)
    try_unlock_rooms(state, log)
    cast_available_spells(state, log)
    try_emeritus_prepared_tutor(state, log)
    try_stensian_prepared_exsanguinate(state, log)

def try_emeritus_prepared_tutor(state: GameState, log: List[Dict]):
    # Emeritus of Woe "prepared" (setado no do_end_step do turno
    # anterior): "you may cast a copy of its spell" - so' PERMISSAO,
    # ainda paga o custo real do Demonic Tutor ({1}{B}=2, achado real
    # 2026-08-27, usuario corrigiu: "o tutor... nao e' gratuito, custa
    # 2cmc pra cast"). Chamado 2x por turno (fim do main_phase E depois
    # da 2a passada de cast_available_spells no play_turn, ver la) pra
    # tambem poder usar mana sobrando do sac_loop (Ashnod's/Treasure) -
    # mesmo padrao ja usado pro resto do motor.
    if state.emeritus_prepared and remaining_mana(state) >= 2:
        target = _tutor_target(state)
        if target:
            state.mana_spent_this_turn += 2
            state.library.remove(target)
            state.hand.append(target)
            state.tutors_used_total += 1
            state.emeritus_of_woe_tutors += 1
            log.append({"trigger": "emeritus_of_woe_prepared_tutor", "found": target, "turn": state.turn})
            state.emeritus_prepared = False

def try_stensian_prepared_exsanguinate(state: GameState, log: List[Dict]):
    # Stensian Sanguinist "prepared" (setado em combat_step, ver
    # acima). Exsanguinate ({X}{B}{B}, "each opponent loses X life, you
    # gain life equal") e' um mana sink puro e um finalizador em
    # potencial. 2 achados reais aqui, os 2 apontados pelo usuario:
    # (1) 2026-08-27 - a copia AINDA paga o custo real (nao e'
    # free-cast, mesmo erro ja corrigido no Emeritus of Woe), entao
    # X = mana sobrando menos o {B}{B} fixo, so' conjura se X>0.
    # (2) 2026-08-27 (correcao seguinte) - a 1a versao so chamava esta
    # funcao ANTES do combate (achando que "prepared" so' liberava no
    # turno SEGUINTE, por analogia errada com o Emeritus of Woe, que de
    # fato so libera no fim do end step). Mas Stensian fica prepared
    # DURANTE o combate, e Magic real tem uma 2a main phase logo depois
    # do combate NO MESMO turno - corrigido chamando esta funcao
    # tambem logo apos combat_step() em play_turn(). "Prepared" nao
    # expira no fim do turno (texto de lembrete nao diz isso), entao as
    # chamadas anteriores ao combate continuam validas como fallback
    # pro turno seguinte se nao sobrar mana nem na 2a main phase.
    if not state.stensian_prepared:
        return
    if color_sources(state, "B") < 1 or remaining_mana(state) < 2:
        return
    x = remaining_mana(state) - 2
    if x <= 0:
        return
    state.mana_spent_this_turn += 2 + x
    lose_life_opponent(state, x, log, source="exsanguinate")
    gain_life(state, x, log, source="exsanguinate")
    state.exsanguinate_casts += 1
    state.exsanguinate_x_total += x
    state.stensian_prepared = False
    log.append({"trigger": "exsanguinate_prepared", "x": x, "turn": state.turn})

def play_turn(state: GameState, turn: int, game_log: List[List[Dict]]):
    state.turn = turn
    state.land_played = False
    state.mana_spent_this_turn = 0
    state.vito_fanatic_stage_this_turn = 0
    state.welcoming_vampire_trigger_pending = 0
    state.caretakers_talent_trigger_pending = 0
    state.creatures_died_this_turn = 0
    state.tapped_lands_this_turn = 0
    log = []

    do_upkeep(state, log)
    state.draw(1)
    do_urzas_saga_chapter_check(state, log)
    play_land(state, log)
    main_phase(state, log)
    sac_loop(state, log)
    cast_available_spells(state, log)  # mana extra de altares/Treasures do sac_loop, ver docstring de cast_available_spells
    try_unlock_rooms(state, log)
    try_emeritus_prepared_tutor(state, log)
    try_stensian_prepared_exsanguinate(state, log)
    welcoming_vampire_check(state, log)
    caretakers_talent_check(state, log)
    combat_step(state, log)
    try_minas_tirith(state, log)
    # 2a main phase (achado real 2026-08-27, usuario corrigiu de novo:
    # "Os spells preparados que sao preparados no combate podem ser
    # cast na second main phase, nao precisam esperar um turno") - o
    # turno de Magic real tem main phase 1 -> combate -> main phase 2
    # -> end step, TUDO no mesmo turno. Stensian Sanguinist fica
    # prepared DURANTE o combate (ver combat_step acima) - errado supor
    # que so' da pra usar no turno seguinte, quando na real ha uma 2a
    # main phase disponivel na hora, no mesmo turno, com qualquer mana
    # que ainda estiver sobrando. As chamadas de try_* la em cima (pre
    # combate) continuam validas como fallback: "prepared" nao expira
    # no fim do turno (o texto de lembrete nao diz isso), entao se nao
    # sobrar mana nem aqui, o proximo turno ainda tenta de novo.
    try_stensian_prepared_exsanguinate(state, log)
    do_end_step(state, log)

    game_log.append(log)

# =========================================================
# SIMULACAO
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
        state.draw(7)
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

    game_log = []
    for t in range(1, turns + 1):
        play_turn(state, t, game_log)

    return {
        "seed": seed,
        "mulligans": mulligans,
        "commander_cast_turn": state.commander_cast_turn,
        "eminence_tokens_created": state.eminence_tokens_created,
        "adanto_tokens_created": state.adanto_tokens_created,
        "minas_tirith_draws": state.minas_tirith_draws,
        "edgar_attack_counters_total": state.edgar_attack_counters_total,
        "edgar_attack_turns": state.edgar_attack_turns,
        "drain_total": state.drain_total,
        "lifegain_total": state.lifegain_total,
        "creatures_sacrificed_total": state.creatures_sacrificed_total,
        "death_trigger_events": state.death_trigger_events,
        "champion_of_dusk_draws": state.champion_of_dusk_draws,
        "welcoming_vampire_draws": state.welcoming_vampire_draws,
        "sanctum_seeker_drains": state.sanctum_seeker_drains,
        "vito_fanatic_demons_created": state.vito_fanatic_demons_created,
        "clavileno_triggers": state.clavileno_triggers,
        "combo_active": state.combo_active,
        "combo_active_turn": state.combo_active_turn,
        "combo_enabler": state.combo_enabler,
        "both_combo_pieces_turn": state.both_combo_pieces_turn,
        "roaming_throne_in_play": state.has("Roaming Throne"),
        "roaming_throne_doublings": state.roaming_throne_doublings,
        "lands_played_total": state.lands_played_total,
        "purphoros_damage_total": state.purphoros_damage_total,
        "warleaders_call_damage_total": state.warleaders_call_damage_total,
        "ophiomancer_snakes_created": state.ophiomancer_snakes_created,
        "skullclamp_draws": state.skullclamp_draws,
        "pitiless_plunderer_treasures": state.pitiless_plunderer_treasures,
        "unholy_annex_draws": state.unholy_annex_draws,
        "bastion_of_remembrance_tokens": state.bastion_of_remembrance_tokens,
        "elenda_counters": state.elenda_counters,
        "token_doubler_events": state.token_doubler_events,
        "tutors_used_total": state.tutors_used_total,
        "emeritus_of_woe_tutors": state.emeritus_of_woe_tutors,
        "exsanguinate_casts": state.exsanguinate_casts,
        "exsanguinate_x_total": state.exsanguinate_x_total,
        "plumb_the_forbidden_draws": state.plumb_the_forbidden_draws,
        "sevinnes_reclamation_returns": state.sevinnes_reclamation_returns,
        "bloodline_bidding_returns": state.bloodline_bidding_returns,
        "urzas_saga_tutors": state.urzas_saga_tutors,
        "caretakers_talent_draws": state.caretakers_talent_draws,
        "black_market_treasures": state.black_market_treasures,
        "ramp_pieces_cast": state.ramp_pieces_cast,
        "awakening_hall_unlocked": state.awakening_hall_unlocked,
        "awakening_hall_reanimated": state.awakening_hall_reanimated,
        "ritual_chamber_unlocked": state.ritual_chamber_unlocked,
        "ritual_chamber_demons_created": state.ritual_chamber_demons_created,
    }

def run_batch(n=2000, turns=8, out_jsonl="edgar_markov_v1_runs.jsonl", seed_base=6000000):
    import json as _json, statistics
    results = [simulate_one(seed_base + i, turns) for i in range(n)]
    with open(out_jsonl, "w") as f:
        for r in results:
            f.write(_json.dumps(r) + "\n")

    cmd_turns = [r["commander_cast_turn"] for r in results if r["commander_cast_turn"] is not None]
    never = n - len(cmd_turns)
    combo_turns = [r["combo_active_turn"] for r in results if r["combo_active"]]

    print(f"=== Edgar Markov Goldfish v1 - n={n}, turns={turns} ===")
    print(f"Avg mulligans: {sum(r['mulligans'] for r in results)/n:.2f}")
    if cmd_turns:
        print(f"Turno medio de conjuracao do Edgar Markov: {statistics.mean(cmd_turns):.2f} | mediana: {statistics.median(cmd_turns)}")
    print(f"Nunca conjurado em {turns} turnos: {100*never/n:.1f}%")
    print(f"Avg tokens de Vampiro via Eminence: {sum(r['eminence_tokens_created'] for r in results)/n:.2f}")
    print(f"Avg tokens de Vampiro via Adanto (agora despachado): {sum(r['adanto_tokens_created'] for r in results)/n:.2f}")
    print(f"Avg compras via Minas Tirith (agora despachado): {sum(r['minas_tirith_draws'] for r in results)/n:.2f}")
    print(f"Avg turnos em que Edgar atacou: {sum(r['edgar_attack_turns'] for r in results)/n:.2f}")
    print(f"Avg contadores +1/+1 distribuidos (ataque do Edgar): {sum(r['edgar_attack_counters_total'] for r in results)/n:.2f}")
    print(f"Avg drain_total (proxy de vida perdida pelo oponente): {sum(r['drain_total'] for r in results)/n:.2f}")
    print(f"Avg lifegain_total (proxy de vida ganha): {sum(r['lifegain_total'] for r in results)/n:.2f}")
    print(f"Avg criaturas sacrificadas: {sum(r['creatures_sacrificed_total'] for r in results)/n:.2f}")
    print(f"Avg gatilhos de morte (death payoffs): {sum(r['death_trigger_events'] for r in results)/n:.2f}")
    print(f"Avg compras via Champion of Dusk: {sum(r['champion_of_dusk_draws'] for r in results)/n:.2f}")
    print(f"Avg compras via Welcoming Vampire: {sum(r['welcoming_vampire_draws'] for r in results)/n:.2f}")
    print(f"Avg drains via Sanctum Seeker: {sum(r['sanctum_seeker_drains'] for r in results)/n:.2f}")
    print(f"Avg Demons criados via Vito Fanatic (3o estagio): {sum(r['vito_fanatic_demons_created'] for r in results)/n:.2f}")
    print(f"Avg gatilhos de Clavileno (sem efeito numerico extra modelado): {sum(r['clavileno_triggers'] for r in results)/n:.2f}")
    print(f"Avg dano via Purphoros: {sum(r['purphoros_damage_total'] for r in results)/n:.2f}")
    print(f"Avg dano via Warleader's Call: {sum(r['warleaders_call_damage_total'] for r in results)/n:.2f}")
    print(f"Avg Snakes via Ophiomancer: {sum(r['ophiomancer_snakes_created'] for r in results)/n:.2f}")
    print(f"Avg compras via Skullclamp: {sum(r['skullclamp_draws'] for r in results)/n:.2f}")
    print(f"Avg Treasures via Pitiless Plunderer: {sum(r['pitiless_plunderer_treasures'] for r in results)/n:.2f}")
    print(f"Avg compras via Unholy Annex (end step): {sum(r['unholy_annex_draws'] for r in results)/n:.2f}")
    print(f"Avg tokens via Bastion of Remembrance ETB: {sum(r['bastion_of_remembrance_tokens'] for r in results)/n:.2f}")
    print(f"Avg contadores da Elenda (passivo, sem payoff numerico alem do dado): {sum(r['elenda_counters'] for r in results)/n:.2f}")
    print(f"Avg eventos de dobra de token (Anointed Procession/Mondrak): {sum(r['token_doubler_events'] for r in results)/n:.2f}")
    print(f"Avg tutores usados no total (Vampiric Tutor/Diabolic Intent/Emeritus of Woe): {sum(r['tutors_used_total'] for r in results)/n:.2f}")
    print(f"Avg tutores via Emeritus of Woe (Demonic Tutor prepared): {sum(r['emeritus_of_woe_tutors'] for r in results)/n:.2f}")
    print(f"Avg Exsanguinate conjurados (Stensian Sanguinist prepared): {sum(r['exsanguinate_casts'] for r in results)/n:.2f}")
    print(f"Avg X total do Exsanguinate (drain/gain): {sum(r['exsanguinate_x_total'] for r in results)/n:.2f}")
    print(f"Avg compras via Plumb the Forbidden: {sum(r['plumb_the_forbidden_draws'] for r in results)/n:.2f}")
    print(f"Avg reanimacoes via Sevinne's Reclamation: {sum(r['sevinnes_reclamation_returns'] for r in results)/n:.2f}")
    print(f"Avg reanimacoes via Bloodline Bidding: {sum(r['bloodline_bidding_returns'] for r in results)/n:.2f}")
    print(f"Avg tutores via Urza's Saga (capitulo III): {sum(r['urzas_saga_tutors'] for r in results)/n:.2f}")
    print(f"Avg compras via Caretaker's Talent (base, token ETB): {sum(r['caretakers_talent_draws'] for r in results)/n:.2f}")
    print(f"Avg Treasures via Black Market Connections: {sum(r['black_market_treasures'] for r in results)/n:.2f}")
    ah_unlocked = sum(1 for r in results if r["awakening_hall_unlocked"])
    if ah_unlocked:
        print(f"Awakening Hall destrancada em {100*ah_unlocked/n:.1f}% dos jogos, "
              f"avg criaturas reanimadas: {sum(r['awakening_hall_reanimated'] for r in results)/n:.2f}")
    rc_unlocked = sum(1 for r in results if r["ritual_chamber_unlocked"])
    if rc_unlocked:
        print(f"Ritual Chamber destrancada em {100*rc_unlocked/n:.1f}% dos jogos "
              f"(cria o Demon que habilita o bonus do proprio Unholy Annex)")
    print()
    print(f"--- Combo Exquisite Blood/Bloodthirsty Conqueror + Vito, Thorn of the Dusk Rose ---")
    print(f"Partidas em que o combo montou E ligou: {100*len(combo_turns)/n:.1f}%")
    if combo_turns:
        print(f"Turno medio em que o combo liga: {statistics.mean(combo_turns):.2f} | mediana: {statistics.median(combo_turns)}")
    enablers = [r["combo_enabler"] for r in results if r["combo_active"]]
    if enablers:
        from collections import Counter
        print(f"Habilitador do combo: {dict(Counter(enablers))}")
    print()
    rt_in_play = sum(1 for r in results if r["roaming_throne_in_play"])
    print(f"Roaming Throne em campo em {100*rt_in_play/n:.1f}% dos jogos (tipo escolhido: Vampire)")
    print(f"Avg gatilhos de Vampiro dobrados por partida: {sum(r['roaming_throne_doublings'] for r in results)/n:.2f}")
    print()

    # Achado real 2026-08-28 (auditoria de checklist - metricas basicas
    # obrigatorias em TODO simulador: ramp, draw, interaction, recursion,
    # finisher/lethality - "recursion" adicionada por reforco explicito do
    # usuario apos a Correcao #10: "acrescente a variavel recursao e
    # interacao a lista de variaveis pra avaliar/medir/registrar em todos
    # os decks"). As metricas especificas de carta acima ja cobrem quase
    # tudo isso, mas nunca estavam resumidas nas categorias-base
    # explicitamente - agregando aqui pra deixar auditavel de relance, sem
    # precisar somar manualmente.
    print("--- Metricas basicas (checklist obrigatoria) ---")
    print(f"RAMP: avg pecas de rampa conjuradas (Sol Ring/Arcane Signet/Ashnod's Altar/Phyrexian Altar): "
          f"{sum(r['ramp_pieces_cast'] for r in results)/n:.2f}")
    total_draw = sum(
        r["champion_of_dusk_draws"] + r["welcoming_vampire_draws"] + r["skullclamp_draws"]
        + r["unholy_annex_draws"] + r["caretakers_talent_draws"] + r["minas_tirith_draws"]
        + r["plumb_the_forbidden_draws"]
        for r in results)
    print(f"DRAW: avg compras extras totais (soma de todos os motores - Champion of Dusk, Welcoming Vampire, "
          f"Skullclamp, Unholy Annex, Caretaker's Talent, Minas Tirith, Plumb the Forbidden): {total_draw/n:.2f}")
    print(f"INTERACTION: avg remocao conjurada de verdade: 0.00 (N/A por arquitetura - este e' um goldfish "
          f"SOLO sem oponente real pra mirar. 6 spells de remocao reais na lista (Anguished Unmaking, Get "
          f"Lost, Path to Exile, Swords to Plowshares, Vindicate, Rite of Oblivion) ficam em "
          f"EXCLUDE_BLIND_CAST de proposito - um piloto real segura remocao ate ter alvo, nunca conjura as "
          f"cegas. So Goblin Bombardment, sac outlet nao removal de fato neste motor, e' castavel; 0 e' o "
          f"resultado CORRETO, nao um bug.)")
    total_recursion = sum(
        r["sevinnes_reclamation_returns"] + r["bloodline_bidding_returns"] + r["awakening_hall_reanimated"]
        for r in results)
    print(f"RECURSION: avg cartas recuperadas do cemiterio pro campo (soma de Sevinne's Reclamation, "
          f"Bloodline Bidding, Awakening Hall): {total_recursion/n:.2f}. Tutores de biblioteca (Vampiric "
          f"Tutor/Diabolic Intent/Emeritus of Woe/Urza's Saga) NAO contam aqui - buscam da biblioteca, nao "
          f"do cemiterio, categoria diferente por definicao.")
    total_finisher_damage = sum(
        r["drain_total"] + r["purphoros_damage_total"] + r["warleaders_call_damage_total"]
        + r["exsanguinate_x_total"]
        for r in results)
    print(f"FINISHER/LETHALITY: combo infinito (Exquisite Blood/Bloodthirsty Conqueror + Vito Thorn/Enduring "
          f"Tenacity) monta e liga em {100*len(combo_turns)/n:.1f}% dos jogos"
          + (f", turno medio {statistics.mean(combo_turns):.2f}" if combo_turns else "")
          + f". Fora do combo, avg 'dano' agregado (drain_total + Purphoros + Warleader's Call + "
          f"Exsanguinate X) por partida: {total_finisher_damage/n:.2f}.")
    print()
    print(f"Logs salvos em: {out_jsonl}")
    return results

if __name__ == "__main__":
    run_batch(n=2000, turns=8)

