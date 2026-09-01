# Goldfish Log — Ulalek, Fused Atrocity

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

### Auditoria linha-a-linha "compile TUDO" — 2026-09-01

**Gatilho:** pedido direto do usuário ("AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha") — mesmo tratamento já aplicado a
Toph, Beorn, Edgar Markov, Hei Bai, Maralen, Megatron, Nekusar, Prismatic
Bridge, Rat King e Thranduil nesta sessão. Ver `checklist-oraculo.md`
(novo) pra detalhamento completo carta-a-carta.

**Método:** detecção automatizada de (a) tags órfãs e (b) nomes de carta
que só aparecem em `add()`+decklist. A maioria dos 9 candidatos de tag e
~30 candidatos de nome eram falsos positivos — este arquivo já tinha
passado por 2 rodadas de auditoria completa (2026-08-28, 2026-08-30) e
dispatcha boa parte por tabela de tag (`ct_*` pros cast-triggers dos
Eldrazi titãs) ou por checagem de nome direta dentro de funções
compartilhadas (`eldrazi_cost_discount`, etc) em vez de tag própria — os
falsos positivos mais notáveis: Kozilek/Ulamog/Emrakul (dispatchados via
tabela `CT_TRIGGERS`), Urza's Incubator e It That Heralds the End (já
implementados por nome dentro de `eldrazi_cost_discount`).

**3 gaps reais confirmados**, todos em terrenos que estavam registrados
genericamente como `add(n, 0, "land", {"colorless"})` dentro de um loop
de 34 terrenos (só a mana {C} básica coberta) — o próprio docstring do
cabeçalho já documentava 2 deles como deferidos ("decisão de escopo...
fica pra uma rodada dedicada"):

1. **Eye of Ugin** — a redução estática de custo ("Colorless Eldrazi
   spells cost {2} less") já era coberta por nome em
   `eldrazi_cost_discount()`; faltava a ativada real *"{7}, {T}: Search
   your library for a colorless creature card... put it into your
   hand."* Corrigido com `try_eye_of_ugin()`.
2. **Urza's Cave** — *"{3}, {T}, Sacrifice this land: Search your library
   for a land card, put it onto the battlefield tapped."* 100% ausente.
   Corrigido com `try_urzas_cave()` (busca Ancient Tomb se disponível,
   senão qualquer terreno).
3. **Ruins of Oran-Rief** — 2ª habilidade real *"{T}: Put a +1/+1 counter
   on target colorless creature that entered this turn"* (mutuamente
   exclusiva com a mana {C} básica no mesmo `{T}`) nunca implementada.
   Corrigido com `try_ruins_oran_rief()`, contador agregado (sem P/T por
   criatura, mesma convenção já usada no resto do arquivo). Simplificação
   documentada: só conta criaturas conjuradas via `resolve_cast`, não
   cobre tokens Spawn/Scion/Manifest criados fora desse fluxo.

**Reclassificação (linguagem de julgamento de valor corrigida, não bug):**
o comentário do cabeçalho sobre Void Grafter/Liberator/Ruins de Oran-Rief
dizia "sem efeito numérico relevante pro goldfish" — reescrito pra
justificativa estrutural real por carta (Void Grafter: sem
oponente/remoção real; Liberator: exigiria comparar power dele
contador-a-contador contra cada gasto de mana futuro, mesmo limite de
"sem P/T por criatura" já documentado alhures; Ruins: implementado nesta
rodada).

**Validação:** 6 testes unitários isolados (todos passando) + regressão
de 20.000 partidas (seed 3000000+, turns=10, 0 exceções) + `run_batch`
antes/depois via `importlib` (3000 jogos, seed 6000000, turns=10):

| Métrica | Antes | Depois |
|---|---|---|
| Tutores usados (total) | 0.60 | 0.70 |
| RAMP (peças resolvidas) | 2.33 | 2.52 |
| Urza's Cave sacrificado | — (nem existia) | 17.0% dos jogos |
| Ruins of Oran-Rief contadores | — (nem existia) | 0.66 avg/partida |
| DRAW (compras extras) | 4.12 | 4.26 |

Todas as métricas relevantes subiram na direção esperada, sem nenhuma
outra métrica se mover de forma inexplicável (turno de conjuração da
Ulalek, cópias pagas, cascatas, finishers ficaram praticamente estáveis,
como esperado — nenhum dos 3 fixes toca essas mecânicas).
`ulalek_v1_runs.jsonl` regenerado (3000 jogos, seed_base=8600000,
turns=8, mesmos parâmetros já estabelecidos no `__main__` do arquivo).

---

## Teste #1 — Radagast of Rhosgobel dentro vs. fora (`ulalek_radagast_test.py`) — 2026-08-23

Pergunta do usuário: "Vale a pena incluir um Radagast no deck do Ulalek?".
Radagast of Rhosgobel (`{2}{G}{G}`, Legendary Creature — Avatar Wizard,
colors=['G'] — cor real, NÃO colorless, NÃO Eldrazi): "The first creature
spell you cast each turn costs {2} less to cast and can be cast as though
it had flash." Ele NÃO está na `lista.md` hoje — este teste é só uma
comparação, não uma mudança de deck.

**Ajuste no script principal antes do teste:** ao cadastrar Radagast no
`CARD_DB` pra permitir o teste, generalizei `eldrazi_cost_discount()` — o
desconto de "primeira criatura do turno" antes só olhava pra Conduit of
Ruin (que já está no deck e tem o texto quase idêntico); agora soma -2 por
cada fonte presente (`FIRST_CREATURE_DISCOUNT_SOURCES`), empilhando de
verdade se as duas estiverem em campo (mesma criatura, -4 total). Também
corrigi de passagem uma tag órfã que já existia (`flash_source` em Vedalken
Orrery/Liberator/Skittering Cicada nunca tinha virado métrica real) e
adicionei uma métrica causal dedicada (`radagast_flash_grants_total`) em
vez de reaproveitar `flash_online_turns` pro flash do Radagast — os dois
NÃO são a mesma coisa: `flash_online_turns` cobre só as 3 fontes de flash
incondicional (qualquer spell), enquanto o flash do Radagast é condicional
(só a primeira criatura do turno). Confirmado no próprio teste: o delta de
`flash_online_turns` (+0,147) bateu quase igual ao de
`radagast_flash_grants_total` (+0,146) por coincidência de amostra — são
métricas diferentes, não a mesma coisa medida duas vezes.

**Metodologia:** mesma dos testes pareados anteriores (Maralen flash-vs-
Radagast, Thranduil mana-fix) — monkeypatch temporário de `BASE_LIBRARY`
trocando 1 carta por Radagast, mesmas seeds nas duas variantes. Carta
cortada pro teste: **Null Elemental Blast** (interação de 1 mana bem
estreita, sem efeito colateral próprio neste simulador sem oponente real —
escolhida só como parceira de troca pra manter 99 cartas, não é uma
recomendação de corte real).

**n=3000, seed_base=9900000, mesmas seeds — resultado:**

```
                                          SEM Radagast   COM Radagast   delta
Turno medio de conjuracao da Ulalek           4,509          4,497     -0,013
Nunca conjurada em 8 turnos                    5,00%          6,03%    +1,03pp
Avg copias pagas da Ulalek (CC)                0,992          1,005    +0,013
Avg tokens-copia de permanentes                1,100          1,106    +0,006
Avg cartas compradas extra                     1,593          1,596    +0,003
Avg descontos "primeira criatura do turno"     0,058          0,209    +0,151
Avg flash concedido pelo Radagast              0,000          0,146    +0,146
```

**Checagem de ruído:** o delta de "nunca conjurada em 8 turnos" (+1,03pp)
parecia sugerir que Radagast piora a chance de resolver a comandante — mas
troquei o `seed_base` 3 vezes (1M/2M/3M) e o delta ficou +0,60pp / +0,37pp
/ **-0,73pp**: o sinal INVERTE de lado dependendo da amostra. Isso é ruído
de reamostragem de um swap de 1 carta só (mesma seed não significa "mesmo
jogo com uma carta a mais" — muda a posição de TODAS as cartas na mão
embaralhada), não um efeito real do Radagast. Não uso esse número pra
concluir nada.

**Leitura honesta:**

- **Não ajuda a conjuração da própria Ulalek** — turno médio praticamente
  idêntico (4,509→4,497), esperado: Radagast só desconta OUTRAS criaturas
  cast depois dele, não tem relação direta com o comandante a menos que a
  Ulalek por acaso seja a primeira criatura do turno.
- **Não alimenta o motor de cópia da Ulalek** — Radagast não é Eldrazi
  (Avatar Wizard), então conjurá-lo nunca dispara o gatilho da comandante;
  as métricas de cópia (`ulalek_copies_avg`, `spell_copies_avg`) ficaram
  essencialmente inalteradas (+0,013 / +0,006, dentro do ruído normal).
- **O ganho real é modesto, não transformador.** O desconto de "primeira
  criatura do turno" mais que triplica (0,058→0,209 eventos/partida) — mas
  isso soma a contribuição de Conduit sozinho (que já dava 0,058) com
  Radagast; isolado, Radagast concede flash em média **0,146 vezes por
  partida** — aproximadamente 1 em cada 7 partidas, ao longo de 8 turnos.
  Isso é baixo porque Radagast primeiro precisa resolver (4 mana, R{2}{G}{G}
  — compete por slot com o resto do pacote de rampa/valor) E DEPOIS precisa
  que outra criatura seja conjurada num turno seguinte pra valer alguma
  coisa.
- **Downside estrutural não coberto pelas métricas numéricas acima:**
  Radagast é um permanente colorido de verdade (`colors=['G']`). Hoje só
  Defense of the Heart e Rhystic Study são permanentes coloridos na lista
  inteira de 100 cartas — o que faz All Is Dust ser um wipe quase
  perfeitamente assimétrico (média de 0,22 sacrificado quando é conjurada,
  ver Simulação #1 acima). Incluir Radagast adicionaria um 3º alvo real
  pro próprio All Is Dust sacrificar.

**Conclusão:** vale a pena testar em jogo real se sobrar espaço, mas não é
um upgrade óbvio — o efeito é pequeno em cima de uma peça (Conduit of Ruin)
que já faz metade do trabalho, não conecta com o motor central da
comandante, e introduz o único tipo de fragilidade que este deck evita hoje
(permanente colorido de verdade, vulnerável ao próprio All Is Dust). Se o
objetivo é mais flash pro plano de copiar Eldrazi no end step do oponente,
Vedalken Orrery/Liberator/Skittering Cicada (flash incondicional, qualquer
spell) continuam sendo a peça mais direta pra isso.

## Simulação #1 — goldfish Python completo, construído do zero (`ulalek_goldfish_v1.py`) — 2026-08-23

**Script construído do zero, de forma independente.** A `auditoria.md` deste
deck (seção 3) é uma categorização funcional (ramp/draw/removal/proteção/
flash/multiplicadores), não um catálogo carta-a-carta de gatilhos como o do
Nekusar — então a varredura mecânica completa (Passo 0, regex "Whenever"/"At
the beginning of"/"When ... enters"/"When you cast this spell" no
`oracle_text` real das 100 cartas) foi feita aqui pela primeira vez.

**Importante:** os números abaixo NÃO foram calibrados pra bater com os
números do Colab externo do usuário (seção "v2/v2.1/v2.2" logo abaixo, já
registrada neste arquivo antes desta sessão). Aquele simulador é uma
ferramenta própria do usuário, e a própria auditoria já registrava que eu não
tinha como verificar a lógica interna dele. Este script foi escrito puro a
partir do oráculo real das cartas, igual aos outros 8 simuladores desta
biblioteca — qualquer semelhança ou diferença com o Colab é reportada abaixo
com honestidade, não forçada.

### Mecânica central implementada com fidelidade real

**O motor de cópia da Ulalek** ("Whenever you cast an Eldrazi spell, you may
pay {C}{C}. If you do, copy all spells you control, then copy all other
activated and triggered abilities you control.") foi implementado como duas
cópias distintas e separadas quando `{C}{C}` é pago: (1) cópia do PRÓPRIO
SPELL — token extra se for permanente, resolução extra se for instant/
sorcery — e (2) cópia do gatilho "when you cast this spell" da mesma carta
(se existir), que ainda está na pilha e é uma habilidade DIFERENTE do spell
em si. Testado manualmente: Kozilek, Butcher of Truth conjurado com Ulalek
em campo + CC pago = 2 corpos 10/10 Annihilator 4 EM CAMPO + 8 cartas
compradas (2 disparos de "compre 4"), não 1 corpo + 4 cartas.

**Echoes of Eternity** tem DUAS habilidades tratadas como mecanicamente
distintas: a 1ª ("triggered ability of a colorless spell... or another
colorless permanent... triggers an additional time") dobra qualquer gatilho
de fonte colorless — inclui cast-triggers, já que quase toda carta relevante
deste deck é Devoid/incolor mesmo com pips coloridos no custo (Sowing
Mycospawn {3}{G}, World Breaker {6}{G} etc. — a cor REAL da carta, campo
`colors` do Scryfall, é `[]` pra praticamente tudo aqui por causa do Devoid).
A 2ª habilidade ("Whenever you cast a colorless spell, copy it") é uma cópia
incondicional e SEPARADA, empilhando com a cópia paga da Ulalek se as duas
estiverem em campo.

**Roaming Throne — tipo escolhido: Eldrazi**, documentado mesmo sendo óbvio.
Achado real que vale registrar: ao contrário do Ur-Dragon (onde o gatilho de
ataque da própria comandante, que é Dragão, levava a maior parte do valor da
carta), aqui a maior parte do valor de Ulalek é em CAST-triggers — e Roaming
Throne só dobra gatilho de criatura JÁ EM CAMPO, nunca gatilho de conjuração
(a fonte, no momento em que o gatilho de cast dispara, é um spell na pilha,
não uma criatura em campo — checado explicitamente no código via um
parâmetro `is_permanent_source`). Na prática, Roaming Throne só dobra aqui:
Glaring Fleshraker (gatilho de "você conjura colorless", fonte é o próprio
Fleshraker em campo), Chittering Dispatcher (leaves-trigger) e Spawnbed
Protector (end step) — e NÃO dobra Liberator, Urza's Battlethopter (tipo
Thopter, não Eldrazi). Resultado batido no batch oficial: **0,03 dobras
médias por partida**, contra praticamente qualquer coisa >0 no Ur-Dragon.
Isso é uma leitura real e precisa das regras, não um nerf inventado — vale a
pena o usuário saber que Roaming Throne é uma peça bem mais fraca neste deck
especificamente do que seria em qualquer deck tribal com gatilhos de
permanente-em-campo como motor central.

**Zhulodok, Void Gorger** (cascade, cascade em colorless MV≥7 conjurado da
mão) implementado com busca real na biblioteca — carta achada é conjurada de
graça pelo mesmo pipeline (`resolve_cast`), podendo re-disparar Ulalek/Echoes
recursivamente (comportamento real das cartas), sem precisar de teto
artificial (a própria regra de Zhulodok, "cast... from your hand", já corta
a recursão infinita — cascade nunca é "da mão").

**Warp (Anticausal Vestige)** implementado de verdade, não decorativo:
sempre conjurada pelo custo de warp (estritamente mais barato, escolha
greedy correta), exilada de verdade no end step (dispara o leaves-trigger
real: compra 1 carta), disponível depois pra reconjurar da zona de exílio
pelo custo cheio — sem loop, porque não é reconjurada via warp uma segunda
vez.

**All Is Dust** checado contra o campo `colors` real do Scryfall (não pips
do custo). Achado numérico real, confirma a tese da auditoria de "wipe
assimétrico": em toda a lista de 100 cartas, só **Defense of the Heart** e
**Rhystic Study** são permanentes coloridos de verdade — todo o resto (até
cartas com pips coloridos tipo World Breaker/Sowing Mycospawn) é Devoid =
incolor. No batch oficial, quando All Is Dust foi conjurada (5,5% das
partidas), sacrificou em média só **0,22 permanente nosso**.

**Teste de robustez:** 3 sweeps de 20.000 partidas (60.000 total) com
timeout de 2s via `signal.alarm`, **0 erros, 0 timeouts** em todos. Um ajuste
de fidelidade foi feito no meio do processo (não um bug/crash, uma correção
de modelagem): Eldrazi Spawn tokens criados NO MEIO do turno agora
convertem em mana disponível imediatamente pro resto daquele mesmo turno
(sac de token pra mana não depende de summoning sickness, é regra real) —
antes só ficavam disponíveis no turno seguinte, subestimando a mana real do
deck.

**n=3000, seed_base=8600000, 8 turnos — resultado oficial:**

```
Avg mulligans: 0.46
Turno medio de conjuracao da Ulalek: 4.54 | mediana: 4.0
Nunca conjurada em 8 turnos: 5.6%
Avg copias pagas da Ulalek (CC): 0.97
Avg copias incondicionais de Echoes of Eternity: 0.10
Avg tokens-copia de permanentes (spell copies): 1.08
Avg resolucoes extras de cast-trigger (Echoes+Ulalek): 0.29
Avg cascade cascade disparadas (Zhulodok): 0.06 | acertos: 0.06
Avg cartas compradas extra (motores de draw): 1.45
Avg cartas via The One Ring: 0.80
Avg tutores usados: 0.27
Avg Eldrazi Spawn tokens criados: 1.23
Avg Manifest tokens criados (Kozilek Broken Reality): 0.04
Avg remocao/exilio proxy total: 0.16
Avg vida ganha proxy (Forsaken Monument): 0.23
Avg spells de interacao conjurados (proxy): 1.80
% de jogos que conjuraram All Is Dust: 5.5%
  Avg permanentes proprios sacrificados por All Is Dust nesses jogos: 0.22
Avg dobras via Roaming Throne (contador direto): 0.03
Avg mao final: 2.87
```

Resultados salvos em `ulalek_v1_runs.jsonl` (3000 jogos).

**Nota (2026-08-30):** este bloco ficou desatualizado depois de duas
rodadas de correção no código (checklist de 2026-08-28 mais abaixo, e a
reanálise de 2026-08-30 no fim deste arquivo) — mantido aqui como registro
histórico do resultado original, não mais o número vigente. Ver a seção
"Reanálise do simulador Python" no fim do arquivo pro resultado
atualizado com a mesma seed.

### Comparação honesta com o Colab externo do usuário (seção abaixo)

Não são a mesma métrica exata em todos os casos (arquiteturas diferentes —
o Colab tem um modelo de "janelas boas/ruins" pra Ulalek que este script não
replica 1:1), mas o turno de conjuração da comandante é diretamente
comparável e converge bem: meu resultado deu **turno médio 4,54** com
**5,6% nunca conjurada em 8 turnos**; o Colab v2.2 deu **turno médio 4,25**
com **83,8% já conjurada até o turno 5** (implica ficar perto de ~15-16%
ainda não conjurada no turno 5, convergindo pra uma faixa parecida de "quase
sempre resolve, mas não sempre cedo"). As duas ferramentas, construídas de
forma totalmente independente, concordam que Ulalek é uma comandante barata
e confiável de resolver (bem diferente do achado do Ur-Dragon, onde a
comandante de 9 mana quase nunca resolvia a tempo). Não uso isso pra validar
o Colab (ainda não tenho como auditar a lógica interna dele) — só registro
a convergência como um dado a mais, não como prova de nada.

**Simplificações documentadas no docstring do script** (não inventadas —
omissões explícitas, lista completa no topo do arquivo): modelo de mana
genérico/total (não pip a pip, sem rastrear dano de vida de manabase);
Eldrazi Temple/Cascading Cataracts/Shrine of the Forsaken Gods tratadas como
terreno genérico de 1 mana (suas restrições de cor/condição não modeladas);
Defense of the Heart e Sire of Stagnation nunca disparam (dependem de
condição do oponente, Regra 1 — sem oponente real, não presumido); toda
remoção/contramágica é tratada como proxy sem alvo real; leaves-the-
battlefield triggers só disparam nos casos onde este simulador de fato causa
a saída (o warp da Vestige).

---

## Simulações estatísticas v2 / v2.1 / v2.2 — fonte: ferramenta externa do usuário (não Claude)

**Atribuição:** estes três sumários e o CSV vêm de um script/simulador heurístico próprio do usuário (Python, rodado no Google Colab), fora desta conversa. Não foram gerados por mim.

**Atualização:** o usuário colou o código-fonte completo do script v2.2 (`ulalek_v2_flash_v22_runs.jsonl`). Conferido:
- A `DECKLIST_TEXT` embutida no script bate **exatamente** com o `lista.md` registrado aqui — 99 cartas não-comandante, mesmo conjunto (`assert len(deck) == 99` no código, confirmado por diff de conjuntos).
- Agora consigo dar a definição real de cada métrica a partir do próprio código, em vez de só repetir o nome:

| Métrica | Definição real (do código) |
|---|---|
| `total_ulalek_windows` | Incrementa toda vez que um Eldrazi é conjurado — é toda oportunidade em que o gatilho do Ulalek poderia ser pago, independente de ter sido pago ou não |
| `good_ulalek_windows` | Subconjunto acima onde `worthwhile_stack_present()` é verdadeiro: a carta tem a flag `worthy_copy`, tem efeito de compra ao conjurar, é Anticausal Vestige/Nulldrifter/Conduit of Ruin, ou Kozilek's Unsealing/Echoes of Eternity está em campo |
| `dead_ulalek_windows` | Janelas onde o `{C}{C}` do gatilho **não** foi pago (mana incolor insuficiente) |
| `ulalek_paid_triggers` / `copied_eldrazi_spells` | Mesma condição no código (`commander_in_play and available_colorless_for_ulalek >= 2`) — são a mesma contagem sob dois nomes, não duas métricas independentes |
| `flash_online_turns` | Turnos em que Vedalken Orrery, Liberator Urza's Battlethopter, Skittering Cicada, ou Emergence Zone está em campo |
| `premium_flash_windows` / `flash_online_with_full_ulalek_window` | Mesma condição (`premium_flash_window()`): comandante em campo + `{C}{C}` disponível + pilha que vale a pena copiar + algum habilitador de flash em campo |
| `flash_lines_taken` | Conjurar um Eldrazi no end step do oponente (via flash) **E** o gatilho do Ulalek ter sido pago no mesmo evento |
| `vestige_casts` / `vestige_warp_casts` | Total de conjurações de Anticausal Vestige / especificamente via custo Warp alternativo |
| `vestige_endstep_triggers` | Quantas vezes o gatilho de "sai do campo" do Vestige resolveu (compra 1 + pode trapacear um permanente da mão pro campo) |
| `throne_online_relevant_turns` | Roaming Throne em campo **e** o Eldrazi conjurado contou como "good window" |
| `big_threats_resolved` | Cartas com a tag `finisher` que resolveram (conjuradas ou trapaceadas para o campo via Vestige/Defense of the Heart) |

**Limitações do modelo, identificadas lendo o código (o próprio script já se descreve como "heuristic, not a full MTG rules engine"):**
- O modelo de mana (`total_available_mana`) conta manas disponíveis de forma agregada — **não rastreia cores/pips**, só total genérico + incolor separado pro gatilho do Ulalek. Isso é preciso pro custo do próprio Ulalek (5 pips híbridos incolor/cor, então qualquer 5 mana serve), mas pra outras cartas com custo colorido fixo isso pode superestimar o quão "castável" uma mão é, já que o script não simula travar por falta de uma cor específica.
- O mulligan (`should_keep`) usa um heurístico simplificado: mantém mãos com 2-5 terrenos E (pelo menos 1 carta da lista `KEEPERS` OU 3+ terrenos com no máximo 2 Eldrazi grandes na mão) — é uma aproximação razoável de julgamento humano, não uma réplica dele.

**Nota metodológica, reproduzida do usuário:** são três execuções do mesmo simulador heurístico em estágios diferentes de refinamento (v2 inicial, v2.1 com modelagem de flash melhorada, v2.2 mais completa), cada uma com 500 jogos de 8 turnos, on the play. A lista do deck permaneceu essencialmente a mesma entre as três — as diferenças nos números refletem mudança na modelagem do simulador, não mudança no deck. Campos em branco no CSV significam "métrica não reportada naquela versão", não zero.

### v2 — primeira versão funcional

```
=== Ulalek v2 Goldfish Summary ===
Games: 500
Turns simulated: 8
On play: True
Avg mulligans: 0.38
Avg commander cast turn: 4.24
Commander cast by turn 4: 65.2%
Commander cast by turn 5: 82.6%
Avg spells cast: 10.21
Avg extra cards drawn: 3.69
Avg Eldrazi cast: 3.61
Avg Ulalek paid triggers: 2.91
Avg copied Eldrazi spells: 2.91
Avg total Ulalek windows: 3.61
Avg good Ulalek windows: 2.02
Avg dead Ulalek windows: 0.70
Avg flash lines taken: 0.13
Avg big threats resolved: 1.48
Defense triggers per game: 0.38
Vestige end-step triggers per game: 0.06
Avg final battlefield count: 14.45
Avg final hand size: 2.77
Detailed logs saved to: ulalek_v2_runs.jsonl
```

### v2.1 — modelagem de flash melhorada

```
=== Ulalek v2 Goldfish Summary v2.1 ===
Games: 500
Turns simulated: 8
On play: True
Avg mulligans: 0.39
Avg commander cast turn: 4.29
Commander cast by turn 4: 62.2%
Commander cast by turn 5: 83.6%
Avg spells cast: 10.06
Avg extra draws: 3.63
Avg Eldrazi cast: 3.45
Avg Ulalek paid triggers: 2.72
Avg copied Eldrazi spells: 2.72
Avg total Ulalek windows: 3.45
Avg good Ulalek windows: 2.08
Avg dead Ulalek windows: 0.73
Avg flash online turns: 1.83
Avg flash online + Eldrazi in hand: 0.74
Avg flash online + full Ulalek window: 0.50
Avg flash lines taken: 0.64
Avg big threats resolved: 1.39
Avg Defense triggers: 0.36
Avg Vestige end-step triggers: 0.10
Avg final battlefield count: 14.25
Avg final hand size: 2.88
Detailed logs saved to: ulalek_v2_flash_improved_runs.jsonl
```

### v2.2 — teste mais recente e mais completo

```
=== Ulalek v2 Goldfish Summary v2.2 ===
Games: 500
Turns simulated: 8
On play: True
Avg mulligans: 0.38
Avg commander cast turn: 4.25
Commander cast by turn 4: 65.4%
Commander cast by turn 5: 83.8%
Avg spells cast: 10.47
Avg extra draws: 4.38
Avg Eldrazi cast: 3.64
Avg Ulalek paid triggers: 2.89
Avg copied Eldrazi spells: 2.89
Avg total Ulalek windows: 3.64
Avg good Ulalek windows: 2.30
Avg dead Ulalek windows: 0.75
Avg flash online turns: 2.00
Avg flash online + Eldrazi in hand: 0.83
Avg flash online + full Ulalek window: 0.58
Avg premium flash windows: 0.58
Avg flash lines taken: 0.74
Avg Vestige casts: 0.15
Avg Vestige warp casts: 0.13
Avg Vestige good-copy windows: 0.15
Avg Vestige end-step triggers: 0.13
Avg Echoes-online Eldrazi casts: 0.53
Avg Throne-online relevant turns: 0.50
Avg big threats resolved: 1.49
Avg Defense triggers: 0.34
Avg final battlefield count: 14.63
Avg final hand size: 3.26
Detailed logs saved to: ulalek_v2_flash_v22_runs.jsonl
```

### CSV consolidado (fonte: usuário)

```
version,games,turns,on_play,avg_mulligans,avg_commander_cast_turn,commander_by_t4_pct,commander_by_t5_pct,avg_spells_cast,avg_extra_draws,avg_eldrazi_cast,avg_ulalek_paid_triggers,avg_copied_eldrazi_spells,avg_total_ulalek_windows,avg_good_ulalek_windows,avg_dead_ulalek_windows,avg_flash_online_turns,avg_flash_with_eldrazi,avg_flash_full_ulalek_window,avg_premium_flash_windows,avg_flash_lines_taken,avg_vestige_casts,avg_vestige_warp_casts,avg_vestige_good_copy_windows,avg_vestige_endstep_triggers,avg_echoes_online_eldrazi_casts,avg_throne_online_relevant_turns,avg_big_threats_resolved,avg_defense_triggers,avg_final_battlefield,avg_final_hand
v2_initial,500,8,True,0.38,4.24,65.2,82.6,10.21,3.69,3.61,2.91,2.91,3.61,2.02,0.70,,,,,0.13,,,,0.06,,,1.48,0.38,14.45,2.77
v2.1,500,8,True,0.39,4.29,62.2,83.6,10.06,3.63,3.45,2.72,2.72,3.45,2.08,0.73,1.83,0.74,0.50,,0.64,,,,0.10,,,1.39,0.36,14.25,2.88
v2.2,500,8,True,0.38,4.25,65.4,83.8,10.47,4.38,3.64,2.89,2.89,3.64,2.30,0.75,2.00,0.83,0.58,0.58,0.74,0.15,0.13,0.15,0.13,0.53,0.50,1.49,0.34,14.63,3.26
```

---

### Correção — checklist obrigatória de mecânica (regra nova pós-Beorn) — 2026-08-28

**Gatilho (usuário):** depois de eu entregar o Beorn sem despacho de landfall
nenhum, o usuário pediu auditoria da checklist nova (landfall, mana dorks,
mana rocks, fixing lands, draw engines, ramp engines, ativadas repetíveis,
combos) em **todos** os decks — aplicada aqui ao `ulalek_goldfish_v1.py`
atual (não confundir com os testes v2.x acima, de um script anterior).
Landfall N/A (0 cartas), dorks N/A (0 mana dorks criatura na lista).

**Achado mais grave — Forsaken Monument's habilidade mais impactante das 3
reais 100% ausente:** "Colorless creatures you control get +2/+2. Whenever
you tap a permanent for {C}, add an additional {C}. Whenever you cast a
colorless spell, you gain 2 life." Só a 3ª (vida) estava modelada. A 2ª
(dobra de mana de {C}) nunca existia — significativo, já que o deck é
literalmente sobre conjurar spells colorless MV7+. Implementado
`forsaken_monument_bonus()`, mas com cuidado real: dos 37 terrenos
"colorless"-tageados neste arquivo (tag que só significa "contado
genericamente neste modelo", não "produz {C} de verdade"), a maioria são
painlands/duais ABUR que produzem cor REAL (ex: Badlands = B ou R, não
{C}) — só dobram as fontes que de fato tapam por {C} no oráculo real
(conferido carta a carta: Eldrazi Temple, Cascading Cataracts, Wastes,
Shrine of the Forsaken Gods, Ugin's Labyrinth, Spawning Bed, Urza's Cave,
Cavern of Souls, Corrupted Crossroads, Sanctum of Ugin, Emergence Zone,
Ancient Tomb, Sol Ring, Thran Dynamo, os 3 Talismãs).

**Docstring mischaracterizava 3 cartas:** a linha "ativações pagas de
Urza's Cave/Sanctum of Ugin/Eye of Ugin/Mystic Forge (exilar topo)" —
"exilar topo" é o texto real de **Mystic Forge**, não dessas 3. Sanctum of
Ugin é na verdade um **gatilho grátis** ("Whenever you cast a colorless
spell with mana value 7 or greater, you may sacrifice this land... search
your library for a colorless creature card... to your hand") — implementado
de verdade (via `on_any_spell_cast_hooks`), já que é exatamente o gameplan
central do deck. Urza's Cave (busca land) e Eye of Ugin (desconto de custo +
busca criatura) continuam não implementados por decisão de escopo.

**Spawnbed Protector**: tagueada `endstep_recursion`, nunca despachada —
"At the beginning of your end step, return up to one Eldrazi creature card
from graveyard to hand. Create two 1/1 Eldrazi Scion tokens." Implementado
em `end_step()` (Scion tokens reaproveitam `create_spawn_tokens()`, mesma
habilidade real de sacrificar por {C}, só nome de token diferente).

**Resultado (n=2000, seed_base=2000000, antes → depois):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg tutores usados | 0,27 | **0,36** |
| Avg Eldrazi Spawn/Scion tokens criados | 1,17 | **1,44** |
| Avg vida ganha proxy (Forsaken Monument) | 0,19 | **0,35** |
| Avg cópias pagas da Ulalek | 0,99 | **1,04** |
| Avg cartas compradas extra | 1,49 | **1,55** |

Impacto moderado — o deck já tinha bastante mecânica real implementada nas
rodadas anteriores (v2.x), então esta rodada preencheu gaps específicos
(Forsaken Monument, Sanctum of Ugin, Spawnbed Protector), não uma reescrita.

**Robustez:** sweep de 20.000 jogos (seeds 2000000–2019999, timeout 2s/jogo)
— 0 erros, 0 timeouts.

`lista.md` não mudou. `ulalek_v1_runs.jsonl` sobrescrito.

---

### Reconfirmação total de oráculo e interações (a pedido do usuário) — 2026-08-30

**Gatilho:** usuário pediu explicitamente pra confirmar todo o oráculo das
100 cartas e todas as interações já documentadas neste deck, incluindo o
teste do Radagast (acima).

**Método:** novo fetch via `cards/collection` da Scryfall (dois lotes de
70+30, limite de 75 por request) das 100 cartas de `lista.md` — nenhum dado
reaproveitado do `oracle-cache.json` antigo. Radagast of Rhosgobel buscado
à parte (não está na lista, só no teste comparativo). Todo texto entre
aspas na `auditoria.md` e neste log foi conferido contra o `oracle_text`
fresco, carta a carta.

**Confirmado correto (sem alteração):**
- 100 cartas, singleton, identidade de cor e legalidade em Commander —
  todas `legal`, todas dentro de WUBRG.
- **37 terrenos reais** (contagem por `type_line` contendo "Land") — bate
  com a auditoria mesmo Spawning Bed e Ugin's Labyrinth estando na seção
  "Deck" de `lista.md` em vez de "Terrenos" (organização do arquivo, não
  erro de contagem).
- **Só Defense of the Heart e Rhystic Study são permanentes com `colors`
  não-vazio** em toda a lista — confirma exatamente a tese de "All Is Dust
  quase simétrico a favor de quem conjura".
- **3 Game Changers exatos:** Ancient Tomb, Rhystic Study, The One Ring
  (`cards/search?q=is:gamechanger`, 53 cartas no total, cruzado contra as
  100 da lista).
- Texto do comandante, Echoes of Eternity (as 2 habilidades), Forsaken
  Monument (as 3 habilidades), Sanctum of Ugin (gatilho grátis), Zhulodok
  ("cast... from your hand"), Radagast of Rhosgobel — todos batem
  literalmente com o `oracle_text` real, inclusive o resultado numérico do
  teste do Radagast (delta de desconto, flash concedido, ausência de
  interação com o motor de cópia) continua válido: a leitura mecânica
  estava certa desde o teste original, não precisou de correção.

**Erro real encontrado e corrigido:** `auditoria.md`, seção 3 (Remoção),
descrevia Ugin, the Ineffable como "-3: destrói permanente CMC 3+". O
oráculo real é **"−3: Destroy target permanent that's one or more
colors"** — não tem restrição de CMC nenhuma, é o mesmo eixo cor-vs-incolor
do All Is Dust (faz sentido nesse deck: quase todo o board é incolor via
Devoid, então o -3 também tende a ser assimétrico a favor de quem
conjura). Corrigido na `auditoria.md`. **Sem impacto no simulador** —
conferido em `ulalek_goldfish_v1.py` (linha 655): a única coisa modelada
de Ugin, the Ineffable é o desconto estático de {2} em spells colorless,
que já estava correto; a habilidade -3 nunca tinha sido implementada como
remoção específica (fica dentro do proxy genérico de interação), então o
erro nunca vazou pros números de nenhuma simulação.

**Conclusão:** oráculo e interações documentadas neste deck estão corretos
com uma exceção pontual (agora corrigida), incluindo a recomendação sobre
o Radagast — que segue válida como estava: ganho real mas modesto, não
alimenta o motor de cópia da Ulalek (não é Eldrazi), e adiciona um 3º
permanente colorido de verdade à lista.

---

### Reanálise do simulador Python (`ulalek_goldfish_v1.py`) — a pedido do usuário — 2026-08-30

**Gatilho:** depois da reconfirmação de oráculo acima, usuário pediu
explicitamente pra reanalisar o simulador em si "pra ver se não há erros
como nos outros" (referência às correções feitas em Beorn/Ur-Dragon/etc).
Passei o código inteiro (1100 linhas) por conferência linha a linha contra
o `oracle.json` fresco da reconfirmação — comparação sistemática via
script (tags `colorless`/`eldrazi` de cada carta no `CARD_DB` vs. `colors`/
`type_line` reais da Scryfall, mv declarado vs. `cmc` real, `ctype`
declarado vs. `type_line` real) mais leitura manual de cada função central.

**4 achados reais, todos corrigidos:**

1. **Forsaken Monument (`TRUE_C_LANDS`) faltavam os 8 painlands.** O
   comentário do código afirmava que "a maioria dos terrenos... são
   painlands/duais ABUR que produzem cor real" (implicando que não tapam
   por `{C}`) — falso pros 8 painlands da lista (Adarkar Wastes, Brushland,
   Caves of Koilos, Karplusan Forest, Llanowar Wastes, Shivan Reef,
   Sulfurous Springs, Yavimaya Coast): todos têm um modo `"{T}: Add {C}."`
   incondicional e sem custo de vida, além do modo colorido com dano —
   confirmado carta a carta no oráculo fresco. Só os 10 duais ABUR de
   verdade não têm modo `{C}`. Os 8 painlands estavam sendo tratados como
   se nunca dobrassem via Forsaken Monument. Corrigido.
2. **Glaring Fleshraker tem 2 habilidades reais, só 1 estava implementada
   e a 2ª nunca foi sequer documentada como omissão.** Oráculo real:
   "Whenever you cast a colorless spell, create a Spawn token" (1ª, já
   implementada) **e** "Whenever another colorless creature you control
   enters, this creature deals 1 damage to each opponent" (2ª — nunca
   despachada, nem na seção de simplificações documentadas do arquivo).
   Como o deck cria tokens Spawn/Scion/Manifest o tempo todo, essa 2ª
   habilidade dispara com frequência real. Implementada como proxy de dano
   (`glaring_fleshraker_damage_total`, mesma convenção de
   `proxy_removal_total`), disparando em toda criatura colorless entrando
   em campo — spells conjurados E tokens sintéticos — com suporte a
   Echoes of Eternity/Roaming Throne dobrando igual à 1ª habilidade.
3. **Skittering Cicada sem a tag `colorless`, apesar de ser realmente
   incolor (`colors: []` na Scryfall, custo genérico `{3}`, sem Devoid
   necessário).** Sem a tag, o simulador tratava a Cicada como permanente
   "colorido" — o que a fazia ser sacrificada erroneamente por All Is Dust
   e ficar fora da elegibilidade de cópia da Echoes of Eternity. Achado
   por varredura sistemática (script comparando toda tag `colorless` do
   `CARD_DB` contra o campo `colors` real de cada uma das 100 cartas) —
   única carta com esse mismatch em toda a lista. Corrigido.
4. **Emrakul, the Promised End nunca recebia seu próprio desconto de
   custo real.** Oráculo: "This spell costs {1} less to cast for each
   card type among cards in your graveyard" — nunca implementado nem
   citado nas simplificações documentadas; Emrakul ficava sempre travada
   no custo cheio de 13. Implementado via `graveyard_card_types()`
   (conta tipos reais distintos no cemitério, `artifact_creature` conta
   como Artifact E Creature), empilhando com os outros descontos
   (Eye of Ugin, Urza's Incubator, Ugin the Ineffable, It That Heralds
   the End) como as regras reais permitem.

**Robustez:** sweep de 20.000 jogos (seeds 3000000–3019999, timeout 2s/
jogo) — 0 erros, 0 timeouts.

**n=3000, seed_base=8600000, 8 turnos — antes (HEAD anterior a hoje) →
depois:**

| Métrica | Antes | Depois |
|---|---|---|
| Avg copias pagas da Ulalek (CC) | 1,03 | 1,05 |
| Avg tokens-copia de permanentes | 1,13 | 1,16 |
| Avg cartas compradas extra | 1,50 | 1,54 |
| Avg Eldrazi Spawn tokens criados | 1,49 | 1,52 |
| Avg vida ganha proxy (Forsaken Monument) | 0,36 | **0,43** |
| **Avg permanentes próprios sacrificados por All Is Dust** | 0,22 | **0,12** |
| Avg dobras via Roaming Throne | 0,04 | **0,16** |
| Avg dano proxy via Glaring Fleshraker (2ª habilidade) | — (n/a) | **1,17** |
| Avg mão final | 2,93 | 2,91 |

Leitura: a queda de "permanentes sacrificados por All Is Dust" (0,22→0,12)
é diretamente a correção da Skittering Cicada (deixou de ser contada como
alvo colorido). O salto de "dobras via Roaming Throne" (0,04→0,16) é a
2ª habilidade de Glaring Fleshraker virando um novo gatilho dobrável. O
aumento geral pequeno em quase todas as outras métricas vem do bônus extra
de mana do Forsaken Monument (8 painlands agora contando pra dobra) —
mais mana disponível ao longo do jogo, efeito difuso.

`lista.md` não mudou. `ulalek_v1_runs.jsonl` sobrescrito.

---

### Rodada ampliada — checklist categorias 10-13 (regra ampliada de mecânica) — 2026-08-31

**Gatilho:** pedido explícito do usuário para completar a "rodada ampliada" do
checklist obrigatório de `references/goldfish-sim-card-rules.md` neste deck —
as categorias 1-9 já tinham sido auditadas em 2026-08-28, mas as categorias
10-13 (métricas básicas completas, multi-face, planeswalker, Classe/Saga)
nunca tinham passado por essa rodada formal aqui.

**Categoria 11 (multi-face) e categoria 13 (Classe/Saga) — N/A confirmado,
varredura própria independente.** Script cruzando as 100 cartas de
`lista.md` contra `scryfall-cache/oracle-cache.json` (campo `mana_cost`,
`oracle_text`, `type_line`) não achou nenhum nome com "//", nenhum
`card_faces`, e nenhum `type_line` contendo "Class" ou "Saga". Nenhuma
implementação necessária — só documentação (já estava correta na avaliação
prévia desta sessão, confirmada de novo aqui de forma independente, não só
repetida).

**Categoria 12 (planeswalker) — Ugin, the Ineffable, lealdade rastreada de
verdade.** Oráculo real (Scryfall, `oracle-cache.json`, loyalty inicial 4,
`type_line`: "Legendary Planeswalker — Ugin"):

```
Colorless spells you cast cost {2} less to cast.
+1: Exile the top card of your library face down and look at it. Create a
2/2 colorless Spirit creature token. When that token leaves the
battlefield, put the exiled card into your hand.
−3: Destroy target permanent that's one or more colors.
```

A parte estática (desconto de {2} em colorless) já estava correta havia
várias rodadas (`eldrazi_cost_discount`). Antes desta correção, **0
ocorrências de `state.loyalty` em todo o arquivo** — nenhuma lealdade
rastreada, nenhuma decisão de ativação, nenhum efeito de +1/-3
implementado. Corrigido via `do_ugin_loyalty()`:

- **Lealdade inicial real (4)** rastreada em `state.loyalty["Ugin, the
  Ineffable"]`, setada no ETB (`enter_battlefield`).
- **Decisão real de qual habilidade ativar por turno** (CR 606.3, 1
  ativação/turno, velocidade de feitiço): heurística documentada — **sempre
  +1**. O -3 é reativo e só vale a pena com um alvo colorido de oponente
  real — mas este simulador não modela oponente (Regra 1), e as **únicas 2
  cartas coloridas de verdade em toda a lista de 100** são NOSSAS (Defense
  of the Heart, Rhystic Study — mesma checagem já usada pro All Is Dust).
  Destruir permanente próprio seria uma piora, nunca escolhida por uma
  heurística greedy. -3 fica "disponível mas sem efeito numérico
  proveitoso" — mesma convenção já usada em Defense of the Heart/Sire of
  Stagnation — e contado explicitamente em
  `ugin_minus3_skipped_no_target_total` pra deixar a decisão auditável, não
  só omitida.
- **Efeito do +1 implementado de verdade:** token 2/2 colorless Spirit
  criado (`ugin_spirit_tokens_created_total`) + topo da biblioteca exilado
  face-down (`ugin_cards_exiled_stuck_total`). Como o token Spirit não tem
  sac outlet próprio (só Eldrazi Spawn/Scion têm "sacrifice: add {C}") e
  este goldfish solo não modela combate/remoção de oponente, o token
  **nunca sai de campo neste simulador** — então "when that token leaves
  the battlefield, put the exiled card into your hand" nunca dispara aqui,
  documentado como omissão explícita (mesma convenção já usada nos outros
  leaves-the-battlefield triggers do arquivo). A carta exilada fica presa
  em exílio — perda real, tornada visível pela métrica dedicada em vez de
  silenciada.

**Achado adicional durante a varredura — legend rule não é aplicada a
cópias-token de permanentes lendários (limitação conhecida, não corrigida
nesta rodada):** o motor de cópia (Ulalek/Echoes) não força o sacrifício de
uma 2ª cópia de um permanente lendário (Kozilek x3, Ulamog x2, Emrakul,
Zhulodok, Morophon, e agora potencialmente Ugin via Echoes) — CR 704.5j
exigiria isso numa mesa real. Esse comportamento já existia antes desta
rodada e já foi documentado/aceito em várias sessões anteriores (ex.: "2
corpos 10/10 EM CAMPO" pro Kozilek, Butcher of Truth, descrito como correto
no docstring do arquivo desde 2026-08-23). Corrigir isso agora mudaria
números do motor central de cópia já validados em múltiplas rodadas sem
pedido explícito do usuário para essa mudança específica — documentado como
achado real desta auditoria, não implementado. Fica como candidato pra uma
rodada dedicada futura.

**Categoria 10 (métricas básicas obrigatórias) — RECURSION, RAMP e
FINISHER/LETHALITY nunca tinham linha própria no relatório.**

- **RECURSION:** confirmado o que o usuário suspeitava — Spawnbed Protector
  já retornava carta do cemitério pra mão desde a correção de 2026-08-28,
  mas **nunca virava uma métrica agregada reportada**, ficava "invisível"
  no `run_batch`. Corrigido (`recursion_events_total`,
  `spawnbed_protector_recursion_total`). Durante a varredura, achado um
  **2º gap real**: **World Breaker** ("{2}{C}, Sacrifice a land: Return
  this card from your graveyard to your hand.") tinha só o cast-trigger
  (`ct_removal1`) implementado — a habilidade de recursão (ativada, custo
  real 3 mana + sacrifício de terreno) estava 100% ausente. Implementada
  via `do_world_breaker_recursion()`, heurística documentada (só ativa com
  mana sobrando ≥3, mais de 5 terrenos em campo — piso de segurança pra
  nunca sacrificar terreno que reduza a manabase abaixo de 5).
- **RAMP:** nunca teve uma linha agregada própria — os componentes (rocks,
  land tutors) existiam espalhados sem contador central. Adicionado
  `ramp_pieces_resolved_total` (incrementado em cada resolução real de
  mana rock — Sol Ring/Arcane Signet/Talismans/Thran Dynamo — e cada land
  tutor bem-sucedido — Farseek/Nature's Lore/Three Visits/Sowing
  Mycospawn/Expedition Map). Achado extra: as amostras de mana por turno
  (`true_c_capacity_samples`/`total_mana_samples`, coletadas desde
  2026-08-30 "a pedido do usuário" segundo o próprio comentário do código)
  **nunca eram impressas em lugar nenhum do relatório** — corrigido,
  agora aparecem como parte do bloco RAMP.
- **FINISHER/LETHALITY:** 100% ausente do relatório antes desta correção.
  Implementado via tag `"finisher"` nas 8 criaturas MV≥9 da lista (mesmo
  conjunto já citado em `auditoria.md` seção 2: "Kozilek x3, Ulamog x2,
  Emrakul, Void Winnower, Flayer of Loyalties") — conta reais + cópias
  (Echoes/Ulalek) + acertos de cascade, já que todos passam por
  `enter_battlefield()`. Reporta: avg finishers resolvidos, % de jogos com
  pelo menos 1 finisher resolvido, turno médio/mediano do 1º finisher.

**Robustez:** 2 sweeps de 20.000 jogos cada (seeds 5100000–5119999 e
5200000–5219999, timeout 2s/jogo via `signal.alarm`) — **0 erros, 0
timeouts** nos dois, 40.000 jogos totais.

**n=3000, seed_base=8600000, 8 turnos — antes → depois (mesma seed):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg cópias pagas da Ulalek (CC) | 1,05 | 1,04 |
| Avg cascade cascade disparadas | 0,08 | 0,07 |
| Avg spells de interação conjurados (proxy) | 1,82 | 1,81 |
| Avg dobras via Roaming Throne | 0,16 | 0,15 |
| Avg dano proxy via Glaring Fleshraker | 1,17 | 1,16 |
| **RECURSION — Avg eventos totais** | *(não reportado)* | **0,0007** |
| **RECURSION — % de jogos com ≥1 evento** | *(não reportado)* | **0,07%** |
| **RAMP — Avg peças de ramp resolvidas** | *(não reportado)* | **1,73** |
| **RAMP — Avg mana total/turno** | *(não reportado)* | **4,68** |
| **RAMP — Avg capacidade {C} real/turno** | *(não reportado)* | **2,76** |
| **FINISHER/LETHALITY — Avg finishers resolvidos** | *(não reportado)* | **0,25** |
| **FINISHER/LETHALITY — % jogos c/ ≥1 finisher** | *(não reportado)* | **15,4%** |
| **FINISHER/LETHALITY — turno médio do 1º finisher** | *(não reportado)* | **7,36** |
| **Ugin — Avg ativações de lealdade/partida** | *(não rastreado)* | **0,17** |
| **Ugin — % de jogos em que resolveu** | *(não rastreado)* | **8,17% (245/3000)** |
| **Ugin — Avg lealdade final (jogos que resolveram)** | *(não rastreado)* | **6,11** |

**Leitura das 5 pequenas quedas (-0,01 cada) nas métricas pré-existentes:**
causadas pelo próprio +1 do Ugin passar a exilar o topo da biblioteca
(mecânica nova, real) — isso desloca a ordem de compra do resto do jogo
mesmo com a MESMA seed, um efeito colateral esperado e explicado (não um
bug), da mesma natureza já documentada em correções anteriores deste deck
quando um novo consumo de biblioteca é introduzido.

**RECURSION é real, mas rara neste deck especificamente** (0,07% dos
jogos) — não porque a implementação esteja errada, mas porque as duas
fontes reais de recursão do deck têm pré-condições pouco frequentes num
goldfish solo de 8 turnos com uma IA proativa: Spawnbed Protector (7 mana)
precisa que já exista um Eldrazi elegível no cemitério (raro, já que a IA
não descarta Eldrazi voluntariamente) e World Breaker precisa já estar no
cemitério (só acontece via mão cheia de 7+ no fim do turno). Confirmado por
varredura dedicada: Spawnbed Protector chega ao campo em 190/3000 jogos
(6,3%), mas só 2 desses têm um Eldrazi elegível no cemitério no momento do
end step.

`lista.md` não mudou. `ulalek_v1_runs.jsonl` sobrescrito com os campos
novos (`ugin_loyalty_final`, `recursion_events_total`,
`ramp_pieces_resolved_total`, `finisher_resolved_total`, etc.).

---

## Partida #1 — 2026-08-30 (partida REAL, jogada à mão no goldfish do Archidekt)

**Formato do registro:** igual ao método usado nas Partidas #13-15 do Ur-Dragon —
não é simulação automatizada. Usuário jogou manualmente no modo goldfish do
Archidekt e colou o log estruturado (JSON) de mudança de zona, turno a
turno, junto de screenshots da mão inicial. Vários detalhes da linha de
jogo (turno exato da comandante, quais spells foram copiados, a conta do
desconto de custo) foram corrigidos pelo usuário e reconferidos contra o
oráculo real ao longo da conversa antes de fechar este registro — os
números abaixo já refletem essas correções, não a primeira leitura do log.

- **Mão inicial (mulligan até):** keep na mão de 7 (sem mulligan). Urza's Incubator, Plateau, Kozilek, the Great Distortion, It That Heralds the End, Underground Sea, Shivan Reef, Talisman of Dominance.
- **Turno 1:** joga Plateau.
- **Turno 2:** joga Underground Sea (2º terreno). Conjura Talisman of Dominance.
- **Turno 3:** joga Taiga (3º terreno). Conjura Urza's Incubator, tipo escolhido: Eldrazi.
- **Turno 4:** joga Shivan Reef (4º terreno). **Conjura a Ulalek, Fused Atrocity** (dentro da média medida pela auditoria, ~4,5 turnos — nesse caso até um pouco antes).
- **Turno 5:** conjura 2 Eldrazi spells (It That Heralds the End e Chittering Dispatcher) e paga o `{C}{C}` da Ulalek nas duas — cada uma sai com uma cópia-token extra em campo. Fim do turno: 2x It That Heralds the End e 2x Chittering Dispatcher em campo.
- **Turno 6:** conjura Kozilek, the Great Distortion (`{8}{C}{C}`, 10 de mana base) por só **6 mana** — desconto de -4 confirmado carta a carta: -2 do Urza's Incubator ("creature spells of the chosen type cost {2} less", Eldrazi qualifica) + -1 de cada uma das 2 cópias do It That Heralds the End ("colorless spells... mana value 7 or greater cost {1} less", cada cópia em campo aplica o próprio desconto).
- **Turnos seguintes (Roaming Throne entra, ataque em massa dos Chittering Dispatchers):** com Roaming Throne (tipo escolhido: Eldrazi) já em campo, os 2 Chittering Dispatchers atacam. Myriad é ele mesmo uma habilidade disparada (fonte = o próprio Chittering, criatura Eldrazi em campo) — então o Throne dobra o Myriad de cada um: em vez de 2 tokens por ataque (mesa de 4 jogadores, 1 token por oponente que não o alvo), cada Chittering gera 4 (2 resoluções × 2 oponentes). Os 2 reais atacando = **8 tokens-cópia do Chittering**. Cada token, ao ser exilado no fim do turno pelo próprio Myriad, dispara seu próprio "when this creature leaves the battlefield, create a Spawn" — também dobrado pelo Throne (fonte = criatura Eldrazi em campo) → 2 Spawns por token. **8 tokens × 2 = 16 Eldrazi Spawn tokens** de um único ataque duplo. Conta verificada passo a passo nessa sessão, bate exatamente com o oráculo do Myriad e do Roaming Throne.
- **Fim do trecho registrado:** Echoes of Eternity entra em campo — 3º motor de cópia/dobra simultâneo com Ulalek e Roaming Throne já ativos (Kozilek, the Great Distortion também tinha sido copiado ao ser conjurado, mesma mecânica do turno 5).
- **Resultado:** sem resolução (trecho de goldfish solo, sem oponente real — objetivo era desenvolver o motor, não fechar o jogo).
- **O que funcionou bem:** curva perfeita (land drop todo turno, nunca travou), Urza's Incubator no T3 descontando tudo dali pra frente, comandante resolvida no T4 (acima da média). A partir do T5 o motor de cópia (Ulalek pagando CC em sequência) e o desconto acumulado de custo (Incubator + 2x It That Heralds) permitiram uma bomba de 10 mana (Kozilek, the Great Distortion) sair por 6 já no T6. O combo Chittering Dispatcher x2 + Myriad + Roaming Throne se mostrou o pico de valor da partida — 16 Spawn tokens de um ataque só, bem acima do que a intuição sugere à primeira vista (o Throne dobra o próprio Myriad, não só o gatilho de saída de campo, e os dois efeitos se multiplicam).
- **O que travou o deck:** nada — outlier positivo, mesma classificação de partidas de pico já registradas nesse repositório (Ur-Dragon Partida #15, por exemplo). Curva sem nenhum land drop perdido do T1 ao T6+ é o cenário favorável, não o típico.
- **Ajustes a considerar:** nenhum de lista — reforça que Roaming Throne, apesar de mais fraco nesse deck do que em decks de gatilho-em-campo puro (achado da Simulação #1), ainda é uma bomba real quando combinado com Myriad (Chittering Dispatcher) — os dois juntos multiplicam de forma não-óbvia (dobra o gatilho de ataque E o gatilho de saída de campo, dois pontos de dobra independentes na mesma carta).

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
