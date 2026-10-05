# Goldfish Log — Ms. Bumbleflower

> **Rodada 2026-10-05 (Terreno virado primeiro em T1/T2 + ordem de equipar determinística (varredura de 2026-10-05)) — dados brutos e reprodução:** [`resultados-ab/2026-10-05-terreno-virado-primeiro/LEIAME.md`](resultados-ab/2026-10-05-terreno-virado-primeiro/LEIAME.md)

## Terreno virado primeiro em T1/T2 + ordem de equipar determinística (varredura de 2026-10-05) — 2026-10-05

**Pedido do usuário:** *"Com base nos erros encontrados nas ultimas revisões, reanálise todos os outros decks em busca de erros semelhantes, e os corrija"*. Arquivo bruto/auditável: `resultados-ab/2026-10-05-terreno-virado-primeiro/` (`LEIAME.md`).

**Veredito:** um erro real, um conserto, bit-idêntico com a chave desligada e com o ensaio sem efeito colateral (modo GHOST). Modo padrão, N=10.000: comandante em campo até T3 25,3% → 27,1% (+1,84 ± 0,38 pp), até T4 +2,94 ± 0,36 pp, até T5 +1,37 ± 0,24 pp; comandante que nunca chega a entrar na partida -0,03 ± 0,03 pp. Modo resiliência: comandante em campo até T3 23,6% → 25,3% (+1,65 ± 0,37 pp), até T4 +2,95 ± 0,39 pp, até T5 +1,69 ± 0,32 pp; comandante que nunca chega a entrar na partida -0,20 ± 0,12 pp. A correção joga o terreno virado primeiro em média 0,41 vez(es) por partida (N=10.000, padrão) e o ensaio impede 0,32 vez(es) por partida (teria custado uma jogada).

**Achado (varredura das classes de erro do Vihaan/Megatron neste simulador):**
- **Terreno que entra virado nunca é jogado primeiro.** `play_land` jogava sempre o primeiro terreno da ordem própria do deck (desvirado antes de virado). Em T1/T2, sem nada pra conjurar, a mana do turno era desperdiçada enquanto o terreno que entra virado ficava na mão pra um turno em que ele custa desenvolvimento. Mesmo erro achado e corrigido no Vihaan e no Megatron (2026-10-03/04).
- **Ordem de iteração de `set` de strings dependia de `PYTHONHASHSEED`.** A mesma semente dava resultados diferentes em processos diferentes (o hash de `str` muda a cada execução do Python). Medido: 3 `PYTHONHASHSEED` diferentes, 1.500 sementes × 2 modos, comparando o estado final campo a campo (`resumos/determinismo.txt`). Aqui: `for eq_name in EQUIPMENT_NAMES` (set) decidia a ORDEM em que Lightning Greaves e Swiftfoot Boots tentam equipar, com mana limitada. No controle (chave desligada) 0 sementes divergentes em 1.500 × 2 modos: a correção é **preventiva** (só 2 equipamentos na lista; a divergência exigiria os dois desequipados com mana pra um só).

**O que mudou:**
- `TAPPED_LAND_FIRST_ENABLED` (padrão `True`), `TAPPED_LAND_FIRST_MAX_TURN = 2`: em T1..T2, havendo terreno virado E desvirado na mão, `tapped_first_pick` joga o virado, **salvo se isso custar desenvolvimento**: o teste é um ENSAIO a seco da própria fase de conjuração pré-combate do deck (cópia profunda do estado; `CARD_DB` compartilhado; RNG do estado copiado; `random` global restaurado), comparando o MV total das cartas que saem da mão com cada candidato. Empate → o virado. Dentro de cada grupo vale a ordem própria do deck (cor mais escassa etc.). Contadores novos no estado: `tapped_land_first_plays_total` (jogou o virado) e `tapped_land_skipped_for_play_total` (o ensaio mostrou que custaria uma jogada e jogou o desvirado). `TAPPED_LAND_FIRST_GHOST` só existe pra validação (roda o ensaio e ignora o resultado). Com a chave em `False` o caminho antigo volta bit a bit.
- `DETERMINISTIC_SET_ORDER_ENABLED` (padrão `True`): `for eq_name in sorted(EQUIPMENT_NAMES)` no lugar de iterar o `set`. Com a chave em `False` o laço antigo (ordem do hash) volta.

**Medido (pareado, mesmas sementes; IC95% = 1,96·dp/√N da diferença):**

Modo padrão, N=10.000 (`resumos/ab_10000.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 6217 (62.2%)
   campo                                          base     variante dif. pareada (IC95%)
   commander_cast_turn__nunca                   0.0176       0.0173      -0.0003 ±0.0003  
  *commander_cast_turn__ate_T3                  0.2527       0.2711      +0.0184 ±0.0038  
  *commander_cast_turn__ate_T4                  0.6222       0.6516      +0.0294 ±0.0036  
  *commander_cast_turn__ate_T5                  0.8052       0.8189      +0.0137 ±0.0024  
  *next_uid                                    27.6954      27.8745      +0.1791 ±0.0375  
  *len_battlefield                             26.3806      26.5556      +0.1750 ±0.0368  
  *opponent_forced_draws_total                 18.8363      19.0375      +0.2012 ±0.0441  
  *interaction_plays                            3.5706       3.6073      +0.0367 ±0.0094  
  *len_library                                 62.2983      62.0584      -0.2399 ±0.0646  
  *len_graveyard                                5.6115       5.6702      +0.0587 ±0.0162  
  *cards_drawn_extra                           26.4223      26.6327      +0.2104 ±0.0614  
  *commander_cast_turn__ate_T6                  0.8897       0.8938      +0.0041 ±0.0014  
  *mana_spent_this_turn                        13.4606      13.5814      +0.1208 ±0.0421  
  *proxy_damage_total                         218.8067     223.2510      +4.4443 ±1.5527  
  *len_first_counter_this_turn                  3.4820       3.5161      +0.0341 ±0.0150  
  *counters_placed_total                       90.4371      92.4162      +1.9791 ±0.8743  
  *turn                                         9.7198       9.7123      -0.0075 ±0.0034  
  *won_via_ascendancy                           0.2292       0.2340      +0.0048 ±0.0022
```
Modo resiliência, N=10.000 (`resumos/ab_10000_resiliencia.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 6217 (62.2%)
   campo                                          base     variante dif. pareada (IC95%)
  *commander_cast_turn__nunca                   0.0305       0.0285      -0.0020 ±0.0012  
  *commander_cast_turn__ate_T3                  0.2361       0.2526      +0.0165 ±0.0037  
  *commander_cast_turn__ate_T4                  0.5730       0.6025      +0.0295 ±0.0039  
  *commander_cast_turn__ate_T5                  0.7518       0.7687      +0.0169 ±0.0032  
  *opponent_forced_draws_total                 12.6883      12.8769      +0.1886 ±0.0589  
  *commander_cast_turn__ate_T6                  0.8483       0.8552      +0.0069 ±0.0024  
  *interaction_plays                            2.7530       2.7812      +0.0282 ±0.0111  
  *len_library                                 69.1143      68.9294      -0.1849 ±0.0749  
  *cards_drawn_extra                           20.5250      20.6755      +0.1505 ±0.0685  
  *next_uid                                    24.7555      24.9143      +0.1588 ±0.0880  
  *commander_uid                               10.2416      10.4117      +0.1701 ±0.0973  
  *len_smart_removal_log                        0.9283       0.9419      +0.0136 ±0.0078  
  *smart_removals_total                         0.9283       0.9419      +0.0136 ±0.0078  
  *proxy_damage_total                          91.2522      93.0961      +1.8439 ±1.1331  
  *commander_in_play                            0.7413       0.7481      +0.0068 ±0.0045  
  *len_graveyard                                7.6616       7.7308      +0.0692 ±0.0459  
  *len_first_counter_this_turn                  1.8154       1.8356      +0.0202 ±0.0151  
  *communal_brewing_ingredient_counters         0.2338       0.2372      +0.0034 ±0.0026
```
Os lotes de N=2.000 (`ab_2000*.txt`) e as variantes de sensibilidade (uma correção por vez) estão em `resumos/`.

**Raciocinado (não medido):** o ganho esperado é pequeno e concentrado em T1–T3: só muda a partida quando a mão tem terreno virado E desvirado e nenhuma jogada de T1/T2 que o terreno desvirado pague (nesses casos o terreno virado deixa de ficar parado na mão até um turno em que atrasaria o desenvolvimento).

**Validação:** smoke (99 cartas, 0 desconhecidas, 0 duplicadas não-básicas, 200 partidas × 2 modos sem exceção); bit-identidade com as chaves desligadas × `bumbleflower_goldfish_v1_ANTES_f4b6289.py`, 20.000 partidas × 2 modos (`resumos/bitident_20000.txt`); regressão 20.000 × 2 modos × 2 configurações, 0 exceções (`resumos/regressao_20000.txt`); testes dirigidos 8/8 (`resumos/testes_dirigidos.txt`); ghost (chave ligada + ensaio ignorado == desligada), 20.000 × 2 modos (`resumos/ghost_20000.txt`); reprodutibilidade por `cmp` (`resumos/verificacao_reproducao.txt`).

**Escopo — verificado:**
- **Terreno virado primeiro:** leitura de `play_land` (+ predicado de entrada virada do deck); testes dirigidos TL1–TL8 (escolha com/sem jogada em T1, chave desligada, T3, só um tipo na mão, ensaio sem efeito no estado/RNG/`random`, modo GHOST, integração em `play_land`); A/B pareado 2.000 e 10.000 nos dois modos.
- **Ensaio sem efeito colateral:** com a chave ligada + modo GHOST (roda o ensaio e ignora o resultado) o resultado é idêntico a tudo desligado, 20.000 × 2 modos (`resumos/ghost_20000.txt`).
- **Bit-identidade** com as chaves desligadas × snapshot: 20.000 partidas × 2 modos, impressão digital do resultado inteiro.
- **Regressão** 20.000 × 2 modos × 2 configurações: 0 exceções.
- **Determinismo:** 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, controle × correção (`resumos/determinismo.txt`); varredura AST (`varredura-2026-10-05/`).

**Escopo — NÃO verificado:**
- **Condições de entrada dos terrenos** além do que a varredura mecânica cobriu (`varredura-2026-10-05/`: cenário de campo vazio + cenário condição satisfeita × violada para os padrões "unless you control …"/reveal; terrenos que o `CARD_DB` do deck não tem como básico foram pulados e estão listados lá).
- **Resto da taxonomia da Regra #1 neste arquivo** (caminhos de conjuração fora da mão e "whenever you cast", sacrifício × destroy, cascade, contadores `_sick` agregados, fórmulas dinâmicas achatadas): varrido na triagem de 2026-10-05 por `grep` e leitura pontual das funções, **sem** leitura integral do arquivo e **sem** instrumentação em runtime nesta rodada. "Sem achado" aí significa "o `grep` não achou", não "não existe".
- **Oponente real:** o goldfish não modela (convenção do repositório); nada aqui mede interação além do proxy já existente.

**Observação:** 0 exceções em 20.000 × 2 modos × 2 configurações; os invariantes genéricos (carta acima do número no baralho; contadores negativos) deram 0 violações.

---

## Porte completo do modo de resiliência + CR 903.9a nativa desde o início — 2026-09-21

**Gatilho:** "Faça agora a Ms. Bumbleflower" — seguindo o porte
concluído no Nekusar, Azula, Beorn e Thranduil. Detalhes completos em
`checklist-oraculo.md`.

**Achado:** deck nasce com CR 903.9a correta desde o início. `state.
battlefield` aqui é lista de objetos `Permanent` (não strings) —
`remove_permanent` envolve a `leave_battlefield` já existente (que já
tratava Ozolith/Chasm Skulker) e só adiciona o tratamento do comandante
(zona de comando). Auditoria dos pontos de sacrifício pré-existentes
(disciplina obrigatória) achou **0 sacrifice outlets neste deck**
(diferente do Beorn/Thranduil) — mas achou 2 bugs reais não
relacionados: (1) taxa de comandante (CR 903.8) tinha o contador
certo, mas o efeito de taxação nunca era lido em `effective_cost`; (2)
`mulligan()` reembaralhava via RNG global em vez do RNG seedado (mesma
classe de bug do Azula — 685/3000 = 22,8% de partidas
não-determinísticas com a mesma seed antes do fix).

**Resultado:** modo padrão com bit-identidade PERFEITA (0/20000
mismatches) contra uma versão anterior patcheada só com o fix de
determinismo — porte 100% estrutural, como esperado (0 sacrifícios
voluntários = comandante nunca sai de campo em modo padrão = taxa
nunca observável fora do modo de resiliência).

**Validação:** regressão de 20.000 partidas em modo de resiliência, 0
exceções, 0 comandantes presos no cemitério, 33,48% das partidas com
recast pagando a taxa CR 903.8 + 22 testes dirigidos.

## Auditoria oráculo-por-oráculo completa — 2026-09-13

Extensão pra este deck da mesma auditoria já feita no
Megatron/Azula/Beorn/Captain Storm/Edgar Markov/Hei Bai/Maralen/Kutzil.
Detalhes carta-a-carta completos em `checklist-oraculo.md` (seção no
topo) — **12 gaps reais** encontrados, mesmo depois da rodada de
construção original já ter corrigido 8 outros + 1 bug crítico (comandante
nunca em campo). Achado principal: Heliod, Sun-Crowned tratado como
criatura o tempo todo, sem o gate real de devoção ao branco (`>=5`),
afetando 5 pontos do motor (combate, contador, mana do Rishkar, Ozolith).
Mais 11 gaps: 2 habilidades de Heliod incompletas/ausentes (gatilho de
vida só via combate, `{1}{W}` de lifelink 100% ausente); Deepglow Skate
só dobrava 1 alvo em vez de "any number"; Jolrael's `{4}{G}{G}` overdrive
100% ausente; Swiftfoot Boots' Equip {1} nunca cobrado (mesma classe do
bug sistêmico do Captain Storm); Slip Out the Back's "phases out" 100%
ignorado (alvo continuava atacando); Tamiyo Seasoned Scholar's −7 100%
ausente; Walking Ballista's "remove counter: 1 dano" 100% ausente; Twenty
-Toed Toad's limite de mão (20, não infinito) misturado com as fontes
verdadeiramente ilimitadas; Flooded Grove subcontada como 0 mana junto
com 3 filter lands que são genuinamente líquido-0 (ela não é, tem `{T}:
Add {C}` de graça); Oakhollow Village esquecia Twenty-Toed Toad (Frog) do
próprio set de tipos elegíveis.

### Métricas antes/depois (2.000 partidas, seed 7.000.000, turns=10, mesma seed)

| Métrica | Antes | Depois |
|---|---|---|
| Dano proxy médio | 187,8 | 199,0 |
| Dano proxy mediano | 126,5 | 133,0 |
| Cartas compradas extra (média) | 24,5 | 25,9 |
| Compras forçadas do oponente (média) | 17,3 | 18,1 |
| Treasures criados (média) | 2,6 | 2,8 |
| Contadores colocados (média) | 72,5 | 79,9 |
| Vida ganha (média) | 2,5 | 17,3 |
| Interação jogada (média) | 3,4 | 3,5 |
| Vitórias via Simic Ascendancy | 419/2000 (21,0%) | 440/2000 (22,0%) |
| Vitórias via Twenty-Toed Toad | 61/2000 (3,1%) | 73/2000 (3,7%) |
| Biblioteca esgotada | 0/2000 | 1/2000 |

**Leitura:** todas as métricas se movem pra CIMA, na direção esperada de
uma rodada que só corrigiu implementações ausentes/parciais (nenhum fix
removeu valor de nenhuma carta). O salto mais chamativo é vida ganha
(2,5→17,3, ~7x) — driver principal é o achado #3 (Heliod's `{1}{W}:
lifelink noutra criatura`, ramo antes 100% ausente): antes, Heliod só
ganhava vida via lifelink de combate nativo (raro nesta lista — só
Mangara tem lifelink impresso); agora, sempre que Heliod está em campo
com mana sobrando, ele ativamente converte o poder do melhor atacante em
vida ganha TODO turno, o que também retrigger o próprio Heliod (mais
contadores) — efeito composto real, não um bug (mana-gated a 1 ativação
por turno, sem loop). Dano proxy subiu ~6% (187,8→199,0) — soma de vários
fixes menores na mesma direção (Deepglow dobrando múltiplos alvos,
Jolrael overdrive, Ballista convertendo contadores em dano no último
turno, Flooded Grove destravando 1 mana extra). Contadores colocados
subiu ~10% (mesma causa: Deepglow multi-alvo + Oakhollow incluindo o Toad
+ fasear ainda coloca o contador do Slip Out). As 2 condições de vitória
alternativa também sobem levemente (mais contadores = growth counters da
Ascendancy sobem mais rápido; Toad se beneficia do próprio ajuste de Frog
no Oakhollow) — nenhuma métrica se moveu de forma inexplicável ou na
direção errada.

**Validação:** smoke test (94 cartas no `CARD_DB`, 99 na `BASE_LIBRARY`,
0 desconhecidas/duplicadas fora das básicas) + 2.000 partidas antes/depois
(tabela acima) + 20.000 partidas de regressão (seed 9.500.000+, turns=10,
**0 exceções**, ~40s) + 23 checagens dirigidas (1 arquivo, uma por gap,
todas passando).

---

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

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

---

## 2026-09-02 — Simulador goldfish construído do zero (`bumbleflower_goldfish_v1.py`)

Último dos 4 decks sem simulador desta sessão a ser fechado (depois de
Kutzil, Azula e Captain Storm) — a lista foi colada ao vivo pelo usuário
nesta conversa (`lista.md` estava vazio antes disso). Detalhamento
completo carta-a-carta em `checklist-oraculo.md`.

**Metodologia:** oráculo real via Scryfall (line-by-line, "compile
TUDO"), implementação com objetos `Permanent` (o deck de contadores mais
denso da sessão), testes unitários (12 no total, 2 arquivos), 1 bug
crítico (comandante nunca em campo — mesmo bug já visto no Azula) + 8
gaps reais após varredura automatizada de tags órfãs, regressão de
20.000 partidas (0 exceções, ~62s).

**Motor real deste deck:** Ms. Bumbleflower dispara em toda magia
conjurada (força o oponente a comprar + põe contador + no 2º gatilho do
turno compra 2), centralizado junto com TODA outra fonte de contador do
deck (Rishkar, Forgotten Ancient, Managorger/Kalonian Hydra, Deepglow
Skate, Simic Ascendancy, Noble Heritage, Wizard Class, Oakhollow
Village, Ozolith) numa função única `put_counters()` — o que faz Danny
Pink (compra no 1º contador de cada criatura por turno) e Simic
Ascendancy (vitória alternativa com 20+ growth counters) reagirem a
QUALQUER uma dessas fontes automaticamente, sem precisar de código
duplicado em cada carta.

### Achado: 2 vitórias alternativas reais, ambas disparando na prática

- **Simic Ascendancy** (20+ growth counters no upkeep): **4.093/20.000
  partidas (~20.5%)** venceram assim na regressão de 10 turnos — um
  resultado real do quão denso é o pacote de multiplicadores de
  contador (Kalonian Hydra dobra tudo ao atacar, Deepglow Skate dobra na
  ETB, a própria Simic Ascendancy é um mana sink direto pra +1/+1).
- **Twenty-Toed Toad** (20+ contadores nele ou 20+ cartas na mão ao
  atacar): **505/20.000 (~2.5%)**.

Nenhuma das duas foi "decidida" a dar certo — surgiram naturalmente da
implementação fiel de cada carta, exatamente o tipo de achado que a
regressão longa existe pra revelar.

### Métricas (20.000 partidas, seed 5.000.000+, turns=10, 0 exceções)

| Métrica | Média |
|---|---|
| Dano proxy total | 188.7 |
| Cartas compradas extra | 24.8 |
| Compras forçadas do oponente (retrigger Smothering Tithe) | 17.7 |
| Contadores colocados | 72.3 |
| Vida ganha | 2.7 |
| Interação jogada | 3.5 |
| Biblioteca esgotada | 9/20000 |

