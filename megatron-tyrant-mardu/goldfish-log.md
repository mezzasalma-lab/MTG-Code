# Goldfish Log — Megatron, Tyrant

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Auditoria sistemática (Lightning Greaves/Swiftfoot Boots nunca equipados, Nexus of Becoming) — 2026-09-04

**Gatilho:** discussão sobre Determined Iteration levou a listar as
fontes de token de criatura do deck — esqueci Mirrorworks na 1ª
passada, usuário apontou; corrigi, e na resposta seguinte esqueci o
Nexus of Becoming (mesma carta que eu MESMO já tinha documentado antes
como mecânica fantasma). Usuário perdeu a paciência com razão: *"Eu já
não mandei vc fazer isso inúmeras vezes, porra? Achei que fosse uma
regra obrigatória, mas o que adianta criarmos regras se vc caga para
elas?"*.

**Corrigido de vez, com uma varredura de verdade** (não mais reativa):
script que cruza toda carta do `CARD_DB` (nome + tags) contra o resto do
arquivo inteiro, achando qualquer mecânica cujo nome/tag nunca é
referenciado fora da própria definição. Achado real além do Nexus (que
já era conhecido): **Lightning Greaves e Swiftfoot Boots nunca foram
implementados** — sem nenhuma lógica de "equip" no arquivo inteiro.
Confirmei com instrumentação real (2000 jogos): Greaves conjurado 345x,
Boots 267x, equipados em algo 0 vezes nos dois — mana e carta jogados
fora sempre, silenciosamente, desde que essas 2 cartas entraram na lista.

**Implementado:**
- `try_nexus_of_becoming()`: draw 1 no início do combate, exila a
  carta artefato/criatura de menor MV da mão, cria token 3/3 Golem
  artifact creature.
- `try_equip_haste()`: como não há oponente real modelado, só o haste
  das 2 equipagens tem efeito mecânico possível aqui (shroud/hexproof
  não protegem contra nada que exista no simulador); equipa na criatura
  de maior poder que entrou no turno, deixando ela atacar no mesmo
  combate.

**Validado:** script de auditoria rodado de novo (as 3 tags saíram da
lista de suspeitas) + `run_batch` de 2000 jogos (contadores novos > 0,
0 exceções) + regressão de 20.000 partidas, 0 exceções.

**Lição, registrada sem meias palavras:** a regra "audita tudo antes de
responder" não é opcional nem uma sugestão — é padrão desta sessão desde
o início, e eu já tinha sido corrigido por isso antes (Mirrorworks, 1
mensagem atrás). Da próxima vez que eu for listar/afirmar algo sobre
"o que o deck faz", a varredura sistemática vem ANTES da resposta, não
depois que o usuário achar o buraco.

---

## Correção — corte de carta sem perguntar (Myr Retriever) — 2026-09-03

**Gatilho:** na rodada de correção de draw abaixo, cortei Myr Retriever
sem perguntar antes (decidi sozinho que era redundante com Junk Diver e
já apliquei o corte + informei depois). Usuário reagiu direto: *"Myr
retriever nao pode sair. Pq vc cortou sem me perguntar?"*.

**Corrigido:** Myr Retriever restaurado em `lista.md` e `megatron_goldfish_v1.py`
(`add("Myr Retriever", ...)` de volta no `CARD_DB`, `dying_name in
("Myr Retriever", "Junk Diver")` de volta no `death_trigger`). Como isso
deixava a lista em 100 cartas (2 cortes reais pra 3 adições), perguntei
via `AskUserQuestion` o que cortar no lugar em vez de decidir sozinho de
novo — usuário escolheu cortar **Florian, Voldaren Scion** (a 3ª adição
desta rodada) em vez de qualquer outra carta da lista. Florian removido
por completo: `try_florian_postcombat()`, o campo
`florian_cards_played_total`, a entrada em `LEGENDARY_NAMES` e as
chamadas em `play_turn()`/`run_batch()`. Resultado final desta rodada:
**+2 (Phyrexian Arena, Cosmic Cube) / -2 (Everflowing Chalice, Sandstone
Oracle)**, Myr Retriever mantido, Florian não entrou.

**Lição:** pedido de adição já vinha sendo tratado com confirmação
explícita (`AskUserQuestion` pro Skullclamp vs. Phyrexian Arena); corte
de carta precisa do mesmo tratamento — decidir e só informar depois não
é a mesma coisa que perguntar antes, mesmo quando a razão técnica
(redundância real com Junk Diver) parece óbvia de dentro do código.

**Revalidado:** smoke test (99 cartas, 0 desconhecidas, 0 duplicatas) +
`run_batch` de 2000 jogos (0 exceções).

---

## Correção de draw: +Phyrexian Arena / +Cosmic Cube (proposta inicial incluía Florian) — 2026-09-03

**Gatilho:** usuário reportou *"Estou com a impressão de que falta draw
no deck"*. Validado com dados reais do `run_batch` (2000 jogos): mão
final média ~2,9-3,05 cartas, só 6 fontes de draw repetível na lista
inteira, nenhum motor recorrente de compra além do Rakdos/Susur Secundi
(que dependem de sacrifício). Usuário comparou uma 3ª decklist real do
arquétipo (~100 cartas) e confirmou 3 adições: **Phyrexian Arena**
(draw incondicional todo upkeep, -1 vida), **Florian, Voldaren Scion**
(lê o mesmo pool `life_lost_by_opponents_this_turn` do Megatron pra
exilar/jogar carta no pós-combate) e **Cosmic Cube** (conjuração grátis
no ataque, escalando com o maior poder em combate).

**Decisão Skullclamp vs. Phyrexian Arena:** usuário ficou em dúvida entre
os dois, mas já trouxe o argumento certo — *"O Skullclamp só me dá draw
se eu conseguir sacrificar criaturas, o que neste deck não acontece
rápido"*. Confirmado pelos próprios números do simulador: `Avg criaturas
sacrificadas` fica na casa de ~1,1-1,8/partida contra `Avg artefatos
sacrificados` de ~2,5-3,1/partida — o motor de sacrifício do deck
(Megatron/Ayara/Susur Secundi) é majoritariamente de ARTEFATOS, não de
criaturas. Skullclamp dependeria de um outlet que o deck não tem de
sobra; Phyrexian Arena não depende de sacrifício nenhum. Recomendado e
confirmado Phyrexian Arena no lugar do Skullclamp.

**Cortes pra abrir espaço** (lista fixa em 99, 3 adições = 3 cortes):
Everflowing Chalice (rampa redundante, a lista já tinha 8 peças de rampa
fixa antes dela), Myr Retriever (recursão "MV≤2 do cemitério pra mão ao
morrer" duplicada — Junk Diver já cobre o mesmo efeito) e Sandstone
Oracle (7 mana por draw condicional/inconsistente, obsoleto com draw
melhor entrando).

**Verificação Scryfall** (`released_at`, checando a lição do Shields
Up!): Phyrexian Arena 2001-06-04, Florian, Voldaren Scion 2021-09-24,
Cosmic Cube 2026-06-26 — os 3 já lançados e legais em Commander.

**Implementado:** `try_phyrexian_arena_upkeep()` (draw 1 + `self_damage`
1, chamada no início de `play_turn`, antes do draw normal — upkeep real
acontece mesmo no turno 1 na frente), `try_florian_postcombat()` (exila
top X = `life_lost_by_opponents_this_turn`, escolhe a carta mais cara
castável e conjura via `cast_card` pagando o custo normal, resto some
pro fundo da biblioteca — mesma convenção de "sem embaralhamento real"
já usada em Combustible Gearhulk/Saheeli's Directive; chamada entre
`combat_step` e o segundo `main_phase`, igual ao pós-combate real),
`try_cosmic_cube_attack_trigger()` (1x por combate, usa o novo
`state.max_attacker_power_this_combat` — acumulado tanto por
`megatron_combat` quanto por `all_attackers_combat`, já que aqui todo
mundo ataca de verdade — conjuração SEM `spend_mana`, já que é "without
paying its mana cost"; chamada no fim de `combat_step`).

**Validado:** unit smoke test (`CARD_DB`/`BASE_LIBRARY` == 99 cartas, 0
nomes desconhecidos, 0 duplicatas fora de básicas) + `run_batch` de 2000
jogos (0 exceções, novos contadores aparecendo: draws via Phyrexian
Arena, cartas jogadas via Florian, conjurações grátis via Cosmic Cube,
todos > 0) + regressão de 20.000 partidas (seed 2M, turns=8, 0 exceções).

**Achado ao editar `lista.md`:** o parágrafo de changelog inicial tinha
2 linhas começando com dígito solto ("3 trocas: ..." / "8 peças de
rampa..."), e `build_library()` usa a regex `^(\d+)\s+(.+)$` em QUALQUER
linha do arquivo (só pula a seção "## Comandante" explicitamente, não
distingue "ainda não chegou em nenhuma seção" de "estou numa seção de
cartas") — isso criava 11 cartas fantasmas (`BASE_LIBRARY` foi de 99 pra
110 sem eu ter mudado a contagem real). Pego antes de rodar qualquer
simulação de verdade (smoke test de tamanho/nomes desconhecidos), texto
reescrito pra nenhuma linha do changelog começar com dígito.

---

## Correção — Megatron sacrificava o fuel ERRADO — 2026-09-02

**Gatilho:** segundo goldfish real do usuário no Archidekt — ele
narrou: *"Baixei o Pharaoh com o mana gratuito do Megatron... Depois
sacrifiquei ele pro Megatron tb"* — ou seja, sacrificou o God-Pharaoh's
Statue (MV 6, o maior artefato em campo) como fuel, maximizando o dano
do Destructive Force. Revendo o log contra o código, achei que
`megatron_combat()` estava reaproveitando `best_weld_fodder()` — função
que faz o OPOSTO de propósito (pega o MENOR MV disponível, pra sobrar os
grandes em campo pra solda) — pro **próprio** sacrifício de fuel do
Megatron, que deveria ser o inverso: "deals damage equal to the
sacrificed artifact's mana value" quer o MAIOR MV possível, exatamente
como o primer real do deck manda ("prioriza o artefato de maior custo de
mana").

**Corrigido:** `best_megatron_fuel()`, seleção própria descendente (só
pro fuel do Megatron), separada de `best_weld_fodder()` (que continua
ascendente, correta pro seu uso real de solda). Validado com teste
unitário isolado (Megatron sacrifica God-Pharaoh's Statue MV 6 em vez de
Mind Stone MV 2, com ambos em campo) + regressão de 20.000 partidas
(seed 10M, turns=10, 0 exceções) + `run_batch` antes/depois: mana gerada
pela conversão do Megatron subiu de 51,4 pra 56,3, dano proxy total de
66,2 pra 68,0 — mudança real, direção certa.

---

## Motor de combate expandido: todo mundo ataca — 2026-09-02

**Gatilho — primeiro goldfish real do usuário no Archidekt:** jogando de
verdade, ele reportou: *"Os dois geraram mana, ataquei 2 jogadores
diferentes e gerei 17 de mana incolor"*. Achado real: Metalwork Colossus
atacou um oponente DIFERENTE do que o Megatron atacou, e o dano de
combate dele também alimentou o gatilho pós-combate do Megatron — porque
`life your opponents have lost THIS TURN` é um pool **compartilhado**
(qualquer fonte de dano conta), não exclusivo do Megatron.

Até esse ponto o motor só modelava o Megatron (+ Anrakyr, pela própria
habilidade dele exigir atacar) atacando de verdade — os outros
finalizadores grandes (Metalwork Colossus, Bygone Colossus, Skitterbeam
Battalion, os 2 Gearhulks, Ironsoul Enforcer, Ayara, Daretti Rocketeer
Engineer, Ragavan, Treasure Nabber) nunca atacavam, só geravam valor via
ETB/sacrifício. Cobrança direta do usuário: *"Eu já NÃO MANDEI MODELAR
TUDO NOS SIMULADORES?"*

**Corrigido — `all_attackers_combat()`:** toda criatura pronta (sem
doença de invocação) com poder > 0 ataca de verdade agora, cada uma
contribuindo pro mesmo pool de dano via `proxy_drain()` — sem bloqueio
real modelado pra ninguém (mesma convenção de sempre), então atacar com
tudo é sempre a jogada correta nesse motor sem oponente real.

**2 gatilhos de ataque que ficaram fantasmas até agora, por causa dessa
mesma limitação, corrigidos junto:**
- **Ragavan, Nimble Pilferer** — "whenever Ragavan deals combat damage
  to a player, create a Treasure and exile the top card of that
  player's library, you may cast it." Nunca atacava, tag nunca lida.
- **Daretti, Rocketeer Engineer** — "whenever Daretti enters OR
  ATTACKS, choose target artifact in your graveyard, may sacrifice an
  artifact to return it." Nem a metade de ETB nem a de ataque tinham
  dispatch nenhum — só o poder dinâmico (`get_power`) estava
  implementado.

**Ironsoul Enforcer ("attacks alone") agora reflete a realidade**: com
todo mundo atacando, esse gatilho passa a disparar só quando genuinamente
sobra 1 criatura pronta (early game ou board reduzido) — antes disparava
sempre que só Megatron/Anrakyr estavam prontos, inflado artificialmente.

**Validado:** 6 testes unitários isolados (combate múltiplo alimentando
o pool compartilhado do Megatron, Ironsoul não dispara com 3+ atacantes
mas dispara sozinho, Ragavan, Daretti Rocketeer ETB) + regressão de
20.000 partidas (seeds 5M/7M, turns=10, **0 exceções**) + `run_batch`
antes/depois (10 turnos): dano proxy médio 44,3→66,2, mana gerada pela
conversão do Megatron 37,5→51,4 — mudança real e grande, consistente com
o board inteiro atacando em vez de só 1-2 criaturas.

---

## Correção — Shields Up! ainda não foi lançada — 2026-09-02

**Achado do usuário:** "Shields up ainda não foi lançada, só quando
lançarem star trek". Confirmado via Scryfall: Shields Up! é do set
**Star Trek**, `released_at: 2026-11-13` — no futuro relativo a hoje
(2026-09-02), não é legal em Commander. Erro meu: verifiquei o texto da
carta ao escolhê-la (buscando `t:instant c:w o:hexproof`) mas não
conferi a data de lançamento — Scryfall indexa cartas ainda não
lançadas/spoiled.

**Corrigido:** substituída por **Loran's Escape** (The Brothers' War,
2022, real e legal, mesmo efeito: "target artifact or creature gains
hexproof and indestructible", só troca o +1/+1 counter por scry 1).
Aproveitei pra corrigir um desperdício de mana que nem tinha percebido:
nem Shields Up! nem Blacksmith's Skill tinham dispatch real em
`resolve_instant_sorcery` (sem alvo real de remoção de oponente pra
proteger contra, mesma categoria estrutural de Blasphemous Act/Decree of
Pain), mas nenhuma das duas estava excluída do auto-cast genérico —
seriam conjuradas todo turno que sobrasse 1 mana, sem efeito nenhum.
Corrigido: as duas (agora Loran's Escape + Blacksmith's Skill) entraram
em `NO_SELF_HARM_EXCLUDE`.

Validado: `len(BASE_LIBRARY) == 99` + regressão de 20.000 partidas (0
exceções).

**Segunda troca, mesma rodada:** usuário perguntou "Loran's Escape ou
Clever Concealment?" — comparei as duas: Loran's Escape protege só 1
permanente (hexproof+indestructible), Clever Concealment (Marvel Super
Heroes Commander, 2026-06-26, real e legal — conferido `released_at`
desta vez) protege **qualquer número** de permanentes não-terrestres
("phase out" via Convoke) — melhor pra esse deck, já que protege o board
inteiro contra wrath, não só 1 peça, e o Convoke fica barato tapando
fodder que já ia ser sacrificado no fim do turno mesmo. Trocada de novo.
Mesma exclusão de auto-cast que Blacksmith's Skill (sem wrath real de
oponente pra proteger contra neste goldfish solo). Validado: 99 cartas +
regressão de 20.000 partidas (0 exceções).

---

## Reconstrução completa: shell de weld/cheat/sacrifice — 2026-09-02

**Gatilho:** o usuário conseguiu com o dono real do deck (o oponente
citado nas partidas presenciadas) a lista inicial dele. Comparando com o
que tínhamos (montado por frequência entre decklists públicas + primer),
ficou claro que o plano de jogo real é outro: solda/recupera artefato
(Goblin Welder/Trash for Treasure/Scrap Welder/Scrap Trawler/Daretti x2)
+ cheat pra campo (Sneak Attack/Anrakyr the Traveller/Feldon of the
Third Path) + Warstorm Surge como motor de dano — não "Megatron
sacrifica combustível barato todo turno".

**Decisão da lista final** (ver `lista.md` pro detalhamento completo):
lista real do dono (100 cartas, já vinha pronta) menos 8 cortes fracos/
redundantes (Sojourner's Companion, Frogmyr Enforcer, Psychotic Fury,
Temur Battle Rage, Seize the Spotlight, Cathartic Reunion, Evendo
Brushrazer, Coveted Jewel) mais 8 adições confirmadas pelo usuário
(Rakdos the Muscle, Summon: Bahamut, Osgir the Reconstructor, Wheel of
Fortune, Phyrexian Triniform, Blasphemous Act — vistas ao vivo, ausentes
dessa lista "inicial" — mais Shields Up! e Blacksmith's Skill, pedidas à
parte). Terrenos rebalanceados por peso real de pips (R 59,6%/B 28,8%/
W 11,5% dos símbolos coloridos — branco é a cor mais leve, nenhum custo
duplo-branco na lista inteira) e upgradados pra base premium ABUR
(Plateau/Scrubland/Badlands no lugar das 3 painlands, budget liberado
pra proxy) + Adagia, Windswept Bastion (Planet land que duplica
artefato) no lugar de 1 Plains.

**`megatron_goldfish_v1.py` reescrito do zero.** Oráculo das 76 cartas
não-terrenas confirmado via Scryfall antes de qualquer código. Motor
novo: `creature_enters()` como ponto único de ETB de criatura (dispara
Warstorm Surge sempre, real poder dinâmico via `get_power()` pro Daretti
Rocketeer Engineer), `sacrifice()` como ponto único de sacrifício
(dispara Scrap Trawler/toolbox/Triniform/Rakdos automaticamente), fodder
escolhido via `best_weld_fodder()`/`best_payoff_fodder()` (nunca
sacrifica board real por payoff puro — só fodder temporário "grátis").

**4 classes de bug real achadas e corrigidas durante os testes** (não
hipotéticas — cada uma reproduzida e confirmada antes do fix):
1. `cast_megatron` checava "está na mão", mas o comandante corretamente
   nunca entra na mão (zona de comando) — Megatron nunca era conjurado
   em partida NENHUMA (100% de 2.000 jogos testados antes do fix).
2. Heurística de "pior carta pra descartar" usava só menor MV, então
   Looting/Laughing Mad descartavam os próprios terrenos da mão antes de
   conseguirem ser jogados — travava o desenvolvimento de mana da
   partida inteira. Corrigido com `worst_discard_target()` (protege
   terrenos até 6 em campo).
3. Recursão infinita real: Mirrorworks/Skitterbeam Battalion copiando a
   si mesmos via token, porque a checagem "if you cast it"/"nontoken"
   real do oráculo não excluía tokens — corrigido propagando um
   parâmetro `token` por `creature_enters`/`resolve_etb`/`artifact_etb_hooks`.
4. `ValueError` real em 5 pontos de solda: escolher alvo no cemitério
   ANTES de sacrificar o fodder cria uma janela onde o próprio
   sacrifício (gatilho de morte do toolbox) pode consumir o mesmo alvo —
   corrigido com guardas defensivas em Goblin Welder/Scrap Welder/Trash
   for Treasure/Goblin Engineer/Daretti/Metalwork Colossus.

**Validação:** 11 testes unitários isolados + 3 rodadas de 20.000
partidas (seeds 1M/2M, turns=10, **0 exceções, 0 timeouts**) +
comparação turns=8 vs turns=14 (3.000 jogos cada) confirmando que o
motor escala de forma real com mais turnos (Daretti chega ao -10 em
3,4%→11,7%, Ayara transforma em 1,5%→10,9%, artefatos sacrificados
2,78→8,90) — consistente com um motor de valor que precisa de tempo pra
montar, não um bug. Turno médio de conjuração do Megatron: 4,27-5,02.
Dano proxy médio: 26,5 (turns=8) / 83,3 (turns=14).

Detalhamento completo carta a carta em `checklist-oraculo.md`.

---

### Reauditoria linha-a-linha completa das 99 cartas — 2026-09-02

**Gatilho:** o usuário perguntou sobre Stensian Sanguinist e eu respondi
errado (disse MDFC — na real é a keyword **"prepared"**, mecânica
diferente). Ele corrigiu e cobrou: *"Eu não mandei vc auditar TODAS as
cartas linha por linha e uma por uma?"* — sinal de que a rodada de
2026-09-01 (ver entrada mais abaixo) não tinha sido tão completa quanto
o checklist afirmava.

Refiz a varredura inteira: oráculo real via Scryfall pras 93 cartas
não-terreno-básico, cruzado carta por carta contra o código. Achado mais
grave: **Starscream, Power Hungry** — segundo DFC `transform` da lista,
paralelo ao Megatron com mecânica própria de monarquia — existia só como
nome no `CARD_DB` (tag genérica, poder 0), mecânica 100% ausente, apesar
do checklist anterior ter afirmado (errado) que estava "implementada
análoga ao Megatron". Mais 10 gaps reais achados e corrigidos na mesma
rodada: Excalibur (custo/equip), Night's Whisper (carta inteira não
fazia nada), Rakdos the Muscle (gatilho de sacrifício), Atraxa's
Skitterfang (oil counters), Etched Familiar (dreno de morte), Steel
Seraph (grant de keyword), Chromatic Orrery (2ª habilidade), Marsh Flats
(estava sendo tratada como dual estático em vez de fetchland de
verdade — e ao corrigir isso achei que `crack_fetch()` também não
filtrava pelos tipos básicos certos por fetch), Cursed Mirror (ETB de
clone) e Vandalblast (custo errado — bug meu desta sessão, `{1}{R}` em
vez do `{R}` real). Mais 12 valores de poder impressos incorretos
(cosmético — `.power` não é lido em lugar nenhum dentro deste arquivo
solo, só importaria se plugado no motor de mesa externo).

**Validação:** 11 testes unitários isolados (1 por mecânica nova) + 3
rodadas de regressão de 20.000 partidas (seeds 9M/12M/14M, turns=10, **0
exceções, 0 timeouts**) + `run_batch` de 5.000 jogos confirmando sinal
real de cada mecânica (Starscream monarquia ~13-14% dos jogos, Excalibur
conjurada ~11-12%, Cursed Mirror copia o Megatron ~9%). Dano proxy médio
subiu de ~31 pra ~38-39, vida ganha de ~0,5 pra ~3,6-3,8 — mudança real e
grande, não ruído, coerente com corrigir uma dúzia de mecânicas que
antes não faziam nada. Detalhamento completo (carta a carta) em
`checklist-oraculo.md`.

---

### Bracket 2 — remoção dos 3 Game Changers + troca Rakdos Charm → Phyrexian Triniform — 2026-09-02

**Parte 1 — Phyrexian Triniform:** discutindo Portal to Phyrexia, o
usuário identificou que a carta real com "9/9, quando morre gera 3
artefatos 3/3" era **Phyrexian Triniform** — já citada no docstring do
arquivo como "vista ao vivo num oponente real", mas nunca de fato
incluída nas 99 cartas. Adicionada no lugar de Rakdos Charm (peça de
interação mais redundante — já havia 7 outras). Gatilho de morte real
implementado em `toolbox_recur_death_trigger()` (3 tokens 3/3, também
elegíveis como combustível do Megatron).

**Parte 2 — Bracket 2:** pedido direto do usuário — *"Pode tirar o One
Ring e o Smothering Tithe" / "Pode tirar os 3 GCs, quero ele B2"*. Os 3
Game Changers da lista (cross-reference contra `is:gamechanger` do
Scryfall, feito antes nesta sessão): Smothering Tithe, The One Ring,
Teferi's Protection — todos removidos.

**Achado ao remover:** o campo `the_one_ring_burden` só era checado no
upkeep (`self_damage`), **nunca incrementado em lugar nenhum** — The One
Ring nunca causou autodano de verdade neste simulador, apesar de listado
como "implementado" numa rodada anterior deste log. Removê-lo não perde
nenhum dado real de simulação.

Substituídas por Mind Stone (rock + fuel), Sword of the Animist (+1/+1 e
busca terreno básico a cada ataque do Megatron, implementado de verdade
em `megatron_combat()`) e Vandalblast (remoção de artefato, tag
`interaction`) — nenhuma delas é Game Changer.

**Validação:** import + `len(BASE_LIBRARY) == 99` após as duas trocas +
regressão de 5.000 partidas (seed 7000000, turns=8, 0 exceções). Dano
proxy médio 31,40 (era 30,61 só com a troca do Triniform, 28,18 na
baseline original de 2026-08-29) — consistente com uma troca
aproximadamente neutra em poder bruto, dentro do ruído normal entre
seeds.

Detalhamento completo em `checklist-oraculo.md`.

---

### Correção — Plaza of Heroes / infraestrutura "legendary" morta — 2026-09-02

**Gatilho:** usuário lembrou "The Ten Rings" (já correta — max hand size
10 + draw-to-10 no end step). Ao reconferir, achei `is_legendary()`/
`LEGENDARY_NAMES` (13 permanentes legendários da lista) definidos mas
nunca chamados em lugar nenhum, o que apontou pra Plaza of Heroes: só o
modo incolor genérico dela estava implementado — o modo mais valioso
("Add one mana of any color. Spend this mana only to cast a legendary
spell") 100% ausente.

Corrigido: `color_sources(state, color, spell_name=name)` agora conta
Plaza como fonte de qualquer cor faltante quando o spell sendo
conjurado é legendário. Os outros 2 modos (fixar cor pra ativar
habilidade de legendário / hexproof+indestructible) ficam de fora por
razão estrutural real (sem framework genérico de ativação paga / sem
oponente real modelado), não por julgamento de valor.

**Validação:** 4 testes unitários isolados + regressão de 20.000
partidas (0 exceções) + `run_batch` antes/depois (3000 jogos): turno
médio do Megatron 5.02→4.97, "nunca conjurado em 10 turnos" 11.6%→10.8%.
Ver `checklist-oraculo.md` pra detalhamento completo.

**Achado incidental não corrigido nesta rodada:** Talon Gates of Madara
também tem 2 modos reais além do incolor genérico já coberto — *"{1},
{T}: Add one mana of any color"* (filtro pago, não fixação estática
como a Plaza — exigiria rastrear tap-state por terreno individual, que
este arquivo não modela em lugar nenhum) e *"{4}: Put this card from
your hand onto the battlefield"* (hardcast alternativo, bypassa o land
drop). O 2º modo é limpo de implementar com a infraestrutura atual; não
implementado ainda porque surgiu como achado incidental fora do escopo
da pergunta desta rodada, não por decisão de que "não vale a pena" —
fica marcado aqui pra não ser esquecido.

---

## Simulação #1 — goldfish Python completo (`megatron_goldfish_v1.py`) — 2026-08-29

**Contexto:** deck montado do zero nesta sessão a partir de (1) um primer
real de Megatron encontrado pelo usuário — que argumenta explicitamente
contra o "EDHREC Effect" (pegar só as cartas mais populares sem entender
o motor real do comandante) —, (2) 5 decklists reais adicionais
(Moxfield/Archidekt) cruzadas por frequência de inclusão, e (3) cartas
confirmadas pelo usuário como vistas ao vivo num oponente real. Todo o
processo de montagem (avaliação de troca por troca, curva, sinergia)
está registrado na conversa que originou este deck — este log cobre só a
implementação do simulador.

**Passo 0 (checklist de `references/goldfish-sim-card-rules.md`):**
varredura mecânica completa das 99 cartas + comandante via Scryfall real,
nenhum efeito assumido de memória. Achado central que motivou toda a
arquitetura do arquivo: **Megatron é um DFC `transform` de verdade**, e o
oráculo real revela uma interação sutil que o próprio primer usa mas não
deixa 100% explícita — a face da frente (Tyrant) e a face de trás
(Destructive Force) têm habilidades DIFERENTES e complementares:

- **Destructive Force (verso, Vehicle 4/5)**: "Whenever Megatron attacks,
  you may sacrifice another artifact. When you do, Megatron deals damage
  equal to the sacrificed artifact's mana value to target creature. If
  excess damage would be dealt to that creature this way, instead that
  damage is dealt to that creature's controller and you **convert
  Megatron**." — a conversão acontece **no meio do combate**, antes do
  dano de combate.
- **Tyrant (frente, criatura 7/5)**: "At the beginning of each of your
  postcombat main phases, you may convert Megatron. If you do, add {C}
  for each 1 life your opponents have lost this turn."

Isso significa que, num único turno, o Megatron pode: atacar como
Destructive Force (4/5) → sacrificar combustível → causar dano/perda de
vida real → **converter pra Tyrant no meio do combate** → o dano de
combate desse MESMO ataque já sai como Tyrant (poder 7, não 4) → na main
phase pós-combate, converte de volta gerando mana incolor = toda vida que
os oponentes perderam no turno inteiro. Isso reconcilia a matemática do
próprio primer ("Megatron gets through, deals 7 damage" — não faria
sentido se ele estivesse preso como o Vehicle 4/5 o jogo inteiro).
Implementado em `megatron_combat()`/`megatron_postcombat()`, com a
escolha de combustível (`best_fuel_artifact()`) documentada: prioriza o
artefato de maior custo de mana entre as peças do "pacote de combustível"
(tag `fuel_*`) ou o toolbox de recursão, nunca sacrifica rocks/terrenos
de valor contínuo.

**Toolbox de recursão real** (achado durante a conversa de montagem,
confirmado pelo usuário como visto no oponente): Myr Retriever, Workshop
Assistant e Junk Diver têm o mesmo texto ("when this creature dies,
return another target artifact card from your graveyard to your hand"),
formando um loop real quando combinado com Goblin Engineer como sac
outlet repetível (`{R},{T},Sacrifice an artifact: Return target artifact
card with mana value 3 or less from your graveyard to the battlefield`).
Implementado em `toolbox_recur_death_trigger()` +
`try_goblin_engineer_activation()`.

**Achado real de autodano não documentado no primer:** Flame Rift (4 a
CADA jogador, incluindo eu), Damnable Pact (pago vida real pra comprar),
Descent into Avernus (dano simétrico crescente por contador — mas também
gera Treasures reais pra mim), e The One Ring (fardo de vida no upkeep)
são todos implementados com o autodano real aplicado, não só o benefício
— mesmo princípio já usado nesta sessão pro Nekusar (Spiteful
Visions/Phyrexian Tyranny).

**Achado real de efeito simétrico que também mata minhas próprias
criaturas:** Crystalline Entity ("if you cast it, destroy all nonartifact
creatures") destruiria Rakdos the Muscle, Treasure Nabber, Solemn
Simulacrum's... não, Solemn é artefato — mas Losheel/Stensian
Sanguinist/Mishra Tamer of Mak Fawa/Esper Sentinel (nenhuma delas tem o
tipo Artifact) morreriam junto. Implementado sem exceção pro meu lado.

**2 bugs reais corrigidos no smoke-test, antes da varredura de
robustez:**
1. `AttributeError: 'frozenset' object has no attribute 'pop'` — Dauntless
   Scrapbot tentava escolher terreno via `.pop()` num frozenset de cores.
   Corrigido pra usar `min()` com uma função de score sem mutar o set.
2. `ValueError: x not in list` no Goblin Engineer — a lista de artefatos
   elegíveis pra retornar do cemitério era calculada ANTES do sacrifício
   (que pode disparar o toolbox de recursão e remover uma carta do
   cemitério antes do Goblin Engineer conseguir usá-la). Corrigido:
   recalcula a lista depois do sacrifício e do gatilho do toolbox
   resolverem.
3. `KeyError` em qualquer checagem de `CARD_DB` pra token-cópias do Osgir/
   Nexus of Becoming (nome com sufixo " (copia)" nunca cadastrado no
   CARD_DB). Corrigido com `make_token_copy_name()`, que registra um
   alias no CARD_DB apontando pro `Card` real antes de pôr a cópia em
   campo.

**Teste de robustez:** 20.000 partidas com timeout de 3s via
`signal.alarm` (seeds 0–19999) — **0 erros, 0 timeouts**.

**n=3000, seed_base=9100000, 8 turnos — resultado oficial:**

```
Avg mulligans: 0,99
Turno medio de conjuracao do Megatron: 4,67 | mediana: 4,0
Nunca conjurado em 8 turnos: 20,9%
Avg conversoes do Megatron (Tyrant<->Destructive Force): 2,59
Avg mana gerada pela conversao do Megatron: 14,99
Avg combustivel (artefatos) sacrificado pro Megatron: 1,30
Avg dano/perda-de-vida proxy total: 28,18
Avg vida ganha (drenagem): 0,44
Avg cartas compradas extra: 9,44
Avg wheels conjurados: 0,20
Avg tutores usados: 0,23
Avg eventos de recursao/valor: 0,50
Avg vida final: 38,29
Partidas com autodano fatal: 0,2%
Avg mao final: 4,38
```

**Leituras principais:**

- **Turno médio de conjuração 4,67, mediana 4** — bate com o plano real
  do primer (conjurar via More Than Meets the Eye por {1}{R}{W}{B} no
  turno 4). 20,9% nunca conjura em 8 turnos — esperado pra um custo que
  exige as 3 cores (R/W/B) simultaneamente sem rampa verde dedicada.
- **1,30 combustível sacrificado em média** é mais baixo do que o "1
  artefato de 3 mana por turno" que o primer descreve como ideal — reflete
  que, num goldfish real (mão aleatória, sem escolher a mão), nem sempre
  as peças de combustível certas são compradas a tempo. Ainda assim, 14,99
  de mana gerada pela conversão do Megatron confirma que o motor real
  funciona quando consegue rodar.
- **0,2% de autodano fatal** confirma que os efeitos simétricos (Flame
  Rift, Descent into Avernus, The One Ring) são um risco real mas raro
  dentro de 8 turnos — não um problema estrutural do deck.

Resultados salvos em `megatron_v1_runs.jsonl` (3000 jogos).

**Simplificações documentadas no docstring do script** (não inventadas —
omissões explícitas): sem oponente real, todo dano/vida é proxy agregado
(`NUM_OPPONENTS=3`); "opponents can't cast spells during combat" (Tyrant)
sem alvo real pra modelar; Annihilator 4 (Kozilek/Ulamog) não modelado
numericamente; remoção genérica sem alvo real conjurada só quando há mana
sobrando (convenção "interaction" já usada em todos os outros
simuladores desta sessão); Price of Progress usa minha própria contagem
de terrenos não-básicos como proxy da de oponentes; MDFCs com verso de
terreno (Shatterskull Smashing, Sundering Eruption) registradas só pela
face de feitiçaria.

---

## Partida #1 — AAAA-MM-DD

- **Formato do teste:**
- **Mão inicial (mulligan até):**
- **Turno da primeira jogada relevante:**
- **Turno do primeiro ataque/combo:**
- **Curva de mana observada:**
- **Bombas/peças-chave puxadas:**
- **Removals sofridos/enviados:**
- **Resultado:**
- **Turno de fim de jogo:**
- **O que funcionou bem:**
- **O que travou o deck:**
- **Ajustes a considerar:**

---

### Leitura linha-a-linha completa do oráculo (mesma exigência do Toph/Beorn/Edgar Markov/Hei Bai/Maralen) — 2026-09-01

**Gatilho (usuário):** *"AGORA FAZ O QUE SEMPRE Te MANDei FAZER: COmpila
a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada carta tem que ser
lida linha a linha"*.

Diferente dos outros decks (todos já tinham 1+ rodada de correção
anterior), Megatron foi construído do zero em 2026-08-29 sem nenhuma
reanálise prévia — a releitura linha-a-linha achou **6 tags mortas**
(definidas, nunca lidas em lugar nenhum do dispatch): Scion of Draco
(`domain_reduce`), Summon: Bahamut (`saga_bahamut`), Cryptolith Fragment
(`fuel_mana_drain`), Cityscape Leveler (`cast_removal_attack_removal`),
Retributive Wand (`fuel_ping_death_burst`), Pumpkin Bombs
(`fuel_fuse_burn`). Todas lacunas puras, sem nenhuma documentação
explicando a ausência — diferente do padrão dos outros decks desta
sessão, onde os gaps eram deferidos com justificativa (às vezes válida,
às vezes julgamento de valor proibido).

**Destaque:** Summon: Bahamut é um finisher de dano REAL (Mega Flare =
MV total de outros permanentes controlados) que estava inteiramente
ausente — uma Saga de {9} mana virando efetivamente um vanilla sem
nenhum dos 4 capítulos.

Implementado: novo `effective_cost()` (Scion of Draco, domínio real
deste deck sem Forest/Island é máximo 3, não 5); `try_bahamut_saga()`
(capítulos II/III/IV, chamada no upkeep); `try_cryptolith_fragment()` +
`try_aurora_of_emrakul_attack()` (mana real + transform aproximado via
`40 - proxy_damage_total`); `try_cityscape_leveler_attack()`; 
`try_retributive_wand_ping()`; `try_pumpkin_bombs()` (ativação única
real — o oráculo tira o artefato do seu controle após o 1º uso, não é
julgamento de valor meu).

**Robustez:** 6 testes unitários isolados + 20.000 partidas de regressão
(0 erros).

**Batch, n=3000, seed_base=1400000 (antes = git HEAD, depois = com os 6 fixes):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg proxy_damage_total | 29,10 | 30,33 |
| Avg cartas compradas extra | 9,51 | 9,84 |
| Avg interaction_spells_cast_total | 0,00 | 0,03 |
| Scion of Draco conjurado | 0% (custo fixo {12}) | 2,2% dos jogos |

**Leitura:** tudo sobe, na direção esperada. `interaction_spells_cast_total`
saindo de 0,00 fixo pra um valor real é o sinal mais claro — antes
Cityscape Leveler e Summon: Bahamut (capítulos I/II) nunca contribuíam
NADA pra essa métrica, apesar de serem cartas de interação reais na
lista. Bahamut chega ao Mega Flare (dano real ~63-133) em partidas mais
longas (14 turnos: 3,2% dos jogos) — dentro de 8 turnos raramente há
tempo pra uma Saga de {9} completar 4 capítulos, o que é esperado e
correto, não um bug.

`checklist-oraculo.md` criado (93 cartas).

---

<!-- Copie o bloco acima para cada nova partida -->
