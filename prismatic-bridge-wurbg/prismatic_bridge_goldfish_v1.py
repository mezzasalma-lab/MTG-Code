"""
Goldfish simulator - Esika, God of the Tree // The Prismatic Bridge (5 cores - WUBRG)
Escrito e executado por Claude.

Metodologia:
- Tags de cada carta derivadas de oracle_text real (Scryfall,
  /tmp/scryfall_cache/prismatic_bridge_full.json), nao inventadas.
- Este e um simulador FOCADO, nao um goldfish completo de curva geral como
  o do Thranduil/Beorn. Escopo deliberadamente restrito ao que a pergunta
  do usuario pede: turno em que a Bridge resolve, taxa de acerto da Bridge
  em criatura/planeswalker, e sobrevivencia da Bridge/protetores sob
  remocao do oponente - especificamente pra decidir se vale incluir
  Greater Auramancy.
- NAO modelado (limitacao documentada, nao e um bug): a frente do
  comandante (Esika, God of the Tree) e sua habilidade de conceder mana de
  qualquer cor a outras lendarias; efeitos dos 11 criaturas que nao sejam
  ramp/draw/removal/counter-doubler ja tageados. O simulador so joga a
  carta "The Prismatic Bridge" (verso do MDFC) como comandante, direto do
  zone de comando.
- Correcao GRANDE 2026-08-28 (usuario: "Preciso que os counters de
  lealdade e ativacoes de planeswalker sejam sempre contabilizados, a base
  do Prismatic Bridge e essa!" - ver regra permanente categoria 12 em
  references/goldfish-sim-card-rules.md): os 17 planeswalkers da lista
  AGORA tem lealdade real rastreada (state.loyalty) e ativam uma
  habilidade real por turno (CR 606.3) - antes eram so um nome parado em
  campo depois da Bridge acertar, sem nenhum efeito. Doubling
  Season/Vorinclex (dobradores de counter) e Evolution Sage/Deepglow
  Skate/Vraska (proliferate) agora tem efeito real sobre a lealdade
  tambem. Correcao 2026-08-28 (2a rodada, regra nova de Classes/Sagas -
  "níveis"): Innkeeper's Talent agora sobe de nivel de verdade
  (try_level_up_innkeepers_talent, custo real {G}/{3}{G}) - nivel 3 dobra
  TODOS os counters (empilha com Doubling Season/Vorinclex em
  counter_doubler_multiplier), incluindo lealdade de planeswalker ao
  entrar. Ver goldfish-log.md pra detalhe completo e o que ficou
  deliberadamente deferido (estatico da Nicol Bolas, proliferate de outras
  6 fontes que precisam de hooks de cast/end-step que este arquivo ainda
  nao tem).
- NAO modelado (achado 2026-08-28, auditoria de checklist de mecanica -
  decisao consciente de escopo, nao esquecimento silencioso): as 14
  cartas tageadas "draw" que NAO sao planeswalker (Rhystic Study, etc.)
  tem a tag mas nenhum gatilho real disparado. Ficou de fora desta rodada
  por volume (14 motores, escopo comparavel a montar um goldfish completo)
  - fica pra uma rodada dedicada se o usuario quiser.
- PREMISSA NAO VALIDADA (usuario nao tem dado real, deck nunca jogado):
  taxa de tentativa de remocao por oponente por turno mirando a Bridge ou
  seus protetores. Default usado: 12% por oponente por turno, 3 oponentes
  (confirmado pelo usuario). Isso e um CHUTE razoavel pra Bracket 3
  upgraded, NAO um dado real - o resultado do teste Greater Auramancy deve
  ser lido como "dado esse chute, o efeito e X", nao como "X e a resposta
  definitiva". Ajustar REMOVAL_CHANCE_PER_OPPONENT se o usuario validar um
  numero diferente depois de jogar partidas reais.
- MODELO DE COMBATE (2026-09-24, so' no modo de resiliencia): oponentes com
  campo de criaturas (perfis go_wide/voltron/low/mixed) atacando voce e seus
  planeswalkers, bloqueio, pillowfort (A/B via `swap`), nossas remocoes com
  efeito real. Ver secao "MODELO DE COMBATE" e checklist-oraculo.md. Na
  mesma rodada: Sphinx of the Second Sun reimplementado com o oraculo real,
  All Will Be One/Atraxa (end step)/Doubling Season (fichas)/The Chain Veil
  (perda de vida) implementados, `creature_enters` unico.
"""

import random
from dataclasses import dataclass, field
from typing import Set, List, Dict, Optional

COMMANDER = "The Prismatic Bridge"
N_OPPONENTS = 3
REMOVAL_CHANCE_PER_OPPONENT = 0.12  # premissa assumida, ver docstring

# Politica de conjuracao da Bridge:
# False (default) = "cast ASAP" - conjura normal na main phase assim que
#   fica pagavel, nunca espera pra flashar (comportamento historico).
# True = "hold for flash" - se um habilitador de flash JA esta em campo,
#   segura a Bridge de proposito (nao conjura normal, mesmo pagavel) e
#   espera a janela de flash no end step alheio, especificamente pra
#   pular a rodada de remocao antes do 1o gatilho de upkeep (o plano de
#   jogo real do usuario). So muda comportamento nos jogos em que um
#   habilitador chega a estar em campo (~17% das partidas, ver auditoria).
HOLD_FOR_FLASH_POLICY = False

DECKLIST_TEXT = """
1 Alchemist's Refuge
1 All Will Be One
1 Aminatou, the Fateshifter
1 Anguished Unmaking
1 Arcane Signet
1 Arena Rector
1 Ashiok, Dream Render
1 Atraxa, Praetors' Voice
1 Blasphemous Act
1 Bloom Tender
1 Carth the Lion
1 Chromatic Lantern
1 Counterspell
1 Damn
1 Deepglow Skate
1 Delighted Halfling
1 Doubling Season
1 Dovin's Veto
1 Elspeth, Sun's Champion
1 Evolution Sage
1 Farseek
1 Farewell
1 Flux Channeler
1 Ichormoon Gauntlet
1 Inexorable Tide
1 Innkeeper's Talent
1 Kaya, Intangible Slayer
1 Liliana, Dreadhorde General
1 Mana Drain
1 Mutational Advantage
1 Narset, Parter of Veils
1 Nature's Lore
1 Nesting Grounds
1 Nicol Bolas, Dragon-God
1 Oath of Nissa
1 Oath of Teferi
1 Oko, the Ringleader
1 Paradox Haze
1 Path to Exile
1 Rhystic Study
1 Ripples of Potential
1 Sol Ring
1 Sphinx of the Second Sun
1 Sterling Grove
1 Supreme Verdict
1 Swan Song
1 Swords to Plowshares
1 Tamiyo, Compleated Sage
1 Tamiyo, Field Researcher
1 Teferi, Hero of Dominaria
1 Teferi, Temporal Archmage
1 Teferi, Time Raveler
1 Teferi, Who Slows the Sunset
1 The Chain Veil
1 The Eternal Wanderer
1 The Peregrine Dynamo
1 The World Tree
1 Three Visits
1 Toxic Deluge
1 Ugin, the Spirit Dragon
1 Urza Assembles the Titans
1 Veil of Summer
1 Void Rend
1 Vorinclex, Monstrous Raider
1 Vraska, Betrayal's Sting
1 Badlands
1 Bayou
1 Blood Crypt
1 Breeding Pool
1 Brushland
1 City of Brass
1 Command Tower
1 Emergence Zone
1 Exotic Orchard
1 Fabled Passage
1 Godless Shrine
1 Hallowed Fountain
1 Interplanar Beacon
1 Mana Confluence
1 Overgrown Tomb
1 Plateau
1 Plaza of Heroes
1 Sacred Foundry
1 Savannah
1 Scrubland
1 Snow-Covered Forest
1 Snow-Covered Island
1 Snow-Covered Mountain
1 Snow-Covered Plains
1 Snow-Covered Swamp
1 Steam Vents
1 Stomping Ground
1 Taiga
1 Temple Garden
1 Tropical Island
1 Tundra
1 Underground Sea
1 Volcanic Island
1 Watery Grave
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

# -------- Comandante (so o verso - ver limitacao no docstring) --------
add("The Prismatic Bridge", 5, "Enchantment", colors={"B", "G", "R", "U", "W"}, tags={"bridge_engine"})
add("Greater Auramancy", 2, "Enchantment", colors={"W"}, tags={"protection_shroud"})

# -------- Deck (99 cartas, geradas via Scryfall cards/collection) --------
add("Alchemist's Refuge", 0, "Land", colors={"G", "U"}, produces={"C"}, tags={"flash_enabler"})
add("All Will Be One", 5, "Enchantment", colors={"R"}, produces=set(), tags=set())
add("Aminatou, the Fateshifter", 3, "Planeswalker", colors={"B", "U", "W"}, produces=set(), tags={"draw", "planeswalker"})
add("Anguished Unmaking", 3, "Instant", colors={"B", "W"}, produces=set(), tags={"removal"})
add("Arcane Signet", 2, "Artifact", colors=set(), produces={"B", "G", "R", "U", "W"}, tags={"ramp"})
add("Arena Rector", 4, "Creature", colors={"W"}, produces=set(), tags={"creature"})
add("Ashiok, Dream Render", 3, "Planeswalker", colors={"B", "U"}, produces=set(), tags={"planeswalker"})
add("Atraxa, Praetors' Voice", 4, "Creature", colors={"B", "G", "U", "W"}, produces=set(), tags={"creature", "proliferate"})
add("Blasphemous Act", 9, "Sorcery", colors={"R"}, produces=set(), tags={"wipe"})
add("Bloom Tender", 2, "Creature", colors={"G"}, produces=set(), tags={"creature", "ramp", "bloom_tender"})
# Achado real 2026-08-28 (auditoria de checklist): oraculo real e' "Vivid -
# {T}: For each color among permanents you control, add one mana of that
# color" - escala com cores REAIS em campo, nao 5c fixo. produces=set(),
# tratada com logica propria em color_sources()/total_mana() via tag
# "bloom_tender".
add("Carth the Lion", 4, "Creature", colors={"B", "G"}, produces=set(), tags={"creature"})
add("Chromatic Lantern", 3, "Artifact", colors=set(), produces={"B", "G", "R", "U", "W"}, tags={"ramp", "lands_any_color"})
# Achado real 2026-08-28: alem do proprio {T}: Add any color (produces
# acima, correto), tem uma estatica de campo inteiro nunca implementada:
# "Lands you control have '{T}: Add one mana of any color.'" - afeta TODO
# terreno em campo, nao so ela mesma. Tag "lands_any_color" checada em
# color_sources().
add("Counterspell", 2, "Instant", colors={"U"}, produces=set(), tags={"counterspell"})
add("Damn", 2, "Sorcery", colors={"B"}, produces=set(), tags={"removal"})  # {B}{B} (cor = so' preta; o {W} e' do overload {2}{W}{W}, identidade de cor)
add("Deepglow Skate", 5, "Creature", colors={"U"}, produces=set(), tags={"counter_doubler", "creature"})
add("Delighted Halfling", 1, "Creature", colors={"G"}, produces={"C"}, tags={"creature", "ramp", "legendary_only_color"})
# Achado real 2026-08-28: "{T}: Add {C}." incondicional (produces acima),
# mas a mana colorida real e' "{T}: Add one mana of any color. Spend this
# mana only to cast a legendary spell, and that spell can't be countered" -
# so' incolor era incondicional. Tag "legendary_only_color" checada em
# color_sources() (so conta pra spells lendarios de verdade).
add("Doubling Season", 5, "Enchantment", colors={"G"}, produces=set(), tags={"counter_doubler"})
add("Dovin's Veto", 2, "Instant", colors={"U", "W"}, produces=set(), tags=set())
add("Elspeth, Sun's Champion", 6, "Planeswalker", colors={"W"}, produces=set(), tags={"planeswalker", "wipe"})
add("Evolution Sage", 3, "Creature", colors={"G"}, produces=set(), tags={"creature", "proliferate"})
add("Farseek", 2, "Sorcery", colors={"G"}, produces=set(), tags={"ramp"})
add("Farewell", 6, "Sorcery", colors={"W"}, produces=set(), tags={"wipe"})
add("Flux Channeler", 3, "Creature", colors={"U"}, produces=set(), tags={"creature", "proliferate"})
add("Ichormoon Gauntlet", 3, "Artifact", colors={"U"}, produces=set(), tags={"proliferate"})
add("Inexorable Tide", 5, "Enchantment", colors={"U"}, produces=set(), tags={"proliferate"})
add("Innkeeper's Talent", 2, "Enchantment", colors={"G"}, produces=set(), tags={"counter_doubler"})
add("Kaya, Intangible Slayer", 7, "Planeswalker", colors={"B", "W"}, produces=set(), tags={"draw", "planeswalker", "removal"})
add("Liliana, Dreadhorde General", 6, "Planeswalker", colors={"B"}, produces=set(), tags={"draw", "planeswalker", "wipe"})
add("Mana Drain", 2, "Instant", colors={"U"}, produces=set(), tags={"counterspell"})
add("Mutational Advantage", 3, "Instant", colors={"G", "U"}, produces=set(), tags={"proliferate"})
add("Narset, Parter of Veils", 3, "Planeswalker", colors={"U"}, produces=set(), tags={"planeswalker"})
add("Nature's Lore", 2, "Sorcery", colors={"G"}, produces=set(), tags={"ramp"})
add("Nesting Grounds", 0, "Land", colors=set(), produces={"C"}, tags=set())
add("Nicol Bolas, Dragon-God", 5, "Planeswalker", colors={"B", "R", "U"}, produces=set(), tags={"draw", "planeswalker", "removal"})
add("Oath of Nissa", 1, "Enchantment", colors={"G"}, produces=set(), tags=set())
# Achado real (auditoria oraculo-por-oraculo): "You may activate the
# loyalty abilities of planeswalkers you control TWICE each turn rather
# than only once" -- estatico, sempre ligado enquanto em campo, nunca
# implementado (so a metade de ETB-flicker, de baixo valor, ficaria de
# fora mesmo). Com 17 planeswalkers na lista, e' um dos maiores
# multiplicadores de valor do deck. Ver extra_pw_activation_sources().
add("Oath of Teferi", 5, "Enchantment", colors={"U", "W"}, produces=set(), tags={"double_pw_activation"})
add("Oko, the Ringleader", 4, "Planeswalker", colors={"G", "U"}, produces=set(), tags={"draw", "planeswalker"})
add("Paradox Haze", 3, "Enchantment", colors={"U"}, produces=set(), tags={"extra_upkeep"})
add("Path to Exile", 1, "Instant", colors={"W"}, produces=set(), tags={"removal"})
add("Rhystic Study", 3, "Enchantment", colors={"U"}, produces=set(), tags={"draw"})
add("Ripples of Potential", 2, "Instant", colors={"U"}, produces=set(), tags={"proliferate"})
add("Sol Ring", 1, "Artifact", colors=set(), produces={"C"}, tags={"ramp"})
add("Sphinx of the Second Sun", 8, "Creature", colors={"U"}, produces=set(), tags={"creature"})
add("Sterling Grove", 2, "Enchantment", colors={"G", "W"}, produces=set(), tags={"protection_shroud"})
add("Supreme Verdict", 4, "Sorcery", colors={"U", "W"}, produces=set(), tags={"wipe"})
add("Swan Song", 1, "Instant", colors={"U"}, produces=set(), tags=set())
add("Swords to Plowshares", 1, "Instant", colors={"W"}, produces=set(), tags={"removal"})
add("Tamiyo, Compleated Sage", 5, "Planeswalker", colors={"G", "U"}, produces=set(), tags={"draw", "planeswalker", "removal"})
add("Tamiyo, Field Researcher", 4, "Planeswalker", colors={"G", "U", "W"}, produces=set(), tags={"draw", "planeswalker"})
add("Teferi, Hero of Dominaria", 5, "Planeswalker", colors={"U", "W"}, produces=set(), tags={"draw", "planeswalker", "removal"})
add("Teferi, Temporal Archmage", 6, "Planeswalker", colors={"U"}, produces=set(), tags={"planeswalker"})
add("Teferi, Time Raveler", 3, "Planeswalker", colors={"U", "W"}, produces=set(), tags={"draw", "planeswalker"})
add("Teferi, Who Slows the Sunset", 4, "Planeswalker", colors={"U", "W"}, produces=set(), tags={"draw", "planeswalker"})
# Achado real (auditoria oraculo-por-oraculo): "{4},{T}: For each
# planeswalker you control, you may activate one of its loyalty
# abilities once this turn as though none of its loyalty abilities have
# been activated this turn" -- habilidade ativada real, paga, nunca
# implementada (so' o downside de vida, sem rastreio de vida neste
# arquivo, ficaria de fora mesmo). Ver try_chain_veil_activation().
add("The Chain Veil", 4, "Artifact", colors=set(), produces=set(), tags={"chain_veil"})
add("The Eternal Wanderer", 6, "Planeswalker", colors={"W"}, produces=set(), tags={"planeswalker", "wipe"})
add("The Peregrine Dynamo", 3, "Creature", colors=set(), produces=set(), tags={"creature", "artifact"})  # "Legendary Artifact Creature" (tag "artifact": wipe de artefato alcanca)
add("The World Tree", 0, "Land", colors={"G"}, produces={"G"}, tags={"world_tree_6lands"})
# Achado real 2026-08-28: "{T}: Add {G}" incondicional (produces acima),
# mas o resto do oraculo real e' "This land enters tapped." + "As long as
# you control six or more lands, lands you control have '{T}: Add one
# mana of any color.'" (afeta TODO terreno em campo, condicionado a 6+
# terrenos - nao 5c incondicional desde o turno 1). Tag "world_tree_6lands"
# checada em color_sources(). NAO modelado (esse arquivo nao rastreia
# terreno tapped-on-ETB pra nenhuma carta - mesma simplificacao geral ja
# em uso aqui): o "enters tapped" proprio dela, atraso de 1 turno.
add("Three Visits", 2, "Sorcery", colors={"G"}, produces=set(), tags={"ramp"})
add("Toxic Deluge", 3, "Sorcery", colors={"B"}, produces=set(), tags={"wipe"})
add("Ugin, the Spirit Dragon", 8, "Planeswalker", colors=set(), produces=set(), tags={"draw", "planeswalker", "removal"})
# Achado real (auditoria oraculo-por-oraculo): Saga real (Read ahead) 100%
# ausente -- I: scry 4 (nao modelado, sem infra de scry neste arquivo,
# mesma convencao de omissao ja usada noutros decks) + revela o topo, se
# for planeswalker vai pra mao; II: pode botar um planeswalker MV<=6 da
# mao em campo de graca; III: ativa lealdade 2x so' neste turno. Ver
# try_urza_saga_tick().
add("Urza Assembles the Titans", 5, "Enchantment", colors={"W"}, produces=set(), tags={"urza_saga"})
add("Veil of Summer", 1, "Instant", colors={"G"}, produces=set(), tags={"draw"})
add("Void Rend", 3, "Instant", colors={"B", "U", "W"}, produces=set(), tags={"removal"})
add("Vorinclex, Monstrous Raider", 6, "Creature", colors={"G"}, produces=set(), tags={"counter_doubler", "creature"})
add("Vraska, Betrayal's Sting", 6, "Planeswalker", colors={"B"}, produces={"B", "G", "R", "U", "W"}, tags={"draw", "planeswalker", "proliferate", "ramp"})
add("Badlands", 0, "Land", colors={"B", "R"}, produces={"B", "R"}, tags=set())
add("Bayou", 0, "Land", colors={"B", "G"}, produces={"B", "G"}, tags=set())
add("Blood Crypt", 0, "Land", colors={"B", "R"}, produces={"B", "R"}, tags=set())
add("Breeding Pool", 0, "Land", colors={"G", "U"}, produces={"G", "U"}, tags=set())
add("Brushland", 0, "Land", colors={"G", "W"}, produces={"C", "G", "W"}, tags=set())
add("City of Brass", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())
add("Command Tower", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())
add("Emergence Zone", 0, "Land", colors=set(), produces={"C"}, tags={"flash_enabler"})
add("Exotic Orchard", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())
# Achado real 2026-08-28 (auditoria de checklist): Fabled Passage NAO TEM
# nenhuma habilidade de mana no oraculo real - so' "{T}, Sacrifice this
# land: Search your library for a basic land card, put it onto the
# battlefield tapped, then shuffle. Then if you control four or more
# lands, untap that land." Estava modelada como fonte incondicional de
# qualquer cor (nem sequer excluida do +1 generico de is_land()). Corrigido:
# produces=set() + tag "fabled_passage" (excluida do +1 generico em
# total_mana(), tem busca real implementada em try_fabled_passage()).
add("Fabled Passage", 0, "Land", colors=set(), produces=set(), tags={"fabled_passage"})
add("Godless Shrine", 0, "Land", colors={"B", "W"}, produces={"B", "W"}, tags=set())
add("Hallowed Fountain", 0, "Land", colors={"U", "W"}, produces={"U", "W"}, tags=set())
add("Interplanar Beacon", 0, "Land", colors=set(), produces={"C"}, tags=set())
# Achado real 2026-08-28: "{T}: Add {C}" incondicional (produces acima) e'
# a UNICA parte generica real - a mana colorida real ("{1},{T}: Add two
# mana of different colors") custa mana adicional e so' vale pra conjurar
# planeswalkers. Modelada como 5c incondicional antes - corrigido pra so'
# incolor. A metade restrita a planeswalkers nao foi modelada (custo extra
# de mana + restricao de tipo, baixo valor pro escopo desse sim).
add("Mana Confluence", 0, "Land", colors=set(), produces={"B", "G", "R", "U", "W"}, tags=set())
add("Overgrown Tomb", 0, "Land", colors={"B", "G"}, produces={"B", "G"}, tags=set())
add("Plateau", 0, "Land", colors={"R", "W"}, produces={"R", "W"}, tags=set())
add("Plaza of Heroes", 0, "Land", colors=set(), produces={"C"}, tags=set())
# Achado real 2026-08-28: "{T}: Add {C}" incondicional (produces acima) e'
# a UNICA parte generica real - as outras 2 habilidades de mana colorida
# ("Spend only to cast a legendary spell" / "any color among legendary
# permanents you control") sao restritas, nao modeladas (baixo valor pro
# escopo desse sim, deck ja tem Delighted Halfling pro caso legendary).
add("Sacred Foundry", 0, "Land", colors={"R", "W"}, produces={"R", "W"}, tags=set())
add("Savannah", 0, "Land", colors={"G", "W"}, produces={"G", "W"}, tags=set())
add("Scrubland", 0, "Land", colors={"B", "W"}, produces={"B", "W"}, tags=set())
add("Snow-Covered Forest", 0, "Land", colors={"G"}, produces={"G"}, tags=set())
add("Snow-Covered Island", 0, "Land", colors={"U"}, produces={"U"}, tags=set())
add("Snow-Covered Mountain", 0, "Land", colors={"R"}, produces={"R"}, tags=set())
add("Snow-Covered Plains", 0, "Land", colors={"W"}, produces={"W"}, tags=set())
add("Snow-Covered Swamp", 0, "Land", colors={"B"}, produces={"B"}, tags=set())
add("Steam Vents", 0, "Land", colors={"R", "U"}, produces={"R", "U"}, tags=set())
add("Stomping Ground", 0, "Land", colors={"G", "R"}, produces={"G", "R"}, tags=set())
add("Taiga", 0, "Land", colors={"G", "R"}, produces={"G", "R"}, tags=set())
add("Temple Garden", 0, "Land", colors={"G", "W"}, produces={"G", "W"}, tags=set())
add("Tropical Island", 0, "Land", colors={"G", "U"}, produces={"G", "U"}, tags=set())
add("Tundra", 0, "Land", colors={"U", "W"}, produces={"U", "W"}, tags=set())
add("Underground Sea", 0, "Land", colors={"B", "U"}, produces={"B", "U"}, tags=set())
add("Volcanic Island", 0, "Land", colors={"R", "U"}, produces={"R", "U"}, tags=set())
add("Watery Grave", 0, "Land", colors={"B", "U"}, produces={"B", "U"}, tags=set())

# -------- Tokens gerados por habilidades de planeswalker --------
add("Soldier Token", 0, "Creature", colors={"W"}, produces=set(), tags=set())
add("Zombie Token", 0, "Creature", colors={"B"}, produces=set(), tags=set())
add("Elk Token", 0, "Creature", colors={"G"}, produces=set(), tags=set())
add("Samurai Token", 0, "Creature", colors={"W"}, produces=set(), tags=set())
add("Spirit Token", 0, "Creature", colors={"W"}, produces=set(), tags=set())  # Kaya, Intangible Slayer -3 (copia 1/1 voadora)

# -------- Candidatas de pillowfort (A/B, 2026-09-24) -- NAO estao na lista --------
# Oraculo conferido ao vivo no Scryfall. Entram so' via `swap` de
# `simulate_one_with_interaction` pra medir o efeito contra ataque real
# aos planeswalkers (modelo de combate, ver secao propria).
add("Silent Arbiter", 4, "Creature", colors=set(), produces=set(), tags={"creature", "artifact", "attack_limit_one"})  # "Artifact Creature"
# "No more than one creature can attack each combat. No more than one creature can block each combat."
add("Dueling Grounds", 3, "Enchantment", colors={"G", "W"}, produces=set(), tags={"attack_limit_one"})
# mesmo texto do Silent Arbiter, em encantamento
add("Sphere of Safety", 5, "Enchantment", colors={"W"}, produces=set(), tags={"sphere_of_safety"})
# "Creatures can't attack you or planeswalkers you control unless their controller pays {X} for each
# of those creatures, where X is the number of enchantments you control."
add("Ghostly Prison", 3, "Enchantment", colors={"W"}, produces=set(), tags={"ghostly_prison"})
# "Creatures can't attack you unless their controller pays {2} for each creature they control that's
# attacking you." Ruling oficial: "a creature that can't attack you can still attack a planeswalker you control."

# Poder/resistencia/palavras-chave reais (Scryfall, 2026-09-24) das criaturas
# que podem estar do nosso lado -- so' usado pelo modelo de combate.
CREATURE_STATS = {
    "Bloom Tender": (1, 1, set()),
    "Delighted Halfling": (1, 2, set()),
    "Evolution Sage": (3, 2, set()),
    "Arena Rector": (1, 2, set()),
    "Atraxa, Praetors' Voice": (4, 4, {"deathtouch", "flying", "lifelink", "vigilance"}),
    "Carth the Lion": (3, 5, set()),
    "Deepglow Skate": (3, 3, set()),
    "Flux Channeler": (2, 2, set()),
    "The Peregrine Dynamo": (1, 5, {"haste"}),
    "Sphinx of the Second Sun": (6, 6, {"flying"}),
    "Vorinclex, Monstrous Raider": (6, 6, {"haste", "trample"}),
    "Silent Arbiter": (1, 5, set()),
    "Soldier Token": (1, 1, set()),
    "Zombie Token": (2, 2, set()),
    "Elk Token": (3, 3, set()),
    "Samurai Token": (2, 2, {"double_strike"}),
    "Spirit Token": (1, 1, {"flying"}),
}
# Criaturas "descartaveis" pra bloqueio de sacrificio (chump): fichas e
# dorks/paredes. Motores (Carth, Atraxa, Vorinclex, Flux Channeler,
# Evolution Sage, Deepglow Skate, Sphinx, Peregrine Dynamo, Arena Rector)
# so' bloqueiam se sobrevivem ou se a troca mata um atacante que mataria
# um planeswalker (ver `_choose_blocker`).
CHUMP_OK = {"Soldier Token", "Zombie Token", "Elk Token", "Samurai Token", "Spirit Token",
            "Bloom Tender", "Delighted Halfling", "Silent Arbiter"}

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

def has_tag(card: str, tag: str) -> bool:
    return tag in C(card).tags

# Permanentes lendarios de verdade na decklist (type_line real, Scryfall) -
# usado por Delighted Halfling/Plaza of Heroes ("cast a legendary spell").
LEGENDARY_CARD_NAMES = {
    "Aminatou, the Fateshifter", "Ashiok, Dream Render", "Atraxa, Praetors' Voice",
    "Carth the Lion", "Elspeth, Sun's Champion", "Kaya, Intangible Slayer",
    "Liliana, Dreadhorde General", "Narset, Parter of Veils", "Nicol Bolas, Dragon-God",
    "Oath of Nissa", "Oath of Teferi", "Oko, the Ringleader", "Tamiyo, Compleated Sage",
    "Tamiyo, Field Researcher", "Teferi, Hero of Dominaria", "Teferi, Temporal Archmage",
    "Teferi, Time Raveler", "Teferi, Who Slows the Sunset", "The Chain Veil",
    "The Eternal Wanderer", "The Peregrine Dynamo", "Ugin, the Spirit Dragon",
    "Vorinclex, Monstrous Raider", "Vraska, Betrayal's Sting",
}

# Achado real 2026-08-28 (auditoria de checklist): Farseek/Nature's
# Lore/Three Visits eram conjurados como Sorcery generica e iam direto pro
# cemiterio, sem NENHUMA busca real - puro sink de mana. Pools reais
# (type_line, Scryfall) de terrenos desta decklist que se qualificam:
BASIC_LAND_NAMES = {"Snow-Covered Forest", "Snow-Covered Island", "Snow-Covered Mountain",
                     "Snow-Covered Plains", "Snow-Covered Swamp"}
FARSEEK_POOL = {"Badlands", "Bayou", "Blood Crypt", "Breeding Pool", "Godless Shrine",
                 "Hallowed Fountain", "Overgrown Tomb", "Plateau", "Sacred Foundry", "Savannah",
                 "Scrubland", "Snow-Covered Island", "Snow-Covered Mountain", "Snow-Covered Plains",
                 "Snow-Covered Swamp", "Steam Vents", "Stomping Ground", "Taiga", "Temple Garden",
                 "Tropical Island", "Tundra", "Underground Sea", "Volcanic Island", "Watery Grave"}
FOREST_FETCH_POOL = {"Bayou", "Breeding Pool", "Overgrown Tomb", "Savannah", "Snow-Covered Forest",
                      "Stomping Ground", "Taiga", "Temple Garden", "Tropical Island"}
LAND_FETCH_SPELLS = {"Farseek", "Nature's Lore", "Three Visits"}

# Achado real 2026-08-28 (usuario: "Preciso que os counters de lealdade e
# ativacoes de planeswalker sejam sempre contabilizados, a base do
# Prismatic Bridge e essa!"): lealdade inicial real (Scryfall) dos 17
# planeswalkers da lista - nenhum tinha lealdade rastreada antes, so a tag
# decorativa "planeswalker". Ver regra permanente nova em
# references/goldfish-sim-card-rules.md, categoria 12.
PLANESWALKER_STARTING_LOYALTY = {
    "Aminatou, the Fateshifter": 3, "Ashiok, Dream Render": 5,
    "Elspeth, Sun's Champion": 4, "Kaya, Intangible Slayer": 6,
    "Liliana, Dreadhorde General": 6, "Narset, Parter of Veils": 5,
    "Nicol Bolas, Dragon-God": 4, "Oko, the Ringleader": 3,
    "Tamiyo, Compleated Sage": 5, "Tamiyo, Field Researcher": 4,
    "Teferi, Hero of Dominaria": 4, "Teferi, Temporal Archmage": 5,
    "Teferi, Time Raveler": 4, "Teferi, Who Slows the Sunset": 4,
    "The Eternal Wanderer": 5, "Ugin, the Spirit Dragon": 7,
    "Vraska, Betrayal's Sting": 6,
}
# Tamiyo, Compleated Sage / Vraska, Betrayal's Sting tem custo "Compleated"
# (paga 2 vida em vez de mana colorida, entra com 2 lealdade a menos) - so
# se aplica quando a carta e' CONJURADA pagando o custo. A Bridge poe a
# carta direto em campo (nao e' um cast), entao a lealdade inicial e'
# sempre a cheia - nao ha custo alternativo a pagar aqui.

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
    mana_spent_this_turn: int = 0
    tapped_lands_this_turn: Set[str] = field(default_factory=set)  # Farseek/Fabled Passage - terreno entra tapped esse turno, resetado em play_turn()
    evolution_sage_proliferates: int = 0
    mana_held_back: int = 0  # mana nao gasta no ultimo turno, disponivel pra flash no end step alheio (untap so acontece no MEU untap step - CR 500.1 - entao isso NAO reseta pra total_mana entre meus turnos)
    lands_played_total: int = 0

    bridge_in_play: bool = False
    bridge_cast_turn: Optional[int] = None
    bridge_first_cast_turn: Optional[int] = None
    bridge_cast_count: int = 0
    bridge_removed_count: int = 0
    bridge_flash_cast: bool = False
    bridge_triggers: int = 0
    bridge_hits_creature: int = 0
    bridge_hits_planeswalker: int = 0
    bridge_no_hit_empty_library: int = 0
    first_pw_hit_turn: Optional[int] = None

    protectors_removed_count: int = 0
    removal_attempts_total: int = 0
    removal_attempts_wasted: int = 0

    with_greater_auramancy: bool = False

    # Doenca de invocacao pra mana dorks criatura (Bloom Tender, Delighted
    # Halfling) - achado real 2026-08-28 (auditoria de checklist de
    # mecanica): nao existia NENHUM rastreio de turno de entrada, entao
    # ambas produziam mana no proprio turno em que eram conjuradas.
    creature_cast_turn: Dict[str, int] = field(default_factory=dict)

    # Lealdade real dos planeswalkers em campo (nome -> lealdade atual).
    loyalty: Dict[str, int] = field(default_factory=dict)
    pw_draws_total: int = 0
    pw_tokens_created_total: int = 0
    pw_life_gained_total: int = 0
    pw_life_lost_opponent_total: int = 0
    pw_removal_proxy_total: int = 0
    pw_wipe_proxy_total: int = 0
    pw_recursion_total: int = 0
    pw_ultimates_used_total: int = 0
    pw_deaths_total: int = 0
    pw_activations_total: int = 0
    teferi_sunset_emblem: bool = False  # ultimate: draw extra durante upkeep de cada oponente (ver do_upkeep)

    # Achado real 2026-08-28 (usuario: "verifique as cartas com niveis,
    # como classes e sagas... o innkeeper's no Prismatic no nivel 3 DOBRA
    # TODOS OS COUNTERS, inclusive os de lealdade de PWs ao entrarem no
    # jogo!"): nivel comeca em 1 (habilidade base) ao ser conjurada, sobe
    # "as a sorcery" pagando o custo real de cada nivel.
    innkeepers_talent_level: int = 1

    # Achados reais 2026-09-01 (leitura linha-a-linha completa do
    # oraculo, "compile TUDO" - a nota antiga do docstring sobre "11
    # criaturas nao-ramp/draw/removal/counter-doubler" ficou desatualizada;
    # verificado carta a carta contra o oraculo real via Scryfall):
    # Sphinx of the Second Sun ("if you cast it, take an extra turn") e
    # Carth the Lion (ETB: tutor de planeswalker + taxa de {1} extra em
    # TODA ativacao de lealdade, inclusive a nossa) sao reais e
    # implementaveis neste motor - Arena Rector (gatilho de MORTE, nao
    # ETB) e The Peregrine Dynamo (copiar gatilho entre N fontes
    # legendarias, mesma excecao arquitetural do Strionic Resonator)
    # permanecem estruturalmente fora de escopo, ver docstring.
    extra_turns_pending: int = 0  # fila generica de turno extra (hoje nenhuma carta da lista usa)
    # CORRIGIDO 2026-09-24: o Sphinx of the Second Sun estava implementado
    # com um texto que a carta NAO tem ("if you cast it, take an extra turn"
    # + sacrificio no upkeep). Oraculo real (Scryfall ao vivo): "At the
    # beginning of each of your postcombat main phases, there is an
    # additional beginning phase after this phase." Ver
    # `sphinx_additional_beginning_phase`.
    sphinx_extra_beginning_phases_total: int = 0
    carth_tutors_total: int = 0

    # Achado real (auditoria oraculo-por-oraculo): "removal"/"counterspell"/
    # "wipe" nas 11 cartas nao-planeswalker (Anguished Unmaking, Blasphemous
    # Act, Counterspell, Damn, Farewell, Mana Drain, Path to Exile, Supreme
    # Verdict, Swords to Plowshares, Toxic Deluge, Void Rend) nunca eram
    # lidas em lugar nenhum -- as cartas eram conjuradas pelo loop generico
    # (corretamente sem efeito de bordo real, Regra 1: sem oponente real, um
    # wipe/remocao sem alvo nao faz nada), mas nem sequer contavam pra
    # metrica de interacao, ao contrario de TODOS os outros decks desta
    # sessao (que tem esse contador pras 5 metricas basicas).
    interaction_spells_cast_total: int = 0

    # Achado real: 3 fontes reais de "ative habilidades de lealdade mais de
    # 1x por turno" nunca implementadas -- Oath of Teferi (estatico,
    # "twice each turn rather than only once"), The Chain Veil ({4},{T}:
    # mais 1x pra CADA planeswalker) e Urza Assembles the Titans capitulo
    # III (2x so' no turno em que resolve). Com 17 planeswalkers na lista,
    # sao os maiores multiplicadores de valor do deck inteiro fora da
    # propria Bridge -- nenhum estava implementado.
    chain_veil_activated_this_turn: bool = False
    urza_chapter: int = 0
    urza_last_ticked_turn: int = -1
    urza_chapter_iii_this_turn: bool = False
    chain_veil_activations_total: int = 0
    urza_pw_cheated_total: int = 0
    urza_pw_tutored_total: int = 0

    # ---- Modo opcional de resiliencia (interacao de oponente), 2026-09-20 ----
    # Porte do mesmo modo ja implementado e validado no Megatron/Ur-Dragon/
    # Hei Bai/Markov/Ulalek/Toph. Todos os campos abaixo ficam INERTES em
    # modo padrao (`simulate_one`/`run_batch`) -- so' tem efeito quando
    # `interaction_rng` e' setado por `simulate_one_with_interaction`, que
    # tambem passa `skip_legacy_removal=True` pra `play_turn` (desliga o
    # sistema antigo `resolve_removal_round`, ver decisao do usuario no
    # checklist-oraculo.md -- os 2 sistemas nao se empilham). `life` e'
    # NOVO neste arquivo (nunca rastreou vida propria) -- serve so' de
    # alvo pro ataque de oponente do modo de resiliencia, comeca em 40.
    interaction_rng: Optional[random.Random] = None
    life: int = 40
    smart_removals_total: int = 0
    smart_removal_log: list = field(default_factory=list)
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

    # ---- Modelo de combate: ataque de oponente a planeswalkers, 2026-09-24 ----
    # Pedido do usuario ("Conseguimos implementar no goldfish um simulador de
    # ataque aos PW?", aprovado com 3 perfis de mesa + perfil misto). So'
    # ativo quando `attack_profile` e' setado por `simulate_one_with_
    # interaction`; em modo padrao tudo abaixo fica inerte.
    attack_profile: Optional[str] = None
    opp_archetypes: List[str] = field(default_factory=list)
    opp_boards: List[list] = field(default_factory=list)       # por oponente: lista de dicts de criatura
    opp_cmd_cooldown: List[int] = field(default_factory=list)  # voltron: turnos ate recastar o comandante
    opp_cmd_bonus: List[int] = field(default_factory=list)     # voltron: bonus de equipamento que sobra ao recastar
    our_tapped: List[str] = field(default_factory=list)        # atacaram no meu turno, ficam virados ate o meu untap (CR 500.1)
    new_tokens_this_turn: Dict[str, int] = field(default_factory=dict)
    creature_counters: Dict[str, int] = field(default_factory=dict)       # +1/+1 em criatura nomeada (unica)
    token_counters: Dict[str, List[int]] = field(default_factory=dict)    # +1/+1 por instancia de ficha
    elspeth_emblem: bool = False
    opp_attackers_total: int = 0
    opp_attacks_on_pw_total: int = 0
    pw_combat_damage_total: int = 0
    pw_combat_deaths_total: int = 0
    face_combat_damage_total: int = 0
    blocks_total: int = 0
    our_blockers_lost_total: int = 0
    opp_creatures_killed_total: int = 0
    our_wipes_cast_total: int = 0
    our_spot_removal_cast_total: int = 0
    pw_defensive_uses_total: int = 0
    attackers_stopped_by_tax_total: int = 0
    attackers_redirected_to_pw_total: int = 0
    attackers_limited_total: int = 0
    our_combat_damage_proxy_total: int = 0
    pw_turns_alive_total: int = 0
    liliana_static_draws_total: int = 0
    arena_rector_triggers_total: int = 0
    tamiyo_fr_marked: List[tuple] = field(default_factory=list)  # +1 da Tamiyo FR: ate' 2 criaturas nossas, ate' meu proximo turno
    tamiyo_fr_combat_draws_total: int = 0
    teferi_hero_emblem: bool = False
    teferi_emblem_exiles_total: int = 0
    ugin_minus_x_total: int = 0
    oko_combat_copies_total: int = 0
    our_lifelink_gain_total: int = 0
    pw_enter_turn: Dict[str, int] = field(default_factory=dict)
    all_will_be_one_triggers_total: int = 0
    all_will_be_one_kills_total: int = 0
    all_will_be_one_face_damage_total: int = 0
    loyalty_activated_this_turn: bool = False
    chain_veil_life_lost_total: int = 0
    died_turn: Optional[int] = None  # 1o turno (meu) em que a vida chegou a <= 0 -- o motor nao encerra a partida; a metrica marca
    pillowfort_first_turn: Optional[int] = None   # A/B: 1o turno com Silent Arbiter/Dueling Grounds/Sphere/Ghostly Prison em campo
    pillowfort_turns_total: int = 0

    def draw(self, n: int = 1):
        for _ in range(n):
            if self.library:
                self.hand.append(self.library.pop(0))
                if self.teferi_hero_emblem and self.attack_profile is not None:
                    # Emblema do Teferi, Hero of Dominaria (-8): "Whenever you
                    # draw a card, exile target permanent an opponent
                    # controls." So' ha' permanente de oponente rastreado no
                    # modelo de combate.
                    _teferi_hero_emblem_trigger(self)

    def has(self, name: str) -> bool:
        return name in self.battlefield

# =========================================================
# MANA MODEL
# =========================================================

def _dork_ready(state: GameState, card: str) -> bool:
    return state.creature_cast_turn.get(card, -1) < state.turn

def total_mana(state: GameState) -> int:
    total = 0
    for card in state.battlefield:
        if has_tag(card, "fabled_passage"):
            continue  # sem habilidade de mana propria - so' fetch (try_fabled_passage)
        if is_land(card):
            if card in state.tapped_lands_this_turn:
                continue  # entrou tapped esse turno (Farseek/Fabled Passage), ainda nao produz
            total += 1
        elif card == "Sol Ring":
            total += 2
        elif has_tag(card, "bloom_tender"):
            if _dork_ready(state, card):
                colors_in_play = set()
                for c in state.battlefield:
                    colors_in_play |= C(c).colors
                total += max(0, len(colors_in_play))
        elif has_tag(card, "ramp") and card != "Delighted Halfling":
            if C(card).type == "Creature" and not _dork_ready(state, card):
                continue  # doenca de invocacao (CR 302.6) - so' pra criatura
            total += 1
        elif card == "Delighted Halfling":
            if _dork_ready(state, card):
                total += 1  # so' o {T}: Add {C} incondicional
    return total

def color_sources(state: GameState, color: str, legendary_spell: bool = False) -> int:
    n = 0
    world_tree_active = "The World Tree" in state.battlefield and sum(1 for c in state.battlefield if is_land(c)) >= 6
    lantern_active = "Chromatic Lantern" in state.battlefield
    for card in state.battlefield:
        base_produces = C(card).produces
        # Chromatic Lantern / The World Tree (6+ terrenos): TODO terreno em
        # campo ganha "{T}: Add one mana of any color" via efeito estatico.
        if is_land(card) and (lantern_active or world_tree_active) and card != "Chromatic Lantern":
            n += 1
            continue
        if has_tag(card, "bloom_tender"):
            colors_in_play = {cc for c in state.battlefield for cc in C(c).colors}
            if _dork_ready(state, card) and color in colors_in_play:
                n += 1
            continue
        if color not in base_produces:
            continue
        if has_tag(card, "legendary_only_color") and not legendary_spell:
            continue
        if C(card).type == "Creature" and not _dork_ready(state, card):
            continue
        n += 1
    return n

def remaining_mana(state: GameState) -> int:
    return total_mana(state) - state.mana_spent_this_turn

def bridge_effective_mv(state: GameState) -> int:
    return C(COMMANDER).mv + 2 * state.bridge_cast_count

def can_cast(state: GameState, card: str) -> bool:
    mv = bridge_effective_mv(state) if card == COMMANDER else C(card).mv
    if remaining_mana(state) < mv:
        return False
    legendary = card == COMMANDER or card in LEGENDARY_CARD_NAMES
    for color in C(card).colors:
        if color_sources(state, color, legendary_spell=legendary) < 1:
            return False
    return True

# =========================================================
# MULLIGAN (simplificado - so garante mao jogavel de terrenos)
# =========================================================

# Rocks/dorks reais que aceleram de verdade (validado por analise de
# correlacao, n=8000 maos, 2026-08-21): Sol Ring/Arcane Signet/Bloom
# Tender/Delighted Halfling/Chromatic Lantern reduzem o turno medio da
# 1a conjuracao da Bridge de ~4,1-4,2 pra ~3,2-3,8 quando estao na mao
# inicial. Farseek/Nature's Lore/Three Visits (tutores de terreno) NAO
# entram aqui de proposito - a mesma analise mostrou que eles pioram a
# velocidade (custam carta+2 mana pra fazer o que 1 land drop ja faz de
# graca), entao nao contam como equivalente a um rock pra decisao de
# mulligan.
FAST_RAMP_ROCKS_DORKS = {"Sol Ring", "Arcane Signet", "Chromatic Lantern", "Bloom Tender", "Delighted Halfling"}

def should_keep(hand: List[str]) -> bool:
    # Heuristico validado por dados (n=8000, 2026-08-21): 2 terrenos sem
    # rock e uma mao ruim de verdade (turno medio 5,72, 31,8% nunca
    # conjura a Bridge) - pior que 3 terrenos sozinhos (4,50/14,0%), que
    # por sua vez e pior que 2 terrenos + 1 rock (4,32/12,2%). Exige 3+
    # terrenos OU 2 terrenos + pelo menos 1 rock/dork real.
    lands = sum(1 for c in hand if is_land(c))
    if lands > 5:
        return False
    if lands >= 3:
        return True
    if lands == 2:
        return any(c in FAST_RAMP_ROCKS_DORKS for c in hand)
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
    # prioriza terreno que cobre cor que falta
    have_colors = set()
    for c in state.battlefield:
        have_colors |= C(c).produces
    missing = {"W", "U", "B", "R", "G"} - have_colors
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
    on_land_enters(state, log)

def on_land_enters(state: GameState, log: List[Dict]):
    # Evolution Sage: "Landfall - Whenever a land you control enters,
    # proliferate." Achado real 2026-08-28: sem NENHUM despacho de landfall
    # nesse arquivo, mesma classe do bug do Beorn. Achado real 2026-08-28
    # (2a rodada, regra nova de lealdade): agora que a lealdade de
    # planeswalker E' rastreada de verdade, proliferate tem um alvo real -
    # aplicado via proliferate_loyalty() (+1 lealdade em cada planeswalker
    # que controla, dobrado se Doubling Season/Vorinclex em campo).
    if "Evolution Sage" in state.battlefield:
        state.evolution_sage_proliferates += 1
        proliferate_loyalty(state, log, source="evolution_sage")

def do_land_fetch_spell(state: GameState, card: str, log: List[Dict]):
    """Farseek/Nature's Lore/Three Visits - busca real de terreno, corrigindo
    o achado 2026-08-28: eram Sorcery generica sem NENHUM efeito de board,
    puro sink de mana."""
    pool = FARSEEK_POOL if card == "Farseek" else FOREST_FETCH_POOL
    available = [c for c in state.library if c in pool]
    if not available:
        return
    have_colors = set()
    for c in state.battlefield:
        have_colors |= C(c).produces
    missing = {"W", "U", "B", "R", "G"} - have_colors
    best = next((c for c in available if C(c).produces & missing), available[0])
    state.library.remove(best)
    state.battlefield.append(best)
    if card == "Farseek":
        state.tapped_lands_this_turn.add(best)  # "put onto the battlefield tapped"
    log.append({"action": "land_fetch", "card": card, "target": best, "turn": state.turn})
    on_land_enters(state, log)


def _carth_lion_look_at_top7(state: GameState, log: List[Dict], source: str):
    """Carth the Lion (Scryfall, oraculo real): 'Whenever Carth enters
    or a planeswalker you control dies, look at the top seven cards of
    your library. You may reveal a planeswalker card from among them
    and put it into your hand. Put the rest on the bottom of your
    library in a random order.'

    Extraido de `do_carth_etb` (achado real 2026-09-20, ao auditar como
    `remove_permanent` do modo de resiliencia deveria interagir com
    `state.loyalty`): 2 bugs reais encontrados na mesma funcao, os 2
    JA' alcancaveis em modo padrao, sem relacao nenhuma com o modo de
    resiliencia -- so' achados por estar auditando esta area por outro
    motivo.

    1. **"Put the rest on the bottom" estava colocando no TOPO**
       (`state.library = top7 + rest`) -- inverteu duas vezes o
       posicionamento real (nem "topo" nem realmente "random" no
       sentido correto de fundo). Corrigido: `rest + shuffled_top7`.
    2. **A metade "morte de planeswalker" nunca disparava** -- o
       comentario original (2026-09-01) dizia que "nada remove nossos
       planeswalkers uma vez em campo", mas isso ja' era falso mesmo em
       modo padrao: `add_loyalty()` mata um planeswalker de verdade
       quando a lealdade cai a 0 ou menos (ex.: ultimate que zera a
       propria lealdade) -- medido: 1.861 mortes de planeswalker em
       3.000 partidas de modo padrao, nao um evento raro. Ver hook
       adicionado em `add_loyalty()`."""
    top7 = state.library[:7]
    rest = state.library[7:]
    pw_in_top7 = [c for c in top7 if C(c).type == "Planeswalker"]
    if pw_in_top7:
        found = pw_in_top7[0]
        top7.remove(found)
        state.hand.append(found)
        state.carth_tutors_total += 1
        log.append({"trigger": "carth_tutor", "found": found, "source": source, "turn": state.turn})
    state.rng.shuffle(top7)
    state.library = rest + top7


def do_carth_etb(state: GameState, log: List[Dict]):
    _carth_lion_look_at_top7(state, log, source="etb")


def creature_enters(state: GameState, name: str, log: List[Dict]):
    """Ponto UNICO de 'uma criatura nossa entra no campo' (achado real
    2026-09-24, Regra #1 taxonomia "gatilho compartilhado ligado so' em
    ALGUNS dos pontos"): antes, doenca de invocacao e os ETBs de Deepglow
    Skate ("When this creature enters, double the number of each kind of
    counter on any number of target permanents") e Carth the Lion
    ("Whenever Carth enters...") so' existiam no caminho de CONJURAR da mao.
    Criatura posta em campo pela propria Bridge (o caminho mais comum
    deste deck!), pelo ultimate do Ugin ou copiada pela Tamiyo, Compleated
    Sage entrava sem doenca de invocacao (dork gerava mana no mesmo turno)
    e sem ETB nenhum. "Enters" nao distingue como a carta entrou."""
    state.creature_cast_turn[name] = state.turn
    if name == "Deepglow Skate":
        # Sempre escolhe dobrar TODOS os planeswalkers em campo (nunca ha'
        # razao real pra nao escolher) e, no modelo de combate, as +1/+1.
        for pw in list(state.loyalty.keys()):
            add_loyalty(state, pw, state.loyalty[pw], log, reason="deepglow_skate_etb")
        if attack_model_on(state):
            _double_creature_counters(state)
    if name == "Carth the Lion":
        do_carth_etb(state, log)

def try_fabled_passage(state: GameState, log: List[Dict]):
    """Fabled Passage: '{T}, Sacrifice this land: Search your library for a
    basic land card, put it onto the battlefield tapped, then shuffle. Then
    if you control four or more lands, untap that land.' Ativa assim que
    entra (nenhum motivo real pra segurar - vira um basico de verdade, que
    o resto do motor ja sabe usar pra mana)."""
    if "Fabled Passage" not in state.battlefield:
        return
    available = [c for c in state.library if c in BASIC_LAND_NAMES]
    if not available:
        return
    have_colors = set()
    for c in state.battlefield:
        have_colors |= C(c).produces
    missing = {"W", "U", "B", "R", "G"} - have_colors
    best = next((c for c in available if C(c).produces & missing), available[0])
    state.library.remove(best)
    state.battlefield.remove("Fabled Passage")
    state.battlefield.append(best)
    lands_now = sum(1 for c in state.battlefield if is_land(c))
    if lands_now < 4:
        state.tapped_lands_this_turn.add(best)  # so' fica tapped se < 4 terrenos
    log.append({"action": "fabled_passage_crack", "target": best, "turn": state.turn})
    on_land_enters(state, log)

# =========================================================
# BRIDGE ENGINE
# =========================================================
# LEALDADE DE PLANESWALKER (regra nova - ver goldfish-sim-card-rules.md #12)
# =========================================================

def counter_doubler_multiplier(state: GameState) -> int:
    # Doubling Season ("counters... twice that many") e Vorinclex, Monstrous
    # Raider (mesmo efeito pros NOSSOS counters) sao replacement effects
    # reais que dobram lealdade - empilham multiplicativamente (regra real,
    # mesmo padrao ja usado pros dobradores de token no Edgar Markov).
    # Achado real 2026-08-28 (usuario: "verifique as cartas com niveis...
    # o innkeeper's no Prismatic no nivel 3 DOBRA TODOS OS COUNTERS"):
    # Innkeeper's Talent nivel 3 ("If you would put one or more counters on
    # a permanent or player, put twice that many...") e' o MESMO efeito -
    # engine de leveling implementada (ver try_level_up_innkeepers_talent),
    # empilha com os outros 2 igual.
    # Achado real 2026-09-24 (Regra #3): conta CADA copia em campo (a
    # Tamiyo, Compleated Sage -X cria ficha copia de Doubling Season/
    # Vorinclex do cemiterio -- 2 Doubling Seasons = x4). Innkeeper's
    # Talent copiada entra no nivel 1 (nivel de Class nao e' copiavel,
    # CR 716.2b), entao so' o original conta pro nivel 3.
    n = sum(state.battlefield.count(c) for c in ("Doubling Season", "Vorinclex, Monstrous Raider"))
    if "Innkeeper's Talent" in state.battlefield and state.innkeepers_talent_level >= 3:
        n += 1
    return 2 ** n

INNKEEPERS_TALENT_LEVEL_COST = {2: 1, 3: 4}  # {G}=1 pro nivel 2, {3}{G}=4 pro nivel 3

def try_level_up_innkeepers_talent(state: GameState, log: List[Dict]):
    if "Innkeeper's Talent" not in state.battlefield or state.innkeepers_talent_level >= 3:
        return
    next_level = state.innkeepers_talent_level + 1
    cost = INNKEEPERS_TALENT_LEVEL_COST[next_level]
    if remaining_mana(state) < cost or color_sources(state, "G") < 1:
        return
    state.mana_spent_this_turn += cost
    state.innkeepers_talent_level = next_level
    log.append({"trigger": "innkeepers_talent_level_up", "level": next_level, "turn": state.turn})

def _planeswalker_dies(state: GameState, pw: str, log: List[Dict]):
    """Cascata de 'um planeswalker seu morre' -- extraida de `add_loyalty()`
    (achado real 2026-09-20, ao portar `remove_permanent` do modo de
    resiliencia) pra ser reusada tanto por lealdade chegando a 0 (causa
    original, self-inflicted via ultimate/custo) quanto por remocao/wipe de
    OPONENTE (`remove_permanent`) -- a regra real ("whenever a planeswalker
    you control dies") nao distingue a CAUSA da morte, so' que ela
    aconteceu. Mesmo comportamento de antes pro call site original
    (confirmado por regressao bit-a-bit do modo padrao)."""
    if pw in state.battlefield:
        state.battlefield.remove(pw)
    state.graveyard.append(pw)
    if pw in state.loyalty:
        del state.loyalty[pw]
    state.pw_deaths_total += 1
    log.append({"trigger": "planeswalker_death", "pw": pw, "turn": state.turn})
    # Carth the Lion, "...or a planeswalker you control dies" -- achado real
    # 2026-09-20, ver `_carth_lion_look_at_top7`.
    if "Carth the Lion" in state.battlefield:
        _carth_lion_look_at_top7(state, log, source="pw_death")


def _counters_put(state: GameState, n: int, log: List[Dict], source: str = ""):
    """Ponto UNICO de "voce coloca N marcadores num permanente" (ja' com
    dobradores aplicados). All Will Be One (achado real 2026-09-24: carta
    na lista com ZERO codigo -- tags vazias): "Whenever you put one or more
    counters on a permanent or player, this enchantment deals that much
    damage to target opponent, creature an opponent controls, or
    planeswalker an opponent controls." Ruling oficial (2023-02-04):
    dispara tambem quando um permanente nosso ENTRA com marcadores
    (planeswalker entrando com lealdade). 1 gatilho por permanente que
    recebeu marcadores (proliferate em 3 PWs = 3 gatilhos). Chamado de:
    `add_loyalty` (+N), `planeswalker_enters`, `_add_ctr` (+1/+1 no modelo
    de combate) e lore counter da Urza.
    Alvo (politica): com o modelo de combate, mata a MAIOR criatura de
    oponente que o dano mata (defesa dos planeswalkers); senao vai no
    oponente (metrica proxy, sem vida de oponente rastreada)."""
    if n <= 0:
        return
    for _ in range(state.battlefield.count("All Will Be One")):
        state.all_will_be_one_triggers_total += 1
        if attack_model_on(state):
            cands = [(i, c) for i, b in enumerate(state.opp_boards) for c in b if c["t"] <= n]
            if cands:
                i, c = max(cands, key=lambda ic: (ic[1]["p"], ic[1]["cmd"]))
                _opp_remove_creature(state, i, c, how="damage")
                state.all_will_be_one_kills_total += 1
                continue
        state.all_will_be_one_face_damage_total += n


def add_loyalty(state: GameState, pw: str, amount: int, log: List[Dict], reason: str = ""):
    """Aplica uma mudanca de lealdade (positiva = ganha counters, negativa =
    remove) - so a parte POSITIVA e' dobrada por Doubling Season/Vorinclex
    (sao "puts counters", nao afetam remocao de lealdade pra pagar uma
    habilidade). Mata o planeswalker (remove de campo) se a lealdade
    chegar a 0 ou menos."""
    if pw not in state.loyalty:
        return
    if amount > 0:
        amount *= counter_doubler_multiplier(state)
    state.loyalty[pw] += amount
    if amount > 0:
        _counters_put(state, amount, log, source=reason)
    log.append({"trigger": "loyalty_change", "pw": pw, "amount": amount,
                "new_loyalty": state.loyalty[pw], "reason": reason, "turn": state.turn})
    if state.loyalty[pw] <= 0:
        _planeswalker_dies(state, pw, log)

def proliferate_loyalty(state: GameState, log: List[Dict], source: str = ""):
    # "Choose any number of permanents/players... give each another counter
    # of each kind already there." Modelado so pra lealdade de planeswalker
    # (unico sistema de counters rastreado por este simulador) - sempre
    # escolhe proliferar TODOS os planeswalkers que controla (nunca ha
    # razao real pra nao escolher os proprios).
    for pw in list(state.loyalty.keys()):
        add_loyalty(state, pw, 1, log, reason=f"proliferate_{source}")
    if attack_model_on(state):
        # Proliferate tambem alcanca +1/+1 de criatura -- so' existe marcador
        # de criatura rastreado quando o modelo de combate esta' ligado.
        _proliferate_creature_counters(state)

def planeswalker_enters(state: GameState, name: str, log: List[Dict]):
    base = PLANESWALKER_STARTING_LOYALTY[name]
    mult = counter_doubler_multiplier(state)
    state.loyalty[name] = base * mult
    state.pw_enter_turn[name] = state.turn  # doenca de invocacao do Oko quando vira copia de criatura
    _counters_put(state, base * mult, log, source=f"enters_{name}")
    log.append({"trigger": "planeswalker_enters", "pw": name, "loyalty": state.loyalty[name], "turn": state.turn})
    # Deepglow Skate: "When this creature enters, double the number of each
    # kind of counter on any number of target permanents" - ETB de UMA VEZ
    # SO (nao e' estatico), so' relevante se ela mesma entrar DEPOIS de um
    # planeswalker ja estar em campo (ver dispatch no cast normal dela).

def bridge_upkeep_trigger(state: GameState, log: List[Dict]):
    state.bridge_triggers += 1
    revealed_nonhit = []
    hit = None
    while state.library:
        card = state.library.pop(0)
        if C(card).type in ("Creature", "Planeswalker"):
            hit = card
            break
        revealed_nonhit.append(card)
    state.rng.shuffle(revealed_nonhit)
    state.library.extend(revealed_nonhit)
    if hit:
        state.battlefield.append(hit)
        if C(hit).type == "Creature":
            state.bridge_hits_creature += 1
            creature_enters(state, hit, log)
        else:
            state.bridge_hits_planeswalker += 1
            if state.first_pw_hit_turn is None:
                state.first_pw_hit_turn = state.turn
            planeswalker_enters(state, hit, log)
        log.append({"trigger": "bridge_hit", "card": hit, "type": C(hit).type, "turn": state.turn})
    else:
        state.bridge_no_hit_empty_library += 1
        log.append({"trigger": "bridge_no_hit", "reason": "biblioteca vazia", "turn": state.turn})

# Custo pra ativar cada habilitador de flash (generico, simplificacao - o
# Alchemist's Refuge exige G+U especificamente, tratado aqui so como 2
# generico ja que color_sources ja garante que essas cores existem no
# manabase). Emergence Zone se sacrifica ao ser usado (perde a fonte de
# mana permanentemente, nao so tapa).
FLASH_ENABLER_COST = {"Alchemist's Refuge": 2, "Emergence Zone": 1}

def choose_flash_enabler(state: GameState) -> Optional[str]:
    candidates = [c for c in state.battlefield if has_tag(c, "flash_enabler")]
    if not candidates:
        return None
    # prioriza o mais barato
    candidates.sort(key=lambda c: FLASH_ENABLER_COST.get(c, 0))
    return candidates[0]

def can_flash_bridge(state: GameState) -> bool:
    # A Bridge vem da zona de comando, nao precisa estar na mao (mesma
    # convencao do simulador do Thranduil: comandante sempre "disponivel").
    # IMPORTANTE: untap so acontece no MEU untap step (CR 500.1 - untap,
    # upkeep, draw). Terrenos ficam tapados do jeito que ficaram no meu
    # ultimo turno durante os turnos dos oponentes - entao a mana
    # disponivel pra flashar no end step alheio e o que sobrou NAO GASTO
    # do meu ultimo turno (state.mana_held_back), nao o total_mana atual.
    if state.bridge_in_play:
        return False
    enabler = choose_flash_enabler(state)
    if enabler is None:
        return False
    needed = FLASH_ENABLER_COST[enabler] + bridge_effective_mv(state)
    if state.mana_held_back < needed:
        return False
    for color in C(COMMANDER).colors:
        if color_sources(state, color) < 1:
            return False
    return True

def cast_bridge(state: GameState, log: List[Dict], via_flash: bool):
    # Contraataque (`try_smart_opponent_counter`, 7a categoria do modo de
    # resiliencia -- so' faz sentido no exato momento do cast, mesmo
    # padrao dos outros 6 decks): mana/enabler e taxa contam ANTES do
    # counter (CR 903.10a conta "cast", nao "resolved"), entrada em
    # campo so' DEPOIS de passar.
    if COMMANDER in state.hand:
        state.hand.remove(COMMANDER)
    mv = bridge_effective_mv(state)
    if via_flash:
        enabler = choose_flash_enabler(state)
        cost = FLASH_ENABLER_COST[enabler] + mv
        state.mana_held_back -= cost
        if enabler == "Emergence Zone":
            state.battlefield.remove(enabler)  # se sacrifica ao ativar
        log.append({"action": "flash_enabler_used", "card": enabler, "turn": state.turn})
    else:
        state.mana_spent_this_turn += mv
    state.bridge_cast_count += 1
    if try_smart_opponent_counter(state):
        log.append({"action": "cast_bridge_countered", "via_flash": via_flash, "turn": state.turn})
        return
    state.battlefield.append(COMMANDER)
    state.bridge_in_play = True
    state.bridge_cast_turn = state.turn
    if state.bridge_first_cast_turn is None:
        state.bridge_first_cast_turn = state.turn
    state.bridge_flash_cast = via_flash
    log.append({"action": "cast_bridge", "via_flash": via_flash, "turn": state.turn, "effective_mv": mv})

# =========================================================
# REMOCAO DO OPONENTE (premissa assumida - ver docstring)
# =========================================================

def protectors_in_play(state: GameState) -> List[str]:
    prot = ["Sterling Grove"]
    if state.with_greater_auramancy:
        prot.append("Greater Auramancy")
    return [p for p in prot if state.has(p)]

def resolve_removal_round(state: GameState, log: List[Dict]):
    if not state.bridge_in_play and not protectors_in_play(state):
        return
    for _ in range(N_OPPONENTS):
        if state.rng.random() >= REMOVAL_CHANCE_PER_OPPONENT:
            continue
        state.removal_attempts_total += 1
        prot = protectors_in_play(state)
        if prot:
            target = state.rng.choice(prot)
            state.battlefield.remove(target)
            state.graveyard.append(target)  # simplificacao: remocao = destroy (maioria dos casos reais)
            state.protectors_removed_count += 1
            log.append({"trigger": "removal", "target": target, "turn": state.turn})
        elif state.bridge_in_play:
            state.battlefield.remove(COMMANDER)
            # CORRIGIDO 2026-09-21 (achado real do usuario, CR 903.9a -- ver
            # `rules-cache/comprehensive-rules.txt` linhas 6888-6896, Regra
            # 18 de `references/user-standing-rules.md`): comandante indo
            # pro cemiterio/exilio NAO e' substituicao, e' ACAO BASEADA EM
            # ESTADO (CR 704) -- ela vai pro cemiterio DE VERDADE primeiro
            # (CR 700.4, "dies"), so' DEPOIS o dono PODE escolher move-la
            # pra zona de comando. Sem efeito NUMERICO aqui (0 cartas
            # "creature/planeswalker dies" neste deck reagem a um
            # ENCANTAMENTO morrendo -- Carth the Lion so' reage a criatura/
            # planeswalker, The Prismatic Bridge nunca e' nenhum dos 2),
            # mas corrigido por consistencia estrutural.
            state.graveyard.append(COMMANDER)
            if COMMANDER in state.graveyard:
                state.graveyard.remove(COMMANDER)
            state.bridge_in_play = False
            state.bridge_removed_count += 1
            log.append({"trigger": "removal", "target": COMMANDER, "turn": state.turn})
        else:
            state.removal_attempts_wasted += 1

def remove_permanent(state: GameState, name: str, log: List[Dict], source: str = "opponent"):
    """Ponto central de remocao de permanente do CAMPO pelo modo de
    resiliencia (7 categorias padronizadas, 2026-09-20 -- porte do
    Megatron/Ur-Dragon/Hei Bai/Markov/Ulalek/Toph). Diferente de
    `resolve_removal_round` (sistema ANTIGO, especifico deste deck, so'
    mira Bridge/protetores, sempre ativo desde o turno 1) -- por decisao
    do usuario, o modo de resiliencia NAO empilha os 2 sistemas: dentro
    dele, `resolve_removal_round` fica desligado (ver `play_turn(...,
    skip_legacy_removal=True)`) e SO' este chokepoint novo, com os
    mesmos gates/calibracao ja validados nos outros 6 decks, roda.

    Comandante: CORRIGIDO 2026-09-21 (achado real do usuario, CR
    903.9a -- ver `rules-cache/comprehensive-rules.txt` linhas
    6888-6896, Regra 18 de `references/user-standing-rules.md`, mesma
    correcao aplicada em `resolve_removal_round` acima). Ela vai pro
    cemiterio DE VERDADE primeiro (CR 700.4, "dies"), so' DEPOIS o dono
    PODE escolher move-la pra zona de comando (`bridge_in_play=False`).
    Sem efeito numerico aqui (0 cartas "creature/planeswalker dies"
    neste deck reagem a um ENCANTAMENTO morrendo).

    Planeswalker: delega pra `_planeswalker_dies` (mesma cascata real de
    "um planeswalker seu morre" que a lealdade chegando a 0 usa --
    remove de `state.battlefield` E `state.loyalty`, dispara Carth the
    Lion se em campo).

    Token: deixa de existir sem ir pro cemiterio (mesma convencao dos
    outros decks -- nomes com "Token" no final, ver `make_pw_token`).
    Carta nomeada: vai pro cemiterio de verdade."""
    if name not in state.battlefield:
        return
    if name == COMMANDER:
        state.battlefield.remove(name)
        state.graveyard.append(name)
        if name in state.graveyard:
            state.graveyard.remove(name)
        state.bridge_in_play = False
        return
    if name in state.loyalty:
        _planeswalker_dies(state, name, log)
        return
    if C(name).type == "Creature":
        # Achado real 2026-09-24 (Regra #3, gatilho compartilhado): criatura
        # nossa morrendo por remocao/wipe de oponente precisa disparar
        # Liliana, Dreadhorde General ("Whenever a creature you control
        # dies, draw a card") e o gatilho de morte da Arena Rector -- os 2
        # passam pela mesma cascata que combate e nossos proprios wipes usam.
        _our_creature_leaves(state, name, log, exiled=False, source=source)
        return
    state.battlefield.remove(name)
    if "Token" not in name:
        state.graveyard.append(name)

# =========================================================
# ATIVACAO DE PLANESWALKER (regra nova - ver goldfish-sim-card-rules.md #12)
# =========================================================
# Cada planeswalker so ativa UMA habilidade por turno (velocidade de
# feitico, CR 606.3) - garantido aqui por so' chamar o resolver 1x por PW
# por turno (activate_planeswalkers, chamada 1x no main_phase). Heuristica
# geral: prioriza a habilidade de maior valor real e sem downside
# simetrico (nunca usa uma habilidade que prejudica nosso proprio board
# sem necessidade); usa o ultimate assim que alcancavel se ele for
# claramente bom (nao simetrico); helper make_pw_token() reusa o padrao
# de criacao de token ja usado no resto do arquivo.

def make_pw_token(state: GameState, token_name: str, n: int, log: List[Dict]):
    # Doubling Season: "If an effect would create one or more tokens under
    # your control, it creates twice that many of those tokens instead."
    # Achado real 2026-09-24: so' a metade de CONTADOR da carta estava
    # implementada (counter_doubler_multiplier); a de FICHA nunca. Cada
    # copia dobra de novo. (Vorinclex e Innkeeper's Talent so' dobram
    # contador, nao ficha.)
    n *= 2 ** state.battlefield.count("Doubling Season")
    for _ in range(n):
        state.battlefield.append(token_name)
    if attack_model_on(state):
        # Doenca de invocacao (fichas criadas neste turno nao atacam) e
        # marcadores +1/+1 por instancia -- so' o modelo de combate le.
        state.new_tokens_this_turn[token_name] = state.new_tokens_this_turn.get(token_name, 0) + n
        state.token_counters.setdefault(token_name, []).extend([0] * n)
    state.pw_tokens_created_total += n
    log.append({"trigger": "pw_token", "token": token_name, "count": n, "turn": state.turn})

def resolve_planeswalker(state: GameState, pw: str, log: List[Dict]):
    loy = state.loyalty[pw]
    state.pw_activations_total += 1
    state.loyalty_activated_this_turn = True  # lido pelo gatilho de end step da The Chain Veil

    # Modelo de combate (2026-09-24): com criatura de oponente ameacando os
    # planeswalkers, os modos de remocao/controle que ja existem nas cartas
    # (Nicol Bolas -3, Kaya -3, Vraska -2, Teferi Hero -3, Eternal Wanderer
    # +1/-4, Elspeth -3, Liliana -4, Tamiyo FR -2) passam a ter alvo real.
    # Sem modelo de combate, nunca ha' ameaca -> heuristica antiga intacta.
    if attack_model_on(state) and _pw_defensive_activation(state, pw, loy, log):
        return

    if pw == "Aminatou, the Fateshifter":
        # +1: draw then put back (filtragem, sem vantagem liquida de cartas
        # - so registra a ativacao). -1 (blink proprio) e -6 (simetrico,
        # ajuda oponentes) ficam de fora - sem alvo/valor claro nesse motor.
        add_loyalty(state, pw, 1, log, reason="aminatou_plus1")

    elif pw == "Ashiok, Dream Render":
        # -1 e' a UNICA habilidade real - mill 4 + exila cemiterio de um
        # oponente. Sem efeito numerico no nosso lado (nao ha cemiterio de
        # oponente rastreado), mas e' denial real - conta como interacao.
        if loy >= 1:
            add_loyalty(state, pw, -1, log, reason="ashiok_minus1")
            state.pw_removal_proxy_total += 1

    elif pw == "Elspeth, Sun's Champion":
        if loy >= 7:
            add_loyalty(state, pw, -7, log, reason="elspeth_ultimate")
            state.pw_ultimates_used_total += 1  # emblem: +2/+2 e voar pras criaturas, estatico
            state.elspeth_emblem = True  # lido so' pelo modelo de combate (P/T e voo dos nossos bloqueadores)
        else:
            add_loyalty(state, pw, 1, log, reason="elspeth_plus1")
            make_pw_token(state, "Soldier Token", 3, log)

    elif pw == "Kaya, Intangible Slayer":
        # +2 sempre (drenagem real + cresce lealdade, sem downside - nao ha
        # razao pra preferir o modo "0" de compra, que nao drena).
        add_loyalty(state, pw, 2, log, reason="kaya_plus2")
        state.pw_life_lost_opponent_total += 3
        state.pw_life_gained_total += 3
        state.life += 3  # "you gain 3 life" -- vida propria rastreada (lida pelo modelo de combate)

    elif pw == "Liliana, Dreadhorde General":
        if loy >= 9:
            add_loyalty(state, pw, -9, log, reason="liliana_ultimate")
            state.pw_ultimates_used_total += 1
            state.pw_wipe_proxy_total += 1  # oponente sacrifica quase tudo
            if attack_model_on(state):
                # "Each opponent chooses a permanent they control of each
                # permanent type and sacrifices the rest." -- cada oponente
                # fica com a MELHOR criatura dele (escolha dele).
                for j, b in enumerate(state.opp_boards):
                    if b:
                        keep = max(b, key=lambda c: (c["p"], c["cmd"]))
                        for c in list(b):
                            if c is not keep:
                                _opp_remove_creature(state, j, c, how="sacrifice")
        else:
            add_loyalty(state, pw, 1, log, reason="liliana_plus1")
            make_pw_token(state, "Zombie Token", 1, log)

    elif pw == "Narset, Parter of Veils":
        # -2: olha 4, pega 1 nao-criatura-nao-terreno - carta real na mao.
        if loy >= 2:
            add_loyalty(state, pw, -2, log, reason="narset_minus2")
            state.draw(1)
            state.pw_draws_total += 1

    elif pw == "Nicol Bolas, Dragon-God":
        # Estatico real "has all loyalty abilities of all other
        # planeswalkers on the battlefield" NAO modelado - exigiria um
        # dispatch combinatorio (Bolas ganhando as habilidades de QUALQUER
        # outro PW simultaneamente em campo) desproporcional ao valor real:
        # a Bridge so acerta 1 permanente por gatilho, entao ter 2+
        # planeswalkers vivos ao mesmo tempo (nenhum morreu ainda) e' raro
        # por padrao. Documentado, nao omitido silenciosamente.
        if loy >= 8:
            add_loyalty(state, pw, -8, log, reason="bolas_ultimate")
            state.pw_ultimates_used_total += 1  # oponente sem lendaria perde o jogo - sinal de finisher
        else:
            add_loyalty(state, pw, 1, log, reason="bolas_plus1")
            state.draw(1)
            state.pw_draws_total += 1

    elif pw == "Oko, the Ringleader":
        # -1: cria Elk 3/3 real. +1: compra 2 descarta 2 (sem "crime"
        # rastreado, assume o pior caso - liquido 0 cartas, sem valor
        # numerico, so mantem a lealdade se -1 nao for pagavel).
        if loy >= 2:
            add_loyalty(state, pw, -1, log, reason="oko_minus1")
            make_pw_token(state, "Elk Token", 1, log)
        else:
            add_loyalty(state, pw, 1, log, reason="oko_plus1")

    elif pw == "Tamiyo, Compleated Sage":
        # -X: exila carta do CEMITERIO com MV=X, cria token copia dela -
        # recursao real (mesma categoria da regra de RECURSION). Escolhe o
        # maior X pagavel que tenha alvo real no cemiterio.
        gy_creatures = [c for c in state.graveyard if C(c).type in ("Creature", "Artifact", "Enchantment", "Planeswalker")]
        by_mv = {}
        for c in gy_creatures:
            if C(c).mv not in by_mv:
                by_mv[C(c).mv] = c
        affordable = sorted((mv, c) for mv, c in by_mv.items() if mv <= loy)
        if affordable:
            mv, target = affordable[-1]
            add_loyalty(state, pw, -mv, log, reason="tamiyo_sage_minusX")
            state.graveyard.remove(target)
            state.battlefield.append(target)  # token copia - simplificado como o mesmo nome em campo
            if C(target).type == "Planeswalker":
                planeswalker_enters(state, target, log)
            elif C(target).type == "Creature":
                creature_enters(state, target, log)
            state.pw_recursion_total += 1
            log.append({"trigger": "tamiyo_sage_token_copy", "of": target, "turn": state.turn})
        elif loy >= 7:
            add_loyalty(state, pw, -7, log, reason="tamiyo_sage_ultimate")
            state.pw_ultimates_used_total += 1  # Tamiyo's Notebook - sem efeito numerico modelado
        else:
            add_loyalty(state, pw, 1, log, reason="tamiyo_sage_plus1")
            if attack_model_on(state):
                # "+1: Tap up to one target artifact or creature. It doesn't
                # untap during its controller's next untap step."
                _freeze_biggest_threats(state, 1, log, source="tamiyo_sage_plus1")

    elif pw == "Tamiyo, Field Researcher":
        if loy >= 7:
            add_loyalty(state, pw, -7, log, reason="tamiyo_researcher_ultimate")
            state.pw_ultimates_used_total += 1
            state.draw(3)
            state.pw_draws_total += 3  # emblem de cast gratis nao modelado (sem alvo/limite claro)
        else:
            add_loyalty(state, pw, 1, log, reason="tamiyo_researcher_plus1")
            if attack_model_on(state):
                # "+1: Choose up to two target creatures. Until your next
                # turn, whenever either of those creatures deals combat
                # damage, you draw a card." -- escolhe as 2 nossas de maior
                # poder que ja' podem atacar (sem doenca) primeiro.
                cands = sorted(_our_creature_instances(state),
                               key=lambda x: (not _is_sick(state, x), _pt(state, x)[0]), reverse=True)
                state.tamiyo_fr_marked = cands[:2]

    elif pw == "Teferi, Hero of Dominaria":
        if loy >= 8:
            add_loyalty(state, pw, -8, log, reason="teferi_hero_ultimate")
            state.pw_ultimates_used_total += 1
            # Emblema "Whenever you draw a card, exile target permanent an
            # opponent controls" -- tem alvo real so' no modelo de combate
            # (ver GameState.draw); fora dele segue sem efeito numerico.
            state.teferi_hero_emblem = True
        else:
            add_loyalty(state, pw, 1, log, reason="teferi_hero_plus1")
            state.draw(1)
            state.pw_draws_total += 1  # untap de 2 lands no proximo end step - sem valor de instant-speed modelado

    elif pw == "Teferi, Temporal Archmage":
        if loy >= 10:
            add_loyalty(state, pw, -10, log, reason="teferi_archmage_ultimate")
            state.pw_ultimates_used_total += 1  # emblem de ativar loyalty a qualquer momento - sem instant-speed modelado
        else:
            add_loyalty(state, pw, 1, log, reason="teferi_archmage_plus1")
            state.draw(1)
            state.pw_draws_total += 1  # olha 2, fica com 1 - carta real selecionada

    elif pw == "Teferi, Time Raveler":
        # -3: "up to one target" bounce (opcional) + compra 1 - sempre pode
        # escolher ZERO alvos e so comprar, sem downside.
        if loy >= 3:
            add_loyalty(state, pw, -3, log, reason="teferi_raveler_minus3")
            state.draw(1)
            state.pw_draws_total += 1
            if attack_model_on(state):
                # "-3: Return up to one target artifact, creature, or
                # enchantment to its owner's hand." Agora ha' alvo real.
                _bounce_biggest_threat(state, log, source="teferi_raveler_minus3")
        else:
            add_loyalty(state, pw, 1, log, reason="teferi_raveler_plus1")  # flash pra sorceries - sem valor de instant-speed modelado

    elif pw == "Teferi, Who Slows the Sunset":
        if loy >= 7:
            add_loyalty(state, pw, -7, log, reason="teferi_sunset_ultimate")
            state.pw_ultimates_used_total += 1
            state.teferi_sunset_emblem = True
        elif loy >= 2:
            add_loyalty(state, pw, -2, log, reason="teferi_sunset_minus2")
            state.draw(1)
            state.pw_draws_total += 1
        else:
            add_loyalty(state, pw, 1, log, reason="teferi_sunset_plus1")
            state.pw_life_gained_total += 2
            state.life += 2  # "You gain 2 life."

    elif pw == "The Eternal Wanderer":
        # "0" custa 0 lealdade, cria Samurai 2/2 double strike de graca -
        # sempre a melhor escolha (sem custo, sem risco).
        add_loyalty(state, pw, 0, log, reason="eternal_wanderer_zero")
        make_pw_token(state, "Samurai Token", 1, log)

    elif pw == "Ugin, the Spirit Dragon":
        if loy >= 10:
            add_loyalty(state, pw, -10, log, reason="ugin_ultimate")
            state.pw_ultimates_used_total += 1
            state.pw_life_gained_total += 7
            state.life += 7  # "You gain 7 life"
            state.draw(7)
            state.pw_draws_total += 7
            # "put up to seven permanent cards from your hand onto the
            # battlefield" - mesmo padrao do Last March of the Ents no
            # Beorn (coloca em campo de graca, sem pagar custo).
            free_permanents = [c for c in state.hand if C(c).type != "Instant" and C(c).type != "Sorcery"][:7]
            # Entram TODAS ao mesmo tempo; os ETBs (Deepglow Skate/Carth,
            # via creature_enters) so' resolvem depois -- o Deepglow ve os
            # planeswalkers que entraram junto com ela.
            for c in free_permanents:
                state.hand.remove(c)
                state.battlefield.append(c)
                if C(c).type == "Planeswalker":
                    planeswalker_enters(state, c, log)
                log.append({"trigger": "ugin_ultimate_free_permanent", "card": c, "turn": state.turn})
            for c in free_permanents:
                if C(c).type == "Creature":
                    creature_enters(state, c, log)
        else:
            add_loyalty(state, pw, 2, log, reason="ugin_plus2")
            state.pw_removal_proxy_total += 1  # "3 dano a qualquer alvo"
            if attack_model_on(state):
                # Com criatura de oponente em campo, os 3 de dano matam a
                # maior ameaca com resistencia <= 3.
                _ugin_ping(state, log)

    elif pw == "Vraska, Betrayal's Sting":
        # "0": compra 1 + proliferate - sempre a melhor escolha (sem custo
        # de lealdade, e agora proliferate tem alvo real - lealdade dos
        # OUTROS planeswalkers que controla).
        add_loyalty(state, pw, 0, log, reason="vraska_zero")
        state.draw(1)
        state.pw_draws_total += 1
        proliferate_loyalty(state, log, source="vraska")

def try_chain_veil_activation(state: GameState, log: List[Dict]):
    """Achado real: '{4}, {T}: For each planeswalker you control, you
    may activate one of its loyalty abilities once this turn as though
    none of its loyalty abilities have been activated this turn.'
    Habilidade ativada real, paga -- nunca era conjurada com efeito
    algum (so' entrava em campo). So' vale pagar se ha' planeswalker
    real em campo pra se beneficiar."""
    if "The Chain Veil" not in state.battlefield or state.chain_veil_activated_this_turn:
        return
    if not state.loyalty:
        return
    if remaining_mana(state) < 4:
        return
    state.mana_spent_this_turn += 4
    state.chain_veil_activated_this_turn = True
    state.chain_veil_activations_total += 1
    log.append({"trigger": "chain_veil_activation", "turn": state.turn})

def try_urza_saga_tick(state: GameState, log: List[Dict]):
    """Achado real: Saga real (Read ahead) 100% ausente. Capitulo I:
    scry 4 (nao modelado, sem infra de scry neste arquivo) + revela o
    topo, planeswalker vai pra mao. Capitulo II: planeswalker MV<=6 da
    mao pra campo de graca. Capitulo III: libera ativacao dupla de
    lealdade so' neste turno (via extra_pw_activation_sources()), depois
    sacrifica (regra real de Saga: 'Sacrifice after III')."""
    if "Urza Assembles the Titans" not in state.battlefield:
        return
    if state.urza_last_ticked_turn == state.turn:
        return
    state.urza_last_ticked_turn = state.turn
    # CORRIGIDO 2026-09-24 (Regra #3, conceito compartilhado "marcador"):
    # lore counter e' marcador colocado num permanente nosso -- Doubling
    # Season/Vorinclex/Innkeeper nivel 3 dobram (antes sempre +1). Com
    # Read ahead (CR 702.155a), no turno em que ENTRA so' dispara o
    # capitulo cujo numero e' EXATAMENTE o numero de marcadores (escolha
    # modelada: sempre "1", como antes -> com 1 dobrador entra com 2 e so'
    # o capitulo II dispara). Nos turnos seguintes (CR 714.2b), dispara
    # todo capitulo N com antes < N <= depois.
    entering = state.urza_chapter == 0
    n = counter_doubler_multiplier(state)
    old = state.urza_chapter
    new = old + n
    state.urza_chapter = min(new, 3)
    _counters_put(state, n, log, source="urza_lore")
    for ch in range(old + 1, min(new, 3) + 1):
        if entering and ch != new:
            continue
        if ch == 1:
            if state.library and C(state.library[0]).type == "Planeswalker":
                state.hand.append(state.library.pop(0))
                state.urza_pw_tutored_total += 1
        elif ch == 2:
            pw_in_hand = [c for c in state.hand if C(c).type == "Planeswalker" and C(c).mv <= 6]
            if pw_in_hand:
                best = max(pw_in_hand, key=lambda c: C(c).mv)
                state.hand.remove(best)
                state.battlefield.append(best)
                planeswalker_enters(state, best, log)
                state.urza_pw_cheated_total += 1
        elif ch == 3:
            state.urza_chapter_iii_this_turn = True
        log.append({"trigger": "urza_saga_chapter", "chapter": ch, "turn": state.turn})
    if new >= 3 and "Urza Assembles the Titans" in state.battlefield:
        # "Sacrifice after III" (CR 714.4, acao baseada em estado)
        state.battlefield.remove("Urza Assembles the Titans")
        state.graveyard.append("Urza Assembles the Titans")

def extra_pw_activation_sources(state: GameState) -> int:
    """Achado real: 3 fontes reais e distintas de ativar lealdade mais de
    1x por turno, todas aditivas (cada uma concede 'mais uma' ativacao,
    nao se sobrepoe): Oath of Teferi (estatico, sempre liga enquanto em
    campo), The Chain Veil (pago neste turno, {4},{T}) e Urza Assembles
    the Titans capitulo III (so' no turno em que resolve)."""
    extra = 0
    # CORRIGIDO 2026-09-24 (ruling oficial da Oath of Teferi: "If you
    # somehow control more than one Oath of Teferi, you won't be able to
    # activate abilities of planeswalkers you control more than twice in
    # one turn"): Oath e Urza capitulo III dizem a MESMA coisa ("twice
    # ... rather than only once") -- nao somam entre si. So' a Chain Veil
    # ("as though none of its loyalty abilities have been activated")
    # soma de verdade (rulings da Chain Veil: cada resolucao = +1).
    if state.has("Oath of Teferi") or state.urza_chapter_iii_this_turn:
        extra += 1
    if state.chain_veil_activated_this_turn:
        extra += 1
    return extra

def activate_planeswalkers(state: GameState, log: List[Dict]):
    # Carth the Lion: "Planeswalkers' loyalty abilities you activate cost
    # an additional {1} to activate." Achado real 2026-09-01 (leitura
    # linha-a-linha, "compile TUDO"): estatico real, sem excecao pros
    # NOSSOS proprios planeswalkers - aplicado como custo de mana real
    # antes de CADA ativacao (inclusive as extras, se sobrar mana), se
    # nao sobrar mana, essa ativacao especifica e' pulada nesse turno,
    # sem gastar loyalty de graca.
    carth_tax = 1 if state.has("Carth the Lion") else 0
    extra = extra_pw_activation_sources(state)
    for pw in list(state.loyalty.keys()):
        for _ in range(1 + extra):
            if pw not in state.battlefield:
                break  # morreu por outro efeito nesse meio tempo (Deepglow Skate etc. nao removem, so seguranca)
            if carth_tax and remaining_mana(state) < carth_tax:
                break
            if carth_tax:
                state.mana_spent_this_turn += carth_tax
            resolve_planeswalker(state, pw, log)

# =========================================================
# TURNO
# =========================================================

def main_phase(state: GameState, log: List[Dict]):
    # Subir de nivel a Innkeeper's Talent primeiro (sorcery speed, pilha
    # vazia) - se alcancar nivel 3 neste turno, o dobro de counter so vale
    # pra gatilhos QUE AINDA VAO ACONTECER neste turno em diante (nao
    # retroage sobre o upkeep da Bridge, que ja resolveu antes do main
    # phase, mesma ordem real do jogo).
    try_level_up_innkeepers_talent(state, log)

    # Urza (se ja estava em campo de um turno anterior) e Chain Veil (pago)
    # precisam resolver ANTES da ativacao de lealdade, pra que a 2a/3a
    # ativacao por planeswalker (extra_pw_activation_sources) ja valha
    # neste mesmo turno.
    try_urza_saga_tick(state, log)
    try_chain_veil_activation(state, log)

    # Ativa a habilidade de lealdade de cada planeswalker em campo primeiro
    # (velocidade de feitico, pilha vazia, mesmo momento real que um
    # jogador faria isso) - qualquer compra/mana disso alimenta o resto do
    # turno.
    activate_planeswalkers(state, log)

    # protetores primeiro (sao baratos e habilitam a Bridge)
    protection_cards = [c for c in state.hand if has_tag(c, "protection_shroud") and can_cast(state, c)]
    for c in sorted(protection_cards, key=lambda c: C(c).mv):
        state.hand.remove(c)
        state.mana_spent_this_turn += C(c).mv
        state.battlefield.append(c)
        log.append({"action": "cast", "card": c, "turn": state.turn})

    try_fabled_passage(state, log)

    # Bridge via main phase normal, se nao foi flashada nesse ciclo.
    # Sob HOLD_FOR_FLASH_POLICY, se um habilitador de flash ja esta em
    # campo, o jogador segura a Bridge de proposito (nao conjura normal
    # mesmo pagavel) e espera a janela de flash no end step alheio.
    skip_normal_cast = HOLD_FOR_FLASH_POLICY and choose_flash_enabler(state) is not None
    if not state.bridge_in_play and not skip_normal_cast and can_cast(state, COMMANDER):
        cast_bridge(state, log, via_flash=False)

    # Se ja tem habilitador de flash em campo e a Bridge ainda nao saiu,
    # o jogador segura mana de proposito pra linha de flash no end step
    # alheio (plano de jogo explicito do usuario) - nao gasta tudo no
    # resto da mao.
    reserved = 0
    if not state.bridge_in_play:
        enabler = choose_flash_enabler(state)
        if enabler is not None:
            reserved = FLASH_ENABLER_COST[enabler] + bridge_effective_mv(state)

    # Modelo de combate: remocao/wipe so' sai com alvo real (criatura de
    # oponente ameacando), nunca "de graca" -- e com efeito de verdade dos 2
    # lados da mesa. Sem o modelo, o loop generico abaixo segue igual.
    if attack_model_on(state):
        _cast_defensive_spells(state, log, reserved)

    # resto da mao, ordem generica por CMC crescente, respeitando a reserva
    for _ in range(8):
        budget = remaining_mana(state) - reserved
        castables = [c for c in state.hand if c != COMMANDER and can_cast(state, c) and C(c).mv <= budget
                     and not (attack_model_on(state) and _held_for_threat(c))]
        if not castables:
            break
        castables.sort(key=lambda c: C(c).mv)
        choice = castables[0]
        state.hand.remove(choice)
        state.mana_spent_this_turn += C(choice).mv

        # Achados reais 2026-09-01 (leitura linha-a-linha, "compile TUDO" -
        # a nota antiga do docstring listava estas 5 fontes de proliferate
        # como deferidas por volume; implementadas aqui reusando
        # `proliferate_loyalty()`, ja testada pro Evolution Sage/Vraska):
        # Flux Channeler/Inexorable Tide ("whenever you cast a
        # noncreature/any spell, proliferate") + Mutational
        # Advantage/Ripples of Potential (proliferate no proprio efeito ao
        # serem conjuradas). Ichormoon Gauntlet permanece fora de escopo -
        # concede uma habilidade de lealdade NOVA a cada um dos 17
        # planeswalkers (exigiria reestruturar a logica hardcoded por-PW
        # de `resolve_planeswalker()`, escopo desproporcional ao resto
        # desta rodada), ver docstring.
        # Fontes independentes (permanentes DIFERENTES) - proliferam
        # separadamente se ambas estiverem em campo, nao mutuamente exclusivas.
        if state.has("Inexorable Tide"):
            proliferate_loyalty(state, log, source="inexorable_tide")
        if state.has("Flux Channeler") and C(choice).type != "Creature":
            proliferate_loyalty(state, log, source="flux_channeler")
        if choice in ("Mutational Advantage", "Ripples of Potential"):
            proliferate_loyalty(state, log, source=choice.lower().replace(" ", "_").replace(",", ""))

        if has_tag(choice, "removal") or has_tag(choice, "counterspell") or has_tag(choice, "wipe"):
            # Achado real: essas 11 cartas nunca contavam pra metrica de
            # interacao (Regra 1 ja corretamente nao aplica o efeito
            # destrutivo/de contramagia sem alvo/spell de oponente real,
            # mas nem o "foi conjurada" era contado, ao contrario de todos
            # os outros decks desta sessao).
            state.interaction_spells_cast_total += 1

        if C(choice).type in ("Instant", "Sorcery"):
            state.graveyard.append(choice)
        else:
            state.battlefield.append(choice)
            if choice == "Urza Assembles the Titans":
                try_urza_saga_tick(state, log)  # capitulo I dispara no proprio turno do cast
            if C(choice).type == "Creature":
                creature_enters(state, choice, log)
        if choice in LAND_FETCH_SPELLS:
            do_land_fetch_spell(state, choice, log)
        log.append({"action": "cast", "card": choice, "turn": state.turn})

def sphinx_additional_beginning_phase(state: GameState, log: List[Dict]):
    """Sphinx of the Second Sun (oraculo real, Scryfall 2026-09-24): "At the
    beginning of each of your postcombat main phases, there is an
    additional beginning phase after this phase. (The beginning phase
    includes the untap, upkeep, and draw steps.)" Rulings oficiais: no
    untap voce desvira seus permanentes; tudo que dispara "at the beginning
    of your upkeep" dispara; voce compra no draw step; efeitos "until your
    next turn" NAO expiram (e' o mesmo turno); depois da fase adicional o
    jogo vai pro ending phase (NAO ha' outro main phase -- nada de
    feitico/lealdade depois dela).

    - Untap: terrenos/rochas desviram -> a mana volta a estar disponivel,
      mas so' pra velocidade de instantaneo (sobra como `mana_held_back`,
      ex.: flashar a Bridge no end step de um oponente). Criaturas que
      atacaram desviram e podem bloquear no turno dos oponentes.
    - Upkeep: gatilho da The Prismatic Bridge de novo. Paradox Haze NAO
      dobra este ("enchanted player's FIRST upkeep each turn").
    - Draw: compra 1.
    Planeswalker que a Bridge poe em campo aqui so' ativa no proximo turno
    (sem main phase depois)."""
    state.sphinx_extra_beginning_phases_total += 1
    # untap step
    state.mana_spent_this_turn = 0
    state.tapped_lands_this_turn = set()
    if attack_model_on(state):
        state.our_tapped = []
    # upkeep step
    if state.bridge_in_play:
        bridge_upkeep_trigger(state, log)
    # draw step
    state.draw(1)
    log.append({"trigger": "sphinx_additional_beginning_phase", "turn": state.turn})


def play_turn(state: GameState, turn: int, game_log: List[List[Dict]], skip_legacy_removal: bool = False):
    """`skip_legacy_removal`: usado SO' pelo modo de resiliencia
    (`simulate_one_with_interaction`) -- desliga `resolve_removal_round`
    (sistema ANTIGO, especifico deste deck) pra evitar empilhar com o
    novo sistema padronizado de 7 categorias (decisao do usuario,
    2026-09-20: modo de resiliencia SUBSTITUI o antigo, nao soma).
    Default `False` preserva 100% o comportamento de todo call site
    existente (`simulate_one` nunca passa este argumento)."""
    state.turn = turn
    state.land_played = False
    state.mana_spent_this_turn = 0
    state.tapped_lands_this_turn = set()
    state.chain_veil_activated_this_turn = False
    state.urza_chapter_iii_this_turn = False
    state.loyalty_activated_this_turn = False
    log = []
    if attack_model_on(state):
        # Meu untap step (CR 502.3): so' aqui desviram as criaturas que
        # atacaram no meu turno anterior -- durante os turnos dos oponentes
        # elas continuaram viradas e nao puderam bloquear.
        state.our_tapped = []
        state.new_tokens_this_turn = {}
        state.tamiyo_fr_marked = []  # +1 da Tamiyo FR vale "until your next turn"

    # Linha de flash no end step do oponente anterior (ver docstring: modelado
    # como acontecendo ANTES da rodada de remocao deste turno, entao a Bridge
    # flashada escapa da rodada de remocao que precede seu primeiro gatilho)
    if can_flash_bridge(state):
        cast_bridge(state, log, via_flash=True)

    if not skip_legacy_removal:
        resolve_removal_round(state, log)

    if state.bridge_in_play:
        n_triggers = 2 if state.has("Paradox Haze") else 1
        for _ in range(n_triggers):
            bridge_upkeep_trigger(state, log)

    state.draw(1)
    if state.teferi_sunset_emblem:
        # Ultimate de Teferi, Who Slows the Sunset: "You draw a card during
        # each opponent's draw step." Este motor so avanca os PROPRIOS
        # turnos - modelado como N_OPPONENTS compras extras por ciclo do
        # nosso turno, mesma premissa/convencao ja usada em
        # REMOVAL_CHANCE_PER_OPPONENT (ver docstring do arquivo).
        state.draw(N_OPPONENTS)
        state.pw_draws_total += N_OPPONENTS
    play_land(state, log)
    main_phase(state, log)
    if attack_model_on(state):
        # Fase de combate (depois do main 1): gatilho "at the beginning of
        # combat on your turn" da Innkeeper's Talent + nosso ataque.
        our_combat_step(state, log)

    # Main pos-combate (Regra #6: ordem real das fases). Nenhuma conjuracao
    # modelada aqui (tudo sai no main 1), mas e' o momento do gatilho do
    # Sphinx of the Second Sun -- e a fase inicial adicional vem DEPOIS
    # deste main e ANTES do end step.
    if "Sphinx of the Second Sun" in state.battlefield:
        sphinx_additional_beginning_phase(state, log)

    # End step. Atraxa, Praetors' Voice: "At the beginning of your end step,
    # proliferate." Achado real 2026-09-24: nunca implementado (a carta so'
    # tinha a tag "proliferate", nenhum dispatch lia). Mesmo helper das
    # outras 6 fontes de proliferate (lealdade + +1/+1 no modelo de combate).
    if state.has("Atraxa, Praetors' Voice"):
        proliferate_loyalty(state, log, source="atraxa_end_step")
    # The Chain Veil: "At the beginning of your end step, if you didn't
    # activate a loyalty ability of a planeswalker this turn, you lose 2
    # life." Achado real 2026-09-24: so' a 2a habilidade dela existia.
    if state.has("The Chain Veil") and not state.loyalty_activated_this_turn:
        state.life -= 2
        state.chain_veil_life_lost_total += 2

    if attack_model_on(state):
        state.pw_turns_alive_total += len(state.loyalty)
        if any(n in PILLOWFORT_CARDS for n in state.battlefield):
            state.pillowfort_turns_total += 1
            if state.pillowfort_first_turn is None:
                state.pillowfort_first_turn = state.turn

    # Mana nao gasta neste turno fica destapada ate o MEU proximo untap
    # step (CR 500.1) - e a mana real disponivel pra flashar algo no end
    # step de um oponente antes do meu proximo turno.
    state.mana_held_back = max(0, total_mana(state) - state.mana_spent_this_turn)

    game_log.append(log)

# =========================================================
# SIMULACAO
# =========================================================

def build_decklist(with_greater_auramancy: bool) -> str:
    if not with_greater_auramancy:
        return DECKLIST_TEXT
    # troca 1 carta de baixo synergy score/pouco impacto pela Greater Auramancy
    # (The Peregrine Dynamo - unica criatura sem nenhuma tag de sinergia)
    return DECKLIST_TEXT.replace("1 The Peregrine Dynamo\n", "1 Greater Auramancy\n")

def simulate_one(seed: int, turns: int, with_greater_auramancy: bool) -> Dict:
    rng = random.Random(seed)
    decklist = build_decklist(with_greater_auramancy)
    deck = parse_decklist(decklist)
    assert len(deck) == 99, f"Mainboard deveria ser 99, deu {len(deck)}"
    rng.shuffle(deck)
    state = GameState(rng=rng, library=deck, with_greater_auramancy=with_greater_auramancy)

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
    # Achado real 2026-09-18 (mesma convencao dos goldfishes manuais do
    # usuario no Archidekt): 1o mulligan e' GRATIS, so' o 2o+ bota cartas.
    penalty = max(0, mulligans - 1)
    if penalty:
        bottoms = choose_bottom(state.hand, penalty)
        for c in bottoms:
            state.hand.remove(c)
            state.library.append(c)
        rng.shuffle(state.library)

    game_log = []
    t = 0
    turns_played = 0
    while turns_played < turns:
        t += 1
        play_turn(state, t, game_log)
        turns_played += 1
        while state.extra_turns_pending > 0 and turns_played < turns:
            # Sphinx of the Second Sun: "take an extra turn after this
            # one" - achado real 2026-09-01. Inserida imediatamente
            # apos o turno que a disparou (mesma convencao ja usada nos
            # simuladores do Maralen/Megatron desta sessao).
            state.extra_turns_pending -= 1
            t += 1
            play_turn(state, t, game_log)
            turns_played += 1

    return {
        "seed": seed,
        "mulligans": mulligans,
        "bridge_cast_turn": state.bridge_cast_turn,
        "bridge_first_cast_turn": state.bridge_first_cast_turn,
        "bridge_flash_cast": state.bridge_flash_cast,
        "bridge_cast_count": state.bridge_cast_count,
        "bridge_in_play_end": state.bridge_in_play,
        "bridge_removed_count": state.bridge_removed_count,
        "bridge_triggers": state.bridge_triggers,
        "bridge_hits_creature": state.bridge_hits_creature,
        "bridge_hits_planeswalker": state.bridge_hits_planeswalker,
        "first_pw_hit_turn": state.first_pw_hit_turn,
        "bridge_no_hit": state.bridge_no_hit_empty_library,
        "protectors_removed_count": state.protectors_removed_count,
        "removal_attempts_total": state.removal_attempts_total,
        "lands_played_total": state.lands_played_total,
        "pw_activations_total": state.pw_activations_total,
        "pw_draws_total": state.pw_draws_total,
        "pw_tokens_created_total": state.pw_tokens_created_total,
        "pw_life_gained_total": state.pw_life_gained_total,
        "pw_life_lost_opponent_total": state.pw_life_lost_opponent_total,
        "pw_removal_proxy_total": state.pw_removal_proxy_total,
        "pw_wipe_proxy_total": state.pw_wipe_proxy_total,
        "pw_recursion_total": state.pw_recursion_total,
        "pw_ultimates_used_total": state.pw_ultimates_used_total,
        "pw_deaths_total": state.pw_deaths_total,
        "planeswalkers_in_play_end": len(state.loyalty),
        "innkeepers_talent_in_play": "Innkeeper's Talent" in state.battlefield,
        "innkeepers_talent_level_end": state.innkeepers_talent_level,
        # Achados reais 2026-09-01 (leitura linha-a-linha completa do oraculo):
        "sphinx_extra_beginning_phases_total": state.sphinx_extra_beginning_phases_total,
        "carth_tutors_total": state.carth_tutors_total,
        # Achados reais da auditoria oraculo-por-oraculo 2026-09-13/14:
        "interaction_spells_cast_total": state.interaction_spells_cast_total,
        "chain_veil_activations_total": state.chain_veil_activations_total,
        "urza_pw_tutored_total": state.urza_pw_tutored_total,
        "urza_pw_cheated_total": state.urza_pw_cheated_total,
        "urza_chapter_end": state.urza_chapter,
        # Achados reais 2026-09-24 (rodada do modelo de combate):
        "all_will_be_one_triggers_total": state.all_will_be_one_triggers_total,
        "all_will_be_one_face_damage_total": state.all_will_be_one_face_damage_total,
    }

def run_batch(n=2000, turns=10, with_greater_auramancy=False, seed_base=3000000, label=""):
    import statistics
    results = [simulate_one(seed_base + i, turns, with_greater_auramancy) for i in range(n)]

    bridge_turns = [r["bridge_cast_turn"] for r in results if r["bridge_cast_turn"] is not None]
    first_cast_turns = [r["bridge_first_cast_turn"] for r in results if r["bridge_first_cast_turn"] is not None]
    never = n - len(bridge_turns)
    flash_casts = sum(1 for r in results if r["bridge_flash_cast"])
    total_triggers = sum(r["bridge_triggers"] for r in results)
    total_hits_creature = sum(r["bridge_hits_creature"] for r in results)
    total_hits_pw = sum(r["bridge_hits_planeswalker"] for r in results)
    end_in_play = sum(1 for r in results if r["bridge_in_play_end"])
    avg_removed = sum(r["bridge_removed_count"] for r in results) / n
    avg_protectors_removed = sum(r["protectors_removed_count"] for r in results) / n
    avg_attempts = sum(r["removal_attempts_total"] for r in results) / n

    print(f"=== Prismatic Bridge Goldfish v1 ({label}) — n={n}, turns={turns} ===")
    print(f"Greater Auramancy no deck: {with_greater_auramancy}")
    print(f"Avg mulligans: {sum(r['mulligans'] for r in results)/n:.2f}")
    print(f"Bridge nunca conjurada em {turns} turnos: {100*never/n:.1f}%")
    if first_cast_turns:
        print(f"Turno medio da PRIMEIRA conjuracao da Bridge: {statistics.mean(first_cast_turns):.2f} | mediana: {statistics.median(first_cast_turns)}")
    if bridge_turns:
        print(f"Turno medio da ULTIMA conjuracao (inclui recasts pos-remocao, taxa de comandante +2 cada vez): {statistics.mean(bridge_turns):.2f} | mediana: {statistics.median(bridge_turns)}")
    print(f"Conjurada via flash (end step anterior): {100*flash_casts/n:.1f}% das partidas")
    print(f"Avg gatilhos de upkeep da Bridge por partida: {total_triggers/n:.2f}")
    print(f"  Acertos em criatura: {total_hits_creature} | em planeswalker: {total_hits_pw} | total: {total_hits_creature+total_hits_pw}")
    print(f"% da Bridge ainda em campo no fim da simulacao: {100*end_in_play/n:.1f}%")
    print(f"Avg vezes que a Bridge foi removida por partida: {avg_removed:.2f}")
    print(f"Avg vezes que um protetor (Sterling Grove/Greater Auramancy) foi removido: {avg_protectors_removed:.2f}")
    print(f"Avg tentativas de remocao do oponente por partida (premissa: {REMOVAL_CHANCE_PER_OPPONENT*100:.0f}%/oponente/turno, {N_OPPONENTS} oponentes): {avg_attempts:.2f}")

    pw_hit_turns = [r["first_pw_hit_turn"] for r in results if r["first_pw_hit_turn"] is not None]
    from collections import Counter
    c = Counter(pw_hit_turns)
    print(f"\n--- Bridge colocou planeswalker em jogo (1o acerto de PW via gatilho de upkeep) ---")
    for t in [6, 7, 8]:
        cum = sum(v for k, v in c.items() if k <= t)
        print(f"  Chance acumulada ate o turno {t}: {100*cum/n:.1f}%")
    never_pw = n - len(pw_hit_turns)
    print(f"  Nunca acertou planeswalker em {turns} turnos: {100*never_pw/n:.1f}%")

    # Achado real 2026-08-28 (usuario: "Preciso que os counters de lealdade
    # e ativacoes de planeswalker sejam sempre contabilizados") - antes
    # NENHUMA habilidade de planeswalker era simulada, so se a Bridge
    # acertava um. Agora os 17 planeswalkers tem lealdade real e ativam
    # uma habilidade real por turno em campo.
    print(f"\n--- Planeswalkers (lealdade + ativacoes reais, regra nova) ---")
    print(f"Avg ativacoes de habilidade de planeswalker por partida: {sum(r['pw_activations_total'] for r in results)/n:.2f}")
    print(f"Avg planeswalkers vivos no fim da simulacao: {sum(r['planeswalkers_in_play_end'] for r in results)/n:.2f}")
    print(f"Avg mortes de planeswalker (lealdade a 0) por partida: {sum(r['pw_deaths_total'] for r in results)/n:.2f}")
    print(f"Avg ultimates usados por partida: {sum(r['pw_ultimates_used_total'] for r in results)/n:.2f}")
    print(f"RECURSION (via Tamiyo, Compleated Sage -X): {sum(r['pw_recursion_total'] for r in results)/n:.2f}")
    print(f"DRAW: avg compras via planeswalker: {sum(r['pw_draws_total'] for r in results)/n:.2f}")
    print(f"Avg tokens criados via planeswalker: {sum(r['pw_tokens_created_total'] for r in results)/n:.2f}")
    print(f"Avg vida ganha via planeswalker: {sum(r['pw_life_gained_total'] for r in results)/n:.2f} | "
          f"vida perdida do oponente (proxy): {sum(r['pw_life_lost_opponent_total'] for r in results)/n:.2f}")
    print(f"INTERACTION: avg remocao proxy (Ashiok/Ugin, sem alvo real de oponente): "
          f"{sum(r['pw_removal_proxy_total'] for r in results)/n:.2f} | wipe proxy (Elspeth/Liliana ultimate): "
          f"{sum(r['pw_wipe_proxy_total'] for r in results)/n:.2f}")
    it_in_play = sum(1 for r in results if r["innkeepers_talent_in_play"])
    if it_in_play:
        it_lvl3 = sum(1 for r in results if r["innkeepers_talent_level_end"] >= 3)
        print(f"Innkeeper's Talent em campo em {100*it_in_play/n:.1f}% dos jogos, alcancou nivel 3 "
              f"(dobra TODOS os counters, inclusive lealdade de planeswalker ao entrar) em "
              f"{100*it_lvl3/n:.1f}%")
    print(f"Avg proliferates via Flux Channeler/Inexorable Tide/Mutational Advantage/Ripples of Potential "
          f"(achado 2026-09-01, implementado nesta rodada): "
          f"{sum(r['pw_activations_total'] for r in results)/n:.2f} ativacoes de PW no total (inclui esses proliferates)")
    print(f"Sphinx of the Second Sun (fase inicial adicional -- untap/upkeep com Bridge/compra -- por turno em campo): "
          f"{sum(r['sphinx_extra_beginning_phases_total'] for r in results)/n:.3f} avg | "
          f"{100*sum(1 for r in results if r['sphinx_extra_beginning_phases_total']>0)/n:.1f}% dos jogos")
    print(f"Carth the Lion (tutor de planeswalker no ETB): {sum(r['carth_tutors_total'] for r in results)/n:.2f} avg | "
          f"{100*sum(1 for r in results if r['carth_tutors_total']>0)/n:.1f}% dos jogos")
    print(f"All Will Be One (gatilhos por marcador colocado; dano no oponente = proxy): "
          f"{sum(r['all_will_be_one_triggers_total'] for r in results)/n:.2f} gatilhos avg | "
          f"{sum(r['all_will_be_one_face_damage_total'] for r in results)/n:.1f} de dano avg | "
          f"{100*sum(1 for r in results if r['all_will_be_one_triggers_total']>0)/n:.1f}% dos jogos")
    print(f"\n--- Auditoria oraculo-por-oraculo 2026-09-13/14 (achados novos) ---")
    print(f"INTERACTION (Counterspell/Mana Drain/Path/Swords/Anguished Unmaking/Damn/Void Rend/Toxic Deluge/"
          f"Blasphemous Act/Supreme Verdict/Farewell, so' contadas - Regra 1, sem efeito de bordo real): "
          f"{sum(r['interaction_spells_cast_total'] for r in results)/n:.2f} avg")
    print(f"Chain Veil ativado (dobra lealdade de TODOS os planeswalkers naquele turno): "
          f"{sum(r['chain_veil_activations_total'] for r in results)/n:.2f} avg | "
          f"{100*sum(1 for r in results if r['chain_veil_activations_total']>0)/n:.1f}% dos jogos")
    urza_cast_games = [r for r in results if r["urza_chapter_end"] >= 1]
    print(f"Urza Assembles the Titans: planeswalker tutorado (cap. I) {sum(r['urza_pw_tutored_total'] for r in results)/n:.2f} avg | "
          f"planeswalker colocado de graca (cap. II) {sum(r['urza_pw_cheated_total'] for r in results)/n:.2f} avg | "
          f"conjurada em {100*len(urza_cast_games)/n:.1f}% dos jogos, alcancou cap. III (dobra lealdade naquele "
          f"turno) em {100*sum(1 for r in urza_cast_games if r['urza_chapter_end']>=3)/len(urza_cast_games):.1f}% "
          f"desses" if urza_cast_games else "Urza Assembles the Titans: nunca conjurada nesta amostra")
    print(f"Deferido nesta rodada (nao implementado, documentado - genuinamente estrutural ou desproporcional): "
          f"estatico da Nicol Bolas ('has all loyalty abilities of all other planeswalkers' - exigiria uma "
          f"segunda camada de escolha por PW); Ichormoon Gauntlet (concede uma habilidade de lealdade NOVA a "
          f"cada um dos 17 planeswalkers - exigiria reestruturar a logica hardcoded por-PW de "
          f"resolve_planeswalker()); Arena Rector (gatilho de MORTE, nada remove nossas criaturas neste sim); "
          f"The Peregrine Dynamo (copiar gatilho entre N fontes legendarias, mesma excecao do Strionic Resonator).")
    print()
    return results

# =========================================================
# MODO OPCIONAL DE RESILIENCIA (interacao de oponente)
# =========================================================
# Porte do modo de resiliencia ja' implementado e validado no Megatron/
# Ur-Dragon/Hei Bai/Markov/Ulalek/Toph (usuario, 2026-09-20: "Repita o
# processo todo com o deck da Prismatic Bridge"). Aditivo e OPCIONAL --
# nunca chamado por `simulate_one`/`run_batch` (modo padrao), gated
# inteiramente por `state.interaction_rng`. Design final direto (mesmas 7
# categorias + as 3 rodadas de correcao de orquestracao de turno ja'
# validadas nos outros 6 decks), sem precisar reproduzir o historico.
#
# DIFERENCA REAL vs. os outros 6 decks: este arquivo JA TINHA um sistema
# de remocao de oponente proprio (`resolve_removal_round`, especifico
# pra decidir se vale Greater Auramancy -- 12%/oponente/turno, sempre
# ativo desde o turno 1, sem gates, mira so' Bridge/protetores). Por
# decisao EXPLICITA do usuario (perguntado antes de implementar, ver
# checklist-oraculo.md): o modo de resiliencia NAO empilha os 2 sistemas.
# `simulate_one_with_interaction` chama `play_turn(..., skip_legacy_
# removal=True)`, desligando o sistema antigo DENTRO do modo de
# resiliencia -- o modo PADRAO continua 100% intocado, `resolve_removal_
# round` roda exatamente como sempre rodou, respondendo a pergunta
# original do Greater Auramancy sem nenhuma mudanca.
#
# Outras diferencas estruturais reais (levadas em conta no design):
# - Planeswalkers sao rastreados em `state.loyalty` (nome -> lealdade),
#   ALEM de `state.battlefield` -- remocao/wipe precisa manter os 2
#   sincronizados. `remove_permanent` delega pra `_planeswalker_dies`
#   (mesma cascata que a lealdade chegando a 0 ja usa -- Carth the Lion
#   dispara igual, nao importa a causa da morte).
# - O comandante (The Prismatic Bridge) e' um ENCHANTMENT, nao criatura
#   -- board wipe ("destroy all creatures") nunca a alcanca por
#   definicao de tipo, so' remocao/counterspell dedicados.
# - Nenhum combate real e' modelado (sem funcao de ataque neste arquivo)
#   -- ataque de oponente aqui tambem conecta sem bloqueio, mesmo padrao
#   dos outros 6 decks.
# - `INTERACTION_ENGINE_PRIORITY` prioriza o planeswalker de MAIOR
#   lealdade em campo (motor dinamico real deste deck -- qualquer um
#   dos 17 pode estar em campo a qualquer momento, entao uma lista fixa
#   de nomes nao capturaria a ameaca real), com fallback pra uma lista
#   fixa curada de nao-planeswalkers recorrentes.
# - 📊 Nao corrigido nesta rodada (decisao documentada, nao esquecimento
#   -- mesma classe do token do Ugin no Ulalek): Arena Rector ("When
#   this creature dies, you may exile it... search for a planeswalker
#   card, put it onto the battlefield") so' importa se ELA especificamente
#   morrer -- ao contrario do bug real do Carth (ja' corrigido acima,
#   JA' alcancavel em modo padrao via lealdade chegando a 0, 1.861/3.000
#   jogos), morte de CRIATURA nomeada nunca foi possivel neste arquivo
#   antes desta rodada -- so' fica relevante especificamente quando MEU
#   novo wipe/remocao alcanca a propria Arena Rector, nao um
#   pre-requisito estrutural do port (diferente dos 2 fixes do Carth).

NUM_OPPONENTS = N_OPPONENTS  # reusa a mesma constante ja' declarada no topo do arquivo (mesa de 4, ja documentada)

INTERACTION_SETUP_TURNS = 2
# Turnos 1-2 sao sempre setup, sem chance de reacao nenhuma -- o
# oponente ainda nao tem motivo/mana pra reagir.

def interaction_chance(state: GameState) -> float:
    """Formula compartilhada de 'chance do oponente reagir esse turno' --
    identica aos outros 6 decks: escala com o impacto do meu proprio
    board (permanentes nao-terreno em campo)."""
    board_impact = sum(1 for n in state.battlefield if not is_land(n))
    return min(0.10 + 0.03 * board_impact, 0.75)

OPPONENT_ATTENTION_CHANCE = 1.0 / NUM_OPPONENTS
# Gate de "esse oponente esta' de olho em mim esse turno" (achado real
# do usuario nos outros decks, 2026-09-20: "se sempre for 3 contra 1,
# ai' nao consigo fazer nada, nunca!") -- por simetria, ha' 3 alvos
# possiveis pra atencao de qualquer oponente (eu e os outros 2 que este
# simulador nao modela), entao a chance BASE de que um turno de
# oponente qualquer seja sobre MIM e' 1/NUM_OPPONENTS, antes de
# qualquer ajuste por ameaca de board (que ja' fica dentro de
# `interaction_chance()`). Rolado 1x no INICIO de `try_smart_opponent_
# turn`, antes de qualquer categoria.

BOARD_WIPE_CHANCE_FACTOR = 0.4
GRAVEYARD_WIPE_CHANCE_FACTOR = 0.4
GRAVEYARD_SNIPE_CHANCE_FACTOR = 0.5
COUNTERSPELL_CHANCE_FACTOR = 0.5
# Mesmos fatores redutores dos outros 6 decks sobre a MESMA
# `interaction_chance()` compartilhada.

NONPLANESWALKER_ENGINE_PRIORITY = [
    "Doubling Season",
    "The Chain Veil",
    "Vorinclex, Monstrous Raider",
    "Innkeeper's Talent",
    "Deepglow Skate",
    "Carth the Lion",
    "Evolution Sage",
    "Flux Channeler",
]
# Fallback de `try_smart_opponent_removal` quando NENHUM planeswalker
# esta' em campo -- lista curada por prioridade (dobradores de
# contador/lealdade primeiro, maior multiplicador de valor do deck;
# depois ativacao extra, tutor de carta, proliferate). A propria Bridge
# fica de fora de proposito -- ja' tem categoria dedicada
# (`try_smart_opponent_counter`) e remocao nao a mata de verdade mesmo.

def try_smart_opponent_removal(state: GameState, log: List[Dict]) -> Optional[str]:
    """Remocao 'inteligente' -- mira o planeswalker de MAIOR lealdade em
    campo (motor dinamico real deste deck), com fallback pra
    `NONPLANESWALKER_ENGINE_PRIORITY` se nenhum planeswalker estiver em
    campo. Nunca aleatorio.

    Achado real do usuario 2026-09-21: Sterling Grove/Greater Auramancy
    ('Other enchantments you control have shroud' -- confirmado via
    Scryfall, shroud de verdade, nao hexproof) blindam qualquer OUTRO
    encantamento contra remocao ALVO (nao contra wipe -- 'destroy
    all'/'exile all' nunca usa 'target', shroud nao se aplica la', ver
    `try_smart_opponent_wipe`). 2 dos 8 itens de `NONPLANESWALKER_
    ENGINE_PRIORITY` sao encantamentos de verdade (Doubling Season,
    Innkeeper's Talent) -- o sistema LEGADO (`resolve_removal_round`,
    ja' desligado no modo resiliencia) ja' respeitava isso via
    `protectors_in_play()`, redirecionando remocao pro PROTETOR primeiro
    (unico jeito de destravar o alvo real depois). Essa checagem nunca
    foi portada pra esta categoria nova -- corrigido aqui, reaproveitando
    a mesma `protectors_in_play()` de sempre. Planeswalkers nunca sao
    encantamento nesta lista (confirmado, sem hibrido), entao o ramo de
    lealdade nunca precisa de redirecionamento."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if state.loyalty:
        target = max(state.loyalty, key=lambda pw: state.loyalty[pw])
    else:
        target = next((n for n in NONPLANESWALKER_ENGINE_PRIORITY if n in state.battlefield), None)
    if target is None:
        return None
    if C(target).type == "Enchantment":
        prot = protectors_in_play(state)
        if prot:
            target = state.interaction_rng.choice(prot)
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    remove_permanent(state, target, log, source="opponent_removal")
    state.smart_removals_total += 1
    state.smart_removal_log.append((state.turn, target))
    return target

def try_smart_opponent_discard(state: GameState, log: List[Dict]) -> Optional[str]:
    """Discard aleatorio -- mesma logica dos outros 6 decks (alvo
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
# escolha ponderada pelos mesmos 3 fatores. The Chain Veil (ja' na
# `NONPLANESWALKER_ENGINE_PRIORITY`) e' um artefato real -- um wipe de
# artefato pode alcancar o maior multiplicador de ativacao do deck de
# uma vez. IMPORTANTE: a propria The Prismatic Bridge E' Enchantment
# (confirmado via Scryfall) -- este e' o UNICO dos 3 tipos de wipe
# (criatura/artefato/encantamento) que alcanca o comandante de verdade
# neste deck. `remove_permanent` ja' trata isso corretamente (CR 903.9,
# zona de comando em vez de cemiterio) sem precisar de excecao extra
# aqui.
WIPE_TYPE_WEIGHTS = {
    "creature": BOARD_WIPE_CHANCE_FACTOR,
    "artifact": ARTIFACT_WIPE_CHANCE_FACTOR,
    "enchantment": ENCHANTMENT_WIPE_CHANCE_FACTOR,
}
TOTAL_WIPE_CHANCE_FACTOR = sum(WIPE_TYPE_WEIGHTS.values())


def try_smart_opponent_wipe(state: GameState, log: List[Dict]) -> Optional[list]:
    """Board wipe ('destroy all creatures'/'destroy all artifacts'/
    'destroy all enchantments') -- destroi TODOS os meus permanentes do
    tipo escolhido de uma vez via `remove_permanent`. Um wipe de
    CRIATURA nunca alcanca o comandante (Enchantment) nem planeswalkers
    -- so' `C(n).type == "Creature"` de verdade. Um wipe de ARTEFATO
    tambem nunca alcanca a Bridge (ela nunca e' artefato de verdade). Um
    wipe de ENCANTAMENTO E' O UNICO dos 3 tipos que alcanca o comandante
    de verdade neste deck (CR 903.9, `remove_permanent` ja' trata isso
    corretamente -- zona de comando em vez de cemiterio, sem precisar
    de excecao extra aqui).

    Design de 2 passos (nao 3 rolagens independentes -- ver comentario
    de `WIPE_TYPE_WEIGHTS` acima): 1) rola 1x se ALGUM wipe acontece
    esse turno de oponente, chance = `interaction_chance() *
    TOTAL_WIPE_CHANCE_FACTOR`; 2) SO' se isso disparar, escolhe qual
    TIPO de sweeper via escolha ponderada (`state.interaction_rng.
    choices`) restrita aos tipos que tem pelo menos 1 alvo legal em
    campo. Criatura-artefato (The Peregrine Dynamo, Silent Arbiter) e'
    alvo do wipe de artefato tambem (tag "artifact"), e morre pela
    cascata normal de criatura (`remove_permanent`). Sem nenhum alvo
    legal de tipo nenhum, retorna None sem fazer nada."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * TOTAL_WIPE_CHANCE_FACTOR:
        return None
    candidates = {
        "creature": [n for n in state.battlefield if C(n).type == "Creature"],
        # Achado real 2026-09-24 (Regra #3, conceito compartilhado "o que e'
        # artefato"): The Peregrine Dynamo e' "Legendary Artifact Creature"
        # (Scryfall) mas o `CARD_DB` so' guarda 1 tipo ("Creature") -- um wipe
        # de artefato nunca a alcancava. Tag "artifact" cobre criatura-artefato.
        "artifact": [n for n in state.battlefield if C(n).type == "Artifact" or has_tag(n, "artifact")],
        "enchantment": [n for n in state.battlefield if C(n).type == "Enchantment"],
    }
    available = [t for t in candidates if candidates[t]]
    if not available:
        return None
    wipe_type = state.interaction_rng.choices(available, weights=[WIPE_TYPE_WEIGHTS[t] for t in available])[0]
    targets = candidates[wipe_type]
    for n in targets:
        remove_permanent(state, n, log, source=f"opponent_{wipe_type}_wipe")
    if wipe_type == "creature" and attack_model_on(state):
        # Wipe de criatura e' SIMETRICO: limpa o campo de TODOS os
        # oponentes tambem (substitui o antigo `wiped_this_round`).
        _clear_all_opp_boards(state, how="destroy")
    if wipe_type == "creature":
        state.smart_wipes_total += 1
        state.smart_wipe_log.append((state.turn, targets))
    elif wipe_type == "artifact":
        state.smart_artifact_wipes_total += 1
        state.smart_artifact_wipe_log.append((state.turn, targets))
    else:
        state.smart_enchantment_wipes_total += 1
        state.smart_enchantment_wipe_log.append((state.turn, targets))
    return targets

def try_smart_opponent_graveyard_wipe(state: GameState, log: List[Dict]) -> Optional[list]:
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

def try_smart_opponent_graveyard_snipe(state: GameState, log: List[Dict]) -> Optional[str]:
    """Graveyard hate, modelo EXILIO DE CARTA UNICA (Scavenging
    Ooze/Cease-style) -- repetivel todo turno. Alvo SMART: maior MV
    entre criatura OU planeswalker no cemiterio -- mesmo criterio real
    que `Tamiyo, Compleated Sage -X` ja' usa pra escolher alvo de
    recursao (`by_mv`/`affordable`, qualquer permanente card, nao so'
    criatura)."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    candidates = [c for c in state.graveyard if C(c).type in ("Creature", "Planeswalker")]
    if not candidates:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * GRAVEYARD_SNIPE_CHANCE_FACTOR:
        return None
    target = max(candidates, key=lambda n: C(n).mv)
    state.graveyard.remove(target)
    state.smart_graveyard_snipes_total += 1
    state.smart_graveyard_snipe_log.append((state.turn, target))
    return target

def try_smart_opponent_counter(state: GameState) -> bool:
    """Counterspell -- so' mira a conjuracao da propria Bridge (mesma
    logica dos outros 6 decks: o motor inteiro do deck depende do
    comandante resolver). Chamada de dentro de `cast_bridge()`, nao do
    loop de `simulate_one_with_interaction` -- so' faz sentido no exato
    momento do cast, dentro do MEU turno (cobre tanto cast normal
    quanto flash)."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return False
    if state.interaction_rng.random() >= interaction_chance(state) * COUNTERSPELL_CHANCE_FACTOR:
        return False
    state.smart_counters_total += 1
    state.smart_counter_log.append(state.turn)
    return True

# =========================================================
# MODELO DE COMBATE -- ataque de oponente a planeswalkers (2026-09-24)
# =========================================================
# Pedido do usuario: "Conseguimos implementar no goldfish um simulador de
# ataque aos PW?" (aprovado com 3 perfis de mesa; a mesa real dele e'
# "Misto, um pouco de cada, simulando diferentes decks de forma aleatoria").
#
# Antes disto, o unico ataque do modo de resiliencia era 1 ficha generica
# de 1-3 de poder que SEMPRE acertava a vida, nunca um planeswalker, e
# ninguem bloqueava -- entao nenhuma carta de pillowfort (Silent Arbiter,
# Dueling Grounds, Sphere of Safety, Ghostly Prison) tinha como ser avaliada.
#
# SUPOSICOES (documentadas, nao dados reais -- ler os resultados como
# comparacao RELATIVA entre variantes do deck nas mesmas seeds):
# - Cada um dos 3 oponentes tem um arquetipo: "go_wide" (1-3 criaturas
#   1/1-2/2 por turno a partir do T2, ate 15), "voltron" (comandante 3/3 com
#   atropelar a partir do T3, +1..3/+1..3 por turno ate 20, volta 1 turno
#   depois de removido com metade do bonus de equipamento; ate 2 criaturas
#   2/2 de apoio) ou "low" (30%/turno de uma 3/3 ou 4/4 a partir do T3, ate
#   3). Perfil "mixed" sorteia o arquetipo de cada oponente por partida.
# - O campo do oponente cresce TODO turno dele; ele so' ataca voce/seus PWs
#   no turno em que passa no gate de atencao ja' existente (1/3).
# - Alvo: os atacantes vao, do maior pro menor, pro planeswalker de MAIOR
#   lealdade ate somar poder pra mata-lo; depois o proximo PW; sobra vai na
#   sua vida.
# - Imposto (Sphere of Safety/Ghostly Prison): o oponente usa ate metade da
#   mana dele (turno, max 10) pra pagar; quem nao e' pago nao ataca voce --
#   na Ghostly Prison o atacante de vida nao pago e' redirecionado pro seu
#   planeswalker (ruling oficial: a Prison nao protege planeswalker).
# - Nossas remocoes/wipes, que antes eram so' contadas, agora tem efeito
#   real nos 2 lados da mesa -- e so' saem com alvo (ameaca real).
# - Instantaneas sao usadas na velocidade de feitico, no meu turno
#   (simplificacao: sem janela de resposta no turno do oponente).
ATTACK_PROFILES = ("mixed", "go_wide", "voltron", "low")
PILLOWFORT_CARDS = ("Silent Arbiter", "Dueling Grounds", "Sphere of Safety", "Ghostly Prison")
OPP_ARCHETYPES = ("go_wide", "voltron", "low")
TAX_BUDGET_FRACTION = 0.5
THREAT_POWER = 3
SPOT_REMOVAL_MIN_POWER = 4
WIPE_MIN_OPP_POWER = 8
GO_WIDE_CAP = 15
LOW_CAP = 3
VOLTRON_BASE = 3
VOLTRON_CAP = 20
SPOT_REMOVAL_SPELLS = {  # nome -> (custo, simbolos coloridos {cor: qtd}, como remove) -- custo real, Scryfall
    "Swords to Plowshares": (1, {"W": 1}, "exile"),            # {W}
    "Path to Exile": (1, {"W": 1}, "exile"),                   # {W}
    "Damn": (2, {"B": 2}, "destroy"),                          # {B}{B} (modo normal, alvo unico)
    "Anguished Unmaking": (3, {"W": 1, "B": 1}, "exile"),      # {1}{W}{B}, "You lose 3 life."
    "Void Rend": (3, {"W": 1, "U": 1, "B": 1}, "destroy"),     # {W}{U}{B}
}
WIPE_SPELL_NAMES = ("Toxic Deluge", "Damn", "Supreme Verdict", "Blasphemous Act", "Farewell")


def attack_model_on(state: GameState) -> bool:
    return state.attack_profile is not None


def _attack_limit_one(state: GameState) -> bool:
    return any(has_tag(n, "attack_limit_one") for n in state.battlefield)


def _held_for_threat(card: str) -> bool:
    """Remocao/wipe (so' as magicas -- planeswalkers com tag removal/wipe
    continuam sendo conjurados normalmente) ficam na mao ate existir alvo."""
    return C(card).type in ("Instant", "Sorcery") and (has_tag(card, "removal") or has_tag(card, "wipe"))


# ---------------- criaturas do nosso lado ----------------

def _our_creature_instances(state: GameState) -> List[tuple]:
    """Uma entrada por criatura nossa em campo: (nome, indice) pra ficha
    (varias com o mesmo nome) ou (nome, None) pra carta nomeada."""
    inst = []
    seen = set()
    for name in state.battlefield:
        if C(name).type != "Creature" or name in seen:
            continue
        seen.add(name)
        n = state.battlefield.count(name)
        if "Token" in name:
            lst = state.token_counters.setdefault(name, [])
            while len(lst) < n:
                lst.append(0)
            del lst[n:]
            inst.extend((name, i) for i in range(n))
        else:
            inst.append((name, None))
    return inst


def _ctr(state: GameState, inst: tuple) -> int:
    name, i = inst
    if i is None:
        return state.creature_counters.get(name, 0)
    lst = state.token_counters.get(name, [])
    return lst[i] if i < len(lst) else 0


def _add_ctr(state: GameState, inst: tuple, n: int):
    name, i = inst
    if i is None:
        state.creature_counters[name] = state.creature_counters.get(name, 0) + n
    else:
        state.token_counters[name][i] += n
    _counters_put(state, n, [], source="plus1_counter")


def _pt(state: GameState, inst: tuple):
    p, t, kw = CREATURE_STATS[inst[0]]
    c = _ctr(state, inst)
    bonus = 2 if state.elspeth_emblem else 0
    kw = set(kw) | ({"flying"} if state.elspeth_emblem else set())
    return p + c + bonus, t + c + bonus, kw


def _is_sick(state: GameState, inst: tuple) -> bool:
    name, i = inst
    if "haste" in CREATURE_STATS[name][2]:
        return False
    if i is None:
        return state.creature_cast_turn.get(name, -1) >= state.turn
    new = state.new_tokens_this_turn.get(name, 0)
    return i >= len(state.token_counters.get(name, [])) - new


def _blocker_value(state: GameState, inst: tuple):
    """Menor = mais descartavel (bloqueia/chumpa primeiro)."""
    p, t, _ = _pt(state, inst)
    return (0 if "Token" in inst[0] else C(inst[0]).mv, p + t)


def _proliferate_creature_counters(state: GameState):
    mult = counter_doubler_multiplier(state)
    for inst in _our_creature_instances(state):
        if _ctr(state, inst) > 0:
            _add_ctr(state, inst, mult)


def _double_creature_counters(state: GameState):
    """Deepglow Skate ETB: 'double the number of each kind of counter on
    any number of target permanents' -- tambem as +1/+1 das criaturas."""
    mult = counter_doubler_multiplier(state)
    for inst in _our_creature_instances(state):
        c = _ctr(state, inst)
        if c > 0:
            _add_ctr(state, inst, c * mult)


def _shift_instances(lst: List[tuple], inst: tuple) -> List[tuple]:
    """Tira `inst` de uma lista de instancias e reindexa as fichas de mesmo
    nome que estavam depois dela (o indice e' a posicao na lista de
    marcadores daquela ficha)."""
    name, i = inst
    out = []
    for (n, j) in lst:
        if n == name:
            if j == i:
                continue
            if i is not None and j is not None and j > i:
                j -= 1
        out.append((n, j))
    return out


def _remove_our_instance(state: GameState, inst: tuple):
    name, i = inst
    state.battlefield.remove(name)
    if i is None:
        state.creature_counters.pop(name, None)
    else:
        lst = state.token_counters.get(name, [])
        if i < len(lst):
            lst.pop(i)
    state.our_tapped = _shift_instances(state.our_tapped, inst)
    state.tamiyo_fr_marked = _shift_instances(state.tamiyo_fr_marked, inst)


def _our_creature_leaves(state: GameState, name: str, log: List[Dict], exiled: bool = False,
                         source: str = "", inst: Optional[tuple] = None):
    """Cascata unica de 'uma criatura nossa sai de campo' (combate, nossos
    wipes, remocao/wipe de oponente). Morrer (nao exilio) dispara:
    - Liliana, Dreadhorde General: 'Whenever a creature you control dies,
      draw a card.' (fichas tambem morrem)
    - Arena Rector: 'When this creature dies, you may exile it. If you do,
      search your library for a planeswalker card, put it onto the
      battlefield, then shuffle.'"""
    if name not in state.battlefield:
        return
    if inst is None:
        if "Token" in name:
            lst = state.token_counters.get(name) or [0]
            inst = (name, lst.index(min(lst)))
        else:
            inst = (name, None)
    _remove_our_instance(state, inst)
    if "Token" not in name and not exiled:
        state.graveyard.append(name)
    log.append({"trigger": "our_creature_leaves", "card": name, "exiled": exiled, "source": source, "turn": state.turn})
    if exiled:
        return
    if "Liliana, Dreadhorde General" in state.loyalty:
        state.draw(1)
        state.pw_draws_total += 1
        state.liliana_static_draws_total += 1
    if name == "Arena Rector":
        pws = [c for c in state.library if C(c).type == "Planeswalker"]
        if pws:
            if "Arena Rector" in state.graveyard:
                state.graveyard.remove("Arena Rector")  # "you may exile it"
            best = max(pws, key=lambda c: (C(c).mv, PLANESWALKER_STARTING_LOYALTY[c]))
            state.library.remove(best)
            state.rng.shuffle(state.library)
            state.battlefield.append(best)
            planeswalker_enters(state, best, log)
            state.arena_rector_triggers_total += 1
            log.append({"trigger": "arena_rector_dies", "found": best, "turn": state.turn})


# ---------------- campo dos oponentes ----------------

def _new_opp_creature(p: int, t: int, flying: bool, haste: bool, trample: bool = False,
                      cmd: bool = False, token: bool = False, mv: int = 0) -> dict:
    # `mv` so' e' lido pelo -X do Ugin (ficha = 0; carta = suposicao
    # documentada: comandante voltron 3, apoio 2/2 = 2, 3/3 = 3, 4/4 = 4).
    return {"p": p, "t": t, "flying": flying, "trample": trample, "cmd": cmd, "token": token,
            "sick": not haste, "frozen": 0, "frozen_now": False, "mv": 0 if token else mv}


def _opp_threats(state: GameState) -> List[tuple]:
    """(indice do oponente, criatura) que podem atacar no proximo turno do
    dono (congeladas nao contam)."""
    return [(i, c) for i, b in enumerate(state.opp_boards) for c in b if c["frozen"] == 0]


def _biggest_threat(state: GameState, max_toughness: Optional[int] = None):
    cands = [(i, c) for i, c in _opp_threats(state) if max_toughness is None or c["t"] <= max_toughness]
    if not cands:
        return None, None
    return max(cands, key=lambda ic: (ic[1]["p"], ic[1]["trample"], ic[1]["flying"]))


def _opp_remove_creature(state: GameState, i: int, c: dict, how: str = "destroy", cooldown: int = 1):
    b = state.opp_boards[i]
    for k, x in enumerate(b):
        if x is c:
            del b[k]
            break
    else:
        return
    state.opp_creatures_killed_total += 1
    if c["cmd"]:
        # Comandante volta pra zona de comando (CR 903.9); recasta depois,
        # perdendo as auras (sobra metade do bonus -- equipamento fica).
        state.opp_cmd_cooldown[i] = cooldown
        state.opp_cmd_bonus[i] = max(0, (c["p"] - VOLTRON_BASE) // 2)


def _clear_all_opp_boards(state: GameState, how: str = "destroy", max_toughness: Optional[int] = None,
                          min_power: Optional[int] = None):
    for i, b in enumerate(state.opp_boards):
        for c in list(b):
            if max_toughness is not None and c["t"] > max_toughness:
                continue
            if min_power is not None and c["p"] < min_power:
                continue
            _opp_remove_creature(state, i, c, how=how)


def _freeze_biggest_threats(state: GameState, n: int, log: List[Dict], source: str = ""):
    """'Tap ... It doesn't untap during its controller's next untap step' --
    a criatura nao ataca no proximo turno do dono."""
    for _ in range(n):
        i, c = _biggest_threat(state)
        if c is None:
            return
        c["frozen"] = 1
        log.append({"trigger": "opp_creature_frozen", "power": c["p"], "source": source, "turn": state.turn})


def _bounce_biggest_threat(state: GameState, log: List[Dict], source: str = ""):
    i, c = _biggest_threat(state)
    if c is None:
        return
    if c["token"]:
        _opp_remove_creature(state, i, c, how="bounce")        # ficha que sai de campo deixa de existir
    elif c["cmd"]:
        _opp_remove_creature(state, i, c, how="bounce", cooldown=0)  # recasta no proximo turno, com doenca
    else:
        c["frozen"] = 1  # volta pra mao e e' reconjurada com doenca: nao ataca no proximo turno
    log.append({"trigger": "opp_creature_bounced", "power": c["p"], "source": source, "turn": state.turn})


def _ugin_ping(state: GameState, log: List[Dict]):
    i, c = _biggest_threat(state, max_toughness=3)
    if c is not None:
        _opp_remove_creature(state, i, c, how="destroy")
        log.append({"trigger": "ugin_ping_kill", "power": c["p"], "turn": state.turn})


def _teferi_hero_emblem_trigger(state: GameState):
    """Emblema do Teferi, Hero of Dominaria: 'Whenever you draw a card,
    exile target permanent an opponent controls.' Unico permanente de
    oponente rastreado = criatura; exila a de maior poder (qualquer uma,
    inclusive congelada)."""
    cands = [(i, c) for i, b in enumerate(state.opp_boards) for c in b]
    if not cands:
        return
    i, c = max(cands, key=lambda ic: (ic[1]["p"], ic[1]["cmd"]))
    _opp_remove_creature(state, i, c, how="exile")
    state.teferi_emblem_exiles_total += 1


def _ugin_minus_x_choice(state: GameState, loy: int) -> Optional[int]:
    """Ugin '-X: Exile each permanent with mana value X or less that's one
    or more colors.' SIMETRICO: pega nossas fichas (todas coloridas, MV 0)
    e qualquer permanente colorido nosso de MV <= X. Terreno e artefato
    incolor nao sao afetados. Escolhe o X (< lealdade) que exila mais poder
    de oponente SEM exilar nenhum permanente nosso que nao seja ficha, e so'
    se isso compensar (mesmo limiar dos nossos wipes)."""
    ours_nontoken = [n for n in set(state.battlefield)
                     if not is_land(n) and "Token" not in n and C(n).colors]
    our_token_power = sum(_pt(state, x)[0] for x in _our_creature_instances(state) if "Token" in x[0])
    best, best_power = None, 0
    for x in range(0, loy):
        if any(C(n).mv <= x for n in ours_nontoken):
            break
        opp_power = sum(c["p"] for b in state.opp_boards for c in b if c["mv"] <= x)
        if opp_power > best_power:
            best, best_power = x, opp_power
    if best is None or best_power < WIPE_MIN_OPP_POWER or best_power < 2 * our_token_power:
        return None
    return best


def _ugin_minus_x(state: GameState, x: int, log: List[Dict]):
    for j, b in enumerate(state.opp_boards):
        for c in list(b):
            if c["mv"] <= x:
                _opp_remove_creature(state, j, c, how="exile")
    for inst in sorted([i for i in _our_creature_instances(state) if "Token" in i[0]],
                       key=lambda v: (v[0], -v[1])):
        _our_creature_leaves(state, inst[0], log, exiled=True, source="ugin_minus_x", inst=inst)
    state.ugin_minus_x_total += 1


def _develop_opponent_board(state: GameState, i: int):
    arch = state.opp_archetypes[i]
    rng = state.interaction_rng
    t = state.turn
    b = state.opp_boards[i]
    if arch == "go_wide":
        if t >= 2:
            for _ in range(rng.randint(1, 3)):
                if len(b) >= GO_WIDE_CAP:
                    break
                size = 1 if rng.random() < 0.6 else 2
                b.append(_new_opp_creature(size, size, flying=rng.random() < 0.15,
                                           haste=rng.random() < 0.10, token=True))
    elif arch == "voltron":
        cmd = next((c for c in b if c["cmd"]), None)
        if cmd is not None:
            grow = rng.randint(1, 3)
            cmd["p"] = min(VOLTRON_CAP, cmd["p"] + grow)
            cmd["t"] = min(VOLTRON_CAP, cmd["t"] + grow)
        elif state.opp_cmd_cooldown[i] > 0:
            state.opp_cmd_cooldown[i] -= 1
        elif t >= 3:
            base = VOLTRON_BASE + state.opp_cmd_bonus[i]
            b.append(_new_opp_creature(base, base, flying=rng.random() < 0.35,
                                       haste=rng.random() < 0.15, trample=True, cmd=True, mv=3))
        if t >= 2 and sum(1 for c in b if not c["cmd"]) < 2 and rng.random() < 0.25:
            b.append(_new_opp_creature(2, 2, flying=False, haste=False, mv=2))
    else:  # "low"
        if t >= 3 and len(b) < LOW_CAP and rng.random() < 0.30:
            size = rng.choice((3, 4))
            b.append(_new_opp_creature(size, size, flying=rng.random() < 0.25, haste=rng.random() < 0.05, mv=size))


def _opp_turn_start(state: GameState, i: int):
    """Untap do oponente i (so' as criaturas DELE): perde a doenca de
    invocacao; a congelada ('doesn't untap during its controller's next
    untap step') fica virada e nao ataca neste turno. Depois o campo cresce."""
    for c in state.opp_boards[i]:
        c["sick"] = False
        c["frozen_now"] = c["frozen"] > 0
        if c["frozen"] > 0:
            c["frozen"] -= 1
    _develop_opponent_board(state, i)


# ---------------- combate: oponente ataca ----------------

def _choose_blocker(state: GameState, c: dict, tgt: str, avail: List[tuple]) -> Optional[tuple]:
    cands = [b for b in avail if not c["flying"] or "flying" in _pt(state, b)[2]]
    if not cands:
        return None

    def outcome(b):
        p, t, kw = _pt(state, b)
        dt = "deathtouch" in kw
        first_kill = "double_strike" in kw and (p >= c["t"] or dt)
        kills = first_kill or dt or p * (2 if "double_strike" in kw else 1) >= c["t"]
        survives = first_kill or c["p"] < t
        return kills, survives

    good = [b for b in cands if all(outcome(b))]
    if good:
        return min(good, key=lambda b: _blocker_value(state, b))
    if tgt == "face":
        chumps = [b for b in cands if b[0] in CHUMP_OK]
        if chumps and state.life - c["p"] <= 10:
            return min(chumps, key=lambda b: _blocker_value(state, b))
        return None
    walls = [b for b in cands if outcome(b)[1]]
    if walls:
        return min(walls, key=lambda b: _blocker_value(state, b))
    lethal = c["p"] >= state.loyalty.get(tgt, 0)
    chumps = [b for b in cands if b[0] in CHUMP_OK]
    if chumps and (lethal or c["p"] >= 2):
        return min(chumps, key=lambda b: _blocker_value(state, b))
    trades = [b for b in cands if outcome(b)[0]]
    if trades and lethal:
        return min(trades, key=lambda b: _blocker_value(state, b))
    return None


def opponent_combat(state: GameState, i: int, log: List[Dict]):
    """Combate do oponente i contra mim (so' depois do gate de atencao)."""
    if state.turn <= INTERACTION_SETUP_TURNS:
        return
    attackers = [c for c in state.opp_boards[i] if not c["sick"] and not c["frozen_now"]]
    if not attackers:
        return
    limit_one = _attack_limit_one(state)
    if limit_one and len(attackers) > 1:
        # "No more than one creature can attack each combat."
        state.attackers_limited_total += len(attackers) - 1
        attackers = [max(attackers, key=lambda c: (c["p"], c["trample"], c["flying"]))]

    pws = sorted(state.loyalty.items(), key=lambda kv: -kv[1])
    need = {pw: loy for pw, loy in pws}
    # The Eternal Wanderer: "No more than one creature can attack The
    # Eternal Wanderer each combat."
    wanderer_taken = [False]

    def pick_pw(skip_full: bool):
        for pw, _ in pws:
            if pw == "The Eternal Wanderer" and wanderer_taken[0]:
                continue
            if skip_full and need[pw] <= 0:
                continue
            return pw
        return None

    assign = []
    for c in sorted(attackers, key=lambda c: -c["p"]):
        tgt = pick_pw(skip_full=True)
        if tgt is not None:
            need[tgt] -= c["p"]
            if tgt == "The Eternal Wanderer":
                wanderer_taken[0] = True
            assign.append([c, tgt])
        else:
            assign.append([c, "face"])

    sphere = "Sphere of Safety" in state.battlefield
    ghostly = "Ghostly Prison" in state.battlefield
    if sphere or ghostly:
        budget = int(TAX_BUDGET_FRACTION * min(state.turn, 10))
        x = sum(1 for n in state.battlefield if C(n).type == "Enchantment") if sphere else 0
        paid = []
        for c, tgt in sorted(assign, key=lambda a: -a[0]["p"]):
            cost = x + (2 if ghostly and tgt == "face" else 0)
            if cost <= budget:
                budget -= cost
                paid.append([c, tgt])
            elif ghostly and tgt == "face" and pick_pw(skip_full=False) is not None and x <= budget:
                # Ruling: "a creature that can't attack you can still attack
                # a planeswalker you control" -- vai pro planeswalker.
                budget -= x
                new_tgt = pick_pw(skip_full=False)
                if new_tgt == "The Eternal Wanderer":
                    wanderer_taken[0] = True
                paid.append([c, new_tgt])
                state.attackers_redirected_to_pw_total += 1
            else:
                state.attackers_stopped_by_tax_total += 1
        assign = paid
    if not assign:
        return
    state.opp_attackers_total += len(assign)
    state.opp_attacks_on_pw_total += sum(1 for _, t in assign if t != "face")

    avail = [b for b in _our_creature_instances(state) if b not in state.our_tapped]
    max_blocks = 1 if limit_one else len(avail)  # "No more than one creature can block each combat."
    blocks = {}
    for c, tgt in sorted(assign, key=lambda a: (a[1] == "face", -a[0]["p"])):
        if len(blocks) >= max_blocks:
            break
        b = _choose_blocker(state, c, tgt, avail)
        if b is not None:
            blocks[id(c)] = b
            avail.remove(b)

    pw_damage: Dict[str, int] = {}
    face = 0
    lifelink = 0
    dead_attackers = []
    dead_blockers = []
    for c, tgt in assign:
        b = blocks.get(id(c))
        if b is None:
            if tgt == "face":
                face += c["p"]
            else:
                pw_damage[tgt] = pw_damage.get(tgt, 0) + c["p"]
            continue
        state.blocks_total += 1
        bp, bt, bkw = _pt(state, b)
        ds = "double_strike" in bkw
        dt = "deathtouch" in bkw
        attacker_dead = ds and (bp >= c["t"] or dt)
        dealt = bp if attacker_dead else 0
        if not attacker_dead:
            if c["p"] >= bt:
                dead_blockers.append(b)
            if c["trample"]:
                excess = max(0, c["p"] - bt)
                if excess:
                    if tgt == "face":
                        face += excess
                    else:
                        pw_damage[tgt] = pw_damage.get(tgt, 0) + excess
            dealt = bp * (2 if ds else 1)
            if dt or dealt >= c["t"]:
                attacker_dead = True
        if "lifelink" in bkw:
            lifelink += dealt
        if b in state.tamiyo_fr_marked and bp > 0:
            # Tamiyo FR +1: "whenever either of those creatures deals combat
            # damage, you draw a card" -- dupla: 2 passos de dano (so' 1 se
            # o atacante ja' morreu no primeiro).
            n_steps = 2 if ds and not (bp >= c["t"] or dt) else 1
            state.draw(n_steps)
            state.pw_draws_total += n_steps
            state.tamiyo_fr_combat_draws_total += n_steps
        if attacker_dead:
            dead_attackers.append(c)

    state.life += lifelink
    state.life -= face
    state.face_combat_damage_total += face
    if state.life <= 0 and state.died_turn is None:
        state.died_turn = state.turn
    for pw, d in pw_damage.items():
        if pw in state.loyalty:
            state.pw_combat_damage_total += min(d, state.loyalty[pw])
            if d >= state.loyalty[pw]:
                state.pw_combat_deaths_total += 1
            add_loyalty(state, pw, -d, log, reason="combat_damage")
    for c in dead_attackers:
        _opp_remove_creature(state, i, c, how="combat")
    for b in sorted(dead_blockers, key=lambda x: (x[0], -(x[1] if x[1] is not None else -1))):
        if b[0] in state.battlefield:
            _our_creature_leaves(state, b[0], log, exiled=False, source="combat_block", inst=b)
            state.our_blockers_lost_total += 1


# ---------------- nosso turno: combate e respostas ----------------

def _best_counter_target(state: GameState) -> Optional[tuple]:
    inst = _our_creature_instances(state)
    if not inst:
        return None
    named = [x for x in inst if x[1] is None]
    pool = named or inst
    return max(pool, key=lambda x: (_pt(state, x)[1], _pt(state, x)[0]))


def our_combat_step(state: GameState, log: List[Dict]):
    # Innkeeper's Talent nivel 1: "At the beginning of combat on your turn,
    # put a +1/+1 counter on target creature you control." (marcador ->
    # dobradores valem, inclusive o nivel 3 dela mesma)
    if "Innkeeper's Talent" in state.battlefield:
        tgt = _best_counter_target(state)
        if tgt is not None:
            _add_ctr(state, tgt, counter_doubler_multiplier(state))

    # Oko, the Ringleader: "At the beginning of combat on your turn, Oko
    # becomes a copy of up to one target creature you control until end of
    # turn, except he has hexproof." Copia valores copiaveis (P/T impressos,
    # sem marcadores -- CR 707.2); nunca copia lendaria (regra de lenda,
    # 704.5j, mataria uma das 2). Ataca se estava sob nosso controle desde o
    # inicio do turno (nao entrou pela Bridge neste upkeep). No fim do turno
    # volta a ser planeswalker -- nao bloqueia no turno do oponente.
    oko = None
    if "Oko, the Ringleader" in state.loyalty:
        cands = [x for x in _our_creature_instances(state) if x[0] not in LEGENDARY_CARD_NAMES]
        if cands:
            src = max(cands, key=lambda x: (CREATURE_STATS[x[0]][0], CREATURE_STATS[x[0]][1]))
            state.oko_combat_copies_total += 1
            if state.pw_enter_turn.get("Oko, the Ringleader", -1) < state.turn:
                p, t, kw = CREATURE_STATS[src[0]]
                if state.elspeth_emblem:
                    p, t, kw = p + 2, t + 2, set(kw) | {"flying"}
                oko = (("Oko, the Ringleader", None), p, kw)

    ready = [x for x in _our_creature_instances(state) if not _is_sick(state, x)]
    if not ready and oko is None:
        return
    limit_one = _attack_limit_one(state)
    keep = max((len(b) for b in state.opp_boards), default=0)
    if limit_one:
        keep = min(keep, 1)
    vig = [x for x in ready if "vigilance" in _pt(state, x)[2]]
    nonvig = sorted([x for x in ready if x not in vig],
                    key=lambda x: ("deathtouch" in _pt(state, x)[2], _pt(state, x)[1], _pt(state, x)[0]),
                    reverse=True)
    entries = [(x, _pt(state, x)[0], _pt(state, x)[2]) for x in vig + nonvig[keep:]]
    if oko is not None:
        entries.append(oko)
    if limit_one and len(entries) > 1:
        entries = [max(entries, key=lambda e: e[1] * (2 if "double_strike" in e[2] else 1))]
    dmg = 0
    for x, p, kw in entries:
        steps = 2 if "double_strike" in kw else 1
        dmg += p * steps
        if "lifelink" in kw:
            state.life += p * steps
            state.our_lifelink_gain_total += p * steps
        if x in state.tamiyo_fr_marked and p > 0:
            state.draw(steps)
            state.pw_draws_total += steps
            state.tamiyo_fr_combat_draws_total += steps
        if "vigilance" not in kw and x[0] != "Oko, the Ringleader":
            state.our_tapped.append(x)
    state.our_combat_damage_proxy_total += dmg


def _cast_our_spell(state: GameState, name: str, cost: int, log: List[Dict]):
    """Conjura uma remocao/wipe nossa com efeito real (modelo de combate).
    Os gatilhos de 'whenever you cast' continuam disparando aqui tambem
    (Regra #3: gatilho compartilhado em TODO ponto de conjuracao)."""
    state.hand.remove(name)
    state.mana_spent_this_turn += cost
    state.graveyard.append(name)
    state.interaction_spells_cast_total += 1
    if state.has("Inexorable Tide"):
        proliferate_loyalty(state, log, source="inexorable_tide")
    if state.has("Flux Channeler"):
        proliferate_loyalty(state, log, source="flux_channeler")
    log.append({"action": "cast", "card": name, "cost": cost, "turn": state.turn})


def _castable_now(state: GameState, cost: int, colors: Dict[str, int], reserved: int) -> bool:
    """`colors` = simbolos coloridos do custo ({B}{B} -> {"B": 2}): exige
    uma fonte distinta por simbolo."""
    if remaining_mana(state) - reserved < cost:
        return False
    return all(color_sources(state, col) >= k for col, k in colors.items())


def _wipe_option(state: GameState, name: str, reserved: int):
    """(custo, cores, max_toughness, como) se castavel agora, senao None."""
    if name not in state.hand:
        return None
    n_creatures = sum(len(b) for b in state.opp_boards) + len(_our_creature_instances(state))
    if name == "Toxic Deluge":
        # {2}{B} + pague X de vida: "All creatures get -X/-X" -- X = maior
        # resistencia de oponente (mata tudo deles), so' se a vida aguenta.
        x = max((c["t"] for b in state.opp_boards for c in b), default=0)
        if state.life - x <= 10:
            return None
        opt = (3, {"B": 1}, x, "destroy")
    elif name == "Damn":
        opt = (4, {"W": 2}, None, "destroy")   # overload {2}{W}{W}
    elif name == "Supreme Verdict":
        opt = (4, {"W": 2, "U": 1}, None, "destroy")  # {1}{W}{W}{U}
    elif name == "Blasphemous Act":
        # {8}{R}, "costs {1} less for each creature on the battlefield"
        # (minimo so' o {R}); "13 damage to each creature" -- resistencia 14+
        # sobrevive (comandante voltron chega a 20).
        opt = (max(1, 9 - n_creatures), {"R": 1}, 13, "destroy")
    elif name == "Farewell":
        opt = (6, {"W": 2}, None, "exile")     # {4}{W}{W}, modo "Exile all creatures" (so' esse)
    else:
        return None
    return opt if _castable_now(state, opt[0], opt[1], reserved) else None


def _mass_creature_removal(state: GameState, how: str, log: List[Dict], max_toughness: Optional[int] = None,
                           min_power: Optional[int] = None, source: str = ""):
    """Remocao em massa SIMETRICA (nossos wipes, Elspeth -3): pega os 2
    lados da mesa. Toxic Deluge: -X/-X (so' morre resistencia <= X)."""
    _clear_all_opp_boards(state, how=how, max_toughness=max_toughness, min_power=min_power)
    victims = []
    for x in _our_creature_instances(state):
        p, t, _ = _pt(state, x)
        if max_toughness is not None and t > max_toughness:
            continue
        if min_power is not None and p < min_power:
            continue
        victims.append(x)
    for x in sorted(victims, key=lambda v: (v[0], -(v[1] if v[1] is not None else -1))):
        if x[0] in state.battlefield:
            _our_creature_leaves(state, x[0], log, exiled=(how == "exile"), source=source, inst=x)


def _cast_defensive_spells(state: GameState, log: List[Dict], reserved: int):
    for _ in range(6):
        threats = _opp_threats(state)
        if not threats:
            return
        opp_power = sum(c["p"] for _, c in threats)
        our_power = sum(_pt(state, x)[0] for x in _our_creature_instances(state))
        if opp_power >= WIPE_MIN_OPP_POWER and opp_power >= 2 * our_power:
            best = None
            for w in WIPE_SPELL_NAMES:
                opt = _wipe_option(state, w, reserved)
                if opt and (best is None or opt[0] < best[1][0]):
                    best = (w, opt)
            if best:
                w, (cost, _, max_t, how) = best
                if w == "Toxic Deluge":
                    state.life -= max_t  # custo adicional: pague X de vida
                _cast_our_spell(state, w, cost, log)
                _mass_creature_removal(state, how, log, max_toughness=max_t, source=w)
                state.our_wipes_cast_total += 1
                continue
        i, big = _biggest_threat(state)
        min_loy = min(state.loyalty.values()) if state.loyalty else 99
        if big["p"] >= SPOT_REMOVAL_MIN_POWER or (big["p"] >= THREAT_POWER and big["p"] >= min_loy):
            opts = [(v[0], s) for s, v in SPOT_REMOVAL_SPELLS.items()
                    if s in state.hand and _castable_now(state, v[0], v[1], reserved)]
            if opts:
                cost, s = min(opts)
                _cast_our_spell(state, s, cost, log)
                if s == "Anguished Unmaking":
                    state.life -= 3
                _opp_remove_creature(state, i, big, how=SPOT_REMOVAL_SPELLS[s][2])
                state.our_spot_removal_cast_total += 1
                continue
        return


def _pw_defensive_activation(state: GameState, pw: str, loy: int, log: List[Dict]) -> bool:
    """Modo de remocao/controle do planeswalker, quando ha' ameaca real.
    Ultimates que ja' fecham o jogo continuam com prioridade (a heuristica
    antiga cuida delas): so' entra aqui abaixo do limiar do ultimate."""
    threats = _opp_threats(state)
    if not threats:
        return False
    i, big = _biggest_threat(state)
    n = len(threats)
    if pw == "Nicol Bolas, Dragon-God" and 3 <= loy < 8 and big["p"] >= THREAT_POWER:
        add_loyalty(state, pw, -3, log, reason="bolas_minus3_defense")      # "Destroy target creature or planeswalker."
        _opp_remove_creature(state, i, big, how="destroy")
    elif pw == "Kaya, Intangible Slayer" and loy >= 4 and big["p"] >= THREAT_POWER:
        add_loyalty(state, pw, -3, log, reason="kaya_minus3_defense")       # exila + copia 1/1 voadora pra nos
        _opp_remove_creature(state, i, big, how="exile")
        make_pw_token(state, "Spirit Token", 1, log)
    elif pw == "Vraska, Betrayal's Sting" and loy >= 3 and big["p"] >= SPOT_REMOVAL_MIN_POWER:
        add_loyalty(state, pw, -2, log, reason="vraska_minus2_defense")     # vira Treasure (sai como criatura)
        _opp_remove_creature(state, i, big, how="treasure", cooldown=2)
    elif pw == "Teferi, Hero of Dominaria" and 4 <= loy < 8 and big["p"] >= 5:
        add_loyalty(state, pw, -3, log, reason="teferi_hero_minus3_defense")  # 3a do topo da biblioteca
        _opp_remove_creature(state, i, big, how="library")
    elif pw == "The Eternal Wanderer" and loy >= 5 and n >= 5:
        add_loyalty(state, pw, -4, log, reason="wanderer_minus4_defense")
        # "For each player, choose a creature that player controls. Each
        # player sacrifices all creatures they control not chosen" -- NOS
        # escolhemos: a mais fraca de cada oponente, a nossa melhor.
        for j, b in enumerate(state.opp_boards):
            if b:
                keep = min(b, key=lambda c: c["p"])
                for c in list(b):
                    if c is not keep:
                        _opp_remove_creature(state, j, c, how="sacrifice")
        ours = _our_creature_instances(state)
        if ours:
            keep_us = max(ours, key=lambda x: _pt(state, x)[0] + _pt(state, x)[1])
            for x in sorted([x for x in ours if x != keep_us], key=lambda v: (v[0], -(v[1] if v[1] is not None else -1))):
                _our_creature_leaves(state, x[0], log, exiled=False, source="wanderer_minus4", inst=x)
    elif pw == "The Eternal Wanderer" and big["p"] >= SPOT_REMOVAL_MIN_POWER:
        add_loyalty(state, pw, 1, log, reason="wanderer_plus1_defense")
        # "Exile up to one target artifact or creature. Return that card to
        # the battlefield ... at the beginning of that player's next end
        # step." Ficha exilada deixa de existir; carta nao ataca no proximo
        # turno do dono (e o comandante volta sem as auras).
        if big["token"]:
            _opp_remove_creature(state, i, big, how="exile")
        else:
            if big["cmd"]:
                lost = max(0, (big["p"] - VOLTRON_BASE) // 2)
                big["p"] -= lost
                big["t"] -= lost
            big["frozen"] = 1
    elif pw == "Elspeth, Sun's Champion" and 4 <= loy < 7:
        opp_big = sum(c["p"] for _, c in threats if c["p"] >= 4)
        our_big = sum(_pt(state, x)[0] for x in _our_creature_instances(state) if _pt(state, x)[0] >= 4)
        if not (opp_big >= 8 and opp_big > 2 * our_big):
            return False
        add_loyalty(state, pw, -3, log, reason="elspeth_minus3_defense")    # "Destroy all creatures with power 4 or greater."
        _mass_creature_removal(state, "destroy", log, min_power=4, source="elspeth_minus3")
    elif pw == "Liliana, Dreadhorde General" and 5 <= loy < 9 and n >= 4:
        add_loyalty(state, pw, -4, log, reason="liliana_minus4_defense")
        # "Each player sacrifices two creatures of their choice." -- cada
        # um escolhe as 2 mais fracas.
        for j, b in enumerate(state.opp_boards):
            for c in sorted(b, key=lambda c: (c["cmd"], c["p"]))[:2]:
                _opp_remove_creature(state, j, c, how="sacrifice")
        ours = sorted(_our_creature_instances(state), key=lambda x: _blocker_value(state, x))[:2]
        for x in sorted(ours, key=lambda v: (v[0], -(v[1] if v[1] is not None else -1))):
            _our_creature_leaves(state, x[0], log, exiled=False, source="liliana_minus4", inst=x)
    elif pw == "Ugin, the Spirit Dragon" and loy < 10 and _ugin_minus_x_choice(state, loy) is not None:
        x = _ugin_minus_x_choice(state, loy)
        add_loyalty(state, pw, -x, log, reason="ugin_minus_x_defense")
        _ugin_minus_x(state, x, log)
    elif pw == "Tamiyo, Field Researcher" and 3 <= loy < 7 and big["p"] >= THREAT_POWER:
        add_loyalty(state, pw, -2, log, reason="tamiyo_researcher_minus2_defense")
        _freeze_biggest_threats(state, 2, log, source="tamiyo_researcher_minus2")
    else:
        return False
    state.pw_defensive_uses_total += 1
    return True


def try_smart_opponent_turn(state: GameState, log: List[Dict], opp_index: int = 0):
    """Simula O TURNO DE UM oponente dentro da rodada entre os meus
    turnos (mesmo design final ja' validado nos outros 6 decks, Regra
    #6 do CLAUDE.md: bug de orquestracao de turno que auditoria
    carta-a-carta nao pega). Chamada `NUM_OPPONENTS` vezes por rodada --
    um wipe de um oponente ANTERIOR na rodada continua afetando
    corretamente o ataque de um oponente POSTERIOR na MESMA rodada
    (chamadas em sequencia, mesmo `state`).

    Gate de atencao: antes de rolar QUALQUER categoria, este turno de
    oponente precisa passar em `OPPONENT_ATTENTION_CHANCE`.

    Modelo de combate (2026-09-24): o untap/desenvolvimento do campo do
    oponente (`_opp_turn_start`) roda TODO turno dele, ANTES do gate (o
    campo dele cresce mesmo quando ele nao esta' olhando pra mim). Ordem
    real do turno dele: main 1 (wipe) -> combate (`opponent_combat`) ->
    main 2 (o resto). O wipe de criatura dele limpa os campos de TODOS
    os oponentes tambem (simetrico) -- substitui o antigo
    `wiped_this_round`."""
    if attack_model_on(state):
        _opp_turn_start(state, opp_index)
    if state.turn > INTERACTION_SETUP_TURNS and state.interaction_rng.random() >= OPPONENT_ATTENTION_CHANCE:
        return
    try_smart_opponent_wipe(state, log)
    if attack_model_on(state):
        opponent_combat(state, opp_index, log)
    try_smart_opponent_graveyard_wipe(state, log)
    try_smart_opponent_graveyard_snipe(state, log)
    try_smart_opponent_removal(state, log)
    try_smart_opponent_discard(state, log)

def simulate_one_with_interaction(seed: int, turns: int, with_greater_auramancy: bool = False,
                                  attack_profile: Optional[str] = "mixed",
                                  swap: Optional[tuple] = None) -> GameState:
    """Mesmo goldfish de `simulate_one`, mas com `NUM_OPPONENTS` turnos
    de oponente de verdade simulados (`try_smart_opponent_turn`) a cada
    rodada entre os meus turnos, e `resolve_removal_round` (sistema
    ANTIGO) desligado via `skip_legacy_removal=True` (ver decisao do
    usuario no topo da secao). Counterspell (7a categoria) NAO mora
    neste loop -- ver `try_smart_opponent_counter`, chamada de dentro de
    `cast_bridge` no exato momento do cast (normal ou flash).

    Mulligan duplicado (nao extraido pra helper compartilhado) de
    proposito -- este arquivo nunca teve uma funcao `mulligan()`
    separada, e extrair uma agora tocaria `simulate_one` (modo padrao)
    sem necessidade real -- mais seguro duplicar aqui.

    NUNCA chamado por `run_batch`/`simulate_one` padrao. Retorna o
    `GameState` bruto (nao um dict resumido como `simulate_one`), mesma
    convencao dos outros 6 decks.

    `attack_profile` (modelo de combate, 2026-09-24): "mixed" (default --
    mesa real do usuario, arquetipo sorteado por oponente), "go_wide",
    "voltron", "low" (os 3 oponentes com o mesmo arquetipo) ou None (sem
    criatura de oponente nenhuma). `swap=(sai, entra)`: troca 1 carta da
    lista so' nesta simulacao (A/B de pillowfort) -- a lista real nao muda."""
    if attack_profile is not None and attack_profile not in ATTACK_PROFILES:
        raise ValueError(f"attack_profile invalido: {attack_profile}")
    rng = random.Random(seed)
    decklist = build_decklist(with_greater_auramancy)
    if swap is not None:
        out_card, in_card = swap
        assert f"1 {out_card}\n" in decklist, f"{out_card} nao esta' na lista"
        assert in_card in CARD_DB, f"{in_card} sem entrada no CARD_DB"
        decklist = decklist.replace(f"1 {out_card}\n", f"1 {in_card}\n", 1)
    deck = parse_decklist(decklist)
    assert len(deck) == 99, f"Mainboard deveria ser 99, deu {len(deck)}"
    rng.shuffle(deck)
    state = GameState(rng=rng, library=deck, with_greater_auramancy=with_greater_auramancy,
                       interaction_rng=random.Random(seed + 999_999))
    if attack_profile is not None:
        state.attack_profile = attack_profile
        if attack_profile == "mixed":
            state.opp_archetypes = [state.interaction_rng.choice(OPP_ARCHETYPES) for _ in range(NUM_OPPONENTS)]
        else:
            state.opp_archetypes = [attack_profile] * NUM_OPPONENTS
        state.opp_boards = [[] for _ in range(NUM_OPPONENTS)]
        state.opp_cmd_cooldown = [0] * NUM_OPPONENTS
        state.opp_cmd_bonus = [0] * NUM_OPPONENTS

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
    penalty = max(0, mulligans - 1)
    if penalty:
        bottoms = choose_bottom(state.hand, penalty)
        for c in bottoms:
            state.hand.remove(c)
            state.library.append(c)
        rng.shuffle(state.library)

    game_log = []
    interaction_log: List[Dict] = []
    t = 0
    turns_played = 0
    while turns_played < turns:
        t += 1
        play_turn(state, t, game_log, skip_legacy_removal=True)
        turns_played += 1
        for i in range(NUM_OPPONENTS):
            try_smart_opponent_turn(state, interaction_log, opp_index=i)
        while state.extra_turns_pending > 0 and turns_played < turns:
            state.extra_turns_pending -= 1
            t += 1
            play_turn(state, t, game_log, skip_legacy_removal=True)
            turns_played += 1
            for i in range(NUM_OPPONENTS):
                try_smart_opponent_turn(state, interaction_log, opp_index=i)
    return state

def run_batch_with_interaction(n=2000, turns=10, with_greater_auramancy=False, seed_base=6000000,
                               attack_profile="mixed", swap=None):
    """Batch do modo de resiliencia -- reporta so' as metricas
    relevantes pra 'o motor aguenta perder a peca central?', nao
    duplica o relatorio inteiro do `run_batch` padrao."""
    states = [simulate_one_with_interaction(seed_base + i, turns=turns,
                                             with_greater_auramancy=with_greater_auramancy,
                                             attack_profile=attack_profile, swap=swap) for i in range(n)]

    def avg(vals):
        return sum(vals) / len(vals) if vals else 0.0

    print(f"=== Prismatic Bridge Goldfish v1 - MODO DE RESILIENCIA - n={n}, turns={turns}, Greater Auramancy={with_greater_auramancy}, "
          f"mesa={attack_profile}, troca={swap} ===")
    print(f"Avg remocoes inteligentes sofridas: {avg([s.smart_removals_total for s in states]):.2f}")
    print(f"Avg criaturas de oponente atacando (total): {avg([s.opp_attackers_total for s in states]):.2f} "
          f"(em planeswalker: {avg([s.opp_attacks_on_pw_total for s in states]):.2f})")
    print(f"Avg dano de combate em planeswalker: {avg([s.pw_combat_damage_total for s in states]):.2f} | "
          f"PWs mortos em combate: {avg([s.pw_combat_deaths_total for s in states]):.2f} | "
          f"dano de combate na vida: {avg([s.face_combat_damage_total for s in states]):.2f}")
    print(f"Avg PW-turnos vivos: {avg([s.pw_turns_alive_total for s in states]):.2f} | ativacoes: "
          f"{avg([s.pw_activations_total for s in states]):.2f} | ultimates: {avg([s.pw_ultimates_used_total for s in states]):.2f} | "
          f"usos defensivos: {avg([s.pw_defensive_uses_total for s in states]):.2f}")
    print(f"Avg bloqueios: {avg([s.blocks_total for s in states]):.2f} | bloqueadores perdidos: "
          f"{avg([s.our_blockers_lost_total for s in states]):.2f} | criaturas de oponente mortas: "
          f"{avg([s.opp_creatures_killed_total for s in states]):.2f}")
    print(f"Avg nossos wipes: {avg([s.our_wipes_cast_total for s in states]):.2f} | nossas remocoes pontuais: "
          f"{avg([s.our_spot_removal_cast_total for s in states]):.2f}")
    print(f"Avg atacantes barrados por imposto: {avg([s.attackers_stopped_by_tax_total for s in states]):.2f} | "
          f"redirecionados pro PW (Ghostly Prison): {avg([s.attackers_redirected_to_pw_total for s in states]):.2f} | "
          f"cortados por 'so' 1 ataca': {avg([s.attackers_limited_total for s in states]):.2f}")
    print(f"Avg dano de combate nosso (proxy): {avg([s.our_combat_damage_proxy_total for s in states]):.2f}")
    print(f"Avg descartes forcados sofridos: {avg([s.smart_discards_total for s in states]):.2f}")
    print(f"Avg board wipes sofridos: {avg([s.smart_wipes_total for s in states]):.2f}")
    print(f"Avg artifact wipes sofridos: {avg([s.smart_artifact_wipes_total for s in states]):.2f}")
    print(f"Avg enchantment wipes sofridos: {avg([s.smart_enchantment_wipes_total for s in states]):.2f}")
    print(f"Board wipe sofrido em {100*sum(1 for s in states if s.smart_wipes_total > 0)/n:.1f}% das partidas")
    print(f"Avg graveyard wipes (mass exile) sofridos: {avg([s.smart_graveyard_wipes_total for s in states]):.2f}")
    print(f"Avg graveyard snipes (exilio unico) sofridos: {avg([s.smart_graveyard_snipes_total for s in states]):.2f}")
    print(f"Avg counterspells sofridos (cast da Bridge): {avg([s.smart_counters_total for s in states]):.2f}")
    print(f"Avg vida final: {avg([s.life for s in states]):.2f}")
    never_cast = sum(1 for s in states if s.bridge_cast_count == 0)
    print(f"Bridge nunca conjurada em {turns} turnos: {100*never_cast/n:.1f}%")
    recast = sum(1 for s in states if s.bridge_cast_count >= 2)
    print(f"Bridge recastada ao menos 1x (removida e voltou): {100*recast/n:.1f}%")
    return states


if __name__ == "__main__":
    run_batch(n=2000, turns=10, with_greater_auramancy=False, label="SEM Greater Auramancy (lista atual)")
    run_batch(n=2000, turns=10, with_greater_auramancy=True, label="COM Greater Auramancy (troca The Peregrine Dynamo)")
