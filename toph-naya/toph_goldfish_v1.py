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
"""

import json
import random
import statistics
from dataclasses import dataclass, field
from typing import Optional

# Politica opcional: ativar de verdade as habilidades de sacrificio das
# cartas earthbend-recorrentes (Motor #16), em vez de so earthbenda-las e
# deixa-las paradas. Testada contra o baseline passivo em 2026-08-22 (ver
# goldfish-log.md): triplica a taxa de recorrencia real (11,1%->29,2% dos
# jogos) sem custo medido em curva/earthbend/vida — default True.
RECURRING_ARTIFACT_POLICY = True
RECURRING_TARGETS = ("The Stasis Coffin", "Unstable Obelisk", "Ichor Wellspring", "Mishra's Bauble")

# Qual permanente o earthbend mira primeiro. "narrow" = so as 4 cartas com
# habilidade de sacrificio propria valiosa (RECURRING_TARGETS). "broad_artifact"
# = qualquer um dos 26 artefatos nao-token da lista, ja que QUALQUER artefato
# earthbendado pode ser sacrificado pro Krark-Clan Ironworks e voltar de graca
# via Motor #16 (2 mana "gratis" de tempo, sem perder o permanente). "land_only"
# = earthbend nunca mira artefato, so terreno real (controle/contraste).
# Testado em 2026-08-22 (goldfish-log.md): broad_artifact domina narrow e
# land_only em toda metrica (recorrencia, mana extra, draw, tokens) sem custo
# medido em curva — default.
EARTHBEND_TARGET_POLICY = "broad_artifact"

# Ativa a priorizacao por valor (2026-08-22) ao escolher QUAL artefato
# earthbendado sacrificar pro Krark-Clan Ironworks sob "broad_artifact" —
# em vez do primeiro elegivel na ordem do campo. False = comportamento
# antigo (ordem de campo), testado como ponto de comparacao no
# goldfish-log.md.
SAC_VALUE_PRIORITY_POLICY = True

# Kodama of the East Tree so acha o proprio gatilho se sobrar uma carta
# barata na mao quando outro permanente entra depois — a politica gananciosa
# padrao esvazia a mao antes disso acontecer (6,2% de acerto condicional,
# medido em 2026-08-22). Com o flag ligado, se Kodama estiver em campo,
# reserva deliberadamente 1 permanente barato na mao em vez de conjura-lo.
KODAMA_HOLD_POLICY = True

# Bristly Bill's ativada (dobra contadores, {3}{G}{G}=5) so achava mana
# sobrando DEPOIS do loop ganancioso de conjurar tudo que dava. Testado
# (2026-08-22) reservar a mana ANTES do loop: melhora a propria ativacao
# (74,1%->89,0% condicional) mas e um TRADE-OFF real, nao vitoria de graca —
# compete com o resto do plano (cartas compradas extra -4%, tokens -5%,
# porque sobra menos mana pro loop ganancioso conjurar outras cartas).
# Default False (comportamento antigo) porque o custo liquido pro deck como
# um todo nao compensou nos dados — True fica disponivel pra quem preferir
# priorizar esse motor especifico.
BRISTLY_BILL_RESERVE_POLICY = False

# The Ozolith: testado (2026-08-22) priorizar sacrificar um artefato COM
# contador quando o Ozolith esta em campo — resultado nulo, revertido. Todo
# artefato com earthbend_return=True ja tem contador>0 por definicao (o
# proprio earthbend so seta essa flag ao adicionar contadores), entao "prefira
# quem tem contador" e um no-op: sempre verdadeiro pra todo candidato. O
# gargalo real do Ozolith (31,9% de acerto condicional) e timing de compra —
# ele precisa estar em campo ANTES de um artefato-terreno morrer, e isso nao
# e uma decisao de politica de jogo, e probabilidade de compra de singleton.

# Quanto MENOR o numero, mais descartavel — sacrificada primeiro. O criterio
# real e "quanto essa carta perde por ficar tapped/fora por um ciclo de
# earthbend" (o permanente sempre volta via Motor #16, entao a unica perda
# de verdade e 1 turno de habilidade ativada/mana, nunca o cartao em si):
#   0 = sem perda relevante — nao tem habilidade ativada por turno que valha
#       a pena preservar (equipamento desequipado, peca situacional, ou uma
#       das 4 cartas do RECURRING_TARGETS que ja tem tratamento proprio e so
#       cairia aqui como fallback).
#   1 = rocks de mana puros — perde 1 turno de rampa ao voltar tapped, mas
#       nunca perde o rock de verdade.
#   2 = utilidade ativa que compete por mana/tap todo turno (Iron Spider,
#       Strionic Resonator, Esper Sentinel).
#   3 = proteger — motor que outras partes do proprio simulador dependem
#       (Ozolith recicla contadores, Krark-Clan Ironworks E o proprio sac
#       outlet do loop) ou bomba de alto impacto continuo (Krang, The Great
#       Henge, Ultron, Mycosynth Lattice) — so sacrificada se nao sobrar mais
#       nenhuma opcao de valor mais baixo.
SAC_VALUE = {
    "Lightning Greaves": 0,
    "Liquimetal Coating": 0,
    "Skullclamp": 0,
    "Sword of Feast and Famine": 0,
    "Haywire Mite": 0,
    "Oblivion Stone": 0,
    "Conduit of Worlds": 0,
    "Crucible of Worlds": 0,
    "Mishra's Bauble": 0,
    "Ichor Wellspring": 0,
    "The Stasis Coffin": 0,
    "Unstable Obelisk": 0,
    "Zuran Orb": 0,
    "Sol Ring": 1,
    "Arcane Signet": 1,
    "Mox Opal": 1,
    "Liquimetal Torque": 1,
    "Strionic Resonator": 2,
    "Iron Spider, Stark Upgrade": 2,
    "Esper Sentinel": 2,
    "Krark-Clan Ironworks": 3,
    "The Ozolith": 3,
    "Krang, Utrom Warlord": 3,
    "The Great Henge": 3,
    "Ultron, Artificial Malevolence": 3,
    "Mycosynth Lattice": 3,
}


# ---------------------------------------------------------------------------
# Card database
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Card:
    name: str
    mv: int
    ctype: str  # 'land','artifact','creature','artifact_creature','enchantment',
                # 'enchantment_creature','planeswalker','instant','sorcery'
    tags: frozenset = field(default_factory=frozenset)


CARD_DB: dict[str, Card] = {}


def add(name, mv, ctype, tags=()):
    CARD_DB[name] = Card(name=name, mv=mv, ctype=ctype, tags=frozenset(tags))


COMMANDER = "Toph, the First Metalbender"
add(COMMANDER, 3, "creature", {"commander", "earthbend_source_end_step"})

# --- Lands (32, incl. 3x Forest) ---------------------------------------------------
add("Arid Mesa", 0, "land", {"fetch"})
# Ba Sing Se: "This land enters tapped unless you control a basic land."
# Achado real 2026-09-01 (revisao completa do oraculo) -- essa condicional
# nunca era checada (entrava sempre destapada). Tag nova, ver
# `ENTERS_TAPPED_UNLESS_BASIC` em `play_land()`.
add("Ba Sing Se", 0, "land", {"earthbend_source_activated", "enters_tapped_unless_basic"})
# Bala Ged Recovery // Bala Ged Sanctuary: MDFC (modal_dfc, Scryfall
# confirmado). Registrada so' como land (mv=0 -- o "3" antigo aqui era o
# custo real do lado sorcery {2}{G}, vestigial, mesmo problema ja
# corrigido no Ondu Inversion/Bridgeworks Battle). Lado sorcery ("Return
# target card from your graveyard to your hand") NAO depende de oponente
# -- diferente dos outros 2 MDFCs da lista -- mas modela-lo exigiria
# permitir DOIS modos de conjuracao pra uma unica entrada de CARD_DB
# (hoje `ctype` e' singular por carta; o loop de `castables` em
# `main_phase()` ja exclui `ctype=="land"` inteiro). Fora do escopo desta
# rodada (limitacao de arquitetura, nao omissao) -- decisao documentada
# 2026-08-31, agravada pelo fato de o deck ja estar no piso de terrenos
# (lista.md), entao um piloto real quase sempre prefere o lado land aqui
# de qualquer forma. Face land real: "This land enters tapped."
add("Bala Ged Recovery // Bala Ged Sanctuary", 0, "land", {"enters_tapped"})
add("Bountiful Promenade", 0, "land", set())
# Bridgeworks Battle // Tanglespan Bridgeworks: MDFC (modal_dfc). So' land
# (mv=0, mesmo motivo do Ondu Inversion acima). Lado sorcery ("fights up
# to one target creature you don't control") exige uma criatura de
# OPONENTE de verdade pra mirar -- impossivel modelar num goldfish solo
# sem inventar estado alheio (Regra 1). N/A estrutural, nao omissao. Face
# land real (Tanglespan Bridgeworks): "As this land enters, you may pay 3
# life. If you don't, it enters tapped." -- unico dos 3 MDFCs da lista com
# essa escolha (os outros dois so' entram tapped, sem opcao).
add("Bridgeworks Battle // Tanglespan Bridgeworks", 0, "land", {"enters_tapped_payable"})
# Canopy Vista/Cinder Glade ("battle lands"): "This land enters tapped
# unless you control two or more basic lands." Achado real 2026-09-01 --
# condicional nunca checada (entravam sempre destapadas). Tag nova, ver
# `ENTERS_TAPPED_UNLESS_2_BASICS` em `play_land()`.
add("Canopy Vista", 0, "land", {"enters_tapped_unless_2_basics"})
add("Cinder Glade", 0, "land", {"enters_tapped_unless_2_basics"})
add("Command Tower", 0, "land", {"rock_any"})
# Field of the Dead: "This land enters tapped." (sem condicional nenhuma,
# diferente de Ba Sing Se/battle lands). Achado real 2026-09-01 -- faltava
# a tag `enters_tapped`, mesma classe de bug ja corrigida nos 3 MDFCs.
add("Field of the Dead", 0, "land", {"field_of_the_dead", "enters_tapped"})
add("Forest", 0, "land", set())
add("Fountainport", 0, "land", {"token_sac_draw"})
# Gruul Turf: "This land enters tapped." Achado real 2026-09-01 (2a
# passada da revisao de oraculo) -- faltava a tag, bouncelands entravam
# destapadas de graca.
add("Gruul Turf", 0, "land", {"bounceland", "enters_tapped"})
add("Inventors' Fair", 0, "land", {"artifact_lifegain"})
# Jetmir's Garden: "This land enters tapped." (tri-land, sem condicao,
# como qualquer trilando). Achado real 2026-09-01 -- faltava a tag.
add("Jetmir's Garden", 0, "land", {"rock_any", "enters_tapped"})
add("Mountain", 0, "land", set())
# Ondu Inversion // Ondu Skyruins: MDFC (modal_dfc, Scryfall confirmado).
# Registrada so' como land (mv=0, como qualquer outro terreno -- o "8"
# antigo aqui era o custo real do lado sorcery {6}{W}{W}, vestigial e
# inflava curva/CMC medio sem nenhum efeito real, ja que ctype=="land"
# exclui a carta do loop de conjuracao). Decisao documentada (achado real
# 2026-08-31, fechamento da rodada ampliada): o lado sorcery ("Destroy
# all nonland permanents") e' um wipe SIMETRICO sem excecao nenhuma --
# num goldfish solo sem oponente real, conjurar isso so' destruiria o
# proprio board pra ganho zero (mesmo raciocinio ja aplicado ao Kindred
# Dominance/Swarmyard Massacre/Damnation no Rat King, Regra 1: nao fingir
# uma jogada irracional que nenhum piloto real faria). Tag `wipe_unused`
# (nunca tinha dispatch nenhum) removida. Face land real (Ondu Skyruins):
# "This land enters tapped."
add("Ondu Inversion // Ondu Skyruins", 0, "land", {"enters_tapped"})
add("Plains", 0, "land", set())
# Selesnya Sanctuary: mesmo achado do Gruul Turf, "This land enters tapped".
add("Selesnya Sanctuary", 0, "land", {"bounceland", "enters_tapped"})
add("Snow-Covered Forest", 0, "land", set())
add("Snow-Covered Mountain", 0, "land", set())
add("Snow-Covered Plains", 0, "land", set())
add("Spire Garden", 0, "land", set())
# Stomping Ground/Temple Garden (shock lands): "As this land enters, you
# may pay 2 life. If you don't, it enters tapped." Achado real 2026-09-01
# -- a escolha nunca era modelada (entravam sempre destapadas de graca,
# sem custo nenhum). Mesma tag `enters_tapped_payable` das MDFCs, mas com
# custo de vida diferente (2, nao 3) -- ver `ENTERS_TAPPED_PAYABLE_LIFE`.
add("Stomping Ground", 0, "land", {"enters_tapped_payable"})
add("Strip Mine", 0, "land", set())
# Achado real 2026-09-02 (usuario apontou): a tag "phase_out_unused" e a
# nota do checklist ("sem bom alvo sem oponente") tratavam o ETB SO como
# remocao ofensiva (precisa de criatura de oponente) -- mas "up to one
# target creature" NAO exige alvo alheio: um piloto real usa isso pra
# PROTEGER a propria criatura mais valiosa (fase fora, some do jogo ate
# o proximo untap step, imune a qualquer coisa nesse intervalo). Com
# earthbend transformando este proprio terreno numa criatura ("When it
# dies or is exiled, return it to the battlefield tapped" -- Motor#16 ja
# implementado), cada vez que Talon Gates volta ao campo (inclusive via
# essa recorrencia) o ETB dispara de novo, protegendo outra criatura.
# Implementado como evento REAL contado (tag renomeada pra
# `phase_out_protect`), mesma convencao ja usada nesta lista pra
# Teferi's Protection/Heroic Intervention/Lightning Greaves
# (`protection_unused`, "contado" mas sem valor numerico de HP salvo --
# sem oponente real, nao ha dano/remocao concreta pra medir prevenida).
# A MAGNITUDE de quantas vezes isso "recorre" de verdade depende de
# oponentes reais destruindo a criatura earthbendada (unico jeito de
# reciclar via Motor#16, ja que Talon Gates nao tem habilidade de
# sacrificio propria nem e' artefato pro KCI) -- isso e' genuinamente
# opponent-dependent, mesma classe estrutural de todo o resto da sessao,
# nao um julgamento de valor sobre a sinergia em si.
add("Talon Gates of Madara", 0, "land", {"rock_any_paid", "phase_out_protect"})
add("Temple Garden", 0, "land", {"enters_tapped_payable"})
# Engine real de capitulo I/II/III implementada 2026-08-31 (ver
# `urza_saga_advance()`), dispachada por nome (como Bristly Bill/Ba Sing
# Se/etc), nao por tag -- a tag `saga_token` antiga nunca tinha dispatch
# nenhum e foi removida.
add("Urza's Saga", 0, "land", set())
add("Windswept Heath", 0, "land", {"fetch"})
add("Wooded Foothills", 0, "land", {"fetch"})
add("Wrenn and Realmbreaker", 3, "planeswalker", {"rock_all_lands_any"})
add("Yavimaya, Cradle of Growth", 0, "land", set())

# --- Ramp -----------------------------------------------------------------
add("Arcane Signet", 2, "artifact", {"rock_any"})
add("Sol Ring", 1, "artifact", {"rock2"})
add("Mox Opal", 0, "artifact", {"rock_metalcraft", "legendary"})
# Achado real 2026-09-01: type_line real e' "Enchantment Creature", nao so'
# "Creature" (nao muda nada no modelo -- CREATURE_ISH ja cobre os dois --
# mas a classificacao errada e' corrigida por precisao).
add("Dryad of the Ilysian Grove", 3, "enchantment_creature", {"extra_land_drop"})
# "Lands you control enter untapped" (estatica, achado real 2026-09-01,
# nunca implementada) -- ver `resolve_land_enters_tapped()`, dispachada por
# nome (`has_card`), nao por tag.
add("Horizon Explorer", 3, "creature", {"lander_on_attack"})
add("Lotus Cobra", 2, "creature", {"landfall_mana"})
add("Nissa, Resurgent Animist", 3, "creature", {"landfall_mana", "landfall_dig_2nd"})
add("Tireless Provisioner", 3, "creature", {"landfall_token"})
add("Planar Engineering", 4, "sorcery", {"land_ramp_burst"})
add("Unstable Obelisk", 3, "artifact", {"rock1", "removal_recurring"})
add("Liquimetal Torque", 2, "artifact", {"rock1", "liquimetal"})
add("The Great Henge", 9, "artifact", {"rock2life", "etb_creature_draw_counter", "legendary"})

# --- Card draw --------------------------------------------------------------
add("Sylvan Library", 2, "enchantment", {"draw_engine"})
add("Esper Sentinel", 1, "artifact_creature", {"opponent_dependent"})
add("Skullclamp", 1, "artifact", {"combat_dependent"})
add("Ichor Wellspring", 2, "artifact", {"draw_etb_death", "earthbend_target_priority"})
add("Mishra's Bauble", 0, "artifact", {"delayed_draw"})
add("Iron Spider, Stark Upgrade", 3, "artifact_creature", {"artifact_counter_draw", "legendary"})
add("Caretaker's Talent", 3, "enchantment", {"token_draw"})
add("Tannuk, Memorial Ensign", 3, "creature", {"landfall_dmg", "landfall_draw_2nd"})
# Mesma estatica "lands enter untapped" do Horizon Explorer, ver ali.
add("Spelunking", 3, "enchantment", {"etb_draw_land"})
add("Fountainport", 0, "land", {"token_sac_draw"})  # already added above as land

# --- Removal & wipes --------------------------------------------------------
add("Erode", 1, "instant", {"removal"})
# "Bridgeworks Battle" (sem "// Tanglespan Bridgeworks") removido -- codigo
# morto: o nome real que build_library()/lista.md usam e' o nome completo
# com "//" (registrado abaixo como land), essa entrada solta nunca era
# alcancada (achado real 2026-08-31, rodada ampliada de fechamento).
add("Haywire Mite", 1, "artifact_creature", {"opponent_dependent"})
add("Swords to Plowshares", 1, "instant", {"removal"})
add("Council's Judgment", 3, "sorcery", {"opponent_dependent"})
add("Teferi's Protection", 3, "instant", {"protection_unused"})
add("Oblivion Stone", 3, "artifact", {"wipe_unused"})

# --- Win-con / sinergia central --------------------------------------------
add("Ashaya, Soul of the Wild", 5, "creature", {"ashaya"})
add("Avatar Kyoshi, Earthbender", 8, "creature", {"earthbend_source_combat_8"})
add("Awaken the Woods", 2, "sorcery", {"land_token_x"})
add("Badgermole Cub", 2, "creature", {"earthbend_source_etb_1"})
add("Bristly Bill, Spine Sower", 2, "creature", {"landfall_counter", "mass_double_activated"})
add("Bumi, Eclectic Earthbender", 5, "creature", {"earthbend_source_etb_1", "attack_counter_lands"})
# Canopy Vista/Cinder Glade registradas na secao de terrenos (achado real
# 2026-09-01: "enters tapped unless you control two or more basic lands"
# corrigido la, ver `ENTERS_TAPPED_UNLESS_2_BASICS`). add() duplicado
# (dado identico, `set()`) removido daqui.
add("Conduit of Worlds", 4, "artifact", {"gy_lands", "gy_recursion_1turn"})
add("Crucible of Worlds", 3, "artifact", {"gy_lands"})
add("Earth Kingdom General", 4, "creature", {"earthbend_source_etb_2", "counter_lifegain"})
add("Earthbender Ascension", 3, "enchantment", {"earthbend_source_etb_2", "landfall_quest"})
add("Earthbending Student", 3, "creature", {"earthbend_source_etb_2"})
add("Earthshape", 3, "instant", {"earthbend_source_cast_3"})
add("Enduring Vitality", 3, "enchantment_creature", {"creature_mana_any"})
add("Enlightened Tutor", 1, "instant", {"tutor_artifact_enchant"})
add("Felidar Retreat", 4, "enchantment", {"landfall_choice"})
# Field of the Dead registrada na secao de terrenos (com "enters_tapped",
# achado real 2026-09-01). add() duplicado removido daqui.
add("Germination Practicum", 5, "sorcery", {"mass_counter_repeat"})
add("Great Divide Guide", 2, "creature", set())
# Achado real 2026-08-28 (auditoria de checklist de mecanica): tag
# "rock_lands_any" nunca lida em lugar nenhum (dead tag), removida. Oraculo
# real: "Each land and Ally you control has '{T}: Add one mana of any
# color.'" - estatica de FIXACAO de cor pra terrenos ja existentes, nao
# uma fonte de mana propria adicional. Esse motor nao rastreia cor
# nenhuma em total_mana() (so' magnitude total) - terrenos ja contam 1
# cada independente de cor, entao o efeito real dela nao muda o total
# numerico neste modelo. Documentado como limitacao de arquitetura, nao
# um bug (nao ha estrutura de cor pra "consertar" aqui).
# Gruul Turf ja registrada na secao de terrenos. add() duplicado removido.
add("Heroic Intervention", 2, "instant", {"protection_unused"})
add("Kodama of the East Tree", 6, "creature", {"cheat_permanent"})
add("Krang, Utrom Warlord", 9, "artifact_creature", {"combat_dependent", "legendary"})
add("Krark-Clan Ironworks", 4, "artifact", {"sac_outlet_mana"})
add("Lightning Greaves", 2, "artifact", {"protection_unused"})
add("Liquimetal Coating", 2, "artifact", {"liquimetal_unused"})
add("Mossborn Hydra", 3, "creature", {"landfall_double_self"})
add("Mycosynth Lattice", 6, "artifact", {"mycosynth"})
add("Oswald Fiddlebender", 2, "creature", {"artifact_tutor_cheat"})
add("Overlord of the Hauntwoods", 5, "enchantment_creature", {"land_token_everywhere"})
# Planar Engineering ja registrada na secao de ramp. add() duplicado removido.
add("Prismatic Omen", 2, "enchantment", {"fixing_unused"})
add("Sapling Nursery", 8, "enchantment", {"landfall_token"})
add("Scute Swarm", 3, "creature", {"landfall_token_or_copy"})
add("Springheart Nantuko", 2, "enchantment_creature", {"landfall_token"})
add("Strionic Resonator", 2, "artifact", {"trigger_copy"})
add("Sword of Feast and Famine", 3, "artifact", {"combat_dependent"})
add("The Ozolith", 1, "artifact", {"ozolith", "legendary"})
add("The Stasis Coffin", 3, "artifact", {"protection_recurring", "earthbend_target_priority", "legendary"})
add("Toph, Earthbending Master", 4, "creature", {"landfall_experience", "attack_earthbend_experience"})
add("Toph, Greatest Earthbender", 4, "creature", {"earthbend_source_cast_x", "double_strike_land_creatures"})
add("Ultron, Artificial Malevolence", 3, "artifact_creature", {"artifact_copy", "legendary"})
# Windswept Heath/Wooded Foothills/Yavimaya ja registradas na secao de
# terrenos. add()s duplicados removidos (dados identicos).
add("Zuran Orb", 0, "artifact", {"sac_land_lifegain"})
add("Forest Dryad Token", 0, "land", {"always_creature"})  # Awaken the Woods
add("Everywhere Token", 0, "land", set())  # Overlord of the Hauntwoods

# Sanity: dedupe re-adds don't break anything (dict overwrite is idempotent
# for cards added twice above with identical data)

LAND_NAMES = {n for n, c in CARD_DB.items() if c.ctype == "land"}
ARTIFACT_ISH = {"artifact", "artifact_creature"}
CREATURE_ISH = {"creature", "artifact_creature", "enchantment_creature"}

# Metrica obrigatoria #10 (goldfish-sim-card-rules.md secao 10) -- interaction:
# qualquer carta cujo efeito real dependa de oponente/alvo adversario
# (removal, protecao, wipe, valor so' relevante em combate real) conta aqui
# quando conjurada/colocada em campo, mesmo sem efeito numerico solo
# (documentado em vez de omitido). "combat_dependent" (Skullclamp/Krang/
# Sword of Feast and Famine) incluida 2026-09-01 -- essas 3 cartas nao
# tinham NENHUM numero reportado antes, nem como N/A.
INTERACTION_TAGS = {"removal", "opponent_dependent", "protection_unused", "wipe_unused", "combat_dependent"}

# Metrica obrigatoria #10 -- finisher/lethality: proxy de "turno em que uma
# ameaca de vitoria resolve" (secao 8 de auditoria.md: earthbend em escala,
# wide+counters, Krang, Great Henge). Sem combate real modelado (docstring),
# NAO e' turno de dano letal de verdade, so' turno de resolucao da peca --
# documentado explicitamente, nao fingido como taxa de vitoria real.
FINISHER_CARDS = {
    "Avatar Kyoshi, Earthbender",
    "Toph, Earthbending Master",
    "Krang, Utrom Warlord",
    "The Great Henge",
    "Scute Swarm",
    "Sapling Nursery",
    "Felidar Retreat",
    "Mossborn Hydra",
}

# Prioridade generica de "melhor artefato disponivel" usada por qualquer
# tutor de artefato do deck (Enlightened Tutor, Inventors' Fair) -- fatorada
# 2026-09-01 pra nao duplicar a lista em cada dispatch.
ARTIFACT_TUTOR_PRIORITY = ("Sol Ring", "The Great Henge", "Skullclamp", "Krark-Clan Ironworks",
                           "Sylvan Library", "Mycosynth Lattice", "Unstable Obelisk", "Mox Opal",
                           "Arcane Signet", "The Ozolith")


# ---------------------------------------------------------------------------
# Game state
# ---------------------------------------------------------------------------

@dataclass
class Permanent:
    card: Card
    tapped: bool = False
    counters: int = 0
    earthbent: bool = False
    earthbend_return: bool = False
    entered_turn: int = 0
    uid: int = 0
    is_token: bool = False
    saga_chapter: int = 0  # Urza's Saga only
    level: int = 1  # Class enchantments (Caretaker's Talent) only
    forced_creature: bool = False  # Ultron copiando artefato nao-criatura (vira 2/2 Robot Villain)
    temp_creature_until_turn: Optional[int] = None  # Wrenn +1: terreno vira criatura ate seu proximo turno
    temp_artifact_until_turn: Optional[int] = None  # Liquimetal Coating/Torque: vira artefato ate o fim do turno


@dataclass
class GameState:
    turn: int = 0
    hand: list = field(default_factory=list)
    battlefield: list = field(default_factory=list)
    graveyard: list = field(default_factory=list)
    library: list = field(default_factory=list)
    mulligans: int = 0

    commander_in_play: bool = False
    commander_cast_count: int = 0
    ashaya_in_play: bool = False
    mycosynth_in_play: bool = False

    lands_played_this_turn: int = 0
    extra_land_drops: int = 0
    landfalls_this_turn: int = 0
    mana_spent_this_turn: int = 0

    treasures: int = 0
    foods: int = 0
    ozolith_counters: int = 0
    experience_counters: int = 0  # Toph, Earthbending Master
    wrenn_loyalty: int = 0

    scheduled_draws: int = 0  # Mishra's Bauble
    life_total: int = 40
    life_gained: int = 0
    token_drawn_this_turn: bool = False  # Caretaker's Talent (1x/turno)
    counter_lifegain_this_turn: bool = False  # Earth Kingdom General (1x/turno)
    germination_practicum_active: bool = False  # Paradigm: recast de graca todo turno seguinte

    next_uid: int = 1

    # metrics --------------------------------------------------------------
    log: list = field(default_factory=list)
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
    scute_swarm_cap_hits: int = 0
    obelisk_activations: int = 0
    coffin_activations: int = 0
    kci_sacrifices_of_recurring: int = 0
    kci_sacrifices_broad: int = 0
    talon_gates_protections: int = 0
    commander_cast_turn: Optional[int] = None
    first_pw_ish_turn: Optional[int] = None  # not used, placeholder for parity

    # Achados 2026-08-31 (rodada de implementacao dos itens diagnosticados-mas-
    # nao-implementados da rodada anterior) -----------------------------------
    crucible_land_replays: int = 0  # Crucible/Conduit of Worlds: terreno do cemiterio jogado
    interaction_plays: int = 0  # metrica obrigatoria #10: remocao/protecao conjurada
    first_finisher_turn: Optional[int] = None  # metrica obrigatoria #10: finisher/lethality (proxy)
    wrenn_minus2_activations: int = 0
    wrenn_plus1_activations: int = 0
    wrenn_ultimate_activations: int = 0
    wrenn_emblem: bool = False  # -7: play lands/cast permanent spells do cemiterio
    spells_cast_this_turn: int = 0  # Conduit of Worlds: "if you haven't cast a spell this turn"
    conduit_lockout: bool = False  # Conduit of Worlds: "can't cast additional spells this turn"
    conduit_reanimations: int = 0
    urza_saga_chapter2_tokens: int = 0
    urza_saga_chapter3_tutors: int = 0
    legend_rule_sacrifices: int = 0  # Ultron copiando permanente Legendary -> token sacrificado (regra do lendario)


def mk_perm(state: GameState, name: str) -> Permanent:
    p = Permanent(card=CARD_DB[name], entered_turn=state.turn, uid=state.next_uid)
    state.next_uid += 1
    return p


# ---------------------------------------------------------------------------
# Type helpers (dynamic — depend on Toph/Ashaya/Mycosynth being in play)
# ---------------------------------------------------------------------------

def is_artifact(perm: Permanent, state: GameState) -> bool:
    if perm.card.ctype in ARTIFACT_ISH:
        return True
    if state.mycosynth_in_play:
        return True  # Mycosynth Lattice: all permanents are artifacts
    if perm.temp_artifact_until_turn is not None:
        if state.turn > perm.temp_artifact_until_turn:
            perm.temp_artifact_until_turn = None  # Liquimetal: "until end of turn", expirou
        else:
            return True
    return False


def is_creature_type(perm: Permanent, state: GameState) -> bool:
    if perm.temp_creature_until_turn is not None and state.turn > perm.temp_creature_until_turn:
        perm.temp_creature_until_turn = None  # Wrenn +1: expirou ("until your next turn")
    return (perm.card.ctype in CREATURE_ISH or perm.earthbent
            or "always_creature" in perm.card.tags or perm.forced_creature
            or perm.temp_creature_until_turn is not None)


def is_land(perm: Permanent, state: GameState) -> bool:
    if perm.card.ctype == "land":
        return True
    if perm.is_token:
        return False  # Toph/Ashaya so afetam permanentes NAO-TOKEN
    if state.commander_in_play and is_artifact(perm, state):
        return True  # Toph: nontoken artifacts are lands
    if state.ashaya_in_play and perm.card.ctype in ("creature", "artifact_creature", "enchantment_creature"):
        return True  # Ashaya: nontoken creatures are lands
    return False


def distinct_land_names(state: GameState) -> int:
    return len({p.card.name for p in state.battlefield if is_land(p, state)})


# ---------------------------------------------------------------------------
# Core zone-change machinery — this is where Motor #16 lives
# ---------------------------------------------------------------------------

def leave_battlefield(state: GameState, perm: Permanent, log: list, to_hand: bool = False):
    """Handles a permanent dying / being sacrificed / exiled. Central place
    for The Ozolith (counter recycling) and Motor #16 (earthbend return)."""
    if perm not in state.battlefield:
        # Ja saiu do campo por outro efeito (ex: bounce land disparado por uma
        # cadeia de landfall/Motor#16 no meio do processamento de um sacrificio
        # em lote, como Planar Engineering) — nada a fazer.
        return
    state.battlefield.remove(perm)

    if perm.counters > 0 and any(p.card.name == "The Ozolith" for p in state.battlefield):
        state.ozolith_counters += perm.counters
        state.ozolith_moves += 1
        log.append(f"  [Ozolith] recicla {perm.counters} contadores de {perm.card.name}")

    # Ichor Wellspring: draw on entering graveyard from battlefield
    if perm.card.name == "Ichor Wellspring" and not to_hand:
        draw_cards(state, 1, log, source="Ichor Wellspring (morte)")

    if perm.card.name == "Haywire Mite" and not to_hand:
        gain_life(state, 2, log, source="Haywire Mite (morte)")

    if perm.earthbend_return and not to_hand:
        # Motor #16: return to the battlefield tapped instead of staying dead.
        state.motor16_recursions += 1
        new_perm = mk_perm(state, perm.card.name)
        new_perm.tapped = True
        log.append(f"  [Motor#16] {perm.card.name} earthbendada volta ao campo tapped (recorrencia)")
        enter_battlefield(state, new_perm, log)
        return

    if to_hand:
        state.hand.append(perm.card.name)
    else:
        state.graveyard.append(perm.card.name)


def enter_battlefield(state: GameState, perm: Permanent, log: list):
    state.battlefield.append(perm)

    if perm.card.name == COMMANDER:
        state.commander_in_play = True
    if perm.card.name == "Ashaya, Soul of the Wild":
        state.ashaya_in_play = True
    if perm.card.name == "Mycosynth Lattice":
        state.mycosynth_in_play = True
    if perm.card.name in FINISHER_CARDS and state.first_finisher_turn is None:
        state.first_finisher_turn = state.turn

    if is_land(perm, state):
        landfall_trigger(state, perm, log)

    if is_creature_type(perm, state):
        kodama_trigger(state, perm, log)

    # Achado real 2026-09-01 (usuario: "quero que vc compile TUDO... SEMPRE"):
    # The Great Henge ("Whenever a nontoken creature you control enters,
    # put a +1/+1 counter on it and draw a card") so' tinha um PROXY no
    # proprio ETB do Henge (achado de 2026-08-28, nunca corrigido pra
    # virar o gatilho de verdade). Corrigido pra disparar em QUALQUER
    # criatura nao-token que entra depois do Henge estar em campo -- o
    # proprio Henge nunca e' ele mesmo uma criatura neste sim (ctype
    # "artifact", Ashaya so' converte criatura->terreno, nao o contrario),
    # entao nao ha risco de auto-disparo.
    if (is_creature_type(perm, state) and not perm.is_token
            and any(p.card.name == "The Great Henge" for p in state.battlefield if p is not perm)):
        perm.counters += 1
        draw_cards(state, 1, log, source="The Great Henge (criatura nao-token entra)")
        log.append(f"  [The Great Henge] +1/+1 em {perm.card.name}, compra 1 carta")

    # Achado real 2026-09-01 (pergunta direta do usuario: "com Mycosynth
    # Lattice + Ultron em campo, qualquer coisa que eu baixar vira copia
    # 2/2?"): SIM, pela regra real -- mas o codigo checava o `ctype`
    # ESTATICO da carta ("artifact"/"artifact_creature"), nao se ela e' um
    # artefato de verdade AGORA (`is_artifact()`, que ja considera
    # Mycosynth Lattice). Sob Mycosynth, QUALQUER permanente nao-token
    # (criatura, terreno, o que for) que entra e' tambem um artefato
    # nao-token de verdade -- Ultron devia disparar nesses casos e nao
    # disparava. Corrigido pra usar `is_artifact()`.
    if is_artifact(perm, state) and not perm.is_token and perm.card.name != "Ultron, Artificial Malevolence":
        ultron_trigger(state, perm, log)

    apply_etb(state, perm, log)

    # Regra do lendario (achado real 2026-09-01, pergunta direta do usuario
    # sobre Krang, Utrom Warlord): SBA real de MTG -- se um jogador controla
    # 2+ permanentes lendarios com o mesmo nome, ele escolhe 1 e sacrifica o
    # resto. So alcancavel neste sim via Ultron copiando um artefato
    # lendario nao-token (Krang, Mox Opal, The Great Henge, Iron Spider,
    # The Ozolith, The Stasis Coffin -- o proprio Ultron nao dispara copia
    # de si mesmo, ver acima) ou, em tese, Conduit of Worlds reanimando um
    # lendario do cemiterio enquanto outra copia ja esta em campo. Nenhum
    # lugar do codigo checava isso antes -- o token ficava em campo lado a
    # lado com o original, estado de jogo ilegal. Mantem o mais antigo
    # (menor uid -- o original, que pode ja ter contador/estado acumulado
    # como Ozolith/Stasis Coffin), sacrifica o(s) mais novo(s).
    if "legendary" in perm.card.tags:
        same_name = [p for p in state.battlefield if p.card.name == perm.card.name]
        if len(same_name) > 1:
            oldest = min(same_name, key=lambda p: p.uid)
            for dup in same_name:
                if dup is not oldest:
                    state.legend_rule_sacrifices += 1
                    log.append(f"  [Legend rule] {dup.card.name} sacrificada -- ja havia outro "
                               f"permanente lendario com esse nome em campo")
                    leave_battlefield(state, dup, log)


def ultron_trigger(state: GameState, entering_perm: Permanent, log: list):
    ultron = next((p for p in state.battlefield if p.card.name == "Ultron, Artificial Malevolence"
                    and p is not entering_perm), None)
    if ultron is None:
        return
    # Achado real 2026-09-01 (pergunta do usuario sobre Krang, Utrom
    # Warlord): copiar um permanente LENDARIO cria um token com o mesmo
    # nome do original que ja esta em campo -- morre IMEDIATAMENTE pela
    # regra do lendario (ver checagem em `enter_battlefield()`), sem
    # nenhum ETB/valor pro token (nenhum dos lendarios copiaveis por
    # Ultron nesta lista -- Krang, Mox Opal, The Great Henge, Iron Spider,
    # The Ozolith, The Stasis Coffin -- tem ETB modelado). "You may pay
    # {2}" e' opcional; nenhum piloto racional paga mana por um token
    # garantido-morto-ao-nascer. Isso NAO e' julgamento de valor da
    # habilidade (Regra "compile TUDO"), e' reconhecer que o resultado da
    # copia e' zero garantido pela propria regra do lendario -- mesmo
    # principio ja usado em "sem alvo legal, a habilidade nao faz nada".
    if "legendary" in entering_perm.card.tags:
        log.append(f"  [Ultron] NAO copia {entering_perm.card.name} (lendario -- token morreria de graca "
                    f"pela regra do lendario, sem ETB/valor nenhum)")
        return
    if remaining_mana(state) < 2:
        return
    spend_mana(state, 2)
    token = mk_perm(state, entering_perm.card.name)
    token.is_token = True
    # Achado real 2026-09-01 (Partida manual #2, turno 5, visto ao vivo:
    # Ultron copiou Liquimetal Torque): "If the token isn't a creature, it
    # becomes a 2/2 Robot Villain creature in addition to its other
    # types." O `ctype` normal e' por definicao de carta (compartilhado
    # entre todas as copias), entao um campo dedicado por instancia
    # (`forced_creature`) marca so' esse token especifico como criatura --
    # relevante pra alvo do Bristly Bill/gatilhos de "whenever you attack"/
    # etc. Sem P/T rastreado (docstring), o "2/2" em si nao e' um numero
    # que este simulador modifica em lugar nenhum, so' o status de
    # criatura muda.
    if not is_creature_type(token, state):
        token.forced_creature = True
        log.append(f"  [Ultron] copia de {entering_perm.card.name} vira 2/2 Robot Villain creature")
    create_token(state, log, note=f"copia de {entering_perm.card.name} via Ultron")
    log.append(f"  [Ultron] copia {entering_perm.card.name} (token)")
    enter_battlefield(state, token, log)


def kodama_trigger(state: GameState, entering_perm: Permanent, log: list):
    if not any(p.card.name == "Kodama of the East Tree" for p in state.battlefield if p is not entering_perm):
        return
    if entering_perm.card.name == "Kodama of the East Tree":
        return
    cheap = [n for n in state.hand if CARD_DB[n].mv <= entering_perm.card.mv and CARD_DB[n].ctype != "instant"
             and CARD_DB[n].ctype != "sorcery" and n != COMMANDER]
    if cheap:
        cheap.sort(key=lambda n: -CARD_DB[n].mv)
        choice = cheap[0]
        state.hand.remove(choice)
        state.kodama_cheats += 1
        log.append(f"  [Kodama] cheat-into-play: {choice} de graca")
        new_perm = mk_perm(state, choice)
        enter_battlefield(state, new_perm, log)


# ---------------------------------------------------------------------------
# Landfall dispatcher
# ---------------------------------------------------------------------------

def landfall_trigger(state: GameState, land_perm: Permanent, log: list):
    state.landfalls_this_turn += 1
    state.landfall_triggers_fired += 1

    for p in list(state.battlefield):
        tags = p.card.tags
        if "landfall_mana" in tags:
            state.mana_generated_extra += 1
        if "landfall_token" in tags and p.card.name == "Tireless Provisioner":
            if state.treasures < 3:
                state.treasures += 1
            else:
                state.foods += 1
            create_token(state, log)
        if "landfall_counter" in tags:
            # Bristly Bill: "put a +1/+1 counter on TARGET CREATURE" -- achado
            # real 2026-09-01, mirava `best_earthbend_target` (qualquer
            # terreno, nem sempre uma criatura de verdade). Ver `best_creature_target`.
            target = best_creature_target(state)
            if target:
                target.counters += 1
        if "landfall_double_self" in tags and p.card.name == "Mossborn Hydra":
            p.counters *= 2
        if "landfall_dmg" in tags:
            pass  # Tannuk direct damage: sem oponente real, nao modelado
        if "landfall_draw_2nd" in tags and state.landfalls_this_turn == 2:
            draw_cards(state, 1, log, source="Tannuk (2o landfall)")
        if "landfall_dig_2nd" in tags and state.landfalls_this_turn == 2:
            draw_cards(state, 1, log, source="Nissa Resurgent Animist (2o landfall)")
        if "landfall_experience" in tags:
            state.experience_counters += 1
        if "landfall_quest" in tags and p.card.name == "Earthbender Ascension":
            p.counters += 1
            if p.counters >= 4:
                # "put a +1/+1 counter on TARGET CREATURE you control" --
                # mesmo bug de alvo do Bristly Bill, mesmo fix.
                target = best_creature_target(state)
                if target:
                    target.counters += 1
        if "landfall_token_or_copy" in tags and p.card.name == "Scute Swarm":
            lands_ct = sum(1 for x in state.battlefield if is_land(x, state))
            # Scute Swarm com 6+ terrenos e genuinamente exponencial no jogo real
            # (cada copia tambem copia no proximo landfall) — cap defensivo de
            # implementacao pra manter a simulacao tratavel; contado a parte,
            # nao escondido (ver SCUTE_SWARM_CAP_HITS).
            if lands_ct >= 6 and len(state.battlefield) < 200:
                clone = mk_perm(state, "Scute Swarm")
                clone.is_token = True
                create_token(state, log)
                state.battlefield.append(clone)  # copy doesn't retrigger landfall dispatch
            elif lands_ct >= 6:
                state.scute_swarm_cap_hits += 1
            else:
                create_token(state, log)
        if "landfall_token" in tags and p.card.name == "Sapling Nursery":
            create_token(state, log)
        if "landfall_token" in tags and p.card.name == "Springheart Nantuko":
            # Achado real 2026-09-01 (documentacao, sem mudanca de
            # comportamento): a habilidade real e' um modal -- "you may pay
            # {1}{G} if this permanent is attached to a creature you
            # control. If you do, create a token that's a copy of that
            # creature. If you didn't create a token this way, create a 1/1
            # Insect." Bestow (o unico jeito de "attached to a creature")
            # ja e' documentado fora de escopo (mecanismo de custo
            # alternativo, arquitetura de `mv` fixo por carta) -- entao
            # essa carta SEMPRE cai no fallback (1/1 Insect), nunca no modo
            # de copia. Consequencia direta do Bestow nao ser modelado, nao
            # um bug novo.
            create_token(state, log)
        if "landfall_choice" in tags:
            # Felidar Retreat, modal real: "Create a 2/2 Cat Beast token." OU
            # "Put a +1/+1 counter on EACH creature you control. Those
            # creatures gain vigilance until end of turn." Achado real
            # 2026-09-01: o codigo antigo mirava so' 1 permanente qualquer
            # (nem sempre criatura de verdade) em vez de TODAS as criaturas,
            # e nao modelava a escolha como as 2 opcoes reais do modal (so'
            # tinha 1 modo com fallback condicional). Politica: contador em
            # todas quando ja existem 2+ criaturas de verdade em campo (mais
            # valor total, alimenta Bristly Bill/Ozolith); senao token (mais
            # util com 0-1 criatura). Vigilance nao importa neste modelo
            # (sem combate real).
            creatures = [p for p in state.battlefield if is_creature_type(p, state)]
            if len(creatures) >= 2:
                for c in creatures:
                    c.counters += 1
            else:
                create_token(state, log)

    # Field of the Dead — verifica a cada terreno que entra (o proprio ou outro)
    if distinct_land_names(state) >= 7:
        state.field_of_the_dead_tokens += 1
        create_token(state, log)


def draw_cards(state: GameState, n: int, log: list, source: str = ""):
    for _ in range(n):
        if state.library:
            state.hand.append(state.library.pop(0))
            state.cards_drawn_extra += 1


def create_token(state: GameState, log: list, note: str = ""):
    """Contabiliza um token generico (Field of the Dead zombie, Insect, Cat
    Beast, etc — coisas que nao precisam virar Permanent de verdade porque
    nao interagem com landfall/earthbend). Dispara Caretaker's Talent."""
    state.tokens_created += 1
    if not state.token_drawn_this_turn and any(p.card.name == "Caretaker's Talent" for p in state.battlefield):
        draw_cards(state, 1, log, source="Caretaker's Talent (token entra)")
        state.token_drawn_this_turn = True


def gain_life(state: GameState, n: int, log: list, source: str = ""):
    state.life_total += n
    state.life_gained += n


def best_earthbend_target(state: GameState) -> Optional[Permanent]:
    """Prioridade depende de EARTHBEND_TARGET_POLICY:
    - narrow: so RECURRING_TARGETS (4 cartas com ability de sacrificio propria).
    - broad_artifact: RECURRING_TARGETS primeiro, depois QUALQUER um dos 26
      artefatos nao-token (podem virar mana via Krark-Clan Ironworks e voltar
      de graca pelo Motor #16), depois terreno comum.
    - land_only: nunca mira artefato, so terreno real (controle).
    Fallback final em qualquer politica: terreno normal ainda nao
    earthbendado, senao qualquer terreno."""
    candidates = [p for p in state.battlefield if is_land(p, state)]
    if not candidates:
        return None

    if EARTHBEND_TARGET_POLICY == "land_only":
        real_lands_fresh = [p for p in candidates if p.card.ctype == "land" and not p.earthbent]
        if real_lands_fresh:
            return real_lands_fresh[0]
        fresh = [p for p in candidates if not p.earthbent]
        return fresh[0] if fresh else candidates[0]

    for p in candidates:
        if p.card.name in RECURRING_TARGETS and not p.earthbend_return:
            return p

    if EARTHBEND_TARGET_POLICY == "broad_artifact":
        other_artifacts = [p for p in candidates
                            if p.card.ctype in ARTIFACT_ISH and not p.is_token
                            and not p.earthbent and p.card.name not in RECURRING_TARGETS]
        if other_artifacts:
            return other_artifacts[0]

    fresh = [p for p in candidates if not p.earthbent]
    if fresh:
        return fresh[0]
    return candidates[0]


def best_creature_target(state: GameState) -> Optional[Permanent]:
    """Achado real 2026-09-01: Bristly Bill ("put a +1/+1 counter on TARGET
    CREATURE") e Earthbender Ascension 4o contador ("put a +1/+1 counter on
    TARGET CREATURE you control") miravam `best_earthbend_target()` — que
    escolhe qualquer TERRENO, nao necessariamente uma criatura de verdade
    (so vira criatura depois de earthbendado). Um terreno comum, ainda nao
    earthbendado, nao e' um alvo legal pra "target creature" — bug de
    legalidade de alvo. Corrigido: prefere o alvo de earthbend se ele ja for
    uma criatura de verdade, senao cai pra qualquer outra criatura real em
    campo; sem candidato legal, retorna None (habilidade nao faz nada, como
    fixaria um jogador real sem alvo)."""
    eb = best_earthbend_target(state)
    if eb is not None and is_creature_type(eb, state):
        return eb
    creatures = [p for p in state.battlefield if is_creature_type(p, state)]
    return creatures[0] if creatures else None


def apply_earthbend(state: GameState, amount: int, log: list, source: str) -> Optional[Permanent]:
    target = best_earthbend_target(state)
    if target is None or amount <= 0:
        return None
    target.counters += amount
    target.earthbent = True
    target.earthbend_return = True
    state.earthbend_applications += 1
    state.earthbend_by_source[source] = state.earthbend_by_source.get(source, 0) + 1
    log.append(f"  [Earthbend {amount}] via {source} -> {target.card.name} ({target.counters} contadores)")
    maybe_earth_kingdom_general_lifegain(state, log, target, amount)

    if any(p.card.name == "Strionic Resonator" and not p.tapped for p in state.battlefield):
        res = next(p for p in state.battlefield if p.card.name == "Strionic Resonator" and not p.tapped)
        if remaining_mana(state) >= 2:
            res.tapped = True
            spend_mana(state, 2)
            target.counters += amount
            state.resonator_copies += 1
            log.append(f"  [Strionic Resonator] copia o earthbend -> +{amount} contadores extra em {target.card.name}")
    return target


def maybe_earth_kingdom_general_lifegain(state: GameState, log: list, target: Permanent, amount: int):
    """Achado real 2026-09-01: Earth Kingdom General ("Whenever you put one
    or more +1/+1 counters on a creature, you may gain that much life. Do
    this only once each turn") tinha a tag `counter_lifegain` sem NENHUM
    dispatch — nunca implementada. Ligada aqui em `apply_earthbend()`, o
    caminho central de praticamente toda contagem de +1/+1 counter em
    criatura neste sim (todos os ETBs de earthbend, Ba Sing Se/Avatar
    Kyoshi/Toph Earthbending Master em combate, Earthshape). Escopo
    explicito: NAO ligada em outros caminhos que tambem adicionam counter
    (dobra do Bristly Bill/Mossborn Hydra landfall, realocacao do Ozolith,
    contador de quest do Earthbender Ascension) -- cobrir TODOS exigiria
    instrumentar cada `p.counters +=`/`*=` do arquivo por um ganho de vida
    secundario de baixo impacto; decisao de escopo, nao omissao silenciosa."""
    if target is None or amount <= 0 or not is_creature_type(target, state):
        return
    if state.counter_lifegain_this_turn:
        return
    if not any(p.card.name == "Earth Kingdom General" for p in state.battlefield):
        return
    state.counter_lifegain_this_turn = True
    gain_life(state, amount, log, source="Earth Kingdom General (contadores)")
    log.append(f"  [Earth Kingdom General] ganha {amount} de vida (contadores em {target.card.name})")


# ---------------------------------------------------------------------------
# ETB effects (one-shot, card-specific)
# ---------------------------------------------------------------------------

def apply_etb(state: GameState, perm: Permanent, log: list):
    name = perm.card.name
    if name == "Mossborn Hydra":
        perm.counters += 1
    if name == "Badgermole Cub":
        apply_earthbend(state, 1, log, "Badgermole Cub (ETB)")
    elif name == "Bumi, Eclectic Earthbender":
        apply_earthbend(state, 1, log, "Bumi (ETB)")
    elif name == "Earth Kingdom General":
        apply_earthbend(state, 2, log, "Earth Kingdom General (ETB)")
    elif name == "Earthbender Ascension":
        apply_earthbend(state, 2, log, "Earthbender Ascension (ETB)")
        # Achado real 2026-09-01 (2a passada da revisao de oraculo): "Then
        # search your library for a basic land card, put it onto the
        # battlefield tapped, then shuffle" -- so' o earthbend estava
        # implementado, esse segundo efeito (ramp real) nunca tinha
        # dispatch nenhum.
        basics = [n for n in state.library if n in BASIC_LAND_NAMES]
        if basics:
            found = basics[0]
            state.library.remove(found)
            land_perm = mk_perm(state, found)
            land_perm.tapped = True
            log.append(f"  [Earthbender Ascension] busca {found} tapped pro campo")
            enter_battlefield(state, land_perm, log)
    elif name == "Earthbending Student":
        apply_earthbend(state, 2, log, "Earthbending Student (ETB)")
    elif name == "Talon Gates of Madara":
        # "When this land enters, up to one target creature phases out."
        # Achado real 2026-09-02: usada pra proteger a PROPRIA criatura
        # mais valiosa (comandante primeiro, senao a de maior MV), nao so
        # remocao de oponente. Ver comentario completo no add() acima.
        protect_target = None
        commander_perm = next((p for p in state.battlefield if p.card.name == COMMANDER
                                and is_creature_type(p, state)), None)
        if commander_perm is not None:
            protect_target = commander_perm
        else:
            own_creatures = [p for p in state.battlefield if is_creature_type(p, state) and p is not perm]
            if own_creatures:
                protect_target = max(own_creatures, key=lambda p: p.card.mv)
        if protect_target is not None:
            state.talon_gates_protections += 1
            log.append(f"  [Talon Gates of Madara] fase fora {protect_target.card.name} (protecao)")
    elif name == "Toph, Greatest Earthbender":
        apply_earthbend(state, perm.card.mv, log, "Toph Greatest Earthbender (ETB, X=mana gasto)")
    elif name == "Spelunking":
        draw_cards(state, 1, log, source="Spelunking (ETB)")
        # Achado real 2026-09-01: "then you may put a land card from your
        # hand onto the battlefield" -- so' a compra estava implementada.
        # (O bonus de vida e' condicional a "if you put a Cave onto the
        # battlefield" -- nenhuma Cave na lista, N/A estrutural.) Essa
        # colocacao NAO usa o land-drop normal do turno (efeito a parte).
        lands_in_hand = [n for n in state.hand if is_land_name(n)]
        if lands_in_hand:
            choice = lands_in_hand[0]
            state.hand.remove(choice)
            land_perm = mk_perm(state, choice)
            resolve_land_enters_tapped(state, land_perm, choice)
            log.append(f"  [Spelunking] coloca {choice} da mao no campo (bonus, fora do land-drop do turno)")
            enter_battlefield(state, land_perm, log)
    elif name == "Ichor Wellspring":
        draw_cards(state, 1, log, source="Ichor Wellspring (ETB)")
    elif name == "Overlord of the Hauntwoods":
        create_token(state, log)
        everywhere = mk_perm(state, "Everywhere Token")
        everywhere.is_token = True
        everywhere.tapped = True
        enter_battlefield(state, everywhere, log)
    elif name == "Gruul Turf" or name == "Selesnya Sanctuary":
        # Bounceland: "return a land you control to its owner's hand" --
        # mandatorio (nao "up to one"). Achado real 2026-09-01 (Partida
        # manual #1, turno 1, visto ao vivo): se nao ha OUTRO terreno em
        # campo, a regra real obriga devolver A SI MESMA (ainda e' "a land
        # you control" -- so' nao existe outro candidato). O codigo antigo
        # so' devolvia quando havia outro terreno, deixando a bounceland
        # de graca em campo nesse cenario especifico (bounceland como 1o
        # terreno da mesa) -- errado, corrigido com fallback pra si mesma.
        others = [p for p in state.battlefield if is_land(p, state) and p is not perm]
        bounced = others[0] if others else perm
        state.battlefield.remove(bounced)
        state.hand.append(bounced.card.name)
    elif name == "Wrenn and Realmbreaker":
        state.wrenn_loyalty = 4  # lealdade inicial real (Scryfall)
    elif name == "Urza's Saga":
        perm.saga_chapter = 1  # "as this Saga enters... add a lore counter"


# ---------------------------------------------------------------------------
# Mana model (generico — ver nota de simplificacao no docstring)
# ---------------------------------------------------------------------------

def total_mana(state: GameState) -> int:
    total = 0
    for p in state.battlefield:
        if p.tapped:
            continue
        tags = p.card.tags
        land = is_land(p, state)
        if land:
            # Achado real 2026-08-28 (auditoria de checklist de mecanica):
            # Command Tower/Jetmir's Garden/Talon Gates of Madara sao
            # terrenos tagueados "rock_any"/"rock_any_paid" - antes ganhavam
            # +1 aqui E +1 de novo no bloco de rock abaixo (double count,
            # um unico {T} contando 2x). A habilidade colorida delas E' a
            # unica habilidade de mana real (Command Tower/Jetmir's Garden)
            # ou um conversor liquido-zero (Talon Gates: paga {1} extra pra
            # trocar por qualquer cor - sem ganho de mana total, so' fixacao,
            # que esse modelo generico nao rastreia por cor de qualquer
            # forma). Nenhuma delas soma mana ALEM do +1 de terreno normal.
            total += 1
        elif "rock_any" in tags or "rock1" in tags or "rock_any_paid" in tags:
            total += 1
        elif "rock2" in tags or "rock2life" in tags:
            total += 2
        elif "rock_metalcraft" in tags:
            n_art = sum(1 for x in state.battlefield if is_artifact(x, state))
            if n_art >= 3:
                total += 1
        if "creature_mana_any" in tags:
            # Enduring Vitality: TODA criatura sua tapa por 1 de qualquer cor.
            # Achado real 2026-08-28 (auditoria de checklist): nunca checava
            # doenca de invocacao (CR 302.6) - criaturas recem-conjuradas
            # contribuiam mana no proprio turno em que entravam.
            n_creatures = sum(1 for x in state.battlefield
                               if is_creature_type(x, state) and not x.tapped and x is not p
                               and x.entered_turn < state.turn)
            total += n_creatures
            # Badgermole Cub: "Whenever you tap a creature for mana, add an
            # additional {G}." Achado real 2026-09-01 -- essa segunda
            # habilidade (a primeira, earthbend 1 no ETB, ja era simulada)
            # nunca tinha dispatch nenhum. So' importa quando algo de fato
            # tapa criatura por mana neste modelo generico -- ou seja,
            # combinado com Enduring Vitality (unica fonte de mana-por-
            # criatura simulada aqui).
            if n_creatures and any(x.card.name == "Badgermole Cub" for x in state.battlefield):
                total += n_creatures
    total += state.treasures
    return total


def remaining_mana(state: GameState) -> int:
    return max(0, total_mana(state) - state.mana_spent_this_turn)


def spend_mana(state: GameState, n: int):
    state.mana_spent_this_turn += n


def can_cast(state: GameState, name: str) -> bool:
    return remaining_mana(state) >= CARD_DB[name].mv


def commander_effective_mv(state: GameState) -> int:
    return CARD_DB[COMMANDER].mv + 2 * state.commander_cast_count


def can_cast_commander(state: GameState) -> bool:
    if state.commander_in_play:
        return False
    return remaining_mana(state) >= commander_effective_mv(state)


# ---------------------------------------------------------------------------
# Casting
# ---------------------------------------------------------------------------

def cast_card(state: GameState, name: str, log: list, from_hand: bool = True):
    card = CARD_DB[name]
    state.spells_cast_this_turn += 1
    if card.tags & INTERACTION_TAGS:
        state.interaction_plays += 1
    if name == COMMANDER:
        spend_mana(state, commander_effective_mv(state))
    else:
        spend_mana(state, card.mv)
    if from_hand and name in state.hand:
        state.hand.remove(name)

    if card.ctype in ("instant", "sorcery"):
        resolve_instant_sorcery(state, name, log)
        state.graveyard.append(name)
        return

    perm = mk_perm(state, name)
    if name == COMMANDER:
        state.commander_cast_count += 1
        if state.commander_cast_turn is None:
            state.commander_cast_turn = state.turn
        log.append(f"  [Comandante] Toph conjurada (turno {state.turn})")
    enter_battlefield(state, perm, log)


def resolve_instant_sorcery(state: GameState, name: str, log: list):
    if name == "Awaken the Woods":
        # Achado real 2026-09-01: "Create X 1/1 ... tokens" com X real
        # podendo ser 0 (custo base e' so' {G}{G}, `mv=2` no CARD_DB) --
        # o codigo antigo forcava `max(1, ...)`, criando 1 token de graca
        # mesmo com 0 mana extra sobrando, E nunca deduzia o custo de X da
        # mana disponivel (mana infinita de fato). Corrigido: minimo 0,
        # X realmente pago. Cap de 4 e' decisao de politica pre-existente
        # (nao relacionada a esse bug), mantido como estava.
        x = max(0, min(4, remaining_mana(state)))
        if x > 0:
            spend_mana(state, x)
        for _ in range(x):
            token = mk_perm(state, "Forest Dryad Token")
            token.is_token = True
            create_token(state, log)
            enter_battlefield(state, token, log)
    elif name == "Enlightened Tutor":
        # Achado real 2026-09-01: um dos 3 Game Changers da lista, e
        # estava 100% sem implementacao (so' registrada no CARD_DB, tag
        # `tutor_artifact_enchant` sem dispatch nenhum). "Search your
        # library for an artifact or enchantment card, reveal it, then
        # shuffle and put that card on top" -- vai pro TOPO da biblioteca,
        # nao pra mao (proxima compra e' garantida ser essa carta).
        pool = [n for n in state.library
                if CARD_DB[n].ctype in ARTIFACT_ISH
                or CARD_DB[n].ctype in ("enchantment", "enchantment_creature")]
        if pool:
            found = next((n for n in ARTIFACT_TUTOR_PRIORITY if n in pool), None)
            if found is None:
                pool.sort(key=lambda n: -CARD_DB[n].mv)
                found = pool[0]
            state.library.remove(found)
            state.library.insert(0, found)
            log.append(f"  [Enlightened Tutor] busca {found}, topo da biblioteca")
    elif name == "Planar Engineering":
        sac = [p for p in state.battlefield if is_land(p, state)][:2]
        for p in sac:
            leave_battlefield(state, p, log)
        basics = ("Forest", "Plains", "Mountain",
                  "Snow-Covered Forest", "Snow-Covered Mountain", "Snow-Covered Plains")
        for _ in range(4):
            # Reavalia a biblioteca a cada iteracao (nao uma lista congelada) —
            # um landfall no meio do loop (Tannuk/Nissa 2o gatilho) pode
            # comprar cartas e mudar o que ainda esta disponivel.
            found = next((c for c in state.library if c in basics), None)
            if found is None:
                break
            state.library.remove(found)
            perm = mk_perm(state, found)
            perm.tapped = True
            enter_battlefield(state, perm, log)
    elif name == "Germination Practicum":
        for p in state.battlefield:
            if is_creature_type(p, state):
                p.counters += 2
        # Achado real 2026-09-01 (2a passada da revisao de oraculo):
        # "Paradigm" ("After you first resolve a spell with this name, you
        # may cast a copy of it from exile without paying its mana cost at
        # the beginning of each of your first main phases") nunca era
        # modelado -- so' o efeito do 1o cast estava implementado, sem o
        # recast gratuito repetido todo turno seguinte. Flag ligada aqui;
        # dispatch em `main_phase()` (uma vez por turno, a partir do
        # PROXIMO turno -- essa mesma chamada ja aplicou o efeito de hoje).
        state.germination_practicum_active = True
    elif name == "Earthshape":
        apply_earthbend(state, 3, log, "Earthshape (instant)")
    elif name in ("Erode", "Swords to Plowshares", "Council's Judgment"):
        # removal: sem alvo de oponente real num goldfish solo. "Bridgeworks
        # Battle" (sem "// Tanglespan Bridgeworks") removido daqui 2026-09-01
        # -- codigo morto, esse MDFC e' registrado so' como land (ctype=="land"),
        # nunca passa por `cast_card()`/`resolve_instant_sorcery()`.
        pass


# ---------------------------------------------------------------------------
# Deck construction / mulligan
# ---------------------------------------------------------------------------

def build_library():
    lib = []
    lines = open("lista.md").read().split("## Lista completa")[1].strip().split("\n")[1:]
    import re
    for l in lines:
        l = l.strip()
        if not l:
            continue
        m = re.match(r"^(\d+)\s+(.+)$", l)
        qty, name = int(m.group(1)), m.group(2).strip()
        assert name in CARD_DB, f"faltando no CARD_DB: {name}"
        for _ in range(qty):
            lib.append(name)
    assert len(lib) == 99, len(lib)
    return lib


BASE_LIBRARY = build_library()


def should_keep(hand: list) -> bool:
    lands = sum(1 for n in hand if is_land_name(n))
    good_ramp = {"Sol Ring", "Arcane Signet", "Lotus Cobra", "Unstable Obelisk"}
    if lands >= 3:
        return True
    if lands == 2 and any(n in good_ramp for n in hand):
        return True
    return False


def is_land_name(name: str) -> bool:
    return CARD_DB[name].ctype == "land"


def has_card(state: GameState, name: str) -> bool:
    return any(p.card.name == name for p in state.battlefield)


def draw_opening_hand(rng: random.Random):
    lib = BASE_LIBRARY[:]
    rng.shuffle(lib)
    hand = lib[:7]
    lib = lib[7:]
    return hand, lib


def mulligan(rng: random.Random, max_mulls: int = 3):
    mulls = 0
    while mulls < max_mulls:
        hand, lib = draw_opening_hand(rng)
        if should_keep(hand) or mulls == max_mulls - 1:
            # London mulligan: bottom `mulls` cards
            if mulls > 0:
                rng.shuffle(hand)
                bottom = hand[:mulls]
                hand = hand[mulls:]
                lib = lib + bottom
            return hand, lib, mulls
        mulls += 1
    return hand, lib, mulls


# ---------------------------------------------------------------------------
# Turn structure
# ---------------------------------------------------------------------------

# Pools reais de busca por fetch (Scryfall) - achado real 2026-08-28.
FETCH_POOLS = {
    "Arid Mesa": ("Mountain", "Plains", "Snow-Covered Mountain", "Snow-Covered Plains"),
    "Windswept Heath": ("Forest", "Plains", "Snow-Covered Forest", "Snow-Covered Plains"),
    "Wooded Foothills": ("Mountain", "Forest", "Snow-Covered Mountain", "Snow-Covered Forest"),
}

BASIC_LAND_NAMES = {"Forest", "Mountain", "Plains",
                     "Snow-Covered Forest", "Snow-Covered Mountain", "Snow-Covered Plains"}

# Custo de vida real de cada "enters_tapped_payable" (Scryfall confirmado,
# achado real 2026-09-01) -- nao e' o mesmo pra todas: shock lands
# (Stomping Ground/Temple Garden) pagam 2, a MDFC Tanglespan Bridgeworks
# paga 3. Sem entrada aqui = tag mal aplicada (erro de programacao).
ENTERS_TAPPED_PAYABLE_LIFE = {
    "Stomping Ground": 2,
    "Temple Garden": 2,
    "Bridgeworks Battle // Tanglespan Bridgeworks": 3,
}


def resolve_land_enters_tapped(state: GameState, perm: Permanent, name: str):
    """Decide se um terreno que esta entrando fica tapped. Fatorado (achado
    real 2026-09-01, 2a passada da revisao de oraculo) porque terreno pode
    entrar por 2 caminhos: `play_land()` (land-drop normal) e o ETB do
    Spelunking ("...put a land card from your hand onto the battlefield").
    Horizon Explorer/Spelunking ("Lands you control enter untapped") sao
    estaticas que SOBREPOEM qualquer condicional abaixo -- checadas
    primeiro, curto-circuitam o resto (nem a vida de shock land/MDFC e'
    paga, ja que o terreno entra destapado de graca de qualquer forma)."""
    if has_card(state, "Horizon Explorer") or has_card(state, "Spelunking"):
        return
    tags = CARD_DB[name].tags
    if "enters_tapped" in tags:
        perm.tapped = True
    elif "enters_tapped_payable" in tags:
        cost = ENTERS_TAPPED_PAYABLE_LIFE[name]
        if state.life_total > 10:
            state.life_total -= cost
        else:
            perm.tapped = True
    elif "enters_tapped_unless_basic" in tags:
        if not any(is_land(p, state) and p.card.name in BASIC_LAND_NAMES
                   for p in state.battlefield):
            perm.tapped = True
    elif "enters_tapped_unless_2_basics" in tags:
        n_basics = sum(1 for p in state.battlefield
                       if is_land(p, state) and p.card.name in BASIC_LAND_NAMES)
        if n_basics < 2:
            perm.tapped = True


def play_land(state: GameState, log: list):
    # Achado real 2026-08-31: "extra_land_drop" (Dryad of the Ilysian Grove)
    # era uma tag decorativa sem dispatch nenhum -- `state.extra_land_drops`
    # nunca era incrementado em lugar nenhum do arquivo, entao a estatica
    # "you may play an additional land on each of your turns" nunca fazia
    # nada. Corrigido como efeito continuo (recalculado a cada chamada, nao
    # um contador que precisa reset por turno) enquanto a Dryad estiver em
    # campo. `state.extra_land_drops` continua existindo pra efeitos de UM
    # turno so' (ex: Wrenn +1 real nao foi implementado -- ver
    # `wrenn_loyalty_ability` -- mas o campo fica disponivel pra isso).
    max_drops = 1 + state.extra_land_drops
    if has_card(state, "Dryad of the Ilysian Grove"):
        max_drops += 1

    while state.lands_played_this_turn < max_drops:
        lands_in_hand = [n for n in state.hand if is_land_name(n)]
        from_graveyard = False
        if lands_in_hand:
            # fetches primeiro (deixam a biblioteca mais previsivel / menos "morta")
            fetches = [n for n in lands_in_hand if "fetch" in CARD_DB[n].tags]
            choice = fetches[0] if fetches else lands_in_hand[0]
        elif has_card(state, "Crucible of Worlds") or has_card(state, "Conduit of Worlds") or state.wrenn_emblem:
            # Achado real 2026-08-31: "gy_lands" (Crucible/Conduit of Worlds,
            # "You may play lands from your graveyard") era uma tag
            # decorativa sem dispatch nenhum. Fonte real de terreno no
            # cemiterio neste sim: fetches ja craqueados (unico jeito de um
            # terreno de verdade morrer aqui -- earthbend/KCI/Obelisk/Coffin
            # nunca alvejam terreno REAL nao-artefato, so' artefato). Fetch
            # do cemiterio, jogado de novo, dispara o ETB de fetch de novo
            # (mais 1 basica pro campo) -- motor de recorrencia real.
            lands_in_gy = [n for n in state.graveyard if is_land_name(n)]
            if not lands_in_gy:
                return
            fetches = [n for n in lands_in_gy if "fetch" in CARD_DB[n].tags]
            choice = fetches[0] if fetches else lands_in_gy[0]
            from_graveyard = True
        else:
            return

        if from_graveyard:
            state.graveyard.remove(choice)
            state.crucible_land_replays += 1
        else:
            state.hand.remove(choice)
        state.lands_played_this_turn += 1

        if "fetch" in CARD_DB[choice].tags:
            state.graveyard.append(choice)
            # Achado real 2026-09-01: "{T}, Pay 1 life, Sacrifice this
            # land" -- o custo de vida nunca era pago. Pago mesmo quando
            # vindo do cemiterio via Crucible/Conduit (a habilidade e' a
            # mesma, independente de onde a carta foi jogada de).
            state.life_total -= 1
            # Achado real 2026-08-28 (auditoria de checklist de mecanica):
            # todo fetch buscava dos 6 basicos, ignorando que cada um so'
            # busca 2 tipos reais (Arid Mesa: Mountain/Plains; Windswept
            # Heath: Forest/Plains; Wooded Foothills: Mountain/Forest).
            pool = FETCH_POOLS.get(choice, ("Forest", "Plains", "Mountain",
                    "Snow-Covered Forest", "Snow-Covered Mountain", "Snow-Covered Plains"))
            basics = [n for n in state.library if n in pool]
            if basics:
                fetched = basics[0]
                state.library.remove(fetched)
                perm = mk_perm(state, fetched)
                perm.tapped = False
                enter_battlefield(state, perm, log)
            continue

        perm = mk_perm(state, choice)
        resolve_land_enters_tapped(state, perm, choice)
        enter_battlefield(state, perm, log)


def try_bristly_bill_double(state: GameState, log: list) -> bool:
    bb = next((p for p in state.battlefield if p.card.name == "Bristly Bill, Spine Sower" and not p.tapped), None)
    if bb and remaining_mana(state) >= 5 and any(p.counters > 0 for p in state.battlefield):
        spend_mana(state, 5)
        for p in state.battlefield:
            if p.counters > 0:
                p.counters *= 2
        state.bristly_bill_doubles += 1
        log.append("  [Bristly Bill] dobra todos os contadores do campo")
        return True
    return False


def main_phase(state: GameState, log: list):
    if state.germination_practicum_active:
        # Paradigm: recast de graca (ver `resolve_instant_sorcery`). Roda
        # antes de tudo -- "at the beginning of each of your first main
        # phases", nao compete por mana com o resto do turno.
        for p in state.battlefield:
            if is_creature_type(p, state):
                p.counters += 2
        log.append("  [Germination Practicum] Paradigm: recast de graca, +2 contadores em cada criatura")

    if can_cast_commander(state):
        cast_card(state, COMMANDER, log, from_hand=False)

    conduit_of_worlds_reanimate(state, log)

    if BRISTLY_BILL_RESERVE_POLICY:
        try_bristly_bill_double(state, log)

    held_for_kodama = None
    if not state.conduit_lockout and KODAMA_HOLD_POLICY and any(p.card.name == "Kodama of the East Tree" for p in state.battlefield):
        nonland_perms = [n for n in state.hand
                          if CARD_DB[n].ctype not in ("instant", "sorcery", "land") and n != COMMANDER]
        if nonland_perms:
            nonland_perms.sort(key=lambda n: CARD_DB[n].mv)
            held_for_kodama = nonland_perms[0]
            # NAO remove da mao — kodama_trigger() procura em state.hand
            # quando outro permanente entra, entao a carta precisa continuar
            # la pra ser encontrada. So marca ela como protegida do loop de
            # casting generico abaixo.

    # `conduit_lockout`: se o Conduit reanimou algo esse turno, "can't cast
    # additional spells this turn" -- pula o loop guloso principal E o
    # emblema do Wrenn -7 abaixo (ambos sao "cast a spell").
    if not state.conduit_lockout:
        castables = [n for n in state.hand if CARD_DB[n].ctype != "land" and can_cast(state, n) and n != held_for_kodama]
        castables.sort(key=lambda n: CARD_DB[n].mv)
        for n in castables:
            if n not in state.hand:
                continue
            if not can_cast(state, n):
                continue
            cast_card(state, n, log)
            castables = [x for x in state.hand if CARD_DB[x].ctype != "land" and can_cast(state, x) and x != held_for_kodama]
            castables.sort(key=lambda x: CARD_DB[x].mv)

    # Achado real 2026-09-01 (usuario: "compile TUDO"): Wrenn -7 dá um
    # emblema real ("You may play lands and cast permanent spells from
    # your graveyard") -- a metade de terreno ja e' tratada junto com
    # Crucible/Conduit em `play_land()`; aqui a metade "cast permanent
    # spells" (nao-terreno) do mesmo emblema, mesmo loop guloso do resto
    # do main_phase (ordenado por mv, o mais barato primeiro).
    if state.wrenn_emblem and not state.conduit_lockout:
        gy_castables = [n for n in state.graveyard
                        if CARD_DB[n].ctype not in ("land", "instant", "sorcery") and can_cast(state, n)]
        gy_castables.sort(key=lambda n: CARD_DB[n].mv)
        for n in gy_castables:
            if n not in state.graveyard or not can_cast(state, n):
                continue
            state.graveyard.remove(n)
            log.append(f"  [Wrenn -7, emblema] conjura {n} do cemiterio")
            cast_card(state, n, log, from_hand=False)
            gy_castables = [x for x in state.graveyard
                            if CARD_DB[x].ctype not in ("land", "instant", "sorcery") and can_cast(state, x)]
            gy_castables.sort(key=lambda x: CARD_DB[x].mv)

    # Ba Sing Se: earthbend ativado se sobrar mana
    ba_sing_se = next((p for p in state.battlefield if p.card.name == "Ba Sing Se" and not p.tapped), None)
    if ba_sing_se and remaining_mana(state) >= 3:
        ba_sing_se.tapped = True
        spend_mana(state, 3)
        apply_earthbend(state, 2, log, "Ba Sing Se (ativada)")

    # Bristly Bill: se a reserva antecipada estiver desligada, tenta so agora
    # (comportamento antigo — so com o que sobrou depois do loop ganancioso).
    if not BRISTLY_BILL_RESERVE_POLICY:
        try_bristly_bill_double(state, log)

    # Krark-Clan Ironworks: sacrifica um artefato descartavel por mana se precisar
    kci = next((p for p in state.battlefield if p.card.name == "Krark-Clan Ironworks" and not p.tapped), None)
    if kci:
        pass  # nao usado agressivamente — nao ha spell caro o suficiente pra justificar sacrificar valor

    wrenn_loyalty_ability(state, log)
    liquimetal_activation(state, log)
    bala_ged_recovery_spell_mode(state, log)
    caretaker_talent_levelup(state, log)
    oswald_fiddlebender_tinker(state, log)
    fountainport_abilities(state, log)
    inventors_fair_tutor(state, log)
    iron_spider_abilities(state, log)
    zuran_orb_activation(state, log)

    if RECURRING_ARTIFACT_POLICY:
        work_recurring_artifact_loop(state, log)


def work_recurring_artifact_loop(state: GameState, log: list):
    """Motor #16 de verdade: earthbenda as cartas-alvo (ja priorizado por
    best_earthbend_target) E ativa a habilidade de sacrificio delas quando
    tiver a flag de retorno — sem isso elas so ficam paradas em campo."""

    # Achado real 2026-09-01 (2a passada da revisao de oraculo): Mishra's
    # Bauble estava em RECURRING_TARGETS (earthbend a mira) mas sua PROPRIA
    # habilidade ("{T}, Sacrifice: ... draw a card next upkeep") nunca era
    # ativada de verdade -- so' virava mana pro Krark-Clan Ironworks (custo
    # DIFERENTE, nao dispara o gatilho de draw). `scheduled_draws` existia
    # no GameState e era lido no passo de compra, mas nunca incrementado em
    # lugar nenhum. Ativada aqui, ANTES do bloco de KCI abaixo -- sua
    # propria habilidade (draw agendado) vale mais que virar so' 2 mana
    # generico, e earthbendada ela volta via Motor#16 de qualquer forma.
    bauble = next((p for p in state.battlefield if p.card.name == "Mishra's Bauble" and not p.tapped), None)
    if bauble:
        bauble.tapped = True
        state.scheduled_draws += 1
        log.append("  [Mishra's Bauble] {T}, sacrifica: draw agendado pro proximo upkeep")
        leave_battlefield(state, bauble, log)

    obelisk = next((p for p in state.battlefield if p.card.name == "Unstable Obelisk"
                     and not p.tapped and p.earthbend_return), None)
    if obelisk and remaining_mana(state) >= 7:
        spend_mana(state, 7)
        obelisk.tapped = True
        state.obelisk_activations += 1
        log.append("  [Unstable Obelisk] ativa (destroy target permanent) e e sacrificada")
        leave_battlefield(state, obelisk, log)

    coffin = next((p for p in state.battlefield if p.card.name == "The Stasis Coffin"
                    and not p.tapped and p.earthbend_return), None)
    if coffin and remaining_mana(state) >= 2:
        spend_mana(state, 2)
        coffin.tapped = True
        state.coffin_activations += 1
        log.append("  [The Stasis Coffin] ativa (protecao ate o proximo turno) e e exilada")
        leave_battlefield(state, coffin, log)

    kci = next((p for p in state.battlefield if p.card.name == "Krark-Clan Ironworks" and not p.tapped), None)
    if kci:
        sac_target = next((p for p in state.battlefield
                            if p.card.name in ("Ichor Wellspring", "Mishra's Bauble")
                            and p.earthbend_return), None)
        if sac_target is None and EARTHBEND_TARGET_POLICY == "broad_artifact":
            # Qualquer outro artefato nao-token earthbendado tambem serve —
            # volta de graca pelo Motor #16, entao virar 2 mana dele nao
            # custa o permanente de verdade, so tempo (volta tapped).
            eligible = [p for p in state.battlefield
                        if p.card.ctype in ARTIFACT_ISH and not p.is_token and p.earthbend_return]
            if eligible:
                if SAC_VALUE_PRIORITY_POLICY:
                    eligible.sort(key=lambda p: SAC_VALUE.get(p.card.name, 1))
                sac_target = eligible[0]
                state.kci_sacrifices_broad += 1
        if sac_target:
            state.kci_sacrifices_of_recurring += 1
            log.append(f"  [Krark-Clan Ironworks] sacrifica {sac_target.card.name} (earthbendada) por {{C}}{{C}}")
            leave_battlefield(state, sac_target, log)
            state.mana_generated_extra += 2


def urza_saga_advance(state: GameState, log: list):
    """Engine real de capitulo I/II/III (achado real 2026-08-31, diagnosticado
    na rodada anterior e agora implementado). Chamada 1x por turno, apos o
    passo de compra, antes da main phase -- "as this Saga enters and after
    your draw step, add a lore counter" (timing real do Scryfall). Capitulo I
    e' inerte (so' concede a habilidade de mana que o modelo generico ja da
    a qualquer terreno em campo). Capitulo II concede uma habilidade ATIVADA
    ({2},{T}: cria Construct 0/0) -- ativada de forma gananciosa se sobrar
    mana, igual ao padrao ja usado pra Ba Sing Se/Bristly Bill neste arquivo.
    Capitulo III busca um artefato de custo 0 ou 1 na biblioteca direto pro
    campo, depois sacrifica a Saga (regra 714 de Saga, nao um custo da
    propria carta -- ainda assim conta como "morrer" pro Motor #16: se essa
    copia da Saga tiver sido earthbendada antes, ela volta tapped em vez de
    ir pro cemiterio, reiniciando o ciclo de capitulos do zero -- correto
    per o texto reminder do earthbend, que reage a QUALQUER morte)."""
    saga = next((p for p in state.battlefield if p.card.name == "Urza's Saga"), None)
    if saga is None or saga.saga_chapter >= 3 or saga.entered_turn >= state.turn:
        return
    saga.saga_chapter += 1
    if saga.saga_chapter == 2:
        if not saga.tapped and remaining_mana(state) >= 2:
            spend_mana(state, 2)
            saga.tapped = True
            state.urza_saga_chapter2_tokens += 1
            create_token(state, log, note="Construct 0/0 (Urza's Saga cap. II)")
            log.append("  [Urza's Saga II] {2},{T}: cria Construct 0/0 (+1/+1 por artefato)")
    elif saga.saga_chapter == 3:
        pool = [n for n in state.library if CARD_DB[n].ctype in ARTIFACT_ISH and CARD_DB[n].mv <= 1]
        if pool:
            found = pool[0]
            state.library.remove(found)
            state.urza_saga_chapter3_tutors += 1
            new_perm = mk_perm(state, found)
            log.append(f"  [Urza's Saga III] busca {found} (custo 0/1) direto pro campo")
            enter_battlefield(state, new_perm, log)
        leave_battlefield(state, saga, log)
        log.append("  [Urza's Saga] sacrificada (capitulo III completo, regra 714)")


def wrenn_loyalty_ability(state: GameState, log: list):
    """+1/-2/-7 -- achado real 2026-09-01 (usuario: "nao quero que vc
    decida se a habilidade vai ativar... compile TUDO, SEMPRE"): so' -2
    estava implementada; +1 e -7 tinham ficado de fora por eu ter
    decidido, por conta propria, que nunca valeriam a pena. Isso nao era
    minha decisao. Implementadas as 3, com prioridade real por turno
    (so' 1 ativacao, regra de planeswalker):
    1. **-7** (se lealdade >= 7): emblema permanente "play lands and cast
       permanent spells from your graveyard" -- estritamente melhor que
       qualquer -2 pontual, sempre usada se disponivel.
    2. **+1**: "up to one target land you control becomes a 3/3 Elemental
       ... until your next turn. It's still a land." Sem P/T rastreado
       (docstring), a estatistica 3/3 em si nao e' um numero que este
       simulador manipula -- mas "ainda e' terreno E vira criatura" tem
       efeito real de verdade aqui: land-alvo fica elegivel como "target
       creature" (Bristly Bill/Ozolith) ate seu proximo turno (campo
       `temp_creature_until_turn`). Usada quando esse alvo de criatura
       faz falta (Bristly Bill ou Ozolith-com-contadores-guardados em
       campo, sem nenhuma criatura real disponivel) OU quando a lealdade
       ainda nao permite -2 (< 2) -- construir rumo ao -7 organicamente,
       sem planejamento de varios turnos a frente (mesmo horizonte
       guloso/imediato do resto do arquivo).
    3. **-2** (padrao, valor imediato garantido): mill 3, recupera
       permanente pra mao."""
    wrenn = next((p for p in state.battlefield if p.card.name == "Wrenn and Realmbreaker"), None)
    if wrenn is None:
        return

    if state.wrenn_loyalty >= 7:
        state.wrenn_emblem = True
        state.wrenn_ultimate_activations += 1
        log.append("  [Wrenn -7] emblema: joga terrenos e conjura permanentes do cemiterio")
        return

    needs_creature_target = (
        (any(p.card.name == "Bristly Bill, Spine Sower" for p in state.battlefield)
         or (state.ozolith_counters > 0 and any(p.card.name == "The Ozolith" for p in state.battlefield)))
        and best_creature_target(state) is None
    )
    if needs_creature_target or state.wrenn_loyalty < 2:
        state.wrenn_loyalty += 1
        state.wrenn_plus1_activations += 1
        candidates = [p for p in state.battlefield if is_land(p, state) and not is_creature_type(p, state)]
        if candidates:
            target = candidates[0]
            target.temp_creature_until_turn = state.turn + 1
            log.append(f"  [Wrenn +1] {target.card.name} vira 3/3 ate o proximo turno")
        else:
            log.append("  [Wrenn +1] sem alvo de terreno elegivel, so' ganha lealdade")
        return

    state.wrenn_loyalty -= 2
    state.wrenn_minus2_activations += 1
    milled = []
    for _ in range(3):
        if state.library:
            milled.append(state.library.pop(0))
    state.graveyard.extend(milled)
    permanent_ctypes = {"land", "artifact", "creature", "artifact_creature",
                         "enchantment", "enchantment_creature", "planeswalker"}
    candidates = [c for c in milled if CARD_DB[c].ctype in permanent_ctypes]
    if candidates:
        chosen = candidates[0]
        state.graveyard.remove(chosen)
        state.hand.append(chosen)
        log.append(f"  [Wrenn -2] mill 3, recupera {chosen} pra mao")
    else:
        log.append("  [Wrenn -2] mill 3, nenhum permanente entre os milhados")
    if state.wrenn_loyalty <= 0:
        leave_battlefield(state, wrenn, log)
        log.append("  [Wrenn and Realmbreaker] sacrificado (lealdade 0)")


def caretaker_talent_levelup(state: GameState, log: list):
    """Nivel 2 (copia token) e nivel 3 (anthem +2/+2) diagnosticados mas nao
    implementados na rodada anterior -- implementado 2026-08-31. Nivel 1
    (draw ao token entrar) ja estava correto (ver `create_token()`). Custo de
    level up real (Scryfall): {W} pro nivel 2, {3}{W} pro nivel 3 -- pago de
    forma gananciosa (mesmo padrao de Ba Sing Se/Bristly Bill) apos o loop
    generico de conjuracao. Nivel 2 copia um token -- so' dispara se existir
    um Permanent de token DE VERDADE em campo pra mirar: a maioria dos
    tokens deste simulador (Field of the Dead, Tireless Provisioner,
    Sapling Nursery etc) e' abstraida como so' um contador em
    `create_token()`, sem um objeto Permanent real (limitacao de arquitetura
    documentada, nao nova). Nivel 3 (anthem +2/+2 em tokens de criatura) nao
    tem numero pra modificar (sem P/T rastreado, docstring) -- so' o nivel em
    si e' concedido de verdade e reportado como metrica separada em
    `run_batch`, nunca fingido como dano/poder real."""
    ct = next((p for p in state.battlefield if p.card.name == "Caretaker's Talent"), None)
    if ct is None:
        return
    if ct.level == 1 and remaining_mana(state) >= 1:
        spend_mana(state, 1)
        ct.level = 2
        log.append("  [Caretaker's Talent] level up -> 2 ({W})")
        token_target = next((p for p in state.battlefield if p.is_token and p is not ct), None)
        if token_target is not None:
            clone = mk_perm(state, token_target.card.name)
            clone.is_token = True
            log.append(f"  [Caretaker's Talent II] copia token {token_target.card.name}")
            create_token(state, log, note="copia via Caretaker's Talent nivel 2")
            enter_battlefield(state, clone, log)
    if ct.level == 2 and remaining_mana(state) >= 4:
        spend_mana(state, 4)
        ct.level = 3
        log.append("  [Caretaker's Talent] level up -> 3 ({3}{W}, anthem +2/+2 em "
                    "tokens de criatura -- P/T nao rastreado, ver docstring)")


def oswald_fiddlebender_tinker(state: GameState, log: list):
    """Achado real 2026-09-01: Oswald Fiddlebender estava 100% sem
    implementacao (so' registrado no CARD_DB, tag `artifact_tutor_cheat`
    sem dispatch nenhum) -- nao era so' um item da lista de pendencias, foi
    achado agora na revisao completa do oraculo. "Magical Tinkering --
    {W}, {T}, Sacrifice an artifact: Search your library for an artifact
    card with mana value equal to 1 plus the sacrificed artifact's mana
    value, put it onto the battlefield, then shuffle. Activate only as a
    sorcery." Sacrifica o artefato mais descartavel disponivel (mesma
    prioridade SAC_VALUE ja usada pro Krark-Clan Ironworks) -- so' ativa se
    existir alvo LEGAL na biblioteca pro valor exato mv+1 (visibilidade
    total da biblioteca e' o mesmo padrao de decisao "onisciente" ja usado
    em toda IA deste simulador, ex: Kodama/best_earthbend_target)."""
    oswald = next((p for p in state.battlefield if p.card.name == "Oswald Fiddlebender" and not p.tapped), None)
    if oswald is None or remaining_mana(state) < 1:
        return
    candidates = [p for p in state.battlefield
                  if p.card.ctype in ARTIFACT_ISH and not p.is_token and p is not oswald]
    if not candidates:
        return
    if SAC_VALUE_PRIORITY_POLICY:
        candidates.sort(key=lambda p: SAC_VALUE.get(p.card.name, 1))
    for sac in candidates:
        target_mv = sac.card.mv + 1
        pool = [n for n in state.library if CARD_DB[n].ctype in ARTIFACT_ISH and CARD_DB[n].mv == target_mv]
        if not pool:
            continue  # sem alvo legal pra esse valor -- tenta o proximo candidato de sacrificio
        spend_mana(state, 1)
        oswald.tapped = True
        found = pool[0]
        state.library.remove(found)
        log.append(f"  [Oswald Fiddlebender] sacrifica {sac.card.name} (mv {sac.card.mv}), busca {found} (mv {target_mv})")
        leave_battlefield(state, sac, log)
        new_perm = mk_perm(state, found)
        enter_battlefield(state, new_perm, log)
        return


def fountainport_abilities(state: GameState, log: list):
    """Fountainport tem 3 habilidades ativadas, todas com {T} -- so' 1 pode
    ser usada por turno. Achado real 2026-09-01 (usuario, apos a 2a
    partida manual: "quero que vc compile TUDO... SEMPRE"): as 2 abaixo
    (Fish/Treasure) tinham ficado de fora por eu ter julgado "valor
    menor" -- decisao que nao era minha pra tomar. Implementadas as 3,
    priorizadas por valor real (draw > mana fixo/flexivel > corpo 1/1
    sem uso de combate neste sim):
    1. {2},{T},sac token real: draw a card (limitacao pre-existente: so'
       dispara contra um token que seja um `Permanent` de verdade em
       campo, nao os abstraidos como contador em `create_token()`).
    2. {4},{T}: cria Treasure (mana flexivel, sem custo de vida).
    3. {3},{T},pay 1 life: cria Fish 1/1 (ultima opcao -- so' conta como
       corpo/token, sem combate neste sim, e ainda custa vida)."""
    fp = next((p for p in state.battlefield if p.card.name == "Fountainport" and not p.tapped), None)
    if fp is None:
        return
    token = next((p for p in state.battlefield if p.is_token and p is not fp), None)
    if token is not None and remaining_mana(state) >= 2:
        spend_mana(state, 2)
        fp.tapped = True
        log.append(f"  [Fountainport] sacrifica token {token.card.name}, compra 1 carta")
        leave_battlefield(state, token, log)
        draw_cards(state, 1, log, source="Fountainport (sacrifica token)")
        return
    if remaining_mana(state) >= 4:
        spend_mana(state, 4)
        fp.tapped = True
        state.treasures += 1
        log.append("  [Fountainport] {4},{T}: cria Treasure")
        return
    if remaining_mana(state) >= 3 and state.life_total > 10:
        spend_mana(state, 3)
        fp.tapped = True
        state.life_total -= 1
        log.append("  [Fountainport] {3},{T},paga 1 vida: cria Fish 1/1")
        create_token(state, log)


def inventors_fair_tutor(state: GameState, log: list):
    """Achado real 2026-09-01 (checklist clausula-a-clausula, pos-Partida
    #2): "{4}, {T}, Sacrifice Inventors' Fair: Search your library for an
    artifact card, reveal it, put it into your hand, then shuffle. Activate
    only if you control three or more artifacts." So' a metade upkeep
    (lifegain com 3+ artefatos) estava implementada -- essa 3a habilidade
    nunca tinha dispatch nenhum, nem estava documentada como fora de
    escopo. Sacrifica o proprio terreno (perda real de fonte de mana) --
    so' vale a pena achando algo bom, reusa a mesma prioridade do
    Enlightened Tutor."""
    fair = next((p for p in state.battlefield if p.card.name == "Inventors' Fair" and not p.tapped), None)
    if fair is None or remaining_mana(state) < 4:
        return
    n_artifacts = sum(1 for p in state.battlefield if is_artifact(p, state))
    if n_artifacts < 3:
        return
    pool = [n for n in state.library if CARD_DB[n].ctype in ARTIFACT_ISH]
    if not pool:
        return
    found = next((n for n in ARTIFACT_TUTOR_PRIORITY if n in pool), None)
    if found is None:
        pool.sort(key=lambda n: -CARD_DB[n].mv)
        found = pool[0]
    spend_mana(state, 4)
    fair.tapped = True
    state.library.remove(found)
    state.hand.append(found)
    log.append(f"  [Inventors' Fair] sacrifica, busca {found} pra mao")
    leave_battlefield(state, fair, log)


def iron_spider_abilities(state: GameState, log: list):
    """Iron Spider, Stark Upgrade: 2 habilidades ativadas, nenhuma
    opponent-dependent -- estavam marcadas "fora de escopo" desde
    2026-08-28 sem motivo real (nao dependem de P/T pra combate, contador
    e' rastreado de verdade neste sim). Achado real 2026-09-01 (usuario:
    "quero que vc compile TUDO... SEMPRE") -- implementadas as 2:
    1. {T}: +1/+1 em cada artefato-criatura que voce controla (nao ha
       Vehicle nesta lista). Conta pra Ozolith/Earth Kingdom General
       depois.
    2. {2}, remove 2 contadores dentre artefatos que voce controla: draw
       (nao precisa ser do proprio Iron Spider -- "among artifacts you
       control", qualquer combinacao)."""
    spider = next((p for p in state.battlefield if p.card.name == "Iron Spider, Stark Upgrade" and not p.tapped), None)
    if spider is not None:
        spider.tapped = True
        targets = [p for p in state.battlefield if is_artifact(p, state) and is_creature_type(p, state)]
        if targets:
            for p in targets:
                p.counters += 1
            log.append(f"  [Iron Spider] {{T}}: +1/+1 em {len(targets)} artefato-criatura(s)")

    if remaining_mana(state) >= 2:
        with_counters = [p for p in state.battlefield if is_artifact(p, state) and p.counters > 0]
        if sum(p.counters for p in with_counters) >= 2:
            spend_mana(state, 2)
            to_remove = 2
            for p in sorted(with_counters, key=lambda x: -x.counters):
                take = min(p.counters, to_remove)
                p.counters -= take
                to_remove -= take
                if to_remove <= 0:
                    break
            draw_cards(state, 1, log, source="Iron Spider (remove 2 contadores)")
            log.append("  [Iron Spider] remove 2 contadores dentre artefatos, compra 1 carta")


def conduit_of_worlds_reanimate(state: GameState, log: list):
    """Conduit of Worlds: "{T}: Choose target nonland permanent card in
    your graveyard. If you haven't cast a spell this turn, you may cast
    that card. If you do, you can't cast additional spells this turn.
    Activate only as a sorcery." Achado real 2026-09-01 (usuario: "compile
    TUDO, SEMPRE") -- tinha ficado de fora porque eu julguei que essa
    troca (abrir mao do loop ganancioso do turno inteiro por 1 reanimacao)
    precisaria de dados A/B, no padrao do `BRISTLY_BILL_RESERVE_POLICY`.
    Isso nao era motivo pra nunca implementar -- so' motivo pra escolher
    uma politica e medir. Politica adotada: so' vale abrir mao do turno se
    o alvo for um reconhecido de alto valor (`ARTIFACT_TUTOR_PRIORITY`) OU
    se a mao nao tem NADA castavel esse turno de qualquer forma (sem custo
    de oportunidade real). Chamada ANTES do loop guloso principal --
    trava `state.conduit_lockout`, que o loop guloso e o emblema do Wrenn
    -7 respeitam."""
    conduit = next((p for p in state.battlefield if p.card.name == "Conduit of Worlds" and not p.tapped), None)
    if conduit is None or state.spells_cast_this_turn > 0:
        return
    pool = [n for n in state.graveyard if CARD_DB[n].ctype != "land"]
    if not pool:
        return
    bomb = next((n for n in ARTIFACT_TUTOR_PRIORITY if n in pool and can_cast(state, n)), None)
    hand_has_castables = any(CARD_DB[n].ctype != "land" and can_cast(state, n) for n in state.hand)
    if bomb is None and hand_has_castables:
        return  # mao ja tem opcoes -- nao vale travar o turno por algo generico
    target = bomb
    if target is None:
        affordable = [n for n in pool if can_cast(state, n)]
        if not affordable:
            return
        target = max(affordable, key=lambda n: CARD_DB[n].mv)
    conduit.tapped = True
    state.graveyard.remove(target)
    state.conduit_reanimations += 1
    log.append(f"  [Conduit of Worlds] reanima {target} do cemiterio (trava o resto do turno)")
    cast_card(state, target, log, from_hand=False)
    state.conduit_lockout = True


def liquimetal_activation(state: GameState, log: list):
    """Liquimetal Coating/Torque: "{T}: Target permanent becomes an
    artifact ... until end of turn." Achado real 2026-09-01 (usuario:
    "compile TUDO") -- eu tinha decidido nao implementar (e a 1a versao
    desta funcao usava um gatilho de "falta alvo de criatura" que se
    provou auto-contraditorio: `best_creature_target()` ja acha QUALQUER
    criatura real, land ou nao -- entao "falta alvo" so' acontece quando
    NAO ha criatura nenhuma, momento em que tambem nao ha criatura nenhuma
    pra converter). O valor real e' outro: junto com a estatica da Toph
    ("nontoken artifacts you control are lands"), converter um permanente
    NAO-terreno em artefato faz ele virar TAMBEM terreno -- isso amplia o
    pool de `best_earthbend_target()` (que so' considera terrenos) pra
    incluir uma criatura real de verdade, e soma no total de terrenos
    (relevante pros gatilhos de "N terrenos" do Field of the Dead/Scute
    Swarm/battle lands) e na contagem de artefatos (Metalcraft do Mox
    Opal, "3+ artefatos" do Inventors' Fair). Ativada sempre que houver
    um alvo real disponivel (nao-terreno, ainda nao-artefato) -- prefere
    criatura real (amplia earthbend) sobre qualquer outro permanente."""
    if not state.commander_in_play:
        return
    for card_name in ("Liquimetal Coating", "Liquimetal Torque"):
        source = next((p for p in state.battlefield if p.card.name == card_name and not p.tapped), None)
        if source is None:
            continue
        candidates = [p for p in state.battlefield
                      if not is_land(p, state) and not is_artifact(p, state) and not p.is_token]
        if not candidates:
            continue
        candidates.sort(key=lambda p: 0 if is_creature_type(p, state) else 1)
        target = candidates[0]
        target.temp_artifact_until_turn = state.turn
        source.tapped = True
        log.append(f"  [{card_name}] {target.card.name} vira artefato-terreno ate o fim do turno")
        return


def bala_ged_recovery_spell_mode(state: GameState, log: list):
    """Bala Ged Recovery // Bala Ged Sanctuary: face sorcery ("Return
    target card from your graveyard to your hand", {2}{G}). Ja documentado
    como limitacao de arquitetura no `CARD_DB` (a carta e' registrada so'
    como land, `ctype` unico por carta) -- mas achado real 2026-09-01
    (usuario: "compile TUDO") mostrou que "limitacao de arquitetura" nao
    e' desculpa pra nunca tentar: da' pra despachar por nome, igual
    Conduit/Oswald/Inventors' Fair, sem precisar mudar `ctype`. So' faz
    sentido quando o land-drop do turno ja foi usado (senao joga como
    terreno, que o deck quer mais -- "ja abaixo do piso de terrenos")."""
    # nota: CARD_DB[name].mv == 0 (registrada como land) -- custo real da
    # face sorcery e' {2}{G} = 3 generico neste modelo, checado direto aqui.
    name = "Bala Ged Recovery // Bala Ged Sanctuary"
    if name not in state.hand or state.conduit_lockout or remaining_mana(state) < 3:
        return
    max_drops = 1 + state.extra_land_drops + (1 if has_card(state, "Dryad of the Ilysian Grove") else 0)
    if state.lands_played_this_turn < max_drops:
        return  # ainda da pra jogar como terreno esse turno -- prioridade real do deck
    if not state.graveyard:
        return
    target = next((n for n in ARTIFACT_TUTOR_PRIORITY if n in state.graveyard), None)
    if target is None:
        lands_in_gy = [n for n in state.graveyard if is_land_name(n)]
        target = lands_in_gy[0] if lands_in_gy else state.graveyard[0]
    spend_mana(state, 3)
    state.spells_cast_this_turn += 1
    state.hand.remove(name)
    state.graveyard.remove(target)
    state.hand.append(target)
    log.append(f"  [Bala Ged Recovery] conjurada como sorcery (terreno ja jogado), devolve {target} pra mao")


def zuran_orb_activation(state: GameState, log: list):
    """Achado real 2026-09-01 (usuario: "nao quero que vc decida se a
    habilidade vai ativar ou nao... compile TUDO"). "Sacrifice a land: You
    gain 2 life" nunca era ativado -- eu tinha julgado que trocar um
    terreno de verdade por 2 de vida e' sempre ruim pra esse deck sem
    oponente, e decidi por conta propria nunca modelar. Implementada com
    um gatilho real (emergencia de vida baixa, o unico cenario onde
    perder um terreno permanente por vida faz sentido pra QUALQUER piloto
    -- vida abaixo de 10 aqui vem so' dos custos de vida ja modelados:
    fetches, shock lands, Sylvan Library, Tanglespan Bridgeworks) -- nao
    "nunca ativa" mais, ativa quando a condicao real pede."""
    orb = next((p for p in state.battlefield if p.card.name == "Zuran Orb"), None)
    if orb is None or state.life_total >= 10:
        return
    real_lands = [p for p in state.battlefield if p.card.ctype == "land"]
    if not real_lands:
        return
    sac = real_lands[0]
    log.append(f"  [Zuran Orb] sacrifica {sac.card.name} (vida baixa: {state.life_total}), ganha 2")
    leave_battlefield(state, sac, log)
    gain_life(state, 2, log, source="Zuran Orb")


def combat_step(state: GameState, log: list):
    # Achado real 2026-09-01 (2a passada da revisao de oraculo): The
    # Ozolith so' tinha a METADE "reciclagem" implementada (contadores de
    # criatura que morre vao pro Ozolith, em `leave_battlefield()`) -- a
    # OUTRA metade, "At the beginning of combat on your turn, if The
    # Ozolith has counters on it, you may move all counters from The
    # Ozolith onto target creature", nunca tinha dispatch nenhum:
    # `state.ozolith_counters` so' era incrementado, nunca lido/gasto.
    # "target creature" (nao terreno) -- usa `best_creature_target`, mesmo
    # fix de legalidade de alvo do Bristly Bill/Earthbender Ascension.
    if state.ozolith_counters > 0 and any(p.card.name == "The Ozolith" for p in state.battlefield):
        target = best_creature_target(state)
        if target is not None:
            target.counters += state.ozolith_counters
            state.ozolith_moves += 1
            log.append(f"  [The Ozolith] move {state.ozolith_counters} contadores pra {target.card.name}")
            state.ozolith_counters = 0

    # Achado real 2026-09-01: Avatar Kyoshi ("At the beginning of combat on
    # your turn, earthbend 8, then untap that land") e' um gatilho de INICIO
    # DE COMBATE -- dispara todo turno com Kyoshi em campo, mesmo sem NENHUM
    # atacante elegivel (inclusive se a propria Kyoshi acabou de entrar e
    # ainda tem doenca de invocacao). O codigo antigo dependia de
    # `attackers` nao-vazio ANTES de checar Kyoshi, o que a fazia nunca
    # disparar num turno em que ela mesma fosse a unica criatura em campo e
    # tivesse acabado de ser conjurada. Corrigido: checado antes/fora do
    # gate de `attackers`. Tambem faltava o "then untap that land" -- se o
    # terreno-alvo ja estava tapped (usado por mana), agora ele destapa de
    # volta (mana extra real).
    if any(p.card.name == "Avatar Kyoshi, Earthbender" for p in state.battlefield):
        target = apply_earthbend(state, 8, log, "Avatar Kyoshi (inicio de combate)")
        if target is not None and target.tapped:
            target.tapped = False
            log.append(f"  [Avatar Kyoshi] destapa {target.card.name} de volta")

    attackers = [p for p in state.battlefield if is_creature_type(p, state) and p.entered_turn < state.turn]

    # Toph, Earthbending Master ("Whenever YOU attack, earthbend X") e
    # Horizon Explorer ("Whenever you attack a player, create a Lander
    # token") sao gatilhos de "voce ataca" (com QUALQUER criatura), nao
    # "sempre que ESTA criatura ataca". Achado real 2026-09-01: o codigo
    # antigo exigia a propria Toph EM/Horizon Explorer estarem na lista de
    # atacantes elegiveis (ou seja, sem doenca de invocacao) pra disparar,
    # o que sub-contava o gatilho quando elas estavam sick mas outra
    # criatura atacava mesmo assim. Corrigido: so' precisa a carta estar em
    # campo E o jogador ter atacado com ALGO (attackers nao-vazio).
    if attackers and any(p.card.name == "Toph, Earthbending Master" for p in state.battlefield):
        apply_earthbend(state, state.experience_counters, log, "Toph Earthbending Master (ataque, X=experiencia)")
    if attackers and any(p.card.name == "Horizon Explorer" for p in state.battlefield):
        create_token(state, log)  # Lander token

    # Bumi ("Whenever BUMI attacks") e' um gatilho de auto-ataque de
    # verdade -- corretamente exige Bumi elegivel pra atacar (sem doenca de
    # invocacao), diferente dos 2 acima.
    if any(p.card.name == "Bumi, Eclectic Earthbender" for p in attackers):
        for p in state.battlefield:
            if is_land(p, state) and is_creature_type(p, state):
                p.counters += 2

    # Achado real 2026-09-01 (checklist clausula-a-clausula, pos-Partida #2):
    # Overlord of the Hauntwoods ("Whenever this permanent enters OR
    # ATTACKS, create a tapped Everywhere land token") -- so' a metade ETB
    # estava implementada (`apply_etb`), a metade "ou ataca" nunca disparava
    # nenhuma vez, mesmo Overlord virando um motor de terreno repetivel de
    # verdade uma vez em campo. Auto-ataque de verdade (igual Bumi), nao
    # "whenever you attack" do jogador.
    if any(p.card.name == "Overlord of the Hauntwoods" for p in attackers):
        create_token(state, log)
        everywhere = mk_perm(state, "Everywhere Token")
        everywhere.is_token = True
        everywhere.tapped = True
        enter_battlefield(state, everywhere, log)


def end_step(state: GameState, log: list):
    if state.commander_in_play:
        apply_earthbend(state, 2, log, "Toph, the First Metalbender (end step)")


def play_turn(state: GameState, log: list, is_first_turn: bool, on_play: bool):
    state.turn += 1
    state.lands_played_this_turn = 0
    state.mana_spent_this_turn = 0
    state.landfalls_this_turn = 0
    for p in state.battlefield:
        p.tapped = False

    state.token_drawn_this_turn = False
    state.counter_lifegain_this_turn = False
    state.spells_cast_this_turn = 0
    state.conduit_lockout = False

    # Upkeep: Inventors' Fair (lifegain se 3+ artefatos)
    n_artifacts = sum(1 for p in state.battlefield if is_artifact(p, state))
    if n_artifacts >= 3 and any(p.card.name == "Inventors' Fair" for p in state.battlefield):
        gain_life(state, 1, log, source="Inventors' Fair (upkeep)")

    if not (is_first_turn and on_play):
        if state.library:
            state.hand.append(state.library.pop(0))
        if state.scheduled_draws > 0 and state.library:
            state.hand.append(state.library.pop(0))
            state.scheduled_draws -= 1
        # Sylvan Library: compra 2 extra, decide manter (pagando 4 de vida cada)
        # ou devolver ao topo com base numa margem de seguranca de vida.
        if any(p.card.name == "Sylvan Library" for p in state.battlefield) and len(state.library) >= 2:
            extra = [state.library.pop(0), state.library.pop(0)]
            state.hand.extend(extra)
            state.cards_drawn_extra += 2
            keep = state.life_total > 20
            if keep:
                state.life_total -= 8
                log.append("  [Sylvan Library] mantem as 2 cartas extra, paga 8 de vida")
            else:
                for c in extra:
                    state.hand.remove(c)
                    state.library.insert(0, c)
                state.cards_drawn_extra -= 2
                log.append("  [Sylvan Library] devolve as 2 cartas extra (vida baixa demais)")

    urza_saga_advance(state, log)
    play_land(state, log)
    main_phase(state, log)
    combat_step(state, log)
    end_step(state, log)


# ---------------------------------------------------------------------------
# Full game simulation
# ---------------------------------------------------------------------------

def simulate_one(seed: int, turns: int = 8):
    rng = random.Random(seed)
    hand, lib, mulls = mulligan(rng)
    state = GameState(hand=hand, library=lib, mulligans=mulls)
    log = [f"=== seed {seed} ==="]

    for t in range(turns):
        play_turn(state, log, is_first_turn=(t == 0), on_play=True)

    return state, log


def run_batch(n: int, seed_base: int, turns: int = 8):
    states = []
    for i in range(n):
        state, _ = simulate_one(seed_base + i, turns=turns)
        states.append(state)

    def avg(vals):
        return sum(vals) / len(vals) if vals else 0.0

    mulls = avg([s.mulligans for s in states])
    cmd_turn = [s.commander_cast_turn for s in states if s.commander_cast_turn is not None]
    cmd_never = 100 * sum(1 for s in states if s.commander_cast_turn is None) / n

    earthbend_apps = avg([s.earthbend_applications for s in states])
    motor16 = avg([s.motor16_recursions for s in states])
    motor16_any = 100 * sum(1 for s in states if s.motor16_recursions > 0) / n
    landfalls = avg([s.landfall_triggers_fired for s in states])
    fotd_tokens = avg([s.field_of_the_dead_tokens for s in states])
    fotd_any = 100 * sum(1 for s in states if s.field_of_the_dead_tokens > 0) / n
    extra_draw = avg([s.cards_drawn_extra for s in states])
    extra_mana = avg([s.mana_generated_extra for s in states])
    kodama = avg([s.kodama_cheats for s in states])
    resonator = avg([s.resonator_copies for s in states])
    bristly = avg([s.bristly_bill_doubles for s in states])
    ozolith = avg([s.ozolith_moves for s in states])
    tokens = avg([s.tokens_created for s in states])
    lands_final = avg([sum(1 for p in s.battlefield if is_land(p, s)) for s in states])
    ashaya_rate = 100 * sum(1 for s in states if s.ashaya_in_play) / n
    life_gained = avg([s.life_gained for s in states])
    scute_cap = sum(s.scute_swarm_cap_hits for s in states)
    obelisk_act = avg([s.obelisk_activations for s in states])
    coffin_act = avg([s.coffin_activations for s in states])
    kci_sac = avg([s.kci_sacrifices_of_recurring for s in states])
    talon_gates_protect = avg([s.talon_gates_protections for s in states])

    # --- Metricas obrigatorias #10 (goldfish-sim-card-rules.md secao 10) ---
    # ramp e draw ja existiam (extra_mana/extra_draw acima); interaction,
    # recursion e finisher/lethality sao novas (achado real 2026-08-31,
    # implementadas nesta rodada — antes so' citadas como "N/A" sem linha
    # propria auditavel no relatorio).
    interaction = avg([s.interaction_plays for s in states])
    interaction_any = 100 * sum(1 for s in states if s.interaction_plays > 0) / n
    crucible_replays = avg([s.crucible_land_replays for s in states])
    recursion = avg([s.motor16_recursions + s.crucible_land_replays for s in states])
    finisher_turns = [s.first_finisher_turn for s in states if s.first_finisher_turn is not None]
    finisher_rate = 100 * len(finisher_turns) / n

    wrenn_minus2 = avg([s.wrenn_minus2_activations for s in states])
    wrenn_any = 100 * sum(1 for s in states if s.wrenn_minus2_activations > 0) / n
    caretaker_lv2 = 100 * sum(1 for s in states
                                if any(p.card.name == "Caretaker's Talent" and p.level >= 2 for p in s.battlefield)) / n
    caretaker_lv3 = 100 * sum(1 for s in states
                                if any(p.card.name == "Caretaker's Talent" and p.level >= 3 for p in s.battlefield)) / n
    saga_ch2 = avg([s.urza_saga_chapter2_tokens for s in states])
    saga_ch3 = avg([s.urza_saga_chapter3_tutors for s in states])

    wrenn_plus1 = avg([s.wrenn_plus1_activations for s in states])
    wrenn_ultimate_rate = 100 * sum(1 for s in states if s.wrenn_ultimate_activations > 0) / n
    conduit_reanim = avg([s.conduit_reanimations for s in states])
    legend_sac = avg([s.legend_rule_sacrifices for s in states])

    print(f"n={n}, seed_base={seed_base}, turns={turns}, RECURRING_ARTIFACT_POLICY={RECURRING_ARTIFACT_POLICY}")
    print(f"Avg mulligans: {mulls:.2f}")
    print(f"Turno medio de conjuracao da Toph: {avg(cmd_turn):.2f} | mediana: {statistics.median(cmd_turn) if cmd_turn else float('nan'):.1f}")
    print(f"Nunca conjurada em {turns} turnos: {cmd_never:.1f}%")
    print(f"Avg terrenos em campo (turno {turns}, contando artefato/criatura-terreno): {lands_final:.2f}")
    print(f"Avg aplicacoes de earthbend: {earthbend_apps:.2f}")
    print(f"Avg recorrencias via Motor#16: {motor16:.2f} | % de jogos com pelo menos 1: {motor16_any:.1f}%")
    print(f"Avg gatilhos de landfall disparados: {landfalls:.2f}")
    print(f"Avg tokens de Field of the Dead: {fotd_tokens:.2f} | % de jogos que ligou: {fotd_any:.1f}%")
    print(f"Avg cartas compradas extra (motores de draw): {extra_draw:.2f}")
    print(f"Avg mana extra gerado (Lotus Cobra/Nissa por landfall): {extra_mana:.2f}")
    print(f"Avg cheats do Kodama of the East Tree: {kodama:.2f}")
    print(f"Avg copias via Strionic Resonator: {resonator:.2f}")
    print(f"Avg dobras via Bristly Bill (ativada): {bristly:.2f}")
    print(f"Avg realocacoes de contador via The Ozolith: {ozolith:.2f}")
    print(f"Avg tokens totais criados: {tokens:.2f}")
    print(f"% de jogos com Ashaya em campo: {ashaya_rate:.1f}%")
    print(f"Avg vida ganha (Inventors' Fair/Haywire Mite/Sylvan Library liquido): {life_gained:.2f}")
    print(f"Total de vezes que o cap defensivo da Scute Swarm foi atingido (200+ permanentes): {scute_cap}")
    print(f"Avg ativacoes do Unstable Obelisk (earthbendado): {obelisk_act:.3f}")
    print(f"Avg ativacoes do The Stasis Coffin (earthbendado): {coffin_act:.3f}")
    print(f"Avg protecoes via Talon Gates of Madara (fase fora criatura propria no ETB): {talon_gates_protect:.3f}")
    print(f"Avg sacrificios via Krark-Clan Ironworks de artefato earthbendado: {kci_sac:.3f}")

    print("\n--- 5 metricas obrigatorias (goldfish-sim-card-rules.md secao 10) ---")
    print(f"[1) Ramp] Avg mana extra gerado por rampa (Lotus Cobra/Nissa landfall + KCI sac): {extra_mana:.2f}")
    print(f"[2) Draw] Avg cartas compradas alem da compra normal do turno: {extra_draw:.2f}")
    print(f"[3) Interaction] Avg spells/permanentes de interacao conjurados (Swords to Plowshares/"
          f"Council's Judgment/Erode/Haywire Mite/Heroic Intervention/Lightning Greaves/Teferi's Protection/"
          f"Oblivion Stone/Skullclamp/Krang/Sword of Feast and Famine (combat_dependent, achado real "
          f"2026-09-01) — efeito numerico solo N/A por falta de oponente/combate real, ver docstring): "
          f"{interaction:.2f} | % de jogos com pelo menos 1: {interaction_any:.1f}%")
    print(f"[4) Recursion] Avg recorrencia de permanente (Motor#16 earthbend_return + terreno do "
          f"cemiterio via Crucible/Conduit of Worlds): {recursion:.2f} "
          f"(Motor#16 {motor16:.2f} + Crucible/Conduit {crucible_replays:.2f})")
    print(f"[5) Finisher/lethality] Proxy: % de jogos que resolvem >=1 ameaca de vitoria "
          f"(Avatar Kyoshi/Toph Earthbending Master/Krang/Great Henge/Scute Swarm/Sapling Nursery/"
          f"Felidar Retreat/Mossborn Hydra) em {turns} turnos: {finisher_rate:.1f}% | "
          f"turno medio de resolucao: {avg(finisher_turns):.2f} "
          f"(turno de RESOLUCAO da carta, nao de dano letal real — sem combate modelado, ver docstring)")

    print("\n--- Mecanicas implementadas nesta rodada (2026-08-31) ---")
    print(f"Avg terrenos replayados do cemiterio via Crucible/Conduit of Worlds: {crucible_replays:.2f}")
    print(f"Avg ativacoes de Wrenn and Realmbreaker -2 (mill 3 + recupera permanente): {wrenn_minus2:.2f} "
          f"| % de jogos com pelo menos 1: {wrenn_any:.1f}%")
    print(f"% de jogos que Caretaker's Talent atinge nivel 2 (copia token): {caretaker_lv2:.1f}%")
    print(f"% de jogos que Caretaker's Talent atinge nivel 3 (anthem +2/+2, P/T nao rastreado): {caretaker_lv3:.1f}%")
    print(f"Avg tokens Construct via Urza's Saga capitulo II: {saga_ch2:.3f}")
    print(f"Avg tutores de artefato custo 0/1 via Urza's Saga capitulo III: {saga_ch3:.3f}")

    print("\n--- Mecanicas implementadas 2026-09-01 (usuario: \"compile TUDO, SEMPRE\") ---")
    print(f"Avg ativacoes de Wrenn and Realmbreaker +1 (terreno vira criatura ate o proximo turno): {wrenn_plus1:.2f}")
    print(f"% de jogos que alcancam o -7 (emblema: joga terreno/conjura permanente do cemiterio): {wrenn_ultimate_rate:.1f}%")
    print(f"Avg reanimacoes via Conduit of Worlds ({{T}}, trava o turno): {conduit_reanim:.3f}")
    print(f"Avg sacrificios via regra do lendario (backstop -- Ultron ja recusa copiar lendario antes disso): {legend_sac:.4f}")

    # breakdown de fontes de earthbend
    combined = {}
    for s in states:
        for k, v in s.earthbend_by_source.items():
            combined[k] = combined.get(k, 0) + v
    print("\nEarthbend por fonte (soma de todas as partidas, ordenado):")
    for k, v in sorted(combined.items(), key=lambda kv: -kv[1]):
        print(f"  {k}: {v} ({v/n:.2f}/jogo)")

    return states


if __name__ == "__main__":
    import sys
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    states = run_batch(n=3000, seed_base=9000000, turns=8)

    with open("toph_v1_runs.jsonl", "w") as f:
        for s in states:
            f.write(json.dumps({
                "mulligans": s.mulligans,
                "commander_cast_turn": s.commander_cast_turn,
                "earthbend_applications": s.earthbend_applications,
                "motor16_recursions": s.motor16_recursions,
                "landfall_triggers_fired": s.landfall_triggers_fired,
                "field_of_the_dead_tokens": s.field_of_the_dead_tokens,
                "cards_drawn_extra": s.cards_drawn_extra,
                "tokens_created": s.tokens_created,
                "ashaya_in_play": s.ashaya_in_play,
                "life_gained": s.life_gained,
                "scute_swarm_cap_hits": s.scute_swarm_cap_hits,
                "talon_gates_protections": s.talon_gates_protections,
            }) + "\n")
