# Goldfish Compilado — Kutzil, Malamet Exemplar

> **Rodada 2026-10-05 (Terreno virado primeiro em T1/T2 (varredura de 2026-10-05)) — dados brutos e reprodução:** [`resultados-ab/2026-10-05-terreno-virado-primeiro/LEIAME.md`](resultados-ab/2026-10-05-terreno-virado-primeiro/LEIAME.md)

## Terreno virado primeiro em T1/T2 (varredura de 2026-10-05) — 2026-10-05

**Pedido do usuário:** *"Com base nos erros encontrados nas ultimas revisões, reanálise todos os outros decks em busca de erros semelhantes, e os corrija"*. Arquivo bruto/auditável: `resultados-ab/2026-10-05-terreno-virado-primeiro/` (`LEIAME.md`).

**Veredito:** um erro real, um conserto, bit-idêntico com a chave desligada e com o ensaio sem efeito colateral (modo GHOST). Modo padrão, N=10.000: (campos do comandante ausentes). Modo resiliência: comandante em campo até T3 75,2% → 75,6% (+0,37 ± 0,45 pp), até T4 +0,00 ± 0,19 pp, até T5 +0,02 ± 0,14 pp; comandante que nunca chega a entrar na partida +0,08 ± 0,09 pp. A correção joga o terreno virado primeiro em média 0,34 vez(es) por partida (N=10.000, padrão) e o ensaio impede 0,47 vez(es) por partida (teria custado uma jogada).

**Achado (varredura das classes de erro do Vihaan/Megatron neste simulador):**
- **Terreno que entra virado nunca é jogado primeiro.** `play_land` jogava sempre o primeiro terreno da ordem própria do deck (desvirado antes de virado). Em T1/T2, sem nada pra conjurar, a mana do turno era desperdiçada enquanto o terreno que entra virado ficava na mão pra um turno em que ele custa desenvolvimento. Mesmo erro achado e corrigido no Vihaan e no Megatron (2026-10-03/04).

**O que mudou:**
- `TAPPED_LAND_FIRST_ENABLED` (padrão `True`), `TAPPED_LAND_FIRST_MAX_TURN = 2`: em T1..T2, havendo terreno virado E desvirado na mão, `tapped_first_pick` joga o virado, **salvo se isso custar desenvolvimento**: o teste é um ENSAIO a seco da própria fase de conjuração pré-combate do deck (cópia profunda do estado; `CARD_DB` compartilhado; RNG do estado copiado; `random` global restaurado), comparando o MV total das cartas que saem da mão com cada candidato. Empate → o virado. Dentro de cada grupo vale a ordem própria do deck (cor mais escassa etc.). Contadores novos no estado: `tapped_land_first_plays_total` (jogou o virado) e `tapped_land_skipped_for_play_total` (o ensaio mostrou que custaria uma jogada e jogou o desvirado). `TAPPED_LAND_FIRST_GHOST` só existe pra validação (roda o ensaio e ignora o resultado). Com a chave em `False` o caminho antigo volta bit a bit.
- Faces de MDFC jogadas como terreno (`MDFC_LAND_SPELLS`) ficam fora do dilema virado × desvirado (decisão à parte, inalterada).

**Medido (pareado, mesmas sementes; IC95% = 1,96·dp/√N da diferença):**

Modo padrão, N=10.000 (`resumos/ab_10000.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 6782 (67.8%)
   campo                                          base     variante dif. pareada (IC95%)
  *commander_cast_turn__ate_T3                  0.7983       0.8035      +0.0052 ±0.0044  
   commander_cast_turn__ate_T4                  0.9152       0.9150      -0.0002 ±0.0004  
  *commander_uid                                5.2677       5.3689      +0.1012 ±0.0121  
  *warp_plot_free_casts_total                   0.0511       0.0598      +0.0087 ±0.0022  
  *recursion_events_total                       0.0434       0.0515      +0.0081 ±0.0022  
  *interaction_plays                            1.1827       1.2043      +0.0216 ±0.0061  
  *saddle_activations_total                     0.9768       0.9863      +0.0095 ±0.0038  
  *len_hand                                     3.2700       3.2492      -0.0208 ±0.0092  
  *proxy_damage_total                         136.1272     138.4894      +2.3622 ±1.4321  
  *restoration_seminar_active                   0.0590       0.0608      +0.0018 ±0.0014  
  *next_uid                                    18.6979      18.7242      +0.0263 ±0.0199  
  *cards_drawn_extra                           14.0432      14.0625      +0.0193 ±0.0152  
  *counters_placed_total                       64.4833      65.8685      +1.3852 ±1.1031  
  *len_library                                 76.0629      76.0373      -0.0256 ±0.0207  
  *len_graveyard                                0.1427       0.1460      +0.0033 ±0.0027  
   len_exile_warp                               0.0105       0.0112      +0.0007 ±0.0007
```
Modo resiliência, N=10.000 (`resumos/ab_10000_resiliencia.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 6782 (67.8%)
   campo                                          base     variante dif. pareada (IC95%)
   commander_cast_turn__nunca                   0.0370       0.0378      +0.0008 ±0.0009  
   commander_cast_turn__ate_T3                  0.7525       0.7562      +0.0037 ±0.0045  
   commander_cast_turn__ate_T4                  0.8664       0.8664      +0.0000 ±0.0019  
   commander_cast_turn__ate_T5                  0.9113       0.9115      +0.0002 ±0.0014  
  *warp_plot_free_casts_total                   0.0553       0.0635      +0.0082 ±0.0023  
  *recursion_events_total                       0.0579       0.0671      +0.0092 ±0.0027  
  *len_hand                                     2.4327       2.4042      -0.0285 ±0.0119  
  *interaction_plays                            0.8110       0.8247      +0.0137 ±0.0062  
   len_smart_wipe_log                           0.9084       0.9135      +0.0051 ±0.0055  
   smart_wipes_total                            0.9084       0.9135      +0.0051 ±0.0055  
   len_botanical_brawler_first_counter_this_turn       0.0006       0.0003      -0.0003 ±0.0003  
   mikey_leo_drawn_this_turn                    0.0010       0.0013      +0.0003 ±0.0003  
   len_battlefield                             10.4865      10.4577      -0.0288 ±0.0329  
   len_exile_warp                               0.0141       0.0150      +0.0009 ±0.0011  
   commander_cast_count                         1.5590       1.5627      +0.0037 ±0.0047  
   len_smart_counter_log                        0.1012       0.1036      +0.0024 ±0.0030  
   smart_counters_total                         0.1012       0.1036      +0.0024 ±0.0030  
   ramp_pieces_in_play                          1.1469       1.1447      -0.0022 ±0.0028
```
Os lotes de N=2.000 (`ab_2000*.txt`) e as variantes de sensibilidade (uma correção por vez) estão em `resumos/`.

**Raciocinado (não medido):** o ganho esperado é pequeno e concentrado em T1–T3: só muda a partida quando a mão tem terreno virado E desvirado e nenhuma jogada de T1/T2 que o terreno desvirado pague (nesses casos o terreno virado deixa de ficar parado na mão até um turno em que atrasaria o desenvolvimento).

**Validação:** smoke (99 cartas, 0 desconhecidas, 0 duplicadas não-básicas, 200 partidas × 2 modos sem exceção); bit-identidade com as chaves desligadas × `kutzil_goldfish_v1_ANTES_98300d9.py`, 20.000 partidas × 2 modos (`resumos/bitident_20000.txt`); regressão 20.000 × 2 modos × 2 configurações, 0 exceções (`resumos/regressao_20000.txt`); testes dirigidos 8/8 (`resumos/testes_dirigidos.txt`); ghost (chave ligada + ensaio ignorado == desligada), 20.000 × 2 modos (`resumos/ghost_20000.txt`); reprodutibilidade por `cmp` (`resumos/verificacao_reproducao.txt`).

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

## Porte completo do modo de resiliência + CR 903.9a nativa desde o início — 2026-09-21

**Gatilho:** "Agora faz o Kutzil" — seguindo o porte concluído no
Nekusar, Azula, Beorn, Thranduil e Ms. Bumbleflower. Detalhes completos
em `checklist-oraculo.md`.

**Achado CRÍTICO (diferente de tudo achado antes nesta sessão):** o bug
de comandante presa não era latente/estrutural — **já acontecia em
partidas de modo PADRÃO**. `Damning Verdict` ("destroy all creatures
with no counters") podia matar a própria Kutzil (criatura recém-
conjurada com 0 contadores), e como `leave_battlefield` nunca tratava o
comandante, ela ficava "fantasma": `commander_in_play=True` mas ausente
do battlefield e presa no cemitério pra sempre. Confirmado: 6/10000
partidas nessa condição ANTES do fix, 0/10000 depois. Corrigido em
`should_cast_damning_verdict()` (nunca conjura enquanto isso mataria o
comandante — a carta em si não tem exceção no oráculo, então a proteção
é na decisão de CONJURAR, não no efeito).

**Achado adicional:** `commander_cast_count` (CR 903.8) já existia
declarado no GameState, mas nunca era incrementado nem lido —
`effective_cost()` corrigido pra somar a taxa real. Diferente do Azula/
Bumbleflower, este deck **não tinha** bug de RNG não-seedado (`mulligan`
já usava o RNG seedado corretamente).

**Resultado:** bit-identidade em modo padrão com 13/20000 (0,07%)
divergências — todas legítimas (confirmado via trace: o fix impede a
morte real da comandante que já acontecia antes). A/B agregado (10k
seeds): métricas principais idênticas dentro de margem de ruído.

**Validação:** regressão de 20.000 partidas em modo de resiliência, 0
exceções, 0 comandantes presos/fantasma, 52,76% das partidas com recast
pagando a taxa CR 903.8 + 23 testes dirigidos.

## Auditoria oráculo-por-oráculo completa — 2026-09-13

Extensão pra este deck da mesma auditoria já feita no Megatron/Azula/
Beorn/Captain Storm/Edgar Markov/Hei Bai. Detalhes carta-a-carta completos
em `checklist-oraculo.md` (seção no topo) — **11 gaps reais** encontrados
mesmo depois da rodada de construção original já ter corrigido 12 outros
via varredura de tags órfãs. Resumo dos achados: transferência de
contadores pro "The Ozolith" e movimentação do Broodguard Elite bypassavam
o motor central `place_counters()` (perdendo a própria estática do
"Ozolith, the Shattered Spire" e o gate creature-only de Hardened
Scales/Michelangelo); Wakka's "Blitzball Captain" só disparava via
combate, não via qualquer fonte de contador; Kodama ignorava Rancor como
"modified"; District Mascot e Ornery Tumblewagg tinham os próprios
gatilhos "attacks while saddled" 100% ausentes; Requisition Raid cobrava
1 mana a menos que o custo real (Spree); Broodguard Elite's Warp e
Restoration Seminar's Paradigm (recast grátis recorrente) estavam 100%
ausentes; Selvala nunca pagava o próprio `{G}` de ativação; 7 habilidades
ativadas nunca checavam a cor do pip no custo (só o total genérico); e
Rishkar tinha 2 bugs relacionados no modelo de mana (mana dele nunca
contava pro requisito de cor verde + double-counting de dorks que já têm
sua própria habilidade).

### Métricas antes/depois (2.000 partidas, seed 555.000, turns=8, mesma seed)

| Métrica | Antes | Depois |
|---|---|---|
| Turno médio de conjuração da Kutzil | 3,45 | 3,45 |
| Avg dano proxy total de combate | 95,43 | 100,97 |
| Avg compras via Kutzil (poder>base) | 3,90 | 3,87 |
| Avg contadores +1/+1 colocados (com multiplicadores) | 38,97 | 45,53 |
| Avg cartas compradas extra (todos os motores) | 12,17 | 12,16 |
| Avg spells de interação conjurados | 0,95 | 1,00 |
| Avg ativações de saddle | 0,84 | 0,84 |
| Avg Plot/Warp custo-alternativo | 0,00 | 0,06 |
| Avg eventos de recursão | 0,01 | 0,05 |
| Craterhoof Behemoth resolvido | 4,9% | 4,9% |
| Damning Verdict conjurada | 2,0% | 2,1% |
| Avg vida final | 39,76 | 39,75 |

**Leitura:** os contadores totais subiram ~17% (38,97→45,53) — driver
principal são os 2 gatilhos "attacks while saddled" (achados #5/#6, District
Mascot e Ornery Tumblewagg) somados ao roteamento do Ozolith/Broodguard
pelo motor central de multiplicadores (achado #1/#2), que agora captura
corretamente a própria estática do "Ozolith, the Shattered Spire" nessas
transferências. O dano proxy subiu ~5,8% na mesma direção (mais
contadores = criaturas maiores). Eventos de recursão saltaram 5x
(0,01→0,05) — baixo em termos absolutos porque tanto Restoration Seminar
(7 mana) quanto o ciclo completo de Warp do Broodguard exigem bastante
mana disponível num goldfish de 8 turnos, mas a direção é a esperada (as
2 cartas antes contribuíam quase nada, agora contribuem algo real). As
métricas de mana "corrigida pra baixo" (Selvala perdendo 1 mana líquida
por ativação, Requisition Raid custando 1 a mais, os 7 gates de cor)
puxam na direção oposta mas em volume pequeno frente ao ganho líquido dos
gatilhos de contador reais — resultado agregado positivo e plausível,
sem nenhuma métrica se movendo de forma inexplicável.

**Validação:** smoke test (99/99, 0 desconhecidas) + 2.000 partidas
antes/depois (tabela acima) + 20.000 partidas de regressão (2 rodadas,
seeds 9.000.000+ e 4.200.000+, turns=10): **0 exceções em ambas**. 20
testes unitários dirigidos (`kutzil_fix_tests.py`) confirmaram cada
correção isoladamente.

---

Compilação dos goldfishes rodados com o deck, exportada e organizada a partir dos logs do simulador. Segue convenção estrita de separar **fato registrado** de **interpretação**, e marca explicitamente onde os dados não são recuperáveis — nada foi inventado para preencher lacunas.

---

### Simulador Python construído do zero — `kutzil_goldfish_v1.py` — 2026-09-02

**Gatilho:** pedido direto do usuário ("Pode começar com o Kutzil") — um
dos 4 decks desta pasta sem simulador nenhum ainda. Os 10 goldfishes
manuais abaixo (pré-v8/v8, jogados pelo próprio usuário antes de
qualquer simulador existir) continuam registrados como estavam — este
simulador é uma ferramenta NOVA e independente, não uma reconstrução
dos jogos manuais.

**Construção:** oráculo real de todas as 92 cartas (91 não-básicas +
comandante) buscado ao vivo via Scryfall, arquitetura de objetos
`Permanent` (necessária pro motor central de +1/+1 counters — ver
`checklist-oraculo.md` pra detalhamento completo). Depois do primeiro
rascunho passar na regressão de 20.000 partidas (0 exceções), rodei a
mesma varredura automatizada de tags órfãs usada nas auditorias dos
outros 13 decks — achou **12 gaps reais** que o próprio rascunho tinha
deixado passar (The Great Henge sem redução de custo, Managorger Hydra,
Walking Ballista, Beast Whisperer, Goldvein Hydra, Puca's Covenant, Tale
of Katara and Toph, Abandoned Air Temple, Ba Sing Se, Lion Sash, Mosswort
Bridge, Hushwood Verge) — todos corrigidos antes de considerar o deck
pronto. Ver `checklist-oraculo.md` pra detalhamento carta-a-carta.

**Validação:** 29 testes unitários isolados (3 baterias, cobrindo o
motor de multiplicadores de contador, os 4 gatilhos reativos, o gatilho
de compra da própria Kutzil, a heurística do Damning Verdict, Rancor, e
os 12 gaps achados na varredura) + regressão de 20.000 partidas repetida
a cada rodada de correção (seeds 2000000+ a 6000000+, turns=10, 0
exceções em todas as rodadas).

**Métricas do build final** (3000 jogos, seed_base=1000000, turns=8):

| Métrica | Valor |
|---|---|
| Turno médio de conjuração da Kutzil | 3.47 (mediana 3) |
| Nunca conjurada em 8 turnos | 6.6% |
| Avg contadores +1/+1 colocados (com multiplicadores) | 38.29 |
| Avg compras extras (todos os motores) | 12.05 |
| Avg compras via Kutzil (poder>base em combate) | 3.81 |
| Avg dano proxy de combate | 96.45 |
| Craterhoof Behemoth resolvido | 5.4% dos jogos |
| Damning Verdict conjurada | 1.9% dos jogos |

Achado incidental durante os testes (não um bug — confirmado com
`time`, sem loop infinito nem travamento): em ~4/20000 sementes, a
Kutzil terminou com 500+ contadores via um combo real conhecido de papel
(Ouroboroid — "put X counters on each creature, X = seu próprio poder" —
realimentando a si mesmo turno após turno com 2+ multiplicadores
ativos). Crescimento exponencial genuíno da própria carta, não um erro
de implementação — deixado como está, consistente com o mandato de
"compilar tudo e deixar os dados revelarem o resultado real".

**Turno médio de conjuração (3.47) e explosividade dos contadores**
batem com o que a `auditoria.md` (seção 10, cruzamento com os
goldfishes manuais) já tinha confirmado: T2-T3 consistente e um motor
genuinamente explosivo quando os multiplicadores se alinham — agora com
uma amostra de 3000 partidas simuladas em vez de 5-6 goldfishes manuais.

---

## Convenções

- **KEEP** = mão mantida.
- **MULLIGAN** = mulligan explicitamente informado.
- **N/D** = dado não recuperável no histórico disponível; não foi inventado.
- Os counters mostrados são os registrados no simulador. Nos testes em que houve confusão de contagem, isso fica marcado.
- Um goldfish não simula remoções dos oponentes; quando havia decisão deliberada de manter proteção disponível (em vez de maximizar o goldfish), isso é registrado como decisão de pilotagem.

---

## Goldfish #1

**Versão:** anterior ao v8
**Mão inicial:** N/D no contexto atualmente recuperável.
**Keep/Mulligan:** N/D.
**Log turn-by-turn:** N/D.

Não reconstruído a partir de conclusões posteriores, para não criar informação que não existe no registro.

**Status:** `DADOS_INCOMPLETOS`

---

## Goldfish #2

**Versão:** anterior ao v8
**Mão inicial:** N/D | **Keep/Mulligan:** N/D | **Log:** N/D

**Status:** `DADOS_INCOMPLETOS`

---

## Goldfish #3

**Versão:** anterior ao v8
**Mão inicial:** N/D | **Keep/Mulligan:** N/D | **Log:** N/D

**Status:** `DADOS_INCOMPLETOS`

---

## Goldfish #4

**Versão:** anterior ao v8
**Mão inicial:** N/D | **Keep/Mulligan:** N/D | **Log:** N/D

**Status:** `DADOS_INCOMPLETOS`

---

## Goldfish #5

**Versão:** anterior ao v8
**Mão inicial:** N/D no contexto recuperável.

Informação preservada da discussão original: nesse teste, o piloto manteve criaturas desviradas e mana disponível para **Clever Concealment**, em vez de gastar todos os recursos para maximizar o goldfish.

**Comportamento de pilotagem observado:** proteção deliberadamente representada.

**Status:** `DADOS_PARCIAIS`

---

## Goldfish #6

**Versão:** pré-v8
**Decisão:** KEEP

**Mão inicial registrada** (8 cartas — o primeiro bloco do log registrou 8 antes da primeira jogada; preservadas literalmente em vez de cortar arbitrariamente pra 7):

1. Fight Rigging
2. Snow-Covered Forest
3. Sphere Grid
4. Brushland
5. Mother of Runes
6. Mikey & Leo, Chaos & Order
7. Temple Garden
8. Branchloft Pathway // Boulderloft Pathway

**T1:** Brushland → Mother of Runes.

**T2:** Draw: Duskshell Crawler. Snow-Covered Forest → Sphere Grid. Mother of Runes recebeu counter +1/+1.

**T3:** Draw: Path to Exile. Branchloft Pathway → Kutzil, Malamet Exemplar. Mother chegou a 2 counters no tracking. Draw adicional: The Great Henge.

**T4:** Draw: Ozolith, the Shattered Spire. Temple Garden → Fight Rigging. Hideaway do Fight Rigging: Esper Sentinel. Fight Rigging colocou counter em Kutzil. Kutzil atacou. Draw: Swords to Plowshares. Kutzil chegou a 3 counters no tracking.

**T5:** Há movimentos envolvendo Walking Ballista e Swords to Plowshares retornando à library — sem causa atribuída além do que está registrado.

**T6:** Draw: Botanical Brawler. Botanical Brawler entrou. Ozolith, the Shattered Spire entrou. Kutzil avançou de 4 para 5 counters no tracking. Esper Sentinel (no hideaway) foi liberado pelo Fight Rigging. Botanical Brawler cresceu e chegou a 4 counters registrados. Draw: Dauntless Escort.

**T7:** Draw: Avacyn's Pilgrim. Entraram: Mikey & Leo Chaos & Order, The Great Henge, Duskshell Crawler. Duskshell recebeu counters. Botanical Brawler aparece chegando a 5 counters e depois a 4 — **inconsistência de tracking**. Draw: Collector's Cage. Kutzil atacou.

**O que demonstrou:** montou simultaneamente Kutzil + Fight Rigging + Ozolith + Botanical Brawler + Great Henge, além de gerar Esper Sentinel de graça pelo hideaway. Piloto avisou explicitamente: *"Novamente eu me confundi com os counters, mas parece que o deck funcionou bem!"* — os valores exatos de counters não devem ser usados como dado estatístico confiável.

**Status:** `LOG_COMPLETO_COUNTERS_NAO_CONFIAVEIS`

---

## Goldfish #7

**Versão:** pré-v8
**Decisão:** KEEP

**Mão inicial registrada** (8 cartas, mesma ressalva do #6):

1. Avacyn's Pilgrim
2. Teferi's Protection
3. Snow-Covered Forest
4. Rancor
5. Branchloft Pathway // Boulderloft Pathway
6. Snow-Covered Forest
7. Wakka, Devoted Guardian
8. Sunpetal Grove

**T1:** Snow-Covered Forest → Avacyn's Pilgrim.

**T2:** Draw: Hardened Scales. Sunpetal Grove. Avacyn's Pilgrim acelerou Kutzil pro turno 2.

**T3:** Draw: Akroma's Will. Segundo Snow-Covered Forest. Entraram: Hardened Scales, Rancor. Kutzil atacou. Draw: Canopy Vista.

**T4:** Canopy Vista. Wakka, Devoted Guardian entrou. Kutzil atacou. Draw: Requisition Raid.

**T5:** Draw: Ozolith, the Shattered Spire. Branchloft Pathway. Ozolith entrou. Counters começaram a aparecer em Wakka, Avacyn's Pilgrim e Kutzil.

**T6:** Draw: Forest. Forest entrou. Tracking mostra crescimento acentuado: Wakka chegando a 9 counters, Kutzil a 5, Avacyn's Pilgrim a 6. **Teferi's Protection foi utilizada.** Draw: Gavony Township.

**T7:** Draw: Knight of Autumn. Gavony Township entrou. Knight of Autumn entrou. Tracking final: Wakka ~12 counters, Knight of Autumn ~7, Kutzil ~8, Avacyn's Pilgrim ~9. Draws posteriores: Snow-Covered Plains, Lion Sash. Swords to Plowshares também foi utilizado.

**O que demonstrou:** a sequência mais relevante foi T1 mana dork → T2 Kutzil → T3 Hardened Scales/Rancor → engine de counters, com a mão contendo proteção pesada (Teferi's Protection ficou disponível até ser efetivamente usada). Piloto novamente avisou erro na manipulação dos counters.

**Status:** `LOG_COMPLETO_COUNTERS_NAO_CONFIAVEIS`

---

## Goldfish #8

**Versão:** pré-v8
**Decisão:** KEEP

**Mão inicial** (8 cartas, mesma ressalva):

1. The Ozolith
2. Requisition Raid
3. Snow-Covered Plains
4. Gavony Township
5. Kabira Takedown // Kabira Plateau
6. The Great Henge
7. Exotic Orchard
8. Snow-Covered Forest

**T1:** Snow-Covered Plains → The Ozolith.

**T2:** Draw: Dyadrine, Synthesis Amalgam. Snow-Covered Forest.

**T3:** Draw: Path to Exile. Gavony Township → Kutzil.

**T4:** Draw: Witch Enchanter // Witch-Blessed Meadow. Exotic Orchard. Dyadrine entrou com 2 counters.

**T5:** Draw: Railway Brawler. Kabira Plateau usada como land. Railway Brawler foi plotted. Dyadrine atacou. Draw: The Earth Crystal.

**T6:** Draw: Akroma's Will. Railway Brawler entrou. Tracking mostra counters em Kutzil, Dyadrine, Railway Brawler. Dyadrine atacou. Draw: Hopeful Initiate.

**T7:** Draw: Branchloft Pathway. Branchloft entrou. The Great Henge entrou. Hopeful Initiate entrou e recebeu counters. Draw: Hardened Scales.

**T8:** Draw: Maester Seymour. Hardened Scales entrou. Maester Seymour entrou. Mesa passou a produzir grande quantidade de counters envolvendo Railway Brawler, Hopeful Initiate e demais permanentes. Draw: Eiganjo, Seat of the Empire.

**T9:** Draw: Horizon Canopy. The Earth Crystal entrou.

**Conclusão registrada do piloto (avaliação imediata, não reconstruída):**
*"Esse acho que foi o mais explosivo de todos, com a entrada do Earth Crystal os counters explodem!!!"*

**Status:** `LOG_COMPLETO`
**Tag:** `MAIOR_EXPLOSIVIDADE_PERCEBIDA_ATE_ENTAO`
**Peça-chave identificada pelo piloto:** `THE_EARTH_CRYSTAL`

---

## Goldfish #9

**Versão:** pré-v8

A imagem da mão foi enviada e o piloto informou explicitamente: **KEEP com apenas 2 lands, deliberadamente para fins de teste.**

A composição completa da mão e o log #9 não aparecem mais textualmente no contexto recuperável — não preenchido com base em lembrança/conclusão posterior.

**Condição experimental confirmada:** `KEEP_2_LANDS = TRUE`

**Status:** `DADOS_PARCIAIS`

---

## Goldfish — primeiro teste explicitamente do Kutzil v8

Teste feito depois de salvar a lista como "Kutzil v8".

**Decisão:** KEEP

**Mão inicial** (8 cartas, mesma ressalva):

1. Avacyn's Pilgrim
2. Metastatic Evangel
3. Brushland
4. Gavony Township
5. Rancor
6. Knight of Autumn
7. Ozolith, the Shattered Spire
8. Swiftfoot Boots

**T1:** Brushland → Avacyn's Pilgrim.

**T2:** Draw: Urdnan, Dromoka Warrior. Gavony Township. Kutzil no T2, de novo graças ao Pilgrim.

**T3:** Draw: Damning Verdict. Rancor entrou em Kutzil. Kutzil atacou. Draw: Ornery Tumblewagg. Metastatic Evangel entrou.

**T4:** Draw: Innkeeper's Talent. Innkeeper's Talent entrou. Kutzil recebeu counter. Kutzil atacou. Draw: Kodama of the West Tree.

**T5:** Draw: Fight Rigging. Kodama of the West Tree entrou. Kutzil recebeu outro counter. Draw: Maester Seymour. Kodama colocou Snow-Covered Forest no campo.

**T6:** Draw: Forest. Forest entrou. Ornery Tumblewagg entrou. Fight Rigging entrou. Carta exilada pelo hideaway: Michelangelo, Weirdness to 11. Kodama recebeu counter. Metastatic Evangel recebeu counter. Ornery recebeu counter.

Fato confirmado pelo piloto posteriormente: Michelangelo estava exilado pelo Fight Rigging e foi conjurado **de graça** porque Kutzil estava com poder 7. Michelangelo entrou e produziu um Mutagen token.

**T7:** Draw: Command Tower. Command Tower entrou. Ozolith entrou. Maester Seymour entrou. Tracking passa a registrar counters em Michelangelo, Maester Seymour, Metastatic Evangel, Ornery Tumblewagg. Ornery termina a sequência com **22 counters +1/+1** registrados. Draw: Clever Concealment. Kodama colocou terrenos adicionais no campo, incluindo Ba Sing Se e Plains.

**Estado seguinte:** Draw: Selvala, Heart of the Wilds.

**O que demonstrou:** sequência T1 Pilgrim → T2 Kutzil → Rancor → Innkeeper's Talent → Kodama → Fight Rigging → Michelangelo grátis → Ozolith → Maester. Damning Verdict e Clever Concealment apareceram na mão como proteção/resposta disponível. Kodama acelerou terrenos. Fight Rigging converteu Kutzil grande em spell gratuito. Ornery Tumblewagg virou uma ameaça enorme.

**Status:** `LOG_COMPLETO`

---

## Goldfish #10 — v8 (teste proposital de mão problemática)

**Primeira mão:** enviada, decisão de **MULLIGAN GRATUITO**. Composição não aparece textualmente no log posterior — não inventada.

**Segunda mão — KEEP.** Piloto informou explicitamente: *"Mantive as 7 mesmo sem fonte de mana verde para testar!"*

**Mão recuperada pelo início do log** (8 cartas registradas no bloco inicial, embora a observação textual do piloto dissesse "7" — discrepância registrada, não corrigida arbitrariamente):

1. Snow-Covered Plains
2. Duskshell Crawler
3. War Room
4. Aetheric Amplifier
5. Path to Exile
6. Hopeful Initiate
7. Plains
8. Knight of Autumn

**Fontes verdes iniciais: 0** — teste específico de color screw.

**T1:** Snow-Covered Plains. Hopeful Initiate entrou.

**T2 (draw decisivo):** Draw: Snow-Covered Forest — problema de cor corrigido no primeiro draw após o keep. Snow-Covered Forest entrou. Duskshell Crawler entrou e recebeu counter. Hopeful Initiate atacou.

**T3:** Draw: Terrasymbiosis. Plains entrou. Kutzil entrou. Duskshell atacou. Draw: Railway Brawler.

**T4:** Draw: Forest. Forest entrou. Railway Brawler foi plotted.

**T5:** Draw: Tale of Katara and Toph. War Room entrou. Tale of Katara and Toph entrou. Ataques: Kutzil, Duskshell Crawler, Hopeful Initiate. Counters: Hopeful → 2, Duskshell → 2, Kutzil → 1. Draws: Beast Whisperer, Kodama of the West Tree. Path to Exile foi utilizado.

**T6:** Draw: Branchloft Pathway. Branchloft entrou. Terrasymbiosis entrou. Railway Brawler estava no campo. Kodama of the West Tree entrou e recebeu 2 counters no tracking. Ataques: Kutzil, Duskshell, Hopeful. Counters posteriores: Hopeful 3, Duskshell 3, Kutzil 3. Draws: Gavony Township, Fyndhorn Elves, Selvala Heart of the Wilds. Kodama/efeitos colocaram terrenos adicionais: Snow-Covered Plains, Forest.

**T7 / estado final recuperável:** Draw: Requisition Raid. Board registrado: Kutzil (3 counters), Duskshell Crawler (3), Hopeful Initiate (3), Kodama of the West Tree, Railway Brawler, Terrasymbiosis, War Room, Branchloft Pathway, Forest, Snow-Covered Forest, Plains, Snow-Covered Plains.

**Resultado do experimento:** não deve ser interpretado como "uma mão sem verde é segura". O que ele efetivamente mostrou foi: mão sem verde → Forest imediatamente no draw do T2 → curva recuperada. Ou seja, foi um caso de recuperação bem-sucedida do color screw, não evidência de que esse tipo de keep seja correto em geral.

**Status:** `LOG_COMPLETO`
**Tag:** `COLOR_SCREW_TEST`

---

## Resumo consolidado dos testes recuperáveis

| Goldfish | Versão | Mão | Mulligan | Kutzil no jogo | Destaque |
|---|---|---|---|---|---|
| #1 | pré-v8 | N/D | N/D | N/D | dados não recuperáveis |
| #2 | pré-v8 | N/D | N/D | N/D | dados não recuperáveis |
| #3 | pré-v8 | N/D | N/D | N/D | dados não recuperáveis |
| #4 | pré-v8 | N/D | N/D | N/D | dados não recuperáveis |
| #5 | pré-v8 | N/D | N/D | N/D | proteção deliberadamente representada (Clever Concealment) |
| #6 | pré-v8 | 8 cartas registradas | KEEP | T3 | Kutzil + Fight Rigging + Ozolith + Botanical Brawler + Henge; Esper Sentinel de graça; counters não confiáveis |
| #7 | pré-v8 | 8 cartas registradas | KEEP | T2 | dork T1 → Kutzil T2; Teferi's Protection guardada e usada no T6; counters não confiáveis |
| #8 | pré-v8 | 8 cartas registradas | KEEP | T3 | Earth Crystal identificado pelo piloto como pico de explosividade até então |
| #9 | pré-v8 | N/D (KEEP 2 lands confirmado) | KEEP proposital | N/D | teste deliberado de mão com só 2 terrenos |
| v8 teste 1 | v8 | 8 cartas registradas | KEEP | T2 | Fight Rigging solta Michelangelo de graça (Kutzil poder 7); Ornery Tumblewagg fecha com 22 counters |
| #10 | v8 | 8 cartas registradas (mulligan gratuito antes) | KEEP (0 fontes verdes) | T3 | color screw test — corrigido no draw do T2, não evidência de que o keep seja correto em geral |

> **Nota de integridade:** este resumo foi compilado a partir de um export externo (ChatGPT) que o piloto colou aqui. A tabela final enviada foi cortada antes de listar os testes #5 em diante — reconstruí as linhas correspondentes a partir do corpo do próprio documento (que continha os detalhes completos de #6 a #10 e do teste v8), mas se a tabela original continha alguma coluna ou observação adicional que não apareceu no corpo do texto, ela não está representada aqui.
>
> **Nota sobre cartas cortadas:** Fight Rigging (Goldfish #6 e teste v8) e Aetheric Amplifier (Goldfish #10) aparecem nesses logs mas **não estão na lista atual registrada em `lista.md`**. Confirmado pelo piloto: foram cortadas numa atualização posterior do deck — a lista salva aqui É a versão atual. Ou seja, as linhas de jogo que dependiam de Fight Rigging (soltar Esper Sentinel/Michelangelo de graça via hideaway) não são mais reproduzíveis com a lista de hoje; leia esses trechos dos Goldfish #6 e do teste v8 como histórico de uma versão anterior do deck, não como algo a esperar em testes futuros.

---

<!-- Para novas partidas avulsas, use o formato abaixo -->

## Partida #N — AAAA-MM-DD

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
