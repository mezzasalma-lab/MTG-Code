# Goldfish Log — Nekusar, the Mindrazer

> **Rodada 2026-10-05 (Terreno virado primeiro em T1/T2 + contagem de magias/storm (varredura de 2026-10-05)) — dados brutos e reprodução:** [`resultados-ab/2026-10-05-terreno-virado-primeiro/LEIAME.md`](resultados-ab/2026-10-05-terreno-virado-primeiro/LEIAME.md)

> **Rodada 2026-10-05 (Mulligan com escolha do fundo (varredura de 2026-10-05)) — dados brutos e reprodução:** [`resultados-ab/2026-10-05-mulligan-e-ordem-das-fases/LEIAME.md`](resultados-ab/2026-10-05-mulligan-e-ordem-das-fases/LEIAME.md)

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Terreno virado primeiro em T1/T2 + contagem de magias/storm (varredura de 2026-10-05) — 2026-10-05

**Pedido do usuário:** *"Com base nos erros encontrados nas ultimas revisões, reanálise todos os outros decks em busca de erros semelhantes, e os corrija"*. Arquivo bruto/auditável: `resultados-ab/2026-10-05-terreno-virado-primeiro/` (`LEIAME.md`).

**Veredito:** um erro real, um conserto, bit-idêntico com a chave desligada e com o ensaio sem efeito colateral (modo GHOST). Modo padrão, N=10.000: comandante em campo até T3 10,0% → 9,9% (-0,04 ± 0,16 pp), até T4 +0,26 ± 0,17 pp, até T5 +0,48 ± 0,25 pp; comandante que nunca chega a entrar na partida +0,07 ± 0,12 pp. Modo resiliência: comandante em campo até T3 9,3% → 9,2% (-0,01 ± 0,15 pp), até T4 +0,19 ± 0,19 pp, até T5 +0,40 ± 0,27 pp; comandante que nunca chega a entrar na partida -0,01 ± 0,14 pp. A correção joga o terreno virado primeiro em média 0,17 vez(es) por partida (N=10.000, padrão) e o ensaio impede 0,25 vez(es) por partida (teria custado uma jogada).

**Achado (varredura das classes de erro do Vihaan/Megatron neste simulador):**
- **Terreno que entra virado nunca é jogado primeiro.** `play_land` jogava sempre o primeiro terreno da ordem própria do deck (desvirado antes de virado). Em T1/T2, sem nada pra conjurar, a mana do turno era desperdiçada enquanto o terreno que entra virado ficava na mão pra um turno em que ele custa desenvolvimento. Mesmo erro achado e corrigido no Vihaan e no Megatron (2026-10-03/04).
- **Jogar terreno contava como magia conjurada.** `cast_card` (que também joga os terrenos) incrementava `spells_cast_this_turn` e `storm_count_max` antes do ramo de terreno. CR 305.1: jogar terreno não é conjurar magia. Isso inflava o storm do Brain Freeze e a métrica `storm_count_max`.
- **O storm do Brain Freeze contava ela mesma.** `copies = spells_cast_this_turn` já inclui o próprio Brain Freeze (o contador sobe antes de resolver), mas storm copia "para cada outra magia conjurada ANTES" e a fórmula do mill somava 1 do original (`3 × (1 + copies)`): uma cópia a mais. Medido no HEAD: Brain Freeze como 1ª magia do turno dava mill proxy 18 (storm 1) em vez de 9 (storm 0); com 1 terreno jogado antes, 27 em vez de 9 (`varredura-2026-10-05/resumos/audit_terreno_nao_e_magia_ANTES.txt`: Nekusar é o único dos 18 simuladores em que jogar um terreno comum mexe num contador de magia).

**O que mudou:**
- `TAPPED_LAND_FIRST_ENABLED` (padrão `True`), `TAPPED_LAND_FIRST_MAX_TURN = 2`: em T1..T2, havendo terreno virado E desvirado na mão, `tapped_first_pick` joga o virado, **salvo se isso custar desenvolvimento**: o teste é um ENSAIO a seco da própria fase de conjuração pré-combate do deck (cópia profunda do estado; `CARD_DB` compartilhado; RNG do estado copiado; `random` global restaurado), comparando o MV total das cartas que saem da mão com cada candidato. Empate → o virado. Dentro de cada grupo vale a ordem própria do deck (cor mais escassa etc.). Contadores novos no estado: `tapped_land_first_plays_total` (jogou o virado) e `tapped_land_skipped_for_play_total` (o ensaio mostrou que custaria uma jogada e jogou o desvirado). `TAPPED_LAND_FIRST_GHOST` só existe pra validação (roda o ensaio e ignora o resultado). Com a chave em `False` o caminho antigo volta bit a bit.
- `LAND_PLAY_NOT_A_SPELL_ENABLED` (padrão `True`): `cast_card` não conta a jogada de terreno em `spells_cast_this_turn`/`storm_count_max`.
- `STORM_SELF_COUNT_FIX_ENABLED` (padrão `True`): Brain Freeze usa `spells_cast_this_turn - 1` (magias conjuradas antes dela). Com as chaves em `False` a contagem antiga volta.

**Medido (pareado, mesmas sementes; IC95% = 1,96·dp/√N da diferença):**

Modo padrão, N=10.000 (`resumos/ab_10000.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 713 (7.1%)
   campo                                          base     variante dif. pareada (IC95%)
   commander_cast_turn__nunca                   0.0766       0.0773      +0.0007 ±0.0012  
   commander_cast_turn__ate_T3                  0.0996       0.0992      -0.0004 ±0.0016  
  *commander_cast_turn__ate_T4                  0.3035       0.3061      +0.0026 ±0.0017  
  *commander_cast_turn__ate_T5                  0.7084       0.7132      +0.0048 ±0.0025  
  *spells_cast_this_turn                        5.1322       4.3554      -0.7768 ±0.0432  
  *storm_count_max                              7.3068       6.5211      -0.7857 ±0.0588  
  *sensei_top_draws_total                       2.2445       2.2670      +0.0225 ±0.0113  
  *len_library                                 61.6486      61.5002      -0.1484 ±0.0847  
  *tutors_used_total                            0.9216       0.9293      +0.0077 ±0.0044  
  *cards_drawn_extra                           30.1579      30.3011      +0.1432 ±0.0847  
  *len_graveyard                               16.0192      16.1141      +0.0949 ±0.0608  
  *len_battlefield                             14.8198      14.8587      +0.0389 ±0.0255  
  *self_damage_total                           13.5460      13.7239      +0.1779 ±0.1197  
  *interaction_spells_cast_total                3.2486       3.2704      +0.0218 ±0.0147  
  *len_creature_cast_turn                       3.1891       3.2023      +0.0132 ±0.0089  
  *puzzle_box_events_total                      0.4547       0.4605      +0.0058 ±0.0040  
  *the_one_ring_burden                          0.3262       0.3349      +0.0087 ±0.0073  
  *proxy_lifegain_total                        20.3406      20.6810      +0.3404 ±0.2892
```
Modo resiliência, N=10.000 (`resumos/ab_10000_resiliencia.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 840 (8.4%)
   campo                                          base     variante dif. pareada (IC95%)
   commander_cast_turn__nunca                   0.0989       0.0988      -0.0001 ±0.0014  
   commander_cast_turn__ate_T3                  0.0926       0.0925      -0.0001 ±0.0015  
   commander_cast_turn__ate_T4                  0.2659       0.2678      +0.0019 ±0.0019  
  *commander_cast_turn__ate_T5                  0.6553       0.6593      +0.0040 ±0.0027  
  *spells_cast_this_turn                        3.9466       3.2284      -0.7182 ±0.0298  
  *storm_count_max                              5.6990       4.8870      -0.8120 ±0.0514  
  *commander_cast_count                         1.1578       1.1634      +0.0056 ±0.0035  
  *tutors_used_total                            0.7973       0.8040      +0.0067 ±0.0045  
  *sensei_top_draws_total                       1.6033       1.6188      +0.0155 ±0.0109  
  *len_smart_graveyard_snipe_log                0.1371       0.1407      +0.0036 ±0.0029  
  *smart_graveyard_snipes_total                 0.1371       0.1407      +0.0036 ±0.0029  
  *faerie_mastermind_draws_total                0.6237       0.6351      +0.0114 ±0.0104  
  *len_smart_wipe_log                           0.4713       0.4753      +0.0040 ±0.0040  
  *smart_wipes_total                            0.4713       0.4753      +0.0040 ±0.0040  
   mill_proxy_total                            66.2504      62.2875      -3.9629 ±3.9655  
   self_damage_total                            5.8097       5.9028      +0.0931 ±0.0938  
   graveyard_wipe_used                          0.3616       0.3642      +0.0026 ±0.0028  
   len_smart_graveyard_wipe_log                 0.3616       0.3642      +0.0026 ±0.0028
```
Os lotes de N=2.000 (`ab_2000*.txt`) e as variantes de sensibilidade (uma correção por vez) estão em `resumos/`.

**Raciocinado (não medido):** a correção do storm não muda o jogo goldfish (Brain Freeze só alimenta a métrica `mill_proxy_total`/`storm_count_max`), muda a medida que o deck usa pra avaliar o finalizador de mill: o número antigo estava inflado.

**Validação:** smoke (99 cartas, 0 desconhecidas, 0 duplicadas não-básicas, 200 partidas × 2 modos sem exceção); bit-identidade com as chaves desligadas × `nekusar_goldfish_v1_ANTES_7918e0b.py`, 20.000 partidas × 2 modos (`resumos/bitident_20000.txt`); regressão 20.000 × 2 modos × 2 configurações, 0 exceções (`resumos/regressao_20000.txt`); testes dirigidos 11/11 (`resumos/testes_dirigidos.txt`); ghost (chave ligada + ensaio ignorado == desligada), 20.000 × 2 modos (`resumos/ghost_20000.txt`); reprodutibilidade por `cmp` (`resumos/verificacao_reproducao.txt`).

**Escopo — verificado:**
- **Terreno virado primeiro:** leitura de `play_land` (+ predicado de entrada virada do deck); testes dirigidos TL1–TL8 (escolha com/sem jogada em T1, chave desligada, T3, só um tipo na mão, ensaio sem efeito no estado/RNG/`random`, modo GHOST, integração em `play_land`); A/B pareado 2.000 e 10.000 nos dois modos.
- **Ensaio sem efeito colateral:** com a chave ligada + modo GHOST (roda o ensaio e ignora o resultado) o resultado é idêntico a tudo desligado, 20.000 × 2 modos (`resumos/ghost_20000.txt`).
- **Bit-identidade** com as chaves desligadas × snapshot: 20.000 partidas × 2 modos, impressão digital do resultado inteiro.
- **Regressão** 20.000 × 2 modos × 2 configurações: 0 exceções.
- **Contagem de magias:** testes dirigidos TL17–TL19 (terreno não conta; Brain Freeze com storm 0 e com 2 magias antes; chaves desligadas = contagem antiga); varredura mecânica `audit_terreno_nao_e_magia.py` nos 18 simuladores (só `play_land` com terreno comum; caminhos de fetch/reanimação de terreno não varridos).

**Escopo — NÃO verificado:**
- **Condições de entrada dos terrenos** além do que a varredura mecânica cobriu (`varredura-2026-10-05/`: cenário de campo vazio + cenário condição satisfeita × violada para os padrões "unless you control …"/reveal; terrenos que o `CARD_DB` do deck não tem como básico foram pulados e estão listados lá).
- **Resto da taxonomia da Regra #1 neste arquivo** (caminhos de conjuração fora da mão e "whenever you cast", sacrifício × destroy, cascade, contadores `_sick` agregados, fórmulas dinâmicas achatadas): varrido na triagem de 2026-10-05 por `grep` e leitura pontual das funções, **sem** leitura integral do arquivo e **sem** instrumentação em runtime nesta rodada. "Sem achado" aí significa "o `grep` não achou", não "não existe".
- **Oponente real:** o goldfish não modela (convenção do repositório); nada aqui mede interação além do proxy já existente.

**Observação:** 0 exceções em 20.000 × 2 modos × 2 configurações; os invariantes genéricos (carta acima do número no baralho; contadores negativos) deram 0 violações.

---

## Mulligan com escolha do fundo (varredura de 2026-10-05) — 2026-10-05

**Pedido do usuário:** *"Com base nos erros encontrados nas ultimas revisões, reanálise todos os outros decks em busca de erros semelhantes, e os corrija"*. Arquivo bruto/auditável: `resultados-ab/2026-10-05-mulligan-e-ordem-das-fases/` (`LEIAME.md`).

**Veredito:** um erro real, um conserto, bit-idêntico com a chave desligada. É o deck em que o mulligan mais pesa: comandante em campo até T5: 69,2% → 70,8% (+1,69 ± 0,32 pp); nunca em 8 turnos: 8,7% → 7,7% (−1,02 ± 0,24 pp); cartas em campo no fim +0,17 ± 0,04 (N=10.000, padrão; resiliência com o mesmo sinal).

**Achado (varredura das classes de erro do Vihaan/Megatron neste simulador):**
- **London Mulligan com as cartas do fundo SORTEADAS** (`rng.shuffle(hand); bottom = hand[:penalty]`). CR 103.5: depois de comprar a mão nova o jogador "puts a number of those cards ... on the bottom of their library in any order", ou seja, ESCOLHE quais. O arquivo devolvia, com a mesma chance, uma carta-chave ou um terreno que faltava. Mesma classe do erro achado e corrigido no Megatron e no Vihaan (2026-10-03/04).

**O que mudou:**
- `MULLIGAN_SMART_BOTTOM_ENABLED` (padrão `True`) + `choose_bottom(hand, n)`: só devolve terreno quando sobram MAIS de 4 na mão (e então o que entra virado primeiro, se o `CARD_DB` marcar `etb_tapped`); fora isso devolve a carta não-terreno de MAIOR custo, poupando `MULLIGAN_PROTECTED` (as cartas que `should_keep` já trata como boa abertura). A regra do mulligan grátis do 1º mulligan (CR 103.5c, multiplayer) já estava modelada e não mudou. Com a chave em `False` o caminho antigo (sorteio) volta bit a bit.

**Medido (pareado, mesmas sementes; IC95% = 1,96·dp/√N da diferença):**

Modo padrão, N=10.000 (`resumos/ab_10000.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 8174 (81.7%)
   campo                                          base     variante dif. pareada (IC95%)
  *commander_cast_turn__nunca                   0.0868       0.0766      -0.0102 ±0.0024  
  *commander_cast_turn__ate_T3                  0.0960       0.0996      +0.0036 ±0.0014  
  *commander_cast_turn__ate_T4                  0.2928       0.3035      +0.0107 ±0.0024  
  *commander_cast_turn__ate_T5                  0.6915       0.7084      +0.0169 ±0.0032  
  *commander_cast_turn__ate_T6                  0.8035       0.8177      +0.0142 ±0.0030  
  *len_battlefield                             14.6506      14.8198      +0.1692 ±0.0373  
  *commander_cast_count                         0.9132       0.9234      +0.0102 ±0.0024  
  *commander_in_play                            0.9132       0.9234      +0.0102 ±0.0024  
  *len_creature_cast_turn                       3.1473       3.1891      +0.0418 ±0.0129  
  *lands_played_this_turn                       0.7655       0.7761      +0.0106 ±0.0036  
  *tutors_used_total                            0.9047       0.9216      +0.0169 ±0.0057  
  *interaction_spells_cast_total                3.1900       3.2486      +0.0586 ±0.0203  
  *len_library                                 61.9738      61.6486      -0.3252 ±0.1319  
  *cards_drawn_extra                           29.8373      30.1579      +0.3206 ±0.1322  
  *sensei_top_draws_total                       2.2012       2.2445      +0.0433 ±0.0187  
  *small_wheel_lands_used_total                 0.2820       0.2923      +0.0103 ±0.0050  
  *rituals_cast_total                           0.8730       0.8871      +0.0141 ±0.0070  
  *breach_recasts_total                         1.3636       1.4013      +0.0377 ±0.0199
```
Modo resiliência, N=10.000 (`resumos/ab_10000_resiliencia.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 8172 (81.7%)
   campo                                          base     variante dif. pareada (IC95%)
  *commander_cast_turn__nunca                   0.1110       0.0989      -0.0121 ±0.0027  
  *commander_cast_turn__ate_T3                  0.0893       0.0926      +0.0033 ±0.0013  
  *commander_cast_turn__ate_T4                  0.2569       0.2659      +0.0090 ±0.0023  
  *commander_cast_turn__ate_T5                  0.6395       0.6553      +0.0158 ±0.0033  
  *len_battlefield                             11.1055      11.2345      +0.1290 ±0.0275  
  *commander_cast_turn__ate_T6                  0.7673       0.7810      +0.0137 ±0.0031  
  *commander_in_play                            0.7727       0.7851      +0.0124 ±0.0036  
  *commander_cast_count                         1.1423       1.1578      +0.0155 ±0.0045  
  *interaction_spells_cast_total                2.5779       2.6281      +0.0502 ±0.0179  
  *len_creature_cast_turn                       1.9889       2.0195      +0.0306 ±0.0118  
  *len_hand                                     4.4064       4.3606      -0.0458 ±0.0182  
  *lands_played_this_turn                       0.7048       0.7130      +0.0082 ±0.0038  
  *breach_loops_total                           0.3291       0.3377      +0.0086 ±0.0043  
  *rituals_cast_total                           0.7020       0.7131      +0.0111 ±0.0058  
  *sensei_top_draws_total                       1.5705       1.6033      +0.0328 ±0.0172  
  *small_wheel_lands_used_total                 0.2808       0.2910      +0.0102 ±0.0056  
  *breach_recasts_total                         0.8583       0.8866      +0.0283 ±0.0157  
  *tutors_used_total                            0.7884       0.7973      +0.0089 ±0.0051
```
Os lotes de N=2.000 (`ab_2000*.txt`) e as variantes de sensibilidade (uma correção por vez) estão em `resumos/`.

**Raciocinado (não medido):** o comandante do Nekusar é caro e o deck depende de terrenos e rituais; devolver uma carta sorteada tinha mais chance de custar uma peça-chave do que sobrar um terreno extra, por isso o ganho aqui é maior do que nos decks com comandante barato.

**Validação:** smoke (99 cartas, 0 desconhecidas, 0 duplicadas não-básicas, 200 partidas × 2 modos sem exceção); bit-identidade com as chaves desligadas × `nekusar_goldfish_v1_ANTES_96a6a22.py`, 20.000 partidas × 2 modos (`resumos/bitident_20000.txt`); regressão 20.000 × 2 modos × 2 configurações, 0 exceções (`resumos/regressao_20000.txt`); testes dirigidos 8/8 (`resumos/testes_dirigidos.txt`); reprodutibilidade por `cmp` (`resumos/verificacao_reproducao.txt`).

**Escopo — verificado:**
- **Mulligan:** leitura de `mulligan` e `should_keep`; teste dirigido (M1–M8: escolha do fundo, conservação das cartas, caminho antigo com a chave desligada); A/B pareado 2.000 e 10.000 nos dois modos.
- **Bit-identidade** com as chaves desligadas × snapshot: 20.000 partidas × 2 modos, impressão digital do resultado inteiro.
- **Regressão** 20.000 × 2 modos × 2 configurações: 0 exceções.

**Escopo — NÃO verificado:**
- **Jogada de terreno virado em T1/T2 ("tapped-first")** e **condições de entrada dos terrenos** (checkland/fastland/slow/reveal): não são tratadas nesta seção; quando houver correção, ela tem seção própria.
- **Resto da taxonomia da Regra #1 neste arquivo** (caminhos de conjuração fora da mão e "whenever you cast", sacrifício × destroy, cascade, contadores `_sick` agregados, fórmulas dinâmicas achatadas): varrido na triagem de 2026-10-05 por `grep` e leitura pontual das funções, **sem** leitura integral do arquivo e **sem** instrumentação em runtime nesta rodada. "Sem achado" aí significa "o `grep` não achou", não "não existe".
- **Oponente real:** o goldfish não modela (convenção do repositório); nada aqui mede interação além do proxy já existente.

**Observação:** 0 exceções em 20.000 × 2 modos × 2 configurações; os invariantes genéricos (carta acima do número no baralho; contadores negativos) deram 0 violações.

---

## Porte completo do modo de resiliência + CR 903.9a nativa desde o início — 2026-09-21

**Gatilho:** "Agora faça com oNekusar" — seguindo o porte concluído no
Vihaan. Detalhes completos em `checklist-oraculo.md` e
`megatron-tyrant-mardu/checklist-oraculo.md`.

**Achado:** 2º deck desta sessão a nascer com CR 903.9a correta desde o
início. Sem impacto numérico (0 cartas "creature dies", 0 tokens
agregados — deck de dano-por-compra/wheel/storm, não aristocrata).
Achado de modelagem real: Spark Double (cópia de criatura) precisa de
tratamento específico em `remove_permanent` — remover a cópia limpa
`spark_double_copy_target`, remover o original copiado NÃO afeta a
cópia (CR 706.2).

**Resultado:** modo padrão idêntico (0/20000 mismatches) — diferente do
Vihaan, nenhum bug pré-existente do motor próprio foi achado aqui.

**Validação:** regressão de 20.000 partidas em modo de resiliência, 0
exceções, 0 comandantes presos no cemitério + 6 testes dirigidos.

---

## Auditoria oráculo-por-oráculo completa — 2026-09-13

Ver `checklist-oraculo.md` pra lista completa dos 11 gaps reais achados e
corrigidos nesta rodada (releitura linha-a-linha contra o oráculo real de
todas as 92 cartas + comandante via Scryfall).

**Resultado (n=2000, seed_base=5550000, turns=8, antes → depois):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg eventos de wheel | 3,60 | **2,81** |
| Avg dano/vida proxy total | 453,31 | **345,59** |
| Avg vida ganha (Sheoldred/Bloodchief) | 11,05 | **16,86** |
| Avg storm count máximo | 7,79 | **6,54** |
| Avg recasts via Breach/Flames | 1,41 | **1,12** |
| Avg autodano (Spiteful Visions+Tyranny) | 91,00 | **11,26** |
| Avg vida final | -50,79 | **30,32** |
| Partidas em que payoffs próprios me derrubam a 0- | 11,8% | **8,9%** |

**Leitura das quedas (eventos de wheel, dano proxy, storm count, recasts):**
o achado mais impactante numericamente não foi um dos 11 gaps "de
adição" (Sheoldred/Mindcrank/Bloodchief centralizados, The One Ring, etc.
— todos esses SOBEM valor), foi um bug de **overcounting** achado
incidentalmente ao validar os outros: `draw_cards()` cobrava autodano
(Spiteful Visions/Phyrexian Tyranny) usando a quantidade de compra
PEDIDA em vez da REALMENTE feita — em jogos que batem no loop profundo
de storm (Underworld Breach/Past in Flames recastando wheels
repetidamente), a biblioteca podia esgotar no meio da sequência, e cada
pedido de compra "fantasma" subsequente ainda cobrava autodano cheio.
Comparando as mesmas 2000 seeds carta a carta, um jogo isolado tinha
`self_damage_total` **2.787** (contra dezenas esperadas) só por causa
desse bug — outliers assim distorciam a média pra cima e, como
consequência colateral (menos autodano = menos vida perdida = jogos
convergem menos vezes em `life <= 0`, que MUDA A TRAJETÓRIA de RNG
subsequente via `bonus_mana_pool`/tutores/etc, já que tudo compartilha o
mesmo `random.Random(seed)`), explicam a maior parte da queda observada
em eventos-de-wheel/storm/recasts nesta comparação de médias (efeito de
cauda longa em ~2000 jogos, não uma regressão real de nenhuma mecânica -
confirmado pelos 9 snippets standalone no checklist, que isolam cada
correção controlando o resto do estado). "Avg cartas compradas extra"
ficou praticamente igual (26,13 → 26,04), confirmando que o VOLUME de
compra não mudou - só o autodano cobrado por compras que nunca
aconteceram de verdade.

**Vida ganha (Sheoldred) subindo 11,05 → 16,86** é o efeito direto e
esperado da centralização real (item 1 do checklist): agora conta em
TODAS as fontes de compra, não só `draw_step()`.

**Robustez:** 20.000 partidas de regressão (seed_base=9500000, turns=8,
timeout 2s via `signal.alarm`) — **0 exceções, 0 timeouts**.

`lista.md` não mudou (trabalho só de implementação, nenhuma carta
adicionada/removida). `nekusar_v1_runs.jsonl` sobrescrito na próxima
execução de `__main__`.

---

## Simulação #1 — goldfish Python completo (`nekusar_goldfish_v1.py`) — 2026-08-23

**Script construído do zero**, reaproveitando a varredura mecânica já feita na auditoria (`auditoria.md` seções 5 e 6, que já tinha catalogado os 9 payoffs reais de dano-por-compra e as 15 fontes de wheel/draw em massa carta a carta com oracle_text exato) em vez de refazer o Passo 0 do zero — a auditoria já tinha esse trabalho pronto e correto.

**Sem oponente real num goldfish solo**, e este é o deck mais dependente disso de todos os já simulados nesta biblioteca (é literalmente um deck de "dano por compra do oponente"): `NUM_OPPONENTS = 3` é uma premissa declarada de mesa (4 jogadores), e todo dano/perda-de-vida gerado é um contador **proxy agregado** (`proxy_damage_total`), nunca vida real de ninguém — reportado sempre com esse aviso, nunca como "matou a mesa".

**Motor central implementado com fidelidade real:** `damage_per_opponent_draw()` soma os 8 payoffs de dano-por-compra ativos (comandante, Orcish Bowmasters, Sheoldred, Underworld Dreams, Spiteful Visions, Phyrexian Tyranny, Razorkin Needlehead, Scrawling Crawler), e cada evento de wheel (`wheel_event()`) multiplica isso pelo número de compras de cada oponente-proxy. Os gatilhos simétricos "each player's draw step, +1 draw" (comandante, Spiteful Visions) são tratados à parte no `draw_step()`, afetando tanto minha mão real quanto o dano proxy gerado nos oponentes.

**Combo de storm/recursão (Underworld Breach + Past in Flames + rituais) implementado como loop real**, não decorativo — `work_breach_or_flames_recast()` respeita os custos reais de cada mecânica: escape (Underworld Breach) exige exilar 3 outras cartas do cemitério a cada recast (auto-limitante, o cemitério encolhe 3 por iteração); flashback (Past in Flames) exila a própria carta recastada ao resolver (regra real, CR 702.32a).

**2 bugs reais encontrados e corrigidos no smoke-test/robustez, antes do batch oficial:**

1. **Comandante nunca saía da mão** — mesmo bug já visto em todos os outros 5 simuladores desta biblioteca: `cast_card()` tentava `state.hand.remove(COMMANDER)` incondicionalmente, mas ela vem da zona de comando, não da mão. Corrigido excluindo a comandante dessa remoção.
2. **Loop do Past in Flames nunca convergia** — a primeira versão devolvia a carta recastada via flashback de volta pro cemitério (copiando a lógica do escape do Underworld Breach), mas flashback de verdade **exila** a carta ao resolver, não devolve. Sem isso, o loop batia no teto defensivo de 40 iterações repetidamente (visto em 3 das primeiras 30 seeds testadas manualmente, com `storm_count` grudado em 40-50). Corrigido: só o modo "escape" devolve a carta pro cemitério; o modo "flashback" a exila de verdade.
3. **Sem descarte por limite de mão (CR 514.3)** — achado rodando uma amostra maior: mãos chegando a **74 cartas** depois de 8 turnos, porque nada descartava o excesso no cleanup. Esperado nesse deck especificamente, já que ele compra em volume absurdo (Nekusar + Spiteful Visions dão +1 compra simétrica por turno, fora os wheels completos). Corrigido com `cleanup_discard()`: descarta até 7 no fim do turno, priorizando manter as cartas de maior CMC (mais impactantes) e descartando o excedente mais barato primeiro — incluindo terrenos excedentes quando já há mana suficiente em campo, uma escolha real de jogo, documentada.

**Teste de robustez** (antes e depois dos 2 bugs de loop/mão): 20.000 partidas com timeout de 2s via `signal.alarm`, **0 erros, 0 timeouts** em ambas as rodadas — a segunda rodada (pós-fix do cleanup) confirmou a correção (mão máxima voltou a 7, contra 74 antes).

**n=3000, seed_base=7300000, 8 turnos — resultado oficial:**

```
Avg mulligans: 0,61
Turno medio de conjuracao do Nekusar: 5,14 | mediana: 5,0
Nunca conjurado em 8 turnos: 12,8%
Avg eventos de wheel (full+parcial): 1,19
Avg wheels completos (descarta mao, compra 7): 1,19
Avg dano/perda-de-vida proxy total (3 oponentes hipoteticos, NUNCA vida real): 81,51
Avg vida ganha (Sheoldred, proxy Bloodchief): 1,91
Avg cartas compradas extra: 16,60
Avg tutores usados: 0,78
Avg recasts via Underworld Breach/Past in Flames: 0,51
Partidas com pelo menos 1 loop de Breach/Flames (2+ recasts no mesmo evento): 26,7%
Avg storm count maximo no turno: 4,03
Avg mill proxy total (Mindcrank + Brain Freeze): 9,66
Avg reanimados (Animate Dead/Reanimate): 0,01
Avg mao final: 3,38
```

**Leituras principais:**

- **Comandante mais lento que os outros decks já simulados** (T5,14 médio, 12,8% nunca resolve em 8 turnos) — coerente com o custo `{2}{U}{B}{R}` (3 cores + genérico) e uma base de mana que prioriza fetches/duais sobre rampa dedicada (só 3 rocks reais: Sol Ring, Arcane Signet, os 2 Talismãs).
- **O combo de storm (Breach/Flames) é real e aparece em parcela relevante das partidas (26,7% com pelo menos 1 loop de 2+ recasts)**, mas o volume médio de recasts é modesto (0,51/partida) — bate com a leitura qualitativa da auditoria ("não é um combo de 2 peças isolado, é uma cadeia que pode explodir quando as peças se alinham"): quando liga, gera valor real (storm médio de 4,03, alguns jogos passam disso), mas não é a maioria das partidas.
- **Dano proxy médio de 81,51 por partida** é alto mesmo sem o cenário extremo de "todos os 8 payoffs em campo simultâneo" que a auditoria descreveu como matemática de mesa — confirma que o motor de wheel-damage é genuinamente forte mesmo em jogos parciais, não só no caso hipotético ideal.
- **Reanimados praticamente zero (0,01/partida)** — esperado: só 9 criaturas em 99 cartas, e nada no deck sacrifica/descarta criaturas de propósito (os wheels descartam a mão inteira aleatoriamente, então às vezes pegam uma criatura, raramente).

Resultados salvos em `nekusar_v1_runs.jsonl` (3000 jogos).

**Simplificações documentadas no docstring do script** (não inventadas — omissões explícitas): sem oponente real, todo dano/vida é proxy agregado (`NUM_OPPONENTS=3`); contramágicas/proteção conjuradas quando há mana sobrando, sem efeito de combate real modelado; fetchlands tratadas como terreno genérico (thinning não modelado); Brain Freeze e Mindcrank registram mill como proxy, nunca aplicado a biblioteca real de ninguém; Wheel of Misfortune modelado como wheel completo padrão, sem a metade condicional de dano-por-número-escolhido; sem combate real (deck não é de ataque).

---

## Correção — checklist obrigatória de mecânica (regra nova pós-Beorn) — 2026-08-28

**Gatilho (usuário):** depois de eu entregar o Beorn sem despacho de landfall
nenhum, o usuário pediu auditoria da checklist nova (landfall, mana dorks,
mana rocks, fixing lands, draw engines, ramp engines, ativadas repetíveis,
combos) em **todos** os decks. Achado grave nesta rodada: o próprio docstring
do script afirmava "9 payoffs... 15 fontes de wheel/draw... **todos** com
efeito real implementado" — falso. **11 das ~15 fontes catalogadas tinham só
a tag, nenhum gatilho real**:

- **Waste Not / Liliana's Caress** (tag `discard_payoff`): gatilhos por carta
  DESCARTADA por oponente (evento distinto de "compra", que `wheel_event()`
  já cobria) — nunca disparavam. Nova função `discard_payoff_total()`,
  chamada de dentro de `wheel_event()` com um parâmetro de descartes por
  oponente (premissa documentada: na maioria dos wheels simétricos
  "descarta a mão, compra N" o descarte tem a mesma ordem de grandeza do
  redraw). Waste Not modelado com a composição real da decklist (22
  terrenos/10 criaturas/67 outras de 99) pra dividir entre as 3 cláusulas.
- **Jace's Archivist / Magus of the Wheel**: wheels reais ({U},{T} repetível
  1x/turno; sacrifício de um tiro só) — 100% ausentes, implementadas como
  eventos de wheel de verdade.
- **Faerie Mastermind**: as DUAS metades ausentes — passiva ("whenever an
  opponent draws their second card each turn, you draw a card", dispara
  quando o próprio estático do Nekusar está ativo) e ativada ("{3}{U}: each
  player draws a card", repetível, teto de 10/turno).
- **Resonating Lute**: metade "{T}: Draw a card. Activate only if 7+ cards
  in hand" implementada; a estática de campo (lands ganham mana extra
  restrita a instant/sorcery) fica de fora — esse motor não restringe mana
  por tipo de spell, baixo valor pro escopo.
- **Sensei's Divining Top**: achado extra — o gate usava `ready_creatures()`
  (lista só de criaturas), mas o Top é um Artifact, nunca aparecia lá.
  Condição morta por construção, nunca disparava. Corrigido (artefato não
  tem doença de invocação).
- **Teferi's Puzzle Box**: tag `wheel_passive` só era lida pra ordenar
  prioridade de cast, nunca disparava o efeito real ("at the beginning of
  each player's draw step..."). Implementado 1x por meu turno (premissa:
  tamanho médio de mão do oponente = 5, representa o ciclo dos 3 turnos-
  proxy dos oponentes desde meu último turno).
- **Mikokoro / Geier Reach Sanitarium / Cephalid Coliseum**: 3 terrenos
  wheel, 100% ausentes — implementados como ativações reais ({2},{T} pra
  Mikokoro/Geier Reach; Cephalid Coliseum com o gate real de Threshold,
  7+ cartas no cemitério, sacrifício de um tiro só).

**Resultado (n=2000, seed_base=4000000, antes → depois):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg eventos de wheel | 1,19 | **3,45** |
| Avg dano/vida proxy total | 81,05 | **404,75** |
| Avg cartas compradas extra | 16,54 | **25,70** |
| Avg storm count máximo | 4,06 | **7,33** |
| Avg recasts via Breach/Flames | 0,53 | **1,18** |
| Avg vida ganha (Sheoldred) | 1,91 | **9,92** |

Salto grande (5x no dano proxy) — o deck estava significativamente
subsimulado: quase todo o "motor de wheel secundário" (fora os 4-5 payoffs
principais já implementados desde a Simulação #1) não existia de verdade.
Mais cartas compradas por turno também alimenta mais recasts via Underworld
Breach (fica com mais spells no cemitério pra reciclar), explicando o
aumento composto em storm count e recasts.

**Robustez:** sweep de 20.000 jogos (seeds 4000000–4019999, timeout 2s/jogo)
— 0 erros, 0 timeouts.

Docstring do script corrigido (a frase "todos com efeito real implementado"
era falsa — substituída por uma nota explícita desta correção).

`lista.md` não mudou. `nekusar_v1_runs.jsonl` sobrescrito.

---

## Correção #2 — checklist ampliado (13 categorias: layout real de multi-face, planeswalker loyalty, Classes/Sagas) + varredura de tags mortas — 2026-08-28

**Gatilho (usuário):** continuação de "Sim por favor" (par Maralen + Nekusar).
Checklist de 13 categorias aplicado do zero.

**Categorias 11/12/13:** confirmado via `lista.md` e grep — 0 cartas de
dupla face, 0 planeswalkers, 0 Classes/Sagas nesta decklist. N/A,
documentado.

**Varredura de tags mortas em CARD_DB** (mesma técnica que achou o gap do
Growing Rites of Itlimoc na Maralen — cruzar toda tag registrada contra
onde ela é lida no resto do arquivo) achou **6 gaps reais adicionais**,
além dos 11 já corrigidos na Correção #1:

- **Spark Double** (tag `copy`, 100% inerte): oráculo real *"You may have
  this creature enter as a copy of a creature or planeswalker you
  control, except it isn't legendary"* — evita a legend rule ao copiar o
  próprio Nekusar. Maior gap desta rodada: copiar um payoff de
  dano-por-compra empilha o motor central inteiro. Implementado
  `resolve_spark_double_target()` (prioriza Nekusar > Sheoldred >
  Bowmasters > Razorkin > Scrawling Crawler) + refatoração de
  `damage_per_opponent_draw()`/`symmetric_extra_draws_per_player()` pra
  contar cópias (`_copies_of()`/`_commander_copies()`) em vez de só
  checar presença — decklist é singleton, então isso nunca mudava nada
  antes do Spark Double existir.
- **Deflecting Swat** (tag `free_with_commander`, nunca lida): oráculo
  real *"If you control a commander, you may cast this spell without
  paying its mana cost."* Pagava o custo cheio ({3}) igual qualquer outra
  "interaction" genérica. Corrigido em `can_cast()`/`cast_card()`.
- **Undercity Sewers** (tag mal-rotulada `etb_tapped_filter`, nunca
  lida): oráculo real *"This land enters tapped. When this land enters,
  surveil 1."* Nem o enters-tapped nem o surveil eram modelados — nova
  infraestrutura `tapped_lands_this_turn` (mesmo padrão já usado nos
  outros simuladores desta sessão) + `do_surveil_1()` (heurística
  documentada: manda terreno do topo pro cemitério se já há mana
  suficiente em campo, alimentando Underworld Breach).
- **Cascade Bluffs**: a mesma tag `etb_tapped_filter` estava nela também,
  mas o oráculo real dela **não** entra tapped — mislabel puro (tag
  nunca lida de qualquer forma, então nunca mudou o comportamento, só
  corrigido o rótulo pra `set()`).
- **Flashback** (o card, tag genérica `interaction`, nunca despachada
  além de consumir mana): oráculo real *"Target instant or sorcery card
  in your graveyard gains flashback until end of turn. The flashback
  cost is equal to its mana cost."* Distinto da palavra-chave que Past in
  Flames concede — os dois "Flashback" coexistem nesta decklist.
  Reaproveitado `work_breach_or_flames_recast()` com novo parâmetro
  `max_iterations=1` (é um enabler de um tiro só, não um motor
  repetível).
- **Orcish Bowmasters** (achado ao reverificar oráculo de todos os
  payoffs, não uma tag morta): real é *"...whenever an opponent draws a
  card EXCEPT THE FIRST ONE they draw in each of their draw steps..."* —
  a versão anterior contava a compra normal do draw step também,
  **superestimando** o dano dele. Corrigido: `damage_per_opponent_draw()`
  ganhou parâmetro `count_bowmasters`, e `draw_step()` separa a compra
  "base" (exclui Bowmasters) das compras "extra" via Nekusar/Spiteful
  Visions (contam normalmente — não são "a primeira").

**Achado extra, não vindo de tag morta — reverificação de oráculo real de
todos os payoffs simétricos:** **Spiteful Visions** (*"Whenever A PLAYER
draws a card..."*) e **Phyrexian Tyranny** (*"Whenever A PLAYER draws a
card, that player loses 2 life unless they pay {2}"*) dizem **"a
player"**, não "an opponent" como Nekusar/Underworld Dreams/Razorkin
Needlehead/Scrawling Crawler — ou seja, **também me acertam quando EU
compro**. Isso nunca era rastreado, apesar do deck comprar em volume
extremo (até 7+ cartas por wheel, ~26 cartas extra/partida em média).
Implementado `self_damage_per_draw()`, aplicado dentro de `draw_cards()`
(único ponto de entrada de toda compra minha no arquivo, cobre todos os
motores automaticamente). Premissa documentada: não pago o {2} do
Phyrexian Tyranny pra evitar (pagar {2} POR CARTA durante um wheel de 7
compras seria 14 mana, inviável na prática — mesma decisão já assumida
pro lado do oponente).

**Resultado (n=2000, seed_base=12345, antes → depois):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg dano/vida proxy total | 442,94 | **461,81** |
| Avg vida ganha (Sheoldred) | 11,09 | **11,52** |
| Avg cartas compradas extra | 25,86 | **26,09** |
| Avg recasts via Breach/Flames | 1,24 | **1,44** |
| Avg storm count máximo | 7,64 | **7,91** |
| Avg mill proxy total | 111,34 | **123,84** |
| Avg mão final | 4,71 | **4,70** |
| Spark Double copiou algo | N/A (inerte) | **9,8%** dos jogos, alvo mais comum: Nekusar |
| Avg recasts via Flashback (card) | N/A (inerte) | **0,27** |
| Avg mills via surveil (Undercity Sewers) | N/A (inerte) | **0,03** |
| **Avg autodano (Spiteful Visions+Tyranny nas MINHAS compras)** | **0 (nunca rastreado)** | **95,34** |
| **Avg vida final** | **não reportado** | **-55,14** |
| **Partidas em que os PRÓPRIOS payoffs me derrubam a 0 ou menos** | **não reportado** | **11,4%** |

O achado mais importante desta rodada não é um número que sobe — é um
número que **nunca existia**: autodano médio de 95,34 por partida, vida
final média **negativa** (-55,14), e 11,4% das partidas em que os
próprios payoffs simétricos (Spiteful Visions + Phyrexian Tyranny)
matariam o piloto antes de qualquer coisa que os oponentes façam. Isso é
consistente com sabedoria real de deckbuilding do arquétipo (pilotos de
Nekusar competitivo costumam evitar rodar as duas juntas por esse motivo
exato), mas o simulador nunca tinha essa informação disponível pra
reportar — `state.life` existia desde a Simulação #1 mas nunca era
decrementado por essas duas cartas.

**Robustez:** sweep de 20.000 jogos (seeds 920000–939999, timeout 2s/jogo)
— 0 erros, 0 timeouts.

Bloco "Métricas básicas (checklist obrigatório)" (RAMP/DRAW/INTERACTION/
RECURSION/FINISHER-LETHALITY) adicionado ao `run_batch()`, que faltava
nesta decklist.

`lista.md` não mudou. `nekusar_v1_runs.jsonl` sobrescrito na próxima
execução de `__main__`.

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

### Leitura linha-a-linha completa do oráculo (mesma exigência do Toph/Beorn/Edgar Markov/Hei Bai/Maralen/Megatron) — 2026-09-01

**Gatilho (usuário):** *"AGORA FAZ O QUE SEMPRE Te MANDei FAZER: COmpila
a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada carta tem que ser
lida linha a linha"*.

Nekusar já tinha passado por 2 rodadas anteriores (auditoria.md
2026-08-20, checklist obrigatória 2026-08-28 — achou e corrigiu 11
fontes de wheel/draw com tag mas sem gatilho real). Varredura
automatizada desta rodada (toda tag em `add()` comparada contra o resto
do arquivo, procurando tags mortas) achou 9 candidatas; 8 eram
dispatchadas por nome literal (tag decorativa, não bug); a única
genuinamente órfã (`flash_enabler`, Emergence Zone) é 📊 estrutural real
— este sim não modela timing de instant-speed/stack pra NENHUMA carta,
consistente em todo o arquivo, não uma exceção seletiva.

**Nenhum bug de comportamento novo achado.** Segundo deck (depois do Hei
Bai) em que a releitura linha-a-linha confirma trabalho anterior
completo. `checklist-oraculo.md` criado (99 cartas) documentando a
verificação.

---

<!-- Copie o bloco acima para cada nova partida -->
