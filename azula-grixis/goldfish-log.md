# Goldfish Log — Fire Lord Azula

> **Rodada 2026-10-05 (Terreno virado primeiro em T1/T2 (varredura de 2026-10-05)) — dados brutos e reprodução:** [`resultados-ab/2026-10-05-terreno-virado-primeiro/LEIAME.md`](resultados-ab/2026-10-05-terreno-virado-primeiro/LEIAME.md)

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Terreno virado primeiro em T1/T2 (varredura de 2026-10-05) — 2026-10-05

**Pedido do usuário:** *"Com base nos erros encontrados nas ultimas revisões, reanálise todos os outros decks em busca de erros semelhantes, e os corrija"*. Arquivo bruto/auditável: `resultados-ab/2026-10-05-terreno-virado-primeiro/` (`LEIAME.md`).

**Veredito:** um erro real, um conserto, bit-idêntico com a chave desligada e com o ensaio sem efeito colateral (modo GHOST). Modo padrão, N=10.000: comandante em campo até T3 14,2% → 14,6% (+0,42 ± 0,27 pp), até T4 +2,87 ± 0,53 pp, até T5 +0,95 ± 0,33 pp; comandante que nunca chega a entrar na partida -0,18 ± 0,11 pp. Modo resiliência: comandante em campo até T3 13,3% → 13,7% (+0,34 ± 0,26 pp), até T4 +2,73 ± 0,52 pp, até T5 +1,16 ± 0,38 pp; comandante que nunca chega a entrar na partida -0,23 ± 0,13 pp. A correção joga o terreno virado primeiro em média 0,45 vez(es) por partida (N=10.000, padrão) e o ensaio impede 0,13 vez(es) por partida (teria custado uma jogada).

**Achado (varredura das classes de erro do Vihaan/Megatron neste simulador):**
- **Terreno que entra virado nunca é jogado primeiro.** `play_land` jogava sempre o primeiro terreno da ordem própria do deck (desvirado antes de virado). Em T1/T2, sem nada pra conjurar, a mana do turno era desperdiçada enquanto o terreno que entra virado ficava na mão pra um turno em que ele custa desenvolvimento. Mesmo erro achado e corrigido no Vihaan e no Megatron (2026-10-03/04).

**O que mudou:**
- `TAPPED_LAND_FIRST_ENABLED` (padrão `True`), `TAPPED_LAND_FIRST_MAX_TURN = 2`: em T1..T2, havendo terreno virado E desvirado na mão, `tapped_first_pick` joga o virado, **salvo se isso custar desenvolvimento**: o teste é um ENSAIO a seco da própria fase de conjuração pré-combate do deck (cópia profunda do estado; `CARD_DB` compartilhado; RNG do estado copiado; `random` global restaurado), comparando o MV total das cartas que saem da mão com cada candidato. Empate → o virado. Dentro de cada grupo vale a ordem própria do deck (cor mais escassa etc.). Contadores novos no estado: `tapped_land_first_plays_total` (jogou o virado) e `tapped_land_skipped_for_play_total` (o ensaio mostrou que custaria uma jogada e jogou o desvirado). `TAPPED_LAND_FIRST_GHOST` só existe pra validação (roda o ensaio e ignora o resultado). Com a chave em `False` o caminho antigo volta bit a bit.
- Faces de MDFC jogadas como terreno ficam fora do dilema virado × desvirado (jogar a face de terreno custa a magia: decisão à parte, inalterada).

**Medido (pareado, mesmas sementes; IC95% = 1,96·dp/√N da diferença):**

Modo padrão, N=10.000 (`resumos/ab_10000.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 5925 (59.2%)
   campo                                          base     variante dif. pareada (IC95%)
  *commander_cast_turn__nunca                   0.0296       0.0278      -0.0018 ±0.0011  
  *commander_cast_turn__ate_T3                  0.1417       0.1459      +0.0042 ±0.0027  
  *commander_cast_turn__ate_T4                  0.5968       0.6255      +0.0287 ±0.0053  
  *commander_cast_turn__ate_T5                  0.7999       0.8094      +0.0095 ±0.0033  
  *commander_damage_win                         0.6174       0.6431      +0.0257 ±0.0051  
  *azula_commander_damage_dealt                21.3037      21.5147      +0.2110 ±0.0477  
  *len_battlefield                             15.0861      15.1409      +0.0548 ±0.0285  
  *skitterspike_counters                        1.5070       1.5320      +0.0250 ±0.0138  
  *skitterspike_monstrous                       0.3014       0.3064      +0.0050 ±0.0028  
  *commander_cast_turn__ate_T6                  0.8775       0.8819      +0.0044 ±0.0025  
  *azula_copy_events_total                      1.8621       1.8959      +0.0338 ±0.0197  
  *commander_cast_count                         0.9704       0.9722      +0.0018 ±0.0011  
  *commander_in_play                            0.9704       0.9722      +0.0018 ±0.0011  
  *len_creature_cast_turn                       5.6345       5.6646      +0.0301 ±0.0187  
  *ascension_quest_counters                     0.4938       0.5061      +0.0123 ±0.0083  
  *interaction_plays                            2.3047       2.3198      +0.0151 ±0.0119  
  *skitterspike_pings_total                     1.3688       1.3984      +0.0296 ±0.0247  
  *ascension_copies_total                       0.3917       0.3959      +0.0042 ±0.0035
```
Modo resiliência, N=10.000 (`resumos/ab_10000_resiliencia.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 5925 (59.2%)
   campo                                          base     variante dif. pareada (IC95%)
  *commander_cast_turn__nunca                   0.0357       0.0334      -0.0023 ±0.0013  
  *commander_cast_turn__ate_T3                  0.1334       0.1368      +0.0034 ±0.0026  
  *commander_cast_turn__ate_T4                  0.5578       0.5851      +0.0273 ±0.0052  
  *commander_cast_turn__ate_T5                  0.7713       0.7829      +0.0116 ±0.0038  
  *azula_commander_damage_dealt                18.2165      18.3862      +0.1697 ±0.0527  
  *commander_cast_turn__ate_T6                  0.8576       0.8644      +0.0068 ±0.0028  
  *commander_cast_count                         1.6769       1.6952      +0.0183 ±0.0084  
  *commander_damage_win                         0.3343       0.3439      +0.0096 ±0.0047  
  *azula_copy_events_total                      1.3358       1.3624      +0.0266 ±0.0145  
  *len_smart_wipe_log                           0.8143       0.8256      +0.0113 ±0.0071  
  *smart_wipes_total                            0.8143       0.8256      +0.0113 ±0.0071  
  *life                                        37.7036      37.6755      -0.0281 ±0.0181  
  *len_hand                                     1.1806       1.1566      -0.0240 ±0.0169  
  *zada_extra_draws_total                       0.8406       0.7719      -0.0687 ±0.0539  
  *len_battlefield                             10.6474      10.6784      +0.0310 ±0.0254  
  *len_smart_graveyard_snipe_log                0.3580       0.3653      +0.0073 ±0.0061  
  *smart_graveyard_snipes_total                 0.3580       0.3653      +0.0073 ±0.0061  
  *ascension_quest_counters                     0.3682       0.3772      +0.0090 ±0.0077
```
Os lotes de N=2.000 (`ab_2000*.txt`) e as variantes de sensibilidade (uma correção por vez) estão em `resumos/`.

**Raciocinado (não medido):** o ganho esperado é pequeno e concentrado em T1–T3: só muda a partida quando a mão tem terreno virado E desvirado e nenhuma jogada de T1/T2 que o terreno desvirado pague (nesses casos o terreno virado deixa de ficar parado na mão até um turno em que atrasaria o desenvolvimento).

**Validação:** smoke (99 cartas, 0 desconhecidas, 0 duplicadas não-básicas, 200 partidas × 2 modos sem exceção); bit-identidade com as chaves desligadas × `azula_goldfish_v1_ANTES_687b8ba.py`, 20.000 partidas × 2 modos (`resumos/bitident_20000.txt`); regressão 20.000 × 2 modos × 2 configurações, 0 exceções (`resumos/regressao_20000.txt`); testes dirigidos 8/8 (`resumos/testes_dirigidos.txt`); ghost (chave ligada + ensaio ignorado == desligada), 20.000 × 2 modos (`resumos/ghost_20000.txt`); reprodutibilidade por `cmp` (`resumos/verificacao_reproducao.txt`).

**Escopo — verificado:**
- **Terreno virado primeiro:** leitura de `play_land` (+ predicado de entrada virada do deck); testes dirigidos TL1–TL8 (escolha com/sem jogada em T1, chave desligada, T3, só um tipo na mão, ensaio sem efeito no estado/RNG/`random`, modo GHOST, integração em `play_land`); A/B pareado 2.000 e 10.000 nos dois modos.
- **Ensaio sem efeito colateral:** com a chave ligada + modo GHOST (roda o ensaio e ignora o resultado) o resultado é idêntico a tudo desligado, 20.000 × 2 modos (`resumos/ghost_20000.txt`).
- **Bit-identidade** com as chaves desligadas × snapshot: 20.000 partidas × 2 modos, impressão digital do resultado inteiro.
- **Regressão** 20.000 × 2 modos × 2 configurações: 0 exceções.
- **MDFC:** teste TL7/leitura de `play_land`: `hand_lands[0]` MDFC mantém o caminho antigo.

**Escopo — NÃO verificado:**
- **Condições de entrada dos terrenos** além do que a varredura mecânica cobriu (`varredura-2026-10-05/`: cenário de campo vazio + cenário condição satisfeita × violada para os padrões "unless you control …"/reveal; terrenos que o `CARD_DB` do deck não tem como básico foram pulados e estão listados lá).
- **Resto da taxonomia da Regra #1 neste arquivo** (caminhos de conjuração fora da mão e "whenever you cast", sacrifício × destroy, cascade, contadores `_sick` agregados, fórmulas dinâmicas achatadas): varrido na triagem de 2026-10-05 por `grep` e leitura pontual das funções, **sem** leitura integral do arquivo e **sem** instrumentação em runtime nesta rodada. "Sem achado" aí significa "o `grep` não achou", não "não existe".
- **Oponente real:** o goldfish não modela (convenção do repositório); nada aqui mede interação além do proxy já existente.

**Observação:** 0 exceções em 20.000 × 2 modos × 2 configurações; os invariantes genéricos (carta acima do número no baralho; contadores negativos) deram 0 violações.

---

## Porte completo do modo de resiliência + CR 903.9a nativa desde o início — 2026-09-21

**Gatilho:** "Agora o deck da Azula" — seguindo o porte concluído no
Vihaan e no Nekusar. Detalhes completos em `checklist-oraculo.md` e
`megatron-tyrant-mardu/checklist-oraculo.md`.

**Achado:** 3º deck desta sessão a nascer com CR 903.9a correta desde o
início. Sem impacto numérico (0 cartas "creature dies" — deck
spellslinger/magecraft/storm, não aristocrata). 1 token agregado real
(Treasures) tratado no wipe de artefato.

**Resultado:** modo padrão idêntico ao commit anterior (0/20000
mismatches, isolando o fix de determinismo abaixo).

**Validação:** regressão de 20.000 partidas em modo de resiliência, 0
exceções, 0 comandantes presos no cemitério + 6 testes dirigidos.

---

## Achado adicional: `mulligan()` não era determinística — bug pré-existente sério, não relacionado ao comandante — 2026-09-21

**Gatilho:** validação de bit-identidade do porte acima revelou que
`mulligan()` reembaralhava a biblioteca com o módulo `random` GLOBAL
(sem seed própria) sempre que um 2º+ mulligan acontecia — `simulate_
one(seed)` **não era determinística**: 953/5.000 seeds (19,1%)
retornavam resultado diferente rodando a MESMA seed 2 vezes. Qualquer
`run_batch`/goldfishing anterior deste deck pode ter tido resultados
não totalmente reproduzíveis.

**Corrigido:** `state.rng` (mesmo padrão dos outros 11 decks) agora
alimenta TODA aleatoriedade do jogo, incluindo o reembaralhamento de
mulligan.

**Validação:** 0/N resultados diferentes depois do fix (era 953/5000
antes), confirmado via teste dirigido.

---

## Achado adicional: `state.life` nunca existiu neste arquivo — 2026-09-21

**Gatilho:** ao implementar a categoria "ataque de oponente" do modo
de resiliência, achei que este deck nunca rastreou a própria vida (nem
fetches/shock lands descontam) — diferente de todos os outros 11
decks. Simplificação pré-existente real, não um bug introduzido por
mim.

**Corrigido:** adicionado `life: int = 40` ao `GameState` (aditivo, só
usado pela nova categoria de ataque — não muda nenhum comportamento
pré-existente, confirmado pela bit-identidade 0/20000 acima).

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

## 2026-09-02 — Simulador goldfish construído do zero (`azula_goldfish_v1.py`)

Segundo dos 4 decks sem simulador desta sessão a ser fechado (depois do
Kutzil). Detalhamento completo carta-a-carta em `checklist-oraculo.md`.

**Metodologia:** oráculo real via Scryfall (line-by-line, "compile
TUDO"), implementação, testes unitários (13 no total, 2 arquivos), 3
rodadas de correção após varredura automatizada de tags órfãs + 1 bug de
regra (706.10, valor de X em cópias) achado por análise de um outlier
estatístico, regressão de 20.000 partidas (0 exceções, ~18.5s).

**Achado mais grave da sessão inteira até agora:** o comandante nunca
entrava em campo no primeiro rascunho (faltava o passo de conjurar da
zona de comando — `BASE_LIBRARY` corretamente não inclui Azula, mas
nada a conjurava de lá). Isso zerava o motor central do deck inteiro
(Firebending + cópia de magia ao atacar). Achado ao verificar
`azula_copy_events_total == 0` em 2.000 partidas seguidas (suspeito
demais pra ser aleatoriedade) e confirmado rastreando presença de Azula
em campo: **0/500** antes do fix, **474/500 (~95%)** depois. Ver
checklist-oraculo.md item 1.

**Motor real deste deck** (Storm + Magecraft + o combo composto
Zada+Azula+Veyran, onde Veyran dobra os gatilhos do Zada e da Azula, não
só o próprio Magecraft dela) é categoricamente diferente de qualquer
outro simulador desta sessão — nenhum outro deck tem esse tipo de
motor de multiplicação de gatilhos por conjurar magia.

### Métricas (20.000 partidas, seed 5.000.000+, turns=10, 0 exceções)

| Métrica | Média | Mediana |
|---|---|---|
| Dano proxy total | 1586.2 | 70.0 |
| Cartas compradas extra | 28.0 | — |
| Treasures criados | 12.4 | — |
| Eventos de cópia do Zada | 0.7 | — |
| Cópias via Azula atacando | 1.7 | — |
| Dobras via Veyran | 8.9 | — |
| Grapeshots conjurados | 0.31 | — |
| Maior dano de 1 Grapeshot (max entre partidas) | — | 46 |
| Biblioteca esgotada | 2695/20000 (13.5%) | — |

**Nota sobre a diferença grande entre média e mediana:** o motor
Zada+Veyran+Storm-Kiln Artist tem uma combinação genuinamente explosiva
e rara — quando as 3 peças estão em campo simultaneamente com um board
largo, cada magia de alvo único gera mais Treasures (via os gatilhos
duplos de Magecraft em cada cópia) do que custou pra conjurar, permitindo
jogar a mão inteira e puxar o deck inteiro no mesmo turno. Isso é uma
linha de combo real e conhecida deste arquétipo em Magic de papel (não
um bug de simulação) — confirmado rápido (poucos ms por partida, sem
travamento) e determinístico por seed. Mesmo tratamento dado ao outlier
do Ouroboroid no Kutzil: documentado como achado real, não suprimido
artificialmente.

---

## Auditoria oráculo-por-oráculo completa — 2026-09-13

Extensão pra este deck da mesma auditoria já feita no Megatron: oráculo
real via Scryfall pras 63 cartas + 20 terrenos + comandante, comparação
cláusula-por-cláusula contra o código, 9 gaps reais corrigidos (detalhes
completos em `checklist-oraculo.md`, seção no topo): mana colorida das 3
rocks (Signet/Talisman/Tablet) não contava pra checagem de cor; Grixis
Panorama crackeava de graça (devia custar `{1}`); 5 mágicas com "discard
a card" como custo adicional obrigatório podiam ser conjuradas com a mão
vazia; Fists of Flame tinha o pump fixo em +1/0 em vez de escalar com
cartas compradas no turno; Frantic Search não passava seus draws por
`draw_cards()` (undercounting de métricas) e descartava as cartas
ERRADAS (maior custo, não menor); o token do Firebender Ascension nunca
gerava o próprio mana de Firebending 1 ao atacar; Sazacap's Brew recusava
o gift sem necessidade (sem desvantagem real modelada pra dar o token ao
oponente); e Lunar Frenzy calculava o pump de X mas nunca gastava esse
mana de verdade (bug de mana fantasma reaproveitável).

### Métricas antes/depois (20.000 partidas, seed 5.000.000, turns=10, 0 exceções)

| Métrica | Antes | Depois |
|---|---|---|
| Dano proxy médio | 1586.2 | 2931.9 |
| Dano proxy mediano | 70.0 | 75.0 |
| Cartas compradas extra (média) | 28.0 | 30.4 |
| Treasures criados (média) | 12.4 | 15.8 |
| Cópias via Azula atacando (média) | 1.7 | 1.8 |
| Dobras via Veyran (média) | 8.9 | 10.7 |
| Biblioteca esgotada | 2695/20000 (13.5%) | 3207/20000 (16.0%) |

A mediana subiu pouco (~7%, o jogo "típico" mudou pouco) — a média subiu
bem mais porque os gaps corrigidos (mais mana colorida real disponível
via rocks, X realmente pago, Fists escalando de verdade) alimentam ainda
mais a cauda extrema do combo Zada+Veyran+Storm-Kiln Artist já documentado
acima, não porque o comportamento típico do deck mudou de categoria.

