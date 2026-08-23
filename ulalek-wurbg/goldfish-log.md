# Goldfish Log — Ulalek, Fused Atrocity

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

---

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
