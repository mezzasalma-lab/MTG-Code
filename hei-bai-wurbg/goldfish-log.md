# Goldfish Log — Hei-Bai, Forest Guardian

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Teste #1 — Farewell vs. Aura Shards (`heibai_aurashards_test.py`) — 2026-08-24

Pedido do usuário: trocar Farewell POR Aura Shards (não só adicionar) e
comparar os dois decks resultantes. Aura Shards (`{1}{G}{W}`, Enchantment):
"Whenever a creature you control enters, you may destroy target artifact
or enchantment."

**Nota de Bracket:** Farewell e Aura Shards são AMBAS Game Changers reais
(confirmado ao vivo contra `is:gamechanger`) — essa troca especificamente
(uma por outra) MANTÉM o deck em 3/3 Game Changers, continua no teto do
Bracket 3. Isso é diferente de simplesmente adicionar Aura Shards por cima
da lista atual, que empurraria pra 4/4 e Bracket 4 automaticamente.

Implementada em `CARD_DB` sem "another" no gatilho (dispara até na
própria criatura entrando, diferente do Purphoros) — sem oponente real,
tratada como interação proxy disparada por todo ETB de criatura,
acumulada numa métrica dedicada (`aura_shards_destroys_total`) separada
do total genérico de interação.

**Metodologia:** monkeypatch temporário de `BASE_LIBRARY`, mesmas seeds
nas duas variantes.

**n=3000, seed_base=4400000, mesmas seeds — resultado:**

```
                                              COM Farewell   COM Aura Shards   delta
Turno medio de conjuracao da Hei Bai              3,760          3,768        +0,007
Nunca conjurada em 8 turnos                       2,47%          2,50%        +0,03pp
Avg Shrines em campo (fim)                        4,581          4,587        +0,006
Avg cartas compradas extra                        9,567          9,627        +0,059
Avg tokens criados                                7,701          7,670        -0,031
Avg spells de interacao (proxy, total)             2,563          6,333       +3,770
Avg destruicoes via Aura Shards                    0,000          3,833       +3,833
```

**Checagem de ruído:** troquei o `seed_base` 2 vezes (1M/2M) — a métrica
central (destruições via Aura Shards) ficou estável em 3,39-4,00 por
partida, e o delta de "nunca conjurada" ficou pequeno e sem sinal
consistente (-0,27pp / -0,10pp) nas duas rodadas extras — dentro do
ruído normal de um swap de 1 carta, não um efeito real na comandante.

**Leitura honesta:** a troca é isolada de verdade — turno de comandante,
contagem de Shrines, draw e tokens praticamente não mudam (tudo dentro do
ruído de reamostragem), confirmando que Aura Shards não compete por
recursos com o motor central do deck, só adiciona em cima. O ganho real e
mensurável: **Aura Shards dispara em média 3,83 vezes por partida em 8
turnos** — mais que triplicando o volume total de interação do deck
(2,56 → 6,33 eventos de interação proxy por partida) — contra o único uso
de Farewell (sorcery, sem gatilho repetível). Isso confirma numericamente
por que a carta é classificada como Game Changer: o deck já cria token de
criatura o tempo todo (Honden of Life's Web, Go-Shintai of Shared Purpose,
Crescent Island Temple, o próprio ativado da Hei Bai, Hallowed Haunting a
cada encantamento conjurado), e cada um vira uma chance grátis de destruir
artefato/encantamento do oponente.

**Conclusão:** mecanicamente é um upgrade real e significativo em volume
de interação repetível, com custo de oportunidade quase zero sobre o
resto do deck (a troca não desacelera nada que já estava funcionando). A
decisão real não é sobre poder — é sobre Bracket: essa troca específica
(1-por-1) mantém o teto de 3 Game Changers, então não muda a classificação
oficial do deck. Se o grupo já aceita Farewell como um dos 3 GCs do deck,
não há motivo mecânico pra recusar essa troca.

**Troca aplicada de verdade em `lista.md` (2026-08-24)** — Farewell saiu,
Aura Shards entrou. `heibai_v1_runs.jsonl` foi regerado com a lista nova
(reteste de robustez: 20.000 partidas, 0 erros/timeouts). A Simulação #1
abaixo já reflete o deck ATUAL (com Aura Shards, não Farewell) — os
números batem com a coluna "COM Aura Shards" do teste acima, dentro do
esperado pra seeds diferentes.

---

## Simulação #1 — goldfish Python completo (`heibai_goldfish_v1.py`) — 2026-08-24

**Script construído do zero.** A `auditoria.md` já tinha uma boa categorização
das 17 Shrines, mas não um catálogo carta-a-carta de todo gatilho real —
varredura mecânica completa feita aqui pela primeira vez (94 cartas
únicas, ver `/tmp/heibai_full.txt` gerado durante o processo).

**Motor central implementado com fidelidade real:** cada Shrine tem, em
geral, DOIS gatilhos distintos — um "when THIS Shrine enters" (X = Shrines
controladas naquele momento) e um "whenever ANOTHER Shrine you control
enters" (efeito fixo de 1 unidade, disparado por toda Shrine já em campo).
Implementado via `shrine_enters()`, dispatch central chamado toda vez que
QUALQUER Shrine entra — nomeada, token (inclusive os tokens-Shrine
criados por Go-Shintai of Life's Origin), ou **reentrada via blink**.

**Três dobradores de gatilho distintos, implementados sem confundir um
com o outro** (a diferença real importa e muda o resultado):
- **Elesh Norn** — incondicional, cobre QUALQUER gatilho causado por algo
  entrando (Shrine ETB, reação de outra Shrine, e também o gatilho da
  Purphoros — que dispara quando OUTRA criatura entra, também "causado
  por permanente entrando").
- **Sanctum of All** — condicional (6+ Shrines), escopado só a "outra
  Shrine" (não pega Purphoros), mas cobre tanto ETB quanto as habilidades
  pagas de end step dos Go-Shintai (que também são "triggered ability of
  another Shrine").
- **Annie Joins Up** — nem ETB nem Shrine, é sobre a fonte ser uma
  criatura LENDÁRIA: cobre o ETB da própria Hei Bai, os 5 Go-Shintai, e o
  gatilho de conjuração da Sythis (que é `Legendary Enchantment Creature`,
  ao contrário de Argothian Enchantress/Enchantress's Presence — essas
  duas nunca são dobradas por nada neste deck).

As três empilham de forma independente quando aplicáveis simultaneamente,
via `resolve_times()` — testado manualmente com Elesh Norn + Sanctum of
All + 6 Shrines: um "when this enters" de Shrine dispara 3 vezes.

**Motor de blink implementado com efeito real** (não decorativo): repiscar
uma Shrine já em campo dispara o "when THIS enters" dela de novo — uma
entrada nova de verdade, não a reação "another Shrine enters". Deadeye
Navigator (soulbond + `{1}{U}` repetível), Ephemerate (com rebound = 2
usos reais), Thassa/Teleportation Circle/Mind Stone harnessed (end step),
Waterbender's Restoration — todos escolhem greedy a Shrine de maior valor
disponível (`best_shrine_to_reblink()`).

**Bug real encontrado e corrigido no smoke-test:** a primeira versão do
ETB da própria Hei Bai ("reveal until Shrine... **then shuffle**") mandava
as cartas reveladas que não eram Shrine pro cemitério — mas o oráculo real
diz "then shuffle", não "then discard"/"then mill". Corrigido pra devolver
essas cartas à biblioteca (sem RNG real de reembaralhar, mesma convenção
já usada nesta biblioteca pra qualquer "search... then shuffle" —
devolvidas deterministicamente, documentado). O bug também tinha uma
condição de loop frágil (`reveal_count < len(state.library)` comparando
contra um comprimento que encolhia a cada iteração), reescrita como um
`while state.library:` limpo.

**Teste de robustez:** 2 sweeps de 20.000 partidas com timeout de 2s via
`signal.alarm`, **0 erros, 0 timeouts** nos dois.

**n=3000, seed_base=9100000, 8 turnos — resultado oficial (versão original, com Farewell):**

```
Avg mulligans: 0,58
Turno medio de conjuracao da Hei Bai: 3,79 | mediana: 4,0
Nunca conjurada em 8 turnos: 3,0%
Avg contagem de Shrines em campo (fim de jogo): 4,54
Avg cartas compradas extra: 8,90
Avg drain proxy total: 8,78
Avg dano proxy total (Purphoros/Go-Shintai Ancient Wars): 9,67
Avg tokens criados: 7,67
Avg dobras via Elesh Norn: 1,45
Avg dobras via Sanctum of All (6+ Shrines): 2,63
Avg dobras via Annie Joins Up: 0,34
Avg blinks totais: 1,06 | dos quais em Shrine: 0,79
Avg tutores usados: 0,85
Avg vida ganha proxy: 1,97
Avg spells de interacao conjurados (proxy): 2,53
Avg mao final: 3,17
```

**Atualizado em 2026-08-24 após a troca Farewell → Aura Shards (mesma
seed_base=9100000, reteste de robustez limpo — 20.000 partidas, 0
erros/timeouts):**

```
Avg mulligans: 0,58
Turno medio de conjuracao da Hei Bai: 3,79 | mediana: 4,0
Nunca conjurada em 8 turnos: 3,1%
Avg contagem de Shrines em campo (fim de jogo): 4,46
Avg cartas compradas extra: 8,84
Avg drain proxy total: 8,44
Avg dano proxy total (Purphoros/Go-Shintai Ancient Wars): 10,82
Avg tokens criados: 7,51
Avg dobras via Elesh Norn: 2,87
Avg dobras via Sanctum of All (6+ Shrines): 2,38
Avg dobras via Annie Joins Up: 0,36
Avg blinks totais: 1,06 | dos quais em Shrine: 0,78
Avg tutores usados: 0,85
Avg vida ganha proxy: 2,08
Avg spells de interacao conjurados (proxy): 6,14
Avg destruicoes via Aura Shards: 3,67
Avg mao final: 3,14
```

Tudo dentro do esperado do Teste #1 acima — motor central intacto, volume
de interação mais que dobrou (2,53→6,14/partida). `heibai_v1_runs.jsonl`
reflete esta versão atualizada.

Resultados salvos em `heibai_v1_runs.jsonl` (3000 jogos).

**Leituras principais:**

- **A comandante em si é a mais confiável desta biblioteca até agora**
  (turno médio 3,79, só 3,0% nunca conjurada em 8 turnos) — CMC 4 baixo +
  14 peças de rampa + o próprio ETB da Hei Bai não depende de ter mana
  sobrando pra funcionar, é parte do próprio cast.
- **O achado da auditoria ("motor de draw mais forte desta biblioteca")
  se confirma numericamente**: 8,90 cartas extra em média — mais que o
  dobro do próximo melhor motor de draw já medido nesta biblioteca
  (Nekusar, com wheels dedicados).
- **Os dois dobradores de Shrine (Elesh Norn + Sanctum of All) realmente
  compõem**: 1,45 + 2,63 = mais de 4 eventos de dobra por partida em
  média, confirmando que o achado da auditoria (Sanctum of All como
  multiplicador extra, corrigido em 24/08) não era só teórico — acontece
  de verdade em boa parte das partidas.
- **O motor de blink entrega valor real mas modesto** (0,79 reentradas de
  Shrine em média) — a maioria das fontes de blink (Thassa, Teleportation
  Circle, Mind Stone) só ativa 1x por turno no end step e compete entre si
  pelo mesmo alvo prioritário, então o ganho não escala tão rápido quanto
  o motor de Shrine-ETB em si.

**Simplificações documentadas no docstring do script** (não inventadas —
omissões explícitas): modelo de mana genérico/total; devoção a
vermelho/azul (Purphoros/Thassa) não rastreada (nenhuma das duas depende
disso pra sua habilidade disparada/ativada funcionar); Skybind implementado
com valor modesto (nenhuma criatura não-Shrine deste deck tem ETB de peso
pra repiscar com ele); Weaver of Harmony só o buff estático (a habilidade
de copiar gatilho/ativada de fonte de encantamento não é modelada,
genérica demais pra um efeito determinístico); Destiny Spinner só o
"can't be countered"; Sanctum Weaver e Bloom Tender com mana aproximada
(não pip-a-pip); removal/contramágica proxy sem alvo real, mesma convenção
dos outros 9 simuladores desta biblioteca.

---

## Correção #1 — revisão completa (pedido do usuário: "deve ter muitos erros semelhantes" ao Ur-Dragon)

Usuário pediu a mesma revisão rigorosa aplicada ao Ur-Dragon. Gerado o
oráculo real completo (sem truncar) das 94 cartas da lista, cruzado
carta a carta com o CARD_DB. Achados reais (confirmado: sim, muitos
erros semelhantes):

### Corrigido

1. **Displacer Kitten — 100% não implementada.** "Whenever you cast a
   noncreature spell, exile up to one target nonland permanent you
   control, then return it." Dispara em quase tudo neste deck (Shrines
   são encantamentos = noncreature spell). Implementado em `cast_card()`.
2. **Enduring Vitality — 100% não implementada.** "Creatures you control
   have '{T}: Add one mana of any color.'" Concede habilidade de mana a
   TODAS as criaturas em campo (menos as que já têm uma própria, pra não
   dobrar). Implementado em `dork_mana()`.
3. **A própria Hei Bai tinha uma segunda habilidade nunca implementada.**
   "{W}{U}{B}{R}{G}, {T}: For each legendary enchantment you control,
   create a 1/1 colorless Spirit creature token..." — 5 mana + tap,
   repetível 1x/turno. Implementado (`do_hei_bai_activated`), com gate de
   doença de invocação (turno de conjuração < turno atual).
4. **Ephemerate estava 100% morta**, apesar do docstring do arquivo
   afirmar o contrário — a tag `blink_rebound` nunca era checada em
   lugar nenhum: nem o blink imediato do cast, nem o rebound (que
   dependia de uma flag `ephemerate_rebound_pending` que nunca era
   setada). Corrigido, e movida a checagem do rebound de `end_step()`
   pra `upkeep_step()` (turno errado dentro do próprio ciclo — "next
   upkeep", não "this end step").
5. **Motor de blink inteiro com bug sistêmico de alvo ilegal.**
   `best_shrine_to_reblink()` (prioriza as 4 Shrines puramente
   encantamento — Spirit Oasis/Kyoshi/Northern Air Temple/Crescent
   Island Temple) era usada indiscriminadamente por TODOS os motores de
   blink, mas cada um tem restrição REAL diferente: Deadeye
   Navigator/Ephemerate/Waterbender's Restoration/Thassa exigem "target
   CREATURE" (só os 5 Go-Shintai são criatura entre as Shrines — e só
   Go-Shintai of Life's Origin tem ETB self de valor real); Teleportation
   Circle exige "artifact or creature"; The Mind Stone (harnessed) é o
   ÚNICO que alcança "any nonland permanent" (as 12 Shrines puras
   inclusas). Corrigido com 4 funções de alvo separadas por legalidade
   real (`best_creature_to_reblink`, `best_nonland_permanent_to_reblink`,
   `best_nonenchantment_permanent_to_reblink`, mantendo
   `best_shrine_to_reblink` só pro Mind Stone).
6. **Skybind com pool de alvo duplamente errado.** Oráculo real: "exile
   target NONENCHANTMENT permanent" — exclui TODAS as 17 Shrines
   (encantamentos). O filtro anterior (`n not in ("token",)`) comparava
   o NOME da carta com a string literal `"token"` — nunca batia com
   nada de verdade, então nunca excluía token nenhum de fato, E ainda
   incluía Go-Shintai (Shrine-criatura, alvo ilegal) na lista. Corrigido
   com `best_nonenchantment_permanent_to_reblink` (só terrenos,
   artefatos e criaturas PURAS — Purphoros/Aura Shards precisam estar em
   campo pra justificar o alvo, já que criaturas puras deste deck não
   têm ETB próprio de peso).
7. **Nenhum terreno jamais entrava tapped** (mesma classe de bug do
   Ur-Dragon). Indatha Triome e Ketria Triome têm "This land enters
   tapped." incondicional. Corrigido com `tapped_lands_this_turn`
   (contador, não terreno único — Kyoshi Island Plaza pode buscar vários
   terrenos tapped na mesma entrada, escalando com Shrine count).
8. **Os tutores de terreno verde (Farseek, Nature's Lore, Three Visits,
   Cultivate, Aang's Journey) pegavam qualquer terreno da biblioteca,
   sem checar tipo real nem o "tapped" que cada um exige.** Corrigido
   com `search_land()` (mesmo padrão do Ur-Dragon) — Farseek sempre
   tapped, Cultivate só básica de verdade + 1 tapped no campo + 1 pra
   mão (era ambas pro campo antes), Aang's Journey só básica pra mão.
9. **Bloom Tender fixa em 1 mana flat** — oráculo real: "For each color
   among permanents you control, add one mana of that color" (escala
   com cores distintas em campo, não aproximado). Corrigido com
   `bloom_tender_colors()` (cor real de cada permanente, via Scryfall).
10. **Sanctum Weaver com fórmula errada** (`enchantment_count // 2`,
    documentada como "aproximação conservadora" quando na real era só um
    erro de fórmula) — oráculo real: "Add X mana... where X is the
    number of enchantments you control", sem divisão. Corrigido pro
    valor exato.
11. **Northern Air Temple e Sanctum of Stone Fangs só drenavam, sem
    ganhar a vida** que o próprio oráculo concede junto ("each opponent
    loses X life AND you gain X life"). Corrigido.
12. **Shrine Token registrada com ctype errado** ("creature" em vez de
    "enchantment_creature" — ela é uma cópia real de Shrine, "1/1
    colorless Shrine enchantment creature token"). Isso a deixava
    incorretamente elegível como alvo de efeitos "nonenchantment"
    (Skybind) e não-contada em `is_enchantment_card()`. Corrigido.
13. **Cartas 'interaction' (remoção/contramágica/proteção) eram
    conjuradas às cegas pela IA gulosa**, sem alvo real, desperdiçando
    carta e mana — mesma classe de bug corrigida no Ur-Dragon (Correção
    #13). Excluídas do loop de auto-cast, com uma exceção: **Annie Joins
    Up** também é tageada 'interaction' (ETB de 5 dano, proxy) mas seu
    dobrador estático de gatilho de criatura lendária é real e modelado
    — excluí-la jogaria fora valor de verdade que ela entrega.

Testado: 300 jogos smoke test, 30.000 jogos de robustez (0 erros).

### Deferido (achado, documentado, não implementado)

- Fetch lands não são "cracked" de verdade (ficam como si mesmas em
  campo) — ao contrário do Ur-Dragon, aqui o modelo de mana é 100%
  genérico (sem cor), então qual terreno especificamente é buscado não
  muda a contagem de mana total — baixa prioridade real neste deck
  especificamente (diferente do Ur-Dragon, onde importava muito).
- Sanctum of Shattered Heights (habilidade ativada, paga {1} + descarte)
  só ativa 1x por turno no código — o oráculo permite múltiplas
  ativações se houver mana/cartas — mas é uma habilidade de remoção
  (proxy, sem efeito no nosso lado), então a diferença não muda o board
  próprio, só o contador de "interação usada".
- Weaver of Harmony (copiar gatilho/ativada), Destiny Spinner (terreno
  vira criatura), Sphere of Safety (taxa ataques do oponente) — já
  documentados como fora de escopo antes desta revisão, confirmados
  ainda corretos (genuinamente não-modeláveis ou baixo valor
  determinístico).

### Impacto real (mesma seed_base=9100000, n=3000)

| métrica | antes | depois |
|---|---|---|
| nunca conjurada | 3,1% | 2,9% |
| dano proxy total | 10,82 | **195,95 (+18x)** |
| tokens criados | 7,51 | **59,10 (+7,9x)** |
| dobras via Elesh Norn | 2,87 | **89,87 (+31x)** |
| blinks totais (dos quais em Shrine) | 1,06 (0,78) | **2,54 (1,76)** |
| destruições via Aura Shards | 3,67 | **91,30 (+25x)** |
| vida ganha proxy | (não existia) | 37,75 |

Salto grande e real, não inflação — a maior parte vem de mecânicas que
estavam **completamente ausentes** (Displacer Kitten, Enduring Vitality,
Ephemerate, a habilidade da própria Hei Bai), não de ajuste fino. Esse
deck estava sendo medido, a sessão toda desde 24/08, como um motor de
valor muito mais fraco do que a lista realmente é — o padrão se repete
do Ur-Dragon.

`lista.md` não mudou. `heibai_v1_runs.jsonl` sobrescrito.

---

## Correção #2 — Purphoros e Thassa também são lendárias (usuário perguntou direto)

Usuário: *"Conferiu o blink da Thassa e o ping do Purphoros tb?"*

Reconferindo os dois com o oráculo real: **Purphoros, God of the Forge**
e **Thassa, Deep-Dwelling** são ambas `Legendary Enchantment Creature —
God` (Scryfall). O conjunto `LEGENDARY_CREATURES` (usado por
`resolve_times()` pra saber se o dobrador da Annie Joins Up se aplica)
não incluía nenhuma das duas — 2 bugs reais:

1. **Ping da Purphoros** ("whenever another creature you control enters,
   deals 2 damage") — o 4º argumento de `resolve_times()` estava
   hardcoded `False`. Como a FONTE do gatilho (Purphoros) é lendária, a
   Annie deveria dobrar esse ping — nunca dobrava.
2. **Blink de end step da Thassa** ("at the beginning of your end step,
   exile up to one other target creature...") — nem passava por
   `resolve_times()` — o blink acontecia direto, sem checar dobra
   nenhuma (nem da Annie, a única que se aplicaria aqui, já que não é
   ETB-causado nem Shrine-triggered).

Corrigido: `Purphoros, God of the Forge` e `Thassa, Deep-Dwelling`
adicionadas a `LEGENDARY_CREATURES`; ping da Purphoros passa `True` pro
4º argumento; blink da Thassa agora passa por `resolve_times()` antes de
executar (looping o blink pelo número de vezes resolvido, re-escolhendo
o melhor alvo a cada iteração — pode mudar depois da 1ª, já que um blink
em Go-Shintai of Life's Origin cria mais uma Shrine).

Testado: 300 jogos smoke test, 30.000 jogos de robustez (0 erros).

**Impacto real** (mesma seed_base=9100000, n=3000):

| métrica | antes | depois |
|---|---|---|
| dobras via Annie Joins Up | 2,49 | **51,17 (+20x)** |
| dano proxy total | 195,95 | **307,55 (+57%)** |
| tokens criados | 59,10 | 62,14 |
| blinks totais (dos quais em Shrine) | 2,54 (1,76) | 2,67 (1,88) |

O achado da Annie Joins Up era real e grande — ela estava presente no
CARD_DB desde o início mas só dobrava os Go-Shintai e a própria Hei Bai,
nunca Purphoros/Thassa, apesar de ambas serem lendárias de verdade.

`lista.md` não mudou. `heibai_v1_runs.jsonl` sobrescrito.

---

## Correção #3 — revisão carta-a-carta/interação-a-interação (pedido explícito do usuário)

Usuário: *"Eu quero que vc reconfira o deck todo, carta por carta e
interação por interação. Vários dos encantamentos shrine são lendários
tb!"* — depois, em sequência, perguntas pontuais: *"E as dobras do
Sanctum of all se tiver mais de 6 shrines na mesa (inclusive os tokens
do Go-Shintai of Life Origin)? E a Enchantress presence não triggar
quando Hei-Bai coloca shrine na mesa (não é cast)?"* e *"E Sythis
triggar 2X com Annie Joins Up? Outros lendários?"*

### Verificado com teste real (já estava correto, sem bug)

- **Sanctum of All conta Shrine Tokens no threshold de 6+.** Testado:
  5 Shrines nomeadas + 1 Shrine Token = `shrine_count()` retorna 6 e o
  dobrador ativa (`times=2`); com só 5 nomeadas, `times=1`.
  `shrine_count()` conta qualquer permanente com a tag `shrine`, token
  incluso — já correto.
- **Enchantress's Presence não dispara pro ETB da Hei Bai colocando
  Shrine em campo.** Testado: `cards_drawn_extra` fica em 0 antes e
  depois da Hei Bai encontrar e colocar uma Shrine via seu próprio ETB
  — `enter_battlefield()` (usado por "put onto the battlefield") nunca
  chama `on_cast_enchantment()`, só `cast_card()` chama (conjurar de
  verdade). Já correto.
- **Sythis dobra 2x com Annie Joins Up.** Testado: 2 vida + 2 compras
  com Annie em campo vs. 1/1 sem ela.
- **Go-Shintai of Ancient Wars dobra 2x com Annie.** Testado: 4 dano
  (2 Shrines × 2 dobra) vs. 2 sem Annie.
- **Go-Shintai of Life's Origin dobra 2x com Annie.** Testado: 2 Shrine
  Tokens criados vs. 1 sem Annie.

### Corrigido (achados reais novos)

1. **O próprio ETB da Hei Bai nunca passava por `resolve_times()`** —
   "When Hei Bai enters, reveal... until Shrine... put onto the
   battlefield" é um gatilho da PRÓPRIA Hei Bai (causado por ela mesma
   entrando). Elesh Norn (causado por ETB) e Annie Joins Up (Hei Bai é
   lendária) podiam dobrar isso, mas o código nunca checava. Corrigido
   e testado: com Annie em campo, a Hei Bai agora encontra 2 Shrines em
   vez de 1.
2. **Nenhum dork deste deck respeitava doença de invocação.** Birds of
   Paradise, Bloom Tender, Sanctum Weaver (e agora Enduring Vitality)
   produziam mana no MESMO turno em que eram conjurados, sem haste
   real. Corrigido com `state.creature_cast_turn` — as 3 cartas
   nomeadas (singleton, sem ambiguidade de instância) checam prontidão
   real; tokens (nome compartilhado entre várias instâncias no
   battlefield-como-lista) ficam de fora dessa checagem específica —
   aproximação conservadora documentada, o erro daí é limitado a 1
   turno por token, não o jogo inteiro como era o bug das 3 nomeadas.

Testado: 300 jogos smoke test, 30.000 jogos de robustez (0 erros) após
cada uma das 2 correções.

**Impacto real** (mesma seed_base=9100000, n=3000, as 2 correções
juntas — efeitos em direções opostas, doença de invocação REDUZ o
motor, ETB dobrável da Hei Bai AUMENTA um pouco):

| métrica | antes (Correção #2) | depois |
|---|---|---|
| dano proxy total | 307,55 | **178,74** |
| tokens criados | 62,14 | **40,72** |
| dobras via Elesh Norn | 99,75 | 57,35 |
| dobras via Annie Joins Up | 51,17 | 29,42 |
| Shrines em campo (fim) | — | 7,80 |

Líquido: queda real, porque restringir doença de invocação nos dorks é
uma correção mais impactante que o pequeno ganho do ETB dobrável da Hei
Bai — o motor de mana estava inflado desde o início por essa lacuna, e
agora reflete uma curva de desenvolvimento mais realista.

`lista.md` não mudou. `heibai_v1_runs.jsonl` sobrescrito.

---

## Correção #4 — perguntas pontuais sobre blink/tutor/free-cast (usuário conferindo carta por carta)

Usuário: *"VC considerou tb o rebound do Ephemerate?"* e, em seguida:
*"os efeitos de Aang's Journey, Deadeye Navigator, In search of
Greatness e Teleportation Circle estão corretos no simulador? E
Waterbender's restoration? Vc colocou no simulador o Harness do The
Mind Stone?"*

### Verificado com teste real (já estava correto, sem bug)

- **Rebound do Ephemerate.** Testado em 3 passos: blink imediato no
  cast, rebound real no upkeep seguinte (conjura de graça de novo, 2º
  blink), e nenhuma repetição no upkeep depois disso —
  `ephemerate_rebound_pending` é setada e consumida exatamente 1 vez.
  Único detalhe técnico de zero impacto: o Ephemerate vai pro graveyard
  no momento do cast (correto), mas nenhuma carta do deck interage com
  o conteúdo do graveyard de instant/sorcery, então isso não muda
  nenhuma métrica.
- **Deadeye Navigator.** `best_creature_to_reblink(state,
  exclude="Deadeye Navigator")` — soulbond real, não pode ter a si
  mesmo como alvo do próprio blink repetível. Já correto (fix de uma
  rodada anterior desta mesma sessão).
- **Teleportation Circle.** Alvo "artifact or creature" — como
  artefatos deste deck (Sol Ring/Signet/Mind Stone) não têm ETB de
  valor nenhum, `best_creature_to_reblink(state)` cobre o universo real
  de alvos com valor. Já correto.
- **Harness do The Mind Stone.** Está implementado: custo real de
  ativação é `{5}{W}` (6 mana total) — o código gasta 6 e seta
  `state.mind_stone_harnessed`, checado depois em `do_endstep_blinks()`
  como gate pro efeito de Harness. Simplificação aceita e documentada:
  a própria mana do Mind Stone não é excluída no turno em que ele é
  tapado pra pagar o custo de ativação (não existe rastreamento de tap
  por fonte individual em nenhum lugar deste simulador — nem Sol
  Ring/Arcane Signet são "esgotados" no turno em que pagam algo; é uma
  limitação arquitetural consistente, de impacto estreito, não vale um
  fix isolado só pro Mind Stone).

### Corrigido (achados reais novos)

1. **Kicker do Aang's Journey nunca era pago.** O código checava
   `remaining_mana(state) >= 2` pra liberar o bônus (tutor de Shrine),
   mas nunca chamava `spend_mana(state, 2)` — o kicker saía de graça.
   Corrigido.
2. **In Search of Greatness — 2 bugs.** (a) "greatest mana value among
   **OTHER** permanents you control" incluía a própria ISOG no cálculo
   de `highest_mv`, superestimando `target_mv` num board vazio/inicial
   (só ISOG em campo dava `target_mv=3` em vez do correto `1`) — na
   prática isso fazia a ISOG "acertar" um Shrine de 3 mana de graça
   logo cedo, com muito mais frequência do que deveria. (b) "you may
   **cast** a permanent spell... without paying its mana cost" é um
   cast de verdade (só sem pagar) — o código antigo ia direto pra
   `enter_battlefield()`, pulando `cast_card()` inteiro e perdendo os
   gatilhos de conjuração (Enchantress package se for encantamento,
   Displacer Kitten se for não-criatura). Corrigido: `cast_card()`
   ganhou um parâmetro `pay_cost: bool = True`, e ISOG agora chama
   `cast_card(state, pick, pay_cost=False)`. De quebra, o pool de
   candidatos agora exclui instant/sorcery da mão (a carta real é
   "permanent spell" apenas).
3. **Waterbender's Restoration resolvia o retorno na hora.** Oráculo
   real: "Exile X target creatures you control. Return those cards to
   the battlefield under their owner's control **at the beginning of
   the next end step**" — um retorno ADIADO, não um blink atômico. O
   código anterior chamava `blink_permanent()` direto no resolve do
   instant, dando o ETB (e a permanência em campo) imediatamente.
   Corrigido: agora exila e enfileira em
   `state.waterbenders_pending_return`, processado em `end_step()`
   (mesmo padrão do rebound do Ephemerate). Enquanto exilada, a
   criatura fica fora do campo pro resto do main phase — correto pelo
   oráculo, e também significa que ela não conta mais como fonte de
   mana/ETB pra outros spells conjurados depois dela no mesmo turno.

Testado: 300 jogos smoke test (0 erros), 25.000 jogos de robustez com
timeout de 2s/jogo via `signal.alarm` (0 erros, 0 timeouts).

**Impacto real** (mesma seed_base=9100000, n=3000, as 3 correções
juntas):

| métrica | antes (Correção #3) | depois |
|---|---|---|
| Shrines em campo (fim) | 7,80 | **6,84** |
| dano proxy total | 178,74 | **120,56** |
| drain proxy total | 23,60 | **18,78** |
| tokens criados | 40,72 | **31,21** |
| dobras via Elesh Norn | 57,35 | 38,65 |
| dobras via Sanctum of All | 14,86 | 11,10 |
| dobras via Annie Joins Up | 29,42 | 19,77 |
| blinks totais | 1,94 | 1,83 |
| tutores usados | 0,92 | 0,92 |
| vida ganha proxy | 27,57 | 22,52 |
| spells de interação (proxy) | 58,77 | 40,67 |
| destruições via Aura Shards | 57,61 | 39,55 |
| cartas compradas extra | 11,52 | 11,28 |

Líquido: queda real e proporcionalmente grande em quase toda métrica —
mas o driver principal é só o bug (2a) da In Search of Greatness. Antes
da correção, num board inicial (sem Shrine nenhuma ainda), o
`target_mv` inflado (3, por contar a própria ISOG) casava direto com
um Shrine de 3 mana na mão — ISOG "acertava" um Shrine de graça cedo
com bastante frequência. Corrigido pra `target_mv=1`, ela raramente
encontra alvo (poucos 1-drops sobram na mão depois que o main phase já
gastou os óbvios), e como o motor deste deck é multiplicativo (mais
Shrine → mais gatilho lendário → mais dobra → mais Shrine/token/dano),
perder aquele "Shrine fantasma" cedo se propaga e amplifica por 8
turnos. Os fixes do kicker do Aang's Journey e do timing do
Waterbender's Restoration reforçam a mesma direção (menos mana líquida
disponível / 1 permanente a menos disponível durante o main phase),
mas são contribuições bem menores.

`lista.md` não mudou. `heibai_v1_runs.jsonl` sobrescrito.

---

## Correção #5 — varredura das cartas ainda sem pergunta pontual (usuário: "Quero o foco nas próximas carta sim")

Depois da Correção #4, o usuário perguntou se o modelo já estava
"correto, preciso e coeso". A resposta honesta foi: sem bug conhecido,
mas várias cartas só tinham passado pela auditoria geral (Correção #1),
nunca por uma pergunta pontual — e o padrão da sessão inteira é que
pergunta pontual sempre achava bug que a auditoria geral não pegou.
Usuário: *"Quero o foco nas próximas carta sim."*

Auditadas contra o oráculo real (Scryfall) nesta rodada: as 12
Sanctums/Hondens/Temples ainda não conferidas (Crescent Island Temple,
Honden of Life's Web, Honden of Seeing Winds, Kyoshi Island Plaza,
Northern Air Temple, Sanctum of All, Sanctum of Calm Waters, Sanctum of
Fruitful Harvest, Sanctum of Shattered Heights, Sanctum of Stone Fangs,
Southern Air Temple, The Spirit Oasis), os 3 Go-Shintai restantes
(Hidden Cruelty, Lost Wisdom, Shared Purpose), Seedborn Muse, Dryad of
the Ilysian Grove, Argothian Enchantress, Weaver of Harmony, Sterling
Grove, Greater Auramancy, Hallowed Haunting, Herald of the Pantheon,
Elesh Norn, Annie Joins Up, Displacer Kitten, Sol Ring, Arcane Signet,
Idyllic Tutor, Replenish, Cultivate, Farseek, Nature's Lore, Three
Visits, Enduring Vitality — praticamente o resto da lista.

### Verificado correto (sem mudança)

- Todos os 12 Sanctums/Hondens/Temples: gatilho próprio de ETB (escala
  com contagem de Shrines no momento em que resolve, já incluindo a si
  mesma) vs. gatilho "whenever ANOTHER Shrine enters" (fixo, 1 por
  Shrine, separado corretamente em `SHRINE_SELF_ETB` vs.
  `SHRINE_OTHER_REACT`) — conferido contra o oráculo carta por carta,
  os dois gatilhos são realmente distintos no texto real e o código já
  os trata como duas abilities separadas.
- Sanctum of All: "search library and/or graveyard" modelado como busca
  única (biblioteca primeiro, cemitério como fallback) — bate com "a
  Shrine card" (singular) do oráculo; auto-exclusão do próprio dobrador
  (6+ Shrines) já confirmada em rodada anterior.
- Sterling Grove: `{1}, sacrifice: search... put on top` — conferido
  que o código insere no índice 0 da lista de biblioteca (`insert(0,
  ...)`) e que `draw_cards`/o resto do motor sempre puxam do índice 0
  (`pop(0)`) — "topo" é literalmente o próximo a ser comprado, timing
  certo.
- Go-Shintai of Hidden Cruelty/Lost Wisdom/Shared Purpose: gatilho
  pago de end step, cada um seu próprio `{1}` independente — batem com
  o oráculo; Hidden Cruelty (remoção) e Lost Wisdom (mill de oponente)
  corretamente tratados como proxy sem efeito no nosso board (mesma
  convenção de todo o pacote de remoção do deck).
- Deadeye Navigator, Thassa Deep-Dwelling, Teleportation Circle, The
  Mind Stone (Harness) — conferido que os 4 são blink ATÔMICO no
  oráculo real ("exile, then return", sem "next end step"), batendo
  com `blink_permanent()` direto. Nenhum precisa do mecanismo de
  retorno adiado.
- Dryad of the Ilysian Grove, Weaver of Harmony, Greater Auramancy,
  Sterling Grove (metade do shroud) — estáticos sem efeito numérico
  possível de capturar num modelo sem combate/sem oponente real, já
  documentados como fora de escopo.

### Corrigido (achado real novo)

1. **Skybind fazia blink atômico em vez de retorno adiado.** Oráculo
   real: "exile target nonenchantment permanent. Return that card to
   the battlefield... **at the beginning of the next end step**" — a
   MESMA classe de bug do Waterbender's Restoration (Correção #4), só
   que aqui passou despercebida porque aquela correção não foi conferir
   os outros efeitos de blink do deck. Como Skybind dispara em CADA
   encantamento que entra (Shrines inclusas — é frequente neste deck),
   o impacto é mais visível que o do Waterbender's. Corrigido
   reaproveitando o mesmo mecanismo: `state.pending_end_step_returns`
   (renomeado de `waterbenders_pending_return`, agora compartilhado
   pelas duas fontes), resolvido em `end_step()`.

### Documentado (não era bug, era lacuna de documentação)

- **Seedborn Muse** — a tag `untap_all` existia na `CARD_DB` mas nunca
  era checada em lugar nenhum do código. Investigado: o gatilho real
  ("untap all permanents... during EACH OTHER PLAYER'S untap step")
  não tem nenhuma janela pra disparar neste simulador, que só avança os
  PRÓPRIOS turnos (nunca simula untap step de oponente) — corpo 2/4
  vanilla é o resultado correto aqui, não um bug. Documentado
  explicitamente no cabeçalho do arquivo (antes era um buraco
  silencioso, sem nem estar na lista de simplificações).

Testado: 300 jogos smoke test (0 erros), 25.000 jogos de robustez com
timeout de 2s/jogo (0 erros, 0 timeouts).

**Impacto real** (mesma seed_base=9100000, n=3000, só o fix do
Skybind — as verificações "corretas" não mudam nada):

| métrica | antes (Correção #4) | depois |
|---|---|---|
| Shrines em campo (fim) | 6,84 | **6,74** |
| dano proxy total | 120,56 | **115,33** |
| dobras via Elesh Norn | 38,65 | 35,95 |
| dobras via Annie Joins Up | 19,77 | 18,98 |
| tokens criados | 31,21 | 30,30 |
| blinks totais | 1,83 | 1,75 |
| spells de interação (proxy) | 40,67 | 38,37 |
| destruições via Aura Shards | 39,55 | 37,26 |

Queda modesta e proporcional — bem menor que o salto da Correção #4,
porque o alvo legal do Skybind já era estreito (só criatura pura +
Purphoros/Aura Shards em campo), então o efeito de "ETB disponível 1
turno antes do correto" tinha valor limitado pra começo de conversa.
Ainda assim, real: qualquer permanente exilado pelo Skybind ficava
disponível como mana/ETB pros spells seguintes no MESMO main phase
antes da correção, o que não deveria acontecer.

`lista.md` não mudou. `heibai_v1_runs.jsonl` sobrescrito.

---

## Correção #6 — checklist obrigatória de mecânica (regra nova pós-Beorn)

**Gatilho (usuário):** depois de eu entregar o Beorn sem despacho de landfall
nenhum, o usuário pediu auditoria da mesma checklist (landfall, mana dorks,
mana rocks, fixing lands, draw engines, ramp engines, ativadas repetíveis,
combos) em **todos** os decks do repositório. Rodada dedicada a essa
checklist no Hei Bai (via agente de auditoria, comparando `oracle_text` real
de todo o `lista.md` contra o código).

**Landfall/dorks/rocks/fixing/draw/ramp:** todos verificados corretos ou N/A
(0 cartas qualificantes) — esse deck não tem nenhuma carta de landfall, os 4
mana dorks respeitam doença de invocação (já corrigido em rodada anterior
desta sessão), Sol Ring/Arcane Signet/Mind Stone corretos, e os 6 motores de
draw batem com o oráculo real.

**Bug real encontrado (ativadas repetíveis):** `do_deadeye_navigator()` e
`do_sanctum_shattered_heights()` ativavam **no máximo 1 vez por turno**, mas
nenhuma das duas cartas tem `{T}` no custo real — Deadeye Navigator
("{1}{U}: Exile this creature, then return it") e Sanctum of Shattered
Heights ("{1}, Discard a land or Shrine card:") são repetíveis enquanto
sobrar mana/recurso. Corrigido pra um loop real, com teto duro de 20
ativações/turno.

**Achado ao testar o loop:** sem o teto, o Deadeye Navigator trava o jogo
(timeout) num board com Sanctum Weaver + Go-Shintai of Life's Origin —
repiscar o Go-Shintai cria um Shrine Token, que aumenta `enchantment_count()`
e portanto a mana da Sanctum Weaver, então `remaining_mana()` nunca esvazia
(esse motor não rastreia "fonte já usada este turno" por permanente, só
recalcula `total_mana()` do zero a cada chamada). Teto de 20 ativações/turno
resolve sem descaracterizar o valor real da linha (generoso pra um goldfish
heurístico).

**Resultado (n=3000, seed_base=9100000, antes → depois):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg blinks totais | 1,75 | 2,17 |
| Avg spells de interação (proxy) | 38,37 | 51,69 |
| Avg drain proxy total | 18,21 | 21,93 |
| Avg dano proxy total | 115,33 | 157,14 |
| Avg tokens criados | 30,30 | 35,57 |
| Avg vida ganha proxy | 21,84 | 25,32 |

Impacto real e no sentido esperado — as duas cartas eram subutilizadas por um
fator de várias vezes. **Robustez:** sweep de 20.000 jogos (seeds
9100000–9119999, timeout 2s/jogo) rodado depois da correção do teto — 0
erros, 0 timeouts (o teste sem teto tinha ~65+ timeouts nos primeiros 5.500
seeds, confirmando que o loop travava de verdade, não só teoricamente).

`lista.md` não mudou. `heibai_v1_runs.jsonl` sobrescrito.

---

## Correção #7 — checklist ampliada (habilidades estáticas + métricas básicas)

**Gatilho (usuário):** *"Lembre da regra que criamos: TODA SIMULAÇÃO E DECK
TEM QUE TER TODAS AS Ativações, gatilhos, habilidades estáticas, combos e
métricas básicas (ramp, draw, interaction, finisher/lethality) contabilizados
e auditados SEMPRE!"* — 2 categorias novas na checklist. Hei Bai já tinha
passado pela checklist original de 8 categorias na Correção #6; esta rodada
focou nas 2 novas.

**Habilidades estáticas — conferido `oracle_text` de Sphere of Safety, Weaver
of Harmony, Destiny Spinner, Greater Auramancy, Sterling Grove, Enduring
Vitality, Elesh Norn contra o código:** todas já corretamente implementadas
ou corretamente fora de escopo. Único achado real: **Sphere of Safety**
(tag `"defense"` nunca despachada) tem oráculo puramente defensivo — *"Creatures
can't attack you... unless their controller pays {X}"* — sem nenhum efeito
no próprio board/mana/draw; este simulador não modela ataques de oponente
contra nós, então é fora de escopo de verdade (mesma razão do Seedborn Muse),
não um buraco silencioso — documentado explicitamente no docstring agora
(antes só a tag existia, sem explicação). Mesmo achado pra metade
"retorna como encantamento após morrer" de Enduring Vitality (nunca há
morte de criatura nomeada neste motor).

**Métricas básicas — novo bloco no `run_batch()`:** RAMP (novo contador
`ramp_pieces_cast`, nunca existia como métrica agregada — só entrava no
cálculo turno-a-turno de mana), DRAW (já existia via `cards_drawn_extra`,
agora rotulada explicitamente), INTERACTION (já existia via
`interaction_spells_cast_total`, agora rotulada e com nota de que é proxy
sem alvo real), FINISHER/LETHALITY (este deck não tem combo infinito, ao
contrário do Edgar Markov — documentado como tal, com o dano/drain agregado
reportado como proxy de pressão de jogo).

**Resultado:** puramente aditivo — nenhuma lógica de jogo mudou (só
contadores e o bloco de relatório novos). Confirmado com n=2000,
seed_base=6000000: `cards_drawn_extra`/`proxy_drain_total`/`proxy_damage_total`
idênticos byte a byte antes e depois (10,75 / 21,15 / 158,48 nas duas
rodadas). `ramp_pieces_cast` novo: avg 1,29 por partida.

**Robustez:** sweep de 20.000 jogos (seeds 900000–919999, timeout 2s/jogo) —
0 erros, 0 timeouts.

`lista.md` não mudou.

---

## Correção #8 — varredura exaustiva das 94 cartas (usuário: "desde que vc tenha avaliado TUDO dos 2 decks anteriores")

**Gatilho (usuário):** depois da Correção #7, o usuário pediu confirmação
explícita de que a auditoria tinha sido exaustiva, não uma checagem pontual.
Refeito: `oracle_text` de **todas as 94 cartas únicas** da lista extraído do
`scryfall-cache/oracle-cache.json` e comparado linha a linha contra o código
— toda linha de habilidade que NÃO começa com "Whenever"/"At the beginning"
(ou seja, ativadas, estáticas e ações especiais) foi conferida uma a uma.

**3 achados reais (100% ausentes em 7 rodadas de correção anteriores):**

1. **Go-Shintai of Life's Origin** tem uma SEGUNDA habilidade além da ETB já
   implementada: *"{W}{U}{B}{R}{G}, {T}: Return target enchantment card from
   your graveyard to the battlefield."* Nunca despachada. Implementado
   (`do_life_origin_reanimate`), respeitando doença de invocação (reusa
   `state.creature_cast_turn`, já rastreado genericamente pra toda criatura).
2. **Hall of Heliod's Generosity** — *"{1}{W}, {T}: Put target enchantment
   card from your graveyard on top of your library."* Só contava como
   terreno genérico fixo, essa segunda habilidade 100% ausente. Implementado
   (`do_hall_of_heliods_generosity`) com custo efetivo {1}{W}+1 (a mana que a
   própria land deixaria de produzir usando o {T} nesta ability em vez do
   tap normal pra mana) — mesmo padrão já usado pro Phyrexian Tower no
   simulador do Edgar Markov, pra não contar a mana da land 2x no turno.
3. **Abandoned Air Temple** — *"This land enters tapped unless you control a
   basic land."* Nunca era checado (só Indatha/Ketria Triome, tapped
   incondicional, estavam em `ETB_TAPPED_LANDS`). Corrigido em `play_land()`
   com checagem real do battlefield no momento do land-drop.

**Resultado (n=2000, seed_base=6000000, antes → depois):**

| Métrica | Antes (Correção #7) | Depois (Correção #8) |
|---|---|---|
| Avg cartas compradas extra | 10,75 | 10,71 |
| Avg dano proxy total | 158,48 | 161,01 |
| Avg blinks totais | 2,17 | 2,19 |
| Reanimações via Go-Shintai of Life's Origin | 0% (não existia) | avg 0,01/partida |
| Retornos via Hall of Heliod's Generosity | 0% (não existia) | avg 0,03/partida |

Impacto pequeno em todas as direções — as 2 ativadas novas raramente têm
alvo (cemitério de encantamento pouco populado, mesma razão já documentada
pra Replenish/Sanctum of All), e o Abandoned Air Temple tapado
condicionalmente puxa levemente pra baixo a mana disponível no turno em que
entra (esperado, some 1 turno de vantagem de mana num caso raro).

**Robustez:** sweep de 20.000 jogos (seeds 1300000–1319999, timeout 2s/jogo)
— 0 erros, 0 timeouts.

`lista.md` não mudou.

---

## Correção #9 — recursão vira 5ª métrica básica obrigatória (regra reforçada)

**Gatilho (usuário):** *"Vc precisa acrescentar a variável recursão e
interação à lista de variáveis para avaliar, medir e registrar em todos os
decks tb!"*

**Achado real ao implementar:** `tutors_used_total` misturava 2 categorias
diferentes no mesmo contador — o ramo de biblioteca do Sanctum of All
(*"search your library... for a Shrine card"* = tutor) e o ramo de
cemitério (*"and/or graveyard"* = recursão) incrementavam o MESMO campo.
Separado: `sanctum_of_all_graveyard_returns` (recursão) agora distinto de
`tutors_used_total` (só biblioteca). Também achado: **Replenish** ("return
all enchantment cards from your graveyard to the battlefield") nunca tinha
NENHUM contador — só o efeito, sem métrica nenhuma pra reportar.

**Ajustado no bloco `--- Metricas basicas ---` já existente (Correção #7):**
RECURSION (nova, 5ª categoria) = Replenish + Sanctum of All (ramo cemitério)
+ Go-Shintai of Life's Origin + Hall of Heliod's Generosity.

**Resultado:** puramente aditivo pro jogo em si (nenhuma lógica de
simulação mudou) — confirmado com n=2000, seed_base=6000000: `drain proxy
total`/`dano proxy total` idênticos aos já reportados na Correção #8
(21,19 / 161,01). `tutores usados` cai levemente (a fração que era do
Sanctum of All via cemitério migrou pra `sanctum_of_all_graveyard_returns`
— reclassificação de métrica, não mudança de comportamento). RECURSION novo:
avg 0,21/partida.

**Robustez:** sweep de 20.000 jogos (seeds 1400000–1419999, timeout 2s/jogo)
— 0 erros, 0 timeouts.

`lista.md` não mudou.

---

### Correção #10 — verificação de cartas multi-face (regra nova pós-Edgar Markov)

**Gatilho (usuário):** depois do achado de Ojer Taq/Legion's Landing no
Edgar Markov (jogadas ilegalmente como land — layout real "transform", não
"modal_dfc"), o usuário pediu pra conferir todas as cartas modais/
Adventure/Room/"Prepared"/dupla face dos dois decks trabalhados e registrar
a regra de verificar o `layout` real antes de assumir qual face é jogável.

**Conferido:** `grep -c "//" lista.md` = **0**. Hei Bai não tem nenhuma
carta com nome de face múltipla — categoria 11 da checklist (ver
`references/goldfish-sim-card-rules.md`) é **N/A por decklist**, não por
falta de verificação. Nenhuma mudança de código necessária.

---

### Correção #11 — verificação de planeswalkers (regra nova pós-Prismatic Bridge)

**Gatilho (usuário):** depois do Prismatic Bridge revelar que nenhum
simulador do repositório modelava lealdade/ativações de planeswalker, o
usuário registrou a regra permanente (categoria 12,
`goldfish-sim-card-rules.md`) — *"Adicione essa regra para tudo, sempre
também!"*

**Conferido:** `grep -in "Planeswalker" heibai_goldfish_v1.py` só encontra
a palavra dentro do texto do Sphere of Safety ("attack you or planeswalkers
you control"), não uma carta do tipo Planeswalker de verdade. Hei Bai não
tem nenhum planeswalker na lista — categoria 12 é **N/A por decklist**.
Nenhuma mudança de código necessária.

---

## Partida #1 — AAAA-MM-DD

- **Formato do teste:** goldfish / playtest com amigos / mesa competitiva
- **Mão inicial (mulligan até):**
- **Turno da primeira jogada relevante:**
- **Turno do primeiro ataque/combo:**
- **Curva de mana observada:**
- **Bombas/peças-chave puxadas:**
- **Removals sofridos/enviados:**
- **Resultado:** vitória / derrota / sem resolução
- **Turno de fim de jogo:**
- **O que funcionou bem:**
- **O que travou o deck:**
- **Ajustes a considerar:**

---

## Partida #2 — AAAA-MM-DD

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

### Leitura linha-a-linha completa do oráculo (mesma exigência do Toph/Beorn/Edgar Markov) — 2026-09-01

**Gatilho (usuário):** *"AGORA FAZ O QUE SEMPRE Te MANDei FAZER: COmpila
a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada carta tem que ser
lida linha a linha e isso tudo incorporado aos modelos que já fizemos até
agora"*.

Diferente do Beorn (7 gaps) e do Edgar Markov (4 gaps), a releitura
linha-a-linha de Hei Bai **não achou nenhum bug de comportamento novo**.
As 89 cartas (oráculo real via Scryfall, `checklist-oraculo.md` novo
criado com a tabela completa) já estavam cobertas por um dispatch central
bem arquitetado (`shrine_enters()`, 3 dobradores de gatilho distintos,
motor de blink com timing atômico vs. adiado corretamente diferenciado).

Único achado: 2 comentários no docstring do arquivo usavam a frase
"baixo valor esperado" (Weaver of Harmony's habilidade de copiar
gatilho; Destiny Spinner's animação de terreno) — a mesma linguagem de
julgamento de valor que o usuário proibiu explicitamente no Toph.
Investigando os dois: ambos são genuinamente estruturais, não julgamento
de valor disfarçado —
- Weaver of Harmony exige escolher QUAL dentre 17 tipos de gatilho de
  Shrine copiar a cada ativação (mesma exceção arquitetural do Strionic
  Resonator no Toph, não um "vale a pena?").
- Destiny Spinner cria um atacante/bloqueador TEMPORÁRIO (buff só até o
  fim do turno) — mesma família estrutural de Craterhoof/Unnatural
  Growth/Goreclaw (combate real não modelado neste sim).

Reclassificados com a justificativa correta, **sem mudança de
comportamento no código** (só docstring). Regressão de 5.000 partidas
pós-edição: 0 erros (esperado, mudança é só documentação).

**Leitura:** nem todo deck vai ter bug novo — reportar "já estava
correto" é tão parte da exigência do usuário quanto reportar um fix real,
desde que seja verificado de verdade (Scryfall, não memória) e não uma
alegação preguiçosa.

---

<!-- Copie o bloco acima para cada nova partida -->
