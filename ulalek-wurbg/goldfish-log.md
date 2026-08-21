# Goldfish Log — Ulalek, Fused Atrocity

Registro de partidas de goldfishing (testes solo) e partidas reais com este deck.

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
