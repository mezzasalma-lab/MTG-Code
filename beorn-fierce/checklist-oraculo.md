# Checklist cláusula-a-cláusula — Beorn the Fierce

## Achado real 2026-09-14 (usuário apontou os demais motores de draw: Great Henge, Selvala, Toski, Tribute to the World Tree)

Usuário pediu confirmação de que esses 4 também estão certos, além de
Beorn/Beast Whisperer. Reli o oráculo real (Scryfall) clausula a clausula
contra o código pros 4:

- **The Great Henge** — `{T}: Add {G}{G}` ✅ (`total_mana()`/`green_sources()`,
  2 mana, fonte verde dupla). ETB "put a +1/+1 counter... and draw a card"
  ✅ (`on_creature_enters()`). A cláusula "You gain 2 life" da habilidade
  de mana fica de fora — mas esse arquivo **não rastreia vida em lugar
  nenhum, pra nenhuma carta** (War Room paga vida, Defiler of Vigor paga
  vida — ambos já documentados como N/A pela mesma razão estrutural desde
  antes desta rodada). Não é um julgamento de valor sobre o Great Henge
  especificamente, é uma omissão consistente do arquivo inteiro.
- **Toski, Bearer of Secrets / Ohran Frostfang** — "whenever a creature
  you control deals combat damage to a player, draw a card" ✅, e já
  escala corretamente por atacante × fonte (`len(attackers) * draw_sources`
  em `combat_step()` — 2 cartas em campo = 2 draws por atacante que
  conecta, não 1 fixo). Confirmado certo.
- **Tribute to the World Tree** — "draw if power>=3, else 2 counters" ✅,
  usa `effective_power()` (com anthems), não o poder impresso bruto.
  Confirmado certo.
- **Selvala, Heart of the Wilds (2ª habilidade, a de draw — não a de
  mana)** — 🐛 **bug real encontrado**. Oráculo: *"Whenever another
  creature enters, its controller may draw a card if its power is
  greater than each **other** creature's power."* — compara contra as
  outras criaturas **atualmente** em campo. O código usava um acumulador
  `max_power_seen` que só subia, nunca descia, mesmo quando a
  criatura-recorde saía de campo (morte, bounce, Managorger removido pela
  premissa de lifespan). Isso tornava o gatilho artificialmente mais
  difícil de disparar depois que a maior criatura do jogo já tivesse
  saído — o oposto de "compra demais", uma imprecisão real na direção
  contrária à queixa do usuário, mas ainda uma imprecisão.

**Corrigido:** removido `max_power_seen` (campo morto depois da correção),
substituído por comparação ao vivo contra `max(effective_power(state, c)
for c in battlefield if is_creature(c) and c != card)` a cada entrada de
criatura.

**Validação:** 2 testes unitários dirigidos (Ghalta poder 12 entra e sai
de campo, depois Little Bear poder 3 com só Selvala poder 2 restando —
dispara corretamente, o que o bug antigo bloquearia pelo recorde
histórico de 12; com Ghalta ainda em campo, a mesma Little Bear
corretamente NÃO dispara) — ambos passando. 20.000 partidas de regressão
(seed 9980000+), 0 exceções. Batch de 2.000 partidas antes/depois (mesma
seed 9970000) instrumentado especificamente na fonte "Selvala draw":
0,1975→0,1815 compras/partida em média (**caiu**, não subiu — explicação:
a versão nova recalcula `effective_power` das outras criaturas AO VIVO a
cada comparação, então uma vez que os anthems tribais de Bear (Beorn/
Chronicle of Victory/Patchwork Banner) entram em campo, TODAS as outras
Bears ficam mais fortes retroativamente na comparação — o código antigo
congelava o poder de cada criatura no momento em que ela entrou, nunca
reavaliando sob anthems que vieram depois, então ficava artificialmente
mais fácil de bater um "recorde" desatualizado e mais baixo. A versão
nova é mais fiel ao sistema de camadas real do jogo — P/T é sempre
característica atual, não congelada no momento do ETB).

---

## Achado real 2026-09-14 (usuário apontou Beorn + Beast Whisperer somando muita carta na mesa): 3 pontos de cast de criatura pulavam o hook de "quando você conjura um spell"

**Contexto:** usuário relatou descartar 2 cartas por turno na mesa por
causa da soma de Beorn + Beast Whisperer, e perguntou se a soma dos
efeitos de draw batia com o que o simulador mostrava.

Investigando: `on_spell_cast_effects()` é a função central que despacha
Beast Whisperer ("whenever you cast a creature spell, draw a card"),
Necklace of Girion ("whenever you cast a green spell, +1/+1 counter") e
Dancing from Dark to Dawn (contadores = MV do spell de criatura). Só que
ela só era chamada de **1 lugar** (`cast_spell()`, usada pelo loop guloso
de conjurar cartas da mão) — existem **3 outros pontos reais** do arquivo
que conjuram uma carta de verdade (aumentam `spells_cast`, cobram mana) e
nenhum deles chamava esse hook:

1. **Cast do próprio comandante** (2 blocos em `main_phase()` — um antes
   do loop guloso, outro depois) — conjurar Beorn é conjurar um spell de
   criatura verde real (`{3}{G}{G}`). Beast Whisperer/Necklace of
   Girion/Dancing from Dark to Dawn nunca disparavam nesse cast — nem
   Managorger Hydra (que também estava faltando nos 2 blocos).
2. **Beorn, Reluctant Host // Till and Tend conjurado do exílio**
   (`try_cast_beorn_host_from_exile`, 2ª metade do Adventure) — é um cast
   de criatura verde real (`{4}{G}`), Managorger já disparava mas Beast
   Whisperer/Necklace of Girion/Dancing from Dark to Dawn não.
3. **Germination Practicum via Paradigm** (recast grátis da cópia do
   exílio todo turno) — é `Sorcery {3}{G}{G}`, não dispara Beast
   Whisperer/Dancing (corretamente, `on_spell_cast_effects()` já filtra
   por `is_creature_spell`), mas É um spell verde real — Necklace of
   Girion deveria disparar em CADA recast, não só no cast original.

**Corrigido:** chamada de `on_spell_cast_effects()` adicionada nos 3
pontos (mais o incremento de Managorger que faltava nos 2 blocos do
comandante).

**Validação:** 3 testes unitários dirigidos (cast do comandante com Beast
Whisperer+Necklace+Managorger em campo; cast do Beorn Host do exílio com
Beast Whisperer+Necklace; recast do Germination Practicum via Paradigm
soma o Necklace mas não dispara Beast Whisperer) — todos passando. Batch
de 2.000 partidas antes/depois (mesma seed 9950000): `extra_draws`
17,322→17,412, `mão final` 8,934→8,966, `spells_cast` 12,384→12,403 —
movimento pequeno e real (esses 3 pontos disparam quase sempre 1x por
partida cada, não são motores repetíveis como o gatilho de combate da
própria Beorn). 20.000 partidas de regressão (seed 9960000+), **0
exceções**.

---

## Achado real 2026-09-14 (reportado pelo usuário na própria mesa): Firdoch Core conta como Urso mesmo sem estar animado

**Contexto:** usuário notou que na mesa física ele termina com muito mais
cartas do que o simulador mostrava, e apontou especificamente: "toda vez
que eu tiver com três ursos... incluindo o Firdoch Core como o artefato
que ele também é urso, no início do combate eu compro duas cartas."

Oráculo real da Beorn (Scryfall, confirmado ao vivo): *"Trample. Other
Bears you control get +2/+2. At the beginning of combat on your turn, put
a trample counter on up to one target creature you control. It becomes a
Bear in addition to its other types. Then if you control three or more
Bears, draw two cards."* — a cláusula final não exige que os "Bears"
sejam **criaturas**, só que você os controle.

Firdoch Core (`Kindred Artifact — Shapeshifter`, tem Changeling: *"This
card is every creature type"*) raramente é animado (custa {4} pra virar
4/4 até o fim do turno) — na prática, fica em campo o jogo inteiro como
rock de mana, nunca criatura. Ruling oficial do Scryfall pro Firdoch Core
confirma que isso não importa: *"Kindred is a card type that allows
noncreature cards to have creature types... [ex.] is an Elf (although not
a creature) while on the battlefield."* Ou seja, Firdoch Core **é um Urso
o tempo todo**, animado ou não.

**Bug real:** `bears_in_play()` (a função central que o gatilho da Beorn
usa pra contar "controle 3+ Bears") exigia `is_creature(c)` ANTES de
checar `is_bear(state, c)` — excluindo Firdoch Core da contagem sempre que
ele não estava animado, ou seja, na prática quase sempre. Isso fazia o
motor de compra principal do deck (o próprio gatilho da Beorn, ~3 vezes
por partida em média) disparar mais tarde e com menos frequência do que
na mesa real.

**Achado colateral ao investigar (não reportado pelo usuário, achado
verificando a própria função):** a tag `"changeling"` estava na carta
errada — no encantamento **Springleaf Parade** em si (`{"token_maker",
"changeling"}`), quando o oráculo real diz *"create X 1/1 ... Shapeshifter
creature tokens **with changeling**"* — é o TOKEN que tem Changeling, não
o encantamento (que nunca é criatura, e por isso nunca deveria contar como
Urso). Isso teria virado um bug NOVO e oposto (contar Springleaf Parade
demais) no momento em que eu removesse o filtro `is_creature()` de
`bears_in_play()` pra corrigir o Firdoch Core — corrigido junto, a tag de
changeling ficou só no `"Springleaf Parade Token"` (que já tinha sua
própria entrada correta).

**Corrigido:** removido o filtro `is_creature(c)` de `bears_in_play()` —
agora conta qualquer permanente que `is_bear()` reconheça, criatura ou
não (a própria `is_bear()` já trata corretamente os outros casos: Maskwood
Nexus só afeta criatura de verdade, `converted_to_bear` só se aplica a algo
que já era criatura quando convertido pela própria Beorn).

**Validação:** 4 testes unitários dirigidos (Firdoch Core sozinho conta
como Urso mesmo não-animado; sem ele a contagem cai 1; Springleaf Parade
o encantamento NÃO conta; o Springleaf Parade Token conta) — todos
passando. 20.000 partidas de regressão (seed 9900000+), **0 exceções**.
Batch de 2.000 partidas antes/depois (mesma seed 9800000): gatilho "3+
Bears, draw 2" médio por partida 2,998→3,107; % de jogos que dispararam
esse gatilho no turno 4 4,9%→6,0%, no turno 5 28,0%→32,6%, no turno 6
63,9%→67,1%; turno médio do 1º disparo (entre os jogos que dispararam)
6,03→5,93; % de jogos que NUNCA dispararam em 8 turnos 8,4%→7,8%; compras
extras totais médias por partida 17,44→17,89. Movimento real, consistente
com a queixa do usuário (motor de compra dispara mais cedo e com mais
frequência) — não é dramático porque Firdoch Core só "destrava" o gatilho
nos jogos em que os outros 2 Ursos já estavam perto de 3, mas é
sistemático (afeta toda partida em que Firdoch Core está em campo, que é
a maioria).

---

## Auditoria oráculo-por-oráculo completa — 2026-09-13

Extensão pra este deck da mesma auditoria já feita no Megatron/Azula:
pedido do usuário pra revisar TODOS os decks do repositório, cláusula a
cláusula contra o oráculo real (Scryfall), atrás de implementações
parciais que passaram pelas varreduras anteriores (este deck já tinha
sido auditado de forma muito completa em 2026-08-28 até 2026-09-02, com
vários "achado real" documentados acima — esta é mais uma passada em
cima de um arquivo já maduro).

**8 gaps reais encontrados e corrigidos:**

1. **Cultivate/Sakura-Tribe Elder/Solemn Simulacrum/Titania's Command/
   Archdruid's Charm (modo terreno)/Lumra (retorno de terrenos)** — todos
   os 6 têm oráculo real "put/return onto the battlefield **tapped**",
   mas NENHUM marcava o terreno buscado como tapped — o terreno produzia
   mana de graça no turno em que entrava (mana fantasma, tempo mais
   rápido do que o real). Corrigido com um contador novo
   (`tapped_basics_this_turn`/`tapped_green_this_turn`, não o `set`
   `tapped_lands_this_turn` já existente — esse é indexado por NOME e só
   funciona pra terrenos singleton como Bala Ged Sanctuary; "Forest" tem
   31 cópias no decklist, então marcar "Forest" nesse set zeraria a mana
   de TODAS as cópias em campo, não só a buscada).
2. **Ezuri's Predation** (`mass_removal`) só era excluída do loop de
   interação dedicado (`try_use_own_interaction`), não do loop guloso
   principal — podia ser conjurada por lá mesmo sem nenhum efeito real
   possível (cria 0 tokens sem criaturas de oponente modeladas).
   Corrigido: excluída dos dois loops, nunca mais conjurada de graça (8
   mana por zero efeito, correto pra esse motor solo).
3. **Gigantic Big Bear** — oráculo real é "Hexproof, **haste**", mas a
   tag `haste` nunca tinha sido atribuída (só Craterhoof tinha) — o motor
   tratava essa criatura de 10 mana como doente de invocação no turno em
   que entra, atrasando os gatilhos de combate (Ohran/Toski/Beorn) em 1
   turno inteiro.
4. **Shamanic Revelation** — "draw a card for each creature you control"
   tinha um piso artificial `max(1, creatures)`, garantindo 1 compra
   mesmo com 0 criaturas em campo (o oráculo real não tem esse piso).
5. **Lumra, Bellow of the Woods** — "Lumra's power and toughness are each
   equal to the number of lands you control" é uma CDA real, mas
   `BASE_POWER`/`BASE_TOUGHNESS` tinham ela hardcoded em 0 — zerando ela
   em TODO cálculo que usa esses dicts (Garruk's Uprising/Tribute to the
   World Tree "power >= X", redução de custo do Goreclaw, maior poder do
   Great Henge/Selvala, Last March of the Ents), apesar dela ser
   normalmente um dos maiores corpos do deck (8-15+ de poder/resistência).
   Corrigido com `lands_in_play(state)` calculado ao vivo.
6. **Toughness nunca recebia os 3 anthems reais de Bear** (Beorn +2/+2,
   Chronicle of Victory +2/+2, Patchwork Banner +1/+1) — já corrigidos
   pro PODER numa rodada anterior (`effective_power()`), mas a
   TOUGHNESS (usada só por Last March of the Ents, "greatest toughness
   among creatures you control") lia o `BASE_TOUGHNESS` bruto. Nova
   função `effective_toughness()` espelhando `effective_power()`, com a
   mesma premissa já documentada pra `greatest_power_in_play()` de somar
   `counters_on_board` ao maior valor (assume que os contadores foram
   pra maior criatura).
7. **Natural Order** escolhia qual criatura verde sacrificar usando
   `BASE_POWER.get(c, 0)` bruto (não `effective_power()`) — podia
   escolher errado (Lumra aparecendo como poder 0, ou um Bear com anthem
   real parecendo mais fraco do que é).
8. **Garruk's Uprising** (ETB "if you control a creature with power 4 or
   greater, draw a card") tinha a mesma imprecisão — comparava contra
   `BASE_POWER` bruto em vez de `effective_power()`.

**Validação:** smoke test (73 nomes no `CARD_DB`, 99 cartas na
`BASE_LIBRARY`, 0 desconhecidas) + 2.000 partidas antes/depois (mesma
seed) + 20.000 partidas de regressão, 0 exceções em todas. Testes
unitários dirigidos confirmaram cada uma das 8 correções: Cultivate
zera a mana do turno da mesma forma que Three Visits NÃO zera (correto,
Three Visits não tem "tapped" no oráculo); Gigantic Big Bear ataca no
turno em que entra; Lumra com 7 Forests em campo tem poder/resistência
7; Ezuri's Predation nunca aparece nos candidatos de nenhum dos 2 loops
de conjuração; Shamanic Revelation com 0 criaturas compra 0; Last March
of the Ents com um Bear sob o anthem da Beorn usa a toughness já somada
(2 base + 2 anthem = 4), não a bruta.


Pedido direto do usuário (2026-09-01), o mesmo trabalho já feito pro Toph
agora exigido pra **todos os decks**: *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA COMO EU
MANDEI DESDE O COMEÇO"* — seguido de: *"cada carta tem que ser lida
linha a linha e isso tudo incorporado aos modelos que já fizemos até
agora"*.

Este arquivo quebra as 69 cartas não-terreno-básico da lista (comandante +
deck, excluindo as 31 Forest) em cláusulas individuais — uma por
frase/parágrafo do oráculo real, buscado ao vivo via Scryfall
(`POST /cards/collection` + `/cards/named?fuzzy=` pros 2 MDFC/Adventure) —
e marca o status de cada uma contra o `beorn_goldfish_v1.py` atual,
verificado por leitura/grep do arquivo, não por recordação.

**Contexto importante:** diferente do Toph (que partiu de um estado
pouco auditado), este deck já tinha passado por **duas rodadas de
auditoria anteriores** (2026-08-30 e 2026-08-31, documentadas no próprio
docstring do arquivo e em `goldfish-log.md`) que corrigiram vários gaps
reais (Eternal Witness, Natural Order, Lumra, Nykthos, War Room, Chameleon
Colossus, Beorn's Hospitality, etc — ver comentários "achado real
2026-08-30/31" espalhados pelo código). Mesmo assim, a releitura
linha-a-linha desta rodada achou **7 gaps reais adicionais** que as
rodadas anteriores tinham deixado passar — provando que "já foi auditado
antes" não é garantia de completude, exatamente o padrão que motivou o
pedido do usuário.

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — não produz número neste modelo por decisão de
  arquitetura documentada (sem P/T por criatura individual, sem combate
  real, sem oponente) — limite conhecido do simulador, não julgamento de
  valor.
- 📝 **Documentado, fora de escopo** — decisão explícita por motivo
  genuinamente estrutural.
- 🐛 **Corrigido nesta rodada (2026-09-01)** — gap real que as auditorias
  anteriores (2026-08-30/31) tinham deixado passar.

## 🐛 Os 7 gaps corrigidos nesta rodada

1. **Selvala, Heart of the Wilds** — mana ability real é `{G}, {T}: Add X
   mana in any combination of colors, where X is the greatest power among
   creatures you control`. Estava caindo no tratamento genérico de "dork
   de 1 mana" (mesma categoria de Llanowar Elves) — subestimava
   MUITO o valor real (X escala com counters/anthems, facilmente 4-12+
   nesse deck). Corrigido em `total_mana()`: `max(0, greatest_power_in_play(state) - 1)`.
2. **Return of the Wildspeaker** — fórmula errada: estava conflada com a
   de Shamanic Revelation ("draw por criatura"), mas o oráculo real é
   "draw cards equal to the **greatest power** among **non-Human**
   creatures you control" — filtro de tipo E fórmula diferentes. Corrigido
   em `cast_spell()` com novo helper `is_human()`.
3. **Obscuring Haze** — "If you control a commander, you may cast this
   spell **without paying its mana cost**." Alt-cost grátis nunca
   modelado — o sim cobrava sempre o custo impresso. Corrigido em
   `effective_cost()`/`can_cast()`.
4. **Lightning Greaves** — Equip {0} nunca era ativado em lugar nenhum;
   o haste que ela concede de graça nunca beneficiava nenhuma criatura.
   Corrigido: `try_lightning_greaves_equip()`, novo campo
   `lightning_greaves_equipped_to`, `can_attack()` atualizado.
5. **Allosaurus Shepherd** — `{4}{G}{G}: each Elf creature... 5/5
   Dinosaur` 100% ausente (só as estáticas "can't be countered" estavam
   modeladas). Corrigido: `try_allosaurus_shepherd_pump()` (mesmo
   tratamento do Chameleon Colossus: métrica de ativação, buff temporário
   não propagado pra BASE_POWER).
6. **Chronicle of Victory / Patchwork Banner** — os anthems reais
   ("+2/+2 tipo escolhido" e "+1/+1 tipo escolhido") nunca tinham efeito
   de poder modelado — só o anthem da própria Beorn era somado, e só
   localmente dentro de `on_creature_enters` (nunca propagado pro resto
   do arquivo). Corrigido: novo helper `effective_power()`, usado
   consistentemente em `on_creature_enters`, `total_power_in_play()`,
   `greatest_power_in_play()` e no desconto de custo do Goreclaw.
7. **Roaming Throne** só dobrava o gatilho de combate da Beorn — mas
   Ayula, Queen Among Bears é ela mesma um Bear, e seu próprio gatilho de
   ETB ("whenever another Bear enters") também deveria dobrar sob Roaming
   Throne. Corrigido em `on_creature_enters()`.

Validado com 7 testes unitários isolados (1 por gap) + regressão de
20.000 partidas (0 erros) + `run_batch` n=3000 antes/depois (ver
`goldfish-log.md` pros números completos).

---

## Allosaurus Shepherd {G}
1. This spell can't be countered — 📊 opponent_dependent (sem counterspell de oponente modelado).
2. Green spells you control can't be countered — 📊 idem.
3. `{4}{G}{G}`: cada Elfo vira 5/5 Dinossauro até o fim do turno — 🐛 `try_allosaurus_shepherd_pump()`, ativa com 2+ Elfos em campo.

## Ambush Viper {1}{G}
1. Flash — 📊 sem instant-speed real modelado (só conjura na main phase).
2. Deathtouch — 📊 combate.

## Archdruid's Charm {G}{G}{G}
1. Modo tutor (criatura/terreno pra mão/campo) — ✅ `cast_spell()`, único modo sem alvo de oponente.
2. Modo +1/+1 counter + fight — 📝 opponent_dependent (fight exige criatura do oponente).
3. Modo exile artefato/encantamento — 📝 opponent_dependent.

## Ayula's Influence {G}{G}{G}
1. Discard terreno: cria Bear 2/2 — ✅ `try_ayula_influence()`.

## Ayula, Queen Among Bears {1}{G}
1. Outro Bear entra: 2 contadores OU fight — ✅ `on_creature_enters()` (modo contadores, fight é opponent_dependent 📝). 🐛 Roaming Throne agora dobra esse gatilho corretamente (Ayula é ela mesma um Bear).

## Bala Ged Recovery // Bala Ged Sanctuary
1. Face sorcery: retorna carta do cemitério — ✅ `try_bala_ged_recovery()`.
2. Face terreno: enters tapped, `{T}`: Add G — ✅ `play_land()` + genérico.

## Beast Whisperer {2}{G}{G}
1. Cast creature spell: draw — ✅ `on_spell_cast_effects()`.

## Beast Within {2}{G}
1. Destroy target permanent — ✅ tag "removal", `try_use_own_interaction()`.
2. Controlador cria Beast 3/3 — 📊 é o OPONENTE que recebe o token (efeito do oponente, não nosso).

## Beorn the Fierce (comandante) {3}{G}{G}
1. Trample — 📊 combate.
2. Other Bears +2/+2 — ✅ `effective_power()` (🐛 corrigido: antes só local em on_creature_enters, não propagado pro resto do arquivo).
3. Início de combate: trample counter + vira Bear + 3+ Bears→draw 2 — ✅ `combat_step()`.

## Beorn's Hospitality {1}{G}
1. Landfall: +1/+1 counter em criatura alvo — ✅ `on_land_enters()`.
2. `{5}{G}{G}`: vira criatura Bear P/T=terrenos — ✅ `try_beorns_hospitality_animate()`.

## Beorn, Reluctant Host // Till and Tend
1. Trample (face criatura) — 📊 combate.
2. Till and Tend: land drop extra — ✅ `try_till_and_tend()`.
3. Cast da criatura do exílio depois — ✅ `try_cast_beorn_host_from_exile()`.

## Birds of Paradise {G}
1. Flying — 📊 combate.
2. `{T}`: Add any color — ✅ genérico (ramp/green_source_any).

## Boseiju, Who Endures
1. `{T}`: Add G — ✅ genérico.
2. Channel: destrói artefato/encantamento/terreno não-básico do oponente — 📝 opponent_dependent.

## Chameleon Colossus {2}{G}{G}
1. Changeling — ✅ `is_bear()` conta via tag "changeling".
2. Protection from black — 📊 combate/oponente.
3. `{2}{G}{G}`: +X/+X (X=próprio poder) até o fim do turno — ✅ `try_chameleon_colossus_pump()` (métrica de ativação, buff temporário não propagado).

## Chronicle of Victory {6}
1. Tipo escolhido (Bear, convenção do arquivo) — ✅ `is_bear()`.
2. Criaturas do tipo escolhido +2/+2, first strike, trample — 🐛 `effective_power()` (first strike/trample são 📊 combate, +2/+2 agora real).
3. Cast spell do tipo escolhido: draw — ✅ `on_spell_cast_effects()`.

## Craterhoof Behemoth {5}{G}{G}{G}
1. Haste — 📊 combate.
2. ETB: trample + X/+X pro time (X=criaturas) — 📊 buff temporário até o fim do turno, mesma família de efeitos de combate não rastreados por criatura individual (documentado, contado como finisher via tag).

## Cultivate {2}{G}
1. Busca 2 básicas, 1 campo tapped + 1 mão — ✅ `cast_spell()`.

## Dancing from Dark to Dawn {3}{G}{G}
1. Cast creature spell: X contadores (X=mv) — ✅ `on_spell_cast_effects()`.
2. Landfall: cria Bear 2/2 — ✅ `on_land_enters()`.

## Defiler of Vigor {3}{G}{G}
1. Trample — 📊 combate.
2. Custo alternativo (pagar 2 vida, spells verdes custam {G} menos) — ✅ `effective_cost()` (vida não rastreada, sempre assume que paga — documentado).
3. Cast green permanent spell: +1/+1 em cada criatura — ✅ `on_spell_cast_effects()`.

## Emerald Medallion {2}
1. Spells verdes custam {1} menos — ✅ `effective_cost()`.

## Eternal Witness {1}{G}{G}
1. ETB: retorna carta do cemitério pra mão — ✅ `cast_spell()`.

## Ezuri's Predation {5}{G}{G}{G}
1. Cria token 4/4 por criatura do oponente + fight — 📝 opponent_dependent (tag "mass_removal", excluída de `try_use_own_interaction`).

## Firdoch Core {3}
1. Changeling — ✅ `is_bear()`.
2. `{T}`: Add any color — ✅ genérico (ramp/green_source_any).
3. `{4}`: vira 4/4 artefato-criatura até o fim do turno — 📝 buff temporário, sem P/T por criatura individual (documentado desde 2026-08-30).

## Forgotten Ancient {3}{G}
1. Player casts spell: pode por +1/+1 counter — ✅ `on_spell_cast_effects()` (próprios casts) + `play_turn()` (aproximação de 2 casts de oponentes/turno).
2. Upkeep: move contadores entre criaturas — 📊 sem efeito no modelo agregado (counters_on_board é um total, mover entre criaturas não muda a soma).

## Garruk's Uprising {2}{G}
1. ETB: se poder>=4 em campo, draw — ✅ `cast_spell()`.
2. Criaturas têm trample — 📊 combate.
3. Criatura poder>=4 entra: draw — ✅ `on_creature_enters()`.

## Genji Glove {5}
1. Equipped: double strike — 📊 combate.
2. Ataca (1º combate): untap + combate extra — ✅ `combat_step()` + equip em `main_phase()`.
3. Equip {3} — ✅ `main_phase()`.

## Germination Practicum {3}{G}{G}
1. 2 contadores em cada criatura — ✅ `cast_spell()`.
2. Paradigm (recast grátis do exílio) — ✅ `main_phase()`.

## Ghalta, Primal Hunger {10}{G}{G}
1. Custo reduzido por poder total em campo — ✅ `effective_cost()`.
2. Trample — 📊 combate.

## Gigantic Big Bear {5}{G}{G}
1. Can't be countered — 📊 opponent_dependent.
2. Hexproof, haste — 📊 combate/oponente (haste não precisa de dispatch, é vanilla stats).

## Goreclaw, Terror of Qal Sisma {3}{G}
1. Creature spells poder>=4 custam {2} menos — ✅ `effective_cost()` (🐛 agora usa `effective_power()`, considerando anthems).
2. Ataca: criaturas poder>=4 +1/+1 e trample até o fim do turno — 📝 buff temporário de combate, mesma família de Craterhoof/Unnatural Growth (documentado nesta rodada — antes não tinha nenhum comentário explicando a ausência).

## Haywire Mite {1}
1. Morre: ganha 2 vida — 📊 vida não rastreada neste modelo (mono-verde, documentado no header do arquivo).
2. `{G}`, Sac: exile artefato/encantamento não-criatura — 📝 sem restrição de "do oponente" no oráculo, mas sem alvo próprio valioso (Regra 1) nem alvo de oponente modelado — excluída explicitamente de `try_use_own_interaction` (comentário na linha ~1506).

## Heroic Intervention {1}{G}
1. Permanentes ganham hexproof/indestructible até o fim do turno — 📊 proteção reativa, sem remoção de oponente modelada pra proteger contra.

## Last March of the Ents {6}{G}{G}
1. Can't be countered — 📊 opponent_dependent.
2. Draw = maior toughness + coloca criaturas da mão em campo — ✅ `cast_spell()`.

## Lightning Greaves {2}
1. Haste + shroud — 🐛 `try_lightning_greaves_equip()` + `can_attack()` (shroud continua 📊, sem remoção de oponente modelada).
2. Equip {0} — ✅ idem (reativa todo turno, sem {T} no custo).

## Little Bear {2}{G}
1. Flash — 📊 sem instant-speed modelado.
2. ETB: untap outra criatura + se for Bear, +1/+1 counter — ✅ `cast_spell()` (untap sem efeito modelável, documentado; contador real).

## Llanowar Elves {G}
1. `{T}`: Add G — ✅ genérico.

## Lotus Cobra {1}{G}
1. Landfall: Add any color — ✅ `on_land_enters()`.

## Lumra, Bellow of the Woods {4}{G}{G}
1. Reach, vigilance — 📊 combate.
2. P/T = terrenos controlados — 📊 sem P/T por criatura rastreado (não afeta os thresholds deste deck, que usam BASE_POWER fixo).
3. ETB: mill 4, retorna terrenos do cemitério pro campo tapped — ✅ `cast_spell()`.

## Managorger Hydra {2}{G}
1. Trample — 📊 combate.
2. Player casts spell: +1/+1 counter — ✅ `cast_spell()` (próprios) + `play_turn()` (aproximação de oponentes + premissa de "morre" por remoção depois de ~4 turnos).

## Maskwood Nexus {4}
1. Suas criaturas são todo tipo de criatura — ✅ `is_bear()`, `is_human()`.
2. `{3}, {T}`: cria Shapeshifter 2/2 changeling — ✅ `try_maskwood_nexus()`.

## Natural Order {2}{G}{G}
1. Custo adicional: sacrifica criatura verde — ✅ `can_cast()` (gate) + `cast_spell()` (sacrifício real).
2. Busca criatura verde pro campo — ✅ `cast_spell()`.

## Necklace of Girion {2}{G}
1. Cast spell verde OU Forest entra: +1/+1 counter em criatura alvo — ✅ `on_spell_cast_effects()` + `on_land_enters()`.
2. `{T}`: Add G — ✅ genérico (green_source).

## Nykthos, Shrine to Nyx
1. `{T}`: Add C — ✅ genérico.
2. `{2}, {T}`: Add mana = devoção à cor escolhida — ✅ `try_nykthos()`.

## Obscuring Haze {2}{G}
1. Se controla comandante, pode conjurar de graça — 🐛 `effective_cost()`/`can_cast()`.
2. Previne todo dano de criaturas do oponente — 📊 sem combate/dano de oponente modelado.

## Ohran Frostfang {3}{G}{G}
1. Criaturas atacantes têm deathtouch — 📊 combate.
2. Criatura causa dano de combate a jogador: draw — ✅ `combat_step()`.

## Patchwork Banner {3}
1. Tipo escolhido (Bear, mesma convenção de Chronicle/Roaming Throne) — ✅ `is_bear()`.
2. Criaturas do tipo +1/+1 — 🐛 `effective_power()` (antes: zero efeito de poder modelado).
3. `{T}`: Add any color — ✅ genérico (ramp/green_source_any).

## Radagast of Rhosgobel {2}{G}{G}
1. 1º creature spell do turno custa {2} menos — ✅ `effective_cost()`.
2. ...e pode ser conjurado com flash — 📝 sem instant-speed/janela de turno adversário modelada (documentado).

## Ram Through {1}{G}
1. Criatura sua causa dano = seu poder numa criatura do oponente (excesso c/ trample vai na cara) — ✅ tag "removal", `try_use_own_interaction()` (efeito numérico exato do combate é 📊, mas a conjuração conta como interação real).

## Reliquary Tower
1. Sem tamanho máximo de mão — ✅ `cleanup_hand_size()`.
2. `{T}`: Add C — ✅ genérico.

## Return of the Wildspeaker {4}{G}
1. Draw = maior poder entre criaturas não-Humanas — 🐛 `cast_spell()` (fórmula corrigida, era conflada com Shamanic Revelation).
2. Modo alternativo: +3/+3 não-Humanas até o fim do turno — 📝 buff temporário de combate (mesma família de Craterhoof).

## Roaming Throne {4}
1. Ward {2} — 📊 opponent_dependent.
2. Tipo escolhido (Bear) — ✅ `roaming_throne_active()`.
3. Gatilho de OUTRA criatura do tipo escolhido dispara 2x — ✅ `combat_step()` (Beorn) + `on_creature_enters()` (Ayula, 🐛 corrigido nesta rodada — antes só a Beorn dobrava).

## Scavenger Grounds
1. `{T}`: Add C — ✅ genérico.
2. `{2}, {T}, Sac Desert`: exile todos os cemitérios — 📝 opponent_dependent (exilar o PRÓPRIO cemitério é estritamente ruim pra esse deck sem alvo de oponente que valha, Regra 1).

## Selvala, Heart of the Wilds {1}{G}{G}
1. Outra criatura entra com poder maior que todas as outras: draw — ✅ `on_creature_enters()` (`max_power_seen`).
2. `{G}, {T}`: Add X mana (X=maior poder em campo) — 🐛 `total_mana()` (era tratada como dork genérico de 1 mana, agora usa `greatest_power_in_play()`).

## Shamanic Revelation {3}{G}{G}
1. Draw = número de criaturas controladas — ✅ `cast_spell()`.
2. Ferocious: ganha 4 vida por criatura poder>=4 — 📊 vida não rastreada neste modelo.

## Sol Ring {1}
1. `{T}`: Add CC — ✅ genérico (caso especial em `total_mana()`).

## Solemn Simulacrum {4}
1. ETB: busca básica pro campo tapped — ✅ `cast_spell()`.
2. Morre: pode draw — 📝 sem morte/remoção modelada pra esse corpo especificamente (nunca "morre" nesse sim, só fica em campo — consistente com o resto do arquivo, que não modela remoção de oponente).

## Song of the Dryads {2}{G}
1. Encantada vira Forest incolor — ✅ tag "removal", `try_use_own_interaction()`.

## Springleaf Parade {X}{G}{G}
1. ETB: cria X tokens Shapeshifter 1/1 changeling — ✅ `cast_spell()` (X=1, convenção do arquivo pra custo {X}).
2. Tokens-criatura têm `{T}: Add any color` — ✅ `total_mana()`/`green_sources()` (vale pra qualquer token-criatura, não só o próprio).

## The Great Henge {7}{G}{G}
1. Custo reduzido pelo maior poder em campo — ✅ `effective_cost()`.
2. `{T}`: Add GG, ganha 2 vida — ✅ `total_mana()` (vida 📊 não rastreada).
3. Criatura não-token entra: +1/+1 counter + draw — ✅ `on_creature_enters()`.

## Thought Vessel {2}
1. Sem tamanho máximo de mão — ✅ `cleanup_hand_size()`.
2. `{T}`: Add C — ✅ genérico.

## Three Visits {1}{G}
1. Busca Forest pro campo — ✅ `cast_spell()`.

## Tireless Provisioner {2}{G}
1. Landfall: Food ou Treasure — ✅ `on_land_enters()` (sempre Treasure, cracka na hora).

## Tireless Tracker {2}{G}
1. Landfall: investigate (Clue) — ✅ `on_land_enters()`.
2. Sacrifica Clue: +1/+1 counter — ✅ `try_crack_clues()`.

## Titania's Command {4}{G}{G}
1. Exile cemitério de um jogador + ganha vida — 📝 opponent_dependent, não escolhido pela heurística (vida 📊).
2. Busca até 2 terrenos tapped — ✅ `cast_spell()` (modo escolhido).
3. Cria 2 Bears 2/2 — ✅ `cast_spell()` (modo escolhido).
4. 2 contadores em cada criatura — 📝 modo não escolhido pela heurística (só busca terreno + Bears).

## Toski, Bearer of Secrets {3}{G}
1. Can't be countered — 📊 opponent_dependent.
2. Indestructible — 📊 combate/oponente.
3. Ataca todo combate se puder — 📊 já assumido implicitamente (toda criatura apta ataca).
4. Criatura causa dano de combate a jogador: draw — ✅ `combat_step()`.

## Tribute to the World Tree {G}{G}{G}
1. Criatura entra: draw se poder>=3, senão 2 contadores — ✅ `on_creature_enters()`.

## Unnatural Growth {1}{G}{G}{G}{G}
1. Início de cada combate: dobra poder/toughness até o fim do turno — 📝 buff temporário de combate, mesma família de Craterhoof/Goreclaw (contado como finisher via tag, sem número exato).

## War Room
1. `{T}`: Add C — ✅ genérico.
2. `{3}, {T}, pague vida=cores da identidade`: draw — ✅ `try_war_room()` (vida 📊 não rastreada, custo de mana real).

## Yavimaya, Cradle of Growth
1. Todo terreno é Forest adicionalmente — ✅ `is_forest_for_landfall()`, `green_sources()`.

---

## Resumo numérico

- **69 cartas** (comandante + 68 do deck, excluindo as 31 Forest básicas).
- **~120 linhas de cláusula** cobertas nesta tabela.
- **✅ Implementado:** ~85 linhas.
- **📊 N/A estrutural:** ~24 linhas (combate, vida não rastreada, oponente).
- **📝 Documentado, fora de escopo:** ~11 linhas (buffs temporários de
  combate não rastreados por criatura, modos de spell não escolhidos pela
  heurística, opponent_dependent sem alvo modelável).
- **🐛 Corrigido nesta rodada (2026-09-01):** Selvala (mana real),
  Return of the Wildspeaker (fórmula), Obscuring Haze (custo alternativo
  grátis), Lightning Greaves (nunca equipada), Allosaurus Shepherd (pump
  100% ausente), Chronicle of Victory/Patchwork Banner (anthems sem
  efeito de poder), Roaming Throne (só dobrava a Beorn, não a Ayula).

Nenhuma cláusula ficou sem uma linha nesta tabela. Se algo aqui estiver
errado, o local citado (`nome_da_funcao()`) é onde conferir.

---

## 🐛 Correção — conversão de Bear pela Beorn nunca era persistente (2026-09-02)

**Gatilho:** pergunta direta do usuário — *"Vc considerou que com o Beorn
ele transforma as demais cartas em campo em urso, uma por turno,
ampliando o escopo de efeito do Roaming Throne?"*

Oráculo real de Beorn the Fierce (Scryfall, reconfirmado nesta rodada):
*"At the beginning of combat on your turn, put a trample counter on up
to one target creature you control. **It becomes a Bear in addition to
its other types.** Then if you control three or more Bears, draw two
cards."* A cláusula "becomes a Bear" é uma **mudança de tipo
permanente** (não "until end of turn") — a rodada de 2026-09-01 já tinha
implementado o gatilho de combate (linha `Beorn combat` na tabela acima,
marcada ✅), mas a resposta ao usuário revelou que essa implementação
tinha um bug real: `state.bear_count` era só um contador abstrato
incrementado a cada combate — a criatura-alvo NUNCA era marcada de forma
persistente em nenhum lugar que `is_bear()` checasse depois.

**2 consequências reais perdidas, confirmadas lendo o código:**
1. **Anthems não se aplicavam.** `effective_power()` (a função que soma
   os 3 anthems reais de Bear — Beorn +2/+2, Chronicle of Victory +2/+2,
   Patchwork Banner +1/+1) chama `is_bear(state, card)` internamente. Uma
   criatura convertida nunca passava nessa checagem, então nunca recebia
   os bônus de poder aos quais passou a ter direito.
2. **A mesma criatura era "reconvertida" todo combate.** `creatures_not_bear`
   era recalculado via `is_bear()`, que nunca reconhecia conversões
   anteriores — então o alvo de maior MV era selecionado (e
   "reconvertido") indefinidamente, turno após turno, em vez de cada
   combate converter uma criatura NOVA (o que a carta realmente faz: até
   UMA criatura por combate, esgotando o pool real de alvos elegíveis).
   Isso também é exatamente o mecanismo que expande o escopo do Roaming
   Throne perguntado pelo usuário — mais criaturas reais viram Bear ao
   longo do jogo, então mais delas se beneficiam de qualquer sinergia de
   Bear (incluindo os gatilhos que o Roaming Throne dobra).

**Corrigido:**
- Novo campo `state.converted_to_bear: set` — rastreia de verdade quais
  criaturas foram convertidas pela Beorn, persistente pro resto da
  partida.
- `is_bear()` agora também consulta esse conjunto.
- O campo antigo `bear_count` (nunca decrementado quando um Bear saía de
  campo — Sakura-Tribe Elder, sacrifício do Wildwood Rebirth, Managorger
  Hydra removido — outra fonte de staleness achada ao investigar)
  substituído por `bears_in_play()`, calculado ao vivo a partir do
  battlefield real a cada checagem, eliminando as duas classes de bug de
  uma vez.

Validado com 5 testes unitários isolados (conversão persiste em
`is_bear()`; criatura convertida ganha o anthem real da Beorn; cada
combate converte uma criatura NOVA, não a mesma; `bears_in_play()`
recalcula corretamente quando um Bear sai de campo; Roaming Throne dobra
a conversão pra 2 criaturas no mesmo combate) + regressão de 20.000
partidas (seed 9500000+, turns=10, 0 exceções) + `run_batch` antes/depois
via `importlib` (3000 jogos, seed 10000000, turns=10):

| Métrica | Antes | Depois |
|---|---|---|
| Bear count final (avg) | 14.74 | 15.27 |
| Beorn "draw 2" triggers (3+ Bears) | 4.82 | 5.32 |
| Beorn combat triggers (converteu em Bear) | 5.03 | 4.36 |
| Avg compras extras (draw) | 37.73 | 40.25 |
| Avg spells conjurados | 19.31 | 19.80 |

Os "combat triggers" caem (5.03→4.36) porque agora o pool de alvos
elegíveis se esgota de verdade conforme criaturas reais viram Bear —
comportamento correto (antes o gatilho nunca "secava", convertendo a
mesma criatura pra sempre). Apesar de menos triggers, o "Bear count
final" e os draws sobem, porque agora cada conversão é real e
permanente, alimentando os anthems e o gatilho de 3+ Bears de forma
consistente com o board de verdade, em vez de um contador desconectado.
