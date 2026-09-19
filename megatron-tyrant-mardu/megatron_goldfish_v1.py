"""
Goldfish simulator — Megatron, Tyrant (Mardu, B/R/W)
RECONSTRUCAO COMPLETA 2026-09-02.

A versao anterior deste arquivo (motor "Megatron sacrifica combustivel
barato todo turno") foi montada a partir de frequencia entre decklists
publicas + primer de comunidade. O dono real do deck (o oponente citado
nas partidas presenciadas pelo usuario) passou a lista inicial dele, e
comparando ficou claro que o plano de jogo real e' outro por completo:

    SOLDA/RECUPERA ARTEFATO (Goblin Welder, Trash for Treasure, Scrap
    Welder, Scrap Trawler, Daretti Scrap Savant, Daretti Rocketeer
    Engineer) + CHEAT PRA CAMPO (Sneak Attack, Anrakyr the Traveller,
    Feldon of the Third Path) + WARSTORM SURGE como motor de dano
    ("whenever a creature you control enters, it deals damage equal to
    its power to any target" -- dispara em TODO ETB de criatura, nao so'
    em ataque).

Ver `references/goldfish-sim-card-rules.md` (checklist de 13 categorias)
e `references/user-standing-rules.md`. Lista final e a decisao carta a
carta (8 cortes da lista original + 8 adicoes confirmadas + terrenos
premium ABUR) em `lista.md`, `checklist-oraculo.md` e `goldfish-log.md`.

======================================================================
MECANICA REAL DO MEGATRON (inalterada da versao anterior, ja verificada
via Scryfall)
======================================================================
Megatron e' um DFC `transform`: frente ("Tyrant", {3}{R}{W}{B} ou MTMTE
{1}{R}{W}{B}, 7/5) "opponents can't cast spells during combat" +
converte no postcombat main gerando mana = vida perdida pelos
oponentes no turno; verso ("Destructive Force", Vehicle 4/5) ataca e
pode sacrificar OUTRO artefato pra causar dano = MV desse artefato,
convertendo pra Tyrant no meio do combate. So' o Megatron ataca de
verdade nesse motor (mesma convencao da versao anterior) -- o resto do
dano real vem do motor NOVO: Warstorm Surge disparando em cada ETB de
criatura gerado pelos efeitos de cheat/solda/reanimacao.

Simplificacoes documentadas (nao inventadas -- omissoes explicitas):
- Sem oponente real: todo dano/perda-de-vida direcionado a oponente e'
  PROXY agregado (`NUM_OPPONENTS=3`, mesma convencao de todos os
  simuladores desta biblioteca).
- So' o Megatron ataca de verdade (combate real, sem bloqueio) -- as
  outras criaturas geram valor via ETB (Warstorm Surge) e sacrificio,
  nao via combate. Isso e' uma escolha de escopo, nao um limite do
  oraculo: nada na lista real do dono exige uma segunda criatura
  atacando pra funcionar (o motor de dano e' Warstorm Surge, nao
  combate multiplo).
- Efeitos "target opponent"/"each opponent" sempre multiplicados por
  NUM_OPPONENTS quando o oraculo diz "each opponent"; mantidos como
  valor unico quando diz "target opponent" (so' 1 oponente).
- Remocao/interacao sem alvo real de oponente (Path to Exile, Swords to
  Plowshares, Chaos Warp, Vandalblast) conjurada quando ha mana sobrando
  e conta como interaction_spells_cast, mesma convencao de toda a sessao.
"""

from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional
import random

# ---------------------------------------------------------------------------
# Infra de cartas
# ---------------------------------------------------------------------------

@dataclass
class Card:
    name: str
    mv: int
    ctype: str  # "creature" | "artifact" | "enchantment" | "sorcery" | "instant" | "land" | "planeswalker"
    tags: frozenset = field(default_factory=frozenset)
    power: int = 0
    toughness: int = 0
    pips: dict = field(default_factory=dict)
    produces: frozenset = field(default_factory=frozenset)


CARD_DB: dict = {}


def add(name, mv, ctype, tags=(), power=0, toughness=0, pips=None, produces=None):
    CARD_DB[name] = Card(name=name, mv=mv, ctype=ctype, tags=frozenset(tags),
                          power=power, toughness=toughness,
                          pips=dict(pips or {}), produces=frozenset(produces or ()))


COMMANDER = "Megatron, Tyrant"
# Frente (Tyrant): {3}{R}{W}{B}, mv real 6. Custo MTMTE (verso, Destructive
# Force): {1}{R}{W}{B}, mv 4 -- registrado a parte em MEGATRON_* abaixo,
# ja' que o simulador escolhe qual face conjurar dinamicamente (mesmo
# padrao da versao anterior).
add(COMMANDER, 6, "creature", {"commander", "artifact"}, power=7, toughness=5, pips={"R": 1, "W": 1, "B": 1})
MEGATRON_TYRANT_COST = 6
MEGATRON_TYRANT_POWER = 7
MEGATRON_VEHICLE_COST = 4  # MTMTE
MEGATRON_VEHICLE_POWER = 4
MEGATRON_PIPS = {"R": 1, "W": 1, "B": 1}

NUM_OPPONENTS = 3  # premissa declarada (mesa de 4), nunca vida real rastreada
CHANDRAS_IGNITION_LETHAL_THRESHOLD = 70
POISON_LETHAL = 10  # regra real: 10+ marcadores de veneno = derrota (BlightSteel Colossus tem Infect)
COMMANDER_DAMAGE_LETHAL = 21  # regra real: 21+ de dano de combate do MESMO comandante ao mesmo jogador = derrota (CR 704.5c/903.10a)
# Achado real 2026-09-15 (usuario apontou o uso real da carta -- "se
# tiver 2 oponentes com 7 ou menos de vida vale usar no Megatron e
# eliminar estes 2, alem de ser boardwipe"): Chandra's Ignition e' um
# FINALIZADOR condicional, nao um wrath simetrico incondicional -- so'
# vale perder o proprio board quando os oponentes ja' estao baixos.
# Este simulador NAO rastreia vida real por oponente (so' o agregado
# `proxy_damage_total`), entao 70 e' uma aproximacao documentada: se ja'
# saiu esse tanto de dano proxy acumulado (mais de 1,5x uma vida inicial
# de 40), e' razoavel supor que pelo menos parte da mesa esta' baixa o
# suficiente pra valer o wipe + queima. Nao e' exato (nao pode ser, sem
# vida real de oponente) -- e' metrica proxy, mesma convencao do resto
# do arquivo pra efeito opponent-dependente, em vez de ignorar a carta
# inteira (que e' o que a versao anterior fazia, via
# `NO_SELF_HARM_EXCLUDE`).

# --- Mana / rampa ------------------------------------------------------------
add("Sol Ring", 1, "artifact", {"rock2"})
add("Arcane Signet", 2, "artifact", {"rock1"}, produces=set("WUBRG"))
add("Fellwar Stone", 2, "artifact", {"rock1"}, produces=set("WUBRG"))
add("Mind Stone", 2, "artifact", {"rock1", "fuel_rock1"})
add("Talisman of Conviction", 2, "artifact", {"rock1"}, produces={"R", "W"})
add("Talisman of Hierarchy", 2, "artifact", {"rock1"}, produces={"W", "B"})
add("Talisman of Indulgence", 2, "artifact", {"rock1"}, produces={"B", "R"})
add("The Eternity Elevator", 5, "artifact", {"rock3", "station"}, pips={})
add("Blightsteel Colossus", 12, "creature", {"artifact", "infect", "blightsteel"}, power=11, toughness=11, pips={})

# --- Motor central: solda / recuperacao de artefato --------------------------
add("Goblin Welder", 1, "creature", {"welder"}, power=1, toughness=1, pips={"R": 1})
add("Goblin Engineer", 2, "creature", {"goblin_engineer"}, power=1, toughness=2, pips={"R": 1})
add("Myr Retriever", 2, "creature", {"artifact", "toolbox_recur"}, power=1, toughness=1, pips={})
add("Junk Diver", 3, "creature", {"artifact", "toolbox_recur"}, power=1, toughness=1, pips={})
add("Scarecrone", 3, "creature", {"artifact", "scarecrone"}, power=1, toughness=2, pips={})  # Achado real 2026-09-11
add("Scrap Trawler", 3, "creature", {"artifact", "scrap_trawler"}, power=3, toughness=2, pips={})
add("Scrap Welder", 3, "creature", {"scrap_welder"}, power=3, toughness=3, pips={"R": 1})
add("Feldon of the Third Path", 3, "creature", {"feldon"}, power=2, toughness=3, pips={"R": 2})
add("Trash for Treasure", 3, "sorcery", {"trash_for_treasure"}, pips={"R": 1})
add("Daretti, Scrap Savant", 4, "planeswalker", {"daretti_savant"}, pips={"R": 1})
add("Anrakyr the Traveller", 5, "creature", {"artifact", "anrakyr"}, power=4, toughness=4, pips={"B": 1})
add("Daretti, Rocketeer Engineer", 5, "creature", {"daretti_rocketeer"}, power=0, toughness=5, pips={"R": 1})
add("Mishra, Tamer of Mak Fawa", 5, "creature", {"mishra_unearth_all"}, power=4, toughness=4, pips={"B": 1, "R": 1})
add("Osgir, the Reconstructor", 4, "creature", {"osgir_clone"}, power=4, toughness=4, pips={"R": 1, "W": 1})  # Achado real 2026-09-04: NAO e' artefato (Legendary Creature -- Giant Artificer), so' cuida de artefato

# --- Cheat pra campo -----------------------------------------------------------
add("Sneak Attack", 4, "enchantment", {"sneak_attack"}, pips={"R": 1})

# --- Sacrificio / payoff -------------------------------------------------------
add("Ayara, Widow of the Realm", 3, "creature", {"ayara"}, power=3, toughness=3, pips={"B": 2})
add("Rakdos, the Muscle", 5, "creature", {"rakdos_sac_creature"}, power=6, toughness=5, pips={"B": 2, "R": 1})
add("Pia's Revolution", 3, "enchantment", {"pia_revolution"}, pips={"R": 1})  # Achado real 2026-09-04 (EDHREC)

# --- Corpo grande / finalizadores (fodder real pro motor de solda/cheat) ------
add("Cursed Mirror", 3, "artifact", {"fuel_rock1", "cursed_mirror_clone"}, pips={"R": 1}, produces={"R"})
add("Ironsoul Enforcer", 5, "creature", {"artifact", "ironsoul"}, power=4, toughness=4, pips={"W": 1})
add("Combustible Gearhulk", 6, "creature", {"artifact", "combustible_gearhulk"}, power=6, toughness=6, pips={"R": 2})
add("Noxious Gearhulk", 6, "creature", {"artifact", "noxious_gearhulk"}, power=5, toughness=4, pips={"B": 2})
add("Steel Seraph", 6, "creature", {"artifact", "steel_seraph"}, power=5, toughness=4, pips={"W": 1})
# Achado real 2026-09-15 (usuario apontou o uso real -- removal + fuel
# pro Megatron): oraculo real e' "Artifact -- VEHICLE" (Crew 2), NAO
# "Artifact Creature"! ctype corrigido pra "artifact" -- Vehicle
# desanimado nao e' criatura (nao dispara Warstorm Surge no ETB, nao
# ataca sozinho em `all_attackers_combat`, CONTA pro desconto do
# Metalwork Colossus como artefato nao-criatura). Usuario confirmou que
# nunca vai crewar -- Crew 2 fica de fora do modelo (0, decisao
# consciente do usuario, nao estrutural).
add("Demonic Junker", 7, "artifact", {"demonic_junker"}, power=4, toughness=3, pips={"B": 1})
add("Bygone Colossus", 9, "creature", {"artifact", "warp3"}, power=9, toughness=9, pips={})
# Achado real 2026-09-15: trocada por Triplicate Titan (mesmo {9}, 9/9,
# artifact creature, mesmo "on death: create three 3/3 Golem artifact
# creature tokens"). Diferenca real do oraculo: Titan tem Flying,
# vigilance, trample no proprio corpo + cada 1 dos 3 tokens ganha 1
# dessas palavras-chave -- mas sem bloqueio real modelado pra ninguem
# no arquivo, isso e' 100% cosmetico aqui (ver `death_trigger`). Titan
# NAO tem o Encore {12} do Triniform (habilidade real, estruturalmente
# modelavel via NUM_OPPONENTS mas nunca implementada -- vira moot com a
# troca, nao precisa mais ser corrigida).
add("Triplicate Titan", 9, "creature", {"artifact"}, power=9, toughness=9, pips={})
add("Skitterbeam Battalion", 9, "creature", {"artifact", "skitterbeam"}, power=4, toughness=4, pips={})
add("Summon: Bahamut", 9, "creature", {"saga_bahamut"}, power=9, toughness=9, pips={})
add("Metalwork Colossus", 11, "creature", {"artifact", "metalwork_colossus"}, power=10, toughness=10, pips={})
# Correcao 2026-09-15 (auditoria comparativa): a analise anterior
# tratava "destroy up to one target nonland permanent" (cast E ataque)
# como 📊 zero por "so' alvo valido no oponente" -- mas essa e' a MESMA
# categoria de Path to Exile/Swords to Plowshares/Vandalblast/Generous
# Gift, todas ja creditadas como interacao real. Corrigido: credita
# `interaction_spells_cast_total` no ETB (cast) E em cada ataque (ver
# `all_attackers_combat`). Unearth {8} tambem estava fora por "caro
# igual ao hardcast" -- mesmo raciocinio usado ANTES de implementar o
# Warp {3} do Bygone Colossus (que E' modelado, `try_bygone_colossus_
# warp`) -- inconsistente excluir so' esse. Implementado
# `try_cityscape_leveler_unearth`, mesmo padrao do Warp (reanima
# temporario com haste, exilado no fim do turno).
add("Cityscape Leveler", 8, "creature", {"artifact", "cityscape_leveler"}, power=8, toughness=8, pips={})  # Achado real 2026-09-11

# --- Artefatos de valor continuo ----------------------------------------------
add("Nexus of Becoming", 6, "artifact", {"nexus_combat_draw_copy"}, pips={})
# Achado real 2026-09-11: trocada por Ultron, Artificial Malevolence
# (Marvel Super Heroes, 2026-06-26, legal) -- mesmo gatilho/custo real
# ("whenever another nontoken artifact you control enters, pay {2}:
# create a copy token" -- MESMO {2} flat do Mirrorworks, nao X=MV),
# mas Ultron E' criatura (2/4 colorless) -- participa de combate e
# dispara Warstorm Surge na propria entrada (ao contrario do Mirrorworks,
# artefato puro). Simplificacao documentada: a clausula extra do Ultron
# ("se o token copiado NAO for criatura, ele se torna 2/2 Robot Villain
# tambem") fica fora -- token continua exatamente igual ao original via
# `make_token_copy_name`, mesma convencao ja usada pra todo copy-effect
# do arquivo (Cursed Mirror/Adagia/etc).
add("Ultron, Artificial Malevolence", 3, "creature", {"artifact"}, power=2, toughness=4, pips={})
add("Portal to Phyrexia", 9, "artifact", {"portal_phyrexia"}, pips={})
add("Warstorm Surge", 6, "enchantment", {"warstorm_surge"}, pips={"R": 1})
add("Brass's Tunnel-Grinder", 3, "artifact", {"tunnel_grinder"}, pips={"R": 1})
# Tecutlan, the Searing Rift: verso apos transformar (land). "Whenever
# you cast a permanent spell using mana produced by Tecutlan, discover
# X" fica fora do modelo -- nao rastreamos qual fonte de mana especifica
# pagou cada gasto em lugar nenhum do arquivo (mesma limitacao
# estrutural que ja impede modelar o dano das Talismans). Fica so' como
# terreno R normal apos transformar.
add("Tecutlan, the Searing Rift", 0, "land", set(), produces={"R"})
add("Cosmic Cube", 5, "artifact", {"cosmic_cube"}, pips={})  # Achado real 2026-09-03
add("Genesis Chamber", 2, "artifact", {"genesis_chamber"}, pips={})  # Achado real 2026-09-09
add("Tarrian's Journal", 2, "artifact", {"tarrians_journal"}, pips={"B": 1})  # Achado real 2026-09-09

# --- Draw / filtragem ----------------------------------------------------------
add("Faithless Looting", 1, "sorcery", {"loot2_2_flashback"}, pips={"R": 1})
# Achado real 2026-09-15: trocada por Melded Moxite (Edge of Eternities,
# 2025-08-01, legal) -- mesmo "discard 1, draw 2" do Demand Answers, mas
# como ARTEFATO PERMANENTE entrando: dispara o Ultron (copia via {2}),
# reduz o custo do Metalwork Colossus enquanto fica em campo, e e' alvo
# valido de Goblin Engineer (busca sem restricao + reanima MV<=3, ela e'
# MV 2)/Goblin Welder/Trash for Treasure (todos exigem "artifact card" no
# cemiterio -- Demand Answers, sendo instant, nunca voltava pra lugar
# nenhum depois de resolver). A 2a habilidade ({3}, sac: cria Robot 2/2)
# ainda alimenta o flip do Megatron (combustivel de sacrificio) e gera
# mais um gatilho de Warstorm Surge quando o token entra.
add("Melded Moxite", 2, "artifact", {"melded_moxite"}, pips={"R": 1})
add("Black Market Connections", 3, "enchantment", {"black_market"}, pips={"B": 1})
add("Saheeli's Directive", 3, "sorcery", {"saheeli_directive"}, pips={"R": 3})
add("The Ten Rings", 8, "artifact", {"ten_rings"}, pips={})

# --- Removal / interacao (sem alvo real de oponente) ---------------------------
add("Path to Exile", 1, "instant", {"interaction"}, pips={"W": 1})
add("Swords to Plowshares", 1, "instant", {"interaction"}, pips={"W": 1})
add("Vandalblast", 1, "sorcery", {"interaction"}, pips={"R": 1})
add("Chaos Warp", 3, "instant", {"interaction"}, pips={"R": 1})
add("Generous Gift", 3, "instant", {"interaction"}, pips={"W": 1})  # Achado real 2026-09-11
add("Decree of Pain", 8, "sorcery", {"decree_of_pain"}, pips={"B": 2})
add("Heartless Conscription", 8, "sorcery", {"heartless_conscription"}, pips={"B": 2})
add("Blasphemous Act", 9, "sorcery", {"wipe_reduces_creatures"}, pips={"R": 1})
add("Chandra's Ignition", 5, "sorcery", {"chandras_ignition"}, pips={"R": 2})

# --- Protecao / equipment --------------------------------------------------------
add("Lightning Greaves", 2, "artifact", {"haste_shroud_equip"}, pips={})
add("Clever Concealment", 4, "instant", {"clever_concealment"}, pips={"W": 2})  # Achado real
# 2026-09-02: Shields Up! e' do set Star Trek, lancamento 2026-11-13 --
# usuario apontou que ainda nao foi lancada (nao e' legal em Commander
# ainda). Substituida primeiro por Loran's Escape (protege so' 1
# permanente), depois trocada de novo por pedido direto do usuario pra
# Clever Concealment (Marvel Super Heroes Commander, 2026-06-26, real e
# legal): "{2}{W}{W}, Convoke -- any number of target nonland permanents
# you control phase out." Protege o board INTEIRO contra wrath (nao so'
# 1 peca), custo efetivo baixo na pratica ja' que Convoke tapa fodder que
# ia ser sacrificado no fim do turno mesmo (Sneak Attack/Feldon).
add("Blacksmith's Skill", 1, "instant", {"blacksmiths_skill"}, pips={"W": 1})

# --- Ataque solo -------------------------------------------------------------
add("Treasure Nabber", 3, "creature", {"opponent_dependent"}, power=3, toughness=2, pips={"R": 1})

# --- Terrenos --------------------------------------------------------------------
LAND_BASIC_TYPES = {
    "Plateau": {"Mountain", "Plains"}, "Scrubland": {"Plains", "Swamp"}, "Badlands": {"Swamp", "Mountain"},
    "Smoldering Marsh": {"Swamp", "Mountain"},
    "Mountain": {"Mountain"}, "Plains": {"Plains"}, "Swamp": {"Swamp"},
}
add("Badlands", 0, "land", set(), produces={"B", "R"})
add("Command Tower", 0, "land", set(), produces={"W", "B", "R"})
add("Exotic Orchard", 0, "land", set(), produces={"W", "B", "R"})
add("Forbidden Orchard", 0, "land", set(), produces={"W", "B", "R"})
add("Fountainport", 0, "land", {"fountainport"}, produces=set())  # Achado real 2026-09-09: so' produz {C}, nao fixa W/B/R
add("Plateau", 0, "land", set(), produces={"R", "W"})
add("Scrubland", 0, "land", set(), produces={"W", "B"})
add("Smoldering Marsh", 0, "land", {"etb_tapped_check"}, produces={"B", "R"})
add("Susur Secundi, Void Altar", 0, "land", {"station", "etb_tapped"}, produces={"B"})
add("Mountain", 0, "land", set(), produces={"R"})
add("Plains", 0, "land", set(), produces={"W"})
add("Swamp", 0, "land", set(), produces={"B"})

# --- Manabase DeckTechsforDecks (achado real 2026-09-11) ---------------------
# Usuario testou empiricamente (A/B, 20.000 jogos, mesmas seeds) a manabase
# publicada do DeckTechsforDecks (com as 3 painlands trocadas pelos duais
# ABUR equivalentes, mesmo upgrade que ja tinhamos feito na nossa) contra a
# nossa: "Megatron nunca conjurado em 8 turnos" caiu de 12,9% pra 5,1-5,7%
# (validado tanto com a contagem original de 35 terrenos quanto ajustada pra
# 34, igualando a nossa -- a melhora e' real, nao so' "1 terreno extra").
# Motivo real: mais tri-lands (Nomad Outpost) + 2 fetches reais (Evolving
# Wilds/Terramorphic Expanse) que a nossa base nao tinha nenhum. Adotada
# como nova manabase (Adagia/Ash Barrens saem; Susur Secundi e Fountainport
# ficam, unicos "extras" mantidos por pedido explicito do usuario).
# Fetches/tapped-duals simplificados como fontes fixas + sempre tapped (mesma
# convencao ja usada pra Exotic/Forbidden Orchard -- sem simular
# busca/embaralhamento real).
add("Evolving Wilds", 0, "land", set(), produces={"W", "B", "R"})
add("Terramorphic Expanse", 0, "land", set(), produces={"W", "B", "R"})
add("Rocky Tar Pit", 0, "land", set(), produces={"B", "R"})
add("Nomad Outpost", 0, "land", set(), produces={"W", "B", "R"})
add("Sunlit Marsh", 0, "land", set(), produces={"W", "B"})
add("Myriad Landscape", 0, "land", set(), produces=set())  # so' rampa incolor no modelo simplificado
add("Shadowblood Ridge", 0, "land", set(), produces={"B", "R"})  # untapped real (custo extra de {1} pras 2 cores juntas nao rastreado, mesma convencao do arquivo)

LAND_NAMES = {n for n, c in CARD_DB.items() if c.ctype == "land"}
ETB_TAPPED_LANDS = {
    "Smoldering Marsh", "Susur Secundi, Void Altar",  # Smoldering so' se <2 terrenos; Susur sempre
    "Evolving Wilds", "Terramorphic Expanse", "Rocky Tar Pit", "Nomad Outpost",
    "Sunlit Marsh", "Myriad Landscape",  # todos sempre tapped no oraculo real
}


def is_creature_card(name: str) -> bool:
    return CARD_DB[name].ctype == "creature"


def is_artifact_card(name: str) -> bool:
    return "artifact" in CARD_DB[name].tags or CARD_DB[name].ctype == "artifact"


LEGENDARY_NAMES = {
    "Megatron, Tyrant", "Ayara, Widow of the Realm", "Feldon of the Third Path",
    "Daretti, Scrap Savant", "Daretti, Rocketeer Engineer", "Anrakyr the Traveller",
    "Mishra, Tamer of Mak Fawa", "Osgir, the Reconstructor", "Rakdos, the Muscle",
    "Brass's Tunnel-Grinder", "The Eternity Elevator", "Tarrian's Journal",
    "Susur Secundi, Void Altar", "Ultron, Artificial Malevolence",
}


def is_legendary(name: str) -> bool:
    return name in LEGENDARY_NAMES


def is_historic(name: str) -> bool:
    return is_artifact_card(name) or is_legendary(name) or "saga_bahamut" in CARD_DB[name].tags


def build_library():
    import re
    entries = []
    section = None
    with open("lista.md") as f:
        for line in f:
            s = line.strip()
            if s.startswith("## Comandante"):
                section = "cmd"
                continue
            if s.startswith("## Deck"):
                section = "deck"
                continue
            if s.startswith("## Terrenos"):
                section = "land"
                continue
            if section not in ("deck", "land"):
                continue
            m = re.match(r'^(\d+)\s+(.+)$', s)
            if not m:
                continue
            n, name = int(m.group(1)), m.group(2)
            entries.extend([name] * n)
    return entries


BASE_LIBRARY = build_library()


# ---------------------------------------------------------------------------
# Estado de jogo
# ---------------------------------------------------------------------------

@dataclass
class GameState:
    turn: int = 0
    hand: list = field(default_factory=list)
    battlefield: list = field(default_factory=list)
    graveyard: list = field(default_factory=list)
    library: list = field(default_factory=list)
    exile: list = field(default_factory=list)
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

    # --- motor novo: solda/cheat/sacrificio/Warstorm Surge --------------------
    daretti_savant_loyalty: int = 0
    daretti_savant_ultimate_active: bool = False
    ayara_transformed: bool = False
    ayara_recur_used_this_turn: bool = False
    goblin_welder_used_this_turn: bool = False
    scrap_welder_used_this_turn: bool = False
    feldon_used_this_turn: bool = False
    sneak_attack_used_this_turn: bool = False
    anrakyr_attack_used_this_turn: bool = False
    goblin_engineer_used_this_turn: bool = False
    scarecrone_used_this_turn: bool = False
    mishra_unearth_used_this_turn: bool = False
    osgir_used_this_turn: bool = False
    nexus_used_this_turn: bool = False
    black_market_used_this_turn: bool = False
    losheel_draw_used_this_turn: bool = False
    susur_secundi_used_this_turn: bool = False
    fountainport_used_this_turn: bool = False
    tarrians_journal_used_this_turn: bool = False
    attackers_this_combat: int = 0
    attackers_total_all_turns: int = 0  # soma de todos os combates, pra metrica de run_batch
    max_attacker_power_this_combat: int = 0  # pro gatilho do Cosmic Cube
    charge_counters: dict = field(default_factory=dict)  # nome do Planet -> contadores
    temp_power_boost: dict = field(default_factory=dict)  # nome -> bonus de poder ate' o fim do turno (Osgir)
    bygone_colossus_exiled_warp: bool = False
    daretti_rocketeer_mv_seen: int = 0
    temp_creatures_pending_sacrifice: list = field(default_factory=list)
    temp_creatures_pending_exile: list = field(default_factory=list)
    daretti_emblem_pending_return: list = field(default_factory=list)
    triplicate_titan_tokens_total: int = 0
    bahamut_entered_turn: Optional[int] = None
    bahamut_chapter: int = 0
    bahamut_mega_flare_total: int = 0
    tunnel_grinder_bore_counters: int = 0
    turn_start_gy_permanents: int = 0

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
    library_emptied: bool = False
    warstorm_surge_damage_total: int = 0
    warstorm_surge_triggers_total: int = 0
    weld_activations_total: int = 0
    creatures_cheated_in_total: int = 0
    sacrifice_payoff_damage_total: int = 0
    sacrifice_payoff_draws_total: int = 0
    artifacts_sacrificed_total: int = 0
    creatures_sacrificed_total: int = 0
    daretti_savant_minus10_active: bool = False
    cosmic_cube_free_casts_total: int = 0
    ten_rings_draws_total: int = 0
    blightsteel_poison_win: bool = False
    chandras_ignition_infect_kills_total: int = 0
    megatron_commander_damage_dealt: int = 0
    commander_damage_win: bool = False
    portal_phyrexia_reanimations_total: int = 0
    tunnel_grinder_transforms_total: int = 0
    nexus_tokens_created_total: int = 0
    equip_haste_activations_total: int = 0
    pia_revolution_returns_total: int = 0
    genesis_chamber_tokens_total: int = 0
    fountainport_draws_total: int = 0
    fountainport_tokens_total: int = 0
    tarrians_journal_draws_total: int = 0
    melded_moxite_loots_total: int = 0
    melded_moxite_tokens_total: int = 0
    ultron_cheap_copies_total: int = 0
    demonic_junker_removals_total: int = 0
    chandras_ignition_casts_total: int = 0
    chandras_ignition_own_creatures_lost_total: int = 0
    interaction_rng: Optional[random.Random] = None
    rng: Optional[random.Random] = None  # o mesmo rng do mulligan/shuffle inicial, guardado no state pro BlightSteel Colossus (shuffle pra biblioteca)
    smart_removals_total: int = 0
    smart_removal_log: list = field(default_factory=list)
    smart_attacks_taken_total: int = 0
    smart_blocks_total: int = 0
    smart_attack_log: list = field(default_factory=list)
    smart_discards_total: int = 0
    smart_discard_log: list = field(default_factory=list)
    smart_wipes_total: int = 0
    smart_wipe_log: list = field(default_factory=list)
    crewed_creatures_tapped: set = field(default_factory=set)
    ironsoul_triggered_this_combat: bool = False
    megatron_alone_combos_total: int = 0
    demonic_junker_crewed_this_turn: bool = False
    demonic_junker_crews_total: int = 0


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


def gain_life(state: GameState, n: int):
    state.life += n
    state.proxy_lifegain_total += n


def worst_discard_target(state: GameState, pool: list = None):
    """Escolhe a pior carta pra descartar (Faithless Looting/Wheel de
    filtragem/limite de mao no fim do turno). Achado real ao testar: escolher so'
    por MENOR mana value (como o resto do arquivo faz em varios lugares)
    tratava terrenos (MV 0) como sempre "a pior carta" -- looting
    descartava os proprios terrenos da mao antes de conseguirem ser
    jogados, travando o desenvolvimento de mana da partida inteira.
    Corrigido: nunca descarta terreno enquanto houver menos de 6 em campo
    E houver alguma carta nao-terreno pra descartar no lugar; alagado
    (6+ terrenos), terreno volta a ser descartavel normalmente."""
    candidates = pool if pool is not None else state.hand
    if not candidates:
        return None
    lands_in_play = sum(1 for n in state.battlefield if n in LAND_NAMES)
    nonlands = [c for c in candidates if c not in LAND_NAMES]
    if nonlands and lands_in_play < 6:
        return min(nonlands, key=lambda n: CARD_DB[n].mv if n in CARD_DB else 0)
    return min(candidates, key=lambda n: CARD_DB[n].mv if n in CARD_DB else 0)


ROCK_TAG_VALUE = {"rock1": 1, "rock2": 2, "rock3": 3}


def rocks_mana(state: GameState) -> int:
    """Mana generica de rocks continuas. Achado real 2026-09-15 (usuario
    apontou que duplicar um rock de custo 2 via Ultron e' motor real de
    rampa + combustivel de graca pro Megatron): a versao anterior desta
    funcao checava so' PRESENCA ("Sol Ring" in state.battlefield), nunca
    CONTAGEM real de instancias -- uma copia via Ultron (nome com sufixo
    " (copia)" de `make_token_copy_name`) nunca batia em nenhum desses
    checks, e a copia renderia ZERO mana extra mesmo estando de verdade
    em campo. Corrigido: soma por INSTANCIA real na battlefield, lendo a
    tag (`rock1`/`rock2`/`rock3`, preservada em toda copia pois
    `make_token_copy_name` aponta pro mesmo `Card` do original) em vez do
    nome fixo -- generaliza pra qualquer numero de copias."""
    total = 0
    for card in state.battlefield:
        if card not in CARD_DB:
            continue
        tags = CARD_DB[card].tags
        for tag, value in ROCK_TAG_VALUE.items():
            if tag in tags:
                total += value
        if card == "Cursed Mirror":
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
    return n


def has_color_sources_for(state: GameState, name: str) -> bool:
    for color, needed in CARD_DB[name].pips.items():
        if color_sources(state, color) < needed:
            return False
    return True


def spend_mana(state: GameState, n: int):
    state.mana_spent_this_turn += n


def ready_creatures(state: GameState):
    """Criaturas sem doenca de invocacao E nao tapadas. Achado real
    2026-09-15 (Crew do Demonic Junker -- usuario apontou a linha real
    de tapar um token barato pra crewar): antes desta correcao nao
    existia NENHUM conceito de "tapado" no arquivo, so' doenca de
    invocacao -- crew introduz o primeiro caso real de "esta criatura
    ja' tapou por outro motivo esse turno", `crewed_creatures_tapped`
    cobre isso de forma generica (tambem impede usar {T} de novo em
    Welder/Scrap Welder/Engineer/Scarecrone/estacao na MESMA criatura,
    regra real)."""
    return [n for n in state.battlefield if is_creature_card(n)
            and (state.creature_cast_turn.get(n, -1) < state.turn)
            and n not in state.crewed_creatures_tapped]



# ---------------------------------------------------------------------------
# Infra central: ETB (com Warstorm Surge), sacrificio, gatilhos de morte
# ---------------------------------------------------------------------------

def get_power(state: GameState, name: str) -> int:
    """Poder real de uma criatura, com override pras dinamicas (Daretti,
    Rocketeer Engineer: 'power is equal to the greatest mana value among
    artifacts you control') e bonus temporario (Osgir: '+2/+0 until end
    of turn')."""
    if name == "Daretti, Rocketeer Engineer":
        mvs = [CARD_DB[n].mv for n in state.battlefield if is_artifact_card(n) and n != name]
        return max(mvs, default=0) + state.temp_power_boost.get(name, 0)
    return CARD_DB[name].power + state.temp_power_boost.get(name, 0)


def creature_enters(state: GameState, name: str, from_hand: bool = True, token: bool = False):
    """Ponto central de TODA criatura entrando em campo -- cast normal,
    token (Feldon/Skitterbeam/Osgir/Triplicate Titan), ou reanimacao (Trash for
    Treasure/Ayara-flip/Anrakyr/Mishra unearth/Portal to Phyrexia). Dispara
    Warstorm Surge aqui, no unico lugar real do arquivo onde ETB de
    criatura acontece -- garante que NENHUM ponto de entrada escape do
    gatilho ('whenever a creature you control enters, it deals damage
    equal to its power to any target')."""
    if from_hand and name in state.hand:
        state.hand.remove(name)
    state.battlefield.append(name)
    if is_creature_card(name):
        state.creature_cast_turn[name] = state.turn
        if "Warstorm Surge" in state.battlefield:
            power = get_power(state, name)
            if power > 0:
                proxy_drain(state, power)
                state.warstorm_surge_damage_total += power
                state.warstorm_surge_triggers_total += 1
    resolve_etb(state, name, token=token)
    if is_artifact_card(name):
        artifact_etb_hooks(state, name, token=token)
    try_genesis_chamber_token(state, token)


def try_genesis_chamber_token(state: GameState, entering_was_token: bool):
    """Genesis Chamber: 'Whenever a nontoken creature enters, if this
    artifact is untapped, that creature's controller creates a 1/1
    colorless Myr artifact creature token.' Achado real 2026-09-09
    (usuario notou que o token 1/1 vira alvo perfeito pro excesso de
    dano do Destructive Force -- ver `megatron_combat`, que ja assume
    por premissa um alvo de 1 de resistencia sempre disponivel; Genesis
    Chamber torna essa premissa real de verdade em vez de assumida).
    So' modela o lado 'eu mesmo conjuro/reanimo/cheat uma criatura' --
    a metade simetrica (oponente tambem ganha token quando ELE conjura)
    fica fora, estruturalmente (sem oponente real modelado, mesma
    convencao de Treasure Nabber/Noxious Gearhulk). Sem tap real
    modelado pro Genesis Chamber em lugar nenhum do arquivo, ele fica
    sempre destapado. `token=True` (a propria entrada e' de um token)
    nunca dispara de novo -- oraculo real e' 'nontoken creature enters'."""
    if entering_was_token or "Genesis Chamber" not in state.battlefield:
        return
    token_name = "Myr Token"
    if token_name not in CARD_DB:
        add(token_name, 0, "creature", {"artifact"}, power=1, toughness=1)
    creature_enters(state, token_name, from_hand=False, token=True)
    state.genesis_chamber_tokens_total += 1


def sacrifice(state: GameState, name: str, is_own_sacrifice: bool = True):
    """Ponto central de TODO sacrificio/destruicao do arquivo -- remove
    de battlefield, poe no graveyard, dispara os gatilhos reais de
    morte (Scrap Trawler, toolbox Myr Retriever/Junk Diver, Triplicate
    Titan) e os payoffs que disparam em QUALQUER
    sacrificio de criatura (Rakdos, the Muscle -- 'whenever you sacrifice
    another creature', gatilho automatico, nao e' escolha).

    `is_own_sacrifice=False` (achado real 2026-09-16, modo de
    resiliencia via `try_smart_opponent_removal`): quando o permanente
    morre por DESTRUICAO de oponente (nao um sacrificio meu), Rakdos NAO
    dispara -- o oraculo dele e' 'whenever YOU sacrifice', nao 'whenever
    a creature dies'. Todo o resto (ir pro cemiterio/exilio, Scrap
    Trawler, Pia's Revolution, death_trigger) e' igual pras duas causas
    -- essas exigem so' 'put into a graveyard from the battlefield',
    que acontece independente de quem causou.

    Achado real 2026-09-15 (usuario perguntou a regra ao vivo sobre
    sacrificar o Cityscape Leveler reanimado por Unearth pro Megatron --
    confirmou via ruling oficial: 'If a permanent returned to the
    battlefield with unearth would leave the battlefield for any reason,
    it's exiled instead'). Warp (Bygone Colossus) tem o MESMO texto de
    substituicao. Sem esse redirect, sacrificar um permanente Warp/
    Unearth ANTES do fim do turno colocava ele no cemiterio errado --
    dispararia Scrap Trawler/Pia's Revolution/morte do Triplicate Titan
    (todos exigem 'put into a GRAVEYARD', que nunca acontece aqui de
    verdade) e deixaria a carta disponivel pra weld/re-Warp/re-Unearth
    de novo, o que a regra real nao permite (esta' exilada, nao no
    cemiterio). O sacrificio em si ainda conta pra Rakdos (dispara em
    QUALQUER sacrificio, nao em 'dies')."""
    if name not in state.battlefield:
        return
    state.battlefield.remove(name)
    if name in state.temp_creatures_pending_sacrifice:
        state.temp_creatures_pending_sacrifice.remove(name)
    was_creature = is_creature_card(name)
    was_artifact = is_artifact_card(name)
    if name == COMMANDER:
        # Achado real 2026-09-18 (goldfish manual do usuario -- Path to
        # Exile de um oponente no Megatron, via modo de interacao do
        # Archidekt): comandante que sairia do campo pra QUALQUER zona
        # (cemiterio, exilio, mao, biblioteca) pode ir pra ZONA DE
        # COMANDO em vez disso (regra 903.9) -- reconjuravel depois
        # pagando o "commander tax" (`cast_megatron` ja modela o tax via
        # `commander_cast_count`). Sem essa checagem, `sacrifice()`
        # tratava o Megatron como permanente comum: ia pro cemiterio de
        # verdade e `commander_in_play` nunca resetava pra False --
        # travava ele fora do jogo pro resto da partida, sem poder
        # reconjurar (confirmado com teste isolado). Vira bug ATIVO a
        # partir do combo BlightSteel Colossus + Chandra's Ignition
        # (ver `try_chandras_ignition`): "each OTHER creature" tambem
        # atinge o proprio Megatron (toughness 5 <= poder 11 da fonte),
        # entao o combo sacrificava o comandante de verdade sempre que
        # disparava. Escolha sempre pra zona de comando (estritamente
        # melhor pro piloto, mesma convencao de "sempre a jogada boa"
        # usada no resto do arquivo). Ainda conta como sacrificio real
        # pro Rakdos ("whenever you sacrifice", nao depende de cemiterio)
        # mas NAO dispara Scrap Trawler/Pia's Revolution/death_trigger
        # (esses exigem "put into a graveyard", que nunca acontece aqui
        # -- mesmo padrao ja usado pro redirect de Warp/Unearth abaixo).
        state.commander_in_play = False
        state.megatron_face = None
        if was_artifact:
            state.artifacts_sacrificed_total += 1
        if was_creature:
            state.creatures_sacrificed_total += 1
        if is_own_sacrifice and was_creature and "Rakdos, the Muscle" in state.battlefield:
            rakdos_muscle_trigger(state, name)
        return
    if name in state.temp_creatures_pending_exile:
        state.temp_creatures_pending_exile.remove(name)
        state.exile.append(name)
        if was_artifact:
            state.artifacts_sacrificed_total += 1
        if was_creature:
            state.creatures_sacrificed_total += 1
        if is_own_sacrifice and was_creature and name != "Rakdos, the Muscle" and "Rakdos, the Muscle" in state.battlefield:
            rakdos_muscle_trigger(state, name)
        return
    if name == "Blightsteel Colossus":
        # "If Blightsteel Colossus would be put into a graveyard from
        # anywhere, reveal Blightsteel Colossus and shuffle it into its
        # owner's library instead." Substituicao real -- nunca chega a
        # ir pro cemiterio, entao NUNCA e' alvo de Welder/Scrap Welder/
        # Trash for Treasure/Osgir/Scarecrone/Portal to Phyrexia (todos
        # exigem "graveyard"); isso e' consistente com a linha real do
        # combo (hardcast/Sneak Attack/Anrakyr -> ataca ou vira fuel do
        # Megatron -> volta pra biblioteca, pode ser puxado de novo mais
        # tarde, nunca preso morto no cemiterio).
        idx = state.rng.randrange(len(state.library) + 1) if state.rng else len(state.library)
        state.library.insert(idx, name)
        if was_artifact:
            state.artifacts_sacrificed_total += 1
        if was_creature:
            state.creatures_sacrificed_total += 1
        if is_own_sacrifice and was_creature and "Rakdos, the Muscle" in state.battlefield:
            rakdos_muscle_trigger(state, name)
        return
    state.graveyard.append(name)
    if was_artifact:
        state.artifacts_sacrificed_total += 1
        scrap_trawler_trigger(state, name)
        daretti_ultimate_recursion_check(state, name)
        pia_revolution_trigger(state, name)
    if was_creature:
        state.creatures_sacrificed_total += 1
    death_trigger(state, name)
    if is_own_sacrifice and was_creature and name != "Rakdos, the Muscle" and "Rakdos, the Muscle" in state.battlefield:
        rakdos_muscle_trigger(state, name)


def pia_revolution_trigger(state: GameState, dying_name: str):
    """Pia's Revolution: 'Whenever a nontoken artifact is put into your
    graveyard from the battlefield, return that card to your hand unless
    target opponent has this enchantment deal 3 damage to them.' Achado
    real 2026-09-04 (EDHREC: card mais jogado com o Megatron entre as
    enchantments, 41,6% dos decks -- validado por dado real de jogadores,
    nao so' por oraculo). Sempre escolhe devolver pra mao: vantagem de
    cartas > 3 de dano proxy aqui, ja que o deck reaproveita fartamente
    artefato reciclado (fuel do Megatron/fodder de solda de novo), e o
    combate ja alimenta `life_lost_by_opponents_this_turn` de sobra sem
    precisar desses 3 pontos extras. So' dispara pra artefato NAO-token
    (token deixa de existir ao mudar de zona pelas regras reais -- ver
    `is_token_name`)."""
    if "Pia's Revolution" not in state.battlefield or is_token_name(dying_name):
        return
    if dying_name not in state.graveyard:
        return
    state.graveyard.remove(dying_name)
    state.hand.append(dying_name)
    state.pia_revolution_returns_total += 1


def scrap_trawler_trigger(state: GameState, dying_name: str):
    """'Whenever this creature dies or another artifact you control is
    put into a graveyard from the battlefield, return to your hand
    target artifact card in your graveyard with lesser mana value.'"""
    if dying_name != "Scrap Trawler" and "Scrap Trawler" not in state.battlefield:
        return
    dying_mv = CARD_DB[dying_name].mv
    pool = [c for c in state.graveyard if c != dying_name and is_artifact_card(c) and CARD_DB[c].mv < dying_mv]
    if not pool:
        return
    best = max(pool, key=lambda n: CARD_DB[n].mv)
    state.graveyard.remove(best)
    state.hand.append(best)
    state.recursion_events_total += 1


def rakdos_muscle_trigger(state: GameState, dying_name: str):
    """'Whenever you sacrifice another creature, exile cards equal to its
    mana value from the top of target player's library. Until your next
    end step, you may play those cards, and mana of any type can be
    spent to cast those spells.' Alvo = minha propria biblioteca (premissa
    documentada: maximiza valor pra mim). Aproximado como impulso de
    compra direta -- mesma convencao ja usada nesta sessao pra efeitos de
    'exile and may play' (Sandstone Oracle, Portal to Phyrexia etc), ja
    que o arquivo nao rastreia uma 'mao exilada temporaria' separada em
    lugar nenhum."""
    mv = CARD_DB[dying_name].mv
    if mv <= 0:
        return
    draw_cards(state, mv)
    state.sacrifice_payoff_draws_total += mv


def death_trigger(state: GameState, dying_name: str):
    """Gatilhos reais de 'quando isso morre' que nao sao o Scrap Trawler
    nem o Rakdos (esses sao genericos, ja tratados em `sacrifice()`)."""
    if dying_name == "Triplicate Titan":
        # "When this creature dies, create a 3/3 colorless Golem artifact
        # creature token with flying, a ... with vigilance, and a ...
        # with trample." As 3 palavras-chave ficam 📊 estrutural -- sem
        # bloqueio real modelado pra ninguem no arquivo inteiro (nenhuma
        # criatura tem essa restricao), flying/vigilance/trample nao tem
        # efeito numerico possivel aqui; os 3 tokens continuam 3/3
        # identicos na pratica (mesma convencao de simplificacao de
        # copy-effects/tokens ja usada no arquivo inteiro).
        token_name = "Golem Token"
        if token_name not in CARD_DB:
            add(token_name, 0, "creature", {"artifact"}, power=3, toughness=3)
        for _ in range(3):
            creature_enters(state, token_name, from_hand=False, token=True)
        state.triplicate_titan_tokens_total += 3
    if dying_name in ("Myr Retriever", "Junk Diver"):
        pool = [c for c in state.graveyard if c != dying_name and is_artifact_card(c)]
        if pool:
            best = max(pool, key=lambda n: CARD_DB[n].mv)
            state.graveyard.remove(best)
            state.hand.append(best)
            state.recursion_events_total += 1


def best_weld_fodder(state: GameState, min_mv: int = 0):
    """Escolha de qual artefato sacrificar quando o objetivo e' 'trocar
    algo barato por algo melhor do cemiterio' (Goblin Welder/Trash for
    Treasure/Scrap Welder/Daretti/Metalwork Colossus). Prioriza SEMPRE
    uma criatura temporaria pendente de sacrificio no fim do turno
    (Sneak Attack/Feldon -- e' literalmente gratis, ela ia morrer de
    qualquer jeito); senao, o artefato de MENOR custo de mana disponivel
    (mantem os grandes em campo), excluindo o Megatron e o proprio
    Warstorm Surge/rocks continuos de valor alto."""
    for n in state.temp_creatures_pending_sacrifice:
        if n in state.battlefield and is_artifact_card(n):
            return n
    KEEP_ALWAYS = {COMMANDER, "Warstorm Surge", "Sneak Attack", "Daretti, Scrap Savant"}
    candidates = [n for n in state.battlefield
                  if n not in KEEP_ALWAYS and is_artifact_card(n) and CARD_DB[n].mv >= min_mv]
    if not candidates:
        return None
    candidates.sort(key=lambda n: CARD_DB[n].mv)
    return candidates[0]


def best_megatron_fuel(state: GameState):
    """Escolha de qual artefato o proprio Megatron sacrifica como fuel
    (Destructive Force: 'deals damage equal to the sacrificed artifact's
    mana value'). Achado real 2026-09-02 (revendo o log de goldfish real
    do usuario -- ele sacrificou o God-Pharaoh's Statue, MV 6, o maior
    artefato disponivel, maximizando o dano): `megatron_combat()` estava
    reaproveitando `best_weld_fodder()`, que faz o OPOSTO de proposito
    (pega o MENOR MV, pra sobrar os grandes em campo pra solda) --
    fazendo o Megatron sacrificar sempre o artefato MAIS FRACO como fuel,
    ao contrario da estrategia real do primer ("prioriza o artefato de
    MAIOR custo de mana"). Corrigido com selecao propria, descendente.
    Achado real 2026-09-15 (Crew do Demonic Junker): sem essa exclusao,
    Junker -- sendo o maior MV do campo -- era sacrificado como o
    PROPRIO fuel assim que crewado, perdendo o ataque que o crew tinha
    acabado de habilitar (desperdicia a criatura/token que tapou pra
    nada). So' o exclui enquanto estiver crewado ESSE turno -- depois do
    combate, ou se nunca foi crewado, continua candidato normal (um
    Vehicle usado so' pela removal ETB e' fuel valido depois)."""
    for n in state.temp_creatures_pending_sacrifice:
        if n in state.battlefield and is_artifact_card(n):
            return n
    KEEP_ALWAYS = {COMMANDER, "Warstorm Surge", "Sneak Attack", "Daretti, Scrap Savant"}
    if state.demonic_junker_crewed_this_turn:
        KEEP_ALWAYS = KEEP_ALWAYS | {"Demonic Junker"}
    candidates = [n for n in state.battlefield if n not in KEEP_ALWAYS and is_artifact_card(n)]
    if not candidates:
        return None
    candidates.sort(key=lambda n: -CARD_DB[n].mv)
    return candidates[0]


def best_payoff_fodder(state: GameState):
    """Fodder pros payoffs de sacrificio 'livres' (Ayara, Susur Secundi,
    Altar of the Wretched) -- so' consome criaturas temporarias que iam
    morrer de qualquer jeito no fim do turno (nunca sacrifica board real
    por esses payoffs; a decisao de trocar valor permanente por dano/
    vida/compra fica fora de escopo de uma heuristica de goldfish)."""
    for n in state.temp_creatures_pending_sacrifice:
        if n in state.battlefield:
            return n
    return None


CHEAP_WORTH_COPYING_TAGS = {"rock1", "rock2", "rock3", "melded_moxite"}
# Achado real 2026-09-15 (correcao do usuario): o oraculo do Ultron NAO
# tem restricao nenhuma de custo ("whenever ANOTHER nontoken artifact...
# pay {2}: copy" -- qualquer artefato serve). O corte de MV>=3 abaixo e'
# so' heuristica de VALOR (nao regra da carta) -- mas a versao anterior
# dessa heuristica errava justamente nos rocks de custo 2: copiar um
# rock nao e' "+1 mana uma vez" (rate ruim), e' +1 mana TODO turno daí
# em diante (rampa recorrente) MAIS um token descartavel de graca pro
# `Destructive Force` sacrificar depois (combustivel sem custo de carta
# real, so' os {2} da copia). Mesma logica vale pro Melded Moxite (MV 2,
# tag `melded_moxite`) -- dobrar o loot ETB dela e' bom mesmo barata.


def artifact_etb_hooks(state: GameState, name: str, token: bool = False):
    """Ultron, Artificial Malevolence: 'whenever another nontoken
    artifact you control enters, you may pay {2}. If you do, create a
    token that's a copy of it.' Escolhe pagar sempre que sobra mana e o
    artefato tem valor real de copia -- MV>=3 (corpo/efeito grande) OU
    esta' em `CHEAP_WORTH_COPYING_TAGS` (rock continuo/Melded Moxite,
    ver comentario acima). `token=True` (a propria entrada e' de um
    token, ex: copia do Ultron/Osgir/Feldon/Skitterbeam) precisa ficar
    de fora -- senao um token de MV alto copiando a si mesmo via Ultron
    entra em recursao infinita (achado real ao testar)."""
    if token or name == "Ultron, Artificial Malevolence" or "Ultron, Artificial Malevolence" not in state.battlefield:
        return
    cheap_worth_it = bool(CARD_DB[name].tags & CHEAP_WORTH_COPYING_TAGS)
    if CARD_DB[name].mv < 3 and not cheap_worth_it:
        return
    if remaining_mana(state) < 2:
        return
    if cheap_worth_it:
        state.ultron_cheap_copies_total += 1
    spend_mana(state, 2)
    token_name = make_token_copy_name(name)
    if is_creature_card(name):
        creature_enters(state, token_name, from_hand=False, token=True)
    else:
        state.battlefield.append(token_name)
        resolve_etb(state, token_name)
    state.recursion_events_total += 1


def make_token_copy_name(base_name: str) -> str:
    token_name = base_name + " (copia)"
    if token_name not in CARD_DB:
        CARD_DB[token_name] = CARD_DB[base_name]
    return token_name


TOKEN_FIXED_NAMES = {"Golem Token", "Shapeshifter Token",
                     "Myr Token", "Fish Token", "Robot Token"}
# Correcao 2026-09-09: "Myr Token" (Genesis Chamber) faltava aqui -- gap
# real, pia_revolution_trigger() teria disparado errado ('nontoken
# artifact') se um Myr Token artefato fosse sacrificado como fodder em
# qualquer lugar do arquivo. "Fish Token" (Fountainport) adicionado junto
# ja' na criacao, pra nao nascer com o mesmo gap.


def is_token_name(name: str) -> bool:
    """Distingue token de carta real -- necessario pro Pia's Revolution
    ('nontoken artifact'). Cobre os tokens-copia dinamicos
    (`make_token_copy_name`, sufixo ' (copia)'; `make_nexus_copy_name`,
    sufixo ' (Nexus)') e os tokens de nome fixo (Golem/Nexus Golem/
    Shapeshifter/Myr/Fish)."""
    return name.endswith(" (copia)") or name.endswith(" (Nexus)") or name in TOKEN_FIXED_NAMES


def resolve_etb(state: GameState, name: str, token: bool = False):
    tags = CARD_DB[name].tags

    if "goblin_engineer" in tags:
        # "When this creature enters, you may search your library for an
        # artifact card, put it into your graveyard, then shuffle."
        # Achado real 2026-09-13 (auditoria completa oraculo-por-oraculo):
        # a tag existia so' pra categorizacao, o ETB nunca foi despachado
        # -- fantasma real.
        # Achado real 2026-09-15 (usuario perguntou sobre tutor de
        # artefato por causa do Portal to Phyrexia): a versao anterior
        # so' priorizava MAIOR MV, sem preferir criatura -- testado e
        # confirmado que isso podia buscar o proprio Portal to Phyrexia
        # (MV9, NAO criatura) empatado com Triplicate Titan/Skitterbeam
        # (tambem MV9) e mandar ele pro cemiterio, onde fica inutil pra
        # alimentar tanto a propria recursao dele (`try_portal_phyrexia_
        # upkeep`, exige "creature card") quanto a do Scarecrone (exige
        # "artifact CREATURE card" tambem). Corrigido: prioriza artefato
        # CRIATURA primeiro, MV descendente como critério secundário --
        # so' busca um nao-criatura se nao houver nenhuma criatura-
        # artefato disponivel na biblioteca."""
        gy_targets = [c for c in state.library if is_artifact_card(c)]
        if gy_targets:
            target = max(gy_targets, key=lambda n: (is_creature_card(n), CARD_DB[n].mv))
            state.library.remove(target)
            state.graveyard.append(target)
            state.tutors_used_total += 1

    if "combustible_gearhulk" in tags:
        # "target opponent may have you draw three cards. If the player
        # doesn't, you mill three cards, then this deals damage = total MV
        # of those cards." Premissa: oponente NUNCA deixa eu comprar
        # (pior escolha pra ele), entao sempre milha e' dano real.
        milled = state.library[:3]
        state.library = state.library[3:]
        state.graveyard.extend(milled)
        dmg = sum(CARD_DB[c].mv for c in milled if c in CARD_DB)
        if dmg > 0:
            proxy_drain(state, dmg)

    if "noxious_gearhulk" in tags:
        # "may destroy another target creature. If a creature is
        # destroyed this way, you gain life equal to its toughness."
        # Achado real 2026-09-15 (auditoria comparativa pedida pelo
        # usuario): estava tratada como 📊 zero, mas essa e' remocao de
        # ALVO UNICO no oponente -- MESMA categoria de Path to
        # Exile/Swords to Plowshares/Generous Gift, ja creditadas como
        # interacao real (`interaction_spells_cast_total`). Inconsistente
        # deixar so' essa zerada. Ganho de vida usa proxy de 3 (media
        # aproximada de resistencia de criatura em Commander -- sem
        # resistencia real de oponente rastreada, mesma convencao de
        # aproximacao ja usada em outros efeitos "unknown opponent
        # stat" do arquivo).
        state.interaction_spells_cast_total += 1
        gain_life(state, 3)

    if "demonic_junker" in tags:
        # "When this Vehicle enters, for each player, destroy up to one
        # target creature that player controls. If a creature you
        # controlled was destroyed this way, put two +1/+1 counters on
        # this Vehicle." Achado real 2026-09-15 (usuario apontou: isso E'
        # removal real, "for each player" bate em CADA oponente, nao so'
        # no meu lado -- mesma convencao de "each opponent" ja usada em
        # todo o arquivo, NAO e' 📊 estrutural como Noxious Gearhulk
        # (aquele e' "another target creature", so' 1 alvo isolado, esse
        # aqui e' garantido por oponente). Nunca destruo minha propria
        # criatura por escolha (os contadores so' importam crewado, e o
        # usuario confirmou que nunca vai crewar -- ctype corrigido pra
        # "artifact" acima, Vehicle nao e' criatura por padrao).
        state.interaction_spells_cast_total += NUM_OPPONENTS
        state.demonic_junker_removals_total += NUM_OPPONENTS

    if "skitterbeam" in tags and not token:
        # "When this creature enters, if you cast it [pelo custo cheio,
        # nao Prototype], create two tokens that are copies of it." O "if
        # you cast it" e' real e importante: um TOKEN copia de Skitterbeam
        # (por Mirrorworks/Osgir/Feldon/etc) nao foi CONJURADO, entao nao
        # dispara de novo -- sem o `and not token` aqui, um token copiando
        # a si mesmo entra em recursao infinita (achado real ao testar,
        # Ultron/Osgir/Feldon incluidos).
        # Premissa: sempre conjurado pelo custo cheio ({9}), nunca a
        # versao Prototype barata ({3}{R}{R}, 2/2) -- mesma convencao de
        # 'escolhe sempre a linha de maior valor' ja usada pro Boros
        # Charm/etc no arquivo anterior.
        # Achado real 2026-09-13 (auditoria completa): tokens sao copias
        # de Skitterbeam Battalion, que TEM "Trample, haste" real -- sem
        # marcar `creature_cast_turn` no turno anterior, os tokens
        # ficavam com doenca de invocacao e nao atacavam no turno que
        # entravam, fantasma parcial na propria mecanica ja existente.
        for _ in range(2):
            token_name = make_token_copy_name(name)
            creature_enters(state, token_name, from_hand=False, token=True)
            state.creature_cast_turn[token_name] = state.turn - 1

    if "saga_bahamut" in tags:
        state.bahamut_entered_turn = state.turn
        state.bahamut_chapter = 1
        # Capitulo I: destroy up to one target nonland permanent -- sem
        # alvo real de oponente, conta como interacao (mesma convencao).
        # Capitulos II/III/IV disparam em `try_bahamut_saga_tick`, um por
        # turno apos o draw step -- achado real 2026-09-13 (auditoria
        # completa): so' o capitulo I (ETB) tinha dispatch, os campos
        # `bahamut_entered_turn`/`bahamut_chapter` eram setados mas nunca
        # lidos de novo -- a saga nunca avancava, fantasma real (perdia o
        # Mega Flare do capitulo IV, o maior payoff da carta).
        state.interaction_spells_cast_total += 1

    if "portal_phyrexia" in tags:
        # ETB: "each opponent sacrifices three creatures of their
        # choice" -- sem board real de oponente, conta como valor de
        # bordo destruido (recursion_events, nao dano numerico, mesma
        # convencao ja usada nesta sessao). A 2a habilidade real da
        # carta (reanimacao repetivel todo upkeep) fica em
        # `try_portal_phyrexia_upkeep`, achado real 2026-09-13.
        state.recursion_events_total += 1

    if "cursed_mirror_clone" in tags:
        # "As this artifact enters, you may have it become a copy of ANY
        # creature on the battlefield until end of turn, except it has
        # haste" (Scryfall, confirmado 2026-09-18) -- nao restrito ao
        # comandante. Achado real 2026-09-18 (goldfish manual do usuario:
        # copiou o Cityscape Leveler, 8/8, em vez do Megatron): a versao
        # anterior sempre copiava o Megatron especificamente ("unica
        # criatura que ataca de verdade"), premissa que ficou desatualizada
        # desde que `all_attackers_combat` passou a fazer TODO MUNDO atacar
        # (achado 2026-09-02, ver docstring de anrakyr_attack_ability).
        #
        # Correcao 2 (mesma rodada, usuario apontou): copiar uma criatura
        # LENDARIA e' literalmente pior que inutil, nao so' "subotimo" --
        # CR 704.5j (regra de lendario): eu ja controlo o original de
        # qualquer lendaria minha (Megatron/Anrakyr/Ayara/etc), entao a
        # copia entra e e' IMEDIATAMENTE sacrificada (escolho manter o
        # original) antes de sequer poder atacar. `LEGENDARY_NAMES`
        # exclui essas do pool -- so' criaturas NAO-lendarias (Triplicate
        # Titan 9/9, Blightsteel Colossus 11/11, Cityscape Leveler 8/8
        # trample + destroi ao atacar, tokens, etc) sao alvos legais de
        # verdade. Copia a de MAIOR poder real (get_power, cobre CDAs/
        # boosts) entre essas -- haste vem do proprio efeito, nao exige
        # `ready_creatures`.
        creatures_in_play = [n for n in state.battlefield
                              if is_creature_card(n) and not is_legendary(n)]
        if creatures_in_play:
            best = max(creatures_in_play, key=lambda n: get_power(state, n))
            power = get_power(state, best)
            if power > 0:
                proxy_drain(state, power)

    if "tunnel_grinder" in tags:
        # "discard any number of cards, then draw that many plus one."
        # Premissa: descarta 0 (mantem a mao), compra so' o +1 garantido
        # -- sem avaliacao real de quais cartas valem descartar.
        draw_cards(state, 1)

    if "cityscape_leveler" in tags:
        # "When you cast this spell..., destroy up to one target
        # nonland permanent." Credita como interacao no ETB (mesma
        # convencao de Path/Swords/Vandalblast/Generous Gift). A
        # clausula "its controller creates a tapped Powerstone token"
        # e' ganho do OPONENTE -- fora do modelo, so' rastreamos nosso
        # proprio lado. O gatilho de ATAQUE ("whenever this creature
        # attacks...") fica em `all_attackers_combat`.
        state.interaction_spells_cast_total += 1

    if "melded_moxite" in tags:
        # "When this artifact enters, you may discard a card. If you do,
        # draw two cards." Achado real 2026-09-15 (troca por Demand
        # Answers): sempre descarta se houver carta na mao pra descartar
        # (a propria Moxite ja' foi removida da mao antes desse ETB
        # resolver, mesma convencao de todo o arquivo) -- +1 carta
        # liquida garantida, mesma logica do worst_discard_target usado
        # em todo loot do arquivo. Refoga tambem numa copia via Ultron
        # (make_token_copy_name preserva a tag, resolve_etb dispara de
        # novo pro token -- dobra o loot de verdade).
        if state.hand:
            worst = worst_discard_target(state)
            state.hand.remove(worst)
            state.graveyard.append(worst)
            draw_cards(state, 2)
            state.melded_moxite_loots_total += 1

    if "daretti_rocketeer" in tags:
        # "Whenever Daretti enters or attacks, choose target artifact
        # card in your graveyard. You may sacrifice an artifact. If you
        # do, return the chosen card to the battlefield." Metade de ETB
        # -- achado real 2026-09-02 (reauditoria pos-jogo real do
        # usuario): nunca tinha dispatch nenhum, nem essa nem a de
        # ataque (`daretti_rocketeer_attack_ability`, chamada em
        # `all_attackers_combat`).
        daretti_rocketeer_attack_ability(state)


# ---------------------------------------------------------------------------
# Solda / recuperacao de artefato
# ---------------------------------------------------------------------------

def try_goblin_welder(state: GameState):
    """'{T}: Choose target artifact a player controls and target artifact
    card in that player's graveyard. If both targets are still legal,
    that player simultaneously sacrifices the artifact and returns the
    artifact card to the battlefield.' So' faz sentido quando o artefato
    no cemiterio vale mais que o sacrificado -- so' ativa se achar um
    upgrade real (MV do alvo do cemiterio > MV do fodder)."""
    if "Goblin Welder" not in state.battlefield or "Goblin Welder" not in ready_creatures(state):
        return
    if state.goblin_welder_used_this_turn:
        return
    fodder = best_weld_fodder(state)
    if fodder is None:
        return
    gy_artifacts = [c for c in state.graveyard if is_artifact_card(c) and CARD_DB[c].mv > CARD_DB[fodder].mv]
    if not gy_artifacts:
        return
    target = max(gy_artifacts, key=lambda n: CARD_DB[n].mv)
    state.goblin_welder_used_this_turn = True
    sacrifice(state, fodder)
    if target not in state.graveyard:
        return  # o proprio sacrificio (ex: morte do toolbox) ja consumiu o alvo
    state.graveyard.remove(target)
    if is_creature_card(target):
        creature_enters(state, target, from_hand=False)
    else:
        state.battlefield.append(target)
        resolve_etb(state, target)
    state.weld_activations_total += 1


def try_scrap_welder(state: GameState):
    """'{T}, Sacrifice an artifact with mana value X: Return target
    artifact card with mana value less than X from your graveyard to the
    battlefield. It gains haste until end of turn.' Volta PERMANENTE
    (nao e' sacrificada de novo no fim do turno -- so' ganha haste)."""
    if "Scrap Welder" not in state.battlefield or "Scrap Welder" not in ready_creatures(state):
        return
    if state.scrap_welder_used_this_turn:
        return
    fodder = best_weld_fodder(state)
    if fodder is None:
        return
    gy_artifacts = [c for c in state.graveyard if is_artifact_card(c) and CARD_DB[c].mv < CARD_DB[fodder].mv]
    if not gy_artifacts:
        return
    target = max(gy_artifacts, key=lambda n: CARD_DB[n].mv)
    state.scrap_welder_used_this_turn = True
    sacrifice(state, fodder)
    if target not in state.graveyard:
        return
    state.graveyard.remove(target)
    if is_creature_card(target):
        creature_enters(state, target, from_hand=False)
        state.creature_cast_turn[target] = state.turn - 1  # haste: pronta ja'
    else:
        state.battlefield.append(target)
        resolve_etb(state, target)
    state.weld_activations_total += 1


def try_trash_for_treasure(state: GameState):
    """'As an additional cost to cast this spell, sacrifice an artifact.
    Return target artifact card from your graveyard to the battlefield.'
    Sorcery, sem limite de 1x/turno alem de estar na mao e' castavel."""
    if "Trash for Treasure" not in state.hand or not can_cast(state, "Trash for Treasure"):
        return
    fodder = best_weld_fodder(state)
    if fodder is None:
        return
    gy_artifacts = [c for c in state.graveyard if is_artifact_card(c) and c != fodder]
    if not gy_artifacts:
        return
    target = max(gy_artifacts, key=lambda n: CARD_DB[n].mv)
    if CARD_DB[target].mv <= CARD_DB[fodder].mv:
        return  # so' vale a pena se for upgrade real
    spend_mana(state, effective_cost(state, "Trash for Treasure"))
    state.hand.remove("Trash for Treasure")
    state.graveyard.append("Trash for Treasure")
    sacrifice(state, fodder)
    if target not in state.graveyard:
        return
    state.graveyard.remove(target)
    if is_creature_card(target):
        creature_enters(state, target, from_hand=False)
    else:
        state.battlefield.append(target)
        resolve_etb(state, target)
    state.weld_activations_total += 1


def try_chandras_ignition(state: GameState):
    """Chandra's Ignition: 'Target creature you control deals damage
    equal to its power to each other creature and each opponent.'
    Achado real 2026-09-15 (usuario apontou que e' um finalizador
    condicional, nao um wrath incondicional -- ver
    `CHANDRAS_IGNITION_LETHAL_THRESHOLD`): so' conjura quando ja' saiu
    dano proxy suficiente pra supor os oponentes numa faixa de queima
    letal. "Each opponent" bate em todos (x NUM_OPPONENTS, mesma
    convencao do arquivo); "each OTHER creature" mata minhas proprias
    tambem -- processado via `sacrifice()` pra disparar os gatilhos
    reais de morte (Scrap Trawler/Pia's Revolution/Rakdos/Triplicate
    Titan etc), nao um efeito silencioso.

    Achado real 2026-09-17 (usuario): com BlightSteel Colossus (Infect)
    em campo, o alvo real deixa de ser o Megatron -- Infect faz QUALQUER
    dano dessa fonte (incluindo o desta habilidade) ser marcado como
    veneno nos oponentes em vez de perda de vida, e 11 de poder ja'
    excede sozinho o teto real de derrota por veneno (`POISON_LETHAL`
    = 10). Isso e' um auto-win determinístico, independente de quanto
    dano proxy ja' saiu -- NUNCA passa pelo `CHANDRAS_IGNITION_LETHAL_
    THRESHOLD` (esse threshold e' so' a heuristica de "os oponentes
    devem estar baixos de vida", irrelevante pra veneno). Nao precisa
    de `ready_creatures` -- "target creature you control" nao exige
    ausencia de doenca de invocacao pra ser alvo legal de um spell
    (so' pra atacar/usar habilidade com {T})."""
    if "Chandra's Ignition" not in state.hand or not can_cast(state, "Chandra's Ignition"):
        return
    infect_source = None
    if "Blightsteel Colossus" in state.battlefield:
        p = get_power(state, "Blightsteel Colossus")
        if p >= POISON_LETHAL:
            infect_source = "Blightsteel Colossus"
    if infect_source is None:
        if state.proxy_damage_total < CHANDRAS_IGNITION_LETHAL_THRESHOLD:
            return
        if COMMANDER not in state.battlefield or COMMANDER not in ready_creatures(state):
            return
        source = COMMANDER
    else:
        source = infect_source
    power = get_power(state, source)
    if power <= 0:
        return
    spend_mana(state, effective_cost(state, "Chandra's Ignition"))
    state.hand.remove("Chandra's Ignition")
    state.graveyard.append("Chandra's Ignition")
    others = [n for n in state.battlefield if is_creature_card(n) and n != source]
    for n in others:
        if CARD_DB[n].toughness <= power:
            sacrifice(state, n)
            state.chandras_ignition_own_creatures_lost_total += 1
    if infect_source is not None:
        state.blightsteel_poison_win = True
        state.chandras_ignition_infect_kills_total += 1
    else:
        proxy_drain(state, power * NUM_OPPONENTS)
    state.chandras_ignition_casts_total += 1


def try_metalwork_colossus_recursion(state: GameState):
    """'Sacrifice two artifacts: Return this card from your graveyard to
    your hand.' Confirma 2 candidatos ANTES de sacrificar (evita o caso
    do primeiro sacrificio consumir o unico candidato disponivel)."""
    if "Metalwork Colossus" not in state.graveyard:
        return
    KEEP_ALWAYS = {COMMANDER, "Warstorm Surge", "Sneak Attack", "Daretti, Scrap Savant"}
    candidates = sorted(
        [n for n in state.battlefield if n not in KEEP_ALWAYS and is_artifact_card(n)],
        key=lambda n: CARD_DB[n].mv,
    )
    if len(candidates) < 2:
        return
    sacrifice(state, candidates[0])
    sacrifice(state, candidates[1])
    if "Metalwork Colossus" not in state.graveyard:
        return  # um dos sacrificios (ex: morte do toolbox) ja devolveu ela pra mao
    state.graveyard.remove("Metalwork Colossus")
    state.hand.append("Metalwork Colossus")
    state.recursion_events_total += 1


def try_scarecrone(state: GameState):
    """Scarecrone: '{4}, {T}: Return target artifact creature card from
    your graveyard to the battlefield.' Sempre pega a criatura-artefato
    de maior MV disponivel no cemiterio. So' 1 ativacao por turno (tap
    real). A outra habilidade ('{1}, Sacrifice a Scarecrow: Draw a
    card' -- so' ela mesma, unico Scarecrow do deck) fica fora do
    modelo: sacrificar um motor de recursao repetivel por 1 carta avulsa
    raramente e' a jogada certa pra uma heuristica simples (mesma
    convencao de simplificacao do lado 'transformar' do Tarrian's
    Journal)."""
    if "Scarecrone" not in state.battlefield or "Scarecrone" not in ready_creatures(state):
        return
    if state.scarecrone_used_this_turn or remaining_mana(state) < 4:
        return
    candidates = [c for c in state.graveyard if is_artifact_card(c) and is_creature_card(c)]
    if not candidates:
        return
    best = max(candidates, key=lambda n: CARD_DB[n].mv)
    state.scarecrone_used_this_turn = True
    spend_mana(state, 4)
    state.graveyard.remove(best)
    creature_enters(state, best, from_hand=False)
    state.recursion_events_total += 1


def try_mind_stone_sac(state: GameState):
    """Mind Stone: '{1}, {T}, Sacrifice this artifact: Draw a card.'
    Achado real 2026-09-13 (auditoria completa oraculo-por-oraculo): a
    tag `fuel_rock1` existia mas nunca era despachada em lugar nenhum --
    fantasma real. So' vale a pena trocar rampa permanente por 1 carta
    quando ja' sobra bastante mana de outras fontes (nunca sacrifica a
    unica rampa disponivel)."""
    if "Mind Stone" not in state.battlefield:
        return
    if remaining_mana(state) < 1 or total_mana(state) < 7:
        return
    spend_mana(state, 1)
    sacrifice(state, "Mind Stone")
    draw_cards(state, 1)


def try_melded_moxite_sac(state: GameState):
    """Melded Moxite: '{3}, Sacrifice this artifact: Create a tapped 2/2
    colorless Robot artifact creature token.' Mana sink de fim de main
    phase -- so' quando sobra mana de verdade e nao ha mais nada pra
    fazer com ela (chamada por ultimo, mesmo padrao do Mind Stone acima).
    O proprio sacrificio (nao-token) dispara Pia's Revolution, e a
    entrada do token (criatura) dispara Warstorm Surge de novo -- ambos
    genericos via `sacrifice()`/`creature_enters()`, sem codigo extra
    aqui."""
    if "Melded Moxite" not in state.battlefield or remaining_mana(state) < 3:
        return
    spend_mana(state, 3)
    sacrifice(state, "Melded Moxite")
    token_name = "Robot Token"
    if token_name not in CARD_DB:
        add(token_name, 0, "creature", {"artifact"}, power=2, toughness=2)
    creature_enters(state, token_name, from_hand=False, token=True)
    state.melded_moxite_tokens_total += 1


def try_goblin_engineer_activation(state: GameState):
    """'{R}, {T}, Sacrifice an artifact: Return target artifact card with
    mana value 3 or less from your graveyard to the battlefield.'"""
    if "Goblin Engineer" not in state.battlefield or "Goblin Engineer" not in ready_creatures(state):
        return
    if state.goblin_engineer_used_this_turn or remaining_mana(state) < 1:
        return
    fodder = best_weld_fodder(state)
    if fodder is None:
        return
    gy_artifacts = [c for c in state.graveyard if is_artifact_card(c) and c != fodder and CARD_DB[c].mv <= 3]
    if not gy_artifacts:
        return
    target = max(gy_artifacts, key=lambda n: CARD_DB[n].mv)
    if CARD_DB[target].mv <= CARD_DB[fodder].mv:
        return
    state.goblin_engineer_used_this_turn = True
    spend_mana(state, 1)
    sacrifice(state, fodder)
    if target not in state.graveyard:
        return
    state.graveyard.remove(target)
    if is_creature_card(target):
        creature_enters(state, target, from_hand=False)
    else:
        state.battlefield.append(target)
        resolve_etb(state, target)
    state.weld_activations_total += 1


def try_mishra_unearth(state: GameState):
    """'Each artifact card in your graveyard has unearth {1}{B}{R}.'
    Unearth: {1}{B}{R}, return da GY pro campo, ganha haste, exilada no
    fim do turno (ou se sair do campo). So' unearth-a a maior MV
    disponivel, uma vez por turno (limite real de mana pratico)."""
    if "Mishra, Tamer of Mak Fawa" not in state.battlefield:
        return
    if state.mishra_unearth_used_this_turn or remaining_mana(state) < 3:
        return
    gy_artifacts = [c for c in state.graveyard if is_artifact_card(c)]
    if not gy_artifacts:
        return
    target = max(gy_artifacts, key=lambda n: CARD_DB[n].mv)
    state.mishra_unearth_used_this_turn = True
    spend_mana(state, 3)
    state.graveyard.remove(target)
    if is_creature_card(target):
        creature_enters(state, target, from_hand=False)
        state.creature_cast_turn[target] = state.turn - 1  # haste
    else:
        state.battlefield.append(target)
        resolve_etb(state, target)
    state.temp_creatures_pending_exile.append(target)
    state.recursion_events_total += 1


def try_osgir_activation(state: GameState):
    """Osgir, the Reconstructor: '{X}, {T}, Exile an artifact card with
    mana value X from your graveyard: Create two tokens that are copies
    of the exiled card. Activate only as a sorcery.'"""
    if "Osgir, the Reconstructor" not in state.battlefield or "Osgir, the Reconstructor" not in ready_creatures(state):
        return
    if state.osgir_used_this_turn:
        return
    gy_artifacts = [c for c in state.graveyard if is_artifact_card(c)]
    affordable = [c for c in gy_artifacts if CARD_DB[c].mv <= remaining_mana(state)]
    if not affordable:
        return
    target = max(affordable, key=lambda n: CARD_DB[n].mv)
    state.osgir_used_this_turn = True
    spend_mana(state, CARD_DB[target].mv)
    state.graveyard.remove(target)
    state.exile.append(target)
    for _ in range(2):
        token_name = make_token_copy_name(target)
        if is_creature_card(target):
            creature_enters(state, token_name, from_hand=False, token=True)
        else:
            state.battlefield.append(token_name)
            resolve_etb(state, token_name)
    state.recursion_events_total += 1


def try_osgir_pump(state: GameState):
    """Osgir, the Reconstructor: '{1}, Sacrifice an artifact: Target
    creature you control gets +2/+0 until end of turn.' Achado real
    2026-09-13 (auditoria completa): so' a habilidade principal de
    clonagem estava implementada. Sem 'activate only once' no oraculo,
    mas limitada a 1x por turno aqui pra nao canibalizar fodder que
    outros efeitos (Welder/Scrap Welder/Daretti) usam melhor -- so' ativa
    depois de todos eles ja terem rodado nesse main_phase."""
    if "Osgir, the Reconstructor" not in state.battlefield or remaining_mana(state) < 1:
        return
    target = next((n for n in ready_creatures(state) if n != COMMANDER), None)
    if target is None:
        return
    fodder = best_weld_fodder(state)
    if fodder is None:
        return
    spend_mana(state, 1)
    sacrifice(state, fodder)
    state.temp_power_boost[target] = state.temp_power_boost.get(target, 0) + 2


# ---------------------------------------------------------------------------
# Cheat pra campo (temporario) + sacrificio-payoff
# ---------------------------------------------------------------------------

def try_feldon(state: GameState):
    """'{2}{R}, {T}: Create a token that's a copy of target creature card
    in your graveyard, except it's an artifact in addition to its other
    types. It gains haste. Sacrifice it at the beginning of the next end
    step.' Escolhe a maior MV disponivel no cemiterio."""
    if "Feldon of the Third Path" not in state.battlefield or "Feldon of the Third Path" not in ready_creatures(state):
        return
    if state.feldon_used_this_turn or remaining_mana(state) < 3:
        return
    creatures_in_gy = [c for c in state.graveyard if is_creature_card(c)]
    if not creatures_in_gy:
        return
    target = max(creatures_in_gy, key=lambda n: CARD_DB[n].mv)
    state.feldon_used_this_turn = True
    spend_mana(state, 3)
    token_name = make_token_copy_name(target)
    creature_enters(state, token_name, from_hand=False, token=True)
    state.creature_cast_turn[token_name] = state.turn - 1  # haste
    state.temp_creatures_pending_sacrifice.append(token_name)
    state.creatures_cheated_in_total += 1


def try_sneak_attack(state: GameState):
    """'{R}: You may put a creature card from your hand onto the
    battlefield. That creature gains haste. Sacrifice the creature at the
    beginning of the next end step.' Sem limite de ativacoes/turno no
    oraculo -- ativa repetidamente enquanto houver mana E criatura na
    mao, priorizando a de maior poder (maximiza Warstorm Surge + dano de
    combate do proprio Anrakyr, se for ele)."""
    if "Sneak Attack" not in state.battlefield:
        return
    guard = 0
    while remaining_mana(state) >= 1 and guard < 6:
        guard += 1
        creatures_in_hand = [c for c in state.hand if is_creature_card(c) and c != COMMANDER]
        if not creatures_in_hand:
            return
        target = max(creatures_in_hand, key=lambda n: get_power(state, n))
        spend_mana(state, 1)
        creature_enters(state, target, from_hand=True)
        state.creature_cast_turn[target] = state.turn - 1  # haste
        state.temp_creatures_pending_sacrifice.append(target)
        state.creatures_cheated_in_total += 1


def try_ayara(state: GameState):
    """Ayara, Widow of the Realm: '{T}, Sacrifice another creature or
    artifact: Ayara deals X damage to target opponent and you gain X
    life, where X is the sacrificed permanent's mana value.' So' consome
    fodder que ia morrer de qualquer jeito (`best_payoff_fodder`) -- nunca
    sacrifica board real por essa ativada (ver docstring da funcao)."""
    if "Ayara, Widow of the Realm" not in state.battlefield or state.ayara_transformed:
        return
    if "Ayara, Widow of the Realm" not in ready_creatures(state):
        return
    if state.ayara_recur_used_this_turn:
        return
    fodder = best_payoff_fodder(state)
    if fodder is None:
        return
    mv = CARD_DB[fodder].mv
    if mv <= 0:
        return
    state.ayara_recur_used_this_turn = True
    sacrifice(state, fodder)
    proxy_drain(state, mv)
    gain_life(state, mv)
    state.sacrifice_payoff_damage_total += mv


def try_ayara_flip_reanimate(state: GameState):
    """Ayara, Furnace Queen (verso, apos transformar): 'At the beginning
    of combat on your turn, return up to one target artifact or creature
    card from your graveyard to the battlefield. It gains haste. Exile it
    at the beginning of the next end step.'"""
    if not state.ayara_transformed:
        return
    candidates = [c for c in state.graveyard if is_creature_card(c) or is_artifact_card(c)]
    if not candidates:
        return
    target = max(candidates, key=lambda n: CARD_DB[n].mv)
    state.graveyard.remove(target)
    if is_creature_card(target):
        creature_enters(state, target, from_hand=False)
        state.creature_cast_turn[target] = state.turn - 1
    else:
        state.battlefield.append(target)
        resolve_etb(state, target)
    state.temp_creatures_pending_exile.append(target)
    state.recursion_events_total += 1


def try_ayara_transform(state: GameState):
    """'{5}{R/P}: Transform Ayara. Activate only as a sorcery.' Paga com
    mana real (nunca vida, {R/P} tratado como {R} aqui -- premissa
    documentada: vida e' recurso mais valioso que 1 mana extra)."""
    if "Ayara, Widow of the Realm" not in state.battlefield or state.ayara_transformed:
        return
    if remaining_mana(state) < 6 or color_sources(state, "R") < 1:
        return
    spend_mana(state, 6)
    state.ayara_transformed = True


def try_susur_secundi(state: GameState):
    """'12+ | {1}{B}, {T}, Pay 2 life, Sacrifice a creature: Draw cards
    equal to the sacrificed creature's power.' So' liga com 12+ contadores
    de carga (station) -- ver `try_station_lands`."""
    if "Susur Secundi, Void Altar" not in state.battlefield:
        return
    if state.charge_counters.get("Susur Secundi, Void Altar", 0) < 12:
        return
    if state.susur_secundi_used_this_turn or remaining_mana(state) < 1 or state.life <= 2:
        return
    fodder = best_payoff_fodder(state)
    if fodder is None or not is_creature_card(fodder):
        return
    power = get_power(state, fodder)
    if power <= 0:
        return
    state.susur_secundi_used_this_turn = True
    spend_mana(state, 1)
    self_damage(state, 2)
    sacrifice(state, fodder)
    draw_cards(state, power)
    state.sacrifice_payoff_draws_total += power


def try_fountainport(state: GameState):
    """Fountainport: '{T}: Add {C}.' terreno generico normal, ja contado
    no total_mana() agregado como qualquer outro terreno (produces=set()
    porque {C} nao fixa W/B/R). As 3 habilidades abaixo competem pelo
    MESMO tap (cada uma tem seu proprio '{T}' no oraculo real), entao so'
    1 por turno; todo custo de mana e' 100% generico -- o mana incolor do
    Megatron paga qualquer uma (achado real do usuario 2026-09-09).
    Prioriza draw (sacrifica um token disponivel) > Fish token > Treasure,
    na ordem de valor real pro deck:
    {2}, {T}, Sacrifice a token: Draw a card.
    {3}, {T}, Pay 1 life: Create a 1/1 blue Fish creature token.
    {4}, {T}: Create a Treasure token."""
    if "Fountainport" not in state.battlefield or state.fountainport_used_this_turn:
        return
    tokens = [n for n in state.battlefield if is_token_name(n)]
    if tokens and remaining_mana(state) >= 2:
        state.fountainport_used_this_turn = True
        spend_mana(state, 2)
        sacrifice(state, tokens[0])
        draw_cards(state, 1)
        state.fountainport_draws_total += 1
    elif remaining_mana(state) >= 3 and state.life > 3:
        state.fountainport_used_this_turn = True
        spend_mana(state, 3)
        self_damage(state, 1)
        if "Fish Token" not in CARD_DB:
            add("Fish Token", 0, "creature", set(), power=1, toughness=1)
        creature_enters(state, "Fish Token", from_hand=False, token=True)
        state.fountainport_tokens_total += 1
    elif remaining_mana(state) >= 4:
        state.fountainport_used_this_turn = True
        spend_mana(state, 4)
        state.bonus_mana_pool += 1  # Treasure: convencao ja usada pelo Black Market Connections


def try_tarrians_journal(state: GameState):
    """Tarrian's Journal: '{T}, Sacrifice another artifact or creature:
    Draw a card. Activate only as a sorcery.' Sem custo de mana, so' tap
    + sacrificio -- prioriza SEMPRE sacrificar um token disponivel (Myr
    do Genesis Chamber, Fish do Fountainport, Shapeshifter do Black Market, etc; achado
    do usuario 2026-09-09: 'sacrifica Myr, fish token e qq criatura ou
    artefato pra gerar draw'), ja que sacrificar carta real seria so'
    troca 1-por-1 sem ganho liquido. So' 1 ativacao por turno (tap real).
    O verso '{2}, {T}, Discard your hand: Transform Tarrian's Journal' /
    'The Tomb of Aclazotz' (land, {T}: Add {B}. / reanima criatura do
    cemiterio) fica FORA -- custo de descartar a mao inteira e'
    proibitivo pra qualquer heuristica simples de IA, nunca seria a
    jogada certa no automatico (simplificacao documentada, mesma
    convencao do arquivo inteiro: nunca ghost silencioso)."""
    if "Tarrian's Journal" not in state.battlefield or state.tarrians_journal_used_this_turn:
        return
    tokens = [n for n in state.battlefield if is_token_name(n)]
    if not tokens:
        return
    state.tarrians_journal_used_this_turn = True
    sacrifice(state, tokens[0])
    draw_cards(state, 1)
    state.tarrians_journal_draws_total += 1


def try_station_lands(state: GameState):
    """Station (Susur Secundi, Void Altar / The Eternity Elevator): 'Tap
    another creature you control: Put charge counters equal to its power
    on this [Planet/Spacecraft]. Station only as a sorcery.' Estaciona
    com a MAIOR criatura pronta disponivel que nao seja essencial pro
    combate desse turno (nunca o Megatron -- ele precisa atacar)."""
    for land_name in ("Susur Secundi, Void Altar", "The Eternity Elevator"):
        if land_name not in state.battlefield:
            continue
        candidates = [n for n in ready_creatures(state) if n != COMMANDER and get_power(state, n) > 0]
        if not candidates:
            continue
        best = max(candidates, key=lambda n: get_power(state, n))
        state.charge_counters[land_name] = state.charge_counters.get(land_name, 0) + get_power(state, best)
        state.creature_cast_turn[best] = state.turn  # simplificacao: "tapped" ~ nao ataca esse turno


# ---------------------------------------------------------------------------
# Daretti (planeswalker + criatura), Megatron, Anrakyr, Ironsoul
# ---------------------------------------------------------------------------

DARETTI_SAVANT_STARTING_LOYALTY = 5


def try_daretti_savant(state: GameState):
    """Daretti, Scrap Savant: +2 discard-ate-2/draw-mesmo-numero; -2
    sacrifica artefato, devolve outro do cemiterio pro campo; -10
    emblema ('whenever an artifact is put into your graveyard from the
    battlefield, return it at the beginning of the next end step' --
    tratado como flag permanente que faz TODO artefato que morre voltar
    automaticamente). Prioriza -2 quando ha' upgrade real disponivel
    (motor principal do deck), senao +2 pra filtrar e chegar no -10."""
    if "Daretti, Scrap Savant" not in state.battlefield:
        return
    if state.daretti_savant_ultimate_active:
        return
    fodder = best_weld_fodder(state)
    gy_upgrade = None
    if fodder is not None:
        gy_artifacts = [c for c in state.graveyard if is_artifact_card(c) and CARD_DB[c].mv > CARD_DB[fodder].mv]
        if gy_artifacts:
            gy_upgrade = max(gy_artifacts, key=lambda n: CARD_DB[n].mv)
    if gy_upgrade is not None and state.daretti_savant_loyalty >= 2:
        state.daretti_savant_loyalty -= 2
        sacrifice(state, fodder)
        if gy_upgrade not in state.graveyard:
            return
        state.graveyard.remove(gy_upgrade)
        if is_creature_card(gy_upgrade):
            creature_enters(state, gy_upgrade, from_hand=False)
        else:
            state.battlefield.append(gy_upgrade)
            resolve_etb(state, gy_upgrade)
        state.weld_activations_total += 1
    elif state.daretti_savant_loyalty >= 10:
        state.daretti_savant_loyalty = 0
        state.daretti_savant_ultimate_active = True
    else:
        discard_n = min(2, len(state.hand))
        for c in state.hand[:discard_n]:
            state.hand.remove(c)
            state.graveyard.append(c)
        draw_cards(state, discard_n)
        state.daretti_savant_loyalty += 2


def daretti_ultimate_recursion_check(state: GameState, dying_artifact_name: str):
    """Emblema do -10: 'whenever an artifact is put into your graveyard
    from the battlefield, return that card to the battlefield at the
    beginning of the next end step.' Fila propria (`daretti_emblem_
    pending_return`), processada no fim do turno em `end_step` -- nao
    reaproveita a fila de exilio (semantica oposta: essa VOLTA pro
    campo, nao sai dele)."""
    if state.daretti_savant_ultimate_active and dying_artifact_name in state.graveyard:
        state.daretti_emblem_pending_return.append(dying_artifact_name)


def anrakyr_attack_ability(state: GameState):
    """'Whenever Anrakyr the Traveller attacks, you may cast an artifact
    spell from your hand or graveyard by paying life equal to its mana
    value rather than paying its mana cost.' O dano de combate dele em si
    ja' e' contado por `all_attackers_combat` (achado real do usuario
    jogando 2026-09-02: TODO mundo ataca agora, nao so' Megatron/Anrakyr
    -- ver essa funcao pra a mudanca completa) -- aqui so' o efeito extra
    exclusivo de Anrakyr, disparado de dentro do loop generico quando ele
    e' quem esta' atacando."""
    pool = [c for c in (state.hand + state.graveyard) if is_artifact_card(c) and c != COMMANDER]
    if not pool:
        return
    affordable = [c for c in pool if CARD_DB[c].mv < state.life]
    if not affordable:
        return
    target = max(affordable, key=lambda n: CARD_DB[n].mv)
    life_cost = CARD_DB[target].mv
    if life_cost <= 0:
        return
    self_damage(state, life_cost)
    if target in state.hand:
        state.hand.remove(target)
    else:
        state.graveyard.remove(target)
    if is_creature_card(target):
        creature_enters(state, target, from_hand=False)
    else:
        state.battlefield.append(target)
        resolve_etb(state, target)
    state.creatures_cheated_in_total += 1


def ironsoul_reanimate(state: GameState):
    """Corpo real do gatilho do Ironsoul Enforcer ('return target artifact
    card from your graveyard to the battlefield'), fatorado numa funcao
    separada pra poder ser chamado tanto pelo caso organico (poucas
    criaturas prontas por acaso, ver `ironsoul_enforcer_trigger`) quanto
    pelo caso deliberado (Megatron ataca sozinho de proposito, ver
    `try_megatron_alone_with_ironsoul`) -- nesse 2o caso precisa disparar
    ANTES do gatilho de ataque do Megatron, pra' o artefato recem-
    reanimado ja' estar disponivel como fuel."""
    gy_artifacts = [c for c in state.graveyard if is_artifact_card(c)]
    if not gy_artifacts:
        return
    target = max(gy_artifacts, key=lambda n: CARD_DB[n].mv)
    state.graveyard.remove(target)
    if is_creature_card(target):
        creature_enters(state, target, from_hand=False)
    else:
        state.battlefield.append(target)
        resolve_etb(state, target)
    state.recursion_events_total += 1


def ironsoul_enforcer_trigger(state: GameState):
    """'Whenever this creature or a commander you control attacks alone,
    return target artifact card from your graveyard to the battlefield.'
    So' dispara quando exatamente 1 criatura atacou nesse combate --
    checagem pos-hoc pro caso organico (Megatron ou qualquer outra
    criatura acabou sendo a unica pronta esse turno, sem escolha
    deliberada). O caso deliberado (linha do Megatron sozinho, achado
    real 2026-09-17: usuario apontou que Megatron nao precisa do resto do
    time pra satisfazer 'attacks alone', ja que ele mesmo e' o comandante)
    ja' disparou este mesmo gatilho antes da declaracao de ataque via
    `try_megatron_alone_with_ironsoul` -- `ironsoul_triggered_this_combat`
    evita reanimar 2x no mesmo combate."""
    if "Ironsoul Enforcer" not in state.battlefield or state.attackers_this_combat != 1:
        return
    if state.ironsoul_triggered_this_combat:
        return
    ironsoul_reanimate(state)
    state.ironsoul_triggered_this_combat = True


def steel_seraph_combat(state: GameState):
    """'At the beginning of combat on your turn, target creature you
    control gains your choice of flying, vigilance, or lifelink until end
    of turn.' Escolhe sempre lifelink no Megatron -- unica opcao com
    efeito numerico neste motor (mesma logica ja usada na versao
    anterior deste arquivo)."""
    if "Steel Seraph" not in state.battlefield:
        return False
    return True


def cast_megatron(state: GameState):
    # O comandante vem da zona de comando, nao da mao/biblioteca --
    # castavel a qualquer main phase desde o turno 1 (nao depende de ter
    # sido "comprado"). Achado real ao testar a reconstrucao 2026-09-02:
    # BASE_LIBRARY exclui o comandante de proposito (nunca entra na mao
    # via draw_cards), mas o cast_megatron original checava "COMMANDER
    # not in state.hand" -- nunca era verdade, Megatron nunca era
    # conjurado em partida nenhuma. Corrigido pra so' depender de mana.
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
    state.battlefield.append(COMMANDER)
    state.commander_in_play = True
    state.commander_cast_count += 1
    if state.commander_cast_turn is None:
        state.commander_cast_turn = state.turn
    state.creature_cast_turn[COMMANDER] = state.turn


def try_ten_rings_draw(state: GameState):
    """The Ten Rings: 'Your maximum hand size is ten. At the beginning of
    your end step, if you have fewer than ten cards in hand, draw cards
    equal to the difference.' Achado real 2026-09-18 (troca por Phyrexian
    Arena): o motor real medido em `hand_by_turn` mostra a mao
    estabilizando em ~3,3 cartas do turno 6 em diante -- com isso em
    campo, compra a diferenca TODO end step (tipicamente 6-7 cartas),
    nao 1 fixa como a Arena. O tamanho maximo de mao tambem sobe pra 10
    enquanto ela esta' em campo (ver o `max_hand` no fim de `end_step`)."""
    if "The Ten Rings" not in state.battlefield:
        return
    missing = 10 - len(state.hand)
    if missing <= 0:
        return
    draw_cards(state, missing)
    state.ten_rings_draws_total += missing


def try_portal_phyrexia_upkeep(state: GameState):
    """Portal to Phyrexia: 'At the beginning of your upkeep, put target
    creature card from a graveyard onto the battlefield under your
    control. It's a Phyrexian in addition to its other types.' Achado
    real 2026-09-13 (usuario notou que 2 copias via Ultron pareciam
    'overpowered' -- a metade ETB ('each opponent sacrifices three
    creatures') ja' era modelada, mas essa 2a habilidade, repetivel todo
    upkeep, tinha ficado de fora inteira -- mecanica fantasma real, nao
    so' impressao). Cada copia em campo (original + tokens via Ultron/
    Cursed Mirror/Osgir) da' um gatilho SEPARADO -- reanima sempre a
    criatura de maior MV do nosso cemiterio (sem cemiterio de oponente
    real modelado, mesma convencao de sempre)."""
    count = sum(1 for n in state.battlefield
                if n == "Portal to Phyrexia" or n.startswith("Portal to Phyrexia (copia"))
    for _ in range(count):
        candidates = [c for c in state.graveyard if is_creature_card(c)]
        if not candidates:
            return
        target = max(candidates, key=lambda n: CARD_DB[n].mv)
        state.graveyard.remove(target)
        creature_enters(state, target, from_hand=False)
        state.portal_phyrexia_reanimations_total += 1


def count_permanent_cards(cards: list) -> int:
    """Conta cartas de permanente (tudo exceto instant/sorcery) numa
    zona -- usado pra aproximar 'descended' do Brass's Tunnel-Grinder
    sem precisar instrumentar cada `state.graveyard.append(...)` do
    arquivo inteiro (dezenas de lugares diferentes)."""
    return sum(1 for c in cards if c in CARD_DB and CARD_DB[c].ctype not in ("instant", "sorcery"))


def try_tunnel_grinder_transform(state: GameState):
    """Brass's Tunnel-Grinder: 'At the beginning of your end step, if
    you descended this turn, put a bore counter on it. Then if there
    are three or more bore counters, remove those counters and
    transform it.' Achado real 2026-09-13 (auditoria completa): so' o
    ETB (looter) tinha dispatch -- essa 2a habilidade, e a transformacao
    inteira pro verso Tecutlan (terreno R), nunca disparava. 'Descended'
    aproximado comparando a contagem de permanentes no cemiterio no
    inicio do turno vs agora (mesmo efeito de rastrear toda vez que algo
    entra no cemiterio, sem precisar instrumentar cada ponto do arquivo
    que ja faz `state.graveyard.append`)."""
    if "Brass's Tunnel-Grinder" not in state.battlefield:
        return
    descended = count_permanent_cards(state.graveyard) > state.turn_start_gy_permanents
    if not descended:
        return
    state.tunnel_grinder_bore_counters += 1
    if state.tunnel_grinder_bore_counters >= 3:
        state.tunnel_grinder_bore_counters = 0
        state.battlefield.remove("Brass's Tunnel-Grinder")
        state.battlefield.append("Tecutlan, the Searing Rift")
        state.tunnel_grinder_transforms_total += 1


def try_bahamut_saga_tick(state: GameState):
    """Summon: Bahamut (Saga -- Enchantment Creature): 'As this Saga
    enters and after your draw step, add a lore counter.' Capitulo I
    (ETB) ja disparado em `resolve_etb`. Aqui, um turno depois do que
    entrou (o proprio turno de entrada nao conta -- o draw step ja
    passou antes dela ser conjurada), avanca 1 capitulo por turno:
    II -- 'Destroy up to one target nonland permanent' (mesma interacao
    do capitulo I, sem alvo real de oponente). III -- 'Draw two cards'
    (ganho real, sem sacrificio). IV -- 'Mega Flare: deals damage equal
    to the total mana value of other permanents you control to EACH
    opponent' (dano multiplicado por NUM_OPPONENTS, mesma convencao de
    todo efeito 'each opponent' do arquivo), depois sacrifica (dispara
    Rakdos, the Muscle se estiver em campo, via `sacrifice()` normal)."""
    if "Summon: Bahamut" not in state.battlefield or state.bahamut_entered_turn == state.turn:
        return
    state.bahamut_chapter += 1
    if state.bahamut_chapter == 2:
        state.interaction_spells_cast_total += 1
    elif state.bahamut_chapter == 3:
        draw_cards(state, 2)
    elif state.bahamut_chapter >= 4:
        other_mv = sum(CARD_DB[n].mv for n in state.battlefield if n != "Summon: Bahamut")
        if other_mv > 0:
            proxy_drain(state, other_mv * NUM_OPPONENTS)
        sacrifice(state, "Summon: Bahamut")
        state.bahamut_mega_flare_total += 1


def make_nexus_copy_name(base_name: str) -> str:
    """Token de Nexus of Becoming: 'a token that's a copy of the exiled
    card, except it's a 3/3 Golem artifact creature in addition to its
    other types.' Achado real 2026-09-15 (usuario apontou: exilar uma
    carta cara de verdade -- ex. Demonic Junker -- e' 'cheating' ela pra
    campo pelo custo da ativacao, nao pelo mana cheio, E o token ainda
    dispara a habilidade ETB real da carta copiada). Diferente do
    `make_token_copy_name` (Ultron/Osgir/Feldon, copia EXATA, mesmo P/T),
    aqui o oraculo manda sobrescrever poder/resistencia pra 3/3 --
    preserva as TAGS (dispatch de ETB real) e o MV (pro Metalwork
    Colossus/fuel do Megatron -- copia mantem MV do original, so' P/T e'
    sobrescrito, regra real de copia)."""
    token_name = base_name + " (Nexus)"
    if token_name not in CARD_DB:
        base = CARD_DB[base_name]
        add(token_name, base.mv, "creature", base.tags | {"artifact"}, power=3, toughness=3, pips={})
    return token_name


def try_nexus_of_becoming(state: GameState):
    """Nexus of Becoming: 'At the beginning of combat on your turn, draw
    a card. Then you may exile an artifact or creature card from your
    hand. If you do, create a token that's a copy of the exiled card,
    except it's a 3/3 Golem artifact creature in addition to its other
    types.' Achado real 2026-09-15 (correcao do usuario, ver
    `make_nexus_copy_name`): a versao anterior exilava a carta de MENOR
    MV e criava um token vanilla desconectado -- mas o oraculo real diz
    que o token E' uma copia (habilidades/ETB reais da carta original),
    entao o certo e' exilar a carta de MAIOR MV disponivel (maior ETB
    real pra "cheatar" pra campo pelo preco de uma ativacao de combate,
    mesma logica de `best_megatron_fuel` -- prioriza sempre o maior
    valor). Dispara em `beginning of combat`, DEPOIS do main_phase (onde
    tudo que cabia no mana ja' foi conjurado) -- exilar o que restou na
    mao e' sempre lucro liquido aqui."""
    if "Nexus of Becoming" not in state.battlefield:
        return
    draw_cards(state, 1)
    candidates = [c for c in state.hand if c in CARD_DB and (is_artifact_card(c) or is_creature_card(c))]
    if not candidates:
        return
    exiled = max(candidates, key=lambda n: CARD_DB[n].mv)
    state.hand.remove(exiled)
    state.exile.append(exiled)
    token_name = make_nexus_copy_name(exiled)
    creature_enters(state, token_name, from_hand=False, token=True)
    state.nexus_tokens_created_total += 1


def try_equip_haste(state: GameState):
    """Lightning Greaves ('equipped creature has haste and shroud') --
    achado real 2026-09-04 (auditoria de fantasmas): era conjurada
    normalmente (confirmado com instrumentacao: 345x em 2000 jogos) mas
    NUNCA equipada em nada -- nenhuma logica de equip existia no arquivo
    inteiro, mana e carta gastos por zero efeito. A metade de protecao
    (shroud) nao tem efeito mecanico possivel aqui (sem oponente real com
    remocao pra proteger contra -- mesma convencao ja documentada pra
    Clever Concealment/Blacksmith's Skill). A metade que TEM efeito real
    e' o haste: uma criatura com doenca de invocacao nao ataca esse turno
    em `ready_creatures()`. Equipa (Equip {0}, gratis) na criatura de
    maior poder que entrou esse turno e ainda nao tem haste."""
    if "Lightning Greaves" not in state.battlefield:
        return
    sick = [n for n in state.battlefield if is_creature_card(n) and n != COMMANDER
            and state.creature_cast_turn.get(n, -1) == state.turn and get_power(state, n) > 0]
    if not sick:
        return
    target = max(sick, key=lambda n: get_power(state, n))
    state.creature_cast_turn[target] = state.turn - 1
    state.equip_haste_activations_total += 1


def try_cosmic_cube_attack_trigger(state: GameState):
    """Cosmic Cube: 'Whenever you attack, look at the top six cards of
    your library. You may cast a spell from among them with mana value
    less than or equal to the greatest power among attacking creatures
    you control without paying its mana cost. Put the rest on the bottom
    of your library in a random order.' Dispara 1x por combate (nao por
    atacante), usando `state.max_attacker_power_this_combat` (acumulado
    por Megatron + `all_attackers_combat`, ja' que aqui TODO mundo ataca
    de verdade). 'Without paying its mana cost' -- sem gate de mana/cor
    nenhum, dispatch direto igual `cast_card` mas sem `spend_mana`. Mesma
    simplificacao de nao embaralhar o resto ja documentada nos reveals de
    Combustible Gearhulk/Saheeli's Directive."""
    if "Cosmic Cube" not in state.battlefield:
        return
    max_power = state.max_attacker_power_this_combat
    if max_power <= 0 or not state.library:
        return
    top = state.library[:6]
    state.library = state.library[6:]
    castable = [c for c in top if c in CARD_DB and c not in LAND_NAMES
                and c not in NO_SELF_HARM_EXCLUDE and CARD_DB[c].mv <= max_power]
    if castable:
        chosen = max(castable, key=lambda n: CARD_DB[n].mv)
        top.remove(chosen)
        if is_creature_card(chosen):
            creature_enters(state, chosen, from_hand=False)
        elif CARD_DB[chosen].ctype in ("instant", "sorcery"):
            resolve_instant_sorcery(state, chosen)
            state.graveyard.append(chosen)
        elif CARD_DB[chosen].ctype == "planeswalker":
            state.battlefield.append(chosen)
            state.daretti_savant_loyalty = DARETTI_SAVANT_STARTING_LOYALTY
        else:
            state.battlefield.append(chosen)
            resolve_etb(state, chosen)
            if is_artifact_card(chosen):
                artifact_etb_hooks(state, chosen)
        state.cosmic_cube_free_casts_total += 1
        state.recursion_events_total += 1
    state.library.extend(top)


def megatron_combat(state: GameState):
    if not state.commander_in_play or state.megatron_face is None:
        return
    if COMMANDER not in ready_creatures(state):
        return
    state.attackers_this_combat += 1

    if state.megatron_face == "vehicle":
        fuel = best_megatron_fuel(state)
        if fuel is not None:
            mv = CARD_DB[fuel].mv
            sacrifice(state, fuel)
            state.megatron_fuel_sacrificed_total += 1
            excess = max(0, mv - 1)  # proxy: alvo de 1 de resistencia (premissa do proprio primer)
            if excess > 0:
                proxy_drain(state, excess)
            state.megatron_face = "tyrant"
            state.megatron_conversions_total += 1

    power = MEGATRON_TYRANT_POWER if state.megatron_face == "tyrant" else MEGATRON_VEHICLE_POWER
    lifelink_this_combat = steel_seraph_combat(state)
    proxy_drain(state, power)
    state.max_attacker_power_this_combat = max(state.max_attacker_power_this_combat, power)
    if lifelink_this_combat:
        gain_life(state, power)
    # Achado real 2026-09-18 (usuario apontou -- regra de commander
    # damage nunca modelada): "if a player has been dealt 21 or more
    # combat damage by the same commander since the game started, that
    # player loses the game" (CR 903.10a). Linha real disponivel pro
    # piloto: focar o MESMO oponente com o Megatron ataque apos ataque
    # (escolha deliberada, igual `try_megatron_alone_with_ironsoul` --
    # nada aqui assume isso automaticamente, so' credita quando os 21
    # de dano de combate do proprio Megatron realmente se acumulam).
    state.megatron_commander_damage_dealt += power
    if state.megatron_commander_damage_dealt >= COMMANDER_DAMAGE_LETHAL:
        state.commander_damage_win = True


def megatron_postcombat(state: GameState):
    if not state.commander_in_play or state.megatron_face != "tyrant":
        return
    if state.life_lost_by_opponents_this_turn > 0:
        mana = state.life_lost_by_opponents_this_turn
        state.bonus_mana_pool += mana
        state.megatron_mana_generated_total += mana
        state.megatron_face = "vehicle"
        state.megatron_conversions_total += 1


def try_bygone_colossus_warp(state: GameState):
    """Bygone Colossus: 'Warp {3} (cast for {3}, exile at next end step,
    may cast from exile later for warp again).' Repetivel enquanto
    houver mana sobrando -- cada cast dispara Warstorm Surge de novo
    (9 de dano por ativacao, se Warstorm Surge estiver em campo)."""
    in_hand = "Bygone Colossus" in state.hand
    in_exile = "Bygone Colossus" in state.exile
    if not (in_hand or in_exile) or remaining_mana(state) < 3:
        return
    spend_mana(state, 3)
    if in_hand:
        state.hand.remove("Bygone Colossus")
    else:
        state.exile.remove("Bygone Colossus")
    creature_enters(state, "Bygone Colossus", from_hand=False)
    state.creature_cast_turn["Bygone Colossus"] = state.turn - 1
    state.temp_creatures_pending_exile.append("Bygone Colossus")
    state.creatures_cheated_in_total += 1


def try_cityscape_leveler_unearth(state: GameState):
    """Cityscape Leveler: 'Unearth {8}' (reanima do cemiterio, ganha
    haste, exilada no fim do turno ou se deixar o campo). Achado real
    2026-09-15 (auditoria comparativa): antes excluida por "custo igual
    ao hardcast, sem ganho de modelar separado" -- mesmo raciocinio que
    seria usado pra rejeitar o Warp {3} do Bygone Colossus, que E'
    modelado (`try_bygone_colossus_warp`, template direto pra esta
    funcao). Reanimar de novo dispara o ETB completo (Warstorm Surge +
    a remocao real do `cityscape_leveler`, ver `resolve_etb`) e ainda
    ataca esse turno (haste)."""
    if "Cityscape Leveler" not in state.graveyard or remaining_mana(state) < 8:
        return
    spend_mana(state, 8)
    state.graveyard.remove("Cityscape Leveler")
    creature_enters(state, "Cityscape Leveler", from_hand=False)
    state.creature_cast_turn["Cityscape Leveler"] = state.turn - 1
    state.temp_creatures_pending_exile.append("Cityscape Leveler")
    state.creatures_cheated_in_total += 1


# ---------------------------------------------------------------------------
# Custo efetivo / cast / terrenos
# ---------------------------------------------------------------------------

def effective_cost(state: GameState, name: str) -> int:
    mv = CARD_DB[name].mv
    if name == "Metalwork Colossus":
        # "This spell costs {X} less to cast, where X is the total mana
        # value of noncreature artifacts you control."
        reduction = sum(CARD_DB[n].mv for n in state.battlefield
                         if is_artifact_card(n) and not is_creature_card(n))
        mv = max(0, mv - reduction)
    elif name == "Demonic Junker":
        # "Affinity for artifacts (costs {1} less for each artifact you control)."
        reduction = sum(1 for n in state.battlefield if is_artifact_card(n))
        mv = max(0, mv - reduction)
    return mv


def can_cast(state: GameState, name: str) -> bool:
    return remaining_mana(state) >= effective_cost(state, name) and has_color_sources_for(state, name)


NO_SELF_HARM_EXCLUDE = {
    # Wipes/dano simetrico que so' machucariam o proprio board -- sem
    # oponente real pra tambem atingir, nunca vale a pena conjurar
    # (mesma convencao ja usada pro Blasphemous Act em toda a sessao).
    "Blasphemous Act", "Decree of Pain", "Heartless Conscription", "Chandra's Ignition",
    # Protecao (hexproof/indestructible/phase out) sem remocao/wrath real
    # de oponente pra proteger contra -- conjurar so' desperdicaria mana
    # (achado real ao testar: sem essa exclusao, Blacksmith's Skill era
    # auto-conjurada todo turno que sobrava 1 mana, sem efeito nenhum,
    # mesma categoria de simplificacao estrutural de sempre, nao e'
    # fantasma -- a tag continua definida e documentada).
    "Blacksmith's Skill", "Clever Concealment",
    # Achado real 2026-09-15: sorcery com CUSTO ADICIONAL real (sacrificio)
    # que `resolve_instant_sorcery()` nao paga -- sem essa exclusao, o
    # loop generico de castables via' "Trash for Treasure" como qualquer
    # sorcery afordavel, gastava a mana + a carta, e nunca chamava a
    # logica real (`try_trash_for_treasure`, que exige sacrificar um
    # artefato E escolher alvo no cemiterio). Confirmado com teste
    # isolado: mana gasta, carta pro cemiterio, ZERO reanimacao
    # (`weld_activations_total` ficava em 0). So' a funcao dedicada, mais
    # tarde no `main_phase`, deve conjurar essa carta.
    "Trash for Treasure",
}


def resolve_instant_sorcery(state: GameState, name: str):
    tags = CARD_DB[name].tags
    if "interaction" in tags:
        state.interaction_spells_cast_total += 1
    elif "loot2_2_flashback" in tags:
        # Faithless Looting: "draw two cards, then discard two cards."
        draw_cards(state, 2)
        for _ in range(min(2, len(state.hand))):
            worst = worst_discard_target(state)
            state.hand.remove(worst)
            state.graveyard.append(worst)
    elif "saheeli_directive" in tags:
        # "Improvise. Reveal the top X cards of your library. You may put
        # any number of artifact cards with mana value X or less from
        # among them onto the battlefield. Then put the rest into your
        # graveyard." X = o maximo pagavel (Improvise nao modelado a
        # parte -- paga so' com mana real, documentado).
        x = max(0, remaining_mana(state) - 3)
        if x <= 0:
            return
        spend_mana(state, x + 3)
        revealed = state.library[:x]
        state.library = state.library[x:]
        for c in revealed:
            if c in CARD_DB and is_artifact_card(c) and CARD_DB[c].mv <= x:
                if is_creature_card(c):
                    creature_enters(state, c, from_hand=False)
                else:
                    state.battlefield.append(c)
                    resolve_etb(state, c)
            else:
                state.graveyard.append(c)


def try_cast_flashback(state: GameState, name: str, flashback_cost: int):
    """Faithless Looting {2}{R} flashback, do cemiterio, exilada depois
    de resolver."""
    if name not in state.graveyard or remaining_mana(state) < flashback_cost:
        return
    spend_mana(state, flashback_cost)
    state.graveyard.remove(name)
    resolve_instant_sorcery(state, name)
    state.exile.append(name)


def cast_card(state: GameState, name: str):
    card = CARD_DB[name]
    spend_mana(state, effective_cost(state, name))
    if name in state.hand:
        state.hand.remove(name)

    if any(t.startswith("rock") for t in card.tags):
        state.ramp_pieces_cast_total += 1

    if card.ctype in ("instant", "sorcery"):
        resolve_instant_sorcery(state, name)
        state.graveyard.append(name)
        return

    if card.ctype == "planeswalker":
        state.battlefield.append(name)
        state.daretti_savant_loyalty = DARETTI_SAVANT_STARTING_LOYALTY
        return

    if card.ctype == "creature":
        creature_enters(state, name, from_hand=False)
        return

    state.battlefield.append(name)
    resolve_etb(state, name)
    if is_artifact_card(name):
        artifact_etb_hooks(state, name)


def play_land(state: GameState):
    if state.lands_played_this_turn >= 1:
        return
    lands_in_hand = [n for n in state.hand if n in LAND_NAMES]
    if not lands_in_hand:
        return

    def missing_score(card):
        score = 0
        for color in "WBR":
            if color_sources(state, color) == 0 and color in CARD_DB[card].produces:
                score += 1
        return -score

    lands_in_hand.sort(key=missing_score)
    choice = lands_in_hand[0]
    state.hand.remove(choice)
    state.lands_played_this_turn += 1
    state.battlefield.append(choice)
    if choice in ETB_TAPPED_LANDS:
        if choice == "Smoldering Marsh":
            basics_in_play = sum(1 for n in state.battlefield if n in ("Mountain", "Plains", "Swamp"))
            if basics_in_play < 2:
                state.tapped_land_this_turn = choice
        else:
            state.tapped_land_this_turn = choice


# ---------------------------------------------------------------------------
# Loop de turno
# ---------------------------------------------------------------------------

def try_black_market_connections(state: GameState):
    """'At the beginning of your first main phase, choose one or more --
    Sell Contraband (Treasure, lose 1 life) / Buy Information (draw,
    lose 2 life) / Hire a Mercenary (3/2 token, lose 3 life).' Escolhe as
    3 (maximiza valor por ativacao), paga 6 de vida total -- so' se tiver
    vida sobrando."""
    if state.life <= 10:
        return
    state.black_market_used_this_turn = True
    state.bonus_mana_pool += 1
    self_damage(state, 1)
    draw_cards(state, 1)
    self_damage(state, 2)
    token = "Shapeshifter Token"
    if token not in CARD_DB:
        add(token, 0, "creature", set(), power=3, toughness=2)
    creature_enters(state, token, from_hand=False, token=True)
    self_damage(state, 3)


def main_phase(state: GameState):
    cast_megatron(state)
    if "Black Market Connections" in state.battlefield and not state.black_market_used_this_turn:
        try_black_market_connections(state)

    try_station_lands(state)

    while True:
        castables = [n for n in state.hand if n not in LAND_NAMES and can_cast(state, n)
                     and n not in NO_SELF_HARM_EXCLUDE]
        if not castables:
            break

        def prio(n):
            tags = CARD_DB[n].tags
            group = 0 if (tags & {"rock1", "rock2", "rock3"}) else 1
            return (group, effective_cost(state, n))

        castables.sort(key=prio)
        cast_card(state, castables[0])

    try_goblin_welder(state)
    try_scrap_welder(state)
    try_trash_for_treasure(state)
    try_chandras_ignition(state)
    try_goblin_engineer_activation(state)
    try_scarecrone(state)
    try_mishra_unearth(state)
    try_osgir_activation(state)
    try_osgir_pump(state)
    try_metalwork_colossus_recursion(state)
    try_daretti_savant(state)
    try_feldon(state)
    try_sneak_attack(state)
    try_ayara(state)
    try_ayara_transform(state)
    try_susur_secundi(state)
    try_bygone_colossus_warp(state)
    try_cityscape_leveler_unearth(state)
    try_fountainport(state)
    try_tarrians_journal(state)
    try_cast_flashback(state, "Faithless Looting", 3)
    try_mind_stone_sac(state)
    try_melded_moxite_sac(state)


def daretti_rocketeer_attack_ability(state: GameState):
    """'Whenever Daretti enters or attacks, choose target artifact card
    in your graveyard. You may sacrifice an artifact. If you do, return
    the chosen card to the battlefield.' Achado real 2026-09-02: nem a
    metade de ETB nem a de ataque tinham dispatch nenhum (so' o poder
    dinamico estava implementado) -- mesmo padrao de "so Megatron/Anrakyr
    atacam" escondendo o gatilho de ataque; a de ETB nao tinha nem essa
    desculpa, era fantasma puro. Corrigido as 2 aqui (chamada tanto do
    ETB quanto do loop de ataque generico)."""
    gy_artifacts = [c for c in state.graveyard if is_artifact_card(c)]
    if not gy_artifacts:
        return
    target = max(gy_artifacts, key=lambda n: CARD_DB[n].mv)
    fodder = best_weld_fodder(state)
    if fodder is None or CARD_DB[fodder].mv >= CARD_DB[target].mv:
        return
    sacrifice(state, fodder)
    if target not in state.graveyard:
        return
    state.graveyard.remove(target)
    if is_creature_card(target):
        creature_enters(state, target, from_hand=False)
    else:
        state.battlefield.append(target)
        resolve_etb(state, target)
    state.weld_activations_total += 1


def try_crew_demonic_junker(state: GameState):
    """Demonic Junker: 'Crew 2 (Tap any number of untapped creatures you
    control with total power 2 or greater: This Vehicle becomes an
    artifact creature until end of turn.)' Achado real 2026-09-15
    (usuario mudou de ideia sobre nunca crewar -- linha real: um token/
    criatura barata que sobrou de turno anterior tapa pra crewar, o
    Junker ataca junto com o Megatron nesse combate, e o MESMO token
    ainda serve de combustivel pro sacrificio do Megatron depois --
    crewar so' TAPA quem crewou, nunca sacrifica). Nunca tapa o Megatron
    (ataca por conta propria via `megatron_combat`) -- prioriza as
    criaturas de MENOR poder disponiveis (preserva os atacantes grandes
    de verdade), somando ate' bater o Crew 2. `ready_creatures()` ja'
    exclui doenca de invocacao -- um token criado NESSE combate (ex:
    Nexus of Becoming) nunca pode crewar no mesmo turno sem haste
    (achado real do usuario, confere com a regra oficial: crew e' um
    custo de {T}, sujeito a doenca de invocacao igual atacar)."""
    if "Demonic Junker" not in state.battlefield or state.demonic_junker_crewed_this_turn:
        return
    candidates = sorted(
        (n for n in ready_creatures(state) if n != COMMANDER and get_power(state, n) > 0),
        key=lambda n: get_power(state, n),
    )
    used = []
    total = 0
    for n in candidates:
        used.append(n)
        total += get_power(state, n)
        if total >= 2:
            break
    if total < 2:
        return
    for n in used:
        state.crewed_creatures_tapped.add(n)
    state.demonic_junker_crewed_this_turn = True
    state.demonic_junker_crews_total += 1


def all_attackers_combat(state: GameState):
    """Achado real 2026-09-02 (usuario jogou no Archidekt e reportou:
    "Os dois geraram mana, ataquei 2 jogadores diferentes e gerei 17 de
    mana incolor" -- Metalwork Colossus atacou um oponente DIFERENTE do
    que o Megatron, e o dano dele TAMBEM alimentou o gatilho pos-combate
    do Megatron via `state.life_lost_by_opponents_this_turn`, que e' um
    pool COMPARTILHADO -- o oraculo diz "life your opponents have lost
    THIS TURN", nao "life lost to Megatron"). Ate' aqui o motor so'
    modelava Megatron (+ Anrakyr, pela propria habilidade dele) atacando
    de verdade -- os outros finalizadores grandes (Metalwork Colossus,
    Bygone Colossus, Skitterbeam Battalion, os Gearhulks, Ironsoul
    Enforcer, Ayara, Daretti Rocketeer, Ragavan, Treasure Nabber) nunca
    atacavam. Corrigido: TODA criatura pronta (sem doenca de invocacao)
    com poder > 0 ataca de verdade, cada uma contribuindo pro mesmo pool
    de dano/vida-perdida via `proxy_drain()` -- sem bloqueio real
    modelado pra ninguem (mesma convencao de sempre), entao atacar com
    tudo e' sempre a jogada correta aqui."""
    for name in ready_creatures(state):
        if name == COMMANDER:
            continue  # ja' tratado em megatron_combat (fuel/conversao propria)
        power = get_power(state, name)
        if power <= 0:
            continue
        state.attackers_this_combat += 1
        proxy_drain(state, power)
        state.max_attacker_power_this_combat = max(state.max_attacker_power_this_combat, power)
        if "infect" in CARD_DB[name].tags and power >= POISON_LETHAL:
            # Infect: "deals damage to players in the form of poison
            # counters instead." Combate normal desbloqueado (sem
            # bloqueio real modelado pra nenhum atacante meu, convencao
            # de sempre) com BlightSteel Colossus (11 de poder, teto real
            # de 10 pra derrota) e' letal so' de atacar, sem precisar do
            # combo com Chandra's Ignition.
            state.blightsteel_poison_win = True
        if name == "Anrakyr the Traveller":
            anrakyr_attack_ability(state)
        elif name == "Daretti, Rocketeer Engineer":
            daretti_rocketeer_attack_ability(state)
        elif "cityscape_leveler" in CARD_DB[name].tags:
            # "whenever this creature attacks, destroy up to one target
            # nonland permanent" -- mesma interacao do ETB, dispara de
            # novo a cada combate que ela ataca (ready_creatures ja'
            # garante que so' ataca sem doenca de invocacao). Achado real
            # 2026-09-19: dispatch por NOME LITERAL ("Cityscape Leveler")
            # nunca batia pra token-copia dela (Ultron/Osgir/Feldon, todos
            # via `make_token_copy_name` -> "Cityscape Leveler (copia)",
            # `CARD_DB[token_name] = CARD_DB[base_name]` preserva a tag
            # `cityscape_leveler` mas nao o nome) -- o gatilho de ETB
            # (`resolve_etb`) ja' checava a tag corretamente, so' o de
            # ataque estava por nome. Corrigido pra checar a tag, mesmo
            # padrao ja usado por "infect" 2 linhas acima nesta mesma
            # funcao.
            state.interaction_spells_cast_total += 1

    if state.demonic_junker_crewed_this_turn and "Demonic Junker" in state.battlefield:
        # Crewado esse turno -- "becomes an artifact creature until end
        # of turn", ataca junto (ctype fica "artifact" no CARD_DB de
        # proposito -- Vehicle nao e' criatura por padrao -- entao entra
        # aqui explicito em vez de via `ready_creatures()`).
        power = get_power(state, "Demonic Junker")
        if power > 0:
            state.attackers_this_combat += 1
            proxy_drain(state, power)
            state.max_attacker_power_this_combat = max(state.max_attacker_power_this_combat, power)


def try_megatron_alone_with_ironsoul(state: GameState) -> bool:
    """Linha real achada pelo usuario 2026-09-17: com Ironsoul Enforcer em
    campo, Megatron NAO precisa do resto do time pra satisfazer 'attacks
    alone' -- ele mesmo e' o comandante, entao atacar SO' com ele ja'
    dispara o Ironsoul. Sequencia real (os 2 gatilhos disparam juntos na
    declaracao de ataque; o controlador escolhe a ordem na pilha -- aqui
    colocamos o do Ironsoul pra resolver primeiro): Ironsoul devolve o
    artefato de MAIOR CMC do cemiterio pro campo -> esse artefato
    recem-chegado fica disponivel como fuel do proprio gatilho de ataque
    do Megatron ('may sacrifice another artifact... damage equal to its
    mana value... excess dealt to that creature's controller and you
    convert Megatron') -> dano extra + flip no meio do combate -> ainda
    causa dano de combate normal (mudar de face nao remove do combate) ->
    no postcombat main da face Tyrant pode converter de novo e ganhar
    mana incolor = vida perdida pelos oponentes esse turno. O corpo
    reanimado fica permanente no campo depois (fuel pro weld/Ultron/
    Metalwork Colossus).

    So' vale abrir mao do ataque do resto do time quando o artefato de
    maior CMC do cemiterio bate mais poder-equivalente do que a soma do
    poder dos outros atacantes prontos -- sem bloqueio real modelado,
    atacar com todo mundo e' sempre pelo menos tao bom quanto nao atacar,
    entao so' compensa abrir mao disso quando o combo entrega mais do que
    essa soma."""
    if "Ironsoul Enforcer" not in state.battlefield:
        return False
    if COMMANDER not in ready_creatures(state):
        return False
    gy_artifacts = [c for c in state.graveyard if is_artifact_card(c)]
    if not gy_artifacts:
        return False
    best_target = max(gy_artifacts, key=lambda n: CARD_DB[n].mv)
    other_power = sum(get_power(state, n) for n in ready_creatures(state)
                       if n != COMMANDER and get_power(state, n) > 0)
    if CARD_DB[best_target].mv <= other_power:
        return False
    ironsoul_reanimate(state)
    state.ironsoul_triggered_this_combat = True
    state.megatron_alone_combos_total += 1
    return True


def combat_step(state: GameState):
    state.attackers_this_combat = 0
    state.max_attacker_power_this_combat = 0
    state.ironsoul_triggered_this_combat = False
    try_nexus_of_becoming(state)
    try_ayara_flip_reanimate(state)

    alone = try_megatron_alone_with_ironsoul(state)
    if not alone:
        try_crew_demonic_junker(state)
    megatron_combat(state)
    if not alone:
        all_attackers_combat(state)
    ironsoul_enforcer_trigger(state)
    try_cosmic_cube_attack_trigger(state)
    state.attackers_total_all_turns += state.attackers_this_combat


def end_step(state: GameState):
    try_tunnel_grinder_transform(state)
    try_ten_rings_draw(state)

    for n in state.temp_creatures_pending_sacrifice[:]:
        if n in state.battlefield:
            sacrifice(state, n)
    state.temp_creatures_pending_sacrifice = []

    for n in state.temp_creatures_pending_exile[:]:
        if n in state.battlefield:
            state.battlefield.remove(n)
            state.exile.append(n)
    state.temp_creatures_pending_exile = []

    for n in state.daretti_emblem_pending_return[:]:
        if n in state.graveyard:
            state.graveyard.remove(n)
            if is_creature_card(n):
                creature_enters(state, n, from_hand=False)
            else:
                state.battlefield.append(n)
                resolve_etb(state, n)
    state.daretti_emblem_pending_return = []

    max_hand = 10 if "The Ten Rings" in state.battlefield else 7
    while len(state.hand) > max_hand:
        worst = worst_discard_target(state)
        state.hand.remove(worst)
        state.graveyard.append(worst)


def play_turn(state: GameState, is_first_turn: bool, on_play: bool):
    state.turn += 1
    state.turn_start_gy_permanents = count_permanent_cards(state.graveyard)
    state.lands_played_this_turn = 0
    state.mana_spent_this_turn = 0
    state.bonus_mana_pool = 0
    state.temp_power_boost = {}
    state.tapped_land_this_turn = None
    state.life_lost_by_opponents_this_turn = 0
    state.ayara_recur_used_this_turn = False
    state.goblin_welder_used_this_turn = False
    state.scrap_welder_used_this_turn = False
    state.feldon_used_this_turn = False
    state.goblin_engineer_used_this_turn = False
    state.scarecrone_used_this_turn = False
    state.mishra_unearth_used_this_turn = False
    state.osgir_used_this_turn = False
    state.black_market_used_this_turn = False
    state.susur_secundi_used_this_turn = False
    state.fountainport_used_this_turn = False
    state.tarrians_journal_used_this_turn = False
    state.crewed_creatures_tapped = set()
    state.demonic_junker_crewed_this_turn = False

    try_portal_phyrexia_upkeep(state)
    # Achado real 2026-09-18 (usuario apontou): "skip the draw step" no
    # primeiro turno de quem joga primeiro so' existe na regra 1x1 (CR
    # 103.8a: "In a two-player game..."). Commander e' sempre multiplayer
    # -- CR real pra 3+ jogadores: NENHUM jogador pula a compra do
    # primeiro turno, nem quem comeca. `NUM_OPPONENTS=3` (mesa de 4) e'
    # convencao de sempre neste arquivo -- a checagem antiga aplicava a
    # regra errada (1x1) numa mesa que nunca e' 1x1, tirando 1 carta de
    # TODO jogo simulado (nao so' um combo raro -- 100% dos jogos, desde
    # a reconstrucao 2026-09-02).
    draw_cards(state, 1)
    try_bahamut_saga_tick(state)

    play_land(state)
    main_phase(state)
    try_equip_haste(state)
    combat_step(state)
    # Achado real 2026-09-18 (usuario perguntou quanto de mana incolor o
    # 2o flip do Megatron gera pra questionar o hardcast do BlightSteel
    # Colossus): `megatron_postcombat` estava dentro de `end_step`, ou
    # seja, DEPOIS da 2a chamada de `main_phase` -- a mana gerada pela
    # conversao nunca chegava a ser gastavel em nenhum cast daquele
    # turno, so' existia pro contador `megatron_mana_generated_total`.
    # O oraculo real e' "at the beginning of each of your postcombat main
    # phases, you may convert Megatron" -- o gatilho tem que resolver
    # ANTES do proprio main phase pos-combate rodar, pra' mana gerada
    # poder ser gasta nele (ex.: hardcast do BlightSteel Colossus).
    megatron_postcombat(state)
    main_phase(state)
    end_step(state)


# ---------------------------------------------------------------------------
# Modo opcional de resiliencia -- remocao "inteligente" de oponente
# ---------------------------------------------------------------------------
# Achado real 2026-09-16 (usuario, playtest com o simulador de interacao
# do Archidekt): oponente de mesa real NAO remove aleatorio -- mira
# sempre a peca que vira motor recorrente ("quando estava com Portal na
# mesa a remocao de artefato automaticamente pega ele, por causa do
# motor que ele traz pro deck"). Isso e' um modo SEPARADO e OPCIONAL --
# `simulate_one`/`run_batch` continuam exatamente como sempre foram
# (goldfish puro, sem oponente real, premissa documentada no topo do
# arquivo). Este modo serve pra medir RESILIENCIA (o motor aguenta
# perder a peca central?), nao pra validar dano/draw normais.

INTERACTION_ENGINE_PRIORITY = [
    "Warstorm Surge",
    "Portal to Phyrexia",
    "Goblin Welder",
    "Pia's Revolution",
    "Genesis Chamber",
    "Ultron, Artificial Malevolence",
    "Cosmic Cube",
    "Daretti, Scrap Savant",
    "Osgir, the Reconstructor",
    "Scrap Trawler",
]
# Lista curada por prioridade (a mais critica primeiro) -- so' cartas
# que sao motor RECORRENTE de valor (dano/recursao/token/draw todo
# turno), nao corpos grandes isolados. Metalwork Colossus fica DE FORA
# de proposito: ele QUER ser removido/sacrificado (`try_metalwork_
# colossus_recursion` o traz de volta pra mao pagando 2 sacrificios) --
# remove-lo do campo nao atrapalha o plano, entao um oponente esperto
# nao gastaria a remocao nele em vez de numa peca irrecuperavel.

INTERACTION_SETUP_TURNS = 2
# Achado real do usuario: turnos 1-2 sao sempre setup, sem chance de
# remocao nenhuma -- o oponente ainda nao tem motivo/mana pra reagir.


def interaction_chance(state: GameState) -> float:
    """Formula compartilhada de 'chance do oponente reagir esse turno'
    -- usada tanto pela remocao (`try_smart_opponent_removal`) quanto
    pelo ataque (`try_smart_opponent_attack`). Escala com o impacto do
    meu proprio board (contagem de permanentes nao-terreno em campo) --
    board mais desenvolvido = ameaca mais obvia = mais provavel que o
    oponente reaja."""
    board_impact = sum(1 for n in state.battlefield if n not in LAND_NAMES)
    return min(0.10 + 0.03 * board_impact, 0.75)


def try_smart_opponent_removal(state: GameState) -> Optional[str]:
    """Rola 1x por turno (a partir do turno 3) se o oponente "esperto"
    destroi a peca-motor de maior prioridade presente em campo. Sem
    nenhuma peca da lista curada em campo, retorna sem fazer nada
    (oponente nao gasta remocao "aleatoria" num corpo grande vanilla
    so' porque e' grande). Usa `state.interaction_rng` (separado do
    `rng` do mulligan) -- so' setado por `simulate_one_with_interaction`,
    nunca pelo goldfish padrao."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    present = [n for n in INTERACTION_ENGINE_PRIORITY if n in state.battlefield]
    if not present:
        return None
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    target = present[0]
    sacrifice(state, target, is_own_sacrifice=False)
    state.smart_removals_total += 1
    state.smart_removal_log.append((state.turn, target))
    return target


OPPONENT_ATTACKER_PROFILES = [
    ("Knight Token", 2, 2),
    ("Saproling Token", 1, 1),
    ("Vampire Token", 1, 1),
    ("Zombie Token", 2, 2),
    ("Soldier Token", 1, 1),
    ("Goblin Token", 1, 1),
    ("Elemental Token", 3, 3),
]
# Achado real do usuario (playtest real, Archidekt interaction sim):
# "ataqeui o Knight token do adversario absorvi com o Feldon, ele e 2/3
# e os knights eram 2/2! Um passou e outro morreu." -- calibrado pelo
# exemplo real (Knight 2/2), depois generalizado por pedido direto do
# usuario ("pode variar o token: Knight, saproling, vampiro, etc") pra
# uma lista de perfis genericos comuns de token em Commander, sorteada
# a cada ataque via `state.interaction_rng`. Stats sao os tipicos reais
# de cada tipo (Saproling/Soldier/Goblin 1/1, Knight/Zombie 2/2,
# Elemental 3/3) -- keywords de evasao (ex.: flying do Vampire token)
# ficam FORA de proposito, mesma convencao de "sem bloqueio real
# modelado" ja documentada pro resto do arquivo (so' poder/resistencia
# entram na conta aqui).


def try_smart_opponent_attack(state: GameState) -> Optional[str]:
    """Modo opcional de resiliencia -- ataque de oponente (rola
    independente da remocao, mesma janela/formula de chance via
    `interaction_chance`). Sorteia 1 perfil de `OPPONENT_ATTACKER_
    PROFILES` e bloqueia com a MENOR criatura pronta que mata o
    atacante E sobrevive (preserva as criaturas grandes pro meu
    proprio ataque, mesma logica de `best_weld_fodder` pra fodder
    barato) -- sem bloqueador bom disponivel, leva o dano na cara.
    Nunca usa o Megatron como bloqueador: ele ja atacou nesse mesmo
    ciclo (tapped) e, na face Vehicle, so' e' criatura durante O MEU
    turno ('Living metal') -- nao existe como bloqueador real no turno
    do oponente em nenhuma das duas faces. Retorna o nome do token que
    atacou (pra log/relatorio) ou None se nao atacou."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    name, power, toughness = state.interaction_rng.choice(OPPONENT_ATTACKER_PROFILES)
    candidates = [n for n in ready_creatures(state) if n != COMMANDER
                  and get_power(state, n) >= toughness
                  and CARD_DB[n].toughness > power]
    if candidates:
        blocker = min(candidates, key=lambda n: CARD_DB[n].mv)
        state.smart_blocks_total += 1
        state.smart_attack_log.append((state.turn, name, "blocked"))
        return name
    self_damage(state, power)
    state.smart_attacks_taken_total += 1
    state.smart_attack_log.append((state.turn, name, "unblocked"))
    return name


def try_smart_opponent_discard(state: GameState) -> Optional[str]:
    """Modo opcional de resiliencia -- discard/disrupcao de mao (rola
    independente de remocao/ataque, mesma janela/formula de chance via
    `interaction_chance`). Pedido direto do usuario 2026-09-19, depois
    de estudar o simulador de interacao real do Archidekt: la' tambem e'
    so' um "rolou discard" com o alvo puxado sem inteligencia nenhuma
    (carta real aleatoria de uma pool, sem checar se faz sentido pro
    board -- os proprios devs documentam isso, ex.: sugeriu Assassin's
    Trophy contra um board com so' um Kraken Hatchling). Achado real que
    motivou isso: Partida #1 (goldfish-log.md, 2026-09-18) teve a mao
    inteira descartada por um Jace's Archivist do oponente -- categoria
    que o modo de resiliencia simplesmente nao tinha.

    Ao contrario de `try_smart_opponent_removal` (sempre acerta a peca-
    motor de MAIOR prioridade, seleciono 'inteligente' de proposito),
    aqui o alvo e' escolhido puramente AO ACASO dentro da mao inteira --
    exatamente o pedido do usuario ('aleatoriamente, no modelo do
    Archidekt'), sem filtrar terreno/carta ruim: um oponente real
    escolheria a melhor carta pra te fazer descartar (efeito dirigido,
    tipo Thoughtseize), mas o PERFIL aleatorio aqui representa efeitos
    de descarte aleatorio de verdade (ex. seu proprio Faithless
    Looting/Melded Moxite nao sao aleatorios, mas ha' cartas reais de
    oponente que sao -- e a falta de 'inteligencia' no alvo e' o mesmo
    tradeoff que o Archidekt aceitou de proposito, documentado no post
    deles). Descarta exatamente 1 carta por instancia (mesma granularidade
    de 1-permanente/1-atacante das outras 2 categorias) -- sem mao pra
    descartar, retorna None sem fazer nada."""
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


BOARD_WIPE_CHANCE_FACTOR = 0.4
# Um board wipe real (Wrath of God/Blasphemous Act/Toxic Deluge, etc.)
# e' MUITO mais raro numa lista de 99 cartas do que remocao pontual --
# a maioria dos decks reais de Commander roda uns 8-12 spot removals
# contra so' 2-4 sweepers. Em vez de inventar uma formula nova, aplica
# um fator redutor sobre a MESMA `interaction_chance()` compartilhada
# (documentado aqui, ajustavel se o usuario achar que nao bate com a
# mesa real dele).


def try_smart_opponent_wipe(state: GameState) -> Optional[list]:
    """Modo opcional de resiliencia -- board wipe ("destroy all
    creatures", categoria real do simulador do Archidekt junto com
    ataque/remocao/discard). Rola independente das outras 3 categorias,
    mesma janela (`INTERACTION_SETUP_TURNS`), chance reduzida por
    `BOARD_WIPE_CHANCE_FACTOR` (ver acima). Destroi TODAS as minhas
    criaturas em campo de uma vez -- ao contrario da remocao (1 peca-
    motor curada) e do discard (1 carta aleatoria), aqui o "alvo" e'
    sempre o board inteiro, e' isso que torna um wipe um wipe.

    Achado de regra real ao implementar: o Megatron na face Destructive
    Force (Vehicle) SO' e' criatura durante O MEU turno ('Living metal')
    -- as 4 funcoes deste modo de resiliencia representam interacao do
    OPONENTE, ou seja, fora do meu turno. Um wipe que resolve nesse
    momento (sorcery-speed, main phase do proprio oponente, mesma janela
    de sempre) NAO acerta o Megatron se ele estiver na face Vehicle
    nesse instante (`state.megatron_face == "vehicle"`) -- mesma
    checagem ja usada em `try_smart_opponent_attack` pra excluir o
    Megatron como bloqueador. Na face Tyrant (Legendary Artifact
    CREATURE, sem depender de Living Metal) ele e' sempre um alvo legal.

    Cada criatura destruida passa por `sacrifice(is_own_sacrifice=False)`
    -- mesma funcao central que ja trata comandante->zona de comando,
    Warp/Unearth->exilio, Blightsteel->biblioteca, e dispara os gatilhos
    reais de morte (Scrap Trawler/toolbox/Triplicate Titan) pra cada uma.
    Sem nenhuma criatura em campo (contando a excecao do Megatron-
    Vehicle), retorna None sem fazer nada -- oponente esperto nao gasta
    um wipe num board vazio. Retorna a lista de nomes destruidos (pra
    log/relatorio) ou None se nao disparou."""
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    targets = [n for n in state.battlefield if is_creature_card(n)
               and not (n == COMMANDER and state.megatron_face == "vehicle")]
    if not targets:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * BOARD_WIPE_CHANCE_FACTOR:
        return None
    for n in targets:
        sacrifice(state, n, is_own_sacrifice=False)
    state.smart_wipes_total += 1
    state.smart_wipe_log.append((state.turn, targets))
    return targets


# ---------------------------------------------------------------------------
# Mulligan / build / batch
# ---------------------------------------------------------------------------

def should_keep(hand: list) -> bool:
    lands = sum(1 for n in hand if n in LAND_NAMES)
    good_early = {"Sol Ring", "Arcane Signet", "Fellwar Stone", "Mind Stone", COMMANDER}
    if lands >= 3:
        return True
    if lands == 2 and any(n in good_early for n in hand):
        return True
    return False


def mulligan(rng: random.Random):
    # Achado real 2026-09-18 (usuario apontou -- mesma convencao usada
    # em todos os goldfishes manuais dele no Archidekt, "Mulligan (0)"
    # separado de "Keep this"): o 1o mulligan e' GRATIS (compra 7 de
    # novo, mao final continua com 7 cartas) -- so' a partir do 2o
    # mulligan que a punicao real do London Mulligan (bottom N-1 cartas)
    # entra. Antes o codigo aplicava a punicao ja no 1o mulligan.
    mulligans = 0
    while True:
        deck = BASE_LIBRARY[:]
        rng.shuffle(deck)
        hand = deck[:7]
        library = deck[7:]
        if should_keep(hand) or mulligans >= 3:
            penalty = max(0, mulligans - 1)
            for _ in range(penalty):
                worst = min(hand, key=lambda n: CARD_DB[n].mv if n in CARD_DB else 0)
                hand.remove(worst)
                library.insert(0, worst)
            return hand, library, mulligans
        mulligans += 1


def simulate_one(seed: int, turns: int = 8):
    rng = random.Random(seed)
    hand, lib, mulls = mulligan(rng)
    state = GameState(hand=hand, library=lib, mulligans=mulls, rng=rng)
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
    megatron_cast = [s.commander_cast_turn for s in states if s.commander_cast_turn is not None]
    print(f"Turno medio de conjuracao do Megatron: {avg(megatron_cast):.2f} | "
          f"mediana: {sorted(megatron_cast)[len(megatron_cast)//2] if megatron_cast else 0}")
    print(f"Nunca conjurado em {turns} turnos: {100*(n-len(megatron_cast))/n:.1f}%")
    print(f"Avg conversoes do Megatron: {avg([s.megatron_conversions_total for s in states]):.2f}")
    print(f"Avg mana gerada pela conversao do Megatron: {avg([s.megatron_mana_generated_total for s in states]):.2f}")
    print(f"Avg combustivel sacrificado pro Megatron: {avg([s.megatron_fuel_sacrificed_total for s in states]):.2f}")
    print(f"Avg dano/perda-de-vida proxy total (3 oponentes hipoteticos, NUNCA vida real): "
          f"{avg([s.proxy_damage_total for s in states]):.2f}")
    print(f"  -- dos quais via Warstorm Surge: {avg([s.warstorm_surge_damage_total for s in states]):.2f} "
          f"({avg([s.warstorm_surge_triggers_total for s in states]):.2f} gatilhos/partida)")
    print(f"Avg spells/gatilhos de interacao (Path/Swords/Vandalblast/Generous Gift/Bahamut/Noxious "
          f"Gearhulk/Demonic Junker/Cityscape Leveler): {avg([s.interaction_spells_cast_total for s in states]):.2f}")
    print(f"Avg atacantes por partida (soma de todos os combates -- Megatron + todo o resto do "
          f"board pronto, achado real 2026-09-02): {avg([s.attackers_total_all_turns for s in states]):.2f}")
    print(f"Avg vida ganha: {avg([s.proxy_lifegain_total for s in states]):.2f}")
    print(f"Avg cartas compradas extra: {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"  -- dos quais via The Ten Rings (compra a diferenca pra 10 no end step): "
          f"{avg([s.ten_rings_draws_total for s in states]):.2f} draws/partida")
    print(f"Avg conjuracoes gratis via Cosmic Cube: {avg([s.cosmic_cube_free_casts_total for s in states]):.2f}")
    print(f"Avg tokens 3/3 criados via Nexus of Becoming: {avg([s.nexus_tokens_created_total for s in states]):.2f}")
    print(f"Avg ativacoes de haste via Lightning Greaves: "
          f"{avg([s.equip_haste_activations_total for s in states]):.2f}")
    print(f"Avg artefatos devolvidos pra mao via Pia's Revolution: "
          f"{avg([s.pia_revolution_returns_total for s in states]):.2f}")
    print(f"Avg ativacoes de solda (Welder/Scrap Welder/Trash for Treasure/Engineer/Osgir/Daretti): "
          f"{avg([s.weld_activations_total for s in states]):.2f}")
    print(f"Avg criaturas cheatadas pra campo (Sneak Attack/Feldon/Anrakyr/Bygone Colossus warp): "
          f"{avg([s.creatures_cheated_in_total for s in states]):.2f}")
    print(f"Avg eventos de recursao/valor totais: {avg([s.recursion_events_total for s in states]):.2f}")
    print(f"Avg reanimacoes via Portal to Phyrexia (upkeep): "
          f"{avg([s.portal_phyrexia_reanimations_total for s in states]):.2f}")
    print(f"Avg Mega Flares do Summon: Bahamut (capitulo IV): "
          f"{avg([s.bahamut_mega_flare_total for s in states]):.2f}")
    bore = sum(1 for s in states if s.tunnel_grinder_transforms_total > 0)
    print(f"Partidas em que o Brass's Tunnel-Grinder transformou em Tecutlan: {100*bore/n:.1f}%")
    print(f"Avg artefatos sacrificados: {avg([s.artifacts_sacrificed_total for s in states]):.2f} | "
          f"Avg criaturas sacrificadas: {avg([s.creatures_sacrificed_total for s in states]):.2f}")
    print(f"Avg dano via payoff de sacrificio (Ayara/Susur Secundi): "
          f"{avg([s.sacrifice_payoff_damage_total for s in states]):.2f}")
    print(f"Avg compras via payoff de sacrificio (Rakdos/Susur Secundi): "
          f"{avg([s.sacrifice_payoff_draws_total for s in states]):.2f}")
    print(f"Avg tokens Myr via Genesis Chamber: {avg([s.genesis_chamber_tokens_total for s in states]):.2f}")
    print(f"Avg compras via Fountainport: {avg([s.fountainport_draws_total for s in states]):.2f} | "
          f"Avg Fish tokens via Fountainport: {avg([s.fountainport_tokens_total for s in states]):.2f}")
    print(f"Avg compras via Tarrian's Journal: {avg([s.tarrians_journal_draws_total for s in states]):.2f}")
    print(f"Avg loots via Melded Moxite (ETB discard1/draw2): "
          f"{avg([s.melded_moxite_loots_total for s in states]):.2f}")
    print(f"Avg Robot tokens via Melded Moxite (sac {{3}}): "
          f"{avg([s.melded_moxite_tokens_total for s in states]):.2f}")
    print(f"Avg copias baratas via Ultron (rocks/Melded Moxite, MV<3): "
          f"{avg([s.ultron_cheap_copies_total for s in states]):.2f}")
    print(f"Avg Golem tokens via morte do Triplicate Titan: "
          f"{avg([s.triplicate_titan_tokens_total for s in states]):.2f}")
    print(f"Avg remocoes via Demonic Junker (ETB, por oponente): "
          f"{avg([s.demonic_junker_removals_total for s in states]):.2f}")
    chandras = sum(1 for s in states if s.chandras_ignition_casts_total > 0)
    print(f"Partidas em que Chandra's Ignition foi usada como finalizador: {100*chandras/n:.1f}% "
          f"| Avg criaturas proprias perdidas pra ela: {avg([s.chandras_ignition_own_creatures_lost_total for s in states]):.2f}")
    poison_win = sum(1 for s in states if s.blightsteel_poison_win)
    infect_ignition = sum(1 for s in states if s.chandras_ignition_infect_kills_total > 0)
    print(f"Partidas com auto-win via veneno do BlightSteel Colossus (11 de poder >= {POISON_LETHAL} letal, "
          f"atacando OU via Chandra's Ignition): {100*poison_win/n:.1f}% "
          f"(dos quais via combo com Chandra's Ignition: {100*infect_ignition/n:.1f}%)")
    cmd_dmg_win = sum(1 for s in states if s.commander_damage_win)
    print(f"Partidas com auto-win via commander damage (21+ de dano de combate do proprio Megatron "
          f"ao mesmo oponente, CR 903.10a): {100*cmd_dmg_win/n:.1f}% "
          f"| Avg dano de commander acumulado no Megatron: {avg([s.megatron_commander_damage_dealt for s in states]):.2f}")
    print(f"Avg vezes que o Demonic Junker foi crewado (atacou junto com o Megatron): "
          f"{avg([s.demonic_junker_crews_total for s in states]):.2f}")
    print(f"Avg vezes que o Megatron atacou SOZINHO de proposito pro combo com Ironsoul Enforcer "
          f"(reanima artefato do cemiterio ANTES do proprio gatilho de ataque, que o usa como fuel): "
          f"{avg([s.megatron_alone_combos_total for s in states]):.2f}")
    print(f"Avg vida final: {avg([s.life for s in states]):.2f}")
    own_ko = sum(1 for s in states if s.life <= 0)
    print(f"Partidas em que os PROPRIOS efeitos derrubam minha vida a 0 ou menos: {100*own_ko/n:.1f}%")
    print(f"Avg mao final: {avg([len(s.hand) for s in states]):.2f}")
    daretti_ult = sum(1 for s in states if s.daretti_savant_ultimate_active)
    print(f"Daretti, Scrap Savant chegou ao -10 (emblema): {100*daretti_ult/n:.1f}% dos jogos")
    ayara_flip = sum(1 for s in states if s.ayara_transformed)
    print(f"Ayara transformou (Furnace Queen): {100*ayara_flip/n:.1f}% dos jogos")
    return states


def simulate_one_with_interaction(seed: int, turns: int = 8):
    """Mesmo goldfish de `simulate_one`, mas com `try_smart_opponent_
    wipe`/`try_smart_opponent_removal`/`try_smart_opponent_attack`/
    `try_smart_opponent_discard` rodando a cada turno -- ver comentario
    da secao 'Modo opcional de resiliencia' acima. As 4 rolam
    independente (podem disparar todas no mesmo turno, mesmo modelo do
    Archidekt de multiplas categorias de interacao por turno). Wipe roda
    PRIMEIRO de proposito -- representa o "pior turno possivel" do
    oponente pra teste de resiliencia (limpa o board antes de checar
    ataque desbloqueado/remocao/discard), nao uma exigencia de regra
    real (as 4 categorias sao instancias hipoteticas independentes,
    nao uma sequencia obrigatoria). NUNCA chamado por `run_batch`/
    `simulate_one` padrao."""
    rng = random.Random(seed)
    hand, lib, mulls = mulligan(rng)
    state = GameState(hand=hand, library=lib, mulligans=mulls, rng=rng,
                       interaction_rng=random.Random(seed + 999_999))
    turns_played = 0
    is_first = True
    while turns_played < turns:
        play_turn(state, is_first_turn=is_first, on_play=True)
        try_smart_opponent_wipe(state)
        try_smart_opponent_removal(state)
        try_smart_opponent_attack(state)
        try_smart_opponent_discard(state)
        is_first = False
        turns_played += 1
        if state.extra_turns_pending > 0:
            state.extra_turns_pending -= 1
            play_turn(state, is_first_turn=False, on_play=True)
            try_smart_opponent_wipe(state)
            try_smart_opponent_removal(state)
            try_smart_opponent_attack(state)
            try_smart_opponent_discard(state)
            turns_played += 1
    return state


def run_batch_with_interaction(n: int, seed_base: int, turns: int = 8):
    """Batch do modo de resiliencia. Reporta so' as metricas relevantes
    pra "o motor aguenta perder a peca central?" -- nao duplica o
    relatorio inteiro do `run_batch` padrao (esse continua sendo a
    referencia de dano/draw sem oponente)."""
    states = [simulate_one_with_interaction(seed_base + i, turns=turns) for i in range(n)]

    def avg(vals):
        return sum(vals) / len(vals) if vals else 0.0

    print(f"n={n}, seed_base={seed_base}, turns={turns} (MODO RESILIENCIA -- wipe + remocao + ataque inteligente + discard aleatorio de oponente)")
    print(f"Avg board wipes sofridos: {avg([s.smart_wipes_total for s in states]):.2f}")
    wipe_kills = Counter()
    for s in states:
        for _, killed in s.smart_wipe_log:
            for name in killed:
                wipe_kills[name] += 1
    if sum(len(killed) for s in states for _, killed in s.smart_wipe_log):
        avg_kills = avg([len(killed) for s in states for _, killed in s.smart_wipe_log])
        print(f"  -- Avg criaturas perdidas por wipe (quando dispara): {avg_kills:.2f}")
        for name, count in wipe_kills.most_common(5):
            print(f"  -- {name} perdido em wipe em {100*count/n:.1f}% dos jogos")
    print(f"Avg remocoes inteligentes sofridas: {avg([s.smart_removals_total for s in states]):.2f}")
    hit_counts = Counter()
    for s in states:
        for _, target in s.smart_removal_log:
            hit_counts[target] += 1
    for name in INTERACTION_ENGINE_PRIORITY:
        pct = 100 * hit_counts[name] / n
        if pct > 0:
            print(f"  -- {name} removido em {pct:.1f}% dos jogos")
    print(f"Avg ataques de oponente sofridos (perfis variados: Knight/Saproling/Vampire/Zombie/Soldier/Goblin/Elemental): "
          f"{avg([s.smart_attacks_taken_total for s in states]):.2f} | "
          f"Avg bloqueios com sucesso (matou o atacante, sobreviveu): {avg([s.smart_blocks_total for s in states]):.2f}")
    attack_by_type = Counter()
    for s in states:
        for _, name, outcome in s.smart_attack_log:
            attack_by_type[(name, outcome)] += 1
    for token_name, _, _ in OPPONENT_ATTACKER_PROFILES:
        blocked = attack_by_type[(token_name, "blocked")]
        unblocked = attack_by_type[(token_name, "unblocked")]
        if blocked + unblocked > 0:
            print(f"  -- {token_name}: {unblocked} conectaram / {blocked} bloqueados e mortos (em {n} jogos)")
    print(f"Avg descartes forcados sofridos (alvo aleatorio na mao, achado real: Partida #1 "
          f"do goldfish-log.md, Jace's Archivist do oponente): "
          f"{avg([s.smart_discards_total for s in states]):.2f}")
    discard_counts = Counter()
    for s in states:
        for _, card in s.smart_discard_log:
            discard_counts[card] += 1
    for card, count in discard_counts.most_common(5):
        print(f"  -- {card} descartado em {100*count/n:.1f}% dos jogos")
    print(f"Avg dano/perda-de-vida proxy total: {avg([s.proxy_damage_total for s in states]):.2f}")
    print(f"Avg eventos de recursao/valor totais: {avg([s.recursion_events_total for s in states]):.2f}")
    print(f"Avg ativacoes de solda (Welder/Scrap Welder/Trash for Treasure/Engineer/Osgir/Daretti): "
          f"{avg([s.weld_activations_total for s in states]):.2f}")
    print(f"Avg cartas compradas extra: {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"Avg vida final: {avg([s.life for s in states]):.2f}")
    return states


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run_batch(2000, seed_base=1_000_000, turns=8)
