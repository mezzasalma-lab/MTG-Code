# Megatron, Tyrant — Mardu (B/R/W)

**Reconstrução completa 2026-09-02**: o dono real do deck (o oponente citado
nas partidas presenciadas) passou a lista inicial dele. Comparando com o
que tínhamos (montado por frequência entre decklists públicas + primer),
ficou claro que o plano de jogo real é outro: **solda/recupera artefato
(Goblin Welder/Trash for Treasure/Scrap Welder/Scrap Trawler/Daretti x2),
cheat pra campo (Sneak Attack/Anrakyr the Traveller/Feldon of the Third
Path) e `Warstorm Surge` como motor de dano** — não o motor de
"Megatron sacrifica combustível barato todo turno" que tínhamos montado.
Lista reconstruída do zero a partir da dele. Ver `checklist-oraculo.md` e
`goldfish-log.md` para o histórico completo carta a carta.

**Cortes feitos na lista original dele** (8 cartas fracas/redundantes pro
plano de solda/cheat, abrindo espaço pras cartas que o usuário confirmou
ter visto ao vivo + as 2 hexproof que ele pediu): Sojourner's Companion,
Frogmyr Enforcer, Psychotic Fury, Temur Battle Rage, Seize the Spotlight,
Cathartic Reunion, Evendo Brushrazer, Coveted Jewel.

**Adições confirmadas pelo usuário** (vistas ao vivo numa partida real,
ausentes desta lista "inicial" — upgrades feitos depois): Rakdos, the
Muscle; Summon: Bahamut; Osgir, the Reconstructor; Wheel of Fortune;
Phyrexian Triniform; Blasphemous Act. Mais 2 magias de proteção pedidas
à parte: Clever Concealment e Blacksmith's Skill.

**Correção 2026-09-02**: a escolha original pra 1 das 2 magias de
proteção (Shields Up!) era do set Star Trek, que só sai em 2026-11-13 —
ainda não lançado, não é legal em Commander. Usuário pegou o erro.
Trocada primeiro por Loran's Escape (real e legal, mas protege só 1
permanente), depois trocada de novo por pedido direto do usuário pra
**Clever Concealment** (Marvel Super Heroes Commander, 2026-06-26, real
e legal): protege o board inteiro contra wrath ("any number of target
nonland permanents you control phase out"), com Convoke reduzindo o
custo efetivo tapando fodder que já ia ser sacrificado no fim do turno.

**Correção de draw 2026-09-03**: usuário relatou "impressão de que falta
draw" — confirmado pelos números reais do simulador (mão final média
~2,9-3,05 cartas em várias rodadas de 2000+ jogos, só 6 fontes de draw
repetível na lista de 99, nenhum motor recorrente de compra). Comparando
com uma 3ª lista real do arquétipo (~100 cartas, artifact-matters/combo),
foram feitas 2 trocas: **-1 Everflowing Chalice** (rampa redundante — a
lista já tem Sol Ring/Arcane Signet/Mind Stone/Fellwar Stone/Gilded
Lotus/3 Talismans, oito peças de rampa fixa antes dela; Chalice é a mais
fraca, nunca compra carta nenhuma), **-1 Sandstone Oracle** (7 mana por
um draw condicional e inconsistente, obsoleta com draw melhor entrando)
→ **+1 Phyrexian Arena** ({1}{B}{B}, "at the beginning of your upkeep,
draw a card and lose 1 life" — draw repetível de verdade, todo turno,
sem depender de sacrifício), **+1 Cosmic Cube** ({5}, Ward {2}, "whenever
you attack, look at the top six cards of your library, may cast a spell
with mana value ≤ greatest power among attacking creatures without
paying its mana cost" — motor de valor gratuito que também escala com os
finalizadores grandes já em campo, usuário pediu especificamente essa
depois de comparar as 2 listas). Skullclamp descartado por pedido do
próprio usuário: o motor de sacrifício do deck é majoritariamente de
ARTEFATOS (Megatron/Ayara/Susur Secundi), não de criaturas — Skullclamp
não teria outlet rápido o suficiente pra ser confiável aqui, ao contrário
de Phyrexian Arena que não depende de sacrifício nenhum. Ambos
verificados reais/legais em Commander via Scryfall (`released_at`:
2001-06-04 e 2026-06-26 — os 2 já lançados, nenhum caso tipo Shields
Up!).

**Correção 2026-09-03 (2)**: primeira proposta desta rodada cortava
também **Myr Retriever** (achando a recursão duplicada com Junk Diver) e
adicionava **Florian, Voldaren Scion** no lugar do 3º slot — mas o corte
foi feito sem perguntar. Usuário reclamou direto: *"Myr retriever nao
pode sair. Pq vc cortou sem me perguntar?"*. Myr Retriever voltou pra
lista; como resultado, coube só uma adição a menos — usuário escolheu
tirar **Florian, Voldaren Scion** (não o Myr Retriever) pra fechar as
contas em 99 cartas de novo, mantendo Phyrexian Arena e Cosmic Cube.
Lição: cortes de carta precisam de confirmação explícita antes de
implementar, não só as adições.

**Correção 2026-09-04 — validação real via EDHREC**: usuário perguntou
como o Determined Iteration performa no EDHREC pro Megatron — não
aparece em nenhuma das 13 categorias da página (5.333 decks
rastreados). Em compensação, achamos o **Pia's Revolution** como a
enchantment MAIS jogada com esse comandante (41,6% dos decks, muito à
frente do resto). Oráculo: "whenever a nontoken artifact is put into
your graveyard from the battlefield, return that card to your hand
unless target opponent has this enchantment deal 3 damage to them" —
seguro de vida direto pro motor de sacrifício de artefato (fuel do
Megatron, fodder de solda). Corte: cruzamos nossas 66 cartas contra
TODAS as listas do EDHREC pro Megatron pra achar candidatos objetivos
(sem aparecer em lugar nenhum lá E sem histórico de partida real);
usuário escolheu **-1 Altar of the Wretched** (ETB único, sem
repetição) e deixou explícito que Treasure Nabber não sai em hipótese
alguma.

**Terrenos**: mantida a base dele quase toda, com 2 mudanças pedidas —
(1) proporção de básicas rebalanceada pelo peso real de pips (R 59,6% /
B 28,8% / W 11,5% dos símbolos coloridos da lista final — branco é
claramente a cor mais leve, nenhum custo duplo-branco na lista inteira),
saindo de 6 Mountain/12 Plains/6 Swamp pra 14 Mountain/2 Plains/7 Swamp;
(2) as 3 painlands (Battlefield Forge/Caves of Koilos/Sulfurous Springs)
upgradadas pros 3 duals ABUR equivalentes (Plateau/Scrubland/Badlands —
mesmas 2 cores, sem o dano, budget liberado pra proxy) + Adagia,
Windswept Bastion adicionada no lugar de 1 Plains (produz W + duplica
artefato quando "estacionada", ótimo com Metalwork Colossus/Bygone
Colossus/Gearhulks). Susur Secundi, Void Altar já vinha na lista dele,
mantida.

## Comandante

1 Megatron, Tyrant

## Deck

1 Anrakyr the Traveller
1 Arcane Signet
1 Ayara, Widow of the Realm
1 Black Market Connections
1 Blacksmith's Skill
1 Blasphemous Act
1 Brass's Tunnel-Grinder
1 Bygone Colossus
1 Chandra's Ignition
1 Chaos Warp
1 Combustible Gearhulk
1 Cosmic Cube
1 Cursed Mirror
1 Daretti, Rocketeer Engineer
1 Daretti, Scrap Savant
1 Decree of Pain
1 Demand Answers
1 Demonic Junker
1 Faithless Looting
1 Feldon of the Third Path
1 Fellwar Stone
1 Gilded Lotus
1 Goblin Engineer
1 Goblin Welder
1 God-Pharaoh's Statue
1 Heartless Conscription
1 Ironsoul Enforcer
1 Junk Diver
1 Laughing Mad
1 Lightning Greaves
1 Metalwork Colossus
1 Mind Stone
1 Mirrorworks
1 Mishra, Tamer of Mak Fawa
1 Myr Retriever
1 Nexus of Becoming
1 Noxious Gearhulk
1 Osgir, the Reconstructor
1 Path to Exile
1 Phyrexian Arena
1 Phyrexian Triniform
1 Pia's Revolution
1 Portal to Phyrexia
1 Ragavan, Nimble Pilferer
1 Rakdos, the Muscle
1 Saheeli's Directive
1 Scrap Trawler
1 Scrap Welder
1 Clever Concealment
1 Skitterbeam Battalion
1 Sneak Attack
1 Sol Ring
1 Solemn Simulacrum
1 Steel Seraph
1 Summon: Bahamut
1 Swiftfoot Boots
1 Swords to Plowshares
1 Talisman of Conviction
1 Talisman of Hierarchy
1 Talisman of Indulgence
1 The Eternity Elevator
1 Trash for Treasure
1 Treasure Nabber
1 Vandalblast
1 Warstorm Surge
1 Wheel of Fortune

## Terrenos

1 Adagia, Windswept Bastion
1 Ash Barrens
1 Badlands
1 Command Tower
1 Exotic Orchard
1 Forbidden Orchard
14 Mountain
2 Plains
1 Plateau
1 Scrubland
1 Smoldering Marsh
1 Susur Secundi, Void Altar
7 Swamp
