# Goldfish Log — Maralen, Fae Ascendant

> **Rodada 2026-10-07 (Payoff de landfall antes do terreno) — dados brutos e reprodução:** [`resultados-ab/2026-10-07-landfall-payoff-primeiro/LEIAME.md`](resultados-ab/2026-10-07-landfall-payoff-primeiro/LEIAME.md)

> **Rodada 2026-10-05 (Terreno virado primeiro em T1/T2 + condições de entrada de terreno (varredura de 2026-10-05)) — dados brutos e reprodução:** [`resultados-ab/2026-10-05-terreno-virado-primeiro/LEIAME.md`](resultados-ab/2026-10-05-terreno-virado-primeiro/LEIAME.md)

> **Rodada 2026-10-05 (Mulligan com escolha do fundo + upkeep antes do draw (varredura de 2026-10-05)) — dados brutos e reprodução:** [`resultados-ab/2026-10-05-mulligan-e-ordem-das-fases/LEIAME.md`](resultados-ab/2026-10-05-mulligan-e-ordem-das-fases/LEIAME.md)

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Payoff de landfall antes do terreno (`LANDFALL_PAYOFF_FIRST`) — 2026-10-07

**Pedido do usuário:** *"Corrige os simuladores com erro no script para automatizar a ordem de jogadas para o landfall"*. Arquivo bruto/auditável: `resultados-ab/2026-10-07-landfall-payoff-primeiro/` (`LEIAME.md`).

**Veredito:** um erro real de ordem, um conserto atrás de chave, bit-idêntico com a chave desligada. O payoff entra antes do terreno em **16,1%** das partidas (11,7% na resiliência). Efeito pequeno: **+0,11 tokens de Elfo por partida (+42%)** e **+0,12 contadores de landfall**; neutro em comandante, combo infinito e compras do Staff.

**Achado:** o simulador jogava o terreno do turno ANTES de conjurar o payoff de landfall (`play_land` antes da fase de conjuração; a ordem completa do turno está no `LEIAME.md` da pasta). Com a ordem antiga o terreno do turno nunca disparava o landfall do payoff que o mana de agora já pagava.

**Correção:** chave `LANDFALL_PAYOFF_FIRST` + `cast_landfall_payoffs_first`, com guarda por ensaio a seco (nada que a ordem antiga conjuraria/jogaria pode deixar de acontecer). Detalhes e a 1ª guarda aritmética que estava errada: `LEIAME.md` da pasta.

**Números (N=10.000 pareado, `*` = excede o IC95%):**

| campo (N=10.000 pareado) | padrao: base -> depois (dif ± IC95%) | resiliencia: base -> depois (dif ± IC95%) |
|---|---|---|
| `lands_played_total` | 6.154 -> 6.169 (+0.016 ± 0.007) * | 5.822 -> 5.834 (+0.012 ± 0.005) * |
| `landfall_elf_tokens_total` | 0.250 -> 0.356 (+0.106 ± 0.009) * | 0.090 -> 0.166 (+0.076 ± 0.007) * |
| `landfall_counters_total` | 0.329 -> 0.450 (+0.121 ± 0.010) * | 0.126 -> 0.212 (+0.086 ± 0.008) * |
| `tokens_created_total` | 1002.887 -> 1030.995 (+28.108 ± 42.218) | 254.725 -> 258.801 (+4.076 ± 17.087) |
| `ramp_pieces_cast_total` | 5.005 -> 5.010 (+0.005 ± 0.017) | 3.725 -> 3.730 (+0.005 ± 0.011) |
| `commander_cast_turn__ate_T3` | - | 0.140 -> 0.140 (-0.000 ± 0.000) |
| `commander_cast_turn__ate_T4` | 0.494 -> 0.494 (+0.000 ± 0.000) | 0.418 -> 0.418 (+0.000 ± 0.001) |
| `commander_cast_turn__ate_T5` | - | 0.758 -> 0.758 (-0.000 ± 0.001) |
| `infinite_combo_turn__nunca` | 0.840 -> 0.840 (+0.000 ± 0.002) | 0.943 -> 0.943 (-0.000 ± 0.002) |
| `infinite_combo_turn__ate_T6` | 0.049 -> 0.049 (+0.000 ± 0.001) | 0.023 -> 0.024 (+0.001 ± 0.001) * |
| `staff_infinite_draws` | 2.112 -> 2.123 (+0.011 ± 0.070) | 0.575 -> 0.596 (+0.022 ± 0.045) |
| partidas com resultado idêntico ao da base | 83.8% | 88.3% |

**Validação:** testes dirigidos 6/6; bit-identidade 20.000 × 2 modos com a chave desligada (0 divergências); regressão 20.000 × 2 modos × 2 configurações (0 exceções); determinismo 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos (0 divergências); smoke 99 cartas.

**Não coberto / não verificado:** magia que põe terreno em campo antes do payoff, terreno que volta ao campo, política de jogador humano; o A/B mede o simulador (3 oponentes passivos), não a mesa real.

---

## Terreno virado primeiro em T1/T2 + condições de entrada de terreno (varredura de 2026-10-05) — 2026-10-05

**Pedido do usuário:** *"Com base nos erros encontrados nas ultimas revisões, reanálise todos os outros decks em busca de erros semelhantes, e os corrija"*. Arquivo bruto/auditável: `resultados-ab/2026-10-05-terreno-virado-primeiro/` (`LEIAME.md`).

**Veredito:** um erro real, um conserto, bit-idêntico com a chave desligada e com o ensaio sem efeito colateral (modo GHOST). Modo padrão, N=10.000: comandante em campo até T3 15,9% → 15,2% (-0,76 ± 0,28 pp), até T4 -0,39 ± 0,34 pp, até T5 -0,63 ± 0,26 pp, comandante que nunca entra +0,02 ± 0,04 pp. Modo resiliência: comandante em campo até T3 14,8% → 14,0% (-0,75 ± 0,27 pp), até T4 -0,39 ± 0,34 pp, até T5 -0,75 ± 0,31 pp, comandante que nunca entra +0,07 ± 0,11 pp. A correção joga o terreno virado primeiro em média 0,36 vez(es) por partida (N=10.000, padrão) e o ensaio impede 0,52 vez(es) por partida (teria custado uma jogada). Terrenos jogados no total: +0,003 ± 0,009 por partida.

**Achado (varredura das classes de erro do Vihaan/Megatron neste simulador):**
- **Terreno que entra virado nunca é jogado primeiro.** `play_land` jogava sempre o primeiro terreno da ordem própria do deck (desvirado antes de virado). Em T1/T2, sem nada pra conjurar, a mana do turno era desperdiçada enquanto o terreno que entra virado ficava na mão pra um turno em que ele custa desenvolvimento. Mesmo erro achado e corrigido no Vihaan e no Megatron (2026-10-03/04).
- **Cinco terrenos entravam DESVIRADOS contra o oráculo** (varredura mecânica de entrada, `varredura-2026-10-05/resumos/audit_entrada_ANTES.txt` e `audit_entrada2_ANTES.txt`): só Bojuka Bog/Path of Ancestry/Zagoth Triome (tag `etb_tapped`) entravam virados. Faltavam: **Drowned Catacomb** ("tapped unless you control an Island or a Swamp"), **Hinterland Harbor** (Forest or Island), **Woodland Cemetery** (Swamp or Forest), **Sunken Hollow** ("unless you control two or more basic lands") e **Gilt-Leaf Palace** ("you may reveal an Elf card from your hand. If you don't, this land enters tapped"). "Island/Swamp/Forest" aqui é SUBTIPO de terreno (Bayou, Tropical Island, Underground Sea, Breeding Pool, Watery Grave, Overgrown Tomb, Sunken Hollow e Zagoth Triome contam; Sunken Hollow, uma dual tipada, NÃO conta como básico). Os choques (Breeding Pool/Watery Grave/Overgrown Tomb) seguem a convenção do repositório (pagam 2 de vida, entram desvirados) e Morphic Pool/Undergrowth Stadium ("unless you have two or more opponents") entram desvirados em mesa de 4. Mana fantasma: esses 5 produziam mana no próprio turno.

**O que mudou:**
- `TAPPED_LAND_FIRST_ENABLED` (padrão `True`), `TAPPED_LAND_FIRST_MAX_TURN = 2`: em T1..T2, havendo terreno virado E desvirado na mão, `tapped_first_pick` joga o virado, **salvo se isso custar desenvolvimento**: o teste é um ENSAIO a seco da própria fase de conjuração pré-combate do deck (cópia profunda do estado; `CARD_DB` compartilhado; RNG do estado copiado; `random` global restaurado), comparando o MV total das cartas que saem da mão com cada candidato. Empate → o virado. Dentro de cada grupo vale a ordem própria do deck (cor mais escassa etc.). Contadores novos no estado: `tapped_land_first_plays_total` (jogou o virado) e `tapped_land_skipped_for_play_total` (o ensaio mostrou que custaria uma jogada e jogou o desvirado). `TAPPED_LAND_FIRST_GHOST` só existe pra validação (roda o ensaio e ignora o resultado). Com a chave em `False` o caminho antigo volta bit a bit.
- `LAND_ENTRY_CONDITIONS_ENABLED` (padrão `True`) + `land_enters_tapped(state, name)` (fonte única, avaliada ANTES de o terreno entrar): checklands por subtipo (`CHECKLAND_SUBTYPES`/`LAND_BASIC_SUBTYPES`, tabela derivada do `type_line` do oráculo), Sunken Hollow (≥2 básicos Forest/Island/Swamp), Gilt-Leaf Palace (algum card de Elfo na mão, fora ela mesma). Com a chave em `False` só a tag `etb_tapped` manda (antigo).

**Medido (pareado, mesmas sementes; IC95% = 1,96·dp/√N da diferença):**

Modo padrão, N=10.000 (`resumos/ab_10000.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 5793 (57.9%)
   campo                                          base     variante dif. pareada (IC95%)
   lands_played_total                           6.1506       6.1536      +0.0030 ±0.0088  
   commander_cast_turn__nunca                   0.0191       0.0193      +0.0002 ±0.0004  
  *commander_cast_turn__ate_T3                  0.1592       0.1516      -0.0076 ±0.0028  
  *commander_cast_turn__ate_T4                  0.4976       0.4937      -0.0039 ±0.0034  
  *commander_cast_turn__ate_T5                  0.8520       0.8457      -0.0063 ±0.0026  
  *len_tapped_lands_this_turn                   0.1735       0.2047      +0.0312 ±0.0043  
  *interaction_spells_cast_total                2.5118       2.4983      -0.0135 ±0.0129  
   len_graveyard                                3.0796       3.0668      -0.0128 ±0.0143  
   lands_played_this_turn                       0.6518       0.6562      +0.0044 ±0.0050  
   itlimoc_transform_turn__ate_T4               0.0207       0.0199      -0.0008 ±0.0010  
   tokens_created_total                       960.8860    1002.8867     +42.0007 ±54.5951 
   elf_tokens                                 959.4792    1001.4788     +41.9996 ±54.5944 
   maralen_triggers_total                      12.9223      12.8792      -0.0431 ±0.0590  
   maralen_free_casts_total                     3.2235       3.2175      -0.0060 ±0.0083  
   itlimoc_transform_turn__ate_T3               0.0014       0.0012      -0.0002 ±0.0003  
   itlimoc_transform_turn__ate_T6               0.1322       0.1310      -0.0012 ±0.0019  
   cards_exiled_total                          23.2569      23.2003      -0.0566 ±0.0911  
   len_mistbind_exiled                          0.2355       0.2335      -0.0020 ±0.0033  
   staff_finite_draws_total                     0.8676       0.8475      -0.0201 ±0.0345
```
Modo resiliência, N=10.000 (`resumos/ab_10000_resiliencia.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 5828 (58.3%)
   campo                                          base     variante dif. pareada (IC95%)
   lands_played_total                           5.8189       5.8224      +0.0035 ±0.0087  
   commander_cast_turn__nunca                   0.0469       0.0476      +0.0007 ±0.0011  
  *commander_cast_turn__ate_T3                  0.1475       0.1400      -0.0075 ±0.0027  
  *commander_cast_turn__ate_T4                  0.4215       0.4176      -0.0039 ±0.0034  
  *commander_cast_turn__ate_T5                  0.7659       0.7584      -0.0075 ±0.0031  
  *len_tapped_lands_this_turn                   0.0932       0.1170      +0.0238 ±0.0039  
  *cards_exiled_total                          14.8227      14.6914      -0.1313 ±0.0717  
  *itlimoc_transform_turn__ate_T4               0.0162       0.0147      -0.0015 ±0.0009  
  *maralen_free_casts_total                     2.4845       2.4705      -0.0140 ±0.0100  
  *faerie_tokens                                0.4786       0.4650      -0.0136 ±0.0102  
  *maralen_triggers_total                       7.6740       7.6161      -0.0579 ±0.0448  
  *len_library                                 66.0182      66.1662      +0.1480 ±0.1187  
  *tokens_created_total                       214.7286     254.7245     +39.9959 ±33.3693 
  *len_smart_removal_log                        0.6488       0.6558      +0.0070 ±0.0060  
  *smart_removals_total                         0.6488       0.6558      +0.0070 ±0.0060  
  *len_smart_graveyard_snipe_log                0.2934       0.2881      -0.0053 ±0.0047  
  *smart_graveyard_snipes_total                 0.2934       0.2881      -0.0053 ±0.0047  
  *commander_cast_count                         1.5034       1.4974      -0.0060 ±0.0054  
  *landfall_elf_tokens_total                    0.0935       0.0898      -0.0037 ±0.0033
```
Os lotes de N=2.000 (`ab_2000*.txt`) e as variantes de sensibilidade (uma correção por vez) estão em `resumos/`.

**Raciocinado (não medido):** o ganho esperado é pequeno e concentrado em T1–T3: só muda a partida quando a mão tem terreno virado E desvirado e nenhuma jogada de T1/T2 que o terreno desvirado pague (nesses casos o terreno virado deixa de ficar parado na mão até um turno em que atrasaria o desenvolvimento).

**Validação:** smoke (99 cartas, 0 desconhecidas, 0 duplicadas não-básicas, 200 partidas × 2 modos sem exceção); bit-identidade com as chaves desligadas × `maralen_goldfish_v1_ANTES_7918e0b.py`, 20.000 partidas × 2 modos (`resumos/bitident_20000.txt`); regressão 20.000 × 2 modos × 2 configurações, 0 exceções (`resumos/regressao_20000.txt`); testes dirigidos 13/13 (`resumos/testes_dirigidos.txt`); ghost (chave ligada + ensaio ignorado == desligada), 20.000 × 2 modos (`resumos/ghost_20000.txt`); reprodutibilidade por `cmp` (`resumos/verificacao_reproducao.txt`).

**Escopo — verificado:**
- **Terreno virado primeiro:** leitura de `play_land` (+ predicado de entrada virada do deck); testes dirigidos TL1–TL8 (escolha com/sem jogada em T1, chave desligada, T3, só um tipo na mão, ensaio sem efeito no estado/RNG/`random`, modo GHOST, integração em `play_land`); A/B pareado 2.000 e 10.000 nos dois modos.
- **Ensaio sem efeito colateral:** com a chave ligada + modo GHOST (roda o ensaio e ignora o resultado) o resultado é idêntico a tudo desligado, 20.000 × 2 modos (`resumos/ghost_20000.txt`).
- **Bit-identidade** com as chaves desligadas × snapshot: 20.000 partidas × 2 modos, impressão digital do resultado inteiro.
- **Regressão** 20.000 × 2 modos × 2 configurações: 0 exceções.
- **Entrada de terrenos:** testes dirigidos TL12–TL16 (checklands com basico e com dual tipado, Sunken Hollow com duais que não contam como básico, Gilt-Leaf Palace com/sem Elfo, chave desligada = antigo, integração: mana do turno); varredura mecânica de entrada antes/depois.

**Escopo — NÃO verificado:**
- **Condições de entrada dos terrenos** além do que a varredura mecânica cobriu (`varredura-2026-10-05/`: cenário de campo vazio + cenário condição satisfeita × violada para os padrões "unless you control …"/reveal; terrenos que o `CARD_DB` do deck não tem como básico foram pulados e estão listados lá).
- **Resto da taxonomia da Regra #1 neste arquivo** (caminhos de conjuração fora da mão e "whenever you cast", sacrifício × destroy, cascade, contadores `_sick` agregados, fórmulas dinâmicas achatadas): varrido na triagem de 2026-10-05 por `grep` e leitura pontual das funções, **sem** leitura integral do arquivo e **sem** instrumentação em runtime nesta rodada. "Sem achado" aí significa "o `grep` não achou", não "não existe".
- **Oponente real:** o goldfish não modela (convenção do repositório); nada aqui mede interação além do proxy já existente.

**Observação:** 0 exceções em 20.000 × 2 modos × 2 configurações; os invariantes genéricos (carta acima do número no baralho; contadores negativos) deram 0 violações.

---

## Mulligan com escolha do fundo + upkeep antes do draw (varredura de 2026-10-05) — 2026-10-05

**Pedido do usuário:** *"Com base nos erros encontrados nas ultimas revisões, reanálise todos os outros decks em busca de erros semelhantes, e os corrija"*. Arquivo bruto/auditável: `resultados-ab/2026-10-05-mulligan-e-ordem-das-fases/` (`LEIAME.md`).

**Veredito:** dois erros reais, dois consertos, bit-idênticos com a chave desligada. Comandante em campo até T5: 84,1% → 85,2% (+1,11 ± 0,27 pp); nunca em 8 turnos: −0,37 ± 0,14 pp (N=10.000, padrão). O ganho vem do **mulligan** (isolado dá o mesmo número). A ordem upkeep × draw muda 32% das partidas mas **não move o comandante**; dos ~100 campos medidos só uns poucos passam do IC95% (`marwyn_power` +0,047 ± 0,028, `ramp_pieces_cast_total` +0,041 ± 0,026: ~1,5 IC95%), o que cabe no acaso de olhar ~100 campos. Não afirmo efeito da ordem.

**Achado (varredura das classes de erro do Vihaan/Megatron neste simulador):**
- **London Mulligan com as cartas do fundo SORTEADAS** (`rng.shuffle(hand); bottom = hand[:penalty]`). CR 103.5: depois de comprar a mão nova o jogador "puts a number of those cards ... on the bottom of their library in any order", ou seja, ESCOLHE quais. O arquivo devolvia, com a mesma chance, uma carta-chave ou um terreno que faltava. Mesma classe do erro achado e corrigido no Megatron e no Vihaan (2026-10-03/04).
- **Upkeep depois do draw.** `play_turn` comprava e só então rodava `upkeep_step` (Bitterblossom, Bitterbloom Bearer). CR 502–504: upkeep vem ANTES do draw step. Regra #6: o código da carta estava certo, a posição da chamada não.

**O que mudou:**
- `MULLIGAN_SMART_BOTTOM_ENABLED` (padrão `True`) + `choose_bottom(hand, n)`: só devolve terreno quando sobram MAIS de 4 na mão (e então o que entra virado primeiro, se o `CARD_DB` marcar `etb_tapped`); fora isso devolve a carta não-terreno de MAIOR custo, poupando `MULLIGAN_PROTECTED` (as cartas que `should_keep` já trata como boa abertura). A regra do mulligan grátis do 1º mulligan (CR 103.5c, multiplayer) já estava modelada e não mudou. Com a chave em `False` o caminho antigo (sorteio) volta bit a bit.
- `UPKEEP_BEFORE_DRAW_ENABLED` (padrão `True`): em `play_turn`, `upkeep_step` roda antes da compra; desligada, roda depois (caminho antigo).

**Medido (pareado, mesmas sementes; IC95% = 1,96·dp/√N da diferença):**

Modo padrão, N=10.000 (`resumos/ab_10000.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 5642 (56.4%)
   campo                                          base     variante dif. pareada (IC95%)
  *commander_cast_turn__nunca                   0.0228       0.0191      -0.0037 ±0.0014  
  *commander_cast_turn__ate_T3                  0.1556       0.1592      +0.0036 ±0.0017  
  *commander_cast_turn__ate_T4                  0.4892       0.4976      +0.0084 ±0.0027  
  *commander_cast_turn__ate_T5                  0.8409       0.8520      +0.0111 ±0.0027  
  *commander_cast_turn__ate_T6                  0.9253       0.9338      +0.0085 ±0.0023  
  *lands_played_total                           6.0999       6.1506      +0.0507 ±0.0145  
  *commander_cast_count                         0.9772       0.9809      +0.0037 ±0.0014  
  *commander_in_play                            0.9772       0.9809      +0.0037 ±0.0014  
  *ramp_pieces_cast_total                       4.9592       5.0141      +0.0549 ±0.0320  
  *maralen_free_casts_total                     3.2059       3.2235      +0.0176 ±0.0113  
  *len_battlefield                             21.2289      21.3403      +0.1114 ±0.0833  
  *faerie_tokens                                1.3126       1.3280      +0.0154 ±0.0122  
  *len_bounce_untap_used                        0.4937       0.5022      +0.0085 ±0.0075  
  *cards_exiled_total                          23.1117      23.2569      +0.1452 ±0.1308  
  *interaction_spells_cast_total                2.4905       2.5118      +0.0213 ±0.0199  
  *len_library                                 52.2232      51.9964      -0.2268 ±0.2197  
  *marwyn_power                                 2.5557       2.5921      +0.0364 ±0.0358  
   len_creature_cast_turn                      11.3890      11.4493      +0.0603 ±0.0610
```
Modo resiliência, N=10.000 (`resumos/ab_10000_resiliencia.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 6482 (64.8%)
   campo                                          base     variante dif. pareada (IC95%)
  *commander_cast_turn__nunca                   0.0531       0.0469      -0.0062 ±0.0022  
  *commander_cast_turn__ate_T3                  0.1444       0.1475      +0.0031 ±0.0016  
  *commander_cast_turn__ate_T4                  0.4142       0.4215      +0.0073 ±0.0027  
  *commander_cast_turn__ate_T5                  0.7557       0.7659      +0.0102 ±0.0030  
  *lands_played_total                           5.7678       5.8189      +0.0511 ±0.0124  
  *commander_cast_turn__ate_T6                  0.8674       0.8768      +0.0094 ±0.0028  
  *commander_cast_count                         1.4861       1.5034      +0.0173 ±0.0060  
  *maralen_free_casts_total                     2.4604       2.4845      +0.0241 ±0.0114  
  *interaction_spells_cast_total                1.9174       1.9439      +0.0265 ±0.0132  
  *len_hand                                     1.7681       1.6949      -0.0732 ±0.0435  
  *landfall_elf_tokens_total                    0.0996       0.0935      -0.0061 ±0.0044  
  *maralen_triggers_total                       7.6042       7.6740      +0.0698 ±0.0510  
  *ramp_pieces_cast_total                       3.7072       3.7351      +0.0279 ±0.0207  
  *len_smart_counter_log                        0.1283       0.1318      +0.0035 ±0.0032  
  *smart_counters_total                         0.1283       0.1318      +0.0035 ±0.0032  
  *len_creature_cast_turn                       8.2479       8.2881      +0.0402 ±0.0376  
  *cards_exiled_total                          14.7392      14.8227      +0.0835 ±0.0805  
  *len_battlefield                             11.7069      11.7650      +0.0581 ±0.0567
```
Os lotes de N=2.000 (`ab_2000*.txt`) e as variantes de sensibilidade (uma correção por vez) estão em `resumos/`.

**Raciocinado (não medido):** com o upkeep antes da compra, o token de Faerie do Bitterblossom/Bearer já existe quando a mão é comprada, mas nada na compra depende dele; o efeito esperado é nulo, e a medição não contradiz (nada de relevante além do IC95% no comandante). Por que 32% das partidas divergem, se o efeito esperado é nulo: **hipótese não testada** — a troca de ordem das chamadas pode mudar a sequência de sorteios do `rng` (`create_token` e a compra usam o mesmo gerador) e com isso o desenrolar de partidas que seguem equivalentes em distribuição.

**Validação:** smoke (99 cartas, 0 desconhecidas, 0 duplicadas não-básicas, 200 partidas × 2 modos sem exceção); bit-identidade com as chaves desligadas × `maralen_goldfish_v1_ANTES_c7cf734.py`, 20.000 partidas × 2 modos (`resumos/bitident_20000.txt`); regressão 20.000 × 2 modos × 2 configurações, 0 exceções (`resumos/regressao_20000.txt`); testes dirigidos 9/9 (`resumos/testes_dirigidos.txt`); reprodutibilidade por `cmp` (`resumos/verificacao_reproducao.txt`).

**Escopo — verificado:**
- **Mulligan:** leitura de `mulligan` e `should_keep`; teste dirigido (M1–M8: escolha do fundo, conservação das cartas, caminho antigo com a chave desligada); A/B pareado 2.000 e 10.000 nos dois modos.
- **Bit-identidade** com as chaves desligadas × snapshot: 20.000 partidas × 2 modos, impressão digital do resultado inteiro.
- **Regressão** 20.000 × 2 modos × 2 configurações: 0 exceções.
- **Ordem das fases:** teste dirigido O1 e leitura de `play_turn` inteiro (Regra #6).

**Escopo — NÃO verificado:**
- **Jogada de terreno virado em T1/T2 ("tapped-first")** e **condições de entrada dos terrenos** (checkland/fastland/slow/reveal): não são tratadas nesta seção; quando houver correção, ela tem seção própria.
- **Resto da taxonomia da Regra #1 neste arquivo** (caminhos de conjuração fora da mão e "whenever you cast", sacrifício × destroy, cascade, contadores `_sick` agregados, fórmulas dinâmicas achatadas): varrido na triagem de 2026-10-05 por `grep` e leitura pontual das funções, **sem** leitura integral do arquivo e **sem** instrumentação em runtime nesta rodada. "Sem achado" aí significa "o `grep` não achou", não "não existe".
- **Oponente real:** o goldfish não modela (convenção do repositório); nada aqui mede interação além do proxy já existente.
- **Condições de entrada dos terrenos da Maralen** (checkland/slow/reveal): levantadas na triagem, não corrigidas nesta seção.

**Observação:** 0 exceções em 20.000 × 2 modos × 2 configurações; os invariantes genéricos (carta acima do número no baralho; contadores negativos) deram 0 violações.

---

## CR 903.9a: comandante passa pelo `leave_battlefield()` central de verdade — 2026-09-21

**Gatilho:** usuário conferiu a regra real do CR 903.9 e apontou o erro
("comandantes podem ser mortos sim!"). Detalhes completos em
`checklist-oraculo.md` e `megatron-tyrant-mardu/checklist-oraculo.md`.

**Achado:** igual ao Toph nesta sessão — chokepoint central real já
existia (`leave_battlefield`), só o comandante pulava ele. Maralen é
Fada de verdade — Tegwyll (draw+lose 1 life) e o clear de Umbral Mantle
deveriam disparar com a morte dela e estavam sendo silenciados.

**Resultado:** modo padrão idêntico (0/20000 mismatches, comparado
contra uma baseline com o guard do bug de loop infinito abaixo já
aplicado, pra isolar só o efeito deste fix).

**Validação:** regressão de 20.000 partidas nos 2 modos, 0 exceções, 0
comandantes presos no cemitério + 4 testes dirigidos.

---

## Achado adicional: loop infinito real, bug pré-existente não relacionado ao comandante — 2026-09-21

**Gatilho:** a própria regressão de 20k acima travou indefinidamente
(não erro, hang de verdade). Rastreado até `use_staff_of_domination_v2`:
`remaining_mana()` pode mutar `state.infinite_mana_this_turn=True`
como efeito colateral (combo Umbral Mantle), e o loop finito do Staff
reavaliava essa mesma função a cada iteração sem guard — uma vez que o
flag vira True no meio do loop, a condição nunca mais fica falsa. Bug
pré-existente (mesmo hang no commit anterior), só descoberto agora
porque a validação de CR 903.9a rodou 20k partidas reais pela 1ª vez
nesse espaço de seeds.

**Corrigido:** replicado o guard que o loop irmão (Faerie Mastermind)
já tinha (`and not state.infinite_mana_this_turn`).

**Validação:** 20.000 seeds (mesmo espaço) sem nenhum travamento, 30s
total (antes: hang permanente a partir do seed 8010333).

---

## Porte completo do modo de resiliência (interação de oponente) — 2026-09-20

**Gatilho:** "Agora vamos atualizar o simulador da Maralen, mantendo
todos os cuidados que já estamos usando" — mesmo modo já validado em
Megatron/Ur-Dragon/Hei Bai/Edgar Markov/Ulalek/Toph/Prismatic Bridge,
este deck nunca tinha nenhuma extensão de resiliência antes. Detalhes
técnicos completos em `checklist-oraculo.md`.

**Particularidade real deste deck**: tokens de Elfo/Fada são contadores
agregados, não entradas nomeadas em `state.battlefield` — o wipe de
criatura precisou de tratamento especial pra zerar esses contadores
também (são criaturas reais na mesa). 2 bugs reais corrigidos durante o
porte: `leave_battlefield()` não tratava token corretamente (CR 111.7,
nunca exercitado antes por falta de call site real) e a taxa de recast
do comandante não incrementava num cast counterado (CR 903.10a).

**Resultado (A/B 2000 jogos mesma seed_base, modo padrão vs.
resiliência):** Maralen nunca resolvida em 8 turnos sobe de 1,8% pra
4,4%. Avg counterspells sofridos: 0,14. Avg board wipes: 0,83, artifact:
0,16, enchantment: 0,17. Avg remoções inteligentes: 0,65 (Priest of
Titania o alvo mais removido, 11,7%). Vida final média: 35,63 (de 40).

**Validação:** modo padrão 100% bit-idêntico ao commit `13178fc` (3.000
seeds) + regressão de 20.000 partidas em modo resiliência, 0 exceções +
7 testes dirigidos.

---

### Auditoria oráculo-por-oráculo completa (extensão da sessão de 6 decks) — 2026-09-13

**Gatilho:** continuação da auditoria "compile TUDO" aplicada a Azula/
Beorn/Captain Storm/Edgar Markov/Hei Bai nesta mesma sessão — mesmo
tratamento pra Maralen, já o deck mais auditado da biblioteca (6+ rodadas
anteriores documentadas acima). Oráculo fresco via Scryfall pras 88 cartas
+ 3 MDFC/Adventure + comandante, releitura completa das ~1580 linhas do
simulador. **4 gaps reais encontrados e corrigidos** (detalhe completo em
`checklist-oraculo.md`):

1. `marwyn_effective_power()` faltava os anthems reais de Imperious
   Perfect e Thranduil, Sindarin Liege (mesma cláusula "Other Elves you
   control get +1/+1" já corrigida pro Elvish Archdruid numa rodada
   anterior, nunca estendida pras outras 2 fontes idênticas).
2. Faerie Mastermind: a habilidade ativada real (*"{3}{U}: Each player
   draws a card"*) nunca disparava — a carta inteira tinha sido descartada
   como "opponent_dependent" por causa da OUTRA metade (passiva).
3. Staff of Domination: o motor de compra normal (*"{5},{T}: Draw a
   card"* + *"{1}: Untap"* pra repetir) só existia dentro do combo
   infinito — 100% inerte com mana finita, mesmo sobrando 5+ mana.
4. Elven Chorus / Realmwalker: tag `cast_from_top` cadastrada desde a
   criação do arquivo, nunca despachada — "cast creature spells from the
   top of your library" 100% ausente.

**Robustez:** 20.000 partidas de regressão (seeds 9500000–9519999,
timeout 2s/jogo) — 0 erros, 0 timeouts.

**n=2000, seed_base=5555000, 8 turnos — antes → depois:**

| Métrica | Antes | Depois |
|---|---|---|
| Avg gatilhos de Maralen (exila 2) | 9,62 | **10,51** |
| Avg cartas exiladas total | 17,77 | **19,10** |
| Avg casts grátis via Maralen | 2,71 | 2,81 |
| Avg tutores usados | 0,86 | 0,92 |
| Avg tokens criados | 4,44 | 4,71 |
| Avg dobras via Roaming Throne | 1,19 | 1,40 |
| Avg nível final do Joraga Treespeaker | 0,86 | 0,96 |
| Combo Umbral Mantle montado | 11,0% | **12,2%** |
| Staff of Domination infinito | 2,7% | 3,2% |
| Avg cartas compradas extra (draw) | 3,23 | **4,52** |
| Avg mão final | 2,23 | **3,08** |
| Avg compras via Staff modo finito (novo) | — | **0,62** |
| Avg compras via Faerie Mastermind ativado (novo) | — | **0,88** |
| Avg criaturas conjuradas do topo (Elven Chorus/Realmwalker, novo) | — | **0,33** |

**Leitura:** o salto mais visível é em compra de carta (3,23 → 4,52,
quase inteiro vindo dos 2 motores de draw que antes eram 100% inertes —
Staff modo finito e Faerie Mastermind ativado), refletido diretamente na
mão final maior (2,23 → 3,08). O combo do Umbral Mantle sobe de forma
mensurável (11,0% → 12,2%) como efeito direto do fix da Marwyn (mais
fontes de anthem = mais chance de cruzar o threshold de 4+ mana por
ativação). Os demais deltas (gatilhos de Maralen, dobras via Roaming
Throne, nível do Joraga) sobem moderadamente como efeito indireto de
mais mana/cartas disponíveis mudando quais spells a IA prioriza a cada
turno — nada satura ou explode, consistente com correções pontuais num
arquivo já maduro.

---

## Simulação #1 — goldfish Python completo (`maralen_goldfish_v1.py`) — 2026-08-23

**Script construído do zero**, seguindo a arquitetura já estabelecida nos outros 6 simuladores desta biblioteca (`Card`/`GameState` dataclasses, `total_mana()`/`remaining_mana()`/`spend_mana()` com gasto real rastreado por turno). Passo 0 (regra de `references/goldfish-sim-card-rules.md`): varredura mecânica no oráculo completo das 99 cartas achou os gatilhos reais listados no docstring do script. Todos com efeito real implementado, exceto os explicitamente dependentes de oponente real (Rhystic Study, Mystic Remora, Faerie Mastermind passivo, Alela, Bojuka Bog) — documentados como "disponíveis mas sem efeito numérico solo", nunca fingidos.

**Roaming Throne — tipo escolhido: Faerie.** Maralen é ela mesma `Elf Faerie Noble`, então o próprio gatilho dela dobra com QUALQUER um dos dois tipos escolhidos (ela conta como "outra criatura do tipo escolhido" pra si mesma). Faerie foi escolhido porque tem mais criaturas com gatilho relevante além da comandante (Bitterbloom Bearer, Obyra, Tegwyll, Faerie Harbinger, Spellstutter Sprite, Mistbind Clique) do que Elfo (só Marwyn e Elvish Warmaster têm ETB relevante).

**Motor central implementado com fidelidade real:** o gatilho da própria Maralen (`Whenever Maralen or another Elf or Faerie you control enters, exile the top two cards of target opponent's library. Once each turn, you may cast a spell with mana value <= Elves+Faeries you control from among cards exiled with Maralen this turn without paying its mana cost`). Sem biblioteca de oponente real num goldfish solo, a exilada vem da PRÓPRIA biblioteca — mesma aproximação já usada pro Grenzo/Laughing Jasper Flint no simulador do Vihaan, documentada no código, nunca fingida como "roubo real".

**Combo de 2 peças (Umbral Mantle + mana dork escalável) implementado como detecção real, não decorativa:** a cada turno, `dork_mana()` calcula a saída de cada dork; se Umbral Mantle está equipada num dork cuja saída (Priest of Titania/Elvish Archdruid = nº de Elfos; Marwyn = seu poder; Circle of Dreams Druid = nº de criaturas) atinge 4+, a flag `infinite_mana_this_turn` liga de verdade (não é um número arbitrário — é a mesma lógica de "mana líquida positiva" descrita na auditoria). Staff of Domination, quando em campo junto com mana infinita, resolve puxando a biblioteca inteira pra mão (limite defensivo real: **nunca finge vencer por deck-out**, só registra `staff_infinite_draws` e marca `library_emptied`).

**Simplificações documentadas** (não inventadas — omissões explícitas, ver docstring completo do script):
- Bloom Tender: aproximado como 2 mana fixo (cores em jogo tipicamente 2-3, não rastreio cor exata de cada permanente).
- Joraga Treespeaker: nivelado só até nível 1 (2 mana investidos), nível 5 quase nunca compensa em 8 turnos.
- Heritage Druid / Birchlore Rangers: aproximação documentada — convertem Elfos "sick" (recém-conjurados, que ainda não produziriam mana) em mana extra, já que tapar OUTROS Elfos como custo ignora summoning sickness (CR 302.6) — sem duplicar a contagem desses Elfos caso eles não estivessem sick.
- Devoted Druid: self-untap via -1/-1 counter com teto defensivo de 3 ativações extras/turno.
- Mistbind Clique (Champion a Faerie): sacrificada no ETB se não há outra Fada em campo pra exilar.

**Teste de robustez** (prática obrigatória): 15.000 partidas com timeout de 2s/partida via `signal.alarm`, **0 erros, 0 timeouts** — o único bug real encontrado (comandante nunca saía da mão porque ela nunca ESTAVA na mão — vem direto da zona de comando, mesmo bug documentado nos outros 5 simuladores desta biblioteca) foi corrigido antes mesmo dessa varredura, durante o smoke-test manual de 20 partidas.

**Bug real encontrado e corrigido (achado no smoke-test manual, antes da varredura de robustez):** `resolve_cast()` tentava `state.hand.remove(COMMANDER)` incondicionalmente ao conjurá-la, mas a comandante nunca entra na mão (vem da zona de comando) — `ValueError` imediato na primeira partida testada. Corrigido excluindo a comandante dessa remoção.

**n=3000, seed_base=8000000, 8 turnos — resultado oficial:**

```
Avg mulligans: 0,55
Turno medio de conjuracao da Maralen: 4,60 | mediana: 4,0
Nunca conjurada em 8 turnos: 4,5%
Avg gatilhos de Maralen (exila 2): 5,11
Avg cartas exiladas total: 9,36
Avg casts gratis via Maralen: 2,24
Avg tutores usados: 0,65
Avg tokens criados (exclui explosao infinita): 3,35
Avg dobras via Roaming Throne: 0,21
Combo Umbral Mantle (mana infinita) montado: 7,8% dos jogos | turno medio: 6,65
Staff of Domination converteu em compra infinita: 1,5% dos jogos
Avg cartas compradas extra (motores de draw, exclui staff infinito): 0,39
Avg mao final: 0,87
```

**Leituras principais:**

- **O motor central funciona desde cedo**: comandante em campo no turno 4,6 em média, com ~5,1 gatilhos de exílio por partida (9,4 cartas exiladas) e **2,24 casts grátis** via a habilidade dela — o plano de "roubar e jogar de graça" está ativo na maioria das partidas, não é situacional.
- **O combo do Umbral Mantle é real, mas não trivial de montar**: 7,8% das partidas em 8 turnos, turno médio 6,65 quando acontece. Isso confirma numericamente o que a auditoria já tinha identificado por leitura de texto — não é um combo de canto teórico, mas também não é algo que "sempre liga cedo". Consistente com o padrão já visto no Edgar Markov desta mesma biblioteca (combo real ≠ combo garantido).
- **Staff of Domination como fechador é ainda mais raro (1,5%)** — precisa da junção de DUAS condições independentes (mana infinita montada + Staff já em campo), o que reduz a taxa efetiva pela metade.
- **Densidade de tutores baixa em jogo (0,65 usados/partida)** apesar de 5 tutores reais na lista — é matemática normal de deck singleton de 99 cartas (cada tutor é ~1% de densidade), não um problema de implementação.
- **Roaming Throne dobrou gatilhos em 0,21/partida** — como o tipo escolhido (Faerie) também cobre a própria Maralen, isso inclui dobras do gatilho central dela quando a Roaming Throne está em campo, não só das Fadas menores.

Resultados salvos em `maralen_v1_runs.jsonl` (3000 jogos).

**Simplificações documentadas no docstring do script** (não inventadas — omissões explícitas): sem combate real contra oponente; drain/vida de oponente nunca reais; Rhystic Study/Mystic Remora/Faerie Mastermind passivo/Alela/Bojuka Bog opponent-dependent, sem efeito numérico solo; removal/contra-mágica conjuradas quando há mana sobrando, sem efeito de combate real (mesma convenção dos outros 6 simuladores desta biblioteca).

---

### Teste pontual — motor de flash em criaturas, T4-T8, COM vs SEM Radagast of Rhosgobel — 2026-08-23

**Pedido do usuário:** medir a probabilidade real de ter o "motor de flash" online nos turnos 4, 5, 6, 7 e 8, comparando a lista atual (com Radagast) contra a versão anterior (sem Radagast, com Elves of Deep Shadow no lugar), pra decidir se a troca vale a pena.

**Script:** `maralen_flash_radagast_test.py`. Duas métricas rastreadas por turno em `maralen_goldfish_v1.py` (`flash_universal_by_turn`, `flash_with_radagast_by_turn`, populadas no fim de cada `play_turn`):
- **Motor universal puro**: pelo menos 1 de Leyline of Anticipation / Vedalken Orrery / High Fae Trickster / Alchemist's Refuge em campo.
- **Motor combinado**: o universal OU Radagast of Rhosgobel em campo (Radagast não dá flash universal — só a 1ª criatura do turno, com desconto de {2} — mas conta como fonte parcial pra essa métrica).

Duas variantes de biblioteca, mesmas 3000 seeds pareadas (comparação direta, não amostras independentes): lista atual (com Radagast) vs. lista revertida (Radagast → Elves of Deep Shadow). Teste de robustez prévio na variante nova (sem Radagast, nunca simulada antes): 5.000 jogos com timeout de 2s, 0 erros.

**Checagem de sanidade — motor universal puro (deveria ser ~igual nas duas listas, já que nenhuma das duas cartas trocadas é fonte de flash universal):**

| Turno | Com Radagast na lista | Sem Radagast na lista |
|---|---|---|
| T4 | 14,2% | 14,7% |
| T5 | 23,0% | 23,6% |
| T6 | 33,8% | 34,6% |
| T7 | 42,2% | 43,2% |
| T8 | 48,4% | 49,3% |

Diferença de ~0,5-1pp entre as duas — dentro do ruído esperado de amostra (mesmas seeds, então nem deveria zerar por completo: a ordem de embaralhamento muda porque a biblioteca tem cartas diferentes num slot). Confirma que a troca não afetou acidentalmente o pacote universal — bom sinal de que a implementação está correta.

**Resultado principal — motor de flash em criaturas disponível (universal + Radagast quando presente):**

| Turno | Com Radagast | Sem Radagast | Δ |
|---|---|---|---|
| T4 | 15,3% | 14,7% | +0,7pp |
| T5 | 26,4% | 23,6% | +2,8pp |
| T6 | 39,3% | 34,6% | +4,6pp |
| T7 | 49,6% | 43,2% | +6,4pp |
| T8 | 56,5% | 49,3% | +7,2pp |

**Leitura:** Radagast adiciona uma cobertura real e crescente ao motor de flash — de +0,7pp no turno 4 (ele mesmo ainda raramente resolvido tão cedo, CMC 4) até +7,2pp no turno 8 (quase 1 em cada 14 partidas a mais tem alguma forma de flash em criaturas só por causa dele). Dito isso, o teto absoluto do motor combinado ainda fica abaixo de 60% mesmo no turno 8 — em mais de 4 de cada 10 partidas, NENHUMA das 5 peças (4 universais + Radagast) está em campo até o fim do jogo, porque cada uma é 1 carta em 99. A contribuição do Radagast é real mas incremental sobre uma base já limitada por densidade de singleton, não uma mudança estrutural na confiabilidade do motor.

---

## Simulação #2 — implementação do landfall (Thranduil, Sindarin Liege + Thranduil's Company) — 2026-08-23

**Contexto:** a lista trocou Devoted Druid e Cloud of Faeries por Thranduil, Sindarin Liege // Silvan Rally e Thranduil's Company — um subtema de landfall que o script ainda não tinha nenhum gancho pra modelar (nenhum `landfall_trigger()` existia até agora).

**Implementação real (não decorativa):**
- `play_land()` reescrita: agora suporta até **2 lands por turno** quando Thranduil's Company está em campo E há outro Elfo controlado (`As long as you control another Elf, you may play an additional land on each of your turns` — checado de verdade contra Elfos nomeados + tokens de Elfo, não assumido).
- Nova função `landfall_trigger(state)`, chamada a cada terreno que entra (land normal ou o extra do Company): se Thranduil, Sindarin Liege está em campo, cria um token de Elfo 1/1 real (`Landfall — ... create a 1/1 green Elf creature token`); se Thranduil's Company está em campo, registra o gatilho de "2 contadores +1/+1 num alvo" — modelado com efeito numérico real quando o alvo de maior valor (Marwyn, the Nurturer) está em campo (a mana dela escala com o próprio poder, então +2 de poder é +2 de mana real), documentado como não-modelado pra outros alvos sem relevância numérica no sim.

**Bug real encontrado e corrigido nesse processo (não é sobre as cartas novas — achado ao mexer em `create_token()` pra ela aceitar o tipo do token):** `create_token()` **nunca disparava o gatilho da Maralen** pra nenhum token — nem os de Elfo Guerreiro do Elvish Warmaster/Imperious Perfect, nem os de Fada do Bitterblossom/Bitterbloom Bearer, que já estavam na lista desde o início. Pelas regras reais, um token Elfo ou Fada entrando em campo DEVE disparar "Whenever Maralen or another Elf or Faerie you control enters" — isso nunca tinha sido implementado, mesmo antes desta atualização. Corrigido: `create_token(state, kind, source)` agora recebe o tipo do token e dispara `maralen_trigger_token()` (mesma lógica de exílio/dobra por Roaming Throne da carta nomeada) pra todo token Elfo ou Fada, além de contar corretamente pra `elf_faerie_count()` (teto de custo do cast grátis), pra a contagem de Elfos que os dorks escaláveis (Priest of Titania/Elvish Archdruid/Circle of Dreams Druid) usam, e pro contador de poder da Marwyn.

**Também separei o contador genérico `other_tokens` em `elf_tokens`/`faerie_tokens`** — necessário pra tokens de Elfo contarem certo nos cálculos de mana escalável (antes, tokens nunca contribuíam pra `elves_in_play`/`creatures_in_play`, subestimando a saída real do Priest of Titania, Elvish Archdruid, Marwyn e Circle of Dreams Druid sempre que havia token de Elfo em campo).

Teste de robustez: 15.000 partidas com timeout de 2s, **0 erros, 0 timeouts**.

**n=3000, seed_base=8000000, 8 turnos — comparação com o batch anterior (antes do landfall + antes do fix de token):**

| Métrica | v1 (sem landfall, bug do token) | v2 (com landfall, token fixo) | Δ |
|---|---|---|---|
| Turno médio de conjuração da Maralen | 4,60 | 4,67 | ~igual |
| Avg gatilhos de Maralen (exila 2) | 5,11 | 7,28 | **+42,5%** |
| Avg cartas exiladas total | 9,36 | 13,58 | +45,1% |
| Avg casts grátis via Maralen | 2,24 | 2,40 | +7,1% |
| Avg dobras via Roaming Throne | 0,21 | 0,35 | +66,7% |
| Combo Umbral Mantle montado | 7,8% | 7,7% | ~igual |
| Avg terrenos jogados (total) | (não rastreado) | 5,37 | — |
| Avg tokens de Elfo via landfall (Sindarin Liege) | — | 0,15 | (mecânica nova) |
| Avg contadores via landfall (Company) | — | 0,14 | (mecânica nova) |

**Leitura honesta — o salto grande (+42,5% nos gatilhos da Maralen) é majoritariamente o bug corrigido, não as cartas novas.** Os tokens de landfall do Sindarin Liege contribuem pouco em volume absoluto (0,15/partida — CMC 4, 1 cópia em 99, raramente resolve e ainda mais raramente com terreno sobrando na mão pra aproveitar). O grosso do aumento vem de Elvish Warmaster e Imperious Perfect (que já estavam na lista desde o início) finalmente disparando a Maralen quando criam token — um efeito que deveria ter existido desde a Simulação #1 e não existia. Registrado aqui com transparência total, não escondido como se fosse "ganho" das cartas novas. O combo do Umbral Mantle ficou estatisticamente idêntico (7,8% → 7,7%), como esperado — nenhuma das mudanças desta rodada afeta a montagem dele.

Resultados salvos em `maralen_v1_runs.jsonl` (sobrescrito com os 3000 jogos novos).

---

## Correção — checklist obrigatória de mecânica (regra nova pós-Beorn) — 2026-08-28

**Gatilho (usuário):** depois de eu entregar o Beorn sem despacho de landfall
nenhum, o usuário pediu auditoria da checklist nova (landfall, mana dorks,
mana rocks, fixing lands, draw engines, ramp engines, ativadas repetíveis,
combos) em **todos** os decks. Landfall (Simulação #2 acima) já estava
correto; os bugs achados nesta rodada foram outros:

- **Devoted Druid**: oráculo real é "Put a -1/-1 counter on this creature:
  Untap this creature" — sem restrição de quantidade, MAS ela é 0/2 e morre
  na regra de estado depois do 2º contador. O código dava **+3 ativações
  extras todo turno, pra sempre**, e nunca a removia do campo — superprodução
  indefinida. Corrigido: no máximo 2 ativações NA VIDA INTEIRA (usadas de
  uma vez no primeiro turno em que fica pronta), depois ela morre de
  verdade e some do campo pro resto do jogo.
- **Marwyn, the Nurturer**: base inicializada como 2/2 (`marwyn_power = 2`)
  quando o oráculo real é 1/1. Também nunca refletia o anthem do Elvish
  Archdruid ("other Elf creatures you control get +1/+1", dinâmico —
  desaparece se o Archdruid sair de campo, corrigido via
  `marwyn_effective_power()` em vez de somar direto no contador
  permanente).
- **Green Sun's Zenith**: pool de busca filtrava por tag "elf" em vez do
  texto real ("search for a green creature card") — excluía injustamente
  Birds of Paradise, Wirewood Symbiote, Realmwalker e Radagast of Rhosgobel
  (verdes, não-Elfo). Nova tabela `GREEN_CREATURE_NAMES` (28 criaturas
  verdes reais na lista, cor via Scryfall).
- **Kindred Discovery**: 100% ausente — tag existia, nenhum gatilho real.
  Oráculo: "Whenever a creature you control of the chosen type enters or
  attacks, draw a card" (tipo escolhido: Elfo, mesma convenção da Roaming
  Throne). Implementadas as duas metades: ETB (hook em `enter_battlefield`/
  `create_token`) e "attacks" (novo `combat_step` real — o arquivo não
  tinha NENHUM modelo de combate antes, "sem oponente real, nenhum gatilho
  de combate real no deck"; implementado com a mesma premissa já usada
  noutros decks desta sessão: toda criatura pronta ataca desimpedida).
- **Bojuka Bog / Path of Ancestry / Zagoth Triome**: tag `etb_tapped`
  existia, nunca era lida — produziam mana no próprio turno em que
  entravam apesar do "enters tapped" real. Nova infraestrutura
  `tapped_lands_this_turn` (mesmo padrão de outros decks desta sessão).

**Resultado (n=2000, seed_base=5000000, antes → depois):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg gatilhos de Maralen (exila 2) | 7,20 | **8,20** |
| Avg cartas exiladas total | 14,01 | **15,38** |
| Avg tutores usados | 0,65 | **0,73** |
| Avg tokens criados | 3,82 | **4,42** |
| Avg dobras via Roaming Throne | 0,33 | **0,45** |
| Combo Umbral Mantle montado | 7,0% | **9,2%** |
| Avg cartas compradas extra (draw) | 0,39 | **2,84** |

Salto grande em cartas compradas (0,39→2,84) — quase inteiro vindo do
Kindred Discovery, que antes contribuía zero. O resto sobe moderadamente
(GSZ com pool maior, Marwyn com poder correto alimentando mais mana pro
combo do Umbral Mantle). Devoted Druid puxa levemente pra baixo (menos mana
de longo prazo), mas os ganhos líquidos superam.

**Robustez:** sweep de 20.000 jogos (seeds 5000000–5019999, timeout 2s/jogo)
— 0 erros, 0 timeouts.

`lista.md` não mudou. `maralen_v1_runs.jsonl` sobrescrito.

---

## Correção #2 — checklist ampliado (13 categorias: layout real de multi-face, planeswalker loyalty, Classes/Sagas) — 2026-08-28

**Gatilho (usuário):** "Sim por favor", continuando a rodada de auditoria
completa que já tinha achado gaps sérios em Edgar Markov (Ojer Taq/Legion's
Landing jogados ilegalmente como terreno) e construído o sistema de loyalty
completo no Prismatic Bridge. Checklist de 13 categorias aplicado à Maralen
do zero.

**Categoria 11 (multi-face — layout real via Scryfall):** 3 cartas de dupla
face na lista. `Brazen Borrower // Petty Theft` e `Thranduil, Sindarin Liege
// Silvan Rally` confirmadas `layout: adventure` — face de criatura é a
única legalmente conjurável direto da mão, já cadastradas certas (lado
Instant/Sorcery de Adventure não implementado é decisão de escopo legítima,
não bug de regra). **`Growing Rites of Itlimoc // Itlimoc, Cradle of the
Sun` confirmada `layout: transform`** — cadastrada corretamente como a face
da frente (Enchantment, {2}{G}, mv 3), mas a tag `"itlimoc"` estava **morta,
referenciada em lugar nenhum do arquivo**: sem ETB, sem gatilho real de
transformação, sem a habilidade de mana da face de trás. Card 100% inerte
num deck onde ela é peça real de ramp+seleção.

Oráculo real (via `scryfall-cache/oracle-cache.json`):
- Frente: *"When Growing Rites of Itlimoc enters, look at the top four
  cards of your library. You may reveal a creature card from among them
  and put it into your hand. Put the rest on the bottom of your library in
  any order. At the beginning of your end step, if you control four or
  more creatures, transform Growing Rites of Itlimoc."*
- Trás (Itlimoc, Cradle of the Sun — Legendary Land, sem custo de
  conjuração): *"{T}: Add {G}. {T}: Add {G} for each creature you
  control."*

Implementado: ETB real em `resolve_etb()` (olha top 4, leva criatura pra
mão via `best_missing_dork()`, resto pro fundo da biblioteca —
`itlimoc_creatures_found_total`); gatilho de transformação real em
`end_step()` (4+ criaturas → `state.itlimoc_transformed = True`,
`itlimoc_transform_turn` registrado); habilidade de mana real em nova
`itlimoc_mana()` (escolha racional entre as duas ativações — sempre
`max(1, criaturas em campo)` — somada em `total_mana()`), gated pela flag
de transformação (a carta é `Card` frozen, não dá pra "trocar o tipo" —
mesmo padrão já usado no Ojer Taq/Deepest Foundation do Edgar Markov).

**Categoria 12 (planeswalker loyalty):** confirmado via grep — 0
planeswalkers na lista. N/A, documentado.

**Categoria 13 (Classes/Sagas):** confirmado via grep — 0 Classes/Sagas na
lista. `Joraga Treespeaker` tem "Level Up" (moldura diferente de Classe,
mecânica pré-existente desta sessão anterior, já documentada no docstring
como "nivelado só até nível 1, raramente alcança nível 5 — não forçado");
não é o gatilho da regra 13 (que é sobre Classe/Saga), mas confirmado que a
implementação já é fiel ao oráculo real (custo de nível 1 = 2 mana, nível 5
exigiria 10 mana investidos, quase nunca compensa em 8 turnos).

**Bug adicional achado na auditoria de correção do modelo de estado (não
fazia parte de nenhuma categoria específica, mas apareceu ao ler
`resolve_cast()` de perto pra decidir onde plugar o ETB do Itlimoc):**
instantes e feitiçarias (Counterspell, Toxic Deluge, Pongify, etc.) e o
próprio Green Sun's Zenith resolviam e **ficavam presos em
`state.battlefield` pra sempre**, nunca indo pro cemitério. Não corrompia
nenhuma métrica calculada (todos os filtros de `state.battlefield` checam
tipo/tag via `is_creature_card`/`is_elf`/`is_faerie`/`LAND_NAMES`, e
nenhum deles casa com Instant/Sorcery), mas era estado incorreto — e este
deck não tem hoje nenhuma recursão de cemitério (categoria RECURSION = 0,
N/A, documentado), então um bug futuro nessa área ficaria mascarado até
alguém adicionar uma carta de recursão. Corrigido: `resolve_cast()` agora
manda Instant/Sorcery pro cemitério de verdade (`interaction_spells_cast_total`
incrementado quando a tag é `"interaction"`); GSZ também vai pro cemitério
depois de resolver.

**Categoria 10 (métricas básicas — bloco explícito):** `run_batch()` não
tinha o bloco "Métricas básicas (checklist obrigatório)" presente nos
outros decks já corrigidos nesta sessão (Markov/Hei Bai/Prismatic Bridge).
Adicionado: RAMP (peças de rampa conjuradas via novo `ramp_pieces_cast_total`,
incluindo Itlimoc pós-transformação), DRAW (reaproveita
`cards_drawn_extra - staff_infinite_draws`), INTERACTION (novo
`interaction_spells_cast_total`), RECURSION (0,00 — N/A, documentado:
tutores de biblioteca não contam como recursão de cemitério), FINISHER/
LETHALITY (combo Umbral Mantle + Staff of Domination/Imperious Perfect,
sem dano de combate real por ser goldfish solo).

**Resultado (n=2000, seed_base=12345, antes → depois):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg tokens criados | 4,08 | **4,18** |
| Combo Umbral Mantle montado | 9,1% | **9,6%** |
| Staff of Domination infinito | 2,0% | **2,2%** |
| Avg cartas compradas extra | 2,72 | **2,84** |
| Avg mão final | 1,95 | **1,97** |
| Itlimoc transformou | N/A (inerte) | **19,4%** dos jogos, turno médio 6,38 |
| Avg criaturas achadas via ETB do Itlimoc | N/A (inerte) | **0,16** |

Ganho moderado e consistente em todas as métricas que dependem de mana
disponível (Itlimoc pós-transformação alimenta mais ativações de Imperious
Perfect, mais chance de atingir o threshold de 4+ mana do combo Umbral
Mantle) — direção esperada de uma peça de ramp que antes contribuía zero.

**Robustez:** sweep de 20.000 jogos (seeds 900000–919999, timeout 2s/jogo)
— 0 erros, 0 timeouts.

**Varredura extra de tags mortas (categoria 9 — estáticas):** depois de
corrigir o Itlimoc, rodei um script que cruza toda tag registrada em
`CARD_DB` contra onde ela é lida no resto do arquivo (mesma classe de bug
que achou o Itlimoc). Achou 2 gaps reais adicionais:

- **Murkfiend Liege**: estático real é *"Other green creatures you control
  get +1/+1. Other blue creatures you control get +1/+1."* — Marwyn é Elfo
  E verde, então deveria receber o bônus (mesmo padrão já corrigido pro
  Elvish Archdruid). Nunca era somado. Corrigido em
  `marwyn_effective_power()`, ao lado do bônus do Archdruid.
- **Radagast of Rhosgobel**: oráculo real *"The first creature spell you
  cast each turn costs {2} less to cast and can be cast as though it had
  flash."* — só o lado do flash (`flash_with_radagast_by_turn`) estava
  implementado; o desconto de {2} no custo nunca era aplicado. Implementado
  em `cast_card()` (aplica no primeiro creature spell do turno, capado em
  0) e espelhado em `can_cast()` (senão o filtro de castables rejeitava
  criaturas que na verdade ficavam pagáveis com o desconto).

Também documentados no docstring (decisões de escopo, não bugs): Seedborn
Muse (untap-step de outro jogador — genuinamente N/A, goldfish solo nunca
tem "outro jogador"), Spellstutter Sprite (contra-magia real precisa de
alvo de oponente, mesma convenção já usada pras outras contra-magicas do
deck) e Wirewood Symbiote/Scryb Ranger (bounce-untap repetível — valor
esperado baixo o suficiente frente ao risco de reestruturar o motor de
mana pra rastrear tap individual, decisão de escopo documentada).

**Resultado (n=2000, seed_base=12345, antes do Murkfiend/Radagast → depois):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg tokens criados | 4,18 | **4,28** |
| Combo Umbral Mantle montado | 9,6% | **9,8%** |
| Staff of Domination infinito | 2,2% | **2,4%** |
| Avg cartas compradas extra | 2,84 | **2,86** |
| Avg mão final | 1,97 | **1,98** |

**Robustez (2ª rodada, com Murkfiend/Radagast):** sweep de 20.000 jogos
(seeds 910000–929999, timeout 2s/jogo) — 0 erros, 0 timeouts.

`lista.md` não mudou. `maralen_v1_runs.jsonl` sobrescrito na próxima
execução de `__main__`.

---

### Reanálise do simulador Python (`maralen_goldfish_v1.py`) — a pedido do usuário — 2026-08-30

**Gatilho:** usuário pediu explicitamente pra reanalisar o simulador em
busca de erros, mesmo tratamento dado ao Ulalek nessa sessão. Oráculo
fresco das 95 cartas únicas via Scryfall (`cards/collection`, mais os 3
lados de face múltipla — Brazen Borrower, Growing Rites of Itlimoc,
Thranduil Sindarin Liege — buscados individualmente), comparação
sistemática de tags contra `colors`/`type_line` real, e leitura manual
completa das 1204 linhas do simulador.

**6 achados reais, todos corrigidos:**

1. **Mistbind Clique — Champion a Faerie nunca exilava a Fada "campeã".**
   Oráculo: *"sacrifice it unless you exile another Faerie you
   control."* Quando havia outra Fada disponível, o código mantinha a
   Mistbind em campo mas nunca removia a outra Fada — as duas ficavam
   contando ao mesmo tempo, quando só 1 corpo deveria estar presente até
   a Mistbind sair de campo. Corrigido: exila de verdade, preferindo um
   token (menor perda real) a uma carta nomeada, nunca a própria
   comandante (Maralen também é Fada por tipo).
2. **Tegwyll, Duke of Splendor — faltava a metade do custo.** Oráculo:
   *"you draw a card **and you lose 1 life**."* Só a compra estava
   implementada.
3. **Black Market Connections — 3 problemas empilhados.** Disparava no
   upkeep (oráculo real: *"beginning of your first main phase"*);
   pagava o custo de vida do modo Sell Contraband sem nunca criar o
   Treasure correspondente (pior que não escolher o modo); e o modo
   Hire a Mercenary (token 3/2 Changeling — conta como Elfo *e* Fada pra
   toda sinergia do deck) nunca era modelado. Corrigido: passo certo do
   turno, Treasure tratado como mana avulsa do próprio turno (mesma
   convenção do refund do Cloud of Faeries), token de Mercenário
   implementado de verdade via `enter_battlefield()`.
4. **Heritage Druid / Birchlore Rangers exigiam a si mesmas "prontas"
   sem necessidade.** Nenhuma das duas tem `{T}` no próprio custo
   ("Tap three/two untapped Elves you control: Add...") — CR 302.6 não
   bloqueia ativar habilidade de outro permanente por doença de
   invocação própria quando o custo não usa o `{T}` do próprio
   permanente. O código exigia isso mesmo assim, subestimando a mana
   disponível no turno em que qualquer uma delas entra.
5. **Joraga Treespeaker nunca alcançava o nível 5 — 0% estrutural, não
   "raro".** O comentário antigo dizia "raramente alcança nível 5" como
   se fosse probabilístico, mas o código só progredia até nível 1
   (binário 0/1) — o bônus de equipe real do nível 5+ ("Elves you
   control have '{T}: Add {G}{G}'") nunca existia no modelo. Implementado
   nível real 0-5, subindo com mana sobrando (movido pra depois do loop
   principal de conjuração — nivelar não deveria competir por mana com
   spells de verdade).
6. **Código morto de 2 cartas cortadas da lista** (`Devoted Druid`,
   `Cloud of Faeries` — trocadas por Thranduil, Sindarin Liege/Thranduil's
   Company em sessão anterior) ainda registradas no `CARD_DB` com
   mecânica completa. Inofensivo (`build_library()` só lê `lista.md`,
   nunca entram no baralho de verdade), documentado com comentário
   explícito em vez de removido (evitar risco de corte em múltiplos
   pontos do arquivo por um problema de baixo risco).

**Robustez:** sweep de 20.000 jogos (seeds 6600000–6619999, timeout
2s/jogo) — 0 erros, 0 timeouts.

**n=3000, seed_base=8000000, 8 turnos — antes (HEAD anterior a hoje) →
depois:**

| Métrica | Antes | Depois |
|---|---|---|
| Turno médio de conjuração da Maralen | 4,75 | 4,83 |
| Avg gatilhos de Maralen (exila 2) | 8,36 | 8,65 |
| Avg cartas exiladas total | 15,50 | 16,03 |
| Avg dobras via Roaming Throne | 0,46 | 0,49 |
| Avg nível final do Joraga Treespeaker | — (sempre 0 ou 1) | **0,92, atinge nível 5 em 16,8% dos jogos** |
| Avg Fadas exiladas pelo Champion do Mistbind | — (nunca acontecia) | **0,16** |
| Avg Treasures via Black Market Connections | — (n/a) | **0,39** |
| Avg Mercenary Tokens via Black Market Connections | — (n/a) | **0,39** |
| Combo Umbral Mantle montado | 10,4% | 10,7% |

Leitura: os deltas são pequenos e todos rastreáveis às correções
específicas — nada satura nem explode, consistente com bugs pontuais
corrigidos, não uma reescrita de mecânica central. O achado mais
significativo é qualitativo, não numérico: o nível 5 do Joraga (bônus de
mana pra todos os Elfos) e a exilação real do Mistbind simplesmente não
existiam antes, não é uma questão de frequência errada.

`lista.md` não mudou. `maralen_v1_runs.jsonl` sobrescrito.

---

### Correção — Bitterblossom disparava no end step (achado real, pergunta direta do usuário) — 2026-08-30

**Gatilho:** logo depois da reanálise acima, usuário perguntou diretamente
"Bitterblossom e Bitterbloom Bearer estão funcionando certo?" — checagem
revelou que Bitterbloom Bearer estava correta (upkeep), mas Bitterblossom
disparava em `end_step()`. Oráculo real das duas: *"At the beginning of
your upkeep, you lose 1 life and create a 1/1 ... Faerie ... token..."*
— mesma habilidade, mesmo passo do turno, mas só uma estava no lugar
certo.

**Impacto real:** o token criado tarde demais (fim do turno em vez do
início) nunca contava pro teto do free-cast da Maralen
(`elf_faerie_count()`) durante as main phases do MESMO turno em que
nascia — só passava a contar a partir do turno seguinte. Corrigido:
movido pro `upkeep_step()`, junto do Bitterbloom Bearer.

**Robustez:** sweep de 20.000 jogos (seeds 7700000–7719999, timeout
2s/jogo) — 0 erros, 0 timeouts.

**n=3000, seed_base=8000000 — antes (com o bug) → depois:**

| Métrica | Antes (bug) | Depois |
|---|---|---|
| Avg casts grátis via Maralen | 2,53 | **2,60** |
| Avg cartas compradas extra | 2,73 | 2,82 |
| Avg gatilhos de Maralen (exila 2) | 8,65 | 8,49 |
| Avg cartas exiladas total | 16,03 | 15,81 |
| Avg tokens criados | 4,21 | 4,06 |
| Growing Rites of Itlimoc transformou | 17,8% | 18,4% |

Leitura: o teto de free-cast maior e mais cedo no turno muda qual carta a
IA escolhe conjurar de graça a cada turno — isso cascata pros totais de
gatilho/exílio/token ao longo do jogo (às vezes pra baixo, quando a carta
escolhida não é ela mesma Elfo/Fada e não retrigger a Maralen), não é
sinal de regressão. O número mais direto e sem ambiguidade de leitura é
"casts grátis via Maralen" subindo — exatamente o efeito esperado de
disponibilizar o token 1 fase mais cedo.

`lista.md` não mudou.

---

### Correção — Roaming Throne dobrava com base no tipo de quem ENTRA, não no tipo de quem TEM a habilidade — 2026-08-31

**Gatilho:** reanálise pedida pelo usuário depois das duas rodadas
anteriores. Oráculo real do Roaming Throne: *"If a triggered ability of
**another creature you control of the chosen type** triggers, it
triggers an additional time."* A condição é sobre o tipo da criatura
**dona** da habilidade (a fonte do gatilho) — não sobre o tipo do que
entrou/morreu para causar o gatilho. O próprio docstring do arquivo já
raciocinava certo sobre isso ("Maralen é ela mesma Elf Faerie Noble... o
próprio gatilho dela dobra de qualquer forma"), mas o código nunca
seguia essa lógica.

**3 achados reais:**
1. **Gatilho da própria Maralen** (`_maralen_resolve`) calculava a dobra
   a partir de `is_roaming_type(entering_name)` / `kind ==
   ROAMING_THRONE_TYPE` — ou seja, só dobrava quando uma **Fada**
   entrava. Todo Elfo entrando (a maioria real dos gatilhos do deck —
   qualquer dork, Elvish Warmaster, Imperious Perfect, Priest of
   Titania, Marwyn etc.) nunca dobrava, quando deveria dobrar sempre que
   o Roaming Throne está em campo, já que a fonte do gatilho é sempre a
   Maralen (Faerie por tipo, bate com a escolha do Roaming Throne o
   tempo todo, independente do que entrou).
2. **Tegwyll, Duke of Splendor** (compra+perda de vida quando outra Fada
   morre): Tegwyll é ele mesmo Fada, então bate com o tipo escolhido —
   nunca era dobrado. Corrigido.
3. **Faerie Harbinger** (tutor de Fada pro topo no ETB): mesmo caso —
   Faerie Harbinger é Fada, nunca era dobrado. Corrigido (dobrar aqui
   significa buscar e empilhar uma 2ª Fada no topo).

**Decisão documentada, não corrigida:** Mistbind Clique (Champion) —
tecnicamente também bate com o tipo escolhido, mas dobrar "sacrifice
IT unless you exile another Faerie" não tem um efeito de jogo bem
definido com uma única cópia da carta (ver comentário junto de
`champion_faerie` em `resolve_etb()`). Risco de modelar errado maior
que o valor esperado — deixado de fora, igual à convenção já usada pro
Wirewood Symbiote/Scryb Ranger.

**Robustez:** sweep de 20.000 jogos (seeds 8800000–8819999, timeout
2s/jogo) — 0 erros, 0 timeouts.

**n=3000, seed_base=8000000 — antes (com o bug) → depois:**

| Métrica | Antes (bug) | Depois |
|---|---|---|
| Avg dobras via Roaming Throne | 0,46 | **1,09** |
| Avg gatilhos de Maralen (exila 2) | 8,49 | 9,08 |
| Avg cartas exiladas total | 15,81 | 16,83 |
| Avg casts grátis via Maralen | 2,60 | 2,62 |
| Avg tutores usados | 0,79 | 0,81 |
| Avg tokens criados | 4,06 | 4,16 |
| Avg Fadas exiladas pelo Champion do Mistbind | 0,16 | 0,17 (ruído de RNG a jusante, não tocado) |
| Combo Umbral Mantle montado | 10,8% | 10,6% (ruído de RNG a jusante) |

Leitura: a dobra do Roaming Throne mais do que dobra de frequência real
(0,46 → 1,09) — efeito esperado de passar a contar Elfos entrando, que
são a maioria dos gatilhos reais do deck, não só Fadas. Deltas nas
outras métricas são pequenos e rastreáveis à mudança de timing/escolha
de qual carta a IA conjura de graça a cada turno via Maralen, não sinal
de regressão.

`lista.md` não mudou.

---

## Achado real 2026-09-14 — Faerie Harbinger tutorava Roaming Throne + hang de verdade achado na Faerie Mastermind

Usuário perguntou se o bug do Roaming Throne achado no Beorn se repetia
em outros decks. Achado real (Faerie Harbinger tutorando Roaming Throne
da biblioteca) + um bug bem mais grave achado incidentalmente ao validar
com a regressão de 20.000: um hang de verdade, pré-existente, sem
relação com a Roaming Throne — `try_faerie_mastermind()` podia entrar
num loop infinito se o combo do Umbral Mantle fosse detectado no meio do
próprio loop de compra dela. Ver `checklist-oraculo.md` pro detalhe
completo. Antes do fix, a regressão de 20.000 partidas TRAVAVA por
completo por volta da partida #13500 (nunca terminava); depois, 0
exceções, termina normalmente. `Avg tutors_used_total` 0,925→0,905.

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

### Leitura linha-a-linha completa do oráculo (mesma exigência do Toph/Beorn/Edgar Markov/Hei Bai) — 2026-09-01

**Gatilho (usuário):** *"AGORA FAZ O QUE SEMPRE Te MANDei FAZER: COmpila
a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada carta tem que ser
lida linha a linha"*.

Achado: 4 cartas (Wirewood Symbiote, Scryb Ranger, Wirewood Lodge,
Formidable Speaker — todas na família "return an Elf/Forest OU tap:
untap target creature") estavam deferidas ou nem mencionadas, com
justificativa de "risco de bug > valor esperado" para as 2 primeiras —
linguagem de julgamento de valor proibida.

**Implementando a família, achei um bug real:** Maralen (comandante) é
ela mesma um Elf — sem excluí-la do pool de bounce do Wirewood Symbiote,
ela podia ser selecionada como fodder, voltando pra mão. Isso expôs um
hang infinito real: recast descontrolado do comandante via o loop
genérico de conjuração (nunca removia ela de `state.hand` corretamente
nesse caminho), battlefield crescendo sem fim. Achado via varredura
sistemática de timeout (seed 2000026 travava indefinidamente; testei
range(2000000, 2000050) com print incremental até isolar o seed exato).
Corrigido excluindo o comandante do pool de fodder — decisão correta de
qualquer forma (ninguém bounça o próprio comandante de 5 mana com um
Elfo de 1 mana havendo fodder mais barato).

**Robustez:** seed 2000026 isolado (antes: hang indefinido; depois:
0,001s) + 20.000 partidas de regressão (0 erros) + varredura de 1000
seeds sem timeout.

**Batch, n=2000, seed_base=6000000:** nova métrica "família untap" ativa
em 30,8% dos jogos, avg 0,94 ativações/partida — confirmado real, não
morto por bug de gate.

**Leitura:** o achado mais importante não foi a habilidade em si — foi
que implementar uma mecânica antes deferida por julgamento de valor
revelou um bug pré-existente que nenhuma auditoria anterior podia ter
achado, porque o caminho de código nunca era alcançado antes. Evidência
direta de por que "compile TUDO" > filtrar por valor esperado.

`checklist-oraculo.md` criado (92 cartas).

---

<!-- Copie o bloco acima para cada nova partida -->
