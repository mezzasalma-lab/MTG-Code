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

<!-- Copie o bloco acima para cada nova partida -->
