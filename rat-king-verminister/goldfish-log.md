# Goldfish Log — Rat King, Verminister

> **Rodada 2026-10-05 (Terreno virado primeiro em T1/T2 (varredura de 2026-10-05)) — dados brutos e reprodução:** [`resultados-ab/2026-10-05-terreno-virado-primeiro/LEIAME.md`](resultados-ab/2026-10-05-terreno-virado-primeiro/LEIAME.md)

> **Rodada 2026-10-05 (Mulligan com escolha do fundo + upkeep antes do draw (varredura de 2026-10-05)) — dados brutos e reprodução:** [`resultados-ab/2026-10-05-mulligan-e-ordem-das-fases/LEIAME.md`](resultados-ab/2026-10-05-mulligan-e-ordem-das-fases/LEIAME.md)

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Terreno virado primeiro em T1/T2 (varredura de 2026-10-05) — 2026-10-05

**Pedido do usuário:** *"Com base nos erros encontrados nas ultimas revisões, reanálise todos os outros decks em busca de erros semelhantes, e os corrija"*. Arquivo bruto/auditável: `resultados-ab/2026-10-05-terreno-virado-primeiro/` (`LEIAME.md`).

**Veredito:** um erro real, um conserto, bit-idêntico com a chave desligada e com o ensaio sem efeito colateral (modo GHOST). Modo padrão, N=10.000: sem diferença pareada nos campos do turno do comandante (ou o simulador não os registra). Modo resiliência: comandante em campo até T3 99,2% → 98,7% (-0,49 ± 0,16 pp), até T4 -0,03 ± 0,04 pp, até T5 -0,01 ± 0,02 pp, comandante que nunca entra: sem diferença pareada. A correção joga o terreno virado primeiro em média 0,33 vez(es) por partida (N=10.000, padrão) e o ensaio impede 0,14 vez(es) por partida (teria custado uma jogada). Terrenos jogados no total: +0,002 ± 0,004 por partida.

**Achado (varredura das classes de erro do Vihaan/Megatron neste simulador):**
- **Terreno que entra virado nunca é jogado primeiro.** `play_land` jogava sempre o primeiro terreno da ordem própria do deck (desvirado antes de virado). Em T1/T2, sem nada pra conjurar, a mana do turno era desperdiçada enquanto o terreno que entra virado ficava na mão pra um turno em que ele custa desenvolvimento. Mesmo erro achado e corrigido no Vihaan e no Megatron (2026-10-03/04).

**O que mudou:**
- `TAPPED_LAND_FIRST_ENABLED` (padrão `True`), `TAPPED_LAND_FIRST_MAX_TURN = 2`: em T1..T2, havendo terreno virado E desvirado na mão, `tapped_first_pick` joga o virado, **salvo se isso custar desenvolvimento**: o teste é um ENSAIO a seco da própria fase de conjuração pré-combate do deck (cópia profunda do estado; `CARD_DB` compartilhado; RNG do estado copiado; `random` global restaurado), comparando o MV total das cartas que saem da mão com cada candidato. Empate → o virado. Dentro de cada grupo vale a ordem própria do deck (cor mais escassa etc.). Contadores novos no estado: `tapped_land_first_plays_total` (jogou o virado) e `tapped_land_skipped_for_play_total` (o ensaio mostrou que custaria uma jogada e jogou o desvirado). `TAPPED_LAND_FIRST_GHOST` só existe pra validação (roda o ensaio e ignora o resultado). Com a chave em `False` o caminho antigo volta bit a bit.
- Terrenos virados do deck: os de tag `etb_tapped` e Castle Locthwain sem Swamp/Urborg em campo. A ordem própria do deck (Urborg, Cabal Coffers, Nykthos, Castle Locthwain, Swamp) vale dentro de cada grupo.

**Medido (pareado, mesmas sementes; IC95% = 1,96·dp/√N da diferença):**

Modo padrão, N=10.000 (`resumos/ab_10000.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 7200 (72.0%)
   campo                                          base     variante dif. pareada (IC95%)
   lands_played_total                           5.8447       5.8470      +0.0023 ±0.0038  
  *len_tapped_lands_this_turn                   0.2007       0.1951      -0.0056 ±0.0029  
  *rat_tokens                                   3.2757       3.3417      +0.0660 ±0.0548  
  *len_battlefield                             16.1854      16.2165      +0.0311 ±0.0261  
  *tokens_created_total                         6.1467       6.2123      +0.0656 ±0.0580  
  *len_creature_cast_turn                       4.5104       4.5174      +0.0070 ±0.0065  
  *mercenary_tokens                             0.1597       0.1617      +0.0020 ±0.0020  
  *mana_spent_this_turn                         7.4141       7.4500      +0.0359 ±0.0358  
   creatures_died_this_turn                     1.8417       1.8555      +0.0138 ±0.0139  
   treasure_tokens                              0.9636       0.9737      +0.0101 ±0.0102  
   soul_stone_harnessed                         0.0546       0.0538      -0.0008 ±0.0009  
   library_emptied                              0.0020       0.0023      +0.0003 ±0.0003  
   tutors_used_total                            0.9225       0.9053      -0.0172 ±0.0211  
   cards_drawn_extra                            2.9853       3.0050      +0.0197 ±0.0277  
   len_tapped_creatures_this_turn               0.7999       0.8027      +0.0028 ±0.0040
```
Modo resiliência, N=10.000 (`resumos/ab_10000_resiliencia.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 7202 (72.0%)
   campo                                          base     variante dif. pareada (IC95%)
   lands_played_total                           5.6605       5.6596      -0.0009 ±0.0056  
  *commander_cast_turn__ate_T3                  0.9923       0.9874      -0.0049 ±0.0016  
   commander_cast_turn__ate_T4                  0.9966       0.9963      -0.0003 ±0.0004  
   commander_cast_turn__ate_T5                  0.9980       0.9979      -0.0001 ±0.0002  
  *len_smart_counter_log                        0.0499       0.0540      +0.0041 ±0.0029  
  *smart_counters_total                         0.0499       0.0540      +0.0041 ±0.0029  
  *len_smart_graveyard_snipe_log                0.2734       0.2684      -0.0050 ±0.0046  
  *smart_graveyard_snipes_total                 0.2734       0.2684      -0.0050 ±0.0046  
  *wiped_this_round                             0.1734       0.1694      -0.0040 ±0.0037  
  *len_battlefield                             10.7435      10.7820      +0.0385 ±0.0373  
  *commander_cast_count                         1.7040       1.7097      +0.0057 ±0.0056  
  *creatures_died_this_turn                     2.8953       2.8495      -0.0458 ±0.0455  
   len_tapped_lands_this_turn                   0.1679       0.1642      -0.0037 ±0.0037  
   mercenary_tokens                             0.0658       0.0682      +0.0024 ±0.0026  
   commander_in_play                            0.8146       0.8180      +0.0034 ±0.0037  
   life                                        36.6752      36.6281      -0.0471 ±0.0545  
   len_smart_discard_log                        1.1339       1.1408      +0.0069 ±0.0081  
   smart_discards_total                         1.1339       1.1408      +0.0069 ±0.0081
```
Os lotes de N=2.000 (`ab_2000*.txt`) e as variantes de sensibilidade (uma correção por vez) estão em `resumos/`.

**Raciocinado (não medido):** o ganho esperado é pequeno e concentrado em T1–T3: só muda a partida quando a mão tem terreno virado E desvirado e nenhuma jogada de T1/T2 que o terreno desvirado pague (nesses casos o terreno virado deixa de ficar parado na mão até um turno em que atrasaria o desenvolvimento).

**Validação:** smoke (99 cartas, 0 desconhecidas, 0 duplicadas não-básicas, 200 partidas × 2 modos sem exceção); bit-identidade com as chaves desligadas × `ratking_goldfish_v1_ANTES_7918e0b.py`, 20.000 partidas × 2 modos (`resumos/bitident_20000.txt`); regressão 20.000 × 2 modos × 2 configurações, 0 exceções (`resumos/regressao_20000.txt`); testes dirigidos 8/8 (`resumos/testes_dirigidos.txt`); ghost (chave ligada + ensaio ignorado == desligada), 20.000 × 2 modos (`resumos/ghost_20000.txt`); reprodutibilidade por `cmp` (`resumos/verificacao_reproducao.txt`).

**Escopo — verificado:**
- **Terreno virado primeiro:** leitura de `play_land` (+ predicado de entrada virada do deck); testes dirigidos TL1–TL8 (escolha com/sem jogada em T1, chave desligada, T3, só um tipo na mão, ensaio sem efeito no estado/RNG/`random`, modo GHOST, integração em `play_land`); A/B pareado 2.000 e 10.000 nos dois modos.
- **Ensaio sem efeito colateral:** com a chave ligada + modo GHOST (roda o ensaio e ignora o resultado) o resultado é idêntico a tudo desligado, 20.000 × 2 modos (`resumos/ghost_20000.txt`).
- **Bit-identidade** com as chaves desligadas × snapshot: 20.000 partidas × 2 modos, impressão digital do resultado inteiro.
- **Regressão** 20.000 × 2 modos × 2 configurações: 0 exceções.

**Escopo — NÃO verificado:**
- **Condições de entrada dos terrenos** além do que a varredura mecânica cobriu (`varredura-2026-10-05/`: cenário de campo vazio + cenário condição satisfeita × violada para os padrões "unless you control …"/reveal; terrenos que o `CARD_DB` do deck não tem como básico foram pulados e estão listados lá).
- **Resto da taxonomia da Regra #1 neste arquivo** (caminhos de conjuração fora da mão e "whenever you cast", sacrifício × destroy, cascade, contadores `_sick` agregados, fórmulas dinâmicas achatadas): varrido na triagem de 2026-10-05 por `grep` e leitura pontual das funções, **sem** leitura integral do arquivo e **sem** instrumentação em runtime nesta rodada. "Sem achado" aí significa "o `grep` não achou", não "não existe".
- **Oponente real:** o goldfish não modela (convenção do repositório); nada aqui mede interação além do proxy já existente.

**Observação:** 0 exceções em 20.000 × 2 modos × 2 configurações; os invariantes genéricos (carta acima do número no baralho; contadores negativos) deram 0 violações.

---

## Mulligan com escolha do fundo + upkeep antes do draw (varredura de 2026-10-05) — 2026-10-05

**Pedido do usuário:** *"Com base nos erros encontrados nas ultimas revisões, reanálise todos os outros decks em busca de erros semelhantes, e os corrija"*. Arquivo bruto/auditável: `resultados-ab/2026-10-05-mulligan-e-ordem-das-fases/` (`LEIAME.md`).

**Veredito:** dois erros reais, dois consertos, bit-idênticos com a chave desligada. O efeito é pequeno porque o comandante já entra cedo neste deck (em campo até T3: 99,2% → 99,5%; +0,26 ± 0,10 pp, N=10.000). O mulligan escolhido ajuda um pouco (mais terrenos jogados: +0,018 ± 0,004 por partida); a ordem upkeep × draw muda 0,5% das partidas e **não** move nenhuma métrica além do ruído.

**Achado (varredura das classes de erro do Vihaan/Megatron neste simulador):**
- **London Mulligan com as cartas do fundo SORTEADAS** (`rng.shuffle(hand); bottom = hand[:penalty]`). CR 103.5: depois de comprar a mão nova o jogador "puts a number of those cards ... on the bottom of their library in any order", ou seja, ESCOLHE quais. O arquivo devolvia, com a mesma chance, uma carta-chave ou um terreno que faltava. Mesma classe do erro achado e corrigido no Megatron e no Vihaan (2026-10-03/04).
- **Upkeep depois do draw.** `play_turn` comprava a carta e só então rodava `upkeep_step`. CR 502–504: upkeep vem ANTES do draw step. O tutor do Ratcatcher ("at the beginning of your upkeep, search for a Rat") buscava com a carta do topo já fora da biblioteca. Regra #6 (orquestração de turno): o código da carta estava certo; a posição da chamada não.

**O que mudou:**
- `MULLIGAN_SMART_BOTTOM_ENABLED` (padrão `True`) + `choose_bottom(hand, n)`: só devolve terreno quando sobram MAIS de 4 na mão (e então o que entra virado primeiro, se o `CARD_DB` marcar `etb_tapped`); fora isso devolve a carta não-terreno de MAIOR custo, poupando `MULLIGAN_PROTECTED` (as cartas que `should_keep` já trata como boa abertura). A regra do mulligan grátis do 1º mulligan (CR 103.5c, multiplayer) já estava modelada e não mudou. Com a chave em `False` o caminho antigo (sorteio) volta bit a bit.
- `UPKEEP_BEFORE_DRAW_ENABLED` (padrão `True`): em `play_turn`, `upkeep_step` roda antes da compra; com a chave desligada roda depois (caminho antigo).

**Medido (pareado, mesmas sementes; IC95% = 1,96·dp/√N da diferença):**

Modo padrão, N=10.000 (`resumos/ab_10000.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 9355 (93.5%)
   campo                                          base     variante dif. pareada (IC95%)
  *commander_cast_turn__nunca                   0.0010       0.0006      -0.0004 ±0.0004  
  *commander_cast_turn__ate_T3                  0.9921       0.9947      +0.0026 ±0.0010  
  *commander_cast_turn__ate_T4                  0.9954       0.9971      +0.0017 ±0.0008  
  *commander_cast_turn__ate_T5                  0.9966       0.9981      +0.0015 ±0.0008  
  *lands_played_total                           5.8267       5.8447      +0.0180 ±0.0038  
  *len_battlefield                             16.1445      16.1854      +0.0409 ±0.0166  
  *len_hand                                     3.2338       3.1980      -0.0358 ±0.0194  
  *commander_cast_turn__ate_T6                  0.9973       0.9985      +0.0012 ±0.0007  
  *tokens_created_total                         6.0888       6.1467      +0.0579 ±0.0355  
  *rat_tokens                                   3.2295       3.2757      +0.0462 ±0.0321  
  *len_tapped_lands_this_turn                   0.1987       0.2007      +0.0020 ±0.0016  
  *len_tapped_creatures_this_turn               0.7959       0.7999      +0.0040 ±0.0033  
  *ramp_pieces_cast_total                       0.6981       0.7007      +0.0026 ±0.0024  
  *commander_cast_count                         0.9990       0.9994      +0.0004 ±0.0004  
  *commander_in_play                            0.9990       0.9994      +0.0004 ±0.0004  
   soul_stone_harnessed                         0.0537       0.0546      +0.0009 ±0.0010  
   creatures_died_this_turn                     1.8354       1.8417      +0.0063 ±0.0085  
   thrumming_stone_free_casts_total             0.4317       0.4272      -0.0045 ±0.0067
```
Modo resiliência, N=10.000 (`resumos/ab_10000_resiliencia.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 9343 (93.4%)
   campo                                          base     variante dif. pareada (IC95%)
  *commander_cast_turn__nunca                   0.0013       0.0007      -0.0006 ±0.0005  
  *commander_cast_turn__ate_T3                  0.9895       0.9923      +0.0028 ±0.0010  
  *commander_cast_turn__ate_T4                  0.9949       0.9966      +0.0017 ±0.0008  
  *commander_cast_turn__ate_T5                  0.9965       0.9980      +0.0015 ±0.0008  
  *lands_played_total                           5.6458       5.6605      +0.0147 ±0.0040  
  *len_hand                                     2.6403       2.5992      -0.0411 ±0.0204  
  *commander_cast_turn__ate_T6                  0.9973       0.9985      +0.0012 ±0.0007  
  *len_battlefield                             10.7181      10.7435      +0.0254 ±0.0171  
  *len_smart_removal_log                        0.5238       0.5209      -0.0029 ±0.0027  
  *smart_removals_total                         0.5238       0.5209      -0.0029 ±0.0027  
  *permanent_left_battlefield_this_turn         0.5767       0.5741      -0.0026 ±0.0026  
   commander_cast_count                         1.7015       1.7040      +0.0025 ±0.0026  
   emeritus_prepared                            0.0509       0.0500      -0.0009 ±0.0009  
   ramp_pieces_cast_total                       0.6294       0.6315      +0.0021 ±0.0023  
   tutors_used_total                            0.8834       0.8694      -0.0140 ±0.0174  
   len_tapped_lands_this_turn                   0.1667       0.1679      +0.0012 ±0.0016  
   recursion_events_total                       3.4180       3.4295      +0.0115 ±0.0155  
   len_graveyard                                5.8854       5.9012      +0.0158 ±0.0219
```
Os lotes de N=2.000 (`ab_2000*.txt`) e as variantes de sensibilidade (uma correção por vez) estão em `resumos/`.

**Raciocinado (não medido):** a ordem upkeep × draw só importa quando o upkeep olha ou muda a biblioteca/mão; aqui só o tutor de Rat do Ratcatcher faz isso, e ele raramente decide uma partida. O resultado (99,5% das partidas idênticas) é coerente com isso.

**Validação:** smoke (99 cartas, 0 desconhecidas, 0 duplicadas não-básicas, 200 partidas × 2 modos sem exceção); bit-identidade com as chaves desligadas × `ratking_goldfish_v1_ANTES_53e6255.py`, 20.000 partidas × 2 modos (`resumos/bitident_20000.txt`); regressão 20.000 × 2 modos × 2 configurações, 0 exceções (`resumos/regressao_20000.txt`); testes dirigidos 9/9 (`resumos/testes_dirigidos.txt`); reprodutibilidade por `cmp` (`resumos/verificacao_reproducao.txt`).

**Escopo — verificado:**
- **Mulligan:** leitura de `mulligan` e `should_keep`; teste dirigido (M1–M8: escolha do fundo, conservação das cartas, caminho antigo com a chave desligada); A/B pareado 2.000 e 10.000 nos dois modos.
- **Bit-identidade** com as chaves desligadas × snapshot: 20.000 partidas × 2 modos, impressão digital do resultado inteiro.
- **Regressão** 20.000 × 2 modos × 2 configurações: 0 exceções.
- **Ordem das fases:** teste dirigido O1 (com a chave ligada o upkeep roda com a mão ainda sem a carta comprada) e leitura de `play_turn` inteiro (Regra #6).

**Escopo — NÃO verificado:**
- **Jogada de terreno virado em T1/T2 ("tapped-first")** e **condições de entrada dos terrenos** (checkland/fastland/slow/reveal): não são tratadas nesta seção; quando houver correção, ela tem seção própria.
- **Resto da taxonomia da Regra #1 neste arquivo** (caminhos de conjuração fora da mão e "whenever you cast", sacrifício × destroy, cascade, contadores `_sick` agregados, fórmulas dinâmicas achatadas): varrido na triagem de 2026-10-05 por `grep` e leitura pontual das funções, **sem** leitura integral do arquivo e **sem** instrumentação em runtime nesta rodada. "Sem achado" aí significa "o `grep` não achou", não "não existe".
- **Oponente real:** o goldfish não modela (convenção do repositório); nada aqui mede interação além do proxy já existente.

**Observação:** `mana_spent_this_turn` negativo em ~0,3% das partidas (62/20.000 padrão, 49 resiliência; 60 e 50 com a chave desligada): é a convenção do arquivo para mana extra de ritual (`Dark Ritual`: custa 1 e faz `mana_spent_this_turn -= 3`; `Culling the Weak`: `-= 4`; o contador negativo vira mana a gastar no turno), idêntica antes e depois, não um bug da correção. 0 exceções em 20.000 × 2 modos × 2 configurações; os invariantes genéricos (carta acima do número no baralho; contadores negativos) deram 0 violações.

---

## CR 903.9a: comandante dispara os 4 payoffs de aristocrata de verdade — 2026-09-21

**Gatilho:** usuário conferiu a regra real do CR 903.9 e apontou o erro
("comandantes podem ser mortos sim!"). Detalhes completos em
`checklist-oraculo.md` e `megatron-tyrant-mardu/checklist-oraculo.md`.

**Achado:** 2 pontos reais — `leave_battlefield` (chokepoint central,
comandante especial-casado pulava ele, igual Toph/Maralen) E o cálculo
manual de LKI (last known information) do `try_smart_opponent_wipe`,
que excluía o comandante EXPLICITAMENTE dos 4 payoffs (Zulaport/
Pitiless Plunderer/Syr Konrad/Species Specialist). Achado adicional: o
Rat King tem a tag "rat" (Legendary Creature — Rat Noble) — Species
Specialist também estava sendo silenciado, não só os outros 3.

**Resultado:** modo padrão idêntico (0/20000 mismatches). Modo de
resiliência (5000 seeds, A/B): `proxy_damage_total` médio
3,7574→3,8632; `tokens_created_total` médio 3,956→3,9978; `life` médio
36,4676→36,5378. Métricas de RNG puro (`smart_wipes_total`/`smart_
removals_total`) ficaram praticamente idênticas, confirmando
isolamento da correção.

**Validação:** regressão de 20.000 partidas em modo de resiliência, 0
exceções, 0 comandantes presos no cemitério + 5 testes dirigidos.

---

## Porte completo do modo de resiliência (interação de oponente) — 2026-09-21

**Gatilho:** "Vamos fazer a implementação no Verminister agora" — mesmo
modo já validado em Megatron/Ur-Dragon/Hei Bai/Edgar Markov/Ulalek/
Toph/Prismatic Bridge/Maralen. Detalhes técnicos completos em
`checklist-oraculo.md`.

**Achado real mais substancial da sessão nesta categoria**: aristocrats
+ simultaneidade real (CR 603.10). Um wipe matando Zulaport Cutthroat/
Pitiless Plunderer/Syr Konrad/Species Specialist JUNTO de outras
criaturas precisou de um recálculo manual via snapshot pra não
subcontar os gatilhos (o caminho genérico do arquivo removia uma
criatura de cada vez, então uma fonte de gatilho já removida no meio
do loop parava de "ver" as mortes seguintes no mesmo wipe). Corrigido
só dentro da função de wipe nova, sem tocar nada do modo padrão.

**Resultado (A/B 2000 jogos mesma seed_base):** vida final 38,11 →
36,24. Avg board wipes: 0,84, artifact: 0,20, enchantment: 0,08. Avg
proxy_damage_total cai de 5,74 pra 3,59 (a perda de board pra
interação supera o bônus do payoff simultâneo dos wipes).

**Validação:** modo padrão 100% bit-idêntico (3.000 seeds) + regressão
de 20.000 partidas, 0 exceções + 7 testes dirigidos, incluindo 3 casos
específicos do aristocrats simultâneo (Zulaport self-inclusiva +7 vida
com 7 mortes; Syr Konrad exclui só a própria morte, 4 de dano com 5
mortes; comandante junto de Zulaport no mesmo wipe nunca conta pro
total, só +1 vida).

---

### Auditoria oráculo-por-oráculo completa — 2026-09-13/14

Extensão pra este deck da mesma auditoria já feita no Megatron/Azula/
Beorn/Captain Storm/Edgar Markov/Hei Bai/Maralen/Kutzil/Nekusar/Ms.
Bumbleflower. Achado principal (detalhes completos em
`checklist-oraculo.md`, seção no topo): 4 habilidades de criatura com
`{T}` no custo real (Ayara, Marrow-Gnawer, Priest of Forgotten Gods, Rat
King) podiam ativar 2x por turno (`main_phase()` roda antes e depois do
combate, sem guarda de "já tapei esta criatura"); Piper of the Swarm era
pior ainda — um `while` loop criava tokens ILIMITADOS por turno com mana
sobrando, quando o `{T}` no custo real limita a 1 ativação por turno (o
maior gerador de "mana fantasma" do arquivo); Syr Konrad, the Grim tinha
2 das suas 3 cláusulas de dano nunca implementadas ("creature card put
into graveyard from anywhere other than battlefield" / "creature card
leaves your graveyard") e uma 2ª habilidade inteira ("{1}{B}: each
player mills a card") 100% ausente apesar da tag já existir desde a
construção original; Big Apple, 3 a.m. só ativava no turno em que era
jogado, nunca de novo depois.

### Métricas antes/depois (2.000 partidas, seed 9300000, turns=8, 0 exceções)

| Métrica | Antes | Depois |
|---|---|---|
| Avg Rats totais em campo (final) | 16.89 | 8.46 |
| Avg tokens criados | 13.55 | 4.76 |
| Avg reanimações via Rat King (sac 3 Rats) | 3.17 | 2.23 |
| Avg compras via Skullclamp | 0.93 | 0.82 |
| Avg eventos de recursão | 3.58 | 2.66 |
| Avg dano/dreno proxy total (finisher) | 5.75 | 4.89 |
| Avg mão final | 3.32 | 2.93 |

Regressão de 20.000 partidas (seed 9500000, turns=8): 0 exceções,
métricas estáveis com a amostra de 2.000 (Rats finais 8.73, dreno proxy
4.90). A queda grande em quase todas as métricas é o efeito esperado de
corrigir o bug do Piper of the Swarm (loop de tokens ilimitado) — ele
sozinho inflava tokens/Rats/reanimações/recursão de forma irreal; mesmo
com Syr Konrad ganhando 2 cláusulas novas de dano, o dreno total ainda
caiu porque a base de Rats disponível pra alimentar o motor de
sacrifício (Ayara/Zulaport/aristocrats) ficou muito menor sem a
inflação do Piper.

### Auditoria linha-a-linha "compile TUDO" — 2026-09-01

**Gatilho:** pedido direto do usuário ("AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha") — mesmo tratamento já aplicado a
Toph, Beorn, Edgar Markov, Hei Bai, Maralen, Megatron, Nekusar e Prismatic
Bridge nesta sessão. Ver `checklist-oraculo.md` (novo) pra detalhamento
completo carta-a-carta.

**Método:** detecção automatizada de tags definidas em `add()` que nunca
aparecem em nenhum `if`/`elif` de despacho no resto do arquivo (esta
arquivo despacha primariamente por tag, não por nome literal). Achou 3
gaps reais que a auditoria de construção original (2026-08-31) tinha
deixado passar:

1. **Species Specialist** (`death_draw_type`) — "Whenever a creature of
   the chosen type dies, you may draw a card" nunca disparava. Corrigido
   centralizando em `on_creature_dies()`, que agora recebe
   `dying_is_rat: bool` propagado pelos 4 pontos reais de morte
   (`leave_battlefield()`, ramo de esquilo em `sacrifice_any_creature()`,
   loop de Skullclamp — agora rastreia qual token realmente morreu — e
   `sacrifice_rats()`, que já só sacrifica Rats reais). Tipo escolhido =
   Rat, tema tribal central do deck.
2. **Deadly Rollick** (`free_removal_commander`) — "If you control a
   commander, you may cast this spell without paying its mana cost."
   nunca implementado, sempre pagava o custo cheio (MV4, {3}{B}).
   Corrigido em `effective_cost()`.
3. **Takenuma, Abandoned Mire** (`takenuma`) — só o `{T}: Add {B}`
   genérico estava coberto; a habilidade de Channel ("Discard this card:
   Mill three cards, then return a creature or planeswalker card from
   your graveyard to your hand", custo reduzido por lendária controlada)
   nunca implementada. Corrigido com `try_takenuma_channel()` + novo
   conjunto `LEGENDARY_CREATURES` (7 criaturas, verificadas via
   Scryfall). Só ativa quando sobra outro terreno na mão nesse turno
   (não perde o land drop).

**Validação:** 7 testes unitários isolados (todos passando) + regressão
de 20.000 partidas (seed 1000000+, turns=10, 0 exceções) + `run_batch`
antes/depois via `importlib` (5000 jogos, seed 4000000, turns=10):

| Métrica | Antes | Depois |
|---|---|---|
| DRAW (compras extras) | 6.12 | 8.18 |
| INTERACTION (spells de interação) | 1.01 | 1.15 |
| RECURSION (eventos de recursão) | 7.64 | 7.91 |
| Tokens criados | 223.80 | 239.37 |
| Vida final média | 59.67 | 63.72 |
| Mão final média | 4.40 | 5.48 |

Todas as 3 métricas relevantes subiram na direção esperada, sem nenhuma
outra métrica se mover de forma inexplicável (turno de conjuração do
comandante, mulligans e Thrumming Stone ripple ficaram praticamente
estáveis, como esperado — nenhum dos 3 fixes toca essas mecânicas).

Demais cartas: confirmadas ✅ implementadas ou 📊 estruturais de verdade
(Dictate of Erebos, Kindred Dominance/Swarmyard Massacre/Damnation,
Piper of the Swarm's steal, Karumonix toxic — todos opponent-dependent
ou combat-dependent, sem oponente/combate real neste goldfish solo,
já documentado no código desde 2026-08-31, não achados novos).

---

### Correção — lista completada com Damnation (100ª carta) + bug real nos wipes — 2026-08-31

**Contexto:** o usuário mandou 3 versões diferentes da lista pra comparar
(uma delas era a mesma lista com Emeritus of Woe e Demonic Tutor contados
como 2 cartas por engano — mesmo erro já corrigido em 2026-08-20 — e outra
trocava Emeritus of Woe por Demonic Tutor avulso + 5 outras cartas). O
usuário confirmou: manter Emeritus of Woe // Demonic Tutor como está, sem
aplicar as outras trocas.

**Escolha da 100ª carta:** sugeri Toxic Deluge (wipe escalável, mais barato
e sinergiza com o motor de vida do deck). O usuário contrapôs — pra
eliminar ameaças **grandes** de verdade, Toxic Deluge exige pagar vida
igual ou maior que a toughness do alvo, o que fica caro/arriscado contra
uma ameaça realmente grande; Damnation mata qualquer coisa por custo fixo,
sem escalar com o tamanho do alvo. Argumento tecnicamente correto — troquei
a sugestão. **Damnation adicionado como a 100ª carta.**

**Bug real encontrado ao implementar o Damnation:** ao decidir como modelar
o "destroy all creatures" dele, percebi que `Kindred Dominance` e
`Swarmyard Massacre` (já na lista) tinham a mesma falha — a versão anterior
do simulador destruía de verdade as próprias criaturas não-Rat do jogador
(Ayara, Gray Merchant, Syr Konrad, Species Specialist etc.) toda vez que
essas cartas eram conjuradas, mesmo sem nenhum oponente real em campo pra
justificar o wipe. Isso é estritamente irracional — nenhum piloto de
verdade sacrifica o próprio motor de valor por zero ganho. Corrigido: os
3 wipes (Kindred Dominance, Swarmyard Massacre, Damnation) agora contam
como "conjurados" pra métrica de interação, mas não destroem mais nada do
próprio board — mesma convenção já usada em Withering Torment/Deadly
Rollick (paga o custo, sem efeito de combate real por falta de alvo). O
token de Esquilo do Swarmyard Massacre (benefício incondicional) continua
real.

**Robustez:** 20.000 partidas (seeds 9400000-9419999, timeout 2s/jogo) —
0 erros, 0 timeouts.

**n=3000, seed_base=9300000 — antes (98 cartas, wipes destrutivos) →
depois (100 cartas, Damnation, wipes corrigidos):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg Rats totais em campo (final) | 14,87 | **17,28** |
| Avg tokens criados | 11,61 | **14,03** |
| Avg compras via Skullclamp | 0,74 | 0,85 |
| Avg tutores usados | 0,76 | 0,79 |
| Avg mão final | 2,85 | 3,00 |
| DRAW | 2,32 | 2,50 |
| INTERACTION (agora inclui Damnation) | 0,49 | **0,59** |
| RECURSION | 3,75 | 3,51 |
| FINISHER/LETHALITY (dreno proxy) | 4,95 | **5,19** |

Leitura: o board de Rats sobrevive bem mais (14,87→17,28) porque os wipes
pararam de se autodestruir — Ayara/Gray Merchant/Syr Konrad continuam em
campo drenando por mais turnos, o que também explica o FINISHER/LETHALITY
subir. Deltas pequenos e rastreáveis no resto.

`lista.md` agora tem 100/100 cartas — comandante + 99 de biblioteca.
`ratking_v1_runs.jsonl` sobrescrito (3000 jogos).

---

### Simulação #1 — goldfish Python completo (`ratking_goldfish_v1.py`) — 2026-08-31

**Contexto:** simulador construído do zero a pedido direto do usuário
("faça a análise e crie o simulador sem erros do Verminister"). Passo 0
(checklist de `references/goldfish-sim-card-rules.md`): oráculo real das
53 cartas únicas da lista consultado via `scryfall-cache/oracle-cache.json`
(2 cartas ausentes do cache — Fell the Profane // Fell Mire e Priest of
Forgotten Gods — buscadas na API real da Scryfall e adicionadas antes de
qualquer implementação).

**2 correções reais de grafia em `lista.md`** (mesmo padrão do erro já
corrigido antes nesta lista pra Emeritus of Woe/Demonic Tutor, confirmadas
via Scryfall, não presumidas):
- `Priest of the Forgotten Gods` → **`Priest of Forgotten Gods`** (nome
  real não tem "the" — a busca exata pela grafia antiga retornava
  `not_found` na API).
- `Fell the Profane` → **`Fell the Profane // Fell Mire`** — é uma MDFC
  verdadeira (`layout: modal_dfc`, Instant // Land), o nome sem o verso
  não é o nome completo real da carta.

**⚠️ Lista ainda incompleta — não inventado aqui:** `lista.md` já tinha
uma nota própria avisando que a lista está em 99/100 cartas (98 de
biblioteca + comandante, falta 1 carta que o usuário ainda vai escolher).
O simulador reflete a lista REAL como está — `BASE_LIBRARY` tem 98 cartas,
não 99 — `build_library()` faz `assert len(lib) == 98` (não 99) pra não
mascarar o buraco fingindo uma carta que não existe. **Isso significa que
o simulador não pode ser tratado como "final" até a 100ª carta ser
escolhida** — os números abaixo são válidos pra lista atual, mas vão
mudar quando a carta 100 entrar.

**Motores principais implementados de verdade (não só tag), checklist de
13 categorias completo desde a construção inicial (não retrofit):**
- Rat Colony (24x, "+1/+0 por outro Rat") — escala com `rat_count()` real.
- Skullclamp + geradores de token — loop real de equipar/sacrificar por
  {1}, compra 2.
- Cabal Coffers + Urborg, Tomb of Yawgmoth + Crypt Ghast — combo clássico
  modelado com precisão, incluindo o próprio Cabal Coffers virando fonte
  de "tap de Swamp" pro Crypt Ghast dobrar quando Urborg está em campo.
- Thrumming Stone + Rat Colony (ripple 4) — a peça mais explosiva do
  deck (auditoria.md, seção 8), disparo real a cada magia conjurada.
- Aristocrats/dreno (Zulaport, Ayara, Pitiless Plunderer, Priest of
  Forgotten Gods, Dictate of Erebos, Syr Konrad) — despachados a partir
  de um único ponto central (`on_creature_dies()`), sem duplicar gatilho.
- Devoção ao preto real (soma de pips {B}, não aproximação) — Gray
  Merchant, Nykthos.
- The Soul Stone (Harness) — ativação única liga motor de reanimação
  repetível real todo upkeep.
- Emeritus of Woe // Demonic Tutor — layout real `prepare` (Scryfall
  confirmado), condição de 2+ mortes no turno, custo real pago (não de
  graça) ao usar a cópia do Demonic Tutor.
- Ninja Teen (Classe, 3 níveis reais, nível 3 = motor de recursão via
  sneak do cemitério).
- Rat King, Verminister (comandante): "Disappear" (token + contador
  quando um permanente seu sai de campo) + a habilidade de reanimação
  (sac 3 Rats, traz de volta 1 criatura E todas as cópias do mesmo nome
  do cemitério — devastador com Rat Colony).

**Simplificações documentadas (não inventadas):** sem oponente real,
qualquer efeito "opponent loses life"/edict/toxic fica disponível com
contador de disparo mas sem efeito numérico do lado do oponente (mesma
convenção de todos os simuladores desta sessão) — o ganho de vida
próprio (Zulaport, Ayara, Valley Rotcaller, Gray Merchant) é real.
Fell the Profane // Fell Mire registrada só pela face Instant (remoção é
o gap real do deck, 35 terrenos já bastam). Toxic 1 do Karumonix é N/A
estrutural (sem combate real contra oponente). Thornbite Staff sem
nenhuma criatura Shaman na lista — auto-attach nunca dispara, N/A.

**Robustez:** 20.000 partidas (seeds 9300000-9319999, timeout 2s/jogo) —
0 erros, 0 timeouts.

**n=3000, seed_base=9300000, 8 turnos — resultado oficial:**

```
Avg mulligans: 0.31
Turno medio de conjuracao do Rat King: 2.13 | mediana: 2.0
Nunca conjurado em 8 turnos: 0.3%
Avg Rats totais em campo (final): 14.87
Avg tokens criados: 11.61
Avg reanimacoes via Rat King (sac 3 Rats): 3.35
Avg casts gratis via Thrumming Stone (ripple 4): 0.36
Avg compras via Skullclamp: 0.74
Avg nivel final do Ninja Teen: 0.26
Soul Stone harnessed: 4.3% dos jogos
Avg tutores usados: 0.76
Avg vida final: 38.96
Avg mao final: 2.85

--- Metricas basicas (checklist obrigatorio) ---
RAMP: 0.63
DRAW: 2.32
INTERACTION: 0.49
RECURSION: 3.75
FINISHER/LETHALITY (dreno proxy): 4.95
```

**Leitura:** curva muito rápida (comandante em {1}{B}, conjurada em
média no turno 2,13, quase nunca falha em resolver — 0,3% em 8 turnos).
RECURSION alta (3,75/jogo) reflete o motor de reanimação central do
comandante somado a Echoing Return/Secret Salvage/Reanimate — todos
potencializados pelas 24 cópias de Rat Colony no cemitério. Thrumming
Stone só dispara casts grátis em 36% dos jogos em média (0,36) — a
"explosão" citada na auditoria.md depende de já ter Thrumming Stone em
campo E revelar Rat Colony no topo, evento condicional, não garantido.
Skullclamp com só 0,74 compras médias é mais modesto do que a auditoria
sugere ("motor de draw quase sem fim") — o loop de equipar/sacrificar
roda DEPOIS do loop principal de conjuração no `main_phase()`, então só
usa mana que sobrou depois de gastar em ameaças reais primeiro; pode
estar subestimado por essa ordem de prioridade — candidato a revisão
numa próxima rodada.

`lista.md` corrigida (2 erros de grafia). `ratking_v1_runs.jsonl`
criado (3000 jogos).

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
