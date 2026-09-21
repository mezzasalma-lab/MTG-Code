# Checklist cláusula-a-cláusula — Hei Bai, Forest Guardian

## CR 903.9a: comandante passa pelo cemitério de verdade antes da zona de comando — 2026-09-21

**Gatilho:** mesmo achado do usuário aplicado a todos os 9 decks desta
sessão, depois de eu documentar em TODOS eles que "o comandante nunca
dispara gatilho de morte": *"O comandante não morre e ao invés de ir
pro cemitério, pode ser movido de volta a zona de comando? Pq até onde
sei, comandantes podem ser mortos sim! Confere essa regra com muita
calma e atenção!"* Raciocínio completo da regra em
`megatron-tyrant-mardu/checklist-oraculo.md` (CR 903.9a é ação baseada
em estado — CR 704 — não substituição; texto oficial cacheado em
`rules-cache/comprehensive-rules.txt`, Regra 18 de
`references/user-standing-rules.md`).

**Achado específico deste deck:** `remove_permanent()` desviava o
comandante direto pra zona de comando, pulando o cemitério
inteiramente. Este deck tem **0 cartas com gatilho "whenever ~
dies"/"creature put into graveyard" compartilhado** (grep confirmado) —
a única carta com "when ~ dies" é o próprio Enduring Vitality, e ela
reage a SI MESMA morrendo (excecão dinâmica real do oráculo, "return it
to the battlefield... as an enchantment"), nunca ao comandante. Cuidado
extra na correção: a ordem dos `if` em `remove_permanent()` importa —
o check do comandante teve que ficar ANTES do check do Enduring
Vitality (já estava assim, preservado), senão um nome igual por
coincidência quebraria a lógica; confirmado com teste dirigido que a
exceção do Enduring Vitality continua 100% intacta depois do fix.

**Corrigido mesmo assim** por consistência estrutural (Regra #1 do
`CLAUDE.md`): o comandante agora entra no cemitério de verdade via
`put_into_graveyard()`, e só DEPOIS é removido de lá pra representar a
escolha do dono de movê-lo pra zona de comando.

**Validação:** compilação OK. Bit-identidade em modo padrão
(`simulate_one`, 3000 seeds, seed_base 9100000) contra o commit
anterior: **0/3000 mismatches** (ambos os call sites de
`remove_permanent` — `try_smart_opponent_wipe`/`try_smart_opponent_
removal` — só disparam com `interaction_rng` ativo). Regressão de
20.000 partidas em modo de resiliência (seed_base 9500000): 0
exceções, 0/20000 partidas com o comandante preso no cemitério. 3
testes dirigidos: (1) comandante removido → `commander_in_play=False`,
fora do campo, não preso no cemitério; (2) permanente comum vai pro
cemitério e fica lá; (3) Enduring Vitality ainda volta corretamente
pro campo como enchantment puro na 1ª morte (excecão intacta, não
afetada pelo fix do comandante).

**Resultado:** correção estrutural sem impacto numérico observável
nesta lista atual (0 cartas reagem à morte do comandante), mas fecha o
gap de consistência com CR 903.9a.

## Modo de resiliência ganha wipe de artefato e wipe de encantamento — 2026-09-20

**Gatilho:** "Temos que incluir remoções de artefatos e encantamentos
tb: Vandalblast, Farewell, Austere Command, etc…" Raciocínio completo
em `megatron-tyrant-mardu/checklist-oraculo.md`.

**Achado real específico deste deck:** o Enduring Vitality tem uma
exceção dinâmica real (`state.enduring_vitality_enchantment_only`) que
já fazia `try_smart_opponent_wipe` tratá-lo como NÃO-criatura quando
voltou só como encantamento. Extraído `is_creature_now(state, name)`
(mesma exceção, reusável) pra que `wiped_this_round` continue correto
quando um wipe de encantamento o destrói nesse estado — ele é
encantamento de verdade (`is_enchantment_card` já inclui
"enchantment_creature"), mas não conta como perda de poder de ataque
se já não era criatura no momento.

**Implementado (1ª versão, SUPERSEDIDA no mesmo dia):** inicialmente 2
funções novas com rolagens INDEPENDENTES (`ARTIFACT_WIPE_CHANCE_FACTOR
= 0.2`, `ENCHANTMENT_WIPE_CHANCE_FACTOR = 0.15`) somadas ao wipe de
criatura já existente.

### Correção de design: unificado num único roll + escolha ponderada — 2026-09-20

**Gatilho:** mesma correção do usuário aplicada primeiro no Megatron —
*"Obviamente tem que ter uma alternância de remoções, aleatória, até pq
wipes de criaturas são muito mais comuns que remoção de artefatos e
encantamentos"*. Raciocínio completo em
`megatron-tyrant-mardu/checklist-oraculo.md`.

**Implementado (final):** `try_smart_opponent_wipe()` único — 1 rolagem
"algum wipe acontece" (`chance = interaction_chance() *
TOTAL_WIPE_CHANCE_FACTOR`, soma dos 3 pesos = 0.75) seguida de escolha
ponderada de 1 TIPO só (`WIPE_TYPE_WEIGHTS = {"creature": 0.4,
"artifact": 0.2, "enchantment": 0.15}`), restrita aos tipos com alvo
legal em campo. Este deck roda vários encantamentos reais, incluindo
enchantment creatures, então a categoria de encantamento é
particularmente relevante aqui. Hei Bai nunca é artefato nem
encantamento (Legendary Creature — Bear Spirit, confirmado via
Scryfall).

`is_creature_now(state, name)` (exceção dinâmica real do Enduring
Vitality — `state.enduring_vitality_enchantment_only`) preservada
dentro da função unificada, tanto pros candidatos de criatura quanto
pro cálculo de `wiped_this_round` quando um wipe de outro tipo também
derruba uma enchantment creature de verdade (`is_enchantment_card` já
inclui "enchantment_creature").

**Validação:** modo padrão 100% bit-idêntico ao commit `8b84daf` (2.000
seeds) + regressão de 20.000 partidas em modo resiliência, 0 exceções +
testes dirigidos (no máximo 1 tipo por chamada; distribuição ponderada
correta; `is_creature_now` continua respeitando a exceção do Enduring
Vitality dentro da função unificada).

**Resultado (A/B 2000 jogos mesma seed_base, design unificado final):**
% de jogos com pelo menos 1 wipe de qualquer tipo sobe de 53,8% pra
75,2% (antes = commit `8b84daf`, só wipe de criatura). Avg wipes totais
por jogo: 0,687 → 1,238. 13,1% dos jogos "depois" sofrem pelo menos 1
artifact wipe, 29,5% pelo menos 1 enchantment wipe (a categoria mais
relevante deste deck em particular, como esperado).

## Bug de design: modelo assumia 100% da mesa mirando em mim, todo turno, de todo oponente — 2026-09-20

**Gatilho:** mesmo achado do usuário aplicado ao Megatron primeiro —
*"se sempre for 3 contra 1, aí não consigo fazer nada, nunca!"* —
medição real mostrou 88,4% das rodadas com pelo menos 1 evento de
interação contra mim, o pior dos 3 decks. Raciocínio completo e opções
levantadas em `megatron-tyrant-mardu/checklist-oraculo.md`.

**Corrigido:** mesmo padrão do Megatron/Ur-Dragon —
`OPPONENT_ATTENTION_CHANCE = 1/NUM_OPPONENTS`, gate rolado no início de
`try_smart_opponent_turn()` antes de qualquer categoria.

**Validação:** modo padrão 100% bit-idêntico ao HEAD anterior (5.000
seeds) + regressão de 20.000 partidas no modo resiliência, 0 exceções.

**Resultado (A/B mesma seed, 2000 jogos):**

| Métrica | Antes do gate | Depois do gate |
|---|---|---|
| Rodadas com zero interação | 11,6% | 50,1% |
| Avg ataques de oponente sofridos | 4,01 | 1,47 |
| Avg vida final | 33,69 | 37,67 |

## Bug real de orquestração de turno (2ª rodada): wipe é simétrico pra mesa inteira — 2026-09-20

**Gatilho:** mesmo achado do usuário aplicado ao Megatron primeiro —
*"se jogador A faz wipe, jogador C não tem como atacar até voltar ao
turno do jogador A, a não ser no caso de haste!"* — a correção anterior
só tornava wipe/ataque mutuamente exclusivos no MESMO turno do wiper.
Raciocínio e validação completos em
`megatron-tyrant-mardu/checklist-oraculo.md`.

**Corrigido:** mesmo padrão do Megatron/Ur-Dragon —
`state.wiped_this_round` (setado por `try_smart_opponent_wipe`,
resetado 1x por rodada), `try_smart_opponent_attack()` reduz a própria
chance pra `POST_WIPE_ATTACK_HASTE_FACTOR = 0.15` quando o flag está
ligado. Gate manual antigo removido de `try_smart_opponent_turn()`.

**Validação:** modo padrão confirmado 100% bit-idêntico ao HEAD anterior
(5.000 seeds) + regressão de 20.000 partidas no modo resiliência, 0
exceções.

**Resultado (A/B mesma seed, 2000 jogos):**

| Métrica | Antes (wipe só bloqueia o próprio turno) | Depois (wipe suprime a rodada inteira) |
|---|---|---|
| Avg board wipes sofridos | 1,579 | 1,573 |
| Avg ataques de oponente sofridos | 4,009 | 3,753 |
| Avg vida final | 33,69 | 34,11 |

## Bug real de orquestração de turno: wipe e ataque no mesmo turno de oponente — 2026-09-20

**Gatilho:** mesmo achado do usuário aplicado ao Megatron primeiro —
board wipe é sorcery (main phase de UM oponente), ataque vem de
criatura em campo DAQUELE MESMO oponente. Se o wipe for simétrico, ele
não ataca no mesmo turno. Regra #6 do CLAUDE.md. Raciocínio e
validação completos em `megatron-tyrant-mardu/checklist-oraculo.md`.

**Corrigido:** `try_smart_opponent_turn()` simula o turno de 1 oponente
por vez (`NUM_OPPONENTS = 3` por rodada, nova constante, mesma
convenção do Megatron/Ur-Dragon), wipe e ataque mutuamente exclusivos
dentro do MESMO turno de oponente.

**Validação:** teste dirigido (2000 seeds, exclusão mútua 100%) +
regressão de 20.000 partidas, 0 exceções + modo padrão intocado.

**Resultado (batch 2000 jogos mesma seed):**

| Métrica | Modelo antigo (1 rolagem/rodada) | Modelo novo (3 turnos/rodada) |
|---|---|---|
| Avg board wipes sofridos | 0,74 | 1,59 |
| Graveyard wipe sofrido (partidas) | 48,8% | 79,6% |
| Avg remoções inteligentes sofridas | 0,99 | 1,46 |
| Avg dano proxy total | 37,72 | 3,14 |

Queda AINDA mais acentuada que o Ur-Dragon (37,72→3,14, ~8% do valor
anterior) — Elesh Norn/Sanctum of All multiplicam praticamente todo o
board, e com board wipe agora disparando em quase 80% das partidas (em
vez de ~49%), o motor "que se realimenta" raramente sobrevive intacto
até o fim.

## Modo de resiliência portado do Megatron/Ur-Dragon (6 categorias + counterspell) — 2026-09-20

**Gatilho:** usuário pediu pra implementar mesmo assim, depois de eu
usar este deck como piloto pra avaliar esforço (achado que ele tem 2
lacunas estruturais sérias: sem `sacrifice()`/remoção central, sem
combate/P-T modelado nenhum). Pedido: mesmo comparativo antes/depois
que o Ur-Dragon.

**Achado real MAIS IMPORTANTE desta rodada:** o próprio docstring do
arquivo (linhas ~187-193) já documentava **Enduring Vitality** ("When
~ dies, if it was a creature, return it to the battlefield... It's an
enchantment") como fora de escopo — mas especificamente PORQUE "este
simulador não mata criaturas nomeadas... essa cláusula nunca teria
janela real pra disparar". Ao implementar wipe/remoção pela 1ª vez
neste arquivo, essa janela passa a existir de verdade — se eu não
tratasse isso, teria reintroduzido exatamente o gap que a nota dizia
ser estruturalmente impossível. Confirmei o oráculo real via Scryfall
antes de implementar (Regra #1): *"When Enduring Vitality dies, if it
was a creature, return it to the battlefield under its owner's
control. It's an enchantment. (It's not a creature.)"*

`remove_permanent()` trata isso: na primeira morte como criatura, ela
NUNCA vai pro cemitério — volta direto pro campo como enchantment puro
(`state.enduring_vitality_enchantment_only`). E `try_smart_opponent_
wipe()` precisa saber que, uma vez flagada, ela **não é mais alvo
legal de "destroy all creatures"**, mesmo `is_creature_card()` (lookup
estático no `CARD_DB`) dizendo que sim — mesmo padrão do Megatron-
Vehicle/Living-Metal (Regra #3 do CLAUDE.md: conceito compartilhado
errado pra um subconjunto de quem o lê, porque é um efeito contínuo
que muda o tipo, não o tipo impresso na carta).

**Outras diferenças estruturais reais vs. Megatron/Ur-Dragon:**
- Sem `power`/`toughness` rastreado em NENHUMA criatura (`Card` só tem
  `mv`/`ctype`/`tags`) — ataque de oponente aqui NUNCA é bloqueado,
  mesma limitação do Ur-Dragon, mais extrema (nem o combate do PRÓPRIO
  jogador existe neste arquivo).
- Sem taxa de comandante nenhuma (diferente do Megatron/Ur-Dragon) —
  counterspell mais simples de portar, sem bookkeeping de taxa.
- Alvo do graveyard snipe usa o MESMO critério que `do_life_origin_
  reanimate()`/`do_hall_of_heliods_generosity()` já usam (maior MV
  entre ENCANTAMENTO no cemitério) — recursão real deste deck é de
  encantamento, não de artefato/Dragão.
- `INTERACTION_ENGINE_PRIORITY` curada a partir do `auditoria.md` real
  (seção 2, "motor que se realimenta"): Sanctum of All (dobra Shrine
  com 6+ em campo + tutor, multiplicador central), Elesh Norn (dobra
  ETB incondicional), Sythis/Sanctum Weaver (draw/mana), shrines de
  draw/drain recorrentes, Go-Shintai of Life's Origin, Displacer
  Kitten.

**Validação:** 6 testes unitários dirigidos (gating; **Enduring
Vitality retorna como enchantment ao morrer, nunca vai pro cemitério**;
**2º wipe confirma que ela fica IMUNE uma vez flagada não-criatura**;
removal mira prioridade correta; graveyard snipe mira maior MV
encantamento; counterspell sem taxa) + 5.000 seeds de equivalência
bit-a-bit do modo padrão (0 diferenças) + smoke test + regressão de
20.000 partidas em CADA modo, 0 exceções nos dois.

**Resultado (A/B 2000 jogos mesma seed):**

| Métrica | Padrão | Resiliência |
|---|---|---|
| Turno médio de conjuração (resolveu) | 3,60 | 3,68 |
| Nunca resolveu em 8 turnos | 0,9% | 0,9% |
| Avg dano proxy total | 231,65 | 37,72 (16% do original) |
| Avg drain proxy total | 33,61 | 6,89 |
| Avg dobras via Elesh Norn | 80,93 | 11,05 |
| Avg tokens criados | 53,84 | 14,20 |
| Avg board wipes sofridos | — | 0,74 (11,43 criaturas perdidas quando dispara) |
| Graveyard wipe sofrido (partidas) | — | 48,8% |
| Avg remoções inteligentes sofridas | — | 0,99 |
| Avg counterspells sofridos | — | 0,12 |

Queda proporcional MAIOR que o Ur-Dragon (16% vs. 31% do dano
original) — coerente com a estrutura do deck: Elesh Norn e Sanctum of
All são multiplicadores praticamente sobre TUDO (qualquer ETB de
Shrine), então perdê-los (ou perder Shrines em massa pro board wipe —
11,43 em média por wipe, contra um board médio de ~10 Shrines) corta o
motor de forma muito mais desproporcional do que no Ur-Dragon.

## Auditoria oráculo-por-oráculo completa — 2026-09-13

Extensão pra este deck da mesma auditoria já feita no Megatron/Azula/
Beorn/Captain Storm: oráculo real via Scryfall pras 90 cartas
não-terreno-básico + comandante (`POST /cards/collection`, 2 lotes, 0
`not_found` — sem MDFC/split neste deck), comparado cláusula-por-cláusula
contra o `heibai_goldfish_v1.py` atual.

**Contexto importante:** este deck já tinha passado por 3 rodadas de
auditoria anteriores (2026-08-27, 2026-08-28, e uma releitura linha-a-
linha completa em 2026-09-01 que não achou NENHUM bug de comportamento
novo — ver seção abaixo). Era, de longe, o simulador mais maduro desta
sessão até agora. Mesmo assim, esta rodada achou **5 gaps reais**, todos
sutis o bastante pra terem escapado das 3 rodadas anteriores — a maioria
em cantos que as rodadas passadas não cobriram diretamente (contabilidade
de custo de habilidade ativada que compartilha `{T}` com a própria
habilidade de mana da fonte, e cartas "interaction"-tagged cujo próprio
gatilho nunca era despachado por serem do `ctype` errado pro dispatch
genérico existente).

**5 gaps reais encontrados e corrigidos** (nenhum exigiu adicionar/cortar
carta, só corrigir como habilidades já presentes são modeladas):

1. **The Mind Stone — custo do harness nunca pagava a mana fantasma
   perdida.** Oráculo real: `"{5}{W}, {T}: Harness The Mind Stone."` — o
   próprio `{T}` do harness é O MESMO `{T}` da habilidade de mana dela
   (`{T}: Add {W}`), então ativar o harness custa, na prática, os 6 mana
   do custo impresso MAIS a mana que ela deixaria de produzir usando o
   `{T}` no harness em vez do tap normal (exatamente o mesmo padrão já
   documentado e corrigido pra Hall of Heliod's Generosity neste mesmo
   arquivo, herdado do Phyrexian Tower no Edgar Markov). O código
   cobrava só os 6 mana impressos (`remaining_mana(state) >= 6`), dando
   mana fantasma toda vez que harnessava. Corrigido: custo efetivo agora
   é 7 (`>= 7`, `spend_mana(state, 7)`). Este é o achado com maior efeito
   cascata na simulação — atrasa quando (e quantos turnos) o motor `∞`
   de blink repetível fica ativo, reduzindo bastante gatilhos de ETB
   repetidos (Elesh Norn doubles, Aura Shards, Purphoros) ao longo da
   partida — queda esperada, não um efeito colateral acidental (ver
   métricas abaixo).
2. **Waterbender's Restoration — X sempre tratado como 1.** Oráculo
   real: `"waterbend {X}... Exile X target creatures you control."` — X é
   pago TAPANDO artefatos/criaturas (não mana), e como este simulador não
   modela ataque/bloqueio, tapar criaturas pra pagar não tem custo real
   nenhum algum aqui. O código anterior sempre exilava exatamente 1
   criatura (a de maior valor), mesmo quando X poderia escalar pra
   exilar TODAS as criaturas em campo de uma vez — o que importa de
   verdade quando Purphoros ou Aura Shards estão em campo, porque CADA
   criatura reentrando dispara o gatilho delas separadamente (multiplica
   valor real, não só X cosmético). Corrigido: se Purphoros ou Aura
   Shards estiver em campo, X = todas as criaturas controladas; senão, X
   continua 1 (só a de maior valor de ETB próprio, mesmo comportamento de
   antes — sem esses 2 multiplicadores, exilar mais de uma criatura não
   agrega valor real neste modelo).
3. **Touch the Spirit Realm — nunca era conjurada, e mesmo se fosse, seu
   próprio ETB nunca era contado.** Duplo problema: (a) a carta é um
   `Enchantment` (não instant/sorcery), mas estava marcada com a tag
   genérica `"interaction"`, que só é lida dentro de
   `resolve_instant_sorcery()` — nunca despachada pra cartas de
   `ctype == "enchantment"`, então mesmo que fosse conjurada, seu próprio
   "When this enchantment enters, exile up to one target artifact or
   creature" nunca disparava/contava nada; (b) o loop guloso do
   `main_phase()` exclui TODA carta "interaction"-tagged do pool de
   `castables` (decisão deliberada de uma rodada anterior — "um piloto
   real segura essas cartas até ter alvo", correta pras reativas puras
   tipo Path to Exile/contramagia), mas Touch the Spirit Realm tem
   "up to one" (alvo OPCIONAL) — ao contrário das reativas puras, vale a
   pena conjurar só pelo CORPO (dispara o pacote Enchantress/Sythis/
   Herald/Hallowed Haunting, conta pra `enchantment_count()` da Sanctum
   Weaver), mesma classe de exceção já reconhecida pra Annie Joins Up
   (que também é "interaction"-tagged mas tem um efeito estático real
   modelado). Corrigido: adicionada à mesma exceção da Annie Joins Up no
   filtro de `castables` (mas em grupo de prioridade MAIS BAIXO que o
   motor real de Shrines/encantamentos — um piloto racional não compete
   por mana com Shrines só pra jogar uma remoção sem alvo, só gasta mana
   sobrando nela), e seu próprio ETB agora conta em
   `interaction_spells_cast_total` via `enter_battlefield()`.
4. **Annie Joins Up — o próprio ETB de 5 dano nunca disparava.** Oráculo
   real: `"When Annie Joins Up enters, it deals 5 damage to target
   creature or planeswalker an opponent controls."` Só o dobrador
   estático dela (`legendary_creature_doubler`) estava implementado; a
   ETB em si — mesmo como proxy de interação sem efeito de tabuleiro
   (regra 1 da sessão, sem oponente real) — nunca era sequer CONTADA em
   lugar nenhum, porque Annie é um `Enchantment` (não Shrine, não
   criatura) e `enter_battlefield()` não tinha nenhum dispatch específico
   pra ela. Corrigido: novo hook em `enter_battlefield()`, incrementa
   `interaction_spells_cast_total` passando por `resolve_times()` (Elesh
   Norn pode dobrar — "permanente entrando causa gatilho" é genérico o
   bastante pra cobrir; a própria Annie NÃO dobra a si mesma, porque seu
   dobrador exige que a FONTE do gatilho seja uma criatura lendária, e
   Annie é enchantment puro, não criatura).
5. **Go-Shintai of Lost Wisdom — mill de oponente nunca contava como
   interação usada.** As outras 2 habilidades pagas de end step dos
   Go-Shintai que também dependem de alvo de oponente (Hidden Cruelty,
   "destroy target creature"; e a ativada de Sanctum of Shattered
   Heights, dano a criatura/planeswalker) já incrementavam
   `interaction_spells_cast_total` como proxy — só o mill de Lost Wisdom
   (`"target player mills X cards"`) fazia `pass`, sem contar nada,
   apesar de pagar o MESMO custo `{1}` real todo turno junto com as
   outras 3. Inconsistência de contabilidade, não intencional (o
   comentário só documentava "sem efeito no nosso lado", não justificava
   a omissão da métrica). Corrigido pra contar, mesma convenção das
   outras 3.

**Validação:** smoke test (98 nomes no `CARD_DB`, 99 cartas na
`BASE_LIBRARY`, 0 desconhecidas) + 2.000 partidas antes/depois (mesma
seed) + 20.000 partidas de regressão (seed 5.000.000+, turns=10), 0
exceções. Testes unitários dirigidos (1 script combinando as 5 correções)
confirmaram cada uma disparando: Mind Stone harness recusa com 6 mana
disponível e só harnessa com 7; Waterbender's Restoration exila as 4
criaturas em campo quando Purphoros está presente (vs. 1 sem ele);
Touch the Spirit Realm aparece em `castables` e conta interação ao ser
conjurada; Annie Joins Up conta interação ao entrar (e dobra via Elesh
Norn: 1→2); Go-Shintai of Lost Wisdom conta interação ao ativar.

**Leitura das métricas antes/depois (ver `goldfish-log.md`):** a maioria
caiu, não subiu — driver dominante é o fix #1 (Mind Stone harness), que
remove mana fantasma que estava acelerando o motor de blink repetível
mais do que deveria; o fix #2 (Waterbender's X) puxa pro lado contrário
(mais blinks) mas é um evento único por partida (1 cópia na lista),
insuficiente pra compensar o efeito cascata do #1 ao longo de 8 turnos.
Padrão consistente com o já documentado nesta sessão (Azula, Captain
Storm): corrigir mana fantasma/custo não-pago tende a REDUZIR médias,
diferente de corrigir uma habilidade 100% ausente (que tende a subir).

---

## Reconfirmado sem gaps novos (3ª+4ª rodada de releitura, além da de 2026-09-01)

Todo o resto do oráculo das 90 cartas + comandante foi conferido
cláusula-a-cláusula de novo contra o código atual — nenhum outro desvio
encontrado além dos 5 acima. Alguns pontos verificados especificamente
por serem os mais fáceis de esconder um bug sutil:
- Todos os 90 custos de mana (`mv` no `CARD_DB`) batem exatamente com o
  `mana_cost` real do Scryfall — conferido carta a carta, não amostrado.
- `FETCH_NAMES` (tag `"fetch"`) segue genuinamente sem uso fora do
  cadastro — não é bug: no modelo de mana TOTAL (não pip-a-pip) deste
  deck, um fetch land parado em campo já conta como 1 mana genérico
  igual a qualquer terreno buscado por ele, então "buscar de verdade"
  não muda o total (já documentado como correto no checklist anterior,
  reconfirmado aqui).
- O anthem estático da Weaver of Harmony ("Other enchantment creatures
  you control get +1/+1") **não tem nenhum código associado** — o
  checklist anterior (2026-08-24) marcava isso como "✅ implementado",
  o que é impreciso: como este simulador não modela P/T por permanente
  individual nem combate real (mesma razão estrutural de Southern Air
  Temple/Purphoros pump/Destiny Spinner), um anthem de +1/+1 não tem
  efeito numérico capturável aqui — é 📊 estrutural, não ✅. Correção de
  documentação, sem mudança de código (o comportamento sempre foi
  "sem efeito", só a legenda no checklist antigo estava errada).
- `Waterbender's Restoration`/`Skybind`/`The Mind Stone` (∞): timing
  adiado (`pending_end_step_returns`) continua correto nos 3, sem
  regressão do fix do item 2 acima (só mudou QUANTAS criaturas entram na
  fila, não QUANDO elas voltam).

---

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado ao
Toph, Beorn the Fierce e Edgar Markov.

89 cartas não-terreno-básico do decklist (comandante + deck, excluindo
Forest/Island/Mountain/Plains/Swamp básicas), oráculo real buscado ao
vivo via Scryfall (`POST /cards/collection`, 2 lotes) contra o
`heibai_goldfish_v1.py` atual.

**Contexto importante:** este deck (5 cores, WUBRG, tribal Shrine) já era
o mais estruturalmente sofisticado da sessão — construído do zero em
2026-08-24 com um dispatch central pra Shrines (`shrine_enters()`), um
motor de blink completo com timing atômico vs. adiado corretamente
diferenciado, e 3 dobradores de gatilho distintos (Elesh Norn/Sanctum of
All/Annie Joins Up) implementados sem se confundirem. Passou por rodadas
de correção em 2026-08-27 (timing de blink adiado, tag `untap_all` morta)
e 2026-08-28 (auditoria de habilidades estáticas). A releitura linha-a-
linha desta rodada **não achou nenhum bug de comportamento novo** — só 2
comentários que usavam linguagem de "julgamento de valor" (Weaver of
Harmony, Destiny Spinner) para justificar exceções que na verdade já são
genuinamente estruturais. Reclassificados/reescritos, sem mudança de
comportamento (ver docstring do arquivo).

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — sem combate real, sem oponente modelado, sem
  P/T por permanente individual fora do agregado, ou sem janela de
  "untap step do oponente"/"ataque do oponente" que este sim nunca avança.
- 📝 **Documentado, fora de escopo genuíno** — exceção arquitetural real
  (ex: "escolher qual gatilho copiar" — mesma classe do Strionic Resonator).

## Terrenos (35, incluindo básicas contadas genericamente)
Todos os terrenos (duais, fetches, triomes, Command Tower/Arcane Signet
equivalentes) contam como fonte de mana genérica — modelo TOTAL, não
pip-a-pip (decisão documentada no topo do arquivo, consistente pra TODOS
os terrenos, não uma simplificação seletiva). Fetches (`FETCH_NAMES`)
não "buscam" de verdade porque não há cor/tipo pra fixar num modelo sem
pips — ✅ correto dado o modelo de mana escolhido.
- **Abandoned Air Temple**: enters tapped condicional — ✅; `{3}{W},{T}`:
  +1/+1 em cada criatura — ✅ `do_shrine_mainphase_triggers()`/ativada dedicada.
- **Hall of Heliod's Generosity**: `{1}{W},{T}`: encantamento do
  cemitério pro topo — ✅ `do_hall_of_heliods_generosity()`.
- **Yavimaya, Cradle of Growth**: todo terreno é Forest — ✅ (fixação, sem efeito numérico no modelo total, consistente).
- Demais terrenos: mana genérica — ✅.

## Sanctums / Hondens / Temples (as 17 Shrines)
Dispatch central `shrine_enters()` cobre TODAS: gatilho "esta entra" (X=Shrines,
inclusive ela mesma) + "outra Shrine entra" (efeito fixo). Cada uma
verificada individualmente:
- **Crescent Island Temple**: Monk tokens (própria + outras) — ✅.
- **Go-Shintai of Ancient Wars**: first strike 📊 combate; end step dano
  pago — ✅ `do_go_shintai_endstep()`.
- **Go-Shintai of Hidden Cruelty**: deathtouch 📊 combate; end step
  destrói criatura — 📝 opponent_dependent (proxy de interação).
- **Go-Shintai of Life's Origin**: `{WUBRG},{T}` reanima encantamento —
  ✅ `do_life_origin_reanimate()`; ETB token (self OU outra Shrine
  nontoken) — ✅ `shrine_enters()`.
- **Go-Shintai of Lost Wisdom**: flying 📊; end step mill — 📊 opponent_dependent (proxy).
- **Go-Shintai of Shared Purpose**: vigilance 📊; end step Spirit tokens = Shrines — ✅.
- **Honden of Life's Web**: upkeep Spirit tokens = Shrines — ✅ `do_shrine_upkeep_triggers()`.
- **Honden of Seeing Winds**: upkeep draw = Shrines — ✅ idem.
- **Kyoshi Island Plaza**: ETB busca X básicas; outra Shrine entra: busca 1 — ✅ `shrine_enters()`.
- **Northern Air Temple**: ETB drain X; outra Shrine entra: drain 1 — ✅ idem (`proxy_drain`).
- **Sanctum of All**: upkeep busca Shrine; dobrador (6+ Shrines) — ✅ `resolve_times()`.
- **Sanctum of Calm Waters**: main phase draw X, descarta 1 — ✅ `do_shrine_mainphase_triggers()`.
- **Sanctum of Fruitful Harvest**: main phase mana X — ✅ idem.
- **Sanctum of Shattered Heights**: descarta terreno/Shrine: dano X — ✅ `do_sanctum_shattered_heights()` (opponent_dependent no alvo, mas o CUSTO/ativação é real).
- **Sanctum of Stone Fangs**: main phase drain X — ✅ `do_shrine_mainphase_triggers()`.
- **Southern Air Temple**: ETB counters X; outra Shrine entra: +1/+1 — ✅.
- **The Spirit Oasis**: ETB draw X; outra Shrine entra: draw 1 — ✅.

## Criaturas / Payoffs
- **Argothian Enchantress**: shroud 📊; cast encantamento: draw — ✅ `on_cast_enchantment()`.
- **Birds of Paradise / Bloom Tender / Sanctum Weaver**: mana dorks, doença de invocação real — ✅ `dork_mana()`.
- **Deadeye Navigator**: soulbond + blink repetível — ✅ `do_deadeye_navigator()`.
- **Displacer Kitten**: cast não-criatura: blink — ✅ (dispatch de conjuração).
- **Dryad of the Ilysian Grove**: land drop extra — ✅; fixação — 📊 (modelo total).
- **Elesh Norn**: vigilance 📊; dobrador de ETB — ✅ `resolve_times()`; nega gatilhos de oponente — 📊 opponent_dependent (sem gatilho de oponente modelado, já N/A por padrão).
- **Enduring Vitality**: vigilance 📊; mana em massa — ✅ (via tag em `dork_mana`/`total_mana`, criaturas ganham `{T}: any color`); morre→volta como encantamento — 📝 nunca alcançável (sem morte de criatura nomeada, mesma razão documentada no topo do arquivo).
- **Go-Shintai of Ancient Wars/etc.**: ver seção Shrines acima.
- **Herald of the Pantheon**: custo -{1} encantamento — ✅ `effective_cost()`; cast encantamento: +1 vida — ✅.
- **Purphoros**: indestructible 📊; dano por criatura entrando — ✅ (dispatch central de ETB); bombeio `{2}{R}` — 📝 buff temporário de combate (mesma família de Craterhoof/Destiny Spinner).
- **Seedborn Muse**: untap em turno de OPONENTE — 📊 genuinamente fora de escopo (sim nunca avança turno de oponente), corpo vanilla 2/4.
- **Sythis**: cast encantamento: +1 vida + draw — ✅.
- **Thassa**: indestructible 📊; blink de end step — ✅ `do_endstep_blinks()`; tap ativado `{3}{U}` — 📊 combate (tapar bloqueador, sem combate real modelado).
- **Weaver of Harmony**: anthem +1/+1 enchantment creatures — ✅; copiar ativada/disparada — 📝 exceção estrutural genuína (escolher QUAL gatilho copiar entre 17 Shrines com efeitos diferentes, mesma classe do Strionic Resonator — reclassificado 2026-09-01, não é mais "baixo valor").

## Encantamentos
- **Annie Joins Up**: ETB 5 dano — 📝 opponent_dependent (proxy interação); dobrador de gatilho de criatura lendária — ✅ `resolve_times()`.
- **Destiny Spinner**: can't be countered — 📊; `{3}{G}` land vira X/X — 📝 buff temporário de combate (reclassificado 2026-09-01, não é mais "baixo valor").
- **Enchantress's Presence**: cast encantamento: draw — ✅.
- **Greater Auramancy**: shroud pra encantamentos — 📊 sem targeting de oponente modelado (mesma razão de Sterling Grove).
- **Hallowed Haunting**: 7+ encantamentos: voo/vigilance — 📊 combate; cast encantamento: Spirit token X/X — ✅.
- **In Search of Greatness**: upkeep cast grátis ou scry — ✅ `do_in_search_of_greatness()`.
- **Skybind**: Constellation blink — ✅ `on_any_enchantment_enters()`, `best_nonenchantment_permanent_to_reblink()`.
- **Sphere of Safety**: defesa pura de ataque de oponente — 📊 (sem ataque de oponente modelado).
- **Sterling Grove**: shroud — 📊; sac: tutor encantamento pro topo — ✅ `do_sterling_grove_tutor()`.
- **Teleportation Circle**: end step blink — ✅ `do_endstep_blinks()`.

## Interação / Proteção
Todas (An Offer You Can't Refuse, Arcane Denial, Aura Shards, Dovin's
Veto, Heroic Intervention, Path to Exile, Swan Song, Swords to
Plowshares, Teferi's Protection, Touch the Spirit Realm) — 📝/📊
opponent_dependent, contadas como interação usada sem efeito colateral
no próprio campo (convenção consistente da biblioteca inteira). **Aura
Shards** e **Ephemerate** são exceções parciais reais: Aura Shards
("criatura entra: destrói artefato/encantamento alvo") é opponent-target
mas o GATILHO em si (criatura entra) é real — ✅ contado; Ephemerate
(blink com rebound) é 100% self-target — ✅ `do_ephemerate()`.

## Ramp / Tutores
- **Aang's Journey**: kicker busca básica+Shrine — ✅ `search_land()`/dispatch dedicado, vida ✅ `gain_life()`.
- **Cultivate / Nature's Lore / Three Visits / Farseek**: busca terreno — ✅ `search_land()`.
- **Idyllic Tutor**: busca encantamento pra mão — ✅.
- **Replenish**: retorna todos os encantamentos do cemitério — ✅.
- **Waterbender's Restoration**: waterbend X, blink X criaturas (retorno adiado) — ✅ `resolve_instant_sorcery()`, `state.pending_end_step_returns`.

## Rocks
- **Arcane Signet / Sol Ring / The Mind Stone**: mana — ✅ `rocks_mana()`.
  The Mind Stone: indestructible 📊; harness + ∞ blink end step — ✅ `do_endstep_blinks()`.

---

## Resumo numérico

- **89 cartas.**
- **~110 linhas de cláusula.**
- **✅ Implementado:** ~75 linhas.
- **📊 N/A estrutural:** ~25 linhas (combate, oponente, "untap step do
  oponente" genuinamente fora do loop de simulação).
- **📝 Documentado, fora de escopo genuíno:** ~10 linhas (proxies de
  interação/remoção sem alvo real de oponente; Weaver of Harmony —
  escolha entre 17 tipos de gatilho, mesma classe do Strionic Resonator).
- **🐛 Corrigido nesta rodada:** nenhum bug de comportamento novo — 2
  comentários reclassificados de "baixo valor esperado" pra justificativa
  estrutural real (Weaver of Harmony, Destiny Spinner), sem mudança de
  código funcional.

Este foi o único dos decks auditados até agora (Toph, Beorn, Edgar
Markov, Hei Bai) em que a releitura linha-a-linha não achou nenhum gap
funcional novo — consistente com o nível de detalhe já presente no
docstring do arquivo antes desta rodada.
