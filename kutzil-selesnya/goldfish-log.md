# Goldfish Compilado — Kutzil, Malamet Exemplar

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
