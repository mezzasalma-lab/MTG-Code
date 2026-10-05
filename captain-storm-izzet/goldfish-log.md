# Goldfish Log — Captain Storm, Cosmium Raider

> **Rodada 2026-10-05 (Terreno virado primeiro em T1/T2 + Izzet Boilerworks entra virado (varredura de 2026-10-05)) — dados brutos e reprodução:** [`resultados-ab/2026-10-05-terreno-virado-primeiro/LEIAME.md`](resultados-ab/2026-10-05-terreno-virado-primeiro/LEIAME.md)

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

## Terreno virado primeiro em T1/T2 + Izzet Boilerworks entra virado (varredura de 2026-10-05) — 2026-10-05

**Pedido do usuário:** *"Com base nos erros encontrados nas ultimas revisões, reanálise todos os outros decks em busca de erros semelhantes, e os corrija"*. Arquivo bruto/auditável: `resultados-ab/2026-10-05-terreno-virado-primeiro/` (`LEIAME.md`).

**Veredito:** um erro real, um conserto, bit-idêntico com a chave desligada e com o ensaio sem efeito colateral (modo GHOST). Modo padrão, N=10.000: comandante em campo até T3 80,9% → 83,2% (+2,33 ± 0,47 pp), até T4 +0,46 ± 0,25 pp, até T5 -0,04 ± 0,16 pp, comandante que nunca entra +0,03 ± 0,04 pp. Modo resiliência: comandante em campo até T3 78,8% → 80,6% (+1,76 ± 0,50 pp), até T4 +0,86 ± 0,33 pp, até T5 +0,11 ± 0,20 pp, comandante que nunca entra +0,03 ± 0,08 pp. A correção joga o terreno virado primeiro em média 0,30 vez(es) por partida (N=10.000, padrão) e o ensaio impede 0,19 vez(es) por partida (teria custado uma jogada).

**Achado (varredura das classes de erro do Vihaan/Megatron neste simulador):**
- **Terreno que entra virado nunca é jogado primeiro.** `play_land` jogava sempre o primeiro terreno da ordem própria do deck (desvirado antes de virado). Em T1/T2, sem nada pra conjurar, a mana do turno era desperdiçada enquanto o terreno que entra virado ficava na mão pra um turno em que ele custa desenvolvimento. Mesmo erro achado e corrigido no Vihaan e no Megatron (2026-10-03/04).
- **Izzet Boilerworks entrava DESVIRADO.** Oráculo: "This land enters tapped. When this land enters, return a land you control to its owner's hand." O `CARD_DB` só tinha a tag `bounceland_ur`, que `enters_tapped` nunca lia: o terreno produzia mana no próprio turno (mana fantasma). E sem outro terreno em campo o oráculo manda devolver ELE MESMO; o código antigo não devolvia nada. (Achado pela varredura mecânica de entrada de terrenos, `varredura-2026-10-05/resumos/audit_entrada_ANTES.txt`.)

**O que mudou:**
- `TAPPED_LAND_FIRST_ENABLED` (padrão `True`), `TAPPED_LAND_FIRST_MAX_TURN = 2`: em T1..T2, havendo terreno virado E desvirado na mão, `tapped_first_pick` joga o virado, **salvo se isso custar desenvolvimento**: o teste é um ENSAIO a seco da própria fase de conjuração pré-combate do deck (cópia profunda do estado; `CARD_DB` compartilhado; RNG do estado copiado; `random` global restaurado), comparando o MV total das cartas que saem da mão com cada candidato. Empate → o virado. Dentro de cada grupo vale a ordem própria do deck (cor mais escassa etc.). Contadores novos no estado: `tapped_land_first_plays_total` (jogou o virado) e `tapped_land_skipped_for_play_total` (o ensaio mostrou que custaria uma jogada e jogou o desvirado). `TAPPED_LAND_FIRST_GHOST` só existe pra validação (roda o ensaio e ignora o resultado). Com a chave em `False` o caminho antigo volta bit a bit.
- `BOUNCELAND_ENTRY_ENABLED` (padrão `True`): `enters_tapped` passa a incluir a tag `bounceland_ur`; em `resolve_etb`, sem outro terreno em campo o bounceland devolve a si mesmo; `play_land` só marca `tapped_land_this_turn` se o terreno ainda está em campo. O `tapped_first_pick` não considera bounceland sem outro terreno em campo (jogá-lo devolveria ele mesmo = jogada perdida).

**Medido (pareado, mesmas sementes; IC95% = 1,96·dp/√N da diferença):**

Modo padrão, N=10.000 (`resumos/ab_10000.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 6432 (64.3%)
   campo                                          base     variante dif. pareada (IC95%)
   commander_cast_turn__nunca                   0.0058       0.0061      +0.0003 ±0.0004  
  *commander_cast_turn__ate_T3                  0.8088       0.8321      +0.0233 ±0.0047  
  *commander_cast_turn__ate_T4                  0.9185       0.9231      +0.0046 ±0.0025  
   commander_cast_turn__ate_T5                  0.9525       0.9521      -0.0004 ±0.0016  
  *tapped_land_this_turn                        1.0509       1.3598      +0.3089 ±0.0805  
  *next_uid                                    35.1443      34.9259      -0.2184 ±0.0920  
  *treasures_created_total                      5.4447       5.3886      -0.0561 ±0.0252  
  *len_battlefield                             26.1902      26.0380      -0.1522 ±0.0766  
  *interaction_plays                            1.5222       1.5099      -0.0123 ±0.0064  
  *counters_placed_total                       27.9275      27.5863      -0.3412 ±0.2200  
  *cards_drawn_extra                           20.6325      20.5058      -0.1267 ±0.0820  
  *equip_activations_total                      3.6090       3.5817      -0.0273 ±0.0184  
  *len_library                                 71.1470      71.2582      +0.1112 ±0.0817  
  *proxy_damage_total                         205.1673     202.8367      -2.3306 ±1.7654  
  *jhoira_ingenuity                             1.6850       1.6712      -0.0138 ±0.0105  
  *commander_cast_turn__ate_T6                  0.9697       0.9687      -0.0010 ±0.0010  
   len_graveyard                                7.1981       7.1408      -0.0573 ±0.0580  
   commander_damage_win                         0.9320       0.9342      +0.0022 ±0.0022
```
Modo resiliência, N=10.000 (`resumos/ab_10000_resiliencia.txt`):
```
[depois - antes] N=10000 | partidas com resultado IDENTICO ao da base: 6497 (65.0%)
   campo                                          base     variante dif. pareada (IC95%)
   commander_cast_turn__nunca                   0.0089       0.0092      +0.0003 ±0.0008  
  *commander_cast_turn__ate_T3                  0.7885       0.8061      +0.0176 ±0.0050  
  *commander_cast_turn__ate_T4                  0.8954       0.9040      +0.0086 ±0.0033  
   commander_cast_turn__ate_T5                  0.9400       0.9411      +0.0011 ±0.0020  
  *tapped_land_this_turn                        0.7755       1.0374      +0.2619 ±0.0629  
  *proxy_damage_total                          87.1578      86.1500      -1.0078 ±0.6988  
  *len_smart_graveyard_snipe_log                0.4284       0.4190      -0.0094 ±0.0071  
  *smart_graveyard_snipes_total                 0.4284       0.4190      -0.0094 ±0.0071  
  *commander_damage_dealt                      60.0502      59.4314      -0.6188 ±0.5774  
  *commander_in_play                            0.7769       0.7717      -0.0052 ±0.0052  
   equip_activations_total                      2.6056       2.5832      -0.0224 ±0.0227  
   commander_uid                               10.5685      10.4647      -0.1038 ±0.1136  
   len_smart_enchantment_wipe_log               0.0963       0.0937      -0.0026 ±0.0030  
   smart_enchantment_wipes_total                0.0963       0.0937      -0.0026 ±0.0030  
   interaction_plays                            1.1169       1.1114      -0.0055 ±0.0073  
   wiped_this_round                             0.1387       0.1419      +0.0032 ±0.0044  
   next_uid                                    25.3985      25.3471      -0.0514 ±0.0728  
   jhoira_ingenuity                             0.9998       0.9890      -0.0108 ±0.0159
```
Os lotes de N=2.000 (`ab_2000*.txt`) e as variantes de sensibilidade (uma correção por vez) estão em `resumos/`.

**Raciocinado (não medido):** o ganho esperado é pequeno e concentrado em T1–T3: só muda a partida quando a mão tem terreno virado E desvirado e nenhuma jogada de T1/T2 que o terreno desvirado pague (nesses casos o terreno virado deixa de ficar parado na mão até um turno em que atrasaria o desenvolvimento).

**Validação:** smoke (99 cartas, 0 desconhecidas, 0 duplicadas não-básicas, 200 partidas × 2 modos sem exceção); bit-identidade com as chaves desligadas × `captainstorm_goldfish_v1_ANTES_d9a170f.py`, 20.000 partidas × 2 modos (`resumos/bitident_20000.txt`); regressão 20.000 × 2 modos × 2 configurações, 0 exceções (`resumos/regressao_20000.txt`); testes dirigidos 8/8 (`resumos/testes_dirigidos.txt`); ghost (chave ligada + ensaio ignorado == desligada), 20.000 × 2 modos (`resumos/ghost_20000.txt`); reprodutibilidade por `cmp` (`resumos/verificacao_reproducao.txt`).

**Escopo — verificado:**
- **Terreno virado primeiro:** leitura de `play_land` (+ predicado de entrada virada do deck); testes dirigidos TL1–TL8 (escolha com/sem jogada em T1, chave desligada, T3, só um tipo na mão, ensaio sem efeito no estado/RNG/`random`, modo GHOST, integração em `play_land`); A/B pareado 2.000 e 10.000 nos dois modos.
- **Ensaio sem efeito colateral:** com a chave ligada + modo GHOST (roda o ensaio e ignora o resultado) o resultado é idêntico a tudo desligado, 20.000 × 2 modos (`resumos/ghost_20000.txt`).
- **Bit-identidade** com as chaves desligadas × snapshot: 20.000 partidas × 2 modos, impressão digital do resultado inteiro.
- **Regressão** 20.000 × 2 modos × 2 configurações: 0 exceções.
- **Bounceland:** testes dirigidos TL9–TL11 (entra virado e devolve o outro terreno; devolve a si mesmo sem outro terreno e não deixa mana negativa; chave desligada = antigo).

**Escopo — NÃO verificado:**
- **Condições de entrada dos terrenos** além do que a varredura mecânica cobriu (`varredura-2026-10-05/`: cenário de campo vazio + cenário condição satisfeita × violada para os padrões "unless you control …"/reveal; terrenos que o `CARD_DB` do deck não tem como básico foram pulados e estão listados lá).
- **Resto da taxonomia da Regra #1 neste arquivo** (caminhos de conjuração fora da mão e "whenever you cast", sacrifício × destroy, cascade, contadores `_sick` agregados, fórmulas dinâmicas achatadas): varrido na triagem de 2026-10-05 por `grep` e leitura pontual das funções, **sem** leitura integral do arquivo e **sem** instrumentação em runtime nesta rodada. "Sem achado" aí significa "o `grep` não achou", não "não existe".
- **Oponente real:** o goldfish não modela (convenção do repositório); nada aqui mede interação além do proxy já existente.

**Observação:** 0 exceções em 20.000 × 2 modos × 2 configurações; os invariantes genéricos (carta acima do número no baralho; contadores negativos) deram 0 violações.

---

## Porte completo do modo de resiliência + CR 903.9a nativa desde o início — 2026-09-21

**Gatilho:** "Então implemente ele tb" — último dos 18 decks com
simulador desta sessão a receber o porte. Detalhes completos em
`checklist-oraculo.md`.

**Achado CRÍTICO (o mais impactante numericamente desta sessão):**
`Ghostly Flicker`/`Planar Incision` (blinks legítimos, não CR 903.9a)
recriam o Permanent da comandante com um `uid` NOVO, mas `state.
commander_uid` nunca era atualizado — depois de um blink na própria
Captain Storm, TODO o dano de combate dela parava de ser contado
silenciosamente (CR 903.10a quebrado sem erro nenhum). Confirmado:
409/10000 partidas nessa condição antes do fix, 0/10000 depois. A
win-condition primária do deck (auto-win via 21+ dano da comandante)
estava sendo subestimada: **81,70% → 84,17%** depois do fix — a maior
correção numérica de qualquer deck desta sessão.

**Achado adicional:** `commander_cast_count` (CR 903.8) já existia
declarado e incrementado, mas nunca somado ao custo em `effective_
cost()`. Mesma classe de bug de RNG não-seedado do Azula/Bumbleflower no
`mulligan()` (723/3000 = 24,1% de partidas não-determinísticas antes do
fix, 0/3000 depois).

**Resultado:** bit-identidade em modo padrão com 816/20000 (4,08%)
divergências — a maior desta sessão, mas 100% legítima e rastreada
(confirmado via trace direto: o fix corrige o rastreio de dano da
comandante que já estava quebrado). A/B agregado (10k seeds): todas as
outras métricas idênticas dentro de ruído.

**Validação:** regressão de 20.000 partidas em modo de resiliência, 0
exceções, 0 comandantes presos/uid obsoleto, 46,11% das partidas com
recast pagando a taxa CR 903.8 + 25 testes dirigidos.

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

## 2026-09-02 — Simulador goldfish construído do zero (`captainstorm_goldfish_v1.py`)

Terceiro dos 4 decks sem simulador desta sessão a ser fechado (depois de
Kutzil e Azula). Detalhamento completo carta-a-carta em
`checklist-oraculo.md`.

**Metodologia:** oráculo real via Scryfall (line-by-line, "compile
TUDO"), implementação com objetos `Permanent` (contadores +1/+1
persistentes + Equipment anexado), testes unitários (10 no total, 2
arquivos), 1 rodada de correção após varredura automatizada de tags
órfãs (4 gaps reais confirmados), regressão de 20.000 partidas (0
exceções, ~154s).

**⚠️ Nota herdada da auditoria:** a lista enviada pelo usuário tem 98
cartas de biblioteca (99 com o comandante), falta 1 carta pro total
padrão de 100 — não corrigido/inventado aqui, `BASE_LIBRARY` reflete a
lista real.

**Motor real deste deck:** Captain Storm ("+1/+1 num Pirata quando um
artefato entra") combinado com um pacote denso de geração de
Treasure/Clue/Food, Academy Manufactor (triplica cada criação) e
Panharmonicon+Starfield Vocalist (dobram multiplicativamente qualquer
gatilho de ETB) — três camadas que se retroalimentam.

### Achado estatístico (Bloodforged Battle-Axe)

Confirmado num teste de estresse (seed fixa, turns=10): quando várias
cópias de Bloodforged Battle-Axe acabam equipadas na mesma criatura que
conecta sem bloqueio todo turno, cada cópia dispara SEPARADAMENTE
("whenever equipped creature deals combat damage, create a token copy
of this Equipment") — N cópias = N gatilhos = N novas cópias por
combate, dobrando a cada turno que conecta. Resultado observado: **1.296
cópias de Bloodforged Battle-Axe** em campo até o turno 10, simulação
rodando em 0.39s (determinístico, sem travamento). Esta é uma interação
real e conhecida de Magic de papel (não um bug de implementação) —
documentada, não suprimida, mesmo tratamento dado aos outliers do
Ouroboroid (Kutzil) e do combo Zada+Veyran+Storm-Kiln Artist (Azula)
nesta sessão.

### Métricas (20.000 partidas, seed 5.000.000+, turns=10, 0 exceções)

| Métrica | Média | Mediana |
|---|---|---|
| Dano proxy total | 325.9 | 163.0 |
| Cartas compradas extra | 21.4 | — |
| Treasures criados | 5.4 | — |
| Clues criados | 2.7 | — |
| Food criado | 1.1 | — |
| Contadores colocados pela Captain Storm | 62.8 | — |
| Gatilhos extra via dobradores de ETB | 16.3 | — |
| Equip/attach ativados | 15.6 | — |
| Biblioteca esgotada | 999/20000 (5.0%) | — |

A diferença entre média (325.9) e mediana (163.0) segue o mesmo padrão
documentado no Azula: um motor genuinamente explosivo e raro (Academy
Manufactor + os 2 dobradores de ETB + Bloodforged Battle-Axe
simultâneos) puxa a média pra cima em poucas partidas muito boas, sem
mudar o "jogo típico" (mediana).

---

## Auditoria oráculo-por-oráculo completa — 2026-09-13

Achado principal (detalhes completos em `checklist-oraculo.md`, seção no
topo): `try_equip()` nunca cobrava NENHUM custo de Equip em nenhuma das
11 peças de Equipment — todas anexavam de graça sempre, quando o
oráculo real só concede isso de graça (ETB) pras 2 com essa cláusula
explícita (Twin Blades, Embercleave); as outras 9 exigem pagar o Equip
normal. Mais 6 gaps: Two-Handed Axe nunca dobrava poder de combate (bug
de nome — comparava contra "Two-Handed Axe" mas o card real se chama
"Two-Handed Axe // Sweeping Cleave"); Enterprising Scallywag só
detectava "descended" pelo descarte de limite de mão, ignorando
sacrifícios reais; Izzet Locket/Lotus Petal/Trickster's Talisman
sacrificavam sem passar pelo cemitério nem disparar Geardrake/
Soulcleaver; Oaken Siren (único mana-dork de criatura da lista) nunca
contribuía mana nenhuma; Auras podiam ser conjuradas sem criatura em
campo pra enfeitiçar.

### Métricas antes/depois (20.000 partidas, seed 5.000.000, turns=10, 0 exceções)

| Métrica | Antes | Depois |
|---|---|---|
| Dano proxy médio | 325.9 | 201.3 |
| Dano proxy mediano | 163.0 | 158.0 |
| Cartas compradas extra (média) | 21.4 | 20.7 |
| Treasures criados (média) | 5.4 | 5.3 |
| Contadores colocados pela Captain Storm (média) | 62.8 | 28.2 |
| Gatilhos extra via dobradores de ETB (média) | 16.3 | 6.7 |
| Equip/attach ativados (média) | 15.6 | 3.6 |
| Biblioteca esgotada | 999/20000 (5.0%) | 681/20000 (3.4%) |

A queda grande em "Equip/attach ativados" (15.6→3.6) e nos "Contadores
da Captain Storm" (62.8→28.2) é exatamente o efeito esperado de corrigir
o bug do Equip de graça: antes, toda peça de Equipment conjurada também
"ativava" instantaneamente sem custo, inflando a contagem de ativações
e, indiretamente, o ritmo geral do motor (mais mana livre = mais
artefatos conjurados = mais contadores da Captain Storm). A mediana caiu
pouco (163→158, ~3%) porque o "jogo típico" não dependia tanto do
Equipment quanto a cauda explosiva dependia — a média caiu bem mais
(325.9→201.3) porque a correção do Equip atinge justamente os jogos em
que múltiplas peças caras (Embercleave, Sword of Once and Future,
Dragonfire Blade) estavam sendo empilhadas de graça.

