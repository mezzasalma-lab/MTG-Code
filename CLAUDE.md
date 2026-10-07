# MTG-Code — regras permanentes deste repositório

## Regra #1 (obrigatória, sem exceção): TODA habilidade de TODA carta tem que estar implementada

A partir de 2026-09-14, por pedido explícito do usuário ("SEMPRE USE TODAS
AS HABILIDADES DE TODAS AS CARTAS DE HOJE EM DIANTE"), esta é a regra
permanente pra qualquer trabalho neste repositório — simulador novo,
correção pontual, ou adição/troca de carta numa lista existente:

**Toda carta (comandante + decklist) tem TODAS as suas habilidades reais
modeladas no simulador correspondente — nunca só a habilidade "principal"
ou a mais óbvia, nunca só metade de uma carta com 2+ cláusulas.** Isso
inclui: estáticos, ETB, morte/leaves-the-battlefield, ativadas (mesmo as
"secundárias" ou de baixo custo), Sagas (todos os capítulos), custos
alternativos reais (Flashback/Escape/Adventure/Evoke/Warp/Plot/Kicker),
gatilhos "whenever" (mesmo os que parecem redundantes com outra carta), e
qualquer cláusula extra além da primeira frase do oráculo.

### Como fazer isso de verdade (método já validado em 17 decks nesta sessão)

1. **Nunca confiar em memória de oráculo.** Buscar o texto real ao vivo via
   Scryfall (`POST /cards/collection` em lote pra maioria; `/cards/named?
   fuzzy=` individual pra MDFC/split/adventure que o batch erra) antes de
   julgar qualquer carta como "correta" ou "já implementada". Cartas levam
   errata (ex.: Skullclamp em 2023) — o texto que você lembra pode estar
   desatualizado.
2. **Ler o arquivo `.py` inteiro, não só a função relacionada à carta.**
   A maioria dos gaps reais encontrados nesta sessão eram implementação
   PARCIAL: a carta tinha código, mas só pra uma das suas 2+ cláusulas —
   invisível se você só grepar o nome da carta e olhar 1 ocorrência.
3. **Comparar clausula-por-cláusula**, cada frase/parágrafo do oráculo
   contra o código, marcando ✅ implementado, 🐛 corrigido nesta rodada, ou
   📊 estrutural (ver critério abaixo).
4. **Rodar uma varredura automatizada de "tags/nomes órfãos"** (definidos
   em `add()`/`CARD_DB`, nunca referenciados em nenhum dispatch fora
   dali) como primeira triagem — pega tags fantasma, mas NÃO pega
   implementação parcial (uma tag pode estar corretamente referenciada e
   ainda cobrir só parte da carta). As duas técnicas são complementares,
   nunca use só uma.

### Bugs recorrentes pra procurar especificamente (taxonomia confirmada nesta sessão)

- Habilidade ativada com `{T}` que nunca é bloqueada por doença de
  invocação, ou que compartilha o mesmo `{T}` de outra habilidade da MESMA
  fonte sem cobrar as duas.
- Custo de ativação (mana ou vida) nunca de fato deduzido — "mana
  fantasma".
- Efeito estático (anthem, CDA tipo "power = terrenos que controlo",
  contador acumulado) lido em UMA função mas não propagado pra TODAS as
  outras que leem poder/custo/mana daquele mesmo permanente.
- Gatilho compartilhado (morte de criatura, sacrifício, "sempre que você
  compra") ligado só em ALGUNS dos pontos reais do arquivo onde esse
  evento acontece, não em TODOS.
- Carta registrada no `CARD_DB`/dispatch sob um nome, checada em outro
  lugar com nome diferente/abreviado (nunca bate).
- Busca/fetch aplicado sem a restrição de tipo real do oráculo (ex.:
  Farseek só busca terreno básico + Plains/Island/Swamp/Mountain type,
  não "qualquer terreno").
- Custo alternativo real (Evoke, Flashback, Warp, Escape, Plot, Adventure)
  simplesmente inexistente no código — carta só é conjurada pelo custo
  cheio.
- Saga com só o capítulo I implementado, capítulos seguintes nunca
  avançam.
- Fórmula dinâmica real (escala com board state) achatada pra um número
  fixo aproximado quando o arquivo já rastreia os dados pra calcular o
  valor exato.

### Único critério válido pra NÃO implementar algo: impossibilidade estrutural, nunca julgamento de valor

- 📊 **N/A estrutural aceitável:** a habilidade depende de estado de
  OPONENTE real que este simulador goldfish-solo não modela (remoção
  visando permanente do oponente, "target opponent", vida real de
  oponente, bloqueio). Mesmo assim, sempre que possível, contar a
  carta/ativação como métrica proxy (ex.: "spells de interação
  conjurados") em vez de simplesmente ignorá-la.
- ❌ **NUNCA aceitável:** decidir não implementar por achar o efeito "de
  baixo valor esperado", "raro demais pra importar", ou qualquer variação
  de julgamento de valor subjetivo. Se a carta tem a habilidade e ela é
  fisicamente modelável neste motor (mesmo que rara), ela entra.
- Sempre documentar cada decisão de 📊 com a cláusula real do oráculo
  citada — nunca com a própria opinião de que "não vale a pena".

### Constrangimentos que continuam valendo

- Nunca adicionar/cortar carta de nenhuma decklist — correção é sempre
  só de implementação.
- Nunca fabricar estado de tabuleiro do oponente pra fazer uma habilidade
  "funcionar" — usar sempre a convenção de métrica proxy já estabelecida
  (contagem de uso, não efeito de board simulado).
- Toda correção precisa de validação real antes de comitar: smoke test
  (contagem de cartas, 0 desconhecidas/duplicadas), 2.000 partidas antes/
  depois (mesma seed) mostrando a métrica nova se mover na direção
  esperada, 20.000 partidas de regressão com 0 exceções, e teste unitário
  dirigido confirmando que cada correção específica dispara de verdade.
- Documentar toda rodada em `checklist-oraculo.md` (achados + correções +
  validação) e `goldfish-log.md` (números antes/depois) do deck
  correspondente.

Esta regra vale pra QUALQUER trabalho futuro neste repositório, incluindo
decks totalmente novos, não só correções em decks existentes.

## Regra #2 (obrigatória): nunca marcar uma carta como ausente/desconhecida sem checar `flavor_name` no Scryfall

Achado real em 2026-09-14 (deck Beorn/Thranduil): vários decks deste
repositório usam cartas impressas em produtos "Universes Beyond" (Secret
Lair Drop de Avatar/Final Fantasy, Marvel Universe, Tales of Middle-earth)
com nome de capa diferente do nome real da carta — ex.: "Huu's Reach" é a
impressão Avatar de **Kodama's Reach**; "Aerith's Curaga Magic" é a
impressão Final Fantasy de **Heroic Intervention**; "Doom Variant" é a
impressão Marvel de **Roaming Throne**; "The Party Tree"/"Fangorn Forest"
são impressões Tales of Middle-earth de **The Great Henge**/**Yavimaya,
Cradle of Growth**. Nomes assim NÃO batem com o `oracle_id` real por texto
literal, e se o usuário mandar uma lista com esses nomes, uma comparação
ingênua de string vai apontar a carta como "removida"/"desconhecida"
quando ela pode estar lá o tempo todo sob o nome real.

**Antes de marcar qualquer carta como ausente, trocada ou desconhecida ao
comparar listas ou validar o `CARD_DB`:** buscar o nome exato no Scryfall
via `/cards/search?q="Nome Exato"` — se vier um resultado com `flavor_name`
igual ao nome buscado, o campo `name` da resposta é a carta real; resolver
pra esse nome antes de qualquer julgamento. Só depois dessa checagem
concluir que uma carta genuinamente saiu da lista.

## Regra #3 (obrigatória): habilidade "implementada" não basta — os CONCEITOS COMPARTILHADOS que ela usa (o que é "Urso", "criatura", "controla X") também têm que estar certos pra TODA carta que os lê

Achado real em 2026-09-14 (deck Beorn, reportado pelo usuário na própria
mesa): a habilidade do comandante ("if you control three or more Bears,
draw two cards") JÁ tinha código, JÁ disparava, JÁ contava Ursos — e ainda
assim estava errada, porque a função central `bears_in_play()` (usada por
essa E por outras cartas) exigia `is_creature(c)` antes de reconhecer um
Urso, excluindo Firdoch Core (artefato com Changeling, raramente animado)
da contagem. A ruling oficial do Firdoch Core no Scryfall confirma:
Changeling concede o tipo de criatura **mesmo fora de criatura** ("Kindred
is a card type that allows noncreature cards to have creature types").

**A lição não é "faltou 1 carta" — é que a auditoria clausula-a-clausula
("essa carta tem código?") não pega esse tipo de bug**, porque a carta
com a habilidade (Beorn) e a carta com o problema real (Firdoch Core) são
DIFERENTES. O bug mora numa função auxiliar compartilhada, não na carta
auditada. Isso só aparece auditando o CONCEITO (tudo que responde "o que
conta como X"), não a carta isoladamente.

**Daqui pra frente, além de clausula-a-clausula por carta:**
1. Pra toda função central que define um conceito compartilhado (`is_bear`,
   `is_creature`, `color_sources`, `ready_creatures`, etc.) — listar TODA
   carta do deck que esse conceito toca, não só a que "dá nome" à função.
2. Pra toda carta com Changeling, Kindred, ou qualquer estático que redefina
   tipo/característica de permanente (ex.: "this is every creature type",
   "treat this as a X") — buscar a **ruling** no Scryfall (`rulings_uri`,
   não só `oracle_text`) ANTES de decidir se ela conta ou não pra outras
   cartas do deck que fazem type-checking ("Bears you control", "creatures
   you control that are X"). Oracle text sozinho geralmente não deixa claro
   se o efeito vale fora de criatura — a ruling geralmente deixa.
3. Ao corrigir uma função central, sempre grepar TODOS os call sites dela
   no arquivo antes de mudar (ver caso do Springleaf Parade nesse mesmo
   commit: quase criei um bug novo removendo o filtro errado, se não
   tivesse checado todos os outros usos primeiro).

### Reincidência (2026-09-29, Sarkhan the Masterless): ler a ruling ANTES de escrever o código, não depois

O item 2 acima já mandava buscar a `rulings_uri` de toda carta que redefine
tipo. Na Sarkhan ("each planeswalker you control becomes a 4/4 red Dragon
creature") eu escrevi o efeito e rodei o A/B primeiro, com uma premissa minha
("o PW animado não ativa mais"), e só li as rulings depois. O ruling de
2019-05-03 diz o contrário: *"you can still activate their loyalty abilities
if you haven't done so yet this turn"*. Refiz o código e descartei um lote de
A/B. Na Vronos foi igual (o Construct ataca no mesmo turno se o artefato já
estava em campo). **Passo obrigatório antes de implementar qualquer carta
candidata: baixar as rulings (`rulings_uri`), listar cada uma no
`checklist-oraculo.md` e conferir o código contra elas.** Vale pra toda carta
com "becomes", "phase out", "gains control", "copy" ou substituição, não só
Changeling/Kindred.

## Regra #4 (obrigatória): avaliar sugestão de carta = comparar com os MOTORES do deck e as OUTRAS cartas, nunca poder isolado

Pedido explícito do usuário em 2026-09-15 (deck Megatron), depois de eu
avaliar Melded Moxite vs Demand Answers só pelo ângulo "quantas cartas
compra" e errar a chamada — o usuário trouxe a comparação certa por conta
própria (Ultron copia, alimenta o flip do Megatron, é alvo de
Engineer/Welder) e eu tive que corrigir minha recomendação depois:
**"É esse tipo de lógica que eu quero que vc utilize ao avaliar cada
sugestão minha, comparar com os motores do deck e as outras cartas do
deck!"**

**Daqui pra frente, toda vez que o usuário propuser incluir, cortar ou
trocar uma carta (em QUALQUER deck deste repositório), a avaliação nunca
pode parar em "essa carta é boa/isolada por si". Tem que, na ordem:**

1. Buscar o oráculo real da carta no Scryfall (Regra #1/#2 — nunca por
   memória).
2. Listar os motores/subsistemas reais do deck em questão (ex. no
   Megatron: weld/recursão de artefato, cheat-to-play, Warstorm Surge
   como dano, sacrifício pro flip do comandante, Pia's Revolution como
   seguro) e checar, cláusula por cláusula do oráculo da carta nova,
   **em quantos desses motores ela entra** — não só o efeito óbvio de
   quando ela resolve.
3. Checar interação com cartas ESPECÍFICAS já na lista que têm
   restrição de tipo/custo relevante (ex.: Goblin Engineer só reanima
   MV ≤3; Goblin Welder/Trash for Treasure exigem "artifact card", uma
   sorcery/instant nunca serve de alvo; Ultron/anthem/doubling só
   disparam em permanente entrando, nunca em spell instantânea) — isso
   frequentemente decide o caso mais do que o efeito isolado da carta.
4. Comparar contra a alternativa real (o que está saindo, se for troca)
   pelo MESMO critério — quantos motores/interações a carta que sai
   também alimentava, não só quantas cartas ela comprava.
5. Só then dar a recomendação, e citar explicitamente qual motor/carta
   da lista cada ponto da lógica referencia (nunca "essa é mais forte"
   sem dizer com o que ela interage de verdade nesse deck específico).

Isso vale tanto pra avaliar sugestão do usuário quanto pra eu propor
sugestão minha (upgrade, corte por EDHREC, etc.) — a mesma lógica
relacional, nunca julgamento de power level isolado.

### Adendo obrigatório (2026-09-28): combos e documentação do deck, ANTES de listar motores

Cobrança real do usuário: *"Bladewing não tem um combo no deck? Vc avaliou
isso na sua consideração?"* e *"Como vc ainda erra por não seguir as
regras que criei?"*. Eu recomendei cortar Bladewing the Risen pra Tiamat
sem ver que ela é peça do infinito **Miirym + Bladewing + Terror of the
Peaks**. O combo estava registrado na `auditoria.md` do próprio deck
desde 2026-08-27, via Commander Spellbook. A Regra #4 existia; eu listei
os "motores" de memória, e combo não entrou na lista. O passo 2 acima não
é executável sem as duas checagens abaixo, que passam a ser parte dele:

1. **Ler a documentação do deck antes de listar motores.** Isso vale pra
   `auditoria.md`, `checklist-oraculo.md` e `goldfish-log.md`, com grep
   de "combo", "infinit", "loop" e do nome de CADA carta envolvida (a que
   entra e toda candidata a sair). Nunca listar motores de memória.
2. **Rodar o Commander Spellbook com a lista ANTES e DEPOIS de cada troca
   avaliada.** Endpoint: `POST
   https://backend.commanderspellbook.com/find-my-combos`, comandante +
   lista. O combo que SOME com a troca é custo da troca. O que APARECE
   (inclusive um tutor que monta combo já existente) é ganho, e também
   pode mudar o Bracket (Regra 7 de `user-standing-rules.md`). A
   diferença entra no relatório, com o nome do combo. **A API ignora, sem
   erro, nome de carta que não reconhece** (achado de 2026-10-05, deck
   Mothman): "nenhum combo novo" com nome não reconhecido é resultado
   vácuo. Resolver cada nome antes via `GET /cards/?q=<nome>` (cartas de
   2 faces entram como `Frente // Verso`), registrar no arquivo de dados
   se foi reconhecido, e rodar sempre um **controle positivo** (combo
   conhecido tem de aparecer) e um **controle de corte** (cortar peça de
   combo da lista tem de fazê-lo sumir). Rodadas antigas deste
   repositório que passaram nomes sem essa checagem não foram reauditadas.
3. **Conferir se o simulador executa o combo.** Se não executa, o valor
   da peça no A/B é piso, e isso vira fix no simulador (Regra #5) antes de
   concluir.
4. **Pra toda carta avaliada (a que entra e cada candidata a sair) com
   gatilho ou estático que depende de uma condição — tipo de criatura,
   "Treasure", "artifact", "Dragon", "nontoken" — enumerar POR SCRIPT
   quais cartas da lista satisfazem essa condição**, lendo `type_line` e
   `oracle_text` ao vivo (Changeling e Kindred contam em toda zona; buscar
   a ruling). Nunca listar de memória. Cobrança real de 2026-09-28: *"Vc
   esqueceu que com ela em campo, toda vez que eu tap o Firdoch Core eu
   gero um tesouro. Fica chato ter que te lembrar isso o tempo todo!"*.
   Ao varrer o conceito "Dwarf" (Magda, Firdoch Core, Morophon) e "Treasure
   que você controla" achei 4 furos no simulador, todos subestimando a
   Magda: o Morophon não contava como Dwarf, a Magda não dava +1/+0 aos
   outros Dwarves, Treasure de outra fonte não contava pro tutor, e
   Treasure não gasto sumia no fim do turno. Cortar a Magda passou de
   "aceitável" a "não vale". Regra #3 vale também pra avaliar cartas, não
   só pra auditar o simulador.

## Regra #5 (obrigatória): a análise prioriza o DECK real (oráculo + regras + jogo real), o simulador é evidência de apoio, nunca a fonte da verdade

Achado real em 2026-09-17 (deck Megatron): pedi 3 candidatas a corte e
sugeri Ironsoul Enforcer com base numa métrica que instrumentei — quantas
vezes a habilidade "attacks alone" disparava rodando o goldfish. O número
saiu baixo porque a IA do simulador tem uma convenção fixa (`all_
attackers_combat`: ataca com toda criatura pronta, sempre, todo turno) que
**nunca escolhe deliberadamente atacar só com uma criatura** — então a
métrica media uma limitação da IA do goldfish, não o valor real da carta.
O usuário corrigiu direto: Megatron é o próprio comandante, então "attacks
alone" se satisfaz SÓ com ele atacando, de propósito, puxando um combo
real (Ironsoul reanima artefato do cemitério → Megatron sacrifica esse
artefato pro próprio gatilho de ataque → dano + flip → dano de combate →
converte de novo no postcombat, gera mana). Mesmo padrão de erro também
nas outras 2 candidatas da mesma rodada: Clever Concealment marcada como
"sem sinergia" só porque o goldfish solo não modela remoção real de
oponente pra ela proteger contra (mas é literalmente uma Teferi's
Protection não-GC — altíssimo power level real); Heartless Conscription
marcada como "starva a recursão" sem considerar que o próprio "mana of
any type" dela pluga direto no mana incolor que o Megatron já produz.
Depois de eu confirmar os 3 erros, o usuário perguntou diretamente: **"Vc
consegue fazer a análise priorizando o deck ao invés do goldfish?"**

**A partir de agora, pra QUALQUER avaliação de carta (corte, inclusão,
troca) ou pergunta sobre "essa carta funciona bem aqui?", a ORDEM de
prioridade é sempre:**

1. **Oráculo real (Scryfall) + regras reais do Magic** — incluindo linhas
   de jogo deliberadas que um jogador real escolheria (atacar sozinho de
   propósito, guardar mana, sequenciar gatilhos numa ordem específica),
   não só o que "acontece sozinho" numa partida.
2. **Motores e cartas reais do deck** (Regra #4) — sinergias, restrições
   de tipo/custo, interações específicas.
3. **Comportamento atual do simulador** — usado só como evidência de
   APOIO (confirmar magnitude, achar bug de implementação real). NUNCA
   como árbitro de se uma carta/linha é boa: o goldfish tem convenções
   fixas documentadas (ataca com tudo, sem bloqueio real, sem oponente
   real) que são simplificações do MOTOR DE SIMULAÇÃO, não limites da
   carta ou da linha de jogo real.

**Sinal de alerta (parar e reconsiderar antes de concluir que uma carta é
fraca):** se a única razão pra achar "essa carta não faz nada" é uma
convenção conhecida do simulador (ex.: "sem oponente real", "ataca com
tudo sempre", "sem bloqueio modelado") — isso é candidato a virar um
FIX NO SIMULADOR (nova função que modela a linha de jogo real que faltava,
como `try_megatron_alone_with_ironsoul`), não um corte de carta. Corte de
carta só é válido quando o oráculo real + os motores reais do deck (não o
simulador) mostram baixo valor.

## Regra #6 (obrigatória): auditoria carta-a-carta NÃO pega bug de ORQUESTRAÇÃO DE TURNO — timing de fase nomeado exige checar a ORDEM DE CHAMADAS em `play_turn`/`combat_step`/`end_step`, não só a função da carta

Achado real em 2026-09-18 (deck Megatron): o usuário perguntou quanto
mana incolor o 2º flip do Megatron gera de verdade, questionando minha
afirmação de que hardcastar o BlightSteel Colossus era inviável. Ao
instrumentar a resposta, achei que `megatron_postcombat` (o gatilho real
"At the beginning of each of your postcombat main phases, you may
convert Megatron") estava sendo chamado dentro de `end_step`, que roda
DEPOIS da última chamada de `main_phase` daquele turno (`play_turn`:
`main_phase → combat_step → main_phase → end_step`). A mana gerada
nunca era gastável em NENHUM cast daquele turno — só alimentava um
contador. Isso sobreviveu a pelo menos 3 rodadas anteriores de auditoria
deste mesmo arquivo (linha-a-linha das 99 cartas, varredura de
"mecânicas fantasma", + vários fixes pontuais) porque nenhuma delas
pegaria esse bug por construção: **o código da própria carta estava
100% certo** — a função soma a vida perdida, gera `{C}`, incrementa o
contador, tudo conforme o oráculo. O bug nunca esteve DENTRO da função
de nenhuma carta — esteve em ONDE, na ordem de chamadas do turno, essa
função é invocada. Auditoria carta-a-carta pergunta "essa carta tem
código pra essa cláusula?"; isso nunca pergunta "a ORDEM DAS FASES no
`play_turn` bate com a regra real de quando esse timing acontece?".

**A lição é a mesma da Regra #3, um nível mais abstrato**: ali o bug
morava numa função auxiliar COMPARTILHADA por várias cartas
(`bears_in_play`); aqui mora na própria ORQUESTRAÇÃO DE FASES do turno
(`play_turn`), compartilhada por TODAS as cartas com timing nomeado.
Só apareceu porque o usuário fez uma pergunta numérica adversarial
("quanto gera, pra você dizer que é impossível?") que forçou
instrumentar o runtime de verdade — nenhuma leitura de oráculo vs código
por carta chegaria nessa pergunta.

**Daqui pra frente, toda vez que uma carta tiver texto de oráculo com
timing de fase nomeado** ("at the beginning of your upkeep/end step/
precombat ou postcombat main phase/draw step", etc.):
1. Não basta confirmar que existe uma função pra ela — confirmar TAMBÉM
   onde, em `play_turn`/`combat_step`/`end_step`, ela é chamada, e se
   essa posição bate com a ordem real das fases (upkeep vem antes do
   draw step, que vem antes do main phase, etc.) — em particular, se o
   efeito é "you may spend/cast" algo GERADO por esse gatilho, confirmar
   que a chamada acontece ANTES da janela de conjuração daquela mesma
   fase, não depois.
2. Sempre que adicionar ou mover a chamada de uma função de gatilho de
   fase, reler `play_turn` inteiro (a função é curta) pra confirmar a
   sequência resultante ainda bate com as fases reais de um turno de
   Magic — não só que a chamada nova "roda em algum lugar".
3. Um teste unitário isolado da função em si (dar um estado e chamar a
   função direto) NUNCA pega esse tipo de bug — ele só aparece rodando
   `play_turn`/`simulate_one` completo e checando se o recurso gerado
   está disponível pra gastar na mesma fase que o oráculo promete.

**Agravante real descoberto na mesma rodada**: esse bug específico não
dependia só de auditoria de código — o usuário JÁ tinha descrito a
sequência exata num relato de jogo real, dias antes de eu corrigir
("No último round do goldfish, ataqeui com o Titan e o Megatron, assim
pude jogar o Cityscape com o mana incolor do Megatron" — 2026-09-15).
Isso é literalmente "ataca, gera mana no flip, gasta a mana pra conjurar
algo grande no MESMO turno" — a sequência que estava quebrada. Eu usei
esse relato só pra justificar UMA correção (a remoção real do Cityscape
Leveler + Unearth, que realmente faltavam) e nunca testei se a OUTRA
metade da mesma frase (a mana do Megatron sendo gastável no mesmo turno)
de fato funcionava no simulador — só vim descobrir isso 3 dias depois,
por uma pergunta numérica adversarial não relacionada. **Relato de jogo
real do usuário não é só contexto/flavor pra justificar a correção óbvia
que ele está pedindo — cada cláusula operacional dentro do relato
("consegui fazer X usando Y") é uma afirmação testável sobre o
simulador, e tem que ser instrumentada e confirmada como qualquer outra,
mesmo que o pedido explícito do usuário aponte pra uma cláusula
diferente da mesma frase.**

## Regra #7 (obrigatória): nunca declarar uma auditoria "completa" — declarar o ESCOPO que foi de fato verificado

Cobrança real do usuário em 2026-09-25, depois da avaliação da Draconic
Visitor: *"Acho incrível como vc ainda acha muitos erros após me garantir
que já revisou tudo!"* Nessa rodada apareceram 5 bugs reais em 2 arquivos
(Ur-Dragon e Vihaan). Os dois já tinham "auditoria oráculo-por-oráculo
completa" documentada. **Os 5 caem em classes que JÁ estavam na
taxonomia desta CLAUDE.md:**

- **Fichas de Dragão do Ur-Dragon eram só um contador.** Nunca atacavam
  nem disparavam gatilho de entrada. É a Regra #3: conceito compartilhado
  "Dragão que você controla".
- **Roaming Throne não dobrava Terror of the Peaks nem Dragon
  Broodmother.** É "efeito estático lido em UMA função mas não propagado
  pra todas".
- **Kambal: "This ability triggers only once each turn" estava aplicado à
  cláusula errada.** Falha de leitura cláusula-a-cláusula, justamente o
  método que dizia ter sido seguido.
- **The Reaver Cleaver: "that many" estava achatado pra 1 fixo, com a
  justificativa "o arquivo não rastreia P/T".** Isso era julgamento, não
  impossibilidade: o poder impresso sempre esteve no cache do Scryfall.
  É "fórmula dinâmica achatada".
- **Smothering Tithe: o proxy estava posicionado no MEU turno, mas o
  gatilho real acontece no turno do oponente.** É a Regra #6: posição de
  chamada, não código da carta.

**A falha não foi falta de regra. Foi declarar "completo" depois de uma
passada ancorada em "essa carta tem código?", sem varrer cada classe da
taxonomia, deck a deck, com evidência.**

**Daqui pra frente:**
1. **Palavras proibidas.** Nunca escrever "completo", "tudo revisado",
   "garantido" ou "100%" sobre auditoria de simulador. O relatório lista:
   - quais classes da taxonomia (Regra #1) foram varridas;
   - com que método: grep, instrumentação em runtime ou teste dirigido;
   - quais classes NÃO foram varridas naquele arquivo.
2. **Toda justificativa 📊 do tipo "o arquivo não rastreia X" é suspeita
   até prova em contrário.** Se o dado existe no cache do Scryfall (poder,
   custo, tipo, cor), não é estrutural: é trabalho a fazer. Estrutural é
   só estado real de OPONENTE (Regra #1).
3. **Todo conceito de ficha/token precisa passar em 4 checagens**, não só
   em "é criado":
   - ataca (e com que doença de invocação);
   - dispara os gatilhos de "enters" e "dies/leaves";
   - morre no wipe;
   - conta em todo "you control X".
4. **Todo proxy de gatilho que acontece fora do meu turno precisa de
   checagem explícita.** Upkeep ou draw de oponente, "whenever an opponent
   ...": confirmar se a posição do proxy muda o resultado quando o
   produto é criatura, ou quando uma substituição transforma o produto em
   criatura.

## Regra #8 (obrigatória): todo resultado que sustenta uma conclusão é ARQUIVADO no repositório — resumido, acessível e auditável

Pedido explícito do usuário em 2026-09-30, depois de descobrir que os dados
brutos de 3 dias de A/B estavam só na pasta temporária da sessão (perdida ao
fim dela; só as tabelas resumidas estavam no GitHub): **"Guarde tudo para
referência futura, hoje e sempre, de forma resumida mas acessível e
auditável."**

**Toda vez que uma conclusão entregue ao usuário depender de simulação, A/B,
regressão, instrumentação ou consulta a API (Spellbook, Scryfall), no MESMO
commit da conclusão, arquivar em `<deck>/resultados-ab/<AAAA-MM-DD>-<tema>/`:**
1. **Dados brutos comprimidos** (`dados/*.json.xz`, `xz -9`): nunca só as
   tabelas. Custo medido: ~12 MB para 128 arquivos (268 MB crus).
2. **`LEIAME.md`** com: como foram gerados (simulador, sementes, N, pareamento,
   sintaxe das variantes), **mapa arquivo → o que é → commit do código → status
   (usado / superado / INVÁLIDO) → tabela do log que o usa**, e o **comando que
   reproduz cada tabela**. Lote superado ou inválido se guarda e se MARCA, não
   se apaga.
3. **`resumos/`**: a saída de cada script de resumo, o índice de dados
   (`indice_dados.py`), regressões, bit-identidade e respostas de API.
4. **`orquestracao/`**: os scripts que só existiam na pasta temporária
   (lançadores, `bitident.py`, etc.).
5. **`SHA256SUMS`** (e `sha256sum -c` passando) e `descomprimir.sh`.
6. **Verificação de reprodutibilidade feita ANTES de declarar arquivado:**
   refazer pelo menos as tabelas publicadas a partir dos `.json.xz` e comparar
   com `cmp`. Registrar no `LEIAME.md` quais bateram byte a byte e quais não
   foram conferidas.
7. Linkar a pasta no topo do `goldfish-log.md` do deck.

Modelo a copiar: `prismatic-bridge-wurbg/resultados-ab/2026-09-29-candidatas-e-sisay/`.
Isso vale pra QUALQUER deck deste repositório, não só o Prismatic Bridge, e
**nunca substitui** documentar a rodada em `checklist-oraculo.md` e
`goldfish-log.md` (Regra #1). Ao começar uma rodada nova, criar a pasta de
resultados logo no início e ir guardando os lotes nela, em vez de deixar tudo
pro fim: a pasta temporária da sessão some.

## Regra #9 (obrigatória): a skill `mtg-commander` tem backup em `skills-backup/`; alterou a skill, atualize o backup no mesmo commit

Pedido do usuário em 2026-09-30: *"Atualize a skill e faça uma cópia dela no
GitHub para backup."* A skill é a cópia que eu consulto (regras permanentes,
protocolo de avaliação, referências); a pasta sincronizada dela fica fora do
git; **alterações feitas nela não são gravadas na conta do usuário e o próximo
sync pode sobrescrevê-las** (avisar o usuário toda vez). **Depois de qualquer alteração na skill, ou nos
arquivos espelhados (`CLAUDE.md`, `references/user-standing-rules.md`,
`references/goldfish-sim-card-rules.md`, `references/pod-simulator-design.md`),
rodar `bash skills-backup/sincronizar-skill.sh` (modos e restauração em
`skills-backup/README.md`) e commitar o resultado junto.** As cópias não podem
divergir.

## Regra #10 (obrigatória): classes de erro SISTÊMICAS são varridas por script em TODO simulador (novo ou alterado), e o determinismo é checado com `PYTHONHASHSEED` variável

Pedido do usuário em 2026-10-05: *"Com base nos erros encontrados nas ultimas
revisões, reanálise todos os outros decks em busca de erros semelhantes, e os
corrija"*; depois de eu propor esta regra no relatório final: *"Sim, adicione a
Regra #10 e sincronize a skill"*. **Achado real:** a varredura achou erro de
simulador em 14 dos 18 decks, e **nenhum** teria sido pego por auditoria
carta-a-carta (Regra #1), porque o erro não mora na carta: mora no motor
(mulligan que devolvia o fundo por sorteio, terreno que entra virado nunca
jogado primeiro, terreno que entra desvirado contra o oráculo, fetchland que
ficava em campo como dual, gatilho de "a land enters" ligado só em parte dos
pontos de entrada, resultado que mudava com `PYTHONHASHSEED`). Mesma lição das
Regras #3 e #6, um nível acima: o conceito compartilhado é a **mecânica do
motor**, não a função de uma carta.

**Daqui pra frente, antes de declarar pronto qualquer simulador novo ou
alterado (deck novo, carta nova com efeito de terreno/mulligan/fase, mudança
no `play_land`/`play_turn`/mulligan):**
1. **Rodar as varreduras mecânicas** de `varredura-2026-10-05/scripts/`
   (`LEIAME.md` da pasta explica cada uma e lista os falsos positivos já
   verificados): `audit_entrada.py` e `audit_entrada2.py` (terreno entra virado
   quando o oráculo manda; condições "unless you control…" por SUBTIPO),
   `audit_fetch.py` (sacrifício, 1 de vida, busca por subtipo, thinning),
   `audit_terreno_nao_e_magia.py` (jogar terreno não conta como magia/storm),
   `audit_landfall.py` (todo terreno que entra dispara o landfall do deck),
   `audit_landfall_ordem.py` (o terreno do turno é jogado ANTES do payoff de
   landfall, como o Ruin Crab/Icetill do Mothman, achado em 2026-10-06; lê o
   oráculo do cache, o arquivo do simulador e a `lista.md` do deck; só lista
   candidatos, e a ordem do turno de cada simulador é lida à mão; **hoje 0
   candidatos: os 6 simuladores com payoff de landfall têm a política**),
   `colisao_nome.py` (estado por NOME em vez de por instância). Ler à mão cada
   divergência antes de corrigir ou de classificar como falso positivo.
2. **Conferir a lista de classes do motor** (todas já tiveram erro real): o
   mulligan ESCOLHE o fundo (CR 103.5); o imposto do comandante conta no cast,
   inclusive contra-atacado (CR 903.8); upkeep antes do draw; em T1/T2 o terreno
   que entra virado é jogado primeiro quando não custa desenvolvimento (ensaio a
   seco com cópia profunda, modo GHOST provando que o ensaio não tem efeito
   colateral); fetch real, **inclusive a fetch devolvida do cemitério**; todo
   gatilho de "whenever a land enters" (Field of the Dead, landfall) em TODO
   ponto de entrada (`play_land`, fetch, ramp, blink, saga), não só no
   `play_land`; **a ORDEM terreno × payoff de landfall**: com um terreno por
   jogar, conjurar antes o payoff que o mana de agora já paga, **só se um ensaio a seco do resto
   da fase pré-combate mostrar que o turno não perde nenhuma jogada** (comandante, rocha de
   mana, qualquer jogada de prioridade maior; a fórmula "mana de agora + 1" falhou: não conta
   o mana de landfall já em campo nem o 2º land drop, e atrasou o comandante em 38 de 2.000
   partidas do Beorn e, no Mothman, gastava o único Island do comandante), senão o terreno do turno nunca dispara o landfall, e a Company
   do Thranduil/Maralen nunca libera o 2º land drop no turno em que entra.
   Chave `LANDFALL_PAYOFF_FIRST` (padrão ligada; desligada = ordem antiga, bit
   a bit) em **Mothman, Toph, Beorn, Thranduil, Maralen e Prismatic Bridge**
   (Mothman: +13% de gatilhos do Ruin Crab com o ensaio a seco, +21% com a guarda aritmética, que
   era cega a cor e superestimou o efeito; pedido do usuário em 2026-10-07:
   *"Corrige os simuladores com erro no script para automatizar a ordem de
   jogadas para o landfall"*). **Todo simulador novo, ou carta nova com landfall
   num simulador existente, precisa da política** e o `audit_landfall_ordem.py`
   tem de continuar dando 0 candidatos. **Não coberto (declarar na Regra #7):**
   magia que põe terreno em campo (Cultivate, Farseek, Three Visits...) conjurada
   antes de um payoff que o mana também pagaria depois do terreno; terreno que
   volta ao campo (blink, Lander); ordem de várias fases principais.
3. **Determinismo entre processos.** Os `driver.py` das pastas de resultados
   fixam `PYTHONHASHSEED=0` (senão nada reproduz byte a byte), e por isso **não
   enxergam** dependência de ordem de hash. A única checagem que enxerga é
   `det_check.sh`/`det_wide2.sh`: ≥ 3 `PYTHONHASHSEED` × ≥ 1.500 sementes × 2
   modos, campo a campo, no estado final. Rodar sempre que o código mudar
   iteração de `set`/`dict`/`frozenset` de strings; iterar `set` de `str` com a
   ordem importando é bug (usar ordem do cemitério/lista/`sorted`). Medido: o
   Thranduil mudava de resultado em 14/1.500 (padrão) e 36/1.500 (resiliência)
   sementes entre processos.
4. **Verificação que dá vazio ou zero é vácua: conferir que o número é > 0.**
   Achados desta rodada: o smoke contava 0 cartas nos simuladores baseados em
   dict (sem `BASE_LIBRARY`); a tabela do A/B calculada em memória usava só os
   campos da partida 0 e divergia da refeita dos brutos (12/16 no Captain
   Storm); um inteiro astronômico (`10^212`) estourava a média. **A tabela
   publicada tem que ser função só do bruto arquivado** (comparar `driver.py sum`
   com a re-execução), e o resultado de uma bateria longa se confere pelo
   `Traceback` no `log_driver.txt`, nunca pelo `rc` de um `echo` (`$(date)` no
   mesmo `echo` zera o `$?`).
5. **Cada correção** segue a Regra #1 (chave, bit-identidade com a chave
   desligada em 20.000 × 2 modos, regressão 20.000 × 2 modos com 0 exceções, A/B
   pareado 2.000 e 10.000, teste dirigido), a Regra #7 (declarar o que foi e o
   que NÃO foi varrido) e a Regra #8 (arquivar). Verificação completa
   (`verificar_reproducao.sh --tudo`) re-simula o arquivo VIVO: **não editar o
   simulador enquanto ela roda**.
6. **Rodada longa em segundo plano:** o contêiner pode reiniciar e derrubar tudo
   (aconteceu em 2026-10-05, 15:14 UTC). Comitar e enviar cada deck assim que a
   verificação dele fecha, não deixar tudo pro fim; scripts de espera usam arquivo
   de sinal ou PID, nunca `pgrep -f`/`pkill -f` por nome de script.

**O que esta regra NÃO cobre (continua sujeito à Regra #7, varrer e declarar):**
caminhos de conjuração fora da mão e "whenever you cast"; sacrifício × destroy;
contadores `_sick` agregados; fórmulas dinâmicas achatadas; combinação de
condições de entrada de terreno; choque que não deduz os 2 de vida (Kutzil e
Edgar confirmados; vida só importa onde algo a lê); estado de oponente real.
Esta lista é o piso, não o teto: classe nova achada vira script em
`varredura-2026-10-05/scripts/` e linha nesta regra.
