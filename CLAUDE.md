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
