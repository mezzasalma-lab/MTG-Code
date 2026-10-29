"""
Goldfish simulator — Toph, the First Metalbender (Naya, R/G/W)

Construido do zero em 2026-08-22, cobrindo os 16 motores documentados em
`auditoria.md` secao 4, nao so 1 ou 2. Passo 0 (regra de
`references/goldfish-sim-card-rules.md`): varredura mecanica no oraculo
completo achou 43 cartas com gatilho real ("Whenever"/"At the beginning
of"/"When"). Cada uma delas tem o efeito real implementado abaixo — nao
uma tag decorativa — exceto onde a carta depende de um oponente real
(combate, alvo em permanente adversario), documentado explicitamente como
simplificacao em vez de fingir um efeito.

Mecanica central (a razao de earthbend + "artefato/criatura vira terreno"
serem tratados como um so sistema neste script, nao dois separados):
- Toph, the First Metalbender (comandante): artefatos nao-token que voce
  controla sao TAMBEM terrenos.
- Ashaya, Soul of the Wild (se em campo): criaturas nao-token que voce
  controla sao TAMBEM terrenos (Floresta).
- Mycosynth Lattice (se em campo) + Toph: todo permanente vira artefato,
  e por extensao terreno, via a cadeia acima.
- earthbend: transforma um terreno-alvo (real ou virado terreno pelas
  regras acima) numa criatura 0/0 com contadores e haste, ainda terreno.
  O reminder text ("When it dies or is exiled, return it to the
  battlefield tapped") e uma triggered ability real que reage a QUALQUER
  morte/exilio do permanente, inclusive um custo de sacrificio pago pela
  propria carta — Motor #16 da auditoria: qualquer artefato earthbendado
  com gatilho/custo de "morrer" (Stasis Coffin, Ichor Wellspring, Unstable
  Obelisk) fica recorrente em vez de uso unico. Implementado como
  `earthbend_return` flag em cada Permanent + logica central em
  `leave_battlefield()`.

Simplificacoes documentadas (nao inventadas — sao omissoes explicitas):
- Sem combate real contra oponente: nenhuma criatura adversaria, nenhum
  bloqueio. "Ataca" = passou de summoning sickness e o jogador optou por
  atacar; usado so pra disparar gatilhos de ataque (earthbend, contadores),
  nao ha dano/vida de oponente real.
- Cartas cujo efeito so importa contra permanente/spell adversario (Esper
  Sentinel, Haywire Mite mirando algo do oponente, Council's Judgment,
  Krang/Sword of Feast and Famine em combate real, Lightning Greaves,
  Heroic Intervention, Talon Gates phase-out, Oblivion Stone/Ondu Inversion
  como wipe) sao contadas como "disponivel na mao/campo" mas NAO geram
  efeito numerico solo — reportadas em métricas separadas, nunca fingidas.
- Cores de mana: modelo generico de mana total (como os outros simuladores
  desta biblioteca) — o deck tem fixing extenso e documentado (secao 2/4 da
  auditoria), entao nao rastreio pip a pip.
- Nenhum P/T (power/toughness) e' rastreado em lugar nenhum do simulador
  (consequencia direta de nao haver combate real contra oponente) — isso
  significa que anthems de P/T puro (Caretaker's Talent nivel 3: "Creature
  tokens you control get +2/+2") nao tem um numero pra modificar; o nivel
  e' rastreado e concedido de verdade (categoria 13), mas o efeito
  numerico do anthem e' reportado como metrica separada (tokens criados
  com o anthem ativo), nunca fingido como dano/poder real.

Achados reais 2026-08-31 (rodada ampliada do checklist, categorias 10-13
pedidas explicitamente pelo usuario) — ver `goldfish-log.md` pro relato
completo.

CORRIGIDO na sessao de fechamento (2026-08-31, parte 1):
- **Bug fundamental achado durante a auditoria (nao listado pelo
  usuario, achado nesta varredura):** o loop generico de conjuracao do
  `main_phase()` nao excluia cartas `ctype=="land"` — qualquer terreno
  excedente que sobrasse na mao depois do land-drop do turno (mv=0,
  sempre "castable" por `can_cast()`) era `cast_card()`ado como se fosse
  um spell, entrando em campo de graca, ALEM do land-drop normal
  (bypassa a regra de 1 terreno por turno). Corrigido excluindo
  `ctype=="land"` do loop `castables` (as 2 ocorrencias em
  `main_phase()`).
- Urza's Saga: `add()` duplicado sobrescrevia a tag `saga_token` por um
  `set()` vazio. Duplicata removida.

IMPLEMENTADO na sessao seguinte (2026-08-31, parte 2 — itens que tinham
ficado so' DIAGNOSTICADOS na parte 1, agora com codigo real, nao so' tag):
- **Urza's Saga**: engine real de capitulo I/II/III via `saga_chapter`
  (campo dedicado em `Permanent`, ver `urza_saga_advance()`). Capitulo II
  cria Construct 0/0 se sobrar `{2}`; capitulo III busca artefato custo
  0/1 pra campo e sacrifica a Saga (regra 714).
- **Bala Ged Recovery/Sanctuary, Ondu Inversion/Skyruins, Bridgeworks
  Battle/Tanglespan Bridgeworks**: as 3 faces land reais agora entram
  tapped (`enters_tapped`) — Tanglespan Bridgeworks com a escolha real de
  pagar 3 de vida pra entrar destapado (`enters_tapped_payable`, ver
  `play_land()`). MV vestigial da Bala Ged Recovery (3, nunca lido por
  `ctype=="land"`) corrigido pra 0, igual as outras duas.
- **Wrenn and Realmbreaker**: `-2` (mill 3, recupera permanente pra mao)
  implementado de verdade (`wrenn_loyalty_ability()`). `+1` (land vira
  3/3 ate o proximo turno) nao produz numero neste modelo sem combate/PT
  — decisao de escopo, nao bug. `-7` nunca e' alcancado sob a politica
  "-2 todo turno que der" (ver docstring da propria funcao).
- **Caretaker's Talent**: nivel 2 (copia token) e nivel 3 (anthem +2/+2,
  so' o nivel em si — sem PT pra modificar) implementados
  (`caretaker_talent_levelup()`, campo `level` em `Permanent`).
- **Crucible of Worlds / Conduit of Worlds** (`gy_lands`): terreno do
  cemiterio (fetch ja craqueado, unica fonte real de terreno morto neste
  sim) agora pode ser jogado via `play_land()`. A habilidade ATIVADA
  propria do Conduit (`gy_recursion_1turn` — reanima permanente do
  cemiterio, mas trava o resto do turno pra 1 spell so') continua fora
  de escopo: e' uma troca de politica de jogo real (reanimar 1 alvo vs.
  o loop ganancioso de conjurar tudo que der) que precisaria de dados A/B
  dedicados, no padrao ja usado pro `BRISTLY_BILL_RESERVE_POLICY` — nao
  decidida por suposicao.
- **Extra land drop da Dryad of the Ilysian Grove** (achado real nesta
  rodada, nao listado pelo usuario): tag `extra_land_drop` nunca tinha
  dispatch nenhum — `state.extra_land_drops` nunca era incrementado em
  lugar nenhum do arquivo. Corrigido em `play_land()`.
- **Metricas obrigatorias #10** (`run_batch`): ramp/draw ja existiam
  (so' rotuladas agora); interaction, recursion e finisher/lethality sao
  linhas novas, auditaveis, documentadas como proxy onde o efeito real
  depende de mecanica fora do escopo do simulador (oponente real /
  combate real) em vez de omitidas.

Ainda fora de escopo, por decisao explicita (nao omissao):
- Bala Ged Recovery: face sorcery ("Return target card from your
  graveyard to your hand") nao depende de oponente mas exigiria dois
  modos de `ctype` pra uma so' carta — limitacao de arquitetura, ver
  comentario no `CARD_DB`.
- Conduit of Worlds: habilidade ativada de reanimacao (ver acima).
- Wrenn and Realmbreaker: `+1`/`-7` (ver acima).

Revisao completa do oraculo (2026-09-01, pedida explicitamente pelo
usuario: "Revise TODAS as cartas da Toph pelo oraculo completo") — as 100
cartas da lista (99 + comandante) foram buscadas ao vivo via
`POST /cards/collection` da API do Scryfall (nao por memoria) e cruzadas
contra `CARD_DB`/dispatch de verdade. Achados reais corrigidos:
- **Enlightened Tutor** (1 dos 3 Game Changers da lista) estava 100% sem
  implementacao — so' registrada no CARD_DB, tag sem dispatch. Implementada
  ("Search... put that card on top" — vai pro topo da biblioteca, nao mao).
- **Oswald Fiddlebender** tambem 100% sem implementacao (Magical Tinkering
  — sac artefato, tutora artefato de mv+1 pro campo). Implementada.
- **4 terrenos com "enters tapped" condicional nunca checado**: Field of
  the Dead (sempre tapped, sem condicao — faltava a tag inteira), Ba Sing
  Se ("unless you control a basic land"), Canopy Vista/Cinder Glade
  ("unless you control two or more basic lands"). Corrigido em `play_land()`.
- **Stomping Ground/Temple Garden** (shock lands) nunca pagavam o "pay 2
  life or enters tapped" — entravam destapadas de graca. Corrigido
  (generalizado o mecanismo ja usado pra Tanglespan Bridgeworks, com custo
  de vida por carta em `ENTERS_TAPPED_PAYABLE_LIFE`).
- **Fetches** (Arid Mesa/Windswept Heath/Wooded Foothills) nunca pagavam
  "Pay 1 life" ao ativar. Corrigido.
- **Avatar Kyoshi**: gatilho de "beginning of combat" dependia de existir
  algum atacante elegivel ANTES de checar Kyoshi — nunca disparava se ela
  mesma tivesse doenca de invocacao e fosse a unica criatura em campo.
  Faltava tambem o "then untap that land" (mana extra real se o alvo ja
  estava tapped). Ambos corrigidos.
- **Toph, Earthbending Master / Horizon Explorer**: "Whenever YOU attack"
  (gatilho do JOGADOR, com qualquer criatura) estava implementado como se
  fosse "whenever THIS creature attacks" — exigia a propria carta elegivel
  pra atacar (sem doenca de invocacao), sub-contando o gatilho. Corrigido
  pra disparar sempre que o jogador atacou com qualquer coisa.
- **Bristly Bill / Earthbender Ascension (4o contador)**: "put a +1/+1
  counter on TARGET CREATURE" mirava `best_earthbend_target()` — que
  escolhe qualquer TERRENO, nem sempre uma criatura de verdade (alvo
  ilegal). Nova `best_creature_target()` corrige os dois.
- **Felidar Retreat**: modal real e' "criar token" OU "contador em CADA
  criatura", nao "contador em 1 alvo, com token de fallback". Corrigido.
- **Awaken the Woods**: X forcava minimo 1 (token de graca mesmo com 0
  mana extra) e nunca deduzia o custo de X da mana disponivel (mana
  infinita de fato). Corrigido (minimo 0, X pago de verdade).
- **Earth Kingdom General**: "whenever you put +1/+1 counters on a
  creature, gain that much life, once each turn" tinha tag sem dispatch
  nenhum. Implementada via `apply_earthbend()` (cobre a maioria dos
  caminhos de contador do deck; Bristly Bill/Mossborn Hydra
  dobrando/Ozolith ficam fora, decisao de escopo documentada na propria
  funcao).
- **Badgermole Cub**: segunda habilidade ("whenever you tap a creature for
  mana, add an additional G") nunca implementada — so' o earthbend do ETB
  estava. Implementada em `total_mana()` (relevante combinada com Enduring
  Vitality).
- **Fountainport**: {2},{T},sac token: draw a card — decisao de escopo de
  2026-08-28 revertida, implementada agora (as outras 2 habilidades
  ativadas continuam fora, valor menor).
- **Dryad of the Ilysian Grove**: `ctype` registrado como "creature", real
  e' "Enchantment Creature" (zero impacto numerico — `CREATURE_ISH` cobre
  os dois — mas corrigido por precisao).
- 6 `add()` duplicados removidos (Canopy Vista/Field of the Dead/Planar
  Engineering/Windswept Heath/Wooded Foothills/Yavimaya apareciam 2x no
  CARD_DB com dados identicos — inofensivo mas confuso, mesmo padrao de
  limpeza ja aplicado a Urza's Saga/Talon Gates/Bridgeworks Battle em
  rodadas anteriores).

Confirmado correto sem mudanca (verificado contra o oraculo, nao assumido):
Bumi ("whenever BUMI attacks" — auto-ataque de verdade, gate por
elegibilidade continua certo), Bountiful Promenade/Spire Garden ("enters
tapped unless voce tem 2+ oponentes" — sempre verdade numa mesa real de
Commander, default destapado ja estava certo), Great Divide
Guide/Prismatic Omen/Yavimaya (fixacao de cor pura, sem efeito numerico
neste modelo generico — precedente ja estabelecido em 2026-08-28), Strip
Mine (sacrificio pra destruir terreno e' opponent-dependent, sem razao pra
mirar o proprio terreno).

Ainda fora de escopo apos esta revisao (achado real, decisao explicita):
Urza's Saga capitulos ja cobertos; Iron Spider (habilidades ativadas, ja
documentado 2026-08-28); Talon Gates phase-out (sem bom alvo sem
oponente); Fountainport (Fish token + Treasure via {4}, valor menor).

2a passada da mesma revisao (2026-09-01, pedido do usuario "vc fez a
checagem completa?" apos eu ter dado a primeira passada por completa sem
ter verificado clausula por clausula) — a 1a passada tinha comparado
"card existe no dispatch?" mas nao "TODA clausula do oraculo esta no
dispatch?". Reler o dump completo do Scryfall (ja salvo, nao rebuscado)
clausula a clausula achou mais 8 bugs reais, corrigidos:
- **Earthbender Ascension**: ETB tinha SO' o earthbend — faltava "Then
  search your library for a basic land card, put it onto the battlefield
  tapped" (ramp real, 2a metade da propria habilidade).
- **Horizon Explorer / Spelunking**: "Lands you control enter untapped"
  (estatica) nunca implementada — sobrepoe TODAS as condicionais de
  enters-tapped corrigidas nesta e na rodada anterior. Nova
  `resolve_land_enters_tapped()`, fatorada de `play_land()` pra ser
  reusada no ETB do Spelunking tambem.
- **Spelunking**: ETB tinha SO' a compra — faltava "then you may put a
  land card from your hand onto the battlefield" (land extra de graca,
  fora do land-drop do turno).
- **Gruul Turf / Selesnya Sanctuary / Jetmir's Garden**: "This land enters
  tapped" (sem condicao nenhuma) nunca tinha a tag — entravam destapadas
  de graca.
- **Mishra's Bauble**: `state.scheduled_draws` existia e era LIDO no passo
  de compra, mas nunca INCREMENTADO — a propria habilidade ({T},Sac:
  agendar draw) nunca disparava (so' virava mana pro Krark-Clan Ironworks,
  que e' um custo DIFERENTE). Ja documentado como pendente em 2026-08-28,
  ainda sem correcao ate agora.
- **The Ozolith**: so' a METADE "reciclagem" estava implementada
  (contadores vao pro Ozolith quando uma criatura morre); a redistribuicao
  ("beginning of combat: move all counters from The Ozolith onto target
  creature") nunca tinha dispatch — contadores se acumulavam pra sempre
  sem nunca voltar pra uma criatura.
- **Germination Practicum**: "Paradigm" (recast gratuito automatico todo
  primeiro main phase, a partir do turno seguinte ao 1o cast) nunca era
  modelado — so' o efeito do cast inicial existia.
- **combat_dependent** (Skullclamp/Krang/Sword of Feast and Famine) virou
  parte de `INTERACTION_TAGS` — essas 3 cartas nao tinham NENHUM numero
  reportado antes, nem como N/A (violava a mesma regra #10 que motivou a
  metrica de interaction na rodada anterior).

Documentado nesta 2a passada como fora de escopo (achado real, nao
implementado, motivo explicito — nao e' mais uma lista completa, e' o que
sobrou apos os fixes acima):
- **Enduring Vitality**: "when dies, if it was a creature, return it,
  it's an enchantment" (persist) so' e' alcancavel via earthbend+Ashaya
  (a unica forma dela virar alvo de qualquer remocao neste sim) — uma
  combinacao rara (Ashaya em so' ~9% dos jogos) que colidiria com o
  proprio retorno do Motor #16 (2 gatilhos de "retorna ao morrer" na
  mesma morte) — interacao de regras genuinamente complexa (2 replacement/
  return effects simultaneos) pra um caminho raro; risco de bug novo > o
  ganho.
- **Ultron copiando artefato NAO-criatura**: "If the token isn't a
  creature, it becomes a 2/2 Robot Villain creature" — o token copiado
  herda o `ctype` da carta original (nivel de definicao, nao de
  instancia), entao nunca vira criatura de verdade neste modelo. So'
  importa pra alvo de Bristly Bill/gatilhos de ataque numa interacao de
  2a ordem (Ultron + artefato nao-criatura copiado + outro efeito que
  precise dele ser criatura).
- **Mecanismos de custo alternativo** (Overlord of the Hauntwoods
  Impending, Sapling Nursery Affinity for Forests, Springheart Nantuko
  Bestow, Talon Gates of Madara "{4}: put this card from hand onto the
  battlefield", The Great Henge "costs X less, X = greatest power") — o
  modelo usa 1 `mv` fixo por carta (`cast_card()`/`can_cast()`), sem
  suporte a custo variavel/alternativo. Great Henge em particular exigiria
  rastrear P/T (que o simulador deliberadamente nao rastreia, ver
  docstring acima) pra computar a reducao — arquitetura, nao omissao.
- **Liquimetal Coating / Liquimetal Torque**: "{T}: target permanent
  becomes an artifact until end of turn" — conversao TEMPORARIA de tipo
  sem um mecanismo de "reverter no fim do turno" neste modelo (`ctype` e'
  fixo por carta); tambem exigiria decidir QUEM converter e por que
  (Toph so' afeta artefato NAO-token — converter algo pra virar terreno
  via Toph seria o unico uso real aqui, mas so' dura ate o fim do turno).
- **Zuran Orb**: "Sacrifice a land: gain 2 life" nunca ativado — trocar um
  terreno de verdade (recurso escasso, mana permanente) por 2 de vida (sem
  valor real num deck sem oponente aplicando pressao) e' uma jogada
  irracional pra esse deck especificamente (Regra 1, mesmo raciocinio do
  Ondu Inversion/Strip Mine).
- **Strionic Resonator**: implementado so' pra copiar earthbend (nao
  QUALQUER triggered ability, como o oraculo real permite) — decisao de
  escopo pre-existente, mantida: copiar landfall/ETB tambem exigiria uma
  politica nova de "qual gatilho vale mais copiar", nao testada.
- **Teferi's Protection**: vai pro cemiterio em vez de exilada
  (`cast_card()` generico pra instant/sorcery) — zero impacto funcional
  neste modelo (nada aqui distingue cemiterio de exilio pra instant/
  sorcery), corrigido so' seria por completude cosmetica.

**Robustez desta 2a passada:** 20.000 partidas (seeds 8300000–8319999), 0
erros/timeouts. Todas as 5 mecanicas novas confirmadas disparando via
teste direto (nao so' "roda sem erro").

Achado real via PARTIDA MANUAL (2026-09-01, Partida #1 no goldfish-log.md,
nao pela auditoria de oraculo) — corrigido na hora: Gruul Turf/Selesnya
Sanctuary ("return a land you control to its owner's hand", mandatorio)
so' devolviam um terreno quando havia OUTRO alem delas mesmas em campo —
se a bounceland fosse o UNICO terreno na mesa (visto ao vivo no turno 1
da partida), o codigo antigo pulava o bounce inteiro, deixando o terreno
de graca em campo. Regra real: sem outro candidato, ela devolve A SI
MESMA (ainda e' "a land you control"). Corrigido em `apply_etb()` com
fallback pra `perm` quando `others` esta vazio.

Achado real via PARTIDA MANUAL #2 (2026-09-01, goldfish-log.md, turno 5,
visto ao vivo) — corrigido na hora: Ultron copiando um artefato
NAO-criatura (Liquimetal Torque, na partida) nunca fazia o token virar
criatura de verdade. Oraculo real: "If the token isn't a creature, it
becomes a 2/2 Robot Villain creature in addition to its other types." O
`ctype` de uma carta e' compartilhado por TODAS as copias (nivel de
definicao, nao de instancia), entao o token herdava "artifact" sem
nunca virar criatura -- ja tinha sido diagnosticado na 2a passada da
auditoria de oraculo (2026-09-01) como fora de escopo por ser "narrow,
2a ordem", mas apareceu numa partida real, elevando a prioridade.
Corrigido com campo dedicado por instancia `forced_creature` em
`Permanent` (mesmo padrao ja usado por `earthbent` em `is_creature_type()`)
-- setado em `ultron_trigger()` so' quando a carta copiada nao e' criatura
de verdade. Relevante pra alvo do Bristly Bill/Earthbender Ascension
(`best_creature_target`) e gatilhos "whenever you attack" -- sem P/T
rastreado (docstring), o "2/2" em si nao vira um numero manipulavel, so'
o status de criatura muda.

Compilacao final clausula-a-clausula (2026-09-01, pedido direto do
usuario apos a 2a partida manual: "Pra que eu peco pra vc checar tudo se
vc ainda nao compila TODAS AS HABILIDADES?") — as 2 rodadas de auditoria
anteriores comparavam "a carta tem dispatch?", nao "toda FRASE do oraculo
tem dispatch?". As 100 cartas foram quebradas em 189 clausulas
individuais (uma por frase/paragrafo do oraculo real) e cada uma
verificada por grep contra o codigo, nao por memoria -- tabela completa
em `checklist-oraculo.md` (persistente, nao so' neste docstring). Achou
mais 2 bugs reais:
- **Overlord of the Hauntwoods**: "Whenever this permanent enters OR
  ATTACKS, create a tapped Everywhere land token" -- so' a metade ETB
  tinha dispatch (`apply_etb`), a metade "ou ataca" nunca disparava
  nenhuma vez, apesar de ser um motor de terreno repetivel de verdade uma
  vez a criatura em campo. Corrigido em `combat_step()` (auto-ataque, tipo
  Bumi -- nao "whenever you attack" do jogador).
- **Inventors' Fair**: "{4}, {T}, Sacrifice Inventors' Fair: Search your
  library for an artifact card... Activate only if you control three or
  more artifacts" -- so' a metade upkeep (lifegain com 3+ artefatos)
  tinha dispatch; essa 3a habilidade (tutor real, sacrifica o proprio
  terreno) nunca tinha sido implementada NEM documentada como fora de
  escopo -- lacuna pura, achada so' agora. Implementada
  (`inventors_fair_tutor()`, reusa a prioridade do Enlightened Tutor,
  fatorada em `ARTIFACT_TUTOR_PRIORITY`).

Lacunas de DOCUMENTACAO (nao de comportamento -- ja estavam corretas,
so' sem comentario explicito) fechadas na mesma passada: Dryad of the
Ilysian Grove ("every basic land type", fixacao pura, mesmo padrao do
Great Divide Guide/Prismatic Omen/Yavimaya); Springheart Nantuko (sempre
cria o Insect 1/1 de fallback, nunca copia a criatura anexada -- 100%
consequencia do Bestow ja documentado fora de escopo, comentario
adicionado no dispatch); palavras-chave de combate puras sem numero pra
modificar (Avatar Kyoshi hexproof, Earthbending Student/Toph Greatest
Earthbender land creatures vigilance/double strike, Mossborn Hydra
trample, Kodama reach/partner) -- ja cobertas pela premissa geral "sem
combate real, sem P/T rastreado" do topo deste docstring, nunca
precisaram de tratamento individual.

**Robustez desta rodada:** 20.000 partidas (seeds 8700000–8719999), 0
erros/timeouts. Overlord attack trigger e Inventors' Fair tutor testados
isoladamente (nao so' "roda sem erro"). n=3000 de validacao: movimento
pequeno e no sentido esperado (tokens totais 11,59→11,88 pelo Overlord
atacando mais vezes; vida ganha 0,85→0,77 porque Inventors' Fair as
vezes se sacrifica, perdendo o gatilho de upkeep).

"Compile TUDO, SEMPRE" (2026-09-01) -- o usuario cortou explicitamente a
pratica de eu decidir, por conta propria, que uma habilidade "nao vale a
pena" e por isso nunca implementa-la. Pergunta real que motivou a virada:
"com Mycosynth Lattice + Ultron em campo, qq coisa que eu baixar posso
pagar 2 e criar uma copia 2/2?" -- SIM, e ao confirmar isso achei um bug
real: `enter_battlefield()` checava o `ctype` ESTATICO da carta
("artifact"/"artifact_creature") pra decidir se o Ultron dispara, nao
`is_artifact()` (que ja considera Mycosynth Lattice dinamicamente) --
entao sob Mycosynth, baixar uma criatura ou terreno comum NAO disparava
Ultron, quando deveria. Corrigido.

Alem disso, TODAS as clausulas que antes estavam marcadas "📝 fora de
escopo" na `checklist-oraculo.md` por decisao MINHA de valor (nao por
impossibilidade estrutural real) foram implementadas:
- **Iron Spider, Stark Upgrade**: as 2 habilidades ativadas (contador em
  cada artefato-criatura; remove 2 contadores dentre artefatos: draw) --
  nao dependiam de oponente nem de P/T, ficaram de fora sem motivo real.
- **Fountainport**: as 2 habilidades que faltavam (Fish 1/1 via {3}+1 vida;
  Treasure via {4}) -- prioridade real entre as 3 (draw > Treasure > Fish).
- **The Great Henge**: o proxy no proprio ETB virou o gatilho de verdade
  ("whenever a nontoken creature you control enters") -- dispara pra
  QUALQUER criatura nao-token que entrar depois do Henge, nao so' uma vez.
- **Zuran Orb**: ativa quando a vida fica perigosamente baixa (<10) --
  cenario real onde qualquer piloto trocaria terreno por vida, nao mais
  "nunca".
- **Wrenn and Realmbreaker +1/-7**: +1 (terreno vira criatura ate o
  proximo turno, via novo campo `temp_creature_until_turn`) usada quando
  falta alvo real de criatura pro Bristly Bill/Ozolith; -7 (emblema real:
  joga terreno E conjura permanente do cemiterio) alcancavel de verdade
  se a lealdade chegar a 7. Dados honestos: quase nunca disparam nos
  30.000 jogos de robustez -- NAO por decisao minha, mas porque o proprio
  earthbend da Toph ja cria uma criatura real desde o turno 1 quase
  sempre, entao raramente falta alvo. A mecanica esta la, disponivel,
  testada isoladamente -- e' a simulacao que decide que -2 quase sempre
  ganha, nao eu.
- **Liquimetal Coating/Liquimetal Torque**: convertem um permanente
  real (preferencialmente criatura) em artefato-terreno ate o fim do
  turno (`temp_artifact_until_turn`) -- amplia o pool de
  `best_earthbend_target()` pra incluir criaturas reais, soma em
  contagens de terreno/artefato (Metalcraft, Inventors' Fair, thresholds
  de N-terrenos). A 1a versao desta funcao tinha um gatilho
  auto-contraditorio ("falta alvo de criatura" -- mas se falta, tambem
  nao ha criatura pra converter); corrigida pra ativar sempre que houver
  alvo real disponivel.
- **Conduit of Worlds**: reanima permanente do cemiterio (trava o resto
  do turno pra 1 spell so', regra real) -- politica: so' se o alvo for
  reconhecido de alto valor OU a mao nao tiver nada castavel de qualquer
  forma (sem custo de oportunidade real). Novo campo `conduit_lockout`
  respeitado pelo loop guloso principal E pelo emblema do Wrenn -7 (ambos
  contam como "cast a spell").
- **Bala Ged Recovery // Bala Ged Sanctuary**: face sorcery agora
  despachada por nome quando o land-drop do turno ja foi usado (o deck
  ainda prefere ela como terreno na maioria dos jogos, "ja abaixo do piso
  de terrenos") -- a "limitacao de arquitetura" documentada antes nao
  era motivo pra nunca tentar.

**Robustez:** 20.000 partidas (seeds 8800000–8819999), 0 erros/timeouts.
Cada mecanica nova testada isoladamente (Mycosynth+Ultron em ambos os
sentidos, Great Henge, Wrenn +1/-7, Conduit, Bala Ged Recovery, Liquimetal,
Zuran Orb, Iron Spider). n=3000: movimento grande e no sentido esperado --
draw quase dobra (1,59→3,24, Great Henge real + Iron Spider + Conduit +
Bala Ged Recovery), terrenos sobem (9,95→10,94, Liquimetal contando
conversoes), tokens sobem (11,88→14,85, Fountainport completo); Obelisk/
Stasis Coffin/Strionic Resonator CAEM (mais mecanicas competindo pela
mesma mana).

Auditoria oraculo-por-oraculo NOVA rodada (2026-09-14) -- apos as rodadas
anteriores ja terem quebrado as 100 cartas em 189 clausulas individuais
(`checklist-oraculo.md`), essa rodada procurou GAPS que passaram pelas
rodadas anteriores (mesmo criterio "carta tem dispatch?" x "toda clausula
do oraculo real tem dispatch?"). Achados reais, ambos corrigidos:
- **Skullclamp**: so tinha a tag `combat_dependent` (contada em
  `interaction_plays`, sem efeito numerico) -- mas o oraculo ATUAL da
  Scryfall ("Equipped creature gets +1/-1. Whenever equipped creature
  dies, draw two cards. Equip {1}") NAO exige combate: e' um gatilho de
  morte puro, e a antiga habilidade ativada "{T}, Sacrifice: draw 2" que
  motivou a tag original ja nao existe mais (errata de 2023). Implementado
  como um engine real (`skullclamp_activation()`): equipa de preferencia
  um terreno-criatura earthbendado com 1 contador (o +1/-1 derruba a
  resistencia pra 0, SBA mata na hora, compra 2, o Motor#16 devolve o
  terreno tapped de graca no mesmo evento) -- reequipa a cada main phase
  em que o alvo anterior sumiu do campo.
- **Field of the Dead**: o gatilho "7+ terrenos com nomes diferentes ->
  Zombie 2/2" em `landfall_trigger()` era checado INCONDICIONALMENTE
  (fora do loop `for p in battlefield: if p.card.name == ...` que gate
  TODO outro efeito de landfall na mesma funcao) -- criava Zombies mesmo
  em partidas onde Field of the Dead nunca tinha entrado em campo, so por
  causa da contagem geral de nomes distintos de terreno (facil de bater
  com artefatos-terreno da Toph). Corrigido com `has_card(state, "Field
  of the Dead")`, mesmo padrao ja usado por Horizon Explorer/Spelunking.

**Robustez desta rodada:** 20.000 partidas (seeds 9600000-9619999), 0
erros/timeouts. Skullclamp (equipa alvo de 1 contador, SBA mata, compra 2,
Motor#16 devolve) e Field of the Dead (nao dispara sem a carta em campo,
dispara normalmente com ela) testados isoladamente. n=3000, seed 9500000:
draw sobe (Skullclamp real), tokens de Field of the Dead caem levemente
(deixou de disparar em jogos onde a carta nunca chegou ao campo -- correcao
de um falso positivo, nao perda de mecanica real).

REESCRITA DO MOTOR (2026-09-26) -- pedido do usuario: "Faz a varredura
completa de TUDO do deck da Toph". Regra #7 do CLAUDE.md: este bloco NAO
declara nada "completo" -- lista o que foi varrido e o que ficou de fora
(tabela completa por carta/clausula em `checklist-oraculo.md`, secao
2026-09-26). Oraculo das 98 cartas unicas buscado ao vivo (Scryfall
`/cards/collection`) + rulings das 55 cartas que redefinem tipo/mana/
contador (Regra #3).

As auditorias anteriores perguntavam "essa carta tem codigo?". Os achados
desta rodada moravam nos CONCEITOS COMPARTILHADOS, por isso sobreviveram:
- Mana: modelo "total generico - gasto" trocado por mana POR PERMANENTE,
  COM COR (`mana_units`/`pay`). O antigo: todo terreno somava 1 --
  inclusive artefato-terreno da Toph sem habilidade de mana ("They don't
  gain the ability to {T} for mana"); Sol Ring/Great Henge sob a Toph
  caiam de 2 pra 1; mana de Lotus Cobra/Nissa/KCI ia so' pra metrica, nunca
  podia ser gasta; Treasure nunca era sacrificado (mana infinita por
  turno); terreno-criatura da Ashaya tapava no turno em que entrava;
  bounceland dava 1 em vez de 2; o {T} de habilidade (Ba Sing Se, Urza's
  Saga II, Fountainport, Inventors' Fair...) tambem contava como mana; sem
  cor nenhuma. Wrenn/Great Divide Guide/Yavimaya/Prismatic Omen/Dryad eram
  "fixacao pura" -- sob a Toph eles DAO habilidade de mana a artefato-
  terreno. Badgermole Cub dispara pra qualquer criatura tapada pra mana.
  Mycosynth: qualquer mana paga qualquer cor.
- Comandante registrada com mv=3; custo real {1}{R}{G}{W} = 4.
- Fichas eram contador (`create_token` so' somava): agora Permanent de
  verdade -- Treasure/Food/Lander (habilidades proprias), Insect, Zombie,
  Cat Beast, Treefolk, Fish, Construct (+1/+1 por artefato), Forest Dryad
  (terreno-criatura), Everywhere (todo tipo basico), copias (Scute Swarm,
  Ultron, Springheart, Caretaker II). Contam em Metalcraft/Inventors'
  Fair/KCI/Oswald/Felidar/Germination/Enduring Vitality/Skullclamp/Kodama.
- Landfall: a propria fetch nunca disparava landfall; fetch so' buscava
  basico (o oraculo aceita dual tipado); Tannuk/Nissa contavam o 2o
  landfall GLOBAL em vez da 2a resolucao da PROPRIA habilidade; Nissa
  comprava 1 carta qualquer em vez de revelar ate' Elf/Elemental; Tannuk
  nao contava dano (agora dano na mesa, proxy).
- Earthbend: base P/T 0/0; ficha earthbendada nao volta (deixa de existir);
  earthbend 0 mata o terreno (SBA) e ele volta (landfall); Toph Greatest
  Earthbender X = mana GASTA (0 via Kodama); Strionic Resonator copiava o
  earthbend do Earthshape (magica) e do Ba Sing Se (ativada) -- so'
  gatilho pode ser copiado.
- Contadores: Earth Kingdom General so' via earthbend -> agora TODO +1/+1
  (`add_counters`); Bristly Bill dobrava qualquer contador de qualquer
  permanente (inclusive quest counter) -> so' +1/+1 em criatura, e a
  ativacao e' repetivel; Ozolith recebia contador de nao-criatura.
- P/T e combate: "sem P/T rastreado" e "sem combate" estavam marcados 📊
  -- nao sao estruturais (Regra #7 item 2). Agora: P/T real, Great Henge
  com reducao de custo, Sapling Nursery com Affinity for Forests, Caretaker
  III +2/+2, Sword of Feast and Famine (+2/+2 e desvira terrenos no dano),
  Lightning Greaves (haste/shroud), Krang (haste/indestrutivel pros outros
  artefatos-criatura), Toph Greatest (double strike em terreno-criatura),
  vigilance, dano de combate como proxy (sem bloqueio, convencao do repo).
- Turno (Regra #6): so' existia 1 fase principal -- mana do Avatar Kyoshi
  ("then untap that land"), da Sword e do landfall em combate nunca podia
  ser gasta. Agora main1/combate/main2/end step/cleanup (descarte ate 7),
  Paradigm so' na PRIMEIRA fase principal, Wrenn 1x por turno.
- Custos alternativos que nao existiam: Overlord Impending, Springheart
  Bestow, Talon Gates "{4}: put from hand", Jetmir's Garden cycling,
  MDFCs Bridgeworks Battle (pump) e Bala Ged Recovery.
- Kodama: disparava so' pra criatura e se re-disparava em cadeia -> "another
  PERMANENT", nunca o que ele mesmo pos, terreno (valor de mana 0) conta;
  MDFC na mao nao e' "permanent card".
- Skullclamp: 1 equip por fase e so' em terreno com 1 contador -> equip
  repetivel em qualquer criatura de resistencia 1 que valha menos que 2
  cartas (fichas 1/1, Haywire Mite, Esper Sentinel, terreno earthbendado).
- Horizon Explorer: Lander 1x por JOGADOR atacado (ruling) e o Lander
  agora funciona; "lands enter untapped" vale pra todo terreno, inclusive
  o retorno do earthbend e os postos "tapped" por efeito.
- Urza's Saga III: custo de mana {0}/{1} (Esper Sentinel {W} nao entra);
  II ativavel todo turno, inclusive em resposta ao III.
- Wrenn -7 nao pagava lealdade; Iron Spider/Oswald ({T} de criatura)
  ignoravam doenca de invocacao; Germination Practicum e Teferi's
  Protection vao pro exilio (nao cemiterio).
- Resiliencia: Teferi's Protection, Heroic Intervention, Earthshape,
  Sapling Nursery, shroud do Lightning Greaves, indestrutivel do Krang,
  protecao do Stasis Coffin e phase-out do Talon Gates agora respondem de
  verdade a wipe/remocao/ataque (antes: so' contados).
- Remocao sem alvo (Swords/Erode/Council's Judgment) nao e' mais conjurada
  no vazio (gastava mana em nada): fica na mao, contada em
  `interaction_held_turns` (📊 -- alvo de oponente real).

📊 continua estrutural (estado real de oponente): alvo de Swords/Erode/
Council's Judgment/Haywire Mite/Oblivion Stone/Unstable Obelisk (quando
nao ha' terreno proprio pra reciclar)/Strip Mine (sem Crucible); descarte
da Sword; luta do Bridgeworks Battle; Esper Sentinel; lado magica do Ondu
Inversion (wipe sem board de oponente); bloqueio; hexproof da Kyoshi (so'
no MEU turno, quando o modo de resiliencia nao age).
📝 simplificacoes de politica (nao de regra) documentadas no checklist.
"""

import collections
import copy
import json
import random
import re
from dataclasses import dataclass, field
from typing import Optional

# Politica opcional: ativar de verdade as habilidades de sacrificio das
# cartas earthbend-recorrentes (Motor #16), em vez de so earthbenda-las e
# deixa-las paradas. Testada contra o baseline passivo em 2026-08-22 (ver
# goldfish-log.md) -- default True.
RECURRING_ARTIFACT_POLICY = True
RECURRING_TARGETS = ("The Stasis Coffin", "Unstable Obelisk", "Ichor Wellspring", "Mishra's Bauble")

# Qual permanente o earthbend mira primeiro (ver `best_earthbend_target`).
# "broad_artifact" (default, testado 2026-08-22), "narrow", "land_only".
EARTHBEND_TARGET_POLICY = "broad_artifact"

# Ordem de sacrificio por valor (SAC_VALUE) ao escolher o artefato
# earthbendado pro Krark-Clan Ironworks/Oswald. False = ordem do campo.
SAC_VALUE_PRIORITY_POLICY = True

# Kodama of the East Tree: reserva 1 permanente barato na mao pro gatilho.
KODAMA_HOLD_POLICY = True

# Bristly Bill: reservar {3}{G}{G} antes do loop de conjuracao (trade-off
# medido 2026-08-22, default False).
BRISTLY_BILL_RESERVE_POLICY = False

# Quanto MENOR, mais descartavel (sacrificado primeiro pelo KCI/Oswald).
SAC_VALUE = {
    "Lightning Greaves": 0, "Liquimetal Coating": 0, "Skullclamp": 0, "Sword of Feast and Famine": 0,
    "Haywire Mite": 0, "Oblivion Stone": 0, "Conduit of Worlds": 0, "Crucible of Worlds": 0,
    "Mishra's Bauble": 0, "Ichor Wellspring": 0, "The Stasis Coffin": 0, "Unstable Obelisk": 0,
    "Zuran Orb": 0, "Sol Ring": 1, "Arcane Signet": 1, "Mox Opal": 1, "Liquimetal Torque": 1,
    "Strionic Resonator": 2, "Iron Spider, Stark Upgrade": 2, "Esper Sentinel": 2,
    "Krark-Clan Ironworks": 3, "The Ozolith": 3, "Krang, Utrom Warlord": 3, "The Great Henge": 3,
    "Ultron, Artificial Malevolence": 3, "Mycosynth Lattice": 3,
}


# ---------------------------------------------------------------------------
# Card database -- custo, cor, P/T e subtipos do oraculo real (Scryfall ao
# vivo, 2026-09-26), nao de memoria.
# ---------------------------------------------------------------------------

ANY = frozenset("WUBRG")
COLORLESS = frozenset()
COLOR_OF_TYPE = {"Forest": "G", "Mountain": "R", "Plains": "W", "Island": "U", "Swamp": "B"}
BASIC_TYPES = frozenset(COLOR_OF_TYPE)
COMMANDER_IDENTITY = frozenset("RGW")


@dataclass(eq=False)
class Card:
    name: str
    mv: int
    ctype: str  # 'land','artifact','creature','artifact_creature','enchantment',
                # 'enchantment_creature','planeswalker','instant','sorcery'
    tags: frozenset = frozenset()
    generic: int = 0
    pips: tuple = ()               # (("G", 2), ("W", 1))
    power: Optional[int] = None    # None = sem P/T impresso (ou CDA, ex. Ashaya "*")
    toughness: Optional[int] = None
    subtypes: frozenset = frozenset()
    legendary: bool = False
    token: bool = False
    mdfc_front: Optional[str] = None  # MDFC: tipo da face da frente (na mao ela e' esse tipo)
    mdfc_front_mv: int = 0


CARD_DB: dict = {}


def parse_cost(cost: str):
    generic, pips = 0, {}
    for sym in re.findall(r"\{([^}]+)\}", cost or ""):
        if sym.isdigit():
            generic += int(sym)
        elif sym == "X":
            continue
        else:
            pips[sym] = pips.get(sym, 0) + 1
    return generic, tuple(sorted(pips.items()))


def add(name, ctype, cost="", tags=(), pt=None, subtypes=(), legendary=False, token=False,
        mdfc_front=None, mdfc_cost=""):
    generic, pips = parse_cost(cost)
    mv = generic + sum(n for _, n in pips)
    power, toughness = (pt if pt is not None else (None, None))
    front_mv = sum(parse_cost(mdfc_cost)[0:1]) + sum(n for _, n in parse_cost(mdfc_cost)[1]) if mdfc_cost else 0
    CARD_DB[name] = Card(name=name, mv=mv, ctype=ctype, tags=frozenset(tags), generic=generic, pips=pips,
                         power=power, toughness=toughness, subtypes=frozenset(subtypes), legendary=legendary,
                         token=token, mdfc_front=mdfc_front, mdfc_front_mv=front_mv)


COMMANDER = "Toph, the First Metalbender"
# CORRIGIDO 2026-09-26: o CARD_DB registrava a comandante com mv=3 -- custo
# real {1}{R}{G}{W} = 4. Ela era conjurada 1 turno antes do possivel.
add(COMMANDER, "creature", "{1}{R}{G}{W}", {"commander"}, (3, 3), {"Human", "Warrior", "Ally"}, legendary=True)

# --- Terrenos ---------------------------------------------------------------
add("Arid Mesa", "land", tags={"fetch"})
add("Ba Sing Se", "land", tags={"enters_tapped_unless_basic"})
add("Bala Ged Recovery // Bala Ged Sanctuary", "land", tags={"enters_tapped"}, mdfc_front="sorcery", mdfc_cost="{2}{G}")
add("Bountiful Promenade", "land")
add("Bridgeworks Battle // Tanglespan Bridgeworks", "land", tags={"enters_tapped_payable"},
    mdfc_front="sorcery", mdfc_cost="{2}{G}")
add("Canopy Vista", "land", tags={"enters_tapped_unless_2_basics"}, subtypes={"Forest", "Plains"})
add("Cinder Glade", "land", tags={"enters_tapped_unless_2_basics"}, subtypes={"Mountain", "Forest"})
add("Command Tower", "land")
add("Field of the Dead", "land", tags={"enters_tapped"})
add("Forest", "land", subtypes={"Forest"})
add("Fountainport", "land")
add("Gruul Turf", "land", tags={"bounceland", "enters_tapped"})
add("Inventors' Fair", "land", legendary=True)
add("Jetmir's Garden", "land", tags={"enters_tapped", "cycling3"}, subtypes={"Mountain", "Forest", "Plains"})
add("Mountain", "land", subtypes={"Mountain"})
add("Ondu Inversion // Ondu Skyruins", "land", tags={"enters_tapped"}, mdfc_front="sorcery", mdfc_cost="{6}{W}{W}")
add("Plains", "land", subtypes={"Plains"})
add("Selesnya Sanctuary", "land", tags={"bounceland", "enters_tapped"})
add("Snow-Covered Forest", "land", subtypes={"Forest"})
add("Snow-Covered Mountain", "land", subtypes={"Mountain"})
add("Snow-Covered Plains", "land", subtypes={"Plains"})
add("Spire Garden", "land")
add("Stomping Ground", "land", tags={"enters_tapped_payable"}, subtypes={"Mountain", "Forest"})
add("Strip Mine", "land")
add("Talon Gates of Madara", "land", subtypes={"Gate"})
add("Temple Garden", "land", tags={"enters_tapped_payable"}, subtypes={"Forest", "Plains"})
add("Urza's Saga", "land", subtypes={"Urza's", "Saga"})
add("Windswept Heath", "land", tags={"fetch"})
add("Wooded Foothills", "land", tags={"fetch"})
add("Yavimaya, Cradle of Growth", "land", legendary=True)

# --- Artefatos --------------------------------------------------------------
add("Arcane Signet", "artifact", "{2}")
add("Conduit of Worlds", "artifact", "{2}{G}{G}")
add("Crucible of Worlds", "artifact", "{3}")
add("Esper Sentinel", "artifact_creature", "{W}", {"opponent_dependent"}, (1, 1), {"Human", "Soldier"})
add("Haywire Mite", "artifact_creature", "{1}", {"opponent_dependent"}, (1, 1), {"Insect"})
add("Ichor Wellspring", "artifact", "{2}")
add("Iron Spider, Stark Upgrade", "artifact_creature", "{3}", {"vigilance"}, (2, 3), {"Spider", "Hero"}, legendary=True)
add("Krang, Utrom Warlord", "artifact_creature", "{9}", {"haste", "flying", "trample", "indestructible"}, (9, 9),
    {"Utrom", "Robot"}, legendary=True)
add("Krark-Clan Ironworks", "artifact", "{4}")
add("Lightning Greaves", "artifact", "{2}", {"equipment"}, subtypes={"Equipment"})
add("Liquimetal Coating", "artifact", "{2}")
add("Liquimetal Torque", "artifact", "{2}")
add("Mishra's Bauble", "artifact", "{0}")
add("Mox Opal", "artifact", "{0}", legendary=True)
add("Mycosynth Lattice", "artifact", "{6}")
add("Oblivion Stone", "artifact", "{3}", {"wipe_unused"})
add("Skullclamp", "artifact", "{1}", {"equipment"}, subtypes={"Equipment"})
add("Sol Ring", "artifact", "{1}")
add("Strionic Resonator", "artifact", "{2}")
add("Sword of Feast and Famine", "artifact", "{3}", {"equipment"}, subtypes={"Equipment"})
add("The Great Henge", "artifact", "{7}{G}{G}", legendary=True)
add("The Ozolith", "artifact", "{1}", legendary=True)
add("The Stasis Coffin", "artifact", "{3}", legendary=True)
add("Ultron, Artificial Malevolence", "artifact_creature", "{3}", set(), (2, 4), {"Robot", "Villain"}, legendary=True)
add("Unstable Obelisk", "artifact", "{3}")
add("Zuran Orb", "artifact", "{0}")

# --- Criaturas --------------------------------------------------------------
add("Ashaya, Soul of the Wild", "creature", "{3}{G}{G}", set(), None, {"Elemental"}, legendary=True)
add("Avatar Kyoshi, Earthbender", "creature", "{5}{G}{G}{G}", set(), (6, 6), {"Human", "Avatar"}, legendary=True)
add("Badgermole Cub", "creature", "{1}{G}", set(), (2, 2), {"Badger", "Mole"})
add("Bristly Bill, Spine Sower", "creature", "{1}{G}", set(), (2, 2), {"Plant", "Druid"}, legendary=True)
add("Bumi, Eclectic Earthbender", "creature", "{3}{G}{G}", set(), (4, 4), {"Human", "Noble", "Ally"}, legendary=True)
add("Dryad of the Ilysian Grove", "enchantment_creature", "{2}{G}", set(), (2, 4), {"Nymph", "Dryad"})
add("Earth Kingdom General", "creature", "{3}{G}", set(), (2, 2), {"Human", "Soldier", "Ally"})
add("Earthbending Student", "creature", "{2}{G}", set(), (1, 3), {"Human", "Warrior", "Ally"})
add("Enduring Vitality", "enchantment_creature", "{1}{G}{G}", {"vigilance"}, (3, 3), {"Elk", "Glimmer"})
add("Great Divide Guide", "creature", "{1}{G}", set(), (2, 3), {"Human", "Scout", "Ally"})
add("Horizon Explorer", "creature", "{2}{G}", set(), (2, 4), {"Insect", "Scout"})
add("Kodama of the East Tree", "creature", "{4}{G}{G}", {"reach"}, (6, 6), {"Spirit"}, legendary=True)
add("Lotus Cobra", "creature", "{1}{G}", set(), (2, 1), {"Snake"})
add("Mossborn Hydra", "creature", "{2}{G}", {"trample"}, (0, 0), {"Elemental", "Hydra"})
add("Nissa, Resurgent Animist", "creature", "{2}{G}", set(), (3, 3), {"Elf", "Scout"}, legendary=True)
add("Oswald Fiddlebender", "creature", "{1}{W}", set(), (2, 2), {"Gnome", "Artificer"}, legendary=True)
add("Overlord of the Hauntwoods", "enchantment_creature", "{3}{G}{G}", set(), (6, 5), {"Avatar", "Horror"})
add("Scute Swarm", "creature", "{2}{G}", set(), (1, 1), {"Insect"})
add("Springheart Nantuko", "enchantment_creature", "{1}{G}", set(), (1, 1), {"Insect", "Monk"})
add("Tannuk, Memorial Ensign", "creature", "{1}{R}{G}", set(), (2, 4), {"Kavu", "Pilot"}, legendary=True)
add("Tireless Provisioner", "creature", "{2}{G}", set(), (3, 2), {"Elf", "Scout"})
add("Toph, Earthbending Master", "creature", "{3}{G}", set(), (2, 4), {"Human", "Warrior", "Ally"}, legendary=True)
add("Toph, Greatest Earthbender", "creature", "{2}{R}{G}", set(), (3, 3), {"Human", "Warrior", "Ally"}, legendary=True)

# --- Encantamentos / planeswalker ------------------------------------------
add("Caretaker's Talent", "enchantment", "{2}{W}", subtypes={"Class"})
add("Earthbender Ascension", "enchantment", "{2}{G}")
add("Felidar Retreat", "enchantment", "{3}{W}")
add("Prismatic Omen", "enchantment", "{1}{G}")
add("Sapling Nursery", "enchantment", "{6}{G}{G}")
add("Spelunking", "enchantment", "{2}{G}")
add("Sylvan Library", "enchantment", "{1}{G}")
add("Wrenn and Realmbreaker", "planeswalker", "{1}{G}{G}", legendary=True)

# --- Magicas ---------------------------------------------------------------
add("Awaken the Woods", "sorcery", "{G}{G}")          # + {X}
add("Council's Judgment", "sorcery", "{1}{W}{W}", {"opponent_dependent"})
add("Earthshape", "instant", "{2}{W}")
add("Enlightened Tutor", "instant", "{W}")
add("Erode", "instant", "{W}", {"removal"})
add("Germination Practicum", "sorcery", "{3}{G}{G}", subtypes={"Lesson"})
add("Heroic Intervention", "instant", "{1}{G}", {"protection"})
add("Planar Engineering", "sorcery", "{3}{G}")
add("Swords to Plowshares", "instant", "{W}", {"removal"})
add("Teferi's Protection", "instant", "{2}{W}", {"protection"})

# --- Fichas (tokens) -- permanentes de verdade (2026-09-26) -----------------
add("Treasure", "artifact", token=True, subtypes={"Treasure"})
add("Food", "artifact", token=True, subtypes={"Food"})
add("Lander", "artifact", token=True, subtypes={"Lander"})
add("Insect", "creature", token=True, pt=(1, 1), subtypes={"Insect"})
add("Zombie", "creature", token=True, pt=(2, 2), subtypes={"Zombie"})
add("Cat Beast", "creature", token=True, pt=(2, 2), subtypes={"Cat", "Beast"})
add("Treefolk", "creature", tags={"reach"}, token=True, pt=(3, 4), subtypes={"Treefolk"})
add("Fish", "creature", token=True, pt=(1, 1), subtypes={"Fish"})
add("Construct", "artifact_creature", token=True, pt=(0, 0), subtypes={"Construct"})
add("Forest Dryad", "land", token=True, pt=(1, 1), subtypes={"Forest", "Dryad"}, tags={"always_creature"})
add("Everywhere", "land", token=True, subtypes=set(BASIC_TYPES))

LAND_NAMES = {n for n, c in CARD_DB.items() if c.ctype == "land" and not c.token}
ARTIFACT_ISH = {"artifact", "artifact_creature"}
CREATURE_ISH = {"creature", "artifact_creature", "enchantment_creature"}
BASIC_LAND_NAMES = {"Forest", "Mountain", "Plains", "Snow-Covered Forest", "Snow-Covered Mountain", "Snow-Covered Plains"}
ELF_OR_ELEMENTAL = {n for n, c in CARD_DB.items() if not c.token and ({"Elf", "Elemental"} & c.subtypes)}

# Habilidade de mana PROPRIA de cada carta (fora a intrinseca de tipo
# basico de terreno, calculada a parte). Cada item e' uma "unidade" de mana
# (o conjunto de cores que ela pode ser); 1 {T} gera todas as unidades da
# lista. Toph: "Nontoken artifacts you control are lands ... (They don't
# gain the ability to {T} for mana.)" -- artefato-terreno SEM entrada aqui
# nao gera mana, a menos que Wrenn/Great Divide Guide/tipo basico concedam.
_RGW = COMMANDER_IDENTITY
OWN_MANA = {
    "Command Tower": [_RGW], "Arcane Signet": [_RGW],
    "Bountiful Promenade": [frozenset("GW")], "Spire Garden": [frozenset("RG")],
    "Gruul Turf": [frozenset("R"), frozenset("G")], "Selesnya Sanctuary": [frozenset("G"), frozenset("W")],
    "Ba Sing Se": [frozenset("G")], "Bala Ged Recovery // Bala Ged Sanctuary": [frozenset("G")],
    "Bridgeworks Battle // Tanglespan Bridgeworks": [frozenset("G")],
    "Ondu Inversion // Ondu Skyruins": [frozenset("W")],
    "Field of the Dead": [COLORLESS], "Fountainport": [COLORLESS], "Inventors' Fair": [COLORLESS],
    "Strip Mine": [COLORLESS], "Talon Gates of Madara": [COLORLESS], "Urza's Saga": [COLORLESS],
    "Sol Ring": [COLORLESS, COLORLESS], "Unstable Obelisk": [COLORLESS], "Liquimetal Torque": [COLORLESS],
    "The Great Henge": [frozenset("G"), frozenset("G")],
}
# Permanentes cujo {T} tambem serve pra outra habilidade -- so' viram mana
# depois das fontes "so' mana" (prioridade 2 em `gather_packages`).
TAP_ABILITY_CARDS = {"Urza's Saga", "Ba Sing Se", "Fountainport", "Inventors' Fair", "Conduit of Worlds",
                     "Liquimetal Coating", "Liquimetal Torque", "Strionic Resonator", "The Stasis Coffin",
                     "Unstable Obelisk", "Iron Spider, Stark Upgrade", "Strip Mine", "Oblivion Stone",
                     "Mishra's Bauble"}

INTERACTION_TAGS = {"removal", "opponent_dependent", "protection", "wipe_unused"}

FINISHER_CARDS = {"Avatar Kyoshi, Earthbender", "Toph, Earthbending Master", "Krang, Utrom Warlord",
                  "The Great Henge", "Scute Swarm", "Sapling Nursery", "Felidar Retreat", "Mossborn Hydra"}

ARTIFACT_TUTOR_PRIORITY = ("Sol Ring", "The Great Henge", "Skullclamp", "Krark-Clan Ironworks",
                           "Sylvan Library", "Mycosynth Lattice", "Unstable Obelisk", "Mox Opal",
                           "Arcane Signet", "The Ozolith")
# Urza's Saga III: "artifact card with mana cost {0} or {1}" -- CUSTO de
# mana, nao valor de mana (ruling oficial): Esper Sentinel ({W}) nao entra.
SAGA_TUTOR_PRIORITY = ("Sol Ring", "Skullclamp", "Mox Opal", "The Ozolith", "Haywire Mite",
                       "Mishra's Bauble", "Zuran Orb")


# ---------------------------------------------------------------------------
# Game state
# ---------------------------------------------------------------------------

@dataclass(eq=False)
class Permanent:
    card: Card
    tapped: bool = False
    counters: int = 0                 # SO' contadores +1/+1
    quest_counters: int = 0           # Earthbender Ascension
    time_counters: int = 0            # Overlord of the Hauntwoods (impending)
    impending: bool = False
    earthbent: bool = False
    earthbend_return: bool = False
    entered_turn: int = 0
    uid: int = 0
    is_token: bool = False
    saga_chapter: int = 0             # Urza's Saga
    level: int = 1                    # Caretaker's Talent
    forced_creature: bool = False     # Ultron: copia nao-criatura vira 2/2 Robot Villain
    temp_creature_until_turn: Optional[int] = None   # Wrenn +1 (3/3 ate o proximo turno)
    temp_artifact_until_turn: Optional[int] = None   # Liquimetal (ate o fim do turno)
    attached_to: Optional[int] = None  # Equipamento / Springheart com bestow: uid do portador
    bestowed: bool = False
    phased_out: bool = False
    enchantment_only: bool = False    # Enduring Vitality que voltou como encantamento
    put_by_kodama: bool = False
    mana_spent_to_cast: Optional[int] = None
    landfall_resolutions: int = 0     # Tannuk/Nissa: "second time this ability has resolved this turn"
    vigilance_until_turn: Optional[int] = None  # Felidar Retreat modo 2
    indestructible_until_turn: Optional[int] = None  # Heroic Intervention / Earthshape / Sapling
    hexproof_until_turn: Optional[int] = None
    temp_pump: int = 0                # Bridgeworks Battle: +2/+2 ate o fim do turno
    temp_pump_turn: int = -1


@dataclass(eq=False)
class GameState:
    turn: int = 0
    hand: list = field(default_factory=list)
    battlefield: list = field(default_factory=list)
    graveyard: list = field(default_factory=list)
    exile: list = field(default_factory=list)
    library: list = field(default_factory=list)
    mulligans: int = 0
    phase: str = "main1"

    commander_in_play: bool = False
    commander_cast_count: int = 0
    tapped_land_first_plays_total: int = 0   # correcao de 2026-10-05: vezes em que T1/T2 jogou o terreno virado primeiro
    tapped_land_skipped_for_play_total: int = 0   # ... e vezes em que o ensaio mostrou que isso custaria uma jogada e jogou o desvirado

    lands_played_this_turn: int = 0
    extra_land_drops: int = 0
    landfalls_this_turn: int = 0
    floating: list = field(default_factory=list)   # mana no pool (unidades), esvazia a cada fase

    experience_counters: int = 0
    wrenn_loyalty: int = 0
    wrenn_activated_turn: int = 0
    ozolith_counters: int = 0
    scheduled_draws: int = 0
    life_total: int = 40
    life_gained: int = 0
    token_drawn_this_turn: bool = False
    counter_lifegain_this_turn: bool = False
    germination_practicum_active: bool = False
    paradigm_done_turn: int = 0
    spells_cast_this_turn: int = 0
    conduit_lockout: bool = False
    resonator_used_turn: int = 0
    coffin_protected_until: int = 0     # Stasis Coffin: protecao do jogador ate o meu proximo turno
    tp_protected_until: int = 0         # Teferi's Protection
    wrenn_emblem: bool = False

    next_uid: int = 1
    bf_version: int = 0               # invalida o cache de nomes em campo (performance)
    names_key: tuple = ()
    names_cache: dict = field(default_factory=dict)
    attach_cache: dict = field(default_factory=dict)
    any_phased: bool = False

    # metrics --------------------------------------------------------------
    earthbend_applications: int = 0
    earthbend_by_source: dict = field(default_factory=dict)
    motor16_recursions: int = 0
    landfall_triggers_fired: int = 0
    field_of_the_dead_tokens: int = 0
    cards_drawn_extra: int = 0
    mana_generated_extra: int = 0
    kodama_cheats: int = 0
    resonator_copies: int = 0
    bristly_bill_doubles: int = 0
    ozolith_moves: int = 0
    tokens_created: int = 0
    token_cap_hits: int = 0
    scute_swarm_cap_hits: int = 0
    obelisk_activations: int = 0
    coffin_activations: int = 0
    kci_sacrifices_of_recurring: int = 0
    kci_sacrifices_broad: int = 0
    talon_gates_protections: int = 0
    commander_cast_turn: Optional[int] = None
    crucible_land_replays: int = 0
    interaction_plays: int = 0
    interaction_held_turns: int = 0
    first_finisher_turn: Optional[int] = None
    wrenn_minus2_activations: int = 0
    wrenn_plus1_activations: int = 0
    wrenn_ultimate_activations: int = 0
    conduit_reanimations: int = 0
    urza_saga_chapter2_tokens: int = 0
    urza_saga_chapter3_tutors: int = 0
    legend_rule_sacrifices: int = 0
    skullclamp_equip_count: int = 0
    skullclamp_draws: int = 0
    zuran_orb_sacrifices: int = 0
    lander_activations: int = 0
    food_eaten: int = 0
    bestow_casts: int = 0
    springheart_copies: int = 0
    impending_casts: int = 0
    talon_gates_hand_drops: int = 0
    cycled: int = 0
    strip_mine_loops: int = 0
    greaves_equips: int = 0
    sword_untaps: int = 0
    discarded_to_hand_size: int = 0
    combat_damage_proxy_total: int = 0
    commander_damage_dealt: int = 0
    commander_damage_win: bool = False
    table_damage_total: int = 0        # vida total da mesa (3 oponentes x 40 = 120), proxy
    lethal_turn: Optional[int] = None
    spells_cast_total: int = 0
    mana_spent_total: int = 0
    attacks_total: int = 0

    # ---- Modo opcional de resiliencia (2026-09-20) ------------------------
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
    protection_saves_total: int = 0
    protection_log: list = field(default_factory=list)


def mk_perm(state: GameState, name: str, token: bool = False) -> Permanent:
    p = Permanent(card=CARD_DB[name], entered_turn=state.turn, uid=state.next_uid, is_token=token)
    state.next_uid += 1
    return p


def touch(state: GameState):
    """Qualquer mudanca de campo/fase/equipamento invalida o cache de nomes."""
    state.bf_version += 1


def _names(state: GameState) -> dict:
    key = (state.bf_version, len(state.battlefield))
    if state.names_key != key:
        c = {}
        phased = False
        for p in state.battlefield:
            if p.phased_out:
                phased = True
                continue
            c[p.card.name] = c.get(p.card.name, 0) + 1
        att = {}
        for p in state.battlefield:
            if p.attached_to is not None and not p.phased_out:
                att.setdefault(p.attached_to, []).append(p)
        state.names_cache = c
        state.attach_cache = att
        state.names_key = key
        state.any_phased = phased
    return state.names_cache


def attached(state: GameState, perm: Permanent) -> list:
    _names(state)
    return state.attach_cache.get(perm.uid, ())


def bf(state: GameState) -> list:
    """Permanentes que EXISTEM agora (phased-out e' "como se nao existisse")."""
    _names(state)
    if not state.any_phased:
        return list(state.battlefield)
    return [p for p in state.battlefield if not p.phased_out]


def has_card(state: GameState, name: str) -> bool:
    return name in _names(state)


def count_card(state: GameState, name: str) -> int:
    return _names(state).get(name, 0)


def by_uid(state: GameState, uid: Optional[int]) -> Optional[Permanent]:
    if uid is None:
        return None
    return next((p for p in state.battlefield if p.uid == uid), None)


def toph_active(state: GameState) -> bool:
    return has_card(state, COMMANDER)


# ---------------------------------------------------------------------------
# Conceitos compartilhados (Regra #3) -- tipo, P/T, mana, doenca de invocacao
# ---------------------------------------------------------------------------

def is_artifact(perm: Permanent, state: GameState) -> bool:
    if perm.card.ctype in ARTIFACT_ISH:
        return True
    if has_card(state, "Mycosynth Lattice"):
        return True  # "All permanents are artifacts in addition to their other types."
    if perm.temp_artifact_until_turn is not None:
        if state.turn > perm.temp_artifact_until_turn:
            perm.temp_artifact_until_turn = None  # Liquimetal: "until end of turn"
        else:
            return True
    return False


def is_enchantment(perm: Permanent, state: GameState) -> bool:
    return perm.card.ctype in ("enchantment", "enchantment_creature") or perm.enchantment_only


def is_creature_type(perm: Permanent, state: GameState) -> bool:
    if perm.enchantment_only:
        return False  # Enduring Vitality devolvida: "It's an enchantment. (It's not a creature.)"
    if perm.bestowed and perm.attached_to is not None:
        return False  # Springheart Nantuko como Aura
    if perm.impending and perm.time_counters > 0:
        return False  # Overlord: "isn't a creature until the last [time counter] is removed"
    if perm.temp_creature_until_turn is not None and state.turn > perm.temp_creature_until_turn:
        perm.temp_creature_until_turn = None  # Wrenn +1: "until your next turn"
    return (perm.card.ctype in CREATURE_ISH or perm.earthbent or "always_creature" in perm.card.tags
            or perm.forced_creature or perm.temp_creature_until_turn is not None)


def is_land(perm: Permanent, state: GameState) -> bool:
    if perm.card.ctype == "land":
        return True
    if perm.is_token:
        return False  # Toph e Ashaya so' afetam permanentes NAO-TOKEN
    if toph_active(state) and is_artifact(perm, state):
        return True  # Toph: "Nontoken artifacts you control are lands"
    if has_card(state, "Ashaya, Soul of the Wild") and is_creature_type(perm, state):
        return True  # Ashaya: "Nontoken creatures you control are Forest lands"
    return False


def land_types(perm: Permanent, state: GameState) -> set:
    """Tipos basicos de terreno (cada um da' "{T}: Add [cor]" intrinseco).
    Yavimaya: "Each land is a Forest". Prismatic Omen/Dryad: "Lands you
    control are every basic land type". Ashaya: criaturas nao-token sao
    Forest. Everywhere: todo tipo basico."""
    if not is_land(perm, state):
        return set()
    types = set(perm.card.subtypes & BASIC_TYPES)
    if has_card(state, "Yavimaya, Cradle of Growth"):
        types.add("Forest")
    if has_card(state, "Prismatic Omen") or has_card(state, "Dryad of the Ilysian Grove"):
        types |= BASIC_TYPES
    if (has_card(state, "Ashaya, Soul of the Wild") and not perm.is_token
            and perm.card.ctype != "land" and is_creature_type(perm, state)):
        types.add("Forest")
    return types


def is_forest(perm: Permanent, state: GameState) -> bool:
    return "Forest" in land_types(perm, state)


def has_haste(perm: Permanent, state: GameState) -> bool:
    if perm.earthbent:
        return True  # earthbend: "becomes a 0/0 land creature with haste"
    if "haste" in perm.card.tags:
        return True
    if perm.temp_creature_until_turn is not None:
        return True  # Wrenn +1: vigilance, hexproof, haste
    if any(p.card.name == "Lightning Greaves" for p in attached(state, perm)):
        return True
    if (is_artifact(perm, state) and perm.card.name != "Krang, Utrom Warlord"
            and has_card(state, "Krang, Utrom Warlord")):
        return True  # Krang: "Other artifact creatures you control have ... haste"
    return False


def is_sick(perm: Permanent, state: GameState) -> bool:
    """Doenca de invocacao (CR 302.6): so' criaturas, sem haste, que nao
    estao sob meu controle desde o comeco do meu turno mais recente."""
    return (is_creature_type(perm, state) and perm.entered_turn >= state.turn
            and not has_haste(perm, state))


def n_artifacts(state: GameState) -> int:
    return sum(1 for p in bf(state) if is_artifact(p, state))


def n_lands(state: GameState) -> int:
    return sum(1 for p in bf(state) if is_land(p, state))


def base_pt(perm: Permanent, state: GameState):
    if perm.earthbent:
        return 0, 0  # earthbend: base 0/0 (sobrepoe P/T impresso e CDA)
    if perm.temp_creature_until_turn is not None and perm.card.power is None:
        return 3, 3  # Wrenn +1: 3/3 Elemental
    if perm.card.name == "Ashaya, Soul of the Wild":
        n = n_lands(state)
        return n, n
    if perm.card.name == "Construct":
        n = n_artifacts(state)
        return n, n  # "This token gets +1/+1 for each artifact you control" (base 0/0)
    if perm.forced_creature:
        return 2, 2  # Ultron: "becomes a 2/2 Robot Villain"
    if perm.card.power is None:
        return 0, 0
    return perm.card.power, perm.card.toughness


def pt(perm: Permanent, state: GameState):
    p, t = base_pt(perm, state)
    p += perm.counters
    t += perm.counters
    if perm.temp_pump_turn == state.turn:
        p += perm.temp_pump
        t += perm.temp_pump
    for eq in attached(state, perm):
        if eq.attached_to != perm.uid:
            continue
        if eq.card.name == "Sword of Feast and Famine":
            p += 2
            t += 2
        elif eq.card.name == "Skullclamp":
            p += 1
            t -= 1
        elif eq.card.name == "Springheart Nantuko" and eq.bestowed:
            p += 1
            t += 1
    if perm.is_token and has_card(state, "Caretaker's Talent") and is_creature_type(perm, state):
        ct = next((c for c in bf(state) if c.card.name == "Caretaker's Talent" and c.level >= 3), None)
        if ct is not None:
            p += 2
            t += 2  # Caretaker's Talent nivel 3: "Creature tokens you control get +2/+2"
    return p, t


def power(perm: Permanent, state: GameState) -> int:
    return pt(perm, state)[0]


def greatest_power(state: GameState) -> int:
    return max([power(p, state) for p in bf(state) if is_creature_type(p, state)] or [0])


def is_indestructible(perm: Permanent, state: GameState) -> bool:
    if "indestructible" in perm.card.tags:
        return True
    if perm.indestructible_until_turn is not None and perm.indestructible_until_turn >= state.turn:
        return True
    if (is_artifact(perm, state) and is_creature_type(perm, state)
            and perm.card.name != "Krang, Utrom Warlord" and has_card(state, "Krang, Utrom Warlord")):
        return True  # Krang: "Other artifact creatures you control have ... indestructible"
    return False


def has_vigilance(perm: Permanent, state: GameState) -> bool:
    if "vigilance" in perm.card.tags:
        return True
    if perm.temp_creature_until_turn is not None:
        return True
    if perm.vigilance_until_turn == state.turn:
        return True
    if is_land(perm, state) and has_card(state, "Earthbending Student"):
        return True  # "Land creatures you control have vigilance"
    return False


def distinct_land_names(state: GameState) -> int:
    return len({p.card.name for p in bf(state) if is_land(p, state)})


def draw_cards(state: GameState, n: int, log: list, source: str = ""):
    for _ in range(n):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1


def gain_life(state: GameState, n: int, log: list, source: str = ""):
    if state.tp_protected_until >= state.turn:
        return  # Teferi's Protection: "your life total can't change"
    state.life_total += n
    state.life_gained += n


def lose_life(state: GameState, n: int):
    if state.tp_protected_until >= state.turn:
        return
    state.life_total -= n


def deal_table_damage(state: GameState, n: int):
    state.table_damage_total += n


# ---------------------------------------------------------------------------
# Mana -- por permanente, com cor (reescrito 2026-09-26)
# ---------------------------------------------------------------------------
# O modelo antigo era "total generico - gasto": (1) todo terreno somava 1,
# inclusive artefato-terreno da Toph SEM habilidade de mana (a propria Toph
# diz "They don't gain the ability to {T} for mana"), e Sol Ring/Great
# Henge sob Toph caiam de 2 pra 1; (2) mana de landfall (Lotus Cobra/Nissa)
# e do Krark-Clan Ironworks ia so' pra uma metrica, nunca podia ser gasta;
# (3) Treasure nunca era sacrificado -- cada um virava 1 mana por turno pra
# sempre; (4) criatura/terreno-criatura da Ashaya tapava no turno em que
# entrava; (5) Gruul Turf/Selesnya Sanctuary davam 1 em vez de 2; (6) um {T}
# de habilidade (Ba Sing Se, Urza's Saga II, Fountainport...) tambem contava
# como mana; (7) sem cor nenhuma (Prismatic Omen/Yavimaya/Great Divide
# Guide/Wrenn "fixacao pura" -- falso sob a Toph: eles DAO habilidade de
# mana a artefato-terreno, que sem eles nao gera nada).


def mana_units(perm: Permanent, state: GameState) -> list:
    """Unidades que UM {T} deste permanente gera, pela melhor habilidade de
    mana que ele tem agora. [] = nao gera mana agora."""
    if perm.tapped or perm.phased_out or is_sick(perm, state):
        return []
    name = perm.card.name
    options = []
    own = OWN_MANA.get(name)
    if own and not (name == "Urza's Saga" and perm.saga_chapter < 1):
        options.append(list(own))
    if name == "Mox Opal" and n_artifacts(state) >= 3:
        options.append([ANY])  # Metalcraft
    types = land_types(perm, state)
    if types:
        options.append([frozenset(COLOR_OF_TYPE[t] for t in types)])
    land = is_land(perm, state)
    creature = is_creature_type(perm, state)
    if land and has_card(state, "Wrenn and Realmbreaker"):
        options.append([ANY])  # "Lands you control have '{T}: Add one mana of any color.'"
    if has_card(state, "Great Divide Guide") and (land or (creature and "Ally" in perm.card.subtypes)):
        options.append([ANY])  # "Each land and Ally you control has '{T}: Add one mana of any color.'"
    if creature and has_card(state, "Enduring Vitality"):
        options.append([ANY])  # "Creatures you control have '{T}: Add one mana of any color.'"
    if not options:
        return []
    return max(options, key=lambda u: (len(u), sum(len(x) for x in u)))


@dataclass(eq=False)
class Pkg:
    prio: int
    perm: Permanent
    units_col: list   # unidades se aberto pra pagar pip colorido
    units_gen: list   # unidades se aberto pra pagar generico
    kind: str         # "tap" | "treasure" | "kci" | "talon"
    extra_generic_if_col: int = 0  # Talon Gates: "{1}, {T}: Add one mana of any color"


def gather_packages(state: GameState, exclude: set = frozenset()) -> list:
    pkgs = []
    kci = has_card(state, "Krark-Clan Ironworks")
    n_badger = count_card(state, "Badgermole Cub")
    for p in bf(state):
        if p.uid in exclude:
            continue
        name = p.card.name
        if name == "Treasure" and p.is_token and not p.tapped:
            # "{T}, Sacrifice: Add one mana of any color" -- ou KCI: {C}{C}
            pkgs.append(Pkg(4, p, [ANY], [COLORLESS, COLORLESS] if kci else [ANY], "treasure"))
            continue
        units = mana_units(p, state)
        if units and name == "Talon Gates of Madara" and units == [COLORLESS]:
            # "{T}: Add {C}." ou "{1}, {T}: Add one mana of any color." (filtro: custa 1 a mais)
            pkgs.append(Pkg(2, p, [ANY], [COLORLESS], "tap", extra_generic_if_col=1))
            continue
        if units:
            if is_creature_type(p, state) and n_badger:
                # Badgermole Cub: "Whenever you tap a creature for mana, add an additional {G}."
                units = units + [frozenset("G")] * n_badger
            if is_creature_type(p, state):
                prio = 3
            elif name in TAP_ABILITY_CARDS:
                prio = 2
            else:
                prio = 1
            pkgs.append(Pkg(prio, p, units, units, "tap"))
        elif kci and p.is_token and name in ("Food", "Lander"):
            pkgs.append(Pkg(5, p, [COLORLESS, COLORLESS], [COLORLESS, COLORLESS], "kci"))
    return pkgs


def available_mana(state: GameState, exclude: set = frozenset()) -> int:
    return len(state.floating) + sum(len(k.units_gen) for k in gather_packages(state, exclude))


def pay(state: GameState, generic: int, pips: tuple, log: list = None, exclude: set = frozenset(),
        dry: bool = False) -> bool:
    """Paga {generic} + pips. Pips coloridos primeiro (a cor mais escassa
    primeiro), depois generico. Fontes: pool flutuante, depois pacotes por
    prioridade (terreno/rock simples < {T} com outro uso < criatura <
    Treasure < ficha pro KCI). 1 {T} abre todas as unidades daquele
    permanente -- as que sobram ficam flutuando ate o fim da fase."""
    if generic < 0:
        generic = 0
    myco = has_card(state, "Mycosynth Lattice")  # "spend mana as though it were mana of any color"
    floating = list(state.floating)
    pkgs = gather_packages(state, exclude)
    opened = []

    def ok(u, c):
        return myco or c in u

    need = []
    for c, n in pips:
        need += [c] * n

    def supply(c):
        return (sum(1 for u in floating if ok(u, c))
                + sum(sum(1 for u in k.units_col if ok(u, c)) for k in pkgs))
    need.sort(key=supply)

    for c in need:
        cands = [i for i, u in enumerate(floating) if ok(u, c)]
        if not cands:
            best = None
            for k in pkgs:
                if k in opened:
                    continue
                oks = [u for u in k.units_col if ok(u, c)]
                if not oks:
                    continue
                key = (k.prio, min(len(u) for u in oks))
                if best is None or key < best[0]:
                    best = (key, k)
            if best is None:
                return False
            k = best[1]
            opened.append(k)
            floating.extend(k.units_col)
            generic += k.extra_generic_if_col
            cands = [i for i, u in enumerate(floating) if ok(u, c)]
        i = min(cands, key=lambda j: len(floating[j]))
        floating.pop(i)

    for _ in range(generic):
        if not floating:
            best = None
            for k in pkgs:
                if k in opened:
                    continue
                key = (k.prio, sum(len(u) for u in k.units_gen) / max(1, len(k.units_gen)))
                if best is None or key < best[0]:
                    best = (key, k)
            if best is None:
                return False
            opened.append(best[1])
            floating.extend(best[1].units_gen)
        i = min(range(len(floating)), key=lambda j: len(floating[j]))
        floating.pop(i)

    if dry:
        return True
    state.floating = floating
    state.mana_spent_total += generic + len(need)
    for k in opened:
        if k.kind == "tap":
            k.perm.tapped = True
            if k.perm.card.name == "The Great Henge":
                gain_life(state, 2, log, source="The Great Henge ({T}: GG, ganha 2)")
        elif k.kind == "treasure":
            k.perm.tapped = True
            leave_battlefield(state, k.perm, log if log is not None else [], reason="sacrifice")
        elif k.kind == "kci":
            state.kci_sacrifices_broad += 1
            state.mana_generated_extra += 2
            leave_battlefield(state, k.perm, log if log is not None else [], reason="sacrifice")
    return True


def cast_cost(state: GameState, name: str, mode: str = "normal"):
    card = CARD_DB[name]
    generic, pips = card.generic, card.pips
    if card.mdfc_front:
        g, p = parse_cost({"Bala Ged Recovery // Bala Ged Sanctuary": "{2}{G}",
                           "Bridgeworks Battle // Tanglespan Bridgeworks": "{2}{G}",
                           "Ondu Inversion // Ondu Skyruins": "{6}{W}{W}"}[name])
        return g, p
    if name == COMMANDER:
        generic += 2 * state.commander_cast_count  # taxa de comandante
    elif name == "The Great Henge":
        # "costs {X} less, where X is the greatest power among creatures you
        # control" -- so' o generico (ruling); {G}{G} sempre pago.
        generic = max(0, generic - greatest_power(state))
    elif name == "Sapling Nursery":
        # Affinity for Forests: {1} a menos por Forest que voce controla.
        generic = max(0, generic - sum(1 for p in bf(state) if is_forest(p, state)))
    elif name == "Overlord of the Hauntwoods" and mode == "impending":
        generic, pips = parse_cost("{1}{G}{G}")  # Impending 4--{1}{G}{G}
    return generic, pips


def can_cast(state: GameState, name: str, mode: str = "normal") -> bool:
    g, p = cast_cost(state, name, mode)
    return pay(state, g, p, dry=True)


def can_activate(state: GameState, source: Permanent, generic: int, pips: tuple = (), needs_tap: bool = True) -> bool:
    if needs_tap and (source.tapped or source.phased_out or (is_creature_type(source, state) and is_sick(source, state))):
        return False
    return pay(state, generic, pips, dry=True, exclude={source.uid} if needs_tap else frozenset())


def activate(state: GameState, source: Permanent, generic: int, pips: tuple = (), log: list = None,
             needs_tap: bool = True) -> bool:
    if not can_activate(state, source, generic, pips, needs_tap):
        return False
    pay(state, generic, pips, log, exclude={source.uid} if needs_tap else frozenset())
    if needs_tap:
        source.tapped = True
    return True


def add_floating(state: GameState, units: list, source: str = ""):
    state.floating.extend(units)
    state.mana_generated_extra += len(units)


# ---------------------------------------------------------------------------
# Zonas: entrar / sair do campo (Motor #16 mora aqui), fichas reais, SBA
# ---------------------------------------------------------------------------

TOKEN_CAP = 250  # teto do SIMULADOR (Scute Swarm e' exponencial de verdade); contado em token_cap_hits


def create_token(state: GameState, name: str, log: list, tapped: bool = False, copy_of: Optional[str] = None,
                 note: str = "") -> Optional[Permanent]:
    """Ficha de verdade (Permanent), nao mais um contador (Regra #7 item 3:
    ataca, dispara "enters"/"dies", morre em wipe, conta em "you control X")."""
    if len(state.battlefield) >= TOKEN_CAP:
        state.token_cap_hits += 1
        if copy_of == "Scute Swarm":
            state.scute_swarm_cap_hits += 1
        return None
    p = mk_perm(state, copy_of or name, token=True)
    p.tapped = tapped
    if copy_of is not None and CARD_DB[copy_of].ctype not in CREATURE_ISH and note == "ultron":
        p.forced_creature = True  # Ultron: "If the token isn't a creature, it becomes a 2/2 Robot Villain creature"
    state.tokens_created += 1
    enter_battlefield(state, p, log)
    return p


def enter_battlefield(state: GameState, perm: Permanent, log: list):
    name = perm.card.name
    if is_land(perm, state) and (has_card(state, "Horizon Explorer") or has_card(state, "Spelunking")):
        # "Lands you control enter untapped." -- vale pra QUALQUER terreno, inclusive
        # os postos "tapped" por efeito (ruling do Horizon Explorer) e o retorno do earthbend.
        perm.tapped = False
    state.battlefield.append(perm)
    touch(state)
    if name == COMMANDER:
        state.commander_in_play = True
    if name in FINISHER_CARDS and state.first_finisher_turn is None:
        state.first_finisher_turn = state.turn

    # Substituicao "enters with" antes de qualquer gatilho (CR 614.1c/122.6):
    # Mossborn Hydra ja' tem o contador quando o landfall dela mesma (Ashaya)
    # ou o do resto do campo resolve.
    if name == "Mossborn Hydra":
        add_counters(state, perm, 1, log)
    # Landfall e os gatilhos de ETB disparam JUNTOS: o landfall conta mesmo que
    # o ETB tire o proprio terreno do campo (bounceland devolvendo a si mesma).
    if is_land(perm, state):
        landfall(state, perm, log)
    if perm in state.battlefield:
        apply_etb(state, perm, log)
    if "fetch" in perm.card.tags and perm in state.battlefield and not perm.tapped and not perm.earthbent:
        # "{T}, Pay 1 life, Sacrifice this land: Search..." -- quebrada na hora,
        # venha de onde vier (land drop, Crucible, Kodama, Spelunking).
        lose_life(state, 1)
        perm.tapped = True
        leave_battlefield(state, perm, log, reason="sacrifice")
        fetch_search(state, perm.card.name, log)
    kodama_trigger(state, perm, log)
    if perm not in state.battlefield:
        check_sba(state, log)
        return
    if not perm.is_token and is_creature_type(perm, state):
        for _ in range(count_card(state, "The Great Henge")):
            # "Whenever a nontoken creature you control enters, put a +1/+1 counter on it and draw a card."
            add_counters(state, perm, 1, log)
            draw_cards(state, 1, log, source="The Great Henge")
    if not perm.is_token and is_artifact(perm, state):
        ultron_trigger(state, perm, log)
    if perm.is_token and not state.token_drawn_this_turn and has_card(state, "Caretaker's Talent"):
        # "Whenever one or more tokens you control enter, draw a card. This ability triggers only once each turn."
        state.token_drawn_this_turn = True
        draw_cards(state, 1, log, source="Caretaker's Talent")
    if perm.card.legendary and perm in state.battlefield:
        same = [p for p in bf(state) if p.card.name == name]
        if len(same) > 1:
            keep = min(same, key=lambda p: p.uid)
            for dup in same:
                if dup is not keep:
                    state.legend_rule_sacrifices += 1
                    leave_battlefield(state, dup, log, reason="dies")
    check_sba(state, log)


def leave_battlefield(state: GameState, perm: Permanent, log: list, reason: str = "dies"):
    """reason: "dies" (SBA/legend rule), "sacrifice", "destroy" -> vai pro
    cemiterio ("dies"); "exile"; "bounce" (mao). Earthbend: "When it dies OR
    IS EXILED, return it to the battlefield tapped" (so' esses 2 -- ruling);
    ficha deixa de existir fora do campo, entao nunca volta."""
    if perm not in state.battlefield:
        return
    creature = is_creature_type(perm, state)
    was_clamped = any(e.card.name == "Skullclamp" and e.attached_to == perm.uid for e in bf(state))
    state.battlefield.remove(perm)
    touch(state)
    dies = reason in ("dies", "sacrifice", "destroy")
    name = perm.card.name
    for e in state.battlefield:
        if e.attached_to == perm.uid:
            e.attached_to = None
            if e.bestowed:
                e.bestowed = False  # bestow: vira criatura-encantamento, fica em campo
    touch(state)
    if creature and perm.counters > 0:
        for _ in range(count_card(state, "The Ozolith")):
            state.ozolith_counters += perm.counters
            state.ozolith_moves += 1
    if dies and name == "Ichor Wellspring":
        draw_cards(state, 1, log, source="Ichor Wellspring (morre)")
    if dies and name == "Haywire Mite":
        gain_life(state, 2, log, source="Haywire Mite")
    if dies and creature and was_clamped:
        state.skullclamp_draws += 1
        draw_cards(state, 2, log, source="Skullclamp")
        if maybe_resonator(state, log, "skullclamp"):
            draw_cards(state, 2, log, source="Skullclamp (copia Resonator)")
    if perm.is_token:
        return
    if (dies or reason == "exile") and perm.earthbend_return:
        state.motor16_recursions += 1
        back = mk_perm(state, name)
        back.tapped = True
        enter_battlefield(state, back, log)
        return
    if dies and name == "Enduring Vitality" and creature:
        # "When Enduring Vitality dies, if it was a creature, return it ... It's an enchantment."
        back = mk_perm(state, name)
        back.enchantment_only = True
        enter_battlefield(state, back, log)
        return
    if name == COMMANDER:
        state.commander_in_play = False  # CR 903.9a/b: vai pra zona de comando
        return
    if reason == "bounce":
        state.hand.append(name)
    elif reason == "exile":
        state.exile.append(name)
    else:
        state.graveyard.append(name)


def check_sba(state: GameState, log: list):
    while True:
        dead = [p for p in bf(state) if is_creature_type(p, state) and pt(p, state)[1] <= 0]
        if not dead:
            return
        for p in dead:
            leave_battlefield(state, p, log, reason="dies")


def add_counters(state: GameState, perm: Permanent, n: int, log: list):
    """Ponto UNICO de "put +1/+1 counters" (Earth Kingdom General: "Whenever
    you put one or more +1/+1 counters on a creature, you may gain that much
    life. Do this only once each turn." -- antes ligado so' no earthbend)."""
    if n <= 0 or perm not in state.battlefield:
        return
    perm.counters += n
    if (is_creature_type(perm, state) and not state.counter_lifegain_this_turn
            and has_card(state, "Earth Kingdom General")):
        state.counter_lifegain_this_turn = True
        gain_life(state, n, log, source="Earth Kingdom General")


def best_creature_target(state: GameState) -> Optional[Permanent]:
    creatures = [p for p in bf(state) if is_creature_type(p, state)]
    if not creatures:
        return None

    def key(p):
        if p.card.name == "Mossborn Hydra":
            return 0  # landfall dobra os contadores dela
        if p.earthbent and not p.is_token:
            return 1
        if not p.is_token:
            return 2
        return 3
    return min(creatures, key=key)


def best_earthbend_target(state: GameState, amount: int) -> Optional[Permanent]:
    lands = [p for p in bf(state) if is_land(p, state)]
    if not lands:
        return None
    if amount <= 0:
        # Earthbend 0: vira 0/0 e morre na SBA -> volta tapped (landfall de graca).
        # Alvo: um terreno JA tapped, nao-ficha (ficha nao volta), nao-criatura.
        pool = [p for p in lands if not p.is_token and not is_creature_type(p, state)]
        pool.sort(key=lambda p: (not p.tapped, p.card.ctype != "land", p.card.name not in BASIC_LAND_NAMES))
        return pool[0] if pool else None

    def real_creature(p):
        return is_creature_type(p, state) and not p.earthbent and p.card.ctype != "land"

    if EARTHBEND_TARGET_POLICY == "land_only":
        pool = [p for p in lands if p.card.ctype == "land" and not p.earthbent and not p.is_token]
        return pool[0] if pool else next((p for p in lands if not real_creature(p)), lands[0])
    for p in lands:
        if p.card.name in RECURRING_TARGETS and not p.earthbend_return:
            return p
    if EARTHBEND_TARGET_POLICY == "broad_artifact":
        arts = [p for p in lands if p.card.ctype == "artifact" and not p.is_token and not p.earthbent]
        if arts:
            return arts[0]
    fresh = [p for p in lands if not p.earthbent and not real_creature(p) and not p.is_token]
    if fresh:
        return fresh[0]
    already = [p for p in lands if p.earthbent]
    if already:
        return max(already, key=lambda p: p.counters)
    safe = [p for p in lands if not real_creature(p)]
    return safe[0] if safe else lands[0]


def apply_earthbend(state: GameState, amount: int, log: list, source: str, triggered: bool = True,
                    target: Optional[Permanent] = None) -> Optional[Permanent]:
    """"Earthbend N": target land you control becomes a 0/0 land creature
    with haste (base 0/0 sobrepoe P/T impresso). Put N +1/+1 counters on
    it. When it dies or is exiled, return it to the battlefield tapped."""
    target = target or best_earthbend_target(state, amount)
    if target is None:
        return None
    target.earthbent = True
    target.earthbend_return = not target.is_token
    state.earthbend_applications += 1
    state.earthbend_by_source[source] = state.earthbend_by_source.get(source, 0) + 1
    add_counters(state, target, amount, log)
    if triggered and amount >= 2 and maybe_resonator(state, log, "earthbend"):
        apply_earthbend(state, amount, log, source + " (copia Resonator)", triggered=False)
    check_sba(state, log)
    return target


def maybe_resonator(state: GameState, log: list, kind: str) -> bool:
    """Strionic Resonator: "{2}, {T}: Copy target triggered ability you
    control." So' pode copiar GATILHO -- nunca o earthbend do Earthshape
    (magica) nem do Ba Sing Se (ativada). Politica: copia o 1o earthbend
    >=2 ou o gatilho do Skullclamp (compra 2) que aparecer com {2} livre."""
    res = next((p for p in bf(state) if p.card.name == "Strionic Resonator" and not p.tapped), None)
    if res is None:
        return False
    if not activate(state, res, 2, (), log):
        return False
    state.resonator_copies += 1
    return True


def kodama_trigger(state: GameState, perm: Permanent, log: list):
    """"Whenever ANOTHER PERMANENT you control enters, if it wasn't put onto
    the battlefield with this ability, you may put a permanent card with
    equal or lesser mana value from your hand onto the battlefield." Antes
    so' disparava pra criatura e se re-disparava em cadeia."""
    if perm.put_by_kodama:
        return
    for k in [p for p in bf(state) if p.card.name == "Kodama of the East Tree" and p is not perm]:
        # ficha: valor de mana 0; copia (Scute/Ultron/Springheart) tem o do original
        mv = 0 if (perm.is_token and perm.card.token) else perm.card.mv
        cands = [n for n in state.hand
                 if CARD_DB[n].ctype not in ("instant", "sorcery") and not CARD_DB[n].mdfc_front
                 and n != COMMANDER and CARD_DB[n].mv <= mv]
        if not cands:
            continue
        if mv == 0 and any(CARD_DB[n].ctype == "land" for n in cands):
            choice = next(n for n in cands if CARD_DB[n].ctype == "land")
        else:
            choice = max(cands, key=lambda n: (CARD_DB[n].mv, CARD_DB[n].ctype != "land"))
        state.hand.remove(choice)
        state.kodama_cheats += 1
        new = mk_perm(state, choice)
        new.put_by_kodama = True
        if CARD_DB[choice].ctype == "land":
            resolve_land_enters_tapped(state, new, choice)
        enter_battlefield(state, new, log)


def ultron_trigger(state: GameState, perm: Permanent, log: list):
    """"Whenever another nontoken artifact you control enters, you may pay
    {2}. If you do, create a token that's a copy of it." Copia de lendario
    morre na regra do lendario -- nao paga."""
    if perm.card.name == "Ultron, Artificial Malevolence" or perm.card.legendary:
        return
    for _u in [u for u in bf(state) if u.card.name == "Ultron, Artificial Malevolence" and u is not perm]:
        if not pay(state, 2, (), dry=True):
            return
        pay(state, 2, (), log)
        create_token(state, perm.card.name, log, copy_of=perm.card.name, note="ultron")


# ---------------------------------------------------------------------------
# Landfall
# ---------------------------------------------------------------------------

def landfall(state: GameState, land: Permanent, log: list):
    state.landfalls_this_turn += 1
    state.landfall_triggers_fired += 1
    for p in list(bf(state)):
        if p not in state.battlefield or p.phased_out:
            continue
        name = p.card.name
        if name == "Lotus Cobra":
            add_floating(state, [ANY], "Lotus Cobra")
        elif name == "Nissa, Resurgent Animist":
            add_floating(state, [ANY], "Nissa")
            p.landfall_resolutions += 1
            if p.landfall_resolutions == 2:
                nissa_reveal(state, log)
        elif name == "Tireless Provisioner":
            n_treasure = sum(1 for x in bf(state) if x.card.name == "Treasure")
            create_token(state, "Treasure" if n_treasure < 3 else "Food", log)
        elif name == "Bristly Bill, Spine Sower":
            t = best_creature_target(state)
            if t is not None:
                add_counters(state, t, 1, log)
        elif name == "Mossborn Hydra":
            add_counters(state, p, p.counters, log)  # "double the number of +1/+1 counters"
        elif name == "Tannuk, Memorial Ensign":
            deal_table_damage(state, NUM_OPPONENTS)  # "1 damage to each opponent"
            p.landfall_resolutions += 1
            if p.landfall_resolutions == 2:
                draw_cards(state, 1, log, source="Tannuk (2a resolucao)")
        elif name == "Toph, Earthbending Master":
            state.experience_counters += 1
        elif name == "Earthbender Ascension":
            p.quest_counters += 1
            if p.quest_counters >= 4:
                t = best_creature_target(state)
                if t is not None:
                    add_counters(state, t, 1, log)
        elif name == "Scute Swarm":
            if n_lands(state) >= 6:
                create_token(state, "Scute Swarm", log, copy_of="Scute Swarm")
            else:
                create_token(state, "Insect", log)
        elif name == "Sapling Nursery":
            create_token(state, "Treefolk", log)
        elif name == "Springheart Nantuko":
            host = by_uid(state, p.attached_to) if p.bestowed else None
            if host is not None and pay(state, 1, (("G", 1),), dry=True):
                pay(state, 1, (("G", 1),), log)
                state.springheart_copies += 1
                create_token(state, host.card.name, log, copy_of=host.card.name)
            else:
                create_token(state, "Insect", log)
        elif name == "Felidar Retreat":
            creatures = [c for c in bf(state) if is_creature_type(c, state)]
            if len(creatures) >= 2:
                for c in creatures:
                    add_counters(state, c, 1, log)
                    c.vigilance_until_turn = state.turn
            else:
                create_token(state, "Cat Beast", log)
        elif name == "Field of the Dead":
            if distinct_land_names(state) >= 7:
                state.field_of_the_dead_tokens += 1
                create_token(state, "Zombie", log)


def nissa_reveal(state: GameState, log: list):
    """"reveal cards from the top of your library until you reveal an Elf or
    Elemental card. Put that card into your hand and the rest on the bottom
    in a random order." (antes: comprava 1 carta qualquer)."""
    revealed = []
    while state.library:
        c = state.library.pop(0)
        if c in ELF_OR_ELEMENTAL:
            state.hand.append(c)
            state.cards_drawn_extra += 1
            break
        revealed.append(c)
    state.library.extend(revealed)  # 📝 ordem "aleatoria" -> ordem revelada (deterministico)


# ---------------------------------------------------------------------------
# ETB
# ---------------------------------------------------------------------------

def apply_etb(state: GameState, perm: Permanent, log: list):
    name = perm.card.name
    if name == "Badgermole Cub":
        apply_earthbend(state, 1, log, "Badgermole Cub (ETB)")
    elif name == "Bumi, Eclectic Earthbender":
        apply_earthbend(state, 1, log, "Bumi (ETB)")
    elif name == "Earth Kingdom General":
        apply_earthbend(state, 2, log, "Earth Kingdom General (ETB)")
    elif name == "Earthbending Student":
        apply_earthbend(state, 2, log, "Earthbending Student (ETB)")
    elif name == "Earthbender Ascension":
        apply_earthbend(state, 2, log, "Earthbender Ascension (ETB)")
        basics = [n for n in state.library if n in BASIC_LAND_NAMES]
        if basics:
            state.library.remove(basics[0])
            b = mk_perm(state, basics[0])
            b.tapped = True
            enter_battlefield(state, b, log)
    elif name == "Toph, Greatest Earthbender":
        # "earthbend X, where X is the amount of mana spent to cast her" -- 0 se
        # entrou sem ser conjurada (Kodama).
        apply_earthbend(state, perm.mana_spent_to_cast or 0, log, "Toph Greatest Earthbender (ETB)")
    elif name == "Spelunking":
        draw_cards(state, 1, log, source="Spelunking")
        lands = [n for n in state.hand if n in LAND_NAMES]
        if lands:
            choice = pick_land_to_play(state, lands)
            state.hand.remove(choice)
            lp = mk_perm(state, choice)
            resolve_land_enters_tapped(state, lp, choice)
            enter_battlefield(state, lp, log)
    elif name == "Ichor Wellspring":
        draw_cards(state, 1, log, source="Ichor Wellspring (ETB)")
    elif name == "Overlord of the Hauntwoods":
        create_token(state, "Everywhere", log, tapped=True)
    elif name in ("Gruul Turf", "Selesnya Sanctuary"):
        bounceland_return(state, perm, log)
    elif name == "Wrenn and Realmbreaker":
        state.wrenn_loyalty = 4
    elif name == "Urza's Saga":
        perm.saga_chapter = 1
    elif name == "Talon Gates of Madara":
        talon_gates_phase_out(state, perm, log)


def bounceland_return(state: GameState, perm: Permanent, log: list):
    """"When this land enters, return a land you control to its owner's hand"
    (mandatorio; sem outro terreno, volta ela mesma). Escolha: terreno de
    verdade ja' tapped (a mana dele ja foi usada), basico de preferencia --
    nunca artefato-terreno da Toph nem terreno earthbendado/ficha."""
    others = [p for p in bf(state) if is_land(p, state) and p is not perm]
    good = [p for p in others if p.card.ctype == "land" and not p.is_token and not p.earthbent
            and p.card.name != "Urza's Saga" and "bounceland" not in p.card.tags]
    if good:
        good.sort(key=lambda p: (not p.tapped, p.card.name not in BASIC_LAND_NAMES))
        target = good[0]
    elif others:
        target = min(others, key=lambda p: (p.is_token, p.card.ctype != "land"))
    else:
        target = perm
    leave_battlefield(state, target, log, reason="bounce")


def talon_gates_phase_out(state: GameState, perm: Permanent, log: list):
    """"When this land enters, up to one target creature phases out." No
    goldfish nao ha' o que evitar -- nenhum alvo (fase fora so' tiraria a
    criatura do meu proprio turno). No modo de resiliencia protege a peca-motor
    criatura quando a entrada acontece depois do combate / fora do meu turno
    (fica fora ate' o meu proximo untap)."""
    if state.interaction_rng is None or state.phase == "main1":
        return
    prio = [COMMANDER] + list(INTERACTION_ENGINE_PRIORITY)
    target = None
    for n in prio:
        target = next((p for p in bf(state) if p.card.name == n and is_creature_type(p, state)), None)
        if target:
            break
    if target is None:
        return
    target.phased_out = True
    for e in state.battlefield:
        if e.attached_to == target.uid:
            e.phased_out = True
    touch(state)
    state.talon_gates_protections += 1


# ---------------------------------------------------------------------------
# Terrenos
# ---------------------------------------------------------------------------

FETCH_TYPES = {
    "Arid Mesa": {"Mountain", "Plains"},
    "Windswept Heath": {"Forest", "Plains"},
    "Wooded Foothills": {"Mountain", "Forest"},
}
ENTERS_TAPPED_PAYABLE_LIFE = {"Stomping Ground": 2, "Temple Garden": 2,
                              "Bridgeworks Battle // Tanglespan Bridgeworks": 3}


def resolve_land_enters_tapped(state: GameState, perm: Permanent, name: str):
    tags = CARD_DB[name].tags
    if "enters_tapped" in tags:
        perm.tapped = True
    elif "enters_tapped_payable" in tags:
        if has_card(state, "Horizon Explorer") or has_card(state, "Spelunking"):
            return  # entra destapado de graca -- nao paga vida
        if state.life_total > 10:
            lose_life(state, ENTERS_TAPPED_PAYABLE_LIFE[name])
        else:
            perm.tapped = True
    elif "enters_tapped_unless_basic" in tags:
        if not any(is_land(p, state) and p.card.name in BASIC_LAND_NAMES for p in bf(state)):
            perm.tapped = True
    elif "enters_tapped_unless_2_basics" in tags:
        if sum(1 for p in bf(state) if is_land(p, state) and p.card.name in BASIC_LAND_NAMES) < 2:
            perm.tapped = True


def color_sources(state: GameState, c: str) -> int:
    return sum(1 for p in bf(state) for u in mana_units(p, state)[:1] if c in u)


def _land_tapped_now(state: GameState, n: str) -> bool:
    """O terreno `n` entraria virado agora? (extraido de `pick_land_to_play` sem mudar a regra)"""
    t = CARD_DB[n].tags
    if has_card(state, "Horizon Explorer") or has_card(state, "Spelunking"):
        return False
    if "enters_tapped" in t:
        return True
    if "enters_tapped_unless_basic" in t:
        return not any(p.card.name in BASIC_LAND_NAMES for p in bf(state))
    if "enters_tapped_unless_2_basics" in t:
        return sum(1 for p in bf(state) if p.card.name in BASIC_LAND_NAMES) < 2
    return False


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
    return _land_tapped_now(state, name)


def _tl_develop(sim, log: list):
    """Fase de conjuracao pre-combate do turno: a mesma sequencia que o turno roda logo depois de `play_land`."""
    main_phase(sim, log, True)


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
        pass   # em Toph `play_land` faz parte de `main_phase(first=True)`: o ensaio roda a fase inteira com o terreno imposto
        _tl_develop(sim, [])
    finally:
        _TL_FORCED, _TL_BUSY = None, False
        random.setstate(saved)
    saiu = ficam - collections.Counter(sim.hand)
    return sum(CARD_DB[c].mv for c in saiu.elements() if c in CARD_DB)


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
    mv_virado, mv_desvirado = _tl_dry_run_mv(state, tapped[0]), _tl_dry_run_mv(state, untapped[0])
    if TAPPED_LAND_FIRST_GHOST:
        return default
    if mv_virado >= mv_desvirado:
        state.tapped_land_first_plays_total += 1
        return tapped[0]
    state.tapped_land_skipped_for_play_total += 1
    return untapped[0]


def pick_land_to_play(state: GameState, lands: list) -> str:
    fetches = [n for n in lands if "fetch" in CARD_DB[n].tags]
    if fetches:
        return fetches[0]  # 2 landfalls (a propria fetch + o que ela busca)
    def key(n):
        bounce = "bounceland" in CARD_DB[n].tags
        return (bounce and not any(p.card.ctype == "land" for p in bf(state)), _land_tapped_now(state, n), bounce)
    pool = sorted(lands, key=key)   # estavel: pool[0] == min(lands, key=key), o comportamento antigo
    if TAPPED_LAND_FIRST_ENABLED and not any(p.card.ctype == "land" for p in bf(state)):
        # bounceland sem outro terreno em campo devolve a si mesmo: nao e' candidato a 'jogar o virado primeiro'
        pool = [n for n in pool if "bounceland" not in CARD_DB[n].tags] or pool
    return tapped_first_pick(state, pool)


def fetch_search(state: GameState, fetch_name: str, log: list):
    """"Search your library for a Mountain or Plains card" -- qualquer carta
    com esse TIPO: basico ou nao-basico tipado (Cinder Glade, Jetmir's
    Garden, Stomping Ground, Canopy Vista, Temple Garden). Prefere basico da
    cor mais escassa (destapado, afina o deck); senao o dual tipado."""
    types = FETCH_TYPES[fetch_name]
    pool = [n for n in state.library if CARD_DB[n].ctype == "land" and (CARD_DB[n].subtypes & types)]
    if not pool:
        return
    basics = [n for n in pool if n in BASIC_LAND_NAMES]
    if basics:
        choice = min(basics, key=lambda n: color_sources(state, COLOR_OF_TYPE[next(iter(CARD_DB[n].subtypes & BASIC_TYPES))]))
    else:
        choice = pool[0]
    state.library.remove(choice)
    lp = mk_perm(state, choice)
    resolve_land_enters_tapped(state, lp, choice)
    enter_battlefield(state, lp, log)


def land_drops_allowed(state: GameState) -> int:
    # Dryad of the Ilysian Grove: "You may play an additional land on each of your turns." (cumulativa)
    return 1 + state.extra_land_drops + count_card(state, "Dryad of the Ilysian Grove")


def play_land(state: GameState, log: list):
    while state.lands_played_this_turn < land_drops_allowed(state):
        lands_in_hand = [n for n in state.hand if n in LAND_NAMES]
        from_gy = False
        if lands_in_hand:
            choice = pick_land_to_play(state, lands_in_hand)
        elif has_card(state, "Crucible of Worlds") or has_card(state, "Conduit of Worlds") or state.wrenn_emblem:
            gy_lands = [n for n in state.graveyard if n in LAND_NAMES]
            if not gy_lands:
                return
            choice = pick_land_to_play(state, gy_lands)
            from_gy = True
        else:
            return
        if from_gy:
            state.graveyard.remove(choice)
            state.crucible_land_replays += 1
        else:
            state.hand.remove(choice)
        state.lands_played_this_turn += 1
        lp = mk_perm(state, choice)
        resolve_land_enters_tapped(state, lp, choice)
        enter_battlefield(state, lp, log)  # landfall da propria fetch (antes: nunca disparava); quebra em enter_battlefield


# ---------------------------------------------------------------------------
# Conjuracao
# ---------------------------------------------------------------------------

HELD_SPELLS = {"Council's Judgment", "Swords to Plowshares", "Erode",   # 📊 alvo de oponente
               "Heroic Intervention", "Teferi's Protection",           # resposta (resiliencia)
               "Earthshape", "Enlightened Tutor",                      # instantaneo: fim do turno
               "Awaken the Woods"}                                     # X: por ultimo, com o que sobrar


def cast_spell(state: GameState, name: str, log: list, mode: str = "normal", from_zone: str = "hand",
               x: int = 0) -> bool:
    g, p = cast_cost(state, name, mode)
    g += x
    if not pay(state, g, p, dry=True):
        return False
    spent_before = state.mana_spent_total
    pay(state, g, p, log)
    spent = state.mana_spent_total - spent_before
    state.spells_cast_this_turn += 1
    state.spells_cast_total += 1
    card = CARD_DB[name]
    if card.tags & INTERACTION_TAGS:
        state.interaction_plays += 1
    if from_zone == "hand":
        state.hand.remove(name)
    elif from_zone == "graveyard":
        state.graveyard.remove(name)
    if name == COMMANDER:
        state.commander_cast_count += 1
        if try_smart_opponent_counter(state):
            return True  # anulada: mana e taxa ja' contam (CR 903.10a conta "cast")
        if state.commander_cast_turn is None:
            state.commander_cast_turn = state.turn
    if card.ctype in ("instant", "sorcery") or card.mdfc_front:
        resolve_instant_sorcery(state, name, log, x)
        if name in ("Teferi's Protection", "Germination Practicum"):
            state.exile.append(name)  # "Exile Teferi's Protection" / Paradigm
        elif name != COMMANDER:
            state.graveyard.append(name)
        return True
    perm = mk_perm(state, name)
    perm.mana_spent_to_cast = spent
    if mode == "impending":
        perm.impending = True
        perm.time_counters = 4
        state.impending_casts += 1
    if mode == "bestow":
        host = best_bestow_host(state)
        if host is not None:
            perm.bestowed = True
            perm.attached_to = host.uid
            state.bestow_casts += 1
    enter_battlefield(state, perm, log)
    return True


BESTOW_VALUE = ("Scute Swarm", "Earthbending Student", "Earth Kingdom General", "Badgermole Cub",
                "Lotus Cobra", "Tireless Provisioner", "Mossborn Hydra", "Great Divide Guide",
                "Horizon Explorer", "Springheart Nantuko")


def best_bestow_host(state: GameState) -> Optional[Permanent]:
    """Springheart Nantuko com bestow: landfall paga {1}{G} e cria copia da
    criatura encantada. Copia de lendaria morre (regra do lendario) -- so'
    nao-lendarias com valor de copia (ETB de earthbend, landfall, mana)."""
    for n in BESTOW_VALUE:
        host = next((p for p in bf(state) if p.card.name == n and is_creature_type(p, state)
                     and not p.card.legendary), None)
        if host is not None:
            return host
    return None


def resolve_instant_sorcery(state: GameState, name: str, log: list, x: int = 0):
    if name == "Awaken the Woods":
        for _ in range(x):
            create_token(state, "Forest Dryad", log)  # land creature -> landfall por ficha
    elif name == "Enlightened Tutor":
        pool = [n for n in state.library if CARD_DB[n].ctype in ARTIFACT_ISH
                or CARD_DB[n].ctype in ("enchantment", "enchantment_creature")]
        if pool:
            found = next((n for n in ARTIFACT_TUTOR_PRIORITY if n in pool), None) or max(pool, key=lambda n: CARD_DB[n].mv)
            state.library.remove(found)
            state.library.insert(0, found)
    elif name == "Planar Engineering":
        sac_lands_for(state, 2, log)
        for _ in range(4):
            found = next((c for c in state.library if c in BASIC_LAND_NAMES), None)
            if found is None:
                break
            state.library.remove(found)
            b = mk_perm(state, found)
            b.tapped = True
            enter_battlefield(state, b, log)
    elif name == "Germination Practicum":
        for c in [c for c in bf(state) if is_creature_type(c, state)]:
            add_counters(state, c, 2, log)
        state.germination_practicum_active = True
        state.paradigm_done_turn = state.turn
    elif name == "Earthshape":
        land = apply_earthbend(state, 3, log, "Earthshape (instant)", triggered=False)
        if land is not None:
            lp = power(land, state)
            for c in bf(state):
                if is_creature_type(c, state) and power(c, state) <= lp:
                    c.indestructible_until_turn = state.turn
                    c.hexproof_until_turn = state.turn
    elif name == "Bala Ged Recovery // Bala Ged Sanctuary":
        target = next((n for n in ARTIFACT_TUTOR_PRIORITY if n in state.graveyard), None)
        if target is None:
            nonland = [n for n in state.graveyard if n not in LAND_NAMES]
            target = max(nonland, key=lambda n: CARD_DB[n].mv) if nonland else (state.graveyard[0] if state.graveyard else None)
        if target is not None:
            state.graveyard.remove(target)
            state.hand.append(target)
    elif name == "Bridgeworks Battle // Tanglespan Bridgeworks":
        # "+2/+2 until end of turn. It fights up to one target creature you don't control." (luta 📊)
        t = best_attacker(state)
        if t is not None:
            t.temp_pump = 2
            t.temp_pump_turn = state.turn
    elif name == "Teferi's Protection":
        teferis_protection(state, log)
    elif name == "Heroic Intervention":
        for c in bf(state):
            c.indestructible_until_turn = state.turn
            c.hexproof_until_turn = state.turn


def sac_lands_for(state: GameState, n: int, log: list):
    """Planar Engineering ("Sacrifice two lands"): terreno earthbendado
    primeiro (volta), depois terreno de verdade ja' tapped; nunca
    artefato-terreno que nao volta."""
    lands = [p for p in bf(state) if is_land(p, state)]
    def key(p):
        if p.earthbend_return:
            return (0, not p.tapped)
        if p.card.ctype == "land":
            return (1 if p.card.name in BASIC_LAND_NAMES else 2, not p.tapped)
        return (3, 0)
    for p in sorted(lands, key=key)[:n]:
        leave_battlefield(state, p, log, reason="sacrifice")


def castable_names(state: GameState, held: Optional[str]) -> list:
    out = []
    for n in state.hand:
        c = CARD_DB[n]
        if c.ctype == "land" or n in HELD_SPELLS or n == held or c.mdfc_front:
            continue
        if n == "Germination Practicum" and not any(is_creature_type(p, state) for p in bf(state)):
            continue
        if n == "Planar Engineering" and (sum(1 for x in state.library if x in BASIC_LAND_NAMES) < 3
                                          or sum(1 for p in bf(state) if is_land(p, state)) < 2):
            continue
        if n == "Overlord of the Hauntwoods":
            if can_cast(state, n) or can_cast(state, n, "impending"):
                out.append(n)
            continue
        if can_cast(state, n):
            out.append(n)
    out.sort(key=lambda n: CARD_DB[n].mv)
    return out


def cast_loop(state: GameState, log: list, held: Optional[str]):
    if state.conduit_lockout:
        return
    for _ in range(60):
        if not state.commander_in_play and can_cast(state, COMMANDER):
            # comandante primeiro, sempre que der (inclusive depois de um rock
            # barato abrir a mana, ou na fase pos-combate)
            cast_spell(state, COMMANDER, log, from_zone="command")
            continue
        cands = castable_names(state, held)
        if not cands:
            return
        n = cands[0]
        if n == "Overlord of the Hauntwoods":
            cast_spell(state, n, log, "normal" if can_cast(state, n) else "impending")
        elif n == "Springheart Nantuko" and best_bestow_host(state) is not None:
            cast_spell(state, n, log, "bestow")
        else:
            cast_spell(state, n, log)


def best_attacker(state: GameState) -> Optional[Permanent]:
    cands = [p for p in bf(state) if is_creature_type(p, state) and not p.tapped and not is_sick(p, state)]
    return max(cands, key=lambda p: power(p, state), default=None)


# ---------------------------------------------------------------------------
# Habilidades ativadas (fase principal)
# ---------------------------------------------------------------------------

def skullclamp_loop(state: GameState, log: list):
    """Skullclamp: "Equipped creature gets +1/-1. Whenever equipped creature
    dies, draw two cards. Equip {1}." Equip e' repetivel (velocidade de
    feitico) -- antes: 1x por fase e so' em terreno earthbendado com 1
    contador. Agora qualquer criatura de resistencia 1 que valha menos que 2
    cartas: terreno earthbendado (volta), ficha 1/1, Haywire Mite, Esper
    Sentinel, e copia de Scute Swarm quando ja' ha' 4+. Nunca pecas-motor."""
    for _ in range(40):
        clamp = next((p for p in bf(state) if p.card.name == "Skullclamp"), None)
        if clamp is None:
            return
        n_scute = count_card(state, "Scute Swarm")

        def fodder_rank(p):
            if not is_creature_type(p, state) or pt(p, state)[1] != 1 or p.uid == clamp.attached_to:
                return None
            if p.earthbend_return:
                return 0
            if p.is_token and p.card.name in ("Insect", "Fish", "Construct", "Zombie", "Cat Beast"):
                return 1
            if p.card.name in ("Haywire Mite", "Esper Sentinel"):
                return 2
            if p.is_token and p.card.name == "Forest Dryad":
                return 3
            if p.is_token and p.card.name == "Scute Swarm" and n_scute >= 4:
                return 4
            return None
        cands = [(fodder_rank(p), p) for p in bf(state)]
        cands = [(r, p) for r, p in cands if r is not None]
        if not cands or not pay(state, 1, (), dry=True):
            return
        target = min(cands, key=lambda rp: rp[0])[1]
        pay(state, 1, (), log)
        clamp.attached_to = target.uid
        touch(state)
        state.skullclamp_equip_count += 1
        check_sba(state, log)


def sacrifice_engine(state: GameState, log: list):
    """Terreno earthbendado que volta (Motor #16): tapa pra mana primeiro, poe
    o Skullclamp se der, e sacrifica -- KCI ("Sacrifice an artifact: Add
    {C}{C}") se for artefato, Zuran Orb ("Sacrifice a land: You gain 2
    life") se for so' terreno. Ele volta (landfall de novo). Rodado no pos-
    combate: o terreno-criatura ataca primeiro. Os grandes (3+ contadores)
    ficam pro combate, a menos que o Ozolith recicle os contadores."""
    kci = has_card(state, "Krark-Clan Ironworks")
    orb = has_card(state, "Zuran Orb")
    if not kci and not orb:
        return
    ozolith = has_card(state, "The Ozolith")
    for p in list(bf(state)):
        if p not in state.battlefield or not p.earthbend_return or p.card.name in RECURRING_TARGETS:
            continue
        if p.counters > 2 and not ozolith:
            continue
        artifact = is_artifact(p, state)
        if not ((kci and artifact) or (orb and is_land(p, state))):
            continue
        units = mana_units(p, state)
        if units:
            n_badger = count_card(state, "Badgermole Cub") if is_creature_type(p, state) else 0
            add_floating(state, units + [frozenset("G")] * n_badger, "tapa antes do sacrificio")
            p.tapped = True
        clamp = next((c for c in bf(state) if c.card.name == "Skullclamp" and c.attached_to is None), None)
        if clamp is not None and is_creature_type(p, state) and pay(state, 1, (), dry=True):
            pay(state, 1, (), log)
            clamp.attached_to = p.uid
            touch(state)
            state.skullclamp_equip_count += 1
            check_sba(state, log)
            if p not in state.battlefield:
                continue
        if kci and artifact:
            state.kci_sacrifices_of_recurring += 1
            leave_battlefield(state, p, log, reason="sacrifice")
            add_floating(state, [COLORLESS, COLORLESS], "Krark-Clan Ironworks")
        else:
            state.zuran_orb_sacrifices += 1
            leave_battlefield(state, p, log, reason="sacrifice")
            gain_life(state, 2, log, source="Zuran Orb")


def zuran_orb_emergency(state: GameState, log: list):
    """Zuran Orb com vida baixa: terreno de verdade (perda real) por 2 de vida."""
    if not has_card(state, "Zuran Orb") or state.life_total >= 10:
        return
    lands = [p for p in bf(state) if p.card.ctype == "land" and not p.is_token and p.tapped]
    if lands:
        state.zuran_orb_sacrifices += 1
        leave_battlefield(state, lands[0], log, reason="sacrifice")
        gain_life(state, 2, log, source="Zuran Orb (vida baixa)")


def strip_mine_loop(state: GameState, log: list):
    """Strip Mine ("{T}, Sacrifice this land: Destroy target land") mirando o
    PROPRIO terreno earthbendado: ele volta (landfall) e o Strip Mine vai pro
    cemiterio -- so' e' linha racional com Crucible/Conduit/emblema do Wrenn
    pra rejogar o Strip Mine. Contra terreno de oponente: 📊."""
    if not (has_card(state, "Crucible of Worlds") or has_card(state, "Conduit of Worlds") or state.wrenn_emblem):
        return
    sm = next((p for p in bf(state) if p.card.name == "Strip Mine"), None)
    target = next((p for p in bf(state) if p.earthbend_return and is_land(p, state) and p.counters <= 2), None)
    if sm is None or target is None:
        return
    units = mana_units(sm, state)
    if units:
        add_floating(state, units)
    sm.tapped = True
    leave_battlefield(state, sm, log, reason="sacrifice")
    state.strip_mine_loops += 1
    leave_battlefield(state, target, log, reason="destroy")


def work_recurring_artifact_loop(state: GameState, log: list):
    """Motor #16: as cartas com sacrificio proprio (Mishra's Bauble, Unstable
    Obelisk, The Stasis Coffin) ativadas de verdade."""
    bauble = next((p for p in bf(state) if p.card.name == "Mishra's Bauble" and not p.tapped), None)
    if bauble is not None:
        bauble.tapped = True
        state.scheduled_draws += 1  # "Draw a card at the beginning of the next turn's upkeep."
        leave_battlefield(state, bauble, log, reason="sacrifice")
    obelisk = next((p for p in bf(state) if p.card.name == "Unstable Obelisk" and p.earthbend_return), None)
    if obelisk is not None and activate(state, obelisk, 7, (), log):
        state.obelisk_activations += 1
        # "Destroy target permanent": mira terreno earthbendado proprio (volta,
        # landfall); sem alvo proprio util, o alvo real seria de oponente (📊).
        own = next((p for p in bf(state) if p.earthbend_return and p is not obelisk and is_land(p, state)
                    and p.counters <= 2), None)
        leave_battlefield(state, obelisk, log, reason="sacrifice")
        if own is not None:
            leave_battlefield(state, own, log, reason="destroy")
    coffin = next((p for p in bf(state) if p.card.name == "The Stasis Coffin" and p.earthbend_return), None)
    if coffin is not None and activate(state, coffin, 2, (), log):
        state.coffin_activations += 1
        state.coffin_protected_until = state.turn  # "protection from everything until your next turn"
        leave_battlefield(state, coffin, log, reason="exile")


def try_bristly_bill_double(state: GameState, log: list):
    """"{3}{G}{G}: Double the number of +1/+1 counters on each creature you
    control." Sem {T} -- repetivel. So' criaturas e so' +1/+1 (antes dobrava
    qualquer contador de qualquer permanente, inclusive quest counter)."""
    for _ in range(4):
        if not has_card(state, "Bristly Bill, Spine Sower"):
            return
        with_c = [p for p in bf(state) if is_creature_type(p, state) and p.counters > 0]
        if sum(p.counters for p in with_c) < 3 or not pay(state, 3, (("G", 2),), dry=True):
            return
        pay(state, 3, (("G", 2),), log)
        for p in with_c:
            add_counters(state, p, p.counters, log)
        state.bristly_bill_doubles += 1


def ba_sing_se_activation(state: GameState, log: list):
    bss = next((p for p in bf(state) if p.card.name == "Ba Sing Se" and not p.tapped), None)
    if bss is not None and activate(state, bss, 2, (("G", 1),), log):
        apply_earthbend(state, 2, log, "Ba Sing Se (ativada)", triggered=False)  # ativada: Resonator nao copia


def wrenn_loyalty_ability(state: GameState, log: list):
    wrenn = next((p for p in bf(state) if p.card.name == "Wrenn and Realmbreaker"), None)
    if wrenn is None or state.wrenn_activated_turn == state.turn:
        return
    state.wrenn_activated_turn = state.turn
    if state.wrenn_loyalty >= 7:
        state.wrenn_loyalty -= 7  # CORRIGIDO: o -7 nunca pagava a lealdade
        state.wrenn_emblem = True
        state.wrenn_ultimate_activations += 1
    else:
        needs_target = ((has_card(state, "Bristly Bill, Spine Sower")
                         or (state.ozolith_counters > 0 and has_card(state, "The Ozolith")))
                        and best_creature_target(state) is None)
        if needs_target or state.wrenn_loyalty < 2:
            state.wrenn_loyalty += 1
            state.wrenn_plus1_activations += 1
            cands = [p for p in bf(state) if is_land(p, state) and not is_creature_type(p, state)]
            if cands:
                cands[0].temp_creature_until_turn = state.turn + 1
        else:
            state.wrenn_loyalty -= 2
            state.wrenn_minus2_activations += 1
            milled = [state.library.pop(0) for _ in range(min(3, len(state.library)))]
            state.graveyard.extend(milled)
            perms = [c for c in milled if CARD_DB[c].ctype not in ("instant", "sorcery") and not CARD_DB[c].mdfc_front]
            if perms:
                need_land = not any(n in LAND_NAMES for n in state.hand)
                lands = [c for c in perms if c in LAND_NAMES]
                nonland = [c for c in perms if c not in LAND_NAMES]
                chosen = lands[0] if (need_land and lands) else (max(nonland, key=lambda c: CARD_DB[c].mv)
                                                                 if nonland else lands[0])
                state.graveyard.remove(chosen)
                state.hand.append(chosen)
    if state.wrenn_loyalty <= 0:
        leave_battlefield(state, wrenn, log, reason="dies")


def caretaker_talent_levelup(state: GameState, log: list):
    ct = next((p for p in bf(state) if p.card.name == "Caretaker's Talent"), None)
    if ct is None:
        return
    if ct.level == 1 and pay(state, 0, (("W", 1),), dry=True):
        pay(state, 0, (("W", 1),), log)
        ct.level = 2
        # "When this Class becomes level 2, create a token that's a copy of target token you control."
        pref = ("Scute Swarm", "Construct", "Treefolk", "Zombie", "Cat Beast", "Treasure", "Lander",
                "Everywhere", "Forest Dryad", "Food", "Insect", "Fish")
        toks = [p for p in bf(state) if p.is_token]
        if toks:
            src = min(toks, key=lambda p: pref.index(p.card.name) if p.card.name in pref else 99)
            create_token(state, src.card.name, log, copy_of=src.card.name if not src.card.token else None)
    if ct.level == 2 and pay(state, 3, (("W", 1),), dry=True):
        pay(state, 3, (("W", 1),), log)
        ct.level = 3  # "Creature tokens you control get +2/+2" -- aplicado em `pt()`


def oswald_fiddlebender_tinker(state: GameState, log: list):
    """{W}, {T}, Sacrifice an artifact: artefato de valor de mana +1 da
    biblioteca pro campo. Criatura: {T} respeita doenca de invocacao. Ficha
    (valor de mana 0) serve de sacrificio -> busca custo 1."""
    oswald = next((p for p in bf(state) if p.card.name == "Oswald Fiddlebender" and not p.tapped
                   and not is_sick(p, state)), None)
    if oswald is None or not pay(state, 0, (("W", 1),), dry=True, exclude={oswald.uid}):
        return
    cands = [p for p in bf(state) if is_artifact(p, state) and p is not oswald]
    cands.sort(key=lambda p: (0 if p.is_token else 1, SAC_VALUE.get(p.card.name, 1)))
    for sac in cands:
        target_mv = (0 if (sac.is_token and sac.card.token) else sac.card.mv) + 1
        pool = [n for n in state.library if CARD_DB[n].ctype in ARTIFACT_ISH and CARD_DB[n].mv == target_mv]
        if not pool:
            continue
        activate(state, oswald, 0, (("W", 1),), log)
        found = pool[0]
        state.library.remove(found)
        leave_battlefield(state, sac, log, reason="sacrifice")
        enter_battlefield(state, mk_perm(state, found), log)
        return


def fountainport_abilities(state: GameState, log: list):
    fp = next((p for p in bf(state) if p.card.name == "Fountainport" and not p.tapped), None)
    if fp is None:
        return
    pref = ("Food", "Fish", "Insect", "Lander", "Cat Beast", "Zombie")
    token = next((p for n in pref for p in bf(state) if p.is_token and p.card.name == n), None)
    if token is not None and activate(state, fp, 2, (), log):
        leave_battlefield(state, token, log, reason="sacrifice")
        draw_cards(state, 1, log, source="Fountainport")
        return
    if activate(state, fp, 4, (), log):
        create_token(state, "Treasure", log)
        return
    if state.life_total > 10 and activate(state, fp, 3, (), log):
        lose_life(state, 1)
        create_token(state, "Fish", log)


def inventors_fair_tutor(state: GameState, log: list):
    fair = next((p for p in bf(state) if p.card.name == "Inventors' Fair" and not p.tapped), None)
    if fair is None or n_artifacts(state) < 3:
        return
    pool = [n for n in state.library if CARD_DB[n].ctype in ARTIFACT_ISH]
    if not pool or not can_activate(state, fair, 4):
        return
    found = next((n for n in ARTIFACT_TUTOR_PRIORITY if n in pool), None) or max(pool, key=lambda n: CARD_DB[n].mv)
    activate(state, fair, 4, (), log)
    state.library.remove(found)
    state.hand.append(found)
    leave_battlefield(state, fair, log, reason="sacrifice")


def iron_spider_abilities(state: GameState, log: list):
    spider = next((p for p in bf(state) if p.card.name == "Iron Spider, Stark Upgrade"), None)
    if spider is not None and not spider.tapped and not is_sick(spider, state):
        spider.tapped = True  # {T} (vigilance nao importa aqui) -- antes ignorava doenca de invocacao
        for p in [p for p in bf(state) if is_artifact(p, state) and is_creature_type(p, state)]:
            add_counters(state, p, 1, log)
    if spider is not None:
        with_c = [p for p in bf(state) if is_artifact(p, state) and p.counters > 0]
        if sum(p.counters for p in with_c) >= 2 and pay(state, 2, (), dry=True):
            pay(state, 2, (), log)
            to_remove = 2
            for p in sorted(with_c, key=lambda x: -x.counters):
                take = min(p.counters, to_remove)
                p.counters -= take
                to_remove -= take
                if to_remove <= 0:
                    break
            draw_cards(state, 1, log, source="Iron Spider")
            check_sba(state, log)


def conduit_of_worlds_reanimate(state: GameState, log: list):
    conduit = next((p for p in bf(state) if p.card.name == "Conduit of Worlds" and not p.tapped), None)
    if conduit is None or state.spells_cast_this_turn > 0:
        return
    pool = [n for n in state.graveyard if n not in LAND_NAMES and CARD_DB[n].ctype not in ("instant", "sorcery")
            and not CARD_DB[n].mdfc_front]
    if not pool:
        return
    affordable = [n for n in pool if pay(state, *cast_cost(state, n), dry=True, exclude={conduit.uid})]
    bomb = next((n for n in ARTIFACT_TUTOR_PRIORITY if n in affordable), None)
    hand_castables = castable_names(state, None)
    if bomb is None and hand_castables:
        return
    target = bomb or (max(affordable, key=lambda n: CARD_DB[n].mv) if affordable else None)
    if target is None:
        return
    conduit.tapped = True
    state.conduit_reanimations += 1
    cast_spell(state, target, log, from_zone="graveyard")
    state.conduit_lockout = True


def liquimetal_activation(state: GameState, log: list):
    if not toph_active(state):
        return
    for card_name in ("Liquimetal Coating", "Liquimetal Torque"):
        src = next((p for p in bf(state) if p.card.name == card_name and not p.tapped), None)
        if src is None:
            continue
        cands = [p for p in bf(state) if not is_land(p, state) and not is_artifact(p, state) and not p.is_token]
        if not cands:
            continue
        cands.sort(key=lambda p: 0 if is_creature_type(p, state) else 1)
        cands[0].temp_artifact_until_turn = state.turn
        src.tapped = True
        return


def bala_ged_recovery_spell_mode(state: GameState, log: list):
    name = "Bala Ged Recovery // Bala Ged Sanctuary"
    if name not in state.hand or state.conduit_lockout or not state.graveyard:
        return
    if state.lands_played_this_turn < land_drops_allowed(state):
        return  # ainda pode jogar como terreno -- prioridade do deck
    cast_spell(state, name, log)


def bridgeworks_battle_spell_mode(state: GameState, log: list):
    name = "Bridgeworks Battle // Tanglespan Bridgeworks"
    if name not in state.hand or state.conduit_lockout or state.phase != "main1":
        return
    if state.lands_played_this_turn < land_drops_allowed(state) or best_attacker(state) is None:
        return
    cast_spell(state, name, log)


def urza_saga_construct(state: GameState, log: list):
    saga = next((p for p in bf(state) if p.card.name == "Urza's Saga" and p.saga_chapter >= 2 and not p.tapped), None)
    if saga is not None and activate(state, saga, 2, (), log):
        state.urza_saga_chapter2_tokens += 1
        create_token(state, "Construct", log)


def lander_activations(state: GameState, log: list):
    for lander in [p for p in bf(state) if p.card.name == "Lander" and not p.tapped]:
        basics = [n for n in state.library if n in BASIC_LAND_NAMES]
        if not basics or not activate(state, lander, 2, (), log):
            return
        state.lander_activations += 1
        leave_battlefield(state, lander, log, reason="sacrifice")
        b = mk_perm(state, basics[0])
        state.library.remove(basics[0])
        b.tapped = True
        enter_battlefield(state, b, log)


def food_activations(state: GameState, log: list):
    for food in [p for p in bf(state) if p.card.name == "Food" and not p.tapped]:
        if not activate(state, food, 2, (), log):
            return
        state.food_eaten += 1
        leave_battlefield(state, food, log, reason="sacrifice")
        gain_life(state, 3, log, source="Food")


def equip_lightning_greaves(state: GameState, log: list):
    """Equip {0}: haste (ataca / tapa pra mana no turno em que entra) e
    shroud (modo de resiliencia). Vai pra criatura doente de maior valor de
    ataque -- gatilho de ataque primeiro (Bumi, Overlord)."""
    gr = next((p for p in bf(state) if p.card.name == "Lightning Greaves"), None)
    if gr is None:
        return
    sick = [p for p in bf(state) if is_creature_type(p, state) and p.entered_turn >= state.turn
            and "haste" not in p.card.tags and not p.earthbent and not p.tapped]
    if not sick:
        return
    def key(p):
        return (p.card.name not in ("Bumi, Eclectic Earthbender", "Overlord of the Hauntwoods"), -power(p, state))
    target = min(sick, key=key)
    if gr.attached_to != target.uid:
        gr.attached_to = target.uid
        touch(state)
        state.greaves_equips += 1


def equip_sword(state: GameState, log: list):
    sword = next((p for p in bf(state) if p.card.name == "Sword of Feast and Famine"), None)
    if sword is None:
        return
    holder = by_uid(state, sword.attached_to)
    if holder is not None and holder in state.battlefield:
        return
    t = best_attacker(state)
    if t is not None and pay(state, 2, (), dry=True):
        pay(state, 2, (), log)
        sword.attached_to = t.uid
        touch(state)


def talon_gates_from_hand(state: GameState, log: list):
    """"{4}: Put this card from your hand onto the battlefield." -- sem usar
    o land drop (landfall + ETB). So' quando o land drop ja' foi usado."""
    name = "Talon Gates of Madara"
    if name not in state.hand or state.lands_played_this_turn < land_drops_allowed(state):
        return
    if not pay(state, 4, (), dry=True):
        return
    pay(state, 4, (), log)
    state.hand.remove(name)
    state.talon_gates_hand_drops += 1
    enter_battlefield(state, mk_perm(state, name), log)


def jetmir_cycling(state: GameState, log: list):
    """Jetmir's Garden: "Cycling {3}" -- com o land drop do turno ja' feito e
    terreno de sobra (6+ em campo)."""
    name = "Jetmir's Garden"
    if name not in state.hand or n_lands(state) < 6 or state.lands_played_this_turn < 1:
        return
    if not pay(state, 3, (), dry=True):
        return
    pay(state, 3, (), log)
    state.hand.remove(name)
    state.graveyard.append(name)
    state.cycled += 1
    draw_cards(state, 1, log, source="Jetmir's Garden (cycling)")


def awaken_the_woods(state: GameState, log: list):
    name = "Awaken the Woods"
    if name not in state.hand or state.conduit_lockout:
        return
    if not pay(state, 0, (("G", 2),), dry=True):
        return
    x = 0
    while pay(state, x + 1, (("G", 2),), dry=True) and x < 20:
        x += 1
    if x >= 1:
        cast_spell(state, name, log, x=x)


def henge_life_tap(state: GameState, log: list):
    for h in [p for p in bf(state) if p.card.name == "The Great Henge" and not p.tapped]:
        h.tapped = True  # "{T}: Add {G}{G}. You gain 2 life." -- sem uso pra mana, ainda ganha a vida
        gain_life(state, 2, log, source="The Great Henge")


# ---------------------------------------------------------------------------
# Fases
# ---------------------------------------------------------------------------

def main_phase(state: GameState, log: list, first: bool):
    state.phase = "main1" if first else "main2"
    state.floating = []
    if first and state.germination_practicum_active and state.paradigm_done_turn != state.turn:
        # Paradigm: "at the beginning of each of your FIRST main phases" (1x por turno)
        state.paradigm_done_turn = state.turn
        state.spells_cast_this_turn += 1  # a copia e' conjurada
        for c in [c for c in bf(state) if is_creature_type(c, state)]:
            add_counters(state, c, 2, log)
    if first:
        play_land(state, log)
    if not first:
        sacrifice_engine(state, log)
        strip_mine_loop(state, log)
    conduit_of_worlds_reanimate(state, log)
    if BRISTLY_BILL_RESERVE_POLICY and first:
        try_bristly_bill_double(state, log)

    held = None
    if KODAMA_HOLD_POLICY and has_card(state, "Kodama of the East Tree"):
        perms = [n for n in state.hand if CARD_DB[n].ctype not in ("instant", "sorcery", "land")
                 and not CARD_DB[n].mdfc_front]
        if perms:
            held = min(perms, key=lambda n: CARD_DB[n].mv)

    for _ in range(4):
        before = (len(state.hand), len(state.battlefield), state.mana_spent_total)
        cast_loop(state, log, held)
        if state.wrenn_emblem and not state.conduit_lockout:
            for n in sorted([n for n in state.graveyard if CARD_DB[n].ctype not in ("land", "instant", "sorcery")
                             and not CARD_DB[n].mdfc_front and can_cast(state, n)], key=lambda n: CARD_DB[n].mv):
                if n in state.graveyard and can_cast(state, n):
                    cast_spell(state, n, log, from_zone="graveyard")
        if first:
            wrenn_loyalty_ability(state, log)
            lander_activations(state, log)
        ba_sing_se_activation(state, log)
        liquimetal_activation(state, log)
        bala_ged_recovery_spell_mode(state, log)
        caretaker_talent_levelup(state, log)
        oswald_fiddlebender_tinker(state, log)
        inventors_fair_tutor(state, log)
        iron_spider_abilities(state, log)
        urza_saga_construct(state, log)
        skullclamp_loop(state, log)
        if RECURRING_ARTIFACT_POLICY:
            work_recurring_artifact_loop(state, log)
        if first:
            bridgeworks_battle_spell_mode(state, log)
        after = (len(state.hand), len(state.battlefield), state.mana_spent_total)
        if after == before:
            break
    if first:
        if not BRISTLY_BILL_RESERVE_POLICY:
            try_bristly_bill_double(state, log)
        equip_sword(state, log)
        equip_lightning_greaves(state, log)
    else:
        lander_activations(state, log)
        fountainport_abilities(state, log)
        talon_gates_from_hand(state, log)
        jetmir_cycling(state, log)
        awaken_the_woods(state, log)
        cast_loop(state, log, held)
        food_activations(state, log)
        zuran_orb_emergency(state, log)
        henge_life_tap(state, log)


def combat_step(state: GameState, log: list):
    state.phase = "combat"
    state.floating = []
    # Beginning of combat
    if state.ozolith_counters > 0 and has_card(state, "The Ozolith"):
        t = best_creature_target(state)
        if t is not None:
            add_counters(state, t, state.ozolith_counters, log)
            state.ozolith_moves += 1
            state.ozolith_counters = 0
    for _ in range(count_card(state, "Avatar Kyoshi, Earthbender")):
        target = apply_earthbend(state, 8, log, "Avatar Kyoshi (inicio de combate)")
        if target is not None and target in state.battlefield:
            target.tapped = False  # "then untap that land"

    attackers = [p for p in bf(state) if is_creature_type(p, state) and not p.tapped
                 and not is_sick(p, state) and power(p, state) > 0]
    if not attackers:
        state.floating = []
        return
    state.attacks_total += 1
    for p in attackers:
        if not has_vigilance(p, state):
            p.tapped = True
    # "Whenever you attack" (1x por combate)
    for _ in range(count_card(state, "Toph, Earthbending Master")):
        apply_earthbend(state, state.experience_counters, log, "Toph Earthbending Master (ataque, X=experiencia)")
    # Horizon Explorer: "Whenever you attack a player" -- 1x POR JOGADOR atacado (ruling).
    # Goldfish espalha os atacantes pelos 3 oponentes quando da'.
    for _ in range(count_card(state, "Horizon Explorer")):
        for _p in range(min(NUM_OPPONENTS, len(attackers))):
            create_token(state, "Lander", log)
    for p in attackers:
        if p not in state.battlefield:
            continue
        if p.card.name == "Bumi, Eclectic Earthbender":
            for c in [c for c in bf(state) if is_land(c, state) and is_creature_type(c, state)]:
                add_counters(state, c, 2, log)  # "put two +1/+1 counters on each land creature you control"
        elif p.card.name == "Overlord of the Hauntwoods":
            create_token(state, "Everywhere", log, tapped=True)
    # Dano de combate (proxy: sem bloqueio, mesma convencao dos outros decks)
    double_strike = has_card(state, "Toph, Greatest Earthbender")
    dmg = 0
    sword_hit = False
    for p in attackers:
        if p not in state.battlefield:
            continue
        mult = 2 if (double_strike and is_land(p, state)) else 1  # "Land creatures you control have double strike"
        d = max(0, power(p, state)) * mult
        dmg += d
        if p.card.name == COMMANDER:
            state.commander_damage_dealt += d  # CR 903.10a: 21+ de UM comandante mata aquele oponente
            if state.commander_damage_dealt >= 21:
                state.commander_damage_win = True
        if any(e.card.name == "Sword of Feast and Famine" and e.attached_to == p.uid for e in bf(state)):
            sword_hit = True
    state.combat_damage_proxy_total += dmg
    deal_table_damage(state, dmg)
    if sword_hit:
        # "...that player discards a card (📊) and you untap all lands you control."
        state.sword_untaps += 1
        for p in bf(state):
            if is_land(p, state):
                p.tapped = False
    state.floating = []


def end_step(state: GameState, log: list):
    state.phase = "end"
    state.floating = []
    if toph_active(state):
        apply_earthbend(state, 2, log, "Toph, the First Metalbender (end step)")
    for p in bf(state):
        if p.impending and p.time_counters > 0:
            p.time_counters -= 1  # "At the beginning of your end step, remove a time counter"


def cleanup(state: GameState, log: list):
    state.floating = []
    while len(state.hand) > 7:
        lands = [n for n in state.hand if n in LAND_NAMES]
        if len(lands) > 2:
            worst = lands[-1]
        else:
            worst = max(state.hand, key=lambda n: (n not in LAND_NAMES, CARD_DB[n].mv))
        state.hand.remove(worst)
        state.graveyard.append(worst)
        state.discarded_to_hand_size += 1


def end_of_round_instants(state: GameState, log: list):
    """Instantaneos com mana aberta no fim da rodada (depois dos oponentes):
    Enlightened Tutor, Earthshape (earthbend 3 -> criatura com haste pro meu
    turno). Heroic Intervention/Teferi's Protection so' como resposta."""
    state.phase = "opp"
    state.floating = []
    if "Enlightened Tutor" in state.hand:
        cast_spell(state, "Enlightened Tutor", log)
    if "Earthshape" in state.hand:
        cast_spell(state, "Earthshape", log)
    if any(n in state.hand for n in ("Swords to Plowshares", "Erode", "Council's Judgment")):
        state.interaction_held_turns += 1
    state.floating = []


def untap_step(state: GameState):
    for p in state.battlefield:
        p.phased_out = False  # fase de volta ANTES de desvirar
    touch(state)
    for p in state.battlefield:
        p.tapped = False
        p.landfall_resolutions = 0


def upkeep_and_draw(state: GameState, log: list):
    if n_artifacts(state) >= 3:
        for _ in range(count_card(state, "Inventors' Fair")):
            gain_life(state, 1, log, source="Inventors' Fair")
    while state.scheduled_draws > 0:
        state.scheduled_draws -= 1
        draw_cards(state, 1, log, source="Mishra's Bauble")
    if state.library:
        state.hand.append(state.library.pop(0))  # compra normal (Commander: sempre compra, CR 103.8a)
    if has_card(state, "Sylvan Library") and len(state.library) >= 2:
        extra = [state.library.pop(0), state.library.pop(0)]
        state.hand.extend(extra)
        state.cards_drawn_extra += 2
        if state.life_total > 20:
            lose_life(state, 8)
        else:
            for c in extra:
                state.hand.remove(c)
            for c in reversed(extra):
                state.library.insert(0, c)
            state.cards_drawn_extra -= 2
    # Urza's Saga: "after your draw step, add a lore counter"
    for saga in [p for p in bf(state) if p.card.name == "Urza's Saga" and p.entered_turn < state.turn]:
        saga.saga_chapter += 1
        if saga.saga_chapter >= 3:
            # em resposta ao capitulo III, a habilidade do II ainda pode ser usada
            state.phase = "upkeep"
            urza_saga_construct(state, log)
            pool = [n for n in SAGA_TUTOR_PRIORITY if n in state.library]
            if pool:
                state.library.remove(pool[0])
                state.urza_saga_chapter3_tutors += 1
                enter_battlefield(state, mk_perm(state, pool[0]), log)
            if saga in state.battlefield:
                leave_battlefield(state, saga, log, reason="sacrifice")


def play_turn(state: GameState, log: list, is_first_turn: bool = False, on_play: bool = True):
    state.turn += 1
    state.lands_played_this_turn = 0
    state.landfalls_this_turn = 0
    state.token_drawn_this_turn = False
    state.counter_lifegain_this_turn = False
    state.spells_cast_this_turn = 0
    state.conduit_lockout = False
    state.floating = []
    untap_step(state)
    upkeep_and_draw(state, log)
    main_phase(state, log, first=True)
    combat_step(state, log)
    main_phase(state, log, first=False)
    end_step(state, log)
    cleanup(state, log)


# ---------------------------------------------------------------------------
# Construcao do deck / mulligan
# ---------------------------------------------------------------------------

def build_library():
    lib = []
    lines = open("lista.md").read().split("## Lista completa")[1].strip().split("\n")[1:]
    for l in lines:
        l = l.strip()
        if not l:
            continue
        m = re.match(r"^(\d+)\s+(.+)$", l)
        qty, name = int(m.group(1)), m.group(2).strip()
        assert name in CARD_DB, f"faltando no CARD_DB: {name}"
        lib += [name] * qty
    assert len(lib) == 99, len(lib)
    return lib


BASE_LIBRARY = build_library()


def is_land_name(name: str) -> bool:
    return name in LAND_NAMES


def should_keep(hand: list) -> bool:
    lands = sum(1 for n in hand if is_land_name(n))
    good_ramp = {"Sol Ring", "Arcane Signet", "Lotus Cobra", "Unstable Obelisk"}
    if lands >= 3:
        return True
    return lands == 2 and any(n in good_ramp for n in hand)


def library_with_swap(swap) -> list:
    """`swap` = (sai, entra) ou lista de pares: troca NA MESMA POSICAO."""
    if swap is None:
        return BASE_LIBRARY
    pairs = [swap] if isinstance(swap[0], str) else list(swap)
    lib = BASE_LIBRARY[:]
    for out_card, in_card in pairs:
        assert out_card in lib and in_card in CARD_DB and in_card not in lib
        lib[lib.index(out_card)] = in_card
    return lib


# Correcao de 2026-10-05 (varredura das classes de erro das rodadas do Vihaan/Megatron nos outros decks): o London Mulligan deste arquivo SORTEAVA as cartas do fundo
# (`rng.shuffle(hand)`), devolvendo com a mesma chance uma carta-chave e um terreno sobrando. Com a chave em False o arquivo se comporta bit-a-bit como antes.
MULLIGAN_SMART_BOTTOM_ENABLED = True   # o jogador ESCOLHE as cartas do fundo (mesma regra do Vihaan/Megatron)
MULLIGAN_PROTECTED = frozenset({"Sol Ring", "Arcane Signet", "Lotus Cobra", "Unstable Obelisk"})   # as cartas que `should_keep` ja' trata como "boa abertura": nao sao devolvidas se houver outra


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
    while mulls < max_mulls:
        lib = (library or BASE_LIBRARY)[:]
        rng.shuffle(lib)
        hand, lib = lib[:7], lib[7:]
        if should_keep(hand) or mulls == max_mulls - 1:
            penalty = max(0, mulls - 1)  # 1o mulligan gratis (convencao do usuario)
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


def total_mana(state: GameState) -> int:
    """Compatibilidade: mana disponivel agora (pool + fontes)."""
    return available_mana(state)


LETHAL_PROXY = 120  # 3 oponentes x 40 -- metrica limitada, nao vida real


def check_lethal(state: GameState):
    if state.lethal_turn is None and state.table_damage_total >= LETHAL_PROXY:
        state.lethal_turn = state.turn


def simulate_one(seed: int, turns: int = 8, swap=None):
    rng = random.Random(seed)
    hand, lib, mulls = mulligan(rng, library=library_with_swap(swap))
    state = GameState(hand=hand, library=lib, mulligans=mulls)
    log = [f"=== seed {seed} ==="]
    for t in range(turns):
        play_turn(state, log, is_first_turn=(t == 0), on_play=True)
        end_of_round_instants(state, log)
        check_lethal(state)
    return state, log


# ---------------------------------------------------------------------------
# MODO OPCIONAL DE RESILIENCIA (interacao de oponente) -- 2026-09-20,
# respostas de protecao 2026-09-26
# ---------------------------------------------------------------------------

NUM_OPPONENTS = 3
INTERACTION_SETUP_TURNS = 2
OPPONENT_ATTENTION_CHANCE = 1.0 / NUM_OPPONENTS
POST_WIPE_ATTACK_HASTE_FACTOR = 0.15
BOARD_WIPE_CHANCE_FACTOR = 0.4
GRAVEYARD_WIPE_CHANCE_FACTOR = 0.4
GRAVEYARD_SNIPE_CHANCE_FACTOR = 0.5
COUNTERSPELL_CHANCE_FACTOR = 0.5
ARTIFACT_WIPE_CHANCE_FACTOR = 0.2
ENCHANTMENT_WIPE_CHANCE_FACTOR = 0.15
WIPE_TYPE_WEIGHTS = {"creature": BOARD_WIPE_CHANCE_FACTOR, "artifact": ARTIFACT_WIPE_CHANCE_FACTOR,
                     "enchantment": ENCHANTMENT_WIPE_CHANCE_FACTOR}
TOTAL_WIPE_CHANCE_FACTOR = sum(WIPE_TYPE_WEIGHTS.values())
INTERACTION_ENGINE_PRIORITY = [
    "Ultron, Artificial Malevolence", "The Ozolith", "Skullclamp", "Wrenn and Realmbreaker",
    "Caretaker's Talent", "Conduit of Worlds", "Kodama of the East Tree", "Sylvan Library",
    "Zuran Orb", "Bristly Bill, Spine Sower",
]
OPPONENT_ATTACKER_PROFILES = [
    ("Knight Token", 2), ("Saproling Token", 1), ("Vampire Token", 1),
    ("Zombie Token", 2), ("Soldier Token", 1), ("Goblin Token", 1), ("Elemental Token", 3),
]


def interaction_chance(state: GameState) -> float:
    board_impact = sum(1 for p in bf(state) if not is_land(p, state))
    return min(0.10 + 0.03 * board_impact, 0.75)


def is_targetable_by_opponent(perm: Permanent, state: GameState) -> bool:
    if perm.phased_out:
        return False
    if perm.hexproof_until_turn is not None and perm.hexproof_until_turn >= state.turn:
        return False
    if perm.temp_creature_until_turn is not None:
        return False  # Wrenn +1: hexproof
    if any(e.card.name == "Lightning Greaves" and e.attached_to == perm.uid for e in bf(state)):
        return False  # shroud
    return True


def teferis_protection(state: GameState, log: list):
    """"Until your next turn, your life total can't change and you gain
    protection from everything. All permanents you control phase out."""
    state.tp_protected_until = state.turn
    for p in state.battlefield:
        p.phased_out = True
    touch(state)


def try_protection_response(state: GameState, log: list, kind: str, targets: list) -> Optional[str]:
    """Resposta real com mana aberta no turno do oponente (antes: todas essas
    cartas eram so' 'contadas', 📊). Teferi's Protection so' contra wipe que
    pega 3+ permanentes meus; Heroic Intervention contra wipe ou remocao de
    peca-motor; Earthshape (wipe de criatura: earthbend 3 e criaturas com
    poder <= o do terreno ganham indestrutivel/hexproof); Sapling Nursery
    ({1}{G}, exile: Treefolk e Forests indestrutiveis)."""
    if not targets:
        return None
    wipe = kind.startswith("wipe")
    if wipe and len(targets) >= 3 and "Teferi's Protection" in state.hand and can_cast(state, "Teferi's Protection"):
        cast_spell(state, "Teferi's Protection", log)
        return "Teferi's Protection"
    if "Heroic Intervention" in state.hand and can_cast(state, "Heroic Intervention"):
        cast_spell(state, "Heroic Intervention", log)
        return "Heroic Intervention"
    if kind == "wipe_creature" and "Earthshape" in state.hand and can_cast(state, "Earthshape"):
        cast_spell(state, "Earthshape", log)
        return "Earthshape"
    if wipe and kind != "wipe_enchantment":
        sap = next((p for p in bf(state) if p.card.name == "Sapling Nursery"), None)
        if sap is not None and pay(state, 1, (("G", 1),), dry=True):
            pay(state, 1, (("G", 1),), log)
            for p in bf(state):
                if p.card.name == "Treefolk" or is_forest(p, state):
                    p.indestructible_until_turn = state.turn
            leave_battlefield(state, sap, log, reason="exile")
            return "Sapling Nursery"
    return None


def remove_permanent(state: GameState, perm: Permanent, log: list, source: str = "opponent"):
    """Remocao de OPONENTE: destroi; se indestrutivel, exila (oponente esperto)."""
    leave_battlefield(state, perm, log, reason="exile" if is_indestructible(perm, state) else "destroy")


def try_smart_opponent_removal(state: GameState, log: list) -> Optional[str]:
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    target = None
    for n in INTERACTION_ENGINE_PRIORITY:
        target = next((p for p in bf(state) if p.card.name == n and is_targetable_by_opponent(p, state)), None)
        if target:
            break
    if target is None:
        return None
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    resp = try_protection_response(state, log, "removal", [target])
    if resp and not is_targetable_by_opponent(target, state):
        state.protection_saves_total += 1
        state.protection_log.append((state.turn, resp, "removal"))
        return None
    remove_permanent(state, target, log)
    state.smart_removals_total += 1
    state.smart_removal_log.append((state.turn, target.card.name))
    return target.card.name


def try_smart_opponent_attack(state: GameState, log: list) -> Optional[str]:
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    chance = interaction_chance(state) * (POST_WIPE_ATTACK_HASTE_FACTOR if state.wiped_this_round else 1.0)
    if state.interaction_rng.random() >= chance:
        return None
    name, pw = state.interaction_rng.choice(OPPONENT_ATTACKER_PROFILES)
    if state.tp_protected_until >= state.turn or state.coffin_protected_until >= state.turn:
        return None  # "protection from everything" / "life total can't change"
    state.life_total -= pw
    state.smart_attacks_taken_total += 1
    state.smart_attack_log.append((state.turn, name))
    return name


def try_smart_opponent_discard(state: GameState, log: list) -> Optional[str]:
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS or not state.hand:
        return None
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    target = state.interaction_rng.choice(state.hand)
    state.hand.remove(target)
    state.graveyard.append(target)
    state.smart_discards_total += 1
    state.smart_discard_log.append((state.turn, target))
    return target


def try_smart_opponent_wipe(state: GameState, log: list) -> Optional[list]:
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * TOTAL_WIPE_CHANCE_FACTOR:
        return None
    candidates = {
        "creature": [p for p in bf(state) if is_creature_type(p, state)],
        "artifact": [p for p in bf(state) if is_artifact(p, state)],
        "enchantment": [p for p in bf(state) if is_enchantment(p, state)],
    }
    available = [t for t in candidates if candidates[t]]
    if not available:
        return None
    wtype = state.interaction_rng.choices(available, weights=[WIPE_TYPE_WEIGHTS[t] for t in available])[0]
    targets = candidates[wtype]
    if wtype == "creature" or any(is_creature_type(p, state) for p in targets):
        state.wiped_this_round = True  # simetrico
    resp = try_protection_response(state, log, f"wipe_{wtype}", targets)
    if resp:
        state.protection_saves_total += 1
        state.protection_log.append((state.turn, resp, f"wipe_{wtype}"))
    victims = [p for p in targets if p in state.battlefield and not p.phased_out and not is_indestructible(p, state)]
    names = [p.card.name for p in victims]
    for p in victims:
        leave_battlefield(state, p, log, reason="destroy")
    key = {"creature": ("smart_wipes_total", "smart_wipe_log"),
           "artifact": ("smart_artifact_wipes_total", "smart_artifact_wipe_log"),
           "enchantment": ("smart_enchantment_wipes_total", "smart_enchantment_wipe_log")}[wtype]
    setattr(state, key[0], getattr(state, key[0]) + 1)
    getattr(state, key[1]).append((state.turn, names))
    return names


def try_smart_opponent_graveyard_wipe(state: GameState, log: list) -> Optional[list]:
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


def try_smart_opponent_graveyard_snipe(state: GameState, log: list) -> Optional[str]:
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return None
    cands = [c for c in state.graveyard if CARD_DB[c].ctype in CREATURE_ISH]
    if not cands:
        return None
    if state.interaction_rng.random() >= interaction_chance(state) * GRAVEYARD_SNIPE_CHANCE_FACTOR:
        return None
    target = max(cands, key=lambda n: CARD_DB[n].mv)
    state.graveyard.remove(target)
    state.smart_graveyard_snipes_total += 1
    state.smart_graveyard_snipe_log.append((state.turn, target))
    return target


def try_smart_opponent_counter(state: GameState) -> bool:
    if state.interaction_rng is None or state.turn <= INTERACTION_SETUP_TURNS:
        return False
    if state.interaction_rng.random() >= interaction_chance(state) * COUNTERSPELL_CHANCE_FACTOR:
        return False
    state.smart_counters_total += 1
    state.smart_counter_log.append(state.turn)
    return True


def try_smart_opponent_turn(state: GameState, log: list):
    state.phase = "opp"
    state.floating = []
    # cada turno de oponente e' um "turno" novo pros gatilhos "once each
    # turn"/"second time ... this turn" (Tannuk, Nissa, Caretaker's Talent)
    state.token_drawn_this_turn = False
    state.counter_lifegain_this_turn = False
    for p in state.battlefield:
        p.landfall_resolutions = 0
    if state.turn > INTERACTION_SETUP_TURNS and state.interaction_rng.random() >= OPPONENT_ATTENTION_CHANCE:
        return
    try_smart_opponent_wipe(state, log)
    try_smart_opponent_attack(state, log)
    try_smart_opponent_graveyard_wipe(state, log)
    try_smart_opponent_graveyard_snipe(state, log)
    try_smart_opponent_removal(state, log)
    try_smart_opponent_discard(state, log)


def simulate_one_with_interaction(seed: int, turns: int = 8, swap=None):
    rng = random.Random(seed)
    hand, lib, mulls = mulligan(rng, library=library_with_swap(swap))
    state = GameState(hand=hand, library=lib, mulligans=mulls, interaction_rng=random.Random(seed + 999_999))
    log = [f"=== seed {seed} (modo resiliencia) ==="]
    for t in range(turns):
        play_turn(state, log, is_first_turn=(t == 0), on_play=True)
        state.wiped_this_round = False
        for _ in range(NUM_OPPONENTS):
            try_smart_opponent_turn(state, log)
        end_of_round_instants(state, log)
        check_lethal(state)
    return state, log


# ---------------------------------------------------------------------------
# Relatorios
# ---------------------------------------------------------------------------

def run_batch(n: int, seed_base: int, turns: int = 8):
    states = [simulate_one(seed_base + i, turns=turns)[0] for i in range(n)]

    def avg(vals):
        return sum(vals) / len(vals) if vals else 0.0

    cmd_turn = [s.commander_cast_turn for s in states if s.commander_cast_turn is not None]
    lethal = [s.lethal_turn for s in states if s.lethal_turn is not None]
    print(f"n={n}, seed_base={seed_base}, turns={turns}")
    print(f"Avg mulligans: {avg([s.mulligans for s in states]):.2f}")
    print(f"Turno medio de conjuracao da Toph: {avg(cmd_turn):.2f} | nunca conjurada: "
          f"{100 * sum(1 for s in states if s.commander_cast_turn is None) / n:.1f}%")
    print(f"Avg terrenos em campo (turno {turns}, incl. artefato/criatura-terreno): "
          f"{avg([n_lands(s) for s in states]):.2f}")
    print(f"Avg magicas conjuradas: {avg([s.spells_cast_total for s in states]):.2f} | "
          f"mana gasta: {avg([s.mana_spent_total for s in states]):.2f}")
    print(f"Avg aplicacoes de earthbend: {avg([s.earthbend_applications for s in states]):.2f}")
    print(f"Avg recorrencias via Motor#16: {avg([s.motor16_recursions for s in states]):.2f}")
    print(f"Avg gatilhos de landfall: {avg([s.landfall_triggers_fired for s in states]):.2f}")
    print(f"Avg cartas compradas extra: {avg([s.cards_drawn_extra for s in states]):.2f}")
    print(f"Avg mana extra gerada e gastavel (Lotus Cobra/Nissa/KCI): {avg([s.mana_generated_extra for s in states]):.2f}")
    print(f"Avg fichas criadas: {avg([s.tokens_created for s in states]):.2f} | teto atingido em "
          f"{100 * sum(1 for s in states if s.token_cap_hits) / n:.1f}% dos jogos")
    print(f"Avg compras via Skullclamp: {avg([s.skullclamp_draws for s in states]):.2f}")
    print(f"Avg dano de combate (proxy, sem bloqueio): {avg([s.combat_damage_proxy_total for s in states]):.1f}")
    print(f"Avg dano na mesa (combate + Tannuk): {avg([s.table_damage_total for s in states]):.1f}")
    print(f"Letal proxy (>=120 na mesa) ate o T{turns}: {100 * len(lethal) / n:.1f}% | turno medio: {avg(lethal):.2f}")
    print(f"Avg vida final: {avg([s.life_total for s in states]):.2f}")
    print(f"Avg turnos com remocao guardada (📊 sem alvo de oponente): {avg([s.interaction_held_turns for s in states]):.2f}")
    combined = {}
    for s in states:
        for k, v in s.earthbend_by_source.items():
            combined[k] = combined.get(k, 0) + v
    print("\nEarthbend por fonte (por jogo):")
    for k, v in sorted(combined.items(), key=lambda kv: -kv[1]):
        print(f"  {k}: {v / n:.2f}")
    return states


def run_batch_with_interaction(n=2000, turns=8, seed_base=6000000):
    states = [simulate_one_with_interaction(seed_base + i, turns=turns)[0] for i in range(n)]

    def avg(vals):
        return sum(vals) / len(vals) if vals else 0.0

    print(f"=== Toph Goldfish v1 - MODO DE RESILIENCIA - n={n}, turns={turns} ===")
    print(f"Avg remocoes sofridas: {avg([s.smart_removals_total for s in states]):.2f}")
    print(f"Avg ataques sofridos: {avg([s.smart_attacks_taken_total for s in states]):.2f}")
    print(f"Avg descartes sofridos: {avg([s.smart_discards_total for s in states]):.2f}")
    print(f"Avg wipes (criatura/artefato/encantamento): {avg([s.smart_wipes_total for s in states]):.2f}/"
          f"{avg([s.smart_artifact_wipes_total for s in states]):.2f}/{avg([s.smart_enchantment_wipes_total for s in states]):.2f}")
    print(f"Avg respostas de protecao que salvaram algo: {avg([s.protection_saves_total for s in states]):.2f}")
    print(f"Avg counterspells sofridos (cast do comandante): {avg([s.smart_counters_total for s in states]):.2f}")
    print(f"Avg vida final: {avg([s.life_total for s in states]):.2f}")
    print(f"Letal proxy ate o T{turns}: {100 * sum(1 for s in states if s.lethal_turn) / n:.1f}%")
    print(f"Toph nunca conjurada: {100 * sum(1 for s in states if s.commander_cast_count == 0) / n:.1f}%")
    return states


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    states = run_batch(n=3000, seed_base=9000000, turns=8)
    with open("toph_v1_runs.jsonl", "w") as f:
        for s in states:
            f.write(json.dumps({
                "mulligans": s.mulligans, "commander_cast_turn": s.commander_cast_turn,
                "earthbend_applications": s.earthbend_applications, "motor16_recursions": s.motor16_recursions,
                "landfall_triggers_fired": s.landfall_triggers_fired,
                "field_of_the_dead_tokens": s.field_of_the_dead_tokens, "cards_drawn_extra": s.cards_drawn_extra,
                "tokens_created": s.tokens_created, "life_total": s.life_total,
                "combat_damage_proxy_total": s.combat_damage_proxy_total,
                "table_damage_total": s.table_damage_total, "lethal_turn": s.lethal_turn,
            }) + "\n")
